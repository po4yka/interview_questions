---
id: 20251012-003
title: "Val vs Var in Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [val, var, immutability, mutability, read-only, constants]
question_kind: comparison
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Deep dive into val vs var in Kotlin

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-properties--kotlin--easy, q-kotlin-const--kotlin--easy, q-kotlin-constructors--kotlin--easy]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, val, var, immutability, mutability, read-only, constants, difficulty/easy]
---

# Question (EN)
> What's the difference between val and var in Kotlin? When should you use each?

# Вопрос (RU)
> В чём разница между val и var в Kotlin? Когда использовать каждый из них?

---

## Answer (EN)

`val` and `var` are keywords for declaring variables/properties in Kotlin. Understanding when to use each is fundamental to writing idiomatic, safe Kotlin code.

### Core Difference

```kotlin
val name = "Alice"      // Read-only (immutable reference)
var age = 25            // Mutable

// name = "Bob"         // Error: Val cannot be reassigned
age = 26                // OK: Var can be reassigned
```

**val** = **value** = read-only reference (like Java's `final`)
**var** = **variable** = mutable reference

### Val: Read-Only Reference

```kotlin
val x = 10
// x = 20  // Compilation error

val list = mutableListOf(1, 2, 3)
list.add(4)                // OK: contents can change
// list = mutableListOf()  // Error: reference cannot change
```

**Key points about val**:
1. Reference cannot be reassigned
2. Must be initialized when declared or in init block
3. Can only be assigned once
4. Does NOT mean the object is immutable
5. Preferred in Kotlin (immutability-first approach)

### Var: Mutable Reference

```kotlin
var counter = 0
counter = 1      // OK
counter = 2      // OK
counter += 10    // OK
```

**Key points about var**:
1. Reference can be reassigned
2. Can be modified after initialization
3. Use when value needs to change over time
4. Less preferred than val

### Type Inference

Both `val` and `var` work with type inference:

```kotlin
val name = "Alice"              // Type inferred as String
val age = 25                    // Type inferred as Int
val items = listOf(1, 2, 3)     // Type inferred as List<Int>

var counter = 0                 // Type inferred as Int
var text: String                // Type must be specified if not initialized
text = "Hello"
```

### Val is Not Deep Immutability

```kotlin
// Val means the reference is read-only, NOT the object
val person = Person("Alice", 25)
// person = Person("Bob", 30)    // Error: can't reassign reference
person.age = 26                  // OK if age is var

val numbers = mutableListOf(1, 2, 3)
// numbers = mutableListOf(4, 5) // Error: can't reassign reference
numbers.add(4)                   // OK: can modify contents
numbers.clear()                  // OK: can modify contents

// For true immutability, use immutable types
val immutableNumbers = listOf(1, 2, 3)
// immutableNumbers.add(4)       // Error: List<T> is immutable
```

### Custom Getters with Val

`val` can have custom getters, making it recompute on access:

```kotlin
class Rectangle(val width: Int, val height: Int) {
    val area: Int
        get() = width * height  // Computed each time
}

val rect = Rectangle(10, 20)
println(rect.area)  // 200

// Area is recomputed, not stored
```

### When to Use Val

#### DO use val when:

```kotlin
// 1. Value doesn't need to change
val pi = 3.14159
val appName = "MyApp"

// 2. Constructor parameters
class User(val id: Int, val name: String)

// 3. Function parameters (implicit val)
fun greet(name: String) {  // name is val by default
    // name = "Bob"  // Error
    println("Hello, $name")
}

// 4. Local variables that don't change
fun calculateTotal(items: List<Item>): Double {
    val subtotal = items.sumOf { it.price }
    val tax = subtotal * 0.1
    val total = subtotal + tax
    return total
}

// 5. Exposing read-only collections
class DataStore {
    private val _items = mutableListOf<String>()
    val items: List<String> = _items  // Exposed as read-only
}

// 6. Computed properties
class Circle(val radius: Double) {
    val area: Double
        get() = Math.PI * radius * radius
}
```

### When to Use Var

#### DO use var when:

```kotlin
// 1. Value needs to change over time
var counter = 0
counter++

// 2. Accumulating results in loops
var sum = 0
for (i in 1..10) {
    sum += i
}

// 3. State that changes
class Game {
    var score: Int = 0
    var isRunning: Boolean = false
}

// 4. Mutable UI state
class ViewModel {
    var isLoading: Boolean = false
    var errorMessage: String? = null
}

// 5. Builder pattern
class HttpRequestBuilder {
    var url: String = ""
    var method: String = "GET"
    var body: String? = null
}
```

### Val vs Var in Classes

```kotlin
// Primary constructor
class Person(
    val name: String,      // Read-only property
    var age: Int           // Mutable property
)

val person = Person("Alice", 25)
println(person.name)      // Alice
person.age = 26           // OK
// person.name = "Bob"    // Error

// Properties in class body
class User {
    val id: Int = generateId()          // Initialized once
    var username: String = ""            // Can be changed
    val createdAt: Long = System.currentTimeMillis()  // Initialized once

    private var _loginCount = 0          // Private mutable state
    val loginCount: Int                  // Public read-only
        get() = _loginCount
}
```

### Val vs Var with Nullable Types

```kotlin
val name: String? = null
// name = "Alice"  // Error: val cannot be reassigned

var username: String? = null
username = "Alice"  // OK
username = null     // OK

// Smart casts work better with val
fun printLength(text: String?) {
    if (text != null) {
        println(text.length)  // Smart cast to String
    }
}

val message: String? = getMessage()
if (message != null) {
    println(message.length)  // Smart cast works
}

var mutableMessage: String? = getMessage()
if (mutableMessage != null) {
    // println(mutableMessage.length)  // May not smart cast (could be changed by another thread)
}
```

### Val in Loops

```kotlin
// Loop variable is val (implicit)
for (item in items) {
    // item = something  // Error: loop variable is val
    println(item)
}

// Index in loop is val
for (i in 0..10) {
    // i = 5  // Error
    println(i)
}

// With while loop, use var
var i = 0
while (i < 10) {
    println(i)
    i++  // OK: i is var
}
```

### Val with Late Initialization

```kotlin
class MyTest {
    // lateinit works only with var
    lateinit var subject: TestSubject

    @Before
    fun setup() {
        subject = TestSubject()
    }
}

// For val, use lazy
class DatabaseManager {
    val connection: Connection by lazy {
        DriverManager.getConnection(DATABASE_URL)
    }
}
```

### Performance Considerations

```kotlin
// Val doesn't necessarily mean better performance
class Example {
    // Stored once, accessed many times
    val storedValue = expensiveComputation()

    // Computed every access
    val computedValue: Int
        get() = expensiveComputation()

    // Better for expensive computations accessed once
    val lazyValue: Int by lazy {
        expensiveComputation()
    }
}
```

### Best Practices

#### DO:
```kotlin
// Prefer val over var (immutability first)
val name = "Alice"
val age = 25

// Use var only when necessary
var counter = 0
counter++

// Use val for constructor parameters
class User(val id: Int, val name: String)

// Use backing property pattern for mutable state
class ViewModel {
    private val _state = MutableStateFlow<State>(State.Initial)
    val state: StateFlow<State> = _state.asStateFlow()
}

// Use val for constants
val MAX_RETRY_COUNT = 3
val DEFAULT_TIMEOUT = 5000

// Use descriptive names for mutable state
var isLoading = false
var currentIndex = 0
```

#### DON'T:
```kotlin
// Don't use var when val is sufficient
var name = "Alice"  // Bad if name never changes
val name = "Alice"  // Better

// Don't expose mutable state directly
class BadViewModel {
    var state = State.Initial  // Bad: external code can modify
}

// Don't use val for everything without thinking
class Counter {
    val count = 0  // Bad: count should be var
}

// Don't use var for constants
var PI = 3.14159  // Bad: should be val or const val
```

### Common Patterns

#### State Management

```kotlin
class ViewModel {
    // Internal mutable state
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)

    // External read-only state
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadData() {
        _uiState.value = UiState.Loading
        // ...
        _uiState.value = UiState.Success(data)
    }
}
```

#### Builder Pattern

```kotlin
class HttpRequest private constructor(
    val url: String,
    val method: String,
    val headers: Map<String, String>
) {
    class Builder {
        var url: String = ""
        var method: String = "GET"
        private val headers = mutableMapOf<String, String>()

        fun url(url: String) = apply { this.url = url }
        fun method(method: String) = apply { this.method = method }
        fun header(key: String, value: String) = apply {
            headers[key] = value
        }

        fun build(): HttpRequest {
            require(url.isNotBlank()) { "URL required" }
            return HttpRequest(url, method, headers)
        }
    }
}
```

#### Lazy Initialization

```kotlin
class ResourceManager {
    // Initialized on first access
    val database: Database by lazy {
        Database.connect(DATABASE_URL)
    }

    // Always mutable
    var cacheSize: Int = 100
}
```

### Val vs Const Val

```kotlin
// const val: Compile-time constant
const val MAX_SIZE = 100
const val API_KEY = "secret"

// val: Runtime constant
val timestamp = System.currentTimeMillis()
val random = Random.nextInt()

class Config {
    companion object {
        const val VERSION = "1.0"  // Compile-time constant
        val BUILD_TIME = System.currentTimeMillis()  // Runtime constant
    }
}
```

### Real-World Examples

#### Data Class

```kotlin
data class User(
    val id: Int,              // Immutable
    val email: String,        // Immutable
    var username: String,     // Can be changed
    var lastLogin: Long       // Can be updated
)

val user = User(1, "user@test.com", "alice", System.currentTimeMillis())
// user.id = 2           // Error: val
// user.email = "new"    // Error: val
user.username = "bob"    // OK: var
user.lastLogin = System.currentTimeMillis()  // OK: var
```

#### Android ViewModel

```kotlin
class UserViewModel : ViewModel() {
    // Mutable state (private)
    private val _users = MutableLiveData<List<User>>()
    private val _isLoading = MutableLiveData<Boolean>()

    // Immutable state (public)
    val users: LiveData<List<User>> = _users
    val isLoading: LiveData<Boolean> = _isLoading

    fun loadUsers() {
        _isLoading.value = true
        viewModelScope.launch {
            val result = repository.getUsers()
            _users.value = result
            _isLoading.value = false
        }
    }
}
```

#### Configuration

```kotlin
class AppConfig {
    val apiUrl: String = BuildConfig.API_URL      // Immutable
    val appVersion: String = BuildConfig.VERSION  // Immutable

    var debugMode: Boolean = false                // Can be toggled
    var logLevel: LogLevel = LogLevel.INFO        // Can be changed
}
```

### Summary

| Aspect | val | var |
|--------|-----|-----|
| **Mutability** | Read-only reference | Mutable reference |
| **Reassignment** | Cannot be reassigned | Can be reassigned |
| **Initialization** | Once | Multiple times |
| **Preference** | Preferred (default choice) | Use when necessary |
| **Thread Safety** | Safer (reference won't change) | Less safe |
| **Smart Casts** | Works reliably | May not work |
| **Java Equivalent** | final | non-final |

**General Rule**: Start with `val`, change to `var` only if you need mutability.

---

## Ответ (RU)

`val` и `var` — ключевые слова для объявления переменных/свойств в Kotlin. Понимание когда использовать каждое из них фундаментально для написания идиоматичного, безопасного Kotlin кода.

### Основное различие

```kotlin
val name = "Alice"      // Только для чтения (неизменяемая ссылка)
var age = 25            // Изменяемая

// name = "Bob"         // Ошибка: Val нельзя переназначить
age = 26                // OK: Var можно переназначить
```

**val** = **value** = ссылка только для чтения (как `final` в Java)
**var** = **variable** = изменяемая ссылка

### Val: Ссылка только для чтения

```kotlin
val x = 10
// x = 20  // Ошибка компиляции

val list = mutableListOf(1, 2, 3)
list.add(4)                // OK: содержимое может меняться
// list = mutableListOf()  // Ошибка: ссылка не может меняться
```

**Ключевые моменты о val**:
1. Ссылку нельзя переназначить
2. Должна быть инициализирована при объявлении или в init блоке
3. Может быть присвоена только один раз
4. НЕ означает, что объект неизменяем
5. Предпочтительна в Kotlin (подход immutability-first)

### Var: Изменяемая ссылка

```kotlin
var counter = 0
counter = 1      // OK
counter = 2      // OK
counter += 10    // OK
```

**Ключевые моменты о var**:
1. Ссылку можно переназначить
2. Можно изменять после инициализации
3. Использовать когда значение нужно менять со временем
4. Менее предпочтительна чем val

### Val это не глубокая неизменяемость

```kotlin
// Val означает что ссылка только для чтения, НЕ объект
val person = Person("Alice", 25)
// person = Person("Bob", 30)    // Ошибка: нельзя переназначить ссылку
person.age = 26                  // OK если age это var

val numbers = mutableListOf(1, 2, 3)
// numbers = mutableListOf(4, 5) // Ошибка: нельзя переназначить ссылку
numbers.add(4)                   // OK: можно изменять содержимое
numbers.clear()                  // OK: можно изменять содержимое

// Для истинной неизменяемости используйте неизменяемые типы
val immutableNumbers = listOf(1, 2, 3)
// immutableNumbers.add(4)       // Ошибка: List<T> неизменяем
```

### Когда использовать Val

#### ИСПОЛЬЗОВАТЬ val когда:

```kotlin
// 1. Значение не нужно менять
val pi = 3.14159
val appName = "MyApp"

// 2. Параметры конструктора
class User(val id: Int, val name: String)

// 3. Параметры функции (неявно val)
fun greet(name: String) {  // name это val по умолчанию
    // name = "Bob"  // Ошибка
    println("Hello, $name")
}

// 4. Локальные переменные которые не меняются
fun calculateTotal(items: List<Item>): Double {
    val subtotal = items.sumOf { it.price }
    val tax = subtotal * 0.1
    val total = subtotal + tax
    return total
}

// 5. Предоставление коллекций только для чтения
class DataStore {
    private val _items = mutableListOf<String>()
    val items: List<String> = _items  // Открыто только для чтения
}
```

### Когда использовать Var

#### ИСПОЛЬЗОВАТЬ var когда:

```kotlin
// 1. Значение нужно менять со временем
var counter = 0
counter++

// 2. Накопление результатов в циклах
var sum = 0
for (i in 1..10) {
    sum += i
}

// 3. Состояние которое меняется
class Game {
    var score: Int = 0
    var isRunning: Boolean = false
}

// 4. Изменяемое состояние UI
class ViewModel {
    var isLoading: Boolean = false
    var errorMessage: String? = null
}
```

### Лучшие практики

#### ДЕЛАТЬ:
```kotlin
// Предпочитать val вместо var (immutability first)
val name = "Alice"
val age = 25

// Использовать var только когда необходимо
var counter = 0
counter++

// Использовать val для параметров конструктора
class User(val id: Int, val name: String)

// Использовать паттерн backing property для изменяемого состояния
class ViewModel {
    private val _state = MutableStateFlow<State>(State.Initial)
    val state: StateFlow<State> = _state.asStateFlow()
}
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не использовать var когда достаточно val
var name = "Alice"  // Плохо если name никогда не меняется
val name = "Alice"  // Лучше

// Не открывать изменяемое состояние напрямую
class BadViewModel {
    var state = State.Initial  // Плохо: внешний код может изменить
}

// Не использовать var для констант
var PI = 3.14159  // Плохо: должно быть val или const val
```

### Резюме

| Аспект | val | var |
|--------|-----|-----|
| **Изменяемость** | Только для чтения | Изменяемая |
| **Переназначение** | Нельзя переназначить | Можно переназначить |
| **Инициализация** | Один раз | Многократно |
| **Предпочтение** | Предпочтительна (выбор по умолчанию) | Использовать когда необходимо |
| **Потокобезопасность** | Безопаснее (ссылка не изменится) | Менее безопасна |
| **Smart Casts** | Работает надёжно | Может не работать |
| **Java Эквивалент** | final | non-final |

**Общее правило**: Начинайте с `val`, меняйте на `var` только если нужна изменяемость.

---

## References

- [Kotlin Basic Types](https://kotlinlang.org/docs/basic-types.html)
- [Kotlin Properties](https://kotlinlang.org/docs/properties.html)
- [Effective Kotlin - Item 1: Limit mutability](https://kt.academy/article/ek-mutability)

## Related Questions

- [[q-kotlin-properties--kotlin--easy]]
- [[q-kotlin-const--kotlin--easy]]
- [[q-kotlin-constructors--kotlin--easy]]
- [[q-lazy-vs-lateinit--kotlin--medium]]

## MOC Links

- [[moc-kotlin]]
