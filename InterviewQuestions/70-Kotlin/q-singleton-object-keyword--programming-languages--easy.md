---
topic: kotlin
tags:
  - programming-languages
difficulty: easy
status: draft
---

# What keyword is used to create singleton objects in Kotlin?

**English**: What keyword is used to create singleton objects (singleton) in Kotlin?

## Answer (EN)
The `object` keyword is used to create singleton objects in Kotlin.

**Key characteristics:**
- Creates a single instance that exists throughout the application lifetime
- Thread-safe by default
- Lazily initialized on first access
- No constructor needed (automatically instantiated)
- Can contain properties, methods, and init blocks
- Can implement interfaces and inherit from classes

### Code Examples

**Basic singleton:**
```kotlin
object AppSettings {
    var theme = "Light"
    var language = "English"
    var notificationsEnabled = true

    fun printSettings() {
        println("Theme: $theme")
        println("Language: $language")
        println("Notifications: $notificationsEnabled")
    }
}

fun main() {
    // Access directly without creating instance
    println(AppSettings.theme)  // Light

    AppSettings.theme = "Dark"
    AppSettings.notificationsEnabled = false

    AppSettings.printSettings()
    // Theme: Dark
    // Language: English
    // Notifications: false
}
```

**Singleton with initialization:**
```kotlin
object Logger {
    private val startTime = System.currentTimeMillis()

    init {
        println("Logger initialized at $startTime")
    }

    fun log(message: String) {
        val elapsed = System.currentTimeMillis() - startTime
        println("[$elapsed ms] $message")
    }
}

fun main() {
    Logger.log("Application started")  // Logger initialized at 1696348800000
                                        // [5 ms] Application started
    Logger.log("Processing data")       // [12 ms] Processing data
}
```

**Singleton implementing interface:**
```kotlin
interface Cache {
    fun put(key: String, value: String)
    fun get(key: String): String?
    fun clear()
}

object MemoryCache : Cache {
    private val cache = mutableMapOf<String, String>()

    override fun put(key: String, value: String) {
        cache[key] = value
    }

    override fun get(key: String): String? {
        return cache[key]
    }

    override fun clear() {
        cache.clear()
    }
}

fun main() {
    MemoryCache.put("user_id", "12345")
    MemoryCache.put("username", "alice")

    println(MemoryCache.get("user_id"))     // 12345
    println(MemoryCache.get("username"))    // alice

    MemoryCache.clear()
    println(MemoryCache.get("user_id"))     // null
}
```

**Multiple access points - same instance:**
```kotlin
object Counter {
    private var count = 0

    fun increment() {
        count++
    }

    fun getCount() = count
}

fun incrementTwice() {
    Counter.increment()
    Counter.increment()
}

fun main() {
    println(Counter.getCount())  // 0

    Counter.increment()
    println(Counter.getCount())  // 1

    incrementTwice()
    println(Counter.getCount())  // 3

    // Same instance everywhere
    val counter1 = Counter
    val counter2 = Counter
    println(counter1 === counter2)  // true
}
```

**Real-world example: API client:**
```kotlin
object ApiClient {
    private const val BASE_URL = "https://api.example.com"
    private val headers = mutableMapOf<String, String>()

    init {
        headers["Content-Type"] = "application/json"
    }

    fun setAuthToken(token: String) {
        headers["Authorization"] = "Bearer $token"
    }

    fun get(endpoint: String): String {
        val url = "$BASE_URL$endpoint"
        println("GET $url")
        println("Headers: $headers")
        return """{"status": "success"}"""
    }

    fun post(endpoint: String, body: String): String {
        val url = "$BASE_URL$endpoint"
        println("POST $url")
        println("Headers: $headers")
        println("Body: $body")
        return """{"status": "created"}"""
    }
}

fun main() {
    ApiClient.setAuthToken("abc123xyz")

    val userData = ApiClient.get("/users/1")
    println("Response: $userData")

    val createResponse = ApiClient.post("/users", """{"name": "Alice"}""")
    println("Response: $createResponse")
}
```

---

## Ответ (RU)
# Вопрос (RU)
Какой ключевое слово используется для создания объектов-одиночек (singleton) в Kotlin?

## Ответ (RU)
object
