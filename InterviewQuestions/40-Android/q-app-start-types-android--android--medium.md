---
id: 20251012-122782
title: "App Start Types Android / Типы запуска приложения Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [performance, app-startup, cold-start, warm-start, hot-start, optimization, difficulty/medium]
---
# Hot, Warm, and Cold App Start in Android

**Сложность**: Medium
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> What are the differences between hot, warm, and cold app starts in Android? How do you optimize each type?

# Вопрос (RU)
> В чем разница между горячим, теплым и холодным запуском приложения в Android? Как оптимизировать каждый тип?

---

## Answer (EN)

App startup time directly impacts user experience. Android categorizes app launches into three types based on what's already in memory and what needs to be loaded.

#### 1. **Cold Start**

App is started from scratch. The system process creates the app process.

**What Happens:**

```
1. System loads and launches app
2. Creates app process
3. Creates Application object
4. Launches main thread
5. Creates main Activity
6. Inflates views
7. Lays out screen
8. Performs initial draw
```

**Timeline:**

```kotlin
// Measured from:
// - User taps app icon
// To:
// - First frame is fully drawn

// Phases:
System.currentTimeMillis() // App clicked
↓
Application.onCreate() // ~500ms (includes system overhead)
↓
Activity.onCreate()
↓
Activity.onStart()
↓
Activity.onResume()
↓
View.onMeasure()
↓
View.onLayout()
↓
View.onDraw()
↓
reportFullyDrawn() // App fully loaded
```

**Measuring Cold Start:**

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        val startTime = System.currentTimeMillis()

        // Critical initialization only
        initializeCritical()

        val endTime = System.currentTimeMillis()
        Log.d("ColdStart", "Application.onCreate took ${endTime - startTime}ms")
    }
}

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        val startTime = System.currentTimeMillis()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val endTime = System.currentTimeMillis()
        Log.d("ColdStart", "Activity.onCreate took ${endTime - startTime}ms")
    }

    override fun onResume() {
        super.onResume()

        // Report when app is fully functional
        window.decorView.post {
            reportFullyDrawn()
        }
    }
}
```

**Optimization Strategies:**

```kotlin
// 1. Lazy initialization
class OptimizedApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Only critical initialization
        FirebaseCrashlytics.getInstance()

        // Defer non-critical work
        deferInitialization()
    }

    private fun deferInitialization() {
        Handler(Looper.getMainLooper()).post {
            // Post-startup initialization
            initializeAnalytics()
            initializeAds()
        }
    }
}

// 2. Use App Startup library
class CrashlyticsInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        FirebaseCrashlytics.getInstance().setCrashlyticsCollectionEnabled(true)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

// 3. Splash screen with loading indicator
class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Use custom theme with windowBackground
        setTheme(R.style.AppTheme)
        super.onCreate(savedInstanceState)

        // No setContentView needed
        // windowBackground drawable shows immediately

        lifecycleScope.launch {
            // Perform initialization
            initializeApp()

            // Navigate to main activity
            startActivity(Intent(this@SplashActivity, MainActivity::class.java))
            finish()
        }
    }
}

// res/values/styles.xml
<style name="SplashTheme" parent="Theme.AppCompat.NoActionBar">
    <item name="android:windowBackground">@drawable/splash_background</item>
    <item name="android:windowNoTitle">true</item>
    <item name="android:windowFullscreen">true</item>
</style>

// 4. Optimize layout inflation
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Use ViewBinding instead of findViewById
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Or use Jetpack Compose (no inflation needed)
        // setContent {
        //     MainScreen()
        // }
    }
}

// 5. ViewStub for rarely used views
<ViewStub
    android:id="@+id/stub_import"
    android:layout="@layout/progress_overlay"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

// Inflate only when needed
binding.stubImport.inflate()
```

#### 2. **Warm Start**

App's process is in memory, but Activity needs to be recreated.

**What Happens:**

```
1. System brings process to foreground
2. Activity.onCreate() is called
3. Inflates views
4. Lays out screen
5. Performs draw
```

**Scenarios:**
- User backs out of app, then returns
- System destroys Activity due to memory pressure
- Configuration change (if not handled)

**Timeline:**

```kotlin
// Faster than cold start (no process creation)
// Measured from:
// - User taps app in recents
// To:
// - Activity is fully drawn

Activity.onCreate() // ~300ms
↓
Activity.onStart()
↓
Activity.onRestoreInstanceState() // If state was saved
↓
Activity.onResume()
↓
View inflation and drawing
```

**Measuring Warm Start:**

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        val isWarmStart = savedInstanceState != null
        Log.d("WarmStart", "Is warm start: $isWarmStart")

        val startTime = System.nanoTime()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (savedInstanceState != null) {
            // Restoring from saved state
            restoreState(savedInstanceState)
        } else {
            // Fresh start
            initializeState()
        }

        val duration = (System.nanoTime() - startTime) / 1_000_000
        Log.d("WarmStart", "Activity creation took ${duration}ms")
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save minimal state only
        outState.putInt("current_page", currentPage)
    }

    private fun restoreState(savedState: Bundle) {
        currentPage = savedState.getInt("current_page")
    }
}
```

