---
id: lang-024
title: "Runtime Generic Access / Доступ к дженерикам во время выполнения"
aliases: [Runtime Generic Access, Доступ к дженерикам во время выполнения]
topic: programming-languages
subtopics: [generics, reification, type-system]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-what-is-garbage-in-gc--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/hard, generics, kotlin, programming-languages, reified, type-erasure]
---
# Можно Ли Получить В Runtime Доступ К Типу Дженерика?

# Вопрос (RU)
> Можно ли получить в runtime доступ к типу дженерика?

---

# Question (EN)
> Can you access generic type at runtime?

## Ответ (RU)

По умолчанию нельзя, потому что дженерики стираются (Type Erasure) во время компиляции. Если используем inline fun, можно сделать дженерик "реальным" (reified). Также для получения типа в классе можно использовать KClass<T>, а для сложных дженериков (List<T>, Map<K, V>) использовать typeOf<T>() только с reified

## Answer (EN)

By default, no, because generics are erased (Type Erasure) during compilation. If using inline fun, you can make the generic 'real' (reified). Also, to get type in a class, you can use KClass<T>, and for complex generics (List<T>, Map<K, V>) use typeOf<T>() only with reified.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-what-is-garbage-in-gc--programming-languages--easy]]
-
-
