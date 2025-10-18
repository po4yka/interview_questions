---
id: 20251017-144929
title: "Performance Monitoring Jank Compose / Мониторинг производительности и джанка в Compose"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-what-needs-to-be-done-in-android-project-to-start-drawing-ui-on-screen--android--easy, q-what-are-px-dp-sp--android--easy, q-what-are-the-navigation-methods-in-kotlin--android--medium]
created: 2025-10-15
tags: [jetpack-compose, performance, jank, profiling, optimization, difficulty/medium]
---
# Performance Monitoring and Jank Detection in Compose

**English**: How do you detect and fix performance issues (jank) in Jetpack Compose apps?

## Answer (EN)

**Jank** - "замирания" UI когда frame rate падает ниже 60fps (16.67ms per frame). Главные причины в Compose: избыточные recompositions, медленные вычисления, неоптимизированные списки, блокировка UI thread.

**Инструменты обнаружения:** (1) Layout Inspector - визуализация recompositions, count, timing, (2) Composition Tracing - профилирование частоты recomposition, (3) Macrobenchmark - измерение frame timing, jank count, P50/P90/P95/P99 метрики, (4) FrameMetrics API - runtime мониторинг jank в production.

**Техники оптимизации:** (1) **remember** - кэширование дорогих вычислений, (2) **derivedStateOf** - recompose только когда derived значение изменилось, (3) **@Stable/@Immutable** - стабильные классы для smart recomposition, (4) **LazyColumn keys** - стабильные unique keys предотвращают recomposition, (5) **Modifier reuse** - избегать создания новых Modifiers каждый recompose.

**Правила Stability:** Primitives stable, `val` stable, `var` unstable, immutable collections stable, mutable unstable, классы требуют `@Stable`/`@Immutable`.

## Ответ (RU)

**Jank** - это "замирания" UI когда frame rate падает ниже 60fps (16.67ms per frame). В Compose главные причины: избыточные recompositions, медленные вычисления, неоптимизированные списки.

### What is Jank?

```
Perfect:  60fps (16.67ms per frame)
Jank:             Пропущенные frames
         ^            ^
         Задержка!    Видимое замирание
```

**Причины jank в Compose**:
1. Избыточные recompositions (ненужные перерисовки)
2. Медленные вычисления в composable функциях
3. Неоптимизированные LazyColumn/LazyRow
4. Blocking UI thread (IO/CPU работа)
5. Large memory allocations

### Layout Inspector - Visualizing Recompositions

```kotlin
// Android Studio → Tools → Layout Inspector → Live Updates

@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        // - Recompose только когда count изменяется
        Text("Count: $count")

        // - ПРОБЛЕМА: всегда recompose при каждом изменении
        Text("Current time: ${System.currentTimeMillis()}")

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Layout Inspector показывает**:
-  Красные границы - recomposed компоненты
-  Количество recompositions
- ⏱ Время выполнения

### Recomposition Profiling

```kotlin
// Включите Composition Tracing
// Android Studio → Run → Edit Configurations → Profiling → Enable Composition Tracing

@Composable
fun ProductsList(products: List<Product>) {
    LazyColumn {
        items(products) { product ->
            // Profiler покажет сколько раз recompose
            ProductItem(product)
        }
    }
}

// Анализ в Android Studio Profiler:
// - Количество recompositions
// - Время каждой recomposition
// - Skipped recompositions (оптимизация сработала)
```

### remember - Avoiding Unnecessary Computations

```kotlin
// - НЕПРАВИЛЬНО - вычисляется каждый recompose
@Composable
fun ExpensiveComponent(items: List<Item>) {
    val processedItems = items.map { processItem(it) } // Каждый раз!

    LazyColumn {
        items(processedItems) { item ->
            ItemView(item)
        }
    }
}

// - ПРАВИЛЬНО - кэшируем результат
@Composable
fun ExpensiveComponent(items: List<Item>) {
    val processedItems = remember(items) {
        items.map { processItem(it) } // Только когда items изменился
    }

    LazyColumn {
        items(processedItems) { item ->
            ItemView(item)
        }
    }
}
```

### derivedStateOf - Computed State

```kotlin
// - НЕПРАВИЛЬНО - каждое изменение listState → recompose
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()

    // Recompose при КАЖДОМ scroll pixel!
    val showButton = listState.firstVisibleItemIndex > 0

    LazyColumn(state = listState) {
        items(100) { index ->
            Text("Item $index")
        }
    }

    if (showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}

