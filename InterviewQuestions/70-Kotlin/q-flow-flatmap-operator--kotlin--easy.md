---
---
---\
id: lang-081
title: "Flow Flatmap Operator / Оператор flatMap для Flow"
aliases: [Flow Flatmap Operator, Оператор flatMap для Flow]
topic: kotlin
subtopics: [coroutines, flow, operators]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-flow]
created: 2025-10-15
updated: 2025-11-10
tags: [coroutines, difficulty/easy, flow, kotlin, operators, programming-languages, reactive]
---\
# Вопрос (RU)
> Чем в Kotlin `Flow` воспользоваться, если нужно преобразовать один поток данных в другой поток данных?

---

# Question (EN)
> In Kotlin `Flow`, what should you use if you need to transform one data stream into another data stream?

## Ответ (RU)

Используйте оператор `flatMap` (и его варианты). Он преобразует каждый элемент исходного `Flow` в новый `Flow` и "сплющивает" их в один результирующий поток.

Пример: из потока URL-адресов в поток содержимого страниц.

```kotlin
flow {
    emit("https://example.com")
    emit("https://google.com")
}.flatMapConcat { url ->
    fetchPageContent(url) // Возвращает Flow<String>
}.collect { content ->
    println(content)
}
```

**Варианты:**
- `flatMapConcat` — последовательная обработка внутренних `Flow` в порядке прихода значений.
- `flatMapMerge` — конкурентная обработка нескольких внутренних `Flow` с межлевелингом значений.
- `flatMapLatest` — при поступлении нового значения отменяет предыдущий внутренний `Flow` и переключается на новый.

## Answer (EN)

Use the `flatMap` operator (and its variants). It transforms each element of the original `Flow` into a new `Flow` and flattens them into a single resulting stream.

Example: from a stream of URLs to a stream of page content.

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
- `flatMapConcat` - sequentially collects inner Flows in order.
- `flatMapMerge` - collects from multiple inner Flows concurrently, interleaving values.
- `flatMapLatest` - cancels the previous inner `Flow` when a new value arrives and switches to the latest.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java-подходов к работе с потоками данных?
- Когда на практике стоит использовать `flatMap` для `Flow`?
- Каких распространенных ошибок при использовании `flatMap` следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- "Kotlin Documentation" — "https://kotlinlang.org/docs/home.html"

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-what-is-flow--kotlin--medium]]
- [[q-singleton-pattern--cs--easy]]
- [[q-priorityqueue-vs-deque--kotlin--easy]]

## Related Questions

- [[q-what-is-flow--kotlin--medium]]
- [[q-singleton-pattern--cs--easy]]
- [[q-priorityqueue-vs-deque--kotlin--easy]]
