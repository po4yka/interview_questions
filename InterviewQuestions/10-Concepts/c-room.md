---
id: "20251025-120100"
title: "Room Database / База данных Room"
aliases: ["Room", "Room Database", "Room Persistence Library", "База данных Room"]
summary: "Android persistence library that provides an abstraction layer over SQLite for fluent database access"
topic: "android"
subtopics: ["room", "database", "sqlite", "persistence", "jetpack"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["concept", "android", "room", "database", "sqlite", "persistence", "jetpack"]
---

# Room Database / База данных Room

## Summary (EN)

Room is a persistence library that provides an abstraction layer over SQLite to allow fluent database access while harnessing the full power of SQLite. Room handles much of the boilerplate code for working with databases, provides compile-time verification of SQL queries, and works seamlessly with LiveData, Flow, and RxJava for reactive data observation.

## Краткое описание (RU)

Room - это библиотека для сохранения данных, которая предоставляет слой абстракции над SQLite, позволяя удобный доступ к базе данных при сохранении всей мощности SQLite. Room обрабатывает большую часть шаблонного кода для работы с базами данных, обеспечивает проверку SQL-запросов на этапе компиляции и бесшовно работает с LiveData, Flow и RxJava для реактивного наблюдения за данными.

## Key Points (EN)

- Part of Android Jetpack Architecture Components
- Three main components: Database, Entity, and DAO (Data Access Object)
- Compile-time verification of SQL queries prevents runtime errors
- Automatic mapping between Kotlin/Java objects and database tables
- Built-in support for LiveData, Flow, and RxJava observables
- Type converters allow storing custom types
- Database migrations ensure smooth schema updates

## Ключевые моменты (RU)

- Часть Android Jetpack Architecture Components
- Три основных компонента: Database, Entity и DAO (Data Access Object)
- Проверка SQL-запросов на этапе компиляции предотвращает ошибки во время выполнения
- Автоматическое сопоставление между Kotlin/Java объектами и таблицами базы данных
- Встроенная поддержка LiveData, Flow и RxJava observables
- Type converters позволяют хранить пользовательские типы
- Миграции базы данных обеспечивают плавное обновление схемы

## Core Components

### Entity
Represents a table in the database.

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,

    @ColumnInfo(name = "user_name")
    val name: String,

    val email: String,

    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
)
```

### DAO (Data Access Object)
Defines methods for accessing the database.

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Long): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User): Long

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteUserById(userId: Long)
}
```

### Database
The main access point for the underlying SQLite database.

```kotlin
@Database(
    entities = [User::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
```

## Advanced Features

### Relationships
Define relationships between entities.

```kotlin
// One-to-Many relationship
data class UserWithPosts(
    @Embedded val user: User,
    @Relation(
        parentColumn = "id",
        entityColumn = "userId"
    )
    val posts: List<Post>
)

@Dao
interface UserDao {
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?
}
```

### Type Converters
Store custom types in the database.

```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }
}

@Database(
    entities = [User::class],
    version = 1
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    // ...
}
```

### Database Migration
Handle schema changes between versions.

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL(
            "ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0"
        )
    }
}

val db = Room.databaseBuilder(
    context,
    AppDatabase::class.java,
    "app_database"
)
    .addMigrations(MIGRATION_1_2)
    .build()
```

### Pre-populated Database

```kotlin
val db = Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .createFromAsset("database/initial_data.db")
    .build()
```

## Use Cases

### When to Use

- **Local data caching**: Cache network responses for offline access
- **User preferences**: Store complex user settings and preferences
- **Offline-first apps**: Primary data storage for offline functionality
- **Structured data**: Relational data requiring complex queries
- **Large datasets**: Store and query large amounts of structured data
- **Data synchronization**: Local storage for sync with remote server

### When to Avoid

- **Simple key-value storage**: Use DataStore or SharedPreferences instead
- **Very small datasets**: Overhead might not be justified
- **Unstructured data**: Consider using files or other storage methods
- **Real-time sync only**: If data never needs offline access
- **Sensitive data**: Encrypt database or use specialized secure storage

## Trade-offs

**Pros**:
- Compile-time SQL verification prevents errors
- Less boilerplate code compared to raw SQLite
- Seamless integration with coroutines and Flow
- Automatic LiveData/Flow updates on data changes
- Type-safe query builders reduce errors
- Built-in migration support
- Better testability with in-memory databases
- Support for complex relationships

**Cons**:
- Learning curve for developers new to Room
- Slightly more overhead than raw SQLite
- Migration complexity for schema changes
- Limited support for complex SQL operations
- Database must be created on background thread
- No built-in encryption (requires additional library)
- Compile-time processing increases build time

## Integration with Architecture Components

```kotlin
// Repository pattern
class UserRepository(private val userDao: UserDao) {
    val allUsers: Flow<List<User>> = userDao.getAllUsers()

    suspend fun insert(user: User) {
        userDao.insertUser(user)
    }

    suspend fun getUserById(id: Long): User? {
        return userDao.getUserById(id)
    }
}

// ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    val users: StateFlow<List<User>> = repository.allUsers
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun addUser(user: User) {
        viewModelScope.launch {
            repository.insert(user)
        }
    }
}
```

## Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun createDb() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(
            context,
            AppDatabase::class.java
        ).build()
        userDao = database.userDao()
    }

    @After
    fun closeDb() {
        database.close()
    }

    @Test
    fun insertAndGetUser() = runBlocking {
        val user = User(name = "Test User", email = "test@example.com")
        userDao.insertUser(user)

        val loaded = userDao.getUserById(1)
        assertEquals(user.name, loaded?.name)
    }
}
```

## Best Practices

- Use suspend functions with coroutines for database operations
- Return Flow or LiveData for reactive updates
- Implement repository pattern for separation of concerns
- Use @Transaction for operations that should be atomic
- Create database instance as singleton
- Always perform database operations on background thread
- Use migrations instead of destructive migration in production
- Enable exportSchema for version control of database schema
- Use indices for frequently queried columns

## Common Annotations

```kotlin
@Entity              // Marks a class as a database table
@PrimaryKey          // Marks a field as primary key
@ColumnInfo          // Customizes column name and properties
@Ignore              // Excludes field from database
@Embedded            // Flattens nested object into parent table
@Relation            // Defines relationship between entities
@Dao                 // Marks interface as Data Access Object
@Database            // Marks class as Room database
@Query               // Defines SQL query
@Insert              // Auto-generates insert method
@Update              // Auto-generates update method
@Delete              // Auto-generates delete method
@Transaction         // Marks method as transactional
@TypeConverter       // Defines type conversion method
```

## Related Concepts

- [[c-sqlite]]
- [[c-datastore]]
- [[c-repository-pattern]]
- [[c-livedata]]
- [[c-flow]]
- [[c-coroutines]]
- [[c-dao-pattern]]
- [[c-database-migration]]

## References

- [Android Developer Guide: Room Persistence Library](https://developer.android.com/training/data-storage/room)
- [Room Documentation](https://developer.android.com/jetpack/androidx/releases/room)
- [Codelabs: Room with a View](https://developer.android.com/codelabs/android-room-with-a-view-kotlin)
- [Room Database Migration](https://developer.android.com/training/data-storage/room/migrating-db-versions)
