---
id: "20251015082238626"
title: "Jit Vs Aot Compilation"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [jit, aot, compilation, art, performance, baseline-profiles, difficulty/medium]
---
# JIT vs AOT Compilation in Android

**Сложность**: 🟡 Medium
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
What are the differences between JIT and AOT compilation in Android? How does Android use both strategies?

## Answer (EN)
JIT (Just-In-Time) and AOT (Ahead-Of-Time) are compilation strategies for converting bytecode to machine code. Modern Android uses a hybrid approach combining both for optimal performance.

#### 1. **JIT Compilation (Just-In-Time)**

**How It Works:**

```
App Execution:
  Start → Interpret bytecode → Profile hot code → Compile → Execute
         (slow)                                   (fast)

First execution: SLOW (interpreted)
  ↓
Profile collection
  ↓
JIT compilation when threshold reached
  ↓
Subsequent executions: FAST (compiled code)
```

**Example:**

```kotlin
class JITExample {
    fun calculateSum(numbers: List<Int>): Int {
        // First few calls: Interpreted (~1000ns)
        // Profiler detects hot method
        // JIT compiles to native code
        // Subsequent calls: Compiled (~100ns, 10x faster)

        return numbers.sum()
    }
}

// Execution timeline:
// Call 1: 1000ns (interpreted)
// Call 2: 1000ns (interpreted)
// Call 10: 950ns (profiling overhead)
// Call 100: JIT compilation triggered
// Call 101: 100ns (compiled)
// Call 102+: 100ns (compiled, cached)
```

**Advantages:**

```kotlin
// - Fast startup
// - No compilation during installation
// - App launches immediately

// - Small storage footprint
// - Only bytecode stored
// - Compiled code in memory cache

// - Adaptive optimization
// - Compiles only hot code
// - Optimizes based on actual usage patterns

// - Quick app updates
// - No recompilation needed
// - Instant deployment
```

**Disadvantages:**

```kotlin
// - Warm-up time
fun firstInteraction() {
    // Slow until JIT compilation kicks in
    heavyComputation() // 1000ns (interpreted)
}

// - Runtime overhead
// - Profiling adds overhead
// - Compilation happens during execution
// - May cause jank

// - Lost on restart
// - Compiled code in memory only
// - Recompilation needed after app restart
```

#### 2. **AOT Compilation (Ahead-Of-Time)**

**How It Works:**

```
App Installation:
  APK → Extract DEX → Compile to native → Store OAT file
                      (dex2oat)            (machine code)

App Execution:
  Start → Load native code → Execute
         (already compiled)   (FAST)
```

**Example:**

```kotlin
class AOTExample {
    fun calculateSum(numbers: List<Int>): Int {
        // Compiled during installation
        // All calls: Fast from the start (~100ns)
        return numbers.sum()
    }
}

// Execution timeline:
// Installation: Compilation happens (30-60 seconds)
// Call 1: 100ns (compiled)
// Call 2: 100ns (compiled)
// All calls: 100ns (compiled)
```

**Advantages:**

```kotlin
// - Instant performance
// - No warm-up needed
// - Fast from first launch

// - Predictable performance
// - Consistent execution times
// - No JIT overhead during runtime

// - Persistent optimization
// - Survives app restarts
// - No recompilation needed

// - Lower battery usage
// - No runtime compilation
// - Less CPU work during execution
```

**Disadvantages:**

```kotlin
// - Slow installation
// Installation time comparison:
val jitInstall = 5  // seconds
val aotInstall = 45 // seconds (9x slower!)

// - Large storage footprint
data class AppSize(
    val dex: Int,  // MB
    val oat: Int   // MB
)

val sizes = AppSize(
    dex = 20,      // Original DEX
    oat = 40       // Compiled OAT (2x larger)
)

// - Slow updates
// - Recompilation on every update
// - Delays app availability

// - Compiles unused code
// - All code compiled, even rarely used
// - Wasted storage and compilation time
```

#### 3. **Hybrid Approach (Android 7.0+)**

**Profile-Guided Optimization:**

```
Installation:
  APK → Extract DEX → Quick install → Store DEX only
                      (no compilation)

First Run:
  Launch → JIT interpret → Profile hot paths → Cache
          (medium speed)

Background (device idle + charging):
  Read profile → AOT compile hot code → Store optimized OAT
                (dex2oat with profile)

Subsequent Runs:
  Launch → Load optimized code → Fast execution
          (pre-compiled hot paths)
```

**Implementation:**

```kotlin
// Profile collection
class ProfileGuidedExample {

    // Hot method (called frequently)
    fun processUserData(user: User): ProcessedData {
        // Profiler detects this is hot
        // Gets AOT compiled in background
        // Subsequent runs: Fast
        return transform(user)
    }

    // Cold method (rarely called)
    fun exportDebugData(): String {
        // Profiler detects this is cold
        // Remains interpreted
        // Saves compilation time and storage
        return generateReport()
    }
}

// Profile location on device:
// /data/misc/profiles/cur/0/com.example.app/primary.prof
```

