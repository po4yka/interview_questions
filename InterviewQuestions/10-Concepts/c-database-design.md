---
id: "20251012-000000"
title: "Database Design Principles / Принципы проектирования баз данных"
aliases: []
summary: ""
topic: "cs"
subtopics: ["database", "design", "normalization"]
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
tags: ["concept", "database", "design", "difficulty/medium", "normalization", "relational", "schema"]
date created: Sunday, October 12th 2025, 2:28:05 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

Database design is the process of organizing data according to a database model. Good database design is essential for data integrity, performance, scalability, maintainability, and query efficiency. Key principles include normalization, entity-relationship modeling, proper constraints, and indexing strategies.

# Сводка (RU)

Проектирование базы данных - это процесс организации данных в соответствии с моделью базы данных. Хорошее проектирование БД необходимо для обеспечения целостности данных, производительности, масштабируемости, поддерживаемости и эффективности запросов. Ключевые принципы включают нормализацию, моделирование сущность-связь, правильные ограничения и стратегии индексации.

## Use Cases / Trade-offs

**Use Cases:**
- Transactional systems (OLTP)
- Data warehousing (OLAP)
- Application databases
- Content management systems
- E-commerce platforms

**Trade-offs:**
- **Normalization:** Better data integrity vs. query performance
- **Denormalization:** Faster reads vs. data redundancy and update complexity
- **Constraints:** Data integrity vs. insert/update overhead
- **Indexes:** Query speed vs. storage and write performance

## Overview / Обзор

Database design is the process of organizing data according to a database model. Good database design is essential for:
- Data integrity
- Performance
- Scalability
- Maintainability
- Query efficiency

Проектирование базы данных - это процесс организации данных в соответствии с моделью базы данных. Хорошее проектирование БД необходимо для обеспечения целостности данных, производительности, масштабируемости, поддерживаемости и эффективности запросов.

---

## Core Principles / Основные Принципы

### 1. Normalization / Нормализация

**Normal Forms (Нормальные формы):**

#### First Normal Form (1NF)
```sql
--  NOT 1NF: Multiple values in single field
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    courses VARCHAR(500)  -- "Math,Physics,Chemistry"
);

--  1NF: Atomic values
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE student_courses (
    student_id INT,
    course VARCHAR(100),
    PRIMARY KEY (student_id, course),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

**1NF Requirements:**
- Atomic values (no arrays, no lists)
- Each cell contains single value
- Column names are unique
- Order doesn't matter

#### Second Normal Form (2NF)
```sql
--  NOT 2NF: Partial dependency
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100),    -- Depends only on product_id
    product_price DECIMAL(10,2),  -- Depends only on product_id
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

--  2NF: No partial dependencies
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    product_price DECIMAL(10,2)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

**2NF Requirements:**
- Must be in 1NF
- No partial dependencies
- All non-key attributes depend on entire primary key

#### Third Normal Form (3NF)
```sql
--  NOT 3NF: Transitive dependency
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100),  -- Depends on department_id, not emp_id
    department_location VARCHAR(100)  -- Transitive dependency
);

--  3NF: No transitive dependencies
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100),
    department_location VARCHAR(100)
);

CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
```

**3NF Requirements:**
- Must be in 2NF
- No transitive dependencies
- All attributes depend only on primary key

#### Boyce-Codd Normal Form (BCNF)
```sql
-- Example: Every determinant must be a candidate key
CREATE TABLE professor_courses (
    professor_id INT,
    course_id INT,
    textbook VARCHAR(200),
    -- Assumption: each course has exactly one textbook
    -- course_id -> textbook (violation if professor_id is part of key)
    PRIMARY KEY (professor_id, course_id)
);

-- BCNF Solution:
CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    textbook VARCHAR(200)
);

CREATE TABLE professor_courses (
    professor_id INT,
    course_id INT,
    PRIMARY KEY (professor_id, course_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

### 2. Entity-Relationship Modeling / Моделирование Сущность-связь

#### Entities (Сущности)
```sql
-- Strong entities: exist independently
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Weak entities: depend on strong entities
CREATE TABLE customer_addresses (
    customer_id INT,
    address_id INT,
    street VARCHAR(200),
    city VARCHAR(100),
    PRIMARY KEY (customer_id, address_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
);
```

#### Relationships (Связи)

**One-to-One:**
```sql
-- Example: User and Profile
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100)
);

CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    bio TEXT,
    avatar_url VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);
```

**One-to-Many:**
```sql
-- Example: Author and Books
CREATE TABLE authors (
    author_id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE books (
    book_id INT PRIMARY KEY,
    title VARCHAR(200),
    author_id INT,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
```

**Many-to-Many:**
```sql
-- Example: Students and Courses
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100)
);

-- Junction table
CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    enrollment_date DATE,
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

### 3. Constraints / Ограничения

```sql
CREATE TABLE products (
    -- Primary Key: Unique identifier
    product_id INT PRIMARY KEY AUTO_INCREMENT,

    -- NOT NULL: Required fields
    product_name VARCHAR(200) NOT NULL,

    -- UNIQUE: Unique values
    sku VARCHAR(50) UNIQUE NOT NULL,

    -- CHECK: Value validation
    price DECIMAL(10,2) CHECK (price >= 0),
    quantity INT CHECK (quantity >= 0),

    -- FOREIGN KEY: Referential integrity
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    -- DEFAULT: Default values
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 4. Indexing Strategy / Стратегия Индексации

```sql
-- Primary index (automatic)
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    email VARCHAR(100)
);

-- Unique index
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Regular index for frequent queries
CREATE INDEX idx_users_created_at ON users(created_at);

-- Composite index for multi-column queries
CREATE INDEX idx_orders_user_date
    ON orders(user_id, order_date DESC);

-- Partial index (PostgreSQL)
CREATE INDEX idx_active_users
    ON users(email)
    WHERE is_active = true;

-- Full-text index
CREATE FULLTEXT INDEX idx_posts_content
    ON posts(title, content);
```

---

## Design Patterns / Паттерны Проектирования

### 1. Temporal Data (History Tracking)

```sql
-- Valid Time: When data is true in real world
CREATE TABLE employee_salaries (
    employee_id INT,
    salary DECIMAL(10,2),
    valid_from DATE,
    valid_to DATE,
    PRIMARY KEY (employee_id, valid_from),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Transaction Time: When data was stored in database
CREATE TABLE product_history (
    product_id INT,
    product_name VARCHAR(200),
    price DECIMAL(10,2),
    transaction_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_to TIMESTAMP DEFAULT '9999-12-31 23:59:59',
    PRIMARY KEY (product_id, transaction_from)
);
```

### 2. Soft Deletes

```sql
CREATE TABLE posts (
    post_id INT PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query only active records
SELECT * FROM posts WHERE deleted_at IS NULL;

-- "Delete" a record
UPDATE posts SET deleted_at = CURRENT_TIMESTAMP WHERE post_id = 123;
```

### 3. Audit Tables

```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100)
);

CREATE TABLE user_audit (
    audit_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(10),  -- INSERT, UPDATE, DELETE
    old_values JSON,
    new_values JSON,
    changed_by INT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Trigger for automatic auditing
DELIMITER $$
CREATE TRIGGER user_update_audit
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO user_audit (user_id, action, old_values, new_values)
    VALUES (
        NEW.user_id,
        'UPDATE',
        JSON_OBJECT('username', OLD.username, 'email', OLD.email),
        JSON_OBJECT('username', NEW.username, 'email', NEW.email)
    );
END$$
DELIMITER ;
```

### 4. Polymorphic Associations

```sql
-- Single Table Inheritance
CREATE TABLE media (
    media_id INT PRIMARY KEY,
    media_type VARCHAR(20),  -- 'image', 'video', 'document'
    title VARCHAR(200),

    -- Image-specific
    width INT,
    height INT,

    -- Video-specific
    duration INT,
    codec VARCHAR(50),

    -- Document-specific
    page_count INT,
    format VARCHAR(20)
);

-- Class Table Inheritance (better approach)
CREATE TABLE media (
    media_id INT PRIMARY KEY,
    media_type VARCHAR(20),
    title VARCHAR(200)
);

CREATE TABLE images (
    media_id INT PRIMARY KEY,
    width INT,
    height INT,
    FOREIGN KEY (media_id) REFERENCES media(media_id)
);

CREATE TABLE videos (
    media_id INT PRIMARY KEY,
    duration INT,
    codec VARCHAR(50),
    FOREIGN KEY (media_id) REFERENCES media(media_id)
);
```

### 5. Tree Structures

```sql
-- Adjacency List (simple, but slow queries)
CREATE TABLE categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100),
    parent_id INT,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id)
);

-- Nested Set Model (fast queries, slow inserts)
CREATE TABLE categories_nested (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100),
    lft INT NOT NULL,
    rgt INT NOT NULL,
    INDEX (lft),
    INDEX (rgt)
);

-- Closure Table (best for complex queries)
CREATE TABLE categories_closure (
    ancestor_id INT,
    descendant_id INT,
    depth INT,
    PRIMARY KEY (ancestor_id, descendant_id),
    FOREIGN KEY (ancestor_id) REFERENCES categories(category_id),
    FOREIGN KEY (descendant_id) REFERENCES categories(category_id)
);
```

---

## Best Practices / Лучшие Практики

### 1. Naming Conventions

```sql
-- Tables: plural nouns, snake_case
CREATE TABLE user_accounts (...);
CREATE TABLE product_categories (...);

-- Columns: snake_case, descriptive
first_name VARCHAR(50)
email_address VARCHAR(100)
created_at TIMESTAMP

-- Primary Keys: table_name_id or just id
user_id INT PRIMARY KEY
-- or
id INT PRIMARY KEY

-- Foreign Keys: referenced_table_singular_id
user_id INT  -- references users table
category_id INT  -- references categories table

-- Indexes: idx_tablename_columnname
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id_created_at ON orders(user_id, created_at);

-- Constraints: type_tablename_columnname
CONSTRAINT pk_users_user_id PRIMARY KEY (user_id)
CONSTRAINT fk_orders_user_id FOREIGN KEY (user_id) REFERENCES users(user_id)
CONSTRAINT uk_users_email UNIQUE (email)
CONSTRAINT chk_products_price CHECK (price >= 0)
```

### 2. Data Types Selection

```sql
-- Use appropriate types for better performance and storage
CREATE TABLE users (
    -- Integer types
    user_id BIGINT,          -- Large IDs
    age TINYINT,             -- 0-255
    login_count INT,         -- 0-4 billion

    -- String types
    username VARCHAR(50),    -- Variable length, known max
    bio TEXT,                -- Large text
    country CHAR(2),         -- Fixed length (ISO codes)

    -- Numeric types
    price DECIMAL(10,2),     -- Exact values (money)
    rating FLOAT,            -- Approximate values

    -- Date/Time
    birthdate DATE,          -- Date only
    created_at TIMESTAMP,    -- Date + time + timezone
    last_login DATETIME,     -- Date + time

    -- Boolean
    is_active BOOLEAN,       -- TRUE/FALSE

    -- JSON (modern databases)
    preferences JSON,        -- Flexible schema
    metadata JSONB           -- PostgreSQL: indexed JSON
);
```

### 3. Denormalization When Needed

```sql
-- Normalized (better for writes, data integrity)
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    order_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    PRIMARY KEY (order_id, product_id)
);

-- Denormalized (better for read performance)
CREATE TABLE orders_denormalized (
    order_id INT PRIMARY KEY,
    user_id INT,
    user_name VARCHAR(100),      -- Denormalized from users
    user_email VARCHAR(100),     -- Denormalized from users
    order_date TIMESTAMP,
    total_amount DECIMAL(10,2),  -- Calculated field
    item_count INT               -- Aggregated field
);
```

---

## Anti-Patterns to Avoid / Анти-паттерны

### 1. Multi-Column Attributes

```sql
--  BAD: Multiple similar columns
CREATE TABLE contacts (
    contact_id INT PRIMARY KEY,
    phone1 VARCHAR(20),
    phone2 VARCHAR(20),
    phone3 VARCHAR(20),
    phone4 VARCHAR(20)
);

--  GOOD: Separate table
CREATE TABLE contact_phones (
    contact_id INT,
    phone VARCHAR(20),
    phone_type VARCHAR(20),  -- 'mobile', 'home', 'work'
    PRIMARY KEY (contact_id, phone),
    FOREIGN KEY (contact_id) REFERENCES contacts(contact_id)
);
```

### 2. Using Strings for Everything

```sql
--  BAD: String for everything
CREATE TABLE orders (
    order_id VARCHAR(50),      -- Should be INT/BIGINT
    total VARCHAR(50),         -- Should be DECIMAL
    order_date VARCHAR(50),    -- Should be DATE/TIMESTAMP
    is_paid VARCHAR(10)        -- Should be BOOLEAN
);

--  GOOD: Appropriate types
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    total DECIMAL(10,2),
    order_date TIMESTAMP,
    is_paid BOOLEAN
);
```

### 3. Not Using Foreign Keys

```sql
--  BAD: No referential integrity
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT  -- Just a number, no constraint
);

--  GOOD: Enforce referential integrity
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE RESTRICT  -- Prevent deleting users with orders
);
```

---

## Related Questions / Связанные Вопросы

- [[q-database-migration-purpose--backend--medium]]
- [[q-relational-table-unique-data--backend--medium]]
- [[q-sql-join-algorithms-complexity--backend--hard]]
- [[q-virtual-tables-disadvantages--backend--medium]]

## Related Concepts / Связанные Концепции

- [[c-relational-databases]]
- [[c-database-performance]]
- [[c-sql-queries]]
- [[c-migrations]]

## References / Ссылки

- [Database Normalization Explained](https://www.guru99.com/database-normalization.html)
- [PostgreSQL Documentation - Database Design](https://www.postgresql.org/docs/current/ddl.html)
- [MySQL Best Practices](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- "Database Design for Mere Mortals" by Michael J. Hernandez
- "SQL Antipatterns" by Bill Karwin

---

## MOC Links

- [[moc-backend]] - Backend Development
- [[moc-algorithms]] - For query optimization
