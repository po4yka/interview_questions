---
id: 20251012-12271111131
title: "Kotlin Flatmap Ranges / flatMap и диапазоны в Kotlin"
topic: computer-science
difficulty: easy
status: draft
moc: moc-kotlin
related: [q-inline-function-limitations--kotlin--medium, q-interface-properties--programming-languages--medium, q-retry-exponential-backoff-flow--kotlin--medium]
created: 2025-10-15
tags:
  - collections
  - flatMap
  - kotlin
  - programming-languages
  - ranges
---
# Какой результат выполнения выражения val result = (1..3).flatMap { listOf(it, it * 2) }?

# Question (EN)
> What is the result of executing val result = (1..3).flatMap { listOf(it, it * 2) }?

# Вопрос (RU)
> Какой результат выполнения выражения val result = (1..3).flatMap { listOf(it, it * 2) }?

---

## Answer (EN)

The result of executing the expression will be the list [1, 2, 2, 4, 3, 6].

---

## Ответ (RU)

Результат выполнения выражения будет список [1, 2, 2, 4, 3, 6].

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-interface-properties--programming-languages--medium]]
- [[q-retry-exponential-backoff-flow--kotlin--medium]]
