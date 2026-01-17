---\
id: android-328
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
related: [c-flow, q-websocket-implementation--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/networking-http, android/websockets, difficulty/medium, fcm, firebase, networking, real-time, sse, websockets]
anki_cards:
  - slug: android-328-0-en
    front: "What are the main technologies for real-time updates in Android?"
    back: |
      **1. WebSockets** - full-duplex bidirectional
      - OkHttp WebSocket API
      - Best for: chat, collaborative editing

      **2. Server-Sent Events (SSE)** - server->client only
      - Simple HTTP, auto-reconnect
      - Best for: live feeds, notifications

      **3. Firebase Realtime Database / Firestore**
      - Real-time listeners, offline support
      - Best for: sync across devices

      **4. FCM** - push notifications
      - Best for: low-frequency alerts

      **Best practice:** lifecycle-aware scope, reconnection strategy, battery optimization.
    tags:
      - android_general
      - difficulty::medium
  - slug: android-328-0-ru
    front: "Какие основные технологии для real-time обновлений в Android?"
    back: |
      **1. WebSockets** - полнодуплексная двунаправленная связь
      - OkHttp WebSocket API
      - Лучше для: чат, совместное редактирование

      **2. Server-Sent Events (SSE)** - только сервер->клиент
      - Простой HTTP, автопереподключение
      - Лучше для: live feeds, уведомления

      **3. Firebase Realtime Database / Firestore**
      - Real-time listeners, offline поддержка
      - Лучше для: синхронизация между устройствами

      **4. FCM** - push уведомления
      - Лучше для: редкие alerts

      **Best practice:** lifecycle-aware scope, стратегия reconnect, оптимизация батареи.
    tags:
      - android_general
      - difficulty::medium

---\
# Вопрос (RU)

> Как реализовать обновления в реальном времени в Android-приложении? Какие технологии доступны и каковы best practices?

# Question (EN)

> How do you implement real-time updates in Android applications? What are the available technologies and best practices?

---

## Ответ (RU)

Real-time обновления обеспечивают более быструю и частую синхронизацию данных между сервером и клиентом, стремящуюся к минимальной задержке. Основные технологии:

### 1. WebSockets — Полнодуплексная Связь

```kotlin
class WebSocketManager(
    private val client: OkHttpClient,
    private val url: String,
    private val scope: CoroutineScope // lifecycle-aware scope, e.g. viewModelScope
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
            scheduleReconnect() // ✅ Auto-reconnect with backoff (реализовать отдельно)
        }
    }

    fun connect() {
        if (_state.value == State.CONNECTED) return

        val request = Request.Builder()
            .url(url)
            .build()
        webSocket = client.newWebSocket(request, listener)
    }

    fun disconnect() {
        // ✅ Закрывать соединение по завершении жизненного цикла владельца (например, ViewModel)
        webSocket?.close(1000, "Client disconnect")
        webSocket = null
        _state.value = State.DISCONNECTED
    }

    private fun scheduleReconnect() {
        // ✅ Заглушка: реализовать backoff-стратегию в реальном коде
    }
}
```

**Плюсы**: низкая задержка, двусторонний обмен

**Минусы**: расход батареи, необходимость правильного управления соединением и повторными подключениями

### 2. Server-Sent Events (SSE) — Односторонние Обновления

```kotlin
fun connectSSE(
    client: OkHttpClient,
    url: String
): Flow<ServerEvent> = flow {
    val request = Request.Builder()
        .url(url)
        .addHeader("Accept", "text/event-stream")
        .build()

    withContext(Dispatchers.IO) {
        client.newCall(request).execute().use { response ->
            val source = response.body?.source() ?: return@use

            while (currentCoroutineContext().isActive && !source.exhausted()) {
                val line = source.readUtf8Line() ?: continue
                if (line.startsWith("data:")) {
                    val data = line.substring(5).trim()
                    emit(Json.decodeFromString<ServerEvent>(data))
                }
            }
        }
    }
}
```

**Плюсы**: простота, эффективна для потока однонаправленных событий

**Минусы**: только от сервера к клиенту, авто-переподключение и обработку `Last-Event-ID` нужно реализовывать явно на клиенте

### 3. Firebase Realtime Database

```kotlin
fun getMessagesFlow(chatId: String): Flow<List<Message>> = callbackFlow {
    val ref = database.getReference("messages/$chatId")

    val listener = object : ValueEventListener {
        override fun onDataChange(snapshot: DataSnapshot) {
            val messages = snapshot.children.mapNotNull {
                it.getValue(Message::class.java)
            }
            trySend(messages).isSuccess
        }

        override fun onCancelled(error: DatabaseError) {
            close(error.toException())
        }
    }

    ref.addValueEventListener(listener)

    awaitClose {
        ref.removeEventListener(listener)
    }
}
```

