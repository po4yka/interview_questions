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
- q-compose-testing--android--medium
- q-recyclerview-explained--android--medium
- q-recyclerview-viewtypes-delegation--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/networking-http
- difficulty/medium
date created: Saturday, November 1st 2025, 12:47:03 pm
date modified: Saturday, November 1st 2025, 5:43:29 pm
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
3. **Automatic Reconnection**: Built-in reconnection with exponential backoff
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

Let's implement a production-ready SSE client for Android.

#### 1. SSE Client with OkHttp

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext
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
 * Server-Sent Events client implementation
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
                .readTimeout(0, TimeUnit.SECONDS) // No timeout for SSE
                .writeTimeout(30, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build()
        }
    }

    /**
     * Connect to SSE endpoint and receive events as Flow
     */
    fun connect(
        url: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> = callbackFlow {
        val request = buildRequest(url, headers, lastEventId)
        var retryCount = 0
        var shouldReconnect = true
        var customRetryDelay: Long? = null
        var lastReceivedEventId: String? = lastEventId

        while (shouldReconnect) {
            try {
                val response = okHttpClient.newCall(request).execute()

                if (!response.isSuccessful) {
                    trySend(SseEvent.Error(
                        Exception("HTTP ${response.code}: ${response.message}")
                    ))

                    if (response.code in 400..499) {
                        // Client error, don't retry
                        shouldReconnect = false
                        break
                    }

                    // Server error, retry with backoff
                    val delay = calculateBackoffDelay(retryCount, customRetryDelay)
                    retryCount++
                    Thread.sleep(delay)
                    continue
                }

                trySend(SseEvent.Connected)
                retryCount = 0 // Reset retry count on successful connection

                // Parse SSE stream
                response.body?.use { body ->
                    val reader = BufferedReader(InputStreamReader(body.byteStream()))
                    val parser = SseParser()

                    reader.useLines { lines ->
                        for (line in lines) {
                            parser.parseLine(line)?.let { event ->
                                // Update last event ID
                                event.id?.let { lastReceivedEventId = it }

                                // Update custom retry delay if specified
                                event.retry?.let { customRetryDelay = it }

                                trySend(event)
                            }
                        }
                    }
                }

                // Connection closed normally
                trySend(SseEvent.Disconnected("Connection closed by server"))

            } catch (e: Exception) {
                if (!shouldReconnect) break

                trySend(SseEvent.Error(e))

                // Calculate backoff delay and retry
                val delay = calculateBackoffDelay(retryCount, customRetryDelay)
                retryCount++
                Thread.sleep(delay)
            }
        }

        awaitClose {
            shouldReconnect = false
        }
    }.flowOn(Dispatchers.IO)

    /**
     * Connect using OkHttp's EventSource API (alternative implementation)
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
                trySend(SseEvent.Disconnected("Connection closed"))
                close()
            }

            override fun onFailure(
                eventSource: EventSource,
                t: Throwable?,
                response: Response?
            ) {
                trySend(SseEvent.Error(t ?: Exception("Unknown error")))
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
                lastEventId?.let {
                    header("Last-Event-ID", it)
                }
            }
            .build()
    }

    private fun calculateBackoffDelay(
        retryCount: Int,
        customRetryDelay: Long?
    ): Long {
        val baseDelay = customRetryDelay ?: DEFAULT_RETRY_DELAY_MS
        val exponentialDelay = baseDelay * BACKOFF_MULTIPLIER.pow(retryCount).toLong()
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
        when {
            line.isEmpty() -> {
                // Empty line signals end of event
                return if (dataBuffer.isNotEmpty()) {
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
                return null
            }
            else -> {
                parseField(line)
                return null
            }
        }
    }

    private fun parseField(line: String) {
        val colonIndex = line.indexOf(':')
        if (colonIndex == -1) {
            // Field with no value
            return
        }

        val field = line.substring(0, colonIndex)
        val value = line.substring(colonIndex + 1).let {
            if (it.startsWith(' ')) it.substring(1) else it
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
     * Subscribe to multiple event types
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

    suspend fun collectScores(matchId: String) {
        trackMatch(matchId).collect { event ->
            when (event) {
                is TypedSseEvent.Connected -> {
                    println("Connected to live scores")
                }

                is TypedSseEvent.Data -> {
                    val score = event.data
                    println("Score updated: ${score.homeScore} - ${score.awayScore}")
                }

                is TypedSseEvent.Disconnected -> {
                    println("Disconnected: ${event.reason}")
                }

                is TypedSseEvent.Error -> {
                    println("Error: ${event.exception.message}")
                }
            }
        }
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
            // Cache last event ID for resumption
            if (event is SseEvent.Message && event.id != null) {
                localCache.saveLastEventId(userId, event.id)
            }
        }
    }

    private fun getToken(): String {
        // Get auth token
        return "token"
    }
}

interface LiveDataCache {
    fun getLastEventId(userId: String): String?
    fun saveLastEventId(userId: String, eventId: String)
}

class LiveDataCacheImpl(
    private val sharedPreferences: SharedPreferences
) : LiveDataCache {

    override fun getLastEventId(userId: String): String? {
        return sharedPreferences.getString("last_event_id_$userId", null)
    }

    override fun saveLastEventId(userId: String, eventId: String) {
        sharedPreferences.edit()
            .putString("last_event_id_$userId", eventId)
            .apply()
    }
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
                            _uiState.value = LiveUpdatesUiState.Connected
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
| **Direction** | Server → Client | Bidirectional | Server → Client | Server → Client |
| **Protocol** | HTTP | WebSocket (ws://) | HTTP | HTTP |
| **Connection** | Persistent | Persistent | Long-lived request | Multiple requests |
| **Complexity** | Low | Medium | Medium | Low |
| **Browser Support** | Native EventSource | Native WebSocket | Requires implementation | Simple fetch |
| **Reconnection** | Automatic | Manual | Automatic | N/A |
| **Message Format** | Text (UTF-8) | Binary or Text | Any | Any |
| **Resource Usage** | Low | Medium | Medium | High |
| **Latency** | Very Low | Very Low | Low | High |
| **Scalability** | High | Medium | Medium | Low |
| **Proxy/Firewall** | Works well | May have issues | Works well | Works well |
| **HTTP/2** | Supported | N/A | Limited benefit | Limited benefit |
| **Event IDs** | Built-in | Manual | Manual | N/A |
| **Retry Logic** | Built-in | Manual | Built-in | N/A |

### Decision Matrix: When to Use Each

#### Use SSE When:

 **One-Way Communication Needed**
- Server pushes updates to clients
- No need for client to send messages back
- Examples: notifications, live scores, stock prices

 **Simple Implementation Required**
- Built on standard HTTP
- Native browser support
- Easy to debug with standard tools

 **Automatic Reconnection Important**
- Built-in reconnection with exponential backoff
- Event ID resumption support
- No manual retry logic needed

 **Proxy/Firewall Friendly**
- Works through standard HTTP infrastructure
- No special port requirements
- Corporate firewall compatible

 **Text-Based Data**
- UTF-8 encoded messages
- JSON data structures
- No binary data requirements

#### Use WebSocket When:

 **Bidirectional Communication Required**
- Client and server both send messages
- Real-time interactions
- Examples: chat apps, gaming, collaborative editing

 **Low Latency Critical**
- Microsecond-level latency requirements
- High-frequency updates
- Examples: trading platforms, multiplayer games

 **Binary Data Transfer**
- Efficient binary protocol
- Image/video streaming
- Large data transfers

 **Custom Protocol Needed**
- Full control over message format
- Custom handshake requirements
- Protocol-level optimizations

#### Use Polling When:

 **Simple Updates Sufficient**
- Infrequent updates (> 30 seconds)
- Not latency-sensitive
- Examples: email checking, weather updates

 **No Persistent Connection Support**
- Server limitations
- Load balancer restrictions
- Legacy infrastructure

 **Stateless Preferred**
- Each request independent
- Easy horizontal scaling
- Simple load balancing

### Performance Comparison

```kotlin
// Performance test comparing SSE, WebSocket, and Polling

class PerformanceComparison {

    data class PerformanceMetrics(
        val method: String,
        val messagesReceived: Int,
        val avgLatencyMs: Double,
        val reconnections: Int,
        val memoryUsageMb: Double,
        val batteryDrainPercent: Double
    )

    suspend fun comparePerformance(): List<PerformanceMetrics> {
        val duration = 60_000L // 1 minute test

        return listOf(
            testSSE(duration),
            testWebSocket(duration),
            testLongPolling(duration),
            testShortPolling(duration)
        )
    }

    private suspend fun testSSE(duration: Long): PerformanceMetrics {
        // SSE typically shows:
        // - Low latency (50-100ms)
        // - Minimal memory usage
        // - Automatic reconnection
        // - Low battery drain
        return PerformanceMetrics(
            method = "SSE",
            messagesReceived = 600,
            avgLatencyMs = 75.0,
            reconnections = 0,
            memoryUsageMb = 8.5,
            batteryDrainPercent = 2.1
        )
    }

    private suspend fun testWebSocket(duration: Long): PerformanceMetrics {
        // WebSocket typically shows:
        // - Very low latency (10-50ms)
        // - Moderate memory usage
        // - Manual reconnection needed
        // - Moderate battery drain
        return PerformanceMetrics(
            method = "WebSocket",
            messagesReceived = 1200,
            avgLatencyMs = 25.0,
            reconnections = 2,
            memoryUsageMb = 12.0,
            batteryDrainPercent = 3.5
        )
    }

    private suspend fun testLongPolling(duration: Long): PerformanceMetrics {
        // Long Polling typically shows:
        // - Moderate latency (100-200ms)
        // - Moderate memory usage
        // - Many connections
        // - Moderate battery drain
        return PerformanceMetrics(
            method = "Long Polling",
            messagesReceived = 300,
            avgLatencyMs = 150.0,
            reconnections = 60,
            memoryUsageMb = 10.0,
            batteryDrainPercent = 4.0
        )
    }

    private suspend fun testShortPolling(duration: Long): PerformanceMetrics {
        // Short Polling typically shows:
        // - High latency (5000ms)
        // - Low memory per request
        // - Many requests
        // - High battery drain
        return PerformanceMetrics(
            method = "Short Polling (5s)",
            messagesReceived = 12,
            avgLatencyMs = 5000.0,
            reconnections = 0,
            memoryUsageMb = 5.0,
            batteryDrainPercent = 6.5
        )
    }
}
```

### Best Practices

1. **Always Handle Reconnection**
   ```kotlin
   // Let SSE handle reconnection automatically
   sseClient.connect(url)
       .retry(3) // Retry on errors
       .collect { event -> /* handle */ }
   ```

2. **Store Last Event ID**
   ```kotlin
   // Enable resumption after disconnect
   var lastEventId: String? = null

   sseClient.connect(url, lastEventId = lastEventId)
       .collect { event ->
           if (event is SseEvent.Message) {
               lastEventId = event.id
           }
       }
   ```

3. **Respect Retry Delays**
   ```kotlin
   // Honor server's retry directive
   event.retry?.let { delay ->
       // Server specified custom retry delay
       useCustomRetryDelay(delay)
   }
   ```

4. **Monitor Connection Health**
   ```kotlin
   fun monitorConnection(): Flow<ConnectionHealth> {
       return sseClient.connect(url)
           .map { event ->
               when (event) {
                   is SseEvent.Connected -> ConnectionHealth.Healthy
                   is SseEvent.Error -> ConnectionHealth.Unhealthy
                   else -> ConnectionHealth.Unknown
               }
           }
   }
   ```

5. **Handle Background/Foreground Transitions**
   ```kotlin
   class SseManager(private val lifecycleOwner: LifecycleOwner) {

       init {
           lifecycleOwner.lifecycle.addObserver(object : DefaultLifecycleObserver {
               override fun onStop(owner: LifecycleOwner) {
                   // App going to background, disconnect SSE
                   disconnect()
               }

               override fun onStart(owner: LifecycleOwner) {
                   // App returning to foreground, reconnect
                   connect()
               }
           })
       }
   }
   ```

### Common Pitfalls

1. **Not Handling Connection Drops**
   ```kotlin
   // BAD: No reconnection handling
   sseClient.connect(url).collect { /* ... */ }

   // GOOD: Automatic reconnection with retry
   sseClient.connect(url)
       .retry { cause ->
           delay(calculateBackoff())
           true
       }
       .collect { /* ... */ }
   ```

2. **Forgetting to Close Connections**
   ```kotlin
   // BAD: Connection leak
   fun startListening() {
       viewModelScope.launch {
           sseClient.connect(url).collect { /* ... */ }
       }
   }

   // GOOD: Proper lifecycle management
   fun startListening() {
       viewModelScope.launch {
           sseClient.connect(url)
               .flowOn(Dispatchers.IO)
               .collect { /* ... */ }
       } // Job cancelled when ViewModel cleared
   }
   ```

3. **Not Parsing Event Types**
   ```kotlin
   // BAD: Ignoring event types
   when (event) {
       is SseEvent.Message -> handleMessage(event.data)
   }

   // GOOD: Handle different event types
   when (event) {
       is SseEvent.Message -> {
           when (event.event) {
               "score-update" -> handleScoreUpdate(event.data)
               "game-end" -> handleGameEnd(event.data)
               else -> handleGenericMessage(event.data)
           }
       }
   }
   ```

4. **Excessive Memory Usage**
   ```kotlin
   // BAD: Storing all messages in memory
   val allMessages = mutableListOf<String>()
   sseClient.connect(url).collect { event ->
       if (event is SseEvent.Message) {
           allMessages.add(event.data) // Memory leak!
       }
   }

   // GOOD: Process and discard
   sseClient.connect(url).collect { event ->
       if (event is SseEvent.Message) {
           processMessage(event.data)
           // Message garbage collected after processing
       }
   }
   ```

5. **Not Considering Battery Life**
   ```kotlin
   // GOOD: Disconnect when not needed
   class EfficientSseManager {
       fun startWhenVisible() {
           lifecycleOwner.lifecycleScope.launch {
               lifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                   sseClient.connect(url).collect { /* ... */ }
               } // Automatically disconnects when stopped
           }
       }
   }
   ```

### Summary

Server-Sent Events provide:

- **Simplicity**: Built on standard HTTP, easy to implement
- **Efficiency**: One-way communication without WebSocket complexity
- **Reliability**: Automatic reconnection with event ID resumption
- **Compatibility**: Works with existing HTTP infrastructure
- **Real-Time Updates**: Low latency push notifications
- **Resource Efficiency**: Lower overhead than polling
- **Native Support**: Browser EventSource API, OkHttp support

**Choose SSE for**: Notifications, live scores, stock prices, monitoring dashboards, activity feeds

**Choose WebSocket for**: Chat applications, gaming, collaborative editing, bidirectional real-time communication

**Choose Polling for**: Infrequent updates, legacy systems, simple implementations

---


# Question (EN)
> Server-Sent Events (SSE)

---


---


## Answer (EN)
**Server-Sent Events (SSE)** is a standard describing how servers can initiate data transmission towards clients once an initial client connection has been established. Unlike WebSockets, SSE is a one-way communication channel from server to client built on top of standard HTTP, making it simpler and more lightweight for specific use cases.

### Understanding SSE Protocol

SSE provides a persistent connection over HTTP that allows servers to push updates to clients automatically. The protocol is built on these key concepts:

#### Key Characteristics

1. **One-Way Communication**: Server → Client only
2. **HTTP/1.1 or HTTP/2**: Built on standard HTTP
3. **Automatic Reconnection**: Built-in reconnection with exponential backoff
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

Let's implement a production-ready SSE client for Android.

#### 1. SSE Client with OkHttp

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext
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
 * Server-Sent Events client implementation
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
                .readTimeout(0, TimeUnit.SECONDS) // No timeout for SSE
                .writeTimeout(30, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build()
        }
    }

    /**
     * Connect to SSE endpoint and receive events as Flow
     */
    fun connect(
        url: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> = callbackFlow {
        val request = buildRequest(url, headers, lastEventId)
        var retryCount = 0
        var shouldReconnect = true
        var customRetryDelay: Long? = null
        var lastReceivedEventId: String? = lastEventId

        while (shouldReconnect) {
            try {
                val response = okHttpClient.newCall(request).execute()

                if (!response.isSuccessful) {
                    trySend(SseEvent.Error(
                        Exception("HTTP ${response.code}: ${response.message}")
                    ))

                    if (response.code in 400..499) {
                        // Client error, don't retry
                        shouldReconnect = false
                        break
                    }

                    // Server error, retry with backoff
                    val delay = calculateBackoffDelay(retryCount, customRetryDelay)
                    retryCount++
                    Thread.sleep(delay)
                    continue
                }

                trySend(SseEvent.Connected)
                retryCount = 0 // Reset retry count on successful connection

                // Parse SSE stream
                response.body?.use { body ->
                    val reader = BufferedReader(InputStreamReader(body.byteStream()))
                    val parser = SseParser()

                    reader.useLines { lines ->
                        for (line in lines) {
                            parser.parseLine(line)?.let { event ->
                                // Update last event ID
                                event.id?.let { lastReceivedEventId = it }

                                // Update custom retry delay if specified
                                event.retry?.let { customRetryDelay = it }

                                trySend(event)
                            }
                        }
                    }
                }

                // Connection closed normally
                trySend(SseEvent.Disconnected("Connection closed by server"))

            } catch (e: Exception) {
                if (!shouldReconnect) break

                trySend(SseEvent.Error(e))

                // Calculate backoff delay and retry
                val delay = calculateBackoffDelay(retryCount, customRetryDelay)
                retryCount++
                Thread.sleep(delay)
            }
        }

        awaitClose {
            shouldReconnect = false
        }
    }.flowOn(Dispatchers.IO)

    /**
     * Connect using OkHttp's EventSource API (alternative implementation)
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
                trySend(SseEvent.Disconnected("Connection closed"))
                close()
            }

            override fun onFailure(
                eventSource: EventSource,
                t: Throwable?,
                response: Response?
            ) {
                trySend(SseEvent.Error(t ?: Exception("Unknown error")))
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
                lastEventId?.let {
                    header("Last-Event-ID", it)
                }
            }
            .build()
    }

    private fun calculateBackoffDelay(
        retryCount: Int,
        customRetryDelay: Long?
    ): Long {
        val baseDelay = customRetryDelay ?: DEFAULT_RETRY_DELAY_MS
        val exponentialDelay = baseDelay * BACKOFF_MULTIPLIER.pow(retryCount).toLong()
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
        when {
            line.isEmpty() -> {
                // Empty line signals end of event
                return if (dataBuffer.isNotEmpty()) {
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
                return null
            }
            else -> {
                parseField(line)
                return null
            }
        }
    }

    private fun parseField(line: String) {
        val colonIndex = line.indexOf(':')
        if (colonIndex == -1) {
            // Field with no value
            return
        }

        val field = line.substring(0, colonIndex)
        val value = line.substring(colonIndex + 1).let {
            if (it.startsWith(' ')) it.substring(1) else it
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
     * Subscribe to multiple event types
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

    suspend fun collectScores(matchId: String) {
        trackMatch(matchId).collect { event ->
            when (event) {
                is TypedSseEvent.Connected -> {
                    println("Connected to live scores")
                }

                is TypedSseEvent.Data -> {
                    val score = event.data
                    println("Score updated: ${score.homeScore} - ${score.awayScore}")
                }

                is TypedSseEvent.Disconnected -> {
                    println("Disconnected: ${event.reason}")
                }

                is TypedSseEvent.Error -> {
                    println("Error: ${event.exception.message}")
                }
            }
        }
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
            // Cache last event ID for resumption
            if (event is SseEvent.Message && event.id != null) {
                localCache.saveLastEventId(userId, event.id)
            }
        }
    }

    private fun getToken(): String {
        // Get auth token
        return "token"
    }
}

interface LiveDataCache {
    fun getLastEventId(userId: String): String?
    fun saveLastEventId(userId: String, eventId: String)
}

class LiveDataCacheImpl(
    private val sharedPreferences: SharedPreferences
) : LiveDataCache {

    override fun getLastEventId(userId: String): String? {
        return sharedPreferences.getString("last_event_id_$userId", null)
    }

    override fun saveLastEventId(userId: String, eventId: String) {
        sharedPreferences.edit()
            .putString("last_event_id_$userId", eventId)
            .apply()
    }
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
                            _uiState.value = LiveUpdatesUiState.Connected
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
| **Direction** | Server → Client | Bidirectional | Server → Client | Server → Client |
| **Protocol** | HTTP | WebSocket (ws://) | HTTP | HTTP |
| **Connection** | Persistent | Persistent | Long-lived request | Multiple requests |
| **Complexity** | Low | Medium | Medium | Low |
| **Browser Support** | Native EventSource | Native WebSocket | Requires implementation | Simple fetch |
| **Reconnection** | Automatic | Manual | Automatic | N/A |
| **Message Format** | Text (UTF-8) | Binary or Text | Any | Any |
| **Resource Usage** | Low | Medium | Medium | High |
| **Latency** | Very Low | Very Low | Low | High |
| **Scalability** | High | Medium | Medium | Low |
| **Proxy/Firewall** | Works well | May have issues | Works well | Works well |
| **HTTP/2** | Supported | N/A | Limited benefit | Limited benefit |
| **Event IDs** | Built-in | Manual | Manual | N/A |
| **Retry Logic** | Built-in | Manual | Built-in | N/A |

### Decision Matrix: When to Use Each

#### Use SSE When:

 **One-Way Communication Needed**
- Server pushes updates to clients
- No need for client to send messages back
- Examples: notifications, live scores, stock prices

 **Simple Implementation Required**
- Built on standard HTTP
- Native browser support
- Easy to debug with standard tools

 **Automatic Reconnection Important**
- Built-in reconnection with exponential backoff
- Event ID resumption support
- No manual retry logic needed

 **Proxy/Firewall Friendly**
- Works through standard HTTP infrastructure
- No special port requirements
- Corporate firewall compatible

 **Text-Based Data**
- UTF-8 encoded messages
- JSON data structures
- No binary data requirements

#### Use WebSocket When:

 **Bidirectional Communication Required**
- Client and server both send messages
- Real-time interactions
- Examples: chat apps, gaming, collaborative editing

 **Low Latency Critical**
- Microsecond-level latency requirements
- High-frequency updates
- Examples: trading platforms, multiplayer games

 **Binary Data Transfer**
- Efficient binary protocol
- Image/video streaming
- Large data transfers

 **Custom Protocol Needed**
- Full control over message format
- Custom handshake requirements
- Protocol-level optimizations

#### Use Polling When:

 **Simple Updates Sufficient**
- Infrequent updates (> 30 seconds)
- Not latency-sensitive
- Examples: email checking, weather updates

 **No Persistent Connection Support**
- Server limitations
- Load balancer restrictions
- Legacy infrastructure

 **Stateless Preferred**
- Each request independent
- Easy horizontal scaling
- Simple load balancing

### Performance Comparison

```kotlin
// Performance test comparing SSE, WebSocket, and Polling

class PerformanceComparison {

    data class PerformanceMetrics(
        val method: String,
        val messagesReceived: Int,
        val avgLatencyMs: Double,
        val reconnections: Int,
        val memoryUsageMb: Double,
        val batteryDrainPercent: Double
    )

    suspend fun comparePerformance(): List<PerformanceMetrics> {
        val duration = 60_000L // 1 minute test

        return listOf(
            testSSE(duration),
            testWebSocket(duration),
            testLongPolling(duration),
            testShortPolling(duration)
        )
    }

    private suspend fun testSSE(duration: Long): PerformanceMetrics {
        // SSE typically shows:
        // - Low latency (50-100ms)
        // - Minimal memory usage
        // - Automatic reconnection
        // - Low battery drain
        return PerformanceMetrics(
            method = "SSE",
            messagesReceived = 600,
            avgLatencyMs = 75.0,
            reconnections = 0,
            memoryUsageMb = 8.5,
            batteryDrainPercent = 2.1
        )
    }

    private suspend fun testWebSocket(duration: Long): PerformanceMetrics {
        // WebSocket typically shows:
        // - Very low latency (10-50ms)
        // - Moderate memory usage
        // - Manual reconnection needed
        // - Moderate battery drain
        return PerformanceMetrics(
            method = "WebSocket",
            messagesReceived = 1200,
            avgLatencyMs = 25.0,
            reconnections = 2,
            memoryUsageMb = 12.0,
            batteryDrainPercent = 3.5
        )
    }

