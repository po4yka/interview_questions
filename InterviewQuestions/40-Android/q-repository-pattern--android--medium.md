---
id: android-070
title: "Repository Pattern in Android / Паттерн Repository в Android"
aliases: []

# Classification
topic: android
subtopics: [architecture-clean, architecture-mvvm]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/architecture, android/repository, android/data-layer, android/clean-architecture, android/mvvm, difficulty/medium]
source: internal
source_note: Created for vault completeness

# Workflow & relations
status: draft
moc: moc-android
related: [q-repository-multiple-sources--android--medium, q-clean-architecture-android--android--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-31

tags: [android/architecture-clean, android/architecture-mvvm, en, ru, difficulty/medium]
---

# Question (EN)
> What is the Repository pattern in Android? How does it abstract data sources, provide a single source of truth, and work with ViewModels?

# Вопрос (RU)
> Что такое паттерн Repository в Android? Как он абстрагирует источники данных, предоставляет единый источник истины и работает с ViewModels?

---

## Answer (EN)

**Repository Pattern** is an architectural pattern that abstracts data sources (network, database, cache) behind a clean API, providing a single source of truth and separating business logic from data access logic.

### Why Repository Pattern?

**Problems it solves:**
1. **Data source coupling** - ViewModels shouldn't know if data comes from API or database
2. **Duplicate logic** - Caching logic shouldn't be repeated across screens
3. **Testing difficulty** - Hard to test ViewModels with real data sources
4. **Complexity** - Managing multiple data sources becomes unmanageable

**Benefits:**
- Single source of truth
- Centralized caching and data logic
- Easy to test (mock repository)
- Clean separation of concerns
- Swappable data sources

### Basic Repository

```kotlin
interface UserRepository {
    suspend fun getUser(userId: String): User
    suspend fun updateUser(user: User)
}

class UserRepositoryImpl(
    private val userApi: UserApi,
    private val userDao: UserDao
) : UserRepository {

    override suspend fun getUser(userId: String): User {
        return try {
            // Try network first
            val user = userApi.getUser(userId)
            // Cache in database
            userDao.insertUser(user)
            user
        } catch (e: IOException) {
            // Fallback to database
            userDao.getUser(userId) ?: throw e
        }
    }

    override suspend fun updateUser(user: User) {
        userApi.updateUser(user)
        userDao.insertUser(user)
    }
}
```

### Repository in MVVM Architecture

```
View (Activity/Fragment/Composable)
    ↓ observes state
ViewModel
    ↓ calls repository
Repository
    ↓ coordinates data sources
DataSources (API, Database, Cache)
```

**Example:**

```kotlin
// 1. Data Sources
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User
}

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>
}

// 2. Repository
class UserRepository(
    private val userApi: UserApi,
    private val userDao: UserDao
) {
    fun getUser(userId: String): Flow<User> = flow {
        // Emit cached data immediately
        userDao.getUser(userId)?.let { emit(it) }

        // Fetch fresh data
        try {
            val freshUser = userApi.getUser(userId)
            userDao.insertUser(freshUser)
            emit(freshUser)
        } catch (e: Exception) {
            // Already emitted cached data, ignore error
        }
    }

    fun observeUsers(): Flow<List<User>> {
        return userDao.observeUsers()
    }

    suspend fun refreshUsers() {
        val users = userApi.getUsers()
        userDao.insertUsers(users)
    }
}

// 3. ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            repository.getUser(userId)
                .catch { e ->
                    _uiState.value = UiState.Error(e.message ?: "Unknown error")
                }
                .collect { user ->
                    _uiState.value = UiState.Success(user)
                }
        }
    }
}

// 4. UI
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    when (uiState) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> UserContent((uiState as UiState.Success).user)
        is UiState.Error -> ErrorMessage((uiState as UiState.Error).message)
    }
}
```

### Single Source of Truth

**Database as source of truth** - Network updates database, UI observes database:

```kotlin
class ProductRepository(
    private val productApi: ProductApi,
    private val productDao: ProductDao
) {
    // Database is the single source of truth
    fun getProducts(): Flow<List<Product>> = flow {
        // 1. Emit from database (source of truth)
        emitAll(productDao.observeProducts())

        // 2. Refresh from network in background
        try {
            val products = productApi.getProducts()
            productDao.insertProducts(products)  // Updates the flow above
        } catch (e: Exception) {
            // Ignore - using cached data
        }
    }

    suspend fun refreshProducts() {
        val products = productApi.getProducts()
        productDao.insertProducts(products)
    }
}
```

**Benefits:**
- UI always shows consistent data
- Network failures don't break UI
- Automatic updates via Flow/LiveData
- No state management needed in UI

### Caching Strategies

#### 1. Cache-First Strategy

```kotlin
class ArticleRepository(
    private val articleApi: ArticleApi,
    private val memoryCache: MutableMap<String, Article> = mutableMapOf()
) {
    suspend fun getArticle(id: String): Article {
        // 1. Check memory cache
        memoryCache[id]?.let { return it }

        // 2. Fetch from network
        val article = articleApi.getArticle(id)

        // 3. Update cache
        memoryCache[id] = article

        return article
    }

    fun clearCache() {
        memoryCache.clear()
    }
}
```

#### 2. Time-Based Caching

```kotlin
class WeatherRepository(
    private val weatherApi: WeatherApi,
    private val weatherDao: WeatherDao
) {
    private val cacheValidityDuration = 10.minutes

    suspend fun getWeather(city: String): Weather {
        val cached = weatherDao.getWeather(city)

        // Check if cache is still valid
        if (cached != null && !isCacheExpired(cached.timestamp)) {
            return cached
        }

        // Fetch fresh data
        val weather = weatherApi.getWeather(city).copy(
            timestamp = System.currentTimeMillis()
        )
        weatherDao.insertWeather(weather)

        return weather
    }

    private fun isCacheExpired(timestamp: Long): Boolean {
        val now = System.currentTimeMillis()
        return now - timestamp > cacheValidityDuration.inWholeMilliseconds
    }
}
```

#### 3. Stale-While-Revalidate

```kotlin
class NewsRepository(
    private val newsApi: NewsApi,
    private val newsDao: NewsDao
) {
    fun getNews(): Flow<Resource<List<News>>> = flow {
        // 1. Emit loading
        emit(Resource.Loading())

        // 2. Emit cached data (might be stale)
        val cached = newsDao.getNews()
        if (cached.isNotEmpty()) {
            emit(Resource.Success(cached))
        }

        // 3. Fetch fresh data
        try {
            val fresh = newsApi.getNews()
            newsDao.insertNews(fresh)
            emit(Resource.Success(fresh))
        } catch (e: Exception) {
            if (cached.isEmpty()) {
                emit(Resource.Error(e.message))
            }
            // else: keep showing cached data
        }
    }
}

sealed class Resource<T> {
    class Loading<T> : Resource<T>()
    data class Success<T>(val data: T) : Resource<T>()
    data class Error<T>(val message: String?) : Resource<T>()
}
```

### Dependency Injection with Hilt

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DataModule {

    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi {
        return retrofit.create(UserApi::class.java)
    }

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }

    @Provides
    @Singleton
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }

    @Provides
    @Singleton
    fun provideUserRepository(
        userApi: UserApi,
        userDao: UserDao
    ): UserRepository {
        return UserRepositoryImpl(userApi, userDao)
    }
}

