---
id: 20251011-220004
title: "Jank Detection and Frame Metrics / Обнаружение рывков и метрики кадров"
aliases: []

# Classification
topic: android
subtopics:
  - performance
  - jank
  - frames
  - rendering
  - profiling
question_kind: practical
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/performance, android/jank, android/frames, android/rendering, android/profiling, android/optimization, difficulty/medium]
source: Original
source_note: Frame rendering performance best practices

# Workflow & relations
status: draft
moc: moc-android
related: [macrobenchmark-startup, app-startup-optimization, baseline-profiles-optimization]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [en, ru, android/performance, android/jank, android/frames, android/rendering, android/profiling, android/optimization, difficulty/medium]
---
# Question (EN)
> Implement frame metrics monitoring to detect and fix jank. Use FrameMetricsAggregator, OnFrameMetricsAvailableListener, and systrace to identify rendering issues.

# Вопрос (RU)
> Реализуйте мониторинг метрик кадров для обнаружения и исправления рывков. Используйте FrameMetricsAggregator, OnFrameMetricsAvailableListener и systrace для выявления проблем рендеринга.

---

## Answer (EN)

### Overview

**Jank** occurs when the app fails to render a frame within the 16.67ms budget (60 FPS), causing visible stuttering. Modern devices support 90Hz (11.1ms) or 120Hz (8.33ms), making smooth rendering even more critical.

**Frame Budget:**
- 60 FPS: 16.67ms per frame
- 90 FPS: 11.11ms per frame
- 120 FPS: 8.33ms per frame

**Common Causes of Jank:**
1. Overdraw (rendering pixels multiple times)
2. Layout complexity (nested hierarchies)
3. Expensive onDraw() operations
4. Main thread blocking (I/O, computation)
5. RecyclerView inefficient adapter
6. Large bitmap loading
7. GC pauses

### FrameMetricsAggregator Implementation

**app/build.gradle.kts:**
```kotlin
dependencies {
    implementation("androidx.metrics:metrics-performance:1.0.0-beta01")
}
```

#### 1. Basic Frame Metrics Monitoring

```kotlin
class PerformanceMonitoringActivity : AppCompatActivity() {

    private var frameMetricsAggregator: FrameMetricsAggregator? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Start frame metrics collection
        frameMetricsAggregator = FrameMetricsAggregator()
        frameMetricsAggregator?.add(this)
    }

    override fun onResume() {
        super.onResume()
        frameMetricsAggregator?.reset()
    }

    override fun onPause() {
        super.onPause()

        // Analyze frame metrics
        frameMetricsAggregator?.let { aggregator ->
            val metrics = aggregator.metrics

            // Get frame durations for different stages
            val totalMetrics = metrics?.get(FrameMetricsAggregator.TOTAL_INDEX)

            if (totalMetrics != null) {
                analyzeFrameMetrics(totalMetrics)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        frameMetricsAggregator?.stop()
        frameMetricsAggregator = null
    }

    private fun analyzeFrameMetrics(metrics: SparseIntArray) {
        var slowFrames = 0
        var frozenFrames = 0
        var totalFrames = 0

        // Iterate through frame durations
        for (i in 0 until metrics.size()) {
            val frameDurationMs = metrics.keyAt(i)
            val frameCount = metrics.valueAt(i)

            totalFrames += frameCount

            // Slow frame: > 16ms (missed 60 FPS deadline)
            if (frameDurationMs > 16) {
                slowFrames += frameCount
            }

            // Frozen frame: > 700ms (completely unresponsive)
            if (frameDurationMs > 700) {
                frozenFrames += frameCount
            }
        }

        val slowFramePercentage = (slowFrames.toFloat() / totalFrames) * 100
        val frozenFramePercentage = (frozenFrames.toFloat() / totalFrames) * 100

        Log.d("FrameMetrics", """
            Total Frames: $totalFrames
            Slow Frames: $slowFrames (${"%.2f".format(slowFramePercentage)}%)
            Frozen Frames: $frozenFrames (${"%.2f".format(frozenFramePercentage)}%)
        """.trimIndent())

        // Report to analytics if jank is significant
        if (slowFramePercentage > 5.0) {
            reportJankToAnalytics(slowFramePercentage, frozenFramePercentage)
        }
    }

    private fun reportJankToAnalytics(slowFramePercentage: Float, frozenFramePercentage: Float) {
        Firebase.analytics.logEvent("jank_detected") {
            param("screen", this@PerformanceMonitoringActivity.javaClass.simpleName)
            param("slow_frame_percentage", slowFramePercentage.toDouble())
            param("frozen_frame_percentage", frozenFramePercentage.toDouble())
        }
    }
}
```

