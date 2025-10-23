---
id: 20251020-200600
title: Fakes Vs Mocks Testing / Fakes против Mocks Тестирование
aliases:
  - Fakes Vs Mocks Testing
  - Fakes против Mocks Тестирование
topic: android
subtopics:
  - testing-unit
  - testing-instrumented
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
source: https://developer.android.com/training/testing/unit-testing/local-unit-tests
source_note: Android unit testing documentation
status: reviewed
moc: moc-android
related:
  - q-android-testing-strategies--testing--medium
  - q-mockito-vs-mockk--testing--medium
  - q-testing-best-practices--testing--medium
created: 2025-10-20
updated: 2025-10-20
tags:
  - android/testing-unit
  - android/testing-instrumented
  - fakes
  - mocks
  - test-doubles
  - testing-strategy
  - difficulty/medium
---
# Вопрос (RU)
> Объясните разницу между fakes, mocks и stubs. Когда следует использовать каждый?

# Question (EN)
> Explain the difference between fakes, mocks, and stubs. When should you use each?

---

## Ответ (RU)

**Test doubles** - объекты, заменяющие реальные зависимости в тестах. Типы: **Fakes**, **Mocks**, **Stubs**, **Spies**, **Dummies** - каждый для конкретных целей.

### Основные типы

**1. Stub**
- Назначение: возвращает предопределенные ответы
- Использование: простые тесты без проверки взаимодействий
- Пример: всегда возвращает один пользователь

```kotlin
// Stub implementation
class UserRepositoryStub : UserRepository {
    override suspend fun getUser(id: Int): User {
        return User(id, "Stub User") // Всегда одинаковый ответ
    }

    override suspend fun saveUser(user: User): Boolean {
        return true // Всегда успех
    }
}

// Использование
@Test
fun testWithStub() = runTest {
    val repository = UserRepositoryStub()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // Проверяем состояние, не взаимодействия
    assertEquals("Stub User", viewModel.userName.value)
}
```

**2. Mock**
- Назначение: записывает взаимодействия и проверяет их
- Использование: проверка поведения, не состояния
- Пример: проверка вызовов методов

```kotlin
// Mock с MockK
@Test
fun testWithMock() = runTest {
    val repository = mockk<UserRepository>()

    // Настройка mock
    coEvery { repository.getUser(1) } returns User(1, "John")

    val viewModel = UserViewModel(repository)
    viewModel.loadUser(1)

    // Проверка взаимодействий
    coVerify { repository.getUser(1) }
    verify { repository.getUser(1) }
}
```

**3. Fake**
- Назначение: рабочая реализация, упрощенная для тестов
- Использование: интеграционные тесты, сложная логика
- Пример: in-memory база данных

```kotlin
// Fake implementation
class UserRepositoryFake : UserRepository {
    private val users = mutableMapOf<Int, User>()

    override suspend fun getUser(id: Int): User {
        return users[id] ?: throw UserNotFoundException()
    }

    override suspend fun saveUser(user: User): Boolean {
        users[user.id] = user
        return true
    }
}

// Использование
@Test
fun testWithFake() = runTest {
    val repository = UserRepositoryFake()
    val viewModel = UserViewModel(repository)

    // Сохраняем пользователя
    viewModel.saveUser(User(1, "John"))

    // Загружаем и проверяем
    viewModel.loadUser(1)
    assertEquals("John", viewModel.userName.value)
}
```

**4. Spy**
- Назначение: реальный объект с возможностью проверки взаимодействий
- Использование: частичная замена поведения
- Пример: логирование вызовов

```kotlin
// Spy implementation
class UserRepositorySpy(private val realRepository: UserRepository) : UserRepository {
    var getUserCallCount = 0
    var lastUserId: Int? = null

    override suspend fun getUser(id: Int): User {
        getUserCallCount++
        lastUserId = id
        return realRepository.getUser(id)
    }

    override suspend fun saveUser(user: User): Boolean {
        return realRepository.saveUser(user)
    }
}
```

### Теория Test Doubles

**Test Double Hierarchy:**
- **Dummy**: заглушка, никогда не используется
- **Stub**: возвращает предопределенные значения
- **Spy**: реальный объект + проверка взаимодействий
- **Mock**: проверяет взаимодействия, может возвращать значения
- **Fake**: рабочая реализация для тестов

**Принципы Test Doubles:**

**Изоляция (Isolation):**
- Test doubles изолируют тестируемый код от внешних зависимостей
- Предотвращают side effects между тестами
- Обеспечивают детерминированное поведение
- Позволяют тестировать код независимо от окружения

**Контроль (Control):**
- Полный контроль над поведением зависимостей
- Предсказуемые ответы на вызовы методов
- Возможность симуляции различных сценариев
- Тестирование edge cases и error conditions

**Наблюдаемость (Observability):**
- Возможность проверки взаимодействий с зависимостями
- Верификация вызовов методов и их параметров
- Отслеживание порядка операций
- Логирование для отладки тестов

**Теория Mocking:**

**Behavior Verification vs State Verification:**
- **Behavior Verification**: проверяет как объект взаимодействует с зависимостями
- **State Verification**: проверяет конечное состояние объекта
- Mocks используют behavior verification
- Fakes используют state verification
- Выбор зависит от того, что важнее: поведение или результат

**Interaction Testing:**
- Проверка вызовов методов с правильными параметрами
- Верификация количества вызовов
- Проверка порядка операций
- Тестирование callback'ов и event'ов

**Contract Testing:**
- Test doubles должны соблюдать контракт интерфейса
- Поведение должно быть совместимо с реальной реализацией
- Исключения должны соответствовать реальным
- Возвращаемые типы должны быть корректными

**Когда использовать:**

**Stub:**
- Простые тесты без проверки поведения
- Нужны предопределенные ответы
- Тестирование состояния, не взаимодействий
- Быстрые unit тесты без сложной логики

**Mock:**
- Проверка поведения и взаимодействий
- Тестирование вызовов методов
- Проверка параметров и количества вызовов
- Тестирование callback'ов и event handling

**Fake:**
- Интеграционные тесты
- Сложная бизнес-логика
- Нужна рабочая реализация
- Тестирование end-to-end сценариев

**Spy:**
- Частичная замена поведения
- Логирование и мониторинг
- Отладка тестов
- Тестирование с реальными объектами + проверка

**Теория Test Design:**

**Test Pyramid:**
- **Unit Tests (70%)**: быстрые, изолированные, используют mocks/stubs
- **Integration Tests (20%)**: тестируют взаимодействие компонентов, используют fakes
- **E2E Tests (10%)**: полные сценарии, используют реальные зависимости

**Dependency Injection Benefits:**
- Легкая замена зависимостей на test doubles
- Слабая связанность компонентов
- Тестируемость архитектуры
- Гибкость в конфигурации

**Test Doubles Lifecycle:**
- **Setup**: создание и конфигурация test doubles
- **Exercise**: выполнение тестируемого кода
- **Verify**: проверка результатов и взаимодействий
- **Teardown**: очистка ресурсов и состояния

**Best Practices:**
- Использовать fakes для интеграционных тестов
- Mocks для unit тестов поведения
- Stubs для простых тестов состояния
- Избегать over-mocking
- Предпочитать fakes над mocks когда возможно
- Один mock per test для простоты
- Использовать builder pattern для сложных test doubles

### Реализация Fake Repository

**Полный пример:**
```kotlin
class UserRepositoryFake : UserRepository {
    private val users = mutableMapOf<Int, User>()
    private val saveHistory = mutableListOf<User>()

    override suspend fun getUser(id: Int): User {
        return users[id] ?: throw UserNotFoundException("User $id not found")
    }

    override suspend fun saveUser(user: User): Boolean {
        users[user.id] = user
        saveHistory.add(user)
        return true
    }

    // Дополнительные методы для тестов
    fun getAllUsers(): List<User> = users.values.toList()
    fun getSaveHistory(): List<User> = saveHistory.toList()
    fun clear() {
        users.clear()
        saveHistory.clear()
    }
}
```

## Answer (EN)

**Test doubles** are objects that replace real dependencies in tests. Types: **Fakes**, **Mocks**, **Stubs**, **Spies**, **Dummies** - each for specific purposes.

### Key Types

**1. Stub**
- Purpose: returns predefined responses
- Usage: simple tests without interaction verification
- Example: always returns same user

```kotlin
// Stub implementation
class UserRepositoryStub : UserRepository {
    override suspend fun getUser(id: Int): User {
        return User(id, "Stub User") // Always same response
    }

    override suspend fun saveUser(user: User): Boolean {
        return true // Always success
    }
}

// Usage
@Test
fun testWithStub() = runTest {
    val repository = UserRepositoryStub()
    val viewModel = UserViewModel(repository)

    viewModel.loadUser(1)

    // Check state, not interactions
    assertEquals("Stub User", viewModel.userName.value)
}
```

**2. Mock**
- Purpose: records interactions and verifies them
- Usage: behavior verification, not state
- Example: method call verification

```kotlin
// Mock with MockK
@Test
fun testWithMock() = runTest {
    val repository = mockk<UserRepository>()

    // Configure mock
    coEvery { repository.getUser(1) } returns User(1, "John")

    val viewModel = UserViewModel(repository)
    viewModel.loadUser(1)

    // Verify interactions
    coVerify { repository.getUser(1) }
    verify { repository.getUser(1) }
}
```

**3. Fake**
- Purpose: working implementation, simplified for tests
- Usage: integration tests, complex logic
- Example: in-memory database

```kotlin
// Fake implementation
class UserRepositoryFake : UserRepository {
    private val users = mutableMapOf<Int, User>()

    override suspend fun getUser(id: Int): User {
        return users[id] ?: throw UserNotFoundException()
    }

    override suspend fun saveUser(user: User): Boolean {
        users[user.id] = user
        return true
    }
}

// Usage
@Test
fun testWithFake() = runTest {
    val repository = UserRepositoryFake()
    val viewModel = UserViewModel(repository)

    // Save user
    viewModel.saveUser(User(1, "John"))

    // Load and verify
    viewModel.loadUser(1)
    assertEquals("John", viewModel.userName.value)
}
```

**4. Spy**
- Purpose: real object with interaction verification capability
- Usage: partial behavior replacement
- Example: call logging

```kotlin
// Spy implementation
class UserRepositorySpy(private val realRepository: UserRepository) : UserRepository {
    var getUserCallCount = 0
    var lastUserId: Int? = null

    override suspend fun getUser(id: Int): User {
        getUserCallCount++
        lastUserId = id
        return realRepository.getUser(id)
    }

    override suspend fun saveUser(user: User): Boolean {
        return realRepository.saveUser(user)
    }
}
```

### Test Doubles Theory

**Test Double Hierarchy:**
- **Dummy**: placeholder, never used
- **Stub**: returns predefined values
- **Spy**: real object + interaction verification
- **Mock**: verifies interactions, can return values
- **Fake**: working implementation for tests

**Test Doubles Principles:**

**Isolation:**
- Test doubles isolate code under test from external dependencies
- Prevent side effects between tests
- Ensure deterministic behavior
- Allow testing code independently of environment

**Control:**
- Full control over dependency behavior
- Predictable responses to method calls
- Ability to simulate various scenarios
- Testing edge cases and error conditions

**Observability:**
- Ability to verify interactions with dependencies
- Verification of method calls and their parameters
- Tracking operation order
- Logging for test debugging

**Mocking Theory:**

**Behavior Verification vs State Verification:**
- **Behavior Verification**: checks how object interacts with dependencies
- **State Verification**: checks final state of object
- Mocks use behavior verification
- Fakes use state verification
- Choice depends on what's more important: behavior or result

**Interaction Testing:**
- Verification of method calls with correct parameters
- Verification of call counts
- Checking operation order
- Testing callbacks and events

**Contract Testing:**
- Test doubles must follow interface contract
- Behavior must be compatible with real implementation
- Exceptions must match real ones
- Return types must be correct

**When to use:**

**Stub:**
- Simple tests without behavior verification
- Need predefined responses
- Testing state, not interactions
- Fast unit tests without complex logic

**Mock:**
- Behavior and interaction verification
- Testing method calls
- Verifying parameters and call counts
- Testing callbacks and event handling

**Fake:**
- Integration tests
- Complex business logic
- Need working implementation
- Testing end-to-end scenarios

**Spy:**
- Partial behavior replacement
- Logging and monitoring
- Test debugging
- Testing with real objects + verification

**Test Design Theory:**

**Test Pyramid:**
- **Unit Tests (70%)**: fast, isolated, use mocks/stubs
- **Integration Tests (20%)**: test component interaction, use fakes
- **E2E Tests (10%)**: full scenarios, use real dependencies

**Dependency Injection Benefits:**
- Easy replacement of dependencies with test doubles
- Loose coupling of components
- Testable architecture
- Flexibility in configuration

**Test Doubles Lifecycle:**
- **Setup**: creation and configuration of test doubles
- **Exercise**: execution of code under test
- **Verify**: verification of results and interactions
- **Teardown**: cleanup of resources and state

**Best Practices:**
- Use fakes for integration tests
- Mocks for unit behavior tests
- Stubs for simple state tests
- Avoid over-mocking
- Prefer fakes over mocks when possible
- One mock per test for simplicity
- Use builder pattern for complex test doubles

### Fake Repository Implementation

**Complete example:**
```kotlin
class UserRepositoryFake : UserRepository {
    private val users = mutableMapOf<Int, User>()
    private val saveHistory = mutableListOf<User>()

    override suspend fun getUser(id: Int): User {
        return users[id] ?: throw UserNotFoundException("User $id not found")
    }

    override suspend fun saveUser(user: User): Boolean {
        users[user.id] = user
        saveHistory.add(user)
        return true
    }

    // Additional methods for tests
    fun getAllUsers(): List<User> = users.values.toList()
    fun getSaveHistory(): List<User> = saveHistory.toList()
    fun clear() {
        users.clear()
        saveHistory.clear()
    }
}
```

## Follow-ups
- What's the difference between MockK and Mockito?
- How to test coroutines with test doubles?
- When to use dependency injection in tests?

## Related Questions
- [[q-espresso-advanced-patterns--testing--medium]]
