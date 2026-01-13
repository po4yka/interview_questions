---
anki_cards:
- slug: q-singleton-object-keyword--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-singleton-object-keyword--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-180
title: "Singleton Object Keyword / Синглтон с ключевым словом object"
aliases: [Object Keyword, Singleton, Singleton Pattern, Синглтон]
topic: kotlin
subtopics: [classes, singleton]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-associatewith-vs-associateby--kotlin--easy, q-coroutine-cancellation-cooperation--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [classes, design-patterns, difficulty/easy, kotlin, object-keyword, singleton]
---\
# Вопрос (RU)

> Какое ключевое слово используется для создания синглтонов (singleton-объектов) в Kotlin?

# Question (EN)

> What keyword is used to create singleton objects (singleton) in Kotlin?

## Ответ (RU)

Ключевое слово `object` используется для создания синглтонов в Kotlin (через объявления `object` на уровне файла, внутри классов или объектов).

Важно отличать:
- объявление `object` (singleton-объект, один экземпляр на classloader);
- выражение `object` (анонимный объект, не является глобальным синглтоном).

**Основные характеристики объявлений `object`:**
- Создают один общий экземпляр для данного объявления в пределах соответствующего classloader
- Инициализация объявления `object` потокобезопасна по умолчанию
- Инициализируются лениво при первом обращении к объявлению `object`
- Не имеют публичного конструктора (экземпляр создаётся и управляется рантаймом целевой платформы)
- Могут содержать свойства, методы и `init`-блоки
- Могут реализовывать интерфейсы и наследовать классы

### Примеры Кода

**Базовый синглтон:**
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
    // Доступ напрямую без создания экземпляра
    println(AppSettings.theme)  // Light

    AppSettings.theme = "Dark"
    AppSettings.notificationsEnabled = false

    AppSettings.printSettings()
    // Theme: Dark
    // Language: English
    // Notifications: false
}
```

**Синглтон с инициализацией:**
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
    Logger.log("Application started")  // Logger initialized at <timestamp>
                                        // [x ms] Application started
    Logger.log("Processing data")       // [y ms] Processing data
}
```

**Синглтон, реализующий интерфейс:**
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

**Множественные точки доступа - один экземпляр:**
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

    // Один и тот же экземпляр везде
    val counter1 = Counter
    val counter2 = Counter
    println(counter1 === counter2)  // true
}
```

**Реальный пример: API-клиент:**
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

## Answer (EN)

The `object` keyword is used to create singleton objects in Kotlin (via `object` declarations at file level, inside classes, or inside other objects).

It's important to distinguish between:
- `object` declarations (singleton objects: one shared instance per classloader);
- `object` expressions (anonymous objects: not global singletons).

**Key characteristics of `object` declarations:**
- Create a single shared instance for the declaration within the corresponding classloader
- `Thread`-safe initialization by default for object declarations
- Lazily initialized on first access for object declarations
- No public constructor is needed or available (the instance is created and managed by the target platform runtime)
- Can contain properties, functions, and `init` blocks
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
    Logger.log("Application started")  // Logger initialized at <timestamp>
                                        // [x ms] Application started
    Logger.log("Processing data")       // [y ms] Processing data
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

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java-синглтонов?
- Когда вы бы использовали этот подход на практике?
- Какие распространенные ошибки стоит избегать?

## Follow-ups (EN)

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References (EN)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-coroutine-cancellation-cooperation--kotlin--medium]]
- [[q-associatewith-vs-associateby--kotlin--easy]]

## Related Questions (EN)

- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-coroutine-cancellation-cooperation--kotlin--medium]]
- [[q-associatewith-vs-associateby--kotlin--easy]]
