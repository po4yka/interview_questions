---
id: 20251003140305
title: What is crossinline used for / Зачем нужен crossinline
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, inline, crossinline]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/93
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
tags: [kotlin, inline-functions, crossinline, difficulty/hard, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is crossinline used for

# Вопрос (RU)
> Зачем нужен crossinline

---

## Answer (EN)

The crossinline keyword is used in the context of inline functions and is important for correctly managing lambda expressions passed to these functions as parameters. Inline functions avoid the overhead of function calls and lambda object creation, improving performance in critical scenarios. However, using inline functions has certain limitations and possibilities, including non-inlined lambda calls. crossinline is needed to ensure safety and correctness when passing lambda expressions that shouldn't contain non-local returns (e.g., returns from the outer function) to inline functions. This keyword guarantees that the lambda expression won't use non-local returns, allowing safe lambda inlining even in contexts where non-local returns could lead to unexpected behavior or errors.

## Ответ (RU)

Ключевое слово crossinline используется в контексте встроенных функций (inline functions) и имеет важное значение для корректного управления лямбда-выражениями, передаваемыми в эти функции как параметры. Встроенные функции позволяют избежать затрат на вызов функций и создание объектов лямбда-выражений при каждом вызове, что может улучшить производительность кода, особенно в критичных сценариях. Однако использование inline функций влечёт за собой определённые ограничения и возможности, среди которых и возможность "невстроенного" вызова лямбды. Необходим для обеспечения безопасности и корректности программы при передаче лямбда-выражений, которые не должны содержать нелокальных возвратов (например, возвратов из внешней функции), в inline функции. Это ключевое слово гарантирует, что лямбда-выражение не будет использовать нелокальный возврат, что позволяет безопасно встраивать лямбды, даже если они используются в контексте, где нелокальные возвраты могут привести к неожиданному поведению или ошибкам.

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
