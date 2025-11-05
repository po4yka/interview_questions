---
id: android-114
title: "Navigation Methods Android / Методы навигации Android"
aliases: ["Navigation Methods Android", "Методы навигации Android"]
topic: android
subtopics: [ui-compose, ui-navigation]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-31
sources: []
tags: [android, android/ui-compose, android/ui-navigation, architecture, compose, difficulty/medium, navigation]
moc: moc-android
related: []
date created: Tuesday, October 28th 2025, 9:51:01 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)

> Какие способы навигации знаешь в Android?

# Question (EN)

> What navigation methods do you know in Android?

---

## Ответ (RU)

Android предоставляет несколько подходов к навигации между экранами:

**1. Activity Navigation (Intent)** - традиционный способ через Intent для перехода между Activity.

**2. Fragment Navigation (FragmentManager)** - управление фрагментами внутри одной Activity.

**3. Navigation Component (Jetpack)** - декларативная навигация с визуальным графом и type-safe аргументами.

**4. Bottom/Tab Navigation** - быстрый доступ к top-level секциям через BottomNavigationView или TabLayout.

**5. Drawer Navigation** - боковое меню для множества направлений навигации.

**6. Deep Links/App Links** - навигация по URI, внешняя интеграция.

**7. Compose Navigation** - навигация в Jetpack Compose через NavHost.

### 1. Activity Navigation

Переход между Activity через Intent:

```kotlin
// Простой переход
startActivity(Intent(this, DetailActivity::class.java))

// С данными
val intent = Intent(this, DetailActivity::class.java).apply {
    putExtra("USER_ID", userId)
}
startActivity(intent)

// ✅ Современный способ получения результата
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("RESULT")
    }
}
```

**Применение**: разные секции приложения, интеграция с внешними приложениями. Не рекомендуется для внутренней навигации.

### 2. Fragment Navigation

Управление фрагментами через FragmentManager:

```kotlin
// Замена фрагмента
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// ✅ С анимацией
supportFragmentManager.beginTransaction()
    .setCustomAnimations(
        R.anim.slide_in_right,
        R.anim.slide_out_left,
        R.anim.slide_in_left,
        R.anim.slide_out_right
    )
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

**Применение**: навигация внутри одной Activity, master-detail layouts, вкладки.

### 3. Navigation Component

Декларативная навигация с навигационным графом:

```kotlin
// Навигация по ID действия
findNavController().navigate(R.id.action_home_to_detail)

// ✅ С типобезопасными аргументами (Safe Args)
val action = HomeFragmentDirections.actionHomeToDetail(itemId = 123)
findNavController().navigate(action)

// Получение аргументов
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val itemId = args.itemId // ✅ Type-safe
    }
}
```

**Преимущества**:
- Визуальный граф навигации
- Type-safe аргументы (Safe Args plugin)
- Автоматическое управление back stack
- Поддержка deep links
- Интеграция с Bottom Navigation и Drawer

### 4. Bottom Navigation

Быстрый доступ к top-level секциям:

```kotlin
// ✅ Автоматическая интеграция с NavController
val navController = findNavController(R.id.nav_host_fragment)
bottomNavigationView.setupWithNavController(navController)
```

**Применение**: 3-5 основных секций приложения с равным приоритетом.

### 5. Drawer Navigation

Боковое меню для множества направлений:

```kotlin
// ✅ Интеграция с Navigation Component
val appBarConfiguration = AppBarConfiguration(
    setOf(R.id.homeFragment, R.id.settingsFragment),
    drawerLayout
)
setupActionBarWithNavController(navController, appBarConfiguration)
```

**Применение**: много направлений навигации, вторичные функции, настройки.

### 6. Deep Links

Навигация по URI:

```kotlin
// В navigation graph
<fragment android:id="@+id/detailFragment">
    <deepLink app:uri="myapp://item/{itemId}" />
</fragment>

// ✅ Программная навигация
val uri = Uri.parse("myapp://item/$itemId")
findNavController().navigate(uri)
```

**Применение**: внешняя навигация (веб, email, уведомления), shareable контент.

### 7. Compose Navigation

Навигация в Compose:

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigate = { itemId ->
                    navController.navigate("detail/$itemId")
                }
            )
        }

        composable(
            route = "detail/{itemId}",
            arguments = listOf(
                navArgument("itemId") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId")
            DetailScreen(
                itemId = itemId,
                onBack = { navController.navigateUp() }
            )
        }
    }
}
```

### Сравнение Подходов

| Метод | Применение | Сложность | Статус |
|-------|-----------|-----------|--------|
| Activity (Intent) | Секции приложения | Низкая | Legacy |
| Fragment (FragmentManager) | Внутренняя навигация | Средняя | Manual |
| Navigation Component | Fragment навигация | Средняя | Recommended |
| Bottom Navigation | Top-level вкладки | Низкая | Common |
| Drawer Navigation | Много направлений | Средняя | Common |
| Deep Links | Внешняя/shareable | Высокая | Modern |
| Compose Navigation | Compose UI | Средняя | Modern |

**Рекомендуемый подход**: Single Activity + Navigation Component для современных приложений, Compose Navigation для Compose-based приложений.

