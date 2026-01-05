---
id: kotlin-211
title: "By Keyword Function Call / Ключевое слово by и вызов функции"
aliases: [By Keyword Function Call, Ключевое слово by]
topic: kotlin
subtopics: [delegation]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin]
created: 2025-10-15
updated: 2025-11-11
tags: [by-keyword, delegation, difficulty/easy, programming-languages]

---
# Вопрос (RU)
> Можно ли вызывать функцию или конструктор после ключевого слова `by` в Kotlin?

---

# Question (EN)
> Can you call a function or constructor after the `by` keyword in Kotlin?

## Ответ (RU)

Да. Ключевое слово `by` ожидает выражение, которое возвращает объект-делегат, поэтому после `by` можно вызывать конструкторы, функции или использовать любое другое выражение, возвращающее корректный делегат.

**Важно:**
- `by` требует выражение, которое возвращает объект-делегат
- Можно вызывать конструкторы, возвращающие экземпляры делегатов (частый случай)
- Можно вызывать функции, возвращающие делегаты
- Можно использовать свойства, параметры или любое выражение, возвращающее подходящий делегат
- Ключевое требование: выражение должно возвращать объект с правильным контрактом делегирования (`getValue` / `setValue` или реализации нужных интерфейсов)

### Примеры Кода

**Делегирование свойств — КОРРЕКТНО:**

```kotlin
import kotlin.properties.Delegates

class Example {
    // КОРРЕКТНО: by вызывает функцию, возвращающую делегат
    val lazyValue: String by lazy { "Computed value" }

    // КОРРЕКТНО: делегирование к свойству / объекту-коллекции
    private val backingList = mutableListOf<String>()
    val items: List<String> by backingList

    // Примечание: делегат должен реализовывать контракт делегирования
    // (operator fun getValue / setValue или соответствующие интерфейсы).

    // КОРРЕКТНО: использование observable-делегата
    var count: Int by Delegates.observable(0) { _, old, new ->
        println("Count changed: $old -> $new")
    }
}
```

### Делегирование Интерфейса — Все КОРРЕКТНЫЕ Варианты

```kotlin
interface Printer {
    fun print(message: String)
}

class ConsolePrinter : Printer {
    override fun print(message: String) {
        println(message)
    }
}

// КОРРЕКТНО: использование object-ссылки
object DefaultPrinter : Printer {
    override fun print(message: String) {
        println("[DEFAULT] $message")
    }
}

class Document1 : Printer by DefaultPrinter  // OK — ссылка на объект

// КОРРЕКТНО: делегирование на параметр конструктора
class Document2(printer: Printer) : Printer by printer  // OK — параметр

// КОРРЕКТНО: прямой вызов конструктора
class Document3 : Printer by ConsolePrinter()  // OK — вызов конструктора!

fun main() {
    val doc1 = Document1()
    doc1.print("Hello from doc1")

    val doc2 = Document2(ConsolePrinter())
    doc2.print("Hello from doc2")

    val doc3 = Document3()
    doc3.print("Hello from doc3")
}
```

### Примеры С Lazy-делегированием

```kotlin
class LazyExample {
    // КОРРЕКТНО: lazy возвращает делегат
    val value1: String by lazy { "Lazy value" }

    // КОРРЕКТНО: функция с параметрами, возвращающая делегат
    val value2: String by lazy(LazyThreadSafetyMode.NONE) {
        "Thread-unsafe lazy value"
    }

    // НЕРАБОЧЕЕ: функция, не возвращающая делегат
    // val value3: String by getValue()  // ОШИБКА, если getValue возвращает String, а не делегат

    // КОРРЕКТНО: функция, возвращающая делегат
    private fun getDelegate() = lazy { "From function" }
    val value4: String by getDelegate()  // Вызов функции допустим
}

fun main() {
    val example = LazyExample()
    println(example.value1)
    println(example.value2)
    println(example.value4)
}
```

### Делегирование Классов Подробнее

```kotlin
interface Repository<T> {
    fun save(item: T)
    fun findAll(): List<T>
}

class InMemoryRepository<T> : Repository<T> {
    private val items = mutableListOf<T>()

    override fun save(item: T) {
        items.add(item)
    }

    override fun findAll(): List<T> = items.toList()
}

// ПОДХОД 1: делегирование на параметр (КОРРЕКТНО)
class UserRepository1(
    repository: Repository<String>
) : Repository<String> by repository

// ПОДХОД 2: ручная передача вызовов (без использования `by`)
class UserRepository2 : Repository<String> {
    private val delegate = InMemoryRepository<String>()

    override fun save(item: String) = delegate.save(item)
    override fun findAll(): List<String> = delegate.findAll()
}

// ПОДХОД 3: использование `by` с вызовом конструктора (КОРРЕКТНО)
class UserRepository3 : Repository<String> by InMemoryRepository()

fun main() {
    val repo1 = UserRepository1(InMemoryRepository())
    repo1.save("User1")
    println(repo1.findAll())

    val repo3 = UserRepository3()
    repo3.save("User3")
    println(repo3.findAll())
}
```

### Пользовательские Делегаты Свойств

```kotlin
import kotlin.properties.ReadWriteProperty
import kotlin.reflect.KProperty

class LoggingDelegate<T>(private var value: T) : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Getting ${property.name} = $value")
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Setting ${property.name} = $value")
        this.value = value
    }
}

class ExampleWithLogging {
    // КОРРЕКТНО: вызов конструктора, возвращающего делегат
    var name: String by LoggingDelegate("Alice")
    var age: Int by LoggingDelegate(30)

    // КОРРЕКТНО: функция, возвращающая делегат
    private fun createLoggingDelegate(initial: String) = LoggingDelegate(initial)
    var email: String by createLoggingDelegate("test@example.com")
}

fun main() {
    val example = ExampleWithLogging()

    println(example.name)   // Getting name = Alice
    example.name = "Bob"   // Setting name = Bob
    println(example.name)   // Getting name = Bob

    println(example.age)    // Getting age = 30
    example.age = 31        // Setting age = 31
}
```

### Observable И Vetoable Делегаты

```kotlin
import kotlin.properties.Delegates

class User {
    // Встроенные делегаты — работают с `by`
    var name: String by Delegates.observable("Initial") { prop, old, new ->
        println("${prop.name}: '$old' -> '$new'")
    }

    var age: Int by Delegates.vetoable(0) { prop, old, new ->
        println("Attempting to change ${prop.name}: $old -> $new")
        new >= 0  // Разрешаем только неотрицательные значения
    }

    // Обёртка в функцию, возвращающую делегат
    private fun createObservable(initial: String) =
        Delegates.observable(initial) { _, old, new ->
            println("Changed: $old -> $new")
        }

    var email: String by createObservable("default@example.com")
}

fun main() {
    val user = User()

    user.name = "Alice"    // name: 'Initial' -> 'Alice'
    user.name = "Bob"      // name: 'Alice' -> 'Bob'

    user.age = 30           // Attempting to change age: 0 -> 30
    user.age = -5           // Attempting to change age: 30 -> -5 (отклонено)
    println("Age: ${user.age}")  // 30 (изменение отклонено)

    user.email = "alice@example.com"  // Changed: default@example.com -> alice@example.com
}
```

### Делегирование На `Map`

```kotlin
class UserFromMap(map: Map<String, Any>) {
    // Делегирование на `Map` (стандартные `Map` предоставляют нужные операторы)
    val name: String by map
    val age: Int by map
    val email: String by map

    // НЕРАБОЧЕЕ: делегирование на результат `map.getValue("id")`
    // val id: Int by map.getValue("id")  // ОШИБКА — это значение, а не делегат
}

class MutableUserFromMap(val map: MutableMap<String, Any>) {
    var name: String by map
    var age: Int by map
    var email: String by map
}

fun main() {
    val userData = mapOf(
        "name" to "Alice",
        "age" to 30,
        "email" to "alice@example.com"
    )

    val user = UserFromMap(userData)
    println("${user.name}, ${user.age}, ${user.email}")

    val mutableData = mutableMapOf(
        "name" to "Bob",
        "age" to 25,
        "email" to "bob@example.com"
    )

    val mutableUser = MutableUserFromMap(mutableData)
    println("${mutableUser.name}, ${mutableUser.age}")

    mutableUser.name = "Charlie"
    println("Updated: ${mutableUser.name}")
    println("Map: ${mutableData}")  // Map также обновляется
}
```

### Итог — Что Работает С `by`

