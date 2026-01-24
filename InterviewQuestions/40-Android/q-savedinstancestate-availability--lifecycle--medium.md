---
id: android-lc-002
title: SavedInstanceState Availability / Доступность SavedInstanceState
aliases: []
topic: android
subtopics:
- lifecycle
- state
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
- c-state
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/state
- difficulty/medium
anki_cards:
- slug: android-lc-002-0-en
  language: en
  anki_id: 1769172299683
  synced_at: '2026-01-23T16:45:06.377914'
- slug: android-lc-002-0-ru
  language: ru
  anki_id: 1769172299707
  synced_at: '2026-01-23T16:45:06.378920'
---
# Question (EN)
> When is SavedInstanceState available and when is it null?

# Vopros (RU)
> Когда SavedInstanceState доступен и когда он null?

---

## Answer (EN)

**SavedInstanceState** is a Bundle passed to `onCreate()` and `onRestoreInstanceState()` containing previously saved UI state.

**When savedInstanceState is NOT null:**
- After configuration change (rotation)
- After process death and user returns
- After being stopped and system kills the Activity

**When savedInstanceState IS null:**
- First launch of Activity
- After `finish()` is called
- User presses back (explicit exit)
- Task is removed from recents

**Key rule:** `onSaveInstanceState()` is called when the system **might** destroy the Activity, not when user explicitly exits.

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    if (savedInstanceState == null) {
        // Fresh start - load initial data
        loadFromNetwork()
    } else {
        // Restoration - recover UI state
        val scrollPos = savedInstanceState.getInt("scroll_pos")
        recyclerView.scrollToPosition(scrollPos)
    }
}

override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // Called AFTER onStop() on API 28+
    // Called BEFORE onStop() on older APIs
    outState.putInt("scroll_pos", getCurrentScrollPosition())
}
```

**Limits and best practices:**
- **Size limit:** ~1MB for entire process (TransactionTooLargeException)
- **Store only:** UI state (scroll position, text input, selections)
- **Don't store:** Large objects, Bitmaps, complex data
- **For large data:** Use ViewModel or local database

## Otvet (RU)

**SavedInstanceState** - Bundle, передаваемый в `onCreate()` и `onRestoreInstanceState()`, содержащий ранее сохранённое UI-состояние.

**Когда savedInstanceState НЕ null:**
- После изменения конфигурации (поворот)
- После смерти процесса и возврата пользователя
- После остановки и уничтожения Activity системой

**Когда savedInstanceState IS null:**
- Первый запуск Activity
- После вызова `finish()`
- Пользователь нажимает назад (явный выход)
- Задача удалена из недавних

**Ключевое правило:** `onSaveInstanceState()` вызывается когда система **может** уничтожить Activity, не когда пользователь явно выходит.

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    if (savedInstanceState == null) {
        // Свежий старт - загрузить начальные данные
        loadFromNetwork()
    } else {
        // Восстановление - восстановить UI-состояние
        val scrollPos = savedInstanceState.getInt("scroll_pos")
        recyclerView.scrollToPosition(scrollPos)
    }
}

override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // Вызывается ПОСЛЕ onStop() на API 28+
    // Вызывается ДО onStop() на старых API
    outState.putInt("scroll_pos", getCurrentScrollPosition())
}
```

**Лимиты и лучшие практики:**
- **Лимит размера:** ~1МБ на весь процесс (TransactionTooLargeException)
- **Сохраняйте только:** UI-состояние (позиция прокрутки, ввод текста, выборки)
- **Не сохраняйте:** Большие объекты, Bitmap, сложные данные
- **Для больших данных:** Используйте ViewModel или локальную БД

---

## Follow-ups
- What causes TransactionTooLargeException?
- How does SavedStateHandle in ViewModel work?
- What is the difference between onSaveInstanceState and onRestoreInstanceState?

## References
- [[c-lifecycle]]
- [[c-state]]
- [[moc-android]]
