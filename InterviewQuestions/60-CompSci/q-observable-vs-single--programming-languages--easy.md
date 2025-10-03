---
id: 20251003140812
title: Observable vs Single (RxJava) / Различия между Observable и Single
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, rxjava]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/781
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-rxjava
  - c-reactive-programming

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [rxjava, observable, single, reactive, kotlin, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between Observable and Single

# Вопрос (RU)
> В чем заключается отличие Observable от Single

---

## Answer (EN)

**Observable** generates a sequence of data (0, 1, or more elements) and is used for data streams.

**Single** generates only one data element or error and is used for operations that return a single result, for example HTTP request.

**Key differences:**

| Aspect | Observable | Single |
|--------|-----------|---------|
| Items emitted | 0..N items | Exactly 1 item |
| Use case | Streams, multiple events | Single result operations |
| Events | onNext, onComplete, onError | onSuccess, onError |
| Example | WebSocket stream | HTTP GET request |

## Ответ (RU)

Observable генерирует последовательность данных (0, 1 или больше элементов) и используется для стримов данных. Single генерирует только один элемент данных или ошибку и используется для операций, которые возвращают один результат например HTTP-запрос.

---

## Follow-ups
- What are Maybe and Completable in RxJava?
- How to convert Observable to Single?
- When should you use Flowable instead of Observable?

## References
- [[c-rxjava]]
- [[c-reactive-programming]]
- [[moc-kotlin]]

## Related Questions
- [[q-coroutines-advantages-over-rxjava--programming-languages--medium]]
