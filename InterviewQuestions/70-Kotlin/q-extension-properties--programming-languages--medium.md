---
id: lang-077
title: "Extension Properties / Расширяющие свойства"
aliases: [Extension Properties, Расширяющие свойства]
topic: programming-languages
subtopics: [extensions, kotlin, properties]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-extensions, c-properties, q-extensions-concept--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium, extensions, kotlin, programming-languages, properties]
date created: Friday, October 31st 2025, 6:29:51 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Свойства Какого Вида Можно Добавить Как Расширение

# Вопрос (RU)
> Свойства какого вида можно добавить как расширение?

---

# Question (EN)
> What kind of properties can be added as extensions?

## Ответ (RU)

В Kotlin можно добавлять свойства-расширения (extension properties), но только с кастомным get (геттером). Можно добавлять val с get(). Расширяемые свойства могут быть только вычисляемыми (val), потому что нельзя создать field внутри расширения. var работает только с get() и set(), но всё равно нельзя использовать field.

## Answer (EN)

In Kotlin, you can add extension properties, but only with a custom get (getter). You can add val with get(). Extension properties can only be computed (val) because you cannot create a field inside an extension. var works only with get() and set(), but you still cannot use a field.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-what-is-coroutinescope--programming-languages--medium]]
- [[q-how-suspend-function-detects-suspension--programming-languages--hard]]
- [[q-error-handling-in-coroutines--programming-languages--medium]]
