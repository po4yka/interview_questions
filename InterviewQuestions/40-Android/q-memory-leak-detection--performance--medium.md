---
id: 20251011-220002
title: "Memory Leak Detection and Fixing / Обнаружение и исправление утечек памяти"
aliases: []

# Classification
topic: android
subtopics:
  - performance
  - memory-leaks
  - profiling
  - leakcanary
  - optimization
question_kind: practical
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/performance, android/memory-leaks, android/profiling, android/leakcanary, android/optimization, android/lifecycle, difficulty/medium]
source: Original
source_note: Memory management best practices

# Workflow & relations
status: draft
moc: moc-android
related: [app-startup-optimization, jank-detection-frame-metrics, baseline-profiles-optimization]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [en, ru, android/performance, android/memory-leaks, android/profiling, android/leakcanary, android/optimization, android/lifecycle, difficulty/medium]
---
# Question (EN)
> Identify and fix common memory leaks in Android. Use LeakCanary, Memory Profiler, and heap dumps for systematic analysis. Fix Activity/Fragment/ViewModel leaks.

# Вопрос (RU)
> Выявите и исправьте распространенные утечки памяти в Android. Используйте LeakCanary, Memory Profiler и дампы кучи для систематического анализа. Исправьте утечки Activity/Fragment/ViewModel.

---

## Answer (EN)

### Overview

A **memory leak** occurs when an object that is no longer needed is still referenced, preventing garbage collection. In Android, leaks commonly involve Activities, Fragments, and ViewModels that remain in memory after they should be destroyed.

**Impact:**
- Increased memory usage (OutOfMemoryError crashes)
- Performance degradation (more frequent GC pauses)
- Battery drain (keeping large objects alive)
- Poor user experience (app slowness, crashes)

**Detection Tools:**
- **LeakCanary**: Automatic leak detection during development
- **Memory Profiler**: Real-time memory monitoring and heap dumps
- **Android Studio Profiler**: Live memory allocation tracking
- **MAT (Memory Analyzer Tool)**: Advanced heap dump analysis

### LeakCanary Integration

#### 1. Setup

**app/build.gradle.kts:**
```kotlin
dependencies {
    // LeakCanary - automatic memory leak detection
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")

    // Optional: customize leak detection
    debugImplementation("com.squareup.leakcanary:plumber-android:2.12")
}
```

**No code changes required!** LeakCanary automatically initializes via ContentProvider and monitors Activity/Fragment/ViewModel leaks.

#### 2. Custom Leak Detection

**MyApplication.kt:**
```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        configureLeakCanary()
    }

    private fun configureLeakCanary() {
        LeakCanary.config = LeakCanary.config.copy(
            // Retain heap dumps for analysis
            retainedVisibleThreshold = 5,

            // Watch custom objects for leaks
            objectInspectors = LeakCanary.config.objectInspectors + listOf(
                CustomObjectInspector()
            ),

            // Custom leak detection rules
            leakingObjectFinder = FilteringLeakingObjectFinder(
                AndroidObjectInspectors.appLeakingObjectFilters
            ),

            // Upload leaks to backend
            onHeapAnalyzedListener = OnHeapAnalyzedListener { heapAnalysis ->
                when (heapAnalysis) {
                    is HeapAnalysisSuccess -> {
                        // Log or upload leaks
                        heapAnalysis.applicationLeaks.forEach { leak ->
                            Log.e("LeakCanary", "Leak detected: ${leak.className}")
                            // Upload to crash reporting
                            Firebase.crashlytics.recordException(
                                LeakException(leak.leakTrace.toString())
                            )
                        }
                    }
                    is HeapAnalysisFailure -> {
                        Log.e("LeakCanary", "Analysis failed: ${heapAnalysis.exception}")
                    }
                }
            }
        )
    }
}

class CustomObjectInspector : ObjectInspector {
    override fun inspect(reporter: ObjectReporter) {
        reporter.whenInstanceOf("com.example.MyCustomCache") { instance ->
            val size = instance["size"]?.value?.asInt ?: 0
            reporter.labels += "Cache size: $size items"

            if (size > 1000) {
                reporter.leakingReasons += "Cache size exceeds threshold: $size > 1000"
            }
        }
    }
}
```

#### 3. Watch Custom Objects

```kotlin
class MyRepository(private val context: Context) {

    private val cache = mutableMapOf<String, Any>()

    init {
        // Watch this repository for leaks
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyRepository instance"
        )
    }

    fun cleanup() {
        cache.clear()
        // Signal that this object is no longer needed
        AppWatcher.objectWatcher.expectWeaklyReachable(
            watchedObject = this,
            description = "MyRepository cleanup called"
        )
    }
}
```

### Common Memory Leak Patterns

#### 1. Activity Leaks - Static References

** LEAK: Static reference to Activity**
```kotlin
class MainActivity : AppCompatActivity() {

    companion object {
        // LEAK: Static reference prevents GC
        private var instance: MainActivity? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // LEAK: Activity can never be GC'd
    }
}

// Leak chain:
// MainActivity class → static instance field → MainActivity instance → Context
```

** FIX: Use Application Context or WeakReference**
```kotlin
class MainActivity : AppCompatActivity() {

    companion object {
        // Option 1: Store Application context instead
        private var appContext: Context? = null

        // Option 2: Use WeakReference
        private var instanceRef: WeakReference<MainActivity>? = null

        fun getInstance(): MainActivity? = instanceRef?.get()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        appContext = applicationContext  // Safe: Application outlives Activity
        instanceRef = WeakReference(this)  // Safe: Can be GC'd
    }
}
```

#### 2. Activity Leaks - Inner Classes

** LEAK: Non-static inner class holds Activity reference**
```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // LEAK: Inner class holds implicit reference to Activity
        val runnable = object : Runnable {
            override fun run() {
                // This closure captures 'this@MainActivity'
                Toast.makeText(this@MainActivity, "Hello", Toast.LENGTH_SHORT).show()
            }
        }

        // LEAK: Handler with delayed message keeps Activity alive
        Handler(Looper.getMainLooper()).postDelayed(runnable, 60_000)
    }
}

// Leak chain:
// Handler → MessageQueue → Message → Runnable → MainActivity instance
```

** FIX: Static inner class with WeakReference**
```kotlin
class MainActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed(
            MyRunnable(this),
            60_000
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        // Clean up pending messages
        handler.removeCallbacksAndMessages(null)
    }

    // Static class doesn't hold implicit reference to outer class
    private class MyRunnable(activity: MainActivity) : Runnable {
        private val activityRef = WeakReference(activity)

        override fun run() {
            val activity = activityRef.get()
            if (activity != null && !activity.isFinishing) {
                Toast.makeText(activity, "Hello", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
```

#### 3. Activity Leaks - Listeners and Callbacks

** LEAK: Listener not unregistered**
```kotlin
class MainActivity : AppCompatActivity() {

    private val locationManager by lazy {
        getSystemService(Context.LOCATION_SERVICE) as LocationManager
    }

    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            // Use location
        }
        // Other methods...
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // LEAK: Listener holds reference to Activity
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            1000L,
            10f,
            locationListener
        )
        // Missing: removeUpdates in onDestroy()
    }
}

// Leak chain:
// LocationManager (system service) → LocationListener → MainActivity
```

** FIX: Unregister listeners in lifecycle callbacks**
```kotlin
class MainActivity : AppCompatActivity() {

    private val locationManager by lazy {
        getSystemService(Context.LOCATION_SERVICE) as LocationManager
    }

    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            // Use location
        }
        // Other methods...
    }

    override fun onResume() {
        super.onResume()
        // Register listener
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            1000L,
            10f,
            locationListener
        )
    }

    override fun onPause() {
        super.onPause()
        // Unregister listener to prevent leak
        locationManager.removeUpdates(locationListener)
    }
}

// Better: Use lifecycle-aware components
class MainActivity : AppCompatActivity() {

    private val locationObserver = lifecycle.addObserver(object : DefaultLifecycleObserver {
        override fun onResume(owner: LifecycleOwner) {
            locationManager.requestLocationUpdates(...)
        }

        override fun onPause(owner: LifecycleOwner) {
            locationManager.removeUpdates(locationListener)
        }
    })
}
```

#### 4. Fragment Leaks - View References

