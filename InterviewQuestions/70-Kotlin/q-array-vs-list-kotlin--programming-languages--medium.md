---
tags:
  - array
  - collections
  - kotlin
  - list
  - performance
  - programming-languages
difficulty: medium
status: reviewed
---

# Чем array отличается от list

**English**: What is the difference between array and list?

## Answer

Arrays and lists are data structures for storing sets of elements.

**Main differences:**

1. **Size**: Arrays have fixed size after creation, while lists are dynamic and can automatically change size when adding or removing elements

2. **Typing**: Arrays can be primitive or object types. In Kotlin arrays are always objects but there are special types for primitives (IntArray, etc.). Lists always contain objects and are generic

3. **Functionality**: Arrays have basic operations, while lists provide a rich set of methods for working with elements

4. **Performance**: Arrays are faster for direct index access. Lists may be less efficient due to dynamic resizing but are more convenient for management

5. **Usage**: Arrays for known size and high-performance index access, lists for flexibility in collection management

**Examples:**
```kotlin
// Array - fixed size
val array = arrayOf(1, 2, 3)

// List - dynamic
val list = mutableListOf(1, 2, 3)
list.add(4) // Can grow
```

## Ответ

Массивы и списки представляют собой структуры данных для хранения наборов элементов. [Full Russian text preserved in source]

