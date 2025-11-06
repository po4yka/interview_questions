---
id: android-034
title: How do image loading libraries like Glide work internally? / Как работают библиотеки
  загрузки изображений вроде Glide?
aliases:
- How do image loading libraries like Glide work internally?
- Как работают библиотеки загрузки изображений вроде Glide?
topic: android
subtopics:
- cache-offline
- files-media
- performance-memory
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- android/caching
- android/glide
- android/image-loading
- android/memory-management
- difficulty/medium
- en
- ru
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository
status: draft
moc: moc-android
related:
- c-memory-management
- c-database-design
- c-scoped-storage-security
- bitmap-handling
- caching
- glide
- memory-optimization
created: 2025-10-06
updated: 2025-10-31
tags:
- android/cache-offline
- android/files-media
- android/performance-memory
- difficulty/medium
- en
- ru
---

# Question (EN)
> How do image loading libraries like Glide/Fresco work internally?
# Вопрос (RU)
> Как работают библиотеки загрузки изображений вроде Glide/Fresco внутри?

---

## Answer (EN)

Image loading libraries like Glide, Fresco, and Coil solve complex problems related to loading, caching, and displaying images efficiently in Android applications.

### 1. Core Components of Glide

```kotlin
// High-level overview of Glide architecture

           Glide Request Manager
  (Lifecycle-aware request management)



         Request Coordinator & Engine
    (Job scheduling, deduplication)





 Memory        Disk      Network
 Cache         Cache     Fetcher
 (LruCache)    (DiskLRU  (OkHttp)

```

### 2. Loading Pipeline

```kotlin
// Simplified Glide loading process

class GlideRequestFlow {
    fun loadImage(url: String, target: ImageView) {
        // 1. Check memory cache (fastest)
        val cachedBitmap = memoryCache.get(url)
        if (cachedBitmap != null) {
            target.setImageBitmap(cachedBitmap)
            return
        }

        // 2. Check active resources (currently displayed images)
        val activeResource = activeResources.get(url)
        if (activeResource != null) {
            target.setImageBitmap(activeResource)
            return
        }

        // 3. Check disk cache
        diskCacheExecutor.execute {
            val diskCached = diskCache.get(url)
            if (diskCached != null) {
                val bitmap = BitmapFactory.decodeStream(diskCached)
                memoryCache.put(url, bitmap)
                mainHandler.post {
                    target.setImageBitmap(bitmap)
                }
                return@execute
            }

            // 4. Network fetch
            networkExecutor.execute {
                val stream = httpClient.fetch(url)
                val bitmap = BitmapFactory.decodeStream(stream)

                // Save to disk cache
                diskCache.put(url, bitmap)

                // Save to memory cache
                memoryCache.put(url, bitmap)

                mainHandler.post {
                    target.setImageBitmap(bitmap)
                }
            }
        }
    }
}
```

### 3. Memory Cache Implementation

```kotlin
class MemoryCache(maxSize: Int) {
    private val cache = LruCache<String, Bitmap>(maxSize)

    init {
        // Calculate cache size (typically 1/8 of available memory)
        val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
        val cacheSize = maxMemory / 8
    }

    fun get(key: String): Bitmap? {
        return cache.get(key)
    }

    fun put(key: String, bitmap: Bitmap) {
        if (get(key) == null) {
            cache.put(key, bitmap)
        }
    }

    override fun sizeOf(key: String, bitmap: Bitmap): Int {
        // Return size in kilobytes
        return bitmap.byteCount / 1024
    }
}
```

### 4. Request `Lifecycle` Management

```kotlin
class RequestManager(private val lifecycle: Lifecycle) {
    private val requests = mutableSetOf<ImageRequest>()

    init {
        lifecycle.addObserver(object : LifecycleEventObserver {
            override fun onStateChanged(source: LifecycleOwner, event: Lifecycle.Event) {
                when (event) {
                    Lifecycle.Event.ON_START -> resumeRequests()
                    Lifecycle.Event.ON_STOP -> pauseRequests()
                    Lifecycle.Event.ON_DESTROY -> clearRequests()
                    else -> {}
                }
            }
        })
    }

    fun load(url: String): RequestBuilder {
        val request = RequestBuilder(url, this)
        requests.add(request)
        return request
    }

    private fun pauseRequests() {
        requests.forEach { it.pause() }
    }

    private fun resumeRequests() {
        requests.forEach { it.resume() }
    }

    private fun clearRequests() {
        requests.forEach { it.cancel() }
        requests.clear()
    }
}
```

