---
id: android-345
title: "Navigation Methods In Android / Методы навигации в Android"
aliases: ["Navigation Methods In Android", "Методы навигации в Android"]
topic: android
subtopics: [architecture-modularization, intents-deeplinks, ui-navigation]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity, c-compose-navigation, c-content-provider]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/architecture-modularization, android/intents-deeplinks, android/ui-navigation, difficulty/medium, navigation, ui]

date created: Saturday, November 1st 2025, 1:25:26 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)

> Какие способы навигации в Android знаешь?

# Question (EN)

> What navigation methods in Android do you know?

---

## Ответ (RU)

Android предоставляет несколько методов навигации, каждый со своими преимуществами и сценариями использования:

### 1. Навигация Между `Activity` Через `Intent`

Традиционный способ перехода между экранами на уровне `Activity`. `Intent` может быть явным (explicit) или неявным (implicit).

```kotlin
// ✅ Явный Intent - прямой переход к конкретной Activity
val intent = Intent(this, DetailActivity::class.java).apply {
    putExtra("item_id", 42)
}
startActivity(intent)

// ✅ Intent с результатом через Activity Result API
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result_data")
    }
}

launcher.launch(Intent(this, DetailActivity::class.java))

// ❌ Устаревший способ - использование startActivityForResult
// startActivityForResult(intent, REQUEST_CODE)  // Deprecated
```

**Когда использовать**: системная интеграция, запуск внешних `Activity`, навигация между крупными фичами или модулями. В современных приложениях для внутренних экранов чаще предпочитается single-activity + фрагменты/Compose.

### 2. Навигация На Основе `Fragment` С FragmentManager

Управление фрагментами внутри одной `Activity`. Позволяет создавать модульные UI-компоненты и управлять back stack.

```kotlin
// ✅ Рекомендуемый подход с FragmentContainerView и reordering
supportFragmentManager.commit {
    setReorderingAllowed(true)
    replace(R.id.fragment_container, DetailFragment())
    addToBackStack("detail")
}

// ⚠️ commitAllowingStateLoss - использовать осознанно, только если допустима потеря состояния
if (!isFinishing && !isDestroyed) {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, DetailFragment())
        .commitAllowingStateLoss() // Может скрыть проблемы потери состояния
}

// ⚠️ Простой commit без setReorderingAllowed сам по себе не "неправильный",
// но при сложных транзакциях reordering помогает избежать ошибок восстановления состояния.
// supportFragmentManager.beginTransaction()
//     .replace(R.id.container, DetailFragment())
//     .commit()
```

**Когда использовать**: single-activity архитектура, управление сложным UI внутри одного экрана, master-detail layouts.

### 3. Navigation Component Из Jetpack

Декларативная система навигации с визуальным редактором, поддержкой SafeArgs и автоматическим управлением back stack.

```kotlin
// ✅ Type-safe навигация с SafeArgs
val action = HomeFragmentDirections.actionHomeToDetail(itemId = 42)
findNavController().navigate(action)

// ✅ Навигация с опциями анимации и popUpTo
findNavController().navigate(
    R.id.action_home_to_detail,
    bundleOf("item_id" to 42),
    navOptions {
        anim {
            enter = R.anim.slide_in_right
            exit = R.anim.slide_out_left
            popEnter = R.anim.slide_in_left
            popExit = R.anim.slide_out_right
        }
        popUpTo(R.id.homeFragment) { inclusive = false }
    }
)

// ✅ Получение результата из другого фрагмента через SavedStateHandle
findNavController().currentBackStackEntry
    ?.savedStateHandle
    ?.getLiveData<String>("result_key")
    ?.observe(viewLifecycleOwner) { result ->
        // Обработка результата
    }
```

**Когда использовать**: сложные навигационные графы, типобезопасная передача аргументов, автоматическая обработка deep links и up/back навигации, единая архитектура навигации.

### 4. Bottom/Tab Navigation С BottomNavigationView Или TabLayout

Навигация между главными разделами приложения через bottom bar или tabs.

```kotlin
// ✅ Базовый пример Bottom Navigation
bottomNav.setOnItemSelectedListener { item ->
    val fragment = when (item.itemId) {
        R.id.nav_home -> HomeFragment()
        R.id.nav_search -> SearchFragment()
        R.id.nav_profile -> ProfileFragment()
        else -> return@setOnItemSelectedListener false
    }

    supportFragmentManager.commit {
        replace(R.id.container, fragment)
        // Обычно НЕ добавляем в back stack для bottom navigation,
        // чтобы системная "назад" возвращала на предыдущие экраны, а не между табами.
    }
    true
}

// ✅ Предпочтительно с Navigation Component + несколькими back stack-ами
val navController = findNavController(R.id.nav_host_fragment)
binding.bottomNav.setupWithNavController(navController)
```

**Когда использовать**: главные разделы приложения (3-5 основных экранов). Для сохранения состояния разделов рекомендуется хранить отдельные back stack-и (через Navigation Component или управление фрагментами без пересоздания при каждом выборе).

### 5. Deep Links И App Links

Навигация по URL-схемам для внешних и внутренних переходов.

```kotlin
// ✅ Создание Deep Link с NavDeepLinkBuilder
val pendingIntent = NavDeepLinkBuilder(context)
    .setGraph(R.navigation.nav_graph)
    .setDestination(R.id.detailFragment)
    .setArguments(bundleOf("item_id" to 42))
    .createPendingIntent()

// ✅ Обработка входящего Intent в Activity при использовании Navigation Component
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    val navController = findNavController(R.id.nav_host_fragment)
    intent?.data?.let { uri ->
        // Если deep link не обработан автоматически (например, кастомная логика), можно явно навигировать
        if (!navController.handleDeepLink(intent)) {
            navController.navigate(uri)
        }
    }
}
```

**Манифест**:
```xml
<!-- ✅ App Link с верификацией домена -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https"
          android:host="example.com"
          android:pathPrefix="/detail" />
</intent-filter>
```

**Когда использовать**: внешние переходы из уведомлений, email, web-страниц, динамические ссылки, универсальные ссылки. Navigation Component может автоматически обрабатывать deep links, сопоставленные с графом.

### 6. Навигация В Jetpack Compose С NavHost И NavController

Compose-native навигация для полностью декларативных UI.

```kotlin
// ✅ Настройка навигационного графа в Compose
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onNavigateToDetail = { itemId ->
                // Для простых id допустимо, для строк/сложных данных использовать аргументы/encoding
                navController.navigate("detail/$itemId")
            })
        }

        composable(
            route = "detail/{itemId}",
            arguments = listOf(navArgument("itemId") { type = NavType.IntType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId") ?: 0
            DetailScreen(itemId = itemId)
        }
    }
}

// ✅ Передача сложных объектов через ViewModel или сохранение в репозитории/Shared ViewModel
@Composable
fun DetailScreen(
    itemId: Int,
    viewModel: DetailViewModel = hiltViewModel()
) {
    LaunchedEffect(itemId) {
        viewModel.loadItem(itemId)
    }
    // UI
}
```

**Когда использовать**: полностью Compose-based приложения, декларативная навигация, интеграция с Compose state management и Navigation Component.

### 7. Navigation Drawer

Боковое меню для доступа к дополнительным разделам приложения.

```kotlin
// ✅ Drawer с Navigation Component
val navController = findNavController(R.id.nav_host_fragment)
binding.navView.setupWithNavController(navController)

binding.drawerLayout.addDrawerListener(
    ActionBarDrawerToggle(
        this,
        binding.drawerLayout,
        binding.toolbar,
        R.string.navigation_drawer_open,
        R.string.navigation_drawer_close
    )
)
```

**Когда использовать**: второстепенные разделы, настройки, профиль пользователя, дополнительные функции (обычно когда разделов много, 6+).

---

## Ответ: Дополнительные Вопросы (RU)

- Как Navigation Component обрабатывает изменения конфигурации и убийство процесса?
- В чем преимущества и недостатки single-activity по сравнению с multi-activity архитектурой?
- Как реализовать вложенные графы навигации с помощью Navigation Component?
- В чем разница между Deep Links и App Links?
- Как шарить `ViewModel` между фрагментами при использовании Navigation Component?
- Как реализовать условную навигацию в зависимости от состояния пользователя?
- Каковы лучшие практики для анимаций и переходов между экранами?

## Ответ: Ссылки (RU)

