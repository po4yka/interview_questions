---
id: 20251012-154385
title: "Object Keyword Kotlin / Ключевое слово object в Kotlin"
aliases: [Object Keyword, Object Declaration, Singleton, Object в Kotlin]
topic: kotlin
subtopics: [classes, singleton]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-flow-backpressure--kotlin--hard, q-kotlin-intrange--programming-languages--easy, q-collection-implementations--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - object-keyword
  - singleton
  - classes
  - difficulty/medium
---
# Tell about the Object keyword in Kotlin

# Question (EN)
> Tell about the `object` keyword in Kotlin. What are its use cases and characteristics?

# Вопрос (RU)
> Расскажите про ключевое слово `object` в Kotlin. Каковы его применения и характеристики?

---

## Answer (EN)

The `object` keyword in Kotlin is one of the most powerful and unique features of the language. It has several important applications:

1. **Object declaration (Singleton)** - Creates a single instance that exists throughout the application
2. **Companion objects** - Declares members accessible without creating a class instance (similar to static in Java)
3. **Object expressions** - Creates anonymous objects (similar to anonymous inner classes in Java)
4. **Anonymous objects** - Implements interfaces or extends classes on the fly

**Key characteristics:**
- Thread-safe by default
- Lazily initialized on first access
- Can implement interfaces and inherit from classes
- Can have properties, methods, and init blocks

### Code Examples

**1. Object Declaration (Singleton):**

```kotlin
object DatabaseManager {
    private var connectionCount = 0

    init {
        println("DatabaseManager initialized")
    }

    fun connect(): String {
        connectionCount++
        return "Connection #$connectionCount established"
    }

    fun disconnect() {
        println("Disconnected")
    }

    fun getStats() = "Total connections: $connectionCount"
}

fun main() {
    println(DatabaseManager.connect())  // Connection #1 established
    println(DatabaseManager.connect())  // Connection #2 established
    println(DatabaseManager.getStats())  // Total connections: 2

    DatabaseManager.disconnect()
}
```

**2. Companion Objects:**

```kotlin
class User(val id: Int, val name: String) {
    companion object {
        private var nextId = 1
        const val MIN_NAME_LENGTH = 3

        // Factory method
        fun create(name: String): User {
            require(name.length >= MIN_NAME_LENGTH) {
                "Name must be at least $MIN_NAME_LENGTH characters"
            }
            return User(nextId++, name)
        }

        // Helper method
        fun validateName(name: String): Boolean {
            return name.length >= MIN_NAME_LENGTH
        }
    }

    override fun toString() = "User(id=$id, name=$name)"
}

fun main() {
    val user1 = User.create("Alice")
    val user2 = User.create("Bob")

    println(user1)  // User(id=1, name=Alice)
    println(user2)  // User(id=2, name=Bob)

    println("Is valid: ${User.validateName("Al")}")  // false
}
```

**3. Object Expressions (Anonymous Objects):**

```kotlin
interface ClickListener {
    fun onClick()
    fun onLongClick()
}

fun setClickListener(listener: ClickListener) {
    listener.onClick()
}

fun main() {
    // Anonymous object implementing interface
    setClickListener(object : ClickListener {
        override fun onClick() {
            println("Button clicked!")
        }

        override fun onLongClick() {
            println("Button long-clicked!")
        }
    })

    // Anonymous object extending class
    open class Animal(val name: String) {
        open fun makeSound() {
            println("$name makes a sound")
        }
    }

    val dog = object : Animal("Dog") {
        override fun makeSound() {
            println("$name barks: Woof!")
        }
    }

    dog.makeSound()  // Dog barks: Woof!
}
```

**4. Object Expressions with Multiple Interfaces:**

```kotlin
interface Logger {
    fun log(message: String)
}

interface ErrorHandler {
    fun handleError(error: Exception)
}

fun createLogger(): Logger {
    return object : Logger, ErrorHandler {
        override fun log(message: String) {
            println("[LOG] $message")
        }

        override fun handleError(error: Exception) {
            println("[ERROR] ${error.message}")
        }
    }
}

fun main() {
    val logger = createLogger()
    logger.log("Application started")
}
```

**5. Object with State:**

