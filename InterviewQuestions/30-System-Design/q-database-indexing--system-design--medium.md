---
id: sysdes-025
title: Database Indexing - B-Tree and LSM-Tree
aliases:
- Database Index
- B-Tree
- LSM-Tree
topic: system-design
subtopics:
- databases
- performance
- data-structures
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-sql-nosql-databases--system-design--medium
- q-database-sharding-partitioning--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- difficulty/medium
- performance
- system-design
anki_cards:
- slug: sysdes-025-0-en
  language: en
  anki_id: 1769158891341
  synced_at: '2026-01-23T13:49:17.830838'
- slug: sysdes-025-0-ru
  language: ru
  anki_id: 1769158891366
  synced_at: '2026-01-23T13:49:17.831933'
---
# Question (EN)
> How do database indexes work? Explain B-Tree vs LSM-Tree and when to use each.

# Vopros (RU)
> Как работают индексы базы данных? Объясните B-Tree vs LSM-Tree и когда использовать каждый.

---

## Answer (EN)

**Database indexes** are data structures that speed up data retrieval at the cost of additional storage and write overhead.

### Why Indexes Matter

```
Without index: Full table scan O(n)
With index:    Lookup O(log n) or O(1)

Example: 1M rows
- Full scan: ~1M operations
- B-Tree index: ~20 operations (log base 100)
```

### B-Tree (Balanced Tree)

**Structure:**
```
                    [50]
                   /    \
              [25,35]   [75,85]
              /  |  \    /  |  \
           [10][30][40][60][80][90]
                    ↓
              Leaf nodes (data pointers)
```

**Characteristics:**
- Balanced tree, all leaves at same depth
- Each node has multiple keys (high fanout)
- Excellent for reads and range queries
- Updates modify tree in-place
- Used by: PostgreSQL, MySQL InnoDB, Oracle

**Operations:**
| Operation | Complexity |
|-----------|------------|
| Search | O(log n) |
| Insert | O(log n) |
| Delete | O(log n) |
| Range query | O(log n + k) |

### LSM-Tree (Log-Structured Merge-Tree)

**Structure:**
```
Writes → [Memtable (RAM)]
              ↓ Flush when full
         [Level 0 SSTable]
              ↓ Compaction
         [Level 1 SSTables]
              ↓ Compaction
         [Level 2 SSTables]
              ...
```

**Characteristics:**
- Writes go to in-memory buffer first
- Periodically flushed to disk as immutable files (SSTables)
- Background compaction merges and sorts
- Excellent for write-heavy workloads
- Used by: Cassandra, RocksDB, LevelDB, HBase

**Operations:**
| Operation | Complexity |
|-----------|------------|
| Write | O(1) amortized |
| Read | O(n) levels to check |
| Range query | Slower (multiple SSTables) |

### B-Tree vs LSM-Tree Comparison

| Aspect | B-Tree | LSM-Tree |
|--------|--------|----------|
| Write performance | Slower (in-place) | Faster (sequential) |
| Read performance | Faster (single lookup) | Slower (multiple levels) |
| Space efficiency | Lower (fragmentation) | Higher (compaction) |
| Write amplification | Lower | Higher |
| Read amplification | Lower | Higher |
| Best for | Read-heavy, OLTP | Write-heavy, time-series |

### Write Amplification

**B-Tree:**
- Update may require reading page, modifying, writing back
- Typically 1-2x write amplification

**LSM-Tree:**
- Data written multiple times (memtable, L0, L1, L2...)
- Typically 10-30x write amplification
- But sequential writes (faster on SSDs)

### Index Types

| Type | Description | Use Case |
|------|-------------|----------|
| Primary | On primary key | Always |
| Secondary | On non-key columns | Query patterns |
| Composite | Multiple columns | Multi-column queries |
| Covering | Includes all query columns | Avoid table lookup |
| Partial | Subset of rows | Filtered queries |

### When to Add Index

**Add index when:**
- Column used in WHERE clauses frequently
- Column used in JOIN conditions
- Column used in ORDER BY
- High selectivity (few matching rows)

**Avoid index when:**
- Table is small
- Column has low selectivity
- Write-heavy table with few reads
- Column rarely queried

---

## Otvet (RU)

**Индексы базы данных** - структуры данных, ускоряющие извлечение данных ценой дополнительного хранения и накладных расходов на запись.

### Почему индексы важны

```
Без индекса: Полное сканирование таблицы O(n)
С индексом:  Поиск O(log n) или O(1)

Пример: 1M строк
- Полное сканирование: ~1M операций
- B-Tree индекс: ~20 операций (log по основанию 100)
```

### B-Tree (Сбалансированное дерево)

**Структура:**
```
                    [50]
                   /    \
              [25,35]   [75,85]
              /  |  \    /  |  \
           [10][30][40][60][80][90]
                    ↓
              Листовые узлы (указатели на данные)
```

**Характеристики:**
- Сбалансированное дерево, все листья на одной глубине
- Каждый узел имеет несколько ключей (высокий fanout)
- Отлично для чтения и range-запросов
- Обновления модифицируют дерево in-place
- Используется: PostgreSQL, MySQL InnoDB, Oracle

**Операции:**
| Операция | Сложность |
|----------|-----------|
| Поиск | O(log n) |
| Вставка | O(log n) |
| Удаление | O(log n) |
| Range запрос | O(log n + k) |

### LSM-Tree (Log-Structured Merge-Tree)

**Структура:**
```
Записи → [Memtable (RAM)]
              ↓ Flush когда полон
         [Level 0 SSTable]
              ↓ Compaction
         [Level 1 SSTables]
              ↓ Compaction
         [Level 2 SSTables]
              ...
```

**Характеристики:**
- Записи сначала идут в in-memory буфер
- Периодически сбрасываются на диск как неизменяемые файлы (SSTables)
- Фоновый compaction объединяет и сортирует
- Отлично для write-heavy нагрузок
- Используется: Cassandra, RocksDB, LevelDB, HBase

**Операции:**
| Операция | Сложность |
|----------|-----------|
| Запись | O(1) амортизированно |
| Чтение | O(n) уровней для проверки |
| Range запрос | Медленнее (несколько SSTables) |

### B-Tree vs LSM-Tree сравнение

| Аспект | B-Tree | LSM-Tree |
|--------|--------|----------|
| Производительность записи | Медленнее (in-place) | Быстрее (последовательно) |
| Производительность чтения | Быстрее (один lookup) | Медленнее (несколько уровней) |
| Эффективность места | Ниже (фрагментация) | Выше (compaction) |
| Write amplification | Ниже | Выше |
| Read amplification | Ниже | Выше |
| Лучше для | Read-heavy, OLTP | Write-heavy, time-series |

### Write Amplification

**B-Tree:**
- Обновление может требовать чтения страницы, модификации, записи
- Обычно 1-2x write amplification

**LSM-Tree:**
- Данные записываются несколько раз (memtable, L0, L1, L2...)
- Обычно 10-30x write amplification
- Но последовательные записи (быстрее на SSD)

### Типы индексов

| Тип | Описание | Применение |
|-----|----------|------------|
| Primary | На первичном ключе | Всегда |
| Secondary | На не-ключевых колонках | Паттерны запросов |
| Composite | Несколько колонок | Многоколоночные запросы |
| Covering | Включает все колонки запроса | Избежать lookup в таблицу |
| Partial | Подмножество строк | Фильтрованные запросы |

### Когда добавлять индекс

**Добавляйте индекс когда:**
- Колонка часто используется в WHERE
- Колонка используется в JOIN условиях
- Колонка используется в ORDER BY
- Высокая селективность (мало совпадающих строк)

**Избегайте индекса когда:**
- Таблица маленькая
- Колонка имеет низкую селективность
- Write-heavy таблица с редким чтением
- Колонка редко запрашивается

---

## Follow-ups

- What is the difference between clustered and non-clustered index?
- How does VACUUM relate to B-Tree indexes?
- What is bloom filter and how does it help LSM-Tree reads?

## Related Questions

### Prerequisites (Easier)
- [[q-sql-nosql-databases--system-design--medium]] - Database basics

### Related (Same Level)
- [[q-caching-strategies--system-design--medium]] - Caching
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding

### Advanced (Harder)
- [[q-consistency-models--system-design--hard]] - Consistency
