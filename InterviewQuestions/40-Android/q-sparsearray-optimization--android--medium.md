---
id: q-sparsearray-optimization--android--medium--1728115440000
title: "SparseArray and Optimization / SparseArray и оптимизация"
topic: android
aliases:
  - SparseArray and Optimization
  - SparseArray и оптимизация
date_created: 2025-10-05
date_modified: 2025-10-13
status: draft
original_language: en
language_tags:
  - en
  - ru
type: question
category: android
difficulty: medium
subtopics:
  - performance-memory
  - performance-rendering
tags:
  - android
  - sparsearray
  - data-structures
  - performance
  - memory-optimization
  - difficulty/medium
moc: moc-android
related_questions: []
source: "https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20SparseArray.md"
---

# SparseArray and Optimization / SparseArray и оптимизация

# Question (EN)
> 

What do you know about SparseArray?

## Answer (EN)
`SparseArray` maps integers to Objects and, unlike a normal array of Objects, its indices can contain gaps. `SparseArray` is intended to be more memory-efficient than a `HashMap`, because it avoids auto-boxing keys and its data structure doesn't rely on an extra entry object for each mapping.

Note that this container keeps its mappings in an array data structure, using a binary search to find keys. The implementation is not intended to be appropriate for data structures that may contain large numbers of items. It is generally slower than a `HashMap` because lookups require a binary search, and adds and removes require inserting and deleting entries in the array. For containers holding up to hundreds of items, the performance difference is less than 50%.

### Memory Optimization

To help with performance, the container includes an optimization when removing keys: instead of compacting its array immediately, it leaves the removed entry marked as deleted. The entry can then be re-used for the same key or compacted later in a single garbage collection of all removed entries. This garbage collection must be performed whenever the array needs to be grown, or when the map size or entry values are retrieved.

### Iteration

It is possible to iterate over the items in this container using `keyAt(int)` and `valueAt(int)`. Iterating over the keys using `keyAt(int)` with ascending values of the index returns the keys in ascending order. In the case of `valueAt(int)`, the values corresponding to the keys are returned in ascending order.

### Benefits

Benefits to use `SparseArray` over `HashMap`:
- More memory efficient by using primitives
- No auto-boxing
- Allocation-free

### Drawbacks

Drawbacks:
- For large collections, it is slower
- It only available for Android

### Example of Usage

```kotlin
import android.util.SparseArray
import androidx.core.util.set
import androidx.core.util.size

class SparseArrayExample {

    fun example() {
        val sparseArray = SparseArray<String>()
        sparseArray[0] = "First item"
        sparseArray[10] = "Second item"
        sparseArray[24] = "Third item"
        sparseArray[50] = "Fourth item"

        for (i in 0 until sparseArray.size) {
            println("Index = " + sparseArray.keyAt(i) + ", Item = " + sparseArray.valueAt(i))
        }

        if (sparseArray[100] == null) {
            println("SparseArray not contains item with index 100")
        }
    }
}
```

Output:

```
Index = 0, Item = First item
Index = 10, Item = Second item
Index = 24, Item = Third item
Index = 50, Item = Fourth item
SparseArray not contains item with index 100
```

### When to Use SparseArray

Use `SparseArray` when:
- You have a map with integer keys
- The number of items is relatively small (up to hundreds)
- Memory efficiency is more important than lookup speed
- You want to avoid auto-boxing overhead

### Related Classes

Android provides several variants of SparseArray:
- `SparseArray<E>` - maps int to Object
- `SparseBooleanArray` - maps int to boolean
- `SparseIntArray` - maps int to int
- `SparseLongArray` - maps int to long
- `LongSparseArray<E>` - maps long to Object

---

# Вопрос (RU)
> 

Что вы знаете о SparseArray?

## Ответ (RU)
`SparseArray` отображает целые числа на объекты и, в отличие от обычного массива объектов, его индексы могут содержать пропуски. `SparseArray` предназначен для более эффективного использования памяти, чем `HashMap`, поскольку он избегает автоупаковки ключей, а его структура данных не зависит от дополнительного объекта записи для каждого отображения.

Обратите внимание, что этот контейнер хранит свои отображения в структуре данных массива, используя бинарный поиск для нахождения ключей. Реализация не предназначена для структур данных, которые могут содержать большое количество элементов. Обычно она медленнее, чем `HashMap`, потому что поиск требует бинарного поиска, а добавление и удаление требуют вставки и удаления записей в массиве. Для контейнеров, содержащих до сотен элементов, разница в производительности составляет менее 50%.

### Оптимизация памяти

Для повышения производительности контейнер включает оптимизацию при удалении ключей: вместо немедленного сжатия массива он оставляет удаленную запись помеченной как удаленная. Запись затем может быть повторно использована для того же ключа или сжата позже в одной сборке мусора всех удаленных записей. Эта сборка мусора должна выполняться всякий раз, когда массив необходимо увеличить, или когда запрашиваются размер карты или значения записей.

### Итерация

Можно итерировать элементы в этом контейнере, используя `keyAt(int)` и `valueAt(int)`. Итерация по ключам с использованием `keyAt(int)` с возрастающими значениями индекса возвращает ключи в возрастающем порядке. В случае `valueAt(int)` значения, соответствующие ключам, возвращаются в возрастающем порядке.

### Преимущества

Преимущества использования `SparseArray` вместо `HashMap`:
- Более эффективное использование памяти за счет использования примитивов
- Отсутствие автоупаковки
- Без выделения памяти

### Недостатки

Недостатки:
- Для больших коллекций работает медленнее
- Доступен только для Android

### Пример использования

```kotlin
import android.util.SparseArray
import androidx.core.util.set
import androidx.core.util.size

class SparseArrayExample {

    fun example() {
        val sparseArray = SparseArray<String>()
        sparseArray[0] = "First item"
        sparseArray[10] = "Second item"
        sparseArray[24] = "Third item"
        sparseArray[50] = "Fourth item"

        for (i in 0 until sparseArray.size) {
            println("Index = " + sparseArray.keyAt(i) + ", Item = " + sparseArray.valueAt(i))
        }

        if (sparseArray[100] == null) {
            println("SparseArray not contains item with index 100")
        }
    }
}
```

Вывод:

```
Index = 0, Item = First item
Index = 10, Item = Second item
Index = 24, Item = Third item
Index = 50, Item = Fourth item
SparseArray not contains item with index 100
```

### Когда использовать SparseArray

Используйте `SparseArray`, когда:
- У вас есть карта с целочисленными ключами
- Количество элементов относительно невелико (до сотен)
- Эффективность использования памяти важнее скорости поиска
- Вы хотите избежать накладных расходов на автоупаковку

### Связанные классы

Android предоставляет несколько вариантов SparseArray:
- `SparseArray<E>` - отображает int на Object
- `SparseBooleanArray` - отображает int на boolean
- `SparseIntArray` - отображает int на int
- `SparseLongArray` - отображает int на long
- `LongSparseArray<E>` - отображает long на Object

---

## Related Questions

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-deferred-async-patterns--kotlin--medium]] - Performance
- [[q-coroutine-performance-optimization--kotlin--hard]] - Performance
- [[q-channel-buffering-strategies--kotlin--hard]] - Performance
- [[q-custom-dispatchers-limited-parallelism--kotlin--hard]] - Performance
- [[q-kotlin-inline-functions--kotlin--medium]] - Performance

### Related Algorithms
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Data Structures
