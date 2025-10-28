---
id: 20251012-1227138
title: "Fix Slow App Startup Legacy / Исправление медленного запуска приложения"
aliases: ["Fix Slow App Startup in Legacy Project", "Исправление медленного запуска приложения в легаси-проекте"]
topic: android
subtopics: [performance-startup, architecture-modularization, profiling]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-app-startup, c-lazy-initialization, q-what-are-services-used-for--android--medium, q-android-profiling-tools--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/performance-startup, android/architecture-modularization, android/profiling, app-startup, difficulty/hard, lazy-init, legacy-code, optimization]
---

# Вопрос (RU)

Что делать, если нужно исправить медленный запуск приложения в legacy-проекте?

# Question (EN)

How would you approach fixing slow app startup in a legacy Android project?

---

## Ответ (RU)

**Подход:** Систематическая оптимизация с измеримыми результатами через профилирование, отложенную инициализацию и архитектурные улучшения.

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

**2. Оптимизация Application.onCreate()**

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

**4. Оптимизация Activity startup**

Перенесите тяжелую работу в ViewModel + coroutines:

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

## Answer (EN)

**Approach:** Systematic optimization with measurable results through profiling, deferred initialization, and architectural improvements.

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

**2. Optimize Application.onCreate()**

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

**4. Optimize Activity Startup**

Move heavy work to ViewModel + coroutines:

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

---

## Follow-ups

- How would you profile startup on devices without developer options enabled?
- What trade-offs exist between App Startup library and manual initialization?
- How do you measure startup performance in CI/CD pipeline?
- What's the impact of ProGuard/R8 optimization on startup time?
- How would you prioritize initialization for 20+ SDKs in Application.onCreate()?

## References

- [[c-app-startup]]
- [[c-lazy-initialization]]
- [[c-baseline-profiles]]
- Android Baseline Profiles documentation
- Macrobenchmark library guide

## Related Questions

### Prerequisites
- [[q-what-are-services-used-for--android--medium]] - Understanding Android components
- [[q-android-lifecycle-basics--android--easy]] - Activity/Application lifecycle

### Related
- [[q-android-profiling-tools--android--medium]] - Profiling techniques
- [[q-optimize-memory-leaks-android--android--hard]] - Memory optimization

### Advanced
- [[q-implement-custom-classloader-android--android--hard]] - Advanced initialization control
- [[q-android-strictmode-anr-debugging--android--hard]] - Performance monitoring
