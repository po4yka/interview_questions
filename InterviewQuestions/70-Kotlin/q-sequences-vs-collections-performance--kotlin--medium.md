---
tags:
  - kotlin
  - sequences
  - collections
  - performance
  - lazy-evaluation
  - optimization
difficulty: medium
status: draft
---

# Sequences vs Collections Performance

# Question (EN)
> When should you use Sequences over Collections? Explain intermediate vs terminal operations and performance implications.

# Вопрос (RU)
> Когда следует использовать Sequences вместо Collections? Объясните промежуточные против терминальных операций и влияние на производительность.

---

## Answer (EN)

**Sequences** use lazy evaluation, while **Collections** use eager evaluation. This affects performance significantly in chained operations.

---

### Collections (Eager)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers
    .filter { it > 2 }     // Creates intermediate list
    .map { it * 2 }        // Creates another intermediate list
    .take(2)               // Creates final list

// 3 intermediate collections created!
```

---

### Sequences (Lazy)

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

val result = numbers
    .asSequence()
    .filter { it > 2 }     // No intermediate list
    .map { it * 2 }        // No intermediate list
    .take(2)               // Evaluation happens here
    .toList()

// Only 1 collection created!
```

---

### Performance Comparison

**Collections:**
- ✅ Fast for small datasets
- ✅ Simple, predictable
- ❌ Creates intermediate collections
- ❌ Processes all elements

**Sequences:**
- ✅ Efficient for large datasets
- ✅ No intermediate collections
- ✅ Short-circuits early
- ❌ Overhead for small datasets

---

### When to Use Sequences

**✅ Large datasets:**

```kotlin
// Process 1 million items
val largeList = (1..1_000_000).toList()

// Sequence: Much faster
largeList.asSequence()
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .take(100)
    .toList()
```

**✅ Multiple chained operations:**

```kotlin
// Many transformations
list.asSequence()
    .filter { ... }
    .map { ... }
    .flatMap { ... }
    .filter { ... }
    .toList()
```

**✅ Early termination:**

```kotlin
// Stops after finding first
list.asSequence()
    .filter { expensive(it) }
    .firstOrNull()
```

---

### When to Use Collections

**✅ Small datasets:**

```kotlin
// 10 items - collection is faster
listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    .filter { it > 5 }
    .map { it * 2 }
```

**✅ Single operation:**

```kotlin
// Just one transformation
list.map { it * 2 }
```

**✅ Multiple terminal operations:**

```kotlin
val seq = list.asSequence().filter { it > 0 }

// Need to evaluate twice - use collection
val sum = seq.sum() // Evaluates entire sequence
val count = seq.count() // Evaluates again!
```

---

## Ответ (RU)

**Sequences** используют ленивое вычисление, в то время как **Collections** используют энергичное вычисление.

### Collections (Энергичные)

Создают промежуточные коллекции на каждом шаге. Быстрее для малых данных.

### Sequences (Ленивые)

Не создают промежуточные коллекции. Эффективнее для больших данных и цепочек операций.

### Когда использовать Sequences

- Большие наборы данных
- Множество цепных операций
- Ранняя терминация (firstOrNull, take)

### Когда использовать Collections

- Малые наборы данных
- Одна операция
- Множество терминальных операций

Sequences оптимизируют производительность для больших данных с ленивым вычислением.
