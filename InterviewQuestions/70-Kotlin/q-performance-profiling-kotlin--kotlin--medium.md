---
id: kotlin-259
title: Performance Profiling in Kotlin / Профилирование производительности Kotlin
aliases:
- Performance Profiling
- Android Profiler
- Профилирование Kotlin
topic: kotlin
subtopics:
- performance
- profiling
- debugging
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-performance
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- performance
- profiling
- leakcanary
- strictmode
- difficulty/medium
anki_cards:
- slug: kotlin-259-0-en
  language: en
  anki_id: 1769170308521
  synced_at: '2026-01-23T17:03:50.761928'
- slug: kotlin-259-0-ru
  language: ru
  anki_id: 1769170308545
  synced_at: '2026-01-23T17:03:50.763507'
---
# Вопрос (RU)
> Как профилировать Kotlin/Android приложения? Какие инструменты используются для поиска проблем производительности?

# Question (EN)
> How do you profile Kotlin/Android applications? What tools are used to find performance issues?

---

## Ответ (RU)

**Основные инструменты профилирования:**

| Инструмент | Назначение |
|------------|------------|
| Android Profiler | CPU, память, сеть, энергопотребление |
| LeakCanary | Утечки памяти |
| StrictMode | Нарушения best practices |
| Benchmark | Микробенчмарки |

**Android Profiler:**
```kotlin
// CPU Profiling - найти медленные методы
// В Android Studio: View > Tool Windows > Profiler

// Добавить trace в код
import android.os.Trace

fun expensiveOperation() {
    Trace.beginSection("expensiveOperation")
    try {
        // код
    } finally {
        Trace.endSection()
    }
}
```

**LeakCanary - утечки памяти:**
```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}

// Автоматически отслеживает утечки Activity, Fragment, View, ViewModel
// Уведомления показываются при обнаружении утечки

// Распространённые причины утечек:
// 1. Static reference к Context
object Singleton {
    // ПЛОХО
    lateinit var context: Context
}

// 2. Inner class с ссылкой на outer
class MyActivity : Activity() {
    // ПЛОХО - handler держит ссылку на Activity
    private val handler = Handler(Looper.getMainLooper())
}
```

**StrictMode - обнаружение нарушений:**
```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectDiskReads()
                    .detectDiskWrites()
                    .detectNetwork()
                    .penaltyLog()
                    .build()
            )

            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectLeakedClosableObjects()
                    .detectActivityLeaks()
                    .penaltyLog()
                    .build()
            )
        }
    }
}
```

**Benchmark - микробенчмарки:**
```kotlin
// build.gradle.kts
android {
    defaultConfig {
        testInstrumentationRunner = "androidx.benchmark.junit4.AndroidBenchmarkRunner"
    }
}

dependencies {
    androidTestImplementation("androidx.benchmark:benchmark-junit4:1.2.0")
}

// Тест
@RunWith(AndroidJUnit4::class)
class MyBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun listIteration() {
        val list = (1..1000).toList()
        benchmarkRule.measureRepeated {
            list.filter { it % 2 == 0 }.map { it * 2 }
        }
    }
}
```

**Профилирование корутин:**
```kotlin
// Включить отладочные имена
System.setProperty("kotlinx.coroutines.debug", "on")

// Корутины будут показывать имена в stack traces
launch(CoroutineName("DataLoader")) {
    // ...
}
```

## Answer (EN)

**Main Profiling Tools:**

| Tool | Purpose |
|------|---------|
| Android Profiler | CPU, memory, network, energy |
| LeakCanary | Memory leaks |
| StrictMode | Best practice violations |
| Benchmark | Microbenchmarks |

**Android Profiler:**
```kotlin
// CPU Profiling - find slow methods
// In Android Studio: View > Tool Windows > Profiler

// Add trace in code
import android.os.Trace

fun expensiveOperation() {
    Trace.beginSection("expensiveOperation")
    try {
        // code
    } finally {
        Trace.endSection()
    }
}
```

**LeakCanary - Memory Leaks:**
```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}

// Automatically tracks leaks in Activity, Fragment, View, ViewModel
// Notifications shown when leak detected

// Common leak causes:
// 1. Static reference to Context
object Singleton {
    // BAD
    lateinit var context: Context
}

// 2. Inner class with outer reference
class MyActivity : Activity() {
    // BAD - handler holds reference to Activity
    private val handler = Handler(Looper.getMainLooper())
}
```

**StrictMode - Detecting Violations:**
```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectDiskReads()
                    .detectDiskWrites()
                    .detectNetwork()
                    .penaltyLog()
                    .build()
            )

            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectLeakedClosableObjects()
                    .detectActivityLeaks()
                    .penaltyLog()
                    .build()
            )
        }
    }
}
```

**Benchmark - Microbenchmarks:**
```kotlin
// build.gradle.kts
android {
    defaultConfig {
        testInstrumentationRunner = "androidx.benchmark.junit4.AndroidBenchmarkRunner"
    }
}

dependencies {
    androidTestImplementation("androidx.benchmark:benchmark-junit4:1.2.0")
}

// Test
@RunWith(AndroidJUnit4::class)
class MyBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun listIteration() {
        val list = (1..1000).toList()
        benchmarkRule.measureRepeated {
            list.filter { it % 2 == 0 }.map { it * 2 }
        }
    }
}
```

**Profiling Coroutines:**
```kotlin
// Enable debug names
System.setProperty("kotlinx.coroutines.debug", "on")

// Coroutines will show names in stack traces
launch(CoroutineName("DataLoader")) {
    // ...
}
```

---

## Follow-ups

- How do you read and interpret a flame graph?
- What are common causes of jank in Android apps?
- How do you profile Compose recomposition performance?
