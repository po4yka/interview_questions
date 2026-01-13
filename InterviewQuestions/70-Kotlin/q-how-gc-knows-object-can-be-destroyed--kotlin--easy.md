---
'---id': lang-046
title: How GC Knows Object Can Be Destroyed / Как GC знает что объект можно уничтожить
aliases:
- How GC Knows Object Can Be Destroyed
- Как GC знает что объект можно уничтожить
topic: kotlin
subtopics:
- garbage-collection
- memory-management
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-aggregation
- c-app-signing
- c-backend
- c-binary-search
- c-binary-search-tree
- c-binder
- c-biometric-authentication
- c-bm25-ranking
- c-by-type
- c-cap-theorem
- c-ci-cd
- c-ci-cd-pipelines
- c-clean-code
- c-compiler-optimization
- c-compose-modifiers
- c-compose-phases
- c-compose-semantics
- c-computer-science
- c-concurrency
- c-cross-platform-development
- c-cross-platform-mobile
- c-cs
- c-data-classes
- c-data-loading
- c-debugging
- c-declarative-programming
- c-deep-linking
- c-density-independent-pixels
- c-dimension-units
- c-dp-sp-units
- c-dsl-builders
- c-dynamic-programming
- c-espresso-testing
- c-event-handling
- c-folder
- c-functional-programming
- c-garbage-collection
- c-gdpr-compliance
- c-gesture-detection
- c-gradle-build-cache
- c-gradle-build-system
- c-https-tls
- c-image-formats
- c-inheritance
- c-jit-aot-compilation
- c-kmm
- c-kotlin
- c-lambda-expressions
- c-lazy-grid
- c-lazy-initialization
- c-level
- c-load-balancing
- c-manifest
- c-memory-optimization
- c-memory-profiler
- c-microservices
- c-multipart-form-data
- c-multithreading
- c-mutablestate
- c-networking
- c-offline-first-architecture
- c-oop
- c-oop-concepts
- c-oop-fundamentals
- c-oop-principles
- c-play-console
- c-play-feature-delivery
- c-programming-languages
- c-properties
- c-real-time-communication
- c-references
- c-scaling-strategies
- c-scoped-storage
- c-security
- c-serialization
- c-server-sent-events
- c-shader-programming
- c-snapshot-system
- c-specific
- c-strictmode
- c-system-ui
- c-test-doubles
- c-test-sharding
- c-testing-pyramid
- c-testing-strategies
- c-theming
- c-to-folder
- c-token-management
- c-touch-input
- c-turbine-testing
- c-two-pointers
- c-ui-testing
- c-ui-ux-accessibility
- c-value-classes
- c-variable
- c-weak-references
- c-windowinsets
- c-xml
created: 2025-10-15
updated: 2025-11-11
tags:
- difficulty/easy
- garbage-collection
- jvm
- kotlin
- memory-management
- programming-languages
anki_cards:
- slug: q-how-gc-knows-object-can-be-destroyed--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-how-gc-knows-object-can-be-destroyed--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> Как сборщик мусора понимает что объект можно уничтожить?

---

# Question (EN)
> How does garbage collector know that an object can be destroyed?

## Ответ (RU)

(Контекст: ниже речь про Kotlin/JVM и типичный трассирующий GC JVM. Для Kotlin/Native и Kotlin/JS механизмы управления памятью отличаются.)

Сборщик мусора использует анализ достижимости (`reachability analysis`) от корневых объектов (`GC Roots`). Объект может быть уничтожен (становится кандидатом на сборку), если он недостижим ни из одного `GC Root`.

Типичный алгоритм (например, в JVM) — `Mark and Sweep`:

1. Находятся `GC Roots` (стековые ссылки локальных переменных, активные потоки, статические поля, некоторые нативные ссылки и т.п.).
2. Помечаются все объекты, достижимые по цепочкам ссылок от `GC Roots`.
3. Все непомеченные (недостижимые) объекты считаются мусором и становятся кандидатами на освобождение памяти.

Круговые ссылки не мешают сборке мусора: если вся группа объектов недостижима от `GC Roots`, она будет собрана, даже если объекты ссылаются друг на друга.

Ядро условия:

- Объект может быть уничтожен, если он недостижим из любых `GC Roots` (то есть только становится кандидатом на сборку; фактический момент освобождения памяти определяется GC).

Примеры:

```kotlin
fun example() {
    val user1 = User("Alice")  // Ссылка из текущего фрейма стека
    val user2 = User("Bob")    // Ссылка из текущего фрейма стека

    val temp = User("Charlie") // Ссылка из текущего фрейма стека
    // Все 3 объекта достижимы через ссылки на стеке

    // Когда temp выходит из области видимости или присваивается null,
    // ссылка удаляется. Если других ссылок нет,
    // User("Charlie") становится недостижимым → МОЖЕТ БЫТЬ СОБРАН GC.
}
```

Граф достижимости:

```kotlin
class Node(val value: Int, var next: Node? = null)

fun main() {
    val root = Node(1)  // Ссылка из текущего фрейма стека
    root.next = Node(2)
    root.next?.next = Node(3)

    // Цепочка достижимости:
    // стек → root → Node(2) → Node(3)
    // Все достижимы → НЕ КАНДИДАТЫ НА GC

    root.next = null
    // Теперь пути от GC Roots к Node(2) и Node(3) нет
    // Node(2) и Node(3) НЕДОСТИЖИМЫ → МОГУТ БЫТЬ СОБРАНЫ GC
}
```

Визуально:

До:

[GC Root (stack)] → [Node(1)] → [Node(2)] → [Node(3)]
Все достижимы → не подлежат GC

После root.next = null:

[GC Root (stack)] → [Node(1)]
[Node(2)] → [Node(3)]  ← недостижимы → кандидаты на GC

