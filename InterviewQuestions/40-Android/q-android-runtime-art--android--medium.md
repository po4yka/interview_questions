---
id: 20251012-122770
title: Android Runtime ART / Android Runtime ART
aliases:
- Android Runtime ART
- Android Runtime ART
topic: android
subtopics:
- performance-memory
- processes
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-app-lag-analysis--android--medium
- q-android-performance-measurement-tools--android--medium
- q-android-build-optimization--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/performance-memory
- android/processes
- difficulty/medium
---

## Answer (EN)
**Android Runtime (ART)** is the execution environment for Android applications, responsible for running code, managing memory, and interacting with the operating system. ART replaced Dalvik VM from Android 5.0 and uses **AOT (Ahead-of-Time) compilation** for improved performance.

**Runtime Theory:**
Android Runtime provides a managed execution environment that abstracts hardware differences and provides [[c-memory-management]], [[c-garbage-collection]], and security isolation. It converts DEX bytecode to native machine code for optimal performance while maintaining portability across different Android devices.

**ART vs Dalvik:**
- **Dalvik**: JIT (Just-In-Time) compilation during execution
- **ART**: AOT (Ahead-of-Time) compilation at install time + JIT profiling since Android 7.0

**AOT Compilation Process:**
```
APK → DEX bytecode → AOT compilation → Native machine code
                    (at install time)
```

**Key ART Features:**
- **AOT Compilation**: Converts DEX to native code at install time
- **Improved Garbage Collection**: Concurrent copying GC with heap compaction
- **Better Performance**: Faster app startup and execution
- **Lower Battery Consumption**: No runtime compilation overhead
- **Hybrid Compilation**: AOT + JIT profiling for optimal performance

**Memory Management:**
```kotlin
class MemoryExample {
    fun createObjects() {
        val list = mutableListOf<String>()
        repeat(10000) {
            list.add("Object $it")
        }
        // ART automatically manages garbage collection
    }
}
```

**Garbage Collection Theory:**
ART uses a concurrent copying garbage collector that runs alongside the application, minimizing pause times. It performs heap compaction to reduce fragmentation and improve memory allocation efficiency.

**Class Loading:**
```kotlin
class MyActivity : AppCompatActivity() {
    // Classes loaded on-demand from DEX files
    private val helper by lazy { DatabaseHelper(this) }
}
```

**DEX Format:**
```
Java/Kotlin code → .class files → .dex files → ART execution
```

**DEX Theory:**
DEX (Dalvik Executable) format is optimized for mobile devices with smaller file sizes than Java bytecode. All classes are packaged in a single DEX file for efficient loading and execution.

**Hybrid Compilation (Android 7.0+):**
```
Install: Basic AOT compilation (fast)
         ↓
First runs: JIT compilation of "hot" code paths
         ↓
Background: Full AOT optimization
```

**Performance Optimization:**
```kotlin
class PerformanceExample {
    fun hotMethod() {
        // Frequently called - compiled to optimized native code
        processData()
    }

    fun coldMethod() {
        // Rarely called - may remain interpreted
        cleanup()
    }
}
```

**Security Features:**
- **Sandboxed Execution**: Each app runs in isolated environment
- **Process Isolation**: Apps run in separate processes
- **Permission System**: Controlled access to system resources

**Runtime Detection:**
```kotlin
fun checkRuntime() {
    val runtime = System.getProperty("java.vm.name")
    Log.d("Runtime", "VM: $runtime") // "ART" or "Dalvik"
}
```

**Key Differences:**
- **ART**: AOT compilation, better GC, faster execution, larger app size
- **Dalvik**: JIT compilation, simpler GC, slower execution, smaller app size

## Follow-ups

- How does ART's garbage collection differ from Dalvik's approach?
- What are the performance implications of AOT vs JIT compilation?
- How does hybrid compilation work in modern Android versions?

## References

- https://developer.android.com/guide/practices/verifying-app-behavior-on-runtime
- https://source.android.com/docs/core/runtime

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-android-manifest-file--android--easy]] - App configuration

### Related (Medium)
- [[q-android-app-lag-analysis--android--medium]] - Performance analysis
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools
- [[q-android-build-optimization--android--medium]] - Build optimization

### Advanced (Harder)
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns