---
tags:
  - generics
  - kotlin
  - programming-languages
  - reified
  - type-erasure
difficulty: hard
status: draft
---

# Можно ли получить в runtime доступ к типу дженерика?

**English**: Can you access generic type at runtime

## Answer

By default, no, because generics are erased (Type Erasure) during compilation. If using inline fun, you can make the generic 'real' (reified). Also, to get type in a class, you can use KClass<T>, and for complex generics (List<T>, Map<K, V>) use typeOf<T>() only with reified.

## Ответ

По умолчанию нельзя, потому что дженерики стираются (Type Erasure) во время компиляции. Если используем inline fun, можно сделать дженерик "реальным" (reified). Также для получения типа в классе можно использовать KClass<T>, а для сложных дженериков (List<T>, Map<K, V>) использовать typeOf<T>() только с reified

