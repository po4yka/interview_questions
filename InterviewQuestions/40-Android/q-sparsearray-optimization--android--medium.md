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
related: [c-android, q-android-build-optimization--android--medium]
created: 2025-10-05
updated: 2025-11-11
tags: [android/performance-memory, android/profiling, difficulty/medium, memory-optimization, sparsearray]
sources: []
anki_cards:
  - slug: android-012-0-en
    front: "What is SparseArray and when to use it instead of HashMap<Int, V>?"
    back: |
      **SparseArray** - optimized int-to-Object mapping.

      **Advantages over HashMap<Integer, V>**:
      - No Integer boxing (uses primitive int[] keys)
      - Less memory overhead

      **Trade-offs**:
      - O(log n) lookup (binary search) vs HashMap's O(1)
      - Best for small-medium collections (up to few thousand entries)

      ```kotlin
      val cache = SparseArray<View>(8)
      cache.put(R.id.button, button)
      ```

      **Variants**: `SparseIntArray`, `SparseBooleanArray`, `LongSparseArray`
    tags:
      - android_general
      - difficulty::medium
  - slug: android-012-0-ru
    front: "Что такое SparseArray и когда его использовать вместо HashMap<Int, V>?"
    back: |
      **SparseArray** - оптимизированное отображение int в Object.

      **Преимущества над HashMap<Integer, V>**:
      - Нет боксинга Integer (использует примитивный int[] для ключей)
      - Меньше накладных расходов памяти

      **Компромиссы**:
      - O(log n) поиск (бинарный) против O(1) у HashMap
      - Лучше для небольших коллекций (до нескольких тысяч элементов)

      ```kotlin
      val cache = SparseArray<View>(8)
      cache.put(R.id.button, button)
      ```

      **Варианты**: `SparseIntArray`, `SparseBooleanArray`, `LongSparseArray`
    tags:
      - android_general
      - difficulty::medium

---
# Вопрос (RU)
> Что такое SparseArray и когда его использовать вместо `HashMap` с ключами `Int`?

# Question (EN)
> What is SparseArray and when to use it instead of `HashMap` with `Int` keys?

---

## Ответ (RU)

**Концепция:**
SparseArray — оптимизированная структура данных для отображения int → Object. Избегает автоупаковки ключей (Integer boxing) и использует два массива: int[] для ключей и Object[] для значений. Ключи хранятся отсортированными, для поиска используется бинарный поиск (`Arrays.binarySearch`) вместо хеширования. См. также [[c-android]].

**Компромиссы:**
- Экономия памяти: обычно заметно меньше overhead по сравнению с `HashMap<Integer, V>`, за счёт отсутствия Integer-объектов и хеш-таблицы.
- Производительность: операции поиска — O(log n) из-за бинарного поиска, тогда как у `HashMap` амортизированно O(1). При очень больших коллекциях и частых обращениях может быть медленнее.
- Подходит для: коллекций с int-ключами, когда важна экономия памяти и количество элементов не чрезмерно велико (часто до нескольких тысяч), а также при разреженных ключах.

```kotlin
// ✅ Эффективное использование SparseArray
val viewCache = SparseArray<View>(8) // preallocate capacity
viewCache.put(R.id.button, button)
viewCache.put(R.id.text_view, textView)

// Итерация без автоупаковки
for (i in 0 until viewCache.size()) {
    val viewId = viewCache.keyAt(i)  // ✅ примитив int
    val view = viewCache.valueAt(i)
}
```

```kotlin
// ❌ Потенциальный антипаттерн: очень большие коллекции
val userMap = SparseArray<User>(10_000)  // Может быть медленно из-за O(log n) поиска
userMap[userId] = user

// ✅ Для больших и интенсивно используемых наборов данных
// часто лучше подходит HashMap
val userMap = HashMap<Int, User>(10_000)
```

**Специализированные варианты:**
```kotlin
SparseIntArray()      // int → int (без объектов)
SparseBooleanArray()  // int → boolean
SparseLongArray()     // int → long
LongSparseArray<T>()  // long → Object (в android.util или androidx.collection)
```

