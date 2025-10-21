---
id: 20251012-1227105
title: Compose Navigation Deep Dive / Навигация в Compose — детально
aliases: [Compose Navigation Deep Dive, Навигация в Compose — детально]
topic: android
subtopics: [ui-compose, navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/jetpack/compose/navigation
source_note: Official Compose Navigation docs
status: reviewed
moc: moc-android
related: [q-animated-visibility-vs-content--jetpack-compose--medium, q-compose-gesture-detection--jetpack-compose--medium, q-compose-compiler-plugin--jetpack-compose--hard]
created: 2025-10-06
updated: 2025-10-20
tags: [android/ui-compose, android/navigation, compose/navigation, difficulty/medium]
---
# Question (EN)
> How does Navigation work in Jetpack Compose? Show minimal patterns for NavHost, arguments, type‑safe routes, and back stack control.

# Вопрос (RU)
> Как работает Navigation в Jetpack Compose? Покажите минимальные паттерны для NavHost, аргументов, типобезопасных роутов и управления back stack.

---

## Answer (EN)

### Core pieces
- NavController: holds navigation state
- NavHost: maps routes to destinations
- Route: string with path/query; prefer sealed API wrappers

### Minimal setup
```kotlin
@Composable
fun AppNav() {
  val nav = rememberNavController()
  NavHost(navController = nav, startDestination = "home") {
    composable("home") { Home(onOpen = { id -> nav.navigate("details/$id") }) }
    composable("details/{id}", arguments = listOf(navArgument("id") { type = NavType.StringType })) {
      val id = it.arguments?.getString("id")!!
      Details(id)
    }
  }
}
```

### Required vs optional args
```kotlin
// Required path
nav.navigate("profile/123")
composable("profile/{userId}", listOf(navArgument("userId") { type = NavType.StringType })) { /*...*/ }

// Optional query
composable("search?query={query}", listOf(navArgument("query") { nullable = true })) { /*...*/ }
nav.navigate("search?query=kotlin")
```

### Type‑safe routes
```kotlin
sealed class Screen(val route: String) {
  data object Home: Screen("home")
  data object Profile: Screen("profile/{userId}") { fun route(userId: String) = "profile/$userId" }
}
NavHost(nav, Screen.Home.route) {
  composable(Screen.Home.route) { /*...*/ }
  composable(Screen.Profile.route) { val id = it.arguments!!.getString("userId")!! /*...*/ }
}
```

### Back stack control
```kotlin
nav.navigate("home") { launchSingleTop = true }
nav.popBackStack()
nav.navigate("login") { popUpTo("home") { inclusive = true } }
```

### Bottom navigation (minimal)
```kotlin
Scaffold(bottomBar = {
  BottomNavigation {
    val current = nav.currentBackStackEntryAsState().value?.destination?.route
    BottomNavigationItem(selected = current=="home", onClick = {
      nav.navigate("home") { popUpTo(nav.graph.startDestinationId); launchSingleTop = true }
    }, icon = { Icon(Icons.Default.Home, null) })
  }
}) { padding ->
  NavHost(nav, "home", Modifier.padding(padding)) { composable("home") { Home() } }
}
```

Passing complex objects: prefer shared ViewModel over large route payloads.

## Ответ (RU)

### Основные элементы
- NavController: хранит состояние навигации
- NavHost: сопоставляет маршруты и экраны
- Route: строка с path/query; предпочтительно обёртки через sealed API

### Минимальная настройка
```kotlin
@Composable
fun AppNav() {
  val nav = rememberNavController()
  NavHost(navController = nav, startDestination = "home") {
    composable("home") { Home(onOpen = { id -> nav.navigate("details/$id") }) }
    composable("details/{id}", arguments = listOf(navArgument("id") { type = NavType.StringType })) {
      val id = it.arguments?.getString("id")!!
      Details(id)
    }
  }
}
```

### Обязательные и опциональные аргументы
```kotlin
// Обязательный path
nav.navigate("profile/123")
composable("profile/{userId}", listOf(navArgument("userId") { type = NavType.StringType })) { /*...*/ }

// Опциональный query
composable("search?query={query}", listOf(navArgument("query") { nullable = true })) { /*...*/ }
nav.navigate("search?query=kotlin")
```

### Типобезопасные роуты
```kotlin
sealed class Screen(val route: String) {
  data object Home: Screen("home")
  data object Profile: Screen("profile/{userId}") { fun route(userId: String) = "profile/$userId" }
}
NavHost(nav, Screen.Home.route) {
  composable(Screen.Home.route) { /*...*/ }
  composable(Screen.Profile.route) { val id = it.arguments!!.getString("userId")!! /*...*/ }
}
```

### Управление back stack
```kotlin
nav.navigate("home") { launchSingleTop = true }
nav.popBackStack()
nav.navigate("login") { popUpTo("home") { inclusive = true } }
```

### Bottom navigation (минимум)
```kotlin
Scaffold(bottomBar = {
  BottomNavigation {
    val current = nav.currentBackStackEntryAsState().value?.destination?.route
    BottomNavigationItem(selected = current=="home", onClick = {
      nav.navigate("home") { popUpTo(nav.graph.startDestinationId); launchSingleTop = true }
    }, icon = { Icon(Icons.Default.Home, null) })
  }
}) { padding ->
  NavHost(nav, "home", Modifier.padding(padding)) { composable("home") { Home() } }
}
```

Передача сложных объектов: предпочтительнее общий ViewModel, а не большие полезные нагрузки в роуте.

---

## Follow-ups
- How to structure nested graphs and save/restore state across tabs?
- Deep links and app links: route design and argument encoding best practices?
- Multi-activity vs single-activity navigation trade‑offs in Compose?

## References
- https://developer.android.com/jetpack/compose/navigation
- https://developer.android.com/guide/navigation

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-animated-visibility-vs-content--jetpack-compose--medium]]
- [[q-compose-gesture-detection--jetpack-compose--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--jetpack-compose--hard]]
- [[q-compose-custom-layout--jetpack-compose--hard]]
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]]
