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
- c-activity
- c-compose-navigation
- q-activity-navigation-how-it-works--android--medium
- q-compose-navigation-advanced--android--medium
- q-how-is-navigation-implemented--android--medium
- q-navigation-methods-in-android--android--medium
- q-what-navigation-methods-do-you-know--android--medium
- q-what-navigation-methods-exist-in-kotlin--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags:
- android/activity
- android/fragment
- android/ui-navigation
- difficulty/medium
- navigation
- ui
anki_cards:
- slug: android-282-0-en
  language: en
  anki_id: 1768378372994
  synced_at: '2026-01-23T16:45:06.010664'
- slug: android-282-0-ru
  language: ru
  anki_id: 1768378373016
  synced_at: '2026-01-23T16:45:06.011926'
---
# Вопрос (RU)

> Каким образом осуществляется навигация в Android?

# Question (EN)

> How is navigation implemented in Android?

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
// ✅ Пример адаптации UI под жесты (упрощенный пример, не полный рецепт edge-to-edge)
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

Три навигационные кнопки (Назад, Домой, Недавние приложения) остаются поддерживаемым вариантом навигации на многих устройствах.

### Навигация В Приложении

#### 1. `Activity` Navigation

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

#### 2. `Fragment` Navigation

```kotlin
// ✅ FragmentManager
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// ✅ Navigation Component (рекомендуется, внутри Fragment/Activity с NavHost)
findNavController().navigate(R.id.action_home_to_detail)
```

#### 3. Навигационные Паттерны

**Bottom Navigation** — для 3-5 главных разделов:

```kotlin
bottomNav.setOnItemSelectedListener { item ->
    when (item.itemId) {
        R.id.nav_home -> {
            loadFragment(HomeFragment())
            true
        }
        R.id.nav_search -> {
            loadFragment(SearchFragment())
            true
        }
        else -> false
    }
}
```

**Navigation Drawer** — для многочисленных разделов.

**Tabs** — для связанных экранов одного уровня.

#### 4. Predictive Back (Android 13+)

Показ превью предыдущего экрана при жесте назад. Требует включения поддержки в манифесте (`android:enableOnBackInvokedCallback="true"` для соответствующей `Activity`) и корректной обработки обратных вызовов (через `OnBackInvokedCallback` в API 33+ или совместимые API из ActivityX). При включении флага без реализации callback система может выдать предупреждение.

```kotlin
// Пример кастомной анимации прогресса жеста (поддержка совместимости через BackEventCompat)
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

        override fun handleOnBackPressed() {
            // Базовое поведение "назад"
            isEnabled = false
            onBackPressedDispatcher.onBackPressed()
        }
    }
)
```

### Best Practices

1. Уважайте системную навигацию — не блокируйте жесты назад без необходимости.
2. Следуйте соглашениям платформы — используйте знакомые паттерны.
3. Сохраняйте состояние — восстанавливайте навигацию после пересоздания `Activity`.
4. Поддержка deep linking — позволяйте открывать экраны напрямую.
5. Используйте predictive back на Android 13+ — при включении корректной обработки улучшает UX на современных устройствах.

## Answer (EN)

Navigation in Android is implemented at two levels: **system-level** (between apps) and **application-level** (within apps).

### System-Level Navigation

#### Gestures (Android 10+)

Modern devices use gesture navigation:
- Swipe up from bottom — home screen
- Swipe up and hold — recent apps
- Swipe from edges — back navigation

