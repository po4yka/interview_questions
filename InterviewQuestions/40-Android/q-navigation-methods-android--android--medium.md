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
updated: 2025-11-10
sources: []
tags: [android, android/ui-compose, android/ui-navigation, architecture, compose, difficulty/medium, navigation]
moc: moc-android
related: [c-activity, q-navigation-methods-in-android--android--medium]

date created: Saturday, November 1st 2025, 1:25:25 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)

> Какие способы навигации знаешь в Android?

# Question (EN)

> What navigation methods do you know in Android?

---

## Ответ (RU)

Android предоставляет несколько подходов к навигации между экранами:

**1. `Activity` Navigation (`Intent`)** - традиционный способ через `Intent` для перехода между `Activity`.

**2. `Fragment` Navigation (FragmentManager)** - управление фрагментами внутри одной `Activity`.

**3. Navigation Component (Jetpack)** - декларативная навигация с визуальным графом и type-safe аргументами.

**4. Bottom/Tab Navigation** - быстрый доступ к top-level секциям через BottomNavigationView или TabLayout (реализуется через выбранный навигационный механизм, чаще всего Navigation Component).

**5. Drawer Navigation** - боковое меню для множества направлений навигации (обычно поверх Navigation Component / `Fragment` навигации).

**6. Deep Links/App Links** - навигация по URI, внешняя интеграция (часто через Navigation Component).

**7. Compose Navigation** - навигация в Jetpack Compose через NavHost (на базе Navigation Component для Compose).

### 1. `Activity` Navigation

Переход между `Activity` через `Intent`:

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

**Применение**: разные секции/флоу приложения, экраны-энтрипойнты, интеграция с внешними приложениями. Для мелких внутренних переходов внутри одного флоу в современных архитектурах обычно предпочтительнее использовать одну `Activity` с фрагментами или Compose-навигацией.

### 2. `Fragment` Navigation

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

**Применение**: навигация внутри одной `Activity`, master-detail layouts, вкладки. Требует ручного управления back stack и состоянием.

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
- Управление back stack для распространённых сценариев навигации
- Поддержка deep links
- Интеграция с Bottom Navigation и Drawer

### 4. Bottom Navigation

Быстрый доступ к top-level секциям:

```kotlin
// ✅ Интеграция с NavController
val navController = findNavController(R.id.nav_host_fragment)
bottomNavigationView.setupWithNavController(navController)
```

**Применение**: 3-5 основных секций приложения с равным приоритетом. Используется в связке с NavController (Navigation Component) или вручную через переключение фрагментов.

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

**Применение**: много направлений навигации, вторичные функции, настройки. Обычно комбинируется с Navigation Component или `Fragment` навигацией.

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

**Применение**: внешняя навигация (веб, email, уведомления), shareable контент, прямой переход к экрану/состоянию внутри приложения.

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
| `Activity` (`Intent`) | Отдельные флоу/секции, энтрипойнты | Низкая | Legacy для мелкой навигации, актуален для крупных флоу |
| `Fragment` (FragmentManager) | Внутренняя навигация | Средняя | Manual |
| Navigation Component | Навигация между фрагментами/дестинациями | Средняя | Recommended |
| Bottom Navigation | Top-level вкладки (поверх NavController/фрагментов) | Низкая | Common |
| Drawer Navigation | Много направлений (поверх NavController/фрагментов) | Средняя | Common |
| Deep Links | Внешняя/shareable навигация (URI/App Links) | Средняя–Высокая | Modern |
| Compose Navigation | Compose UI (Navigation Component for Compose) | Средняя | Modern |

**Рекомендуемый подход**: Single `Activity` + Navigation Component для современных приложений на `View`/`Fragment`-стеке; Navigation Component for Compose (Compose Navigation) для Compose-based приложений.

---

## Answer (EN)

Android provides several approaches for navigating between screens:

**1. `Activity` Navigation (`Intent`)** - traditional `Intent`-based navigation between Activities.

**2. `Fragment` Navigation (FragmentManager)** - managing fragments within a single `Activity`.

**3. Navigation Component (Jetpack)** - declarative navigation with visual graph and type-safe arguments.

**4. Bottom/Tab Navigation** - quick access to top-level sections via BottomNavigationView or TabLayout (implemented on top of a chosen navigation mechanism, most commonly Navigation Component).

**5. Drawer Navigation** - side menu for multiple destinations (typically built on top of Navigation Component / `Fragment` navigation).

**6. Deep Links/App Links** - URI-based navigation, external integration (often via Navigation Component).

**7. Compose Navigation** - navigation in Jetpack Compose via NavHost (based on the Navigation Component for Compose).

### 1. `Activity` Navigation

Navigate between Activities using `Intent`:

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

