---
topic: android
tags:
  - layout
  - performance
  - android
  - ui
  - layouts
difficulty: medium
status: draft
---

# What is layout performance measured in?

# Вопрос (RU)

В чём измеряется производительность layout

## Answer (EN)
Layout performance in Android is measured in **milliseconds (ms)** of rendering time, specifically tracking the time spent in three main phases: **measure**, **layout**, and **draw**. Additionally, in modern Android development, we measure **recomposition count** and **frame drops**.

### 1. Three Phases of Rendering

Android renders UI in three phases, each measured in milliseconds:

```kotlin
// Each frame must complete in ~16ms (60fps) or ~11ms (90fps)
val frameTime = 16.67ms  // 60 FPS target
val frameTime90 = 11.11ms // 90 FPS target
val frameTime120 = 8.33ms // 120 FPS target

// Three phases:
// 1. Measure phase  - determine size of views
// 2. Layout phase   - position views
// 3. Draw phase     - render to screen
```

#### Measuring Performance

```kotlin
class PerformanceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val rootView = layoutInflater.inflate(R.layout.activity_main, null)

        // Measure phase timing
        val measureStart = System.nanoTime()
        rootView.measure(
            View.MeasureSpec.makeMeasureSpec(resources.displayMetrics.widthPixels, View.MeasureSpec.EXACTLY),
            View.MeasureSpec.makeMeasureSpec(resources.displayMetrics.heightPixels, View.MeasureSpec.EXACTLY)
        )
        val measureTime = (System.nanoTime() - measureStart) / 1_000_000.0
        Log.d("Performance", "Measure: ${measureTime}ms")

        // Layout phase timing
        val layoutStart = System.nanoTime()
        rootView.layout(0, 0, rootView.measuredWidth, rootView.measuredHeight)
        val layoutTime = (System.nanoTime() - layoutStart) / 1_000_000.0
        Log.d("Performance", "Layout: ${layoutTime}ms")

        setContentView(rootView)
    }
}
```

### 2. Frame Rate Metrics

Performance is often measured in frames per second (FPS) and dropped frames.

```kotlin
class FrameRateMonitor {

    private var frameCount = 0
    private var lastTime = System.currentTimeMillis()

    fun onFrame() {
        frameCount++
        val currentTime = System.currentTimeMillis()

        if (currentTime - lastTime >= 1000) {
            val fps = frameCount
            Log.d("FPS", "Current FPS: $fps")

            frameCount = 0
            lastTime = currentTime
        }
    }

    // Check for dropped frames
    fun checkFrameDrop(frameTimeMs: Long) {
        val targetFrameTime = 16.67 // 60fps
        if (frameTimeMs > targetFrameTime) {
            val droppedFrames = (frameTimeMs / targetFrameTime).toInt()
            Log.w("Performance", "Dropped $droppedFrames frames (${frameTimeMs}ms)")
        }
    }
}
```

### 3. Using Choreographer for Frame Timing

```kotlin
class ChoreographerMonitor(private val context: Context) {

    private val choreographer = Choreographer.getInstance()
    private var lastFrameTime = 0L

    fun start() {
        choreographer.postFrameCallback(frameCallback)
    }

    private val frameCallback = object : Choreographer.FrameCallback {
        override fun doFrame(frameTimeNanos: Long) {
            if (lastFrameTime != 0L) {
                val frameTime = (frameTimeNanos - lastFrameTime) / 1_000_000.0
                val fps = 1000.0 / frameTime

                Log.d("Choreographer", "Frame time: ${frameTime}ms, FPS: $fps")

                if (frameTime > 16.67) {
                    Log.w("Performance", "Slow frame detected: ${frameTime}ms")
                }
            }

            lastFrameTime = frameTimeNanos
            choreographer.postFrameCallback(this)
        }
    }

    fun stop() {
        choreographer.removeFrameCallback(frameCallback)
    }
}
```

### 4. Systrace and Performance Profiling

