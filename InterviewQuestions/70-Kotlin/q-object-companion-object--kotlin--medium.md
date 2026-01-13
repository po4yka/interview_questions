---
id: kotlin-143
title: Object Companion Object / Object и Companion Object
aliases:
- Companion
- Companion Object
- Object
- Object Keyword
- Singleton
topic: kotlin
subtopics:
- classes
- singleton
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-coroutinecontext-composition--kotlin--hard
- q-flow-backpressure--kotlin--hard
created: 2025-10-15
updated: 2025-11-09
tags:
- classes
- companion-object
- difficulty/medium
- kotlin
- object-keyword
- singleton
---
# Что Такое Object / Companion Object?

# Вопрос (RU)
> Что такое `object` и `companion object` в Kotlin? В чём их различия и когда их использовать?

---

# Question (EN)
> What are `object` and `companion object` in Kotlin? What are their differences and use cases?

## Ответ (RU)

`object` и `companion object` используются для объявления объектов, доступных без явного создания экземпляра обычного класса: для реализации паттерна одиночка (singleton), объявления членов, аналогичных статическим по способу доступа, создания объектов-утилит, фабрик и объектных выражений.

### Object - Одиночка (Singleton)

`object`-объявление создаёт одиночный экземпляр (singleton) для данного объявления в области его видимости.

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
- Для каждого `object`-объявления существует ровно один экземпляр этого объекта
- Инициализируется при первом обращении (lazy initialization) инициализационным кодом
- Инициализация потокобезопасна по умолчанию
- Не может иметь конструктор с параметрами

```kotlin
// Неправильно
object Config(val apiKey: String)  // Ошибка компиляции!

// Правильно
object Config {
    const val API_KEY = "your_api_key"
}
```

(Дополнительно: существуют object-выражения и локальные object-объявления, которые также используют ключевое слово `object`, но не являются глобальными синглтонами — они создаются там, где объявлены/используются.)

### Companion Object - Статические Члены

Используется внутри класса и служит для объявления членов, доступных без создания экземпляра этого класса (по способу доступа аналогично статическим членам в Java), при этом сам `companion object` является полноценным объектом (может реализовывать интерфейсы, иметь своё состояние и передаваться как значение).

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

### Основные Различия

| Aspect | object | companion object |
|--------|--------|------------------|
| **Расположение** | Отдельное объявление (top-level, локальное, вложенное) | Внутри класса, объявлено как `companion object` |
| **Доступ** | Через имя object | Через имя класса (или имя companion, если указано) |
| **Назначение** | Singleton для данного объявления, утилиты, object-выражения | "Статические" по способу доступа члены и фабрики, связанные с классом |
| **Количество** | Один экземпляр на каждое `object`-объявление | Не более одного `companion object` на класс (необязателен) |

### Примеры Использования

#### 1. Factory Pattern С Companion Object

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

#### 2. Константы В Companion Object

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

#### 3. Object Для Утилит

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

#### 4. Anonymous Objects

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

### Расширение Companion Object

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

## Answer (EN)

`object` and `companion object` are Kotlin features for declaring objects accessible without explicitly instantiating a regular class: used for singletons, static-like access to members, utilities, factories, and object expressions.

### Object - Singleton

`object` declarations create a single instance (a singleton) for that declaration within its scope.

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

// Usage
DatabaseManager.executeQuery("SELECT * FROM users")
DatabaseManager.close()
```

Key properties of `object`:
- Exactly one instance per `object` declaration
- Lazily initialized on first access with its initialization code
- Initialization is thread-safe by default
- Cannot have a constructor with parameters

```kotlin
// Incorrect
object Config(val apiKey: String)  // Compilation error!

// Correct
object Config {
    const val API_KEY = "your_api_key"
}
```

Note: there are also object expressions and local object declarations that use the `object` keyword but are not global singletons — they are created where they are declared/used.

### Companion Object - Static-like Members

A `companion object` is declared inside a class and provides members that can be accessed without creating an instance of that class (similar in access style to `static` members in Java). However, the companion itself is a real object (it can implement interfaces, hold state, and be passed around as a value).

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

// Usage
val user1 = User.create("Alice")
val user2 = User.create("Bob")
println(User.MAX_NAME_LENGTH)  // 50
```

### Key Differences

| Aspect | object | companion object |
|--------|--------|------------------|
| Location | Separate declaration (top-level, local, nested) | Inside a class, declared as `companion object` |
| Access | Via the object name | Via the class name (or companion name if specified) |
| Purpose | Singleton for that declaration, utilities, object expressions | Static-like access to members and factories associated with the class |
| Count | One instance per `object` declaration | At most one `companion object` per class (optional) |

### Usage Examples

#### 1. Factory Pattern with Companion Object

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

// Usage
val localDb = DatabaseConnection.createLocalConnection()
val remoteDb = DatabaseConnection.createRemoteConnection("192.168.1.1")
```

#### 2. Constants in Companion Object

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

// Usage
val timeout = HttpClient.DEFAULT_TIMEOUT
val client = HttpClient.create()
```

#### 3. Object for Utilities

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

// Usage
val fact = MathUtils.factorial(5)  // 120
val prime = MathUtils.isPrime(17)  // true
```

#### 4. Anonymous Objects

```kotlin
// One-off interface implementations
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View?) {
        println("Button clicked")
    }
})

// Or shorter with SAM conversion
button.setOnClickListener { println("Button clicked") }
```

### Extending a Companion Object

```kotlin
class MyClass {
    companion object {
        fun foo() = "foo"
    }
}

// Extension on companion object
fun MyClass.Companion.bar() = "bar"

// Usage
MyClass.foo()  // "foo"
MyClass.bar()  // "bar"
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-kotlin-java-type-differences--kotlin--medium]]
- [[q-coroutinecontext-composition--kotlin--hard]]
- [[q-flow-backpressure--kotlin--hard]]
