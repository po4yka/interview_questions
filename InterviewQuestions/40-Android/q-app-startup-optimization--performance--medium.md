---
id: 20251011-220003
title: "App Startup Optimization / Оптимизация запуска приложения"
aliases: []

# Classification
topic: android
subtopics: [performance, startup, app-startup, optimization, lazy-init, profiling]
question_kind: practical
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: Original
source_note: App startup optimization best practices

# Workflow & relations
status: draft
moc: moc-android
related: [macrobenchmark-startup, baseline-profiles-optimization, memory-leak-detection]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [android, performance, startup, app-startup, optimization, lazy-init, profiling, difficulty/medium]
---
# Question (EN)
> Optimize app startup time using App Startup library, lazy initialization, content provider consolidation, and deferred task execution.

# Вопрос (RU)
> Оптимизируйте время запуска приложения с помощью библиотеки App Startup, ленивой инициализации, консолидации content provider и отложенного выполнения задач.

---

## Answer (EN)

### Overview

**App startup time** is critical for user experience. Users expect apps to launch quickly, and slow startups lead to poor reviews and abandonment.

**Startup Time Metrics:**
- **Cold startup**: < 500ms (excellent), < 1000ms (acceptable)
- **Warm startup**: < 300ms (excellent), < 500ms (acceptable)
- **Hot startup**: < 100ms (excellent), < 200ms (acceptable)

**Common Startup Bottlenecks:**
1. Application.onCreate() doing too much work
2. Multiple ContentProviders initializing on main thread
3. Synchronous I/O operations
4. Eager library initialization
5. Complex view hierarchies
6. Database/network calls on main thread

### App Startup Library Integration

The **App Startup library** provides a performant way to initialize components at app startup by consolidating ContentProviders and managing dependencies.

#### 1. Setup

**app/build.gradle.kts:**
```kotlin
dependencies {
    implementation("androidx.startup:startup-runtime:1.1.1")
}
```

#### 2. Before: Traditional Initialization

**❌ SLOW: Multiple ContentProviders**

```kotlin
// Traditional approach - each library adds a ContentProvider

// AndroidManifest.xml
<manifest>
    <application>
        <!-- Each ContentProvider adds 20-30ms to startup -->
        <provider
            android:name="com.example.analytics.AnalyticsInitProvider"
            android:authorities="${applicationId}.analytics-init"
            android:exported="false" />

        <provider
            android:name="com.example.crash.CrashReportingInitProvider"
            android:authorities="${applicationId}.crash-init"
            android:exported="false" />

        <provider
            android:name="com.example.ads.AdsInitProvider"
            android:authorities="${applicationId}.ads-init"
            android:exported="false" />

        <provider
            android:name="com.example.messaging.MessagingInitProvider"
            android:authorities="${applicationId}.messaging-init"
            android:exported="false" />
    </application>
</manifest>

// AnalyticsInitProvider.kt
class AnalyticsInitProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // Runs on main thread during app startup
        Analytics.initialize(context!!)  // 50ms
        return true
    }
    // Other required methods...
}

// Result: 4 providers × 25ms average = 100ms added to startup
```

**❌ SLOW: Application.onCreate() doing everything**

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // All on main thread, blocks startup
        initAnalytics()         // 50ms
        initCrashReporting()    // 40ms
        initDatabase()          // 80ms
        initNetworking()        // 60ms
        initImageLoading()      // 30ms
        initLogging()           // 20ms
        loadUserPreferences()   // 45ms
        initPushNotifications() // 70ms

        // Total: 395ms of blocking initialization
    }
}
```

#### 3. After: App Startup Library

**✅ OPTIMIZED: Consolidated initialization**

**Step 1: Create Initializers**

```kotlin
// AnalyticsInitializer.kt
import android.content.Context
import androidx.startup.Initializer

class AnalyticsInitializer : Initializer<AnalyticsService> {

    override fun create(context: Context): AnalyticsService {
        Trace.beginSection("AnalyticsInit")
        val service = AnalyticsService.getInstance()
        service.initialize(context)
        Trace.endSection()
        return service
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        // No dependencies
        return emptyList()
    }
}

