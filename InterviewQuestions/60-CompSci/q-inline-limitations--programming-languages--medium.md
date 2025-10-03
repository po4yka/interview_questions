---
id: 20251003140306
title: Are there cases when you cannot use inline / Бывают ли случаи, когда нельзя использовать inline ?
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, inline]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/179
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
tags: [kotlin, inline, functions, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> Are there cases when you cannot use inline

# Вопрос (RU)
> Бывают ли случаи, когда нельзя использовать inline ?

---

## Answer (EN)

There are situations when using the inline modifier may be unacceptable or impossible. Main cases when inline is undesirable or impossible: 1. Large function code can lead to increased compiled code size. 2. Recursive functions cannot be inlined directly due to infinite loop risk (however, you can inline part of the function using local inline functions for recursive calls). 3. Virtual functions or interface functions cannot be declared as inline due to the need for dynamic resolution. 4. Calls inside inline functions that cannot be inlined will be processed as regular calls, reducing inline efficiency.

## Ответ (RU)

Существуют ситуации, когда использование inline модификатора может быть неприемлемым или невозможным. Основные случаи, когда использование inline может быть нежелательным или невозможным: 1. Большой объём кода функции может привести к увеличению размера скомпилированного кода. 2. Рекурсивные функции невозможно встроить напрямую из-за риска бесконечного цикла. Однако можно встроить часть функции с помощью локальных inline функций для рекурсивных вызовов. 3. Виртуальные функции или функции интерфейса не могут быть объявлены как inline из-за необходимости динамического разрешения. 4. Вызовы внутри inline функций, которые не могут быть встроены, будут обрабатываться как обычные вызовы. Это может снизить эффективность использования inline.

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
