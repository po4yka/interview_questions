---
id: "20251025-110312"
title: "Memory Management / Управление Памятью"
aliases: ["Garbage Collection", "GC", "Heap", "Memory Management", "Stack", "Управление Памятью"]
summary: "How applications allocate, use, and free memory resources"
topic: "performance"
subtopics: ["garbage-collection", "jvm", "memory"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-performance"
related: [c-memory-leaks, c-memory-optimization, c-memory-profiler, c-weak-references, c-android-profiler]
created: "2025-10-25"
updated: "2025-10-25"
tags: ["concept", "difficulty/medium", "garbage-collection", "jvm", "memory", "performance"]
date created: Saturday, October 25th 2025, 11:05:40 am
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Memory Management / Управление Памятью

## Summary (EN)

Memory management is the process of controlling and coordinating how an application uses computer memory. In Android and JVM-based systems, memory is divided into stack and heap regions, with automatic garbage collection handling most memory deallocation. Understanding memory management is crucial for preventing memory leaks, optimizing performance, and avoiding OutOfMemory errors.

## Краткое Описание (RU)

Управление памятью - это процесс контроля и координации использования компьютерной памяти приложением. В Android и JVM-системах память разделена на стек и кучу, при этом автоматическая сборка мусора обрабатывает большую часть освобождения памяти. Понимание управления памятью критически важно для предотвращения утечек памяти, оптимизации производительности и избежания ошибок OutOfMemory.

## Key Points (EN)

- **Stack**: Fast, automatic memory for local variables and method calls
- **Heap**: Slower, managed memory for objects and dynamic allocation
- **Garbage Collection**: Automatic reclamation of unused memory
- **Memory Leaks**: Objects that cannot be garbage collected despite being unused
- **Strong/Weak/Soft References**: Different reference types affect GC behavior
- **Memory Profiling**: Tools to identify and fix memory issues
- **Android specifics**: Activity lifecycle affects memory management

## Ключевые Моменты (RU)

- **Стек**: Быстрая автоматическая память для локальных переменных и вызовов методов
- **Куча**: Более медленная управляемая память для объектов и динамического выделения
- **Сборка мусора**: Автоматическое освобождение неиспользуемой памяти
- **Утечки памяти**: Объекты, которые не могут быть собраны GC несмотря на неиспользование
- **Сильные/Слабые/Мягкие ссылки**: Различные типы ссылок влияют на поведение GC
- **Профилирование памяти**: Инструменты для выявления и исправления проблем с памятью
- **Специфика Android**: Жизненный цикл Activity влияет на управление памятью

## Memory Regions

### Stack Memory

```kotlin
fun calculateSum(a: Int, b: Int): Int {
    // All these variables are allocated on the stack
    val sum = a + b           // Primitive value on stack
    val result = sum * 2      // Another primitive on stack
    return result
    // Stack frame is automatically cleaned up when function returns
}
```

**Characteristics**:
- Fast allocation and deallocation (LIFO - Last In First Out)
- Automatic memory management
- Limited size (typically 1-2 MB per thread)
- Stores: primitive values, local variables, method call frames
- StackOverflowError when exceeded

### Heap Memory

```kotlin
class User(val name: String, val age: Int)

fun createUser(): User {
    // Object is allocated on the heap
    val user = User("John", 30)  // Reference on stack, object on heap
    return user
    // Object remains on heap even after function returns
    // Will be garbage collected when no longer referenced
}
```

**Characteristics**:
- Slower allocation than stack
- Managed by garbage collector
- Larger size (configurable, typically hundreds of MB)
- Stores: objects, arrays, class instances
- OutOfMemoryError when exceeded

## Garbage Collection (GC)

### How GC Works

```kotlin
fun processData() {
    val data = LargeObject()  // Allocated on heap

    // Use data
    data.process()

    // When function ends, 'data' reference is removed
    // Object becomes eligible for garbage collection
    // GC will eventually reclaim this memory
}
```

### GC Generations

**Young Generation**:
- Newly created objects
- Frequent, fast GC cycles (Minor GC)
- Most objects die young

**Old Generation**:
- Long-lived objects promoted from young generation
- Infrequent, slower GC cycles (Major GC)
- Contains objects that survived multiple GC cycles

**Permanent Generation** (Java 7) / **Metaspace** (Java 8+):
- Class metadata, static fields
- Rarely collected

### GC Algorithms in Android

```kotlin
// Android uses different GC algorithms based on version

// Concurrent Mark-Sweep (CMS) - older Android
// - Runs concurrently with app
// - Minimizes pause times
// - Can fragment memory

// Generational Concurrent Copying (GCC) - Android 5.0+
// - Moves objects during collection
// - Reduces fragmentation
// - Shorter pause times

// Low Memory Killer (LMK)
// - Android system service
// - Kills entire processes to free memory
// - Based on process priority (oom_adj scores)
```

## Memory Leaks

### Common Leak Patterns

**1. Static References to Context**
```kotlin
// BAD: Memory leak
class DatabaseHelper {
    companion object {
        private var context: Context? = null  // Leaks entire Activity

        fun init(context: Context) {
            this.context = context
        }
    }
}

// GOOD: Use Application context
class DatabaseHelper {
    companion object {
        private var context: Context? = null

        fun init(context: Context) {
            this.context = context.applicationContext  // Won't leak
        }
    }
}
```

**2. Non-static Inner Classes**
```kotlin
// BAD: Inner class holds reference to outer Activity
class MainActivity : AppCompatActivity() {
    inner class AsyncTask {
        fun doWork() {
            // This implicitly references MainActivity
            // If task runs after Activity destroyed -> leak
        }
    }
}

// GOOD: Use static class with WeakReference
class MainActivity : AppCompatActivity() {
    class AsyncTask(activity: MainActivity) {
        private val activityRef = WeakReference(activity)

        fun doWork() {
            activityRef.get()?.let { activity ->
                // Use activity safely
            }
        }
    }
}
```

**3. Listeners and Callbacks**
```kotlin
// BAD: Listener holds reference to Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        SomeService.addListener(object : Listener {
            override fun onEvent() {
                // Implicitly references MainActivity
            }
        })
        // Listener is never removed -> leak
    }
}

// GOOD: Remove listeners in onDestroy
class MainActivity : AppCompatActivity() {
    private val listener = object : Listener {
        override fun onEvent() {
            handleEvent()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        SomeService.addListener(listener)
    }

    override fun onDestroy() {
        SomeService.removeListener(listener)
        super.onDestroy()
    }
}
```

## Reference Types

### Strong References (Default)

```kotlin
val user = User("John")  // Strong reference
// Object cannot be GC'd while 'user' reference exists
```

### Weak References

```kotlin
import java.lang.ref.WeakReference

val user = User("John")
val weakRef = WeakReference(user)

// Get object from weak reference
weakRef.get()?.let { user ->
    // Use user
}

// After setting user = null, object can be GC'd
// even if weakRef still exists
```

**Use cases**:
- Caching without preventing GC
- Avoiding memory leaks in callbacks

### Soft References

```kotlin
import java.lang.ref.SoftReference

val softRef = SoftReference(largeObject)

// Object will be kept until memory is needed
// JVM only clears soft references when memory pressure is high
```

**Use cases**:
- Memory-sensitive caches
- Image caching

### Lifecycle-Aware References

```kotlin
class MyViewModel : ViewModel() {
    private var repository: Repository? = null

    override fun onCleared() {
        // Clean up resources when ViewModel is destroyed
        repository = null
        super.onCleared()
    }
}
```

## Memory Profiling

### Using Android Profiler

```kotlin
// Trigger GC manually for profiling
System.gc()

// Dump heap for analysis
Debug.dumpHprofData("/sdcard/heap_dump.hprof")
```

### LeakCanary Integration

```kotlin
// In build.gradle
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}

// LeakCanary automatically detects memory leaks in debug builds
// No additional code needed - shows notification when leak detected
```

### Memory Allocation Tracking

```kotlin
// Monitor allocations
Debug.startAllocCounting()

// ... run code ...

val allocations = Debug.getThreadAllocCount()
val allocatedSize = Debug.getThreadAllocSize()

Debug.stopAllocCounting()

Log.d("Memory", "Allocations: $allocations, Size: $allocatedSize bytes")
```

## Best Practices

### 1. Context Management

```kotlin
// Use appropriate context
class MyClass(context: Context) {
    // For long-lived objects
    private val appContext = context.applicationContext

    // For short-lived operations
    private val activityContext = context  // Only if needed
}
```

### 2. Lifecycle Awareness

```kotlin
class MyObserver : LifecycleObserver {
    @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
    fun cleanup() {
        // Release resources
    }
}

class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(MyObserver())
    }
}
```

### 3. Bitmap Management

```kotlin
// Bitmaps consume significant memory
fun loadBitmap(path: String): Bitmap? {
    return try {
        BitmapFactory.decodeFile(path)?.also { bitmap ->
            // Recycle when no longer needed
            registerBitmapForRecycling(bitmap)
        }
    } catch (e: OutOfMemoryError) {
        System.gc()
        null
    }
}

fun recycleBitmap(bitmap: Bitmap) {
    if (!bitmap.isRecycled) {
        bitmap.recycle()
    }
}
```

### 4. Collection Management

```kotlin
// Clear collections when done
val cache = mutableListOf<Data>()

fun clearCache() {
    cache.clear()
    // Helps GC reclaim memory faster
}

// Use appropriate collection types
val limitedCache = object : LinkedHashMap<String, Data>(
    initialCapacity = 100,
    loadFactor = 0.75f,
    accessOrder = true
) {
    override fun removeEldestEntry(eldest: Map.Entry<String, Data>): Boolean {
        return size > MAX_CACHE_SIZE
    }
}
```

## Use Cases

### When to Focus on Memory Management

- **Large datasets**: Processing big collections or files
- **Image-heavy apps**: Photo galleries, image editors
- **Long-running operations**: Background services, downloads
- **Caching**: Implementing memory caches
- **Performance optimization**: Reducing GC pressure
- **Low-memory devices**: Supporting budget Android devices

### When Less Critical

- **Simple apps**: Basic CRUD applications
- **Short-lived processes**: Quick operations
- **Modern devices**: Devices with abundant RAM

## Trade-offs

**Pros of Automatic GC**:
- **Simplicity**: No manual memory management needed
- **Safety**: Prevents use-after-free bugs
- **Productivity**: Focus on business logic, not memory details

**Cons of Automatic GC**:
- **Pause times**: GC can cause UI jank
- **Unpredictable**: Cannot control when GC runs
- **Memory overhead**: GC requires extra memory
- **Memory leaks still possible**: Due to retained references

**Manual Memory Management Alternatives**:
- **Native code (C/C++)**: Direct memory control via JNI
- **Object pools**: Reuse objects to reduce allocations
- **Off-heap storage**: Store data outside JVM heap

## Monitoring and Debugging

### Memory Leak Indicators

```kotlin
// Signs of memory leaks:
// 1. Increasing memory usage over time
// 2. OutOfMemoryError crashes
// 3. Slow GC cycles
// 4. Multiple instances of same Activity in heap dump

// Tools:
// - Android Studio Profiler
// - LeakCanary
// - MAT (Memory Analyzer Tool)
// - adb shell dumpsys meminfo <package>
```

### Heap Dump Analysis

```bash
# Capture heap dump
adb shell am dumpheap <package> /sdcard/heap.hprof

# Pull heap dump
adb pull /sdcard/heap.hprof

# Analyze with Android Studio or MAT
# Look for:
# - Dominator tree (which objects retain most memory)
# - Duplicate strings/objects
# - Leaked Activities/Fragments
# - Large collections
```

## Related Concepts

- [[c-lifecycle]]
- [[c-coroutines]]
- [[c-software-design-patterns]]

## References

- [Android Memory Management Overview](https://developer.android.com/topic/performance/memory-overview)
- [Investigate RAM usage with Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Java Garbage Collection Basics](https://www.oracle.com/webfolder/technetwork/tutorials/obe/java/gc01/index.html)
- [Android Performance Patterns - Memory](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)
- "Java Performance: The Definitive Guide" by Scott Oaks
