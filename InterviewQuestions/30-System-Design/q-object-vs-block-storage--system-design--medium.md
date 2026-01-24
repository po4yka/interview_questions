---
id: sysdes-058
title: Object Storage vs Block Storage
aliases:
- Object Storage
- Block Storage
- S3
- EBS
topic: system-design
subtopics:
- data-management
- storage
- infrastructure
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-dropbox--system-design--hard
- q-cdn--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- data-management
- difficulty/medium
- storage
- system-design
anki_cards:
- slug: sysdes-058-0-en
  language: en
  anki_id: 1769160585227
  synced_at: '2026-01-23T13:49:17.853423'
- slug: sysdes-058-0-ru
  language: ru
  anki_id: 1769160585250
  synced_at: '2026-01-23T13:49:17.854285'
---
# Question (EN)
> What is the difference between object storage and block storage? When would you use each?

# Vopros (RU)
> В чём разница между объектным хранилищем и блочным хранилищем? Когда использовать каждое?

---

## Answer (EN)

**Block storage** stores data as fixed-size blocks (like a hard drive). **Object storage** stores data as objects with metadata (like a file system in the cloud).

### Comparison

| Aspect | Block Storage | Object Storage |
|--------|---------------|----------------|
| Unit | Fixed-size blocks (4KB-64KB) | Variable-size objects |
| Access | Low-level (raw blocks) | HTTP API (REST) |
| Metadata | Minimal | Rich, custom metadata |
| Performance | Low latency, high IOPS | Higher latency, high throughput |
| Scale | Limited (TB) | Unlimited (PB+) |
| Cost | Higher $/GB | Lower $/GB |
| Examples | AWS EBS, Azure Disk | AWS S3, Azure Blob, GCS |

### Block Storage

```
Structure:
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ B0 │ B1 │ B2 │ B3 │ B4 │ B5 │ B6 │ B7 │
└────┴────┴────┴────┴────┴────┴────┴────┘
  ↑
  File system manages blocks

Use cases:
- Database storage (need low latency)
- Boot volumes for VMs
- Applications requiring file system
- Transactional workloads
```

### Object Storage

```
Structure:
┌─────────────────────────────────────────┐
│ Object: profile_photo_123.jpg           │
│ ├── Data: [binary image data]           │
│ ├── Metadata:                           │
│ │   ├── content-type: image/jpeg        │
│ │   ├── size: 2.5MB                     │
│ │   ├── created: 2024-01-15             │
│ │   └── custom: {user_id: 123}          │
│ └── Key: /users/123/photos/profile.jpg  │
└─────────────────────────────────────────┘

Use cases:
- Static content (images, videos, documents)
- Backup and archival
- Data lakes
- CDN origin
- Log storage
```

### Access Patterns

```
Block Storage:
mount /dev/sda1 /data
read/write at byte level
fseek(file, offset)
fread(buffer, size)

Object Storage:
PUT https://s3.amazonaws.com/bucket/key
GET https://s3.amazonaws.com/bucket/key
(No partial updates - replace entire object)
```

### Decision Matrix

| Requirement | Choose |
|-------------|--------|
| Database backend | Block |
| VM disk | Block |
| Static website hosting | Object |
| Media storage (images, videos) | Object |
| Backup/archive | Object |
| Need file system | Block |
| Need HTTP access | Object |
| Cost-sensitive, large scale | Object |

---

## Otvet (RU)

**Блочное хранилище** хранит данные как блоки фиксированного размера (как жёсткий диск). **Объектное хранилище** хранит данные как объекты с метаданными.

### Сравнение

| Аспект | Блочное | Объектное |
|--------|---------|-----------|
| Единица | Блоки фикс. размера (4KB-64KB) | Объекты переменного размера |
| Доступ | Низкоуровневый (raw блоки) | HTTP API (REST) |
| Метаданные | Минимальные | Богатые, кастомные |
| Производительность | Низкая задержка, высокий IOPS | Выше задержка, высокий throughput |
| Масштаб | Ограниченный (TB) | Неограниченный (PB+) |
| Стоимость | Выше $/GB | Ниже $/GB |
| Примеры | AWS EBS, Azure Disk | AWS S3, Azure Blob, GCS |

### Блочное хранилище

```
Структура:
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ B0 │ B1 │ B2 │ B3 │ B4 │ B5 │ B6 │ B7 │
└────┴────┴────┴────┴────┴────┴────┴────┘
  Файловая система управляет блоками

Применение:
- Хранилище БД (нужна низкая задержка)
- Boot volumes для VM
- Приложения с файловой системой
- Транзакционные нагрузки
```

### Объектное хранилище

```
Структура:
┌─────────────────────────────────────────┐
│ Object: profile_photo_123.jpg           │
│ ├── Data: [бинарные данные изображения] │
│ ├── Metadata:                           │
│ │   ├── content-type: image/jpeg        │
│ │   └── custom: {user_id: 123}          │
│ └── Key: /users/123/photos/profile.jpg  │
└─────────────────────────────────────────┘

Применение:
- Статический контент (изображения, видео)
- Backup и архивация
- Data lakes
- CDN origin
```

### Матрица выбора

| Требование | Выбор |
|------------|-------|
| Backend БД | Блочное |
| Диск VM | Блочное |
| Статический хостинг | Объектное |
| Медиа хранение | Объектное |
| Backup/архив | Объектное |
| Нужна файловая система | Блочное |
| Нужен HTTP доступ | Объектное |

---

## Follow-ups

- What is file storage and how does it compare?
- How does S3 achieve 99.999999999% durability?
- What are storage classes (hot/warm/cold) in object storage?
