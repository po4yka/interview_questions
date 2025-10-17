---
id: "20251015082237315"
title: "Room Paging3 Integration / Интеграция Room с Paging3"
topic: room
difficulty: medium
status: draft
created: 2025-10-15
tags: - room
  - paging3
  - database
  - pagination
  - architecture
  - offline-first
  - difficulty/medium
---
# Room Paging 3 Integration / Интеграция Room с Paging 3

**English**: Implement Room database source for Paging 3. Handle remote mediator for network + database paging.

## Answer (EN)
**Paging 3** is a modern pagination library that integrates seamlessly with Room to efficiently load and display large datasets. It supports both local database paging and network + database (offline-first) architectures through **RemoteMediator**.

### Why Paging 3 with Room?

- **Efficient Memory Usage**: Load data in chunks instead of all at once
- **Performance**: Display data immediately while loading more
- **Offline-First**: Cache network data in Room for offline access
- **Automatic Loading**: Handle loading states, errors, and retry logic
- **RecyclerView/LazyColumn Integration**: Seamless UI updates
- **Separation of Concerns**: Clean architecture with layered approach

### Basic Room PagingSource

The simplest way to implement paging with Room is using `PagingSource` directly from DAO queries.

#### Entity and DAO

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey
    val id: Long,
    val name: String,
    val email: String,
    val avatarUrl: String,
    val createdAt: Long = System.currentTimeMillis()
)

// DAO with PagingSource
@Dao
interface UserDao {
    // Room automatically creates PagingSource implementation
    @Query("SELECT * FROM users ORDER BY createdAt DESC")
    fun getUsersPaged(): PagingSource<Int, User>

    // With filtering
    @Query("SELECT * FROM users WHERE name LIKE '%' || :query || '%' ORDER BY name ASC")
    fun searchUsersPaged(query: String): PagingSource<Int, User>

    // With complex sorting
    @Query("""
        SELECT * FROM users
        ORDER BY
            CASE WHEN :sortBy = 'name' THEN name END ASC,
            CASE WHEN :sortBy = 'date' THEN createdAt END DESC
    """)
    fun getUsersPagedSorted(sortBy: String): PagingSource<Int, User>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)

    @Query("DELETE FROM users")
    suspend fun clearAllUsers()
}
```

#### Repository

```kotlin
class UserRepository(private val userDao: UserDao) {

    fun getUsersPaged(): Flow<PagingData<User>> {
        return Pager(
            config = PagingConfig(
                pageSize = 20,              // Items per page
                prefetchDistance = 5,       // Load next page when 5 items from end
                enablePlaceholders = false, // Show null placeholders or not
                initialLoadSize = 40,       // First page size (usually 2x pageSize)
                maxSize = 200              // Max items in memory
            ),
            pagingSourceFactory = { userDao.getUsersPaged() }
        ).flow
    }

    fun searchUsersPaged(query: String): Flow<PagingData<User>> {
        return Pager(
            config = PagingConfig(
                pageSize = 20,
                enablePlaceholders = false
            ),
            pagingSourceFactory = { userDao.searchUsersPaged(query) }
        ).flow
    }
}
```

#### ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    val users: Flow<PagingData<User>> = repository.getUsersPaged()
        .cachedIn(viewModelScope)  // Cache to survive configuration changes

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val searchResults: Flow<PagingData<User>> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { query ->
            if (query.isEmpty()) {
                repository.getUsersPaged()
            } else {
                repository.searchUsersPaged(query)
            }
        }
        .cachedIn(viewModelScope)

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

#### UI with RecyclerView and PagingDataAdapter

```kotlin
// Adapter
class UserAdapter : PagingDataAdapter<User, UserAdapter.UserViewHolder>(USER_COMPARATOR) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return UserViewHolder(binding)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        val user = getItem(position)
        if (user != null) {
            holder.bind(user)
        }
    }

    class UserViewHolder(private val binding: ItemUserBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(user: User) {
            binding.apply {
                nameTextView.text = user.name
                emailTextView.text = user.email
                // Load image with Coil/Glide
                Glide.with(avatarImageView.context)
                    .load(user.avatarUrl)
                    .into(avatarImageView)
            }
        }
    }

    companion object {
        private val USER_COMPARATOR = object : DiffUtil.ItemCallback<User>() {
            override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
                return oldItem.id == newItem.id
            }

            override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
                return oldItem == newItem
            }
        }
    }
}

