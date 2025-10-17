---
id: "20251015082238631"
title: "Android Runtime Internals / Внутреннее устройство Android Runtime"
topic: android
difficulty: hard
status: draft
created: 2025-10-13
tags: [art, runtime, jit, aot, dex, compilation, performance, difficulty/hard]
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---
# Android Runtime Internals

**Сложность**: Hard
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> How does the Android Runtime (ART) work internally? Explain the bytecode execution, compilation, and memory management processes.

# Вопрос (RU)
> Как работает Android Runtime (ART) внутри? Объясните выполнение байткода, компиляцию и управление памятью.

---

## Answer (EN)

ART is the managed runtime environment that executes Android app code. Understanding its internals helps optimize app performance and troubleshoot issues.

#### 1. **ART Architecture Overview**

```
Application Layer:
  ↓
DEX Bytecode (.dex files)
  ↓
ART Runtime Components:
   Class Loader
   Bytecode Verifier
   Interpreter
   JIT Compiler
   AOT Compiler (dex2oat)
   Garbage Collector
   Memory Manager
  ↓
Native Code Execution
  ↓
Hardware (CPU, RAM)
```

#### 2. **DEX Bytecode Format**

```kotlin
// Kotlin/Java source
class Example {
    fun add(a: Int, b: Int): Int {
        return a + b
    }
}

// Compiled to DEX bytecode
method public add(II)I
    .registers 4
    .param p1, "a"    # I
    .param p2, "b"    # I

    .prologue
    .line 3
    add-int v0, p1, p2    # v0 = p1 + p2
    return v0              # return v0
.end method

// DEX instruction format:
// - Compact register-based architecture
// - 16-bit instruction units
// - Optimized for mobile devices
```

**DEX Structure:**

```
DEX File Format:
 Header
 String IDs (string pool)
 Type IDs (types/classes)
 Proto IDs (method prototypes)
 Field IDs
 Method IDs
 Class Definitions
 Call Site IDs (Android 8+)
 Method Handles (Android 8+)
 Data Section
 Link Data
```

#### 3. **Class Loading Process**

```kotlin
// App startup class loading sequence
Application Startup
  ↓
1. Load Application class
  PathClassLoader.loadClass("com.example.MyApplication")
    ↓
  2. Load DEX file
    DexFile.loadDex("/data/app/com.example/base.apk")
    ↓
  3. Verify bytecode
    verifyClass(MyApplication)
    ↓
  4. Link class
    linkClass(MyApplication)
    ↓
  5. Initialize class
    <clinit>() // Static initializers
    ↓
  6. Class ready for use

// ClassLoader hierarchy
BootClassLoader (framework classes)
  ↓
PathClassLoader (app classes)
  ↓
DexClassLoader (dynamic loading)
```

**Implementation:**

```kotlin
class ClassLoadingExample {
    fun demonstrateClassLoading() {
        // Standard class loading
        val clazz = Class.forName("com.example.MyClass")

        // Get class loader
        val classLoader = clazz.classLoader
        Log.d("ClassLoader", "Loader: $classLoader")
        // Output: dalvik.system.PathClassLoader[DexPathList[...]]

        // Parent class loader
        val parent = classLoader?.parent
        Log.d("ClassLoader", "Parent: $parent")
        // Output: java.lang.BootClassLoader

        // Dynamic loading (if needed)
        val dexFile = File("/data/local/tmp/dynamic.dex")
        val dexClassLoader = DexClassLoader(
            dexFile.absolutePath,
            codeCacheDir.absolutePath,
            null,
            classLoader
        )

        val dynamicClass = dexClassLoader.loadClass("com.dynamic.DynamicClass")
    }
}
```

#### 4. **Execution Modes**

**4.1 Interpreter**

