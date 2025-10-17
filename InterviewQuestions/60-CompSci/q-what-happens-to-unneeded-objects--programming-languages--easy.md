---
id: "20251015082237156"
title: "What Happens To Unneeded Objects / Что происходит с ненужными объектами"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - automatic-memory
  - garbage-collection
  - jvm
  - kotlin
  - memory-management
  - programming-languages
---
# Что происходит с объектами, которые больше не нужны?

# Question (EN)
> What happens to objects that are no longer needed?

# Вопрос (RU)
> Что происходит с объектами, которые больше не нужны?

---

## Answer (EN)

Objects that are no longer needed are **automatically deleted by the garbage collector (GC)**, freeing memory for new objects.

**Process:**

1. Object becomes **unreachable** (no references)
2. **Garbage collector** identifies it as garbage
3. Object is **automatically deleted**
4. **Memory is freed**
5. No manual intervention required

**Example:**

```kotlin
fun example() {
    val user = User("John")  // Object created

    // user is used here
    println(user.name)

    // Function ends
    // user goes out of scope
    // User object has no references
    // → Automatically garbage collected
}
```

**Automatic Memory Management:**

```kotlin
fun createManyObjects() {
    repeat(1000) {
        val temp = Data()  // Created
        // Immediately unreachable after iteration
        // GC will collect these objects automatically
    }
    // No need to manually delete objects!
}
```

**Kotlin/Java vs C/C++:**

**C++ (Manual):**
```cpp
// Must manually free memory
Data* data = new Data();
delete data;  // Manual cleanup required!
// Forget to delete → memory leak
```

**Kotlin (Automatic):**
```kotlin
val data = Data()
// Automatically freed when unreachable
// No manual cleanup needed!
```

**When Objects Are Collected:**

```kotlin
class Example {
    fun demo() {
        var obj: Data? = Data()  // Object created

        // obj is reachable → Safe from GC

        obj = null  // No more references

        // Object is now unreachable
        // Will be garbage collected (eventually)
        // Memory freed automatically
    }
}
```

**Background Process:**

```kotlin
// Developer code:
fun processData() {
    val temp = LargeData()
    // Use temp
}  // temp goes out of scope

// Behind the scenes:
// 1. GC runs periodically (background thread)
// 2. Finds unreachable objects
// 3. Deletes them
// 4. Frees memory
// All automatic, no manual work!
```

**Benefits:**

- **No manual memory management**
- **No memory leaks** (if code is correct)
- **Developer focuses on logic**, not memory
- **Safer** than manual memory management

**How It Works:**

```
1. Application creates objects
2. GC monitors memory usage
3. When memory pressure increases:
   - GC pauses application briefly
   - Identifies unreachable objects
   - Deletes them
   - Frees memory
4. Application resumes
```

**Example with Timing:**

```kotlin
fun main() {
    println("Creating objects...")

    repeat(1000000) {
        val data = ByteArray(1024)  // 1KB each
        // Immediately unreachable
    }

    println("Objects created")
    println("GC will collect them automatically")

    // Force GC (for demonstration only)
    System.gc()

    println("Memory freed!")
}
```

**Summary:**

Unneeded objects (no active references) are:
- Considered **garbage**
- **Automatically deleted** by garbage collector
- **Memory is freed** for reuse
- **No manual cleanup** required
- Process runs in **background**

This is automatic memory management in Kotlin/Java!

---

## Ответ (RU)

Объекты, которые больше не имеют активных ссылок, считаются мусором. Такие объекты автоматически удаляются сборщиком мусора, освобождая память для новых объектов. Это происходит в фоновом режиме и не требует прямого вмешательства разработчика.