** LEAK: Fragment holds view references after onDestroyView**
```kotlin
class MyFragment : Fragment() {

    // LEAK: View references not cleared
    private lateinit var textView: TextView
    private lateinit var recyclerView: RecyclerView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_my, container, false)

        textView = view.findViewById(R.id.text_view)
        recyclerView = view.findViewById(R.id.recycler_view)

        return view
    }

    // Missing: clearing view references in onDestroyView()
}

// Leak chain:
// Fragment → TextView/RecyclerView → destroyed View hierarchy
```

** FIX: Clear view references or use ViewBinding**
```kotlin
class MyFragment : Fragment() {

    // Option 1: Nullable lateinit with manual cleanup
    private var textView: TextView? = null
    private var recyclerView: RecyclerView? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_my, container, false)

        textView = view.findViewById(R.id.text_view)
        recyclerView = view.findViewById(R.id.recycler_view)

        return view
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Clear references to prevent leak
        textView = null
        recyclerView = null
    }
}

// Better: Use ViewBinding with automatic cleanup
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

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.textView.text = "Hello"
        binding.recyclerView.adapter = myAdapter
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Clear binding to prevent leak
        _binding = null
    }
}

// Best: Use view binding delegate
class MyFragment : Fragment(R.layout.fragment_my) {

    // Automatically cleaned up
    private val binding by viewBinding(FragmentMyBinding::bind)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.textView.text = "Hello"
    }
}
```

#### 5. ViewModel Leaks - Context References

** LEAK: ViewModel holds Activity context**
```kotlin
class MyViewModel(
    private val context: Context  // LEAK: If this is Activity context
) : ViewModel() {

    private val database = MyDatabase.getInstance(context)

    fun loadData() {
        // Use context
    }
}

// In Activity:
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel> {
        // LEAK: Passing Activity context to ViewModel
        MyViewModelFactory(this)  // 'this' is Activity context
    }
}

// Leak chain:
// ViewModel (survives config change) → Context (Activity) → entire Activity
```

** FIX: Use Application context or AndroidViewModel**
```kotlin
// Option 1: Use Application context
class MyViewModel(
    private val appContext: Context  // Application context is safe
) : ViewModel() {

    private val database = MyDatabase.getInstance(appContext)
}

class MyViewModelFactory(
    private val application: Application
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return MyViewModel(application.applicationContext) as T
    }
}

// In Activity:
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel> {
        MyViewModelFactory(application)  // Safe: Application context
    }
}

// Option 2: Use AndroidViewModel (has Application built-in)
class MyViewModel(application: Application) : AndroidViewModel(application) {

    private val database = MyDatabase.getInstance(application)

    fun getContext(): Context = getApplication()
}

// In Activity:
class MainActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()  // No factory needed
}
```

#### 6. ViewModel Leaks - LiveData Observers

** LEAK: Forever observer not removed**
```kotlin
class MainActivity : AppCompatActivity() {

    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // LEAK: observeForever not removed
        viewModel.userData.observeForever { user ->
            updateUI(user)
        }
    }
}

// Leak chain:
// LiveData → Observer → Activity
```

** FIX: Use lifecycle-aware observe or remove observer**
```kotlin
class MainActivity : AppCompatActivity() {

    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Option 1: Lifecycle-aware observer (automatic cleanup)
        viewModel.userData.observe(this) { user ->
            updateUI(user)
        }

        // Option 2: Manual observeForever with cleanup
        val observer = Observer<User> { user ->
            updateUI(user)
        }
        viewModel.userData.observeForever(observer)

        // Clean up when activity is destroyed
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onDestroy(owner: LifecycleOwner) {
                viewModel.userData.removeObserver(observer)
            }
        })
    }
}
```

#### 7. Coroutine Leaks - Unscoped Launches

** LEAK: GlobalScope keeps references alive**
```kotlin
class MyFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // LEAK: GlobalScope doesn't cancel when Fragment is destroyed
        GlobalScope.launch {
            delay(60_000)
            // Fragment might be destroyed, but coroutine still holds reference
            updateUI()
        }
    }

    private fun updateUI() {
        // Access view - crash if Fragment is destroyed
        binding.textView.text = "Updated"
    }
}
```

** FIX: Use lifecycle scopes**
```kotlin
class MyFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Automatically cancelled when viewLifecycleOwner is destroyed
        viewLifecycleOwner.lifecycleScope.launch {
            delay(60_000)
            // Safe: coroutine is cancelled if Fragment is destroyed
            updateUI()
        }
    }

    private fun updateUI() {
        binding.textView.text = "Updated"
    }
}

// In ViewModel:
class MyViewModel : ViewModel() {

    fun loadData() {
        // Automatically cancelled when ViewModel is cleared
        viewModelScope.launch {
            val data = repository.fetchData()
            _dataState.value = data
        }
    }
}
```

#### 8. Bitmap and Large Object Leaks

** LEAK: Bitmaps not recycled**
```kotlin
class ImageCache {
    companion object {
        // LEAK: Large bitmaps held in static map
        private val cache = mutableMapOf<String, Bitmap>()

        fun putBitmap(key: String, bitmap: Bitmap) {
            cache[key] = bitmap  // Never cleared
        }

        fun getBitmap(key: String): Bitmap? = cache[key]
    }
}
```

** FIX: Use LruCache with size limit**
```kotlin
class ImageCache {
    companion object {
        // Calculate max cache size (10% of available memory)
        private val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
        private val cacheSize = maxMemory / 10

        private val bitmapCache = object : LruCache<String, Bitmap>(cacheSize) {
            override fun sizeOf(key: String, bitmap: Bitmap): Int {
                // Size in KB
                return bitmap.byteCount / 1024
            }

            override fun entryRemoved(
                evicted: Boolean,
                key: String,
                oldValue: Bitmap,
                newValue: Bitmap?
            ) {
                // Recycle bitmap when evicted
                if (evicted) {
                    oldValue.recycle()
                }
            }
        }

        fun putBitmap(key: String, bitmap: Bitmap) {
            bitmapCache.put(key, bitmap)
        }

        fun getBitmap(key: String): Bitmap? = bitmapCache.get(key)

        fun clear() {
            bitmapCache.evictAll()
        }
    }
}

// Better: Use modern image loading libraries
class MyFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Coil handles caching and memory management automatically
        binding.imageView.load("https://example.com/image.jpg") {
            crossfade(true)
            placeholder(R.drawable.placeholder)
        }
    }
}
```

### Memory Profiler Analysis

#### 1. Live Memory Monitoring

**Steps:**
```
1. Open Android Studio
2. Run app on device/emulator
3. View → Tool Windows → Profiler
4. Click on app process
5. Memory timeline shows real-time allocation
```

**Monitor for:**
- **Gradual increase**: Potential leak (memory not released)
- **Sawtooth pattern**: Normal (allocate → GC → allocate)
- **Sudden spikes**: Large object allocation
- **No decrease after GC**: Definite leak

#### 2. Heap Dump Analysis

**MainActivity.kt (trigger leak):**
```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<Button>(R.id.btn_create_leak).setOnClickListener {
            // Create intentional leak for testing
            LeakyRepository.instance = LeakyRepository(this)
        }

        findViewById<Button>(R.id.btn_trigger_gc).setOnClickListener {
            // Force GC to see if objects are released
            Runtime.getRuntime().gc()
            System.runFinalization()
        }

        findViewById<Button>(R.id.btn_dump_heap).setOnClickListener {
            // Dump heap for analysis
            dumpHeap()
        }
    }

    private fun dumpHeap() {
        try {
            val heapDumpFile = File(
                getExternalFilesDir(null),
                "memory_${System.currentTimeMillis()}.hprof"
            )
            Debug.dumpHprofData(heapDumpFile.absolutePath)
            Toast.makeText(this, "Heap dumped: ${heapDumpFile.name}", Toast.LENGTH_SHORT).show()
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }
}

object LeakyRepository {
    // LEAK: Holds Activity reference
    var instance: LeakyRepository? = null
}

class LeakyRepository(private val context: Context) {
    // This reference prevents Activity from being GC'd
}
```

**Analyzing Heap Dump:**
```
1. Profile → Memory → Dump Java Heap
2. Wait for dump to complete
3. Heap dump opens in editor
4. Click "Arrange by package"
5. Find your Activity class
6. Check "Retained Size" column
7. If Activity instance exists after rotation/back press → LEAK
8. Right-click instance → "Jump to Source"
9. View "References" tab to see leak chain
```

#### 3. Allocation Tracker