```kotlin
// Bytecode interpretation
fun interpretBytecode(method: Method) {
    // Pseudo-code of ART interpreter
    val instructions = method.instructions
    val registers = IntArray(method.registersSize)

    var pc = 0 // Program counter

    while (pc < instructions.size) {
        val instruction = instructions[pc]

        when (instruction.opcode) {
            Opcode.CONST -> {
                // const vX, literal
                registers[instruction.vA] = instruction.literal
            }

            Opcode.ADD_INT -> {
                // add-int vA, vB, vC
                registers[instruction.vA] =
                    registers[instruction.vB] + registers[instruction.vC]
            }

            Opcode.RETURN -> {
                // return vX
                return registers[instruction.vA]
            }

            // ... other opcodes
        }

        pc++
    }
}

// Performance: ~10-100x slower than native code
```

**4.2 JIT Compilation**

```kotlin
// JIT compilation flow
Method Execution
  ↓
Interpreter (first calls)
  ↓
Profile collection (hot method detection)
  ↓
JIT compilation threshold reached
  ↓
Background compilation to native code
  ↓
Native code cache (in memory)
  ↓
Direct native execution (subsequent calls)

// JIT compiler stages:
class JITCompiler {
    fun compile(method: Method): NativeCode {
        // 1. Parse bytecode
        val ir = parseBytecode(method)

        // 2. Optimize IR
        val optimizedIR = optimize(ir)
        //    - Inline small methods
        //    - Eliminate dead code
        //    - Constant folding
        //    - Loop optimization

        // 3. Generate machine code
        val machineCode = generateMachineCode(optimizedIR)

        // 4. Cache compiled code
        codeCache.put(method, machineCode)

        return machineCode
    }
}
```

**4.3 AOT Compilation (dex2oat)**

```kotlin
// Installation-time compilation
Install APK
  ↓
Extract DEX files
  ↓
dex2oat compiler
   Parse DEX
   Build compiler IR
   Optimize (if profile available)
   Generate machine code
   Create OAT file
  ↓
Store OAT file (/data/app/.../oat/)

// OAT file format:
OAT File:
 OAT Header
 DEX files (embedded)
 OAT DEX files (metadata)
 Native code (compiled methods)
 QuickInfo (method offsets)
 Bitmap (compilation status)

// Compilation modes:
enum class CompilationFilter {
    ASSUME_VERIFIED,  // Trust code is valid
    EXTRACT,          // Only extract DEX
    VERIFY,           // Verify DEX only
    QUICKEN,          // Optimize DEX instructions
    SPACE_PROFILE,    // Compile profiled methods (smaller)
    SPACE,            // Compile with space optimizations
    SPEED_PROFILE,    // Compile profiled methods (faster)
    SPEED,            // Compile everything (fastest)
    EVERYTHING        // Maximum optimization
}
```

#### 5. **Garbage Collection**

**5.1 GC Algorithms**

```kotlin
// ART GC evolution

// Android 5.0-7.0: Concurrent Mark Sweep (CMS)
class CMSCollector {
    fun collect() {
        // Phase 1: Initial mark (STW pause ~5-10ms)
        markRoots()

        // Phase 2: Concurrent mark (app running)
        concurrentMark()

        // Phase 3: Remark (STW pause ~2-5ms)
        remark()

        // Phase 4: Concurrent sweep (app running)
        concurrentSweep()

        // Issue: Heap fragmentation over time
    }
}

// Android 8.0+: Concurrent Copying (CC)
class ConcurrentCopyingCollector {
    fun collect() {
        // Phase 1: Initial mark (STW pause ~2-5ms)
        markRoots()

        // Phase 2: Concurrent copy (app running)
        copyLiveObjects()
        updateReferences()

        // Phase 3: Reclaim space (app running)
        reclaimSpace()

        // Benefits:
        // - Compacts heap (no fragmentation)
        // - Shorter pauses
        // - Better cache locality
    }
}

// Android 10+: Generational GC
class GenerationalGC {
    val youngGeneration = Region("young") // New objects
    val oldGeneration = Region("old")     // Long-lived objects

    fun collect() {
        // Minor GC (frequent, fast)
        collectYoungGeneration() // ~1-2ms pause

        // Major GC (infrequent, slower)
        if (needsMajorGC()) {
            collectFullHeap()    // ~5-10ms pause
        }

        // Weak generational hypothesis:
        // Most objects die young
        // Young GC is much faster than full GC
    }
}
```

