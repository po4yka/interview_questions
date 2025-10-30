---
id: 20251016-163010
title: Android Storage Types / Типы хранилища Android
aliases: ["Android Storage Types", "Типы хранилища Android"]
topic: android
subtopics: [room, datastore, files-media]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-room-database, c-datastore, c-scoped-storage, q-android-manifest-file--android--easy, q-android-security-best-practices--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/room, android/datastore, android/files-media, storage, persistence, difficulty/medium]
date created: Thursday, October 30th 2025, 11:36:48 am
date modified: Thursday, October 30th 2025, 12:43:01 pm
---

# Вопрос (RU)
> Какие существуют типы хранилищ данных в Android и когда их использовать?

# Question (EN)
> What are the Android storage types and when should you use each?

## Ответ (RU)

Android предоставляет четыре основных механизма хранения, каждый оптимизирован под конкретные сценарии.

**1. DataStore — настройки приложения**

Асинхронная замена SharedPreferences на основе Kotlin Flow.

```kotlin
// ✅ Типобезопасное чтение/запись
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

dataStore.edit { prefs ->
    prefs[stringPreferencesKey("theme")] = "dark"
}
val theme = dataStore.data.map { it[stringPreferencesKey("theme")] }
```

**Использование**: пользовательские настройки, feature flags, токены (до 10-20 ключей, <1 MB).

**2. Internal Storage — приватные файлы**

Доступны только вашему приложению, удаляются при деинсталляции.

```kotlin
// ✅ Безопасная запись
context.openFileOutput("cache.json", MODE_PRIVATE).use {
    it.write(data.toByteArray())
}

// ❌ Избегайте прямого File API
val wrong = File("/data/data/com.app/files/cache.json") // небезопасно
```

**Использование**: временный кэш, логи, приватные конфигурации.

**3. External Storage — общие файлы**

Scoped Storage (Android 10+): app-specific directories без разрешений, MediaStore для общих медиа.

```kotlin
// ✅ App-specific (разрешения не нужны)
val appDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
val photo = File(appDir, "photo.jpg")

// ✅ MediaStore для общих медиа
val uri = contentResolver.insert(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    }
)
```

**Использование**: фото/видео, документы, экспортируемые файлы.

**4. Room Database — структурированные данные**

Type-safe ORM над SQLite с compile-time проверкой SQL.

```kotlin
@Entity
data class User(@PrimaryKey val id: Int, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE name LIKE :search")
    fun search(search: String): Flow<List<User>>
}
```

**Использование**: сложные запросы, связанные данные, offline-first.

**Сравнительная таблица:**

| Хранилище | Размер | Приватность | Сценарий |
|-----------|--------|-------------|----------|
| DataStore | <1 MB | Приватное | Настройки |
| Internal | До квоты | Приватное | Кэш, логи |
| External (app-specific) | До емкости | Приватное | Приватные медиа |
| External (MediaStore) | До емкости | Публичное | Общие медиа |
| Room | До емкости | Приватное | БД |

**Рекомендации:**
- Мигрируйте с SharedPreferences на DataStore
- Для чувствительных данных: EncryptedSharedPreferences или EncryptedFile
- Room > raw SQLite (типобезопасность)
- Scoped Storage обязателен для targetSdk 30+

## Answer (EN)

Android provides four core storage mechanisms, each optimized for specific use cases.

**1. DataStore — app settings**

Async SharedPreferences replacement based on Kotlin Flow.

```kotlin
// ✅ Type-safe read/write
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

dataStore.edit { prefs ->
    prefs[stringPreferencesKey("theme")] = "dark"
}
val theme = dataStore.data.map { it[stringPreferencesKey("theme")] }
```

**Use for**: user preferences, feature flags, tokens (up to 10-20 keys, <1 MB).

**2. Internal Storage — private files**

Accessible only by your app, deleted on uninstall.

```kotlin
// ✅ Safe write
context.openFileOutput("cache.json", MODE_PRIVATE).use {
    it.write(data.toByteArray())
}

// ❌ Avoid direct File API
val wrong = File("/data/data/com.app/files/cache.json") // unsafe
```

**Use for**: temp cache, logs, private configs.

**3. External Storage — shared files**

Scoped Storage (Android 10+): app-specific directories without permissions, MediaStore for shared media.

```kotlin
// ✅ App-specific (no permissions needed)
val appDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
val photo = File(appDir, "photo.jpg")

// ✅ MediaStore for shared media
val uri = contentResolver.insert(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    }
)
```

**Use for**: photos/videos, documents, exportable files.

**4. Room Database — structured data**

Type-safe ORM over SQLite with compile-time SQL verification.

```kotlin
@Entity
data class User(@PrimaryKey val id: Int, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE name LIKE :search")
    fun search(search: String): Flow<List<User>>
}
```

**Use for**: complex queries, related data, offline-first.

**Comparison Table:**

| Storage | Size | Privacy | Scenario |
|---------|------|---------|----------|
| DataStore | <1 MB | Private | Settings |
| Internal | Up to quota | Private | Cache, logs |
| External (app-specific) | Device limit | Private | Private media |
| External (MediaStore) | Device limit | Public | Shared media |
| Room | Device limit | Private | Database |

**Recommendations:**
- Migrate from SharedPreferences to DataStore
- For sensitive data: EncryptedSharedPreferences or EncryptedFile
- Prefer Room over raw SQLite (type safety)
- Scoped Storage mandatory for targetSdk 30+

## Follow-ups

- How does Proto DataStore differ from Preferences DataStore and when should you choose each?
- What happens to Internal Storage data during app updates vs. uninstall?
- How do you implement encrypted storage for sensitive data like auth tokens?
- What are the performance trade-offs between Room and raw SQLite?
- How do you handle storage permission changes when migrating from pre-Scoped Storage to Android 10+?

## References

- [[c-room-database]]
- [[c-datastore]]
- [[c-scoped-storage]]
- https://developer.android.com/training/data-storage
- https://developer.android.com/topic/libraries/architecture/datastore
- https://developer.android.com/training/data-storage/room

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]] - Permissions configuration for storage access

### Related
- [[q-android-security-best-practices--android--medium]] - Encryption and secure storage patterns
- [[q-android-architectural-patterns--android--medium]] - Repository pattern for data layer

### Advanced
- Implementing custom ContentProvider for inter-app data sharing
- Optimizing Room performance with indices and query optimization
