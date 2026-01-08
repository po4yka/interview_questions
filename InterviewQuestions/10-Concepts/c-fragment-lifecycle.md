---\
id: "20260108-110550"
title: "Fragment Lifecycle / Жизненный цикл Fragment"
aliases: ["Fragment Lifecycle", "Жизненный цикл Fragment"]
summary: "Understanding the lifecycle of Android Fragments and their relationship with Activity lifecycle"
topic: "android"
subtopics: ["fragment", "lifecycle"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-11-06"
updated: "2025-11-06"
tags: ["android", "concept", "fragment", "lifecycle", "difficulty/medium"]
---\

# Summary (EN)

The `Fragment` lifecycle is a series of states and callbacks that a `Fragment` goes through from creation to destruction. Fragments have their own lifecycle that is closely tied to their host `Activity`'s lifecycle, but with additional states for view creation and destruction.

Key lifecycle methods:
- `onCreate()` - `Fragment` instance created
- `onCreateView()` - Inflate and return the fragment's view
- `onViewCreated()` - `View` hierarchy created
- `onStart()` - `Fragment` visible
- `onResume()` - `Fragment` interactive
- `onPause()` - `Fragment` no longer interactive
- `onStop()` - `Fragment` no longer visible
- `onDestroyView()` - `View` hierarchy destroyed
- `onDestroy()` - `Fragment` instance destroyed

# Сводка (RU)

Жизненный цикл `Fragment` — это серия состояний и колбэков, через которые проходит `Fragment` от создания до уничтожения. Фрагменты имеют собственный жизненный цикл, тесно связанный с жизненным циклом `Activity`, но с дополнительными состояниями для создания и уничтожения представления.

Ключевые методы жизненного цикла:
- `onCreate()` - Создан экземпляр `Fragment`
- `onCreateView()` - Инфляция и возврат view фрагмента
- `onViewCreated()` - Иерархия view создана
- `onStart()` - `Fragment` видим
- `onResume()` - `Fragment` интерактивен
- `onPause()` - `Fragment` больше не интерактивен
- `onStop()` - `Fragment` больше не виден
- `onDestroyView()` - Иерархия view уничтожена
- `onDestroy()` - Экземпляр `Fragment` уничтожен

## Use Cases / Trade-offs

**Use Cases**:
- Modular UI components that can be reused across Activities
- Multi-pane layouts for tablets
- Navigation between screens using Navigation `Component`
- ViewPager implementations

**Key Considerations**:
- `Fragment`'s view lifecycle is separate from `Fragment` lifecycle
- Configuration changes can destroy views but not `Fragment` instances
- Must handle view recreation properly in `onCreateView()`
- `Activity` lifecycle affects `Fragment` lifecycle

## References

- [Android Fragments Guide](https://developer.android.com/guide/fragments)
- [Fragment `Lifecycle` Documentation](https://developer.android.com/guide/fragments/lifecycle)
