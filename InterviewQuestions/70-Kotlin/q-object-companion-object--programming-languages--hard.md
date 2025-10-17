---
id: "20251015082236031"
title: "Object Companion Object"
topic: kotlin
difficulty: hard
status: draft
created: 2025-10-15
tags: - programming-languages
---
# What is object / companion object?

# Question (EN)
> What is `object` / `companion object` in Kotlin? Explain their characteristics, differences, and advanced use cases.

# Вопрос (RU)
> Что такое `object` / `companion object` в Kotlin? Объясните их характеристики, различия и продвинутые случаи использования.

---

## Answer (EN)

`object` and `companion object` are used to implement various patterns and functionalities in Kotlin:

**object declaration:**
- Used to create a single instance of a class (Singleton pattern)
- Thread-safe by default
- Lazily initialized when first accessed
- Cannot have constructors (automatically instantiated)
- Can inherit from classes and implement interfaces

**companion object:**
- Declared inside a class
- Used to declare members accessible without creating an instance of the class
- Similar to static members in Java
- Can implement interfaces
- Can have extension functions
- Only one companion object per class
- Can be named (optional)

### Code Examples

**Object declaration (Singleton):**
```kotlin
// Simple singleton
object DatabaseConnection {
    private var isConnected = false

    fun connect() {
        if (!isConnected) {
            println("Connecting to database...")
            isConnected = true
        }
    }

    fun disconnect() {
        if (isConnected) {
            println("Disconnecting from database...")
            isConnected = false
        }
    }
}

// Usage
fun main() {
    DatabaseConnection.connect()     // Connecting to database...
    DatabaseConnection.disconnect()  // Disconnecting from database...
}
```

**Object with inheritance and interfaces:**
```kotlin
interface ClickListener {
    fun onClick()
}

open class BaseLogger {
    open fun log(message: String) {
        println("Log: $message")
    }
}

object Logger : BaseLogger(), ClickListener {
    override fun log(message: String) {
        println("[${System.currentTimeMillis()}] $message")
    }

    override fun onClick() {
        log("Button clicked")
    }
}

fun main() {
    Logger.log("Application started")
    Logger.onClick()
}
```

**Companion object (static-like members):**
```kotlin
class User(val id: Int, val name: String) {
    companion object {
        private var nextId = 1

        // Factory method
        fun create(name: String): User {
            return User(nextId++, name)
        }

        // Constants
        const val MIN_NAME_LENGTH = 3
        const val MAX_NAME_LENGTH = 50
    }

    init {
        require(name.length >= MIN_NAME_LENGTH) {
            "Name too short"
        }
    }
}

// Usage
fun main() {
    val user1 = User.create("Alice")
    val user2 = User.create("Bob")

    println("${user1.name} has ID ${user1.id}")  // Alice has ID 1
    println("${user2.name} has ID ${user2.id}")  // Bob has ID 2

    println("Min name length: ${User.MIN_NAME_LENGTH}")
}
```

**Named companion object:**
```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

// Can be called with or without name
fun main() {
    val obj1 = MyClass.create()           // Using companion object
    val obj2 = MyClass.Factory.create()   // Using companion object name
}
```

**Companion object with interface:**
```kotlin
interface JsonSerializer {
    fun toJson(): String
}

class Person(val name: String, val age: Int) {
    companion object : JsonSerializer {
        override fun toJson(): String {
            return """{"type": "Person"}"""
        }

        fun fromJson(json: String): Person {
            // Parse JSON and create Person
            return Person("Unknown", 0)
        }
    }

    fun toJson(): String {
        return """{"name": "$name", "age": $age}"""
    }
}

fun main() {
    val person = Person("Alice", 30)
    println(person.toJson())              // Instance method
    println(Person.toJson())               // Companion object method
    val newPerson = Person.fromJson("{}")  // Factory method
}
```

**Anonymous object (object expression):**
```kotlin
interface OnClickListener {
    fun onClick()
    fun onLongClick()
}

fun setClickListener(listener: OnClickListener) {
    listener.onClick()
}

fun main() {
    // Anonymous object (like anonymous inner class in Java)
    setClickListener(object : OnClickListener {
        override fun onClick() {
            println("Clicked!")
        }

        override fun onLongClick() {
            println("Long clicked!")
        }
    })
}
```

**Companion object extension:**
```kotlin
class Person(val name: String) {
    companion object {
        // Companion object members
    }
}

// Extension function for companion object
fun Person.Companion.createDefault(): Person {
    return Person("Default Name")
}

fun main() {
    val person = Person.createDefault()
    println(person.name)  // Default Name
}
```

---

## Ответ (RU)

`object` и `companion object` используются для реализации различных паттернов и функциональностей в Kotlin:

### object declaration (объявление object)

**Характеристики:**
- Используется для создания единственного экземпляра класса (паттерн Singleton)
- Потокобезопасен по умолчанию
- Ленивая инициализация при первом обращении
- Не может иметь конструкторов (создаётся автоматически)
- Может наследоваться от классов и реализовывать интерфейсы

**Пример простого singleton:**
```kotlin
object DatabaseConnection {
    private var isConnected = false

    fun connect() {
        if (!isConnected) {
            println("Подключение к БД...")
            isConnected = true
        }
    }

    fun disconnect() {
        if (isConnected) {
            println("Отключение от БД...")
            isConnected = false
        }
    }
}

// Использование
DatabaseConnection.connect()
DatabaseConnection.disconnect()
```

**Object с наследованием и интерфейсами:**
```kotlin
interface ClickListener {
    fun onClick()
}

open class BaseLogger {
    open fun log(message: String) {
        println("Log: $message")
    }
}

object Logger : BaseLogger(), ClickListener {
    override fun log(message: String) {
        println("[${System.currentTimeMillis()}] $message")
    }

    override fun onClick() {
        log("Нажата кнопка")
    }
}

// Использование
Logger.log("Приложение запущено")
Logger.onClick()
```

### companion object (объект-компаньон)

**Характеристики:**
- Объявляется внутри класса
- Используется для членов, доступных без создания экземпляра класса
- Аналог статических членов в Java
- Может реализовывать интерфейсы
- Может иметь extension-функции
- Только один companion object на класс
- Может иметь имя (опционально)

**Пример со статико-подобными членами:**
```kotlin
class User(val id: Int, val name: String) {
    companion object {
        private var nextId = 1

        // Фабричный метод
        fun create(name: String): User {
            return User(nextId++, name)
        }

        // Константы
        const val MIN_NAME_LENGTH = 3
        const val MAX_NAME_LENGTH = 50
    }

    init {
        require(name.length >= MIN_NAME_LENGTH) {
            "Имя слишком короткое"
        }
    }
}

// Использование
val user1 = User.create("Alice")
val user2 = User.create("Bob")

println("${user1.name} имеет ID ${user1.id}")  // Alice имеет ID 1
println("${user2.name} имеет ID ${user2.id}")  // Bob имеет ID 2
```

**Именованный companion object:**
```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

// Можно вызывать с именем или без
val obj1 = MyClass.create()           // Используя companion object
val obj2 = MyClass.Factory.create()   // Используя имя companion object
```

**Companion object с интерфейсом:**
```kotlin
interface JsonSerializer {
    fun toJson(): String
}

class Person(val name: String, val age: Int) {
    companion object : JsonSerializer {
        override fun toJson(): String {
            return """{"type": "Person"}"""
        }

        fun fromJson(json: String): Person {
            // Парсинг JSON и создание Person
            return Person("Неизвестно", 0)
        }
    }

    fun toJson(): String {
        return """{"name": "$name", "age": $age}"""
    }
}

// Использование
val person = Person("Alice", 30)
println(person.toJson())              // Метод экземпляра
println(Person.toJson())               // Метод companion object
val newPerson = Person.fromJson("{}")  // Фабричный метод
```

**Анонимный object (object expression):**
```kotlin
interface OnClickListener {
    fun onClick()
    fun onLongClick()
}

fun setClickListener(listener: OnClickListener) {
    listener.onClick()
}

// Анонимный объект (как anonymous inner class в Java)
setClickListener(object : OnClickListener {
    override fun onClick() {
        println("Нажато!")
    }

    override fun onLongClick() {
        println("Длинное нажатие!")
    }
})
```

**Расширение companion object:**
```kotlin
class Person(val name: String) {
    companion object {
        // Члены companion object
    }
}

// Extension-функция для companion object
fun Person.Companion.createDefault(): Person {
    return Person("Имя по умолчанию")
}

// Использование
val person = Person.createDefault()
println(person.name)  // Имя по умолчанию
```

### Ключевые различия

| Характеристика | object | companion object |
|----------------|--------|------------------|
| **Расположение** | Отдельная сущность | Внутри класса |
| **Доступ** | Через имя object | Через имя класса |
| **Назначение** | Singleton паттерн | "Статические" члены |
| **Количество** | Один на объявление | Один на класс (опционально) |
| **Конструктор** | Не может иметь | Не может иметь |
| **Наследование** | Может наследоваться | Может реализовывать интерфейсы |
| **Инициализация** | Ленивая | При загрузке класса |
| **Extension** | Нет | Да (можно расширять) |

### Когда использовать

**Используйте object когда:**
- Нужен единственный экземпляр (Singleton)
- Создаёте утилитный класс
- Реализуете глобальный менеджер
- Создаёте константы на уровне модуля

**Используйте companion object когда:**
- Нужны фабричные методы
- Создаёте константы внутри класса
- Нужны "статические" члены, связанные с классом
- Реализуете паттерн Factory

### Продвинутые примеры

**Singleton с инициализацией:**
```kotlin
object AppConfig {
    private val properties = mutableMapOf<String, String>()

    init {
        // Выполняется один раз при первом обращении
        println("Инициализация AppConfig")
        loadProperties()
    }

    private fun loadProperties() {
        properties["api_url"] = "https://api.example.com"
        properties["timeout"] = "30"
    }

    fun get(key: String): String? = properties[key]
}

// Первое обращение инициализирует объект
val apiUrl = AppConfig.get("api_url")
```

**Companion object для DSL:**
```kotlin
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    fun tag(name: String, content: String) {
        elements.add("<$name>$content</$name>")
    }

    fun build(): String = elements.joinToString("\n")

    companion object {
        fun html(init: HtmlBuilder.() -> Unit): String {
            val builder = HtmlBuilder()
            builder.init()
            return builder.build()
        }
    }
}

// Использование DSL
val page = HtmlBuilder.html {
    tag("h1", "Заголовок")
    tag("p", "Параграф")
}
```

### Краткий ответ

**object**: Создаёт потокобезопасный singleton с ленивой инициализацией. Используется для одиночных экземпляров, утилит, глобальных менеджеров. Может наследоваться и реализовывать интерфейсы.

**companion object**: Объявляет статико-подобные члены внутри класса, доступные через имя класса. Используется для фабричных методов, констант, "статических" функций. Может реализовывать интерфейсы и иметь extension-функции. Один на класс, может быть именованным.
