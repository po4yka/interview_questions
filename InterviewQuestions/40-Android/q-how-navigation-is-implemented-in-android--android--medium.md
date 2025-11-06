---
id: android-282
title: How Navigation Is Implemented In Android / Как реализована навигация в Android
aliases:
- How Navigation Is Implemented In Android
- Navigation Implementation
- Как реализована навигация в Android
- Реализация навигации
topic: android
subtopics:
- activity
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
- c-activity
- c-fragments
- q-activity-navigation-how-it-works--android--medium
- q-compose-navigation-advanced--android--medium
- q-what-navigation-methods-do-you-know--android--medium
sources: []
created: 2025-10-15
updated: 2025-10-28
tags:
- android/activity
- android/fragment
- android/ui-navigation
- difficulty/medium
- navigation
- ui
date created: Tuesday, October 28th 2025, 9:35:54 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

Каким образом осуществляется навигация в Android?

# Question (EN)

How is navigation implemented in Android?

---

## Ответ (RU)

Навигация в Android реализуется на двух уровнях: **системном** (между приложениями) и **уровне приложения** (внутри приложения).

### Системная Навигация

#### Жесты (Android 10+)

Современные устройства используют жесты:
- Свайп снизу — возврат на главный экран
- Свайп снизу с задержкой — список недавних приложений
- Свайп от краев — возврат назад

```kotlin
// ✅ Адаптация UI под жесты
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    WindowCompat.setDecorFitsSystemWindows(window, false)

    ViewCompat.setOnApplyWindowInsetsListener(binding.root) { view, insets ->
        val gestureInsets = insets.getInsets(WindowInsetsCompat.Type.systemGestures())
        view.updatePadding(bottom = gestureInsets.bottom)
        insets
    }
}
```

#### Кнопки (Legacy)

Три экранные кнопки: Назад, Домой, Недавние приложения.

### Навигация В Приложении

#### 1. Activity Navigation

```kotlin
// ✅ Базовый переход
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// ✅ Управление задачами
val intent = Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
}
startActivity(intent)
```

#### 2. Fragment Navigation

```kotlin
// ✅ FragmentManager
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// ✅ Navigation Component (рекомендуется)
findNavController().navigate(R.id.action_home_to_detail)
```

#### 3. Навигационные Паттерны

**Bottom Navigation** — для 3-5 главных разделов:

```kotlin
bottomNav.setOnItemSelectedListener { item ->
    when (item.itemId) {
        R.id.nav_home -> loadFragment(HomeFragment())
        R.id.nav_search -> loadFragment(SearchFragment())
        else -> false
    }
}
```

**Navigation Drawer** — для многочисленных разделов.

**Tabs** — для связанных экранов одного уровня.

#### 4. Predictive Back (Android 13+)

Показ превью предыдущего экрана при жесте назад:

```kotlin
onBackPressedDispatcher.addCallback(
    this,
    object : OnBackPressedCallback(true) {
        override fun handleOnBackProgressed(backEvent: BackEventCompat) {
            // Анимация прогресса жеста
            val progress = backEvent.progress
            binding.root.scaleX = 1 - (progress * 0.1f)
        }

        override fun handleOnBackCancelled() {
            // Отмена — возврат к исходному состоянию
            binding.root.animate().scaleX(1f).start()
        }
    }
)
```

### Best Practices

1. **Уважайте системную навигацию** — не блокируйте жесты назад
2. **Следуйте соглашениям платформы** — используйте знакомые паттерны
3. **Сохраняйте состояние** — восстанавливайте навигацию после пересоздания Activity
4. **Поддержка deep linking** — позволяйте открывать экраны напрямую
5. **Реализуйте predictive back** — улучшает UX на современных устройствах

## Answer (EN)

Navigation in Android is implemented at two levels: **system-level** (between apps) and **application-level** (within apps).

### System-Level Navigation

#### Gestures (Android 10+)

Modern devices use gesture navigation:
- Swipe up from bottom — home screen
- Swipe up with hold — recent apps
- Swipe from edges — back navigation

```kotlin
// ✅ Adapt UI for gesture navigation
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    WindowCompat.setDecorFitsSystemWindows(window, false)

    ViewCompat.setOnApplyWindowInsetsListener(binding.root) { view, insets ->
        val gestureInsets = insets.getInsets(WindowInsetsCompat.Type.systemGestures())
        view.updatePadding(bottom = gestureInsets.bottom)
        insets
    }
}
```

#### Button Navigation (Legacy)

Three on-screen buttons: Back, Home, Recent Apps.

### Application-Level Navigation

#### 1. Activity Navigation

```kotlin
// ✅ Basic transition
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// ✅ Task management
val intent = Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
}
startActivity(intent)
```

#### 2. Fragment Navigation

```kotlin
// ✅ FragmentManager approach
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// ✅ Navigation Component (recommended)
findNavController().navigate(R.id.action_home_to_detail)
```

#### 3. Navigation Patterns

**Bottom Navigation** — for 3-5 top-level destinations:

```kotlin
bottomNav.setOnItemSelectedListener { item ->
    when (item.itemId) {
        R.id.nav_home -> loadFragment(HomeFragment())
        R.id.nav_search -> loadFragment(SearchFragment())
        else -> false
    }
}
```

**Navigation Drawer** — for many destinations.

**Tabs** — for related destinations at the same level.

#### 4. Predictive Back (Android 13+)

Shows preview of previous screen during back gesture:

```kotlin
onBackPressedDispatcher.addCallback(
    this,
    object : OnBackPressedCallback(true) {
        override fun handleOnBackProgressed(backEvent: BackEventCompat) {
            // Animate gesture progress
            val progress = backEvent.progress
            binding.root.scaleX = 1 - (progress * 0.1f)
        }

        override fun handleOnBackCancelled() {
            // Cancel — restore original state
            binding.root.animate().scaleX(1f).start()
        }
    }
)
```

### Best Practices

1. **Respect system navigation** — don't block back gestures
2. **Follow platform conventions** — use familiar patterns
3. **Preserve state** — restore navigation after Activity recreation
4. **Support deep linking** — allow direct screen access
5. **Implement predictive back** — improves UX on modern devices

---

## Follow-ups

- How do you handle navigation state restoration after process death?
- What are the differences between `launchMode` flags and how do they affect back stack?
- How would you implement a custom back stack for a complex multi-module navigation?
- How does Navigation Component handle deep links and argument passing?
- What are the trade-offs between single-Activity architecture and multi-Activity?

## References

- [Android Navigation Guide](https://developer.android.com/guide/navigation)
- [Gesture Navigation](https://developer.android.com/develop/ui/views/layout/edge-to-edge)
- [Predictive Back](https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-activity]]
- [[c-fragments]]


### Prerequisites
- [[q-what-navigation-methods-do-you-know--android--medium]] - Overview of navigation approaches

### Related
- [[q-activity-navigation-how-it-works--android--medium]] - Activity navigation details
- [[q-compose-navigation-advanced--android--medium]] - Jetpack Compose navigation
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Deep linking challenges

### Advanced
- Multi-module navigation architecture with dynamic features
- Custom navigation transitions and SharedElement animations
- Type-safe navigation with compile-time route validation
