---
id: be-obs-001
title: Structured Logging / Структурированное логирование
aliases: []
topic: observability
subtopics:
- logging
- json
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
- c-observability
- c-logging
created: 2025-01-23
updated: 2025-01-23
tags:
- observability
- logging
- json
- difficulty/medium
- topic/observability
anki_cards:
- slug: be-obs-001-0-en
  language: en
  anki_id: 1769167242812
  synced_at: '2026-01-23T15:20:43.081492'
- slug: be-obs-001-0-ru
  language: ru
  anki_id: 1769167242848
  synced_at: '2026-01-23T15:20:43.083148'
---
# Question (EN)
> What is structured logging and why is it better than plain text logs?

# Vopros (RU)
> Что такое структурированное логирование и почему оно лучше простых текстовых логов?

---

## Answer (EN)

**Plain Text Logging (Traditional):**
```
2024-01-15 10:30:45 INFO User john@example.com logged in from 192.168.1.1
```

**Structured Logging (JSON):**
```json
{
    "timestamp": "2024-01-15T10:30:45.123Z",
    "level": "INFO",
    "message": "User logged in",
    "user_email": "john@example.com",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "request_id": "abc-123",
    "duration_ms": 45
}
```

---

**Why Structured Logging:**

| Benefit | Description |
|---------|-------------|
| **Queryable** | Filter by any field (find all errors for user X) |
| **Aggregatable** | Count events, calculate averages |
| **Machine-readable** | Parse without regex |
| **Consistent** | Same format across services |
| **Context-rich** | Include metadata automatically |

---

**Implementation (Python):**

**Using structlog:**
```python
import structlog

# Configure once at startup
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Usage - key-value pairs become JSON fields
logger.info("user_login",
    user_email="john@example.com",
    ip_address="192.168.1.1",
    login_method="oauth"
)

# Output:
# {"event": "user_login", "user_email": "john@...", "level": "info", ...}
```

**Using standard logging with JSON:**
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data)

# Configure handler
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

---

**Contextual Logging:**

```python
# Bind context that persists across log calls
logger = logger.bind(
    request_id="abc-123",
    user_id=42
)

logger.info("processing_started")  # Includes request_id, user_id
logger.info("item_processed", item_id=1)  # Also includes context
logger.info("processing_completed")
```

---

**Log Aggregation Pipeline:**

```
Application -> JSON Logs -> Fluentd/Filebeat -> Elasticsearch/Loki -> Grafana/Kibana
                    |
                    v
              Query: level:ERROR AND user_id:42 AND timestamp:[now-1h TO now]
```

**Common Fields to Include:**
| Field | Purpose |
|-------|---------|
| `timestamp` | When event occurred |
| `level` | Severity (DEBUG, INFO, WARN, ERROR) |
| `message` | Human-readable description |
| `request_id` | Correlation ID for tracing |
| `user_id` | Who triggered the action |
| `service` | Which microservice |
| `duration_ms` | Performance measurement |
| `error_type` | Exception class name |
| `stack_trace` | For errors only |

## Otvet (RU)

**Текстовое логирование (традиционное):**
```
2024-01-15 10:30:45 INFO User john@example.com logged in from 192.168.1.1
```

**Структурированное логирование (JSON):**
```json
{
    "timestamp": "2024-01-15T10:30:45.123Z",
    "level": "INFO",
    "message": "User logged in",
    "user_email": "john@example.com",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "request_id": "abc-123",
    "duration_ms": 45
}
```

---

**Почему структурированное логирование:**

| Преимущество | Описание |
|--------------|----------|
| **Запрашиваемость** | Фильтрация по любому полю (найти все ошибки пользователя X) |
| **Агрегируемость** | Подсчёт событий, расчёт средних |
| **Машиночитаемость** | Парсинг без регулярных выражений |
| **Консистентность** | Одинаковый формат во всех сервисах |
| **Богатый контекст** | Автоматическое включение метаданных |

---

**Реализация (Python):**

**Используя structlog:**
```python
import structlog

# Настройка один раз при запуске
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Использование - пары ключ-значение становятся JSON-полями
logger.info("user_login",
    user_email="john@example.com",
    ip_address="192.168.1.1",
    login_method="oauth"
)

# Вывод:
# {"event": "user_login", "user_email": "john@...", "level": "info", ...}
```

**Используя стандартный logging с JSON:**
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        # Добавление дополнительных полей
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data)

# Настройка handler
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

---

**Контекстное логирование:**

```python
# Привязка контекста, который сохраняется между вызовами лога
logger = logger.bind(
    request_id="abc-123",
    user_id=42
)

logger.info("processing_started")  # Включает request_id, user_id
logger.info("item_processed", item_id=1)  # Также включает контекст
logger.info("processing_completed")
```

---

**Конвейер агрегации логов:**

```
Приложение -> JSON Logs -> Fluentd/Filebeat -> Elasticsearch/Loki -> Grafana/Kibana
                    |
                    v
              Запрос: level:ERROR AND user_id:42 AND timestamp:[now-1h TO now]
```

**Типичные поля для включения:**
| Поле | Назначение |
|------|------------|
| `timestamp` | Когда произошло событие |
| `level` | Серьёзность (DEBUG, INFO, WARN, ERROR) |
| `message` | Человекочитаемое описание |
| `request_id` | Correlation ID для трассировки |
| `user_id` | Кто инициировал действие |
| `service` | Какой микросервис |
| `duration_ms` | Измерение производительности |
| `error_type` | Имя класса исключения |
| `stack_trace` | Только для ошибок |

---

## Follow-ups
- How to implement log rotation with structured logs?
- What is the ELK stack?
- How to avoid logging sensitive data?

## Dopolnitelnye voprosy (RU)
- Как реализовать ротацию логов со структурированными логами?
- Что такое ELK-стек?
- Как избежать логирования конфиденциальных данных?

## References
- [[c-observability]]
- [[c-logging]]
- [[moc-backend]]
