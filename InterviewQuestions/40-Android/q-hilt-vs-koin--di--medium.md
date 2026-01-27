---
id: android-di-002
title: Hilt vs Koin Performance and Compose / Производительность Hilt vs Koin и Compose
aliases:
- Hilt vs Koin 2026
- Hilt Koin Performance
- Производительность Hilt и Koin
- Hilt против Koin
topic: android
subtopics:
- di-hilt
- di-koin
question_kind: comparison
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- c-hilt
- q-koin-vs-hilt-comparison--android--medium
- q-koin-fundamentals--android--medium
- q-what-is-hilt--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/di-koin
- dependency-injection
- difficulty/medium
- hilt
- koin
- performance
anki_cards:
- slug: android-di-002-0-en
  language: en
- slug: android-di-002-0-ru
  language: ru
---
# Вопрос (RU)
> Сравните `Hilt` и `Koin` с точки зрения производительности: compile-time vs runtime DI, влияние на старт приложения, и интеграция с Jetpack Compose. Учитывайте улучшения Koin 4.x.

# Question (EN)
> Compare `Hilt` and `Koin` from a performance perspective: compile-time vs runtime DI, app startup impact, and Jetpack Compose integration. Consider Koin 4.x improvements.

---

## Ответ (RU)

### Сравнение Производительности

| Метрика | `Hilt` (compile-time) | `Koin 4.x` (runtime) |
|---------|----------------------|---------------------|
| **Время сборки** | Медленнее (kapt/ksp codegen) | Быстрее (нет codegen) |
| **Время старта** | Минимальный overhead | Overhead инициализации модулей |
| **Резолвинг** | O(1) - прямой вызов | O(1) с кэшированием (улучшено в 4.x) |
| **Memory footprint** | Больше сгенерированных классов | Меньше классов, но registry в памяти |
| **Proguard/R8** | Требует правила для рефлексии | Меньше правил |

### Compile-Time vs Runtime DI

**Hilt (Compile-Time):**
```kotlin
// Ошибки обнаруживаются при сборке
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository  // Если нет binding - сборка упадёт
) : ViewModel()

// Плюсы:
// - Гарантия корректности графа до запуска
// - Нет runtime reflection для резолвинга
// - IDE поддержка навигации по графу

// Минусы:
// - kapt: +30-60 сек на чистую сборку
// - ksp: +10-30 сек (лучше, но всё равно overhead)
```

**Koin 4.x (Runtime):**
```kotlin
// Ошибки обнаруживаются в runtime
val appModule = module {
    viewModelOf(::UserViewModel)  // Новый DSL в Koin 4.x
    singleOf(::UserRepositoryImpl) { bind<UserRepository>() }
}

// Плюсы:
// - Быстрая сборка (нет codegen)
// - Гибкие runtime-переопределения

// Минусы:
// - Crash при отсутствии зависимости
// - Нужны тесты с checkModules()
```

### Влияние на Старт Приложения

**Измерения (типичное приложение, ~50 зависимостей):**

| Этап | `Hilt` | `Koin 4.x` |
|------|--------|-----------|
| DI Initialization | ~5-10 ms | ~15-30 ms |
| First ViewModel | ~1-2 ms | ~2-5 ms |
| Subsequent resolves | <1 ms | <1 ms |

```kotlin
// Koin 4.x - оптимизация старта
startKoin {
    // Ленивая инициализация модулей (новое в 4.x)
    lazyModules(featureModule)

    // Стандартная загрузка для критичных модулей
    modules(coreModule)
}
```

### Интеграция с Jetpack Compose

**Hilt + Compose:**
```kotlin
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyApp()
        }
    }
}

@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()  // Стандартная интеграция
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    // UI
}
```

**Koin 4.x + Compose:**
```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // Compose-специфичный контекст (новое в Koin 4.x)
            KoinContext {
                MyApp()
            }
        }
    }
}

@Composable
fun UserScreen(
    viewModel: UserViewModel = koinViewModel()  // Улучшенная интеграция
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    // UI
}

// Koin 4.x: Compose Multiplatform поддержка
@Composable
fun KoinContext(content: @Composable () -> Unit) {
    // Автоматическое управление scope
    CompositionLocalProvider(
        LocalKoinScope provides currentKoinScope()
    ) {
        content()
    }
}
```

### Улучшения Koin 4.x (2024-2026)

| Функция | Описание |
|---------|----------|
| **Новый DSL** | `singleOf()`, `factoryOf()`, `viewModelOf()` |
| **Lazy modules** | Отложенная загрузка модулей |
| **Compose integration** | `KoinContext`, улучшенный `koinViewModel()` |
| **Verify API** | Улучшенный `verify()` вместо `checkModules()` |
| **Performance** | Оптимизированный резолвинг и кэширование |
| **Multiplatform** | Полная поддержка KMP + Compose Multiplatform |

```kotlin
// Koin 4.x verify API
class ModuleVerificationTest : KoinTest {
    @Test
    fun verifyAllModules() {
        appModule.verify(
            extraTypes = listOf(SavedStateHandle::class)
        )
    }
}
```

### Рекомендации по Выбору

