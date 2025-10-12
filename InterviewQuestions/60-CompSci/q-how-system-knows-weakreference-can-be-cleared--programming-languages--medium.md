---
tags:
  - garbage-collection
  - jvm
  - kotlin
  - memory-management
  - programming-languages
  - weak-reference
  - weak-references
difficulty: medium
status: draft
---

# Как система понимает, что WeakReference можно очистить?

# Question (EN)
> How does the system know that WeakReference can be cleared?

# Вопрос (RU)
> Как система понимает, что WeakReference можно очистить?

---

## Answer (EN)

The system uses the **garbage collector (GC)** to determine when a WeakReference can be cleared.

**Key Principle:**

WeakReference can be cleared when the referenced object is **reachable ONLY through weak references** (no strong references).

**How It Works:**

**1. GC Runs:**
```kotlin
import java.lang.ref.WeakReference

val data = Data()  // Strong reference
val weakRef = WeakReference(data)

// data is reachable through strong reference
// weakRef.get() != null GOOD
```

**2. Strong References Removed:**
```kotlin
val weakRef = WeakReference(Data())

// No strong reference to Data object
// GC can clear it

System.gc()  // Suggest GC run

// weakRef.get() == null - (may be cleared)
```

**GC Algorithm for Weak References:**

```
1. Mark Phase:
   - Find all objects reachable through STRONG references
   - Mark them as "strongly reachable"

2. Weak Reference Phase:
   - For each WeakReference:
     - If referenced object is NOT strongly reachable:
       → Clear the WeakReference (set to null)

3. Sweep Phase:
   - Delete unmarked objects
```

**Example:**

```kotlin
class Cache {
    val weakCache = mutableMapOf<String, WeakReference<Data>>()

    fun put(key: String, value: Data) {
        weakCache[key] = WeakReference(value)
    }

    fun get(key: String): Data? {
        val weakRef = weakCache[key]
        val data = weakRef?.get()

        if (data == null) {
            // Object was garbage collected
            weakCache.remove(key)
        }

        return data
    }
}

fun example() {
    val cache = Cache()

    var data: Data? = Data()
    cache.put("key1", data!!)

    println(cache.get("key1"))  // Data object GOOD

    data = null  // Remove strong reference

    System.gc()  // Suggest GC

    println(cache.get("key1"))  // null - (GC cleared it)
}
```

**Strong vs Weak References:**

```kotlin
// Scenario 1: Strong reference exists
val strongRef = Data()
val weakRef = WeakReference(strongRef)

// GC runs:
// 1. strongRef keeps Data alive
// 2. weakRef.get() returns Data GOOD

// Scenario 2: No strong reference
val weakRef = WeakReference(Data())

// GC runs:
// 1. No strong reference to Data
// 2. GC clears WeakReference
// 3. weakRef.get() returns null BAD
```

**Reachability States:**

| Object State | Strong Ref | Weak Ref | GC Action |
|-------------|------------|----------|-----------|
| Strongly reachable | - Yes | Optional | Keep object |
| Weakly reachable | - No | - Yes | Clear WeakRef, GC object |
| Unreachable | - No | - No | GC object |

**Practical Example:**

```kotlin
class ImageCache {
    private val cache = mutableMapOf<String, WeakReference<Bitmap>>()

    fun get(url: String): Bitmap? {
        return cache[url]?.get()?.also {
            println("Cache hit!")
        } ?: run {
            println("Cache miss (GC cleared)")
            null
        }
    }

    fun put(url: String, bitmap: Bitmap) {
        cache[url] = WeakReference(bitmap)
    }
}

// Usage:
val imageCache = ImageCache()
var bitmap: Bitmap? = loadBitmap()

imageCache.put("url", bitmap!!)
// bitmap is strongly held → cache works

bitmap = null  // Remove strong reference
System.gc()

// imageCache.get("url") returns null
// GC cleared WeakReference
```

**Summary:**

The GC determines WeakReference can be cleared when:
- Object is **NOT strongly reachable**
- Object is **ONLY weakly reachable**
- GC run occurs (mark & sweep)

---

## Ответ (RU)

Система определяет, что WeakReference можно очистить, используя механизм сборщика мусора. Если объект достижим только через слабые ссылки (нет сильных ссылок), GC очищает WeakReference.

