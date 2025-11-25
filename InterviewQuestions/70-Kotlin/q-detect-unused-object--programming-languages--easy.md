---
id: lang-020
title: "Detect Unused Object / Обнаружение неиспользуемых объектов"
aliases: [Detect Unused Object, Обнаружение неиспользуемых объектов]
topic: kotlin
subtopics: [garbage-collection, memory-management, references]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, q-garbage-collector-basics--programming-languages--medium, q-how-system-knows-weakreference-can-be-cleared--programming-languages--medium]
created: 2024-10-15
updated: 2025-11-09
tags: [difficulty/easy, garbage-collection, kotlin, memory-management, programming-languages, weak-references]
date created: Friday, October 31st 2025, 6:29:22 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---

# Вопрос (RU)
> Как по объекту понять что он не используется?

# Question (EN)
> How to detect that an object is no longer used?

---

## Ответ (RU)

Строго и надёжно определить "по самому объекту", что он больше не используется, из пользовательского кода нельзя: сборка мусора недетерминирована, а рантайм не предоставляет общего API для проверки его "живости".

Можно использовать следующие подходы для диагностики и отладки:

**1. WeakReference (наблюдение достижимости)**

```kotlin
import java.lang.ref.WeakReference

class Example {
    var data: Data? = Data()
    private val weakRef = WeakReference(data)

    fun checkIfPossiblyCollected() {
        data = null  // Убираем сильную ссылку

        System.gc()  // Подсказка GC; не гарантирует сборку

        if (weakRef.get() == null) {
            println("Объект (скорее всего) был собран GC")
        } else {
            println("Объект всё ещё сильно достижим")
        }
    }
}
```

Замечания:
- `WeakReference.get()` возвращает `null`, если объект уже очищен сборщиком мусора.
- Момент сборки мусора не гарантируется: после `System.gc()` объект может быть как собран, так и нет.
- Такой подход подходит для экспериментов и понимания поведения GC, но не для основной логики приложения.

**2. LeakCanary ObjectWatcher (Android, поиск утечек)**

```kotlin
// В Android-приложении (debug / поиск утечек)
class MyFragment : Fragment() {
    override fun onDestroy() {
        super.onDestroy()

        // LeakCanary отслеживает потенциальные утечки объектов
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyFragment должен быть уничтожен"
        )
    }
}
```

Замечания:
- ObjectWatcher используется, чтобы находить объекты, которые должны стать недостижимыми (и быть собранными), но остаются сильно достижимыми.
- Это инструмент для отладки утечек, а не универсальный рантайм-API "используется ли объект".

**3. Концептуальное правило о сильных ссылках**

Объект становится кандидатом на сборку мусора, когда (концептуально):
- на него не указывают локальные переменные активных стеков;
- на него не указывают статические поля;
- на него не указывают поля других достижимых объектов;
- на него ссылаются только `WeakReference` (или аналогичные несильные ссылки).

Именно так GC рассуждает о достижимости. Обычный код не может полно и переносимо перечислить все ссылки на произвольный объект.

**4. Практический анализ: профилировщик памяти и heap dump**

Для реального поиска утечек и "залипающих" объектов используйте инструменты профилирования памяти (Android Studio Memory Profiler, JVM-профилировщики):
- снимите heap dump;
- найдите нужные экземпляры объекта;
- изучите цепочки ссылок до GC-root;
- сделайте вывод, должны ли они быть недостижимыми (утечка) или корректно удерживаются.

**Пример (только для иллюстрации):**

```kotlin
data class User(val name: String)

fun testGarbageCollection() {
    var user: User? = User("John")
    val weakRef = WeakReference(user)

    println("Before: ${weakRef.get()}")  // Скорее всего: User(name=John)

    user = null  // Убираем сильную ссылку
    System.gc()  // Подсказка GC

    println("After: ${weakRef.get()}")   // Может стать null, если объект собран
}
```

**Итоги:**

- Нельзя детерминированно спросить из обычного кода: "этот объект уже не используется?".
- Право на сборку определяется достижимостью (отсутствием сильных ссылок).
- `WeakReference` помогает наблюдать момент, когда объект может быть собран, но поведение недетерминированно.
- Инструменты вроде LeakCanary и профилировщиков памяти — правильный путь для поиска утечек и нежелательного удержания объектов.

