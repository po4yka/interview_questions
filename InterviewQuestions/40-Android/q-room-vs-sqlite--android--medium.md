---
id: android-270
title: Room vs SQLite / Room против SQLite
aliases: [Room vs SQLite, Room против SQLite]
topic: android
subtopics:
  - room
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-room
  - q-android-runtime-art--android--medium
  - q-room-code-generation-timing--android--medium
  - q-room-relations-embedded--android--medium
  - q-room-transactions-dao--android--medium
  - q-room-type-converters-advanced--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/room, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:03 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)
> Room против SQLite

# Question (EN)
> Room vs SQLite

---

## Ответ (RU)

**SQLite** – это **низкоуровневая реляционная база данных**, которая требует **ручного написания SQL-запросов**.

**Room** – это **библиотека-абстракция с ORM-подобным маппингом над SQLite** (но не «полноценный» универсальный ORM), которая предоставляет **удобный API с аннотациями**, поддерживает **`LiveData` и `Flow`**, и предлагает **структурированную систему миграций** (включая ограниченную поддержку autoMigrations для совместимых изменений схемы).

Room упрощает работу с базой данных и делает код более читаемым, но **внутри все равно использует SQLite**.

### Ключевые Различия

#### 1. Уровень Абстракции

**SQLite — низкоуровневый:**

```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(
    context, "database.db", null, 1
) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT
            )
        """)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS users")
        onCreate(db)
    }
}
```

**Room — более высокоуровневый:**

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

#### 2. Обработка SQL-запросов

**SQLite — ручные строки:**

```kotlin
fun getUser(userId: Int): User? {
    val db = dbHelper.readableDatabase

    // SQL как сырая строка — ошибки только во время выполнения!
    val cursor = db.rawQuery(
        "SELECT * FROM usres WHERE id = ?",  // Опечатка! "usres" вместо "users"
        arrayOf(userId.toString())
    )

    // Ручная обработка курсора
    var user: User? = null
    if (cursor.moveToFirst()) {
        user = User(
            id = cursor.getInt(cursor.getColumnIndexOrThrow("id")),
            name = cursor.getString(cursor.getColumnIndexOrThrow("name")),
            email = cursor.getString(cursor.getColumnIndexOrThrow("email"))
        )
    }
    cursor.close()
    return user
}
```

**Room — типобезопасный, проверяемый:**

```kotlin
@Dao
interface UserDao {
    // Проверка SQL на этапе компиляции относительно описанной схемы
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Int): User?

    // Опечатки в именах таблиц/колонок будут пойманы при компиляции
}
```

#### 3. CRUD-операции

**SQLite — многословный:**

```kotlin
// Insert
fun insertUser(name: String, email: String) {
    val db = dbHelper.writableDatabase
    val values = ContentValues().apply {
        put("name", name)
        put("email", email)
    }
    db.insert("users", null, values)
}

// Update
fun updateUser(user: User) {
    val db = dbHelper.writableDatabase
    val values = ContentValues().apply {
        put("name", user.name)
        put("email", user.email)
    }
    db.update("users", values, "id = ?", arrayOf(user.id.toString()))
}

// Delete
fun deleteUser(userId: Int) {
    val db = dbHelper.writableDatabase
    db.delete("users", "id = ?", arrayOf(userId.toString()))
}
```

**Room — лаконичный:**

```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User)

    @Update
    suspend fun update(user: User)

    @Delete
    suspend fun delete(user: User)

    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteById(userId: Int)
}
```

#### 4. Реактивные Данные

**SQLite — нет встроенной поддержки:**

```kotlin
// Нужно вручную уведомлять наблюдателей
fun getUsers(): List<User> {
    val db = dbHelper.readableDatabase
    val cursor = db.rawQuery("SELECT * FROM users", null)

    val users = mutableListOf<User>()
    while (cursor.moveToNext()) {
        users.add(/* парсинг пользователя */)
    }
    cursor.close()

    // Нет автоматических обновлений при изменении данных
    return users
}
```

**Room — встроенные `Flow`/`LiveData`:**

```kotlin
@Dao
interface UserDao {
    // Автоматически эмитит новые значения при изменении данных
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    // Или с LiveData
    @Query("SELECT * FROM users")
    fun getAllUsersLiveData(): LiveData<List<User>>
}

// Во Fragment/Activity — сбор с учетом жизненного цикла
viewLifecycleOwner.lifecycleScope.launch {
    userDao.getAllUsers().collect { users ->
        adapter.submitList(users)
    }
}
```

#### 5. Типобезопасность

**SQLite — нет типобезопасности:**

