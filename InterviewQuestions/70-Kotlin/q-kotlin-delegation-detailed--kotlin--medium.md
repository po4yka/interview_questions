---
id: kotlin-043
title: "Kotlin Delegation Pattern Deep Dive / Паттерн делегирования в Kotlin - детально"
aliases: ["Kotlin Delegation Pattern Deep Dive", "Паттерн делегирования в Kotlin - детально"]

# Classification
topic: kotlin
subtopics: [by-keyword, delegates]
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
related: [c-kotlin, q-destructuring-declarations--kotlin--medium, q-infix-functions--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-11-09

tags: [by-keyword, delegates, delegation, difficulty/medium, kotlin, patterns]
date created: Sunday, October 12th 2025, 1:56:16 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---

# Вопрос (RU)
> Объясните паттерн делегирования в Kotlin детально. Что такое делегирование классов и делегирование свойств?

---

# Question (EN)
> Explain the delegation pattern in Kotlin in detail. What are class delegation and property delegation?
## Ответ (RU)

Kotlin предоставляет нативную поддержку **паттерна делегирования** через ключевое слово `by`, позволяя переиспользовать реализацию без наследования.

### Делегирование Классов

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
class CachedRepositoryManual(private val repo: Repository) : Repository {
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

**Преимущества:**
- Устраняет шаблонный код
- Поощряет композицию вместо наследования
- Позволяет переопределять отдельные методы при необходимости

### Делегирование Свойств

**Делегирует логику getter/setter свойства другому объекту.**

**Встроенные делегаты:**

**1. lazy - Ленивая инициализация**

```kotlin
class ExpensiveResource {
    val data: String by lazy {
        println("Вычисление дорогого значения...")
        loadFromNetwork()  // Вызывается только один раз при первом доступе
    }
}
```

**2. observable - Наблюдение за изменениями свойства**

```kotlin
class UserObservable {
    var name: String by Delegates.observable("<no name>") { prop, old, new ->
        println("$old -> $new")
    }
}

val userObservable = UserObservable()
userObservable.name = "Alice"  // Печатает: <no name> -> Alice
userObservable.name = "Bob"    // Печатает: Alice -> Bob
```

**3. vetoable - Вето на изменения свойства**

```kotlin
class Product {
    var price: Double by Delegates.vetoable(0.0) { prop, old, new ->
        new >= 0  // Разрешить только неотрицательные цены
    }
}
```

**4. notNull - Поздняя инициализация с проверкой**

```kotlin
class Config {
    var apiKey: String by Delegates.notNull()
}

val config = Config()
// config.apiKey  // Бросит IllegalStateException, если обратиться до инициализации
config.apiKey = "abc123"
println(config.apiKey)  // OK
```

### Пользовательский Делегат Свойства

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

class UserUppercase {
    var name: String by Uppercase()
}

val userUppercase = UserUppercase()
userUppercase.name = "alice"
println(userUppercase.name)  // Печатает: ALICE
```

### Примеры Из Реальной Практики

**Пример 1: `ViewModel` с делегированием**

```kotlin
interface UserRepository {
    fun getUser(): Flow<User>
    fun updateUser(user: User): Flow<Result<Unit>>
}

class UserViewModel(
    repository: UserRepository
) : ViewModel(), UserRepository by repository {
    // Все методы репозитория доступны без шаблонного кода

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

**Пример 2: Делегат `SharedPreferences` (поддерживает только конкретные типы)**

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
                else -> throw IllegalArgumentException("Unsupported type")
            }
        }
    }
}

class AppSettings(prefs: SharedPreferences) {
    var username: String by PreferenceDelegate("username", "", prefs)
    var darkMode: Boolean by PreferenceDelegate("dark_mode", false, prefs)
    var fontSize: Int by PreferenceDelegate("font_size", 14, prefs)
}
```

**Пример 3: Делегирование к `Map`**

```kotlin
class UserFromMap(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
    val email: String by map
}

val userFromMap = UserFromMap(mapOf(
    "name" to "Alice",
    "age" to 30,
    "email" to "alice@example.com"
))

println(userFromMap.name)  // Alice
println(userFromMap.age)   // 30
```

**Пример 4: Делегат валидации**

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

class UserValidated {
    var email: String by validated("Invalid email") { it.contains("@") }
    var age: Int by validated("Age must be positive") { it > 0 }
}
```

**Краткое содержание**: Делегирование в Kotlin: **Делегирование классов** (ключевое слово `by`) — делегирует реализацию интерфейса объекту, устраняет шаблонный код. **Делегирование свойств** — делегирует логику getter/setter. Встроенные: `lazy` (ленивая инициализация), `observable` (наблюдение за изменениями), `vetoable` (вето на изменения), `notNull` (поздняя инициализация). Пользовательские делегаты: реализуют `ReadOnlyProperty` / `ReadWriteProperty`. Применение: `SharedPreferences`, валидация, кэширование, композиция вместо наследования.

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
class CachedRepositoryManual(private val repo: Repository) : Repository {
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
- Eliminates boilerplate
- Encourages composition over inheritance
- Allows overriding specific methods when needed

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
class UserObservable {
    var name: String by Delegates.observable("<no name>") { prop, old, new ->
        println("$old -> $new")
    }
}

val user = UserObservable()
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

**Implement `ReadOnlyProperty` or `ReadWriteProperty`:**

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

class UserUppercase {
    var name: String by Uppercase()
}

val userUppercase = UserUppercase()
userUppercase.name = "alice"
println(userUppercase.name)  // Prints: ALICE
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

**Example 2: SharedPreferences delegate (supports only specific types)**

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
                else -> throw IllegalArgumentException("Unsupported type")
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
class UserFromMap(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
    val email: String by map
}

val userFromMap = UserFromMap(mapOf(
    "name" to "Alice",
    "age" to 30,
    "email" to "alice@example.com"
))

println(userFromMap.name)  // Alice
println(userFromMap.age)   // 30
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

class UserValidated {
    var email: String by validated("Invalid email") { it.contains("@") }
    var age: Int by validated("Age must be positive") { it > 0 }
}
```

**English Summary**: Kotlin delegation: **Class delegation** (`by` keyword) — delegates interface implementation to another object, eliminating boilerplate. **Property delegation** — delegates getter/setter logic. Built-in: `lazy` (lazy init), `observable` (observe changes), `vetoable` (veto changes), `notNull` (late init). Custom delegates: implement `ReadOnlyProperty` / `ReadWriteProperty`. Use cases: SharedPreferences, validation, caching, composition over inheritance.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия делегирования в Kotlin от подхода в Java?
- Когда вы бы использовали делегирование на практике?
- Какие распространенные подводные камни при использовании делегирования?

## Ссылки (RU)

- [[c-kotlin]]
- [Delegation - Kotlin Documentation](https://kotlinlang.org/docs/delegation.html)
- [Delegated Properties](https://kotlinlang.org/docs/delegated-properties.html)

## Связанные Вопросы (RU)

- [[q-kotlin-delegation--programming-languages--easy]]
- [[q-lazy-vs-lateinit--kotlin--medium]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Delegation - Kotlin Documentation](https://kotlinlang.org/docs/delegation.html)
- [Delegated Properties](https://kotlinlang.org/docs/delegated-properties.html)

## Related Questions
- [[q-kotlin-delegation--programming-languages--easy]]
- [[q-lazy-vs-lateinit--kotlin--medium]]
