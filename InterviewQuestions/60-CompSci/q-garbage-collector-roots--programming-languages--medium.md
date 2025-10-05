---
tags:
  - kotlin
  - jvm
  - garbage-collection
  - gc-roots
  - memory-management
  - easy_kotlin
  - programming-languages
difficulty: medium
---

# Что такое Garbage Collector Roots?

**English**: What are Garbage Collector Roots?

## Answer

**Garbage Collector (GC) Roots** are the starting points that the garbage collector uses to determine which objects are reachable (alive) and which can be garbage collected.

**How GC Works:**

1. Start from GC Roots
2. Mark all reachable objects
3. Sweep (delete) unreachable objects

**An object is reachable if it can be accessed from any GC Root through a chain of references.**

**Types of GC Roots:**

**1. Local Variables & Parameters**
```kotlin
fun example() {
    val user = User("John")  // GC Root (local variable)
    // user is reachable while method is executing
}
// After method exits, user is no longer a GC Root
```

**2. Active Thread Stack Frames**
```kotlin
Thread.start {
    val data = Data()  // GC Root (in active thread)
    // data is reachable while thread is running
}
```

**3. Static Fields**
```kotlin
object AppConfig {
    val instance = Config()  // GC Root (static field)
    // Always reachable while class is loaded
}
```

**4. JNI References**
```kotlin
// Native code references
external fun nativeMethod()  // May create JNI GC Roots
```

**Example:**

```kotlin
class Node(val value: Int, var next: Node? = null)

fun main() {
    val root = Node(1)  // GC Root (local variable)
    root.next = Node(2)
    root.next?.next = Node(3)

    // Reachable: root, Node(2), Node(3)
    // All are kept alive because reachable from GC Root

    root.next = null  // Node(2) and Node(3) now unreachable
    // Node(2) and Node(3) can be garbage collected
}
```

**Memory Leak Example:**

```kotlin
object Cache {
    private val data = mutableListOf<Data>()  // GC Root!

    fun add(item: Data) {
        data.add(item)
        // Items never removed - memory leak!
        // All items are always reachable from static field
    }
}
```

**Categories:**

| GC Root Type | Lifetime | Example |
|--------------|----------|---------|
| Local variables | Method execution | `val x = User()` |
| Static fields | Class loaded | `companion object { val x }` |
| Active threads | Thread running | Thread stack variables |
| JNI references | Native code | JNI global refs |

**Summary:**

GC Roots are the **starting points** for garbage collection. Objects reachable from GC Roots are **kept alive**. Objects not reachable are **garbage** and will be collected.

## Ответ

Garbage Collector Roots — это набор объектов, которые используются как отправные точки для определения достижимых объектов. Включают: локальные переменные активных потоков, статические поля классов и JNI ссылки.

