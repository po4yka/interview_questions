---
id: lang-005
title: Kotlin Delegation / Делегирование в Kotlin
aliases:
- Kotlin Delegation
- Делегирование в Kotlin
topic: kotlin
subtopics:
- c-kotlin
- c-kotlin-coroutines-basics
- c-kotlin-features
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-kotlin-features
- q-kotlin-delegation-detailed--kotlin--medium
created: 2025-10-13
updated: 2025-11-09
tags:
- difficulty/easy
---
# Вопрос (RU)
> Что известно о делегировании?

---

# Question (EN)
> What do you know about delegation?

## Ответ (RU)

Делегирование в Kotlin — это передача реализации части функциональности другому объекту с помощью ключевого слова `by`.

Основные формы:
- Делегирование реализации интерфейса (class delegation):
  - `class MyClass(private val delegate: MyInterface) : MyInterface by delegate`
  - Методы интерфейса `MyInterface` в `MyClass` автоматически перенаправляются к `delegate`.
- Делегированные свойства (property delegation):
  - `val/var name: Type by delegate`
  - Стандартные делегаты: `lazy` (ленивая инициализация), `Delegates.observable`, `Delegates.vetoable`.

Это позволяет:
- Избежать дублирования кода и ручного проксирования методов.
- Гибко комбинировать поведение через композицию вместо наследования.

См. также: [[c-kotlin]], [[c-kotlin-features]]

---

## Answer (EN)

Delegation in Kotlin is passing implementation of part of the functionality to another object using the `by` keyword.

Main forms:
- Class delegation (interface implementation delegation):
  - `class MyClass(private val delegate: MyInterface) : MyInterface by delegate`
  - Methods of `MyInterface` in `MyClass` are automatically forwarded to `delegate`.
- Property delegation:
  - `val/var name: Type by delegate`
  - Standard delegates: `lazy` (lazy initialization), `Delegates.observable`, `Delegates.vetoable`.

This lets you:
- Avoid boilerplate and manual forwarding.
- Compose behavior via composition instead of inheritance.

See also: [[c-kotlin]], [[c-kotlin-features]]

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия делегирования в Kotlin и Java?
- Когда вы бы использовали делегирование на практике?
- Какие распространенные подводные камни следует учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

### Реализации В Android
- [[q-recyclerview-viewtypes-delegation--android--medium]] - Паттерны проектирования

### Возможности Языка Kotlin
- [[q-delegation-by-keyword--kotlin--medium]] - Паттерны проектирования
- [[q-kotlin-singleton-creation--kotlin--easy]] - Паттерны проектирования
- [[q-deferred-async-patterns--kotlin--medium]] - Паттерны проектирования
- [[q-object-singleton-companion--kotlin--medium]] - Паттерны проектирования
- [[q-kotlin-delegation-detailed--kotlin--medium]] - Паттерны проектирования

## Related Questions

### Android Implementation
- [[q-recyclerview-viewtypes-delegation--android--medium]] - Design Patterns

### Kotlin Language Features
- [[q-delegation-by-keyword--kotlin--medium]] - Design Patterns
- [[q-kotlin-singleton-creation--kotlin--easy]] - Design Patterns
- [[q-deferred-async-patterns--kotlin--medium]] - Design Patterns
- [[q-object-singleton-companion--kotlin--medium]] - Design Patterns
- [[q-kotlin-delegation-detailed--kotlin--medium]] - Design Patterns