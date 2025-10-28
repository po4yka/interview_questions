---
id: 20251012-122710
title: Compose Navigation Advanced / Продвинутая навигация Compose
aliases: [Compose Navigation Advanced, Продвинутая навигация Compose]
topic: android
subtopics:
  - ui-compose
  - ui-navigation
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-animated-visibility-vs-content--android--medium
  - q-compose-gesture-detection--android--medium
created: 2025-10-15
updated: 2025-10-28
tags: [android/ui-compose, android/ui-navigation, difficulty/medium]
sources: [https://developer.android.com/jetpack/compose/navigation]
---

# Вопрос (RU)
> Как реализовать продвинутую навигацию в Jetpack Compose с аргументами, deep links и контролем back stack?

# Question (EN)
> How to implement advanced navigation in Jetpack Compose with arguments, deep links, and back stack control?

---

## Ответ (RU)

### Базовая настройка
NavController управляет back stack и текущим экраном; NavHost связывает паттерны маршрутов с composable-функциями.

```kotlin
@Composable
fun AppNav() {
  val nav = rememberNavController() // ✅ Создание один раз на верхнем уровне
  NavHost(nav, startDestination = "home") {
    composable("home") {
      Home(onOpen = { id -> nav.navigate("details/$id") })
    }
    composable(
      route = "details/{id}",
      arguments = listOf(navArgument("id") { type = NavType.StringType })
    ) { backStackEntry ->
      Details(backStackEntry.arguments?.getString("id") ?: "")
    }
  }
}
```

### Обязательные и опциональные аргументы
- Path-аргументы обязательны и позиционные; query-аргументы опциональны с дефолтами.
- NavType обеспечивает type-safety; используйте Uri.encode для спецсимволов.

```kotlin
// Обязательный path-аргумент
composable(
  "profile/{userId}",
  listOf(navArgument("userId") { type = NavType.StringType })
) { /* ... */ }

// Опциональный query-аргумент
composable(
  "search?query={q}",
  listOf(navArgument("q") {
    type = NavType.StringType
    nullable = true
    defaultValue = "" // ✅ Значение по умолчанию
  })
) { /* ... */ }
```

### Type-safe маршруты
Централизуйте определения маршрутов для избежания строковых ошибок.

```kotlin
sealed class Screen(val route: String) {
  data object Home: Screen("home")
  data object Profile: Screen("profile/{userId}") {
    fun createRoute(id: String) = "profile/$id" // ✅ Type-safe builder
  }
}

NavHost(nav, Screen.Home.route) {
  composable(Screen.Home.route) { HomeScreen() }
  composable(Screen.Profile.route) {
    val userId = it.arguments?.getString("userId") ?: ""
    ProfileScreen(userId)
  }
}
```

### Deep Links
Deep links сопоставляют URI с маршрутами; требуют intent-filters в манифесте для app/https схем.

```kotlin
composable(
  route = "profile/{userId}",
  arguments = listOf(navArgument("userId") { type = NavType.StringType }),
  deepLinks = listOf(
    navDeepLink { uriPattern = "myapp://profile/{userId}" },
    navDeepLink { uriPattern = "https://example.com/profile/{userId}" }
  )
) { /* ... */ }
```

### Управление back stack
- `launchSingleTop` предотвращает дублирование верхнего экрана
- `popUpTo` очищает стек до указанного маршрута

```kotlin
// ✅ Избегаем дублирования
nav.navigate("home") { launchSingleTop = true }

// ✅ Очистка стека до login
nav.navigate("main") {
  popUpTo("login") { inclusive = true }
}

// ❌ Без настроек создаст дубликаты
nav.navigate("home")
```

### Передача сложных объектов
Используйте shared ViewModel или SavedStateHandle вместо сериализации в URL.

```kotlin
// ✅ Shared ViewModel
val viewModel = hiltViewModel<SharedDataViewModel>()
nav.navigate("details/$id")

// ❌ Сериализация сложного объекта в URL
nav.navigate("details?data=${complexObject.toJson()}") // Ограничения размера URL
```

## Answer (EN)

### Basic Setup
NavController manages the back stack and current destination; NavHost maps route patterns to composable destinations.

```kotlin
@Composable
fun AppNav() {
  val nav = rememberNavController() // ✅ Create once at top level
  NavHost(nav, startDestination = "home") {
    composable("home") {
      Home(onOpen = { id -> nav.navigate("details/$id") })
    }
    composable(
      route = "details/{id}",
      arguments = listOf(navArgument("id") { type = NavType.StringType })
    ) { backStackEntry ->
      Details(backStackEntry.arguments?.getString("id") ?: "")
    }
  }
}
```

### Required vs Optional Arguments
- Path arguments are positional and required; query arguments are named with optional defaults.
- NavType enforces runtime type safety; use Uri.encode for special characters.

```kotlin
// Required path argument
composable(
  "profile/{userId}",
  listOf(navArgument("userId") { type = NavType.StringType })
) { /* ... */ }

// Optional query argument
composable(
  "search?query={q}",
  listOf(navArgument("q") {
    type = NavType.StringType
    nullable = true
    defaultValue = "" // ✅ Default value provided
  })
) { /* ... */ }
```

### Type-safe Routes
Centralize route definitions to avoid string typos in navigation calls.

```kotlin
sealed class Screen(val route: String) {
  data object Home: Screen("home")
  data object Profile: Screen("profile/{userId}") {
    fun createRoute(id: String) = "profile/$id" // ✅ Type-safe builder
  }
}

NavHost(nav, Screen.Home.route) {
  composable(Screen.Home.route) { HomeScreen() }
  composable(Screen.Profile.route) {
    val userId = it.arguments?.getString("userId") ?: ""
    ProfileScreen(userId)
  }
}
```

### Deep Links
Deep links match incoming URIs to routes; require manifest intent filters for app/https schemes.

```kotlin
composable(
  route = "profile/{userId}",
  arguments = listOf(navArgument("userId") { type = NavType.StringType }),
  deepLinks = listOf(
    navDeepLink { uriPattern = "myapp://profile/{userId}" },
    navDeepLink { uriPattern = "https://example.com/profile/{userId}" }
  )
) { /* ... */ }
```

### Back Stack Control
- `launchSingleTop` prevents duplicate top entries
- `popUpTo` clears the stack up to a target route

```kotlin
// ✅ Avoid duplicates
nav.navigate("home") { launchSingleTop = true }

// ✅ Clear stack up to login
nav.navigate("main") {
  popUpTo("login") { inclusive = true }
}

// ❌ Creates duplicates without options
nav.navigate("home")
```

### Passing Complex Objects
Use shared ViewModel or SavedStateHandle instead of serializing to URL parameters.

```kotlin
// ✅ Shared ViewModel
val viewModel = hiltViewModel<SharedDataViewModel>()
nav.navigate("details/$id")

// ❌ Serializing complex object to URL
nav.navigate("details?data=${complexObject.toJson()}") // URL size limits
```

## Follow-ups
- How to implement nested navigation graphs for modular features?
- What are best practices for multi-module navigation with type safety?
- How to preserve state across bottom navigation tabs?
- How to handle navigation testing with NavController?

## References
- https://developer.android.com/jetpack/compose/navigation
- https://developer.android.com/guide/navigation/navigation-principles

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-gesture-detection--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]
