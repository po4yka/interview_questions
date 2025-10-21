---
id: 20251016-163010
title: Android Storage Types / Типы хранилища Android
aliases: [Android Storage Types, Типы хранилища Android]
topic: android
subtopics: [data-storage, files-media]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-android-manifest-file--android--easy, q-android-security-best-practices--android--medium, q-android-architectural-patterns--android--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/data-storage, android/files-media, content-providers, data-storage, external-storage, file-system, internal-storage, persistence, sharedpreferences, sqlite, storage, difficulty/medium]
---

# Question (EN)
> What types of storage exist in Android applications?

# Вопрос (RU)
> Какие типы хранилищ существуют в Android-приложениях?

---

## Answer (EN)

**Android Storage Types** provide different mechanisms for persisting data based on size, privacy, and sharing requirements.

**Storage Types Theory:**
Android offers multiple storage options, each optimized for specific use cases. The choice depends on data size, privacy needs, sharing requirements, and query complexity.

**1. SharedPreferences:**
Key-value storage for small data like settings and preferences.

```kotlin
val prefs = getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit()
    .putString("username", "john_doe")
    .putBoolean("dark_mode", true)
    .apply()

val username = prefs.getString("username", "")
```

**1.1. DataStore (Modern Alternative):**
Type-safe, asynchronous replacement for SharedPreferences with Flow support.

```kotlin
// Preferences DataStore
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

// Write
context.dataStore.edit { settings ->
    settings[stringPreferencesKey("username")] = "john_doe"
    settings[booleanPreferencesKey("dark_mode")] = true
}

// Read as Flow
val usernameFlow: Flow<String> = context.dataStore.data
    .map { preferences ->
        preferences[stringPreferencesKey("username")] ?: ""
    }
```

**2. Internal Storage:**
Private file storage accessible only by your app.

```kotlin
// Write file
context.openFileOutput("data.txt", Context.MODE_PRIVATE).use { output ->
    output.write("content".toByteArray())
}

// Read file
val inputStream = context.openFileInput("data.txt")
val content = inputStream.bufferedReader().use { it.readText() }
```

**3. External Storage:**
Shared storage for media files and large data.

```kotlin
// App-specific directory (no permission needed)
val appDir = context.getExternalFilesDir(null)
val file = File(appDir, "photo.jpg")

// MediaStore for shared media
val contentValues = ContentValues().apply {
    put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
}
val uri = context.contentResolver.insert(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    contentValues
)
```

**4. SQLite Database:**
Relational database for structured data with complex queries.

```kotlin
// Room database
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE name LIKE :search")
    suspend fun searchUsers(search: String): List<User>

    @Insert
    suspend fun insert(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**5. Content Providers:**
Secure data sharing between applications.

```kotlin
// Read contacts
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)

cursor?.use {
    while (it.moveToNext()) {
        val name = it.getString(it.getColumnIndexOrThrow(
            ContactsContract.Contacts.DISPLAY_NAME
        ))
    }
}
```

**Storage Comparison:**

| Type | Size Limit | Privacy | Persistence | Use Case |
|------|------------|---------|-------------|----------|
| SharedPreferences | Small (KB) | Private | Survives restart | Settings, flags |
| DataStore | Small (KB) | Private | Survives restart | Modern settings, reactive |
| Internal Storage | App quota | Private | Deleted on uninstall | Private files, cache |
| External Storage | Device limit | Public/Private | Configurable | Media, large files |
| SQLite | Device limit | Private | Deleted on uninstall | Structured data |
| Content Providers | Varies | Controlled | Varies | Inter-app sharing |

**Modern Recommendations:**
- **DataStore** instead of SharedPreferences
- **Room** instead of raw SQLite
- **Scoped Storage** for external files
- **Encrypted storage** for sensitive data

---

## Ответ (RU)

**Типы хранилища Android** предоставляют различные механизмы для сохранения данных в зависимости от размера, приватности и требований к обмену.

**Теория типов хранилища:**
Android предлагает несколько вариантов хранения, каждый оптимизирован для конкретных случаев использования. Выбор зависит от размера данных, потребностей в приватности, требований к обмену и сложности запросов.

**1. SharedPreferences:**
Хранилище ключ-значение для небольших данных как настройки и предпочтения.

```kotlin
val prefs = getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit()
    .putString("username", "john_doe")
    .putBoolean("dark_mode", true)
    .apply()

val username = prefs.getString("username", "")
```

**1.1. DataStore (Современная альтернатива):**
Типобезопасная, асинхронная замена SharedPreferences с поддержкой Flow.

```kotlin
// Preferences DataStore
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

// Запись
context.dataStore.edit { settings ->
    settings[stringPreferencesKey("username")] = "john_doe"
    settings[booleanPreferencesKey("dark_mode")] = true
}

// Чтение как Flow
val usernameFlow: Flow<String> = context.dataStore.data
    .map { preferences ->
        preferences[stringPreferencesKey("username")] ?: ""
    }
```

**2. Внутреннее хранилище:**
Приватное файловое хранилище, доступное только вашему приложению.

```kotlin
// Запись файла
context.openFileOutput("data.txt", Context.MODE_PRIVATE).use { output ->
    output.write("content".toByteArray())
}

// Чтение файла
val inputStream = context.openFileInput("data.txt")
val content = inputStream.bufferedReader().use { it.readText() }
```

**3. Внешнее хранилище:**
Общее хранилище для медиафайлов и больших данных.

```kotlin
// Директория приложения (разрешение не нужно)
val appDir = context.getExternalFilesDir(null)
val file = File(appDir, "photo.jpg")

// MediaStore для общих медиа
val contentValues = ContentValues().apply {
    put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
}
val uri = context.contentResolver.insert(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    contentValues
)
```

**4. База данных SQLite:**
Реляционная база данных для структурированных данных со сложными запросами.

```kotlin
// База данных Room
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE name LIKE :search")
    suspend fun searchUsers(search: String): List<User>

    @Insert
    suspend fun insert(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**5. Content Providers:**
Безопасный обмен данными между приложениями.

```kotlin
// Чтение контактов
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)

cursor?.use {
    while (it.moveToNext()) {
        val name = it.getString(it.getColumnIndexOrThrow(
            ContactsContract.Contacts.DISPLAY_NAME
        ))
    }
}
```

**Сравнение хранилищ:**

| Тип | Ограничение размера | Приватность | Постоянство | Случай использования |
|------|---------------------|-------------|-------------|---------------------|
| SharedPreferences | Маленький (KB) | Приватный | Переживает перезапуск | Настройки, флаги |
| DataStore | Маленький (KB) | Приватный | Переживает перезапуск | Современные настройки, реактивные |
| Внутреннее хранилище | Квота приложения | Приватный | Удаляется при удалении | Приватные файлы, кеш |
| Внешнее хранилище | Лимит устройства | Публичный/Приватный | Настраиваемое | Медиа, большие файлы |
| SQLite | Лимит устройства | Приватный | Удаляется при удалении | Структурированные данные |
| Content Providers | Варьируется | Контролируемый | Варьируется | Межприложенный обмен |

**Современные рекомендации:**
- **DataStore** вместо SharedPreferences
- **Room** вместо сырого SQLite
- **Scoped Storage** для внешних файлов
- **Зашифрованное хранилище** для чувствительных данных

---

## Follow-ups

- How do you choose between different storage types?
- What are the security implications of each storage type?
- How do you handle data migration between storage types?

## References

- https://developer.android.com/training/data-storage
- https://developer.android.com/guide/topics/data/data-storage
- https://developer.android.com/topic/libraries/architecture/room

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration
- [[q-android-app-components--android--easy]] - App components

### Related (Medium)
- [[q-android-security-best-practices--android--medium]] - Security practices
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns
