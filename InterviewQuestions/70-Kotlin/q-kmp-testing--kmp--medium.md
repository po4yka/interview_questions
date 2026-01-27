---
id: kotlin-kmp-010
title: Testing Shared Code in KMP / Тестирование общего кода в KMP
aliases:
- KMP Testing
- Multiplatform Testing
- Cross-Platform Tests
topic: kotlin
subtopics:
- kmp
- multiplatform
- testing
question_kind: theory
difficulty: medium
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
- testing
- difficulty/medium
anki_cards:
- slug: kotlin-kmp-010-0-en
  language: en
  anki_id: 1769344154640
  synced_at: '2026-01-25T16:29:14.693150'
- slug: kotlin-kmp-010-0-ru
  language: ru
  anki_id: 1769344154691
  synced_at: '2026-01-25T16:29:14.696707'
---
# Question (EN)
> How do you test shared code across platforms in Kotlin Multiplatform?

# Vopros (RU)
> Как тестировать общий код на разных платформах в Kotlin Multiplatform?

## Answer (EN)

KMP supports writing tests in `commonTest` that run on all target platforms, plus platform-specific tests when needed.

### Project Test Structure

```
shared/
  src/
    commonMain/
      kotlin/
    commonTest/           # Shared tests - run on ALL platforms
      kotlin/
        com/example/
          domain/
            UserUseCaseTest.kt
          data/
            UserRepositoryTest.kt

    androidUnitTest/      # Android-specific unit tests
      kotlin/
    androidInstrumentedTest/  # Android instrumented tests
      kotlin/

    iosTest/              # iOS-specific tests
      kotlin/

    jvmTest/              # JVM-specific tests (Desktop)
      kotlin/
```

### Dependencies Setup

```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
            implementation(libs.turbine)  // Flow testing
            implementation(libs.mockk.common)
        }

        androidUnitTest.dependencies {
            implementation(libs.kotlin.test.junit)
            implementation(libs.mockk.android)
            implementation(libs.robolectric)
        }

        iosTest.dependencies {
            // iOS-specific test dependencies
        }
    }
}

// libs.versions.toml
[versions]
turbine = "1.0.0"
mockk = "1.13.8"

[libraries]
kotlin-test = { module = "org.jetbrains.kotlin:kotlin-test" }
kotlin-test-junit = { module = "org.jetbrains.kotlin:kotlin-test-junit" }
kotlinx-coroutines-test = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-test", version.ref = "coroutines" }
turbine = { module = "app.cash.turbine:turbine", version.ref = "turbine" }
mockk-common = { module = "io.mockk:mockk-common", version.ref = "mockk" }
mockk-android = { module = "io.mockk:mockk-android", version.ref = "mockk" }
```

### Basic Unit Tests

```kotlin
// commonTest/kotlin/com/example/domain/UserUseCaseTest.kt
class GetUserUseCaseTest {

    private lateinit var repository: FakeUserRepository
    private lateinit var useCase: GetUserUseCase

    @BeforeTest
    fun setup() {
        repository = FakeUserRepository()
        useCase = GetUserUseCase(repository)
    }

    @Test
    fun `returns user when found`() = runTest {
        // Given
        val userId = UserId("123")
        val expectedUser = User(
            id = userId,
            email = Email("test@example.com"),
            profile = UserProfile("John", "Doe", null),
            createdAt = Clock.System.now()
        )
        repository.addUser(expectedUser)

        // When
        val result = useCase(userId)

        // Then
        assertTrue(result.isSuccess)
        assertEquals(expectedUser, result.getOrNull())
    }

    @Test
    fun `returns failure when user not found`() = runTest {
        // Given
        val userId = UserId("nonexistent")

        // When
        val result = useCase(userId)

        // Then
        assertTrue(result.isFailure)
        assertIs<DomainException.UserNotFoundException>(result.exceptionOrNull())
    }
}

// Fake implementation for testing
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<UserId, User>()

    fun addUser(user: User) {
        users[user.id] = user
    }

    override suspend fun getUser(id: UserId): User? = users[id]

    override fun observeUser(id: UserId): Flow<User?> = flow {
        emit(users[id])
    }

    override suspend fun updateProfile(id: UserId, profile: UserProfile): User {
        val existing = users[id] ?: throw DomainException.UserNotFoundException(id)
        val updated = existing.copy(profile = profile)
        users[id] = updated
        return updated
    }

    override suspend fun deleteUser(id: UserId) {
        users.remove(id)
    }
}
```

### Testing Coroutines

