---
id: kotlin-043
title: "Kotlin Delegation Pattern Deep Dive / Паттерн делегирования в Kotlin - детально"
aliases: []

# Classification
topic: kotlin
subtopics: [delegation, by-keyword, delegates, patterns]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-infix-functions--kotlin--medium, q-destructuring-declarations--kotlin--medium, q-sequences-vs-collections-performance--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, delegation, by-keyword, delegates, patterns, difficulty/medium]
---
# Question (EN)
> Explain the delegation pattern in Kotlin in detail. What are class delegation and property delegation?
# Вопрос (RU)
> Объясните паттерн делегирования в Kotlin детально. Что такое делегирование классов и делегирование свойств?

---

## Answer (EN)

Kotlin provides native support for the **delegation pattern** through the `by` keyword, allowing implementation reuse without inheritance.

### Class Delegation

**Delegates interface implementation to another object.**

```kotlin
interface Repository {
    fun getData(): String
    fun saveData(data: String)
}

class RepositoryImpl : Repository {
    override fun getData() = "data"
    override fun saveData(data: String) { println("Saving: $data") }
}

// Without delegation - manual forwarding
class CachedRepository(private val repo: Repository) : Repository {
    override fun getData() = repo.getData()  // Boilerplate
    override fun saveData(data: String) = repo.saveData(data)  // Boilerplate
}

// With delegation - automatic forwarding
class CachedRepository(
    private val repo: Repository
) : Repository by repo {
    // All methods delegated automatically!
    // Can override specific methods if needed
    private val cache = mutableMapOf<String, String>()

    override fun getData(): String {
        return cache.getOrPut("data") {
            repo.getData()  // Delegate to original
        }
    }
}
```

**Benefits:**
- - Eliminates boilerplate
- - Composition over inheritance
- - Can override specific methods

### Property Delegation

**Delegates property getter/setter logic to another object.**

**Built-in delegates:**

**1. lazy - Lazy initialization**

```kotlin
class ExpensiveResource {
    val data: String by lazy {
        println("Computing expensive value...")
        loadFromNetwork()  // Only called once on first access
    }
}

val resource = ExpensiveResource()
// "Computing expensive value..." not printed yet
println(resource.data)  // Now it's computed
println(resource.data)  // Uses cached value
```

**2. observable - Observe property changes**

```kotlin
class User {
    var name: String by Delegates.observable("<no name>") { prop, old, new ->
        println("$old -> $new")
    }
}

val user = User()
user.name = "Alice"  // Prints: <no name> -> Alice
user.name = "Bob"    // Prints: Alice -> Bob
```

**3. vetoable - Veto property changes**

```kotlin
class Product {
    var price: Double by Delegates.vetoable(0.0) { prop, old, new ->
        new >= 0  // Only allow non-negative prices
    }
}

val product = Product()
product.price = 100.0  // OK
product.price = -50.0  // Rejected, stays 100.0
```

**4. notNull - Late initialization with null check**

```kotlin
class Config {
    var apiKey: String by Delegates.notNull()
}

val config = Config()
// config.apiKey  // Would throw IllegalStateException
config.apiKey = "abc123"
println(config.apiKey)  // OK
```

### Custom Property Delegate

**Implement ReadOnlyProperty or ReadWriteProperty:**

```kotlin
class Uppercase : ReadWriteProperty<Any?, String> {
    private var value: String = ""

    override fun getValue(thisRef: Any?, property: KProperty<*>): String {
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        this.value = value.uppercase()
    }
}

class User {
    var name: String by Uppercase()
}

val user = User()
user.name = "alice"
println(user.name)  // Prints: ALICE
```

### Real-World Examples

**Example 1: ViewModel with delegation**

```kotlin
interface UserRepository {
    fun getUser(): Flow<User>
    fun updateUser(user: User): Flow<Result<Unit>>
}

class UserViewModel(
    repository: UserRepository
) : ViewModel(), UserRepository by repository {
    // All repository methods available without boilerplate

    val user: StateFlow<User?> = getUser()
        .stateIn(viewModelScope, SharingStarted.Lazily, null)

    fun updateName(name: String) {
        viewModelScope.launch {
            user.value?.let { currentUser ->
                updateUser(currentUser.copy(name = name))
            }
        }
    }
}
```

**Example 2: SharedPreferences delegate**

```kotlin
class PreferenceDelegate<T>(
    private val key: String,
    private val defaultValue: T,
    private val prefs: SharedPreferences
) : ReadWriteProperty<Any?, T> {

    @Suppress("UNCHECKED_CAST")
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return when (defaultValue) {
            is String -> prefs.getString(key, defaultValue) as T
            is Int -> prefs.getInt(key, defaultValue) as T
            is Boolean -> prefs.getBoolean(key, defaultValue) as T
            else -> throw IllegalArgumentException("Unsupported type")
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        prefs.edit {
            when (value) {
                is String -> putString(key, value)
                is Int -> putInt(key, value)
                is Boolean -> putBoolean(key, value)
            }
        }
    }
}

class AppSettings(prefs: SharedPreferences) {
    var username: String by PreferenceDelegate("username", "", prefs)
    var darkMode: Boolean by PreferenceDelegate("dark_mode", false, prefs)
    var fontSize: Int by PreferenceDelegate("font_size", 14, prefs)
}

// Usage
val settings = AppSettings(sharedPreferences)
settings.username = "Alice"
println(settings.darkMode)
```

**Example 3: Map delegation**

```kotlin
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
    val email: String by map
}

val user = User(mapOf(
    "name" to "Alice",
    "age" to 30,
    "email" to "alice@example.com"
))

println(user.name)  // Alice
println(user.age)   // 30
```

**Example 4: Validation delegate**

```kotlin
class ValidatedProperty<T>(
    private val validator: (T) -> Boolean,
    private val errorMessage: String
) : ReadWriteProperty<Any?, T> {
    private lateinit var value: T

    override fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        require(validator(value)) { errorMessage }
        this.value = value
    }
}

fun <T> validated(errorMessage: String, validator: (T) -> Boolean) =
    ValidatedProperty(validator, errorMessage)

class User {
    var email: String by validated("Invalid email") {
        it.contains("@")
    }

    var age: Int by validated("Age must be positive") {
        it > 0
    }
}
```

**English Summary**: Kotlin delegation: **Class delegation** (`by` keyword) - delegates interface implementation to object, eliminates boilerplate. **Property delegation** - delegates getter/setter logic. Built-in: `lazy` (lazy init), `observable` (observe changes), `vetoable` (veto changes), `notNull` (late init). Custom delegates: implement ReadWriteProperty. Use cases: SharedPreferences, validation, caching, composition over inheritance.

## Ответ (RU)

Kotlin предоставляет нативную поддержку **паттерна делегирования** через ключевое слово `by`, позволяя переиспользовать реализацию без наследования.

### Делегирование классов

**Делегирует реализацию интерфейса другому объекту.**

```kotlin
interface Repository {
    fun getData(): String
    fun saveData(data: String)
}

class RepositoryImpl : Repository {
    override fun getData() = "data"
    override fun saveData(data: String) { println("Saving: $data") }
}

// Без делегирования - ручная переадресация
class CachedRepository(private val repo: Repository) : Repository {
    override fun getData() = repo.getData()  // Шаблонный код
    override fun saveData(data: String) = repo.saveData(data)  // Шаблонный код
}

// С делегированием - автоматическая переадресация
class CachedRepository(
    private val repo: Repository
) : Repository by repo {
    // Все методы делегированы автоматически!
    private val cache = mutableMapOf<String, String>()

    override fun getData(): String {
        return cache.getOrPut("data") {
            repo.getData()
        }
    }
}
```

### Делегирование свойств

**Делегирует логику getter/setter свойства другому объекту.**

**Встроенные делегаты:**

**1. lazy - Ленивая инициализация**

```kotlin
class ExpensiveResource {
    val data: String by lazy {
        println("Вычисление дорогого значения...")
        loadFromNetwork()  // Вызывается только раз при первом доступе
    }
}
```

**2. observable - Наблюдение за изменениями свойства**

```kotlin
class User {
    var name: String by Delegates.observable("<no name>") { prop, old, new ->
        println("$old -> $new")
    }
}

val user = User()
user.name = "Alice"  // Печатает: <no name> -> Alice
```

**3. vetoable - Вето на изменения свойства**

```kotlin
class Product {
    var price: Double by Delegates.vetoable(0.0) { prop, old, new ->
        new >= 0  // Разрешить только неотрицательные цены
    }
}
```

### Пользовательский делегат свойства

```kotlin
class Uppercase : ReadWriteProperty<Any?, String> {
    private var value: String = ""

    override fun getValue(thisRef: Any?, property: KProperty<*>): String {
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        this.value = value.uppercase()
    }
}

class User {
    var name: String by Uppercase()
}

val user = User()
user.name = "alice"
println(user.name)  // Печатает: ALICE
```

### Примеры из реальной практики

**Пример 1: SharedPreferences делегат**

```kotlin
class PreferenceDelegate<T>(
    private val key: String,
    private val defaultValue: T,
    private val prefs: SharedPreferences
) : ReadWriteProperty<Any?, T> {

    @Suppress("UNCHECKED_CAST")
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return when (defaultValue) {
            is String -> prefs.getString(key, defaultValue) as T
            is Int -> prefs.getInt(key, defaultValue) as T
            is Boolean -> prefs.getBoolean(key, defaultValue) as T
            else -> throw IllegalArgumentException("Unsupported type")
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        prefs.edit {
            when (value) {
                is String -> putString(key, value)
                is Int -> putInt(key, value)
                is Boolean -> putBoolean(key, value)
            }
        }
    }
}

class AppSettings(prefs: SharedPreferences) {
    var username: String by PreferenceDelegate("username", "", prefs)
    var darkMode: Boolean by PreferenceDelegate("dark_mode", false, prefs)
}
```

**Пример 2: Делегат валидации**

```kotlin
class ValidatedProperty<T>(
    private val validator: (T) -> Boolean,
    private val errorMessage: String
) : ReadWriteProperty<Any?, T> {
    private lateinit var value: T

    override fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        require(validator(value)) { errorMessage }
        this.value = value
    }
}

class User {
    var email: String by validated("Invalid email") { it.contains("@") }
    var age: Int by validated("Age must be positive") { it > 0 }
}
```

**Краткое содержание**: Делегирование в Kotlin: **Делегирование классов** (ключевое слово `by`) - делегирует реализацию интерфейса объекту, устраняет шаблонный код. **Делегирование свойств** - делегирует логику getter/setter. Встроенные: `lazy` (ленивая инициализация), `observable` (наблюдение за изменениями), `vetoable` (вето на изменения), `notNull` (поздняя инициализация). Пользовательские делегаты: реализуют ReadWriteProperty. Применение: SharedPreferences, валидация, кэширование, композиция вместо наследования.

---

## References
- [Delegation - Kotlin Documentation](https://kotlinlang.org/docs/delegation.html)
- [Delegated Properties](https://kotlinlang.org/docs/delegated-properties.html)

## Related Questions
- [[q-kotlin-delegation--programming-languages--easy]]
- [[q-lazy-vs-lateinit--kotlin--medium]]
