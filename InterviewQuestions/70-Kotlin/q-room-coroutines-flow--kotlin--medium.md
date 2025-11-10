---
id: kotlin-115
title: "Room Database with Coroutines and Flow / Room БД с корутинами и Flow"
aliases: ["Room Database with Coroutines and Flow", "Room БД с корутинами и Flow"]

# Classification
topic: kotlin
subtopics: [coroutines, database]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Room Coroutines Flow Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-room, c-flow, q-stateflow-sharedflow-android--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [android, coroutines, database, difficulty/medium, flow, kotlin, room]
---
# Вопрос (RU)
> Как использовать Room БД с корутинами и `Flow`? Объясните suspend функции в DAO, `Flow` для реактивных запросов, обработку транзакций и лучшие практики.

---

# Question (EN)
> How to use Room database with coroutines and `Flow`? Explain suspend functions in DAO, `Flow` for reactive queries, transaction handling, and best practices.

## Ответ (RU)

Room предоставляет первоклассную поддержку корутин и `Flow` для асинхронной и реактивной работы с БД в Android.

### Базовая работа с suspend-функциями Room

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val email: String
)

// DAO с suspend-функциями
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Int): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("DELETE FROM users")
    suspend fun deleteAll()
}

// Использование во ViewModel
class UserViewModel(private val userDao: UserDao) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            val usersFromDb = userDao.getAllUsers()
            _users.value = usersFromDb
        }
    }

    fun insertUser(user: User) {
        viewModelScope.launch {
            userDao.insertUser(user)
            // При использовании `Flow` обычно нет необходимости вручную обновлять список
        }
    }
}
```

Примечание: suspend-вызовы DAO Room выполняет вне главного потока с помощью своих исполнителей, поэтому обычно не требуется оборачивать их в `withContext(Dispatchers.IO)`.

### Реактивные запросы с `Flow`

```kotlin
// DAO с Flow
@Dao
interface UserDao {
    // Возвращает Flow, который повторно выполняет запрос и эмитит значения при изменениях таблицы users
    @Query("SELECT * FROM users")
    fun observeAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :userId")
    fun observeUser(userId: Int): Flow<User?>

    @Query("SELECT * FROM users WHERE name LIKE :query")
    fun searchUsers(query: String): Flow<List<User>>
}

// ViewModel — UI автоматически обновляется при изменениях в БД
class UserViewModel(private val userDao: UserDao) : ViewModel() {
    val allUsers: Flow<List<User>> = userDao.observeAllUsers()

    fun searchUsers(query: String): Flow<List<User>> {
        return userDao.searchUsers("%$query%")
    }
}

// Fragment — сбор Flow с учётом жизненного цикла
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.allUsers.collect { users ->
                    // Автоматическое обновление при изменениях в БД
                    updateUserList(users)
                }
            }
        }
    }

    private fun updateUserList(users: List<User>) {}
}
```

### Обработка транзакций (Transaction Handling)

```kotlin
@Dao
interface UserDao {
    // Relations + @Transaction для атомарной и согласованной загрузки связанных данных
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserWithDetails(userId: Int): UserWithDetails

    // Объединение нескольких операций в одной транзакции
    @Transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        insertUser(user)
        insertPosts(posts)
    }

    @Insert
    suspend fun insertUser(user: User)

    @Insert
    suspend fun insertPosts(posts: List<Post>)
}

// База данных
@Database(entities = [User::class, Post::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    // Пользовательская транзакция с withTransaction
    suspend fun performTransaction() {
        withTransaction {
            // Все операции выполняются атомарно
            userDao().insertUser(User(1, "Name", "email"))
            userDao().deleteAll()
        }
    }
}

data class Post(
    @PrimaryKey val id: Int,
    val userId: Int,
    val content: String
)

data class UserWithDetails(
    @Embedded val user: User,
    @Relation(
        parentColumn = "id",
        entityColumn = "userId"
    )
    val posts: List<Post>
)
```

### Лучшие практики (Best Practices)

```kotlin
// Repository pattern
class UserRepository(private val userDao: UserDao) {

    // Отдаём Flow напрямую из DAO для реактивного UI
    val allUsers: Flow<List<User>> = userDao.observeAllUsers()

    // Suspend-функции для одноразовых операций; Room сам управляет потоками для suspend DAO
    suspend fun insertUser(user: User) {
        userDao.insertUser(user)
    }

    suspend fun deleteUser(user: User) {
        userDao.deleteUser(user)
    }

    // Пример объединения источников: cache-then-network
    fun getUserWithCache(userId: Int): Flow<User?> = flow {
        // Сначала отдаем данные из кэша (Room)
        emit(userDao.getUserById(userId))

        // Затем пробуем получить данные из сети и обновить БД
        try {
            val networkUser = fetchUserFromNetwork(userId)
            userDao.insertUser(networkUser)
            emit(networkUser)
        } catch (e: Exception) {
            // Обработка ошибки (лог, fallback и т.д.)
        }
    }

    private suspend fun fetchUserFromNetwork(userId: Int): User {
        delay(1000)
        return User(userId, "Network User", "email@example.com")
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

    fun addUser(name: String, email: String) {
        viewModelScope.launch {
            repository.insertUser(
                User(
                    id = System.currentTimeMillis().toInt(),
                    name = name,
                    email = email
                )
            )
        }
    }
}
```

Кратко:
- Используйте suspend-функции в DAO для одноразовых операций.
- Используйте `Flow` для реактивных запросов и автоматических обновлений UI.
- Применяйте `@Transaction` и `withTransaction` для атомарности.
- Инкапсулируйте доступ к БД в репозитории и комбинируйте Room с сетью по необходимости.

---

## Answer (EN)

Room provides first-class support for coroutines and `Flow`, making async and reactive database operations straightforward in Android apps.

### Basic Room with Suspend Functions

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val email: String
)

// DAO with suspend functions
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Int): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("DELETE FROM users")
    suspend fun deleteAll()
}

// Usage in ViewModel
class UserViewModel(private val userDao: UserDao) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            val usersFromDb = userDao.getAllUsers()
            _users.value = usersFromDb
        }
    }

    fun insertUser(user: User) {
        viewModelScope.launch {
            userDao.insertUser(user)
            // Optionally reload or rely on a Flow-backed source instead of manual refresh
        }
    }
}
```

Note: Room executes suspend DAO calls off the main thread using its own executors, so you generally do not need to wrap them in `withContext(Dispatchers.IO)`.

### Reactive Queries with `Flow`

```kotlin
// DAO with Flow
@Dao
interface UserDao {
    // Returns Flow that re-runs the query and emits whenever "users" table changes
    @Query("SELECT * FROM users")
    fun observeAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :userId")
    fun observeUser(userId: Int): Flow<User?>

    @Query("SELECT * FROM users WHERE name LIKE :query")
    fun searchUsers(query: String): Flow<List<User>>
}

// ViewModel - no manual refresh needed
class UserViewModel(private val userDao: UserDao) : ViewModel() {
    // Automatically updates when database changes
    val allUsers: Flow<List<User>> = userDao.observeAllUsers()

    fun searchUsers(query: String): Flow<List<User>> {
        return userDao.searchUsers("%$query%")
    }
}

// Fragment - reactive UI
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.allUsers.collect { users ->
                    // Automatically updates when DB changes
                    updateUserList(users)
                }
            }
        }
    }

    private fun updateUserList(users: List<User>) {}
}
```

### Transaction Handling

```kotlin
@Dao
interface UserDao {
    // Relations + @Transaction to load related data atomically & consistently
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserWithDetails(userId: Int): UserWithDetails

    // Wrap multiple operations in a single transaction
    @Transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        insertUser(user)
        insertPosts(posts)
    }

    @Insert
    suspend fun insertUser(user: User)

    @Insert
    suspend fun insertPosts(posts: List<Post>)
}

// Database class
@Database(entities = [User::class, Post::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    // Custom transaction using Room's withTransaction extension
    suspend fun performTransaction() {
        withTransaction {
            // All operations in one atomic transaction
            userDao().insertUser(User(1, "Name", "email"))
            userDao().deleteAll()
        }
    }
}

data class Post(
    @PrimaryKey val id: Int,
    val userId: Int,
    val content: String
)

data class UserWithDetails(
    @Embedded val user: User,
    @Relation(
        parentColumn = "id",
        entityColumn = "userId"
    )
    val posts: List<Post>
)
```

### Best Practices

```kotlin
// Repository pattern
class UserRepository(private val userDao: UserDao) {

    // Expose Flow directly from DAO for reactive UI
    val allUsers: Flow<List<User>> = userDao.observeAllUsers()

    // Suspend functions for one-off operations; Room handles threading for suspend DAO calls
    suspend fun insertUser(user: User) {
        userDao.insertUser(user)
    }

    suspend fun deleteUser(user: User) {
        userDao.deleteUser(user)
    }

    // Combine multiple sources: simple cache-then-network pattern
    fun getUserWithCache(userId: Int): Flow<User?> = flow {
        // Emit cached data first (may call suspend Room function inside flow)
        emit(userDao.getUserById(userId))

        // Then fetch from network and update DB
        try {
            val networkUser = fetchUserFromNetwork(userId)
            userDao.insertUser(networkUser)
            emit(networkUser)
        } catch (e: Exception) {
            // Handle error (e.g., emit(null) or log)
        }
    }

    private suspend fun fetchUserFromNetwork(userId: Int): User {
        delay(1000)
        return User(userId, "Network User", "email@example.com")
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

    fun addUser(name: String, email: String) {
        viewModelScope.launch {
            repository.insertUser(
                User(
                    id = System.currentTimeMillis().toInt(),
                    name = name,
                    email = email
                )
            )
        }
    }
}
```

---

## Follow-ups

1. How to handle database migrations with coroutines and ensure queries remain non-blocking?
2. When to use `Flow` vs `suspend` functions in DAO for different use cases?
3. How to test Room DAOs and repositories that use coroutines and `Flow`?
4. How to handle and propagate errors from Room operations using `Flow` and structured concurrency?
5. How to integrate Room `Flow` streams with UI state holders like `StateFlow` and `SharedFlow`?

---

## References

- [Room with Coroutines](https://developer.android.com/training/data-storage/room/async-queries)
- [[c-room]]
- [[c-flow]]

---

## Related Questions

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - Flow

### Related (Medium)
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Coroutines
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs `LiveData`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-flow-testing-advanced--kotlin--hard]] - Flow
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction
