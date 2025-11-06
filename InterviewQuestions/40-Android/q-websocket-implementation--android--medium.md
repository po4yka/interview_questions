---
id: android-092
title: WebSocket Implementation / Реализация WebSocket
aliases:
- WebSocket Implementation
- Реализация WebSocket
topic: android
subtopics:
- networking-http
- performance-startup
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-what-are-services-for--android--easy
created: 2025-10-13
updated: 2025-10-31
tags:
- android/networking-http
- android/performance-startup
- difficulty/medium
- okhttp
- real-time
- resilience
- websocket
---

# Вопрос (RU)
> Реализация WebSocket

# Question (EN)
> WebSocket Implementation

---

## Answer (EN)
**WebSocket** is a protocol providing full-duplex communication channels over a single TCP connection. Unlike HTTP, which is request-response based, WebSocket enables bidirectional, real-time communication between client and server. This makes it ideal for chat applications, live updates, gaming, and any scenario requiring low-latency, bidirectional data flow.

### Why WebSocket?

**Traditional HTTP Polling:**
```
Client: "Any updates?" → Server: "No"
Client: "Any updates?" → Server: "No"
Client: "Any updates?" → Server: "Yes, here's data"
```
- Wasteful: Many empty responses
- High latency: Delays between polls
- Resource intensive: Constant connections

**WebSocket:**
```
Client ←→ Server (persistent connection)
Server: "Here's data" → Client (instant push)
Client: "Here's data" → Server (instant send)
```
- Efficient: Single persistent connection
- Low latency: Instant bidirectional communication
- Resource friendly: One connection for both directions

### WebSocket `Lifecycle`

```

 CLOSED ← Initial state

 connect()
 ↓

 CONNECTING ← Opening handshake

 onOpen()
 ↓

 CONNECTED ← Active communication

 onMessage(), send()
 ping/pong heartbeat

 → Network issue → DISCONNECTED
 → Manual close() → CLOSING → CLOSED
 → onFailure() → DISCONNECTED
 ↓

 DISCONNECTED

 Auto-reconnect (exponential backoff)
 → CONNECTING
```

### Complete WebSocket Client Implementation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import okhttp3.*
import okio.ByteString
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlin.math.pow

class WebSocketClient(
 private val url: String,
 private val okHttpClient: OkHttpClient,
 private val config: Config = Config()
) {

 data class Config(
 val maxReconnectAttempts: Int = Int.MAX_VALUE,
 val initialReconnectDelayMs: Long = 1000L,
 val maxReconnectDelayMs: Long = 30000L,
 val reconnectDelayFactor: Double = 2.0,
 val heartbeatIntervalMs: Long = 30000L,
 val heartbeatTimeoutMs: Long = 10000L,
 val connectionTimeoutMs: Long = 10000L,
 val enableMessageQueue: Boolean = true,
 val maxQueueSize: Int = 100
 )

 sealed class State {
 object Closed : State()
 object Connecting : State()
 data class Connected(val webSocket: WebSocket) : State()
 data class Disconnected(val reason: String, val code: Int?) : State()
 }

 sealed class Event {
 data class MessageReceived(val text: String) : Event()
 data class DataReceived(val bytes: ByteString) : Event()
 data class StateChanged(val state: State) : Event()
 data class Error(val throwable: Throwable) : Event()
 }

 private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

 private val _state = MutableStateFlow<State>(State.Closed)
 val state: StateFlow<State> = _state.asStateFlow()

 private val _events = MutableSharedFlow<Event>(
 extraBufferCapacity = 64,
 onBufferOverflow = BufferOverflow.DROP_OLDEST
 )
 val events: SharedFlow<Event> = _events.asSharedFlow()

 private var currentWebSocket: WebSocket? = null
 private var reconnectAttempt = AtomicInteger(0)
 private var reconnectJob: Job? = null
 private var heartbeatJob: Job? = null

 // Message queue for offline messages
 private val messageQueue = mutableListOf<QueuedMessage>()
 private val queueMutex = kotlinx.coroutines.sync.Mutex()

 private data class QueuedMessage(
 val message: String,
 val timestamp: Long = System.currentTimeMillis()
 )

 // Heartbeat tracking
 private var lastPongReceived = System.currentTimeMillis()
 private var heartbeatMissCount = 0

 fun connect() {
 scope.launch {
 if (_state.value is State.Connected || _state.value is State.Connecting) {
 return@launch
 }

 updateState(State.Connecting)
 performConnect()
 }
 }

 fun disconnect() {
 scope.launch {
 reconnectJob?.cancel()
 heartbeatJob?.cancel()
 currentWebSocket?.close(1000, "Client disconnecting")
 currentWebSocket = null
 updateState(State.Closed)
 }
 }

 fun send(message: String): Boolean {
 val currentState = _state.value

 return if (currentState is State.Connected) {
 currentState.webSocket.send(message)
 } else {
 // Queue message if offline
 if (config.enableMessageQueue) {
 queueMessage(message)
 true
 } else {
 false
 }
 }
 }

 fun send(bytes: ByteString): Boolean {
 val currentState = _state.value
 return if (currentState is State.Connected) {
 currentState.webSocket.send(bytes)
 } else {
 false
 }
 }

 private suspend fun performConnect() {
 try {
 val request = Request.Builder()
 .url(url)
 .build()

 val webSocket = okHttpClient.newWebSocket(request, createWebSocketListener())
 currentWebSocket = webSocket

 // Wait for connection with timeout
 withTimeout(config.connectionTimeoutMs) {
 // Wait until state changes from Connecting
 _state.first { it !is State.Connecting }
 }

 } catch (e: TimeoutCancellationException) {
 updateState(State.Disconnected("Connection timeout", null))
 scheduleReconnect()
 } catch (e: Exception) {
 updateState(State.Disconnected("Connection failed: ${e.message}", null))
 scheduleReconnect()
 }
 }

 private fun createWebSocketListener() = object : WebSocketListener() {

 override fun onOpen(webSocket: WebSocket, response: Response) {
 scope.launch {
 updateState(State.Connected(webSocket))
 reconnectAttempt.set(0)
 startHeartbeat()
 sendQueuedMessages()
 }
 }

 override fun onMessage(webSocket: WebSocket, text: String) {
 scope.launch {
 _events.emit(Event.MessageReceived(text))
 }
 }

 override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
 scope.launch {
 _events.emit(Event.DataReceived(bytes))
 }
 }

 override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
 webSocket.close(1000, null)
 }

 override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
 scope.launch {
 heartbeatJob?.cancel()
 if (code == 1000) {
 // Normal closure
 updateState(State.Closed)
 } else {
 updateState(State.Disconnected(reason, code))
 scheduleReconnect()
 }
 }
 }

 override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
 scope.launch {
 heartbeatJob?.cancel()
 _events.emit(Event.Error(t))

 val reason = response?.message ?: t.message ?: "Unknown error"
 val code = response?.code
 updateState(State.Disconnected(reason, code))
 scheduleReconnect()
 }
 }
 }

 private fun startHeartbeat() {
 heartbeatJob?.cancel()
 lastPongReceived = System.currentTimeMillis()
 heartbeatMissCount = 0

 heartbeatJob = scope.launch {
 while (isActive) {
 delay(config.heartbeatIntervalMs)

 val currentState = _state.value
 if (currentState !is State.Connected) {
 break
 }

 // Check if we received pong response
 val timeSinceLastPong = System.currentTimeMillis() - lastPongReceived
 if (timeSinceLastPong > config.heartbeatTimeoutMs) {
 heartbeatMissCount++

 if (heartbeatMissCount >= 3) {
 // Connection appears dead, reconnect
 currentWebSocket?.close(1001, "Heartbeat timeout")
 break
 }
 }

 // Send ping
 currentState.webSocket.send("ping")
 }
 }
 }

 fun onPongReceived() {
 lastPongReceived = System.currentTimeMillis()
 heartbeatMissCount = 0
 }

 private fun scheduleReconnect() {
 reconnectJob?.cancel()

 if (reconnectAttempt.get() >= config.maxReconnectAttempts) {
 return
 }

 val attempt = reconnectAttempt.getAndIncrement()
 val delay = calculateReconnectDelay(attempt)

 reconnectJob = scope.launch {
 delay(delay)

 if (_state.value is State.Disconnected) {
 updateState(State.Connecting)
 performConnect()
 }
 }
 }

 private fun calculateReconnectDelay(attempt: Int): Long {
 val exponentialDelay = config.initialReconnectDelayMs *
 config.reconnectDelayFactor.pow(attempt).toLong()

 val delayWithCap = exponentialDelay.coerceAtMost(config.maxReconnectDelayMs)

 // Add jitter (±10%) to prevent thundering herd
 val jitter = (delayWithCap * 0.1 * (Math.random() - 0.5)).toLong()

 return delayWithCap + jitter
 }

 private fun queueMessage(message: String) {
 scope.launch {
 queueMutex.withLock {
 if (messageQueue.size >= config.maxQueueSize) {
 messageQueue.removeAt(0) // Remove oldest
 }
 messageQueue.add(QueuedMessage(message))
 }
 }
 }

 private suspend fun sendQueuedMessages() {
 queueMutex.withLock {
 val currentState = _state.value
 if (currentState is State.Connected) {
 messageQueue.forEach { queued ->
 currentState.webSocket.send(queued.message)
 }
 messageQueue.clear()
 }
 }
 }

 private suspend fun updateState(newState: State) {
 _state.value = newState
 _events.emit(Event.StateChanged(newState))
 }

 fun close() {
 disconnect()
 scope.cancel()
 }
}
```

### Chat `Application` Example

Complete chat application using WebSocket:

```kotlin
// Chat Message Models
@Serializable
sealed class ChatMessage {
 abstract val id: String
 abstract val timestamp: Long

 @Serializable
 @SerialName("text")
 data class TextMessage(
 override val id: String,
 val userId: String,
 val userName: String,
 val text: String,
 override val timestamp: Long,
 val status: MessageStatus = MessageStatus.SENT
 ) : ChatMessage()

 @Serializable
 @SerialName("typing")
 data class TypingIndicator(
 override val id: String,
 val userId: String,
 val userName: String,
 val isTyping: Boolean,
 override val timestamp: Long
 ) : ChatMessage()

 @Serializable
 @SerialName("user_joined")
 data class UserJoined(
 override val id: String,
 val userId: String,
 val userName: String,
 override val timestamp: Long
 ) : ChatMessage()

 @Serializable
 @SerialName("user_left")
 data class UserLeft(
 override val id: String,
 val userId: String,
 val userName: String,
 override val timestamp: Long
 ) : ChatMessage()

 enum class MessageStatus {
 SENDING, SENT, DELIVERED, READ, FAILED
 }
}

// Chat Client
class ChatClient(
 private val webSocketUrl: String,
 private val userId: String,
 private val userName: String,
 okHttpClient: OkHttpClient
) {

 private val json = Json {
 ignoreUnknownKeys = true
 classDiscriminator = "type"
 }

 private val webSocketClient = WebSocketClient(
 url = webSocketUrl,
 okHttpClient = okHttpClient,
 config = WebSocketClient.Config(
 heartbeatIntervalMs = 30000L,
 enableMessageQueue = true,
 maxQueueSize = 50
 )
 )

 private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
 val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

 private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
 val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

 sealed class ConnectionState {
 object Connected : ConnectionState()
 object Connecting : ConnectionState()
 object Disconnected : ConnectionState()
 data class Error(val message: String) : ConnectionState()
 }

 private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

 init {
 observeWebSocketEvents()
 }

 private fun observeWebSocketEvents() {
 scope.launch {
 webSocketClient.state.collect { state ->
 _connectionState.value = when (state) {
 is WebSocketClient.State.Connected -> ConnectionState.Connected
 is WebSocketClient.State.Connecting -> ConnectionState.Connecting
 is WebSocketClient.State.Closed -> ConnectionState.Disconnected
 is WebSocketClient.State.Disconnected ->
 ConnectionState.Error(state.reason)
 }
 }
 }

 scope.launch {
 webSocketClient.events.collect { event ->
 when (event) {
 is WebSocketClient.Event.MessageReceived -> {
 handleIncomingMessage(event.text)
 }

 is WebSocketClient.Event.Error -> {
 _connectionState.value = ConnectionState.Error(
 event.throwable.message ?: "Unknown error"
 )
 }

 else -> {}
 }
 }
 }
 }

 fun connect() {
 webSocketClient.connect()
 }

 fun disconnect() {
 webSocketClient.disconnect()
 }

 fun sendMessage(text: String) {
 val message = ChatMessage.TextMessage(
 id = generateMessageId(),
 userId = userId,
 userName = userName,
 text = text,
 timestamp = System.currentTimeMillis(),
 status = ChatMessage.MessageStatus.SENDING
 )

 // Optimistically add to messages
 addMessage(message)

 // Send via WebSocket
 val jsonString = json.encodeToString(ChatMessage.serializer(), message)
 val sent = webSocketClient.send(jsonString)

 if (!sent) {
 // Update status to failed
 updateMessageStatus(message.id, ChatMessage.MessageStatus.FAILED)
 } else {
 updateMessageStatus(message.id, ChatMessage.MessageStatus.SENT)
 }
 }

 fun sendTypingIndicator(isTyping: Boolean) {
 val message = ChatMessage.TypingIndicator(
 id = generateMessageId(),
 userId = userId,
 userName = userName,
 isTyping = isTyping,
 timestamp = System.currentTimeMillis()
 )

 val jsonString = json.encodeToString(ChatMessage.serializer(), message)
 webSocketClient.send(jsonString)
 }

 fun retrySendMessage(messageId: String) {
 val message = _messages.value.find { it.id == messageId }
 if (message is ChatMessage.TextMessage) {
 val jsonString = json.encodeToString(ChatMessage.serializer(), message)
 val sent = webSocketClient.send(jsonString)

 updateMessageStatus(
 messageId,
 if (sent) ChatMessage.MessageStatus.SENDING else ChatMessage.MessageStatus.FAILED
 )
 }
 }

 private fun handleIncomingMessage(jsonString: String) {
 try {
 val message = json.decodeFromString<ChatMessage>(jsonString)

 // Handle special message types
 when (message) {
 is ChatMessage.TypingIndicator -> {
 // Update typing state (not added to messages list)
 // Could emit to separate typing indicators flow
 }

 else -> {
 addMessage(message)
 }
 }

 // Handle pong for heartbeat
 if (jsonString == "pong") {
 webSocketClient.onPongReceived()
 }

 } catch (e: Exception) {
 // Log parse error
 }
 }

 private fun addMessage(message: ChatMessage) {
 _messages.value = _messages.value + message
 }

 private fun updateMessageStatus(messageId: String, status: ChatMessage.MessageStatus) {
 _messages.value = _messages.value.map { message ->
 if (message.id == messageId && message is ChatMessage.TextMessage) {
 message.copy(status = status)
 } else {
 message
 }
 }
 }

 private fun generateMessageId(): String {
 return "${userId}_${System.currentTimeMillis()}_${(0..999).random()}"
 }

 fun close() {
 webSocketClient.close()
 scope.cancel()
 }
}
```

### UI Implementation with Jetpack Compose

```kotlin
@Composable
fun ChatScreen(
 chatClient: ChatClient,
 viewModel: ChatViewModel = viewModel()
) {
 val messages by chatClient.messages.collectAsState()
 val connectionState by chatClient.connectionState.collectAsState()
 val messageText by viewModel.messageText.collectAsState()

 LaunchedEffect(Unit) {
 chatClient.connect()
 }

 DisposableEffect(Unit) {
 onDispose {
 chatClient.disconnect()
 }
 }

 Scaffold(
 topBar = {
 ChatTopBar(connectionState = connectionState)
 }
 ) { padding ->
 Column(
 modifier = Modifier
 .fillMaxSize()
 .padding(padding)
 ) {
 // Messages list
 LazyColumn(
 modifier = Modifier.weight(1f),
 reverseLayout = true
 ) {
 items(
 items = messages.reversed(),
 key = { it.id }
 ) { message ->
 ChatMessageItem(message = message)
 }
 }

 // Input area
 ChatInput(
 text = messageText,
 onTextChange = { viewModel.updateMessageText(it) },
 onSend = {
 chatClient.sendMessage(messageText)
 viewModel.clearMessageText()
 },
 onTypingChanged = { isTyping ->
 chatClient.sendTypingIndicator(isTyping)
 }
 )
 }
 }
}

@Composable
private fun ChatTopBar(connectionState: ChatClient.ConnectionState) {
 TopAppBar(
 title = {
 Column {
 Text("Chat Room")

 Text(
 text = when (connectionState) {
 is ChatClient.ConnectionState.Connected -> "Connected"
 is ChatClient.ConnectionState.Connecting -> "Connecting..."
 is ChatClient.ConnectionState.Disconnected -> "Disconnected"
 is ChatClient.ConnectionState.Error -> "Error: ${connectionState.message}"
 },
 style = MaterialTheme.typography.bodySmall,
 color = when (connectionState) {
 is ChatClient.ConnectionState.Connected -> Color.Green
 is ChatClient.ConnectionState.Connecting -> Color.Yellow
 else -> Color.Red
 }
 )
 }
 },
 colors = TopAppBarDefaults.topAppBarColors(
 containerColor = MaterialTheme.colorScheme.primaryContainer
 )
 )
}

@Composable
private fun ChatMessageItem(message: ChatMessage) {
 when (message) {
 is ChatMessage.TextMessage -> {
 Row(
 modifier = Modifier
 .fillMaxWidth()
 .padding(8.dp),
 horizontalArrangement = if (message.userId == getCurrentUserId()) {
 Arrangement.End
 } else {
 Arrangement.Start
 }
 ) {
 Surface(
 shape = RoundedCornerShape(8.dp),
 color = if (message.userId == getCurrentUserId()) {
 MaterialTheme.colorScheme.primary
 } else {
 MaterialTheme.colorScheme.surfaceVariant
 }
 ) {
 Column(
 modifier = Modifier.padding(12.dp)
 ) {
 if (message.userId != getCurrentUserId()) {
 Text(
 text = message.userName,
 style = MaterialTheme.typography.labelSmall,
 fontWeight = FontWeight.Bold
 )
 Spacer(modifier = Modifier.height(4.dp))
 }

 Text(text = message.text)

 Row(
 modifier = Modifier.fillMaxWidth(),
 horizontalArrangement = Arrangement.End,
 verticalAlignment = Alignment.CenterVertically
 ) {
 Text(
 text = formatTimestamp(message.timestamp),
 style = MaterialTheme.typography.labelSmall
 )

 if (message.userId == getCurrentUserId()) {
 Spacer(modifier = Modifier.width(4.dp))
 MessageStatusIcon(status = message.status)
 }
 }
 }
 }
 }
 }

 is ChatMessage.UserJoined -> {
 SystemMessage("${message.userName} joined")
 }

 is ChatMessage.UserLeft -> {
 SystemMessage("${message.userName} left")
 }

 else -> {}
 }
}

@Composable
private fun MessageStatusIcon(status: ChatMessage.MessageStatus) {
 val (icon, tint) = when (status) {
 ChatMessage.MessageStatus.SENDING -> Icons.Default.Schedule to Color.Gray
 ChatMessage.MessageStatus.SENT -> Icons.Default.Done to Color.Gray
 ChatMessage.MessageStatus.DELIVERED -> Icons.Default.DoneAll to Color.Gray
 ChatMessage.MessageStatus.READ -> Icons.Default.DoneAll to Color.Blue
 ChatMessage.MessageStatus.FAILED -> Icons.Default.Error to Color.Red
 }

 Icon(
 imageVector = icon,
 contentDescription = status.name,
 modifier = Modifier.size(14.dp),
 tint = tint
 )
}

@Composable
private fun ChatInput(
 text: String,
 onTextChange: (String) -> Unit,
 onSend: () -> Unit,
 onTypingChanged: (Boolean) -> Unit
) {
 var isTyping by remember { mutableStateOf(false) }

 LaunchedEffect(text) {
 if (text.isNotEmpty() && !isTyping) {
 isTyping = true
 onTypingChanged(true)
 } else if (text.isEmpty() && isTyping) {
 isTyping = false
 onTypingChanged(false)
 }

 // Stop typing indicator after 2 seconds of no input
 delay(2000)
 if (isTyping) {
 isTyping = false
 onTypingChanged(false)
 }
 }

 Surface(
 modifier = Modifier.fillMaxWidth(),
 tonalElevation = 3.dp
 ) {
 Row(
 modifier = Modifier.padding(8.dp),
 verticalAlignment = Alignment.CenterVertically
 ) {
 TextField(
 value = text,
 onValueChange = onTextChange,
 modifier = Modifier.weight(1f),
 placeholder = { Text("Type a message...") },
 maxLines = 4
 )

 Spacer(modifier = Modifier.width(8.dp))

 IconButton(
 onClick = {
 if (text.isNotBlank()) {
 onSend()
 }
 },
 enabled = text.isNotBlank()
 ) {
 Icon(Icons.Default.Send, contentDescription = "Send")
 }
 }
 }
}
```

### Best Practices

1. **Automatic Reconnection**: Implement exponential backoff

2. **Heartbeat Mechanism**: Detect stale connections early

3. **`Message` `Queue`**: Store messages when offline

4. **State Management**: Clear connection states for UI

5. **Error Handling**: Graceful degradation on errors

6. **Resource Cleanup**: Close connections properly

7. **Backpressure**: Handle message bursts

8. **Security**: Use WSS (WebSocket Secure) in production

9. **Jitter in Reconnects**: Prevent thundering herd

10. **Testing**: Test reconnection and failure scenarios

### Common Pitfalls

1. **No Heartbeat**: Not detecting dead connections

2. **Infinite Reconnects**: Not limiting retry attempts

3. **Memory Leaks**: Not closing WebSocket properly

4. **No `Message` `Queue`**: Losing messages when offline

5. **Fixed Reconnect Delay**: Overwhelming server on mass disconnect

6. **Not Handling State**: Confusing UI states

7. **Blocking Operations**: Performing long operations in listeners

8. **No Timeouts**: Hanging on connection attempts

### Performance Considerations

```kotlin
// Use compression for large messages
val okHttpClient = OkHttpClient.Builder()
 .addInterceptor { chain ->
 val request = chain.request().newBuilder()
 .header("Sec-WebSocket-Extensions", "permessage-deflate")
 .build()
 chain.proceed(request)
 }
 .build()

// Batch messages when possible
private val messageBatch = mutableListOf<String>()
private val batchJob = scope.launch {
 while (isActive) {
 delay(100) // Batch window
 if (messageBatch.isNotEmpty()) {
 val batch = messageBatch.toList()
 messageBatch.clear()
 sendBatch(batch)
 }
 }
}

// Use binary frames for efficiency
fun sendBinary(data: ByteArray) {
 webSocket.send(ByteString.of(*data))
}
```

### Summary

WebSocket implementation provides:

- **Real-Time Communication**: Bidirectional, low-latency messaging
- **Resilience**: Automatic reconnection with exponential backoff
- **Reliability**: `Message` queuing for offline scenarios
- **Health Monitoring**: Heartbeat mechanism for connection health
- **User Experience**: Clear connection states and error handling
- **Resource Efficiency**: Single persistent connection
- **Scalability**: Proper backpressure and batching

Master WebSocket to build responsive, real-time Android applications.

---

# Question (EN)
> WebSocket Implementation

---

---

## Answer (EN)
**WebSocket** is a protocol providing full-duplex communication channels over a single TCP connection. Unlike HTTP, which is request-response based, WebSocket enables bidirectional, real-time communication between client and server. This makes it ideal for chat applications, live updates, gaming, and any scenario requiring low-latency, bidirectional data flow.

### Why WebSocket?

**Traditional HTTP Polling:**
```
Client: "Any updates?" → Server: "No"
Client: "Any updates?" → Server: "No"
Client: "Any updates?" → Server: "Yes, here's data"
```
- Wasteful: Many empty responses
- High latency: Delays between polls
- Resource intensive: Constant connections

**WebSocket:**
```
Client ←→ Server (persistent connection)
Server: "Here's data" → Client (instant push)
Client: "Here's data" → Server (instant send)
```
- Efficient: Single persistent connection
- Low latency: Instant bidirectional communication
- Resource friendly: One connection for both directions

### WebSocket `Lifecycle`

```

 CLOSED ← Initial state

 connect()
 ↓

 CONNECTING ← Opening handshake

 onOpen()
 ↓

 CONNECTED ← Active communication

 onMessage(), send()
 ping/pong heartbeat

 → Network issue → DISCONNECTED
 → Manual close() → CLOSING → CLOSED
 → onFailure() → DISCONNECTED
 ↓

 DISCONNECTED

 Auto-reconnect (exponential backoff)
 → CONNECTING
```

### Complete WebSocket Client Implementation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import okhttp3.*
import okio.ByteString
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlin.math.pow

class WebSocketClient(
 private val url: String,
 private val okHttpClient: OkHttpClient,
 private val config: Config = Config()
) {

 data class Config(
 val maxReconnectAttempts: Int = Int.MAX_VALUE,
 val initialReconnectDelayMs: Long = 1000L,
 val maxReconnectDelayMs: Long = 30000L,
 val reconnectDelayFactor: Double = 2.0,
 val heartbeatIntervalMs: Long = 30000L,
 val heartbeatTimeoutMs: Long = 10000L,
 val connectionTimeoutMs: Long = 10000L,
 val enableMessageQueue: Boolean = true,
 val maxQueueSize: Int = 100
 )

 sealed class State {
 object Closed : State()
 object Connecting : State()
 data class Connected(val webSocket: WebSocket) : State()
 data class Disconnected(val reason: String, val code: Int?) : State()
 }

 sealed class Event {
 data class MessageReceived(val text: String) : Event()
 data class DataReceived(val bytes: ByteString) : Event()
 data class StateChanged(val state: State) : Event()
 data class Error(val throwable: Throwable) : Event()
 }

 private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

 private val _state = MutableStateFlow<State>(State.Closed)
 val state: StateFlow<State> = _state.asStateFlow()

 private val _events = MutableSharedFlow<Event>(
 extraBufferCapacity = 64,
 onBufferOverflow = BufferOverflow.DROP_OLDEST
 )
 val events: SharedFlow<Event> = _events.asSharedFlow()

 private var currentWebSocket: WebSocket? = null
 private var reconnectAttempt = AtomicInteger(0)
 private var reconnectJob: Job? = null
 private var heartbeatJob: Job? = null

 // Message queue for offline messages
 private val messageQueue = mutableListOf<QueuedMessage>()
 private val queueMutex = kotlinx.coroutines.sync.Mutex()

 private data class QueuedMessage(
 val message: String,
 val timestamp: Long = System.currentTimeMillis()
 )

 // Heartbeat tracking
 private var lastPongReceived = System.currentTimeMillis()
 private var heartbeatMissCount = 0

 fun connect() {
 scope.launch {
 if (_state.value is State.Connected || _state.value is State.Connecting) {
 return@launch
 }

 updateState(State.Connecting)
 performConnect()
 }
 }

 fun disconnect() {
 scope.launch {
 reconnectJob?.cancel()
 heartbeatJob?.cancel()
 currentWebSocket?.close(1000, "Client disconnecting")
 currentWebSocket = null
 updateState(State.Closed)
 }
 }

 fun send(message: String): Boolean {
 val currentState = _state.value

 return if (currentState is State.Connected) {
 currentState.webSocket.send(message)
 } else {
 // Queue message if offline
 if (config.enableMessageQueue) {
 queueMessage(message)
 true
 } else {
 false
 }
 }
 }

 fun send(bytes: ByteString): Boolean {
 val currentState = _state.value
 return if (currentState is State.Connected) {
 currentState.webSocket.send(bytes)
 } else {
 false
 }
 }

 private suspend fun performConnect() {
 try {
 val request = Request.Builder()
 .url(url)
 .build()

 val webSocket = okHttpClient.newWebSocket(request, createWebSocketListener())
 currentWebSocket = webSocket

 // Wait for connection with timeout
 withTimeout(config.connectionTimeoutMs) {
 // Wait until state changes from Connecting
 _state.first { it !is State.Connecting }
 }

 } catch (e: TimeoutCancellationException) {
 updateState(State.Disconnected("Connection timeout", null))
 scheduleReconnect()
 } catch (e: Exception) {
 updateState(State.Disconnected("Connection failed: ${e.message}", null))
 scheduleReconnect()
 }
 }

 private fun createWebSocketListener() = object : WebSocketListener() {

 override fun onOpen(webSocket: WebSocket, response: Response) {
 scope.launch {
 updateState(State.Connected(webSocket))
 reconnectAttempt.set(0)
 startHeartbeat()
 sendQueuedMessages()
 }
 }

 override fun onMessage(webSocket: WebSocket, text: String) {
 scope.launch {
 _events.emit(Event.MessageReceived(text))
 }
 }

 override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
 scope.launch {
 _events.emit(Event.DataReceived(bytes))
 }
 }

 override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
 webSocket.close(1000, null)
 }

 override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
 scope.launch {
 heartbeatJob?.cancel()
 if (code == 1000) {
 // Normal closure
 updateState(State.Closed)
 } else {
 updateState(State.Disconnected(reason, code))
 scheduleReconnect()
 }
 }
 }

 override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
 scope.launch {
 heartbeatJob?.cancel()
 _events.emit(Event.Error(t))

 val reason = response?.message ?: t.message ?: "Unknown error"
 val code = response?.code
 updateState(State.Disconnected(reason, code))
 scheduleReconnect()
 }
 }
 }

 private fun startHeartbeat() {
 heartbeatJob?.cancel()
 lastPongReceived = System.currentTimeMillis()
 heartbeatMissCount = 0

 heartbeatJob = scope.launch {
 while (isActive) {
 delay(config.heartbeatIntervalMs)

 val currentState = _state.value
 if (currentState !is State.Connected) {
 break
 }

 // Check if we received pong response
 val timeSinceLastPong = System.currentTimeMillis() - lastPongReceived
 if (timeSinceLastPong > config.heartbeatTimeoutMs) {
 heartbeatMissCount++

 if (heartbeatMissCount >= 3) {
 // Connection appears dead, reconnect
 currentWebSocket?.close(1001, "Heartbeat timeout")
 break
 }
 }

 // Send ping
 currentState.webSocket.send("ping")
 }
 }
 }

 fun onPongReceived() {
 lastPongReceived = System.currentTimeMillis()
 heartbeatMissCount = 0
 }

 private fun scheduleReconnect() {
 reconnectJob?.cancel()

 if (reconnectAttempt.get() >= config.maxReconnectAttempts) {
 return
 }

 val attempt = reconnectAttempt.getAndIncrement()
 val delay = calculateReconnectDelay(attempt)

 reconnectJob = scope.launch {
 delay(delay)

 if (_state.value is State.Disconnected) {
 updateState(State.Connecting)
 performConnect()
 }
 }
 }

 private fun calculateReconnectDelay(attempt: Int): Long {
 val exponentialDelay = config.initialReconnectDelayMs *
 config.reconnectDelayFactor.pow(attempt).toLong()

 val delayWithCap = exponentialDelay.coerceAtMost(config.maxReconnectDelayMs)

 // Add jitter (±10%) to prevent thundering herd
 val jitter = (delayWithCap * 0.1 * (Math.random() - 0.5)).toLong()

 return delayWithCap + jitter
 }

 private fun queueMessage(message: String) {
 scope.launch {
 queueMutex.withLock {
 if (messageQueue.size >= config.maxQueueSize) {
 messageQueue.removeAt(0) // Remove oldest
 }
 messageQueue.add(QueuedMessage(message))
 }
 }
 }

 private suspend fun sendQueuedMessages() {
 queueMutex.withLock {
 val currentState = _state.value
 if (currentState is State.Connected) {
 messageQueue.forEach { queued ->
 currentState.webSocket.send(queued.message)
 }
 messageQueue.clear()
 }
 }
 }

 private suspend fun updateState(newState: State) {
 _state.value = newState
 _events.emit(Event.StateChanged(newState))
 }

 fun close() {
 disconnect()
 scope.cancel()
 }
}
```

### Chat `Application` Example

Complete chat application using WebSocket:

