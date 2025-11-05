---
id: android-120
title: "Integration Testing Strategies / Стратегии интеграционного тестирования"
aliases: [Integration Testing Strategies, Стратегии интеграционного тестирования]
topic: android
subtopics: [testing-instrumented]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-manifest-file--android--easy, q-koin-vs-hilt-comparison--dependency-injection--medium, q-react-native-comparison--multiplatform--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/testing-instrumented, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, November 1st 2025, 5:43:34 pm
---

# Integration Testing Strategies

**English**: Design integration testing strategy. Test ViewModel + Repository + Database layers. Mock external dependencies.

**Russian**: Разработайте стратегию интеграционного тестирования. Тестируйте слои ViewModel + Repository + Database. Мокируйте внешние зависимости.

## Answer (EN)

Integration tests verify that multiple components work together correctly. They test the interaction between layers while mocking external dependencies like network and system services.

### Integration Test Pyramid

```
    E2E Tests (UI)
        ↑
Integration Tests (Multiple Layers)
        ↑
  Unit Tests (Single Components)
```

### Testing Strategy

**1. ViewModel + Repository + Local Database**
- Mock: Network API
- Real: ViewModel, Repository, Room Database

**2. Repository + Network + Cache**
- Mock: Nothing (use test server or fake)
- Real: All repository logic

**3. Full Stack (except external services)**
- Mock: Only external APIs, system services
- Real: All app layers

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
        // Use in-memory database
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
        // Setup
        fakeApiService.users["1"] = User("1", "John", "john@example.com")

        // First fetch - from network
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
        // Setup initial user
        val user = User("1", "John", "john@example.com")
        userDao.insert(user)

        // Update
        val updated = user.copy(name = "Jane")
        repository.updateUser(updated)

        // Verify database updated
        val fromDb = userDao.getUser("1")
        assertEquals("Jane", fromDb?.name)

        // Verify network called
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

        delay(100)

        // Update user
        val updated = user.copy(name = "Jane")
        userDao.update(updated)

        delay(100)

        job.cancel()

        assertTrue(values.any { it.name == "John" })
        assertTrue(values.any { it.name == "Jane" })
    }
}
```

### ViewModel + Repository Integration

```kotlin
@ExperimentalCoroutinesTest
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

        // Execute
        viewModel.loadUser("1")

        // Verify state progression
        val states = mutableListOf<UiState>()
        val job = launch {
            viewModel.uiState.collect { states.add(it) }
        }

        advanceUntilIdle()
        job.cancel()

        assertTrue(states.contains(UiState.Loading))
        assertTrue(states.any { it is UiState.Success })
    }

    @Test
    fun loadUser_error() = runTest {
        fakeRepository.shouldReturnError = true

        viewModel.loadUser("1")

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
    }
}
```

### Full Stack Integration Test

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

### Best Practices

1. **Use in-memory database** for faster tests
2. **Mock only external dependencies** (network, file system)
3. **Test realistic scenarios** end-to-end
4. **Verify state changes** through multiple layers
5. **Clean up between tests** (clear database)
6. **Test error scenarios** (network failures, database errors)
7. **Balance coverage with speed** - don't test everything at integration level

## Ответ (RU)

Интеграционные тесты проверяют, что несколько компонентов корректно работают вместе. Они тестируют взаимодействие между слоями, используя моки для внешних зависимостей, таких как сеть и системные сервисы.


### Стратегия Тестирования

1. **ViewModel + Repository + Local Database**: мокируем только сеть
2. **Repository + Network + Cache**: мокируем минимум
3. **Full Stack**: мокируем только внешние сервисы

[Полные примеры приведены в английском разделе]

### Лучшие Практики

1. **Используйте in-memory database**
2. **Мокируйте только внешние зависимости**
3. **Тестируйте реалистичные сценарии**
4. **Проверяйте изменения состояния** через несколько слоев
5. **Очищайте между тестами**
6. **Тестируйте error сценарии**
7. **Балансируйте покрытие и скорость**

---


## Follow-ups

- [[q-android-manifest-file--android--easy]]
- [[q-koin-vs-hilt-comparison--dependency-injection--medium]]
- [[q-react-native-comparison--multiplatform--medium]]


## References

- [Instrumented Tests](https://developer.android.com/training/testing/instrumented-tests)


## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--android--medium]] - Testing
- [[q-screenshot-snapshot-testing--android--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing
