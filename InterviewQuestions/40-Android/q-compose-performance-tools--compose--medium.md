---
id: android-748
title: Compose Performance Tools / Инструменты анализа производительности Compose
aliases:
- Compose Performance Tools
- Layout Inspector Compose
- Compose Compiler Reports
- Инструменты анализа производительности Compose
- Отчёты компилятора Compose
topic: android
subtopics:
- performance-rendering
- ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-recomposition
- c-recomposition
- q-compose-compiler-plugin--android--hard
- q-compose-performance-optimization--android--hard
- q-compose-stability-skippability--android--hard
- q-compose-slot-table-recomposition--android--hard
- q-android-performance-measurement-tools--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/performance-rendering
- android/ui-compose
- difficulty/medium
sources:
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/tooling/layout-inspector
---
# Вопрос (RU)
> Какие инструменты используются для анализа производительности Jetpack Compose? Как интерпретировать отчёты компилятора и данные Layout Inspector?

# Question (EN)
> What tools are used to analyze Jetpack Compose performance? How to interpret compiler reports and Layout Inspector data?

---

## Ответ (RU)

### Краткий Вариант

Основные инструменты для анализа производительности Compose:
1. **Layout Inspector** --- визуализация дерева композиции, подсчёт рекомпозиций, анализ семантики
2. **Compose Compiler Reports** --- анализ стабильности типов и пропускаемости функций
3. **Perfetto / System Tracing** --- низкоуровневый анализ времени кадров и потоков
4. **Macrobenchmark** --- измерение производительности в реальных условиях

### Подробный Вариант

#### 1. Layout Inspector

Layout Inspector в Android Studio позволяет инспектировать Compose UI в реальном времени.

**Ключевые возможности**:
- Просмотр дерева композиции (не View-иерархии)
- Подсчёт рекомпозиций и их пропусков (skips)
- Анализ параметров composable-функций
- Просмотр семантического дерева для accessibility

**Как включить подсчёт рекомпозиций**:

1. Запустите приложение в debug-режиме
2. Откройте Layout Inspector: View -> Tool Windows -> Layout Inspector
3. Включите "Show Recomposition Counts" в панели инструментов

```
Пример вывода:
UserProfile (recomposed: 15, skipped: 42)
  |-- Avatar (recomposed: 2, skipped: 55)
  |-- NameText (recomposed: 15, skipped: 42)  <-- проблема!
  |-- EmailText (recomposed: 0, skipped: 57)
```

**Интерпретация**:
- Высокое число recomposed при низком skipped = нестабильные параметры
- Высокое skipped = эффективная оптимизация
- Частые рекомпозиции дочерних при стабильном родителе = проблема с пропускаемостью

**Отладка проблем**:

```kotlin
// Плохо: рекомпозируется при каждом изменении родителя
@Composable
fun NameText(user: User) { // User может быть нестабильным
    Text(user.name)
}

// Лучше: передаём только нужные данные
@Composable
fun NameText(name: String) { // String стабилен
    Text(name)
}
```

#### 2. Compose Compiler Reports

Compiler reports показывают, как компилятор классифицирует типы и функции.

**Включение в build.gradle.kts**:

```kotlin
// Для AGP 8.x+ и Compose Compiler 2.0+
composeCompiler {
    reportsDestination = layout.buildDirectory.dir("compose_reports")
    metricsDestination = layout.buildDirectory.dir("compose_metrics")
}

// Альтернативный способ через compilerOptions (для старых версий)
// kotlinOptions {
//     freeCompilerArgs += listOf(
//         "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
//             project.buildDir.absolutePath + "/compose_reports",
//         "-P", "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=" +
//             project.buildDir.absolutePath + "/compose_metrics"
//     )
// }
```

**Генерация отчётов**:

```bash
./gradlew :app:assembleRelease
# Отчёты появятся в app/build/compose_reports/
```

**Типы файлов отчётов**:

| Файл | Содержимое |
|------|------------|
| `*-classes.txt` | Стабильность классов |
| `*-composables.txt` | Пропускаемость и перезапускаемость функций |
| `*-module.json` | Сводная статистика модуля |

