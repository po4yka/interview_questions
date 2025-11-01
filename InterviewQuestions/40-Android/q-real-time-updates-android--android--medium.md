---
id: 20251012-12271177
title: "Real Time Updates Android / Обновления в реальном времени Android"
aliases: ["Real Time Updates Android", "Обновления в реальном времени Android"]
topic: android
subtopics: [networking-http, websockets]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-websockets, c-firebase-realtime, c-server-sent-events, q-networking-in-android--android--medium]
created: 2025-10-15
updated: 2025-10-31
sources: []
tags: [android, networking, websockets, sse, firebase, fcm, real-time, difficulty/medium, android/networking-http, android/websockets]
---

# Вопрос (RU)

Как реализовать обновления в реальном времени в Android-приложении? Какие технологии доступны и каковы best practices?

# Question (EN)

How do you implement real-time updates in Android applications? What are the available technologies and best practices?

---

## Ответ (RU)

Real-time обновления обеспечивают мгновенную синхронизацию данных между сервером и клиентом. Основные технологии:

### 1. WebSockets — полнодуплексная связь

```kotlin
class WebSocketManager(
    private val client: OkHttpClient,
    private val url: String
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<Message>()
    val messages = _messages.asSharedFlow()

    private val _state = MutableStateFlow(State.DISCONNECTED)
    val state = _state.asStateFlow()

    private val listener = object : WebSocketListener() {
        override fun onOpen(ws: WebSocket, response: Response) {
            _state.value = State.CONNECTED
        }

        override fun onMessage(ws: WebSocket, text: String) {
            // ✅ Parse and emit message asynchronously
            scope.launch {
                val message = Json.decodeFromString<Message>(text)
                _messages.emit(message)
            }
        }

        override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
            _state.value = State.ERROR
            scheduleReconnect() // ✅ Auto-reconnect with backoff
        }
    }

    fun connect() {
        val request = Request.Builder()
            .url(url)
            .build()
        webSocket = client.newWebSocket(request, listener)
    }

    // ❌ Don't forget to disconnect when app goes to background
    fun disconnect() {
        webSocket?.close(1000, "Client disconnect")
    }
}
```

**Плюсы**: низкая задержка, двусторонний обмен
**Минусы**: расход батареи, управление соединением

### 2. Server-Sent Events (SSE) — односторонние обновления

```kotlin
fun connectSSE(url: String): Flow<ServerEvent> = flow {
    val request = Request.Builder()
        .url(url)
        .addHeader("Accept", "text/event-stream")
        .build()

    val response = client.newCall(request).execute()
    val source = response.body?.source()

    while (!source.exhausted()) {
        val line = source.readUtf8Line()
        if (line.startsWith("data:")) {
            val data = line.substring(5).trim()
            emit(Json.decodeFromString(data))
        }
    }
}
```

**Плюсы**: простота, авто-переподключение
**Минусы**: только от сервера к клиенту

### 3. Firebase Realtime Database

```kotlin
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

    database.getReference("messages/$chatId")
        .addValueEventListener(listener)

    awaitClose {
        database.getReference("messages/$chatId")
            .removeEventListener(listener)
    }
}
```

**Плюсы**: быстрое развертывание, масштабируемость
**Минусы**: vendor lock-in, стоимость

