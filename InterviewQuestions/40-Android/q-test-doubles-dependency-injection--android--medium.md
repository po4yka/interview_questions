---
id: android-128
title: Test Doubles Dependency Injection / Тестовые двойники Dependency Injection
aliases:
- Test Doubles
- Тестовые двойники
topic: android
subtopics:
- di-hilt
- testing-unit
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-what-is-hilt--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/di-hilt
- android/testing-unit
- dependency-injection
- difficulty/medium
- hilt
- test-doubles

---

# Вопрос (RU)
> Тестовые двойники Dependency Injection

# Question (EN)
> Test Doubles Dependency Injection

---

## Ответ (RU)

Hilt предоставляет мощные возможности для тестирования с dependency injection, позволяя легко заменять production-зависимости на test doubles (mock-и, fake-и, stub-ы) как в инструментальных тестах, так и в локальных unit-тестах.

### Настройка тестов с Hilt

```kotlin
dependencies {
    // Интеграция Hilt для instrumented/androidTest
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.48")
    kaptAndroidTest("com.google.dagger:hilt-android-compiler:2.48")

    // Основные зависимости Hilt для приложения
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-android-compiler:2.48")
}
```

Убедитесь, что приложение/тесты настроены для Hilt: есть `@HiltAndroidApp` в production-приложении или используется `HiltTestApplication` в test-манифесте при необходимости.

```kotlin
@HiltAndroidTest
class RepositoryTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var repository: UserRepository

    @Before
    fun init() {
        hiltRule.inject()
    }

    @Test
    fun testRepository() {
        // Тестируем поведение с внедрённым репозиторием
    }
}
```

### `@TestInstallIn` для замены модулей

Позволяет глобально заменить production-модуль тестовым модулем в тестовом рантайме.

```kotlin
// Production-модуль
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
            .create(ApiService::class.java)
    }
}

// Test-модуль, заменяющий production-модуль
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [NetworkModule::class]
)
object FakeNetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return FakeApiService()
    }
}
```

### Создание fakes

Fake — это рабочая реализация интерфейса с упрощённым и детерминированным поведением для тестов.

```kotlin
// Интерфейс реального репозитория
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun updateUser(user: User)
    fun observeUser(id: String): Flow<User>
}

// Fake-реализация для тестов
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<String, User>()
    private val userFlows = mutableMapOf<String, MutableStateFlow<User?>>()

    var shouldReturnError = false
    var networkDelay = 0L

    override suspend fun getUser(id: String): User {
        delay(networkDelay)
        if (shouldReturnError) {
            throw IOException("Network error")
        }
        return users[id] ?: throw NoSuchElementException("User not found")
    }

    override suspend fun updateUser(user: User) {
        delay(networkDelay)
        if (shouldReturnError) {
            throw IOException("Network error")
        }
        users[user.id] = user
        userFlows[user.id]?.value = user
    }

    override fun observeUser(id: String): Flow<User> {
        return userFlows.getOrPut(id) {
            MutableStateFlow(users[id])
        }.filterNotNull()
    }

    // Хелперы для тестов
    fun addUser(user: User) {
        users[user.id] = user
        userFlows[user.id]?.value = user
    }

    fun clear() {
        users.clear()
        userFlows.clear()
    }
}
```

В локальных coroutine/`Flow`-тестах используйте тестовый диспетчер (`runTest`, `StandardTestDispatcher`), чтобы избежать нестабильного поведения.

### Использование fakes в тестах

```kotlin
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
object FakeRepositoryModule {
    @Provides
    @Singleton
    fun provideUserRepository(): UserRepository {
        return FakeUserRepository()
    }
}

@HiltAndroidTest
class UserScreenTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var repository: UserRepository

    private lateinit var fakeRepository: FakeUserRepository

    @Before
    fun setup() {
        hiltRule.inject()
        fakeRepository = repository as FakeUserRepository
        fakeRepository.clear()
    }

    @Test
    fun userScreen_displaysUser() {
        // Настраиваем данные в fake
        fakeRepository.addUser(User("1", "John Doe", "john@example.com"))

        composeTestRule.setContent {
            UserScreen(userId = "1")
        }

        composeTestRule.onNodeWithText("John Doe").assertExists()
        composeTestRule.onNodeWithText("john@example.com").assertExists()
    }

    @Test
    fun userScreen_handlesError() {
        fakeRepository.shouldReturnError = true

        composeTestRule.setContent {
            UserScreen(userId = "1")
        }

        composeTestRule.onNodeWithText("Error loading user").assertExists()
    }
}
```

### Несколько конфигураций тестовых double-ов

