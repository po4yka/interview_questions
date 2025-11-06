---
id: lang-081
title: "Flow Flatmap Operator / Оператор flatMap для Flow"
aliases: [Flow Flatmap Operator, Оператор flatMap для Flow]
topic: programming-languages
subtopics: [coroutines, flow, operators]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-flow, q-flow-map-operator--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [coroutines, difficulty/easy, flow, kotlin, operators, programming-languages, reactive]
---
# Чем Воспользоваться Если Нужно Преобразовать Один Поток Данных В Другой Поток Данных

# Вопрос (RU)
> Чем воспользоваться если нужно преобразовать один поток данных в другой поток данных?

---

# Question (EN)
> What to use if you need to transform one data stream into another data stream?

## Ответ (RU)

Используйте оператор flatMap. Преобразует элементы из одного потока в другой поток Пример из потока URL в поток содержимого страниц

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

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-what-is-flow--programming-languages--medium]]
- [[q-singleton-pattern--design-patterns--easy]]
- [[q-priorityqueue-vs-deque--programming-languages--easy]]
