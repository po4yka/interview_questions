---
id: "20251015082237334"
title: "Android Storage Types / Типы хранилища Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - android/data-storage
  - content-providers
  - data-storage
  - external-storage
  - file-system
  - internal-storage
  - persistence
  - sharedpreferences
  - sqlite
  - storage
---
# Какие типы хранилищ существуют в Android-приложениях?

# Question (EN)
> What types of storage exist in Android applications?

# Вопрос (RU)
> Какие типы хранилищ существуют в Android-приложениях?

---

## Answer (EN)

Android applications have **several types of data storage**, each suitable for different scenarios and data requirements.

### Main Storage Types

### 1. SharedPreferences

**Purpose:** Store small key-value pairs

**Best for:**
- User settings and preferences
- App configuration
- Simple flags and states
- Tokens and session IDs

**Example:**

```kotlin
val prefs = getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

// Write
prefs.edit()
    .putString("username", "john_doe")
    .putBoolean("dark_mode", true)
    .putInt("launch_count", 5)
    .apply()

// Read
val username = prefs.getString("username", "")
val isDarkMode = prefs.getBoolean("dark_mode", false)
```

**Characteristics:**
- Simple API
- Persistent across app sessions
- Not suitable for large data
- Not suitable for complex objects

---

### 2. Internal Storage

**Purpose:** Store private files inside app's internal memory

**Best for:**
- Private app data
- Cache files
- Downloaded content
- User-generated files that should be private

**Characteristics:**
- **Private**: Only accessible by your app
- **Auto-deleted**: Removed when app is uninstalled
- **Location**: `/data/data/<package_name>/files/`

**Example:**

```kotlin
// Write file to internal storage
val filename = "user_data.txt"
val content = "User profile information"

context.openFileOutput(filename, Context.MODE_PRIVATE).use { output ->
    output.write(content.toByteArray())
}

// Read file from internal storage
val inputStream = context.openFileInput(filename)
val text = inputStream.bufferedReader().use { it.readText() }

// Get file object
val file = File(context.filesDir, filename)

// Cache directory (automatically managed)
val cacheFile = File(context.cacheDir, "temp.dat")
```

**File Locations:**

```kotlin
// Regular files
context.filesDir  // /data/data/<package>/files/

// Cache files (can be cleared by system)
context.cacheDir  // /data/data/<package>/cache/

// Code cache (for dynamically generated code)
context.codeCacheDir  // /data/data/<package>/code_cache/
```

---

### 3. External Storage

**Purpose:** Store files on external storage (SD card or device external partition)

**Best for:**
- Media files (photos, videos, music)
- Large files
- Files that should survive app uninstall
- Files shared with other apps

**Characteristics:**
- **Accessible**: Can be accessed by other apps (if public)
- **Persistent**: Survives app uninstall (public directories)
- **Requires permissions** (on older Android versions)

**Scoped Storage (Android 10+):**

```kotlin
// App-specific directory (no permission needed)
val appDir = context.getExternalFilesDir(null)
val mediaDir = context.getExternalFilesDir(Environment.DIRECTORY_PICTURES)

// Write to app-specific directory
val file = File(appDir, "photo.jpg")
FileOutputStream(file).use { output ->
    bitmap.compress(Bitmap.CompressFormat.JPEG, 100, output)
}
```

**MediaStore API (for shared media):**

```kotlin
// Save image to shared Pictures directory
fun saveImageToGallery(context: Context, bitmap: Bitmap, displayName: String) {
    val contentValues = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, displayName)
        put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
        put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
    }

    val uri = context.contentResolver.insert(
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        contentValues
    )

    uri?.let {
        context.contentResolver.openOutputStream(it)?.use { output ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, output)
        }
    }
}
```

**Storage Locations:**

```kotlin
// App-specific external storage (deleted on uninstall)
context.getExternalFilesDir(null)
context.getExternalCacheDir()

// Public shared directories (survive uninstall)
Environment.DIRECTORY_PICTURES
Environment.DIRECTORY_DOWNLOADS
Environment.DIRECTORY_MUSIC
Environment.DIRECTORY_MOVIES
```

