---
id: android-092
title: WebSocket Implementation / Реализация WebSocket
aliases: [WebSocket Implementation, Реализация WebSocket]
topic: android
subtopics:
  - connectivity-caching
  - coroutines
  - websockets
question_kind: coding
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android
  - q-cache-implementation-strategies--android--medium
  - q-custom-drawable-implementation--android--medium
  - q-http-protocols-comparison--android--medium
  - q-what-are-services-for--android--easy
created: 2025-10-13
updated: 2025-11-10
tags: [android/connectivity-caching, android/coroutines, android/websockets, difficulty/medium, okhttp, real-time, resilience, websocket]

date created: Saturday, November 1st 2025, 12:47:06 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)
> Реализация WebSocket-клиента на Android (устойчивое, отказоустойчивое подключение для реального времени)

# Question (EN)
> Implement a resilient, fault-tolerant real-time WebSocket client on Android.

---

## Ответ (RU)
**WebSocket** — протокол, обеспечивающий дуплексную (full-duplex) связь поверх одного TCP-соединения. В отличие от HTTP с моделью запрос–ответ, WebSocket даёт двунаправленное, почти мгновенное взаимодействие между клиентом и сервером. Это делает его подходящим для чатов, лайв-обновлений, игр и любых сценариев с низкой задержкой.

### Зачем Нужен WebSocket? (RU)

**Классический HTTP-polling:**
```text
Клиент: "Есть обновления?"  Сервер: "Нет"
Клиент: "Есть обновления?"  Сервер: "Нет"
Клиент: "Есть обновления?"  Сервер: "Да, вот данные"
```
- Ресурсоёмко: множество пустых ответов
- Задержки: ожидание между запросами
- Нагрузка: постоянные запросы и обработка

**WebSocket:**
```text
Клиент  — Сервер (постоянное соединение)
Сервер: "Вот данные"  (моментальный push)
Клиент: "Вот данные"  (моментальная отправка)
```
- Эффективно: одно постоянное соединение
- Низкая задержка: мгновенная двунаправленная доставка
- Экономно: один канал для обоих направлений

### Жизненный Цикл WebSocket (RU)

```text
   CLOSED      Начальное состояние

        connect()
       

 CONNECTING    Открывающий handshake

        onOpen()
       

  CONNECTED    Активное взаимодействие

        onMessage(), send()
        ping/pong heartbeat

        Сетевой сбой   DISCONNECTED
        Ручное close()  CLOSING  CLOSED
        onFailure()   DISCONNECTED
                

       DISCONNECTED

               Авто-переподключение (экспоненциальный backoff с jitter)
               CONNECTING
```

Ключевые состояния клиента:
- Closed — нет активного соединения
- Connecting — идёт установление соединения
- Connected — можно отправлять/принимать сообщения
- Disconnected — соединение потеряно, может запускаться логика переподключения в зависимости от конфигурации

### Полная Реализация WebSocket-клиента (RU)

