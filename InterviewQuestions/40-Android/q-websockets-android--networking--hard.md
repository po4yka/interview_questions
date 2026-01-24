---
id: android-751
title: "WebSocket Implementation on Android / Реализация WebSocket на Android"
aliases: ["WebSocket Implementation on Android", "Реализация WebSocket на Android"]
topic: android
subtopics: [networking]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-networking, q-real-time-updates-android--android--medium, q-ktor-client--networking--medium]
created: 2026-01-23
updated: 2026-01-23
sources: ["https://square.github.io/okhttp/features/websockets/", "https://ktor.io/docs/client-websockets.html", "https://developer.android.com/guide/background/persistent/getting-started/using-ws"]
tags: [android/networking, difficulty/hard, websocket, okhttp, real-time, bidirectional-communication]

---
# Вопрос (RU)

> Как реализовать WebSocket соединение на Android? Объясните OkHttp WebSocket, управление жизненным циклом и стратегии переподключения.

# Question (EN)

> How do you implement WebSocket connections on Android? Explain OkHttp WebSocket, lifecycle management, and reconnection strategies.

---

## Ответ (RU)

**WebSocket** - протокол полнодуплексной связи поверх одного TCP-соединения, позволяющий серверу отправлять данные клиенту без запроса. На Android основные реализации - **OkHttp WebSocket** и **Ktor WebSocket**.

### Краткий Ответ

- **WebSocket** обеспечивает двунаправленную связь в реальном времени
- **OkHttp WebSocket** - зрелая, стабильная реализация для Android
- Критичны: управление жизненным циклом, reconnect с exponential backoff, heartbeat
- Используйте **Flow** для реактивной обработки сообщений

### Подробный Ответ

### OkHttp WebSocket: Базовая Реализация

```kotlin
class WebSocketManager(
    private val okHttpClient: OkHttpClient
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<WebSocketMessage>(
        replay = 0,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val messages: SharedFlow<WebSocketMessage> = _messages.asSharedFlow()

    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

    fun connect(url: String) {
        if (_connectionState.value == ConnectionState.Connected) return

        _connectionState.value = ConnectionState.Connecting

        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = okHttpClient.newWebSocket(request, createListener())
    }

    private fun createListener() = object : WebSocketListener() {
        override fun onOpen(webSocket: WebSocket, response: Response) {
            _connectionState.value = ConnectionState.Connected
            _messages.tryEmit(WebSocketMessage.Connected)
        }

        override fun onMessage(webSocket: WebSocket, text: String) {
            _messages.tryEmit(WebSocketMessage.Text(text))
        }

        override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
            _messages.tryEmit(WebSocketMessage.Binary(bytes.toByteArray()))
        }

        override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
            webSocket.close(code, reason)
        }

        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            _connectionState.value = ConnectionState.Disconnected
            _messages.tryEmit(WebSocketMessage.Closed(code, reason))
        }

        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            _connectionState.value = ConnectionState.Error(t)
            _messages.tryEmit(WebSocketMessage.Error(t))
        }
    }

    fun send(message: String): Boolean {
        return webSocket?.send(message) ?: false
    }

    fun send(bytes: ByteArray): Boolean {
        return webSocket?.send(bytes.toByteString()) ?: false
    }

    fun disconnect(code: Int = 1000, reason: String = "Normal closure") {
        webSocket?.close(code, reason)
        webSocket = null
    }
}

sealed class WebSocketMessage {
    data object Connected : WebSocketMessage()
    data class Text(val content: String) : WebSocketMessage()
    data class Binary(val bytes: ByteArray) : WebSocketMessage()
    data class Closed(val code: Int, val reason: String) : WebSocketMessage()
    data class Error(val throwable: Throwable) : WebSocketMessage()
}

sealed class ConnectionState {
    data object Disconnected : ConnectionState()
    data object Connecting : ConnectionState()
    data object Connected : ConnectionState()
    data class Error(val throwable: Throwable) : ConnectionState()
}
```

### Reconnect с Exponential Backoff

```kotlin
class ReconnectingWebSocketManager(
    private val okHttpClient: OkHttpClient,
    private val scope: CoroutineScope
) {
    private var webSocket: WebSocket? = null
    private var reconnectJob: Job? = null
    private var reconnectAttempt = 0
    private var shouldReconnect = true

    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

    private val _messages = MutableSharedFlow<String>(extraBufferCapacity = 64)
    val messages: SharedFlow<String> = _messages.asSharedFlow()

    companion object {
        private const val INITIAL_BACKOFF_MS = 1000L
        private const val MAX_BACKOFF_MS = 30_000L
        private const val BACKOFF_MULTIPLIER = 2.0
        private const val MAX_RECONNECT_ATTEMPTS = 10
    }

    fun connect(url: String) {
        shouldReconnect = true
        reconnectAttempt = 0
        establishConnection(url)
    }

    private fun establishConnection(url: String) {
        _connectionState.value = ConnectionState.Connecting

        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                reconnectAttempt = 0 // Сброс счетчика при успешном подключении
                _connectionState.value = ConnectionState.Connected
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                _messages.tryEmit(text)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                handleDisconnection(url)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _connectionState.value = ConnectionState.Error(t)
                handleDisconnection(url)
            }
        })
    }

    private fun handleDisconnection(url: String) {
        if (!shouldReconnect) {
            _connectionState.value = ConnectionState.Disconnected
            return
        }

        if (reconnectAttempt >= MAX_RECONNECT_ATTEMPTS) {
            _connectionState.value = ConnectionState.Disconnected
            return
        }

        reconnectJob = scope.launch {
            val backoffMs = calculateBackoff(reconnectAttempt)
            _connectionState.value = ConnectionState.Reconnecting(backoffMs)

            delay(backoffMs)
            reconnectAttempt++
            establishConnection(url)
        }
    }

    private fun calculateBackoff(attempt: Int): Long {
        val backoff = INITIAL_BACKOFF_MS * BACKOFF_MULTIPLIER.pow(attempt.toDouble())
        val jitter = (0..1000).random() // Jitter для предотвращения thundering herd
        return (backoff.toLong() + jitter).coerceAtMost(MAX_BACKOFF_MS)
    }

    fun disconnect() {
        shouldReconnect = false
        reconnectJob?.cancel()
        webSocket?.close(1000, "User disconnect")
        webSocket = null
        _connectionState.value = ConnectionState.Disconnected
    }

    sealed class ConnectionState {
        data object Disconnected : ConnectionState()
        data object Connecting : ConnectionState()
        data object Connected : ConnectionState()
        data class Reconnecting(val backoffMs: Long) : ConnectionState()
        data class Error(val throwable: Throwable) : ConnectionState()
    }
}
```

### Heartbeat (Ping/Pong)

```kotlin
class HeartbeatWebSocketManager(
    private val okHttpClient: OkHttpClient,
    private val scope: CoroutineScope
) {
    private var webSocket: WebSocket? = null
    private var heartbeatJob: Job? = null
    private var lastPongTime = AtomicLong(0)

    companion object {
        private const val HEARTBEAT_INTERVAL_MS = 30_000L
        private const val PONG_TIMEOUT_MS = 10_000L
    }

    private fun startHeartbeat() {
        heartbeatJob = scope.launch {
            while (isActive) {
                delay(HEARTBEAT_INTERVAL_MS)

                // Проверяем, получили ли pong на предыдущий ping
                val timeSinceLastPong = System.currentTimeMillis() - lastPongTime.get()
                if (lastPongTime.get() > 0 && timeSinceLastPong > HEARTBEAT_INTERVAL_MS + PONG_TIMEOUT_MS) {
                    // Соединение потеряно
                    handleConnectionLost()
                    break
                }

                // Отправляем ping (OkHttp автоматически обрабатывает pong)
                webSocket?.send("ping")
            }
        }
    }

    private fun stopHeartbeat() {
        heartbeatJob?.cancel()
        heartbeatJob = null
    }

    private fun handleConnectionLost() {
        webSocket?.cancel()
        // Инициировать переподключение
    }

    fun onPongReceived() {
        lastPongTime.set(System.currentTimeMillis())
    }
}
```

### Интеграция с ViewModel и Lifecycle

```kotlin
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val webSocketManager: ReconnectingWebSocketManager,
    private val messageRepository: MessageRepository
) : ViewModel() {

    val connectionState = webSocketManager.connectionState
        .stateIn(viewModelScope, SharingStarted.Eagerly, ConnectionState.Disconnected)

    val messages = webSocketManager.messages
        .map { json -> parseMessage(json) }
        .catch { e -> emit(ChatMessage.Error(e.message ?: "Parse error")) }
        .stateIn(viewModelScope, SharingStarted.Eagerly, null)

    init {
        // Автоматическое подключение при создании ViewModel
        connect()

        // Сохранение сообщений в локальную БД
        viewModelScope.launch {
            messages.filterNotNull().collect { message ->
                if (message is ChatMessage.Incoming) {
                    messageRepository.saveMessage(message)
                }
            }
        }
    }

    fun connect() {
        webSocketManager.connect("wss://chat.example.com/ws")
    }

    fun sendMessage(text: String) {
        val message = ChatMessage.Outgoing(
            id = UUID.randomUUID().toString(),
            text = text,
            timestamp = System.currentTimeMillis()
        )
        val json = Json.encodeToString(message)
        webSocketManager.send(json)
    }

    override fun onCleared() {
        super.onCleared()
        webSocketManager.disconnect()
    }

    private fun parseMessage(json: String): ChatMessage {
        return Json.decodeFromString<ChatMessage>(json)
    }
}
```

### Ktor WebSocket (Альтернатива)

```kotlin
class KtorWebSocketManager(
    private val client: HttpClient
) {
    private var session: DefaultClientWebSocketSession? = null

    suspend fun connect(url: String, onMessage: (String) -> Unit) {
        client.webSocket(url) {
            session = this

            // Получение сообщений
            for (frame in incoming) {
                when (frame) {
                    is Frame.Text -> onMessage(frame.readText())
                    is Frame.Binary -> { /* handle binary */ }
                    is Frame.Close -> break
                    else -> {}
                }
            }
        }
    }

    suspend fun send(message: String) {
        session?.send(Frame.Text(message))
    }

    suspend fun close() {
        session?.close(CloseReason(CloseReason.Codes.NORMAL, "User disconnect"))
    }
}

// Настройка Ktor Client с WebSocket
val client = HttpClient(OkHttp) {
    install(WebSockets) {
        pingInterval = 30_000
        maxFrameSize = Long.MAX_VALUE
    }
}
```

### Лучшие Практики

1. **Lifecycle-aware** - привязывайте WebSocket к жизненному циклу (ViewModel, Service)
2. **Reconnect стратегия** - exponential backoff с jitter
3. **Heartbeat** - регулярные ping/pong для обнаружения потери соединения
4. **Буферизация сообщений** - очередь исходящих при reconnect
5. **Оффлайн-режим** - сохраняйте сообщения локально
6. **Безопасность** - всегда используйте WSS (WebSocket Secure)
7. **Сериализация** - JSON или Protobuf для структурированных данных

---

## Answer (EN)

**WebSocket** is a full-duplex communication protocol over a single TCP connection, allowing the server to push data to the client without request. On Android, main implementations are **OkHttp WebSocket** and **Ktor WebSocket**.

### Short Version

- **WebSocket** enables bidirectional real-time communication
- **OkHttp WebSocket** - mature, stable implementation for Android
- Critical: lifecycle management, reconnect with exponential backoff, heartbeat
- Use **Flow** for reactive message handling

### Detailed Version

### OkHttp WebSocket: Basic Implementation

```kotlin
class WebSocketManager(
    private val okHttpClient: OkHttpClient
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<WebSocketMessage>(
        replay = 0,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val messages: SharedFlow<WebSocketMessage> = _messages.asSharedFlow()

    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

    fun connect(url: String) {
        if (_connectionState.value == ConnectionState.Connected) return

        _connectionState.value = ConnectionState.Connecting

        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = okHttpClient.newWebSocket(request, createListener())
    }

    private fun createListener() = object : WebSocketListener() {
        override fun onOpen(webSocket: WebSocket, response: Response) {
            _connectionState.value = ConnectionState.Connected
            _messages.tryEmit(WebSocketMessage.Connected)
        }

        override fun onMessage(webSocket: WebSocket, text: String) {
            _messages.tryEmit(WebSocketMessage.Text(text))
        }

        override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
            _messages.tryEmit(WebSocketMessage.Binary(bytes.toByteArray()))
        }

        override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
            webSocket.close(code, reason)
        }

        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            _connectionState.value = ConnectionState.Disconnected
            _messages.tryEmit(WebSocketMessage.Closed(code, reason))
        }

        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            _connectionState.value = ConnectionState.Error(t)
            _messages.tryEmit(WebSocketMessage.Error(t))
        }
    }

    fun send(message: String): Boolean {
        return webSocket?.send(message) ?: false
    }

    fun send(bytes: ByteArray): Boolean {
        return webSocket?.send(bytes.toByteString()) ?: false
    }

    fun disconnect(code: Int = 1000, reason: String = "Normal closure") {
        webSocket?.close(code, reason)
        webSocket = null
    }
}

sealed class WebSocketMessage {
    data object Connected : WebSocketMessage()
    data class Text(val content: String) : WebSocketMessage()
    data class Binary(val bytes: ByteArray) : WebSocketMessage()
    data class Closed(val code: Int, val reason: String) : WebSocketMessage()
    data class Error(val throwable: Throwable) : WebSocketMessage()
}

sealed class ConnectionState {
    data object Disconnected : ConnectionState()
    data object Connecting : ConnectionState()
    data object Connected : ConnectionState()
    data class Error(val throwable: Throwable) : ConnectionState()
}
```

### Reconnect with Exponential Backoff

```kotlin
class ReconnectingWebSocketManager(
    private val okHttpClient: OkHttpClient,
    private val scope: CoroutineScope
) {
    private var webSocket: WebSocket? = null
    private var reconnectJob: Job? = null
    private var reconnectAttempt = 0
    private var shouldReconnect = true

    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

    private val _messages = MutableSharedFlow<String>(extraBufferCapacity = 64)
    val messages: SharedFlow<String> = _messages.asSharedFlow()

    companion object {
        private const val INITIAL_BACKOFF_MS = 1000L
        private const val MAX_BACKOFF_MS = 30_000L
        private const val BACKOFF_MULTIPLIER = 2.0
        private const val MAX_RECONNECT_ATTEMPTS = 10
    }

    fun connect(url: String) {
        shouldReconnect = true
        reconnectAttempt = 0
        establishConnection(url)
    }

    private fun establishConnection(url: String) {
        _connectionState.value = ConnectionState.Connecting

        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                reconnectAttempt = 0 // Reset counter on successful connection
                _connectionState.value = ConnectionState.Connected
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                _messages.tryEmit(text)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                handleDisconnection(url)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _connectionState.value = ConnectionState.Error(t)
                handleDisconnection(url)
            }
        })
    }

    private fun handleDisconnection(url: String) {
        if (!shouldReconnect) {
            _connectionState.value = ConnectionState.Disconnected
            return
        }

        if (reconnectAttempt >= MAX_RECONNECT_ATTEMPTS) {
            _connectionState.value = ConnectionState.Disconnected
            return
        }

        reconnectJob = scope.launch {
            val backoffMs = calculateBackoff(reconnectAttempt)
            _connectionState.value = ConnectionState.Reconnecting(backoffMs)

            delay(backoffMs)
            reconnectAttempt++
            establishConnection(url)
        }
    }

    private fun calculateBackoff(attempt: Int): Long {
        val backoff = INITIAL_BACKOFF_MS * BACKOFF_MULTIPLIER.pow(attempt.toDouble())
        val jitter = (0..1000).random() // Jitter to prevent thundering herd
        return (backoff.toLong() + jitter).coerceAtMost(MAX_BACKOFF_MS)
    }

    fun disconnect() {
        shouldReconnect = false
        reconnectJob?.cancel()
        webSocket?.close(1000, "User disconnect")
        webSocket = null
        _connectionState.value = ConnectionState.Disconnected
    }

    sealed class ConnectionState {
        data object Disconnected : ConnectionState()
        data object Connecting : ConnectionState()
        data object Connected : ConnectionState()
        data class Reconnecting(val backoffMs: Long) : ConnectionState()
        data class Error(val throwable: Throwable) : ConnectionState()
    }
}
```

### Heartbeat (Ping/Pong)

```kotlin
class HeartbeatWebSocketManager(
    private val okHttpClient: OkHttpClient,
    private val scope: CoroutineScope
) {
    private var webSocket: WebSocket? = null
    private var heartbeatJob: Job? = null
    private var lastPongTime = AtomicLong(0)

    companion object {
        private const val HEARTBEAT_INTERVAL_MS = 30_000L
        private const val PONG_TIMEOUT_MS = 10_000L
    }

    private fun startHeartbeat() {
        heartbeatJob = scope.launch {
            while (isActive) {
                delay(HEARTBEAT_INTERVAL_MS)

                // Check if we received pong for previous ping
                val timeSinceLastPong = System.currentTimeMillis() - lastPongTime.get()
                if (lastPongTime.get() > 0 && timeSinceLastPong > HEARTBEAT_INTERVAL_MS + PONG_TIMEOUT_MS) {
                    // Connection lost
                    handleConnectionLost()
                    break
                }

                // Send ping (OkHttp handles pong automatically)
                webSocket?.send("ping")
            }
        }
    }

    private fun stopHeartbeat() {
        heartbeatJob?.cancel()
        heartbeatJob = null
    }

    private fun handleConnectionLost() {
        webSocket?.cancel()
        // Initiate reconnection
    }

    fun onPongReceived() {
        lastPongTime.set(System.currentTimeMillis())
    }
}
```

### Integration with ViewModel and Lifecycle

