---
id: 20251006-000004
title: "HTTP vs Long-Polling vs WebSocket vs SSE / HTTP против Long-Polling против WebSocket против SSE"
aliases: []

# Classification
topic: android
subtopics: [networking-http, websockets, performance-memory]
question_kind: comparison
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/networking, android/real-time, android/protocols, android/performance, difficulty/medium]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [websocket, real-time-updates, networking]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android/networking-http, android/websockets, android/performance-memory, en, ru, difficulty/medium]
---
# Question (EN)
> What are the differences between HTTP, Long-Polling, WebSocket, and Server-Sent Events (SSE)? When should each be used?
# Вопрос (RU)
> В чем разница между HTTP, Long-Polling, WebSocket и Server-Sent Events (SSE)? Когда следует использовать каждый из них?

---

## Answer (EN)

Understanding the differences between these communication protocols is crucial for choosing the right approach for real-time features in Android applications.

### 1. HTTP (Request-Response)

**Description:**
Traditional HTTP follows a request-response model where the client initiates a request and the server responds.

**How it works:**
```kotlin
// OkHttp example
class HttpClient @Inject constructor(
    private val okHttpClient: OkHttpClient
) {
    suspend fun getData(): Response {
        val request = Request.Builder()
            .url("https://api.example.com/data")
            .build()

        return withContext(Dispatchers.IO) {
            okHttpClient.newCall(request).execute()
        }
    }
}

// Retrofit example
interface ApiService {
    @GET("data")
    suspend fun getData(): DataResponse
}
```

**Characteristics:**
- **Unidirectional**: Client → Server → Client
- **Stateless**: Each request is independent
- **Overhead**: HTTP headers sent with every request
- **Latency**: Round-trip time for each request

**Pros:**
 Simple and widely supported
 Cacheable responses
 Works through firewalls and proxies
 Scalable for stateless operations

**Cons:**
 Not suitable for real-time updates
 Client must poll for new data
 High latency for frequent updates
 Inefficient for continuous data flow

**Use Cases:**
- REST APIs
- CRUD operations
- One-time data fetches
- File downloads
- Non-real-time operations

---

### 2. Long-Polling

**Description:**
Long-polling is a technique where the client sends a request and the server keeps it open until new data is available or a timeout occurs.

**How it works:**
```kotlin
class LongPollingClient @Inject constructor(
    private val okHttpClient: OkHttpClient
) {
    private var isPolling = false

    fun startPolling() {
        isPolling = true
        viewModelScope.launch {
            while (isPolling) {
                try {
                    val request = Request.Builder()
                        .url("https://api.example.com/poll")
                        .build()

                    val response = okHttpClient.newCall(request).execute()
                    val data = response.body?.string()

                    // Process data
                    handleData(data)

                    // Immediately start next poll
                } catch (e: Exception) {
                    // Handle error, add delay before retry
                    delay(5000)
                }
            }
        }
    }

    fun stopPolling() {
        isPolling = false
    }
}
```

**Characteristics:**
- **Near real-time**: Server pushes data when available
- **Connection held open**: Until data arrives or timeout
- **New connection**: After each response
- **Fallback**: Works where WebSocket might be blocked

**Pros:**
 Near real-time updates
 Works through most firewalls
 Compatible with HTTP/1.1
 Simple server implementation

**Cons:**
 High resource usage on server
 Latency between polls
 Overhead of HTTP headers
 Not truly bidirectional

**Use Cases:**
- Chat applications (fallback)
- Notification systems
- Live updates when WebSocket unavailable
- Legacy system integration

---

### 3. WebSocket

**Description:**
WebSocket provides full-duplex, bidirectional communication over a single TCP connection.

**How it works:**
```kotlin
class WebSocketClient @Inject constructor(
    private val okHttpClient: OkHttpClient
) {
    private var webSocket: WebSocket? = null
    private val messageFlow = MutableSharedFlow<String>()

    fun connect(url: String) {
        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d("WebSocket", "Connected")
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                // Receive message from server
                viewModelScope.launch {
                    messageFlow.emit(text)
                }
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                // Handle binary message
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
            }

            override fun onFailure(
                webSocket: WebSocket,
                t: Throwable,
                response: Response?
            ) {
                Log.e("WebSocket", "Error: ${t.message}")
                // Implement reconnection logic
                scheduleReconnect()
            }
        })
    }

    fun sendMessage(message: String) {
        webSocket?.send(message)
    }

    fun disconnect() {
        webSocket?.close(1000, "Client closing")
    }

    fun observeMessages(): Flow<String> = messageFlow.asSharedFlow()
}
```

