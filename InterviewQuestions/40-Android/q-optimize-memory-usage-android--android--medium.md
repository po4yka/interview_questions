---
id: android-077
title: "Memory Optimization in Android / Оптимизация памяти в Android"
aliases: ["Memory Optimization in Android", "Оптимизация памяти в Android"]
topic: android
subtopics: [performance-memory, profiling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-01-27
tags: [android/performance-memory, android/profiling, performance, profiling, difficulty/medium]
moc: moc-android
related: [q-list-to-detail-navigation--android--medium, q-how-to-fix-a-bad-element-layout--android--easy, c-memory-management]
sources: []
date created: Monday, October 27th 2025, 4:02:09 pm
date modified: Thursday, October 30th 2025, 3:15:34 pm
---

# Вопрос (RU)

> Как оптимизировать использование памяти в Android-приложении?

# Question (EN)

> How to optimize memory usage in an Android application?

## Ответ (RU)

**1. Избегайте утечек памяти**

Правильно управляйте ссылками на контексты и активности через WeakReference для асинхронных операций.

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

**2. Используйте LruCache для кеширования**

```kotlin
// ✅ Кеш для битмапов с ограничением по памяти (12.5% heap)
val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
val cacheSize = maxMemory / 8

val memoryCache = object : LruCache<String, Bitmap>(cacheSize) {
    override fun sizeOf(key: String, bitmap: Bitmap): Int {
        return bitmap.byteCount / 1024
    }
}
```

**3. Оптимизируйте работу с Bitmap**

```kotlin
// ✅ Загружайте только необходимый размер через inSampleSize
val options = BitmapFactory.Options().apply {
    inJustDecodeBounds = true
    inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
    inJustDecodeBounds = false
}
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image, options)
```

**4. Освобождайте ресурсы при низкой памяти**

```kotlin
override fun onTrimMemory(level: Int) {
    super.onTrimMemory(level)
    when (level) {
        ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN -> {
            // ✅ UI скрыт - освободите кеши UI
            imageCache.evictAll()
        }
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL -> {
            // ✅ Критически мало памяти - освободите все возможное
            clearCaches()
        }
    }
}
```

---

## Answer (EN)

**1. Avoid Memory Leaks**

Properly manage references to contexts and activities using WeakReference for async operations.

```kotlin
// ❌ BAD - Activity leak
class MyTask(private val activity: Activity) : AsyncTask<>() {
    // Holds Activity reference
}

// ✅ GOOD - Use WeakReference
class MyTask(activity: Activity) : AsyncTask<>() {
    private val activityRef = WeakReference(activity)

    override fun doInBackground() {
        activityRef.get()?.let { activity ->
            // Safe access
        }
    }
}
```

**2. Use LruCache for Caching**

```kotlin
// ✅ Bitmap cache with memory limit (12.5% of heap)
val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
val cacheSize = maxMemory / 8

val memoryCache = object : LruCache<String, Bitmap>(cacheSize) {
    override fun sizeOf(key: String, bitmap: Bitmap): Int {
        return bitmap.byteCount / 1024
    }
}
```

**3. Optimize Bitmap Loading**

```kotlin
// ✅ Load only necessary size via inSampleSize
val options = BitmapFactory.Options().apply {
    inJustDecodeBounds = true
    inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
    inJustDecodeBounds = false
}
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large_image, options)
```

**4. Release Resources on Low Memory**

```kotlin
override fun onTrimMemory(level: Int) {
    super.onTrimMemory(level)
    when (level) {
        ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN -> {
            // ✅ UI hidden - clear UI caches
            imageCache.evictAll()
        }
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL -> {
            // ✅ Critically low memory - clear everything possible
            clearCaches()
        }
    }
}
```

---

## Follow-ups

- How do you diagnose memory leaks using Android Studio Profiler heap dumps and allocation tracking?
- When should you use LruCache vs DiskLruCache for different data types?
- How does Bitmap.Config (ARGB_8888 vs RGB_565) impact memory usage and quality trade-offs?

## References

- [[c-memory-management]]
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/topic/performance/graphics/manage-memory

## Related Questions

### Prerequisites
- [[q-how-to-fix-a-bad-element-layout--android--easy]]

### Related
- [[q-list-to-detail-navigation--android--medium]]

### Advanced
- Consider memory profiling and heap dump analysis techniques
