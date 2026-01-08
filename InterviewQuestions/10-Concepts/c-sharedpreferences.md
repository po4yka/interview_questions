---\
id: "20251110-184513"
title: "Sharedpreferences / Sharedpreferences"
aliases: ["Sharedpreferences"]
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
related: ["c-datastore", "c-room-library", "c-android-storage-options", "c-scoped-storage", "c-encryption-android"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

`SharedPreferences` is an Android API for storing small amounts of primitive data (key-value pairs) persistently on the device. It is typically used for lightweight configuration, user preferences, flags, and simple state that must survive app restarts. Data is stored in XML files, scoped to the application (or a specific file name), and is read synchronously, making it simple but best suited only for small datasets.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

`SharedPreferences` — это API в Android для постоянного хранения небольших объемов примитивных данных в виде пар ключ-значение. Обычно используется для легковесных настроек, пользовательских предпочтений, флагов и простого состояния, которое должно сохраняться между запусками приложения. Данные хранятся в XML-файлах, привязаны к приложению (или конкретному имени файла) и читаются синхронно, поэтому подходят только для небольших наборов данных.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Simple key-value storage: Supports primitives (boolean, int, long, float), `String`, `String` `Set`; no complex objects without manual serialization.
- Persistence: Values are written to disk and preserved across app restarts and process death until explicitly changed or cleared.
- Access model: Obtained via `getSharedPreferences(name, mode)` or `getPreferences(mode)` in Activities; read operations are synchronous.
- Write strategies: `apply()` writes asynchronously (no return, non-blocking), `commit()` writes synchronously (returns boolean, may block UI thread).
- Best for small data: Not suitable for large data, structured data, or sensitive information; prefer databases, DataStore, or encrypted storage where appropriate.

## Ключевые Моменты (RU)

- Простое key-value хранилище: Поддерживает примитивы (boolean, int, long, float), `String` и `Set`<`String`>; сложные объекты требуют ручной сериализации.
- Устойчивость данных: Значения записываются на диск и сохраняются между перезапусками приложения и убийством процесса, пока явно не изменены или не очищены.
- Модель доступа: Получается через `getSharedPreferences(name, mode)` или `getPreferences(mode)` в `Activity`; операции чтения выполняются синхронно.
- Стратегии записи: `apply()` пишет асинхронно (без результата, не блокирует UI), `commit()` — синхронно (возвращает boolean, может блокировать основной поток).
- Подходит для малых данных: Не предназначен для больших объемов, сложных структур или чувствительных данных; в таких случаях лучше использовать БД, DataStore или зашифрованное хранилище.

## References

- Android Developers: `SharedPreferences` API documentation — https://developer.android.com/reference/android/content/SharedPreferences
- Android Developers Guides: Data and file storage overview — https://developer.android.com/training/data-storage
