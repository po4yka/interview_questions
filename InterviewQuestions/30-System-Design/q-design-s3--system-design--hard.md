---
id: sysdes-078
title: Design S3 (Cloud Object Storage)
aliases:
- Design S3
- Design Cloud Object Storage
- Design Blob Storage
- Design Azure Blob
- Design GCS
topic: system-design
subtopics:
- design-problems
- storage
- distributed-systems
- durability
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
- q-design-dropbox--system-design--hard
- q-consistent-hashing--system-design--hard
- q-replication-strategies--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/hard
- storage
- distributed-systems
- system-design
---
# Question (EN)
> How would you design a cloud object storage service like Amazon S3?

# Vopros (RU)
> Как бы вы спроектировали облачное объектное хранилище, подобное Amazon S3?

---

## Answer (EN)

### Requirements

**Functional**:
- Store and retrieve objects (files) via HTTP API
- Organize objects in buckets with unique keys
- Support objects from bytes to 5TB
- Versioning and lifecycle policies
- Access control (IAM, bucket policies, ACLs)

**Non-functional**:
- **Durability**: 99.999999999% (11 nines) - designed to not lose data
- **Availability**: 99.99% (4 nines)
- **Scalability**: Exabytes of data, billions of objects
- **Performance**: Low latency for small objects, high throughput for large objects

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Clients (SDK, CLI, Console)                  │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ HTTPS
┌─────────────────────────────────▼───────────────────────────────────┐
│                         API Gateway / Load Balancer                  │
│                   (TLS termination, request routing)                 │
└────────┬─────────────────────────────────────────────┬──────────────┘
         │                                             │
   ┌─────▼─────┐                                 ┌─────▼─────┐
   │  Frontend │                                 │  Frontend │
   │  Service  │ ────────────────────────────── │  Service  │
   └─────┬─────┘                                 └─────┬─────┘
         │                                             │
         ▼                                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         Metadata Service                             │
│            (Object location, versioning, ACLs)                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  Distributed KV Store (DynamoDB-like) - sharded by bucket    │   │
│   └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Data Placement Service                          │
│        (Decides where to store data, manages replication)            │
└──────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         Storage Layer                                │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│   │    AZ-1     │   │    AZ-2     │   │    AZ-3     │   ...        │
│   │  ┌───────┐  │   │  ┌───────┐  │   │  ┌───────┐  │              │
│   │  │ Node  │  │   │  │ Node  │  │   │  │ Node  │  │              │
│   │  │ Node  │  │   │  │ Node  │  │   │  │ Node  │  │              │
│   │  │ Node  │  │   │  │ Node  │  │   │  │ Node  │  │              │
│   │  └───────┘  │   │  └───────┘  │   │  └───────┘  │              │
│   └─────────────┘   └─────────────┘   └─────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

### Object Storage Model

```
Bucket: my-bucket (globally unique name)
  │
  ├── photos/vacation/beach.jpg     (object key)
  │     ├── Data: [binary content]
  │     ├── Metadata:
  │     │     ├── Content-Type: image/jpeg
  │     │     ├── Content-Length: 2.5MB
  │     │     ├── ETag: "abc123..." (MD5 or multipart)
  │     │     ├── Last-Modified: 2024-01-15T10:30:00Z
  │     │     └── x-amz-meta-author: "john"
  │     └── ACL: owner=full, public=read
  │
  └── documents/report.pdf
```

### Data Partitioning

```
Challenge: Billions of objects, exabytes of data

Solution: Two-level partitioning

1. Bucket-level: Each bucket maps to metadata shard
   ┌─────────────────────────────────────────────┐
   │ Hash(bucket_name) → Metadata Shard          │
   │ bucket-a → Shard 1                          │
   │ bucket-b → Shard 2                          │
   │ bucket-c → Shard 1 (consistent hashing)     │
   └─────────────────────────────────────────────┘

2. Object-level: Object key determines storage nodes
   ┌─────────────────────────────────────────────┐
   │ Hash(bucket + key) → Storage Node Group     │
   │ Consider key prefix for hot spots           │
   │ "photos/2024/01/..." may be hot → randomize │
   └─────────────────────────────────────────────┘

Key insight: Random prefix or hash-based naming
prevents hot partitions
```

