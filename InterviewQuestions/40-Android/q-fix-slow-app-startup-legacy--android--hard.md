---
id: android-271
title: Fix Slow App Startup Legacy / Исправление медленного запуска приложения
aliases:
- Fix Slow App Startup in Legacy Project
- Исправление медленного запуска приложения в легаси-проекте
topic: android
subtopics:
- architecture-modularization
- performance-startup
- profiling
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- c-app-startup
- c-lazy-initialization
- q-android-profiling-tools--android--medium
- q-what-are-services-used-for--android--medium
sources:
- Android App Startup documentation
created: 2025-10-15
updated: 2025-11-03
tags:
- android/architecture-modularization
- android/performance-startup
- android/profiling
- app-startup
- difficulty/hard
- lazy-init
- legacy-code
- optimization
---

# Вопрос (RU)

> Что делать, если нужно исправить медленный запуск приложения в legacy-проекте?

## Краткая Версия

Оптимизируйте запуск legacy Android приложения: профилируйте bottleneck'ы, перенесите тяжелую инициализацию в фон, используйте lazy loading и Baseline Profiles для 15-30% улучшения производительности.

## Подробная Версия

Систематически оптимизируйте медленный запуск legacy Android приложения:

**Профилирование:**
- Используйте Android Profiler для выявления узких мест
- Измерьте холодный/теплый/горячий старт с целевыми показателями <2с/<1с/<500мс

**Оптимизация инициализации:**
- Перенесите тяжелые операции из `Application`.onCreate() в фоновые потоки
- Используйте Jetpack App Startup для отложенной инициализации компонентов
- Примените lazy initialization через dependency injection

**Архитектурные улучшения:**
- Разбейте монолитную инициализацию на модули с зависимостями
- Используйте Baseline Profiles для AOT-компиляции критических путей
- Реализуйте постепенный rollout оптимизаций с измерением метрик

# Question (EN)

> How would you approach fixing slow app startup in a legacy Android project?

## `Short` Version

Optimize legacy Android app startup: profile bottlenecks, move heavy initialization to background, use lazy loading and Baseline Profiles for 15-30% performance improvement.

## Detailed Version

Systematically optimize slow startup in legacy Android application:

**Profiling:**
- Use Android Profiler to identify bottlenecks
- Measure cold/warm/hot start with targets <2s/<1s/<500ms

**Initialization Optimization:**
- Move heavy operations from `Application`.onCreate() to background threads
- Use Jetpack App Startup for deferred component initialization
- Apply lazy initialization through dependency injection

**Architectural Improvements:**
- Break monolithic initialization into modules with dependencies
- Use Baseline Profiles for AOT compilation of critical paths
- Implement gradual rollout of optimizations with metrics measurement

---

## Ответ (RU)

**Подход:** Систематическая оптимизация с измеримыми результатами через профилирование, отложенную инициализацию и архитектурные улучшения.

### Теоретические Основы

**Типы запуска приложения:**
- **Холодный старт** — приложение запускается с нуля, требует полной инициализации
- **Теплый старт** — приложение уже запущено но уничтожено процессом, данные частично кешированы
- **Горячий старт** — приложение уже активно, перезапуск из background

**Критические факторы производительности:**
- **`Application`.onCreate()** — блокирует UI-поток, должен содержать только критические инициализации
- **Lazy initialization** — отложенная загрузка компонентов при первом обращении
- **Baseline Profiles** — AOT-компиляция критических путей для 15-30% улучшения производительности
- **App Startup library** — управление порядком инициализации компонентов с зависимостями

**1. Профилирование и анализ**

Используйте Android Profiler и Systrace для выявления узких мест:

```kotlin
// ✅ Трассировка критических участков
Trace.beginSection("DatabaseInit")
initDatabase()
Trace.endSection()

// ✅ Macrobenchmark для точных измерений
@Test
fun startupBenchmark() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(StartupTimingMetric()),
    iterations = 5
) { pressHome(); startActivityAndWait() }
```

Анализируйте метрики: холодный старт (cold), теплый (warm), горячий (hot). Целевые значения для production: холодный старт < 2 сек, теплый < 1 сек.

**2. Оптимизация `Application`.onCreate()**

Критично: только crash reporting и критические системы инициализируются синхронно.

```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Только критическое
        FirebaseCrashlytics.getInstance().setCrashlyticsCollectionEnabled(true)

        // ❌ Плохо: блокирует UI-поток
        // initDatabase()
        // initNetworking()

        // ✅ Отложенная инициализация через App Startup
        AppInitializer.getInstance(this)
            .initializeComponent(WorkManagerInitializer::class.java)
    }
}
```

**3. Jetpack App Startup + Lazy Init**

Используйте App Startup для управления порядком инициализации компонентов:

```kotlin
class NetworkInitializer : Initializer<ApiClient> {
    override fun create(context: Context): ApiClient {
        return ApiClient.Builder()
            .baseUrl(BuildConfig.API_URL)
            .build()
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}

// ✅ Ленивая инициализация через Hilt
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(app: Application): AppDatabase =
        Room.databaseBuilder(app, AppDatabase::class.java, "db")
            .build() // Создание только при первом обращении
}
```

**4. Оптимизация `Activity` startup**

Перенесите тяжелую работу в `ViewModel` + coroutines:

```kotlin
// ❌ Плохо: блокирует onCreate
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        loadUserData() // Синхронная операция!
    }
}

// ✅ Хорошо: async в ViewModel
class MainViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    val userData = repository.getUserDataFlow()
        .stateIn(viewModelScope, SharingStarted.Lazily, null)
}
```

