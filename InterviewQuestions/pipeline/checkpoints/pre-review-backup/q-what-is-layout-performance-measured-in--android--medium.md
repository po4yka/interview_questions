---
id: 20251017-112427
title: "What Is Layout Performance Measured In / В чем измеряется производительность layout"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-separate-ui-business-logic--android--easy, q-koin-fundamentals--dependency-injection--medium, q-fragments-history-and-purpose--android--hard]
created: 2025-10-15
tags: [performance, android, ui, layouts, difficulty/medium]
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

Производительность layout в Android измеряется в **миллисекундах (мс)** времени отрисовки, конкретно отслеживая время, затраченное в трёх основных фазах: **measure**, **layout** и **draw**. Кроме того, в современной разработке Android мы измеряем **количество перекомпоновок (recomposition count)** и **потерянные кадры (frame drops)**.

### 1. Три фазы отрисовки

Android отрисовывает UI в три фазы, каждая измеряется в миллисекундах:

```kotlin
// Каждый кадр должен завершиться за ~16мс (60fps) или ~11мс (90fps)
val frameTime = 16.67 // Цель 60 FPS
val frameTime90 = 11.11 // Цель 90 FPS
val frameTime120 = 8.33 // Цель 120 FPS

// Три фазы:
// 1. Фаза Measure  - определение размера views
// 2. Фаза Layout   - позиционирование views
// 3. Фаза Draw     - отрисовка на экран
```

#### Измерение производительности

```kotlin
class PerformanceActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val rootView = layoutInflater.inflate(R.layout.activity_main, null)

        // Измерение фазы measure
        val measureStart = System.nanoTime()
        rootView.measure(
            View.MeasureSpec.makeMeasureSpec(resources.displayMetrics.widthPixels, View.MeasureSpec.EXACTLY),
            View.MeasureSpec.makeMeasureSpec(resources.displayMetrics.heightPixels, View.MeasureSpec.EXACTLY)
        )
        val measureTime = (System.nanoTime() - measureStart) / 1_000_000.0
        Log.d("Performance", "Measure: ${measureTime}мс")

        // Измерение фазы layout
        val layoutStart = System.nanoTime()
        rootView.layout(0, 0, rootView.measuredWidth, rootView.measuredHeight)
        val layoutTime = (System.nanoTime() - layoutStart) / 1_000_000.0
        Log.d("Performance", "Layout: ${layoutTime}мс")

        setContentView(rootView)
    }
}
```

### 2. Метрики частоты кадров

Производительность часто измеряется в кадрах в секунду (FPS) и потерянных кадрах.

```kotlin
class FrameRateMonitor {

    private var frameCount = 0
    private var lastTime = System.currentTimeMillis()

    fun onFrame() {
        frameCount++
        val currentTime = System.currentTimeMillis()

        if (currentTime - lastTime >= 1000) {
            val fps = frameCount
            Log.d("FPS", "Текущий FPS: $fps")

            frameCount = 0
            lastTime = currentTime
        }
    }

    // Проверка потерянных кадров
    fun checkFrameDrop(frameTimeMs: Long) {
        val targetFrameTime = 16.67 // 60fps
        if (frameTimeMs > targetFrameTime) {
            val droppedFrames = (frameTimeMs / targetFrameTime).toInt()
            Log.w("Performance", "Потеряно $droppedFrames кадров (${frameTimeMs}мс)")
        }
    }
}
```

### 3. Использование Choreographer для измерения времени кадров

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

                Log.d("Choreographer", "Время кадра: ${frameTime}мс, FPS: $fps")

                if (frameTime > 16.67) {
                    Log.w("Performance", "Обнаружен медленный кадр: ${frameTime}мс")
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

### 4. Systrace и профилирование производительности

Android предоставляет инструменты для детального измерения производительности:

```kotlin
class SystemTraceExample {

    fun measurePerformance() {
        // Добавление секций трассировки
        Trace.beginSection("loadData")
        loadDataFromDatabase()
        Trace.endSection()

        Trace.beginSection("renderUI")
        renderComplexUI()
        Trace.endSection()
    }

    private fun loadDataFromDatabase() {
        // Операции с базой данных
    }

    private fun renderComplexUI() {
        // Отрисовка UI
    }
}

// Просмотр в Systrace:
// adb shell atrace --async_start view gfx input
// (выполнение действий)
// adb shell atrace --async_stop > trace.html
```

### 5. Метрики сложности layout

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

// Использование
val analyzer = LayoutComplexityAnalyzer()
val metrics = analyzer.analyzeLayout(rootView)
Log.d("Layout", """
    Views: ${metrics.viewCount}
    Глубина: ${metrics.maxDepth}
    Сложность: ${metrics.complexity}
""".trimIndent())
```

### 6. Метрики перекомпоновки Jetpack Compose

В Compose производительность измеряется количеством перекомпоновок:

```kotlin
@Composable
fun RecompositionCounter() {
    val recompositions = remember { mutableStateOf(0) }

    SideEffect {
        recompositions.value++
    }

    Text("Перекомпоновок: ${recompositions.value}")
}

// Измерение перекомпоновок с метриками компилятора Compose
// В build.gradle:
// kotlinOptions {
//     freeCompilerArgs += [
//         "-P",
//         "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
//         project.buildDir.absolutePath + "/compose_metrics"
//     ]
// }
```

### 7. Инструменты мониторинга производительности

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
                        Всего: ${totalDuration}мс
                        Layout: ${layoutDuration}мс
                        Draw: ${drawDuration}мс
                        Потеряно: $dropCount
                    """.trimIndent())
                },
                Handler(Looper.getMainLooper())
            )
        }
    }
}
```

### 8. Бенчмаркинг с Macrobenchmark

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

### 9. Пользовательские метрики производительности

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

        // Фаза measure
        measureTime = measureTime {
            view.measure(
                View.MeasureSpec.UNSPECIFIED,
                View.MeasureSpec.UNSPECIFIED
            )
        }

        // Фаза layout
        layoutTime = measureTime {
            view.layout(0, 0, view.measuredWidth, view.measuredHeight)
        }

        // Фаза draw (приблизительно)
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

### 10. Пороговые значения производительности

```kotlin
object PerformanceThresholds {
    // Целевое время кадров
    const val TARGET_60FPS_MS = 16.67
    const val TARGET_90FPS_MS = 11.11
    const val TARGET_120FPS_MS = 8.33

    // Целевые значения фаз (для 60fps)
    const val MAX_MEASURE_MS = 5.0
    const val MAX_LAYOUT_MS = 5.0
    const val MAX_DRAW_MS = 6.67

    // Лимиты сложности
    const val MAX_VIEW_HIERARCHY_DEPTH = 10
    const val MAX_VIEWS_PER_LAYOUT = 80

    // Лимиты перекомпоновок (Compose)
    const val MAX_RECOMPOSITIONS_PER_FRAME = 10

    fun checkPerformance(metrics: RenderMetrics): PerformanceReport {
        return PerformanceReport(
            isWithinBudget = metrics.totalTimeMs <= TARGET_60FPS_MS,
            warnings = buildList {
                if (metrics.measureTimeMs > MAX_MEASURE_MS) {
                    add("Фаза measure слишком медленная: ${metrics.measureTimeMs}мс")
                }
                if (metrics.layoutTimeMs > MAX_LAYOUT_MS) {
                    add("Фаза layout слишком медленная: ${metrics.layoutTimeMs}мс")
                }
                if (metrics.drawTimeMs > MAX_DRAW_MS) {
                    add("Фаза draw слишком медленная: ${metrics.drawTimeMs}мс")
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

### Резюме: ключевые метрики производительности

| Метрика | Единица | Цель (60fps) |
|--------|------|----------------|
| Время кадра | миллисекунды | < 16.67мс |
| Фаза measure | миллисекунды | < 5мс |
| Фаза layout | миллисекунды | < 5мс |
| Фаза draw | миллисекунды | < 6.67мс |
| Количество перекомпоновок | число | Минимизировать |
| Глубина иерархии view | уровни | < 10 |
| Всего views | количество | < 80 |

### Лучшие практики

1. **Мониторинг времени кадров** - Держать ниже 16.67мс для 60fps
2. **Минимизация перекомпоновок** в Compose
3. **Упрощение иерархии view** - Уменьшение глубины
4. **Использование ConstraintLayout** - Избегать вложенных layouts
5. **Профилирование с Systrace** - Выявление узких мест
6. **Пакетирование обновлений** - Избегать множественных инвалидаций

### Дополнительные метрики и инструменты

**Инструменты профилирования**:
- **Android Profiler** в Android Studio для анализа в реальном времени
- **Systrace** для детальной трассировки системных событий
- **Perfetto** для расширенного анализа производительности
- **Layout Inspector** для визуализации иерархии view
- **Macrobenchmark** для тестирования производительности приложения

**Дополнительные метрики**:
```kotlin
// Метрики памяти для layout
class LayoutMemoryMetrics {
    fun measureMemoryUsage(view: View): MemoryInfo {
        val runtime = Runtime.getRuntime()
        val beforeMemory = runtime.totalMemory() - runtime.freeMemory()

        // Инфляция layout
        val inflatedView = LayoutInflater.from(context)
            .inflate(R.layout.complex_layout, null)

        val afterMemory = runtime.totalMemory() - runtime.freeMemory()
        val memoryUsed = (afterMemory - beforeMemory) / 1024 / 1024 // MB

        return MemoryInfo(
            memoryUsedMb = memoryUsed,
            viewCount = countViews(inflatedView)
        )
    }

    data class MemoryInfo(
        val memoryUsedMb: Long,
        val viewCount: Int
    )
}

// Метрики overdraw
class OverdrawAnalyzer {
    fun analyzeOverdraw(view: View): OverdrawMetrics {
        var overdrawCount = 0

        fun checkOverdraw(v: View) {
            if (v.background != null) overdrawCount++
            if (v is ViewGroup) {
                for (i in 0 until v.childCount) {
                    checkOverdraw(v.getChildAt(i))
                }
            }
        }

        checkOverdraw(view)

        return OverdrawMetrics(
            backgroundLayers = overdrawCount,
            severity = when {
                overdrawCount < 3 -> "Низкий"
                overdrawCount < 5 -> "Средний"
                else -> "Высокий"
            }
        )
    }

    data class OverdrawMetrics(
        val backgroundLayers: Int,
        val severity: String
    )
}
```

### Практические рекомендации по оптимизации

1. **Использование ViewStub для отложенной инфляции**
   ```kotlin
   val viewStub = findViewById<ViewStub>(R.id.stub)
   viewStub.inflate() // Только когда действительно нужно
   ```

2. **Merge tags для уменьшения иерархии**
   ```xml
   <merge xmlns:android="...">
       <TextView ... />
       <Button ... />
   </merge>
   ```

3. **Include для переиспользования layouts**
   ```xml
   <include layout="@layout/reusable_component" />
   ```

4. **RecyclerView вместо ScrollView с множеством элементов**
   - Переиспользование view holders
   - Ленивая загрузка данных
   - Оптимизированная отрисовка

5. **ConstraintLayout для плоских иерархий**
   ```xml
   <androidx.constraintlayout.widget.ConstraintLayout>
       <!-- Все дочерние элементы на одном уровне -->
   </androidx.constraintlayout.widget.ConstraintLayout>
   ```

6. **Избегание вложенных весов в LinearLayout**
   ```kotlin
   // ПЛОХО: Вложенные LinearLayout с весами
   // ХОРОШО: ConstraintLayout с цепочками
   ```

### Итоговое резюме

Производительность layout в Android измеряется в:

- **Миллисекундах (мс)** для времени отрисовки (measure, layout, draw)
- **Кадрах в секунду (FPS)** для плавности анимаций
- **Количестве потерянных кадров** для стабильности
- **Количестве перекомпоновок** в Jetpack Compose
- **Сложности иерархии** (глубина и количество views)
- **Использовании памяти** для оптимизации ресурсов
- **Overdraw** для эффективности отрисовки

**Основные цели**:
- 60 FPS = 16.67мс на кадр
- 90 FPS = 11.11мс на кадр
- 120 FPS = 8.33мс на кадр

**Инструменты для измерения**:
- Android Profiler (Android Studio)
- Systrace / Perfetto
- Choreographer API
- FrameMetrics API
- Macrobenchmark
- Layout Inspector
- Compose Compiler Metrics

---

## Related Questions

### Related (Medium)
- [[q-compose-modifier-order-performance--android--medium]] - Performance
- [[q-macrobenchmark-startup--performance--medium]] - Performance
- [[q-performance-optimization-android--android--medium]] - Performance
- [[q-app-startup-optimization--android--medium]] - Performance
- [[q-baseline-profiles-optimization--android--medium]] - Performance

### Advanced (Harder)
- [[q-compose-lazy-layout-optimization--android--hard]] - Performance, View
- [[q-canvas-drawing-optimization--android--hard]] - Performance, View
- [[q-compose-custom-layout--android--hard]] - View