```kotlin
// Конфигурация 1: быстрый fake
class FastFakeRepository : UserRepository {
    override suspend fun getUser(id: String): User = User(id, "Fast", "fast@example.com")
    override suspend fun updateUser(user: User) { /* no-op */ }
    override fun observeUser(id: String): Flow<User> = flowOf(User(id, "Fast", "fast@example.com"))
}

// Конфигурация 2: медленный fake
class SlowFakeRepository : UserRepository {
    override suspend fun getUser(id: String): User {
        delay(2_000)
        return User(id, "Slow", "slow@example.com")
    }
    override suspend fun updateUser(user: User) { delay(2_000) }
    override fun observeUser(id: String): Flow<User> = flow {
        delay(2_000)
        emit(User(id, "Slow", "slow@example.com"))
    }
}

// Конфигурация 3: fake, всегда выбрасывающий ошибку
class ErrorFakeRepository : UserRepository {
    override suspend fun getUser(id: String): User = throw IOException("Test error")
    override suspend fun updateUser(user: User) { throw IOException("Test error") }
    override fun observeUser(id: String): Flow<User> = flow { throw IOException("Test error") }
}

// Использование @BindValue для конфигурации на уровне теста
@HiltAndroidTest
class ConfigurableTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    // `@BindValue` переопределяет биндинг UserRepository только для этого теста
    @BindValue
    @JvmField
    val repository: UserRepository = FastFakeRepository()

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun test_withFastRepository() {
        // Тест с быстрыми ответами
    }
}

@HiltAndroidTest
class SlowNetworkTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val repository: UserRepository = SlowFakeRepository()

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun test_withSlowNetwork() {
        // Тестируем состояния загрузки / таймауты
    }
}
```

### Использование MockK с Hilt

```kotlin
dependencies {
    androidTestImplementation("io.mockk:mockk-android:1.13.8")
}

@HiltAndroidTest
class MockTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    // `@BindValue` заменяет production-реализацию UserRepository в этом тесте
    @BindValue
    @JvmField
    val repository: UserRepository = mockk(relaxed = true)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun test_withMock() {
        coEvery { repository.getUser("1") } returns User("1", "Mock User", "mock@example.com")

        // Код теста, который вызывает repository.getUser("1")

        coVerify { repository.getUser("1") }
    }
}
```

### Лучшие практики

1. Предпочитайте fakes вместо mocks для сложных взаимодействий
2. Используйте `@TestInstallIn` для глобальной замены модулей в тестах
3. Используйте `@BindValue` для конфигурации и переопределения зависимостей на уровне конкретного теста
4. Создавайте переиспользуемые fake-реализации
5. Тестируйте разные сценарии (успех, ошибка, медленная сеть)
6. Очищайте состояние fakes между тестами
7. Держите fakes синхронизированными с реальными контрактами интерфейсов

---

## Answer (EN)

Hilt provides powerful dependency injection testing capabilities, allowing you to replace production dependencies with test doubles (mocks, fakes, stubs) easily in both instrumented and local tests.

### Test Setup with Hilt

```kotlin
dependencies {
    // Hilt test integration for instrumented/androidTest
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.48")
    kaptAndroidTest("com.google.dagger:hilt-android-compiler:2.48")

    // Regular Hilt dependencies for main code (already required in app)
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-android-compiler:2.48")
}
```

Make sure your test `Application` is configured for Hilt (e.g. via `@HiltAndroidApp` in the production app, or using `HiltTestApplication` in the test manifest when needed).

```kotlin
@HiltAndroidTest
class RepositoryTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var repository: UserRepository

    @Before
    fun init() {
        hiltRule.inject()
    }

    @Test
    fun testRepository() {
        // Test with injected repository
    }
}
```

### Replacing Modules with `@TestInstallIn`

```kotlin
// Production module
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
            .create(ApiService::class.java)
    }
}

// Test module - replaces production
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [NetworkModule::class]
)
object FakeNetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return FakeApiService()
    }
}
```

### Creating Fakes

```kotlin
// Real interface
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun updateUser(user: User)
    fun observeUser(id: String): Flow<User>
}

// Fake implementation for testing
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<String, User>()
    private val userFlows = mutableMapOf<String, MutableStateFlow<User?>>()

    var shouldReturnError = false
    var networkDelay = 0L

    override suspend fun getUser(id: String): User {
        delay(networkDelay)
        if (shouldReturnError) {
            throw IOException("Network error")
        }
        return users[id] ?: throw NoSuchElementException("User not found")
    }

    override suspend fun updateUser(user: User) {
        delay(networkDelay)
        if (shouldReturnError) {
            throw IOException("Network error")
        }
        users[user.id] = user
        userFlows[user.id]?.value = user
    }

    override fun observeUser(id: String): Flow<User> {
        return userFlows.getOrPut(id) {
            MutableStateFlow(users[id])
        }.filterNotNull()
    }

    // Test helpers
    fun addUser(user: User) {
        users[user.id] = user
        userFlows[user.id]?.value = user
    }

    fun clear() {
        users.clear()
        userFlows.clear()
    }
}
```

When testing suspend functions and Flows in local unit tests, run them with a proper coroutine test dispatcher (e.g. `runTest` and `StandardTestDispatcher`) to avoid flaky behavior.

### Using Fakes in Tests

