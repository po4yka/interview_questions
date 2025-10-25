---
id: 20251012-12271177
title: "Real Time Updates Android / Обновления в реальном времени Android"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-alternative-distribution--distribution--medium, q-mlkit-face-detection--ml--medium, q-what-navigation-methods-exist-in-kotlin--programming-languages--medium]
created: 2025-10-15
tags: [networking, websockets, sse, firebase, fcm, real-time, difficulty/medium]
---

# How to Implement Real-Time Updates in Android

# Вопрос (RU)
>

---

## Answer (EN)
# Question (EN)
How do you implement real-time updates in Android applications? What are the available technologies and best practices?

## Answer (EN)
Real-time updates enable instant data synchronization between server and client, essential for chat apps, collaborative tools, live feeds, and notifications. There are several approaches with different trade-offs.

#### 1. **WebSockets**

WebSockets provide full-duplex communication over a single TCP connection.

**Setup with OkHttp:**

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
}
```

**Implementation:**

```kotlin
class WebSocketManager(
    private val client: OkHttpClient,
    private val url: String
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<Message>(replay = 0)
    val messages: SharedFlow<Message> = _messages.asSharedFlow()

    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

    private val listener = object : WebSocketListener() {
        override fun onOpen(webSocket: WebSocket, response: Response) {
            _connectionState.value = ConnectionState.Connected
            Log.d("WebSocket", "Connection opened")
        }

        override fun onMessage(webSocket: WebSocket, text: String) {
            try {
                val message = Json.decodeFromString<Message>(text)
                CoroutineScope(Dispatchers.IO).launch {
                    _messages.emit(message)
                }
            } catch (e: Exception) {
                Log.e("WebSocket", "Failed to parse message", e)
            }
        }

        override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
            _connectionState.value = ConnectionState.Disconnecting
            Log.d("WebSocket", "Connection closing: $code $reason")
        }

        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            _connectionState.value = ConnectionState.Disconnected
            Log.d("WebSocket", "Connection closed: $code $reason")
        }

        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            _connectionState.value = ConnectionState.Error(t.message ?: "Unknown error")
            Log.e("WebSocket", "Connection failed", t)

            // Auto-reconnect with exponential backoff
            scheduleReconnect()
        }
    }

    fun connect() {
        if (webSocket != null) {
            disconnect()
        }

        val request = Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer ${getAuthToken()}")
            .build()

        webSocket = client.newWebSocket(request, listener)
        _connectionState.value = ConnectionState.Connecting
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        webSocket = null
    }

    fun sendMessage(message: Message) {
        val json = Json.encodeToString(message)
        webSocket?.send(json)
    }

    private var reconnectAttempts = 0
    private val maxReconnectAttempts = 5
    private val reconnectDelayMs = 1000L

    private fun scheduleReconnect() {
        if (reconnectAttempts >= maxReconnectAttempts) {
            _connectionState.value = ConnectionState.Error("Max reconnect attempts reached")
            return
        }

        val delay = reconnectDelayMs * (1 shl reconnectAttempts) // Exponential backoff
        reconnectAttempts++

        CoroutineScope(Dispatchers.IO).launch {
            delay(delay)
            connect()
        }
    }

    fun resetReconnectAttempts() {
        reconnectAttempts = 0
    }
}

sealed class ConnectionState {
    object Disconnected : ConnectionState()
    object Connecting : ConnectionState()
    object Connected : ConnectionState()
    object Disconnecting : ConnectionState()
    data class Error(val message: String) : ConnectionState()
}

@Serializable
data class Message(
    val id: String,
    val type: String,
    val content: String,
    val timestamp: Long,
    val userId: String
)
```

**Usage in Repository:**

```kotlin
class ChatRepository(
    private val webSocketManager: WebSocketManager,
    private val messageDao: MessageDao
) {
    init {
        // Collect messages and save to local database
        CoroutineScope(Dispatchers.IO).launch {
            webSocketManager.messages.collect { message ->
                messageDao.insert(message.toEntity())
            }
        }
    }

    fun getMessagesFlow(): Flow<List<Message>> = messageDao.getAllMessagesFlow()

    val connectionState = webSocketManager.connectionState

    fun connect() = webSocketManager.connect()

    fun disconnect() = webSocketManager.disconnect()

    fun sendMessage(content: String) {
        val message = Message(
            id = UUID.randomUUID().toString(),
            type = "chat",
            content = content,
            timestamp = System.currentTimeMillis(),
            userId = getCurrentUserId()
        )

        // Save locally first (offline-first)
        CoroutineScope(Dispatchers.IO).launch {
            messageDao.insert(message.toEntity())
        }

        // Send via WebSocket
        webSocketManager.sendMessage(message)
    }
}
```

#### 2. **Server-Sent Events (SSE)**

SSE provides one-way real-time updates from server to client.

```kotlin
class SSEClient(
    private val url: String,
    private val client: OkHttpClient
) {
    private val _events = MutableSharedFlow<ServerEvent>()
    val events: SharedFlow<ServerEvent> = _events.asSharedFlow()

    private var isConnected = false

    fun connect() {
        if (isConnected) return

        val request = Request.Builder()
            .url(url)
            .addHeader("Accept", "text/event-stream")
            .addHeader("Authorization", "Bearer ${getAuthToken()}")
            .build()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = client.newCall(request).execute()
                if (!response.isSuccessful) {
                    throw IOException("Unexpected code $response")
                }

                isConnected = true
                val source = response.body?.source() ?: throw IOException("Response body is null")

                while (isConnected && !source.exhausted()) {
                    val line = source.readUtf8Line() ?: break

                    when {
                        line.startsWith("data:") -> {
                            val data = line.substring(5).trim()
                            val event = parseServerEvent(data)
                            _events.emit(event)
                        }
                        line.startsWith("event:") -> {
                            // Handle custom event types
                        }
                        line.startsWith("id:") -> {
                            // Handle event ID for resuming
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("SSE", "Connection failed", e)
                isConnected = false
                // Reconnect logic
                delay(5000)
                connect()
            }
        }
    }

    fun disconnect() {
        isConnected = false
    }

    private fun parseServerEvent(data: String): ServerEvent {
        return Json.decodeFromString(data)
    }
}

@Serializable
data class ServerEvent(
    val type: String,
    val data: JsonElement,
    val timestamp: Long
)
```

#### 3. **Firebase Realtime Database**

```kotlin
class FirebaseRealtimeRepository(
    private val database: FirebaseDatabase
) {
    private val messagesRef = database.getReference("messages")

    // Listen to real-time updates
    fun getMessagesFlow(chatId: String): Flow<List<Message>> = callbackFlow {
        val listener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                val messages = snapshot.children.mapNotNull {
                    it.getValue(Message::class.java)
                }
                trySend(messages)
            }

            override fun onCancelled(error: DatabaseError) {
                close(error.toException())
            }
        }

        messagesRef.child(chatId).addValueEventListener(listener)

        awaitClose {
            messagesRef.child(chatId).removeEventListener(listener)
        }
    }

    // Listen to child added events
    fun observeNewMessages(chatId: String): Flow<Message> = callbackFlow {
        val listener = object : ChildEventListener {
            override fun onChildAdded(snapshot: DataSnapshot, previousChildName: String?) {
                snapshot.getValue(Message::class.java)?.let { trySend(it) }
            }

            override fun onChildChanged(snapshot: DataSnapshot, previousChildName: String?) {}
            override fun onChildRemoved(snapshot: DataSnapshot) {}
            override fun onChildMoved(snapshot: DataSnapshot, previousChildName: String?) {}
            override fun onCancelled(error: DatabaseError) {
                close(error.toException())
            }
        }

        messagesRef.child(chatId).addChildEventListener(listener)

        awaitClose {
            messagesRef.child(chatId).removeEventListener(listener)
        }
    }

    // Send message
    suspend fun sendMessage(chatId: String, message: Message) {
        messagesRef.child(chatId).push().setValue(message).await()
    }

    // Update message
    suspend fun updateMessage(chatId: String, messageId: String, updates: Map<String, Any>) {
        messagesRef.child(chatId).child(messageId).updateChildren(updates).await()
    }
}
```

#### 4. **Firebase Cloud Messaging (FCM) for Push Notifications**

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        Log.d("FCM", "From: ${remoteMessage.from}")

        // Handle data payload
        remoteMessage.data.isNotEmpty().let {
            Log.d("FCM", "Message data payload: ${remoteMessage.data}")
            handleDataMessage(remoteMessage.data)
        }

        // Handle notification payload
        remoteMessage.notification?.let {
            Log.d("FCM", "Message Notification Body: ${it.body}")
            showNotification(it.title, it.body)
        }
    }

    override fun onNewToken(token: String) {
        Log.d("FCM", "New token: $token")
        // Send token to server
        sendTokenToServer(token)
    }

    private fun handleDataMessage(data: Map<String, String>) {
        when (data["type"]) {
            "new_message" -> {
                val messageId = data["message_id"]
                val chatId = data["chat_id"]
                // Fetch and update local database
                fetchAndStoreMessage(messageId, chatId)
            }
            "update" -> {
                val entityType = data["entity_type"]
                val entityId = data["entity_id"]
                // Trigger sync for specific entity
                syncEntity(entityType, entityId)
            }
        }
    }

    private fun showNotification(title: String?, body: String?) {
        val notificationManager = getSystemService<NotificationManager>()

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(body)
            .setSmallIcon(R.drawable.ic_notification)
            .setAutoCancel(true)
            .build()

        notificationManager?.notify(Random.nextInt(), notification)
    }
}
```

#### 5. **Polling (Fallback Strategy)**

```kotlin
class PollingManager(
    private val apiService: ApiService,
    private val scope: CoroutineScope
) {
    private var pollingJob: Job? = null
    private val pollingIntervalMs = 5000L

    fun startPolling(chatId: String, onUpdate: (List<Message>) -> Unit) {
        stopPolling()

        pollingJob = scope.launch {
            var lastTimestamp = 0L

            while (isActive) {
                try {
                    val response = apiService.getMessages(chatId, since = lastTimestamp)
                    if (response.isSuccessful) {
                        response.body()?.let { messages ->
                            if (messages.isNotEmpty()) {
                                onUpdate(messages)
                                lastTimestamp = messages.maxOf { it.timestamp }
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e("Polling", "Failed to fetch updates", e)
                }

                delay(pollingIntervalMs)
            }
        }
    }

    fun stopPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }
}
```

#### 6. **Long Polling**

```kotlin
class LongPollingManager(
    private val apiService: ApiService,
    private val scope: CoroutineScope
) {
    private var pollingJob: Job? = null

    fun startLongPolling(chatId: String, onUpdate: (List<Message>) -> Unit) {
        stopLongPolling()

        pollingJob = scope.launch {
            var lastMessageId: String? = null

            while (isActive) {
                try {
                    // Server holds request open until new data arrives or timeout
                    val response = apiService.longPollMessages(
                        chatId = chatId,
                        lastMessageId = lastMessageId,
                        timeout = 30000 // 30 seconds
                    )

                    if (response.isSuccessful) {
                        response.body()?.let { messages ->
                            if (messages.isNotEmpty()) {
                                onUpdate(messages)
                                lastMessageId = messages.last().id
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e("LongPolling", "Failed to fetch updates", e)
                    delay(1000) // Brief delay before reconnecting
                }
            }
        }
    }

    fun stopLongPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }
}
```

#### 7. **Combining Strategies with Lifecycle Awareness**

```kotlin
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository,
    private val networkMonitor: NetworkMonitor
) : ViewModel() {

    private val webSocketManager = chatRepository.webSocketManager

    val messages = chatRepository.getMessagesFlow()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    val connectionState = chatRepository.connectionState
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = ConnectionState.Disconnected
        )

    init {
        // Monitor network state and connect/disconnect accordingly
        viewModelScope.launch {
            networkMonitor.observeNetworkStatus().collect { status ->
                when (status) {
                    is NetworkStatus.Available -> {
                        chatRepository.connect()
                    }
                    is NetworkStatus.Lost -> {
                        chatRepository.disconnect()
                    }
                }
            }
        }
    }

    fun sendMessage(content: String) {
        chatRepository.sendMessage(content)
    }

    override fun onCleared() {
        super.onCleared()
        chatRepository.disconnect()
    }
}

@Composable
fun ChatScreen(viewModel: ChatViewModel = hiltViewModel()) {
    val messages by viewModel.messages.collectAsState()
    val connectionState by viewModel.connectionState.collectAsState()

    DisposableEffect(Unit) {
        // Component becomes active
        onDispose {
            // Component is being disposed
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Chat") },
                actions = {
                    ConnectionIndicator(connectionState)
                }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            LazyColumn(
                modifier = Modifier.weight(1f),
                reverseLayout = true
            ) {
                items(messages) { message ->
                    MessageItem(message)
                }
            }

            MessageInput(
                onSendMessage = { content ->
                    viewModel.sendMessage(content)
                },
                enabled = connectionState is ConnectionState.Connected
            )
        }
    }
}
```

### Technology Comparison

| Technology | Use Case | Pros | Cons |
|------------|----------|------|------|
| WebSockets | Chat, gaming, real-time collaboration | Full-duplex, low latency | Connection management, battery drain |
| SSE | Live feeds, notifications | Simple, auto-reconnect | One-way, limited browser support |
| Firebase | MVP, rapid development | Easy setup, scalable | Vendor lock-in, costs |
| FCM | Push notifications | Reliable, cross-platform | Requires Google services |
| Polling | Simple updates | Easy to implement | High server load, delayed updates |
| Long Polling | Medium-frequency updates | Better than polling | Still resource-intensive |

### Best Practices

**Connection Management:**
- [ ] Implement auto-reconnect with exponential backoff
- [ ] Handle lifecycle events (pause/resume)
- [ ] Disconnect when app is in background
- [ ] Monitor network connectivity

**Performance:**
- [ ] Batch updates when possible
- [ ] Implement local caching
- [ ] Use compression for messages
- [ ] Limit message history in memory
- [ ] Implement pagination

**Security:**
- [ ] Use secure WebSocket (wss://)
- [ ] Implement authentication
- [ ] Validate all incoming messages
- [ ] Encrypt sensitive data
- [ ] Implement rate limiting

**User Experience:**
- [ ] Show connection status
- [ ] Handle offline gracefully
- [ ] Implement optimistic updates
- [ ] Show message delivery status
- [ ] Provide retry mechanisms

---



## Ответ (RU)

Обновления в реальном времени обеспечивают мгновенную синхронизацию данных между сервером и клиентом, что критически важно для чатов, инструментов совместной работы, live-лент и уведомлений. Существует несколько подходов с различными компромиссами.

#### Технологии:

**1. WebSockets**
- Полнодуплексная связь через одно TCP-соединение
- Низкая задержка
- Подходит для чатов, игр, совместной работы
- Требует управления соединением и расходует батарею

**2. Server-Sent Events (SSE)**
- Односторонние обновления от сервера к клиенту
- Простая реализация
- Автоматическое переподключение
- Подходит для live-лент, уведомлений

**3. Firebase Realtime Database**
- Быстрое развертывание и разработка MVP
- Автоматическая синхронизация
- Масштабируемость из коробки
- Привязка к вендору и стоимость

**4. Firebase Cloud Messaging (FCM)**
- Push-уведомления
- Надежная доставка
- Кроссплатформенность
- Требует Google Services

**5. Polling/Long Polling**
- Простая реализация в качестве fallback
- Long Polling держит соединение открытым до получения данных
- Высокая нагрузка на сервер
- Задержки в обновлениях

#### Лучшие практики:

**Управление соединением:**
- Автопереподключение с экспоненциальной задержкой
- Обработка lifecycle-событий (pause/resume)
- Отключение в фоне для экономии батареи
- Мониторинг сетевого подключения

**Производительность:**
- Пакетная обработка обновлений
- Локальное кэширование данных
- Сжатие сообщений
- Ограничение истории сообщений в памяти
- Пагинация

**Безопасность:**
- Защищенное соединение WebSocket (wss://)
- Реализация аутентификации
- Валидация всех входящих сообщений
- Шифрование чувствительных данных
- Rate limiting

**UX:**
- Отображение статуса соединения
- Обработка offline-режима
- Optimistic updates для мгновенного отклика
- Отображение статуса доставки сообщений
- Механизмы повторной отправки

## Related Questions

- [[q-alternative-distribution--android--medium]]
- q-mlkit-face-detection--ml--medium
- [[q-what-navigation-methods-exist-in-kotlin--android--medium]]