```kotlin
// Chat Message Models
@Serializable
sealed class ChatMessage {
 abstract val id: String
 abstract val timestamp: Long

 @Serializable
 @SerialName("text")
 data class TextMessage(
 override val id: String,
 val userId: String,
 val userName: String,
 val text: String,
 override val timestamp: Long,
 val status: MessageStatus = MessageStatus.SENT
 ) : ChatMessage()

 @Serializable
 @SerialName("typing")
 data class TypingIndicator(
 override val id: String,
 val userId: String,
 val userName: String,
 val isTyping: Boolean,
 override val timestamp: Long
 ) : ChatMessage()

 @Serializable
 @SerialName("user_joined")
 data class UserJoined(
 override val id: String,
 val userId: String,
 val userName: String,
 override val timestamp: Long
 ) : ChatMessage()

 @Serializable
 @SerialName("user_left")
 data class UserLeft(
 override val id: String,
 val userId: String,
 val userName: String,
 override val timestamp: Long
 ) : ChatMessage()

 enum class MessageStatus {
 SENDING, SENT, DELIVERED, READ, FAILED
 }
}

// Chat Client
class ChatClient(
 private val webSocketUrl: String,
 private val userId: String,
 private val userName: String,
 okHttpClient: OkHttpClient
) {

 private val json = Json {
 ignoreUnknownKeys = true
 classDiscriminator = "type"
 }

 private val webSocketClient = WebSocketClient(
 url = webSocketUrl,
 okHttpClient = okHttpClient,
 config = WebSocketClient.Config(
 heartbeatIntervalMs = 30000L,
 enableMessageQueue = true,
 maxQueueSize = 50
 )
 )

 private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
 val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

 private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
 val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

 sealed class ConnectionState {
 object Connected : ConnectionState()
 object Connecting : ConnectionState()
 object Disconnected : ConnectionState()
 data class Error(val message: String) : ConnectionState()
 }

 private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

 init {
 observeWebSocketEvents()
 }

 private fun observeWebSocketEvents() {
 scope.launch {
 webSocketClient.state.collect { state ->
 _connectionState.value = when (state) {
 is WebSocketClient.State.Connected -> ConnectionState.Connected
 is WebSocketClient.State.Connecting -> ConnectionState.Connecting
 is WebSocketClient.State.Closed -> ConnectionState.Disconnected
 is WebSocketClient.State.Disconnected ->
 ConnectionState.Error(state.reason)
 }
 }
 }

 scope.launch {
 webSocketClient.events.collect { event ->
 when (event) {
 is WebSocketClient.Event.MessageReceived -> {
 handleIncomingMessage(event.text)
 }

 is WebSocketClient.Event.Error -> {
 _connectionState.value = ConnectionState.Error(
 event.throwable.message ?: "Unknown error"
 )
 }

 else -> {}
 }
 }
 }
 }

 fun connect() {
 webSocketClient.connect()
 }

 fun disconnect() {
 webSocketClient.disconnect()
 }

 fun sendMessage(text: String) {
 val message = ChatMessage.TextMessage(
 id = generateMessageId(),
 userId = userId,
 userName = userName,
 text = text,
 timestamp = System.currentTimeMillis(),
 status = ChatMessage.MessageStatus.SENDING
 )

 // Optimistically add to messages
 addMessage(message)

 // Send via WebSocket
 val jsonString = json.encodeToString(ChatMessage.serializer(), message)
 val sent = webSocketClient.send(jsonString)

 if (!sent) {
 // Update status to failed
 updateMessageStatus(message.id, ChatMessage.MessageStatus.FAILED)
 } else {
 updateMessageStatus(message.id, ChatMessage.MessageStatus.SENT)
 }
 }

 fun sendTypingIndicator(isTyping: Boolean) {
 val message = ChatMessage.TypingIndicator(
 id = generateMessageId(),
 userId = userId,
 userName = userName,
 isTyping = isTyping,
 timestamp = System.currentTimeMillis()
 )

 val jsonString = json.encodeToString(ChatMessage.serializer(), message)
 webSocketClient.send(jsonString)
 }

 fun retrySendMessage(messageId: String) {
 val message = _messages.value.find { it.id == messageId }
 if (message is ChatMessage.TextMessage) {
 val jsonString = json.encodeToString(ChatMessage.serializer(), message)
 val sent = webSocketClient.send(jsonString)

 updateMessageStatus(
 messageId,
 if (sent) ChatMessage.MessageStatus.SENDING else ChatMessage.MessageStatus.FAILED
 )
 }
 }

 private fun handleIncomingMessage(jsonString: String) {
 try {
 val message = json.decodeFromString<ChatMessage>(jsonString)

 // Handle special message types
 when (message) {
 is ChatMessage.TypingIndicator -> {
 // Update typing state (not added to messages list)
 // Could emit to separate typing indicators flow
 }

 else -> {
 addMessage(message)
 }
 }

 // Handle pong for heartbeat
 if (jsonString == "pong") {
 webSocketClient.onPongReceived()
 }

 } catch (e: Exception) {
 // Log parse error
 }
 }

 private fun addMessage(message: ChatMessage) {
 _messages.value = _messages.value + message
 }

 private fun updateMessageStatus(messageId: String, status: ChatMessage.MessageStatus) {
 _messages.value = _messages.value.map { message ->
 if (message.id == messageId && message is ChatMessage.TextMessage) {
 message.copy(status = status)
 } else {
 message
 }
 }
 }

 private fun generateMessageId(): String {
 return "${userId}_${System.currentTimeMillis()}_${(0..999).random()}"
 }

 fun close() {
 webSocketClient.close()
 scope.cancel()
 }
}
```

### UI Implementation with Jetpack Compose

```kotlin
@Composable
fun ChatScreen(
 chatClient: ChatClient,
 viewModel: ChatViewModel = viewModel()
) {
 val messages by chatClient.messages.collectAsState()
 val connectionState by chatClient.connectionState.collectAsState()
 val messageText by viewModel.messageText.collectAsState()

 LaunchedEffect(Unit) {
 chatClient.connect()
 }

 DisposableEffect(Unit) {
 onDispose {
 chatClient.disconnect()
 }
 }

 Scaffold(
 topBar = {
 ChatTopBar(connectionState = connectionState)
 }
 ) { padding ->
 Column(
 modifier = Modifier
 .fillMaxSize()
 .padding(padding)
 ) {
 // Messages list
 LazyColumn(
 modifier = Modifier.weight(1f),
 reverseLayout = true
 ) {
 items(
 items = messages.reversed(),
 key = { it.id }
 ) { message ->
 ChatMessageItem(message = message)
 }
 }

 // Input area
 ChatInput(
 text = messageText,
 onTextChange = { viewModel.updateMessageText(it) },
 onSend = {
 chatClient.sendMessage(messageText)
 viewModel.clearMessageText()
 },
 onTypingChanged = { isTyping ->
 chatClient.sendTypingIndicator(isTyping)
 }
 )
 }
 }
}

@Composable
private fun ChatTopBar(connectionState: ChatClient.ConnectionState) {
 TopAppBar(
 title = {
 Column {
 Text("Chat Room")

 Text(
 text = when (connectionState) {
 is ChatClient.ConnectionState.Connected -> "Connected"
 is ChatClient.ConnectionState.Connecting -> "Connecting..."
 is ChatClient.ConnectionState.Disconnected -> "Disconnected"
 is ChatClient.ConnectionState.Error -> "Error: ${connectionState.message}"
 },
 style = MaterialTheme.typography.bodySmall,
 color = when (connectionState) {
 is ChatClient.ConnectionState.Connected -> Color.Green
 is ChatClient.ConnectionState.Connecting -> Color.Yellow
 else -> Color.Red
 }
 )
 }
 },
 colors = TopAppBarDefaults.topAppBarColors(
 containerColor = MaterialTheme.colorScheme.primaryContainer
 )
 )
}

@Composable
private fun ChatMessageItem(message: ChatMessage) {
 when (message) {
 is ChatMessage.TextMessage -> {
 Row(
 modifier = Modifier
 .fillMaxWidth()
 .padding(8.dp),
 horizontalArrangement = if (message.userId == getCurrentUserId()) {
 Arrangement.End
 } else {
 Arrangement.Start
 }
 ) {
 Surface(
 shape = RoundedCornerShape(8.dp),
 color = if (message.userId == getCurrentUserId()) {
 MaterialTheme.colorScheme.primary
 } else {
 MaterialTheme.colorScheme.surfaceVariant
 }
 ) {
 Column(
 modifier = Modifier.padding(12.dp)
 ) {
 if (message.userId != getCurrentUserId()) {
 Text(
 text = message.userName,
 style = MaterialTheme.typography.labelSmall,
 fontWeight = FontWeight.Bold
 )
 Spacer(modifier = Modifier.height(4.dp))
 }

 Text(text = message.text)

 Row(
 modifier = Modifier.fillMaxWidth(),
 horizontalArrangement = Arrangement.End,
 verticalAlignment = Alignment.CenterVertically
 ) {
 Text(
 text = formatTimestamp(message.timestamp),
 style = MaterialTheme.typography.labelSmall
 )

 if (message.userId == getCurrentUserId()) {
 Spacer(modifier = Modifier.width(4.dp))
 MessageStatusIcon(status = message.status)
 }
 }
 }
 }
 }
 }

 is ChatMessage.UserJoined -> {
 SystemMessage("${message.userName} joined")
 }

 is ChatMessage.UserLeft -> {
 SystemMessage("${message.userName} left")
 }

 else -> {}
 }
}

@Composable
private fun MessageStatusIcon(status: ChatMessage.MessageStatus) {
 val (icon, tint) = when (status) {
 ChatMessage.MessageStatus.SENDING -> Icons.Default.Schedule to Color.Gray
 ChatMessage.MessageStatus.SENT -> Icons.Default.Done to Color.Gray
 ChatMessage.MessageStatus.DELIVERED -> Icons.Default.DoneAll to Color.Gray
 ChatMessage.MessageStatus.READ -> Icons.Default.DoneAll to Color.Blue
 ChatMessage.MessageStatus.FAILED -> Icons.Default.Error to Color.Red
 }

 Icon(
 imageVector = icon,
 contentDescription = status.name,
 modifier = Modifier.size(14.dp),
 tint = tint
 )
}

@Composable
private fun ChatInput(
 text: String,
 onTextChange: (String) -> Unit,
 onSend: () -> Unit,
 onTypingChanged: (Boolean) -> Unit
) {
 var isTyping by remember { mutableStateOf(false) }

 LaunchedEffect(text) {
 if (text.isNotEmpty() && !isTyping) {
 isTyping = true
 onTypingChanged(true)
 } else if (text.isEmpty() && isTyping) {
 isTyping = false
 onTypingChanged(false)
 }

 // Stop typing indicator after 2 seconds of no input
 delay(2000)
 if (isTyping) {
 isTyping = false
 onTypingChanged(false)
 }
 }

 Surface(
 modifier = Modifier.fillMaxWidth(),
 tonalElevation = 3.dp
 ) {
 Row(
 modifier = Modifier.padding(8.dp),
 verticalAlignment = Alignment.CenterVertically
 ) {
 TextField(
 value = text,
 onValueChange = onTextChange,
 modifier = Modifier.weight(1f),
 placeholder = { Text("Type a message...") },
 maxLines = 4
 )

 Spacer(modifier = Modifier.width(8.dp))

 IconButton(
 onClick = {
 if (text.isNotBlank()) {
 onSend()
 }
 },
 enabled = text.isNotBlank()
 ) {
 Icon(Icons.Default.Send, contentDescription = "Send")
 }
 }
 }
}
```

### Best Practices

1. **Automatic Reconnection**: Implement exponential backoff

2. **Heartbeat Mechanism**: Detect stale connections early

3. **`Message` `Queue`**: Store messages when offline

4. **State Management**: Clear connection states for UI

5. **Error Handling**: Graceful degradation on errors

6. **Resource Cleanup**: Close connections properly

7. **Backpressure**: Handle message bursts

8. **Security**: Use WSS (WebSocket Secure) in production

9. **Jitter in Reconnects**: Prevent thundering herd

10. **Testing**: Test reconnection and failure scenarios

### Common Pitfalls

1. **No Heartbeat**: Not detecting dead connections

2. **Infinite Reconnects**: Not limiting retry attempts

3. **Memory Leaks**: Not closing WebSocket properly

4. **No `Message` `Queue`**: Losing messages when offline

5. **Fixed Reconnect Delay**: Overwhelming server on mass disconnect

6. **Not Handling State**: Confusing UI states

7. **Blocking Operations**: Performing long operations in listeners

8. **No Timeouts**: Hanging on connection attempts

### Performance Considerations

```kotlin
// Use compression for large messages
val okHttpClient = OkHttpClient.Builder()
 .addInterceptor { chain ->
 val request = chain.request().newBuilder()
 .header("Sec-WebSocket-Extensions", "permessage-deflate")
 .build()
 chain.proceed(request)
 }
 .build()

// Batch messages when possible
private val messageBatch = mutableListOf<String>()
private val batchJob = scope.launch {
 while (isActive) {
 delay(100) // Batch window
 if (messageBatch.isNotEmpty()) {
 val batch = messageBatch.toList()
 messageBatch.clear()
 sendBatch(batch)
 }
 }
}

// Use binary frames for efficiency
fun sendBinary(data: ByteArray) {
 webSocket.send(ByteString.of(*data))
}
```

### Summary

WebSocket implementation provides:

- **Real-Time Communication**: Bidirectional, low-latency messaging
- **Resilience**: Automatic reconnection with exponential backoff
- **Reliability**: `Message` queuing for offline scenarios
- **Health Monitoring**: Heartbeat mechanism for connection health
- **User Experience**: Clear connection states and error handling
- **Resource Efficiency**: Single persistent connection
- **Scalability**: Proper backpressure and batching

Master WebSocket to build responsive, real-time Android applications.

---

## Ответ (RU)
**WebSocket** - протокол, обеспечивающий полнодуплексные каналы связи через одно TCP-соединение. В отличие от HTTP, который основан на запрос-ответ, WebSocket позволяет двунаправленную связь в реальном времени между клиентом и сервером. Это идеально для чат-приложений, живых обновлений, игр и любых сценариев, требующих низколатентного двунаправленного потока данных.

### Зачем WebSocket?

**Традиционный HTTP Polling:**
```
Клиент: "Есть обновления?" → Сервер: "Нет"
Клиент: "Есть обновления?" → Сервер: "Нет"
Клиент: "Есть обновления?" → Сервер: "Да, вот данные"
```
- Расточительно: Много пустых ответов
- Высокая задержка: Интервалы между опросами
- Ресурсоемко: Постоянные соединения

**WebSocket:**
```
Клиент ←→ Сервер (постоянное соединение)
Сервер: "Вот данные" → Клиент (мгновенный push)
Клиент: "Вот данные" → Сервер (мгновенная отправка)
```
- Эффективно: Одно постоянное соединение
- Низкая задержка: Мгновенная двунаправленная связь
- Дружественно к ресурсам: Одно соединение в обоих направлениях

### Жизненный Цикл WebSocket

```

 CLOSED ← Начальное состояние

 connect()
 ↓

 CONNECTING ← Открытие handshake

 onOpen()
 ↓

 CONNECTED ← Активная коммуникация

 onMessage(), send()
 ping/pong heartbeat

 → Сетевая проблема → DISCONNECTED
 → Ручной close() → CLOSING → CLOSED
 → onFailure() → DISCONNECTED
 ↓

 DISCONNECTED

 Авто-переподключение
 → CONNECTING
```

### Полная Реализация WebSocket Клиента

```kotlin
class WebSocketClient(
 private val url: String,
 private val okHttpClient: OkHttpClient,
 private val config: Config = Config()
) {

 data class Config(
 val maxReconnectAttempts: Int = Int.MAX_VALUE,
 val initialReconnectDelayMs: Long = 1000L,
 val maxReconnectDelayMs: Long = 30000L,
 val reconnectDelayFactor: Double = 2.0,
 val heartbeatIntervalMs: Long = 30000L,
 val enableMessageQueue: Boolean = true,
 val maxQueueSize: Int = 100
 )

 sealed class State {
 object Closed : State()
 object Connecting : State()
 data class Connected(val webSocket: WebSocket) : State()
 data class Disconnected(val reason: String) : State()
 }

 private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

 private val _state = MutableStateFlow<State>(State.Closed)
 val state: StateFlow<State> = _state.asStateFlow()

 private var currentWebSocket: WebSocket? = null
 private var reconnectAttempt = AtomicInteger(0)
 private var heartbeatJob: Job? = null
 private val messageQueue = mutableListOf<String>()

 fun connect() {
 scope.launch {
 if (_state.value is State.Connected || _state.value is State.Connecting) {
 return@launch
 }

 _state.value = State.Connecting
 performConnect()
 }
 }

 fun send(message: String): Boolean {
 val currentState = _state.value

 return if (currentState is State.Connected) {
 currentState.webSocket.send(message)
 } else {
 if (config.enableMessageQueue) {
 queueMessage(message)
 true
 } else {
 false
 }
 }
 }

 private suspend fun performConnect() {
 try {
 val request = Request.Builder().url(url).build()
 val webSocket = okHttpClient.newWebSocket(request, createWebSocketListener())
 currentWebSocket = webSocket
 } catch (e: Exception) {
 _state.value = State.Disconnected("Connection failed")
 scheduleReconnect()
 }
 }

 private fun createWebSocketListener() = object : WebSocketListener() {

 override fun onOpen(webSocket: WebSocket, response: Response) {
 scope.launch {
 _state.value = State.Connected(webSocket)
 reconnectAttempt.set(0)
 startHeartbeat()
 sendQueuedMessages()
 }
 }

 override fun onMessage(webSocket: WebSocket, text: String) {
 // Handle incoming message
 }

 override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
 scope.launch {
 heartbeatJob?.cancel()
 if (code == 1000) {
 _state.value = State.Closed
 } else {
 _state.value = State.Disconnected(reason)
 scheduleReconnect()
 }
 }
 }

 override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
 scope.launch {
 heartbeatJob?.cancel()
 _state.value = State.Disconnected(t.message ?: "Unknown error")
 scheduleReconnect()
 }
 }
 }

 private fun startHeartbeat() {
 heartbeatJob?.cancel()

 heartbeatJob = scope.launch {
 while (isActive) {
 delay(config.heartbeatIntervalMs)

 val currentState = _state.value
 if (currentState is State.Connected) {
 currentState.webSocket.send("ping")
 } else {
 break
 }
 }
 }
 }

 private fun scheduleReconnect() {
 if (reconnectAttempt.get() >= config.maxReconnectAttempts) {
 return
 }

 val attempt = reconnectAttempt.getAndIncrement()
 val delay = calculateReconnectDelay(attempt)

 scope.launch {
 delay(delay)
 if (_state.value is State.Disconnected) {
 _state.value = State.Connecting
 performConnect()
 }
 }
 }

 private fun calculateReconnectDelay(attempt: Int): Long {
 val exponentialDelay = (config.initialReconnectDelayMs *
 config.reconnectDelayFactor.pow(attempt)).toLong()

 return exponentialDelay.coerceAtMost(config.maxReconnectDelayMs)
 }

 private fun queueMessage(message: String) {
 if (messageQueue.size >= config.maxQueueSize) {
 messageQueue.removeAt(0)
 }
 messageQueue.add(message)
 }

 private fun sendQueuedMessages() {
 val currentState = _state.value
 if (currentState is State.Connected) {
 messageQueue.forEach { message ->
 currentState.webSocket.send(message)
 }
 messageQueue.clear()
 }
 }
}
```

### Пример Чат-приложения

```kotlin
@Serializable
sealed class ChatMessage {
 abstract val id: String
 abstract val timestamp: Long

 @Serializable
 data class TextMessage(
 override val id: String,
 val userId: String,
 val userName: String,
 val text: String,
 override val timestamp: Long
 ) : ChatMessage()
}

class ChatClient(
 private val webSocketUrl: String,
 okHttpClient: OkHttpClient
) {

 private val webSocketClient = WebSocketClient(
 url = webSocketUrl,
 okHttpClient = okHttpClient
 )

 private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
 val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

 fun connect() {
 webSocketClient.connect()
 }

 fun sendMessage(text: String) {
 val message = ChatMessage.TextMessage(
 id = generateId(),
 userId = getCurrentUserId(),
 userName = getCurrentUserName(),
 text = text,
 timestamp = System.currentTimeMillis()
 )

 val json = Json.encodeToString(message)
 webSocketClient.send(json)
 }
}
```

### UI С Jetpack Compose

```kotlin
@Composable
fun ChatScreen(chatClient: ChatClient) {
 val messages by chatClient.messages.collectAsState()

 LaunchedEffect(Unit) {
 chatClient.connect()
 }

 Column(modifier = Modifier.fillMaxSize()) {
 LazyColumn(
 modifier = Modifier.weight(1f),
 reverseLayout = true
 ) {
 items(messages.reversed()) { message ->
 ChatMessageItem(message = message)
 }
 }

 ChatInput(onSend = { text ->
 chatClient.sendMessage(text)
 })
 }
}
```

### Best Practices

1. **Автоматическое переподключение**: Экспоненциальная задержка

2. **Механизм heartbeat**: Раннее обнаружение мёртвых соединений

3. **Очередь сообщений**: Хранение при оффлайн

4. **Управление состоянием**: Чёткие состояния для UI

5. **Обработка ошибок**: Изящная деградация

6. **Очистка ресурсов**: Правильное закрытие

7. **Безопасность**: WSS в production

8. **Jitter**: Предотвращение thundering herd

### Распространённые Ошибки

1. **Нет heartbeat**: Не обнаруживаются мёртвые соединения

2. **Бесконечные переподключения**: Не ограничивать попытки

3. **Утечки памяти**: Не закрывать WebSocket

4. **Нет очереди**: Потеря сообщений оффлайн

5. **Фиксированная задержка**: Перегрузка сервера

### Резюме

Реализация WebSocket обеспечивает:

- **Связь в реальном времени**: Двунаправленный обмен с низкой задержкой
- **Устойчивость**: Автоматическое переподключение
- **Надёжность**: Очередь сообщений
- **Мониторинг здоровья**: Heartbeat механизм
- **UX**: Чёткие состояния и обработка ошибок
- **Эффективность**: Одно постоянное соединение

## Follow-ups

- 
- 
- [[q-what-are-services-for--android--easy]]

## References

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)
- [App Startup Time](https://developer.android.com/topic/performance/vitals/launch-time)

## Related Questions

- [[q-parcelable-implementation--android--medium]]
- [[q-what-problems-can-there-be-with-list-items--android--easy]]
- [[q-leakcanary-heap-dump-analysis--android--medium]]
