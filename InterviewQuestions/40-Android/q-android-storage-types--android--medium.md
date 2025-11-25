---
id: android-183
title: Android Storage Types / Типы хранилища Android
aliases: [Android Storage Types, Типы хранилища Android]
topic: android
subtopics:
  - datastore
  - files-media
  - room
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-storage-options
  - q-android-manifest-file--android--easy
  - q-android-security-best-practices--android--medium
  - q-android-service-types--android--easy
  - q-app-start-types-android--android--medium
  - q-module-types-android--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/datastore, android/files-media, android/room, difficulty/medium, persistence, storage]

date created: Saturday, November 1st 2025, 12:46:43 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Какие существуют типы хранилищ данных в Android и когда их использовать?

# Question (EN)
> What are the Android storage types and when should you use each?

## Ответ (RU)

Android предоставляет четыре основных механизма хранения, каждый оптимизирован под конкретные сценарии.

**1. DataStore — настройки приложения и небольшие данные**

Асинхронная, более безопасная замена `SharedPreferences` на основе Kotlin `Flow` и корутин. Подходит для небольших наборов key-value или структурированных данных.

```kotlin
// ✅ Типобезопасное чтение/запись
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

dataStore.edit { prefs ->
    prefs[stringPreferencesKey("theme")] = "dark"
}
val theme = dataStore.data.map { it[stringPreferencesKey("theme")] }
```

**Использование**: пользовательские настройки, feature flags, легковесные токены и конфигурация. Предпочтительно для относительно малого объема данных; не для больших файлов или больших структур.

**2. Internal Storage — приватные файлы приложения**

Доступны только вашему приложению (через его UID), удаляются при деинсталляции.

```kotlin
// ✅ Безопасная запись
context.openFileOutput("cache.json", MODE_PRIVATE).use {
    it.write(data.toByteArray())
}

// ❌ Избегайте прямого File API с жестко заданными путями
val wrong = File("/data/data/com.app/files/cache.json") // небезопасно и ломко
```

**Использование**: временный и постоянный кэш, приватные конфигурации, внутренние БД/файлы, которые не должны быть доступны другим приложениям и будут очищены при удалении приложения.

**3. External Storage — общие файлы и app-specific каталоги**

Scoped Storage (Android 10+):
- app-specific директории на внешнем/общем хранилище через `getExternalFilesDir()` — не требуют разрешений, изолированы от других приложений, но физически находятся в общем хранилище и могут быть доступны пользователю (например, через подключение к ПК);
- `MediaStore` для общих медиафайлов.

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

**Использование**:
- app-specific external: кэш/медиа, которые может увидеть пользователь и которые удаляются при деинсталляции приложения;
- MediaStore: фото/видео/аудио и другие файлы, которые должны быть доступны за пределами приложения.

**4. Room Database — структурированные данные**

Type-safe слой над SQLite с compile-time проверкой SQL.

```kotlin
@Entity
data class User(@PrimaryKey val id: Int, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE name LIKE :search")
    fun search(search: String): Flow<List<User>>
}
```

**Использование**: сложные запросы, связанные данные, offline-first, кеш доменной модели, когда требуется индексация и целостность.

См. также: [[c-android-storage-options]]

**Сравнительная таблица:**

| Хранилище | Размер (ориентир) | Приватность | Сценарий |
|-----------|-------------------|-------------|----------|
| DataStore | Малый объем       | Приватное   | Настройки, конфиг |
| Internal  | До квоты          | Приватное   | Кэш, конфиг, приватные файлы |
| External (app-specific) | До емкости устройства | Изолировано от других приложений; доступно пользователю | Медиа/файлы приложения |
| External (MediaStore)   | До емкости устройства | Доступно другим приложениям/пользователю | Общие медиа и документы |
| Room     | До емкости устройства | Приватное | Локальная БД |

**Рекомендации:**
- Мигрируйте с `SharedPreferences` на `DataStore` для настроек и конфигурации;
- Для чувствительных данных: используйте `EncryptedSharedPreferences` или `EncryptedFile` (и/или шифрование над Room);
- Предпочитайте Room сырому SQLite для безопасности типов и поддержки миграций;
- Scoped Storage обязателен для `targetSdk 30+`.

## Answer (EN)

Android provides four core storage mechanisms, each optimized for specific use cases.

**1. DataStore — app settings and small data**

Asynchronous, safer replacement for `SharedPreferences` based on Kotlin `Flow` and coroutines. Suitable for small key-value or structured datasets.