// ViewModel with injected repository
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    // ...
}
```

### Testing Repository

#### 1. Unit Testing with Fakes

```kotlin
class FakeUserApi : UserApi {
    private val users = mutableMapOf<String, User>()
    var shouldFail = false

    override suspend fun getUser(id: String): User {
        if (shouldFail) throw IOException("Network error")
        return users[id] ?: User(id, "Default User", "default@example.com")
    }

    fun addUser(user: User) {
        users[user.id] = user
    }
}

class UserRepositoryTest {
    private lateinit var fakeApi: FakeUserApi
    private lateinit var dao: UserDao
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val database = Room.inMemoryDatabaseBuilder(
            context,
            AppDatabase::class.java
        ).build()

        dao = database.userDao()
        fakeApi = FakeUserApi()
        repository = UserRepositoryImpl(fakeApi, dao)
    }

    @Test
    fun `getUser from network and cache in database`() = runTest {
        // Given
        val user = User("1", "John", "john@example.com")
        fakeApi.addUser(user)

        // When
        val result = repository.getUser("1")

        // Then
        assertEquals(user, result)
        assertEquals(user, dao.getUser("1"))
    }

    @Test
    fun `getUser falls back to database on network error`() = runTest {
        // Given
        val user = User("1", "John", "john@example.com")
        dao.insertUser(user)
        fakeApi.shouldFail = true

        // When
        val result = repository.getUser("1")

        // Then
        assertEquals(user, result)
    }
}
```

#### 2. Integration Testing

```kotlin
@HiltAndroidTest
class UserRepositoryIntegrationTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var repository: UserRepository

    @Inject
    lateinit var database: AppDatabase

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @After
    fun teardown() {
        database.close()
    }

    @Test
    fun `repository caches users from API`() = runTest {
        // When
        repository.refreshUsers()

        // Then
        val users = repository.observeUsers().first()
        assertTrue(users.isNotEmpty())
    }
}
```

### Real-World Example: E-Commerce Repository

```kotlin
interface ProductRepository {
    fun getProducts(): Flow<List<Product>>
    fun getProduct(id: String): Flow<Product>
    suspend fun refreshProducts()
    suspend fun searchProducts(query: String): List<Product>
    fun getFavorites(): Flow<List<Product>>
    suspend fun toggleFavorite(productId: String)
}

