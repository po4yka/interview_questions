---
id: android-koin-005
title: Koin parametersOf / Параметры в Koin
aliases:
- Koin Parameters
- parametersOf
- Runtime Dependencies
topic: android
subtopics:
- di-koin
- dependency-injection
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-koin-setup-modules--koin--medium
- q-koin-inject-get--koin--medium
- q-koin-viewmodel--koin--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-koin
- dependency-injection
- difficulty/medium
- koin
anki_cards:
- slug: android-koin-005-0-en
  language: en
- slug: android-koin-005-0-ru
  language: ru
---
# Vopros (RU)
> Как передавать runtime-параметры в зависимости Koin с помощью parametersOf?

# Question (EN)
> How do you pass runtime parameters to Koin dependencies using parametersOf?

---

## Otvet (RU)

**parametersOf** позволяет передавать динамические параметры в зависимости во время выполнения. Это полезно когда некоторые значения известны только в runtime (например, userId, настройки экрана).

### Базовое использование

```kotlin
// Определение в модуле
val appModule = module {
    // Один параметр
    factory { (name: String) ->
        Logger(name)
    }

    // Несколько параметров
    factory { (userId: String, token: String) ->
        UserSession(userId, token)
    }
}

// Использование
class MyService : KoinComponent {
    fun createLogger() {
        // Передача параметра через parametersOf
        val logger: Logger = get { parametersOf("MyService") }
    }

    fun startSession(userId: String, token: String) {
        val session: UserSession = get {
            parametersOf(userId, token)
        }
    }
}
```

### Деструктуризация параметров

```kotlin
val module = module {
    // Деструктуризация в лямбде
    factory { (id: String, name: String, age: Int) ->
        User(id = id, name = name, age = age)
    }

    // Альтернативный синтаксис с params
    factory { params ->
        val id: String = params[0]
        val name: String = params[1]
        val age: Int = params[2]
        User(id, name, age)
    }

    // Использование get() на params
    factory { params ->
        User(
            id = params.get(),      // Первый String
            name = params.get(),    // Второй String
            age = params.get()      // Int
        )
    }
}
```

### parametersOf с inject()

```kotlin
class UserActivity : AppCompatActivity(), KoinComponent {

    // Ленивая инъекция с параметрами
    private val userSession: UserSession by inject {
        parametersOf(
            intent.getStringExtra("USER_ID") ?: "",
            intent.getStringExtra("TOKEN") ?: ""
        )
    }

    // ViewModel с параметрами
    private val viewModel: UserViewModel by viewModel {
        parametersOf(intent.getStringExtra("USER_ID"))
    }
}
```

### Комбинирование с get()

```kotlin
val repositoryModule = module {
    single { ApiClient() }
    single { Database() }

    // Параметр + зависимости через get()
    factory { (userId: String) ->
        UserRepository(
            userId = userId,           // Runtime параметр
            apiClient = get(),         // Из Koin
            database = get()           // Из Koin
        )
    }
}

// Использование
val repository: UserRepository = get { parametersOf("user_123") }
```

### Nullable параметры

```kotlin
val module = module {
    factory { (config: Config?) ->
        ServiceClient(config ?: Config.default())
    }
}

// Можно передать null
val client: ServiceClient = get { parametersOf(null) }
```

### Параметры в ViewModel

```kotlin
val viewModelModule = module {
    // ViewModel с обязательным параметром
    viewModel { (productId: String) ->
        ProductDetailViewModel(
            productId = productId,
            repository = get()
        )
    }

    // ViewModel с несколькими параметрами
    viewModel { (userId: String, isEditing: Boolean) ->
        ProfileViewModel(
            userId = userId,
            isEditing = isEditing,
            repository = get(),
            analytics = get()
        )
    }
}

// В Activity
class ProductActivity : AppCompatActivity() {
    private val viewModel: ProductDetailViewModel by viewModel {
        parametersOf(intent.getStringExtra("PRODUCT_ID"))
    }
}

// В Compose
@Composable
fun ProductScreen(productId: String) {
    val viewModel: ProductDetailViewModel = koinViewModel {
        parametersOf(productId)
    }
}
```

### Типизированные параметры

```kotlin
// Data class для группировки параметров
data class UserParams(
    val id: String,
    val name: String,
    val email: String
)

val module = module {
    factory { (params: UserParams) ->
        UserProfile(
            id = params.id,
            name = params.name,
            email = params.email
        )
    }
}

// Использование
val params = UserParams("1", "John", "john@example.com")
val profile: UserProfile = get { parametersOf(params) }
```

### Параметры в Scopes

```kotlin
val sessionModule = module {
    scope(named("user_session")) {
        // Scoped зависимость с параметрами
        scoped { (userId: String) ->
            UserPreferences(userId)
        }

        scoped { (userId: String) ->
            UserRepository(userId, get())
        }
    }
}

// Создание scope и получение зависимости
val scope = getKoin().createScope("session_1", named("user_session"))
val prefs = scope.get<UserPreferences> { parametersOf("user_123") }
```

### Параметры с Assisted Injection pattern

```kotlin
// Интерфейс фабрики
interface UserViewModelFactory {
    fun create(userId: String): UserViewModel
}

val module = module {
    // Фабрика использует parametersOf внутри
    single<UserViewModelFactory> {
        object : UserViewModelFactory {
            override fun create(userId: String): UserViewModel {
                return get { parametersOf(userId) }
            }
        }
    }

    factory { (userId: String) ->
        UserViewModel(userId, get())
    }
}

// Использование фабрики
class UserFragment : Fragment(), KoinComponent {
    private val factory: UserViewModelFactory by inject()

    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val userId = requireArguments().getString("USER_ID")!!
        viewModel = factory.create(userId)
    }
}
```

### Ошибки и отладка

```kotlin
// Ошибка: неправильное количество параметров
val module = module {
    factory { (a: String, b: Int) -> MyClass(a, b) }
}

// Runtime error - передали 1 параметр вместо 2
val instance: MyClass = get { parametersOf("only_one") } // Crash!

// Правильно
val instance: MyClass = get { parametersOf("first", 42) }

// Проверка с logging
startKoin {
    androidLogger(Level.DEBUG) // Покажет ошибки параметров
    modules(module)
}
```

### Лучшие практики

1. **Минимизируйте количество параметров** - лучше 1-2, не больше 3
2. **Используйте data class** для группировки связанных параметров
3. **Предпочитайте конструктор injection** когда возможно
4. **Документируйте параметры** - какие и в каком порядке
5. **Типобезопасность** - используйте явную деструктуризацию

```kotlin
// Хорошо: один значимый параметр
factory { (userId: String) -> UserRepository(userId, get()) }

// Хорошо: data class для группы параметров
data class OrderParams(val orderId: String, val customerId: String)
factory { (params: OrderParams) -> OrderProcessor(params, get()) }

// Плохо: много разрозненных параметров
factory { (a: String, b: Int, c: Boolean, d: Long) -> ... }
```

---

## Answer (EN)

**parametersOf** allows passing dynamic parameters to dependencies at runtime. This is useful when some values are only known at runtime (e.g., userId, screen settings).

### Basic Usage

```kotlin
// Definition in module
val appModule = module {
    // Single parameter
    factory { (name: String) ->
        Logger(name)
    }

    // Multiple parameters
    factory { (userId: String, token: String) ->
        UserSession(userId, token)
    }
}

// Usage
class MyService : KoinComponent {
    fun createLogger() {
        // Pass parameter via parametersOf
        val logger: Logger = get { parametersOf("MyService") }
    }

    fun startSession(userId: String, token: String) {
        val session: UserSession = get {
            parametersOf(userId, token)
        }
    }
}
```

### Parameter Destructuring

```kotlin
val module = module {
    // Destructuring in lambda
    factory { (id: String, name: String, age: Int) ->
        User(id = id, name = name, age = age)
    }

    // Alternative syntax with params
    factory { params ->
        val id: String = params[0]
        val name: String = params[1]
        val age: Int = params[2]
        User(id, name, age)
    }

    // Using get() on params
    factory { params ->
        User(
            id = params.get(),      // First String
            name = params.get(),    // Second String
            age = params.get()      // Int
        )
    }
}
```

### parametersOf with inject()

```kotlin
class UserActivity : AppCompatActivity(), KoinComponent {

    // Lazy injection with parameters
    private val userSession: UserSession by inject {
        parametersOf(
            intent.getStringExtra("USER_ID") ?: "",
            intent.getStringExtra("TOKEN") ?: ""
        )
    }

    // ViewModel with parameters
    private val viewModel: UserViewModel by viewModel {
        parametersOf(intent.getStringExtra("USER_ID"))
    }
}
```

### Combining with get()

```kotlin
val repositoryModule = module {
    single { ApiClient() }
    single { Database() }

    // Parameter + dependencies via get()
    factory { (userId: String) ->
        UserRepository(
            userId = userId,           // Runtime parameter
            apiClient = get(),         // From Koin
            database = get()           // From Koin
        )
    }
}

// Usage
val repository: UserRepository = get { parametersOf("user_123") }
```

### Nullable Parameters

```kotlin
val module = module {
    factory { (config: Config?) ->
        ServiceClient(config ?: Config.default())
    }
}

// Can pass null
val client: ServiceClient = get { parametersOf(null) }
```

### Parameters in ViewModel

```kotlin
val viewModelModule = module {
    // ViewModel with required parameter
    viewModel { (productId: String) ->
        ProductDetailViewModel(
            productId = productId,
            repository = get()
        )
    }

    // ViewModel with multiple parameters
    viewModel { (userId: String, isEditing: Boolean) ->
        ProfileViewModel(
            userId = userId,
            isEditing = isEditing,
            repository = get(),
            analytics = get()
        )
    }
}

// In Activity
class ProductActivity : AppCompatActivity() {
    private val viewModel: ProductDetailViewModel by viewModel {
        parametersOf(intent.getStringExtra("PRODUCT_ID"))
    }
}

// In Compose
@Composable
fun ProductScreen(productId: String) {
    val viewModel: ProductDetailViewModel = koinViewModel {
        parametersOf(productId)
    }
}
```

### Typed Parameters

```kotlin
// Data class for grouping parameters
data class UserParams(
    val id: String,
    val name: String,
    val email: String
)

val module = module {
    factory { (params: UserParams) ->
        UserProfile(
            id = params.id,
            name = params.name,
            email = params.email
        )
    }
}

// Usage
val params = UserParams("1", "John", "john@example.com")
val profile: UserProfile = get { parametersOf(params) }
```

### Parameters in Scopes

```kotlin
val sessionModule = module {
    scope(named("user_session")) {
        // Scoped dependency with parameters
        scoped { (userId: String) ->
            UserPreferences(userId)
        }

        scoped { (userId: String) ->
            UserRepository(userId, get())
        }
    }
}

// Create scope and get dependency
val scope = getKoin().createScope("session_1", named("user_session"))
val prefs = scope.get<UserPreferences> { parametersOf("user_123") }
```

### Assisted Injection Pattern

```kotlin
// Factory interface
interface UserViewModelFactory {
    fun create(userId: String): UserViewModel
}

val module = module {
    // Factory uses parametersOf internally
    single<UserViewModelFactory> {
        object : UserViewModelFactory {
            override fun create(userId: String): UserViewModel {
                return get { parametersOf(userId) }
            }
        }
    }

    factory { (userId: String) ->
        UserViewModel(userId, get())
    }
}

// Using factory
class UserFragment : Fragment(), KoinComponent {
    private val factory: UserViewModelFactory by inject()

    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val userId = requireArguments().getString("USER_ID")!!
        viewModel = factory.create(userId)
    }
}
```

### Errors and Debugging

```kotlin
// Error: wrong number of parameters
val module = module {
    factory { (a: String, b: Int) -> MyClass(a, b) }
}

// Runtime error - passed 1 parameter instead of 2
val instance: MyClass = get { parametersOf("only_one") } // Crash!

// Correct
val instance: MyClass = get { parametersOf("first", 42) }

// Check with logging
startKoin {
    androidLogger(Level.DEBUG) // Will show parameter errors
    modules(module)
}
```

### Best Practices

1. **Minimize number of parameters** - prefer 1-2, max 3
2. **Use data class** for grouping related parameters
3. **Prefer constructor injection** when possible
4. **Document parameters** - which ones and in what order
5. **Type safety** - use explicit destructuring

```kotlin
// Good: single meaningful parameter
factory { (userId: String) -> UserRepository(userId, get()) }

// Good: data class for parameter group
data class OrderParams(val orderId: String, val customerId: String)
factory { (params: OrderParams) -> OrderProcessor(params, get()) }

// Bad: many scattered parameters
factory { (a: String, b: Int, c: Boolean, d: Long) -> ... }
```

---

## Dopolnitelnye Voprosy (RU)

- Как обрабатывать optional параметры в Koin?
- Можно ли использовать parametersOf с single определениями?
- Как реализовать assisted injection pattern в Koin?

## Follow-ups

- How do you handle optional parameters in Koin?
- Can you use parametersOf with single definitions?
- How do you implement assisted injection pattern in Koin?

## Ssylki (RU)

- [Koin Parameters](https://insert-koin.io/docs/reference/koin-core/injection-parameters)
- [Koin DSL](https://insert-koin.io/docs/reference/koin-core/dsl)

## References

- [Koin Parameters](https://insert-koin.io/docs/reference/koin-core/injection-parameters)
- [Koin DSL](https://insert-koin.io/docs/reference/koin-core/dsl)

## Svyazannye Voprosy (RU)

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-koin-viewmodel--koin--medium]]
- [[q-koin-inject-get--koin--medium]]

## Related Questions

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-koin-viewmodel--koin--medium]]
- [[q-koin-inject-get--koin--medium]]
