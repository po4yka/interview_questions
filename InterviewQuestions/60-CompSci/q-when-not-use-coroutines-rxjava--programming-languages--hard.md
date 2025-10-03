---
id: 20251003140808
title: When NOT to use coroutines and RxJava / Когда не стоит использовать корутины и RxJava
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, coroutines, best-practices]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/409
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-coroutines
  - c-best-practices

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, coroutines, rxjava, best-practices, anti-patterns, difficulty/hard, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> When is it not recommended to use coroutines and RxJava

# Вопрос (RU)
> В каких случаях не рекомендуется использовать корутины и RxJava

---

## Answer (EN)

Coroutines and RxJava should not be used when asynchrony doesn't provide advantages and code becomes more complex.

**When NOT to use coroutines:**
- **Simple tasks**: If task is simple and doesn't require complex async management, coroutines may add unnecessary complexity (e.g., simple file reading)
- **Inexperienced team**: If team doesn't have enough coroutine experience, it may lead to errors and debugging difficulties
- **Low-level tasks**: For tasks requiring low-level thread management or high-performance computing, coroutines may not be suitable

**When NOT to use RxJava:**
- **Excessive complexity**: RxJava adds abstraction layer that may be excessive for simple tasks (handling 1-2 simple async events)
- **Performance issues**: RxJava may add performance overhead due to creating many objects and event processing
- **Debugging complexity**: RxJava can be hard to debug and maintain due to complexity of data flows and operators
- **Small dev team**: If team is small and doesn't have functional programming experience, RxJava may lead to code maintenance issues

**General rule**: Don't use async frameworks when simple synchronous code would suffice.

## Ответ (RU)

Корутины и RxJava не стоит использовать, если асинхронность не даёт преимуществ, а код становится сложнее например для простых и быстрых задач или в проектах с ограниченными ресурсами. [Full Russian text omitted for brevity]

---

## Follow-ups
- What are simpler alternatives for basic async operations?
- How to evaluate when to introduce async frameworks?
- What are the team training requirements?

## References
- [[c-kotlin-coroutines]]
- [[c-best-practices]]
- [[moc-kotlin]]

## Related Questions
- [[q-coroutines-advantages-over-rxjava--programming-languages--medium]]
- [[q-kotlin-coroutines-overview--programming-languages--medium]]
