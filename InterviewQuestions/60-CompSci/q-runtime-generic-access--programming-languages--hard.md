---
id: "20251015082237091"
title: "Runtime Generic Access / Доступ к дженерикам во время выполнения"
topic: computer-science
difficulty: hard
status: draft
created: 2025-10-15
tags: - generics
  - kotlin
  - programming-languages
  - reified
  - type-erasure
---
# Можно ли получить в runtime доступ к типу дженерика?

# Question (EN)
> Can you access generic type at runtime?

# Вопрос (RU)
> Можно ли получить в runtime доступ к типу дженерика?

---

## Answer (EN)

By default, no, because generics are erased (Type Erasure) during compilation. If using inline fun, you can make the generic 'real' (reified). Also, to get type in a class, you can use KClass<T>, and for complex generics (List<T>, Map<K, V>) use typeOf<T>() only with reified.

---

## Ответ (RU)

По умолчанию нельзя, потому что дженерики стираются (Type Erasure) во время компиляции. Если используем inline fun, можно сделать дженерик "реальным" (reified). Также для получения типа в классе можно использовать KClass<T>, а для сложных дженериков (List<T>, Map<K, V>) использовать typeOf<T>() только с reified

