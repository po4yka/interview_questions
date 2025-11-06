---
id: android-421
title: How Is Navigation Implemented / Как реализована навигация
aliases:
- Android Navigation
- How Is Navigation Implemented
- Как реализована навигация
- Навигация в Android
topic: android
subtopics:
- fragment
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
- q-navigation-methods-in-kotlin--android--medium
- q-what-is-the-layout-called-where-objects-can-overlay-each-other--android--easy
created: 2025-10-15
updated: 2025-10-28
sources: []
tags:
- android/fragment
- android/ui-navigation
- difficulty/medium
- fragments
- navigation
- navigation-component
- ui
---

# Вопрос (RU)

> Как реализована навигация в Android приложениях?

# Question (EN)

> How is navigation implemented in Android applications?

---

## Ответ (RU)

Навигация в Android — это процесс перехода между экранами (Fragments, Activities) или их частями. Существует несколько подходов к реализации навигации, от традиционных до современных.

### Основные Подходы К Навигации

#### 1. Navigation Component (рекомендуемый подход)

Navigation Component — официальная библиотека от Google для управления навигацией. Предоставляет единый API и визуальный редактор навигационного графа.

```kotlin
// ✅ Переход между фрагментами через NavController
class HomeFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.openDetailsButton.setOnClickListener {
            findNavController().navigate(R.id.action_home_to_detail)
        }
    }
}

// ✅ Передача аргументов через Safe Args
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)
```

Навигационный граф (`nav_graph.xml`) определяет все экраны и переходы:

```xml
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.DetailFragment">
        <argument
            android:name="userId"
            app:argType="string" />
    </fragment>
</navigation>
```

#### 2. Bottom Navigation

Используется для переключения между 3-5 основными разделами приложения:

```kotlin
// ✅ Bottom Navigation с Navigation Component
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val navController = findNavController(R.id.nav_host_fragment)
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        bottomNav.setupWithNavController(navController)
    }
}
```

#### 3. Navigation Drawer

Боковое меню для доступа к дополнительным разделам:

```kotlin
// ✅ Navigation Drawer с Navigation Component
class MainActivity : AppCompatActivity() {
    private lateinit var drawerLayout: DrawerLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val navController = findNavController(R.id.nav_host_fragment)
        drawerLayout = findViewById(R.id.drawer_layout)
        val navView = findViewById<NavigationView>(R.id.nav_view)

        navView.setupWithNavController(navController)
    }
}
```

#### 4. `Fragment` Navigation (традиционный подход)

```kotlin
// ❌ Ручное управление FragmentTransaction (устаревший подход)
supportFragmentManager.beginTransaction()
    .replace(R.id.fragment_container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

### Ключевые Концепции

**Back `Stack`** — стек фрагментов для навигации назад. Navigation Component автоматически управляет back stack.

**Deep Links** — возможность открыть конкретный экран напрямую:

```xml
<fragment android:id="@+id/detailFragment">
    <deepLink
        app:uri="myapp://detail/{itemId}"
        android:autoVerify="true" />
</fragment>
```

**Safe Args** — плагин для типобезопасной передачи аргументов:

```kotlin
// ✅ Генерируемые классы для безопасной передачи параметров
val action = HomeFragmentDirections.actionHomeToDetail(userId = "123")
findNavController().navigate(action)
```

## Answer (EN)

Navigation in Android is the process of moving between screens (Fragments, Activities) or their sections. There are several approaches to implementing navigation, from traditional to modern.

### Main Navigation Approaches

#### 1. Navigation Component (recommended approach)

Navigation Component is the official library from Google for managing navigation. It provides a unified API and visual navigation graph editor.

```kotlin
// ✅ Navigate between fragments using NavController
class HomeFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.openDetailsButton.setOnClickListener {
            findNavController().navigate(R.id.action_home_to_detail)
        }
    }
}

// ✅ Pass arguments with Safe Args
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)
```

Navigation graph (`nav_graph.xml`) defines all screens and transitions:

```xml
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.DetailFragment">
        <argument
            android:name="userId"
            app:argType="string" />
    </fragment>
</navigation>
```

#### 2. Bottom Navigation

Used for switching between 3-5 main app sections:

```kotlin
// ✅ Bottom Navigation with Navigation Component
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val navController = findNavController(R.id.nav_host_fragment)
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        bottomNav.setupWithNavController(navController)
    }
}
```

#### 3. Navigation Drawer

Side menu for accessing additional sections:

```kotlin
// ✅ Navigation Drawer with Navigation Component
class MainActivity : AppCompatActivity() {
    private lateinit var drawerLayout: DrawerLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val navController = findNavController(R.id.nav_host_fragment)
        drawerLayout = findViewById(R.id.drawer_layout)
        val navView = findViewById<NavigationView>(R.id.nav_view)

        navView.setupWithNavController(navController)
    }
}
```

#### 4. `Fragment` Navigation (traditional approach)

```kotlin
// ❌ Manual FragmentTransaction management (deprecated approach)
supportFragmentManager.beginTransaction()
    .replace(R.id.fragment_container, DetailFragment())
    .addToBackStack(null)
    .commit()
```

### Key Concepts

**Back `Stack`** — fragment stack for backward navigation. Navigation Component automatically manages the back stack.

**Deep Links** — ability to open a specific screen directly:

```xml
<fragment android:id="@+id/detailFragment">
    <deepLink
        app:uri="myapp://detail/{itemId}"
        android:autoVerify="true" />
</fragment>
```

**Safe Args** — plugin for type-safe argument passing:

```kotlin
// ✅ Generated classes for safe parameter passing
val action = HomeFragmentDirections.actionHomeToDetail(userId = "123")
findNavController().navigate(action)
```

---

## Follow-ups

- How does Navigation Component handle back stack in nested navigation graphs?
- What are the differences between `popUpTo` and `popUpToInclusive` in navigation actions?
- How to implement conditional navigation based on user authentication state?
- How to migrate from manual `Fragment` transactions to Navigation Component?
- What are the best practices for handling deep links with dynamic parameters?

## References

- [Android Developers: Navigation Component](https://developer.android.com/guide/navigation)
- [Android Developers: Design - Navigation](https://developer.android.com/guide/navigation/navigation-design-graph)
- [Android Developers: Fragments](https://developer.android.com/guide/fragments)
- [Material Design: Navigation](https://material.io/design/navigation)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-fragments]]


### Prerequisites (Easier)
- [[q-what-is-the-layout-called-where-objects-can-overlay-each-other--android--easy]] - Basic UI layout concepts

### Related (Same Level)
- [[q-navigation-methods-in-kotlin--android--medium]] - Different navigation techniques
- [[q-what-navigation-methods-do-you-know--android--medium]] - Navigation patterns overview
- [[q-activity-navigation-how-it-works--android--medium]] - `Activity`-based navigation
- [[q-compose-navigation-advanced--android--medium]] - Navigation in Jetpack Compose

### Advanced (Harder)
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Deep link edge cases
