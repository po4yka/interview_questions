---
id: sysdes-069
title: Design Search Autocomplete
aliases:
- Design Autocomplete
- Typeahead
- Search Suggestions
topic: system-design
subtopics:
- design-problems
- search
- data-structures
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-elasticsearch-full-text-search--system-design--medium
- q-design-web-crawler--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- search
- system-design
anki_cards:
- slug: sysdes-069-0-en
  language: en
  anki_id: 1769160584827
  synced_at: '2026-01-23T13:49:17.842817'
- slug: sysdes-069-0-ru
  language: ru
  anki_id: 1769160584849
  synced_at: '2026-01-23T13:49:17.844069'
---
# Question (EN)
> Design a search autocomplete system that suggests queries as users type.

# Vopros (RU)
> Спроектируйте систему автодополнения поиска, которая предлагает запросы по мере ввода.

---

## Answer (EN)

### Requirements

**Functional**: Return top suggestions as user types, sorted by relevance/popularity
**Non-functional**: <100ms latency, handle billions of queries, real-time updates

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                               │
│    User types: "face" → debounce → API call                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    API Gateway                              │
│               (Rate limiting, Load balancing)              │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               Autocomplete Service                          │
│    (Query trie, Return top-k suggestions)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Trie Storage                             │
│              (In-memory or Redis)                          │
└─────────────────────────────────────────────────────────────┘
```

### Trie Data Structure

```
Trie for ["face", "facebook", "facetime", "factory"]:

        root
          │
          f
          │
          a
          │
          c
         / \
        e   t
       /│    \
      b t     o
      │ │     │
      o i     r
      │ │     │
      o m     y
      │ │
      k e

Each node stores:
- Character
- Children
- isEndOfWord
- Frequency/score (for ranking)
```

### Ranking Suggestions

```
Factors:
1. Search frequency (most important)
2. Recency (trending queries)
3. Personalization (user history)
4. Geographic relevance

Score = 0.7 * frequency + 0.2 * recency + 0.1 * personalization

Top-k retrieval:
- Store top suggestions at each trie node
- Pre-compute during index build
- O(prefix_length) lookup time
```

### Data Collection Pipeline

```
Search queries → Kafka → Aggregator → Trie Builder → Deploy

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Search    │───►│   Kafka     │───►│ Aggregator  │
│   Logs      │    │   Topic     │    │  (Spark)    │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Trie Builder   │
                                    │ (Hourly/Daily)  │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │    Deploy to    │
                                    │    Servers      │
                                    └─────────────────┘
```

### Optimization Strategies

| Strategy | Benefit |
|----------|---------|
| Client debouncing | Reduce API calls (wait 100-200ms) |
| Browser caching | Cache frequent prefixes |
| CDN for static | Pre-computed top queries |
| Sampling | Don't count every query |
| Sharding by prefix | Distribute load |

### Sharding

```
Shard by first character(s):
- Shard 1: a-f
- Shard 2: g-l
- Shard 3: m-r
- Shard 4: s-z

Or consistent hashing on prefix hash

Request routing:
prefix="face" → hash("fa") → Shard 1
```

### Real-time Updates

```
For trending queries:

Approach 1: Periodic rebuild (every hour)
- Simple, but stale data

Approach 2: Streaming updates
- Kafka Streams / Flink
- Update trie in real-time
- More complex

Hybrid:
- Batch update for frequency
- Real-time for trending/breaking news
```

### Scale Numbers

```
Google scale:
- 5 billion searches/day
- ~60K queries/second
- Millions of unique queries

Storage:
- Trie with 10M terms: ~10GB
- Can fit in memory per shard
```

---

## Otvet (RU)

### Требования

**Функциональные**: Возвращать топ предложений по мере ввода, отсортированные по релевантности
**Нефункциональные**: <100мс задержка, миллиарды запросов, real-time обновления

### Структура данных Trie

```
Trie для ["face", "facebook", "facetime", "factory"]:

        root
          │
          f
          │
          a
          │
          c
         / \
        e   t
       /│    \
      b t     o
      ...    ...

Каждый узел хранит:
- Символ
- Дочерние узлы
- isEndOfWord
- Частота/score (для ранжирования)
```

### Ранжирование предложений

```
Факторы:
1. Частота поиска (самый важный)
2. Актуальность (трендовые запросы)
3. Персонализация (история пользователя)
4. Географическая релевантность

Score = 0.7 * frequency + 0.2 * recency + 0.1 * personalization

Top-k извлечение:
- Хранить топ предложений на каждом узле trie
- Предвычислять при построении индекса
- O(prefix_length) время lookup
```

### Pipeline сбора данных

```
Search queries → Kafka → Aggregator → Trie Builder → Deploy

Search Logs → Kafka Topic → Aggregator (Spark) → Trie Builder → Deploy
```

### Стратегии оптимизации

| Стратегия | Польза |
|-----------|--------|
| Debouncing на клиенте | Меньше API вызовов (ждать 100-200мс) |
| Кеширование в браузере | Кешировать частые префиксы |
| CDN для статики | Предвычисленные топ запросы |
| Сэмплирование | Не считать каждый запрос |
| Шардинг по префиксу | Распределить нагрузку |

### Шардинг

```
Шардинг по первым символам:
- Shard 1: a-f
- Shard 2: g-l
- Shard 3: m-r
- Shard 4: s-z

Или consistent hashing на хеше префикса
```

### Real-time обновления

```
Для трендовых запросов:

Подход 1: Периодическая пересборка (каждый час)
- Просто, но устаревшие данные

Подход 2: Streaming обновления
- Kafka Streams / Flink
- Обновление trie в real-time
- Сложнее

Гибридный:
- Batch обновление для частоты
- Real-time для трендов/новостей
```

---

## Follow-ups

- How do you handle typos and spelling corrections?
- How do you personalize suggestions per user?
- How do you filter inappropriate suggestions?
