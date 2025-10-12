---
id: 20251006-009
title: "Compose Navigation Deep Dive / Навигация в Compose - детально"
aliases: []

# Classification
topic: android
subtopics: [jetpack-compose, navigation, compose-navigation]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, jetpack-compose, navigation, compose-navigation, difficulty/medium]
---
# Question (EN)
> How does Navigation work in Jetpack Compose? Explain NavHost, NavController, and navigation arguments.
# Вопрос (RU)
> Как работает навигация в Jetpack Compose? Объясните NavHost, NavController и навигационные аргументы.

---

## Answer (EN)

**Compose Navigation** provides declarative type-safe navigation between composables.

### Core Components

**1. NavController** - Navigation state manager
**2. NavHost** - Container displaying current destination
**3. Routes** - String identifiers for destinations

### Basic Setup

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToDetails = { id ->
                    navController.navigate("details/$id")
                }
            )
        }

        composable(
            route = "details/{itemId}",
            arguments = listOf(
                navArgument("itemId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getString("itemId")
            DetailsScreen(itemId = itemId)
        }
    }
}
```

### Navigation with Arguments

**Required arguments:**

```kotlin
composable(
    route = "profile/{userId}",
    arguments = listOf(
        navArgument("userId") {
            type = NavType.StringType
        }
    )
) { backStackEntry ->
    val userId = backStackEntry.arguments?.getString("userId")
    ProfileScreen(userId = userId!!)
}

// Navigate
navController.navigate("profile/123")
```

**Optional arguments:**

```kotlin
composable(
    route = "search?query={query}",
    arguments = listOf(
        navArgument("query") {
            type = NavType.StringType
            nullable = true
            defaultValue = null
        }
    )
) { backStackEntry ->
    val query = backStackEntry.arguments?.getString("query")
    SearchScreen(initialQuery = query)
}

// Navigate with or without query
navController.navigate("search")
navController.navigate("search?query=kotlin")
```

### Type-Safe Navigation (Recommended)

```kotlin
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Profile : Screen("profile/{userId}") {
        fun createRoute(userId: String) = "profile/$userId"
    }
    object Settings : Screen("settings")
}

// NavHost
NavHost(
    navController = navController,
    startDestination = Screen.Home.route
) {
    composable(Screen.Home.route) {
        HomeScreen(
            onNavigateToProfile = { userId ->
                navController.navigate(Screen.Profile.createRoute(userId))
            }
        )
    }

    composable(Screen.Profile.route) { backStackEntry ->
        val userId = backStackEntry.arguments?.getString("userId")
        ProfileScreen(userId = userId!!)
    }
}
```

### Navigation Actions

```kotlin
// Navigate forward
navController.navigate("details")

// Navigate back
navController.popBackStack()

// Navigate back to specific destination
navController.popBackStack("home", inclusive = false)

// Navigate and clear backstack
navController.navigate("login") {
    popUpTo("home") { inclusive = true }
}

// Single top (avoid duplicates)
navController.navigate("home") {
    launchSingleTop = true
}
```

### Bottom Navigation Example

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            BottomNavigation {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentRoute = navBackStackEntry?.destination?.route

                BottomNavigationItem(
                    icon = { Icon(Icons.Default.Home, null) },
                    selected = currentRoute == "home",
                    onClick = {
                        navController.navigate("home") {
                            popUpTo(navController.graph.startDestinationId)
                            launchSingleTop = true
                        }
                    }
                )

                BottomNavigationItem(
                    icon = { Icon(Icons.Default.Search, null) },
                    selected = currentRoute == "search",
                    onClick = {
                        navController.navigate("search") {
                            popUpTo(navController.graph.startDestinationId)
                            launchSingleTop = true
                        }
                    }
                )
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = "home",
            modifier = Modifier.padding(padding)
        ) {
            composable("home") { HomeScreen() }
            composable("search") { SearchScreen() }
        }
    }
}
```

### Passing Complex Objects

**Option 1: Use ViewModel (Recommended)**

```kotlin
// Shared ViewModel
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableStateFlow<Item?>(null)
    val selectedItem = _selectedItem.asStateFlow()

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Screen 1
@Composable
fun ListScreen(
    viewModel: SharedViewModel = hiltViewModel(),
    onNavigateToDetails: () -> Unit
) {
    LazyColumn {
        items(items) { item ->
            ItemCard(
                item = item,
                onClick = {
                    viewModel.selectItem(item)
                    onNavigateToDetails()
                }
            )
        }
    }
}

// Screen 2
@Composable
fun DetailsScreen(
    viewModel: SharedViewModel = hiltViewModel()
) {
    val item by viewModel.selectedItem.collectAsState()
    item?.let { ItemDetails(it) }
}
```

**Option 2: Serialize to JSON**

```kotlin
val item = Item(id = 1, name = "Product")
val json = Json.encodeToString(item)
val encoded = URLEncoder.encode(json, "UTF-8")
navController.navigate("details/$encoded")

// In destination
val json = backStackEntry.arguments?.getString("itemJson")
val decoded = URLDecoder.decode(json, "UTF-8")
val item = Json.decodeFromString<Item>(decoded)
```

### Nested Navigation

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "auth") {
        // Auth graph
        navigation(startDestination = "login", route = "auth") {
            composable("login") { LoginScreen() }
            composable("register") { RegisterScreen() }
        }

        // Main graph
        navigation(startDestination = "home", route = "main") {
            composable("home") { HomeScreen() }
            composable("profile") { ProfileScreen() }
        }
    }
}
```

**English Summary**: Compose Navigation: NavController (state manager), NavHost (container), routes (destinations). Arguments: required (path), optional (query). Type-safe with sealed classes. Actions: navigate, popBackStack, popUpTo. Pass complex objects via ViewModel or serialize to JSON. Bottom nav: currentBackStackEntryAsState + launchSingleTop. Nested navigation with navigation().

## Ответ (RU)

**Compose Navigation** предоставляет декларативную типобезопасную навигацию между composables.

### Основные компоненты

**1. NavController** - Менеджер состояния навигации
**2. NavHost** - Контейнер отображающий текущее назначение
**3. Routes** - Строковые идентификаторы для назначений

### Базовая настройка

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToDetails = { id ->
                    navController.navigate("details/$id")
                }
            )
        }

        composable(
            route = "details/{itemId}",
            arguments = listOf(
                navArgument("itemId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getString("itemId")
            DetailsScreen(itemId = itemId)
        }
    }
}
```

### Типобезопасная навигация (Рекомендуется)

```kotlin
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Profile : Screen("profile/{userId}") {
        fun createRoute(userId: String) = "profile/$userId"
    }
}

// NavHost
NavHost(
    navController = navController,
    startDestination = Screen.Home.route
) {
    composable(Screen.Home.route) {
        HomeScreen(
            onNavigateToProfile = { userId ->
                navController.navigate(Screen.Profile.createRoute(userId))
            }
        )
    }
}
```

### Действия навигации

```kotlin
// Навигация вперед
navController.navigate("details")

// Навигация назад
navController.popBackStack()

// Навигация назад к определенному назначению
navController.popBackStack("home", inclusive = false)

// Навигация и очистка backstack
navController.navigate("login") {
    popUpTo("home") { inclusive = true }
}

// Single top (избегать дубликатов)
navController.navigate("home") {
    launchSingleTop = true
}
```

### Передача сложных объектов

**Вариант 1: Использовать ViewModel (Рекомендуется)**

```kotlin
// Shared ViewModel
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableStateFlow<Item?>(null)
    val selectedItem = _selectedItem.asStateFlow()

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Экран 1
@Composable
fun ListScreen(
    viewModel: SharedViewModel = hiltViewModel(),
    onNavigateToDetails: () -> Unit
) {
    LazyColumn {
        items(items) { item ->
            ItemCard(
                item = item,
                onClick = {
                    viewModel.selectItem(item)
                    onNavigateToDetails()
                }
            )
        }
    }
}
```

**Краткое содержание**: Compose Navigation: NavController (менеджер состояния), NavHost (контейнер), routes (назначения). Аргументы: обязательные (path), опциональные (query). Типобезопасность с sealed классами. Действия: navigate, popBackStack, popUpTo. Передача сложных объектов через ViewModel или сериализация в JSON. Bottom nav: currentBackStackEntryAsState + launchSingleTop.

---

## References
- [Compose Navigation](https://developer.android.com/jetpack/compose/navigation)

## Related Questions
- [[q-jetpack-compose-basics--android--medium]]