**Пример classes.txt**:

```
stable class StableUser {
  stable val id: Int
  stable val name: String
}

unstable class UnstableUser {
  stable val id: Int
  unstable var name: String  // <-- var делает класс нестабильным
}

runtime class UserFromLibrary {
  // Компилятор не может определить стабильность
}
```

**Пример composables.txt**:

```
restartable skippable scheme("[androidx.compose.ui.UiComposable]") fun Counter(
  stable count: Int
  stable onIncrement: Function0<Unit>
)

restartable scheme("[androidx.compose.ui.UiComposable]") fun UserCard(
  unstable user: User  // <-- функция не пропускаема из-за нестабильного параметра
)
```

**Интерпретация**:
- `restartable skippable` = оптимальный случай
- `restartable` (без skippable) = функция будет рекомпозироваться при любом обновлении родителя
- `stable` параметр = компилятор может эффективно сравнивать
- `unstable` параметр = принудительная рекомпозиция

#### 3. Perfetto / System Tracing

Для низкоуровневого анализа времени кадров и идентификации jank.

**Запуск трейса**:

```bash
# Через adb
adb shell perfetto \
  -c - --txt \
  -o /data/misc/perfetto-traces/trace.perfetto-trace \
<<EOF
buffers: {
    size_kb: 63488
    fill_policy: RING_BUFFER
}
data_sources: {
    config {
        name: "android.surfaceflinger.frametimeline"
    }
}
data_sources: {
    config {
        name: "linux.ftrace"
        ftrace_config {
            ftrace_events: "ftrace/print"
        }
    }
}
duration_ms: 10000
EOF
```

**Или через Android Studio**:
1. View -> Tool Windows -> Profiler
2. CPU -> Record -> System Trace

**Что искать в трейсе**:
- Длительные фреймы (>16ms для 60fps)
- Блокировки на главном потоке
- Частые GC паузы
- Длительные measure/layout/draw фазы

#### 4. Compose Tracing

Начиная с Compose 1.3.0, можно добавить трейсинг композиции.

**Подключение**:

```kotlin
dependencies {
    implementation("androidx.compose.runtime:runtime-tracing:1.0.0-beta01")
}
```

**Использование**:

```kotlin
// В Application.onCreate()
if (BuildConfig.DEBUG) {
    // Трейсинг автоматически интегрируется с Perfetto
}
```

После этого в Perfetto будут видны имена composable-функций и время их выполнения.

#### 5. Macrobenchmark

Для измерения производительности в реальных условиях.

**Пример теста**:

```kotlin
@RunWith(AndroidJUnit4::class)
class ComposeScrollBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun scrollPerformance() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(FrameTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.WARM,
        setupBlock = {
            startActivityAndWait()
        }
    ) {
        // Выполнить скролл
        device.findObject(By.res("list")).apply {
            setGestureMargin(device.displayWidth / 5)
            fling(Direction.DOWN)
        }
        device.waitForIdle()
    }
}
```

**Метрики**:
- `frameDurationCpuMs` --- время CPU на кадр
- `frameOverrunMs` --- превышение бюджета кадра
- `initialDisplayMs` --- время до первого кадра

#### Практические Рекомендации

**Workflow анализа производительности**:

1. **Выявление проблемы**: Layout Inspector -> найти часто рекомпозируемые composable
2. **Анализ причины**: Compiler Reports -> проверить стабильность параметров
3. **Измерение baseline**: Macrobenchmark -> записать текущую производительность
4. **Оптимизация**: Исправить нестабильные типы, добавить `@Stable`/`@Immutable`
5. **Валидация**: Повторить измерения, сравнить с baseline

**Типичные проблемы и решения**:

| Симптом | Причина | Решение |
|---------|---------|---------|
| Частые recomposition | Нестабильные параметры | `@Stable`, ImmutableList |
| Низкий skip count | Lambda recreations | `remember { }` для lambda |
| Jank при скролле | Тяжёлые item | `LazyColumn` с ключами |
| Медленная инициализация | Eager composition | `LazyColumn`, `SubcomposeLayout` |

---

## Answer (EN)

### Short Version

