---
id: cs-db-sql
title: Database - SQL Fundamentals
topic: database
difficulty: medium
tags:
- cs_database
- sql
anki_cards:
- slug: cs-db-sql-0-en
  language: en
  anki_id: 1769160676324
  synced_at: '2026-01-23T13:31:18.930524'
- slug: cs-db-sql-0-ru
  language: ru
  anki_id: 1769160676349
  synced_at: '2026-01-23T13:31:18.932160'
- slug: cs-db-sql-1-en
  language: en
  anki_id: 1769160676374
  synced_at: '2026-01-23T13:31:18.933498'
- slug: cs-db-sql-1-ru
  language: ru
  anki_id: 1769160676399
  synced_at: '2026-01-23T13:31:18.934627'
- slug: cs-db-sql-2-en
  language: en
  anki_id: 1769160676426
  synced_at: '2026-01-23T13:31:18.935965'
- slug: cs-db-sql-2-ru
  language: ru
  anki_id: 1769160676451
  synced_at: '2026-01-23T13:31:18.937452'
---
# SQL Fundamentals

## SQL Basics

### SELECT Queries

```sql
-- Basic SELECT
SELECT column1, column2 FROM table_name;

-- All columns
SELECT * FROM users;

-- With alias
SELECT first_name AS name, email AS contact FROM users;

-- Distinct values
SELECT DISTINCT country FROM customers;

-- Limit results
SELECT * FROM users LIMIT 10;
SELECT * FROM users LIMIT 10 OFFSET 20;  -- Pagination
```

### WHERE Clause

```sql
-- Comparison operators
SELECT * FROM users WHERE age > 18;
SELECT * FROM users WHERE status = 'active';
SELECT * FROM users WHERE created_at >= '2024-01-01';

-- Logical operators
SELECT * FROM users WHERE age > 18 AND status = 'active';
SELECT * FROM users WHERE country = 'US' OR country = 'CA';
SELECT * FROM users WHERE NOT is_deleted;

-- IN operator
SELECT * FROM users WHERE country IN ('US', 'CA', 'UK');

-- BETWEEN
SELECT * FROM orders WHERE total BETWEEN 100 AND 500;

-- LIKE pattern matching
SELECT * FROM users WHERE email LIKE '%@gmail.com';
SELECT * FROM users WHERE name LIKE 'John%';  -- Starts with
SELECT * FROM users WHERE name LIKE '%son';   -- Ends with
SELECT * FROM users WHERE name LIKE '_ohn';   -- Single char wildcard

-- NULL checks
SELECT * FROM users WHERE phone IS NULL;
SELECT * FROM users WHERE phone IS NOT NULL;
```

### ORDER BY

```sql
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM users ORDER BY last_name ASC, first_name ASC;
SELECT * FROM users ORDER BY age DESC NULLS LAST;
```

## JOINs

### INNER JOIN

Returns only matching rows from both tables.

```sql
SELECT orders.id, users.name, orders.total
FROM orders
INNER JOIN users ON orders.user_id = users.id;
```

### LEFT JOIN (LEFT OUTER JOIN)

Returns all rows from left table, matching rows from right (NULL if no match).

```sql
SELECT users.name, orders.total
FROM users
LEFT JOIN orders ON users.id = orders.user_id;
-- Users without orders will have NULL for orders.total
```

### RIGHT JOIN (RIGHT OUTER JOIN)

Returns all rows from right table, matching rows from left.

```sql
SELECT users.name, orders.total
FROM users
RIGHT JOIN orders ON users.id = orders.user_id;
```

### FULL OUTER JOIN

Returns all rows from both tables.

```sql
SELECT users.name, orders.total
FROM users
FULL OUTER JOIN orders ON users.id = orders.user_id;
```

### CROSS JOIN

Cartesian product - every row with every row.

```sql
SELECT colors.name, sizes.name
FROM colors
CROSS JOIN sizes;
```

### Self JOIN

Table joined with itself.

```sql
-- Find employees and their managers
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

### JOIN Visualization

```
INNER JOIN:        LEFT JOIN:         FULL OUTER:
   A   B              A   B              A   B
  (  X  )           (  X  ]            [  X  ]
     ^               ^  ^              ^     ^
   Both            All A            All A & B
```

## Aggregation

### Aggregate Functions

```sql
SELECT COUNT(*) FROM users;                    -- Count rows
SELECT COUNT(DISTINCT country) FROM users;     -- Count unique
SELECT SUM(total) FROM orders;                 -- Sum
SELECT AVG(age) FROM users;                    -- Average
SELECT MIN(created_at), MAX(created_at) FROM users;
```

### GROUP BY

```sql
-- Count users per country
SELECT country, COUNT(*) AS user_count
FROM users
GROUP BY country;

