---
id: android-352
title: How To Catch The Earliest Entry Point Into The Application / Как поймать самую раннюю точку входа в приложение
aliases: [How To Catch The Earliest Entry Point Into The Application, Как поймать самую раннюю точку входа в приложение]
topic: android
subtopics: [lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-lifecycle, q-hilt-entry-points--android--medium, q-how-application-priority-is-determined-by-the-system--android--hard, q-jetpack-compose-lazy-column--android--easy, q-retrofit-modify-all-requests--android--hard, q-which-class-to-catch-gestures--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [android/lifecycle, difficulty/medium]

---
# Вопрос (RU)
> Как поймать самую раннюю точку входа в приложение

# Question (EN)
> How To Catch The Earliest Entry Point Into The `Application`

---

## Ответ (RU)
Самый ранний код вашего приложения может выполниться ещё до `Application.onCreate()`:

- В `onCreate()` собственного `ContentProvider` (включая `InitializationProvider`, который использует Jetpack App Startup).
- Затем в `Application.attachBaseContext()`.
- Затем в `Application.onCreate()` — это стандартная, явная точка входа для глобальной инициализации.

Ниже — практические варианты.

### `Application`.onCreate() — Стандартная Точка Входа

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Вызывается до любых Activity/Service/BroadcastReceiver в данном процессе
        // Здесь обычно настраивают логирование, crash reporting, DI и т.п.
        initializeTimber()
        initializeCrashlytics()
        initializeLeakCanary()

        Log.d("App", "Application onCreate called")
    }

    private fun initializeTimber() {
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
    }
}
```

Манифест:
```xml
<application
    android:name=".MyApplication"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name">
    <!-- Activities и другие компоненты -->
</application>
```

### Порядок Выполнения (упрощённо, В Одном процессе)

```text
1. Создание процесса
   ↓
2. ContentProvider.onCreate()          ← Самый ранний код (для каждого провайдера)
   ↓
3. Application.attachBaseContext()
   ↓
4. Application.onCreate()              ← Основная точка входа приложения
   ↓
5. Activity.onCreate() / Service.onCreate() / BroadcastReceiver.onReceive()
```

Важно: `ContentProvider` вашего приложения или библиотек создаётся до `Application.onCreate()` в этом процессе. Jetpack App Startup использует тот же механизм.

### `ContentProvider` — Раньше, Чем `Application`.onCreate()

```kotlin
class InitializationProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // Этот код выполнится ДО MyApplication.onCreate() в данном процессе
        val ctx = context ?: return false

        // Здесь можно разместить небольшую критичную инициализацию (очень аккуратно)
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }

        Log.d("Init", "ContentProvider onCreate - earliest entry point")
        return true
    }

    // Заглушки — сами по себе для инициализации не используются
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? = null

    override fun insert(uri: Uri, values: ContentValues?): Uri? = null

    override fun update(
        uri: Uri,
        values: ContentValues?,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int = 0

    override fun delete(
        uri: Uri,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int = 0

    override fun getType(uri: Uri): String? = null
}
```

Манифест:
```xml
<application>
    <provider
        android:name=".InitializationProvider"
        android:authorities="${applicationId}.initialization"
        android:exported="false" />
</application>
```

Особенности:
- `onCreate()` провайдера выполняется на main-потоке при старте — не делайте там тяжёлую работу.
- Инициализация происходит для каждого процесса, где загружается провайдер.

### `Application`.attachBaseContext() — Ранняя Настройка Контекста

Метод вызывается до `onCreate()` и подходит для MultiDex и обёрток контекста. При этом `ContentProvider` уже могли быть инициализированы.

```kotlin
class MyApplication : Application() {
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(base)

        // Вызывается до onCreate()
        // Типичный кейс — MultiDex или обёртка контекста
        MultiDex.install(this)

        // Пример: изменение конфигурации/локали (использовать осторожно, зависит от API)
    }

    override fun onCreate() {
        super.onCreate()
        // Основная инициализация
    }
}
```

### App Startup (Jetpack) — Рекомендованный Способ (на Базе `ContentProvider`)

Jetpack App Startup регистрирует `InitializationProvider` (`ContentProvider`), который вызывается до `Application.onCreate()` и последовательно запускает ваши `Initializer`-ы.

```kotlin
class TimberInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        Timber.plant(Timber.DebugTree())
        Log.d("Startup", "Timber initialized")
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val configuration = Configuration.Builder()
            .setMinimumLoggingLevel(Log.DEBUG)
            .build()
        WorkManager.initialize(context, configuration)
        return WorkManager.getInstance(context)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> =
        listOf(TimberInitializer::class.java)
}
```

Манифест (обычно генерируется через manifest merger, здесь для наглядности):
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false">
    <meta-data
        android:name="com.example.TimberInitializer"
        android:value="androidx.startup" />
    <meta-data
        android:name="com.example.WorkManagerInitializer"
        android:value="androidx.startup" />
</provider>
```

### ActivityLifecycleCallbacks — Отслеживание foreground/background

Не самая ранняя точка входа, но полезно для мониторинга состояния приложения.

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        registerActivityLifecycleCallbacks(object : ActivityLifecycleCallbacks {
            private var activityReferences = 0
            private var isActivityChangingConfigurations = false

            override fun onActivityCreated(activity: Activity, bundle: Bundle?) {
                Log.d("Lifecycle", "Activity created: ${activity.localClassName}")
            }

            override fun onActivityStarted(activity: Activity) {
                if (++activityReferences == 1 && !isActivityChangingConfigurations) {
                    Log.d("Lifecycle", "App entered foreground")
                }
            }

            override fun onActivityStopped(activity: Activity) {
                isActivityChangingConfigurations = activity.isChangingConfigurations
                if (--activityReferences == 0 && !isActivityChangingConfigurations) {
                    Log.d("Lifecycle", "App entered background")
                }
            }

            override fun onActivityResumed(activity: Activity) {}
            override fun onActivityPaused(activity: Activity) {}
            override fun onActivitySaveInstanceState(activity: Activity, bundle: Bundle) {}
            override fun onActivityDestroyed(activity: Activity) {}
        })
    }
}
```

### ProcessLifecycleOwner — Более Высокий Уровень

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        ProcessLifecycleOwner.get().lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onStart(owner: LifecycleOwner) {
                Log.d("Lifecycle", "App foreground")
            }

            override fun onStop(owner: LifecycleOwner) {
                Log.d("Lifecycle", "App background")
            }
        })
    }
}
```

### Типичные Инициализации В `Application`.onCreate()

```kotlin
class MyApplication : Application() {
    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onCreate() {
        super.onCreate()

        // Логирование
        initTimber()

        // Crash reporting
        FirebaseCrashlytics.getInstance()

        // DI
        startKoin {
            androidContext(this@MyApplication)
            modules(appModule)
        }

        // Загрузка картинок
        Coil.setImageLoader {
            ImageLoader.Builder(this)
                .crossfade(true)
                .build()
        }

        // Мониторинг сети
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            val connectivityManager =
                getSystemService(ConnectivityManager::class.java)
            connectivityManager.registerDefaultNetworkCallback(networkCallback)
        }

        // StrictMode (только debug)
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
        }

        // Некритичная асинхронная инициализация
        appScope.launch {
            initAnalytics()
            preloadData()
        }
    }
}
```

### Лучшие Практики

1. В `ContentProvider`/App Startup — только минимальный критичный синхронный код.
2. `Application.onCreate()` — основная точка глобальной инициализации, держите её максимально лёгкой.
3. Используйте ленивую/отложенную инициализацию.
4. Некритичные операции переносите в фон, используя структурированные корутины или другие async-инструменты (избегайте `GlobalScope`).
5. Измеряйте время старта (`adb shell am start -W`, профилировщик, Startup Tracing).

---

## Answer (EN)
The absolute earliest application-specific code in an Android app usually runs in one of the following (all before any `Activity`):

- A custom `ContentProvider`'s `onCreate()` defined in your app or libraries (including Jetpack App Startup's internal `InitializationProvider`).
- Then `Application.attachBaseContext()`.
- Then `Application.onCreate()` as the standard, explicit entry point.

Below is the practical order and options.

### `Application`.onCreate() - Standard Entry Point

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // This is called before any Activity/Service/BroadcastReceiver in this process
        // Initialize libraries, logging, crash reporting
        initializeTimber()
        initializeCrashlytics()
        initializeLeakCanary()

        Log.d("App", "Application onCreate called")
    }

    private fun initializeTimber() {
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
    }
}
```

Register in AndroidManifest.xml:
```xml
<application
    android:name=".MyApplication"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name">
    <!-- Activities and other components -->
</application>
```

### Execution Order (simplified, Same process)

```text
1. Process creation
   ↓
2. ContentProvider.onCreate()          ← Earliest app code (for each provider)
   ↓
3. Application.attachBaseContext()
   ↓
4. Application.onCreate()              ← Standard app-wide entry point
   ↓
5. Activity.onCreate() / Service.onCreate() / BroadcastReceiver.onReceive()
```

Note: A `ContentProvider` belonging to your app or libraries is created before `Application.onCreate()` in that process. Jetpack App Startup uses this mechanism under the hood.

### `ContentProvider` - Earlier Than `Application`.onCreate()

```kotlin
class InitializationProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // This runs BEFORE MyApplication.onCreate() in this process
        val ctx = context ?: return false

        // Initialize critical libraries here (keep it fast!)
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }

        Log.d("Init", "ContentProvider onCreate - earliest entry point")
        return true
    }

    // Stub implementations (not used for initialization)
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? = null

    override fun insert(uri: Uri, values: ContentValues?): Uri? = null

    override fun update(
        uri: Uri,
        values: ContentValues?,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int = 0

    override fun delete(
        uri: Uri,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int = 0

    override fun getType(uri: Uri): String? = null
}
```

Register in AndroidManifest.xml:
```xml
<application>
    <provider
        android:name=".InitializationProvider"
        android:authorities="${applicationId}.initialization"
        android:exported="false" />
</application>
```

Important:
- Provider `onCreate()` runs on the main thread during startup; do not do heavy work here.
- It runs per-process where the provider is loaded.

### `Application`.attachBaseContext() - Early Configuration

Called before `onCreate()` in the same process. Useful for attaching a wrapped context or enabling MultiDex. It is still invoked after any `ContentProvider` initializations for that process.

```kotlin
class MyApplication : Application() {
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(base)

        // Called before onCreate()
        // Commonly used for MultiDex or context wrapping
        MultiDex.install(this)

        // Example: locale/other configuration adjustments (implementation depends on API level)
        // Use with care; configuration overrides at the Application level can have side effects.
    }

    override fun onCreate() {
        super.onCreate()
        // Regular initialization
    }
}
```

### App Startup Library (Recommended, Uses `ContentProvider` internally)

Jetpack App Startup defines an `InitializationProvider` (a `ContentProvider`) that runs before `Application.onCreate()` and calls your `Initializer`s in a defined order.

```kotlin
class TimberInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        Timber.plant(Timber.DebugTree())
        Log.d("Startup", "Timber initialized")
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val configuration = Configuration.Builder()
            .setMinimumLoggingLevel(Log.DEBUG)
            .build()
        WorkManager.initialize(context, configuration)
        return WorkManager.getInstance(context)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> =
        listOf(TimberInitializer::class.java) // Ensure Timber is ready first
}
```

Register in AndroidManifest.xml (usually auto via manifest merger, shown explicitly for clarity):
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false">
    <meta-data
        android:name="com.example.TimberInitializer"
        android:value="androidx.startup" />
    <meta-data
        android:name="com.example.WorkManagerInitializer"
        android:value="androidx-startup" />
</provider>
```

### Lifecycle Callbacks - Monitor App Foreground/Background

