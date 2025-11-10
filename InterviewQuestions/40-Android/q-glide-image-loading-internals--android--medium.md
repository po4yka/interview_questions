---
id: android-034
title: How do image loading libraries like Glide work internally? / Как работают библиотеки загрузки изображений вроде Glide?
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
- en
- ru
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository
status: draft
moc: moc-android
related:
- c-memory-management
- c-database-design
- c-scoped-storage-security
created: 2025-10-06
updated: 2025-11-10
tags:
- android/cache-offline
- android/files-media
- android/performance-memory
- difficulty/medium
- en
- ru

---

# Вопрос (RU)
> Как работают библиотеки загрузки изображений вроде Glide/Fresco внутри?

# Question (EN)
> How do image loading libraries like Glide/Fresco work internally?

---

## Ответ (RU)

Библиотеки загрузки изображений, такие как Glide, Fresco и Coil, решают сложные задачи эффективной загрузки, кэширования и отображения изображений в Android-приложениях. Ниже приведён упрощённый (концептуальный) обзор архитектуры Glide-подобных библиотек. Это НЕ точный исходный код Glide.

### 1. Основные компоненты Glide-подобных библиотек

```kotlin
// Высокоуровневый (упрощённый) обзор архитектуры Glide-подобной библиотеки

           RequestManager
  (Управление запросами с учётом жизненного цикла)


        Request Coordinator & Engine
    (Планирование задач, потоки, дедупликация)


 Memory          Disk           Network
 Cache           Cache          Fetcher
 (Lru-like)      (DiskLru-like) (например, OkHttp)
```

Ключевые части:
- Memory cache: LRU-подобный кэш в памяти для декодированных ресурсов (Bitmap/Drawable).
- Disk cache: LRU-подобный кэш на диске для исходных данных и/или преобразованных ресурсов.
- Model loader / fetcher: преобразует модель (URL, Uri, файл, ресурс) в поток данных.
- Decoder: декодирует данные в Bitmap/Drawable.
- Transformation: масштабирование, обрезка, скругление углов и т.п.
- RequestManager: привязка запросов к жизненному циклу `Activity`/`Fragment`/`View`.
- Engine: координация поиска в кэше, декодирования, трансформаций и доставки результата.

### 2. Pipeline загрузки (упрощённый)

```kotlin
// Сильно упрощённый, концептуальный пример потока загрузки (не production-ready)

class GlideRequestFlow(
    private val memoryCache: MemoryCache,
    private val diskCache: DiskCache,
    private val httpClient: HttpClient,
    private val diskExecutor: Executor,
    private val networkExecutor: Executor,
    private val mainHandler: Handler,
) {
    fun loadImage(url: String, target: ImageView) {
        // 1. Проверка кэша в памяти (самый быстрый путь, можно на потоке вызова)
        memoryCache.get(url)?.let { bitmap ->
            target.setImageBitmap(bitmap)
            return
        }

        // 2. Проверка disk cache во вспомогательном потоке
        diskExecutor.execute {
            val diskStream = diskCache.get(url)
            if (diskStream != null) {
                val bitmap = BitmapFactory.decodeStream(diskStream)
                memoryCache.put(url, bitmap)
                mainHandler.post { target.setImageBitmap(bitmap) }
                return@execute
            }

            // 3. Загрузка из сети во фоновом потоке
            networkExecutor.execute {
                val stream = httpClient.fetch(url)
                val bitmap = BitmapFactory.decodeStream(stream)

                // Сохранение в disk/memory cache
                diskCache.put(url, bitmap)
                memoryCache.put(url, bitmap)

                // Доставка на главный поток
                mainHandler.post { target.setImageBitmap(bitmap) }
            }
        }
    }
}
```

