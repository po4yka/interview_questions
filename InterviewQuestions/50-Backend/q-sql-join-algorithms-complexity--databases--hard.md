---
id: db-002
title: SQL JOIN algorithms and complexity / Алгоритмы SQL JOIN и их сложность
aliases: []

# Classification
topic: databases
subtopics: [sql, algorithms]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: ru
language_tags: [en, ru]
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-backend
related: [
  c-sql-queries,
  c-database-performance,
  c-algorithms
]

# Timestamps
created: 2025-10-03
updated: 2025-11-11

# Tags
tags: [sql, join, algorithms, complexity, database-performance, difficulty/hard, easy_kotlin, lang/ru, topic/databases]
---
# Вопрос (RU)
> Как выглядит алгоритм запроса данных из двух таблиц и какая у него сложность?

# Question (EN)
> What does the algorithm for querying data from two tables look like and what is its complexity?

---

## Ответ (RU)

Запрос данных из двух таблиц в реляционных СУБД обычно выполняется с помощью операций JOIN в SQL. Физически движок БД выбирает один из нескольких алгоритмов соединения; их сложность зависит от выбранного алгоритма, типа JOIN, наличия индексов, распределения данных и доступной памяти.

**Пример запроса:**
```sql
SELECT employees.name, departments.name
FROM employees
INNER JOIN departments
ON employees.department_id = departments.id
```

**Алгоритмы выполнения JOIN (типичные физические стратегии соединения):**

1. **Nested Loop Join (Вложенные циклы)**
   - Для каждой строки из внешней таблицы выполняется поиск соответствующих строк во внутренней таблице.
   - Наивная реализация без индексов:
     - **Сложность**: O(n × m), где n и m — размеры таблиц.
   - При наличии индекса по ключу соединения во внутренней таблице:
     - Поиск может быть ускорен (например, O(log m) для B-tree индекса или близко к O(1) для подходящей хеш-структуры), так что суммарное время может быть ближе к O(n log m) или O(n).
   - Лучший выбор для: Случаев, когда одна таблица маленькая, либо когда по ключу соединения во внутренней таблице есть эффективный индекс.

2. **Hash Join (Хеш-объединение)**
   - Фаза построения: Для одной (обычно меньшей) таблицы по ключу соединения строится хеш-таблица.
   - Фаза поиска: Для каждой строки из другой таблицы выполняется проверка соответствующего ключа в хеш-таблице.
   - При размещении хеша в памяти и хорошей хеш-функции:
     - **Сложность**: O(n + m) в среднем.
   - Практические моменты:
     - Требует достаточного объема памяти; при выходе за пределы памяти используются многошаговые/разделённые хеш-join'ы и обращение к диску, что ухудшает производительность (хотя обычно остаётся эффективно).
   - Лучший выбор для: Больших таблиц с соединением по равенству при наличии достаточной памяти.

3. **Sort-Merge Join (Сортировка и слияние)**
   - Обе входные выборки сортируются по ключу соединения.
   - Затем отсортированные потоки сливаются за один проход.
   - Если сортировка необходима с нуля:
     - **Сложность**: O(n log n + m log m) для сортировки + O(n + m) для слияния.
   - Если данные уже отсортированы (например, за счёт индексов или предыдущих операций):
     - Затраты на сортировку можно пропустить или сильно уменьшить, приближаясь к O(n + m).
   - Лучший выбор для: Больших наборов данных, range-join'ов или когда данные уже отсортированы/упорядочены по ключу соединения.

## Answer (EN)

Querying data from two tables in relational databases is typically executed via JOIN operations in SQL. Physically, the database engine can choose between several join algorithms; their complexity depends on the chosen algorithm, join type, indexing, data distribution, and available memory.

**Example query:**
```sql
SELECT employees.name, departments.name
FROM employees
INNER JOIN departments
ON employees.department_id = departments.id
```

**JOIN execution algorithms (typical physical join strategies):**

1. **Nested Loop Join** (Вложенные циклы)
   - For each row from the outer table, matching rows are searched in the inner table.
   - Naive implementation without indexes:
     - **Complexity**: O(n × m), where n and m are table sizes.
   - With an index on the join key of the inner table:
     - Lookup can be reduced (e.g., O(log m) for B-tree index, or close to O(1) on a suitable hash structure), so total time may be closer to O(n log m) or O(n).
   - Best for: Cases where one table is small, or where efficient indexes exist on the join key of the inner table.

2. **Hash Join** (Хеш-объединение)
   - Build phase: A hash table is created for one (usually smaller) table based on the join key.
   - Probe phase: For each row from the other table, the corresponding key is checked in the hash table.
   - In-memory case with a good hash function:
     - **Complexity**: O(n + m) on average.
   - Practical considerations:
     - Requires sufficient memory; if spilling to disk or using multi-pass/partitioned hash join, performance degrades (though it often remains efficient in practice).
   - Best for: Large tables with equality joins when enough memory is available.

3. **Sort-Merge Join** (Сортировка и слияние)
   - Both inputs are sorted by the join key.
   - The sorted streams are then merged in a single pass.
   - If sorting is required:
     - **Complexity**: O(n log n + m log m) for sorting + O(n + m) for merging.
   - If inputs are already sorted (e.g., due to indexes or prior operations):
     - Sorting cost can be skipped or greatly reduced, approaching O(n + m).
   - Best for: Large datasets, range joins, or when data is already sorted / ordered by the join key.

---

## Дополнительные вопросы (RU)
- Как оптимизатор базы данных выбирает, какой алгоритм JOIN использовать?
- В чем разница между INNER JOIN, LEFT JOIN и другими типами соединений?
- Как индексы влияют на производительность JOIN?

## Follow-ups (EN)
- How do database optimizers choose which JOIN algorithm to use?
- What are the differences between INNER JOIN, LEFT JOIN, and other join types?
- How do indexes affect JOIN performance?

## Ссылки (RU)
- [[c-sql-queries]]
- [[c-database-performance]]
- [[c-algorithms]]
- [[moc-backend]]

## References (EN)
- [[c-sql-queries]]
- [[c-database-performance]]
- [[c-algorithms]]
- [[moc-backend]]

## Связанные вопросы (RU)
- [[q-hashmap-how-it-works--kotlin--medium]]
- [[q-data-structures-overview--algorithms--easy]]

## Related Questions (EN)
- [[q-hashmap-how-it-works--kotlin--medium]]
- [[q-data-structures-overview--algorithms--easy]]
