---
id: be-test-002
title: Integration Testing with Databases / Интеграционное тестирование с БД
aliases: []
topic: testing
subtopics:
- integration-testing
- databases
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
- c-databases
created: 2025-01-23
updated: 2025-01-23
tags:
- testing
- integration-testing
- databases
- difficulty/medium
- topic/testing
anki_cards:
- slug: be-test-002-0-en
  language: en
  anki_id: 1769167240856
  synced_at: '2026-01-23T15:20:42.995833'
- slug: be-test-002-0-ru
  language: ru
  anki_id: 1769167240879
  synced_at: '2026-01-23T15:20:42.997625'
---
# Question (EN)
> How to write integration tests that interact with a real database?

# Vopros (RU)
> Как писать интеграционные тесты, взаимодействующие с реальной базой данных?

---

## Answer (EN)

**Integration Test Characteristics:**
- Tests real component interactions
- Uses real database (test instance)
- Slower than unit tests
- Tests repository/query logic

---

**Database Setup Strategies:**

**1. In-Memory Database (SQLite):**
```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```
**Pros:** Fast, no setup
**Cons:** Dialect differences from production DB

**2. Test Database (Same dialect as prod):**
```python
@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("postgresql://test:test@localhost/test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
```

**3. Testcontainers (Docker):**
```python
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres.get_connection_url()
```

---

**Transaction Rollback Pattern:**

```python
@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Rollback after each test (clean slate)
    session.close()
    transaction.rollback()
    connection.close()
```

---

**Test Example:**

```python
class TestUserRepository:
    def test_create_user(self, db_session):
        # Arrange
        repo = UserRepository(db_session)
        user = User(email="test@example.com", name="Test")

        # Act
        saved_user = repo.save(user)
        db_session.flush()

        # Assert
        found = repo.get_by_id(saved_user.id)
        assert found.email == "test@example.com"

    def test_find_by_email(self, db_session):
        # Seed data
        repo = UserRepository(db_session)
        repo.save(User(email="find@example.com", name="Find Me"))
        db_session.flush()

        # Test query
        user = repo.get_by_email("find@example.com")
        assert user is not None
        assert user.name == "Find Me"

    def test_delete_user(self, db_session):
        repo = UserRepository(db_session)
        user = repo.save(User(email="delete@example.com"))
        db_session.flush()

        repo.delete(user.id)
        db_session.flush()

        assert repo.get_by_id(user.id) is None
```

---

**Test Data Management:**

**Factories (factory_boy):**
```python
import factory

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")

def test_with_factory(db_session):
    UserFactory._meta.sqlalchemy_session = db_session
    user = UserFactory.create()
    assert user.id is not None
```

**Best Practices:**
- Use same DB dialect as production
- Rollback transactions for isolation
- Use factories for test data
- Keep integration tests separate from unit tests
- Run in CI with real database

## Otvet (RU)

**Характеристики интеграционных тестов:**
- Тестируют реальное взаимодействие компонентов
- Используют реальную БД (тестовый инстанс)
- Медленнее модульных тестов
- Тестируют логику репозитория/запросов

---

**Стратегии настройки БД:**

**1. In-Memory база данных (SQLite):**
```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```
**Плюсы:** Быстро, не требует настройки
**Минусы:** Различия диалекта с продакшн БД

**2. Тестовая БД (тот же диалект что и прод):**
```python
@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("postgresql://test:test@localhost/test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
```

**3. Testcontainers (Docker):**
```python
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres.get_connection_url()
```

---

**Паттерн отката транзакции:**

```python
@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Откат после каждого теста (чистое состояние)
    session.close()
    transaction.rollback()
    connection.close()
```

---

**Пример теста:**

```python
class TestUserRepository:
    def test_create_user(self, db_session):
        # Arrange
        repo = UserRepository(db_session)
        user = User(email="test@example.com", name="Test")

        # Act
        saved_user = repo.save(user)
        db_session.flush()

        # Assert
        found = repo.get_by_id(saved_user.id)
        assert found.email == "test@example.com"

    def test_find_by_email(self, db_session):
        # Подготовка данных
        repo = UserRepository(db_session)
        repo.save(User(email="find@example.com", name="Find Me"))
        db_session.flush()

        # Тест запроса
        user = repo.get_by_email("find@example.com")
        assert user is not None
        assert user.name == "Find Me"

    def test_delete_user(self, db_session):
        repo = UserRepository(db_session)
        user = repo.save(User(email="delete@example.com"))
        db_session.flush()

        repo.delete(user.id)
        db_session.flush()

        assert repo.get_by_id(user.id) is None
```

---

**Управление тестовыми данными:**

**Фабрики (factory_boy):**
```python
import factory

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")

def test_with_factory(db_session):
    UserFactory._meta.sqlalchemy_session = db_session
    user = UserFactory.create()
    assert user.id is not None
```

**Лучшие практики:**
- Используйте тот же диалект БД, что и в продакшене
- Откатывайте транзакции для изоляции
- Используйте фабрики для тестовых данных
- Держите интеграционные тесты отдельно от модульных
- Запускайте в CI с реальной базой данных

---

## Follow-ups
- What are Testcontainers and when to use them?
- How to test database migrations?
- What is the difference between fixtures and factories?

## Dopolnitelnye voprosy (RU)
- Что такое Testcontainers и когда их использовать?
- Как тестировать миграции базы данных?
- В чём разница между фикстурами и фабриками?

## References
- [[c-testing]]
- [[c-databases]]
- [[moc-backend]]
