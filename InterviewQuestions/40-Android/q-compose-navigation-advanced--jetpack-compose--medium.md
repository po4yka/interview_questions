---
id: "20251015082237353"
title: "Compose Navigation Advanced / Продвинутая навигация Compose"
topic: jetpack-compose
difficulty: medium
status: draft
created: 2025-10-15
tags: - jetpack-compose
  - navigation
  - type-safety
  - deep-links
---
# Advanced Navigation Compose with Type Safety

**English**: Implement type-safe navigation with arguments, deep links, and back stack handling. Use Navigation Compose with sealed classes.

**Russian**: Реализуйте type-safe навигацию с аргументами, deep links и управлением back stack. Используйте Navigation Compose с sealed классами.

## Answer (EN)

Navigation Compose provides a declarative API for navigation, but without proper patterns, it can become error-prone. Type-safe navigation with sealed classes ensures compile-time safety.

### Basic Navigation Setup

```kotlin
dependencies {
    implementation("androidx.navigation:navigation-compose:2.7.5")
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToProfile = { userId ->
                    navController.navigate("profile/$userId")
                }
            )
        }

        composable(
            route = "profile/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            ProfileScreen(userId = userId)
        }
    }
}
```

### Type-Safe Navigation with Sealed Classes

```kotlin
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Search : Screen("search")
    data class Profile(val userId: String) : Screen("profile/{userId}") {
        fun createRoute(userId: String) = "profile/$userId"
    }
    data class Post(val postId: String, val commentId: String? = null) :
        Screen("post/{postId}?commentId={commentId}") {
        fun createRoute(postId: String, commentId: String? = null): String {
            return if (commentId != null) {
                "post/$postId?commentId=$commentId"
            } else {
                "post/$postId"
            }
        }
    }
}

@Composable
fun TypeSafeNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Screen.Home.route
    ) {
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToProfile = { userId ->
                    navController.navigate(Screen.Profile("").createRoute(userId))
                }
            )
        }

        composable(
            route = Screen.Profile("").route,
            arguments = listOf(
                navArgument("userId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
            ProfileScreen(
                userId = userId,
                onNavigateToPost = { postId ->
                    navController.navigate(Screen.Post("", null).createRoute(postId))
                }
            )
        }

        composable(
            route = Screen.Post("", "").route,
            arguments = listOf(
                navArgument("postId") { type = NavType.StringType },
                navArgument("commentId") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val postId = backStackEntry.arguments?.getString("postId") ?: return@composable
            val commentId = backStackEntry.arguments?.getString("commentId")
            PostScreen(postId = postId, commentId = commentId)
        }
    }
}
```

### Improved Type-Safe Navigation with Extension Functions

```kotlin
// Define destinations
sealed interface Destination {
    val route: String

    object Home : Destination {
        override val route = "home"
    }

    object Search : Destination {
        override val route = "search"
    }

    data class Profile(val userId: String) : Destination {
        override val route = "profile/$userId"

        companion object {
            const val routePattern = "profile/{userId}"
            const val argUserId = "userId"
        }
    }

    data class Settings(val section: String? = null) : Destination {
        override val route = if (section != null) {
            "settings?section=$section"
        } else {
            "settings"
        }

        companion object {
            const val routePattern = "settings?section={section}"
            const val argSection = "section"
        }
    }
}

// Extension function for type-safe navigation
fun NavController.navigate(destination: Destination) {
    navigate(destination.route)
}

// Extension function for safe back navigation
fun NavController.navigateBack() {
    if (!popBackStack()) {
        // Handle case where back stack is empty
        // Could navigate to home or exit app
    }
}

// Usage
@Composable
fun AppWithImprovedNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Destination.Home.route
    ) {
        composable(Destination.Home.route) {
            HomeScreen(
                onNavigateToProfile = { userId ->
                    navController.navigate(Destination.Profile(userId))
                }
            )
        }

        composable(
            route = Destination.Profile.routePattern,
            arguments = listOf(
                navArgument(Destination.Profile.argUserId) {
                    type = NavType.StringType
                }
            )
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString(Destination.Profile.argUserId)
                ?: return@composable

            ProfileScreen(
                userId = userId,
                onBack = { navController.navigateBack() }
            )
        }

        composable(
            route = Destination.Settings.routePattern,
            arguments = listOf(
                navArgument(Destination.Settings.argSection) {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val section = backStackEntry.arguments?.getString(Destination.Settings.argSection)
            SettingsScreen(section = section)
        }
    }
}
```

