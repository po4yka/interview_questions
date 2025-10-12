---
id: concept-views
title: "Database Views / Представления баз данных"
type: concept
tags: [concept, database, views, virtual-tables, materialized-views]
created: 2025-10-12
updated: 2025-10-12
---

# Database Views

## Overview

Views are virtual tables based on SQL queries. They simplify complex queries and provide security through data abstraction.

---

## Regular Views

```sql
-- Create view
CREATE VIEW active_users AS
SELECT user_id, username, email
FROM users
WHERE is_active = TRUE AND deleted_at IS NULL;

-- Use view
SELECT * FROM active_users WHERE username LIKE 'john%';

-- Views are computed on each query (no storage)
```

## Materialized Views

```sql
-- PostgreSQL: Store query results physically
CREATE MATERIALIZED VIEW user_order_summary AS
SELECT
    u.user_id,
    u.username,
    COUNT(o.order_id) as order_count,
    SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.username;

-- Refresh manually
REFRESH MATERIALIZED VIEW user_order_summary;

-- Refresh concurrently (non-blocking)
REFRESH MATERIALIZED VIEW CONCURRENTLY user_order_summary;
```

## Advantages

- Simplify complex queries
- Abstract underlying schema
- Security (limit column access)
- Consistent interface

## Disadvantages

- Performance overhead (regular views)
- Stale data (materialized views)
- Cannot index regular views
- Limited UPDATE/INSERT support

---

## Related Questions

- [[q-virtual-tables-disadvantages--backend--medium]]

## Related Concepts

- [[c-database-performance]]
- [[c-sql-queries]]

## MOC Links

- [[moc-backend]]
