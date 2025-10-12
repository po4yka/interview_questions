---
tags:
  - control-flow
  - expressions
  - kotlin
  - programming-languages
  - switch
  - syntax
  - when
  - when-expression
difficulty: easy
status: draft
---

# Какой оператор используется вместо switch в Kotlin?

# Question (EN)
> Which operator is used instead of switch in Kotlin?

# Вопрос (RU)
> Какой оператор используется вместо switch в Kotlin?

---

## Answer (EN)

In Kotlin, the **`when` expression** is used instead of `switch`. It is a more powerful tool with support for values, ranges, conditions, and multiple branches.

**Basic usage:**
```kotlin
fun describe(x: Int): String {
    return when (x) {
        1 -> "One"
        2 -> "Two"
        3 -> "Three"
        else -> "Other"
    }
}
```

**Key advantages over Java's `switch`:**

**1. Multiple values in one branch:**
```kotlin
when (x) {
    1, 2, 3 -> println("1-3")
    4, 5 -> println("4-5")
    else -> println("Other")
}
```

**2. Ranges:**
```kotlin
when (age) {
    in 0..12 -> "Child"
    in 13..19 -> "Teenager"
    in 20..64 -> "Adult"
    else -> "Senior"
}
```

**3. Type checking:**
```kotlin
when (obj) {
    is String -> println("String of length ${obj.length}")
    is Int -> println("Integer: $obj")
    is Boolean -> println("Boolean: $obj")
    else -> println("Unknown")
}
```

**4. Conditions (without argument):**
```kotlin
when {
    x < 0 -> "Negative"
    x == 0 -> "Zero"
    x > 0 -> "Positive"
    else -> "Unknown"
}
```

**5. As expression:**
```kotlin
val result = when (status) {
    200 -> "OK"
    404 -> "Not Found"
    500 -> "Server Error"
    else -> "Unknown"
}
```

**6. No fall-through (no `break` needed):**
```kotlin
// Java switch (before Java 14):
switch (x) {
    case 1:
        System.out.println("One");
        break;  // Need break!
    case 2:
        System.out.println("Two");
        break;
}

// Kotlin when:
when (x) {
    1 -> println("One")  // No break needed
    2 -> println("Two")
}
```

**Comparison:**

| Feature | Java `switch` | Kotlin `when` |
|---------|---------------|---------------|
| Syntax | `switch (x) { case 1: }` | `when (x) { 1 -> }` |
| Multiple values | - | `1, 2, 3 ->` |
| Ranges | - | `in 1..10 ->` |
| Type checks | - | `is String ->` |
| Conditions | - | `x > 0 ->` |
| Expression | (Java 14+) | Always |
| Fall-through | (default) | Not allowed |
| `break` | Required | Not needed |

**Summary:**
`when` is Kotlin's replacement for `switch`, offering more flexibility, safety, and expressiveness.

---

## Ответ (RU)

В Kotlin switch заменён на when. Это более мощный инструмент с поддержкой значений, диапазонов, условий и множественных веток.

