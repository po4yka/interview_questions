---
id: kotlin-079
title: "Adaptive Layouts in Compose / Адаптивные layouts в Compose"
aliases: [Adaptive Layouts Compose, Адаптивные layouts Compose]
topic: kotlin
subtopics: [jetpack-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
tags: [adaptive-layouts, difficulty/hard, jetpack-compose, kotlin/adaptive-layouts, kotlin/jetpack-compose, responsive-design, window-size-classes]
moc: moc-kotlin
related: [c-jetpack-compose, c-window-size-class, q-android-jetpack-overview--android--easy]
date created: Sunday, October 19th 2025, 1:47:08 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---

# Вопрос (RU)
> Как создавать адаптивные layouts в Compose? Что такое window size классы? Как обрабатывать телефоны, планшеты и складные устройства?

---

# Question (EN)
> How do you build adaptive layouts in Compose? What are window size classes? How do you handle phones, tablets, and foldables?

## Ответ (RU)

Адаптивные layouts подстраивают UI под размер экрана, ориентацию и форм-фактор. В Compose на Android основой являются window size классы (Material 3 / material3-window-size-class) и адаптивные компоненты, а также вспомогательные API (`BoxWithConstraints`, `Configuration`, `WindowManager`) — они используются совместно.

**Window Size Classes:**

```kotlin
@Composable
fun AdaptiveScreen(activity: Activity) {
    val windowSizeClass = calculateWindowSizeClass(activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()    // обычно < 600dp
        WindowWidthSizeClass.Medium -> MediumLayout()     // обычно 600-840dp
        WindowWidthSizeClass.Expanded -> ExpandedLayout() // обычно >= 840dp
    }
}
```

(В реальном приложении `windowSizeClass`, как правило, вычисляется на уровне `Activity`/entry-point и пробрасывается вниз по иерархии, а не через небезопасный cast `LocalContext.current as Activity`.)

**Точки останова (ориентировочные):**
- Compact: < 600dp (часто телефон в портретной ориентации)
- Medium: 600-840dp (часто планшет в портретной, телефон в ландшафтной)
- Expanded: >= 840dp (часто планшет в ландшафтной, десктоп)

Это не жесткая привязка к типу устройства, а рекомендуемые диапазоны для адаптации layout.

**Адаптивная навигация:**

```kotlin
when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> {
        // Нижняя навигация для компактных ширин
        Scaffold(bottomBar = { NavigationBar { /* ... */ } }) { innerPadding ->
            NavHost(/* modifier = Modifier.padding(innerPadding), ... */)
        }
    }
    WindowWidthSizeClass.Medium -> {
        // NavigationRail для средних ширин
        Row {
            NavigationRail { /* ... */ }
            NavHost(/* ... */)
        }
    }
    WindowWidthSizeClass.Expanded -> {
        // Постоянный drawer для широких экранов
        PermanentNavigationDrawer(drawerContent = { /* ... */ }) {
            NavHost(/* ... */)
        }
    }
}
```

**Паттерн список-детали:**

```kotlin
when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> {
        // Одна панель: навигация между списком и деталями
        if (selectedItem == null) ItemList() else ItemDetail()
    }
    else -> {
        // Две панели: список и детали бок о бок
        Row {
            ItemList(modifier = Modifier.weight(0.4f))
            ItemDetail(modifier = Modifier.weight(0.6f))
        }
    }
}
```

**Отзывчивая сетка:**

```kotlin
val columns = when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> 2
    WindowWidthSizeClass.Medium -> 3
    WindowWidthSizeClass.Expanded -> 4
    else -> 2
}

LazyVerticalGrid(columns = GridCells.Fixed(columns)) {
    // items(...)
}
```

**BoxWithConstraints для детального контроля:**

```kotlin
@Composable
fun AdaptiveContent() {
    BoxWithConstraints {
        if (maxWidth < 600.dp) {
            Column { Header(); Content(); Footer() }
        } else {
            Row {
                Sidebar(modifier = Modifier.weight(0.3f))
                Column(modifier = Modifier.weight(0.7f)) { /* ... */ }
            }
        }
    }
}
```

`BoxWithConstraints` хорошо подходит для тонкой настройки внутри экрана и дополняет window size classes, а не заменяет их.

**Обработка ориентации:**

```kotlin
val configuration = LocalConfiguration.current
val isLandscape = configuration.orientation == Configuration.ORIENTATION_LANDSCAPE

if (isLandscape) {
    Row {
        VideoPlayer(modifier = Modifier.weight(0.6f))
        Comments(modifier = Modifier.weight(0.4f))
    }
} else {
    Column {
        VideoPlayer(modifier = Modifier.fillMaxWidth())
        Comments(modifier = Modifier.weight(1f))
    }
}
```

Ориентация — дополнительный сигнал, но основным должно быть поведение по размеру и доступному пространству.

**Поддержка складных устройств:**

```kotlin
@Composable
fun FoldableAwareLayout(activity: Activity) {
    val windowLayoutInfoState = remember { mutableStateOf<WindowLayoutInfo?>(null) }

    LaunchedEffect(activity) {
        WindowInfoTracker.getOrCreate(activity)
            .windowLayoutInfo(activity)
            .collect { info -> windowLayoutInfoState.value = info }
    }

    val foldingFeature = windowLayoutInfoState.value?.displayFeatures
        ?.filterIsInstance<FoldingFeature>()
        ?.firstOrNull()

    when {
        foldingFeature != null &&
            foldingFeature.isSeparating &&
            foldingFeature.state == FoldingFeature.State.HALF_OPENED -> {
            // Пример: разделить контент по обе стороны шарнира
            FoldedLayout()
        }
        else -> NormalLayout()
    }
}
```

(Реальная логика должна учитывать позицию и ориентацию шарнира, состояние `FULLY_OPENED`/`HALF_OPENED` и сценарии одного/двух экранов.)

**Адаптивные компоненты Material 3:**

```kotlin
@OptIn(ExperimentalMaterial3AdaptiveApi::class)
@Composable
fun Material3AdaptiveNav() {
    val navigator = rememberListDetailPaneScaffoldNavigator<String>()

    ListDetailPaneScaffold(
        directive = navigator.scaffoldDirective,
        value = navigator.scaffoldValue,
        listPane = { AnimatedPane { ItemList() } },
        detailPane = { AnimatedPane { ItemDetail() } }
    )
}
```

## Дополнительные Вопросы (RU)

- Как тестировать адаптивные layouts на разных размерах экранов?
- В чем разница между `WindowSizeClass` и `BoxWithConstraints`?
- Как обрабатывать multi-window режим в адаптивных layouts?
- Что такое канонические layouts в Material Design?
- Как реализовать адаптивную типографику и отступы?

## Ссылки (RU)

- [Material 3 Adaptive Design](https://m3.material.io/foundations/adaptive-design)
- [Window Size Classes](https://developer.android.com/guide/topics/large-screens/support-different-screen-sizes)
- [Compose Adaptive Layouts](https://developer.android.com/jetpack/compose/layouts/adaptive)
- [[c-jetpack-compose]]

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-what-is-coroutine--kotlin--easy]] - основы `Coroutine`
- [[q-kotlin-flow-basics--kotlin--medium]] - основы `Flow`

### Связанные (средней сложности)
- [[q-compose-side-effects-coroutines--kotlin--medium]] - сайд-эффекты в Compose
- [[q-coroutine-builders-comparison--kotlin--medium]] - паттерны `Coroutine`

---

## Answer (EN)

Adaptive layouts adjust UI based on screen size, orientation, and form factor. In Compose on Android, the core tools are window size classes (Material 3 / material3-window-size-class) and adaptive components, plus helper APIs (`BoxWithConstraints`, `Configuration`, `WindowManager`). These are meant to be used together.

**Window Size Classes:**

```kotlin
@Composable
fun AdaptiveScreen(activity: Activity) {
    val windowSizeClass = calculateWindowSizeClass(activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()    // typically < 600dp
        WindowWidthSizeClass.Medium -> MediumLayout()     // typically 600-840dp
        WindowWidthSizeClass.Expanded -> ExpandedLayout() // typically >= 840dp
    }
}
```

(In a real app, `windowSizeClass` is usually computed at the `Activity`/entry point level and passed down, rather than relying on an unsafe `LocalContext.current as Activity` cast inside arbitrary composables.)

**Breakpoints (guidelines, not device types):**
- Compact: < 600dp (often phone portrait)
- Medium: 600-840dp (often tablet portrait, phone landscape)
- Expanded: >= 840dp (often tablet landscape, desktop)

Treat these as recommended ranges for adapting layouts, not strict mappings to specific devices.

**Adaptive Navigation:**

```kotlin
when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> {
        // Bottom navigation for compact widths
        Scaffold(bottomBar = { NavigationBar { /* ... */ } }) { innerPadding ->
            NavHost(/* modifier = Modifier.padding(innerPadding), ... */)
        }
    }
    WindowWidthSizeClass.Medium -> {
        // NavigationRail for medium widths
        Row {
            NavigationRail { /* ... */ }
            NavHost(/* ... */)
        }
    }
    WindowWidthSizeClass.Expanded -> {
        // Permanent drawer for large widths
        PermanentNavigationDrawer(drawerContent = { /* ... */ }) {
            NavHost(/* ... */)
        }
    }
}
```

**List-Detail Pattern:**

```kotlin
when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> {
        // Single pane: navigate between list and detail
        if (selectedItem == null) ItemList() else ItemDetail()
    }
    else -> {
        // Two pane: list and detail side by side
        Row {
            ItemList(modifier = Modifier.weight(0.4f))
            ItemDetail(modifier = Modifier.weight(0.6f))
        }
    }
}
```

**Responsive Grid:**

```kotlin
val columns = when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> 2
    WindowWidthSizeClass.Medium -> 3
    WindowWidthSizeClass.Expanded -> 4
    else -> 2
}

LazyVerticalGrid(columns = GridCells.Fixed(columns)) {
    // items(...)
}
```

**BoxWithConstraints for Fine Control:**

```kotlin
@Composable
fun AdaptiveContent() {
    BoxWithConstraints {
        if (maxWidth < 600.dp) {
            Column { Header(); Content(); Footer() }
        } else {
            Row {
                Sidebar(modifier = Modifier.weight(0.3f))
                Column(modifier = Modifier.weight(0.7f)) { /* ... */ }
            }
        }
    }
}
```

`BoxWithConstraints` is great for local decisions inside a screen and complements window size classes instead of replacing them.

**Orientation Handling:**

```kotlin
val configuration = LocalConfiguration.current
val isLandscape = configuration.orientation == Configuration.ORIENTATION_LANDSCAPE

if (isLandscape) {
    Row {
        VideoPlayer(modifier = Modifier.weight(0.6f))
        Comments(modifier = Modifier.weight(0.4f))
    }
} else {
    Column {
        VideoPlayer(modifier = Modifier.fillMaxWidth())
        Comments(modifier = Modifier.weight(1f))
    }
}
```

Orientation is an additional signal; primary behavior should be based on available size/space.

**Foldable Support:**

```kotlin
@Composable
fun FoldableAwareLayout(activity: Activity) {
    val windowLayoutInfoState = remember { mutableStateOf<WindowLayoutInfo?>(null) }

    LaunchedEffect(activity) {
        WindowInfoTracker.getOrCreate(activity)
            .windowLayoutInfo(activity)
            .collect { info -> windowLayoutInfoState.value = info }
    }

    val foldingFeature = windowLayoutInfoState.value?.displayFeatures
        ?.filterIsInstance<FoldingFeature>()
        ?.firstOrNull()

    when {
        foldingFeature != null &&
            foldingFeature.isSeparating &&
            foldingFeature.state == FoldingFeature.State.HALF_OPENED -> {
            // Example: split content across the hinge
            FoldedLayout()
        }
        else -> NormalLayout()
    }
}
```

(In production code, you should also consider the hinge position/orientation and other states such as `FULLY_OPENED`, and design single- vs dual-pane layouts accordingly.)

**Material 3 Adaptive Components:**

```kotlin
@OptIn(ExperimentalMaterial3AdaptiveApi::class)
@Composable
fun Material3AdaptiveNav() {
    val navigator = rememberListDetailPaneScaffoldNavigator<String>()

    ListDetailPaneScaffold(
        directive = navigator.scaffoldDirective,
        value = navigator.scaffoldValue,
        listPane = { AnimatedPane { ItemList() } },
        detailPane = { AnimatedPane { ItemDetail() } }
    )
}
```

## Follow-ups

- How do you test adaptive layouts on different screen sizes?
- What's the difference between `WindowSizeClass` and `BoxWithConstraints`?
- How do you handle multi-window mode in adaptive layouts?
- What are canonical layouts in Material Design?
- How do you implement adaptive typography and spacing?

## References

- [Material 3 Adaptive Design](https://m3.material.io/foundations/adaptive-design)
- [Window Size Classes](https://developer.android.com/guide/topics/large-screens/support-different-screen-sizes)
- [Compose Adaptive Layouts](https://developer.android.com/jetpack/compose/layouts/adaptive)
- [[c-jetpack-compose]]

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - `Coroutine` fundamentals
- [[q-kotlin-flow-basics--kotlin--medium]] - `Flow` basics

### Related (Medium)
- [[q-compose-side-effects-coroutines--kotlin--medium]] - Compose side effects
- [[q-coroutine-builders-comparison--kotlin--medium]] - `Coroutine` patterns
