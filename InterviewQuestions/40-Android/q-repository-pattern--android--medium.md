---
id: android-070
title: Repository Pattern in Android / Паттерн Repository в Android
aliases: [Repository Pattern in Android, Паттерн Repository в Android]
topic: android
subtopics:
  - architecture-clean
  - architecture-mvvm
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
source: internal
source_note: Created for vault completeness
status: draft
moc: moc-android
related:
  - c-clean-architecture
  - c-mvvm
  - c-viewmodel
  - q-clean-architecture-android--android--hard
  - q-factory-pattern-android--android--medium
  - q-repository-multiple-sources--android--medium
  - q-usecase-pattern-android--android--medium
created: 2025-10-12
updated: 2025-11-11
tags: [android/architecture-clean, android/architecture-mvvm, difficulty/medium, en, ru]

date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)
> Что такое паттерн Repository в Android? Как он абстрагирует источники данных, предоставляет единый источник истины и работает с ViewModels?

# Question (EN)
> What is the Repository pattern in Android? How does it abstract data sources, provide a single source of truth, and work with ViewModels?

## Ответ (RU)

**Repository Pattern** — это архитектурный паттерн, который абстрагирует источники данных (сеть, база данных, кэш) за чистым API, предоставляя единый источник истины и разделяя бизнес-логику и логику доступа к данным.

### Зачем Нужен Repository Pattern?

**Проблемы, которые он решает:**
1. **Связанность с источниками данных** — `ViewModel` не должна знать, откуда приходят данные: из API или БД.
2. **Дублирование логики** — логика кэширования, маппинга и обработки ошибок не должна повторяться на разных экранах.
3. **Сложность тестирования** — трудно тестировать `ViewModel` с реальными источниками данных.
4. **Рост комплексности** — без отдельного слоя координации работа с несколькими источниками данных становится неуправляемой.

**Преимущества:**
- Единый источник истины.
- Централизованная логика работы с данными и кэшем.
- Упрощённое тестирование (mock/fake репозитория).
- Чёткое разделение ответственности.
- Взаимозаменяемые источники данных.

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
            // Пробуем загрузить из сети
            val user = userApi.getUser(userId)
            // Кэшируем в БД
            userDao.insertUser(user)
            user
        } catch (e: IOException) {
            // Переходим к данным из БД при ошибке сети
            userDao.getUser(userId) ?: throw e
        }
    }

    override suspend fun updateUser(user: User) {
        // Обновляем удалённый источник и кэшируем локально
        userApi.updateUser(user)
        userDao.insertUser(user)
    }
}
```

### Repository В MVVM-архитектуре

```text
View (Activity/Fragment/Composable)
    ↓ наблюдает состояние
ViewModel
    ↓ вызывает repository
Repository
    ↓ координирует источники данных
DataSources (API, Database, Cache)
```

**Пример:**

```kotlin
// 1. Источники данных
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User

    @GET("users")
    suspend fun getUsers(): List<User>

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: User)
}

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>
}

