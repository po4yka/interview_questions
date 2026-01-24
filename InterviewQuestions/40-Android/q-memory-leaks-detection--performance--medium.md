---
id: android-749
title: Memory Leaks Detection / Обнаружение Утечек Памяти
aliases: [LeakCanary, Memory Profiler, Обнаружение Утечек Памяти]
topic: android
subtopics: [performance, memory, debugging]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-strict-mode--performance--medium, q-profiler-tools--performance--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/performance, android/memory, difficulty/medium, leakcanary, memory-profiler]
---
# Вопрос (RU)

> Как обнаруживать утечки памяти в Android? Объясните LeakCanary и Memory Profiler.

# Question (EN)

> How do you detect memory leaks in Android? Explain LeakCanary and Memory Profiler.

---

## Ответ (RU)

**Утечка памяти** происходит, когда объект больше не нужен, но на него всё ещё есть ссылка, препятствующая сборке мусора. В Android чаще всего утекают Activity, Fragment и View.

### Краткий Ответ

- **LeakCanary** -- автоматически обнаруживает утечки в debug-сборках
- **Memory Profiler** -- инструмент Android Studio для анализа heap dump
- Основные источники утечек: статические ссылки, внутренние классы, Handler, Listener

### Подробный Ответ

### LeakCanary: Настройка

```kotlin
// build.gradle.kts
dependencies {
    // Только для debug сборок
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
}
```

LeakCanary автоматически отслеживает:
- Activity после `onDestroy()`
- Fragment после `onFragmentDestroyed()`
- Fragment View после `onDestroyView()`
- ViewModel после `onCleared()`

### Как Работает LeakCanary

```
1. Объект уничтожается (Activity.onDestroy)
         |
         v
2. LeakCanary сохраняет weak reference
         |
         v
3. Ждёт 5 секунд + GC
         |
         v
4. Проверяет: объект ещё жив?
         |
    Да   |   Нет
    v    |    v
5. Dump heap    OK
         |
         v
6. Анализ + уведомление
```

### Типичные Утечки и Исправления

#### 1. Статическая Ссылка на Context

```kotlin
// ПЛОХО -- утечка Activity
object Analytics {
    private lateinit var context: Context

    fun init(context: Context) {
        this.context = context // Activity утечёт!
    }
}

// ХОРОШО -- используем Application context
object Analytics {
    private lateinit var appContext: Context

    fun init(context: Context) {
        this.appContext = context.applicationContext
    }
}
```

#### 2. Внутренний Класс с Ссылкой на Activity

```kotlin
// ПЛОХО -- внутренний класс держит ссылку на Activity
class MyActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            // Этот Runnable держит неявную ссылку на Activity
            updateUI()
        }, 60_000) // 60 секунд
    }

    // Activity уничтожена, но Runnable всё ещё в очереди!
}

// ХОРОШО -- очищаем Handler
class MyActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())
    private val updateRunnable = Runnable { updateUI() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed(updateRunnable, 60_000)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacks(updateRunnable) // Очищаем!
    }
}
```

#### 3. Listener Не Отписан

```kotlin
// ПЛОХО -- не отписываемся от listener
class MyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        LocationManager.addListener(this) // this = Activity
    }
    // Activity уничтожена, но LocationManager держит ссылку!
}

// ХОРОШО -- отписываемся
class MyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        LocationManager.addListener(this)
    }

    override fun onDestroy() {
        super.onDestroy()
        LocationManager.removeListener(this) // Отписываемся!
    }
}
```

#### 4. View Binding во Fragment

```kotlin
// ПЛОХО -- binding живёт дольше view
class MyFragment : Fragment() {

    private lateinit var binding: FragmentMyBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }
    // binding держит ссылку на view после onDestroyView!
}

// ХОРОШО -- обнуляем binding
class MyFragment : Fragment() {

    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Обнуляем!
    }
}
```

### Memory Profiler в Android Studio

```
View -> Tool Windows -> Profiler -> Memory

Функции:
1. Live Allocations -- отслеживание аллокаций в реальном времени
2. Heap Dump -- снимок всех объектов в памяти
3. Record Allocations -- запись аллокаций за период
```

### Анализ Heap Dump

```kotlin
// Шаги анализа:
// 1. Выполнить действие (открыть/закрыть Activity)
// 2. Нажать "Force GC" несколько раз
// 3. Нажать "Dump Java Heap"
// 4. В heap dump искать:
//    - Activity по имени класса
//    - "Retained Size" -- сколько памяти держит объект
//    - "References" -- кто держит ссылку
```

### Программный Heap Dump

```kotlin
class DebugUtils {

    fun dumpHeap(context: Context) {
        val heapFile = File(context.cacheDir, "heap_${System.currentTimeMillis()}.hprof")
        Debug.dumpHprofData(heapFile.absolutePath)
        Log.d("Memory", "Heap dumped to: ${heapFile.absolutePath}")
    }

    fun logMemoryInfo() {
        val runtime = Runtime.getRuntime()
        val usedMemory = (runtime.totalMemory() - runtime.freeMemory()) / 1024 / 1024
        val maxMemory = runtime.maxMemory() / 1024 / 1024

        Log.d("Memory", "Used: ${usedMemory}MB / Max: ${maxMemory}MB")
    }
}
```

### LeakCanary Кастомизация

```kotlin
// Добавляем свои объекты для отслеживания
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Отслеживаем кастомные объекты
        val watcher = AppWatcher.objectWatcher
        watcher.expectWeaklyReachable(
            myObject,
            "MyObject should be GC'd after close()"
        )
    }
}

// Игнорируем известные утечки библиотек
class IgnoreKnownLeaks : LeakCanary.Config {
    override val referenceMatchers: List<ReferenceMatcher>
        get() = AndroidReferenceMatchers.appDefaults +
            AndroidReferenceMatchers.instanceFieldLeak(
                "com.thirdparty.Lib",
                "leakyField"
            )
}
```

### Чеклист Предотвращения Утечек

| Контекст | Правило |
|----------|---------|
| Singleton | Только `applicationContext` |
| Handler | Очищать в `onDestroy()` |
| Listener | Отписываться в `onDestroy()` |
| View Binding | Обнулять в `onDestroyView()` |
| Coroutines | Использовать `lifecycleScope` |
| Anonymous class | Избегать long-running задач |

---

## Answer (EN)

A **memory leak** occurs when an object is no longer needed but still has a reference preventing garbage collection. In Android, Activity, Fragment, and View are most commonly leaked.

### Short Answer

- **LeakCanary** -- automatically detects leaks in debug builds
- **Memory Profiler** -- Android Studio tool for heap dump analysis
- Main leak sources: static references, inner classes, Handler, Listener

### Detailed Answer

### LeakCanary: Setup

```kotlin
// build.gradle.kts
dependencies {
    // Debug builds only
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
}
```

LeakCanary automatically watches:
- Activity after `onDestroy()`
- Fragment after `onFragmentDestroyed()`
- Fragment View after `onDestroyView()`
- ViewModel after `onCleared()`

### How LeakCanary Works

```
1. Object destroyed (Activity.onDestroy)
         |
         v
2. LeakCanary saves weak reference
         |
         v
3. Waits 5 seconds + GC
         |
         v
4. Checks: is object still alive?
         |
    Yes  |   No
    v    |    v
5. Dump heap    OK
         |
         v
6. Analysis + notification
```

### Common Leaks and Fixes

#### 1. Static Reference to Context

```kotlin
// BAD -- Activity leak
object Analytics {
    private lateinit var context: Context

    fun init(context: Context) {
        this.context = context // Activity will leak!
    }
}

// GOOD -- use Application context
object Analytics {
    private lateinit var appContext: Context

    fun init(context: Context) {
        this.appContext = context.applicationContext
    }
}
```

#### 2. Inner Class Holding Activity Reference

```kotlin
// BAD -- inner class holds Activity reference
class MyActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            // This Runnable holds implicit reference to Activity
            updateUI()
        }, 60_000) // 60 seconds
    }

    // Activity destroyed, but Runnable still in queue!
}

// GOOD -- clean Handler
class MyActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())
    private val updateRunnable = Runnable { updateUI() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed(updateRunnable, 60_000)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacks(updateRunnable) // Clean up!
    }
}
```

#### 3. Listener Not Unregistered

```kotlin
// BAD -- not unregistering listener
class MyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        LocationManager.addListener(this) // this = Activity
    }
    // Activity destroyed, but LocationManager holds reference!
}

// GOOD -- unregister
class MyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        LocationManager.addListener(this)
    }

    override fun onDestroy() {
        super.onDestroy()
        LocationManager.removeListener(this) // Unregister!
    }
}
```

#### 4. View Binding in Fragment

```kotlin
// BAD -- binding outlives view
class MyFragment : Fragment() {

    private lateinit var binding: FragmentMyBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }
    // binding holds view reference after onDestroyView!
}

// GOOD -- nullify binding
class MyFragment : Fragment() {

    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Nullify!
    }
}
```

### Memory Profiler in Android Studio

```
View -> Tool Windows -> Profiler -> Memory

Features:
1. Live Allocations -- real-time allocation tracking
2. Heap Dump -- snapshot of all objects in memory
3. Record Allocations -- record allocations over a period
```

### Heap Dump Analysis

```kotlin
// Analysis steps:
// 1. Perform action (open/close Activity)
// 2. Click "Force GC" several times
// 3. Click "Dump Java Heap"
// 4. In heap dump look for:
//    - Activity by class name
//    - "Retained Size" -- how much memory object holds
//    - "References" -- who holds the reference
```

### Programmatic Heap Dump

```kotlin
class DebugUtils {

    fun dumpHeap(context: Context) {
        val heapFile = File(context.cacheDir, "heap_${System.currentTimeMillis()}.hprof")
        Debug.dumpHprofData(heapFile.absolutePath)
        Log.d("Memory", "Heap dumped to: ${heapFile.absolutePath}")
    }

    fun logMemoryInfo() {
        val runtime = Runtime.getRuntime()
        val usedMemory = (runtime.totalMemory() - runtime.freeMemory()) / 1024 / 1024
        val maxMemory = runtime.maxMemory() / 1024 / 1024

        Log.d("Memory", "Used: ${usedMemory}MB / Max: ${maxMemory}MB")
    }
}
```

### LeakCanary Customization

```kotlin
// Watch custom objects
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Watch custom objects
        val watcher = AppWatcher.objectWatcher
        watcher.expectWeaklyReachable(
            myObject,
            "MyObject should be GC'd after close()"
        )
    }
}

// Ignore known library leaks
class IgnoreKnownLeaks : LeakCanary.Config {
    override val referenceMatchers: List<ReferenceMatcher>
        get() = AndroidReferenceMatchers.appDefaults +
            AndroidReferenceMatchers.instanceFieldLeak(
                "com.thirdparty.Lib",
                "leakyField"
            )
}
```

### Leak Prevention Checklist

| Context | Rule |
|---------|------|
| Singleton | Only `applicationContext` |
| Handler | Clean in `onDestroy()` |
| Listener | Unregister in `onDestroy()` |
| View Binding | Nullify in `onDestroyView()` |
| Coroutines | Use `lifecycleScope` |
| Anonymous class | Avoid long-running tasks |

---

## Ссылки (RU)

- [LeakCanary](https://square.github.io/leakcanary/)
- [Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [Manage Memory](https://developer.android.com/topic/performance/memory)

## References (EN)

- [LeakCanary](https://square.github.io/leakcanary/)
- [Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [Manage Memory](https://developer.android.com/topic/performance/memory)

## Follow-ups (EN)

- How does LeakCanary detect leaks without affecting production?
- What is the difference between shallow and retained size?
- How to analyze native memory leaks?
- How do coroutines affect memory management?

## Дополнительные Вопросы (RU)

- Как LeakCanary обнаруживает утечки, не влияя на production?
- В чём разница между shallow и retained size?
- Как анализировать утечки нативной памяти?
- Как корутины влияют на управление памятью?
