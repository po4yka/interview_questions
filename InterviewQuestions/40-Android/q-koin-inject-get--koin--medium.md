---
id: android-koin-002
title: Koin by inject() vs get() / Koin by inject() против get()
aliases: [Koin inject, Koin get, Lazy Injection Koin]
topic: android
subtopics: [di-koin, dependency-injection]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-koin-setup-modules--koin--medium, q-koin-scopes--koin--medium, q-koin-viewmodel--koin--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/di-koin, dependency-injection, difficulty/medium, koin]
---
# Vopros (RU)
> В чем разница между by inject() и get() в Koin? Когда использовать каждый способ?

# Question (EN)
> What is the difference between by inject() and get() in Koin? When should you use each approach?

---

## Otvet (RU)

Koin предоставляет два основных способа получения зависимостей: **by inject()** (ленивая инъекция) и **get()** (немедленное получение).

### by inject() - Ленивая инъекция

**by inject()** использует Kotlin `lazy` делегат - зависимость создается только при первом обращении:

```kotlin
class UserActivity : AppCompatActivity(), KoinComponent {

    // Ленивая инъекция - создается при первом использовании
    private val userRepository: UserRepository by inject()
    private val analytics: Analytics by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // userRepository создается здесь при первом вызове
        val user = userRepository.getCurrentUser()
    }
}
```

#### Характеристики by inject()

```kotlin
class MyViewModel : ViewModel(), KoinComponent {

    // Все три свойства ленивые
    private val repo: UserRepository by inject()
    private val api: ApiService by inject()
    private val config: AppConfig by inject()

    fun loadData() {
        // repo создается только здесь, при первом вызове
        repo.getData()
    }

    fun callApi() {
        // api создается только здесь
        api.fetchData()
    }

    // config может никогда не создаться, если не используется
}
```

### get() - Немедленное получение

**get()** возвращает экземпляр сразу при вызове:

```kotlin
class UserActivity : AppCompatActivity(), KoinComponent {

    // Немедленное получение
    private val userRepository: UserRepository = get()

    // Или в методе
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val analytics: Analytics = get()
        analytics.logEvent("screen_opened")
    }
}
```

#### get() в определениях модулей

```kotlin
val appModule = module {
    single { Database() }
    single { UserDao(get()) }  // get() для получения Database

    single<UserRepository> {
        UserRepositoryImpl(
            dao = get(),        // UserDao
            api = get(),        // ApiService
            dispatcher = get()  // CoroutineDispatcher
        )
    }
}
```

### Сравнение

| Аспект | by inject() | get() |
|--------|-------------|-------|
| Момент создания | При первом обращении | Сразу при вызове |
| Тип | `Lazy<T>` делегат | Прямое значение `T` |
| Производительность | Отложенная инициализация | Немедленная инициализация |
| Использование | Свойства класса | Модули, методы, конструкторы |
| Thread-safety | Да (Kotlin lazy) | Зависит от контекста |

### Примеры использования

#### by inject() - для Activity/Fragment

```kotlin
class MainActivity : AppCompatActivity(), KoinComponent {

    // Рекомендуется для Activity - не блокирует onCreate
    private val viewModel: MainViewModel by inject()
    private val navigator: Navigator by inject()
    private val analytics: Analytics by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Зависимости создаются только при использовании
        viewModel.loadData()
    }
}
```

#### get() - для модулей и конструкторов

```kotlin
val repositoryModule = module {
    single { ApiClient() }
    single { LocalDatabase(androidContext()) }

    // get() в определениях модулей - стандартный подход
    single<UserRepository> {
        UserRepositoryImpl(
            apiClient = get(),
            database = get()
        )
    }

    factory {
        CreateUserUseCase(
            repository = get(),
            validator = get()
        )
    }
}
```

#### Смешанное использование

```kotlin
class ProfileFragment : Fragment(), KoinComponent {

    // Ленивая инъекция для тяжелых зависимостей
    private val imageLoader: ImageLoader by inject()
    private val analyticsTracker: AnalyticsTracker by inject()

    // Немедленное получение в методах
    fun updateProfile(userId: String) {
        val repository: UserRepository = get()
        val user = repository.getUser(userId)

        // Используем ленивые зависимости
        imageLoader.load(user.avatarUrl)
        analyticsTracker.trackProfileView(userId)
    }
}
```

### Именованные зависимости

```kotlin
val configModule = module {
    single(named("debug")) { DebugLogger() }
    single(named("release")) { ReleaseLogger() }
}

class MyService : KoinComponent {
    // by inject() с qualifier
    private val logger: Logger by inject(named("debug"))

    fun doWork() {
        // get() с qualifier
        val releaseLogger: Logger = get(named("release"))
    }
}
```

### KoinComponent интерфейс

Для использования `by inject()` и `get()` класс должен реализовать `KoinComponent`:

```kotlin
// Стандартный способ
class MyService : KoinComponent {
    private val repo: Repository by inject()
}

// Без KoinComponent - используйте GlobalContext
class PlainClass {
    private val repo: Repository = GlobalContext.get().get()
}

// В Compose - используйте koinInject()
@Composable
fun UserScreen() {
    val viewModel: UserViewModel = koinViewModel()
    val analytics: Analytics = koinInject()
}
```

### Когда использовать каждый подход

#### Используйте by inject() когда:

- Зависимость используется в свойстве класса
- Хотите отложить создание до первого использования
- Зависимость может быть не нужна в некоторых сценариях
- В Activity/Fragment для ускорения создания

#### Используйте get() когда:

- Внутри определений модулей Koin
- Нужен экземпляр немедленно в методе
- В конструкторах (хотя лучше передавать явно)
- Для одноразового использования

### Лучшие практики

```kotlin
// Хорошо: ленивая инъекция в Activity
class GoodActivity : AppCompatActivity(), KoinComponent {
    private val viewModel: MainViewModel by inject()
}

// Хорошо: get() в модулях
val goodModule = module {
    single { Repository(get(), get()) }
}

// Плохо: get() в свойстве - блокирует инициализацию
class BadActivity : AppCompatActivity(), KoinComponent {
    private val viewModel: MainViewModel = get() // Избегайте
}

// Хорошо: явная передача зависимостей
class UseCase(
    private val repository: Repository,
    private val validator: Validator
) {
    // Зависимости переданы через конструктор
}
```

---

## Answer (EN)

Koin provides two main ways to retrieve dependencies: **by inject()** (lazy injection) and **get()** (immediate retrieval).

### by inject() - Lazy Injection

**by inject()** uses Kotlin's `lazy` delegate - the dependency is created only on first access:

```kotlin
class UserActivity : AppCompatActivity(), KoinComponent {

    // Lazy injection - created on first use
    private val userRepository: UserRepository by inject()
    private val analytics: Analytics by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // userRepository is created here on first call
        val user = userRepository.getCurrentUser()
    }
}
```

#### Characteristics of by inject()

```kotlin
class MyViewModel : ViewModel(), KoinComponent {

    // All three properties are lazy
    private val repo: UserRepository by inject()
    private val api: ApiService by inject()
    private val config: AppConfig by inject()

    fun loadData() {
        // repo is created only here, on first call
        repo.getData()
    }

    fun callApi() {
        // api is created only here
        api.fetchData()
    }

    // config may never be created if not used
}
```

### get() - Immediate Retrieval

**get()** returns the instance immediately when called:

```kotlin
class UserActivity : AppCompatActivity(), KoinComponent {

    // Immediate retrieval
    private val userRepository: UserRepository = get()

    // Or in a method
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val analytics: Analytics = get()
        analytics.logEvent("screen_opened")
    }
}
```

#### get() in Module Definitions

```kotlin
val appModule = module {
    single { Database() }
    single { UserDao(get()) }  // get() to retrieve Database

    single<UserRepository> {
        UserRepositoryImpl(
            dao = get(),        // UserDao
            api = get(),        // ApiService
            dispatcher = get()  // CoroutineDispatcher
        )
    }
}
```

### Comparison

| Aspect | by inject() | get() |
|--------|-------------|-------|
| Creation time | On first access | Immediately on call |
| Type | `Lazy<T>` delegate | Direct value `T` |
| Performance | Deferred initialization | Immediate initialization |
| Usage | Class properties | Modules, methods, constructors |
| Thread-safety | Yes (Kotlin lazy) | Depends on context |

### Usage Examples

#### by inject() - for Activity/Fragment

```kotlin
class MainActivity : AppCompatActivity(), KoinComponent {

    // Recommended for Activity - doesn't block onCreate
    private val viewModel: MainViewModel by inject()
    private val navigator: Navigator by inject()
    private val analytics: Analytics by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Dependencies created only when used
        viewModel.loadData()
    }
}
```

#### get() - for Modules and Constructors

```kotlin
val repositoryModule = module {
    single { ApiClient() }
    single { LocalDatabase(androidContext()) }

    // get() in module definitions - standard approach
    single<UserRepository> {
        UserRepositoryImpl(
            apiClient = get(),
            database = get()
        )
    }

    factory {
        CreateUserUseCase(
            repository = get(),
            validator = get()
        )
    }
}
```

#### Mixed Usage

```kotlin
class ProfileFragment : Fragment(), KoinComponent {

    // Lazy injection for heavy dependencies
    private val imageLoader: ImageLoader by inject()
    private val analyticsTracker: AnalyticsTracker by inject()

    // Immediate retrieval in methods
    fun updateProfile(userId: String) {
        val repository: UserRepository = get()
        val user = repository.getUser(userId)

        // Use lazy dependencies
        imageLoader.load(user.avatarUrl)
        analyticsTracker.trackProfileView(userId)
    }
}
```

### Named Dependencies

```kotlin
val configModule = module {
    single(named("debug")) { DebugLogger() }
    single(named("release")) { ReleaseLogger() }
}

class MyService : KoinComponent {
    // by inject() with qualifier
    private val logger: Logger by inject(named("debug"))

    fun doWork() {
        // get() with qualifier
        val releaseLogger: Logger = get(named("release"))
    }
}
```

### KoinComponent Interface

To use `by inject()` and `get()`, a class must implement `KoinComponent`:

```kotlin
// Standard way
class MyService : KoinComponent {
    private val repo: Repository by inject()
}

// Without KoinComponent - use GlobalContext
class PlainClass {
    private val repo: Repository = GlobalContext.get().get()
}

// In Compose - use koinInject()
@Composable
fun UserScreen() {
    val viewModel: UserViewModel = koinViewModel()
    val analytics: Analytics = koinInject()
}
```

### When to Use Each Approach

#### Use by inject() when:

- Dependency is used in a class property
- You want to defer creation until first use
- Dependency may not be needed in some scenarios
- In Activity/Fragment to speed up creation

#### Use get() when:

- Inside Koin module definitions
- You need the instance immediately in a method
- In constructors (though explicit passing is better)
- For one-time use

### Best Practices

```kotlin
// Good: lazy injection in Activity
class GoodActivity : AppCompatActivity(), KoinComponent {
    private val viewModel: MainViewModel by inject()
}

// Good: get() in modules
val goodModule = module {
    single { Repository(get(), get()) }
}

// Bad: get() in property - blocks initialization
class BadActivity : AppCompatActivity(), KoinComponent {
    private val viewModel: MainViewModel = get() // Avoid
}

// Good: explicit dependency passing
class UseCase(
    private val repository: Repository,
    private val validator: Validator
) {
    // Dependencies passed through constructor
}
```

---

## Dopolnitelnye Voprosy (RU)

- Как работает lazy делегат в Kotlin и почему by inject() потокобезопасен?
- Можно ли использовать by inject() без KoinComponent?
- Как обрабатывать ошибки при отсутствии зависимости?

## Follow-ups

- How does the lazy delegate work in Kotlin and why is by inject() thread-safe?
- Can you use by inject() without KoinComponent?
- How do you handle errors when a dependency is missing?

## Ssylki (RU)

- [Koin Injection](https://insert-koin.io/docs/reference/koin-core/injection-parameters)
- [KoinComponent](https://insert-koin.io/docs/reference/koin-core/koin-component)

## References

- [Koin Injection](https://insert-koin.io/docs/reference/koin-core/injection-parameters)
- [KoinComponent](https://insert-koin.io/docs/reference/koin-core/koin-component)

## Svyazannye Voprosy (RU)

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-koin-scopes--koin--medium]]
- [[q-koin-parameters--koin--medium]]

## Related Questions

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-koin-scopes--koin--medium]]
- [[q-koin-parameters--koin--medium]]
