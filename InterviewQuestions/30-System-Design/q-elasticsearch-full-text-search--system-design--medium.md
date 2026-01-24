---
id: sysdes-057
title: Full-Text Search and Elasticsearch
aliases:
- Elasticsearch
- Full-Text Search
- Inverted Index
topic: system-design
subtopics:
- data-management
- search
- indexing
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-database-indexing--system-design--medium
- q-design-search-autocomplete--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- data-management
- difficulty/medium
- search
- system-design
anki_cards:
- slug: sysdes-057-0-en
  language: en
  anki_id: 1769160582628
  synced_at: '2026-01-23T13:49:17.759162'
- slug: sysdes-057-0-ru
  language: ru
  anki_id: 1769160582650
  synced_at: '2026-01-23T13:49:17.760510'
---
# Question (EN)
> What is Elasticsearch and how does it enable full-text search? When would you use it over a relational database?

# Vopros (RU)
> Что такое Elasticsearch и как он обеспечивает полнотекстовый поиск? Когда использовать его вместо реляционной БД?

---

## Answer (EN)

**Elasticsearch** is a distributed search and analytics engine built on Apache Lucene, optimized for full-text search using inverted indexes.

### Inverted Index

```
Documents:
Doc1: "The quick brown fox"
Doc2: "The quick dog"
Doc3: "The brown dog jumps"

Inverted Index:
┌─────────┬────────────────┐
│ Term    │ Documents      │
├─────────┼────────────────┤
│ the     │ [1, 2, 3]      │
│ quick   │ [1, 2]         │
│ brown   │ [1, 3]         │
│ fox     │ [1]            │
│ dog     │ [2, 3]         │
│ jumps   │ [3]            │
└─────────┴────────────────┘

Query "brown dog" → Intersection of [1,3] and [2,3] → Doc3
```

### Architecture

```
┌────────────────────────────────────────────┐
│              Elasticsearch Cluster          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Node 1  │  │ Node 2  │  │ Node 3  │     │
│  │┌───────┐│  │┌───────┐│  │┌───────┐│     │
│  ││Shard 0││  ││Shard 1││  ││Shard 2││     │
│  ││Primary││  ││Primary││  ││Primary││     │
│  │└───────┘│  │└───────┘│  │└───────┘│     │
│  │┌───────┐│  │┌───────┐│  │┌───────┐│     │
│  ││Shard 1││  ││Shard 2││  ││Shard 0││     │
│  ││Replica││  ││Replica││  ││Replica││     │
│  │└───────┘│  │└───────┘│  │└───────┘│     │
│  └─────────┘  └─────────┘  └─────────┘     │
└────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| Index | Collection of documents (like a database) |
| Document | JSON object (like a row) |
| Shard | Horizontal partition of an index |
| Replica | Copy of a shard for redundancy |
| Analyzer | Tokenizes and normalizes text |

### Text Analysis Pipeline

```
Input: "The QUICK Brown Foxes!"
         ↓
Tokenizer: ["The", "QUICK", "Brown", "Foxes!"]
         ↓
Lowercase filter: ["the", "quick", "brown", "foxes!"]
         ↓
Punctuation filter: ["the", "quick", "brown", "foxes"]
         ↓
Stemmer: ["the", "quick", "brown", "fox"]
         ↓
Stored in inverted index
```

### When to Use Elasticsearch

| Use Case | Why Elasticsearch |
|----------|-------------------|
| Full-text search | Relevance scoring, fuzzy matching |
| Log aggregation | Fast search across billions of logs |
| Autocomplete | Prefix queries, suggestions |
| Analytics | Aggregations on large datasets |
| Geospatial | Location-based queries |

### Elasticsearch vs SQL

| Aspect | Elasticsearch | SQL Database |
|--------|---------------|--------------|
| Query type | Full-text search | Exact matches |
| Schema | Schema-less | Schema-defined |
| Joins | Limited (denormalize) | Full support |
| Transactions | No ACID | ACID compliant |
| Scale | Horizontally | Vertically (mostly) |

---

## Otvet (RU)

**Elasticsearch** - распределённый поисковый и аналитический движок на Apache Lucene, оптимизированный для полнотекстового поиска через инвертированные индексы.

### Инвертированный индекс

```
Документы:
Doc1: "The quick brown fox"
Doc2: "The quick dog"
Doc3: "The brown dog jumps"

Инвертированный индекс:
┌─────────┬────────────────┐
│ Терм    │ Документы      │
├─────────┼────────────────┤
│ the     │ [1, 2, 3]      │
│ quick   │ [1, 2]         │
│ brown   │ [1, 3]         │
│ dog     │ [2, 3]         │
└─────────┴────────────────┘

Запрос "brown dog" → Пересечение [1,3] и [2,3] → Doc3
```

### Ключевые концепции

| Концепция | Описание |
|-----------|----------|
| Index | Коллекция документов (как база данных) |
| Document | JSON объект (как строка) |
| Shard | Горизонтальная партиция индекса |
| Replica | Копия шарда для redundancy |
| Analyzer | Токенизирует и нормализует текст |

### Pipeline анализа текста

```
Вход: "The QUICK Brown Foxes!"
         ↓
Tokenizer: ["The", "QUICK", "Brown", "Foxes!"]
         ↓
Lowercase filter: ["the", "quick", "brown", "foxes!"]
         ↓
Stemmer: ["the", "quick", "brown", "fox"]
         ↓
Сохранено в инвертированном индексе
```

### Когда использовать Elasticsearch

| Случай | Почему Elasticsearch |
|--------|---------------------|
| Полнотекстовый поиск | Relevance scoring, fuzzy matching |
| Агрегация логов | Быстрый поиск по миллиардам логов |
| Autocomplete | Prefix queries, suggestions |
| Аналитика | Агрегации на больших датасетах |

### Elasticsearch vs SQL

| Аспект | Elasticsearch | SQL БД |
|--------|---------------|--------|
| Тип запроса | Полнотекстовый поиск | Точные совпадения |
| Схема | Schema-less | Определённая схема |
| Joins | Ограниченные | Полная поддержка |
| Транзакции | Нет ACID | ACID |
| Масштабирование | Горизонтальное | Вертикальное |

---

## Follow-ups

- How does Elasticsearch handle relevance scoring?
- What is the ELK stack?
- How do you handle data consistency between ES and primary database?
