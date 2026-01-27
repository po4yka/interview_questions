---
id: q-design-google-search
title: Design Google Search
aliases:
- Design Google Search
- Search Engine Design
- Web Search System
topic: system-design
subtopics:
- design-problems
- search-engine
- distributed-systems
- indexing
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-web-crawler--system-design--hard
- q-design-search-autocomplete--system-design--hard
- q-elasticsearch-full-text-search--system-design--medium
- q-consistent-hashing--system-design--hard
- q-caching-strategies--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/hard
- distributed-systems
- system-design
anki_cards:
- slug: q-design-google-search-0-en
  anki_id: null
  synced_at: null
- slug: q-design-google-search-0-ru
  anki_id: null
  synced_at: null
---

# Question (EN)
> How would you design a web search engine like Google?

# Vopros (RU)
> Как бы вы спроектировали поисковую систему, подобную Google?

---

## Answer (EN)

### Requirements

**Functional:**
- Index billions of web pages
- Return relevant results for text queries
- Sub-second query latency
- Spell correction and query suggestions
- Support for different content types (text, images, videos)

**Non-functional:**
- High availability (99.99%)
- Low latency (<500ms p99)
- Scalable to billions of queries/day
- Fresh index (pages updated within hours)

### Scale Estimation

```
Web scale:
- ~50 billion indexed web pages
- Average page size: 100KB (compressed: 10KB)
- Total index size: ~500 PB
- Queries: 8.5 billion/day = 100K QPS
- Peak: 200K QPS

Per query:
- Latency target: <200ms
- Pages to rank: millions -> top 10 results
```

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Query Flow                                   │
│                                                                      │
│  User Query                                                          │
│      │                                                               │
│      ▼                                                               │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────────────────┐   │
│  │   DNS    │───▶│Load Balancer │───▶│   Query Processing      │   │
│  │   CDN    │    │              │    │   - Tokenization        │   │
│  └──────────┘    └──────────────┘    │   - Spell correction    │   │
│                                       │   - Query expansion     │   │
│                                       └───────────┬─────────────┘   │
│                                                   │                  │
│                       ┌───────────────────────────┼──────────────┐  │
│                       │                           │              │  │
│                       ▼                           ▼              ▼  │
│               ┌──────────────┐          ┌──────────────┐  ┌────────┐│
│               │ Index Shards │          │   Web Cache  │  │ Ads    ││
│               │   (1000s)    │          │              │  │ System ││
│               └──────────────┘          └──────────────┘  └────────┘│
│                       │                                              │
│                       ▼                                              │
│               ┌──────────────┐                                       │
│               │   Ranking    │                                       │
│               │   Service    │                                       │
│               └──────────────┘                                       │
│                       │                                              │
│                       ▼                                              │
│               ┌──────────────┐                                       │
│               │   Results    │                                       │
│               │  Aggregator  │                                       │
│               └──────────────┘                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       Indexing Flow                                  │
│                                                                      │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐  │
│  │   Web     │───▶│  Content  │───▶│  Index    │───▶│  Index    │  │
│  │  Crawler  │    │ Processor │    │  Builder  │    │  Shards   │  │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘  │
│                         │                                            │
│                         ▼                                            │
│                   ┌───────────┐                                      │
│                   │  PageRank │                                      │
│                   │ Calculator│                                      │
│                   └───────────┘                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Component 1: Web Crawler

See: [[q-design-web-crawler--system-design--hard]]

```
Key responsibilities:
- Discover and download web pages
- Respect robots.txt and crawl rate limits
- Handle updates and recrawling
- Distributed across data centers

Scale:
- Crawl 1+ billion pages/day
- URL frontier with priority queue
- Politeness: 1 request/second per domain
```

### Component 2: Content Processing

```
Pipeline:
┌────────────────┐
│  Raw HTML      │
└───────┬────────┘
        ▼
┌────────────────┐
│  HTML Parser   │  Extract text, titles, headings
└───────┬────────┘
        ▼
┌────────────────┐
│  Tokenizer     │  Break text into tokens
└───────┬────────┘
        ▼
┌────────────────┐
│  Normalizer    │  Lowercase, stemming, lemmatization
└───────┬────────┘
        ▼
┌────────────────┐
│  Language      │  Detect language, filter spam
│  Detection     │
└───────┬────────┘
        ▼
┌────────────────┐
│  Entity        │  Extract people, places, dates
│  Extraction    │
└────────────────┘

Processing per document:
- Title, meta description, headings (H1-H6)
- Body text with position information
- Anchor text from incoming links
- URL structure and path
```

### Component 3: Inverted Index

```
Structure:
┌────────────────────────────────────────────────────────────┐
│                    Inverted Index                           │
│                                                             │
│  Term      │  Posting List                                  │
│  ──────────┼──────────────────────────────────────────────  │
│  "kotlin"  │  [doc1:5, doc2:12, doc3:1, doc47:3, ...]      │
│  "android" │  [doc1:8, doc5:15, doc12:2, ...]              │
│  "coroutine"│ [doc1:3, doc2:7, doc99:1, ...]               │
│                                                             │
│  Posting entry: (doc_id, term_frequency, positions[])       │
└────────────────────────────────────────────────────────────┘

Optimizations:
1. Delta encoding for doc IDs (save space)
2. Variable-byte encoding for frequencies
3. Skip pointers for faster intersection
4. Compression: ~2 bits per posting

Sharding strategy:
- By term (term-partitioned) - good for single-term queries
- By document (doc-partitioned) - good for multi-term queries
- Google uses document-partitioned with term partitioning for hot terms
```

### Component 4: PageRank Algorithm

```
Core idea: A page is important if important pages link to it

Formula:
PR(A) = (1-d) + d * Σ(PR(Ti)/C(Ti))

Where:
- d = damping factor (typically 0.85)
- Ti = pages linking to A
- C(Ti) = number of outbound links from Ti

Computation:
1. Initialize all pages with PR = 1/N
2. Iteratively update until convergence
3. Typically 50-100 iterations

Scale challenge:
- 50B pages = 50B nodes
- ~1 trillion edges
- MapReduce/Pregel for distributed computation

Modern additions:
- TrustRank (combat spam)
- Topic-sensitive PageRank
- Personalized PageRank
```

### Component 5: Query Processing

```
Query flow:
┌────────────────────────────────────────────────────────┐
│ 1. Query Parsing                                        │
│    "kotlin coroutines tutorial" →                       │
│    tokens: ["kotlin", "coroutines", "tutorial"]         │
│                                                         │
│ 2. Spell Correction                                     │
│    "kotlinn" → "kotlin" (edit distance, language model) │
│                                                         │
│ 3. Query Expansion                                      │
│    "kotlin" → "kotlin", "kotlinlang"                    │
│    Synonyms, stemming variants                          │
│                                                         │
│ 4. Query Understanding                                  │
│    Intent: informational                                │
│    Entity: "Kotlin" (programming language)              │
│                                                         │
│ 5. Index Lookup                                         │
│    Fetch posting lists, intersect, score                │
│                                                         │
│ 6. Ranking                                              │
│    Apply ranking model to top candidates                │
└────────────────────────────────────────────────────────┘
```

### Component 6: Ranking System

```
Two-phase ranking:

Phase 1: Candidate Generation (fast, coarse)
- Retrieve top ~10,000 candidates
- Use BM25 or simple TF-IDF
- Intersect posting lists

Phase 2: Re-ranking (slow, precise)
- Apply ML model to top candidates
- Consider 100s of features
- Return top 10-20 results

Ranking signals:
┌──────────────────────────────────────────────────────┐
│ Content signals:                                      │
│   - TF-IDF score                                     │
│   - BM25 score                                       │
│   - Title match                                      │
│   - URL match                                        │
│   - Content freshness                                │
│                                                       │
│ Authority signals:                                    │
│   - PageRank                                         │
│   - Domain authority                                 │
│   - Backlink quality/quantity                        │
│                                                       │
│ User signals:                                         │
│   - Click-through rate                               │
│   - Dwell time                                       │
│   - Bounce rate                                      │
│   - Pogo-sticking (quick back clicks)                │
│                                                       │
│ Quality signals:                                      │
│   - Content quality (E-E-A-T)                        │
│   - Site speed                                       │
│   - Mobile-friendliness                              │
│   - HTTPS                                            │
└──────────────────────────────────────────────────────┘

Modern ML ranking:
- Learning to Rank (LTR)
- BERT for semantic understanding
- Two-tower models for retrieval
```

