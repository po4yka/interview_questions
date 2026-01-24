---
id: be-pat-004
title: Dependency Injection / Внедрение зависимостей
aliases: []
topic: patterns
subtopics:
- dependency-injection
- architecture
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
- c-patterns
- c-architecture
created: 2025-01-23
updated: 2025-01-23
tags:
- patterns
- dependency-injection
- architecture
- difficulty/medium
- topic/patterns
anki_cards:
- slug: be-pat-004-0-en
  language: en
  anki_id: 1769167242765
  synced_at: '2026-01-23T15:20:43.077629'
- slug: be-pat-004-0-ru
  language: ru
  anki_id: 1769167242791
  synced_at: '2026-01-23T15:20:43.079357'
---
# Question (EN)
> What is Dependency Injection and what are its benefits?

# Vopros (RU)
> Что такое внедрение зависимостей и каковы его преимущества?

---

## Answer (EN)

**Dependency Injection (DI)** - A design pattern where objects receive their dependencies from external sources rather than creating them internally.

**Without DI (Tight Coupling):**
```python
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard-coded dependency
        self.cache = RedisCache()     # Can't change or mock

    def get_user(self, user_id):
        return self.db.query(User, user_id)
```

**With DI (Loose Coupling):**
```python
class UserService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db      # Injected from outside
        self.cache = cache

    def get_user(self, user_id):
        return self.db.query(User, user_id)

# Usage
service = UserService(
    db=PostgresDatabase(),
    cache=RedisCache()
)
```

---

**DI Types:**

**1. Constructor Injection (Preferred)**
```python
class OrderService:
    def __init__(self, repo: OrderRepository, mailer: EmailService):
        self.repo = repo
        self.mailer = mailer
```

**2. Setter Injection**
```python
class OrderService:
    def set_repository(self, repo: OrderRepository):
        self.repo = repo
```

**3. Method Injection**
```python
class OrderService:
    def process_order(self, order, payment_gateway: PaymentGateway):
        payment_gateway.charge(order.total)
```

---

**DI Containers (IoC Containers):**

**FastAPI (Built-in):**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()
```

**Python (dependency-injector):**
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(
        Database,
        connection_string=config.db_url
    )

    user_service = providers.Factory(
        UserService,
        db=db
    )
```

---

**Benefits:**

| Benefit | Description |
|---------|-------------|
| Testability | Easy to mock dependencies |
| Flexibility | Swap implementations |
| Loose coupling | Components independent |
| Single Responsibility | Class doesn't manage deps |
| Reusability | Components work anywhere |

**Testing with DI:**
```python
def test_user_service():
    # Mock dependencies
    mock_db = Mock(spec=Database)
    mock_db.query.return_value = User(id=1, name="Test")

    # Inject mocks
    service = UserService(db=mock_db, cache=Mock())

    # Test
    user = service.get_user(1)
    assert user.name == "Test"
```

## Otvet (RU)

**Dependency Injection (DI)** - Паттерн проектирования, при котором объекты получают свои зависимости из внешних источников, а не создают их внутри.

**Без DI (сильная связанность):**
```python
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()  # Жёстко заданная зависимость
        self.cache = RedisCache()     # Нельзя изменить или замокать

    def get_user(self, user_id):
        return self.db.query(User, user_id)
```

**С DI (слабая связанность):**
```python
class UserService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db      # Внедрено извне
        self.cache = cache

    def get_user(self, user_id):
        return self.db.query(User, user_id)

# Использование
service = UserService(
    db=PostgresDatabase(),
    cache=RedisCache()
)
```

---

**Типы DI:**

**1. Constructor Injection (предпочтительно)**
```python
class OrderService:
    def __init__(self, repo: OrderRepository, mailer: EmailService):
        self.repo = repo
        self.mailer = mailer
```

**2. Setter Injection**
```python
class OrderService:
    def set_repository(self, repo: OrderRepository):
        self.repo = repo
```

**3. Method Injection**
```python
class OrderService:
    def process_order(self, order, payment_gateway: PaymentGateway):
        payment_gateway.charge(order.total)
```

---

**DI-контейнеры (IoC-контейнеры):**

**FastAPI (встроенный):**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()
```

**Python (dependency-injector):**
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(
        Database,
        connection_string=config.db_url
    )

    user_service = providers.Factory(
        UserService,
        db=db
    )
```

---

**Преимущества:**

| Преимущество | Описание |
|--------------|----------|
| Тестируемость | Легко мокать зависимости |
| Гибкость | Замена реализаций |
| Слабая связанность | Компоненты независимы |
| Single Responsibility | Класс не управляет deps |
| Переиспользуемость | Компоненты работают везде |

**Тестирование с DI:**
```python
def test_user_service():
    # Мокаем зависимости
    mock_db = Mock(spec=Database)
    mock_db.query.return_value = User(id=1, name="Test")

    # Внедряем моки
    service = UserService(db=mock_db, cache=Mock())

    # Тест
    user = service.get_user(1)
    assert user.name == "Test"
```

---

## Follow-ups
- What is Inversion of Control (IoC)?
- How does DI relate to SOLID principles?
- What are DI scopes (singleton, transient, scoped)?

## Dopolnitelnye voprosy (RU)
- Что такое Inversion of Control (IoC)?
- Как DI связан с принципами SOLID?
- Что такое scope в DI (singleton, transient, scoped)?

## References
- [[c-patterns]]
- [[c-architecture]]
- [[moc-backend]]