**5.2 GC Roots**

```kotlin
// Objects that are always reachable
sealed class GCRoot {
    // 1. Static fields
    companion object {
        val STATIC_FIELD = Any() // GC root
    }

    // 2. Active threads
    val thread = Thread {
        // Thread object is GC root
        // All objects it references are kept alive
    }

    // 3. Stack variables
    fun method() {
        val localVariable = Any() // GC root while method executing
    }

    // 4. JNI references
    external fun nativeMethod() // Native references are GC roots

    // 5. System classes
    // ClassLoader, String constants, etc.
}

// Reachability analysis
fun isReachable(obj: Any): Boolean {
    val visited = mutableSetOf<Any>()
    val queue = ArrayDeque<Any>()

    // Start from GC roots
    queue.addAll(gcRoots)

    while (queue.isNotEmpty()) {
        val current = queue.removeFirst()

        if (current == obj) return true
        if (current in visited) continue

        visited.add(current)
        queue.addAll(getReferences(current))
    }

    return false // Unreachable, can be collected
}
```

#### 6. **Memory Management**

**6.1 Heap Structure**

```kotlin
// ART heap regions (Android 10+)
class ARTHeap {
    // Space types
    val imageSpace: Space       // Framework classes (read-only)
    val zygoteSpace: Space      // Shared with zygote process
    val allocationSpace: Space  // Main app heap
    val largeObjectSpace: Space // Objects > 12KB
    val nonMovingSpace: Space   // JNI pinned objects

    data class Space(
        val start: Long,
        val size: Long,
        val used: Long,
        val type: SpaceType
    )

    enum class SpaceType {
        REGION,           // Generational GC regions
        ROSALLOC,         // Run-of-slots allocator
        DLMALLOC,         // Doug Lea malloc
        LARGE_OBJECT,     // Large allocations
        ZYGOTE,           // Shared space
        IMAGE             // Framework classes
    }

    // Memory allocation
    fun allocate(size: Int): Long {
        return when {
            size > LARGE_OBJECT_THRESHOLD -> {
                largeObjectSpace.allocate(size)
            }
            else -> {
                allocationSpace.allocate(size)
            }
        }
    }
}
```

**6.2 Reference Types**

```kotlin
// Reference strength hierarchy
class ReferenceExample {
    // Strong reference (default)
    val strong = Any() // Prevents GC

    // Soft reference
    val soft = SoftReference(Any())
    // Cleared when memory pressure high
    // Good for caches

    // Weak reference
    val weak = WeakReference(Any())
    // Cleared at next GC
    // Good for avoiding leaks

    // Phantom reference
    val phantom = PhantomReference(Any(), ReferenceQueue())
    // Enqueued after finalization
    // For cleanup tracking

    fun demonstrateReferences() {
        // Soft reference usage
        val cache = object {
            private val map = mutableMapOf<String, SoftReference<Bitmap>>()

            fun get(key: String): Bitmap? {
                return map[key]?.get()
            }

            fun put(key: String, bitmap: Bitmap) {
                map[key] = SoftReference(bitmap)
            }
        }

        // Weak reference usage (avoid leaks)
        val weakActivity = WeakReference(activity)

        handler.postDelayed({
            weakActivity.get()?.let { activity ->
                activity.updateUI()
            } ?: Log.w("Leak", "Activity already collected")
        }, 1000)
    }
}
```

#### 7. **Optimization Techniques**

