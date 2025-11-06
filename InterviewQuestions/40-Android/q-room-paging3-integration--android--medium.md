---
id: android-242
title: "Room Paging3 Integration / Интеграция Room с Paging3"
aliases: ["Room Paging3 Integration", "Интеграция Room с Paging3"]
topic: android
subtopics: [architecture-mvvm, room, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-room-library-definition--android--easy, q-room-transactions-dao--android--medium]
sources: []
created: 2025-10-15
updated: 2025-01-27
tags: [android/architecture-mvvm, android/room, android/ui-compose, database, difficulty/medium, offline-first, pagination, paging3]
---

# Вопрос (RU)

> Как интегрировать Room с Paging 3? Реализуйте источник данных из Room и обработку RemoteMediator для офлайн-first архитектуры с сетью и базой данных.

# Question (EN)

> How to integrate Room with Paging 3? Implement Room database source and handle RemoteMediator for offline-first architecture with network and database paging.

## Ответ (RU)

**Paging 3** — библиотека пагинации, интегрируемая с [[c-room]] для эффективной загрузки больших наборов данных. Поддерживает локальную пагинацию БД и офлайн-first архитектуру (сеть + БД) через **RemoteMediator**.

### Базовый PagingSource

Room автоматически создаёт `PagingSource` из DAO запросов:

```kotlin
@Dao
interface UserDao {
    // ✅ Room создаёт PagingSource автоматически
    @Query("SELECT * FROM users ORDER BY createdAt DESC")
    fun getUsersPaged(): PagingSource<Int, User>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)
}

// Repository
class UserRepository(private val userDao: UserDao) {
    fun getUsersPaged(): Flow<PagingData<User>> = Pager(
        config = PagingConfig(
            pageSize = 20,              // ✅ Элементов на страницу
            prefetchDistance = 5,       // ✅ Предзагрузка за 5 элементов до конца
            enablePlaceholders = false  // ❌ Без null-заполнителей
        ),
        pagingSourceFactory = { userDao.getUsersPaged() }
    ).flow
}

// ViewModel
class UserViewModel(repository: UserRepository) : ViewModel() {
    val users: Flow<PagingData<User>> = repository.getUsersPaged()
        .cachedIn(viewModelScope)  // ✅ Кэш для переживания rotation
}
```

### UI (Compose)

```kotlin
@Composable
fun UserListScreen(viewModel: UserViewModel) {
    val users = viewModel.users.collectAsLazyPagingItems()

    LazyColumn {
        items(users.itemCount) { index ->
            users[index]?.let { UserItem(it) }
        }

        // ✅ Обработка LoadState
        when (users.loadState.refresh) {
            is LoadState.Loading -> item { CircularProgressIndicator() }
            is LoadState.Error -> item {
                ErrorItem(onRetry = { users.retry() })
            }
            else -> {}
        }
    }
}
```

### RemoteMediator (Offline-First)

**RemoteMediator** загружает данные из сети и кэширует в Room:

```kotlin
// ✅ Remote Keys для отслеживания состояния пагинации
@Entity(tableName = "user_remote_keys")
data class UserRemoteKeys(
    @PrimaryKey val userId: Long,
    val prevKey: Int?,
    val nextKey: Int?
)

@OptIn(ExperimentalPagingApi::class)
class UserRemoteMediator(
    private val apiService: UserApiService,
    private val database: AppDatabase
) : RemoteMediator<Int, User>() {

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, User>
    ): MediatorResult = try {
        val page = when (loadType) {
            LoadType.REFRESH -> 1
            LoadType.PREPEND -> return MediatorResult.Success(true)
            LoadType.APPEND -> {
                val remoteKeys = getRemoteKeyForLastItem(state)
                remoteKeys?.nextKey
                    ?: return MediatorResult.Success(true)
            }
        }

        val apiResponse = apiService.getUsers(page, state.config.pageSize)
        val endOfPaginationReached = apiResponse.isEmpty()

        // ✅ Атомарная транзакция для вставки данных и ключей
        database.withTransaction {
            if (loadType == LoadType.REFRESH) {
                database.userRemoteKeysDao().clearRemoteKeys()
                database.userDao().clearAllUsers()
            }

            val prevKey = if (page == 1) null else page - 1
            val nextKey = if (endOfPaginationReached) null else page + 1

            val keys = apiResponse.map {
                UserRemoteKeys(it.id, prevKey, nextKey)
            }
            val users = apiResponse.map { it.toEntity() }

            database.userRemoteKeysDao().insertAll(keys)
            database.userDao().insertUsers(users)
        }

        MediatorResult.Success(endOfPaginationReached)
    } catch (e: Exception) {
        MediatorResult.Error(e)
    }

    private suspend fun getRemoteKeyForLastItem(
        state: PagingState<Int, User>
    ): UserRemoteKeys? {
        return state.pages.lastOrNull { it.data.isNotEmpty() }
            ?.data?.lastOrNull()
            ?.let { database.userRemoteKeysDao().getRemoteKeys(it.id) }
    }
}
```

