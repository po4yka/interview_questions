---
id: 20251006-015
title: "Clean Architecture in Android"
aliases: []

# Classification
topic: android
subtopics: [architecture, clean-architecture, layers, separation-of-concerns]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, architecture, clean-architecture, layers, separation-of-concerns, difficulty/hard]
---
# Question (EN)
> What is Clean Architecture in Android? How to implement it with layers?
# Вопрос (RU)
> Что такое Clean Architecture в Android? Как реализовать её со слоями?

---

## Answer (EN)

**Clean Architecture** separates app into independent layers with dependency rule: **outer layers depend on inner layers, never reverse.**

### Layers (from inner to outer)

**1. Domain** - Business logic (entities, use cases)
**2. Data** - Data sources (repositories, API, DB)
**3. Presentation** - UI (ViewModel, Compose)

```

     Presentation Layer            ← UI, ViewModel

       Data Layer                  ← Repository, API, DB

      Domain Layer                 ← Use Cases, Entities


Dependencies flow: Presentation → Data → Domain
```

### Domain Layer (Core business logic)

```kotlin
// domain/model/User.kt
data class User(
    val id: String,
    val name: String,
    val email: String
)

// domain/repository/UserRepository.kt (interface)
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    suspend fun updateUser(user: User): Result<Unit>
}

// domain/usecase/GetUserUseCase.kt
class GetUserUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(userId: String): Result<User> {
        return repository.getUser(userId)
    }
}
```

### Data Layer (Implementation)

```kotlin
// data/remote/dto/UserDto.kt
@Serializable
data class UserDto(
    val id: String,
    val name: String,
    val email: String
)

// data/remote/api/UserApi.kt
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto
}

// data/repository/UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val api: UserApi,
    private val mapper: UserMapper
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> {
        return try {
            val dto = api.getUser(id)
            val user = mapper.toDomain(dto)
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Presentation Layer

```kotlin
// presentation/UserViewModel.kt
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            getUserUseCase(userId)
                .onSuccess { user ->
                    _uiState.value = UiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = UiState.Error(error.message ?: "Unknown")
                }
        }
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val user: User) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Dependency Injection

```kotlin
// di/DataModule.kt
@Module
@InstallIn(SingletonComponent::class)
object DataModule {

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi {
        return retrofit.create(UserApi::class.java)
    }

    @Provides
    @Singleton
    fun provideUserRepository(
        api: UserApi,
        mapper: UserMapper
    ): UserRepository {
        return UserRepositoryImpl(api, mapper)
    }
}

// di/DomainModule.kt
@Module
@InstallIn(ViewModelComponent::class)
object DomainModule {

    @Provides
    fun provideGetUserUseCase(
        repository: UserRepository
    ): GetUserUseCase {
        return GetUserUseCase(repository)
    }
}
```

### Benefits

**1. Testability** - Mock dependencies easily
**2. Separation of concerns** - Clear responsibilities
**3. Independence** - Business logic independent of frameworks
**4. Maintainability** - Changes isolated to layers

**English Summary**: Clean Architecture: Domain (entities, use cases), Data (repository impl, API, DB), Presentation (ViewModel, UI). Dependency rule: outer depends on inner. Domain has interfaces, Data implements them. Use cases encapsulate business logic. Benefits: testability, separation of concerns, maintainability.

## Ответ (RU)

**Clean Architecture** разделяет приложение на независимые слои с правилом зависимости: **внешние слои зависят от внутренних, никогда наоборот.**

### Слои (от внутреннего к внешнему)

**1. Domain** - Бизнес-логика (entities, use cases)
**2. Data** - Источники данных (repositories, API, DB)
**3. Presentation** - UI (ViewModel, Compose)

```
Зависимости: Presentation → Data → Domain
```

### Слой Domain (Основная бизнес-логика)

```kotlin
// domain/model/User.kt
data class User(val id: String, val name: String, val email: String)

// domain/repository/UserRepository.kt (интерфейс)
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
}

// domain/usecase/GetUserUseCase.kt
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(userId: String): Result<User> {
        return repository.getUser(userId)
    }
}
```

### Слой Data (Реализация)

```kotlin
// data/repository/UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val api: UserApi
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> {
        return try {
            val dto = api.getUser(id)
            Result.success(mapper.toDomain(dto))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Преимущества

**1. Тестируемость** - Легко мокать зависимости
**2. Разделение обязанностей** - Четкие ответственности
**3. Независимость** - Бизнес-логика независима от фреймворков
**4. Поддерживаемость** - Изменения изолированы в слоях

**Краткое содержание**: Clean Architecture: Domain (entities, use cases), Data (реализация repository, API, DB), Presentation (ViewModel, UI). Правило зависимости: внешние зависят от внутренних. Domain имеет интерфейсы, Data реализует их. Use cases инкапсулируют бизнес-логику.

---

## References
- [Guide to app architecture](https://developer.android.com/topic/architecture)

## Related Questions

### Prerequisites (Easier)
- [[q-usecase-pattern-android--android--medium]] - Architecture
- [[q-repository-pattern--android--medium]] - Architecture
- [[q-repository-multiple-sources--android--medium]] - Architecture
- [[q-architecture-components-libraries--android--easy]] - Architecture Components overview
- [[q-viewmodel-pattern--android--easy]] - ViewModel pattern basics
### Related (Hard)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-modularization-patterns--android--hard]] - Architecture
- [[q-design-instagram-stories--android--hard]] - Media
### Related (Hard)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-modularization-patterns--android--hard]] - Architecture
- [[q-design-instagram-stories--android--hard]] - Media
### Related (Hard)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-modularization-patterns--android--hard]] - Architecture
- [[q-design-instagram-stories--android--hard]] - Media
### MVVM & ViewModel (Medium)
- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
- [[q-what-is-viewmodel--android--medium]] - What is ViewModel
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel purpose & internals
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - ViewModel state preservation
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - ViewModel vs onSavedInstanceState

### Patterns & Layers (Medium)
- [[q-repository-pattern--android--medium]] - Repository pattern
- [[q-repository-multiple-sources--android--medium]] - Repository with multiple sources
- [[q-usecase-pattern-android--android--medium]] - Use Case pattern
- [[q-mvi-one-time-events--android--medium]] - MVI one-time events
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing ViewModels with Turbine

### Advanced Architecture (Harder)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture
- [[q-kmm-architecture--multiplatform--hard]] - KMM architecture patterns