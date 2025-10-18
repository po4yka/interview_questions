---
id: 20251012-12271136
title: "Memory Leak Vs Oom Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: [memory, memory-leak, oom, performance-memory, leakcanary, debugging, difficulty/medium]
moc: moc-android
related: [q-what-is-the-main-application-execution-thread--android--easy, q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium, q-play-feature-delivery-dynamic-modules--android--medium]
---
# Memory Leak vs OutOfMemoryError in Android

**Сложность**: 🟡 Medium
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
What is the difference between a memory leak and OutOfMemoryError in Android? How do you detect and fix them?

## Answer (EN)
Memory leaks and OutOfMemoryErrors are related but distinct issues. Memory leaks gradually consume memory, potentially leading to OutOfMemoryError crashes.

#### 1. **Memory Leak**

A memory leak occurs when objects are no longer needed but remain referenced, preventing garbage collection.

**Common Causes:**

```kotlin
// - BAD: Activity leak via static reference
class LeakyActivity : AppCompatActivity() {
    companion object {
        private var listener: OnDataListener? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Activity referenced by static field
        // Never garbage collected even after finish()
        listener = object : OnDataListener {
            override fun onData(data: String) {
                updateUI(data) // References Activity
            }
        }
    }
}

// - BAD: Handler leak
class HandlerLeakActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Non-static inner class holds implicit reference to Activity
        handler.postDelayed({
            updateUI() // Leaks Activity if posted long delay
        }, 60000) // 1 minute
    }
}

// - BAD: Anonymous listener leak
class ListenerLeakActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // EventBus holds reference to Activity
        EventBus.getDefault().register(object : EventListener {
            override fun onEvent(event: Event) {
                handleEvent(event)
            }
        })

        // Never unregistered!
    }
}

// - BAD: Thread leak
class ThreadLeakActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        Thread {
            while (true) {
                // Activity referenced by thread
                runOnUiThread {
                    updateUI() // Leaks Activity
                }
                Thread.sleep(1000)
            }
        }.start()
    }
}
```

**- Proper Solutions:**

```kotlin
// - GOOD: Use WeakReference
class FixedActivity : AppCompatActivity() {
    companion object {
        private var listenerRef: WeakReference<OnDataListener>? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val listener = object : OnDataListener {
            override fun onData(data: String) {
                updateUI(data)
            }
        }
        listenerRef = WeakReference(listener)
    }
}

// - GOOD: Static Handler + WeakReference
class FixedHandlerActivity : AppCompatActivity() {
    private val handler = MyHandler(this)

    class MyHandler(activity: FixedHandlerActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            activityRef.get()?.let { activity ->
                activity.updateUI()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }
}

// - GOOD: Proper lifecycle management
class FixedListenerActivity : AppCompatActivity() {
    private val eventListener = object : EventListener {
        override fun onEvent(event: Event) {
            handleEvent(event)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        EventBus.getDefault().register(eventListener)
    }

    override fun onDestroy() {
        super.onDestroy()
        EventBus.getDefault().unregister(eventListener)
    }
}

// - GOOD: Lifecycle-aware coroutines
class CoroutineActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            while (isActive) {
                updateUI()
                delay(1000)
            }
            // Automatically cancelled when lifecycle destroyed
        }
    }
}

// - GOOD: ViewModel for data retention
class ViewModelActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ViewModel survives configuration changes
        // No Activity leak
        viewModel.data.observe(this) { data ->
            updateUI(data)
        }
    }
}
```

#### 2. **OutOfMemoryError (OOM)**

OOM occurs when the app tries to allocate more memory than available.

**Common Causes:**

```kotlin
// - BAD: Loading large bitmaps
class OOMActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Loading large image without scaling
        val bitmap = BitmapFactory.decodeFile("/sdcard/large_image.jpg")
        // May throw OOM if image is too large
        imageView.setImageBitmap(bitmap)
    }
}

// - BAD: Excessive object allocation
fun processLargeDataset() {
    val results = mutableListOf<Result>()

    repeat(1_000_000) {
        // Allocating millions of objects
        results.add(Result(it, it.toString()))
    }
    // OOM if dataset too large
}

// - BAD: Memory leak accumulation
class LeakyService : Service() {
    companion object {
        private val leakedActivities = mutableListOf<Activity>()
    }

    fun registerActivity(activity: Activity) {
        leakedActivities.add(activity)
        // Activities never removed
        // Eventually causes OOM
    }
}
```

**- Solutions:**

