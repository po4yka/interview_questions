---
id: "20251015082237292"
title: "Leakcanary Library / Библиотека LeakCanary"
topic: android
difficulty: easy
status: draft
created: 2025-10-13
tags: - android
  - android/memory-management
  - debugging-tools
  - leakcanary
  - memory-leaks
  - memory-management
  - square
  - tools
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# Question (EN)

> What library is used for finding memory leaks in Android?

# Вопрос (RU)

> Какая библиотека используется для нахождения утечек памяти в Android?

---

## Answer (EN)

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

-   **Automatic detection** of Activity/Fragment leaks
-   **Zero configuration** - works out of the box
-   **Visual leak traces** with retention chains
-   **Heap dump analysis** with Shark library
-   **Debug builds only** - no production overhead

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

   LeakCanary

  MainActivity has leaked

  1 retained object
  Retaining 2.5 MB

  Tap to see leak trace

```

**Leak Trace Example:**

```

 REFERENCES UNDERLINED are the leak
 cause


 GC Root: System class
     ↓ static MyApplication.sInstance
 MyApplication instance
     ↓ MyApplication.activityManager
 ActivityManager instance
     ↓ ActivityManager.currentActivity

 MainActivity instance

   Leaking: YES (Activity#mDestroyed=true)
   Retaining 2.5 MB in 1234 objects

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

| Library                              | Purpose               | Pros               | Cons           |
| ------------------------------------ | --------------------- | ------------------ | -------------- |
| **LeakCanary**                       | Memory leak detection | Auto, visual, easy | Debug only     |
| **Memory Profiler** (Android Studio) | Manual analysis       | Powerful, detailed | Manual work    |
| **MAT (Eclipse)**                    | Heap dump analysis    | Professional tool  | Complex        |
| **Perfetto**                         | System tracing        | Complete picture   | Learning curve |

**Common Leaks Detected:**

**1. Static Activity Reference:**

```kotlin
companion object {
    var activity: Activity? = null  // - Leak!
}
```

---

## Follow-ups

-   How do you interpret LeakCanary leak traces and fix common leak patterns?
-   What’s the difference between retained object count and actual memory usage?
-   How can you integrate LeakCanary with CI or turn it off in release builds?

## References

-   `https://square.github.io/leakcanary/` — LeakCanary docs
-   `https://github.com/square/leakcanary` — LeakCanary GitHub
-   `https://developer.android.com/topic/performance/memory` — Memory management

## Related Questions
