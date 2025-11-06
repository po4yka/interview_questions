---
id: android-457
title: Fakes Vs Mocks Testing / Fakes против Mocks Тестирование
aliases: [Fakes Vs Mocks Testing, Fakes против Mocks Тестирование, Test Doubles, Тестовые дублёры]
topic: android
subtopics:
  - testing-instrumented
  - testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-dependency-injection
sources:
  - https://developer.android.com/training/testing/unit-testing/local-unit-tests
created: 2025-10-20
updated: 2025-11-03
tags: [android/testing-instrumented, android/testing-unit, difficulty/medium, fakes, mocks, test-doubles]
---

# Вопрос (RU)
> Объясните разницу между fakes, mocks и stubs. Когда следует использовать каждый?

# Question (EN)
> Explain the difference between fakes, mocks, and stubs. When should you use each?

---

## Ответ (RU)

**Test doubles** — объекты, заменяющие реальные зависимости в тестах. Основные типы: **`Stub`**, **`Mock`**, **`Fake`**, **`Spy`**.

### Основные Типы

**1. `Stub` — предопределённые ответы**
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

**2. `Mock` — проверка взаимодействий**
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
    coVerify(exactly = 1) { repository.getUser(1) }
}
```

**3. `Fake` — рабочая реализация**
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

**4. `Spy` — частичная замена**
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

### Когда Использовать

| Type | Use Case | Verification |
|------|----------|-------------|
| **`Stub`** | Простые unit-тесты | State |
| **`Mock`** | Проверка взаимодействий | Behavior |
| **`Fake`** | Интеграционные тесты | State |
| **`Spy`** | Отладка, частичная замена | Behavior |

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

### Лучшие Практики

- Предпочитайте `Fake` вместо `Mock` для интеграционных тестов
- Используйте `Stub` для простых unit-тестов с предопределёнными ответами
- Один assertion на тест для фокусировки
- Test Pyramid: 70% unit (stubs/mocks), 20% integration (fakes), 10% E2E (real)

### Типичные Ошибки

- Over-mocking: избыточное использование `Mock` ведет к хрупким тестам
- Отсутствие очистки состояния между тестами в `Fake`
- Проверка внутренней реализации вместо поведения
- Использование `Spy` может маскировать баги в реальной логике

---

## Answer (EN)

**Test doubles** replace real dependencies in tests. Main types: **`Stub`**, **`Mock`**, **`Fake`**, **`Spy`**.

### Key Types

**1. `Stub` — predefined responses**
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

**2. `Mock` — interaction verification**
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
    coVerify(exactly = 1) { repository.getUser(1) }
}
```

**3. `Fake` — working implementation**
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

**4. `Spy` — partial replacement**
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
| **`Stub`** | Simple unit tests | State |
| **`Mock`** | Interaction verification | Behavior |
| **`Fake`** | Integration tests | State |
| **`Spy`** | Debugging, partial replacement | Behavior |

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

- Prefer `Fake` over `Mock` for integration tests
- Use `Stub` for simple unit tests with predefined responses
- One assertion per test for focus
- Test Pyramid: 70% unit (stubs/mocks), 20% integration (fakes), 10% E2E (real)

### Common Pitfalls

- Over-mocking: excessive `Mock` usage leads to brittle tests
- Missing state cleanup between tests in `Fake`
- Verifying implementation details instead of behavior
- Using `Spy` can mask bugs in real logic

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

### Related (Same Level)

### Advanced
- [[q-espresso-advanced-patterns--android--medium]]