// CrashReportingInitializer.kt
class CrashReportingInitializer : Initializer<CrashReportingService> {

    override fun create(context: Context): CrashReportingService {
        Trace.beginSection("CrashReportingInit")
        val service = CrashReportingService()
        service.initialize(context)
        Trace.endSection()
        return service
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        // Initialize after Analytics (for crash metadata)
        return listOf(AnalyticsInitializer::class.java)
    }
}

// DatabaseInitializer.kt
class DatabaseInitializer : Initializer<AppDatabase> {

    override fun create(context: Context): AppDatabase {
        Trace.beginSection("DatabaseInit")
        // Initialize database off main thread
        val database = Room.databaseBuilder(
            context.applicationContext,
            AppDatabase::class.java,
            "app-database"
        )
            .fallbackToDestructiveMigration()
            .build()

        // Pre-warm database connection in background
        GlobalScope.launch(Dispatchers.IO) {
            database.query("SELECT 1", null)
        }

        Trace.endSection()
        return database
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return emptyList()
    }
}

// NetworkInitializer.kt
class NetworkInitializer : Initializer<OkHttpClient> {

    override fun create(context: Context): OkHttpClient {
        Trace.beginSection("NetworkInit")
        val client = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(LoggingInterceptor())
            .build()
        Trace.endSection()
        return client
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        // Initialize after logging
        return listOf(LoggingInitializer::class.java)
    }
}

// LoggingInitializer.kt
class LoggingInitializer : Initializer<LoggingService> {

    override fun create(context: Context): LoggingService {
        Trace.beginSection("LoggingInit")
        val service = LoggingService()
        service.initialize(
            context = context,
            level = if (BuildConfig.DEBUG) Log.DEBUG else Log.INFO
        )
        Trace.endSection()
        return service
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return emptyList()
    }
}
```

**Step 2: Declare in Manifest**

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <application>
        <!-- Single ContentProvider for all initialization -->
        <provider
            android:name="androidx.startup.InitializationProvider"
            android:authorities="${applicationId}.androidx-startup"
            android:exported="false"
            tools:node="merge">

            <!-- Declare all initializers -->
            <meta-data
                android:name="com.example.startup.AnalyticsInitializer"
                android:value="androidx.startup" />

            <meta-data
                android:name="com.example.startup.CrashReportingInitializer"
                android:value="androidx.startup" />

            <meta-data
                android:name="com.example.startup.DatabaseInitializer"
                android:value="androidx.startup" />

            <meta-data
                android:name="com.example.startup.NetworkInitializer"
                android:value="androidx.startup" />

            <meta-data
                android:name="com.example.startup.LoggingInitializer"
                android:value="androidx.startup" />
        </provider>
    </application>
</manifest>
```

**Step 3: Access Initialized Components**

```kotlin
class MainActivity : AppCompatActivity() {

    // Get initialized components
    private val database by lazy {
        AppInitializer.getInstance(this)
            .initializeComponent(DatabaseInitializer::class.java)
    }

    private val analytics by lazy {
        AppInitializer.getInstance(this)
            .initializeComponent(AnalyticsInitializer::class.java)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Components are already initialized
        analytics.trackEvent("screen_view", mapOf("screen" to "main"))
    }
}
```

**Result: 100ms (4 providers) → 25ms (1 provider) = 75ms improvement**

### Lazy Initialization Pattern

Defer initialization until actually needed, not at app startup.

#### 1. Lazy SDK Initialization

**Before: Eager initialization**

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Initialized even if user never uses these features
        initPushNotifications()  // 70ms
        initInAppMessaging()     // 50ms
        initRemoteConfig()       // 60ms
        initAds()                // 80ms

        // Total: 260ms wasted if features not used
    }
}
```

**After: Lazy initialization**

```kotlin
class MyApplication : Application() {

    // Lazy initialization - only when accessed
    val pushNotifications by lazy {
        Trace.beginSection("InitPushNotifications")
        PushNotificationService().apply {
            initialize(this@MyApplication)
        }.also {
            Trace.endSection()
        }
    }

