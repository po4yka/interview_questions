---
id: lang-080
title: "Garbage Collector Roots / Корни Garbage Collector"
aliases: [Garbage Collector Roots, Корни Garbage Collector]
topic: programming-languages
subtopics: [garbage-collection, jvm, memory-management]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, q-garbage-collector-basics--programming-languages--medium, q-garbage-collector-definition--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium, garbage-collection, jvm, kotlin, memory-management, programming-languages]
date created: Friday, October 31st 2025, 6:31:04 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Что Такое Garbage Collector Roots?

# Question (EN)
> What are Garbage Collector Roots?

# Вопрос (RU)
> Что такое Garbage Collector Roots?

---

## Answer (EN)

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

---

## Ответ (RU)

**Garbage Collector (GC) Roots** — это начальные точки, которые сборщик мусора использует для определения того, какие объекты достижимы (живы) и какие могут быть собраны сборщиком мусора.

**Как работает GC:**

1. Начать с GC Roots
2. Пометить все достижимые объекты
3. Удалить (sweep) недостижимые объекты

**Объект достижим, если к нему можно получить доступ из любого GC Root через цепочку ссылок.**

**Типы GC Roots:**

**1. Локальные переменные и параметры**
```kotlin
fun example() {
    val user = User("John")  // GC Root (локальная переменная)
    // user достижим пока выполняется метод
}
// После выхода из метода user больше не GC Root
```

**2. Активные фреймы стека потоков**
```kotlin
Thread.start {
    val data = Data()  // GC Root (в активном потоке)
    // data достижим пока поток выполняется
}
```

**3. Статические поля**
```kotlin
object AppConfig {
    val instance = Config()  // GC Root (статическое поле)
    // Всегда достижим пока класс загружен
}
```

**4. JNI ссылки**
```kotlin
// Ссылки из нативного кода
external fun nativeMethod()  // Может создавать JNI GC Roots
```

**Пример:**

```kotlin
class Node(val value: Int, var next: Node? = null)

fun main() {
    val root = Node(1)  // GC Root (локальная переменная)
    root.next = Node(2)
    root.next?.next = Node(3)

    // Достижимые: root, Node(2), Node(3)
    // Все остаются живыми, так как достижимы из GC Root

    root.next = null  // Node(2) и Node(3) теперь недостижимы
    // Node(2) и Node(3) могут быть собраны сборщиком мусора
}
```

**Пример утечки памяти:**

```kotlin
object Cache {
    private val data = mutableListOf<Data>()  // GC Root!

    fun add(item: Data) {
        data.add(item)
        // Элементы никогда не удаляются - утечка памяти!
        // Все элементы всегда достижимы из статического поля
    }
}
```

**Категории:**

| Тип GC Root | Время жизни | Пример |
|-------------|-------------|--------|
| Локальные переменные | Выполнение метода | `val x = User()` |
| Статические поля | Класс загружен | `companion object { val x }` |
| Активные потоки | Поток выполняется | Переменные в стеке потока |
| JNI ссылки | Нативный код | Глобальные JNI ссылки |

**Резюме:**

GC Roots — это **начальные точки** для сборки мусора. Объекты, достижимые из GC Roots, **остаются живыми**. Объекты, не достижимые, являются **мусором** и будут собраны. Основные типы GC Roots: локальные переменные активных методов, статические поля загруженных классов, активные потоки и JNI ссылки. Понимание GC Roots важно для предотвращения утечек памяти и оптимизации использования памяти.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-extension-properties--programming-languages--medium]]
- [[q-java-lambda-type--programming-languages--easy]]
- [[q-inheritance-vs-composition--oop--medium]]
