---
id: 20251003141109
title: Not-null assertion operator (!!) / Оператор утверждения о ненулевости (!!)
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, null-safety]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/734
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-null-safety

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, not-null-assertion, double-bang, null-safety, operators, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What do you know about double bang (!!)?

# Вопрос (RU)
> Что известно о double bang (!!)?

---

## Answer (EN)

The `!!` operator (not-null assertion) is used to **explicitly indicate that a value is not null**.

**Behavior:**
- If value is **not null**: Returns the value
- If value **is null**: Throws `KotlinNullPointerException`

**Example:**
```kotlin
var nullable: String? = "Hello"
val length = nullable!!.length  // OK, returns 5

nullable = null
val length2 = nullable!!.length  // Throws KotlinNullPointerException!
```

**When it's used:**

```kotlin
// When you're absolutely sure value is not null
fun process(input: String?) {
    val trimmed = input!!.trim()  // "I know it's not null!"
}

// Better alternatives:
fun process(input: String?) {
    // Option 1: Safe call
    val trimmed = input?.trim()
    
    // Option 2: Elvis operator
    val trimmed = input?.trim() ?: return
    
    // Option 3: let
    input?.let { trimmed ->
        // Use trimmed
    }
}
```

**Why it's generally discouraged:**

1. **Defeats null safety**: One of Kotlin's main features
2. **Hard to debug**: Stack trace shows `!!` location, not actual cause
3. **Crashes app**: Just like Java's NullPointerException
4. **Better alternatives exist**: Safe calls, Elvis operator, let

**Legitimate use cases:**

- Interfacing with legacy Java code
- After explicit null check (but smart casts are better)
- Platform types from Java (but better to use safe calls)

**Best practice:** Avoid `!!` and use safer alternatives like `?.`, `?:`, or proper null checks.

## Ответ (RU)

Оператор !! используется для явного указания, что значение не null. При использовании !! если значение оказывается null выбрасывается исключение KotlinNullPointerException. Рекомендуется избегать !! и использовать безопасные вызовы (?.) или оператор ?: для обработки null.

---

## Follow-ups
- When is !! acceptable to use?
- How does !! differ from as vs as??
- What are platform types?

## References
- [[c-kotlin-null-safety]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-null-safety--programming-languages--medium]]
- [[q-kotlin-safe-cast--programming-languages--easy]]