#### 2. Real-Time Frame Monitoring with OnFrameMetricsAvailableListener

```kotlin
class RealTimeFrameMonitor : AppCompatActivity() {

    private val frameMetricsListener = Window.OnFrameMetricsAvailableListener {
        _, frameMetrics, _ ->

        // Copy metrics (must be done in callback)
        val metrics = FrameMetrics(frameMetrics)

        // Analyze individual frame
        val totalDurationNs = metrics.getMetric(FrameMetrics.TOTAL_DURATION)
        val totalDurationMs = totalDurationNs / 1_000_000.0

        val inputDurationMs = metrics.getMetric(FrameMetrics.INPUT_HANDLING_DURATION) / 1_000_000.0
        val animationDurationMs = metrics.getMetric(FrameMetrics.ANIMATION_DURATION) / 1_000_000.0
        val layoutDurationMs = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
        val drawDurationMs = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
        val syncDurationMs = metrics.getMetric(FrameMetrics.SYNC_DURATION) / 1_000_000.0
        val commandDurationMs = metrics.getMetric(FrameMetrics.COMMAND_ISSUE_DURATION) / 1_000_000.0

        // Check for slow frames
        if (totalDurationMs > 16.67) {
            Log.w("FrameMetrics", """
                Slow frame detected: ${"%.2f".format(totalDurationMs)}ms
                Breakdown:
                - Input: ${"%.2f".format(inputDurationMs)}ms
                - Animation: ${"%.2f".format(animationDurationMs)}ms
                - Layout: ${"%.2f".format(layoutDurationMs)}ms
                - Draw: ${"%.2f".format(drawDurationMs)}ms
                - Sync: ${"%.2f".format(syncDurationMs)}ms
                - Command: ${"%.2f".format(commandDurationMs)}ms
            """.trimIndent())

            // Identify bottleneck
            val bottleneck = when {
                layoutDurationMs > 8 -> "Layout complexity"
                drawDurationMs > 8 -> "Draw operations"
                syncDurationMs > 8 -> "GPU synchronization"
                else -> "Multiple factors"
            }

            reportFrameBottleneck(bottleneck, totalDurationMs)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Register listener
        window.addOnFrameMetricsAvailableListener(
            frameMetricsListener,
            Handler(Looper.getMainLooper())
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        window.removeOnFrameMetricsAvailableListener(frameMetricsListener)
    }

    private fun reportFrameBottleneck(bottleneck: String, duration: Double) {
        Firebase.analytics.logEvent("frame_bottleneck") {
            param("type", bottleneck)
            param("duration_ms", duration)
        }
    }
}
```

#### 3. JankStats Library (Modern Approach)

```kotlin
dependencies {
    implementation("androidx.metrics:metrics-performance:1.0.0-beta01")
}

class ModernJankMonitor : AppCompatActivity() {

    private lateinit var jankStats: JankStats

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Create JankStats instance
        jankStats = JankStats.createAndTrack(
            window,
            jankStatsListener
        )
    }

    private val jankStatsListener = JankStats.OnFrameListener { frameData ->
        // Called for each frame
        if (frameData.isJank) {
            val frameDurationMs = frameData.frameDurationUiNanos / 1_000_000.0

            Log.w("JankStats", """
                Jank detected:
                Duration: ${"%.2f".format(frameDurationMs)}ms
                States: ${frameData.states.joinToString()}
            """.trimIndent())

            // Track jank by UI state
            val currentState = frameData.states.lastOrNull() ?: "unknown"
            trackJankByState(currentState, frameDurationMs)
        }
    }

    // Track UI state for better jank attribution
    private fun trackScrolling(isScrolling: Boolean) {
        if (isScrolling) {
            jankStats.jankHappened("scrolling")
        }
    }

    private fun trackJankByState(state: String, duration: Double) {
        Firebase.analytics.logEvent("jank_by_state") {
            param("state", state)
            param("duration_ms", duration)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        jankStats.isTrackingEnabled = false
    }
}
```

