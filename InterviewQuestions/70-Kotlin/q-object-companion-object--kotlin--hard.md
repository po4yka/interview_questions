---
---
---\
id: kotlin-159
title: "Object Companion Object / Object и Companion Object Advanced"
aliases: [Advanced, Advanced Object Patterns, Companion Object, Object]
topic: kotlin
subtopics: [classes, singleton]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-equals-hashcode-purpose--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [classes, companion-object, difficulty/hard, kotlin, object-keyword, singleton]
---\
# Вопрос (RU)
> Что такое `object` / `companion object` в Kotlin? Объясните их характеристики, различия и продвинутые случаи использования.

---

# Question (EN)
> What is `object` / `companion object` in Kotlin? Explain their characteristics, differences, and advanced use cases.

## Ответ (RU)

`object` и `companion object` используются для реализации различных паттернов и функциональностей в Kotlin (см. также [[c-kotlin]]):

### Object Declaration (объявление object)

**Характеристики:**
- Используется для создания единственного экземпляра класса (паттерн Singleton)
- Инициализация потокобезопасна по умолчанию (гарантируется корректная инициализация единственного экземпляра), но внутренняя изменяемая логика не становится автоматически потокобезопасной
- Ленивая инициализация при первом обращении к объекту
- Не может иметь конструкторов (экземпляр создаётся автоматически компилятором)
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

### Companion Object (объект-компаньон)

**Характеристики:**
- Объявляется внутри класса
- Используется для членов, доступных без создания экземпляра класса
- Аналог статических членов в Java (но реализован через обычный объект, а не ключевое слово `static`)
- Может реализовывать интерфейсы
- Может иметь extension-функции
- Только один companion object на класс
- Может иметь имя (опционально)
- Является единственным экземпляром, связанным с классом, и инициализируется при первом обращении к ним (или к содержащему классу); инициализация потокобезопасна

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
println(person.toJson())               // Метод экземпляра
println(Person.toJson())               // Метод companion object
val newPerson = Person.fromJson("{}"); // Фабричный метод
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

// Анонимный объект (как anonymous inner class в Java), также использует ключевое слово `object`
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

### Ключевые Различия

| Характеристика | object | companion object |
|----------------|--------|------------------|
| **Расположение** | Отдельная сущность | Внутри класса |
| **Доступ** | Через имя object | Через имя класса |
| **Назначение** | Singleton-паттерн, утилиты, объекты как значения | "Статические" члены, связанные с классом |
| **Количество** | Один экземпляр на объявление | Не более одного на класс (опционально) |
| **Конструктор** | Не может иметь | Не может иметь |
| **Наследование** | Может наследоваться и реализовывать интерфейсы | Может реализовывать интерфейсы |
| **Инициализация** | Ленивая при первом обращении, инициализация потокобезопасна | Ленивая при первом обращении к companion object или его членам, инициализация потокобезопасна |
| **Extension** | Можно объявлять extension-функции/свойства для конкретного `object` по его имени | Можно объявлять extension-функции/свойства для `Companion` (или именованного companion object) |

### Когда Использовать

**Используйте `object` когда:**
- Нужен единственный экземпляр (Singleton)
- Создаёте утилитный класс
- Реализуете глобальный менеджер
- Создаёте константы на уровне модуля / верхнего уровня (или используете `object` как контейнер)

**Используйте `companion object` когда:**
- Нужны фабричные методы
- Создаёте константы внутри класса
- Нужны "статические" члены, связанные с классом
- Реализуете паттерн Factory

### Продвинутые Примеры

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

### Краткий Ответ

**`object`**: Создаёт singleton с ленивой, потокобезопасной инициализацией. Используется для одиночных экземпляров, утилит, глобальных менеджеров. Может наследоваться и реализовывать интерфейсы. Потокобезопасность касается инициализации экземпляра; синхронизация изменяемого состояния требует отдельного управления.

**`companion object`**: Объявляет статико-подобные члены внутри класса, доступные через имя класса. Используется для фабричных методов, констант, "статических" функций. Может реализовывать интерфейсы и иметь extension-функции. Один на класс, может быть именованным. Инициализируется лениво и потокобезопасно при первом обращении.

## Answer (EN)

