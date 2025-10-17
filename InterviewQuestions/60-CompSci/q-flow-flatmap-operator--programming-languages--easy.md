---
id: "20251015082237209"
title: "Flow Flatmap Operator / Оператор flatMap для Flow"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - coroutines
  - flatmap
  - flow
  - kotlin
  - operators
  - programming-languages
  - reactive
---
# Чем воспользоваться если нужно преобразовать один поток данных в другой поток данных

# Question (EN)
> What to use if you need to transform one data stream into another data stream?

# Вопрос (RU)
> Чем воспользоваться если нужно преобразовать один поток данных в другой поток данных?

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

---

## Ответ (RU)

Используйте оператор flatMap. Преобразует элементы из одного потока в другой поток Пример из потока URL в поток содержимого страниц