### 5. Image Transformation

```kotlin
class TransformationEngine {
    fun applyTransformations(
        bitmap: Bitmap,
        transformations: List<Transformation>
    ): Bitmap {
        var result = bitmap
        for (transformation in transformations) {
            result = transformation.transform(result)
        }
        return result
    }
}

// Built-in transformations
class CenterCropTransformation : Transformation {
    override fun transform(source: Bitmap): Bitmap {
        val scale = max(
            targetWidth.toFloat() / source.width,
            targetHeight.toFloat() / source.height
        )

        val scaledWidth = (scale * source.width).toInt()
        val scaledHeight = (scale * source.height).toInt()

        val scaled = Bitmap.createScaledBitmap(source, scaledWidth, scaledHeight, true)

        val left = (scaled.width - targetWidth) / 2
        val top = (scaled.height - targetHeight) / 2

        return Bitmap.createBitmap(scaled, left, top, targetWidth, targetHeight)
    }
}
```

### 6. Request Deduplication

```kotlin
class EngineJob {
    private val activeJobs = ConcurrentHashMap<Key, Job>()

    fun load(key: Key, callback: ResourceCallback): Job? {
        // Check if same request is already running
        val existingJob = activeJobs[key]
        if (existingJob != null) {
            existingJob.addCallback(callback)
            return null // Deduplication - don't start new job
        }

        // Create new job
        val newJob = Job(key, callback)
        activeJobs[key] = newJob
        return newJob
    }

    fun onJobComplete(key: Key) {
        activeJobs.remove(key)
    }
}
```

### 7. `Bitmap` Pool for Reuse

```kotlin
class BitmapPool(maxSize: Int) {
    private val pool = LruCache<Int, MutableList<Bitmap>>(maxSize)

    fun get(width: Int, height: Int, config: Bitmap.Config): Bitmap? {
        val size = width * height * config.bytesPerPixel
        val bitmaps = pool.get(size) ?: return null

        return if (bitmaps.isNotEmpty()) {
            bitmaps.removeAt(bitmaps.size - 1)
        } else null
    }

    fun put(bitmap: Bitmap) {
        if (!bitmap.isMutable) return

        val size = bitmap.byteCount
        val bitmaps = pool.get(size) ?: mutableListOf()
        bitmaps.add(bitmap)
        pool.put(size, bitmaps)
    }
}
```

### 8. Disk Cache Strategy

```kotlin
sealed class DiskCacheStrategy {
    object None : DiskCacheStrategy()
    object All : DiskCacheStrategy() // Cache original + transformed
    object Automatic : DiskCacheStrategy() // Smart decision
    object Data : DiskCacheStrategy() // Cache only original
    object Resource : DiskCacheStrategy() // Cache only transformed
}

class DiskCacheManager {
    fun shouldCacheData(strategy: DiskCacheStrategy): Boolean {
        return when (strategy) {
            DiskCacheStrategy.All,
            DiskCacheStrategy.Data,
            DiskCacheStrategy.Automatic -> true
            else -> false
        }
    }

    fun shouldCacheResource(strategy: DiskCacheStrategy): Boolean {
        return when (strategy) {
            DiskCacheStrategy.All,
            DiskCacheStrategy.Resource -> true
            else -> false
        }
    }
}
```

### 9. Glide Key Differences from Others

| Library | Memory Cache | Disk Cache | `Lifecycle` | Transformations |
|---------|-------------|-----------|-----------|-----------------|
| **Glide** | LruCache | DiskLruCache | Automatic | Built-in + Custom |
| **Fresco** | Native memory | File system | Manual | Extensive |
| **Coil** | LruCache | OkHttp cache | Coroutines | Composable |
| **Picasso** | LruCache | OkHttp cache | Manual | Limited |

### 10. Complete Usage Example

```kotlin
// Modern Glide usage
Glide.with(context) // Lifecycle-aware
    .load(url)
    .placeholder(R.drawable.placeholder)
    .error(R.drawable.error)
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .transform(CenterCrop(), RoundedCorners(16))
    .transition(DrawableTransitionOptions.withCrossFade())
    .thumbnail(0.25f) // Load low-res first
    .into(imageView)
```

---


# Question (EN)
> How do image loading libraries like Glide/Fresco work internally?
# Вопрос (RU)
> Как работают библиотеки загрузки изображений вроде Glide/Fresco внутри?

---


---


