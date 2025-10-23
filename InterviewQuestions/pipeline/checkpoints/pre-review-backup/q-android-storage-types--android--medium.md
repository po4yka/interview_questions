---
id: 20251016-163010
title: Android Storage Types / Типы хранилища Android
aliases:
- Android Storage Types
- Типы хранилища Android
topic: android
subtopics:
- datastore
- files-media
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-manifest-file--android--easy
- q-android-security-best-practices--android--medium
- q-android-architectural-patterns--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/datastore
- android/files-media
- difficulty/medium
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