---
id: lang-061
title: "What Is Garbage In GC / Что такое мусор в GC"
aliases: [What Is Garbage In GC, Что такое мусор в GC]
topic: kotlin
subtopics: [garbage-collection, memory-management]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, c-memory-management]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/easy, garbage-collection, jvm, kotlin, memory-management]
---
# Вопрос (RU)
> Что такое "мусор" в сборщике мусора?

# Question (EN)
> What is "garbage" in a garbage collector?

## Ответ (RU)

"Мусор" в контексте сборщика мусора — это объекты в куче, которые больше не используются и недостижимы из корневых объектов (GC Roots).

Формально объект считается мусором, если:
- он находится в куче;
- к нему нельзя добраться ни из корневых ссылок, ни через объекты, достижимые из этих корней;
- он недостижим из любых GC Roots (например, стеки потоков, статические ссылки и т.п.).

Пример:

```kotlin
fun example() {
    val user = User("John")  // Объект создан; есть ссылка из текущего фрейма стека
    // Пока функция выполняется, локальные переменные учитываются при обходе GC Roots

    // После выхода из функции локальная переменная выходит из области видимости,
    // и если других ссылок на этот User нет, объект становится кандидатом на удаление (мусор)
}
// Здесь, если других ссылок нет, объект User недостижим → мусор
```

Визуальный пример:

```kotlin
class Node(val value: Int, var next: Node? = null)

fun createGarbage() {
    val node1 = Node(1)
    val node2 = Node(2)

    node1.next = node2

    // node2 достижим через node1, на который есть ссылка из стека

    node1.next = null
    // Если других ссылок на node2 нет, он становится мусором (недостижимым)
}
```

Не мусор:

```kotlin
object Singleton {
    val data = mutableListOf<String>()  // Не мусор, пока Singleton (и его класс) загружен
    // Фактически достижимо через статик-подобную ссылку, поэтому это источник достижимых объектов
}

class Activity {
    val viewModel: ViewModel  // Не мусор, пока экземпляр Activity сильно достижим
}
```

Процесс сборки мусора (концептуально):

1. Mark (пометка): обход объектов, достижимых из GC Roots, и их пометка как живых.
2. Sweep (очистка): освобождение памяти объектов, которые не были помечены (мусор).
3. Compact (уплотнение, опционально): перемещение живых объектов для уменьшения фрагментации памяти.

Почему это важно (сравнение):

```kotlin
// Ручное управление памятью в стиле C/C++ (концептуально)
val data = malloc(1000)
// Нужно явно вызвать free(data)
// Если забыть освободить память → утечка памяти
```

```kotlin
// Kotlin/Java на управляемом рантайме
val data = ByteArray(1000)
// Память может быть автоматически освобождена,
// когда data становится недостижимым (мусор)
```

Итого: мусор — это объекты в памяти, которые больше не нужны программе и недостижимы из GC Roots, поэтому рантайм может безопасно освободить занимаемую ими память.

## Answer (EN)

"Garbage" in garbage collection refers to objects in heap memory that are no longer used and unreachable from GC Roots.

Definition:

An object is garbage if:
- It's in heap memory
- No live references from roots (or from objects reachable from roots) point to it
- It is unreachable from any GC Root (e.g., thread stacks, static references, etc.)

Example:

```kotlin
fun example() {
    val user = User("John")  // Object created; referenced from the current stack frame
    // While this function is executing, the stack frame (and its local refs) are considered during GC root scanning

    // After the method returns, the local reference goes out of scope
    // and if no other references to this User remain, it becomes eligible for GC (garbage)
}
// Here, if no other references exist, the User object is unreachable → garbage
```

Visual Example:

```kotlin
class Node(val value: Int, var next: Node? = null)

fun createGarbage() {
    val node1 = Node(1)
    val node2 = Node(2)

    node1.next = node2

    // node2 is reachable through node1, which is referenced from the stack

    node1.next = null
    // If there are no other references to node2, it becomes garbage (unreachable)
}
```

Not Garbage:

```kotlin
object Singleton {
    val data = mutableListOf<String>()  // Not garbage while the Singleton (and its class) remains loaded
    // Effectively reachable via a static-like reference, so it is treated as a root reference source
}

class Activity {
    val viewModel: ViewModel  // Not garbage while the Activity instance is strongly reachable
}
```

Garbage Collection Process (conceptually):

1. Mark: Start from GC Roots, mark all reachable objects.
2. Sweep: Reclaim memory of unmarked objects (garbage).
3. Compact (optional): Move objects to reduce fragmentation.

Why GC Matters (contrast):

```kotlin
// C/C++ style manual memory (conceptual example)
val data = malloc(1000)
// Must call free(data) manually
// Forgetting to free → memory leak
```

```kotlin
// Kotlin/Java on a managed runtime
val data = ByteArray(1000)
// Memory can be reclaimed automatically once data becomes unreachable (garbage)
```

Summary: Garbage = objects in memory that are no longer needed and are unreachable from GC Roots, so the runtime can safely reclaim their memory.

---

## Follow-ups (RU)

- Как определение "мусора" связано с понятием достижимости и GC Roots в JVM, на которой работает Kotlin?
- Как объекты, которые больше не нужны логике программы, но всё ещё удерживаются через одиночки или статические ссылки, могут приводить к утечкам памяти даже при наличии GC?
- Какие алгоритмы сборки мусора используют модель достижимости (mark-sweep, поколенческий GC и т.д.)?

## Follow-ups (EN)

- How does the definition of "garbage" relate to reachability and GC Roots on the JVM used by Kotlin?
- How can objects that are no longer needed by the program logic but are still held via singletons or static references cause memory leaks even with GC?
- What GC algorithms use this notion of reachability (mark-sweep, generational GC, etc.)?

## Ссылки (RU)

- [[c-garbage-collection]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References (EN)

- [[c-garbage-collection]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- См. список ниже на английском.

## Related Questions (EN)

(Note: The following previously referenced wikilinks were removed because matching files do not exist: q-garbage-collection-basics--kotlin--easy, q-memory-leaks-with-gc--kotlin--medium, q-generational-gc-concepts--kotlin--medium.)
