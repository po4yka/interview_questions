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
related: [c-kotlin, q-channel-buffering-strategies--kotlin--hard, q-cold-vs-hot-flows--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [control-flow, difficulty/easy, kotlin, switch, syntax, when]
---
# Вопрос (RU)
> Какой оператор используется вместо switch в Kotlin?

# Question (EN)
> Which operator is used instead of switch in Kotlin?

## Ответ (RU)

В Kotlin вместо `switch` используется **выражение `when`**. Оно может использоваться и как выражение (возвращает значение), и как оператор (как `if`), и при этом более мощное: поддерживает значения, диапазоны, условия и множественные ветки.

См. также: [[c-kotlin]]

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

**Ключевые преимущества по сравнению с классическим Java `switch`:**

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

**4. Условия (when без аргумента):**

```kotlin
when {
    x < 0 -> "Отрицательное"
    x == 0 -> "Ноль"
    x > 0 -> "Положительное"
    else -> "Неизвестно"
}
```

(Важно: произвольные булевы условия вида `x > 0` допустимы только в форме `when` без аргумента. В форме `when (x)` ветки сопоставляются со значением `x`.)

**5. Как выражение:**

```kotlin
val result = when (status) {
    200 -> "OK"
    404 -> "Не найдено"
    500 -> "Ошибка сервера"
    else -> "Неизвестно"
}
```

**6. Нет неявного проваливания (не нужен `break`):**

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
| Условия | - | `when { x > 0 -> }` |
| Выражение | (как switch-выражение с Java 14+) | `when` является выражением и может возвращать значение |
| Проваливание | По умолчанию есть, без `break` | Неявное проваливание отсутствует |
| `break` | Часто требуется | Не нужен |

**Резюме:**

`when` — это замена `switch` в Kotlin, предлагающая большую гибкость, безопасность и выразительность.

## Answer (EN)

In Kotlin, the **`when` expression** is used instead of `switch`. It can be used both as an expression (returning a value) and as a statement (like `if`), and it is more powerful: it supports values, ranges, conditions, and multiple branches.

See also: [[c-kotlin]]

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

**Key advantages over the classic Java `switch`:**

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

**4. Conditions (when without argument):**
```kotlin
when {
    x < 0 -> "Negative"
    x == 0 -> "Zero"
    x > 0 -> "Positive"
    else -> "Unknown"
}
```

(Important: arbitrary boolean conditions like `x > 0` are valid only in the `when` without an argument. In `when (x)`, branches are matched against the value of `x`.)

**5. As expression:**
```kotlin
val result = when (status) {
    200 -> "OK"
    404 -> "Not Found"
    500 -> "Server Error"
    else -> "Unknown"
}
```

**6. No implicit fall-through (no `break` needed):**
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
| Conditions | - | `when { x > 0 -> }` |
| Expression | (as switch expression since Java 14+) | `when` is an expression and can return a value |
| Fall-through | Enabled by default without `break` | No implicit fall-through |
| `break` | Often required | Not needed |

**Summary:**
`when` is Kotlin's replacement for `switch`, offering more flexibility, safety, and expressiveness.

---

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
