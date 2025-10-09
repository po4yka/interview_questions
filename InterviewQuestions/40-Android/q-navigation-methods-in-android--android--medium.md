---
topic: android
tags:
  - android
  - android/navigation
  - android/ui
  - bottomnavigationview
  - fragmentmanager
  - intent
  - jetpack navigation
  - navhost
  - navigation
  - tablayout
  - ui
difficulty: medium
status: reviewed
---

# Какие способы навигации в Android знаешь?

**English**: What navigation methods in Android do you know?

## Answer

Android provides several navigation methods:

1. **Activity navigation via Intent**
2. **Fragment-based navigation using FragmentManager**
3. **Navigation Component from Jetpack**
4. **Bottom/Tab Navigation with BottomNavigationView or TabLayout**
5. **Drawer Navigation via Navigation Drawer**
6. **Deep Links and App Links**
7. **Navigation in Jetpack Compose with NavHost and NavController**

### Examples

```kotlin
// 1. Intent navigation
startActivity(Intent(this, DetailActivity::class.java))

// 2. Fragment navigation
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// 3. Navigation Component
findNavController().navigate(R.id.action_home_to_detail)

// 4. Bottom Navigation
bottomNav.setOnItemSelectedListener { item ->
    when (item.itemId) {
        R.id.nav_home -> navigateToHome()
        R.id.nav_profile -> navigateToProfile()
        else -> false
    }
}

// 5. Deep Links
val deepLink = NavDeepLinkBuilder(context)
    .setGraph(R.navigation.nav_graph)
    .setDestination(R.id.detailFragment)
    .createPendingIntent()
```

## Ответ

В Android есть несколько способов навигации между экранами. Основные методы включают: 1) Activity-навигация через Intent; 2) Fragment-based навигация с использованием FragmentManager; 3) Navigation Component из Jetpack; 4) Bottom/Tab Navigation с BottomNavigationView или TabLayout; 5) Drawer Navigation через Navigation Drawer; 6) Deep Links и App Links для перехода по ссылкам; и 7) Navigation в Jetpack Compose с NavHost и NavController.

