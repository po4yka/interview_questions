---
anki_cards:
- slug: q-kotlin-singleton-creation--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-singleton-creation--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: lang-028
title: "Kotlin Singleton Creation / Создание синглтона в Kotlin"
aliases: [Kotlin Singleton Creation, Создание синглтона в Kotlin]
topic: kotlin
subtopics: [c-kotlin, c-kotlin-features]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-coroutine-job-lifecycle--kotlin--medium, q-statein-sharein-flow--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [design-patterns, difficulty/easy, singleton]
---\
# Вопрос (RU)
> Как создать singleton в Kotlin?

# Question (EN)
> How to create a singleton in Kotlin?

## Ответ (RU)

В Kotlin можно создать singleton, используя object-декларацию. Это самый простой и идиоматичный способ реализации паттерна Singleton в Kotlin. См. также [[c-kotlin]].

**Синтаксис:**
```kotlin
object MySingleton {
    // свойства и методы
}
```

**Ключевые особенности (для JVM):**
- Потокобезопасная инициализация по умолчанию (object создаётся один раз, без явной синхронизации)
- Ленивая инициализация при первом обращении
- Существует только один экземпляр на всё приложение
- Не может иметь конструкторы
- Может иметь свойства, методы и блоки init
- Может наследоваться от классов и реализовывать интерфейсы

Важно: потокобезопасна именно инициализация объекта. Если singleton хранит изменяемое состояние, операции над ним сами по себе не становятся потокобезопасными — при работе из нескольких потоков потребуется синхронизация или атомарные типы.

### Примеры

**Базовый singleton:**
```kotlin
object AppConfig {
    var apiUrl = "https://api.example.com"
    var timeout = 30

    fun printConfig() {
        println("API URL: $apiUrl")
    }
}

// Прямой доступ без создания экземпляра
AppConfig.apiUrl = "https://api.production.com"
AppConfig.printConfig()

// Всегда один и тот же экземпляр
val config1 = AppConfig
val config2 = AppConfig
println(config1 === config2)  // true
```

**С инициализацией:**
```kotlin
object DatabaseManager {
    private val connections = mutableListOf<String>()

    init {
        println("DatabaseManager initialized")
        // Выполнение инициализации
        connections.add("Default Connection")
    }

    fun addConnection(name: String) {
        connections.add(name)
    }

    fun getConnections(): List<String> = connections
}
```

**Реализующий интерфейс:**
```kotlin
interface Logger {
    fun log(message: String)
}

object ConsoleLogger : Logger {
    override fun log(message: String) {
        println("[LOG] $message")
    }
}

ConsoleLogger.log("Application started")
```

**Singleton с полями и методами для сессии пользователя:**
```kotlin
object UserSession {
    var userId: String? = null
    var username: String? = null
    var isLoggedIn: Boolean = false

    fun login(id: String, name: String) {
        userId = id
        username = name
        isLoggedIn = true
        println("User $name logged in")
    }

    fun logout() {
        println("User $username logged out")
        userId = null
        username = null
        isLoggedIn = false
    }

    fun getCurrentUser(): String? = username
}
```

**Альтернатива: через companion object (для ленивой инициализации с параметрами):**
```kotlin
class DatabaseConnection private constructor(val url: String) {
    companion object {
        @Volatile
        private var instance: DatabaseConnection? = null

        fun getInstance(url: String): DatabaseConnection {
            // Первый вызов определяет конфигурацию singleton; последующие url игнорируются
            return instance ?: synchronized(this) {
                instance ?: DatabaseConnection(url).also { instance = it }
            }
        }
    }

    fun connect() {
        println("Connecting to $url")
    }
}

fun main() {
    val db1 = DatabaseConnection.getInstance("jdbc:mysql://localhost:3306")
    val db2 = DatabaseConnection.getInstance("jdbc:mysql://localhost:3306")

    println(db1 === db2)  // true
    db1.connect()
}
```

**Заметка о потокобезопасности операций:**
```kotlin
object Counter {
    private val lock = Any()
    private var count = 0

    fun increment() {
        synchronized(lock) {
            count++
        }
    }

    fun getCount(): Int = synchronized(lock) { count }
}

fun main() {
    val threads = List(10) {
        Thread {
            repeat(1000) {
                Counter.increment()
            }
        }
    }

    threads.forEach { it.start() }
    threads.forEach { it.join() }

    println("Final count: ${Counter.getCount()}")  // 10000
}
```

## Answer (EN)

In Kotlin, you can create a singleton using an object declaration. This is the simplest and most idiomatic way to implement the Singleton pattern in Kotlin.

**Syntax:**
```kotlin
object MySingleton {
    // properties and methods
}
```

**Key features (on the JVM):**
- `Thread`-safe initialization by default (the object instance is created once without explicit synchronization)
- Lazily initialized when first accessed
- Only one instance exists throughout the application
- Cannot have constructors
- Can have properties, methods, and init blocks
- Can inherit from classes and implement interfaces

Important: what is guaranteed to be thread-safe is the object initialization itself. If the singleton holds mutable state, operations on that state are not automatically thread-safe; you still need synchronization or atomic primitives when accessing it from multiple threads.

### Code Examples

**Basic singleton:**
```kotlin
object AppConfig {
    var apiUrl = "https://api.example.com"
    var timeout = 30

    fun printConfig() {
        println("API URL: $apiUrl")
    }
}

// Direct access without instantiation
AppConfig.apiUrl = "https://api.production.com"
AppConfig.printConfig()

// Always the same instance
val config1 = AppConfig
val config2 = AppConfig
println(config1 === config2)  // true
```

**Singleton with initialization:**
```kotlin
object DatabaseManager {
    private val connections = mutableListOf<String>()

    init {
        println("DatabaseManager initialized")
        // Perform initialization
        connections.add("Default Connection")
    }

    fun addConnection(name: String) {
        connections.add(name)
    }

    fun getConnections(): List<String> = connections
}
```

**Singleton implementing interface:**
```kotlin
interface Logger {
    fun log(message: String)
}

object ConsoleLogger : Logger {
    override fun log(message: String) {
        println("[LOG] $message")
    }
}

ConsoleLogger.log("Application started")
```

**Singleton with properties and methods:**
```kotlin
object UserSession {
    var userId: String? = null
    var username: String? = null
    var isLoggedIn: Boolean = false

    fun login(id: String, name: String) {
        userId = id
        username = name
        isLoggedIn = true
        println("User $name logged in")
    }

    fun logout() {
        println("User $username logged out")
        userId = null
        username = null
        isLoggedIn = false
    }

    fun getCurrentUser(): String? = username
}
```

**Alternative: Singleton using companion object (for lazy initialization with parameters):**
```kotlin
class DatabaseConnection private constructor(val url: String) {
    companion object {
        @Volatile
        private var instance: DatabaseConnection? = null

        fun getInstance(url: String): DatabaseConnection {
            // The first call defines the singleton configuration; subsequent url values are ignored
            return instance ?: synchronized(this) {
                instance ?: DatabaseConnection(url).also { instance = it }
            }
        }
    }

    fun connect() {
        println("Connecting to $url")
    }
}

fun main() {
    val db1 = DatabaseConnection.getInstance("jdbc:mysql://localhost:3306")
    val db2 = DatabaseConnection.getInstance("jdbc:mysql://localhost:3306")

    println(db1 === db2)  // true
    db1.connect()
}
```

**Note on thread safety of operations:**
```kotlin
object Counter {
    private val lock = Any()
    private var count = 0

    fun increment() {
        synchronized(lock) {
            count++
        }
    }

    fun getCount(): Int = synchronized(lock) { count }
}

fun main() {
    val threads = List(10) {
        Thread {
            repeat(1000) {
                Counter.increment()
            }
        }
    }

    threads.forEach { it.start() }
    threads.forEach { it.join() }

    println("Final count: ${Counter.getCount()}")  // 10000
}
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали такой singleton на практике?
- Каковы распространенные ошибки и подводные камни при использовании singleton?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-suspend-functions-basics--kotlin--easy]]
- [[q-statein-sharein-flow--kotlin--medium]]

## Related Questions

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-suspend-functions-basics--kotlin--easy]]
- [[q-statein-sharein-flow--kotlin--medium]]
