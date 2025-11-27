---
id: android-053
title: Jank Detection and Frame Metrics / Обнаружение рывков и метрики кадров
aliases: [Jank Detection and Frame Metrics, Обнаружение рывков и метрики кадров]
topic: android
subtopics:
  - monitoring-slo
  - performance-rendering
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
source: Original
source_note: Frame rendering performance best practices
status: draft
moc: moc-android
related:
  - c-perfetto
  - c-performance
  - q-compose-gesture-detection--android--medium
  - q-mlkit-face-detection--android--medium
  - q-performance-monitoring-jank-compose--android--medium
created: 2025-10-11
updated: 2025-11-11
tags: [android/monitoring-slo, android/performance-rendering, difficulty/medium, en, ru]

date created: Saturday, November 1st 2025, 12:46:55 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---
# Вопрос (RU)
> Реализуйте мониторинг метрик кадров для обнаружения и исправления рывков. Используйте FrameMetricsAggregator, OnFrameMetricsAvailableListener и инструменты трассировки (Systrace/Perfetto) для выявления проблем рендеринга.

# Question (EN)
> Implement frame metrics monitoring to detect and fix jank. Use FrameMetricsAggregator, OnFrameMetricsAvailableListener, and Perfetto/System Trace tools to identify rendering issues.

## Ответ (RU)

### Обзор

Jank (рывки) возникает, когда приложение не успевает отрисовать кадр в пределах бюджета синхронизации экрана (например, ~16.67 мс при 60 Гц), что приводит к заметным подлагиваниям. На современных устройствах с 90 Гц (~11.11 мс) и 120 Гц (~8.33 мс) требования к производительности ещё выше.

Примеры бюджета кадра (на кадр):
- 60 Гц: 16.67 мс
- 90 Гц: 11.11 мс
- 120 Гц: 8.33 мс

Частые причины рывков:
1. Overdraw (многократная перерисовка одних и тех же пикселей)
2. Сложные и глубокие иерархии `View` (measure/layout дорогие)
3. Тяжёлые операции в `onDraw()`
4. Блокировка главного потока (I/O, вычисления)
5. Неэффективный `RecyclerView` (тяжёлый `onBindViewHolder()`)
6. Загрузка/декодирование крупных `Bitmap` в UI-потоке
7. Паузы GC и избыточные выделения памяти

### Реализация FrameMetricsAggregator

Примечание: `FrameMetricsAggregator` агрегирует длительности по миллисекундным "бакетам". Порог >16 мс актуален для 60 Гц; для дисплеев с 90/120 Гц порог должен быть ниже. Доступен начиная с API 24.

app/build.gradle.kts:
```kotlin
dependencies {
    implementation("androidx.metrics:metrics-performance:1.0.0")
}
```

#### 1. Базовый Мониторинг Метрик Кадров

