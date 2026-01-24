---
id: be-pat-001
title: Repository Pattern / Паттерн репозиторий
aliases: []
topic: patterns
subtopics:
- repository
- data-access
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
- repository
- architecture
- difficulty/medium
- topic/patterns
anki_cards:
- slug: be-pat-001-0-en
  language: en
  anki_id: 1769167240205
  synced_at: '2026-01-23T15:20:42.964173'
- slug: be-pat-001-0-ru
  language: ru
  anki_id: 1769167240230
  synced_at: '2026-01-23T15:20:42.965616'
---
# Question (EN)
> What is the Repository pattern and when should it be used?

# Vopros (RU)
> Что такое паттерн Репозиторий и когда его следует использовать?

---

## Answer (EN)

**Repository Pattern** - An abstraction layer between domain/business logic and data access layer. Provides collection-like interface for accessing domain objects.

**Purpose:**
- Decouple business logic from data access
- Enable testability (mock repositories)
- Centralize query logic
- Hide persistence details from domain

---

**Interface Definition:**

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        pass
```

**Concrete Implementation:**

```python
class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def save(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
```

**Usage in Service:**

```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_user(self, email: str, password: str) -> User:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user = User(email=email, password=hash_password(password))
        return self.user_repo.save(user)
```

---

**Repository vs Active Record:**

| Aspect | Repository | Active Record |
|--------|------------|---------------|
| Data access | Separate class | In domain object |
| Testability | Easy to mock | Harder |
| Complexity | Higher | Lower |
| SRP | Follows | Violates |
| Use case | Complex domains | Simple CRUD |

**When to Use:**
- Complex business logic
- Multiple data sources
- Need high testability
- Domain-Driven Design

**When NOT to Use:**
- Simple CRUD apps
- Small projects
- When ORM provides enough abstraction

## Otvet (RU)

**Паттерн Репозиторий** - Слой абстракции между доменной/бизнес-логикой и слоем доступа к данным. Предоставляет коллекционно-подобный интерфейс для доступа к доменным объектам.

**Назначение:**
- Отделить бизнес-логику от доступа к данным
- Обеспечить тестируемость (мок репозитории)
- Централизовать логику запросов
- Скрыть детали персистентности от домена

---

**Определение интерфейса:**

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        pass
```

**Конкретная реализация:**

```python
class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def save(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
```

**Использование в сервисе:**

```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_user(self, email: str, password: str) -> User:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user = User(email=email, password=hash_password(password))
        return self.user_repo.save(user)
```

---

**Repository vs Active Record:**

| Аспект | Repository | Active Record |
|--------|------------|---------------|
| Доступ к данным | Отдельный класс | В доменном объекте |
| Тестируемость | Легко мокать | Сложнее |
| Сложность | Выше | Ниже |
| SRP | Соблюдает | Нарушает |
| Сценарий | Сложные домены | Простой CRUD |

**Когда использовать:**
- Сложная бизнес-логика
- Несколько источников данных
- Нужна высокая тестируемость
- Domain-Driven Design

**Когда НЕ использовать:**
- Простые CRUD-приложения
- Маленькие проекты
- Когда ORM даёт достаточную абстракцию

---

## Follow-ups
- What is the Unit of Work pattern?
- How does Repository differ from DAO?
- Should repositories handle transactions?

## Dopolnitelnye voprosy (RU)
- Что такое паттерн Unit of Work?
- Чем Repository отличается от DAO?
- Должны ли репозитории обрабатывать транзакции?

## References
- [[c-patterns]]
- [[c-architecture]]
- [[moc-backend]]
