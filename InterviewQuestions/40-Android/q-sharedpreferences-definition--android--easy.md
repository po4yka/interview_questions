---
id: android-133
title: "SharedPreferences Definition / Определение SharedPreferences"
aliases: ["SharedPreferences Definition", "Определение SharedPreferences"]
topic: android
subtopics: [datastore]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-components, q-android-components-besides-activity--android--easy, q-how-to-break-text-by-screen-width--android--easy, q-workmanager-return-result--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/datastore, datastore, difficulty/easy, key-value, persistence, sharedpreferences]
---
# Вопрос (RU)

> Что такое SharedPreferences?

# Question (EN)

> What is SharedPreferences?

---

## Ответ (RU)

**SharedPreferences** — это механизм для **хранения и получения простых данных** в формате **пар ключ-значение**.

Это один из **простейших способов** сохранения небольших объёмов данных, таких как настройки пользователя или состояние приложения между сессиями.

> В современных приложениях Google рекомендует использовать **DataStore** как более надёжную и безопасную альтернативу для большинства случаев, но `SharedPreferences` по-прежнему часто встречается и используется.

**Основные характеристики:**

- **Простота использования** — минимальный API
- **Приватность по умолчанию** — данные доступны только внутри приложения (при использовании `MODE_PRIVATE`)
- **Постоянство** — данные сохраняются между запусками приложения
- **Только малые данные** — не для больших наборов данных
- **Идеально для**: настроек пользователя, флагов, несекретных токенов и идентификаторов

**Базовое использование:**

```kotlin
// 1. Получить экземпляр SharedPreferences
val sharedPreferences = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// 2. Записать данные через Editor
sharedPreferences.edit {
    putString("username", "john_doe")
    putInt("user_age", 25)
    putBoolean("is_logged_in", true)
} // Uses apply() under the hood (из androidx.core.content.edit)

// 3. Прочитать данные
val username = sharedPreferences.getString("username", "")  // По умолчанию: ""
val age = sharedPreferences.getInt("user_age", 0)            // По умолчанию: 0
```

**Два способа сохранения через Editor:**

```kotlin
// apply() — не блокирует вызывающий поток, а запись на диск планируется асинхронно
editor.putString("key", "value")
editor.apply()  // Рекомендуется вызывать даже с главного потока

// commit() — синхронно пишет на диск в вызывающем потоке
val success = editor.commit()  // Может блокировать, не вызывайте с главного потока при долгих операциях
```

**Современный подход (Kotlin Extensions из core-ktx):**

```kotlin
// core-ktx предоставляет готовое расширение edit { }
import androidx.core.content.edit

sharedPreferences.edit {
    putString("username", "john")
    putInt("age", 25)
} // Внутри вызывает apply()
```

**Поддерживаемые типы данных:**

```kotlin
editor.putString("name", "John")              // String
editor.putInt("age", 25)                      // Int
editor.putLong("timestamp", 123456789L)       // Long
editor.putFloat("rating", 4.5f)               // Float
editor.putBoolean("enabled", true)            // Boolean
editor.putStringSet("tags", setOf("a", "b")) // Set<String>
```

**Ограничения:**

- Не подходит для больших данных (используйте [[c-room]] или другие механизмы хранения)
- Не подходит для сложных объектов (используйте JSON/сериализацию поверх строк или другие решения)
- Не зашифрован по умолчанию — не храните чувствительные данные (пароли, секретные токены) в обычных `SharedPreferences`
- Не подходит для структурированных/реляционных данных

**Безопасность — EncryptedSharedPreferences:**

```kotlin
// Для чувствительных данных используйте зашифрованное хранилище
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secret_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Тот же API
encryptedPrefs.edit {
    putString("auth_token", "sensitive_token")
}
```

---

## Answer (EN)

**SharedPreferences** is a mechanism for **storing and retrieving simple data** as **key-value pairs**.

It is one of the **simplest ways** to persist small amounts of data, such as user settings or application state between sessions.

> In modern apps, Google recommends using **DataStore** as a more robust and safer alternative for most use cases, but `SharedPreferences` is still widely used and encountered in codebases.

