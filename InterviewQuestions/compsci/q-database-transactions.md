---
id: cs-db-transactions
title: Database - Transactions and Concurrency
topic: database
difficulty: hard
tags:
- cs_database
- transactions
- concurrency
anki_cards:
- slug: cs-db-tx-0-en
  language: en
  anki_id: 1769160674424
  synced_at: '2026-01-23T13:31:18.821075'
- slug: cs-db-tx-0-ru
  language: ru
  anki_id: 1769160674450
  synced_at: '2026-01-23T13:31:18.823004'
- slug: cs-db-tx-1-en
  language: en
  anki_id: 1769160674474
  synced_at: '2026-01-23T13:31:18.824566'
- slug: cs-db-tx-1-ru
  language: ru
  anki_id: 1769160674499
  synced_at: '2026-01-23T13:31:18.826183'
- slug: cs-db-tx-2-en
  language: en
  anki_id: 1769160674524
  synced_at: '2026-01-23T13:31:18.827473'
- slug: cs-db-tx-2-ru
  language: ru
  anki_id: 1769160674549
  synced_at: '2026-01-23T13:31:18.828920'
---
# Transactions and Concurrency

## ACID Properties

### Atomicity

All or nothing - transaction either completes fully or rolls back entirely.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- Both happen or neither
```

### Consistency

Transaction brings database from one valid state to another.

Constraints, triggers, and rules maintained.

### Isolation

Concurrent transactions don't interfere with each other.

Each transaction sees consistent snapshot.

### Durability

Committed transactions survive system failures.

Write-ahead logging (WAL) ensures recovery.

## Isolation Levels

### Read Phenomena

| Phenomenon | Description |
|------------|-------------|
| **Dirty Read** | Read uncommitted data from another transaction |
| **Non-repeatable Read** | Same query returns different data (row modified) |
| **Phantom Read** | Same query returns different rows (rows added/deleted) |

### Isolation Level Comparison

| Level | Dirty Read | Non-repeatable | Phantom |
|-------|------------|----------------|---------|
| Read Uncommitted | Yes | Yes | Yes |
| Read Committed | No | Yes | Yes |
| Repeatable Read | No | No | Yes |
| Serializable | No | No | No |

### Read Uncommitted

```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Transaction A
BEGIN;
UPDATE products SET price = 100 WHERE id = 1;
-- Not committed yet

-- Transaction B can see price = 100 (dirty read)
SELECT price FROM products WHERE id = 1;
```

### Read Committed (Default in PostgreSQL)

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Only sees committed data
-- But same query can return different values if other tx commits
```

### Repeatable Read

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Same query returns same rows throughout transaction
-- But new rows (phantoms) may appear
```

### Serializable

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Transactions execute as if serial (one after another)
-- Strictest isolation, lowest concurrency
```

## Locking

### Lock Types

| Lock | Also Called | Allows | Blocks |
|------|-------------|--------|--------|
| Shared (S) | Read lock | Other S locks | X locks |
| Exclusive (X) | Write lock | Nothing | All locks |

### Lock Granularity

| Level | Description | Concurrency | Overhead |
|-------|-------------|-------------|----------|
| Row | Lock individual rows | High | High |
| Page | Lock data page | Medium | Medium |
| Table | Lock entire table | Low | Low |

### Pessimistic Locking

Lock before access, assume conflicts.

```sql
-- Lock row for update
SELECT * FROM products WHERE id = 1 FOR UPDATE;
UPDATE products SET stock = stock - 1 WHERE id = 1;
COMMIT;
```

### Optimistic Locking

No locks, detect conflicts at commit.

```sql
-- Check version before update
SELECT id, stock, version FROM products WHERE id = 1;
-- Application: version = 5, stock = 100

UPDATE products
SET stock = 99, version = 6
WHERE id = 1 AND version = 5;
-- Fails if version changed (0 rows updated)
```

### Lock Modes in PostgreSQL

```sql
SELECT * FROM t FOR UPDATE;         -- Exclusive row lock
SELECT * FROM t FOR NO KEY UPDATE;  -- Weaker exclusive (allows foreign key checks)
SELECT * FROM t FOR SHARE;          -- Shared lock
SELECT * FROM t FOR KEY SHARE;      -- Weakest shared lock
```

## Deadlocks

Two or more transactions waiting for each other.

```
Transaction A: Holds lock on row 1, wants lock on row 2
Transaction B: Holds lock on row 2, wants lock on row 1
= Deadlock!
```

### Prevention

1. **Access order**: Always lock resources in same order
2. **Lock timeout**: Give up after waiting too long
3. **Deadlock detection**: Database kills one transaction

```sql
-- Set lock timeout
SET lock_timeout = '5s';
```

## MVCC (Multi-Version Concurrency Control)

Readers don't block writers, writers don't block readers.

Each transaction sees snapshot of data.

### How It Works

```
Row versions:
  Version 1: created by TX 100, deleted by TX 150
  Version 2: created by TX 150, active

Transaction 120 sees Version 1
Transaction 200 sees Version 2
```

**PostgreSQL**: Keeps old versions in table (requires VACUUM).
**MySQL InnoDB**: Keeps old versions in undo log.

## Transaction Management

### Savepoints

Partial rollback within transaction.

```sql
BEGIN;
INSERT INTO orders VALUES (1, 100);
SAVEPOINT sp1;
INSERT INTO order_items VALUES (1, 1, 10);
-- Error occurs
ROLLBACK TO sp1;  -- Undo items, keep order
INSERT INTO order_items VALUES (1, 2, 20);  -- Retry
COMMIT;
```

### Autocommit

Each statement is its own transaction (default in many DBs).

```sql
SET autocommit = 0;  -- Disable
-- Statements now need explicit COMMIT
```

## Distributed Transactions

### Two-Phase Commit (2PC)

```
Phase 1 (Prepare):
  Coordinator -> All participants: "Prepare to commit"
  Participants -> Coordinator: "Ready" or "Abort"

Phase 2 (Commit):
  If all ready:
    Coordinator -> All: "Commit"
  Else:
    Coordinator -> All: "Rollback"
```

**Problems**: Blocking if coordinator fails.

### Saga Pattern

Long-running transactions with compensating actions.

```
Transaction: Order -> Payment -> Inventory -> Shipping

If Payment fails:
  Compensate: Cancel Order

If Inventory fails:
  Compensate: Refund Payment
  Compensate: Cancel Order
```

## Best Practices

1. **Keep transactions short**: Reduce lock contention
2. **Access resources in consistent order**: Prevent deadlocks
3. **Use appropriate isolation level**: Balance consistency vs concurrency
4. **Handle deadlocks**: Retry on deadlock error
5. **Avoid long-running transactions**: Use batching
6. **Monitor lock waits**: Identify contention issues

## Interview Questions

1. **What are ACID properties?**
   - Atomicity: All or nothing
   - Consistency: Valid state to valid state
   - Isolation: Transactions don't interfere
   - Durability: Committed data survives crashes

2. **Difference between pessimistic and optimistic locking?**
   - Pessimistic: Lock before access, blocks others
   - Optimistic: No locks, check version at commit
   - Pessimistic for high contention
   - Optimistic for low contention

3. **What is a deadlock and how to prevent?**
   - Circular wait between transactions
   - Prevention: consistent lock order, timeouts
   - Detection: database auto-detects and kills one

4. **What is MVCC?**
   - Multi-Version Concurrency Control
   - Multiple versions of rows
   - Readers see snapshot
   - No read-write blocking
