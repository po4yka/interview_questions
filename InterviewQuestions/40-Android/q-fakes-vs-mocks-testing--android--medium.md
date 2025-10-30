---
id: 20251020-200600
title: Fakes Vs Mocks Testing / Fakes против Mocks Тестирование
aliases: [Fakes Vs Mocks Testing, Fakes против Mocks Тестирование, Test Doubles, Тестовые дублёры]
topic: android
subtopics: [testing-unit, testing-instrumented]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-testing-strategies--android--medium, q-mockito-vs-mockk--testing--medium, c-dependency-injection]
sources:
  - https://developer.android.com/training/testing/unit-testing/local-unit-tests
created: 2025-10-20
updated: 2025-10-28
tags: [android/testing-unit, android/testing-instrumented, difficulty/medium, fakes, mocks, test-doubles]
date created: Tuesday, October 28th 2025, 9:22:36 am
date modified: Thursday, October 30th 2025, 12:47:46 pm
---

# Вопрос (RU)
> Объясните разницу между fakes, mocks и stubs. Когда следует использовать каждый?

# Question (EN)
> Explain the difference between fakes, mocks, and stubs. When should you use each?

---

## Ответ (RU)

**Test doubles** — объекты, заменяющие реальные зависимости в тестах. Основные типы: **Stub**, **Mock**, **Fake**, **Spy**.

### Основные типы

**1. Stub — предопределённые ответы**
- Возвращает жёстко заданные значения
- Для тестов без проверки взаимодействий
- State verification

```kotlin
// ✅ Stub для простых тестов
class UserRepositoryStub : UserRepository {
    override suspend fun getUser(id: Int): User {
        return User(id, "Stub User") // Фиксированный ответ
    }
}

@Test
fun `load user updates UI`() = runTest {
    val viewModel = UserViewModel(UserRepositoryStub())
    viewModel.loadUser(1)

    assertEquals("Stub User", viewModel.userName.value) // State verification
}
```

**2. Mock — проверка взаимодействий**
- Записывает вызовы методов
- Для behavior verification
- Проверяет параметры и количество вызовов

```kotlin
// ✅ Mock для проверки поведения
@Test
fun `load user calls repository`() = runTest {
    val repository = mockk<UserRepository>()
    coEvery { repository.getUser(1) } returns User(1, "John")

    val viewModel = UserViewModel(repository)
    viewModel.loadUser(1)

    coVerify(exactly = 1) { repository.getUser(1) } // Behavior verification
}
```

**3. Fake — рабочая реализация**
- Упрощённая, но полнофункциональная реализация
- Для интеграционных тестов
- Сохраняет состояние между вызовами

```kotlin
// ✅ Fake с реальной логикой
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

@Test
fun `save and load user workflow`() = runTest {
    val repository = UserRepositoryFake()
    val viewModel = UserViewModel(repository)

    viewModel.saveUser(User(1, "John"))
    viewModel.loadUser(1)

    assertEquals("John", viewModel.userName.value) // End-to-end scenario
}
```

**4. Spy — частичная замена**
- Реальный объект + отслеживание вызовов
- Для логирования и отладки

```kotlin
// ✅ Spy для частичной замены
class UserRepositorySpy(private val real: UserRepository) : UserRepository {
    var callCount = 0

    override suspend fun getUser(id: Int): User {
        callCount++
        return real.getUser(id) // Делегирование + логирование
    }

    override suspend fun saveUser(user: User) = real.saveUser(user)
}
```

### Когда использовать

| Type | Use Case | Verification |
|------|----------|-------------|
| **Stub** | Простые unit-тесты | State |
| **Mock** | Проверка взаимодействий | Behavior |
| **Fake** | Интеграционные тесты | State |
| **Spy** | Отладка, частичная замена | Behavior |

**Stub:**
- ✅ Быстрые unit-тесты
- ✅ Предсказуемые ответы
- ❌ Не проверяет взаимодействия

**Mock:**
- ✅ Проверка вызовов методов
- ✅ Контроль параметров
- ❌ Хрупкие тесты при overuse

**Fake:**
- ✅ Реалистичное поведение
- ✅ Интеграционные тесты
- ❌ Требует больше кода

**Spy:**
- ✅ Реальная логика + логирование
- ✅ Частичная замена
- ❌ Может маскировать баги

### Best Practices

**1. Prefer Fakes over Mocks**
```kotlin
// ❌ Over-mocking
val mock = mockk<Database>()
every { mock.query() } returns list
every { mock.insert() } just Runs

// ✅ Fake with real logic
val fake = InMemoryDatabase() // Реальная работающая реализация
```

