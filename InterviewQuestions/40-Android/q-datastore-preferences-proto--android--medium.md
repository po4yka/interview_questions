---
id: 20251020-200000
title: Datastore Preferences Proto / DataStore Preferences Proto
aliases: [Datastore Preferences Proto, DataStore Preferences Proto]
topic: android
subtopics:
  - datastore
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-storage-types--android--medium
  - q-room-database-basics--android--easy
  - q-shared-preferences-android--android--easy
created: 2025-10-20
updated: 2025-10-20
tags: [android/datastore, datastore, difficulty/medium, preferences, proto-datastore, storage]
source: https://developer.android.com/topic/libraries/architecture/datastore
source_note: Android DataStore documentation
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:10 pm
---

# Вопрос (RU)
> Что вы знаете о DataStore?

# Question (EN)
> What do you know about DataStore?

## Ответ (RU)

Jetpack DataStore - это решение для хранения данных, которое позволяет хранить пары ключ-значение или типизированные объекты с протокольными буферами. DataStore использует Kotlin корутины и Flow для асинхронного, последовательного и транзакционного хранения данных.

### Теория: DataStore В Android

**Основные концепции:**
- **DataStore** - современная замена SharedPreferences
- **Preferences DataStore** - хранение пар ключ-значение без схемы
- **Proto DataStore** - типизированное хранение с протокольными буферами
- **Асинхронность** - использование корутин и Flow
- **Транзакционность** - атомарные операции

**Принципы работы:**
- DataStore использует корутины для асинхронных операций
- Flow обеспечивает реактивные обновления данных
- Транзакции гарантируют консистентность данных
- Типизация обеспечивает безопасность типов
- Миграция данных из SharedPreferences

### Preferences DataStore Vs Proto DataStore

**Сравнение реализаций:**

| Критерий | Preferences DataStore | Proto DataStore |
|----------|----------------------|-----------------|
| Схема | Без предопределенной схемы | Требует схему protobuf |
| Типизация | Нет типизации | Полная типизация |
| Сложность | Простая | Средняя |
| Производительность | Хорошая | Отличная |
| Размер | Минимальный | Больше |

**Выбор реализации:**
- **Preferences DataStore** - для простых настроек приложения
- **Proto DataStore** - для сложных структур данных

### Preferences DataStore

**Теоретические основы:**
Preferences DataStore хранит данные как пары ключ-значение без предопределенной схемы. Это простая реализация для базовых настроек приложения.

**Создание DataStore:**
```kotlin
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")
```

**Чтение данных:**
```kotlin
val EXAMPLE_COUNTER = intPreferencesKey("example_counter")
val exampleCounterFlow: Flow<Int> = context.dataStore.data.map { preferences ->
    preferences[EXAMPLE_COUNTER] ?: 0
}
```

**Запись данных:**
```kotlin
suspend fun incrementCounter() {
    context.dataStore.edit { preferences ->
        val currentCounterValue = preferences[EXAMPLE_COUNTER] ?: 0
        preferences[EXAMPLE_COUNTER] = currentCounterValue + 1
    }
}
```

### Proto DataStore

**Теоретические основы:**
Proto DataStore хранит данные как типизированные объекты с использованием протокольных буферов. Это обеспечивает полную типизацию и лучшую производительность.

**Определение схемы:**
```protobuf
syntax = "proto3";

option java_package = "com.example.application";
option java_multiple_files = true;

message Settings {
  int32 example_counter = 1;
  string user_name = 2;
  bool notifications_enabled = 3;
}
```

**Сериализатор:**
```kotlin
object SettingsSerializer : Serializer<Settings> {
    override val defaultValue: Settings = Settings.getDefaultInstance()

    override suspend fun readFrom(input: InputStream): Settings {
        try {
            return Settings.parseFrom(input)
        } catch (exception: InvalidProtocolBufferException) {
            throw CorruptionException("Cannot read proto.", exception)
        }
    }

    override suspend fun writeTo(t: Settings, output: OutputStream) = t.writeTo(output)
}
```

**Создание Proto DataStore:**
```kotlin
val Context.settingsDataStore: DataStore<Settings> by dataStore(
    fileName = "settings.pb",
    serializer = SettingsSerializer
)
```

**Использование Proto DataStore:**
```kotlin
val settingsFlow: Flow<Settings> = context.settingsDataStore.data

suspend fun updateUserName(newName: String) {
    context.settingsDataStore.updateData { currentSettings ->
        currentSettings.toBuilder()
            .setUserName(newName)
            .build()
    }
}
```

### Миграция Из SharedPreferences

**Теоретические основы:**
DataStore предоставляет инструменты для миграции данных из SharedPreferences. Это обеспечивает плавный переход без потери пользовательских данных.

**Миграция:**
```kotlin
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "settings",
    produceMigrations = { context ->
        listOf(sharedPreferencesMigration(context, "old_preferences_name"))
    }
)
```

### Преимущества DataStore

**Теоретические преимущества:**
- **Асинхронность** - не блокирует UI поток
- **Типизация** - безопасность типов на этапе компиляции
- **Транзакционность** - атомарные операции
- **Реактивность** - автоматические обновления через Flow
- **Консистентность** - гарантии целостности данных

**Практические преимущества:**
- Замена устаревшего SharedPreferences
- Лучшая производительность
- Современный API с корутинами
- Поддержка миграций
- Интеграция с архитектурными компонентами

### Лучшие Практики

**Теоретические принципы:**
- Используйте Preferences DataStore для простых настроек
- Используйте Proto DataStore для сложных структур
- Обрабатывайте исключения при чтении/записи
- Используйте миграции для обновления данных
- Кэшируйте часто используемые данные

**Практические рекомендации:**
- Создавайте DataStore как singleton
- Используйте Flow для реактивных обновлений
- Обрабатывайте ошибки gracefully
- Тестируйте миграции данных
- Документируйте схемы protobuf

## Answer (EN)

Jetpack DataStore is a data storage solution that allows you to store key-value pairs or typed objects with protocol buffers. DataStore uses Kotlin coroutines and Flow to store data asynchronously, consistently, and transactionally.

### Theory: DataStore in Android

**Core Concepts:**
- **DataStore** - modern replacement for SharedPreferences
- **Preferences DataStore** - key-value pair storage without schema
- **Proto DataStore** - typed storage with protocol buffers
- **Asynchrony** - using coroutines and Flow
- **Transactional** - atomic operations

**Working Principles:**
- DataStore uses coroutines for asynchronous operations
- Flow provides reactive data updates
- Transactions ensure data consistency
- Typing provides type safety
- Data migration from SharedPreferences

### Preferences DataStore Vs Proto DataStore

**Implementation Comparison:**

| Criterion | Preferences DataStore | Proto DataStore |
|-----------|----------------------|-----------------|
| Schema | No predefined schema | Requires protobuf schema |
| Typing | No typing | Full typing |
| Complexity | Simple | Medium |
| Performance | Good | Excellent |
| Size | Minimal | Larger |

**Implementation Selection:**
- **Preferences DataStore** - for simple app settings
- **Proto DataStore** - for complex data structures

### Preferences DataStore

**Theoretical Foundations:**
Preferences DataStore stores data as key-value pairs without a predefined schema. This is a simple implementation for basic app settings.

**Creating DataStore:**
```kotlin
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")
```

**Reading Data:**
```kotlin
val EXAMPLE_COUNTER = intPreferencesKey("example_counter")
val exampleCounterFlow: Flow<Int> = context.dataStore.data.map { preferences ->
    preferences[EXAMPLE_COUNTER] ?: 0
}
```

**Writing Data:**
```kotlin
suspend fun incrementCounter() {
    context.dataStore.edit { preferences ->
        val currentCounterValue = preferences[EXAMPLE_COUNTER] ?: 0
        preferences[EXAMPLE_COUNTER] = currentCounterValue + 1
    }
}
```

### Proto DataStore

**Theoretical Foundations:**
Proto DataStore stores data as typed objects using protocol buffers. This provides full typing and better performance.

**Schema Definition:**
```protobuf
syntax = "proto3";

option java_package = "com.example.application";
option java_multiple_files = true;

message Settings {
  int32 example_counter = 1;
  string user_name = 2;
  bool notifications_enabled = 3;
}
```

**Serializer:**
```kotlin
object SettingsSerializer : Serializer<Settings> {
    override val defaultValue: Settings = Settings.getDefaultInstance()

    override suspend fun readFrom(input: InputStream): Settings {
        try {
            return Settings.parseFrom(input)
        } catch (exception: InvalidProtocolBufferException) {
            throw CorruptionException("Cannot read proto.", exception)
        }
    }

    override suspend fun writeTo(t: Settings, output: OutputStream) = t.writeTo(output)
}
```

**Creating Proto DataStore:**
```kotlin
val Context.settingsDataStore: DataStore<Settings> by dataStore(
    fileName = "settings.pb",
    serializer = SettingsSerializer
)
```

**Using Proto DataStore:**
```kotlin
val settingsFlow: Flow<Settings> = context.settingsDataStore.data

suspend fun updateUserName(newName: String) {
    context.settingsDataStore.updateData { currentSettings ->
        currentSettings.toBuilder()
            .setUserName(newName)
            .build()
    }
}
```

### Migration from SharedPreferences

**Theoretical Foundations:**
DataStore provides tools for migrating data from SharedPreferences. This ensures a smooth transition without losing user data.

**Migration:**
```kotlin
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "settings",
    produceMigrations = { context ->
        listOf(sharedPreferencesMigration(context, "old_preferences_name"))
    }
)
```

### DataStore Benefits

**Theoretical Benefits:**
- **Asynchrony** - doesn't block UI thread
- **Typing** - compile-time type safety
- **Transactional** - atomic operations
- **Reactive** - automatic updates through Flow
- **Consistency** - data integrity guarantees

**Practical Benefits:**
- Replacement for deprecated SharedPreferences
- Better performance
- Modern API with coroutines
- Migration support
- Integration with architectural components

### Best Practices

**Theoretical Principles:**
- Use Preferences DataStore for simple settings
- Use Proto DataStore for complex structures
- Handle exceptions when reading/writing
- Use migrations for data updates
- Cache frequently used data

**Practical Recommendations:**
- Create DataStore as singleton
- Use Flow for reactive updates
- Handle errors gracefully
- Test data migrations
- Document protobuf schemas

**See also:** c-protocol-buffers, c-data-serialization


## Follow-ups

- How do you migrate from SharedPreferences to DataStore?
- What are the performance differences between Preferences and Proto DataStore?
- How do you handle errors in DataStore operations?

## Related Questions

### Related (Same Level)
- [[q-android-storage-types--android--medium]]
