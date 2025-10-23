---
id: 20251012-122768
title: Android Performance Measurement Tools / Инструменты измерения производительности
aliases:
- Android Performance Measurement Tools
- Инструменты измерения производительности Android
topic: android
subtopics:
- performance-memory
- profiling
- testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-app-lag-analysis--android--medium
- q-android-build-optimization--android--medium
- q-android-architectural-patterns--android--medium
created: 2025-10-13
updated: 2025-10-15
tags:
- android/performance-memory
- android/profiling
- android/testing-unit
- difficulty/medium
---

## Answer (EN)
**Android Performance Measurement** involves using specialized tools to quantify and analyze app performance before and after optimizations. The key is establishing baseline metrics and measuring improvements systematically.

**Performance Measurement Theory:**
Performance measurement requires establishing baseline metrics, identifying bottlenecks, and quantifying improvements. Different tools target different performance aspects: [[c-rendering]] (UI rendering), CPU usage, [[c-memory-management]] (memory allocation), network operations, and system-level interactions.

**Core Measurement Tools:**
- **Android Profiler**: Real-time CPU, memory, network, and energy analysis
- **GPU Rendering**: Frame timing visualization for UI performance
- **Jetpack Benchmark**: Quantitative testing for code performance
- **Perfetto**: System-wide tracing for deep analysis
- **StrictMode**: Main thread violation detection

**Android Profiler Setup:**
```kotlin
// Enable in Android Studio: View → Tool Windows → Profiler
// Connect device and select app process
// Use CPU, Memory, Network, Energy tabs for analysis
```

**GPU Rendering Analysis:**
```kotlin
// Enable in Developer Options:
// Settings → Developer Options → Profile GPU Rendering → On screen as bars

// Green line = 16ms (60 fps target)
// Bars above green = dropped frames
// Red bars = over 16ms (jank)
```

**Jetpack Benchmark Implementation:**
```kotlin
// build.gradle.kts
androidTestImplementation("androidx.benchmark:benchmark-junit4:1.3.2")
androidTestImplementation("androidx.benchmark:benchmark-macro-junit4:1.3.2")

// Microbenchmark - method-level performance
@RunWith(AndroidJUnit4::class)
class PerformanceBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun benchmarkDataProcessing() {
        benchmarkRule.measureRepeated {
            processData()
        }
    }
}

// Macrobenchmark - app-level performance
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startup() {
        benchmarkRule.measureRepeated(
            packageName = "com.example.app",
            metrics = listOf(StartupTimingMetric()),
            iterations = 5
        ) {
            pressHome()
            startActivityAndWait()
        }
    }
}
```

**Custom Performance Measurement:**
```kotlin
class PerformanceMeasurer {
    fun measureOperation(operation: () -> Unit): Long {
        val startTime = System.nanoTime()
        operation()
        return System.nanoTime() - startTime
    }

    fun measureWithWarmup(operation: () -> Unit, iterations: Int = 1000): Double {
        // Warmup
        repeat(10) { operation() }

        // Measure
        val times = mutableListOf<Long>()
        repeat(iterations) {
            times.add(measureOperation(operation))
        }

        return times.average() / 1_000_000.0 // Convert to milliseconds
    }
}
```

**StrictMode Configuration:**
```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )
}
```

**Perfetto System Tracing:**
```kotlin
// Custom trace sections
Trace.beginSection("DataProcessing")
processData()
Trace.endSection()

// System tracing via Android Studio:
// Run → Profile → CPU → System Trace
```

**Performance Comparison Workflow:**
```kotlin
class PerformanceComparison {
    @Test
    fun compareImplementations() {
        val measurer = PerformanceMeasurer()

        // Baseline measurement
        val baseline = measurer.measureWithWarmup { oldImplementation() }

        // Optimized measurement
        val optimized = measurer.measureWithWarmup { newImplementation() }

        // Calculate improvement
        val improvement = ((baseline - optimized) / baseline * 100)
        println("Performance improved by ${improvement.toInt()}%")

        assertTrue(optimized < baseline)
    }
}
```

**Tool Selection Guide:**
- **UI Performance**: GPU Rendering, Macrobenchmark
- **CPU Analysis**: Android Profiler CPU tab, Perfetto
- **Memory Issues**: Android Profiler Memory tab
- **Network Performance**: Android Profiler Network tab
- **Code Optimization**: Microbenchmark, custom measurement
- **System Analysis**: Perfetto, Systrace

## Follow-ups

- How to set up continuous performance monitoring in CI/CD?
- What are the best practices for performance regression testing?
- How to measure performance on different device configurations?

## References

- https://developer.android.com/topic/performance/measurement
- https://developer.android.com/topic/performance/benchmarking

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-lag-analysis--android--medium]] - Performance analysis
- [[q-android-build-optimization--android--medium]] - Build optimization

### Related (Medium)
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns
- [[q-android-modularization--android--medium]] - Modular architecture
- [[q-android-lint-tool--android--medium]] - Code quality tools