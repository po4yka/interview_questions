---
id: lang-030
title: "Iterator Concept / Концепция Iterator"
aliases: [Iterator Concept, Концепция Iterator]
topic: programming-languages
subtopics: [collections, design-patterns, iterators]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, c-design-patterns, q-iterator-order-guarantee--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, design-patterns, difficulty/easy, iterator, kotlin, programming-languages]
---
# Что Такое Итератор?

# Вопрос (RU)
> Что такое итератор?

---

# Question (EN)
> What is an iterator?

## Ответ (RU)

Итератор — это объект, позволяющий поэлементно перебирать коллекцию (список, массив и т.п.). Он обычно предоставляет методы hasNext() и next() и позволяет абстрагироваться от конкретной структуры.

## Answer (EN)

**Iterator** is an object that allows **element-by-element traversal** of a collection (list, array, set, etc.). It abstracts the underlying structure and provides a uniform way to iterate.

### Iterator Interface

**Core methods:**
```kotlin
interface Iterator<out T> {
    fun hasNext(): Boolean  // Check if more elements exist
    fun next(): T           // Get next element
}
```

### Using Iterator

**Manual iteration:**
```kotlin
val list = listOf("A", "B", "C")
val iterator = list.iterator()

while (iterator.hasNext()) {
    val element = iterator.next()
    println(element)
}
// Output: A B C
```

**For loop (uses iterator internally):**
```kotlin
val list = listOf("A", "B", "C")

for (element in list) {  // Calls iterator() behind the scenes
    println(element)
}
```

### MutableIterator

**Allows removal during iteration:**
```kotlin
interface MutableIterator<out T> : Iterator<T> {
    fun remove()  // Remove last element returned by next()
}
```

**Example:**
```kotlin
val list = mutableListOf(1, 2, 3, 4, 5)
val iterator = list.iterator()

while (iterator.hasNext()) {
    val element = iterator.next()
    if (element % 2 == 0) {
        iterator.remove()  // Remove even numbers
    }
}

println(list)  // [1, 3, 5]
```

### Custom Iterator

**Creating your own iterator:**
```kotlin
class Range(private val start: Int, private val end: Int) : Iterable<Int> {
    override fun iterator(): Iterator<Int> {
        return object : Iterator<Int> {
            private var current = start

            override fun hasNext(): Boolean = current <= end

            override fun next(): Int {
                if (!hasNext()) throw NoSuchElementException()
                return current++
            }
        }
    }
}

// Usage
val range = Range(1, 5)
for (num in range) {
    println(num)  // 1 2 3 4 5
}
```

### Iterator Methods in Kotlin

**Standard library extensions:**
```kotlin
val list = listOf(1, 2, 3, 4, 5)
val iterator = list.iterator()

// forEach with iterator
iterator.forEach { println(it) }

// Convert to list
val newList = iterator.asSequence().toList()

// Filter while iterating
list.iterator().asSequence()
    .filter { it % 2 == 0 }
    .forEach { println(it) }
```

### Benefits of Iterator

1. **Abstraction**: Don't need to know internal structure
2. **Uniformity**: Same interface for all collections
3. **Safety**: Prevents index out of bounds errors
4. **Flexibility**: Can implement custom iteration logic
5. **Modification**: MutableIterator allows safe removal during iteration

### Iterator Vs Index-Based Loop

**Iterator approach:**
```kotlin
val iterator = list.iterator()
while (iterator.hasNext()) {
    val item = iterator.next()
    println(item)
}
```

**Index-based approach:**
```kotlin
for (i in list.indices) {
    val item = list[i]
    println(item)
}
```

**When to use iterator:**
- Working with abstract collections (don't know if it's indexed)
- Need to remove elements during iteration
- Working with sequences or streams
- LinkedList or other non-indexed structures

**When to use indices:**
- Need current index value
- ArrayList or array (fast random access)
- Need to access multiple elements at once

### Common Pitfall

**ConcurrentModificationException:**
```kotlin
val list = mutableListOf(1, 2, 3, 4, 5)

// - Wrong: Modifying collection while iterating
for (element in list) {
    if (element % 2 == 0) {
        list.remove(element)  // ConcurrentModificationException!
    }
}

// - Correct: Use iterator.remove()
val iterator = list.iterator()
while (iterator.hasNext()) {
    if (iterator.next() % 2 == 0) {
        iterator.remove()  // Safe
    }
}

// - Alternative: Filter to new list
val filtered = list.filter { it % 2 != 0 }
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-what-happens-to-unneeded-objects--programming-languages--easy]]
- [[q-interface-vs-abstract-class--programming-languages--medium]]
-