### 4. Firebase Cloud Messaging (FCM) — push-уведомления

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        // ✅ Handle data payload for silent updates
        message.data.let { data ->
            when (data["type"]) {
                "new_message" -> fetchAndStore(data["id"])
                "update" -> syncEntity(data["entity_id"])
            }
        }

        // ✅ Show notification if user is not in app
        if (!isAppInForeground()) {
            showNotification(message.notification)
        }
    }
}
```

**Плюсы**: надежная доставка, кроссплатформенность
**Минусы**: требует Google Services

### 5. Polling / Long Polling — fallback стратегия

```kotlin
fun startPolling(interval: Long, onUpdate: (List<Message>) -> Unit) {
    scope.launch {
        var lastTimestamp = 0L

        while (isActive) {
            // ✅ Request only new messages since last timestamp
            val messages = api.getMessages(since = lastTimestamp)
            if (messages.isNotEmpty()) {
                onUpdate(messages)
                lastTimestamp = messages.maxOf { it.timestamp }
            }
            delay(interval)
        }
    }
}
```

**Плюсы**: простота реализации
**Минусы**: высокая нагрузка на сервер, задержки

### Lifecycle-aware подключение

```kotlin
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val webSocketManager: WebSocketManager,
    networkMonitor: NetworkMonitor
) : ViewModel() {

    init {
        // ✅ Connect/disconnect based on network availability
        viewModelScope.launch {
            networkMonitor.isOnline.collect { online ->
                if (online) webSocketManager.connect()
                else webSocketManager.disconnect()
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        webSocketManager.disconnect() // ✅ Clean up on ViewModel destruction
    }
}
```

### Сравнение технологий

| Технология | Когда использовать | Ключевая особенность |
|------------|-------------------|---------------------|
| WebSockets | Чаты, игры, коллаборация | Двусторонний обмен, низкая задержка |
| SSE | Live-ленты, уведомления | Односторонний, авто-переподключение |
| Firebase Realtime | MVP, быстрый старт | Готовое решение, масштабируемость |
| FCM | Push-уведомления | Надежная доставка |
| Polling | Fallback | Простота |

### Best Practices

**Управление соединением:**
- Авто-переподключение с exponential backoff
- Отключение в фоне для экономии батареи
- Мониторинг сети (ConnectivityManager, NetworkCallback)

**Производительность:**
- Пакетная обработка обновлений
- Локальное кэширование (Room)
- Сжатие сообщений (Gzip)
- Пагинация истории

**Безопасность:**
- Защищенное соединение (wss://, https://)
- Аутентификация через токены
- Валидация входящих данных

**UX:**
- Отображение статуса соединения
- Optimistic updates для мгновенного отклика
- Graceful degradation в offline

## Answer (EN)

Real-time updates enable instant data synchronization between server and client. Main technologies:

### 1. WebSockets — Full-Duplex Communication

```kotlin
class WebSocketManager(
    private val client: OkHttpClient,
    private val url: String
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<Message>()
    val messages = _messages.asSharedFlow()

    private val _state = MutableStateFlow(State.DISCONNECTED)
    val state = _state.asStateFlow()

    private val listener = object : WebSocketListener() {
        override fun onOpen(ws: WebSocket, response: Response) {
            _state.value = State.CONNECTED
        }

        override fun onMessage(ws: WebSocket, text: String) {
            // ✅ Parse and emit message asynchronously
            scope.launch {
                val message = Json.decodeFromString<Message>(text)
                _messages.emit(message)
            }
        }

        override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
            _state.value = State.ERROR
            scheduleReconnect() // ✅ Auto-reconnect with backoff
        }
    }

    fun connect() {
        val request = Request.Builder()
            .url(url)
            .build()
        webSocket = client.newWebSocket(request, listener)
    }

    // ❌ Don't forget to disconnect when app goes to background
    fun disconnect() {
        webSocket?.close(1000, "Client disconnect")
    }
}
```

**Pros**: Low latency, bidirectional
**Cons**: Battery drain, connection management

### 2. Server-Sent Events (SSE) — One-Way Updates

```kotlin
fun connectSSE(url: String): Flow<ServerEvent> = flow {
    val request = Request.Builder()
        .url(url)
        .addHeader("Accept", "text/event-stream")
        .build()

    val response = client.newCall(request).execute()
    val source = response.body?.source()

    while (!source.exhausted()) {
        val line = source.readUtf8Line()
        if (line.startsWith("data:")) {
            val data = line.substring(5).trim()
            emit(Json.decodeFromString(data))
        }
    }
}
```

**Pros**: Simple, auto-reconnect
**Cons**: Server-to-client only

### 3. Firebase Realtime Database

```kotlin
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

    database.getReference("messages/$chatId")
        .addValueEventListener(listener)

    awaitClose {
        database.getReference("messages/$chatId")
            .removeEventListener(listener)
    }
}
```

**Pros**: Fast deployment, scalability
**Cons**: Vendor lock-in, cost

### 4. Firebase Cloud Messaging (FCM) — Push Notifications

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        // ✅ Handle data payload for silent updates
        message.data.let { data ->
            when (data["type"]) {
                "new_message" -> fetchAndStore(data["id"])
                "update" -> syncEntity(data["entity_id"])
            }
        }

        // ✅ Show notification if user is not in app
        if (!isAppInForeground()) {
            showNotification(message.notification)
        }
    }
}
```

**Pros**: Reliable delivery, cross-platform
**Cons**: Requires Google Services

### 5. Polling / Long Polling — Fallback Strategy

```kotlin
fun startPolling(interval: Long, onUpdate: (List<Message>) -> Unit) {
    scope.launch {
        var lastTimestamp = 0L

        while (isActive) {
            // ✅ Request only new messages since last timestamp
            val messages = api.getMessages(since = lastTimestamp)
            if (messages.isNotEmpty()) {
                onUpdate(messages)
                lastTimestamp = messages.maxOf { it.timestamp }
            }
            delay(interval)
        }
    }
}
```

**Pros**: Easy to implement
**Cons**: High server load, delayed updates

### Lifecycle-Aware Connection

```kotlin
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val webSocketManager: WebSocketManager,
    networkMonitor: NetworkMonitor
) : ViewModel() {

    init {
        // ✅ Connect/disconnect based on network availability
        viewModelScope.launch {
            networkMonitor.isOnline.collect { online ->
                if (online) webSocketManager.connect()
                else webSocketManager.disconnect()
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        webSocketManager.disconnect() // ✅ Clean up on ViewModel destruction
    }
}
```

### Technology Comparison

| Technology | Use Case | Key Feature |
|------------|----------|-------------|
| WebSockets | Chat, gaming, collaboration | Bidirectional, low latency |
| SSE | Live feeds, notifications | One-way, auto-reconnect |
| Firebase Realtime | MVP, rapid development | Ready solution, scalable |
| FCM | Push notifications | Reliable delivery |
| Polling | Fallback | Simplicity |

### Best Practices

**Connection Management:**
- Auto-reconnect with exponential backoff
- Disconnect when in background to save battery
- Network monitoring (ConnectivityManager, NetworkCallback)

**Performance:**
- Batch updates
- Local caching (Room)
- Message compression (Gzip)
- Pagination for message history

**Security:**
- Secure connections (wss://, https://)
- Token-based authentication
- Validate incoming data

**UX:**
- Show connection status
- Optimistic updates for instant feedback
- Graceful degradation in offline mode

---

## Follow-ups

- How to handle message ordering and deduplication in real-time systems?
- What are the trade-offs between WebSockets and FCM for chat applications?
- How to implement offline-first architecture with real-time sync?
- What strategies exist for reducing battery consumption in always-connected apps?
- How to handle reconnection storms when many clients reconnect simultaneously?

## References

- [[c-websockets]]
- [[c-firebase-realtime]]
- [[c-server-sent-events]]
- [[c-offline-first-architecture]]

## Related Questions

### Prerequisites
- [[q-networking-in-android--android--medium]]
- [[q-coroutines-and-flow--kotlin--medium]]

### Related
- [[q-workmanager-background-tasks--android--medium]]
- [[q-retrofit-implementation--android--medium]]

### Advanced
- [[q-distributed-systems-consistency--system-design--hard]]
- [[q-websocket-scalability--system-design--hard]]
