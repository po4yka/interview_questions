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
date created: Saturday, November 1st 2025, 12:47:00 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)

> Как обнаружить и устранить проблемы производительности (jank) в Jetpack Compose приложениях?

# Question (EN)

> How do you detect and fix performance issues (jank) in Jetpack Compose apps?

---

## Ответ (RU)

**Jank** - "замирания" UI когда frame rate падает ниже 60fps (>16.67ms per frame). Главные причины в Compose: избыточные recompositions, медленные вычисления, неоптимизированные списки, блокировка UI thread.

### Инструменты Обнаружения

**1. Layout Inspector** - визуализация recompositions (красные границы, count, timing)
**2. Composition Tracing** - профилирование частоты recomposition в Android Studio Profiler
**3. Macrobenchmark** - измерение frame timing, jank count, P50/P90/P95/P99 метрики
**4. FrameMetrics API** - runtime мониторинг jank в production

### Ключевые Техники Оптимизации

**remember** - кэширование дорогих вычислений:

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

**derivedStateOf** - recompose только когда derived значение изменилось:

```kotlin
// ❌ Recompose при КАЖДОМ scroll pixel
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()
    val showButton = listState.firstVisibleItemIndex > 0
    // ...
}

// ✅ Recompose только когда условие изменилось (0 → 1+)
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }
    // ...
}
```

**@Stable/@Immutable** - стабильные классы для smart recomposition:

```kotlin
// ❌ Нестабильный класс - всегда recompose
data class User(val name: String, val posts: MutableList<Post>)

// ✅ Стабильный класс - recompose только при изменении
@Immutable
data class User(val name: String, val posts: List<Post>)
```

**Правила Stability**: Primitives/val stable, var unstable, immutable collections stable, mutable unstable, классы требуют `@Stable`/`@Immutable`.

**LazyColumn keys** - стабильные unique keys предотвращают recomposition:

```kotlin
// ❌ Без key - полный recompose при изменении порядка
LazyColumn {
    items(products) { product -> ProductItem(product) }
}

// ✅ С key - recompose только измененных элементов
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

// Результат: frameDurationCpuMs P50 16.2, P90 18.1, P95 22.3, P99 45.2
// jankyFrames count 12 (из 100 frames)
```

**Метрики**: P50 (median), P90/P95/P99 percentiles, Jank = frame >16.67ms.

### Production Мониторинг

**FrameMetrics API** для runtime jank detection:

```kotlin
activity.window.addOnFrameMetricsAvailableListener({ _, metrics, _ ->
    val duration = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000
    if (duration > 16.67) {
        analytics.logEvent("jank_detected", mapOf("duration_ms" to duration))
    }
}, Handler(Looper.getMainLooper()))
```

**Baseline Profiles** - AOT compilation для быстрого startup:

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
// ❌ 1. Lambda создает новый объект каждый recompose
Button(onClick = { viewModel.increment() }) { Text("Click") }

// ✅ remember lambda
val onClick = remember(viewModel) { { viewModel.increment() } }
Button(onClick = onClick) { Text("Click") }

// ❌ 2. Чтение всего State когда нужна часть
@Composable
fun BadComponent(state: AppState) {
    val user = state.user
    val products = state.products // Не используется!
    Text(user.name)
}

// ✅ Читаем только необходимое
@Composable
fun GoodComponent(state: AppState) {
    val userName = state.user.name
    Text(userName)
}

// ❌ 3. Modifier создается каждый recompose
Column(modifier = Modifier.fillMaxSize().padding(16.dp).background(Color.White)) { }

// ✅ Переиспользуем Modifier
private val containerModifier = Modifier.fillMaxSize().padding(16.dp)
Column(modifier = containerModifier) { }
```

## Answer (EN)

**Jank** is UI "stuttering" when frame rate drops below 60fps (>16.67ms per frame). Main causes in Compose: excessive recompositions, slow computations, unoptimized lists, blocking UI thread.

### Detection Tools

**1. Layout Inspector** - visualize recompositions (red borders, count, timing)
**2. Composition Tracing** - profile recomposition frequency in Android Studio Profiler
**3. Macrobenchmark** - measure frame timing, jank count, P50/P90/P95/P99 metrics
**4. FrameMetrics API** - runtime jank monitoring in production

### Key Optimization Techniques

**remember** - cache expensive computations:

```kotlin
// ❌ Recomputed every recompose
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

**derivedStateOf** - recompose only when derived value changes:

```kotlin
// ❌ Recompose on EVERY scroll pixel
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()
    val showButton = listState.firstVisibleItemIndex > 0
    // ...
}

// ✅ Recompose only when condition changes (0 → 1+)
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }
    // ...
}
```

**@Stable/@Immutable** - mark classes stable for smart recomposition:

```kotlin
// ❌ Unstable class - always recompose
data class User(val name: String, val posts: MutableList<Post>)

// ✅ Stable class - recompose only when changed
@Immutable
data class User(val name: String, val posts: List<Post>)
```

**Stability rules**: Primitives/val stable, var unstable, immutable collections stable, mutable unstable, classes need `@Stable`/`@Immutable` annotation.

**LazyColumn keys** - stable unique keys prevent unnecessary recomposition:

```kotlin
// ❌ No key - full recompose on order change
LazyColumn {
    items(products) { product -> ProductItem(product) }
}

// ✅ With key - recompose only changed items
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

// Result: frameDurationCpuMs P50 16.2, P90 18.1, P95 22.3, P99 45.2
// jankyFrames count 12 (out of 100 frames)
```

**Metrics**: P50 (median), P90/P95/P99 percentiles, Jank = frame >16.67ms.

### Production Monitoring

**FrameMetrics API** for runtime jank detection:

```kotlin
activity.window.addOnFrameMetricsAvailableListener({ _, metrics, _ ->
    val duration = metrics.getMetric(FrameMetrics.TOTAL_DURATION) / 1_000_000
    if (duration > 16.67) {
        analytics.logEvent("jank_detected", mapOf("duration_ms" to duration))
    }
}, Handler(Looper.getMainLooper()))
```

**Baseline Profiles** - AOT compilation for fast startup:

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
// ❌ 1. Lambda creates new object every recompose
Button(onClick = { viewModel.increment() }) { Text("Click") }

// ✅ remember lambda
val onClick = remember(viewModel) { { viewModel.increment() } }
Button(onClick = onClick) { Text("Click") }

// ❌ 2. Reading entire State when only need part
@Composable
fun BadComponent(state: AppState) {
    val user = state.user
    val products = state.products // Not used!
    Text(user.name)
}

// ✅ Read only what's needed
@Composable
fun GoodComponent(state: AppState) {
    val userName = state.user.name
    Text(userName)
}

// ❌ 3. Modifier created every recompose
Column(modifier = Modifier.fillMaxSize().padding(16.dp).background(Color.White)) { }

// ✅ Reuse Modifier
private val containerModifier = Modifier.fillMaxSize().padding(16.dp)
Column(modifier = containerModifier) { }
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