**Track where objects are created:**
```
1. Profiler → Memory → Record allocations
2. Perform actions in app (navigate, rotate, etc.)
3. Stop recording
4. View allocations by class
5. Sort by count/size
6. Identify unexpected allocations
```

**Example findings:**
```
Class: MainActivity
Allocations: 15 instances
Size: 2.4 MB total

Expected: 1 instance
Issue: 14 leaked instances from rotations

Leak chain:
LeakyRepository.instance → MainActivity → Context → entire Activity tree
```

### Advanced Leak Detection

#### 1. Custom LeakCanary Rules

**MyLeakCanaryConfig.kt:**
```kotlin
object MyLeakCanaryConfig {

    fun configure() {
        LeakCanary.config = LeakCanary.config.copy(
            // Custom filtering
            leakingObjectFinder = FilteringLeakingObjectFinder(
                AndroidObjectInspectors.appLeakingObjectFilters +
                    listOf(
                        // Ignore specific library leaks
                        { heapObject ->
                            heapObject.asClass?.name?.startsWith("com.some.library") == true
                        },
                        // Custom leak detection
                        { heapObject ->
                            val instance = heapObject.asInstance ?: return@listOf false
                            instance["isLeaked"]?.value?.asBoolean == true
                        }
                    )
            ),

            // Track more objects
            maxStoredHeapDumps = 10,
            dumpHeap = true,
            dumpHeapWhenDebugging = true
        )
    }
}
```

#### 2. Production Leak Reporting

**LeakUploader.kt:**
```kotlin
class LeakUploader {

    fun uploadLeakTrace(leak: ApplicationLeak) {
        val leakInfo = LeakInfo(
            className = leak.className,
            leakTrace = leak.leakTraces.first().toString(),
            retainedSize = leak.leakTraces.first().retainedHeapByteSize ?: 0,
            timestamp = System.currentTimeMillis(),
            deviceInfo = getDeviceInfo(),
            appVersion = BuildConfig.VERSION_NAME
        )

        // Upload to backend
        analyticsService.logEvent("memory_leak_detected", leakInfo.toBundle())

        // Or use Firebase Crashlytics
        Firebase.crashlytics.apply {
            setCustomKey("leak_class", leakInfo.className)
            setCustomKey("retained_size", leakInfo.retainedSize)
            recordException(MemoryLeakException(leakInfo.leakTrace))
        }
    }

    private fun getDeviceInfo(): DeviceInfo {
        return DeviceInfo(
            manufacturer = Build.MANUFACTURER,
            model = Build.MODEL,
            sdkVersion = Build.VERSION.SDK_INT,
            availableMemory = getAvailableMemory()
        )
    }

    private fun getAvailableMemory(): Long {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val memInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memInfo)
        return memInfo.availMem
    }
}

class MemoryLeakException(leakTrace: String) : Exception("Memory leak detected:\n$leakTrace")
```

### Best Practices

1. **Use LeakCanary in Debug Builds**: Catch leaks during development before they reach production
2. **Lifecycle-Aware Components**: Use LiveData, ViewModel, lifecycle scopes to avoid manual cleanup
3. **Weak References for Caches**: Use WeakReference or LruCache for caching to allow GC
4. **Unregister Listeners**: Always unregister broadcast receivers, location listeners, etc.
5. **Clear View References in Fragments**: Set binding to null in onDestroyView()
6. **Use Application Context**: For long-lived objects, use Application context not Activity
7. **Avoid Static Activity References**: Never store Activity in static fields
8. **Cancel Coroutines**: Use viewModelScope, lifecycleScope, not GlobalScope
9. **Recycle Bitmaps**: Use image libraries (Coil, Glide) that handle memory automatically
10. **Profile Regularly**: Run Memory Profiler and heap dumps periodically during development
11. **Test Configuration Changes**: Rotate device multiple times and check for duplicate instances
12. **Monitor Production**: Set up leak reporting to catch issues in the wild

### Common Pitfalls