```kotlin
// - GOOD: Proper bitmap loading
class OptimizedActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Use Glide/Coil for automatic memory management
        Glide.with(this)
            .load("/sdcard/large_image.jpg")
            .override(imageView.width, imageView.height)
            .into(imageView)
    }

    // Or manual bitmap scaling
    private fun decodeSampledBitmap(path: String, reqWidth: Int, reqHeight: Int): Bitmap {
        return BitmapFactory.Options().run {
            inJustDecodeBounds = true
            BitmapFactory.decodeFile(path, this)

            inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
            inJustDecodeBounds = false

            BitmapFactory.decodeFile(path, this)
        }
    }

    private fun calculateInSampleSize(
        options: BitmapFactory.Options,
        reqWidth: Int,
        reqHeight: Int
    ): Int {
        val (height, width) = options.run { outHeight to outWidth }
        var inSampleSize = 1

        if (height > reqHeight || width > reqWidth) {
            val halfHeight = height / 2
            val halfWidth = width / 2

            while (halfHeight / inSampleSize >= reqHeight &&
                halfWidth / inSampleSize >= reqWidth
            ) {
                inSampleSize *= 2
            }
        }

        return inSampleSize
    }
}

// - GOOD: Process data in chunks
suspend fun processLargeDataset() = withContext(Dispatchers.Default) {
    val results = mutableListOf<Result>()
    val chunkSize = 1000

    (0 until 1_000_000 step chunkSize).forEach { start ->
        val chunk = (start until minOf(start + chunkSize, 1_000_000))
            .map { Result(it, it.toString()) }

        results.addAll(chunk)

        // Allow GC between chunks
        if (start % 10000 == 0) {
            delay(1)
        }
    }

    results
}

// - GOOD: Use Sequence for lazy evaluation
fun processLargeDatasetLazy(): Sequence<Result> {
    return sequence {
        repeat(1_000_000) {
            yield(Result(it, it.toString()))
            // Items generated on-demand, not all at once
        }
    }
}
```

#### 3. **Detection Tools**

**3.1 LeakCanary (Memory Leaks)**

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}

// Automatically detects and reports leaks
// No additional code needed

// Custom leak detection
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            // Watch custom objects
            AppWatcher.objectWatcher.watch(
                watchedObject = myObject,
                description = "My custom object"
            )
        }
    }
}
```

**3.2 Android Profiler (Memory Analysis)**

```kotlin
// Monitor memory in real-time
class MemoryMonitor {
    fun logMemoryUsage() {
        val runtime = Runtime.getRuntime()
        val usedMemory = runtime.totalMemory() - runtime.freeMemory()
        val maxMemory = runtime.maxMemory()

        Log.d("Memory", """
            Used: ${usedMemory / 1024 / 1024} MB
            Max: ${maxMemory / 1024 / 1024} MB
            Usage: ${usedMemory * 100 / maxMemory}%
        """.trimIndent())
    }

    fun dumpHeap() {
        if (BuildConfig.DEBUG) {
            val heapDumpFile = File(
                Environment.getExternalStorageDirectory(),
                "heap_dump.hprof"
            )
            Debug.dumpHprofData(heapDumpFile.absolutePath)
            Log.d("Memory", "Heap dumped to: ${heapDumpFile.absolutePath}")
        }
    }
}
```

**3.3 Manual Leak Detection**

```kotlin
class LeakDetector {
    private val activityRefs = mutableListOf<WeakReference<Activity>>()

    fun trackActivity(activity: Activity) {
        activityRefs.add(WeakReference(activity))

        activity.lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onDestroy(owner: LifecycleOwner) {
                // Schedule leak check
                Handler(Looper.getMainLooper()).postDelayed({
                    checkForLeaks()
                }, 5000)
            }
        })
    }

    private fun checkForLeaks() {
        // Force GC
        Runtime.getRuntime().gc()
        System.runFinalization()
        Runtime.getRuntime().gc()

        // Check for leaked activities
        activityRefs.removeAll { it.get() == null }

        if (activityRefs.isNotEmpty()) {
            Log.w("LeakDetector", "Potential leaks detected: ${activityRefs.size} activities")
            activityRefs.forEach { ref ->
                ref.get()?.let { activity ->
                    Log.w("LeakDetector", "Leaked: ${activity.javaClass.simpleName}")
                }
            }
        }
    }
}
```

#### 4. **Common Patterns**

**4.1 Bitmap Management**

```kotlin
class BitmapManager {
    private val bitmapCache = LruCache<String, Bitmap>(
        (Runtime.getRuntime().maxMemory() / 1024 / 8).toInt()
    ) {
        override fun sizeOf(key: String, bitmap: Bitmap): Int {
            return bitmap.byteCount / 1024
        }
    }