class ProductRepositoryImpl(
    private val productApi: ProductApi,
    private val productDao: ProductDao,
    private val favoriteDao: FavoriteDao
) : ProductRepository {

    override fun getProducts(): Flow<List<Product>> = flow {
        // Emit cached products immediately
        emitAll(productDao.observeProducts())

        // Refresh from network
        try {
            val products = productApi.getProducts()
            productDao.deleteAll()
            productDao.insertProducts(products)
        } catch (e: Exception) {
            Log.e("ProductRepository", "Failed to refresh products", e)
        }
    }

    override fun getProduct(id: String): Flow<Product> = flow {
        // Emit cached product
        productDao.getProduct(id)?.let { emit(it) }

        // Fetch fresh details
        try {
            val product = productApi.getProduct(id)
            productDao.insertProduct(product)
            emit(product)
        } catch (e: Exception) {
            // Already emitted cached, ignore error
        }
    }

    override suspend fun refreshProducts() {
        val products = productApi.getProducts()
        productDao.deleteAll()
        productDao.insertProducts(products)
    }

    override suspend fun searchProducts(query: String): List<Product> {
        // Search in database first
        val localResults = productDao.searchProducts("%$query%")

        if (localResults.isNotEmpty()) {
            return localResults
        }

        // Search in API if local search has no results
        return try {
            productApi.searchProducts(query)
        } catch (e: Exception) {
            emptyList()
        }
    }

    override fun getFavorites(): Flow<List<Product>> {
        return favoriteDao.observeFavorites()
            .map { favorites ->
                favorites.mapNotNull { favoriteId ->
                    productDao.getProduct(favoriteId)
                }
            }
    }

    override suspend fun toggleFavorite(productId: String) {
        val isFavorite = favoriteDao.isFavorite(productId)

        if (isFavorite) {
            favoriteDao.removeFavorite(productId)
        } else {
            favoriteDao.addFavorite(Favorite(productId))
        }
    }
}

// ViewModel
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ProductListUiState>(ProductListUiState.Loading)
    val uiState: StateFlow<ProductListUiState> = _uiState.asStateFlow()

    init {
        loadProducts()
    }

    private fun loadProducts() {
        viewModelScope.launch {
            repository.getProducts()
                .catch { e ->
                    _uiState.value = ProductListUiState.Error(e.message ?: "Unknown error")
                }
                .collect { products ->
                    _uiState.value = ProductListUiState.Success(products)
                }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            try {
                repository.refreshProducts()
            } catch (e: Exception) {
                // Show error, but keep existing data visible
                _uiState.value = ProductListUiState.Error(e.message ?: "Refresh failed")
            }
        }
    }

    fun search(query: String) {
        viewModelScope.launch {
            _uiState.value = ProductListUiState.Loading
            val results = repository.searchProducts(query)
            _uiState.value = ProductListUiState.Success(results)
        }
    }

    fun toggleFavorite(productId: String) {
        viewModelScope.launch {
            repository.toggleFavorite(productId)
        }
    }
}