// 2. Репозиторий (упрощённый, сеть + БД)
class UserRepository(
    private val userApi: UserApi,
    private val userDao: UserDao
) {
    fun getUser(userId: String): Flow<User> = flow {
        // Сначала пробуем отдать кэшированные данные, если есть
        userDao.getUser(userId)?.let { emit(it) }

        // Затем обновляем данные из сети и обновляем кэш
        try {
            val freshUser = userApi.getUser(userId)
            userDao.insertUser(freshUser)
            emit(freshUser)
        } catch (e: Exception) {
            // В этом примере оставляем кэшированные данные; в реальном коде явно обрабатывайте ошибки
            if (userDao.getUser(userId) == null) throw e
        }
    }

    fun observeUsers(): Flow<List<User>> = userDao.observeUsers()

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

    when (val state = uiState) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> UserContent(state.user)
        is UiState.Error -> ErrorMessage(state.message)
    }
}
```

### Единый Источник Истины (Single Source of Truth)

Обычно в Android в качестве единого источника истины используют локальную БД:
- Репозиторий записывает результаты сетевых запросов в базу данных.
- UI наблюдает данные из БД (`Flow`/`LiveData`), а не обращается напрямую к сети.

```kotlin
class ProductRepository(
    private val productApi: ProductApi,
    private val productDao: ProductDao
) {
    // База данных — единый источник истины
    fun getProducts(): Flow<List<Product>> = flow {
        // 1. Эмитим данные из БД
        emitAll(productDao.observeProducts())

        // 2. Обновляем данные из сети в фоне
        try {
            val products = productApi.getProducts()
            productDao.insertProducts(products)
        } catch (e: Exception) {
            // Продолжаем использовать кэш; при необходимости дополнительно сигналим об ошибке
        }
    }

    suspend fun refreshProducts() {
        val products = productApi.getProducts()
        productDao.insertProducts(products)
    }
}
```

**Преимущества:**
- UI всегда читает из одного консистентного источника.
- Сетевые ошибки не ломают UI при наличии кэша.
- Автоматические обновления через `Flow`/`LiveData`.
- Меньше состояния, управляемого на уровне UI.

### Стратегии Кэширования

Стратегии реализуются внутри репозиториев.

#### 1. Cache-first (сначала кэш)

```kotlin
class ArticleRepository(
    private val articleApi: ArticleApi,
    private val memoryCache: MutableMap<String, Article> = mutableMapOf()
) {
    suspend fun getArticle(id: String): Article {
        // 1. Проверяем кэш в памяти
        memoryCache[id]?.let { return it }

        // 2. Загружаем из сети
        val article = articleApi.getArticle(id)

        // 3. Обновляем кэш
        memoryCache[id] = article

        return article
    }

    fun clearCache() {
        memoryCache.clear()
    }
}
```

#### 2. Кэширование По Времени

```kotlin
class WeatherRepository(
    private val weatherApi: WeatherApi,
    private val weatherDao: WeatherDao
) {
    private val cacheValidityDuration = 10.minutes

    suspend fun getWeather(city: String): Weather {
        val cached = weatherDao.getWeather(city)

        // Проверяем, не истёк ли срок действия кэша
        if (cached != null && !isCacheExpired(cached.timestamp)) {
            return cached
        }

        // Загружаем свежие данные
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

#### 3. Stale-While-Revalidate (устаревшие Данные + обновление)

```kotlin
class NewsRepository(
    private val newsApi: NewsApi,
    private val newsDao: NewsDao
) {
    fun getNews(): Flow<Resource<List<News>>> = flow {
        // 1. Эмитим состояние загрузки
        emit(Resource.Loading())

        // 2. Эмитим кэшированные данные (могут быть устаревшими)
        val cached = newsDao.getNews()
        if (cached.isNotEmpty()) {
            emit(Resource.Success(cached))
        }

        // 3. Пытаемся получить свежие данные
        try {
            val fresh = newsApi.getNews()
            newsDao.insertNews(fresh)
            emit(Resource.Success(fresh))
        } catch (e: Exception) {
            if (cached.isEmpty()) {
                emit(Resource.Error(e.message))
            }
            // Иначе продолжаем показывать кэшированные данные
        }
    }
}

sealed class Resource<T> {
    class Loading<T> : Resource<T>()
    data class Success<T>(val data: T) : Resource<T>()
    data class Error<T>(val message: String?) : Resource<T>()
}
```

### Dependency Injection С Hilt

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

// ViewModel с внедрённым репозиторием
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    // ...
}
```

### Тестирование Repository

#### 1. Unit-тесты С Фейковыми Реализациями

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

#### 2. Интеграционные Тесты (пример)

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
        val users = database.userDao().observeUsers().first()
        assertTrue(users.isNotEmpty())
    }
}
```

### Реальный Пример: Репозиторий Для E-commerce

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
        // Эмитим продукты из БД
        emitAll(productDao.observeProducts())

        // Обновляем из сети
        try {
            val products = productApi.getProducts()
            productDao.deleteAll()
            productDao.insertProducts(products)
        } catch (e: Exception) {
            Log.e("ProductRepository", "Failed to refresh products", e)
        }
    }

    override fun getProduct(id: String): Flow<Product> = flow {
        // Эмитим кэшированный продукт, если есть
        productDao.getProduct(id)?.let { emit(it) }

        // Загружаем актуальные данные
        try {
            val product = productApi.getProduct(id)
            productDao.insertProduct(product)
            emit(product)
        } catch (e: Exception) {
            // Если в БД нет данных — пробрасываем ошибку
            if (productDao.getProduct(id) == null) throw e
        }
    }

    override suspend fun refreshProducts() {
        val products = productApi.getProducts()
        productDao.deleteAll()
        productDao.insertProducts(products)
    }

    override suspend fun searchProducts(query: String): List<Product> {
        // Сначала ищем в БД
        val localResults = productDao.searchProducts("%$query%")
        if (localResults.isNotEmpty()) return localResults

        // Фолбэк на API
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
                // Показываем ошибку, но сохраняем текущие данные
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

### Продвинутый Пример: Композиция Нескольких Репозиториев

```kotlin
// Композиция нескольких репозиториев для сложной операции
class CheckoutRepository(
    private val cartRepository: CartRepository,
    private val userRepository: UserRepository,
    private val orderRepository: OrderRepository,
    private val paymentRepository: PaymentRepository
) {
    suspend fun checkout(paymentMethod: PaymentMethod): Result<Order> {
        return try {
            // 1. Получаем товары в корзине
            val cartItems = cartRepository.getCartItems()
            if (cartItems.isEmpty()) {
                return Result.failure(Exception("Cart is empty"))
            }

            // 2. Получаем адрес пользователя
            val user = userRepository.getCurrentUser()
            val address = user.defaultAddress
                ?: return Result.failure(Exception("No default address"))

            // 3. Считаем итоговую сумму
            val total = cartItems.sumOf { it.price * it.quantity }

            // 4. Обрабатываем платёж
            val paymentResult = paymentRepository.processPayment(
                amount = total,
                method = paymentMethod
            )
            if (!paymentResult.isSuccess) {
                return Result.failure(Exception("Payment failed"))
            }

            // 5. Создаём заказ
            val order = orderRepository.createOrder(
                items = cartItems,
                address = address,
                paymentId = paymentResult.getOrNull()?.id ?: ""
            )

            // 6. Очищаем корзину
            cartRepository.clearCart()

            Result.success(order)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Лучшие Практики

1. Отдельный репозиторий на сущность/фичу — `UserRepository`, `ProductRepository` и т.п., а не один огромный `DataRepository`.
2. Для реактивных данных — `Flow`/`LiveData`, чтобы UI подписывался и автоматически обновлялся.
3. Для разовых операций — `suspend`-функции (логин, отправка формы, обновление профиля).
4. Явный единый источник истины — чаще всего база данных; сеть только синхронизирует её.
5. Явная обработка ошибок — `Result`/`Resource` или доменные ошибки, а не глухое подавление исключений.
6. Использовать интерфейсы для тестируемости и подмены реализаций.
7. Внедрять репозитории через DI, а не создавать глубоко в UI-слое.
8. Держать репозиторий сфокусированным на координации источников данных; тяжёлую бизнес-логику выносить в use cases/интеракторы.
9. Кэшировать осознанно — там, где это даёт выигрыш.
10. Тщательно тестировать — unit-тесты с фейками/моками, интеграционные тесты с реальной БД/DI.

### Типичные Ошибки

#### 1. Экспонирование Внутренних Источников Данных

```kotlin
// ПЛОХО: раскрываем внутренний источник данных
class UserRepository(private val userDao: UserDao) {
    fun getUserDao() = userDao // Так делать не нужно
}

// ХОРОШО: предоставляем только чистый API
class UserRepository(private val userDao: UserDao) {
    fun observeUsers(): Flow<List<User>> = userDao.observeUsers()
}
```

#### 2. Отсутствие Единого Источника Истины

```kotlin
// ПЛОХО: два источника истины
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao
) {
    suspend fun getProducts(): List<Product> {
        return if (isNetworkAvailable()) {
            api.getProducts()
        } else {
            dao.getProducts()
        }
    }
}

// ХОРОШО: база данных как единый источник истины
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao
) {
    fun getProducts(): Flow<List<Product>> = flow {
        emitAll(dao.observeProducts())

        try {
            val products = api.getProducts()
            dao.insertProducts(products)
        } catch (e: Exception) {
            // Продолжаем использовать кэш; при необходимости сигналим об ошибке
        }
    }
}
```

#### 3. Блокирующие Операции

```kotlin
// ПЛОХО: блокируем главный поток
class UserRepository(private val api: UserApi) {
    fun getUser(id: String): User {
        return runBlocking { // Так делать нельзя на главном потоке Android
            api.getUser(id)
        }
    }
}

// ХОРОШО: suspend-функция
class UserRepository(private val api: UserApi) {
    suspend fun getUser(id: String): User {
        return api.getUser(id)
    }
}
```

## Answer (EN)

**Repository Pattern** is an architectural pattern that abstracts data sources (network, database, cache) behind a clean API, providing a single source of truth and separating business logic from data access logic.

### Why Repository Pattern?

**Problems it solves:**
1. **Data source coupling** - ViewModels shouldn't know if data comes from API or database.
2. **Duplicate logic** - Caching and mapping logic shouldn't be repeated across screens.
3. **Testing difficulty** - Hard to test ViewModels with real data sources.
4. **Complexity** - Managing multiple data sources becomes unmanageable without a coordination layer.

**Benefits:**
- Single source of truth.
- Centralized caching and data logic.
- Easy to test (mock or fake repository).
- Clean separation of concerns.
- Swappable data sources (e.g., change API/DB implementation without touching UI).

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
        // Update remote source and cache locally
        userApi.updateUser(user)
        userDao.insertUser(user)
    }
}
```

