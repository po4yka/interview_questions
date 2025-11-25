---
id: concept-001
title: Garbage Collection / Сборка мусора
aliases: [Garbage Collection, GC, Автоматическое управление памятью, Сборка мусора]
kind: concept
summary: Automatic memory management mechanism that identifies and reclaims memory occupied by objects that are no longer reachable or needed by the program.
links: []
created: 2025-11-05
updated: 2025-11-05
tags: [concept, jvm, memory-management, runtime]
date created: Wednesday, November 5th 2025, 6:30:35 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

**Garbage Collection (GC)** is an automatic memory management process that runs in managed runtime environments (JVM, .NET CLR, etc.). The garbage collector periodically identifies objects that are no longer reachable from any root references and reclaims their memory.

Key concepts:
- **Garbage**: Objects that have no live references pointing to them
- **GC Roots**: Starting points for reachability analysis (local variables, static fields, active threads, JNI references)
- **Reachability**: An object is reachable if there's a path of references from any GC root to that object
- **Collection cycles**: GC runs periodically or when memory pressure increases

Common GC algorithms:
- **Mark-and-Sweep**: Mark all reachable objects, then sweep and reclaim unmarked ones
- **Generational GC**: Separate heap into generations (young/old) based on object lifetime
- **Concurrent GC**: Run collection cycles concurrently with application threads to minimize pauses

# Сводка (RU)

**Сборка мусора (Garbage Collection, GC)** — это процесс автоматического управления памятью, который работает в управляемых средах выполнения (JVM, .NET CLR и др.). Сборщик мусора периодически находит объекты, которые больше не достижимы из корневых ссылок, и освобождает их память.

Ключевые понятия:
- **Мусор**: Объекты, на которые нет активных ссылок
- **Корни GC**: Стартовые точки для анализа достижимости (локальные переменные, статические поля, активные потоки, JNI-ссылки)
- **Достижимость**: Объект достижим, если существует путь ссылок от любого корня GC до этого объекта
- **Циклы сборки**: GC запускается периодически или при увеличении давления на память

Распространённые алгоритмы GC:
- **Mark-and-Sweep**: Пометить все достижимые объекты, затем удалить непомеченные
- **Поколенческий GC**: Разделить кучу на поколения (молодое/старое) по времени жизни объектов
- **Конкурентный GC**: Выполнять циклы сборки параллельно с потоками приложения для минимизации пауз

## Use Cases / Trade-offs

**Benefits**:
- Eliminates manual memory management and prevents memory leaks
- Prevents dangling pointers and use-after-free bugs
- Simplifies development and reduces cognitive load

**Trade-offs**:
- Non-deterministic timing: GC can run at unpredictable moments
- Pause times: Some GC phases stop application threads (Stop-The-World)
- Memory overhead: GC requires extra memory for bookkeeping
- Performance impact: GC cycles consume CPU and can affect latency

**When it matters**:
- Real-time systems: GC pauses can violate latency requirements
- Memory-constrained devices: GC overhead may be too expensive
- High-performance systems: GC tuning becomes critical (heap size, collector type, pause time goals)

## References

- [Oracle Java GC Tuning Guide](https://docs.oracle.com/en/java/javase/17/gctuning/)
- [Understanding Java Garbage Collection](https://www.oracle.com/webfolder/technetwork/tutorials/obe/java/gc01/index.html)
- [Android Memory Management](https://developer.android.com/topic/performance/memory-overview)
- [Wikipedia: Garbage Collection](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science))