```kotlin
class PerformanceMonitoringActivity : AppCompatActivity() {

    private var frameMetricsAggregator: FrameMetricsAggregator? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Запуск сбора метрик кадров для этого Activity
        frameMetricsAggregator = FrameMetricsAggregator()
        frameMetricsAggregator?.add(this)
    }

    override fun onResume() {
        super.onResume()
        // Опционально: сброс статистики при возврате экрана,
        // агрегатор остаётся добавленным, повторно add() не требуется
        frameMetricsAggregator?.reset()
    }

    override fun onPause() {
        super.onPause()

        // Анализ метрик для текущего экрана перед тем, как он станет невидимым
        frameMetricsAggregator?.let { aggregator ->
            val metricsArrays = aggregator.metrics
            val totalMetrics = metricsArrays?.get(FrameMetricsAggregator.TOTAL_INDEX)

            if (totalMetrics != null) {
                analyzeFrameMetrics(totalMetrics)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Останавливаем сбор, чтобы избежать утечек Activity
        frameMetricsAggregator?.stop()
        frameMetricsAggregator = null
    }

    private fun analyzeFrameMetrics(metrics: SparseIntArray) {
        var slowFrames = 0
        var frozenFrames = 0
        var totalFrames = 0

        for (i in 0 until metrics.size()) {
            val frameDurationMs = metrics.keyAt(i) // верхняя граница бакета в мс
            val frameCount = metrics.valueAt(i)

            totalFrames += frameCount

            // Медленный кадр (для 60 Гц): > 16 мс
            if (frameDurationMs > 16) {
                slowFrames += frameCount
            }

            // "Замороженный" кадр (Android vitals): > 700 мс
            if (frameDurationMs > 700) {
                frozenFrames += frameCount
            }
        }

        if (totalFrames == 0) return

        val slowFramePercentage = (slowFrames.toFloat() / totalFrames) * 100
        val frozenFramePercentage = (frozenFrames.toFloat() / totalFrames) * 100

        Log.d(
            "FrameMetrics",
            """
            Всего кадров: $totalFrames
            Медленных кадров: $slowFrames (${ "%.2f".format(slowFramePercentage)}%)
            Замороженных кадров: $frozenFrames (${ "%.2f".format(frozenFramePercentage)}%)
            """.trimIndent()
        )

        // Пример: репортим, если доля медленных кадров заметна
        if (slowFramePercentage > 5.0f) {
            reportJankToAnalytics(slowFramePercentage, frozenFramePercentage)
        }
    }

    private fun reportJankToAnalytics(
        slowFramePercentage: Float,
        frozenFramePercentage: Float
    ) {
        Firebase.analytics.logEvent("jank_detected") {
            param("screen", this@PerformanceMonitoringActivity.javaClass.simpleName)
            param("slow_frame_percentage", slowFramePercentage.toDouble())
            param("frozen_frame_percentage", frozenFramePercentage.toDouble())
        }
    }
}
```

#### 2. Мониторинг Кадров В Реальном Времени С `OnFrameMetricsAvailableListener`

```kotlin
class RealTimeFrameMonitor : AppCompatActivity() {

    private val frameMetricsListener = Window.OnFrameMetricsAvailableListener { _, frameMetrics, _ ->
        // FrameMetrics в колбэке уже содержит снимок для этого кадра
        val metrics = FrameMetrics(frameMetrics)

        val totalDurationNs = metrics.getMetric(FrameMetrics.TOTAL_DURATION)
        val totalDurationMs = totalDurationNs / 1_000_000.0

        val inputDurationMs =
            metrics.getMetric(FrameMetrics.INPUT_HANDLING_DURATION) / 1_000_000.0
        val animationDurationMs =
            metrics.getMetric(FrameMetrics.ANIMATION_DURATION) / 1_000_000.0
        val layoutDurationMs =
            metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
        val drawDurationMs =
            metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
        val syncDurationMs =
            metrics.getMetric(FrameMetrics.SYNC_DURATION) / 1_000_000.0
        val commandDurationMs =
            metrics.getMetric(FrameMetrics.COMMAND_ISSUE_DURATION) / 1_000_000.0

        // Порог для 60 Гц; для 90/120 Гц нужно уменьшить
        if (totalDurationMs > 16.67) {
            Log.w(
                "FrameMetrics",
                """
                Обнаружен медленный кадр: ${"%.2f".format(totalDurationMs)} мс
                Разбивка:
                - Input: ${"%.2f".format(inputDurationMs)} мс
                - Animation: ${"%.2f".format(animationDurationMs)} мс
                - Layout: ${"%.2f".format(layoutDurationMs)} мс
                - Draw: ${"%.2f".format(drawDurationMs)} мс
                - Sync: ${"%.2f".format(syncDurationMs)} мс
                - Command: ${"%.2f".format(commandDurationMs)} мс
                """.trimIndent()
            )

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

        window.addOnFrameMetricsAvailableListener(
            frameMetricsListener,
            Handler(Looper.getMainLooper())
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        window.removeOnFrameMetricsAvailableListener(frameMetricsListener)
    }

    private fun reportFrameBottleneck(bottleneck: String, durationMs: Double) {
        Firebase.analytics.logEvent("frame_bottleneck") {
            param("type", bottleneck)
            param("duration_ms", durationMs)
        }
    }
}
```

#### 3. Библиотека JankStats (современный подход)

```kotlin
dependencies {
    implementation("androidx.metrics:metrics-performance:1.0.0")
}

class ModernJankMonitor : AppCompatActivity() {

    private lateinit var jankStats: JankStats

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        jankStats = JankStats.createAndTrack(window) { frameData ->
            if (frameData.isJank) {
                val frameDurationMs = frameData.frameDurationUiNanos / 1_000_000.0

                Log.w(
                    "JankStats",
                    """
                    Обнаружен jank:
                    Длительность: ${"%.2f".format(frameDurationMs)} мс
                    Состояния: ${frameData.states.joinToString()}
                    """.trimIndent()
                )

                val currentState = frameData.states.lastOrNull() ?: "unknown"
                trackJankByState(currentState, frameDurationMs)
            }
        }
    }

    // Пример: помечаем состояние "scrolling" для лучшей атрибуции
    private fun setScrollingState(isScrolling: Boolean) {
        if (isScrolling) {
            jankStats.beginState("scrolling")
        } else {
            jankStats.endState("scrolling")
        }
    }

    private fun trackJankByState(state: String, durationMs: Double) {
        Firebase.analytics.logEvent("jank_by_state") {
            param("state", state)
            param("duration_ms", durationMs)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Отключаем сбор при уничтожении Activity, чтобы не собирать лишние метрики
        jankStats.isTrackingEnabled = false
    }
}
```

### Распространённые Причины И Исправления Рывков

#### 1. Overdraw

Проблема: Несколько фонов и перекрывающихся `View` приводят к лишней отрисовке пикселей.

```xml
<!-- Несколько background, вызывающих overdraw -->
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

Решение: Убирать лишние `background`, рисовать по возможности один слой.

```xml
<!-- Один слой background -->
<LinearLayout>

    <LinearLayout
        android:background="@color/light_gray">

        <TextView
            android:text="Hello" />
    </LinearLayout>
</LinearLayout>
```

Обнаружение overdraw:
- Developer Options → Debug GPU Overdraw → Show overdraw areas
- Синий: 1x (норма), зелёный: 2x (проверить), розовый: 3x (оптимизировать), красный: 4x+ (критично)

#### 2. Сложность Макета

Проблема: Глубоко вложенные макеты → тяжёлый `measure/layout`.

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
```

Решение: Уплощать иерархию с помощью `ConstraintLayout`.

```xml
<androidx.constraintlayout.widget.ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

#### 3. Рывки В RecyclerView

Проблема: Тяжёлый `onBindViewHolder` (синхронная декодировка изображений, сложное форматирование текста).

```kotlin
class SlowAdapter : RecyclerView.Adapter<ViewHolder>() {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        // ПЛОХО: синхронная декодировка в главном потоке
        val bitmap = BitmapFactory.decodeFile(item.imagePath)
        holder.imageView.setImageBitmap(bitmap)

        // ПЛОХО: сложное текстовое форматирование в UI-потоке
        val formattedText = complexTextFormatting(item.description)
        holder.textView.text = formattedText
    }

    private fun complexTextFormatting(text: String): Spanned {
        return Html.fromHtml(text, Html.FROM_HTML_MODE_LEGACY)
    }
}
```

Решение: Асинхронная загрузка и кэширование.

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val formattedTextCache = LruCache<String, Spanned>(100)

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        // Асинхронная загрузка изображений (например, Coil)
        holder.imageView.load(item.imagePath) {
            crossfade(true)
            placeholder(R.drawable.placeholder)
        }

        val cached = formattedTextCache.get(item.id)
        val formatted = cached ?: complexTextFormatting(item.description).also {
            formattedTextCache.put(item.id, it)
        }
        holder.textView.text = formatted
    }

    private fun complexTextFormatting(text: String): Spanned {
        return Html.fromHtml(text, Html.FROM_HTML_MODE_LEGACY)
    }

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

#### 4. Рывки При Инфляции `View`

Проблема: Инфляция тяжёлого layout по клику блокирует UI-поток.

```kotlin
button.setOnClickListener {
    val detailView = layoutInflater.inflate(
        R.layout.complex_detail_view,
        container,
        false
    )
    container.addView(detailView)
}
```

Решение: Использовать `ViewStub` для ленивой инфляции.

```xml
<FrameLayout>
    <ViewStub
        android:id="@+id/detail_view_stub"
        android:layout="@layout/complex_detail_view"
        android:inflatedId="@+id/detail_view" />
