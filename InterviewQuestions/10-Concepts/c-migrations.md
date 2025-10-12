---
id: concept-migrations
title: "Database Migrations / Миграции баз данных"
type: concept
tags: [concept, database, migrations, schema, versioning]
created: 2025-10-12
updated: 2025-10-12
---

# Database Migrations

## Overview

Database migrations are version-controlled schema changes that can be applied and rolled back systematically.

---

## Migration Patterns

### Forward Migration

```sql
-- V001__create_users_table.sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Rollback Migration

```sql
-- V001__create_users_table_down.sql
DROP TABLE IF EXISTS users;
```

### Additive Changes (Safe)

```sql
-- Adding column with default
ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;

-- Adding index
CREATE INDEX idx_users_email ON users(email);
```

### Breaking Changes (Dangerous)

```sql
-- Renaming column (requires data migration)
ALTER TABLE users RENAME COLUMN username TO user_name;

-- Changing data type
ALTER TABLE users MODIFY COLUMN email VARCHAR(200);
```

---

## Zero-Downtime Migrations

```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN new_email VARCHAR(200);

-- Step 2: Dual-write (application code)
-- Write to both old_email and new_email

-- Step 3: Backfill data
UPDATE users SET new_email = old_email WHERE new_email IS NULL;

-- Step 4: Switch reads (application code)
-- Read from new_email

-- Step 5: Remove old column
ALTER TABLE users DROP COLUMN old_email;
```

---

## Related Questions

- [[q-database-migration-purpose--backend--medium]]

## Related Concepts

- [[c-database-design]]
- [[c-relational-databases]]

## MOC Links

- [[moc-backend]]
