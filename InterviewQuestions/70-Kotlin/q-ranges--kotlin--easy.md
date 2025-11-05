---
id: kotlin-022
title: "Ranges in Kotlin / Диапазоны в Kotlin"
aliases: ["Ranges in Kotlin, Диапазоны в Kotlin"]

# Classification
topic: kotlin
subtopics: [downto, iteration, ranges]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-flatmap-ranges--programming-languages--easy, q-kotlin-let-function--programming-languages--easy, q-retry-exponential-backoff-flow--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [difficulty/easy, downto, iteration, kotlin, ranges, rangeto, step]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---
# Вопрос (RU)
> Что такое диапазоны в Kotlin и как их использовать?

---

# Question (EN)
> What are ranges in Kotlin and how do you use them?
## Ответ (RU)

Диапазон — это коллекция конечных значений, определенная конечными точками. Состоит из начала, конца и шага. Начало и конец включительны, шаг по умолчанию 1.

### Базовое Использование

```kotlin
if (i in 1..4) {  // эквивалентно 1 <= i && i <= 4
    print(i)
}
```

### Итерация

```kotlin
for (i in 1..4) print(i)  // Печатает: 1234
```

### Обратная Итерация С downTo

```kotlin
for (i in 4 downTo 1) print(i)  // Печатает: 4321
```

### Пользовательский Шаг

```kotlin
for (i in 1..8 step 2) print(i)  // Печатает: 1357
```

### Исключение Конца С until

```kotlin
for (i in 1 until 10) {  // i в [1, 10), 10 исключено
    print(i)  // Печатает: 123456789
}
```

### Три Способа Создания Диапазонов

1. **Оператор `..`**
2. **Функция `rangeTo()`**
3. **Функция `downTo()`**

**Краткое содержание**: Диапазоны представляют последовательности значений с началом, концом (оба включительно) и шагом. Создаются с `..`, `rangeTo()` или `downTo()`. Используйте `step` для пользовательских приращений, `until` для исключения конца. Поддерживают итерацию в циклах for.

---

## Answer (EN)

A range is a collection of finite values defined by endpoints. Consists of a start, stop, and step. Start and stop are inclusive, step defaults to 1.

### Basic Usage

```kotlin
if (i in 1..4) {  // equivalent of 1 <= i && i <= 4
    print(i)
}
```

### Iteration

```kotlin
for (i in 1..4) print(i)  // Prints: 1234
```

### Reverse Iteration with downTo

```kotlin
for (i in 4 downTo 1) print(i)  // Prints: 4321
```

### Custom Step

```kotlin
for (i in 1..8 step 2) print(i)  // Prints: 1357
for (i in 8 downTo 1 step 2) print(i)  // Prints: 8642
```

### Excluding End with until

```kotlin
for (i in 1 until 10) {  // i in [1, 10), 10 is excluded
    print(i)  // Prints: 123456789
}
```

### Three Ways to Create Ranges

#### 1. `..` Operator

```kotlin
for(num in 1..5) {
    println(num)
}
// Output: 1, 2, 3, 4, 5
```

#### 2. `rangeTo()` Function

```kotlin
for(num in 1.rangeTo(5)) {
    println(num)
}
// Output: 1, 2, 3, 4, 5
```

#### 3. `downTo()` Function

```kotlin
for(num in 5.downTo(1)) {
    println(num)
}
// Output: 5, 4, 3, 2, 1
```

### step() Function

Provides gap between values. Default step is 1. Step cannot be 0.

```kotlin
for (i in 3..10 step 2) print("$i ")  // Prints: 3 5 7 9

println((11..20 step 2).first)  // 11
println((11..20 step 4).last)   // 19
println((11..20 step 5).step)   // 5
```

### Range Types

- `IntRange` - range of integers
- `LongRange` - range of longs
- `CharRange` - range of characters

All support iteration in for loops.

**English Summary**: Ranges represent sequences of values with start, stop (both inclusive), and step. Create with `..`, `rangeTo()`, or `downTo()`. Use `step` for custom increments, `until` to exclude end. Support iteration in for loops. Common for: iteration, membership checks (in), validation.

## References
- [Ranges - Kotlin Documentation](https://kotlinlang.org/docs/reference/ranges.html)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions
- [[q-kotlin-collections--kotlin--easy]]
