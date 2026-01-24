---
id: android-koin-001
title: Koin Setup and Modules / Настройка Koin и модули
aliases: [Koin Setup, Koin Modules, startKoin, module DSL]
topic: android
subtopics: [di-koin, dependency-injection]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-koin-inject-get--koin--medium, q-koin-scopes--koin--medium, q-koin-viewmodel--koin--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/di-koin, dependency-injection, difficulty/medium, koin]
---
# Vopros (RU)
> Как настроить Koin в Android-приложении? Объясните startKoin, module DSL, single, factory и другие определения.

# Question (EN)
> How do you set up Koin in an Android application? Explain startKoin, module DSL, single, factory, and other definitions.

---

## Otvet (RU)

**Koin** - это легковесный фреймворк dependency injection для Kotlin, использующий DSL вместо кодогенерации. Он прост в настройке и не требует аннотаций.

### Подключение Koin

```kotlin
// build.gradle.kts (Module)
dependencies {
    // Core
    implementation("io.insert-koin:koin-core:3.5.6")

    // Android
    implementation("io.insert-koin:koin-android:3.5.6")

    // Jetpack Compose
    implementation("io.insert-koin:koin-androidx-compose:3.5.6")

    // ViewModel
    implementation("io.insert-koin:koin-androidx-viewmodel:3.5.6")
}
```

