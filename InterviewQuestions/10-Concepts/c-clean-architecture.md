---
id: "20251025-143200"
title: "Clean Architecture / Чистая Архитектура"
aliases: ["Clean Architecture", "Clean Code Architecture", "Архитектура Роберта Мартина", "Чистая Архитектура"]
summary: "Software architecture pattern with layered structure promoting independence, testability, and maintainability by separating concerns into Domain, Data, and Presentation layers"
topic: "android"
subtopics: ["architecture-patterns", "clean-architecture", "domain-layer"]
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
tags: ["android", "architecture-patterns", "clean-architecture", "concept", "difficulty/medium", "domain-layer", "repository", "use-cases"]
date created: Saturday, October 25th 2025, 12:52:57 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Clean Architecture / Чистая Архитектура

## Summary (EN)

Clean Architecture is a software architecture pattern introduced by Robert C. Martin (Uncle Bob) that organizes code into concentric layers with strict dependency rules. The core principle is the Dependency Rule: dependencies point inward, with outer layers depending on inner layers, never the reverse. This creates a highly testable, maintainable, and framework-independent codebase. In Android, Clean Architecture typically consists of three layers: Domain (business logic, use cases, entities), Data (repositories, data sources), and Presentation (ViewModels, UI). The Domain layer is the innermost, containing pure Kotlin code with no Android dependencies, making it highly testable and reusable.

## Краткое Описание (RU)

Clean Architecture - это паттерн архитектуры программного обеспечения, представленный Робертом Мартином (Дядя Боб), который организует код в концентрические слои со строгими правилами зависимостей. Основной принцип - Правило Зависимостей: зависимости направлены внутрь, внешние слои зависят от внутренних, никогда наоборот. Это создает высоко тестируемую, поддерживаемую и независимую от фреймворков кодовую базу. В Android Clean Architecture обычно состоит из трех слоев: Domain (бизнес-логика, use cases, entities), Data (репозитории, источники данных) и Presentation (ViewModels, UI). Слой Domain является самым внутренним, содержит чистый Kotlin код без зависимостей от Android, что делает его высоко тестируемым и переиспользуемым.

## Key Points (EN)

- **Dependency Rule**: Dependencies point inward (outer → inner), never reversed
- **Layer independence**: Inner layers know nothing about outer layers
- **Framework independence**: Business logic doesn't depend on Android/UI frameworks
- **Testability**: Each layer can be tested in isolation
- **Three main layers**: Presentation → Domain ← Data
- **Use Cases**: Encapsulate single business operations (Domain layer)
- **Entities**: Business models representing core concepts
- **Repository pattern**: Abstract data sources in Data layer
- **Pure Kotlin domain**: Domain layer has no Android dependencies

## Ключевые Моменты (RU)

- **Правило зависимостей**: Зависимости направлены внутрь (внешний → внутренний), никогда наоборот
- **Независимость слоев**: Внутренние слои ничего не знают о внешних
- **Независимость от фреймворков**: Бизнес-логика не зависит от Android/UI фреймворков
- **Тестируемость**: Каждый слой можно тестировать изолированно
- **Три основных слоя**: Presentation → Domain ← Data
- **Use Cases**: Инкапсулируют отдельные бизнес-операции (слой Domain)
- **Entities**: Бизнес-модели, представляющие основные концепции
- **Паттерн Repository**: Абстрагирует источники данных в слое Data
- **Чистый Kotlin domain**: Слой Domain не имеет зависимостей от Android

## Clean Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│              Presentation Layer                     │
│  (UI, ViewModels, Adapters, Activities, Fragments)  │
│  - Android framework dependencies                   │
│  - Depends on: Domain                               │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│                Domain Layer                         │
│        (Use Cases, Entities, Repositories)          │
│  - Pure Kotlin (no Android dependencies)            │
│  - Business logic                                   │
│  - Independent of frameworks                        │
└────────────────────┬────────────────────────────────┘
                     ↑
                     │ implements
┌─────────────────────────────────────────────────────┐
│                 Data Layer                          │
│  (Repository Impl, Data Sources, API, Database)     │
│  - Android/framework dependencies allowed           │
│  - Depends on: Domain (implements interfaces)       │
└─────────────────────────────────────────────────────┘
```

## The Dependency Rule

**CRITICAL**: Dependencies always point INWARD
- Presentation depends on Domain
- Data depends on Domain (implements interfaces)
- Domain depends on NOTHING (pure Kotlin)

```kotlin
// ✅ CORRECT
// Presentation → Domain
class UserViewModel(
    private val getUserUseCase: GetUserUseCase  // Domain dependency
) : ViewModel()

// Data → Domain (implements interface)
class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {  // Implements Domain interface
    // ...
}

// ❌ WRONG
// Domain → Data (breaks dependency rule!)
class GetUserUseCase(
    private val userApi: UserApi  // Data layer dependency - FORBIDDEN!
)

// Domain → Presentation (breaks dependency rule!)
class User {
    var viewModel: UserViewModel? = null  // Presentation dependency - FORBIDDEN!
}
```

## Layer 1: Domain Layer (Innermost)

### Entities (Business Models)

```kotlin
// domain/model/User.kt
data class User(
    val id: String,
    val name: String,
    val email: String,
    val isActive: Boolean
) {
    fun isValid(): Boolean {
        return email.contains("@") && name.isNotBlank()
    }
}

// domain/model/Order.kt
data class Order(
    val id: String,
    val userId: String,
    val items: List<OrderItem>,
    val totalAmount: Double,
    val status: OrderStatus
) {
    fun canBeCancelled(): Boolean {
        return status == OrderStatus.PENDING || status == OrderStatus.PROCESSING
    }

    fun calculateTotal(): Double {
        return items.sumOf { it.price * it.quantity }
    }
}

enum class OrderStatus {
    PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED
}
```

### Repository Interfaces (defined in Domain)

```kotlin
// domain/repository/UserRepository.kt
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    suspend fun getUsers(): Result<List<User>>
    suspend fun updateUser(user: User): Result<Unit>
    fun observeUser(id: String): Flow<User>
}

// domain/repository/OrderRepository.kt
interface OrderRepository {
    suspend fun getOrders(userId: String): Result<List<Order>>
    suspend fun createOrder(order: Order): Result<String>
    suspend fun cancelOrder(orderId: String): Result<Unit>
}
```

### Use Cases (Business Operations)

```kotlin
// domain/usecase/GetUserUseCase.kt
class GetUserUseCase(
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(userId: String): Result<User> {
        return userRepository.getUser(userId)
    }
}

