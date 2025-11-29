---
id: kotlin-022
title: "Ranges in Kotlin / Диапазоны в Kotlin"
aliases: ["Ranges in Kotlin", "Диапазоны в Kotlin"]

# Classification
topic: kotlin
subtopics: [iteration, ranges, step]
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
related: [c-kotlin]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [difficulty/easy, kotlin, ranges]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---
# Вопрос (RU)
> Что такое диапазоны в Kotlin и как их использовать?

---

# Question (EN)
> What are ranges in Kotlin and how do you use them?

## Ответ (RU)

Диапазон в Kotlin — это упорядоченная конечная последовательность значений одного совместимого типа, задаваемая границами. Для стандартных числовых и символьных типов используются специализированные типы диапазонов (`IntRange`, `LongRange`, `CharRange` и т.п.), которые являются закрытыми диапазонами: начало и конец включительны.

Конструкции `..`, `downTo`, `until` и `step` создают объекты типов диапазонов и числовых прогрессий (`IntProgression`, `LongProgression`, `CharProgression` и соответствующих им `*Range`). Шаг по умолчанию равен 1, не может быть 0 и всегда положителен для возрастающих прогрессий; для `downTo` используется убывающая прогрессия с отрицательным внутренним шагом.

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
for (i in 8 downTo 1 step 2) print(i)  // Печатает: 8642
```

### Исключение Конца С until

```kotlin
for (i in 1 until 10) {  // i в [1, 10), 10 исключено
    print(i)  // Печатает: 123456789
}
```

### Способы Создания Диапазонов И Прогрессий

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

`step` создает числовую прогрессию с заданным шагом на основе существующего диапазона или прогрессии. Шаг по умолчанию равен 1 и не может быть 0. Для возрастающих прогрессий шаг положителен, для прогрессий от `downTo` фактический шаг отрицателен.

```kotlin
for (i in 3..10 step 2) print("$i ")  // Печатает: 3 5 7 9

println((11..20 step 2).first)  // 11
println((11..20 step 4).last)   // 19
println((11..20 step 5).step)   // 5
```

### Типы Диапазонов И Прогрессий

- `IntRange`, `LongRange`, `CharRange`, `UIntRange`, `ULongRange` — диапазоны для соответствующих типов
- `IntProgression`, `LongProgression`, `CharProgression` — базовые типы для прогрессий с шагом

Все они поддерживают использование в цикле `for` и проверку вхождения с оператором `in` (для диапазонов).

**Краткое содержание**: Диапазоны и прогрессии в Kotlin представляют последовательности значений с началом и концом. Для `..`, `rangeTo` и `downTo` обе границы включительны, `until` создает полузакрытый диапазон с исключенной правой границей. Используйте `step` для задания шага (не равного 0); для прямых прогрессий он положителен, для `downTo` — убывающий. Диапазоны и прогрессии широко применяются для итерации, проверок принадлежности (`in`) и валидации значений.

---

## Answer (EN)

A range in Kotlin is an ordered finite sequence of values of a compatible type, defined by its bounds. For standard numeric and character types you get specialized range types (`IntRange`, `LongRange`, `CharRange`, etc.) which are closed ranges: both start and end are inclusive.

The `..`, `downTo`, `until`, and `step` constructs create instances of range and numeric progression types (`IntProgression`, `LongProgression`, `CharProgression` and their corresponding `*Range` types). The default step is 1 and cannot be 0. For increasing progressions the step is positive; for `downTo` you get a decreasing progression with a negative internal step.

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

#### 1. `..` Operator

```kotlin
for (num in 1..5) {
    println(num)
}
// Output: 1, 2, 3, 4, 5
```

#### 2. `rangeTo()` Function

```kotlin
for (num in 1.rangeTo(5)) {
    println(num)
}
// Output: 1, 2, 3, 4, 5
```

#### 3. `downTo()` Function

```kotlin
for (num in 5.downTo(1)) {
    println(num)
}
// Output: 5, 4, 3, 2, 1
```

#### 4. `until` Function (end exclusive)

```kotlin
for (num in 1 until 5) {
    println(num)
}
// Output: 1, 2, 3, 4
```

### step() Function

`step` creates a numeric progression with the given step based on an existing range or progression. The default step is 1 and it cannot be 0. For increasing progressions the step is positive; for `downTo` the resulting progression has a negative step.

```kotlin
for (i in 3..10 step 2) print("$i ")  // Prints: 3 5 7 9

println((11..20 step 2).first)  // 11
println((11..20 step 4).last)   // 19
println((11..20 step 5).step)   // 5
```

### Range and Progression Types

- `IntRange`, `LongRange`, `CharRange`, `UIntRange`, `ULongRange` - ranges for the corresponding types
- `IntProgression`, `LongProgression`, `CharProgression` - base types for step-based progressions

All of them support iteration in `for` loops, and range types support membership checks via the `in` operator.

**English Summary**: In Kotlin, ranges and progressions represent sequences of values with a start and end. For `..`, `rangeTo`, and `downTo`, both ends are inclusive; `until` creates a half-open interval with an exclusive end. Use `step` for custom (non-zero) step values; it's positive for increasing progressions and negative for `downTo`. Ranges and progressions are commonly used for iteration, membership checks (`in`), and validation.

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия диапазонов Kotlin от подхода в Java?
- Когда вы бы использовали диапазоны на практике?
- Каковы распространенные ошибки при работе с диапазонами?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Диапазоны и прогрессии — документация Kotlin](https://kotlinlang.org/docs/ranges.html)

## References

- [[c-kotlin]]
- [Ranges and progressions - Kotlin Documentation](https://kotlinlang.org/docs/ranges.html)

## Связанные Вопросы (RU)

- [[q-kotlin-collections--kotlin--easy]]

## Related Questions

- [[q-kotlin-collections--kotlin--easy]]
