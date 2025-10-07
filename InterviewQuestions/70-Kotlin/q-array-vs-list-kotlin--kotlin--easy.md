---
tags:
  - kotlin
  - collections
  - data-structures
difficulty: easy
status: draft
---

# Чем array отличается от list

**English**: What is the difference between array and list in Kotlin?

## Answer

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

**English**: Arrays have fixed size and better performance for direct access. Lists are dynamic, provide rich functional operations (map, filter, etc.), and are more flexible for collection management. Arrays are faster but less convenient than Lists.