```kotlin
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
object FakeRepositoryModule {
    @Provides
    @Singleton
    fun provideUserRepository(): UserRepository {
        return FakeUserRepository()
    }
}

@HiltAndroidTest
class UserScreenTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var repository: UserRepository

    private lateinit var fakeRepository: FakeUserRepository

    @Before
    fun setup() {
        hiltRule.inject()
        fakeRepository = repository as FakeUserRepository
        fakeRepository.clear()
    }

    @Test
    fun userScreen_displaysUser() {
        // Setup fake data
        fakeRepository.addUser(User("1", "John Doe", "john@example.com"))

        composeTestRule.setContent {
            UserScreen(userId = "1")
        }

        composeTestRule.onNodeWithText("John Doe").assertExists()
        composeTestRule.onNodeWithText("john@example.com").assertExists()
    }

    @Test
    fun userScreen_handlesError() {
        fakeRepository.shouldReturnError = true

        composeTestRule.setContent {
            UserScreen(userId = "1")
        }

        composeTestRule.onNodeWithText("Error loading user").assertExists()
    }
}
```

### Multiple Test Configurations

```kotlin
// Configuration 1: Fast fake
class FastFakeRepository : UserRepository {
    // Immediate responses, no delays
    override suspend fun getUser(id: String): User = User(id, "Fast", "fast@example.com")
    override suspend fun updateUser(user: User) { /* no-op */ }
    override fun observeUser(id: String): Flow<User> = flowOf(User(id, "Fast", "fast@example.com"))
}

// Configuration 2: Slow fake
class SlowFakeRepository : UserRepository {
    override suspend fun getUser(id: String): User {
        delay(2_000)
        return User(id, "Slow", "slow@example.com")
    }
    override suspend fun updateUser(user: User) { delay(2_000) }
    override fun observeUser(id: String): Flow<User> = flow {
        delay(2_000)
        emit(User(id, "Slow", "slow@example.com"))
    }
}

// Configuration 3: Error fake
class ErrorFakeRepository : UserRepository {
    override suspend fun getUser(id: String): User = throw IOException("Test error")
    override suspend fun updateUser(user: User) { throw IOException("Test error") }
    override fun observeUser(id: String): Flow<User> = flow { throw IOException("Test error") }
}

// Use @BindValue to inject per-test (replaces existing binding of same type/qualifiers in this test)
@HiltAndroidTest
class ConfigurableTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val repository: UserRepository = FastFakeRepository()

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun test_withFastRepository() {
        // Test with fast responses
    }
}

@HiltAndroidTest
class SlowNetworkTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val repository: UserRepository = SlowFakeRepository()

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun test_withSlowNetwork() {
        // Test loading states, timeouts
    }
}
```

### Using MockK with Hilt

```kotlin
dependencies {
    androidTestImplementation("io.mockk:mockk-android:1.13.8")
}

@HiltAndroidTest
class MockTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    // @BindValue replaces the production binding for UserRepository in this test
    @BindValue
    @JvmField
    val repository: UserRepository = mockk(relaxed = true)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun test_withMock() {
        coEvery { repository.getUser("1") } returns User("1", "Mock User", "mock@example.com")

        // Test code that calls repository.getUser("1")

        coVerify { repository.getUser("1") }
    }
}
```

### Best Practices

1. Prefer fakes over mocks for complex interactions
2. Use `@TestInstallIn` to replace modules globally in tests
3. Use `@BindValue` for per-test configuration (overriding specific bindings)
4. Create reusable fake implementations
5. Test with different configurations (success, error, slow network)
6. Clear fake state between tests
7. Keep fakes in sync with real implementations

---

## Дополнительные вопросы (RU)

- [[c-dependency-injection]]
- [[q-what-is-hilt--android--medium]]

## Follow-ups

- [[c-dependency-injection]]
- [[q-what-is-hilt--android--medium]]

## Ссылки (RU)

- [Local Unit Tests](https://developer.android.com/training/testing/local-tests)
- [Android Documentation](https://developer.android.com/docs)

## References

- [Local Unit Tests](https://developer.android.com/training/testing/local-tests)
- [Android Documentation](https://developer.android.com/docs)

## Связанные вопросы (RU)

### Medium
- [[q-testing-viewmodels-turbine--android--medium]]
- [[q-testing-compose-ui--android--medium]]
- [[q-compose-testing--android--medium]]
- [[q-dagger-build-time-optimization--android--medium]]
- [[q-robolectric-vs-instrumented--android--medium]]

### Hard
- [[q-testing-coroutines-flow--android--hard]]

## Related Questions

### Medium
- [[q-testing-viewmodels-turbine--android--medium]]
- [[q-testing-compose-ui--android--medium]]
- [[q-compose-testing--android--medium]]
- [[q-dagger-build-time-optimization--android--medium]]
- [[q-robolectric-vs-instrumented--android--medium]]

### Hard
- [[q-testing-coroutines-flow--android--hard]]
