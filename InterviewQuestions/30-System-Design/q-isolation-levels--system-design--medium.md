---
id: sysdes-031
title: Database Isolation Levels
aliases:
- Isolation Levels
- Transaction Isolation
topic: system-design
subtopics:
- databases
- transactions
- consistency
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-acid-properties--system-design--medium
- q-consistency-models--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- difficulty/medium
- transactions
- system-design
anki_cards:
- slug: sysdes-031-0-en
  language: en
  anki_id: 1769159521093
  synced_at: '2026-01-23T13:49:17.780581'
- slug: sysdes-031-0-ru
  language: ru
  anki_id: 1769159521120
  synced_at: '2026-01-23T13:49:17.782494'
---
# Question (EN)
> What are the database isolation levels? Explain the trade-offs between Read Uncommitted, Read Committed, Repeatable Read, and Serializable.

# Vopros (RU)
> Какие уровни изоляции транзакций существуют в базах данных? Объясните компромиссы между Read Uncommitted, Read Committed, Repeatable Read и Serializable.

---

## Answer (EN)

**Isolation levels** define how transactions interact with each other and what anomalies are prevented.

### Isolation Levels (Weakest to Strongest)

**1. Read Uncommitted**
- Can read uncommitted changes from other transactions
- Allows: Dirty reads, Non-repeatable reads, Phantom reads
- Use case: Rarely used, approximate counts

**2. Read Committed** (PostgreSQL default)
- Only reads committed data
- Prevents: Dirty reads
- Allows: Non-repeatable reads, Phantom reads
- Most common in practice

**3. Repeatable Read** (MySQL InnoDB default)
- Same row returns same value within transaction
- Prevents: Dirty reads, Non-repeatable reads
- Allows: Phantom reads (new rows can appear)

**4. Serializable**
- Transactions execute as if serial
- Prevents: All anomalies
- Highest consistency, lowest concurrency

### Read Anomalies

| Anomaly | Description |
|---------|-------------|
| Dirty read | Read uncommitted data that may rollback |
| Non-repeatable read | Same query returns different values |
| Phantom read | New rows appear matching query criteria |

### Comparison Table

| Level | Dirty Read | Non-Repeatable | Phantom | Performance |
|-------|------------|----------------|---------|-------------|
| Read Uncommitted | Yes | Yes | Yes | Fastest |
| Read Committed | No | Yes | Yes | Fast |
| Repeatable Read | No | No | Yes | Medium |
| Serializable | No | No | No | Slowest |

### Implementation Mechanisms

- **Locking**: Shared/exclusive locks on rows/tables
- **MVCC**: Multiple versions, snapshot isolation
- **Optimistic**: Validate at commit time

---

## Otvet (RU)

**Уровни изоляции** определяют, как транзакции взаимодействуют друг с другом и какие аномалии предотвращаются.

### Уровни изоляции (от слабого к сильному)

**1. Read Uncommitted**
- Может читать незакоммиченные изменения других транзакций
- Допускает: Грязное чтение, Неповторяемое чтение, Фантомное чтение
- Применение: Редко используется, приблизительные подсчеты

**2. Read Committed** (PostgreSQL по умолчанию)
- Читает только закоммиченные данные
- Предотвращает: Грязное чтение
- Допускает: Неповторяемое чтение, Фантомное чтение
- Наиболее распространен на практике

**3. Repeatable Read** (MySQL InnoDB по умолчанию)
- Та же строка возвращает то же значение в рамках транзакции
- Предотвращает: Грязное чтение, Неповторяемое чтение
- Допускает: Фантомное чтение (могут появиться новые строки)

**4. Serializable**
- Транзакции выполняются как последовательные
- Предотвращает: Все аномалии
- Наивысшая согласованность, наименьшая конкурентность

### Аномалии чтения

| Аномалия | Описание |
|----------|----------|
| Грязное чтение | Чтение незакоммиченных данных, которые могут откатиться |
| Неповторяемое чтение | Тот же запрос возвращает разные значения |
| Фантомное чтение | Появляются новые строки, соответствующие критериям |

### Сравнительная таблица

| Уровень | Грязное | Неповторяемое | Фантомное | Производительность |
|---------|---------|---------------|-----------|-------------------|
| Read Uncommitted | Да | Да | Да | Быстрейший |
| Read Committed | Нет | Да | Да | Быстрый |
| Repeatable Read | Нет | Нет | Да | Средний |
| Serializable | Нет | Нет | Нет | Медленнейший |

---

## Follow-ups

- How does MVCC implement isolation levels?
- What is snapshot isolation?
- How do you choose the right isolation level?
