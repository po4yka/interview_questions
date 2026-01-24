---
id: android-344
title: Navigation Methods In Kotlin / Методы навигации в Kotlin
aliases:
- Android Navigation
- Navigation Methods
- Методы навигации
topic: android
subtopics:
- architecture-mvvm
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
- c-android-components
- q-activity-navigation-how-it-works--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/architecture-mvvm
- android/ui-navigation
- difficulty/medium
- navigation
anki_cards:
- slug: android-344-0-en
  language: en
  anki_id: 1768398021459
  synced_at: '2026-01-23T16:45:06.183948'
- slug: android-344-0-ru
  language: ru
  anki_id: 1768398021483
  synced_at: '2026-01-23T16:45:06.184732'
---
# Вопрос (RU)

> Какие есть способы навигации в Android-приложениях на Kotlin?

# Question (EN)

> What navigation methods exist in Android applications with Kotlin?

---

## Ответ (RU)

**Основные подходы**:

Android предлагает несколько способов навигации — от традиционных `Intent` до современного Navigation `Component`. Выбор зависит от архитектуры (single-`Activity`/multi-`Activity`), UI-стека (Views/Compose) и требований к глубоким ссылкам и BackStack.

**1. Jetpack Navigation `Component` (Рекомендуемый для фрагментов и многомодульных приложений)**

Современный подход с графом навигации, поддержкой deep link, анимаций и безопасной передачей аргументов (Safe Args для `View`-based UI, `Bundle`/`Parcelable` и др. для Compose destinations):

```kotlin
// ✅ Навигация во Fragment через NavController
class HomeFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val navController = findNavController()

        // Простая навигация
        button.setOnClickListener {
            navController.navigate(R.id.action_home_to_detail)
        }

        // С аргументами через Safe Args
        val action = HomeFragmentDirections.actionHomeToDetail(itemId = 123)
        navController.navigate(action)
    }
}

// Получение аргументов
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val itemId = args.itemId
    }
}
```

**2. `Intent` (Навигация между `Activity` и межприложенческая навигация)**

Явные и неявные `Intent` используются как для перехода между `Activity` внутри приложения, так и для вызова других приложений/системных действий.

```kotlin
// ✅ Явный Intent (между Activity внутри приложения)
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("ITEM_ID", 123)
startActivity(intent)

// Получение данных
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val itemId = intent.getIntExtra("ITEM_ID", 0)
    }
}

// ❌ Неявный Intent без проверки
val viewIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://example.com"))
startActivity(viewIntent) // Может упасть, если нет подходящего обработчика

// ✅ С проверкой
if (viewIntent.resolveActivity(packageManager) != null) {
    startActivity(viewIntent)
}
```

**3. FragmentTransaction (Ручное управление фрагментами)**

Используется при навигации внутри одной `Activity` без Navigation `Component`. Вызов `supportFragmentManager` выполняется из `AppCompatActivity`, из фрагмента — через `requireActivity().supportFragmentManager`.

```kotlin
// ✅ Корректная замена с добавлением в BackStack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// ❌ Без addToBackStack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .commit() // Кнопка Back не вернет на предыдущий экран
```

**Кратко про выбор**:
- Navigation `Component` — предпочтителен для новых проектов, сложной навигации, deep links, single-`Activity` архитектуры, но может быть внедрён и постепенно.
- `Intent` — базовый механизм для перехода между `Activity` (как внутри приложения, так и между приложениями).
- Ручные `FragmentTransaction` — уместны для простых сценариев или легаси-кода, но требуют ручного управления BackStack.

---

## Answer (EN)

**Key Approaches**:

Android provides several navigation methods — from traditional Intents to the modern Navigation `Component`. The choice depends on architecture (single-`Activity` vs multi-`Activity`), UI stack (Views/Compose), and deep-link/back stack requirements.

**1. Jetpack Navigation `Component` (Recommended for fragments and modular apps)**

Modern approach with a navigation graph, deep link support, animations, and type-safe arguments (Safe Args for `View`-based UI, `Bundle`/`Parcelable` etc. for Compose destinations):

```kotlin
// ✅ Navigate inside a Fragment via NavController
class HomeFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val navController = findNavController()

        // Simple navigation
        button.setOnClickListener {
            navController.navigate(R.id.action_home_to_detail)
        }

        // With Safe Args
        val action = HomeFragmentDirections.actionHomeToDetail(itemId = 123)
        navController.navigate(action)
    }
}

// Receiving arguments
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val itemId = args.itemId
    }
}
```

**2. `Intent` (`Activity` navigation and inter-app communication)**

Explicit and implicit Intents are used both for navigation between Activities within your app and for launching external apps/system actions.

```kotlin
// ✅ Explicit Intent (between Activities in the same app)
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("ITEM_ID", 123)
startActivity(intent)

// Receiving data
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val itemId = intent.getIntExtra("ITEM_ID", 0)
    }
}

// ❌ Implicit Intent without checking
val viewIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://example.com"))
startActivity(viewIntent) // May crash if no matching handler

// ✅ With check
if (viewIntent.resolveActivity(packageManager) != null) {
    startActivity(viewIntent)
}
```

**3. FragmentTransaction (Manual fragment management)**

Used for navigation inside a single `Activity` without Navigation `Component`. `supportFragmentManager` is called from an AppCompatActivity; from a `Fragment` you would use `requireActivity().supportFragmentManager`.

```kotlin
// ✅ Correct replacement with BackStack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// ❌ Without addToBackStack
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .commit() // Back button won't return to previous screen
```

**Summary of choices**:
- Navigation `Component`: preferred for new projects, complex navigation graphs, deep links, and single-`Activity` setups; can be adopted incrementally.
- Intents: fundamental mechanism for `Activity`-to-`Activity` navigation (both intra-app and inter-app).
- Manual FragmentTransactions: fine for simple or legacy flows but require manual back stack management.

---

## Дополнительные Вопросы (RU)

- Как обрабатывать deep links с помощью Navigation `Component`?
- В чем разница между `popBackStack()` и `popUpTo`?
- Как безопасно передавать сложные объекты между фрагментами?
- Когда лучше использовать архитектуру с одной `Activity` против нескольких `Activity`?
- Как тестировать навигационные потоки?

## Follow-ups

- How to handle deep links with Navigation `Component`?
- What are the differences between `popBackStack()` and `popUpTo`?
- How to pass complex objects between fragments safely?
- When to use single `Activity` architecture vs multiple Activities?
- How to test navigation flows?

---

## Ссылки (RU)

- [[c-android-components]]
- [[c-compose-navigation]]

## References

- [[c-android-components]]
- [[c-compose-navigation]]

---

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-how-does-activity-lifecycle-work--android--medium]] - Базовые сведения о жизненном цикле `Activity`

### Связанные (того Же уровня)
- [[q-activity-navigation-how-it-works--android--medium]] - Детали навигации между `Activity`
- [[q-compose-navigation-advanced--android--medium]] - Паттерны навигации в Compose
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Обработка deep link

### Продвинутые (сложнее)
- [[q-cache-implementation-strategies--android--medium]] - Управление состоянием при навигации

## Related Questions

### Prerequisites (Easier)
- [[q-how-does-activity-lifecycle-work--android--medium]] - `Activity` lifecycle basics

### Related (Same Level)
- [[q-activity-navigation-how-it-works--android--medium]] - `Activity` navigation details
- [[q-compose-navigation-advanced--android--medium]] - Compose navigation patterns
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Deep link handling

### Advanced (Harder)
- [[q-cache-implementation-strategies--android--medium]] - State management across navigation