```kotlin
// Легко допустить ошибки
fun getUser(id: Int): User {
    val cursor = db.rawQuery("SELECT * FROM users WHERE id = ?", arrayOf(id.toString()))
    cursor.moveToFirst()

    // Опечатка в имени колонки — ошибка во время выполнения!
    val name = cursor.getString(cursor.getColumnIndexOrThrow("nmae"))

    // Неверный тип — ошибка во время выполнения!
    val email = cursor.getInt(cursor.getColumnIndexOrThrow("email"))

    return User(id, name, email.toString())
}
```

**Room — типобезопасный:**

```kotlin
@Dao
interface UserDao {
    // Проверка соответствия типов на этапе компиляции
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Int): User?
}

// Использование — типобезопасно
val user: User? = userDao.getUser(123)
```

#### 6. Миграции

**SQLite — ручные:**

```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(
    context, "db", null, 2
) {
    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        when (oldVersion) {
            1 -> {
                // Ручная миграция
                db.execSQL("ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 0")
            }
        }
    }
}
```

**Room — структурированные миграции:**

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("CREATE INDEX index_users_email ON users(email)")
    }
}

val db = Room.databaseBuilder(context, AppDatabase::class.java, "database")
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    .build()
```

#### 7. Тестирование

**SQLite — сложнее:**

```kotlin
// Можно писать тесты, работая с реальной SQLite (инструментальные тесты),
// но при прямом использовании API часто возникает много шаблонного кода и ручной настройки.
@Test
fun testGetUser() {
    val mockDb = mock(SQLiteDatabase::class.java)
    val mockCursor = mock(Cursor::class.java)

    whenever(mockDb.rawQuery(any(), any())).thenReturn(mockCursor)
    // ... много моков
}
```

**Room — проще:**

```kotlin
@Test
fun testGetUser() = runTest {
    // In-memory база данных для тестирования
    val db = Room.inMemoryDatabaseBuilder(
        context,
        AppDatabase::class.java
    ).build()

    val userDao = db.userDao()

    val user = User(id = 1, name = "John", email = "john@test.com")
    userDao.insert(user)

    val result = userDao.getUser(1)
    assertEquals(user, result)
}
```

### Таблица Сравнения

| Функция | SQLite | Room |
|---------|--------|------|
| **Абстракция** | Низкоуровневая | Высокоуровневый ORM-подобный слой |
| **Шаблонный код** | Много | Мало |
| **Проверка SQL** | Во время выполнения | На этапе компиляции |
| **Типобезопасность** | Нет | Да |
| **CRUD-операции** | Ручные ContentValues | Аннотации |
| **Реактивность (`Flow`/`LiveData`)** | Нет | Да (через API Room) |
| **Поддержка корутин** | Нет встроенной | Поддерживаются `suspend`/`Flow` API Room (выполняются вне UI-потока) |
| **Миграции** | Ручные | Структурированные (есть autoMigrations для части кейсов) |
| **Тестирование** | Сложнее | Проще (in-memory / инструментальные тесты) |
| **Производительность** | Быстро | Быстро (использует SQLite внутри) |
| **Зависимости** | Встроено | Библиотека Jetpack |

### Полный Пример Сравнения

**SQLite:**

```kotlin
class UserRepository(context: Context) {
    private val dbHelper = DatabaseHelper(context)

    fun insertUser(name: String, email: String): Long {
        val db = dbHelper.writableDatabase
        val values = ContentValues().apply {
            put("name", name)
            put("email", email)
        }
        return db.insert("users", null, values)
    }

    fun getAllUsers(): List<User> {
        val db = dbHelper.readableDatabase
        val cursor = db.rawQuery("SELECT * FROM users", null)
        val users = mutableListOf<User>()

        while (cursor.moveToNext()) {
            users.add(
                User(
                    id = cursor.getInt(0),
                    name = cursor.getString(1),
                    email = cursor.getString(2)
                )
            )
        }
        cursor.close()
        return users
    }
}
```

**Room:**

```kotlin
@Dao
interface UserDao {
    @Insert
    suspend fun insert(user: User): Long

    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>
}

class UserRepository(private val userDao: UserDao) {
    suspend fun insertUser(name: String, email: String): Long {
        return userDao.insert(User(name = name, email = email))
    }

    fun getAllUsers(): Flow<List<User>> = userDao.getAllUsers()
}
```

### Резюме

**SQLite:**
- Низкоуровневая реляционная база данных
- Требует ручных SQL-запросов в виде строк
- Нет проверки на этапе компиляции
- Много шаблонного кода
- Встроено в Android

**Room:**
- Высокоуровневая ORM-подобная абстракция над SQLite (но с ограничениями по сравнению с полноценными ORM)
- Типобезопасный API на основе аннотаций
- Проверка SQL и схемы на этапе компиляции
- Поддержка `LiveData`/`Flow`
- Структурированные миграции (autoMigrations для части изменений схемы)
- Более простое тестирование
- Меньше шаблонного кода
- По-прежнему использует SQLite внутри

**Рекомендация:** Используйте **Room** для современной разработки Android. Он обеспечивает лучшую безопасность, меньше кода и более простое сопровождение при сохранении производительности SQLite.

---

## Answer (EN)

**SQLite** is a **low-level relational database** that requires **manual SQL queries**.

**Room** is a **SQLite abstraction library with ORM-style mapping** (but not a fully generic ORM) that provides a **convenient annotation-based API**, supports **`LiveData` and `Flow`**, and offers a **structured migrations system** (including limited support for autoMigrations for compatible schema changes).

Room simplifies database operations and makes code more readable, but **internally it still uses SQLite**.

## Key Differences

### 1. Abstraction Level

**SQLite - Low-level:**

```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(
    context,
    "database.db",
    null,
    1
) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT
            )
        """)
    }

    override fun onUpgrade(db: SQLiteDatabase, old: Int, new: Int) {
        db.execSQL("DROP TABLE IF EXISTS users")
        onCreate(db)
    }
}
```

**Room - High-level:**

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

---

### 2. SQL Query Handling

**SQLite - Manual strings:**

```kotlin
// No compile-time validation
fun getUser(userId: Int): User? {
    val db = dbHelper.readableDatabase

    // SQL as raw string - errors only at runtime!
    val cursor = db.rawQuery(
        "SELECT * FROM usres WHERE id = ?",  // Typo! "usres" instead of "users"
        arrayOf(userId.toString())
    )

    // Manual cursor handling
    var user: User? = null
    if (cursor.moveToFirst()) {
        user = User(
            id = cursor.getInt(cursor.getColumnIndexOrThrow("id")),
            name = cursor.getString(cursor.getColumnIndexOrThrow("name")),
            email = cursor.getString(cursor.getColumnIndexOrThrow("email"))
        )
    }
    cursor.close()
    return user
}
```

**Room - Type-safe, validated:**

```kotlin
@Dao
interface UserDao {
    // Compile-time SQL validation against the schema
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Int): User?

    // Typo in table/column name will be caught at compile time
}
```

---

### 3. CRUD Operations

**SQLite - Verbose:**

```kotlin
// Insert
fun insertUser(name: String, email: String) {
    val db = dbHelper.writableDatabase
    val values = ContentValues().apply {
        put("name", name)
        put("email", email)
    }
    db.insert("users", null, values)
}

// Update
fun updateUser(user: User) {
    val db = dbHelper.writableDatabase
    val values = ContentValues().apply {
        put("name", user.name)
        put("email", user.email)
    }
    db.update("users", values, "id = ?", arrayOf(user.id.toString()))
}

// Delete
fun deleteUser(userId: Int) {
    val db = dbHelper.writableDatabase
    db.delete("users", "id = ?", arrayOf(userId.toString()))
}
```

**Room - Concise:**

```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User)

    @Update
    suspend fun update(user: User)

    @Delete
    suspend fun delete(user: User)

    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteById(userId: Int)
}
```

---

### 4. Reactive Data

**SQLite - No built-in support:**

```kotlin
// Must manually notify observers
fun getUsers(): List<User> {
    val db = dbHelper.readableDatabase
    val cursor = db.rawQuery("SELECT * FROM users", null)

    val users = mutableListOf<User>()
    while (cursor.moveToNext()) {
        users.add(/* parse user */)
    }
    cursor.close()

    // No automatic updates when data changes
    return users
}
```

**Room - Built-in `Flow`/`LiveData`:**

```kotlin
@Dao
interface UserDao {
    // Automatically emits new values when data changes
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    // Or with LiveData
    @Query("SELECT * FROM users")
    fun getAllUsersLiveData(): LiveData<List<User>>
}

// In Fragment/Activity - collect with lifecycle awareness
viewLifecycleOwner.lifecycleScope.launch {
    userDao.getAllUsers().collect { users ->
        adapter.submitList(users)
    }
}
```

---

### 5. Type Safety

**SQLite - No type safety:**

```kotlin
// Easy to make mistakes
fun getUser(id: Int): User {
    val cursor = db.rawQuery("SELECT * FROM users WHERE id = ?", arrayOf(id.toString()))
    cursor.moveToFirst()

    // Column name typo - runtime error!
    val name = cursor.getString(cursor.getColumnIndexOrThrow("nmae"))

    // Wrong type - runtime error!
    val email = cursor.getInt(cursor.getColumnIndexOrThrow("email"))

    return User(id, name, email.toString())
}
```

**Room - Type-safe:**

```kotlin
@Dao
interface UserDao {
    // Compile-time checking of mapping between SQL and Kotlin types
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Int): User?
}

// Usage - type-safe
val user: User? = userDao.getUser(123)
```

---

### 6. Migrations

**SQLite - Manual:**

```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(
    context, "db", null, 2
) {
    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        when (oldVersion) {
            1 -> {
                // Manual migration
                db.execSQL("ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 0")
            }
        }
    }
}
```

**Room - Structured migrations:**

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("CREATE INDEX index_users_email ON users(email)")
    }
}

val db = Room.databaseBuilder(context, AppDatabase::class.java, "database")
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    .build()
```

---

### 7. Testing

**SQLite - Difficult:**

```kotlin
// You can test against real SQLite (instrumented tests),
// but using the low-level APIs often involves more boilerplate and setup.
@Test
fun testGetUser() {
    val mockDb = mock(SQLiteDatabase::class.java)
    val mockCursor = mock(Cursor::class.java)

    whenever(mockDb.rawQuery(any(), any())).thenReturn(mockCursor)
    // ... lots of mocking
}
```

**Room - Easier:**

```kotlin
@Test
fun testGetUser() = runTest {
    // In-memory database for testing
    val db = Room.inMemoryDatabaseBuilder(
        context,
        AppDatabase::class.java
    ).build()

    val userDao = db.userDao()

    // Insert test data
    val user = User(id = 1, name = "John", email = "john@test.com")
    userDao.insert(user)

    // Test query
    val result = userDao.getUser(1)
    assertEquals(user, result)
}
```

---

## Comparison Table

| Feature | SQLite | Room |
|---------|--------|------|
| **Abstraction** | Low-level | High-level ORM-style layer |
| **Boilerplate** | High | Low |
| **SQL Validation** | Runtime | Compile-time |
| **Type Safety** | No | Yes |
| **CRUD Operations** | Manual ContentValues | Annotations |
| **Reactive (`Flow`/`LiveData`)** | No | Yes (via Room APIs) |
| **Coroutines Support** | No built-in | `suspend`/`Flow` APIs provided by Room (off main thread) |
| **Migrations** | Manual | Structured (with optional autoMigrations) |
| **Testing** | More boilerplate | Easier (in-memory / instrumented tests) |
| **Performance** | Fast | Fast (uses SQLite internally) |
| **Dependencies** | Built-in | Jetpack library |
| **Learning Curve** | SQL knowledge | Annotations + SQL |

## Code Comparison - Complete Example

**SQLite:**

```kotlin
class UserRepository(context: Context) {
    private val dbHelper = DatabaseHelper(context)

    fun insertUser(name: String, email: String): Long {
        val db = dbHelper.writableDatabase
        val values = ContentValues().apply {
            put("name", name)
            put("email", email)
        }
        return db.insert("users", null, values)
    }

    fun getAllUsers(): List<User> {
        val db = dbHelper.readableDatabase
        val cursor = db.rawQuery("SELECT * FROM users", null)
        val users = mutableListOf<User>()

        while (cursor.moveToNext()) {
            users.add(
                User(
                    id = cursor.getInt(0),
                    name = cursor.getString(1),
                    email = cursor.getString(2)
                )
            )
        }
        cursor.close()
        return users
    }
}
```

**Room:**

```kotlin
@Dao
interface UserDao {
    @Insert
    suspend fun insert(user: User): Long

    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>
}

class UserRepository(private val userDao: UserDao) {
    suspend fun insertUser(name: String, email: String): Long {
        return userDao.insert(User(name = name, email = email))
    }

    fun getAllUsers(): Flow<List<User>> = userDao.getAllUsers()
}
```

## Summary

**SQLite:**
- Low-level relational database
- Requires manual SQL query strings
- No compile-time validation
- Lots of boilerplate code
- Built into Android

**Room:**
- High-level ORM-style abstraction over SQLite (with limitations compared to full ORMs)
- Type-safe, annotation-based API
- Compile-time SQL and schema validation
- `LiveData`/`Flow` support
- Structured migrations (with optional autoMigrations for supported changes)
- Easier testing
- Less boilerplate
- Still uses SQLite internally

**Recommendation:** Use **Room** for most modern Android development. It provides better safety, less code, and easier maintenance while maintaining SQLite's performance.

---

## Follow-ups

- [[q-android-runtime-art--android--medium]]
- [[q-room-transactions-dao--android--medium]]

## References

- [Room Database](https://developer.android.com/training/data-storage/room)

## Related Questions

### Prerequisites / Concepts

- [[c-room]]

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Related (Medium)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--android--medium]] - Storage
- [[q-room-paging3-integration--android--medium]] - Storage
- [[q-room-type-converters-advanced--android--medium]] - Storage
- [[q-room-type-converters--android--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--android--hard]] - Storage