**2. One Assertion Per Test**
```kotlin
// ✅ Focused test
@Test
fun `repository throws on missing user`() = runTest {
    val repository = UserRepositoryFake()

    assertThrows<UserNotFoundException> {
        repository.getUser(999)
    }
}
```

**3. Use Test Pyramid**
- 70% unit tests → stubs/mocks
- 20% integration tests → fakes
- 10% E2E tests → real dependencies

---

## Answer (EN)

**Test doubles** replace real dependencies in tests. Main types: **Stub**, **Mock**, **Fake**, **Spy**.

### Key Types

**1. Stub — predefined responses**
- Returns hard-coded values
- For tests without interaction verification
- State verification

```kotlin
// ✅ Stub for simple tests
class UserRepositoryStub : UserRepository {
    override suspend fun getUser(id: Int): User {
        return User(id, "Stub User") // Fixed response
    }
}

@Test
fun `load user updates UI`() = runTest {
    val viewModel = UserViewModel(UserRepositoryStub())
    viewModel.loadUser(1)

    assertEquals("Stub User", viewModel.userName.value) // State verification
}
```

**2. Mock — interaction verification**
- Records method calls
- For behavior verification
- Checks parameters and call counts

```kotlin
// ✅ Mock for behavior verification
@Test
fun `load user calls repository`() = runTest {
    val repository = mockk<UserRepository>()
    coEvery { repository.getUser(1) } returns User(1, "John")

    val viewModel = UserViewModel(repository)
    viewModel.loadUser(1)

    coVerify(exactly = 1) { repository.getUser(1) } // Behavior verification
}
```

**3. Fake — working implementation**
- Simplified but fully functional implementation
- For integration tests
- Maintains state between calls

```kotlin
// ✅ Fake with real logic
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

@Test
fun `save and load user workflow`() = runTest {
    val repository = UserRepositoryFake()
    val viewModel = UserViewModel(repository)

    viewModel.saveUser(User(1, "John"))
    viewModel.loadUser(1)

    assertEquals("John", viewModel.userName.value) // End-to-end scenario
}
```

**4. Spy — partial replacement**
- Real object + call tracking
- For logging and debugging

```kotlin
// ✅ Spy for partial replacement
class UserRepositorySpy(private val real: UserRepository) : UserRepository {
    var callCount = 0

    override suspend fun getUser(id: Int): User {
        callCount++
        return real.getUser(id) // Delegation + logging
    }

    override suspend fun saveUser(user: User) = real.saveUser(user)
}
```

### When to Use

| Type | Use Case | Verification |
|------|----------|-------------|
| **Stub** | Simple unit tests | State |
| **Mock** | Interaction verification | Behavior |
| **Fake** | Integration tests | State |
| **Spy** | Debugging, partial replacement | Behavior |

**Stub:**
- ✅ Fast unit tests
- ✅ Predictable responses
- ❌ No interaction verification

**Mock:**
- ✅ Method call verification
- ✅ Parameter control
- ❌ Brittle tests when overused

**Fake:**
- ✅ Realistic behavior
- ✅ Integration tests
- ❌ Requires more code

**Spy:**
- ✅ Real logic + logging
- ✅ Partial replacement
- ❌ Can mask bugs

### Best Practices

**1. Prefer Fakes over Mocks**
```kotlin
// ❌ Over-mocking
val mock = mockk<Database>()
every { mock.query() } returns list
every { mock.insert() } just Runs

// ✅ Fake with real logic
val fake = InMemoryDatabase() // Real working implementation
```

**2. One Assertion Per Test**
```kotlin
// ✅ Focused test
@Test
fun `repository throws on missing user`() = runTest {
    val repository = UserRepositoryFake()

    assertThrows<UserNotFoundException> {
        repository.getUser(999)
    }
}
```

**3. Use Test Pyramid**
- 70% unit tests → stubs/mocks
- 20% integration tests → fakes
- 10% E2E tests → real dependencies

---

## Follow-ups

- How to avoid over-mocking in tests?
- When to write custom Fakes vs using in-memory implementations?
- How to test coroutines with test doubles?
- What is behavior vs state verification?

## References

- [[c-dependency-injection]]
- [[c-unit-testing]]
- https://developer.android.com/training/testing/unit-testing/local-unit-tests

## Related Questions

### Prerequisites
- [[q-android-testing-strategies--android--medium]]

### Related (Same Level)
- [[q-mockito-vs-mockk--testing--medium]]
- [[q-testing-best-practices--testing--medium]]

### Advanced
- [[q-espresso-advanced-patterns--android--medium]]
