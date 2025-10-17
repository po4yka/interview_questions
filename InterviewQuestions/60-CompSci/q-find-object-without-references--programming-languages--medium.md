---
id: "20251015082237191"
title: "Find Object Without References / Поиск объектов без ссылок"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags: - debugging
  - heap-dump
  - kotlin
  - mat
  - memory-management
  - memory-profiler
  - programming-languages
---
# Как найти объект, если на него нет ссылок?

# Question (EN)
> How to find an object if there are no references to it?

# Вопрос (RU)
> Как найти объект, если на него нет ссылок?

---

## Answer (EN)

Finding objects without references is challenging because they're normally garbage collected. However, you can analyze them using **memory profiling tools**.

**Methods:**

**1. Heap Dump (Android Studio)**

```
1. Open Android Profiler
2. Select Memory tab
3. Click "Dump Java heap"
4. Wait for heap dump to load
```

**2. Analyze with Android Studio**

- View "Unreachable objects"
- Check "Shallow Size" and "Retained Size"
- Inspect object instances
- Find objects that should have been GC'd

**3. Memory Analyzer Tool (MAT)**

```bash

# Export heap dump
adb shell am dumpheap <package-name> /data/local/tmp/heap.hprof
adb pull /data/local/tmp/heap.hprof

# Open in MAT

# Eclipse Memory Analyzer
```

**MAT Features:**

- **Histogram**: Show all object instances
- **Dominator Tree**: Find memory-consuming objects
- **Leak Suspects**: Automatically detect leaks
- **Path to GC Roots**: Show why object is still in memory

**Example Analysis:**

```kotlin
// Suspected leak
class Fragment {
    private var callback: (() -> Unit)? = null

    fun setCallback(cb: () -> Unit) {
        callback = cb  // Potential leak!
    }

    override fun onDestroy() {
        // Forgot to clear callback!
        // callback = null
    }
}
```

**In Memory Profiler:**

```
1. Find Fragment instances
2. Check "Depth" (should be 0 after destroy)
3. If depth > 0, Fragment is leaked
4. Click "References" to see what holds it
5. Follow chain to find leak source
```

**LeakCanary (Automatic)**

```kotlin
// build.gradle
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.x'
}

// Automatically detects and reports leaks
// No code changes needed!
```

**Manual Check:**

```kotlin
import java.lang.ref.WeakReference

class LeakDetector {
    private val trackedObjects = mutableListOf<WeakReference<Any>>()

    fun track(obj: Any) {
        trackedObjects.add(WeakReference(obj))
    }

    fun checkLeaks() {
        System.gc()

        trackedObjects.forEach { ref ->
            if (ref.get() != null) {
                println("Potential leak: ${ref.get()}")
            }
        }
    }
}
```

**Common Tools:**

| Tool | Platform | Use Case |
|------|----------|----------|
| Android Studio Profiler | Android | Real-time monitoring |
| MAT | Android/JVM | Deep heap analysis |
| LeakCanary | Android | Automatic leak detection |
| VisualVM | JVM | Desktop JVM profiling |

**Summary:**

- Capture **heap dump**
- Analyze with **Memory Profiler** or **MAT**
- Look for **unreachable objects**
- Use **LeakCanary** for automatic detection
- Find **dominators** and **GC Root paths**

---

## Ответ (RU)

Создайте дамп памяти в Android Studio ("Dump Java heap"). Используйте Memory Analyzer Tool (MAT) для анализа. Ищите "Unreachable objects" и "Dominators". LeakCanary автоматически обнаруживает утечки.

