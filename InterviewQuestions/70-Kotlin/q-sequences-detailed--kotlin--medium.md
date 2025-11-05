---
id: kotlin-013
title: "Sequences in Kotlin / Последовательности в Kotlin"
aliases: ["Sequences in Kotlin, Последовательности в Kotlin"]

# Classification
topic: kotlin
subtopics: [collections, lazy-evaluation, performance]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-collections--kotlin--easy, q-list-vs-sequence--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [collections, difficulty/medium, kotlin, lazy-evaluation, performance, sequences]
date created: Sunday, October 12th 2025, 12:27:46 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Question (EN)
> What are sequences in Kotlin and how do they differ from Iterables?
# Вопрос (RU)
> Что такое последовательности в Kotlin и чем они отличаются от Iterable?

---

## Answer (EN)

Sequences offer the same functions as Iterable but implement a different approach to multi-step collection processing through **lazy evaluation**.

### Eager Vs Lazy Evaluation

**Iterable (Eager)**: Each processing step completes fully and returns intermediate collection. Next step executes on this collection.

**Sequence (Lazy)**: Processing steps execute only when result is requested. Actual computing happens when terminal operation is called.

### Execution Order Difference

**Iterable**: Completes each step for **whole collection**, then proceeds to next step.

**Sequence**: Performs all processing steps **one-by-one for every element**.

### Example

```kotlin
// Sequence - lazy evaluation
sequenceOf("A", "B", "C")
    .filter {
        println("filter: $it")
        true
    }
    .forEach {
        println("forEach: $it")
    }

// Output (element-by-element):
// filter:  A
// forEach: A
// filter:  B
// forEach: B
// filter:  C
// forEach: C

// Iterable - eager evaluation
listOf("A", "B", "C")
    .filter {
        println("filter: $it")
        true
    }
    .forEach {
        println("forEach: $it")
    }

// Output (step-by-step):
// filter:  A
// filter:  B
// filter:  C
// forEach: A
// forEach: B
// forEach: C
```

### Sequence Operations

#### Stateless Operations

Require no state, process each element independently:
- `map()`, `filter()`, `take()`, `drop()`

#### Stateful Operations

Require significant state, proportional to number of elements:
- `sorted()`, `distinct()`

### Intermediate Vs Terminal Operations

**Intermediate**: Returns another sequence (lazy), like `filter()`, `map()`

**Terminal**: Produces result, like `toList()`, `sum()`, `forEach()`

### When to Use

Sequences let you avoid building intermediate results, **improving performance** for large collections or expensive operations.

However, lazy nature adds overhead for small collections or simple computations.

**Use Sequence when**:
- Processing large collections
- Multiple transformation steps
- Not all elements need processing
- Expensive operations

**Use Iterable when**:
- Small collections
- Simple operations
- Need all results immediately

**English Summary**: Sequences use lazy evaluation - operations execute element-by-element only when terminal operation is called. Iterables use eager evaluation - each step processes entire collection. Sequences avoid intermediate collections, improving performance for large datasets and chained operations. Use sequences for large collections with multiple transformations; iterables for small collections and simple operations.

## Ответ (RU)

Последовательности предлагают те же функции что и Iterable, но реализуют другой подход к многоэтапной обработке коллекций через **ленивое вычисление**.

### Жадное Vs Ленивое Вычисление

**Iterable (жадное)**: Каждый этап обработки завершается полностью и возвращает промежуточную коллекцию.

**Sequence (ленивое)**: Этапы обработки выполняются только когда запрошен результат.

### Пример

```kotlin
sequenceOf("A", "B", "C")
    .filter {
        println("filter: $it")
        true
    }
    .forEach {
        println("forEach: $it")
    }

// Вывод (элемент за элементом):
// filter:  A
// forEach: A
// filter:  B
// forEach: B
// filter:  C
// forEach: C
```

### Когда Использовать

**Используйте Sequence когда**:
- Обработка больших коллекций
- Множественные этапы трансформации
- Не все элементы нужно обрабатывать
- Дорогостоящие операции

**Используйте Iterable когда**:
- Маленькие коллекции
- Простые операции
- Нужны все результаты сразу

**Краткое содержание**: Последовательности используют ленивое вычисление - операции выполняются элемент за элементом только при вызове терминальной операции. Iterable используют жадное вычисление - каждый этап обрабатывает всю коллекцию. Последовательности избегают промежуточных коллекций, улучшая производительность для больших наборов данных.

---

## References
- [Sequences - Kotlin Documentation](https://kotlinlang.org/docs/reference/sequences.html)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions
- [[q-kotlin-collections--kotlin--easy]]
- [[q-list-vs-sequence--kotlin--medium]]
