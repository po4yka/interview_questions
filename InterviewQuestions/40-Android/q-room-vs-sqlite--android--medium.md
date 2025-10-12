---
topic: android
tags:
  - android
  - android/data-storage
  - comparison
  - database
  - orm
  - room
  - sqlite
difficulty: medium
status: draft
---

# В чем разница между Room & SQLite?

**English**: What is the difference between Room and SQLite?

## Answer (EN)
**SQLite** is a **low-level relational database** that requires **manual SQL queries**.

**Room** is a **wrapper/ORM (Object-Relational Mapping) layer over SQLite** that provides a **convenient API with annotations**, supports **LiveData and Flow**, and enables **automatic data migration**.

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
// - No compile-time validation
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
    // - Compile-time SQL validation
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Int): User?

    // Typo in table name would be caught at compile time!
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

**Room - Built-in Flow/LiveData:**

```kotlin
@Dao
interface UserDao {
    // - Automatically updates UI when data changes
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    // Or with LiveData
    @Query("SELECT * FROM users")
    fun getAllUsersLiveData(): LiveData<List<User>>
}

// In Fragment/Activity - automatic updates!
viewLifecycleOwner.lifecycleScope.launch {
    userDao.getAllUsers().collect { users ->
        adapter.submitList(users)  // UI updates automatically
    }
}
```

---

### 5. Type Safety

**SQLite - No type safety:**

```kotlin
// - Easy to make mistakes
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
    // - Compile-time type checking
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Int): User?  // Returns typed object
}

// Usage - type-safe!
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
// Need to mock SQLiteDatabase, SQLiteOpenHelper, Cursor, etc.
@Test
fun testGetUser() {
    val mockDb = mock(SQLiteDatabase::class.java)
    val mockCursor = mock(Cursor::class.java)

    whenever(mockDb.rawQuery(any(), any())).thenReturn(mockCursor)
    // ... lots of mocking
}
```

**Room - Easy:**

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
| **Abstraction** | Low-level | High-level ORM |
| **Boilerplate** | High | Low |
| **SQL Validation** | Runtime | Compile-time - |
| **Type Safety** | No | Yes - |
| **CRUD Operations** | Manual ContentValues | Annotations - |
| **Reactive (Flow/LiveData)** | No | Yes - |
| **Coroutines Support** | No | Yes - |
| **Migrations** | Manual | Structured - |
| **Testing** | Difficult | Easy - |
| **Performance** | Fast | Fast (same - uses SQLite) |
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
- High-level ORM wrapper over SQLite
- Type-safe, annotation-based API
- Compile-time SQL validation
- LiveData/Flow support
- Automatic migrations
- Easier testing
- Less boilerplate
- **Still uses SQLite internally**

**Recommendation:** Use **Room** for modern Android development. It provides better safety, less code, and easier maintenance while maintaining SQLite's performance.

## Ответ (RU)
SQLite – низкоуровневая реляционная база данных, требует SQL-запросов вручную. Room – надстройка над SQLite, предоставляет удобный API с аннотациями, поддерживает LiveData, Flow и автоматическую миграцию данных. Room упрощает работу с базой и делает код читаемым, но внутри все равно использует SQLite.

