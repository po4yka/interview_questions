---
id: 20251003140811
title: Flow flatMap operator / Оператор flatMap для потоков
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, coroutines, flow]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/777
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-flow
  - c-functional-programming

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, flow, flatmap, operators, reactive, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What to use if you need to transform one data stream into another data stream

# Вопрос (RU)
> Чем воспользоваться если нужно преобразовать один поток данных в другой поток данных

---

## Answer (EN)

Use the **flatMap** operator. It transforms elements from one stream into another stream.

**Example**: from a stream of URLs to a stream of page content

```kotlin
flow {
    emit("https://example.com")
    emit("https://google.com")
}.flatMapConcat { url ->
    fetchPageContent(url) // Returns Flow<String>
}.collect { content ->
    println(content)
}
```

**Variants:**
- `flatMapConcat` - sequential processing
- `flatMapMerge` - concurrent processing
- `flatMapLatest` - cancel previous when new arrives

## Ответ (RU)

Используйте оператор flatMap. Преобразует элементы из одного потока в другой поток Пример из потока URL в поток содержимого страниц

---

## Follow-ups
- What's the difference between map and flatMap?
- When to use flatMapConcat vs flatMapMerge?
- How does flatMapLatest work?

## References
- [[c-kotlin-flow]]
- [[c-functional-programming]]
- [[moc-kotlin]]

## Related Questions
- [[q-stateflow-purpose--programming-languages--medium]]
