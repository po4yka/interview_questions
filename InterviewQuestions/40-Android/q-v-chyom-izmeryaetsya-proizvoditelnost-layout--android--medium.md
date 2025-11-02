---
id: android-391
title: "В чём измеряется производительность layout / How is layout performance measured"
aliases: ["В чём измеряется производительность layout", "How is layout performance measured", "Layout performance metrics", "Метрики производительности layout"]
topic: android
subtopics: [performance-rendering, ui-views, profiling]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-main-causes-ui-lag--android--medium, c-choreographer, c-systrace]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android, android/performance-rendering, android/ui-views, android/profiling, performance, rendering, frame-timing, difficulty/medium]
---

# Вопрос (RU)

> В чём измеряется производительность layout в Android?

# Question (EN)

> How is layout performance measured in Android?

---

## Ответ (RU)

Производительность layout измеряется в **миллисекундах (ms)** времени отрисовки каждого кадра. Android отрисовывает UI в три фазы: **measure**, **layout**, **draw**. Для плавной работы весь кадр должен укладываться в бюджет времени (16.67ms для 60fps, 11.11ms для 90fps).

### Основные метрики

**Целевое время кадра:**
- 60 FPS → 16.67ms на кадр
- 90 FPS → 11.11ms на кадр
- 120 FPS → 8.33ms на кадр

**Бюджет по фазам (для 60fps):**
- Measure: до 5ms
- Layout: до 5ms
- Draw: до 6.67ms

### 1. Измерение через Choreographer

`Choreographer` синхронизирует анимации с частотой обновления экрана:

```kotlin
class FrameMonitor {
    private val choreographer = Choreographer.getInstance()
    private var lastFrameTime = 0L

    fun start() {
        choreographer.postFrameCallback(frameCallback)
    }

    private val frameCallback = object : Choreographer.FrameCallback {
        override fun doFrame(frameTimeNanos: Long) {
            if (lastFrameTime != 0L) {
                val frameTime = (frameTimeNanos - lastFrameTime) / 1_000_000.0

                if (frameTime > 16.67) {
                    // ❌ Пропущен кадр
                    Log.w("Frame", "Slow frame: ${frameTime}ms")
                } else {
                    // ✅ Кадр в пределах нормы
                }
            }
            lastFrameTime = frameTimeNanos
            choreographer.postFrameCallback(this) // Следующий кадр
        }
    }
}
```

### 2. Измерение фаз через FrameMetrics (API 24+)

```kotlin
class DetailedFrameMonitor(activity: Activity) {

    init {
        activity.window.addOnFrameMetricsAvailableListener(
            { _, metrics, _ ->
                val total = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
                val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
                val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0

                // ✅ Детальная статистика по фазам
                Log.d("Metrics", "Total: ${total}ms, Layout: ${layout}ms, Draw: ${draw}ms")
            },
            Handler(Looper.getMainLooper())
        )
    }
}
```

### 3. Трассировка через Trace API

```kotlin
class OptimizedView : View(context) {

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        Trace.beginSection("OptimizedView:measure") // ✅ Начало секции
        super.onMeasure(widthSpec, heightSpec)
        Trace.endSection() // ✅ Конец секции
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        Trace.beginSection("OptimizedView:layout")
        super.onLayout(changed, l, t, r, b)
        Trace.endSection()
    }
}
```

Просмотр трассировки:
```bash
# Запуск трассировки
adb shell atrace --async_start view gfx input

# Остановка и сохранение
adb shell atrace --async_stop > trace.html
```

### 4. Анализ сложности иерархии

```kotlin
data class LayoutComplexity(
    val viewCount: Int,
    val maxDepth: Int
)

fun analyzeHierarchy(view: View): LayoutComplexity {
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

    return LayoutComplexity(viewCount, maxDepth).also {
        if (it.maxDepth > 10) {
            // ❌ Слишком глубокая иерархия
            Log.w("Layout", "Deep hierarchy: ${it.maxDepth} levels")
        }
        if (it.viewCount > 80) {
            // ❌ Слишком много view
            Log.w("Layout", "Too many views: ${it.viewCount}")
        }
    }
}
```

### 5. Recomposition в Jetpack Compose

В Compose производительность измеряется количеством recomposition:

```kotlin
@Composable
fun MonitoredComposable() {
    val recompositions = remember { mutableStateOf(0) }

    SideEffect {
        recompositions.value++ // ✅ Считаем перекомпоновки
    }

    Text("Recompositions: ${recompositions.value}")
}
```

Включение метрик в `build.gradle.kts`:
```kotlin
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
        "${project.buildDir}/compose_metrics"
    )
}
```

### Таблица метрик производительности

| Метрика | Единица | Целевое значение (60fps) |
|---------|---------|--------------------------|
| Время кадра | ms | < 16.67 |
| Measure | ms | < 5 |
| Layout | ms | < 5 |
| Draw | ms | < 6.67 |
| Глубина иерархии | уровни | < 10 |
| Количество View | шт. | < 80 |
| Recomposition | количество | минимизировать |

---

## Answer (EN)

Layout performance is measured in **milliseconds (ms)** of frame rendering time. Android renders UI in three phases: **measure**, **layout**, **draw**. For smooth operation, each frame must fit within the time budget (16.67ms for 60fps, 11.11ms for 90fps).

### Key Metrics

**Target frame time:**
- 60 FPS → 16.67ms per frame
- 90 FPS → 11.11ms per frame
- 120 FPS → 8.33ms per frame

**Phase budget (for 60fps):**
- Measure: up to 5ms
- Layout: up to 5ms
- Draw: up to 6.67ms

### 1. Measuring with Choreographer

`Choreographer` synchronizes animations with screen refresh rate:

```kotlin
class FrameMonitor {
    private val choreographer = Choreographer.getInstance()
    private var lastFrameTime = 0L

    fun start() {
        choreographer.postFrameCallback(frameCallback)
    }

    private val frameCallback = object : Choreographer.FrameCallback {
        override fun doFrame(frameTimeNanos: Long) {
            if (lastFrameTime != 0L) {
                val frameTime = (frameTimeNanos - lastFrameTime) / 1_000_000.0

                if (frameTime > 16.67) {
                    // ❌ Dropped frame
                    Log.w("Frame", "Slow frame: ${frameTime}ms")
                } else {
                    // ✅ Frame within budget
                }
            }
            lastFrameTime = frameTimeNanos
            choreographer.postFrameCallback(this) // Next frame
        }
    }
}
```

### 2. Measuring Phases with FrameMetrics (API 24+)

```kotlin
class DetailedFrameMonitor(activity: Activity) {

    init {
        activity.window.addOnFrameMetricsAvailableListener(
            { _, metrics, _ ->
                val total = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
                val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
                val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0

                // ✅ Detailed phase statistics
                Log.d("Metrics", "Total: ${total}ms, Layout: ${layout}ms, Draw: ${draw}ms")
            },
            Handler(Looper.getMainLooper())
        )
    }
}
```

### 3. Tracing with Trace API

```kotlin
class OptimizedView : View(context) {

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        Trace.beginSection("OptimizedView:measure") // ✅ Start section
        super.onMeasure(widthSpec, heightSpec)
        Trace.endSection() // ✅ End section
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        Trace.beginSection("OptimizedView:layout")
        super.onLayout(changed, l, t, r, b)
        Trace.endSection()
    }
}
```

Viewing traces:
```bash
# Start tracing
adb shell atrace --async_start view gfx input

# Stop and save
adb shell atrace --async_stop > trace.html
```

### 4. Analyzing Hierarchy Complexity

```kotlin
data class LayoutComplexity(
    val viewCount: Int,
    val maxDepth: Int
)

fun analyzeHierarchy(view: View): LayoutComplexity {
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

    return LayoutComplexity(viewCount, maxDepth).also {
        if (it.maxDepth > 10) {
            // ❌ Hierarchy too deep
            Log.w("Layout", "Deep hierarchy: ${it.maxDepth} levels")
        }
        if (it.viewCount > 80) {
            // ❌ Too many views
            Log.w("Layout", "Too many views: ${it.viewCount}")
        }
    }
}
```

### 5. Recomposition in Jetpack Compose

In Compose, performance is measured by recomposition count:

```kotlin
@Composable
fun MonitoredComposable() {
    val recompositions = remember { mutableStateOf(0) }

    SideEffect {
        recompositions.value++ // ✅ Count recompositions
    }

    Text("Recompositions: ${recompositions.value}")
}
```

Enable metrics in `build.gradle.kts`:
```kotlin
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
        "${project.buildDir}/compose_metrics"
    )
}
```

### Performance Metrics Table

| Metric | Unit | Target (60fps) |
|--------|------|----------------|
| Frame time | ms | < 16.67 |
| Measure | ms | < 5 |
| Layout | ms | < 5 |
| Draw | ms | < 6.67 |
| Hierarchy depth | levels | < 10 |
| View count | count | < 80 |
| Recomposition | count | minimize |

---

## Follow-ups

1. How does ConstraintLayout improve performance compared to nested LinearLayouts?
2. What causes jank and how to detect it with Android Profiler?
3. How do Compose recomposition scopes affect performance?
4. When should you use `Trace.beginSection()` vs Android Studio Profiler?
5. What's the difference between Macrobenchmark and Microbenchmark for layout testing?

## References

- [[c-choreographer]] - Frame timing synchronization
- [[c-systrace]] - System-wide tracing tool
- [[c-android-profiler]] - Performance profiling tool
- [Android Performance Patterns](https://developer.android.com/topic/performance)
- [FrameMetrics API](https://developer.android.com/reference/android/view/FrameMetrics)
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-view-lifecycle--android--easy]]
- [[q-recyclerview-sethasfixedsize--android--easy]]

### Related (Same Level)
- [[q-main-causes-ui-lag--android--medium]]
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]]
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]]
- [[q-optimize-complex-recyclerview--android--hard]]
