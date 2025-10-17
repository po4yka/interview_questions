---
id: 20251012-400008
title: "Adaptive Layouts in Compose / Адаптивные layouts в Compose"
topic: android
difficulty: hard
status: draft
created: 2025-10-12
tags: - android
  - jetpack-compose
  - adaptive-layouts
  - responsive-design
  - window-size-classes
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-android
related_questions:   - q-windowinsets-edge-to-edge--android--medium
  - q-jetpack-compose-basics--android--medium
  - q-material3-components--material-design--easy
slug: adaptive-layouts-compose-jetpack-compose-hard
subtopics:   - jetpack-compose
  - adaptive-layouts
  - responsive-design
  - window-size-classes
  - foldables
---
# Adaptive Layouts in Compose

## English Version

### Problem Statement

Adaptive layouts adjust UI based on screen size, orientation, and form factor (phone, tablet, foldable). Material 3 and Compose provide window size classes and adaptive components for building responsive UIs that work across all devices.

**The Question:** How do you build adaptive layouts in Compose? What are window size classes? How do you handle phones, tablets, and foldables? What are best practices for responsive design?

### Detailed Answer

---

### WINDOW SIZE CLASSES

**Add dependency:**
```gradle
dependencies {
    implementation "androidx.compose.material3:material3-window-size-class:1.1.2"
}
```

**Basics:**
```kotlin
@Composable
fun AdaptiveScreen() {
    val windowSizeClass = calculateWindowSizeClass(activity = LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Phone in portrait: width < 600dp
            CompactLayout()
        }
        WindowWidthSizeClass.Medium -> {
            // Tablet in portrait, phone in landscape: 600dp <= width < 840dp
            MediumLayout()
        }
        WindowWidthSizeClass.Expanded -> {
            // Tablet in landscape, desktop: width >= 840dp
            ExpandedLayout()
        }
    }
}

@Composable
fun CompactLayout() {
    // Single column, bottom navigation
    Scaffold(
        bottomBar = { BottomNavigationBar() }
    ) { paddingValues ->
        Column(modifier = Modifier.padding(paddingValues)) {
            Content()
        }
    }
}

@Composable
fun MediumLayout() {
    // Single column with navigation rail
    Row {
        NavigationRail()
        Column(modifier = Modifier.weight(1f)) {
            Content()
        }
    }
}

@Composable
fun ExpandedLayout() {
    // Two columns with permanent navigation drawer
    Row {
        NavigationDrawer()
        Column(modifier = Modifier.weight(1f)) {
            Content()
        }
    }
}
```

**Window size class breakpoints:**
```
WindowWidthSizeClass:
- Compact: width < 600dp (phone portrait)
- Medium: 600dp <= width < 840dp (tablet portrait, phone landscape)
- Expanded: width >= 840dp (tablet landscape, desktop)

WindowHeightSizeClass:
- Compact: height < 480dp (phone landscape)
- Medium: 480dp <= height < 900dp (phone portrait)
- Expanded: height >= 900dp (tablet)
```

---

### ADAPTIVE NAVIGATION

```kotlin
@Composable
fun AdaptiveNavigation() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)
    val navController = rememberNavController()

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Bottom navigation for phones
            Scaffold(
                bottomBar = {
                    NavigationBar {
                        NavigationBarItem(
                            icon = { Icon(Icons.Default.Home, null) },
                            label = { Text("Home") },
                            selected = true,
                            onClick = { navController.navigate("home") }
                        )
                        NavigationBarItem(
                            icon = { Icon(Icons.Default.Search, null) },
                            label = { Text("Search") },
                            selected = false,
                            onClick = { navController.navigate("search") }
                        )
                        NavigationBarItem(
                            icon = { Icon(Icons.Default.Person, null) },
                            label = { Text("Profile") },
                            selected = false,
                            onClick = { navController.navigate("profile") }
                        )
                    }
                }
            ) { paddingValues ->
                NavHost(
                    navController = navController,
                    startDestination = "home",
                    modifier = Modifier.padding(paddingValues)
                ) {
                    composable("home") { HomeScreen() }
                    composable("search") { SearchScreen() }
                    composable("profile") { ProfileScreen() }
                }
            }
        }

        WindowWidthSizeClass.Medium -> {
            // Navigation rail for medium screens
            Row {
                NavigationRail {
                    NavigationRailItem(
                        icon = { Icon(Icons.Default.Home, null) },
                        label = { Text("Home") },
                        selected = true,
                        onClick = { navController.navigate("home") }
                    )
                    NavigationRailItem(
                        icon = { Icon(Icons.Default.Search, null) },
                        label = { Text("Search") },
                        selected = false,
                        onClick = { navController.navigate("search") }
                    )
                    NavigationRailItem(
                        icon = { Icon(Icons.Default.Person, null) },
                        label = { Text("Profile") },
                        selected = false,
                        onClick = { navController.navigate("profile") }
                    )
                }

                NavHost(
                    navController = navController,
                    startDestination = "home",
                    modifier = Modifier.weight(1f)
                ) {
                    composable("home") { HomeScreen() }
                    composable("search") { SearchScreen() }
                    composable("profile") { ProfileScreen() }
                }
            }
        }

        WindowWidthSizeClass.Expanded -> {
            // Permanent drawer for large screens
            PermanentNavigationDrawer(
                drawerContent = {
                    PermanentDrawerSheet {
                        NavigationDrawerItem(
                            icon = { Icon(Icons.Default.Home, null) },
                            label = { Text("Home") },
                            selected = true,
                            onClick = { navController.navigate("home") }
                        )
                        NavigationDrawerItem(
                            icon = { Icon(Icons.Default.Search, null) },
                            label = { Text("Search") },
                            selected = false,
                            onClick = { navController.navigate("search") }
                        )
                        NavigationDrawerItem(
                            icon = { Icon(Icons.Default.Person, null) },
                            label = { Text("Profile") },
                            selected = false,
                            onClick = { navController.navigate("profile") }
                        )
                    }
                }
            ) {
                NavHost(
                    navController = navController,
                    startDestination = "home"
                ) {
                    composable("home") { HomeScreen() }
                    composable("search") { SearchScreen() }
                    composable("profile") { ProfileScreen() }
                }
            }
        }
    }
}
```

---

### LIST-DETAIL ADAPTIVE LAYOUT

```kotlin
@Composable
fun AdaptiveListDetail(items: List<Item>) {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)
    var selectedItem by remember { mutableStateOf<Item?>(null) }

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Single pane: navigate between list and detail
            if (selectedItem == null) {
                ItemList(
                    items = items,
                    onItemClick = { selectedItem = it }
                )
            } else {
                ItemDetail(
                    item = selectedItem!!,
                    onBack = { selectedItem = null }
                )
            }
        }

        WindowWidthSizeClass.Medium, WindowWidthSizeClass.Expanded -> {
            // Two pane: list and detail side by side
            Row {
                ItemList(
                    items = items,
                    onItemClick = { selectedItem = it },
                    modifier = Modifier.weight(0.4f)
                )

                Box(modifier = Modifier.weight(0.6f)) {
                    selectedItem?.let { item ->
                        ItemDetail(item = item, onBack = null)
                    } ?: EmptyDetailPlaceholder()
                }
            }
        }
    }
}

@Composable
fun ItemList(
    items: List<Item>,
    onItemClick: (Item) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(modifier = modifier) {
        items(items) { item ->
            ListItem(
                headlineContent = { Text(item.title) },
                supportingContent = { Text(item.description) },
                modifier = Modifier.clickable { onItemClick(item) }
            )
        }
    }
}

@Composable
fun ItemDetail(item: Item, onBack: (() -> Unit)?) {
    Column(modifier = Modifier.padding(16.dp)) {
        onBack?.let {
            IconButton(onClick = it) {
                Icon(Icons.Default.ArrowBack, "Back")
            }
        }

        Text(
            text = item.title,
            style = MaterialTheme.typography.headlineMedium
        )

        Text(
            text = item.description,
            modifier = Modifier.padding(top = 8.dp)
        )
    }
}

@Composable
fun EmptyDetailPlaceholder() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Text("Select an item to view details")
    }
}

data class Item(val id: String, val title: String, val description: String)
```

