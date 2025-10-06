---
tags:
  - coroutines
  - flatmap
  - flow
  - kotlin
  - operators
  - programming-languages
  - reactive
difficulty: easy
---

# Чем воспользоваться если нужно преобразовать один поток данных в другой поток данных

**English**: What to use if you need to transform one data stream into another data stream?

## Answer

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

## Ответ

Используйте оператор flatMap. Преобразует элементы из одного потока в другой поток Пример из потока URL в поток содержимого страниц

