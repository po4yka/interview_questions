---
id: be-db-003
title: Database Connection Pooling / Пулинг соединений с БД
aliases: []
topic: databases
subtopics:
- connections
- performance
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
- c-databases
- c-performance
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- connections
- performance
- difficulty/medium
- topic/databases
anki_cards:
- slug: be-db-003-0-en
  language: en
  anki_id: 1769167242886
  synced_at: '2026-01-23T15:20:43.084290'
- slug: be-db-003-0-ru
  language: ru
  anki_id: 1769167242920
  synced_at: '2026-01-23T15:20:43.085486'
---
# Question (EN)
> What is connection pooling and why is it important?

# Vopros (RU)
> Что такое пулинг соединений и почему он важен?

---

## Answer (EN)

**Connection Pooling** - Maintaining a cache of reusable database connections instead of creating new ones for each request.

**Why Connections are Expensive:**
- TCP handshake
- SSL/TLS negotiation
- Authentication
- Server-side memory allocation
- ~10-50ms per new connection

---

**How Pooling Works:**

```
Without Pool:
Request -> Create Connection -> Query -> Close Connection -> Response

With Pool:
Request -> Get Connection from Pool -> Query -> Return to Pool -> Response
```

**Pool Lifecycle:**
1. Application starts: Create minimum connections
2. Request arrives: Borrow connection from pool
3. Query executes
4. Request completes: Return connection to pool
5. Connection idle: Keep alive or close after timeout

---

**Configuration Parameters:**

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `min_size` | Minimum connections always open | 5-10 |
| `max_size` | Maximum connections allowed | 20-50 |
| `max_idle_time` | Close idle connections after | 300s |
| `connection_timeout` | Wait for available connection | 30s |
| `max_lifetime` | Recycle connection after | 1800s |

**Example (Python/SQLAlchemy):**
```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=10,           # Max connections
    max_overflow=5,         # Extra connections if needed
    pool_timeout=30,        # Wait for connection
    pool_recycle=1800,      # Recycle after 30 min
    pool_pre_ping=True      # Validate before use
)
```

**Example (HikariCP/Java):**
```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://host/db");
config.setMaximumPoolSize(10);
config.setMinimumIdle(5);
config.setIdleTimeout(300000);
config.setConnectionTimeout(30000);
```

---

**Pool Sizing Formula:**
```
pool_size = (core_count * 2) + effective_spindle_count
```
For SSDs: `pool_size = core_count * 2 + 1`

**Common Issues:**
- Connection leaks (not returning to pool)
- Pool exhaustion (all connections busy)
- Stale connections (database restart)

**Solutions:**
- Use context managers / try-finally
- Set reasonable timeouts
- Enable connection validation (pre-ping)

## Otvet (RU)

**Пулинг соединений** - Поддержание кэша переиспользуемых соединений с базой данных вместо создания новых для каждого запроса.

**Почему соединения дорогие:**
- TCP handshake
- SSL/TLS переговоры
- Аутентификация
- Выделение памяти на сервере
- ~10-50мс на новое соединение

---

**Как работает пулинг:**

```
Без пула:
Запрос -> Создать соединение -> Запрос к БД -> Закрыть соединение -> Ответ

С пулом:
Запрос -> Взять соединение из пула -> Запрос к БД -> Вернуть в пул -> Ответ
```

**Жизненный цикл пула:**
1. Приложение запускается: Создать минимум соединений
2. Приходит запрос: Взять соединение из пула
3. Выполняется запрос к БД
4. Запрос завершён: Вернуть соединение в пул
5. Соединение простаивает: Поддерживать или закрыть после таймаута

---

**Параметры конфигурации:**

| Параметр | Описание | Типичное значение |
|----------|----------|-------------------|
| `min_size` | Минимум всегда открытых соединений | 5-10 |
| `max_size` | Максимум разрешённых соединений | 20-50 |
| `max_idle_time` | Закрывать простаивающие через | 300с |
| `connection_timeout` | Ожидание свободного соединения | 30с |
| `max_lifetime` | Пересоздавать соединение после | 1800с |

**Пример (Python/SQLAlchemy):**
```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=10,           # Макс соединений
    max_overflow=5,         # Дополнительные при необходимости
    pool_timeout=30,        # Ожидание соединения
    pool_recycle=1800,      # Пересоздание через 30 мин
    pool_pre_ping=True      # Проверка перед использованием
)
```

**Пример (HikariCP/Java):**
```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://host/db");
config.setMaximumPoolSize(10);
config.setMinimumIdle(5);
config.setIdleTimeout(300000);
config.setConnectionTimeout(30000);
```

---

**Формула размера пула:**
```
pool_size = (core_count * 2) + effective_spindle_count
```
Для SSD: `pool_size = core_count * 2 + 1`

**Частые проблемы:**
- Утечки соединений (не возвращаются в пул)
- Исчерпание пула (все соединения заняты)
- Устаревшие соединения (рестарт базы)

**Решения:**
- Используйте context managers / try-finally
- Установите разумные таймауты
- Включите валидацию соединений (pre-ping)

---

## Follow-ups
- What is PgBouncer and when to use it?
- How to monitor connection pool health?
- What is connection pool exhaustion?

## Dopolnitelnye voprosy (RU)
- Что такое PgBouncer и когда его использовать?
- Как мониторить здоровье пула соединений?
- Что такое исчерпание пула соединений?

## References
- [[c-databases]]
- [[c-performance]]
- [[moc-backend]]
