---
id: "20251110-195927"
title: "Bm25 Ranking / Bm25 Ranking"
aliases: ["Bm25 Ranking"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-backend", "c-algorithms"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---

# Summary (EN)

BM25 ranking (Best Match 25) is a probabilistic information retrieval scoring function used to rank documents by their relevance to a search query. It extends TF-IDF with saturation and length-normalization terms, making it robust for real-world text search over varying document sizes. BM25 is widely used in search engines, full-text indexes, and code/documentation search systems because it is simple, efficient, and empirically effective.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

BM25 (Best Match 25) — это вероятностная функция ранжирования для информационного поиска, используемая для упорядочивания документов по релевантности поисковому запросу. Она развивает идеи TF-IDF, добавляя насыщение по частоте термов и нормализацию по длине документа, что делает её устойчивой для текстового поиска по документам разной длины. BM25 широко используется в поисковых системах, полнотекстовых индексах и системах поиска по коду и документации благодаря простоте, эффективности и высокой практической точности.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Term frequency saturation: Increases score with term frequency but with diminishing returns, preventing very frequent terms from dominating.
- Inverse document frequency: Rewards rare, more informative terms and down-weights common terms across the collection.
- Length normalization: Adjusts scores to avoid bias toward longer documents that naturally contain more term matches.
- Tunable parameters (k1, b): Control term frequency scaling and length normalization, allowing adaptation to different datasets and search behaviors.
- Practical relevance: Forms the basis of ranking in popular search libraries (e.g., Lucene-based engines) and is often a strong baseline compared to more complex models.

## Ключевые Моменты (RU)

- Насыщение частоты термов: Учитывает рост частоты вхождений терма с убывающей отдачей, не давая очень частым словам полностью доминировать в оценке.
- Обратная документная частота: Повышает вес редких информативных терминов и снижает влияние часто встречающихся слов в коллекции.
- Нормализация по длине документа: Корректирует оценки, чтобы длинные документы не получали необоснованно высокий рейтинг лишь из-за большего числа совпадений.
- Настраиваемые параметры (k1, b): Управляют влиянием частоты термов и нормализации длины, позволяя адаптировать модель под разные корпуса и сценарии поиска.
- Практическая значимость: Лежит в основе ранжирования во многих поисковых движках (например, на базе Lucene) и служит сильной базовой моделью по сравнению с более сложными подходами.

## References

- BM25 overview in the Apache Lucene documentation
- "Okapi at TREC" by S. E. Robertson et al. (original BM25 work)