## Answer (EN)

Image loading libraries like Glide, Fresco, and Coil solve complex problems related to loading, caching, and displaying images efficiently in Android applications.

### 1. Core Components of Glide

```kotlin
// High-level overview of Glide architecture

           Glide Request Manager
  (Lifecycle-aware request management)



         Request Coordinator & Engine
    (Job scheduling, deduplication)





 Memory        Disk      Network
 Cache         Cache     Fetcher
 (LruCache)    (DiskLRU  (OkHttp)

```

### 2. Loading Pipeline

```kotlin
// Simplified Glide loading process

class GlideRequestFlow {
    fun loadImage(url: String, target: ImageView) {
        // 1. Check memory cache (fastest)
        val cachedBitmap = memoryCache.get(url)
        if (cachedBitmap != null) {
            target.setImageBitmap(cachedBitmap)
            return
        }

        // 2. Check active resources (currently displayed images)
        val activeResource = activeResources.get(url)
        if (activeResource != null) {
            target.setImageBitmap(activeResource)
            return
        }

        // 3. Check disk cache
        diskCacheExecutor.execute {
            val diskCached = diskCache.get(url)
            if (diskCached != null) {
                val bitmap = BitmapFactory.decodeStream(diskCached)
                memoryCache.put(url, bitmap)
                mainHandler.post {
                    target.setImageBitmap(bitmap)
                }
                return@execute
            }

            // 4. Network fetch
            networkExecutor.execute {
                val stream = httpClient.fetch(url)
                val bitmap = BitmapFactory.decodeStream(stream)

                // Save to disk cache
                diskCache.put(url, bitmap)

                // Save to memory cache
                memoryCache.put(url, bitmap)

                mainHandler.post {
                    target.setImageBitmap(bitmap)
                }
            }
        }
    }
}
```

### 3. Memory Cache Implementation

```kotlin
class MemoryCache(maxSize: Int) {
    private val cache = LruCache<String, Bitmap>(maxSize)

    init {
        // Calculate cache size (typically 1/8 of available memory)
        val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
        val cacheSize = maxMemory / 8
    }

    fun get(key: String): Bitmap? {
        return cache.get(key)
    }

    fun put(key: String, bitmap: Bitmap) {
        if (get(key) == null) {
            cache.put(key, bitmap)
        }
    }

    override fun sizeOf(key: String, bitmap: Bitmap): Int {
        // Return size in kilobytes
        return bitmap.byteCount / 1024
    }
}
```

### 4. Request `Lifecycle` Management

```kotlin
class RequestManager(private val lifecycle: Lifecycle) {
    private val requests = mutableSetOf<ImageRequest>()

    init {
        lifecycle.addObserver(object : LifecycleEventObserver {
            override fun onStateChanged(source: LifecycleOwner, event: Lifecycle.Event) {
                when (event) {
                    Lifecycle.Event.ON_START -> resumeRequests()
                    Lifecycle.Event.ON_STOP -> pauseRequests()
                    Lifecycle.Event.ON_DESTROY -> clearRequests()
                    else -> {}
                }
            }
        })
    }

    fun load(url: String): RequestBuilder {
        val request = RequestBuilder(url, this)
        requests.add(request)
        return request
    }

    private fun pauseRequests() {
        requests.forEach { it.pause() }
    }

    private fun resumeRequests() {
        requests.forEach { it.resume() }
    }

    private fun clearRequests() {
        requests.forEach { it.cancel() }
        requests.clear()
    }
}
```

### 5. Image Transformation

```kotlin
class TransformationEngine {
    fun applyTransformations(
        bitmap: Bitmap,
        transformations: List<Transformation>
    ): Bitmap {
        var result = bitmap
        for (transformation in transformations) {
            result = transformation.transform(result)
        }
        return result
    }
}

// Built-in transformations
class CenterCropTransformation : Transformation {
    override fun transform(source: Bitmap): Bitmap {
        val scale = max(
            targetWidth.toFloat() / source.width,
            targetHeight.toFloat() / source.height
        )

        val scaledWidth = (scale * source.width).toInt()
        val scaledHeight = (scale * source.height).toInt()

        val scaled = Bitmap.createScaledBitmap(source, scaledWidth, scaledHeight, true)

        val left = (scaled.width - targetWidth) / 2
        val top = (scaled.height - targetHeight) / 2

        return Bitmap.createBitmap(scaled, left, top, targetWidth, targetHeight)
    }
}
```

### 6. Request Deduplication