-- Total sales per customer
SELECT user_id, SUM(total) AS total_spent
FROM orders
GROUP BY user_id;

-- Multiple columns
SELECT country, city, COUNT(*)
FROM users
GROUP BY country, city;
```

### HAVING (Filter groups)

```sql
-- Countries with more than 100 users
SELECT country, COUNT(*) AS user_count
FROM users
GROUP BY country
HAVING COUNT(*) > 100;

-- Customers who spent more than $1000
SELECT user_id, SUM(total) AS total_spent
FROM orders
GROUP BY user_id
HAVING SUM(total) > 1000;
```

### WHERE vs HAVING

```sql
-- WHERE filters rows BEFORE grouping
-- HAVING filters groups AFTER grouping

SELECT country, COUNT(*) AS user_count
FROM users
WHERE status = 'active'      -- Filter individual rows
GROUP BY country
HAVING COUNT(*) > 100;       -- Filter groups
```

## Subqueries

### Scalar Subquery

Returns single value.

```sql
SELECT name, salary,
       (SELECT AVG(salary) FROM employees) AS avg_salary
FROM employees;
```

### IN Subquery

```sql
-- Users who have placed orders
SELECT * FROM users
WHERE id IN (SELECT DISTINCT user_id FROM orders);
```

### EXISTS Subquery

```sql
-- Users with at least one order
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

### Correlated Subquery

References outer query.

```sql
-- Employees earning more than department average
SELECT * FROM employees e
WHERE salary > (
    SELECT AVG(salary) FROM employees
    WHERE department_id = e.department_id
);
```

### FROM Subquery (Derived Table)

```sql
SELECT avg_by_dept.department, avg_by_dept.avg_salary
FROM (
    SELECT department_id, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department_id
) AS avg_by_dept
WHERE avg_by_dept.avg_salary > 50000;
```

## Common Table Expressions (CTE)

```sql
WITH high_value_orders AS (
    SELECT user_id, SUM(total) AS total_spent
    FROM orders
    GROUP BY user_id
    HAVING SUM(total) > 1000
)
SELECT u.name, h.total_spent
FROM users u
JOIN high_value_orders h ON u.id = h.user_id;
```

### Recursive CTE

```sql
-- Organizational hierarchy
WITH RECURSIVE org_tree AS (
    -- Base case: top-level employees
    SELECT id, name, manager_id, 0 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case
    SELECT e.id, e.name, e.manager_id, t.level + 1
    FROM employees e
    JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree;
```

## Window Functions

```sql
-- Row number
SELECT name, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- Rank (with gaps for ties)
SELECT name, salary,
       RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- Dense rank (no gaps)
SELECT name, salary,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- Partition by department
SELECT name, department, salary,
       RANK() OVER (PARTITION BY department ORDER BY salary DESC)
FROM employees;

-- Running total
SELECT date, amount,
       SUM(amount) OVER (ORDER BY date) AS running_total
FROM transactions;

-- Moving average
SELECT date, amount,
       AVG(amount) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
FROM transactions;
```

## Data Modification

### INSERT

```sql
INSERT INTO users (name, email) VALUES ('John', 'john@example.com');

-- Multiple rows
INSERT INTO users (name, email) VALUES
    ('John', 'john@example.com'),
    ('Jane', 'jane@example.com');

-- Insert from select
INSERT INTO archive_orders
SELECT * FROM orders WHERE created_at < '2023-01-01';
```

### UPDATE

```sql
UPDATE users SET status = 'inactive' WHERE last_login < '2023-01-01';

-- Update with join
UPDATE orders o
SET o.status = 'cancelled'
FROM users u
WHERE o.user_id = u.id AND u.is_banned = true;
```

### DELETE

```sql
DELETE FROM users WHERE status = 'deleted';

-- Delete with join
DELETE FROM orders
USING users
WHERE orders.user_id = users.id AND users.is_banned = true;
```

### UPSERT (INSERT ON CONFLICT)

```sql
-- PostgreSQL
INSERT INTO users (email, name) VALUES ('john@example.com', 'John')
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name;

-- MySQL
INSERT INTO users (email, name) VALUES ('john@example.com', 'John')
ON DUPLICATE KEY UPDATE name = VALUES(name);
```

## Interview Questions

1. **What's the difference between WHERE and HAVING?**
   - WHERE filters rows before aggregation
   - HAVING filters groups after aggregation

2. **When to use JOIN vs subquery?**
   - JOIN: Need columns from multiple tables
   - Subquery: Filter or single value calculation
   - JOINs often more efficient

3. **Explain different types of JOINs**
   - INNER: Only matching rows
   - LEFT: All from left, matching from right
   - RIGHT: All from right, matching from left
   - FULL: All from both
   - CROSS: Cartesian product