</FrameLayout>
```

```kotlin
button.setOnClickListener {
    val viewStub = findViewById<ViewStub>(R.id.detail_view_stub)
    val detailView = viewStub?.inflate() ?: findViewById(R.id.detail_view)
    // Настройка detailView...
}
```

### Анализ С Помощью Systrace / Perfetto

Используйте System Trace / Perfetto (в Android Studio) или `perfetto` CLI вместо устаревшего `systrace.py`. Если используется Systrace, общая логика работы аналогична.

Пример захвата (устаревший Systrace):

```bash
python $ANDROID_HOME/platform-tools/systrace/systrace.py \
    --time=10 \
    -o trace.html \
    -a com.example.myapp \
    sched gfx view wm am app

chrome trace.html
```

На что смотреть:
1. Пропуски дедлайнов кадров (красные/жёлтые кадры)
2. Долгий `measure/layout` (> ~8 мс) → сложная иерархия
3. Дорогой `draw` (> ~8 мс) → тяжёлый кастомный рендеринг/overdraw
4. Паузы GC во время рендера
5. Долгие операции в главном потоке

Пример:

```text
Frame 145: 28 ms (JANK - missed deadline)
 Input: 0.2 ms
 Animation: 0.5 ms
 Measure/Layout: 14.3 ms (slow)
   RecyclerView.onMeasure: 12.8 ms
      Adapter.onBindViewHolder: 11.2 ms (bottleneck)
 Draw: 8.1 ms (slow)
 Sync: 4.9 ms

Action: Move expensive onBindViewHolder work off main thread.
```

### Мониторинг В Продакшене

Пример с Firebase Performance и `FrameMetricsAggregator`:

```kotlin
class MainActivity : AppCompatActivity() {

    private val frameMetricsMonitor = FrameMetricsMonitor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

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
            val totalMetrics = aggregator.metrics?.get(FrameMetricsAggregator.TOTAL_INDEX)

            if (totalMetrics != null) {
                val stats = calculateFrameStats(totalMetrics)

                if (stats.totalFrames > 0) {
                    val trace = performanceMonitoring.newTrace("screen_rendering")
                    trace.putMetric("slow_frames", stats.slowFrames.toLong())
                    trace.putMetric("frozen_frames", stats.frozenFrames.toLong())
                    trace.putMetric("total_frames", stats.totalFrames.toLong())
                    trace.putMetric(
                        "slow_frame_percentage",
                        stats.slowFramePercentage.toLong()
                    )
                    trace.stop()
                }
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

        val slowFramePercentage = if (totalFrames > 0) {
            (slowFrames.toFloat() / totalFrames) * 100
        } else 0f

        return FrameStats(
            totalFrames = totalFrames,
            slowFrames = slowFrames,
            frozenFrames = frozenFrames,
            slowFramePercentage = slowFramePercentage
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

### Лучшие Практики

1. Стремиться как минимум к 60 FPS (и учитывать дисплеи с 90/120 Гц).
2. Тестировать на реальных устройствах, включая средний и низкий сегмент.
3. Мониторить производительность рендеринга в продакшене.
4. Упрощать иерархию `View`, использовать `ConstraintLayout`/Compose.
5. Минимизировать overdraw, избегать лишних фонов и перекрытий.
6. Оптимизировать `RecyclerView`: лёгкий `onBindViewHolder`, `DiffUtil`, prefetch.
7. Загружать изображения асинхронно (Coil/Glide/Picasso), не блокировать UI-поток.
8. Использовать `ViewStub` или ленивую инфляцию для редко используемых частей UI.
9. Сначала профилировать (System Trace/Perfetto, FrameMetrics, JankStats), затем оптимизировать.
10. Выносить тяжёлые операции из главного потока.
11. Избегать избыточных аллокаций во время анимаций и на горячих путях, чтобы снизить jank от GC.
12. Предпочитать современные тулкиты (Jetpack Compose + корректное профилирование), но всегда измерять.

### Распространённые Ошибки

1. Синхронная загрузка изображений в UI-потоке.
2. Тяжёлый и не оптимизированный `onDraw()` без кэширования.
3. Глубоко вложенные макеты, приводящие к медленному `measure/layout`.
4. Тяжёлый `onBindViewHolder()`.
5. Файловый/сетевой I/O в главном потоке.
6. Игнорирование индикаторов overdraw.
7. Использование огромных `Bitmap` без downsampling.
8. Блокировка анимаций неаппаратно-ускоренными свойствами.
9. Тестирование только на флагманских устройствах.

## Answer (EN)

### Overview

Jank occurs when the app fails to render frames within the device's vsync budget (e.g. ~16.67ms at 60Hz), causing visible stuttering. Modern devices support 90Hz (~11.11ms) or 120Hz (~8.33ms), so smooth rendering is even more critical.

Frame budget examples (per frame):
- 60 Hz: 16.67 ms
- 90 Hz: 11.11 ms
- 120 Hz: 8.33 ms

Common causes of jank:
1. Overdraw (rendering pixels multiple times)
2. Layout complexity (deep hierarchies, heavy measure/layout)
3. Expensive `onDraw()` operations
4. Main thread blocking (I/O, heavy computation)
5. Inefficient `RecyclerView` binding
6. Large `Bitmap` loading / decoding on UI thread
7. GC pauses and memory churn

### FrameMetricsAggregator Implementation

Note: `FrameMetricsAggregator` buckets durations in milliseconds. Thresholds below assume a 60Hz budget; for higher refresh rates, adjust accordingly. Available on API 24+.

app/build.gradle.kts:
```kotlin
dependencies {
    implementation("androidx.metrics:metrics-performance:1.0.0")
}
```

#### 1. Basic Frame Metrics Monitoring

```kotlin
class PerformanceMonitoringActivity : AppCompatActivity() {

    private var frameMetricsAggregator: FrameMetricsAggregator? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Start frame metrics collection for this Activity
        frameMetricsAggregator = FrameMetricsAggregator()
        frameMetricsAggregator?.add(this)
    }

    override fun onResume() {
        super.onResume()
        // Optional: reset stats when screen becomes visible again.
        // Aggregator remains added; no need to call add() again.
        frameMetricsAggregator?.reset()
    }

    override fun onPause() {
        super.onPause()

        // Analyze frame metrics for this screen session
        frameMetricsAggregator?.let { aggregator ->
            val metricsArrays = aggregator.metrics
            val totalMetrics = metricsArrays?.get(FrameMetricsAggregator.TOTAL_INDEX)

            if (totalMetrics != null) {
                analyzeFrameMetrics(totalMetrics)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Stop collecting to avoid leaking Activity
        frameMetricsAggregator?.stop()
        frameMetricsAggregator = null
    }

    private fun analyzeFrameMetrics(metrics: SparseIntArray) {
        var slowFrames = 0
        var frozenFrames = 0
        var totalFrames = 0

        for (i in 0 until metrics.size()) {
            val frameDurationMs = metrics.keyAt(i) // bucket upper bound in ms
            val frameCount = metrics.valueAt(i)

            totalFrames += frameCount

            // Slow frame (for 60Hz): > 16 ms
            if (frameDurationMs > 16) {
                slowFrames += frameCount
            }

            // Frozen frame (Android vitals definition): > 700 ms
            if (frameDurationMs > 700) {
                frozenFrames += frameCount
            }
        }

        if (totalFrames == 0) return

        val slowFramePercentage = (slowFrames.toFloat() / totalFrames) * 100
        val frozenFramePercentage = (frozenFrames.toFloat() / totalFrames) * 100

        Log.d(
            "FrameMetrics",
            """
            Total Frames: $totalFrames
            Slow Frames: $slowFrames (${ "%.2f".format(slowFramePercentage)}%)
            Frozen Frames: $frozenFrames (${ "%.2f".format(frozenFramePercentage)}%)
            """.trimIndent()
        )

        // Example: report when slow frames exceed threshold
        if (slowFramePercentage > 5.0f) {
            reportJankToAnalytics(slowFramePercentage, frozenFramePercentage)
        }
    }

    private fun reportJankToAnalytics(
        slowFramePercentage: Float,
        frozenFramePercentage: Float
    ) {
        Firebase.analytics.logEvent("jank_detected") {
            param("screen", this@PerformanceMonitoringActivity.javaClass.simpleName)
            param("slow_frame_percentage", slowFramePercentage.toDouble())
            param("frozen_frame_percentage", frozenFramePercentage.toDouble())
        }
    }
}
```

#### 2. Real-Time Frame Monitoring with `OnFrameMetricsAvailableListener`

```kotlin
class RealTimeFrameMonitor : AppCompatActivity() {

    private val frameMetricsListener = Window.OnFrameMetricsAvailableListener { _, frameMetrics, _ ->
        // FrameMetrics provided here is the snapshot for this frame
        val metrics = FrameMetrics(frameMetrics)

        // Analyze individual frame
        val totalDurationNs = metrics.getMetric(FrameMetrics.TOTAL_DURATION)
        val totalDurationMs = totalDurationNs / 1_000_000.0

        val inputDurationMs =
            metrics.getMetric(FrameMetrics.INPUT_HANDLING_DURATION) / 1_000_000.0
        val animationDurationMs =
            metrics.getMetric(FrameMetrics.ANIMATION_DURATION) / 1_000_000.0
        val layoutDurationMs =
            metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
        val drawDurationMs =
            metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
        val syncDurationMs =
            metrics.getMetric(FrameMetrics.SYNC_DURATION) / 1_000_000.0
        val commandDurationMs =
            metrics.getMetric(FrameMetrics.COMMAND_ISSUE_DURATION) / 1_000_000.0

        // Example threshold for 60Hz; adjust if targeting higher refresh rates.
        if (totalDurationMs > 16.67) {
            Log.w(
                "FrameMetrics",
                """
                Slow frame detected: ${"%.2f".format(totalDurationMs)} ms
                Breakdown:
                - Input: ${"%.2f".format(inputDurationMs)} ms
                - Animation: ${"%.2f".format(animationDurationMs)} ms
                - Layout: ${"%.2f".format(layoutDurationMs)} ms
                - Draw: ${"%.2f".format(drawDurationMs)} ms
                - Sync: ${"%.2f".format(syncDurationMs)} ms
                - Command: ${"%.2f".format(commandDurationMs)} ms
                """.trimIndent()
            )

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

        window.addOnFrameMetricsAvailableListener(
            frameMetricsListener,
            Handler(Looper.getMainLooper())
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        window.removeOnFrameMetricsAvailableListener(frameMetricsListener)
    }

    private fun reportFrameBottleneck(bottleneck: String, durationMs: Double) {
        Firebase.analytics.logEvent("frame_bottleneck") {
            param("type", bottleneck)
            param("duration_ms", durationMs)
        }
    }
}
```

#### 3. JankStats Library (Modern Approach)

```kotlin
dependencies {
    implementation("androidx.metrics:metrics-performance:1.0.0")
}

class ModernJankMonitor : AppCompatActivity() {

    private lateinit var jankStats: JankStats

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        jankStats = JankStats.createAndTrack(window) { frameData ->
            if (frameData.isJank) {
                val frameDurationMs = frameData.frameDurationUiNanos / 1_000_000.0

                Log.w(
                    "JankStats",
                    """
                    Jank detected:
                    Duration: ${"%.2f".format(frameDurationMs)} ms
                    States: ${frameData.states.joinToString()}
                    """.trimIndent()
                )

                val currentState = frameData.states.lastOrNull() ?: "unknown"
                trackJankByState(currentState, frameDurationMs)
            }
        }
    }

    // Example: mark scrolling state for better attribution
    private fun setScrollingState(isScrolling: Boolean) {
        if (isScrolling) {
            jankStats.beginState("scrolling")
        } else {
            jankStats.endState("scrolling")
        }
    }

    private fun trackJankByState(state: String, durationMs: Double) {
        Firebase.analytics.logEvent("jank_by_state") {
            param("state", state)
            param("duration_ms", durationMs)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Disable tracking when Activity is destroyed
        jankStats.isTrackingEnabled = false
    }
}
```

### Common Jank Causes and Fixes

#### 1. Overdraw

Problem: Multiple backgrounds and overlapping `View`s cause redundant pixel rendering.

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

Fix: Remove unnecessary backgrounds; prefer a single background layer when possible.

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

Detecting overdraw:
- Developer Options → Debug GPU Overdraw → Show overdraw areas
- Blue: 1x (OK), green: 2x (review), pink: 3x (optimize), red: 4x+ (critical)

#### 2. Layout Complexity

Problem: Deeply nested layouts lead to expensive `measure/layout`.

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
```

Fix: Flatten hierarchy using `ConstraintLayout`.

```xml
<androidx.constraintlayout.widget.ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

#### 3. RecyclerView Jank

Problem: Heavy `onBindViewHolder` (e.g. synchronous image decoding, complex text formatting).

```kotlin
class SlowAdapter : RecyclerView.Adapter<ViewHolder>() {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        // BAD: synchronous decode on main thread
        val bitmap = BitmapFactory.decodeFile(item.imagePath)
        holder.imageView.setImageBitmap(bitmap)

        // BAD: complex text formatting on UI thread
        val formattedText = complexTextFormatting(item.description)
        holder.textView.text = formattedText
    }

    private fun complexTextFormatting(text: String): Spanned {
        return Html.fromHtml(text, Html.FROM_HTML_MODE_LEGACY)
    }
}
```

Fix: Use async loading and caching.

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val formattedTextCache = LruCache<String, Spanned>(100)

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]

        // Async image loading (e.g., Coil)
        holder.imageView.load(item.imagePath) {
            crossfade(true)
            placeholder(R.drawable.placeholder)
        }

        val cached = formattedTextCache.get(item.id)
        val formatted = cached ?: complexTextFormatting(item.description).also {
            formattedTextCache.put(item.id, it)
        }
        holder.textView.text = formatted
    }

