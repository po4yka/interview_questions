---
id: android-lc-001
title: Configuration Change Recreation / Пересоздание при изменении конфигурации
aliases: []
topic: android
subtopics:
- lifecycle
- configuration
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
- c-configuration
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/configuration
- difficulty/medium
anki_cards:
- slug: android-lc-001-0-en
  language: en
  anki_id: 1769172283157
  synced_at: '2026-01-23T16:45:06.194381'
- slug: android-lc-001-0-ru
  language: ru
  anki_id: 1769172283182
  synced_at: '2026-01-23T16:45:06.195301'
---
# Question (EN)
> What happens during a configuration change and what gets recreated?

# Vopros (RU)
> Что происходит при изменении конфигурации и что пересоздаётся?

---

## Answer (EN)

**Configuration changes** trigger Activity/Fragment destruction and recreation. Common triggers:
- Screen rotation
- Keyboard appearance/disappearance
- Language change
- Dark/light mode switch
- Screen size change (multi-window)

**What gets destroyed:**
- Activity instance
- Fragment instances
- Views and their state
- Local variables
- Anonymous class references

**What survives:**
- `ViewModel` (survives config changes, cleared on finish)
- `SavedInstanceState` bundle (if saved)
- Application-level singletons
- Static fields (use carefully)

**Recreation flow:**
```
onPause() -> onStop() -> onSaveInstanceState() -> onDestroy()
    -> onCreate(savedInstanceState) -> onStart() -> onResume()
```

**Handling strategies:**

1. **ViewModel** (recommended):
```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
}
// Survives rotation automatically
```

2. **android:configChanges** (avoid if possible):
```xml
<activity android:configChanges="orientation|screenSize">
```
Prevents recreation but you must handle changes manually in `onConfigurationChanged()`.

3. **SavedInstanceState** for UI state:
```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("scroll_position", scrollY)
}
```

## Otvet (RU)

**Изменения конфигурации** запускают уничтожение и пересоздание Activity/Fragment. Частые триггеры:
- Поворот экрана
- Появление/скрытие клавиатуры
- Смена языка
- Переключение тёмной/светлой темы
- Изменение размера экрана (multi-window)

**Что уничтожается:**
- Экземпляр Activity
- Экземпляры Fragment
- View и их состояние
- Локальные переменные
- Ссылки анонимных классов

**Что сохраняется:**
- `ViewModel` (переживает config changes, очищается при finish)
- Bundle `SavedInstanceState` (если сохранён)
- Синглтоны уровня Application
- Статические поля (использовать осторожно)

**Поток пересоздания:**
```
onPause() -> onStop() -> onSaveInstanceState() -> onDestroy()
    -> onCreate(savedInstanceState) -> onStart() -> onResume()
```

**Стратегии обработки:**

1. **ViewModel** (рекомендуется):
```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
}
// Автоматически переживает поворот
```

2. **android:configChanges** (избегать если возможно):
```xml
<activity android:configChanges="orientation|screenSize">
```
Предотвращает пересоздание, но нужно вручную обрабатывать изменения в `onConfigurationChanged()`.

3. **SavedInstanceState** для UI-состояния:
```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("scroll_position", scrollY)
}
```

---

## Follow-ups
- When is onSaveInstanceState NOT called?
- How does ViewModel survive configuration changes?
- What are the size limits of SavedInstanceState?

## References
- [[c-lifecycle]]
- [[c-configuration]]
- [[moc-android]]
