---
topic: android
tags:
  - android
  - dalvik
  - art
  - runtime
  - jit
  - aot
  - compilation
  - performance
difficulty: medium
status: reviewed
---

# Dalvik vs ART Runtime

**Сложность**: 🟡 Medium
**Источник**: Amit Shekhar Android Interview Questions

## English

### Question
What are the differences between Dalvik and ART runtimes in Android? Why did Android migrate from Dalvik to ART?

### Answer

Dalvik and ART (Android Runtime) are execution environments for running Android applications. ART replaced Dalvik starting from Android 5.0 (Lollipop) to improve performance, battery life, and developer experience.

#### 1. **Dalvik Virtual Machine (Legacy)**

**Architecture:**

```
APK Installation:
  .apk file → Extract .dex files → Store on device
                                   (Dalvik bytecode)

App Execution:
  Launch app → JIT Compiler → Machine code → Execute
              (Just-In-Time)  (at runtime)
```

**Characteristics:**

```kotlin
// Dalvik execution model
App Start
  ↓
Load .dex bytecode
  ↓
Interpret bytecode (SLOW)
  ↓
Profile hot code paths
  ↓
JIT compile hot methods → Cache compiled code
  ↓
Execute compiled code (FAST)
  ↓
Repeat for each app launch
```

**Advantages:**
- Fast installation (no compilation needed)
- Small storage footprint
- Immediate app updates

**Disadvantages:**
- Slower app startup (JIT compilation overhead)
- Runtime performance overhead (interpretation + JIT)
- Higher battery consumption (repeated JIT compilation)
- More GC pressure (frequent object allocation)

#### 2. **ART (Android Runtime)**

**Architecture:**

```
APK Installation (Android 5.0-6.0):
  .apk file → Extract .dex → AOT Compile → Store OAT files
                             (Ahead-Of-Time)  (native code)

APK Installation (Android 7.0+):
  .apk file → Extract .dex → Profile-Guided → Store OAT files
                             AOT + JIT        (optimized code)

App Execution:
  Launch app → Load compiled code → Execute
              (Already compiled)    (FAST)
```

**Evolution:**

```kotlin
// Android 5.0-6.0: Full AOT
Install time:
  dex2oat → Compile all code → OAT file
  (slow install, fast runtime)

// Android 7.0+: Hybrid AOT + JIT
Install time:
  Quick install → JIT interpreter

Background:
  Profile hot code → AOT compile hot paths
  (fast install, progressive optimization)

// Android 9.0+: Cloud profiles
Install time:
  Quick install + Download baseline profile

Background:
  AOT compile profiled code → Optimal performance
```

#### 3. **Detailed Comparison**

**3.1 Compilation Strategy**

```kotlin
// Dalvik: JIT (Just-In-Time)
class MyClass {
    fun heavyMethod() {
        // First call: Interpreted (SLOW)
        // After threshold: JIT compiled (FAST)
        // Next app start: Interpreted again
    }
}

// ART (Android 5.0-6.0): Full AOT
class MyClass {
    fun heavyMethod() {
        // Install: Fully compiled
        // All calls: Fast (native code)
        // Trade-off: Long installation
    }
}

// ART (Android 7.0+): Profile-Guided
class MyClass {
    fun heavyMethod() {
        // First run: JIT compiled
        // Profile saved
        // Background: AOT compile hot paths
        // Subsequent runs: Optimized AOT code
    }

    fun rareMethod() {
        // Called rarely: Remains interpreted
        // Not worth compiling
    }
}
```

**3.2 Garbage Collection**

```kotlin
// Dalvik GC
// - Mark and Sweep
// - Stop-the-world pauses
// - Fragmenting heap
// - Frequent pauses causing jank

Timeline:
  App running → GC pause (50-200ms) → Resume
               (UI freezes)

// ART GC (Android 5.0+)
// - Concurrent copying collector
// - Reduced pause times
// - Compacting heap (less fragmentation)
// - Background compaction

Timeline:
  App running → Brief pause (2-10ms) → Resume
  Background compaction (concurrent)

// ART GC (Android 8.0+)
// - Generational GC
// - Region-based memory
// - Even shorter pauses (<5ms)
```

**3.3 Performance Comparison**

