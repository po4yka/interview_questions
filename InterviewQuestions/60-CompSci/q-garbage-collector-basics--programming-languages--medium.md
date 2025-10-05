---
tags:
  - garbage-collector
  - gc
  - memory-management
  - kotlin
  - java
  - performance
  - easy_kotlin
  - programming-languages
difficulty: medium
---

# Что такое сборщик мусора?

**English**: What is garbage collector?

## Answer

**Garbage Collector (GC)** is a memory management mechanism that automatically frees unused memory occupied by objects to which there are no more references.

**How it works:**

1. **Tracks object references**: Monitors which objects are still reachable from program
2. **Identifies garbage**: Objects with no references are considered garbage
3. **Reclaims memory**: Frees memory occupied by unreachable objects
4. **Runs in background**: Executes periodically without manual intervention

**In Kotlin/Java:**
- GC works in the background automatically
- Eliminates need to manually free memory (unlike C/C++)
- Helps prevent memory leaks
- Makes memory management safer and simpler

**Benefits:**
- Automatic memory management
- Prevents memory leaks
- Reduces programmer errors
- Improves developer productivity

**Considerations:**
- GC pauses can affect performance
- No control over when GC runs
- Objects remain in memory until GC runs

**Example of memory reclamation:**
```kotlin
fun createObject() {
    val obj = LargeObject()  // Object created
    // ... use obj
}  // obj becomes unreachable here, eligible for GC
```

## Ответ

Сборщик мусора (Garbage Collector) — это механизм управления памятью, который автоматически освобождает неиспользуемую память, занятую объектами, к которым больше нет ссылок...

