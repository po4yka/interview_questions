---
id: android-084
title: "Memory Leak vs OOM / Утечка памяти vs OOM"
aliases: ["Memory Leak vs OOM", "Утечка памяти vs OOM"]
topic: android
subtopics: [performance-memory, profiling]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-coroutine-memory-leak-detection--kotlin--hard, q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium, q-what-is-the-main-application-execution-thread--android--easy]
sources: []
created: 2025-10-13
updated: 2025-10-31
tags: [android, android/performance-memory, android/profiling, difficulty/medium, leakcanary, memory-leak, oom]
---

# Вопрос (RU)
> В чём разница между утечкой памяти и OutOfMemoryError в Android? Как их обнаружить и исправить?

# Question (EN)
> What is the difference between a memory leak and OutOfMemoryError in Android? How do you detect and fix them?

---

## Ответ (RU)

**Утечки памяти** и **OutOfMemoryError** — разные проблемы. Утечки постепенно расходуют память, что может привести к OOM-краху.

### 1. Утечка Памяти

**Определение**: Объекты больше не нужны, но остаются referenced — GC не может их собрать.

**Типичные причины и решения:**

```kotlin
// ❌ Static-ссылка на Activity
class LeakyActivity : AppCompatActivity() {
    companion object {
        var listener: OnDataListener? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        listener = object : OnDataListener {
            override fun onData(data: String) {
                updateUI(data)  // Удерживает Activity
            }
        }
    }
}

// ✅ WeakReference
class FixedActivity : AppCompatActivity() {
    companion object {
        var listenerRef: WeakReference<OnDataListener>? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val listener = object : OnDataListener {
            override fun onData(data: String) { updateUI(data) }
        }
        listenerRef = WeakReference(listener)
    }
}
```

```kotlin
// ❌ Handler-утечка
class HandlerLeakActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed({ updateUI() }, 60_000)
    }
}

// ✅ Static Handler + WeakReference + очистка
class FixedHandlerActivity : AppCompatActivity() {
    private val handler = MyHandler(this)

    class MyHandler(activity: FixedHandlerActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            activityRef.get()?.updateUI()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }
}
```

```kotlin
// ✅ Lifecycle-aware coroutines (лучший подход)
class CoroutineActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            while (isActive) {
                updateUI()
                delay(1000)
            }
            // Автоматическая отмена при destroy
        }
    }
}
```

### 2. OutOfMemoryError (OOM)

**Определение**: Попытка выделить больше памяти, чем доступно.

**Типичные причины и решения:**

```kotlin
// ❌ Загрузка больших изображений
val bitmap = BitmapFactory.decodeFile("/sdcard/large_image.jpg")

// ✅ Glide с автоматическим управлением памятью
Glide.with(this)
    .load("/sdcard/large_image.jpg")
    .override(imageView.width, imageView.height)
    .into(imageView)
```

```kotlin
// ❌ Избыточная аллокация
val results = mutableListOf<Result>()
repeat(1_000_000) {
    results.add(Result(it, it.toString()))
}

// ✅ Lazy-генерация через Sequence
fun processLargeDataset(): Sequence<Result> = sequence {
    repeat(1_000_000) {
        yield(Result(it, it.toString()))
    }
}
```

### 3. Инструменты Обнаружения

**LeakCanary** (автоматическое обнаружение утечек):

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.x")
}
// Zero configuration — работает из коробки
```

**Android Profiler** (мониторинг памяти):

```kotlin
class MemoryMonitor {
    fun logMemoryUsage() {
        val runtime = Runtime.getRuntime()
        val used = runtime.totalMemory() - runtime.freeMemory()
        val max = runtime.maxMemory()

        Log.d("Memory", "Used: ${used / 1024 / 1024} MB / ${max / 1024 / 1024} MB")
    }
}
```

### Предотвращение

**Утечки памяти:**
- WeakReference для долгоживущих объектов
- Очистка listeners/observers в onDestroy
- `Lifecycle`-aware компоненты (`ViewModel`, lifecycleScope)
- `Application` context вместо `Activity` context
- Отмена coroutines/jobs

**OutOfMemoryError:**
- Glide/Coil для изображений
- LruCache для bitmap
- Обработка данных частями (chunking)
- Lazy evaluation (Sequence)
- Pagination для больших наборов данных

---

## Answer (EN)

**Memory leaks** and **OutOfMemoryError** are distinct issues. Memory leaks gradually consume memory, potentially leading to OOM crashes.

### 1. Memory Leak

**Definition**: Objects are no longer needed but remain referenced, preventing garbage collection.

**Common causes and solutions:**

```kotlin
// ❌ Static reference to Activity
class LeakyActivity : AppCompatActivity() {
    companion object {
        var listener: OnDataListener? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        listener = object : OnDataListener {
            override fun onData(data: String) {
                updateUI(data)  // Holds Activity reference
            }
        }
    }
}

// ✅ WeakReference
class FixedActivity : AppCompatActivity() {
    companion object {
        var listenerRef: WeakReference<OnDataListener>? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val listener = object : OnDataListener {
            override fun onData(data: String) { updateUI(data) }
        }
        listenerRef = WeakReference(listener)
    }
}
```

```kotlin
// ❌ Handler leak
class HandlerLeakActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed({ updateUI() }, 60_000)
    }
}

// ✅ Static Handler + WeakReference + cleanup
class FixedHandlerActivity : AppCompatActivity() {
    private val handler = MyHandler(this)

    class MyHandler(activity: FixedHandlerActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            activityRef.get()?.updateUI()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }
}
```

```kotlin
// ✅ Lifecycle-aware coroutines (best approach)
class CoroutineActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            while (isActive) {
                updateUI()
                delay(1000)
            }
            // Automatically cancelled on destroy
        }
    }
}
```

### 2. OutOfMemoryError (OOM)

**Definition**: App attempts to allocate more memory than available.

**Common causes and solutions:**

```kotlin
// ❌ Loading large bitmaps
val bitmap = BitmapFactory.decodeFile("/sdcard/large_image.jpg")

// ✅ Glide with automatic memory management
Glide.with(this)
    .load("/sdcard/large_image.jpg")
    .override(imageView.width, imageView.height)
    .into(imageView)
```

```kotlin
// ❌ Excessive allocation
val results = mutableListOf<Result>()
repeat(1_000_000) {
    results.add(Result(it, it.toString()))
}

// ✅ Lazy generation with Sequence
fun processLargeDataset(): Sequence<Result> = sequence {
    repeat(1_000_000) {
        yield(Result(it, it.toString()))
    }
}
```

### 3. Detection Tools

**LeakCanary** (automatic leak detection):

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.x")
}
// Zero configuration — works out of the box
```

**Android Profiler** (memory monitoring):

```kotlin
class MemoryMonitor {
    fun logMemoryUsage() {
        val runtime = Runtime.getRuntime()
        val used = runtime.totalMemory() - runtime.freeMemory()
        val max = runtime.maxMemory()

        Log.d("Memory", "Used: ${used / 1024 / 1024} MB / ${max / 1024 / 1024} MB")
    }
}
```

### Prevention

**Memory Leaks:**
- WeakReference for long-lived objects
- Clean up listeners/observers in onDestroy
- `Lifecycle`-aware components (`ViewModel`, lifecycleScope)
- `Application` context instead of `Activity` context
- Cancel coroutines/jobs properly

**OutOfMemoryError:**
- Glide/Coil for images
- LruCache for bitmaps
- Process data in chunks
- Lazy evaluation (Sequence)
- Pagination for large datasets

---

## Follow-ups

- How does WeakReference differ from SoftReference in Android?
- What are the memory implications of configuration changes (rotation)?
- How does the garbage collector work in Android (ART vs Dalvik)?
- What is the difference between heap memory and native memory?
- How to handle memory pressure with ComponentCallbacks2?

## References

- Android Memory Management: https://developer.android.com/topic/performance/memory
- LeakCanary Documentation: https://square.github.io/leakcanary/
- [[c-android-lifecycle]]
- [[c-coroutines]]
- [[c-viewmodel]]

## Related Questions

### Prerequisites
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Understanding Android threading fundamentals
- [[q-primitive-vs-reference-types--programming-languages--easy]] - Memory management basics

### Related
- [[q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium]] - UI lifecycle and memory
- [[q-play-feature-delivery-dynamic-modules--android--medium]] - Memory-efficient modularization
- [[q-coroutine-memory-leaks--kotlin--hard]] - `Coroutine`-specific memory issues

### Advanced
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Advanced leak detection strategies
- [[q-kotlin-native--kotlin--hard]] - Native memory management