Main tools for analyzing Compose performance:
1. **Layout Inspector** --- composition tree visualization, recomposition counting, semantics analysis
2. **Compose Compiler Reports** --- type stability and function skippability analysis
3. **Perfetto / System Tracing** --- low-level frame timing and thread analysis
4. **Macrobenchmark** --- real-world performance measurement

### Detailed Version

#### 1. Layout Inspector

Layout Inspector in Android Studio allows inspecting Compose UI in real-time.

**Key features**:
- View composition tree (not View hierarchy)
- Count recompositions and skips
- Analyze composable function parameters
- View semantic tree for accessibility

**Enabling recomposition counts**:

1. Run the app in debug mode
2. Open Layout Inspector: View -> Tool Windows -> Layout Inspector
3. Enable "Show Recomposition Counts" in the toolbar

```
Example output:
UserProfile (recomposed: 15, skipped: 42)
  |-- Avatar (recomposed: 2, skipped: 55)
  |-- NameText (recomposed: 15, skipped: 42)  <-- problem!
  |-- EmailText (recomposed: 0, skipped: 57)
```

**Interpretation**:
- High recomposed with low skipped = unstable parameters
- High skipped = effective optimization
- Frequent child recompositions with stable parent = skippability issue

**Debugging issues**:

```kotlin
// Bad: recomposes on every parent update
@Composable
fun NameText(user: User) { // User might be unstable
    Text(user.name)
}

// Better: pass only needed data
@Composable
fun NameText(name: String) { // String is stable
    Text(name)
}
```

#### 2. Compose Compiler Reports

Compiler reports show how the compiler classifies types and functions.

**Enabling in build.gradle.kts**:

```kotlin
// For AGP 8.x+ and Compose Compiler 2.0+
composeCompiler {
    reportsDestination = layout.buildDirectory.dir("compose_reports")
    metricsDestination = layout.buildDirectory.dir("compose_metrics")
}

// Alternative via compilerOptions (for older versions)
// kotlinOptions {
//     freeCompilerArgs += listOf(
//         "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
//             project.buildDir.absolutePath + "/compose_reports",
//         "-P", "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=" +
//             project.buildDir.absolutePath + "/compose_metrics"
//     )
// }
```

**Generating reports**:

```bash
./gradlew :app:assembleRelease
# Reports will appear in app/build/compose_reports/
```

**Report file types**:

| File | Contents |
|------|----------|
| `*-classes.txt` | Class stability |
| `*-composables.txt` | Function skippability and restartability |
| `*-module.json` | Module-level summary statistics |

**Example classes.txt**:

```
stable class StableUser {
  stable val id: Int
  stable val name: String
}

unstable class UnstableUser {
  stable val id: Int
  unstable var name: String  // <-- var makes the class unstable
}

runtime class UserFromLibrary {
  // Compiler cannot determine stability
}
```

**Example composables.txt**:

```
restartable skippable scheme("[androidx.compose.ui.UiComposable]") fun Counter(
  stable count: Int
  stable onIncrement: Function0<Unit>
)

restartable scheme("[androidx.compose.ui.UiComposable]") fun UserCard(
  unstable user: User  // <-- function is not skippable due to unstable parameter
)
```

**Interpretation**:
- `restartable skippable` = optimal case
- `restartable` (without skippable) = function will recompose on any parent update
- `stable` parameter = compiler can efficiently compare
- `unstable` parameter = forced recomposition

#### 3. Perfetto / System Tracing

For low-level frame timing analysis and jank identification.

**Starting a trace**:

```bash
# Via adb
adb shell perfetto \
  -c - --txt \
  -o /data/misc/perfetto-traces/trace.perfetto-trace \
<<EOF
buffers: {
    size_kb: 63488
    fill_policy: RING_BUFFER
}
data_sources: {
    config {
        name: "android.surfaceflinger.frametimeline"
    }
}
data_sources: {
    config {
        name: "linux.ftrace"
        ftrace_config {
            ftrace_events: "ftrace/print"
        }
    }
}
duration_ms: 10000
EOF
```

**Or via Android Studio**:
1. View -> Tool Windows -> Profiler
2. CPU -> Record -> System Trace

**What to look for in traces**:
- Long frames (>16ms for 60fps)
- Main thread blocking
- Frequent GC pauses
- Long measure/layout/draw phases

#### 4. Compose Tracing

Starting with Compose 1.3.0, you can add composition tracing.

**Setup**:

```kotlin
dependencies {
    implementation("androidx.compose.runtime:runtime-tracing:1.0.0-beta01")
}
```

**Usage**:

```kotlin
// In Application.onCreate()
if (BuildConfig.DEBUG) {
    // Tracing automatically integrates with Perfetto
}
```

After this, Perfetto will show composable function names and execution times.

#### 5. Macrobenchmark

For measuring performance in real-world conditions.

**Example test**:

```kotlin
@RunWith(AndroidJUnit4::class)
class ComposeScrollBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun scrollPerformance() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(FrameTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.WARM,
        setupBlock = {
            startActivityAndWait()
        }
    ) {
        // Perform scroll
        device.findObject(By.res("list")).apply {
            setGestureMargin(device.displayWidth / 5)
            fling(Direction.DOWN)
        }
        device.waitForIdle()
    }
}
```

**Metrics**:
- `frameDurationCpuMs` --- CPU time per frame
- `frameOverrunMs` --- frame budget overrun
- `initialDisplayMs` --- time to first frame

#### Practical Recommendations

**Performance analysis workflow**:

1. **Identify the problem**: Layout Inspector -> find frequently recomposing composables
2. **Analyze the cause**: Compiler Reports -> check parameter stability
3. **Measure baseline**: Macrobenchmark -> record current performance
4. **Optimize**: Fix unstable types, add `@Stable`/`@Immutable`
5. **Validate**: Repeat measurements, compare with baseline

**Common issues and solutions**:

| Symptom | Cause | Solution |
|---------|-------|----------|
| Frequent recomposition | Unstable parameters | `@Stable`, ImmutableList |
| Low skip count | Lambda recreations | `remember { }` for lambdas |
| Scroll jank | Heavy items | `LazyColumn` with keys |
| Slow initialization | Eager composition | `LazyColumn`, `SubcomposeLayout` |

---

## Дополнительные Вопросы (Follow-ups, RU)

- Как интерпретировать "runtime" стабильность в отчётах компилятора?
- Как использовать Strong Skipping Mode и как он влияет на отчёты?
- Какие метрики Macrobenchmark наиболее важны для Compose?
- Как профилировать Compose на устройствах без root?
- Как автоматизировать проверку регрессий производительности в CI?

## Follow-ups

- How to interpret "runtime" stability in compiler reports?
- How to use Strong Skipping Mode and how does it affect reports?
- Which Macrobenchmark metrics are most important for Compose?
- How to profile Compose on non-rooted devices?
- How to automate performance regression checks in CI?

## Ссылки (RU)

- [[c-compose-recomposition]]
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/tooling/layout-inspector
- https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview

## References

- [[c-compose-recomposition]]
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/tooling/layout-inspector
- https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview

## Связанные Вопросы (RU)

### Предпосылки (проще)

- [[q-android-performance-measurement-tools--android--medium]] --- общие инструменты профилирования Android

### Связанные (тот же уровень)

- [[q-compose-stability-skippability--android--hard]] --- стабильность и пропускаемость
- [[q-compose-modifier-order-performance--android--medium]] --- влияние порядка модификаторов

### Продвинутые (сложнее)

- [[q-compose-compiler-plugin--android--hard]] --- внутренности компилятора Compose
- [[q-compose-slot-table-recomposition--android--hard]] --- механика рекомпозиции

## Related Questions

### Prerequisites (Easier)

- [[q-android-performance-measurement-tools--android--medium]] --- general Android profiling tools

### Related (Same Level)

- [[q-compose-stability-skippability--android--hard]] --- stability and skippability
- [[q-compose-modifier-order-performance--android--medium]] --- modifier order impact

### Advanced (Harder)

- [[q-compose-compiler-plugin--android--hard]] --- Compose compiler internals
- [[q-compose-slot-table-recomposition--android--hard]] --- recomposition mechanics
