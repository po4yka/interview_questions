---
id: concept-relational-databases
title: "Relational Databases / Реляционные базы данных"
type: concept
tags: [concept, database, relational, rdbms, acid, transactions]
created: 2025-10-12
updated: 2025-10-12
---

# Relational Databases

## Overview

Relational databases organize data into tables (relations) with rows and columns. They use SQL and enforce ACID properties for data integrity.

---

## ACID Properties

### Atomicity (Атомарность)
All operations in a transaction succeed or all fail.

```sql
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- Both succeed or both rollback
```

### Consistency (Согласованность)
Database remains in valid state after transaction.

```sql
-- Constraints ensure consistency
ALTER TABLE accounts ADD CONSTRAINT chk_balance CHECK (balance >= 0);
```

### Isolation (Изолированность)
Concurrent transactions don't interfere.

```sql
-- Isolation levels
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

### Durability (Долговечность)
Committed transactions persist even after system failure.

---

## Transactions

```sql
-- Explicit transaction
BEGIN TRANSACTION;
    INSERT INTO orders (user_id, total) VALUES (123, 99.99);
    INSERT INTO order_items (order_id, product_id) VALUES (LAST_INSERT_ID(), 456);
COMMIT;

-- Rollback on error
BEGIN TRANSACTION;
    UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 456;
    -- If error occurs
    ROLLBACK;

-- Savepoints
BEGIN TRANSACTION;
    INSERT INTO logs (message) VALUES ('Step 1');
    SAVEPOINT step1;
    INSERT INTO logs (message) VALUES ('Step 2');
    ROLLBACK TO SAVEPOINT step1;  -- Undo Step 2 only
COMMIT;
```

---

## Related Concepts

- [[c-database-design]]
- [[c-database-performance]]
- [[c-migrations]]

## MOC Links

- [[moc-backend]]
