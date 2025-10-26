---
id: "20251025-110311"
title: "Unit Testing / Модульное Тестирование"
aliases: ["Unit Testing", "Unit Tests", "Модульное Тестирование", "Юнит-Тесты", "JUnit"]
summary: "Testing individual units of code in isolation to ensure correctness"
topic: "testing"
subtopics: ["junit", "quality-assurance", "tdd"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-testing"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["concept", "testing", "junit", "quality-assurance", "tdd"]
---

# Unit Testing / Модульное Тестирование

## Summary (EN)

Unit testing is the practice of testing individual units or components of software in isolation from the rest of the application. A unit is the smallest testable part of an application, typically a function, method, or class. Unit tests verify that each unit works correctly on its own, catching bugs early and ensuring code quality through automated validation.

## Краткое описание (RU)

Модульное тестирование - это практика тестирования отдельных модулей или компонентов программного обеспечения в изоляции от остальной части приложения. Модуль - это наименьшая тестируемая часть приложения, обычно функция, метод или класс. Модульные тесты проверяют, что каждый модуль работает корректно сам по себе, выявляя ошибки на ранней стадии и обеспечивая качество кода через автоматизированную проверку.

## Key Points (EN)

- **Isolation**: Tests run independently without external dependencies
- **Fast execution**: Unit tests should run quickly (milliseconds)
- **Automated**: Run automatically in CI/CD pipelines
- **Repeatable**: Same input always produces same result
- **Test structure**: Follow Arrange-Act-Assert (AAA) pattern
- **Coverage**: Aim for high code coverage of critical logic
- **Mocking**: Use mock objects to isolate dependencies

## Ключевые моменты (RU)

- **Изоляция**: Тесты выполняются независимо без внешних зависимостей
- **Быстрое выполнение**: Модульные тесты должны выполняться быстро (миллисекунды)
- **Автоматизация**: Запускаются автоматически в CI/CD конвейерах
- **Воспроизводимость**: Одинаковые входные данные всегда дают одинаковый результат
- **Структура теста**: Следуют паттерну Arrange-Act-Assert (AAA)
- **Покрытие**: Стремление к высокому покрытию кода критической логики
- **Моки**: Использование мок-объектов для изоляции зависимостей

## JUnit Testing in Android/Kotlin

### Basic Test Structure

```kotlin
import org.junit.Test
import org.junit.Assert.*
import org.junit.Before
import org.junit.After

class CalculatorTest {
    private lateinit var calculator: Calculator

    @Before
    fun setup() {
        // Arrange: Set up test dependencies
        calculator = Calculator()
    }

    @After
    fun tearDown() {
        // Clean up resources if needed
    }

    @Test
    fun add_twoPositiveNumbers_returnsSum() {
        // Arrange
        val a = 5
        val b = 3

        // Act
        val result = calculator.add(a, b)

        // Assert
        assertEquals(8, result)
    }

    @Test
    fun divide_byZero_throwsException() {
        // Assert that exception is thrown
        assertThrows(ArithmeticException::class.java) {
            calculator.divide(10, 0)
        }
    }
}
```

### Testing ViewModels

```kotlin
class UserViewModelTest {
    private lateinit var viewModel: UserViewModel
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        // Use fake or mock repository
        repository = FakeUserRepository()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun loadUser_validId_updatesLiveData() = runTest {
        // Arrange
        val userId = 1
        val expectedUser = User(1, "John Doe")

        // Act
        viewModel.loadUser(userId)

        // Assert
        val user = viewModel.user.getOrAwaitValue()
        assertEquals(expectedUser, user)
    }

    @Test
    fun loadUser_invalidId_setsErrorState() = runTest {
        // Arrange
        val invalidId = -1

        // Act
        viewModel.loadUser(invalidId)

        // Assert
        assertTrue(viewModel.error.getOrAwaitValue() is Error.InvalidId)
    }
}
```

### Mocking with MockK

```kotlin
import io.mockk.mockk
import io.mockk.every
import io.mockk.verify
import io.mockk.coEvery
import io.mockk.coVerify

class UserServiceTest {
    private val repository: UserRepository = mockk()
    private lateinit var service: UserService

    @Before
    fun setup() {
        service = UserService(repository)
    }

    @Test
    fun getUser_callsRepository() = runTest {
        // Arrange
        val userId = 1
        val expectedUser = User(1, "John")
        coEvery { repository.getUser(userId) } returns expectedUser

        // Act
        val result = service.getUser(userId)

        // Assert
        assertEquals(expectedUser, result)
        coVerify(exactly = 1) { repository.getUser(userId) }
    }

    @Test
    fun getUser_repositoryThrows_propagatesException() = runTest {
        // Arrange
        val userId = 1
        coEvery { repository.getUser(userId) } throws NetworkException()

        // Act & Assert
        assertThrows(NetworkException::class.java) {
            runBlocking { service.getUser(userId) }
        }
    }
}
```

### Testing Coroutines

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Rule

class CoroutineTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun fetchData_success_returnsData() = runTest {
        // Arrange
        val repository = FakeRepository()
        val useCase = FetchDataUseCase(repository)

        // Act
        val result = useCase.execute()

        // Assert
        assertTrue(result.isSuccess)
        assertEquals("data", result.getOrNull())
    }

    @Test
    fun fetchData_withDelay_completesSuccessfully() = runTest {
        // Arrange
        val repository = FakeRepository()

        // Act
        val job = launch {
            delay(1000)
            repository.saveData("test")
        }

        // Advance time
        advanceTimeBy(1000)

        // Assert
        assertTrue(job.isCompleted)
    }
}
```

### Testing LiveData

```kotlin
// Helper extension for testing LiveData
fun <T> LiveData<T>.getOrAwaitValue(
    time: Long = 2,
    timeUnit: TimeUnit = TimeUnit.SECONDS
): T {
    var data: T? = null
    val latch = CountDownLatch(1)
    val observer = object : Observer<T> {
        override fun onChanged(value: T) {
            data = value
            latch.countDown()
            this@getOrAwaitValue.removeObserver(this)
        }
    }
    this.observeForever(observer)
    if (!latch.await(time, timeUnit)) {
        throw TimeoutException("LiveData value was never set.")
    }
    @Suppress("UNCHECKED_CAST")
    return data as T
}
```

### Parameterized Tests

```kotlin
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized

@RunWith(Parameterized::class)
class ParameterizedCalculatorTest(
    private val input1: Int,
    private val input2: Int,
    private val expected: Int
) {
    companion object {
        @JvmStatic
        @Parameterized.Parameters
        fun data(): Collection<Array<Int>> {
            return listOf(
                arrayOf(1, 1, 2),
                arrayOf(2, 3, 5),
                arrayOf(-1, 1, 0),
                arrayOf(0, 0, 0)
            )
        }
    }

    @Test
    fun add_variousInputs_returnsExpectedSum() {
        val calculator = Calculator()
        assertEquals(expected, calculator.add(input1, input2))
    }
}
```

## Test-Driven Development (TDD)

### Red-Green-Refactor Cycle

```kotlin
// 1. RED: Write failing test first
@Test
fun calculateDiscount_premiumUser_returns20Percent() {
    val calculator = DiscountCalculator()
    val discount = calculator.calculate(User(isPremium = true), 100.0)
    assertEquals(20.0, discount, 0.01)
}

// 2. GREEN: Write minimal code to pass
class DiscountCalculator {
    fun calculate(user: User, amount: Double): Double {
        return if (user.isPremium) amount * 0.2 else 0.0
    }
}

// 3. REFACTOR: Improve code while keeping tests green
class DiscountCalculator {
    companion object {
        private const val PREMIUM_DISCOUNT_RATE = 0.2
        private const val REGULAR_DISCOUNT_RATE = 0.0
    }

    fun calculate(user: User, amount: Double): Double {
        val rate = if (user.isPremium) PREMIUM_DISCOUNT_RATE else REGULAR_DISCOUNT_RATE
        return amount * rate
    }
}
```

## Use Cases

### When to Use

- **Business logic**: Test complex calculations and algorithms
- **Data transformations**: Verify data mapping and parsing
- **Utilities**: Test helper functions and extensions
- **ViewModels**: Test state management and business logic
- **Use cases**: Test single-responsibility business operations
- **Repositories**: Test data access logic (with mocked data sources)
- **Validation**: Test input validation and error handling

### When to Avoid

- **UI testing**: Use Espresso or Compose UI tests instead
- **Integration testing**: Use integration tests for multi-component scenarios
- **Database operations**: Use instrumented tests on real database
- **Network calls**: Use integration tests or E2E tests
- **Android framework dependencies**: Requires instrumented tests

## Trade-offs

**Pros**:
- **Early bug detection**: Catch issues before they reach production
- **Refactoring confidence**: Change code safely with test safety net
- **Documentation**: Tests serve as executable documentation
- **Design improvement**: Writing testable code improves architecture
- **Fast feedback**: Tests run in milliseconds
- **Regression prevention**: Ensure old bugs don't resurface
- **CI/CD integration**: Automated quality gates

**Cons**:
- **Initial time investment**: Writing tests takes time
- **Maintenance overhead**: Tests need updates when code changes
- **False confidence**: High coverage doesn't guarantee bug-free code
- **Learning curve**: Requires knowledge of testing frameworks
- **Mocking complexity**: Complex mocking can be fragile
- **Test brittleness**: Over-specified tests break with minor changes

## Testing Best Practices

### FIRST Principles

- **Fast**: Tests should run quickly
- **Isolated**: Tests should not depend on each other
- **Repeatable**: Same result every time
- **Self-validating**: Pass or fail, no manual verification
- **Timely**: Written close to production code

### Naming Conventions

```kotlin
// Pattern: methodName_stateUnderTest_expectedBehavior
@Test
fun calculateTotal_emptyCart_returnsZero()

@Test
fun validateEmail_invalidFormat_returnsFalse()

@Test
fun processPayment_insufficientFunds_throwsException()
```

### Code Coverage Goals

- **Critical paths**: 100% coverage of business-critical logic
- **Overall target**: 70-80% code coverage
- **Don't chase 100%**: Focus on valuable tests, not coverage metrics
- **Cover edge cases**: Test boundary conditions and error paths

## Common Assertions

```kotlin
// Equality
assertEquals(expected, actual)
assertNotEquals(unexpected, actual)

// Boolean
assertTrue(condition)
assertFalse(condition)

// Null checks
assertNull(value)
assertNotNull(value)

// Collections
assertArrayEquals(expectedArray, actualArray)
assertIterableEquals(expectedList, actualList)

// Exceptions
assertThrows(Exception::class.java) { /* code */ }

// Custom messages
assertEquals(expected, actual, "Values should match")

// Kotlin test assertions
expect(5) { 2 + 3 }
```

## Related Concepts

- [[c-software-design-patterns]]
- [[c-dependency-injection]]
- [[c-coroutines]]
- [[c-lifecycle]]

## References

- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [Android Testing Documentation](https://developer.android.com/training/testing)
- [MockK Documentation](https://mockk.io/)
- [Kotlin Coroutines Test](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-test/)
- "Test Driven Development: By Example" by Kent Beck
- [Testing Best Practices - Android](https://developer.android.com/training/testing/fundamentals)
