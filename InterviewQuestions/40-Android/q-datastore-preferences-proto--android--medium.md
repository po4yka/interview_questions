---\
id: android-455
title: DataStore Preferences и Proto / DataStore Preferences and Proto
aliases: [DataStore Preferences and Proto, DataStore Preferences и Proto]
topic: android
subtopics: [datastore]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, q-android-storage-types--android--medium, q-save-data-outside-fragment--android--medium, q-sharedpreferences-definition--android--easy]
created: 2025-10-20
updated: 2025-11-02
tags: [android/datastore, datastore, difficulty/medium, preferences, proto-datastore, storage]
sources:
  - https://developer.android.com/topic/libraries/architecture/datastore
---\
# Вопрос (RU)
> Что вы знаете о DataStore?

# Question (EN)
> What do you know about DataStore?

## Ответ (RU)

`DataStore` — современное рекомендуемое решение для локального хранения настроек и небольших порций данных в Android, пришедшее на смену большинству сценариев использования `SharedPreferences`. Предоставляет два варианта: **`Preferences DataStore`** (ключ-значение) и **`Proto DataStore`** (типизированные объекты с Protocol Buffers). Использует `Coroutines` и `Flow` для асинхронности и реактивности. Основные преимущества: асинхронный API, транзакционность, типобезопасность (`Proto DataStore`), поддержка миграций.

### Основные Концепции

**`Preferences DataStore`** — простое хранилище ключ-значение без схемы:
- Подходит для простых настроек (theme, language, flags)
- Не требует определения схемы — минимальная конфигурация
- Типобезопасные ключи через `stringPreferencesKey()`, `intPreferencesKey()`, `booleanPreferencesKey()`
- Транзакционные операции через `edit { }` блок

**`Proto DataStore`** — типизированное хранилище:
- Требует определение схемы `.proto` (Protocol Buffers)
- Compile-time type safety — ошибки обнаруживаются на этапе компиляции
- Лучшая производительность сериализации — бинарный формат, компактнее JSON
- Подходит для сложных структур данных — вложенные объекты, списки, перечисления

**Ключевые отличия от `SharedPreferences`:**
- Асинхронный API (`Coroutines`) — не блокирует UI поток, снижает риск `ANR`
- Транзакционность — атомарные операции через `edit` или `updateData`, данные либо записываются полностью, либо откатываются
- Безопасность типов — для `Proto DataStore` (compile-time проверка)
- Поддержка миграций — встроенная миграция из `SharedPreferences` и между версиями `Proto`

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
    override val defaultValue: UserSettings = UserSettings.getDefaultInstance()

    override suspend fun readFrom(input: InputStream): UserSettings =
        UserSettings.parseFrom(input) // На практике стоит обрабатывать IO/Corruption ошибки

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

### Миграция Из SharedPreferences

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
| Миграция с `SharedPreferences` | Preferences | Встроенная поддержка миграций |
| Большой объем данных | Не использовать | Для больших данных → `Room` или файлы |

**Важно:** `DataStore` не подходит для больших объемов данных (используйте `Room` или файлы) или частых синхронных чтений (асинхронный API по умолчанию). Вместо жесткого лимита по размеру ориентируйтесь на практику: хранить относительно небольшой объем (обычно настройки и связанные с ними данные), а для больших объемов или сложных запросов использовать `Room` или другие механизмы хранения.

## Answer (EN)

`DataStore` is a modern recommended solution for local storage of settings and small amounts of data on Android, replacing most `SharedPreferences` use cases. It provides two variants: **`Preferences DataStore`** (key-value) and **`Proto DataStore`** (typed objects with Protocol Buffers). It uses `Coroutines` and `Flow` for asynchronicity and reactivity. Key advantages: asynchronous API, transactional operations, type safety (`Proto DataStore`), migration support.

### Core Concepts

**`Preferences DataStore`** — simple key-value storage without schema:
- Suitable for simple settings (theme, language, flags)
- No schema definition required — minimal configuration
- Type-safe keys via `stringPreferencesKey()`, `intPreferencesKey()`, `booleanPreferencesKey()`
- Transactional operations via `edit { }` block

**`Proto DataStore`** — typed storage:
- Requires `.proto` schema definition (Protocol Buffers)
- Compile-time type safety — errors caught at compile time
- Better serialization performance — binary format, more compact than JSON
- Suitable for complex data structures — nested objects, lists, enums

**Key Differences from `SharedPreferences`:**
- Asynchronous API (`Coroutines`) — doesn't block UI thread, reduces `ANR` risk
- Transactional — atomic operations via `edit` or `updateData`, data either fully written or rolled back
- Type safety — for `Proto DataStore` (compile-time checking)
- Migration support — built-in migration from `SharedPreferences` and between `Proto` versions

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
    override val defaultValue: UserSettings = UserSettings.getDefaultInstance()

    override suspend fun readFrom(input: InputStream): UserSettings =
        UserSettings.parseFrom(input) // In real code, handle IO/Corruption exceptions as needed

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
| Migration from `SharedPreferences` | Preferences | Built-in migration support |
| Large data volumes | Don't use | For large data → `Room` or files |

**Important:** `DataStore` is not suitable for large data volumes (use `Room` or files) or frequent synchronous reads (asynchronous API by default). Rather than a strict documented size limit, follow best practices: keep it for relatively small data sets (typically preferences and related small data), and use `Room` or other storage for large data or complex queries.

## Follow-ups

- How do you handle `DataStore` exceptions (e.g., `CorruptionException`)?
- What are the performance implications of using `DataStore` vs `SharedPreferences`?
- When should you use `DataStore` instead of `Room` database?
- How do you test `DataStore` in unit tests?
- What happens if multiple processes access the same `DataStore` file?
- How to implement custom `Serializer` for `Proto DataStore` with error handling?

## References

- [[c-coroutines]]
- [Android DataStore Documentation](https://developer.android.com/topic/libraries/architecture/datastore)
- [Protocol Buffers Documentation](https://protobuf.dev/) (for `Proto DataStore` schema definition)

## Related Questions

### Prerequisites (Easier)
- Understanding of `Kotlin` coroutines and `Flow`
- Basic knowledge of Android storage options (`SharedPreferences`, `Room`)

### Related (Same Level)
- [[q-android-storage-types--android--medium]] — Overview of storage options in Android
- `Room` database for complex data structures

### Advanced (Harder)
- Implementing custom `Serializer` for `Proto DataStore` with error handling
- Multi-module `DataStore` configuration with dependency injection
- `DataStore` migration strategies for complex scenarios
