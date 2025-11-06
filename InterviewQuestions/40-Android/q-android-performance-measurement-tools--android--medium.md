---
id: android-098
title: Android Performance Measurement Tools / Инструменты измерения производительности Android
aliases: [Android Performance Measurement Tools, Инструменты измерения производительности Android]
topic: android
subtopics:
  - performance-memory
  - profiling
  - testing-benchmark
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-android-profiling
  - c-performance-optimization
  - q-android-app-lag-analysis--android--medium
sources: []
created: 2025-10-13
updated: 2025-10-30
tags: [android/performance-memory, android/profiling, android/testing-benchmark, difficulty/medium, optimization, performance]
---

# Вопрос (RU)
> Какие инструменты используются для измерения производительности Android приложений и как их применять?

# Question (EN)
> What tools are used to measure Android app performance and how to apply them?

---

## Ответ (RU)

**Инструменты измерения производительности** позволяют обнаруживать узкие места через количественный анализ. Принцип: устанавливай базовые метрики, измеряй изменения систематически, выбирай инструмент под конкретную задачу.

### Основные Категории Инструментов

**1. Profiling в реальном времени**
- **Android Profiler** (Android Studio): CPU, память, сеть, энергопотребление в режиме реального времени
- **GPU Rendering**: визуализация времени отрисовки кадров (цель: 16ms для 60fps)
- **Layout Inspector**: анализ иерархии View и композиции

**2. Автоматизированные бенчмарки**

Jetpack Benchmark Library обеспечивает точные, воспроизводимые измерения:

```kotlin
// Microbenchmark - производительность отдельного метода
@RunWith(AndroidJUnit4::class)
class SortBenchmark {
    @get:Rule
    val benchmark = BenchmarkRule()

    @Test
    fun sortLargeList() {
        val data = List(10_000) { Random.nextInt() }
        benchmark.measureRepeated {
            data.sorted() // ✅ Изолированное измерение без setup overhead
        }
    }
}
```

**3. Macrobenchmark - UI scenarios**

```kotlin
@Test
fun appStartup() = benchmarkRule.measureRepeated(
    packageName = "com.app",
    metrics = listOf(StartupTimingMetric())
) {
    pressHome()
    startActivityAndWait() // ✅ Время холодного старта без JIT warmup
}
```

**4. StrictMode - детекция блокировок главного потока**

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        ThreadPolicy.Builder()
            .detectDiskReads()   // ✅ Обнаруживает файловые операции
            .detectNetwork()     // ✅ Обнаруживает сетевые вызовы
            .penaltyLog()
            .build()
    )
}
// ❌ НЕ включать в production builds
```

**5. Perfetto - системная трассировка**

Анализирует низкоуровневые события: планирование CPU, frames, binder calls, memory allocations. Запускается через System Tracing в Android Studio или CLI.

### Выбор Инструмента

| Проблема                  | Инструмент                      |
|---------------------------|---------------------------------|
| UI jank, пропуск кадров   | GPU Rendering + Macrobenchmark  |
| CPU hotspots              | Android Profiler + Perfetto     |
| Утечки памяти             | Android Profiler Memory         |
| Регрессии производительности | Microbenchmark в CI/CD       |
| Медленный старт           | Macrobenchmark + Baseline Profiles |

### Паттерны Корректных Измерений

```kotlin
// ✅ JIT warmup перед измерением
repeat(100) { operation() }

// ✅ Множественные итерации для статистической значимости
val times = (1..1000).map { measureNanos { operation() } }

// ✅ Исключение выбросов (outliers)
val trimmedMean = times.sorted()
    .drop(times.size / 10)
    .take(times.size * 8 / 10)
    .average()
```

**Trade-offs:**
- Microbenchmark: точность vs. реальное окружение (тесты изолированы от system load)
- Profiler: детализация vs. overhead (может замедлять приложение на 20-30%)
- Perfetto: системный контекст vs. сложность интерпретации

## Answer (EN)

**Performance measurement tools** identify bottlenecks through quantitative analysis. Principle: establish baseline metrics, measure changes systematically, select the right tool for the specific task.

### Main Tool Categories

**1. Real-time Profiling**
- **Android Profiler** (Android Studio): CPU, memory, network, energy consumption in real-time
- **GPU Rendering**: frame timing visualization (target: 16ms for 60fps)
- **Layout Inspector**: View hierarchy and composition analysis

**2. Automated Benchmarks**

Jetpack Benchmark Library provides precise, reproducible measurements:

```kotlin
// Microbenchmark - isolated method performance
@RunWith(AndroidJUnit4::class)
class SortBenchmark {
    @get:Rule
    val benchmark = BenchmarkRule()

    @Test
    fun sortLargeList() {
        val data = List(10_000) { Random.nextInt() }
        benchmark.measureRepeated {
            data.sorted() // ✅ Isolated measurement without setup overhead
        }
    }
}
```

**3. Macrobenchmark - UI scenarios**

```kotlin
@Test
fun appStartup() = benchmarkRule.measureRepeated(
    packageName = "com.app",
    metrics = listOf(StartupTimingMetric())
) {
    pressHome()
    startActivityAndWait() // ✅ Cold startup time without JIT warmup
}
```

**4. StrictMode - main thread blocking detection**

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        ThreadPolicy.Builder()
            .detectDiskReads()   // ✅ Detects file operations
            .detectNetwork()     // ✅ Detects network calls
            .penaltyLog()
            .build()
    )
}
// ❌ DO NOT enable in production builds
```

**5. Perfetto - system tracing**

Analyzes low-level events: CPU scheduling, frames, binder calls, memory allocations. Launched via System Tracing in Android Studio or CLI.

### Tool Selection

| Problem                   | Tool                            |
|---------------------------|---------------------------------|
| UI jank, frame drops      | GPU Rendering + Macrobenchmark  |
| CPU hotspots              | Android Profiler + Perfetto     |
| Memory leaks              | Android Profiler Memory         |
| Performance regressions   | Microbenchmark in CI/CD         |
| Slow startup              | Macrobenchmark + Baseline Profiles |

### Correct Measurement Patterns

```kotlin
// ✅ JIT warmup before measurement
repeat(100) { operation() }

// ✅ Multiple iterations for statistical significance
val times = (1..1000).map { measureNanos { operation() } }

// ✅ Exclude outliers
val trimmedMean = times.sorted()
    .drop(times.size / 10)
    .take(times.size * 8 / 10)
    .average()
```

**Trade-offs:**
- Microbenchmark: precision vs. real environment (tests isolated from system load)
- Profiler: detail level vs. overhead (can slow app by 20-30%)
- Perfetto: system context vs. interpretation complexity

---

## Follow-ups

- How to integrate Jetpack Benchmark into CI/CD to detect performance regressions automatically?
- What memory metrics specifically indicate leaks vs. normal growth patterns in Android Profiler?
- How to correlate Perfetto trace events with user-reported jank using custom trace markers?
- Which measurement approaches are most effective for low-end device optimization?
- How to establish baseline performance metrics when adding a new feature to an existing codebase?

## References

- [[c-performance-optimization]]
- [Performance](https://developer.android.com/topic/performance)
- https://developer.android.com/studio/profile/benchmark


## Related Questions

### Prerequisites
- [[q-android-app-lag-analysis--android--medium]] - Understanding performance issues and jank

### Related
- [[q-android-build-optimization--android--medium]] - Build and compile-time performance
 - Memory leak detection techniques
 - Rendering performance optimization
