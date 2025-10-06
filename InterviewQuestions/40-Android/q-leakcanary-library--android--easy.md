---
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

✅ **Automatic detection** of Activity/Fragment leaks
✅ **Zero configuration** - works out of the box
✅ **Visual leak traces** with retention chains
✅ **Heap dump analysis** with Shark library
✅ **Debug builds only** - no production overhead

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
    var activity: Activity? = null  // ❌ Leak!
}
```

**2. Handler without removeCallbacks:**
```kotlin
handler.postDelayed({ /* ... */ }, 60000)  // ❌ Leak if Activity destroyed
```

**3. Anonymous Inner Class:**
```kotlin
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View?) {
        // Holds Activity reference ❌
    }
})
```

**4. Singleton with Context:**
```kotlin
object MyManager {
    private var context: Context? = null  // ❌ Leak if Activity context

    fun init(context: Context) {
        this.context = context  // Should use applicationContext
    }
}
```

**Best Practices:**

```kotlin
// ✅ GOOD - Use LeakCanary in debug builds only
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
    // No release implementation!
}

// ✅ GOOD - Fix leaks shown by LeakCanary
// Don't just disable LeakCanary to hide leaks!

// ✅ GOOD - Watch custom objects
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