// Activity/Fragment
class UserListFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()
    private lateinit var adapter: UserAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = UserAdapter()
        binding.recyclerView.adapter = adapter

        // Collect paging data
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.users.collectLatest { pagingData ->
                adapter.submitData(pagingData)
            }
        }

        // Handle loading state
        viewLifecycleOwner.lifecycleScope.launch {
            adapter.loadStateFlow.collectLatest { loadStates ->
                binding.progressBar.isVisible = loadStates.refresh is LoadState.Loading
                binding.retryButton.isVisible = loadStates.refresh is LoadState.Error

                // Show error message
                val errorState = loadStates.refresh as? LoadState.Error
                    ?: loadStates.append as? LoadState.Error
                    ?: loadStates.prepend as? LoadState.Error

                errorState?.let {
                    Toast.makeText(
                        requireContext(),
                        it.error.localizedMessage,
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }

        // Retry button
        binding.retryButton.setOnClickListener {
            adapter.retry()
        }
    }
}
```

#### UI with Jetpack Compose and LazyColumn

```kotlin
@Composable
fun UserListScreen(viewModel: UserViewModel = viewModel()) {
    val users = viewModel.users.collectAsLazyPagingItems()

    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(users.itemCount) { index ->
                users[index]?.let { user ->
                    UserItem(user = user)
                }
            }

            // Loading state
            when (users.loadState.refresh) {
                is LoadState.Loading -> {
                    item {
                        Box(
                            modifier = Modifier.fillMaxWidth(),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator()
                        }
                    }
                }
                is LoadState.Error -> {
                    val error = (users.loadState.refresh as LoadState.Error).error
                    item {
                        ErrorItem(
                            message = error.localizedMessage ?: "Unknown error",
                            onRetry = { users.retry() }
                        )
                    }
                }
                else -> {}
            }

            // Append loading state
            when (users.loadState.append) {
                is LoadState.Loading -> {
                    item {
                        CircularProgressIndicator(
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }
                else -> {}
            }
        }
    }
}

@Composable
fun UserItem(user: User) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )
            Column {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray
                )
            }
        }
    }
}

@Composable
fun ErrorItem(message: String, onRetry: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = message, color = Color.Red)
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onRetry) {
            Text("Retry")
        }
    }
}
```

### Advanced: RemoteMediator for Offline-First Architecture

**RemoteMediator** enables fetching data from network and caching in Room, providing true offline-first experience.

#### Complete Offline-First Example

```kotlin
// Remote API response
data class UserResponse(
    val id: Long,
    val name: String,
    val email: String,
    val avatarUrl: String
)

// API Service
interface UserApiService {
    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("per_page") perPage: Int
    ): List<UserResponse>
}

// Remote keys entity to track pagination state
@Entity(tableName = "user_remote_keys")
data class UserRemoteKeys(
    @PrimaryKey
    val userId: Long,
    val prevKey: Int?,
    val nextKey: Int?
)

@Dao
interface UserRemoteKeysDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(remoteKeys: List<UserRemoteKeys>)

    @Query("SELECT * FROM user_remote_keys WHERE userId = :userId")
    suspend fun getRemoteKeys(userId: Long): UserRemoteKeys?

    @Query("DELETE FROM user_remote_keys")
    suspend fun clearRemoteKeys()
}

