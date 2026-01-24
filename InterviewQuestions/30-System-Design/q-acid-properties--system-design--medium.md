---
id: sysdes-011
title: ACID Properties in Databases
aliases:
- ACID
- Database Transactions
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
- q-sql-nosql-databases--system-design--medium
- q-base-properties--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- difficulty/medium
- transactions
- system-design
anki_cards:
- slug: sysdes-011-0-en
  language: en
  anki_id: 1769158891241
  synced_at: '2026-01-23T13:49:17.814240'
- slug: sysdes-011-0-ru
  language: ru
  anki_id: 1769158891266
  synced_at: '2026-01-23T13:49:17.820279'
---
# Question (EN)
> What are the ACID properties in database systems? Explain each property and when they matter.

# Vopros (RU)
> Что такое свойства ACID в базах данных? Объясните каждое свойство и когда они важны.

---

## Answer (EN)

**ACID** is a set of properties that guarantee reliable processing of database transactions.

### The Four Properties

**1. Atomicity**
- Transaction is "all or nothing"
- If any part fails, entire transaction rolls back
- No partial updates left in database

```sql
-- Either both happen or neither
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

**2. Consistency**
- Database moves from one valid state to another
- All constraints, triggers, and rules are enforced
- Invariants are preserved (e.g., total balance unchanged in transfer)

**3. Isolation**
- Concurrent transactions don't interfere with each other
- Each transaction sees consistent snapshot of data
- Isolation levels: Read Uncommitted < Read Committed < Repeatable Read < Serializable

**4. Durability**
- Once committed, data survives system failures
- Typically achieved via write-ahead logging (WAL)
- Data written to non-volatile storage before commit confirmed

### When ACID Matters

| Scenario | ACID Importance |
|----------|-----------------|
| Financial transactions | Critical |
| Inventory management | High |
| User registration | High |
| Analytics/reporting | Lower (can use eventual consistency) |
| Social media feeds | Lower |

### Trade-offs

- **Performance**: ACID adds overhead (locking, logging)
- **Scalability**: Harder to distribute ACID-compliant systems
- **Availability**: Strict consistency can reduce availability (CAP theorem)

---

## Otvet (RU)

**ACID** - набор свойств, гарантирующих надежную обработку транзакций базы данных.

### Четыре свойства

**1. Атомарность (Atomicity)**
- Транзакция выполняется "все или ничего"
- При сбое любой части вся транзакция откатывается
- Частичные обновления не остаются в базе

```sql
-- Либо оба запроса выполнятся, либо ни один
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

**2. Согласованность (Consistency)**
- База переходит из одного валидного состояния в другое
- Все ограничения, триггеры и правила соблюдаются
- Инварианты сохраняются (например, общий баланс при переводе)

**3. Изолированность (Isolation)**
- Параллельные транзакции не влияют друг на друга
- Каждая транзакция видит согласованный снимок данных
- Уровни изоляции: Read Uncommitted < Read Committed < Repeatable Read < Serializable

**4. Долговечность (Durability)**
- После коммита данные переживают сбои системы
- Обычно достигается через журнал упреждающей записи (WAL)
- Данные записываются на диск до подтверждения коммита

### Когда ACID важен

| Сценарий | Важность ACID |
|----------|---------------|
| Финансовые транзакции | Критически важен |
| Управление запасами | Высокая |
| Регистрация пользователей | Высокая |
| Аналитика/отчеты | Ниже (можно использовать eventual consistency) |
| Ленты соцсетей | Ниже |

### Компромиссы

- **Производительность**: ACID добавляет накладные расходы (блокировки, логирование)
- **Масштабируемость**: Сложнее распределить ACID-совместимые системы
- **Доступность**: Строгая согласованность может снизить доступность (CAP теорема)

---

## Follow-ups

- What are the different isolation levels and their trade-offs?
- How does write-ahead logging (WAL) ensure durability?
- Compare ACID vs BASE properties

## Related Questions

### Prerequisites (Easier)
- [[q-sql-nosql-databases--system-design--medium]] - Database fundamentals

### Related (Same Level)
- [[q-base-properties--system-design--medium]] - BASE properties
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Database scaling
