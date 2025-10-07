---
topic: android
tags:
  - android
  - android/data-storage
  - architecture-components
  - data-storage
  - database
  - orm
  - room
  - sqlite
difficulty: easy
status: draft
---

# Что из себя представляет библиотека Room?

**English**: What is the Room library?

## Answer

**Room** is a **database management library** that serves as an **abstraction layer over SQLite** for convenient database access.

This library is part of **Android Architecture Components** introduced by Google to simplify development of stable and performant applications.

**Key Benefits:**

Room provides abstraction over SQLite with the goal of:
- 🛡️ **Type safety** - compile-time SQL verification
- 📝 **Less boilerplate** - reduces manual code
- 🔗 **Easy integration** with LiveData, Flow, and RxJava
- ✅ **SQL query validation** at compile time
- 🏗️ **Architecture support** - works with MVVM, Clean Architecture

**Three Main Components:**

**1. Database:**

```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**2. Entity:**

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,

    @ColumnInfo(name = "user_name")
    val name: String,

    val email: String,

    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
)
```

**3. DAO (Data Access Object):**

```kotlin
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

    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteUserById(userId: Int)
}
```

**Complete Example:**

```kotlin
// build.gradle
dependencies {
    implementation "androidx.room:room-runtime:2.6.0"
    implementation "androidx.room:room-ktx:2.6.0"
    ksp "androidx.room:room-compiler:2.6.0"
}

// Database setup
val db = Room.databaseBuilder(
    context.applicationContext,
    AppDatabase::class.java,
    "app-database"
).build()

// Usage in ViewModel
class UserViewModel(private val userDao: UserDao) : ViewModel() {
    val allUsers: Flow<List<User>> = userDao.getAllUsers()

    fun addUser(name: String, email: String) {
        viewModelScope.launch {
            val user = User(name = name, email = email)
            userDao.insertUser(user)
        }
    }

    fun deleteUser(user: User) {
        viewModelScope.launch {
            userDao.deleteUser(user)
        }
    }
}
```

**Room vs Raw SQLite:**

| Feature | Room | Raw SQLite |
|---------|------|------------|
| **Boilerplate** | Minimal | Extensive |
| **Type safety** | Yes | No |
| **Compile-time checks** | Yes | No |
| **LiveData/Flow** | Built-in | Manual |
| **Migrations** | Automated | Manual |
| **SQL validation** | Compile-time | Runtime |

**Advanced Features:**

```kotlin
// Relations
@Entity
data class Library(
    @PrimaryKey val libraryId: Int,
    val name: String
)

@Entity
data class Book(
    @PrimaryKey val bookId: Int,
    val title: String,
    val libraryId: Int  // Foreign key
)

// One-to-many relationship
data class LibraryWithBooks(
    @Embedded val library: Library,
    @Relation(
        parentColumn = "libraryId",
        entityColumn = "libraryId"
    )
    val books: List<Book>
)

@Dao
interface LibraryDao {
    @Transaction
    @Query("SELECT * FROM Library")
    fun getLibrariesWithBooks(): Flow<List<LibraryWithBooks>>
}
```

**Database Migration:**

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    }
}

val db = Room.databaseBuilder(context, AppDatabase::class.java, "app-db")
    .addMigrations(MIGRATION_1_2)
    .build()
```

**Summary:**

- **Room**: Abstraction layer over SQLite
- **Part of**: Android Architecture Components
- **Provides**: Type safety, less boilerplate, compile-time validation
- **Main components**: Database, Entity, DAO
- **Integration**: LiveData, Flow, RxJava, Coroutines
- **Benefits**: Clean API, reduced errors, easier testing

## Ответ

Room — это библиотека управления базами данных, которая служит абстрактным слоем над SQLite для удобного доступа к базе данных. Эта библиотека является частью Android Architecture Components, представленных Google для упрощения разработки стабильных и производительных приложений. Room предоставляет абстракцию над SQLite с целью обеспечения более чистого доступа к базе данных, сохраняя при этом полную мощь SQLite. Основные возможности: типобезопасность, уменьшение шаблонного кода, легкая интеграция с LiveData и RxJava и проверка SQL-запросов во время компиляции. Основные компоненты: Database, Entity и DAO.