```kotlin
// ✅ Example of adapting UI for gesture navigation (simplified, not a full edge-to-edge recipe)
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

Three navigation buttons (Back, Home, Recent Apps) remain a supported navigation mode on many devices.

### `Application`-Level Navigation

#### 1. `Activity` Navigation

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

#### 2. `Fragment` Navigation

```kotlin
// ✅ FragmentManager approach
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// ✅ Navigation Component (recommended, inside Fragment/Activity hosting NavHost)
findNavController().navigate(R.id.action_home_to_detail)
```

#### 3. Navigation Patterns

**Bottom Navigation** — for 3-5 top-level destinations:

```kotlin
bottomNav.setOnItemSelectedListener { item ->
    when (item.itemId) {
        R.id.nav_home -> {
            loadFragment(HomeFragment())
            true
        }
        R.id.nav_search -> {
            loadFragment(SearchFragment())
            true
        }
        else -> false
    }
}
```

**Navigation Drawer** — for many destinations.

**Tabs** — for related destinations at the same level.

#### 4. Predictive Back (Android 13+)

Shows a preview of the previous screen during the back gesture. Requires enabling support in the manifest (`android:enableOnBackInvokedCallback="true"` for the `Activity`) and implementing proper callbacks (`OnBackInvokedCallback` on API 33+ or compatible ActivityX APIs). If you enable the flag without handling callbacks, the system may emit a warning.

```kotlin
// Example of custom back gesture progress animation (with BackEventCompat for compatibility)
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

        override fun handleOnBackPressed() {
            // Default "back" behavior
            isEnabled = false
            onBackPressedDispatcher.onBackPressed()
        }
    }
)
```

### Best Practices

1. Respect system navigation — don't block back gestures without a strong reason.
2. Follow platform conventions — use familiar patterns.
3. Preserve state — restore navigation after `Activity` recreation.
4. Support deep linking — allow direct screen access.
5. Use predictive back on Android 13+ — when properly implemented, it improves UX on modern devices.

---

## Дополнительные Вопросы (RU)

- Как вы обрабатываете восстановление состояния навигации после убийства процесса?
- В чем различия между флагами `launchMode` и как они влияют на back stack?
- Как бы вы реализовали кастомный back stack для сложной мультимодульной навигации?
- Как Navigation `Component` обрабатывает deep links и передачу аргументов?
- Каковы trade-off'ы между архитектурой с одной `Activity` и несколькими `Activity`?

## Ссылки (RU)

- [Android Navigation Guide](https://developer.android.com/guide/navigation)
- [Gesture Navigation](https://developer.android.com/develop/ui/views/layout/edge-to-edge)
- [Predictive Back](https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-compose-navigation]]
- [[c-activity]]

### Предпосылки

- [[q-what-navigation-methods-do-you-know--android--medium]] — Обзор подходов к навигации

### Связанные

- [[q-activity-navigation-how-it-works--android--medium]] — Детали навигации между `Activity`
- [[q-compose-navigation-advanced--android--medium]] — Навигация в Jetpack Compose
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] — Проблемы с deep linking

### Продвинутое

- Архитектура навигации в мультимодульных приложениях с динамическими фичами
- Кастомные переходы навигации и анимации SharedElement
- Type-safe навигация с проверкой маршрутов на этапе компиляции

## Follow-ups

- How do you handle navigation state restoration after process death?
- What are the differences between `launchMode` flags and how do they affect back stack?
- How would you implement a custom back stack for a complex multi-module navigation?
- How does Navigation `Component` handle deep links and argument passing?
- What are the trade-offs between single-`Activity` architecture and multi-`Activity`?

## References

- [Android Navigation Guide](https://developer.android.com/guide/navigation)
- [Gesture Navigation](https://developer.android.com/develop/ui/views/layout/edge-to-edge)
- [Predictive Back](https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-activity]]

### Prerequisites
- [[q-what-navigation-methods-do-you-know--android--medium]] - Overview of navigation approaches

### Related
- [[q-activity-navigation-how-it-works--android--medium]] - `Activity` navigation details
- [[q-compose-navigation-advanced--android--medium]] - Jetpack Compose navigation
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Deep linking challenges

### Advanced
- Multi-module navigation architecture with dynamic features
- Custom navigation transitions and SharedElement animations
- Type-safe navigation with compile-time route validation
