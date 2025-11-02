---
id: lang-061
title: "What Is Garbage In GC / Что такое мусор в GC"
aliases: [What Is Garbage In GC, Что такое мусор в GC]
topic: programming-languages
subtopics: [memory-management, garbage-collection, jvm]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [q-interpreter-pattern--design-patterns--hard, q-mvvm-pattern--architecture-patterns--medium, q-prototype-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [garbage-collection, jvm, kotlin, memory-management, programming-languages, difficulty/easy]
date created: Saturday, October 4th 2025, 1:21:00 pm
date modified: Sunday, October 26th 2025, 1:39:58 pm
---

# О Каком Мусоре Идет Речь В Сборщике Мусора?

# Question (EN)
> What is "garbage" in garbage collector?

# Вопрос (RU)
> О каком мусоре идет речь в сборщике мусора?

---

## Answer (EN)

**"Garbage"** in garbage collection refers to **objects in memory that are no longer used and unreachable from GC Roots**.

**Definition:**

An object is garbage if:
- It's in heap memory
- No active references point to it
- Unreachable from any GC Root

**Example:**

```kotlin
fun example() {
    val user = User("John")  // Object created
    // user is reachable (local variable is GC Root)

    // After method ends, user reference is gone
    // User object becomes garbage
}
// User object is now unreachable → GARBAGE
```

**Visual Example:**

```kotlin
class Node(val value: Int, var next: Node? = null)

fun createGarbage() {
    val node1 = Node(1)
    val node2 = Node(2)

    node1.next = node2

    // Both reachable through node1 (GC Root)

    node1.next = null
    // node2 is now garbage (no references to it)
}
```

**Not Garbage:**

```kotlin
object Singleton {
    val data = mutableListOf<String>()  // NOT garbage
    // Static field - always reachable
}

class Activity {
    val viewModel: ViewModel  // NOT garbage while Activity exists
}
```

**Garbage Collection Process:**

1. **Mark**: Start from GC Roots, mark all reachable objects
2. **Sweep**: Delete unmarked objects (garbage)
3. **Compact**: (Optional) Move objects to reduce fragmentation

**Why GC Matters:**

Without GC:
```kotlin
// C/C++ style manual memory
val data = malloc(1000)
// Must call free(data) manually
// Forget to free → memory leak
```

With GC:
```kotlin
// Kotlin/Java - automatic
val data = ByteArray(1000)
// Automatically freed when unreachable
```

**Summary:**

**Garbage** = objects in memory that are **no longer needed** and **unreachable** from GC Roots. GC automatically frees this memory.

---

## Ответ (RU)

Это объекты в памяти, которые больше не используются и недостижимы из корневых объектов. Сборщик мусора освобождает эти объекты, чтобы уменьшить использование памяти.

## Related Questions

- [[q-prototype-pattern--design-patterns--medium]]
- [[q-interpreter-pattern--design-patterns--hard]]
- [[q-mvvm-pattern--architecture-patterns--medium]]
