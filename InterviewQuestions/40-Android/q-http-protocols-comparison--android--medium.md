---
id: android-022
title: "HTTP vs Long-Polling vs WebSocket vs SSE / HTTP против Long-Polling против WebSocket против SSE"
aliases: [HTTP Protocols Comparison, WebSocket vs HTTP, WebSocket против HTTP, Протоколы HTTP]
topic: android
subtopics: [networking-http, performance-memory, websockets]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
sources: ["https://github.com/amitshekhariitbhu/android-interview-questions"]
status: draft
moc: moc-android
related: [q-retrofit-library--android--medium, q-server-sent-events-sse--android--medium, q-websocket-implementation--android--medium]
created: 2025-10-06
updated: 2025-10-28
tags: [android/networking-http, android/performance-memory, android/websockets, difficulty/medium]

date created: Saturday, November 1st 2025, 12:46:55 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---

# Вопрос (RU)
> В чем разница между HTTP, `Long`-Polling, WebSocket и Server-Sent Events (SSE)? Когда следует использовать каждый из них?

# Question (EN)
> What are the differences between HTTP, `Long`-Polling, WebSocket, and Server-Sent Events (SSE)? When should each be used?

---

## Ответ (RU)

### Краткое Сравнение Протоколов

| Протокол | Направление | Соединение | Задержка | Real-time | Use Case |
|----------|-------------|------------|----------|-----------|----------|
| HTTP | Запрос→Ответ | Новое/мультиплексируемое | Выше при частых опросах | Нет | REST API, CRUD |
| `Long`-Polling | Запрос→Ответ | Удержание | Средняя | Почти | Уведомления (fallback) |
| WebSocket | Двунаправленный | Постоянное | Низкая | Да | Чаты, игры |
| SSE | Сервер→Клиент | Постоянное | Низкая | Да | Новости, тикеры |

### 1. HTTP (Запрос-Ответ)

**Модель**: Клиент инициирует запрос → Сервер отвечает → жизненный цикл запроса завершен.

**Характеристики:**
- Без сохранения состояния (stateless) на уровне протокола
- HTTP заголовки с каждым запросом
- При частых коротких запросах задержка и накладные расходы становятся заметными
- Поддержка кэширования
- Поддержка keep-alive (HTTP/1.1) и мультиплексирования (HTTP/2), но взаимодействие остается моделью запрос-ответ

**Когда использовать:**
- ✅ REST API и CRUD операции
- ✅ Загрузка файлов, изображений
- ✅ Нечастые или пакетные обновления данных
- ❌ Неэффективен для частых двунаправленных real-time обновлений

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

### 2. `Long`-Polling

**Модель**: Клиент → длинный запрос удерживается до появления данных или timeout → Ответ → Новый запрос.

**Характеристики:**
- Сервер держит соединение открытым до данных или timeout
- После ответа клиент сразу инициирует новый запрос
- Работает через большинство firewalls/proxy
- На каждый цикл приходятся накладные расходы HTTP-заголовков и поддержания долгоживущих соединений (особенно без HTTP/2)

**Когда использовать:**
- ✅ WebSocket заблокирован firewall/proxy
- ✅ Fallback для real-time функций
- ✅ Нечастые обновления с сервера
- ❌ Высокая нагрузка на сервер и подключения при масштабировании

```kotlin
class LongPollingClient(
    private val client: OkHttpClient,
    private val scope: CoroutineScope,
    private val endpoint: String
) {
    @Volatile
    private var isActive = false

    fun start() {
        isActive = true
        scope.launch(Dispatchers.IO) {
            while (isActive) {
                try {
                    val request = Request.Builder()
                        .url(endpoint)
                        .build()

                    client.newCall(request).execute().use { response ->
                        if (response.isSuccessful) {
                            processData(response.body?.string())
                        } else {
                            handleError(response.code)
                        }
                    }
                } catch (e: Exception) {
                    handleException(e)
                    delay(5000) // Задержка при ошибке (backoff)
                }
            }
        }
    }

    fun stop() {
        isActive = false
    }

    private fun processData(payload: String?) { /* ... */ }
    private fun handleError(code: Int) { /* ... */ }
    private fun handleException(e: Exception) { /* ... */ }
}
```

### 3. WebSocket

**Модель**: HTTP handshake → Постоянное двунаправленное соединение → Обмен сообщениями.

**Характеристики:**
- Полнодуплексная связь через одно TCP соединение
- Минимальные накладные расходы после handshake (кадры WebSocket вместо HTTP-заголовков)
- Подходит для низкой задержки; фактическая задержка зависит от сети
- Поддержка текстовых и бинарных сообщений

**Когда использовать:**
- ✅ Реал-тайм чаты, мессенджеры
- ✅ Многопользовательские игры
- ✅ Совместное редактирование документов
- ✅ Торговые платформы (биржа)
- ❌ Может блокироваться некоторыми proxy/firewall

