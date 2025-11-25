---
id: android-249
title: "What Is Layout Performance Measured In / В чем измеряется производительность layout"
aliases: ["Layout Performance Measurement", "Измерение производительности layout"]
topic: android
subtopics: [performance-rendering, ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-compose-modifier-order-performance--android--medium, q-macrobenchmark-startup--android--medium, q-performance-optimization-android--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/performance-rendering, android/ui-views, difficulty/medium, performance, rendering]

date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> В чём измеряется производительность layout в Android?

# Question (EN)

> What is layout performance measured in Android?

## Ответ (RU)

Базовая метрика производительности layout и рендеринга в Android измеряется во **времени кадра в миллисекундах (мс)**: сколько времени тратится на фазы **measure** (измерение), **layout** (размещение) и **draw** (отрисовка), а также связанную работу рендеринга в рамках одного кадра относительно бюджета времени под целевую частоту кадров. Дополнительно оцениваются **потерянные кадры (jank)** и, для Compose, **количество перекомпоновок**.

### Ключевые Метрики

**Целевое время кадра:**
- 60 FPS = 16.67мс на кадр
- 90 FPS = 11.11мс на кадр
- 120 FPS = 8.33мс на кадр

**Примерное распределение времени (для 60fps, только как ориентир):**
- Measure phase ≲ 5мс
- Layout phase ≲ 5мс
- Draw phase ≲ 6.67мс

(Значения являются эвристиками и зависят от устройства, частоты обновления, нагрузки на GPU/CPU и сложности UI.)

### Инструменты Измерения

**1. `Choreographer` API** — измерение времени между кадрами (эвристика для оценки jank):

```kotlin
class FrameMonitor {
    private val choreographer = Choreographer.getInstance()
    private var lastFrameTime = 0L

    private val callback = object : Choreographer.FrameCallback {
        override fun doFrame(frameTimeNanos: Long) {
            if (lastFrameTime != 0L) {
                val frameTimeMs = (frameTimeNanos - lastFrameTime) / 1_000_000.0
                // ✅ Эвристическое измерение времени между кадрами
                val budgetMs = 16.67
                if (frameTimeMs > budgetMs) {
                    val dropped = (frameTimeMs / budgetMs).toInt() - 1
                    if (dropped > 0) {
                        Log.w("Perf", "Possible dropped frames (approx): $dropped (frame=${frameTimeMs}ms)")
                    }
                }
            }
            lastFrameTime = frameTimeNanos
            // Продолжаем мониторинг
            choreographer.postFrameCallback(this)
        }
    }

    fun start() {
        choreographer.postFrameCallback(callback)
    }
}
```

**2. `FrameMetrics` API** (API 24+) — детальные метрики по кадрам (значения в наносекундах для окон верхнего уровня):

```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
    window.addOnFrameMetricsAvailableListener({ _, metrics, _ ->
        val total = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
        val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
        val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
        // Анализ фаз measure/layout/draw относительно бюджета кадра
    }, Handler(Looper.getMainLooper()))
}
```

(На практике слушатель нужно удалять при уничтожении окна, чтобы избежать утечек.)

**3. Systrace/Perfetto** — системное профилирование и трассировка рендеринга:

```kotlin
Trace.beginSection("complexOperation")
try {
    // ✅ Маркируем критические секции
    performExpensiveOperation()
} finally {
    Trace.endSection()
}
```

**4. Compose Compiler Metrics** — анализ перекомпоновок и стабильности параметров (build-time отчёты, а не runtime-таймер):

```kotlin
// build.gradle (модуль с Compose UI)
android {
    // ...
}

kotlinOptions {
    freeCompilerArgs += [
        "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
            "${project.buildDir}/compose_metrics"
    ]
}

@Composable
fun PerformanceTracker() {
    // ✅ Стабильные параметры минимизируют перекомпоновки
    val count = remember { mutableStateOf(0) }
}
```

### Метрики Сложности Layout

**Пример анализа иерархии `View`:**

