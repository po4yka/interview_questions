---
id: android-286
title: Server-Sent Events (SSE) / Server-Sent Events (SSE)
aliases:
- Server-Sent Events
- SSE
topic: android
subtopics:
- networking-http
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-retrofit
- q-compose-testing--android--medium
- q-recyclerview-explained--android--medium
- q-recyclerview-viewtypes-delegation--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/networking-http
- difficulty/medium
---

# Вопрос (RU)
> Server-Sent Events (SSE)

# Question (EN)
> Server-Sent Events (SSE)

---

## Answer (EN)
**Server-Sent Events (SSE)** is a standard describing how servers can initiate data transmission towards clients once an initial client connection has been established. Unlike WebSockets, SSE is a one-way communication channel from server to client built on top of standard HTTP, making it simpler and more lightweight for specific use cases.

### Understanding SSE Protocol

SSE provides a persistent connection over HTTP that allows servers to push updates to clients automatically. The protocol is built on these key concepts:

#### Key Characteristics

1. **One-Way Communication**: Server → Client only
2. **HTTP/1.1 or HTTP/2**: Built on standard HTTP
3. **Automatic Reconnection Semantics**: Via the `retry` field and `Last-Event-ID` header; browser EventSource implements this, on Android you implement it yourself
4. **Event IDs**: Support for resuming from last received event
5. **Named Events**: Typed events for different message types
6. **Text-Based**: UTF-8 text data (JSON commonly used)
7. **Browser Native Support**: EventSource API in browsers

#### SSE Message Format

```
event: message-type
id: 123
retry: 10000
data: {"key": "value"}
data: {"more": "data"}

```

### Complete SSE Implementation

Below is an example of an SSE client for Android based on OkHttp. It demonstrates parsing, reconnection with backoff, and integration with Kotlin Flow. It is simplified for interview/educational purposes and should be adapted for production (e.g., robust error handling, resource cleanup, tuning, etc.).

#### 1. SSE Client with OkHttp

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.sse.EventSource
import okhttp3.sse.EventSourceListener
import okhttp3.sse.EventSources
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.concurrent.TimeUnit
import kotlin.math.min
import kotlin.math.pow

/**
 * Server-Sent Events client implementation (simplified example)
 */
