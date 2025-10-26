---
id: "20251018-140002"
title: "Array / Массив"
aliases: ["Array", "Arrays", "Массив", "Массивы", "Fixed-size Array", "Фиксированный массив"]
summary: "Fixed-size sequential collection with contiguous memory and O(1) random access"
topic: "data-structures"
subtopics: ["arrays", "algorithms", "collections"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-algorithms"
related: []
created: "2025-10-18"
updated: "2025-10-18"
tags: ["concept", "data-structures", "arrays", "algorithms", "collections"]
---

# Summary (EN)

An **array** is a fundamental data structure that stores a fixed-size sequential collection of elements of the same type in contiguous memory locations. Arrays provide O(1) random access to elements via indices, making them efficient for read operations but inflexible for dynamic resizing.

Arrays are one of the most basic and widely-used data structures in computer science, serving as the foundation for many other data structures and algorithms.

# Краткое описание (RU)

**Массив** - это фундаментальная структура данных, которая хранит коллекцию элементов фиксированного размера одного типа в последовательных ячейках памяти. Массивы обеспечивают O(1) доступ к элементам по индексу, что делает их эффективными для операций чтения, но негибкими для динамического изменения размера.

Массивы являются одной из самых базовых и широко используемых структур данных в информатике, служащих основой для многих других структур данных и алгоритмов.

---

## Characteristics / Характеристики

### Key Properties (EN)

1. **Fixed Size**: Once created, the size cannot be changed
2. **Contiguous Memory**: Elements are stored in consecutive memory locations
3. **Indexed Access**: Elements accessed via zero-based indices (0, 1, 2, ...)
4. **Homogeneous**: All elements must be of the same type
5. **Random Access**: Direct access to any element in O(1) time
6. **Memory Efficient**: No overhead for pointers or metadata per element

### Основные свойства (RU)

1. **Фиксированный размер**: После создания размер не может быть изменён
2. **Последовательная память**: Элементы хранятся в последовательных ячейках памяти
3. **Индексированный доступ**: Доступ к элементам через индексы (0, 1, 2, ...)
4. **Однородность**: Все элементы должны быть одного типа
5. **Произвольный доступ**: Прямой доступ к любому элементу за O(1)
6. **Эффективность памяти**: Нет накладных расходов на указатели для каждого элемента

---

## Memory Layout / Размещение в памяти

### Contiguous Memory (EN)

Arrays store elements in consecutive memory locations, which allows for efficient cache utilization and predictable memory access patterns.

```
Memory Address:  1000   1004   1008   1012   1016
Array Index:      [0]    [1]    [2]    [3]    [4]
Values:           42     17     89     33     56
```

For an array starting at address `base`, the element at index `i` is located at:
```
address = base + (i × element_size)
```

This formula enables O(1) access to any element.

### Последовательное размещение (RU)

Массивы хранят элементы в последовательных ячейках памяти, что обеспечивает эффективное использование кэша и предсказуемые паттерны доступа к памяти.

Для массива, начинающегося с адреса `base`, элемент с индексом `i` находится по адресу:
```
адрес = base + (i × размер_элемента)
```

Эта формула обеспечивает O(1) доступ к любому элементу.

---

## Time Complexity / Временная сложность

| Operation | Time Complexity | Explanation |
|-----------|----------------|-------------|
| **Access by index** | O(1) | Direct calculation of memory address |
| **Search (unsorted)** | O(n) | Must check each element |
| **Search (sorted)** | O(log n) | Binary search possible |
| **Insert at end** | O(1)* | If space available |
| **Insert at position** | O(n) | Must shift elements |
| **Delete at end** | O(1) | Just decrement logical size |
| **Delete at position** | O(n) | Must shift elements |

*Note: For dynamic arrays (ArrayList), insert at end is O(1) amortized, but O(n) in worst case when resizing occurs.

| Операция | Сложность | Пояснение |
|----------|-----------|-----------|
| **Доступ по индексу** | O(1) | Прямое вычисление адреса в памяти |
| **Поиск (неотсортированный)** | O(n) | Необходимо проверить каждый элемент |
| **Поиск (отсортированный)** | O(log n) | Возможен бинарный поиск |
| **Вставка в конец** | O(1)* | Если есть свободное место |
| **Вставка в позицию** | O(n) | Необходимо сдвинуть элементы |
| **Удаление из конца** | O(1) | Просто уменьшаем логический размер |
| **Удаление из позиции** | O(n) | Необходимо сдвинуть элементы |

---

## Arrays vs Lists vs ArrayList

### Comparison Table (EN)

| Feature | Array | List (Interface) | ArrayList |
|---------|-------|-----------------|-----------|
| **Size** | Fixed | Fixed (immutable) or Dynamic (mutable) | Dynamic |
| **Memory** | Contiguous | Implementation-dependent | Contiguous (backed by array) |
| **Access Time** | O(1) | O(1) | O(1) |
| **Insert/Delete** | O(n) (requires shifting) | Depends on implementation | O(n) average |
| **Resizing** | Not possible | Mutable lists only | Automatic (O(n) when occurs) |
| **Type Safety** | Reified type (can be primitive) | Generic (erased) | Generic (erased) |
| **Primitives** | IntArray, ByteArray, etc. | Always boxed objects | Always boxed objects |
| **Null Safety** | Can contain nulls | Can be List<T?> or List<T> | Can contain nulls |
| **Methods** | Basic (size, get, set) | Rich API (filter, map, etc.) | Rich API + mutability |

### Таблица сравнения (RU)

| Характеристика | Array | List (интерфейс) | ArrayList |
|----------------|-------|------------------|-----------|
| **Размер** | Фиксированный | Фиксированный или динамический | Динамический |
| **Память** | Последовательная | Зависит от реализации | Последовательная (на основе массива) |
| **Время доступа** | O(1) | O(1) | O(1) |
| **Вставка/удаление** | O(n) (требуется сдвиг) | Зависит от реализации | O(n) в среднем |
| **Изменение размера** | Невозможно | Только mutable списки | Автоматическое (O(n) при расширении) |
| **Безопасность типов** | Реифицированный тип (может быть примитивом) | Generic (стёртый) | Generic (стёртый) |
| **Примитивы** | IntArray, ByteArray и т.д. | Всегда упакованные объекты | Всегда упакованные объекты |

---

## When to Use Arrays / Когда использовать массивы

### Use Arrays When (EN):

1. **Size is known and fixed** - Number of elements won't change
   ```kotlin
   val daysInWeek = 7
   val weekDays = arrayOf("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
   ```

2. **Performance-critical with primitives** - Avoid boxing overhead
   ```kotlin
   val pixels = IntArray(1920 * 1080)  // Image buffer - no boxing
   ```

3. **Memory constraints** - Need minimal memory overhead
   ```kotlin
   val coefficients = DoubleArray(1000)  // Scientific computing
   ```

4. **Java interoperability** - Working with Java APIs
   ```kotlin
   val javaArray: Array<String> = arrayOf("a", "b", "c")
   javaMethod(javaArray)  // Java expects T[]
   ```

5. **Multi-dimensional data** - Matrices and grids
   ```kotlin
   val matrix = Array(3) { IntArray(3) }  // 3x3 matrix
   ```

### Используйте массивы когда (RU):

1. **Размер известен и фиксирован** - Количество элементов не изменится
2. **Критична производительность с примитивами** - Избежать накладных расходов на упаковку
3. **Ограничения по памяти** - Нужны минимальные накладные расходы
4. **Совместимость с Java** - Работа с Java API
5. **Многомерные данные** - Матрицы и сетки

### Use Lists/ArrayList When (EN):

1. **Size is dynamic** - Elements will be added/removed
2. **Functional operations needed** - map, filter, reduce
3. **Idiomatic Kotlin code** - Better readability
4. **Don't need primitive performance** - Boxed types acceptable

---

## Kotlin/Java Array Types

### Kotlin Array Types (EN)

```kotlin
// Generic array (uses boxed types)
val array: Array<Int> = arrayOf(1, 2, 3)
// Compiled to: Integer[] in Java

// Primitive arrays (no boxing overhead)
val intArray: IntArray = intArrayOf(1, 2, 3)        // int[]
val byteArray: ByteArray = byteArrayOf(1, 2, 3)     // byte[]
val longArray: LongArray = longArrayOf(1L, 2L, 3L)  // long[]
val floatArray: FloatArray = floatArrayOf(1f, 2f)   // float[]
val doubleArray: DoubleArray = doubleArrayOf(1.0)   // double[]
val booleanArray: BooleanArray = booleanArrayOf(true, false)  // boolean[]
val charArray: CharArray = charArrayOf('a', 'b')    // char[]

// Array creation with size
val zeros = IntArray(10)  // [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
val initialized = IntArray(5) { it * 2 }  // [0, 2, 4, 6, 8]

// Multi-dimensional arrays
val matrix = Array(3) { IntArray(3) }  // 3x3 matrix
```

### Типы массивов в Kotlin (RU)

```kotlin
// Обобщённый массив (использует упакованные типы)
val array: Array<Int> = arrayOf(1, 2, 3)
// Компилируется в: Integer[] в Java

// Примитивные массивы (без упаковки)
val intArray: IntArray = intArrayOf(1, 2, 3)  // int[]
val byteArray: ByteArray = byteArrayOf(1, 2, 3)  // byte[]
// ... и т.д.
```

---

## Common Operations / Основные операции

### Kotlin Examples (EN)

```kotlin
// Creation
val array = intArrayOf(1, 2, 3, 4, 5)
val nullableArray = arrayOfNulls<String>(5)  // [null, null, null, null, null]

// Access
val first = array[0]  // 1
val last = array[array.size - 1]  // 5
val lastSafe = array.last()  // 5

// Modification
array[0] = 10  // [10, 2, 3, 4, 5]

// Iteration
for (element in array) {
    println(element)
}

for ((index, value) in array.withIndex()) {
    println("array[$index] = $value")
}

array.forEach { println(it) }
array.forEachIndexed { index, value ->
    println("array[$index] = $value")
}

// Common operations
val size = array.size
val isEmpty = array.isEmpty()
val contains = array.contains(3)  // true
val indexOf = array.indexOf(3)  // 2

// Transformation
val doubled = array.map { it * 2 }  // Returns List<Int>
val filtered = array.filter { it > 2 }  // Returns List<Int>
val sum = array.sum()  // 20

// Sorting
array.sort()  // In-place sort
val sorted = array.sorted()  // Returns List<Int>
val sortedArray = array.sortedArray()  // Returns new IntArray

// Copying
val copy = array.copyOf()  // Full copy
val partial = array.copyOfRange(1, 4)  // [2, 3, 4]

// Conversion
val list = array.toList()
val set = array.toSet()
val mutableList = array.toMutableList()
```

### Java Examples

```java
// Creation
int[] array = new int[5];  // [0, 0, 0, 0, 0]
int[] array2 = {1, 2, 3, 4, 5};
String[] strings = new String[3];

// Access
int first = array[0];
int last = array[array.length - 1];

// Modification
array[0] = 10;

// Iteration
for (int i = 0; i < array.length; i++) {
    System.out.println(array[i]);
}

for (int value : array) {
    System.out.println(value);
}

// Utilities
Arrays.sort(array);  // In-place sort
int[] copy = Arrays.copyOf(array, array.length);
boolean contains = Arrays.asList(array).contains(3);
String str = Arrays.toString(array);  // "[1, 2, 3, 4, 5]"
```

---

## Advanced Topics / Продвинутые темы

### Array Resizing (Dynamic Arrays)

Since arrays have fixed size, dynamic resizing requires creating a new array and copying elements:

```kotlin
fun resizeArray(array: IntArray, newSize: Int): IntArray {
    val newArray = IntArray(newSize)
    val copySize = minOf(array.size, newSize)

    for (i in 0 until copySize) {
        newArray[i] = array[i]
    }

    return newArray
}

// Or using standard library
val resized = array.copyOf(newSize)
```

This is how `ArrayList` works internally - it maintains an internal array and creates a larger one (typically 1.5x or 2x) when needed.

### Two-Dimensional Arrays

```kotlin
// Creating 2D array
val matrix = Array(3) { IntArray(3) }  // 3x3 matrix

// Initialization with values
val matrix2 = Array(3) { row ->
    IntArray(3) { col ->
        row * 3 + col  // [[0,1,2], [3,4,5], [6,7,8]]
    }
}

// Access
matrix[0][0] = 1
val value = matrix[1][2]

// Iteration
for (row in matrix) {
    for (value in row) {
        print("$value ")
    }
    println()
}
```

### Jagged Arrays (Arrays of Arrays)

```kotlin
// Arrays with different lengths
val jagged = arrayOf(
    intArrayOf(1, 2),
    intArrayOf(3, 4, 5),
    intArrayOf(6)
)

// Access
val element = jagged[1][2]  // 5
```

---

## Common Pitfalls / Распространённые ошибки

### 1. Array Comparison (EN)

Arrays don't override `equals()`, so use `contentEquals()`:

```kotlin
val a = intArrayOf(1, 2, 3)
val b = intArrayOf(1, 2, 3)

println(a == b)  // false - reference comparison!
println(a.contentEquals(b))  // true - value comparison
```

### 2. Array Covariance

Arrays in Java are covariant, which can lead to runtime errors:

```java
// Java code - dangerous!
Object[] objects = new String[10];
objects[0] = 42;  // ArrayStoreException at runtime!
```

Kotlin's generic arrays are invariant to prevent this.

### 3. IndexOutOfBounds

```kotlin
val array = intArrayOf(1, 2, 3)
val value = array[5]  // ArrayIndexOutOfBoundsException!

// Safe alternatives
val safeSample = array.getOrNull(5)  // null
val safeWithDefault = array.getOrElse(5) { 0 }  // 0
```

---

## Performance Characteristics

### Space Complexity
- **Array**: O(n) - exactly n elements
- **ArrayList**: O(n) - capacity ≥ size, typically ~1.5x allocated

### Cache Performance
Arrays have excellent cache locality due to contiguous memory, making them faster than linked structures for sequential access.

### Memory Overhead
- **Primitive Array** (IntArray): 16 bytes (object header) + 4 bytes/element
- **Object Array** (Array<Int>): 16 bytes + 8 bytes/reference + object overhead per element
- **ArrayList**: Additional overhead for capacity management

---

## Use Cases / Примеры использования

### Algorithm Problems (EN)
```kotlin
// Two pointers technique
fun twoSum(nums: IntArray, target: Int): IntArray {
    var left = 0
    var right = nums.size - 1

    while (left < right) {
        val sum = nums[left] + nums[right]
        when {
            sum == target -> return intArrayOf(left, right)
            sum < target -> left++
            else -> right--
        }
    }

    return intArrayOf(-1, -1)
}
```

### Image Processing
```kotlin
// RGB pixel buffer
val width = 1920
val height = 1080
val pixels = IntArray(width * height)  // ARGB format

// Access pixel at (x, y)
fun getPixel(x: Int, y: Int): Int {
    return pixels[y * width + x]
}
```

### Fixed-Size Buffers
```kotlin
// Circular buffer for streaming data
class CircularBuffer(size: Int) {
    private val buffer = IntArray(size)
    private var writePos = 0

    fun write(value: Int) {
        buffer[writePos] = value
        writePos = (writePos + 1) % buffer.size
    }
}
```

---

## Related Questions

### Prerequisites (Easy)
- [[q-data-structures-overview--algorithms--easy]] - Overview of all data structures
- [[q-array-vs-list-kotlin--kotlin--easy]] - Array vs List comparison in Kotlin

### Related (Medium)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Common array algorithms
- [[q-arraylist-linkedlist-vector-difference--programming-languages--medium]] - List implementations
- [[q-kotlin-collections--kotlin--medium]] - Kotlin collections overview

### Advanced (Hard)
- [[q-binary-search-variants--algorithms--medium]] - Binary search on arrays
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Array sorting algorithms
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP with arrays

---

## References

### Documentation
- [Kotlin Arrays Documentation](https://kotlinlang.org/docs/arrays.html)
- [Java Arrays Tutorial](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/arrays.html)
- [Arrays in Data Structures](https://en.wikipedia.org/wiki/Array_data_structure)

### Books
- "Introduction to Algorithms" (CLRS) - Chapter 2: Getting Started
- "Effective Java" (Joshua Bloch) - Item 28: Prefer lists to arrays

### Related Concepts
- [[c-hash-map]] - Hash tables (often implemented with arrays)
- [[c-data-structures]] - General data structures overview
- [[c-algorithms]] - Algorithm fundamentals
- [[moc-algorithms]] - Algorithms Map of Content