```kotlin
import kotlin.properties.Delegates

class DelegationSummary {
    // РАБОТАЕТ: вызов функции, возвращающей делегат
    val value1: String by lazy { "value" }

    // РАБОТАЕТ: делегирование на свойство / объект
    private val backingList = mutableListOf<String>()
    val list: List<String> by backingList

    // РАБОТАЕТ: функция-фабрика встроенного делегата
    var observed: String by Delegates.observable("") { _, _, _ -> }

    // РАБОТАЕТ: вызов конструктора, возвращающего делегат
    var logged: String by LoggingDelegate("initial")

    // РАБОТАЕТ: вызов функции, возвращающей делегат
    private fun getDelegate() = lazy { "value" }
    val value2: String by getDelegate()

    // НЕ РАБОТАЕТ: функция, не возвращающая делегат
    // val value3: String by someFunction()  // ОШИБКА, если someFunction() возвращает String

    // НЕ РАБОТАЕТ: выражение, не возвращающее делегат
    // val value4: String by "string".uppercase()  // ОШИБКА — String не является делегатом
}
```

## Answer (EN)

Yes. The `by` keyword expects an expression that evaluates to a delegate object, so you can call constructors, functions, or use any other expression that returns a proper delegate.

**Important:**
- `by` requires an expression that evaluates to a delegate object
- You can call constructors that return delegate instances (common case)
- You can call functions that return delegates
- You can use properties, parameters, or any expression that returns a valid delegate
- The key is that the expression must evaluate to an object with the proper delegation contract (e.g. `getValue` / `setValue` or proper interfaces)

### Code Examples

**Property delegation - CORRECT:**

```kotlin
import kotlin.properties.Delegates

class Example {
    // CORRECT: by calls function that returns delegate
    val lazyValue: String by lazy { "Computed value" }

    // CORRECT: delegation to property
    private val backingList = mutableListOf<String>()
    val items: List<String> by backingList

    // Note: Property delegation requires a specific delegate contract
    // (operator fun getValue / setValue or relevant interfaces).

    // CORRECT: Use observable delegate
    var count: Int by Delegates.observable(0) { _, old, new ->
        println("Count changed: $old -> $new")
    }
}
```

**Interface delegation - All CORRECT approaches:**

```kotlin
interface Printer {
    fun print(message: String)
}

class ConsolePrinter : Printer {
    override fun print(message: String) {
        println(message)
    }
}

// CORRECT: Use object reference
object DefaultPrinter : Printer {
    override fun print(message: String) {
        println("[DEFAULT] $message")
    }
}

class Document1 : Printer by DefaultPrinter  // OK - object reference

// CORRECT: Use parameter
class Document2(printer: Printer) : Printer by printer  // OK - parameter

// CORRECT: Call constructor directly
class Document3 : Printer by ConsolePrinter()  // OK - constructor call!

fun main() {
    val doc1 = Document1()
    doc1.print("Hello from doc1")

    val doc2 = Document2(ConsolePrinter())
    doc2.print("Hello from doc2")

    val doc3 = Document3()
    doc3.print("Hello from doc3")
}
```

**Lazy delegation examples:**

```kotlin
class LazyExample {
    // CORRECT: lazy function call returns a delegate
    val value1: String by lazy { "Lazy value" }

    // CORRECT: can call function with parameters that returns delegate
    val value2: String by lazy(LazyThreadSafetyMode.NONE) {
        "Thread-unsafe lazy value"
    }

    // WRONG: Random function call that doesn't return a delegate
    // val value3: String by getValue()  // ERROR if getValue returns String instead of delegate

    // CORRECT: Function that returns proper delegate
    private fun getDelegate() = lazy { "From function" }
    val value4: String by getDelegate()  // Function call is OK
}

fun main() {
    val example = LazyExample()
    println(example.value1)
    println(example.value2)
    println(example.value4)
}
```

**Class delegation in detail:**

```kotlin
interface Repository<T> {
    fun save(item: T)
    fun findAll(): List<T>
}

class InMemoryRepository<T> : Repository<T> {
    private val items = mutableListOf<T>()

    override fun save(item: T) {
        items.add(item)
    }

    override fun findAll(): List<T> = items.toList()
}

// APPROACH 1: Delegation to parameter (CORRECT)
class UserRepository1(
    repository: Repository<String>
) : Repository<String> by repository

// APPROACH 2: Delegation to property (manual alternative to 'by')
class UserRepository2 : Repository<String> {
    private val delegate = InMemoryRepository<String>()

    override fun save(item: String) = delegate.save(item)
    override fun findAll(): List<String> = delegate.findAll()
}

// APPROACH 3: Using 'by' with constructor call (CORRECT)
class UserRepository3 : Repository<String> by InMemoryRepository()

fun main() {
    val repo1 = UserRepository1(InMemoryRepository())
    repo1.save("User1")
    println(repo1.findAll())

    val repo3 = UserRepository3()
    repo3.save("User3")
    println(repo3.findAll())
}
```

**Custom property delegates:**

```kotlin
import kotlin.properties.ReadWriteProperty
import kotlin.reflect.KProperty

class LoggingDelegate<T>(private var value: T) : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Getting ${property.name} = $value")
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Setting ${property.name} = $value")
        this.value = value
    }
}

class ExampleWithLogging {
    // CORRECT: Constructor call that returns delegate instance
    var name: String by LoggingDelegate("Alice")  // Constructor call is OK!
    var age: Int by LoggingDelegate(30)  // Constructor call is OK!

    // CORRECT: Function call that returns delegate
    private fun createLoggingDelegate(initial: String) = LoggingDelegate(initial)
    var email: String by createLoggingDelegate("test@example.com")  // Function call is OK!
}

fun main() {
    val example = ExampleWithLogging()

    println(example.name)  // Getting name = Alice
    example.name = "Bob"   // Setting name = Bob
    println(example.name)  // Getting name = Bob

    println(example.age)   // Getting age = 30
    example.age = 31       // Setting age = 31
}
```

**`Observable` and Vetoable delegates:**

```kotlin
import kotlin.properties.Delegates

class User {
    // Built-in delegates - these work with 'by'
    var name: String by Delegates.observable("Initial") { prop, old, new ->
        println("${prop.name}: '$old' -> '$new'")
    }

    var age: Int by Delegates.vetoable(0) { prop, old, new ->
        println("Attempting to change ${prop.name}: $old -> $new")
        new >= 0  // Only allow non-negative values
    }

    // Can wrap in function that returns a delegate
    private fun createObservable(initial: String) =
        Delegates.observable(initial) { _, old, new ->
            println("Changed: $old -> $new")
        }

    var email: String by createObservable("default@example.com")
}

fun main() {
    val user = User()

    user.name = "Alice"    // name: 'Initial' -> 'Alice'
    user.name = "Bob"      // name: 'Alice' -> 'Bob'

    user.age = 30          // Attempting to change age: 0 -> 30
    user.age = -5          // Attempting to change age: 30 -> -5 (rejected)
    println("Age: ${user.age}")  // 30 (change was vetoed)

    user.email = "alice@example.com"  // Changed: default@example.com -> alice@example.com
}
```

**`Map` delegation:**

```kotlin
class UserFromMap(map: Map<String, Any>) {
    // Delegation to map (standard Kotlin `Map` provides the delegate operators)
    val name: String by map
    val age: Int by map
    val email: String by map

    // WRONG: Cannot delegate to result of map.getValue("id") directly
    // val id: Int by map.getValue("id")  // ERROR - this returns a value, not a delegate
}

class MutableUserFromMap(val map: MutableMap<String, Any>) {
    var name: String by map
    var age: Int by map
    var email: String by map
}

fun main() {
    val userData = mapOf(
        "name" to "Alice",
        "age" to 30,
        "email" to "alice@example.com"
    )

    val user = UserFromMap(userData)
    println("${user.name}, ${user.age}, ${user.email}")

    val mutableData = mutableMapOf(
        "name" to "Bob",
        "age" to 25,
        "email" to "bob@example.com"
    )

    val mutableUser = MutableUserFromMap(mutableData)
    println("${mutableUser.name}, ${mutableUser.age}")

    mutableUser.name = "Charlie"
    println("Updated: ${mutableUser.name}")
    println("Map: ${mutableData}")  // Map is updated too
}
```

**Summary - What works with `by`:**

```kotlin
import kotlin.properties.Delegates

class DelegationSummary {
    // - WORKS: Function call returning delegate
    val value1: String by lazy { "value" }

    // - WORKS: Property reference
    private val backingList = mutableListOf<String>()
    val list: List<String> by backingList

    // - WORKS: Function call with built-in delegate factory
    var observed: String by Delegates.observable("") { _, _, _ -> }

    // - WORKS: Constructor call that returns delegate
    var logged: String by LoggingDelegate("initial")

    // - WORKS: Function call that returns delegate
    private fun getDelegate() = lazy { "value" }
    val value2: String by getDelegate()

    // - DOESN'T WORK: Function call that doesn't return a delegate
    // val value3: String by someFunction()  // ERROR if someFunction() returns String

    // - DOESN'T WORK: Expression that doesn't return a delegate
    // val value4: String by "string".uppercase()  // ERROR - String is not a delegate
}
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation]("https://kotlinlang.org/docs/home.html")
- [[c-kotlin]]

## Related Questions

- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-kotlin-reified-types--kotlin--hard]]