---

## Answer (EN)

You generally cannot reliably detect from user code that an arbitrary object is "no longer used". Garbage collection is non-deterministic and there is no general-purpose liveness API. What you can do is reason about reachability and use tooling/weak references for diagnostics.

Methods and concepts:

**1. WeakReference (for reachability observation)**

```kotlin
import java.lang.ref.WeakReference

class Example {
    var data: Data? = Data()
    private val weakRef = WeakReference(data)

    fun checkIfPossiblyCollected() {
        data = null  // Remove this strong reference

        System.gc()  // Hint to GC; does NOT guarantee collection

        if (weakRef.get() == null) {
            println("Object was (likely) garbage collected")
        } else {
            println("Object is still strongly reachable")
        }
    }
}
```

Notes:
- `WeakReference.get()` returning `null` means the referent has been cleared by the GC.
- However, the timing of GC is not guaranteed. After `System.gc()`, the object may or may not be collected.
- This pattern is suitable for experiments and understanding GC behavior, not for core application logic.

**2. LeakCanary ObjectWatcher (Android, leak detection)**

```kotlin
// In an Android app (debug / leak detection)
class MyFragment : Fragment() {
    override fun onDestroy() {
        super.onDestroy()

        // LeakCanary watches for potential leaks of objects
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyFragment should be destroyed"
        )
    }
}
```

Notes:
- ObjectWatcher is used to detect objects that should become unreachable (and thus GC-eligible) but remain strongly reachable.
- It is a debugging tool for finding leaks, not a general runtime API to check "is this object used".

**3. Conceptual rule: strong references**

An object becomes eligible for garbage collection when (conceptually):
- No local variables on live stacks reference it.
- No static fields reference it.
- No fields of other reachable objects reference it.
- It is referenced only by `WeakReference` (or similarly non-strong references).

This is how the GC reasons about reachability. Regular application code cannot fully and portably enumerate all references to an arbitrary object.

**4. Practical analysis: memory profiler and heap dump**

For real-world leak detection and stuck objects, use memory profiling tools (Android Studio Memory Profiler, JVM profilers):
- Capture a heap dump.
- Find instances of the object of interest.
- Inspect reference paths to GC roots.
- Decide whether they should be unreachable (leak) or are legitimately retained.

**Example (illustrative only):**

```kotlin
data class User(val name: String)

fun testGarbageCollection() {
    var user: User? = User("John")
    val weakRef = WeakReference(user)

    println("Before: ${weakRef.get()}")  // Likely: User(name=John)

    user = null  // Remove this strong reference
    System.gc()  // Hint

    println("After: ${weakRef.get()}")   // May be null if collected
}
```

**Summary:**

- You cannot deterministically query "is this object unused" from normal code.
- GC eligibility is based on reachability (absence of strong references).
- `WeakReference` can help observe when an object becomes collectable, but behavior is non-deterministic.
- Tools like LeakCanary (Android) and memory profilers are the right way to detect leaks and unintended object retention.

## Дополнительные Вопросы (RU)

- В чём ключевые отличия между принципами работы GC и ссылок в Kotlin/JVM и в других платформах?
- В каких практических сценариях вы бы использовали `WeakReference` или подобные механизмы?
- Каковы типичные ошибки при интерпретации поведения GC и работе со слабыми ссылками?

## Follow-ups

- What are the key differences between GC and reference behavior in Kotlin/JVM and other platforms?
- When would you use `WeakReference` or similar mechanisms in practice?
- What are common pitfalls when interpreting GC behavior and working with weak references?

## Ссылки (RU)

- [[c-garbage-collection]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-garbage-collector-basics--programming-languages--medium]]
- [[q-how-system-knows-weakreference-can-be-cleared--programming-languages--medium]]

## Related Questions

- [[q-garbage-collector-basics--programming-languages--medium]]
- [[q-how-system-knows-weakreference-can-be-cleared--programming-languages--medium]]