```kotlin
// commonTest
class CoroutineUseCaseTest {

    @Test
    fun `handles concurrent operations`() = runTest {
        val repository = FakeUserRepository()
        val useCase = GetUserUseCase(repository)

        // Add test users
        repeat(100) { index ->
            repository.addUser(createUser(UserId("user-$index")))
        }

        // Execute concurrent requests
        val results = (0 until 100).map { index ->
            async {
                useCase(UserId("user-$index"))
            }
        }.awaitAll()

        // Verify all succeeded
        assertTrue(results.all { it.isSuccess })
    }

    @Test
    fun `respects timeout`() = runTest {
        val slowRepository = object : UserRepository {
            override suspend fun getUser(id: UserId): User? {
                delay(10_000) // Very slow
                return null
            }
            // ... other methods
        }

        val useCase = GetUserWithTimeoutUseCase(slowRepository, timeout = 1000)

        val result = useCase(UserId("123"))

        assertTrue(result.isFailure)
        assertIs<TimeoutException>(result.exceptionOrNull())
    }
}
```

### Testing Flows with Turbine

```kotlin
// commonTest
class FlowUseCaseTest {

    @Test
    fun `emits user updates`() = runTest {
        val repository = FakeUserRepository()
        val useCase = ObserveUserUseCase(repository)
        val userId = UserId("123")

        repository.addUser(createUser(userId, name = "John"))

        useCase(userId).test {
            // Initial value
            val first = awaitItem()
            assertEquals("John", first?.profile?.firstName)

            // Update user
            repository.updateUser(userId, name = "Jane")

            // New value
            val second = awaitItem()
            assertEquals("Jane", second?.profile?.firstName)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `handles errors in flow`() = runTest {
        val failingRepository = object : UserRepository {
            override fun observeUser(id: UserId): Flow<User?> = flow {
                emit(createUser(id))
                throw IOException("Network error")
            }
            // ... other methods
        }

        val useCase = ObserveUserUseCase(failingRepository)

        useCase(UserId("123")).test {
            // First emission succeeds
            assertNotNull(awaitItem())

            // Then error
            val error = awaitError()
            assertIs<IOException>(error)
        }
    }
}
```

### Testing ViewModels

```kotlin
// commonTest
class UserViewModelTest {

    private lateinit var viewModel: UserViewModel
    private lateinit var fakeGetUserUseCase: FakeGetUserUseCase
    private lateinit var fakeUpdateProfileUseCase: FakeUpdateProfileUseCase

    @BeforeTest
    fun setup() {
        fakeGetUserUseCase = FakeGetUserUseCase()
        fakeUpdateProfileUseCase = FakeUpdateProfileUseCase()
    }

    @Test
    fun `initial state is loading`() = runTest {
        fakeGetUserUseCase.delay = 1000 // Slow response

        viewModel = UserViewModel(
            userId = UserId("123"),
            getUserUseCase = fakeGetUserUseCase,
            updateProfileUseCase = fakeUpdateProfileUseCase
        )

        assertTrue(viewModel.uiState.value.isLoading)
    }

    @Test
    fun `loads user successfully`() = runTest {
        val user = createUser(UserId("123"))
        fakeGetUserUseCase.result = Result.success(user)

        viewModel = UserViewModel(
            userId = UserId("123"),
            getUserUseCase = fakeGetUserUseCase,
            updateProfileUseCase = fakeUpdateProfileUseCase
        )

        advanceUntilIdle()

        assertFalse(viewModel.uiState.value.isLoading)
        assertNotNull(viewModel.uiState.value.user)
        assertEquals("123", viewModel.uiState.value.user?.id)
    }

    @Test
    fun `shows error on failure`() = runTest {
        fakeGetUserUseCase.result = Result.failure(DomainException.NetworkException)

        viewModel = UserViewModel(
            userId = UserId("123"),
            getUserUseCase = fakeGetUserUseCase,
            updateProfileUseCase = fakeUpdateProfileUseCase
        )

        advanceUntilIdle()

        assertFalse(viewModel.uiState.value.isLoading)
        assertNotNull(viewModel.uiState.value.error)
    }

    @Test
    fun `emits navigation effect after update`() = runTest {
        val user = createUser(UserId("123"))
        fakeGetUserUseCase.result = Result.success(user)
        fakeUpdateProfileUseCase.result = Result.success(user)

        viewModel = UserViewModel(
            userId = UserId("123"),
            getUserUseCase = fakeGetUserUseCase,
            updateProfileUseCase = fakeUpdateProfileUseCase
        )

        advanceUntilIdle()

        viewModel.effects.test {
            viewModel.onEvent(UserEvent.UpdateProfile("New", "Name"))
            advanceUntilIdle()

            val effect = awaitItem()
            assertIs<UserEffect.NavigateBack>(effect)
        }
    }
}

// Fake use cases
class FakeGetUserUseCase : GetUserUseCase(FakeUserRepository()) {
    var result: Result<User> = Result.failure(Exception("Not configured"))
    var delay: Long = 0

    override suspend fun invoke(userId: UserId): Result<User> {
        if (delay > 0) delay(delay)
        return result
    }
}
```