```kotlin
class WebSocketManager(
    private val client: OkHttpClient,
    private val scope: CoroutineScope
) {
    private var socket: WebSocket? = null
    val messages = MutableSharedFlow<String>(extraBufferCapacity = 64)

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
                scheduleReconnect()
            }
        })
    }

    fun send(message: String) {
        socket?.send(message)
    }

    fun disconnect() {
        socket?.close(1000, null)
        socket = null
    }

    private fun scheduleReconnect() {
        // Экспоненциальная задержка и проверка сетевого состояния
    }
}
```

### 4. Server-Sent Events (SSE)

**Модель**: Клиент подписывается (HTTP-запрос с Accept: text/event-stream) → Сервер отправляет события в одном длинном ответе → Клиент при обрыве соединения инициирует новый запрос (часто с учётом последнего полученного id).

**Характеристики:**
- Однонаправленный (только сервер → клиент)
- Семантика автоматического переподключения и `Last-Event-ID` обычно реализуется на клиенте (в браузере через EventSource или аналогичный механизм)
- Event ID для отслеживания последнего события и возобновления
- Формат событий текстовый; двоичные данные при необходимости инкапсулируются (base64 и т.п.)

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

        val call = client.newCall(request)

        val job = launch(Dispatchers.IO) {
            try {
                call.execute().use { response ->
                    if (!response.isSuccessful) {
                        close(IOException("SSE HTTP ${'$'}{response.code}"))
                        return@use
                    }
                    val source = response.body?.source() ?: return@use
                    while (!isClosedForSend && !source.exhausted()) {
                        val line = source.readUtf8Line() ?: continue
                        // Упрощённый парсер: обрабатываем только строки вида "data: ..."
                        if (line.startsWith("data: ")) {
                            trySend(line.substring(6))
                        }
                        // Полноценный SSE-парсинг (event, id, многострочные data, разделение пустой строкой,
                        // reconnect и Last-Event-ID) должен быть реализован отдельно.
                    }
                }
            } catch (e: Exception) {
                close(e)
            }
        }

        awaitClose {
            call.cancel()
            job.cancel()
        }
    }
}
```

### Матрица Решений

**HTTP**: Простые CRUD, RESTful API, кэшируемые и нечасто изменяющиеся данные
**`Long`-Polling**: Fallback для WebSocket, legacy-системы
**WebSocket**: Двунаправленный real-time, когда критична низкая задержка и частые события
**SSE**: Только сервер→клиент, текстовые уведомления и потоки событий, когда важна простота

### Лучшие Практики

**WebSocket:**
1. Экспоненциальная задержка при переподключении
2. Heartbeat/ping-pong для обнаружения мертвых соединений
3. Обработка изменений состояния сети и фонов/foreground состояний приложения
4. Использование компактных форматов (например, Protocol Buffers) для уменьшения размера сообщений

**SSE:**
1. Отслеживание event ID для возобновления потока (через Last-Event-ID или собственный механизм)
2. Timeout и обработка обрыва соединения
3. При использовании поверх HTTP/2 учитывать особенности буферизации/мультиплексирования сервера и клиента для сохранения своевременной доставки событий

**`Long`-Polling:**
1. Корректные timeout-ы на стороне сервера
2. Jitter/backoff для предотвращения эффекта thundering herd
3. Корректная обработка ошибок и отмены запросов

## Answer (EN)

### Protocol Comparison Quick Reference

| Protocol | Direction | Connection | Latency | Real-time | Use Case |
|----------|-----------|------------|---------|-----------|----------|
| HTTP | Request→Response | New/multiplexed | Higher for frequent polling | No | REST API, CRUD |
| `Long`-Polling | Request→Response | Held | Medium | Near | Notifications (fallback) |
| WebSocket | Bidirectional | Persistent | Low | Yes | Chat, games |
| SSE | Server→Client | Persistent | Low | Yes | News, tickers |

### 1. HTTP (Request-Response)

**Model**: Client initiates request → Server responds → request lifecycle completes.

**Characteristics:**
- Stateless at protocol level (each request self-contained)
- HTTP headers sent with every request
- For frequent short polling, latency and overhead become significant
- Cacheable responses
- Keep-alive (HTTP/1.1) and multiplexing (HTTP/2) reduce connection overhead, but the pattern stays request-response

**When to use:**
- ✅ REST APIs and CRUD operations
- ✅ File/image downloads
- ✅ Infrequent or batch data updates
- ❌ Inefficient for frequent bidirectional real-time updates

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

### 2. `Long`-Polling

**Model**: Client → long request held until data or timeout → Response → New request.

**Characteristics:**
- Server keeps the connection open until data is available or timeout
- Client issues a new request immediately after each response
- Works through most firewalls/proxies
- Each cycle has HTTP header and long-held connection overhead (especially without HTTP/2)

**When to use:**
- ✅ WebSocket blocked by firewall/proxy
- ✅ Fallback for real-time features
- ✅ Infrequent server updates
- ❌ High server and connection load at scale

```kotlin
class LongPollingClient(
    private val client: OkHttpClient,
    private val scope: CoroutineScope,
    private val endpoint: String
) {
    @Volatile
    private var isActive = false

    fun start() {
        isActive = true
        scope.launch(Dispatchers.IO) {
            while (isActive) {
                try {
                    val request = Request.Builder()
                        .url(endpoint)
                        .build()

                    client.newCall(request).execute().use { response ->
                        if (response.isSuccessful) {
                            processData(response.body?.string())
                        } else {
                            handleError(response.code)
                        }
                    }
                } catch (e: Exception) {
                    handleException(e)
                    delay(5000) // Error backoff
                }
            }
        }
    }

    fun stop() {
        isActive = false
    }

    private fun processData(payload: String?) { /* ... */ }
    private fun handleError(code: Int) { /* ... */ }
    private fun handleException(e: Exception) { /* ... */ }
}
```

### 3. WebSocket

**Model**: HTTP handshake → Persistent bidirectional connection → Message exchange.

**Characteristics:**
- Full-duplex communication over a single TCP connection
- Minimal framing overhead after handshake (no full HTTP headers per message)
- Suitable for low-latency messaging; actual latency depends on network conditions
- Supports both text and binary messages

**When to use:**
- ✅ Real-time chat, messaging
- ✅ Multiplayer games
- ✅ Collaborative document editing
- ✅ Trading platforms (stock exchange)
- ❌ May be blocked by some proxies/firewalls

```kotlin
class WebSocketManager(
    private val client: OkHttpClient,
    private val scope: CoroutineScope
) {
    private var socket: WebSocket? = null
    val messages = MutableSharedFlow<String>(extraBufferCapacity = 64)

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
                scheduleReconnect()
            }
        })
    }

    fun send(message: String) {
        socket?.send(message)
    }

    fun disconnect() {
        socket?.close(1000, null)
        socket = null
    }

    private fun scheduleReconnect() {
        // Exponential backoff and network state checks
    }
}
```

### 4. Server-Sent Events (SSE)

**Model**: Client subscribes (HTTP request with Accept: text/event-stream) → Server sends events over a single long-lived response → Client re-issues the request after disconnect (often using the last received id).

**Characteristics:**
- Unidirectional (server → client only)
- Automatic reconnection semantics and `Last-Event-ID` handling are typically implemented by the client (e.g., EventSource in browsers or a custom mechanism)
- Event IDs to track the last event and resume on reconnect
- Events are textual; binary payloads must be encoded if needed

**When to use:**
- ✅ News feeds, notifications
- ✅ Stock tickers, currency rates
- ✅ Server monitoring, logs
- ❌ If bidirectional communication is required (use WebSocket)

```kotlin
class SSEClient(private val client: OkHttpClient) {
    fun connect(url: String): Flow<String> = callbackFlow {
        val request = Request.Builder()
            .url(url)
            .header("Accept", "text/event-stream")
            .build()

        val call = client.newCall(request)

        val job = launch(Dispatchers.IO) {
            try {
                call.execute().use { response ->
                    if (!response.isSuccessful) {
                        close(IOException("SSE HTTP ${'$'}{response.code}"))
                        return@use
                    }
                    val source = response.body?.source() ?: return@use
                    while (!isClosedForSend && !source.exhausted()) {
                        val line = source.readUtf8Line() ?: continue
                        // Simplified parser: handle only "data: ..." lines
                        if (line.startsWith("data: ")) {
                            trySend(line.substring(6))
                        }
                        // Full SSE parsing (event, id, multi-line data, blank line delimiters,
                        // reconnect and Last-Event-ID) should be implemented separately.
                    }
                }
            } catch (e: Exception) {
                close(e)
            }
        }

        awaitClose {
            call.cancel()
            job.cancel()
        }
    }
}
```

### Decision Matrix

**HTTP**: Simple CRUD, RESTful APIs, cacheable and infrequently changing data
**`Long`-Polling**: Fallback for WebSocket, legacy systems
**WebSocket**: Bidirectional real-time where low latency and frequent events are critical
**SSE**: Server→client only, text/event streams where simplicity is desired

### Best Practices

**WebSocket:**
1. Exponential backoff for reconnection
2. Heartbeat/ping-pong to detect dead connections
3. Handle network state changes and app background/foreground
4. Use compact formats (e.g., Protocol Buffers) to reduce payload size

**SSE:**
1. Track event IDs for resumption (via Last-Event-ID or custom mechanism)
2. Timeout and proper handling of dropped connections
3. When using over HTTP/2, be aware of server/client buffering and multiplexing behavior to maintain timely event delivery

**`Long`-Polling:**
1. Proper server-side timeouts
2. Jitter/backoff to prevent thundering herd
3. Proper error handling and request cancellation

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
- [[q-websocket-implementation--android--medium]] - WebSocket setup
- [[q-server-sent-events-sse--android--medium]] - SSE implementation
- [[q-network-error-handling-strategies--networking--medium]] - Error handling

### Advanced (Harder)
- [[q-okhttp-interceptors-advanced--networking--medium]] - OkHttp patterns
- [[q-network-request-deduplication--networking--hard]] - Request optimization
