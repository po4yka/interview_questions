---
id: android-222
title: "KMM Dependency Injection / Dependency Injection в KMM"
aliases: [Dependency Injection в KMM, KMM Dependency Injection, KMM DI, Koin, Koin для KMM]
topic: android
subtopics: [di-koin, kmp]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, c-koin]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/di-koin, android/kmp, DI, difficulty/medium, Koin, Kotlin]
date created: Tuesday, October 28th 2025, 9:23:40 pm
date modified: Saturday, November 1st 2025, 5:43:34 pm
---

# Вопрос (RU)

> Объясните стратегии dependency injection для KMM проектов. Как использовать Koin для multiplatform DI? Как обрабатывать platform-specific зависимости? В чем разница между Koin, Dagger/Hilt и manual DI в KMM?

# Question (EN)

> Explain dependency injection strategies for KMM projects. How do you use Koin for multiplatform DI? How do you handle platform-specific dependencies? What are the differences between using Koin, Dagger/Hilt, and manual DI in KMM?

---

## Ответ (RU)

**Подход**: KMM DI требует унифицированного решения для всех платформ с поддержкой platform-specific реализаций. Koin - оптимальный выбор для KMM благодаря поддержке multiplatform.

### Koin Для KMM

**Настройка модулей**:
```kotlin
// commonMain - общие зависимости
val networkModule = module {
    single {
        HttpClient {
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
        }
    }
    single { TaskApiService(get()) }
}

val repositoryModule = module {
    single<TaskRepository> {
        TaskRepositoryImpl(api = get(), database = get())
    }
}

// ✅ Combine modules
val sharedModules = listOf(networkModule, repositoryModule)
```

**Platform-specific модули**:
```kotlin
// androidMain
val androidModule = module {
    single { androidContext() }
    single { DatabaseDriverFactory(get()) }
    single<SecureStorage> { AndroidSecureStorage(get()) }
}

// iosMain
val iosModule = module {
    single { DatabaseDriverFactory() }
    single<SecureStorage> { IOSSecureStorage() }
}
```

**Инициализация**:
```kotlin
// commonMain
fun initKoin(appDeclaration: KoinAppDeclaration = {}) = startKoin {
    appDeclaration()
    modules(sharedModules)
}

// androidMain
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        initKoin {
            androidContext(this@MyApplication)
            modules(androidModule)
        }
    }
}

// iosMain - вызвать из Swift
fun initKoinIOS() = initKoin { modules(iosModule) }
```

### Platform-Specific Dependencies

**Expect/Actual паттерн**:
```kotlin
// commonMain - объявление
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

// androidMain - Android реализация
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = TaskDatabase.Schema,
            context = context,
            name = "task.db"
        )
    }
}

// ✅ iosMain - iOS реализация
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = TaskDatabase.Schema,
            name = "task.db"
        )
    }
}
```

### Сравнение DI Фреймворков

**Koin**:
- ✅ Multiplatform (Android, iOS, Desktop, Web)
- ✅ Простая настройка, DSL
- ✅ Нет code generation
- ❌ Runtime resolution, нет compile-time safety
- ❌ Runtime errors

**Dagger/Hilt**:
- ✅ Compile-time verification
- ✅ Лучшая производительность
- ✅ Type-safe
- ❌ Android-only, не работает на iOS
- ❌ Сложная настройка, boilerplate

**Manual DI**:
- ✅ Полный контроль, работает везде
- ✅ Без framework dependencies
- ❌ Много boilerplate кода
- ❌ Manual lifecycle, нет scope management

### Рекомендации

**Для KMM**: Koin (максимальное переиспользование, consistency)
**Для Android-only**: Dagger/Hilt (compile-time safety)
**Для простых проектов**: Manual DI (полный контроль)

---

## Answer (EN)

**Approach**: KMM DI requires a unified solution across platforms while supporting platform-specific implementations. Koin provides the most seamless multiplatform DI solution.

### Koin For KMM

**Module setup**:
```kotlin
// commonMain - shared dependencies
val networkModule = module {
    single {
        HttpClient {
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
        }
    }
    single { TaskApiService(get()) }
}

val repositoryModule = module {
    single<TaskRepository> {
        TaskRepositoryImpl(api = get(), database = get())
    }
}

// ✅ Combine modules
val sharedModules = listOf(networkModule, repositoryModule)
```

**Platform-specific modules**:
```kotlin
// androidMain
val androidModule = module {
    single { androidContext() }
    single { DatabaseDriverFactory(get()) }
    single<SecureStorage> { AndroidSecureStorage(get()) }
}

// iosMain
val iosModule = module {
    single { DatabaseDriverFactory() }
    single<SecureStorage> { IOSSecureStorage() }
}
```

**Initialization**:
```kotlin
// commonMain
fun initKoin(appDeclaration: KoinAppDeclaration = {}) = startKoin {
    appDeclaration()
    modules(sharedModules)
}

// androidMain
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        initKoin {
            androidContext(this@MyApplication)
            modules(androidModule)
        }
    }
}

// iosMain - call from Swift
fun initKoinIOS() = initKoin { modules(iosModule) }
```

### Platform-Specific Dependencies

**Expect/Actual pattern**:
```kotlin
// commonMain - declaration
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

// androidMain - Android implementation
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = TaskDatabase.Schema,
            context = context,
            name = "task.db"
        )
    }
}

// ✅ iosMain - iOS implementation
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = TaskDatabase.Schema,
            name = "task.db"
        )
    }
}
```

### DI Framework Comparison

**Koin**:
- ✅ Multiplatform (Android, iOS, Desktop, Web)
- ✅ Simple setup, DSL
- ✅ No code generation
- ❌ Runtime resolution, no compile-time safety
- ❌ Runtime errors

**Dagger/Hilt**:
- ✅ Compile-time verification
- ✅ Better performance
- ✅ Type-safe
- ❌ Android-only, doesn't work on iOS
- ❌ Complex setup, boilerplate

**Manual DI**:
- ✅ Full control, works everywhere
- ✅ No framework dependencies
- ❌ Lots of boilerplate
- ❌ Manual lifecycle, no scope management

### Recommendations

**For KMM**: Koin (maximum code sharing, consistency)
**For Android-only**: Dagger/Hilt (compile-time safety)
**For simple projects**: Manual DI (full control)

---

## Follow-ups

- How do you test Koin modules in KMM?
- What are best practices for ViewModel injection in KMM?
- How do you handle lifecycle-aware dependencies in iOS?
- When should you use factory vs single scope in Koin?
- How do you migrate from Dagger to Koin in KMM?

## References

- [[c-dependency-injection]]
- [[c-koin]]
- [[moc-android]]
- https://insert-koin.io/docs/reference/koin-mp/kmp
- https://kotlinlang.org/docs/multiplatform.html

## Related Questions

### Advanced (Harder)
