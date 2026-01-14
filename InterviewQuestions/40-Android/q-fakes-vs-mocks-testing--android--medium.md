---
id: android-457
title: Fakes Vs Mocks Testing / Fakes против Mocks Тестирование
aliases:
- Fakes Vs Mocks Testing
- Fakes против Mocks Тестирование
- Test Doubles
- Тестовые дублёры
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
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-accessibility-testing--android--medium
- q-kmm-testing--android--medium
- q-unit-testing-coroutines-flow--android--medium
sources:
- https://developer.android.com/training/testing/unit-testing/local-unit-tests
anki_cards:
- slug: android-457-0-en
  language: en
  anki_id: 1768366958231
  synced_at: '2026-01-14T09:17:53.487803'
- slug: android-457-0-ru
  language: ru
  anki_id: 1768366958256
  synced_at: '2026-01-14T09:17:53.490919'
created: 2025-10-20
updated: 2025-11-03
tags:
- android/testing-instrumented
- android/testing-unit
- difficulty/medium
- fakes
- mocks
- test-doubles
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
- Возвращает жёстко заданные или заранее сконфигурированные значения
- Используется для тестов с проверкой результата через состояние (state-based verification)
- Сам по себе не проверяет взаимодействия (но код теста может косвенно учитывать, был ли вызван stub)

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

    assertEquals("Stub User", viewModel.userName.value) // State-based verification
}
```

**2. `Mock` — проверка взаимодействий**
- Записывает/эмулирует вызовы методов
- Для behavior verification (проверка того, КАК взаимодействуют объекты)
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
- Упрощённая, но функциональная реализация интерфейса
- Полезен для интеграционных и более реалистичных unit-тестов
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

    assertEquals("John", viewModel.userName.value) // Близко к end-to-end сценарию
}
```

**4. `Spy` — частичная замена + проверка взаимодействий**
- Основан на реальном объекте (частичная или полная реальная логика)
- Позволяет отслеживать вызовы и параметры (behavior verification), сохраняя поведение реальной реализации
- Может использоваться и для логирования/отладки, но основная задача — проверка взаимодействий с реальным объектом

```kotlin
// ✅ Spy для частичной замены и проверки взаимодействий
class UserRepositorySpy(private val real: UserRepository) : UserRepository {
    var getUserCallCount = 0

    override suspend fun getUser(id: Int): User {
        getUserCallCount++
        return real.getUser(id) // Делегирование + отслеживание
    }

    override suspend fun saveUser(user: User): Boolean = real.saveUser(user)
}
```

### Когда Использовать

| Type | Use Case | Verification |
|------|----------|-------------|
| **`Stub`** | Простые unit-тесты с предсказуемыми ответами | State |
| **`Mock`** | Проверка взаимодействий и контрактов | Behavior |
| **`Fake`** | Более реалистичные unit-/интеграционные тесты | State |
| **`Spy`** | Частичная замена и проверка вызовов реальной логики | Behavior |

**Stub:**
- ✅ Быстрые unit-тесты
- ✅ Предсказуемые ответы
- ❌ Не выполняет явной проверки взаимодействий

**Mock:**
- ✅ Проверка вызовов методов
- ✅ Контроль параметров
- ❌ Хрупкие тесты при чрезмерном использовании

**Fake:**
- ✅ Реалистичное поведение
- ✅ Подходит для интеграционных и более широких сценариев
- ❌ Требует больше кода и поддержки

**Spy:**
- ✅ Реальная логика + отслеживание
- ✅ Частичная замена
- ❌ Может маскировать баги и усложнять тесты при неосторожном использовании

### Лучшие Практики

- Предпочитайте `Fake` вместо «глубоких» `Mock` для интеграционных и более широких сценариев
- Используйте `Stub` для простых unit-тестов с предопределёнными ответами
- Ориентируйтесь на один сценарий/поведение на тест; несколько assert допустимы, если проверяют один логический кейс
- Рассматривайте Test Pyramid как ориентир: большинство тестов — быстрые unit (часто с stubs/fakes/mocks), меньше — интеграционных (часто с fakes/инфраструктурой), ещё меньше — E2E

### Типичные Ошибки

- Over-mocking: избыточное использование `Mock` ведёт к хрупким тестам
- Отсутствие очистки состояния между тестами в `Fake`
- Проверка внутренней реализации вместо наблюдаемого поведения
- Неразборчивое использование `Spy`, из-за чего тесты становятся сложными и скрывают реальные проблемы

---

## Answer (EN)

**Test doubles** replace real dependencies in tests. Main types: **`Stub`**, **`Mock`**, **`Fake`**, **`Spy`**.

### Key Types

**1. `Stub` — predefined responses**
- Returns hard-coded or preconfigured values
- Used for tests with state-based verification of outcomes
- Does not itself assert on interactions (though the test code may indirectly rely on it being called)

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

    assertEquals("Stub User", viewModel.userName.value) // State-based verification
}
```

**2. `Mock` — interaction verification**
- Records/emulates method calls
- For behavior verification (how collaborators are used)
- Verifies parameters and call counts

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
- Simplified but functional implementation of the interface
- Useful for integration tests and more realistic unit tests
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

    assertEquals("John", viewModel.userName.value) // Close to an end-to-end scenario
}
```

**4. `Spy` — partial replacement + interaction verification**
- Wraps a real object (partial or full real implementation)
- Tracks calls and parameters (behavior verification) while delegating to real logic
- Can be used for logging/debugging, but primary purpose is verifying interactions with a real implementation

```kotlin
// ✅ Spy for partial replacement and interaction verification
class UserRepositorySpy(private val real: UserRepository) : UserRepository {
    var getUserCallCount = 0

    override suspend fun getUser(id: Int): User {
        getUserCallCount++
        return real.getUser(id) // Delegation + tracking
    }

    override suspend fun saveUser(user: User): Boolean = real.saveUser(user)
}
```

### When to Use

| Type | Use Case | Verification |
|------|----------|-------------|
| **`Stub`** | Simple unit tests with predictable responses | State |
| **`Mock`** | Verifying interactions and contracts | Behavior |
| **`Fake`** | More realistic unit/integration tests | State |
| **`Spy`** | Partial replacement + verifying calls to real logic | Behavior |

**Stub:**
- ✅ Fast unit tests
- ✅ Predictable responses
- ❌ No explicit interaction verification

**Mock:**
- ✅ Method call verification
- ✅ Parameter control
- ❌ Brittle tests when overused

**Fake:**
- ✅ Realistic behavior
- ✅ Good for integration and broader scenarios
- ❌ Requires more code and maintenance

**Spy:**
- ✅ Real logic + tracking
- ✅ Partial replacement
- ❌ Can mask bugs / add complexity if misused

### Best Practices

- Prefer `Fake` over deeply nested `Mock` setups for integration-like scenarios
- Use `Stub` for simple unit tests with predefined responses
- Aim for one behavior/scenario per test; multiple assertions are fine when they validate a single logical outcome
- Treat the Test Pyramid as guidance: majority fast unit tests (often with stubs/fakes/mocks), fewer integration tests (often with fakes/real infra), and even fewer full end-to-end tests

### Common Pitfalls

- Over-mocking: excessive `Mock` usage leads to brittle tests
- Missing state cleanup between tests when using `Fake`
- Verifying internal implementation instead of observable behavior
- Using `Spy` without clear purpose, making tests complex and hiding real issues

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