### BM25 Formula

```
BM25 is the de-facto standard for text ranking:

score(D,Q) = Σ IDF(qi) * (f(qi,D) * (k1 + 1)) /
             (f(qi,D) + k1 * (1 - b + b * |D|/avgdl))

Where:
- f(qi,D) = term frequency in document
- |D| = document length
- avgdl = average document length
- k1 = 1.2-2.0 (term frequency saturation)
- b = 0.75 (length normalization)

IDF(qi) = log((N - n(qi) + 0.5) / (n(qi) + 0.5))

Where:
- N = total documents
- n(qi) = documents containing term
```

### Caching Strategy

```
Multi-level caching:
┌────────────────────────────────────────────────────────┐
│ Level 1: Result Cache                                   │
│   - Cache complete search results                       │
│   - Key: query hash + user context                     │
│   - Hit rate: ~30% (popular queries)                   │
│   - TTL: minutes to hours                              │
├────────────────────────────────────────────────────────┤
│ Level 2: Posting List Cache                            │
│   - Cache inverted index segments                      │
│   - Hot terms (the, is, and) always in memory          │
│   - Hit rate: ~60%                                     │
├────────────────────────────────────────────────────────┤
│ Level 3: Document Cache                                │
│   - Cache document metadata and snippets               │
│   - Avoid disk reads for ranking                       │
└────────────────────────────────────────────────────────┘

Query result distribution follows power law:
- Top 1% queries = 30% of traffic
- Top 10% queries = 70% of traffic
```

### Index Sharding

```
Document-partitioned architecture:

┌─────────────────────────────────────────────────────────┐
│                    Query Router                          │
│                         │                                │
│     ┌───────────────────┼───────────────────┐           │
│     ▼                   ▼                   ▼           │
│ ┌────────┐         ┌────────┐         ┌────────┐        │
│ │ Shard  │         │ Shard  │         │ Shard  │        │
│ │   1    │         │   2    │   ...   │   N    │        │
│ │        │         │        │         │        │        │
│ │ Docs   │         │ Docs   │         │ Docs   │        │
│ │ 1-1M   │         │ 1M-2M  │         │(N-1)M-│        │
│ └────────┘         └────────┘         └────────┘        │
│     │                   │                   │           │
│     └───────────────────┴───────────────────┘           │
│                         │                                │
│                         ▼                                │
│                   ┌──────────┐                          │
│                   │ Merger   │                          │
│                   │ (Top K)  │                          │
│                   └──────────┘                          │
└─────────────────────────────────────────────────────────┘

Sharding numbers:
- ~1000-10000 shards
- Each shard: ~1M documents
- Replication factor: 3
- Geographic distribution across data centers
```

### Data Flow Summary

```
Complete pipeline:

1. CRAWL: Spider downloads pages → ~1B pages/day
           ↓
2. PROCESS: Parse HTML, extract text → content + links
           ↓
3. INDEX: Build inverted index → term → [doc_ids]
           ↓
4. RANK PREP: Calculate PageRank → authority scores
           ↓
5. QUERY: User searches → parse, correct, expand
           ↓
6. RETRIEVE: Fetch posting lists → candidate docs
           ↓
7. SCORE: Apply ranking model → scored candidates
           ↓
8. RETURN: Top 10 with snippets → <200ms
```

### Key Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Index freshness vs. completeness | Fresher = more crawl resources |
| Ranking quality vs. latency | Better ranking = more computation |
| Cache size vs. hit rate | Larger cache = higher cost |
| Shard count vs. query latency | More shards = higher tail latency |
| Precision vs. recall | Tighter matching = miss relevant results |

---

## Otvet (RU)

### Требования

**Функциональные:**
- Индексация миллиардов веб-страниц
- Релевантные результаты для текстовых запросов
- Задержка запроса менее секунды
- Исправление опечаток и подсказки запросов
- Поддержка разных типов контента (текст, изображения, видео)

**Нефункциональные:**
- Высокая доступность (99.99%)
- Низкая задержка (<500мс p99)
- Масштабируемость до миллиардов запросов/день
- Свежий индекс (страницы обновляются в течение часов)

### Оценка масштаба

```
Масштаб веба:
- ~50 миллиардов проиндексированных страниц
- Средний размер страницы: 100KB (сжато: 10KB)
- Общий размер индекса: ~500 PB
- Запросы: 8.5 миллиардов/день = 100K QPS
- Пик: 200K QPS

На запрос:
- Цель по задержке: <200мс
- Страниц для ранжирования: миллионы -> топ 10
```

### Компонент 1: Инвертированный индекс

```
Структура:
┌────────────────────────────────────────────────────────────┐
│                 Инвертированный индекс                      │
│                                                             │
│  Термин     │  Список постингов                            │
│  ───────────┼──────────────────────────────────────────────│
│  "kotlin"   │  [doc1:5, doc2:12, doc3:1, doc47:3, ...]     │
│  "android"  │  [doc1:8, doc5:15, doc12:2, ...]             │
│  "coroutine"│  [doc1:3, doc2:7, doc99:1, ...]              │
│                                                             │
│  Запись: (doc_id, частота_термина, позиции[])              │
└────────────────────────────────────────────────────────────┘

Оптимизации:
1. Delta-кодирование для doc_id (экономия места)
2. Variable-byte кодирование для частот
3. Skip pointers для быстрого пересечения
4. Сжатие: ~2 бита на постинг
```

### Компонент 2: Алгоритм PageRank

```
Основная идея: Страница важна, если на неё ссылаются важные страницы

Формула:
PR(A) = (1-d) + d * Σ(PR(Ti)/C(Ti))

Где:
- d = коэффициент затухания (обычно 0.85)
- Ti = страницы, ссылающиеся на A
- C(Ti) = количество исходящих ссылок с Ti

Вычисление:
1. Инициализация всех страниц PR = 1/N
2. Итеративное обновление до сходимости
3. Обычно 50-100 итераций

Современные дополнения:
- TrustRank (борьба со спамом)
- Topic-sensitive PageRank
- Персонализированный PageRank
```

### Компонент 3: Обработка запросов

```
Поток запроса:
┌────────────────────────────────────────────────────────┐
│ 1. Парсинг запроса                                     │
│    "kotlin coroutines tutorial" →                      │
│    токены: ["kotlin", "coroutines", "tutorial"]        │
│                                                         │
│ 2. Исправление опечаток                                │
│    "kotlinn" → "kotlin" (edit distance, языковая модель)│
│                                                         │
│ 3. Расширение запроса                                  │
│    "kotlin" → "kotlin", "kotlinlang"                   │
│    Синонимы, варианты стемминга                        │
│                                                         │
│ 4. Понимание запроса                                   │
│    Намерение: информационное                           │
│    Сущность: "Kotlin" (язык программирования)          │
│                                                         │
│ 5. Поиск в индексе                                     │
│    Получить списки постингов, пересечь, оценить        │
│                                                         │
│ 6. Ранжирование                                        │
│    Применить модель ранжирования к кандидатам          │
└────────────────────────────────────────────────────────┘
```

### Компонент 4: Система ранжирования

```
Двухфазное ранжирование:

Фаза 1: Генерация кандидатов (быстро, грубо)
- Получить топ ~10,000 кандидатов
- Использовать BM25 или простой TF-IDF
- Пересечь списки постингов

Фаза 2: Переранжирование (медленно, точно)
- Применить ML-модель к топ кандидатам
- Учесть сотни признаков
- Вернуть топ 10-20 результатов

Сигналы ранжирования:
┌──────────────────────────────────────────────────────┐
│ Контентные сигналы:                                   │
│   - TF-IDF скор                                      │
│   - BM25 скор                                        │
│   - Совпадение в заголовке                           │
│   - Совпадение в URL                                 │
│   - Свежесть контента                                │
│                                                       │
│ Сигналы авторитетности:                              │
│   - PageRank                                         │
│   - Авторитет домена                                 │
│   - Качество/количество обратных ссылок              │
│                                                       │
│ Пользовательские сигналы:                            │
│   - CTR (click-through rate)                         │
│   - Время на странице (dwell time)                   │
│   - Bounce rate                                      │
│   - Pogo-sticking (быстрые возвраты)                 │
└──────────────────────────────────────────────────────┘
```

### Формула BM25

```
BM25 - стандарт де-факто для текстового ранжирования:

score(D,Q) = Σ IDF(qi) * (f(qi,D) * (k1 + 1)) /
             (f(qi,D) + k1 * (1 - b + b * |D|/avgdl))

Где:
- f(qi,D) = частота термина в документе
- |D| = длина документа
- avgdl = средняя длина документа
- k1 = 1.2-2.0 (насыщение частоты термина)
- b = 0.75 (нормализация длины)
```

### Стратегия кеширования

```
Многоуровневое кеширование:
┌────────────────────────────────────────────────────────┐
│ Уровень 1: Кеш результатов                             │
│   - Кешировать полные результаты поиска               │
│   - Ключ: хеш запроса + контекст пользователя         │
│   - Hit rate: ~30% (популярные запросы)               │
├────────────────────────────────────────────────────────┤
│ Уровень 2: Кеш списков постингов                      │
│   - Кешировать сегменты инвертированного индекса      │
│   - Горячие термины (the, is, and) всегда в памяти    │
│   - Hit rate: ~60%                                    │
├────────────────────────────────────────────────────────┤
│ Уровень 3: Кеш документов                             │
│   - Кешировать метаданные и сниппеты документов       │
│   - Избегать чтения с диска при ранжировании          │
└────────────────────────────────────────────────────────┘
```

### Шардирование индекса

```
Архитектура с партиционированием по документам:

┌─────────────────────────────────────────────────────────┐
│                   Query Router                           │
│                        │                                 │
│    ┌───────────────────┼───────────────────┐            │
│    ▼                   ▼                   ▼            │
│ ┌────────┐        ┌────────┐         ┌────────┐         │
│ │ Шард 1 │        │ Шард 2 │   ...   │ Шард N │         │
│ │ Docs   │        │ Docs   │         │ Docs   │         │
│ │ 1-1M   │        │ 1M-2M  │         │(N-1)M- │         │
│ └────────┘        └────────┘         └────────┘         │
│                        │                                 │
│                        ▼                                 │
│                  ┌──────────┐                           │
│                  │  Merger  │                           │
│                  │ (Top K)  │                           │
│                  └──────────┘                           │
└─────────────────────────────────────────────────────────┘

Числа шардирования:
- ~1000-10000 шардов
- Каждый шард: ~1M документов
- Фактор репликации: 3
- Географическое распределение по дата-центрам
```

### Полный pipeline

```
1. КРАУЛИНГ: Паук скачивает страницы → ~1B страниц/день
           ↓
2. ОБРАБОТКА: Парсинг HTML, извлечение текста → контент + ссылки
           ↓
3. ИНДЕКСАЦИЯ: Построение инвертированного индекса → термин → [doc_ids]
           ↓
4. ПОДГОТОВКА: Расчёт PageRank → скоры авторитетности
           ↓
5. ЗАПРОС: Пользователь ищет → парсинг, коррекция, расширение
           ↓
6. ИЗВЛЕЧЕНИЕ: Получение списков постингов → документы-кандидаты
           ↓
7. ОЦЕНКА: Применение модели ранжирования → оценённые кандидаты
           ↓
8. ВОЗВРАТ: Топ 10 со сниппетами → <200мс
```

### Ключевые компромиссы

| Решение | Компромисс |
|---------|------------|
| Свежесть vs полнота индекса | Свежее = больше ресурсов на краулинг |
| Качество ранжирования vs задержка | Лучшее ранжирование = больше вычислений |
| Размер кеша vs hit rate | Больше кеш = выше стоимость |
| Количество шардов vs задержка | Больше шардов = выше tail latency |
| Precision vs recall | Строже matching = пропуск релевантных |

---

## Follow-ups

- How would you handle real-time indexing for news articles?
- How would you implement personalized search results?
- How would you detect and penalize SEO spam?
- How would you handle multi-language search?
- How would you implement Knowledge Graph integration?
- What's the difference between lexical and semantic search?
