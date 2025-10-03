---
id: 20251003141101
title: Kotlin favorite features / Любимые фичи Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, features]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/541
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-features

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, features, extensions, null-safety, coroutines, overview, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> Tell me about three favorite Kotlin features

# Вопрос (RU)
> Расскажи про три любимых фичи в Kotlin

---

## Answer (EN)

Three favorite Kotlin features:

### 1. Extension Functions
Add new functions to existing classes without modifying them or using inheritance/patterns:
```kotlin
fun String.addExclamation() = this + "!"
"Hello".addExclamation()  // "Hello!"
```

### 2. Null Safety
Protection from NullPointerException at language level with explicit nullable types:
```kotlin
var name: String = "John"    // Cannot be null
var nullable: String? = null // Can be null
nullable?.length             // Safe call
```

### 3. Coroutines
Convenient asynchronous code and multithreading with simple, synchronous-looking syntax:
```kotlin
suspend fun fetchData() {
    val data = withContext(Dispatchers.IO) {
        // Async operation
    }
}
```

**Why these features matter:**
- **Extensions**: Code reuse without inheritance complexity
- **Null Safety**: Prevents most runtime crashes
- **Coroutines**: Simplifies async programming dramatically

## Ответ (RU)

Три любимые фичи в Kotlin: Extension Functions для добавления новых функций к существующим классам без их изменения, Null Safety для защиты от NullPointerException и упрощенного управления null-значениями, а также Coroutines для удобной работы с асинхронным кодом и многопоточностью...

---

## Follow-ups
- What other Kotlin features are notable?
- How do extensions work under the hood?
- What makes Kotlin coroutines different from threads?

## References
- [[c-kotlin-features]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-extensions-basics--programming-languages--easy]]
- [[q-kotlin-null-safety--programming-languages--medium]]
- [[q-kotlin-coroutines-overview--programming-languages--medium]]
