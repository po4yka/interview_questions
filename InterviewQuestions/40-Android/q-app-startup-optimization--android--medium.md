---
id: 20251011-220003
title: App Startup Optimization / Оптимизация запуска приложения
aliases:
- App Startup Optimization
- Оптимизация запуска приложения
topic: android
subtopics:
- performance
- app-startup
- optimization
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-app-startup-library--android--medium
- q-app-start-types-android--android--medium
- q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/performance
- android/app-startup
- android/optimization
- performance
- app-startup
- optimization
- difficulty/medium
---# Вопрос (RU)
> Как оптимизировать производительность запуска Android приложения?

---

# Question (EN)
> How do you optimize Android app startup performance?

## Ответ (RU)

**Оптимизация запуска** сокращает время холодного/тёплого/горячего старта через консолидацию ContentProvider, ленивую инициализацию, отложенное выполнение и оптимизацию на основе измерений.

**Теория оптимизации:**
Время запуска напрямую влияет на удержание пользователей. Каждый ContentProvider добавляет 20-50мс, синхронный I/O блокирует главный поток, энергичная инициализация тратит ресурсы. Цель: холодный < 500мс, тёплый < 300мс, горячий < 100мс.

**1. Консолидация ContentProvider**

**Теория**: Каждый ContentProvider запускает отдельные IPC вызовы во время старта приложения, добавляя 20-50мс накладных расходов. Множественные провайдеры создают последовательные узкие места инициализации. App Startup консолидирует всю инициализацию в один провайдер с разрешением зависимостей, уменьшая IPC накладные расходы и позволяя параллельную инициализацию независимых компонентов.

```kotlin
// Раньше: Множественные ContentProvider
class AnalyticsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Analytics.initialize(context!!) // 50мс
        return true
    }
}

class CrashProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Crashlytics.initialize(context!!) // 40мс
        return true
    }
}
// Результат: 4 провайдера × 30мс = штраф 120мс на старт
```

```kotlin
// После: Единый App Startup провайдер
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.initialize(context)
    }
    override fun dependencies() = emptyList()
}

class CrashInitializer : Initializer<Crashlytics> {
    override fun create(context: Context): Crashlytics {
        return Crashlytics.initialize(context)
    }
    override fun dependencies() = listOf(AnalyticsInitializer::class.java)
}
// Результат: 1 провайдер = 25мс всего
```

**2. Ленивая инициализация**

**Теория**: Энергичная инициализация тратит время старта на функции, которые пользователь может никогда не использовать. Ленивая инициализация откладывает создание объектов до первого обращения, сокращая время холодного старта. Использует делегат `by lazy` Kotlin, который создает объекты по требованию с потокобезопасной инициализацией. Критично для опциональных функций как push уведомления, аналитика или премиум функции.

```kotlin
class MyApplication : Application() {
    // Ленивая инициализация - только при обращении
    val pushNotifications by lazy {
        PushNotificationService().apply { initialize(this@MyApplication) }
    }

    val analytics by lazy {
        AnalyticsService().apply { initialize(this@MyApplication) }
    }

    override fun onCreate() {
        super.onCreate()
        // Только критическая инициализация
        initCrashReporting()
    }
}

// Использование: Инициализировать только при необходимости
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        findViewById<Button>(R.id.enable_push).setOnClickListener {
            (application as MyApplication).pushNotifications.subscribe()
        }
    }
}
```

**3. Отложенное выполнение**

**Теория**: Некритическая инициализация может быть перенесена с критического пути старта с помощью WorkManager. Это позволяет приложению показать UI немедленно, пока фоновые задачи выполняются асинхронно. WorkManager гарантирует выполнение задач даже если приложение убито, с настраиваемыми ограничениями (батарея, сеть). Необходимо для прогрева кэша, синхронизации удаленной конфигурации и задач очистки.