Типичный упрощённый порядок:
1. Проверка кэша в памяти (самый быстрый путь).
2. Поиск в disk cache (фоновый поток).
3. При отсутствии — загрузка из сети (фоновый поток).
4. Декодирование, применение трансформаций.
5. Сохранение результатов в соответствующие кэши.
6. Доставка результата на главный поток и отображение в целевом `ImageView` / `View`.
7. Управление `active resources` (отдельная структура для уже используемых ресурсов), а также более надёжная обработка ключей, ошибок, пулами, отменой и т.д. в реальных реализациях.

### 3. Memory Cache (концептуальный пример)

```kotlin
class MemoryCache(maxSizeKb: Int) {

    private val cache = object : LruCache<String, Bitmap>(maxSizeKb) {
        override fun sizeOf(key: String, value: Bitmap): Int {
            return value.byteCount / 1024 // размер в КБ
        }
    }

    fun get(key: String): Bitmap? = cache.get(key)

    fun put(key: String, bitmap: Bitmap) {
        cache.put(key, bitmap)
    }
}
```

На практике `maxSizeKb` часто выбирают как долю от `Runtime.getRuntime().maxMemory()` (например, около 1/8 под кэш изображений).

### 4. Управление жизненным циклом запросов

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
                    else -> Unit
                }
            }
        })
    }

    fun load(url: String): RequestBuilder {
        val request = RequestBuilder(url, this)
        requests.add(request)
        return request
    }

    internal fun remove(request: ImageRequest) {
        requests.remove(request)
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

Glide интегрируется с жизненным циклом `FragmentActivity`, `Fragment`, `View`, автоматически приостанавливает/отменяет запросы и уменьшает утечки памяти и бесполезную работу.

### 5. Трансформации изображений

```kotlin
interface Transformation {
    fun transform(source: Bitmap, targetWidth: Int, targetHeight: Int): Bitmap
}

class CenterCropTransformation : Transformation {
    override fun transform(source: Bitmap, targetWidth: Int, targetHeight: Int): Bitmap {
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

В Glide трансформации являются частью конвейера декодирования, участвуют в формировании ключа и позволяют кэшировать результаты.

### 6. Дедупликация запросов

```kotlin
class EngineJob {
    private val activeJobs = ConcurrentHashMap<Key, Job>()

    fun load(key: Key, callback: ResourceCallback): Job {
        val existingJob = activeJobs[key]
        if (existingJob != null) {
            existingJob.addCallback(callback)
            return existingJob
        }

        val newJob = Job(key, callback) { finishedKey ->
            activeJobs.remove(finishedKey)
        }
        activeJobs[key] = newJob
        return newJob
    }
}
```

Это позволяет нескольким целям использовать один и тот же фоновой загрузчик для одинаковых запросов и избегать дублирующейся работы.

### 7. Пул Bitmap для повторного использования

```kotlin
class BitmapPool(maxSizeBytes: Int) {

    private val pool = object : LruCache<Int, MutableList<Bitmap>>(maxSizeBytes) {
        override fun sizeOf(key: Int, value: MutableList<Bitmap>): Int {
            return value.sumOf { it.byteCount }
        }
    }

    fun get(width: Int, height: Int, config: Bitmap.Config): Bitmap? {
        val bytesPerPixel = when (config) {
            Bitmap.Config.ALPHA_8 -> 1
            Bitmap.Config.RGB_565, Bitmap.Config.ARGB_4444 -> 2
            Bitmap.Config.ARGB_8888 -> 4
            Bitmap.Config.RGBA_F16 -> 8
            else -> 4
        }
        val size = width * height * bytesPerPixel
        val bitmaps = pool.get(size) ?: return null
        return if (bitmaps.isNotEmpty()) bitmaps.removeAt(bitmaps.size - 1) else null
    }

    fun put(bitmap: Bitmap) {
        if (!bitmap.isMutable) return
        val size = bitmap.byteCount
        val list = pool.get(size) ?: mutableListOf()
        list.add(bitmap)
        pool.put(size, list)
    }
}
```

Повторное использование Bitmap снижает давление на GC и повышает производительность при скролле списков.

### 8. Стратегия кэширования на диск

```kotlin
sealed class DiskCacheStrategy {
    object None : DiskCacheStrategy()        // Не кэшировать на диск
    object All : DiskCacheStrategy()         // Исходные + трансформированные
    object Automatic : DiskCacheStrategy()   // Библиотека решает сама
    object Data : DiskCacheStrategy()        // Только исходные данные
    object Resource : DiskCacheStrategy()    // Только трансформированный ресурс
}

class DiskCacheManager {
    fun shouldCacheData(strategy: DiskCacheStrategy): Boolean =
        when (strategy) {
            DiskCacheStrategy.All,
            DiskCacheStrategy.Data,
            DiskCacheStrategy.Automatic -> true
            else -> false
        }

    fun shouldCacheResource(strategy: DiskCacheStrategy): Boolean =
        when (strategy) {
            DiskCacheStrategy.All,
            DiskCacheStrategy.Resource -> true
            else -> false
        }
}
```

Эти стратегии соответствуют основным вариантам `DiskCacheStrategy` в Glide.

### 9. Glide и другие библиотеки (в общих чертах)

- Glide:
  - Сильная автоматическая интеграция с жизненным циклом, оптимизация памяти, bitmap pool.
  - Собственные memory/disk cache и движок.
- Fresco:
  - Собственный pipeline, активное использование нативной памяти, управление через Drawee.
- Coil:
  - Kotlin-first, корутины, собственные кэши (память/диск), часто OkHttp для сети.
- Picasso:
  - Более простой API, LRU-кэши и OkHttp, меньше автоматизации жизненного цикла по сравнению с Glide.

(Детали зависят от версии; это намеренно высокоуровневое сравнение.)

### 10. Пример использования Glide

```kotlin
Glide.with(context) // Привязка к жизненному циклу Activity/Fragment/View
    .load(url)
    .placeholder(R.drawable.placeholder)
    .error(R.drawable.error)
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .transform(CenterCrop(), RoundedCorners(16))
    .transition(DrawableTransitionOptions.withCrossFade())
    .thumbnail(0.25f) // Сначала загружается низкое разрешение
    .into(imageView)
```

---

## Answer (EN)

Image loading libraries like Glide, Fresco, and Coil solve complex problems related to loading, caching, and displaying images efficiently in Android applications. Below is a simplified, conceptual view of how Glide-like libraries are structured (not the exact source code).

### 1. Core Components of Glide-like Libraries

```kotlin
// High-level (simplified) overview of Glide-like architecture

           RequestManager
  (Lifecycle-aware request management)


        Request Coordinator & Engine
    (Job scheduling, threading, deduplication)


 Memory          Disk           Network
 Cache           Cache          Fetcher
 (Lru-like)      (DiskLru-like) (e.g., OkHttp)
```

Key pieces:
- Memory cache: in-memory LRU-style cache for decoded resources (e.g., Bitmaps, Drawables).
- Disk cache: LRU-style cache for original data and/or transformed resources.
- Model loaders/fetchers: turn models (URL, file, Uri, resource) into data streams.
- Decoders: decode data (e.g., byte stream) into Bitmaps/Drawables.
- Transformations: resize/crop/round etc. before displaying.
- RequestManager: ties requests to Android lifecycle (`Activity`/`Fragment`/`View`).
- Engine: orchestrates cache lookup, decoding, transformation, and delivery.

### 2. Loading Pipeline (Simplified)

```kotlin
// Highly simplified, conceptual loading process (not production-ready)

class GlideRequestFlow(
    private val memoryCache: MemoryCache,
    private val diskCache: DiskCache,
    private val httpClient: HttpClient,
    private val diskExecutor: Executor,
    private val networkExecutor: Executor,
    private val mainHandler: Handler,
) {
    fun loadImage(url: String, target: ImageView) {
        // 1. Check memory cache (fastest, must run on caller thread)
        memoryCache.get(url)?.let { bitmap ->
            target.setImageBitmap(bitmap)
            return
        }

        // 2. Check disk cache off the main thread
        diskExecutor.execute {
            val diskStream = diskCache.get(url)
            if (diskStream != null) {
                val bitmap = BitmapFactory.decodeStream(diskStream)
                memoryCache.put(url, bitmap)
                mainHandler.post { target.setImageBitmap(bitmap) }
                return@execute
            }

            // 3. Fetch from network off the main thread
            networkExecutor.execute {
                val stream = httpClient.fetch(url)
                val bitmap = BitmapFactory.decodeStream(stream)

                // Save to disk and memory caches
                diskCache.put(url, bitmap)
                memoryCache.put(url, bitmap)

                mainHandler.post { target.setImageBitmap(bitmap) }
            }
        }
    }
}
```

Notes:
- Real Glide also maintains an `active resources` map for resources currently in use.
- Real implementations are more robust (keys, error handling, pooling, cancellation, etc.).

### 3. Memory Cache (Conceptual Example)

```kotlin
// Wrapper around Android's LruCache with proper size accounting.

class MemoryCache(maxSizeKb: Int) {

    private val cache = object : LruCache<String, Bitmap>(maxSizeKb) {
        override fun sizeOf(key: String, value: Bitmap): Int {
            // Size in KB
            return value.byteCount / 1024
        }
    }

    fun get(key: String): Bitmap? = cache.get(key)

    fun put(key: String, bitmap: Bitmap) {
        cache.put(key, bitmap)
    }
}
```

In real projects, `maxSizeKb` is often derived from `Runtime.getRuntime().maxMemory()` (e.g., ~1/8 for image cache).

### 4. Request Lifecycle Management

```kotlin
// Simplified example of lifecycle-aware request manager.

class RequestManager(private val lifecycle: Lifecycle) {
    private val requests = mutableSetOf<ImageRequest>()

    init {
        lifecycle.addObserver(object : LifecycleEventObserver {
            override fun onStateChanged(source: LifecycleOwner, event: Lifecycle.Event) {
                when (event) {
                    Lifecycle.Event.ON_START -> resumeRequests()
                    Lifecycle.Event.ON_STOP -> pauseRequests()
                    Lifecycle.Event.ON_DESTROY -> clearRequests()
                    else -> Unit
                }
            }
        })
    }

    fun load(url: String): RequestBuilder {
        val request = RequestBuilder(url, this)
        requests.add(request)
        return request
    }

    internal fun remove(request: ImageRequest) {
        requests.remove(request)
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

Glide integrates with `FragmentActivity`, `Fragment`, and `View` lifecycles to automatically pause/cancel requests, reducing leaks and wasted work.

### 5. Image Transformations

```kotlin
interface Transformation {
    fun transform(source: Bitmap, targetWidth: Int, targetHeight: Int): Bitmap
}

class CenterCropTransformation : Transformation {
    override fun transform(source: Bitmap, targetWidth: Int, targetHeight: Int): Bitmap {
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

In Glide, transformations are applied as part of the decode/transform pipeline, contribute to the cache key, and allow caching of transformed results.

### 6. Request Deduplication (Engine Job)

```kotlin
// If two views request the same resource key, share one load.

class EngineJob {
    private val activeJobs = ConcurrentHashMap<Key, Job>()

    fun load(key: Key, callback: ResourceCallback): Job {
        val existingJob = activeJobs[key]
        if (existingJob != null) {
            existingJob.addCallback(callback)
            return existingJob // Reuse existing job
        }

        val newJob = Job(key, callback) { finishedKey ->
            activeJobs.remove(finishedKey)
        }
        activeJobs[key] = newJob
        return newJob
    }
}
```

This avoids duplicate network/decoding work for identical requests.

### 7. Bitmap Pool for Reuse

```kotlin
// Conceptual bitmap pool: real Glide uses more complex strategies.

class BitmapPool(maxSizeBytes: Int) {

    private val pool = object : LruCache<Int, MutableList<Bitmap>>(maxSizeBytes) {
        override fun sizeOf(key: Int, value: MutableList<Bitmap>): Int {
            return value.sumOf { it.byteCount }
        }
    }

    fun get(width: Int, height: Int, config: Bitmap.Config): Bitmap? {
        val bytesPerPixel = when (config) {
            Bitmap.Config.ALPHA_8 -> 1
            Bitmap.Config.RGB_565, Bitmap.Config.ARGB_4444 -> 2
            Bitmap.Config.ARGB_8888 -> 4
            Bitmap.Config.RGBA_F16 -> 8
            else -> 4
        }
        val size = width * height * bytesPerPixel
        val bitmaps = pool.get(size) ?: return null
        return if (bitmaps.isNotEmpty()) bitmaps.removeAt(bitmaps.size - 1) else null
    }

    fun put(bitmap: Bitmap) {
        if (!bitmap.isMutable) return
        val size = bitmap.byteCount
        val list = pool.get(size) ?: mutableListOf()
        list.add(bitmap)
        pool.put(size, list)
    }
}
```

Bitmap reuse reduces GC pressure and improves performance, especially when scrolling lists.

### 8. Disk Cache Strategy (Modeled After Glide)

```kotlin
sealed class DiskCacheStrategy {
    object None : DiskCacheStrategy()              // No disk caching
    object All : DiskCacheStrategy()               // Original + transformed
    object Automatic : DiskCacheStrategy()         // Let library decide
    object Data : DiskCacheStrategy()              // Only original data
    object Resource : DiskCacheStrategy()          // Only transformed
}

class DiskCacheManager {
    fun shouldCacheData(strategy: DiskCacheStrategy): Boolean =
        when (strategy) {
            DiskCacheStrategy.All,
            DiskCacheStrategy.Data,
            DiskCacheStrategy.Automatic -> true
            else -> false
        }

    fun shouldCacheResource(strategy: DiskCacheStrategy): Boolean =
        when (strategy) {
            DiskCacheStrategy.All,
            DiskCacheStrategy.Resource -> true
            else -> false
        }
}
```

These strategies are similar to Glide's real `DiskCacheStrategy` options.

### 9. Glide vs Other Libraries (High-Level, Simplified)

- Glide:
  - Strong focus on automatic lifecycle integration, memory efficiency, bitmap pooling.
  - Custom memory/disk cache and engine.
- Fresco:
  - Uses native memory and its own pipeline; manages Drawee hierarchy and lifecycle explicitly.
- Coil:
  - Kotlin-first, coroutine-based; has its own memory/disk caches; often uses OkHttp for networking.
- Picasso:
  - Simpler API; uses LRU caches and OkHttp; less automatic lifecycle integration compared to Glide.

(Details vary by version; this is intentionally high-level.)

### 10. Complete Usage Example (Glide)

```kotlin
// Example of modern Glide usage
Glide.with(context) // Lifecycle-aware (Activity/Fragment/View)
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

## Дополнительные вопросы (RU)

- Как бы вы спроектировали стратегию кэширования для изображений с разными размерами и качеством?
- Как избежать утечек памяти и OOM при использовании Glide/Fresco в списках (`RecyclerView`)?
- Как реализовать собственный `ModelLoader` или источник данных в Glide?

## Follow-ups (EN)

- How would you design a caching strategy for images with different sizes and qualities?
- How would you avoid memory leaks and OOM when using Glide/Fresco in scrolling lists (`RecyclerView`)?
- How would you implement a custom `ModelLoader` or data source in Glide?

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]
- [[c-database-design]]
- [[c-scoped-storage-security]]

## References

- [Glide Documentation](https://bumptech.github.io/glide/)
- [Coil Documentation](https://coil-kt.github.io/coil/)