**Optimization Strategies:**

```kotlin
// 1. Efficient state restoration
class OptimizedActivity : AppCompatActivity() {

    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ViewModel survives configuration changes
        // No need to restore complex state
        viewModel.data.observe(this) { data ->
            updateUI(data)
        }
    }

    // Only save minimal UI state
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("scroll_position", getScrollPosition())
    }
}

// 2. Retain fragments (legacy, prefer ViewModel)
class RetainedFragment : Fragment() {
    init {
        retainInstance = true // Deprecated in favor of ViewModel
    }
}

// 3. Handle configuration changes manually (specific cases)
// AndroidManifest.xml
<activity
    android:name=".VideoPlayerActivity"
    android:configChanges="orientation|screenSize|keyboardHidden">

class VideoPlayerActivity : AppCompatActivity() {
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        // Handle configuration change without recreating Activity
        adjustLayout(newConfig.orientation)
    }
}

// 4. Optimize view inflation
@Composable
fun FastScreen() {
    // Compose is faster than XML inflation
    // No parsing, no reflection
    LazyColumn {
        items(items) { item ->
            ItemRow(item)
        }
    }
}
```

#### 3. **Hot Start**

App is already in memory and Activity is in foreground or recent background.

**What Happens:**

```
1. Activity.onStart() is called
2. Activity.onResume() is called
3. No view inflation needed (views still in memory)
```

**Scenarios:**
- User presses Home, then returns
- User switches to another app briefly
- User returns from another Activity in same app

**Timeline:**

```kotlin
// Fastest startup
// Measured from:
// - User returns to app
// To:
// - Activity.onResume() completes

Activity.onStart() // ~50ms
↓
Activity.onResume()
```

**Measuring Hot Start:**

```kotlin
class MainActivity : AppCompatActivity() {

    private var pauseTime = 0L
    private var resumeTime = 0L

    override fun onPause() {
        pauseTime = System.currentTimeMillis()
        super.onPause()
        Log.d("HotStart", "Activity paused at $pauseTime")
    }

    override fun onResume() {
        resumeTime = System.currentTimeMillis()
        super.onResume()

        val timeSincePause = resumeTime - pauseTime
        if (pauseTime > 0 && timeSincePause < 1000) {
            Log.d("HotStart", "Hot start: ${timeSincePause}ms since pause")
        }
    }

    override fun onStop() {
        super.onStop()
        Log.d("HotStart", "Activity stopped")
    }

    override fun onStart() {
        val startTime = System.currentTimeMillis()
        super.onStart()
        val duration = System.currentTimeMillis() - startTime
        Log.d("HotStart", "onStart took ${duration}ms")
    }
}
```

**Optimization Strategies:**

```kotlin
// 1. Minimize work in onResume()
class OptimizedActivity : AppCompatActivity() {

    override fun onResume() {
        super.onResume()

        //  Don't do heavy work here
        // loadDataFromNetwork()
        // processLargeDataset()

        //  Only update UI if needed
        refreshUIIfNeeded()
    }

    private fun refreshUIIfNeeded() {
        // Check if data is stale
        val lastUpdate = viewModel.lastUpdateTime
        val now = System.currentTimeMillis()

        if (now - lastUpdate > 60_000) {
            // Only refresh if data is older than 1 minute
            viewModel.refreshData()
        }
    }
}

// 2. Use lifecycle-aware components
class LocationActivity : AppCompatActivity() {

    private val locationObserver = LocationObserver()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Automatically start/stop based on lifecycle
        lifecycle.addObserver(locationObserver)
    }
}

class LocationObserver : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        startLocationUpdates()
    }

    override fun onPause(owner: LifecycleOwner) {
        stopLocationUpdates()
    }
}

// 3. Efficient data refresh
class FeedViewModel : ViewModel() {

    private val _posts = MutableStateFlow<List<Post>>(emptyList())
    val posts: StateFlow<List<Post>> = _posts

    private var lastRefreshTime = 0L
    private val refreshIntervalMs = 30_000L // 30 seconds

    fun onResume() {
        val now = System.currentTimeMillis()

        if (now - lastRefreshTime > refreshIntervalMs) {
            refreshPosts()
        }
    }

    private fun refreshPosts() {
        viewModelScope.launch {
            val newPosts = repository.getPosts()
            _posts.value = newPosts
            lastRefreshTime = System.currentTimeMillis()
        }
    }
}
```

#### 4. **Comparison and Measurement**

