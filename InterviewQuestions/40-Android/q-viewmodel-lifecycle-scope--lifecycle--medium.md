---
id: android-lc-007
title: ViewModel Lifecycle Scope / Жизненный цикл ViewModel
aliases: []
topic: android
subtopics:
- lifecycle
- viewmodel
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-viewmodel
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/viewmodel
- difficulty/medium
anki_cards:
- slug: android-lc-007-0-en
  language: en
  anki_id: 1769172275682
  synced_at: '2026-01-23T16:45:06.102557'
- slug: android-lc-007-0-ru
  language: ru
  anki_id: 1769172275707
  synced_at: '2026-01-23T16:45:06.103618'
---
# Question (EN)
> When is ViewModel created and when is it cleared?

# Vopros (RU)
> Когда создаётся ViewModel и когда она очищается?

---

## Answer (EN)

**ViewModel lifecycle** is tied to its scope (Activity or Fragment), surviving configuration changes but NOT process death.

**Creation:**
- Created on first `ViewModelProvider.get()` or `by viewModels()` call
- Stored in `ViewModelStore` associated with the scope

**When ViewModel SURVIVES:**
- Configuration changes (rotation, locale change)
- Fragment transactions (replace, add)
- Activity going to background

**When ViewModel is CLEARED (onCleared() called):**
- `finish()` is called on Activity
- User presses back (Activity destroyed)
- Fragment is removed (not replaced on back stack)
- `ViewModelStoreOwner` is destroyed permanently

**Lifecycle flow:**
```
Activity created -> ViewModelStore created
    -> ViewModel requested -> onCreate() equivalent

[Configuration changes - ViewModel survives]

Activity finish() -> ViewModelStore.clear()
    -> onCleared() called on all ViewModels
```

**Scoped ViewModels:**
```kotlin
// Activity-scoped (survives Fragment recreation)
val activityViewModel: SharedViewModel by activityViewModels()

// Fragment-scoped (cleared with Fragment)
val fragmentViewModel: MyViewModel by viewModels()

// NavGraph-scoped (cleared when NavGraph is popped)
val navViewModel: FlowViewModel by navGraphViewModels(R.id.checkout_graph)
```

**Common mistake:**
```kotlin
// BAD: ViewModel cleared on rotation
class MyActivity : AppCompatActivity() {
    // Wrong - creates new instance every time
    val viewModel = MyViewModel()
}

// GOOD: ViewModel survives rotation
class MyActivity : AppCompatActivity() {
    val viewModel: MyViewModel by viewModels()
}
```

**Key insight:** ViewModel outlives the Activity/Fragment instance but NOT the logical session.

## Otvet (RU)

**Жизненный цикл ViewModel** привязан к её области видимости (Activity или Fragment), переживает изменения конфигурации, но НЕ смерть процесса.

**Создание:**
- Создаётся при первом вызове `ViewModelProvider.get()` или `by viewModels()`
- Хранится в `ViewModelStore`, связанном с областью видимости

**Когда ViewModel ВЫЖИВАЕТ:**
- Изменения конфигурации (поворот, смена локали)
- Транзакции фрагментов (replace, add)
- Activity уходит в фон

**Когда ViewModel ОЧИЩАЕТСЯ (вызывается onCleared()):**
- Вызван `finish()` на Activity
- Пользователь нажал назад (Activity уничтожается)
- Fragment удалён (не заменён на back stack)
- `ViewModelStoreOwner` уничтожен окончательно

**Поток жизненного цикла:**
```
Activity создана -> ViewModelStore создан
    -> ViewModel запрошена -> эквивалент onCreate()

[Изменения конфигурации - ViewModel выживает]

Activity finish() -> ViewModelStore.clear()
    -> onCleared() вызван на всех ViewModel
```

**ViewModel с областью видимости:**
```kotlin
// Область Activity (переживает пересоздание Fragment)
val activityViewModel: SharedViewModel by activityViewModels()

// Область Fragment (очищается с Fragment)
val fragmentViewModel: MyViewModel by viewModels()

// Область NavGraph (очищается когда NavGraph снимается со стека)
val navViewModel: FlowViewModel by navGraphViewModels(R.id.checkout_graph)
```

**Частая ошибка:**
```kotlin
// ПЛОХО: ViewModel очищается при повороте
class MyActivity : AppCompatActivity() {
    // Неправильно - создаёт новый экземпляр каждый раз
    val viewModel = MyViewModel()
}

// ХОРОШО: ViewModel переживает поворот
class MyActivity : AppCompatActivity() {
    val viewModel: MyViewModel by viewModels()
}
```

**Ключевое понимание:** ViewModel переживает экземпляр Activity/Fragment, но НЕ логическую сессию.

---

## Follow-ups
- How does ViewModelStore work internally?
- What is the difference between viewModels() and activityViewModels()?
- How to share ViewModel between Fragments?

## References
- [[c-lifecycle]]
- [[c-viewmodel]]
- [[moc-android]]
