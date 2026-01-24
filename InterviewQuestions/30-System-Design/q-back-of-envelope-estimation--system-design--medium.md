---
id: sysdes-032
title: Back-of-Envelope Estimation
aliases:
- Capacity Estimation
- System Estimation
topic: system-design
subtopics:
- estimation
- capacity-planning
- scalability
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-horizontal-vertical-scaling--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- estimation
- difficulty/medium
- capacity-planning
- system-design
anki_cards:
- slug: sysdes-032-0-en
  language: en
  anki_id: 1769159520147
  synced_at: '2026-01-23T13:49:17.725551'
- slug: sysdes-032-0-ru
  language: ru
  anki_id: 1769159520169
  synced_at: '2026-01-23T13:49:17.726878'
---
# Question (EN)
> How do you perform back-of-envelope estimation for system design? What are the key numbers to know?

# Vopros (RU)
> Как выполнять приблизительные расчеты для проектирования систем? Какие ключевые числа нужно знать?

---

## Answer (EN)

**Back-of-envelope estimation** helps quickly assess system requirements for storage, bandwidth, and compute.

### Key Numbers to Memorize

**Time:**
- 1 day = 86,400 seconds (~100K)
- 1 month = 2.5M seconds
- 1 year = 31M seconds

**Data sizes:**
- 1 char = 1 byte (ASCII) or 2-4 bytes (Unicode)
- UUID = 36 bytes (string) or 16 bytes (binary)
- Timestamp = 8 bytes
- Average tweet/post = 300 bytes
- Average image = 300KB-2MB
- Average video (1 min) = 50MB

**Latency:**
- L1 cache: 1ns
- L2 cache: 4ns
- RAM: 100ns
- SSD random read: 100us
- HDD seek: 10ms
- Network roundtrip (same DC): 0.5ms
- Network roundtrip (cross-continent): 150ms

### Estimation Framework

```
1. Clarify scale: DAU, MAU, requests/day
2. Calculate QPS: requests / 86400
3. Peak QPS: Average * 2-3x
4. Storage: items * size * retention
5. Bandwidth: QPS * item_size
```

### Example: Twitter-like Service

```
Given: 300M MAU, 50% DAU, 2 tweets/user/day

Writes:
- 150M DAU * 2 = 300M tweets/day
- QPS = 300M / 86400 = 3,500 tweets/sec
- Peak = 3,500 * 3 = 10,500/sec

Storage (1 year):
- 300M tweets * 365 days * 300 bytes = 33TB
- With media: 33TB * 10 = 330TB

Reads (10:1 read/write):
- 35,000 reads/sec average
- 105,000 reads/sec peak
```

### Quick Conversions

| From | To | Factor |
|------|----|--------|
| Per day | Per second | / 100,000 |
| GB | TB | / 1,000 |
| Million | Billion | / 1,000 |

---

## Otvet (RU)

**Приблизительные расчеты** помогают быстро оценить требования системы к хранению, пропускной способности и вычислениям.

### Ключевые числа для запоминания

**Время:**
- 1 день = 86,400 секунд (~100K)
- 1 месяц = 2.5M секунд
- 1 год = 31M секунд

**Размеры данных:**
- 1 символ = 1 байт (ASCII) или 2-4 байта (Unicode)
- UUID = 36 байт (строка) или 16 байт (бинарный)
- Timestamp = 8 байт
- Средний твит/пост = 300 байт
- Среднее изображение = 300KB-2MB
- Среднее видео (1 мин) = 50MB

**Задержки:**
- L1 кеш: 1нс
- L2 кеш: 4нс
- RAM: 100нс
- SSD случайное чтение: 100мкс
- HDD seek: 10мс
- Сетевой roundtrip (тот же DC): 0.5мс
- Сетевой roundtrip (между континентами): 150мс

### Фреймворк оценки

```
1. Уточнить масштаб: DAU, MAU, запросов/день
2. Рассчитать QPS: запросы / 86400
3. Пиковый QPS: Средний * 2-3x
4. Хранение: объекты * размер * срок хранения
5. Пропускная способность: QPS * размер_объекта
```

### Пример: Twitter-подобный сервис

```
Дано: 300M MAU, 50% DAU, 2 твита/пользователь/день

Записи:
- 150M DAU * 2 = 300M твитов/день
- QPS = 300M / 86400 = 3,500 твитов/сек
- Пик = 3,500 * 3 = 10,500/сек

Хранение (1 год):
- 300M твитов * 365 дней * 300 байт = 33TB
- С медиа: 33TB * 10 = 330TB
```

---

## Follow-ups

- How do you estimate cache hit ratio?
- What factors affect peak-to-average ratio?
- How do you estimate database IOPS requirements?
