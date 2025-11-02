---
id: android-089
title: "LeakCanary Heap Dump Analysis / Анализ дампа памяти в LeakCanary"
aliases: ["LeakCanary Heap Dump Analysis", "Анализ дампа памяти в LeakCanary"]
topic: android
subtopics: [performance-memory, profiling]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-31
tags: [android/performance-memory, android/profiling, leakcanary, heap-dump, memory-analysis, shark, difficulty/medium]
moc: moc-android
related: [q-main-thread-android--android--medium, q-canvas-optimization--graphics--medium]
sources: []
---

# Вопрос (RU)

> Как понять что в heap dump есть утечка памяти?

# Question (EN)

> How to detect a memory leak in a heap dump?

---

## Ответ (RU)

Если объект не был освобожден после вызова сборщика мусора, LeakCanary создает **heap dump** (снимок кучи) и анализирует его библиотекой **Shark**.

**Процесс обнаружения утечки:**

**1. Создание heap dump**

```kotlin
// LeakCanary проверяет WeakReference после GC
if (weakReference.get() != null) {
    // ✅ Объект должен был быть собран, но все еще жив
    val heapDumpFile = File(heapDumpsDir, "leak-${UUID.randomUUID()}.hprof")
    Debug.dumpHprofData(heapDumpFile.absolutePath)
    analyzeHeap(heapDumpFile)
}
```

**2. Анализ через Shark**

Shark строит граф объектов и находит пути от GC roots до подозрительных объектов:

```kotlin
fun analyzeHeap(heapDumpFile: File) {
    val heapAnalyzer = HeapAnalyzer(OnAnalysisProgressListener.NO_OP)

    val analysis = heapAnalyzer.analyze(
        heapDumpFile = heapDumpFile,
        leakingObjectFinder = FilteringLeakingObjectFinder(
            AndroidObjectInspectors.appLeakingObjectFilters
        ),
        referenceMatchers = AndroidReferenceMatchers.appDefaults,
        computeRetainedHeapSize = true
    )

    when (analysis) {
        is HeapAnalysisSuccess -> {
            analysis.applicationLeaks.forEach { leak ->
                // ❌ Найдена цепочка удержания от GC root
                println("Leak: ${leak.leakTraces.first()}")
            }
        }
        is HeapAnalysisFailure -> println("Failed: ${analysis.exception}")
    }
}
```

**3. Проверка retention chain**

Shark находит цепочку ссылок от GC root к объекту, который должен был быть собран:

```
GC Root: Thread (main)
  ↓ HandlerThread.mQueue
  ↓ MessageQueue.mMessages
  ↓ Message.callback (Runnable)
  ↓ Lambda → MainActivity reference
  ↓ MainActivity (LEAKED!)

Retained size: 3.2 MB
```

**Типичные паттерны утечек:**

**Статическая ссылка:**
```kotlin
// ❌ Activity в static поле
companion object {
    var activity: Activity? = null
}

// Trace: GC Root (Class) → static field → Activity
```

**Inner class с неявной ссылкой:**
```kotlin
// ❌ AsyncTask держит неявную ссылку на outer class
class MyActivity : AppCompatActivity() {
    inner class MyTask : AsyncTask<Void, Void, Void>() {
        // this$0 → MyActivity
    }
}
```

**Listener без отписки:**
```kotlin
// ❌ Anonymous listener держит Activity
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    someService.addListener(object : Listener {
        override fun onEvent() { updateUI() }
    })
    // Нет removeListener() в onDestroy()
}
```

**Итоговая логика:**

1. Объект не собран после GC → heap dump
2. Shark строит граф объектов
3. Поиск путей от GC roots к "мертвым" объектам
4. Если путь найден → утечка с retention chain и размером

## Answer (EN)

If an object wasn't freed after garbage collection, LeakCanary creates a **heap dump** and analyzes it using the **Shark library**.

**Leak detection process:**

**1. Heap dump creation**

```kotlin
// LeakCanary checks WeakReference after GC
if (weakReference.get() != null) {
    // ✅ Object should be collected but still alive
    val heapDumpFile = File(heapDumpsDir, "leak-${UUID.randomUUID()}.hprof")
    Debug.dumpHprofData(heapDumpFile.absolutePath)
    analyzeHeap(heapDumpFile)
}
```

**2. Analysis via Shark**

Shark builds an object graph and finds paths from GC roots to suspicious objects:

```kotlin
fun analyzeHeap(heapDumpFile: File) {
    val heapAnalyzer = HeapAnalyzer(OnAnalysisProgressListener.NO_OP)

    val analysis = heapAnalyzer.analyze(
        heapDumpFile = heapDumpFile,
        leakingObjectFinder = FilteringLeakingObjectFinder(
            AndroidObjectInspectors.appLeakingObjectFilters
        ),
        referenceMatchers = AndroidReferenceMatchers.appDefaults,
        computeRetainedHeapSize = true
    )

    when (analysis) {
        is HeapAnalysisSuccess -> {
            analysis.applicationLeaks.forEach { leak ->
                // ❌ Found retention chain from GC root
                println("Leak: ${leak.leakTraces.first()}")
            }
        }
        is HeapAnalysisFailure -> println("Failed: ${analysis.exception}")
    }
}
```

**3. Retention chain verification**

Shark finds reference chains from GC roots to objects that should have been collected:

```
GC Root: Thread (main)
  ↓ HandlerThread.mQueue
  ↓ MessageQueue.mMessages
  ↓ Message.callback (Runnable)
  ↓ Lambda → MainActivity reference
  ↓ MainActivity (LEAKED!)

Retained size: 3.2 MB
```

**Common leak patterns:**

**Static reference:**
```kotlin
// ❌ Activity in static field
companion object {
    var activity: Activity? = null
}

// Trace: GC Root (Class) → static field → Activity
```

**Inner class with implicit reference:**
```kotlin
// ❌ AsyncTask holds implicit reference to outer class
class MyActivity : AppCompatActivity() {
    inner class MyTask : AsyncTask<Void, Void, Void>() {
        // this$0 → MyActivity
    }
}
```

**Listener without unsubscribe:**
```kotlin
// ❌ Anonymous listener holds Activity
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    someService.addListener(object : Listener {
        override fun onEvent() { updateUI() }
    })
    // No removeListener() in onDestroy()
}
```

**Detection logic summary:**

1. Object not collected after GC → heap dump
2. Shark builds object graph
3. Find paths from GC roots to "dead" objects
4. If path exists → leak with retention chain and size

---

## Follow-ups

- How does LeakCanary distinguish between intended long-lived objects and memory leaks?
- What are the performance implications of enabling LeakCanary in debug builds?
- How to configure custom leak detection rules for domain-specific objects?
- What role do reference matchers play in filtering false positives?
- How does Shark optimize heap dump analysis for large applications?

## References

- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Shark Library](https://square.github.io/leakcanary/shark/)
- [[c-memory-management]]
- [[c-garbage-collection]]

## Related Questions

### Prerequisites (Easier)
- [[q-main-thread-android--android--medium]] - Understanding Android threading model
- [[q-activity-lifecycle--android--easy]] - Activity lifecycle and destruction

### Related (Same Level)
- [[q-memory-profiler-android--android--medium]] - Alternative memory analysis tools
- [[q-weakreference-android--android--medium]] - WeakReference usage patterns

### Advanced (Harder)
- [[q-bitmap-memory-optimization--android--hard]] - Memory optimization strategies
- [[q-custom-memory-leak-detection--android--hard]] - Building custom leak detectors
