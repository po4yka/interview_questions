---
id: android-391
title: "В чём измеряется производительность layout / How is layout performance measured"
aliases: ["How is layout performance measured", "Layout performance metrics", "В чём измеряется производительность layout", "Метрики производительности layout"]
topic: android
subtopics: [performance-rendering, ui-views]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-android-performance-measurement-tools--android--medium]
created: 2024-10-15
updated: 2025-11-10
sources: []
tags: [android/performance-rendering, android/ui-views, difficulty/medium, performance/rendering]

date created: Saturday, November 1st 2025, 1:24:44 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---
# Вопрос (RU)

> В чём измеряется производительность layout в Android?

# Question (EN)

> How is layout performance measured in Android?

---

## Ответ (RU)

Производительность layout и отрисовки измеряется в **миллисекундах (ms)** на каждый кадр и на выполнение фаз **measure**, **layout**, **draw** внутри кадра. Основной ориентир — укладываться в бюджет времени кадра (примерно 16.67ms для 60fps, 11.11ms для 90fps, 8.33ms для 120fps). Если суммарное время measure/layout/draw (вместе с остальной работой на UI-потоке) выходит за этот бюджет, появляются задержки и jank.

См. также: [[c-android]].

### Основные Метрики

**Целевое время кадра:**
- 60 FPS → ~16.67ms на кадр
- 90 FPS → ~11.11ms на кадр
- 120 FPS → ~8.33ms на кадр

**Время фаз (для 60fps, ориентировочно):**
- Measure: желательно до ~5ms
- Layout: желательно до ~5ms
- Draw: желательно до ~6.67ms

Эти значения — практические ориентиры, а не жёсткие правила платформы: важен суммарный бюджет кадра, стабильность FPS и отсутствие пропусков кадров.

### 1. Измерение Через `Choreographer`

`Choreographer` синхронизирует анимации с частотой обновления экрана и позволяет измерять интервал между кадрами (общую длительность кадра), но не даёт по отдельности времена measure/layout/draw:

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
                    // Медленный кадр, возможен jank или пропуск кадра
                    Log.w("Frame", "Slow frame: ${frameTime}ms")
                } else {
                    // Кадр в пределах целевого бюджета
                }
            }
            lastFrameTime = frameTimeNanos
            choreographer.postFrameCallback(this) // Следующий кадр
        }
    }
}
```

### 2. Измерение Фаз Через `FrameMetrics` (API 24+)

```kotlin
class DetailedFrameMonitor(activity: Activity) {

    init {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            activity.window.addOnFrameMetricsAvailableListener(
                { _, metrics, _ ->
                    val total = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
                    val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
                    val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0

                    // Детальная статистика по фазам рендеринга
                    Log.d("Metrics", "Total: ${total}ms, Layout+Measure: ${layout}ms, Draw: ${draw}ms")
                },
                Handler(Looper.getMainLooper())
            )
            // В реальном коде важно удалить listener при уничтожении Activity
        }
    }
}
```

### 3. Трассировка Через `Trace` API

```kotlin
class OptimizedView(context: Context) : View(context) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        Trace.beginSection("OptimizedView:measure")
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
        Trace.endSection()
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        Trace.beginSection("OptimizedView:layout")
        super.onLayout(changed, left, top, right, bottom)
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

### 4. Анализ Сложности Иерархии

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
            // Эвристика: слишком глубокая иерархия может давать накладные расходы
            Log.w("Layout", "Deep hierarchy (heuristic): ${it.maxDepth} levels")
        }
        if (it.viewCount > 80) {
            // Эвристика: слишком много view, проверьте необходимость
            Log.w("Layout", "Too many views (heuristic): ${it.viewCount}")
        }
    }
}
```

Пороговые значения для глубины и количества `View` — эвристики: они зависят от устройства, экрана и конкретного UI.

### 5. Recomposition В Jetpack Compose

В Compose также важен бюджет кадра, но дополнительно анализируют, как часто и почему происходят recomposition. Количество перекомпозиций само по себе не является основной метрикой, но помогает выявить неэффективные участки.

Важно: измерять количество recomposition нужно так, чтобы не создавать новых состояний, которые сами вызывают дополнительные recomposition. Пример (диагностический, упрощённый):

```kotlin
@Composable
fun MonitoredComposable() {
    var recompositions by remember { mutableStateOf(0) }

    // Этот блок будет вызываться при каждой композиции/перекомпозиции
    SideEffect {
        recompositions++
    }

    Text("Recompositions (approx): ${recompositions}")
}
```

В реальных проектах лучше использовать инструменты профилирования Compose и отчёты компилятора, а не ручные счётчики. Пример включения вывода отчётов (флаг как иллюстрация):

```kotlin
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${'$'}{project.buildDir}/compose_metrics"
    )
}
```

### Таблица Метрик Производительности

| Метрика | Единица | Целевое значение (60fps) |
|---------|---------|--------------------------|
| Время кадра | ms | < 16.67 (стабильно) |
| Measure | ms | ориентир < ~5 |
| Layout | ms | ориентир < ~5 |
| Draw | ms | ориентир < ~6.67 |
| Глубина иерархии | уровни | эвристика, чаще < 10 |
| Количество `View` | шт. | эвристика, чаще < 80 |
| Recomposition | количество | избегать лишних |

---

## Answer (EN)

Layout and rendering performance is measured in **milliseconds (ms)** per frame and by how long the **measure**, **layout**, and **draw** phases take within each frame. The key goal is to stay within the frame time budget (about 16.67ms for 60fps, 11.11ms for 90fps, 8.33ms for 120fps). If total measure/layout/draw time (plus other UI thread work) exceeds this budget, you get delays and jank.

See also: [[c-android]].

### Key Metrics

**Target frame time:**
- 60 FPS → ~16.67ms per frame
- 90 FPS → ~11.11ms per frame
- 120 FPS → ~8.33ms per frame

**Phase timing (for 60fps, indicative):**
- Measure: ideally up to ~5ms
- Layout: ideally up to ~5ms
- Draw: ideally up to ~6.67ms

These are practical guidelines, not strict platform rules; what matters is total frame budget, stable FPS, and avoiding dropped frames.

### 1. Measuring with `Choreographer`

`Choreographer` synchronizes animations with the display refresh rate and can be used to measure the time between frames (overall frame duration). It does not by itself break down measure/layout/draw durations:

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
                    // Slow frame, potential jank or dropped frame(s)
                    Log.w("Frame", "Slow frame: ${frameTime}ms")
                } else {
                    // Frame within target budget
                }
            }
            lastFrameTime = frameTimeNanos
            choreographer.postFrameCallback(this) // Next frame
        }
    }
}
```

### 2. Measuring Phases with `FrameMetrics` (API 24+)

```kotlin
class DetailedFrameMonitor(activity: Activity) {

    init {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            activity.window.addOnFrameMetricsAvailableListener(
                { _, metrics, _ ->
                    val total = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
                    val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
                    val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0

                    // Detailed rendering phase statistics
                    Log.d("Metrics", "Total: ${total}ms, Layout+Measure: ${layout}ms, Draw: ${draw}ms")
                },
                Handler(Looper.getMainLooper())
            )
            // In real code, remove the listener when the Activity is destroyed
        }
    }
}
```

### 3. Tracing with `Trace` API

```kotlin
class OptimizedView(context: Context) : View(context) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        Trace.beginSection("OptimizedView:measure")
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
        Trace.endSection()
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        Trace.beginSection("OptimizedView:layout")
        super.onLayout(changed, left, top, right, bottom)
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
            // Heuristic: deep hierarchy may add overhead
            Log.w("Layout", "Deep hierarchy (heuristic): ${it.maxDepth} levels")
        }
        if (it.viewCount > 80) {
            // Heuristic: many views, verify necessity
            Log.w("Layout", "Too many views (heuristic): ${it.viewCount}")
        }
    }
}
```

These thresholds are heuristics; actual limits depend on device performance, screen size, and UI complexity.

### 5. Recomposition in Jetpack Compose

In Compose, you still care about frame time, and you also look at how often and why recompositions occur. Recomposition count is a diagnostic signal, not the primary performance metric by itself.

It is important to track recompositions without introducing extra state writes that themselves cause additional recompositions. Example (simplified for diagnostics):

```kotlin
@Composable
fun MonitoredComposable() {
    var recompositions by remember { mutableStateOf(0) }

    // This block runs after every successful composition/recomposition
    SideEffect {
        recompositions++
    }

    Text("Recompositions (approx): ${recompositions}")
}
```

For real-world analysis, prefer Compose profiling tools and compiler metrics instead of manual counters. Example flag (illustrative):

```kotlin
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${'$'}{project.buildDir}/compose_metrics"
    )
}
```

### Performance Metrics Table

| Metric | Unit | Target (60fps) |
|--------|------|----------------|
| Frame time | ms | < 16.67 (stable) |
| Measure | ms | guideline < ~5 |
| Layout | ms | guideline < ~5 |
| Draw | ms | guideline < ~6.67 |
| Hierarchy depth | levels | heuristic, often < 10 |
| `View` count | count | heuristic, often < 80 |
| Recomposition | count | avoid unnecessary |

---

## Follow-ups

1. How does `ConstraintLayout` affect measure/layout performance compared to nested `LinearLayout`s?
2. How can you detect and analyze jank using Android performance tooling?
3. How do recomposition scopes and `remember` usage in Compose impact frame time?
4. When is it better to instrument code with `Trace.beginSection()` vs relying only on Android Studio profiling tools?
5. How can `Layout Inspector` and `Profileable` apps help in diagnosing layout performance issues?

## References

- [Android Performance Patterns](https://developer.android.com/topic/performance)
- [FrameMetrics API](https://developer.android.com/reference/android/view/FrameMetrics)
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]]

### Related (Same Level)
- [[q-main-causes-ui-lag--android--medium]]
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]]
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]]