### Repository in MVVM Architecture

```text
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

    @GET("users")
    suspend fun getUsers(): List<User>

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: User)
}

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>
}

// 2. Repository (simplified, network+DB)
class UserRepository(
    private val userApi: UserApi,
    private val userDao: UserDao
) {
    fun getUser(userId: String): Flow<User> = flow {
        // Emit cached data immediately, if available
        userDao.getUser(userId)?.let { emit(it) }

        // Fetch fresh data and update cache
        try {
            val freshUser = userApi.getUser(userId)
            userDao.insertUser(freshUser)
            emit(freshUser)
        } catch (e: Exception) {
            // In this example we keep showing cached data if any; in real apps handle errors explicitly.
            if (userDao.getUser(userId) == null) throw e
        }
    }

    fun observeUsers(): Flow<List<User>> = userDao.observeUsers()

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

    when (val state = uiState) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> UserContent(state.user)
        is UiState.Error -> ErrorMessage(state.message)
    }
}
```

### Single Source of Truth

A common approach is to treat the local database as the single source of truth (SSOT):
- Repository writes remote updates into the database.
- UI observes database (via `Flow`/`LiveData`) instead of talking directly to network.

```kotlin
class ProductRepository(
    private val productApi: ProductApi,
    private val productDao: ProductDao
) {
    // Database is the single source of truth
    fun getProducts(): Flow<List<Product>> = flow {
        // 1. Emit from database
        emitAll(productDao.observeProducts())

        // 2. Refresh from network in background
        try {
            val products = productApi.getProducts()
            productDao.insertProducts(products) // Updates the observed Flow
        } catch (e: Exception) {
            // In SSOT pattern, we keep using cached data; consider surfacing error if needed.
        }
    }

    suspend fun refreshProducts() {
        val products = productApi.getProducts()
        productDao.insertProducts(products)
    }
}
```

### Caching Strategies

These strategies are implemented inside repositories.

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
            // Otherwise keep showing cached data
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

#### 2. Integration Testing (example)

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
        val users = database.userDao().observeUsers().first()
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
        // Emit cached products from DB
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
        // Emit cached product, if any
        productDao.getProduct(id)?.let { emit(it) }

        // Fetch fresh details
        try {
            val product = productApi.getProduct(id)
            productDao.insertProduct(product)
            emit(product)
        } catch (e: Exception) {
            // Keep showing cached data if available
            if (productDao.getProduct(id) == null) throw e
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
        if (localResults.isNotEmpty()) return localResults

        // Fallback to API
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
            val address = user.defaultAddress
                ?: return Result.failure(Exception("No default address"))

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

1. **Repository per entity/feature** - `UserRepository`, `ProductRepository`, etc., not one giant `DataRepository`.
2. **Expose Flows for reactive data** - Allow UI to observe updates.
3. **Use suspend functions for one-shot operations** - Login, updates, commands.
4. **Prefer a clear single source of truth** - Often the database; sync network into it.
5. **Handle errors explicitly** - Prefer returning Result/Resource or domain errors instead of swallowing exceptions.
6. **Use interfaces** - For testability and swapping implementations.
7. **Inject repositories** - Use DI rather than manual construction deep in the UI.
8. **Keep repository focused** - Coordination of data sources; move complex business rules to use cases/interactors.
9. **Cache strategically** - Only where it provides value.
10. **Test thoroughly** - Unit tests with fakes/mocks; integration tests with real DB/network stubs.

### Common Pitfalls

#### 1. Exposing Data Sources

```kotlin
// BAD: Exposes internal data source
class UserRepository(private val userDao: UserDao) {
    fun getUserDao() = userDao // Don't do this!
}

// GOOD: Only expose a clean API
class UserRepository(private val userDao: UserDao) {
    fun observeUsers(): Flow<List<User>> = userDao.observeUsers()
}
```

#### 2. Not Using Single Source of Truth

```kotlin
// BAD: Multiple sources of truth
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao
) {
    suspend fun getProducts(): List<Product> {
        return if (isNetworkAvailable()) {
            api.getProducts() // Raw network data
        } else {
            dao.getProducts() // Raw DB data
        }
    }
}

// GOOD: Database as single source of truth
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao
) {
    fun getProducts(): Flow<List<Product>> = flow {
        emitAll(dao.observeProducts()) // Always from DB

        try {
            val products = api.getProducts()
            dao.insertProducts(products) // Updates the observed Flow
        } catch (e: Exception) {
            // Keep using cached data; surface error as appropriate
        }
    }
}
```

#### 3. Blocking Operations

```kotlin
// BAD: Blocking network on main thread
class UserRepository(private val api: UserApi) {
    fun getUser(id: String): User {
        return runBlocking { // Don't do this on Android main thread!
            api.getUser(id)
        }
    }
}

// GOOD: Suspend function
class UserRepository(private val api: UserApi) {
    suspend fun getUser(id: String): User {
        return api.getUser(id)
    }
}
```

## Follow-ups

- [[q-clean-architecture-android--android--hard]]
- [[q-repository-multiple-sources--android--medium]]
- Как реализовать репозиторий для оффлайн-first приложения с двусторонней синхронизацией?
- Как разделить ответственность между Repository и UseCase в сложном домене?
- Как тестировать репозиторий при сложных сценариях ошибок сети и БД?

## References

- [Data layer - Android](https://developer.android.com/topic/architecture/data-layer)
- [Repository pattern](https://developer.android.com/codelabs/basic-android-kotlin-training-repository-pattern)
- [Guide to app architecture](https://developer.android.com/topic/architecture)

## Related Questions

### Prerequisites / Concepts

- [[c-clean-architecture]]
- [[c-mvvm]]
- [[c-viewmodel]]

### Related (Medium)
- [[q-usecase-pattern-android--android--medium]] - Architecture
- [[q-repository-multiple-sources--android--medium]] - Architecture

### Advanced (Harder)
- [[q-clean-architecture-android--android--hard]] - Architecture
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-multi-module-best-practices--android--hard]] - Architecture

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

## MOC Links
- [[moc-android]]