```kotlin
object StartupMetrics {
    private var appStartTime = 0L
    private var firstActivityCreated = 0L
    private var firstFrameDrawn = 0L

    fun recordAppStart() {
        appStartTime = System.currentTimeMillis()
    }

    fun recordFirstActivityCreated() {
        firstActivityCreated = System.currentTimeMillis()
        val processStartTime = firstActivityCreated - appStartTime
        Log.d("Startup", "Process start to Activity.onCreate: ${processStartTime}ms")

        // Send to analytics
        Analytics.logStartupTime("process_start", processStartTime)
    }

    fun recordFirstFrameDrawn() {
        firstFrameDrawn = System.currentTimeMillis()
        val totalStartTime = firstFrameDrawn - appStartTime
        Log.d("Startup", "Total cold start time: ${totalStartTime}ms")

        Analytics.logStartupTime("cold_start", totalStartTime)
    }
}

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        StartupMetrics.recordAppStart()
    }
}

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        StartupMetrics.recordFirstActivityCreated()
        setContentView(R.layout.activity_main)
    }

    override fun onResume() {
        super.onResume()
        window.decorView.post {
            StartupMetrics.recordFirstFrameDrawn()
            reportFullyDrawn()
        }
    }
}
```

**Using ADB to Measure:**

```bash
# Measure cold start
adb shell am force-stop com.example.app
adb shell am start -W com.example.app/.MainActivity

# Output:
# Starting: Intent { act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] cmp=com.example.app/.MainActivity }
# Status: ok
# Activity: com.example.app/.MainActivity
# ThisTime: 856
# TotalTime: 856
# WaitTime: 872
# Complete

# ThisTime: Time to launch this specific Activity
# TotalTime: Time including previous activities (if any)
# WaitTime: Time system took to start process + TotalTime
```

### Performance Targets

| Start Type | Target Time | Acceptable | Slow |
|------------|-------------|------------|------|
| Cold Start | < 500ms | 500-1500ms | > 1500ms |
| Warm Start | < 300ms | 300-800ms | > 800ms |
| Hot Start | < 100ms | 100-300ms | > 300ms |

### Best Practices

**Cold Start:**
- [ ] Defer non-critical initialization
- [ ] Use App Startup library
- [ ] Implement splash screen with theme
- [ ] Optimize Application.onCreate()
- [ ] Lazy load libraries
- [ ] Use Baseline Profiles

**Warm Start:**
- [ ] Minimize state to save/restore
- [ ] Use ViewModel for data retention
- [ ] Optimize view inflation
- [ ] Consider Jetpack Compose

**Hot Start:**
- [ ] Minimize onResume() work
- [ ] Use lifecycle-aware components
- [ ] Implement smart refresh logic
- [ ] Cache data appropriately

**General:**
- [ ] Profile with Android Studio Profiler
- [ ] Use `reportFullyDrawn()` for accurate metrics
- [ ] Monitor with Firebase Performance
- [ ] Test on low-end devices
- [ ] Implement splash screen API (Android 12+)

---

## Ответ (RU)

Время запуска приложения напрямую влияет на пользовательский опыт. Android категоризирует запуски на три типа.

#### 1. **Cold Start (Холодный запуск)**

Приложение запускается с нуля. Система создаёт процесс приложения.

**Этапы:**
1. Система загружает и запускает приложение
2. Создаёт процесс приложения
3. Создаёт объект Application
4. Запускает главный поток
5. Создаёт главную Activity
6. Inflates views
7. Выполняет layout
8. Отрисовывает первый кадр

**Оптимизация:**
- Отложенная инициализация
- App Startup library
- Splash screen через тему
- Lazy loading библиотек
- Baseline Profiles

#### 2. **Warm Start (Тёплый запуск)**

Процесс в памяти, но Activity пересоздаётся.

**Сценарии:**
- Пользователь вышел из приложения и вернулся
- Система уничтожила Activity из-за нехватки памяти
- Изменение конфигурации

**Оптимизация:**
- ViewModel для сохранения данных
- Минимальное состояние в savedInstanceState
- Оптимизация view inflation
- Jetpack Compose

#### 3. **Hot Start (Горячий запуск)**

Приложение в памяти, Activity на переднем плане или недавно в фоне.

**Сценарии:**
- Пользователь нажал Home и вернулся
- Переключение между приложениями
- Возврат из другой Activity

**Оптимизация:**
- Минимальная работа в onResume()
- Lifecycle-aware компоненты
- Умная логика обновления
- Кэширование данных

### Целевые показатели:

| Тип | Цель | Приемлемо | Медленно |
|-----|------|-----------|----------|
| Cold | < 500ms | 500-1500ms | > 1500ms |
| Warm | < 300ms | 300-800ms | > 800ms |
| Hot | < 100ms | 100-300ms | > 300ms |

### Измерение:

```bash
# Холодный запуск
adb shell am force-stop com.example.app
adb shell am start -W com.example.app/.MainActivity
```

Используйте `reportFullyDrawn()` для точных метрик.
