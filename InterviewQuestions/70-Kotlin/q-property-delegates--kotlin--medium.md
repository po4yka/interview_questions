---
tags:
  - kotlin
  - delegates
  - properties
difficulty: medium
status: reviewed
---

# В чем особенность делегатов свойств

**English**: What is special about property delegates in Kotlin?

## Answer

Делегаты свойств (Property Delegates) — это мощная функциональность Kotlin, позволяющая делегировать выполнение операций получения и установки значения свойства другому объекту.

### Основная идея

Вместо того чтобы каждое свойство самостоятельно хранило данные или выполняло операции, оно может перенаправить эти задачи делегату.

```kotlin
class Example {
    // Обычное свойство
    var normalProperty: String = ""

    // Делегированное свойство
    var delegatedProperty: String by Delegate()
}
```

### Стандартные делегаты

#### 1. lazy - ленивая инициализация

Значение вычисляется только при первом обращении.

```kotlin
class DatabaseConnection {
    // Инициализируется только при первом использовании
    val database: Database by lazy {
        println("Initializing database...")
        Database.connect("jdbc:mysql://localhost/mydb")
    }

    fun query() {
        database.execute("SELECT * FROM users")  // Здесь происходит инициализация
    }
}

// Пример использования
val connection = DatabaseConnection()
// "Initializing database..." ещё не выведено
connection.query()  // Теперь выведется "Initializing database..."
connection.query()  // База уже инициализирована, повторно не создаётся
```

#### 2. observable - наблюдение за изменениями

```kotlin
class User {
    var name: String by Delegates.observable("Initial Name") { property, oldValue, newValue ->
        println("${property.name} changed from $oldValue to $newValue")
    }
}

// Использование
val user = User()
user.name = "Alice"  // Выведет: name changed from Initial Name to Alice
user.name = "Bob"    // Выведет: name changed from Alice to Bob
```

#### 3. vetoable - валидация перед изменением

```kotlin
class Product {
    var price: Int by Delegates.vetoable(0) { _, oldValue, newValue ->
        newValue >= 0  // Разрешить изменение только если новая цена >= 0
    }
}

// Использование
val product = Product()
product.price = 100   // OK, цена установлена
product.price = -50   // Отклонено, цена остаётся 100
println(product.price)  // 100
```

#### 4. notNull - поздняя инициализация с проверкой

```kotlin
class Configuration {
    var apiKey: String by Delegates.notNull()

    fun initialize() {
        apiKey = "your_api_key"  // Должно быть установлено до первого чтения
    }

    fun makeRequest() {
        println("Using API key: $apiKey")  // IllegalStateException если не инициализировано
    }
}
```

### Кастомные делегаты

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
class Example {
    var data: String by LoggingDelegate("initial")
}

val example = Example()
example.data  // Getting data = initial
example.data = "new value"  // Setting data from initial to new value
```

### Делегат для SharedPreferences

```kotlin
class SharedPreferencesDelegate<T>(
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
            is String -> prefs.getString(key, defaultValue) as T
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
            }
        }
    }
}

// Extension функция для удобства
fun <T> SharedPreferences.delegate(key: String, defaultValue: T) =
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

### Map делегаты

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

### Основные особенности и преимущества

#### 1. Изоляция логики

Логика получения/установки значения вынесена в отдельный класс.

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

#### 2. Повторное использование кода

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

Легко создавать новые делегаты для специфичных нужд.

#### 4. Встроенная поддержка в языке

Kotlin предоставляет синтаксис `by` для работы с делегатами.

**English**: Property delegates allow delegating getter/setter operations to another object, avoiding code duplication and making code modular. Built-in delegates include `lazy` (lazy initialization), `observable` (change observation), `vetoable` (validation), and `notNull`. Custom delegates implement `ReadWriteProperty` interface, enabling reusable logic for SharedPreferences, validation, logging, etc.
