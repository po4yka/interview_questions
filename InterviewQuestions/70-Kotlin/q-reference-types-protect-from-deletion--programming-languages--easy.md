---
id: lang-052
title: "Reference Types Protect From Deletion / Типы ссылок защищают от удаления"
aliases: [Reference Types Protect From Deletion, Типы ссылок защищают от удаления]
topic: programming-languages
subtopics: [garbage-collection, jvm, memory-management]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-detect-unused-object--programming-languages--easy, q-java-marker-interfaces--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, garbage-collection, jvm, kotlin, memory-management, phantom-reference, programming-languages, references, soft-reference, strong-reference, weak-reference]
date created: Saturday, October 4th 2025, 1:22:21 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---
# Все Ли Виды Ссылок Защищают Объект От Удаления?

# Вопрос (RU)
> Все ли виды ссылок защищают объект от удаления?

---

# Question (EN)
> Do all types of references protect an object from deletion?

## Ответ (RU)

Нет, не все ссылки защищают объект от удаления. Strong Reference защищает объект, Weak Reference не защищает и позволяет удалить объект. Soft Reference удаляет объект только при нехватке памяти, а Phantom Reference используется для действий после удаления.

## Answer (EN)

**No, not all reference types protect objects from garbage collection.**

**Java/Kotlin Reference Types:**

**1. Strong Reference (Normal)** - Protects

```kotlin
val user = User("John")  // Strong reference
// Object CANNOT be garbage collected while reference exists
```

**2. Weak Reference** - Does NOT Protect

```kotlin
import java.lang.ref.WeakReference

val user = User("John")
val weakRef = WeakReference(user)

// user = null  // Remove strong reference
// Object CAN be garbage collected even though weakRef exists
```

**3. Soft Reference** WARNING: Protects Until Memory Needed

```kotlin
import java.lang.ref.SoftReference

val softRef = SoftReference(Data())
// Object kept in memory until system needs memory
// Then it CAN be garbage collected
```

**4. Phantom Reference** - Does NOT Protect

```kotlin
import java.lang.ref.PhantomReference
import java.lang.ref.ReferenceQueue

val queue = ReferenceQueue<User>()
val phantomRef = PhantomReference(User("John"), queue)
// Used for cleanup actions AFTER object is GC'd
// Object CAN be garbage collected
```

**Comparison:**

| Reference Type | Protects from GC? | Use Case |
|----------------|-------------------|----------|
| **Strong** | - Yes | Normal references |
| **Soft** | WARNING: Until low memory | Caches |
| **Weak** | - No | Break strong reference cycles |
| **Phantom** | - No | Post-GC cleanup |

**Examples:**

**Strong Reference:**
```kotlin
class Cache {
    private val data = mutableListOf<Data>()  // Strong refs

    fun add(item: Data) {
        data.add(item)  // Item protected from GC
    }
}
```

**Weak Reference (Cache):**
```kotlin
import java.lang.ref.WeakReference

class WeakCache {
    private val cache = mutableMapOf<String, WeakReference<Data>>()

    fun put(key: String, value: Data) {
        cache[key] = WeakReference(value)
    }

    fun get(key: String): Data? {
        return cache[key]?.get()  // May return null if GC'd
    }
}
```

**Soft Reference (Image Cache):**
```kotlin
import java.lang.ref.SoftReference

class ImageCache {
    private val cache = mutableMapOf<String, SoftReference<Bitmap>>()

    fun get(url: String): Bitmap? {
        return cache[url]?.get()  // Cleared when memory low
    }
}
```

**Memory Behavior:**

```kotlin
fun example() {
    val strongData = Data()         // - Always in memory
    val weakData = WeakReference(Data())   // - Can be GC'd anytime
    val softData = SoftReference(Data())   // WARNING: GC'd when memory low

    System.gc()  // Suggest garbage collection

    println(weakData.get())  // Likely null (GC'd)
    println(softData.get())  // Probably still there (unless low memory)
    println(strongData)      // Definitely still there
}
```

**Summary:**

- **Strong Reference**: Protects object (normal variables)
- **Weak Reference**: Does NOT protect (GC can collect anytime)
- **Soft Reference**: Protects until low memory
- **Phantom Reference**: Does NOT protect (for post-GC cleanup)

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-detect-unused-object--programming-languages--easy]]
- [[q-java-marker-interfaces--programming-languages--medium]]
-
