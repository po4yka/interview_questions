---
id: sysdes-056
title: Time-Series Databases
aliases:
- Time-Series Database
- TSDB
- InfluxDB
- TimescaleDB
topic: system-design
subtopics:
- data-management
- databases
- monitoring
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-metrics-logs-traces--system-design--medium
- q-database-indexing--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- data-management
- difficulty/medium
- databases
- system-design
anki_cards:
- slug: sysdes-056-0-en
  language: en
  anki_id: 1769160584874
  synced_at: '2026-01-23T13:49:17.845209'
- slug: sysdes-056-0-ru
  language: ru
  anki_id: 1769160584899
  synced_at: '2026-01-23T13:49:17.846270'
---
# Question (EN)
> What is a time-series database? When would you use one instead of a traditional relational database?

# Vopros (RU)
> Что такое база данных временных рядов? Когда её использовать вместо традиционной реляционной БД?

---

## Answer (EN)

**Time-series database (TSDB)** is optimized for storing and querying data indexed by time, such as metrics, events, and measurements.

### Characteristics of Time-Series Data

```
Data point structure:
{
  timestamp: 2024-01-15T10:30:00Z,
  metric: "cpu_usage",
  tags: {host: "server-1", region: "us-east"},
  value: 78.5
}

Properties:
- Time is primary index
- High write throughput (millions/sec)
- Data arrives in chronological order
- Older data less frequently accessed
- Queries often aggregations over time ranges
```

### TSDB vs Relational DB

| Aspect | TSDB | Relational DB |
|--------|------|---------------|
| Write pattern | Append-only, sequential | Random inserts/updates |
| Query pattern | Time-range aggregations | Arbitrary queries |
| Compression | Excellent (time-based) | General purpose |
| Retention | Automatic data expiration | Manual management |
| Scale | Billions of data points | Millions of rows |

### Key Features

```
1. Time-based compression
   Raw:    10:00:01=50, 10:00:02=51, 10:00:03=50, 10:00:04=52
   Stored: 10:00:01=50, delta=[+1,-1,+2] → 80% compression

2. Automatic downsampling
   Raw data:    1-second resolution → keep 7 days
   Downsampled: 1-minute averages → keep 30 days
                1-hour averages → keep 1 year

3. Time-based partitioning
   ┌────────────┬────────────┬────────────┐
   │ Jan 2024   │ Feb 2024   │ Mar 2024   │
   │ (archived) │ (warm)     │ (hot)      │
   └────────────┴────────────┴────────────┘
```

### Use Cases

| Use Case | Example |
|----------|---------|
| Infrastructure monitoring | CPU, memory, disk metrics |
| IoT sensor data | Temperature, humidity readings |
| Financial data | Stock prices, trading volumes |
| Application metrics | Request latency, error rates |
| Log analytics | Event counts over time |

### Popular TSDBs

| Database | Type | Notes |
|----------|------|-------|
| InfluxDB | Native TSDB | Popular, InfluxQL/Flux |
| TimescaleDB | PostgreSQL extension | SQL compatible |
| Prometheus | Metrics-focused | Pull-based, Kubernetes native |
| ClickHouse | Column-store | Fast analytics |
| Amazon Timestream | Managed | AWS native |

### Query Example (InfluxQL)

```sql
-- Average CPU per host over last hour, grouped by 5 minutes
SELECT MEAN(cpu_usage)
FROM metrics
WHERE time > now() - 1h
GROUP BY time(5m), host
```

---

## Otvet (RU)

**База данных временных рядов (TSDB)** оптимизирована для хранения и запросов данных, индексированных по времени: метрик, событий, измерений.

### Характеристики данных временных рядов

```
Структура точки данных:
{
  timestamp: 2024-01-15T10:30:00Z,
  metric: "cpu_usage",
  tags: {host: "server-1", region: "us-east"},
  value: 78.5
}

Свойства:
- Время - первичный индекс
- Высокая пропускная способность записи
- Данные приходят хронологически
- Старые данные реже запрашиваются
- Запросы часто - агрегации по временным диапазонам
```

### TSDB vs Реляционная БД

| Аспект | TSDB | Реляционная БД |
|--------|------|----------------|
| Паттерн записи | Append-only, последовательный | Случайные вставки/обновления |
| Паттерн запросов | Агрегации по временным диапазонам | Произвольные запросы |
| Сжатие | Отличное (на основе времени) | Общего назначения |
| Retention | Автоматическое истечение данных | Ручное управление |

### Ключевые возможности

```
1. Сжатие на основе времени
   80% сжатие через delta-encoding

2. Автоматический downsampling
   Сырые данные: 1-секундное разрешение → хранить 7 дней
   Downsampled: 1-минутные средние → хранить 30 дней

3. Партиционирование по времени
   Hot/warm/cold тиры для разных периодов
```

### Применение

| Случай | Пример |
|--------|--------|
| Мониторинг инфраструктуры | CPU, память, диск |
| IoT сенсоры | Температура, влажность |
| Финансовые данные | Цены акций, объёмы торгов |
| Метрики приложений | Задержка запросов, error rates |

### Популярные TSDB

| База | Тип | Примечания |
|------|-----|------------|
| InfluxDB | Native TSDB | Популярная, InfluxQL/Flux |
| TimescaleDB | Расширение PostgreSQL | SQL совместимая |
| Prometheus | Фокус на метриках | Pull-based, Kubernetes native |
| ClickHouse | Column-store | Быстрая аналитика |

---

## Follow-ups

- How does InfluxDB differ from Prometheus?
- What is the Gorilla compression algorithm used in TSDBs?
- How do you handle high cardinality in time-series data?
