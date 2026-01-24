---
id: cs-eng-testing
title: Software Engineering - Testing
topic: software_engineering
difficulty: medium
tags:
- cs_testing
- best_practices
anki_cards:
- slug: cs-eng-test-0-en
  language: en
  anki_id: 1769160675825
  synced_at: '2026-01-23T13:31:18.896319'
- slug: cs-eng-test-0-ru
  language: ru
  anki_id: 1769160675849
  synced_at: '2026-01-23T13:31:18.897747'
- slug: cs-eng-test-1-en
  language: en
  anki_id: 1769160675874
  synced_at: '2026-01-23T13:31:18.899044'
- slug: cs-eng-test-1-ru
  language: ru
  anki_id: 1769160675899
  synced_at: '2026-01-23T13:31:18.900408'
---
# Software Testing

## Testing Levels

### Unit Testing

Test individual functions/methods in isolation.

```python
import pytest

def add(a, b):
    return a + b

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_add_zero():
    assert add(0, 0) == 0
```

**Characteristics**:
- Fast execution
- No external dependencies
- Tests single unit of code

### Integration Testing

Test interactions between components.

```python
def test_user_order_flow():
    user = create_user()
    product = create_product()
    order = create_order(user, product)

    assert order.user_id == user.id
    assert order.total == product.price
```

**Tests**: Database access, API calls, module interactions.

### End-to-End (E2E) Testing

Test complete user flows through entire system.

```python
# Selenium example
def test_checkout_flow(browser):
    browser.get("/products")
    browser.find_element(By.ID, "add-to-cart").click()
    browser.find_element(By.ID, "checkout").click()
    browser.find_element(By.ID, "confirm").click()

    assert "Order confirmed" in browser.page_source
```

**Characteristics**:
- Slow execution
- Brittle (UI changes break tests)
- High confidence in user experience

## Testing Pyramid

```
          /\
         /E2E\        Few, slow, expensive
        /------\
       / Integ  \     Some
      /----------\
     /    Unit    \   Many, fast, cheap
    /______________\
```

**Ideal ratio**: Many unit tests, some integration, few E2E.

## Test-Driven Development (TDD)

Red-Green-Refactor cycle.

```
1. RED: Write failing test
2. GREEN: Write minimal code to pass
3. REFACTOR: Improve code, keep tests passing
```

**Benefits**:
- Design emerges from tests
- High test coverage
- Documentation through tests

## Testing Techniques

### Mocking

Replace dependencies with test doubles.

```python
from unittest.mock import Mock, patch

def test_send_notification(mocker):
    # Mock email service
    mock_email = mocker.patch('services.email.send')
    mock_email.return_value = True

    result = notify_user(user_id=1, message="Hello")

    mock_email.assert_called_once_with(
        to="user@example.com",
        body="Hello"
    )
    assert result == True
```

### Test Doubles

| Type | Description |
|------|-------------|
| **Dummy** | Passed but never used |
| **Stub** | Returns canned responses |
| **Mock** | Verifies interactions |
| **Fake** | Working implementation (e.g., in-memory DB) |
| **Spy** | Records calls, uses real implementation |

### Fixtures

Set up test data and state.

```python
import pytest

@pytest.fixture
def user():
    return User(name="John", email="john@example.com")

@pytest.fixture
def database():
    db = create_test_database()
    yield db
    db.cleanup()

def test_save_user(database, user):
    database.save(user)
    assert database.get(user.id) == user
```

### Parametrized Tests

Run same test with different inputs.

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (-2, 4),
])
def test_square(input, expected):
    assert square(input) == expected
```

## Test Coverage

**Line coverage**: % of lines executed.
**Branch coverage**: % of branches taken.
**Path coverage**: % of execution paths tested.

```bash
# Python coverage
pytest --cov=myapp --cov-report=html
```

**Goal**: 80%+ coverage, but quality over quantity.

## Property-Based Testing

Generate random inputs, verify properties.

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_preserves_length(lst):
    assert len(sorted(lst)) == len(lst)

@given(st.lists(st.integers()))
def test_sort_is_sorted(lst):
    result = sorted(lst)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]
```

**Benefits**: Finds edge cases you wouldn't think of.

## Testing Best Practices

### FIRST Principles

- **Fast**: Run quickly
- **Independent**: No dependencies between tests
- **Repeatable**: Same result every time
- **Self-validating**: Pass/fail without manual inspection
- **Timely**: Written with production code

### Arrange-Act-Assert

```python
def test_withdraw():
    # Arrange
    account = Account(balance=100)

    # Act
    account.withdraw(30)

    # Assert
    assert account.balance == 70
```

### Test Naming

```python
# Pattern: test_<unit>_<scenario>_<expected>
def test_withdraw_sufficient_balance_reduces_balance():
    ...

def test_withdraw_insufficient_balance_raises_error():
    ...
```

### What to Test

**Do test**:
- Business logic
- Edge cases
- Error handling
- Public APIs

**Don't test**:
- Third-party libraries
- Trivial getters/setters
- Implementation details

## Flaky Tests

Tests that fail intermittently.

**Causes**:
- Race conditions
- External dependencies
- Hardcoded dates/times
- Order dependencies

**Solutions**:
- Isolate tests
- Mock external services
- Use fixed time
- Retry with logging

## Performance Testing

### Load Testing

Normal expected load.

### Stress Testing

Beyond normal capacity.

### Spike Testing

Sudden load increase.

```python
# Locust example
from locust import HttpUser, task

class WebsiteUser(HttpUser):
    @task
    def view_products(self):
        self.client.get("/products")

    @task
    def create_order(self):
        self.client.post("/orders", json={"product_id": 1})
```

## Interview Questions

1. **What is the testing pyramid?**
   - Many unit tests (fast, cheap)
   - Some integration tests
   - Few E2E tests (slow, expensive)
   - Provides balanced coverage

2. **What is TDD?**
   - Test-Driven Development
   - Write test first (red)
   - Write code to pass (green)
   - Refactor (keep green)

3. **When to use mocks?**
   - External services
   - Database access
   - Slow operations
   - Non-deterministic behavior

4. **How to handle flaky tests?**
   - Identify root cause
   - Isolate from external dependencies
   - Mock time-dependent code
   - Remove order dependencies
