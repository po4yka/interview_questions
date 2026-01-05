---
id: "20251110-125202"
title: "Savedinstancestate / Savedinstancestate"
aliases: ["Savedinstancestate"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-savedstate, c-savedstatehandle, c-configuration-changes, c-bundle, c-process-lifecycle]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
---

# Summary (EN)

savedInstanceState (commonly `onSaveInstanceState`/`Bundle` in Android) is the mechanism for persisting an Activity or Fragment's transient UI state so it can be reliably restored after configuration changes (e.g., rotation), process recreation, or lifecycle-driven destruction. It helps prevent data loss and inconsistent UI when the system kills and later recreates components. Understanding when and what to save vs. keep in ViewModel or persistent storage is a frequent Android interview topic.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

savedInstanceState (обычно `onSaveInstanceState`/`Bundle` в Android) — это механизм сохранения временного состояния UI Activity или Fragment для корректного восстановления после смены конфигурации (например, поворот экрана), пересоздания процесса или уничтожения компонента системой. Он предотвращает потерю данных и несогласованное состояние интерфейса при повторном создании экрана. Понимание, что и когда сохранять через savedInstanceState, а что — во ViewModel или постоянном хранилище, является частым вопросом на собеседованиях по Android.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Purpose: Used to store small, transient UI-related data (e.g., scroll position, selected tab, input text) that must survive configuration changes but does not belong in long-term storage.
- Lifecycle hooks: Data is written in `onSaveInstanceState(Bundle outState)` and typically read back in `onCreate(Bundle savedInstanceState)` / `onViewStateRestored(Bundle)` or `onCreateView` for Fragments.
- Data size and type: Intended for lightweight, serializable/Parcelable data; large objects (bitmaps, heavy models, network results) should not be placed here.
- Relation to ViewModel: ViewModel survives configuration changes in-memory, while savedInstanceState survives process death; they are complementary and often used together.
- Common pitfalls: Forgetting to restore, storing too much data, or confusing savedInstanceState with persistent storage (DB/SharedPreferences/files).

## Ключевые Моменты (RU)

- Назначение: Хранит небольшие временные данные UI (позиция списка, выбранная вкладка, введённый текст), которые должны пережить смену конфигурации, но не требуют долгосрочного хранения.
- Жизненный цикл: Данные записываются в `onSaveInstanceState(Bundle outState)` и восстанавливаются в `onCreate(Bundle savedInstanceState)`, `onViewStateRestored(Bundle)` или `onCreateView` для Fragment.
- Размер и тип данных: Предназначен для лёгких Serializable/Parcelable данных; крупные объекты (bitmaps, тяжёлые модели, результаты сети) не рекомендуется сохранять в Bundle.
- Связь с ViewModel: ViewModel переживает смену конфигурации в памяти, а savedInstanceState — пересоздание процесса; обычно используются совместно.
- Частые ошибки: Не восстанавливать сохранённые данные, класть в Bundle слишком много, путать savedInstanceState с постоянным хранилищем (БД/SharedPreferences/файлы).

## References

- Official Android docs: Activity lifecycle and `onSaveInstanceState`: https://developer.android.com/reference/android/app/Activity#onSaveInstanceState(android.os.Bundle)
- Official Android docs: Saving UI States: https://developer.android.com/topic/libraries/architecture/saving-states

