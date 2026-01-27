---
id: kotlin-kmp-007
title: Clean Architecture in KMP / Clean Architecture в KMP
aliases:
- KMP Architecture
- Multiplatform Clean Architecture
- KMP Layers
topic: kotlin
subtopics:
- kmp
- multiplatform
- architecture
- clean-architecture
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- kmp
- multiplatform
- architecture
- clean-architecture
- difficulty/hard
anki_cards:
- slug: kotlin-kmp-007-0-en
  language: en
  anki_id: 1769344147566
  synced_at: '2026-01-25T16:29:07.616816'
- slug: kotlin-kmp-007-0-ru
  language: ru
  anki_id: 1769344147615
  synced_at: '2026-01-25T16:29:07.618798'
---
# Question (EN)
> How do you implement Clean Architecture in Kotlin Multiplatform projects?

# Vopros (RU)
> Как реализовать Clean Architecture в проектах Kotlin Multiplatform?

## Answer (EN)

Clean Architecture in KMP maximizes code sharing while maintaining platform flexibility. The key is proper layer separation with dependency inversion.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Platform Layer (UI)                         │
│    Android (Compose)  │  iOS (SwiftUI/Compose)  │  Desktop      │
├─────────────────────────────────────────────────────────────────┤
│                   Presentation Layer (shared)                    │
│              ViewModels, State Management, Mappers              │
├─────────────────────────────────────────────────────────────────┤
│                     Domain Layer (shared)                        │
│         Use Cases, Entities, Repository Interfaces              │
├─────────────────────────────────────────────────────────────────┤
│                      Data Layer (shared)                         │
│     Repository Impl, Data Sources, DTOs, Mappers                │
├─────────────────────────────────────────────────────────────────┤
│                 Platform Data Sources                            │
│         expect/actual for platform-specific data access          │
└─────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
shared/
  src/
    commonMain/
      kotlin/
        com/example/app/
          domain/
            model/
              User.kt           # Domain entities
              Product.kt
            repository/
              UserRepository.kt # Interfaces only
              ProductRepository.kt
            usecase/
              GetUserUseCase.kt
              UpdateProfileUseCase.kt

          data/
            repository/
              UserRepositoryImpl.kt
              ProductRepositoryImpl.kt
            source/
              remote/
                UserRemoteDataSource.kt
                api/
                  UserApi.kt
              local/
                UserLocalDataSource.kt
            mapper/
              UserMapper.kt
            dto/
              UserDto.kt

          presentation/
            user/
              UserViewModel.kt
              UserUiState.kt
            product/
              ProductListViewModel.kt
              ProductUiState.kt

          di/
            CommonModule.kt     # DI configuration

          platform/
            Platform.kt         # expect declarations

    androidMain/
      kotlin/
        com/example/app/
          platform/
            Platform.android.kt  # actual implementations
          di/
            AndroidModule.kt

    iosMain/
      kotlin/
        com/example/app/
          platform/
            Platform.ios.kt      # actual implementations
          di/
            IosModule.kt
```

### Domain Layer (100% Shared)

```kotlin
// domain/model/User.kt - Pure domain entity
data class User(
    val id: UserId,
    val email: Email,
    val profile: UserProfile,
    val createdAt: Instant
)

@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String) {
    init {
        require(value.contains("@")) { "Invalid email format" }
    }
}

data class UserProfile(
    val firstName: String,
    val lastName: String,
    val avatarUrl: String?
) {
    val fullName: String get() = "$firstName $lastName"
}

// domain/repository/UserRepository.kt - Interface only
interface UserRepository {
    fun observeUser(id: UserId): Flow<User?>
    suspend fun getUser(id: UserId): User?
    suspend fun updateProfile(id: UserId, profile: UserProfile): User
    suspend fun deleteUser(id: UserId)
}

// domain/usecase/GetUserUseCase.kt - Business logic
class GetUserUseCase(
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(userId: UserId): Result<User> {
        return runCatching {
            userRepository.getUser(userId)
                ?: throw UserNotFoundException(userId)
        }
    }
}

class UpdateProfileUseCase(
    private val userRepository: UserRepository,
    private val analyticsTracker: AnalyticsTracker
) {
    suspend operator fun invoke(
        userId: UserId,
        firstName: String,
        lastName: String,
        avatarUrl: String?
    ): Result<User> {
        return runCatching {
            val profile = UserProfile(firstName, lastName, avatarUrl)
            val updatedUser = userRepository.updateProfile(userId, profile)
            analyticsTracker.track(Event.ProfileUpdated(userId))
            updatedUser
        }
    }
}

// domain/exception/DomainExceptions.kt
sealed class DomainException : Exception() {
    data class UserNotFoundException(val userId: UserId) : DomainException()
    data class ValidationException(override val message: String) : DomainException()
    object NetworkException : DomainException()
}
```

### Data Layer (Mostly Shared)

```kotlin
// data/dto/UserDto.kt - Network/Database models
@Serializable
data class UserDto(
    val id: String,
    val email: String,
    @SerialName("first_name")
    val firstName: String,
    @SerialName("last_name")
    val lastName: String,
    @SerialName("avatar_url")
    val avatarUrl: String?,
    @SerialName("created_at")
    val createdAt: Long
)

// data/mapper/UserMapper.kt - DTO to Domain mapping
class UserMapper {
    fun toDomain(dto: UserDto): User {
        return User(
            id = UserId(dto.id),
            email = Email(dto.email),
            profile = UserProfile(
                firstName = dto.firstName,
                lastName = dto.lastName,
                avatarUrl = dto.avatarUrl
            ),
            createdAt = Instant.fromEpochMilliseconds(dto.createdAt)
        )
    }

    fun toDto(user: User): UserDto {
        return UserDto(
            id = user.id.value,
            email = user.email.value,
            firstName = user.profile.firstName,
            lastName = user.profile.lastName,
            avatarUrl = user.profile.avatarUrl,
            createdAt = user.createdAt.toEpochMilliseconds()
        )
    }
}

// data/source/remote/UserRemoteDataSource.kt
class UserRemoteDataSource(private val api: UserApi) {
    suspend fun getUser(id: String): UserDto {
        return api.getUser(id)
    }

    suspend fun updateProfile(id: String, request: UpdateProfileRequest): UserDto {
        return api.updateProfile(id, request)
    }
}

// data/source/local/UserLocalDataSource.kt
class UserLocalDataSource(private val database: AppDatabase) {
    private val queries = database.userQueries

    fun observeUser(id: String): Flow<UserEntity?> {
        return queries.selectById(id)
            .asFlow()
            .mapToOneOrNull(Dispatchers.IO)
    }

    suspend fun insertUser(user: UserEntity) {
        withContext(Dispatchers.IO) {
            queries.insert(user)
        }
    }

    suspend fun deleteUser(id: String) {
        withContext(Dispatchers.IO) {
            queries.delete(id)
        }
    }
}

// data/repository/UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource,
    private val mapper: UserMapper
) : UserRepository {

    override fun observeUser(id: UserId): Flow<User?> {
        return localDataSource.observeUser(id.value)
            .map { entity -> entity?.let { mapper.toDomain(it.toDto()) } }
    }

    override suspend fun getUser(id: UserId): User? {
        return try {
            // Network first, then cache
            val dto = remoteDataSource.getUser(id.value)
            localDataSource.insertUser(dto.toEntity())
            mapper.toDomain(dto)
        } catch (e: Exception) {
            // Fallback to cache
            localDataSource.observeUser(id.value)
                .first()
                ?.let { mapper.toDomain(it.toDto()) }
        }
    }

    override suspend fun updateProfile(id: UserId, profile: UserProfile): User {
        val request = UpdateProfileRequest(
            firstName = profile.firstName,
            lastName = profile.lastName,
            avatarUrl = profile.avatarUrl
        )
        val dto = remoteDataSource.updateProfile(id.value, request)
        localDataSource.insertUser(dto.toEntity())
        return mapper.toDomain(dto)
    }

    override suspend fun deleteUser(id: UserId) {
        localDataSource.deleteUser(id.value)
    }
}
```

### Presentation Layer (Shared ViewModels)

```kotlin
// presentation/user/UserUiState.kt
data class UserUiState(
    val isLoading: Boolean = false,
    val user: UserUi? = null,
    val error: String? = null
)

data class UserUi(
    val id: String,
    val email: String,
    val fullName: String,
    val avatarUrl: String?
)

sealed class UserEvent {
    object Refresh : UserEvent()
    data class UpdateProfile(
        val firstName: String,
        val lastName: String
    ) : UserEvent()
}

sealed class UserEffect {
    data class ShowError(val message: String) : UserEffect()
    object NavigateBack : UserEffect()
}

// presentation/user/UserViewModel.kt
class UserViewModel(
    private val userId: UserId,
    private val getUserUseCase: GetUserUseCase,
    private val updateProfileUseCase: UpdateProfileUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserUiState(isLoading = true))
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    private val _effects = Channel<UserEffect>(Channel.BUFFERED)
    val effects: Flow<UserEffect> = _effects.receiveAsFlow()

    init {
        loadUser()
    }

    fun onEvent(event: UserEvent) {
        when (event) {
            is UserEvent.Refresh -> loadUser()
            is UserEvent.UpdateProfile -> updateProfile(event.firstName, event.lastName)
        }
    }

    private fun loadUser() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            getUserUseCase(userId)
                .onSuccess { user ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            user = user.toUi()
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = error.toUserMessage()
                        )
                    }
                }
        }
    }

    private fun updateProfile(firstName: String, lastName: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            updateProfileUseCase(userId, firstName, lastName, _uiState.value.user?.avatarUrl)
                .onSuccess { user ->
                    _uiState.update {
                        it.copy(isLoading = false, user = user.toUi())
                    }
                    _effects.send(UserEffect.NavigateBack)
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false) }
                    _effects.send(UserEffect.ShowError(error.toUserMessage()))
                }
        }
    }

    private fun User.toUi(): UserUi {
        return UserUi(
            id = id.value,
            email = email.value,
            fullName = profile.fullName,
            avatarUrl = profile.avatarUrl
        )
    }

    private fun Throwable.toUserMessage(): String {
        return when (this) {
            is DomainException.UserNotFoundException -> "User not found"
            is DomainException.NetworkException -> "Network error. Please try again."
            else -> "An unexpected error occurred"
        }
    }
}
```

### Dependency Injection (Koin Example)

```kotlin
// di/CommonModule.kt
val commonModule = module {
    // Domain
    factory { GetUserUseCase(get()) }
    factory { UpdateProfileUseCase(get(), get()) }

    // Data
    single { UserMapper() }
    single { UserRemoteDataSource(get()) }
    single { UserLocalDataSource(get()) }
    single<UserRepository> { UserRepositoryImpl(get(), get(), get()) }

    // Presentation
    viewModelOf(::UserViewModel)
}

// di/AndroidModule.kt (androidMain)
val androidModule = module {
    single { createHttpClient() }
    single { createDatabase(androidContext()) }
    single<AnalyticsTracker> { FirebaseAnalyticsTracker() }
}

// di/IosModule.kt (iosMain)
val iosModule = module {
    single { createHttpClient() }
    single { createDatabase() }
    single<AnalyticsTracker> { IosAnalyticsTracker() }
}
```

### Testing Strategy

```kotlin
// commonTest
class GetUserUseCaseTest {

    private val mockRepository = mockk<UserRepository>()
    private val useCase = GetUserUseCase(mockRepository)

    @Test
    fun `returns user when found`() = runTest {
        val userId = UserId("123")
        val expectedUser = createTestUser(userId)
        coEvery { mockRepository.getUser(userId) } returns expectedUser

        val result = useCase(userId)

        assertTrue(result.isSuccess)
        assertEquals(expectedUser, result.getOrNull())
    }

    @Test
    fun `returns failure when user not found`() = runTest {
        val userId = UserId("123")
        coEvery { mockRepository.getUser(userId) } returns null

        val result = useCase(userId)

        assertTrue(result.isFailure)
        assertTrue(result.exceptionOrNull() is DomainException.UserNotFoundException)
    }
}

class UserViewModelTest {

    @Test
    fun `loads user on init`() = runTest {
        val userId = UserId("123")
        val mockGetUserUseCase = mockk<GetUserUseCase>()
        coEvery { mockGetUserUseCase(userId) } returns Result.success(createTestUser(userId))

        val viewModel = UserViewModel(userId, mockGetUserUseCase, mockk())
        advanceUntilIdle()

        assertFalse(viewModel.uiState.value.isLoading)
        assertNotNull(viewModel.uiState.value.user)
    }
}
```

### Benefits of This Architecture

1. **Maximum code sharing** (70-95%)
2. **Testable business logic** - domain layer has no platform dependencies
3. **Flexible UI layer** - can use native or Compose Multiplatform
4. **Clear separation of concerns**
5. **Easy to add new platforms**

---

## Otvet (RU)

Clean Architecture в KMP максимизирует переиспользование кода при сохранении гибкости для платформ. Ключ - правильное разделение слоёв с инверсией зависимостей.

### Обзор архитектуры

```
┌─────────────────────────────────────────────────────────────────┐
│                      Platform Layer (UI)                         │
│    Android (Compose)  │  iOS (SwiftUI/Compose)  │  Desktop      │
├─────────────────────────────────────────────────────────────────┤
│                   Presentation Layer (общий)                     │
│              ViewModels, Управление состоянием, Mappers         │
├─────────────────────────────────────────────────────────────────┤
│                     Domain Layer (общий)                         │
│         Use Cases, Сущности, Интерфейсы репозиториев            │
├─────────────────────────────────────────────────────────────────┤
│                      Data Layer (общий)                          │
│     Реализация репозиториев, Data Sources, DTO, Mappers         │
├─────────────────────────────────────────────────────────────────┤
│                 Platform Data Sources                            │
│         expect/actual для платформо-специфичного доступа        │
└─────────────────────────────────────────────────────────────────┘
```

### Domain слой (100% общий)

```kotlin
// domain/model/User.kt - Чистая доменная сущность
data class User(
    val id: UserId,
    val email: Email,
    val profile: UserProfile,
    val createdAt: Instant
)

