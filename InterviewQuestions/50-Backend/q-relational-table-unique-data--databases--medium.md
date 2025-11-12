---
id: db-003
title: Storing unique data in relational tables / Хранение уникальных данных в реляционных таблицах
aliases: []

# Classification
topic: databases
subtopics: [databases]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-backend
related: [
  c-database-design,
  c-relational-databases
]

# Timestamps
created: 2025-10-03
updated: 2025-11-11

# Tags
tags: [database, relational, primary-key, unique-constraints, indexes, difficulty/medium, easy_kotlin, lang/ru, topic/databases]
---

# Вопрос (RU)
> Как в реляционной таблице сохранить уникальную для каждого элемента информацию

# Question (EN)
> How to store unique information for each element in a relational table

---

## Ответ (RU)

Для сохранения уникальной информации для каждого элемента в реляционной таблице используются уникальные ключи и различные типы ограничений. В реляционных базах данных уникальные ключи обеспечивают уникальность данных в столбцах, предотвращая дублирование.

Важно: эти механизмы гарантируют уникальность на уровне БД для ограниченных столбцов. Они сами по себе не делают значения «бизнес-идентификаторами», если вы явно так не спроектировали схему.

**Основные механизмы:**

1. **Первичный ключ (Primary Key)**
   - Уникально идентифицирует каждую строку в таблице
   - Таблица может иметь только один первичный ключ
   - Может состоять из одного или нескольких столбцов (составной ключ)
   - Не может содержать NULL значения

2. **Уникальные ограничения (UNIQUE Constraints)**
   - Гарантируют уникальность значений в одном или нескольких столбцах
   - В таблице может существовать несколько UNIQUE-ограничений
   - Обращение с NULL значениями зависит от реализации:
     - По стандарту SQL NULL не считаются равными, поэтому допускаются несколько NULL
     - Многие популярные СУБД (например, PostgreSQL, MySQL/InnoDB) позволяют несколько NULL в UNIQUE-столбцах
     - В отдельных системах и типах индексов возможны отличия, поэтому важно проверять поведение конкретной СУБД

3. **Автоинкремент (Auto-increment)**
   - Автоматически генерирует уникальные значения для столбца
   - Обычно используется для суррогатных первичных ключей (технических идентификаторов)
   - Сам по себе не обеспечивает уникальность бизнес-данных; при необходимости дополняется UNIQUE-ограничениями
   - Реализация варьируется: SERIAL / IDENTITY / GENERATED AS IDENTITY (PostgreSQL), AUTO_INCREMENT (MySQL), IDENTITY (SQL Server)

4. **Уникальные индексы (Unique Indexes)**
   - Обеспечивают уникальность данных в индексируемых столбцах, если индекс объявлен как UNIQUE
   - Помогают ускорить операции поиска по этим столбцам
   - Могут быть созданы на одном или нескольких столбцах

## Answer (EN)

To store unique information for each element in a relational table, unique keys and various types of constraints are used. In relational databases, unique keys ensure data uniqueness in columns, preventing duplication.

Important: these mechanisms guarantee uniqueness at the database level for the constrained columns. They do not automatically ensure that the values are meaningful business identifiers unless you design them as such.

**Key mechanisms:**

1. **Primary Key**
   - Uniquely identifies each row in the table
   - A table can have only one primary key
   - Can consist of one or more columns (composite key)
   - Cannot contain NULL values

2. **Unique Constraints**
   - Guarantee value uniqueness in one or more columns
   - Multiple unique constraints can exist in a table
   - Handling of NULL values is implementation-dependent:
     - By SQL standard, NULLs are not considered equal, so multiple NULLs are allowed
     - Many popular DBMSs (e.g., PostgreSQL, MySQL/InnoDB) allow multiple NULLs in UNIQUE columns
     - Some systems and specific index types may effectively restrict NULLs differently, so check your DBMS behavior

3. **Auto-increment**
   - Automatically generates unique values for a column
   - Commonly used for surrogate primary keys (technical identifiers)
   - Does not by itself ensure uniqueness of business data; combine with UNIQUE constraints when needed
   - Implementation varies: SERIAL / IDENTITY / GENERATED AS IDENTITY (PostgreSQL), AUTO_INCREMENT (MySQL), IDENTITY (SQL Server)

4. **Unique Indexes**
   - Ensure uniqueness of indexed columns when the index is defined as UNIQUE
   - Help speed up search operations on those columns
   - Can be created on single or multiple columns

---

## Дополнительные вопросы (RU)
- В чем разница между PRIMARY KEY и UNIQUE-ограничением?
- Когда стоит использовать естественные ключи по сравнению с суррогатными?
- Как работают составные ключи?

## Follow-ups
- What's the difference between PRIMARY KEY and UNIQUE constraint?
- When should you use natural vs surrogate keys?
- How do composite keys work?

## Ссылки (RU)
- [[c-database-design]]
- [[c-relational-databases]]
- [[moc-backend]]

## References
- [[c-database-design]]
- [[c-relational-databases]]
- [[moc-backend]]

## Связанные вопросы (RU)

### Средний уровень (Medium)
- [[q-virtual-tables-disadvantages--databases--medium]] - Databases
- [[q-database-migration-purpose--databases--medium]] - Databases

### Продвинутый уровень (Harder)
- [[q-sql-join-algorithms-complexity--databases--hard]] - Databases

## Related Questions

### Related (Medium)
- [[q-virtual-tables-disadvantages--databases--medium]] - Databases
- [[q-database-migration-purpose--databases--medium]] - Databases

### Advanced (Harder)
- [[q-sql-join-algorithms-complexity--databases--hard]] - Databases