    val inAppMessaging by lazy {
        Trace.beginSection("InitInAppMessaging")
        InAppMessagingService().apply {
            initialize(this@MyApplication)
        }.also {
            Trace.endSection()
        }
    }

    val remoteConfig by lazy {
        Trace.beginSection("InitRemoteConfig")
        RemoteConfigService().apply {
            initialize(this@MyApplication)
        }.also {
            Trace.endSection()
        }
    }

    override fun onCreate() {
        super.onCreate()
        // No initialization here - happens when needed
    }
}

// Usage: Initialization happens on first access
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Only initialized when user opts in to push
        findViewById<Button>(R.id.enable_push).setOnClickListener {
            (application as MyApplication).pushNotifications.subscribe()
        }
    }
}
```

#### 2. Lazy Dependency Injection (Hilt)

```kotlin
// Provide lazy instances in Hilt modules

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context
    ): Lazy<AppDatabase> = lazy {
        Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app-database"
        ).build()
    }

    @Provides
    @Singleton
    fun provideAnalytics(
        @ApplicationContext context: Context
    ): Lazy<AnalyticsService> = lazy {
        AnalyticsService().apply {
            initialize(context)
        }
    }
}

// Inject lazy instances
@AndroidEntryPoint
class MyViewModel @Inject constructor(
    private val database: Lazy<AppDatabase>,  // Not initialized yet
    private val analytics: Lazy<AnalyticsService>
) : ViewModel() {

    fun loadData() {
        viewModelScope.launch {
            // Database initialized on first access
            val data = database.value.userDao().getAll()
        }
    }

    fun trackEvent(event: String) {
        // Analytics initialized on first access
        analytics.value.trackEvent(event)
    }
}
```

### Deferred Task Execution with WorkManager

Move non-critical initialization to background using WorkManager.

#### 1. Deferred Initialization

```kotlin
// DeferredInitializer.kt
class DeferredInitializer : Initializer<Unit> {

    override fun create(context: Context) {
        // Schedule non-critical work to run after startup
        scheduleBackgroundInit(context)
    }

    private fun scheduleBackgroundInit(context: Context) {
        val constraints = Constraints.Builder()
            .setRequiresBatteryNotLow(true)  // Only when battery is OK
            .build()

        val initWork = OneTimeWorkRequestBuilder<BackgroundInitWorker>()
            .setConstraints(constraints)
            .setInitialDelay(5, TimeUnit.SECONDS)  // Delay 5s after startup
            .build()

        WorkManager.getInstance(context).enqueueUniqueWork(
            "background_init",
            ExistingWorkPolicy.KEEP,
            initWork
        )
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

// BackgroundInitWorker.kt
class BackgroundInitWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            // Non-critical initialization
            Trace.beginSection("BackgroundInit")

            // Warm up caches
            warmUpImageCache()

            // Sync remote config
            syncRemoteConfig()

            // Pre-fetch user preferences
            prefetchUserData()

            // Clean up old files
            cleanupOldFiles()

            Trace.endSection()
            Result.success()
        } catch (e: Exception) {
            Log.e("BackgroundInit", "Failed", e)
            Result.retry()
        }
    }

    private suspend fun warmUpImageCache() {
        // Pre-load frequently used images
        val imageUrls = listOf(
            "https://example.com/logo.png",
            "https://example.com/default-avatar.png"
        )

        imageUrls.forEach { url ->
            Coil.imageLoader(applicationContext)
                .execute(ImageRequest.Builder(applicationContext)
                    .data(url)
                    .build())
        }
    }

    private suspend fun syncRemoteConfig() {
        val remoteConfig = Firebase.remoteConfig
        remoteConfig.fetchAndActivate().await()
    }

    private suspend fun prefetchUserData() {
        // Load user data into cache
        val userRepository = (applicationContext as MyApplication).userRepository
        userRepository.prefetchUserData()
    }

    private fun cleanupOldFiles() {
        val cacheDir = applicationContext.cacheDir
        val threshold = System.currentTimeMillis() - 7 * 24 * 60 * 60 * 1000 // 7 days

        cacheDir.listFiles()?.forEach { file ->
            if (file.lastModified() < threshold) {
                file.delete()
            }
        }
    }
}
```

### Startup Time Measurement

#### 1. Systrace/Perfetto Profiling

**Add custom trace sections:**

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        Trace.beginSection("Application.onCreate")
        super.onCreate()

        Trace.beginSection("InitEssentialServices")
        initCrashReporting()
        initLogging()
        Trace.endSection()

        Trace.endSection()
    }
}

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        Trace.beginSection("MainActivity.onCreate")
        super.onCreate(savedInstanceState)

        Trace.beginSection("SetContentView")
        setContentView(R.layout.activity_main)
        Trace.endSection()

        Trace.beginSection("InitializeUI")
        setupRecyclerView()
        loadInitialData()
        Trace.endSection()

        Trace.endSection()
    }
}
```