---

### 4. SQLite Database

**Purpose:** Full-featured relational database for structured data

**Best for:**
- Structured data with relationships
- Complex queries and transactions
- Large datasets with indexing
- Data requiring ACID guarantees

**Example:**

```kotlin
// Using Room (recommended)
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE name LIKE :search")
    suspend fun searchUsers(search: String): List<User>

    @Insert
    suspend fun insert(user: User)

    @Delete
    suspend fun delete(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// Usage
val db = Room.databaseBuilder(context, AppDatabase::class.java, "app-db").build()
val users = db.userDao().searchUsers("%john%")
```

**Characteristics:**
- ACID transactions
- Complex queries with SQL
- Relationships and joins
- Indexing for performance
- **Location**: `/data/data/<package_name>/databases/`

---

### 5. Content Providers

**Purpose:** Share data between applications

**Best for:**
- Accessing system data (contacts, calendar, media)
- Sharing app data with other apps
- Providing structured access to your data
- Secure data sharing with permissions

**Example - Reading Contacts:**

```kotlin
// Query contacts
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null,
    null,
    null,
    null
)

cursor?.use {
    while (it.moveToNext()) {
        val id = it.getLong(it.getColumnIndexOrThrow(ContactsContract.Contacts._ID))
        val name = it.getString(it.getColumnIndexOrThrow(ContactsContract.Contacts.DISPLAY_NAME))
        // Use contact data
    }
}
```

**Example - Creating Content Provider:**

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Return data as Cursor
        return database.query(...)
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        // Insert data
        return insertedUri
    }

    // Other CRUD methods...
}
```

**Common Content Providers:**
- `ContactsContract` - Contacts
- `MediaStore` - Images, videos, audio
- `CalendarContract` - Calendar events
- `Settings` - System settings

---

### Storage Comparison Table

| Storage Type | Size Limit | Accessibility | Persistence | Use Case |
|--------------|------------|---------------|-------------|----------|
| **SharedPreferences** | Small (KB) | Private | Survives restart | Settings, preferences |
| **Internal Storage** | App quota | Private | Deleted on uninstall | Private files, cache |
| **External Storage** | Device limit | Public/Private | Configurable | Media, large files |
| **SQLite** | Device limit | Private | Deleted on uninstall | Structured data |
| **Content Providers** | Varies | Controlled | Varies | Cross-app data sharing |

## Decision Tree

```kotlin
// Choose storage based on requirements:

if (data is small key-value pairs) {
    use SharedPreferences
} else if (data is private files) {
    use Internal Storage
} else if (data is media/large files to share) {
    use External Storage (MediaStore)
} else if (data is structured/relational) {
    use SQLite (Room)
} else if (sharing data with other apps) {
    use Content Provider
}
```

### Modern Best Practices

**1. DataStore (replacement for SharedPreferences):**

```kotlin
// Preferences DataStore
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

// Write
context.dataStore.edit { settings ->
    settings[stringPreferencesKey("username")] = "john"
}

// Read as Flow
val usernameFlow: Flow<String> = context.dataStore.data
    .map { preferences ->
        preferences[stringPreferencesKey("username")] ?: ""
    }
```

**2. Room (replacement for raw SQLite):**

```kotlin
// Type-safe, compile-time checked queries
@Query("SELECT * FROM users WHERE age > :minAge")
suspend fun getUsersOlderThan(minAge: Int): List<User>
```

**3. WorkManager (for background data sync):**

```kotlin
// Schedule periodic data sync
val syncWorkRequest = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()
```

### Summary

**5 main storage types in Android:**

1. **SharedPreferences** - Small key-value data (settings, flags)
2. **Internal Storage** - Private app files
3. **External Storage** - Media and shared files
4. **SQLite Database** - Structured relational data
5. **Content Providers** - Cross-app data sharing

**Choose based on:**
- Data size and structure
- Privacy requirements
- Sharing needs
- Query complexity

---

## Ответ (RU)

В Android-приложениях существует **несколько типов хранилищ данных**, каждый из которых подходит для различных сценариев и требований к данным.

### Основные типы хранилищ

### 1. SharedPreferences

**Назначение:** Хранение небольших пар ключ-значение

**Лучше всего для:**
- Настройки и предпочтения пользователя
- Конфигурация приложения
- Простые флаги и состояния
- Токены и ID сессий

**Пример:**

```kotlin
val prefs = getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

