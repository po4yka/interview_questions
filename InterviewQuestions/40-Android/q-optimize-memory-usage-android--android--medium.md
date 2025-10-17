---
id: "20251015082237301"
title: "Optimize Memory Usage Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: - android
  - android/memory-management
  - android/performance
  - glide
  - lrucache
  - memory-management
  - memory-optimization
  - optimization
  - performance
  - weakreference
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# Question (EN)

> How to optimize memory usage in an Android application?

# Вопрос (RU)

> Как оптимизировать использование памяти в Android-приложении?

---

## Answer (EN)

**1. Minimize Static Variables**

```kotlin
// - BAD - Static reference leaks
companion object {
    var context: Context? = null
    val userList = mutableListOf<User>()  // Never released
}

// - GOOD - Use application context or avoid statics
companion object {
    lateinit var appContext: Context  // Application context OK
}
```

**2. Avoid Memory Leaks**

Properly manage references to contexts and activities.

```kotlin
// - BAD - Activity leak
class MyTask(private val activity: Activity) : AsyncTask<>() {
    // Holds Activity reference
}

// - GOOD - Use WeakReference
class MyTask(activity: Activity) : AsyncTask<>() {
    private val activityRef = WeakReference(activity)

    override fun doInBackground() {
        activityRef.get()?.let { activity ->
            // Safe access
        }
    }
}
```

---

## Follow-ups

-   How do you diagnose memory leaks and high allocations using Android Studio Profiler and LeakCanary?
-   When should you use LruCache vs DiskLruCache vs in-memory maps?
-   How do Bitmap reuse and inBitmap/inPreferredConfig impact memory?

## References

-   `https://developer.android.com/topic/performance/memory` — Memory management
-   `https://square.github.io/leakcanary/` — LeakCanary
-   `https://developer.android.com/topic/performance/graphics/manage-memory` — Bitmaps memory

## Related Questions
