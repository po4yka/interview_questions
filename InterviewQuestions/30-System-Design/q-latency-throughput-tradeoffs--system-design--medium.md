---
id: sysdes-033
title: Latency vs Throughput Tradeoffs
aliases:
- Latency vs Throughput
- Performance Tradeoffs
topic: system-design
subtopics:
- performance
- scalability
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
- q-back-of-envelope-estimation--system-design--medium
- q-caching-strategies--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- performance
- difficulty/medium
- scalability
- system-design
anki_cards:
- slug: sysdes-033-0-en
  language: en
  anki_id: 1769159521647
  synced_at: '2026-01-23T13:49:17.821424'
- slug: sysdes-033-0-ru
  language: ru
  anki_id: 1769159521669
  synced_at: '2026-01-23T13:49:17.822623'
---
# Question (EN)
> What is the difference between latency and throughput? How do you optimize for each, and what are the tradeoffs?

# Vopros (RU)
> В чем разница между задержкой и пропускной способностью? Как оптимизировать каждую, и какие существуют компромиссы?

---

## Answer (EN)

**Latency** is the time to complete a single operation. **Throughput** is the number of operations per unit time.

### Definitions

| Metric | Definition | Unit | Example |
|--------|------------|------|---------|
| Latency | Time for one request | ms | 50ms response time |
| Throughput | Requests processed | req/s | 10,000 RPS |

### The Tradeoff

```
Low latency often means: dedicated resources, no batching
High throughput often means: batching, queuing, shared resources

Example - Database writes:
- Low latency: Write immediately, fsync each write
- High throughput: Batch writes, fsync periodically
```

### Optimization Strategies

**For Low Latency:**
- Caching (eliminate work)
- Connection pooling (reduce setup time)
- Geo-distribution (reduce network distance)
- SSD over HDD
- Avoid batching

**For High Throughput:**
- Batching requests
- Async processing
- Horizontal scaling
- Connection multiplexing
- Compression

### Measuring Latency

```
Percentiles matter more than averages:
- p50 (median): 50% of requests faster
- p95: 95% of requests faster
- p99: 99% of requests faster (tail latency)

Example:
  Average: 50ms
  p50: 30ms
  p95: 100ms
  p99: 500ms (long tail indicates problems)
```

### Real-World Examples

| System | Priority | Why |
|--------|----------|-----|
| Trading platform | Latency | Microseconds matter |
| Video streaming | Throughput | Serve many concurrent users |
| Gaming | Latency | Real-time responsiveness |
| Batch processing | Throughput | Process large datasets |
| Search engine | Both | Fast results, many queries |

### Little's Law

```
L = λ * W

L = average items in system
λ = throughput (items/sec)
W = average latency (sec)

To increase throughput with same resources:
reduce latency (W) → more capacity (L/W)
```

---

## Otvet (RU)

**Задержка (Latency)** - время выполнения одной операции. **Пропускная способность (Throughput)** - количество операций в единицу времени.

### Определения

| Метрика | Определение | Единица | Пример |
|---------|-------------|---------|--------|
| Задержка | Время одного запроса | мс | 50мс время ответа |
| Пропускная способность | Обработанных запросов | зап/с | 10,000 RPS |

### Компромисс

```
Низкая задержка часто означает: выделенные ресурсы, без батчинга
Высокая пропускная способность часто означает: батчинг, очереди, общие ресурсы

Пример - записи в БД:
- Низкая задержка: Писать сразу, fsync каждой записи
- Высокая пропускная способность: Батчить записи, fsync периодически
```

### Стратегии оптимизации

**Для низкой задержки:**
- Кеширование (исключить работу)
- Пулы соединений (уменьшить время установки)
- Гео-распределение (уменьшить сетевое расстояние)
- SSD вместо HDD
- Избегать батчинга

**Для высокой пропускной способности:**
- Батчинг запросов
- Асинхронная обработка
- Горизонтальное масштабирование
- Мультиплексирование соединений
- Сжатие

### Измерение задержки

```
Перцентили важнее средних:
- p50 (медиана): 50% запросов быстрее
- p95: 95% запросов быстрее
- p99: 99% запросов быстрее (хвостовая задержка)

Пример:
  Среднее: 50мс
  p50: 30мс
  p95: 100мс
  p99: 500мс (длинный хвост указывает на проблемы)
```

### Закон Литтла

```
L = λ * W

L = среднее количество элементов в системе
λ = пропускная способность (элементов/сек)
W = средняя задержка (сек)
```

---

## Follow-ups

- What causes tail latency (p99)?
- How does queuing theory relate to latency?
- What is the difference between response time and latency?
