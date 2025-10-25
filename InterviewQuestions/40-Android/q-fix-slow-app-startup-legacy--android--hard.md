---
id: 20251012-1227138
title: "Fix Slow App Startup Legacy / Исправление медленного запуска приложения"
topic: android
difficulty: hard
status: draft
moc: moc-android
related: [q-fakes-vs-mocks-testing--testing--medium, q-what-are-services-used-for--android--medium, q-what-to-put-in-state-for-initial-list--android--easy]
created: 2025-10-15
tags: [android/performance, app-startup, difficulty/hard, lazy-init, legacy-code, optimization, performance]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:51:59 pm
---

# Что Делать Если Надо Исправить Долгий Запуск Приложения В Legacy Проекте?

**English**: What to do if you need to fix slow app startup in a legacy project?

## Answer (EN)
**1. Analysis and Data Collection**

Use profiling tools to collect data on execution time of different code parts during app startup.

```kotlin
// Add trace points
Trace.beginSection("AppStartup")
// Startup code
Trace.endSection()
```

Analyze logs to find bottlenecks and identify which operations take the most time.

Check all dependencies and libraries used in the project to understand if they cause delays.

**2. Identify Problem Areas**

Check which objects are initialized at startup and assess if they're all truly necessary at this stage.

```kotlin
// BAD - Everything initialized at startup
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        initDatabase()        // Slow!
        initNetworking()      // Slow!
        initAnalytics()       // Slow!
        loadUserPreferences() // Slow!
        setupNotifications()  // Slow!
    }
}
```

Determine if heavy network requests or database operations happen during startup.

Check if large resources (images, files) are loaded at startup.

**3. Code Optimization**

**Move non-critical initialization to later stages:**

```kotlin
// GOOD - Lazy initialization
class MyApplication : Application() {
    // Initialize only critical components
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            setupDebugTools()  // Only in debug
        }
        // Defer other init
    }

    // Lazy database
    val database by lazy { createDatabase() }

    // Initialize on first use
    fun getNetworkClient() = networkClient ?: createNetworkClient().also {
        networkClient = it
    }
}
```

**Use asynchronous operations for heavy tasks:**

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Critical sync init
        setupCrashReporting()

        // Non-critical async init
        CoroutineScope(Dispatchers.Default).launch {
            initAnalytics()
            loadRemoteConfig()
            preloadData()
        }
    }
}
```

**4. Use Architectural Approaches**

**Dependency Injection with Dagger/Hilt:**

```kotlin
@HiltAndroidApp
class MyApp : Application()

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(app: Application): Database {
        // Lazy database creation
        return Room.databaseBuilder(app, Database::class.java, "db")
            .build()
    }
}
```

**Move heavy logic from startup Activity:**

```kotlin
// BAD
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        loadUserData()      // Blocks UI!
        fetchRemoteConfig() // Blocks UI!
    }
}

// GOOD
class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Load in background
        viewModel.loadData()
    }
}

class MainViewModel : ViewModel() {
    init {
        viewModelScope.launch {
            // Async loading
            loadUserData()
        }
    }
}
```

**5. Data Caching**

```kotlin
class DataRepository(private val cache: Cache) {
    suspend fun getUserData(): UserData {
        // Check cache first
        cache.getUserData()?.let { return it }

        // Load from network
        return api.getUserData().also {
            cache.saveUserData(it)
        }
    }
}
```

**6. Resource Optimization**

Optimize images and other resources to reduce loading time.

```kotlin
// Use WebP instead of PNG/JPG
// Reduce image dimensions
// Use vector drawables where possible
```

**7. App Startup Library:**

```kotlin
// build.gradle
implementation "androidx.startup:startup-runtime:1.1.1"

// Initializer
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.getInstance(context).apply {
            setAnalyticsCollectionEnabled(true)
        }
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return emptyList()  // No dependencies
    }
}
```

**Measurement:**

```kotlin
// Before optimization
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val startTime = SystemClock.elapsedRealtime()

        // Initialization
        performStartup()

        val duration = SystemClock.elapsedRealtime() - startTime
        Log.d("Startup", "App startup took: ${duration}ms")
    }
}
```

**Summary Checklist:**

-  Profile startup with Android Profiler
-  Move non-critical init to lazy/background
-  Use async operations for heavy tasks
-  Implement dependency injection
-  Cache frequently used data
-  Optimize resources (images, assets)
-  Defer library initialization
-  Measure improvements with benchmarks

## Ответ (RU)
**Анализ и сбор данных:** Используйте инструменты профилирования для сбора данных о времени выполнения различных частей кода при запуске приложения. Проанализируйте логи чтобы найти узкие места.

**Идентификация проблемных зон:** Проверьте какие объекты инициализируются при старте и оцените действительно ли все они необходимы на этом этапе.

**Оптимизация:** Перенесите инициализацию объектов которые не нужны сразу на более поздние этапы. Используйте асинхронные операции для выполнения тяжелых задач в фоне.

**Использование архитектурных подходов:** Внедрение зависимостей с использованием Dagger/Hilt. Перенос тяжелой логики из стартовой активности в фоновые сервисы или ViewModel.

**Кэширование данных:** Используйте кэширование данных которые не нужно запрашивать каждый раз при запуске.

## Related Questions

- [[q-what-are-services-used-for--android--medium]]
- [[q-what-to-put-in-state-for-initial-list--android--easy]]
- [[q-fakes-vs-mocks-testing--android--medium]]
