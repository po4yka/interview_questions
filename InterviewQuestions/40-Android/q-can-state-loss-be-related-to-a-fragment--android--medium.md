---
id: 20251012-122791
title: Can Fragment State Loss Occur? / Бывает ли потеря состояния у Fragment
aliases: [Can Fragment State Loss Occur, Бывает ли потеря состояния у Fragment]
topic: android
subtopics: [fragment, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, c-viewmodel, c-memory-leaks]
sources: []
created: 2025-10-15
updated: 2025-01-27
tags: [android/fragment, android/lifecycle, difficulty/medium]
---
# Вопрос (RU)
> Бывает ли потеря состояния у Fragment?

# Question (EN)
> Can Fragment State Loss Occur?

---

## Ответ (RU)

**Определение потери состояния**
Потеря состояния фрагмента происходит, когда `FragmentTransaction` выполняется после вызова `onSaveInstanceState()` у Activity. Такая транзакция может быть отброшена при пересоздании процесса, и изменения UI теряются.

**Основные причины**
- Транзакции после сохранения состояния (async коллбэки, фоновые результаты)
- Смерть процесса без персистентного хранения данных
- Пересоздание фрагментов при pop из back stack (эфемерные поля не восстанавливаются)
- Пересоздание Activity (configuration change) без сохранения UI-состояния

**Защита от потери состояния**

```kotlin
// ✅ Безопасная транзакция
lifecycleScope.launchWhenResumed {
  if (!supportFragmentManager.isStateSaved) {
    supportFragmentManager.beginTransaction()
      .replace(R.id.container, MyFragment())
      .commit()
  }
}

// ❌ Небезопасно - может привести к IllegalStateException
supportFragmentManager.beginTransaction()
  .replace(R.id.container, MyFragment())
  .commit()  // после onSaveInstanceState
```

**Best Practices**
- [[c-viewmodel]] для данных, переживающих configuration changes
- `onSaveInstanceState` для временного UI-состояния (scroll position, selections)
- `viewLifecycleOwner` для подписок и очистки view-ссылок в `onDestroyView`
- `commitAllowingStateLoss()` только для некритичных UI (transient dialogs)

## Answer (EN)

**State Loss Definition**
Fragment state loss occurs when a `FragmentTransaction` is executed after the host Activity's `onSaveInstanceState()` has been called. Such transactions may be dropped on process recreation, causing UI changes to be lost.

**Common Causes**
- Transactions after state is saved (async callbacks, background results)
- Process death without persistent storage
- Back stack pop recreates Fragments (ephemeral fields not restored)
- Activity recreation (configuration change) without saving/restoring UI state

**Preventing State Loss**

```kotlin
// ✅ Safe transaction
lifecycleScope.launchWhenResumed {
  if (!supportFragmentManager.isStateSaved) {
    supportFragmentManager.beginTransaction()
      .replace(R.id.container, MyFragment())
      .commit()
  }
}

// ❌ Unsafe - may throw IllegalStateException
supportFragmentManager.beginTransaction()
  .replace(R.id.container, MyFragment())
  .commit()  // after onSaveInstanceState
```

**Best Practices**
- Use [[c-viewmodel]] for data surviving configuration changes
- Use `onSaveInstanceState` for transient UI state (scroll position, selections)
- Use `viewLifecycleOwner` for observations and clear view references in `onDestroyView`
- Use `commitAllowingStateLoss()` only for non-critical UI (transient dialogs)

## Follow-ups
- How does `isStateSaved()` work internally and when exactly does it return true?
- What's the difference between `commit()`, `commitNow()`, and `commitAllowingStateLoss()` in terms of state safety?
- How does Navigation Component prevent state loss during fragment transitions?
- When should data live in ViewModel vs savedInstanceState vs Room/DataStore?

## References
- [[c-viewmodel]]
- [[c-memory-leaks]]
- https://developer.android.com/guide/fragments/lifecycle
- https://developer.android.com/guide/fragments/transactions

## Related Questions

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]]

### Related
- Questions about Fragment lifecycle and state management

### Advanced
- Questions about advanced FragmentManager usage and Navigation Component