`object` and `companion object` are used to implement various patterns and functionalities in Kotlin (see also [[c-kotlin]]):

### Object Declaration

**Characteristics:**
- Used to create a single instance of a class (Singleton pattern)
- Initialization is thread-safe by default (the single instance is initialized safely), but mutable internal logic/state is not automatically thread-safe
- Lazily initialized when first accessed
- Cannot have constructors (the instance is created automatically by the compiler)
- Can inherit from classes and implement interfaces

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
DatabaseConnection.connect()
DatabaseConnection.disconnect()
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

// Usage
Logger.log("Application started")
Logger.onClick()
```

### Companion Object

**Characteristics:**
- Declared inside a class
- Used for members accessible without creating an instance of the class
- Similar to static members in Java (but implemented as a regular object, not via `static` keyword)
- Can implement interfaces
- Can have extension functions
- Only one companion object per class
- Can be named (optional)
- Acts as a single instance associated with the class; initialized on first access to it (or to the enclosing class); initialization is thread-safe

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
val user1 = User.create("Alice")
val user2 = User.create("Bob")

println("${user1.name} has ID ${user1.id}")  // Alice has ID 1
println("${user2.name} has ID ${user2.id}")  // Bob has ID 2
println("Min name length: ${User.MIN_NAME_LENGTH}")
```

**Named companion object:**
```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

// Can be called with or without name
val obj1 = MyClass.create()           // Using companion object
val obj2 = MyClass.Factory.create()   // Using companion object name
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
    println(person.toJson())                // Instance method
    println(Person.toJson())                // Companion object method
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

// Anonymous object (like anonymous inner class in Java), also based on `object` keyword
setClickListener(object : OnClickListener {
    override fun onClick() {
        println("Clicked!")
    }

    override fun onLongClick() {
        println("Long clicked!")
    }
})
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

val person = Person.createDefault()
println(person.name)  // Default Name
```

### Key Differences

| Aspect | `object` | `companion object` |
|--------|---------|--------------------|
| Location | Top-level or nested singleton declaration | Inside a class |
| Access | Via the object name | Via the class name |
| Purpose | Singleton pattern, utilities, objects as values | "Static-like" members associated with the class |
| Count | One instance per declaration | At most one per class (optional) |
| Constructor | Cannot have one | Cannot have one |
| Inheritance | Can extend classes and implement interfaces | Can implement interfaces |
| Initialization | Lazy on first access; initialization is thread-safe | Lazy on first access to the companion or its members; initialization is thread-safe |
| Extensions | You can declare extension functions/properties for a specific `object` by its name | You can declare extensions for `Companion` (or the named companion object) |

### When to Use

Use `object` when:
- You need a single instance (Singleton)
- You are creating a utility holder
- You implement a global manager
- You define constants at module/top level (or use an `object` as a container)

Use `companion object` when:
- You need factory methods
- You keep constants inside the class
- You need "static-like" members strongly associated with the class
- You implement Factory-style APIs

### Advanced Examples

**Singleton with initialization:**
```kotlin
object AppConfig {
    private val properties = mutableMapOf<String, String>()

    init {
        // Runs once on first access
        println("Initializing AppConfig")
        loadProperties()
    }

    private fun loadProperties() {
        properties["api_url"] = "https://api.example.com"
        properties["timeout"] = "30"
    }

    fun get(key: String): String? = properties[key]
}

// First access initializes the object
val apiUrl = AppConfig.get("api_url")
```

**Companion object for DSL:**
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

// Using the DSL
val page = HtmlBuilder.html {
    tag("h1", "Title")
    tag("p", "Paragraph")
}
```

### Short Answer

- `object`: Singleton with lazy, thread-safe initialization. Good for one-off instances, utilities, global managers; can inherit and implement interfaces; can be used for constants at module/top level. `Thread`-safety here refers to initialization only; mutable state still requires explicit concurrency control.
- `companion object`: `Provides` static-like members inside a class, accessed via the class name. Good for factory methods, constants, and static helpers tied to that class; can implement interfaces and have extensions; exactly one per class, optionally named; lazily and safely initialized on first access.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-object-companion-object--kotlin--easy]]
- [[q-equals-hashcode-purpose--kotlin--medium]]
