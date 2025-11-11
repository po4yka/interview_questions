---
id: algo-008
title: "Sorting Algorithms Comparison / Сравнение алгоритмов сортировки"
aliases: ["Sorting Algorithms", "Сравнение алгоритмов сортировки"]
topic: algorithms
subtopics: [heapsort, mergesort, quicksort]
question_kind: coding
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-algorithms, q-binary-search-variants--algorithms--medium, q-graph-algorithms-bfs-dfs--algorithms--hard]
created: 2025-10-12
updated: 2025-11-11
tags: [algorithms, complexity, difficulty/medium, mergesort, quicksort, sorting]
sources: ["https://en.wikipedia.org/wiki/Sorting_algorithm"]

---

# Вопрос (RU)
> Каковы основные алгоритмы сортировки? Сравните их временную/пространственную сложность и когда следует использовать каждый алгоритм?

# Question (EN)
> What are the main sorting algorithms? Compare their time/space complexity and when should you use each algorithm?

---

## Ответ (RU)

**Теория алгоритмов сортировки:**
Сортировка — фундаментальная операция в информатике. Различные алгоритмы имеют разные характеристики сложности и применения в зависимости от типа данных, ограничений по памяти и требований к стабильности.

**Сравнительная таблица:**
| Алгоритм | Лучший | Средний | Худший | Память | Стабильный | На месте |
|----------|--------|---------|--------|--------|------------|----------|
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) | Нет | Да |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | Да | Нет |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) | Нет | Да |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) | Да | Да |
| **Counting Sort*** | O(n + k) | O(n + k) | O(n + k) | O(n + k) | Да | Нет |

\* Counting Sort применим, когда диапазон значений k относительно мал по сравнению с n.

**Когда использовать (кратко):**
- Quick Sort: общий случай, хороший выбор по среднему времени и кэш-локальности; избегать без защиты от худшего случая для уже частично отсортированных/паттерновых данных.
- Merge Sort: когда важна стабильность, предсказуемое O(n log n) и/или удобна работа с потоками/связанными списками.
- Heap Sort: когда нужна O(1) доп. память и приемлемы нестабильность и худшая константа времени.
- Insertion Sort: очень маленькие массивы, почти отсортированные данные; часто используется как часть гибридных алгоритмов.
- Counting Sort: целые ключи из ограниченного диапазона; подходит как базовый шаг в Radix Sort.

**Quick Sort - разделяй и властвуй:**
```kotlin
// Выбор опорного элемента, разделение, рекурсивная сортировка
fun quickSort(arr: IntArray, low: Int = 0, high: Int = arr.size - 1) {
    if (low < high) {
        val pivotIndex = partition(arr, low, high)
        quickSort(arr, low, pivotIndex - 1)
        quickSort(arr, pivotIndex + 1, high)
    }
}

fun partition(arr: IntArray, low: Int, high: Int): Int {
    val pivot = arr[high]
    var i = low - 1

    for (j in low until high) {
        if (arr[j] <= pivot) {
            i++
            // стандартный swap двух элементов
            val temp = arr[i]
            arr[i] = arr[j]
            arr[j] = temp
        }
    }

    // поместить опорный элемент на позицию i+1
    val temp = arr[i + 1]
    arr[i + 1] = arr[high]
    arr[high] = temp

    return i + 1
}
```

**Merge Sort - стабильная сортировка:**
```kotlin
// Разделение пополам, рекурсивная сортировка, слияние
fun mergeSort(arr: IntArray): IntArray {
    if (arr.size <= 1) return arr

    val mid = arr.size / 2
    val left = mergeSort(arr.sliceArray(0 until mid))
    val right = mergeSort(arr.sliceArray(mid until arr.size))

    return merge(left, right)
}

fun merge(left: IntArray, right: IntArray): IntArray {
    val result = IntArray(left.size + right.size)
    var i = 0; var j = 0; var k = 0

    while (i < left.size && j < right.size) {
        if (left[i] <= right[j]) {
            result[k++] = left[i++]
        } else {
            result[k++] = right[j++]
        }
    }

    while (i < left.size) result[k++] = left[i++]
    while (j < right.size) result[k++] = right[j++]

    return result
}
```

**Heap Sort - использование кучи:**
```kotlin
// Построение max-heap, извлечение максимума
fun heapSort(arr: IntArray) {
    val n = arr.size

    // Построение max-heap
    for (i in n / 2 - 1 downTo 0) {
        heapify(arr, n, i)
    }

    // Извлечение элементов из кучи
    for (i in n - 1 downTo 1) {
        val temp = arr[0]
        arr[0] = arr[i]
        arr[i] = temp
        heapify(arr, i, 0)
    }
}

fun heapify(arr: IntArray, n: Int, i: Int) {
    var largest = i
    val left = 2 * i + 1
    val right = 2 * i + 2

    if (left < n && arr[left] > arr[largest]) largest = left
    if (right < n && arr[right] > arr[largest]) largest = right

    if (largest != i) {
        val temp = arr[i]
        arr[i] = arr[largest]
        arr[largest] = temp
        heapify(arr, n, largest)
    }
}
```

**Insertion Sort - для малых массивов:**
```kotlin
// Построение отсортированного массива по одному элементу
fun insertionSort(arr: IntArray) {
    for (i in 1 until arr.size) {
        val key = arr[i]
        var j = i - 1

        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j]
            j--
        }

        arr[j + 1] = key
    }
}
```

**Counting Sort - для малого диапазона:**
```kotlin
// Подсчёт вхождений, восстановление отсортированного массива
// Время: O(n + k), Память: O(n + k), где k — диапазон значений.
fun countingSort(arr: IntArray): IntArray {
    if (arr.isEmpty()) return arr

    val max = arr.maxOrNull()!!
    val min = arr.minOrNull()!!
    val range = max - min + 1

    val count = IntArray(range)
    for (num in arr) count[num - min]++

    for (i in 1 until count.size) {
        count[i] += count[i - 1]
    }

    val output = IntArray(arr.size)
    for (i in arr.indices.reversed()) {
        val num = arr[i]
        output[count[num - min] - 1] = num
        count[num - min]--
    }

    return output
}
```

## Answer (EN)

**Sorting Algorithms Theory:**
Sorting is a fundamental operation in computer science. Different algorithms have different complexity characteristics and use cases depending on data distribution, memory constraints, and stability requirements.

**Comparison Table:**
| Algorithm | Best | Average | Worst | Space | Stable | In-Place |
|-----------|------|---------|-------|-------|--------|----------|
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) | No | Yes |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | No |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) | No | Yes |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) | Yes | Yes |
| **Counting Sort*** | O(n + k) | O(n + k) | O(n + k) | O(n + k) | Yes | No |

*Counting Sort is applicable when the key range k is relatively small compared to n.

**When to use (brief):**
- Quick Sort: general-purpose choice with good average performance and cache locality; avoid naive pivoting on adversarial/structured inputs unless you have worst-case protections.
- Merge Sort: when you require stability, predictable O(n log n) time, or work with linked lists / external data streams.
- Heap Sort: when you need O(1) extra memory and can tolerate being unstable and slightly slower constants.
- Insertion Sort: very small arrays or nearly sorted data; commonly used as a base case in hybrid algorithms.
- Counting Sort: integers/keys from a limited range; often used as a building block in Radix Sort.

**Quick Sort - Divide and Conquer:**
```kotlin
// Pick pivot, partition around it, recursively sort
fun quickSort(arr: IntArray, low: Int = 0, high: Int = arr.size - 1) {
    if (low < high) {
        val pivotIndex = partition(arr, low, high)
        quickSort(arr, low, pivotIndex - 1)
        quickSort(arr, pivotIndex + 1, high)
    }
}

fun partition(arr: IntArray, low: Int, high: Int): Int {
    val pivot = arr[high]
    var i = low - 1

    for (j in low until high) {
        if (arr[j] <= pivot) {
            i++
            // standard swap of two elements
            val temp = arr[i]
            arr[i] = arr[j]
            arr[j] = temp
        }
    }

    // place pivot at position i+1
    val temp = arr[i + 1]
    arr[i + 1] = arr[high]
    arr[high] = temp

    return i + 1
}
```

**Merge Sort - Stable Sorting:**
```kotlin
// Split in half, recursively sort, merge
fun mergeSort(arr: IntArray): IntArray {
    if (arr.size <= 1) return arr

    val mid = arr.size / 2
    val left = mergeSort(arr.sliceArray(0 until mid))
    val right = mergeSort(arr.sliceArray(mid until arr.size))

    return merge(left, right)
}

fun merge(left: IntArray, right: IntArray): IntArray {
    val result = IntArray(left.size + right.size)
    var i = 0; var j = 0; var k = 0

    while (i < left.size && j < right.size) {
        if (left[i] <= right[j]) {
            result[k++] = left[i++]
        } else {
            result[k++] = right[j++]
        }
    }

    while (i < left.size) result[k++] = left[i++]
    while (j < right.size) result[k++] = right[j++]

    return result
}
```

**Heap Sort - Using Heap Data Structure:**
```kotlin
// Build max heap, repeatedly extract max
fun heapSort(arr: IntArray) {
    val n = arr.size

    // Build max heap
    for (i in n / 2 - 1 downTo 0) {
        heapify(arr, n, i)
    }

    // Extract elements from heap
    for (i in n - 1 downTo 1) {
        val temp = arr[0]
        arr[0] = arr[i]
        arr[i] = temp
        heapify(arr, i, 0)
    }
}

fun heapify(arr: IntArray, n: Int, i: Int) {
    var largest = i
    val left = 2 * i + 1
    val right = 2 * i + 2

    if (left < n && arr[left] > arr[largest]) largest = left
    if (right < n && arr[right] > arr[largest]) largest = right

    if (largest != i) {
        val temp = arr[i]
        arr[i] = arr[largest]
        arr[largest] = temp
        heapify(arr, n, largest)
    }
}
```

**Insertion Sort - For Small Arrays:**
```kotlin
// Build sorted array one element at a time
fun insertionSort(arr: IntArray) {
    for (i in 1 until arr.size) {
        val key = arr[i]
        var j = i - 1

        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j]
            j--
        }

        arr[j + 1] = key
    }
}
```

**Counting Sort - For Small Range:**
```kotlin
// Count occurrences, reconstruct sorted array
// Time: O(n + k), Space: O(n + k), where k is the range of values.
fun countingSort(arr: IntArray): IntArray {
    if (arr.isEmpty()) return arr

    val max = arr.maxOrNull()!!
    val min = arr.minOrNull()!!
    val range = max - min + 1

    val count = IntArray(range)
    for (num in arr) count[num - min]++

    for (i in 1 until count.size) {
        count[i] += count[i - 1]
    }

    val output = IntArray(arr.size)
    for (i in arr.indices.reversed()) {
        val num = arr[i]
        output[count[num - min] - 1] = num
        count[num - min]--
    }

    return output
}
```

---

## Follow-ups

- What is the difference between stable and unstable sorting?
- Why is QuickSort preferred over MergeSort in practice?
- What is the lower bound for comparison-based sorting?

## References

- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/Sorting_algorithm"

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-binary-search-variants--algorithms--medium]] - Search algorithms
- [[q-two-pointers-sliding-window--algorithms--medium]] - Two pointers technique

### Advanced (Harder)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP algorithms

## Дополнительные вопросы (RU)
- В чем разница между стабильной и нестабильной сортировкой?
- Почему на практике часто предпочитают QuickSort вместо MergeSort?
- Каков теоретический нижний предел для сравнивающих алгоритмов сортировки?
## Связанные вопросы (RU)
### Предварительные (проще)
- [[q-data-structures-overview--algorithms--easy]] - Основы структур данных
### Связанные (тот же уровень)
- [[q-binary-search-variants--algorithms--medium]] - Алгоритмы поиска
- [[q-two-pointers-sliding-window--algorithms--medium]] - Техника двух указателей
### Продвинутые (сложнее)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Динамическое программирование