```kotlin
object BenchmarkResults {
    // App Startup Time
    val dalvik = Benchmark(
        coldStart = 1200, // ms
        warmStart = 800,
        hotStart = 200
    )

    val artAOT = Benchmark(
        coldStart = 800,  // 33% faster
        warmStart = 500,  // 38% faster
        hotStart = 100    // 50% faster
    )

    val artHybrid = Benchmark(
        coldStart = 900,  // First run (JIT)
        warmStart = 600,
        hotStart = 120,
        optimizedStart = 750 // After profile-guided AOT
    )

    // Runtime Performance
    val runtimePerformance = mapOf(
        "Dalvik" to Performance(
            cpuUsage = 100, // baseline
            batteryDrain = 100,
            frameRate = 55 // avg FPS
        ),
        "ART (AOT)" to Performance(
            cpuUsage = 70,  // 30% less
            batteryDrain = 75,
            frameRate = 60
        ),
        "ART (Hybrid)" to Performance(
            cpuUsage = 65,  // 35% less
            batteryDrain = 70,
            frameRate = 60
        )
    )
}
```

**3.4 Storage Impact**

```kotlin
// Application footprint comparison
data class AppSize(
    val apk: Int,      // MB
    val installed: Int, // MB
    val cache: Int     // MB
)

val dalvikApp = AppSize(
    apk = 50,
    installed = 120,  // .dex + data
    cache = 30        // JIT cache (lost on reboot)
)

val artAOTApp = AppSize(
    apk = 50,
    installed = 180,  // .dex + .oat (50% larger)
    cache = 5         // Minimal cache
)

val artHybridApp = AppSize(
    apk = 50,
    installed = 140,  // .dex + partial .oat
    cache = 10        // Profile + partial JIT
)
```

#### 4. **Debugging Improvements in ART**

```kotlin
// Dalvik: Limited debugging
// - Basic stack traces
// - Limited introspection

// ART: Enhanced debugging
class DebuggingFeatures {
    fun demonstrateARTFeatures() {
        // Better stack traces
        try {
            problematicMethod()
        } catch (e: Exception) {
            // ART provides more detailed traces
            // Including inlined methods
            e.printStackTrace()
        }

        // Improved sampling profiler
        Debug.startMethodTracing("trace")
        performOperation()
        Debug.stopMethodTracing()

        // Better memory profiling
        Debug.dumpHprofData("heap.hprof")
    }
}

// Native crash reporting
// Dalvik: Minimal info
// ART: Detailed native stack traces, register states
```

#### 5. **Developer Impact**

```kotlin
// Dalvik considerations
class DalvikOptimization {
    // Avoid method proliferation (64K method limit)
    // Each method JIT compiled separately

    // Minimize object allocations
    // GC pauses impact UX

    // Be careful with reflection
    // Slow in interpreted mode
}

// ART benefits
class ARTOptimization {
    // Less concern about method count (before MultiDex)
    // AOT compilation handles better

    // More efficient GC
    // Can allocate more freely

    // Better reflection performance
    // Optimized at compile time

    // Inline optimizations
    inline fun performOperation() {
        // Inlined at compile time
        // Zero overhead
    }
}
```

#### 6. **Migration Timeline**

```kotlin
data class AndroidVersion(
    val version: String,
    val apiLevel: Int,
    val runtime: String,
    val features: List<String>
)

val runtimeHistory = listOf(
    AndroidVersion(
        version = "4.4 KitKat",
        apiLevel = 19,
        runtime = "Dalvik (default) + ART (experimental)",
        features = listOf("ART opt-in in developer options")
    ),
    AndroidVersion(
        version = "5.0 Lollipop",
        apiLevel = 21,
        runtime = "ART (default)",
        features = listOf("Full AOT compilation", "64-bit support", "Improved GC")
    ),
    AndroidVersion(
        version = "6.0 Marshmallow",
        apiLevel = 23,
        runtime = "ART",
        features = listOf("Runtime permissions", "Doze mode")
    ),
    AndroidVersion(
        version = "7.0 Nougat",
        apiLevel = 24,
        runtime = "ART (Hybrid JIT+AOT)",
        features = listOf(
            "Profile-guided compilation",
            "Faster installation",
            "Code cache on disk",
            "Background optimization"
        )
    ),
    AndroidVersion(
        version = "9.0 Pie",
        apiLevel = 28,
        runtime = "ART (Cloud profiles)",
        features = listOf("Baseline profiles from cloud")
    ),
    AndroidVersion(
        version = "12.0",
        apiLevel = 31,
        runtime = "ART (Enhanced)",
        features = listOf(
            "Improved baseline profiles",
            "Better GC",
            "Faster compilation"
        )
    )
)
```

