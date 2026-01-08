---\
id: "20251110-170744"
title: "Parcelable / Parcelable"
aliases: ["Parcelable"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-bundle", "c-serialization", "c-intents", "c-savedinstancestate", "c-android-ipc"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

`Parcelable` is an Android-specific serialization interface that allows objects to be flattened into a `Parcel` so they can be efficiently passed between components (Activities, Fragments, Services) or processes. Unlike generic Java serialization, `Parcelable` is optimized for performance and low overhead in mobile environments. It is commonly used for passing complex data via `Intent` extras, `Bundle`s, and IPC in Android.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

`Parcelable` — это специфичный для Android интерфейс сериализации, который позволяет превращать объекты в `Parcel` для эффективной передачи между компонентами (`Activity`, `Fragment`, `Service`) или между процессами. В отличие от стандартной сериализации Java, `Parcelable` оптимизирован по скорости и потреблению памяти для мобильной среды. Часто используется при передаче сложных данных через `Intent` extras, `Bundle` и механизмы IPC в Android.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- `Parcelable` is defined by implementing the `android.os.Parcelable` interface and overriding `writeToParcel()` and `describeContents()`.
- Requires a public static `CREATOR` field that generates instances from a `Parcel` (used by the Android framework).
- More performant and memory-efficient than `java.io.Serializable`, making it preferred for Android IPC and in-app data passing.
- Commonly used to send custom data classes via `Intent` extras, arguments to Fragments (`setArguments`), and saving/restoring instance state.
- Implementation is manual/boilerplate-heavy (though tools/plugins/Kotlin `@Parcelize` can reduce it), and changes to fields must be reflected in parceling logic.

## Ключевые Моменты (RU)

- `Parcelable` реализуется через интерфейс `android.os.Parcelable` с переопределением методов `writeToParcel()` и `describeContents()`.
- Требует публичного статического поля `CREATOR`, которое создаёт экземпляры объекта из `Parcel` (используется фреймворком Android).
- Более быстрый и экономичный по памяти, чем `java.io.Serializable`, поэтому предпочтителен для IPC и передачи данных внутри Android-приложения.
- Часто применяется для передачи пользовательских классов данных через `Intent` extras, аргументы `Fragment` (`setArguments`) и при сохранении/восстановлении состояния.
- Реализация требует ручного кода (boilerplate); при изменении полей нужно синхронно обновлять логику сериализации, что частично упрощается с помощью инструментов и аннотации Kotlin `@Parcelize`.

## References

- Android Developers - `Parcelable`: https://developer.android.com/reference/android/os/Parcelable
- Android Developers - Parcels and Bundles (Intents and Data Transfer guides)