### Durability: 11 Nines (99.999999999%)

```
How to achieve 11 nines durability?

Strategy 1: Replication (simpler, more storage)
┌────────────────────────────────────────────────────┐
│ Object → 3 copies across 3 Availability Zones     │
│                                                    │
│   AZ-1          AZ-2          AZ-3                │
│ ┌──────┐      ┌──────┐      ┌──────┐              │
│ │Copy 1│      │Copy 2│      │Copy 3│              │
│ └──────┘      └──────┘      └──────┘              │
│                                                    │
│ Durability: ~6 nines per copy                     │
│ Combined: (1 - 0.000001^3) ≈ 99.9999999999%       │
└────────────────────────────────────────────────────┘

Strategy 2: Erasure Coding (more efficient)
┌────────────────────────────────────────────────────┐
│ Split data into k data chunks + m parity chunks   │
│ Example: Reed-Solomon (10, 4)                     │
│                                                    │
│ Original: 10 data chunks                          │
│ Encoded:  10 data + 4 parity = 14 total chunks   │
│ Storage overhead: 1.4x (vs 3x for replication)    │
│                                                    │
│ Can recover from any 4 chunk failures             │
│ Spread across 14 storage nodes in different AZs   │
└────────────────────────────────────────────────────┘

S3 uses erasure coding for Standard storage class
```

### Replication Process

```
Write path (synchronous for durability):

1. Client → PUT object
2. Frontend validates, calculates checksum
3. Placement service selects target nodes
4. Write to primary storage node
5. Primary replicates to secondaries (quorum)
6. Return success when W nodes acknowledge (W=2 of 3)

┌────────┐     ┌──────────┐     ┌─────────────────────┐
│ Client │────▶│ Frontend │────▶│ Primary Node (AZ-1) │
└────────┘     └──────────┘     └──────────┬──────────┘
                                           │ sync
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
           ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
           │Secondary (AZ-2)│      │Secondary (AZ-3)│      │Secondary (AZ-4)│
           └───────────────┘      └───────────────┘      └───────────────┘
```

### Metadata Management

```sql
-- Metadata stored in distributed KV store (like DynamoDB)

Object Metadata:
┌──────────────────────────────────────────────────────────────────────┐
│ Partition Key: bucket_name                                           │
│ Sort Key: object_key                                                 │
│                                                                      │
│ Attributes:                                                          │
│   version_id: "v1abc123"                                             │
│   etag: "d41d8cd98f00b204e9800998ecf8427e"                          │
│   size: 1048576                                                      │
│   storage_class: "STANDARD"                                          │
│   content_type: "application/json"                                   │
│   created_at: "2024-01-15T10:30:00Z"                                │
│   data_locations: ["node-1:chunk-a", "node-5:chunk-b", ...]         │
│   user_metadata: {"x-amz-meta-author": "john"}                      │
│   acl: {...}                                                         │
└──────────────────────────────────────────────────────────────────────┘

Bucket Metadata:
┌──────────────────────────────────────────────────────────────────────┐
│ Key: bucket_name                                                     │
│                                                                      │
│ Attributes:                                                          │
│   owner: "account-123"                                               │
│   region: "us-east-1"                                                │
│   versioning: "enabled"                                              │
│   lifecycle_rules: [...]                                             │
│   replication_config: {...}                                          │
│   bucket_policy: {...}                                               │
│   cors_config: {...}                                                 │
└──────────────────────────────────────────────────────────────────────┘
```

### Consistency Model

```
S3 provides strong consistency (since Dec 2020):
- Read-after-write consistency for PUTs
- Strong consistency for GET, PUT, LIST, DELETE

How achieved?
┌─────────────────────────────────────────────────────────────────────┐
│ Metadata layer uses consensus protocol (like Paxos/Raft)            │
│                                                                     │
│ Write: Update metadata → Wait for quorum → Return success          │
│ Read:  Read from quorum → Return latest version                    │
│                                                                     │
│ Version vector or logical clock for ordering                        │
└─────────────────────────────────────────────────────────────────────┘

Previous eventual consistency issues:
- PUT new object, immediately GET → might get 404
- DELETE object, immediately LIST → object might appear
- PUT object twice quickly → might get stale version

Now: Strong consistency eliminates these edge cases
```

### Multipart Upload

```
For large objects (>100MB recommended, required for >5GB):

┌─────────────────────────────────────────────────────────────────────┐
│ 1. Initiate Multipart Upload                                        │
│    POST /bucket/key?uploads                                         │
│    Response: uploadId=abc123                                        │
│                                                                     │
│ 2. Upload Parts (can be parallel, out of order)                     │
│    PUT /bucket/key?partNumber=1&uploadId=abc123                     │
│    PUT /bucket/key?partNumber=2&uploadId=abc123                     │
│    ...                                                               │
│    Each part: 5MB to 5GB (except last)                              │
│    Max 10,000 parts                                                 │
│                                                                     │
│ 3. Complete Multipart Upload                                        │
│    POST /bucket/key?uploadId=abc123                                 │
│    Body: <PartNumber>1</PartNumber><ETag>xyz</ETag>...              │
│                                                                     │
│ Benefits:                                                           │
│ - Resume interrupted uploads                                        │
│ - Parallel uploads (higher throughput)                              │
│ - Upload parts independently                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Versioning

```
When versioning enabled:

PUT object v1 → version_id = "v1abc"
PUT object v2 → version_id = "v2def" (v1 still exists)
DELETE object → delete marker (version_id = "v3ghi")

┌─────────────────────────────────────────────────────────────────────┐
│ Object: photos/cat.jpg                                              │
│                                                                     │
│ Version History:                                                    │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ v3ghi │ DELETE MARKER │ 2024-01-17 │ (current)                 │ │
│ ├───────┼───────────────┼────────────┤                            │ │
│ │ v2def │ 2.5 MB        │ 2024-01-16 │                            │ │
│ ├───────┼───────────────┼────────────┤                            │ │
│ │ v1abc │ 1.8 MB        │ 2024-01-15 │                            │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ GET photos/cat.jpg → 404 (delete marker)                           │
│ GET photos/cat.jpg?versionId=v2def → returns 2.5MB version         │
└─────────────────────────────────────────────────────────────────────┘
```

### Storage Classes & Lifecycle

```
Storage Classes:
┌─────────────────┬────────────────┬───────────────┬────────────────┐
│ Class           │ Durability     │ Availability  │ Use Case       │
├─────────────────┼────────────────┼───────────────┼────────────────┤
│ Standard        │ 11 nines       │ 99.99%        │ Frequent access│
│ Standard-IA     │ 11 nines       │ 99.9%         │ Infrequent     │
│ One Zone-IA     │ 11 nines       │ 99.5%         │ Re-creatable   │
│ Glacier Instant │ 11 nines       │ 99.9%         │ Archive, ms    │
│ Glacier Flexible│ 11 nines       │ 99.99%*       │ Archive, min-hr│
│ Glacier Deep    │ 11 nines       │ 99.99%*       │ Archive, 12hr  │
└─────────────────┴────────────────┴───────────────┴────────────────┘
* After retrieval

