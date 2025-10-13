---
tags:
  - testing
  - fakes
  - mocks
  - test-doubles
  - architecture
  - stubs
  - testing-strategy
difficulty: medium
status: draft
---

# Fakes vs Mocks vs Stubs

# Question (EN)
> Explain the difference between fakes, mocks, and stubs. When should you use each? Implement a fake repository.

# Вопрос (RU)
> Объясните разницу между fakes, mocks и stubs. Когда следует использовать каждый? Реализуйте fake repository.

---

## Answer (EN)

**Test doubles** are objects that replace real dependencies in tests. There are different types: **Fakes**, **Mocks**, **Stubs**, **Spies**, and **Dummies**, each serving specific purposes.

---

### Definitions

**Stub:** Returns pre-configured responses. No behavior verification.

**Mock:** Records interactions and verifies they happened correctly.

**Fake:** Has working implementation, but simplified for testing.

**Spy:** Real object with ability to verify interactions.

**Dummy:** Placeholder passed around but never used.

---

### Stubs

**Purpose:** Provide pre-defined answers to calls.

```kotlin
// Interface
interface UserRepository {
    suspend fun getUser(id: Int): User
    suspend fun saveUser(user: User): Boolean
}

// Stub implementation
class UserRepositoryStub : UserRepository {
    override suspend fun getUser(id: Int): User {
        // Always returns same user
        return User(id, "Stub User")
    }

    override suspend fun saveUser(user: User): Boolean {
        // Always succeeds
        return true
    }
}

// Usage
@Test
fun testWithStub() = runTest {
    val repository = UserRepositoryStub()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // Verify state, not repository interactions
    assertEquals("Stub User", viewModel.userName.value)
}
```

**When to use:**
- Need simple predetermined responses
- Don't care about verification
- Testing state changes, not behavior

---

### Mocks

**Purpose:** Verify interactions happened correctly.

```kotlin
@Test
fun testWithMock() = runTest {
    val repository = mockk<UserRepository>()

    // Configure mock
    coEvery { repository.getUser(1) } returns User(1, "John")

    val viewModel = UserViewModel(repository)
    viewModel.loadUser(1)

    // Verify interaction
    coVerify(exactly = 1) { repository.getUser(1) }

    // Also verify state
    assertEquals("John", viewModel.userName.value)
}
```

**When to use:**
- Need to verify specific interactions
- Testing that collaborations happen correctly
- Complex interaction patterns

---

### Fakes

**Purpose:** Real working implementation, simplified for testing.

**Fake Repository implementation:**

```kotlin
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<Int, User>()
    private var shouldFail = false

    override suspend fun getUser(id: Int): User {
        if (shouldFail) {
            throw IOException("Network error")
        }

        return users[id] ?: throw NoSuchElementException("User not found")
    }

    override suspend fun saveUser(user: User): Boolean {
        if (shouldFail) {
            throw IOException("Network error")
        }

        users[user.id] = user
        return true
    }

    override suspend fun deleteUser(id: Int): Boolean {
        if (shouldFail) {
            throw IOException("Network error")
        }

        return users.remove(id) != null
    }

    override suspend fun getAllUsers(): List<User> {
        if (shouldFail) {
            throw IOException("Network error")
        }

        return users.values.toList()
    }

    // Test helpers
    fun setUsers(vararg userList: User) {
        users.clear()
        userList.forEach { users[it.id] = it }
    }

    fun setShouldFail(fail: Boolean) {
        shouldFail = fail
    }

    fun getUserCount(): Int = users.size

    fun clear() {
        users.clear()
        shouldFail = false
    }
}
```

**Usage:**

```kotlin
class UserViewModelTest {
    private lateinit var fakeRepository: FakeUserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setUp() {
        fakeRepository = FakeUserRepository()
        viewModel = UserViewModel(fakeRepository)
    }

    @Test
    fun `loadUser with existing user shows data`() = runTest {
        // Arrange
        fakeRepository.setUsers(
            User(1, "John"),
            User(2, "Jane")
        )

        // Act
        viewModel.loadUser(1)

        // Assert
        val state = viewModel.uiState.value as UiState.Success
        assertEquals("John", state.user.name)
    }

    @Test
    fun `loadUser with non-existent user shows error`() = runTest {
        fakeRepository.setUsers() // Empty

        viewModel.loadUser(999)

        val state = viewModel.uiState.value as UiState.Error
        assertTrue(state.message.contains("not found"))
    }

    @Test
    fun `saveUser adds to repository`() = runTest {
        viewModel.saveUser(User(1, "John"))

        assertEquals(1, fakeRepository.getUserCount())

        val user = fakeRepository.getUser(1)
        assertEquals("John", user.name)
    }

    @Test
    fun `network error shows error state`() = runTest {
        fakeRepository.setShouldFail(true)

        viewModel.loadUser(1)

        val state = viewModel.uiState.value as UiState.Error
        assertTrue(state.message.contains("Network error"))
    }
}
```

**When to use:**
- Testing complex workflows
- Need realistic behavior
- Multiple tests use same setup
- Testing state mutations
- Integration tests

---

### Advanced Fake: In-Memory Database

```kotlin
class FakeDatabase {
    private val users = mutableMapOf<Int, User>()
    private val posts = mutableMapOf<Int, Post>()
    private var userIdCounter = 1
    private var postIdCounter = 1

    // User operations
    fun insertUser(user: User): Int {
        val id = userIdCounter++
        users[id] = user.copy(id = id)
        return id
    }

    fun getUser(id: Int): User? = users[id]

    fun getAllUsers(): List<User> = users.values.toList()

    fun updateUser(user: User): Boolean {
        if (!users.containsKey(user.id)) return false
        users[user.id] = user
        return true
    }

    fun deleteUser(id: Int): Boolean {
        posts.values.removeIf { it.userId == id }
        return users.remove(id) != null
    }

    // Post operations
    fun insertPost(post: Post): Int {
        val id = postIdCounter++
        posts[id] = post.copy(id = id)
        return id
    }

    fun getPostsByUser(userId: Int): List<Post> {
        return posts.values.filter { it.userId == userId }
    }

    fun deletePost(id: Int): Boolean {
        return posts.remove(id) != null
    }

    // Test helpers
    fun clear() {
        users.clear()
        posts.clear()
        userIdCounter = 1
        postIdCounter = 1
    }
}

class FakeUserRepository(
    private val database: FakeDatabase
) : UserRepository {
    override suspend fun getUser(id: Int): User {
        return database.getUser(id) ?: throw NoSuchElementException()
    }

    override suspend fun saveUser(user: User): Boolean {
        return if (user.id == 0) {
            database.insertUser(user) > 0
        } else {
            database.updateUser(user)
        }
    }

    override suspend fun deleteUser(id: Int): Boolean {
        return database.deleteUser(id)
    }
}

class FakePostRepository(
    private val database: FakeDatabase
) : PostRepository {
    override suspend fun getPostsByUser(userId: Int): List<Post> {
        return database.getPostsByUser(userId)
    }

    override suspend fun savePost(post: Post): Boolean {
        return database.insertPost(post) > 0
    }
}

// Test with shared database
class UserWithPostsTest {
    private lateinit var database: FakeDatabase
    private lateinit var userRepository: FakeUserRepository
    private lateinit var postRepository: FakePostRepository

    @Before
    fun setUp() {
        database = FakeDatabase()
        userRepository = FakeUserRepository(database)
        postRepository = FakePostRepository(database)
    }

    @Test
    fun `deleteUser also deletes user posts`() = runTest {
        // Create user
        val userId = database.insertUser(User(0, "John"))

        // Create posts
        database.insertPost(Post(0, userId, "Post 1"))
        database.insertPost(Post(0, userId, "Post 2"))

        // Verify posts exist
        assertEquals(2, postRepository.getPostsByUser(userId).size)

        // Delete user
        userRepository.deleteUser(userId)

        // Posts should be deleted too
        assertEquals(0, postRepository.getPostsByUser(userId).size)
    }
}
```

---

### Comparison Table

| Type | Purpose | Verification | Complexity | Use Case |
|------|---------|--------------|------------|----------|
| **Stub** | Pre-configured responses | No | Low | Simple predetermined data |
| **Mock** | Verify interactions | Yes | Low | Behavior verification |
| **Fake** | Working implementation | No | High | Realistic behavior, integration tests |
| **Spy** | Real + verification | Yes | Medium | Partial mocking |

---

### When to Use What

**Use Stubs:**

```kotlin
//  Simple predetermined response
class TimeStub : TimeProvider {
    override fun currentTime() = 1234567890L
}
```

**Use Mocks:**

```kotlin
//  Verify specific interaction
@Test
fun `clicking save calls repository`() {
    val repository = mockk<UserRepository>(relaxed = true)
    val viewModel = UserViewModel(repository)

    viewModel.save(User(1, "John"))

    verify { repository.saveUser(any()) }
}
```

**Use Fakes:**

```kotlin
//  Complex behavior, multiple tests
class UserFlowTest {
    private val repository = FakeUserRepository()

    @Test
    fun `create, read, update, delete user`() = runTest {
        // Create
        repository.saveUser(User(1, "John"))

        // Read
        val user = repository.getUser(1)
        assertEquals("John", user.name)

        // Update
        repository.saveUser(user.copy(name = "Jane"))
        assertEquals("Jane", repository.getUser(1).name)

        // Delete
        repository.deleteUser(1)
        assertThrows<NoSuchElementException> {
            repository.getUser(1)
        }
    }
}
```

---

### Fake with Configurable Behavior

```kotlin
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<Int, User>()

    // Configurable behaviors
    var getUserDelay: Long = 0
    var getUserShouldThrow: Exception? = null
    var saveUserShouldFail: Boolean = false

    override suspend fun getUser(id: Int): User {
        getUserShouldThrow?.let { throw it }

        if (getUserDelay > 0) {
            delay(getUserDelay)
        }

        return users[id] ?: throw NoSuchElementException("User $id not found")
    }

    override suspend fun saveUser(user: User): Boolean {
        if (saveUserShouldFail) {
            throw IOException("Save failed")
        }

        users[user.id] = user
        return true
    }

    // Test configuration helpers
    fun simulateNetworkDelay(delayMs: Long) {
        getUserDelay = delayMs
    }

    fun simulateNetworkError() {
        getUserShouldThrow = IOException("Network error")
    }

    fun simulateSaveFailure() {
        saveUserShouldFail = true
    }

    fun reset() {
        users.clear()
        getUserDelay = 0
        getUserShouldThrow = null
        saveUserShouldFail = false
    }
}

// Usage
@Test
fun `loading with slow network shows loading state`() = runTest {
    fakeRepository.simulateNetworkDelay(2000)

    viewModel.loadUser(1)

    // Should be loading
    assertEquals(UiState.Loading, viewModel.uiState.value)

    advanceTimeBy(2000)

    // Should complete
    assertTrue(viewModel.uiState.value is UiState.Success)
}
```

---

### Best Practices

**1. Prefer fakes for complex dependencies:**

```kotlin
//  DO: Fake for stateful dependencies
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<Int, User>()
    // Full implementation
}

//  DON'T: Mock for complex state
val mock = mockk<UserRepository>()
every { mock.getUser(1) } returns user1
every { mock.getUser(2) } returns user2
// Lots of mocking code...
```

**2. Use mocks for external dependencies:**

```kotlin
//  DO: Mock external APIs
val api = mockk<ExternalApi>()
coEvery { api.fetchData() } returns data
```

**3. Fakes should be simple:**

```kotlin
//  DO: In-memory implementation
class FakeRepository {
    private val data = mutableMapOf<Int, Item>()
    // Simple CRUD
}

//  DON'T: Complex business logic in fake
class FakeRepository {
    // Complex validation, caching, threading...
    // This is basically a second implementation!
}
```

**4. Test your fakes:**

```kotlin
//  DO: Test the fake itself
class FakeUserRepositoryTest {
    @Test
    fun `save and retrieve user works`() {
        val fake = FakeUserRepository()
        val user = User(1, "John")

        fake.saveUser(user)

        assertEquals(user, fake.getUser(1))
    }
}
```

---

## Ответ (RU)

**Тестовые дублеры (Test doubles)** — это объекты, заменяющие реальные зависимости в тестах. Существуют разные типы: **Fakes**, **Mocks**, **Stubs**, **Spies** и **Dummies**, каждый служит определенным целям.

### Определения

**Stub:** Возвращает предварительно настроенные ответы. Нет верификации поведения.

**Mock:** Записывает взаимодействия и верифицирует их корректность.

**Fake:** Имеет рабочую реализацию, но упрощенную для тестирования.

**Spy:** Реальный объект с возможностью верификации взаимодействий.

**Dummy:** Placeholder, передаваемый, но никогда не используемый.

### Когда использовать

**Stubs:** Простые предопределенные данные, не нужна верификация.

**Mocks:** Верификация конкретных взаимодействий, тестирование поведения.

**Fakes:** Сложные workflow, нужно реалистичное поведение, интеграционные тесты, множество тестов используют одну настройку.

### Реализация Fake Repository

Fake содержит in-memory хранилище и полную реализацию CRUD операций с помощниками для настройки тестовых сценариев (ошибки, задержки и т.д.).

### Лучшие практики

1. Предпочитайте fakes для сложных зависимостей
2. Используйте mocks для внешних зависимостей
3. Fakes должны быть простыми
4. Тестируйте сами fakes

Правильный выбор тестового дублера упрощает тесты и делает их более поддерживаемыми.

---

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--testing--medium]] - Testing
- [[q-screenshot-snapshot-testing--testing--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--testing--hard]] - Testing
