---
id: 20251012-12271150
title: "Navigation Methods In Android / Методы навигации в Android"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-in-what-cases-might-you-need-to-call-commitallowingstateloss--android--hard, q-what-is-the-difference-between-fragmentmanager-and-fragmenttransaction--android--medium, q-presenter-notify-view--android--medium]
created: 2025-10-15
tags: [android/navigation, android/ui, bottomnavigationview, fragmentmanager, intent, jetpack navigation, navhost, navigation, tablayout, ui, difficulty/medium]
---
# Какие способы навигации в Android знаешь?

**English**: What navigation methods in Android do you know?

## Answer (EN)
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

## Ответ (RU)

Android предоставляет несколько методов навигации:

1. **Навигация между Activity через Intent**
2. **Навигация на основе Fragment с использованием FragmentManager**
3. **Navigation Component из Jetpack**
4. **Bottom/Tab навигация с BottomNavigationView или TabLayout**
5. **Drawer Navigation через Navigation Drawer**
6. **Deep Links и App Links**
7. **Навигация в Jetpack Compose с NavHost и NavController**

### Примеры

```kotlin
// 1. Навигация через Intent
startActivity(Intent(this, DetailActivity::class.java))

// 2. Навигация между Fragment
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


---

## Related Questions

### Related (Medium)
- [[q-compose-navigation-advanced--android--medium]] - Navigation
- [[q-compose-navigation-advanced--android--medium]] - Navigation
- [[q-activity-navigation-how-it-works--android--medium]] - Navigation
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Navigation
- [[q-what-navigation-methods-do-you-know--android--medium]] - Navigation
