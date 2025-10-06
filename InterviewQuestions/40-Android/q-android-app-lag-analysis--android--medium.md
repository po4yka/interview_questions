# Why Does Android App Lag? Analysis and Solutions

**Сложность**: 🟡 Medium
**Источник**: Amit Shekhar Android Interview Questions

## English

### Question
Why does an Android app lag? How do you identify and fix performance issues causing UI stuttering and slowness?

### Answer

App lag occurs when the UI thread is blocked or frame rendering exceeds 16ms (60 FPS target). Understanding root causes and using proper diagnostic tools is essential for smooth user experience.

#### 1. **Common Causes of App Lag**

**1.1 Main Thread Blocking**

```kotlin
// ❌ BAD: Blocking main thread
class BadViewModel : ViewModel() {
    fun loadData() {
        // This blocks UI thread!
        val data = database.getAllUsers() // Synchronous DB call
        val result = heavyComputation(data)
        updateUI(result)
    }

    private fun heavyComputation(data: List<User>): ProcessedData {
        // Long-running calculation on main thread
        Thread.sleep(2000) // Simulating heavy work
        return ProcessedData()
    }
}

// ✅ GOOD: Async operations
class GoodViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val data = withContext(Dispatchers.IO) {
                    repository.getAllUsers()
                }

                val result = withContext(Dispatchers.Default) {
                    heavyComputation(data)
                }

                _uiState.value = UiState.Success(result)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }
}
```

**1.2 Memory Issues**

```kotlin
// ❌ BAD: Memory leak causing lag
class LeakyActivity : AppCompatActivity() {
    companion object {
        // Static reference keeps Activity alive!
        private var listener: OnDataListener? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        listener = object : OnDataListener {
            override fun onData(data: String) {
                updateUI(data)
            }
        }
    }
}

// ✅ GOOD: Proper lifecycle management
class ProperActivity : AppCompatActivity() {
    private lateinit var viewModel: DataViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.data.collect { data ->
                    updateUI(data)
                }
            }
        }
    }
}
```

**1.3 Overdraw and Complex Layouts**

```kotlin
// ❌ BAD: Deep view hierarchy
<LinearLayout>
    <RelativeLayout>
        <FrameLayout>
            <ConstraintLayout>
                <TextView />
            </ConstraintLayout>
        </FrameLayout>
    </RelativeLayout>
</LinearLayout>

// ✅ GOOD: Flat hierarchy
<ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</ConstraintLayout>

// ✅ BETTER: Compose (no XML overhead)
@Composable
fun OptimizedScreen() {
    Text(
        text = "Hello",
        modifier = Modifier.padding(16.dp)
    )
}
```

#### 2. **Identifying Performance Issues**

**2.1 GPU Overdraw Detection**

```kotlin
// Enable in Developer Options:
// Settings → Developer Options → Debug GPU overdraw → Show overdraw areas

// Colors indicate overdraw levels:
// - True color: No overdraw (1x)
// - Blue: 1x overdraw (2x)
// - Green: 2x overdraw (3x)
// - Light red: 3x overdraw (4x)
// - Dark red: 4x+ overdraw (5x+)

// Fix overdraw:
<LinearLayout
    android:background="@color/white"> <!-- Remove if parent has background -->
    <TextView
        android:background="@android:color/transparent" /> <!-- Remove unnecessary backgrounds -->
</LinearLayout>
```

**2.2 Profile GPU Rendering**

```kotlin
// Enable in Developer Options:
// Settings → Developer Options → Profile GPU Rendering → On screen as bars

// Green line = 16ms target (60 FPS)
// Bars above green line = dropped frames

class PerformanceMonitor(private val activity: Activity) {
    private val frameMetrics = FrameMetrics()

    fun startMonitoring() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            activity.window.addOnFrameMetricsAvailableListener(
                { window, frameMetrics, dropCountSinceLastInvocation ->
                    val totalDurationNs = frameMetrics.getMetric(FrameMetrics.TOTAL_DURATION)
                    val totalDurationMs = totalDurationNs / 1_000_000.0

                    if (totalDurationMs > 16.0) {
                        Log.w("Performance", "Slow frame: ${totalDurationMs}ms")
                        logFrameMetrics(frameMetrics)
                    }
                },
                Handler(Looper.getMainLooper())
            )
        }
    }

    @RequiresApi(Build.VERSION_CODES.N)
    private fun logFrameMetrics(metrics: FrameMetrics) {
        val input = metrics.getMetric(FrameMetrics.INPUT_HANDLING_DURATION) / 1_000_000.0
        val animation = metrics.getMetric(FrameMetrics.ANIMATION_DURATION) / 1_000_000.0
        val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
        val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
        val sync = metrics.getMetric(FrameMetrics.SYNC_DURATION) / 1_000_000.0

        Log.d("FrameMetrics", """
            Input: ${input}ms
            Animation: ${animation}ms
            Layout: ${layout}ms
            Draw: ${draw}ms
            Sync: ${sync}ms
        """.trimIndent())
    }
}
```

