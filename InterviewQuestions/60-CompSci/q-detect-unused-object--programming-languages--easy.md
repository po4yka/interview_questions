---
id: 20251012-1227111127
title: "Detect Unused Object / Обнаружение неиспользуемых объектов"
topic: computer-science
difficulty: easy
status: draft
moc: moc-compSci
related: [q-proxy-pattern--design-patterns--medium, q-abstract-factory-pattern--design-patterns--medium, q-command-pattern--design-patterns--medium]
created: 2025-10-15
tags:
  - garbage-collection
  - kotlin
  - leakcanary
  - memory-management
  - programming-languages
  - weak-reference
  - weak-references
---
# Как по объекту понять что он не используется?

# Question (EN)
> How to detect that an object is no longer used?

# Вопрос (RU)
> Как по объекту понять что он не используется?

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
- - No local variables reference it
- - No static fields reference it
- - No other objects reference it
- - Only WeakReferences exist

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

---

## Ответ (RU)

Используйте WeakReference для определения был ли объект освобожден сборщиком мусора. Также проверьте отсутствие сильных ссылок и используйте ObjectWatcher из LeakCanary для отслеживания.

## Related Questions

- [[q-proxy-pattern--design-patterns--medium]]
- [[q-abstract-factory-pattern--design-patterns--medium]]
- [[q-command-pattern--design-patterns--medium]]
