---
id: android-150
title: What Navigation Methods Do You Know / Какие методы навигации вы знаете
aliases:
- What Navigation Methods Do You Know
- Какие методы навигации вы знаете
topic: android
subtopics:
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
- c-compose-navigation
- c-fragments
- q-activity-navigation-how-it-works--android--medium
- q-how-navigation-is-implemented-in-android--android--medium
- q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium
sources: []
created: 2025-10-15
updated: 2025-01-27
tags:
- android
- android/ui-navigation
- difficulty/medium
- navigation
date created: Saturday, November 1st 2025, 12:47:09 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)

> Какие способы навигации вы знаете в Android?

# Question (EN)

> What navigation methods do you know in Android?

---

## Ответ (RU)

Android предлагает несколько основных подходов к навигации, каждый из которых решает конкретные архитектурные задачи.

### 1. Activity Navigation (Intent)

Традиционный подход для навигации между активностями.

```kotlin
class MainActivity : AppCompatActivity() {
    // ✅ Современный подход с Activity Result API
    private val detailsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            // Обработка результата
        }
    }

    // ❌ Устаревший startActivityForResult больше не используется
}
```

**Применение**: простые приложения, системная интеграция (камера, галерея).
**Недостатки**: высокий memory overhead, сложное управление back stack.

### 2. FragmentManager + FragmentTransaction

Ручное управление фрагментами для гибкой композиции UI в single-activity приложениях.

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailsFragment())
    .addToBackStack("details") // ✅ Сохраняет историю
    .commit()                   // ✅ Асинхронный коммит
```

**Применение**: сложные single-activity приложения, динамические UI.
**Недостатки**: требует ручного управления back stack, lifecycle, аргументами.

### 3. Navigation Component (Jetpack)

Современный граф-ориентированный подход с типобезопасными аргументами и визуальным редактором.

```kotlin
// ✅ Type-safe arguments с Safe Args plugin
val action = HomeFragmentDirections.actionHomeToDetails(itemId)
findNavController().navigate(action)

// ❌ Строковые ID подвержены ошибкам
findNavController().navigate("details/$itemId")
```

**Применение**: новые проекты, сложная навигация, deep links.
**Преимущества**: визуальный редактор графа, автоматический back stack, интеграция с Bottom/Drawer Navigation.

### 4. Compose Navigation

Декларативная навигация для Jetpack Compose приложений.

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onNavigate = { navController.navigate("details/$it") })
        }
        composable("details/{id}") { backStack ->
            val id = backStack.arguments?.getString("id")
            DetailsScreen(id, onBack = { navController.navigateUp() })
        }
    }
}
```

**Применение**: Compose-based приложения.
**Преимущества**: декларативный API, интеграция с Compose state, type-safe navigation с kotlinx-serialization.

### 5. Deep Links / App Links

URL-based навигация из внешних источников.

```xml
<!-- Navigation graph -->
<fragment android:id="@+id/detailsFragment">
    <deepLink
        app:uri="myapp://details/{itemId}"
        android:autoVerify="true" /> <!-- ✅ Верифицированные App Links -->
</fragment>
```

**Применение**: маркетинг, push-уведомления, web-to-app переходы.
**Критично**: правильная обработка в `onCreate` и `onNewIntent`.

### Архитектурные Паттерны Навигации

| Паттерн | Случай использования | Компоненты |
|---------|---------------------|------------|
| Bottom Navigation | 3-5 основных разделов | BottomNavigationView + Navigation Component |
| Tab Navigation | Связанный контент | ViewPager2 + TabLayout |
| Drawer Navigation | 6+ разделов | DrawerLayout + NavigationView |

### Best Practices

1. **Single-Activity архитектура** — фрагменты/Compose вместо множественных Activity
2. **Navigation Component** для новых проектов — type-safe аргументы, визуальный граф
3. **Правильный back stack** — используйте `popUpTo`, `launchSingleTop` для избежания дубликатов
4. **Deep links** — для маркетинга и улучшения UX

## Answer (EN)

Android provides several core navigation approaches, each addressing specific architectural needs.

### 1. Activity Navigation (Intent)

Traditional approach for navigating between activities.

```kotlin
class MainActivity : AppCompatActivity() {
    // ✅ Modern approach with Activity Result API
    private val detailsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            // Handle result
        }
    }

    // ❌ Deprecated startActivityForResult is no longer used
}
```

**Use case**: simple apps, system integration (camera, gallery).
**Drawbacks**: high memory overhead, complex back stack management.

### 2. FragmentManager + FragmentTransaction

Manual fragment management for flexible UI composition in single-activity apps.

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailsFragment())
    .addToBackStack("details") // ✅ Preserves history
    .commit()                   // ✅ Asynchronous commit
```

**Use case**: complex single-activity apps, dynamic UI.
**Drawbacks**: requires manual management of back stack, lifecycle, arguments.

### 3. Navigation Component (Jetpack)

Modern graph-based approach with type-safe arguments and visual editor.

```kotlin
// ✅ Type-safe arguments with Safe Args plugin
val action = HomeFragmentDirections.actionHomeToDetails(itemId)
findNavController().navigate(action)

// ❌ String IDs are error-prone
findNavController().navigate("details/$itemId")
```

**Use case**: new projects, complex navigation, deep links.
**Benefits**: visual graph editor, automatic back stack, integration with Bottom/Drawer Navigation.

### 4. Compose Navigation

Declarative navigation for Jetpack Compose apps.

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onNavigate = { navController.navigate("details/$it") })
        }
        composable("details/{id}") { backStack ->
            val id = backStack.arguments?.getString("id")
            DetailsScreen(id, onBack = { navController.navigateUp() })
        }
    }
}
```

**Use case**: Compose-based apps.
**Benefits**: declarative API, Compose state integration, type-safe navigation with kotlinx-serialization.

### 5. Deep Links / App Links

URL-based navigation from external sources.

```xml
<!-- Navigation graph -->
<fragment android:id="@+id/detailsFragment">
    <deepLink
        app:uri="myapp://details/{itemId}"
        android:autoVerify="true" /> <!-- ✅ Verified App Links -->
</fragment>
```

**Use case**: marketing, push notifications, web-to-app transitions.
**Critical**: proper handling in `onCreate` and `onNewIntent`.

### Navigation Architecture Patterns

| Pattern | Use Case | Components |
|---------|----------|------------|
| Bottom Navigation | 3-5 main sections | BottomNavigationView + Navigation Component |
| Tab Navigation | Related content | ViewPager2 + TabLayout |
| Drawer Navigation | 6+ sections | DrawerLayout + NavigationView |

### Best Practices

1. **Single-Activity architecture** — fragments/Compose instead of multiple Activities
2. **Navigation Component** for new projects — type-safe arguments, visual graph
3. **Proper back stack** — use `popUpTo`, `launchSingleTop` to avoid duplicates
4. **Deep links** — for marketing and improved UX

---

## Follow-ups

- How does Navigation Component handle process death and state restoration?
- What are the trade-offs between single-Activity and multi-Activity architecture?
- How to implement nested navigation graphs for modular features?
- What's the difference between Deep Links and App Links in terms of security?
- How to test navigation flows with Espresso or Compose UI tests?

## References

- Android Developer Documentation: Navigation Component
- Android Developer Guide: Single-Activity Architecture

## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-fragments]]


### Prerequisites

- Activity and Fragment lifecycle understanding
- Intent and Bundle fundamentals

### Related

- [[q-activity-navigation-how-it-works--android--medium]] - Deep dive into Activity navigation internals
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Deep link task stack management
- [[q-how-navigation-is-implemented-in-android--android--medium]] - Navigation implementation details

### Advanced

- Advanced Compose Navigation patterns (nested graphs, shared ViewModels)
- Multi-module navigation architecture with dynamic feature modules
