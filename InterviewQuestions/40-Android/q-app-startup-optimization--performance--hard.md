---
id: android-748
title: App Startup Optimization / Оптимизация Запуска Приложения
aliases: [App Startup Library, Cold Warm Hot Start, Оптимизация Запуска]
topic: android
subtopics: [performance, startup, initialization]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-baseline-profiles--performance--hard, q-lazy-initialization--performance--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/performance, android/startup, difficulty/hard, app-startup, initialization]
---
# Вопрос (RU)

> Что такое App Startup library? Объясните разницу между cold, warm и hot start. Как оптимизировать время запуска?

# Question (EN)

> What is the App Startup library? Explain the difference between cold, warm, and hot start. How do you optimize startup time?

---

## Ответ (RU)

**App Startup** -- это Jetpack библиотека для эффективной инициализации компонентов при запуске приложения. Она заменяет множественные ContentProvider-ы единой точкой инициализации.

### Краткий Ответ

- **Cold Start** -- процесс не существует, полная инициализация (~500-2000ms)
- **Warm Start** -- Activity пересоздаётся, Application жив (~200-500ms)
- **Hot Start** -- Activity выводится на передний план (~50-150ms)
- **App Startup** позволяет контролировать порядок и время инициализации библиотек

### Подробный Ответ

### Типы Запуска

```
Cold Start                    Warm Start                  Hot Start
    |                             |                           |
    v                             v                           v
[Процесс создаётся]         [Процесс жив]              [Процесс жив]
    |                             |                           |
    v                             v                           v
[Application.onCreate()]    [Activity создаётся]        [Activity выводится
    |                             |                    на передний план]
    v                             |                           |
[Activity создаётся]              v                           v
    |                        [onStart/onResume]          [onResume]
    v
[Первый кадр]

~500-2000ms                  ~200-500ms                  ~50-150ms
```

### Проблема: ContentProvider Hell

Многие библиотеки используют ContentProvider для автоинициализации:

```xml
<!-- Каждая библиотека добавляет свой ContentProvider -->
<provider android:name="androidx.work.impl.WorkManagerInitializer" />
<provider android:name="com.google.firebase.provider.FirebaseInitProvider" />
<provider android:name="com.facebook.internal.FacebookInitProvider" />
<!-- ... ещё 10+ провайдеров -->
```

**Проблема**: Каждый ContentProvider создаётся ДО `Application.onCreate()`, блокируя запуск.

### App Startup: Решение

```kotlin
// 1. Создаём Initializer для каждого компонента
class WorkManagerInitializer : Initializer<WorkManager> {

    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder()
            .setMinimumLoggingLevel(Log.INFO)
            .build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    // Зависимости -- инициализируются первыми
    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

class AnalyticsInitializer : Initializer<Analytics> {

    override fun create(context: Context): Analytics {
        return Analytics.init(context)
    }

    // Зависит от WorkManager
    override fun dependencies(): List<Class<out Initializer<*>>> {
        return listOf(WorkManagerInitializer::class.java)
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">

    <!-- Только корневые initializer-ы -->
    <meta-data
        android:name="com.example.AnalyticsInitializer"
        android:value="androidx.startup" />
</provider>
```

### Отложенная Инициализация

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Отключаем автоматическую инициализацию
        // (добавить tools:node="remove" в манифесте)

        // Инициализируем вручную когда нужно
        lifecycleScope.launch {
            // После первого кадра
            delay(100)
            AppInitializer.getInstance(this@MyApplication)
                .initializeComponent(HeavyLibraryInitializer::class.java)
        }
    }
}
```

### Трассировка Startup

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        // Трассировка для Android Profiler
        Trace.beginSection("MyApp.onCreate")
        super.onCreate()

        Trace.beginSection("DI.init")
        initDependencyInjection()
        Trace.endSection()

        Trace.beginSection("Analytics.init")
        initAnalytics()
        Trace.endSection()

        Trace.endSection() // MyApp.onCreate
    }
}
```

### Оптимизация Cold Start

```kotlin
class OptimizedApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // 1. Критические компоненты -- синхронно
        initCrashReporting() // ~10ms
        initStrictMode()     // ~5ms

        // 2. Важные, но не блокирующие -- фоновый поток
        Executors.newSingleThreadExecutor().execute {
            initAnalytics()      // ~100ms
            initImageLoader()    // ~50ms
            prefetchData()       // ~200ms
        }

        // 3. Отложенные -- после первого кадра
        // Используем App Startup с ручной инициализацией
    }
}
```

### Splash Screen API (Android 12+)

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        // Splash должен быть ДО super.onCreate()
        val splashScreen = installSplashScreen()

        // Держим splash пока данные не готовы
        var isReady = false
        splashScreen.setKeepOnScreenCondition { !isReady }

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Асинхронная загрузка
        lifecycleScope.launch {
            viewModel.loadInitialData()
            isReady = true
        }

        // Анимация выхода
        splashScreen.setOnExitAnimationListener { splashScreenView ->
            ObjectAnimator.ofFloat(splashScreenView, View.ALPHA, 1f, 0f).apply {
                duration = 300L
                doOnEnd { splashScreenView.remove() }
                start()
            }
        }
    }
}
```

### Измерение Времени Запуска

```kotlin
class StartupMetrics {

    companion object {
        private var processStartTime: Long = 0
        private var applicationCreateTime: Long = 0
        private var activityCreateTime: Long = 0
        private var firstFrameTime: Long = 0

        fun recordProcessStart() {
            processStartTime = Process.getStartElapsedRealtime()
        }

        fun recordApplicationCreate() {
            applicationCreateTime = SystemClock.elapsedRealtime()
        }

        fun recordFirstFrame() {
            firstFrameTime = SystemClock.elapsedRealtime()

            val coldStartTime = firstFrameTime - processStartTime
            val appInitTime = applicationCreateTime - processStartTime
            val activityTime = firstFrameTime - applicationCreateTime

            Log.d("Startup", """
                Cold start: ${coldStartTime}ms
                App init: ${appInitTime}ms
                Activity: ${activityTime}ms
            """.trimIndent())
        }
    }
}
```

### Чеклист Оптимизации

| Проблема | Решение |
|----------|---------|
| Много ContentProvider | App Startup library |
| Тяжёлая DI инициализация | Lazy injection, фоновый поток |
| Синхронная сеть/БД | Отложить до после первого кадра |
| Большой dex файл | Multidex, R8 оптимизация |
| Тяжёлый layout | ViewStub, lazy inflation |
| Reflection при старте | Избегать или кэшировать |

---

## Answer (EN)

**App Startup** is a Jetpack library for efficient component initialization during app launch. It replaces multiple ContentProviders with a single initialization entry point.

### Short Answer

- **Cold Start** -- process doesn't exist, full initialization (~500-2000ms)
- **Warm Start** -- Activity recreated, Application alive (~200-500ms)
- **Hot Start** -- Activity brought to foreground (~50-150ms)
- **App Startup** allows controlling order and timing of library initialization

### Detailed Answer

### Startup Types

```
Cold Start                    Warm Start                  Hot Start
    |                             |                           |
    v                             v                           v
[Process created]           [Process alive]            [Process alive]
    |                             |                           |
    v                             v                           v
[Application.onCreate()]    [Activity created]          [Activity brought
    |                             |                    to foreground]
    v                             |                           |
[Activity created]                v                           v
    |                        [onStart/onResume]          [onResume]
    v
[First frame]

~500-2000ms                  ~200-500ms                  ~50-150ms
```

### Problem: ContentProvider Hell

Many libraries use ContentProvider for auto-initialization:

```xml
<!-- Each library adds its ContentProvider -->
<provider android:name="androidx.work.impl.WorkManagerInitializer" />
<provider android:name="com.google.firebase.provider.FirebaseInitProvider" />
<provider android:name="com.facebook.internal.FacebookInitProvider" />
<!-- ... 10+ more providers -->
```

**Problem**: Each ContentProvider is created BEFORE `Application.onCreate()`, blocking startup.

### App Startup: Solution

```kotlin
// 1. Create Initializer for each component
class WorkManagerInitializer : Initializer<WorkManager> {

    override fun create(context: Context): WorkManager {
        val config = Configuration.Builder()
            .setMinimumLoggingLevel(Log.INFO)
            .build()
        WorkManager.initialize(context, config)
        return WorkManager.getInstance(context)
    }

    // Dependencies -- initialized first
    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

class AnalyticsInitializer : Initializer<Analytics> {

    override fun create(context: Context): Analytics {
        return Analytics.init(context)
    }

    // Depends on WorkManager
    override fun dependencies(): List<Class<out Initializer<*>>> {
        return listOf(WorkManagerInitializer::class.java)
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">

    <!-- Only root initializers -->
    <meta-data
        android:name="com.example.AnalyticsInitializer"
        android:value="androidx.startup" />
</provider>
```

### Deferred Initialization

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Disable automatic initialization
        // (add tools:node="remove" in manifest)

        // Initialize manually when needed
        lifecycleScope.launch {
            // After first frame
            delay(100)
            AppInitializer.getInstance(this@MyApplication)
                .initializeComponent(HeavyLibraryInitializer::class.java)
        }
    }
}
```

### Startup Tracing

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        // Tracing for Android Profiler
        Trace.beginSection("MyApp.onCreate")
        super.onCreate()

        Trace.beginSection("DI.init")
        initDependencyInjection()
        Trace.endSection()

        Trace.beginSection("Analytics.init")
        initAnalytics()
        Trace.endSection()

        Trace.endSection() // MyApp.onCreate
    }
}
```

### Cold Start Optimization

```kotlin
class OptimizedApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // 1. Critical components -- synchronous
        initCrashReporting() // ~10ms
        initStrictMode()     // ~5ms

        // 2. Important but non-blocking -- background thread
        Executors.newSingleThreadExecutor().execute {
            initAnalytics()      // ~100ms
            initImageLoader()    // ~50ms
            prefetchData()       // ~200ms
        }

        // 3. Deferred -- after first frame
        // Use App Startup with manual initialization
    }
}
```

### Splash Screen API (Android 12+)

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        // Splash must be BEFORE super.onCreate()
        val splashScreen = installSplashScreen()

        // Keep splash until data is ready
        var isReady = false
        splashScreen.setKeepOnScreenCondition { !isReady }

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Async loading
        lifecycleScope.launch {
            viewModel.loadInitialData()
            isReady = true
        }

        // Exit animation
        splashScreen.setOnExitAnimationListener { splashScreenView ->
            ObjectAnimator.ofFloat(splashScreenView, View.ALPHA, 1f, 0f).apply {
                duration = 300L
                doOnEnd { splashScreenView.remove() }
                start()
            }
        }
    }
}
```

### Measuring Startup Time

```kotlin
class StartupMetrics {

    companion object {
        private var processStartTime: Long = 0
        private var applicationCreateTime: Long = 0
        private var activityCreateTime: Long = 0
        private var firstFrameTime: Long = 0

        fun recordProcessStart() {
            processStartTime = Process.getStartElapsedRealtime()
        }

        fun recordApplicationCreate() {
            applicationCreateTime = SystemClock.elapsedRealtime()
        }

        fun recordFirstFrame() {
            firstFrameTime = SystemClock.elapsedRealtime()

            val coldStartTime = firstFrameTime - processStartTime
            val appInitTime = applicationCreateTime - processStartTime
            val activityTime = firstFrameTime - applicationCreateTime

            Log.d("Startup", """
                Cold start: ${coldStartTime}ms
                App init: ${appInitTime}ms
                Activity: ${activityTime}ms
            """.trimIndent())
        }
    }
}
```

### Optimization Checklist

| Problem | Solution |
|---------|----------|
| Many ContentProviders | App Startup library |
| Heavy DI initialization | Lazy injection, background thread |
| Synchronous network/DB | Defer until after first frame |
| Large dex file | Multidex, R8 optimization |
| Heavy layout | ViewStub, lazy inflation |
| Reflection at startup | Avoid or cache |

---

## Ссылки (RU)

- [App Startup](https://developer.android.com/topic/libraries/app-startup)
- [App Startup Time](https://developer.android.com/topic/performance/vitals/launch-time)
- [Splash Screen API](https://developer.android.com/develop/ui/views/launch/splash-screen)

## References (EN)

- [App Startup](https://developer.android.com/topic/libraries/app-startup)
- [App Startup Time](https://developer.android.com/topic/performance/vitals/launch-time)
- [Splash Screen API](https://developer.android.com/develop/ui/views/launch/splash-screen)

## Follow-ups (EN)

- How does App Startup handle circular dependencies?
- What is the difference between TTID and TTFD?
- How to profile startup with Android Studio Profiler?
- How does Baseline Profiles affect startup time?

## Дополнительные Вопросы (RU)

- Как App Startup обрабатывает циклические зависимости?
- В чём разница между TTID и TTFD?
- Как профилировать запуск с помощью Android Studio Profiler?
- Как Baseline Profiles влияют на время запуска?