// Database with both entities
@Database(
    entities = [User::class, UserRemoteKeys::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun userRemoteKeysDao(): UserRemoteKeysDao
}
```

#### RemoteMediator Implementation

```kotlin
@OptIn(ExperimentalPagingApi::class)
class UserRemoteMediator(
    private val apiService: UserApiService,
    private val database: AppDatabase
) : RemoteMediator<Int, User>() {

    private val userDao = database.userDao()
    private val remoteKeysDao = database.userRemoteKeysDao()

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, User>
    ): MediatorResult {
        return try {
            // Determine page to load
            val page = when (loadType) {
                LoadType.REFRESH -> {
                    // Initial load or refresh
                    val remoteKeys = getRemoteKeyClosestToCurrentPosition(state)
                    remoteKeys?.nextKey?.minus(1) ?: STARTING_PAGE_INDEX
                }
                LoadType.PREPEND -> {
                    // Load data at the beginning
                    val remoteKeys = getRemoteKeyForFirstItem(state)
                    val prevKey = remoteKeys?.prevKey
                        ?: return MediatorResult.Success(endOfPaginationReached = true)
                    prevKey
                }
                LoadType.APPEND -> {
                    // Load data at the end
                    val remoteKeys = getRemoteKeyForLastItem(state)
                    val nextKey = remoteKeys?.nextKey
                        ?: return MediatorResult.Success(endOfPaginationReached = true)
                    nextKey
                }
            }

            // Fetch data from network
            val apiResponse = apiService.getUsers(
                page = page,
                perPage = state.config.pageSize
            )

            val endOfPaginationReached = apiResponse.isEmpty()

            database.withTransaction {
                // Clear database on refresh
                if (loadType == LoadType.REFRESH) {
                    remoteKeysDao.clearRemoteKeys()
                    userDao.clearAllUsers()
                }

                // Calculate prev/next keys
                val prevKey = if (page == STARTING_PAGE_INDEX) null else page - 1
                val nextKey = if (endOfPaginationReached) null else page + 1

                // Transform API response to entities
                val users = apiResponse.map { response ->
                    User(
                        id = response.id,
                        name = response.name,
                        email = response.email,
                        avatarUrl = response.avatarUrl
                    )
                }

                val keys = apiResponse.map { response ->
                    UserRemoteKeys(
                        userId = response.id,
                        prevKey = prevKey,
                        nextKey = nextKey
                    )
                }

                // Insert into database
                remoteKeysDao.insertAll(keys)
                userDao.insertUsers(users)
            }

            MediatorResult.Success(endOfPaginationReached = endOfPaginationReached)

        } catch (exception: IOException) {
            MediatorResult.Error(exception)
        } catch (exception: HttpException) {
            MediatorResult.Error(exception)
        }
    }

    private suspend fun getRemoteKeyForLastItem(state: PagingState<Int, User>): UserRemoteKeys? {
        return state.pages.lastOrNull { it.data.isNotEmpty() }?.data?.lastOrNull()
            ?.let { user ->
                remoteKeysDao.getRemoteKeys(user.id)
            }
    }

    private suspend fun getRemoteKeyForFirstItem(state: PagingState<Int, User>): UserRemoteKeys? {
        return state.pages.firstOrNull { it.data.isNotEmpty() }?.data?.firstOrNull()
            ?.let { user ->
                remoteKeysDao.getRemoteKeys(user.id)
            }
    }

    private suspend fun getRemoteKeyClosestToCurrentPosition(
        state: PagingState<Int, User>
    ): UserRemoteKeys? {
        return state.anchorPosition?.let { position ->
            state.closestItemToPosition(position)?.id?.let { userId ->
                remoteKeysDao.getRemoteKeys(userId)
            }
        }
    }

    companion object {
        private const val STARTING_PAGE_INDEX = 1
    }
}
```

#### Repository with RemoteMediator

```kotlin
class UserRepository(
    private val apiService: UserApiService,
    private val database: AppDatabase
) {
    private val userDao = database.userDao()

    @OptIn(ExperimentalPagingApi::class)
    fun getUsersWithRemoteMediator(): Flow<PagingData<User>> {
        return Pager(
            config = PagingConfig(
                pageSize = 20,
                prefetchDistance = 5,
                enablePlaceholders = false
            ),
            remoteMediator = UserRemoteMediator(
                apiService = apiService,
                database = database
            ),
            pagingSourceFactory = { userDao.getUsersPaged() }
        ).flow
    }
}
```

### Advanced: Loading State Headers/Footers

Display loading indicators and retry buttons in headers/footers.

```kotlin
// Loading state adapter
class UserLoadStateAdapter(
    private val retry: () -> Unit
) : LoadStateAdapter<UserLoadStateAdapter.LoadStateViewHolder>() {

    override fun onCreateViewHolder(
        parent: ViewGroup,
        loadState: LoadState
    ): LoadStateViewHolder {
        val binding = ItemLoadStateBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return LoadStateViewHolder(binding, retry)
    }

    override fun onBindViewHolder(holder: LoadStateViewHolder, loadState: LoadState) {
        holder.bind(loadState)
    }

    class LoadStateViewHolder(
        private val binding: ItemLoadStateBinding,
        private val retry: () -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(loadState: LoadState) {
            binding.apply {
                progressBar.isVisible = loadState is LoadState.Loading
                retryButton.isVisible = loadState is LoadState.Error
                errorTextView.isVisible = loadState is LoadState.Error

                if (loadState is LoadState.Error) {
                    errorTextView.text = loadState.error.localizedMessage
                }

                retryButton.setOnClickListener {
                    retry()
                }
            }
        }
    }
}

