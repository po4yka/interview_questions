---
id: android-249
title: "What Is Layout Performance Measured In / В чем измеряется производительность layout"
aliases: ["Layout Performance Measurement", "Измерение производительности layout"]
topic: android
subtopics: [performance-rendering, profiling, ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-modifier-order-performance--android--medium, q-macrobenchmark-startup--android--medium, q-performance-optimization-android--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/performance-rendering, android/profiling, android/ui-views, difficulty/medium, performance, rendering]
---

# Вопрос (RU)

В чём измеряется производительность layout в Android?

# Question (EN)

What is layout performance measured in Android?

## Ответ (RU)

Производительность layout в Android измеряется в **миллисекундах (мс)** времени рендеринга, отслеживая три основных фазы: **measure** (измерение), **layout** (размещение) и **draw** (отрисовка). Дополнительно отслеживаются **потерянные кадры** и **количество перекомпоновок** в Compose.

### Ключевые Метрики

**Целевое время кадра:**
- 60 FPS = 16.67мс на кадр
- 90 FPS = 11.11мс на кадр
- 120 FPS = 8.33мс на кадр

**Распределение времени (для 60fps):**
- Measure phase < 5мс
- Layout phase < 5мс
- Draw phase < 6.67мс

### Инструменты Измерения

**1. Choreographer API** - измерение времени кадров:

```kotlin
class FrameMonitor {
    private val choreographer = Choreographer.getInstance()
    private var lastFrameTime = 0L

    fun start() {
        choreographer.postFrameCallback { frameTimeNanos ->
            if (lastFrameTime != 0L) {
                val frameTime = (frameTimeNanos - lastFrameTime) / 1_000_000.0
                // ✅ Корректное измерение между кадрами
                if (frameTime > 16.67) {
                    // ❌ Потерян кадр
                    Log.w("Perf", "Dropped frame: ${frameTime}ms")
                }
            }
            lastFrameTime = frameTimeNanos
        }
    }
}
```

**2. FrameMetrics API** (API 24+) - детальные метрики:

```kotlin
window.addOnFrameMetricsAvailableListener { _, metrics, _ ->
    val total = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
    val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
    val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
    // Анализ фаз рендеринга
}
```

**3. Systrace/Perfetto** - системное профилирование:

```kotlin
Trace.beginSection("complexOperation")
try {
    // ✅ Маркируем критические секции
    performExpensiveOperation()
} finally {
    Trace.endSection()
}
```

**4. Compose Compiler Metrics** - метрики перекомпоновки:

```kotlin
// build.gradle
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

**`View` hierarchy analyzer:**

```kotlin
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

// ✅ Целевые значения: views < 80, depth < 10
// ❌ Превышение лимитов ведет к замедлению
```

### Практические Рекомендации

| Техника | Цель | Инструмент |
|---------|------|-----------|
| Frame timing | < 16.67мс | Choreographer |
| Layout depth | < 10 уровней | Layout Inspector |
| Recomposition | Минимизация | Compose metrics |
| Overdraw | < 2x | GPU Overdraw tool |
| Jank detection | 0 потерь | Systrace/Perfetto |

## Answer (EN)

Layout performance in Android is measured in **milliseconds (ms)** of rendering time, tracking three main phases: **measure**, **layout**, and **draw**. Additionally, we track **dropped frames** and **recomposition count** in Compose.

### Key Metrics

**Target frame times:**
- 60 FPS = 16.67ms per frame
- 90 FPS = 11.11ms per frame
- 120 FPS = 8.33ms per frame

**Time distribution (for 60fps):**
- Measure phase < 5ms
- Layout phase < 5ms
- Draw phase < 6.67ms

### Measurement Tools

**1. Choreographer API** - frame timing:

```kotlin
class FrameMonitor {
    private val choreographer = Choreographer.getInstance()
    private var lastFrameTime = 0L

    fun start() {
        choreographer.postFrameCallback { frameTimeNanos ->
            if (lastFrameTime != 0L) {
                val frameTime = (frameTimeNanos - lastFrameTime) / 1_000_000.0
                // ✅ Correct frame time measurement
                if (frameTime > 16.67) {
                    // ❌ Frame dropped
                    Log.w("Perf", "Dropped frame: ${frameTime}ms")
                }
            }
            lastFrameTime = frameTimeNanos
        }
    }
}
```

**2. FrameMetrics API** (API 24+) - detailed metrics:

```kotlin
window.addOnFrameMetricsAvailableListener { _, metrics, _ ->
    val total = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000.0
    val layout = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION) / 1_000_000.0
    val draw = metrics.getMetric(FrameMetrics.DRAW_DURATION) / 1_000_000.0
    // Analyze rendering phases
}
```

**3. Systrace/Perfetto** - system-level profiling:

```kotlin
Trace.beginSection("complexOperation")
try {
    // ✅ Mark critical sections
    performExpensiveOperation()
} finally {
    Trace.endSection()
}
```

**4. Compose Compiler Metrics** - recomposition tracking:

```kotlin
// build.gradle
kotlinOptions {
    freeCompilerArgs += [
        "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
        "${project.buildDir}/compose_metrics"
    ]
}

@Composable
fun PerformanceTracker() {
    // ✅ Stable parameters minimize recompositions
    val count = remember { mutableStateOf(0) }
}
```

### Layout Complexity Metrics

**`View` hierarchy analyzer:**

```kotlin
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

// ✅ Target values: views < 80, depth < 10
// ❌ Exceeding limits causes slowdowns
```

### Best Practices

| Technique | Target | Tool |
|-----------|--------|------|
| Frame timing | < 16.67ms | Choreographer |
| Layout depth | < 10 levels | Layout Inspector |
| Recomposition | Minimize | Compose metrics |
| Overdraw | < 2x | GPU Overdraw tool |
| Jank detection | 0 drops | Systrace/Perfetto |

---

## Follow-ups

- How do you optimize layout performance when hierarchy depth exceeds 10 levels?
- What's the difference between Systrace and Perfetto for performance analysis?
- How do you prevent excessive recompositions in Jetpack Compose?
- What tools would you use to detect overdraw in production builds?
- How does Layout Inspector help identify performance bottlenecks?

## References

- [[c-android-profiling]] - Android profiling concepts
- [[c-jetpack-compose]] - Compose fundamentals
- [Rendering Performance](https://developer.android.com/topic/performance/rendering)
- https://developer.android.com/studio/profile/inspect-traces


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
