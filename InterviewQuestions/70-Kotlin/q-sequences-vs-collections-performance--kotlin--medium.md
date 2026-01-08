---id: kotlin-176
title: "Sequences Vs Collections Performance / Sequences vs Collections Performance"
aliases: [Collections Performance, Lazy Evaluation, Performance Comparison, Sequences]
topic: kotlin
subtopics: [collections, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, c-compose-recomposition, c-kotlin, c-perfetto, c-power-profiling, q-callsuper-annotation--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [collections, difficulty/medium, kotlin, lazy-evaluation, optimization, performance, sequences]
---
# Вопрос (RU)
> Когда следует использовать Sequences вместо Collections? Объясните промежуточные против терминальных операций и влияние на производительность.

---

# Question (EN)
> When should you use Sequences over Collections? Explain intermediate vs terminal operations and performance implications.

## Ответ (RU)

**Sequences** используют ленивое вычисление, в то время как **Collections** используют энергичное вычисление. Это влияет на способ обработки цепочек операций и использование памяти.

### Collections (Энергичные)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers
    .filter { it > 2 }     // Создаётся промежуточный список
    .map { it * 2 }        // Создаётся ещё один промежуточный список
    .take(2)               // Создаётся финальный список из 2 элементов

// Выделяется несколько списков: по одному на каждый шаг и итоговый результат.
```

- Промежуточные операции (`filter`, `map` и т.п.) создают новые коллекции.
- Все элементы, как правило, обрабатываются на каждом шаге.
- Часто быстрее и проще для небольших наборов данных и коротких цепочек.

### Sequences (Ленивые)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers
    .asSequence()
    .filter { it > 2 }     // Нет материализованного промежуточного списка
    .map { it * 2 }        // Всё ещё без промежуточного списка
    .take(2)               // Лениво ограничивает последовательность
    .toList()              // Терминальная операция: элементы обрабатываются по одному

// Создаётся только итоговый список; элементы проходят через всю цепочку лениво.
```

- Промежуточные операции не создают промежуточные коллекции.
- Элементы обрабатываются поэлементно через всю цепочку операций, вычисление откладывается до терминальной операции.
- Позволяют эффективнее обрабатывать большие наборы данных и длинные цепочки операций, особенно при ранней остановке.
- Имеют накладные расходы на каждый элемент, поэтому для небольших коллекций или простых операций могут быть невыгодны.

### Сравнение Производительности

**Collections:**
- Просты и быстры для маленьких и средних наборов данных.
- Предсказуемое поведение.
- Промежуточные операции создают новые коллекции.
- Обычно заново проходят все элементы для каждой терминальной операции.

**Sequences:**
- Избегают промежуточных коллекций; элементы проходят конвейер по одному.
- Могут завершаться раньше с терминальными операциями (`first`, `firstOrNull`, `any`, `take` и др.).
- Особенно полезны для:
  - больших наборов данных,
  - длинных цепочек преобразований,
  - сценариев, где не нужно потреблять все элементы.
- Вводят накладные расходы на каждый элемент, из-за чего на малых данных могут быть медленнее коллекций.

### Когда Использовать Sequences

**Большие наборы данных / ранняя остановка:**

```kotlin
// Обрабатываем 1 млн элементов, но останавливаемся после первых 100 подходящих
val largeList = (1..1_000_000).toList()

val topMatches = largeList.asSequence()
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(100)         // Останавливает конвейер после 100 элементов
    .toList()
```

**Множественные сложные преобразования:**

```kotlin
val result = list.asSequence()
    .filter { /* ... */ }
    .map { /* ... */ }
    .flatMap { /* ... */ }
    .filter { /* ... */ }
    .toList()
```

**Ранняя терминация с дорогими проверками:**

```kotlin
val firstMatch = list.asSequence()
    .filter { expensive(it) }
    .firstOrNull()    // Останавливается, как только найден подходящий элемент
```

### Когда Использовать Collections

**Малые наборы данных:**

```kotlin
// Для маленького списка энергичные операции обычно дешевле
listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    .filter { it > 5 }
    .map { it * 2 }
```

**Одна простая операция:**

```kotlin
// Одна трансформация: Sequence добавит ненужные накладные расходы
val doubled = list.map { it * 2 }
```

**Несколько терминальных операций над одними данными:**

```kotlin
// Лучше использовать коллекцию, которую можно переиспользовать
val positives = list.filter { it > 0 }

val sum = positives.sum()
val count = positives.count()
```

Если использовать `Sequence`:

```kotlin
val seq = list.asSequence().filter { it > 0 }
val sumSeq = seq.sum()
val countSeq = seq.count() // Повторно проходит источник и фильтр
```

Sequences оптимизируют использование памяти и могут улучшать производительность для больших данных и ленивых сценариев, но не являются автоматически быстрее во всех случаях.

## Answer (EN)

**Sequences** use lazy evaluation, while **Collections** use eager evaluation. This affects how chained operations are executed and memory is used.

---

### Collections (Eager)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers
    .filter { it > 2 }     // Creates an intermediate list
    .map { it * 2 }        // Creates another intermediate list
    .take(2)               // Creates the final list with 2 elements

// Multiple lists are allocated: one per intermediate step plus the final result.
```

---

### Sequences (Lazy)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers
    .asSequence()
    .filter { it > 2 }     // No intermediate materialized list
    .map { it * 2 }        // Still no materialized list
    .take(2)               // Lazily limits the sequence
    .toList()              // Terminal operation: elements are processed one-by-one

// Only the final list is created; elements flow through the whole chain lazily.
```

---

### Performance Comparison

**Collections:**
- Fast and straightforward for small to medium datasets.
- Simple, predictable behavior.
- Intermediate operations allocate new collections.
- Typically process all elements for each terminal operation.

**Sequences:**
- Avoid intermediate collections; process elements one-by-one through the pipeline.
- Can short-circuit early with terminal operations like `first`, `firstOrNull`, `any`, `take`, etc.
- Especially beneficial for:
  - large datasets,
  - long chains of transformations,
  - scenarios where you don't need to consume all elements.
- Introduce per-element overhead; for small collections or simple operations, this overhead can make them slower than using collections directly.

---

### When to Use Sequences

**Large datasets / early termination:**

```kotlin
// Process 1 million items, but stop after first 100 matching
val largeList = (1..1_000_000).toList()

val topMatches = largeList.asSequence()
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(100)         // Stops pipeline after 100 elements
    .toList()
```

**Multiple chained operations:**

```kotlin
val result = list.asSequence()
    .filter { /* ... */ }
    .map { /* ... */ }
    .flatMap { /* ... */ }
    .filter { /* ... */ }
    .toList()
```

**Early termination with expensive checks:**

```kotlin
val firstMatch = list.asSequence()
    .filter { expensive(it) }
    .firstOrNull()    // Stops as soon as condition is met
```

---

### When to Use Collections

**Small datasets:**

```kotlin
// For a small list, eager operations are typically cheaper
listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    .filter { it > 5 }
    .map { it * 2 }
```

**Single simple operation:**

```kotlin
// Just one transformation: a sequence adds unnecessary overhead
val doubled = list.map { it * 2 }
```

**Multiple terminal operations on the same data:**

```kotlin
// Better to use a collection that can be reused
val positives = list.filter { it > 0 }

val sum = positives.sum()
val count = positives.count()
```

If you used a sequence like below, the underlying data would be traversed again for each terminal operation:

```kotlin
val seq = list.asSequence().filter { it > 0 }
val sumSeq = seq.sum()
val countSeq = seq.count() // Re-traverses the source and filter
```

---

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия от Java Streams?
- Когда вы бы использовали это на практике?
- Каковы типичные подводные камни (например, забытая терминальная операция, повторное использование `Sequence`, использование последовательностей над блокирующим I/O)?

## Follow-ups

- What are the key differences between this and Java Streams?
- When would you use this in practice?
- What are common pitfalls to avoid (e.g., forgetting terminal operations, reusing sequences, sequences over blocking I/O)?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-collections]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-collections]]

## Связанные Вопросы (RU)

- [[q-callsuper-annotation--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]

## Related Questions

- [[q-callsuper-annotation--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
