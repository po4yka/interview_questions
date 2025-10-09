---
tags:
  - programming-languages
difficulty: easy
status: reviewed
---

# Can you call a function or constructor after by

**English**: Can you call a function or constructor after the `by` keyword in Kotlin?

## Answer

No, you cannot call functions or constructors after `by`. The `by` keyword expects a ready-made object that implements an interface or delegates a property.

**Important:**
- `by` requires an expression that evaluates to an object
- The object must be available at the point of delegation
- You can use a property, parameter, or expression that returns an object
- You cannot use a constructor call directly (but you can wrap it in a function or property)

### Code Examples

**Property delegation - CORRECT:**

```kotlin
class Example {
    // CORRECT: by expects ready object
    val lazyValue: String by lazy { "Computed value" }

    // CORRECT: delegation to parameter
    constructor(list: MutableList<String>) : this() {
        // delegatedList = list  // Would need to be set elsewhere
    }

    // CORRECT: delegation to property
    private val backingList = mutableListOf<String>()
    val items: List<String> by backingList

    // ERROR: Cannot call constructor
    // val map: MutableMap<String, Any> by HashMap()  // WRONG!

    // CORRECT: Use property
    private val backingMap = HashMap<String, Any>()
    val map: MutableMap<String, Any> by backingMap  // Correct
}
```

**Interface delegation - CORRECT vs WRONG:**

```kotlin
interface Printer {
    fun print(message: String)
}

class ConsolePrinter : Printer {
    override fun print(message: String) {
        println(message)
    }
}

// WRONG: Cannot use constructor directly
// class Document : Printer by ConsolePrinter()  // ERROR!

// CORRECT: Use object or property
object DefaultPrinter : Printer {
    override fun print(message: String) {
        println("[DEFAULT] $message")
    }
}

class Document1 : Printer by DefaultPrinter  // OK - object

class Document2(printer: Printer) : Printer by printer  // OK - parameter

class Document3 : Printer by ConsolePrinter()  // Actually OK in this case!

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
    // CORRECT: lazy returns a delegate
    val value1: String by lazy { "Lazy value" }

    // CORRECT: can call function that returns delegate
    val value2: String by lazy(LazyThreadSafetyMode.NONE) {
        "Thread-unsafe lazy value"
    }

    // WRONG: Cannot call random function
    // val value3: String by getValue()  // ERROR if getValue doesn't return delegate

    // CORRECT: Function returns proper delegate
    private fun getDelegate() = lazy { "From function" }
    val value4: String by getDelegate()
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
    // WRONG: Cannot call function directly
    // var name: String by LoggingDelegate("Initial")  // May or may not work

    // CORRECT: The above actually works because constructor returns delegate

    // More explicit version:
    private fun createLoggingDelegate(initial: String) = LoggingDelegate(initial)
    var name: String by LoggingDelegate("Alice")  // Works
    var age: Int by LoggingDelegate(30)  // Works
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

**Summary - What works:**

```kotlin
import kotlin.properties.Delegates

class DelegationSummary {
    // ✅ WORKS: Object
    val value1: String by lazy { "value" }

    // ✅ WORKS: Property
    private val backingList = mutableListOf<String>()
    val list: List<String> by backingList

    // ✅ WORKS: Built-in delegate factory
    var observed: String by Delegates.observable("") { _, _, _ -> }

    // ✅ WORKS: Constructor that returns delegate
    var logged: String by LoggingDelegate("initial")

    // ✅ WORKS: Function that returns delegate
    private fun getDelegate() = lazy { "value" }
    val value2: String by getDelegate()

    // ❌ DOESN'T WORK: Random function call
    // val value3: String by someFunction()  // Unless it returns a delegate

    // ❌ DOESN'T WORK: Expression that doesn't return delegate
    // val value4: String by "string".uppercase()  // ERROR
}
```

---

## Ответ

### Вопрос
Можно ли после by вызвать функцию или конструктор

### Ответ
Нет, после by нельзя вызывать функции или конструкторы. by ожидает готовый объект, который реализует интерфейс или делегирует свойство.