| Критерий | Hilt | Koin 4.x |
|----------|------|----------|
| Compile-time safety | Необходима | Достаточно тестов |
| Build time | Не критично | Критично |
| Team experience | Знакомы с Dagger | Новая команда |
| Multiplatform | Не нужен | KMP проект |
| Google support | Важна | Не критична |

---

## Answer (EN)

### Performance Comparison

| Metric | `Hilt` (compile-time) | `Koin 4.x` (runtime) |
|--------|----------------------|---------------------|
| **Build time** | Slower (kapt/ksp codegen) | Faster (no codegen) |
| **Startup time** | Minimal overhead | Module initialization overhead |
| **Resolution** | O(1) - direct call | O(1) with caching (improved in 4.x) |
| **Memory footprint** | More generated classes | Fewer classes, but registry in memory |
| **Proguard/R8** | Needs reflection rules | Fewer rules needed |

### Compile-Time vs Runtime DI

**Hilt (Compile-Time):**
```kotlin
// Errors caught at build time
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository  // Missing binding = build failure
) : ViewModel()

// Pros:
// - Graph correctness guaranteed before runtime
// - No runtime reflection for resolution
// - IDE support for graph navigation

// Cons:
// - kapt: +30-60 sec on clean build
// - ksp: +10-30 sec (better, but still overhead)
```

**Koin 4.x (Runtime):**
```kotlin
// Errors caught at runtime
val appModule = module {
    viewModelOf(::UserViewModel)  // New DSL in Koin 4.x
    singleOf(::UserRepositoryImpl) { bind<UserRepository>() }
}

// Pros:
// - Fast builds (no codegen)
// - Flexible runtime overrides

// Cons:
// - Crash on missing dependency
// - Need tests with checkModules()
```

### App Startup Impact

**Measurements (typical app, ~50 dependencies):**

| Stage | `Hilt` | `Koin 4.x` |
|-------|--------|-----------|
| DI Initialization | ~5-10 ms | ~15-30 ms |
| First ViewModel | ~1-2 ms | ~2-5 ms |
| Subsequent resolves | <1 ms | <1 ms |

```kotlin
// Koin 4.x - startup optimization
startKoin {
    // Lazy module initialization (new in 4.x)
    lazyModules(featureModule)

    // Standard loading for critical modules
    modules(coreModule)
}
```

### Jetpack Compose Integration

**Hilt + Compose:**
```kotlin
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyApp()
        }
    }
}

@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()  // Standard integration
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    // UI
}
```

**Koin 4.x + Compose:**
```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // Compose-specific context (new in Koin 4.x)
            KoinContext {
                MyApp()
            }
        }
    }
}

@Composable
fun UserScreen(
    viewModel: UserViewModel = koinViewModel()  // Improved integration
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    // UI
}

// Koin 4.x: Compose Multiplatform support
@Composable
fun KoinContext(content: @Composable () -> Unit) {
    // Automatic scope management
    CompositionLocalProvider(
        LocalKoinScope provides currentKoinScope()
    ) {
        content()
    }
}
```

### Koin 4.x Improvements (2024-2026)

| Feature | Description |
|---------|-------------|
| **New DSL** | `singleOf()`, `factoryOf()`, `viewModelOf()` |
| **Lazy modules** | Deferred module loading |
| **Compose integration** | `KoinContext`, improved `koinViewModel()` |
| **Verify API** | Improved `verify()` replacing `checkModules()` |
| **Performance** | Optimized resolution and caching |
| **Multiplatform** | Full KMP + Compose Multiplatform support |

```kotlin
// Koin 4.x verify API
class ModuleVerificationTest : KoinTest {
    @Test
    fun verifyAllModules() {
        appModule.verify(
            extraTypes = listOf(SavedStateHandle::class)
        )
    }
}
```

### Selection Recommendations

| Criterion | Hilt | Koin 4.x |
|-----------|------|----------|
| Compile-time safety | Required | Tests are enough |
| Build time | Not critical | Critical |
| Team experience | Familiar with Dagger | New team |
| Multiplatform | Not needed | KMP project |
| Google support | Important | Not critical |

---

## Follow-ups

- Как профилировать время инициализации DI в продакшен-приложении?
- Какие стратегии оптимизации времени сборки существуют для Hilt?
- Как организовать миграцию с Koin 3.x на 4.x?

## References

- [Koin 4.x Documentation](https://insert-koin.io/)
- [Hilt + Compose](https://developer.android.com/jetpack/compose/libraries#hilt)
- [KSP vs KAPT Performance](https://kotlinlang.org/docs/ksp-why-ksp.html)

## Related Questions

### Prerequisites
- [[q-koin-fundamentals--android--medium]] - Koin basics
- [[q-what-is-hilt--android--medium]] - Hilt overview

### Related
- [[q-koin-vs-hilt-comparison--android--medium]] - Detailed comparison
- [[q-koin-vs-dagger-philosophy--android--hard]] - Philosophy comparison
- [[q-kapt-vs-ksp--android--medium]] - Build performance

### Advanced
- [[q-koin-resolution-internals--android--hard]] - Koin internals
- [[q-dagger-build-time-optimization--android--medium]] - Build optimization
