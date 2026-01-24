---
id: sysdes-067
title: Design Dropbox / Google Drive
aliases:
- Design Dropbox
- Design Google Drive
- File Sync System
- Cloud Storage
topic: system-design
subtopics:
- design-problems
- storage
- sync
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-object-vs-block-storage--system-design--medium
- q-design-youtube--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- storage
- system-design
anki_cards:
- slug: sysdes-067-0-en
  language: en
  anki_id: 1769160584476
  synced_at: '2026-01-23T13:49:17.832935'
- slug: sysdes-067-0-ru
  language: ru
  anki_id: 1769160584499
  synced_at: '2026-01-23T13:49:17.834208'
---
# Question (EN)
> Design a file storage and synchronization service like Dropbox or Google Drive.

# Vopros (RU)
> Спроектируйте сервис хранения и синхронизации файлов типа Dropbox или Google Drive.

---

## Answer (EN)

### Requirements

**Functional**: Upload/download files, sync across devices, share files, file versioning
**Non-functional**: High availability, fast sync, handle large files (GBs), offline support

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Apps                            │
│   (Desktop sync agent, Web, Mobile)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    API Gateway                              │
│            (Auth, Rate limiting, Routing)                  │
└─────────┬───────────────┬───────────────┬───────────────────┘
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  Metadata │   │   Sync    │   │  Block    │
    │  Service  │   │  Service  │   │  Service  │
    └─────┬─────┘   └───────────┘   └─────┬─────┘
          │                               │
    ┌─────▼─────┐                   ┌─────▼─────┐
    │ Metadata  │                   │   Block   │
    │    DB     │                   │  Storage  │
    └───────────┘                   └───────────┘
```

### File Chunking

```
Why chunk files?
- Resume interrupted uploads
- Deduplication (same chunks across files)
- Parallel upload/download
- Efficient sync (only changed chunks)

Chunking strategy:
┌────────────────────────────────────────┐
│           Large File (1GB)             │
└────────────────────────────────────────┘
                ↓ Split into chunks
┌────────┬────────┬────────┬────────┬────────┐
│ Chunk1 │ Chunk2 │ Chunk3 │ Chunk4 │ Chunk5 │
│  4MB   │  4MB   │  4MB   │  4MB   │  4MB   │
└────────┴────────┴────────┴────────┴────────┘
    │
    ↓ Each chunk gets hash (content-addressable)
Hash: SHA256(chunk1) = "abc123..."
```

### Sync Protocol

```
Client detects change → Compute changed chunks
                     → Upload only changed chunks
                     → Update metadata

Server notification → Push notification to other devices
                   → Clients fetch new metadata
                   → Download changed chunks
                   → Apply changes locally

Conflict resolution:
- Last-write-wins (simpler)
- Keep both versions (user decides)
- Operational transform (collaborative editing)
```

### Metadata Schema

```sql
-- Files table
files (
  id UUID PRIMARY KEY,
  user_id UUID,
  name VARCHAR,
  parent_folder_id UUID,
  is_folder BOOLEAN,
  size BIGINT,
  checksum VARCHAR,
  version INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- File chunks mapping
file_chunks (
  file_id UUID,
  chunk_index INT,
  chunk_hash VARCHAR,  -- For deduplication
  chunk_size INT,
  PRIMARY KEY (file_id, chunk_index)
)

-- Versions for history
file_versions (
  file_id UUID,
  version INT,
  chunk_hashes TEXT[],  -- Array of chunk hashes
  created_at TIMESTAMP
)
```

### Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Block Storage | S3, GCS | Store file chunks |
| Metadata DB | PostgreSQL + sharding | File structure |
| Notification | WebSocket / Long polling | Real-time sync |
| Queue | Kafka | Async processing |
| Cache | Redis | Hot metadata, chunk locations |
| CDN | CloudFront | Fast downloads |

### Deduplication

```
User A uploads: [chunk1, chunk2, chunk3]
User B uploads: [chunk1, chunk4, chunk5]

Storage (deduplicated):
┌─────────────────────────────────────┐
│ chunk1 (stored once, referenced 2x)│
│ chunk2                              │
│ chunk3                              │
│ chunk4                              │
│ chunk5                              │
└─────────────────────────────────────┘

Saves ~50% storage in practice
```

---

## Otvet (RU)

### Требования

**Функциональные**: Загрузка/скачивание файлов, синхронизация между устройствами, шаринг, версионирование
**Нефункциональные**: Высокая доступность, быстрая синхронизация, большие файлы (GB), офлайн поддержка

### Разбиение на чанки

```
Зачем разбивать файлы?
- Возобновление прерванных загрузок
- Дедупликация (одинаковые чанки между файлами)
- Параллельная загрузка/скачивание
- Эффективная синхронизация (только изменённые чанки)

Стратегия:
┌────────────────────────────────────────┐
│           Большой файл (1GB)           │
└────────────────────────────────────────┘
                ↓ Разбить на чанки
┌────────┬────────┬────────┬────────┬────────┐
│ Chunk1 │ Chunk2 │ Chunk3 │ Chunk4 │ Chunk5 │
│  4MB   │  4MB   │  4MB   │  4MB   │  4MB   │
└────────┴────────┴────────┴────────┴────────┘

Каждый чанк получает хеш (content-addressable)
```

### Протокол синхронизации

```
Клиент обнаруживает изменение → Вычислить изменённые чанки
                              → Загрузить только изменённые
                              → Обновить метаданные

Уведомление сервера → Push уведомление другим устройствам
                    → Клиенты получают новые метаданные
                    → Скачивают изменённые чанки
                    → Применяют изменения локально

Разрешение конфликтов:
- Last-write-wins (проще)
- Сохранить обе версии (пользователь решает)
```

### Ключевые компоненты

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Block Storage | S3, GCS | Хранение чанков |
| Metadata DB | PostgreSQL + шардинг | Структура файлов |
| Notification | WebSocket / Long polling | Real-time синхронизация |
| Queue | Kafka | Async обработка |
| Cache | Redis | Горячие метаданные |
| CDN | CloudFront | Быстрое скачивание |

### Дедупликация

```
User A загружает: [chunk1, chunk2, chunk3]
User B загружает: [chunk1, chunk4, chunk5]

Storage (дедуплицированный):
chunk1 (хранится один раз, referenced 2x)
chunk2, chunk3, chunk4, chunk5

Экономит ~50% storage на практике
```

---

## Follow-ups

- How do you handle file conflicts in collaborative editing?
- How does Dropbox implement smart sync (selective sync)?
- How do you design sharing and permissions?
