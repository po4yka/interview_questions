---
id: 20251012-200001
title: "Sorting Algorithms Comparison / Сравнение алгоритмов сортировки"
topic: algorithms
difficulty: medium
status: draft
created: 2025-10-12
tags: - algorithms
  - sorting
  - quicksort
  - mergesort
  - complexity
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-algorithms
related_questions:   - q-binary-search--algorithms--easy
  - q-time-space-complexity--algorithms--easy
slug: sorting-algorithms-comparison-algorithms-medium
subtopics:   - sorting
  - quicksort
  - mergesort
  - heapsort
  - time-complexity
---
# Sorting Algorithms Comparison

## English Version

### Problem Statement

Sorting is one of the most fundamental operations in computer science. Understanding different sorting algorithms, their time/space complexity, and when to use each is essential for technical interviews and real-world applications.

**The Question:** What are the main sorting algorithms? Compare their time/space complexity and when should you use each algorithm?

### Detailed Answer

#### Comparison Table

| Algorithm | Best | Average | Worst | Space | Stable | In-Place |
|-----------|------|---------|-------|-------|--------|----------|
| **Bubble Sort** | O(n) | O(n²) | O(n²) | O(1) |  Yes |  Yes |
| **Selection Sort** | O(n²) | O(n²) | O(n²) | O(1) |  No |  Yes |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) |  Yes |  Yes |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) |  Yes |  No |
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) |  No |  Yes |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) |  No |  Yes |
| **Counting Sort** | O(n+k) | O(n+k) | O(n+k) | O(k) |  Yes |  No |
| **Radix Sort** | O(nk) | O(nk) | O(nk) | O(n+k) |  Yes |  No |

**Stable** = Preserves relative order of equal elements
**In-Place** = Requires O(1) extra space

---

### 1. Quick Sort (Most Important)

**Divide-and-conquer:** Pick pivot, partition around it, recursively sort.

```kotlin
fun quickSort(arr: IntArray, low: Int = 0, high: Int = arr.size - 1) {
    if (low < high) {
        // Partition and get pivot index
        val pivotIndex = partition(arr, low, high)
        
        // Recursively sort left and right
        quickSort(arr, low, pivotIndex - 1)
        quickSort(arr, pivotIndex + 1, high)
    }
}

fun partition(arr: IntArray, low: Int, high: Int): Int {
    val pivot = arr[high]  // Choose last element as pivot
    var i = low - 1  // Index of smaller element
    
    for (j in low until high) {
        if (arr[j] <= pivot) {
            i++
            // Swap arr[i] and arr[j]
            arr[i] = arr[j].also { arr[j] = arr[i] }
        }
    }
    
    // Swap arr[i+1] and arr[high] (pivot)
    arr[i + 1] = arr[high].also { arr[high] = arr[i + 1] }
    
    return i + 1
}

// Example:
val arr = intArrayOf(10, 7, 8, 9, 1, 5)
quickSort(arr)
println(arr.contentToString())  // [1, 5, 7, 8, 9, 10]
```

**How it works:**
```
Initial: [10, 7, 8, 9, 1, 5]
         Pick pivot = 5

Partition:
[1, 5, 8, 9, 7, 10]
    ↑ pivot at index 1

Recursively sort left:  [1]  (already sorted)
Recursively sort right: [8, 9, 7, 10]
  Pick pivot = 10
  Partition: [8, 9, 7, 10]
             [7, 8, 9, 10]
                        ↑ pivot
  Continue...

Final: [1, 5, 7, 8, 9, 10]
```

**Complexity:**
- **Best:** O(n log n) - balanced partitions
- **Average:** O(n log n)
- **Worst:** O(n²) - already sorted array
- **Space:** O(log n) - recursion stack

**Optimization: Random Pivot**
```kotlin
fun partitionRandomPivot(arr: IntArray, low: Int, high: Int): Int {
    // Pick random pivot
    val randomIndex = (low..high).random()
    
    // Swap random with last
    arr[randomIndex] = arr[high].also { arr[high] = arr[randomIndex] }
    
    return partition(arr, low, high)
}
```

** When to use:**
- General-purpose sorting
- Average case O(n log n)
- In-place sorting needed
- **Default choice** for most cases

** When NOT to use:**
- Need guaranteed O(n log n) worst case
- Need stable sort
- Stack overflow concerns (deep recursion)

