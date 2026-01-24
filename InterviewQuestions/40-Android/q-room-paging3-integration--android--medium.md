---
id: android-242
anki_cards:
- slug: android-242-0-en
  language: en
  anki_id: 1768420255454
  synced_at: '2026-01-23T16:45:05.844546'
- slug: android-242-0-ru
  language: ru
  anki_id: 1768420255483
  synced_at: '2026-01-23T16:45:05.846103'
title: Room Paging3 Integration / Интеграция Room с Paging3
aliases:
- Room Paging3 Integration
- Интеграция Room с Paging3
topic: android
subtopics:
- architecture-mvvm
- room
- ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-room
- q-room-library-definition--android--easy
- q-room-transactions-dao--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags:
- android/architecture-mvvm
- android/room
- android/ui-compose
- database
- difficulty/medium
- offline-first
- pagination
- paging3
---
# Вопрос (RU)

> Как интегрировать `Room` с Paging 3? Реализуйте источник данных из `Room` и обработку RemoteMediator для офлайн-first архитектуры с сетью и базой данных.

# Question (EN)

> How to integrate `Room` with Paging 3? Implement `Room` database source and handle RemoteMediator for offline-first architecture with network and database paging.

## Ответ (RU)

**Paging 3** — библиотека пагинации, интегрируемая с [[c-room]] для эффективной загрузки больших наборов данных. Поддерживает локальную пагинацию БД и офлайн-first архитектуру (сеть + БД) через **RemoteMediator**.

### Базовый PagingSource

`Room` автоматически создаёт `PagingSource` из DAO-запросов:

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
            enablePlaceholders = false  // ℹ️ Без null-заполнителей (placeholder'ы отключены намеренно)
        ),
        pagingSourceFactory = { userDao.getUsersPaged() }
    ).flow
}

// ViewModel
class UserViewModel(repository: UserRepository) : ViewModel() {
    val users: Flow<PagingData<User>> = repository.getUsersPaged()
        .cachedIn(viewModelScope)  // ✅ Кэш для переживания rotation и пересоздания UI
}
```

`Room`-интеграция с Paging 3 автоматически инвалидирует `PagingSource` при изменении таблиц, участвующих в запросе, что обеспечивает актуальные данные без ручного обновления.

### UI (Compose)

```kotlin
@Composable
fun UserListScreen(viewModel: UserViewModel) {
    val users = viewModel.users.collectAsLazyPagingItems()

    LazyColumn {
        // ✅ Идиоматичная интеграция с Paging 3
        items(
            count = users.itemCount,
            key = { index -> users[index]?.id ?: index.toLong() } // при наличии стабильного id
        ) { index ->
            users[index]?.let { UserItem(it) }
        }

        // ✅ Обработка LoadState (refresh — начальная загрузка / общий state списка)
        when (val state = users.loadState.refresh) {
            is LoadState.Loading -> item { CircularProgressIndicator() }
            is LoadState.Error -> item {
                ErrorItem(onRetry = { users.retry() })
            }
            is LoadState.NotLoading -> {
                // нет дополнительного UI
            }
        }

        // При необходимости также обрабатываются append/prepend состояния через users.loadState.append/prepend
    }
}
```

### RemoteMediator (Offline-First)

**RemoteMediator** загружает данные из сети и кэширует их в `Room`.
Ниже — пример однонаправленной пагинации «вниз» (APPEND) с постраничным API вида `page=1,2,3...`:

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
            LoadType.REFRESH -> 1 // для простоты считаем, что всегда начинаем с 1-й страницы
            LoadType.PREPEND -> {
                // В этом примере поддерживается только пагинация вниз
                return MediatorResult.Success(endOfPaginationReached = true)
            }
            LoadType.APPEND -> {
                val remoteKeys = getRemoteKeyForLastItem(state)
                remoteKeys?.nextKey
                    ?: return MediatorResult.Success(endOfPaginationReached = true)
            }
        }

        val apiResponse = apiService.getUsers(page, state.config.pageSize)
        val endOfPaginationReached = apiResponse.isEmpty()

        // ✅ Атомарная транзакция для обновления данных и ключей
        database.withTransaction {
            if (loadType == LoadType.REFRESH) {
                database.userRemoteKeysDao().clearRemoteKeys()
                database.userDao().clearAllUsers()
            }

            val prevKey = if (page == 1) null else page - 1
            val nextKey = if (endOfPaginationReached) null else page + 1

            val keys = apiResponse.map { userDto ->
                UserRemoteKeys(userId = userDto.id, prevKey = prevKey, nextKey = nextKey)
            }
            val users = apiResponse.map { it.toEntity() }

            database.userRemoteKeysDao().insertAll(keys)
            database.userDao().insertUsers(users)
        }

        MediatorResult.Success(endOfPaginationReached = endOfPaginationReached)
    } catch (e: Exception) {
        MediatorResult.Error(e)
    }

    private suspend fun getRemoteKeyForLastItem(
        state: PagingState<Int, User>
    ): UserRemoteKeys? {
        // Ищем последний загруженный элемент и его ключ
        return state.pages.lastOrNull { it.data.isNotEmpty() }
            ?.data?.lastOrNull()
            ?.let { user ->
                database.userRemoteKeysDao().getRemoteKeys(user.id)
            }
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
    fun getUsersWithRemoteMediator(): Flow<PagingData<User>> = Pager(
        config = PagingConfig(pageSize = 20),
        remoteMediator = UserRemoteMediator(apiService, database),
        pagingSourceFactory = { database.userDao().getUsersPaged() }
    ).flow
}
```