// Usage in Fragment
class UserListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val userAdapter = UserAdapter()

        // Add header and footer
        binding.recyclerView.adapter = userAdapter.withLoadStateHeaderAndFooter(
            header = UserLoadStateAdapter { userAdapter.retry() },
            footer = UserLoadStateAdapter { userAdapter.retry() }
        )

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.users.collectLatest { pagingData ->
                userAdapter.submitData(pagingData)
            }
        }
    }
}
```

### Item Transformations

Transform paging data before displaying.

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    val users: Flow<PagingData<UserUiModel>> = repository.getUsersWithRemoteMediator()
        .map { pagingData ->
            pagingData
                // Filter items
                .filter { user -> user.email.isNotEmpty() }
                // Transform items
                .map { user ->
                    UserUiModel(
                        id = user.id,
                        displayName = user.name.uppercase(),
                        email = user.email,
                        avatarUrl = user.avatarUrl,
                        isVerified = user.email.endsWith("@example.com")
                    )
                }
                // Insert separators
                .insertSeparators { before, after ->
                    if (after != null && before?.displayName?.first() != after.displayName.first()) {
                        UserUiModel.Separator(after.displayName.first().toString())
                    } else {
                        null
                    }
                }
        }
        .cachedIn(viewModelScope)
}

sealed class UserUiModel {
    data class UserItem(
        val id: Long,
        val displayName: String,
        val email: String,
        val avatarUrl: String,
        val isVerified: Boolean
    ) : UserUiModel()

    data class Separator(val letter: String) : UserUiModel()
}
```

### Testing

#### Unit Test for PagingSource

```kotlin
@RunWith(AndroidJUnit4::class)
class UserPagingSourceTest {

    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).build()
        userDao = database.userDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    @Test
    fun pagingSource_loadsData() = runBlocking {
        // Insert test data
        val users = (1..50).map { i ->
            User(
                id = i.toLong(),
                name = "User $i",
                email = "user$i@example.com",
                avatarUrl = "https://example.com/avatar$i.jpg"
            )
        }
        userDao.insertUsers(users)

        // Create paging source
        val pagingSource = userDao.getUsersPaged()

        // Load first page
        val loadResult = pagingSource.load(
            PagingSource.LoadParams.Refresh(
                key = null,
                loadSize = 20,
                placeholdersEnabled = false
            )
        )

        // Verify results
        assertTrue(loadResult is PagingSource.LoadResult.Page)
        val page = loadResult as PagingSource.LoadResult.Page
        assertEquals(20, page.data.size)
        assertEquals(users.take(20), page.data)
    }
}
```

#### Unit Test for RemoteMediator

```kotlin
@OptIn(ExperimentalPagingApi::class)
@RunWith(AndroidJUnit4::class)
class UserRemoteMediatorTest {

    private lateinit var database: AppDatabase
    private lateinit var apiService: UserApiService
    private lateinit var remoteMediator: UserRemoteMediator

    @Before
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).build()

        apiService = mockk()
        remoteMediator = UserRemoteMediator(apiService, database)
    }

    @Test
    fun refreshLoad_successfullyLoadsData() = runBlocking {
        // Mock API response
        val apiResponse = listOf(
            UserResponse(1, "User 1", "user1@example.com", "avatar1.jpg"),
            UserResponse(2, "User 2", "user2@example.com", "avatar2.jpg")
        )
        coEvery { apiService.getUsers(any(), any()) } returns apiResponse

        // Execute load
        val pagingState = PagingState<Int, User>(
            pages = emptyList(),
            anchorPosition = null,
            config = PagingConfig(pageSize = 20),
            leadingPlaceholderCount = 0
        )

        val result = remoteMediator.load(LoadType.REFRESH, pagingState)

        // Verify
        assertTrue(result is RemoteMediator.MediatorResult.Success)
        val users = database.userDao().getUsersPaged().load(
            PagingSource.LoadParams.Refresh(
                key = null,
                loadSize = 10,
                placeholdersEnabled = false
            )
        )
        assertTrue(users is PagingSource.LoadResult.Page)
        assertEquals(2, (users as PagingSource.LoadResult.Page).data.size)
    }
}
```