### Common Jank Causes and Fixes

#### 1. Overdraw

** Problem: Multiple layers rendering**

```xml
<!-- Multiple backgrounds causing overdraw -->
<LinearLayout
    android:background="@color/white">

    <LinearLayout
        android:background="@color/light_gray">

        <TextView
            android:background="@color/white"
            android:text="Hello" />
    </LinearLayout>
</LinearLayout>
```

** Solution: Remove unnecessary backgrounds**

```xml
<!-- Single background layer -->
<LinearLayout>
    <LinearLayout
        android:background="@color/light_gray">

        <TextView
            android:text="Hello" />
    </LinearLayout>
</LinearLayout>
```

**Detect Overdraw:**
```
Developer Options → Debug GPU Overdraw → Show overdraw areas
- Blue: 1x overdraw (acceptable)
- Green: 2x overdraw (investigate)
- Pink: 3x overdraw (fix)
- Red: 4x+ overdraw (critical)
```

#### 2. Layout Complexity

** Problem: Deeply nested layouts**

```xml
<LinearLayout>
    <RelativeLayout>
        <LinearLayout>
            <RelativeLayout>
                <LinearLayout>
                    <TextView />
                </LinearLayout>
            </RelativeLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>
<!-- Hierarchy depth: 6 levels, slow measure/layout -->
```

** Solution: Flatten with ConstraintLayout**

```xml
<androidx.constraintlayout.widget.ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
<!-- Hierarchy depth: 2 levels, fast measure/layout -->
```

#### 3. RecyclerView Jank

** Problem: Expensive bind operations**

```kotlin
class SlowAdapter : RecyclerView.Adapter<ViewHolder>() {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        // SLOW: Load image synchronously
        val bitmap = BitmapFactory.decodeFile(item.imagePath)
        holder.imageView.setImageBitmap(bitmap)

        // SLOW: Complex text formatting
        val formattedText = complexTextFormatting(item.description)
        holder.textView.text = formattedText
    }

    private fun complexTextFormatting(text: String): Spanned {
        // Expensive operation on main thread
        return Html.fromHtml(text, Html.FROM_HTML_MODE_LEGACY)
    }
}
```

** Solution: Async operations and caching**

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val formattedTextCache = LruCache<String, Spanned>(100)

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        // Load image asynchronously with Coil
        holder.imageView.load(item.imagePath) {
            crossfade(true)
            placeholder(R.drawable.placeholder)
        }

        // Use cached formatted text
        val formattedText = formattedTextCache.get(item.id)
            ?: complexTextFormatting(item.description).also {
                formattedTextCache.put(item.id, it)
            }
        holder.textView.text = formattedText
    }

    // Pre-format text in background
    fun prefetchItems(items: List<Item>) {
        CoroutineScope(Dispatchers.Default).launch {
            items.forEach { item ->
                if (formattedTextCache.get(item.id) == null) {
                    val formatted = complexTextFormatting(item.description)
                    formattedTextCache.put(item.id, formatted)
                }
            }
        }
    }
}
```

#### 4. View Inflation Jank

** Problem: Inflating views on demand**

```kotlin
// Inflate complex view when needed
button.setOnClickListener {
    val detailView = layoutInflater.inflate(
        R.layout.complex_detail_view,  // 50ms to inflate
        container,
        false
    )
    container.addView(detailView)
}
```

** Solution: ViewStub for lazy inflation**

```xml
<!-- activity_main.xml -->
<FrameLayout>
    <ViewStub
        android:id="@+id/detail_view_stub"
        android:layout="@layout/complex_detail_view"
        android:inflatedId="@+id/detail_view" />
</FrameLayout>
```

```kotlin
// Inflate only when needed, UI appears faster
button.setOnClickListener {
    val viewStub = findViewById<ViewStub>(R.id.detail_view_stub)
    val detailView = viewStub?.inflate() ?: findViewById(R.id.detail_view)
    // Configure detailView...
}
```

### Systrace Analysis

#### 1. Capture Systrace

```bash
# Record 10 seconds of app interaction
python $ANDROID_HOME/platform-tools/systrace/systrace.py \
    --time=10 \
    -o trace.html \
    -a com.example.myapp \
    sched gfx view wm am app

