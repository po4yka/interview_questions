---
id: kotlin-079
title: "Adaptive Layouts in Compose / Адаптивные layouts в Compose"
aliases: [Adaptive Layouts Compose, Адаптивные layouts Compose]
topic: kotlin
subtopics: [adaptive-layouts, jetpack-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-10-15
tags: [adaptive-layouts, difficulty/hard, jetpack-compose, kotlin/adaptive-layouts, kotlin/jetpack-compose, responsive-design, window-size-classes]
moc: moc-kotlin
related: [q-compose-custom-layout--kotlin--hard, q-compose-navigation-advanced--kotlin--medium, q-material3-components--kotlin--medium]
date created: Sunday, October 19th 2025, 1:47:08 pm
date modified: Sunday, November 2nd 2025, 12:05:08 pm
---

# Question (EN)
> How do you build adaptive layouts in Compose? What are window size classes? How do you handle phones, tablets, and foldables?

# Вопрос (RU)
> Как создавать адаптивные layouts в Compose? Что такое window size классы? Как обрабатывать телефоны, планшеты и складные устройства?

---

## Answer (EN)

Adaptive layouts adjust UI based on screen size, orientation, and form factor. Material 3 provides window size classes and adaptive components for responsive UIs.

**Window Size Classes:**

```kotlin
@Composable
fun AdaptiveScreen() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()    // < 600dp
        WindowWidthSizeClass.Medium -> MediumLayout()     // 600-840dp
        WindowWidthSizeClass.Expanded -> ExpandedLayout() // >= 840dp
    }
}
```

**Breakpoints:**
- Compact: < 600dp (phone portrait)
- Medium: 600-840dp (tablet portrait, phone landscape)
- Expanded: >= 840dp (tablet landscape, desktop)

**Adaptive Navigation:**

```kotlin
when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> {
        // Bottom navigation for phones
        Scaffold(bottomBar = { NavigationBar { ... } })
    }
    WindowWidthSizeClass.Medium -> {
        // Navigation rail for tablets
        Row {
            NavigationRail { ... }
            NavHost(...)
        }
    }
    WindowWidthSizeClass.Expanded -> {
        // Permanent drawer for desktop
        PermanentNavigationDrawer { ... }
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

LazyVerticalGrid(columns = GridCells.Fixed(columns)) { ... }
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
                Column(modifier = Modifier.weight(0.7f)) { ... }
            }
        }
    }
}
```

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

**Foldable Support:**

```kotlin
@Composable
fun FoldableAwareLayout() {
    val windowLayoutInfo = remember { mutableStateOf<WindowLayoutInfo?>(null) }

    LaunchedEffect(Unit) {
        WindowInfoTracker.getOrCreate(LocalContext.current as Activity)
            .windowLayoutInfo(LocalContext.current as Activity)
            .collect { windowLayoutInfo.value = it }
    }

    val foldingFeature = windowLayoutInfo.value?.displayFeatures
        ?.filterIsInstance<FoldingFeature>()?.firstOrNull()

    when {
        foldingFeature?.state == FoldingFeature.State.HALF_OPENED -> FoldedLayout()
        else -> NormalLayout()
    }
}
```

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

## Ответ (RU)

Адаптивные layouts подстраивают UI под размер экрана, ориентацию и форм-фактор. Material 3 предоставляет window size классы и адаптивные компоненты для responsive UI.

**Window Size Classes:**

```kotlin
@Composable
fun AdaptiveScreen() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()    // < 600dp
        WindowWidthSizeClass.Medium -> MediumLayout()     // 600-840dp
        WindowWidthSizeClass.Expanded -> ExpandedLayout() // >= 840dp
    }
}
```

**Точки останова:**
- Compact: < 600dp (телефон портрет)
- Medium: 600-840dp (планшет портрет, телефон ландшафт)
- Expanded: >= 840dp (планшет ландшафт, десктоп)

**Адаптивная навигация:**

```kotlin
when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> {
        // Нижняя навигация для телефонов
        Scaffold(bottomBar = { NavigationBar { ... } })
    }
    WindowWidthSizeClass.Medium -> {
        // Навигационная панель для планшетов
        Row {
            NavigationRail { ... }
            NavHost(...)
        }
    }
    WindowWidthSizeClass.Expanded -> {
        // Постоянный ящик для десктопа
        PermanentNavigationDrawer { ... }
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

LazyVerticalGrid(columns = GridCells.Fixed(columns)) { ... }
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
                Column(modifier = Modifier.weight(0.7f)) { ... }
            }
        }
    }
}
```

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

**Поддержка складных устройств:**

```kotlin
@Composable
fun FoldableAwareLayout() {
    val windowLayoutInfo = remember { mutableStateOf<WindowLayoutInfo?>(null) }

    LaunchedEffect(Unit) {
        WindowInfoTracker.getOrCreate(LocalContext.current as Activity)
            .windowLayoutInfo(LocalContext.current as Activity)
            .collect { windowLayoutInfo.value = it }
    }

    val foldingFeature = windowLayoutInfo.value?.displayFeatures
        ?.filterIsInstance<FoldingFeature>()?.firstOrNull()

    when {
        foldingFeature?.state == FoldingFeature.State.HALF_OPENED -> FoldedLayout()
        else -> NormalLayout()
    }
}
```

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

---

## Follow-ups

- How do you test adaptive layouts on different screen sizes?
- What's the difference between WindowSizeClass and BoxWithConstraints?
- How do you handle multi-window mode in adaptive layouts?
- What are canonical layouts in Material Design?
- How do you implement adaptive typography and spacing?

## References

- [Material 3 Adaptive Design](https://m3.material.io/foundations/adaptive-design)
- [Window Size Classes](https://developer.android.com/guide/topics/large-screens/support-different-screen-sizes)
- [Compose Adaptive Layouts](https://developer.android.com/jetpack/compose/layouts/adaptive)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - Coroutine fundamentals
- [[q-kotlin-flow-basics--kotlin--medium]] - Flow basics

### Related (Medium)
- [[q-compose-side-effects-coroutines--kotlin--medium]] - Compose side effects
- [[q-coroutine-builders-comparison--kotlin--medium]] - Coroutine patterns