**Оптимизация удаления:**
```kotlin
// Ленивое удаление: remove() помечает элемент как DELETED,
// фактическое сжатие массива (gc()) откладывается до подходящей операции
sparseArray.remove(key)      // Не вызывает немедленный System.arraycopy
sparseArray.put(key, value)  // Может переиспользовать слот или триггернуть сжатие
```

---

## Answer (EN)

**Concept:**
SparseArray is an optimized data structure for int → Object mapping. It avoids Integer boxing by using two arrays: int[] for keys and Object[] for values. Keys are kept sorted and lookups use binary search (`Arrays.binarySearch`) instead of hashing. See also [[c-android]].

**Trade-offs:**
- Memory: typically significantly less overhead than `HashMap<Integer, V>` due to no Integer objects and no hash table.
- Performance: lookups are O(log n) because of binary search, while `HashMap` offers amortized O(1). For very large collections with frequent access, SparseArray can be slower.
- Suitable for: int-keyed collections where memory efficiency matters and the size is not extremely large (often up to a few thousand entries), and for sparse key spaces.

```kotlin
// ✅ Efficient SparseArray usage
val viewCache = SparseArray<View>(8) // preallocate capacity
viewCache.put(R.id.button, button)
viewCache.put(R.id.text_view, textView)

// Iteration without boxing
for (i in 0 until viewCache.size()) {
    val viewId = viewCache.keyAt(i)  // ✅ primitive int
    val view = viewCache.valueAt(i)
}
```

```kotlin
// ❌ Potential anti-pattern: extremely large collections
val userMap = SparseArray<User>(10_000)  // May be slower due to O(log n) lookups
userMap[userId] = user

// ✅ For large, heavily accessed datasets
// HashMap is often a better fit
val userMap = HashMap<Int, User>(10_000)
```

**Specialized variants:**
```kotlin
SparseIntArray()      // int → int (no objects)
SparseBooleanArray()  // int → boolean
SparseLongArray()     // int → long
LongSparseArray<T>()  // long → Object (in android.util or androidx.collection)
```

**Deletion optimization:**
```kotlin
// Lazy deletion: remove() marks an entry as DELETED.
// Actual compaction (gc()) is deferred until a suitable operation occurs.
sparseArray.remove(key)      // Does not immediately call System.arraycopy
sparseArray.put(key, value)  // May reuse the slot or trigger compaction
```

---

## Дополнительные Вопросы (RU)

- В чем количественная разница в накладных расходах памяти между SparseArray и `HashMap`?
- В какой момент стоимость поиска O(log n) перевешивает выигрыш по памяти?
- Как SparseArray обрабатывает конфликты по сравнению с `HashMap`?
- Что происходит во время операции сжатия SparseArray (метод gc())?
- Есть ли особенности потокобезопасности при использовании SparseArray?

## Follow-ups

- What's the memory overhead difference between SparseArray and `HashMap` quantitatively?
- When does the O(log n) lookup cost outweigh memory savings?
- How does SparseArray handle collisions compared to `HashMap`?
- What happens during SparseArray compaction (gc() method)?
- Are there thread-safety considerations with SparseArray?

---

## Ссылки (RU)

- "https://developer.android.com/reference/android/util/SparseArray"

## References

- "https://developer.android.com/reference/android/util/SparseArray"

---

## Связанные Вопросы (RU)

### База (проще)
- [[q-android-app-components--android--easy]] - Обзор компонентов Android-приложения

### Связанные (тот Же уровень)
- [[q-android-build-optimization--android--medium]] - Стратегии оптимизации памяти

### Продвинутые (сложнее)
- [[q-android-performance-measurement-tools--android--medium]] - Инструменты профилирования и анализа производительности

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android app components overview

### Related (Same Level)
- [[q-android-build-optimization--android--medium]] - Memory optimization strategies

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]] - Profiling and performance tools
