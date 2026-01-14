---
id: android-098
title: Android Performance Measurement Tools / Инструменты измерения производительности
  Android
aliases:
- Android Performance Measurement Tools
- Инструменты измерения производительности Android
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
status: draft
moc: moc-android
related:
- c-android-basics
- c-compose-recomposition
- c-perfetto
- c-performance
- c-power-profiling
- q-android-app-lag-analysis--android--medium
- q-multithreading-tools-android--android--medium
- q-optimize-memory-usage-android--android--medium
- q-performance-monitoring-jank-compose--android--medium
sources: []
created: 2025-10-13
updated: 2025-11-10
tags:
- android/performance-memory
- android/profiling
- android/testing-benchmark
- difficulty/medium
- optimization
- performance
anki_cards:
- slug: android-098-0-en
  language: en
  anki_id: 1768363603072
  synced_at: '2026-01-14T09:17:53.661129'
- slug: android-098-0-ru
  language: ru
  anki_id: 1768363603098
  synced_at: '2026-01-14T09:17:53.663557'
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
- **GPU Rendering / Profile GPU Rendering**: визуализация времени отрисовки кадров (цель: ~16ms для 60fps)
- **Layout Inspector**: анализ иерархии `View` и композиции

**2. Автоматизированные микробенчмарки (Jetpack Benchmark)**

Jetpack Benchmark Library обеспечивает точные, воспроизводимые измерения. Данные и окружение готовятся отдельно от измеряемого блока. Пример ниже упрощён и иллюстрирует идею; для реальных тестов используйте официальные шаблоны и Gradle-конфигурацию.

```kotlin
// Microbenchmark - производительность отдельного метода (упрощённый пример)
@RunWith(AndroidJUnit4::class)
class SortBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    private lateinit var data: MutableList<Int>

    @Before
    fun setup() {
        data = MutableList(10_000) { Random.nextInt() }
    }

    @Test
    fun sortLargeList() {
        benchmarkRule.measureRepeated {
            // Измеряем только сортировку, избегая аллокации списка внутри блока
            data.sort()
        }
    }
}
```

**3. Macrobenchmark - UI сценарии и запуск приложения**

Пример ниже демонстрирует общий подход и не включает всю необходимую инфраструктуру (отдельный macrobenchmark-модуль, манифест и т.п.).

```kotlin
@get:Rule
val macrobenchmarkRule = MacrobenchmarkRule()

@Test
fun appStartup() = macrobenchmarkRule.measureRepeated(
    packageName = "com.app",
    metrics = listOf(StartupTimingMetric()),
    iterations = 5,
    startupMode = StartupMode.COLD
) {
    pressHome()
    startActivityAndWait()
}
// Явно измеряет cold start через StartupMode.COLD; в реальных проектах обычно также используют Baseline Profiles / настройки компиляции
```

**4. StrictMode - детекция блокировок главного потока**

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()   // Детектирует файловые операции в главном потоке
            .detectDiskWrites()
            .detectNetwork()     // Детектирует сетевые вызовы в главном потоке
            .penaltyLog()
            .build()
    )
}
// Не включайте в production-сборках
```

**5. Perfetto - системная трассировка**

Анализирует низкоуровневые события: планирование CPU, кадры, binder-вызовы, выделения памяти. Запускается через System Tracing / Record trace (в Android Studio или на устройстве) или из CLI, затем анализируется в Perfetto UI.

### Выбор Инструмента

| Проблема                      | Инструмент                              |
|------------------------------|-----------------------------------------|
| UI jank, пропуск кадров      | GPU Rendering + Macrobenchmark          |
| CPU hotspots                 | Android Profiler + Perfetto             |
| Утечки памяти                | Android Profiler Memory                 |
| Регрессии производительности | Microbenchmark в CI/CD                  |
| Медленный старт              | Macrobenchmark + Baseline Profiles      |

### Паттерны Корректных Измерений

```kotlin
// JIT warmup перед измерением (для релевантных сценариев)
repeat(100) { operation() }

// Множественные итерации для статистической значимости
val times = (1..1000).map { measureNanos { operation() } }

// Исключение выбросов (outliers)
val trimmedMean = times.sorted()
    .drop(times.size / 10)
    .take(times.size * 8 / 10)
    .average()
```

**Компромиссы:**
- Microbenchmark: высокая точность vs. оторванность от реального окружения (тесты изолированы от system load)
- Profiler: детализация vs. overhead (может заметно замедлять приложение)
- Perfetto: системный контекст vs. сложность интерпретации

## Answer (EN)

**Performance measurement tools** identify bottlenecks through quantitative analysis. Principle: establish baseline metrics, measure changes systematically, and select the right tool for the specific task.

### Main Tool Categories

**1. Real-time Profiling**
- **Android Profiler** (Android Studio): CPU, memory, network, energy consumption in real-time
- **GPU Rendering / Profile GPU Rendering**: frame timing visualization (target around 16ms for 60fps)
- **Layout Inspector**: `View` hierarchy and composition analysis

**2. Automated Microbenchmarks (Jetpack Benchmark)**

Jetpack Benchmark Library provides precise, reproducible measurements. Test data and environment should be prepared outside the measured block. The example below is simplified; for real usage follow official templates and Gradle configuration.

```kotlin
// Microbenchmark - isolated method performance (simplified example)
@RunWith(AndroidJUnit4::class)
class SortBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    private lateinit var data: MutableList<Int>

    @Before
    fun setup() {
        data = MutableList(10_000) { Random.nextInt() }
    }

    @Test
    fun sortLargeList() {
        benchmarkRule.measureRepeated {
            // Measure only sorting, avoiding list allocation inside the measured block
            data.sort()
        }
    }
}
```

**3. Macrobenchmark - UI scenarios and app startup**

The snippet below shows the general pattern and omits full setup (separate macrobenchmark module, manifest, etc.).

```kotlin
@get:Rule
val macrobenchmarkRule = MacrobenchmarkRule()

@Test
fun appStartup() = macrobenchmarkRule.measureRepeated(
    packageName = "com.app",
    metrics = listOf(StartupTimingMetric()),
    iterations = 5,
    startupMode = StartupMode.COLD
) {
    pressHome()
    startActivityAndWait()
}
// Measures cold startup explicitly via StartupMode.COLD; real setups commonly also use Baseline Profiles / compilation configuration
```

**4. StrictMode - main thread blocking detection**

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()   // Detects file operations on the main thread
            .detectDiskWrites()
            .detectNetwork()     // Detects network calls on the main thread
            .penaltyLog()
            .build()
    )
}
// DO NOT enable in production builds
```

**5. Perfetto - system tracing**

Analyzes low-level events: CPU scheduling, frames, binder calls, memory allocations. Started via System Tracing / Record trace (in Android Studio or on-device) or CLI, then inspected in Perfetto UI.

### Tool Selection

| Problem                     | Tool                                   |
|-----------------------------|----------------------------------------|
| UI jank, frame drops        | GPU Rendering + Macrobenchmark         |
| CPU hotspots                | Android Profiler + Perfetto            |
| Memory leaks                | Android Profiler Memory                |
| Performance regressions     | Microbenchmark in CI/CD                |
| Slow startup                | Macrobenchmark + Baseline Profiles     |

### Correct Measurement Patterns

```kotlin
// JIT warmup before measurement (where applicable)
repeat(100) { operation() }

// Multiple iterations for statistical significance
val times = (1..1000).map { measureNanos { operation() } }

// Exclude outliers
val trimmedMean = times.sorted()
    .drop(times.size / 10)
    .take(times.size * 8 / 10)
    .average()
```

**Trade-offs:**
- Microbenchmark: precision vs. lack of full real-world environment (tests isolated from system load)
- Profiler: detail vs. overhead (can noticeably slow down the app)
- Perfetto: rich system context vs. complexity of interpretation

---

## Дополнительные Вопросы (RU)

- Как интегрировать Jetpack Benchmark в CI/CD для автоматического выявления регрессий производительности?
- Какие метрики памяти в Android Profiler помогают отличить утечки от нормального роста?
- Как коррелировать события в трассах Perfetto с пользовательским jank с помощью кастомных trace markers?
- Какие подходы измерения наиболее эффективны для оптимизации под устройства начального уровня?
- Как устанавливать базовые метрики производительности при добавлении новой фичи в существующий код?

## Follow-ups

- How to integrate Jetpack Benchmark into CI/CD to detect performance regressions automatically?
- What memory metrics specifically indicate leaks vs. normal growth patterns in Android Profiler?
- How to correlate Perfetto trace events with user-reported jank using custom trace markers?
- Which measurement approaches are most effective for low-end device optimization?
- How to establish baseline performance metrics when adding a new feature to an existing codebase?

## Ссылки (RU)

- [[c-performance]]
- [Performance](https://developer.android.com/topic/performance)
- https://developer.android.com/studio/profile/benchmark

## References

- [[c-performance]]
- [Performance](https://developer.android.com/topic/performance)
- https://developer.android.com/studio/profile/benchmark

## Связанные Вопросы (RU)

### Предпосылки
- [[q-android-app-lag-analysis--android--medium]] - Понимание проблем производительности и jank

### Связано
- [[q-android-build-optimization--android--medium]] - Оптимизация сборки и времени компиляции

## Related Questions

### Prerequisites
- [[q-android-app-lag-analysis--android--medium]] - Understanding performance issues and jank

### Related
- [[q-android-build-optimization--android--medium]] - Build and compile-time performance