### Best Practices

1. **Use cachedIn(viewModelScope)**: Cache paging data to survive configuration changes
2. **Configure PagingConfig properly**:
   - pageSize: 20-50 items for optimal performance
   - prefetchDistance: 5-10 items before end
   - initialLoadSize: 2-3x pageSize
   - enablePlaceholders: false for most cases
3. **Handle LoadState**: Show loading indicators and error messages
4. **RemoteMediator for offline-first**: Cache network data in Room
5. **Use DiffUtil**: Define proper ItemCallback for efficient updates
6. **Remote Keys**: Track pagination state in separate entity
7. **Transactions**: Use withTransaction for atomic operations
8. **Testing**: Write unit tests for PagingSource and RemoteMediator
9. **Error Handling**: Provide retry mechanism for failed loads
10. **Separators**: Use insertSeparators for section headers

### Common Pitfalls

1. **Not using cachedIn()**: Data reloads on configuration changes
2. **Wrong page size**: Too small (many network calls) or too large (slow loading)
3. **No error handling**: App crashes on network errors
4. **Forgetting DiffUtil**: Poor RecyclerView performance
5. **Not clearing database on refresh**: Stale data mixed with fresh data
6. **Missing indices**: Slow Room queries on foreign keys
7. **Synchronous operations**: Using blocking calls in RemoteMediator
8. **Not testing pagination**: Edge cases not covered
9. **No retry mechanism**: Users can't recover from errors
10. **Wrong LoadType handling**: Incorrect page calculation

### Summary

Paging 3 with Room provides powerful pagination capabilities:

- **PagingSource**: Automatic pagination from Room queries
- **RemoteMediator**: Offline-first with network + database
- **LoadState**: Handle loading, error, and success states
- **Compose Support**: LazyColumn integration with collectAsLazyPagingItems()
- **Transformations**: Filter, map, insertSeparators on paging data
- **Performance**: Efficient memory usage and smooth scrolling
- **Testing**: Comprehensive testing support
- **Error Handling**: Built-in retry mechanism

Use PagingSource for simple local pagination, and RemoteMediator for offline-first apps with network data caching.

---

## Ответ (RU)
**Paging 3** — это современная библиотека пагинации, которая беспрепятственно интегрируется с Room для эффективной загрузки и отображения больших наборов данных. Она поддерживает как локальную пагинацию базы данных, так и архитектуру сеть + база данных (offline-first) через **RemoteMediator**.

### Зачем Paging 3 с Room?

- **Эффективное использование памяти**: Загрузка данных порциями вместо всего сразу
- **Производительность**: Отображение данных немедленно при загрузке большего
- **Offline-First**: Кэширование сетевых данных в Room для офлайн доступа
- **Автоматическая загрузка**: Обработка состояний загрузки, ошибок и логики повтора
- **Интеграция RecyclerView/LazyColumn**: Беспроблемные обновления UI
- **Разделение обязанностей**: Чистая архитектура со слоистым подходом

### Базовый Room PagingSource

Простейший способ реализовать пагинацию с Room — использовать `PagingSource` напрямую из запросов DAO.

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey
    val id: Long,
    val name: String,
    val email: String,
    val avatarUrl: String
)

// DAO с PagingSource
@Dao
interface UserDao {
    // Room автоматически создаёт реализацию PagingSource
    @Query("SELECT * FROM users ORDER BY createdAt DESC")
    fun getUsersPaged(): PagingSource<Int, User>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)
}
```

### Repository

```kotlin
class UserRepository(private val userDao: UserDao) {

    fun getUsersPaged(): Flow<PagingData<User>> {
        return Pager(
            config = PagingConfig(
                pageSize = 20,              // Элементов на страницу
                prefetchDistance = 5,       // Загружать следующую страницу за 5 элементов до конца
                enablePlaceholders = false, // Показывать null заполнители или нет
                initialLoadSize = 40,       // Размер первой страницы (обычно 2x pageSize)
                maxSize = 200              // Макс элементов в памяти
            ),
            pagingSourceFactory = { userDao.getUsersPaged() }
        ).flow
    }
}
```

### ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    val users: Flow<PagingData<User>> = repository.getUsersPaged()
        .cachedIn(viewModelScope)  // Кэш для переживания изменений конфигурации
}
```