**Плюсы**: быстрое развертывание, масштабируемость

**Минусы**: vendor lock-in, стоимость, необходимость аккуратного проектирования структуры данных и правил безопасности

### 4. Firebase Cloud Messaging (FCM) — Push-уведомления

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        // ✅ Обработка data payload для "тихих" обновлений
        message.data.let { data ->
            when (data["type"]) {
                "new_message" -> fetchAndStore(data["id"])
                "update" -> syncEntity(data["entity_id"])
            }
        }

        // ✅ Показать уведомление, если пользователь не в приложении
        if (!isAppInForeground()) {
            val notification = message.notification
            if (notification != null) {
                showNotification(notification) // реализовать создание NotificationCompat
            }
        }
    }
}
```

**Плюсы**: надежная доставка push-сообщений, кроссплатформенность; подходит как триггер для синхронизации данных, но не гарантирует жёстко детерминированную задержку доставки для всех сценариев "real-time".

**Минусы**: требует Google Play Services / FCM-инфраструктуру, ограничения частоты/объёма

### 5. Polling / Long Polling — Fallback Стратегии

```kotlin
fun startPolling(
    scope: CoroutineScope,
    interval: Long,
    onUpdate: (List<Message>) -> Unit
) {
    scope.launch {
        var lastTimestamp = 0L

        while (isActive) {
            // ✅ Запрашивать только новые сообщения с момента последнего известного timestamp
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

**Плюсы**: простота реализации, работает везде

**Минусы**: высокая нагрузка на сервер, лишний трафик и задержки, особенно при коротких интервалах; "long polling" обычно подразумевает удержание соединения сервером до появления данных, а не только частый периодический запрос

### Lifecycle-aware Подключение

```kotlin
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val webSocketManager: WebSocketManager,
    networkMonitor: NetworkMonitor
) : ViewModel() {

    init {
        // ✅ Подключаться только при наличии сети
        viewModelScope.launch {
            networkMonitor.isOnline.collect { online ->
                if (online) webSocketManager.connect()
                else webSocketManager.disconnect()
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        webSocketManager.disconnect() // ✅ Очистка при уничтожении ViewModel
    }
}
```

Для production-кода также важно учитывать жизненный цикл UI (например, отключать WebSocket, когда экран не активен, если постоянное соединение не требуется) и использовать жизненно устойчивые скоупы (`ViewModel` / foreground service) для длительных соединений.

### Сравнение Технологий

| Технология | Когда использовать | Ключевая особенность |
|------------|-------------------|---------------------|
| WebSockets | Чаты, игры, коллаборация | Двусторонний обмен, низкая задержка |
| SSE | Live-ленты, уведомления | Односторонний поток событий |
| Firebase Realtime | MVP, быстрый старт | Готовое решение, масштабируемость |
| FCM | Push-уведомления | Надежная доставка push-сообщений, триггер синхронизации |
| Polling | Fallback | Простота, ценой эффективности |

### Best Practices

**Управление соединением:**
- Авто-переподключение с exponential backoff
- Привязка к жизненному циклу (`ViewModel`/экран/сервис), отключение, когда соединение не нужно
- Мониторинг сети (ConnectivityManager, NetworkCallback)

**Производительность:**
- Пакетная обработка обновлений
- Локальное кэширование (`Room`)
- Сжатие сообщений (Gzip), если уместно на уровне протокола
- Пагинация истории

**Безопасность:**
- Защищенное соединение (wss://, https://)
- Аутентификация через токены
- Валидация и санитизация входящих данных

**UX:**
- Отображение статуса соединения
- Optimistic updates для мгновенного отклика
- Graceful degradation и offline-режим

## Answer (EN)

Real-time updates enable more frequent and low-latency data synchronization between server and client. Main technologies:

### 1. WebSockets — Full-Duplex Communication

```kotlin
class WebSocketManager(
    private val client: OkHttpClient,
    private val url: String,
    private val scope: CoroutineScope // lifecycle-aware scope, e.g. viewModelScope
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
            scheduleReconnect() // ✅ Implement auto-reconnect with backoff separately
        }
    }

    fun connect() {
        if (_state.value == State.CONNECTED) return

        val request = Request.Builder()
            .url(url)
            .build()
        webSocket = client.newWebSocket(request, listener)
    }

    fun disconnect() {
        // ✅ Close when the owning lifecycle (e.g., ViewModel/screen) ends
        webSocket?.close(1000, "Client disconnect")
        webSocket = null
        _state.value = State.DISCONNECTED
    }

    private fun scheduleReconnect() {
        // ✅ Stub: implement backoff strategy in real code
    }
}
```

**Pros**: Low latency, bidirectional communication

**Cons**: Battery impact, requires careful connection/reconnect management

### 2. Server-Sent Events (SSE) — One-Way Updates

```kotlin
fun connectSSE(
    client: OkHttpClient,
    url: String
): Flow<ServerEvent> = flow {
    val request = Request.Builder()
        .url(url)
        .addHeader("Accept", "text/event-stream")
        .build()

    withContext(Dispatchers.IO) {
        client.newCall(request).execute().use { response ->
            val source = response.body?.source() ?: return@use

            while (currentCoroutineContext().isActive && !source.exhausted()) {
                val line = source.readUtf8Line() ?: continue
                if (line.startsWith("data:")) {
                    val data = line.substring(5).trim()
                    emit(Json.decodeFromString<ServerEvent>(data))
                }
            }
        }
    }
}
```

**Pros**: Simple, efficient for one-way event streams

**Cons**: Server-to-client only; client-side reconnection and `Last-Event-ID` handling must be implemented explicitly

### 3. Firebase Realtime Database

```kotlin
fun getMessagesFlow(chatId: String): Flow<List<Message>> = callbackFlow {
    val ref = database.getReference("messages/$chatId")

    val listener = object : ValueEventListener {
        override fun onDataChange(snapshot: DataSnapshot) {
            val messages = snapshot.children.mapNotNull {
                it.getValue(Message::class.java)
            }
            trySend(messages).isSuccess
        }

        override fun onCancelled(error: DatabaseError) {
            close(error.toException())
        }
    }

    ref.addValueEventListener(listener)

    awaitClose {
        ref.removeEventListener(listener)
    }
}
```

**Pros**: Fast setup, scalable

**Cons**: Vendor lock-in, cost, requires careful data modeling and security rules

### 4. Firebase Cloud Messaging (FCM) — Push Notifications

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        // ✅ Handle data payload for silent/background updates
        message.data.let { data ->
            when (data["type"]) {
                "new_message" -> fetchAndStore(data["id"])
                "update" -> syncEntity(data["entity_id"])
            }
        }

        // ✅ Show notification if user is not in app
        if (!isAppInForeground()) {
            val notification = message.notification
            if (notification != null) {
                showNotification(notification) // implement NotificationCompat building
            }
        }
    }
}
```

**Pros**: Reliable push delivery, cross-platform; good trigger for sync but not a strict hard real-time transport.

**Cons**: Requires Google Play Services / FCM backend and has rate/size limits

### 5. Polling / Long Polling — Fallback Strategies

```kotlin
fun startPolling(
    scope: CoroutineScope,
    interval: Long,
    onUpdate: (List<Message>) -> Unit
) {
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

**Pros**: Easy to implement, universally supported

**Cons**: Higher server load, extra traffic, potential delays (especially with small intervals); "long polling" usually implies the server holds the request open until data is available

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

For production code, also tie the connection to UI/lifecycle needs (e.g., disconnect when the screen is not visible if a permanent connection is unnecessary) and use lifecycle-resilient scopes (`ViewModel` / foreground service) for long-lived connections.

### Technology Comparison

| Technology | Use Case | Key Feature |
|------------|----------|-------------|
| WebSockets | Chat, gaming, collaboration | Bidirectional, low latency |
| SSE | Live feeds, notifications | One-way event stream |
| Firebase Realtime | MVP, rapid development | Managed, scalable solution |
| FCM | Push notifications | Reliable push trigger for sync |
| Polling | Fallback | Simplicity at the cost of efficiency |

### Best Practices

**Connection Management:**
- Auto-reconnect with exponential backoff
- Bind to lifecycle (`ViewModel`/screen/service), disconnect when not needed
- Network monitoring (ConnectivityManager, NetworkCallback)

**Performance:**
- Batch updates
- Local caching (`Room`)
- `Message` compression (Gzip) when appropriate at protocol level
- Pagination for history

**Security:**
- Secure connections (wss://, https://)
- Token-based authentication
- Validate and sanitize incoming data

**UX:**
- Show connection status
- Optimistic updates for instant feedback
- Graceful degradation and offline mode

---

## Follow-ups

- How to handle message ordering and deduplication in real-time systems?
- What are the trade-offs between WebSockets and FCM for chat applications?
- How to implement offline-first architecture with real-time sync?
- What strategies exist for reducing battery consumption in always-connected apps?
- How to handle reconnection storms when many clients reconnect simultaneously?

## References

- [[c-flow]]

## Related Questions

### Prerequisites
- [[q-websocket-implementation--android--medium]]

### Related
- [[q-websocket-implementation--android--medium]]

### Advanced
- [[q-websocket-implementation--android--medium]]