```kotlin
// ✅ Type-safe read/write
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

dataStore.edit { prefs ->
    prefs[stringPreferencesKey("theme")] = "dark"
}
val theme = dataStore.data.map { it[stringPreferencesKey("theme")] }
```

**Use for**: user preferences, feature flags, lightweight tokens and configuration. Prefer it for relatively small amounts of data; not for large files or big datasets.

**2. Internal Storage — private app files**

Accessible only by your app (per-UID sandbox), deleted on uninstall.

```kotlin
// ✅ Safe write
context.openFileOutput("cache.json", MODE_PRIVATE).use {
    it.write(data.toByteArray())
}

// ❌ Avoid direct File API with hardcoded internal paths
val wrong = File("/data/data/com.app/files/cache.json") // unsafe and brittle
```

**Use for**: temporary and persistent cache, private configs, internal DBs/files that must not be accessible to other apps and will be removed on app uninstall.

**3. External Storage — shared files and app-specific directories**

Scoped Storage (Android 10+):
- App-specific directories on external/shared storage via `getExternalFilesDir()` — no runtime permissions, isolated from other apps, but physically on shared storage and typically user-visible (e.g., via PC);
- `MediaStore` for shared media files.

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

**Use for**:
- App-specific external: app media/cache that should be visible to the user and removed on uninstall;
- MediaStore: photos/videos/audio and other files that should be accessible outside your app.

**4. Room Database — structured data**

Type-safe abstraction over SQLite with compile-time SQL verification.

```kotlin
@Entity
data class User(@PrimaryKey val id: Int, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE name LIKE :search")
    fun search(search: String): Flow<List<User>>
}
```

**Use for**: complex queries, relational/linked data, offline-first caching, when you need indexing and data integrity.

See also: [[c-android-storage-options]]

**Comparison Table:**

| Storage | Size (typical) | Privacy | Scenario |
|---------|----------------|---------|----------|
| DataStore | Small         | Private | Settings, config |
| Internal  | Up to quota   | Private | Cache, config, private files |
| External (app-specific) | Device limit | Isolated from other apps; user-visible | App media/files |
| External (MediaStore)   | Device limit | Visible to other apps/user | Shared media and documents |
| Room     | Device limit | Private | Local database |

**Recommendations:**
- Migrate from `SharedPreferences` to `DataStore` for settings and configuration;
- For sensitive data: use `EncryptedSharedPreferences` or `EncryptedFile` (and/or encryption on top of Room);
- Prefer Room over raw SQLite for type safety and migration support;
- Scoped Storage is mandatory for `targetSdk 30+`.

## Follow-ups

- How does Proto DataStore differ from Preferences DataStore and when should you choose each?
- What happens to Internal Storage data during app updates vs. uninstall?
- How do you implement encrypted storage for sensitive data like auth tokens?
- What are the performance trade-offs between Room and raw SQLite?
- How do you handle storage permission changes when migrating from pre-Scoped Storage to Android 10+?

## References

- [[c-android-storage-options]]

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]] - Permissions configuration for storage access

### Related
- [[q-android-security-best-practices--android--medium]] - Encryption and secure storage patterns
- [[q-android-architectural-patterns--android--medium]] - Repository pattern for data layer

### Advanced
- Implementing custom `ContentProvider` for inter-app data sharing
- Optimizing Room performance with indices and query optimization

## Дополнительные Вопросы (RU)
- В чем различия между Proto DataStore и Preferences DataStore и когда выбирать каждый из них?
- Что происходит с данными во внутреннем хранилище при обновлении приложения и при удалении?
- Как реализовать шифрованное хранилище для чувствительных данных (например, токенов авторизации)?
- Каковы производственные компромиссы между Room и "чистым" SQLite?
- Как обрабатывать изменения разрешений на хранилище при миграции с до-Scoped Storage на Android 10+?
## Связанные Вопросы (RU)
### Предпосылки
- [[q-android-manifest-file--android--easy]] - Конфигурация разрешений для доступа к хранилищу
### Связано
- [[q-android-security-best-practices--android--medium]] - Шифрование и безопасные паттерны хранения
- [[q-android-architectural-patterns--android--medium]] - Паттерн репозитория для слоя данных
### Продвинутое
- Реализация собственного `ContentProvider` для обмена данными между приложениями
- Оптимизация производительности Room с помощью индексов и оптимизации запросов