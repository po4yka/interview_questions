---
id: 20251006-000004
title: "HTTP vs Long-Polling vs WebSocket vs SSE / HTTP против Long-Polling против WebSocket против SSE"
aliases: [HTTP Protocols Comparison, WebSocket vs HTTP, Протоколы HTTP, WebSocket против HTTP]

# Classification
topic: android
subtopics: [networking-http, websockets, performance-memory]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: [https://github.com/amitshekhariitbhu/android-interview-questions]

# Workflow & relations
status: draft
moc: moc-android
related: [q-retrofit-library--android--medium, q-websocket-implementation--networking--medium, q-server-sent-events-sse--networking--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-28

tags: [android/networking-http, android/websockets, android/performance-memory, difficulty/medium]
date created: Tuesday, October 28th 2025, 9:12:30 pm
date modified: Thursday, October 30th 2025, 3:10:22 pm
---

# Вопрос (RU)
> В чем разница между HTTP, Long-Polling, WebSocket и Server-Sent Events (SSE)? Когда следует использовать каждый из них?

# Question (EN)
> What are the differences between HTTP, Long-Polling, WebSocket, and Server-Sent Events (SSE)? When should each be used?

---

## Ответ (RU)

### Краткое Сравнение Протоколов

| Протокол | Направление | Соединение | Задержка | Real-time | Use Case |
|----------|-------------|------------|----------|-----------|----------|
| HTTP | Запрос→Ответ | Новое | Высокая | Нет | REST API, CRUD |
| Long-Polling | Запрос→Ответ | Удержание | Средняя | Почти | Уведомления (fallback) |
| WebSocket | Двунаправленный | Постоянное | Низкая | Да | Чаты, игры |
| SSE | Сервер→Клиент | Постоянное | Низкая | Да | Новости, тикеры |

### 1. HTTP (Запрос-Ответ)

**Модель**: Клиент инициирует запрос → Сервер отвечает → Соединение закрывается

**Характеристики:**
- Без сохранения состояния (stateless)
- HTTP заголовки с каждым запросом
- Высокая задержка для частых обновлений
- Поддержка кэширования

**Когда использовать:**
- ✅ REST API и CRUD операции
- ✅ Загрузка файлов, изображений
- ✅ Нечастые обновления данных
- ❌ Не подходит для real-time обновлений

```kotlin
// Простой HTTP запрос с Retrofit
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

class UserRepository(private val api: ApiService) {
    suspend fun loadUser(id: String) = api.getUser(id)
}
```

### 2. Long-Polling

**Модель**: Клиент → Запрос открыт до появления данных → Ответ → Новый запрос

**Характеристики:**
- Сервер держит соединение открытым до данных или timeout
- После ответа сразу новый запрос
- Работает через большинство firewalls
- Накладные расходы HTTP заголовков

**Когда использовать:**
- ✅ WebSocket заблокирован firewall/proxy
- ✅ Fallback для real-time функций
- ✅ Нечастые обновления с сервера
- ❌ Высокая нагрузка на сервер при масштабировании

```kotlin
class LongPollingClient(private val client: OkHttpClient) {
    private var isActive = false

    fun startPolling(scope: CoroutineScope) {
        isActive = true
        scope.launch {
            while (isActive) {
                try {
                    val request = Request.Builder()
                        .url("https://api.example.com/poll")
                        .build()

                    val response = client.newCall(request).execute()
                    processData(response.body?.string())
                } catch (e: Exception) {
                    delay(5000) // Задержка при ошибке
                }
            }
        }
    }

    fun stop() { isActive = false }
}
```

### 3. WebSocket

**Модель**: Handshake → Постоянное двунаправленное соединение → Обмен сообщениями

**Характеристики:**
- Полнодуплексная связь через одно TCP соединение
- Минимальные накладные расходы после handshake
- Мгновенная доставка сообщений (<50ms)
- Поддержка бинарных данных

**Когда использовать:**
- ✅ Реал-тайм чаты, мессенджеры
- ✅ Многопользовательские игры
- ✅ Совместное редактирование документов
- ✅ Торговые платформы (биржа)
- ❌ Может блокироваться некоторыми proxy/firewall

```kotlin
class WebSocketManager(private val client: OkHttpClient) {
    private var socket: WebSocket? = null
    private val messages = MutableSharedFlow<String>()

    fun connect(url: String) {
        val request = Request.Builder().url(url).build()

        socket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, response: Response) {
                Log.d("WS", "Connected")
            }

            override fun onMessage(ws: WebSocket, text: String) {
                scope.launch { messages.emit(text) }
            }

            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                scheduleReconnect() // Экспоненциальная задержка
            }
        })
    }

    fun send(message: String) = socket?.send(message)
    fun disconnect() = socket?.close(1000, null)
}
```

### 4. Server-Sent Events (SSE)

**Модель**: Клиент подписывается → Сервер отправляет события → Автопереподключение

**Характеристики:**
- Однонаправленный (только сервер → клиент)
- Автоматическое переподключение
- Event ID для отслеживания последнего события
- Только текстовые данные

**Когда использовать:**
- ✅ Новостные ленты, уведомления
- ✅ Тикеры акций, курсы валют
- ✅ Мониторинг сервера, логи
- ❌ Если нужна двунаправленная связь (используйте WebSocket)

```kotlin
class SSEClient(private val client: OkHttpClient) {
    fun connect(url: String): Flow<String> = callbackFlow {
        val request = Request.Builder()
            .url(url)
            .header("Accept", "text/event-stream")
            .build()

        launch(Dispatchers.IO) {
            val response = client.newCall(request).execute()
            response.body?.source()?.use { source ->
                while (!source.exhausted()) {
                    val line = source.readUtf8Line() ?: continue
                    if (line.startsWith("data: ")) {
                        trySend(line.substring(6))
                    }
                }
            }
        }

        awaitClose { /* cleanup */ }
    }
}
```

### Матрица Решений

**HTTP**: Простые CRUD, RESTful API, кэшируемые данные
**Long-Polling**: Fallback для WebSocket, legacy системы
**WebSocket**: Двунаправленный real-time, низкая задержка критична
**SSE**: Только сервер→клиент, текстовые уведомления, простота

### Лучшие Практики

**WebSocket:**
1. Экспоненциальная задержка при переподключении
2. Heartbeat/ping-pong для обнаружения мертвых соединений
3. Обработка изменений состояния сети
4. Protocol Buffers для бинарных данных

**SSE:**
1. Отслеживание event ID для resumption
2. Timeout для зависших соединений
3. HTTP/2 для лучшей производительности

**Long-Polling:**
1. Timeout на стороне сервера
2. Jitter для предотвращения thundering herd
3. Graceful обработка ошибок

## Answer (EN)

### Protocol Comparison Quick Reference

| Protocol | Direction | Connection | Latency | Real-time | Use Case |
|----------|-----------|------------|---------|-----------|----------|
| HTTP | Request→Response | New | High | No | REST API, CRUD |
| Long-Polling | Request→Response | Held | Medium | Near | Notifications (fallback) |
| WebSocket | Bidirectional | Persistent | Low | Yes | Chat, games |
| SSE | Server→Client | Persistent | Low | Yes | News, tickers |

### 1. HTTP (Request-Response)

**Model**: Client initiates request → Server responds → Connection closes

**Characteristics:**
- Stateless - each request independent
- HTTP headers with every request
- High latency for frequent updates
- Cacheable responses

**When to use:**
- ✅ REST APIs and CRUD operations
- ✅ File/image downloads
- ✅ Infrequent data updates
- ❌ Not suitable for real-time updates

```kotlin
// Simple HTTP request with Retrofit
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

class UserRepository(private val api: ApiService) {
    suspend fun loadUser(id: String) = api.getUser(id)
}
```

### 2. Long-Polling

**Model**: Client → Request held until data available → Response → New request

**Characteristics:**
- Server keeps connection open until data or timeout
- Immediately starts new request after response
- Works through most firewalls
- HTTP header overhead on each connection

**When to use:**
- ✅ WebSocket blocked by firewall/proxy
- ✅ Fallback for real-time features
- ✅ Infrequent server updates
- ❌ High server load at scale

```kotlin
class LongPollingClient(private val client: OkHttpClient) {
    private var isActive = false

    fun startPolling(scope: CoroutineScope) {
        isActive = true
        scope.launch {
            while (isActive) {
                try {
                    val request = Request.Builder()
                        .url("https://api.example.com/poll")
                        .build()

                    val response = client.newCall(request).execute()
                    processData(response.body?.string())
                } catch (e: Exception) {
                    delay(5000) // Error delay
                }
            }
        }
    }

    fun stop() { isActive = false }
}
```

### 3. WebSocket

**Model**: Handshake → Persistent bidirectional connection → Message exchange

**Characteristics:**
- Full-duplex communication over single TCP connection
- Minimal overhead after handshake
- Instant message delivery (<50ms)
- Binary data support

**When to use:**
- ✅ Real-time chat, messaging
- ✅ Multiplayer games
- ✅ Collaborative document editing
- ✅ Trading platforms (stock exchange)
- ❌ May be blocked by some proxies/firewalls

```kotlin
class WebSocketManager(private val client: OkHttpClient) {
    private var socket: WebSocket? = null
    private val messages = MutableSharedFlow<String>()

    fun connect(url: String) {
        val request = Request.Builder().url(url).build()

        socket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, response: Response) {
                Log.d("WS", "Connected")
            }

            override fun onMessage(ws: WebSocket, text: String) {
                scope.launch { messages.emit(text) }
            }

            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                scheduleReconnect() // Exponential backoff
            }
        })
    }

    fun send(message: String) = socket?.send(message)
    fun disconnect() = socket?.close(1000, null)
}
```

### 4. Server-Sent Events (SSE)

**Model**: Client subscribes → Server pushes events → Auto-reconnection

**Characteristics:**
- Unidirectional (server → client only)
- Automatic reconnection
- Event IDs for tracking last received event
- Text data only

**When to use:**
- ✅ News feeds, notifications
- ✅ Stock tickers, currency rates
- ✅ Server monitoring, logs
- ❌ If bidirectional needed (use WebSocket)

```kotlin
class SSEClient(private val client: OkHttpClient) {
    fun connect(url: String): Flow<String> = callbackFlow {
        val request = Request.Builder()
            .url(url)
            .header("Accept", "text/event-stream")
            .build()

        launch(Dispatchers.IO) {
            val response = client.newCall(request).execute()
            response.body?.source()?.use { source ->
                while (!source.exhausted()) {
                    val line = source.readUtf8Line() ?: continue
                    if (line.startsWith("data: ")) {
                        trySend(line.substring(6))
                    }
                }
            }
        }

        awaitClose { /* cleanup */ }
    }
}
```

### Decision Matrix

**HTTP**: Simple CRUD, RESTful APIs, cacheable data
**Long-Polling**: Fallback for WebSocket, legacy systems
**WebSocket**: Bidirectional real-time, low latency critical
**SSE**: Server→client only, text notifications, simplicity

### Best Practices

**WebSocket:**
1. Exponential backoff for reconnection
2. Heartbeat/ping-pong to detect dead connections
3. Handle network state changes
4. Protocol Buffers for binary data

**SSE:**
1. Track event IDs for resumption
2. Timeout for hung connections
3. HTTP/2 for better performance

**Long-Polling:**
1. Server-side timeout
2. Jitter to prevent thundering herd
3. Graceful error handling

---

## Follow-ups

- How to implement WebSocket reconnection with exponential backoff?
- What is the battery impact of persistent connections on mobile?
- How to handle authentication for WebSocket connections?
- When to use Protocol Buffers vs JSON over WebSocket?
- How does HTTP/2 Server Push compare to SSE?

## References

- [[c-coroutines]] - Async programming patterns
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [Server-Sent Events W3C](https://www.w3.org/TR/eventsource/)
- [OkHttp WebSocket Documentation](https://square.github.io/okhttp/features/websockets/)

## Related Questions

### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - REST API basics

### Related (Same Level)
- [[q-retrofit-library--android--medium]] - REST API client
- [[q-websocket-implementation--networking--medium]] - WebSocket setup
- [[q-server-sent-events-sse--networking--medium]] - SSE implementation
- [[q-network-error-handling-strategies--networking--medium]] - Error handling

### Advanced (Harder)
- [[q-okhttp-interceptors-advanced--networking--medium]] - OkHttp patterns
- [[q-network-request-deduplication--networking--hard]] - Request optimization
