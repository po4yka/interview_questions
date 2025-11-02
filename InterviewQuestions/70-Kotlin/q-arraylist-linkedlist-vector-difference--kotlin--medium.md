---
id: kotlin-160
title: "Arraylist Linkedlist Vector Difference / Разица ArrayList LinkedList и Vector"
aliases: [ArrayList LinkedList Vector Difference, Разница ArrayList LinkedList Vector]
topic: kotlin
subtopics: [collections]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-coroutine-exception-handler--kotlin--medium, q-coroutine-resource-cleanup--kotlin--medium, q-kotlin-enum-classes--kotlin--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, data structures, difficulty/medium, kotlin]
date created: Friday, October 31st 2025, 6:29:06 pm
date modified: Sunday, November 2nd 2025, 12:05:13 pm
---

# В Чем Разница ArrayList, LinkedList, Vector

**English**: What is the difference between ArrayList, LinkedList, Vector?

## Answer (EN)
These are three different `List` implementations with distinct characteristics.

### ArrayList

**Implementation**: Dynamic array (resizable array).

**Characteristics**:
- Fast random access by index: O(1)
- Fast iteration
- Slow insertion/deletion in middle: O(n) (requires shifting elements)
- Automatically grows when capacity is exceeded
- Not synchronized (not thread-safe)

**Best for**: Frequent access by index, rare insertions/deletions.

```kotlin
val arrayList = ArrayList<String>()
arrayList.add("Item 1")        // Fast append O(1)*
arrayList.add("Item 2")
arrayList.get(0)               // Fast access O(1)
arrayList.add(1, "Middle")     // Slow O(n) - shifts elements
arrayList.remove("Item 1")     // Slow O(n) - shifts elements

// *Amortized O(1) - occasionally needs to resize the internal array
```

### LinkedList

**Implementation**: Doubly-linked list (each element has prev/next pointers).

**Characteristics**:
- Slow random access: O(n) (must traverse from head or tail)
- Fast insertion/deletion at any position: O(1) (if you have the node)
- Fast add/remove at beginning or end: O(1)
- More memory overhead per element (stores prev/next references)
- Not synchronized (not thread-safe)
- Implements both List and Deque interfaces

**Best for**: Frequent insertions/deletions, queue/deque operations, rarely access by index.

```kotlin
val linkedList = LinkedList<String>()
linkedList.add("Item 1")           // Fast O(1)
linkedList.addFirst("First")       // Fast O(1)
linkedList.addLast("Last")         // Fast O(1)
linkedList.get(0)                  // Slow O(n)
linkedList.removeFirst()           // Fast O(1)
linkedList.removeLast()            // Fast O(1)

// Good for queue/deque
linkedList.offer("Element")        // Add to end
linkedList.poll()                  // Remove from beginning
```

### Vector

**Implementation**: Synchronized dynamic array (legacy from Java 1.0).

**Characteristics**:
- Similar to ArrayList internally
- All methods are synchronized (thread-safe)
- Slower than ArrayList due to synchronization overhead
- Grows by doubling capacity (ArrayList grows by 50%)
- Considered legacy - not recommended for new code

**Best for**: Legacy code only. Use `Collections.synchronizedList(ArrayList())` or concurrent collections instead.

```kotlin
val vector = Vector<String>()
vector.add("Item 1")        // Synchronized - thread-safe but slower
vector.get(0)               // Synchronized

// Modern alternative:
val syncList = Collections.synchronizedList(ArrayList<String>())
// Or use CopyOnWriteArrayList for concurrent access
```

### Performance Comparison

| Operation | ArrayList | LinkedList | Vector |
|-----------|-----------|------------|---------|
| **get(index)** | O(1) | O(n) | O(1) |
| **add(element)** | O(1)* | O(1) | O(1)* |
| **add(index, element)** | O(n) | O(1)** | O(n) |
| **remove(index)** | O(n) | O(1)** | O(n) |
| **contains(element)** | O(n) | O(n) | O(n) |
| **Thread Safety** | No | No | Yes |
| **Memory Overhead** | Low | High | Low |

*Amortized
**If you have the node reference, otherwise O(n) to find it

### When to Use What

**ArrayList**:
- - Default choice for most use cases
- - Frequent access by index
- - Iteration over elements
- - Append operations
- - Frequent insertions/deletions in middle

**LinkedList**:
- - Frequent insertions/deletions at beginning/end
- - Queue or Deque operations
- - Frequent insertions/deletions in middle (if you have node reference)
- - Random access by index
- - Iteration (slower due to pointer chasing)

**Vector**:
- - Don't use in new code
- - Only for legacy code compatibility
- Use `Collections.synchronizedList()` or `CopyOnWriteArrayList` instead

### Code Examples

```kotlin
// ArrayList - best for random access
val fruits = ArrayList<String>()
fruits.add("Apple")
fruits.add("Banana")
fruits.add("Cherry")
println(fruits[1])  // Fast: O(1)

// LinkedList - best for queue operations
val queue = LinkedList<String>()
queue.offer("Task 1")
queue.offer("Task 2")
queue.offer("Task 3")
println(queue.poll())  // Removes and returns first element

// Vector - legacy, avoid
val vector = Vector<Int>()
vector.add(1)
vector.add(2)
// Prefer: Collections.synchronizedList(ArrayList())
```

### Modern Alternatives

Instead of Vector, use:
- `Collections.synchronizedList(ArrayList())` for simple thread-safety
- `CopyOnWriteArrayList` for read-heavy concurrent access
- `ConcurrentLinkedQueue` for concurrent queue operations

```kotlin
// Thread-safe alternatives to Vector
val syncList = Collections.synchronizedList(ArrayList<String>())
val cowList = CopyOnWriteArrayList<String>()
val concurrentQueue = ConcurrentLinkedQueue<String>()
```

## Ответ (RU)
ArrayList - динамический массив с быстрым доступом по индексу O(1), но медленными вставками/удалениями в середине O(n). LinkedList - двусвязный список с быстрыми вставками/удалениями O(1), но медленным доступом по индексу O(n). Vector - устаревшая синхронизированная версия ArrayList, медленнее из-за блокировок.

Используйте ArrayList по умолчанию, LinkedList для очередей и частых вставок/удалений, Vector не используйте (замените на Collections.synchronizedList() или CopyOnWriteArrayList).

## Related Questions

- [[q-kotlin-enum-classes--kotlin--easy]]
- [[q-coroutine-resource-cleanup--kotlin--medium]]
- [[q-coroutine-exception-handler--kotlin--medium]]
