---
id: android-211
title: "Performance Monitoring Jank Compose / Мониторинг производительности и джанка в Compose"
aliases: [Compose Performance, Jank Detection, Performance Monitoring Jank Compose, Мониторинг производительности и джанка в Compose]
topic: android
subtopics: [performance-rendering, profiling, ui-compose]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, c-performance-optimization, q-compose-lazy-layout-optimization--android--hard, q-compose-performance-optimization--android--hard]
created: 2025-10-15
updated: 2025-10-30
tags: [android/performance-rendering, android/profiling, android/ui-compose, difficulty/medium, jank, optimization, performance, recomposition]
sources: [https://developer.android.com/jetpack/compose/performance, https://developer.android.com/topic/performance/vitals/render]
---
# Вопрос (RU)

> Как обнаружить и устранить проблемы производительности (jank) в Jetpack Compose приложениях?

# Question (EN)

> How do you detect and fix performance issues (jank) in Jetpack Compose apps?

---

## Ответ (RU)

**Jank** — "замирания" UI, когда кадр не укладывается в отведённый слот времени для текущей частоты обновления экрана (например, >16.67ms для 60 Гц, >11.11ms для 90 Гц). Главные причины в Compose: избыточные recompositions, тяжёлые вычисления в UI-потоке, неоптимизированные списки, блокировка main thread I/O/синхронными операциями, неэффективная работа с состоянием.

### Инструменты Обнаружения

**1. Layout Inspector** — визуализация деревьев Compose, подсветка частоты recomposition (Highlight recompositions), просмотр слоёв и измерений.

**2. Composition Tracing** — трассировка composable-функций и их recomposition в Android Studio Profiler (Compose Tracing / System Trace) для поиска горячих участков.

**3. Macrobenchmark** — измерение времени рендеринга и scroll, frame timing, jank count, percentiles (P50/P90/P95/P99) для типичных сценариев.

**4. FrameMetrics API** — runtime-мониторинг frame-таймингов и jank в production-сборках.

### Ключевые Техники Оптимизации

**remember** — кэширование дорогих вычислений внутри composable:

```kotlin
// ❌ Вычисляется каждый recompose
@Composable
fun ExpensiveList(items: List<Item>) {
    val processed = items.map { processItem(it) }
    LazyColumn { items(processed) { ItemView(it) } }
}

// ✅ Кэшируется, пересчитывается только при изменении items
@Composable
fun ExpensiveList(items: List<Item>) {
    val processed = remember(items) { items.map { processItem(it) } }
    LazyColumn { items(processed) { ItemView(it) } }
}
```

**derivedStateOf** — вычислять производное значение и подписываться только на его изменения, чтобы избежать лишних recomposition потребителей:

```kotlin
// ❌ showButton читается напрямую из listState и может часто меняться
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()
    val showButton = listState.firstVisibleItemIndex > 0
    // ...
}

// ✅ Потребители showButton будут обновляться только при изменении условия (0 → 1+ и обратно)
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }
    // ...
}
```

**@Stable/@Immutable** — помощь Compose в определении стабильности типов для более агрессивного пропуска recomposition:

```kotlin
// ⚠️ Нестабильный из-за MutableList: изменения могут не отслеживаться корректно Compose runtime
data class User(val name: String, val posts: MutableList<Post>)

// ✅ Иммутабельная структура данных лучше согласуется с моделью стабильности
@Immutable
data class User(val name: String, val posts: List<Post>)
```

**Упрощённые правила Stability (Compose)**:
- стабильность определяется моделью стабильности Compose, а не только `val`/`var`;
- примитивные типы и большинство стандартных неизменяемых типов считаются стабильными;
- mutable-коллекции и изменяемые поля (`var`) могут делать тип нестабильным для Compose;
- аннотации `@Stable` / `@Immutable` помогают явно задать контракт, но требуют соблюдения его условий (отсутствие скрытых мутаций и т.п.).

**LazyColumn keys** — стабильные уникальные keys помогают сохранить идентичность элементов при изменении списка:

```kotlin
// ❌ Без key при изменении порядка Compose может пересоздавать элементы
LazyColumn {
    items(products) { product -> ProductItem(product) }
}

// ✅ С ключами Compose лучше сохраняет состояние и избегает лишних пересозданий при reorder/insert/remove
LazyColumn {
    items(products, key = { it.id }) { product -> ProductItem(product) }
}
```

### Macrobenchmark - Измерение Performance

```kotlin
@Test
fun scrollBenchmark() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(FrameTimingMetric()),
    iterations = 5
) {
    val list = device.findObject(By.res("products_list"))
    list.scroll(Direction.DOWN, 1f)
}

// Пример результатов: frameDurationCpuMs P50 16.2, P90 18.1, P95 22.3, P99 45.2
// jankyFrames count 12 (из 100 frames)
```

**Метрики**: P50 (median), P90/P95/P99 (percentile), `jankyFrames` — кадры, превысившие целевую длительность для текущей частоты обновления.

### Production Мониторинг

**FrameMetrics API** для runtime jank detection:

```kotlin
activity.window.addOnFrameMetricsAvailableListener({ _, metrics, _ ->
    val durationNs = metrics.getMetric(FrameMetrics.TOTAL_DURATION)
    val durationMs = durationNs / 1_000_000.0
    val frameIntervalMs = 16.67 // пример для 60 Гц; для 90/120 Гц порог меньше
    if (durationMs > frameIntervalMs) {
        analytics.logEvent("jank_detected", mapOf("duration_ms" to durationMs))
    }
}, Handler(Looper.getMainLooper()))
```

(В реальном приложении порог следует привязать к фактической частоте экрана.)

**Baseline Profiles** — заранее сгенерированные профили для AOT/JIT-оптимизации критичных путей (startup и ключевые user flows):

```kotlin
@Test
fun generateBaselineProfile() = rule.collect(
    packageName = "com.example.app",
    maxIterations = 15
) {
    startActivityAndWait()
    scrollProductsList()
    openProductDetails()
}
```

### Частые Ошибки

```kotlin
// ❌ 1. Тяжёлая логика внутри lambda/onClick или создание больших объектов на каждый recompose
Button(onClick = {
    // тяжёлая работа здесь приведёт к jank
    viewModel.increment()
}) { Text("Click") }

// ✅ Вынести тяжёлую работу из composable/onClick, либо использовать event-хендлер без лишних захватов
@Composable
fun CounterButton(viewModel: CounterViewModel) {
    val onClick = remember(viewModel) { { viewModel.increment() } }
    Button(onClick = onClick) { Text("Click") }
}

// ❌ 2. Подписка composable на большее состояние, чем необходимо
@Composable
fun BadComponent(state: AppState) {
    val user = state.user
    val products = state.products // Не используется, но держит зависимость от всего state
    Text(user.name)
}

// ✅ Сужаем зависимости до реально используемых полей
@Composable
fun GoodComponent(state: AppState) {
    val userName = state.user.name
    Text(userName)
}

// ❌ 3. Создание тяжёлых Modifier / объектов каждый recompose (например, сложные background/shadow/graphics)
Column(modifier = Modifier.fillMaxSize().padding(16.dp).background(Color.White)) { }

// ✅ Hoist/remember действительно тяжёлые объекты; простые цепочки Modifier обычно недороги
private val containerModifier = Modifier.fillMaxSize().padding(16.dp)

@Composable
fun Container(content: @Composable () -> Unit) {
    Column(modifier = containerModifier) { content() }
}
```

## Answer (EN)

"Jank" is UI stuttering when a frame misses its rendering deadline for the current display refresh rate (e.g., >16.67ms on 60Hz, >11.11ms on 90Hz). Main causes in Compose: excessive recompositions, heavy work on the UI thread, unoptimized lists, blocking calls on the main thread, and inefficient state usage.

### Detection Tools

**1. Layout Inspector** - visualize Compose hierarchy, enable "Highlight recompositions" to see how often composables are redrawn, inspect layers and measurements.

**2. Composition Tracing** - use Compose tracing/System Trace in Android Studio Profiler to inspect which composables recompose and how often.

**3. Macrobenchmark** - measure rendering and scroll performance, frame timing, jank count, and percentiles (P50/P90/P95/P99) for critical user journeys.

**4. FrameMetrics API** - monitor frame timings and jank at runtime in production builds.

### Key Optimization Techniques

**remember** - cache expensive computations inside a composable:

```kotlin
// ❌ Recomputed on every recomposition
@Composable
fun ExpensiveList(items: List<Item>) {
    val processed = items.map { processItem(it) }
    LazyColumn { items(processed) { ItemView(it) } }
}

// ✅ Cached, recomputed only when items change
@Composable
fun ExpensiveList(items: List<Item>) {
    val processed = remember(items) { items.map { processItem(it) } }
    LazyColumn { items(processed) { ItemView(it) } }
}
```

**derivedStateOf** - compute derived values and only recompose dependents when that value changes:

```kotlin
// ❌ showButton depends directly on listState and may change frequently
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()
    val showButton = listState.firstVisibleItemIndex > 0
    // ...
}

// ✅ Consumers of showButton update only when the condition changes (0 → 1+ and back)
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }
    // ...
}
```

**@Stable/@Immutable** - help Compose understand which types are stable for smarter skipping behavior:

```kotlin
// ⚠️ Unstable due to MutableList: mutations are not observable for Compose and can break expectations
data class User(val name: String, val posts: MutableList<Post>)

// ✅ Immutable data structure fits Compose stability model better
@Immutable
data class User(val name: String, val posts: List<Post>)
```

**Stability basics (Compose)**:
- stability is defined by Compose's stability model, not just `val` vs `var`;
- primitive types and most standard immutable types are treated as stable;
- mutable collections and mutable properties (`var`) can make a type unstable for skipping;
- `@Stable` / `@Immutable` annotations declare contracts that you must honor (no hidden mutations, etc.).

**LazyColumn keys** - use stable unique keys to preserve item identity and state when the list changes:

```kotlin
// ❌ Without keys, reordering can cause items to be recreated and state to be misaligned
LazyColumn {
    items(products) { product -> ProductItem(product) }
}

// ✅ With keys, Compose can better keep item identity/state across reorder/insert/remove
LazyColumn {
    items(products, key = { it.id }) { product -> ProductItem(product) }
}
```

### Macrobenchmark - Performance Measurement

```kotlin
@Test
fun scrollBenchmark() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(FrameTimingMetric()),
    iterations = 5
) {
    val list = device.findObject(By.res("products_list"))
    list.scroll(Direction.DOWN, 1f)
}

// Example results: frameDurationCpuMs P50 16.2, P90 18.1, P95 22.3, P99 45.2
// jankyFrames count 12 (out of 100 frames)
```

**Metrics**: P50 (median), P90/P95/P99 (percentiles), `jankyFrames` are frames exceeding the target duration for the current refresh rate.

### Production Monitoring

**FrameMetrics API** for runtime jank detection:

```kotlin
activity.window.addOnFrameMetricsAvailableListener({ _, metrics, _ ->
    val durationNs = metrics.getMetric(FrameMetrics.TOTAL_DURATION)
    val durationMs = durationNs / 1_000_000.0
    val frameIntervalMs = 16.67 // example threshold for 60Hz; use lower values for 90/120Hz
    if (durationMs > frameIntervalMs) {
        analytics.logEvent("jank_detected", mapOf("duration_ms" to durationMs))
    }
}, Handler(Looper.getMainLooper()))
```

(In a real app, base the threshold on the actual display refresh rate.)

**Baseline Profiles** - pre-generated profiles that guide AOT/JIT to optimize hot code paths (app startup and key user flows):

```kotlin
@Test
fun generateBaselineProfile() = rule.collect(
    packageName = "com.example.app",
    maxIterations = 15
) {
    startActivityAndWait()
    scrollProductsList()
    openProductDetails()
}
```

### Common Mistakes

```kotlin
// ❌ 1. Doing heavy work in onClick or capturing frequently changing state in lambdas used deep in the tree
Button(onClick = {
    // heavy work here will cause jank
    viewModel.increment()
}) { Text("Click") }

// ✅ Move heavy work out of composition and avoid unnecessary captures
@Composable
fun CounterButton(viewModel: CounterViewModel) {
    val onClick = remember(viewModel) { { viewModel.increment() } }
    Button(onClick = onClick) { Text("Click") }
}

// ❌ 2. Subscribing a composable to more state than it actually needs
@Composable
fun BadComponent(state: AppState) {
    val user = state.user
    val products = state.products // Not used, but ties recomposition to full state
    Text(user.name)
}

// ✅ Narrow dependencies to the specific fields you use
@Composable
fun GoodComponent(state: AppState) {
    val userName = state.user.name
    Text(userName)
}

// ❌ 3. Allocating heavy Modifiers/objects on every recomposition
Column(modifier = Modifier.fillMaxSize().padding(16.dp).background(Color.White)) { }

// ✅ Hoist/remember actually heavy objects; simple Modifier chains are usually cheap
private val containerModifier = Modifier.fillMaxSize().padding(16.dp)

@Composable
fun Container(content: @Composable () -> Unit) {
    Column(modifier = containerModifier) { content() }
}
```

---

## Follow-ups

1. Как использовать Layout Inspector для анализа recomposition в реальном времени? / How to use Layout Inspector to analyze recomposition in real-time?
2. В чем разница между `@Stable` и `@Immutable` и когда использовать каждую? / What's the difference between `@Stable` and `@Immutable` and when to use each?
3. Как настроить Macrobenchmark для CI/CD pipeline? / How to set up Macrobenchmark for CI/CD pipeline?
4. Какие метрики P50/P90/P95/P99 считаются приемлемыми для production? / What P50/P90/P95/P99 metrics are acceptable for production?
5. Как автоматически генерировать Baseline Profiles для release builds? / How to automatically generate Baseline Profiles for release builds?

## References

- [[c-jetpack-compose]]
- [[c-performance-optimization]]
- [[c-recomposition]]
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/topic/performance/vitals/render
- https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview

## Related Questions

### Prerequisites (Easier)
- [[q-what-needs-to-be-done-in-android-project-to-start-drawing-ui-on-screen--android--easy]] - UI Basics
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose Fundamentals

### Related (Same Level)
- [[q-compose-modifier-order-performance--android--medium]] - Compose Performance
- [[q-compositionlocal-advanced--android--medium]] - Compose State
- [[q-accessibility-compose--android--medium]] - Compose UI

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Advanced Performance
- [[q-compose-lazy-layout-optimization--android--hard]] - Lazy Layout Optimization
- [[q-compose-stability-skippability--android--hard]] - Stability Deep Dive
