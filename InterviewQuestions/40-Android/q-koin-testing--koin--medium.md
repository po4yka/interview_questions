---
id: android-koin-006
title: Koin Testing / Тестирование с Koin
aliases: [Koin Testing, checkModules, KoinTest]
topic: android
subtopics: [di-koin, testing-unit, dependency-injection]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-koin-setup-modules--koin--medium, q-koin-inject-get--koin--medium, q-test-doubles-dependency-injection--android--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/di-koin, android/testing-unit, dependency-injection, difficulty/medium, koin]
---
# Vopros (RU)
> Как тестировать приложение с Koin? Объясните checkModules, mock-и и изоляцию тестов.

# Question (EN)
> How do you test applications with Koin? Explain checkModules, mocks, and test isolation.

---

## Otvet (RU)

Koin предоставляет инструменты для тестирования: проверка модулей, подмена зависимостей и изоляция тестов.

### Подключение тестовых зависимостей

```kotlin
// build.gradle.kts
dependencies {
    // Koin Test
    testImplementation("io.insert-koin:koin-test:3.5.6")
    testImplementation("io.insert-koin:koin-test-junit5:3.5.6")
    // или для JUnit4
    testImplementation("io.insert-koin:koin-test-junit4:3.5.6")

    // MockK для моков
    testImplementation("io.mockk:mockk:1.13.9")
}
```

### checkModules - Проверка конфигурации

**checkModules** верифицирует что все зависимости могут быть разрешены:

```kotlin
class ModuleCheckTest : KoinTest {

    @Test
    fun `verify all modules`() {
        koinApplication {
            modules(
                networkModule,
                databaseModule,
                repositoryModule,
                viewModelModule
            )
        }.checkModules()
    }
}
```

### Проверка модулей с параметрами

```kotlin
val viewModelModule = module {
    viewModel { (userId: String) -> UserViewModel(userId, get()) }
}

class ViewModelModuleTest : KoinTest {

    @Test
    fun `check viewModel with parameters`() {
        koinApplication {
            modules(viewModelModule, repositoryModule)
        }.checkModules {
            // Указываем параметры для проверки
            withParameter<UserViewModel> { parametersOf("test_user_id") }
        }
    }
}
```

### KoinTestRule (JUnit 4)

```kotlin
class UserRepositoryTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { FakeUserRepository() }
                single { UserUseCase(get()) }
            }
        )
    }

    // Автоматическое получение зависимостей
    private val repository: UserRepository by inject()
    private val useCase: UserUseCase by inject()

    @Test
    fun `test user repository`() {
        val user = runBlocking { repository.getUser("123") }
        assertNotNull(user)
    }
}
```

### KoinTestExtension (JUnit 5)

```kotlin
@ExtendWith(KoinTestExtension::class)
class UserServiceTest : KoinTest {

    @JvmField
    @RegisterExtension
    val koinTestExtension = KoinTestExtension.create {
        modules(testModule)
    }

    private val service: UserService by inject()

    @Test
    fun `test service`() {
        // Тест с инжектированным сервисом
    }
}
```

### Mock подмена зависимостей

```kotlin
class UserViewModelTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { mockk(relaxed = true) }
                viewModel { UserViewModel(get()) }
            }
        )
    }

    private val repository: UserRepository by inject()
    private val viewModel: UserViewModel by inject()

    @Test
    fun `test load user`() = runTest {
        // Настройка мока
        coEvery { repository.getUser("123") } returns User("123", "John")

        // Действие
        viewModel.loadUser("123")

        // Проверка
        assertEquals("John", viewModel.state.value.user?.name)
        coVerify { repository.getUser("123") }
    }
}
```

### declareMock для подмены в тесте

```kotlin
class ServiceTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(appModule) // Production модули
    }

    @Test
    fun `test with mock`() {
        // Подменяем конкретную зависимость моком
        val mockRepository = declareMock<UserRepository> {
            coEvery { getUser(any()) } returns User("1", "Mock User")
        }

        val service: UserService = get()
        val user = runBlocking { service.fetchUser("1") }

        assertEquals("Mock User", user.name)
    }
}
```

### Изоляция тестов

```kotlin
class IsolatedTest : KoinTest {

    @Before
    fun setup() {
        // Запуск Koin перед каждым тестом
        startKoin {
            modules(testModule)
        }
    }

    @After
    fun tearDown() {
        // Остановка Koin после каждого теста
        stopKoin()
    }

    @Test
    fun `isolated test 1`() {
        val service: MyService = get()
        // Тест с чистым Koin
    }

    @Test
    fun `isolated test 2`() {
        val service: MyService = get()
        // Другой тест с чистым Koin
    }
}
```

### Тестирование с разными конфигурациями

```kotlin
class ConfigurationTest : KoinTest {

    private fun createTestKoin(environment: String) = koinApplication {
        modules(
            module {
                single(named("env")) { environment }
                single { ConfigService(get(named("env"))) }
            }
        )
    }

    @Test
    fun `test production config`() {
        val koin = createTestKoin("production").koin
        val config = koin.get<ConfigService>()

        assertEquals("production", config.environment)
        koin.close()
    }

    @Test
    fun `test staging config`() {
        val koin = createTestKoin("staging").koin
        val config = koin.get<ConfigService>()

        assertEquals("staging", config.environment)
        koin.close()
    }
}
```

### Тестирование ViewModel

```kotlin
class UserViewModelTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { FakeUserRepository() }
                viewModel { UserViewModel(get()) }
            }
        )
    }

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val viewModel: UserViewModel by inject()

    @Test
    fun `initial state is loading`() {
        assertEquals(UiState.Loading, viewModel.state.value)
    }

    @Test
    fun `load user updates state`() = runTest {
        viewModel.loadUser("123")
        advanceUntilIdle()

        val state = viewModel.state.value
        assertTrue(state is UiState.Success)
    }
}

// Rule для тестирования корутин
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description?) {
        Dispatchers.setMain(dispatcher)
    }

    override fun finished(description: Description?) {
        Dispatchers.resetMain()
    }
}
```

### Тестирование Scopes

```kotlin
class ScopeTest : KoinTest {

    @Test
    fun `test scoped dependencies`() {
        val koin = koinApplication {
            modules(
                module {
                    scope(named("session")) {
                        scoped { SessionData() }
                        scoped { SessionRepository(get()) }
                    }
                }
            )
        }.koin

        // Создаем scope
        val scope = koin.createScope("test_session", named("session"))

        // Получаем scoped зависимости
        val data1 = scope.get<SessionData>()
        val data2 = scope.get<SessionData>()

        // Один и тот же экземпляр в scope
        assertSame(data1, data2)

        // Закрываем scope
        scope.close()

        // Новый scope - новые экземпляры
        val newScope = koin.createScope("new_session", named("session"))
        val data3 = newScope.get<SessionData>()

        assertNotSame(data1, data3)

        newScope.close()
        koin.close()
    }
}
```

### Integration тестирование

```kotlin
@RunWith(AndroidJUnit4::class)
class UserFlowIntegrationTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        androidContext(ApplicationProvider.getApplicationContext())
        modules(
            module {
                single<UserRepository> { InMemoryUserRepository() }
                single<UserApi> { FakeUserApi() }
                viewModel { UserListViewModel(get()) }
            }
        )
    }

    @Test
    fun userListFlow() = runTest {
        val viewModel: UserListViewModel = get()

        // Initial load
        viewModel.refresh()
        advanceUntilIdle()

        val users = viewModel.users.value
        assertTrue(users.isNotEmpty())
    }
}
```

### Лучшие практики

1. **checkModules в CI** - запускайте проверку модулей в CI pipeline
2. **Изоляция тестов** - каждый тест с чистым Koin
3. **Fake > Mock** - предпочитайте fake реализации для сложной логики
4. **declareMock** - для точечной подмены в конкретном тесте
5. **Тестовые модули** - создавайте отдельные модули для тестов

```kotlin
// Тестовый модуль
val testModule = module {
    single<UserRepository> { FakeUserRepository() }
    single<ApiService> { FakeApiService() }
    single<Clock> { TestClock() }
}

// Использование в тестах
@get:Rule
val koinTestRule = KoinTestRule.create {
    modules(testModule)
}
```