### Best Practices

1. **cachedIn(viewModelScope)** — кэш данных для переживания rotation и пересоздания UI.
2. **PagingConfig**: `pageSize` 20–50, `prefetchDistance` 5–10, `initialLoadSize` 2–3× `pageSize`.
3. **LoadState** — обработка состояний загрузки и ошибок (`refresh`, `append`, `prepend`).
4. **RemoteMediator** — офлайн-first с кэшированием в `Room`.
5. **`DiffUtil`** — для `RecyclerView` (в Compose используется диффинг списков под капотом).
6. **Remote Keys** — отдельная таблица для состояния пагинации.
7. **withTransaction** — атомарность операций записи.
8. **Retry mechanism** — восстановление после ошибок через `retry()` / пользовательские стратегии.

### Ключевые Моменты

- **PagingSource**: автоматическая пагинация из `Room`-запросов.
- **RemoteMediator**: офлайн-first с сетью + БД.
- **LoadState**: обработка loading/error/success.
- **collectAsLazyPagingItems()**: интеграция с Compose LazyColumn.
- **Трансформации**: `map`, `filter`, `insertSeparators` поверх `PagingData`.
- **Производительность**: эффективное использование памяти и обновлений.

Используйте **PagingSource** для простой локальной пагинации, **RemoteMediator** — для офлайн-first приложений с кэшированием сетевых данных.

---

## Answer (EN)

**Paging 3** is a pagination library that integrates with [[c-room]] to efficiently load large datasets. It supports local database paging and offline-first architecture (network + database) through **RemoteMediator**.

### Basic PagingSource

`Room` automatically creates a `PagingSource` from DAO queries:

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
            enablePlaceholders = false  // ℹ️ No placeholders (disabled intentionally)
        ),
        pagingSourceFactory = { userDao.getUsersPaged() }
    ).flow
}

// ViewModel
class UserViewModel(repository: UserRepository) : ViewModel() {
    val users: Flow<PagingData<User>> = repository.getUsersPaged()
        .cachedIn(viewModelScope)  // ✅ Cache in scope to survive rotation and configuration changes
}
```

Paging 3 with `Room` automatically invalidates the `PagingSource` when underlying tables used in the query change, ensuring up-to-date data without manual refresh logic.

### UI (Compose)

```kotlin
@Composable
fun UserListScreen(viewModel: UserViewModel) {
    val users = viewModel.users.collectAsLazyPagingItems()

    LazyColumn {
        // ✅ Idiomatic Paging 3 + Compose integration
        items(
            count = users.itemCount,
            key = { index -> users[index]?.id ?: index.toLong() } // use stable id when available
        ) { index ->
            users[index]?.let { UserItem(it) }
        }

        // ✅ Handle LoadState (refresh = initial / overall list state)
        when (val state = users.loadState.refresh) {
            is LoadState.Loading -> item { CircularProgressIndicator() }
            is LoadState.Error -> item {
                ErrorItem(onRetry = { users.retry() })
            }
            is LoadState.NotLoading -> {
                // no extra UI
            }
        }

        // Optionally also handle users.loadState.append / prepend for list tail/head states
    }
}
```

### RemoteMediator (Offline-First)

**RemoteMediator** fetches data from the network and caches it into `Room`.
Below is a simple one-directional (append-only) paging example for a page-based API `page = 1,2,3...`:

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
            LoadType.REFRESH -> 1 // for simplicity, always start from page 1
            LoadType.PREPEND -> {
                // This example supports only paging downwards
                return MediatorResult.Success(endOfPaginationReached = true)
            }
            LoadType.APPEND -> {
                val remoteKeys = getRemoteKeyForLastItem(state)
                remoteKeys?.nextKey
                    ?: return MediatorResult.Success(endOfPaginationReached = true)
            }
        }

        val apiResponse = apiService.getUsers(page, state.config.pageSize)
        val endOfPaginationReached = apiResponse.isEmpty()

        // ✅ Atomic transaction for updating both data and keys
        database.withTransaction {
            if (loadType == LoadType.REFRESH) {
                database.userRemoteKeysDao().clearRemoteKeys()
                database.userDao().clearAllUsers()
            }

            val prevKey = if (page == 1) null else page - 1
            val nextKey = if (endOfPaginationReached) null else page + 1

            val keys = apiResponse.map { userDto ->
                UserRemoteKeys(userId = userDto.id, prevKey = prevKey, nextKey = nextKey)
            }
            val users = apiResponse.map { it.toEntity() }

            database.userRemoteKeysDao().insertAll(keys)
            database.userDao().insertUsers(users)
        }

        MediatorResult.Success(endOfPaginationReached = endOfPaginationReached)
    } catch (e: Exception) {
        MediatorResult.Error(e)
    }

    private suspend fun getRemoteKeyForLastItem(
        state: PagingState<Int, User>
    ): UserRemoteKeys? {
        // Find the last item loaded and its remote key
        return state.pages.lastOrNull { it.data.isNotEmpty() }
            ?.data?.lastOrNull()
            ?.let { user ->
                database.userRemoteKeysDao().getRemoteKeys(user.id)
            }
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
    fun getUsersWithRemoteMediator(): Flow<PagingData<User>> = Pager(
        config = PagingConfig(pageSize = 20),
        remoteMediator = UserRemoteMediator(apiService, database),
        pagingSourceFactory = { database.userDao().getUsersPaged() }
    ).flow
}
```

