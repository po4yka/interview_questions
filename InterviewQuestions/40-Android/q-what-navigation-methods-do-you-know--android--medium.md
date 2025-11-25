---
id: android-150
title: What Navigation Methods Do You Know / Какие методы навигации вы знаете
aliases: [What Navigation Methods Do You Know, Какие методы навигации вы знаете]
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
  - q-navigation-methods-in-kotlin--android--medium
  - q-what-do-you-know-about-modifiers--android--medium
  - q-what-navigation-methods-exist-in-kotlin--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android, android/ui-navigation, difficulty/medium, navigation]

date created: Saturday, November 1st 2025, 12:47:09 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Какие способы навигации вы знаете в Android?

# Question (EN)

> What navigation methods do you know in Android?

---

## Ответ (RU)

Android предлагает несколько основных подходов к навигации, каждый из которых решает конкретные архитектурные задачи.

### 1. `Activity` Navigation (`Intent`)

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

    // ⚠️ startActivityForResult устарел (deprecated) и не рекомендуется для новых проектов,
    //    но по-прежнему используется в легаси-коде.
}
```

**Применение**: простые приложения, системная интеграция (камера, галерея).
**Недостатки**: относительно высокий overhead на уровне жизненного цикла `Activity`, более тяжёлый back stack по сравнению с фрагментами/Compose, сложное управление возвращаемыми результатами без `Activity` Result API.

### 2. FragmentManager + FragmentTransaction

Ручное управление фрагментами для гибкой композиции UI в single-activity приложениях.

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailsFragment())
    .addToBackStack("details") // ✅ Сохраняет историю
    .commit()                   // 🔄 Операция планируется и будет применена на главном потоке позже
```

**Применение**: сложные single-activity приложения, динамические UI.
**Недостатки**: требует ручного управления back stack, lifecycle, аргументами; важно понимать разницу между `commit()`, `commitNow()` и вариантами с `allowingStateLoss`.

### 3. Navigation Component (Jetpack)

Современный граф-ориентированный подход с типобезопасными аргументами (при использовании Safe Args) и визуальным редактором.

```kotlin
// ✅ Type-safe arguments с Safe Args plugin
val action = HomeFragmentDirections.actionHomeToDetails(itemId)
findNavController().navigate(action)

// ⚠️ Строковые маршруты / ID более подвержены ошибкам
findNavController().navigate("details/$itemId")
```

**Применение**: новые проекты, сложная навигация, deep links.
**Преимущества**: визуальный редактор графа, управление back stack через навграф, интеграция с Bottom/Drawer Navigation.

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
**Преимущества**: декларативный API, интеграция с состоянием Compose; возможно построить более типобезопасную навигацию (например, с использованием официальных Nav-Compose API с поддержкой сериализации), но это требует явной настройки и не включено "по умолчанию" во всех проектах.

### 5. Deep Links / App Links

URL-based навигация из внешних источников.

```xml
<!-- Пример deep link в navigation graph -->
<fragment
    android:id="@+id/detailsFragment"
    android:name="com.example.DetailsFragment">
    <argument
        android:name="itemId"
        app:argType="string" />
    <deepLink
        app:uri="myapp://details/{itemId}" />
</fragment>
```

```xml
<!-- Пример Android App Links в манифесте -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="example.com"
        android:pathPrefix="" />
</intent-filter>
```

**Применение**: маркетинг, push-уведомления, web-to-app переходы.
**Критично**: корректная обработка входящих интентов (например, в `onCreate` / `onNewIntent` или NavHost) и различение обычных deep links и верифицированных App Links.

### Архитектурные Паттерны Навигации

| Паттерн | Случай использования | Компоненты |
|---------|---------------------|------------|
| Bottom Navigation | 3-5 основных разделов | BottomNavigationView + Navigation Component |
| Tab Navigation | Связанный контент | ViewPager2 + TabLayout |
| Drawer Navigation | 6+ разделов или реже используемые разделы | DrawerLayout + NavigationView |

### Best Practices

1. **Single-`Activity` архитектура** — распространённый современный подход (особенно с фрагментами и Compose), но может сочетаться с несколькими `Activity` при необходимости (auth, onboarding и т.п.).
2. **Navigation Component** для новых проектов — удобное управление графом, аргументами и back stack.
3. **Правильный back stack** — используйте `popUpTo`, `launchSingleTop` и соответствующие options, чтобы избегать дубликатов экранов и контролировать историю.
4. **Deep links/App Links** — используйте для улучшения UX и маркетинга; обеспечьте безопасную обработку и корректное восстановление стека.

---

## Answer (EN)

Android provides several core navigation approaches, each addressing specific architectural needs.

### 1. `Activity` Navigation (`Intent`)

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

    // ⚠️ startActivityForResult is deprecated and not recommended for new code,
    //    but it's still present in legacy/maintained apps.
}
```

**Use case**: simple apps, system integration (camera, gallery).
**Drawbacks**: relatively heavy lifecycle/back stack compared to fragment/Compose navigation, and result handling is more cumbersome without the `Activity` Result API.

### 2. FragmentManager + FragmentTransaction

Manual fragment management for flexible UI composition in single-activity apps.

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailsFragment())
    .addToBackStack("details") // ✅ Preserves history
    .commit()                   // 🔄 Schedules the transaction to be applied on the main thread
```

**Use case**: complex single-activity apps, dynamic UI.
**Drawbacks**: requires manual management of back stack, lifecycle, and arguments; it's important to understand the difference between `commit()`, `commitNow()`, and the `allowingStateLoss` variants.

### 3. Navigation Component (Jetpack)

Modern graph-based approach with type-safe arguments (when using Safe Args) and a visual editor.

```kotlin
// ✅ Type-safe arguments with Safe Args plugin
val action = HomeFragmentDirections.actionHomeToDetails(itemId)
findNavController().navigate(action)

// ⚠️ String-based routes/IDs are more error-prone
findNavController().navigate("details/$itemId")
```

**Use case**: new projects, complex navigation, deep links.
**Benefits**: visual graph editor, back stack driven by the navigation graph, integration with Bottom/Drawer Navigation.

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
**Benefits**: declarative API, integration with Compose state; more type-safe navigation can be achieved (e.g., with the official Navigation Compose serialization support), but it requires explicit setup and is not implicit in all projects.

### 5. Deep Links / App Links

URL-based navigation from external sources.

```xml
<!-- Example deep link in a navigation graph -->
<fragment
    android:id="@+id/detailsFragment"
    android:name="com.example.DetailsFragment">
    <argument
        android:name="itemId"
        app:argType="string" />
    <deepLink
        app:uri="myapp://details/{itemId}" />
</fragment>
```

```xml
<!-- Example Android App Links in the manifest -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="example.com"
        android:pathPrefix="" />
</intent-filter>
```

**Use case**: marketing, push notifications, web-to-app transitions.
**Critical**: correctly handle incoming intents (e.g., in `onCreate` / `onNewIntent` or via the NavHost) and distinguish between generic deep links and verified App Links.

### Navigation Architecture Patterns

| Pattern | Use Case | Components |
|---------|----------|------------|
| Bottom Navigation | 3-5 main sections | BottomNavigationView + Navigation Component |
| Tab Navigation | Related content | ViewPager2 + TabLayout |
| Drawer Navigation | 6+ or less-frequently used sections | DrawerLayout + NavigationView |

### Best Practices

1. **Single-`Activity` architecture** — a common modern pattern (especially with Fragments and Compose), but you can still use multiple Activities where it makes sense (e.g., auth/onboarding).
2. **Navigation Component** for new projects — convenient graph-based navigation, arguments handling, and back stack control.
3. **Proper back stack** — use `popUpTo`, `launchSingleTop`, and related options to avoid duplicate destinations and to control history.
4. **Deep links/App Links** — leverage them for better UX and marketing; ensure secure handling and correct task/back stack behavior.

---

## Дополнительные Вопросы (RU)

- Как Navigation Component обрабатывает уничтожение процесса и восстановление состояния?
- В чём плюсы и минусы архитектуры с одной `Activity` по сравнению с многими `Activity`?
- Как реализовать вложенные графы навигации для модульных фич?
- В чём разница между Deep Links и App Links с точки зрения безопасности?
- Как тестировать навигационные потоки с помощью Espresso или Compose UI-тестов?

## Follow-ups

- How does Navigation Component handle process death and state restoration?
- What are the trade-offs between single-`Activity` and multi-`Activity` architecture?
- How to implement nested navigation graphs for modular features?
- What's the difference between Deep Links and App Links in terms of security?
- How to test navigation flows with Espresso or Compose UI tests?

## Ссылки (RU)

- Документация Android Developers: Navigation Component
- Руководство Android Developers: архитектура с одной `Activity`

## References

- Android Developer Documentation: Navigation Component
- Android Developer Guide: Single-`Activity` Architecture

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[c-compose-navigation]]
- [[c-fragments]]

### Предварительные Требования

- Понимание жизненного цикла `Activity` и `Fragment`
- Базовые знания `Intent` и `Bundle`

### Связанные Материалы

- [[q-activity-navigation-how-it-works--android--medium]] — подробности работы навигации между `Activity`
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] — управление стеком задач при deep links
- [[q-how-navigation-is-implemented-in-android--android--medium]] — подробности реализации навигации

### Продвинутое

- Продвинутые паттерны навигации в Compose (вложенные графы, общие `ViewModel`)
- Архитектура навигации в multi-module проектах с dynamic feature modules

## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-fragments]]

### Prerequisites

- `Activity` and `Fragment` lifecycle understanding
- `Intent` and `Bundle` fundamentals

### Related

- [[q-activity-navigation-how-it-works--android--medium]] - Deep dive into `Activity` navigation internals
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Deep link task stack management
- [[q-how-navigation-is-implemented-in-android--android--medium]] - Navigation implementation details

### Advanced

- Advanced Compose Navigation patterns (nested graphs, shared ViewModels)
- Multi-module navigation architecture with dynamic feature modules
