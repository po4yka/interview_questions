---
id: android-120
title: Integration Testing Strategies / Стратегии интеграционного тестирования
aliases:
- Integration Testing Strategies
- Стратегии интеграционного тестирования
topic: android
subtopics:
- testing-instrumented
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-testing
- q-android-manifest-file--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/testing-instrumented
- difficulty/medium

---

# Вопрос (RU)
> Стратегии интеграционного тестирования

# Question (EN)
> Integration Testing Strategies

---

## Ответ (RU)

Интеграционные тесты проверяют, что несколько компонентов корректно работают вместе. Они фокусируются на взаимодействии между слоями приложения, при этом внешние зависимости (сеть, системные сервисы, сторонние SDK) заменяются моками или фейками.

### Пирамида тестирования

```
    E2E-тесты (UI / Full Stack)
        ↑
Интеграционные тесты (несколько слоёв)
        ↑
  Юнит-тесты (отдельные компоненты)
```

### Стратегия тестирования

1. `ViewModel` + Repository + локальная БД (Room):
   - Мокаем/фейкаем только сетевой слой.
   - Реальными являются `ViewModel`, Repository, Room.

2. Repository + сеть + кеш:
   - Минимизируем мокинг (например, используем MockWebServer или фейковый API).
   - Тестируем реальную логику репозитория, кеширование и (опционально) сериализацию.

3. Full `Stack` (кроме внешних сервисов):
   - Мокаем только внешние API и системные сервисы.
   - Используем реальные слои приложения (БД, репозитории, `ViewModel`, UI) — по сути высокоуровневый интеграционный / E2E-тест внутри границ приложения.

### Пример: интеграционный тест UserRepository

```kotlin
@RunWith(AndroidJUnit4::class)
class UserRepositoryIntegrationTest {
    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao
    private lateinit var fakeApiService: FakeApiService
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        // Используем in-memory базу данных для детерминированных и быстрых тестов
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(
            context,
            AppDatabase::class.java
        ).build()

        userDao = database.userDao()
        fakeApiService = FakeApiService()
        repository = UserRepositoryImpl(userDao, fakeApiService)
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun getUser_cachesInDatabase() = runTest {
        // Настраиваем фейковые данные удаленного источника
        fakeApiService.users["1"] = User("1", "John", "john@example.com")

        // Первый запрос — из сети, затем кеширование
        val user1 = repository.getUser("1")
        assertEquals("John", user1.name)

        // Проверяем, что пользователь сохранен в БД
        val cached = userDao.getUser("1")
        assertNotNull(cached)
        assertEquals("John", cached?.name)

        // Второй запрос — должен использовать кеш даже при ошибке сети
        fakeApiService.shouldReturnError = true
        val user2 = repository.getUser("1")
        assertEquals("John", user2.name)
    }

    @Test
    fun updateUser_syncsWithNetwork() = runTest {
        // Исходный пользователь в БД
        val user = User("1", "John", "john@example.com")
        userDao.insert(user)

        // Обновляем через репозиторий
        val updated = user.copy(name = "Jane")
        repository.updateUser(updated)

        // Проверяем обновление в БД
        val fromDb = userDao.getUser("1")
        assertEquals("Jane", fromDb?.name)

        // Проверяем, что изменения отправлены на сеть
        assertEquals("Jane", fakeApiService.users["1"]?.name)
    }

    @Test
    fun observeUser_receivesUpdates() = runTest {
        val user = User("1", "John", "john@example.com")
        userDao.insert(user)

        val values = mutableListOf<User>()
        val job = launch {
            repository.observeUser("1").collect {
                values.add(it)
            }
        }

        // Симулируем обновление
        val updated = user.copy(name = "Jane")
        userDao.update(updated)

        // Даем эмиссиям завершиться
        advanceUntilIdle()
        job.cancel()

        assertTrue(values.any { it.name == "John" })
        assertTrue(values.any { it.name == "Jane" })
    }
}
```

### Интеграция `ViewModel` + Repository

```kotlin
class UserViewModelIntegrationTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: UserViewModel
    private lateinit var fakeRepository: FakeUserRepository

    @Before
    fun setup() {
        fakeRepository = FakeUserRepository()
        viewModel = UserViewModel(fakeRepository)
    }

    @Test
    fun loadUser_success() = runTest {
        // Настраиваем данные
        fakeRepository.addUser(User("1", "John", "john@example.com"))

        val states = mutableListOf<UiState>()
        val job = launch {
            viewModel.uiState.collect { states.add(it) }
        }

        // Запускаем загрузку
        viewModel.loadUser("1")
        advanceUntilIdle()
        job.cancel()

        assertTrue(states.first() is UiState.Loading)
        assertTrue(states.any { it is UiState.Success })
    }

    @Test
    fun loadUser_error() = runTest {
        fakeRepository.shouldReturnError = true

        viewModel.loadUser("1")
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
    }
}
```

### Full `Stack` интеграционный / E2E-тест

```kotlin
@HiltAndroidTest
class FullStackIntegrationTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var database: AppDatabase

    @Before
    fun setup() {
        hiltRule.inject()
        database.clearAllTables()
    }

    @Test
    fun completeUserFlow() {
        // 1. Начальное пустое состояние
        composeTestRule.onNodeWithText("No users").assertExists()

        // 2. Добавляем пользователя
        composeTestRule.onNodeWithTag("add_user_button").performClick()
        composeTestRule.onNodeWithTag("name_input").performTextInput("John")
        composeTestRule.onNodeWithTag("email_input").performTextInput("john@example.com")
        composeTestRule.onNodeWithTag("save_button").performClick()

        // 3. Проверяем отображение пользователя
        composeTestRule.onNodeWithText("John").assertExists()
        composeTestRule.onNodeWithText("john@example.com").assertExists()

        // 4. Редактируем пользователя
        composeTestRule.onNodeWithText("John").performClick()
        composeTestRule.onNodeWithTag("edit_button").performClick()
        composeTestRule.onNodeWithTag("name_input").performTextClearance()
        composeTestRule.onNodeWithTag("name_input").performTextInput("Jane")
        composeTestRule.onNodeWithTag("save_button").performClick()

        // 5. Проверяем обновление
        composeTestRule.onNodeWithText("Jane").assertExists()
        composeTestRule.onNodeWithText("John").assertDoesNotExist()

        // 6. Удаляем пользователя
        composeTestRule.onNodeWithText("Jane").performClick()
        composeTestRule.onNodeWithTag("delete_button").performClick()
        composeTestRule.onNodeWithText("Confirm").performClick()

        // 7. Проверяем пустое состояние
        composeTestRule.onNodeWithText("No users").assertExists()
    }
}
```

### Лучшие практики

1. Используйте in-memory БД для скорости и детерминизма.
2. Мокируйте или фейкайте только внешние зависимости (сеть, файловая система, системные сервисы, сторонние SDK).
3. Тестируйте реалистичные сценарии, проходящие через несколько слоёв.
4. Проверяйте изменения состояния и поток данных, а не только единичные вызовы.
5. Очищайте состояние между тестами (очистка БД, сброс фейков/моков).
6. Покрывайте негативные сценарии: ошибки сети, парсинга, БД и корректные фоллбеки.
7. Соблюдайте баланс между покрытием и скоростью: максимум логики — в юнит-тестах, ключевые потоки — в интеграционных тестах.

---

## Answer (EN)

Integration tests verify that multiple components work together correctly. They test the interaction between layers while mocking or faking external dependencies like network and system services.

### Integration Test Pyramid

```
    E2E Tests (UI / Full Stack)
        ↑
Integration Tests (Multiple Layers)
        ↑
  Unit Tests (Single Components)
```

### Testing Strategy

**1. `ViewModel` + Repository + Local Database**
- Mock/Fake: Network API
- Real: `ViewModel`, Repository, Room Database

**2. Repository + Network + Cache**
- Mock/Fake: Prefer minimal mocking (e.g., use OkHttp MockWebServer or fake API)
- Real: Repository logic, caching, (optionally) serialization

**3. Full `Stack` (except external services)**
- Mock/Fake: Only external APIs, system services
- Real: All app layers (DB, repositories, ViewModels, UI) — this effectively becomes a high-level integration / E2E-style test inside your app boundary

### Example: UserRepository Integration Test

```kotlin
@RunWith(AndroidJUnit4::class)
class UserRepositoryIntegrationTest {
    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao
    private lateinit var fakeApiService: FakeApiService
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        // Use in-memory database for deterministic, fast tests
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(
            context,
            AppDatabase::class.java
        ).build()

        userDao = database.userDao()
        fakeApiService = FakeApiService()
        repository = UserRepositoryImpl(userDao, fakeApiService)
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun getUser_cachesInDatabase() = runTest {
        // Setup fake remote data
        fakeApiService.users["1"] = User("1", "John", "john@example.com")

        // First fetch - from network, then cached
        val user1 = repository.getUser("1")
        assertEquals("John", user1.name)

        // Verify cached in database
        val cached = userDao.getUser("1")
        assertNotNull(cached)
        assertEquals("John", cached?.name)

        // Second fetch - should use cache even if network fails
        fakeApiService.shouldReturnError = true
        val user2 = repository.getUser("1")
        assertEquals("John", user2.name)
    }

    @Test
    fun updateUser_syncsWithNetwork() = runTest {
        // Setup initial user in DB
        val user = User("1", "John", "john@example.com")
        userDao.insert(user)

        // Update via repository
        val updated = user.copy(name = "Jane")
        repository.updateUser(updated)

        // Verify database updated
        val fromDb = userDao.getUser("1")
        assertEquals("Jane", fromDb?.name)

        // Verify network called / synced
        assertEquals("Jane", fakeApiService.users["1"]?.name)
    }

    @Test
    fun observeUser_receivesUpdates() = runTest {
        val user = User("1", "John", "john@example.com")
        userDao.insert(user)

        val values = mutableListOf<User>()
        val job = launch {
            repository.observeUser("1").collect {
                values.add(it)
            }
        }

        // Simulate update
        val updated = user.copy(name = "Jane")
        userDao.update(updated)

        // Let emissions propagate
        advanceUntilIdle()
        job.cancel()

        assertTrue(values.any { it.name == "John" })
        assertTrue(values.any { it.name == "Jane" })
    }
}
```

