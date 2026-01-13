---
anki_cards:
- slug: q-list-vs-sequence--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-list-vs-sequence--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: lang-001
title: "List Vs Sequence / List против Sequence"
aliases: [List Vs Sequence, List против Sequence]
topic: kotlin
subtopics: [collections, lazy-evaluation, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-collections, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-list-vs-sequence--kotlin--medium]
created: 2024-10-13
updated: 2025-11-11
tags: [collections, difficulty/medium, kotlin, list, programming-languages, sequences]
---
# Вопрос (RU)
> В чем разница между работой с `List` и работой с `Sequence`?

# Question (EN)
> What is the difference between working with `List` and working with `Sequence`?

---

## Ответ (RU)

- `List` в Kotlin — это материализованная коллекция в памяти. Операции (`map`, `filter` и т.п.), как правило, выполняются немедленно и возвращают новые коллекции, создавая промежуточные списки на каждом шаге цепочки.
- `Sequence` — это ленивое представление последовательности элементов (не коллекция). Промежуточные операции не создают новых коллекций; элементы обрабатываются по одному при выполнении терминальной операции (например, `toList()`, `first()`, `count()`).
- Работа с `List` обычно эффективнее для небольших коллекций и коротких цепочек операций из-за меньших накладных расходов.
- `Sequence` полезен для:
  - больших коллекций или потенциально бесконечных источников;
  - длинных цепочек преобразований, где важно избежать создания множества промежуточных коллекций;
  - случаев, когда можно остановить обработку раньше при выполнении условия (short-circuiting).
- Важно: `Sequence` обычно однопроходный, и повторный обход требует повторного создания `Sequence` или явной материализации (например, `toList()`), в отличие от уже материализованного `List`.

---

## Answer (EN)

- In Kotlin, a `List` is a materialized collection in memory. Operations like `map`, `filter`, etc. are generally eager: they run immediately and return new collections, creating intermediate lists at each step of a chain.
- A `Sequence` is a lazy view of elements (not a collection). Intermediate operations do not create new collections; elements are processed one by one when a terminal operation is invoked (e.g., `toList()`, `first()`, `count()`).
- Working with a `List` is often more efficient for small collections and short pipelines because it has lower per-element overhead.
- `Sequence`s are useful for:
  - large collections or potentially infinite sources;
  - long transformation chains where avoiding multiple intermediate collections matters;
  - cases where you can stop early once a condition is met (short-circuiting).
- Note: A `Sequence` is typically single-pass; to traverse again you usually recreate the sequence or materialize it (e.g., `toList()`), whereas a `List` is already materialized and can be iterated multiple times cheaply.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали это на практике?
- Какие распространенные подводные камни следует учитывать?

## Follow-ups (EN)

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-collections]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References (EN)

- [[c-kotlin]]
- [[c-collections]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

### Реализация В Android
- [[q-what-problems-can-there-be-with-list-items--android--easy]] — Структуры данных

### Особенности Языка Kotlin
- — Структуры данных
- [[q-kotlin-immutable-collections--kotlin--easy]] — Структуры данных

## Related Questions (EN)

### Android Implementation
- [[q-what-problems-can-there-be-with-list-items--android--easy]] - Data Structures

### Kotlin Language Features
- - Data Structures
- [[q-kotlin-immutable-collections--kotlin--easy]] - Data Structures
