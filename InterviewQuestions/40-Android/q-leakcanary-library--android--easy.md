---
topic: android
tags:
  - android
  - android/memory-management
  - debugging-tools
  - leakcanary
  - memory-leaks
  - memory-management
  - square
  - tools
difficulty: easy
status: reviewed
---

# Какая библиотека используется для нахождения утечек памяти в Android?

**English**: What library is used for finding memory leaks in Android?

## Answer

The popular library for detecting memory leaks in Android is **LeakCanary** by Square.

**Setup:**

```kotlin
// build.gradle (app)
dependencies {
    // Debug builds only
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}
```

**Features:**

- **Automatic detection** of Activity/Fragment leaks
- **Zero configuration** - works out of the box
- **Visual leak traces** with retention chains
- **Heap dump analysis** with Shark library
- **Debug builds only** - no production overhead

**How It Works:**

```kotlin
// Automatically watches Activity lifecycle
Application.registerActivityLifecycleCallbacks(object : ActivityLifecycleCallbacks {
    override fun onActivityDestroyed(activity: Activity) {
        // LeakCanary watches for leaks
        AppWatcher.objectWatcher.watch(
            activity,
            "${activity::class.java.name} received Activity#onDestroy() callback"
        )
    }
    // ... other callbacks
})
```

**Leak Notification:**

When a leak is detected, LeakCanary shows a notification:

```
┌──────────────────────────────────┐
│  🐛 LeakCanary                    │
├──────────────────────────────────┤
│  MainActivity has leaked          │
│                                   │
│  1 retained object                │
│  Retaining 2.5 MB                 │
│                                   │
│  Tap to see leak trace            │
└──────────────────────────────────┘
```

**Leak Trace Example:**

```
┌─────────────────────────────────────────┐
│ REFERENCES UNDERLINED are the leak      │
│ cause                                    │
├─────────────────────────────────────────┤
│                                          │
│ GC Root: System class                    │
│     ↓ static MyApplication.sInstance     │
│ MyApplication instance                   │
│     ↓ MyApplication.activityManager      │
│ ActivityManager instance                 │
│     ↓ ActivityManager.currentActivity    │
│ ════════════════════════════════════════ │
│ MainActivity instance                    │
│ ════════════════════════════════════════ │
│   Leaking: YES (Activity#mDestroyed=true)│
│   Retaining 2.5 MB in 1234 objects       │
└─────────────────────────────────────────┘
```

**Watch Custom Objects:**

```kotlin
class MyViewModel : ViewModel() {
    init {
        // Watch ViewModel for leaks
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyViewModel cleared"
        )
    }
}
```

**Configuration:**

```kotlin
// Application class
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        // Custom configuration (optional)
        val config = AppWatcher.config.copy(
            watchActivities = true,
            watchFragments = true,
            watchViewModels = true,
            watchDurationMillis = 5000  // Wait 5s before checking
        )
        AppWatcher.config = config
    }
}
```

**Alternatives:**

| Library | Purpose | Pros | Cons |
|---------|---------|------|------|
| **LeakCanary** | Memory leak detection | Auto, visual, easy | Debug only |
| **Memory Profiler** (Android Studio) | Manual analysis | Powerful, detailed | Manual work |
| **MAT (Eclipse)** | Heap dump analysis | Professional tool | Complex |
| **Perfetto** | System tracing | Complete picture | Learning curve |

**Common Leaks Detected:**

**1. Static Activity Reference:**
```kotlin
companion object {
    var activity: Activity? = null  // - Leak!
}
```

**2. Handler without removeCallbacks:**
```kotlin
handler.postDelayed({ /* ... */ }, 60000)  // - Leak if Activity destroyed
```

**3. Anonymous Inner Class:**
```kotlin
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View?) {
        // Holds Activity reference BAD
    }
})
```

**4. Singleton with Context:**
```kotlin
object MyManager {
    private var context: Context? = null  // - Leak if Activity context

    fun init(context: Context) {
        this.context = context  // Should use applicationContext
    }
}
```

**Best Practices:**

```kotlin
// - GOOD - Use LeakCanary in debug builds only
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
    // No release implementation!
}

// - GOOD - Fix leaks shown by LeakCanary
// Don't just disable LeakCanary to hide leaks!

// - GOOD - Watch custom objects
class MyRepository {
    init {
        if (BuildConfig.DEBUG) {
            AppWatcher.objectWatcher.watch(this)
        }
    }
}
```

**Summary:**

- **LeakCanary** by Square - industry-standard leak detection
- **Zero configuration** - automatic Activity/Fragment watching
- **Visual leak traces** - shows retention chain
- **Debug builds only** - no production overhead
- **Easy to use** - just add dependency and run

## Ответ

Популярная библиотека для выявления утечек памяти в Android — **LeakCanary** от Square.

**Установка:**

```kotlin
// build.gradle (app)
dependencies {
    // Только для debug сборок
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}
```

**Возможности:**

- Автоматическое обнаружение утечек Activity/Fragment
- Нулевая конфигурация - работает из коробки
- Визуальные трассировки утечек с цепочками удержания
- Анализ heap dump с библиотекой Shark
- Только для debug сборок - нет overhead в production

**Как работает:**

LeakCanary автоматически отслеживает жизненный цикл Activity и Fragment. Когда компонент уничтожается, библиотека проверяет, освобождена ли память через 5 секунд. Если объект всё ещё в памяти - это утечка.

**Уведомление об утечке:**

При обнаружении утечки LeakCanary показывает уведомление с информацией:
- Какой объект утёк
- Сколько объектов удерживается
- Сколько памяти занято
- Полная трассировка утечки

**Наблюдение за пользовательскими объектами:**

```kotlin
class MyViewModel : ViewModel() {
    init {
        // Отслеживание ViewModel на утечки
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyViewModel cleared"
        )
    }
}
```

**Конфигурация:**

```kotlin
// Application класс
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        // Кастомная конфигурация (опционально)
        val config = AppWatcher.config.copy(
            watchActivities = true,
            watchFragments = true,
            watchViewModels = true,
            watchDurationMillis = 5000  // Ждать 5с перед проверкой
        )
        AppWatcher.config = config
    }
}
```

**Типичные утечки, которые обнаруживает:**

**1. Статическая ссылка на Activity:**
```kotlin
companion object {
    var activity: Activity? = null  // Утечка!
}
```

**2. Handler без removeCallbacks:**
```kotlin
handler.postDelayed({ /* ... */ }, 60000)  // Утечка если Activity уничтожен
```

**3. Анонимный внутренний класс:**
```kotlin
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View?) {
        // Держит ссылку на Activity - утечка
    }
})
```

**4. Singleton с Context:**
```kotlin
object MyManager {
    private var context: Context? = null  // Утечка если Activity context

    fun init(context: Context) {
        this.context = context  // Нужно использовать applicationContext
    }
}
```

**Лучшие практики:**

```kotlin
// Правильно: Используйте LeakCanary только в debug сборках
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
    // Нет release implementation!
}

// Правильно: Исправляйте утечки, показанные LeakCanary
// Не отключайте LeakCanary чтобы скрыть утечки!

// Правильно: Отслеживайте пользовательские объекты
class MyRepository {
    init {
        if (BuildConfig.DEBUG) {
            AppWatcher.objectWatcher.watch(this)
        }
    }
}
```

**Альтернативы:**

| Инструмент | Назначение | Плюсы | Минусы |
|------------|-----------|-------|--------|
| **LeakCanary** | Обнаружение утечек | Авто, визуальный, простой | Только debug |
| **Memory Profiler** (Android Studio) | Ручной анализ | Мощный, детальный | Ручная работа |
| **MAT (Eclipse)** | Анализ heap dump | Профессиональный | Сложный |
| **Perfetto** | Трассировка системы | Полная картина | Кривая обучения |

**Резюме:**

- **LeakCanary** от Square - индустриальный стандарт для обнаружения утечек
- **Нулевая конфигурация** - автоматическое отслеживание Activity/Fragment
- **Визуальные трассировки** - показывает цепочку удержания
- **Только debug сборки** - нет overhead в production
- **Простота использования** - просто добавьте зависимость и запустите

