---
id: db-003
title: Storing unique data in relational tables / Хранение уникальных данных в реляционных таблицах
aliases: []

# Classification
topic: databases
subtopics: [databases, design]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-system-design
related: [
  q-sql-join-algorithms-complexity--backend--hard,
  q-database-migration-purpose--backend--medium,
  q-virtual-tables-disadvantages--backend--medium,
  c-database-design,
  c-relational-databases
]

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [database, relational, primary-key, unique-constraints, indexes, difficulty/medium, easy_kotlin, lang/ru, topic/databases]
date created: Friday, October 3rd 2025, 4:45:41 pm
date modified: Wednesday, October 29th 2025, 2:56:25 pm
---

# Question (EN)
> How to store unique information for each element in a relational table
# Вопрос (RU)
> Как в реляционной таблице сохранить уникальную для каждого элемента информацию

---

## Answer (EN)

To store unique information for each element in a relational table, unique keys and various types of constraints are used. In relational databases, unique keys ensure data uniqueness in columns, preventing duplication.

**Key mechanisms:**

1. **Primary Key**
   - Uniquely identifies each row in the table
   - A table can have only one primary key
   - Can consist of one or more columns (composite key)
   - Cannot contain NULL values

2. **Unique Constraints**
   - Guarantee value uniqueness in one or more columns
   - Multiple unique constraints can exist in a table
   - Can contain NULL values (in most databases)

3. **Auto-increment**
   - Automatically generates unique values for a column
   - Commonly used for primary keys
   - Implementation varies: SERIAL (PostgreSQL), AUTO_INCREMENT (MySQL), IDENTITY (SQL Server)

4. **Unique Indexes**
   - Help speed up search operations
   - Ensure data uniqueness when using a unique index
   - Can be created on single or multiple columns

## Ответ (RU)

Для сохранения уникальной информации для каждого элемента в реляционной таблице используются уникальные ключи и различные типы ограничений. В реляционных базах данных уникальные ключи обеспечивают уникальность данных в столбцах, предотвращая дублирование.

**Основные механизмы:**

1. **Первичный ключ (Primary Key)**
   - Уникально идентифицирует каждую строку в таблице
   - Таблица может иметь только один первичный ключ
   - Может состоять из одного или нескольких столбцов (составной ключ)
   - Не может содержать NULL значения

2. **Уникальные ограничения (Unique Constraints)**
   - Гарантируют уникальность значений в одном или нескольких столбцах
   - В таблице может существовать несколько уникальных ограничений
   - Могут содержать NULL значения (в большинстве баз данных)

3. **Автоинкремент (Auto-increment)**
   - Автоматически генерирует уникальные значения для столбца
   - Обычно используется для первичных ключей
   - Реализация варьируется: SERIAL (PostgreSQL), AUTO_INCREMENT (MySQL), IDENTITY (SQL Server)

4. **Уникальные индексы (Unique Indexes)**
   - Помогают ускорить операции поиска
   - Обеспечивают уникальность данных при использовании уникального индекса
   - Могут быть созданы на одном или нескольких столбцах

---

## Follow-ups
- What's the difference between PRIMARY KEY and UNIQUE constraint?
- When should you use natural vs surrogate keys?
- How do composite keys work?

## References
- [[c-database-design]]
- [[c-relational-databases]]
- [[moc-backend]]

## Related Questions

### Related (Medium)
- [[q-virtual-tables-disadvantages--backend--medium]] - Databases
- [[q-database-migration-purpose--backend--medium]] - Databases

### Advanced (Harder)
- [[q-sql-join-algorithms-complexity--backend--hard]] - Databases
