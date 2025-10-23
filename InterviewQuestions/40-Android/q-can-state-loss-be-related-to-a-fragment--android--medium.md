---
id: 20251012-122791
title: Can Fragment State Loss Occur? / Бывает ли потеря состояния у Fragment
aliases: [Can Fragment State Loss Occur, Бывает ли потеря состояния у Fragment]
topic: android
subtopics: [fragment, lifecycle]
question_kind: android
difficulty: medium
status: reviewed
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-android-app-components--android--easy, q-android-manifest-file--android--easy]
created: 2025-10-15
updated: 2025-10-20
original_language: en
language_tags: [en, ru]
tags: [android/fragment, android/lifecycle, state-management, difficulty/medium]
---# Вопрос (RU)
> Может ли потеря состояния быть связана с Fragment? Когда это происходит и как предотвратить?

---

# Question (EN)
> Can state loss be related to a Fragment? When and how does it happen, and how to prevent it?

## Ответ (RU)

### Что такое «потеря состояния»
- Выполнение FragmentTransaction после сохранения состояния `Activity` (после `onSaveInstanceState`) может быть проигнорировано при восстановлении процесса → изменение UI теряется.
- Состояние View vs состояние экземпляра фрагмента: View может быть уничтожена, пока фрагмент живет (back stack).

### Частые причины
- Транзакции после сохранения состояния (асинхронные колбэки, фоновые результаты).
- Смерть процесса без сохранения нужного состояния.
- Возврат из back stack создает фрагменты заново (эфемерные поля не восстанавливаются).
- Пересоздание `Activity` (смена конфигурации) без сохранения/восстановления UI.

### Профилактика
- Меняйте FragmentManager только когда состояние не сохранено.
- Сохраняйте важное: ViewModel для долговечных данных; `onSaveInstanceState` для UI‑состояния.
- Наблюдайте через `viewLifecycleOwner` и обнуляйте binding в `onDestroyView`.

### Минимальный сниппет (проверка перед транзакцией)
```kotlin
lifecycleScope.launchWhenResumed {
  if (!supportFragmentManager.isStateSaved) {
    supportFragmentManager.beginTransaction()
      .replace(R.id.container, MyFragment())
      .commit()
  }
}
```

### Рекомендации
- ViewModel для данных, переживающих смену конфигурации.
- `onSaveInstanceState` для временного UI (скролл, выделения).
- `commitNow()` только в безопасных точках (например, первый `onCreate` при `savedInstanceState == null`).
- `commitAllowingStateLoss()` — только для некритичного UI (например, диалоги).
- Используйте `viewLifecycleOwner` и очищайте binding в `onDestroyView`.

---

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
- Persist what must survive (ViewModel for data; `onSaveInstanceState` for UI state).
- Observe with `viewLifecycleOwner` and clear view references in `onDestroyView`.

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
- Use ViewModel for durable data across config changes.
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