**Profile Format:**

```
# Example profile content
classes:
  Lcom/example/app/MainActivity;
  Lcom/example/app/ui/HomeScreen;
  Lcom/example/app/viewmodel/HomeViewModel;

methods:
  HSPLcom/example/app/repository/DataRepository;->getData()Ljava/util/List;
  PLcom/example/app/utils/ImageProcessor;->resize(Landroid/graphics/Bitmap;)Landroid/graphics/Bitmap;

# Flags:
# H - Hot (frequently executed)
# S - Startup (executed during app start)
# P - Post-startup (executed after startup)
```

**Benefits of Hybrid:**

```kotlin
object HybridBenefits {
    val installTime = 5       // seconds (like JIT)
    val coldStart = 900      // ms (better than JIT, close to AOT)
    val optimizedStart = 750  // ms (after background compilation)
    val storageOverhead = 20  // MB (only hot code compiled)

    // Best of both worlds:
    // - Fast installation (like JIT)
    // - Good startup performance (close to AOT)
    // - Adaptive optimization (compiles what matters)
    // - Reasonable storage (only hot paths)
    // - Fast updates (no full recompilation)
}
```

#### 4. **Compilation Modes**

```kotlin
// Available compilation modes (adb shell)

// 1. verify - Minimal, only verify DEX
adb shell cmd package compile -m verify com.example.app

// 2. quicken - Optimize DEX without native code
adb shell cmd package compile -m quicken com.example.app

// 3. speed - Full AOT compilation
adb shell cmd package compile -m speed com.example.app

// 4. speed-profile - Profile-guided AOT (default Android 7+)
adb shell cmd package compile -m speed-profile com.example.app

// 5. everything - Compile everything (debugging)
adb shell cmd package compile -m everything com.example.app

// Comparison:
data class CompilationMode(
    val name: String,
    val installTime: Int,  // seconds
    val storageSize: Int,  // MB
    val coldStart: Int,    // ms
    val hotStart: Int      // ms
)

val modes = listOf(
    CompilationMode("verify", 3, 20, 1500, 150),
    CompilationMode("quicken", 5, 22, 1200, 130),
    CompilationMode("speed", 45, 60, 700, 90),
    CompilationMode("speed-profile", 5, 35, 850, 100),
    CompilationMode("everything", 90, 80, 650, 85)
)
```

#### 5. **Tiered Compilation**

```kotlin
// Modern Android uses tiered compilation

// Tier 0: Interpreter
// - First execution of any code
// - Slowest, but instant availability

// Tier 1: Quickened DEX
// - Optimized bytecode
// - Faster interpretation
// - Minimal compilation

// Tier 2: JIT Compilation
// - Hot methods compiled
// - Native code in memory
// - Fast execution, lost on restart

// Tier 3: AOT Compilation (Profile-Guided)
// - Hot paths compiled
// - Native code on disk
// - Persistent optimization

class TieredExample {
    fun processData(data: List<Int>): Int {
        // First call: Tier 0 (interpreter) - 1000ns
        // Calls 2-9: Tier 1 (quickened) - 700ns
        // Call 10+: Tier 2 (JIT) - 150ns
        // Background: Tier 3 (AOT) - stored for next run
        // Next app start: Tier 3 (AOT) - 100ns from start
        return data.sum()
    }
}
```

#### 6. **Baseline Profiles (Android 9+)**

```kotlin
// Ship pre-generated profiles with APK

// app/src/main/baseline-prof.txt
// Tells compiler what to optimize before first run

class BaselineProfileExample {
    // This method listed in baseline-prof.txt
    fun criticalStartupMethod() {
        // Compiled during installation using baseline profile
        // Fast from first launch
        // No need to wait for profiling
    }
}

// Installation with baseline profile:
Install APK
  ↓
Extract baseline-prof.txt
  ↓
AOT compile listed methods (background)
  ↓
First launch: Already optimized!

// Performance improvement:
val withoutBaseline = StartupMetrics(
    coldStart = 1200, // ms
    warmStart = 800
)

val withBaseline = StartupMetrics(
    coldStart = 800,  // 33% faster
    warmStart = 500   // 38% faster
)
```

#### 7. **Optimization Strategies**

```kotlin
// 1. Identify hot paths
class PerformanceCritical {
    // Mark critical methods for optimization
    @FastNative
    external fun nativeCompute(data: IntArray): Int

    // Hot path - will be JIT/AOT compiled
    fun frequentOperation() {
        repeat(1000000) {
            compute()
        }
    }

    // Cold path - may remain interpreted
    fun rareDebugOperation() {
        generateDebugReport()
    }
}

// 2. Force compilation for testing
object CompilationTester {
    fun forceCompile(packageName: String) {
        // Via adb:
        // adb shell cmd package compile -m speed -f $packageName

        // Verify:
        // adb shell dumpsys package dexopt | grep $packageName
    }

    fun clearAndRetest(packageName: String) {
        // Clear compiled code:
        // adb shell cmd package compile --reset $packageName

        // Retest cold performance
    }
}

// 3. Monitor compilation status
class CompilationMonitor {
    fun checkStatus(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val status = ProfileVerifier.getCompilationStatusAsync().get()

            Log.d("Compilation", """
                Has reference profile: ${status.hasReferenceProfile()}
                Profile install result: ${status.profileInstallResultCode}
                Is compiled with profile: ${status.isCompiledWithProfile}
            """.trimIndent())
        }
    }
}
```

#### 8. **Decision Tree**

```kotlin
object CompilationStrategy {
    fun chooseStrategy(appType: AppType): Strategy {
        return when (appType) {
            is Gaming -> {
                // Need instant performance
                Strategy.FullAOT(
                    reason = "Consistent frame times required",
                    tradeoff = "Larger install, slow updates acceptable"
                )
            }

            is SocialMedia -> {
                // Frequent updates, varied usage
                Strategy.ProfileGuided(
                    reason = "Fast updates needed, usage varies",
                    tradeoff = "Best balance for user engagement"
                )
            }

            is Utility -> {
                // Quick launch critical
                Strategy.BaselineProfile(
                    reason = "Fast first impression critical",
                    tradeoff = "Extra build step acceptable"
                )
            }

            is Enterprise -> {
                // Stable, infrequent updates
                Strategy.FullAOT(
                    reason = "Stability over update speed",
                    tradeoff = "Deployment time acceptable"
                )
            }
        }
    }
}
```

### Comparison Summary

| Aspect | JIT | AOT | Hybrid (Profile-Guided) |
|--------|-----|-----|------------------------|
| Install Time | Fast (5s) | Slow (45s) | Fast (5s) |
| First Run | Slow | Fast | Medium |
| Optimized Run | Medium | Fast | Fast |
| Storage | Small (20MB) | Large (60MB) | Medium (35MB) |
| Battery | Higher | Lower | Low |
| Updates | Fast | Slow | Fast |
| Adaptation | Excellent | None | Good |
| Best For | Rapid iteration | Performance-critical | General apps |

### Best Practices

- [ ] Use baseline profiles for critical paths
- [ ] Profile on real devices
- [ ] Test with different compilation modes
- [ ] Monitor compilation status in production
- [ ] Optimize hot paths first
- [ ] Accept interpretation for cold paths
- [ ] Measure impact on app size
- [ ] Consider update frequency

---



## Ответ (RU)
# Вопрос (RU)
В чём различия между JIT и AOT компиляцией в Android? Как Android использует обе стратегии?

## Ответ (RU)
JIT (Just-In-Time) и AOT (Ahead-Of-Time) - стратегии компиляции байткода в машинный код. Современный Android использует гибридный подход.

#### JIT (Just-In-Time):

**Как работает:**
- Байткод интерпретируется при выполнении
- Горячий код компилируется в runtime
- Результат в памяти (теряется при перезапуске)

**Преимущества:**
- Быстрая установка
- Малый размер
- Адаптивная оптимизация

**Недостатки:**
- Прогрев при запуске
- Runtime overhead
- Теряется при рестарте

#### AOT (Ahead-Of-Time):

**Как работает:**
- Компиляция при установке
- Машинный код на диске
- Быстрое выполнение сразу

**Преимущества:**
- Мгновенная производительность
- Предсказуемость
- Постоянная оптимизация

**Недостатки:**
- Медленная установка (9x)
- Большой размер (2x)
- Компилирует неиспользуемый код

#### Гибридный подход (Android 7+):

**Profile-Guided Optimization:**
1. Быстрая установка (только DEX)
2. Первый запуск: JIT + профилирование
3. Фон: AOT компиляция горячего кода
4. Последующие запуски: оптимизированный код

**Baseline Profiles (Android 9+):**
- Предгенерированные профили в APK
- Компиляция при установке
- Быстро с первого запуска

### Сравнение:

| Аспект | JIT | AOT | Hybrid |
|--------|-----|-----|--------|
| Установка | 5s | 45s | 5s |
| Первый запуск | Медленно | Быстро | Средне |
| Оптим. запуск | Средне | Быстро | Быстро |
| Размер | 20MB | 60MB | 35MB |
| Обновления | Быстро | Медленно | Быстро |

**Лучший выбор:** Hybrid с baseline profiles для большинства приложений.
