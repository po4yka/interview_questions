---\
id: android-093
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
related: [c-dagger, c-dependency-injection]
created: 2025-10-13
updated: 2025-11-10
sources: []
tags: [android, android/di-hilt, android/di-koin, architecture, di, difficulty/medium, hilt, koin]

---\
# Вопрос (RU)

> Сравните `Koin` и `Hilt` детально. Когда вы бы выбрали один вместо другого? Обсудите compile-time vs runtime DI.

# Question (EN)

> Compare `Koin` and `Hilt` in detail. When would you choose one over the other? Discuss compile-time vs runtime DI.

## Ответ (RU)

### Архитектурное Сравнение

| Аспект | `Koin` | `Hilt` |
|--------|------|------|
| **Паттерн** | DI через DSL, может использоваться как `Service` Locator | Компилируемый DI поверх `Dagger` |
| **Разрешение** | Runtime (через DSL/registry) | Compile-time (генерация кода) |
| **Верификация** | В основном runtime (есть checkModules()) | Compile-time |
| **Время сборки** | Как правило быстрее (нет/минимум KAPT) | Медленнее (kapt/ksp, генерация кода) |
| **Runtime производительность** | Есть небольшой overhead резолвинга на runtime | Обычно лучше за счёт сгенерированного кода |
| **Overhead старта** | Есть стоимость инициализации модулей при старте | Небольшой/минимальный дополнительный overhead (граф сгенерирован) |
| **Multiplatform** | Да (KMM) | Только Android |
| **Обучение** | Легко (часы–1-2 дня) | Сложнее (нужно понимать Dagger/компоненты) |
| **Тестирование** | Простое (ручная подмена модулей) | Умеренное (работа с компонентами/entry points) |

### Compile-Time Vs Runtime DI

**Compile-Time DI (`Hilt`):**
- Генерация кода на этапе компиляции (`Dagger` под капотом)
- Граф зависимостей проверяется до запуска
- Нет рефлексии для резолвинга зависимостей → обычно лучшая производительность
- Большинство ошибок конфигурации обнаруживаются при сборке

```kotlin
// ✅ Hilt - аннотации и генерация кода
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val repository: AuthRepository
) : ViewModel()

// Реализация с @Inject-конструктором может быть использована напрямую
class AuthRepositoryImpl @Inject constructor(
    private val api: AuthApi
) : AuthRepository
```

**Runtime DI (`Koin`):**
- Модули DSL регистрируются и загружаются при старте
- Зависимости разрешаются на runtime при первом запросе
- Простой декларативный синтаксис, но ошибки wiring-а проявляются в runtime
- Гибкая конфигурация (легко переопределять модули, удобно для тестов)

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

**Выбирайте `Koin`:**
- Kotlin Multiplatform проекты
- MVP/прототипы (быстрая итерация)
- Небольшие/средние приложения
- Время сборки критично
- Простота и гибкость важнее строгой compile-time типобезопасности

**Выбирайте `Hilt`:**
- Только Android приложения
- Крупномасштабные проекты (много модулей, большая команда)
- Критична типобезопасность и compile-time проверка
- Долгосрочная поддержка (официальная поддержка Google, 5+ лет горизонта)
- Команда уже знакома с `Dagger` или готова инвестировать в изучение

### Лучшие Практики

**`Koin`:**
```kotlin
// ✅ Используйте checkModules() для базовой валидации графа
class AppTest : KoinTest {
    @Test
    fun verifyModules() = checkModules {
        modules(appModule, dataModule)
    }
}

// ✅ Предпочитайте ленивое внедрение через by inject() там, где это уместно
class Repository {
    private val api: Api by inject() // lazy, отказ от ранней инициализации
}

// ❌ Избегайте get() для ранней инициализации в местах,
// где граф ещё не готов или это усложняет тестирование
class Repository {
    private val api: Api = get() // eager, может упасть/усложнить подмену
}
```

**`Hilt`:**
```kotlin
// ✅ Для простых связок интерфейс → реализация используйте @Binds
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
    @Binds
    abstract fun bindRepository(impl: RepositoryImpl): Repository
}

// Можно использовать @Provides, но для таких кейсов предпочтительнее @Binds
@Module
@InstallIn(SingletonComponent::class)
object LegacyDataModule {
    @Provides
    fun provideRepository(impl: RepositoryImpl): Repository = impl
}
```

## Answer (EN)

### Architecture Comparison