### Использование RemoteMediator

```kotlin
class UserRepository(
    private val apiService: UserApiService,
    private val database: AppDatabase
) {
    @OptIn(ExperimentalPagingApi::class)
    fun getUsersWithRemoteMediator() = Pager(
        config = PagingConfig(pageSize = 20),
        remoteMediator = UserRemoteMediator(apiService, database),
        pagingSourceFactory = { database.userDao().getUsersPaged() }
    ).flow
}
```

### Best Practices

1. **cachedIn(viewModelScope)** — кэш данных для переживания rotation
2. **PagingConfig**: pageSize 20-50, prefetchDistance 5-10, initialLoadSize 2-3x pageSize
3. **LoadState** — обработка состояний загрузки и ошибок
4. **RemoteMediator** — офлайн-first с кэшированием в Room
5. **DiffUtil** — эффективные обновления `RecyclerView`
6. **Remote Keys** — отдельная таблица для состояния пагинации
7. **withTransaction** — атомарность операций
8. **Retry mechanism** — восстановление после ошибок

### Ключевые Моменты

- **PagingSource**: автоматическая пагинация из Room запросов
- **RemoteMediator**: офлайн-first с сеть + БД
- **LoadState**: обработка loading/error/success
- **collectAsLazyPagingItems()**: интеграция с Compose LazyColumn
- **Трансформации**: filter, map, insertSeparators
- **Производительность**: эффективное использование памяти

Используйте **PagingSource** для простой локальной пагинации, **RemoteMediator** для офлайн-first приложений с кэшированием сетевых данных.

---

## Answer (EN)

**Paging 3** is a pagination library that integrates with [[c-room]] to efficiently load large datasets. Supports local database paging and offline-first architecture (network + database) through **RemoteMediator**.

### Basic PagingSource

Room automatically creates `PagingSource` from DAO queries:

```kotlin
@Dao
interface UserDao {
    // ✅ Room creates PagingSource automatically
    @Query("SELECT * FROM users ORDER BY createdAt DESC")
    fun getUsersPaged(): PagingSource<Int, User>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)
}

// Repository
class UserRepository(private val userDao: UserDao) {
    fun getUsersPaged(): Flow<PagingData<User>> = Pager(
        config = PagingConfig(
            pageSize = 20,              // ✅ Items per page
            prefetchDistance = 5,       // ✅ Prefetch 5 items before end
            enablePlaceholders = false  // ❌ No null placeholders
        ),
        pagingSourceFactory = { userDao.getUsersPaged() }
    ).flow
}

// ViewModel
class UserViewModel(repository: UserRepository) : ViewModel() {
    val users: Flow<PagingData<User>> = repository.getUsersPaged()
        .cachedIn(viewModelScope)  // ✅ Cache to survive rotation
}
```

### UI (Compose)

```kotlin
@Composable
fun UserListScreen(viewModel: UserViewModel) {
    val users = viewModel.users.collectAsLazyPagingItems()

    LazyColumn {
        items(users.itemCount) { index ->
            users[index]?.let { UserItem(it) }
        }

        // ✅ Handle LoadState
        when (users.loadState.refresh) {
            is LoadState.Loading -> item { CircularProgressIndicator() }
            is LoadState.Error -> item {
                ErrorItem(onRetry = { users.retry() })
            }
            else -> {}
        }
    }
}
```

### RemoteMediator (Offline-First)

**RemoteMediator** fetches data from network and caches in Room:

```kotlin
// ✅ Remote Keys to track pagination state
@Entity(tableName = "user_remote_keys")
data class UserRemoteKeys(
    @PrimaryKey val userId: Long,
    val prevKey: Int?,
    val nextKey: Int?
)

@OptIn(ExperimentalPagingApi::class)
class UserRemoteMediator(
    private val apiService: UserApiService,
    private val database: AppDatabase
) : RemoteMediator<Int, User>() {

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, User>
    ): MediatorResult = try {
        val page = when (loadType) {
            LoadType.REFRESH -> 1
            LoadType.PREPEND -> return MediatorResult.Success(true)
            LoadType.APPEND -> {
                val remoteKeys = getRemoteKeyForLastItem(state)
                remoteKeys?.nextKey
                    ?: return MediatorResult.Success(true)
            }
        }

        val apiResponse = apiService.getUsers(page, state.config.pageSize)
        val endOfPaginationReached = apiResponse.isEmpty()

        // ✅ Atomic transaction for inserting data and keys
        database.withTransaction {
            if (loadType == LoadType.REFRESH) {
                database.userRemoteKeysDao().clearRemoteKeys()
                database.userDao().clearAllUsers()
            }

            val prevKey = if (page == 1) null else page - 1
            val nextKey = if (endOfPaginationReached) null else page + 1

            val keys = apiResponse.map {
                UserRemoteKeys(it.id, prevKey, nextKey)
            }
            val users = apiResponse.map { it.toEntity() }

            database.userRemoteKeysDao().insertAll(keys)
            database.userDao().insertUsers(users)
        }

        MediatorResult.Success(endOfPaginationReached)
    } catch (e: Exception) {
        MediatorResult.Error(e)
    }

    private suspend fun getRemoteKeyForLastItem(
        state: PagingState<Int, User>
    ): UserRemoteKeys? {
        return state.pages.lastOrNull { it.data.isNotEmpty() }
            ?.data?.lastOrNull()
            ?.let { database.userRemoteKeysDao().getRemoteKeys(it.id) }
    }
}
```

### Using RemoteMediator

```kotlin
class UserRepository(
    private val apiService: UserApiService,
    private val database: AppDatabase
) {
    @OptIn(ExperimentalPagingApi::class)
    fun getUsersWithRemoteMediator() = Pager(
        config = PagingConfig(pageSize = 20),
        remoteMediator = UserRemoteMediator(apiService, database),
        pagingSourceFactory = { database.userDao().getUsersPaged() }
    ).flow
}
```

### Best Practices

1. **cachedIn(viewModelScope)** — cache data to survive rotation
2. **PagingConfig**: pageSize 20-50, prefetchDistance 5-10, initialLoadSize 2-3x pageSize
3. **LoadState** — handle loading and error states
4. **RemoteMediator** — offline-first with Room caching
5. **DiffUtil** — efficient `RecyclerView` updates
6. **Remote Keys** — separate table for pagination state
7. **withTransaction** — atomic operations
8. **Retry mechanism** — recovery from errors

### Key Points

- **PagingSource**: automatic pagination from Room queries
- **RemoteMediator**: offline-first with network + database
- **LoadState**: handle loading/error/success states
- **collectAsLazyPagingItems()**: Compose LazyColumn integration
- **Transformations**: filter, map, insertSeparators
- **Performance**: efficient memory usage

Use **PagingSource** for simple local pagination, **RemoteMediator** for offline-first apps with network data caching.

---

## Follow-ups

- How does PagingSource handle database updates without invalidation?
- What are the trade-offs between `enablePlaceholders: true` vs `false`?
- How to implement bi-directional paging (prepend and append)?
- What happens when RemoteMediator load fails on APPEND vs REFRESH?
- How to handle complex filtering with RemoteMediator?
- When should maxSize be configured in PagingConfig?
- How to optimize RemoteKeys table with indices?

## References

- [[c-room]] - Room database fundamentals
- [[c-coroutines]] - Kotlin coroutines for async operations
- Android Paging 3 Documentation

## Related Questions

### Prerequisites (Easier)
- [[q-room-library-definition--android--easy]] - Room database basics

### Related (Medium)
- [[q-room-transactions-dao--android--medium]] - Room transactions
- [[q-room-type-converters--android--medium]] - Room type converters

### Advanced (Harder)
- [[q-room-fts-full-text-search--android--hard]] - Full-text search with Room
- Database migrations and versioning strategies