### Deep Links

```kotlin
@Composable
fun AppWithDeepLinks() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen()
        }

        composable(
            route = "profile/{userId}",
            arguments = listOf(
                navArgument("userId") { type = NavType.StringType }
            ),
            deepLinks = listOf(
                navDeepLink {
                    uriPattern = "myapp://profile/{userId}"
                },
                navDeepLink {
                    uriPattern = "https://myapp.com/profile/{userId}"
                }
            )
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            ProfileScreen(userId = userId)
        }

        composable(
            route = "post/{postId}",
            deepLinks = listOf(
                navDeepLink {
                    uriPattern = "myapp://post/{postId}"
                    action = Intent.ACTION_VIEW
                },
                navDeepLink {
                    uriPattern = "https://myapp.com/p/{postId}"
                }
            )
        ) { backStackEntry ->
            val postId = backStackEntry.arguments?.getString("postId")
            PostScreen(postId = postId)
        }
    }
}

// In AndroidManifest.xml:
/*
<activity android:name=".MainActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="myapp"
            android:host="profile" />
        <data
            android:scheme="https"
            android:host="myapp.com"
            android:pathPrefix="/profile" />
    </intent-filter>
</activity>
*/
```

### Back Stack Management

```kotlin
@Composable
fun BackStackExample() {
    val navController = rememberNavController()

    // Navigate with single top
    Button(onClick = {
        navController.navigate("screen") {
            launchSingleTop = true  // Don't create duplicate if already on top
        }
    }) {
        Text("Navigate Single Top")
    }

    // Pop up to destination
    Button(onClick = {
        navController.navigate("home") {
            popUpTo("welcome") {
                inclusive = true  // Include welcome in pop
            }
        }
    }) {
        Text("Navigate and Pop")
    }

    // Clear back stack and navigate
    Button(onClick = {
        navController.navigate("main") {
            popUpTo(navController.graph.startDestinationId) {
                inclusive = true
            }
            launchSingleTop = true
        }
    }) {
        Text("Navigate and Clear Stack")
    }

    // Save state when popping
    Button(onClick = {
        navController.navigate("details") {
            popUpTo("list") {
                saveState = true
            }
            restoreState = true
        }
    }) {
        Text("Navigate with State")
    }
}
```

### Complex Navigation Example with Bottom Navigation

```kotlin
sealed class BottomNavDestination(val route: String, val icon: ImageVector, val label: String) {
    object Home : BottomNavDestination("home", Icons.Default.Home, "Home")
    object Search : BottomNavDestination("search", Icons.Default.Search, "Search")
    object Profile : BottomNavDestination("profile", Icons.Default.Person, "Profile")
}

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    Scaffold(
        bottomBar = {
            NavigationBar {
                val items = listOf(
                    BottomNavDestination.Home,
                    BottomNavDestination.Search,
                    BottomNavDestination.Profile
                )

                items.forEach { destination ->
                    NavigationBarItem(
                        selected = currentRoute == destination.route,
                        onClick = {
                            navController.navigate(destination.route) {
                                popUpTo(navController.graph.startDestinationId) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(destination.icon, contentDescription = destination.label) },
                        label = { Text(destination.label) }
                    )
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = BottomNavDestination.Home.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(BottomNavDestination.Home.route) {
                HomeScreen(
                    onNavigateToDetail = { itemId ->
                        navController.navigate("detail/$itemId")
                    }
                )
            }

            composable(BottomNavDestination.Search.route) {
                SearchScreen()
            }

            composable(BottomNavDestination.Profile.route) {
                ProfileScreen()
            }

            // Detail screen outside bottom nav
            composable(
                route = "detail/{itemId}",
                arguments = listOf(navArgument("itemId") { type = NavType.StringType })
            ) { backStackEntry ->
                val itemId = backStackEntry.arguments?.getString("itemId")
                DetailScreen(
                    itemId = itemId,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
```

### Passing Complex Objects

```kotlin
// Option 1: Serialize to JSON
@Serializable
data class User(val id: String, val name: String, val email: String)

fun NavController.navigateWithObject(user: User) {
    val json = Json.encodeToString(user)
    val encoded = URLEncoder.encode(json, "UTF-8")
    navigate("profile/$encoded")
}

// Retrieve
val userJson = backStackEntry.arguments?.getString("userData")
val user = userJson?.let {
    val decoded = URLDecoder.decode(it, "UTF-8")
    Json.decodeFromString<User>(decoded)
}

// Option 2: Use SavedStateHandle (Recommended)
@Composable
fun DetailScreen(
    navController: NavController,
    viewModel: DetailViewModel = hiltViewModel()
) {
    // ViewModel receives object via SavedStateHandle
}

// In previous screen:
navController.currentBackStackEntry?.savedStateHandle?.set("user", user)
navController.navigate("detail")

// In DetailViewModel:
class DetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    val user: User? = savedStateHandle.get<User>("user")
}
```

### Nested Navigation Graphs

```kotlin
@Composable
fun AppWithNestedGraphs() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "auth",
        route = "root"
    ) {
        // Auth graph
        navigation(
            startDestination = "login",
            route = "auth"
        ) {
            composable("login") {
                LoginScreen(
                    onLoginSuccess = {
                        navController.navigate("main") {
                            popUpTo("auth") { inclusive = true }
                        }
                    }
                )
            }
            composable("register") {
                RegisterScreen()
            }
        }

        // Main graph
        navigation(
            startDestination = "home",
            route = "main"
        ) {
            composable("home") { HomeScreen() }
            composable("profile") { ProfileScreen() }
            composable("settings") { SettingsScreen() }
        }
    }
}
```

### Handling System Back Button

```kotlin
@Composable
fun ScreenWithBackHandler() {
    var showExitDialog by remember { mutableStateOf(false) }

    BackHandler(enabled = true) {
        showExitDialog = true
    }

    if (showExitDialog) {
        AlertDialog(
            onDismissRequest = { showExitDialog = false },
            title = { Text("Exit App?") },
            text = { Text("Are you sure you want to exit?") },
            confirmButton = {
                TextButton(onClick = { /* Exit app */ }) {
                    Text("Yes")
                }
            },
            dismissButton = {
                TextButton(onClick = { showExitDialog = false }) {
                    Text("No")
                }
            }
        )
    }

    // Screen content
}
```

### Common Pitfalls

**1. String-based routes**:
```kotlin
// BAD: Typos, no compile-time safety
navController.navigate("profiel/$userId")  // Typo!

// GOOD: Sealed classes
navController.navigate(Destination.Profile(userId))
```

**2. Not handling null arguments**:
```kotlin
// BAD: Crash if argument missing
val userId = backStackEntry.arguments?.getString("userId")!!

// GOOD: Handle gracefully
val userId = backStackEntry.arguments?.getString("userId") ?: run {
    // Navigate back or show error
    return@composable
}
```

**3. Memory leaks with navigation**:
```kotlin
// BAD: Holding navController reference in ViewModel
class BadViewModel(private val navController: NavController) : ViewModel()

// GOOD: Navigation events via callbacks
class GoodViewModel : ViewModel() {
    private val _navigationEvent = MutableSharedFlow<NavigationEvent>()
    val navigationEvent = _navigationEvent.asSharedFlow()

    fun navigateToProfile(userId: String) {
        viewModelScope.launch {
            _navigationEvent.emit(NavigationEvent.ToProfile(userId))
        }
    }
}
```

### Best Practices

1. **Use sealed classes** for type-safe navigation
2. **Define route patterns as constants**
3. **Handle null arguments gracefully**
4. **Use deep links for important screens**
5. **Manage back stack** with popUpTo
6. **Preserve state** with saveState/restoreState
7. **Test navigation flows** thoroughly
8. **Keep routes simple** - avoid complex objects
9. **Use nested graphs** for logical grouping
10. **Never pass NavController to ViewModels**

## Ответ (RU)

Navigation Compose предоставляет декларативный API для навигации, но без правильных паттернов может быть подвержена ошибкам.

### Type-Safe навигация с Sealed классами

Sealed классы обеспечивают безопасность на этапе компиляции.

[Полные примеры с deep links, управлением back stack, вложенной навигацией и передачей сложных объектов приведены в английском разделе]

### Лучшие практики

1. **Используйте sealed классы** для type-safe навигации
2. **Определяйте route паттерны как константы**
3. **Обрабатывайте null аргументы** корректно
4. **Используйте deep links** для важных экранов
5. **Управляйте back stack** с popUpTo
6. **Сохраняйте состояние** с saveState/restoreState
7. **Тестируйте навигационные потоки** тщательно
8. **Держите routes простыми**
9. **Используйте вложенные графы** для логической группировки
10. **Никогда не передавайте NavController в ViewModels**


---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations

