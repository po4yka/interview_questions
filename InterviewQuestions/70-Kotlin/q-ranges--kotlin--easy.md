---
id: kotlin-022
title: "Ranges in Kotlin / Диапазоны в Kotlin"
aliases: ["Ranges in Kotlin", "Диапазоны в Kotlin"]

# Classification
topic: kotlin
subtopics: [ranges, iteration, step]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-flatmap-ranges--programming-languages--easy, q-kotlin-let-function--programming-languages--easy]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/easy, kotlin, ranges]
---
# Вопрос (RU)
> Что такое диапазоны в Kotlin и как их использовать?

---

# Question (EN)
> What are ranges in Kotlin and how do you use them?

## Ответ (RU)

Диапазон в Kotlin — это упорядоченная конечная последовательность значений одного совместимого типа, задаваемая границами и шагом. Для стандартных числовых и символьных типов используются специализированные типы (`IntRange`, `LongRange`, `CharRange` и т.п.), которые являются закрытыми диапазонами: начало и конец включительны. Шаг по умолчанию равен 1, не может быть 0 и должен быть положительным.

### Базовое использование

```kotlin
if (i in 1..4) {  // эквивалентно 1 <= i && i <= 4
    print(i)
}
```

### Итерация

```kotlin
for (i in 1..4) print(i)  // Печатает: 1234
```

### Обратная итерация с downTo

```kotlin
for (i in 4 downTo 1) print(i)  // Печатает: 4321
```

### Пользовательский шаг

```kotlin
for (i in 1..8 step 2) print(i)  // Печатает: 1357
for (i in 8 downTo 1 step 2) print(i)  // Печатает: 8642
```

### Исключение конца с until

```kotlin
for (i in 1 until 10) {  // i в [1, 10), 10 исключено
    print(i)  // Печатает: 123456789
}
```

### Способы создания диапазонов и прогрессий

#### 1. Оператор `..`

```kotlin
for (num in 1..5) {
    println(num)
}
// Вывод: 1, 2, 3, 4, 5
```

#### 2. Функция `rangeTo()`

```kotlin
for (num in 1.rangeTo(5)) {
    println(num)
}
// Вывод: 1, 2, 3, 4, 5
```

#### 3. Функция `downTo()`

```kotlin
for (num in 5.downTo(1)) {
    println(num)
}
// Вывод: 5, 4, 3, 2, 1
```

#### 4. Функция `until` (конец исключен)

```kotlin
for (num in 1 until 5) {
    println(num)
}
// Вывод: 1, 2, 3, 4
```

### Функция `step()`

`step` создает прогрессию с заданным положительным шагом на основе существующего диапазона или прогрессии. Шаг по умолчанию равен 1; шаг не может быть 0.

```kotlin
for (i in 3..10 step 2) print("$i ")  // Печатает: 3 5 7 9

println((11..20 step 2).first)  // 11
println((11..20 step 4).last)   // 19
println((11..20 step 5).step)   // 5
```

### Типы диапазонов

- `IntRange` — диапазон целых чисел
- `LongRange` — диапазон значений типа Long
- `CharRange` — диапазон символов

Все они поддерживают использование в цикле `for` и проверку вхождения с оператором `in`.

**Краткое содержание**: Диапазоны (и связанные прогрессии) в Kotlin представляют последовательности значений с началом и концом. Для `..`, `rangeTo` и `downTo` обе границы включительны, `until` создает полузакрытый диапазон с исключенной правой границей. Используйте `step` для пользовательских положительных (не равных 0) шагов. Диапазоны и прогрессии широко применяются для итерации, проверок принадлежности (`in`) и валидации значений.

---

## Answer (EN)

A range in Kotlin is an ordered finite sequence of values of a compatible type, defined by its bounds and step. For standard numeric and character types you get specialized types (`IntRange`, `LongRange`, `CharRange`, etc.) which are closed ranges: start and end are inclusive. The default step is 1 and cannot be 0.

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

### Ways to Create Ranges and Progressions

#### 1. `..` operator

```kotlin
for (num in 1..5) {
    println(num)
}
// Output: 1, 2, 3, 4, 5
```

#### 2. `rangeTo()` function

```kotlin
for (num in 1.rangeTo(5)) {
    println(num)
}
// Output: 1, 2, 3, 4, 5
```

#### 3. `downTo()` function

```kotlin
for (num in 5.downTo(1)) {
    println(num)
}
// Output: 5, 4, 3, 2, 1
```

#### 4. `until` function (end exclusive)

```kotlin
for (num in 1 until 5) {
    println(num)
}
// Output: 1, 2, 3, 4
```

### step() function

`step` creates a progression with the given positive step based on an existing range or progression. Default step is 1; step cannot be 0.

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

All support iteration in for loops and membership checks via the `in` operator.

**English Summary**: In Kotlin, ranges (and the related progressions) represent sequences of values with a start and end. For `..`, `rangeTo`, and `downTo`, both ends are inclusive; `until` creates a half-open range with an exclusive end. Use `step` for custom increments (non-zero, positive). Ranges are commonly used for iteration, membership checks (`in`), and validation.

## Дополнительные вопросы (RU)

- Каковы ключевые отличия диапазонов Kotlin от подхода в Java?
- Когда вы бы использовали диапазоны на практике?
- Каковы распространенные ошибки при работе с диапазонами?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Диапазоны — документация Kotlin](https://kotlinlang.org/docs/reference/ranges.html)

## References

- [[c-kotlin]]
- [Ranges - Kotlin Documentation](https://kotlinlang.org/docs/reference/ranges.html)

## Связанные вопросы (RU)

- [[q-kotlin-collections--kotlin--easy]]

## Related Questions

- [[q-kotlin-collections--kotlin--easy]]