---

## Answer (EN)

Koin provides tools for testing: module verification, dependency substitution, and test isolation.

### Adding Test Dependencies

```kotlin
// build.gradle.kts
dependencies {
    // Koin Test
    testImplementation("io.insert-koin:koin-test:3.5.6")
    testImplementation("io.insert-koin:koin-test-junit5:3.5.6")
    // or for JUnit4
    testImplementation("io.insert-koin:koin-test-junit4:3.5.6")

    // MockK for mocks
    testImplementation("io.mockk:mockk:1.13.9")
}
```

### checkModules - Configuration Verification

**checkModules** verifies that all dependencies can be resolved:

```kotlin
class ModuleCheckTest : KoinTest {

    @Test
    fun `verify all modules`() {
        koinApplication {
            modules(
                networkModule,
                databaseModule,
                repositoryModule,
                viewModelModule
            )
        }.checkModules()
    }
}
```

### Checking Modules with Parameters

```kotlin
val viewModelModule = module {
    viewModel { (userId: String) -> UserViewModel(userId, get()) }
}

class ViewModelModuleTest : KoinTest {

    @Test
    fun `check viewModel with parameters`() {
        koinApplication {
            modules(viewModelModule, repositoryModule)
        }.checkModules {
            // Specify parameters for verification
            withParameter<UserViewModel> { parametersOf("test_user_id") }
        }
    }
}
```

### KoinTestRule (JUnit 4)

```kotlin
class UserRepositoryTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { FakeUserRepository() }
                single { UserUseCase(get()) }
            }
        )
    }

    // Automatic dependency retrieval
    private val repository: UserRepository by inject()
    private val useCase: UserUseCase by inject()

    @Test
    fun `test user repository`() {
        val user = runBlocking { repository.getUser("123") }
        assertNotNull(user)
    }
}
```

### KoinTestExtension (JUnit 5)

```kotlin
@ExtendWith(KoinTestExtension::class)
class UserServiceTest : KoinTest {

    @JvmField
    @RegisterExtension
    val koinTestExtension = KoinTestExtension.create {
        modules(testModule)
    }

    private val service: UserService by inject()

    @Test
    fun `test service`() {
        // Test with injected service
    }
}
```

### Mock Dependency Substitution

```kotlin
class UserViewModelTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { mockk(relaxed = true) }
                viewModel { UserViewModel(get()) }
            }
        )
    }

    private val repository: UserRepository by inject()
    private val viewModel: UserViewModel by inject()

    @Test
    fun `test load user`() = runTest {
        // Setup mock
        coEvery { repository.getUser("123") } returns User("123", "John")

        // Action
        viewModel.loadUser("123")

        // Verification
        assertEquals("John", viewModel.state.value.user?.name)
        coVerify { repository.getUser("123") }
    }
}
```

### declareMock for In-Test Substitution

```kotlin
class ServiceTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(appModule) // Production modules
    }

    @Test
    fun `test with mock`() {
        // Replace specific dependency with mock
        val mockRepository = declareMock<UserRepository> {
            coEvery { getUser(any()) } returns User("1", "Mock User")
        }

        val service: UserService = get()
        val user = runBlocking { service.fetchUser("1") }

        assertEquals("Mock User", user.name)
    }
}
```

### Test Isolation

```kotlin
class IsolatedTest : KoinTest {

    @Before
    fun setup() {
        // Start Koin before each test
        startKoin {
            modules(testModule)
        }
    }

    @After
    fun tearDown() {
        // Stop Koin after each test
        stopKoin()
    }

    @Test
    fun `isolated test 1`() {
        val service: MyService = get()
        // Test with clean Koin
    }

    @Test
    fun `isolated test 2`() {
        val service: MyService = get()
        // Another test with clean Koin
    }
}
```

### Testing with Different Configurations

```kotlin
class ConfigurationTest : KoinTest {

    private fun createTestKoin(environment: String) = koinApplication {
        modules(
            module {
                single(named("env")) { environment }
                single { ConfigService(get(named("env"))) }
            }
        )
    }

    @Test
    fun `test production config`() {
        val koin = createTestKoin("production").koin
        val config = koin.get<ConfigService>()

        assertEquals("production", config.environment)
        koin.close()
    }

    @Test
    fun `test staging config`() {
        val koin = createTestKoin("staging").koin
        val config = koin.get<ConfigService>()

        assertEquals("staging", config.environment)
        koin.close()
    }
}
```

### Testing ViewModel

```kotlin
class UserViewModelTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { FakeUserRepository() }
                viewModel { UserViewModel(get()) }
            }
        )
    }

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val viewModel: UserViewModel by inject()

    @Test
    fun `initial state is loading`() {
        assertEquals(UiState.Loading, viewModel.state.value)
    }

    @Test
    fun `load user updates state`() = runTest {
        viewModel.loadUser("123")
        advanceUntilIdle()

        val state = viewModel.state.value
        assertTrue(state is UiState.Success)
    }
}

// Rule for coroutine testing
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description?) {
        Dispatchers.setMain(dispatcher)
    }

    override fun finished(description: Description?) {
        Dispatchers.resetMain()
    }
}
```

### Testing Scopes

```kotlin
class ScopeTest : KoinTest {

    @Test
    fun `test scoped dependencies`() {
        val koin = koinApplication {
            modules(
                module {
                    scope(named("session")) {
                        scoped { SessionData() }
                        scoped { SessionRepository(get()) }
                    }
                }
            )
        }.koin

        // Create scope
        val scope = koin.createScope("test_session", named("session"))

        // Get scoped dependencies
        val data1 = scope.get<SessionData>()
        val data2 = scope.get<SessionData>()

        // Same instance within scope
        assertSame(data1, data2)

        // Close scope
        scope.close()

        // New scope - new instances
        val newScope = koin.createScope("new_session", named("session"))
        val data3 = newScope.get<SessionData>()

        assertNotSame(data1, data3)

        newScope.close()
        koin.close()
    }
}
```

### Integration Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class UserFlowIntegrationTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        androidContext(ApplicationProvider.getApplicationContext())
        modules(
            module {
                single<UserRepository> { InMemoryUserRepository() }
                single<UserApi> { FakeUserApi() }
                viewModel { UserListViewModel(get()) }
            }
        )
    }

    @Test
    fun userListFlow() = runTest {
        val viewModel: UserListViewModel = get()

        // Initial load
        viewModel.refresh()
        advanceUntilIdle()

        val users = viewModel.users.value
        assertTrue(users.isNotEmpty())
    }
}
```

### Best Practices

1. **checkModules in CI** - run module verification in CI pipeline
2. **Test isolation** - each test with clean Koin
3. **Fake > Mock** - prefer fake implementations for complex logic
4. **declareMock** - for targeted substitution in specific test
5. **Test modules** - create separate modules for tests

```kotlin
// Test module
val testModule = module {
    single<UserRepository> { FakeUserRepository() }
    single<ApiService> { FakeApiService() }
    single<Clock> { TestClock() }
}

// Usage in tests
@get:Rule
val koinTestRule = KoinTestRule.create {
    modules(testModule)
}
```

---

## Dopolnitelnye Voprosy (RU)

- Как использовать checkModules с Android контекстом?
- В чем разница между declareMock и определением мока в модуле?
- Как тестировать scoped зависимости в Koin?

## Follow-ups

- How do you use checkModules with Android context?
- What is the difference between declareMock and defining a mock in a module?
- How do you test scoped dependencies in Koin?

## Ssylki (RU)

- [Koin Testing](https://insert-koin.io/docs/reference/koin-test/testing)
- [Koin Test Extensions](https://insert-koin.io/docs/reference/koin-test/checkmodules)

## References

- [Koin Testing](https://insert-koin.io/docs/reference/koin-test/testing)
- [Koin Test Extensions](https://insert-koin.io/docs/reference/koin-test/checkmodules)

## Svyazannye Voprosy (RU)

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-test-doubles-dependency-injection--android--medium]]
- [[q-testing-viewmodels-turbine--android--medium]]

## Related Questions

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-test-doubles-dependency-injection--android--medium]]
- [[q-testing-viewmodels-turbine--android--medium]]
