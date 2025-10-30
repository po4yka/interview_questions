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
related: [q-android-architectural-patterns--android--medium, q-android-manifest-file--android--easy, q-android-security-best-practices--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/room, android/datastore, android/files-media, difficulty/medium]
---
# Вопрос (RU)
> Какие существуют типы хранилищ данных в Android и когда их использовать?

# Question (EN)
> What are the Android storage types and when should you use each?

## Ответ (RU)

Android предлагает четыре основных механизма хранения, каждый оптимизирован под конкретные сценарии.

**1. DataStore** — key-value хранилище для настроек
Асинхронная замена SharedPreferences, возвращает Flow.

```kotlin
// ✅ Типобезопасное чтение/запись
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

dataStore.edit { prefs ->
    prefs[stringPreferencesKey("theme")] = "dark"
}
val theme = dataStore.data.map { it[stringPreferencesKey("theme")] }
```

**Когда использовать**: пользовательские настройки, простые флаги, кэш токенов (до 10-20 ключей).

**2. Internal Storage** — приватные файлы приложения
Доступ только у вашего приложения, удаляется при деинсталляции.

```kotlin
// ✅ Запись через openFileOutput
context.openFileOutput("cache.json", MODE_PRIVATE).use {
    it.write(data.toByteArray())
}

// ❌ Избегайте прямого File API без context.filesDir
val wrongFile = File("/data/data/com.app/files/cache.json") // небезопасно
```

**Когда использовать**: временный кэш, логи, приватные конфиги.

**3. External Storage** — общее файловое хранилище
Scoped Storage (Android 10+): app-specific directories без разрешений, MediaStore для общих медиа.

```kotlin
// ✅ App-specific (разрешение не нужно)
val appDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
val photo = File(appDir, "photo.jpg")

// ✅ MediaStore для доступных медиа
val uri = contentResolver.insert(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    }
)
```

**Когда использовать**: фото/видео, документы, экспортируемые файлы.

**4. Room Database** — структурированные реляционные данные
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

**Когда использовать**: сложные запросы, связанные данные, офлайн-первый подход.

**Сравнительная таблица:**

| Хранилище | Размер | Приватность | Удаление | Сценарий |
|-----------|--------|-------------|----------|----------|
| DataStore | <1 MB | Приватное | С приложением | Настройки |
| Internal | До квоты | Приватное | С приложением | Кэш, логи |
| External | До емкости | Публичное* | Настраивается | Медиа |
| Room | До емкости | Приватное | С приложением | БД |

*\*App-specific directories приватные*

**Рекомендации:**
- Избегайте SharedPreferences (устарел), используйте DataStore
- Для чувствительных данных: EncryptedSharedPreferences или EncryptedFile
- Room > raw SQLite (типобезопасность, меньше ошибок)
- Scoped Storage обязателен для targetSdk 30+

## Answer (EN)

Android provides four core storage mechanisms, each optimized for specific use cases.

**1. DataStore** — key-value storage for settings
Async SharedPreferences replacement, returns Flow.

```kotlin
// ✅ Type-safe read/write
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

dataStore.edit { prefs ->
    prefs[stringPreferencesKey("theme")] = "dark"
}
val theme = dataStore.data.map { it[stringPreferencesKey("theme")] }
```

**Use for**: user preferences, feature flags, token cache (up to 10-20 keys).

**2. Internal Storage** — app-private files
Only accessible by your app, deleted on uninstall.

```kotlin
// ✅ Write via openFileOutput
context.openFileOutput("cache.json", MODE_PRIVATE).use {
    it.write(data.toByteArray())
}

// ❌ Avoid direct File API without context.filesDir
val wrongFile = File("/data/data/com.app/files/cache.json") // unsafe
```

**Use for**: temp cache, logs, private configs.

**3. External Storage** — shared file storage
Scoped Storage (Android 10+): app-specific directories without permissions, MediaStore for shared media.

```kotlin
// ✅ App-specific (no permission needed)
val appDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
val photo = File(appDir, "photo.jpg")

// ✅ MediaStore for accessible media
val uri = contentResolver.insert(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    }
)
```

**Use for**: photos/videos, documents, exportable files.

**4. Room Database** — structured relational data
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

**Use for**: complex queries, related data, offline-first architecture.

**Comparison Table:**

| Storage | Size | Privacy | Deletion | Scenario |
|---------|------|---------|----------|----------|
| DataStore | <1 MB | Private | With app | Settings |
| Internal | Up to quota | Private | With app | Cache, logs |
| External | Device limit | Public* | Configurable | Media |
| Room | Device limit | Private | With app | Database |

*\*App-specific directories are private*

**Recommendations:**
- Avoid SharedPreferences (deprecated), use DataStore
- For sensitive data: EncryptedSharedPreferences or EncryptedFile
- Room > raw SQLite (type safety, fewer bugs)
- Scoped Storage mandatory for targetSdk 30+

## Follow-ups

- What happens to Internal Storage data when the app is updated vs. uninstalled?
- When should you use Proto DataStore instead of Preferences DataStore?
- How do you handle migration from SharedPreferences to DataStore without data loss?
- What are the performance implications of reading large files from Internal vs. External Storage?
- How does Scoped Storage affect backward compatibility for apps targeting Android 9 and below?

## References

- https://developer.android.com/training/data-storage
- https://developer.android.com/topic/libraries/architecture/datastore
- https://developer.android.com/training/data-storage/use-cases

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]] - Permissions configuration for storage access

### Related
- [[q-android-security-best-practices--android--medium]] - Encryption and secure storage patterns
- [[q-android-architectural-patterns--android--medium]] - Repository pattern for data layer abstraction

### Advanced
- Implementing custom ContentProvider for inter-app data sharing
- Optimizing Room database performance with indices and query optimization
- Managing complex database migrations in production with multiple schema versions