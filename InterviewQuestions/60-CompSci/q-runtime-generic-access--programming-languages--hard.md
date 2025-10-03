---
id: 20251003140315
title: Can you access generic type at runtime / Можно ли получить в runtime доступ к типу дженерика
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, generics, reified]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/950
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-features
  - c-kotlin-advanced

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, generics, type-erasure, difficulty/hard, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> Can you access generic type at runtime

# Вопрос (RU)
> Можно ли получить в runtime доступ к типу дженерика

---

## Answer (EN)

By default, no, because generics are erased (Type Erasure) during compilation. If using inline fun, you can make the generic 'real' (reified). Also, to get type in a class, you can use KClass<T>, and for complex generics (List<T>, Map<K, V>) use typeOf<T>() only with reified.

## Ответ (RU)

По умолчанию нельзя, потому что дженерики стираются (Type Erasure) во время компиляции. Если используем inline fun, можно сделать дженерик "реальным" (reified). Также для получения типа в классе можно использовать KClass<T>, а для сложных дженериков (List<T>, Map<K, V>) использовать typeOf<T>() только с reified

---

## Follow-ups
- How does this compare to other approaches?
- What are the performance implications?
- When should you use this feature?

## References
- [[c-kotlin-features]]
- [[c-kotlin-advanced]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-inline-functions--programming-languages--medium]]
