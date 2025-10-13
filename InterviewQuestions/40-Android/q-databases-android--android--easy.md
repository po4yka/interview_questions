---
topic: android
tags:
  - android
  - android/data-storage
  - data-storage
  - database
  - realm
  - room
  - sqlite
difficulty: easy
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# Какие базы данных можно использовать в Android?

**English**: What databases can be used in Android?

## Answer (EN)
Android applications can use **three main database options**: **SQLite**, **Room**, and **Realm**.

## 1. SQLite

**Built-in relational database** for Android. Lightweight, serverless, self-contained.

**Characteristics:**
-  Built into Android
-  Requires manual SQL queries
-  Low-level API
-  More boilerplate code

**Example:**

```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(
    context,
    "app_database.db",
    null,
    1
) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS users")
        onCreate(db)
    }
}

// Insert
fun insertUser(name: String, email: String) {
    val db = dbHelper.writableDatabase
    val values = ContentValues().apply {
        put("name", name)
        put("email", email)
    }
    db.insert("users", null, values)
}

// Query
fun getUsers(): List<User> {
    val db = dbHelper.readableDatabase
    val cursor = db.rawQuery("SELECT * FROM users", null)
    val users = mutableListOf<User>()

    with(cursor) {
        while (moveToNext()) {
            val id = getInt(getColumnIndexOrThrow("id"))
            val name = getString(getColumnIndexOrThrow("name"))
            val email = getString(getColumnIndexOrThrow("email"))
            users.add(User(id, name, email))
        }
    }
    cursor.close()
    return users
}
```

**Pros:**
-  Built-in, no dependencies
-  Full SQL power
-  Lightweight

**Cons:**
-  Lots of boilerplate
-  No compile-time SQL validation
-  Manual cursor handling
-  No type safety

---

## 2. Room

**Abstraction layer over SQLite** from Android Jetpack. Recommended by Google.

**Characteristics:**
-  Type-safe database access
-  Compile-time SQL validation
-  LiveData/Flow support
-  Annotation-based

**Example:**

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)

// DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Int): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)
}

// Database
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// Setup
val db = Room.databaseBuilder(
    context,
    AppDatabase::class.java,
    "app_database"
).build()

// Usage
val userDao = db.userDao()

// Insert
viewModelScope.launch {
    userDao.insertUser(User(name = "John", email = "john@example.com"))
}

// Observe data
viewLifecycleOwner.lifecycleScope.launch {
    userDao.getAllUsers().collect { users ->
        // Update UI
    }
}
```

**Pros:**
-  Type-safe API
-  Compile-time SQL validation
-  Less boilerplate
-  LiveData/Flow integration
-  Automatic migrations
-  Coroutines support

**Cons:**
-  Annotation processing overhead
-  Learning curve
-  Still uses SQLite under the hood

---

## 3. Realm

**Modern mobile database** - object-oriented, fast, reactive.

**Characteristics:**
-  Fast performance
-  Reactive queries
-  Mobile-first design
-  Cloud sync support

**Example:**

```kotlin
// Model
open class User : RealmObject() {
    @PrimaryKey
    var id: Int = 0
    var name: String = ""
    var email: String = ""
}

// Setup
Realm.init(context)
val config = RealmConfiguration.Builder()
    .name("app.realm")
    .schemaVersion(1)
    .build()

Realm.setDefaultConfiguration(config)

// Insert
val realm = Realm.getDefaultInstance()
realm.executeTransaction {
    val user = it.createObject(User::class.java, 1)
    user.name = "John"
    user.email = "john@example.com"
}

// Query
val users = realm.where(User::class.java).findAll()

// Reactive queries
realm.where(User::class.java)
    .findAllAsync()
    .addChangeListener { results ->
        // Auto-updates when data changes
    }

// Close
realm.close()
```

**Pros:**
-  Very fast (faster than SQLite for some operations)
-  Object-oriented (no SQL)
-  Reactive queries
-  Cross-platform (iOS, Android, etc.)
-  Built-in encryption
-  Cloud sync (Realm Sync)

**Cons:**
-  External dependency
-  Larger library size
-  Proprietary format
-  Migration can be complex

**Dependencies:**

```kotlin
// build.gradle (project)
buildscript {
    dependencies {
        classpath "io.realm:realm-gradle-plugin:10.15.1"
    }
}

// build.gradle (app)
apply plugin: 'realm-android'
```

---

## Comparison Table

| Feature | SQLite | Room | Realm |
|---------|--------|------|-------|
| **Type** | Relational | Relational (ORM) | Object DB |
| **Boilerplate** | High | Low | Low |
| **Type Safety** |  No |  Yes |  Yes |
| **SQL Knowledge** | Required | Required | Not required |
| **Reactive** |  No |  Flow/LiveData |  Yes |
| **Performance** | Good | Good | Excellent |
| **Size** | Built-in | Small | Large |
| **Learning Curve** | Medium | Medium | Medium |
| **Cloud Sync** |  No |  No |  Yes |

## Which to Choose?

**Use SQLite if:**
- You need full control
- No external dependencies
- Simple use case

**Use Room if:**  **Recommended**
- Building modern Android app
- Want type safety and less boilerplate
- Using Jetpack components
- Need LiveData/Flow integration

**Use Realm if:**
- Need maximum performance
- Want reactive queries
- Cross-platform project
- Need cloud sync

## Migration Comparison

**SQLite:**
```kotlin
override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
    db.execSQL("ALTER TABLE users ADD COLUMN age INTEGER")
}
```

**Room:**
```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    }
}

Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .addMigrations(MIGRATION_1_2)
    .build()
```

**Realm:**
```kotlin
val config = RealmConfiguration.Builder()
    .schemaVersion(2)
    .migration { realm, oldVersion, newVersion ->
        if (oldVersion == 1L) {
            realm.schema.get("User")?.addField("age", Int::class.java)
        }
    }
    .build()
```

## Summary

**Three main databases for Android:**

1. **SQLite** - Built-in relational database, manual SQL
2. **Room** - Abstraction over SQLite, type-safe, recommended 
3. **Realm** - Modern object database, fast, reactive

**Recommendation:** Use **Room** for most Android projects. It provides the best balance of ease of use, performance, and integration with Android architecture components.

## Ответ (RU)
В Android приложениях можно использовать SQLite, Room и Realm. SQLite является встроенной реляционной базой данных Android. Room предоставляет слой абстракции поверх SQLite и облегчает работу с базой данных. Realm - современная база данных для мобильных приложений.


---

## Related Questions

### Related (Easy)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-sharedpreferences-definition--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Advanced (Harder)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage
- [[q-room-paging3-integration--room--medium]] - Storage
