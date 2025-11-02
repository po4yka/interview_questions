---
id: kotlin-202
title: "Collection Implementations / Реализации коллекций"
aliases: [Collection Implementations, Реализации коллекций]
topic: kotlin
subtopics: [collections]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-globalscope-antipattern--kotlin--easy, q-fan-in-fan-out-channels--kotlin--hard, q-kotlin-generics--kotlin--hard]
created: 2025-10-15
updated: 2025-10-31
tags:
  - collections
  - implementations
  - kotlin
  - list
  - map
  - programming-languages
  - set
  - difficulty/easy
---
# Какие есть реализации коллекций?

# Question (EN)
> What collection implementations are available in Kotlin?

# Вопрос (RU)
> Какие реализации коллекций доступны в Kotlin?

---

## Answer (EN)

Kotlin uses Java collection implementations under the hood. Here are the main implementations:

### List Interface

**ArrayList** - Resizable array implementation:
```kotlin
val list = ArrayList<String>()  // Explicit
val list = mutableListOf("a", "b")  // Creates ArrayList

// Properties:
// + Fast random access O(1)
// + Fast iteration
// - Slow insertion/deletion in middle O(n)
// - Needs memory reallocation when growing
```

**LinkedList** - Doubly-linked list:
```kotlin
val list = LinkedList<String>()

// Properties:
// + Fast insertion/deletion at any position O(1)
// + Fast add/remove at beginning/end
// - Slow random access O(n)
// - More memory per element (prev/next pointers)
```

**When to use:**
- ArrayList: Default choice, frequent access by index
- LinkedList: Frequent insertion/deletion in middle, queue operations

### Set Interface

**HashSet** - Hash table implementation:
```kotlin
val set = HashSet<String>()  // Explicit
val set = mutableSetOf("a", "b")  // Creates LinkedHashSet

// Properties:
// + Fast add/remove/contains O(1)
// - No ordering guarantee
// - Requires good hashCode()
```

**LinkedHashSet** - Hash table + linked list:
```kotlin
val set = LinkedHashSet<String>()

// Properties:
// + Fast operations O(1)
// + Maintains insertion order
// - Slightly more memory than HashSet
```

**TreeSet** - Red-black tree (sorted):
```kotlin
val set = TreeSet<Int>()

// Properties:
// + Elements sorted (natural or custom order)
// + Operations O(log n)
// - Slower than HashSet
// - Elements must be Comparable or need Comparator
```

**When to use:**
- HashSet: Default choice, no ordering needed
- LinkedHashSet: Need insertion order
- TreeSet: Need sorted order

### Map Interface

**HashMap** - Hash table for key-value pairs:
```kotlin
val map = HashMap<String, Int>()

// Properties:
// + Fast get/put/remove O(1)
// - No ordering guarantee
// - Requires good hashCode() for keys
```

**LinkedHashMap** - Hash table + linked list:
```kotlin
val map = LinkedHashMap<String, Int>()  // Explicit
val map = mutableMapOf("a" to 1)  // Creates LinkedHashMap

// Properties:
// + Fast operations O(1)
// + Maintains insertion order
// - Slightly more memory
```

**TreeMap** - Red-black tree (sorted by keys):
```kotlin
val map = TreeMap<Int, String>()

// Properties:
// + Keys sorted
// + Operations O(log n)
// - Slower than HashMap
// - Keys must be Comparable or need Comparator
```

**When to use:**
- HashMap: Default choice, no ordering needed
- LinkedHashMap: Need insertion order
- TreeMap: Need sorted keys

### Summary Table

| Interface | Implementation | Ordering | Speed | Use Case |
|-----------|---------------|----------|-------|----------|
| **List** | ArrayList | Insertion | Fast access | Default list |
| | LinkedList | Insertion | Fast insert/delete | Queues, frequent middle ops |
| **Set** | HashSet | None | Fastest | Default set |
| | LinkedHashSet | Insertion | Fast | Preserve order |
| | TreeSet | Sorted | O(log n) | Sorted unique elements |
| **Map** | HashMap | None | Fastest | Default map |
| | LinkedHashMap | Insertion | Fast | Preserve order |
| | TreeMap | Sorted keys | O(log n) | Sorted keys |

### Kotlin Factory Functions

```kotlin
// Immutable (read-only)
val list = listOf(1, 2, 3)         // Immutable list
val set = setOf("a", "b")          // Immutable set
val map = mapOf("key" to "value")  // Immutable map

// Mutable
val mutableList = mutableListOf(1, 2)      // ArrayList
val mutableSet = mutableSetOf("a")          // LinkedHashSet
val mutableMap = mutableMapOf("k" to "v")   // LinkedHashMap

// Specific implementations
val arrayList = ArrayList<Int>()
val hashSet = HashSet<String>()
val hashMap = HashMap<String, Int>()
val linkedList = LinkedList<String>()
val treeSet = TreeSet<Int>()
val treeMap = TreeMap<Int, String>()
```

### Performance Comparison

| Operation | ArrayList | LinkedList | HashSet | TreeSet |
|-----------|-----------|------------|---------|---------|
| Add at end | O(1)* | O(1) | O(1) | O(log n) |
| Add at beginning | O(n) | O(1) | O(1) | O(log n) |
| Get by index | O(1) | O(n) | N/A | N/A |
| Contains | O(n) | O(n) | O(1) | O(log n) |
| Remove | O(n) | O(1) | O(1) | O(log n) |

*Amortized

---

## Ответ (RU)

Kotlin использует реализации коллекций Java. Основные реализации:

### List (Списки)

- **ArrayList** - массив с изменяемым размером (по умолчанию для mutableListOf)
  - Быстрый доступ по индексу O(1)
  - Медленная вставка/удаление в середине O(n)

- **LinkedList** - двусвязный список
  - Быстрая вставка/удаление O(1)
  - Медленный доступ по индексу O(n)

### Set (Множества)

- **HashSet** - хеш-таблица, без гарантий порядка
  - Быстрые операции O(1)

- **LinkedHashSet** - хеш-таблица + связный список (по умолчанию для mutableSetOf)
  - Быстрые операции O(1)
  - Сохраняет порядок вставки

- **TreeSet** - красно-черное дерево, отсортированное
  - Операции O(log n)
  - Элементы автоматически сортируются

### Map (Словари)

- **HashMap** - хеш-таблица для пар ключ-значение
  - Быстрые операции O(1)
  - Нет гарантий порядка

- **LinkedHashMap** - хеш-таблица + связный список (по умолчанию для mutableMapOf)
  - Быстрые операции O(1)
  - Сохраняет порядок вставки

- **TreeMap** - красно-черное дерево, отсортированное по ключам
  - Операции O(log n)
  - Ключи автоматически сортируются

### Когда что использовать

| Задача | Реализация |
|--------|------------|
| Список по умолчанию | ArrayList |
| Частая вставка в середину | LinkedList |
| Уникальные элементы | HashSet |
| Уникальные + порядок | LinkedHashSet |
| Уникальные + сортировка | TreeSet |
| Ключ-значение | HashMap |
| Ключ-значение + порядок | LinkedHashMap |
| Ключ-значение + сортировка | TreeMap |

## Related Questions

- [[q-globalscope-antipattern--kotlin--easy]]
- [[q-fan-in-fan-out-channels--kotlin--hard]]
- [[q-kotlin-generics--kotlin--hard]]
