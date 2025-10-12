---
id: 20251012-002
title: "Kotlin Properties / Свойства в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [properties, getters, setters, backing-field, lateinit, delegated-properties]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Kotlin properties

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-val-vs-var--kotlin--easy, q-kotlin-constructors--kotlin--easy, q-property-delegates--kotlin--medium, q-kotlin-lateinit--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, properties, getters, setters, backing-field, lateinit, lazy, delegated-properties, difficulty/easy]
---

# Question (EN)
> What are properties in Kotlin? Explain val vs var, custom getters and setters, backing fields, lateinit, and property delegation basics.

# Вопрос (RU)
> Что такое свойства в Kotlin? Объясните val vs var, пользовательские геттеры и сеттеры, backing fields, lateinit и основы делегирования свойств.

---

## Answer (EN)

Properties in Kotlin are first-class language features that replace Java's field + getter/setter pattern. They provide a concise syntax while maintaining encapsulation and allowing custom behavior.

### Key Concepts

1. **Val vs Var**: Immutable vs mutable properties
2. **Custom Getters/Setters**: Add logic when accessing/modifying properties
3. **Backing Fields**: Store property values using the `field` keyword
4. **Backing Properties**: Manual backing with private fields
5. **Lateinit**: Delayed initialization for non-null properties
6. **Lazy**: Initialization on first access
7. **Delegated Properties**: Delegate behavior to another object

### Val vs Var Properties

```kotlin
class Person {
    val name: String = "Alice"  // Read-only (immutable reference)
    var age: Int = 25           // Mutable
}

val person = Person()
println(person.name)      // OK
// person.name = "Bob"    // Error: Val cannot be reassigned

person.age = 26           // OK
println(person.age)
```

**Important**: `val` means the reference is immutable, not the object itself:

```kotlin
val list = mutableListOf(1, 2, 3)
// list = mutableListOf(4, 5, 6)  // Error: can't reassign
list.add(4)                        // OK: can modify contents

val person = Person("Alice", 25)
// person = Person("Bob", 30)     // Error: can't reassign
person.age = 26                    // OK: if age is var
```

### Property Declaration Syntax

```kotlin
class User {
    // Full syntax
    var name: String = ""
        get() = field
        set(value) {
            field = value
        }

    // Compact syntax (equivalent to above)
    var email: String = ""

    // Read-only property with getter
    val fullName: String
        get() = "$firstName $lastName"

    var firstName: String = ""
    var lastName: String = ""
}
```

### Custom Getters

```kotlin
class Rectangle(val width: Int, val height: Int) {
    // Computed property (no backing field)
    val area: Int
        get() = width * height

    // Alternative single-expression syntax
    val perimeter: Int get() = 2 * (width + height)

    val isSquare: Boolean
        get() = width == height
}

val rect = Rectangle(10, 20)
println(rect.area)       // 200 (computed each time)
println(rect.perimeter)  // 60
println(rect.isSquare)   // false
```

### Custom Setters

```kotlin
class User {
    var name: String = ""
        set(value) {
            println("Setting name to: $value")
            field = value.trim().capitalize()
        }

    var age: Int = 0
        set(value) {
            require(value >= 0) { "Age cannot be negative" }
            field = value
        }
}

val user = User()
user.name = "  alice  "  // Prints: Setting name to:   alice
println(user.name)        // Alice (trimmed and capitalized)

user.age = 25             // OK
// user.age = -5          // Throws: Age cannot be negative
```

### Backing Fields

The `field` keyword refers to the backing field that stores the property value:

```kotlin
class Counter {
    var count: Int = 0
        get() = field
        set(value) {
            if (value >= 0) {
                field = value
            }
        }
}

// Property without backing field (computed)
class Circle(val radius: Double) {
    val area: Double
        get() = Math.PI * radius * radius
    // No 'field' used - area is computed, not stored
}
```

**When backing field is created**:
- A property has a default getter/setter, OR
- Custom accessor references `field`

**No backing field when**:
- Property only has a custom getter that doesn't use `field`
- Property is declared with `by` (delegated)