```kotlin
class EngineJob {
    private val activeJobs = ConcurrentHashMap<Key, Job>()

    fun load(key: Key, callback: ResourceCallback): Job? {
        // Check if same request is already running
        val existingJob = activeJobs[key]
        if (existingJob != null) {
            existingJob.addCallback(callback)
            return null // Deduplication - don't start new job
        }

        // Create new job
        val newJob = Job(key, callback)
        activeJobs[key] = newJob
        return newJob
    }

    fun onJobComplete(key: Key) {
        activeJobs.remove(key)
    }
}
```

### 7. `Bitmap` Pool for Reuse

```kotlin
class BitmapPool(maxSize: Int) {
    private val pool = LruCache<Int, MutableList<Bitmap>>(maxSize)

    fun get(width: Int, height: Int, config: Bitmap.Config): Bitmap? {
        val size = width * height * config.bytesPerPixel
        val bitmaps = pool.get(size) ?: return null

        return if (bitmaps.isNotEmpty()) {
            bitmaps.removeAt(bitmaps.size - 1)
        } else null
    }

    fun put(bitmap: Bitmap) {
        if (!bitmap.isMutable) return

        val size = bitmap.byteCount
        val bitmaps = pool.get(size) ?: mutableListOf()
        bitmaps.add(bitmap)
        pool.put(size, bitmaps)
    }
}
```

### 8. Disk Cache Strategy

```kotlin
sealed class DiskCacheStrategy {
    object None : DiskCacheStrategy()
    object All : DiskCacheStrategy() // Cache original + transformed
    object Automatic : DiskCacheStrategy() // Smart decision
    object Data : DiskCacheStrategy() // Cache only original
    object Resource : DiskCacheStrategy() // Cache only transformed
}

class DiskCacheManager {
    fun shouldCacheData(strategy: DiskCacheStrategy): Boolean {
        return when (strategy) {
            DiskCacheStrategy.All,
            DiskCacheStrategy.Data,
            DiskCacheStrategy.Automatic -> true
            else -> false
        }
    }

    fun shouldCacheResource(strategy: DiskCacheStrategy): Boolean {
        return when (strategy) {
            DiskCacheStrategy.All,
            DiskCacheStrategy.Resource -> true
            else -> false
        }
    }
}
```

### 9. Glide Key Differences from Others

| Library | Memory Cache | Disk Cache | `Lifecycle` | Transformations |
|---------|-------------|-----------|-----------|-----------------|
| **Glide** | LruCache | DiskLruCache | Automatic | Built-in + Custom |
| **Fresco** | Native memory | File system | Manual | Extensive |
| **Coil** | LruCache | OkHttp cache | Coroutines | Composable |
| **Picasso** | LruCache | OkHttp cache | Manual | Limited |

### 10. Complete Usage Example

```kotlin
// Modern Glide usage
Glide.with(context) // Lifecycle-aware
    .load(url)
    .placeholder(R.drawable.placeholder)
    .error(R.drawable.error)
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .transform(CenterCrop(), RoundedCorners(16))
    .transition(DrawableTransitionOptions.withCrossFade())
    .thumbnail(0.25f) // Load low-res first
    .into(imageView)
```

---

## Ответ (RU)

Библиотеки загрузки изображений, такие как Glide, Fresco и Coil, решают сложные задачи, связанные с эффективной загрузкой, кэшированием и отображением изображений в Android-приложениях.


### Основные Компоненты

1. **Memory Cache** - LruCache для быстрого доступа
2. **Disk Cache** - Кэш на диске
3. **Network Fetcher** - Загрузка из сети
4. **Request Manager** - Управление жизненным циклом
5. **Transformation Engine** - Преобразование изображений

### Pipeline Загрузки

1. Проверка memory cache
2. Проверка active resources
3. Проверка disk cache
4. Загрузка из сети
5. Сохранение в кэши
6. Отображение

### Лучшие Практики

- Автоматическое управление жизненным циклом
- Дедупликация запросов
- Повторное использование `Bitmap`
- Эффективное кэширование

---


## Follow-ups

- [[bitmap-handling]]
- [[caching]]
- [[glide]]


## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]
- [[c-database-design]]
- [[c-scoped-storage-security]]


### Related (Medium)
- [[q-repository-multiple-sources--android--medium]] - Architecture

## References
- [Glide Documentation](https://bumptech.github.io/glide/)
- [Coil Documentation](https://coil-kt.github.io/coil/)
