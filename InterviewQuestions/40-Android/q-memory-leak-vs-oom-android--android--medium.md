---
id: android-084
title: "Memory Leak vs OOM / Утечка памяти vs OOM"
aliases: ["Memory Leak vs OOM", "Утечка памяти vs OOM"]
topic: android
subtopics: [performance-battery, performance-memory]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-garbage-collection, q-coroutine-memory-leak-detection--kotlin--hard, q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium, q-what-is-the-main-application-execution-thread--android--easy]
sources: []
created: 2025-10-13
updated: 2025-11-10
tags: [android, android/performance-battery, android/performance-memory, difficulty/medium, leakcanary, memory-leak, oom]

---
# Вопрос (RU)
> В чём разница между утечкой памяти и OutOfMemoryError в Android? Как их обнаружить и исправить?

# Question (EN)
> What is the difference between a memory leak and OutOfMemoryError in Android? How do you detect and fix them?

---

## Ответ (RU)

**Утечки памяти** и **OutOfMemoryError** — связанные, но разные проблемы.
- Утечка памяти — логическая ошибка, когда объекты больше не нужны, но остаются достижимыми, и GC не может их освободить.
- OutOfMemoryError (OOM) — симптом: попытка выделить память, когда свободной памяти (в Java heap или native heap) уже недостаточно. OOM может быть вызван как утечками, так и корректным, но слишком большим потреблением памяти (например, загрузкой огромного bitmap).

### 1. Утечка Памяти

**Определение**: Объекты больше не нужны, но остаются достижимыми через цепочку ссылок (например, из статических полей, синглтонов, длинноживущих коллекций), поэтому сборщик мусора не может их собрать.

**Типичные причины и решения (упрощённые примеры):**

```kotlin
// ❌ Статическое поле хранит ссылку, связанной с Activity
// (на практике часто: listener держит Activity или View, а companion/singleton живёт дольше Activity)
class LeakyActivity : AppCompatActivity() {
    companion object {
        var listener: OnDataListener? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        listener = object : OnDataListener {
            override fun onData(data: String) {
                updateUI(data)  // updateUI() использует Activity/View; listener живёт дольше Activity
            }
        }
    }
}

// ✅ Не держать Activity через долгоживущие статические ссылки
// Ключевая идея: если нужен callback из синглтона/companion, хранить WeakReference на владельца
class FixedActivity : AppCompatActivity(), OnDataListener {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ListenerHolder.registerListener(this)
    }

    override fun onDestroy() {
        super.onDestroy()
        ListenerHolder.unregisterListener(this)
    }

    override fun onData(data: String) {
        updateUI(data)
    }
}

object ListenerHolder {
    private var listenerRef: WeakReference<OnDataListener>? = null

    fun registerListener(listener: OnDataListener) {
        listenerRef = WeakReference(listener)
    }

    fun unregisterListener(listener: OnDataListener) {
        if (listenerRef?.get() == listener) listenerRef = null
    }

    fun notifyData(data: String) {
        listenerRef?.get()?.onData(data)
    }
}
```

```kotlin
// ❌ Handler-утечка: внутренний класс не static и/или отложенные сообщения переживают Activity
class HandlerLeakActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed({ updateUI() }, 60_000)
    }
}

// ✅ Static-внутренний Handler + WeakReference + очистка сообщений
class FixedHandlerActivity : AppCompatActivity() {
    private val handler = MyHandler(this)

    private class MyHandler(activity: FixedHandlerActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            activityRef.get()?.updateUI()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.sendEmptyMessageDelayed(0, 60_000)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }
}
```

```kotlin
// ✅ Lifecycle-aware coroutines (рекомендуемый подход)
class CoroutineActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            while (isActive) {
                updateUI()
                delay(1000)
            }
            // coroutine будет автоматически отменена, когда lifecycleOwner уничтожен
        }
    }
}
```

### 2. OutOfMemoryError (OOM)

**Определение**: Исключение, возникающее при попытке выделить память, когда лимит heap (или доступная память процесса) исчерпан.

**Типичные причины и решения:**

```kotlin
// ❌ Наивная загрузка большого изображения в полный размер
val bitmap = BitmapFactory.decodeFile("/sdcard/large_image.jpg")

// ✅ Использовать Glide/Coil/Picasso для downsampling и кэширования
Glide.with(this)
    .load("/sdcard/large_image.jpg")
    .override(imageView.width, imageView.height) // под размер View
    .into(imageView)
```

```kotlin
// ❌ Избыточная аллокация большого списка целиком в памяти
val results = mutableListOf<Result>()
repeat(1_000_000) {
    results.add(Result(it, it.toString()))
}

// ✅ Ленивое перечисление / потоковая обработка без удержания всего набора в памяти
fun processLargeDataset(): Sequence<Result> = sequence {
    repeat(1_000_000) {
        yield(Result(it, it.toString()))
    }
}
```

### 3. Инструменты Обнаружения

**LeakCanary** (автоматическое обнаружение утечек в debug-сборках):

```kotlin
// build.gradle.kts (модуль приложения)
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.x")
}
// Дополнительная конфигурация обычно не требуется, работает "из коробки" в debug.
```

**Android Profiler** (мониторинг памяти, heap dump, анализ allocs) + вспомогательные логи:

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
- Не хранить `Activity`/`Fragment`/`View` в статических полях и синглтонах.
- Освобождать listeners/observers/колбэки в onDestroy/onCleared и т.п.
- Использовать lifecycle-aware компоненты (`ViewModel`, lifecycleScope, `LiveData`/`Flow` с owner'ом).
- Использовать `Application` context только там, где действительно нужен контекст приложения (и избегать утечек `Activity` context).
- Корректно отменять coroutines/jobs и другие асинхронные операции.

**OutOfMemoryError:**
- Использовать библиотеки для работы с изображениями (Glide/Coil) с downsampling и кэшированием.
- Применять LruCache для bitmap и других тяжёлых объектов.
- Обрабатывать большие данные частями (chunking/streaming), избегать удержания всего набора в памяти.
- Использовать ленивую оценку (Sequence/flows) там, где возможно.
- Использовать pagination/постраничную загрузку для больших списков.

---

## Answer (EN)

**Memory leaks** and **OutOfMemoryError** are related but distinct issues.
- A memory leak is a logical/programming bug where objects that are no longer needed remain reachable, so the GC cannot reclaim them.
- OutOfMemoryError (OOM) is a runtime symptom: an allocation fails because the app has exhausted its allowed memory (Java heap and/or native). OOM can be caused by leaks or by legitimately large allocations (e.g., huge bitmaps or data sets).

### 1. Memory Leak

**Definition**: Objects are no longer needed but remain reachable through a chain of references (e.g., from static fields, singletons, long-lived collections), preventing garbage collection.

**Common causes and solutions (simplified examples):**

```kotlin
// ❌ Static holder keeps a reference chain tied to an Activity
// In practice: a listener or callback stored in a singleton/companion indirectly holds Activity/View
class LeakyActivity : AppCompatActivity() {
    companion object {
        var listener: OnDataListener? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        listener = object : OnDataListener {
            override fun onData(data: String) {
                updateUI(data)  // updateUI() uses Activity/View; listener may outlive the Activity
            }
        }
    }
}

// ✅ Do not keep Activities in long-lived static references
// Key idea: if a singleton/companion needs a callback, keep a WeakReference to the owner
class FixedActivity : AppCompatActivity(), OnDataListener {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ListenerHolder.registerListener(this)
    }

    override fun onDestroy() {
        super.onDestroy()
        ListenerHolder.unregisterListener(this)
    }

    override fun onData(data: String) {
        updateUI(data)
    }
}

object ListenerHolder {
    private var listenerRef: WeakReference<OnDataListener>? = null

    fun registerListener(listener: OnDataListener) {
        listenerRef = WeakReference(listener)
    }

    fun unregisterListener(listener: OnDataListener) {
        if (listenerRef?.get() == listener) listenerRef = null
    }

    fun notifyData(data: String) {
        listenerRef?.get()?.onData(data)
    }
}
```

```kotlin
// ❌ Handler leak: non-static inner class and/or delayed messages outlive the Activity
class HandlerLeakActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed({ updateUI() }, 60_000)
    }
}

// ✅ Static inner Handler + WeakReference + removing pending messages
class FixedHandlerActivity : AppCompatActivity() {
    private val handler = MyHandler(this)

    private class MyHandler(activity: FixedHandlerActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            activityRef.get()?.updateUI()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.sendEmptyMessageDelayed(0, 60_000)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }
}
```

```kotlin
// ✅ Lifecycle-aware coroutines (recommended approach)
class CoroutineActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            while (isActive) {
                updateUI()
                delay(1000)
            }
            // Automatically cancelled when the LifecycleOwner is destroyed
        }
    }
}
```

### 2. OutOfMemoryError (OOM)

**Definition**: Thrown when an allocation request cannot be satisfied because the process has exhausted its memory limits.

**Common causes and solutions:**

```kotlin
// ❌ Naively loading a huge bitmap at full resolution
val bitmap = BitmapFactory.decodeFile("/sdcard/large_image.jpg")

// ✅ Use Glide/Coil/Picasso to downsample and manage caching
Glide.with(this)
    .load("/sdcard/large_image.jpg")
    .override(imageView.width, imageView.height) // match the View size
    .into(imageView)
```

```kotlin
// ❌ Holding a massive collection entirely in memory
val results = mutableListOf<Result>()
repeat(1_000_000) {
    results.add(Result(it, it.toString()))
}

// ✅ Lazy / streaming processing to avoid keeping everything in memory
fun processLargeDataset(): Sequence<Result> = sequence {
    repeat(1_000_000) {
        yield(Result(it, it.toString()))
    }
}
```

### 3. Detection Tools

**LeakCanary** (automatic leak detection in debug builds):

```kotlin
// build.gradle.kts (app module)
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.x")
}
// No extra setup required for typical usage; works out of the box in debug.
```

**Android Profiler** (memory monitoring, heap dumps, allocation tracking) + helper logs:

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
- Do not keep `Activity`/`Fragment`/`View` references in static fields or long-lived singletons.
- Properly unregister listeners/observers/callbacks in onDestroy/onCleared/etc.
- Use lifecycle-aware components (`ViewModel`, lifecycleScope, `LiveData`/`Flow` tied to a LifecycleOwner).
- Use `Application` context only when an application-wide context is appropriate; avoid leaking `Activity` context.
- Correctly cancel coroutines/jobs and other async work.

**OutOfMemoryError:**
- Use image libraries (Glide/Coil) with downsampling and caching.
- Use LruCache for bitmaps and other heavy objects.
- Process large data sets in chunks/streams instead of loading everything at once.
- Prefer lazy evaluation (Sequence/flows) where suitable.
- Use pagination / incremental loading for large lists.

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
- [[c-coroutines]]
- [[c-viewmodel]]

## Related Questions

### Prerequisites
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Understanding Android threading fundamentals
- [[q-primitive-vs-reference-types--kotlin--easy]] - Memory management basics

### Related
- [[q-how-to-tell-adapter-to-redraw-list-if-an-item-was-deleted--android--medium]] - UI lifecycle and memory
- [[q-play-feature-delivery-dynamic-modules--android--medium]] - Memory-efficient modularization
- [[q-coroutine-memory-leaks--kotlin--hard]] - `Coroutine`-specific memory issues

### Advanced
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Advanced leak detection strategies
- [[q-kotlin-native--kotlin--hard]] - Native memory management
