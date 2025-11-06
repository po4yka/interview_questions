---
id: lang-020
title: "Detect Unused Object / Обнаружение неиспользуемых объектов"
aliases: [Detect Unused Object, Обнаружение неиспользуемых объектов]
topic: programming-languages
subtopics: [garbage-collection, memory-management, references]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, q-garbage-collector-basics--programming-languages--medium, q-how-system-knows-weakreference-can-be-cleared--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, garbage-collection, kotlin, memory-management, programming-languages, weak-references]
---

# Вопрос (RU)
> Как по объекту понять что он не используется?

# Question (EN)
> How to detect that an object is no longer used?

---

## Ответ (RU)

Используйте WeakReference для определения был ли объект освобожден сборщиком мусора. Также проверьте отсутствие сильных ссылок и используйте ObjectWatcher из LeakCanary для отслеживания.

Все примеры кода из английской версии применимы и к русской версии.

---

## Answer (EN)

**Methods to detect unused objects:**

**1. WeakReference**

```kotlin
import java.lang.ref.WeakReference

class Example {
    var data: Data? = Data()
    private val weakRef = WeakReference(data)

    fun checkIfCollected() {
        data = null  // Remove strong reference

        System.gc()  // Suggest GC (not guaranteed)

        if (weakRef.get() == null) {
            println("Object was garbage collected")
        } else {
            println("Object still in memory")
        }
    }
}
```

**2. LeakCanary ObjectWatcher**

```kotlin
// In Android app
class MyFragment : Fragment() {
    override fun onDestroy() {
        super.onDestroy()

        // LeakCanary watches for leaks
        AppWatcher.objectWatcher.watch(
            watchedObject = this,
            description = "MyFragment should be destroyed"
        )
    }
}
```

**3. Check for Strong References**

Object is unused when:
- No local variables reference it
- No static fields reference it
- No other objects reference it
- Only WeakReferences exist

**Example:**

```kotlin
data class User(val name: String)

fun testGarbageCollection() {
    var user: User? = User("John")
    val weakRef = WeakReference(user)

    println("Before: ${weakRef.get()}")  // User(name=John)

    user = null  // Remove strong reference
    System.gc()

    println("After: ${weakRef.get()}")   // null (if collected)
}
```

**Memory Profiler (Android Studio):**

1. Capture heap dump
2. Find object instances
3. Check references
4. Identify if object should be collected

**Summary:**

- Use **WeakReference** to check if GC collected object
- Use **LeakCanary** for automatic leak detection in Android
- Ensure **no strong references** exist for object to be collected

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-proxy-pattern--design-patterns--medium]]
-
-