// domain/usecase/LoginUseCase.kt
class LoginUseCase(
    private val userRepository: UserRepository,
    private val authRepository: AuthRepository,
    private val analytics: Analytics
) {
    suspend operator fun invoke(email: String, password: String): Result<User> {
        return try {
            // Validation
            if (!email.contains("@")) {
                return Result.failure(InvalidEmailException())
            }

            // Authenticate
            val token = authRepository.login(email, password)

            // Fetch user
            val user = userRepository.getCurrentUser(token)

            // Analytics
            analytics.logEvent("user_login", mapOf("userId" to user.id))

            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// domain/usecase/CreateOrderUseCase.kt
class CreateOrderUseCase(
    private val orderRepository: OrderRepository,
    private val userRepository: UserRepository,
    private val paymentRepository: PaymentRepository
) {
    suspend operator fun invoke(
        userId: String,
        items: List<OrderItem>
    ): Result<String> {
        return try {
            // Validate user
            val user = userRepository.getUser(userId).getOrThrow()
            if (!user.isActive) {
                return Result.failure(InactiveUserException())
            }

            // Create order
            val order = Order(
                id = generateOrderId(),
                userId = userId,
                items = items,
                totalAmount = items.sumOf { it.price * it.quantity },
                status = OrderStatus.PENDING
            )

            // Process payment
            val paymentResult = paymentRepository.processPayment(order.totalAmount)
            if (!paymentResult.isSuccess) {
                return Result.failure(PaymentFailedException())
            }

            // Save order
            orderRepository.createOrder(order)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun generateOrderId(): String {
        return "ORD-${System.currentTimeMillis()}"
    }
}
```

## Layer 2: Data Layer

### Repository Implementations

```kotlin
// data/repository/UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val userApi: UserApiService,
    private val userDao: UserDao,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : UserRepository {  // Implements Domain interface

    override suspend fun getUser(id: String): Result<User> = withContext(ioDispatcher) {
        try {
            // Network first
            val userDto = userApi.getUser(id)
            val user = userDto.toDomainModel()

            // Cache
            userDao.insert(user.toEntity())

            Result.success(user)
        } catch (e: Exception) {
            // Fallback to cache
            val cached = userDao.getUserById(id)
            if (cached != null) {
                Result.success(cached.toDomainModel())
            } else {
                Result.failure(e)
            }
        }
    }

    override suspend fun getUsers(): Result<List<User>> = withContext(ioDispatcher) {
        try {
            val users = userApi.getUsers().map { it.toDomainModel() }
            userDao.insertAll(users.map { it.toEntity() })
            Result.success(users)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateUser(user: User): Result<Unit> = withContext(ioDispatcher) {
        try {
            userApi.updateUser(user.toDto())
            userDao.update(user.toEntity())
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun observeUser(id: String): Flow<User> {
        return userDao.observeUser(id).map { it.toDomainModel() }
    }
}
```

### Data Sources

```kotlin
// data/source/remote/UserApiService.kt
interface UserApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @GET("users")
    suspend fun getUsers(): List<UserDto>

    @PUT("users/{id}")
    suspend fun updateUser(@Body user: UserDto): UserDto
}

// data/source/local/UserDao.kt
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUserById(id: String): UserEntity?

    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<UserEntity>

    @Query("SELECT * FROM users WHERE id = :id")
    fun observeUser(id: String): Flow<UserEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(users: List<UserEntity>)

    @Update
    suspend fun update(user: UserEntity)
}
```

### Data Mappers

```kotlin
// data/mapper/UserMapper.kt

// DTO → Domain
fun UserDto.toDomainModel(): User {
    return User(
        id = this.id,
        name = this.fullName,
        email = this.emailAddress,
        isActive = this.status == "active"
    )
}

// Domain → DTO
fun User.toDto(): UserDto {
    return UserDto(
        id = this.id,
        fullName = this.name,
        emailAddress = this.email,
        status = if (this.isActive) "active" else "inactive"
    )
}

// Entity → Domain
fun UserEntity.toDomainModel(): User {
    return User(
        id = this.id,
        name = this.name,
        email = this.email,
        isActive = this.isActive
    )
}

// Domain → Entity
fun User.toEntity(): UserEntity {
    return UserEntity(
        id = this.id,
        name = this.name,
        email = this.email,
        isActive = this.isActive
    )
}
```

## Layer 3: Presentation Layer

### ViewModels

```kotlin
// presentation/user/UserViewModel.kt
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase,
    private val updateUserUseCase: UpdateUserUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading

            getUserUseCase(userId)
                .onSuccess { user ->
                    _uiState.value = UserUiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = UserUiState.Error(error.message ?: "Unknown error")
                }
        }
    }

    fun updateUser(user: User) {
        viewModelScope.launch {
            updateUserUseCase(user)
                .onSuccess {
                    loadUser(user.id)
                }
                .onFailure { error ->
                    _uiState.value = UserUiState.Error(error.message ?: "Update failed")
                }
        }
    }
}

sealed class UserUiState {
    object Loading : UserUiState()
    data class Success(val user: User) : UserUiState()
    data class Error(val message: String) : UserUiState()
}
```

### UI (Activity/Fragment/Compose)

```kotlin
// presentation/user/UserScreen.kt (Compose)
@Composable
fun UserScreen(
    userId: String,
    viewModel: UserViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(userId) {
        viewModel.loadUser(userId)
    }

    when (val state = uiState) {
        is UserUiState.Loading -> {
            LoadingScreen()
        }
        is UserUiState.Success -> {
            UserContent(
                user = state.user,
                onUpdateClick = { viewModel.updateUser(it) }
            )
        }
        is UserUiState.Error -> {
            ErrorScreen(
                message = state.message,
                onRetry = { viewModel.loadUser(userId) }
            )
        }
    }
}
```

## Module Structure (Multi-Module Project)

```
app/                            # Main app module
├── di/                        # Dependency injection setup
└── MainActivity.kt

domain/                         # Pure Kotlin module
├── model/
│   ├── User.kt
│   └── Order.kt
├── repository/
│   ├── UserRepository.kt      # Interface
│   └── OrderRepository.kt     # Interface
└── usecase/
    ├── GetUserUseCase.kt
    ├── LoginUseCase.kt
    └── CreateOrderUseCase.kt

data/                          # Data layer module
├── repository/
│   ├── UserRepositoryImpl.kt  # Implementation
│   └── OrderRepositoryImpl.kt
├── source/
│   ├── remote/
│   │   ├── UserApiService.kt
│   │   └── dto/UserDto.kt
│   └── local/
│       ├── UserDao.kt
│       └── entity/UserEntity.kt
└── mapper/
    └── UserMapper.kt

presentation/                   # Presentation module
├── user/
│   ├── UserViewModel.kt
│   └── UserScreen.kt
└── order/
    ├── OrderViewModel.kt
    └── OrderScreen.kt
```

## Dependency Injection with Hilt

```kotlin
// domain/di/DomainModule.kt
@Module
@InstallIn(SingletonComponent::class)
object DomainModule {

    @Provides
    fun provideGetUserUseCase(
        userRepository: UserRepository
    ): GetUserUseCase {
        return GetUserUseCase(userRepository)
    }

    @Provides
    fun provideLoginUseCase(
        userRepository: UserRepository,
        authRepository: AuthRepository,
        analytics: Analytics
    ): LoginUseCase {
        return LoginUseCase(userRepository, authRepository, analytics)
    }
}

// data/di/DataModule.kt
@Module
@InstallIn(SingletonComponent::class)
object DataModule {

    @Provides
    @Singleton
    fun provideUserRepository(
        userApi: UserApiService,
        userDao: UserDao
    ): UserRepository {
        return UserRepositoryImpl(userApi, userDao)
    }

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApiService {
        return retrofit.create(UserApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

## Use Cases

### When to Use Clean Architecture

- **Large, complex apps**: Apps with significant business logic
- **Long-term projects**: Projects expected to be maintained for years
- **Team development**: Large teams with parallel feature development
- **Testability critical**: Apps requiring comprehensive testing
- **Framework independence**: Apps that may migrate frameworks/platforms
- **Reusable business logic**: Logic shared across platforms (KMM)
- **Enterprise apps**: Corporate apps with complex business rules
- **Evolving requirements**: Apps with frequently changing requirements

### When to Consider Simpler Architecture

- **Small apps**: Single-feature or prototype apps
- **Short-term projects**: Hackathons, proof-of-concepts
- **Solo developers**: Very small teams with simple requirements
- **Simple CRUD apps**: Apps with minimal business logic
- **Learning projects**: Beginners learning Android (start simpler)

## Trade-offs

**Pros**:
- **Testability**: Each layer tested independently, pure Kotlin domain
- **Maintainability**: Clear separation of concerns, easy to modify
- **Scalability**: Easy to add features without affecting existing code
- **Framework independence**: Business logic not tied to Android
- **Reusability**: Domain layer can be shared (e.g., KMM)
- **Team collaboration**: Teams can work on layers independently
- **Flexibility**: Easy to swap implementations (e.g., change database)
- **Long-term sustainability**: Architecture scales with project growth

**Cons**:
- **Complexity**: More layers, interfaces, and classes
- **Boilerplate**: Significant setup code (mappers, modules, etc.)
- **Learning curve**: Requires understanding of architecture principles
- **Over-engineering**: Can be overkill for simple apps
- **Initial development time**: Slower to start compared to simpler architectures
- **Debugging complexity**: More layers to trace through
- **Mapper overhead**: Converting between DTO/Entity/Domain models
- **Build time**: Multi-module projects can increase build times

## Best Practices

### Domain Layer

- **Pure Kotlin only**: No Android framework dependencies
- **Define interfaces**: Repositories, data sources as interfaces
- **Single responsibility**: Each use case handles one operation
- **Use operator invoke()**: Makes use cases callable like functions
- **Business rules in entities**: Domain models contain validation logic
- **Return Result or sealed classes**: Proper error handling
- **Suspend functions**: Use coroutines for async operations
- **Flow for streams**: Observable data with Kotlin Flow

### Data Layer

- **Implement Domain interfaces**: Repository implementations
- **Separate data sources**: Network, database, cache
- **Use mappers**: Convert DTO ↔ Entity ↔ Domain
- **Error handling**: Convert data layer errors to domain errors
- **Caching strategy**: Implement proper caching (network + cache)
- **Offline support**: Handle offline scenarios gracefully
- **Use Room for local**: Type-safe database with Flow support
- **Use Retrofit for network**: Type-safe API calls

### Presentation Layer

- **ViewModels depend on Use Cases**: Not directly on repositories
- **One ViewModel per screen**: Keep ViewModels focused
- **UI State sealed classes**: Represent all possible UI states
- **Handle one-time events**: Use Channels or Event wrappers
- **Lifecycle awareness**: Use viewLifecycleOwner in fragments
- **Dependency injection**: Use Hilt for all dependencies
- **Keep UI dumb**: No business logic in Activities/Fragments/Composables

## Common Patterns

### Use Case with Parameters

```kotlin
data class LoginParams(
    val email: String,
    val password: String
)

class LoginUseCase(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(params: LoginParams): Result<User> {
        // Use case implementation
    }
}

// Usage
viewModel.launch {
    loginUseCase(LoginParams(email, password))
}
```

### Use Case with Flow

```kotlin
class ObserveUserUseCase(
    private val userRepository: UserRepository
) {
    operator fun invoke(userId: String): Flow<User> {
        return userRepository.observeUser(userId)
    }
}

// Usage
val user: StateFlow<User?> = observeUserUseCase(userId)
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
```

### Error Handling with Sealed Classes

```kotlin
sealed class DomainError {
    data class NetworkError(val message: String) : DomainError()
    data class ValidationError(val field: String, val message: String) : DomainError()
    object UnauthorizedError : DomainError()
    data class UnknownError(val throwable: Throwable) : DomainError()
}

sealed class DomainResult<out T> {
    data class Success<T>(val data: T) : DomainResult<T>()
    data class Error(val error: DomainError) : DomainResult<Nothing>()
}

// Data layer maps exceptions to DomainError
fun Exception.toDomainError(): DomainError {
    return when (this) {
        is HttpException -> {
            if (code == 401) DomainError.UnauthorizedError
            else DomainError.NetworkError(message())
        }
        is IOException -> DomainError.NetworkError(message ?: "Network error")
        else -> DomainError.UnknownError(this)
    }
}
```

## Related Concepts

- [[c-mvvm]]
- [[c-repository-pattern]]
- [[c-dependency-injection]]
- [[c-use-case-pattern]]
- [[c-multi-module-architecture]]
- [[c-domain-driven-design]]
- [[c-solid-principles]]

## References

- [Clean Architecture (Book by Robert C. Martin)](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)
- [Android Clean Architecture Guide](https://developer.android.com/topic/architecture)
- [Guide to App Architecture - Domain Layer](https://developer.android.com/topic/architecture/domain-layer)
- [Clean Architecture on Android (ProAndroidDev)](https://proandroiddev.com/clean-architecture-on-android-7e7f8f1b6f9e)
- [Clean Architecture with Kotlin](https://www.raywenderlich.com/3595916-clean-architecture-tutorial-for-android-getting-started)