// - ПРАВИЛЬНО - derivedStateOf для условий
@Composable
fun ScrollableList() {
    val listState = rememberLazyListState()

    // Recompose только когда ЗНАЧЕНИЕ изменилось (0 → 1+)
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    LazyColumn(state = listState) {
        items(100) { index ->
            Text("Item $index")
        }
    }

    if (showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}
```

### Stability - Key to Optimization

```kotlin
// - НЕСТАБИЛЬНЫЙ класс - всегда recompose
data class User(
    val name: String,
    val posts: MutableList<Post> // Mutable = unstable!
)

@Composable
fun UserProfile(user: User) {
    // Всегда recompose, даже если user не изменился
    Text(user.name)
}

// - СТАБИЛЬНЫЙ класс - recompose только при изменении
@Immutable // или @Stable
data class User(
    val name: String,
    val posts: List<Post> // Immutable list
)

@Composable
fun UserProfile(user: User) {
    // Recompose только когда user изменился
    Text(user.name)
}
```

**Правила Stability**:
- Primitives (Int, String, Boolean) - stable
- `val` properties - stable
- `var` properties - unstable
- Mutable collections (MutableList) - unstable
- Immutable collections (List) - stable
- Классы с `@Stable` или `@Immutable` - stable

### @Stable и @Immutable

```kotlin
// @Immutable - обещаем что НИКОГДА не изменится
@Immutable
data class Product(
    val id: Int,
    val name: String,
    val price: Double
)

// @Stable - может изменяться, но уведомим Compose
@Stable
class UserState(initialName: String) {
    var name by mutableStateOf(initialName)
        private set

    fun updateName(newName: String) {
        name = newName // Compose знает об изменении
    }
}

// Без аннотации - unstable
class SearchQuery {
    var query: String = "" // Compose НЕ знает когда изменилось
}
```

### LazyColumn/LazyRow Optimization

```kotlin
// - НЕПРАВИЛЬНО - нестабильный key
@Composable
fun ProductsList(products: List<Product>) {
    LazyColumn {
        items(products) { product -> // Без key!
            ProductItem(product)
        }
    }
}

// - ПРАВИЛЬНО - стабильный unique key
@Composable
fun ProductsList(products: List<Product>) {
    LazyColumn {
        items(
            items = products,
            key = { product -> product.id } // Stable unique key
        ) { product ->
            ProductItem(product)
        }
    }
}

// - ПРАВИЛЬНО - contentType для mixed lists
@Composable
fun MixedList(items: List<ListItem>) {
    LazyColumn {
        items(
            items = items,
            key = { it.id },
            contentType = { item ->
                when (item) {
                    is HeaderItem -> "header"
                    is ProductItem -> "product"
                    is AdItem -> "ad"
                }
            }
        ) { item ->
            when (item) {
                is HeaderItem -> Header(item)
                is ProductItem -> Product(item)
                is AdItem -> Ad(item)
            }
        }
    }
}
```

### Modifier Reuse

```kotlin
// - НЕПРАВИЛЬНО - новый Modifier каждый recompose
@Composable
fun BadComponent() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .background(Color.White) // Новый объект каждый раз!
    ) {
        // content
    }
}

// - ПРАВИЛЬНО - переиспользуем Modifier
private val containerModifier = Modifier
    .fillMaxSize()
    .padding(16.dp)
    .background(Color.White)

@Composable
fun GoodComponent() {
    Column(modifier = containerModifier) {
        // content
    }
}

// - Или remember для dynamic modifiers
@Composable
fun DynamicComponent(backgroundColor: Color) {
    val containerModifier = remember(backgroundColor) {
        Modifier
            .fillMaxSize()
            .padding(16.dp)
            .background(backgroundColor)
    }

    Column(modifier = containerModifier) {
        // content
    }
}
```

### Macrobenchmark - измерение performance

```kotlin
// app/build.gradle
plugins {
    id 'androidx.benchmark'
}

dependencies {
    androidTestImplementation 'androidx.benchmark:benchmark-macro-junit4:1.2.0'
}