Not the earliest entry point, but useful for tracking app visibility once initialized.

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        registerActivityLifecycleCallbacks(object : ActivityLifecycleCallbacks {
            private var activityReferences = 0
            private var isActivityChangingConfigurations = false

            override fun onActivityCreated(activity: Activity, bundle: Bundle?) {
                Log.d("Lifecycle", "Activity created: ${activity.localClassName}")
            }

            override fun onActivityStarted(activity: Activity) {
                if (++activityReferences == 1 && !isActivityChangingConfigurations) {
                    // App entered foreground
                    Log.d("Lifecycle", "App entered foreground")
                }
            }

            override fun onActivityStopped(activity: Activity) {
                isActivityChangingConfigurations = activity.isChangingConfigurations
                if (--activityReferences == 0 && !isActivityChangingConfigurations) {
                    // App entered background
                    Log.d("Lifecycle", "App entered background")
                }
            }

            override fun onActivityResumed(activity: Activity) {}
            override fun onActivityPaused(activity: Activity) {}
            override fun onActivitySaveInstanceState(activity: Activity, bundle: Bundle) {}
            override fun onActivityDestroyed(activity: Activity) {}
        })
    }
}
```

### ProcessLifecycleOwner - Higher-level App Lifecycle

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        ProcessLifecycleOwner.get().lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onStart(owner: LifecycleOwner) {
                // App moved to foreground
                Log.d("Lifecycle", "App foreground")
            }

            override fun onStop(owner: LifecycleOwner) {
                // App moved to background
                Log.d("Lifecycle", "App background")
            }
        })
    }
}
```

### Common Initializations in `Application`.onCreate()

```kotlin
class MyApplication : Application() {
    // Prefer an application-scoped CoroutineScope instead of GlobalScope
    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onCreate() {
        super.onCreate()

        // Logging
        initTimber()

        // Crash reporting
        FirebaseCrashlytics.getInstance()

        // Dependency injection
        startKoin {
            androidContext(this@MyApplication)
            modules(appModule)
        }

        // Image loading
        Coil.setImageLoader {
            ImageLoader.Builder(this)
                .crossfade(true)
                .build()
        }

        // Network monitoring
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            val connectivityManager =
                getSystemService(ConnectivityManager::class.java)
            connectivityManager.registerDefaultNetworkCallback(networkCallback)
        }

        // Strict mode (debug only)
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
        }

        // Example of non-critical async init
        appScope.launch {
            initAnalytics()
            preloadData()
        }
    }
}
```

### Best Practices

1. `ContentProvider` / App Startup initializers: only very small, critical synchronous work.
2. `Application.onCreate()`: treat as the main app-level initialization point; keep it fast.
3. Use lazy/deferred initialization where possible.
4. Move non-critical work off the main thread using a structured, app-scoped coroutine or other async API (avoid `GlobalScope`).
5. Measure startup performance (e.g., `adb shell am start -W`, Android Studio profiler, Startup Tracing).

---

## Related Topics
- `Application` lifecycle
- `ContentProvider` initialization
- App Startup library
- ProcessLifecycleOwner
- Dependency injection initialization

---

## Follow-ups

- [[q-jetpack-compose-lazy-column--android--easy]]
- [[q-retrofit-modify-all-requests--android--hard]]
- How does using a `ContentProvider` for early initialization affect cold start performance and ANR risk?
- When should you prefer Jetpack App Startup over manual initialization in `Application.onCreate()`?
- How would you structure initialization code to support multi-process apps safely?

## References

- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites / Concepts

- [[c-lifecycle]]

### Prerequisites (Easier)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Fundamentals

### Related (Medium)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-anr-application-not-responding--android--medium]] - Fundamentals
- [[q-intent-filters-android--android--medium]] - Fundamentals
- [[q-what-are-intents-for--android--medium]] - Fundamentals

### Advanced (Harder)
- [[q-how-application-priority-is-determined-by-the-system--android--hard]] - Fundamentals
- [[q-kotlin-context-receivers--android--hard]] - Fundamentals