**2.3 StrictMode**

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            enableStrictMode()
        }
    }

    private fun enableStrictMode() {
        StrictMode.setThreadPolicy(
            StrictMode.ThreadPolicy.Builder()
                .detectDiskReads()
                .detectDiskWrites()
                .detectNetwork()
                .detectCustomSlowCalls()
                .penaltyLog()
                .penaltyFlashScreen() // Visual indicator
                .build()
        )

        StrictMode.setVmPolicy(
            StrictMode.VmPolicy.Builder()
                .detectLeakedSqlLiteObjects()
                .detectLeakedClosableObjects()
                .detectLeakedRegistrationObjects()
                .detectActivityLeaks()
                .detectFileUriExposure()
                .penaltyLog()
                .build()
        )
    }
}
```

**2.4 Systrace/Perfetto**

```kotlin
// Add custom trace sections
class DataProcessor {
    suspend fun processData(data: List<Item>): ProcessedData {
        return trace("DataProcessor.processData") {
            withContext(Dispatchers.Default) {
                trace("sorting") {
                    data.sortedBy { it.timestamp }
                }

                trace("filtering") {
                    data.filter { it.isValid }
                }

                trace("transformation") {
                    data.map { it.toProcessed() }
                }
            }
        }
    }
}

// Capture trace:
// adb shell perfetto -o /data/misc/perfetto-traces/trace --time 10s sched freq idle am wm gfx view binder_driver hal dalvik camera input res memory
```

#### 3. **Common Solutions**

**3.1 RecyclerView Optimization**

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<ViewHolder>() {

    // Use stable IDs
    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long {
        return items[position].id
    }

    // Use DiffUtil for efficient updates
    fun updateItems(newItems: List<Item>) {
        val diffResult = DiffUtil.calculateDiff(
            ItemDiffCallback(items, newItems),
            false // Don't detect moves for better performance
        )

        items = newItems
        diffResult.dispatchUpdatesTo(this)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // Avoid findViewById with ViewBinding
        val binding = ItemViewBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // Keep onBindViewHolder lightweight
        holder.bind(items[position])
    }

    class ViewHolder(private val binding: ItemViewBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: Item) {
            binding.title.text = item.title

            // Load images asynchronously
            Glide.with(binding.root.context)
                .load(item.imageUrl)
                .placeholder(R.drawable.placeholder)
                .into(binding.image)
        }
    }
}

// Configure RecyclerView
recyclerView.apply {
    // Enable item prefetch
    layoutManager = LinearLayoutManager(context).apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }

    // Set fixed size if content doesn't change RecyclerView size
    setHasFixedSize(true)

    // Recycle view pool for nested RecyclerViews
    recycledViewPool.setMaxRecycledViews(0, 20)

    // Increase cache size
    setItemViewCacheSize(20)
}
```

**3.2 Image Loading Optimization**

```kotlin
// ❌ BAD: Loading large images
imageView.setImageBitmap(BitmapFactory.decodeFile(largeImagePath))

// ✅ GOOD: Proper image loading
class ImageLoader {
    fun loadOptimized(
        imageView: ImageView,
        imagePath: String,
        targetWidth: Int,
        targetHeight: Int
    ) {
        Glide.with(imageView.context)
            .load(imagePath)
            .override(targetWidth, targetHeight)
            .diskCacheStrategy(DiskCacheStrategy.ALL)
            .placeholder(R.drawable.placeholder)
            .error(R.drawable.error)
            .into(imageView)
    }

    // Custom bitmap loading with sampling
    suspend fun loadBitmapOptimized(
        path: String,
        reqWidth: Int,
        reqHeight: Int
    ): Bitmap = withContext(Dispatchers.IO) {
        val options = BitmapFactory.Options().apply {
            inJustDecodeBounds = true
            BitmapFactory.decodeFile(path, this)

            inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
            inJustDecodeBounds = false
        }

        BitmapFactory.decodeFile(path, options)
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
```

**3.3 Lazy Initialization**

```kotlin
class OptimizedActivity : AppCompatActivity() {

    // Lazy initialization
    private val heavyObject by lazy {
        HeavyObject().apply {
            initialize()
        }
    }

    // ViewBinding delegation
    private val binding by viewBinding(ActivityMainBinding::inflate)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(binding.root)

        // Don't initialize heavy objects in onCreate
        // Only initialize when actually needed
        binding.button.setOnClickListener {
            heavyObject.doWork()
        }
    }
}
```

**3.4 Database Optimization**

