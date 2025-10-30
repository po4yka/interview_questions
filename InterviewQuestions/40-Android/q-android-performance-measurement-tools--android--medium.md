---
id: 20251012-122768
title: Android Performance Measurement Tools / Инструменты измерения производительности Android
aliases: ["Android Performance Measurement Tools", "Инструменты измерения производительности Android"]
topic: android
subtopics: [performance-memory, profiling, testing-benchmark]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-lag-analysis--android--medium, q-android-architectural-patterns--android--medium, q-android-build-optimization--android--medium]
sources: []
created: 2025-10-13
updated: 2025-10-29
tags: [android/performance-memory, android/profiling, android/testing-benchmark, difficulty/medium]
---
# Вопрос (RU)
> Какие инструменты используются для измерения производительности Android приложений и как их применять?

# Question (EN)
> What tools are used to measure Android app performance and how to apply them?

## Ответ (RU)

**Инструменты измерения производительности** обеспечивают количественный анализ приложений. Принцип: устанавливай базовые метрики, измеряй изменения систематически, выбирай инструмент под задачу.

**Ключевые категории:**

**1. Profiling в реальном времени**
- **Android Profiler**: CPU, память, сеть, энергопотребление
- **GPU Rendering**: время отрисовки кадров (цель: 16ms для 60fps)

**2. Автоматизированные бенчмарки**
```kotlin
// Микробенчмарк - производительность метода
@RunWith(AndroidJUnit4::class)
class DataBenchmark {
    @get:Rule
    val benchmark = BenchmarkRule()

    @Test
    fun sortLargeList() {
        val data = List(10_000) { it }
        benchmark.measureRepeated {
            data.sorted() // ✅ Измеряется чистая производительность
        }
    }
}
```

**3. Макробенчмарки UI**
```kotlin
@Test
fun appStartup() = benchmarkRule.measureRepeated(
    packageName = "com.app",
    metrics = listOf(StartupTimingMetric())
) {
    pressHome()
    startActivityAndWait() // ✅ Время холодного старта
}
```

**4. StrictMode - детекция блокировок**
```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        ThreadPolicy.Builder()
            .detectDiskReads()   // ✅ Файловые операции
            .detectNetwork()     // ✅ Сетевые вызовы
            .penaltyLog()
            .build()
    )
}
```

**5. Perfetto - системная трассировка**
Анализирует: frames, CPU scheduling, binder calls, memory allocations

**Выбор инструмента:**
- Jank в UI → GPU Rendering + Macrobenchmark
- CPU hotspots → Android Profiler + Perfetto
- Утечки памяти → Android Profiler Memory
- Регрессии в коде → Microbenchmark в CI/CD

**Паттерны измерения:**
```kotlin
// ✅ Прогрев JIT перед измерением
repeat(100) { operation() }

// ✅ Множественные итерации для стабильности
val times = (1..1000).map { measureNanos { operation() } }

// ✅ Исключение выбросов
times.sorted().drop(times.size / 10).take(times.size * 8 / 10).average()
```

## Answer (EN)

**Performance measurement tools** provide quantitative app analysis. Principle: establish baseline metrics, measure changes systematically, select the right tool for the task.

**Key Categories:**

**1. Real-time Profiling**
- **Android Profiler**: CPU, memory, network, energy consumption
- **GPU Rendering**: frame timing visualization (target: 16ms for 60fps)

**2. Automated Benchmarks**
```kotlin
// Microbenchmark - method-level performance
@RunWith(AndroidJUnit4::class)
class DataBenchmark {
    @get:Rule
    val benchmark = BenchmarkRule()

    @Test
    fun sortLargeList() {
        val data = List(10_000) { it }
        benchmark.measureRepeated {
            data.sorted() // ✅ Measures pure performance
        }
    }
}
```

**3. UI Macrobenchmarks**
```kotlin
@Test
fun appStartup() = benchmarkRule.measureRepeated(
    packageName = "com.app",
    metrics = listOf(StartupTimingMetric())
) {
    pressHome()
    startActivityAndWait() // ✅ Cold startup time
}
```

**4. StrictMode - Blocking Detection**
```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        ThreadPolicy.Builder()
            .detectDiskReads()   // ✅ File operations
            .detectNetwork()     // ✅ Network calls
            .penaltyLog()
            .build()
    )
}
```

**5. Perfetto - System Tracing**
Analyzes: frames, CPU scheduling, binder calls, memory allocations

**Tool Selection:**
- UI jank → GPU Rendering + Macrobenchmark
- CPU hotspots → Android Profiler + Perfetto
- Memory leaks → Android Profiler Memory
- Code regressions → Microbenchmark in CI/CD

**Measurement Patterns:**
```kotlin
// ✅ JIT warmup before measuring
repeat(100) { operation() }

// ✅ Multiple iterations for stability
val times = (1..1000).map { measureNanos { operation() } }

// ✅ Exclude outliers
times.sorted().drop(times.size / 10).take(times.size * 8 / 10).average()
```

## Follow-ups

- How to integrate Jetpack Benchmark into CI/CD for regression detection?
- What specific metrics indicate memory leaks vs normal memory growth patterns?
- How to correlate Perfetto trace events with user-reported jank incidents?
- Which measurement approaches work best for low-end device optimization?
- How to establish baseline performance metrics for a new feature?

## References

- [[c-android-profiling]]
- [[c-performance-optimization]]
- https://developer.android.com/topic/performance

## Related Questions

### Prerequisites
- [[q-android-app-lag-analysis--android--medium]] - Understanding performance issues

### Related
- [[q-android-build-optimization--android--medium]] - Build performance
- [[q-android-memory-leaks--android--medium]] - Memory leak detection

### Advanced
- [[q-android-baseline-profiles--android--hard]] - Profile-guided optimization
- [[q-android-render-optimization--android--hard]] - Advanced rendering optimization