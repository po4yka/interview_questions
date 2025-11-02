---
id: "20251012-000000"
title: "SQL Queries / SQL запросы"
aliases: []
summary: ""
topic: "cs"
subtopics: ["joins", "queries", "sql"]
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
tags: ["concept", "ctes", "difficulty/medium", "joins", "queries", "sql", "subqueries"]
date created: Sunday, October 12th 2025, 2:31:41 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

SQL (Structured Query Language) is the standard language for relational database management. It provides powerful query capabilities including SELECT statements, various JOIN types, subqueries, Common Table Expressions (CTEs), and window functions for data analysis and manipulation.

# Сводка (RU)

SQL (Structured Query Language) - это стандартный язык для управления реляционными базами данных. Он предоставляет мощные возможности запросов, включая операторы SELECT, различные типы JOIN, подзапросы, общие табличные выражения (CTE) и оконные функции для анализа и манипуляции данными.

## Use Cases / Trade-offs

**Use Cases:**
- Data retrieval and filtering
- Complex data aggregations
- Joining data from multiple tables
- Hierarchical data queries (recursive CTEs)
- Analytical queries (window functions)

**Trade-offs:**
- **JOINs:** Flexibility vs. performance with large datasets
- **Subqueries:** Readability vs. potential performance issues
- **CTEs:** Code clarity vs. materialization overhead
- **Window Functions:** Powerful analytics vs. complexity

## Overview

SQL (Structured Query Language) is the standard language for relational database management. This concept covers query types, joins, subqueries, CTEs, and advanced SQL techniques.

---

## Query Types

### SELECT - Data Retrieval

```sql
-- Basic SELECT
SELECT first_name, last_name, email
FROM users
WHERE is_active = true
ORDER BY created_at DESC
LIMIT 10;

-- SELECT with aggregation
SELECT
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    MAX(salary) as max_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000
ORDER BY avg_salary DESC;
```

### Joins

```sql
-- INNER JOIN: Only matching rows
SELECT u.username, o.order_id, o.total
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id;

-- LEFT JOIN: All from left + matching from right
SELECT u.username, COUNT(o.order_id) as order_count
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.username;

-- RIGHT JOIN: All from right + matching from left
SELECT o.order_id, u.username
FROM users u
RIGHT JOIN orders o ON u.user_id = o.user_id;

-- FULL OUTER JOIN: All from both
SELECT u.username, o.order_id
FROM users u
FULL OUTER JOIN orders o ON u.user_id = o.user_id;

-- CROSS JOIN: Cartesian product
SELECT p.product_name, c.category_name
FROM products p
CROSS JOIN categories c;
```

### Common Table Expressions (CTEs)

```sql
-- Single CTE
WITH recent_orders AS (
    SELECT user_id, COUNT(*) as order_count
    FROM orders
    WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    GROUP BY user_id
)
SELECT u.username, COALESCE(ro.order_count, 0) as recent_orders
FROM users u
LEFT JOIN recent_orders ro ON u.user_id = ro.user_id;

-- Multiple CTEs
WITH
user_stats AS (
    SELECT user_id, COUNT(*) as total_orders
    FROM orders
    GROUP BY user_id
),
high_value_users AS (
    SELECT user_id
    FROM user_stats
    WHERE total_orders > 10
)
SELECT u.username
FROM users u
INNER JOIN high_value_users hvu ON u.user_id = hvu.user_id;

-- Recursive CTE (tree traversal)
WITH RECURSIVE category_tree AS (
    -- Anchor member
    SELECT category_id, category_name, parent_id, 0 as level
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive member
    SELECT c.category_id, c.category_name, c.parent_id, ct.level + 1
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.category_id
)
SELECT * FROM category_tree ORDER BY level, category_name;
```

### Window Functions

```sql
-- ROW_NUMBER: Assign unique sequential numbers
SELECT
    user_id,
    username,
    ROW_NUMBER() OVER (ORDER BY created_at) as row_num
FROM users;

-- RANK: With gaps for ties
SELECT
    product_id,
    product_name,
    price,
    RANK() OVER (ORDER BY price DESC) as price_rank
FROM products;

-- DENSE_RANK: No gaps for ties
SELECT
    student_id,
    score,
    DENSE_RANK() OVER (ORDER BY score DESC) as rank
FROM exam_results;

-- PARTITION BY: Window per group
SELECT
    product_id,
    category,
    price,
    AVG(price) OVER (PARTITION BY category) as category_avg_price,
    price - AVG(price) OVER (PARTITION BY category) as diff_from_avg
FROM products;

-- LAG/LEAD: Access previous/next rows
SELECT
    order_date,
    total_sales,
    LAG(total_sales, 1) OVER (ORDER BY order_date) as prev_day_sales,
    LEAD(total_sales, 1) OVER (ORDER BY order_date) as next_day_sales
FROM daily_sales;
```

---

## Related Questions

- [[q-sql-join-algorithms-complexity--backend--hard]]

## Related Concepts

- [[c-database-design]]
- [[c-database-performance]]
- [[c-relational-databases]]

## References

- [PostgreSQL SQL Documentation](https://www.postgresql.org/docs/current/sql.html)
- [MySQL Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- [SQL Tutorial - W3Schools](https://www.w3schools.com/sql/)
- [Modern SQL](https://modern-sql.com/)

## MOC Links

- [[moc-backend]]
