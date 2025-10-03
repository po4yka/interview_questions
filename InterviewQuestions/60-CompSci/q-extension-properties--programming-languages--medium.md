---
id: 20251003140313
title: What kind of properties can be added as extensions / Свойства какого вида можно добавить как расширение
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, extensions, properties]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/890
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
tags: [kotlin, extension-functions, properties, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What kind of properties can be added as extensions

# Вопрос (RU)
> Свойства какого вида можно добавить как расширение

---

## Answer (EN)

In Kotlin, you can add extension properties, but only with a custom get (getter). You can add val with get(). Extension properties can only be computed (val) because you cannot create a field inside an extension. var works only with get() and set(), but you still cannot use a field.

## Ответ (RU)

В Kotlin можно добавлять свойства-расширения (extension properties), но только с кастомным get (геттером). Можно добавлять val с get(). Расширяемые свойства могут быть только вычисляемыми (val), потому что нельзя создать field внутри расширения. var работает только с get() и set(), но всё равно нельзя использовать field.

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