    private fun complexTextFormatting(text: String): Spanned {
        return Html.fromHtml(text, Html.FROM_HTML_MODE_LEGACY)
    }

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

#### 4. `View` Inflation Jank

Problem: Inflating a heavy layout on click blocks the UI thread.

```kotlin
button.setOnClickListener {
    val detailView = layoutInflater.inflate(
        R.layout.complex_detail_view,
        container,
        false
    )
    container.addView(detailView)
}
```

Fix: Use `ViewStub` for lazy inflation.

```xml
<FrameLayout>
    <ViewStub
        android:id="@+id/detail_view_stub"
        android:layout="@layout/complex_detail_view"
        android:inflatedId="@+id/detail_view" />
</FrameLayout>
```

```kotlin
button.setOnClickListener {
    val viewStub = findViewById<ViewStub>(R.id.detail_view_stub)
    val detailView = viewStub?.inflate() ?: findViewById(R.id.detail_view)
    // Configure detailView...
}
```

### Analysis with Systrace / Perfetto

Prefer using System Trace / Perfetto (via Android Studio or `perfetto` CLI) instead of deprecated `systrace.py`. For Systrace, the overall workflow is similar.

Example capture (legacy Systrace):

```bash
python $ANDROID_HOME/platform-tools/systrace/systrace.py \
    --time=10 \
    -o trace.html \
    -a com.example.myapp \
    sched gfx view wm am app

chrome trace.html
```

What to look for:
1. Missed frame deadlines (red/yellow frames)
2. Long `measure/layout` (> ~8 ms) → complex hierarchy
3. Expensive `draw` (> ~8 ms) → heavy custom rendering/overdraw
4. GC pauses during rendering
5. Long-running work on main thread

Example snippet:

```text
Frame 145: 28 ms (JANK - missed deadline)
 Input: 0.2 ms
 Animation: 0.5 ms
 Measure/Layout: 14.3 ms (slow)
   RecyclerView.onMeasure: 12.8 ms
      Adapter.onBindViewHolder: 11.2 ms (bottleneck)
 Draw: 8.1 ms (slow)
 Sync: 4.9 ms

Action: Move expensive onBindViewHolder work off main thread.
```

### Production Monitoring

Example using Firebase Performance with `FrameMetricsAggregator`:

```kotlin
class MainActivity : AppCompatActivity() {

    private val frameMetricsMonitor = FrameMetricsMonitor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

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
            val totalMetrics = aggregator.metrics?.get(FrameMetricsAggregator.TOTAL_INDEX)

            if (totalMetrics != null) {
                val stats = calculateFrameStats(totalMetrics)

                if (stats.totalFrames > 0) {
                    val trace = performanceMonitoring.newTrace("screen_rendering")
                    trace.putMetric("slow_frames", stats.slowFrames.toLong())
                    trace.putMetric("frozen_frames", stats.frozenFrames.toLong())
                    trace.putMetric("total_frames", stats.totalFrames.toLong())
                    trace.putMetric(
                        "slow_frame_percentage",
                        stats.slowFramePercentage.toLong()
                    )
                    trace.stop()
                }
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

        val slowFramePercentage = if (totalFrames > 0) {
            (slowFrames.toFloat() / totalFrames) * 100
        } else 0f

        return FrameStats(
            totalFrames = totalFrames,
            slowFrames = slowFrames,
            frozenFrames = frozenFrames,
            slowFramePercentage = slowFramePercentage
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

1. Target at least 60 FPS; consider 90/120Hz devices.
2. Profile on real devices, including mid/low-end hardware.
3. Monitor rendering performance in production.
4. Flatten view hierarchies; use `ConstraintLayout`/Compose.
5. Reduce overdraw; avoid redundant backgrounds and overlapping views.
6. Optimize `RecyclerView`: lightweight `onBindViewHolder`, `DiffUtil`, prefetching.
7. Load images asynchronously (Coil/Glide/Picasso); avoid blocking the main thread.
8. Use `ViewStub` or lazy loading for rarely shown UI.
9. Always profile first (System Trace/Perfetto, FrameMetrics, JankStats) before optimizing.
10. Move expensive work off the main thread.
11. Avoid excessive allocations during animations/hot paths to reduce GC jank.
12. Prefer modern toolkits (Jetpack Compose + profiling) but still measure.

### Common Pitfalls

1. Synchronous image loading on UI thread.
2. Heavy custom drawing in `onDraw()` without caching.
3. Deeply nested layouts causing slow `measure/layout`.
4. Expensive logic in `onBindViewHolder()`.
5. File/network I/O on main thread.
6. Ignoring overdraw indicators.
7. Using huge `Bitmap`s without downsampling.
8. Blocking animations with non-accelerated properties.
9. Testing only on flagship devices.

## Дополнительные Вопросы (RU)

1. Как интегрировать Perfetto/System Trace в CI-пайплайн для регулярного анализа jank?
2. Как измерять и оптимизировать jank в Jetpack Compose-сценариях (scrolling, lists, animations)?
3. Как использовать Firebase Performance или аналогичные инструменты для сбора метрик медленных/замороженных кадров в продакшене?
4. Какие подходы применимы для снижения GC-jank в анимациях и интенсивном скролле?
5. Как учитывать разные частоты обновления экрана (60/90/120 Гц) при конфигурировании порогов обнаружения jank?

## Follow-ups

1. How can you integrate Perfetto/System Trace into a CI pipeline to regularly detect jank regressions?
2. How do you measure and reduce jank in Jetpack Compose-heavy screens (scrolling, lists, animations)?
3. How can Firebase Performance or similar tools be used to track slow/frozen frames in production?
4. What techniques help reduce GC-induced jank during animations and intensive scrolling?
5. How should detection thresholds be tuned for devices with different refresh rates (60/90/120Hz)?

## Ссылки (RU)

- https://developer.android.com/jetpack/androidx/releases/metrics
- https://developer.android.com/reference/android/view/FrameMetrics
- https://developer.android.com/topic/performance/vitals/render
- https://developer.android.com/topic/performance/tracing

## References

- https://developer.android.com/jetpack/androidx/releases/metrics
- https://developer.android.com/reference/android/view/FrameMetrics
- https://developer.android.com/topic/performance/vitals/render
- https://developer.android.com/topic/performance/tracing

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-perfetto]]
- [[c-performance]]

### Предпосылки (проще)

- [[q-recyclerview-sethasfixedsize--android--easy]] - RecyclerView

### Связанные (средний уровень)

- [[q-memory-leak-detection--android--medium]] - Performance

### Продвинутые (сложнее)

- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose

## Related Questions

### Prerequisites / Concepts

- [[c-perfetto]]
- [[c-performance]]

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview

### Related (Medium)
- [[q-memory-leak-detection--android--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