**5. Baseline Profiles**

Используйте Baseline Profiles для AOT-компиляции критических путей:

```kotlin
// baseline-prof.txt
HSPLcom/example/app/MainActivity;-><init>()V
HSPLcom/example/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
```

Эффект: 15-30% улучшение холодного старта через предкомпиляцию.

### Лучшие Практики

- **Измеряйте до и после** — устанавливайте baseline метрики перед оптимизациями
- **Постепенные изменения** — внедряйте оптимизации поэтапно для изоляции эффектов
- **Профилируйте на target устройствах** — тестируйте на устройствах с Android 10+ для Baseline Profiles
- **Мониторьте в production** — отслеживайте startup метрики после релиза
- **Используйте App Startup** — для управления зависимостями инициализации компонентов

### Типичные Ошибки

- **Блокировка UI-потока в onCreate()** — приводит к ANR и плохому UX
- **Инициализация всего сразу** — монолитная загрузка всех компонентов
- **Отсутствие baseline измерений** — невозможно оценить эффективность оптимизаций
- **Игнорирование warm/hot стартов** — фокус только на cold start
- **Ручная инициализация без зависимостей** — race conditions и неправильный порядок

## Answer (EN)

**Approach:** Systematic optimization with measurable results through profiling, deferred initialization, and architectural improvements.

### Theoretical Foundations

**App startup types:**
- **Cold start** — app launches from scratch, requires full initialization
- **Warm start** — app was launched but process was killed, data partially cached
- **Hot start** — app already active, restart from background

**Critical performance factors:**
- **`Application`.onCreate()** — blocks UI thread, should contain only critical initializations
- **Lazy initialization** — deferred loading of components on first access
- **Baseline Profiles** — AOT compilation of critical paths for 15-30% performance improvement
- **App Startup library** — managing component initialization order with dependencies

**1. Profiling and Analysis**

Use Android Profiler and Systrace to identify bottlenecks:

```kotlin
// ✅ Trace critical sections
Trace.beginSection("DatabaseInit")
initDatabase()
Trace.endSection()

// ✅ Macrobenchmark for precise measurements
@Test
fun startupBenchmark() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(StartupTimingMetric()),
    iterations = 5
) { pressHome(); startActivityAndWait() }
```

Analyze metrics: cold start, warm start, hot start. Production targets: cold start < 2s, warm < 1s.

**2. Optimize `Application`.onCreate()**

Critical: only crash reporting and essential systems initialize synchronously.

```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Critical only
        FirebaseCrashlytics.getInstance().setCrashlyticsCollectionEnabled(true)

        // ❌ Bad: blocks UI thread
        // initDatabase()
        // initNetworking()

        // ✅ Deferred init via App Startup
        AppInitializer.getInstance(this)
            .initializeComponent(WorkManagerInitializer::class.java)
    }
}
```

**3. Jetpack App Startup + Lazy Init**

Use App Startup to manage component initialization order:

```kotlin
class NetworkInitializer : Initializer<ApiClient> {
    override fun create(context: Context): ApiClient {
        return ApiClient.Builder()
            .baseUrl(BuildConfig.API_URL)
            .build()
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}

// ✅ Lazy init via Hilt
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(app: Application): AppDatabase =
        Room.databaseBuilder(app, AppDatabase::class.java, "db")
            .build() // Created only on first access
}
```

**4. Optimize `Activity` Startup**

Move heavy work to `ViewModel` + coroutines:

```kotlin
// ❌ Bad: blocks onCreate
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        loadUserData() // Synchronous operation!
    }
}

// ✅ Good: async in ViewModel
class MainViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    val userData = repository.getUserDataFlow()
        .stateIn(viewModelScope, SharingStarted.Lazily, null)
}
```

**5. Baseline Profiles**

Use Baseline Profiles for AOT compilation of critical paths:

```kotlin
// baseline-prof.txt
HSPLcom/example/app/MainActivity;-><init>()V
HSPLcom/example/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
```

Effect: 15-30% cold start improvement through pre-compilation.

### Best Practices

- **Measure before and after** — establish baseline metrics before optimizations
- **Incremental changes** — implement optimizations gradually to isolate effects
- **Profile on target devices** — test on Android 10+ devices for Baseline Profiles
- **Monitor in production** — track startup metrics after release
- **Use App Startup** — for managing component initialization dependencies

### Common Pitfalls

- **Blocking UI thread in onCreate()** — leads to ANR and poor UX
- **Initialize everything at once** — monolithic loading of all components
- **No baseline measurements** — impossible to evaluate optimization effectiveness
- **Ignoring warm/hot starts** — focus only on cold start
- **Manual initialization without dependencies** — race conditions and wrong order

---

## Follow-ups

- How would you profile startup on devices without developer options enabled?
- What trade-offs exist between App Startup library and manual initialization?
- How do you measure startup performance in CI/CD pipeline?
- What's the impact of ProGuard/R8 optimization on startup time?
- How would you prioritize initialization for 20+ SDKs in `Application`.onCreate()?

## References

- Android Baseline Profiles documentation
- Macrobenchmark library guide

## Related Questions

### Prerequisites / Concepts

- [[c-app-startup]]
- [[c-lazy-initialization]]


### Prerequisites
- [[q-what-are-services-used-for--android--medium]] - Understanding Android components

### Related
- [[q-android-lint-tool--android--medium]] - Profiling techniques
