---
id: lang-005
title: "Kotlin Delegation / Делегирование в Kotlin"
aliases: ["Kotlin Delegation, Делегирование в Kotlin"]
topic: programming-languages
subtopics: [class-features, functions, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-circuit-breaker-coroutines--kotlin--hard, q-coroutine-timeout-withtimeout--kotlin--medium, q-testing-coroutines-runtest--kotlin--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [difficulty/easy]
date created: Saturday, November 1st 2025, 12:42:09 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Что Известно О Делегировании?

# Question (EN)
> What do you know about delegation?

# Вопрос (RU)
> Что известно о делегировании?

---

## Answer (EN)

Delegation allows transferring implementation of certain functions or properties to other objects. The by keyword is used to transfer logic, e.g., class MyClass : Interface by Delegate. Kotlin provides built-in delegates like lazy, observable, and vetoable for convenient state management of properties.

---

## Ответ (RU)

Делегирование позволяет передавать реализацию определённых функций или свойств другим объектам. Используется ключевое слово by для передачи логики например class MyClass : Interface by Delegate. Kotlin предоставляет встроенные делегаты такие как lazy observable и vetoable для удобного управления состоянием свойств.


---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

### Android Implementation
- [[q-recyclerview-viewtypes-delegation--android--medium]] - Design Patterns

### Kotlin Language Features
- [[q-delegation-by-keyword--kotlin--medium]] - Design Patterns
- [[q-kotlin-singleton-creation--programming-languages--easy]] - Design Patterns
-  - Design Patterns
- [[q-deferred-async-patterns--kotlin--medium]] - Design Patterns
- [[q-object-singleton-companion--kotlin--medium]] - Design Patterns
- [[q-kotlin-delegation-detailed--kotlin--medium]] - Design Patterns