```kotlin
class Example {
    var stored: Int = 0           // Has backing field

    val computed: Int             // No backing field
        get() = stored * 2

    var withField: Int = 0        // Has backing field
        set(value) {
            field = value * 2     // Uses 'field'
        }

    val noField: Int              // No backing field
        get() = 42                // Doesn't use 'field'
}
```

### Backing Properties

When you need more control, use a private backing property:

```kotlin
class StringRepository {
    private val _strings = mutableListOf<String>()

    // Public read-only access
    val strings: List<String>
        get() = _strings

    fun addString(s: String) {
        _strings.add(s)
    }
}

val repo = StringRepository()
repo.addString("Hello")
println(repo.strings)        // [Hello]
// repo.strings.add("World") // Error: List is read-only
```

### Late-Initialized Properties (lateinit)

Use `lateinit` for non-null properties that can't be initialized in the constructor:

```kotlin
class MyTest {
    lateinit var subject: TestSubject

    @Before
    fun setup() {
        subject = TestSubject()
    }

    @Test
    fun test() {
        subject.doSomething()  // Safe to use
    }
}

// Android example
class MyActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }
}
```

**lateinit requirements**:
- Must be `var` (not `val`)
- Must be non-null type
- Cannot be primitive type (Int, Boolean, etc.)
- Cannot have custom getter/setter

**Checking if lateinit is initialized**:

```kotlin
class Example {
    lateinit var text: String

    fun doSomething() {
        if (::text.isInitialized) {
            println(text)
        } else {
            println("Not initialized yet")
        }
    }
}
```

### Lazy Properties

Use `lazy` for properties that should be initialized on first access:

```kotlin
class ExpensiveResource {
    // Initialized only when first accessed
    val data: String by lazy {
        println("Computing data...")
        // Expensive computation
        "Computed result"
    }
}

val resource = ExpensiveResource()
println("Before accessing data")
println(resource.data)  // Prints: Computing data... \n Computed result
println(resource.data)  // Prints: Computed result (not recomputed)
```

**lazy characteristics**:
- Thread-safe by default
- Initialized only once
- Must be `val` (not `var`)
- Initialization block runs on first access

```kotlin
class DatabaseConnection(val url: String) {
    val connection: Connection by lazy {
        println("Opening connection to $url")
        DriverManager.getConnection(url)
    }

    val metadata: DatabaseMetaData by lazy {
        connection.metaData
    }
}

val db = DatabaseConnection("jdbc:sqlite:test.db")
// Nothing printed yet

println("About to use connection")
db.connection.prepareStatement("SELECT * FROM users")
// Prints: Opening connection to jdbc:sqlite:test.db

db.connection.prepareStatement("SELECT * FROM products")
// Connection already initialized, no additional output
```

### Delegated Properties

Kotlin allows delegating property implementation to another object:

```kotlin
import kotlin.properties.Delegates

class User {
    // Observable property
    var name: String by Delegates.observable("Initial") { property, oldValue, newValue ->
        println("${property.name} changed from $oldValue to $newValue")
    }

    // Vetoable property
    var age: Int by Delegates.vetoable(0) { property, oldValue, newValue ->
        newValue >= 0  // Only allow non-negative values
    }
}

val user = User()
user.name = "Alice"  // Prints: name changed from Initial to Alice
user.name = "Bob"    // Prints: name changed from Alice to Bob

user.age = 25        // OK
user.age = -5        // Silently rejected (age stays 25)
println(user.age)    // 25
```

### Property Visibility

```kotlin
class User {
    // Public property
    var name: String = ""

    // Private property
    private var password: String = ""

    // Public getter, private setter
    var email: String = ""
        private set

    // Internal property
    internal var internalId: Int = 0

    fun updateEmail(newEmail: String) {
        if (newEmail.contains("@")) {
            email = newEmail
        }
    }
}

val user = User()
user.name = "Alice"           // OK
// user.password = "secret"   // Error: private
user.email                     // OK: can read
// user.email = "new@test"    // Error: setter is private
user.updateEmail("new@test")  // OK
```

### Property Types

#### Stored Property
```kotlin
class User {
    var name: String = "Unknown"  // Backing field exists
}
```

#### Computed Property
```kotlin
class Rectangle(val width: Int, val height: Int) {
    val area: Int                 // No backing field
        get() = width * height
}
```

#### Property with Backing Property
```kotlin
class Repository {
    private val _items = mutableListOf<String>()
    val items: List<String>
        get() = _items
}
```

### Real-World Examples

#### ViewModel Property Pattern

```kotlin
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                _users.value = repository.getUsers()
            } finally {
                _isLoading.value = false
            }
        }
    }
}
```

#### Configuration with Validation

```kotlin
class ServerConfig {
    var host: String = "localhost"
        set(value) {
            require(value.isNotBlank()) { "Host cannot be blank" }
            field = value
        }

    var port: Int = 8080
        set(value) {
            require(value in 1..65535) { "Invalid port: $value" }
            field = value
        }

    val url: String
        get() = "http://$host:$port"
}

val config = ServerConfig()
config.host = "api.example.com"
config.port = 443
println(config.url)  // http://api.example.com:443
```

#### Cached Property

```kotlin
class ExpensiveCalculation(val input: Int) {
    val result: Int by lazy {
        println("Computing result for $input...")
        Thread.sleep(1000)  // Simulate expensive operation
        input * input
    }
}

val calc = ExpensiveCalculation(10)
println("Created calculator")
println(calc.result)  // Prints: Computing... then 100
println(calc.result)  // Prints: 100 (cached)
```

#### Property with Side Effects

```kotlin
class Logger {
    var level: LogLevel = LogLevel.INFO
        set(value) {
            println("Changing log level from $field to $value")
            field = value
            notifyListeners(value)
        }

    private fun notifyListeners(level: LogLevel) {
        // Notify observers of log level change
    }
}
```

### Best Practices

#### DO:
```kotlin
// Use val for immutable properties
class Person(val name: String, val birthYear: Int) {
    val age: Int
        get() = Calendar.getInstance().get(Calendar.YEAR) - birthYear
}

// Use backing properties for mutable collections
class DataStore {
    private val _items = mutableListOf<String>()
    val items: List<String> get() = _items
}

// Use lateinit for dependency injection
class Repository {
    @Inject
    lateinit var api: ApiService
}

// Use lazy for expensive initialization
class DatabaseManager {
    private val connection: Connection by lazy {
        DriverManager.getConnection(DATABASE_URL)
    }
}

// Validate in setters
class User {
    var age: Int = 0
        set(value) {
            require(value >= 0) { "Age must be non-negative" }
            field = value
        }
}
```

#### DON'T:
```kotlin
// Don't use var when val works
class Point(var x: Int, var y: Int)  // Bad if coordinates don't change
class Point(val x: Int, val y: Int)  // Better

// Don't access backing field in getter without good reason
var name: String = ""
    get() = field  // Unnecessary - default behavior

// Don't use lateinit for nullable types
lateinit var text: String?  // Error: lateinit cannot be nullable
var text: String? = null    // Use nullable instead

// Don't compute expensive operations in getters repeatedly
val data: List<String>
    get() = database.query()  // Bad: queries DB every time
// Use lazy or caching instead

// Don't expose mutable collections directly
val items = mutableListOf<String>()  // Bad: external code can modify
// Use backing property pattern instead
```

### Common Patterns

#### Singleton with lazy

```kotlin
object Database {
    val connection: Connection by lazy {
        DriverManager.getConnection("jdbc:sqlite:app.db")
    }
}
```

#### Property Delegation Chain

```kotlin
class Preferences {
    var theme: String by PreferenceDelegate("theme", "light")
    var fontSize: Int by PreferenceDelegate("fontSize", 14)
}

class PreferenceDelegate<T>(
    private val key: String,
    private val defaultValue: T
) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T {
        // Read from SharedPreferences
        return defaultValue
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        // Write to SharedPreferences
    }
}
```

---

## Ответ (RU)

Свойства в Kotlin — это первоклассные языковые конструкции, заменяющие паттерн Java с полем + getter/setter. Они обеспечивают компактный синтаксис, сохраняя инкапсуляцию и позволяя настраивать поведение.

### Ключевые концепции

1. **Val vs Var**: Неизменяемые vs изменяемые свойства
2. **Пользовательские Getters/Setters**: Добавление логики при доступе/изменении
3. **Backing Fields**: Хранение значений с помощью ключевого слова `field`
4. **Backing Properties**: Ручное хранение с приватными полями
5. **Lateinit**: Отложенная инициализация для non-null свойств
6. **Lazy**: Инициализация при первом обращении
7. **Делегированные свойства**: Делегирование поведения другому объекту

### Val vs Var свойства

```kotlin
class Person {
    val name: String = "Alice"  // Только для чтения (неизменяемая ссылка)
    var age: Int = 25           // Изменяемое
}

val person = Person()
println(person.name)      // OK
// person.name = "Bob"    // Ошибка: Val нельзя переназначить

person.age = 26           // OK
println(person.age)
```

**Важно**: `val` означает, что ссылка неизменяема, а не сам объект:

```kotlin
val list = mutableListOf(1, 2, 3)
// list = mutableListOf(4, 5, 6)  // Ошибка: нельзя переназначить
list.add(4)                        // OK: можно изменить содержимое
```

### Пользовательские Getters

```kotlin
class Rectangle(val width: Int, val height: Int) {
    // Вычисляемое свойство (без backing field)
    val area: Int
        get() = width * height

    // Альтернативный синтаксис
    val perimeter: Int get() = 2 * (width + height)

    val isSquare: Boolean
        get() = width == height
}

val rect = Rectangle(10, 20)
println(rect.area)       // 200 (вычисляется каждый раз)
println(rect.perimeter)  // 60
println(rect.isSquare)   // false
```

### Пользовательские Setters

```kotlin
class User {
    var name: String = ""
        set(value) {
            println("Установка имени: $value")
            field = value.trim().capitalize()
        }

    var age: Int = 0
        set(value) {
            require(value >= 0) { "Возраст не может быть отрицательным" }
            field = value
        }
}

val user = User()
user.name = "  alice  "  // Выводит: Установка имени:   alice
println(user.name)        // Alice (обрезано и с заглавной)

user.age = 25             // OK
// user.age = -5          // Выбрасывает исключение
```

### Backing Fields

Ключевое слово `field` ссылается на backing field, который хранит значение свойства:

```kotlin
class Counter {
    var count: Int = 0
        get() = field
        set(value) {
            if (value >= 0) {
                field = value
            }
        }
}

// Свойство без backing field (вычисляемое)
class Circle(val radius: Double) {
    val area: Double
        get() = Math.PI * radius * radius
    // 'field' не используется - area вычисляется, не хранится
}
```

### Backing Properties

Когда нужен больший контроль, используйте приватное backing свойство:

```kotlin
class StringRepository {
    private val _strings = mutableListOf<String>()

    // Публичный доступ только для чтения
    val strings: List<String>
        get() = _strings

    fun addString(s: String) {
        _strings.add(s)
    }
}

val repo = StringRepository()
repo.addString("Hello")
println(repo.strings)        // [Hello]
// repo.strings.add("World") // Ошибка: List только для чтения
```

### Late-Initialized свойства (lateinit)

Используйте `lateinit` для non-null свойств, которые нельзя инициализировать в конструкторе:

```kotlin
class MyTest {
    lateinit var subject: TestSubject

    @Before
    fun setup() {
        subject = TestSubject()
    }

    @Test
    fun test() {
        subject.doSomething()  // Безопасно использовать
    }
}

// Android пример
class MyActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }
}
```

**Требования lateinit**:
- Должно быть `var` (не `val`)
- Должно быть non-null типом
- Не может быть примитивным типом (Int, Boolean и т.д.)
- Не может иметь пользовательский getter/setter

**Проверка инициализации lateinit**:

```kotlin
class Example {
    lateinit var text: String

    fun doSomething() {
        if (::text.isInitialized) {
            println(text)
        } else {
            println("Ещё не инициализировано")
        }
    }
}
```

