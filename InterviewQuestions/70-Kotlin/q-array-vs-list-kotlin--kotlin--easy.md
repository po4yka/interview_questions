---
id: "20251015082236040"
title: "Array Vs List Kotlin"
topic: kotlin
difficulty: easy
status: draft
created: 2025-10-13
tags: - kotlin
  - collections
  - data-structures
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-kotlin
related_questions:   - q-list-vs-sequence--kotlin--medium.md
subtopics: [collections, data-structures, array, list]
---
# What is the difference between array and list in Kotlin?

# Вопрос (RU)
> Чем array отличается от list

## Answer (EN)

Arrays and lists are data structures for storing collections of elements.

### Key Differences

#### 1. Size

**Array**: Has a fixed size after creation.

```kotlin
val array = arrayOf(1, 2, 3, 4, 5)
// array.size = 5, cannot be changed
```

**List**: Dynamic, can change its size automatically when adding or removing elements.

```kotlin
val mutableList = mutableListOf(1, 2, 3)
mutableList.add(4)      // Size becomes 4
mutableList.removeAt(0) // Size becomes 3
```

#### 2. Typing

**Array**: Can be of a primitive or object type. In Kotlin, arrays are always objects, but there are special types for primitives.

```kotlin
val intArray: IntArray = intArrayOf(1, 2, 3)      // Primitive int[]
val objectArray: Array<Int> = arrayOf(1, 2, 3) // Object Integer[]
```

**List**: Always contains objects and is generic.

```kotlin
val list: List<Int> = listOf(1, 2, 3) // Always an object
```

#### 3. Functionality

**Array**: Has basic operations.

```kotlin
val array = arrayOf(1, 2, 3)
array[0] = 10 // Modifying an element
val size = array.size
```

**List**: Provides a rich set of methods for working with elements.

```kotlin
val list = listOf(1, 2, 3, 4, 5)
val filtered = list.filter { it > 2 }  // [3, 4, 5]
val mapped = list.map { it * 2 }      // [2, 4, 6, 8, 10]
val sum = list.sum()                  // 15
val contains = list.contains(3)       // true
```

#### 4. Performance

**Array**: Faster for direct access to elements by index.

```kotlin
val array = IntArray(1000000)
array[500000] = 42  // O(1) - very fast
```

**List**: Can be less efficient due to dynamic resizing, but more convenient for management.

```kotlin
val list = MutableList(1000000) { 0 }
list.add(42)  // May require memory reallocation
```

#### 5. Use Cases

```kotlin
// Array - fixed size
val daysOfWeek = arrayOf("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

// List - dynamic size
val shoppingList = mutableListOf("Bread", "Milk")
shoppingList.add("Eggs")
shoppingList.remove("Milk")
```

### When to Use

**Array**:
- Known fixed size
- High performance for element access
- Working with primitive types (IntArray, ByteArray, etc.)
- Interop with Java code

**List**:
- Dynamic change in the number of elements
- Use of functional operations (map, filter, reduce)
- More readable and idiomatic Kotlin code

**Summary**: Arrays have a fixed size and better performance for direct access. Lists are dynamic, provide rich functional operations (map, filter, etc.), and are more flexible for collection management. Arrays are faster but less convenient than Lists.

## Ответ (RU)
Массивы и списки представляют собой структуры данных для хранения наборов элементов.

### Основные различия

#### 1. Размер

**Array**: Имеет фиксированный размер после создания.

```kotlin
val array = arrayOf(1, 2, 3, 4, 5)
// array.size = 5, изменить нельзя
```

**List**: Динамический, может изменять свой размер автоматически при добавлении или удалении элементов.

```kotlin
val mutableList = mutableListOf(1, 2, 3)
mutableList.add(4)  // Размер стал 4
mutableList.removeAt(0)  // Размер стал 3
```

#### 2. Типизация

**Array**: Может быть как примитивным типом, так и объектным. В Kotlin массивы всегда объектные, но есть специальные типы для примитивов.

```kotlin
val intArray: IntArray = intArrayOf(1, 2, 3)  // Примитивный int[]
val objectArray: Array<Int> = arrayOf(1, 2, 3)  // Объектный Integer[]
```

**List**: Всегда содержит объекты и обобщён (generic).

```kotlin
val list: List<Int> = listOf(1, 2, 3)  // Всегда объектный
```

#### 3. Функциональность

**Array**: Имеет базовые операции.

```kotlin
val array = arrayOf(1, 2, 3)
array[0] = 10  // Изменение элемента
val size = array.size
```

**List**: Предоставляет богатый набор методов для работы с элементами.

```kotlin
val list = listOf(1, 2, 3, 4, 5)
val filtered = list.filter { it > 2 }  // [3, 4, 5]
val mapped = list.map { it * 2 }  // [2, 4, 6, 8, 10]
val sum = list.sum()  // 15
val contains = list.contains(3)  // true
```

#### 4. Производительность

**Array**: Быстрее для непосредственного доступа к элементам по индексу.

```kotlin
val array = IntArray(1000000)
array[500000] = 42  // O(1) - очень быстро
```

**List**: Может быть менее эффективен из-за динамического изменения размера, но удобнее для управления.

```kotlin
val list = MutableList(1000000) { 0 }
list.add(42)  // Может потребовать перевыделения памяти
```

#### 5. Примеры использования

```kotlin
// Array - фиксированный размер
val daysOfWeek = arrayOf("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

// List - динамический размер
val shoppingList = mutableListOf("Хлеб", "Молоко")
shoppingList.add("Яйца")
shoppingList.remove("Молоко")
```

### Когда использовать

**Array**:
- Известный фиксированный размер
- Высокая производительность доступа к элементам
- Работа с примитивными типами (IntArray, ByteArray и т.д.)
- Interop с Java кодом

**List**:
- Динамическое изменение количества элементов
- Использование функциональных операций (map, filter, reduce)
- Более читаемый и идиоматичный Kotlin код

**Краткое содержание**: Массивы имеют фиксированный размер и лучшую производительность для прямого доступа. Списки динамичны, предоставляют богатые функциональные операции (map, filter и т.д.) и более гибки для управления коллекциями. Массивы быстрее, но менее удобны, чем списки.
