---
id: "20251015082237166"
title: "Kotlin When Expression / Выражение when в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - control-flow
  - kotlin
  - pattern-matching
  - programming-languages
  - switch
  - when
---
# Как использовать when в Kotlin вместо switch?

# Question (EN)
> How to use when in Kotlin instead of switch?

# Вопрос (RU)
> Как использовать when в Kotlin вместо switch?

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

---

## Ответ (RU)

В Kotlin оператор when заменяет switch и позволяет проверять значения. Пример: fun getDayName(day: Int): String { return when (day) { 1 -> "Понедельник" ... } } Также можно использовать when без аргумента и проверять логические выражения.

