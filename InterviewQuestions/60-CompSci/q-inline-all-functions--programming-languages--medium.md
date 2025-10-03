---
id: 20251003140310
title: Can all functions be made inline at compiler level / Можно ли на уровне компилятора сделать все функции inline
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, inline, compiler]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/689
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
tags: [kotlin, inline-functions, compiler-optimization, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> Can all functions be made inline at compiler level

# Вопрос (RU)
> Можно ли на уровне компилятора сделать все функции inline

---

## Answer (EN)

No, not all functions can be made inline at compiler level: 1. Compiler makes decisions based on function size and performance optimization. 2. Recursive functions or complex constructs cannot be inlined as this may cause errors or increased code size. 3. Forced use of inline directives is possible but not always effective.

## Ответ (RU)

Нет, не все функции можно сделать на уровне компилятора: 1. Компилятор принимает решение на основе размера функции и оптимизации производительности. 2. Рекурсивные функции или сложные конструкции не могут быть встроены, так как это может вызвать ошибки или увеличенный размер кода. 3. Принудительное использование inline директив возможно, но это не всегда эффективно.

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
