---
id: sysdes-072
title: Change Data Capture (CDC)
aliases:
- Change Data Capture
- CDC
- Database Streaming
topic: system-design
subtopics:
- data-management
- integration
- streaming
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-event-sourcing--system-design--hard
- q-message-queues--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- data-management
- difficulty/medium
- integration
- system-design
anki_cards:
- slug: sysdes-072-0-en
  language: en
  anki_id: 1769161753029
  synced_at: '2026-01-23T13:49:17.736328'
- slug: sysdes-072-0-ru
  language: ru
  anki_id: 1769161753056
  synced_at: '2026-01-23T13:49:17.737910'
---
# Question (EN)
> What is Change Data Capture (CDC)? How is it used to keep systems synchronized?

# Vopros (RU)
> Что такое Change Data Capture (CDC)? Как его используют для синхронизации систем?

---

## Answer (EN)

**Change Data Capture (CDC)** is a pattern for tracking changes in a database and streaming them to other systems in real-time or near-real-time.

### How CDC Works

```
Traditional Approach (Polling):
Application → Query DB every N seconds → Detect changes → Propagate
             (inefficient, misses deletes, timestamp issues)

CDC Approach (Log-based):
Database writes → Transaction log (WAL) → CDC captures → Stream to consumers
                                         │
                                         ▼
                              Kafka/Kinesis/Pulsar
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
              Search Index          Cache              Analytics
              (Elasticsearch)       (Redis)            (Data Warehouse)
```

### CDC Methods

| Method | How It Works | Pros/Cons |
|--------|--------------|-----------|
| **Log-based** | Read database transaction log (WAL/binlog) | Most reliable, no table changes, low overhead |
| **Trigger-based** | DB triggers write to change table | Works everywhere, adds overhead |
| **Timestamp-based** | Query by updated_at column | Simple, misses deletes, clock issues |
| **Diff-based** | Compare snapshots | Works offline, resource intensive |

### Log-based CDC (Preferred)

```
PostgreSQL:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Table     │ --> │  WAL Log    │ --> │   Debezium  │ --> Kafka
│  INSERT     │     │ (Write-Ahead│     │   (CDC)     │
│  UPDATE     │     │    Log)     │     │             │
│  DELETE     │     └─────────────┘     └─────────────┘
└─────────────┘

MySQL:
Table changes --> Binlog --> Debezium --> Kafka

Each change event contains:
{
  "op": "u",           // c=create, u=update, d=delete
  "before": {...},     // previous state (for update/delete)
  "after": {...},      // new state (for create/update)
  "source": {
    "table": "users",
    "ts_ms": 1234567890
  }
}
```

### Common Use Cases

| Use Case | Description |
|----------|-------------|
| **Cache invalidation** | Update Redis when DB changes |
| **Search indexing** | Keep Elasticsearch in sync |
| **Data replication** | Sync to data warehouse |
| **Microservices** | Propagate changes across services |
| **Audit logging** | Track all changes for compliance |
| **Event sourcing** | Build event stream from DB changes |

### Popular CDC Tools

| Tool | Databases | Output |
|------|-----------|--------|
| **Debezium** | PostgreSQL, MySQL, MongoDB, SQL Server | Kafka |
| **AWS DMS** | Most databases | Kinesis, S3 |
| **Fivetran** | Many sources | Data warehouses |
| **Maxwell** | MySQL only | Kafka, Kinesis |

### Architecture Example

```
┌─────────────────────────────────────────────────────────────┐
│                     Order Service                            │
│  ┌─────────┐                                                │
│  │ Orders  │ --> Debezium --> Kafka topic: orders.changes   │
│  │   DB    │                         │                      │
│  └─────────┘                         │                      │
└──────────────────────────────────────┼──────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────┐
              ▼                        ▼                    ▼
       ┌──────────┐            ┌──────────┐          ┌──────────┐
       │ Analytics│            │  Search  │          │Inventory │
       │ Service  │            │ Service  │          │ Service  │
       │(Snowflake)│           │(Elastic) │          │(Update   │
       └──────────┘            └──────────┘          │ stock)   │
                                                     └──────────┘
```

### Benefits and Challenges

| Benefits | Challenges |
|----------|------------|
| Real-time sync | Schema evolution handling |
| No polling overhead | Initial snapshot complexity |
| Captures all changes including deletes | Ordering guarantees |
| Decouples systems | Exactly-once delivery |

---

## Otvet (RU)

**Change Data Capture (CDC)** - паттерн для отслеживания изменений в базе данных и потоковой передачи их в другие системы в реальном времени.

### Как работает CDC

```
Традиционный подход (Polling):
Приложение → Запрос к БД каждые N секунд → Обнаружение изменений
            (неэффективно, пропускает удаления)

CDC подход (на основе логов):
Записи в БД → Transaction log (WAL) → CDC захватывает → Поток потребителям
                                              │
                                              ▼
                                      Kafka/Kinesis
                                              │
                         ┌────────────────────┼───────────────────┐
                         ▼                    ▼                   ▼
                   Поисковый индекс         Кеш              Аналитика
```

### Методы CDC

| Метод | Как работает | Плюсы/Минусы |
|-------|--------------|--------------|
| **Log-based** | Чтение transaction log (WAL/binlog) | Надёжный, низкие накладные расходы |
| **Trigger-based** | Триггеры БД пишут в таблицу изменений | Работает везде, добавляет нагрузку |
| **Timestamp-based** | Запрос по колонке updated_at | Просто, пропускает удаления |
| **Diff-based** | Сравнение снимков | Работает офлайн, ресурсоёмко |

### Log-based CDC (предпочтительный)

```
PostgreSQL:
Таблица → WAL Log → Debezium → Kafka

MySQL:
Таблица → Binlog → Debezium → Kafka

Каждое событие содержит:
{
  "op": "u",           // c=create, u=update, d=delete
  "before": {...},     // предыдущее состояние
  "after": {...},      // новое состояние
  "source": {"table": "users", "ts_ms": 1234567890}
}
```

### Типичные применения

| Применение | Описание |
|------------|----------|
| **Инвалидация кеша** | Обновление Redis при изменениях в БД |
| **Поисковая индексация** | Синхронизация с Elasticsearch |
| **Репликация данных** | Синхронизация с data warehouse |
| **Микросервисы** | Распространение изменений между сервисами |
| **Аудит** | Отслеживание всех изменений |

### Популярные инструменты CDC

| Инструмент | Базы данных | Выход |
|------------|-------------|-------|
| **Debezium** | PostgreSQL, MySQL, MongoDB | Kafka |
| **AWS DMS** | Большинство БД | Kinesis, S3 |
| **Maxwell** | Только MySQL | Kafka, Kinesis |

### Преимущества и сложности

| Преимущества | Сложности |
|--------------|-----------|
| Синхронизация в реальном времени | Обработка изменений схемы |
| Нет накладных расходов на polling | Сложность начального снимка |
| Захватывает все изменения включая удаления | Гарантии порядка |
| Развязывает системы | Exactly-once доставка |

---

## Follow-ups

- How do you handle schema changes in CDC pipelines?
- What is the Outbox pattern and how does it relate to CDC?
- How do you ensure exactly-once delivery with CDC?