---

## Answer (EN)

Android provides several approaches for navigating between screens:

**1. Activity Navigation (Intent)** - traditional Intent-based navigation between Activities.

**2. Fragment Navigation (FragmentManager)** - managing fragments within a single Activity.

**3. Navigation Component (Jetpack)** - declarative navigation with visual graph and type-safe arguments.

**4. Bottom/Tab Navigation** - quick access to top-level sections via BottomNavigationView or TabLayout.

**5. Drawer Navigation** - side menu for multiple navigation destinations.

**6. Deep Links/App Links** - URI-based navigation, external integration.

**7. Compose Navigation** - navigation in Jetpack Compose via NavHost.

### 1. Activity Navigation

Navigate between Activities using Intent:

```kotlin
// Simple navigation
startActivity(Intent(this, DetailActivity::class.java))

// With data
val intent = Intent(this, DetailActivity::class.java).apply {
    putExtra("USER_ID", userId)
}
startActivity(intent)

// ✅ Modern way to get result
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("RESULT")
    }
}
```

**Use cases**: different app sections, external app integration. Not recommended for in-app navigation.

### 2. Fragment Navigation

Manage fragments via FragmentManager:

```kotlin
// Replace fragment
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// ✅ With animation
supportFragmentManager.beginTransaction()
    .setCustomAnimations(
        R.anim.slide_in_right,
        R.anim.slide_out_left,
        R.anim.slide_in_left,
        R.anim.slide_out_right
    )
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

**Use cases**: in-app navigation within single Activity, master-detail layouts, tabs.

### 3. Navigation Component

Declarative navigation with navigation graph:

```kotlin
// Navigate by action ID
findNavController().navigate(R.id.action_home_to_detail)

// ✅ With type-safe arguments (Safe Args)
val action = HomeFragmentDirections.actionHomeToDetail(itemId = 123)
findNavController().navigate(action)

// Get arguments
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val itemId = args.itemId // ✅ Type-safe
    }
}
```

**Benefits**:
- Visual navigation graph
- Type-safe arguments (Safe Args plugin)
- Automatic back stack management
- Deep link support
- Integration with Bottom Navigation and Drawer

### 4. Bottom Navigation

Quick access to top-level sections:

```kotlin
// ✅ Automatic integration with NavController
val navController = findNavController(R.id.nav_host_fragment)
bottomNavigationView.setupWithNavController(navController)
```

**Use cases**: 3-5 primary app sections with equal priority.

### 5. Drawer Navigation

Side menu for multiple destinations:

```kotlin
// ✅ Integration with Navigation Component
val appBarConfiguration = AppBarConfiguration(
    setOf(R.id.homeFragment, R.id.settingsFragment),
    drawerLayout
)
setupActionBarWithNavController(navController, appBarConfiguration)
```

**Use cases**: many navigation destinations, secondary features, settings.

### 6. Deep Links

URI-based navigation:

```kotlin
// In navigation graph
<fragment android:id="@+id/detailFragment">
    <deepLink app:uri="myapp://item/{itemId}" />
</fragment>

// ✅ Programmatic navigation
val uri = Uri.parse("myapp://item/$itemId")
findNavController().navigate(uri)
```

**Use cases**: external navigation (web, email, notifications), shareable content.

### 7. Compose Navigation

Navigation in Compose:

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigate = { itemId ->
                    navController.navigate("detail/$itemId")
                }
            )
        }

        composable(
            route = "detail/{itemId}",
            arguments = listOf(
                navArgument("itemId") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId")
            DetailScreen(
                itemId = itemId,
                onBack = { navController.navigateUp() }
            )
        }
    }
}
```

### Comparison

| Method | Use Case | Complexity | Status |
|--------|----------|------------|--------|
| Activity (Intent) | App sections | Low | Legacy |
| Fragment (FragmentManager) | In-app navigation | Medium | Manual |
| Navigation Component | Fragment navigation | Medium | Recommended |
| Bottom Navigation | Top-level tabs | Low | Common |
| Drawer Navigation | Many destinations | Medium | Common |
| Deep Links | External/shareable | High | Modern |
| Compose Navigation | Compose UI | Medium | Modern |

**Recommended approach**: Single Activity + Navigation Component for modern apps, Compose Navigation for Compose-based apps.

---

## Follow-ups

- How does Navigation Component handle deep links automatically?
- What are the differences between Activity result API and deprecated onActivityResult?
- How to implement shared element transitions with Navigation Component?
- How to pass complex objects between destinations safely?
- What are the best practices for handling back stack in multi-module apps?
- How does Compose Navigation differ from XML-based Navigation Component?

---

## References

- [[c-android-navigation]] - Navigation patterns
- [[c-fragment-lifecycle]] - Fragment lifecycle management
- [[c-jetpack-compose]] - Compose fundamentals
- [Navigation](https://developer.android.com/guide/navigation)
- https://developer.android.com/jetpack/compose/navigation
---


## Related Questions

### Prerequisites (Easier)
- Related content to be added

### Related (Same Level)
- Related content to be added

### Advanced (Harder)
- Related content to be added