// Macrobenchmark test
@RunWith(AndroidJUnit4::class)
class ScrollBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun scrollProductsList() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(
            FrameTimingMetric(), // Jank detection
            StartupTimingMetric()
        ),
        iterations = 5,
        setupBlock = {
            pressHome()
            startActivityAndWait()
        }
    ) {
        // Scroll list
        val list = device.findObject(By.res("products_list"))
        list.scroll(Direction.DOWN, 1f)
        list.scroll(Direction.DOWN, 1f)
        list.scroll(Direction.DOWN, 1f)
    }
}

// Результат:
// frameDurationCpuMs   P50   16.2,   P90   18.1,   P95   22.3,   P99   45.2
// jankyFrames          count 12      (из 100 frames)
```

**Метрики**:
- **P50** (median) - 50% frames быстрее
- **P90** - 90% frames быстрее
- **P95** - 95% frames быстрее
- **P99** - 99% frames быстрее
- **Jank** - frame > 16.67ms

### Baseline Profiles - AOT compilation

```kotlin
// benchmark/src/main/AndroidManifest.xml
<profileable android:shell="true" />

// Генерация baseline profile
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generateBaselineProfile() = rule.collect(
        packageName = "com.example.app",
        maxIterations = 15,
        stableIterations = 3
    ) {
        pressHome()
        startActivityAndWait()

        // Navigate typical user flows
        scrollProductsList()
        openProductDetails()
        addToCart()
        checkout()
    }
}

// Результат: app/src/main/baseline-prof.txt
// ART скомпилирует эти методы при установке → быстрее startup
```

### TrackFrameMetrics - runtime monitoring

```kotlin
// В production коде
class PerformanceMonitor {
    fun startMonitoring(activity: ComponentActivity) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            activity.window.addOnFrameMetricsAvailableListener(
                { _, frameMetrics, _ ->
                    val totalDuration = frameMetrics.getMetric(
                        FrameMetrics.TOTAL_DURATION
                    ) / 1_000_000 // Nanoseconds to milliseconds

                    if (totalDuration > 16.67) {
                        // Jank detected!
                        logJank(totalDuration)
                    }
                },
                Handler(Looper.getMainLooper())
            )
        }
    }

    private fun logJank(duration: Double) {
        analytics.logEvent("jank_detected", mapOf(
            "duration_ms" to duration,
            "screen" to currentScreen
        ))
    }
}
```

### Recomposition Debugging

```kotlin
// Debug composable для отслеживания recompositions
@Composable
fun <T> LogCompositions(tag: String, value: T) {
    val ref = rememberRef(value)

    SideEffect {
        if (ref.value != value) {
            Log.d("Recomposition", "$tag recomposed: $value")
            ref.value = value
        }
    }
}

@Composable
fun <T> rememberRef(value: T): MutableState<T> {
    val ref = remember { mutableStateOf(value) }
    return ref
}

// Использование
@Composable
fun ProductItem(product: Product) {
    LogCompositions("ProductItem", product.id)

    // Теперь видим в logcat когда и почему recompose
    Row {
        Text(product.name)
        Text(product.price.toString())
    }
}
```

### Common Performance Issues

```kotlin
// - 1. Lambda в parameters создает новый объект
@Composable
fun BadButton() {
    Button(
        onClick = { viewModel.increment() } // Новый lambda каждый раз!
    ) {
        Text("Click")
    }
}

// - Fix: remember lambda
@Composable
fun GoodButton(viewModel: CounterViewModel) {
    val onClick = remember(viewModel) {
        { viewModel.increment() }
    }

    Button(onClick = onClick) {
        Text("Click")
    }
}

// - 2. Чтение State в composable без необходимости
@Composable
fun BadComponent(state: AppState) {
    // Recompose при ЛЮБОМ изменении AppState!
    val user = state.user
    val products = state.products
    val cart = state.cart

    Text(user.name) // Используем только user!
}

// - Fix: read only необходимый state
@Composable
fun GoodComponent(state: AppState) {
    val userName = state.user.name // Только имя

    Text(userName)
}

// - 3. Expensive вычисления без remember
@Composable
fun BadList(items: List<Item>) {
    val sortedItems = items.sortedBy { it.name } // Каждый recompose!

    LazyColumn {
        items(sortedItems) { item ->
            ItemView(item)
        }
    }
}

// - Fix: remember вычисления
@Composable
fun GoodList(items: List<Item>) {
    val sortedItems = remember(items) {
        items.sortedBy { it.name }
    }

    LazyColumn {
        items(sortedItems) { item ->
            ItemView(item)
        }
    }
}

// - 4. State hoisting без необходимости
@Composable
fun BadScreen() {
    var query by remember { mutableStateOf("") }

    Column {
        SearchBar(query = query, onQueryChange = { query = it })
        // Оба recompose при каждом изменении query!
        FilterPanel(query = query)
    }
}

// - Fix: держите state максимально близко
@Composable
fun GoodScreen() {
    Column {
        SearchBar() // State внутри
        FilterPanel() // Независимый
    }
}
```

### Layout Inspector для анализа

```
Android Studio → Tools → Layout Inspector

Проверяйте:
1. Recomposition Count - высокие значения = проблема
2. Skipped Recompositions - высокие = хорошая оптимизация
3. Composition время - slow composables
4. Layout depth - глубокая вложенность = медленно
```

### Performance Best Practices

```kotlin
// - 1. Используйте @Stable/@Immutable
@Immutable
data class Product(val id: Int, val name: String)

// - 2. remember для expensive вычислений
val processed = remember(data) { processData(data) }

// - 3. derivedStateOf для вычисляемого state
val showButton by remember { derivedStateOf { scrollState.value > 100 } }

// - 4. key в LazyColumn
items(products, key = { it.id }) { product -> }

// - 5. Избегайте чтения State без необходимости
// - val all = state.everything
// - val needed = state.specificField

// - 6. Переиспользуйте Modifiers
private val cardModifier = Modifier.fillMaxWidth().padding(8.dp)

// - 7. Используйте contentType для mixed lists
contentType = { item -> item::class.simpleName }

// - 8. Lazy composition где возможно
LazyColumn { items { } } // GOOD
Column { items.forEach { } } // - для больших списков

// - 9. Профилируйте регулярно
// Macrobenchmark тесты в CI/CD

// - 10. Мониторьте jank в production
// Firebase Performance Monitoring, Custom analytics
```

### Tools Summary

| Tool | Use Case | When |
|------|----------|------|
| **Layout Inspector** | Визуализация recompositions | Development |
| **Profiler** | CPU/Memory analysis | Development |
| **Macrobenchmark** | Измерение jank | CI/CD |
| **Baseline Profiles** | Optimize startup | Release |
| **FrameMetrics API** | Runtime monitoring | Production |

**English**: **Jank** is UI "stuttering" when frame rate drops below 60fps (16.67ms per frame). Main causes in Compose: excessive recompositions, slow computations, unoptimized lists, blocking UI thread.

**Detection tools**: (1) **Layout Inspector** - visualize recompositions (red borders), count, timing. (2) **Composition Tracing** - profile recomposition frequency. (3) **Macrobenchmark** - measure frame timing, jank count, P50/P90/P95/P99 metrics. (4) **FrameMetrics API** - runtime jank monitoring in production.

**Optimization techniques**: (1) **remember** - cache expensive computations. (2) **derivedStateOf** - recompose only when derived value changes. (3) **@Stable/@Immutable** - mark classes stable to enable smart recomposition. (4) **LazyColumn keys** - stable unique keys prevent unnecessary recomposition. (5) **Modifier reuse** - avoid creating new Modifiers each recompose.

**Stability rules**: Primitives stable. `val` stable, `var` unstable. Immutable collections stable, mutable unstable. Classes need `@Stable`/`@Immutable` annotation.

**Common issues**: Lambda in parameters creates new object. Reading entire state when only need part. Expensive computations without remember. State hoisting too high. Deep layout nesting. No keys in LazyColumn.

**Production monitoring**: Use Baseline Profiles for AOT compilation. FrameMetrics API for runtime jank detection. Firebase Performance Monitoring. Custom analytics for jank events. Macrobenchmark in CI/CD.


---

## Related Questions

### Related (Medium)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Performance, Compose
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose
- [[q-accessibility-compose--accessibility--medium]] - Compose
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Compose

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Performance, Compose
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]] - Performance, Compose
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose
