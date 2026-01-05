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
updated: 2025-11-10
tags: [android/performance-memory, android/profiling, difficulty/medium, performance, profiling]
moc: moc-android
related: [c-memory-management, q-how-to-fix-a-bad-element-layout--android--easy, q-list-to-detail-navigation--android--medium]
sources: []
---
# Вопрос (RU)

> Как оптимизировать использование памяти в Android-приложении?

# Question (EN)

> How to optimize memory usage in an Android application?

## Ответ (RU)

**1. Избегайте утечек памяти**

- Не храните долгоживущие ссылки на `Activity`, `Fragment` или `View` в синглтонах, статических полях, длительных задачах.
- Для асинхронных операций привязывайтесь к жизненному циклу (`lifecycleScope`, `viewLifecycleOwner.lifecycleScope`), а не к "висящей" ссылке на `Activity`.
- Используйте `applicationContext`, когда не нужен UI-контекст.
- `WeakReference` можно использовать точечно, но это не универсальное решение.

```kotlin
// ❌ ПЛОХО — утечка Activity через статическое поле
object SomeManager {
    var activity: Activity? = null
}

// ✅ ХОРОШО — не удерживаем ссылку на Activity дольше, чем нужно
class SomeManager(private val context: Context) {
    private val appContext = context.applicationContext
}
```

**2. Используйте LruCache для кеширования**

```kotlin
// ✅ Кеш для битмапов с ограничением по памяти (12.5% heap)
val maxMemoryKb = (Runtime.getRuntime().maxMemory() / 1024).toInt()
val cacheSizeKb = maxMemoryKb / 8

val memoryCache = object : LruCache<String, Bitmap>(cacheSizeKb) {
    override fun sizeOf(key: String, bitmap: Bitmap): Int {
        return bitmap.byteCount / 1024
    }
}
```

**3. Оптимизируйте работу с Bitmap**

- Загружайте изображения нужного размера, а не в полном разрешении.
- При необходимости используйте более экономичные форматы (`Bitmap.Config.RGB_565` вместо `ARGB_8888`).

```kotlin
fun decodeSampledBitmapFromResource(
    res: Resources,
    resId: Int,
    reqWidth: Int,
    reqHeight: Int
): Bitmap {
    // Сначала только считаем размеры
    val options = BitmapFactory.Options().apply {
        inJustDecodeBounds = true
    }
    BitmapFactory.decodeResource(res, resId, options)

    // Вычисляем inSampleSize на основе outWidth/outHeight
    options.inSampleSize = calculateInSampleSize(options, reqWidth, reqHeight)

    // Декодируем с учетом inSampleSize
    options.inJustDecodeBounds = false
    return BitmapFactory.decodeResource(res, resId, options)
}
```

**4. Освобождайте ресурсы при низкой памяти**

Реагируйте на сигналы системы (`onTrimMemory`, `onLowMemory`) для очистки кешей и тяжелых объектов.

```kotlin
override fun onTrimMemory(level: Int) {
    super.onTrimMemory(level)
    when (level) {
        ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN -> {
            // ✅ UI скрыт — освободите кеши, связанные с UI
            imageCache.evictAll()
        }
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW,
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL,
        ComponentCallbacks2.TRIM_MEMORY_BACKGROUND -> {
            // ✅ Мало памяти — сократите использование по максимуму
            clearCaches()
        }
    }
}
```

**5. Общие практики снижения потребления памяти**

- Избегайте лишних аллокаций в горячих участках кода (скролл списков, анимации).
- Используйте ленивую инициализацию (lazy loading) для тяжелых объектов.
- Повторно используйте объекты там, где это безопасно (адаптеры списков, view holderы).
- Следите за размерами коллекций и очищайте неиспользуемые ссылки.

---

## Answer (EN)

**1. Avoid Memory Leaks**

- Do not keep long-lived references to `Activity`, `Fragment`, or `View` in singletons, static fields, or long-running tasks.
- Prefer lifecycle-aware scopes (`lifecycleScope`, `viewLifecycleOwner.lifecycleScope`) instead of holding onto an `Activity` reference manually.
- Use `applicationContext` when a UI context is not required.
- `WeakReference` can be used in specific cases, but it is not a universal fix.

