---
id: android-mod-003
title: "Navigation Between Feature Modules / Навигация между feature-модулями"
aliases: ["Feature Module Navigation", "Multi-module Navigation", "Навигация в модульном приложении"]
topic: android
subtopics: [modularization, navigation, architecture]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-module-types--modularization--medium, q-module-dependency-graph--modularization--hard]
created: 2026-01-23
updated: 2026-01-23
sources: []
tags: [android/modularization, android/navigation, android/architecture, difficulty/hard, navigation-compose]

---
# Вопрос (RU)

> Как организовать навигацию между feature-модулями, если они не могут зависеть друг от друга? Какие паттерны используются?

# Question (EN)

> How do you organize navigation between feature modules when they cannot depend on each other? What patterns are used?

---

## Ответ (RU)

Навигация между независимыми feature-модулями - ключевой архитектурный вызов. Модули не должны знать друг о друге напрямую, но должны иметь возможность навигации.

### Проблема

```
feature:home -> feature:profile  // НЕЛЬЗЯ - прямая зависимость
feature:profile -> feature:settings  // НЕЛЬЗЯ - создает связность
```

### Решения

#### 1. Navigation API Module (Рекомендуется)

Создайте отдельный модуль с навигационными контрактами.

```kotlin
// core/navigation/src/.../NavigationApi.kt
// Определяет маршруты без реализации

interface ProfileNavigator {
    fun navigateToProfile(userId: String)
    fun navigateToEditProfile()
}

interface SettingsNavigator {
    fun navigateToSettings()
    fun navigateToNotificationSettings()
}

interface HomeNavigator {
    fun navigateToHome()
}

// Sealed class для type-safe маршрутов
sealed class Route(val route: String) {
    data object Home : Route("home")
    data class Profile(val userId: String) : Route("profile/{userId}") {
        fun createRoute(userId: String) = "profile/$userId"
    }
    data object Settings : Route("settings")
    data object EditProfile : Route("profile/edit")
}
```

```kotlin
// core/navigation/build.gradle.kts
plugins {
    id("org.jetbrains.kotlin.jvm") // Чистый Kotlin, без Android
}
```

**Структура зависимостей**:
```
         +--------+
         |  app   |  <- Реализует навигаторы
         +----+---+
              |
    +---------+---------+
    |         |         |
+---v---+ +---v---+ +---v---+
|feature| |feature| |feature|
| home  | |profile| |settings|
+---+---+ +---+---+ +---+---+
    |         |         |
    +---------+---------+
              |
        +-----v-----+
        |core       |
        |navigation | <- Только контракты
        +-----------+
```

#### 2. Реализация в App Module

```kotlin
// app/src/.../navigation/AppNavigator.kt
class AppNavigator(
    private val navController: NavController
) : ProfileNavigator, SettingsNavigator, HomeNavigator {

    override fun navigateToProfile(userId: String) {
        navController.navigate(Route.Profile.createRoute(userId))
    }

    override fun navigateToSettings() {
        navController.navigate(Route.Settings.route)
    }

    override fun navigateToHome() {
        navController.navigate(Route.Home.route) {
            popUpTo(Route.Home.route) { inclusive = true }
        }
    }

    override fun navigateToEditProfile() {
        navController.navigate(Route.EditProfile.route)
    }
}
```

```kotlin
// app/src/.../navigation/AppNavHost.kt
@Composable
fun AppNavHost(
    navController: NavHostController = rememberNavController(),
    modifier: Modifier = Modifier
) {
    val navigator = remember(navController) { AppNavigator(navController) }

    // Предоставляем навигаторы через CompositionLocal
    CompositionLocalProvider(
        LocalProfileNavigator provides navigator,
        LocalSettingsNavigator provides navigator,
        LocalHomeNavigator provides navigator
    ) {
        NavHost(
            navController = navController,
            startDestination = Route.Home.route,
            modifier = modifier
        ) {
            homeScreen()
            profileScreen()
            settingsScreen()
        }
    }
}
```

#### 3. Feature Module Navigation Extensions

Каждый feature экспортирует extension для NavGraphBuilder.

```kotlin
// feature/profile/src/.../navigation/ProfileNavigation.kt
fun NavGraphBuilder.profileScreen() {
    composable(
        route = Route.Profile.route,
        arguments = listOf(
            navArgument("userId") { type = NavType.StringType }
        )
    ) { backStackEntry ->
        val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
        ProfileRoute(userId = userId)
    }
}

@Composable
internal fun ProfileRoute(
    userId: String,
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val navigator = LocalSettingsNavigator.current // Получаем из CompositionLocal

    ProfileScreen(
        viewModel = viewModel,
        onSettingsClick = { navigator.navigateToSettings() }
    )
}
```

#### 4. CompositionLocals для DI навигаторов

```kotlin
// core/navigation/src/.../LocalNavigators.kt
val LocalProfileNavigator = staticCompositionLocalOf<ProfileNavigator> {
    error("ProfileNavigator not provided")
}

val LocalSettingsNavigator = staticCompositionLocalOf<SettingsNavigator> {
    error("SettingsNavigator not provided")
}

val LocalHomeNavigator = staticCompositionLocalOf<HomeNavigator> {
    error("HomeNavigator not provided")
}
```

### Альтернатива: Deep Links

```kotlin
// feature/profile/src/.../navigation/ProfileDeepLinks.kt
object ProfileDeepLinks {
    const val PROFILE = "myapp://profile/{userId}"
    const val EDIT_PROFILE = "myapp://profile/edit"
}

fun NavGraphBuilder.profileScreen() {
    composable(
        route = Route.Profile.route,
        deepLinks = listOf(
            navDeepLink { uriPattern = ProfileDeepLinks.PROFILE }
        )
    ) { /* ... */ }
}
```

```kotlin
// В любом feature-модуле можно навигировать через deep link
navController.navigate(Uri.parse("myapp://profile/123"))
```

### Type-Safe Navigation (Navigation 2.8+)

```kotlin
// core/navigation/src/.../Routes.kt
@Serializable
sealed interface AppRoute {
    @Serializable
    data object Home : AppRoute

    @Serializable
    data class Profile(val userId: String) : AppRoute

    @Serializable
    data object Settings : AppRoute
}

// feature/home/src/.../HomeScreen.kt
@Composable
fun HomeScreen(
    onNavigateToProfile: (String) -> Unit
) {
    Button(onClick = { onNavigateToProfile("user-123") }) {
        Text("Open Profile")
    }
}

// app/src/.../AppNavHost.kt
NavHost<AppRoute>(
    navController = navController,
    startDestination = AppRoute.Home
) {
    composable<AppRoute.Home> {
        HomeScreen(
            onNavigateToProfile = { userId ->
                navController.navigate(AppRoute.Profile(userId))
            }
        )
    }
    composable<AppRoute.Profile> { backStackEntry ->
        val route = backStackEntry.toRoute<AppRoute.Profile>()
        ProfileScreen(userId = route.userId)
    }
}
```

### Сравнение Подходов

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| Navigation API Module | Type-safe, testable | Дополнительный модуль |
| Deep Links | Простота, универсальность | Нет compile-time проверок |
| Callbacks через app | Явный контроль | Может усложнить граф |
| Type-Safe Nav 2.8+ | Встроенный, Kotlin-first | Требует Navigation 2.8+ |

### Best Practices

```kotlin
// DO: Каждый feature определяет свои маршруты
// feature/profile/navigation/ProfileNavigation.kt
fun NavGraphBuilder.profileGraph(
    onNavigateToSettings: () -> Unit,
    nestedGraphs: NavGraphBuilder.() -> Unit = {}
) {
    navigation(
        route = "profile_graph",
        startDestination = Route.Profile.route
    ) {
        composable(Route.Profile.route) { /* ... */ }
        composable(Route.EditProfile.route) { /* ... */ }
        nestedGraphs()
    }
}

// DON'T: Хардкодить маршруты других модулей
navController.navigate("settings") // BAD - знание о другом модуле
```

---

## Answer (EN)

Navigation between independent feature modules is a key architectural challenge. Modules should not know about each other directly but must be able to navigate.

### The Problem

```
feature:home -> feature:profile  // CANNOT - direct dependency
feature:profile -> feature:settings  // CANNOT - creates coupling
```

### Solutions

#### 1. Navigation API Module (Recommended)

Create a separate module with navigation contracts.

```kotlin
// core/navigation/src/.../NavigationApi.kt
// Defines routes without implementation

interface ProfileNavigator {
    fun navigateToProfile(userId: String)
    fun navigateToEditProfile()
}

interface SettingsNavigator {
    fun navigateToSettings()
    fun navigateToNotificationSettings()
}

interface HomeNavigator {
    fun navigateToHome()
}

// Sealed class for type-safe routes
sealed class Route(val route: String) {
    data object Home : Route("home")
    data class Profile(val userId: String) : Route("profile/{userId}") {
        fun createRoute(userId: String) = "profile/$userId"
    }
    data object Settings : Route("settings")
    data object EditProfile : Route("profile/edit")
}
```

```kotlin
// core/navigation/build.gradle.kts
plugins {
    id("org.jetbrains.kotlin.jvm") // Pure Kotlin, no Android
}
```

**Dependency structure**:
```
         +--------+
         |  app   |  <- Implements navigators
         +----+---+
              |
    +---------+---------+
    |         |         |
+---v---+ +---v---+ +---v---+
|feature| |feature| |feature|
| home  | |profile| |settings|
+---+---+ +---+---+ +---+---+
    |         |         |
    +---------+---------+
              |
        +-----v-----+
        |core       |
        |navigation | <- Contracts only
        +-----------+
```

#### 2. Implementation in App Module

```kotlin
// app/src/.../navigation/AppNavigator.kt
class AppNavigator(
    private val navController: NavController
) : ProfileNavigator, SettingsNavigator, HomeNavigator {

    override fun navigateToProfile(userId: String) {
        navController.navigate(Route.Profile.createRoute(userId))
    }

    override fun navigateToSettings() {
        navController.navigate(Route.Settings.route)
    }

    override fun navigateToHome() {
        navController.navigate(Route.Home.route) {
            popUpTo(Route.Home.route) { inclusive = true }
        }
    }

    override fun navigateToEditProfile() {
        navController.navigate(Route.EditProfile.route)
    }
}
```

```kotlin
// app/src/.../navigation/AppNavHost.kt
@Composable
fun AppNavHost(
    navController: NavHostController = rememberNavController(),
    modifier: Modifier = Modifier
) {
    val navigator = remember(navController) { AppNavigator(navController) }

    // Provide navigators via CompositionLocal
    CompositionLocalProvider(
        LocalProfileNavigator provides navigator,
        LocalSettingsNavigator provides navigator,
        LocalHomeNavigator provides navigator
    ) {
        NavHost(
            navController = navController,
            startDestination = Route.Home.route,
            modifier = modifier
        ) {
            homeScreen()
            profileScreen()
            settingsScreen()
        }
    }
}
```

#### 3. Feature Module Navigation Extensions

Each feature exports an extension for NavGraphBuilder.

```kotlin
// feature/profile/src/.../navigation/ProfileNavigation.kt
fun NavGraphBuilder.profileScreen() {
    composable(
        route = Route.Profile.route,
        arguments = listOf(
            navArgument("userId") { type = NavType.StringType }
        )
    ) { backStackEntry ->
        val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
        ProfileRoute(userId = userId)
    }
}

@Composable
internal fun ProfileRoute(
    userId: String,
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val navigator = LocalSettingsNavigator.current // Get from CompositionLocal

    ProfileScreen(
        viewModel = viewModel,
        onSettingsClick = { navigator.navigateToSettings() }
    )
}
```

#### 4. CompositionLocals for Navigator DI

