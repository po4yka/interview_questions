---
id: lang-080
title: "Garbage Collector Roots / Корни Garbage Collector"
aliases: [Garbage Collector Roots, Корни Garbage Collector]
topic: kotlin
subtopics: [garbage-collection, jvm, memory-management]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, q-garbage-collector-basics--programming-languages--medium, q-garbage-collector-definition--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [difficulty/medium, garbage-collection, jvm, kotlin, memory-management, programming-languages]
---
# Вопрос (RU)
> Что такое Garbage Collector Roots?

---

# Question (EN)
> What are Garbage Collector Roots?

## Ответ (RU)

**Garbage Collector (GC) Roots** — это набор корневых ссылок, от которых сборщик мусора (в трассирующих GC, как в JVM) начинает обход графа объектов, чтобы определить, какие объекты достижимы (живы), а какие можно собрать.

**Как работает трассирующий GC (упрощённо):**

1. Начать обход от всех GC Roots
2. Пометить все объекты, достижимые по цепочкам ссылок
3. Освободить (sweep/compact) объекты, которые не были помечены (недостижимы)

**Объект достижим, если к нему можно получить доступ из любого GC Root через цепочку ссылок.**

Важно: GC Root — это не "любой объект", а конкретные корневые ссылки среды выполнения (стек, статические поля, и т.п.), от которых начинается поиск.

**Типы GC Roots (на JVM, в контексте Kotlin/Java):**

**1. Локальные переменные и параметры в активных фреймах стека**
```kotlin
fun example() {
    val user = User("John")  // Ссылка в стеке потока учитывается как GC Root
    // user достижим, пока фрейм метода активен и ссылка доступна
}
// После выхода из метода стековый фрейм уничтожается, ссылка перестаёт быть корнем
```

**2. Активные потоки и их стеки**
```kotlin
Thread.start {
    val data = Data()  // Ссылки из активного стека потока считаются корнями
    // data достижим, пока поток и этот фрейм стека активны
}
```

**3. Статические поля (JVM), в том числе через `object` / `companion object` в Kotlin**
```kotlin
object AppConfig {
    val instance = Config()  // Ссылка хранится в статическом поле на JVM и служит GC Root
    // Ссылка остаётся корнем, пока класс загружен и поле доступно
}
```

**4. JNI ссылки**
```kotlin
// Нативный код может хранить ссылки на объекты JVM.
// Глобальные JNI-ссылки (и некоторые другие управляемые формы ссылок)
// учитываются как GC Roots до тех пор, пока они не будут освобождены.
external fun nativeMethod()
```

**Пример:**

```kotlin
class Node(val value: Int, var next: Node? = null)

fun main() {
    val root = Node(1)  // Ссылка root в стеке main — часть GC Roots
    root.next = Node(2)
    root.next?.next = Node(3)

    // Достижимые: root, Node(2), Node(3)
    // Все живы, так как достижимы по ссылкам, начиная от GC Root (root в стеке)

    root.next = null
    // Теперь цепочка обрывается: бывшие Node(2) и Node(3) (если на них больше нет ссылок)
    // становятся недостижимыми и могут быть собраны GC.
}
```

**Пример логической утечки памяти:**

```kotlin
object Cache {
    private val data = mutableListOf<Data>()  // Ссылка на список хранится в статическом поле (через object)

    fun add(item: Data) {
        data.add(item)
        // Если элементы никогда не удаляются и нет других ссылок, список остаётся достижимым как GC Root-цепочка,
        // поэтому объекты Data не будут собраны — фактическая утечка памяти на уровне логики приложения.
    }
}
```

**Категории:**

| Тип GC Root                   | Время жизни                             | Пример                                |
|------------------------------|------------------------------------------|----------------------------------------|
| Локальные переменные в стеке | Пока выполняется соответствующий фрейм  | `val x = User()` в активном методе     |
| Статические поля             | Пока класс загружен                      | `companion object { val x = ... }`     |
| Активные потоки              | Пока поток выполняется                   | Переменные в стеке потока              |
| JNI ссылки                   | Пока JNI-ссылка не освобождена          | Глобальные JNI ссылки                  |