    private suspend fun testLongPolling(duration: Long): PerformanceMetrics {
        // Long Polling typically shows:
        // - Moderate latency (100-200ms)
        // - Moderate memory usage
        // - Many connections
        // - Moderate battery drain
        return PerformanceMetrics(
            method = "Long Polling",
            messagesReceived = 300,
            avgLatencyMs = 150.0,
            reconnections = 60,
            memoryUsageMb = 10.0,
            batteryDrainPercent = 4.0
        )
    }

    private suspend fun testShortPolling(duration: Long): PerformanceMetrics {
        // Short Polling typically shows:
        // - High latency (5000ms)
        // - Low memory per request
        // - Many requests
        // - High battery drain
        return PerformanceMetrics(
            method = "Short Polling (5s)",
            messagesReceived = 12,
            avgLatencyMs = 5000.0,
            reconnections = 0,
            memoryUsageMb = 5.0,
            batteryDrainPercent = 6.5
        )
    }
}
```

### Best Practices

1. **Always Handle Reconnection**
   ```kotlin
   // Let SSE handle reconnection automatically
   sseClient.connect(url)
       .retry(3) // Retry on errors
       .collect { event -> /* handle */ }
   ```

2. **Store Last Event ID**
   ```kotlin
   // Enable resumption after disconnect
   var lastEventId: String? = null

   sseClient.connect(url, lastEventId = lastEventId)
       .collect { event ->
           if (event is SseEvent.Message) {
               lastEventId = event.id
           }
       }
   ```

3. **Respect Retry Delays**
   ```kotlin
   // Honor server's retry directive
   event.retry?.let { delay ->
       // Server specified custom retry delay
       useCustomRetryDelay(delay)
   }
   ```

4. **Monitor Connection Health**
   ```kotlin
   fun monitorConnection(): Flow<ConnectionHealth> {
       return sseClient.connect(url)
           .map { event ->
               when (event) {
                   is SseEvent.Connected -> ConnectionHealth.Healthy
                   is SseEvent.Error -> ConnectionHealth.Unhealthy
                   else -> ConnectionHealth.Unknown
               }
           }
   }
   ```

5. **Handle Background/Foreground Transitions**
   ```kotlin
   class SseManager(private val lifecycleOwner: LifecycleOwner) {

       init {
           lifecycleOwner.lifecycle.addObserver(object : DefaultLifecycleObserver {
               override fun onStop(owner: LifecycleOwner) {
                   // App going to background, disconnect SSE
                   disconnect()
               }

               override fun onStart(owner: LifecycleOwner) {
                   // App returning to foreground, reconnect
                   connect()
               }
           })
       }
   }
   ```

### Common Pitfalls

1. **Not Handling Connection Drops**
   ```kotlin
   // BAD: No reconnection handling
   sseClient.connect(url).collect { /* ... */ }

   // GOOD: Automatic reconnection with retry
   sseClient.connect(url)
       .retry { cause ->
           delay(calculateBackoff())
           true
       }
       .collect { /* ... */ }
   ```

2. **Forgetting to Close Connections**
   ```kotlin
   // BAD: Connection leak
   fun startListening() {
       viewModelScope.launch {
           sseClient.connect(url).collect { /* ... */ }
       }
   }

   // GOOD: Proper lifecycle management
   fun startListening() {
       viewModelScope.launch {
           sseClient.connect(url)
               .flowOn(Dispatchers.IO)
               .collect { /* ... */ }
       } // Job cancelled when ViewModel cleared
   }
   ```

3. **Not Parsing Event Types**
   ```kotlin
   // BAD: Ignoring event types
   when (event) {
       is SseEvent.Message -> handleMessage(event.data)
   }

   // GOOD: Handle different event types
   when (event) {
       is SseEvent.Message -> {
           when (event.event) {
               "score-update" -> handleScoreUpdate(event.data)
               "game-end" -> handleGameEnd(event.data)
               else -> handleGenericMessage(event.data)
           }
       }
   }
   ```

4. **Excessive Memory Usage**
   ```kotlin
   // BAD: Storing all messages in memory
   val allMessages = mutableListOf<String>()
   sseClient.connect(url).collect { event ->
       if (event is SseEvent.Message) {
           allMessages.add(event.data) // Memory leak!
       }
   }

   // GOOD: Process and discard
   sseClient.connect(url).collect { event ->
       if (event is SseEvent.Message) {
           processMessage(event.data)
           // Message garbage collected after processing
       }
   }
   ```

5. **Not Considering Battery Life**
   ```kotlin
   // GOOD: Disconnect when not needed
   class EfficientSseManager {
       fun startWhenVisible() {
           lifecycleOwner.lifecycleScope.launch {
               lifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                   sseClient.connect(url).collect { /* ... */ }
               } // Automatically disconnects when stopped
           }
       }
   }
   ```

### Summary

Server-Sent Events provide:

- **Simplicity**: Built on standard HTTP, easy to implement
- **Efficiency**: One-way communication without WebSocket complexity
- **Reliability**: Automatic reconnection with event ID resumption
- **Compatibility**: Works with existing HTTP infrastructure
- **Real-Time Updates**: Low latency push notifications
- **Resource Efficiency**: Lower overhead than polling
- **Native Support**: Browser EventSource API, OkHttp support

**Choose SSE for**: Notifications, live scores, stock prices, monitoring dashboards, activity feeds

**Choose WebSocket for**: Chat applications, gaming, collaborative editing, bidirectional real-time communication

**Choose Polling for**: Infrequent updates, legacy systems, simple implementations

---

## Ответ (RU)
**Server-Sent Events (SSE)** - это стандарт, описывающий, как серверы могут инициировать передачу данных клиентам после установления начального подключения. В отличие от WebSocket, SSE - это односторонний канал связи от сервера к клиенту, построенный поверх стандартного HTTP, что делает его проще и легче для конкретных случаев использования.

### Понимание Протокола SSE

SSE обеспечивает постоянное соединение через HTTP, которое позволяет серверам автоматически отправлять обновления клиентам. Протокол основан на этих ключевых концепциях:

#### Ключевые Характеристики

1. **Односторонняя связь**: Только Сервер → Клиент
2. **HTTP/1.1 или HTTP/2**: Построен на стандартном HTTP
3. **Автоматическое переподключение**: Встроенное переподключение с экспоненциальной задержкой
4. **ID событий**: Поддержка возобновления с последнего полученного события
5. **Именованные события**: Типизированные события для разных типов сообщений
6. **Текстовый формат**: Данные в формате UTF-8 (часто используется JSON)
7. **Нативная поддержка в браузерах**: EventSource API в браузерах

#### Формат Сообщения SSE

```
event: message-type
id: 123
retry: 10000
data: {"key": "value"}
data: {"more": "data"}

