---
id: android-359
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
  - c-compose-navigation
  - q-android-jetpack-overview--android--easy
  - q-compose-side-effects-advanced--android--hard
  - q-compose-ui-testing-advanced--android--hard
  - q-how-dialog-differs-from-other-navigation--android--medium
created: 2025-09-10
updated: 2025-10-10
tags: [android/ui-compose, android/ui-navigation, difficulty/medium]
sources:
  - "https://developer.android.com/jetpack/compose/navigation"

date created: Saturday, November 1st 2025, 1:25:30 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---

# Вопрос (RU)
> Как реализовать продвинутую навигацию в Jetpack Compose с аргументами, deep links и контролем back stack?

# Question (EN)
> How to implement advanced navigation in Jetpack Compose with arguments, deep links, and back stack control?

---

## Ответ (RU)

### Типы Аргументов

**Path-аргументы** — обязательны, позиционны, часть URL. **Query-аргументы** — опциональны, поддерживают значения по умолчанию, задаются в маршруте как `?key={value}` и описываются через `navArgument`.

```kotlin
// ✅ Path-аргумент (обязательный)
composable(
  route = "profile/{userId}",
  arguments = listOf(navArgument("userId") { type = NavType.StringType })
) { entry ->
  ProfileScreen(entry.arguments?.getString("userId") ?: "")
}

// ✅ Query-аргумент (опциональный)
// Маршрут: search?query={query}, аргумент объявлен через navArgument
composable(
  route = "search?query={query}",
  arguments = listOf(
    navArgument("query") {
      type = NavType.StringType
      defaultValue = ""
      nullable = true
    }
  )
) { entry ->
  SearchScreen(entry.arguments?.getString("query"))
}
```

### Type-safe Маршруты

Используйте sealed class для централизованного определения маршрутов и избежания строковых ошибок.

```kotlin
sealed class Screen(val route: String) {
  data object Home : Screen("home")
  data object Profile : Screen("profile/{userId}") {
    fun createRoute(userId: String) = "profile/$userId" // ✅ Type-safe
  }
}

// Использование
nav.navigate(Screen.Profile.createRoute("123"))
```

### Deep Links

Deep links связывают внешние URI с маршрутами навигации. Для запуска извне (`myapp://` или `https://`) требуется `intent-filter` в манифесте, согласованный с шаблонами URI.

```kotlin
composable(
  route = "product/{id}",
  arguments = listOf(navArgument("id") { type = NavType.StringType }),
  deepLinks = listOf(
    navDeepLink { uriPattern = "myapp://product/{id}" }, // ✅ App scheme
    navDeepLink { uriPattern = "https://example.com/product/{id}" } // ✅ Web scheme
  )
) { entry ->
  ProductScreen(entry.arguments?.getString("id") ?: "")
}
```

Манифест (упрощенный пример; `<data>`-элементы должны соответствовать объявленным URI, может быть несколько `<data>` на один `intent-filter`):
```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />

  <!-- myapp://product/{id} -->
  <data android:scheme="myapp" android:host="product" />

  <!-- https://example.com/product/{id} -->
  <data
    android:scheme="https"
    android:host="example.com"
    android:pathPrefix="/product" />
</intent-filter>
```

### Контроль back Stack

**launchSingleTop** — предотвращает дублирование верхней записи. **popUpTo** — очищает стек до указанного маршрута; `inclusive = true` удаляет и сам маршрут. Для bottom navigation и сохранения состояния используйте комбинацию `saveState` и `restoreState`.

```kotlin
// ✅ Избегаем дублей
nav.navigate("home") { launchSingleTop = true }

// ✅ Очистка стека (login → main, удалить login)
nav.navigate("main") {
  popUpTo("login") { inclusive = true }
}

// ✅ Bottom nav с сохранением состояния при повторном выборе
nav.navigate("home") {
  launchSingleTop = true
  saveState = true
  restoreState = true
}

// ❌ Без опций создаст дубликаты при повторной навигации
nav.navigate("home")
```

### Передача Сложных Данных

Для сложных объектов используйте **shared `ViewModel`**, привязанный к общему `NavBackStackEntry` (например, к графу нижней навигации или activity), или **SavedStateHandle** для восстановления после гибели процесса. URL-параметры ограничены по размеру и типам.

```kotlin
// ✅ Shared ViewModel
@HiltViewModel
class SharedDataViewModel @Inject constructor() : ViewModel() {
  private val _data = MutableStateFlow<Data?>(null)
  val data = _data.asStateFlow()
  fun setData(data: Data) { _data.value = data }
}

// В источнике (оба экрана должны получать ViewModel из одного и того же scope)
viewModel.setData(complexObject)
nav.navigate("details")

// В назначении
val data = viewModel.data.collectAsState().value
```

### Дополнительные Вопросы (RU)