---

### RESPONSIVE GRID

```kotlin
@Composable
fun ResponsiveGrid(items: List<String>) {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    val columns = when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> 2
        WindowWidthSizeClass.Medium -> 3
        WindowWidthSizeClass.Expanded -> 4
        else -> 2
    }

    LazyVerticalGrid(
        columns = GridCells.Fixed(columns),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        items(items) { item ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f)
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(item)
                }
            }
        }
    }
}

// Or use adaptive columns
@Composable
fun AdaptiveGrid(items: List<String>) {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    val minItemWidth = when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> 120.dp
        WindowWidthSizeClass.Medium -> 150.dp
        WindowWidthSizeClass.Expanded -> 180.dp
        else -> 120.dp
    }

    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = minItemWidth),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        items(items) { item ->
            ItemCard(item)
        }
    }
}
```

---

### BOXWITHCONSTRAINTS FOR FINE-GRAINED CONTROL

```kotlin
@Composable
fun AdaptiveContent() {
    BoxWithConstraints {
        val isCompact = maxWidth < 600.dp

        if (isCompact) {
            Column {
                Header()
                Content()
                Footer()
            }
        } else {
            Row {
                Column(modifier = Modifier.weight(0.3f)) {
                    Sidebar()
                }
                Column(modifier = Modifier.weight(0.7f)) {
                    Header()
                    Content()
                    Footer()
                }
            }
        }
    }
}

@Composable
fun ResponsiveCard() {
    BoxWithConstraints {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            if (maxWidth < 360.dp) {
                // Very narrow: stack vertically
                Column(modifier = Modifier.padding(16.dp)) {
                    Image()
                    Spacer(modifier = Modifier.height(8.dp))
                    Title()
                    Description()
                }
            } else if (maxWidth < 600.dp) {
                // Narrow: image on left, text on right
                Row(modifier = Modifier.padding(16.dp)) {
                    Image(modifier = Modifier.size(80.dp))
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Title()
                        Description()
                    }
                }
            } else {
                // Wide: large image on left, text on right
                Row(modifier = Modifier.padding(16.dp)) {
                    Image(modifier = Modifier.size(150.dp))
                    Spacer(modifier = Modifier.width(24.dp))
                    Column {
                        Title()
                        Spacer(modifier = Modifier.height(8.dp))
                        Description()
                        Spacer(modifier = Modifier.height(16.dp))
                        Actions()
                    }
                }
            }
        }
    }
}
```

---

### ORIENTATION HANDLING

```kotlin
@Composable
fun OrientationAwareLayout() {
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
}

@Composable
fun ResponsiveForm() {
    val configuration = LocalConfiguration.current
    val isLandscape = configuration.orientation == Configuration.ORIENTATION_LANDSCAPE

    if (isLandscape) {
        // Two columns in landscape
        Row(modifier = Modifier.padding(16.dp)) {
            Column(modifier = Modifier.weight(1f)) {
                FirstNameField()
                EmailField()
                PasswordField()
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                LastNameField()
                PhoneField()
                ConfirmPasswordField()
            }
        }
    } else {
        // Single column in portrait
        Column(modifier = Modifier.padding(16.dp)) {
            FirstNameField()
            LastNameField()
            EmailField()
            PhoneField()
            PasswordField()
            ConfirmPasswordField()
        }
    }
}
```

---

### FOLDABLE DEVICES

```kotlin
@Composable
fun FoldableAwareLayout() {
    val windowLayoutInfo = remember { mutableStateOf<WindowLayoutInfo?>(null) }

    // Get fold information
    LaunchedEffect(Unit) {
        val activity = LocalContext.current as Activity
        WindowInfoTracker.getOrCreate(activity)
            .windowLayoutInfo(activity)
            .collect { windowLayoutInfo.value = it }
    }

    val foldingFeature = windowLayoutInfo.value?.displayFeatures
        ?.filterIsInstance<FoldingFeature>()
        ?.firstOrNull()

    when {
        foldingFeature != null && foldingFeature.state == FoldingFeature.State.HALF_OPENED -> {
            // Device is folded (book mode)
            FoldedLayout(foldingFeature)
        }
        else -> {
            // Device is flat
            NormalLayout()
        }
    }
}

@Composable
fun FoldedLayout(foldingFeature: FoldingFeature) {
    val bounds = foldingFeature.bounds

    if (foldingFeature.orientation == FoldingFeature.Orientation.VERTICAL) {
        // Vertical fold (book-like)
        Row {
            Box(
                modifier = Modifier
                    .width(with(LocalDensity.current) { bounds.left.toDp() })
                    .fillMaxHeight()
            ) {
                LeftPane()
            }
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .fillMaxHeight()
            ) {
                RightPane()
            }
        }
    } else {
        // Horizontal fold (laptop-like)
        Column {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(with(LocalDensity.current) { bounds.top.toDp() })
            ) {
                TopPane()
            }
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) {
                BottomPane()
            }
        }
    }
}
```

---

### MATERIAL 3 ADAPTIVE COMPONENTS

```kotlin
@OptIn(ExperimentalMaterial3AdaptiveApi::class)
@Composable
fun Material3AdaptiveNav() {
    val navigator = rememberListDetailPaneScaffoldNavigator<String>()

    ListDetailPaneScaffold(
        directive = navigator.scaffoldDirective,
        value = navigator.scaffoldValue,
        listPane = {
            AnimatedPane {
                ItemList(
                    onItemClick = { item ->
                        navigator.navigateTo(ListDetailPaneScaffoldRole.Detail, item)
                    }
                )
            }
        },
        detailPane = {
            AnimatedPane {
                navigator.currentDestination?.content?.let { item ->
                    ItemDetail(item = item)
                } ?: Text("Select an item")
            }
        }
    )
}
```

---

### CUSTOM BREAKPOINTS

```kotlin
enum class CustomWindowSize {
    PHONE_PORTRAIT,
    PHONE_LANDSCAPE,
    TABLET_PORTRAIT,
    TABLET_LANDSCAPE,
    DESKTOP
}

@Composable
fun getCustomWindowSize(): CustomWindowSize {
    val configuration = LocalConfiguration.current
    val screenWidth = configuration.screenWidthDp.dp
    val screenHeight = configuration.screenHeightDp.dp
    val isLandscape = configuration.orientation == Configuration.ORIENTATION_LANDSCAPE

    return when {
        screenWidth < 600.dp && !isLandscape -> CustomWindowSize.PHONE_PORTRAIT
        screenWidth < 600.dp && isLandscape -> CustomWindowSize.PHONE_LANDSCAPE
        screenWidth < 840.dp && !isLandscape -> CustomWindowSize.TABLET_PORTRAIT
        screenWidth < 1200.dp && isLandscape -> CustomWindowSize.TABLET_LANDSCAPE
        else -> CustomWindowSize.DESKTOP
    }
}

@Composable
fun CustomAdaptiveLayout() {
    when (getCustomWindowSize()) {
        CustomWindowSize.PHONE_PORTRAIT -> PhonePortraitLayout()
        CustomWindowSize.PHONE_LANDSCAPE -> PhoneLandscapeLayout()
        CustomWindowSize.TABLET_PORTRAIT -> TabletPortraitLayout()
        CustomWindowSize.TABLET_LANDSCAPE -> TabletLandscapeLayout()
        CustomWindowSize.DESKTOP -> DesktopLayout()
    }
}
```

---

### BEST PRACTICES

```kotlin
//  Use window size classes for major layout decisions
@Composable
fun BestPracticeLayout() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()
        WindowWidthSizeClass.Medium -> MediumLayout()
        WindowWidthSizeClass.Expanded -> ExpandedLayout()
    }
}

//  Use BoxWithConstraints for fine-grained control
@Composable
fun FineGrainedLayout() {
    BoxWithConstraints {
        if (maxWidth < 360.dp) {
            VeryNarrowLayout()
        } else if (maxWidth < 600.dp) {
            NarrowLayout()
        } else {
            WideLayout()
        }
    }
}

//  Provide reasonable defaults
@Composable
fun SafeLayout() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()
        WindowWidthSizeClass.Medium -> MediumLayout()
        WindowWidthSizeClass.Expanded -> ExpandedLayout()
        else -> CompactLayout()  //  Default fallback
    }
}

//  Test on different screen sizes
// Use preview with different devices
@Preview(device = Devices.PHONE)
@Preview(device = Devices.TABLET)
@Preview(device = Devices.DESKTOP)
@Composable
fun AdaptivePreview() {
    AdaptiveLayout()
}
```

---

### KEY TAKEAWAYS

1. **WindowSizeClass** provides standardized breakpoints (compact, medium, expanded)
2. **Compact** (< 600dp) for phone portrait
3. **Medium** (600-840dp) for tablet portrait, phone landscape
4. **Expanded** (>= 840dp) for tablet landscape, desktop
5. **Adaptive navigation** - bottom bar, rail, drawer based on size
6. **List-detail** - single pane on phone, two pane on tablet
7. **BoxWithConstraints** for fine-grained layout control
8. **Orientation** handling with Configuration
9. **Foldables** require WindowLayoutInfo and FoldingFeature
10. **Material 3 Adaptive** provides pre-built adaptive components

---

## Russian Version

### Постановка задачи

Адаптивные layouts подстраивают UI под размер экрана, ориентацию и форм-фактор (телефон, планшет, складной). Material 3 и Compose предоставляют window size классы и адаптивные компоненты для создания responsive UI, работающих на всех устройствах.

**Вопрос:** Как создавать адаптивные layouts в Compose? Что такое window size классы? Как обрабатывать телефоны, планшеты и складные устройства? Какие best practices для responsive дизайна?

### Ключевые выводы

1. **WindowSizeClass** предоставляет стандартизированные breakpoints (compact, medium, expanded)
2. **Compact** (< 600dp) для телефона в портрете
3. **Medium** (600-840dp) для планшета в портрете, телефона в ландшафте
4. **Expanded** (>= 840dp) для планшета в ландшафте, десктопа
5. **Адаптивная навигация** - bottom bar, rail, drawer в зависимости от размера
6. **List-detail** - одна панель на телефоне, две на планшете
7. **BoxWithConstraints** для детального контроля layout
8. **Обработка ориентации** с Configuration
9. **Складные устройства** требуют WindowLayoutInfo и FoldingFeature
10. **Material 3 Adaptive** предоставляет готовые адаптивные компоненты

## Follow-ups

1. How do you test adaptive layouts?
2. What's the difference between WindowSizeClass and BoxWithConstraints?
3. How do you handle multi-window mode?
4. What are canonical layouts in Material Design?
5. How do you implement adaptive typography?
6. What is the relationship between adaptive layouts and accessibility?
7. How do you handle different aspect ratios?
8. What are best practices for adaptive images?
9. How do you implement adaptive dialogs?
10. What is the performance impact of adaptive layouts?

---

## Related Questions

### Prerequisites (Easier)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Compose, Jetpack
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose, Jetpack
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Compose, Jetpack

### Related (Medium)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-side-effects-advanced--jetpack-compose--hard]] - Compose, Jetpack
