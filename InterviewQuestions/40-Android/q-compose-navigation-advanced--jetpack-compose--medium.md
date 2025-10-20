---
id: 20251012-1227106
title: Compose Navigation Advanced / Продвинутая навигация Compose
aliases: [Compose Navigation Advanced, Продвинутая навигация Compose]
topic: android
subtopics: [ui-compose, navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/jetpack/compose/navigation
source_note: Official Compose Navigation docs
status: draft
moc: moc-android
related: [q-compose-navigation-advanced--android--medium, q-animated-visibility-vs-content--jetpack-compose--medium, q-compose-gesture-detection--jetpack-compose--medium]
created: 2025-10-15
updated: 2025-10-20
tags: [android/ui-compose, android/navigation, compose/navigation, difficulty/medium]
---
# Question (EN)
> How to implement type‑safe navigation in Compose with arguments, deep links, and back‑stack control? Show minimal patterns.

# Вопрос (RU)
> Как реализовать type‑safe навигацию в Compose с аргументами, deep links и управлением back‑stack? Приведите минимальные паттерны.

---

## Answer (EN)

### Minimal setup
- NavController owns back stack and current destination; NavHost maps route patterns to destinations.
- startDestination initializes the first back stack entry; each composable adds a destination node.
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

### Required vs optional args
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

### Type‑safe routes (sealed API)
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

### Deep links
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

### Back‑stack control
- launchSingleTop avoids duplicate top entries; popUpTo truncates the stack to a target (inclusive removes it).
- Use saveState/restoreState with bottom navigation to preserve screen state across tabs.
```kotlin
nav.navigate("home") { launchSingleTop = true }
nav.navigate("login") { popUpTo("home") { inclusive = true } }
nav.popBackStack()
```

Passing complex objects
- Prefer shared ViewModel/SavedStateHandle over large route payloads to avoid URL limits and encoding issues.

## Ответ (RU)

### Минимальная настройка
- NavController владеет back stack и текущей destination; NavHost сопоставляет паттерны роутов с экранами.
- startDestination инициализирует первый элемент стека; каждый composable добавляет узел назначения.
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

### Обязательные и опциональные аргументы
- Параметры в path позиционные и обязательные; query именованные и могут быть null с значениями по умолчанию.
- NavType обеспечивает проверку типов; кодируйте query при наличии спецсимволов.
```kotlin
// Обязательный path
composable("profile/{userId}", listOf(navArgument("userId") { type = NavType.StringType })) { /*...*/ }
nav.navigate("profile/123")

// Опциональный query
composable("search?query={q}", listOf(navArgument("q") { nullable = true })) { /*...*/ }
nav.navigate("search?query=kotlin")
```

### Типобезопасные маршруты (sealed API)
- Централизуйте паттерны и билдеры маршрутов, чтобы избежать опечаток в строках.
- Держите паттерн (с плейсхолдерами) отдельно от фабрики конкретного маршрута.
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

### Deep links
- Deep links сопоставляют входящие URI с маршрутами; плейсхолдеры должны соответствовать аргументам.
- В Android нужны intent‑фильтры в манифесте для app/https; deep links могут создавать back stack.
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

### Управление back‑stack
- launchSingleTop избегает дублей сверху; popUpTo обрезает стек до цели (inclusive удаляет её).
- Для bottom navigation используйте saveState/restoreState для сохранения состояния экранов.
```kotlin
nav.navigate("home") { launchSingleTop = true }
nav.navigate("login") { popUpTo("home") { inclusive = true } }
nav.popBackStack()
```

Передача сложных объектов
- Предпочтительнее общий ViewModel/SavedStateHandle вместо больших payload в роуте (лимиты URL и кодирование).

---

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
- [[q-animated-visibility-vs-content--jetpack-compose--medium]]
- [[q-compose-gesture-detection--jetpack-compose--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--jetpack-compose--hard]]
- [[q-compose-custom-layout--jetpack-compose--hard]]
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]]