| Aspect | `Koin` | `Hilt` |
|--------|------|------|
| **Pattern** | DI via Kotlin DSL, can be used as `Service` Locator | Compile-time DI on top of `Dagger` |
| **Resolution** | Runtime (via DSL/registry) | Compile-time (code generation) |
| **Verification** | Mostly runtime (has checkModules()) | Compile-time |
| **Build Time** | Generally faster (no/heavy kapt avoided) | Slower (kapt/ksp, code generation) |
| **Runtime Performance** | Some runtime resolution overhead | Typically better due to generated code |
| **Startup Overhead** | Non-zero module initialization cost at startup | Small/minimal extra overhead (graph is generated) |
| **Multiplatform** | Yes (KMM support) | Android only |
| **Learning Curve** | Easy (hours–1-2 days) | Harder (Dagger/components concepts) |
| **Testing** | Simple (override modules easily) | Moderate (components/entry points) |

### Compile-Time Vs Runtime DI

**Compile-Time DI (`Hilt`):**
- Code generation at compile time (`Dagger` under the hood)
- Dependency graph verified before runtime
- No reflection-based resolution → usually better performance
- Most configuration errors caught during build

```kotlin
// ✅ Hilt - annotations and code generation
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val repository: AuthRepository
) : ViewModel()

// Implementation with @Inject constructor can be used directly as a binding
class AuthRepositoryImpl @Inject constructor(
    private val api: AuthApi
) : AuthRepository
```

**Runtime DI (`Koin`):**
- DSL modules registered and loaded at startup
- Dependencies resolved at runtime on demand
- Simple declarative syntax, but wiring errors appear at runtime
- Flexible configuration (easy overrides, convenient for tests)

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

**Choose `Koin`:**
- Kotlin Multiplatform projects
- MVP/prototypes (fast iteration)
- Small/medium apps
- Build time is critical
- Prefer simplicity and flexibility over strict compile-time safety

**Choose `Hilt`:**
- Android-only apps
- Large-scale projects (many modules, big team)
- Type safety and compile-time validation are critical
- `Long`-term maintenance (official Google support, 5+ year horizon)
- Team is experienced with `Dagger` or ready to invest in learning it

### Best Practices

**`Koin`:**
```kotlin
// ✅ Use checkModules() for basic graph validation
class AppTest : KoinTest {
    @Test
    fun verifyModules() = checkModules {
        modules(appModule, dataModule)
    }
}

// ✅ Prefer lazy injection via by inject() where appropriate
class Repository {
    private val api: Api by inject() // lazy, avoids premature init
}

// ❌ Avoid eager get() in places where the graph may not be ready
// or where it complicates testing/overrides
class Repository {
    private val api: Api = get() // eager, can crash/complicate tests
}
```

**`Hilt`:**
```kotlin
// ✅ Prefer @Binds for simple interface -> implementation bindings
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
    @Binds
    abstract fun bindRepository(impl: RepositoryImpl): Repository
}

// @Provides is valid, but for this specific case @Binds is usually better
@Module
@InstallIn(SingletonComponent::class)
object LegacyDataModule {
    @Provides
    fun provideRepository(impl: RepositoryImpl): Repository = impl
}
```

## Follow-ups

- How would you handle scoped dependencies (`Activity`/`Fragment` scope) in both frameworks?
- What are the strategies for migrating from Dagger2 to either `Koin` or `Hilt`?
- How do you test modules with circular dependencies in `Koin` vs `Hilt`?
- Can `Koin` and `Hilt` coexist in the same codebase during migration?

## References

- [Hilt Documentation](https://dagger.dev/hilt/)
- [Koin Documentation](https://insert-koin.io/)
- [[c-dependency-injection]]

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] - DI basics with annotations
- [[q-dagger-purpose--android--easy]] - Why use dependency injection
- [[q-viewmodel-pattern--android--easy]] - `ViewModel` architecture

### Related
- [[q-what-is-hilt--android--medium]] - `Hilt` framework overview
- [[q-koin-fundamentals--android--medium]] - `Koin` fundamentals
- [[q-hilt-components-scope--android--medium]] - `Hilt` scoping
- [[q-koin-scope-management--android--medium]] - `Koin` scopes

### Advanced
- [[q-dagger-framework-overview--android--hard]] - `Dagger` internals
- [[q-koin-resolution-internals--android--hard]] - `Koin` resolution mechanism
- [[q-dagger-custom-scopes--android--hard]] - Custom scopes