**Key Characteristics:**

- **Simple to use** — minimal API
- **Private by default** — data accessible only within the app (when using `MODE_PRIVATE`)
- **Persistent** — survives app restarts
- **Small data only** — not designed for large datasets
- **Good for**: user preferences, flags, non-sensitive tokens and identifiers

**Basic Usage:**

```kotlin
// 1. Get SharedPreferences instance
val sharedPreferences = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// 2. Write data using Editor
sharedPreferences.edit {
    putString("username", "john_doe")
    putInt("user_age", 25)
    putBoolean("is_logged_in", true)
} // Uses apply() under the hood (from androidx.core.content.edit)

// 3. Read data
val username = sharedPreferences.getString("username", "")  // Default: ""
val age = sharedPreferences.getInt("user_age", 0)            // Default: 0
```

**Two save methods on Editor:**

```kotlin
// apply() — updates in-memory state immediately, schedules disk write asynchronously
editor.putString("key", "value")
editor.apply()  // Recommended; safe to call on the main thread

// commit() — writes to disk synchronously on the calling thread
val success = editor.commit()  // May block; avoid calling on main thread for heavy writes
```

**Modern Approach with Kotlin Extensions (core-ktx):**

```kotlin
// core-ktx provides an edit { } extension for SharedPreferences
import androidx.core.content.edit

sharedPreferences.edit {
    putString("username", "john")
    putInt("age", 25)
} // Internally calls apply()
```

**Supported Data Types:**

```kotlin
editor.putString("name", "John")              // String
editor.putInt("age", 25)                      // Int
editor.putLong("timestamp", 123456789L)       // Long
editor.putFloat("rating", 4.5f)               // Float
editor.putBoolean("enabled", true)            // Boolean
editor.putStringSet("tags", setOf("a", "b")) // Set<String>
```

**Limitations:**

- Not suitable for large data (use [[c-room]] or other storage options)
- Not suitable for complex objects (use JSON/serialization on top of strings or other solutions)
- Not encrypted by default — do not store sensitive data (passwords, secret tokens) in plain `SharedPreferences`
- Not suitable for structured/relational data

**Security — EncryptedSharedPreferences:**

```kotlin
// For sensitive data, use encrypted preferences
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secret_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Same API
encryptedPrefs.edit {
    putString("auth_token", "sensitive_token")
}
```

---

## Дополнительные Вопросы (RU)

- Когда следует использовать `SharedPreferences`, а когда [[c-room]] для хранения данных?
- В чём различия между методами `apply()` и `commit()` в `SharedPreferences`?
- Как выполнить миграцию с `SharedPreferences` на DataStore в современных Android-приложениях?

## Follow-ups

- When should you use `SharedPreferences` vs [[c-room]] for data storage?
- What are the differences between `apply()` and `commit()` methods in `SharedPreferences`?
- How do you migrate from `SharedPreferences` to DataStore for modern Android apps?

## Ссылки (RU)

- [[c-room]]
- https://developer.android.com/training/data-storage/shared-preferences
- https://developer.android.com/topic/security/data

## References

- [[c-room]]
- https://developer.android.com/training/data-storage/shared-preferences
- https://developer.android.com/topic/security/data

## Связанные Вопросы (RU)

### Предпосылки

- [[q-android-components-besides-activity--android--easy]] — Понимание компонентов Android

### Связанные

- [[q-workmanager-return-result--android--medium]] — Фоновая работа и сохранение данных
- [[q-how-to-break-text-by-screen-width--android--easy]] — Управление состоянием UI

### Продвинутые

- Миграция на DataStore (требуется отдельная концептуальная заметка)
- Реализация EncryptedSharedPreferences (продвинутые паттерны безопасности)

## Related Questions

### Prerequisites

- [[q-android-components-besides-activity--android--easy]] — Understanding Android components

### Related

- [[q-workmanager-return-result--android--medium]] — Background work and data persistence
- [[q-how-to-break-text-by-screen-width--android--easy]] — UI state management

### Advanced

- DataStore migration (concept note needed)
- EncryptedSharedPreferences implementation (advanced security patterns)