---

### 2. Merge Sort

**Divide-and-conquer:** Split in half, recursively sort, merge.

```kotlin
fun mergeSort(arr: IntArray): IntArray {
    if (arr.size <= 1) return arr
    
    val mid = arr.size / 2
    val left = mergeSort(arr.sliceArray(0 until mid))
    val right = mergeSort(arr.sliceArray(mid until arr.size))
    
    return merge(left, right)
}

fun merge(left: IntArray, right: IntArray): IntArray {
    val result = IntArray(left.size + right.size)
    var i = 0  // left pointer
    var j = 0  // right pointer
    var k = 0  // result pointer
    
    // Merge while both arrays have elements
    while (i < left.size && j < right.size) {
        if (left[i] <= right[j]) {
            result[k++] = left[i++]
        } else {
            result[k++] = right[j++]
        }
    }
    
    // Copy remaining elements
    while (i < left.size) result[k++] = left[i++]
    while (j < right.size) result[k++] = right[j++]
    
    return result
}

// Example:
val arr = intArrayOf(38, 27, 43, 3, 9, 82, 10)
val sorted = mergeSort(arr)
println(sorted.contentToString())  // [3, 9, 10, 27, 38, 43, 82]
```

**How it works:**
```
Initial: [38, 27, 43, 3, 9, 82, 10]

Split:
       [38, 27, 43, 3]    [9, 82, 10]
       /           \          /       \
  [38, 27]      [43, 3]   [9, 82]   [10]
   /    \        /   \     /   \      |
[38]  [27]    [43]  [3]  [9] [82]   [10]

Merge:
[27, 38]      [3, 43]   [9, 82]   [10]
       \      /              \      /
    [3, 27, 38, 43]        [9, 10, 82]
            \                  /
         [3, 9, 10, 27, 38, 43, 82]
```

**Complexity:**
- **Best/Average/Worst:** O(n log n) - guaranteed!
- **Space:** O(n) - needs temporary arrays

** When to use:**
- Need **stable** sort
- Need **guaranteed** O(n log n)
- Sorting linked lists (no random access needed)
- External sorting (large files)

** When NOT to use:**
- Space is limited (O(n) extra space)
- Need in-place sorting

---

### 3. Heap Sort

**Use heap data structure:** Build max heap, repeatedly extract max.

```kotlin
fun heapSort(arr: IntArray) {
    val n = arr.size
    
    // Build max heap
    for (i in n / 2 - 1 downTo 0) {
        heapify(arr, n, i)
    }
    
    // Extract elements from heap
    for (i in n - 1 downTo 1) {
        // Move current root to end
        arr[0] = arr[i].also { arr[i] = arr[0] }
        
        // Heapify reduced heap
        heapify(arr, i, 0)
    }
}

fun heapify(arr: IntArray, n: Int, i: Int) {
    var largest = i
    val left = 2 * i + 1
    val right = 2 * i + 2
    
    // If left child is larger
    if (left < n && arr[left] > arr[largest]) {
        largest = left
    }
    
    // If right child is larger
    if (right < n && arr[right] > arr[largest]) {
        largest = right
    }
    
    // If largest is not root
    if (largest != i) {
        arr[i] = arr[largest].also { arr[largest] = arr[i] }
        heapify(arr, n, largest)
    }
}

// Example:
val arr = intArrayOf(12, 11, 13, 5, 6, 7)
heapSort(arr)
println(arr.contentToString())  // [5, 6, 7, 11, 12, 13]
```

**Complexity:**
- **Best/Average/Worst:** O(n log n) - guaranteed!
- **Space:** O(1) - in-place

** When to use:**
- Need guaranteed O(n log n) with O(1) space
- Partial sorting (find k largest/smallest)
- Priority queue implementation

** When NOT to use:**
- Need stable sort
- Cache efficiency important (poor locality)

---

### 4. Insertion Sort (Simple but Important)

**Build sorted array one element at a time.**

```kotlin
fun insertionSort(arr: IntArray) {
    for (i in 1 until arr.size) {
        val key = arr[i]
        var j = i - 1
        
        // Shift elements greater than key to right
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j]
            j--
        }
        
        arr[j + 1] = key
    }
}

// Example:
val arr = intArrayOf(12, 11, 13, 5, 6)
insertionSort(arr)
println(arr.contentToString())  // [5, 6, 11, 12, 13]
```

