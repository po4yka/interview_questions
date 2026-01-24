---
id: android-045
title: Memory Leak Detection and Fixing / Обнаружение и исправление утечек памяти
aliases:
- LeakCanary
- Memory Leak Detection
- Memory Profiler
- Обнаружение утечек памяти
topic: android
subtopics:
- lifecycle
- performance-memory
- profiling
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
sources:
- Memory management best practices
status: draft
moc: moc-android
related:
- q-app-startup-optimization--android--medium
- q-baseline-profiles-optimization--android--medium
- q-jank-detection-frame-metrics--android--medium
created: 2025-10-11
updated: 2025-11-10
tags:
- android/lifecycle
- android/performance-memory
- android/profiling
- difficulty/medium
anki_cards:
- slug: android-045-0-en
  language: en
  anki_id: 1768380210378
  synced_at: '2026-01-23T16:45:05.859860'
- slug: android-045-0-ru
  language: ru
  anki_id: 1768380210401
  synced_at: '2026-01-23T16:45:05.862176'
---
# Вопрос (RU)
> Как обнаружить и исправить утечки памяти в Android? Используйте LeakCanary, Memory Profiler и дампы кучи (heap dumps). Исправьте утечки `Activity`/`Fragment`/`ViewModel`.

# Question (EN)
> How to identify and fix memory leaks in Android? Use LeakCanary, Memory Profiler, and heap dumps. Fix `Activity`/`Fragment`/`ViewModel` leaks.

---

## Ответ (RU)

### Обзор

**Утечка памяти** — объект сохраняет ссылки после того, как перестал быть нужным, блокируя сборку мусора.

**Последствия:**
- OutOfMemoryError сбои
- Частые паузы GC
- Разряд батареи
- Замедление приложения

**Инструменты:**
- **LeakCanary** — автоматическое обнаружение удерживаемых объектов и цепочек удержания `Activity`/`Fragment`/`View`
- **Memory Profiler** — мониторинг в реальном времени и анализ распределения
- **MAT** — анализ дампов кучи (heap dumps)

### LeakCanary — Интеграция

**app/build.gradle.kts:**
```kotlin
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
```

В типичной настройке дополнительная инициализация не требуется — LeakCanary автоматически интегрируется через `ContentProvider` и отслеживает удерживаемые `Activity`/`Fragment`/`View`.

**Кастомная конфигурация (опционально в `Application`):**
```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        if (LeakCanary.isInstalled) {
            LeakCanary.config = LeakCanary.config.copy(
                retainedVisibleThreshold = 5,
                onHeapAnalyzedListener = OnHeapAnalyzedListener { analysis ->
                    if (analysis is HeapAnalysisSuccess) {
                        analysis.applicationLeaks.forEach { leak ->
                            // Отправлять такие данные во внешние сервисы обычно не нужно;
                            // пример только для демонстрации интеграции.
                            Log.d("LeakCanary", leak.leakTrace.toString())
                        }
                    }
                }
            )
        }
    }
}
```

**Отслеживание кастомных объектов:**
```kotlin
class MyRepository {
    fun close() {
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyRepository instance should be GC'ed after close()"
        )
    }
}
```

### Типичные Утечки

#### 1. `Activity` — Статические Ссылки

**❌ Утечка:**
```kotlin
class MainActivity : AppCompatActivity() {
    companion object {
        private var instance: MainActivity? = null  // Утечка
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // Activity никогда не освободится
    }
}
```

**✅ Исправление (для демонстрации):**
```kotlin
class MainActivity : AppCompatActivity() {
    companion object {
        // В реальном коде лучше вообще избегать глобального доступа к Activity.
        private var instanceRef: WeakReference<MainActivity>? = null

        fun getInstance(): MainActivity? = instanceRef?.get()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instanceRef = WeakReference(this)
    }
}
```

Основной вывод: не храните `Activity`/`Fragment` в статических полях и синглтонах.

#### 2. `Activity` — Отложенные Задачи / Внутренние Классы