1. **Ignoring LeakCanary Warnings**: Every leak reported should be investigated and fixed
2. **Using Activity Context Everywhere**: Default to Application context for singletons
3. **Forgetting to Clear ViewBinding**: Common Fragment leak source
4. **Anonymous Inner Classes**: Implicitly hold reference to outer class
5. **GlobalScope Coroutines**: Live forever, preventing cleanup
6. **Static Collections**: Adding objects to static maps/lists without clearing
7. **ObserveForever Without Removal**: LiveData observers must be removed manually
8. **Long-Running AsyncTasks**: Deprecated but still cause leaks in legacy code
9. **Event Bus Not Unregistered**: EventBus, RxJava subscriptions must be cleaned up
10. **Testing Only on Emulator**: Real devices have memory constraints that expose leaks

## Ответ (RU)

### Обзор

**Утечка памяти** возникает, когда объект, который больше не нужен, все еще имеет ссылки, предотвращающие сборку мусора. В Android утечки обычно связаны с Activity, Fragment и ViewModel, которые остаются в памяти после того, как должны быть уничтожены.

**Влияние:**
- Увеличение использования памяти (сбои OutOfMemoryError)
- Ухудшение производительности (более частые паузы GC)
- Разряд батареи (сохранение больших объектов живыми)
- Плохой пользовательский опыт (замедление приложения, сбои)

**Инструменты обнаружения:**
- **LeakCanary**: Автоматическое обнаружение утечек во время разработки
- **Memory Profiler**: Мониторинг памяти в реальном времени и дампы кучи
- **Android Studio Profiler**: Отслеживание выделения памяти в реальном времени
- **MAT (Memory Analyzer Tool)**: Расширенный анализ дампов кучи

[All code examples and sections remain the same as English version...]

### Лучшие практики

1. **Используйте LeakCanary в отладочных сборках**: Отлавливайте утечки во время разработки, прежде чем они попадут в продакшн
2. **Компоненты с учетом жизненного цикла**: Используйте LiveData, ViewModel, lifecycle scopes для избежания ручной очистки
3. **Слабые ссылки для кэшей**: Используйте WeakReference или LruCache для кэширования, чтобы разрешить GC
4. **Отмена регистрации слушателей**: Всегда отменяйте регистрацию broadcast receivers, location listeners и т.д.
5. **Очистка ссылок на View во Fragment**: Устанавливайте binding в null в onDestroyView()
6. **Использование Application Context**: Для долгоживущих объектов используйте Application context, а не Activity
7. **Избегайте статических ссылок на Activity**: Никогда не храните Activity в статических полях
8. **Отмена корутин**: Используйте viewModelScope, lifecycleScope, а не GlobalScope
9. **Переработка Bitmap**: Используйте библиотеки изображений (Coil, Glide), которые автоматически управляют памятью
10. **Регулярное профилирование**: Запускайте Memory Profiler и дампы кучи периодически во время разработки
11. **Тестирование изменений конфигурации**: Поворачивайте устройство несколько раз и проверяйте дублирующиеся экземпляры
12. **Мониторинг продакшна**: Настройте отчеты об утечках для отлова проблем в реальных условиях

### Распространенные ошибки

1. **Игнорирование предупреждений LeakCanary**: Каждая обнаруженная утечка должна быть исследована и исправлена
2. **Использование Activity Context везде**: По умолчанию используйте Application context для синглтонов
3. **Забывание очистки ViewBinding**: Распространенный источник утечек Fragment
4. **Анонимные внутренние классы**: Неявно держат ссылку на внешний класс
5. **GlobalScope корутины**: Живут вечно, предотвращая очистку
6. **Статические коллекции**: Добавление объектов в статические map/list без очистки
7. **ObserveForever без удаления**: Наблюдатели LiveData должны удаляться вручную
8. **Долгоживущие AsyncTask**: Устарели, но все еще вызывают утечки в устаревшем коде
9. **Event Bus не отменен**: Подписки EventBus, RxJava должны быть очищены
10. **Тестирование только на эмуляторе**: Реальные устройства имеют ограничения памяти, которые выявляют утечки

---

## References
- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Memory Management Best Practices](https://developer.android.com/topic/performance/memory)
- [Android Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [Avoiding Memory Leaks](https://developer.android.com/topic/performance/memory-overview)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview
### Related (Medium)
- [[q-jank-detection-frame-metrics--performance--medium]] - Performance
- [[q-macrobenchmark-startup--performance--medium]] - Performance
- [[q-app-startup-optimization--performance--medium]] - Performance
- [[q-baseline-profiles-optimization--performance--medium]] - Performance
### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
