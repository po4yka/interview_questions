---
id: android-047
title: Clean Architecture on Android / Clean Architecture в Android
aliases: [Clean Architecture on Android, Clean Architecture в Android]
topic: android
subtopics:
  - architecture-clean
  - architecture-modularization
  - di-hilt
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-clean-architecture
  - c-dependency-injection
sources: []
created: 2025-10-11
updated: 2025-10-29
tags: [android/architecture-clean, android/architecture-modularization, android/di-hilt, difficulty/hard]
date created: Thursday, October 30th 2025, 11:18:04 am
date modified: Sunday, November 2nd 2025, 1:30:35 pm
---

# Вопрос (RU)
> Как реализовать Clean Architecture в Android?

# Question (EN)
> How to implement Clean Architecture on Android?

---

## Ответ (RU)

### Ключевые Принципы

**Правило зависимостей**: код зависит от внутренних слоев (UI → domain ← data). Domain определяет интерфейсы (порты), data реализует адаптеры.

**Разделение ответственности**: domain слой на чистом Kotlin без Android SDK. Фреймворки (Android, Retrofit, Room) на периферии.

**Тестируемость**: бизнес-логика полностью независима от платформы.

### Структура Слоев

**Domain (core-domain)**
- Entities: модели бизнес-логики
- Use Cases: операции (один case = одна операция)
- Repository интерфейсы (порты)
- Чистый Kotlin, без Android зависимостей

**Data (core-data)**
- Repository реализации (адаптеры)
- Источники данных (API, DB, Cache)
- Mappers: DTO/DB → Domain
- Зависит от domain (реализует интерфейсы)

**Presentation (app/feature-*)**
- ViewModel: управляет UI состоянием
- UI: Compose/Views
- Mappers: Domain → UI models
- Зависит только от domain (use cases)

### Минимальная Структура Модулей

```
core-domain/     # entities, use cases, repository ports
core-data/       # repository impls, API/DB sources
app/             # DI setup, navigation
feature-user/    # UserScreen, UserViewModel
```

### Use Case Паттерн

```kotlin
// ✅ core-domain: порт репозитория
interface UserRepository {
  suspend fun getUser(id: String): Result<User>
}

// ✅ core-domain: use case инкапсулирует бизнес-операцию
class GetUserUseCase(private val repo: UserRepository) {
  suspend operator fun invoke(id: String): Result<User> =
    repo.getUser(id)
}
```

### Repository Реализация

```kotlin
// ✅ core-data: адаптер репозитория
class UserRepositoryImpl(
  private val api: UserApi,
  private val dao: UserDao
) : UserRepository {
  override suspend fun getUser(id: String): Result<User> =
    runCatching {
      dao.getUser(id)?.toDomain()
        ?: api.fetchUser(id).also { dao.insert(it.toEntity()) }.toDomain()
    }
}
```

### ViewModel Интеграция

```kotlin
// ✅ feature-user: ViewModel зависит от use cases
@HiltViewModel
class UserViewModel @Inject constructor(
  private val getUser: GetUserUseCase
) : ViewModel() {
  val state = MutableStateFlow<UiState>(UiState.Loading)

  fun loadUser(id: String) = viewModelScope.launch {
    getUser(id).fold(
      onSuccess = { state.value = UiState.Success(it.toUiModel()) },
      onFailure = { state.value = UiState.Error(it.message) }
    )
  }
}
```

### Dependency Injection

```kotlin
// ✅ core-data: модуль связывает порты с адаптерами
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
  @Binds
  abstract fun bindUserRepository(
    impl: UserRepositoryImpl
  ): UserRepository
}
```

### Граница Маппинга

```kotlin
// ❌ Не передавать DTO/Entity в domain
data class UserDto(val name: String, val email: String)
viewModel.loadUser(userDto) // WRONG

// ✅ Маппинг на границе модуля
fun UserDto.toDomain() = User(name, email)
fun User.toUiModel() = UserUiModel(name, email)
```

### Тестирование

**Domain**: быстрые unit-тесты с fake repositories (без Android)

**Data**: contract-тесты против портов; instrumented-тесты для Room

**Presentation**: ViewModel тесты с TestDispatcher и fake use cases

## Answer (EN)

### Core Principles

**Dependency Rule**: code depends on inner layers (UI → domain ← data). Domain defines interfaces (ports), data implements adapters.

**Separation of Concerns**: domain layer in pure Kotlin without Android SDK. Frameworks (Android, Retrofit, Room) at the edges.

**Testability**: business logic completely platform-independent.

### Layer Structure

**Domain (core-domain)**
- Entities: business logic models
- Use Cases: operations (one case = one operation)
- Repository interfaces (ports)
- Pure Kotlin, no Android dependencies

**Data (core-data)**
- Repository implementations (adapters)
- Data sources (API, DB, Cache)
- Mappers: DTO/DB → Domain
- Depends on domain (implements interfaces)

**Presentation (app/feature-*)**
- ViewModel: manages UI state
- UI: Compose/Views
- Mappers: Domain → UI models
- Depends only on domain (use cases)

### Minimal Module Layout

```
core-domain/     # entities, use cases, repository ports
core-data/       # repository impls, API/DB sources
app/             # DI setup, navigation
feature-user/    # UserScreen, UserViewModel
```

### Use Case Pattern

```kotlin
// ✅ core-domain: repository port
interface UserRepository {
  suspend fun getUser(id: String): Result<User>
}

// ✅ core-domain: use case encapsulates business operation
class GetUserUseCase(private val repo: UserRepository) {
  suspend operator fun invoke(id: String): Result<User> =
    repo.getUser(id)
}
```

### Repository Implementation

```kotlin
// ✅ core-data: repository adapter
class UserRepositoryImpl(
  private val api: UserApi,
  private val dao: UserDao
) : UserRepository {
  override suspend fun getUser(id: String): Result<User> =
    runCatching {
      dao.getUser(id)?.toDomain()
        ?: api.fetchUser(id).also { dao.insert(it.toEntity()) }.toDomain()
    }
}
```

### ViewModel Integration

```kotlin
// ✅ feature-user: ViewModel depends on use cases
@HiltViewModel
class UserViewModel @Inject constructor(
  private val getUser: GetUserUseCase
) : ViewModel() {
  val state = MutableStateFlow<UiState>(UiState.Loading)

  fun loadUser(id: String) = viewModelScope.launch {
    getUser(id).fold(
      onSuccess = { state.value = UiState.Success(it.toUiModel()) },
      onFailure = { state.value = UiState.Error(it.message) }
    )
  }
}
```

### Dependency Injection

```kotlin
// ✅ core-data: module binds ports to adapters
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
  @Binds
  abstract fun bindUserRepository(
    impl: UserRepositoryImpl
  ): UserRepository
}
```

### Mapping Boundary

```kotlin
// ❌ Don't pass DTO/Entity to domain
data class UserDto(val name: String, val email: String)
viewModel.loadUser(userDto) // WRONG

// ✅ Map at module boundary
fun UserDto.toDomain() = User(name, email)
fun User.toUiModel() = UserUiModel(name, email)
```

### Testing

**Domain**: fast unit tests with fake repositories (no Android)

**Data**: contract tests against ports; instrumented tests for Room

**Presentation**: ViewModel tests with TestDispatcher and fake use cases

## Follow-ups

- How to split features into modules without over-fragmentation?
- Where to place navigation logic in Clean Architecture?
- How to manage domain events across feature boundaries?
- Should use cases be injected directly or through a facade?
- How to handle platform-specific errors in domain layer?

## References

- [[c-clean-architecture]]
- [[c-dependency-injection]]
- https://developer.android.com/topic/architecture
- https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

## Related Questions

### Prerequisites (Easier)
- [[q-architecture-components-libraries--android--easy]]

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-modularization--android--medium]]
