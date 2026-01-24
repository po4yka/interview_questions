---
id: sysdes-075
title: Data Lake vs Data Warehouse
aliases:
- Data Lake
- Data Warehouse
- Analytics Storage
topic: system-design
subtopics:
- data-management
- analytics
- storage
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-sql-vs-nosql--system-design--medium
- q-object-vs-block-storage--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- data-management
- difficulty/medium
- analytics
- system-design
anki_cards:
- slug: sysdes-075-0-en
  language: en
  anki_id: 1769161754733
  synced_at: '2026-01-23T13:49:17.790008'
- slug: sysdes-075-0-ru
  language: ru
  anki_id: 1769161754758
  synced_at: '2026-01-23T13:49:17.791739'
---
# Question (EN)
> What is the difference between a Data Lake and a Data Warehouse? When would you use each?

# Vopros (RU)
> В чём разница между Data Lake и Data Warehouse? Когда использовать каждый?

---

## Answer (EN)

**Data Warehouse** stores structured, processed data for business intelligence. **Data Lake** stores raw data in any format for flexible analysis.

### Key Differences

| Aspect | Data Warehouse | Data Lake |
|--------|----------------|-----------|
| Data type | Structured only | Structured, semi-structured, unstructured |
| Schema | Schema-on-write | Schema-on-read |
| Processing | ETL (Extract, Transform, Load) | ELT (Extract, Load, Transform) |
| Users | Business analysts, BI tools | Data scientists, ML engineers |
| Storage cost | Higher (optimized storage) | Lower (commodity storage) |
| Query speed | Fast (pre-optimized) | Variable (depends on processing) |
| Data quality | High (curated) | Variable (raw) |

### Architecture Comparison

```
Data Warehouse:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Source     │     │    ETL      │     │  Warehouse  │
│  Systems    │ --> │  Pipeline   │ --> │  (Schema)   │ --> BI Tools
│             │     │  Transform  │     │  Snowflake  │
└─────────────┘     └─────────────┘     └─────────────┘

Data Lake:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Source     │     │    Ingest   │     │  Data Lake  │
│  Systems    │ --> │  (Raw)      │ --> │  (S3/HDFS)  │ --> Transform on Read
│             │     │             │     │  Any Format │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Schema-on-Write vs Schema-on-Read

```
Schema-on-Write (Warehouse):
- Define schema BEFORE loading data
- Data validated and transformed during load
- Queries fast because data is organized
- Less flexible for new use cases

Schema-on-Read (Lake):
- Store raw data without schema
- Apply schema when querying/analyzing
- Flexible for exploration
- Can be slow, requires more processing
```

### Data Warehouse Examples

| Platform | Type | Best For |
|----------|------|----------|
| **Snowflake** | Cloud | Scalability, separation of compute/storage |
| **BigQuery** | Cloud | Serverless, ML integration |
| **Redshift** | Cloud | AWS ecosystem |
| **Databricks SQL** | Cloud | Unified with ML platform |

### Data Lake Examples

| Platform | Storage | Processing |
|----------|---------|------------|
| **S3 + Athena** | Object storage | Serverless SQL |
| **Azure Data Lake** | Blob storage | Spark, Synapse |
| **Databricks** | Delta Lake | Unified analytics |
| **Hadoop HDFS** | Distributed FS | MapReduce, Spark |

### Modern: Data Lakehouse

```
Combines best of both:

┌─────────────────────────────────────────────────┐
│                  Data Lakehouse                  │
│  ┌───────────────────────────────────────────┐  │
│  │         Metadata & Governance Layer        │  │
│  │         (Schema, ACID, Time Travel)        │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │         Open File Formats                  │  │
│  │         (Parquet, Delta, Iceberg)          │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │         Object Storage (S3, ADLS)          │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘

Benefits:
- Lake cost with warehouse performance
- ACID transactions on files
- Schema enforcement + flexibility
- Single source for BI and ML
```

### When to Use

| Use Case | Choice | Reason |
|----------|--------|--------|
| BI dashboards, reports | Warehouse | Fast, reliable queries |
| ML training, exploration | Lake | Flexible, raw data |
| Real-time analytics | Warehouse/Stream | Pre-computed metrics |
| Log analysis | Lake | Unstructured, high volume |
| Regulatory compliance | Warehouse | Data quality, lineage |
| Cost-sensitive storage | Lake | Cheap object storage |

---

## Otvet (RU)

**Data Warehouse** хранит структурированные, обработанные данные для бизнес-аналитики. **Data Lake** хранит сырые данные в любом формате для гибкого анализа.

### Ключевые различия

| Аспект | Data Warehouse | Data Lake |
|--------|----------------|-----------|
| Тип данных | Только структурированные | Любые |
| Схема | Schema-on-write | Schema-on-read |
| Обработка | ETL | ELT |
| Пользователи | Бизнес-аналитики | Data scientists |
| Стоимость хранения | Выше | Ниже |
| Скорость запросов | Быстрая | Переменная |
| Качество данных | Высокое (курируемые) | Переменное (сырые) |

### Schema-on-Write vs Schema-on-Read

```
Schema-on-Write (Warehouse):
- Определить схему ДО загрузки данных
- Данные валидируются при загрузке
- Запросы быстрые
- Менее гибко для новых задач

Schema-on-Read (Lake):
- Хранить сырые данные без схемы
- Применять схему при запросе
- Гибко для исследований
- Может быть медленно
```

### Современный подход: Data Lakehouse

```
Объединяет лучшее от обоих:

┌─────────────────────────────────────────────────┐
│                  Data Lakehouse                  │
│  ┌───────────────────────────────────────────┐  │
│  │      Метаданные и управление               │  │
│  │      (Схема, ACID, Time Travel)            │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │      Открытые форматы файлов               │  │
│  │      (Parquet, Delta, Iceberg)             │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │      Объектное хранилище (S3, ADLS)        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘

Преимущества:
- Стоимость озера с производительностью хранилища
- ACID транзакции на файлах
- Единый источник для BI и ML
```

### Когда использовать

| Сценарий | Выбор | Причина |
|----------|-------|---------|
| BI дашборды, отчёты | Warehouse | Быстрые, надёжные запросы |
| ML обучение, исследование | Lake | Гибкость, сырые данные |
| Real-time аналитика | Warehouse/Stream | Предвычисленные метрики |
| Анализ логов | Lake | Неструктурированные, большой объём |
| Регуляторное соответствие | Warehouse | Качество данных, lineage |
| Экономия на хранении | Lake | Дешёвое объектное хранилище |

---

## Follow-ups

- What is a Data Lakehouse and why is it becoming popular?
- How do you handle data quality in a Data Lake?
- What are Delta Lake, Iceberg, and Hudi?