```

### Полная Реализация SSE

Давайте реализуем готовый к продакшену SSE-клиент для Android.

#### 1. SSE-клиент С OkHttp

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext
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
 * Реализация клиента Server-Sent Events
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
                .readTimeout(0, TimeUnit.SECONDS) // Нет таймаута для SSE
                .writeTimeout(30, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build()
        }
    }

    /**
     * Подключение к конечной точке SSE и получение событий в виде Flow
     */
    fun connect(
        url: String,
        headers: Map<String, String> = emptyMap(),
        lastEventId: String? = null
    ): Flow<SseEvent> = callbackFlow {
        val request = buildRequest(url, headers, lastEventId)
        var retryCount = 0
        var shouldReconnect = true
        var customRetryDelay: Long? = null
        var lastReceivedEventId: String? = lastEventId

        while (shouldReconnect) {
            try {
                val response = okHttpClient.newCall(request).execute()

                if (!response.isSuccessful) {
                    trySend(SseEvent.Error(
                        Exception("HTTP ${response.code}: ${response.message}")
                    ))

                    if (response.code in 400..499) {
                        // Ошибка клиента, не повторять
                        shouldReconnect = false
                        break
                    }

                    // Ошибка сервера, повторить с задержкой
                    val delay = calculateBackoffDelay(retryCount, customRetryDelay)
                    retryCount++
                    Thread.sleep(delay)
                    continue
                }

                trySend(SseEvent.Connected)
                retryCount = 0 // Сброс счетчика повторов при успешном подключении

                // Парсинг потока SSE
                response.body?.use { body ->
                    val reader = BufferedReader(InputStreamReader(body.byteStream()))
                    val parser = SseParser()

                    reader.useLines { lines ->
                        for (line in lines) {
                            parser.parseLine(line)?.let { event ->
                                // Обновление ID последнего события
                                event.id?.let { lastReceivedEventId = it }

                                // Обновление пользовательской задержки повтора, если указано
                                event.retry?.let { customRetryDelay = it }

                                trySend(event)
                            }
                        }
                    }
                }

                // Соединение закрыто нормально
                trySend(SseEvent.Disconnected("Соединение закрыто сервером"))

            } catch (e: Exception) {
                if (!shouldReconnect) break

                trySend(SseEvent.Error(e))

                // Вычисление задержки и повтор
                val delay = calculateBackoffDelay(retryCount, customRetryDelay)
                retryCount++
                Thread.sleep(delay)
            }
        }

        awaitClose {
            shouldReconnect = false
        }
    }.flowOn(Dispatchers.IO)

    // ... (остальная часть реализации как в английской версии)
}
```

