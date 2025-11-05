---
id: kotlin-115
title: "Room Database with Coroutines and Flow / Room БД с корутинами и Flow"
aliases: ["Room Database with Coroutines and Flow, Room БД с корутинами и Flow"]

# Classification
topic: kotlin
subtopics: [android, coroutines, database]
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
related: [q-flow-basics--kotlin--medium, q-stateflow-sharedflow-android--kotlin--medium, q-viewmodel-coroutines-lifecycle--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [android, coroutines, database, difficulty/medium, flow, kotlin, room]
date created: Sunday, October 12th 2025, 3:39:19 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---
# Вопрос (RU)
> Как использовать Room БД с корутинами и Flow? Объясните suspend функции в DAO, Flow для реактивных запросов, обработку транзакций и лучшие практики.

---

# Question (EN)
> How to use Room database with coroutines and Flow? Explain suspend functions in DAO, Flow for reactive queries, transaction handling, and best practices.

## Ответ (RU)

Room предоставляет первоклассную поддержку корутин и Flow для работы с БД.

### Основные Возможности

- **Suspend функции**: Для одноразовых операций
- **Flow**: Для реактивных запросов (автообновление)
- **Транзакции**: @Transaction или withTransaction
- **Диспетчеры**: Room автоматически использует IO dispatcher

### Пример

```kotlin
@Dao
interface UserDao {
    // Flow - автоматическое обновление
    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>
    
    // Suspend - одноразовая операция
    @Insert
    suspend fun insert(user: User)
}
```

---

## Answer (EN)

Room provides first-class support for coroutines and Flow, making database operations seamless in Android apps.

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
    fun loadUsers() {
        viewModelScope.launch {
            val users = userDao.getAllUsers()
            _users.value = users
        }
    }
    
    fun insertUser(user: User) {
        viewModelScope.launch {
            userDao.insertUser(user)
        }
    }
    
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users = _users.asStateFlow()
}
```

### Reactive Queries with Flow

```kotlin
// DAO with Flow
@Dao
interface UserDao {
    // Returns Flow - automatically emits when data changes
    @Query("SELECT * FROM users")
    fun observeAllUsers(): Flow<List<User>>
    
    @Query("SELECT * FROM users WHERE id = :userId")
    fun observeUser(userId: Int): Flow<User?>
    
    @Query("SELECT * FROM users WHERE name LIKE :query")
    fun searchUsers(query: String): Flow<List<User>>
}

// ViewModel - no manual refresh needed!
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
                    // Automatically updates when DB changes!
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
    // Single transaction
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserWithDetails(userId: Int): UserWithDetails
    
    // Manual transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        // Room handles transaction automatically for @Transaction
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
    
    // Custom transaction
    suspend fun performTransaction() {
        withTransaction {
            // All operations in one transaction
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
    
    // Expose Flow from DAO
    val allUsers: Flow<List<User>> = userDao.observeAllUsers()
    
    // Suspend functions for one-off operations
    suspend fun insertUser(user: User) {
        withContext(Dispatchers.IO) {
            userDao.insertUser(user)
        }
    }
    
    suspend fun deleteUser(user: User) {
        withContext(Dispatchers.IO) {
            userDao.deleteUser(user)
        }
    }
    
    // Combine multiple sources
    fun getUserWithCache(userId: Int): Flow<User?> = flow {
        // Emit cached data first
        emit(userDao.getUserById(userId))
        
        // Then fetch from network
        try {
            val networkUser = fetchUserFromNetwork(userId)
            userDao.insertUser(networkUser)
            emit(networkUser)
        } catch (e: Exception) {
            // Handle error
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

1. **How to handle database migrations with coroutines?**
2. **When to use Flow vs suspend in DAO?**
3. **How to test Room with coroutines?**
4. **How to handle errors in Room operations?**

---

## References

- [Room with Coroutines](https://developer.android.com/training/data-storage/room/async-queries)

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
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow
### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-flow-testing-advanced--kotlin--hard]] - Flow
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

