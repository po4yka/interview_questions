---
id: "20251015082237442"
title: "Memory Leaks Definition / Определение утечек памяти"
topic: android
difficulty: easy
status: draft
created: 2025-10-13
tags: [android/memory-management, garbage-collection, memory-leaks, memory-management, performance, difficulty/easy]
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---
# Что такое утечки памяти?

**English**: What are memory leaks?

## Answer (EN)
**Memory leaks** occur when an object in memory is **no longer used** but remains **inaccessible to the garbage collector** due to active references to it.

This can happen due to **cyclic references** or **improperly managed resources**.

Memory leaks lead to **increased memory consumption** and **degraded app performance**.

**How Memory Leaks Happen:**

```kotlin
// Object is no longer needed
// But GC cannot collect it
// Because strong reference exists
```

**Common Causes:**

**1. Static References to Activity:**

```kotlin
// - Memory Leak
class MyActivity : AppCompatActivity() {
    companion object {
        var instance: Activity? = null  // Static reference
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // Leak! Activity never released
    }
}
```

**2. Anonymous Inner Classes:**

```kotlin
// - Memory Leak
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Anonymous class holds implicit Activity reference
        button.setOnClickListener(object : View.OnClickListener {
            override fun onClick(v: View?) {
                // Holds MyActivity reference
                updateUI()
            }
        })
    }
}
```

**3. Handler Leaks:**

```kotlin
// - Memory Leak
class MyActivity : AppCompatActivity() {
    private val handler = Handler()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Delayed runnable holds Activity
        handler.postDelayed({
            // Activity leaked if destroyed before this runs
            updateUI()
        }, 60000)
    }
}
```

**4. Listener Not Removed:**

```kotlin
// - Memory Leak
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Register listener
        eventBus.register(this)

        // Forgot to unregister!
    }

    // Missing onDestroy with eventBus.unregister(this)
}
```

**Effects of Memory Leaks:**

-  **Memory usage grows** over time
-  **OutOfMemoryError** crashes
-  **App slowdown** and lag
-  **Battery drain**
-  **UI freezes**

**Detection:**

```kotlin
// Use LeakCanary
debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'

// Automatically detects leaks and shows:
// - Leaked object
// - Retention chain
// - Retained memory size
```

**Prevention:**

```kotlin
// - GOOD - Proper cleanup
class MyActivity : AppCompatActivity() {
    private val disposables = CompositeDisposable()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Register
        disposables.add(
            observable.subscribe { data ->
                updateUI(data)
            }
        )
    }

    override fun onDestroy() {
        // Cleanup to prevent leak
        disposables.clear()
        super.onDestroy()
    }
}
```

**Summary:**

- **Memory leak**: Object no longer used but not garbage collected
- **Cause**: Active references prevent GC
- **Result**: Increased memory usage, poor performance
- **Common sources**: Static refs, inner classes, handlers, listeners
- **Detection**: LeakCanary, Memory Profiler
- **Prevention**: Proper resource cleanup

## Ответ (RU)
Утечки памяти происходят, когда объект в памяти больше не используется, но остаётся недоступным для сборщика мусора из-за активных ссылок на него. Это может случиться из-за циклических ссылок или неправильно управляемых ресурсов. Утечки памяти приводят к увеличению потребления памяти и ухудшению производительности приложения.


---

## Related Questions

### Computer Science Fundamentals
- [[q-primitive-vs-reference-types--programming-languages--easy]] - Memory Management
- [[q-reference-types-criteria--programming-languages--medium]] - Memory Management
- [[q-kotlin-reference-equality-operator--programming-languages--easy]] - Memory Management
- [[q-reference-types-protect-from-deletion--programming-languages--easy]] - Memory Management
- [[q-find-object-without-references--programming-languages--medium]] - Memory Management

### Kotlin Language Features
- [[q-coroutine-memory-leaks--kotlin--hard]] - Memory Management
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Memory Management