(Assumes kotlinx-coroutines-test `runTest`/`advanceUntilIdle` and appropriate imports.)

### `ViewModel` + Repository Integration

```kotlin
class UserViewModelIntegrationTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: UserViewModel
    private lateinit var fakeRepository: FakeUserRepository

    @Before
    fun setup() {
        fakeRepository = FakeUserRepository()
        viewModel = UserViewModel(fakeRepository)
    }

    @Test
    fun loadUser_success() = runTest {
        // Setup
        fakeRepository.addUser(User("1", "John", "john@example.com"))

        val states = mutableListOf<UiState>()
        val job = launch {
            viewModel.uiState.collect { states.add(it) }
        }

        // Execute
        viewModel.loadUser("1")
        advanceUntilIdle()
        job.cancel()

        assertTrue(states.first() is UiState.Loading)
        assertTrue(states.any { it is UiState.Success })
    }

    @Test
    fun loadUser_error() = runTest {
        fakeRepository.shouldReturnError = true

        viewModel.loadUser("1")
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
    }
}
```

(Uses a test dispatcher rule to control `Dispatchers.Main`.)

### Full `Stack` Integration / E2E-style Test

```kotlin
@HiltAndroidTest
class FullStackIntegrationTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Inject
    lateinit var database: AppDatabase

    @Before
    fun setup() {
        hiltRule.inject()
        database.clearAllTables()
    }

    @Test
    fun completeUserFlow() {
        // 1. Start at empty state
        composeTestRule.onNodeWithText("No users").assertExists()

        // 2. Add user
        composeTestRule.onNodeWithTag("add_user_button").performClick()
        composeTestRule.onNodeWithTag("name_input").performTextInput("John")
        composeTestRule.onNodeWithTag("email_input").performTextInput("john@example.com")
        composeTestRule.onNodeWithTag("save_button").performClick()

        // 3. Verify user displayed
        composeTestRule.onNodeWithText("John").assertExists()
        composeTestRule.onNodeWithText("john@example.com").assertExists()

        // 4. Edit user
        composeTestRule.onNodeWithText("John").performClick()
        composeTestRule.onNodeWithTag("edit_button").performClick()
        composeTestRule.onNodeWithTag("name_input").performTextClearance()
        composeTestRule.onNodeWithTag("name_input").performTextInput("Jane")
        composeTestRule.onNodeWithTag("save_button").performClick()

        // 5. Verify update
        composeTestRule.onNodeWithText("Jane").assertExists()
        composeTestRule.onNodeWithText("John").assertDoesNotExist()

        // 6. Delete user
        composeTestRule.onNodeWithText("Jane").performClick()
        composeTestRule.onNodeWithTag("delete_button").performClick()
        composeTestRule.onNodeWithText("Confirm").performClick()

        // 7. Verify empty state
        composeTestRule.onNodeWithText("No users").assertExists()
    }
}
```

(This is a full-stack integration test within the app boundary, often also classified as an E2E UI test.)

### Best Practices

1. Use an in-memory database for faster, deterministic tests.
2. Mock or fake only external dependencies (network, file system, OS services, third-party SDKs).
3. Prefer realistic scenarios that go through multiple layers instead of overly synthetic ones.
4. Verify state changes and data flow through repositories, database, and ViewModels, not just single calls.
5. Clean up shared state between tests (e.g., clear database, reset fakes).
6. Cover error scenarios (network failures, parsing errors, database errors) and fallback behavior.
7. Balance coverage with speed: keep most logic at unit-test level and reserve integration tests for critical flows.

---

## Follow-ups

- [[q-android-manifest-file--android--easy]]

## References

- [Instrumented Tests](https://developer.android.com/training/testing/instrumented-tests)

## Related Questions

### Prerequisites / Concepts

- [[c-testing]]

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--android--medium]] - Testing
- [[q-screenshot-snapshot-testing--android--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing
