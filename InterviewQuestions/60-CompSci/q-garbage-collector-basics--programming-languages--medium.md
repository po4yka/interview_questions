---
id: 20251003141007
title: Garbage collector basics / Основы сборщика мусора
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, java, memory-management]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/444
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-memory-management
  - c-garbage-collection

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [garbage-collector, gc, memory-management, kotlin, java, performance, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is garbage collector

# Вопрос (RU)
> Что такое сборщик мусора

---

## Answer (EN)

**Garbage Collector (GC)** is a memory management mechanism that automatically frees unused memory occupied by objects to which there are no more references.

**How it works:**

1. **Tracks object references**: Monitors which objects are still reachable from program
2. **Identifies garbage**: Objects with no references are considered garbage
3. **Reclaims memory**: Frees memory occupied by unreachable objects
4. **Runs in background**: Executes periodically without manual intervention

**In Kotlin/Java:**
- GC works in the background automatically
- Eliminates need to manually free memory (unlike C/C++)
- Helps prevent memory leaks
- Makes memory management safer and simpler

**Benefits:**
- Automatic memory management
- Prevents memory leaks
- Reduces programmer errors
- Improves developer productivity

**Considerations:**
- GC pauses can affect performance
- No control over when GC runs
- Objects remain in memory until GC runs

**Example of memory reclamation:**
```kotlin
fun createObject() {
    val obj = LargeObject()  // Object created
    // ... use obj
}  // obj becomes unreachable here, eligible for GC
```

## Ответ (RU)

Сборщик мусора (Garbage Collector) — это механизм управления памятью, который автоматически освобождает неиспользуемую память, занятую объектами, к которым больше нет ссылок...

---

## Follow-ups
- What are different GC algorithms?
- How to optimize for garbage collection?
- What are memory leaks in GC languages?

## References
- [[c-memory-management]]
- [[c-garbage-collection]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-memory-leaks-prevention--programming-languages--medium]]