#### 7. **Checking Runtime**

```kotlin
class RuntimeDetector {
    fun getCurrentRuntime(): String {
        return System.getProperty("java.vm.name") ?: "Unknown"
    }

    fun getVMVersion(): String {
        return System.getProperty("java.vm.version") ?: "Unknown"
    }

    fun isART(): Boolean {
        val runtime = getCurrentRuntime()
        return runtime.contains("ART", ignoreCase = true)
    }

    fun logRuntimeInfo() {
        Log.d("Runtime", """
            VM Name: ${getCurrentRuntime()}
            VM Version: ${getVMVersion()}
            VM Vendor: ${System.getProperty("java.vm.vendor")}
            Is ART: ${isART()}
        """.trimIndent())
    }
}

// Output on modern Android:
// VM Name: Android Runtime
// VM Version: 2.1.0
// VM Vendor: The Android Project
// Is ART: true
```

#### 8. **Compilation Commands**

```bash
# Force compilation (testing/debugging)

# Full compilation (like Android 5.0-6.0)
adb shell cmd package compile -m speed -f com.example.app

# Profile-guided compilation (like Android 7.0+)
adb shell cmd package compile -m speed-profile -f com.example.app

# Quick compilation (minimal)
adb shell cmd package compile -m quicken -f com.example.app

# Verify compilation status
adb shell dumpsys package dexopt | grep com.example.app

# Clear profiles and compiled code
adb shell cmd package compile --reset com.example.app

# Check compilation reason
adb shell dumpsys package com.example.app | grep -A 1 "Dexopt state"
```

### Comparison Summary

| Feature | Dalvik | ART (5.0-6.0) | ART (7.0+) |
|---------|--------|---------------|------------|
| Compilation | JIT | Full AOT | Hybrid JIT+AOT |
| Install Time | Fast | Slow | Fast |
| First Run | Slow | Fast | Medium |
| Optimized Run | Medium | Fast | Very Fast |
| Storage | Small | Large | Medium |
| Battery | Higher | Lower | Lowest |
| GC Pauses | Long (50-200ms) | Short (2-10ms) | Very Short (<5ms) |
| Updates | Instant | Slow | Fast |

### Why ART?

**Performance:**
- 2x faster execution
- 70% less CPU usage
- Better battery life

**User Experience:**
- Faster app launches
- Smoother scrolling
- Fewer jank/stutters

**Developer Benefits:**
- Better debugging tools
- Improved profiling
- Native crash reporting

---

## Русский

### Вопрос
В чём различия между Dalvik и ART runtime в Android? Почему Android мигрировал с Dalvik на ART?

### Ответ

Dalvik и ART (Android Runtime) - это среды выполнения для запуска Android-приложений. ART заменил Dalvik начиная с Android 5.0 (Lollipop).

#### Dalvik (Legacy):

**Компиляция:** JIT (Just-In-Time)
- Байткод интерпретируется при запуске
- Горячий код JIT-компилируется
- Компиляция повторяется при каждом запуске

**Преимущества:**
- Быстрая установка
- Малый размер
- Мгновенные обновления

**Недостатки:**
- Медленный запуск
- Overhead интерпретации
- Высокий расход батареи
- Длинные паузы GC (50-200ms)

#### ART:

**Android 5.0-6.0: Полная AOT**
- Компиляция всего кода при установке
- Быстрое выполнение
- Медленная установка
- Большой размер

**Android 7.0+: Гибридная JIT+AOT**
- Быстрая установка
- JIT при первом запуске
- Profile-guided AOT в фоне
- Оптимальная производительность

**Преимущества:**
- 2x быстрее выполнение
- 70% меньше использование CPU
- Лучше батарея
- Короткие паузы GC (2-10ms)
- Улучшенная отладка

### Сравнение производительности:

| Метрика | Dalvik | ART |
|---------|--------|-----|
| Холодный запуск | 1200ms | 800ms (-33%) |
| Тёплый запуск | 800ms | 500ms (-38%) |
| CPU | 100% | 65% (-35%) |
| Батарея | 100% | 70% (-30%) |
| GC паузы | 50-200ms | <5ms |

#### Почему ART?

- Значительное улучшение производительности
- Лучший UX (плавность, отзывчивость)
- Экономия батареи
- Улучшенные инструменты для разработчиков
