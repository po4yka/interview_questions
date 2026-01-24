---
id: sysdes-076
title: Hot/Warm/Cold Data Tiering
aliases:
- Hot Warm Cold Data
- Data Tiering
- Storage Tiering
topic: system-design
subtopics:
- data-management
- storage
- optimization
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-caching-strategies--system-design--medium
- q-data-lake-vs-warehouse--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- data-management
- difficulty/medium
- storage
- system-design
anki_cards:
- slug: sysdes-076-0-en
  language: en
  anki_id: 1769161752334
  synced_at: '2026-01-23T13:49:17.712153'
- slug: sysdes-076-0-ru
  language: ru
  anki_id: 1769161752356
  synced_at: '2026-01-23T13:49:17.714951'
---
# Question (EN)
> What is hot/warm/cold data tiering? How does it optimize storage costs and performance?

# Vopros (RU)
> Что такое горячие/тёплые/холодные данные? Как это оптимизирует затраты на хранение и производительность?

---

## Answer (EN)

**Data tiering** classifies data by access frequency and stores it on appropriate storage types to balance cost and performance.

### The Three Tiers

```
┌─────────────────────────────────────────────────────────────┐
│                         HOT DATA                             │
│  • Frequently accessed (daily/hourly)                       │
│  • Needs lowest latency                                     │
│  • Examples: Current transactions, live dashboards          │
│  • Storage: SSD, in-memory cache, fast databases            │
│  • Cost: $$$                                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        WARM DATA                             │
│  • Occasionally accessed (weekly/monthly)                   │
│  • Moderate latency acceptable                              │
│  • Examples: Recent reports, last quarter data              │
│  • Storage: HDD, standard cloud storage                     │
│  • Cost: $$                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        COLD DATA                             │
│  • Rarely accessed (yearly or less)                         │
│  • High latency acceptable (minutes to hours)               │
│  • Examples: Archives, compliance data, old backups         │
│  • Storage: Tape, glacier, archive storage                  │
│  • Cost: $                                                  │
└─────────────────────────────────────────────────────────────┘
```

### Cost Comparison (AWS Example)

| Tier | Storage Class | Cost/GB/Month | Retrieval |
|------|---------------|---------------|-----------|
| Hot | S3 Standard | $0.023 | Instant |
| Warm | S3 Infrequent Access | $0.0125 | Instant (retrieval fee) |
| Cold | S3 Glacier | $0.004 | Minutes to hours |
| Archive | S3 Glacier Deep Archive | $0.00099 | 12-48 hours |

### Typical Data Lifecycle

```
Day 0-7:    HOT    → Fast SSD, in-memory cache
Day 7-30:   HOT    → Standard SSD/database
Day 30-90: WARM   → Standard storage, compressed
Day 90-365: COLD  → Archive storage
Year 1+:   ARCHIVE → Deep archive/tape

Example: E-commerce order data
┌──────────────────────────────────────────────────────────┐
│ Today's orders        → Redis cache + Primary DB (HOT)   │
│ Last week's orders    → Primary DB (HOT)                 │
│ Last month's orders   → Replica DB, compressed (WARM)    │
│ Last year's orders    → S3 Infrequent Access (COLD)      │
│ Older orders          → Glacier (ARCHIVE)                │
└──────────────────────────────────────────────────────────┘
```

### Implementation Strategies

| Strategy | How It Works |
|----------|--------------|
| **Time-based** | Move data based on age (automatic lifecycle) |
| **Access-based** | Track access patterns, move unused data |
| **Size-based** | Large objects to cheaper storage |
| **Manual policy** | Business rules define tier |

### Database Tiering

```
Elasticsearch:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Hot Nodes  │    │ Warm Nodes  │    │ Cold Nodes  │
│  (SSD, 64GB)│ →  │ (HDD, 32GB) │ →  │ (HDD, 16GB) │
│  Write here │    │ Read-only   │    │ Read-only   │
└─────────────┘    └─────────────┘    └─────────────┘

Index lifecycle management (ILM):
- Index < 7 days: Hot (fast writes, frequent reads)
- Index 7-30 days: Warm (read-only, occasional access)
- Index > 30 days: Cold (compressed, rare access)
- Index > 90 days: Delete or frozen
```

### Cloud Storage Lifecycle Rules

```yaml
# AWS S3 Lifecycle Configuration
Rules:
  - ID: TierData
    Status: Enabled
    Transitions:
      - Days: 30
        StorageClass: STANDARD_IA
      - Days: 90
        StorageClass: GLACIER
      - Days: 365
        StorageClass: DEEP_ARCHIVE
    Expiration:
      Days: 2555  # 7 years
```

### Benefits

| Benefit | Impact |
|---------|--------|
| Cost reduction | 50-90% savings on storage |
| Performance | Hot data on fast storage |
| Compliance | Retain data affordably |
| Scalability | Store more data overall |

---

## Otvet (RU)

**Тиринг данных** классифицирует данные по частоте доступа и хранит их на соответствующих типах хранилища для баланса стоимости и производительности.

### Три уровня

```
┌─────────────────────────────────────────────────────────────┐
│                      ГОРЯЧИЕ ДАННЫЕ                          │
│  • Частый доступ (ежедневно/ежечасно)                       │
│  • Нужна минимальная задержка                               │
│  • Примеры: Текущие транзакции, live дашборды               │
│  • Хранение: SSD, кеш в памяти                              │
│  • Стоимость: $$$                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       ТЁПЛЫЕ ДАННЫЕ                          │
│  • Периодический доступ (еженедельно/ежемесячно)            │
│  • Умеренная задержка допустима                             │
│  • Примеры: Недавние отчёты, данные за квартал              │
│  • Хранение: HDD, стандартное облачное хранилище            │
│  • Стоимость: $$                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      ХОЛОДНЫЕ ДАННЫЕ                         │
│  • Редкий доступ (раз в год или реже)                       │
│  • Высокая задержка допустима (минуты-часы)                 │
│  • Примеры: Архивы, данные для compliance                   │
│  • Хранение: Glacier, архивное хранилище                    │
│  • Стоимость: $                                             │
└─────────────────────────────────────────────────────────────┘
```

### Сравнение стоимости (AWS)

| Уровень | Класс хранения | $/ГБ/месяц | Получение |
|---------|----------------|------------|-----------|
| Горячий | S3 Standard | $0.023 | Мгновенно |
| Тёплый | S3 Infrequent Access | $0.0125 | Мгновенно (плата за получение) |
| Холодный | S3 Glacier | $0.004 | Минуты-часы |
| Архив | S3 Glacier Deep Archive | $0.00099 | 12-48 часов |

### Типичный жизненный цикл данных

```
День 0-7:    ГОРЯЧИЕ → Быстрый SSD, кеш в памяти
День 7-30:   ГОРЯЧИЕ → Стандартный SSD/база данных
День 30-90:  ТЁПЛЫЕ  → Стандартное хранилище, сжатие
День 90-365: ХОЛОДНЫЕ→ Архивное хранилище
Год 1+:      АРХИВ   → Deep archive

Пример: Данные заказов интернет-магазина
┌──────────────────────────────────────────────────────────┐
│ Заказы за сегодня   → Redis кеш + Primary DB (ГОРЯЧИЕ)   │
│ Заказы за неделю    → Primary DB (ГОРЯЧИЕ)               │
│ Заказы за месяц     → Replica DB, сжатые (ТЁПЛЫЕ)        │
│ Заказы за год       → S3 Infrequent Access (ХОЛОДНЫЕ)    │
│ Старые заказы       → Glacier (АРХИВ)                    │
└──────────────────────────────────────────────────────────┘
```

### Стратегии реализации

| Стратегия | Как работает |
|-----------|--------------|
| **По времени** | Перемещение по возрасту данных |
| **По доступу** | Отслеживание паттернов доступа |
| **По размеру** | Большие объекты в дешёвое хранилище |
| **Ручная политика** | Бизнес-правила определяют уровень |

### Преимущества

| Преимущество | Эффект |
|--------------|--------|
| Снижение затрат | Экономия 50-90% на хранении |
| Производительность | Горячие данные на быстром хранилище |
| Соответствие требованиям | Хранить данные доступно |
| Масштабируемость | Хранить больше данных |

---

## Follow-ups

- How do you determine the access patterns for tiering?
- What is intelligent tiering and how does it work?
- How do you handle data that needs to be "reheated"?