Ниже — устойчивый клиент на базе `OkHttp` и `coroutines` с:
- явными состояниями
- потоком событий
- переподключением (экспоненциальный backoff с jitter, управляется `Config`)
- heartbeat (использует ping/pong на уровне протокола и пример app-level ping)
- опциональной очередью сообщений

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.sync.withLock
import okhttp3.*
import okio.ByteString
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

    // Очередь сообщений для офлайн-буфера (асинхронная)
    private val messageQueue = mutableListOf<QueuedMessage>()
    private val queueMutex = kotlinx.coroutines.sync.Mutex()

    private data class QueuedMessage(
        val message: String,
        val timestamp: Long = System.currentTimeMillis()
    )

    // Отслеживание heartbeat (на уровне приложения поверх ping/pong)
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
            if (config.enableMessageQueue) {
                // добавляем в очередь асинхронно; используется как best-effort офлайн-буфер
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

            // Ждём установления соединения с таймаутом
            withTimeout(config.connectionTimeoutMs) {
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

                // Пример примитивного app-level pong по тексту "pong"
                if (text == "pong") {
                    onPongReceived()
                }
            }
        }

        override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
            scope.launch {
                _events.emit(Event.DataReceived(bytes))
            }
        }

        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            scope.launch {
                heartbeatJob?.cancel()
                if (code == 1000) {
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

        // При наличии ping/pong на уровне протокола
        override fun onPong(webSocket: WebSocket, bytes: ByteString) {
            scope.launch {
                onPongReceived()
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

                val timeSinceLastPong = System.currentTimeMillis() - lastPongReceived
                if (timeSinceLastPong > config.heartbeatTimeoutMs) {
                    heartbeatMissCount++

                    if (heartbeatMissCount >= 3) {
                        // Закрываем соединение из-за отсутствия heartbeat;
                        // в реальном приложении выбирайте подходящий код/ reason.
                        currentWebSocket?.close(1000, "Heartbeat timeout")
                        break
                    }
                }

                currentState.webSocket.send("ping")
            }
        }
    }

    private fun onPongReceived() {
        lastPongReceived = System.currentTimeMillis()
        heartbeatMissCount = 0
    }

    private fun scheduleReconnect() {
        reconnectJob?.cancel()

        if (reconnectAttempt.get() >= config.maxReconnectAttempts) {
            return
        }

        val attempt = reconnectAttempt.getAndIncrement()
        val delayMs = calculateReconnectDelay(attempt)

        reconnectJob = scope.launch {
            delay(delayMs)

            if (_state.value is State.Disconnected) {
                updateState(State.Connecting)
                performConnect()
            }
        }
    }

    private fun calculateReconnectDelay(attempt: Int): Long {
        val exponentialDelay = (config.initialReconnectDelayMs *
            config.reconnectDelayFactor.pow(attempt)).toLong()

        val delayWithCap = exponentialDelay.coerceAtMost(config.maxReconnectDelayMs)

        // Jitter (~10%), чтобы избежать одновременных переподключений
        val jitter = (delayWithCap * 0.1 * (Math.random() - 0.5)).toLong()

        return (delayWithCap + jitter).coerceAtLeast(0L)
    }

    private fun queueMessage(message: String) {
        scope.launch {
            queueMutex.withLock {
                if (messageQueue.size >= config.maxQueueSize) {
                    messageQueue.removeAt(0)
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

### Пример Чат-клиента (`Application`-level) (RU)

Над `WebSocketClient` строим чатовый клиент с моделями сообщений, состояниями и обработкой событий.

Примечание: вспомогательные функции и компоненты UI (например, `getCurrentUserId`, `formatTimestamp`, `SystemMessage`, `ChatViewModel`) считаются псевдо-кодом / плейсхолдерами для интервью.

```kotlin
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

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

        addMessage(message)

        val jsonString = json.encodeToString(ChatMessage.serializer(), message)
        val sent = webSocketClient.send(jsonString)

        if (!sent) {
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

            when (message) {
                is ChatMessage.TypingIndicator -> {
                    // обновить индикатор набора текста в UI при необходимости
                }

                else -> {
                    addMessage(message)
                }
            }
        } catch (e: Exception) {
            // логируем ошибку парсинга
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

### UI На Jetpack Compose (RU)

Экран чата, использующий `ChatClient` и отображающий состояние соединения и список сообщений.

```kotlin
import androidx.compose.runtime.*
import androidx.compose.material3.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.Alignment
import androidx.compose.ui.text.font.FontWeight
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*

@Composable
fun ChatScreen(
    chatClient: ChatClient,
    viewModel: ChatViewModel = viewModel()
) {
    val messages by chatClient.messages.collectAsState()
    val connectionState by chatClient.connectionState.collectAsState()
    val messageText by viewModel.messageText.collectAsState()

    // Для простоты: привязка к жизненному циклу Composable.
    // В продакшене чаще используют уровень ViewModel/Screen.
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

### Лучшие Практики (RU)

1. Автопереподключение с экспоненциальным backoff и jitter (через конфигurable `Config`).
2. Heartbeat (app-level или ping/pong) для обнаружения мёртвых соединений.
3. Очередь сообщений с лимитами для офлайн-буфера.
4. Явное управление состояниями для UI (Connected/Connecting/Disconnected/Error).
5. Надёжная обработка ошибок и логирование.
6. Корректное освобождение ресурсов (корутины, закрытие WebSocket).
7. Обработка backpressure и, при необходимости, батчинг.
8. Использование WSS (TLS) в продакшене.
9. Тестирование сценариев отказов и переподключений.

### Типичные Ошибки (RU)

1. Отсутствие heartbeat и, как следствие, "висящие" соединения.
2. Бесконечные переподключения без ограничений.
3. Утечки памяти из-за незакрытых WebSocket/корутин.
4. Отсутствие очереди сообщений и потеря данных.
5. Фиксированная задержка между попытками, перегружающая сервер.
6. Неконсистентное управление состоянием, запутанный UI.
7. Блокирующие операции внутри колбэков WebSocket.
8. Отсутствие таймаутов для начального подключения.

### Производительность (RU)

```kotlin
// Базовый OkHttp-клиент для WebSocket
val okHttpClient = OkHttpClient.Builder()
    .build()

// Отправка бинарных фреймов через WebSocketClient
fun sendBinary(webSocketClient: WebSocketClient, data: ByteArray) {
    webSocketClient.send(ByteString.of(*data))
}
```

### Итог (RU)

Реализация WebSocket на Android должна обеспечивать:
- реальное время и двунаправленный обмен
- устойчивость за счёт переподключения с backoff
- надёжность через очередь сообщений (при необходимости)
- мониторинг здоровья соединения (heartbeat)
- хороший UX за счёт понятных состояний и обработки ошибок
- эффективность благодаря одному постоянному соединению

---

## Answer (EN)
**WebSocket** is a protocol providing full-duplex communication channels over a single TCP connection. Unlike HTTP, which is request-response based, WebSocket enables bidirectional, real-time communication between client and server. This makes it ideal for chat applications, live updates, gaming, and any scenario requiring low-latency, bidirectional data flow.

### Why WebSocket? (EN)

**Traditional HTTP Polling:**
```text
Client: "Any updates?"  Server: "No"
Client: "Any updates?"  Server: "No"
Client: "Any updates?"  Server: "Yes, here's data"
```
- Wasteful: Many empty responses
- High latency: Delays between polls
- Resource intensive: Constant requests

**WebSocket:**
```text
Client  Server (persistent connection)
Server: "Here's data"  (instant push)
Client: "Here's data"  (instant send)
```
- Efficient: Single persistent connection
- Low latency: Instant bidirectional communication
- Resource friendly: One connection for both directions

### WebSocket Lifecycle (EN)

```text
   CLOSED      Initial state

        connect()
       

 CONNECTING    Opening handshake

        onOpen()
       

  CONNECTED    Active communication

        onMessage(), send()
        ping/pong heartbeat

        Network issue  DISCONNECTED
        Manual close()  CLOSING  CLOSED
        onFailure()  DISCONNECTED
                

       DISCONNECTED

               Auto-reconnect (exponential backoff with jitter)
               CONNECTING
```

Key client states:
- Closed: no active connection
- Connecting: establishing connection
- Connected: can send/receive messages
- Disconnected: connection lost; reconnection logic may run depending on configuration

### Complete WebSocket Client Implementation (EN)

Below is the same resilient `WebSocketClient` as in the RU section (OkHttp + coroutines) with:
- explicit states
- event stream
- reconnection using exponential backoff with jitter (configured via `Config`)
- heartbeat (uses protocol ping/pong and an example app-level ping)
- optional message queue

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.sync.withLock
import okhttp3.*
import okio.ByteString
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

    // Message queue for offline buffering (asynchronous)
    private val messageQueue = mutableListOf<QueuedMessage>()
    private val queueMutex = kotlinx.coroutines.sync.Mutex()

    private data class QueuedMessage(
        val message: String,
        val timestamp: Long = System.currentTimeMillis()
    )

    // Heartbeat tracking (app-level on top of protocol ping/pong)
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
            if (config.enableMessageQueue) {
                // enqueue asynchronously; used as best-effort offline buffer
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

            // Wait for connection establishment with timeout
            withTimeout(config.connectionTimeoutMs) {
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

                // Example of simple app-level pong reaction on "pong" text
                if (text == "pong") {
                    onPongReceived()
                }
            }
        }

        override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
            scope.launch {
                _events.emit(Event.DataReceived(bytes))
            }
        }

        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            scope.launch {
                heartbeatJob?.cancel()
                if (code == 1000) {
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

        override fun onPong(webSocket: WebSocket, bytes: ByteString) {
            scope.launch {
                onPongReceived()
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

                val timeSinceLastPong = System.currentTimeMillis() - lastPongReceived
                if (timeSinceLastPong > config.heartbeatTimeoutMs) {
                    heartbeatMissCount++

                    if (heartbeatMissCount >= 3) {
                        // Close due to missing heartbeat; choose appropriate code/reason in real apps
                        currentWebSocket?.close(1000, "Heartbeat timeout")
                        break
                    }
                }

                currentState.webSocket.send("ping")
            }
        }
    }

    private fun onPongReceived() {
        lastPongReceived = System.currentTimeMillis()
        heartbeatMissCount = 0
    }

    private fun scheduleReconnect() {
        reconnectJob?.cancel()

        if (reconnectAttempt.get() >= config.maxReconnectAttempts) {
            return
        }

        val attempt = reconnectAttempt.getAndIncrement()
        val delayMs = calculateReconnectDelay(attempt)

        reconnectJob = scope.launch {
            delay(delayMs)

            if (_state.value is State.Disconnected) {
                updateState(State.Connecting)
                performConnect()
            }
        }
    }

    private fun calculateReconnectDelay(attempt: Int): Long {
        val exponentialDelay = (config.initialReconnectDelayMs *
            config.reconnectDelayFactor.pow(attempt)).toLong()

        val delayWithCap = exponentialDelay.coerceAtMost(config.maxReconnectDelayMs)

        // Jitter (~10%) to avoid thundering herd on reconnect
        val jitter = (delayWithCap * 0.1 * (Math.random() - 0.5)).toLong()

        return (delayWithCap + jitter).coerceAtLeast(0L)
    }

    private fun queueMessage(message: String) {
        scope.launch {
            queueMutex.withLock {
                if (messageQueue.size >= config.maxQueueSize) {
                    messageQueue.removeAt(0)
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

### Chat Client Example (`Application` Level) (EN)

Same as in the RU section, the `ChatClient` wraps `WebSocketClient` and models messages and connection state.

Note: helpers like `getCurrentUserId`, `formatTimestamp`, `SystemMessage`, and `ChatViewModel` are placeholders/pseudo-code for interview purposes.

```kotlin
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

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

        addMessage(message)

        val jsonString = json.encodeToString(ChatMessage.serializer(), message)
        val sent = webSocketClient.send(jsonString)

        if (!sent) {
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

            when (message) {
                is ChatMessage.TypingIndicator -> {
                    // update typing indicator in UI if needed
                }

                else -> {
                    addMessage(message)
                }
            }
        } catch (e: Exception) {
            // log parse error
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

### UI Implementation with Jetpack Compose (EN)

Mirrors the RU section: chat screen using `ChatClient`, showing connection state and messages.

```kotlin
import androidx.compose.runtime.*
import androidx.compose.material3.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.Alignment
import androidx.compose.ui.text.font.FontWeight
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*

@Composable
fun ChatScreen(
    chatClient: ChatClient,
    viewModel: ChatViewModel = viewModel()
) {
    val messages by chatClient.messages.collectAsState()
    val connectionState by chatClient.connectionState.collectAsState()
    val messageText by viewModel.messageText.collectAsState()

    // Simpler lifecycle binding for the example; production apps often use ViewModel scope
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

### Best Practices (EN)

1. Automatic reconnection with exponential backoff and jitter (via configurable `Config`).
2. Heartbeat mechanism (app-level or protocol ping/pong) to detect stale connections.
3. Message queue with limits for offline buffering.
4. Explicit state management for UI (Connected/Connecting/Disconnected/Error).
5. Robust error handling and logging.
6. Proper resource cleanup (cancel coroutines, close WebSocket).
7. Backpressure handling and batching where needed.
8. Use WSS (TLS) in production.
9. Test failure and reconnection scenarios thoroughly.

### Common Pitfalls (EN)

1. Missing heartbeat, leading to hanging connections.
2. Infinite reconnection without limits.
3. Memory leaks from not closing WebSocket/coroutines.
4. No message queue, causing message loss.
5. Fixed reconnect delays that overload the server.
6. Inconsistent state management and confusing UI.
7. Blocking work inside WebSocket callbacks.
8. Missing timeouts for initial connection.

### Performance Considerations (EN)

```kotlin
val okHttpClient = OkHttpClient.Builder()
    .build()

fun sendBinary(webSocketClient: WebSocketClient, data: ByteArray) {
    webSocketClient.send(ByteString.of(*data))
}
```

### Summary (EN)

A production-grade WebSocket implementation on Android should provide:
- real-time, bidirectional communication
- resilience with reconnection and backoff
- reliability through optional message queuing
- connection health monitoring (heartbeat)
- clear UX via explicit states and error handling
- efficiency via a single persistent connection

---

## Дополнительные Вопросы (RU)

- [[q-what-are-services-for--android--easy]]
- Как адаптировать этот WebSocket-клиент для поддержки аутентификации (например, JWT, обновление токенов и переподключение)?
- Как обрабатывать версионирование протокола и обратную совместимость сообщений?
- Как тестировать переподключение, гонки и отказоустойчивость этого клиента?
- Когда вы выберете WebSocket вместо HTTP/2 streaming, Server-Sent Events или gRPC на Android?

## Follow-ups (EN)

- [[q-what-are-services-for--android--easy]]
- How would you adapt this WebSocket client to support authentication (e.g., JWT refresh and reconnection)?
- How would you handle protocol versioning and backward compatibility for messages?
- How would you test reconnection, race conditions, and failure modes for this client?
- When would you choose WebSocket over HTTP/2 streaming, Server-Sent Events, or gRPC for Android?

## Ссылки (RU)

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)
- [App Startup Time](https://developer.android.com/topic/performance/vitals/launch-time)
- [[c-android]]

## References (EN)

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)
- [App Startup Time](https://developer.android.com/topic/performance/vitals/launch-time)
- [[c-android]]

## Связанные Вопросы (RU)

- [[q-parcelable-implementation--android--medium]]
- [[q-what-problems-can-there-be-with-list-items--android--easy]]
- [[q-leakcanary-heap-dump-analysis--android--medium]]

## Related Questions (EN)

- [[q-parcelable-implementation--android--medium]]
- [[q-what-problems-can-there-be-with-list-items--android--easy]]
- [[q-leakcanary-heap-dump-analysis--android--medium]]
