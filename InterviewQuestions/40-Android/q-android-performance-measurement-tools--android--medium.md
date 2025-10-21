---
id: 20251012-122768
title: Android Performance Measurement Tools / Инструменты измерения производительности Android
aliases: [Android Performance Measurement Tools, Инструменты измерения производительности Android]
topic: android
subtopics: [performance, profiling, testing]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
created: 2025-10-13
updated: 2025-10-15
tags: [android/performance, android/profiling, android/testing, android-profiler, benchmark, gpu-rendering, optimization, performance, profiling, difficulty/medium]
related: [q-android-app-lag-analysis--android--medium, q-android-build-optimization--android--medium, q-android-architectural-patterns--android--medium]
---
# Question (EN)
> How to measure program performance changes after our actions in Android?

# Вопрос (RU)
> Как определить изменение скорости работы программы после наших действий в Android?

---

## Answer (EN)

**Android Performance Measurement** involves using specialized tools to quantify and analyze app performance before and after optimizations. The key is establishing baseline metrics and measuring improvements systematically.

**Performance Measurement Theory:**
Performance measurement requires establishing baseline metrics, identifying bottlenecks, and quantifying improvements. Different tools target different performance aspects: UI rendering, CPU usage, memory allocation, network operations, and system-level interactions.

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

## Ответ (RU)

**Измерение производительности Android** включает использование специализированных инструментов для количественной оценки и анализа производительности приложения до и после оптимизаций. Ключ в установлении базовых метрик и систематическом измерении улучшений.

**Теория измерения производительности:**
Измерение производительности требует установления базовых метрик, выявления узких мест и количественной оценки улучшений. Разные инструменты нацелены на разные аспекты производительности: рендеринг UI, использование CPU, выделение памяти, сетевые операции и системные взаимодействия.

**Основные инструменты измерения:**
- **Android Profiler**: Анализ CPU, памяти, сети и энергии в реальном времени
- **GPU Rendering**: Визуализация времени кадров для производительности UI
- **Jetpack Benchmark**: Количественное тестирование производительности кода
- **Perfetto**: Системная трассировка для глубокого анализа
- **StrictMode**: Обнаружение нарушений главного потока

**Настройка Android Profiler:**
```kotlin
// Включить в Android Studio: View → Tool Windows → Profiler
// Подключить устройство и выбрать процесс приложения
// Использовать вкладки CPU, Memory, Network, Energy для анализа
```

**Анализ GPU Rendering:**
```kotlin
// Включить в параметрах разработчика:
// Настройки → Параметры разработчика → Профилирование GPU-рендеринга → На экране в виде полос

// Зеленая линия = 16ms (цель 60 fps)
// Полосы выше зеленой = пропущенные кадры
// Красные полосы = более 16ms (задержки)
```

**Реализация Jetpack Benchmark:**
```kotlin
// build.gradle.kts
androidTestImplementation("androidx.benchmark:benchmark-junit4:1.3.2")
androidTestImplementation("androidx.benchmark:benchmark-macro-junit4:1.3.2")

// Микробенчмарк - производительность на уровне методов
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

// Макробенчмарк - производительность на уровне приложения
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

**Пользовательское измерение производительности:**
```kotlin
class PerformanceMeasurer {
    fun measureOperation(operation: () -> Unit): Long {
        val startTime = System.nanoTime()
        operation()
        return System.nanoTime() - startTime
    }

    fun measureWithWarmup(operation: () -> Unit, iterations: Int = 1000): Double {
        // Прогрев
        repeat(10) { operation() }

        // Измерение
        val times = mutableListOf<Long>()
        repeat(iterations) {
            times.add(measureOperation(operation))
        }

        return times.average() / 1_000_000.0 // Конвертация в миллисекунды
    }
}
```

**Конфигурация StrictMode:**
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

**Системная трассировка Perfetto:**
```kotlin
// Пользовательские секции трассировки
Trace.beginSection("DataProcessing")
processData()
Trace.endSection()

// Системная трассировка через Android Studio:
// Run → Profile → CPU → System Trace
```

**Рабочий процесс сравнения производительности:**
```kotlin
class PerformanceComparison {
    @Test
    fun compareImplementations() {
        val measurer = PerformanceMeasurer()

        // Базовое измерение
        val baseline = measurer.measureWithWarmup { oldImplementation() }

        // Измерение оптимизированной версии
        val optimized = measurer.measureWithWarmup { newImplementation() }

        // Вычисление улучшения
        val improvement = ((baseline - optimized) / baseline * 100)
        println("Производительность улучшена на ${improvement.toInt()}%")

        assertTrue(optimized < baseline)
    }
}
```

**Руководство по выбору инструментов:**
- **Производительность UI**: GPU Rendering, Macrobenchmark
- **Анализ CPU**: Android Profiler CPU tab, Perfetto
- **Проблемы памяти**: Android Profiler Memory tab
- **Производительность сети**: Android Profiler Network tab
- **Оптимизация кода**: Microbenchmark, пользовательское измерение
- **Системный анализ**: Perfetto, Systrace

---

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
