---
topic: android
tags:
  - android
  - android/memory-management
  - heap
  - memory-management
  - multithreading
  - stack
  - threading
difficulty: medium
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# Изменится ли объём памяти стека/кучи, если в приложении создано несколько потоков?

**English**: Will stack/heap memory size change if multiple threads are created in the app?

## Answer (EN)
**Yes**, **stack size will change**, but **heap size will remain unchanged** (though load on it will increase).

**Stack Memory:**

**Each thread gets its own stack** - so more threads = more stack memory.

```kotlin
// Each thread has its own stack
Thread {
    val localVar = 10  // Stored in this thread's stack
    recursiveFunction()  // Uses this thread's stack
}.start()
```

**Heap Memory:**

**All threads share the same heap** - heap size doesn't grow with threads, but contention increases.

```kotlin
// All threads share the same heap
val sharedObject = MyObject()  // Allocated in shared heap

Thread {
    val obj1 = MyObject()  // Same heap
}.start()
```

**Memory Calculation:**

```
Main thread stack:    8 MB
Worker thread stack:  1 MB each
Heap:                 512 MB (shared)

1 thread:    8 + 0 + 512 = 520 MB
10 threads:  8 + 10 + 512 = 530 MB
100 threads: 8 + 100 + 512 = 620 MB
```

**Summary:**

- **Stack**: Each thread = separate stack → total stack **increases**
- **Heap**: All threads share heap → heap size **unchanged**, load increases
- **Per thread**: ~1 MB stack overhead

## Ответ (RU)
**Да**, объём **стека изменится**, а вот объём **кучи останется неизменным**, но нагрузка на неё увеличится.

Каждый поток получает свой собственный стек (~1 MB), поэтому больше потоков = больше памяти стека. Куча же общая для всех потоков.


---

## Related Questions

### Kotlin Language Features
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Concurrency
- [[q-channel-pipelines--kotlin--hard]] - Concurrency
- [[q-coroutines-vs-threads--programming-languages--medium]] - Concurrency
- [[q-deferred-async-patterns--kotlin--medium]] - Concurrency
- [[q-produce-actor-builders--kotlin--medium]] - Concurrency
- [[q-actor-pattern--kotlin--hard]] - Concurrency
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - Concurrency