**Резюме:**

GC Roots — это **корневые ссылки среды выполнения**, от которых трассирующий GC начинает поиск. Объекты, достижимые из GC Roots, считаются **живыми**. Объекты, которые не достижимы из ни одного корня, считаются **мусором** и могут быть собраны. Понимание GC Roots важно для предотвращения логических утечек памяти и оптимизации использования памяти.

## Answer (EN)

**Garbage Collector (GC) Roots** are the set of root references from which a tracing garbage collector (such as the JVM GC) starts traversing the object graph to determine which objects are reachable (alive) and which can be collected.

**How a tracing GC works (simplified):**

1. Start traversal from all GC Roots
2. Mark all objects reachable via chains of references
3. Sweep/compact objects that were not marked (unreachable)

**An object is reachable if it can be accessed from any GC Root through a chain of references.**

Important: a GC Root is not "any object"; it is a special root reference managed by the runtime (stack, static fields, etc.) from which reachability analysis starts.

**Types of GC Roots (on the JVM, in Kotlin/Java context):**

**1. Local Variables & Parameters in Active Stack Frames**
```kotlin
fun example() {
    val user = User("John")  // The reference in the thread's stack frame is treated as part of GC Roots
    // user is reachable while the frame is active and the reference is live
}
// After the method exits, the frame is removed and this reference is no longer a root
```

**2. Active Thread Stack Frames / Threads**
```kotlin
Thread.start {
    val data = Data()  // References from an active thread stack are considered roots
    // data is reachable while the thread (and this frame) is active
}
```

**3. Static Fields (JVM), including Kotlin `object` / `companion object`**
```kotlin
object AppConfig {
    val instance = Config()  // Stored in a JVM static field; that static reference is a GC Root
    // The reference remains a root while the class is loaded and the field is present
}
```

**4. JNI References**
```kotlin
// Native code can hold references to JVM objects.
// Global (and certain managed) JNI references are treated as GC Roots
// until they are explicitly released.
external fun nativeMethod()
```

**Example:**

```kotlin
class Node(val value: Int, var next: Node? = null)

fun main() {
    val root = Node(1)  // The `root` variable on the main stack acts as a root reference
    root.next = Node(2)
    root.next?.next = Node(3)

    // Reachable: root, Node(2), Node(3)
    // All are kept alive because they are reachable from a GC Root reference (`root`)

    root.next = null
    // Now the chain is broken: Node(2) and Node(3) (assuming no other references)
    // become unreachable and can be garbage collected.
}
```

**Memory Leak Example (logical leak):**

```kotlin
object Cache {
    private val data = mutableListOf<Data>()  // The list reference is in a JVM static field (via object)

    fun add(item: Data) {
        data.add(item)
        // If items are never removed and there are no other constraints,
        // they remain reachable through this root chain → effective memory leak at app logic level.
    }
}
```

**Categories:**

| GC Root Type        | Lifetime                           | Example                              |
|---------------------|------------------------------------|--------------------------------------|
| Local variables     | While the stack frame is executing | `val x = User()` in an active method |
| Static fields       | While the class is loaded          | `companion object { val x = ... }`   |
| Active threads      | While the thread is running        | Thread stack variables                |
| JNI references      | While the JNI ref is not released  | JNI global references                 |

**Summary:**

GC Roots are the **runtime root references** from which a tracing garbage collector starts reachability analysis. Objects reachable from GC Roots are **kept alive**. Objects not reachable from any root are **garbage** and may be collected.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы применили это на практике?
- Каковы распространенные ошибки и подводные камни?

## Ссылки (RU)

- [[c-garbage-collection]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-extension-properties--programming-languages--medium]]
- [[q-java-lambda-type--programming-languages--easy]]
- [[q-inheritance-vs-composition--oop--medium]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [[c-garbage-collection]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-extension-properties--programming-languages--medium]]
- [[q-java-lambda-type--programming-languages--easy]]
- [[q-inheritance-vs-composition--oop--medium]]
