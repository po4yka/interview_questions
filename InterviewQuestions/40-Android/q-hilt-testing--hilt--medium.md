---
id: android-hilt-009
title: Hilt Testing / Тестирование с Hilt
aliases:
- Hilt Testing
- HiltAndroidTest
- UninstallModules
- Test Dependencies
- Hilt Test
topic: android
subtopics:
- di-hilt
- testing-unit
- testing-integration
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-hilt-setup-annotations--hilt--medium
- q-hilt-modules-provides--hilt--medium
- q-test-doubles-dependency-injection--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/testing-unit
- android/testing-integration
- difficulty/medium
- hilt
- testing
- dependency-injection
anki_cards:
- slug: android-hilt-009-0-en
  language: en
- slug: android-hilt-009-0-ru
  language: ru
---
# Vopros (RU)
> Как тестировать приложение с Hilt? Объясните @HiltAndroidTest, @UninstallModules, @BindValue и замену зависимостей в тестах.

# Question (EN)
> How do you test an application with Hilt? Explain @HiltAndroidTest, @UninstallModules, @BindValue, and dependency replacement in tests.

---

## Otvet (RU)

Hilt предоставляет мощный инструментарий для тестирования, позволяя легко заменять production-зависимости на тестовые (fakes, mocks, stubs) как в инструментальных, так и в unit-тестах.

### Настройка тестов

```kotlin
// build.gradle.kts (app)
dependencies {
    // Hilt testing
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.52")
    kspAndroidTest("com.google.dagger:hilt-android-compiler:2.52")

    // Для unit-тестов с Robolectric
    testImplementation("com.google.dagger:hilt-android-testing:2.52")
    kspTest("com.google.dagger:hilt-android-compiler:2.52")

    // Дополнительные тестовые зависимости
    androidTestImplementation("androidx.test:runner:1.5.2")
    androidTestImplementation("androidx.test:rules:1.5.0")
}
```

### Кастомный Test Runner

```kotlin
// HiltTestRunner.kt
class HiltTestRunner : AndroidJUnitRunner() {

    override fun newApplication(
        cl: ClassLoader?,
        className: String?,
        context: Context?
    ): Application {
        return super.newApplication(cl, HiltTestApplication::class.java.name, context)
    }
}

// build.gradle.kts
android {
    defaultConfig {
        testInstrumentationRunner = "com.example.HiltTestRunner"
    }
}
```

### @HiltAndroidTest - базовое использование

```kotlin
@HiltAndroidTest
class UserRepositoryTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var userRepository: UserRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testGetUser() = runTest {
        val user = userRepository.getUser("123")
        assertNotNull(user)
        assertEquals("123", user.id)
    }
}
```

### @TestInstallIn - глобальная замена модулей

Заменяет production-модуль во ВСЕХ тестах:

```kotlin
// Production модуль
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// Тестовый модуль - заменяет production во всех тестах
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class FakeRepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: FakeUserRepository): UserRepository
}

// Fake реализация
class FakeUserRepository @Inject constructor() : UserRepository {

    private val users = mutableMapOf<String, User>()
    var shouldFail = false
    var delayMs = 0L

    override suspend fun getUser(id: String): User {
        delay(delayMs)
        if (shouldFail) throw IOException("Test error")
        return users[id] ?: throw NoSuchElementException("User not found")
    }

    override suspend fun saveUser(user: User) {
        delay(delayMs)
        if (shouldFail) throw IOException("Test error")
        users[user.id] = user
    }

    // Хелперы для тестов
    fun addUser(user: User) {
        users[user.id] = user
    }

    fun clear() {
        users.clear()
        shouldFail = false
        delayMs = 0L
    }
}
```

### @UninstallModules - замена для конкретного теста

```kotlin
@HiltAndroidTest
@UninstallModules(NetworkModule::class) // Убираем production модуль
class OfflineUserTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    // Предоставляем свою реализацию через @BindValue
    @BindValue
    @JvmField
    val apiService: ApiService = FakeOfflineApiService()

    @Inject
    lateinit var userRepository: UserRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testOfflineMode() = runTest {
        // Тест с fake API, который всегда возвращает ошибку сети
    }
}

class FakeOfflineApiService : ApiService {
    override suspend fun getUser(id: String): User {
        throw IOException("No network connection")
    }
}
```

### @BindValue - замена конкретной зависимости

```kotlin
@HiltAndroidTest
class LoginViewModelTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    // @BindValue заменяет биндинг для этого конкретного теста
    @BindValue
    @JvmField
    val authRepository: AuthRepository = mockk(relaxed = true)

    @Inject
    lateinit var analyticsService: AnalyticsService // Остается production

    private lateinit var viewModel: LoginViewModel

    @Before
    fun setup() {
        hiltRule.inject()
        viewModel = LoginViewModel(authRepository, analyticsService)
    }

    @Test
    fun `successful login updates state`() = runTest {
        // Arrange
        coEvery { authRepository.login(any(), any()) } returns Result.success(testUser)

        // Act
        viewModel.login("test@example.com", "password")

        // Assert
        assertEquals(LoginState.Success(testUser), viewModel.state.value)
        coVerify { authRepository.login("test@example.com", "password") }
    }

    @Test
    fun `failed login shows error`() = runTest {
        // Arrange
        coEvery { authRepository.login(any(), any()) } returns Result.failure(Exception("Invalid credentials"))

        // Act
        viewModel.login("test@example.com", "wrong")

        // Assert
        assertTrue(viewModel.state.value is LoginState.Error)
    }

    companion object {
        private val testUser = User("1", "Test User", "test@example.com")
    }
}
```

### Тестирование с Compose

```kotlin
@HiltAndroidTest
class UserScreenTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @BindValue
    @JvmField
    val userRepository: UserRepository = FakeUserRepository().apply {
        addUser(User("1", "John Doe", "john@example.com"))
    }

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun userScreen_displaysUserInfo() {
        composeTestRule.setContent {
            UserScreen(userId = "1")
        }

        composeTestRule.onNodeWithText("John Doe").assertIsDisplayed()
        composeTestRule.onNodeWithText("john@example.com").assertIsDisplayed()
    }

    @Test
    fun userScreen_showsLoadingState() {
        (userRepository as FakeUserRepository).delayMs = 5000

        composeTestRule.setContent {
            UserScreen(userId = "1")
        }

        composeTestRule.onNodeWithTag("loading").assertIsDisplayed()
    }

    @Test
    fun userScreen_showsErrorOnFailure() {
        (userRepository as FakeUserRepository).shouldFail = true

        composeTestRule.setContent {
            UserScreen(userId = "1")
        }

        composeTestRule.onNodeWithText("Error loading user").assertIsDisplayed()
    }
}
```

### Unit-тесты без Android (чистый Kotlin)

Для unit-тестов ViewModel можно не использовать Hilt:

```kotlin
class UserViewModelTest {

    private lateinit var viewModel: UserViewModel
    private lateinit var fakeRepository: FakeUserRepository

    @Before
    fun setup() {
        fakeRepository = FakeUserRepository()
        viewModel = UserViewModel(
            userRepository = fakeRepository,
            savedStateHandle = SavedStateHandle(mapOf("userId" to "123"))
        )
    }

    @Test
    fun `loadUser success updates state`() = runTest {
        // Arrange
        fakeRepository.addUser(User("123", "Test User", "test@example.com"))

        // Act
        viewModel.loadUser()

        // Assert
        val state = viewModel.uiState.value
        assertTrue(state is UserUiState.Success)
        assertEquals("Test User", (state as UserUiState.Success).user.name)
    }

    @Test
    fun `loadUser failure shows error`() = runTest {
        // Arrange
        fakeRepository.shouldFail = true

        // Act
        viewModel.loadUser()

        // Assert
        assertTrue(viewModel.uiState.value is UserUiState.Error)
    }
}
```

### Тестирование с Robolectric

```kotlin
@HiltAndroidTest
@Config(application = HiltTestApplication::class)
@RunWith(RobolectricTestRunner::class)
class RobolectricUserTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var userRepository: UserRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testWithRobolectric() = runTest {
        val user = userRepository.getUser("123")
        assertNotNull(user)
    }
}
```

### Паттерн: Настраиваемые Fakes

```kotlin
// Базовый fake с настраиваемым поведением
class ConfigurableFakeUserRepository @Inject constructor() : UserRepository {

    sealed interface Behavior {
        data object Success : Behavior
        data class Error(val exception: Exception) : Behavior
        data class Delay(val millis: Long) : Behavior
    }

    var getUserBehavior: Behavior = Behavior.Success
    var saveUserBehavior: Behavior = Behavior.Success

    private val storage = mutableMapOf<String, User>()

    override suspend fun getUser(id: String): User {
        return when (val behavior = getUserBehavior) {
            is Behavior.Success -> storage[id] ?: throw NoSuchElementException()
            is Behavior.Error -> throw behavior.exception
            is Behavior.Delay -> {
                delay(behavior.millis)
                storage[id] ?: throw NoSuchElementException()
            }
        }
    }

    override suspend fun saveUser(user: User) {
        when (val behavior = saveUserBehavior) {
            is Behavior.Success -> storage[user.id] = user
            is Behavior.Error -> throw behavior.exception
            is Behavior.Delay -> {
                delay(behavior.millis)
                storage[user.id] = user
            }
        }
    }

    fun seed(vararg users: User) {
        users.forEach { storage[it.id] = it }
    }

    fun reset() {
        storage.clear()
        getUserBehavior = Behavior.Success
        saveUserBehavior = Behavior.Success
    }
}

// Использование в тесте
@HiltAndroidTest
class ConfigurableFakeTest {

    @BindValue
    @JvmField
    val repository = ConfigurableFakeUserRepository()

    @Test
    fun `test network error handling`() = runTest {
        repository.getUserBehavior = ConfigurableFakeUserRepository.Behavior.Error(
            IOException("Network error")
        )

        // Test error handling...
    }

    @Test
    fun `test slow network`() = runTest {
        repository.getUserBehavior = ConfigurableFakeUserRepository.Behavior.Delay(2000)

        // Test loading state...
    }
}
```

### Best Practices

1. **Предпочитайте Fakes вместо Mocks** - более читаемые и поддерживаемые тесты
2. **Используйте @TestInstallIn для глобальных замен** - fakes, которые нужны везде
3. **Используйте @BindValue для конкретных тестов** - специфичные конфигурации
4. **Очищайте состояние между тестами** - вызывайте reset() в @Before
5. **Тестируйте граничные случаи** - ошибки, таймауты, пустые данные

---

## Answer (EN)

Hilt provides a powerful testing toolkit that allows easy replacement of production dependencies with test doubles (fakes, mocks, stubs) in both instrumented and unit tests.

### Test Setup

```kotlin
// build.gradle.kts (app)
dependencies {
    // Hilt testing
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.52")
    kspAndroidTest("com.google.dagger:hilt-android-compiler:2.52")

    // For unit tests with Robolectric
    testImplementation("com.google.dagger:hilt-android-testing:2.52")
    kspTest("com.google.dagger:hilt-android-compiler:2.52")
}
```

### Custom Test Runner

```kotlin
class HiltTestRunner : AndroidJUnitRunner() {

    override fun newApplication(
        cl: ClassLoader?,
        className: String?,
        context: Context?
    ): Application {
        return super.newApplication(cl, HiltTestApplication::class.java.name, context)
    }
}
```

### @HiltAndroidTest - Basic Usage

```kotlin
@HiltAndroidTest
class UserRepositoryTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var userRepository: UserRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testGetUser() = runTest {
        val user = userRepository.getUser("123")
        assertNotNull(user)
    }
}
```

### @TestInstallIn - Global Module Replacement

Replaces production module in ALL tests:

```kotlin
// Test module - replaces production in all tests
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class FakeRepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: FakeUserRepository): UserRepository
}
```

### @UninstallModules - Replacement for Specific Test

```kotlin
@HiltAndroidTest
@UninstallModules(NetworkModule::class) // Remove production module
class OfflineUserTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val apiService: ApiService = FakeOfflineApiService()

    @Inject
    lateinit var userRepository: UserRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }
}
```

### @BindValue - Replace Specific Dependency

```kotlin
@HiltAndroidTest
class LoginViewModelTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    // @BindValue replaces binding for this specific test
    @BindValue
    @JvmField
    val authRepository: AuthRepository = mockk(relaxed = true)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun `successful login updates state`() = runTest {
        coEvery { authRepository.login(any(), any()) } returns Result.success(testUser)

        // Test...
    }
}
```

### Best Practices

1. **Prefer Fakes over Mocks** - more readable and maintainable tests
2. **Use @TestInstallIn for global replacements** - fakes needed everywhere
3. **Use @BindValue for specific tests** - specific configurations
4. **Clear state between tests** - call reset() in @Before
5. **Test edge cases** - errors, timeouts, empty data

---

## Dopolnitelnye Voprosy (RU)

- Когда использовать Fake вместо Mock?
- Как тестировать ViewModel без Hilt?
- Как организовать тестовые модули в многомодульном проекте?
- Как тестировать классы с @EntryPoint?

## Follow-ups

- When to use Fake instead of Mock?
- How to test ViewModel without Hilt?
- How to organize test modules in a multi-module project?
- How to test classes with @EntryPoint?

---

## Ssylki (RU)

- [Hilt Testing Documentation](https://developer.android.com/training/dependency-injection/hilt-testing)
- [Android Testing Guide](https://developer.android.com/training/testing)

## References

- [Hilt Testing Documentation](https://developer.android.com/training/dependency-injection/hilt-testing)
- [Android Testing Guide](https://developer.android.com/training/testing)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-test-doubles-dependency-injection--android--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-testing-coroutines-flow--android--hard]]

## Related Questions

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-test-doubles-dependency-injection--android--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-testing-coroutines-flow--android--hard]]
