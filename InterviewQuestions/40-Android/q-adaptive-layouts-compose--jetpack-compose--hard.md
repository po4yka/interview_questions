---
id: 20251012-400008
title: "Adaptive Layouts in Compose / Адаптивные layouts в Compose"
topic: android
difficulty: hard
status: draft
created: 2025-10-12
tags: [jetpack-compose, adaptive-layouts, responsive-design, window-size-classes, android/compose, android/adaptive-layouts, android/responsive-design, android/window-size-classes, android/foldables, difficulty/hard]
moc: moc-android
related:   - q-windowinsets-edge-to-edge--android--medium
  - q-jetpack-compose-basics--android--medium
  - q-material3-components--material-design--easy
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

### Ответ (RU)

---

### КЛАССЫ РАЗМЕРОВ ОКНА (WINDOW SIZE CLASSES)

**Добавьте зависимость:**
```gradle
dependencies {
    implementation "androidx.compose.material3:material3-window-size-class:1.1.2"
}
```

**Основы:**

Window Size Classes - это стандартизированный подход Material Design 3 для создания адаптивных макетов. Вместо работы с конкретными пикселями или dp, вы используете три класса размеров: Compact, Medium и Expanded.

```kotlin
@Composable
fun AdaptiveScreen() {
    // Получаем текущий класс размера окна
    val windowSizeClass = calculateWindowSizeClass(activity = LocalContext.current as Activity)

    // Выбираем макет на основе ширины окна
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Телефон в портретной ориентации: ширина < 600dp
            CompactLayout()
        }
        WindowWidthSizeClass.Medium -> {
            // Планшет в портрете, телефон в ландшафте: 600dp <= ширина < 840dp
            MediumLayout()
        }
        WindowWidthSizeClass.Expanded -> {
            // Планшет в ландшафте, десктоп: ширина >= 840dp
            ExpandedLayout()
        }
    }
}

@Composable
fun CompactLayout() {
    // Одна колонка, навигация снизу
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
    // Одна колонка с навигационной панелью сбоку
    Row {
        NavigationRail()  // Вертикальная панель навигации
        Column(modifier = Modifier.weight(1f)) {
            Content()
        }
    }
}

@Composable
fun ExpandedLayout() {
    // Две колонки с постоянным боковым меню
    Row {
        NavigationDrawer()  // Постоянный выдвижной ящик
        Column(modifier = Modifier.weight(1f)) {
            Content()
        }
    }
}
```

**Точки останова для классов размеров окна:**

```
WindowWidthSizeClass (Классы ширины окна):
- Compact (Компактный): ширина < 600dp (телефон в портрете)
- Medium (Средний): 600dp <= ширина < 840dp (планшет в портрете, телефон в ландшафте)
- Expanded (Расширенный): ширина >= 840dp (планшет в ландшафте, десктоп)

WindowHeightSizeClass (Классы высоты окна):
- Compact (Компактный): высота < 480dp (телефон в ландшафте)
- Medium (Средний): 480dp <= высота < 900dp (телефон в портрете)
- Expanded (Расширенный): высота >= 900dp (планшет)
```

**Почему это важно:**
- Стандартизация: единый подход для всех приложений
- Простота: не нужно помнить конкретные значения dp
- Гибкость: легко поддерживать разные устройства
- Совместимость: работает с Material 3 компонентами

---

### АДАПТИВНАЯ НАВИГАЦИЯ

Одна из ключевых задач адаптивного дизайна - выбор правильного паттерна навигации для каждого размера экрана:

- **Compact (телефоны)**: Bottom Navigation Bar - навигационная панель внизу экрана
- **Medium (средние планшеты)**: Navigation Rail - вертикальная панель навигации сбоку
- **Expanded (большие планшеты/десктоп)**: Permanent Navigation Drawer - постоянный боковой ящик

```kotlin
@Composable
fun AdaptiveNavigation() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)
    val navController = rememberNavController()

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Нижняя навигация для телефонов - занимает меньше места
            Scaffold(
                bottomBar = {
                    NavigationBar {
                        NavigationBarItem(
                            icon = { Icon(Icons.Default.Home, null) },
                            label = { Text("Главная") },
                            selected = true,
                            onClick = { navController.navigate("home") }
                        )
                        NavigationBarItem(
                            icon = { Icon(Icons.Default.Search, null) },
                            label = { Text("Поиск") },
                            selected = false,
                            onClick = { navController.navigate("search") }
                        )
                        NavigationBarItem(
                            icon = { Icon(Icons.Default.Person, null) },
                            label = { Text("Профиль") },
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
            // Navigation Rail для средних экранов - вертикальная панель
            Row {
                NavigationRail {
                    NavigationRailItem(
                        icon = { Icon(Icons.Default.Home, null) },
                        label = { Text("Главная") },
                        selected = true,
                        onClick = { navController.navigate("home") }
                    )
                    NavigationRailItem(
                        icon = { Icon(Icons.Default.Search, null) },
                        label = { Text("Поиск") },
                        selected = false,
                        onClick = { navController.navigate("search") }
                    )
                    NavigationRailItem(
                        icon = { Icon(Icons.Default.Person, null) },
                        label = { Text("Профиль") },
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
            // Постоянный выдвижной ящик для больших экранов
            PermanentNavigationDrawer(
                drawerContent = {
                    PermanentDrawerSheet {
                        NavigationDrawerItem(
                            icon = { Icon(Icons.Default.Home, null) },
                            label = { Text("Главная") },
                            selected = true,
                            onClick = { navController.navigate("home") }
                        )
                        NavigationDrawerItem(
                            icon = { Icon(Icons.Default.Search, null) },
                            label = { Text("Поиск") },
                            selected = false,
                            onClick = { navController.navigate("search") }
                        )
                        NavigationDrawerItem(
                            icon = { Icon(Icons.Default.Person, null) },
                            label = { Text("Профиль") },
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

**Преимущества адаптивной навигации:**
- Эффективное использование пространства на каждом типе устройства
- Привычные паттерны для пользователей
- Легкий доступ к навигации на больших экранах
- Экономия места на маленьких экранах

---

### АДАПТИВНЫЙ МАКЕТ СПИСОК-ДЕТАЛИ (LIST-DETAIL)

Паттерн список-детали - один из самых распространенных в адаптивном дизайне. На телефонах показываем либо список, либо детали (одна панель), на планшетах - обе панели одновременно (две панели).

```kotlin
@Composable
fun AdaptiveListDetail(items: List<Item>) {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)
    var selectedItem by remember { mutableStateOf<Item?>(null) }

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Одна панель: навигация между списком и деталями
            // Телефон не имеет достаточно места для двух панелей
            if (selectedItem == null) {
                ItemList(
                    items = items,
                    onItemClick = { selectedItem = it }
                )
            } else {
                ItemDetail(
                    item = selectedItem!!,
                    onBack = { selectedItem = null }  // Кнопка назад к списку
                )
            }
        }

        WindowWidthSizeClass.Medium, WindowWidthSizeClass.Expanded -> {
            // Две панели: список и детали бок о бок
            // Планшет имеет достаточно места для обеих панелей
            Row {
                ItemList(
                    items = items,
                    onItemClick = { selectedItem = it },
                    modifier = Modifier.weight(0.4f)  // 40% ширины для списка
                )

                Box(modifier = Modifier.weight(0.6f)) {  // 60% ширины для деталей
                    selectedItem?.let { item ->
                        ItemDetail(item = item, onBack = null)  // Нет кнопки назад
                    } ?: EmptyDetailPlaceholder()  // Подсказка при отсутствии выбора
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
        // Кнопка назад только на телефонах (onBack != null)
        onBack?.let {
            IconButton(onClick = it) {
                Icon(Icons.Default.ArrowBack, "Назад")
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
        Text("Выберите элемент для просмотра деталей")
    }
}

data class Item(val id: String, val title: String, val description: String)
```

**Ключевые моменты паттерна список-детали:**
- На телефонах: навигация между экранами (список → детали → список)
- На планшетах: обе панели видны одновременно
- Пропорции: обычно 40/60 или 30/70 для списка/деталей
- UX: на планшетах нет кнопки "Назад", так как список всегда виден

---

### ОТЗЫВЧИВЫЕ СЕТКИ (RESPONSIVE GRID)

Сетки должны адаптироваться к размеру экрана: больше колонок на больших экранах, меньше - на маленьких.

```kotlin
@Composable
fun ResponsiveGrid(items: List<String>) {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    // Определяем количество колонок на основе размера экрана
    val columns = when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> 2      // 2 колонки на телефоне
        WindowWidthSizeClass.Medium -> 3       // 3 колонки на среднем планшете
        WindowWidthSizeClass.Expanded -> 4     // 4 колонки на большом экране
        else -> 2
    }

    LazyVerticalGrid(
        columns = GridCells.Fixed(columns),  // Фиксированное количество колонок
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        items(items) { item ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f)  // Квадратные карточки
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

// Или используем адаптивные колонки (более гибкий подход)
@Composable
fun AdaptiveGrid(items: List<String>) {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    // Определяем минимальную ширину элемента
    val minItemWidth = when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> 120.dp    // Меньшие элементы на телефоне
        WindowWidthSizeClass.Medium -> 150.dp     // Средние элементы на планшете
        WindowWidthSizeClass.Expanded -> 180.dp   // Большие элементы на десктопе
        else -> 120.dp
    }

    LazyVerticalGrid(
        // GridCells.Adaptive автоматически вычисляет количество колонок
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

**Два подхода к сеткам:**

1. **Fixed (Фиксированный)** - точное количество колонок:
   - Полный контроль над количеством колонок
   - Предсказуемый макет
   - Требует явного указания для каждого размера

2. **Adaptive (Адаптивный)** - автоматический расчет:
   - Автоматически подстраивается под ширину
   - Плавная адаптация при изменении размера
   - Просто указываете минимальную ширину элемента

---

### BOXWITHCONSTRAINTS ДЛЯ ДЕТАЛЬНОГО КОНТРОЛЯ

BoxWithConstraints позволяет получить точные размеры контейнера и принимать решения о макете на основе доступного пространства. Это более гибкий подход, чем Window Size Classes.

```kotlin
@Composable
fun AdaptiveContent() {
    BoxWithConstraints {
        // maxWidth и maxHeight - доступное пространство
        val isCompact = maxWidth < 600.dp

        if (isCompact) {
            // Вертикальный макет для узких экранов
            Column {
                Header()
                Content()
                Footer()
            }
        } else {
            // Горизонтальный макет с боковой панелью для широких экранов
            Row {
                Column(modifier = Modifier.weight(0.3f)) {
                    Sidebar()  // 30% ширины
                }
                Column(modifier = Modifier.weight(0.7f)) {
                    Header()
                    Content()
                    Footer()  // 70% ширины
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
            // Три разных макета в зависимости от ширины
            if (maxWidth < 360.dp) {
                // Очень узко: все вертикально
                Column(modifier = Modifier.padding(16.dp)) {
                    Image()
                    Spacer(modifier = Modifier.height(8.dp))
                    Title()
                    Description()
                }
            } else if (maxWidth < 600.dp) {
                // Узко: изображение слева, текст справа
                Row(modifier = Modifier.padding(16.dp)) {
                    Image(modifier = Modifier.size(80.dp))
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Title()
                        Description()
                    }
                }
            } else {
                // Широко: большое изображение слева, текст с кнопками справа
                Row(modifier = Modifier.padding(16.dp)) {
                    Image(modifier = Modifier.size(150.dp))
                    Spacer(modifier = Modifier.width(24.dp))
                    Column {
                        Title()
                        Spacer(modifier = Modifier.height(8.dp))
                        Description()
                        Spacer(modifier = Modifier.height(16.dp))
                        Actions()  // Дополнительные кнопки на широких экранах
                    }
                }
            }
        }
    }
}
```

**Когда использовать BoxWithConstraints:**
- Нужен детальный контроль над макетом
- Требуются кастомные точки останова (не 600/840dp)
- Макет зависит от размера родительского контейнера, а не всего экрана
- Необходимо несколько разных вариантов макета для разных размеров

**Отличие от Window Size Classes:**
- Window Size Classes - для глобальных решений (навигация, общая структура)
- BoxWithConstraints - для локальных решений (отдельные компоненты)

---

### ОБРАБОТКА ОРИЕНТАЦИИ

Ориентация экрана (портрет/ландшафт) также влияет на макет. Некоторые компоненты лучше работают в определенной ориентации.

```kotlin
@Composable
fun OrientationAwareLayout() {
    val configuration = LocalConfiguration.current
    val isLandscape = configuration.orientation == Configuration.ORIENTATION_LANDSCAPE

    if (isLandscape) {
        // Ландшафт: видео и комментарии бок о бок
        Row {
            VideoPlayer(modifier = Modifier.weight(0.6f))
            Comments(modifier = Modifier.weight(0.4f))
        }
    } else {
        // Портрет: видео сверху, комментарии снизу
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
        // Две колонки в ландшафте - экономим вертикальное пространство
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
        // Одна колонка в портрете - естественная прокрутка
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

**Использование ориентации:**
- Формы: две колонки в ландшафте для экономии вертикального пространства
- Видео: полноэкранный режим в ландшафте
- Контент: боковые панели в ландшафте
- Клавиатура: учитывайте, что в ландшафте клавиатура занимает больше экрана

---

### ПОДДЕРЖКА СКЛАДНЫХ УСТРОЙСТВ (FOLDABLES)

Складные устройства имеют физическую линию сгиба, которую нужно учитывать при построении макета. WindowLayoutInfo предоставляет информацию о сгибах.

```kotlin
@Composable
fun FoldableAwareLayout() {
    val windowLayoutInfo = remember { mutableStateOf<WindowLayoutInfo?>(null) }

    // Получаем информацию о сгибах
    LaunchedEffect(Unit) {
        val activity = LocalContext.current as Activity
        WindowInfoTracker.getOrCreate(activity)
            .windowLayoutInfo(activity)
            .collect { windowLayoutInfo.value = it }
    }

    // Ищем первый сгиб
    val foldingFeature = windowLayoutInfo.value?.displayFeatures
        ?.filterIsInstance<FoldingFeature>()
        ?.firstOrNull()

    when {
        foldingFeature != null && foldingFeature.state == FoldingFeature.State.HALF_OPENED -> {
            // Устройство согнуто (режим книги)
            FoldedLayout(foldingFeature)
        }
        else -> {
            // Устройство развернуто
            NormalLayout()
        }
    }
}

@Composable
fun FoldedLayout(foldingFeature: FoldingFeature) {
    val bounds = foldingFeature.bounds

    if (foldingFeature.orientation == FoldingFeature.Orientation.VERTICAL) {
        // Вертикальный сгиб (как книга)
        // Контент слева и справа от сгиба
        Row {
            Box(
                modifier = Modifier
                    .width(with(LocalDensity.current) { bounds.left.toDp() })
                    .fillMaxHeight()
            ) {
                LeftPane()  // Левая половина экрана
            }
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .fillMaxHeight()
            ) {
                RightPane()  // Правая половина экрана
            }
        }
    } else {
        // Горизонтальный сгиб (как ноутбук)
        // Контент сверху и снизу от сгиба
        Column {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(with(LocalDensity.current) { bounds.top.toDp() })
            ) {
                TopPane()  // Верхняя часть (над сгибом)
            }
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) {
                BottomPane()  // Нижняя часть (под сгибом)
            }
        }
    }
}
```

**Типы складных устройств:**

1. **Вертикальный сгиб (режим книги)**:
   - Samsung Galaxy Z Fold в развернутом состоянии
   - Используйте Row для размещения контента по сторонам
   - Идеально для список-детали или двух приложений

2. **Горизонтальный сгиб (режим ноутбука)**:
   - Samsung Galaxy Z Fold в режиме Flex Mode
   - Используйте Column для размещения контента сверху/снизу
   - Идеально для видео сверху, управление снизу

**Важные соображения:**
- Не размещайте важный контент на линии сгиба
- Используйте две отдельные области контента
- Тестируйте на реальных устройствах или эмуляторе

---

### АДАПТИВНЫЕ КОМПОНЕНТЫ MATERIAL 3

Material 3 предоставляет готовые адаптивные компоненты, которые автоматически подстраиваются под размер экрана.

```kotlin
@OptIn(ExperimentalMaterial3AdaptiveApi::class)
@Composable
fun Material3AdaptiveNav() {
    // Навигатор автоматически управляет список-детали паттерном
    val navigator = rememberListDetailPaneScaffoldNavigator<String>()

    ListDetailPaneScaffold(
        directive = navigator.scaffoldDirective,  // Автоматические директивы макета
        value = navigator.scaffoldValue,
        listPane = {
            AnimatedPane {
                ItemList(
                    onItemClick = { item ->
                        // Навигация к деталям
                        navigator.navigateTo(ListDetailPaneScaffoldRole.Detail, item)
                    }
                )
            }
        },
        detailPane = {
            AnimatedPane {
                navigator.currentDestination?.content?.let { item ->
                    ItemDetail(item = item)
                } ?: Text("Выберите элемент")
            }
        }
    )
}
```

**Преимущества Material 3 Adaptive:**
- Автоматическое управление одно/двухпанельным режимом
- Плавные анимации переходов
- Обработка навигации "назад"
- Поддержка различных устройств из коробки
- Интеграция с Navigation Component

---

### КАСТОМНЫЕ ТОЧКИ ОСТАНОВА

Иногда стандартных Window Size Classes недостаточно. Вы можете создать собственную систему классификации размеров.

```kotlin
enum class CustomWindowSize {
    PHONE_PORTRAIT,      // Телефон вертикально
    PHONE_LANDSCAPE,     // Телефон горизонтально
    TABLET_PORTRAIT,     // Планшет вертикально
    TABLET_LANDSCAPE,    // Планшет горизонтально
    DESKTOP              // Десктоп
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

**Когда использовать кастомные точки останова:**
- Приложение требует очень специфичных макетов
- Нужен учет и ширины, и высоты одновременно
- Требуется отдельная обработка ландшафта телефонов
- Есть специфические требования дизайна

---

### ЛУЧШИЕ ПРАКТИКИ АДАПТИВНОГО ДИЗАЙНА

```kotlin
// 1. Используйте Window Size Classes для основных решений о макете
@Composable
fun BestPracticeLayout() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()
        WindowWidthSizeClass.Medium -> MediumLayout()
        WindowWidthSizeClass.Expanded -> ExpandedLayout()
    }
}

// 2. Используйте BoxWithConstraints для детального контроля
@Composable
fun FineGrainedLayout() {
    BoxWithConstraints {
        if (maxWidth < 360.dp) {
            VeryNarrowLayout()  // Очень узкие устройства
        } else if (maxWidth < 600.dp) {
            NarrowLayout()      // Обычные телефоны
        } else {
            WideLayout()        // Планшеты и десктоп
        }
    }
}

// 3. Предоставляйте разумные значения по умолчанию
@Composable
fun SafeLayout() {
    val windowSizeClass = calculateWindowSizeClass(LocalContext.current as Activity)

    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()
        WindowWidthSizeClass.Medium -> MediumLayout()
        WindowWidthSizeClass.Expanded -> ExpandedLayout()
        else -> CompactLayout()  // Безопасное значение по умолчанию
    }
}

// 4. Тестируйте на разных размерах экранов
@Preview(device = Devices.PHONE)
@Preview(device = Devices.TABLET)
@Preview(device = Devices.DESKTOP)
@Composable
fun AdaptivePreview() {
    AdaptiveLayout()
}
```

**Ключевые принципы адаптивного дизайна:**

1. **Начинайте с мобильных устройств** (Mobile First):
   - Сначала проектируйте для компактных экранов
   - Затем добавляйте функции для больших экранов
   - Это гарантирует работу на всех устройствах

2. **Используйте стандартные паттерны**:
   - Bottom Navigation → Navigation Rail → Navigation Drawer
   - Одна панель → Две панели для список-детали
   - Вертикальные списки → Сетки на больших экранах

3. **Учитывайте контекст использования**:
   - Телефон: одной рукой, на ходу
   - Планшет: двумя руками, сидя
   - Десктоп: мышь и клавиатура, длительные сессии

4. **Тестируйте на реальных устройствах**:
   - Эмулятор не заменит реальное тестирование
   - Проверяйте на разных размерах и ориентациях
   - Учитывайте складные устройства

5. **Используйте отступы и пространство правильно**:
   - Больше отступов на больших экранах
   - Ограничивайте максимальную ширину контента
   - Используйте пространство для дополнительных функций

6. **Производительность**:
   - BoxWithConstraints может вызвать дополнительные рекомпозиции
   - Кэшируйте результаты calculateWindowSizeClass
   - Избегайте избыточных вычислений в when-блоках

7. **Доступность**:
   - Убедитесь, что элементы управления доступны на всех размерах
   - Проверяйте размеры touch-целей (минимум 48dp)
   - Тестируйте с крупным шрифтом и увеличенным масштабом

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