// Запись
prefs.edit()
    .putString("username", "ivan_petrov")
    .putBoolean("dark_mode", true)
    .putInt("launch_count", 5)
    .apply()

// Чтение
val username = prefs.getString("username", "")
val isDarkMode = prefs.getBoolean("dark_mode", false)
```

**Характеристики:**
- Простой API
- Сохраняется между сессиями приложения
- Не подходит для больших данных
- Не подходит для сложных объектов

---

### 2. Internal Storage (Внутреннее хранилище)

**Назначение:** Хранение приватных файлов во внутренней памяти приложения

**Лучше всего для:**
- Приватные данные приложения
- Кеш файлы
- Скачанный контент
- Пользовательские файлы, которые должны быть приватными

**Характеристики:**
- **Приватное**: Доступно только вашему приложению
- **Авто-удаление**: Удаляется при удалении приложения
- **Расположение**: `/data/data/<package_name>/files/`

**Пример:**

```kotlin
// Записать файл во внутреннее хранилище
val filename = "user_data.txt"
val content = "Информация профиля пользователя"

context.openFileOutput(filename, Context.MODE_PRIVATE).use { output ->
    output.write(content.toByteArray())
}

// Прочитать файл из внутреннего хранилища
val inputStream = context.openFileInput(filename)
val text = inputStream.bufferedReader().use { it.readText() }

// Получить объект файла
val file = File(context.filesDir, filename)

// Директория кеша (автоматически управляется)
val cacheFile = File(context.cacheDir, "temp.dat")
```

---

### 3. External Storage (Внешнее хранилище)

**Назначение:** Хранение файлов на внешнем хранилище (SD карта или внешний раздел устройства)

**Лучше всего для:**
- Медиа файлы (фото, видео, музыка)
- Большие файлы
- Файлы, которые должны остаться после удаления приложения
- Файлы, общие для других приложений

**Характеристики:**
- **Доступность**: Может быть доступно другим приложениям (если публичное)
- **Постоянство**: Переживает удаление приложения (публичные директории)
- **Требует разрешений** (на старых версиях Android)

**Scoped Storage (Android 10+):**

```kotlin
// Директория, специфичная для приложения (не требует разрешений)
val appDir = context.getExternalFilesDir(null)
val mediaDir = context.getExternalFilesDir(Environment.DIRECTORY_PICTURES)

// Запись в директорию приложения
val file = File(appDir, "photo.jpg")
FileOutputStream(file).use { output ->
    bitmap.compress(Bitmap.CompressFormat.JPEG, 100, output)
}
```

**MediaStore API (для общих медиа):**

```kotlin
// Сохранить изображение в общую директорию Pictures
fun saveImageToGallery(context: Context, bitmap: Bitmap, displayName: String) {
    val contentValues = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, displayName)
        put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
        put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
    }

    val uri = context.contentResolver.insert(
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        contentValues
    )

    uri?.let {
        context.contentResolver.openOutputStream(it)?.use { output ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, output)
        }
    }
}
```

---

### 4. SQLite Database

**Назначение:** Полнофункциональная реляционная база данных для структурированных данных

**Лучше всего для:**
- Структурированные данные с отношениями
- Сложные запросы и транзакции
- Большие наборы данных с индексированием
- Данные, требующие ACID гарантий

**Пример:**

```kotlin
// Использование Room (рекомендуется)
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE name LIKE :search")
    suspend fun searchUsers(search: String): List<User>

    @Insert
    suspend fun insert(user: User)

    @Delete
    suspend fun delete(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// Использование
val db = Room.databaseBuilder(context, AppDatabase::class.java, "app-db").build()
val users = db.userDao().searchUsers("%иван%")
```

**Характеристики:**
- ACID транзакции
- Сложные запросы с SQL
- Отношения и соединения (joins)
- Индексирование для производительности
- **Расположение**: `/data/data/<package_name>/databases/`

---

### 5. Content Providers

**Назначение:** Обмен данными между приложениями

**Лучше всего для:**
- Доступ к системным данным (контакты, календарь, медиа)
- Обмен данными приложения с другими приложениями
- Предоставление структурированного доступа к вашим данным
- Безопасный обмен данными с разрешениями

**Пример - Чтение контактов:**

```kotlin
// Запрос контактов
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null,
    null,
    null,
    null
)

cursor?.use {
    while (it.moveToNext()) {
        val id = it.getLong(it.getColumnIndexOrThrow(ContactsContract.Contacts._ID))
        val name = it.getString(it.getColumnIndexOrThrow(ContactsContract.Contacts.DISPLAY_NAME))
        // Использовать данные контакта
    }
}
```

**Общие Content Providers:**
- `ContactsContract` - Контакты
- `MediaStore` - Изображения, видео, аудио
- `CalendarContract` - События календаря
- `Settings` - Системные настройки

---

### Таблица сравнения хранилищ

| Тип хранилища | Ограничение размера | Доступность | Постоянство | Случай использования |
|--------------|---------------------|-------------|-------------|---------------------|
| **SharedPreferences** | Маленький (KB) | Приватный | Переживает перезапуск | Настройки, предпочтения |
| **Internal Storage** | Квота приложения | Приватный | Удаляется при удалении | Приватные файлы, кеш |
| **External Storage** | Лимит устройства | Публичный/Приватный | Настраиваемое | Медиа, большие файлы |
| **SQLite** | Лимит устройства | Приватный | Удаляется при удалении | Структурированные данные |
| **Content Providers** | Варьируется | Контролируемый | Варьируется | Обмен данными между приложениями |

### Дерево решений

```kotlin
// Выбор хранилища на основе требований:

if (данные это небольшие пары ключ-значение) {
    использовать SharedPreferences
} else if (данные это приватные файлы) {
    использовать Internal Storage
} else if (данные это медиа/большие файлы для обмена) {
    использовать External Storage (MediaStore)
} else if (данные структурированные/реляционные) {
    использовать SQLite (Room)
} else if (обмен данными с другими приложениями) {
    использовать Content Provider
}
```

### Современные лучшие практики

**1. DataStore (замена SharedPreferences):**

```kotlin
// Preferences DataStore
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

// Запись
context.dataStore.edit { settings ->
    settings[stringPreferencesKey("username")] = "иван"
}

// Чтение как Flow
val usernameFlow: Flow<String> = context.dataStore.data
    .map { preferences ->
        preferences[stringPreferencesKey("username")] ?: ""
    }
```

**2. Room (замена сырого SQLite):**

```kotlin
// Типобезопасные, проверяемые во время компиляции запросы
@Query("SELECT * FROM users WHERE age > :minAge")
suspend fun getUsersOlderThan(minAge: Int): List<User>
```

### Резюме

**5 основных типов хранилищ в Android:**

1. **SharedPreferences** - Небольшие данные ключ-значение (настройки, флаги)
2. **Internal Storage** - Приватные файлы приложения
3. **External Storage** - Медиа и общие файлы
4. **SQLite Database** - Структурированные реляционные данные
5. **Content Providers** - Обмен данными между приложениями

**Выбирайте на основе:**
- Размера и структуры данных
- Требований к приватности
- Потребностей в обмене
- Сложности запросов


---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-sharedpreferences-definition--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Related (Medium)
- [[q-encrypted-file-storage--security--medium]] - Storage
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage
- [[q-room-paging3-integration--room--medium]] - Storage
- [[q-room-type-converters-advanced--room--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--room--hard]] - Storage