**❌ Утечка:**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val runnable = object : Runnable {
            override fun run() {
                Toast.makeText(this@MainActivity, "Hello", Toast.LENGTH_SHORT).show()
            }
        }

        Handler(Looper.getMainLooper()).postDelayed(runnable, 60_000)
        // Если Activity уничтожена раньше выполнения, Runnable продолжает удерживать ссылку.
    }
}
```

**✅ Исправление:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed(MyRunnable(this), 60_000)
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        super.onDestroy()
    }

    private class MyRunnable(activity: MainActivity) : Runnable {
        private val activityRef = WeakReference(activity)

        override fun run() {
            activityRef.get()?.let { activity ->
                if (!activity.isFinishing && !activity.isDestroyed) {
                    Toast.makeText(activity, "Hello", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
```

#### 3. `Activity` — Слушатели

**❌ Утечка:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {}
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val locationManager = getSystemService(LOCATION_SERVICE) as LocationManager
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 10f, locationListener
        )
        // Не отменяется в onDestroy -> Activity удерживается системой.
    }
}
```

**✅ Исправление:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val locationManager by lazy {
        getSystemService(LOCATION_SERVICE) as LocationManager
    }

    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {}
    }

    override fun onResume() {
        super.onResume()
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 10f, locationListener
        )
    }

    override fun onPause() {
        locationManager.removeUpdates(locationListener)
        super.onPause()
    }
}
```

#### 4. `Fragment` — Ссылки На `View`

**❌ Утечка:**
```kotlin
class MyFragment : Fragment() {
    private lateinit var textView: TextView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_my, container, false)
        textView = view.findViewById(R.id.text_view)
        return view
    }
    // textView ссылается на View дольше, чем живет view lifecycle.
}
```

**✅ Исправление:**
```kotlin
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
        _binding = null  // Освобождаем ссылки на View
        super.onDestroyView()
    }
}
```

#### 5. `ViewModel` — `Context`

**❌ Утечка:**
```kotlin
class MyViewModel(private val context: Context) : ViewModel() {
    // Если context — Activity, утечка при повороте.
}

class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel> {
        MyViewModelFactory(this)  // Передаем Activity context
    }
}
```

**✅ Исправление:**
```kotlin
class MyViewModel(application: Application) : AndroidViewModel(application) {
    private val appContext: Context = application

    fun getDatabase() = MyDatabase.getInstance(appContext)
}

class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()  // AndroidViewModel поддерживается дефолтной фабрикой
}
```

Ключ: храните только `Application` `Context` в долгоживущих компонентах (`ViewModel`, синглтоны).

#### 6. `LiveData` — observeForever

**❌ Утечка:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userData.observeForever { user ->
            updateUI(user)
        }
        // Observer не удаляется -> Activity удерживается LiveData.
    }
}
```

**✅ Исправление:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userData.observe(this) { user ->
            updateUI(user)  // Отпишется автоматически по lifecycle.
        }
    }
}
```

#### 7. Coroutines — GlobalScope

**❌ Утечка:**
```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        GlobalScope.launch {
            delay(60_000)
            updateUI()  // Fragment может быть уничтожен, но корутина продолжит ссылаться.
        }
    }
}
```

**✅ Исправление:**
```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            delay(60_000)
            updateUI()  // Отменяется при уничтожении view lifecycle.
        }
    }
}
```

#### 8. Bitmap — Кэши

**❌ Утечка:**
```kotlin
object ImageCache {
    private val cache = mutableMapOf<String, Bitmap>()

    fun putBitmap(key: String, bitmap: Bitmap) {
        cache[key] = bitmap  // Никогда не очищается
    }
}
```

**✅ Исправление:**
```kotlin
object ImageCache {
    private val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
    private val cacheSize = maxMemory / 10

    private val cache = object : LruCache<String, Bitmap>(cacheSize) {
        override fun sizeOf(key: String, bitmap: Bitmap): Int = bitmap.byteCount / 1024
    }

    fun putBitmap(key: String, bitmap: Bitmap) {
        cache.put(key, bitmap)
    }

    fun getBitmap(key: String): Bitmap? = cache.get(key)
}
```

Использование `LruCache` ограничивает память и уменьшает риск утечек; вручную вызывать `recycle()` обычно не нужно и может быть опасно.

### Memory Profiler

**Мониторинг:**
1. Android Studio → Profiler → Memory
2. Пилообразный график (выделение → GC) — норма
3. Постоянный рост без освобождения — возможная утечка
4. Если после ручного GC объект не уходит — признак утечки

**Анализ дампа кучи (heap dump):**
```text
1. Profile → Memory → Dump Java Heap
2. Отфильтровать по своему пакету → найти Activity/Fragment
3. Проверить Retained Size
4. Если экземпляры остаются после rotation → подозрение на утечку
5. Через References посмотреть цепочку удержания
```

**Программный дамп (отладка):**
```kotlin
fun dumpHeap() {
    val file = File(getExternalFilesDir(null), "heap_${'$'}{System.currentTimeMillis()}.hprof")
    Debug.dumpHprofData(file.absolutePath)
}
```

Использовать аккуратно: операция тяжелая и не для продакшена.

### Лучшие Практики

1. **LeakCanary в debug** — ловите утечки до продакшена
2. **`Lifecycle`-компоненты** — `LiveData`, `ViewModel`, `lifecycleScope` / `viewLifecycleOwner.lifecycleScope`
3. **Не храните сильные ссылки на контекст `Activity`/`Fragment`** в синглтонах и долгоживущих объектах
4. **Отменяйте слушатели и callback-и** в `onDestroy`/`onPause`/`onStop` (в зависимости от кейса)
5. **Очищайте ViewBinding** в `onDestroyView` у `Fragment`
6. **Используйте `Application` context** для синглтонов и репозиториев
7. **Избегайте статических ссылок на `Activity`/`Fragment`/`View`**
8. **Используйте `viewModelScope` вместо `GlobalScope`**
9. **Используйте проверенные библиотеки изображений** (Coil, Glide) вместо ручного управления `Bitmap`-ами
10. **Регулярно профилируйте память** на реальных сценариях

## Answer (EN)

### Overview

A **memory leak** occurs when objects keep references after they are no longer needed, preventing garbage collection.

**Impact:**
- OutOfMemoryError crashes
- Frequent GC pauses
- Battery drain
- App slowness

**Tools:**
- **LeakCanary** — automatic detection of retained objects and leak traces for `Activity`/`Fragment`/`View`
- **Memory Profiler** — real-time memory monitoring and allocation analysis
- **MAT** — heap dump analysis

### LeakCanary Integration

**app/build.gradle.kts:**
```kotlin
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
```

In a typical setup, no explicit initialization is required — LeakCanary integrates via a `ContentProvider` and automatically tracks retained `Activity`/`Fragment`/`View` instances.

**Optional custom configuration (in `Application`):**
```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        if (LeakCanary.isInstalled) {
            LeakCanary.config = LeakCanary.config.copy(
                retainedVisibleThreshold = 5,
                onHeapAnalyzedListener = OnHeapAnalyzedListener { analysis ->
                    if (analysis is HeapAnalysisSuccess) {
                        analysis.applicationLeaks.forEach { leak ->
                            // Sending traces to external services is usually unnecessary;
                            // this is just to demonstrate integration.
                            Log.d("LeakCanary", leak.leakTrace.toString())
                        }
                    }
                }
            )
        }
    }
}
```

**Watch custom objects:**
```kotlin
class MyRepository {
    fun close() {
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyRepository instance should be GC'ed after close()"
        )
    }
}
```

### Common Leak Patterns

#### 1. `Activity` — Static References

**❌ Leak:**
```kotlin
class MainActivity : AppCompatActivity() {
    companion object {
        private var instance: MainActivity? = null  // Leak
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // Activity never collected
    }
}
```

**✅ Fix (for demonstration):**
```kotlin
class MainActivity : AppCompatActivity() {
    companion object {
        // In real code, avoid global access to Activity altogether.
        private var instanceRef: WeakReference<MainActivity>? = null

        fun getInstance(): MainActivity? = instanceRef?.get()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instanceRef = WeakReference(this)
    }
}
```

Key takeaway: do not store `Activity`/`Fragment` in static fields or singletons.

#### 2. `Activity` — Delayed Tasks / Inner Classes

**❌ Leak:**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val runnable = object : Runnable {
            override fun run() {
                Toast.makeText(this@MainActivity, "Hello", Toast.LENGTH_SHORT).show()
            }
        }

        Handler(Looper.getMainLooper()).postDelayed(runnable, 60_000)
        // If Activity is destroyed earlier, Runnable still holds a reference.
    }
}
```

**✅ Fix:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed(MyRunnable(this), 60_000)
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        super.onDestroy()
    }

    private class MyRunnable(activity: MainActivity) : Runnable {
        private val activityRef = WeakReference(activity)

        override fun run() {
            activityRef.get()?.let { activity ->
                if (!activity.isFinishing && !activity.isDestroyed) {
                    Toast.makeText(activity, "Hello", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
```

#### 3. `Activity` — Listeners

**❌ Leak:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {}
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val locationManager = getSystemService(LOCATION_SERVICE) as LocationManager
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 10f, locationListener
        )
        // Not removed in onDestroy -> system can keep a reference to the Activity.
    }
}
```

**✅ Fix:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val locationManager by lazy {
        getSystemService(LOCATION_SERVICE) as LocationManager
    }

    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {}
    }

    override fun onResume() {
        super.onResume()
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 10f, locationListener
        )
    }

    override fun onPause() {
        locationManager.removeUpdates(locationListener)
        super.onPause()
    }
}
```

#### 4. `Fragment` — `View` References

**❌ Leak:**
```kotlin
class MyFragment : Fragment() {
    private lateinit var textView: TextView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_my, container, false)
        textView = view.findViewById(R.id.text_view)
        return view
    }
    // textView outlives the View lifecycle and keeps a reference.
}
```

**✅ Fix:**
```kotlin
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
        _binding = null  // Clear references to View hierarchy
        super.onDestroyView()
    }
}
```

#### 5. `ViewModel` — `Context`

**❌ Leak:**
```kotlin
class MyViewModel(private val context: Context) : ViewModel() {
    // If context is an Activity, it will leak across configuration changes.
}

class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel> {
        MyViewModelFactory(this)  // Passing Activity context
    }
}
```

**✅ Fix:**
```kotlin
class MyViewModel(application: Application) : AndroidViewModel(application) {
    private val appContext: Context = application

    fun getDatabase() = MyDatabase.getInstance(appContext)
}

class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()  // Default factory supports AndroidViewModel
}
```

Key: keep only `Application` `Context` in long-lived components (`ViewModel`, singletons).

#### 6. `LiveData` — observeForever

**❌ Leak:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userData.observeForever { user ->
            updateUI(user)
        }
        // Observer not removed -> LiveData holds a reference to Activity.
    }
}
```

**✅ Fix:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userData.observe(this) { user ->
            updateUI(user)  // Automatically cleared with the lifecycle.
        }
    }
}
```

#### 7. Coroutines — GlobalScope

**❌ Leak:**
```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        GlobalScope.launch {
            delay(60_000)
            updateUI()  // Fragment might be destroyed, but coroutine keeps a reference.
        }
    }
}
```

**✅ Fix:**
```kotlin
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            delay(60_000)
            updateUI()  // Cancelled when the view lifecycle is destroyed.
        }
    }
}
```

#### 8. Bitmap — Caches

**❌ Leak:**
```kotlin
object ImageCache {
    private val cache = mutableMapOf<String, Bitmap>()

    fun putBitmap(key: String, bitmap: Bitmap) {
        cache[key] = bitmap  // Never cleared
    }
}
```

**✅ Fix:**
```kotlin
object ImageCache {
    private val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
    private val cacheSize = maxMemory / 10

    private val cache = object : LruCache<String, Bitmap>(cacheSize) {
        override fun sizeOf(key: String, bitmap: Bitmap): Int = bitmap.byteCount / 1024
    }

    fun putBitmap(key: String, bitmap: Bitmap) {
        cache.put(key, bitmap)
    }

    fun getBitmap(key: String): Bitmap? = cache.get(key)
}
```

Using `LruCache` bounds memory usage and reduces leak risk; manual `recycle()` is normally unnecessary and can be unsafe.

### Memory Profiler

**Monitoring:**
1. Android Studio → Profiler → Memory
2. Sawtooth pattern (allocations → GC) is normal
3. Continuous growth without drops suggests a leak
4. If objects remain after a forced GC, it indicates potential leaks

**Heap dump analysis:**
```text
1. Profile → Memory → Dump Java Heap
2. Filter/arrange by your package → find Activity/Fragment
3. Inspect Retained Size
4. If instances remain after rotation → suspect a leak
5. Use References to inspect the retention path
```

**Programmatic dump (debug only):**
```kotlin
fun dumpHeap() {
    val file = File(getExternalFilesDir(null), "heap_${'$'}{System.currentTimeMillis()}.hprof")
    Debug.dumpHprofData(file.absolutePath)
}
```

Use with care: this is expensive and not for normal production use.

### Best Practices

1. **Use LeakCanary in debug builds** — catch leaks before production
2. **Use lifecycle-aware components** — `LiveData`, `ViewModel`, `lifecycleScope` / `viewLifecycleOwner.lifecycleScope`
3. **Avoid strong references to `Activity`/`Fragment` `Context`** in singletons and long-lived objects
4. **Unregister listeners and callbacks** in appropriate lifecycle methods (`onDestroy`/`onPause`/`onStop`)
5. **Clear ViewBinding** in `Fragment.onDestroyView`
6. **Use `Application` `Context`** for singletons and repositories
7. **Avoid static references to `Activity`/`Fragment`/`View`**
8. **Prefer `viewModelScope` over `GlobalScope`**
9. **Use mature image libraries** (Coil, Glide) instead of manual `Bitmap` management
10. **Profile memory regularly** with real-world scenarios

---

## Дополнительные Вопросы (RU)

- Как обнаруживать утечки в продакшн-сборках?
- В чем разница между дампом кучи (heap dump) и отслеживанием выделений (allocation tracking)?
- Как анализировать отчеты MAT для сложных цепочек утечек?
- Может ли ViewBinding вызывать утечки, если его не очищать?
- Как автоматизировать проверку на утечки в тестах?

## Follow-ups

- How to detect leaks in production builds?
- What is the difference between heap dump and allocation tracking?
- How to analyze MAT reports for complex leak chains?
- Can ViewBinding cause leaks if not cleared?
- How to test for leaks in automated tests?

## Ссылки (RU)

- Документация LeakCanary: https://square.github.io/leakcanary/
- Руководство по Memory Profiler: https://developer.android.com/studio/profile/memory-profiler
- Обзор управления памятью в Android: https://developer.android.com/topic/performance/memory

## References

- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Memory Profiler Guide](https://developer.android.com/studio/profile/memory-profiler)
- [Android Memory Management](https://developer.android.com/topic/performance/memory)

## Связанные Вопросы (RU)

### Базовые (проще)
- [[q-recyclerview-sethasfixedsize--android--easy]]

### Смежные (средний уровень)
- [[q-jank-detection-frame-metrics--android--medium]]
- [[q-app-startup-optimization--android--medium]]
- [[q-baseline-profiles-optimization--android--medium]]

### Продвинутые (сложнее)
- [[q-compose-performance-optimization--android--hard]]

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]]

### Related (Medium)
- [[q-jank-detection-frame-metrics--android--medium]]
- [[q-app-startup-optimization--android--medium]]
- [[q-baseline-profiles-optimization--android--medium]]

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]]
