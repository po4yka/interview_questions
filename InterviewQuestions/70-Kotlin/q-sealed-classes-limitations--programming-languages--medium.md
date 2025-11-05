---
id: lang-025
title: "Sealed Classes Limitations / Ограничения Sealed Классов"
aliases: [Sealed Classes Limitations, Ограничения Sealed Классов]
topic: programming-languages
subtopics: [class-hierarchy, oop, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-what-is-flow--programming-languages--medium, q-what-is-job-object--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [class-hierarchy, difficulty/medium, kotlin, programming-languages, sealed-classes]
date created: Friday, October 3rd 2025, 4:39:28 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Какие Есть Ограничения У Sealed Классов?

# Question (EN)
> What are the limitations of sealed classes?

# Вопрос (RU)
> Какие есть ограничения у sealed классов?

---

## Answer (EN)

Sealed class limitations: all subtypes must be defined in the same file, sealed class cannot be an interface or abstract class directly, sealed classes and their subtypes cannot be private, sealed classes don't support inheritance from other classes except Any and can only be used for classes and objects but not interfaces. Sealed classes also provide exhaustive when expressions, full control over class hierarchy, and pattern matching support.

---

## Ответ (RU)

Ограничения sealed классов: все подтипы должны быть определены в том же файле, sealed класс не может быть интерфейсом или абстрактным классом напрямую, sealed классы и их подтипы не могут быть private, sealed классы не поддерживают наследование от других классов кроме Any и могут использоваться только для классов и объектов но не интерфейсов. Также sealed классы обеспечивают исчерпывающие выражения when, полный контроль над иерархией классов и поддержку сопоставления с образцом.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-what-is-flow--programming-languages--medium]]
- [[q-what-is-job-object--programming-languages--medium]]
-