```kotlin
data class Metrics(val viewCount: Int, val maxDepth: Int)

fun analyzeComplexity(view: View): Metrics {
    var viewCount = 0
    var maxDepth = 0

    fun traverse(v: View, depth: Int) {
        viewCount++
        maxDepth = maxOf(maxDepth, depth)
        (v as? ViewGroup)?.forEach { child ->
            traverse(child, depth + 1)
        }
    }

    traverse(view, 0)
    return Metrics(viewCount, maxDepth)
}

// ✅ Эвристические ориентиры (не официальные лимиты): views ≲ 80, depth ≲ 10
// ❗ Реальные допустимые значения зависят от устройства и содержимого
```

### Best Practices

| Техника | Цель | Инструмент |
|---------|------|-----------|
| Frame timing | Укладываться в бюджет кадра (< 16.67мс при 60fps) | Choreographer, FrameMetrics |
| Layout depth | Сдерживать глубину иерархии (~< 10 уровней как эвристика) | Layout Inspector |
| Recomposition (Compose) | Минимизировать лишние перекомпоновки | Compose metrics |
| Overdraw | Стремиться к < 2x | GPU Overdraw tool |
| Jank detection | Минимизировать/избегать потерь кадров | Perfetto, Systrace |

## Answer (EN)

The primary unit for layout and rendering performance in Android is **frame time in milliseconds (ms)**: how long the **measure**, **layout**, and **draw** phases, plus associated rendering work, take within a single frame relative to the time budget for the target refresh rate. Additionally, we track **jank/dropped frames** and, for Compose, **recomposition count**.

### Key Metrics

**Target frame times:**
- 60 FPS = 16.67ms per frame
- 90 FPS = 11.11ms per frame
- 120 FPS = 8.33ms per frame

**Example time distribution (for 60fps, for guidance only):**
- Measure phase ≲ 5ms
- Layout phase ≲ 5ms
- Draw phase ≲ 6.67ms

(These are heuristics and depend on device capabilities, refresh rate, overall CPU/GPU load, and UI complexity.)

### Measurement Tools

**1. `Choreographer` API** — frame interval timing (heuristic for jank estimation):

```kotlin
class FrameMonitor {
    private val choreographer = Choreographer.getInstance()
    private var lastFrameTime = 0L

    private val callback = object : Choreographer.FrameCallback {
        override fun doFrame(frameTimeNanos: Long) {
            if (lastFrameTime != 0L) {
                val frameTimeMs = (frameTimeNanos - lastFrameTime) / 1_000_000.0
                // ✅ Heuristic measurement of frame interval
                val budgetMs = 16.67
                if (frameTimeMs > budgetMs) {
                    val dropped = (frameTimeMs / budgetMs).toInt() - 1
                    if (dropped > 0) {
                        Log.w("Perf", "Possible dropped frames (approx): $dropped (frame=${frameTimeMs}ms)")
                    }
                }
            }
            lastFrameTime = frameTimeNanos
            // Continue monitoring
            choreographer.postFrameCallback(this)
        }
    }

    fun start() {
        choreographer.postFrameCallback(callback)
    }
}
```

**2. `FrameMetrics` API** (API 24+) — detailed per-frame metrics (values in nanoseconds for top-level window frames):

```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
    window.addOnFrameMetricsAvailableListener({ _, metrics, _ ->
        val total = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
        val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
        val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
        // Analyze measure/layout/draw phases against the frame budget
    }, Handler(Looper.getMainLooper()))
}
```

(In real code, remove the listener when the window is destroyed to avoid leaks.)

**3. Systrace/Perfetto** — system-level tracing and rendering analysis:

```kotlin
Trace.beginSection("complexOperation")
try {
    // ✅ Mark critical sections
    performExpensiveOperation()
} finally {
    Trace.endSection()
}
```

**4. Compose Compiler Metrics** — build-time reports for recomposition and stability (not direct runtime timing):

```kotlin
// build.gradle (module with Compose UI)
android {
    // ...
}

kotlinOptions {
    freeCompilerArgs += [
        "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
            "${project.buildDir}/compose_metrics"
    ]
}

@Composable
fun PerformanceTracker() {
    // ✅ Stable parameters minimize unnecessary recompositions
    val count = remember { mutableStateOf(0) }
}
```

### Layout Complexity Metrics

**Example view hierarchy analyzer:**

```kotlin
data class Metrics(val viewCount: Int, val maxDepth: Int)

fun analyzeComplexity(view: View): Metrics {
    var viewCount = 0
    var maxDepth = 0

    fun traverse(v: View, depth: Int) {
        viewCount++
        maxDepth = maxOf(maxDepth, depth)
        (v as? ViewGroup)?.forEach { child ->
            traverse(child, depth + 1)
        }
    }

    traverse(view, 0)
    return Metrics(viewCount, maxDepth)
}

// ✅ Heuristic guidelines (not official limits): views ≲ 80, depth ≲ 10
// ❗ Actual safe limits depend on device performance and content
```

### Best Practices

| Technique | Target | Tool |
|-----------|--------|------|
| Frame timing | Stay within frame budget (< 16.67ms at 60fps) | Choreographer, FrameMetrics |
| Layout depth | Keep hierarchy reasonably shallow (~< 10 levels as a heuristic) | Layout Inspector |
| Recomposition (Compose) | Minimize unnecessary recompositions | Compose metrics |
| Overdraw | Aim for < 2x | GPU Overdraw tool |
| Jank detection | Minimize / avoid dropped frames | Perfetto, Systrace |

---

## Дополнительные Вопросы (RU)

- Как оптимизировать производительность layout, если глубина иерархии превышает 10 уровней?
- В чем разница между Systrace и Perfetto для анализа производительности?
- Как предотвратить избыточные перекомпоновки в Jetpack Compose?
- Какие инструменты вы бы использовали для обнаружения overdraw в продакшн-сборках?
- Как Layout Inspector помогает находить узкие места в производительности?

## Follow-ups

- How do you optimize layout performance when hierarchy depth exceeds 10 levels?
- What's the difference between Systrace and Perfetto for performance analysis?
- How do you prevent excessive recompositions in Jetpack Compose?
- What tools would you use to detect overdraw in production builds?
- How does Layout Inspector help identify performance bottlenecks?

## Ссылки (RU)

- [[c-jetpack-compose]]
- [Rendering Performance](https://developer.android.com/topic/performance/rendering)
- https://developer.android.com/studio/profile/inspect-traces

## References

- [[c-jetpack-compose]]
- [Rendering Performance](https://developer.android.com/topic/performance/rendering)
- https://developer.android.com/studio/profile/inspect-traces

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-separate-ui-business-logic--android--easy]] - Базовые принципы архитектуры UI

### Связанные (средний уровень)
- [[q-compose-modifier-order-performance--android--medium]] - Оптимизация производительности в Compose
- [[q-macrobenchmark-startup--android--medium]] - Бенчмаркинг старта приложения
- [[q-performance-optimization-android--android--medium]] - Общая оптимизация производительности Android

### Продвинутые (сложнее)
- [[q-compose-lazy-layout-optimization--android--hard]] - Продвинутая оптимизация layout в Compose
- [[q-canvas-drawing-optimization--android--hard]] - Оптимизация производительности при custom-отрисовке

## Related Questions

### Prerequisites (Easier)
- [[q-separate-ui-business-logic--android--easy]] - UI architecture basics

### Related (Medium)
- [[q-compose-modifier-order-performance--android--medium]] - Compose performance optimization
- [[q-macrobenchmark-startup--android--medium]] - App startup benchmarking
- [[q-performance-optimization-android--android--medium]] - General Android performance

### Advanced (Harder)
- [[q-compose-lazy-layout-optimization--android--hard]] - Advanced Compose layout optimization
- [[q-canvas-drawing-optimization--android--hard]] - Custom drawing performance
