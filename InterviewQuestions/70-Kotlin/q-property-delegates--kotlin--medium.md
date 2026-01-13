---
id: kotlin-147
title: Property Delegates / Делегаты свойств
aliases:
- Delegates
- Property
- Property Delegates
- Делегаты свойств
topic: kotlin
subtopics:
- delegates
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
- q-coroutine-memory-leak-detection--kotlin--hard
- q-dispatchers-unconfined--kotlin--medium
created: 2025-10-15
updated: 2025-11-09
tags:
- delegates
- difficulty/medium
- kotlin
- properties
---
# Вопрос (RU)

> В чем особенность делегатов свойств в Kotlin?

# Question (EN)

> What is special about property delegates in Kotlin?

## Ответ (RU)

Делегаты свойств (Property Delegates) позволяют делегировать операции получения и установки значения свойства другому объекту, избегая дублирования кода и делая код модульным.

Свойство с `by` не обязано хранить значение само — оно делегирует доступ объекту-делегату, который реализует контракт через оператор-функции `getValue`/`setValue` (часто через интерфейсы `ReadOnlyProperty` / `ReadWriteProperty`).

### Основная Идея

Вместо того чтобы каждое свойство само хранило значение и реализовывало логику геттеров/сеттеров, оно делегирует эти операции отдельному объекту-делегату, который повторно используется в разных местах.

```kotlin
class Example {
    // Обычное свойство
    var normalProperty: String = ""

    // Делегированное свойство
    var delegatedProperty: String by Delegate()
}
```

### Встроенные Делегаты

#### 1. Lazy — Ленивая Инициализация

Значение вычисляется только при первом обращении.

```kotlin
class DatabaseConnection {
    // Инициализируется только при первом использовании
    val database: Database by lazy {
        println("Initializing database...")
        Database.connect("jdbc:mysql://localhost/mydb")
    }

    fun query() {
        database.execute("SELECT * FROM users")  // Инициализация произойдет здесь
    }
}

// Пример использования
val connection = DatabaseConnection()
// "Initializing database..." пока не выведено
connection.query()  // Теперь инициализация и вывод
connection.query()  // Повторной инициализации нет
```

#### 2. Observable — Наблюдение За Изменениями

```kotlin
class User {
    var name: String by Delegates.observable("Initial Name") { property, oldValue, newValue ->
        println("${property.name} changed from $oldValue to $newValue")
    }
}

// Использование
val user = User()
user.name = "Alice"  // name changed from Initial Name to Alice
user.name = "Bob"    // name changed from Alice to Bob
```

#### 3. Vetoable — Валидация Перед Изменением

```kotlin
class Product {
    var price: Int by Delegates.vetoable(0) { _, oldValue, newValue ->
        newValue >= 0  // Разрешаем изменение только если цена неотрицательная
    }
}

// Использование
val product = Product()
product.price = 100   // OK
product.price = -50   // Отклонено, значение остается 100
println(product.price)  // 100
```

#### 4. notNull — Отложенная Инициализация С Проверкой

```kotlin
class Configuration {
    var apiKey: String by Delegates.notNull()

    fun initialize() {
        apiKey = "your_api_key"  // Должно быть установлено до первого чтения
    }

    fun makeRequest() {
        // Если apiKey не был инициализирован до чтения, будет выброшен IllegalStateException
        println("Using API key: $apiKey")
    }
}
```

### Пользовательские Делегаты

```kotlin
// Делегат для логирования доступа к свойству
class LoggingDelegate<T>(private var value: T) : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Getting ${property.name} = $value")
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Setting ${property.name} from ${this.value} to $value")
        this.value = value
    }
}

// Использование
class ExampleLogging {
    var data: String by LoggingDelegate("initial")
}

val exampleLogging = ExampleLogging()
exampleLogging.data              // Getting data = initial
exampleLogging.data = "new value"  // Setting data from initial to new value
```

### Делегат Для SharedPreferences

```kotlin
class SharedPreferencesDelegate<T : Any>(
    private val prefs: SharedPreferences,
    private val key: String,
    private val defaultValue: T
) : ReadWriteProperty<Any?, T> {

    @Suppress("UNCHECKED_CAST")
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return when (defaultValue) {
            is Boolean -> prefs.getBoolean(key, defaultValue) as T
            is Int -> prefs.getInt(key, defaultValue) as T
            is Long -> prefs.getLong(key, defaultValue) as T
            is Float -> prefs.getFloat(key, defaultValue) as T
            is String -> prefs.getString(key, defaultValue) ?: defaultValue as T
            else -> throw IllegalArgumentException("Unsupported type")
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        prefs.edit {
            when (value) {
                is Boolean -> putBoolean(key, value)
                is Int -> putInt(key, value)
                is Long -> putLong(key, value)
                is Float -> putFloat(key, value)
                is String -> putString(key, value)
                else -> throw IllegalArgumentException("Unsupported type")
            }
        }
    }
}

// Функция-расширение для удобства
fun <T : Any> SharedPreferences.delegate(key: String, defaultValue: T) =
    SharedPreferencesDelegate(this, key, defaultValue)

// Использование
class Settings(context: Context) {
    private val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

    var username: String by prefs.delegate("username", "")
    var age: Int by prefs.delegate("age", 0)
    var isFirstLaunch: Boolean by prefs.delegate("first_launch", true)
}

val settings = Settings(context)
settings.username = "Alice"  // Автоматически сохраняется в SharedPreferences
println(settings.username)   // Автоматически читается из SharedPreferences
```

### Делегаты Для `Map`

```kotlin
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
    val email: String by map
}

// Использование
val userMap = mapOf(
    "name" to "Alice",
    "age" to 30,
    "email" to "alice@example.com"
)

val user = User(userMap)
println(user.name)   // Alice
println(user.age)    // 30
```

### Ключевые Особенности И Преимущества

#### 1. Изоляция Логики

Логика геттеров/сеттеров выносится в отдельный класс.

```kotlin
class ValidationDelegate(private var value: String) : ReadWriteProperty<Any?, String> {
    override fun getValue(thisRef: Any?, property: KProperty<*>) = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        require(value.isNotBlank()) { "Value cannot be blank" }
        require(value.length <= 100) { "Value too long" }
        this.value = value
    }
}

class Form {
    var email: String by ValidationDelegate("")
    var username: String by ValidationDelegate("")
}
```

#### 2. Переиспользование Кода

Один делегат можно использовать для множества свойств.

```kotlin
class RangeDelegate(private var value: Int, private val range: IntRange) :
    ReadWriteProperty<Any?, Int> {

    override fun getValue(thisRef: Any?, property: KProperty<*>) = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: Int) {
        require(value in range) { "$value is not in range $range" }
        this.value = value
    }
}

class GameCharacter {
    var health: Int by RangeDelegate(100, 0..100)
    var mana: Int by RangeDelegate(50, 0..100)
    var stamina: Int by RangeDelegate(75, 0..100)
}
```

#### 3. Расширяемость

Легко создавать новые делегаты под конкретные сценарии: кеширование, логирование, доступ к конфигурации, валидацию и т. д.

#### 4. Поддержка На Уровне Языка

Kotlin предоставляет синтаксис `by` и механизм делегирования, что делает делегаты свойств удобным и безопасным инструментом.

Итог: делегаты свойств позволяют вынести повторяющуюся логику работы со свойствами в переиспользуемые компоненты, делая код чище и декларативнее.

## Answer (EN)

Property delegates in Kotlin allow you to delegate the logic of getting and setting a property’s value to another object, avoiding duplication and making code more modular.

A property with `by` does not have to store its own value — it delegates access to a delegate object that implements the contract via `getValue`/`setValue` operator functions (often through `ReadOnlyProperty` / `ReadWriteProperty`).

### Main Idea

Instead of each property storing data or performing operations independently, it can delegate these tasks to another object that implements the required delegation contract.

```kotlin
class Example {
    // Normal property
    var normalProperty: String = ""

    // Delegated property
    var delegatedProperty: String by Delegate()
}
```

### Standard Delegates

#### 1. Lazy - Lazy Initialization

Value is computed only on first access.

```kotlin
class DatabaseConnection {
    // Initialized only on first use
    val database: Database by lazy {
        println("Initializing database...")
        Database.connect("jdbc:mysql://localhost/mydb")
    }

    fun query() {
        database.execute("SELECT * FROM users")  // Initialization happens here
    }
}

// Usage example
val connection = DatabaseConnection()
// "Initializing database..." is not printed yet
connection.query()  // Initialization and print happen here
connection.query()  // No re-initialization
```

#### 2. Observable - Change Observation

```kotlin
class User {
    var name: String by Delegates.observable("Initial Name") { property, oldValue, newValue ->
        println("${property.name} changed from $oldValue to $newValue")
    }
}

// Usage
val user = User()
user.name = "Alice"  // name changed from Initial Name to Alice
user.name = "Bob"    // name changed from Alice to Bob
```

#### 3. Vetoable - Validation before Change

```kotlin
class Product {
    var price: Int by Delegates.vetoable(0) { _, oldValue, newValue ->
        newValue >= 0  // Allow change only if non-negative
    }
}

// Usage
val product = Product()
product.price = 100   // OK
product.price = -50   // Rejected, value stays 100
println(product.price)  // 100
```

#### 4. notNull - Late Initialization with Check

```kotlin
class Configuration {
    var apiKey: String by Delegates.notNull()

    fun initialize() {
        apiKey = "your_api_key"  // Must be set before first read
    }

    fun makeRequest() {
        // If apiKey is read before initialization, IllegalStateException will be thrown
        println("Using API key: $apiKey")
    }
}
```

### Custom Delegates

```kotlin
class LoggingDelegate<T>(private var value: T) : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Getting ${property.name} = $value")
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Setting ${property.name} from ${this.value} to $value")
        this.value = value
    }
}

class ExampleLogging {
    var data: String by LoggingDelegate("initial")
}

val exampleLogging = ExampleLogging()
exampleLogging.data              // Getting data = initial
exampleLogging.data = "new value"  // Setting data from initial to new value
```

### Delegate for SharedPreferences

```kotlin
class SharedPreferencesDelegate<T : Any>(
    private val prefs: SharedPreferences,
    private val key: String,
    private val defaultValue: T
) : ReadWriteProperty<Any?, T> {

    @Suppress("UNCHECKED_CAST")
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return when (defaultValue) {
            is Boolean -> prefs.getBoolean(key, defaultValue) as T
            is Int -> prefs.getInt(key, defaultValue) as T
            is Long -> prefs.getLong(key, defaultValue) as T
            is Float -> prefs.getFloat(key, defaultValue) as T
            is String -> prefs.getString(key, defaultValue) ?: defaultValue as T
            else -> throw IllegalArgumentException("Unsupported type")
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        prefs.edit {
            when (value) {
                is Boolean -> putBoolean(key, value)
                is Int -> putInt(key, value)
                is Long -> putLong(key, value)
                is Float -> putFloat(key, value)
                is String -> putString(key, value)
                else -> throw IllegalArgumentException("Unsupported type")
            }
        }
    }
}

fun <T : Any> SharedPreferences.delegate(key: String, defaultValue: T) =
    SharedPreferencesDelegate(this, key, defaultValue)
```

### Map Delegates

```kotlin
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
    val email: String by map
}

val userMap = mapOf(
    "name" to "Alice",
    "age" to 30,
    "email" to "alice@example.com"
)

val user = User(userMap)
println(user.name)   // Alice
println(user.age)    // 30
```

### Key Features and Benefits

1. Logic isolation: move getter/setter logic into dedicated classes.
2. Code reusability: one delegate can be used for many properties.
3. Extensibility: easy to create delegates for caching, logging, config access, validation, etc.
4. Built-in language support: `by` syntax and delegation mechanism make this concise and safe.

In summary, property delegates allow you to extract repetitive property-related logic into reusable components, making code cleaner and more declarative.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия делегатов свойств в Kotlin от подходов в Java?
- Когда на практике стоит использовать делегаты свойств?
- Какие распространенные ошибки и подводные камни при использовании делегатов стоит учитывать?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-dispatchers-unconfined--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-dispatchers-unconfined--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
