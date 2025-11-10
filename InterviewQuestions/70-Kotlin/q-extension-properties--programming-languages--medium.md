---
id: lang-077
title: "Extension Properties / Расширяющие свойства"
aliases: [Extension Properties, Extension Properties RU]
topic: kotlin
subtopics: [extensions, kotlin, properties]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-extensions-concept--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, extensions, kotlin, programming-languages, properties]
---
# Вопрос (RU)
> Свойства какого вида можно добавить как расширение?

## Ответ (RU)

В Kotlin можно объявлять свойства-расширения (`extension properties`) как `val`, так и `var`, но они не могут иметь собственного backing field. Такие свойства всегда реализуются через функции доступа: `val` — только с кастомным `get()`, `var` — с кастомными `get()` и `set()` (если это требуется). То есть свойства-расширения всегда вычисляемые и не могут хранить состояние внутри самого расширения.

---

# Question (EN)
> What kind of properties can be added as extensions?

## Answer (EN)

In Kotlin, you can declare extension properties as both `val` and `var`, but they cannot have their own backing field. These properties are always implemented via accessors: `val` with a custom `get()` only, and `var` with custom `get()` and `set()` (if needed). In other words, extension properties are always computed and cannot store state inside the extension itself.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия от Java?
- Когда это стоит использовать на практике?
- Какие распространенные подводные камни стоит учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные вопросы (RU)

- [[q-what-is-coroutinescope--programming-languages--medium]]
- [[q-how-suspend-function-detects-suspension--programming-languages--hard]]
- [[q-error-handling-in-coroutines--programming-languages--medium]]

## Related Questions

- [[q-what-is-coroutinescope--programming-languages--medium]]
- [[q-how-suspend-function-detects-suspension--programming-languages--hard]]
- [[q-error-handling-in-coroutines--programming-languages--medium]]
