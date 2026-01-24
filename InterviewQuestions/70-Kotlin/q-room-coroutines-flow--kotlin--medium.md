---
anki_cards:
- slug: q-room-coroutines-flow--kotlin--medium-0-en
  language: en
  anki_id: 1768326290832
  synced_at: '2026-01-23T17:03:51.473127'
- slug: q-room-coroutines-flow--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326290857
  synced_at: '2026-01-23T17:03:51.474406'
---
# Question (EN)
> How to use `Room` database with coroutines and `Flow`? Explain suspend functions in DAO, `Flow` for reactive queries, transaction handling, and best practices.

## Ответ (RU)

`Room` предоставляет первоклассную поддержку корутин и `Flow` для асинхронной и реактивной работы с БД в Android.

### Базовая Работа С Suspend-функциями Room

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
            // При использовании Flow-стримов из DAO обычно нет необходимости вручную обновлять список
        }
    }
}
```

Примечание: suspend-вызовы DAO `Room` выполняет вне главного потока с помощью своих внутренних исполнителей (при использовании соответствующих зависимостей `Room`), поэтому обычно не требуется оборачивать их в `withContext(Dispatchers.IO)`.

### Реактивные Запросы С `Flow`

```kotlin
// DAO с Flow
@Dao
interface UserDao {
    // Возвращает Flow, который повторно выполняет запрос и эмитит значения при изменениях таблицы users
    // Flow от Room является холодным: запрос выполняется при коллекции и заново при каждом новом коллекторе.
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

### Обработка Транзакций (Transaction Handling)

```kotlin
@Dao
interface UserDao {
    // Relations + @Transaction для атомарной и согласованной загрузки связанных данных.
    // Если пользователь не найден, функция должна возвращать null (UserWithDetails?).
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserWithDetails(userId: Int): UserWithDetails?

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

    // Пользовательская транзакция с withTransaction из room-ktx (suspend-расширение для RoomDatabase)
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

### Лучшие Практики (Best Practices)

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

    // Упрощённый пример cache-then-network.
    // Обратите внимание: этот Flow холодный и при каждом новом коллекторе заново выполнит запрос БД и сети.
    // Для настоящего "кэш = Room" обычно наблюдают Flow из DAO и отдельно триггерят обновление из сети.
    fun getUserWithCache(userId: Int): Flow<User?> = flow {
        // Сначала отдаём данные из кэша (Room)
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
                    // В реальном коде предпочитайте autoGenerate или надёжную генерацию идентификатора.
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
- Используйте `Flow` для реактивных запросов и автоматических обновлений UI; `Room` переисполняет запрос при изменениях соответствующих таблиц.
- Применяйте `@Transaction` и `withTransaction` для атомарности.
- Инкапсулируйте доступ к БД в репозитории и комбинируйте `Room` с сетью по необходимости.

---

## Answer (EN)

`Room` provides first-class support for coroutines and `Flow`, making async and reactive database operations straightforward in Android apps.

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
            // Typically, when using DAO Flows, you don't need to manually refresh the list.
        }
    }
}
```

Note: `Room` executes suspend DAO calls off the main thread using its own executors (with the appropriate `Room` dependencies), so you generally do not need to wrap them in `withContext(Dispatchers.IO)`.

### Reactive Queries with `Flow`

```kotlin
// DAO with Flow
@Dao
interface UserDao {
    // Returns a Flow that re-runs the query and emits whenever the "users" table changes.
    // Room Flows are cold: the query runs when collected and is re-run per active collector.
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
    // Relations + @Transaction to load related data atomically & consistently.
    // If the user does not exist, this should return null (UserWithDetails?).
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserWithDetails(userId: Int): UserWithDetails?

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

    // Custom transaction using Room's withTransaction extension from room-ktx
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

    // Simplified cache-then-network example.
    // Note: this Flow is cold and will perform the DB and network calls per collector.
    // In a typical Room-as-cache setup, you observe a DAO Flow and trigger network refresh separately.
    fun getUserWithCache(userId: Int): Flow<User?> = flow {
        // Emit cached data first (Room)
        emit(userDao.getUserById(userId))

        // Then fetch from network and update DB
        try {
            val networkUser = fetchUserFromNetwork(userId)
            userDao.insertUser(networkUser)
            emit(networkUser)
        } catch (e: Exception) {
            // Handle error (e.g., log or emit a separate error signal)
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
                    // In real apps prefer autoGenerate or a robust ID generation strategy.
                    id = System.currentTimeMillis().toInt(),
                    name = name,
                    email = email
                )
            )
        }
    }
}
```

In short:
- Use suspend functions in DAO for one-off operations.
- Use `Flow` for reactive queries and automatic UI updates; `Room` re-runs the query when relevant tables change.
- Use `@Transaction` and `withTransaction` for atomic operations.
- Encapsulate DB access in a repository and combine `Room` with network as needed.

---

## Дополнительные Вопросы (RU)

1. Как безопасно выполнять миграции `Room` с использованием корутин, чтобы операции чтения/записи оставались неблокирующими?
2. В каких случаях предпочтительнее использовать `Flow` в DAO, а в каких — только suspend-функции для одноразовых запросов?
3. Как тестировать DAO и репозитории `Room`, которые используют корутины и `Flow` (например, с `runTest` и `TestDispatcher`)?
4. Как обрабатывать и пробрасывать ошибки при работе с `Room` через `Flow` и структурированную конкуррентность?
5. Как интегрировать `Flow` из `Room` с `StateFlow`/`SharedFlow` во `ViewModel` для управления состоянием UI?

---

## Follow-ups

1. How to safely perform `Room` migrations with coroutines so that reads/writes remain non-blocking?
2. In which scenarios should you prefer `Flow` in DAO vs only suspend functions for one-shot queries?
3. How to test `Room` DAOs and repositories using coroutines and `Flow` (e.g., with `runTest` and `TestDispatcher`)?
4. How to handle and propagate errors from `Room` when using `Flow` and structured concurrency?
5. How to integrate `Room` `Flow` streams with `StateFlow`/`SharedFlow` in `ViewModel` for UI state management?

---

## Ссылки (RU)

- [Room с корутинами](https://developer.android.com/training/data-storage/room/async-queries)
---

## References

- [Room with Coroutines](https://developer.android.com/training/data-storage/room/async-queries)
---

## Связанные Вопросы (RU)

### База (проще)
- [[q-kotlin-flow-basics--kotlin--medium]] - Введение в `Flow`

### Связанные (Medium)
- [[q-catch-operator-flow--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Операторы `map`/`filter`
- [[q-channel-flow-comparison--kotlin--medium]] - Каналы и `Flow`
- [[q-hot-cold-flows--kotlin--medium]] - Горячие и холодные `Flow`
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`

### Продвинутое (Hard)
- [[q-testing-flow-operators--kotlin--hard]] - Тестирование операторов `Flow`
- [[q-flowon-operator-context-switching--kotlin--hard]] - `flowOn` и переключение контекстов

---

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

### Related (Medium)
- [[q-catch-operator-flow--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
