---
id: sysdes-037
title: Write-Ahead Logging (WAL)
aliases:
- WAL
- Write-Ahead Log
- Transaction Log
topic: system-design
subtopics:
- databases
- durability
- recovery
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-acid-properties--system-design--medium
- q-database-indexing--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- difficulty/medium
- durability
- system-design
anki_cards:
- slug: sysdes-037-0-en
  language: en
  anki_id: 1769159522147
  synced_at: '2026-01-23T13:49:17.847394'
- slug: sysdes-037-0-ru
  language: ru
  anki_id: 1769159522169
  synced_at: '2026-01-23T13:49:17.848523'
---
# Question (EN)
> What is Write-Ahead Logging (WAL)? How does it ensure durability and support crash recovery?

# Vopros (RU)
> Что такое журнал упреждающей записи (WAL)? Как он обеспечивает durability и поддерживает восстановление после сбоя?

---

## Answer (EN)

**Write-Ahead Logging (WAL)** ensures durability by writing changes to a log before applying them to the database.

### Core Principle

```
Rule: Log record must be written to disk BEFORE data page is modified

1. Write change to WAL (sequential write - fast)
2. Acknowledge transaction to client
3. Later: Apply change to data files (checkpoint)
```

### Why WAL Works

**Sequential vs Random I/O:**
- WAL: Sequential writes (append-only) - very fast
- Data files: Random writes - slower

**Crash Recovery:**
```
Crash happens after WAL write, before data write:
1. On restart, read WAL
2. Replay uncommitted changes
3. Database consistent again
```

### WAL Record Structure

```
┌─────────────────────────────────────────┐
│ LSN │ TxnID │ Type │ TableID │ Data    │
├─────────────────────────────────────────┤
│ 101 │ 42    │ INSERT │ users │ row data│
│ 102 │ 42    │ UPDATE │ users │ changes │
│ 103 │ 42    │ COMMIT │       │         │
└─────────────────────────────────────────┘

LSN = Log Sequence Number (monotonic)
```

### Checkpoint Process

```
Periodically:
1. Pause writes briefly
2. Flush dirty pages to disk
3. Write checkpoint record to WAL
4. Old WAL segments can be deleted

Recovery only needs to replay from last checkpoint
```

### WAL Modes

| Mode | Durability | Performance |
|------|------------|-------------|
| fsync every commit | Highest | Slowest |
| fsync periodic | High | Medium |
| No fsync | None | Fastest |

### Use Cases Beyond Databases

| System | WAL Usage |
|--------|-----------|
| PostgreSQL | Transaction recovery |
| Kafka | Message durability (commit log) |
| Redis AOF | Append-only file persistence |
| Elasticsearch | Translog for durability |
| etcd | Raft log |

---

## Otvet (RU)

**Write-Ahead Logging (WAL)** обеспечивает durability записью изменений в лог до их применения к базе данных.

### Основной принцип

```
Правило: Запись в лог должна быть на диске ДО модификации страницы данных

1. Записать изменение в WAL (последовательная запись - быстро)
2. Подтвердить транзакцию клиенту
3. Позже: Применить изменение к файлам данных (checkpoint)
```

### Почему WAL работает

**Последовательный vs Случайный I/O:**
- WAL: Последовательные записи (append-only) - очень быстро
- Файлы данных: Случайные записи - медленнее

**Восстановление после сбоя:**
```
Сбой после записи WAL, до записи данных:
1. При перезапуске читаем WAL
2. Воспроизводим незакоммиченные изменения
3. База снова согласована
```

### Структура записи WAL

```
┌─────────────────────────────────────────┐
│ LSN │ TxnID │ Type │ TableID │ Data    │
├─────────────────────────────────────────┤
│ 101 │ 42    │ INSERT │ users │ row data│
│ 102 │ 42    │ UPDATE │ users │ changes │
│ 103 │ 42    │ COMMIT │       │         │
└─────────────────────────────────────────┘

LSN = Log Sequence Number (монотонный)
```

### Процесс Checkpoint

```
Периодически:
1. Кратко приостановить записи
2. Сбросить грязные страницы на диск
3. Записать checkpoint в WAL
4. Старые сегменты WAL можно удалить

Восстановление нужно только с последнего checkpoint
```

### Режимы WAL

| Режим | Durability | Производительность |
|-------|------------|-------------------|
| fsync каждый коммит | Наивысшая | Медленнейшая |
| fsync периодически | Высокая | Средняя |
| Без fsync | Нет | Быстрейшая |

---

## Follow-ups

- What is the difference between WAL and redo log?
- How does PostgreSQL implement WAL archiving?
- What is logical vs physical WAL?
