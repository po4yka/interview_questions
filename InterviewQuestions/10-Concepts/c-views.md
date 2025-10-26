---
id: "20251012-000000"
title: "Database Views / Представления баз данных"
aliases: []
summary: ""
topic: "cs"
subtopics: ["database", "views", "virtual-tables"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: []
created: "2025-10-12"
updated: "2025-10-12"
tags: ["concept", "database", "views", "virtual-tables", "materialized-views", "difficulty/medium"]
---

# Summary (EN)

Views are virtual tables based on SQL queries that simplify complex queries and provide security through data abstraction. Regular views are computed on each query, while materialized views store results physically for faster access but require manual refreshing.

# Сводка (RU)

Представления - это виртуальные таблицы, основанные на SQL-запросах, которые упрощают сложные запросы и обеспечивают безопасность через абстракцию данных. Обычные представления вычисляются при каждом запросе, в то время как материализованные представления физически хранят результаты для более быстрого доступа, но требуют ручного обновления.

## Use Cases / Trade-offs

**Use Cases:**
- Simplifying complex queries
- Abstracting schema changes
- Security and access control
- Creating consistent data interfaces
- Pre-aggregated reporting data (materialized views)

**Trade-offs:**
- **Regular Views:** No storage overhead vs. recomputation on each query
- **Materialized Views:** Fast reads vs. stale data and refresh overhead
- **Abstraction:** Simplified queries vs. debugging complexity
- **Updates:** Limited UPDATE/INSERT support through views

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

## References

- [PostgreSQL Views Documentation](https://www.postgresql.org/docs/current/sql-createview.html)
- [PostgreSQL Materialized Views](https://www.postgresql.org/docs/current/sql-creatematerializedview.html)
- [MySQL Views](https://dev.mysql.com/doc/refman/8.0/en/views.html)

## MOC Links

- [[moc-backend]]