sealed interface ProductListUiState {
    object Loading : ProductListUiState
    data class Success(val products: List<Product>) : ProductListUiState
    data class Error(val message: String) : ProductListUiState
}
```

### Advanced: Multiple Repositories

```kotlin
// Compose multiple repositories for complex operations
class CheckoutRepository(
    private val cartRepository: CartRepository,
    private val userRepository: UserRepository,
    private val orderRepository: OrderRepository,
    private val paymentRepository: PaymentRepository
) {
    suspend fun checkout(paymentMethod: PaymentMethod): Result<Order> {
        return try {
            // 1. Get cart items
            val cartItems = cartRepository.getCartItems()

            if (cartItems.isEmpty()) {
                return Result.failure(Exception("Cart is empty"))
            }

            // 2. Get user address
            val user = userRepository.getCurrentUser()
            val address = user.defaultAddress ?: return Result.failure(
                Exception("No default address")
            )

            // 3. Calculate total
            val total = cartItems.sumOf { it.price * it.quantity }

            // 4. Process payment
            val paymentResult = paymentRepository.processPayment(
                amount = total,
                method = paymentMethod
            )

            if (!paymentResult.isSuccess) {
                return Result.failure(Exception("Payment failed"))
            }

            // 5. Create order
            val order = orderRepository.createOrder(
                items = cartItems,
                address = address,
                paymentId = paymentResult.getOrNull()?.id ?: ""
            )

            // 6. Clear cart
            cartRepository.clearCart()

            Result.success(order)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Best Practices

1. **Repository per entity** - `UserRepository`, `ProductRepository`, not `DataRepository`
2. **Return Flow for reactive data** - Automatic UI updates
3. **Return suspend functions for one-shot operations** - Login, update profile
4. **Database as single source of truth** - Network updates database, UI observes database
5. **Handle errors gracefully** - Show cached data even on network errors
6. **Use interfaces** - Easy to mock for testing
7. **Inject repositories** - Don't create them manually
8. **Keep repository logic simple** - Move business logic to use cases if needed
9. **Cache strategically** - Not all data needs caching
10. **Test thoroughly** - Unit test with fakes, integration test with real database

### Common Pitfalls

#### 1. Exposing Data Sources

```kotlin
// BAD: Exposes internal data source
class UserRepository(private val userDao: UserDao) {
    fun getUserDao() = userDao  // Don't do this!
}

// GOOD: Only expose clean API
class UserRepository(private val userDao: UserDao) {
    fun observeUsers(): Flow<List<User>> = userDao.observeUsers()
}
```

#### 2. Not Using Single Source of Truth

```kotlin
// BAD: Multiple sources of truth
class ProductRepository {
    suspend fun getProducts(): List<Product> {
        return if (isNetworkAvailable()) {
            api.getProducts()  // Returns network data
        } else {
            dao.getProducts()  // Returns database data
        }
    }
}

// GOOD: Database is single source of truth
class ProductRepository {
    fun getProducts(): Flow<List<Product>> = flow {
        emitAll(dao.observeProducts())  // Always from database

        try {
            val products = api.getProducts()
            dao.insertProducts(products)  // Updates the flow
        } catch (e: Exception) {
            // Using cached data
        }
    }
}
```

#### 3. Blocking Operations

```kotlin
// BAD: Blocking operation on main thread
class UserRepository {
    fun getUser(id: String): User {
        return runBlocking {  // Don't do this!
            api.getUser(id)
        }
    }
}

// GOOD: Suspend function
class UserRepository {
    suspend fun getUser(id: String): User {
        return api.getUser(id)
    }
}
```

---

## Ответ (RU)

**Repository Pattern** - это архитектурный паттерн, который абстрагирует источники данных (сеть, база данных, кэш) за чистым API, предоставляя единый источник истины и разделяя бизнес-логику от логики доступа к данным.

### Зачем нужен Repository Pattern?

**Проблемы, которые он решает:**
1. **Связанность с источниками данных** - ViewModel не должна знать откуда данные: из API или БД
2. **Дублирование логики** - Логика кэширования не должна повторяться на разных экранах
3. **Сложность тестирования** - Сложно тестировать ViewModel с реальными источниками данных
4. **Комплексность** - Управление множественными источниками данных становится неуправляемым

### Базовый Repository

```kotlin
interface UserRepository {
    suspend fun getUser(userId: String): User
    suspend fun updateUser(user: User)
}

class UserRepositoryImpl(
    private val userApi: UserApi,
    private val userDao: UserDao
) : UserRepository {

    override suspend fun getUser(userId: String): User {
        return try {
            // Попытка загрузить из сети
            val user = userApi.getUser(userId)
            // Кэшировать в БД
            userDao.insertUser(user)
            user
        } catch (e: IOException) {
            // Fallback к БД
            userDao.getUser(userId) ?: throw e
        }
    }

    override suspend fun updateUser(user: User) {
        userApi.updateUser(user)
        userDao.insertUser(user)
    }
}
```

### Repository в MVVM архитектуре

```
View (Activity/Fragment/Composable)
    ↓ наблюдает за состоянием
ViewModel
    ↓ вызывает repository
Repository
    ↓ координирует источники данных
DataSources (API, Database, Cache)
```

### Единый источник истины (Single Source of Truth)

**База данных как источник истины** - Сеть обновляет БД, UI наблюдает за БД:

```kotlin
class ProductRepository(
    private val productApi: ProductApi,
    private val productDao: ProductDao
) {
    // База данных - единый источник истины
    fun getProducts(): Flow<List<Product>> = flow {
        // 1. Эмитить из БД (источник истины)
        emitAll(productDao.observeProducts())

        // 2. Обновить из сети в фоне
        try {
            val products = productApi.getProducts()
            productDao.insertProducts(products)  // Обновляет flow выше
        } catch (e: Exception) {
            // Игнорировать - использовать кэшированные данные
        }
    }
}
```

**Преимущества:**
- UI всегда показывает консистентные данные
- Сбои сети не ломают UI
- Автоматические обновления через Flow/LiveData
- Не нужно управлять состоянием в UI

### Стратегии кэширования

#### 1. Cache-First Strategy (Кэш сначала)

```kotlin
class ArticleRepository(
    private val articleApi: ArticleApi,
    private val memoryCache: MutableMap<String, Article> = mutableMapOf()
) {
    suspend fun getArticle(id: String): Article {
        // 1. Проверить кэш в памяти
        memoryCache[id]?.let { return it }

        // 2. Загрузить из сети
        val article = articleApi.getArticle(id)

        // 3. Обновить кэш
        memoryCache[id] = article

        return article
    }
}
```

#### 2. Time-Based Caching (Кэширование по времени)

```kotlin
class WeatherRepository(
    private val weatherApi: WeatherApi,
    private val weatherDao: WeatherDao
) {
    private val cacheValidityDuration = 10.minutes

    suspend fun getWeather(city: String): Weather {
        val cached = weatherDao.getWeather(city)

        // Проверить валидность кэша
        if (cached != null && !isCacheExpired(cached.timestamp)) {
            return cached
        }

        // Загрузить свежие данные
        val weather = weatherApi.getWeather(city).copy(
            timestamp = System.currentTimeMillis()
        )
        weatherDao.insertWeather(weather)

        return weather
    }

    private fun isCacheExpired(timestamp: Long): Boolean {
        val now = System.currentTimeMillis()
        return now - timestamp > cacheValidityDuration.inWholeMilliseconds
    }
}
```

### Dependency Injection с Hilt

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DataModule {

    @Provides
    @Singleton
    fun provideUserRepository(
        userApi: UserApi,
        userDao: UserDao
    ): UserRepository {
        return UserRepositoryImpl(userApi, userDao)
    }
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    // ...
}
```

### Best Practices (Лучшие практики)

1. **Repository на каждую сущность** - `UserRepository`, `ProductRepository`, не `DataRepository`
2. **Возвращать Flow для реактивных данных** - Автоматические обновления UI
3. **Возвращать suspend функции для one-shot операций** - Логин, обновление профиля
4. **База данных как единый источник истины** - Сеть обновляет БД, UI наблюдает за БД
5. **Обрабатывать ошибки gracefully** - Показывать кэшированные данные даже при ошибках сети
6. **Использовать интерфейсы** - Легко мокировать для тестирования
7. **Инжектировать repositories** - Не создавать их вручную
8. **Держать логику repository простой** - Переносить бизнес-логику в use cases при необходимости
9. **Кэшировать стратегически** - Не все данные нужно кэшировать
10. **Тестировать тщательно** - Unit тесты с fakes, integration тесты с реальной БД

---

## Related Questions

### Related (Medium)
- [[q-usecase-pattern-android--android--medium]] - Architecture
- [[q-repository-multiple-sources--android--medium]] - Architecture

### Advanced (Harder)
- [[q-clean-architecture-android--android--hard]] - Architecture
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-multi-module-best-practices--android--hard]] - Architecture

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

## References

- [Data layer - Android](https://developer.android.com/topic/architecture/data-layer)
- [Repository pattern](https://developer.android.com/codelabs/basic-android-kotlin-training-repository-pattern)
- [Guide to app architecture](https://developer.android.com/topic/architecture)

## MOC Links

- [[moc-android]]