Lifecycle Policy Example:
┌─────────────────────────────────────────────────────────────────────┐
│ Rule: logs/*                                                        │
│   - After 30 days → transition to Standard-IA                       │
│   - After 90 days → transition to Glacier                          │
│   - After 365 days → expire (delete)                                │
│                                                                     │
│ Rule: backups/*                                                     │
│   - After 7 days → transition to Glacier Deep Archive              │
│   - Keep versions for 30 days                                       │
│   - Delete incomplete multipart uploads after 7 days                │
└─────────────────────────────────────────────────────────────────────┘
```

### Access Control

```
Three mechanisms (evaluated in order):

1. IAM Policies (identity-based)
┌─────────────────────────────────────────────────────────────────────┐
│ {                                                                   │
│   "Effect": "Allow",                                                │
│   "Action": ["s3:GetObject", "s3:PutObject"],                      │
│   "Resource": "arn:aws:s3:::my-bucket/*"                           │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘

2. Bucket Policies (resource-based)
┌─────────────────────────────────────────────────────────────────────┐
│ {                                                                   │
│   "Effect": "Deny",                                                 │
│   "Principal": "*",                                                 │
│   "Action": "s3:*",                                                 │
│   "Resource": "arn:aws:s3:::my-bucket/*",                          │
│   "Condition": {                                                    │
│     "Bool": {"aws:SecureTransport": "false"}                       │
│   }                                                                 │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘

3. ACLs (legacy, per-object)
┌─────────────────────────────────────────────────────────────────────┐
│ Owner: FULL_CONTROL                                                 │
│ Authenticated Users: READ                                          │
│ Public: none                                                        │
└─────────────────────────────────────────────────────────────────────┘

Evaluation: Explicit DENY > Explicit ALLOW > Implicit DENY
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage unit | Immutable objects | Simpler consistency, versioning |
| Durability | Erasure coding | 11 nines with 1.4x overhead |
| Consistency | Strong | User expectations, since 2020 |
| Metadata | Distributed KV | Scales horizontally |
| Large files | Multipart upload | Reliability, parallelism |
| Naming | Flat namespace | Simpler, hierarchies are virtual |
| Pricing | Pay per GB + requests | Aligns with usage |

---

## Otvet (RU)

### Требования

**Функциональные**:
- Хранение и получение объектов (файлов) через HTTP API
- Организация объектов в бакеты с уникальными ключами
- Поддержка объектов от байтов до 5TB
- Версионирование и политики жизненного цикла
- Контроль доступа (IAM, политики бакетов, ACL)

**Нефункциональные**:
- **Долговечность**: 99.999999999% (11 девяток) - данные не должны теряться
- **Доступность**: 99.99% (4 девятки)
- **Масштабируемость**: Эксабайты данных, миллиарды объектов
- **Производительность**: Низкая задержка для малых объектов, высокая пропускная способность для больших

### Высокоуровневая архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Клиенты (SDK, CLI, Console)                       │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ HTTPS
┌─────────────────────────────────▼───────────────────────────────────┐
│                      API Gateway / Load Balancer                     │
└────────┬─────────────────────────────────────────────┬──────────────┘
         │                                             │
   ┌─────▼─────┐                                 ┌─────▼─────┐
   │  Frontend │                                 │  Frontend │
   │  Service  │                                 │  Service  │
   └─────┬─────┘                                 └─────┬─────┘
         ▼                                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       Сервис метаданных                              │
│          (Расположение объектов, версии, ACL)                        │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │ Распределённое KV-хранилище - шардировано по бакетам        │   │
│   └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     Сервис размещения данных                         │
│        (Решает где хранить данные, управляет репликацией)            │
└──────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         Слой хранения                                │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│   │    AZ-1     │   │    AZ-2     │   │    AZ-3     │   ...        │
│   │  ┌───────┐  │   │  ┌───────┐  │   │  ┌───────┐  │              │
│   │  │ Node  │  │   │  │ Node  │  │   │  │ Node  │  │              │
│   │  └───────┘  │   │  └───────┘  │   │  └───────┘  │              │
│   └─────────────┘   └─────────────┘   └─────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

### Модель объектного хранилища

```
Бакет: my-bucket (глобально уникальное имя)
  │
  ├── photos/vacation/beach.jpg     (ключ объекта)
  │     ├── Данные: [бинарный контент]
  │     ├── Метаданные:
  │     │     ├── Content-Type: image/jpeg
  │     │     ├── Content-Length: 2.5MB
  │     │     ├── ETag: "abc123..."
  │     │     └── x-amz-meta-author: "john"
  │     └── ACL: owner=full, public=read
  │
  └── documents/report.pdf
```

### Партиционирование данных

```
Задача: Миллиарды объектов, эксабайты данных

Решение: Двухуровневое партиционирование

1. Уровень бакета: Каждый бакет → шард метаданных
   ┌─────────────────────────────────────────────┐
   │ Hash(bucket_name) → Шард метаданных         │
   │ bucket-a → Shard 1                          │
   │ bucket-b → Shard 2                          │
   └─────────────────────────────────────────────┘

2. Уровень объекта: Ключ объекта → узлы хранения
   ┌─────────────────────────────────────────────┐
   │ Hash(bucket + key) → Группа узлов хранения  │
   │ Учитывать префикс ключа для hot spots       │
   │ "photos/2024/01/..." может быть горячим     │
   └─────────────────────────────────────────────┘

Ключевой insight: Случайный префикс или хэш-based
именование предотвращает горячие партиции
```

### Долговечность: 11 девяток

```
Как достичь 11 девяток долговечности?

Стратегия 1: Репликация (проще, больше хранения)
┌────────────────────────────────────────────────────┐
│ Объект → 3 копии в 3 Availability Zones           │
│                                                    │
│   AZ-1          AZ-2          AZ-3                │
│ ┌──────┐      ┌──────┐      ┌──────┐              │
│ │Копия1│      │Копия2│      │Копия3│              │
│ └──────┘      └──────┘      └──────┘              │
│                                                    │
│ Overhead: 3x хранения                              │
└────────────────────────────────────────────────────┘

Стратегия 2: Erasure Coding (эффективнее)
┌────────────────────────────────────────────────────┐
│ Разбить данные на k data чанков + m parity чанков │
│ Пример: Reed-Solomon (10, 4)                      │
│                                                    │
│ Оригинал: 10 data чанков                          │
│ Закодировано: 10 data + 4 parity = 14 чанков     │
│ Overhead: 1.4x (против 3x для репликации)         │
│                                                    │
│ Можно восстановить при любых 4 сбоях чанков       │
└────────────────────────────────────────────────────┘

S3 использует erasure coding для Standard класса
```

### Процесс репликации

```
Путь записи (синхронный для долговечности):

1. Клиент → PUT объект
2. Frontend валидирует, вычисляет checksum
3. Сервис размещения выбирает целевые узлы
4. Запись в primary узел
5. Primary реплицирует на secondaries (quorum)
6. Возврат успеха когда W узлов подтвердили (W=2 из 3)

┌────────┐     ┌──────────┐     ┌─────────────────────┐
│ Клиент │────▶│ Frontend │────▶│ Primary Node (AZ-1) │
└────────┘     └──────────┘     └──────────┬──────────┘
                                           │ sync
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
           ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
           │Secondary (AZ-2)│      │Secondary (AZ-3)│      │Secondary (AZ-4)│
           └───────────────┘      └───────────────┘      └───────────────┘
```

### Модель согласованности

```
S3 обеспечивает строгую согласованность (с декабря 2020):
- Read-after-write consistency для PUT
- Строгая согласованность для GET, PUT, LIST, DELETE

Как достигается?
┌─────────────────────────────────────────────────────────────────────┐
│ Слой метаданных использует протокол консенсуса (Paxos/Raft)         │
│                                                                     │
│ Запись: Обновить метаданные → Дождаться кворума → Вернуть успех    │
│ Чтение: Прочитать из кворума → Вернуть последнюю версию            │
└─────────────────────────────────────────────────────────────────────┘

Прошлые проблемы eventual consistency:
- PUT новый объект, сразу GET → мог получить 404
- DELETE объект, сразу LIST → объект мог появиться

Сейчас: Строгая согласованность устраняет эти edge cases
```

### Multipart Upload

```
Для больших объектов (>100MB рекомендуется, >5GB обязательно):

┌─────────────────────────────────────────────────────────────────────┐
│ 1. Инициировать Multipart Upload                                    │
│    POST /bucket/key?uploads                                         │
│    Ответ: uploadId=abc123                                           │
│                                                                     │
│ 2. Загрузить части (параллельно, в любом порядке)                  │
│    PUT /bucket/key?partNumber=1&uploadId=abc123                     │
│    PUT /bucket/key?partNumber=2&uploadId=abc123                     │
│    Каждая часть: 5MB до 5GB (кроме последней)                      │
│    Макс 10,000 частей                                               │
│                                                                     │
│ 3. Завершить Multipart Upload                                       │
│    POST /bucket/key?uploadId=abc123                                 │
│                                                                     │
│ Преимущества:                                                       │
│ - Возобновление прерванных загрузок                                │
│ - Параллельные загрузки (выше throughput)                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Версионирование

```
При включённом версионировании:

PUT объект v1 → version_id = "v1abc"
PUT объект v2 → version_id = "v2def" (v1 сохраняется)
DELETE объект → delete marker (version_id = "v3ghi")

┌─────────────────────────────────────────────────────────────────────┐
│ Объект: photos/cat.jpg                                              │
│                                                                     │
│ История версий:                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ v3ghi │ DELETE MARKER │ 2024-01-17 │ (текущая)                 │ │
│ ├───────┼───────────────┼────────────┤                            │ │
│ │ v2def │ 2.5 MB        │ 2024-01-16 │                            │ │
│ ├───────┼───────────────┼────────────┤                            │ │
│ │ v1abc │ 1.8 MB        │ 2024-01-15 │                            │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ GET photos/cat.jpg → 404 (delete marker)                           │
│ GET photos/cat.jpg?versionId=v2def → возвращает версию 2.5MB       │
└─────────────────────────────────────────────────────────────────────┘
```

### Классы хранения и жизненный цикл

```
Классы хранения:
┌─────────────────┬────────────────┬───────────────┬────────────────┐
│ Класс           │ Долговечность  │ Доступность   │ Применение     │
├─────────────────┼────────────────┼───────────────┼────────────────┤
│ Standard        │ 11 девяток     │ 99.99%        │ Частый доступ  │
│ Standard-IA     │ 11 девяток     │ 99.9%         │ Редкий доступ  │
│ One Zone-IA     │ 11 девяток     │ 99.5%         │ Воссоздаваемые │
│ Glacier Instant │ 11 девяток     │ 99.9%         │ Архив, мс      │
│ Glacier Flexible│ 11 девяток     │ 99.99%*       │ Архив, мин-час │
│ Glacier Deep    │ 11 девяток     │ 99.99%*       │ Архив, 12 час  │
└─────────────────┴────────────────┴───────────────┴────────────────┘

Пример политики жизненного цикла:
┌─────────────────────────────────────────────────────────────────────┐
│ Правило: logs/*                                                     │
│   - Через 30 дней → переход в Standard-IA                          │
│   - Через 90 дней → переход в Glacier                              │
│   - Через 365 дней → удаление                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Контроль доступа

```
Три механизма (оцениваются по порядку):

1. IAM политики (на основе идентичности)
┌─────────────────────────────────────────────────────────────────────┐
│ {                                                                   │
│   "Effect": "Allow",                                                │
│   "Action": ["s3:GetObject", "s3:PutObject"],                      │
│   "Resource": "arn:aws:s3:::my-bucket/*"                           │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘

2. Политики бакетов (на основе ресурса)
┌─────────────────────────────────────────────────────────────────────┐
│ {                                                                   │
│   "Effect": "Deny",                                                 │
│   "Principal": "*",                                                 │
│   "Action": "s3:*",                                                 │
│   "Condition": {"Bool": {"aws:SecureTransport": "false"}}          │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘

3. ACL (legacy, для каждого объекта)

Оценка: Явный DENY > Явный ALLOW > Неявный DENY
```

### Ключевые решения дизайна

| Решение | Выбор | Обоснование |
|---------|-------|-------------|
| Единица хранения | Неизменяемые объекты | Проще согласованность |
| Долговечность | Erasure coding | 11 девяток с 1.4x overhead |
| Согласованность | Строгая | Ожидания пользователей |
| Метаданные | Распределённое KV | Горизонтальное масштабирование |
| Большие файлы | Multipart upload | Надёжность, параллелизм |
| Пространство имён | Плоское | Проще, иерархии виртуальные |

---

## Follow-ups

- How does S3 handle hot partitions with sequential key naming?
- How would you design cross-region replication?
- How does S3 Transfer Acceleration work?
- How would you implement server-side encryption?
- How does S3 Select optimize query performance?