**Capture trace:**
```bash
# Start recording
adb shell am start-activity com.example.myapp/.MainActivity &
python $ANDROID_HOME/platform-tools/systrace/systrace.py \
    --time=10 \
    -o trace.html \
    sched gfx view wm am app

# Open trace.html in Chrome
chrome trace.html
```

#### 2. MainLooper Slow Log

**Monitor main thread blocking:**

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            // Log operations taking > 100ms on main thread
            Looper.getMainLooper().setMessageLogging(object : Printer {
                private var startTime = 0L

                override fun println(message: String) {
                    if (message.startsWith(">")) {
                        startTime = SystemClock.uptimeMillis()
                    } else if (message.startsWith("<")) {
                        val duration = SystemClock.uptimeMillis() - startTime
                        if (duration > 100) {
                            Log.w("MainLooper", "Long operation: ${duration}ms\n$message")
                        }
                    }
                }
            })
        }
    }
}
```

#### 3. Reportfully Named Metrics

```kotlin
class StartupMetrics {

    companion object {
        private var appStartTime = 0L
        private var firstActivityTime = 0L
        private var firstFrameTime = 0L

        fun recordAppStart() {
            appStartTime = SystemClock.elapsedRealtime()
        }

        fun recordFirstActivity() {
            firstActivityTime = SystemClock.elapsedRealtime()
            logMetric("time_to_first_activity", firstActivityTime - appStartTime)
        }

        fun recordFirstFrame() {
            firstFrameTime = SystemClock.elapsedRealtime()
            logMetric("time_to_first_frame", firstFrameTime - appStartTime)
        }

        private fun logMetric(name: String, value: Long) {
            Log.d("StartupMetrics", "$name: ${value}ms")

            // Send to analytics
            Firebase.analytics.logEvent(name) {
                param("duration_ms", value)
            }

            // Send to performance monitoring
            val trace = Firebase.performance.newTrace(name)
            trace.putMetric("duration_ms", value)
            trace.stop()
        }
    }
}

// Usage
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        StartupMetrics.recordAppStart()
    }
}

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        StartupMetrics.recordFirstActivity()

        window.decorView.viewTreeObserver.addOnDrawListener {
            StartupMetrics.recordFirstFrame()
        }
    }
}
```

### Complete Optimization Example

#### Before Optimization

**Baseline measurements:**
```
Cold startup: 1,250ms
Application.onCreate(): 395ms
ContentProvider init: 100ms
Activity.onCreate(): 280ms
First frame: 475ms

Bottlenecks:
- 8 ContentProviders: 200ms
- Synchronous database open: 80ms
- Eager library init: 260ms
- Complex XML layout: 120ms
```

**Code:**

```kotlin
// MyApplication.kt (BEFORE)
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // All eager initialization
        FirebaseApp.initializeApp(this)
        initAnalytics()
        initCrashReporting()
        initDatabase()
        initNetworking()
        initImageLoading()
        initLogging()
        loadUserPreferences()
        initPushNotifications()
        initInAppMessaging()
        initRemoteConfig()
        initAds()
    }
}