### Platform-Specific Tests

```kotlin
// androidUnitTest - Android-specific tests
class AndroidPlatformTest {

    @Test
    fun `creates android http client`() {
        val client = createPlatformHttpClient()
        assertNotNull(client)
        // Android-specific assertions
    }
}

// iosTest - iOS-specific tests
class IosPlatformTest {

    @Test
    fun `creates darwin http client`() {
        val client = createPlatformHttpClient()
        assertNotNull(client)
        // iOS-specific assertions
    }
}
```

### Integration Tests

```kotlin
// commonTest
class UserRepositoryIntegrationTest {

    private lateinit var database: AppDatabase
    private lateinit var repository: UserRepositoryImpl

    @BeforeTest
    fun setup() {
        // Use in-memory database for testing
        database = createTestDatabase()
        repository = UserRepositoryImpl(
            remoteDataSource = FakeRemoteDataSource(),
            localDataSource = UserLocalDataSource(database),
            mapper = UserMapper()
        )
    }

    @AfterTest
    fun teardown() {
        database.close()
    }

    @Test
    fun `caches user after fetch`() = runTest {
        val userId = UserId("123")

        // First fetch - from remote
        val user1 = repository.getUser(userId)
        assertNotNull(user1)

        // Second fetch - should be cached
        val user2 = repository.getUser(userId)
        assertEquals(user1, user2)

        // Verify cache was written
        val cached = database.userQueries.selectById(userId.value).executeAsOneOrNull()
        assertNotNull(cached)
    }
}

// Platform-specific test database creation
// commonMain
expect fun createTestDatabase(): AppDatabase

// androidUnitTest
actual fun createTestDatabase(): AppDatabase {
    return AppDatabase(
        JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also {
            AppDatabase.Schema.create(it)
        }
    )
}

// iosTest
actual fun createTestDatabase(): AppDatabase {
    return AppDatabase(
        NativeSqliteDriver(AppDatabase.Schema, null) // In-memory
    )
}
```

### Running Tests

```bash
# Run all tests on all platforms
./gradlew :shared:allTests

# Run common tests on JVM (fastest)
./gradlew :shared:jvmTest

# Run Android unit tests
./gradlew :shared:testDebugUnitTest

# Run iOS tests (requires simulator)
./gradlew :shared:iosSimulatorArm64Test

# Run with verbose output
./gradlew :shared:allTests --info
```

### Best Practices

1. **Write tests in commonTest** - They run on all platforms
2. **Use fakes over mocks** - Better for multiplatform
3. **Test business logic thoroughly** - Domain layer is 100% shared
4. **Use Turbine for Flow** - Simplifies Flow testing
5. **Use runTest for coroutines** - Proper test dispatcher
6. **Create test fixtures** - Reusable test data factories
7. **Run tests on CI for all platforms** - Catch platform-specific issues

---

## Otvet (RU)

KMP поддерживает написание тестов в `commonTest`, которые запускаются на всех целевых платформах, плюс платформо-специфичные тесты при необходимости.

### Структура тестов проекта

```
shared/
  src/
    commonMain/
      kotlin/
    commonTest/           # Общие тесты - запускаются на ВСЕХ платформах
      kotlin/
        com/example/
          domain/
            UserUseCaseTest.kt
          data/
            UserRepositoryTest.kt

    androidUnitTest/      # Android-специфичные unit тесты
      kotlin/
    androidInstrumentedTest/  # Android инструментальные тесты
      kotlin/

    iosTest/              # iOS-специфичные тесты
      kotlin/
```

### Настройка зависимостей

```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
            implementation(libs.turbine)  // Тестирование Flow
        }

        androidUnitTest.dependencies {
            implementation(libs.kotlin.test.junit)
            implementation(libs.mockk.android)
        }
    }
}
```

### Базовые Unit тесты

```kotlin
// commonTest/kotlin/com/example/domain/UserUseCaseTest.kt
class GetUserUseCaseTest {

    private lateinit var repository: FakeUserRepository
    private lateinit var useCase: GetUserUseCase

    @BeforeTest
    fun setup() {
        repository = FakeUserRepository()
        useCase = GetUserUseCase(repository)
    }

    @Test
    fun `возвращает пользователя когда найден`() = runTest {
        // Given
        val userId = UserId("123")
        val expectedUser = createUser(userId)
        repository.addUser(expectedUser)

        // When
        val result = useCase(userId)

        // Then
        assertTrue(result.isSuccess)
        assertEquals(expectedUser, result.getOrNull())
    }

    @Test
    fun `возвращает ошибку когда пользователь не найден`() = runTest {
        // Given
        val userId = UserId("nonexistent")

        // When
        val result = useCase(userId)

        // Then
        assertTrue(result.isFailure)
        assertIs<DomainException.UserNotFoundException>(result.exceptionOrNull())
    }
}
```

### Тестирование Flow с Turbine

```kotlin
// commonTest
class FlowUseCaseTest {

    @Test
    fun `эмитит обновления пользователя`() = runTest {
        val repository = FakeUserRepository()
        val useCase = ObserveUserUseCase(repository)
        val userId = UserId("123")

        repository.addUser(createUser(userId, name = "John"))

        useCase(userId).test {
            // Начальное значение
            val first = awaitItem()
            assertEquals("John", first?.profile?.firstName)

            // Обновляем пользователя
            repository.updateUser(userId, name = "Jane")

            // Новое значение
            val second = awaitItem()
            assertEquals("Jane", second?.profile?.firstName)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Тестирование ViewModels

```kotlin
// commonTest
class UserViewModelTest {

    @Test
    fun `начальное состояние - загрузка`() = runTest {
        fakeGetUserUseCase.delay = 1000 // Медленный ответ

        viewModel = UserViewModel(
            userId = UserId("123"),
            getUserUseCase = fakeGetUserUseCase,
            updateProfileUseCase = fakeUpdateProfileUseCase
        )

        assertTrue(viewModel.uiState.value.isLoading)
    }

    @Test
    fun `успешно загружает пользователя`() = runTest {
        val user = createUser(UserId("123"))
        fakeGetUserUseCase.result = Result.success(user)

        viewModel = UserViewModel(/* ... */)
        advanceUntilIdle()

        assertFalse(viewModel.uiState.value.isLoading)
        assertNotNull(viewModel.uiState.value.user)
    }
}
```

### Запуск тестов

```bash
# Запустить все тесты на всех платформах
./gradlew :shared:allTests

# Запустить общие тесты на JVM (быстрее всего)
./gradlew :shared:jvmTest

# Запустить Android unit тесты
./gradlew :shared:testDebugUnitTest

# Запустить iOS тесты (требует симулятор)
./gradlew :shared:iosSimulatorArm64Test
```

### Лучшие практики

1. **Пишите тесты в commonTest** - Они запускаются на всех платформах
2. **Используйте fakes вместо mocks** - Лучше для мультиплатформы
3. **Тестируйте бизнес-логику тщательно** - Domain слой 100% общий
4. **Используйте Turbine для Flow** - Упрощает тестирование Flow
5. **Используйте runTest для корутин** - Правильный тестовый диспатчер
6. **Создавайте тестовые фикстуры** - Переиспользуемые фабрики тестовых данных
7. **Запускайте тесты на CI для всех платформ** - Ловите платформо-специфичные проблемы

---

## Follow-ups

- How do you mock platform-specific dependencies in commonTest?
- What is the best approach for snapshot testing in KMP?
- How do you test Compose Multiplatform UI?
- How do you measure code coverage in KMP?

## Dopolnitelnye Voprosy (RU)

- Как мокать платформо-специфичные зависимости в commonTest?
- Какой лучший подход для snapshot тестирования в KMP?
- Как тестировать Compose Multiplatform UI?
- Как измерять покрытие кода в KMP?

## References

- [KMP Testing Documentation](https://kotlinlang.org/docs/multiplatform-run-tests.html)
- [Turbine - Flow Testing](https://github.com/cashapp/turbine)
- [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)

## Ssylki (RU)

- [[c-kotlin]]
- [Документация по тестированию KMP](https://kotlinlang.org/docs/multiplatform-run-tests.html)

## Related Questions

- [[q-kmp-gradle-setup--kmp--medium]]
- [[q-kmp-architecture--kmp--hard]]