```kotlin
// core/navigation/src/.../LocalNavigators.kt
val LocalProfileNavigator = staticCompositionLocalOf<ProfileNavigator> {
    error("ProfileNavigator not provided")
}

val LocalSettingsNavigator = staticCompositionLocalOf<SettingsNavigator> {
    error("SettingsNavigator not provided")
}

val LocalHomeNavigator = staticCompositionLocalOf<HomeNavigator> {
    error("HomeNavigator not provided")
}
```

### Alternative: Deep Links

```kotlin
// feature/profile/src/.../navigation/ProfileDeepLinks.kt
object ProfileDeepLinks {
    const val PROFILE = "myapp://profile/{userId}"
    const val EDIT_PROFILE = "myapp://profile/edit"
}

fun NavGraphBuilder.profileScreen() {
    composable(
        route = Route.Profile.route,
        deepLinks = listOf(
            navDeepLink { uriPattern = ProfileDeepLinks.PROFILE }
        )
    ) { /* ... */ }
}
```

```kotlin
// From any feature module, navigate via deep link
navController.navigate(Uri.parse("myapp://profile/123"))
```

### Type-Safe Navigation (Navigation 2.8+)

```kotlin
// core/navigation/src/.../Routes.kt
@Serializable
sealed interface AppRoute {
    @Serializable
    data object Home : AppRoute

    @Serializable
    data class Profile(val userId: String) : AppRoute

    @Serializable
    data object Settings : AppRoute
}

// feature/home/src/.../HomeScreen.kt
@Composable
fun HomeScreen(
    onNavigateToProfile: (String) -> Unit
) {
    Button(onClick = { onNavigateToProfile("user-123") }) {
        Text("Open Profile")
    }
}

// app/src/.../AppNavHost.kt
NavHost<AppRoute>(
    navController = navController,
    startDestination = AppRoute.Home
) {
    composable<AppRoute.Home> {
        HomeScreen(
            onNavigateToProfile = { userId ->
                navController.navigate(AppRoute.Profile(userId))
            }
        )
    }
    composable<AppRoute.Profile> { backStackEntry ->
        val route = backStackEntry.toRoute<AppRoute.Profile>()
        ProfileScreen(userId = route.userId)
    }
}
```

### Approach Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Navigation API Module | Type-safe, testable | Extra module |
| Deep Links | Simple, universal | No compile-time checks |
| Callbacks via app | Explicit control | Can complicate graph |
| Type-Safe Nav 2.8+ | Built-in, Kotlin-first | Requires Navigation 2.8+ |

### Best Practices

```kotlin
// DO: Each feature defines its routes
// feature/profile/navigation/ProfileNavigation.kt
fun NavGraphBuilder.profileGraph(
    onNavigateToSettings: () -> Unit,
    nestedGraphs: NavGraphBuilder.() -> Unit = {}
) {
    navigation(
        route = "profile_graph",
        startDestination = Route.Profile.route
    ) {
        composable(Route.Profile.route) { /* ... */ }
        composable(Route.EditProfile.route) { /* ... */ }
        nestedGraphs()
    }
}

// DON'T: Hardcode routes of other modules
navController.navigate("settings") // BAD - knowledge about another module
```

---

## Follow-ups

- How do you handle navigation arguments validation?
- What about shared element transitions between feature modules?
- How do you test navigation in a multi-module setup?

## References

- https://developer.android.com/guide/navigation/design/multi-module
- https://developer.android.com/guide/navigation/design/type-safety
- https://github.com/android/nowinandroid/tree/main/core/navigation

## Related Questions

### Prerequisites

- [[q-module-types--modularization--medium]] - Module types overview
- [[q-what-are-the-navigation-methods-in-kotlin--android--medium]] - Navigation basics

### Related

- [[q-module-dependency-graph--modularization--hard]] - Designing dependency graphs
- [[q-api-vs-implementation--modularization--medium]] - API boundaries

### Advanced

- [[q-dynamic-feature-modules--modularization--hard]] - Dynamic feature navigation
- [[q-deep-linking--android--hard]] - Deep linking patterns
