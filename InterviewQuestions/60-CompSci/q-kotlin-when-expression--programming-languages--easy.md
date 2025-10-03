---
id: 20251003141112
title: Kotlin when expression / Выражение when в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, control-flow]
question_kind: practical
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/878
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-control-flow

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, when, switch, control-flow, pattern-matching, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> How to use when in Kotlin instead of switch

# Вопрос (RU)
> Как использовать when в Kotlin вместо switch

---

## Answer (EN)

`when` in Kotlin replaces Java's `switch` statement and is **much more powerful**.

**Basic syntax:**
```kotlin
fun getDayName(day: Int): String {
    return when (day) {
        1 -> "Monday"
        2 -> "Tuesday"
        3 -> "Wednesday"
        4 -> "Thursday"
        5 -> "Friday"
        6 -> "Saturday"
        7 -> "Sunday"
        else -> "Invalid day"
    }
}
```

**Multiple values per branch:**
```kotlin
when (x) {
    1, 2 -> println("x is 1 or 2")
    in 3..10 -> println("x is between 3 and 10")
    !in 10..20 -> println("x is outside 10-20")
    else -> println("Otherwise")
}
```

**Without argument (replaces if-else chains):**
```kotlin
when {
    x < 0 -> println("Negative")
    x == 0 -> println("Zero")
    x > 0 -> println("Positive")
}
```

**Type checking:**
```kotlin
fun describe(obj: Any): String = when (obj) {
    is String -> "String of length ${obj.length}"
    is Int -> "Int with value $obj"
    is List<*> -> "List of size ${obj.size}"
    else -> "Unknown type"
}
```

**Sealed classes (exhaustive):**
```kotlin
sealed class Result
class Success(val data: String) : Result()
class Error(val message: String) : Result()

fun handle(result: Result) = when (result) {
    is Success -> println(result.data)
    is Error -> println(result.message)
    // No 'else' needed - compiler knows all cases!
}
```

**As expression:**
```kotlin
val result = when (val x = getValue()) {
    1 -> "One"
    2 -> "Two"
    else -> "Other: $x"
}
```

**Advantages over switch:**
- Can be used as expression
- No fall-through (no `break` needed)
- Can check any condition, not just constants
- Supports ranges and type checks
- Exhaustive checking with sealed classes

## Ответ (RU)

В Kotlin оператор when заменяет switch и позволяет проверять значения. Пример: fun getDayName(day: Int): String { return when (day) { 1 -> "Понедельник" ... } } Также можно использовать when без аргумента и проверять логические выражения.

---

## Follow-ups
- What is exhaustiveness checking?
- Can when be used without else?
- How does when work with sealed classes?

## References
- [[c-kotlin-control-flow]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-sealed-classes-purpose--programming-languages--medium]]
