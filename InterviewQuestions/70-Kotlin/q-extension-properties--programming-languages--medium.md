---
id: 20251012-122732
title: "Extension Properties / Расширяющие свойства"
aliases: [Extension Properties, Расширяющие свойства]
topic: programming-languages
subtopics: [kotlin, extensions, properties]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [c-extensions, c-properties, q-extensions-concept--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [programming-languages, kotlin, extensions, properties, difficulty/medium]
---

# Свойства Какого Вида Можно Добавить Как Расширение

# Question (EN)
> What kind of properties can be added as extensions?

# Вопрос (RU)
> Свойства какого вида можно добавить как расширение?

---

## Answer (EN)

In Kotlin, you can add extension properties, but only with a custom get (getter). You can add val with get(). Extension properties can only be computed (val) because you cannot create a field inside an extension. var works only with get() and set(), but you still cannot use a field.

---

## Ответ (RU)

В Kotlin можно добавлять свойства-расширения (extension properties), но только с кастомным get (геттером). Можно добавлять val с get(). Расширяемые свойства могут быть только вычисляемыми (val), потому что нельзя создать field внутри расширения. var работает только с get() и set(), но всё равно нельзя использовать field.

## Related Questions

- [[q-what-is-coroutinescope--programming-languages--medium]]
- [[q-how-suspend-function-detects-suspension--programming-languages--hard]]
- [[q-error-handling-in-coroutines--programming-languages--medium]]
