---
id: 20251012-122768
title: Android Performance Measurement Tools / Инструменты измерения производительности
aliases: ["Android Performance Measurement Tools", "Инструменты измерения производительности Android"]
topic: android
subtopics: [performance-memory, profiling, testing-unit]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-lag-analysis--android--medium, q-android-architectural-patterns--android--medium, q-android-build-optimization--android--medium]
created: 2025-10-13
updated: 2025-10-27
tags: [android/performance-memory, android/profiling, android/testing-unit, difficulty/medium]
---
# Вопрос (RU)
> Какие инструменты используются для измерения производительности Android приложений?

# Question (EN)
> What are Android Performance Measurement Tools?

## Ответ (RU)

**Инструменты измерения производительности Android** используются для количественного анализа и оптимизации приложений. Ключевые принципы: установка базовых метрик, систематическое измерение улучшений и выбор подходящего инструмента для конкретной задачи.

**Основные инструменты:**
- **Android Profiler**: анализ CPU, памяти, сети и энергопотребления в реальном времени
- **GPU Rendering**: визуализация времени отрисовки кадров (цель: 16ms для 60 fps)
- **Jetpack Benchmark**: количественное тестирование производительности кода
- **Perfetto**: системная трассировка для глубокого анализа
- **StrictMode**: обнаружение операций блокирующих главный поток

**Jetpack Benchmark:**
```kotlin
// Микробенчмарк - производительность метода
@RunWith(AndroidJUnit4::class)
class PerformanceBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun benchmarkDataProcessing() {
        benchmarkRule.measureRepeated {
            processData() // ✅ Измеряет чистую производительность метода
        }
    }
}

// Макробенчмарк - производительность приложения
@Test
fun startup() {
    benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 5
    ) {
        pressHome()
        startActivityAndWait() // ✅ Измеряет время запуска приложения
    }
}
```

**Пользовательское измерение:**
```kotlin
class PerformanceMeasurer {
    fun measureWithWarmup(operation: () -> Unit, iterations: Int = 1000): Double {
        repeat(10) { operation() } // ✅ Прогрев для стабильных результатов

        val times = mutableListOf<Long>()
        repeat(iterations) {
            val start = System.nanoTime()
            operation()
            times.add(System.nanoTime() - start)
        }
        return times.average() / 1_000_000.0 // в миллисекунды
    }
}
```

**StrictMode для отладки:**
```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()    // ✅ Обнаружение чтения с диска
            .detectDiskWrites()   // ✅ Обнаружение записи на диск
            .detectNetwork()      // ✅ Обнаружение сетевых операций
            .penaltyLog()         // ❌ В продакшене не используется
            .build()
    )
}
```

**Выбор инструмента:**
- UI производительность → GPU Rendering, Macrobenchmark
- Анализ CPU → Android Profiler, Perfetto
- Проблемы с памятью → Android Profiler Memory
- Оптимизация кода → Microbenchmark
- Системный анализ → Perfetto

## Answer (EN)

**Android Performance Measurement Tools** quantify and analyze app performance. Core principles: establish baseline metrics, measure improvements systematically, and select the right tool for the task.

**Key Tools:**
- **Android Profiler**: Real-time CPU, memory, network, and energy analysis
- **GPU Rendering**: Frame timing visualization (target: 16ms for 60 fps)
- **Jetpack Benchmark**: Quantitative code performance testing
- **Perfetto**: System-wide tracing for deep analysis
- **StrictMode**: Main thread blocking operation detection

**Jetpack Benchmark:**
```kotlin
// Microbenchmark - method-level performance
@RunWith(AndroidJUnit4::class)
class PerformanceBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun benchmarkDataProcessing() {
        benchmarkRule.measureRepeated {
            processData() // ✅ Measures pure method performance
        }
    }
}

// Macrobenchmark - app-level performance
@Test
fun startup() {
    benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 5
    ) {
        pressHome()
        startActivityAndWait() // ✅ Measures app startup time
    }
}
```

**Custom Measurement:**
```kotlin
class PerformanceMeasurer {
    fun measureWithWarmup(operation: () -> Unit, iterations: Int = 1000): Double {
        repeat(10) { operation() } // ✅ Warmup for stable results

        val times = mutableListOf<Long>()
        repeat(iterations) {
            val start = System.nanoTime()
            operation()
            times.add(System.nanoTime() - start)
        }
        return times.average() / 1_000_000.0 // to milliseconds
    }
}
```

**StrictMode for Debugging:**
```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()    // ✅ Detect disk reads
            .detectDiskWrites()   // ✅ Detect disk writes
            .detectNetwork()      // ✅ Detect network operations
            .penaltyLog()         // ❌ Not used in production
            .build()
    )
}
```

**Tool Selection:**
- UI performance → GPU Rendering, Macrobenchmark
- CPU analysis → Android Profiler, Perfetto
- Memory issues → Android Profiler Memory
- Code optimization → Microbenchmark
- System analysis → Perfetto

## Follow-ups

- How to integrate Jetpack Benchmark into CI/CD pipeline?
- What metrics indicate memory leaks vs normal memory growth?
- How to correlate Perfetto traces with user-reported jank?
- Which tools work best for low-end device optimization?

## References

- [[c-memory-management]]
- https://developer.android.com/topic/performance/measurement
- https://developer.android.com/topic/performance/benchmarking

## Related Questions

### Prerequisites
- [[q-android-app-lag-analysis--android--medium]] - Analyzing performance issues

### Related
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns
- [[q-android-build-optimization--android--medium]] - Build optimization

### Advanced
- [[q-android-modularization--android--medium]] - Modular architecture impact on performance