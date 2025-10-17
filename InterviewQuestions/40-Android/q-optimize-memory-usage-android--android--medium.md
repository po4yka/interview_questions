---
id: 20251012-12271158
title: "Optimize Memory Usage Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: [android/memory-management, android/performance, glide, lrucache, memory-management, memory-optimization, optimization, performance, weakreference, difficulty/medium]
moc: moc-android
related: []
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

## Ответ (RU)

**1. Минимизируйте статические переменные**

```kotlin
// ❌ ПЛОХО - Статическая ссылка вызывает утечки
companion object {
    var context: Context? = null
    val userList = mutableListOf<User>()  // Никогда не освобождается
}

// ✅ ХОРОШО - Используйте application context или избегайте статики
companion object {
    lateinit var appContext: Context  // Application context - OK
}
```

**2. Избегайте утечек памяти**

Правильно управляйте ссылками на контексты и активности.

```kotlin
// ❌ ПЛОХО - Утечка Activity
class MyTask(private val activity: Activity) : AsyncTask<>() {
    // Удерживает ссылку на Activity
}

// ✅ ХОРОШО - Используйте WeakReference
class MyTask(activity: Activity) : AsyncTask<>() {
    private val activityRef = WeakReference(activity)

    override fun doInBackground() {
        activityRef.get()?.let { activity ->
            // Безопасный доступ
        }
    }
}
```

**3. Используйте LruCache для кеширования**

```kotlin
// Кеш для битмапов с ограничением по памяти
val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
val cacheSize = maxMemory / 8

val memoryCache = object : LruCache<String, Bitmap>(cacheSize) {
    override fun sizeOf(key: String, bitmap: Bitmap): Int {
        return bitmap.byteCount / 1024
    }
}
```

**4. Оптимизируйте работу с Bitmap**

```kotlin
// ✅ Загружайте только необходимый размер
val options = BitmapFactory.Options().apply {
    inJustDecodeBounds = true
    inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
    inJustDecodeBounds = false
}
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image, options)
```

**5. Освобождайте ресурсы**

```kotlin
override fun onTrimMemory(level: Int) {
    super.onTrimMemory(level)
    when (level) {
        ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN -> {
            // UI скрыт - освободите кеши UI
            imageCache.evictAll()
        }
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL -> {
            // Критически мало памяти - освободите все возможное
            clearCaches()
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
