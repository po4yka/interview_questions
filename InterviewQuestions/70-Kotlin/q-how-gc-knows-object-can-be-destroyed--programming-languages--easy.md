---
id: lang-046
title: "How Gc Knows Object Can Be Destroyed / Как GC знает что объект можно уничтожить"
aliases: [How Gc Knows Object Can Be Destroyed, Как GC знает что объект можно уничтожить]
topic: programming-languages
subtopics: [garbage-collection, jvm, memory-management]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, q-garbage-collector-basics--programming-languages--medium, q-garbage-collector-roots--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, garbage-collection, jvm, kotlin, memory-management, programming-languages]
date created: Friday, October 31st 2025, 6:31:27 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Как Сборщик Мусора Понимает Что Объект Можно Уничтожить?

# Вопрос (RU)
> Как сборщик мусора понимает что объект можно уничтожить?

---

# Question (EN)
> How does garbage collector know that an object can be destroyed?

## Ответ (RU)

Сборщик мусора использует анализ ссылок. Объект считается 'мёртвым', если на него нет доступных ссылок из корневых объектов. GC обходит все достижимые объекты, начиная с корневых. Недостижимые объекты считаются мусором и удаляются.

## Answer (EN)

The garbage collector uses **reachability analysis** to determine if an object can be destroyed.

**Algorithm: Mark and Sweep**

1. **Find GC Roots** (starting points)
2. **Mark** all reachable objects
3. **Sweep** (delete) unmarked objects

**An object can be destroyed if it's UNREACHABLE from any GC Root.**

**Example:**

```kotlin
fun example() {
    val user1 = User("Alice")  // GC Root (local variable)
    val user2 = User("Bob")    // GC Root

    val temp = User("Charlie") // GC Root
    // All 3 objects are reachable

    // temp goes out of scope or set to null
    // User("Charlie") becomes unreachable → CAN BE DESTROYED
}
```

**Reachability Graph:**

```kotlin
class Node(val value: Int, var next: Node? = null)

fun main() {
    val root = Node(1)  // GC Root
    root.next = Node(2)
    root.next?.next = Node(3)

    // Reachability chain:
    // root (GC Root) → Node(2) → Node(3)
    // All are REACHABLE → SAFE

    root.next = null
    // Node(2) and Node(3) are now UNREACHABLE → CAN BE DESTROYED
}
```

**Visual:**

```
Before:
[GC Root: root] → [Node(1)] → [Node(2)] → [Node(3)]
All reachable GOOD

After root.next = null:
[GC Root: root] → [Node(1)]
[Node(2)] → [Node(3)]  ← Unreachable - → Will be destroyed
```

**Dead Object Example:**

```kotlin
class Activity {
    private var listener: (() -> Unit)? = null

    fun setListener(callback: () -> Unit) {
        listener = callback
    }

    fun destroy() {
        listener = null  // Remove reference
        // If no other references exist, callback can be GC'd
    }
}
```

**Circular References:**

```kotlin
class Node(var next: Node? = null)

fun circularExample() {
    val node1 = Node()
    val node2 = Node()

    node1.next = node2
    node2.next = node1  // Circular reference

    // Both are reachable from local variables

    // Function ends, node1 and node2 go out of scope
    // Even though they reference each other,
    // they're UNREACHABLE from GC Roots → CAN BE DESTROYED
}
```

**Key Points:**

| Condition | Result |
|-----------|--------|
| Reachable from GC Root | - KEEP (safe from GC) |
| Unreachable from GC Root | - DESTROY (eligible for GC) |
| Has references but unreachable | - DESTROY (references don't matter) |
| Circular references but unreachable | - DESTROY (GC handles this) |

**Summary:**

GC uses **reachability analysis from GC Roots**. If an object cannot be reached through any chain of references from a GC Root, it's considered **dead** and will be destroyed.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-what-is-job-object--programming-languages--medium]]
- [[q-mediator-pattern--design-patterns--medium]]
-