# Open in Chrome
chrome trace.html
```

#### 2. Identify Jank in Trace

**Look for:**
1. **Frame deadline misses**: Red/yellow bars in frame timeline
2. **Long measure/layout**: > 8ms indicates complexity
3. **Expensive draw**: > 8ms indicates overdraw or custom drawing
4. **GC pauses**: "GC" events during frame rendering
5. **Main thread blocking**: Long operations on UI thread

**Example Analysis:**
```
Frame 145: 28ms (JANK - missed deadline)
 Input: 0.2ms 
 Animation: 0.5ms 
 Measure/Layout: 14.3ms  (TOO SLOW)
   RecyclerView.onMeasure: 12.8ms
      Adapter.onBindViewHolder: 11.2ms (BOTTLENECK)
 Draw: 8.1ms  (SLOW)
 Sync: 4.9ms 

Action: Optimize onBindViewHolder - move work off main thread
```

### Production Monitoring

#### 1. Firebase Performance Monitoring

```kotlin
class MainActivity : AppCompatActivity() {

    private val frameMetricsMonitor = FrameMetricsMonitor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Start monitoring frames
        frameMetricsMonitor.start(this)
    }

    override fun onDestroy() {
        super.onDestroy()
        frameMetricsMonitor.stop()
    }
}

class FrameMetricsMonitor {

    private var frameMetricsAggregator: FrameMetricsAggregator? = null
    private val performanceMonitoring = Firebase.performance

    fun start(activity: Activity) {
        frameMetricsAggregator = FrameMetricsAggregator().apply {
            add(activity)
        }
    }

    fun stop() {
        frameMetricsAggregator?.let { aggregator ->
            val metrics = aggregator.metrics?.get(FrameMetricsAggregator.TOTAL_INDEX)

            if (metrics != null) {
                val stats = calculateFrameStats(metrics)

                // Log to Firebase Performance
                val trace = performanceMonitoring.newTrace("screen_rendering")
                trace.putMetric("slow_frames", stats.slowFrames.toLong())
                trace.putMetric("frozen_frames", stats.frozenFrames.toLong())
                trace.putMetric("total_frames", stats.totalFrames.toLong())
                trace.putMetric("slow_frame_percentage", (stats.slowFramePercentage * 100).toLong())
                trace.stop()
            }

            aggregator.stop()
        }
        frameMetricsAggregator = null
    }

    private fun calculateFrameStats(metrics: SparseIntArray): FrameStats {
        var slowFrames = 0
        var frozenFrames = 0
        var totalFrames = 0

        for (i in 0 until metrics.size()) {
            val frameDurationMs = metrics.keyAt(i)
            val frameCount = metrics.valueAt(i)

            totalFrames += frameCount

            if (frameDurationMs > 16) slowFrames += frameCount
            if (frameDurationMs > 700) frozenFrames += frameCount
        }

        return FrameStats(
            totalFrames = totalFrames,
            slowFrames = slowFrames,
            frozenFrames = frozenFrames,
            slowFramePercentage = slowFrames.toFloat() / totalFrames
        )
    }

