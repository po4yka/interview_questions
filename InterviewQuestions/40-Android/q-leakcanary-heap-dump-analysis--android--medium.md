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
updated: 2025-11-11
tags: [android/performance-memory, difficulty/medium, heap-dump, leakcanary, memory-analysis, shark]
moc: moc-android
related: [c-android-profiling, q-leakcanary-detection-mechanism--android--medium]
sources: []

date created: Saturday, November 1st 2025, 1:25:01 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---
# Вопрос (RU)

> Как понять что в heap dump есть утечка памяти?

# Question (EN)

> How to detect a memory leak in a heap dump?

---

## Ответ (RU)

Если наблюдаемый (watched) LeakCanary объект не был освобожден после нескольких циклов GC и задержки, LeakCanary создает **heap dump** (снимок кучи) и анализирует его библиотекой **Shark**. Важно: сама проверка "утечки" делается не по `WeakReference.get()` во время работы, а по тому, что объект, который должен был стать недостижимым, все еще сильно достижим в дампе памяти.

Ниже — упрощенная концептуальная схема (код иллюстративный, не реальный продакшн-код LeakCanary).

**Процесс обнаружения утечки (упрощенно):**

**1. Мониторинг и создание heap dump**

LeakCanary оборачивает наблюдаемые объекты в `KeyedWeakReference`, ждет несколько GC и задержку. Если `WeakReference` очистилась — считаем, что утечки нет. Если же по внутренним маркерам видно, что объект не был собран, и выполняются условия для анализа, создается heap dump:

```kotlin
// Концептуально: если объект должен был быть собран, но признаки указывают, что он удерживается,
// запускается снятие дампа памяти (упрощенная иллюстрация, не реальный код LeakCanary)
if (shouldHaveBeenCollectedButIsStillRetained) {
    val heapDumpFile = File(heapDumpsDir, "leak-${UUID.randomUUID()}.hprof")
    Debug.dumpHprofData(heapDumpFile.absolutePath)
    analyzeHeap(heapDumpFile)
}
```

Ключевая идея: мы анализируем дамп, когда ожидаемый к сборке объект по-прежнему, по признакам, удерживается в памяти.

**2. Анализ через Shark**

Shark строит граф объектов и находит пути от GC roots до подозрительных объектов — в частности, до watched-объектов, которые по логике должны были стать недостижимыми, но остались сильно достижимыми.

```kotlin
// Концептуальный пример использования Shark API — реальные API/версии могут отличаться
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
                // ❌ Найдена цепочка удержания (retention chain) от GC root до объекта,
                // который должен был быть собран
                println("Leak: ${leak.leakTraces.first()}")
            }
        }
        is HeapAnalysisFailure -> println("Failed: ${analysis.exception}")
    }
}
```

На практике LeakCanary использует собственную обертку над Shark; приведенный код только демонстрирует идею: строим граф, ищем удерживаемые watched-объекты.

**3. Проверка retention chain**

Shark ищет цепочку сильных ссылок от GC root к объекту, который по логике приложения должен был стать недостижимым, но остается удержан. Если такой путь существует и не отфильтрован как допустимый (через reference matchers и leak filters), то это считается утечкой памяти.

```text
GC Root: Thread (main)
  ↓ HandlerThread.mQueue
  ↓ MessageQueue.mMessages
  ↓ Message.callback (Runnable)
  ↓ Lambda → MainActivity reference
  ↓ MainActivity (LEAKED!)

Retained size: 3.2 MB
```

**Типичные паттерны утечек (видны по retention chain в heap dump):**

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

**Итоговая логика (как понять, что в heap dump есть утечка):**

1. Есть watched-объект, чей жизненный цикл завершен — он должен стать недостижимым.
2. После нескольких GC и задержки снимается heap dump для проверки.
3. Shark строит граф объектов.
4. Ищутся пути от GC roots к этому объекту.
5. Если объект все еще сильно достижим, и цепочка удержания не попадает под известные безопасные паттерны (reference matchers), это считается утечкой. LeakCanary показывает retention chain и удержанный размер памяти.

---

## Answer (EN)

If a watched object tracked by LeakCanary is still suspected to be retained after several GC cycles and a delay, LeakCanary creates a **heap dump** and analyzes it using the **Shark library**. Importantly, leak verification is not based on directly checking `WeakReference.get()` at runtime, but on seeing in the heap dump that an object which should be unreachable is still strongly reachable from a GC root.

Below is a simplified conceptual flow (code is illustrative, not the exact production LeakCanary implementation).

**Leak detection process (simplified):**

**1. Monitoring and heap dump creation**

LeakCanary wraps watched objects in a `KeyedWeakReference`, waits for a few GC cycles and a delay. If the weak reference is cleared, there is no leak. If its internal markers indicate the object should have been collected but appears retained, LeakCanary triggers a heap dump for analysis:

```kotlin
// Conceptual: when an object should have been collected but indicators show it is still retained,
// trigger heap dump (simplified illustration, not real LeakCanary code)
if (shouldHaveBeenCollectedButIsStillRetained) {
    val heapDumpFile = File(heapDumpsDir, "leak-${UUID.randomUUID()}.hprof")
    Debug.dumpHprofData(heapDumpFile.absolutePath)
    analyzeHeap(heapDumpFile)
}
```

The key idea: we analyze the heap when an object expected to be garbage collected is suspected to still be held.

**2. Analysis via Shark**

Shark builds an object graph and finds paths from GC roots to suspicious objects — especially watched objects that should have become unreachable but remain strongly reachable.

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
                // ❌ Retention chain from GC root to an object that should have been collected
                println("Leak: ${leak.leakTraces.first()}")
            }
        }
        is HeapAnalysisFailure -> println("Failed: ${analysis.exception}")
    }
}
```

In practice, LeakCanary uses its own integration layer over Shark; this code only conveys the idea: build the graph, look for retained watched objects.

**3. Retention chain verification**

Shark looks for strong reference chains from GC roots to an object that, according to app logic, should no longer be reachable but is still retained. If such a path exists and is not filtered out as allowed (through reference matchers / leak filters), it is treated as a memory leak.

```text
GC Root: Thread (main)
  ↓ HandlerThread.mQueue
  ↓ MessageQueue.mMessages
  ↓ Message.callback (Runnable)
  ↓ Lambda → MainActivity reference
  ↓ MainActivity (LEAKED!)

Retained size: 3.2 MB
```

**Common leak patterns (visible as retention chains in the heap dump):**

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

**Detection logic summary (how to tell there is a leak in the heap dump):**

1. There is a watched object whose lifecycle is finished — it is expected to be unreachable.
2. After several GC cycles and a delay, a heap dump is captured to verify that assumption.
3. Shark builds the object graph.
4. It searches for paths from GC roots to this object.
5. If the object is still strongly reachable, and the retention chain is not classified as safe by known reference matchers / leak filters, it is treated as a memory leak. LeakCanary then reports the retention chain and the retained heap size.

---

## Дополнительные Вопросы (RU)

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

## References

- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Shark Library](https://square.github.io/leakcanary/shark/)

---

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-main-thread-android--android--medium]] - Понимание модели потоков в Android

### Связанные (того Же уровня)
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
