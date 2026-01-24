---
id: sysdes-068
title: Design Web Crawler
aliases:
- Design Web Crawler
- Web Spider
- Googlebot
topic: system-design
subtopics:
- design-problems
- distributed-systems
- data-processing
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-search-autocomplete--system-design--hard
- q-elasticsearch-full-text-search--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- distributed-systems
- system-design
anki_cards:
- slug: sysdes-068-0-en
  language: en
  anki_id: 1769160579878
  synced_at: '2026-01-23T13:29:45.850352'
- slug: sysdes-068-0-ru
  language: ru
  anki_id: 1769160579899
  synced_at: '2026-01-23T13:29:45.852509'
---
# Question (EN)
> Design a web crawler that can crawl billions of web pages efficiently.

# Vopros (RU)
> Спроектируйте веб-краулер, который может эффективно обходить миллиарды веб-страниц.

---

## Answer (EN)

### Requirements

**Functional**: Crawl web pages, extract content, follow links, respect robots.txt
**Non-functional**: Scalable (billions of pages), polite (don't overload sites), fresh content

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      URL Frontier                           │
│            (Priority queue of URLs to crawl)               │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Crawler Workers                          │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│   │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker N │  │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Content Processor                         │
│      (Parse HTML, Extract links, Extract content)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │   Link    │   │  Content  │   │    URL    │
    │ Extractor │   │   Store   │   │   Dedup   │
    └───────────┘   └───────────┘   └───────────┘
```

### Crawl Process

```
1. Get URL from frontier (priority queue)
2. Check robots.txt (cached per domain)
3. Fetch page (with politeness delay)
4. Parse HTML
5. Extract and normalize links
6. Deduplicate URLs
7. Store content
8. Add new URLs to frontier
9. Repeat
```

### URL Frontier Design

```
Priority considerations:
- PageRank/importance
- Freshness (news sites more often)
- Domain diversity (spread load)

Structure:
┌──────────────────────────────────────────┐
│              URL Frontier                 │
│  ┌────────────────────────────────────┐  │
│  │  Front Queues (by priority)        │  │
│  │  [High] [Medium] [Low]             │  │
│  └────────────────────────────────────┘  │
│                   │                       │
│  ┌────────────────▼───────────────────┐  │
│  │  Back Queues (by domain)           │  │
│  │  [site-a.com] [site-b.com] [...]   │  │
│  │  (ensures politeness per domain)   │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

### Politeness

```
Rules:
1. Respect robots.txt
2. Crawl-delay directive
3. Max requests per domain (e.g., 1 req/sec)
4. Avoid peak hours for site

Implementation:
- Per-domain rate limiting
- Distributed semaphores
- Domain-to-worker mapping
```

### URL Deduplication

```
Challenge: Billions of URLs, need O(1) lookup

Solutions:
1. Bloom filter (probabilistic, space-efficient)
   - 1% false positive acceptable
   - Memory: ~10 bits per URL

2. URL fingerprinting
   - MD5/SHA hash of normalized URL
   - Store in distributed cache

Normalization:
- Lowercase domain
- Remove default ports
- Sort query parameters
- Handle trailing slashes
```

### Content Storage

```
Storage hierarchy:
┌────────────────┐
│  Hot Storage   │  Recent, frequently accessed
│    (SSD)       │
├────────────────┤
│  Warm Storage  │  Older, less accessed
│    (HDD)       │
├────────────────┤
│  Cold Storage  │  Archive, rarely accessed
│    (S3)        │
└────────────────┘

Schema:
{
  url: "https://example.com/page",
  content_hash: "sha256...",
  crawl_timestamp: "2024-01-15T10:00:00Z",
  content: "<html>...</html>",
  links: ["url1", "url2", ...],
  http_status: 200
}
```

### Scale Numbers

```
Web scale:
- ~50 billion web pages
- Crawl 1 billion pages/day
- ~10,000 pages/second

Per page:
- Average size: 500KB
- Parse time: 10ms
- Network: 100ms
```

---

## Otvet (RU)

### Требования

**Функциональные**: Обход веб-страниц, извлечение контента, переход по ссылкам, соблюдение robots.txt
**Нефункциональные**: Масштабируемый (миллиарды страниц), вежливый (не перегружать сайты), свежий контент

### Процесс краулинга

```
1. Получить URL из frontier (очередь с приоритетами)
2. Проверить robots.txt (кешированный per domain)
3. Скачать страницу (с вежливой задержкой)
4. Распарсить HTML
5. Извлечь и нормализовать ссылки
6. Дедуплицировать URL
7. Сохранить контент
8. Добавить новые URL в frontier
9. Повторить
```

### Дизайн URL Frontier

```
Соображения приоритета:
- PageRank/важность
- Свежесть (новостные сайты чаще)
- Разнообразие доменов

Структура:
┌──────────────────────────────────────────┐
│              URL Frontier                 │
│  Front Queues (по приоритету)            │
│  [High] [Medium] [Low]                   │
│                   │                       │
│  Back Queues (по домену)                 │
│  [site-a.com] [site-b.com] [...]         │
│  (обеспечивает вежливость per domain)   │
└──────────────────────────────────────────┘
```

### Вежливость (Politeness)

```
Правила:
1. Соблюдать robots.txt
2. Директива crawl-delay
3. Max запросов на домен (напр. 1 req/sec)
4. Избегать пиковых часов сайта

Реализация:
- Per-domain rate limiting
- Распределённые семафоры
- Mapping домен-к-worker
```

### Дедупликация URL

```
Проблема: Миллиарды URL, нужен O(1) lookup

Решения:
1. Bloom filter (вероятностный, экономит место)
   - 1% false positive приемлемо
   - Память: ~10 бит на URL

2. Fingerprinting URL
   - MD5/SHA хеш нормализованного URL
   - Хранить в распределённом кеше
```

### Масштабные числа

```
Масштаб веба:
- ~50 миллиардов веб-страниц
- Обход 1 миллиарда страниц/день
- ~10,000 страниц/секунду

На страницу:
- Средний размер: 500KB
- Время парсинга: 10мс
- Сеть: 100мс
```

---

## Follow-ups

- How do you detect and handle spider traps?
- How do you prioritize which pages to re-crawl?
- How do you handle JavaScript-rendered content?