@JvmInline
value class UserId(val value: String)

// domain/repository/UserRepository.kt - Только интерфейс
interface UserRepository {
    fun observeUser(id: UserId): Flow<User?>
    suspend fun getUser(id: UserId): User?
    suspend fun updateProfile(id: UserId, profile: UserProfile): User
    suspend fun deleteUser(id: UserId)
}

// domain/usecase/GetUserUseCase.kt - Бизнес-логика
class GetUserUseCase(
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(userId: UserId): Result<User> {
        return runCatching {
            userRepository.getUser(userId)
                ?: throw UserNotFoundException(userId)
        }
    }
}
```

### Data слой (в основном общий)

```kotlin
// data/repository/UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource,
    private val mapper: UserMapper
) : UserRepository {

    override fun observeUser(id: UserId): Flow<User?> {
        return localDataSource.observeUser(id.value)
            .map { entity -> entity?.let { mapper.toDomain(it.toDto()) } }
    }

    override suspend fun getUser(id: UserId): User? {
        return try {
            // Сначала сеть, потом кэш
            val dto = remoteDataSource.getUser(id.value)
            localDataSource.insertUser(dto.toEntity())
            mapper.toDomain(dto)
        } catch (e: Exception) {
            // Fallback на кэш
            localDataSource.observeUser(id.value)
                .first()
                ?.let { mapper.toDomain(it.toDto()) }
        }
    }
}
```

### Presentation слой (общие ViewModels)

```kotlin
// presentation/user/UserViewModel.kt
class UserViewModel(
    private val userId: UserId,
    private val getUserUseCase: GetUserUseCase,
    private val updateProfileUseCase: UpdateProfileUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserUiState(isLoading = true))
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    private val _effects = Channel<UserEffect>(Channel.BUFFERED)
    val effects: Flow<UserEffect> = _effects.receiveAsFlow()

    init {
        loadUser()
    }

    fun onEvent(event: UserEvent) {
        when (event) {
            is UserEvent.Refresh -> loadUser()
            is UserEvent.UpdateProfile -> updateProfile(event.firstName, event.lastName)
        }
    }

    private fun loadUser() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            getUserUseCase(userId)
                .onSuccess { user ->
                    _uiState.update {
                        it.copy(isLoading = false, user = user.toUi())
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.toUserMessage())
                    }
                }
        }
    }
}
```

### Внедрение зависимостей (пример Koin)

```kotlin
// di/CommonModule.kt
val commonModule = module {
    // Domain
    factory { GetUserUseCase(get()) }
    factory { UpdateProfileUseCase(get(), get()) }

    // Data
    single { UserMapper() }
    single { UserRemoteDataSource(get()) }
    single { UserLocalDataSource(get()) }
    single<UserRepository> { UserRepositoryImpl(get(), get(), get()) }

    // Presentation
    viewModelOf(::UserViewModel)
}
```

### Преимущества этой архитектуры

1. **Максимальное переиспользование кода** (70-95%)
2. **Тестируемая бизнес-логика** - domain слой не имеет платформенных зависимостей
3. **Гибкий UI слой** - можно использовать нативный или Compose Multiplatform
4. **Чёткое разделение ответственности**
5. **Легко добавлять новые платформы**

---

## Follow-ups

- How do you handle navigation in shared ViewModels?
- What DI frameworks work best with KMP (Koin vs Kodein)?
- How do you share ViewModel lifecycle across platforms?
- When should you use MVI vs MVVM in KMP?

## Dopolnitelnye Voprosy (RU)

- Как обрабатывать навигацию в общих ViewModels?
- Какие DI фреймворки лучше работают с KMP (Koin vs Kodein)?
- Как разделить жизненный цикл ViewModel между платформами?
- Когда использовать MVI vs MVVM в KMP?

## References

- [Clean Architecture Book](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [KMP Sample Apps](https://github.com/JetBrains/compose-multiplatform)

## Ssylki (RU)

- [[c-kotlin]]
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## Related Questions

- [[q-kmp-shared-code-strategy--kmp--hard]]
- [[q-kmp-ios-interop--kmp--hard]]