- Как реализовать вложенные графы навигации для feature-модулей?
- Как тестировать навигационные потоки с `NavController` в unit/UI-тестах?
- Как обрабатывать навигацию с несколькими back stack (bottom nav с независимыми стеками)?
- Как сохранять и восстанавливать состояние навигации после гибели процесса?
- Как реализовать условную навигацию (login-gate, permissions)?

### Ссылки (RU)

- [[c-compose-navigation]]
- https://developer.android.com/jetpack/compose/navigation
- https://developer.android.com/guide/navigation/design

### Связанные Вопросы (RU)

#### Предварительные (проще)
- [[q-android-jetpack-overview--android--easy]]

#### Продвинутые (сложнее)
- [[q-compose-custom-layout--android--hard]]

## Answer (EN)

### Argument Types

**Path arguments** are required, positional, and part of the URL. **Query arguments** are optional, support defaults, and are defined in the route as `?key={value}` with a corresponding `navArgument`.

```kotlin
// ✅ Path argument (required)
composable(
  route = "profile/{userId}",
  arguments = listOf(navArgument("userId") { type = NavType.StringType })
) { entry ->
  ProfileScreen(entry.arguments?.getString("userId") ?: "")
}

// ✅ Query argument (optional)
// Route: search?query={query}, argument declared via navArgument
composable(
  route = "search?query={query}",
  arguments = listOf(
    navArgument("query") {
      type = NavType.StringType
      defaultValue = ""
      nullable = true
    }
  )
) { entry ->
  SearchScreen(entry.arguments?.getString("query"))
}
```

### Type-safe Routes

Use sealed classes for centralized route definitions and string safety.

```kotlin
sealed class Screen(val route: String) {
  data object Home : Screen("home")
  data object Profile : Screen("profile/{userId}") {
    fun createRoute(userId: String) = "profile/$userId" // ✅ Type-safe
  }
}

// Usage
nav.navigate(Screen.Profile.createRoute("123"))
```

### Deep Links

Deep links map external URIs to navigation routes. To open from outside (`myapp://` or `https://`), you need a manifest `intent-filter` aligned with your URI patterns.

```kotlin
composable(
  route = "product/{id}",
  arguments = listOf(navArgument("id") { type = NavType.StringType }),
  deepLinks = listOf(
    navDeepLink { uriPattern = "myapp://product/{id}" }, // ✅ App scheme
    navDeepLink { uriPattern = "https://example.com/product/{id}" } // ✅ Web scheme
  )
) { entry ->
  ProductScreen(entry.arguments?.getString("id") ?: "")
}
```

Manifest (simplified; `<data>` elements should match the declared URIs, and you can have multiple `<data>` entries per `intent-filter`):
```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />

  <!-- myapp://product/{id} -->
  <data android:scheme="myapp" android:host="product" />

  <!-- https://example.com/product/{id} -->
  <data
    android:scheme="https"
    android:host="example.com"
    android:pathPrefix="/product" />
</intent-filter>
```

### Back Stack Control

**launchSingleTop** prevents duplicate top entries. **popUpTo** clears the stack up to the target route; `inclusive = true` removes the target itself. For bottom navigation and state preservation, combine `saveState` and `restoreState`.

```kotlin
// ✅ Avoid duplicates
nav.navigate("home") { launchSingleTop = true }

// ✅ Clear stack (login → main, remove login)
nav.navigate("main") {
  popUpTo("login") { inclusive = true }
}

// ✅ Bottom nav with state preservation on reselection
nav.navigate("home") {
  launchSingleTop = true
  saveState = true
  restoreState = true
}

// ❌ Creates duplicates without options on repeated navigation
nav.navigate("home")
```

### Passing Complex Data

For complex objects, use a **shared `ViewModel`** scoped to a shared `NavBackStackEntry` (e.g., a navigation graph or the activity), or **SavedStateHandle** for restoration after process death. URL parameters are limited in size and supported types.

```kotlin
// ✅ Shared ViewModel
@HiltViewModel
class SharedDataViewModel @Inject constructor() : ViewModel() {
  private val _data = MutableStateFlow<Data?>(null)
  val data = _data.asStateFlow()
  fun setData(data: Data) { _data.value = data }
}

// In source (both screens must obtain the ViewModel from the same scope)
viewModel.setData(complexObject)
nav.navigate("details")

// In destination
val data = viewModel.data.collectAsState().value
```

## Follow-ups

- How to implement nested navigation graphs for feature modules?
- How to test navigation flows with `NavController` in unit/UI tests?
- How to handle multi-backstack navigation (bottom nav with independent stacks)?
- How to preserve/restore navigation state across process death?
- How to implement conditional navigation (login gates, permissions)?

## References

- [[c-compose-navigation]]
- https://developer.android.com/jetpack/compose/navigation
- https://developer.android.com/guide/navigation/design

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]]
