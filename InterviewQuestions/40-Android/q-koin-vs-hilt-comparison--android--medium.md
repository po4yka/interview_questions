---
id: 20251016-174842
title: "Koin Vs Hilt Comparison / Сравнение Koin и Hilt"
aliases: ["Koin Vs Hilt Comparison", "Сравнение Koin и Hilt"]
topic: android
subtopics: [di-hilt, di-koin]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-app-start-types-android--android--medium, q-network-request-deduplication--networking--hard]
created: 2025-10-13
updated: 2025-10-28
sources: []
tags: [android, di, hilt, koin, architecture, difficulty/medium, android/di-hilt, android/di-koin]
date created: Tuesday, October 28th 2025, 9:26:11 pm
date modified: Thursday, October 30th 2025, 3:11:53 pm
---

# Вопрос (RU)

Сравните Koin и Hilt детально. Когда вы бы выбрали один вместо другого? Обсудите compile-time vs runtime DI.

# Question (EN)

Compare Koin and Hilt in detail. When would you choose one over the other? Discuss compile-time vs runtime DI.

## Ответ (RU)

### Архитектурное Сравнение

| Аспект | Koin | Hilt |
|--------|------|------|
| **Паттерн** | Service Locator | True Dependency Injection |
| **Разрешение** | Runtime (рефлексия) | Compile-time (генерация кода) |
| **Верификация** | Runtime | Compile-time |
| **Время сборки** | Быстрое | Медленное (kapt/ksp) |
| **Runtime производительность** | Небольшой overhead | Оптимальная |
| **Overhead старта** | 50-100мс | 0мс |
| **Multiplatform** | Да (KMM) | Только Android |
| **Обучение** | Легко (1-2 дня) | Сложнее (1-2 недели) |
| **Тестирование** | Простое | Умеренное |

### Compile-Time vs Runtime DI

**Compile-Time DI (Hilt):**
- Генерация кода на этапе компиляции
- Граф зависимостей проверяется до запуска
- Нет рефлексии → лучшая производительность
- Ошибки обнаруживаются при сборке

```kotlin
// ✅ Hilt - аннотации и генерация кода
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val repository: AuthRepository
) : ViewModel()

@Singleton
class AuthRepositoryImpl @Inject constructor(
    private val api: AuthApi
) : AuthRepository
```

**Runtime DI (Koin):**
- DSL модули загружаются при старте
- Зависимости разрешаются по требованию
- Простой синтаксис, но runtime ошибки
- Гибкая конфигурация

```kotlin
// ✅ Koin - простой DSL
val dataModule = module {
    single<AuthRepository> { AuthRepositoryImpl(get()) }
    viewModel { AuthViewModel(get()) }
}

class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            modules(dataModule)
        }
    }
}
```

### Матрица Решений

**Выбирайте Koin:**
- Kotlin Multiplatform проекты
- MVP/прототипы (быстрая итерация)
- Небольшие/средние приложения
- Время сборки критично
- Простота важнее типобезопасности

**Выбирайте Hilt:**
- Только Android приложения
- Крупномасштабные проекты (50+ модулей)
- Критична типобезопасность
- Долгосрочная поддержка (5+ лет)
- Опытная команда знает Dagger

### Лучшие Практики

**Koin:**
```kotlin
// ✅ Используйте checkModules() для валидации
class AppTest : KoinTest {
    @Test
    fun verifyModules() = checkModules {
        modules(appModule, dataModule)
    }
}

// ✅ Предпочитайте by inject() вместо get()
class Repository {
    private val api: Api by inject() // lazy
}

// ❌ Избегайте get() для ранней инициализации
class Repository {
    private val api: Api = get() // eager, может упасть
}
```

**Hilt:**
```kotlin
// ✅ Используйте @Binds вместо @Provides
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
    @Binds
    abstract fun bindRepository(impl: RepositoryImpl): Repository
}

// ❌ Избегайте @Provides для интерфейсов
@Provides
fun provideRepository(impl: RepositoryImpl): Repository = impl
```

## Answer (EN)

### Architecture Comparison

| Aspect | Koin | Hilt |
|--------|------|------|
| **Pattern** | Service Locator | True Dependency Injection |
| **Resolution** | Runtime (reflection) | Compile-time (code generation) |
| **Verification** | Runtime | Compile-time |
| **Build Time** | Fast | Slow (kapt/ksp) |
| **Runtime Performance** | Small overhead | Optimal |
| **Startup Overhead** | 50-100ms | 0ms |
| **Multiplatform** | Yes (KMM) | Android only |
| **Learning Curve** | Easy (1-2 days) | Moderate (1-2 weeks) |
| **Testing** | Simple | Moderate |

### Compile-Time vs Runtime DI

**Compile-Time DI (Hilt):**
- Code generation at compile time
- Dependency graph verified before runtime
- No reflection → better performance
- Errors caught during build

```kotlin
// ✅ Hilt - annotations and code generation
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val repository: AuthRepository
) : ViewModel()

@Singleton
class AuthRepositoryImpl @Inject constructor(
    private val api: AuthApi
) : AuthRepository
```

**Runtime DI (Koin):**
- DSL modules loaded at startup
- Dependencies resolved on demand
- Simple syntax but runtime errors
- Flexible configuration

```kotlin
// ✅ Koin - simple DSL
val dataModule = module {
    single<AuthRepository> { AuthRepositoryImpl(get()) }
    viewModel { AuthViewModel(get()) }
}

class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            modules(dataModule)
        }
    }
}
```

### Decision Matrix

**Choose Koin:**
- Kotlin Multiplatform projects
- MVP/prototypes (fast iteration)
- Small/medium apps
- Build time is critical
- Simplicity over type safety

**Choose Hilt:**
- Android-only apps
- Large-scale projects (50+ modules)
- Type safety critical
- Long-term maintenance (5+ years)
- Experienced team knows Dagger

### Best Practices

**Koin:**
```kotlin
// ✅ Use checkModules() for validation
class AppTest : KoinTest {
    @Test
    fun verifyModules() = checkModules {
        modules(appModule, dataModule)
    }
}

// ✅ Prefer by inject() over get()
class Repository {
    private val api: Api by inject() // lazy
}

// ❌ Avoid get() for eager initialization
class Repository {
    private val api: Api = get() // eager, may crash
}
```

**Hilt:**
```kotlin
// ✅ Use @Binds instead of @Provides
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
    @Binds
    abstract fun bindRepository(impl: RepositoryImpl): Repository
}

// ❌ Avoid @Provides for interfaces
@Provides
fun provideRepository(impl: RepositoryImpl): Repository = impl
```

## Follow-ups

- How would you handle scoped dependencies (Activity/Fragment scope) in both frameworks?
- What are the strategies for migrating from Dagger2 to either Koin or Hilt?
- How do you test modules with circular dependencies in Koin vs Hilt?
- Can Koin and Hilt coexist in the same codebase during migration?

## References

- [Hilt Documentation](https://dagger.dev/hilt/)
- [Koin Documentation](https://insert-koin.io/)
- [[c-dependency-injection]]
- [[c-service-locator-pattern]]

## Related Questions

### Prerequisites
- [[q-what-is-dependency-injection--android--easy]]
- [[q-dagger-basics--android--medium]]

### Related
- [[q-app-start-types-android--android--medium]]
- [[q-viewmodel-factory-injection--android--medium]]

### Advanced
- [[q-network-request-deduplication--networking--hard]]
- [[q-custom-scopes-hilt--android--hard]]