// AndroidManifest.xml (BEFORE)
<application>
    <provider android:name=".analytics.AnalyticsProvider" ... />
    <provider android:name=".crash.CrashProvider" ... />
    <provider android:name=".ads.AdsProvider" ... />
    <provider android:name=".messaging.MessagingProvider" ... />
    <provider android:name=".config.RemoteConfigProvider" ... />
    <provider android:name=".auth.AuthProvider" ... />
    <provider android:name=".database.DatabaseProvider" ... />
    <provider android:name=".network.NetworkProvider" ... />
</application>
```

#### After Optimization

**Optimized measurements:**
```
Cold startup: 520ms (-58%)
Application.onCreate(): 25ms (-94%)
ContentProvider init: 25ms (-75%)
Activity.onCreate(): 180ms (-36%)
First frame: 290ms (-39%)

Improvements:
- 1 ContentProvider (App Startup): -175ms
- Lazy initialization: -260ms
- Deferred tasks (WorkManager): -150ms
- Jetpack Compose: -95ms
```

**Code:**

```kotlin
// MyApplication.kt (AFTER)
class MyApplication : Application() {

    // Lazy initialization
    val analytics by lazy { initAnalytics() }
    val pushNotifications by lazy { initPushNotifications() }
    val inAppMessaging by lazy { initInAppMessaging() }

    override fun onCreate() {
        super.onCreate()

        // Only essential initialization
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }

        // Everything else via App Startup library
    }
}

// App Startup initializers
class EssentialInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        // Critical services only
        CrashReporting.initialize(context)
        Logging.initialize(context)
    }

    override fun dependencies() = emptyList<Class<out Initializer<*>>>()
}

class DeferredInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        // Schedule background initialization
        val work = OneTimeWorkRequestBuilder<BackgroundInitWorker>()
            .setInitialDelay(5, TimeUnit.SECONDS)
            .build()

        WorkManager.getInstance(context).enqueue(work)
    }

    override fun dependencies() = listOf(EssentialInitializer::class.java)
}

// AndroidManifest.xml (AFTER)
<application>
    <!-- Single provider for all initialization -->
    <provider
        android:name="androidx.startup.InitializationProvider"
        android:authorities="${applicationId}.androidx-startup"
        android:exported="false">
        <meta-data
            android:name=".startup.EssentialInitializer"
            android:value="androidx.startup" />
        <meta-data
            android:name=".startup.DeferredInitializer"
            android:value="androidx.startup" />
    </provider>
</application>

