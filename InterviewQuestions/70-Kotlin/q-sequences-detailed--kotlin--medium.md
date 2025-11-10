---
id: kotlin-013
title: "Sequences in Kotlin / Последовательности в Kotlin"
aliases: ["Sequences in Kotlin", "Последовательности в Kotlin"]

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
related: [c-kotlin, q-kotlin-collections--kotlin--easy, q-list-vs-sequence--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [collections, difficulty/medium, kotlin, lazy-evaluation, performance, sequences]
---
# Вопрос (RU)
> Что такое последовательности в Kotlin и чем они отличаются от Iterable?

# Question (EN)
> What are sequences in Kotlin and how do they differ from Iterables?

## Ответ (RU)

Последовательности в Kotlin предоставляют схожий набор операций с коллекциями и Iterable, но реализуют другой подход к многоэтапной обработке данных за счёт **ленивого вычисления** и отсутствия промежуточных коллекций.

Важно: `Sequence` и `Iterable` — разные интерфейсы. Коллекции в стандартной библиотеке реализуют `Iterable`, а не `Sequence`. Для использования ленивых операций коллекции нужно явно преобразовать в последовательность через `asSequence()` или создать её с помощью `sequenceOf()` и других фабричных функций.

### Жадное vs ленивое вычисление

**Iterable (жадное):**
- Операции над коллекциями (например, `map`, `filter`) выполняются над всей коллекцией и создают промежуточные коллекции на каждом шаге.
- Каждый этап обработки полностью завершается, затем результат передаётся на следующий этап.

**Sequence (ленивое):**
- Промежуточные операции не выполняются сразу и не создают промежуточных коллекций.
- Обработка элементов откладывается до вызова терминальной операции.
- При терминальной операции все этапы применяются к элементам по цепочке, **элемент за элементом**.

### Порядок выполнения

**Iterable:** сначала выполняется, например, `filter` для всех элементов, создаётся список отфильтрованных элементов, затем `map` или `forEach` проходят по нему и т.д.

**Sequence:** для каждого элемента по очереди применяются все промежуточные операции, затем элемент, при необходимости, попадает в результат.

### Пример (ленивое выполнение)

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
// filter: A
// forEach: A
// filter: B
// forEach: B
// filter: C
// forEach: C
```

### Пример (жадное выполнение через коллекцию / Iterable)

```kotlin
listOf("A", "B", "C")
    .filter {
        println("filter: $it")
        true
    }
    .forEach {
        println("forEach: $it")
    }

// Вывод (по шагам):
// filter: A
// filter: B
// filter: C
// forEach: A
// forEach: B
// forEach: C
```

### Промежуточные и терминальные операции

- Промежуточные операции (`map`, `filter`, `take`, `drop`, `distinct`, `sorted` и т.д.):
  - Для последовательностей возвращают новый `Sequence`.
  - Выполняются лениво, логика применяется при обходе элементов.
  - Некоторые операции (например, `sorted`, `distinct`) являются "stateful" и требуют хранения части или всех уже просмотренных элементов.

- Терминальные операции (`toList`, `sum`, `forEach`, `first`, `find` и т.д.):
  - Запускают вычисление цепочки операций над `Sequence`.
  - Возвращают конечный результат и не возвращают новый `Sequence`.

### Когда использовать

**Используйте `Sequence`, когда:**
- Обрабатываете большие коллекции.
- Есть несколько последовательных операций трансформации.
- Не требуется обработка всех элементов (например, используете `first`, `find`, `take`, прерываете поиск).
- Операции над элементами дорогостоящие, и важно избежать создания промежуточных коллекций.

**Используйте коллекции/Iterable, когда:**
- Размер данных небольшой.
- Операции простые, и накладные расходы ленивой обработки могут быть выше выгоды.
- Нужны все результаты сразу и код проще с жадной семантикой.

**Краткое содержание:** Последовательности используют ленивое вычисление: операции применяются к элементам по цепочке и выполняются только при вызове терминальной операции, без создания промежуточных коллекций. Обычные операции над коллекциями (через `Iterable`) работают жадно, обрабатывая всю коллекцию на каждом шаге и создавая промежуточные структуры. Для больших наборов данных и длинных цепочек операций это делает `Sequence` более эффективным, а для маленьких — наоборот.

См. также: [[c-kotlin]]

## Answer (EN)

Sequences in Kotlin provide a similar set of operations as collections/Iterables, but use a different execution model: **lazy evaluation** with no intermediate collections between steps.

Important: `Sequence` and `Iterable` are different interfaces. Standard Kotlin collection types implement `Iterable`, not `Sequence`. To use lazy operations you either build a sequence directly (e.g. `sequenceOf(...)`) or convert a collection with `asSequence()`.

### Eager vs Lazy Evaluation

**Iterable / collections (eager):**
- Operations like `map` and `filter` process the entire collection eagerly.
- Each step produces a new intermediate collection, which becomes input for the next step.

**Sequence (lazy):**
- Intermediate operations do not execute immediately and do not create intermediate collections.
- Actual work is deferred until a terminal operation is invoked.
- When a terminal operation runs, all steps are applied in a pipeline, **element by element**.

### Execution Order Difference

**Iterable:** completes each operation for the whole collection, then moves to the next operation.

**Sequence:** applies all operations one-by-one for each element as it flows through the pipeline.

### Example (lazy sequence)

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
// filter: A
// forEach: A
// filter: B
// forEach: B
// filter: C
// forEach: C
```

### Example (eager via collection / Iterable)

```kotlin
// Iterable (via List) - eager evaluation
listOf("A", "B", "C")
    .filter {
        println("filter: $it")
        true
    }
    .forEach {
        println("forEach: $it")
    }

// Output (step-by-step):
// filter: A
// filter: B
// filter: C
// forEach: A
// forEach: B
// forEach: C
```

### Sequence Operations

- Intermediate operations (e.g. `map`, `filter`, `take`, `drop`, `distinct`, `sorted`):
  - On sequences, they return another `Sequence` and are evaluated lazily.
  - Some are stateless in the sense they don't need to see the entire input (`map`, `filter`, `take`, `drop` only track position/count), while others are stateful (`sorted`, `distinct` keep substantial state / may need all elements).

- Terminal operations (e.g. `toList`, `sum`, `forEach`, `first`, `find`):
  - Trigger evaluation of the sequence pipeline.
  - Produce a final result and do not return another `Sequence`.

### When to Use

Sequences help avoid building intermediate collections and can **improve performance** when:
- Working with large collections.
- Having multiple chained transformations.
- Not all elements need to be processed (short-circuiting operations like `first`, `find`, `any`, `take`).
- Per-element operations are expensive.

However, lazy processing has its own overhead and can be slower for small collections or very simple operations.

**Use Sequence when:**
- Large collections.
- Multiple transformation steps.
- Short-circuiting or partial consumption is expected.
- Expensive operations and you want to minimize temporary allocations.

**Use Iterable/collections when:**
- Small collections.
- Simple logic.
- You want straightforward eager semantics and need all results.

**English Summary**: Sequences use lazy evaluation: operations are applied element-by-element and executed only when a terminal operation is called, without creating intermediate collections. Iterable-based collection operations are eager: each step processes the entire collection and usually creates intermediate collections. Sequences shine for large datasets and long chains of operations, while eager collection operations are often simpler and faster for small data.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Sequences - Kotlin Documentation](https://kotlinlang.org/docs/reference/sequences.html)

## Related Questions
- [[q-kotlin-collections--kotlin--easy]]
- [[q-list-vs-sequence--kotlin--medium]]