**Characteristics:**
- **Full-duplex**: Bidirectional communication
- **Persistent connection**: Single TCP connection
- **Low overhead**: No HTTP headers after handshake
- **Real-time**: Instant message delivery

**Pros:**
 True real-time, bidirectional
 Low latency
 Minimal overhead after handshake
 Efficient for high-frequency updates
 Binary and text support

**Cons:**
 More complex to implement
 May be blocked by proxies/firewalls
 Requires connection management
 State management complexity
 Doesn't work with HTTP caching

**Use Cases:**
- Real-time chat applications
- Live sports scores
- Multiplayer games
- Trading platforms
- Collaborative editing
- Live location tracking

**Advanced WebSocket with Reconnection:**
```kotlin
class RobustWebSocketManager @Inject constructor(
    private val okHttpClient: OkHttpClient,
    private val networkMonitor: NetworkMonitor
) {
    private var reconnectAttempts = 0
    private val maxReconnectAttempts = 5
    private val baseDelay = 1000L

    fun connect() {
        // Check network first
        if (!networkMonitor.isConnected()) {
            observeNetworkAndReconnect()
            return
        }

        val request = Request.Builder()
            .url("wss://api.example.com/ws")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                reconnectAttempts = 0 // Reset on successful connection
            }

            override fun onFailure(
                webSocket: WebSocket,
                t: Throwable,
                response: Response?
            ) {
                scheduleReconnect()
            }
        })
    }

    private fun scheduleReconnect() {
        if (reconnectAttempts >= maxReconnectAttempts) {
            // Give up and notify user
            return
        }

        // Exponential backoff
        val delay = baseDelay * (1 shl reconnectAttempts)
        reconnectAttempts++

        viewModelScope.launch {
            delay(delay)
            connect()
        }
    }
}
```

---

### 4. Server-Sent Events (SSE)

**Description:**
SSE allows servers to push data to clients over HTTP, but only in one direction (server → client).

**How it works:**
```kotlin
class SSEClient @Inject constructor(
    private val okHttpClient: OkHttpClient
) {
    private val eventFlow = MutableSharedFlow<ServerEvent>()

    fun connect(url: String) {
        val request = Request.Builder()
            .url(url)
            .header("Accept", "text/event-stream")
            .build()

        viewModelScope.launch(Dispatchers.IO) {
            try {
                val response = okHttpClient.newCall(request).execute()
                val source = response.body?.source()

                source?.let {
                    while (!it.exhausted()) {
                        val line = it.readUtf8Line() ?: continue

                        when {
                            line.startsWith("data: ") -> {
                                val data = line.substring(6)
                                val event = parseEvent(data)
                                eventFlow.emit(event)
                            }
                            line.startsWith("event: ") -> {
                                // Handle named events
                            }
                            line.startsWith("id: ") -> {
                                // Track event ID for reconnection
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("SSE", "Connection error", e)
                scheduleReconnect()
            }
        }
    }

    fun observeEvents(): Flow<ServerEvent> = eventFlow.asSharedFlow()
}

// Better implementation using OkHttp EventSource
class SSEManager @Inject constructor() {
    private val eventSourceFactory = EventSources.createFactory(okHttpClient)

    fun connect(url: String): Flow<ServerEvent> = callbackFlow {
        val request = Request.Builder()
            .url(url)
            .build()

        val eventSource = eventSourceFactory.newEventSource(
            request,
            object : EventSourceListener() {
                override fun onOpen(eventSource: EventSource, response: Response) {
                    // Connection opened
                }

                override fun onEvent(
                    eventSource: EventSource,
                    id: String?,
                    type: String?,
                    data: String
                ) {
                    trySend(ServerEvent(id, type, data))
                }

                override fun onFailure(
                    eventSource: EventSource,
                    t: Throwable?,
                    response: Response?
                ) {
                    close(t)
                }
            }
        )

        awaitClose { eventSource.cancel() }
    }
}
```

**Characteristics:**
- **Unidirectional**: Server → Client only
- **Persistent connection**: HTTP/1.1 or HTTP/2
- **Auto-reconnection**: Built-in reconnection
- **Event IDs**: Track last received event

**Pros:**
 Simple to implement
 Automatic reconnection
 Event IDs for reliability
 Works through HTTP proxies
 Text-based format
 Built-in browser support

**Cons:**
 Unidirectional (server to client only)
 Text data only (no binary)
 Limited browser connections (6 per domain)
 Less efficient than WebSocket for bidirectional

**Use Cases:**
- Live news feeds
- Stock price updates
- Social media notifications
- Server monitoring dashboards
- Live sports scores
- Weather updates

---

### Comparison Table

| Feature | HTTP | Long-Polling | WebSocket | SSE |
|---------|------|--------------|-----------|-----|
| **Direction** | Request-Response | Request-Response | Full-duplex | Server→Client |
| **Connection** | New per request | Held until data | Persistent | Persistent |
| **Overhead** | High | Medium | Low | Medium |
| **Latency** | High | Medium | Low | Low |
| **Real-time** | No | Near real-time | Yes | Yes |
| **Binary Data** | Yes | Yes | Yes | No |
| **Complexity** | Low | Medium | High | Low |
| **Firewall** |  |  | Sometimes |  |
| **Scalability** | High | Low | Medium | Medium |

### Performance Comparison

```kotlin
// Example: 1000 messages

// HTTP Polling (every 1s)
// - 1000 requests
// - ~1000ms average latency
// - ~500KB overhead (headers)

// Long-Polling
// - ~100-500 requests (depends on data frequency)
// - ~500ms average latency
// - ~50-250KB overhead

// WebSocket
// - 1 connection
// - <50ms average latency
// - ~2KB overhead (after handshake)

// SSE
// - 1 connection
// - <100ms average latency
// - ~10KB overhead
```

### Decision Matrix

**Use HTTP when:**
- Simple CRUD operations
- Infrequent updates
- Data can be cached
- Stateless operations
- RESTful APIs

**Use Long-Polling when:**
- Real-time needed but WebSocket blocked
- Infrequent server updates
- Legacy system constraints
- Fallback mechanism

**Use WebSocket when:**
- True real-time bidirectional communication
- High-frequency updates
- Chat, gaming, or collaborative apps
- Low latency critical
- Binary data transmission

**Use SSE when:**
- Server-to-client updates only
- Text-based notifications
- Stock tickers, news feeds
- Simpler than WebSocket
- Automatic reconnection needed

### Best Practices

**For WebSocket:**
1. Implement exponential backoff for reconnection
2. Handle network state changes
3. Use heartbeat/ping-pong to detect dead connections
4. Implement proper error handling
5. Use binary format (Protocol Buffers) for efficiency

**For SSE:**
1. Track event IDs for resuming after disconnect
2. Handle automatic reconnection
3. Implement timeout for hung connections
4. Use with HTTP/2 for better performance

**For Long-Polling:**
1. Implement timeout on server
2. Handle connection failures gracefully
3. Add jitter to prevent thundering herd
4. Consider as fallback to WebSocket

### Common Pitfalls

1. Using HTTP polling when WebSocket/SSE would be better
2. Not implementing reconnection logic for WebSocket
3. Ignoring battery impact of persistent connections
4. Not handling network state changes
5. Missing error handling and timeouts
6. Not considering firewall/proxy restrictions

## Ответ (RU)

Понимание различий между этими протоколами связи критически важно для выбора правильного подхода для real-time функций в Android приложениях.

### 1. HTTP (Запрос-Ответ)

**Описание:**
Традиционный HTTP следует модели запрос-ответ, где клиент инициирует запрос, а сервер отвечает.

**Характеристики:**
- **Однонаправленный**: Клиент → Сервер → Клиент
- **Без сохранения состояния**: Каждый запрос независим
- **Накладные расходы**: HTTP заголовки с каждым запросом
- **Задержка**: Время round-trip для каждого запроса

**Когда использовать:** REST API, CRUD операции, загрузка файлов, нереал-тайм операции.

### 2. Long-Polling

**Описание:**
Long-polling - это техника, где клиент отправляет запрос, а сервер держит его открытым до появления новых данных или таймаута.

**Характеристики:**
- **Почти в реальном времени**: Сервер отправляет данные при доступности
- **Удержание соединения**: До получения данных или таймаута
- **Новое соединение**: После каждого ответа

**Когда использовать:** Чат-приложения (fallback), системы уведомлений, когда WebSocket недоступен.

### 3. WebSocket

**Описание:**
WebSocket обеспечивает полнодуплексную двунаправленную связь через одно TCP соединение.

**Характеристики:**
- **Полный дуплекс**: Двунаправленная связь
- **Постоянное соединение**: Одно TCP соединение
- **Низкие накладные расходы**: Нет HTTP заголовков после рукопожатия
- **Реальное время**: Мгновенная доставка сообщений

**Преимущества:**
 Настоящий real-time, двунаправленный
 Низкая задержка
 Минимальные накладные расходы после рукопожатия
 Эффективен для частых обновлений
 Поддержка бинарных и текстовых данных

**Недостатки:**
 Более сложная реализация
 Может блокироваться прокси/файрволами
 Требует управления соединением
 Сложность управления состоянием

**Когда использовать:** Реал-тайм чаты, живые спортивные счета, многопользовательские игры, торговые платформы, совместное редактирование, отслеживание местоположения.

### 4. Server-Sent Events (SSE)

**Описание:**
SSE позволяет серверам отправлять данные клиентам через HTTP, но только в одном направлении (сервер → клиент).

**Характеристики:**
- **Однонаправленный**: Сервер → Клиент
- **Постоянное соединение**: HTTP/1.1 или HTTP/2
- **Автопереподключение**: Встроенное переподключение
- **Event ID**: Отслеживание последнего полученного события

**Преимущества:**
 Простая реализация
 Автоматическое переподключение
 Event ID для надежности
 Работает через HTTP прокси
 Текстовый формат

**Недостатки:**
 Однонаправленный (только сервер → клиент)
 Только текстовые данные (нет бинарных)
 Менее эффективен чем WebSocket для двунаправленной связи

**Когда использовать:** Живые новостные ленты, обновления цен акций, уведомления социальных сетей, панели мониторинга сервера.

### Таблица сравнения

| Характеристика | HTTP | Long-Polling | WebSocket | SSE |
|----------------|------|--------------|-----------|-----|
| **Направление** | Запрос-Ответ | Запрос-Ответ | Полный дуплекс | Сервер→Клиент |
| **Соединение** | Новое на запрос | Удерживается | Постоянное | Постоянное |
| **Накладные расходы** | Высокие | Средние | Низкие | Средние |
| **Задержка** | Высокая | Средняя | Низкая | Низкая |
| **Real-time** | Нет | Почти | Да | Да |
| **Бинарные данные** | Да | Да | Да | Нет |
| **Сложность** | Низкая | Средняя | Высокая | Низкая |

### Матрица решений

**Используйте HTTP когда:**
- Простые CRUD операции
- Нечастые обновления
- Данные могут кэшироваться
- Операции без состояния

**Используйте Long-Polling когда:**
- Нужен real-time, но WebSocket заблокирован
- Нечастые обновления с сервера
- Ограничения legacy системы

**Используйте WebSocket когда:**
- Настоящая двунаправленная связь в реальном времени
- Частые обновления
- Чаты, игры, совместные приложения
- Критична низкая задержка

**Используйте SSE когда:**
- Только обновления сервер → клиент
- Текстовые уведомления
- Тикеры акций, новостные ленты
- Нужна простота
- Требуется автоматическое переподключение

### Лучшие практики

**Для WebSocket:**
1. Реализовать экспоненциальную задержку для переподключения
2. Обрабатывать изменения состояния сети
3. Использовать heartbeat/ping-pong для обнаружения мертвых соединений
4. Правильная обработка ошибок

**Для SSE:**
1. Отслеживать event ID для возобновления после отключения
2. Обрабатывать автоматическое переподключение
3. Реализовать timeout для зависших соединений

### Частые ошибки

1. Использование HTTP polling когда лучше WebSocket/SSE
2. Отсутствие логики переподключения для WebSocket
3. Игнорирование влияния на батарею постоянных соединений
4. Необработка изменений состояния сети
5. Отсутствие обработки ошибок и таймаутов

---

## References
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [Server-Sent Events W3C](https://www.w3.org/TR/eventsource/)
- [OkHttp WebSocket](https://square.github.io/okhttp/features/websockets/)
- [HTTP Long Polling](https://javascript.info/long-polling)

## Related Questions

### Related (Medium)
- [[q-reduce-apk-size-techniques--android--medium]] - Build Optimization
- [[q-macrobenchmark-startup--android--medium]] - Performance
- [[q-recomposition-compose--android--medium]] - Jetpack Compose
- [[q-kapt-ksp-migration--android--medium]] - Kapt

### Advanced (Harder)
- [[q-implement-voice-video-call--android--hard]] - Webrtc
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