"Мёртвый" объект:

```kotlin
class Activity {
    private var listener: (() -> Unit)? = null

    fun setListener(callback: () -> Unit) {
        listener = callback
    }

    fun destroy() {
        listener = null  // Убираем ссылку из этого экземпляра
        // Если других ссылок на callback нет, он становится кандидатом на GC
    }
}
```

Циклические ссылки:

```kotlin
class Node(var next: Node? = null)

fun circularExample() {
    val node1 = Node()
    val node2 = Node()

    node1.next = node2
    node2.next = node1  // Циклическая ссылка

    // Пока есть ссылки из локальных переменных, оба достижимы.

    // После выхода из функции ссылки со стека исчезают.
    // Цикл {node1, node2} недостижим от любых GC Roots
    // → МОЖЕТ БЫТЬ СОБРАН, несмотря на взаимные ссылки.
}
```

Ключевые моменты:

- Достижим от `GC Root` → сохранить (не кандидат на GC).
- Недостижим от `GC Root` → кандидат на сборку (GC может освободить память).
- Есть ссылки, но объект недостижим от корней → кандидат на сборку.
- Циклические ссылки, недостижимые от корней → кандидат на сборку (трассирующий GC умеет работать с циклами).

**Вывод:**

GC использует анализ достижимости от GC Roots. Если объект недостижим по цепочке ссылок, начиная с любого GC Root, он считается мусором и становится кандидатом на сборку. Фактический момент сборки недетерминирован.

## Answer (EN)

(`Context`: below we’re talking about Kotlin/JVM and the typical tracing GC used by the JVM. Kotlin/Native and Kotlin/JS use different memory management mechanisms.)

The garbage collector uses reachability analysis to determine if an object can be destroyed (more precisely: becomes eligible for collection).

Typical algorithm (e.g., on the JVM): Mark and Sweep

1. Find GC Roots (starting points: references in stack frames of active methods, active threads, static fields, some native references, etc.).
2. Mark all objects reachable by following references from GC Roots.
3. Sweep (reclaim) all unmarked (unreachable) objects — these are considered garbage and are eligible for memory reclamation.

An object can be destroyed (is eligible for GC) if it is unreachable from any GC Root. Actual reclamation happens at the GC’s discretion, not immediately.

**Example:**

```kotlin
fun example() {
    val user1 = User("Alice")  // Referenced from the current stack frame
    val user2 = User("Bob")    // Referenced from the current stack frame

    val temp = User("Charlie") // Referenced from the current stack frame
    // All 3 objects are reachable via stack references

    // When temp goes out of scope or is set to null,
    // the reference is removed. If no other references exist,
    // User("Charlie") becomes unreachable → ELIGIBLE FOR GC.
}
```

**Reachability Graph:**

```kotlin
class Node(val value: Int, var next: Node? = null)

fun main() {
    val root = Node(1)  // Referenced from the current stack frame
    root.next = Node(2)
    root.next?.next = Node(3)

    // Reachability chain:
    // stack frame → root → Node(2) → Node(3)
    // All are reachable → NOT ELIGIBLE FOR GC

    root.next = null
    // Now there is no path from GC Roots to Node(2) and Node(3)
    // Node(2) and Node(3) are UNREACHABLE → ELIGIBLE FOR GC
}
```

**Visual:**

```text
Before:
[GC Root (stack)] → [Node(1)] → [Node(2)] → [Node(3)]
All reachable → not eligible for GC

After root.next = null:
[GC Root (stack)] → [Node(1)]
[Node(2)] → [Node(3)]  ← Unreachable → eligible for GC
```

**Dead Object Example:**

```kotlin
class Activity {
    private var listener: (() -> Unit)? = null

    fun setListener(callback: () -> Unit) {
        listener = callback
    }

    fun destroy() {
        listener = null  // Remove reference from this instance
        // If no other references to the callback exist, it becomes eligible for GC
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

    // Both are reachable from local variables here.

    // When the function ends, references from the stack frame disappear.
    // The cycle {node1, node2} is no longer reachable from any GC Root
    // → ELIGIBLE FOR GC, despite the circular references.
}
```

**Key Points:**

- Reachable from GC Root → KEEP (not eligible for GC).
- Unreachable from GC Root → ELIGIBLE FOR GC (GC may reclaim memory).
- Has references but unreachable from roots → ELIGIBLE FOR GC (eligibility depends on reachability, not reference count).
- Circular references but unreachable from roots → ELIGIBLE FOR GC (tracing GC correctly collects cycles).

**Summary:**

GC uses reachability analysis from GC Roots. If an object cannot be reached through any chain of references starting from a GC Root, it is considered garbage and becomes eligible for collection. The actual time of collection is non-deterministic.

---

## Дополнительные Вопросы (RU)

- Как определяются `GC Roots` в JVM, и как Kotlin/JVM опирается на них?
- Чем это отличается от управления памятью на основе подсчёта ссылок?
- Каковы типичные проблемы (например, утечки памяти из-за висящих ссылок, слушателей, кэшей)?

## Follow-ups

- How are GC Roots defined on the JVM, and how does Kotlin/JVM rely on them?
- How does this differ from reference-counting-based memory management?
- What are common pitfalls (e.g., memory leaks due to lingering references, listeners, caches)?

## Ссылки (RU)

- [[c-garbage-collection]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-garbage-collection]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-garbage-collector-basics--kotlin--medium]]
- [[q-what-is-job-object--kotlin--medium]]
- [[q-state-pattern--cs--medium]]

## Related Questions

- [[q-garbage-collector-basics--kotlin--medium]]
- [[q-what-is-job-object--kotlin--medium]]
- [[q-state-pattern--cs--medium]]
