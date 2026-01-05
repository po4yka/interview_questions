---
id: "20251012-000000"
title: "Database Migrations / Миграции баз данных"
aliases: []
summary: ""
topic: "cs"
subtopics: ["database", "migrations", "schema"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: [c-room-library, c-sqlite, c-database-design, c-relational-databases, c-database-performance]
created: "2025-10-12"
updated: "2025-10-12"
tags: ["concept", "database", "difficulty/medium", "migrations", "schema", "versioning"]
---

# Summary (EN)

Database migrations are version-controlled schema changes that can be applied and rolled back systematically. They enable safe database evolution in production environments through forward migrations (applying changes) and rollback migrations (reverting changes). Key patterns include additive changes (safe), breaking changes (requires careful planning), and zero-downtime migrations for high-availability systems.

# Сводка (RU)

Миграции баз данных - это версионированные изменения схемы, которые могут быть применены и откачены систематически. Они обеспечивают безопасную эволюцию базы данных в production-среде через прямые миграции (применение изменений) и откат миграций (отмена изменений). Ключевые паттерны включают аддитивные изменения (безопасные), ломающие изменения (требуют тщательного планирования) и миграции без простоя для высокодоступных систем.

## Use Cases / Trade-offs

**Use Cases:**
- Schema evolution in production
- Synchronized database changes across environments
- Rollback capability for failed deployments
- Team collaboration on database changes
- Database versioning and history

**Trade-offs:**
- **Additive vs Breaking Changes:** Safe additions vs. complex multi-step migrations
- **Automatic vs Manual:** Automated migrations vs. manual control for critical changes
- **Up/Down Migrations:** Bidirectional changes vs. forward-only migrations
- **Zero-Downtime:** Application complexity vs. continuous availability

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

## References

- [Flyway Database Migrations](https://flywaydb.org/)
- [Liquibase Documentation](https://www.liquibase.org/)
- [Refactoring Databases](https://databaserefactoring.com/)
- "Refactoring Databases: Evolutionary Database Design" by Scott W. Ambler and Pramod J. Sadalage

## MOC Links

- [[moc-backend]]