### Best Practices

1. **cachedIn(viewModelScope)** — cache in a lifecycle-aware scope to survive rotation and UI recreation.
2. **PagingConfig**: `pageSize` 20–50, `prefetchDistance` 5–10, `initialLoadSize` 2–3× `pageSize`.
3. **LoadState** — always handle loading and error states (`refresh`, `append`, `prepend`).
4. **RemoteMediator** — implement offline-first behavior with `Room`-backed cache.
5. **`DiffUtil`** — for `RecyclerView` usage (Compose handles diffs internally).
6. **Remote Keys** — dedicated table to persist pagination state.
7. **withTransaction** — ensure atomic writes for data + remote keys.
8. **Retry mechanism** — expose `retry()` / custom retry logic after failures.

### Key Points

- **PagingSource**: automatic paging from `Room` queries.
- **RemoteMediator**: offline-first with network + database cache.
- **LoadState**: handle loading/error/success states.
- **collectAsLazyPagingItems()**: integration with Compose LazyColumn.
- **Transformations**: `map`, `filter`, `insertSeparators` on `PagingData`.
- **Performance**: efficient memory usage and list updates.

Use **PagingSource** for simple local pagination, **RemoteMediator** for offline-first apps with network data caching.

---

## Дополнительные Вопросы (RU)

- Как `PagingSource` обрабатывает обновления базы данных без ручной инвалидции?
- В чем компромиссы между `enablePlaceholders: true` и `false`?
- Как реализовать двунаправленную пагинацию (prepend и append)?
- Что происходит при ошибке `RemoteMediator.load` на стадиях APPEND и REFRESH?
- Как обрабатывать сложную фильтрацию при использовании RemoteMediator?
- В каких случаях следует настраивать `maxSize` в `PagingConfig`?
- Как оптимизировать таблицу `RemoteKeys` с помощью индексов?

## Ссылки (RU)

- [[c-room]] — основы базы данных `Room`
- [[c-coroutines]] — корутины Kotlin для асинхронных операций
- Android Paging 3 Documentation

## Связанные Вопросы (RU)

### Базовые (проще)
- [[q-room-library-definition--android--easy]] — основы `Room`

### Средний Уровень
- [[q-room-transactions-dao--android--medium]] — транзакции в `Room`
- [[q-room-type-converters--android--medium]] — конвертеры типов в `Room`

### Продвинутый Уровень (сложнее)
- [[q-room-fts-full-text-search--android--hard]] — полнотекстовый поиск в `Room`
- Стратегии миграций базы данных и версионирования

---

## Follow-ups

- How does PagingSource handle database updates without invalidation?
- What are the trade-offs between `enablePlaceholders: true` vs `false`?
- How to implement bi-directional paging (prepend and append)?
- What happens when RemoteMediator load fails on APPEND vs REFRESH?
- How to handle complex filtering with RemoteMediator?
- When should `maxSize` be configured in `PagingConfig`?
- How to optimize `RemoteKeys` table with indices?

## References

- [[c-room]] - `Room` database fundamentals
- [[c-coroutines]] - Kotlin coroutines for async operations
- Android Paging 3 Documentation

## Related Questions

### Prerequisites (Easier)
- [[q-room-library-definition--android--easy]] - `Room` database basics

### Related (Medium)
- [[q-room-transactions-dao--android--medium]] - `Room` transactions
- [[q-room-type-converters--android--medium]] - `Room` type converters

### Advanced (Harder)
- [[q-room-fts-full-text-search--android--hard]] - Full-text search with `Room`
- `Database` migrations and versioning strategies