**How it works:**
```
[12, 11, 13, 5, 6]
 ↑ sorted

[11, 12, 13, 5, 6]
     ↑ sorted (11 inserted before 12)

[11, 12, 13, 5, 6]
         ↑ sorted (13 already in place)

[5, 11, 12, 13, 6]
             ↑ sorted (5 inserted at start)

[5, 6, 11, 12, 13]
                ↑ sorted (6 inserted)
```

**Complexity:**
- **Best:** O(n) - already sorted!
- **Average/Worst:** O(n²)
- **Space:** O(1)

** When to use:**
- **Small arrays** (< 10-20 elements)
- **Nearly sorted** data (best case O(n))
- **Online** sorting (elements arrive one at a time)
- Used in **Timsort** hybrid algorithm

** When NOT to use:**
- Large arrays
- Random data

---

### 5. Counting Sort (Non-Comparison)

**Count occurrences, then reconstruct sorted array.**

```kotlin
fun countingSort(arr: IntArray): IntArray {
    if (arr.isEmpty()) return arr
    
    val max = arr.maxOrNull()!!
    val min = arr.minOrNull()!!
    val range = max - min + 1
    
    // Count occurrences
    val count = IntArray(range)
    for (num in arr) {
        count[num - min]++
    }
    
    // Cumulative count
    for (i in 1 until count.size) {
        count[i] += count[i - 1]
    }
    
    // Build output array
    val output = IntArray(arr.size)
    for (i in arr.indices.reversed()) {
        val num = arr[i]
        output[count[num - min] - 1] = num
        count[num - min]--
    }
    
    return output
}

// Example:
val arr = intArrayOf(4, 2, 2, 8, 3, 3, 1)
val sorted = countingSort(arr)
println(sorted.contentToString())  // [1, 2, 2, 3, 3, 4, 8]
```

**Complexity:**
- **Time:** O(n + k) where k = range of values
- **Space:** O(k)

** When to use:**
- **Small range** of integers (k ≈ n)
- Positive integers only
- Need **stable** sort
- **Linear time** possible

** When NOT to use:**
- Large range (k >> n)
- Floating point numbers
- Objects (use comparison-based)

---

### 6. Radix Sort (Non-Comparison)

**Sort by individual digits/characters.**

```kotlin
fun radixSort(arr: IntArray) {
    val max = arr.maxOrNull() ?: return
    
    // Sort by each digit
    var exp = 1
    while (max / exp > 0) {
        countingSortByDigit(arr, exp)
        exp *= 10
    }
}

fun countingSortByDigit(arr: IntArray, exp: Int) {
    val output = IntArray(arr.size)
    val count = IntArray(10)
    
    // Count occurrences
    for (num in arr) {
        val digit = (num / exp) % 10
        count[digit]++
    }
    
    // Cumulative count
    for (i in 1..9) {
        count[i] += count[i - 1]
    }
    
    // Build output
    for (i in arr.indices.reversed()) {
        val digit = (arr[i] / exp) % 10
        output[count[digit] - 1] = arr[i]
        count[digit]--
    }
    
    // Copy back
    arr.indices.forEach { arr[it] = output[it] }
}

// Example:
val arr = intArrayOf(170, 45, 75, 90, 802, 24, 2, 66)
radixSort(arr)
println(arr.contentToString())  // [2, 24, 45, 66, 75, 90, 170, 802]
```

**Complexity:**
- **Time:** O(nk) where k = number of digits
- **Space:** O(n + k)

** When to use:**
- Fixed-length integers
- Strings of same length
- Need stable sort

---

### Language Built-in Sorts

**Kotlin/Java:**
```kotlin
// Arrays.sort() - uses Dual-Pivot QuickSort (primitives)
val arr = intArrayOf(5, 2, 8, 1, 9)
arr.sort()

// Collections.sort() - uses TimSort (objects)
val list = mutableListOf(5, 2, 8, 1, 9)
list.sort()

// Sorted (immutable)
val sorted = listOf(5, 2, 8, 1, 9).sorted()

// Custom comparator
data class Person(val name: String, val age: Int)
val people = listOf(Person("Alice", 30), Person("Bob", 25))
people.sortedBy { it.age }
```

**TimSort (Python/Java default):**
- Hybrid: Merge Sort + Insertion Sort
- Optimized for real-world data
- Best: O(n), Worst: O(n log n)
- Stable

---

### Decision Tree

```
Need to sort?

 Small array (< 20)?
   Insertion Sort (O(n²) but fast constant)

 Nearly sorted?
   Insertion Sort (O(n) best case)

 Need stable?
   Need guaranteed O(n log n)?
     Merge Sort
   Average case OK?
      TimSort (built-in)

 Integers with small range?
   Counting Sort (O(n + k))

 Limited space?
   Heap Sort (O(1) space, O(n log n) time)

 General purpose?
    Quick Sort (average O(n log n), in-place)
```

---

### Real-World Usage

```kotlin
// Android: Sorting a list of items
data class Product(val name: String, val price: Double, val rating: Float)

val products = listOf(
    Product("Laptop", 999.99, 4.5f),
    Product("Mouse", 29.99, 4.8f),
    Product("Keyboard", 79.99, 4.3f)
)

// Sort by price
val byPrice = products.sortedBy { it.price }

// Sort by multiple fields
val byRatingThenPrice = products
    .sortedWith(compareByDescending<Product> { it.rating }
        .thenBy { it.price })

// Custom comparator
val custom = products.sortedWith { a, b ->
    when {
        a.rating != b.rating -> b.rating.compareTo(a.rating)
        else -> a.price.compareTo(b.price)
    }
}
```

---

### Key Takeaways

1. **Quick Sort** - Default choice, O(n log n) average, in-place
2. **Merge Sort** - Stable, guaranteed O(n log n), uses O(n) space
3. **Heap Sort** - Guaranteed O(n log n), O(1) space, not stable
4. **Insertion Sort** - Best for small/nearly-sorted arrays
5. **Counting Sort** - O(n) for small integer ranges
6. **Radix Sort** - O(nk) for fixed-length integers/strings
7. **Built-in sorts** use hybrid algorithms (TimSort, Dual-Pivot QuickSort)
8. **Stable** = preserves order of equal elements
9. **In-place** = O(1) extra space
10. **Choose based on:** data characteristics, space constraints, stability needs

---

## Russian Version

### Постановка задачи

Сортировка - одна из самых фундаментальных операций в информатике. Понимание различных алгоритмов сортировки, их временной/пространственной сложности и когда использовать каждый - необходимо для технических интервью.

**Вопрос:** Каковы основные алгоритмы сортировки? Сравните их временную/пространственную сложность и когда следует использовать каждый алгоритм?

### Детальный ответ

#### Таблица сравнения

| Алгоритм | Лучший | Средний | Худший | Память | Стабильный |
|----------|--------|---------|--------|--------|------------|
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) |  Нет |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) |  Да |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) |  Нет |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) |  Да |

### Ключевые выводы

1. **Quick Sort** - Выбор по умолчанию, O(n log n) в среднем
2. **Merge Sort** - Стабильный, гарантированный O(n log n)
3. **Heap Sort** - Гарантированный O(n log n), O(1) память
4. **Insertion Sort** - Лучше для малых/почти отсортированных массивов
5. **Counting Sort** - O(n) для малого диапазона целых чисел
6. **Встроенные сортировки** используют гибридные алгоритмы
7. **Стабильный** = сохраняет порядок равных элементов
8. **Выбирайте исходя из:** характеристик данных, ограничений памяти

## Follow-ups

1. What is the difference between stable and unstable sorting?
2. Why is QuickSort preferred over MergeSort in practice?
3. How does TimSort work (Python's default sorting)?
4. What is the lower bound for comparison-based sorting?
5. How do you implement QuickSort iteratively (without recursion)?
6. What is 3-way QuickSort and when is it useful?
7. How do you sort a linked list efficiently?
8. What is external sorting for large files?
9. How do you find the kth largest element without full sorting?
10. What is the Dutch National Flag problem?

---

## Related Questions

### Android Implementation
- [[q-compose-canvas-graphics--jetpack-compose--hard]] - Data Structures
- [[q-cache-implementation-strategies--android--medium]] - Data Structures
- [[q-graphql-vs-rest--networking--easy]] - Data Structures
- [[q-recomposition-choreographer--android--hard]] - Data Structures
- [[q-android-security-practices-checklist--android--medium]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--medium]] - Data Structures

### System Design Concepts
- [[q-message-queues-event-driven--system-design--medium]] - Data Structures