Android provides tools to measure performance in detail:

```kotlin
class SystemTraceExample {

    fun measurePerformance() {
        // Add trace sections
        Trace.beginSection("loadData")
        loadDataFromDatabase()
        Trace.endSection()

        Trace.beginSection("renderUI")
        renderComplexUI()
        Trace.endSection()
    }

    private fun loadDataFromDatabase() {
        // Database operations
    }

    private fun renderComplexUI() {
        // UI rendering
    }
}

// View in Systrace:
// adb shell atrace --async_start view gfx input
// (perform actions)
// adb shell atrace --async_stop > trace.html
```

### 5. Layout Complexity Metrics

```kotlin
class LayoutComplexityAnalyzer {

    fun analyzeLayout(view: View): LayoutMetrics {
        var viewCount = 0
        var maxDepth = 0

        fun traverse(v: View, depth: Int) {
            viewCount++
            maxDepth = maxOf(maxDepth, depth)

            if (v is ViewGroup) {
                for (i in 0 until v.childCount) {
                    traverse(v.getChildAt(i), depth + 1)
                }
            }
        }

        traverse(view, 0)

        return LayoutMetrics(
            viewCount = viewCount,
            maxDepth = maxDepth,
            complexity = viewCount * maxDepth
        )
    }

    data class LayoutMetrics(
        val viewCount: Int,
        val maxDepth: Int,
        val complexity: Int
    )
}

// Usage
val analyzer = LayoutComplexityAnalyzer()
val metrics = analyzer.analyzeLayout(rootView)
Log.d("Layout", """
    Views: ${metrics.viewCount}
    Depth: ${metrics.maxDepth}
    Complexity: ${metrics.complexity}
""".trimIndent())
```

### 6. Jetpack Compose Recomposition Metrics

In Compose, performance is measured by recomposition count:

```kotlin
@Composable
fun RecompositionCounter() {
    val recompositions = remember { mutableStateOf(0) }

    SideEffect {
        recompositions.value++
    }

    Text("Recompositions: ${recompositions.value}")
}

// Measure recomposition with Compose Compiler Metrics
// In build.gradle:
// kotlinOptions {
//     freeCompilerArgs += [
//         "-P",
//         "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
//         project.buildDir.absolutePath + "/compose_metrics"
//     ]
// }
```

### 7. Performance Monitoring Tools

```kotlin
class PerformanceMonitor(private val activity: Activity) {

    private val frameMetrics = SparseIntArray()

    fun startMonitoring() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            activity.window.addOnFrameMetricsAvailableListener(
                { _, frameMetrics, dropCount ->
                    val totalDuration = frameMetrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
                    val layoutDuration = frameMetrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
                    val drawDuration = frameMetrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0

                    Log.d("FrameMetrics", """
                        Total: ${totalDuration}ms
                        Layout: ${layoutDuration}ms
                        Draw: ${drawDuration}ms
                        Dropped: $dropCount
                    """.trimIndent())
                },
                Handler(Looper.getMainLooper())
            )
        }
    }
}
```

### 8. Benchmarking with Macrobenchmark

```kotlin
@RunWith(AndroidJUnit4::class)
class LayoutBenchmark {

    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun scrollBenchmark() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(
            FrameTimingMetric(),
            TraceSectionMetric("RecyclerView:onLayout")
        ),
        iterations = 10,
        setupBlock = {
            pressHome()
            startActivityAndWait()
        }
    ) {
        val recycler = device.findObject(By.res("recycler_view"))
        recycler.setGestureMargin(device.displayWidth / 5)

        repeat(3) {
            recycler.fling(Direction.DOWN)
            device.waitForIdle()
        }
    }
}
```

### 9. Custom Performance Metrics

```kotlin
class CustomPerformanceMetrics {

    data class RenderMetrics(
        val measureTimeMs: Double,
        val layoutTimeMs: Double,
        val drawTimeMs: Double,
        val totalTimeMs: Double,
        val recompositionCount: Int = 0
    )

    fun measureRenderPerformance(view: View): RenderMetrics {
        var measureTime = 0.0
        var layoutTime = 0.0
        var drawTime = 0.0

        // Measure phase
        measureTime = measureTime {
            view.measure(
                View.MeasureSpec.UNSPECIFIED,
                View.MeasureSpec.UNSPECIFIED
            )
        }

        // Layout phase
        layoutTime = measureTime {
            view.layout(0, 0, view.measuredWidth, view.measuredHeight)
        }

        // Draw phase (approximate)
        val bitmap = Bitmap.createBitmap(
            view.measuredWidth,
            view.measuredHeight,
            Bitmap.Config.ARGB_8888
        )
        val canvas = Canvas(bitmap)
        drawTime = measureTime {
            view.draw(canvas)
        }

        return RenderMetrics(
            measureTimeMs = measureTime,
            layoutTimeMs = layoutTime,
            drawTimeMs = drawTime,
            totalTimeMs = measureTime + layoutTime + drawTime
        )
    }

    private fun measureTime(block: () -> Unit): Double {
        val start = System.nanoTime()
        block()
        return (System.nanoTime() - start) / 1_000_000.0
    }
}
```

### 10. Performance Thresholds

```kotlin
object PerformanceThresholds {
    // Target frame times
    const val TARGET_60FPS_MS = 16.67
    const val TARGET_90FPS_MS = 11.11
    const val TARGET_120FPS_MS = 8.33

    // Phase targets (for 60fps)
    const val MAX_MEASURE_MS = 5.0
    const val MAX_LAYOUT_MS = 5.0
    const val MAX_DRAW_MS = 6.67

    // Complexity limits
    const val MAX_VIEW_HIERARCHY_DEPTH = 10
    const val MAX_VIEWS_PER_LAYOUT = 80

    // Recomposition limits (Compose)
    const val MAX_RECOMPOSITIONS_PER_FRAME = 10

    fun checkPerformance(metrics: RenderMetrics): PerformanceReport {
        return PerformanceReport(
            isWithinBudget = metrics.totalTimeMs <= TARGET_60FPS_MS,
            warnings = buildList {
                if (metrics.measureTimeMs > MAX_MEASURE_MS) {
                    add("Measure phase too slow: ${metrics.measureTimeMs}ms")
                }
                if (metrics.layoutTimeMs > MAX_LAYOUT_MS) {
                    add("Layout phase too slow: ${metrics.layoutTimeMs}ms")
                }
                if (metrics.drawTimeMs > MAX_DRAW_MS) {
                    add("Draw phase too slow: ${metrics.drawTimeMs}ms")
                }
            }
        )
    }

    data class PerformanceReport(
        val isWithinBudget: Boolean,
        val warnings: List<String>
    )
}
```

### Summary: Key Performance Metrics

| Metric | Unit | Target (60fps) |
|--------|------|----------------|
| Frame time | milliseconds | < 16.67ms |
| Measure phase | milliseconds | < 5ms |
| Layout phase | milliseconds | < 5ms |
| Draw phase | milliseconds | < 6.67ms |
| Recomposition count | number | Minimize |
| View hierarchy depth | levels | < 10 |
| Total views | count | < 80 |

### Best Practices

1. **Monitor frame time** - Keep under 16.67ms for 60fps
2. **Minimize recompositions** in Compose
3. **Flatten view hierarchy** - Reduce depth
4. **Use ConstraintLayout** - Avoid nested layouts
5. **Profile with Systrace** - Identify bottlenecks
6. **Batch updates** - Avoid multiple invalidations

## Ответ (RU)

Производительность измеряется в миллисекундах времени отрисовки (measure, layout, draw). Также учитывается количество операций пересчёта и перекомпоновки. В Jetpack Compose оценивается количеством recomposition и snapshot изменений.