**Use cases**: separate app flows/sections, entry-point screens, integration with other apps. For fine-grained in-flow navigation in modern architectures, a Single-`Activity` approach with fragments or Compose navigation is usually preferred.

### 2. `Fragment` Navigation

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

**Use cases**: in-app navigation within a single `Activity`, master-detail layouts, tabs. Requires manual back stack and state management.

### 3. Navigation Component

Declarative navigation with a navigation graph:

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
- Back stack handling for common navigation scenarios
- Deep link support
- Integration with Bottom Navigation and Drawer

### 4. Bottom Navigation

Quick access to top-level sections:

```kotlin
// ✅ Integration with NavController
val navController = findNavController(R.id.nav_host_fragment)
bottomNavigationView.setupWithNavController(navController)
```

**Use cases**: 3-5 primary app sections with equal priority. Typically used with NavController (Navigation Component) or by manually switching fragments.

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

**Use cases**: many navigation destinations, secondary features, settings. Commonly combined with Navigation Component or `Fragment` navigation.

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

**Use cases**: external navigation (web, email, notifications), shareable content, direct entry to specific screens/states.

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
| `Activity` (`Intent`) | Separate flows/sections, entry points | Low | Legacy for fine-grained navigation, valid for major flows |
| `Fragment` (FragmentManager) | In-app navigation | Medium | Manual |
| Navigation Component | Navigation between fragments/destinations | Medium | Recommended |
| Bottom Navigation | Top-level tabs (on top of NavController/fragments) | Low | Common |
| Drawer Navigation | Many destinations (on top of NavController/fragments) | Medium | Common |
| Deep Links | External/shareable navigation (URI/App Links) | Medium–High | Modern |
| Compose Navigation | Compose UI (Navigation Component for Compose) | Medium | Modern |

**Recommended approach**: Single-`Activity` + Navigation Component for modern `View`/`Fragment`-based apps; Navigation Component for Compose (Compose Navigation) for Compose-based apps.

---

## Дополнительные Вопросы (RU)

- Как Navigation Component обрабатывает deep links автоматически?
- В чем разница между API результатов `Activity` и устаревшим `onActivityResult`?
- Как реализовать shared element transitions с использованием Navigation Component?
- Как безопасно передавать сложные объекты между destination?
- Каковы лучшие практики управления back stack в мультимодульных приложениях?
- Чем навигация в Compose отличается от XML-based Navigation Component?

---

## Follow-ups

- How does Navigation Component handle deep links automatically?
- What are the differences between `Activity` result API and deprecated `onActivityResult`?
- How to implement shared element transitions with Navigation Component?
- How to pass complex objects between destinations safely?
- What are the best practices for handling back stack in multi-module apps?
- How does Compose Navigation differ from XML-based Navigation Component?

---

## Ссылки (RU)

- [Navigation](https://developer.android.com/guide/navigation)
- https://developer.android.com/jetpack/compose/navigation

---

## References

- [Navigation](https://developer.android.com/guide/navigation)
- https://developer.android.com/jetpack/compose/navigation

---

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-what-is-intent--android--easy]] - основы `Intent`
- [[q-fragment-basics--android--easy]] - основы `Fragment`
- [[q-main-android-components--android--easy]] - компоненты Android
- [[q-android-app-components--android--easy]] - типы компонентов приложения

### Связанные (того Же уровня)
- [[q-navigation-methods-in-android--android--medium]] - обзор методов навигации
- [[q-deep-link-vs-app-link--android--medium]] - deep linking
- [[q-single-activity-approach--android--medium]] - паттерн Single `Activity`
- [[q-compose-navigation-advanced--android--medium]] - продвинутая навигация в Compose

### Продвинутое (сложнее)
- [[q-shared-element-transitions--android--hard]] - shared transitions
- [[q-modularization-patterns--android--hard]] - навигация в мультимодульной архитектуре
- [[q-how-to-create-dynamic-screens-at-runtime--android--hard]] - динамические экраны

---

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-intent--android--easy]] - `Intent` basics
- [[q-fragment-basics--android--easy]] - `Fragment` fundamentals
- [[q-main-android-components--android--easy]] - Android components
- [[q-android-app-components--android--easy]] - App component types

### Related (Same Level)
- [[q-navigation-methods-in-android--android--medium]] - Navigation methods overview
- [[q-deep-link-vs-app-link--android--medium]] - Deep linking
- [[q-single-activity-approach--android--medium]] - Single activity pattern
- [[q-compose-navigation-advanced--android--medium]] - Compose navigation

### Advanced (Harder)
- [[q-shared-element-transitions--android--hard]] - Shared transitions
- [[q-modularization-patterns--android--hard]] - Multi-module navigation
- [[q-how-to-create-dynamic-screens-at-runtime--android--hard]] - Dynamic screens