### Инициализация с startKoin

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            // Логирование для отладки
            androidLogger(Level.DEBUG)

            // Контекст Android
            androidContext(this@MyApplication)

            // Загрузка модулей
            modules(
                appModule,
                networkModule,
                repositoryModule,
                viewModelModule
            )
        }
    }
}
```

### Module DSL

Модуль - это контейнер для определений зависимостей:

```kotlin
val appModule = module {
    // single - синглтон (один экземпляр на всё приложение)
    single { AppConfig() }

    // factory - новый экземпляр при каждом запросе
    factory { UserValidator() }

    // single с интерфейсом
    single<UserRepository> { UserRepositoryImpl(get()) }

    // factory с параметрами
    factory { (name: String) -> Logger(name) }
}
```

### Типы определений

#### single - Синглтон

```kotlin
val networkModule = module {
    // Создается один раз, переиспользуется везде
    single {
        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    single {
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(get()) // Получаем OkHttpClient
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    // Синглтон с интерфейсом
    single<ApiService> {
        get<Retrofit>().create(ApiService::class.java)
    }
}
```

#### factory - Новый экземпляр

```kotlin
val repositoryModule = module {
    // Новый экземпляр при каждом вызове get()
    factory { DateFormatter() }

    // factory с зависимостями
    factory {
        UserUseCase(
            repository = get(),
            validator = get()
        )
    }
}
```

#### bind - Привязка к интерфейсу

```kotlin
val dataModule = module {
    // Один класс, несколько интерфейсов
    single { UserRepositoryImpl(get()) } bind UserRepository::class

    // Альтернативный синтаксис
    single<UserRepository> { UserRepositoryImpl(get()) }

    // Множественная привязка
    single {
        AppDatabaseImpl(get())
    } binds arrayOf(
        UserDatabase::class,
        ProductDatabase::class
    )
}
```

#### named - Именованные зависимости

```kotlin
val configModule = module {
    // Разные реализации одного типа
    single(named("production")) {
        ApiConfig(baseUrl = "https://api.example.com")
    }

    single(named("staging")) {
        ApiConfig(baseUrl = "https://staging.example.com")
    }

    // Использование
    factory {
        ApiClient(config = get(named("production")))
    }
}
```

### Получение зависимостей с get()

```kotlin
val appModule = module {
    single { AppDatabase(get()) }
    single { UserDao(get()) }

    single<UserRepository> {
        UserRepositoryImpl(
            dao = get(),          // UserDao
            api = get(),          // ApiService
            config = get(named("production"))
        )
    }
}
```

### Структура модулей в проекте

```kotlin
// NetworkModule.kt
val networkModule = module {
    single { provideOkHttpClient() }
    single { provideRetrofit(get()) }
    single<ApiService> { provideApiService(get()) }
}

// DatabaseModule.kt
val databaseModule = module {
    single { provideDatabase(androidContext()) }
    single { provideUserDao(get()) }
}

// RepositoryModule.kt
val repositoryModule = module {
    single<UserRepository> { UserRepositoryImpl(get(), get()) }
    single<ProductRepository> { ProductRepositoryImpl(get()) }
}

// ViewModelModule.kt
val viewModelModule = module {
    viewModel { MainViewModel(get()) }
    viewModel { UserViewModel(get(), get()) }
}

// AppModule.kt - главный модуль
val appModules = listOf(
    networkModule,
    databaseModule,
    repositoryModule,
    viewModelModule
)

// Application
startKoin {
    androidContext(this@MyApplication)
    modules(appModules)
}
```

### Ленивая загрузка модулей

```kotlin
// Для больших приложений - загрузка по требованию
val featureModule = module {
    single { FeatureRepository() }
    viewModel { FeatureViewModel(get()) }
}

// Динамическая загрузка
fun loadFeatureModule() {
    loadKoinModules(featureModule)
}

fun unloadFeatureModule() {
    unloadKoinModules(featureModule)
}
```

### Лучшие практики

1. **Разделяйте модули** по функциональности (network, database, repository)
2. **Используйте single** для stateless сервисов и репозиториев
3. **Используйте factory** для stateful объектов
4. **Именуйте зависимости** при наличии нескольких реализаций
5. **Избегайте циклических зависимостей**

---

## Answer (EN)

**Koin** is a lightweight dependency injection framework for Kotlin that uses DSL instead of code generation. It is simple to set up and requires no annotations.

### Adding Koin Dependencies

```kotlin
// build.gradle.kts (Module)
dependencies {
    // Core
    implementation("io.insert-koin:koin-core:3.5.6")

    // Android
    implementation("io.insert-koin:koin-android:3.5.6")

    // Jetpack Compose
    implementation("io.insert-koin:koin-androidx-compose:3.5.6")

    // ViewModel
    implementation("io.insert-koin:koin-androidx-viewmodel:3.5.6")
}
```

### Initialization with startKoin

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            // Debug logging
            androidLogger(Level.DEBUG)

            // Android context
            androidContext(this@MyApplication)

            // Load modules
            modules(
                appModule,
                networkModule,
                repositoryModule,
                viewModelModule
            )
        }
    }
}
```

### Module DSL

A module is a container for dependency definitions:

```kotlin
val appModule = module {
    // single - singleton (one instance for the entire application)
    single { AppConfig() }

    // factory - new instance on each request
    factory { UserValidator() }

    // single with interface
    single<UserRepository> { UserRepositoryImpl(get()) }

    // factory with parameters
    factory { (name: String) -> Logger(name) }
}
```

### Definition Types

#### single - Singleton

```kotlin
val networkModule = module {
    // Created once, reused everywhere
    single {
        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    single {
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(get()) // Get OkHttpClient
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    // Singleton with interface
    single<ApiService> {
        get<Retrofit>().create(ApiService::class.java)
    }
}
```

#### factory - New Instance

```kotlin
val repositoryModule = module {
    // New instance on each get() call
    factory { DateFormatter() }

    // factory with dependencies
    factory {
        UserUseCase(
            repository = get(),
            validator = get()
        )
    }
}
```

#### bind - Interface Binding

```kotlin
val dataModule = module {
    // One class, multiple interfaces
    single { UserRepositoryImpl(get()) } bind UserRepository::class

    // Alternative syntax
    single<UserRepository> { UserRepositoryImpl(get()) }

    // Multiple bindings
    single {
        AppDatabaseImpl(get())
    } binds arrayOf(
        UserDatabase::class,
        ProductDatabase::class
    )
}
```

#### named - Named Dependencies

```kotlin
val configModule = module {
    // Different implementations of the same type
    single(named("production")) {
        ApiConfig(baseUrl = "https://api.example.com")
    }

    single(named("staging")) {
        ApiConfig(baseUrl = "https://staging.example.com")
    }

    // Usage
    factory {
        ApiClient(config = get(named("production")))
    }
}
```

### Retrieving Dependencies with get()

```kotlin
val appModule = module {
    single { AppDatabase(get()) }
    single { UserDao(get()) }

    single<UserRepository> {
        UserRepositoryImpl(
            dao = get(),          // UserDao
            api = get(),          // ApiService
            config = get(named("production"))
        )
    }
}
```

### Module Structure in a Project

```kotlin
// NetworkModule.kt
val networkModule = module {
    single { provideOkHttpClient() }
    single { provideRetrofit(get()) }
    single<ApiService> { provideApiService(get()) }
}

// DatabaseModule.kt
val databaseModule = module {
    single { provideDatabase(androidContext()) }
    single { provideUserDao(get()) }
}

// RepositoryModule.kt
val repositoryModule = module {
    single<UserRepository> { UserRepositoryImpl(get(), get()) }
    single<ProductRepository> { ProductRepositoryImpl(get()) }
}

// ViewModelModule.kt
val viewModelModule = module {
    viewModel { MainViewModel(get()) }
    viewModel { UserViewModel(get(), get()) }
}

// AppModule.kt - main module
val appModules = listOf(
    networkModule,
    databaseModule,
    repositoryModule,
    viewModelModule
)

// Application
startKoin {
    androidContext(this@MyApplication)
    modules(appModules)
}
```

### Lazy Module Loading

```kotlin
// For large applications - load on demand
val featureModule = module {
    single { FeatureRepository() }
    viewModel { FeatureViewModel(get()) }
}

// Dynamic loading
fun loadFeatureModule() {
    loadKoinModules(featureModule)
}

fun unloadFeatureModule() {
    unloadKoinModules(featureModule)
}
```

### Best Practices

1. **Separate modules** by functionality (network, database, repository)
2. **Use single** for stateless services and repositories
3. **Use factory** for stateful objects
4. **Name dependencies** when there are multiple implementations
5. **Avoid circular dependencies**

---

## Dopolnitelnye Voprosy (RU)

- Как разделить модули Koin по feature-модулям в multi-module проекте?
- В чем разница между single и factory в контексте жизненного цикла?
- Как организовать модули для тестирования?

## Follow-ups

- How do you split Koin modules across feature modules in a multi-module project?
- What is the difference between single and factory in terms of lifecycle?
- How do you organize modules for testing?

## Ssylki (RU)

- [Koin Documentation](https://insert-koin.io/docs/quickstart/android)
- [Koin GitHub](https://github.com/InsertKoinIO/koin)

## References

- [Koin Documentation](https://insert-koin.io/docs/quickstart/android)
- [Koin GitHub](https://github.com/InsertKoinIO/koin)

## Svyazannye Voprosy (RU)

### Medium
- [[q-koin-inject-get--koin--medium]]
- [[q-koin-scopes--koin--medium]]
- [[q-koin-viewmodel--koin--medium]]
- [[q-koin-parameters--koin--medium]]

## Related Questions

### Medium
- [[q-koin-inject-get--koin--medium]]
- [[q-koin-scopes--koin--medium]]
- [[q-koin-viewmodel--koin--medium]]
- [[q-koin-parameters--koin--medium]]
