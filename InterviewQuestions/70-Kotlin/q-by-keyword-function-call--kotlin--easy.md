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
related: []
created: 2025-10-15
updated: 2025-10-31
tags: [by-keyword, delegation, difficulty/easy, programming-languages]
---
# Can You Call a Function or Constructor after by

# Вопрос (RU)
> Можно ли вызывать функцию или конструктор после ключевого слова `by` в Kotlin?

---

# Question (EN)
> Can you call a function or constructor after the `by` keyword in Kotlin?

## Ответ (RU)

Да, после `by` можно вызывать конструкторы. Ключевое слово `by` ожидает выражение, которое возвращает объект-делегат, а значит можно вызывать конструкторы, функции или использовать любое выражение, возвращающее подходящий делегат.

**Важно:**
- `by` требует выражение, которое возвращает объект-делегат
- Можно вызывать конструкторы, возвращающие экземпляры делегатов (наиболее частый случай)
- Можно вызывать функции, возвращающие делегаты
- Можно использовать свойства, параметры или любое выражение, возвращающее подходящий делегат
- Ключевое требование: выражение должно возвращать объект с правильным контрактом делегирования

### Что Работает С `by`

```kotlin
//  РАБОТАЕТ: Вызов функции, возвращающей делегат
val value1: String by lazy { "value" }

//  РАБОТАЕТ: Ссылка на свойство
private val backingList = mutableListOf<String>()
val list: List<String> by backingList

//  РАБОТАЕТ: Вызов функции со встроенной фабрикой делегатов
var observed: String by Delegates.observable("") { _, _, _ -> }

//  РАБОТАЕТ: Вызов конструктора, возвращающего делегат
var logged: String by LoggingDelegate("initial")

//  РАБОТАЕТ: Вызов функции, возвращающей делегат
private fun getDelegate() = lazy { "value" }
val value2: String by getDelegate()

//  НЕ РАБОТАЕТ: Вызов функции, не возвращающей делегат
// val value3: String by someFunction()  // ОШИБКА, если someFunction() возвращает String

//  НЕ РАБОТАЕТ: Выражение, не возвращающее делегат
// val value4: String by "string".uppercase()  // ОШИБКА - String не является делегатом
```

## Answer (EN)

Yes, you can call constructors after `by`. The `by` keyword expects an expression that evaluates to a delegate object, which means you can call constructors, functions, or use any expression that returns an appropriate delegate.

**Important:**
- `by` requires an expression that evaluates to a delegate object
- You can call constructors that return delegate instances (most common)
- You can call functions that return delegates
- You can use properties, parameters, or any expression that returns a valid delegate
- The key is that the expression must evaluate to an object with the proper delegation contract

### Code Examples

**Property delegation - CORRECT:**

```kotlin
class Example {
    // CORRECT: by calls function that returns delegate
    val lazyValue: String by lazy { "Computed value" }

    // CORRECT: delegation to parameter
    constructor(list: MutableList<String>) : this() {
        // delegatedList = list  // Would need to be set elsewhere
    }

    // CORRECT: delegation to property
    private val backingList = mutableListOf<String>()
    val items: List<String> by backingList

    // Note: Property delegation requires specific delegate contract
    // Maps don't implement property delegate contract directly
    // Use observable/vetoable delegates or custom delegates instead

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

// APPROACH 2: Delegation to property (CORRECT)
class UserRepository2 : Repository<String> {
    private val delegate = InMemoryRepository<String>()

    // Manual delegation (alternative to 'by')
    override fun save(item: String) = delegate.save(item)
    override fun findAll(): List<String> = delegate.findAll()
}

// APPROACH 3: Using 'by' with property (CORRECT)
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

class Example {
    // CORRECT: Constructor call that returns delegate instance
    var name: String by LoggingDelegate("Alice")  // Constructor call is OK!
    var age: Int by LoggingDelegate(30)  // Constructor call is OK!

    // CORRECT: Function call that returns delegate
    private fun createLoggingDelegate(initial: String) = LoggingDelegate(initial)
    var email: String by createLoggingDelegate("test@example.com")  // Function call is OK!
}

fun main() {
    val example = Example()

    println(example.name)  // Getting name = Alice
    example.name = "Bob"   // Setting name = Bob
    println(example.name)  // Getting name = Bob

    println(example.age)   // Getting age = 30
    example.age = 31       // Setting age = 31
}
```

**Observable and Vetoable delegates:**

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

    // Can wrap in function
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

**Map delegation:**

```kotlin
class User(map: Map<String, Any>) {
    // Delegation to map
    val name: String by map
    val age: Int by map
    val email: String by map

    // WRONG: Cannot call function
    // val id: Int by map.getValue("id")  // ERROR

    // CORRECT: map itself is the delegate
}

class MutableUser(val map: MutableMap<String, Any>) {
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

    val user = User(userData)
    println("${user.name}, ${user.age}, ${user.email}")

    val mutableData = mutableMapOf(
        "name" to "Bob",
        "age" to 25,
        "email" to "bob@example.com"
    )

    val mutableUser = MutableUser(mutableData)
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

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-kotlin-reified-types--kotlin--hard]]