    data class FrameStats(
        val totalFrames: Int,
        val slowFrames: Int,
        val frozenFrames: Int,
        val slowFramePercentage: Float
    )
}
```

### Best Practices

1. **Target 60 FPS Minimum**: Modern devices support higher, but 60 FPS is baseline
2. **Measure Real Devices**: Emulators don't reflect real rendering performance
3. **Monitor in Production**: Use Firebase Performance to track user experience
4. **Flatten View Hierarchies**: Use ConstraintLayout to reduce nesting
5. **Eliminate Overdraw**: Remove unnecessary backgrounds and layers
6. **Optimize RecyclerView**: Use DiffUtil, ViewHolder pattern, prefetch
7. **Async Image Loading**: Use Coil/Glide, never load images synchronously
8. **ViewStub for Rare Views**: Defer inflation of infrequently shown content
9. **Profile Before Optimizing**: Use systrace to identify actual bottlenecks
10. **Test on Low-End Devices**: Jank is magnified on slow hardware
11. **Avoid Main Thread Work**: Move heavy computation to background
12. **Use Jetpack Compose**: Modern UI toolkit with better performance

### Common Pitfalls

1. **Synchronous Image Loading**: Always use async image libraries
2. **Complex onDraw()**: Custom drawing should be minimal and cached
3. **Deeply Nested Layouts**: Flatten hierarchies with ConstraintLayout
4. **Expensive Adapter Binding**: Keep onBindViewHolder() lightweight
5. **Main Thread I/O**: File/network operations must be async
6. **Not Caching Formatted Text**: HTML parsing, regex expensive
7. **Ignoring Overdraw**: Multiple background layers slow rendering
8. **Large Bitmaps**: Downsample images to view dimensions
9. **Blocking Animations**: Use hardware-accelerated animations
10. **Testing Only on Flagship Devices**: Jank appears on mid/low-end phones

## Ответ (RU)

### Обзор

**Jank (рывки)** возникает, когда приложение не может отрендерить кадр в рамках бюджета 16.67мс (60 FPS), что вызывает видимые подтормаживания. Современные устройства поддерживают 90Hz (11.1мс) или 120Hz (8.33мс), что делает плавный рендеринг еще более критичным.

**Бюджет кадра:**
- 60 FPS: 16.67мс на кадр
- 90 FPS: 11.11мс на кадр
- 120 FPS: 8.33мс на кадр

**Распространенные причины рывков:**
1. Overdraw (отрисовка пикселей несколько раз)
2. Сложность макета (вложенные иерархии)
3. Дорогие операции в onDraw()
4. Блокировка главного потока (I/O, вычисления)
5. Неэффективный адаптер RecyclerView
6. Загрузка больших bitmap
7. Паузы сборщика мусора (GC)

### Реализация FrameMetricsAggregator

**app/build.gradle.kts:**
```kotlin
dependencies {
    implementation("androidx.metrics:metrics-performance:1.0.0-beta01")
}
```

#### 1. Базовый мониторинг метрик кадров

```kotlin
class PerformanceMonitoringActivity : AppCompatActivity() {

