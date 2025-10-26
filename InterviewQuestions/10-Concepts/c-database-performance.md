---
id: "20251012-000000"
title: "Database Performance Optimization / Оптимизация производительности баз данных"
aliases: []
topic: "performance"
subtopics: ["database", "indexing", "optimization", "query-tuning"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-performance"
related: []
created: "2025-10-12"
updated: "2025-10-12"
tags: ["concept", "database", "performance", "indexing", "optimization", "query-tuning"]
type: "concept"
---

# Summary (EN)

Database performance optimization involves improving query execution speed, reducing resource consumption, and ensuring scalability. Key techniques include proper indexing strategies (B-Tree, partial, covering indexes), query optimization (avoiding N+1 problems, rewriting inefficient queries), batch operations, denormalization for read-heavy workloads, connection pooling, and monitoring with slow query logs.

# Сводка (RU)

Оптимизация производительности БД включает улучшение скорости выполнения запросов, снижение потребления ресурсов и обеспечение масштабируемости. Ключевые техники включают правильные стратегии индексации (B-Tree, частичные, покрывающие индексы), оптимизацию запросов (избегание проблем N+1, переписывание неэффективных запросов), пакетные операции, денормализацию для read-heavy нагрузок, пулы соединений и мониторинг с журналами медленных запросов.

## Use Cases / Trade-offs

**Use Cases:**
- High-traffic applications
- Large dataset queries
- Real-time analytics
- OLTP systems optimization
- Report generation performance

**Trade-offs:**
- **Indexes:** Query speed vs. write performance and storage
- **Denormalization:** Read speed vs. data redundancy and update complexity
- **Caching:** Performance vs. stale data
- **Connection Pools:** Resource efficiency vs. connection limits
- **Batch Operations:** Throughput vs. latency

## Overview / Обзор

Database performance optimization involves improving query execution speed, reducing resource consumption, and ensuring scalability. Key areas include indexing, query optimization, caching, and hardware tuning.

Оптимизация производительности БД включает улучшение скорости выполнения запросов, снижение потребления ресурсов и обеспечение масштабируемости.

---

## Indexing Strategies / Стратегии индексации

### B-Tree Indexes (Default)

```sql
-- Basic index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_user_date
    ON orders(user_id, order_date DESC);

-- Query benefits
SELECT * FROM orders
WHERE user_id = 123                     -- Uses index
  AND order_date >= '2025-01-01'       -- Uses index

SELECT * FROM orders
WHERE order_date >= '2025-01-01';      -- Doesn't use composite index efficiently!
```

### Index Types

```sql
-- UNIQUE index (automatically created for PRIMARY KEY and UNIQUE constraints)
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Partial index (PostgreSQL) - smaller, faster
CREATE INDEX idx_active_users
    ON users(email)
    WHERE is_active = true AND deleted_at IS NULL;

-- Covering index (includes extra columns)
CREATE INDEX idx_orders_covering
    ON orders(user_id, order_date)
    INCLUDE (total_amount, status);

-- Query can be satisfied entirely from index
SELECT total_amount, status
FROM orders
WHERE user_id = 123 AND order_date >= '2025-01-01';

-- Full-text index
CREATE FULLTEXT INDEX idx_posts_search
    ON posts(title, content);

SELECT * FROM posts
WHERE MATCH(title, content) AGAINST ('kotlin coroutines');

-- Hash index (PostgreSQL) - O(1) for equality, no range queries
CREATE INDEX idx_users_hash
    ON users USING HASH (email);
```

### When NOT to Index

```sql
--  Don't index:
-- 1. Small tables (full scan is faster)
-- 2. Columns with low cardinality
CREATE INDEX idx_users_gender ON users(gender);  -- Only 2-3 values, not useful

-- 3. Columns frequently updated
CREATE INDEX idx_logs_message ON logs(message);  -- Logs inserted frequently

-- 4. Columns not used in WHERE, JOIN, ORDER BY
CREATE INDEX idx_users_bio ON users(bio);  -- If never queried
```

---

## Query Optimization / Оптимизация запросов

### EXPLAIN / EXPLAIN ANALYZE

```sql
-- PostgreSQL
EXPLAIN ANALYZE
SELECT u.username, COUNT(o.order_id)
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE u.created_at >= '2025-01-01'
GROUP BY u.username;

-- MySQL
EXPLAIN FORMAT=JSON
SELECT * FROM orders WHERE user_id = 123;

-- Look for:
-- - Seq Scan (bad for large tables)
-- - Index Scan (good)
-- - High cost
-- - Large estimated rows
```

### Avoiding N+1 Queries

```sql
--  N+1 Problem (1 query + N queries for each user)
SELECT * FROM users LIMIT 10;  -- 1 query
-- Then in application code:
-- for each user: SELECT * FROM orders WHERE user_id = ?  -- N queries

--  Solution: JOIN
SELECT u.*, o.order_id, o.total_amount, o.order_date
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE u.user_id IN (1, 2, 3, 4, 5);

--  Solution: Separate batch query
SELECT * FROM users LIMIT 10;
SELECT * FROM orders WHERE user_id IN (1, 2, 3, 4, 5);
```

### Query Rewriting

```sql
--  Slow: Function on indexed column
SELECT * FROM users WHERE YEAR(created_at) = 2025;

--  Fast: Use range
SELECT * FROM users
WHERE created_at >= '2025-01-01'
  AND created_at < '2026-01-01';

--  Slow: OR conditions
SELECT * FROM products WHERE category = 'A' OR category = 'B';

--  Fast: IN
SELECT * FROM products WHERE category IN ('A', 'B');

--  Slow: Wildcard at start
SELECT * FROM users WHERE email LIKE '%@gmail.com';

--  Fast: Wildcard at end (can use index)
SELECT * FROM users WHERE email LIKE 'john%';

--  Slow: NOT IN with subquery
SELECT * FROM users WHERE user_id NOT IN (SELECT user_id FROM banned_users);

--  Fast: LEFT JOIN with NULL check
SELECT u.*
FROM users u
LEFT JOIN banned_users b ON u.user_id = b.user_id
WHERE b.user_id IS NULL;
```

### Pagination

```sql
--  Slow for large offsets
SELECT * FROM posts
ORDER BY created_at DESC
LIMIT 10 OFFSET 10000;  -- Must scan 10,010 rows

--  Fast: Keyset pagination
SELECT * FROM posts
WHERE created_at < '2025-01-01 12:00:00'
ORDER BY created_at DESC
LIMIT 10;

--  Alternative: Store last ID
SELECT * FROM posts
WHERE post_id < 12345
ORDER BY post_id DESC
LIMIT 10;
```

---

## Query Patterns / Паттерны запросов

### Batch Operations

```sql
--  Slow: Multiple INSERTs
INSERT INTO users (name, email) VALUES ('User1', 'user1@example.com');
INSERT INTO users (name, email) VALUES ('User2', 'user2@example.com');
-- ... repeat 1000 times

--  Fast: Batch INSERT
INSERT INTO users (name, email) VALUES
    ('User1', 'user1@example.com'),
    ('User2', 'user2@example.com'),
    ('User3', 'user3@example.com'),
    -- ... up to 1000 rows
    ('User1000', 'user1000@example.com');

--  Fast: Batch UPDATE
UPDATE users
SET is_premium = true
WHERE user_id IN (1, 2, 3, 4, 5, ..., 1000);
```

### Denormalization for Performance

```sql
-- Normalized (slower reads)
SELECT u.username,
       COUNT(DISTINCT o.order_id) as order_count,
       SUM(o.total_amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.username;

-- Denormalized (faster reads, requires maintenance)
CREATE TABLE user_stats (
    user_id INT PRIMARY KEY,
    order_count INT DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    last_order_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Maintain with triggers
DELIMITER $$
CREATE TRIGGER update_user_stats
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    INSERT INTO user_stats (user_id, order_count, total_spent, last_order_date)
    VALUES (NEW.user_id, 1, NEW.total_amount, NEW.order_date)
    ON DUPLICATE KEY UPDATE
        order_count = order_count + 1,
        total_spent = total_spent + NEW.total_amount,
        last_order_date = NEW.order_date;
END$$
DELIMITER ;
```

### Caching Strategies

```sql
-- Materialized views (PostgreSQL)
CREATE MATERIALIZED VIEW user_order_summary AS
SELECT
    u.user_id,
    u.username,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent,
    MAX(o.order_date) as last_order_date
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.username;

-- Refresh periodically
REFRESH MATERIALIZED VIEW user_order_summary;

-- Refresh concurrently (non-blocking)
REFRESH MATERIALIZED VIEW CONCURRENTLY user_order_summary;
```

---

## Connection Pooling / Пул соединений

```kotlin
// HikariCP configuration (optimal settings)
val config = HikariConfig().apply {
    jdbcUrl = "jdbc:postgresql://localhost:5432/mydb"
    username = "user"
    password = "password"

    // Pool sizing
    maximumPoolSize = 10              // Max connections
    minimumIdle = 5                   // Min idle connections

    // Timeouts
    connectionTimeout = 30000          // 30 seconds
    idleTimeout = 600000              // 10 minutes
    maxLifetime = 1800000             // 30 minutes

    // Performance
    cachePrepStmts = true
    prepStmtCacheSize = 250
    prepStmtCacheSqlLimit = 2048

    // Health checks
    keepaliveTime = 300000            // 5 minutes
    validationTimeout = 5000          // 5 seconds
}
val dataSource = HikariDataSource(config)
```

---

## Monitoring & Analysis / Мониторинг и анализ

### Slow Query Log

```sql
-- MySQL: Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- Queries slower than 1 second
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';

-- PostgreSQL: pg_stat_statements
CREATE EXTENSION pg_stat_statements;

-- Find slowest queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Index Usage Statistics

```sql
-- PostgreSQL: Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- MySQL: Check unused indexes
SELECT
    TABLE_NAME,
    INDEX_NAME
FROM information_schema.statistics
WHERE TABLE_SCHEMA = 'mydb'
  AND NON_UNIQUE = 1
GROUP BY TABLE_NAME, INDEX_NAME;
```

---

## Related Questions

- [[q-virtual-tables-disadvantages--backend--medium]]
- [[q-sql-join-algorithms-complexity--backend--hard]]

## Related Concepts

- [[c-database-design]]
- [[c-sql-queries]]
- [[c-views]]

## References

- [Use The Index, Luke!](https://use-the-index-luke.com/)
- [PostgreSQL Performance Optimization](https://www.postgresql.org/docs/current/performance-tips.html)
- [MySQL Optimization](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)

## MOC Links

- [[moc-backend]]