```kotlin
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val webSocketManager: ReconnectingWebSocketManager,
    private val messageRepository: MessageRepository
) : ViewModel() {

    val connectionState = webSocketManager.connectionState
        .stateIn(viewModelScope, SharingStarted.Eagerly, ConnectionState.Disconnected)

    val messages = webSocketManager.messages
        .map { json -> parseMessage(json) }
        .catch { e -> emit(ChatMessage.Error(e.message ?: "Parse error")) }
        .stateIn(viewModelScope, SharingStarted.Eagerly, null)

    init {
        // Auto-connect when ViewModel is created
        connect()

        // Save messages to local DB
        viewModelScope.launch {
            messages.filterNotNull().collect { message ->
                if (message is ChatMessage.Incoming) {
                    messageRepository.saveMessage(message)
                }
            }
        }
    }

    fun connect() {
        webSocketManager.connect("wss://chat.example.com/ws")
    }

    fun sendMessage(text: String) {
        val message = ChatMessage.Outgoing(
            id = UUID.randomUUID().toString(),
            text = text,
            timestamp = System.currentTimeMillis()
        )
        val json = Json.encodeToString(message)
        webSocketManager.send(json)
    }

    override fun onCleared() {
        super.onCleared()
        webSocketManager.disconnect()
    }

    private fun parseMessage(json: String): ChatMessage {
        return Json.decodeFromString<ChatMessage>(json)
    }
}
```

### Ktor WebSocket (Alternative)

```kotlin
class KtorWebSocketManager(
    private val client: HttpClient
) {
    private var session: DefaultClientWebSocketSession? = null

    suspend fun connect(url: String, onMessage: (String) -> Unit) {
        client.webSocket(url) {
            session = this

            // Receive messages
            for (frame in incoming) {
                when (frame) {
                    is Frame.Text -> onMessage(frame.readText())
                    is Frame.Binary -> { /* handle binary */ }
                    is Frame.Close -> break
                    else -> {}
                }
            }
        }
    }

    suspend fun send(message: String) {
        session?.send(Frame.Text(message))
    }

    suspend fun close() {
        session?.close(CloseReason(CloseReason.Codes.NORMAL, "User disconnect"))
    }
}

// Ktor Client setup with WebSocket
val client = HttpClient(OkHttp) {
    install(WebSockets) {
        pingInterval = 30_000
        maxFrameSize = Long.MAX_VALUE
    }
}
```

### Best Practices

1. **Lifecycle-aware** - bind WebSocket to lifecycle (ViewModel, Service)
2. **Reconnect strategy** - exponential backoff with jitter
3. **Heartbeat** - regular ping/pong to detect connection loss
4. **Message buffering** - queue outgoing messages during reconnect
5. **Offline mode** - persist messages locally
6. **Security** - always use WSS (WebSocket Secure)
7. **Serialization** - JSON or Protobuf for structured data

---

## Дополнительные Вопросы (RU)

1. Как обрабатывать очередь исходящих сообщений при переподключении?
2. В чем разница между WebSocket и Server-Sent Events (SSE)?
3. Как реализовать аутентификацию в WebSocket соединении?
4. Как тестировать WebSocket код с MockWebServer?
5. Когда использовать WebSocket вместо polling?

## Follow-ups

1. How do you handle outgoing message queue during reconnection?
2. What are the differences between WebSocket and Server-Sent Events (SSE)?
3. How do you implement authentication in WebSocket connections?
4. How do you test WebSocket code with MockWebServer?
5. When should you use WebSocket instead of polling?

## Ссылки (RU)

- [OkHttp WebSocket](https://square.github.io/okhttp/features/websockets/)
- [Ktor WebSocket](https://ktor.io/docs/client-websockets.html)
- [WebSocket RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)

## References

- [OkHttp WebSocket](https://square.github.io/okhttp/features/websockets/)
- [Ktor WebSocket](https://ktor.io/docs/client-websockets.html)
- [WebSocket RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)

## Связанные Вопросы (RU)

### Предпосылки

- [[q-real-time-updates-android--android--medium]]
- [[q-okhttp-interceptors-advanced--networking--medium]]

### Похожие

- [[q-server-sent-events-sse--android--medium]]
- [[q-polling-implementation--android--medium]]

### Продвинутое

- [[q-grpc-android--networking--hard]]
- [[q-implement-voice-video-call--android--hard]]

## Related Questions

### Prerequisites

- [[q-real-time-updates-android--android--medium]]
- [[q-okhttp-interceptors-advanced--networking--medium]]

### Related

- [[q-server-sent-events-sse--android--medium]]
- [[q-polling-implementation--android--medium]]

### Advanced

- [[q-grpc-android--networking--hard]]
- [[q-implement-voice-video-call--android--hard]]