```kotlin
object AppConfig {
    var apiUrl: String = "https://api.example.com"
    var timeout: Int = 30
    var debugMode: Boolean = false
    private val features = mutableMapOf<String, Boolean>()

    fun enableFeature(name: String) {
        features[name] = true
    }

    fun isFeatureEnabled(name: String): Boolean {
        return features[name] ?: false
    }

    fun printConfig() {
        println("API URL: $apiUrl")
        println("Timeout: $timeout")
        println("Debug Mode: $debugMode")
        println("Features: $features")
    }
}

fun main() {
    AppConfig.apiUrl = "https://api.production.com"
    AppConfig.debugMode = true
    AppConfig.enableFeature("dark_mode")
    AppConfig.enableFeature("notifications")

    AppConfig.printConfig()
    println("Dark mode enabled: ${AppConfig.isFeatureEnabled("dark_mode")}")
}
```

**6. Named Companion Object:**

```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
        fun createWithDefaults(): MyClass = MyClass()
    }
}

fun main() {
    // Can use both ways
    val obj1 = MyClass.create()
    val obj2 = MyClass.Factory.create()
}
```

**7. Object Implementing Interface:**

```kotlin
interface Printer {
    fun print(message: String)
}

object ConsolePrinter : Printer {
    override fun print(message: String) {
        println("[CONSOLE] $message")
    }
}

object FilePrinter : Printer {
    override fun print(message: String) {
        println("[FILE] Writing to file: $message")
    }
}

fun usePrinter(printer: Printer) {
    printer.print("Hello, World!")
}

fun main() {
    usePrinter(ConsolePrinter)
    usePrinter(FilePrinter)
}
```

**8. Anonymous Object with Local Variables:**

```kotlin
fun createCounter(start: Int): Any {
    var count = start

    return object {
        fun increment() = ++count
        fun decrement() = --count
        fun current() = count
    }
}

fun main() {
    val counter = createCounter(10)

    // Note: Need to cast to access methods due to type erasure
    val c = counter as? Any
    // In real code, you'd define an interface
}

// Better approach with interface:
interface Counter {
    fun increment(): Int
    fun decrement(): Int
    fun current(): Int
}

fun createCounterInterface(start: Int): Counter {
    var count = start

    return object : Counter {
        override fun increment() = ++count
        override fun decrement() = --count
        override fun current() = count
    }
}

fun demonstrateCounter() {
    val counter = createCounterInterface(5)
    println(counter.increment())  // 6
    println(counter.increment())  // 7
    println(counter.decrement())  // 6
    println(counter.current())    // 6
}
```

**9. Object as Namespace:**

```kotlin
object MathUtils {
    const val PI = 3.14159265359

    fun square(x: Int) = x * x

    fun cube(x: Int) = x * x * x

    fun isPrime(n: Int): Boolean {
        if (n < 2) return false
        for (i in 2..Math.sqrt(n.toDouble()).toInt()) {
            if (n % i == 0) return false
        }
        return true
    }
}

fun main() {
    println("Square of 5: ${MathUtils.square(5)}")
    println("Cube of 3: ${MathUtils.cube(3)}")
    println("Is 17 prime: ${MathUtils.isPrime(17)}")
    println("PI: ${MathUtils.PI}")
}
```

**10. Object vs Class Instance:**

```kotlin
// Regular class - multiple instances
class RegularClass {
    val id = System.currentTimeMillis()
}

// Object - single instance
object SingletonObject {
    val id = System.currentTimeMillis()
}

fun main() {
    val r1 = RegularClass()
    Thread.sleep(10)
    val r2 = RegularClass()

    println("Regular instances same? ${r1 === r2}")  // false
    println("R1 ID: ${r1.id}")
    println("R2 ID: ${r2.id}")  // Different IDs

    println()

    val s1 = SingletonObject
    Thread.sleep(10)
    val s2 = SingletonObject

    println("Singleton instances same? ${s1 === s2}")  // true
    println("S1 ID: ${s1.id}")
    println("S2 ID: ${s2.id}")  // Same ID
}
```

---

## Ответ (RU)

Ключевое слово `object` в Kotlin является одной из наиболее мощных и уникальных возможностей языка. Оно имеет несколько важных применений:

1. **Object declaration (Объявление объекта)** - Создаёт единственный экземпляр (Singleton), существующий на протяжении всего приложения
2. **Companion objects (Объекты-компаньоны)** - Объявляет члены, доступные без создания экземпляра класса (аналог static в Java)
3. **Object expressions (Объект-выражения)** - Создаёт анонимные объекты (аналог anonymous inner classes в Java)
4. **Anonymous objects (Анонимные объекты)** - Реализует интерфейсы или расширяет классы "на лету"

**Ключевые характеристики:**
- Потокобезопасны по умолчанию
- Ленивая инициализация при первом обращении
- Могут реализовывать интерфейсы и наследоваться от классов
- Могут иметь свойства, методы и init блоки

### Примеры кода

**1. Object Declaration (Singleton):**

```kotlin
object DatabaseManager {
    private var connectionCount = 0

    init {
        println("DatabaseManager инициализирован")
    }

    fun connect(): String {
        connectionCount++
        return "Подключение #$connectionCount установлено"
    }

    fun disconnect() {
        println("Отключено")
    }

    fun getStats() = "Всего подключений: $connectionCount"
}

// Использование
println(DatabaseManager.connect())  // Подключение #1 установлено
println(DatabaseManager.connect())  // Подключение #2 установлено
println(DatabaseManager.getStats())  // Всего подключений: 2
DatabaseManager.disconnect()
```

**2. Companion Objects (Объекты-компаньоны):**

```kotlin
class User(val id: Int, val name: String) {
    companion object {
        private var nextId = 1
        const val MIN_NAME_LENGTH = 3

        // Фабричный метод
        fun create(name: String): User {
            require(name.length >= MIN_NAME_LENGTH) {
                "Имя должно быть не менее $MIN_NAME_LENGTH символов"
            }
            return User(nextId++, name)
        }

        // Вспомогательный метод
        fun validateName(name: String): Boolean {
            return name.length >= MIN_NAME_LENGTH
        }
    }

    override fun toString() = "User(id=$id, name=$name)"
}

// Использование
val user1 = User.create("Alice")
val user2 = User.create("Bob")
println(user1)  // User(id=1, name=Alice)
println(user2)  // User(id=2, name=Bob)
println("Валидно: ${User.validateName("Al")}")  // false
```

**3. Object Expressions (Анонимные объекты):**

```kotlin
interface ClickListener {
    fun onClick()
    fun onLongClick()
}

fun setClickListener(listener: ClickListener) {
    listener.onClick()
}

// Анонимный объект, реализующий интерфейс
setClickListener(object : ClickListener {
    override fun onClick() {
        println("Кнопка нажата!")
    }

    override fun onLongClick() {
        println("Долгое нажатие!")
    }
})

// Анонимный объект, расширяющий класс
open class Animal(val name: String) {
    open fun makeSound() {
        println("$name издаёт звук")
    }
}

val dog = object : Animal("Собака") {
    override fun makeSound() {
        println("$name лает: Гав!")
    }
}

dog.makeSound()  // Собака лает: Гав!
```

**4. Object с состоянием:**

```kotlin
object AppConfig {
    var apiUrl: String = "https://api.example.com"
    var timeout: Int = 30
    var debugMode: Boolean = false
    private val features = mutableMapOf<String, Boolean>()

    fun enableFeature(name: String) {
        features[name] = true
    }

    fun isFeatureEnabled(name: String): Boolean {
        return features[name] ?: false
    }

    fun printConfig() {
        println("API URL: $apiUrl")
        println("Timeout: $timeout")
        println("Debug Mode: $debugMode")
        println("Features: $features")
    }
}

// Использование
AppConfig.apiUrl = "https://api.production.com"
AppConfig.debugMode = true
AppConfig.enableFeature("dark_mode")
AppConfig.enableFeature("notifications")

AppConfig.printConfig()
println("Тёмная тема: ${AppConfig.isFeatureEnabled("dark_mode")}")
```

**5. Именованный Companion Object:**

```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
        fun createWithDefaults(): MyClass = MyClass()
    }
}

// Можно использовать оба способа
val obj1 = MyClass.create()
val obj2 = MyClass.Factory.create()
```