// MainActivity.kt (AFTER) - Jetpack Compose
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MyAppTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    // Lazy loading
    LazyColumn {
        item { HeaderSection() }
        items(data) { item ->
            ItemCard(item)
        }
    }
}
```

### Best Practices

1. **Measure First, Optimize Second**: Use Perfetto/systrace to identify actual bottlenecks
2. **Consolidate ContentProviders**: Use App Startup library to merge multiple providers
3. **Lazy Initialization**: Don't initialize what you don't immediately need
4. **Defer Non-Critical Work**: Use WorkManager for background initialization
5. **Minimize Application.onCreate()**: Should complete in < 50ms
6. **Avoid Synchronous I/O**: Move disk/network operations off main thread
7. **Use Baseline Profiles**: Improve startup with AOT compilation
8. **Simplify First Screen**: Complex layouts delay first frame
9. **Monitor Startup Time**: Track metrics in production with Firebase Performance
10. **Test on Low-End Devices**: Startup issues are magnified on slow devices
11. **Warm Critical Paths**: Pre-load frequently accessed data in background
12. **Use Trace Sections**: Add custom traces to measure initialization steps

### Common Pitfalls

1. **Optimizing Without Profiling**: Don't guess what's slow, measure it
2. **Eager Library Initialization**: Initialize libraries only when needed
3. **Blocking Main Thread**: All I/O must be asynchronous during startup
4. **Too Many ContentProviders**: Each adds 20-30ms, consolidate with App Startup
5. **Complex Application.onCreate()**: Should be minimal, defer everything else
6. **Synchronous Database Opening**: Open database asynchronously or lazily
7. **Large Initial Screen**: First screen should be simple and fast to render
8. **Preloading Everything**: Only preload critical resources
9. **Not Testing Cold Startup**: Most impactful startup type for users
10. **Ignoring Configuration Changes**: Test startup after rotation, process death

## Ответ (RU)

### Обзор

**Время запуска приложения** критически важно для пользовательского опыта. Пользователи ожидают быстрого запуска приложений, а медленные запуски приводят к плохим отзывам и отказам от использования.

**Метрики времени запуска:**
- **Холодный запуск**: < 500мс (отлично), < 1000мс (приемлемо)
- **Теплый запуск**: < 300мс (отлично), < 500мс (приемлемо)
- **Горячий запуск**: < 100мс (отлично), < 200мс (приемлемо)

**Распространенные узкие места при запуске:**
1. Application.onCreate() делает слишком много работы
2. Множественные ContentProvider инициализируются в главном потоке
3. Синхронные I/O операции
4. Энергичная инициализация библиотек
5. Сложные иерархии view
6. Вызовы базы данных/сети в главном потоке

[All content sections remain similar to English version with Russian translations...]

### Лучшие практики

1. **Сначала измеряйте, потом оптимизируйте**: Используйте Perfetto/systrace для выявления фактических узких мест
2. **Консолидируйте ContentProvider**: Используйте библиотеку App Startup для объединения нескольких провайдеров
3. **Ленивая инициализация**: Не инициализируйте то, что не нужно немедленно
4. **Откладывайте некритичную работу**: Используйте WorkManager для фоновой инициализации
5. **Минимизируйте Application.onCreate()**: Должен завершаться за < 50мс
6. **Избегайте синхронного I/O**: Переносите операции диска/сети из главного потока
7. **Используйте Baseline Profiles**: Улучшите запуск с помощью AOT компиляции
8. **Упрощайте первый экран**: Сложные layouts задерживают первый кадр
9. **Мониторьте время запуска**: Отслеживайте метрики в продакшне с Firebase Performance
10. **Тестируйте на слабых устройствах**: Проблемы запуска усиливаются на медленных устройствах
11. **Прогревайте критические пути**: Предзагружайте часто используемые данные в фоне
12. **Используйте секции трассировки**: Добавляйте пользовательские трейсы для измерения шагов инициализации

### Распространенные ошибки

1. **Оптимизация без профилирования**: Не гадайте что медленно, измеряйте это
2. **Энергичная инициализация библиотек**: Инициализируйте библиотеки только когда нужно
3. **Блокировка главного потока**: Весь I/O должен быть асинхронным во время запуска
4. **Слишком много ContentProvider**: Каждый добавляет 20-30мс, консолидируйте с App Startup
5. **Сложный Application.onCreate()**: Должен быть минимальным, откладывайте все остальное
6. **Синхронное открытие БД**: Открывайте базу данных асинхронно или лениво
7. **Большой начальный экран**: Первый экран должен быть простым и быстро отрисовываться
8. **Предзагрузка всего**: Предзагружайте только критические ресурсы
9. **Не тестирование холодного запуска**: Самый важный тип запуска для пользователей
10. **Игнорирование изменений конфигурации**: Тестируйте запуск после поворота, смерти процесса

---

## References
- [App Startup Library](https://developer.android.com/topic/libraries/app-startup)
- [App Startup Time](https://developer.android.com/topic/performance/vitals/launch-time)
- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Perfetto Tracing](https://perfetto.dev/)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview

### Related (Medium)
- [[q-macrobenchmark-startup--performance--medium]] - Performance
- [[q-app-startup-library--android--medium]] - App Startup
- [[q-baseline-profiles-optimization--performance--medium]] - Performance
- [[q-app-size-optimization--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview

### Related (Medium)
- [[q-macrobenchmark-startup--performance--medium]] - Performance
- [[q-app-startup-library--android--medium]] - App Startup
- [[q-baseline-profiles-optimization--performance--medium]] - Performance
- [[q-app-size-optimization--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview

### Related (Medium)
- [[q-macrobenchmark-startup--performance--medium]] - Performance
- [[q-app-startup-library--android--medium]] - App Startup
- [[q-baseline-profiles-optimization--performance--medium]] - Performance
- [[q-app-size-optimization--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose