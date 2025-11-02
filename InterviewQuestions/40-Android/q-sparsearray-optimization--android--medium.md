---
id: android-012
title: "SparseArray Optimization / Оптимизация SparseArray"
aliases: ["SparseArray Optimization", "Оптимизация SparseArray"]
topic: android
subtopics: [performance-memory, profiling]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-sparsearray, q-android-memory-optimization--android--medium, q-hashmap-vs-sparsearray--android--medium]
created: 2025-10-05
updated: 2025-10-28
tags: [android/performance-memory, android/profiling, sparsearray, memory-optimization, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Что такое SparseArray и когда его использовать вместо HashMap?

# Question (EN)
> What is SparseArray and when to use it instead of HashMap?

---

## Ответ (RU)

**Концепция:**
SparseArray — оптимизированная структура данных для отображения int → Object. Избегает автоупаковки ключей (Integer boxing) и использует два массива: int[] для ключей и Object[] для значений. Внутри — бинарный поиск вместо хеширования.

**Компромиссы:**
- Экономия памяти: ~30–50% по сравнению с HashMap<Integer, V>
- Производительность: O(log n) вместо O(1), критично при >1000 элементов
- Подходит для: небольших коллекций (<100 элементов), разреженных ключей

```kotlin
// ✅ Эффективное использование SparseArray
val viewCache = SparseArray<View>(8) // preallocate capacity
viewCache.put(R.id.button, button)
viewCache.put(R.id.text_view, textView)

// Итерация без автоупаковки
for (i in 0 until viewCache.size()) {
    val viewId = viewCache.keyAt(i)  // ✅ Примитив int
    val view = viewCache.valueAt(i)
}
```

```kotlin
// ❌ Антипаттерн: большие коллекции
val userMap = SparseArray<User>(10_000)  // ❌ Медленно из-за бинарного поиска
userMap[userId] = user

// ✅ Лучше использовать HashMap для больших данных
val userMap = HashMap<Int, User>(10_000)
```

**Специализированные варианты:**
```kotlin
SparseIntArray()      // int → int (без объектов)
SparseBooleanArray()  // int → boolean
SparseLongArray()     // int → long
LongSparseArray<T>()  // long → Object
```

**Оптимизация удаления:**
```kotlin
// Ленивое удаление: remove() помечает как DELETE, сжатие откладывается
sparseArray.remove(key)  // Не вызывает System.arraycopy сразу
sparseArray.put(key, newValue)  // Может переиспользовать слот
```

## Answer (EN)

**Concept:**
SparseArray is an optimized data structure for int → Object mapping. Avoids Integer boxing by using two arrays: int[] for keys and Object[] for values. Internally uses binary search instead of hashing.

**Trade-offs:**
- Memory savings: ~30–50% compared to HashMap<Integer, V>
- Performance: O(log n) instead of O(1), critical above 1000 elements
- Suitable for: small collections (<100 elements), sparse keys

```kotlin
// ✅ Efficient SparseArray usage
val viewCache = SparseArray<View>(8) // preallocate capacity
viewCache.put(R.id.button, button)
viewCache.put(R.id.text_view, textView)

// Iteration without boxing
for (i in 0 until viewCache.size()) {
    val viewId = viewCache.keyAt(i)  // ✅ Primitive int
    val view = viewCache.valueAt(i)
}
```

```kotlin
// ❌ Anti-pattern: large collections
val userMap = SparseArray<User>(10_000)  // ❌ Slow due to binary search
userMap[userId] = user

// ✅ Prefer HashMap for large datasets
val userMap = HashMap<Int, User>(10_000)
```

**Specialized variants:**
```kotlin
SparseIntArray()      // int → int (no objects)
SparseBooleanArray()  // int → boolean
SparseLongArray()     // int → long
LongSparseArray<T>()  // long → Object
```

**Deletion optimization:**
```kotlin
// Lazy deletion: remove() marks as DELETE, compaction is deferred
sparseArray.remove(key)  // Doesn't call System.arraycopy immediately
sparseArray.put(key, newValue)  // May reuse the slot
```

---

## Follow-ups

- What's the memory overhead difference between SparseArray and HashMap quantitatively?
- When does the O(log n) lookup cost outweigh memory savings?
- How does SparseArray handle collisions compared to HashMap?
- What happens during SparseArray compaction (gc() method)?
- Are there thread-safety considerations with SparseArray?

## References

- [[c-sparsearray]] - SparseArray concept note
- [[c-hash-map]] - HashMap internals
- https://developer.android.com/reference/android/util/SparseArray

## Related Questions

### Prerequisites (Easier)
- [[q-collections-basics--kotlin--easy]] - Collections fundamentals
- [[q-boxing-unboxing--kotlin--easy]] - Boxing overhead

### Related (Same Level)
- [[q-android-memory-optimization--android--medium]] - Memory optimization strategies
- [[q-hashmap-vs-sparsearray--android--medium]] - Performance comparison
- [[q-view-holder-pattern--android--medium]] - SparseArray in ViewHolder

### Advanced (Harder)
- [[q-memory-profiling--android--hard]] - Profiling memory allocations
- [[q-custom-data-structures--android--hard]] - Building optimized collections
