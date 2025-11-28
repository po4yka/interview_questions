---
id: "20251111-223452"
title: "Caching Strategies / Caching Strategies"
aliases: ["Caching Strategies"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-performance-optimization, c-memory-management, c-databases, c-networking, c-offline-first-architecture]
created: "2025-11-11"
updated: "2025-11-11"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Tuesday, November 11th 2025, 10:34:52 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

Caching strategies define how, where, and for how long data is stored closer to the consumer to reduce latency, offload backends, and improve throughput. They are critical in high-performance systems, APIs, and web/mobile applications to avoid repeated expensive computations or remote calls. Choosing the right strategy balances freshness (consistency) against performance and resource usage.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Стратегии кэширования определяют, как, где и на какой срок данные сохраняются ближе к потребителю для снижения задержек, уменьшения нагрузки на backend и повышения пропускной способности. Они особенно важны в высоконагруженных системах, API, веб- и мобильных приложениях для избегания повторных дорогих вычислений или удалённых запросов. Выбор подходящей стратегии — это баланс между актуальностью данных, производительностью и потреблением ресурсов.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Placement: Caching can occur at multiple layers (client, CDN, application, database, in-memory) and the strategy defines which layer owns which data.
- Invalidation and TTL: Time-to-live (TTL), cache expiration, and explicit invalidation policies determine how stale data is tolerated and refreshed.
- Read vs write patterns: Strategies differ for read-heavy vs write-heavy workloads (e.g., cache-aside for flexible reads, write-through/write-back for controlled writes).
- Cache-aside (lazy loading): Application reads from cache first and loads from the source on miss; simple and popular, but requires manual invalidation.
- Write-through vs write-back: Write-through updates cache and source synchronously (safer, slower), while write-back writes to cache first and flushes to source later (faster, riskier).

## Ключевые Моменты (RU)

- Уровни размещения: Кэш может находиться на разных уровнях (клиент, CDN, приложение, база данных, in-memory), а стратегия определяет, какие данные где хранятся.
- Инвалидация и TTL: Время жизни (TTL), политики истечения и явной инвалидации задают допустимую «устарелость» данных и способ их обновления.
- Паттерны чтения и записи: Разные стратегии подходят для систем с преобладанием чтения или записи (например, cache-aside для гибких чтений, write-through/write-back для управления записями).
- Cache-aside (ленивая загрузка): Приложение сначала читает из кэша и при промахе обращается к источнику; простой и распространённый подход, но требует явной инвалидации.
- Write-through vs write-back: Write-through синхронно обновляет кэш и источник (надёжнее, но медленнее), write-back сначала пишет в кэш и позже сбрасывает в источник (быстрее, но риск потери данных).

## References

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- https://aws.amazon.com/caching/
- https://cloud.google.com/cdn/docs/caching
