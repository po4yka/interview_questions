---
id: 20251012-122710
title: Compose Navigation Deep Dive / Навигация в Compose — детально
aliases:
- Compose Navigation Deep Dive
- Навигация в Compose — детально
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
status: reviewed
moc: moc-android
related:
- q-animated-visibility-vs-content--android--medium
- q-compose-gesture-detection--android--medium
- q-compose-compiler-plugin--android--hard
created: 2025-10-06
updated: 2025-10-20
tags:
- android/ui-compose
- android/ui-navigation
- difficulty/medium
source: https://developer.android.com/jetpack/compose/navigation
source_note: Official Compose Navigation docs
---

# Вопрос (RU)
> Навигация в Compose — детально?

# Question (EN)
> Compose Navigation Deep Dive?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core pieces
- NavController: holds navigation state in [[c-jetpack-compose]]
- NavHost: maps routes to destinations using [[c-navigation-component]]
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
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-gesture-detection--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]
