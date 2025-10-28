---
id: 20251016-163010
title: Android Storage Types / Типы хранилища Android
aliases: ["Android Storage Types", "Типы хранилища Android"]
topic: android
subtopics: [datastore, files-media]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, q-android-manifest-file--android--easy, q-android-security-best-practices--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/datastore, android/files-media, difficulty/medium]
---
# Вопрос (RU)
> Какие существуют типы хранилищ данных в Android и когда их использовать?

# Question (EN)
> What are the Android storage types and when should you use each?

## Ответ (RU)

Android предлагает несколько механизмов хранения данных, каждый оптимизирован для конкретных сценариев на основе размера данных, требований к приватности и возможности совместного доступа.

**Основные типы хранилищ:**

**1. DataStore** (современная замена SharedPreferences)
Типобезопасное асинхронное хранилище для настроек и простых данных.

```kotlin
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

// Запись
dataStore.edit { prefs ->
    prefs[stringPreferencesKey("theme")] = "dark"
}

// Чтение как Flow
val themeFlow = dataStore.data.map { it[stringPreferencesKey("theme")] ?: "light" }
```

**2. Internal Storage** (приватное файловое хранилище)
Доступно только вашему приложению, удаляется при деинсталляции.

```kotlin
// Запись
context.openFileOutput("cache.json", MODE_PRIVATE).use {
    it.write(jsonData.toByteArray())
}

// Чтение
val data = context.openFileInput("cache.json").bufferedReader().readText()
```

**3. External Storage** (общее файловое хранилище)
Для медиа и больших файлов. С Android 10+ используется Scoped Storage.

```kotlin
// ✅ App-specific directory (разрешение не требуется)
val appDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
val photo = File(appDir, "photo.jpg")

// ✅ MediaStore для общих медиафайлов
val values = ContentValues().apply {
    put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
}
contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
```

**4. Room Database** (структурированные данные)
Type-safe обёртка над SQLite для сложных запросов.

```kotlin
@Entity
data class User(@PrimaryKey val id: Int, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE name LIKE :search")
    suspend fun search(search: String): List<User>
}
```

**Сравнение хранилищ:**

| Тип | Размер | Приватность | Удаление | Сценарий |
|-----|--------|-------------|----------|----------|
| DataStore | KB | Приватное | С приложением | Настройки, preferences |
| Internal | До квоты | Приватное | С приложением | Кэш, приватные файлы |
| External | До емкости | Публичное/Приватное | Настраивается | Медиа, документы |
| Room | До емкости | Приватное | С приложением | Реляционные данные |

**Рекомендации:**
- Используйте DataStore вместо SharedPreferences
- Используйте Room для баз данных (не raw SQLite)
- Для чувствительных данных применяйте EncryptedSharedPreferences или EncryptedFile
- С Android 10+ следуйте политике Scoped Storage для внешних файлов

## Answer (EN)

Android provides several data storage mechanisms, each optimized for specific scenarios based on data size, privacy requirements, and sharing capabilities.

**Main Storage Types:**

**1. DataStore** (modern SharedPreferences replacement)
Type-safe asynchronous storage for settings and simple data.

```kotlin
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

// Write
dataStore.edit { prefs ->
    prefs[stringPreferencesKey("theme")] = "dark"
}

// Read as Flow
val themeFlow = dataStore.data.map { it[stringPreferencesKey("theme")] ?: "light" }
```

**2. Internal Storage** (private file storage)
Accessible only to your app, deleted on uninstall.

```kotlin
// Write
context.openFileOutput("cache.json", MODE_PRIVATE).use {
    it.write(jsonData.toByteArray())
}

// Read
val data = context.openFileInput("cache.json").bufferedReader().readText()
```

**3. External Storage** (shared file storage)
For media and large files. Android 10+ uses Scoped Storage.

```kotlin
// ✅ App-specific directory (no permission needed)
val appDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
val photo = File(appDir, "photo.jpg")

// ✅ MediaStore for shared media
val values = ContentValues().apply {
    put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
}
contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
```

**4. Room Database** (structured data)
Type-safe SQLite wrapper for complex queries.

```kotlin
@Entity
data class User(@PrimaryKey val id: Int, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE name LIKE :search")
    suspend fun search(search: String): List<User>
}
```

**Storage Comparison:**

| Type | Size | Privacy | Deletion | Use Case |
|------|------|---------|----------|----------|
| DataStore | KB | Private | With app | Settings, preferences |
| Internal | Up to quota | Private | With app | Cache, private files |
| External | Device limit | Public/Private | Configurable | Media, documents |
| Room | Device limit | Private | With app | Relational data |

**Recommendations:**
- Use DataStore instead of SharedPreferences
- Use Room for databases (not raw SQLite)
- For sensitive data, use EncryptedSharedPreferences or EncryptedFile
- On Android 10+, follow Scoped Storage policies for external files

## Follow-ups

- What happens to Internal Storage data when the app is updated vs. uninstalled?
- How does Scoped Storage affect backward compatibility on Android 9 and below?
- When should you use Proto DataStore instead of Preferences DataStore?
- How do you implement encryption for sensitive data in SharedPreferences?
- What are the performance trade-offs between Room and raw SQLite queries?
- How do you handle migration when moving from SharedPreferences to DataStore?

## References

- [[c-room]] - Room database concept
- https://developer.android.com/training/data-storage
- https://developer.android.com/topic/libraries/architecture/datastore

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Understanding Android app components
- [[q-android-manifest-file--android--easy]] - Permissions configuration

### Related
- [[q-android-security-best-practices--android--medium]] - Encryption and security
- [[q-android-architectural-patterns--android--medium]] - Repository pattern for data layer

### Advanced
- Implementing custom ContentProvider for inter-app data sharing
- Optimizing Room database performance with indices and FTS
- Managing database migrations in production apps