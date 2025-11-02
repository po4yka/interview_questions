---
id: android-455
title: DataStore Preferences и Proto / DataStore Preferences and Proto
aliases: ["DataStore Preferences and Proto", "DataStore Preferences и Proto"]
topic: android
subtopics: [datastore]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, q-android-storage-types--android--medium]
created: 2025-10-20
updated: 2025-10-27
tags: [android/datastore, datastore, preferences, proto-datastore, storage, difficulty/medium]
sources: [https://developer.android.com/topic/libraries/architecture/datastore]
date created: Monday, October 27th 2025, 10:27:18 pm
date modified: Thursday, October 30th 2025, 12:47:37 pm
---

# Вопрос (RU)
> Что вы знаете о DataStore?

# Question (EN)
> What do you know about DataStore?

## Ответ (RU)

DataStore — это современное решение для хранения данных в Android, заменяющее SharedPreferences. Предоставляет два варианта: **Preferences DataStore** (ключ-значение) и **Proto DataStore** (типизированные объекты с Protocol Buffers). Использует корутины и Flow для асинхронности и реактивности.

### Основные Концепции

**Preferences DataStore** — простое хранилище ключ-значение без схемы:
- Подходит для простых настроек (theme, language, flags)
- Не требует определения схемы
- Минимальная конфигурация

**Proto DataStore** — типизированное хранилище:
- Требует определение схемы `.proto`
- Compile-time type safety
- Лучшая производительность сериализации
- Подходит для сложных структур данных

**Ключевые отличия от SharedPreferences:**
- Асинхронный API (корутины) — не блокирует UI поток
- Транзакционность — атомарные операции через `edit` или `updateData`
- Безопасность типов — для Proto DataStore
- Поддержка миграций

### Preferences DataStore: Пример

```kotlin
// ✅ Создание с делегатом
private val Context.dataStore by preferencesDataStore(name = "settings")

// ✅ Определение ключей
private val THEME_KEY = stringPreferencesKey("theme")

// Чтение
val themeFlow: Flow<String> = context.dataStore.data
    .map { prefs -> prefs[THEME_KEY] ?: "light" }

// Запись (транзакционно)
suspend fun saveTheme(theme: String) {
    context.dataStore.edit { prefs ->
        prefs[THEME_KEY] = theme
    }
}
```

### Proto DataStore: Пример

**Схема (settings.proto):**
```protobuf
syntax = "proto3";
message UserSettings {
  string theme = 1;
  bool notifications_enabled = 2;
  int32 font_size = 3;
}
```

**Сериализатор:**
```kotlin
object UserSettingsSerializer : Serializer<UserSettings> {
    override val defaultValue = UserSettings.getDefaultInstance()

    override suspend fun readFrom(input: InputStream) =
        UserSettings.parseFrom(input)

    override suspend fun writeTo(t: UserSettings, output: OutputStream) =
        t.writeTo(output)
}
```

**Использование:**
```kotlin
private val Context.settingsStore by dataStore(
    fileName = "user_settings.pb",
    serializer = UserSettingsSerializer
)

// Чтение
val settingsFlow: Flow<UserSettings> = context.settingsStore.data

// Запись (транзакционно)
suspend fun updateTheme(theme: String) {
    context.settingsStore.updateData { current ->
        current.toBuilder()
            .setTheme(theme)
            .build()
    }
}
```

### Миграция из SharedPreferences

```kotlin
val Context.dataStore by preferencesDataStore(
    name = "settings",
    produceMigrations = { context ->
        listOf(
            // ✅ Автоматическая миграция всех значений
            SharedPreferencesMigration(context, "old_prefs_name")
        )
    }
)
```

### Когда Использовать

| Сценарий | Решение | Причина |
|----------|---------|---------|
| Простые настройки (theme, language) | Preferences | Минимальная конфигурация |
| Сложные структуры (user profile) | Proto | Type safety, лучшая производительность |
| Миграция с SharedPreferences | Preferences | Встроенная поддержка миграций |
| Большой объем данных | Не использовать | Для больших данных → Room или файлы |

**Важно:** DataStore не подходит для больших объемов данных или частых синхронных чтений.

## Answer (EN)

DataStore is a modern data storage solution for Android, replacing SharedPreferences. It provides two variants: **Preferences DataStore** (key-value) and **Proto DataStore** (typed objects with Protocol Buffers). Uses coroutines and Flow for asynchronicity and reactivity.

### Core Concepts

**Preferences DataStore** — simple key-value storage without schema:
- Suitable for simple settings (theme, language, flags)
- No schema definition required
- Minimal configuration

**Proto DataStore** — typed storage:
- Requires `.proto` schema definition
- Compile-time type safety
- Better serialization performance
- Suitable for complex data structures

**Key Differences from SharedPreferences:**
- Asynchronous API (coroutines) — doesn't block UI thread
- Transactional — atomic operations via `edit` or `updateData`
- Type safety — for Proto DataStore
- Migration support

### Preferences DataStore: Example

```kotlin
// ✅ Create with delegate
private val Context.dataStore by preferencesDataStore(name = "settings")

// ✅ Define keys
private val THEME_KEY = stringPreferencesKey("theme")

// Read
val themeFlow: Flow<String> = context.dataStore.data
    .map { prefs -> prefs[THEME_KEY] ?: "light" }

// Write (transactionally)
suspend fun saveTheme(theme: String) {
    context.dataStore.edit { prefs ->
        prefs[THEME_KEY] = theme
    }
}
```

### Proto DataStore: Example

**Schema (settings.proto):**
```protobuf
syntax = "proto3";
message UserSettings {
  string theme = 1;
  bool notifications_enabled = 2;
  int32 font_size = 3;
}
```

**Serializer:**
```kotlin
object UserSettingsSerializer : Serializer<UserSettings> {
    override val defaultValue = UserSettings.getDefaultInstance()

    override suspend fun readFrom(input: InputStream) =
        UserSettings.parseFrom(input)

    override suspend fun writeTo(t: UserSettings, output: OutputStream) =
        t.writeTo(output)
}
```

**Usage:**
```kotlin
private val Context.settingsStore by dataStore(
    fileName = "user_settings.pb",
    serializer = UserSettingsSerializer
)

// Read
val settingsFlow: Flow<UserSettings> = context.settingsStore.data

// Write (transactionally)
suspend fun updateTheme(theme: String) {
    context.settingsStore.updateData { current ->
        current.toBuilder()
            .setTheme(theme)
            .build()
    }
}
```

### Migration from SharedPreferences

```kotlin
val Context.dataStore by preferencesDataStore(
    name = "settings",
    produceMigrations = { context ->
        listOf(
            // ✅ Automatically migrate all values
            SharedPreferencesMigration(context, "old_prefs_name")
        )
    }
)
```

### When to Use

| Scenario | Solution | Reason |
|----------|----------|--------|
| Simple settings (theme, language) | Preferences | Minimal configuration |
| Complex structures (user profile) | Proto | Type safety, better performance |
| Migration from SharedPreferences | Preferences | Built-in migration support |
| Large data volumes | Don't use | For large data → Room or files |

**Important:** DataStore is not suitable for large data volumes or frequent synchronous reads.


## Follow-ups

- How do you handle DataStore exceptions (e.g., CorruptionException)?
- What are the performance implications of using DataStore vs SharedPreferences?
- When should you use DataStore instead of Room database?
- How do you test DataStore in unit tests?
- What happens if multiple processes access the same DataStore file?

## References

- [[c-coroutines]] - Kotlin coroutines and Flow fundamentals
- Android DataStore official documentation
- Protocol Buffers documentation (for Proto DataStore schema definition)

## Related Questions

### Prerequisites
- Understanding of Kotlin coroutines and Flow
- Basic knowledge of Android storage options

### Related (Same Level)
- [[q-android-storage-types--android--medium]] - Overview of storage options in Android

### Advanced
- Implementing custom Serializer for Proto DataStore with error handling
- Multi-module DataStore configuration with dependency injection