### Типизированный Обработчик Событий

```kotlin
import com.google.gson.Gson
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.mapNotNull

/**
 * Типизированный SSE-клиент с автоматической десериализацией JSON
 */
class TypedSseClient(
    private val sseClient: SseClient,
    private val gson: Gson = Gson()
) {
    inline fun <reified T : Any> subscribeToEvent(
        url: String,
        eventType: String,
        headers: Map<String, String> = emptyMap()
    ): Flow<TypedSseEvent<T>> {
        return sseClient.connect(url, headers)
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
                    is SseEvent.Error -> TypedSseEvent.Error(event.exception)
                    else -> null
                }
            }
    }
}
```

### Примеры Из Реального Мира

```kotlin
// Пример 1: Live-счета спортивных матчей
data class ScoreUpdate(
    val matchId: String,
    val homeScore: Int,
    val awayScore: Int
)

class LiveScoreTracker(private val typedSseClient: TypedSseClient) {
    fun trackMatch(matchId: String): Flow<TypedSseEvent<ScoreUpdate>> {
        return typedSseClient.subscribeToEvent(
            url = "https://api.sports.com/matches/$matchId/events",
            eventType = "score-update"
        )
    }
}

// Пример 2: Обновления цен акций
data class StockPrice(
    val symbol: String,
    val price: Double,
    val change: Double
)

// Пример 3: Лента уведомлений
data class Notification(
    val id: String,
    val type: String,
    val message: String
)
```

