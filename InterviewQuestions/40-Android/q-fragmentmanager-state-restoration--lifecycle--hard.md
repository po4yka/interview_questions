---
id: android-lc-009
title: FragmentManager State Restoration / Восстановление состояния FragmentManager
aliases: []
topic: android
subtopics:
- lifecycle
- fragment
- state
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-fragment
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/fragment
- difficulty/hard
anki_cards:
- slug: android-lc-009-0-en
  language: en
  anki_id: 1769172261407
  synced_at: '2026-01-23T16:45:05.834902'
- slug: android-lc-009-0-ru
  language: ru
  anki_id: 1769172261432
  synced_at: '2026-01-23T16:45:05.836843'
---
# Question (EN)
> How does FragmentManager restore Fragment state after process death?

# Vopros (RU)
> Как FragmentManager восстанавливает состояние Fragment после смерти процесса?

---

## Answer (EN)

**FragmentManager** automatically saves and restores Fragment state, including back stack, but with important caveats.

**What is saved automatically:**
- Fragment class name and arguments Bundle
- Back stack structure
- Fragment `savedInstanceState` (via `onSaveInstanceState`)
- View hierarchy state (EditText text, scroll position)

**What is NOT saved:**
- Retained Fragments (deprecated pattern)
- ViewModel content (except SavedStateHandle)
- Transaction animations
- Custom Fragment properties

**Restoration flow:**
```
Process killed -> Activity recreated with savedInstanceState
    -> FragmentManager.restoreAllState() called
    -> Fragments recreated via reflection (empty constructor!)
    -> Arguments Bundle restored
    -> Fragment.onCreate(savedInstanceState) called
    -> Back stack recreated
```

**Common crash: missing empty constructor**
```kotlin
// BAD: Will crash on restoration
class MyFragment(private val data: String) : Fragment()

// GOOD: Use arguments Bundle
class MyFragment : Fragment() {
    companion object {
        fun newInstance(data: String) = MyFragment().apply {
            arguments = bundleOf("data" to data)
        }
    }

    private val data: String by lazy {
        requireArguments().getString("data")!!
    }
}
```

**Fragment Factory (alternative):**
```kotlin
class MyFragmentFactory(
    private val dependency: Dependency
) : FragmentFactory() {
    override fun instantiate(classLoader: ClassLoader, className: String): Fragment {
        return when (className) {
            MyFragment::class.java.name -> MyFragment(dependency)
            else -> super.instantiate(classLoader, className)
        }
    }
}

// In Activity.onCreate() BEFORE super.onCreate()
supportFragmentManager.fragmentFactory = MyFragmentFactory(dependency)
```

**setRetainInstance (deprecated):**
```kotlin
// OLD way - DO NOT USE
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    retainInstance = true // Deprecated in API 28
}

// NEW way - use ViewModel
private val viewModel: MyViewModel by viewModels()
```

**Testing restoration:**
```kotlin
// In test
scenario.recreate() // Simulates config change

// Or via Developer Options
// "Don't keep activities" + background app
```

## Otvet (RU)

**FragmentManager** автоматически сохраняет и восстанавливает состояние Fragment, включая back stack, но с важными оговорками.

**Что сохраняется автоматически:**
- Имя класса Fragment и Bundle аргументов
- Структура back stack
- `savedInstanceState` фрагмента (через `onSaveInstanceState`)
- Состояние иерархии View (текст EditText, позиция прокрутки)

**Что НЕ сохраняется:**
- Retained Fragments (устаревший паттерн)
- Содержимое ViewModel (кроме SavedStateHandle)
- Анимации транзакций
- Кастомные свойства Fragment

**Поток восстановления:**
```
Процесс убит -> Activity пересоздана с savedInstanceState
    -> FragmentManager.restoreAllState() вызван
    -> Фрагменты пересозданы через рефлексию (пустой конструктор!)
    -> Bundle аргументов восстановлен
    -> Fragment.onCreate(savedInstanceState) вызван
    -> Back stack воссоздан
```

**Частый краш: отсутствует пустой конструктор**
```kotlin
// ПЛОХО: Упадёт при восстановлении
class MyFragment(private val data: String) : Fragment()

// ХОРОШО: Используйте Bundle аргументов
class MyFragment : Fragment() {
    companion object {
        fun newInstance(data: String) = MyFragment().apply {
            arguments = bundleOf("data" to data)
        }
    }

    private val data: String by lazy {
        requireArguments().getString("data")!!
    }
}
```

**Fragment Factory (альтернатива):**
```kotlin
class MyFragmentFactory(
    private val dependency: Dependency
) : FragmentFactory() {
    override fun instantiate(classLoader: ClassLoader, className: String): Fragment {
        return when (className) {
            MyFragment::class.java.name -> MyFragment(dependency)
            else -> super.instantiate(classLoader, className)
        }
    }
}

// В Activity.onCreate() ДО super.onCreate()
supportFragmentManager.fragmentFactory = MyFragmentFactory(dependency)
```

**setRetainInstance (устарел):**
```kotlin
// СТАРЫЙ способ - НЕ ИСПОЛЬЗУЙТЕ
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    retainInstance = true // Устарел в API 28
}

// НОВЫЙ способ - используйте ViewModel
private val viewModel: MyViewModel by viewModels()
```

**Тестирование восстановления:**
```kotlin
// В тесте
scenario.recreate() // Симулирует изменение конфигурации

// Или через Developer Options
// "Не сохранять действия" + свернуть приложение
```

---

## Follow-ups
- What is FragmentFactory and when to use it?
- How to handle Fragment arguments with Navigation Component?
- What are FragmentResultListener and setFragmentResult?

## References
- [[c-lifecycle]]
- [[c-fragment]]
- [[moc-android]]
