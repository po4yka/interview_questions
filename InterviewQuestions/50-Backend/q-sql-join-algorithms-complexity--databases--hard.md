---
id: db-002
title: SQL JOIN algorithms and complexity / Алгоритмы SQL JOIN и их сложность
aliases: []

# Classification
topic: databases
subtopics: [databases, sql, algorithms]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: ru
language_tags: [en, ru]
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-system-design
related: [
  q-virtual-tables-disadvantages--backend--medium,
  q-database-migration-purpose--backend--medium,
  q-relational-table-unique-data--backend--medium,
  c-sql-queries,
  c-database-performance,
  c-algorithms
]

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [sql, join, algorithms, complexity, database-performance, difficulty/hard, easy_kotlin, lang/ru, topic/databases]
date created: Friday, October 3rd 2025, 4:45:20 pm
date modified: Wednesday, October 29th 2025, 2:56:26 pm
---

# Question (EN)
> What does the algorithm for querying data from two tables look like and what is its complexity?
# Вопрос (RU)
> Как выглядит алгоритм запроса данных из двух таблиц и какая у него сложность?

---

## Answer (EN)

Querying data from two tables is usually performed using the JOIN operation in SQL. The algorithm and its complexity depend on the join type, data structure, and database used.

**Example query:**
```sql
SELECT employees.name, departments.name
FROM employees
INNER JOIN departments
ON employees.department_id = departments.id
```

**JOIN execution algorithms:**

1. **Nested Loop Join** (Вложенные циклы)
   - For each row from the first table, corresponding rows are searched in the second table
   - **Complexity**: O(n × m) where n and m are table sizes
   - Best for: Small tables or when one table is very small

2. **Hash Join** (Хеш-объединение)
   - A hash table is created for one table based on the join key
   - For each row from the other table, the corresponding key is checked in the hash table
   - **Complexity**: O(n + m) - linear time
   - Best for: Large tables with sufficient memory

3. **Sort-Merge Join** (Сортировка и слияние)
   - Both tables are sorted by the join key
   - Then the sorted lists are merged
   - **Complexity**: O(n log n + m log m) for sorting + O(n + m) for merging
   - Best for: When data is already sorted or needs to be sorted anyway

## Ответ (RU)

Запрос данных из двух таблиц обычно выполняется с помощью операции объединения JOIN в SQL. Алгоритм и его сложность зависят от типа объединения, структуры данных и используемой базы данных.

**Пример запроса:**
```sql
SELECT employees.name, departments.name
FROM employees
INNER JOIN departments
ON employees.department_id = departments.id
```

**Алгоритмы выполнения JOIN:**

1. **Nested Loop Join (Вложенные циклы)**
   - Для каждой строки из первой таблицы выполняется поиск соответствующих строк во второй таблице
   - **Сложность**: O(n × m), где n и m - размеры таблиц
   - Лучший выбор для: Небольших таблиц или когда одна таблица очень маленькая

2. **Hash Join (Хеш-объединение)**
   - Создается хеш-таблица для одной из таблиц на основе ключа соединения
   - Для каждой строки из другой таблицы проверяется наличие соответствующего ключа в хеш-таблице
   - **Сложность**: O(n + m) - линейное время
   - Лучший выбор для: Больших таблиц при наличии достаточной памяти

3. **Sort-Merge Join (Сортировка и слияние)**
   - Обе таблицы сортируются по ключу соединения
   - Затем выполняется слияние отсортированных списков
   - **Сложность**: O(n log n + m log m) для сортировки + O(n + m) для слияния
   - Лучший выбор для: Когда данные уже отсортированы или их в любом случае нужно отсортировать

---

## Follow-ups
- How do database optimizers choose which JOIN algorithm to use?
- What are the differences between INNER JOIN, LEFT JOIN, and other join types?
- How do indexes affect JOIN performance?

## References
- [[c-sql-queries]]
- [[c-database-performance]]
- [[c-algorithms]]
- [[moc-backend]]

## Related Questions
- [[q-hashmap-how-it-works--programming-languages--medium]]
- [[q-data-structures-overview--algorithms--easy]]