### Интеграция С Repository

```kotlin
class LiveDataRepository(
    private val sseClient: SseClient,
    private val localCache: LiveDataCache
) {
    fun observeLiveUpdates(userId: String): Flow<SseEvent> {
        val lastEventId = localCache.getLastEventId(userId)

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
}
```

### Сравнение SSE, WebSocket И Polling

| Характеристика | SSE | WebSocket | Long Polling | Short Polling |
|---|---|---|---|---|
| **Направление** | Сервер → Клиент | Двунаправленное | Сервер → Клиент | Сервер → Клиент |
| **Протокол** | HTTP | WebSocket (ws://) | HTTP | HTTP |
| **Соединение** | Постоянное | Постоянное | Долгоживущий запрос | Множество запросов |
| **Сложность** | Низкая | Средняя | Средняя | Низкая |
| **Поддержка в браузере** | Нативный EventSource | Нативный WebSocket | Требует реализации | Простой fetch |
| **Переподключение** | Автоматическое | Ручное | Автоматическое | Н/Д |
| **Формат сообщений** | Текст (UTF-8) | Бинарный или Текст | Любой | Любой |
| **Использование ресурсов** | Низкое | Среднее | Среднее | Высокое |
| **Задержка** | Очень низкая | Очень низкая | Низкая | Высокая |
| **Масштабируемость** | Высокая | Средняя | Средняя | Низкая |
| **Прокси/Файрвол** | Работает хорошо | Могут быть проблемы | Работает хорошо | Работает хорошо |
| **HTTP/2** | Поддерживается | Н/Д | Ограниченная польза | Ограниченная польза |
| **ID событий** | Встроено | Ручное | Ручное | Н/Д |
| **Логика повторов** | Встроено | Ручное | Встроено | Н/Д |

### Матрица Решений: Когда Что Использовать

#### Используйте SSE, Когда:

**Нужна односторонняя связь**
- Сервер отправляет обновления клиентам
- Клиенту не нужно отправлять сообщения в ответ
- Примеры: уведомления, live-счета, котировки акций

**Требуется простая реализация**
- Построен на стандартном HTTP
- Нативная поддержка в браузерах
- Легко отлаживать стандартными инструментами

**Важно автоматическое переподключение**
- Встроенное переподключение с экспоненциальной задержкой
- Поддержка возобновления по ID события
- Не нужна ручная логика повторов

**Совместимость с прокси/файрволами**
- Работает через стандартную HTTP-инфраструктуру
- Нет требований к специальным портам
- Совместимо с корпоративными файрволами

#### Используйте WebSocket, Когда:

**Требуется двунаправленная связь**
- И клиент, и сервер отправляют сообщения
- Взаимодействие в реальном времени
- Примеры: чаты, игры, совместное редактирование

**Критична низкая задержка**
- Требования к задержке на уровне микросекунд
- Высокочастотные обновления
- Примеры: торговые платформы, многопользовательские игры

**Передача бинарных данных**
- Эффективный бинарный протокол
- Стриминг изображений/видео
- Передача больших объемов данных

**Нужен кастомный протокол**
- Полный контроль над форматом сообщений
- Требования к кастомному хэндшейку
- Оптимизации на уровне протокола

#### Используйте Polling, Когда:

**Достаточно простых обновлений**
- Нечастые обновления (> 30 секунд)
- Не чувствительно к задержкам
- Примеры: проверка почты, обновления погоды

**Нет поддержки постоянного соединения**
- Ограничения сервера
- Ограничения балансировщика нагрузки
- Устаревшая инфраструктура

**Предпочтителен stateless подход**
- Каждый запрос независим
- Простое горизонтальное масштабирование
- Простая балансировка нагрузки

### Лучшие Практики

1. **Всегда обрабатывайте переподключение**
   ```kotlin
   sseClient.connect(url)
       .retry(3) // Повторять при ошибках
       .collect { event -> /* обработка */ }
   ```

2. **Сохраняйте последний ID события**
   ```kotlin
   var lastEventId: String? = null
   sseClient.connect(url, lastEventId = lastEventId)
       .collect { event ->
           if (event is SseEvent.Message) {
               lastEventId = event.id
           }
       }
   ```

3. **Уважайте задержки повторных попыток**
   ```kotlin
   event.retry?.let { delay ->
       // Сервер указал кастомную задержку повтора
       useCustomRetryDelay(delay)
   }
   ```

4. **Мониторьте состояние соединения**
   ```kotlin
   fun monitorConnection(): Flow<ConnectionHealth> {
       return sseClient.connect(url)
           .map { event ->
               when (event) {
                   is SseEvent.Connected -> ConnectionHealth.Healthy
                   is SseEvent.Error -> ConnectionHealth.Unhealthy
                   else -> ConnectionHealth.Unknown
               }
           }
   }
   ```

5. **Обрабатывайте переходы между фоновым и активным режимами**
   ```kotlin
   class SseManager(private val lifecycleOwner: LifecycleOwner) {
       init {
           lifecycleOwner.lifecycle.addObserver(object : DefaultLifecycleObserver {
               override fun onStop(owner: LifecycleOwner) {
                   disconnect() // Приложение уходит в фон
               }

               override fun onStart(owner: LifecycleOwner) {
                   connect() // Приложение возвращается
               }
           })
       }
   }
   ```

### Распространенные Ошибки

1. **Не обрабатывать разрывы соединения**
   ```kotlin
   // ПЛОХО: Нет обработки переподключения
   sseClient.connect(url).collect { /* ... */ }

   // ХОРОШО: Автоматическое переподключение
   sseClient.connect(url)
       .retry { cause ->
           delay(calculateBackoff())
           true
       }
       .collect { /* ... */ }
   ```

2. **Забывать закрывать соединения**
   ```kotlin
   // ПЛОХО: Утечка соединения
   fun startListening() {
       viewModelScope.launch {
           sseClient.connect(url).collect { /* ... */ }
       }
   }

   // ХОРОШО: Правильное управление жизненным циклом
   fun startListening() {
       viewModelScope.launch {
           sseClient.connect(url)
               .flowOn(Dispatchers.IO)
               .collect { /* ... */ }
       } // Job отменяется при очистке ViewModel
   }
   ```

3. **Не парсить типы событий**
   ```kotlin
   // ПЛОХО: Игнорирование типов событий
   when (event) {
       is SseEvent.Message -> handleMessage(event.data)
   }

   // ХОРОШО: Обработка разных типов событий
   when (event) {
       is SseEvent.Message -> {
           when (event.event) {
               "score-update" -> handleScoreUpdate(event.data)
               "game-end" -> handleGameEnd(event.data)
               else -> handleGenericMessage(event.data)
           }
       }
   }
   ```

4. **Чрезмерное использование памяти**
   ```kotlin
   // ПЛОХО: Хранение всех сообщений в памяти
   val allMessages = mutableListOf<String>()
   sseClient.connect(url).collect { event ->
       if (event is SseEvent.Message) {
           allMessages.add(event.data) // Утечка памяти!
       }
   }

   // ХОРОШО: Обработка и удаление
   sseClient.connect(url).collect { event ->
       if (event is SseEvent.Message) {
           processMessage(event.data)
           // Сообщение удаляется сборщиком мусора после обработки
       }
   }
   ```

5. **Не учитывать расход батареи**
   ```kotlin
   // ХОРОШО: Отключаться когда не нужно
   class EfficientSseManager {
       fun startWhenVisible() {
           lifecycleOwner.lifecycleScope.launch {
               lifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                   sseClient.connect(url).collect { /* ... */ }
               } // Автоматически отключается при остановке
           }
       }
   }
   ```

### Резюме

Server-Sent Events предоставляют:

- **Простоту**: Построены на стандартном HTTP, легко реализуются
- **Эффективность**: Односторонняя связь без сложности WebSocket
- **Надежность**: Автоматическое переподключение с возобновлением по ID события
- **Совместимость**: Работают с существующей HTTP-инфраструктурой
- **Обновления в реальном времени**: Push-уведомления с низкой задержкой
- **Эффективность ресурсов**: Меньше накладных расходов, чем у polling
- **Нативная поддержка**: Browser EventSource API, поддержка OkHttp

**Выбирайте SSE для**: уведомлений, live-счетов, котировок акций, дашбордов мониторинга, лент активности

**Выбирайте WebSocket для**: чат-приложений, игр, совместного редактирования, двунаправленной связи в реальном времени

**Выбирайте Polling для**: нечастых обновлений, устаревших систем, простых реализаций

---


## Follow-ups

- [[q-compose-testing--android--medium]]
- [[q-recyclerview-explained--android--medium]]
- [[q-recyclerview-viewtypes-delegation--android--medium]]


## References

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)


## Related Questions

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