### UI с Jetpack Compose

```kotlin
@Composable
fun UserListScreen(viewModel: UserViewModel = viewModel()) {
    val users = viewModel.users.collectAsLazyPagingItems()

    LazyColumn {
        items(users.itemCount) { index ->
            users[index]?.let { user ->
                UserItem(user = user)
            }
        }

        // Состояние загрузки
        when (users.loadState.refresh) {
            is LoadState.Loading -> {
                item {
                    CircularProgressIndicator()
                }
            }
            is LoadState.Error -> {
                val error = (users.loadState.refresh as LoadState.Error).error
                item {
                    ErrorItem(
                        message = error.localizedMessage ?: "Unknown error",
                        onRetry = { users.retry() }
                    )
                }
            }
            else -> {}
        }
    }
}
```

### Продвинуто: RemoteMediator для Offline-First архитектуры

**RemoteMediator** позволяет извлекать данные из сети и кэшировать в Room, обеспечивая настоящий offline-first опыт.

```kotlin
// Сущность удалённых ключей для отслеживания состояния пагинации
@Entity(tableName = "user_remote_keys")
data class UserRemoteKeys(
    @PrimaryKey
    val userId: Long,
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
    ): MediatorResult {
        return try {
            // Определить страницу для загрузки
            val page = when (loadType) {
                LoadType.REFRESH -> STARTING_PAGE_INDEX
                LoadType.PREPEND -> {
                    val remoteKeys = getRemoteKeyForFirstItem(state)
                    remoteKeys?.prevKey
                        ?: return MediatorResult.Success(endOfPaginationReached = true)
                }
                LoadType.APPEND -> {
                    val remoteKeys = getRemoteKeyForLastItem(state)
                    remoteKeys?.nextKey
                        ?: return MediatorResult.Success(endOfPaginationReached = true)
                }
            }

            // Извлечь данные из сети
            val apiResponse = apiService.getUsers(
                page = page,
                perPage = state.config.pageSize
            )

            val endOfPaginationReached = apiResponse.isEmpty()

            database.withTransaction {
                // Очистить БД при обновлении
                if (loadType == LoadType.REFRESH) {
                    database.userRemoteKeysDao().clearRemoteKeys()
                    database.userDao().clearAllUsers()
                }

                // Вставить в базу данных
                val users = apiResponse.map { /* преобразование */ }
                database.userDao().insertUsers(users)
            }

            MediatorResult.Success(endOfPaginationReached = endOfPaginationReached)

        } catch (exception: Exception) {
            MediatorResult.Error(exception)
        }
    }

    companion object {
        private const val STARTING_PAGE_INDEX = 1
    }
}
```

### Best Practices

1. **Использовать cachedIn(viewModelScope)**: Кэшировать данные пагинации
2. **Правильно настроить PagingConfig**: pageSize 20-50, prefetchDistance 5-10
3. **Обрабатывать LoadState**: Показывать индикаторы загрузки и сообщения об ошибках
4. **RemoteMediator для offline-first**: Кэшировать сетевые данные в Room
5. **Использовать DiffUtil**: Определить правильный ItemCallback
6. **Remote Keys**: Отслеживать состояние пагинации в отдельной сущности
7. **Транзакции**: Использовать withTransaction для атомарных операций
8. **Тестирование**: Писать unit тесты для PagingSource и RemoteMediator

### Резюме

Paging 3 с Room предоставляет мощные возможности пагинации:

- **PagingSource**: Автоматическая пагинация из запросов Room
- **RemoteMediator**: Offline-first с сеть + база данных
- **LoadState**: Обработка состояний загрузки, ошибок и успеха
- **Поддержка Compose**: Интеграция LazyColumn с collectAsLazyPagingItems()
- **Трансформации**: filter, map, insertSeparators на paging данных
- **Производительность**: Эффективное использование памяти и плавная прокрутка

---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Related (Medium)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage
- [[q-room-type-converters-advanced--room--medium]] - Storage
- [[q-room-vs-sqlite--android--medium]] - Storage
- [[q-room-type-converters--android--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--room--hard]] - Storage
