---
id: android-133
title: "Sharedpreferences Definition / Определение SharedPreferences"
aliases: ["Sharedpreferences Definition", "Определение SharedPreferences"]
topic: android
subtopics: [datastore]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-components-besides-activity--android--easy, q-how-to-break-text-by-screen-width--android--easy, q-workmanager-return-result--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/datastore, data-storage, difficulty/easy, key-value, persistence, sharedpreferences]
---

# Вопрос (RU)

> Что такое SharedPreferences?

# Question (EN)

> What is SharedPreferences?

---

## Ответ (RU)

**SharedPreferences** — это механизм для **хранения и получения простых данных** в формате **пар ключ-значение**.

Это один из **простейших способов** сохранения небольших объёмов данных, таких как настройки пользователя или состояние приложения между сессиями.

**Основные характеристики:**

- **Простота использования** — минимальный API
- **Приватность по умолчанию** — данные доступны только внутри приложения
- **Постоянство** — переживает перезапуск приложения
- **Только малые данные** — не для больших наборов данных
- **Идеально для**: настроек пользователя, флагов, токенов

**Базовое использование:**

```kotlin
// 1. Получить экземпляр SharedPreferences
val sharedPreferences = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// 2. Записать данные через Editor
sharedPreferences.edit {
    putString("username", "john_doe")  // ✅ Используем apply() неявно
    putInt("user_age", 25)
    putBoolean("is_logged_in", true)
}

// 3. Прочитать данные
val username = sharedPreferences.getString("username", "")  // По умолчанию: ""
val age = sharedPreferences.getInt("user_age", 0)         // По умолчанию: 0
```

**Два метода сохранения:**

```kotlin
// apply() — Асинхронный (рекомендуется)
editor.putString("key", "value")
editor.apply()  // ✅ Не блокирует UI

// commit() — Синхронный
val success = editor.commit()  // ❌ Блокирует UI, возвращает boolean
```

**Современный подход с Kotlin Extensions:**

```kotlin
// Extension функция
fun SharedPreferences.edit(action: SharedPreferences.Editor.() -> Unit) {
    val editor = edit()
    editor.action()
    editor.apply()  // ✅ Всегда асинхронно
}

// Использование
sharedPreferences.edit {
    putString("username", "john")
    putInt("age", 25)
}
```

**Поддерживаемые типы данных:**

```kotlin
editor.putString("name", "John")           // String
editor.putInt("age", 25)                   // Int
editor.putLong("timestamp", 123456789L)    // Long
editor.putFloat("rating", 4.5f)            // Float
editor.putBoolean("enabled", true)         // Boolean
editor.putStringSet("tags", setOf("a", "b"))  // Set<String>
```

**Ограничения:**

- Не подходит для больших данных (используйте [[c-room]])
- Не подходит для сложных объектов (используйте JSON или сериализацию)
- Не зашифрован по умолчанию (используйте EncryptedSharedPreferences для чувствительных данных)
- Не подходит для структурированных/реляционных данных

**Безопасность — EncryptedSharedPreferences:**

```kotlin
// Для чувствительных данных
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

// ✅ Используем тот же API
encryptedPrefs.edit {
    putString("auth_token", "sensitive_token")
}
```

---

## Answer (EN)

**SharedPreferences** is a mechanism for **storing and retrieving simple data** in the form of **key-value pairs**.

It's one of the **simplest ways** to save small amounts of data, such as user settings or application state between sessions.

**Key Characteristics:**

- **Simple to use** — minimal API
- **Private by default** — data accessible only within the app
- **Persistent** — survives app restarts
- **Small data only** — not for large datasets
- **Perfect for**: User preferences, settings, flags, tokens

**Basic Usage:**

```kotlin
// 1. Get SharedPreferences instance
val sharedPreferences = context.getSharedPreferences("MyPrefs", Context.MODE_PRIVATE)

// 2. Write data using Editor
sharedPreferences.edit {
    putString("username", "john_doe")  // ✅ Uses apply() implicitly
    putInt("user_age", 25)
    putBoolean("is_logged_in", true)
}

// 3. Read data
val username = sharedPreferences.getString("username", "")  // Default: ""
val age = sharedPreferences.getInt("user_age", 0)         // Default: 0
```

**Two Save Methods:**

```kotlin
// apply() — Asynchronous (recommended)
editor.putString("key", "value")
editor.apply()  // ✅ Doesn't block UI

// commit() — Synchronous
val success = editor.commit()  // ❌ Blocks UI, returns boolean
```

**Modern Approach with Kotlin Extensions:**

```kotlin
// Extension function
fun SharedPreferences.edit(action: SharedPreferences.Editor.() -> Unit) {
    val editor = edit()
    editor.action()
    editor.apply()  // ✅ Always async
}

// Usage
sharedPreferences.edit {
    putString("username", "john")
    putInt("age", 25)
}
```

**Supported Data Types:**

```kotlin
editor.putString("name", "John")           // String
editor.putInt("age", 25)                   // Int
editor.putLong("timestamp", 123456789L)    // Long
editor.putFloat("rating", 4.5f)            // Float
editor.putBoolean("enabled", true)         // Boolean
editor.putStringSet("tags", setOf("a", "b"))  // Set<String>
```

**Limitations:**

- Not suitable for large data (use [[c-room]])
- Not suitable for complex objects (use JSON or Serialization)
- Not encrypted by default (use EncryptedSharedPreferences for sensitive data)
- Not suitable for structured/relational data

**Security — EncryptedSharedPreferences:**

```kotlin
// For sensitive data
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

// ✅ Use same API
encryptedPrefs.edit {
    putString("auth_token", "sensitive_token")
}
```

---

## Follow-ups

- When should you use SharedPreferences vs [[c-room]] for data storage?
- What are the differences between apply() and commit() methods in SharedPreferences?
- How do you migrate from SharedPreferences to DataStore for modern Android apps?

## References

- [[c-room]]
- https://developer.android.com/training/data-storage/shared-preferences
- https://developer.android.com/topic/security/data

## Related Questions

### Prerequisites

- [[q-android-components-besides-activity--android--easy]] — Understanding Android components

### Related

- [[q-workmanager-return-result--android--medium]] — Background work and data persistence
- [[q-how-to-break-text-by-screen-width--android--easy]] — UI state management

### Advanced

- DataStore migration (concept note needed)
- EncryptedSharedPreferences implementation (advanced security patterns)
