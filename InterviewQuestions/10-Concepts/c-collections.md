---
id: concept-006
title: Collections / Коллекции
aliases: [Collection Framework, Collections, Java Collections, Kotlin Collections, Коллекции]
kind: concept
summary: Data structures for storing and manipulating groups of objects, including List, Set, Map, and their implementations in Java and Kotlin.
links: []
created: 2025-11-05
updated: 2025-11-05
tags: [collections, concept, data-structures, java, kotlin]
date created: Wednesday, November 5th 2025, 6:30:35 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

**Collections** are data structures that hold and manipulate groups of objects. Both Java and Kotlin provide rich collection frameworks with different interfaces and implementations optimized for various use cases.

**Core Collection Interfaces**:

**1. List** (Ordered, allows duplicates):
- **ArrayList**: Dynamic array, fast random access O(1), slow insertion/deletion O(n)
- **LinkedList**: Doubly-linked list, fast insertion/deletion O(1), slow random access O(n)
- Use case: Maintain insertion order, allow duplicates

**2. Set** (Unordered, unique elements):
- **HashSet**: Hash table-based, O(1) add/contains/remove, no ordering guarantees
- **LinkedHashSet**: Hash table + linked list, maintains insertion order
- **TreeSet**: Red-black tree, O(log n) operations, sorted order
- Use case: Enforce uniqueness, fast membership testing

**3. Map** (Key-value pairs):
- **HashMap**: Hash table, O(1) get/put, no ordering guarantees
- **LinkedHashMap**: Hash table + linked list, maintains insertion order
- **TreeMap**: Red-black tree, O(log n) operations, sorted by keys
- Use case: Associate keys with values, fast lookup by key

**4. Queue/Deque**:
- **ArrayDeque**: Resizable array, double-ended queue
- **PriorityQueue**: Heap-based, elements retrieved in priority order
- Use case: FIFO/LIFO operations, priority-based processing

**Kotlin-Specific Features**:

**Immutable vs Mutable**:
- **Read-only**: `List<T>`, `Set<T>`, `Map<K,V>` (no add/remove methods)
- **Mutable**: `MutableList<T>`, `MutableSet<T>`, `MutableMap<K,V>`
- Immutability enforced at compile time via interfaces

**Collection Operators**:
- `map`, `filter`, `reduce`, `fold`, `groupBy`, `partition`
- `any`, `all`, `none`, `first`, `last`, `single`
- Chainable, functional-style operations

**Creation**:
```kotlin
// Read-only
val list = listOf(1, 2, 3)
val set = setOf("a", "b", "c")
val map = mapOf("key" to "value")

// Mutable
val mutableList = mutableListOf(1, 2, 3)
val mutableSet = mutableSetOf("a", "b", "c")
val mutableMap = mutableMapOf("key" to "value")
```

# Сводка (RU)

**Коллекции** — это структуры данных для хранения и манипуляции группами объектов. Java и Kotlin предоставляют богатые фреймворки коллекций с различными интерфейсами и реализациями, оптимизированными под разные сценарии использования.

**Основные интерфейсы коллекций**:

**1. List** (Упорядоченный, допускает дубликаты):
- **ArrayList**: Динамический массив, быстрый произвольный доступ O(1), медленная вставка/удаление O(n)
- **LinkedList**: Двусвязный список, быстрая вставка/удаление O(1), медленный произвольный доступ O(n)
- Применение: Сохранение порядка вставки, разрешение дубликатов

**2. Set** (Неупорядоченный, уникальные элементы):
- **HashSet**: На основе хеш-таблицы, O(1) добавление/проверка/удаление, без гарантии порядка
- **LinkedHashSet**: Хеш-таблица + связный список, сохраняет порядок вставки
- **TreeSet**: Красно-чёрное дерево, O(log n) операции, отсортированный порядок
- Применение: Обеспечение уникальности, быстрая проверка принадлежности

**3. Map** (Пары ключ-значение):
- **HashMap**: Хеш-таблица, O(1) get/put, без гарантии порядка
- **LinkedHashMap**: Хеш-таблица + связный список, сохраняет порядок вставки
- **TreeMap**: Красно-чёрное дерево, O(log n) операции, сортировка по ключам
- Применение: Связывание ключей со значениями, быстрый поиск по ключу

**4. Queue/Deque**:
- **ArrayDeque**: Изменяемый массив, двусторонняя очередь
- **PriorityQueue**: На основе кучи, элементы извлекаются в порядке приоритета
- Применение: FIFO/LIFO операции, обработка по приоритету

**Особенности Kotlin**:

**Неизменяемые vs Изменяемые**:
- **Только для чтения**: `List<T>`, `Set<T>`, `Map<K,V>` (нет методов add/remove)
- **Изменяемые**: `MutableList<T>`, `MutableSet<T>`, `MutableMap<K,V>`
- Неизменяемость обеспечивается на этапе компиляции через интерфейсы

**Операторы коллекций**:
- `map`, `filter`, `reduce`, `fold`, `groupBy`, `partition`
- `any`, `all`, `none`, `first`, `last`, `single`
- Цепочечные операции в функциональном стиле

**Создание**:
```kotlin
// Только для чтения
val list = listOf(1, 2, 3)
val set = setOf("a", "b", "c")
val map = mapOf("key" to "value")

// Изменяемые
val mutableList = mutableListOf(1, 2, 3)
val mutableSet = mutableSetOf("a", "b", "c")
val mutableMap = mutableMapOf("key" to "value")
```

## Use Cases / Trade-offs

**Choosing the right collection**:

**List vs Set vs Map**:
- Need order and duplicates? → `List`
- Need uniqueness, no duplicates? → `Set`
- Need key-value associations? → `Map`

**ArrayList vs LinkedList**:
- Frequent random access (index-based)? → `ArrayList`
- Frequent insertions/deletions at beginning/middle? → `LinkedList`
- Modern advice: Almost always use `ArrayList` (better cache locality)

**HashSet vs TreeSet**:
- Need sorted order? → `TreeSet`
- Just need uniqueness and fast operations? → `HashSet`
- Need insertion order? → `LinkedHashSet`

**HashMap vs TreeMap**:
- Need sorted keys? → `TreeMap`
- Just need fast key-value lookup? → `HashMap`
- Need insertion order? → `LinkedHashMap`

**Immutable vs Mutable (Kotlin)**:
- Default to read-only collections for safety
- Use mutable only when modification is required
- Read-only collections can still be backed by mutable collections (not true immutability)

**Performance considerations**:
- **ArrayList**: O(1) get, O(n) add/remove (if resizing or shifting needed)
- **LinkedList**: O(1) add/remove at ends, O(n) get by index
- **HashSet/HashMap**: O(1) average, O(n) worst case (hash collisions)
- **TreeSet/TreeMap**: O(log n) for all operations

**Thread safety**:
- Standard collections are NOT thread-safe
- Use `Collections.synchronizedList/Set/Map()` for thread-safety (Java)
- Or use concurrent collections: `ConcurrentHashMap`, `CopyOnWriteArrayList`

## References

- [Java Collections Framework Overview](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/doc-files/coll-overview.html)
- [Kotlin Collections Overview](https://kotlinlang.org/docs/collections-overview.html)
- [Effective Java, Chapter 9: Collections](https://www.oreilly.com/library/view/effective-java/9780134686097/)
- [Java Collection Performance](https://www.baeldung.com/java-collections-complexity)
- [Kotlin Collection Operations](https://kotlinlang.org/docs/collection-operations.html)