    fun loadBitmap(key: String, loader: () -> Bitmap): Bitmap {
        return bitmapCache.get(key) ?: run {
            val bitmap = loader()
            bitmapCache.put(key, bitmap)
            bitmap
        }
    }

    fun clear() {
        bitmapCache.evictAll()
    }
}
```

**4.2 Context References**

```kotlin
// - BAD: Storing Activity context
class BadSingleton private constructor(context: Context) {
    companion object {
        private var instance: BadSingleton? = null

        fun getInstance(context: Context): BadSingleton {
            if (instance == null) {
                instance = BadSingleton(context) // Leaks Activity!
            }
            return instance!!
        }
    }
}

// - GOOD: Using Application context
class GoodSingleton private constructor(context: Context) {
    companion object {
        private var instance: GoodSingleton? = null

        fun getInstance(context: Context): GoodSingleton {
            if (instance == null) {
                instance = GoodSingleton(context.applicationContext)
            }
            return instance!!
        }
    }
}
```

**4.3 Observable Patterns**

```kotlin
// - GOOD: Lifecycle-aware observers
class DataObserver : AppCompatActivity() {
    private val viewModel: DataViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Automatically unsubscribed when lifecycle destroyed
        viewModel.data.observe(this) { data ->
            updateUI(data)
        }
    }
}

// - GOOD: Manual lifecycle management
class ManualObserver : AppCompatActivity() {
    private val job = Job()
    private val scope = CoroutineScope(Dispatchers.Main + job)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        scope.launch {
            dataFlow.collect { data ->
                updateUI(data)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        job.cancel() // Prevent leak
    }
}
```

### Prevention Checklist

**Memory Leaks:**
- [ ] Use WeakReference for long-lived objects
- [ ] Clean up listeners/observers in onDestroy
- [ ] Use lifecycle-aware components
- [ ] Prefer Application context over Activity
- [ ] Cancel coroutines/jobs properly
- [ ] Remove Handler callbacks
- [ ] Use ViewModel for data retention
- [ ] Test with LeakCanary

**OutOfMemoryError:**
- [ ] Use image loading libraries (Glide/Coil)
- [ ] Implement bitmap caching
- [ ] Process large datasets in chunks
- [ ] Use Sequence for lazy evaluation
- [ ] Monitor memory usage
- [ ] Handle large data with pagination
- [ ] Compress/downsample images
- [ ] Release resources when not needed

---



## Ответ (RU)

# Вопрос (RU)
В чём разница между утечкой памяти и OutOfMemoryError в Android? Как их обнаружить и исправить?


## Ответ (RU)
# Вопрос (RU)
В чём разница между утечкой памяти и OutOfMemoryError в Android? Как их обнаружить и исправить?


#### Утечка памяти:

**Определение:** Объекты больше не нужны, но остаются referenced, не могут быть собраны GC.

**Частые причины:**
- Static ссылки на Activity
- Handler утечки
- Неотписанные listeners
- Thread утечки
- Context утечки в Singleton

**Решения:**
- WeakReference для долгоживущих объектов
- Очистка listeners в onDestroy
- Lifecycle-aware компоненты
- Application context вместо Activity
- Отмена coroutines/jobs
- ViewModel для данных

#### OutOfMemoryError:

**Определение:** Попытка выделить больше памяти, чем доступно.

**Частые причины:**
- Загрузка больших изображений
- Избыточная аллокация объектов
- Накопление утечек памяти

**Решения:**
- Glide/Coil для изображений
- Bitmap sampling и caching
- Обработка данных частями
- Lazy evaluation (Sequence)
- Пагинация для больших наборов данных

#### Инструменты обнаружения:

**LeakCanary:**
- Автоматическое обнаружение утечек
- Подробные отчёты
- Zero configuration

**Android Profiler:**
- Мониторинг памяти в реальном времени
- Heap dumps
- Allocation tracking

**Чек-лист предотвращения:**
- Используйте lifecycle-aware компоненты
- Очищайте ресурсы
- Мониторьте память
- Тестируйте с LeakCanary
- Оптимизируйте изображения
- Обрабатывайте данные частями

---

## Related Questions

### Computer Science Fundamentals
- [[q-primitive-vs-reference-types--programming-languages--easy]] - Memory Management
- [[q-reference-types-criteria--programming-languages--medium]] - Memory Management
- [[q-kotlin-reference-equality-operator--programming-languages--easy]] - Memory Management
- [[q-reference-types-protect-from-deletion--programming-languages--easy]] - Memory Management

### Kotlin Language Features
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Memory Management
- [[q-coroutine-memory-leaks--kotlin--hard]] - Memory Management
- [[q-kotlin-native--kotlin--hard]] - Memory Management
