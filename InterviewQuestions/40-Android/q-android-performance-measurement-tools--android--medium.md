---
topic: android
tags:
  - android
  - android-profiler
  - android/performance
  - benchmark
  - gpu-rendering
  - optimization
  - performance
  - profiling
difficulty: medium
status: draft
---

# Как определить изменение скорости работы программы после наших действий?

**English**: How to measure program performance changes after our actions?

## Answer

To measure program performance changes, you can use the following tools:

**1. Profile GPU Rendering**

Shows frame rendering time and helps identify heavy frames.

```kotlin
// Enable in Developer Options:
// Settings → Developer Options → Profile GPU Rendering → On screen as bars

// Green line = 16ms (60 fps target)
// Bars above green = dropped frames
```

**2. Android Profiler**

Provides tools for analyzing app performance through CPU, Memory tabs and others.

```kotlin
// In Android Studio: View → Tool Windows → Profiler

// CPU Profiler - method tracing
// Memory Profiler - allocation tracking
// Network Profiler - requests monitoring
// Energy Profiler - battery usage
```

**3. Benchmarking with Jetpack Benchmark**

Allows quantitative assessment of improvements.

```kotlin
// build.gradle
androidTestImplementation "androidx.benchmark:benchmark-junit4:1.2.0"

// Benchmark test
@RunWith(AndroidJUnit4::class)
class MyBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun benchmarkSomeWork() {
        benchmarkRule.measureRepeated {
            // Code to benchmark
            doSomeWork()
        }
    }
}
```

**4. Logcat - Timing Operations**

Used to measure execution time through logging.

```kotlin
val startTime = System.currentTimeMillis()
performOperation()
val endTime = System.currentTimeMillis()
Log.d("Performance", "Operation took ${endTime - startTime}ms")

// Or use SystemClock
val startNanos = SystemClock.elapsedRealtimeNanos()
performOperation()
val durationNanos = SystemClock.elapsedRealtimeNanos() - startNanos
Log.d("Performance", "Duration: ${durationNanos / 1_000_000}ms")
```

**5. StrictMode**

Helps detect operations that slow down the app on the main thread.

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

**6. Systrace**

Allows collecting system performance traces.

```bash

# Command line
python systrace.py --time=10 -o trace.html sched gfx view wm am app

# In code - custom trace sections
Trace.beginSection("MyOperation")
performOperation()
Trace.endSection()
```

**Comparison Workflow:**

```kotlin
class PerformanceTest {
    @Test
    fun comparePerformance() {
        // Before optimization
        val before = measurePerformance { oldImplementation() }

        // After optimization
        val after = measurePerformance { newImplementation() }

        // Calculate improvement
        val improvement = ((before - after) / before.toFloat() * 100).toInt()
        println("Performance improved by $improvement%")

        // Assert improvement
        assertTrue(after < before)
    }

    private fun measurePerformance(block: () -> Unit): Long {
        val iterations = 1000
        val start = System.nanoTime()
        repeat(iterations) { block() }
        return (System.nanoTime() - start) / iterations
    }
}
```

**Summary of Tools:**

| Tool | Purpose | Best For |
|------|---------|----------|
| **GPU Rendering** | Frame time visualization | UI performance |
| **Android Profiler** | Detailed analysis | CPU, Memory, Network |
| **Benchmark** | Quantitative testing | Comparing implementations |
| **Logcat** | Quick measurements | Specific operations |
| **StrictMode** | Main thread violations | Development debugging |
| **Systrace** | System-level traces | Deep performance analysis |

All these methods allow comparing data before and after optimization to assess program performance changes.

## Ответ

Для определения изменения скорости работы программы можно использовать следующие инструменты:

- **Profile GPU Rendering** - показывает время отрисовки кадров и позволяет выявить тяжелые кадры
- **Android Profiler** - предоставляет набор инструментов для анализа производительности приложения через вкладки CPU, Memory и другие
- **Benchmarking** с использованием Jetpack Benchmark - позволяет количественно оценить улучшения
- **Logcat** - используется для измерения времени выполнения операций через логирование
- **StrictMode** - помогает обнаружить операции, замедляющие работу приложения в главном потоке
- **Systrace** - позволяет собирать трассировки производительности системы