    private var frameMetricsAggregator: FrameMetricsAggregator? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Start frame metrics collection
        frameMetricsAggregator = FrameMetricsAggregator()
        frameMetricsAggregator?.add(this)
    }

    override fun onResume() {
        super.onResume()
        frameMetricsAggregator?.reset()
    }

    override fun onPause() {
        super.onPause()

        // Analyze frame metrics
        frameMetricsAggregator?.let { aggregator ->
            val metrics = aggregator.metrics

            // Get frame durations for different stages
            val totalMetrics = metrics?.get(FrameMetricsAggregator.TOTAL_INDEX)

            if (totalMetrics != null) {
                analyzeFrameMetrics(totalMetrics)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        frameMetricsAggregator?.stop()
        frameMetricsAggregator = null
    }

    private fun analyzeFrameMetrics(metrics: SparseIntArray) {
        var slowFrames = 0
        var frozenFrames = 0
        var totalFrames = 0

        // Iterate through frame durations
        for (i in 0 until metrics.size()) {
            val frameDurationMs = metrics.keyAt(i)
            val frameCount = metrics.valueAt(i)

            totalFrames += frameCount

            // Slow frame: > 16ms (missed 60 FPS deadline)
            if (frameDurationMs > 16) {
                slowFrames += frameCount
            }

            // Frozen frame: > 700ms (completely unresponsive)
            if (frameDurationMs > 700) {
                frozenFrames += frameCount
            }
        }

        val slowFramePercentage = (slowFrames.toFloat() / totalFrames) * 100
        val frozenFramePercentage = (frozenFrames.toFloat() / totalFrames) * 100

        Log.d("FrameMetrics", """
            Total Frames: $totalFrames
            Slow Frames: $slowFrames (${"%.2f".format(slowFramePercentage)}%)
            Frozen Frames: $frozenFrames (${"%.2f".format(frozenFramePercentage)}%)
        """.trimIndent())

        // Report to analytics if jank is significant
        if (slowFramePercentage > 5.0) {
            reportJankToAnalytics(slowFramePercentage, frozenFramePercentage)
        }
    }

    private fun reportJankToAnalytics(slowFramePercentage: Float, frozenFramePercentage: Float) {
        Firebase.analytics.logEvent("jank_detected") {
            param("screen", this@PerformanceMonitoringActivity.javaClass.simpleName)
            param("slow_frame_percentage", slowFramePercentage.toDouble())
            param("frozen_frame_percentage", frozenFramePercentage.toDouble())
        }
    }
}
```

#### 2. Мониторинг кадров в реальном времени с OnFrameMetricsAvailableListener

```kotlin
class RealTimeFrameMonitor : AppCompatActivity() {

    private val frameMetricsListener = Window.OnFrameMetricsAvailableListener {
        _, frameMetrics, _ ->

        // Copy metrics (must be done in callback)
        val metrics = FrameMetrics(frameMetrics)

        // Analyze individual frame
        val totalDurationNs = metrics.getMetric(FrameMetrics.TOTAL_DURATION)
        val totalDurationMs = totalDurationNs / 1_000_000.0

        val inputDurationMs = metrics.getMetric(FrameMetrics.INPUT_HANDLING_DURATION) / 1_000_000.0
        val animationDurationMs = metrics.getMetric(FrameMetrics.ANIMATION_DURATION) / 1_000_000.0
        val layoutDurationMs = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
        val drawDurationMs = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
        val syncDurationMs = metrics.getMetric(FrameMetrics.SYNC_DURATION) / 1_000_000.0
        val commandDurationMs = metrics.getMetric(FrameMetrics.COMMAND_ISSUE_DURATION) / 1_000_000.0

        // Check for slow frames
        if (totalDurationMs > 16.67) {
            Log.w("FrameMetrics", """
                Slow frame detected: ${"%.2f".format(totalDurationMs)}ms
                Breakdown:
                - Input: ${"%.2f".format(inputDurationMs)}ms
                - Animation: ${"%.2f".format(animationDurationMs)}ms
                - Layout: ${"%.2f".format(layoutDurationMs)}ms
                - Draw: ${"%.2f".format(drawDurationMs)}ms
                - Sync: ${"%.2f".format(syncDurationMs)}ms
                - Command: ${"%.2f".format(commandDurationMs)}ms
            """.trimIndent())

            // Identify bottleneck
            val bottleneck = when {
                layoutDurationMs > 8 -> "Layout complexity"
                drawDurationMs > 8 -> "Draw operations"
                syncDurationMs > 8 -> "GPU synchronization"
                else -> "Multiple factors"
            }

            reportFrameBottleneck(bottleneck, totalDurationMs)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Register listener
        window.addOnFrameMetricsAvailableListener(
            frameMetricsListener,
            Handler(Looper.getMainLooper())
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        window.removeOnFrameMetricsAvailableListener(frameMetricsListener)
    }

    private fun reportFrameBottleneck(bottleneck: String, duration: Double) {
        Firebase.analytics.logEvent("frame_bottleneck") {
            param("type", bottleneck)
            param("duration_ms", duration)
        }
    }
}
```

#### 3. Библиотека JankStats (Современный подход)

```kotlin
dependencies {
    implementation("androidx.metrics:metrics-performance:1.0.0-beta01")
}

class ModernJankMonitor : AppCompatActivity() {

    private lateinit var jankStats: JankStats

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Create JankStats instance
        jankStats = JankStats.createAndTrack(
            window,
            jankStatsListener
        )
    }

    private val jankStatsListener = JankStats.OnFrameListener { frameData ->
        // Called for each frame
        if (frameData.isJank) {
            val frameDurationMs = frameData.frameDurationUiNanos / 1_000_000.0

            Log.w("JankStats", """
                Jank detected:
                Duration: ${"%.2f".format(frameDurationMs)}ms
                States: ${frameData.states.joinToString()}
            """.trimIndent())

            // Track jank by UI state
            val currentState = frameData.states.lastOrNull() ?: "unknown"
            trackJankByState(currentState, frameDurationMs)
        }
    }

    // Track UI state for better jank attribution
    private fun trackScrolling(isScrolling: Boolean) {
        if (isScrolling) {
            jankStats.jankHappened("scrolling")
        }
    }

    private fun trackJankByState(state: String, duration: Double) {
        Firebase.analytics.logEvent("jank_by_state") {
            param("state", state)
            param("duration_ms", duration)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        jankStats.isTrackingEnabled = false
    }
}
```

### Распространенные причины и исправления рывков

#### 1. Overdraw

**Проблема:** Отрисовка нескольких слоев
**Решение:** Убрать ненужные фоны
**Обнаружение:** Developer Options → Debug GPU Overdraw

#### 2. Сложность макета

**Проблема:** Глубоко вложенные макеты
**Решение:** Упростить с помощью ConstraintLayout

#### 3. Рывки в RecyclerView

**Проблема:** Дорогие операции в onBindViewHolder
**Решение:** Асинхронные операции и кэширование

#### 4. Рывки при инфляции View

**Проблема:** Инфляция сложных view по требованию
**Решение:** ViewStub для ленивой инфляции

### Анализ с помощью Systrace

#### 1. Захват Systrace

```bash
python $ANDROID_HOME/platform-tools/systrace/systrace.py ...
```

#### 2. Определение рывков в трейсе

**Искать:**
1.  **Пропуски дедлайнов кадров**: Красные/желтые полосы
2.  **Долгие measure/layout**: > 8мс
3.  **Дорогие draw**: > 8мс
4.  **Паузы GC**: События "GC"
5.  **Блокировка главного потока**: Долгие операции

### Мониторинг в продакшене

#### 1. Firebase Performance Monitoring

```kotlin
class FrameMetricsMonitor {

    private var frameMetricsAggregator: FrameMetricsAggregator? = null
    private val performanceMonitoring = Firebase.performance

    fun start(activity: Activity) {
        frameMetricsAggregator = FrameMetricsAggregator().apply {
            add(activity)
        }
    }

    fun stop() {
        frameMetricsAggregator?.let { aggregator ->
            val metrics = aggregator.metrics?.get(FrameMetricsAggregator.TOTAL_INDEX)

            if (metrics != null) {
                val stats = calculateFrameStats(metrics)

                // Log to Firebase Performance
                val trace = performanceMonitoring.newTrace("screen_rendering")
                trace.putMetric("slow_frames", stats.slowFrames.toLong())
                trace.putMetric("frozen_frames", stats.frozenFrames.toLong())
                trace.putMetric("total_frames", stats.totalFrames.toLong())
                trace.putMetric("slow_frame_percentage", (stats.slowFramePercentage * 100).toLong())
                trace.stop()
            }

            aggregator.stop()
        }
        frameMetricsAggregator = null
    }
    // ...
}
```

### Лучшие практики

1.  **Цель - минимум 60 FPS**
2.  **Измеряйте на реальных устройствах**
3.  **Мониторьте в продакшене**
4.  **Упрощайте иерархии View**
5.  **Устраняйте Overdraw**
6.  **Оптимизируйте RecyclerView**
7.  **Асинхронная загрузка изображений**
8.  **Используйте ViewStub для редких View**
9.  **Профилируйте перед оптимизацией**
10. **Тестируйте на слабых устройствах**
11. **Избегайте работы в главном потоке**
12. **Используйте Jetpack Compose**

### Распространенные ошибки

1.  **Синхронная загрузка изображений**
2.  **Сложный onDraw()**
3.  **Глубоко вложенные макеты**
4.  **Дорогие привязки в адаптере**
5.  **I/O в главном потоке**
6.  **Игнорирование Overdraw**
7.  **Большие Bitmaps**
8.  **Тестирование только на флагманах**

---

## References
- [JankStats Library](https://developer.android.com/jetpack/androidx/releases/metrics)
- [Frame Metrics](https://developer.android.com/reference/android/view/FrameMetrics)
- [Slow Rendering](https://developer.android.com/topic/performance/vitals/render)
- [Systrace](https://developer.android.com/topic/performance/tracing)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview
### Related (Medium)
- [[q-memory-leak-detection--android--medium]] - Performance
- [[q-macrobenchmark-startup--android--medium]] - Performance
- [[q-app-startup-optimization--android--medium]] - Performance
- [[q-baseline-profiles-optimization--android--medium]] - Performance
### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