```kotlin
@Dao
interface UserDao {
    // ❌ BAD: Loading all data at once
    @Query("SELECT * FROM users")
    fun getAllUsers(): List<User>

    // ✅ GOOD: Pagination
    @Query("SELECT * FROM users ORDER BY id LIMIT :limit OFFSET :offset")
    suspend fun getUsersPaged(limit: Int, offset: Int): List<User>

    // ✅ BETTER: PagingSource
    @Query("SELECT * FROM users ORDER BY id")
    fun getUsersPagingSource(): PagingSource<Int, User>

    // Load only needed columns
    @Query("SELECT id, name FROM users")
    suspend fun getUserNamesOnly(): List<UserNameOnly>
}
```

**3.5 Startup Optimization**

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Critical initialization only
        initializeCriticalComponents()

        // Defer non-critical work
        lifecycleScope.launch {
            initializeNonCriticalComponents()
        }
    }

    private fun initializeCriticalComponents() {
        // Crash reporting
        FirebaseCrashlytics.getInstance()

        // Essential libraries only
    }

    private suspend fun initializeNonCriticalComponents() {
        withContext(Dispatchers.IO) {
            // Analytics
            initializeAnalytics()

            // Ad SDKs
            initializeAds()

            // Other non-critical libraries
        }
    }
}

// Use App Startup library for organized initialization
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.initialize(context)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return emptyList()
    }
}
```

#### 4. **Profiling Tools**

**4.1 Android Profiler**

```kotlin
// CPU Profiler: Identify hot methods
// Memory Profiler: Find memory leaks and excessive allocations
// Network Profiler: Analyze network requests
// Energy Profiler: Check battery consumption

// Add custom events
class TrackedOperation {
    fun performOperation() {
        Debug.startMethodTracing("operation")
        try {
            // Do work
            heavyComputation()
        } finally {
            Debug.stopMethodTracing()
        }
    }
}
```

**4.2 LeakCanary**

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}

// Automatically detects memory leaks in debug builds
// No additional code needed
```

### Performance Checklist

**UI Thread:**
- [ ] No disk I/O on main thread
- [ ] No network calls on main thread
- [ ] No heavy computations on main thread
- [ ] Use coroutines/RxJava for async work

**Layouts:**
- [ ] Minimize view hierarchy depth
- [ ] Use ConstraintLayout or Compose
- [ ] Avoid overdraw
- [ ] Use ViewStub for rarely shown views

**Lists:**
- [ ] Use RecyclerView with DiffUtil
- [ ] Enable view recycling
- [ ] Implement pagination
- [ ] Keep onBindViewHolder lightweight

**Images:**
- [ ] Load images asynchronously
- [ ] Sample large images
- [ ] Use appropriate cache strategies
- [ ] Implement placeholder/error states

**Memory:**
- [ ] No memory leaks
- [ ] Proper bitmap handling
- [ ] Release resources in onDestroy
- [ ] Use weak references where appropriate

---

## Русский

### Вопрос
Почему Android-приложение тормозит? Как выявить и исправить проблемы производительности, вызывающие подтормаживания UI?

### Ответ

Торможение приложения возникает, когда UI-поток блокируется или рендеринг кадра превышает 16ms (цель 60 FPS).

#### Основные причины:

**1. Блокировка главного потока**
- Синхронные DB/Network вызовы
- Тяжелые вычисления
- Решение: использовать корутины, Dispatchers.IO/Default

**2. Проблемы с памятью**
- Утечки памяти
- Избыточные аллокации
- Решение: LeakCanary, профилирование

**3. Overdraw и сложные layouts**
- Глубокая иерархия view
- Множественная отрисовка пикселей
- Решение: ConstraintLayout, Compose, уменьшение вложенности

**4. Неоптимизированные списки**
- Без recycling
- Без DiffUtil
- Решение: RecyclerView с оптимизацией

**5. Неправильная загрузка изображений**
- Загрузка больших изображений
- Синхронная загрузка
- Решение: Glide/Coil, sampling, кэширование

#### Инструменты диагностики:

**1. GPU Overdraw** - визуализация overdraw
**2. Profile GPU Rendering** - анализ времени кадров
**3. StrictMode** - детектирование нарушений
**4. Systrace/Perfetto** - детальное профилирование
**5. Android Profiler** - CPU, память, сеть, энергия
**6. LeakCanary** - детектирование утечек памяти

### Чек-лист производительности:

**UI поток:**
- Без disk I/O
- Без network вызовов
- Без тяжелых вычислений
- Асинхронная работа

**Layouts:**
- Минимальная вложенность
- ConstraintLayout/Compose
- Без overdraw

**Списки:**
- RecyclerView с DiffUtil
- Пагинация
- Легкий onBindViewHolder

**Изображения:**
- Асинхронная загрузка
- Sampling больших изображений
- Кэширование
