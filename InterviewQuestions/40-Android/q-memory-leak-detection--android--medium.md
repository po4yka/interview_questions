---
id: 20251011-220002
title: "Memory Leak Detection and Fixing / Обнаружение и исправление утечек памяти"
aliases: [Memory Leak Detection, Обнаружение утечек памяти, LeakCanary, Memory Profiler]

# Classification
topic: android
subtopics: [performance-memory, profiling, lifecycle]
question_kind: android
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: [Memory management best practices]

# Workflow & relations
status: draft
moc: moc-android
related: [q-app-startup-optimization--android--medium, q-jank-detection-frame-metrics--android--medium, q-baseline-profiles-optimization--android--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-28

tags: [android/performance-memory, android/profiling, android/lifecycle, difficulty/medium]
---
# Вопрос (RU)
> Как обнаружить и исправить утечки памяти в Android? Используйте LeakCanary, Memory Profiler. Исправьте утечки Activity/Fragment/ViewModel.

# Question (EN)
> How to identify and fix memory leaks in Android? Use LeakCanary, Memory Profiler, and heap dumps. Fix Activity/Fragment/ViewModel leaks.

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
- **LeakCanary** — автоматическое обнаружение
- **Memory Profiler** — мониторинг в реальном времени
- **MAT** — анализ дампов кучи

### LeakCanary — интеграция

**app/build.gradle.kts:**
```kotlin
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
```

Не требует настройки — автоматически отслеживает Activity/Fragment/ViewModel.

**Настройка:**
```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        LeakCanary.config = LeakCanary.config.copy(
            retainedVisibleThreshold = 5,
            onHeapAnalyzedListener = OnHeapAnalyzedListener { analysis ->
                if (analysis is HeapAnalysisSuccess) {
                    analysis.applicationLeaks.forEach { leak ->
                        Firebase.crashlytics.recordException(
                            LeakException(leak.leakTrace.toString())
                        )
                    }
                }
            }
        )
    }
}
```

**Отслеживание кастомных объектов:**
```kotlin
class MyRepository {
    init {
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyRepository instance"
        )
    }
}
```

### Типичные утечки

#### 1. Activity — статические ссылки

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

**✅ Исправление:**
```kotlin
class MainActivity : AppCompatActivity() {
    companion object {
        private var instanceRef: WeakReference<MainActivity>? = null

        fun getInstance(): MainActivity? = instanceRef?.get()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instanceRef = WeakReference(this)
    }
}
```

#### 2. Activity — внутренние классы

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
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }

    private class MyRunnable(activity: MainActivity) : Runnable {
        private val activityRef = WeakReference(activity)

        override fun run() {
            activityRef.get()?.let { activity ->
                if (!activity.isFinishing) {
                    Toast.makeText(activity, "Hello", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
```

#### 3. Activity — слушатели

**❌ Утечка:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {}
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val locationManager = getSystemService<LocationManager>()
        locationManager?.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 10f, locationListener
        )
        // Не отменяется в onDestroy
    }
}
```

**✅ Исправление:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val locationManager by lazy { getSystemService<LocationManager>() }
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {}
    }

    override fun onResume() {
        super.onResume()
        locationManager?.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 10f, locationListener
        )
    }

    override fun onPause() {
        super.onPause()
        locationManager?.removeUpdates(locationListener)
    }
}
```

#### 4. Fragment — ссылки на View

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
    // textView не очищается
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
        super.onDestroyView()
        _binding = null  // Освобождаем ссылки
    }
}
```

#### 5. ViewModel — Context

**❌ Утечка:**
```kotlin
class MyViewModel(private val context: Context) : ViewModel() {
    // Если context — Activity, утечка при повороте
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
    private val viewModel by viewModels<MyViewModel>()
}
```

#### 6. LiveData — observeForever

**❌ Утечка:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userData.observeForever { user ->
            updateUI(user)
        }
        // Observer не удаляется
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
            updateUI(user)  // Автоматически очищается
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
            updateUI()  // Fragment может быть уничтожен
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
            updateUI()  // Автоматически отменяется
        }
    }
}
```

#### 8. Bitmap — кэши

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
        override fun sizeOf(key: String, bitmap: Bitmap) = bitmap.byteCount / 1024

        override fun entryRemoved(
            evicted: Boolean, key: String, old: Bitmap, new: Bitmap?
        ) {
            if (evicted) old.recycle()
        }
    }

    fun putBitmap(key: String, bitmap: Bitmap) = cache.put(key, bitmap)
    fun getBitmap(key: String) = cache.get(key)
}
```

### Memory Profiler

**Мониторинг:**
1. Android Studio → Profiler → Memory
2. Паттерн "пила" — норма (выделение → GC)
3. Постоянный рост — утечка
4. Нет падения после GC — утечка

**Анализ дампа:**
```text
1. Profile → Memory → Dump Java Heap
2. Arrange by package → найти ваш Activity
3. Проверить Retained Size
4. Если экземпляры после rotation → утечка
5. References → увидеть цепочку утечки
```

**Программный дамп:**
```kotlin
fun dumpHeap() {
    val file = File(getExternalFilesDir(null), "heap_${System.currentTimeMillis()}.hprof")
    Debug.dumpHprofData(file.absolutePath)
}
```

### Лучшие практики

1. **LeakCanary в debug** — отлавливайте до продакшна
2. **Lifecycle-компоненты** — LiveData, ViewModel, lifecycleScope
3. **WeakReference** для кэшей
4. **Отменяйте слушатели** в onDestroy/onPause
5. **Очищайте binding** в onDestroyView
6. **Application context** для синглтонов
7. **Избегайте статических Activity ссылок**
8. **viewModelScope, не GlobalScope**
9. **Библиотеки изображений** (Coil, Glide)
10. **Регулярное профилирование**

## Answer (EN)

### Overview

A **memory leak** occurs when objects retain references after no longer needed, preventing garbage collection.

**Impact:**
- OutOfMemoryError crashes
- Frequent GC pauses
- Battery drain
- App slowness

**Tools:**
- **LeakCanary** — automatic detection
- **Memory Profiler** — real-time monitoring
- **MAT** — heap dump analysis

### LeakCanary Integration

**app/build.gradle.kts:**
```kotlin
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
```

No setup required — automatically monitors Activity/Fragment/ViewModel.

**Configuration:**
```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        LeakCanary.config = LeakCanary.config.copy(
            retainedVisibleThreshold = 5,
            onHeapAnalyzedListener = OnHeapAnalyzedListener { analysis ->
                if (analysis is HeapAnalysisSuccess) {
                    analysis.applicationLeaks.forEach { leak ->
                        Firebase.crashlytics.recordException(
                            LeakException(leak.leakTrace.toString())
                        )
                    }
                }
            }
        )
    }
}
```

**Watch custom objects:**
```kotlin
class MyRepository {
    init {
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyRepository instance"
        )
    }
}
```

### Common Leak Patterns

#### 1. Activity — Static References

**❌ Leak:**
```kotlin
class MainActivity : AppCompatActivity() {
    companion object {
        private var instance: MainActivity? = null  // Leak
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // Activity never GC'd
    }
}
```

**✅ Fix:**
```kotlin
class MainActivity : AppCompatActivity() {
    companion object {
        private var instanceRef: WeakReference<MainActivity>? = null

        fun getInstance(): MainActivity? = instanceRef?.get()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instanceRef = WeakReference(this)
    }
}
```

#### 2. Activity — Inner Classes

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
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }

    private class MyRunnable(activity: MainActivity) : Runnable {
        private val activityRef = WeakReference(activity)

        override fun run() {
            activityRef.get()?.let { activity ->
                if (!activity.isFinishing) {
                    Toast.makeText(activity, "Hello", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
```

#### 3. Activity — Listeners

**❌ Leak:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {}
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val locationManager = getSystemService<LocationManager>()
        locationManager?.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 10f, locationListener
        )
        // Not removed in onDestroy
    }
}
```

**✅ Fix:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val locationManager by lazy { getSystemService<LocationManager>() }
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {}
    }

    override fun onResume() {
        super.onResume()
        locationManager?.requestLocationUpdates(
            LocationManager.GPS_PROVIDER, 1000L, 10f, locationListener
        )
    }

    override fun onPause() {
        super.onPause()
        locationManager?.removeUpdates(locationListener)
    }
}
```

#### 4. Fragment — View References

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
    // textView not cleared
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
        super.onDestroyView()
        _binding = null  // Clear references
    }
}
```

#### 5. ViewModel — Context

**❌ Leak:**
```kotlin
class MyViewModel(private val context: Context) : ViewModel() {
    // If context is Activity, leaks on rotation
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
    private val viewModel by viewModels<MyViewModel>()
}
```

#### 6. LiveData — observeForever

**❌ Leak:**
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userData.observeForever { user ->
            updateUI(user)
        }
        // Observer not removed
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
            updateUI(user)  // Auto cleanup
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
            updateUI()  // Fragment might be destroyed
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
            updateUI()  // Auto cancelled
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
        override fun sizeOf(key: String, bitmap: Bitmap) = bitmap.byteCount / 1024

        override fun entryRemoved(
            evicted: Boolean, key: String, old: Bitmap, new: Bitmap?
        ) {
            if (evicted) old.recycle()
        }
    }

    fun putBitmap(key: String, bitmap: Bitmap) = cache.put(key, bitmap)
    fun getBitmap(key: String) = cache.get(key)
}
```

### Memory Profiler

**Monitoring:**
1. Android Studio → Profiler → Memory
2. Sawtooth pattern — normal (allocate → GC)
3. Gradual increase — leak
4. No decrease after GC — leak

**Heap dump analysis:**
```text
1. Profile → Memory → Dump Java Heap
2. Arrange by package → find your Activity
3. Check Retained Size
4. If instances exist after rotation → leak
5. References → view leak chain
```

**Programmatic dump:**
```kotlin
fun dumpHeap() {
    val file = File(getExternalFilesDir(null), "heap_${System.currentTimeMillis()}.hprof")
    Debug.dumpHprofData(file.absolutePath)
}
```

### Best Practices

1. **LeakCanary in debug** — catch before production
2. **Lifecycle components** — LiveData, ViewModel, lifecycleScope
3. **WeakReference** for caches
4. **Unregister listeners** in onDestroy/onPause
5. **Clear binding** in onDestroyView
6. **Application context** for singletons
7. **Avoid static Activity references**
8. **Use viewModelScope, not GlobalScope**
9. **Image libraries** (Coil, Glide)
10. **Regular profiling**

---

## Follow-ups

- How to detect leaks in production builds?
- What is the difference between heap dump and allocation tracking?
- How to analyze MAT reports for complex leak chains?
- Can ViewBinding cause leaks if not cleared?
- How to test for leaks in automated tests?

## References

- [[c-memory-leaks]]
- [[c-memory-management]]
- [[c-lifecycle]]
- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Memory Profiler Guide](https://developer.android.com/studio/profile/memory-profiler)
- [Android Memory Management](https://developer.android.com/topic/performance/memory)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]]

### Related (Medium)
- [[q-jank-detection-frame-metrics--android--medium]]
- [[q-app-startup-optimization--android--medium]]
- [[q-baseline-profiles-optimization--android--medium]]

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]]