```kotlin
class DeferredInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        val work = OneTimeWorkRequestBuilder<BackgroundInitWorker>()
            .setInitialDelay(5, TimeUnit.SECONDS)
            .build()

        WorkManager.getInstance(context).enqueueUniqueWork(
            "background_init",
            ExistingWorkPolicy.KEEP,
            work
        )
    }

    override fun dependencies() = emptyList()
}

class BackgroundInitWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        // Некритическая инициализация
        warmUpImageCache()
        syncRemoteConfig()
        cleanupOldFiles()
        Result.success()
    }
}
```

**4. Измерение производительности**

**Теория**: Оптимизация без измерений приводит к преждевременной оптимизации. Пользовательские секции трассировки создают временные маркеры в Perfetto для выявления узких мест. Метрики старта отслеживают реальную производительность на разных устройствах и сетевых условиях. Firebase Performance Monitoring предоставляет продакшн инсайты с автоматической корреляцией крашей и метриками по устройствам.

```kotlin
// Пользовательские секции трассировки для Perfetto
class MyApplication : Application() {
    override fun onCreate() {
        Trace.beginSection("Application.onCreate")
        super.onCreate()

        Trace.beginSection("InitEssentialServices")
        initCrashReporting()
        Trace.endSection()

        Trace.endSection()
    }
}

// Отслеживание метрик запуска
class StartupMetrics {
    companion object {
        private var appStartTime = 0L

        fun recordAppStart() {
            appStartTime = SystemClock.elapsedRealtime()
        }

        fun recordFirstFrame() {
            val duration = SystemClock.elapsedRealtime() - appStartTime
            Firebase.analytics.logEvent("startup_time") {
                param("duration_ms", duration)
            }
        }
    }
}
```

**5. Результаты оптимизации**

- **Раньше**: 1250мс холодный старт, 8 ContentProvider, энергичная инициализация
- **После**: 520мс холодный старт (-58%), 1 ContentProvider, ленивая + отложенная
- **Улучшения**: App Startup (-175мс), ленивая инициализация (-260мс), отложенные задачи (-150мс)

**6. Лучшие практики**

- Сначала измеряйте с Perfetto/systrace
- Консолидируйте ContentProvider с App Startup
- Инициализируйте только критические сервисы в Application.onCreate()
- Используйте ленивую инициализацию для опциональных функций
- Откладывайте некритичную работу с WorkManager
- Избегайте синхронного I/O в главном потоке
- Держите первый экран простым и быстрым
- Тестируйте на слабых устройствах

---

## Answer (EN)

**Startup Optimization** reduces cold/warm/hot start times through ContentProvider consolidation, lazy initialization, deferred execution, and measurement-driven optimization.

**Optimization Theory:**
Startup time directly impacts user retention. Each ContentProvider adds 20-50ms, synchronous I/O blocks main thread, eager initialization wastes resources. Target: cold < 500ms, warm < 300ms, hot < 100ms.

**1. ContentProvider Consolidation**

**Theory**: Each ContentProvider triggers separate IPC calls during app startup, adding 20-50ms overhead. Multiple providers create sequential initialization bottlenecks. App Startup consolidates all initialization into a single provider with dependency resolution, reducing IPC overhead and enabling parallel initialization of independent components.

```kotlin
// Before: Multiple ContentProviders
class AnalyticsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Analytics.initialize(context!!) // 50ms
        return true
    }
}

class CrashProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        Crashlytics.initialize(context!!) // 40ms
        return true
    }
}
// Result: 4 providers × 30ms = 120ms startup penalty
```

```kotlin
// After: Single App Startup provider
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.initialize(context)
    }
    override fun dependencies() = emptyList()
}

class CrashInitializer : Initializer<Crashlytics> {
    override fun create(context: Context): Crashlytics {
        return Crashlytics.initialize(context)
    }
    override fun dependencies() = listOf(AnalyticsInitializer::class.java)
}
// Result: 1 provider = 25ms total
```

**2. Lazy Initialization**

**Theory**: Eager initialization wastes startup time on features users may never use. Lazy initialization defers object creation until first access, reducing cold start time. Uses Kotlin's `by lazy` delegate which creates objects on-demand with thread-safe initialization. Critical for optional features like push notifications, analytics, or premium features.

```kotlin
class MyApplication : Application() {
    // Lazy initialization - only when accessed
    val pushNotifications by lazy {
        PushNotificationService().apply { initialize(this@MyApplication) }
    }

    val analytics by lazy {
        AnalyticsService().apply { initialize(this@MyApplication) }
    }

    override fun onCreate() {
        super.onCreate()
        // Only critical initialization
        initCrashReporting()
    }
}

// Usage: Initialize only when needed
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        findViewById<Button>(R.id.enable_push).setOnClickListener {
            (application as MyApplication).pushNotifications.subscribe()
        }
    }
}
```

**3. Deferred Execution**

**Theory**: Non-critical initialization can be moved off the critical startup path using WorkManager. This allows the app to show UI immediately while background tasks complete asynchronously. WorkManager ensures tasks run even if the app is killed, with configurable constraints (battery, network). Essential for cache warming, remote config sync, and cleanup tasks.

```kotlin
class DeferredInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        val work = OneTimeWorkRequestBuilder<BackgroundInitWorker>()
            .setInitialDelay(5, TimeUnit.SECONDS)
            .build()

        WorkManager.getInstance(context).enqueueUniqueWork(
            "background_init",
            ExistingWorkPolicy.KEEP,
            work
        )
    }

    override fun dependencies() = emptyList()
}

class BackgroundInitWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        // Non-critical initialization
        warmUpImageCache()
        syncRemoteConfig()
        cleanupOldFiles()
        Result.success()
    }
}
```

**4. Performance Measurement**

**Theory**: Optimization without measurement leads to premature optimization. Custom trace sections create timeline markers in Perfetto for identifying bottlenecks. Startup metrics track real-world performance across devices and network conditions. Firebase Performance Monitoring provides production insights with automatic crash correlation and device-specific metrics.

```kotlin
// Custom trace sections for Perfetto
class MyApplication : Application() {
    override fun onCreate() {
        Trace.beginSection("Application.onCreate")
        super.onCreate()

        Trace.beginSection("InitEssentialServices")
        initCrashReporting()
        Trace.endSection()

        Trace.endSection()
    }
}

// Startup metrics tracking
class StartupMetrics {
    companion object {
        private var appStartTime = 0L

        fun recordAppStart() {
            appStartTime = SystemClock.elapsedRealtime()
        }

        fun recordFirstFrame() {
            val duration = SystemClock.elapsedRealtime() - appStartTime
            Firebase.analytics.logEvent("startup_time") {
                param("duration_ms", duration)
            }
        }
    }
}
```

**5. Optimization Results**

- **Before**: 1250ms cold start, 8 ContentProviders, eager initialization
- **After**: 520ms cold start (-58%), 1 ContentProvider, lazy + deferred
- **Improvements**: App Startup (-175ms), lazy init (-260ms), deferred tasks (-150ms)

**6. Best Practices**

- Measure first with Perfetto/systrace
- Consolidate ContentProviders with App Startup
- Initialize only critical services in Application.onCreate()
- Use lazy initialization for optional features
- Defer non-critical work with WorkManager
- Avoid synchronous I/O on main thread
- Keep first screen simple and fast
- Test on low-end devices

## Follow-ups

- How do you measure startup performance in production?
- What's the difference between lazy and eager initialization?
- When should you use WorkManager for deferred tasks?
- How do you handle initialization failures?

## References

- [App Startup Library](https://developer.android.com/topic/libraries/app-startup)
- [App Startup Performance](https://developer.android.com/topic/performance/vitals/launch-time)
- [Perfetto Tracing](https://perfetto.dev/)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-app-startup-library--android--medium]]
- [[q-app-start-types-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]

