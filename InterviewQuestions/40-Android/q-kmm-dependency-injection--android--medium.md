---
id: android-222
title: KMM Dependency Injection / Dependency Injection в KMM
aliases:
- Dependency Injection в KMM
- KMM Dependency Injection
- KMM DI
- Koin для KMM
- Koin
topic: android
subtopics:
- di-koin
- kmp
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- moc-android
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/di-koin
- android/kmp
- di
- difficulty/medium
- koin
- kotlin
anki_cards:
- slug: android-222-0-en
  language: en
  anki_id: 1768396746878
  synced_at: '2026-01-23T16:45:05.778621'
- slug: android-222-0-ru
  language: ru
  anki_id: 1768396746901
  synced_at: '2026-01-23T16:45:05.782836'
---
# Вопрос (RU)

> Объясните стратегии dependency injection для KMM проектов. Как использовать `Koin` для multiplatform DI? Как обрабатывать platform-specific зависимости? В чем разница между `Koin`, Dagger/Hilt и manual DI в KMM?

# Question (EN)

> Explain dependency injection strategies for KMM projects. How do you use `Koin` for multiplatform DI? How do you handle platform-specific dependencies? What are the differences between using `Koin`, Dagger/Hilt, and manual DI in KMM?

---

## Ответ (RU)

**Подход**: KMM DI требует унифицированного решения для всех платформ с поддержкой platform-specific реализаций. `Koin` — один из популярных вариантов для KMM благодаря официальной поддержке multiplatform.

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
        TaskRepositoryImpl(api = get(), databaseDriverFactory = get())
    }
}

// ✅ Combine modules
val sharedModules = listOf(networkModule, repositoryModule)
```

**Platform-specific модули**:
```kotlin
// androidMain
val androidModule = module {
    // androidContext передается при инициализации в startKoin, его не нужно регистрировать как single
    single { DatabaseDriverFactory(androidContext()) }
    single<SecureStorage> { AndroidSecureStorage(androidContext()) }
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

**`Koin`**:
- Multiplatform (Android, iOS, Desktop, Web)
- Простая настройка, DSL
- Нет code generation
- Runtime resolution, нет compile-time safety
- Возможны runtime-ошибки при неверной конфигурации

**Dagger/Hilt**:
- Compile-time verification
- Лучшая производительность
- Type-safe
- Android-only, не используется на iOS в KMM shared-коде
- Сложная настройка, boilerplate

**Manual DI**:
- Полный контроль, работает везде
- Без framework dependencies
- Много boilerplate кода
- Ручное управление жизненным циклом, нет встроенного scope management

### Рекомендации

**Для KMM**: Чаще всего используется `Koin` (много платформ из коробки, единый стиль DI), либо manual DI для максимальной прозрачности.

**Для Android-only**: Dagger/Hilt (compile-time safety, оптимизация).

**Для простых проектов**: Manual DI (полный контроль, минимальные зависимости).

---

## Answer (EN)

**Approach**: KMM DI requires a unified solution across platforms while supporting platform-specific implementations. `Koin` is one of the popular options for KMM thanks to official multiplatform support.

### Koin For KMM

**`Module` setup**:
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
        TaskRepositoryImpl(api = get(), databaseDriverFactory = get())
    }
}

// ✅ Combine modules
val sharedModules = listOf(networkModule, repositoryModule)
```

**Platform-specific modules**:
```kotlin
// androidMain
val androidModule = module {
    // androidContext is provided to Koin in startKoin, no need to register it as a single
    single { DatabaseDriverFactory(androidContext()) }
    single<SecureStorage> { AndroidSecureStorage(androidContext()) }
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

**`Koin`**:
- Multiplatform (Android, iOS, Desktop, Web)
- Simple setup, DSL
- No code generation
- Runtime resolution, no compile-time safety
- Potential runtime errors if misconfigured

**Dagger/Hilt**:
- Compile-time verification
- Better performance
- Type-safe
- Android-only, not used on iOS in shared KMM code
- Complex setup, boilerplate

**Manual DI**:
- Full control, works everywhere
- No framework dependencies
- Lots of boilerplate
- Manual lifecycle handling, no built-in scope management

### Recommendations

**For KMM**: Commonly `Koin` (good multiplatform support, consistent DI style) or manual DI for maximum simplicity/explicitness.

**For Android-only**: Dagger/Hilt (compile-time safety, performance).

**For simple projects**: Manual DI (full control, minimal dependencies).

---

## Дополнительные Вопросы (RU)

- Как тестировать модули `Koin` в KMM?
- Каковы лучшие практики внедрения `ViewModel` в KMM?
- Как обрабатывать зависимости, учитывающие жизненный цикл, на iOS?
- Когда использовать `factory` против `single` scope в `Koin`?
- Как мигрировать с `Dagger` на `Koin` в KMM?

## Follow-ups

- How do you test `Koin` modules in KMM?
- What are best practices for `ViewModel` injection in KMM?
- How do you handle lifecycle-aware dependencies in iOS?
- When should you use factory vs single scope in `Koin`?
- How do you migrate from `Dagger` to `Koin` in KMM?

## Ссылки (RU)

- [[c-dependency-injection]]
- [[moc-android]]
- https://insert-koin.io/docs/reference/koin-mp/kmp
- https://kotlinlang.org/docs/multiplatform.html

## References

- [[c-dependency-injection]]
- [[moc-android]]
- https://insert-koin.io/docs/reference/koin-mp/kmp
- https://kotlinlang.org/docs/multiplatform.html

## Связанные Вопросы (RU)

### Продвинутые (сложнее)

## Related Questions

### Advanced (Harder)
