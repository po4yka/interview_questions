---
id: 20251012-122711108
title: "SparseArray Optimization / Оптимизация SparseArray"
aliases:
  - "SparseArray Optimization"
  - "Оптимизация SparseArray"
topic: android
subtopics: [performance-memory, data-structures]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-sparsearray, q-android-memory-optimization--android--medium, q-data-structures-performance--android--medium]
created: 2025-10-05
updated: 2025-01-25
tags: [android/performance-memory, android/data-structures, sparsearray, data-structures, performance, memory-optimization, difficulty/medium]
sources: [https://developer.android.com/reference/android/util/SparseArray]
---

# Вопрос (RU)
> Что такое SparseArray и когда его использовать?

# Question (EN)
> What is SparseArray and when to use it?

---

## Ответ (RU)

**Теория SparseArray:**
SparseArray - это оптимизированная структура данных для отображения целых чисел на объекты. Она более эффективна по памяти, чем HashMap, поскольку избегает автоупаковки ключей и не создает дополнительные объекты для каждой записи.

**Основные преимущества:**
- Экономия памяти за счет использования примитивов
- Отсутствие автоупаковки ключей
- Меньше аллокаций объектов

```kotlin
// Создание и использование SparseArray
val sparseArray = SparseArray<String>()
sparseArray[0] = "Первый элемент"
sparseArray[10] = "Второй элемент"
sparseArray[24] = "Третий элемент"

// Итерация по элементам
for (i in 0 until sparseArray.size()) {
    val key = sparseArray.keyAt(i)
    val value = sparseArray.valueAt(i)
    println("Ключ: $key, Значение: $value")
}
```

**Оптимизация памяти:**
SparseArray использует бинарный поиск для поиска ключей и отложенную сборку мусора для удаленных элементов.

```kotlin
// Удаление элементов с оптимизацией
sparseArray.remove(10) // Помечает как удаленный, не сжимает сразу
sparseArray.put(10, "Новое значение") // Переиспользует удаленную позицию
```

**Варианты SparseArray:**
Android предоставляет специализированные версии для разных типов данных.

```kotlin
// Различные типы SparseArray
val sparseIntArray = SparseIntArray() // int -> int
val sparseBooleanArray = SparseBooleanArray() // int -> boolean
val sparseLongArray = SparseLongArray() // int -> long
val longSparseArray = LongSparseArray<String>() // long -> Object
```

**Когда использовать:**
- Ключи - целые числа
- Небольшое количество элементов (до сотен)
- Память важнее скорости поиска
- Нужно избежать автоупаковки

## Answer (EN)

**SparseArray Theory:**
SparseArray is an optimized data structure for mapping integers to objects. It's more memory-efficient than HashMap because it avoids auto-boxing keys and doesn't create additional objects for each entry.

**Main advantages:**
- Memory savings through primitive usage
- No auto-boxing of keys
- Fewer object allocations

```kotlin
// Creating and using SparseArray
val sparseArray = SparseArray<String>()
sparseArray[0] = "First element"
sparseArray[10] = "Second element"
sparseArray[24] = "Third element"

// Iterating over elements
for (i in 0 until sparseArray.size()) {
    val key = sparseArray.keyAt(i)
    val value = sparseArray.valueAt(i)
    println("Key: $key, Value: $value")
}
```

**Memory optimization:**
SparseArray uses binary search for key lookup and delayed garbage collection for removed elements.

```kotlin
// Removing elements with optimization
sparseArray.remove(10) // Marks as deleted, doesn't compact immediately
sparseArray.put(10, "New value") // Reuses deleted position
```

**SparseArray variants:**
Android provides specialized versions for different data types.

```kotlin
// Different SparseArray types
val sparseIntArray = SparseIntArray() // int -> int
val sparseBooleanArray = SparseBooleanArray() // int -> boolean
val sparseLongArray = SparseLongArray() // int -> long
val longSparseArray = LongSparseArray<String>() // long -> Object
```

**When to use:**
- Keys are integers
- Small number of elements (up to hundreds)
- Memory is more important than lookup speed
- Need to avoid auto-boxing

---

## Follow-ups

- How does SparseArray compare to HashMap in performance?
- What are the memory implications of using SparseArray?
- When should you avoid SparseArray?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-data-structures-basics--android--easy]] - Data structures basics

### Related (Same Level)
- [[q-android-memory-optimization--android--medium]] - Memory optimization
- [[q-data-structures-performance--android--medium]] - Data structures performance
- [[q-android-performance-basics--android--medium]] - Performance basics

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime internals
- [[q-memory-management--android--hard]] - Memory management
