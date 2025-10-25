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
  - q-compose-navigation-advanced--android--medium
created: 2025-10-15
updated: 2025-10-20
tags: [android/ui-compose, android/ui-navigation, difficulty/medium]
source: https://developer.android.com/jetpack/compose/navigation
source_note: Official Compose Navigation docs
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:38 pm
---

# Вопрос (RU)
> Продвинутая навигация Compose?

# Question (EN)
> Compose Navigation Advanced?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Minimal Setup
- NavController owns back stack and current destination; NavHost maps route patterns to destinations using c-navigation-component.
- startDestination initializes the first back stack entry; each composable adds a destination node in [[c-jetpack-compose]].
```kotlin
@Composable
fun AppNav() {
  val nav = rememberNavController()
  NavHost(nav, startDestination = "home") {
    composable("home") { Home(onOpen = { id -> nav.navigate("details/$id") }) }
    composable("details/{id}", listOf(navArgument("id") { type = NavType.StringType })) {
      Details(it.arguments!!.getString("id")!!)
    }
  }
}
```

### Required Vs Optional Args
- Path args are positional and required; query args are named and can be nullable with defaults.
- NavType enforces runtime type safety; encode query values if they contain reserved characters.
```kotlin
// Required path
composable("profile/{userId}", listOf(navArgument("userId") { type = NavType.StringType })) { /*...*/ }
nav.navigate("profile/123")

// Optional query
composable("search?query={q}", listOf(navArgument("q") { nullable = true })) { /*...*/ }
nav.navigate("search?query=kotlin")
```

### Type‑safe Routes (sealed API)
- Centralize route patterns and builders to avoid string typos in UI code.
- Keep pattern (with placeholders) separate from factory that produces concrete routes.
```kotlin
sealed class Screen(val route: String) {
  data object Home: Screen("home")
  data object Profile: Screen("profile/{userId}") { fun route(id: String) = "profile/$id" }
}
NavHost(nav, Screen.Home.route) {
  composable(Screen.Home.route) { /*...*/ }
  composable(Screen.Profile.route) { val id = it.arguments!!.getString("userId")!! }
}
```

### Deep Links
- Deep links match incoming URIs to routes; placeholders must correspond to arguments.
- Android requires manifest intent filters for app/https links; deep links can create back stack.
```kotlin
composable(
  route = "profile/{userId}",
  arguments = listOf(navArgument("userId") { type = NavType.StringType }),
  deepLinks = listOf(
    navDeepLink { uriPattern = "myapp://profile/{userId}" },
    navDeepLink { uriPattern = "https://example.com/profile/{userId}" }
  )
) { /*...*/ }
```

### Back‑stack Control
- launchSingleTop avoids duplicate top entries; popUpTo truncates the stack to a target (inclusive removes it).
- Use saveState/restoreState with bottom navigation to preserve screen state across tabs.
```kotlin
nav.navigate("home") { launchSingleTop = true }
nav.navigate("login") { popUpTo("home") { inclusive = true } }
nav.popBackStack()
```

Passing complex objects
- Prefer shared ViewModel/SavedStateHandle over large route payloads to avoid URL limits and encoding issues.

## Follow-ups
- How to organize nested graphs and preserve state across tabs?
- What are best practices for deep links and argument encoding?
- How to combine multiple back stacks with bottom navigation?

## References
- https://developer.android.com/jetpack/compose/navigation
- https://developer.android.com/guide/navigation

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-compose-navigation-advanced--android--medium]]
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-gesture-detection--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]