class SseClient(
    private val okHttpClient: OkHttpClient = createDefaultClient()
) {

    companion object {
        private const val DEFAULT_RETRY_DELAY_MS = 3000L
        private const val MAX_RETRY_DELAY_MS = 60000L
        private const val BACKOFF_MULTIPLIER = 2.0

        private fun createDefaultClient(): OkHttpClient {
            return OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(0, TimeUnit.SECONDS) // No read timeout for SSE stream
                .writeTimeout(30, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build()
        }
    }

    /**
     * Connect to SSE endpoint and receive events as Flow.
     * Includes internal reconnection with backoff; in real projects, prefer a
     * non-blocking, cancellation-aware implementation and avoid duplicating retries outside.
     */
    fun connect(
        url: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> = callbackFlow {
        var retryCount = 0
        var shouldReconnect = true
        var customRetryDelay: Long? = null
        var lastReceivedEventId: String? = lastEventId

        suspend fun attemptOnce(): Boolean {
            val request = buildRequest(url, headers, lastReceivedEventId)
            return try {
                val response = okHttpClient.newCall(request).execute()

                if (!response.isSuccessful) {
                    trySend(SseEvent.Error(Exception("HTTP ${response.code}: ${response.message}")))

                    if (response.code in 400..499) {
                        // Client error: do not retry
                        return false
                    }
                    // Server error: allow retry
                    true
                } else {
                    trySend(SseEvent.Connected)
                    retryCount = 0

                    response.body?.use { body ->
                        val reader = BufferedReader(InputStreamReader(body.byteStream()))
                        val parser = SseParser()

                        reader.useLines { lines ->
                            for (line in lines) {
                                if (!isActive) return@useLines
                                parser.parseLine(line)?.let { event ->
                                    event.id?.let { lastReceivedEventId = it }
                                    event.retry?.let { customRetryDelay = it }
                                    trySend(event)
                                }
                            }
                        }
                    }

                    trySend(SseEvent.Disconnected("Connection closed by server"))
                    // Normal close: let caller/loop decide if we should reconnect
                    true
                }
            } catch (e: Exception) {
                if (!isActive) return false
                trySend(SseEvent.Error(e))
                true
            }
        }

        val job = CoroutineScope(Dispatchers.IO).launch {
            while (shouldReconnect && isActive) {
                val shouldRetry = attemptOnce()
                if (!shouldRetry || !isActive) break

                val delayMs = calculateBackoffDelay(retryCount, customRetryDelay)
                retryCount++
                delay(delayMs)
            }
            close()
        }

        awaitClose {
            shouldReconnect = false
            job.cancel()
        }
    }.flowOn(Dispatchers.IO)

    /**
     * Connect using OkHttp's EventSource API (alternative implementation).
     * Reconnection is not automatic; if needed, implement it by re-subscribing.
     */
    fun connectWithEventSource(
        url: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> = callbackFlow {
        val request = buildRequest(url, headers, lastEventId)

        val listener = object : EventSourceListener() {
            override fun onOpen(eventSource: EventSource, response: Response) {
                trySend(SseEvent.Connected)
            }

            override fun onEvent(
                eventSource: EventSource,
                id: String?,
                type: String?,
                data: String
            ) {
                trySend(
                    SseEvent.Message(
                        data = data,
                        event = type,
                        id = id
                    )
                )
            }

            override fun onClosed(eventSource: EventSource) {
                trySend(SseEvent.Disconnected("Connection closed"))
                close()
            }

            override fun onFailure(
                eventSource: EventSource,
                t: Throwable?,
                response: Response?
            ) {
                trySend(SseEvent.Error(t ?: Exception("Unknown error")))
                // Reconnect, if desired, by re-collecting this Flow externally.
            }
        }

        val eventSource = EventSources.createFactory(okHttpClient)
            .newEventSource(request, listener)

        awaitClose {
            eventSource.cancel()
        }
    }.flowOn(Dispatchers.IO)

    private fun buildRequest(
        url: String,
        headers: Map<String, String>,
        lastEventId: String?
    ): Request {
        return Request.Builder()
            .url(url)
            .header("Accept", "text/event-stream")
            .header("Cache-Control", "no-cache")
            .apply {
                headers.forEach { (key, value) ->
                    header(key, value)
                }
                lastEventId?.let { header("Last-Event-ID", it) }
            }
            .build()
    }

    private fun calculateBackoffDelay(
        retryCount: Int,
        customRetryDelay: Long?
    ): Long {
        val baseDelay = customRetryDelay ?: DEFAULT_RETRY_DELAY_MS
        val exponentialDelay = (baseDelay * BACKOFF_MULTIPLIER.pow(retryCount)).toLong()
        return min(exponentialDelay, MAX_RETRY_DELAY_MS)
    }
}

/**
 * Parser for SSE message format
 */
class SseParser {
    private var currentEvent: String? = null
    private var currentId: String? = null
    private var currentRetry: Long? = null
    private val dataBuffer = StringBuilder()

    fun parseLine(line: String): SseEvent.Message? {
        return when {
            line.isEmpty() -> {
                // Empty line signals end of event
                if (dataBuffer.isNotEmpty()) {
                    val event = SseEvent.Message(
                        data = dataBuffer.toString().trimEnd('\n'),
                        event = currentEvent,
                        id = currentId,
                        retry = currentRetry
                    )
                    reset()
                    event
                } else {
                    null
                }
            }

            line.startsWith(":") -> {
                // Comment, ignore
                null
            }

            else -> {
                parseField(line)
                null
            }
        }
    }

    private fun parseField(line: String) {
        val colonIndex = line.indexOf(':')
        if (colonIndex == -1) return

        val field = line.substring(0, colonIndex)
        val value = line.substring(colonIndex + 1).let { raw ->
            if (raw.startsWith(' ')) raw.substring(1) else raw
        }

        when (field) {
            "event" -> currentEvent = value
            "data" -> {
                dataBuffer.append(value)
                dataBuffer.append('\n')
            }

            "id" -> currentId = value
            "retry" -> currentRetry = value.toLongOrNull()
        }
    }

    private fun reset() {
        currentEvent = null
        currentId = null
        currentRetry = null
        dataBuffer.clear()
    }
}

/**
 * Sealed class representing SSE events
 */
sealed class SseEvent {
    object Connected : SseEvent()

    data class Message(
        val data: String,
        val event: String? = null,
        val id: String? = null,
        val retry: Long? = null
    ) : SseEvent()

    data class Disconnected(val reason: String) : SseEvent()

    data class Error(val exception: Throwable) : SseEvent()
}
```

#### 2. Typed Event Handler

```kotlin
import com.google.gson.Gson
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.mapNotNull
import kotlin.reflect.KClass

/**
 * Typed SSE event handler with automatic JSON deserialization
 */
class TypedSseClient(
    private val sseClient: SseClient,
    private val gson: Gson = Gson()
) {

    /**
     * Subscribe to specific event type with automatic deserialization
     */
    inline fun <reified T : Any> subscribeToEvent(
        url: String,
        eventType: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<TypedSseEvent<T>> {
        return sseClient.connect(url, headers, lastEventId)
            .mapNotNull { event ->
                when (event) {
                    is SseEvent.Connected -> TypedSseEvent.Connected()

                    is SseEvent.Message -> {
                        if (event.event == eventType) {
                            try {
                                val data = gson.fromJson(event.data, T::class.java)
                                TypedSseEvent.Data(data, event.id)
                            } catch (e: Exception) {
                                TypedSseEvent.Error(e)
                            }
                        } else {
                            null // Filter out other event types
                        }
                    }

                    is SseEvent.Disconnected -> TypedSseEvent.Disconnected(event.reason)

                    is SseEvent.Error -> TypedSseEvent.Error(event.exception)
                }
            }
    }

    /**
     * Stub demonstrating how multiple event types could be handled.
     * Intentionally returns raw events; real implementation would dispatch via eventHandlers.
     */
    fun subscribeToEvents(
        url: String,
        eventHandlers: Map<String, EventHandler<*>>,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> {
        return sseClient.connect(url, headers, lastEventId)
    }
}

/**
 * Typed SSE event wrapper
 */
sealed class TypedSseEvent<out T> {
    class Connected<T> : TypedSseEvent<T>()
    data class Data<T>(val data: T, val id: String?) : TypedSseEvent<T>()
    data class Disconnected<T>(val reason: String) : TypedSseEvent<T>()
    data class Error<T>(val exception: Throwable) : TypedSseEvent<T>()
}

/**
 * Event handler for processing specific event types
 */
interface EventHandler<T> {
    val eventType: String
    val dataClass: KClass<T>
    fun handle(data: T, id: String?)
}
```

#### 3. Real-World Examples

```kotlin
// Example 1: Live Sports Scores
data class ScoreUpdate(
    val matchId: String,
    val homeScore: Int,
    val awayScore: Int,
    val timestamp: Long
)

class LiveScoreTracker(
    private val typedSseClient: TypedSseClient
) {

    fun trackMatch(matchId: String): Flow<TypedSseEvent<ScoreUpdate>> {
        return typedSseClient.subscribeToEvent(
            url = "https://api.sports.com/matches/$matchId/events",
            eventType = "score-update"
        )
    }
}

// Example 2: Stock Price Updates
data class StockPrice(
    val symbol: String,
    val price: Double,
    val change: Double,
    val timestamp: Long
)

class StockPriceMonitor(
    private val typedSseClient: TypedSseClient
) {

    fun monitorStocks(symbols: List<String>): Flow<TypedSseEvent<StockPrice>> {
        val symbolsParam = symbols.joinToString(",")
        return typedSseClient.subscribeToEvent(
            url = "https://api.stocks.com/stream?symbols=$symbolsParam",
            eventType = "price-update"
        )
    }
}

// Example 3: Notification Feed
data class Notification(
    val id: String,
    val type: String,
    val title: String,
    val message: String,
    val timestamp: Long,
    val read: Boolean
)

class NotificationFeed(
    private val typedSseClient: TypedSseClient
) {

    fun streamNotifications(userId: String): Flow<TypedSseEvent<Notification>> {
        return typedSseClient.subscribeToEvent(
            url = "https://api.app.com/users/$userId/notifications/stream",
            eventType = "notification",
            headers = mapOf("Authorization" to "Bearer token")
        )
    }
}
```

#### 4. Repository Integration

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.onEach

class LiveDataRepository(
    private val sseClient: SseClient,
    private val localCache: LiveDataCache
) {

    fun observeLiveUpdates(
        userId: String,
        resumeFromEventId: String? = null
    ): Flow<SseEvent> {
        val lastEventId = resumeFromEventId ?: localCache.getLastEventId(userId)

        return sseClient.connect(
            url = "https://api.example.com/users/$userId/live",
            headers = mapOf("Authorization" to "Bearer ${getToken()}"),
            lastEventId = lastEventId
        ).onEach { event ->
            if (event is SseEvent.Message && event.id != null) {
                localCache.saveLastEventId(userId, event.id)
            }
        }
    }

    private fun getToken(): String {
        // Get auth token (placeholder)
        return "token"
    }
}

interface LiveDataCache {
    fun getLastEventId(userId: String): String?
    fun saveLastEventId(userId: String, eventId: String)
}
```

#### 5. ViewModel Integration

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.onStart
import kotlinx.coroutines.launch

class LiveUpdatesViewModel(
    private val repository: LiveDataRepository,
    private val userId: String
) : ViewModel() {

    private val _uiState = MutableStateFlow<LiveUpdatesUiState>(LiveUpdatesUiState.Idle)
    val uiState: StateFlow<LiveUpdatesUiState> = _uiState

    fun startListening() {
        viewModelScope.launch {
            repository.observeLiveUpdates(userId)
                .onStart {
                    _uiState.value = LiveUpdatesUiState.Connecting
                }
                .catch { e ->
                    _uiState.value = LiveUpdatesUiState.Error(e.message ?: "Unknown error")
                }
                .collect { event ->
                    when (event) {
                        is SseEvent.Connected -> {
                            _uiState.value = LiveUpdatesUiState.Connected()
                        }

                        is SseEvent.Message -> {
                            val current = _uiState.value
                            if (current is LiveUpdatesUiState.Connected) {
                                _uiState.value = current.copy(
                                    messages = current.messages + event.data
                                )
                            }
                        }

                        is SseEvent.Disconnected -> {
                            _uiState.value = LiveUpdatesUiState.Disconnected(event.reason)
                        }

                        is SseEvent.Error -> {
                            _uiState.value = LiveUpdatesUiState.Error(
                                event.exception.message ?: "Unknown error"
                            )
                        }
                    }
                }
        }
    }
}

sealed class LiveUpdatesUiState {
    object Idle : LiveUpdatesUiState()
    object Connecting : LiveUpdatesUiState()
    data class Connected(val messages: List<String> = emptyList()) : LiveUpdatesUiState()
    data class Disconnected(val reason: String) : LiveUpdatesUiState()
    data class Error(val message: String) : LiveUpdatesUiState()
}
```

### SSE Vs WebSocket Vs Polling Comparison

| Feature | SSE | WebSocket | Long Polling | Short Polling |
|---------|-----|-----------|--------------|---------------|
| Direction | Server → Client | Bidirectional | Server → Client | Server → Client |
| Protocol | HTTP | WebSocket (ws://, wss://) | HTTP | HTTP |
| Connection | Persistent | Persistent | Long-lived request | Multiple requests |
| Complexity | Low | Medium | Medium | Low |
| Browser Support | Native EventSource | Native WebSocket | Requires implementation | Simple fetch |
| Reconnection | Built-in in EventSource (browser) / manual for custom clients | Manual in client | Manual in client | N/A |
| Message Format | Text (UTF-8) | Binary or Text | Any | Any |
| Resource Usage | Low | Medium | Medium | High |
| Latency | Very Low | Very Low | Low | High |
| Scalability | High | Medium | Medium | Low |
| Proxy/Firewall | Works well | May have issues | Works well | Works well |
| HTTP/2 | Supported | N/A | Limited benefit | Limited benefit |
| Event IDs | Built-in field | Manual | Manual | N/A |
| Retry Logic | Via `retry` and Last-Event-ID semantics | Manual | Manual | N/A |

### Decision Matrix: When to Use Each

Use SSE when:
- You need one-way server → client updates
- You prefer simple HTTP-based implementation
- You want EventSource support in browsers
- You need resume from last event using IDs
- You send text/JSON data only

Use WebSocket when:
- You need bidirectional communication
- You require very low latency in both directions
- You send binary data or need a custom protocol

Use Polling when:
- Updates are infrequent and latency is not critical
- You cannot keep long-lived connections (infrastructure constraints)
- You want a fully stateless, simple model

### Performance Comparison (Illustrative Only)

```kotlin
class PerformanceComparison {

    data class PerformanceMetrics(
        val method: String,
        val messagesReceived: Int,
        val avgLatencyMs: Double,
        val reconnections: Int,
        val memoryUsageMb: Double,
        val batteryDrainPercent: Double
    )

    // Hypothetical values to illustrate relative characteristics
    suspend fun comparePerformance(): List<PerformanceMetrics> {
        val duration = 60_000L

        return listOf(
            PerformanceMetrics("SSE", 600, 75.0, 0, 8.5, 2.1),
            PerformanceMetrics("WebSocket", 1200, 25.0, 2, 12.0, 3.5),
            PerformanceMetrics("Long Polling", 300, 150.0, 60, 10.0, 4.0),
            PerformanceMetrics("Short Polling (5s)", 12, 5000.0, 0, 5.0, 6.5)
        )
    }
}
```

### Best Practices

- Implement reconnection logic in exactly one place (inside the client or via Flow operators), not both.
- Persist and send `Last-Event-ID` to resume after disconnects.
- Respect server-provided `retry` hints when implementing backoff.
- Integrate with lifecycle (ViewModel, LifecycleOwner) to avoid leaks and unnecessary background work.
- Avoid storing all messages in memory; process and discard.

---

## Ответ (RU)
**Server-Sent Events (SSE)** — это стандарт, описывающий, как сервер может инициировать передачу данных клиенту после установления начального подключения. В отличие от WebSocket, SSE — это односторонний канал связи от сервера к клиенту поверх стандартного HTTP, что делает его проще и легче для ряда сценариев.

### Понимание протокола SSE

SSE обеспечивает постоянное HTTP-соединение, по которому сервер может автоматически отправлять обновления клиенту. Ключевые идеи протокола:

#### Ключевые характеристики

1. **Односторонняя связь**: только Сервер → Клиент
2. **HTTP/1.1 или HTTP/2**: используется стандартный HTTP
3. **Семантика автопереподключения**: через `retry` и `Last-Event-ID` (в браузерах реализовано в EventSource, на Android реализуется вручную)
4. **ID событий**: возможность возобновить поток с последнего события
5. **Именованные события**: типы событий для разных сообщений
6. **Текстовый формат**: UTF-8 (часто JSON)
7. **Нативная поддержка в браузерах**: API `EventSource`

#### Формат сообщения SSE

```
event: message-type
id: 123
retry: 10000
data: {"key": "value"}
data: {"more": "data"}

```

### Пример реализации SSE-клиента

Ниже приведён пример SSE-клиента для Android на базе OkHttp и Kotlin Flow. Он демонстрирует базовый парсинг и переподключение; для продакшена его следует доработать (обработка ошибок, отмена, логирование и т.п.).

#### 1. SSE-клиент с OkHttp

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.sse.EventSource
import okhttp3.sse.EventSourceListener
import okhttp3.sse.EventSources
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.concurrent.TimeUnit
import kotlin.math.min
import kotlin.math.pow

/**
 * Реализация клиента Server-Sent Events (упрощённый пример)
 */
class SseClient(
    private val okHttpClient: OkHttpClient = createDefaultClient()
) {

    companion object {
        private const val DEFAULT_RETRY_DELAY_MS = 3000L
        private const val MAX_RETRY_DELAY_MS = 60000L
        private const val BACKOFF_MULTIPLIER = 2.0

        private fun createDefaultClient(): OkHttpClient {
            return OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(0, TimeUnit.SECONDS) // Нет read-timeout для SSE-потока
                .writeTimeout(30, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build()
        }
    }

    /**
     * Подключение к SSE endpoint и получение событий как Flow.
     * Включает внутреннее переподключение с backoff; в реальных проектах важно
     * корректно учитывать отмену и не дублировать retries снаружи.
     */
    fun connect(
        url: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> = callbackFlow {
        var retryCount = 0
        var shouldReconnect = true
        var customRetryDelay: Long? = null
        var lastReceivedEventId: String? = lastEventId

        suspend fun attemptOnce(): Boolean {
            val request = buildRequest(url, headers, lastReceivedEventId)
            return try {
                val response = okHttpClient.newCall(request).execute()

                if (!response.isSuccessful) {
                    trySend(SseEvent.Error(Exception("HTTP ${response.code}: ${response.message}")))

                    if (response.code in 400..499) {
                        // Ошибка на стороне клиента — не переподключаемся
                        return false
                    }
                    // Ошибка сервера — можно попробовать ещё раз
                    true
                } else {
                    trySend(SseEvent.Connected)
                    retryCount = 0

                    response.body?.use { body ->
                        val reader = BufferedReader(InputStreamReader(body.byteStream()))
                        val parser = SseParser()

                        reader.useLines { lines ->
                            for (line in lines) {
                                if (!isActive) return@useLines
                                parser.parseLine(line)?.let { event ->
                                    event.id?.let { lastReceivedEventId = it }
                                    event.retry?.let { customRetryDelay = it }
                                    trySend(event)
                                }
                            }
                        }
                    }

                    trySend(SseEvent.Disconnected("Соединение закрыто сервером"))
                    true
                }
            } catch (e: Exception) {
                if (!isActive) return false
                trySend(SseEvent.Error(e))
                true
            }
        }

        val job = CoroutineScope(Dispatchers.IO).launch {
            while (shouldReconnect && isActive) {
                val shouldRetry = attemptOnce()
                if (!shouldRetry || !isActive) break

                val delayMs = calculateBackoffDelay(retryCount, customRetryDelay)
                retryCount++
                delay(delayMs)
            }
            close()
        }

        awaitClose {
            shouldReconnect = false
            job.cancel()
        }
    }.flowOn(Dispatchers.IO)

    /**
     * Альтернативный вариант с OkHttp EventSource API.
     * Переподключение остаётся задачей вызывающего кода.
     */
    fun connectWithEventSource(
        url: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> = callbackFlow {
        val request = buildRequest(url, headers, lastEventId)

        val listener = object : EventSourceListener() {
            override fun onOpen(eventSource: EventSource, response: Response) {
                trySend(SseEvent.Connected)
            }

            override fun onEvent(
                eventSource: EventSource,
                id: String?,
                type: String?,
                data: String
            ) {
                trySend(SseEvent.Message(
                    data = data,
                    event = type,
                    id = id
                ))
            }

            override fun onClosed(eventSource: EventSource) {
                trySend(SseEvent.Disconnected("Соединение закрыто"))
                close()
            }

            override fun onFailure(
                eventSource: EventSource,
                t: Throwable?,
                response: Response?
            ) {
                trySend(SseEvent.Error(t ?: Exception("Неизвестная ошибка")))
            }
        }

        val eventSource = EventSources.createFactory(okHttpClient)
            .newEventSource(request, listener)

        awaitClose {
            eventSource.cancel()
        }
    }.flowOn(Dispatchers.IO)

    private fun buildRequest(
        url: String,
        headers: Map<String, String>,
        lastEventId: String?
    ): Request {
        return Request.Builder()
            .url(url)
            .header("Accept", "text/event-stream")
            .header("Cache-Control", "no-cache")
            .apply {
                headers.forEach { (key, value) ->
                    header(key, value)
                }
                lastEventId?.let { header("Last-Event-ID", it) }
            }
            .build()
    }

    private fun calculateBackoffDelay(
        retryCount: Int,
        customRetryDelay: Long?
    ): Long {
        val baseDelay = customRetryDelay ?: DEFAULT_RETRY_DELAY_MS
        val exponentialDelay = (baseDelay * BACKOFF_MULTIPLIER.pow(retryCount)).toLong()
        return min(exponentialDelay, MAX_RETRY_DELAY_MS)
    }
}

/**
 * Парсер формата SSE-сообщений
 */
class SseParser {
    private var currentEvent: String? = null
    private var currentId: String? = null
    private var currentRetry: Long? = null
    private val dataBuffer = StringBuilder()

    fun parseLine(line: String): SseEvent.Message? {
        return when {
            line.isEmpty() -> {
                if (dataBuffer.isNotEmpty()) {
                    val event = SseEvent.Message(
                        data = dataBuffer.toString().trimEnd('\n'),
                        event = currentEvent,
                        id = currentId,
                        retry = currentRetry
                    )
                    reset()
                    event
                } else null
            }

            line.startsWith(":") -> null // комментарий

            else -> {
                parseField(line)
                null
            }
        }
    }

    private fun parseField(line: String) {
        val colonIndex = line.indexOf(':')
        if (colonIndex == -1) return

        val field = line.substring(0, colonIndex)
        val value = line.substring(colonIndex + 1).let { raw ->
            if (raw.startsWith(' ')) raw.substring(1) else raw
        }

        when (field) {
            "event" -> currentEvent = value
            "data" -> {
                dataBuffer.append(value)
                dataBuffer.append('\n')
            }
            "id" -> currentId = value
            "retry" -> currentRetry = value.toLongOrNull()
        }
    }

    private fun reset() {
        currentEvent = null
        currentId = null
        currentRetry = null
        dataBuffer.clear()
    }
}

/**
 * Модель событий SSE
 */
sealed class SseEvent {
    object Connected : SseEvent()
    data class Message(
        val data: String,
        val event: String? = null,
        val id: String? = null,
        val retry: Long? = null
    ) : SseEvent()
    data class Disconnected(val reason: String) : SseEvent()
    data class Error(val exception: Throwable) : SseEvent()
}
```

#### 2. Типизированный обработчик событий

```kotlin
import com.google.gson.Gson
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.mapNotNull
import kotlin.reflect.KClass

/**
 * Типизированный SSE-клиент с автоматической JSON-десериализацией
 */
class TypedSseClient(
    private val sseClient: SseClient,
    private val gson: Gson = Gson()
) {

    inline fun <reified T : Any> subscribeToEvent(
        url: String,
        eventType: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<TypedSseEvent<T>> {
        return sseClient.connect(url, headers, lastEventId)
            .mapNotNull { event ->
                when (event) {
                    is SseEvent.Connected -> TypedSseEvent.Connected()
                    is SseEvent.Message -> {
                        if (event.event == eventType) {
                            try {
                                val data = gson.fromJson(event.data, T::class.java)
                                TypedSseEvent.Data(data, event.id)
                            } catch (e: Exception) {
                                TypedSseEvent.Error(e)
                            }
                        } else null
                    }
                    is SseEvent.Disconnected -> TypedSseEvent.Disconnected(event.reason)
                    is SseEvent.Error -> TypedSseEvent.Error(event.exception)
                }
            }
    }

    fun subscribeToEvents(
        url: String,
        eventHandlers: Map<String, EventHandler<*>>,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> {
        // Заглушка: в реальной реализации события следует маршрутизировать по eventHandlers
        return sseClient.connect(url, headers, lastEventId)
    }
}

sealed class TypedSseEvent<out T> {
    class Connected<T> : TypedSseEvent<T>()
    data class Data<T>(val data: T, val id: String?) : TypedSseEvent<T>()
    data class Disconnected<T>(val reason: String) : TypedSseEvent<T>()
    data class Error<T>(val exception: Throwable) : TypedSseEvent<T>()
}

interface EventHandler<T> {
    val eventType: String
    val dataClass: KClass<T>
    fun handle(data: T, id: String?)
}
```

#### 3. Примеры из реального мира

```kotlin
// Пример 1: Онлайн-счёт спортивных матчей
data class ScoreUpdate(
    val matchId: String,
    val homeScore: Int,
    val awayScore: Int,
    val timestamp: Long
)

class LiveScoreTracker(
    private val typedSseClient: TypedSseClient
) {
    fun trackMatch(matchId: String): Flow<TypedSseEvent<ScoreUpdate>> {
        return typedSseClient.subscribeToEvent(
            url = "https://api.sports.com/matches/$matchId/events",
            eventType = "score-update"
        )
    }
}

// Пример 2: Котировки акций
data class StockPrice(
    val symbol: String,
    val price: Double,
    val change: Double,
    val timestamp: Long
)

class StockPriceMonitor(
    private val typedSseClient: TypedSseClient
) {
    fun monitorStocks(symbols: List<String>): Flow<TypedSseEvent<StockPrice>> {
        val symbolsParam = symbols.joinToString(",")
        return typedSseClient.subscribeToEvent(
            url = "https://api.stocks.com/stream?symbols=$symbolsParam",
            eventType = "price-update"
        )
    }
}

// Пример 3: Лента уведомлений
data class Notification(
    val id: String,
    val type: String,
    val title: String,
    val message: String,
    val timestamp: Long,
    val read: Boolean
)

class NotificationFeed(
    private val typedSseClient: TypedSseClient
) {
    fun streamNotifications(userId: String): Flow<TypedSseEvent<Notification>> {
        return typedSseClient.subscribeToEvent(
            url = "https://api.app.com/users/$userId/notifications/stream",
            eventType = "notification",
            headers = mapOf("Authorization" to "Bearer token")
        )
    }
}
```

#### 4. Интеграция с Repository

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.onEach

class LiveDataRepository(
    private val sseClient: SseClient,
    private val localCache: LiveDataCache
) {
    fun observeLiveUpdates(
        userId: String,
        resumeFromEventId: String? = null
    ): Flow<SseEvent> {
        val lastEventId = resumeFromEventId ?: localCache.getLastEventId(userId)

        return sseClient.connect(
            url = "https://api.example.com/users/$userId/live",
            headers = mapOf("Authorization" to "Bearer ${getToken()}"),
            lastEventId = lastEventId
        ).onEach { event ->
            if (event is SseEvent.Message && event.id != null) {
                localCache.saveLastEventId(userId, event.id)
            }
        }
    }

    private fun getToken(): String = "token" // заглушка
}

interface LiveDataCache {
    fun getLastEventId(userId: String): String?
    fun saveLastEventId(userId: String, eventId: String)
}
```

#### 5. Интеграция с ViewModel

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.onStart
import kotlinx.coroutines.launch

class LiveUpdatesViewModel(
    private val repository: LiveDataRepository,
    private val userId: String
) : ViewModel() {

    private val _uiState = MutableStateFlow<LiveUpdatesUiState>(LiveUpdatesUiState.Idle)
    val uiState: StateFlow<LiveUpdatesUiState> = _uiState

    fun startListening() {
        viewModelScope.launch {
            repository.observeLiveUpdates(userId)
                .onStart { _uiState.value = LiveUpdatesUiState.Connecting }
                .catch { e ->
                    _uiState.value = LiveUpdatesUiState.Error(e.message ?: "Неизвестная ошибка")
                }
                .collect { event ->
                    when (event) {
                        is SseEvent.Connected ->
                            _uiState.value = LiveUpdatesUiState.Connected()
                        is SseEvent.Message -> {
                            val current = _uiState.value
                            if (current is LiveUpdatesUiState.Connected) {
                                _uiState.value = current.copy(
                                    messages = current.messages + event.data
                                )
                            }
                        }
                        is SseEvent.Disconnected ->
                            _uiState.value = LiveUpdatesUiState.Disconnected(event.reason)
                        is SseEvent.Error ->
                            _uiState.value = LiveUpdatesUiState.Error(
                                event.exception.message ?: "Неизвестная ошибка"
                            )
                    }
                }
        }
    }
}

sealed class LiveUpdatesUiState {
    object Idle : LiveUpdatesUiState()
    object Connecting : LiveUpdatesUiState()
    data class Connected(val messages: List<String> = emptyList()) : LiveUpdatesUiState()
    data class Disconnected(val reason: String) : LiveUpdatesUiState()
    data class Error(val message: String) : LiveUpdatesUiState()
}
```

### Сравнение SSE, WebSocket и Polling

- SSE: односторонние текстовые обновления, простая реализация поверх HTTP, поддержка EventSource.
- WebSocket: двунаправленный низколатентный канал, поддержка бинарных данных.
- Long/Short Polling: резервные варианты для редких обновлений и ограниченной инфраструктуры.

### Резюме

- SSE подходит для уведомлений, live-счетов, котировок, дашбордов и лент активности.
- WebSocket выбирайте для чатов, игр, совместного редактирования и другого полноценно двунаправленного real-time.
- Polling уместен для нечастых запросов и legacy-систем.

---

## Follow-ups

- [[q-compose-testing--android--medium]]
- [[q-recyclerview-explained--android--medium]]
- [[q-recyclerview-viewtypes-delegation--android--medium]]


## References

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)


## Related Questions

### Prerequisites / Concepts

- [[c-retrofit]]


### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - Networking

### Related (Medium)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-kmm-ktor-networking--android--medium]] - Networking
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking
- [[q-network-error-handling-strategies--networking--medium]] - Networking
- [[q-api-file-upload-server--android--medium]] - Networking

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-network-request-deduplication--networking--hard]] - Networking
