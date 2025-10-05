---
id: 202510031420
title: What navigation methods in Android do you know / Какие способы навигации в Android знаешь
aliases: []

# Classification
topic: android
subtopics: [android, ui, navigation]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/788
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-navigation
  - c-jetpack-navigation

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [navigation, intent, fragmentmanager, jetpack navigation, bottomnavigationview, tablayout, navhost, difficulty/medium, easy_kotlin, lang/ru, android/navigation, android/ui]
---

# Question (EN)
> What navigation methods in Android do you know

# Вопрос (RU)
> Какие способы навигации в Android знаешь

---

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

В Android есть несколько способов навигации между экранами. Основные методы включают: 1) Activity-навигация через Intent; 2) Fragment-based навигация с использованием FragmentManager; 3) Navigation Component из Jetpack; 4) Bottom/Tab Navigation с BottomNavigationView или TabLayout; 5) Drawer Navigation через Navigation Drawer; 6) Deep Links и App Links для перехода по ссылкам; и 7) Navigation в Jetpack Compose с NavHost и NavController.

---

## Follow-ups
- What are the advantages of Navigation Component over manual fragment management?
- How do you handle complex navigation scenarios with nested graphs?
- What's the best practice for navigation in single-activity apps?

## References
- [[c-android-navigation]]
- [[c-jetpack-navigation]]
- [[c-android-intent]]
- [[moc-android]]

## Related Questions
- [[q-navigation-methods-in-kotlin--android--medium]]
- [[q-how-navigation-is-implemented-in-android--android--medium]]
