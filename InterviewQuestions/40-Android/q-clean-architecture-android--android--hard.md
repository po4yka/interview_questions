---\
id: android-047
title: Clean Architecture on Android / Clean Architecture в Android
aliases: [Clean Architecture on Android, Clean Architecture в Android]
topic: android
subtopics: [architecture-clean, architecture-modularization, di-hilt]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-clean-architecture, c-dependency-injection, q-android-enterprise-mdm-architecture--android--hard, q-kmm-architecture--android--hard, q-multi-module-best-practices--android--hard]
sources: []
created: 2025-10-11
updated: 2025-11-11
tags: [android/architecture-clean, android/architecture-modularization, android/di-hilt, difficulty/hard]

---\
# Вопрос (RU)
> Как реализовать Clean Architecture в Android?

# Question (EN)
> How to implement Clean Architecture on Android?

---

## Ответ (RU)

## Краткая Версия
Строго разделите слои (`presentation`, `domain`, `data`), направьте зависимости внутрь (только к `domain`), держите бизнес-логику в чистом Kotlin без Android SDK и фреймворков, используйте интерфейсы репозиториев как порты, реализуйте их во внешних модулях, и связывайте всё через DI (например, `Hilt`).

## Подробная Версия
#### Ключевые Принципы

**Правило зависимостей**: код зависит от внутренних слоев (UI → domain ← data). Domain определяет интерфейсы (порты), data реализует адаптеры.

**Разделение ответственности**: domain слой на чистом Kotlin без Android SDK. Фреймворки (Android, `Retrofit`, `Room`, `Hilt`) — на периферии.

**Тестируемость**: бизнес-логика полностью независима от платформы.

#### Требования

- Функциональные:
  - Отделить бизнес-логику от инфраструктуры и UI.
  - Обеспечить возможность подмены источников данных (API, БД, кеш).
  - Облегчить повторное использование `domain` между модулями/проектами.
- Нефункциональные:
  - Высокая тестируемость (`domain` тестируется без Android).
  - Масштабируемость структуры проекта при росте фичей.
  - Минимальная связанность между фичами и слоями.

#### Архитектура

**Структура Слоев**

**Domain (core-domain)**
- Entities: модели бизнес-логики
- Use Cases: операции (один case = одна операция)
- Repository интерфейсы (порты)
- Чистый Kotlin, без Android зависимостей и DI-фреймворков

**Data (core-data)**
- Repository реализации (адаптеры)
- Источники данных (API, DB, Cache)
- Mappers: DTO/DB → Domain
- Зависит от domain (реализует интерфейсы)

**Presentation (app/feature-*)**
- `ViewModel`: управляет UI состоянием
- UI: Compose/Views
- Mappers: Domain → UI models
- Зависит только от domain (use cases)

#### Минимальная Структура Модулей

```text
core-domain/     # entities, use cases, repository ports (без Android/Hilt)
core-data/       # repository impls, API/DB sources, мапперы DTO/DB→domain
app/             # DI setup (Hilt), navigation, composition root
feature-user/    # UserScreen, UserViewModel, мапперы domain→UI
```

#### Use Case Паттерн

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
// Примечание: Result<User> здесь — прагматичный выбор; в строгом варианте
// можно использовать собственный доменный тип результата.
```

#### Repository Реализация

```kotlin
// ✅ core-data: адаптер репозитория
class UserRepositoryImpl(
  private val api: UserApi,
  private val dao: UserDao
) : UserRepository {
  override suspend fun getUser(id: String): Result<User> =
    runCatching {
      val cached = dao.getUser(id)
      if (cached != null) {
        cached.toDomain()
      } else {
        val dto = api.fetchUser(id)
        dao.insert(dto.toEntity())
        dto.toDomain()
      }
    }
}
```

#### `ViewModel` Интеграция

```kotlin
// ✅ feature-user: ViewModel зависит от use cases
@HiltViewModel
class UserViewModel @Inject constructor(
  private val getUser: GetUserUseCase
) : ViewModel() {
  val state = MutableStateFlow<UiState>(UiState.Loading)

  fun loadUser(id: String) = viewModelScope.launch {
    getUser(id).fold(
      onSuccess = { user -> state.value = UiState.Success(user.toUiModel()) },
      onFailure = { error -> state.value = UiState.Error(error.message) }
    )
  }
}
```

#### Dependency Injection

```kotlin
// ✅ app (composition root): модуль связывает порты с адаптерами
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
  @Binds
  abstract fun bindUserRepository(
    impl: UserRepositoryImpl
  ): UserRepository
}
```

#### Граница Маппинга

```kotlin
// ❌ Не передавать DTO/Entity во внутренние слои
data class UserDto(val name: String, val email: String)
viewModel.loadUser(userDto) // WRONG

// ✅ Маппинг на границе между слоями/модулями
fun UserDto.toDomain() = User(name, email)
fun User.toUiModel() = UserUiModel(name, email)
```

#### Тестирование

**Domain**: быстрые unit-тесты с fake repositories (без Android и DI-фреймворков)

**Data**: contract-тесты против портов; instrumented-тесты для `Room`

**Presentation**: `ViewModel` тесты с `TestDispatcher` и fake use cases

## Answer (EN)

## Short Version
Strictly separate layers (`presentation`, `domain`, `data`), direct dependencies inward (only towards `domain`), keep business logic in pure Kotlin without Android SDK/frameworks, expose repository interfaces as ports, implement them in outer modules, and wire everything via DI (e.g., `Hilt`).

## Detailed Version
#### Core Principles

**Dependency Rule**: code depends on inner layers (UI → domain ← data). Domain defines interfaces (ports), data implements adapters.

**Separation of Concerns**: domain layer in pure Kotlin without Android SDK. Frameworks (Android, `Retrofit`, `Room`, `Hilt`) live at the edges.

**Testability**: business logic completely platform-independent.

#### Requirements

- Functional:
  - Separate business logic from infrastructure and UI.
  - Allow swapping data sources (API, DB, cache).
  - Enable reusing `domain` across modules/projects.
- Non-functional:
  - High testability (`domain` testable without Android).
  - Scalable project structure as features grow.
  - Low coupling between features and layers.

#### Architecture

**Layer Structure**

**Domain (core-domain)**
- Entities: business logic models
- Use Cases: operations (one case = one operation)
- Repository interfaces (ports)
- Pure Kotlin, no Android or DI framework dependencies

**Data (core-data)**
- Repository implementations (adapters)
- Data sources (API, DB, Cache)
- Mappers: DTO/DB → Domain
- Depends on domain (implements interfaces)

**Presentation (app/feature-*)**
- `ViewModel`: manages UI state
- UI: Compose/Views
- Mappers: Domain → UI models
- Depends only on domain (use cases)

#### Minimal Module Layout

```text
core-domain/     # entities, use cases, repository ports (no Android/Hilt)
core-data/       # repository impls, API/DB sources, DTO/DB→domain mappers
app/             # DI setup (Hilt), navigation, composition root
feature-user/    # UserScreen, UserViewModel, domain→UI mappers
```

#### Use Case Pattern

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
// Note: using Result<User> is a pragmatic choice; in strict Clean Architecture
// you may prefer a domain-specific result type.
```

#### Repository Implementation

```kotlin
// ✅ core-data: repository adapter
class UserRepositoryImpl(
  private val api: UserApi,
  private val dao: UserDao
) : UserRepository {
  override suspend fun getUser(id: String): Result<User> =
    runCatching {
      val cached = dao.getUser(id)
      if (cached != null) {
        cached.toDomain()
      } else {
        val dto = api.fetchUser(id)
        dao.insert(dto.toEntity())
        dto.toDomain()
      }
    }
}
```

#### `ViewModel` Integration

```kotlin
// ✅ feature-user: ViewModel depends on use cases
@HiltViewModel
class UserViewModel @Inject constructor(
  private val getUser: GetUserUseCase
) : ViewModel() {
  val state = MutableStateFlow<UiState>(UiState.Loading)

  fun loadUser(id: String) = viewModelScope.launch {
    getUser(id).fold(
      onSuccess = { user -> state.value = UiState.Success(user.toUiModel()) },
      onFailure = { error -> state.value = UiState.Error(error.message) }
    )
  }
}
```

#### Dependency Injection

```kotlin
// ✅ app (composition root): module binds ports to adapters
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
  @Binds
  abstract fun bindUserRepository(
    impl: UserRepositoryImpl
  ): UserRepository
}
```

#### Mapping Boundary

```kotlin
// ❌ Don't pass DTO/Entity into inner layers
data class UserDto(val name: String, val email: String)
viewModel.loadUser(userDto) // WRONG

// ✅ Map at the boundary between layers/modules
fun UserDto.toDomain() = User(name, email)
fun User.toUiModel() = UserUiModel(name, email)
```

#### Testing

**Domain**: fast unit tests with fake repositories (no Android or DI frameworks)

**Data**: contract tests against ports; instrumented tests for `Room`

**Presentation**: `ViewModel` tests with `TestDispatcher` and fake use cases

## Дополнительные Вопросы (RU)

- Как разделять фичи на модули без чрезмерной фрагментации?
- Где размещать навигационную логику в контексте Clean Architecture?
- Как обрабатывать доменные события между границами фич?
- Стоит ли инжектировать use cases напрямую или через фасад?
- Как обрабатывать платформенно-специфичные ошибки в domain-слое?

## Follow-ups

- How to split features into modules without over-fragmentation?
- Where to place navigation logic in Clean Architecture?
- How to manage domain events across feature boundaries?
- Should use cases be injected directly or through a facade?
- How to handle platform-specific errors in domain layer?

## Ссылки (RU)

- [[c-clean-architecture]]
- [[c-dependency-injection]]
- [Architecture](https://developer.android.com/topic/architecture)
- https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

## References

- [[c-clean-architecture]]
- [[c-dependency-injection]]
- [Architecture](https://developer.android.com/topic/architecture)
- https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

## Related Questions

### Prerequisites (Easier)
- [[q-architecture-components-libraries--android--easy]]

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-modularization--android--medium]]