```kotlin
// ❌ BAD — Activity leak via static reference
object SomeManager {
    var activity: Activity? = null
}

// ✅ GOOD — do not retain Activity longer than necessary
class SomeManager(context: Context) {
    private val appContext = context.applicationContext
}
```

**2. Use LruCache for Caching**

```kotlin
// ✅ Bitmap cache with memory limit (12.5% of heap)
val maxMemoryKb = (Runtime.getRuntime().maxMemory() / 1024).toInt()
val cacheSizeKb = maxMemoryKb / 8

val memoryCache = object : LruCache<String, Bitmap>(cacheSizeKb) {
    override fun sizeOf(key: String, bitmap: Bitmap): Int {
        return bitmap.byteCount / 1024
    }
}
```

**3. Optimize Bitmap Loading**

- Load images at the required resolution instead of full-size.
- When acceptable, use more memory-efficient configs (e.g., `Bitmap.Config.RGB_565`).

```kotlin
fun decodeSampledBitmapFromResource(
    res: Resources,
    resId: Int,
    reqWidth: Int,
    reqHeight: Int
): Bitmap {
    // First, decode bounds only
    val options = BitmapFactory.Options().apply {
        inJustDecodeBounds = true
    }
    BitmapFactory.decodeResource(res, resId, options)

    // Compute inSampleSize using outWidth/outHeight
    options.inSampleSize = calculateInSampleSize(options, reqWidth, reqHeight)

    // Decode with inSampleSize applied
    options.inJustDecodeBounds = false
    return BitmapFactory.decodeResource(res, resId, options)
}
```

**4. Release Resources on Low Memory**

React to system callbacks (`onTrimMemory`, `onLowMemory`) to clear caches and heavy objects.

```kotlin
override fun onTrimMemory(level: Int) {
    super.onTrimMemory(level)
    when (level) {
        ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN -> {
            // ✅ UI hidden — clear UI-related caches
            imageCache.evictAll()
        }
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW,
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL,
        ComponentCallbacks2.TRIM_MEMORY_BACKGROUND -> {
            // ✅ Low memory — aggressively reduce usage
            clearCaches()
        }
    }
}
```

**5. General Practices to Reduce Memory Usage**

- Avoid unnecessary allocations in hot paths (e.g., list scrolling, animations).
- Use lazy initialization for heavy objects.
- Reuse objects where safe (e.g., view holders in adapters).
- Monitor collection sizes and clear references when no longer needed.

---

## Дополнительные Вопросы (RU)

- Как диагностировать утечки памяти с помощью Android Studio Profiler, heap dump-ов и отслеживания аллокаций?
- Когда следует использовать `LruCache` по сравнению с `DiskLruCache` для разных типов данных?
- Как `Bitmap.Config` (`ARGB_8888` vs `RGB_565`) влияет на использование памяти и качество изображения?

## Follow-ups

- How do you diagnose memory leaks using Android Studio Profiler heap dumps and allocation tracking?
- When should you use `LruCache` vs `DiskLruCache` for different data types?
- How does `Bitmap.Config` (`ARGB_8888` vs `RGB_565`) impact memory usage and quality trade-offs?

## Ссылки (RU)

- [[c-memory-management]]
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/topic/performance/graphics/manage-memory

## References

- [[c-memory-management]]
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/topic/performance/graphics/manage-memory

## Связанные Вопросы (RU)

### Предпосылки
- [[q-how-to-fix-a-bad-element-layout--android--easy]]

### Похожие
- [[q-list-to-detail-navigation--android--medium]]

### Продвинутое
- Рассмотрите техники профилирования памяти и анализа heap dump-ов.

## Related Questions

### Prerequisites
- [[q-how-to-fix-a-bad-element-layout--android--easy]]

### Related
- [[q-list-to-detail-navigation--android--medium]]

### Advanced
- Consider memory profiling and heap dump analysis techniques