- [[c-activity-lifecycle]]
- [[c-compose-navigation]]
- [Navigation](https://developer.android.com/guide/navigation)
- https://developer.android.com/guide/navigation/navigation-deep-link

## Ответ: Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-what-is-intent--android--easy]] - Базовые понятия `Intent`
- [[q-fragment-basics--android--easy]] - Основы `Fragment`
- [[q-main-android-components--android--easy]] - Обзор компонентов Android
- [[q-android-app-components--android--easy]] - Типы основных компонентов приложения

### Связанные (такой Же уровень)
- [[q-navigation-methods-android--android--medium]] - Альтернативные паттерны навигации
- [[q-deep-link-vs-app-link--android--medium]] - Стратегии deep linking
- [[q-single-activity-approach--android--medium]] - Архитектура с одной `Activity`
- [[q-compose-navigation-advanced--android--medium]] - Продвинутая навигация в Compose

### Продвинутые (сложнее)
- [[q-shared-element-transitions--android--hard]] - Продвинутые переходы между экранами
- [[q-modularization-patterns--android--hard]] - Навигация в мульти-модульной архитектуре
- [[q-how-to-create-dynamic-screens-at-runtime--android--hard]] - Динамическое создание экранов во время выполнения

## Answer (EN)

Android provides several navigation methods, each with its own advantages and use cases:

### 1. `Activity` Navigation via `Intent`

Traditional way of navigating between screens at the `Activity` level. Intents can be explicit or implicit.

```kotlin
// ✅ Explicit Intent - direct navigation to specific Activity
val intent = Intent(this, DetailActivity::class.java).apply {
    putExtra("item_id", 42)
}
startActivity(intent)

// ✅ Intent with result using Activity Result API
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("result_data")
    }
}

launcher.launch(Intent(this, DetailActivity::class.java))

// ❌ Deprecated approach - using startActivityForResult
// startActivityForResult(intent, REQUEST_CODE)  // Deprecated
```

**When to use**: system-level integration, launching external Activities, navigation between major features or modules. In modern apps, internal screen navigation is often handled via a single-activity approach with Fragments/Compose.

### 2. `Fragment`-Based Navigation with FragmentManager

Managing fragments within a single `Activity`. Enables modular UI components and back stack management.

```kotlin
// ✅ Recommended approach with FragmentContainerView and reordering
supportFragmentManager.commit {
    setReorderingAllowed(true)
    replace(R.id.fragment_container, DetailFragment())
    addToBackStack("detail")
}

// ⚠️ commitAllowingStateLoss - use carefully, only when state loss is acceptable
if (!isFinishing && !isDestroyed) {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, DetailFragment())
        .commitAllowingStateLoss() // Can hide state loss issues
}

// ⚠️ A simple commit without setReorderingAllowed is not inherently wrong,
// but for complex transactions reordering helps avoid state restoration issues.
// supportFragmentManager.beginTransaction()
//     .replace(R.id.container, DetailFragment())
//     .commit()
```

**When to use**: single-activity architecture, complex UI management within one screen, master-detail layouts.

### 3. Navigation Component from Jetpack

Declarative navigation system with visual editor, SafeArgs support, and automatic back stack management.

```kotlin
// ✅ Type-safe navigation with SafeArgs
val action = HomeFragmentDirections.actionHomeToDetail(itemId = 42)
findNavController().navigate(action)

// ✅ Navigation with animation options and popUpTo
findNavController().navigate(
    R.id.action_home_to_detail,
    bundleOf("item_id" to 42),
    navOptions {
        anim {
            enter = R.anim.slide_in_right
            exit = R.anim.slide_out_left
            popEnter = R.anim.slide_in_left
            popExit = R.anim.slide_out_right
        }
        popUpTo(R.id.homeFragment) { inclusive = false }
    }
)

// ✅ Getting result from another fragment via SavedStateHandle
findNavController().currentBackStackEntry
    ?.savedStateHandle
    ?.getLiveData<String>("result_key")
    ?.observe(viewLifecycleOwner) { result ->
        // Handle result
    }
```

**When to use**: complex navigation graphs, type-safe argument passing, automatic deep link and up/back handling, unified navigation architecture.

### 4. Bottom/Tab Navigation with BottomNavigationView or TabLayout

Navigation between main app sections via bottom bar or tabs.

```kotlin
// ✅ Basic Bottom Navigation example
bottomNav.setOnItemSelectedListener { item ->
    val fragment = when (item.itemId) {
        R.id.nav_home -> HomeFragment()
        R.id.nav_search -> SearchFragment()
        R.id.nav_profile -> ProfileFragment()
        else -> return@setOnItemSelectedListener false
    }

    supportFragmentManager.commit {
        replace(R.id.container, fragment)
        // Typically DON'T add to backstack for bottom navigation,
        // so system back navigates through screen history, not between tabs.
    }
    true
}

// ✅ Prefer using Navigation Component with multiple back stacks
val navController = findNavController(R.id.nav_host_fragment)
binding.bottomNav.setupWithNavController(navController)
```

**When to use**: main app sections (3-5 primary screens). To preserve section state, prefer keeping separate back stacks (via Navigation Component or fragment management without recreating on each selection).

### 5. Deep Links and App Links

URL-based navigation for external and internal transitions.

```kotlin
// ✅ Creating Deep Link with NavDeepLinkBuilder
val pendingIntent = NavDeepLinkBuilder(context)
    .setGraph(R.navigation.nav_graph)
    .setDestination(R.id.detailFragment)
    .setArguments(bundleOf("item_id" to 42))
    .createPendingIntent()

// ✅ Handling incoming Intent in Activity when using Navigation Component
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    val navController = findNavController(R.id.nav_host_fragment)
    intent?.data?.let { uri ->
        // If the deep link wasn't handled automatically (e.g., custom logic), navigate explicitly
        if (!navController.handleDeepLink(intent)) {
            navController.navigate(uri)
        }
    }
}
```

**Manifest**:
```xml
<!-- ✅ App Link with domain verification -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https"
          android:host="example.com"
          android:pathPrefix="/detail" />
</intent-filter>
```

**When to use**: external transitions from notifications, email, web pages, dynamic links, universal links. Navigation Component can automatically handle deep links mapped in the graph.

### 6. Navigation in Jetpack Compose with NavHost and NavController

Compose-native navigation for fully declarative UIs.

```kotlin
// ✅ Setting up navigation graph in Compose
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onNavigateToDetail = { itemId ->
                // For simple ids this is fine; for strings/complex data prefer arguments/encoding
                navController.navigate("detail/$itemId")
            })
        }

        composable(
            route = "detail/{itemId}",
            arguments = listOf(navArgument("itemId") { type = NavType.IntType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId") ?: 0
            DetailScreen(itemId = itemId)
        }
    }
}

// ✅ Passing complex objects via ViewModel or repository/shared ViewModel
@Composable
fun DetailScreen(
    itemId: Int,
    viewModel: DetailViewModel = hiltViewModel()
) {
    LaunchedEffect(itemId) {
        viewModel.loadItem(itemId)
    }
    // UI
}
```

**When to use**: fully Compose-based apps, declarative navigation, tight integration with Compose state management and the Navigation Component ecosystem.

### 7. Navigation Drawer

Side menu for accessing additional app sections.

```kotlin
// ✅ Drawer with Navigation Component
val navController = findNavController(R.id.nav_host_fragment)
binding.navView.setupWithNavController(navController)

binding.drawerLayout.addDrawerListener(
    ActionBarDrawerToggle(
        this,
        binding.drawerLayout,
        binding.toolbar,
        R.string.navigation_drawer_open,
        R.string.navigation_drawer_close
    )
)
```

**When to use**: secondary sections, settings, user profile, additional features (commonly when you have many sections, e.g., 6+).

---

## Follow-ups

- How does Navigation Component handle configuration changes and process death?
- What are the trade-offs between single-activity vs multi-activity architecture?
- How to implement nested navigation graphs with Navigation Component?
- What's the difference between Deep Links and App Links?
- How to share ViewModels between fragments when using Navigation Component?
- How to implement conditional navigation based on user state?
- What are best practices for animation and transitions between screens?

## References

- [[c-activity-lifecycle]]
- [[c-compose-navigation]]
- [Navigation](https://developer.android.com/guide/navigation)
- https://developer.android.com/guide/navigation/navigation-deep-link

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-intent--android--easy]] - Understanding `Intent` basics
- [[q-fragment-basics--android--easy]] - `Fragment` fundamentals
- [[q-main-android-components--android--easy]] - Android component overview
- [[q-android-app-components--android--easy]] - Core app component types

### Related (Same Level)
- [[q-navigation-methods-android--android--medium]] - Alternative navigation patterns
- [[q-deep-link-vs-app-link--android--medium]] - Deep linking strategies
- [[q-single-activity-approach--android--medium]] - Single activity architecture
- [[q-compose-navigation-advanced--android--medium]] - Advanced Compose navigation

### Advanced (Harder)
- [[q-shared-element-transitions--android--hard]] - Advanced transitions between screens
- [[q-modularization-patterns--android--hard]] - Multi-module navigation patterns
- [[q-how-to-create-dynamic-screens-at-runtime--android--hard]] - Dynamic screen creation