**6. Object реализующий интерфейс:**

```kotlin
interface Printer {
    fun print(message: String)
}

object ConsolePrinter : Printer {
    override fun print(message: String) {
        println("[CONSOLE] $message")
    }
}

object FilePrinter : Printer {
    override fun print(message: String) {
        println("[FILE] Запись в файл: $message")
    }
}

fun usePrinter(printer: Printer) {
    printer.print("Привет, мир!")
}

// Использование
usePrinter(ConsolePrinter)
usePrinter(FilePrinter)
```

**7. Object как пространство имён:**

```kotlin
object MathUtils {
    const val PI = 3.14159265359

    fun square(x: Int) = x * x

    fun cube(x: Int) = x * x * x

    fun isPrime(n: Int): Boolean {
        if (n < 2) return false
        for (i in 2..Math.sqrt(n.toDouble()).toInt()) {
            if (n % i == 0) return false
        }
        return true
    }
}

// Использование
println("Квадрат 5: ${MathUtils.square(5)}")
println("Куб 3: ${MathUtils.cube(3)}")
println("17 простое: ${MathUtils.isPrime(17)}")
println("PI: ${MathUtils.PI}")
```

**8. Object vs Class Instance:**

```kotlin
// Обычный класс - множественные экземпляры
class RegularClass {
    val id = System.currentTimeMillis()
}

// Object - единственный экземпляр
object SingletonObject {
    val id = System.currentTimeMillis()
}

fun main() {
    val r1 = RegularClass()
    Thread.sleep(10)
    val r2 = RegularClass()

    println("Обычные экземпляры одинаковые? ${r1 === r2}")  // false
    println("R1 ID: ${r1.id}")
    println("R2 ID: ${r2.id}")  // Разные ID

    val s1 = SingletonObject
    Thread.sleep(10)
    val s2 = SingletonObject

    println("Singleton экземпляры одинаковые? ${s1 === s2}")  // true
    println("S1 ID: ${s1.id}")
    println("S2 ID: ${s2.id}")  // Одинаковый ID
}
```

**9. Анонимный объект с замыканием:**

```kotlin
interface Counter {
    fun increment(): Int
    fun decrement(): Int
    fun current(): Int
}

fun createCounter(start: Int): Counter {
    var count = start

    return object : Counter {
        override fun increment() = ++count
        override fun decrement() = --count
        override fun current() = count
    }
}

// Использование
val counter = createCounter(5)
println(counter.increment())  // 6
println(counter.increment())  // 7
println(counter.decrement())  // 6
println(counter.current())    // 6
```

**10. Object с несколькими интерфейсами:**

```kotlin
interface Logger {
    fun log(message: String)
}

interface ErrorHandler {
    fun handleError(error: Exception)
}

fun createLogger(): Logger {
    return object : Logger, ErrorHandler {
        override fun log(message: String) {
            println("[LOG] $message")
        }

        override fun handleError(error: Exception) {
            println("[ERROR] ${error.message}")
        }
    }
}

// Использование
val logger = createLogger()
logger.log("Приложение запущено")
```

### Основные применения

**1. Singleton паттерн:**
- Единственный экземпляр на всё приложение
- Потокобезопасен
- Ленивая инициализация

**2. Companion objects:**
- "Статические" члены класса
- Фабричные методы
- Константы класса

**3. Анонимные объекты:**
- Реализация интерфейсов "на лету"
- Расширение классов без создания новых типов
- Замыкания с состоянием

**4. Утилитные классы:**
- Группировка связанных функций
- Пространства имён
- Константы

### Краткий ответ

`object` в Kotlin используется для:
- **Singleton**: Создание единственного потокобезопасного экземпляра с ленивой инициализацией
- **Companion objects**: Статико-подобные члены внутри классов
- **Anonymous objects**: Анонимные реализации интерфейсов и классов
- **Utility classes**: Группировка утилитных функций и констант

Все варианты потокобезопасны, могут реализовывать интерфейсы и наследоваться от классов, имеют свойства, методы и init блоки.

## Related Questions

- [[q-flow-backpressure--kotlin--hard]]
- [[q-kotlin-intrange--programming-languages--easy]]
- [[q-collection-implementations--programming-languages--easy]]
