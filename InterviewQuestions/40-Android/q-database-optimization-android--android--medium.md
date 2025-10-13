---
topic: android
tags:
  - android
  - database
  - room
  - performance
  - optimization
  - sql
  - indexing
difficulty: medium
status: draft
---

# Database Optimization Techniques in Android

**Сложность**: 🟡 Medium
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
What are the best practices and techniques for database optimization in Android applications?

## Answer (EN)
Database optimization is crucial for Android app performance, especially when dealing with large datasets or frequent database operations. Here are comprehensive optimization techniques:

#### 1. **Indexing Strategy**

```kotlin
@Entity(
    tableName = "users",
    indices = [
        Index(value = ["email"], unique = true),
        Index(value = ["last_name", "first_name"]),
        Index(value = ["created_at"])
    ]
)
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val email: String,
    val firstName: String,
    val lastName: String,
    val createdAt: Long
)
```

**Benefits:**
- Speeds up queries on indexed columns
- Unique indexes prevent duplicate data
- Composite indexes optimize multi-column queries

**Trade-offs:**
- Increases database size
- Slows down INSERT/UPDATE operations
- Choose indexes based on query patterns

#### 2. **Query Optimization**

```kotlin
@Dao
interface UserDao {
    // Bad: Returns all data
    @Query("SELECT * FROM users WHERE city = :city")
    fun getUsersByCity(city: String): List<User>

    // Good: Returns only needed columns
    @Query("SELECT id, name, email FROM users WHERE city = :city")
    fun getUserNamesByCity(city: String): List<UserNameEmail>

    // Good: Use LIMIT for pagination
    @Query("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    fun getUsersPaged(limit: Int, offset: Int): List<User>

    // Good: Use compiled statements
    @Query("SELECT * FROM users WHERE id IN (:userIds)")
    fun getUsersByIds(userIds: List<Long>): List<User>
}

data class UserNameEmail(
    val id: Long,
    val name: String,
    val email: String
)
```

#### 3. **Batch Operations**

```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(users: List<User>)

    @Update
    suspend fun updateAll(users: List<User>)

    @Delete
    suspend fun deleteAll(users: List<User>)

    @Transaction
    suspend fun updateUsersBatch(users: List<User>) {
        deleteAll(users)
        insertAll(users)
    }
}

// Usage
class UserRepository(private val userDao: UserDao) {
    suspend fun syncUsers(users: List<User>) {
        // Process in chunks to avoid memory issues
        users.chunked(1000).forEach { chunk ->
            userDao.insertAll(chunk)
        }
    }
}
```

#### 4. **Use Transactions**

```kotlin
@Database(entities = [User::class, Order::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun orderDao(): OrderDao
}

class OrderRepository(
    private val database: AppDatabase,
    private val userDao: UserDao,
    private val orderDao: OrderDao
) {
    // Wrap multiple operations in transaction
    suspend fun createOrderWithUser(user: User, order: Order) =
        database.withTransaction {
            val userId = userDao.insert(user)
            orderDao.insert(order.copy(userId = userId))
        }
}
```

#### 5. **Pagination with PagingSource**

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getUsersPaged(): PagingSource<Int, User>
}

class UserRepository(private val userDao: UserDao) {
    fun getUsersFlow(): Flow<PagingData<User>> {
        return Pager(
            config = PagingConfig(
                pageSize = 50,
                enablePlaceholders = false,
                prefetchDistance = 10
            ),
            pagingSourceFactory = { userDao.getUsersPaged() }
        ).flow
    }
}
```

#### 6. **Database Profiling and Monitoring**

```kotlin
// Enable query logging in debug builds
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {

    companion object {
        fun create(context: Context): AppDatabase {
            return Room.databaseBuilder(
                context.applicationContext,
                AppDatabase::class.java,
                "app-database"
            ).apply {
                if (BuildConfig.DEBUG) {
                    setQueryCallback({ sqlQuery, bindArgs ->
                        Log.d("RoomQuery", "Query: $sqlQuery, Args: $bindArgs")
                    }, Executors.newSingleThreadExecutor())
                }
            }.build()
        }
    }
}
```

#### 7. **Optimize Database Structure**

```kotlin
// Bad: Storing JSON as String
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String,
    val addressJson: String // JSON string
)

// Good: Normalized structure
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String
)

@Entity(
    tableName = "addresses",
    foreignKeys = [ForeignKey(
        entity = User::class,
        parentColumns = ["id"],
        childColumns = ["user_id"],
        onDelete = ForeignKey.CASCADE
    )]
)
data class Address(
    @PrimaryKey val id: Long,
    @ColumnInfo(name = "user_id") val userId: Long,
    val street: String,
    val city: String,
    val zipCode: String
)
```

#### 8. **Migration Strategies**

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Create index for better performance
        database.execSQL(
            "CREATE INDEX IF NOT EXISTS index_users_email ON users(email)"
        )
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Add column with default value
        database.execSQL(
            "ALTER TABLE users ADD COLUMN last_login INTEGER NOT NULL DEFAULT 0"
        )
    }
}
```

#### 9. **WAL (Write-Ahead Logging) Mode**

```kotlin
val db = Room.databaseBuilder(
    context,
    AppDatabase::class.java,
    "app-database"
)
    .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING) // Default in Room
    .build()
```

**Benefits:**
- Allows concurrent reads while writing
- Improves performance for read-heavy workloads
- Reduces lock contention

#### 10. **Avoid Main Thread Operations**

```kotlin
// Use Coroutines
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    val users = repository.getAllUsers()
        .cachedIn(viewModelScope)

    fun updateUser(user: User) {
        viewModelScope.launch {
            repository.updateUser(user)
        }
    }
}

// Use Flow for reactive updates
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsersFlow(): Flow<List<User>>
}
```

#### 11. **Vacuum and Optimize**

```kotlin
class DatabaseMaintenanceWorker(
    context: Context,
    params: WorkerParameters,
    private val database: AppDatabase
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            database.openHelper.writableDatabase.apply {
                // Rebuild database to reclaim space
                execSQL("VACUUM")
                // Analyze tables for query optimization
                execSQL("ANALYZE")
            }
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }
}
```

#### 12. **Cache Frequently Accessed Data**

```kotlin
class UserRepository(
    private val userDao: UserDao,
    private val userCache: UserCache
) {
    suspend fun getUserById(userId: Long): User? {
        // Check cache first
        userCache.get(userId)?.let { return it }

        // Load from database
        return userDao.getUserById(userId)?.also { user ->
            userCache.put(userId, user)
        }
    }
}

class UserCache {
    private val cache = LruCache<Long, User>(100)

    fun get(key: Long): User? = cache.get(key)
    fun put(key: Long, value: User) = cache.put(key, value)
    fun clear() = cache.evictAll()
}
```

### Performance Checklist

**Query Optimization:**
- [ ] Use projections (select only needed columns)
- [ ] Add appropriate indexes
- [ ] Use LIMIT for large result sets
- [ ] Avoid N+1 query problems
- [ ] Use compiled statements

**Database Structure:**
- [ ] Normalize data properly
- [ ] Use appropriate data types
- [ ] Add foreign key constraints
- [ ] Avoid storing large BLOBs

**Operations:**
- [ ] Use batch operations for multiple inserts/updates
- [ ] Wrap related operations in transactions
- [ ] Enable WAL mode
- [ ] Use pagination for large datasets

**Threading:**
- [ ] Never block the main thread
- [ ] Use coroutines or RxJava
- [ ] Implement proper error handling

**Monitoring:**
- [ ] Enable query logging in debug
- [ ] Profile database operations
- [ ] Monitor database size
- [ ] Schedule periodic VACUUM

---



## Ответ (RU)
# Вопрос (RU)
Каковы лучшие практики и техники оптимизации базы данных в Android-приложениях?

## Ответ (RU)
Оптимизация базы данных критически важна для производительности Android-приложений, особенно при работе с большими объемами данных или частых операциях с базой данных. Вот комплексные техники оптимизации:

#### 1. **Стратегия индексирования**

Индексы ускоряют запросы по индексированным колонкам, но увеличивают размер базы данных и замедляют операции INSERT/UPDATE. Выбирайте индексы на основе паттернов запросов.

#### 2. **Оптимизация запросов**

- Выбирайте только необходимые колонки
- Используйте LIMIT для пагинации
- Применяйте компилированные выражения
- Избегайте SELECT *

#### 3. **Пакетные операции**

Обрабатывайте множественные вставки/обновления одной операцией. Разбивайте большие наборы данных на части (chunks), чтобы избежать проблем с памятью.

#### 4. **Использование транзакций**

Оборачивайте связанные операции в транзакции для обеспечения атомарности и улучшения производительности.

#### 5. **Пагинация с PagingSource**

Используйте Paging 3 для эффективной загрузки больших списков данных с автоматической подгрузкой и кэшированием.

#### 6. **Профилирование и мониторинг**

Включайте логирование запросов в debug-сборках для анализа производительности и выявления узких мест.

#### 7. **Оптимизация структуры БД**

- Нормализуйте данные правильно
- Избегайте хранения JSON-строк
- Используйте внешние ключи
- Выбирайте подходящие типы данных

#### 8. **Стратегии миграции**

Создавайте индексы и оптимизируйте структуру во время миграций.

#### 9. **Режим WAL (Write-Ahead Logging)**

Позволяет одновременное чтение во время записи, улучшает производительность для read-heavy нагрузок.

#### 10. **Избегайте операций в главном потоке**

Используйте корутины или RxJava для асинхронных операций с базой данных.

#### 11. **VACUUM и оптимизация**

Периодически выполняйте VACUUM для освобождения места и ANALYZE для оптимизации планов запросов.

#### 12. **Кэширование часто используемых данных**

Используйте LruCache или другие механизмы кэширования для часто запрашиваемых данных.

### Чек-лист производительности

**Оптимизация запросов:**
- Используйте проекции
- Добавляйте соответствующие индексы
- Используйте LIMIT
- Избегайте проблем N+1 запросов

**Структура БД:**
- Правильно нормализуйте данные
- Используйте подходящие типы данных
- Добавляйте ограничения внешних ключей

**Операции:**
- Используйте пакетные операции
- Оборачивайте операции в транзакции
- Включайте режим WAL
- Используйте пагинацию

**Потоки:**
- Никогда не блокируйте главный поток
- Используйте корутины
- Реализуйте обработку ошибок

**Мониторинг:**
- Включайте логирование в debug
- Профилируйте операции
- Мониторьте размер БД
- Планируйте периодический VACUUM

---

## Related Questions

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Performance
- [[q-performance-optimization-android--android--medium]] - Performance
- [[q-build-optimization-gradle--gradle--medium]] - Performance
- [[q-app-startup-optimization--performance--medium]] - Performance
- [[q-baseline-profiles-optimization--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Performance
