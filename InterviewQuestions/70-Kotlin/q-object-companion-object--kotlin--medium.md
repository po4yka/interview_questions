---
tags:
  - kotlin
  - object-oriented
  - singleton
difficulty: medium
status: draft
---

# Что такое object / companion object?

# Question (EN)
> What are `object` and `companion object` in Kotlin? What are their differences and use cases?

# Вопрос (RU)
> Что такое `object` и `companion object` в Kotlin? В чём их различия и когда их использовать?

---

## Answer (EN)

`object` and `companion object` are Kotlin features for implementing various patterns without explicit instantiation:

**object**: Creates a singleton (single instance). Accessed by name. Thread-safe lazy initialization. Use for: singletons, utility classes, constants.

**companion object**: Declares static-like members inside a class. Accessed via class name. Use for: factory methods, constants, static utility functions within a class context.

**Key differences:**
- **object**: Standalone entity, accessed by its own name
- **companion object**: Lives inside a class, accessed via class name
- **object**: One per declaration
- **companion object**: One per class (optional)

**Example:**
```kotlin
// object - singleton
object DatabaseManager {
    fun executeQuery(sql: String) { }
}
DatabaseManager.executeQuery("SELECT *")

// companion object - factory pattern
class User private constructor(val name: String) {
    companion object {
        fun create(name: String) = User(name)
    }
}
val user = User.create("Alice")
```

---

## Ответ (RU)

`object` и `companion object` используются для реализации различных паттернов и функциональностей, включая паттерн одиночка (singleton), объявление статических членов и функций, а также для реализации объектов без необходимости явного создания экземпляра класса.

### object - одиночка (Singleton)

Используется для создания одиночного экземпляра класса, то есть реализации паттерна Singleton.

```kotlin
object DatabaseManager {
    private val connection = createConnection()

    fun executeQuery(sql: String): Result {
        return connection.execute(sql)
    }

    fun close() {
        connection.close()
    }
}

// Использование
DatabaseManager.executeQuery("SELECT * FROM users")
DatabaseManager.close()
```

**Особенности object**:
- Создаётся единственный экземпляр при первом обращении (lazy initialization)
- Потокобезопасен по умолчанию
- Не может иметь конструктор с параметрами

```kotlin
// Неправильно
object Config(val apiKey: String)  // Ошибка компиляции!

// Правильно
object Config {
    const val API_KEY = "your_api_key"
}
```

### companion object - статические члены

Используется внутри класса и служит для объявления членов класса, доступных без создания экземпляра этого класса (аналогично статическим членам в Java).

```kotlin
class User private constructor(val id: Int, val name: String) {
    companion object {
        private var nextId = 1

        fun create(name: String): User {
            return User(nextId++, name)
        }

        const val MAX_NAME_LENGTH = 50
    }
}

// Использование
val user1 = User.create("Alice")
val user2 = User.create("Bob")
println(User.MAX_NAME_LENGTH)  // 50
```

### Основные различия

| Aspect | object | companion object |
|--------|--------|------------------|
| **Расположение** | Отдельная сущность | Внутри класса |
| **Доступ** | Через имя object | Через имя класса |
| **Назначение** | Singleton | "Статические" члены |
| **Количество** | Один на файл | Один на класс |

### Примеры использования

#### 1. Factory Pattern с companion object

```kotlin
class DatabaseConnection private constructor(
    private val host: String,
    private val port: Int
) {
    companion object Factory {
        fun createLocalConnection(): DatabaseConnection {
            return DatabaseConnection("localhost", 5432)
        }

        fun createRemoteConnection(host: String): DatabaseConnection {
            return DatabaseConnection(host, 5432)
        }
    }

    fun connect() {
        println("Connecting to $host:$port")
    }
}

// Использование
val localDb = DatabaseConnection.createLocalConnection()
val remoteDb = DatabaseConnection.createRemoteConnection("192.168.1.1")
```

#### 2. Константы в companion object

```kotlin
class HttpClient {
    companion object {
        const val DEFAULT_TIMEOUT = 30_000
        const val MAX_RETRIES = 3
        private const val USER_AGENT = "MyApp/1.0"

        fun create(): HttpClient {
            return HttpClient()
        }
    }
}

// Использование
val timeout = HttpClient.DEFAULT_TIMEOUT
val client = HttpClient.create()
```

#### 3. object для утилит

```kotlin
object MathUtils {
    fun factorial(n: Int): Long {
        return if (n <= 1) 1 else n * factorial(n - 1)
    }

    fun isPrime(n: Int): Boolean {
        if (n < 2) return false
        for (i in 2..Math.sqrt(n.toDouble()).toInt()) {
            if (n % i == 0) return false
        }
        return true
    }
}

// Использование
val fact = MathUtils.factorial(5)  // 120
val prime = MathUtils.isPrime(17)  // true
```

#### 4. Anonymous objects

```kotlin
// Для одноразовых реализаций интерфейсов
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View?) {
        println("Button clicked")
    }
})

// Или короче с SAM conversion
button.setOnClickListener { println("Button clicked") }
```

### Расширение companion object

```kotlin
class MyClass {
    companion object {
        fun foo() = "foo"
    }
}

// Расширение companion object
fun MyClass.Companion.bar() = "bar"

// Использование
MyClass.foo()  // "foo" - обычный метод
MyClass.bar()  // "bar" - расширение
```