```kotlin
// ART compiler optimizations

// 1. Method inlining
class InliningExample {
    inline fun add(a: Int, b: Int) = a + b

    fun test() {
        val result = add(1, 2)
        // Compiled as: val result = 1 + 2
        // No method call overhead
    }
}

// 2. Devirtualization
class DevirtualizationExample {
    interface Calculator {
        fun calculate(a: Int, b: Int): Int
    }

    class Adder : Calculator {
        override fun calculate(a: Int, b: Int) = a + b
    }

    fun test() {
        val calc: Calculator = Adder()
        val result = calc.calculate(1, 2)

        // If compiler determines calc is always Adder:
        // Direct call to Adder.calculate (faster)
        // Instead of virtual dispatch (slower)
    }
}

// 3. Loop optimization
class LoopOptimizationExample {
    fun sumArray(array: IntArray): Int {
        var sum = 0
        for (i in array.indices) {
            sum += array[i]
        }
        return sum

        // Compiler optimizations:
        // - Bounds check elimination
        // - Loop unrolling
        // - Vectorization (SIMD)
    }
}

// 4. Escape analysis
class EscapeAnalysisExample {
    fun test() {
        val point = Point(10, 20)
        val distance = point.distance()
        // Compiler detects Point doesn't escape method
        // Allocates on stack instead of heap
        // No GC overhead
    }

    data class Point(val x: Int, val y: Int) {
        fun distance() = sqrt(x * x + y * y.toDouble())
    }
}
```

#### 8. **Profiling and Debugging**

```kotlin
// Built-in profiling
class ProfilingExample {
    fun profileMethod() {
        Debug.startMethodTracing("trace")
        // Code to profile
        expensiveOperation()
        Debug.stopMethodTracing()

        // Generates trace file:
        // /sdcard/Android/data/com.example/files/trace.trace
        // Analyze with Android Studio Profiler
    }

    fun profileMemory() {
        // Heap dump
        Debug.dumpHprofData("/sdcard/heap.hprof")

        // Memory info
        val memoryInfo = Debug.MemoryInfo()
        Debug.getMemoryInfo(memoryInfo)

        Log.d("Memory", """
            Dalvik Heap: ${memoryInfo.dalvikPrivateDirty} KB
            Native Heap: ${memoryInfo.nativePrivateDirty} KB
            Total PSS: ${memoryInfo.totalPss} KB
        """.trimIndent())
    }
}
```

### Key Concepts Summary

**Execution:**
- DEX bytecode format (compact, register-based)
- Multi-tier execution (interpreter → JIT → AOT)
- Profile-guided optimization

**Compilation:**
- dex2oat (AOT compiler)
- JIT compiler (runtime optimization)
- OAT file format (compiled code)

**Memory:**
- Generational GC (young/old generations)
- Concurrent copying collector
- Multiple heap spaces
- Reference types (strong/soft/weak/phantom)

**Optimization:**
- Method inlining
- Devirtualization
- Loop optimization
- Escape analysis

---

## Ответ (RU)

ART - managed runtime среда для выполнения Android-приложений.

#### Архитектура:

```
Приложение
  ↓
DEX Байткод
  ↓
ART Runtime:
  - Class Loader
  - Bytecode Verifier
  - Interpreter
  - JIT Compiler
  - AOT Compiler
  - GC
  - Memory Manager
  ↓
Native Code
  ↓
Hardware
```

#### Режимы выполнения:

1. **Interpreter** - интерпретация байткода (медленно, 10-100x)
2. **JIT** - компиляция горячего кода в runtime (быстро после прогрева)
3. **AOT** - предварительная компиляция (dex2oat, быстро с первого запуска)

#### Garbage Collection:

**Android 8.0+: Concurrent Copying**
- Паузы 2-5ms
- Компактная куча (no fragmentation)
- Фоновое копирование

**Android 10+: Generational GC**
- Young generation (новые объекты)
- Old generation (долгоживущие)
- Minor GC ~1-2ms
- Major GC ~5-10ms

#### Структура памяти:

- Image Space (framework классы)
- Zygote Space (разделяемый)
- Allocation Space (основная куча)
- Large Object Space (объекты >12KB)
- Non-Moving Space (JNI pinned)

#### Оптимизации:

- Method inlining
- Devirtualization
- Loop optimization
- Escape analysis
- Profile-guided compilation

Понимание ART помогает оптимизировать производительность и решать проблемы.
