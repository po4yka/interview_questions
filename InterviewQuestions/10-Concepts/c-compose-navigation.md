---
id: ivc-20251030-120000
title: Compose Navigation / Навигация в Compose
aliases: [Compose Navigation, Navigation Compose, Навигация Compose]
kind: concept
summary: Navigation component for Jetpack Compose with type-safe routing
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, jetpack-compose, navigation, ui]
date created: Thursday, October 30th 2025, 12:29:19 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

Navigation component designed specifically for Jetpack Compose that enables type-safe navigation between composable destinations. Uses `NavController` for navigation state management, `NavHost` as a container for composable destinations, and supports argument passing, deep links, and back stack manipulation. Promotes declarative navigation with sealed classes for route definitions.

# Сводка (RU)

Компонент навигации, разработанный специально для Jetpack Compose, обеспечивающий типобезопасную навигацию между composable-экранами. Использует `NavController` для управления состоянием навигации, `NavHost` как контейнер для composable-назначений, поддерживает передачу аргументов, deep links и манипуляции со стеком возврата. Продвигает декларативную навигацию с sealed классами для определения маршрутов.

---

## Core Components (EN)

**NavController**: Central navigation coordinator that manages the back stack and navigation state
```kotlin
val navController = rememberNavController()
```

**NavHost**: Container composable that displays the current destination based on the route
```kotlin
NavHost(
    navController = navController,
    startDestination = "home"
) {
    composable("home") { HomeScreen() }
    composable("profile/{userId}") { backStackEntry ->
        ProfileScreen(userId = backStackEntry.arguments?.getString("userId"))
    }
}
```

**Composable Destinations**: Define navigation graph with composable builders

## Основные Компоненты (RU)

**NavController**: Центральный координатор навигации, управляющий стеком возврата и состоянием навигации

**NavHost**: Composable-контейнер, отображающий текущее назначение на основе маршрута

**Composable-назначения**: Определяют граф навигации с помощью composable-билдеров

---

## Type-Safe Navigation (EN)

**Sealed Class Routes**: Define routes as sealed classes for compile-time safety
```kotlin
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Profile : Screen("profile/{userId}") {
        fun createRoute(userId: String) = "profile/$userId"
    }
}

// Navigation
navController.navigate(Screen.Profile.createRoute(userId))

// Graph definition
composable(Screen.Home.route) { HomeScreen() }
composable(Screen.Profile.route) { ProfileScreen() }
```

## Типобезопасная Навигация (RU)

**Sealed-классы для маршрутов**: Определение маршрутов как sealed-классов для безопасности на этапе компиляции

```kotlin
// Навигация
navController.navigate(Screen.Profile.createRoute(userId))
```

---

## Key Features (EN)

1. **Argument Passing**: Required and optional arguments via route patterns
2. **Deep Links**: Support for implicit and explicit deep links
3. **Back Stack Management**: `popBackStack()`, `popUpTo`, `launchSingleTop`
4. **ViewModel Scoping**: Scope ViewModels to navigation graph or destination
5. **Nested Navigation**: Support for nested NavHosts and bottom navigation

```kotlin
// Back stack control
navController.navigate("details") {
    popUpTo("home") { inclusive = false }
    launchSingleTop = true
}

// ViewModel scoping
val viewModel: SharedViewModel = viewModel(
    viewModelStoreOwner = navController.getBackStackEntry("parentRoute")
)
```

## Ключевые Возможности (RU)

1. **Передача аргументов**: Обязательные и опциональные аргументы через паттерны маршрутов
2. **Deep Links**: Поддержка implicit и explicit deep links
3. **Управление стеком**: `popBackStack()`, `popUpTo`, `launchSingleTop`
4. **Область ViewModel**: Привязка ViewModel к графу навигации или назначению
5. **Вложенная навигация**: Поддержка вложенных NavHosts и нижней навигации

---

## Best Practices (EN)

1. **Single NavController**: One NavController per app/activity, passed down as needed
2. **Hoist NavController**: Keep NavController at top level, pass navigation callbacks down
3. **Type-Safe Routes**: Use sealed classes/objects for route definitions
4. **SavedStateHandle**: Access arguments via ViewModel's SavedStateHandle
5. **Testing**: Use TestNavHostController for navigation testing

## Лучшие Практики (RU)

1. **Единый NavController**: Один NavController на приложение/activity
2. **Подъем NavController**: Держать NavController на верхнем уровне, передавать navigation callbacks вниз
3. **Типобезопасные маршруты**: Использовать sealed классы/объекты для определения маршрутов
4. **SavedStateHandle**: Получать аргументы через SavedStateHandle ViewModel
5. **Тестирование**: Использовать TestNavHostController для тестирования навигации

---

## Use Cases / Trade-offs

**Use When**:
- Building Compose-first applications
- Need type-safe navigation with compile-time checks
- Want declarative navigation graph definition
- Integrating with Compose state management

**Avoid When**:
- Using legacy View-based navigation (use Navigation Component instead)
- Need complex multi-module navigation (consider feature-based navigation abstractions)

**Trade-offs**:
- Learning curve for developers familiar with Fragment-based navigation
- Limited animation customization compared to custom solutions
- Route string parsing overhead (mitigated by type-safe wrappers)

---

## References

- [Official Jetpack Compose Navigation Documentation](https://developer.android.com/jetpack/compose/navigation)
- [Navigation with Compose Codelab](https://developer.android.com/codelabs/jetpack-compose-navigation)
- [Type-safe Navigation in Compose](https://developer.android.com/guide/navigation/design/type-safety)
