---
id: kotlin-186
title: "Kotlin When Vs Switch / When vs Switch"
aliases: [Control Flow, When Expression, When Operator, When vs Switch]
topic: kotlin
subtopics: [control-flow, syntax]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-channel-buffering-strategies--kotlin--hard, q-cold-vs-hot-flows--kotlin--medium, q-flow-operators--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [control-flow, difficulty/easy, kotlin, switch, syntax, when]
date created: Friday, October 31st 2025, 6:29:12 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Какой Оператор Используется Вместо Switch В Kotlin?

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

В Kotlin вместо `switch` используется **выражение `when`**. Это более мощный инструмент с поддержкой значений, диапазонов, условий и множественных веток.

**Базовое использование:**

```kotlin
fun describe(x: Int): String {
    return when (x) {
        1 -> "Один"
        2 -> "Два"
        3 -> "Три"
        else -> "Другое"
    }
}
```

**Ключевые преимущества по сравнению с Java `switch`:**

**1. Множественные значения в одной ветке:**

```kotlin
when (x) {
    1, 2, 3 -> println("1-3")
    4, 5 -> println("4-5")
    else -> println("Другое")
}
```

**2. Диапазоны:**

```kotlin
when (age) {
    in 0..12 -> "Ребенок"
    in 13..19 -> "Подросток"
    in 20..64 -> "Взрослый"
    else -> "Пожилой"
}
```

**3. Проверка типа:**

```kotlin
when (obj) {
    is String -> println("Строка длиной ${obj.length}")
    is Int -> println("Целое: $obj")
    is Boolean -> println("Булево: $obj")
    else -> println("Неизвестно")
}
```

**4. Условия (без аргумента):**

```kotlin
when {
    x < 0 -> "Отрицательное"
    x == 0 -> "Ноль"
    x > 0 -> "Положительное"
    else -> "Неизвестно"
}
```

**5. Как выражение:**

```kotlin
val result = when (status) {
    200 -> "OK"
    404 -> "Не найдено"
    500 -> "Ошибка сервера"
    else -> "Неизвестно"
}
```

**6. Нет проваливания (не нужен `break`):**

```kotlin
// Java switch (до Java 14):
switch (x) {
    case 1:
        System.out.println("Один");
        break;  // Нужен break!
    case 2:
        System.out.println("Два");
        break;
}

// Kotlin when:
when (x) {
    1 -> println("Один")  // Не нужен break
    2 -> println("Два")
}
```

**Таблица сравнения:**

| Функция | Java `switch` | Kotlin `when` |
|---------|---------------|---------------|
| Синтаксис | `switch (x) { case 1: }` | `when (x) { 1 -> }` |
| Множественные значения | - | `1, 2, 3 ->` |
| Диапазоны | - | `in 1..10 ->` |
| Проверки типа | - | `is String ->` |
| Условия | - | `x > 0 ->` |
| Выражение | (Java 14+) | Всегда |
| Проваливание | (по умолчанию) | Не разрешено |
| `break` | Обязателен | Не нужен |

**Резюме:**

`when` - это замена Kotlin для `switch`, предлагающая большую гибкость, безопасность и выразительность.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-cold-vs-hot-flows--kotlin--medium]]
- [[q-channel-buffering-strategies--kotlin--hard]]
- [[q-flow-operators--kotlin--medium]]
