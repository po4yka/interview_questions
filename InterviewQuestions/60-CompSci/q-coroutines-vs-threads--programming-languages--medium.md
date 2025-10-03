---
id: 20251003140810
title: Coroutines vs Threads / Корутины против потоков
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, coroutines, java]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/418
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-coroutines
  - c-threading
  - c-concurrency

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, coroutines, threads, java, concurrency, comparison, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the conceptual difference between coroutines and Java threads

# Вопрос (RU)
> В чем концептуальное отличие корутинов от потоков в Java

---

## Answer (EN)

**Coroutines** are lightweight and managed at the language level, unlike threads which are heavyweight and OS-managed.

**Key differences:**

| Aspect | Coroutines | Threads |
|--------|-----------|---------|
| Weight | Lightweight (thousands possible) | Heavyweight (limited by OS) |
| Management | Language-level (Kotlin runtime) | OS-level |
| Cost | Low memory/CPU overhead | High memory/CPU overhead |
| Context switching | Cheap (user space) | Expensive (kernel space) |
| Blocking | Suspending (non-blocking) | Blocking |

**Coroutines are more efficient** for I/O operations and have simpler code through `suspend` functions.

## Ответ (RU)

Корутины легковесные и управляются на уровне языка, в отличие от потоков которые тяжелые и управляются ОС. Корутины эффективнее при операциях ввода-вывода и имеют более простой код.

---

## Follow-ups
- When should you still use threads?
- How do coroutines work under the hood?
- What is the relationship between coroutines and thread pools?

## References
- [[c-kotlin-coroutines]]
- [[c-threading]]
- [[c-concurrency]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-coroutines-overview--programming-languages--medium]]
- [[q-coroutine-dispatchers--programming-languages--medium]]
