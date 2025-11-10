---
id: android-089
title: "LeakCanary Heap Dump Analysis / Анализ дампа памяти в LeakCanary"
aliases: ["LeakCanary Heap Dump Analysis", "Анализ дампа памяти в LeakCanary"]
topic: android
subtopics: [performance-memory]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-10
tags: [android/performance-memory, difficulty/medium, heap-dump, leakcanary, memory-analysis, shark]
moc: moc-android
related: [q-leakcanary-detection-mechanism--android--medium]
sources: []

---

# Вопрос (RU)

> Как понять что в heap dump есть утечка памяти?

# Question (EN)

> How to detect a memory leak in a heap dump?

---

## Ответ (RU)

Если наблюдаемый (watched) LeakCanary объект не был освобожден после нескольких циклов GC и задержки, LeakCanary создает **heap dump** (снимок кучи) и анализирует его библиотекой **Shark**.

Ниже — упрощенная концептуальная схема (код иллюстративный, не реальный продакшн-код LeakCanary).

**Процесс обнаружения утечки:**

**1. Создание heap dump**

```kotlin
// Концептуально: LeakCanary отслеживает watched-объекты через WeakReference
if (weakReference.get() != null) {
    // ✅ Объект должен был быть собран (мы закончили его жизненный цикл), но он все еще достижим
    val heapDumpFile = File(heapDumpsDir, "leak-${UUID.randomUUID()}.hprof")
    Debug.dumpHprofData(heapDumpFile.absolutePath)
    analyzeHeap(heapDumpFile)
}
```

**2. Анализ через Shark**

Shark строит граф объектов и находит пути от GC roots до подозрительных объектов (watched-объектов, которые не освободились):

```kotlin
// Концептуальный пример использования Shark API — реальные версии могут отличаться
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
                // ❌ Найдена цепочка удержания (retention chain) от GC root до watched-объекта
                println("Leak: ${leak.leakTraces.first()}")
            }
        }
        is HeapAnalysisFailure -> println("Failed: ${analysis.exception}")
    }
}
```

**3. Проверка retention chain**

Shark ищет цепочку сильных ссылок от GC root к объекту, который по логике приложения должен был стать недостижимым, но остается удержан:

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

**`Listener` без отписки:**
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

1. Watched-объект не собран после нескольких GC и задержки → создается heap dump
2. Shark строит граф объектов
3. Ищутся пути от GC roots к объектам, которые по ожиданию должны были стать недостижимыми
4. Если такой путь найден (есть retention chain) → считается утечкой; показываются цепочка удержания и удержанный размер памяти

---

## Answer (EN)

If a watched object tracked by LeakCanary is still not freed after several GC cycles and a delay, LeakCanary creates a **heap dump** and analyzes it using the **Shark library**.

Below is a simplified conceptual flow (code is illustrative, not the exact production LeakCanary implementation).

**Leak detection process:**

**1. Heap dump creation**

```kotlin
// Conceptually: LeakCanary tracks watched objects via WeakReference
if (weakReference.get() != null) {
    // ✅ Object should have been collected (its lifecycle is finished), but it is still reachable
    val heapDumpFile = File(heapDumpsDir, "leak-${UUID.randomUUID()}.hprof")
    Debug.dumpHprofData(heapDumpFile.absolutePath)
    analyzeHeap(heapDumpFile)
}
```

**2. Analysis via Shark**

Shark builds an object graph and finds paths from GC roots to suspicious objects (watched objects that were expected to be collected but are still strongly reachable):

```kotlin
// Conceptual example of using Shark API — actual APIs/versions may differ
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
                // ❌ Retention chain from GC root to watched object found
                println("Leak: ${leak.leakTraces.first()}")
            }
        }
        is HeapAnalysisFailure -> println("Failed: ${analysis.exception}")
    }
}
```

**3. Retention chain verification**

Shark looks for strong reference chains from GC roots to an object that, according to app logic, should no longer be reachable but is still retained:

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

**`Listener` without unsubscribe:**
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

1. Watched object not collected after several GC cycles and delay → heap dump is created
2. Shark builds the object graph
3. Find paths from GC roots to objects that were expected to become unreachable
4. If such a retention chain exists → treated as a leak; LeakCanary reports the chain and retained heap size

---

## Дополнительные вопросы (RU)

- Как LeakCanary отличает намеренно долго живущие объекты от утечек памяти?
- Каковы накладные расходы по производительности при использовании LeakCanary в debug-сборках?
- Как настроить пользовательские правила детекции утечек для доменных объектов?
- Какую роль играют reference matchers в фильтрации ложных срабатываний?
- Как Shark оптимизирует анализ heap dump для крупных приложений?

## Follow-ups

- How does LeakCanary distinguish between intended long-lived objects and memory leaks?
- What are the performance implications of enabling LeakCanary in debug builds?
- How to configure custom leak detection rules for domain-specific objects?
- What role do reference matchers play in filtering false positives?
- How does Shark optimize heap dump analysis for large applications?

---

## Ссылки (RU)

- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Shark Library](https://square.github.io/leakcanary/shark/)
- [[c-garbage-collection]]

## References

- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Shark Library](https://square.github.io/leakcanary/shark/)
- [[c-garbage-collection]]

---

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-main-thread-android--android--medium]] - Понимание модели потоков в Android

### Связанные (того же уровня)
- [[q-leakcanary-detection-mechanism--android--medium]] - Как LeakCanary обнаруживает утечки
- [[q-memory-leak-detection--android--medium]] - Общие подходы к обнаружению утечек памяти
- [[q-memory-leak-vs-oom-android--android--medium]] - Утечки памяти vs OOM
- [[q-optimize-memory-usage-android--android--medium]] - Оптимизация использования памяти

### Продвинутые (сложнее)
- [[q-android-runtime-internals--android--hard]] - ART и работа с памятью
- [[q-fix-slow-app-startup-legacy--android--hard]] - Оптимизация производительности
- [[q-sensitive-data-lifecycle--android--hard]] - Управление жизненным циклом чувствительных данных

## Related Questions

### Prerequisites (Easier)
- [[q-main-thread-android--android--medium]] - Understanding Android threading model

### Related (Same Level)
- [[q-leakcanary-detection-mechanism--android--medium]] - How LeakCanary detects leaks
- [[q-memory-leak-detection--android--medium]] - General leak detection strategies
- [[q-memory-leak-vs-oom-android--android--medium]] - Memory leaks vs OOM
- [[q-optimize-memory-usage-android--android--medium]] - Memory optimization

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - ART runtime and memory
- [[q-fix-slow-app-startup-legacy--android--hard]] - Performance optimization
- [[q-sensitive-data-lifecycle--android--hard]] - Data lifecycle management