### Lazy свойства

Используйте `lazy` для свойств, которые должны инициализироваться при первом обращении:

```kotlin
class ExpensiveResource {
    // Инициализируется только при первом обращении
    val data: String by lazy {
        println("Вычисление данных...")
        // Дорогостоящее вычисление
        "Вычисленный результат"
    }
}

val resource = ExpensiveResource()
println("Перед доступом к data")
println(resource.data)  // Выводит: Вычисление данных... \n Вычисленный результат
println(resource.data)  // Выводит: Вычисленный результат (не пересчитывается)
```

**Характеристики lazy**:
- Thread-safe по умолчанию
- Инициализируется только один раз
- Должно быть `val` (не `var`)
- Блок инициализации выполняется при первом обращении

### Делегированные свойства

Kotlin позволяет делегировать реализацию свойства другому объекту:

```kotlin
import kotlin.properties.Delegates

class User {
    // Наблюдаемое свойство
    var name: String by Delegates.observable("Initial") { property, oldValue, newValue ->
        println("${property.name} изменено с $oldValue на $newValue")
    }

    // Свойство с проверкой
    var age: Int by Delegates.vetoable(0) { property, oldValue, newValue ->
        newValue >= 0  // Разрешать только неотрицательные значения
    }
}

val user = User()
user.name = "Alice"  // Выводит: name изменено с Initial на Alice
user.name = "Bob"    // Выводит: name изменено с Alice на Bob

user.age = 25        // OK
user.age = -5        // Тихо отклоняется (age остаётся 25)
println(user.age)    // 25
```

### Видимость свойств

```kotlin
class User {
    // Публичное свойство
    var name: String = ""

    // Приватное свойство
    private var password: String = ""

    // Публичный getter, приватный setter
    var email: String = ""
        private set

    // Internal свойство
    internal var internalId: Int = 0

    fun updateEmail(newEmail: String) {
        if (newEmail.contains("@")) {
            email = newEmail
        }
    }
}

val user = User()
user.name = "Alice"           // OK
// user.password = "secret"   // Ошибка: приватное
user.email                     // OK: можно читать
// user.email = "new@test"    // Ошибка: setter приватный
user.updateEmail("new@test")  // OK
```

### Лучшие практики

#### ДЕЛАТЬ:
```kotlin
// Использовать val для неизменяемых свойств
class Person(val name: String, val birthYear: Int)

// Использовать backing properties для изменяемых коллекций
class DataStore {
    private val _items = mutableListOf<String>()
    val items: List<String> get() = _items
}

// Использовать lateinit для dependency injection
class Repository {
    @Inject
    lateinit var api: ApiService
}

// Валидировать в setters
class User {
    var age: Int = 0
        set(value) {
            require(value >= 0) { "Возраст должен быть неотрицательным" }
            field = value
        }
}
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не использовать var когда подходит val
class Point(var x: Int, var y: Int)  // Плохо если координаты не меняются
class Point(val x: Int, val y: Int)  // Лучше

// Не вычислять дорогостоящие операции в getters повторно
val data: List<String>
    get() = database.query()  // Плохо: запрос к БД каждый раз
// Использовать lazy или кеширование

// Не выставлять изменяемые коллекции напрямую
val items = mutableListOf<String>()  // Плохо: внешний код может изменить
// Использовать паттерн backing property
```

---

## References

- [Kotlin Properties](https://kotlinlang.org/docs/properties.html)
- [Delegated Properties](https://kotlinlang.org/docs/delegated-properties.html)
- [Kotlin Backing Fields](https://kotlinlang.org/docs/properties.html#backing-fields)

## Related Questions

- [[q-kotlin-val-vs-var--kotlin--easy]]
- [[q-kotlin-constructors--kotlin--easy]]
- [[q-property-delegates--kotlin--medium]]
- [[q-kotlin-lateinit--kotlin--medium]]
- [[q-lazy-vs-lateinit--kotlin--medium]]

## MOC Links

- [[moc-kotlin]]
