---
id: 20251012-122791
title: Can Fragment State Loss Occur? / Бывает ли потеря состояния у Fragment
aliases:
- Can Fragment State Loss Occur
- Бывает ли потеря состояния у Fragment
topic: android
subtopics:
- fragment
- lifecycle
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-activity-lifecycle-methods--android--medium
- q-android-app-components--android--easy
- q-android-manifest-file--android--easy
created: 2025-10-15
updated: 2025-10-20
tags:
- android/fragment
- android/lifecycle
- difficulty/medium
---

# Вопрос (RU)
> Бывает ли потеря состояния у Fragment?

# Question (EN)
> Can Fragment State Loss Occur??

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### What “state loss” means
- Performing a FragmentTransaction after the host `Activity` saved state (after `onSaveInstanceState`) may be dropped on process recreation → UI change is lost.
- View state vs Fragment instance state: the view can be destroyed while the Fragment instance remains (back stack).

### Common causes
- Transactions after state is saved (async callbacks, background results).
- Process death without persisting necessary state.
- Back stack pop recreates Fragments (not restores ephemeral fields).
- Parent `Activity` recreation (configuration change) without persisting/restoring UI state.

### Prevention
- Only mutate FragmentManager when state is not saved.
- Persist what must survive ([[c-viewmodel]] for data; `onSaveInstanceState` for UI state).
- Observe with `viewLifecycleOwner` and clear view references in `onDestroyView` to avoid [[c-memory-leaks]].

### Minimal snippet (guarding transactions)
```kotlin
lifecycleScope.launchWhenResumed {
  if (!supportFragmentManager.isStateSaved) {
    supportFragmentManager.beginTransaction()
      .replace(R.id.container, MyFragment())
      .commit()
  }
}
```

### Best practices
- Use [[c-viewmodel]] for durable data across config changes.
- Use `onSaveInstanceState` for transient UI (scroll, selections).
- Prefer `commitNow()` only in safe points (e.g., initial `onCreate` when `savedInstanceState == null`).
- Avoid `commitAllowingStateLoss()` except for non-critical UI where loss is acceptable (e.g., transient dialogs).
- Use `viewLifecycleOwner` for observing and null view bindings in `onDestroyView`.

## Follow-ups
- How to test process death and state restoration reliably?
- What should live in ViewModel vs savedInstanceState vs persistent storage?
- How does Navigation component help avoid unsafe transactions?

## References
- https://developer.android.com/guide/fragments/lifecycle
- https://developer.android.com/guide/fragments/transactions

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Related (Same Level)
- [[q-activity-lifecycle-methods--android--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
