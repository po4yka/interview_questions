---
id: 20251003140301
title: What are inline functions / Что такое inline функции
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, inline, performance]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/23
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
tags: [kotlin, inline-functions, higher-order-functions, lambda-expressions, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What are inline functions

# Вопрос (RU)
> Что такое inline функции

---

## Answer (EN)

Inline functions are a special type of function where the function code is embedded at the call site during compilation. This means that calling an inline function doesn't create a new call stack; instead, the compiler copies the function code directly to the call site. This mechanism is especially useful with higher-order functions that take functions as parameters or return them. Purpose: Reduce function call overhead (no additional function calls or stack creation, improving performance), improve performance with lambda expressions (Kotlin uses objects for lambdas/anonymous functions which can burden the garbage collector - inline functions avoid this by inlining the lambdas), enable language-specific features (only inline functions can use reified type parameters, avoiding runtime type erasure limitations and working with types as regular classes).

## Ответ (RU)

Inline функции — это специальный тип функций, при компиляции которых код функции встраивается в место её вызова. Это значит, что при вызове inline функции не происходит создание нового стека вызовов; вместо этого компилятор копирует код функции непосредственно в место вызова. Этот механизм особенно полезен при использовании функций высшего порядка, которые принимают функции в качестве параметров или возвращают их в результате. Для чего они нужны: Уменьшение накладных расходов на вызов функций. Поскольку не происходит дополнительных вызовов функций и не создаётся новый стек, использование inline функций может значительно умен. Улучшение производительности при использовании лямбда-выражений. Kotlin использует объекты для представления лямбда-выражений и анонимных функций, что может привести к дополнительной нагрузке на сборщик мусора и память. Inline функции позволяют избежать этого, поскольку лямбды, переданные в inline функции, также инлайнятся. Возможность использования некоторых специфичных возможностей языка. Например, только inline функции могут использовать реифицированные типовые параметры что позволяет избежать ограничений связанных с типовой стиранием во время выполнения и работать с типами как с обычными классами.

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
