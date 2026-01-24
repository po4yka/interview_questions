---
id: be-test-001
title: Backend Unit Testing / Модульное тестирование бэкенда
aliases: []
topic: testing
subtopics:
- unit-testing
- pytest
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Backend interview preparation
status: draft
moc: moc-backend
related:
- c-testing
- c-backend
created: 2025-01-23
updated: 2025-01-23
tags:
- testing
- unit-testing
- pytest
- difficulty/medium
- topic/testing
anki_cards:
- slug: be-test-001-0-en
  language: en
  anki_id: 1769167240131
  synced_at: '2026-01-23T15:20:42.960422'
- slug: be-test-001-0-ru
  language: ru
  anki_id: 1769167240181
  synced_at: '2026-01-23T15:20:42.962954'
---
# Question (EN)
> How to write effective unit tests for backend services?

# Vopros (RU)
> Как писать эффективные модульные тесты для бэкенд-сервисов?

---

## Answer (EN)

**Unit Test Principles:**
- Test one thing per test
- Fast execution (no I/O)
- Isolated (no external dependencies)
- Repeatable (same result every time)
- Self-validating (pass/fail automatically)

---

**Test Structure (AAA Pattern):**

```python
def test_user_registration():
    # Arrange - Set up test data and mocks
    user_data = {"email": "test@example.com", "password": "secure123"}
    mock_repo = Mock(spec=UserRepository)
    mock_repo.get_by_email.return_value = None
    service = UserService(mock_repo)

    # Act - Execute the code under test
    result = service.register(user_data)

    # Assert - Verify the outcome
    assert result.email == "test@example.com"
    mock_repo.save.assert_called_once()
```

---

**Mocking Dependencies:**

```python
from unittest.mock import Mock, patch, MagicMock

# Mock object
mock_db = Mock(spec=Database)
mock_db.query.return_value = [User(id=1, name="Test")]

# Patch decorator
@patch('app.services.email_service.send_email')
def test_send_welcome_email(mock_send):
    mock_send.return_value = True
    service = UserService()
    service.send_welcome("test@example.com")
    mock_send.assert_called_with("test@example.com", "Welcome!")

# Context manager
def test_external_api():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        result = fetch_external_data()
        assert result["status"] == "ok"
```

---

**Pytest Fixtures:**

```python
import pytest

@pytest.fixture
def user_service():
    """Create service with mocked dependencies"""
    mock_repo = Mock(spec=UserRepository)
    mock_cache = Mock(spec=Cache)
    return UserService(mock_repo, mock_cache)

@pytest.fixture
def sample_user():
    return User(id=1, email="test@example.com", name="Test User")

def test_get_user(user_service, sample_user):
    user_service.repo.get_by_id.return_value = sample_user
    result = user_service.get_user(1)
    assert result.email == "test@example.com"
```

---

**Testing Edge Cases:**

```python
class TestUserService:
    def test_register_success(self, user_service):
        # Happy path
        ...

    def test_register_duplicate_email(self, user_service):
        user_service.repo.get_by_email.return_value = User(id=1)
        with pytest.raises(DuplicateEmailError):
            user_service.register({"email": "exists@example.com"})

    def test_register_invalid_email(self, user_service):
        with pytest.raises(ValidationError):
            user_service.register({"email": "not-an-email"})

    def test_get_user_not_found(self, user_service):
        user_service.repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            user_service.get_user(999)
```

---

**What to Test:**

| Test | Don't Test |
|------|------------|
| Business logic | Framework code |
| Input validation | Database queries (integration) |
| Error handling | External APIs (integration) |
| Edge cases | Private methods directly |
| State transitions | Simple getters/setters |

**Test Coverage Guidelines:**
- 80%+ for business logic
- Focus on critical paths
- Don't chase 100% coverage blindly

## Otvet (RU)

**Принципы модульных тестов:**
- Один тест - одна проверка
- Быстрое выполнение (без I/O)
- Изолированность (нет внешних зависимостей)
- Повторяемость (одинаковый результат каждый раз)
- Самопроверяемость (pass/fail автоматически)

---

**Структура теста (паттерн AAA):**

```python
def test_user_registration():
    # Arrange - Настройка тестовых данных и моков
    user_data = {"email": "test@example.com", "password": "secure123"}
    mock_repo = Mock(spec=UserRepository)
    mock_repo.get_by_email.return_value = None
    service = UserService(mock_repo)

    # Act - Выполнение тестируемого кода
    result = service.register(user_data)

    # Assert - Проверка результата
    assert result.email == "test@example.com"
    mock_repo.save.assert_called_once()
```

---

**Мокирование зависимостей:**

```python
from unittest.mock import Mock, patch, MagicMock

# Mock-объект
mock_db = Mock(spec=Database)
mock_db.query.return_value = [User(id=1, name="Test")]

# Декоратор patch
@patch('app.services.email_service.send_email')
def test_send_welcome_email(mock_send):
    mock_send.return_value = True
    service = UserService()
    service.send_welcome("test@example.com")
    mock_send.assert_called_with("test@example.com", "Welcome!")

# Контекстный менеджер
def test_external_api():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        result = fetch_external_data()
        assert result["status"] == "ok"
```

---

**Pytest-фикстуры:**

```python
import pytest

@pytest.fixture
def user_service():
    """Создание сервиса с замоканными зависимостями"""
    mock_repo = Mock(spec=UserRepository)
    mock_cache = Mock(spec=Cache)
    return UserService(mock_repo, mock_cache)

@pytest.fixture
def sample_user():
    return User(id=1, email="test@example.com", name="Test User")

def test_get_user(user_service, sample_user):
    user_service.repo.get_by_id.return_value = sample_user
    result = user_service.get_user(1)
    assert result.email == "test@example.com"
```

---

**Тестирование граничных случаев:**

```python
class TestUserService:
    def test_register_success(self, user_service):
        # Успешный путь
        ...

    def test_register_duplicate_email(self, user_service):
        user_service.repo.get_by_email.return_value = User(id=1)
        with pytest.raises(DuplicateEmailError):
            user_service.register({"email": "exists@example.com"})

    def test_register_invalid_email(self, user_service):
        with pytest.raises(ValidationError):
            user_service.register({"email": "not-an-email"})

    def test_get_user_not_found(self, user_service):
        user_service.repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            user_service.get_user(999)
```

---

**Что тестировать:**

| Тестируем | Не тестируем |
|-----------|--------------|
| Бизнес-логику | Код фреймворка |
| Валидацию ввода | Запросы к БД (интеграция) |
| Обработку ошибок | Внешние API (интеграция) |
| Граничные случаи | Приватные методы напрямую |
| Переходы состояний | Простые getter/setter |

**Рекомендации по покрытию:**
- 80%+ для бизнес-логики
- Фокус на критических путях
- Не гонитесь за 100% покрытием слепо

---

## Follow-ups
- What is the difference between mock, stub, and fake?
- How to test async code in pytest?
- What is parameterized testing?

## Dopolnitelnye voprosy (RU)
- В чём разница между mock, stub и fake?
- Как тестировать async-код в pytest?
- Что такое параметризованное тестирование?

## References
- [[c-testing]]
- [[c-backend]]
- [[moc-backend]]
