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
- c-testing
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
date created: Saturday, November 1st 2025, 12:47:05 pm
date modified: Saturday, November 1st 2025, 5:43:29 pm
---

# Вопрос (RU)
> Тестовые двойники Dependency Injection

# Question (EN)
> Test Doubles Dependency Injection

---

## Answer (EN)

Hilt provides powerful dependency injection testing capabilities, allowing you to replace production dependencies with test doubles (mocks, fakes, stubs) easily.

### Test Setup with Hilt

```kotlin
dependencies {
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.48")
    kaptAndroidTest("com.google.dagger:hilt-android-compiler:2.48")
}

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

### Replacing Modules with @TestInstallIn

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
}

// Configuration 2: Slow fake
class SlowFakeRepository : UserRepository {
    // Simulates network delays
}

// Configuration 3: Error fake
class ErrorFakeRepository : UserRepository {
    // Always returns errors
}

// Use BindValue to inject per-test
@HiltAndroidTest
class ConfigurableTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val repository: UserRepository = FastFakeRepository()

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

    @BindValue
    @JvmField
    val repository: UserRepository = mockk(relaxed = true)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun test_withMock() {
        coEvery { repository.getUser("1") } returns User("1", "Mock User")

        // Test code

        coVerify { repository.getUser("1") }
    }
}
```

### Best Practices

1. **Prefer fakes over mocks** for complex interactions
2. **Use @TestInstallIn** to replace modules globally
3. **Use @BindValue** for per-test configuration
4. **Create reusable fake implementations**
5. **Test with different configurations** (success, error, slow network)
6. **Clear fake state** between tests
7. **Keep fakes in sync** with real implementations

## Ответ (RU)

Hilt предоставляет мощные возможности для тестирования с dependency injection, позволяя легко заменять production зависимости на test doubles (mock'и, fake'и, stub'ы).


### @TestInstallIn Для Замены Модулей

Позволяет заменить production модули test модулями глобально.

### Создание Fakes

Fake - это рабочая реализация с упрощенным поведением для тестов.

[Полные примеры приведены в английском разделе]

### Лучшие Практики

1. **Предпочитайте fakes вместо mocks** для сложных взаимодействий
2. **Используйте @TestInstallIn** для глобальной замены модулей
3. **Используйте @BindValue** для конфигурации на уровне теста
4. **Создавайте переиспользуемые fake реализации**
5. **Тестируйте с разными конфигурациями**
6. **Очищайте состояние fakes** между тестами
7. **Держите fakes синхронизированными** с реальными реализациями

---


## Follow-ups

- [[c-dependency-injection]]
- [[c-testing]]
- [[q-what-is-hilt--android--medium]]


## References

- [Local Unit Tests](https://developer.android.com/training/testing/local-tests)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-dagger-build-time-optimization--android--medium]] - Dependency Injection
- [[q-robolectric-vs-instrumented--android--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing
