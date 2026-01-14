---
id: android-105
title: Анализ тормозов приложения Android / Android App Lag Analysis
aliases:
- Android App Lag Analysis
- Анализ тормозов приложения Android
topic: android
subtopics:
- performance-memory
- performance-rendering
- profiling
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-profiling
- q-android-app-components--android--easy
- q-android-performance-measurement-tools--android--medium
- q-app-start-types-android--android--medium
- q-reduce-app-size--android--medium
created: 2025-10-13
updated: 2025-11-10
sources: []
tags:
- android/performance-memory
- android/performance-rendering
- android/profiling
- difficulty/medium
- fps
- lag
- ui-thread
anki_cards:
- slug: android-105-0-en
  language: en
  anki_id: 1768363328821
  synced_at: '2026-01-14T09:17:53.792976'
- slug: android-105-0-ru
  language: ru
  anki_id: 1768363328846
  synced_at: '2026-01-14T09:17:53.795195'
---
# Вопрос (RU)

> Как диагностировать и устранить задержки (лаги) в Android приложении?

---

# Question (EN)

> How to diagnose and fix lag in Android applications?

---

## Ответ (RU)

### Причина Лагов

Лаги возникают, когда время рендеринга кадра превышает бюджет времени, зависящий от частоты обновления экрана (≈16.6ms для 60 Гц, ≈11.1ms для 90 Гц, ≈8.3ms для 120 Гц), или когда UI-поток блокирован и не может обработать input/рендеринг вовремя. Основные причины: блокировка главного потока, утечки памяти (приводящие к частым/долгим GC-паузам и фризам), слишком сложная иерархия `View`, неоптимизированные списки и тяжёлые операции при рендеринге.

См. также: [[c-android-profiling]].

### Блокировка Главного Потока

```kotlin
// ❌ Синхронный вызов блокирует UI
fun loadData() {
    val users = database.getAllUsers() // Блокировка!
    val result = heavyComputation(users)
    updateUI(result)
}

// ✅ Асинхронное выполнение (без блокировки UI-потока)
fun loadData() {
    viewModelScope.launch {
        val users = withContext(Dispatchers.IO) {
            repository.getAllUsers()
        }
        val result = withContext(Dispatchers.Default) {
            heavyComputation(users)
        }
        _uiState.value = UiState.Success(result)
    }
}
```

### Утечки Памяти

```kotlin
// ❌ Статическая/долгоживущая ссылка удерживает Activity/Context/View и может вызвать утечку
companion object {
    private var listener: OnDataListener? = null // если listener ссылается на View/Activity
}

// ✅ Привязка к жизненному циклу и отсутствие статических ссылок на UI-объекты
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { updateUI(it) }
    }
}
```

### Оптимизация Списков

```kotlin
// ✅ RecyclerView с DiffUtil для инкрементальных обновлений (уменьшение перерисовок)
recyclerView.apply {
    // Использовать setHasFixedSize(true), только если размер элементов не зависит от содержимого
    setHasFixedSize(true)
    // Настроить кэш размера в зависимости от сценария; не завышать без необходимости
    setItemViewCacheSize(20)
}

val diff = DiffUtil.calculateDiff(ItemDiffCallback(oldList, newList))
diff.dispatchUpdatesTo(adapter)
```

### Инструменты Диагностики

**1. Android Profiler** - CPU/Memory/Network анализ в реальном времени, запись профилей.

**2. GPU Overdraw** - визуализация перерисовок (Settings → Developer Options → Debug GPU Overdraw).

**3. StrictMode** - обнаружение блокировок главного потока и медленных операций (использовать в debug-сборках):

```kotlin
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
        .detectLeakedSqlLiteObjects()
        .penaltyLog()
        .build()
)
```

**4. LeakCanary** - автоматическое обнаружение утечек памяти.

**5. Systrace/Perfetto** - детальный анализ системных трасс и jank (Frame Timeline, scheduler, GC и т.д.).

### Алгоритм Диагностики

1. Включить Profile GPU Rendering для оценки времени рендеринга кадров.
2. Запустить Android Profiler и записать сессию (CPU/Memory/Network) вокруг проблемных сценариев.
3. Включить StrictMode в debug-сборке для выявления операций ввода-вывода и сети в главном потоке.
4. Проверить overdraw через Debug GPU Overdraw и упростить layout-ы при необходимости.
5. Использовать Layout Inspector для анализа глубины иерархии и "тяжёлых" вью.
6. Использовать Perfetto/Systrace или Frame Timeline в Android Studio для анализа jank и долгих кадров.
7. Измерить startup time через Macrobenchmark и устранить тяжёлые операции на пути запуска.

---

## Answer (EN)

### Root Cause

Lag occurs when frame rendering exceeds the time budget defined by the display refresh rate (~16.6ms for 60Hz, ~11.1ms for 90Hz, ~8.3ms for 120Hz), or when the UI thread is blocked and cannot handle input/rendering on time. Main causes: main thread blocking, memory leaks (leading to frequent/long GC pauses and freezes), overly complex view hierarchies, unoptimized lists, and heavy work done on the critical rendering path.

See also: [[c-android-profiling]].

### Main Thread Blocking

```kotlin
// ❌ Synchronous call blocks UI
fun loadData() {
    val users = database.getAllUsers() // Blocks UI!
    val result = heavyComputation(users)
    updateUI(result)
}

// ✅ Async execution (keeps UI thread responsive)
fun loadData() {
    viewModelScope.launch {
        val users = withContext(Dispatchers.IO) {
            repository.getAllUsers()
        }
        val result = withContext(Dispatchers.Default) {
            heavyComputation(users)
        }
        _uiState.value = UiState.Success(result)
    }
}
```

### Memory Leaks

```kotlin
// ❌ Static/long-lived reference holds Activity/Context/View and may cause leak
companion object {
    private var listener: OnDataListener? = null // if listener captures View/Activity/Context
}

// ✅ Lifecycle-aware collection and no static references to UI objects
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { updateUI(it) }
    }
}
```

### `List` Optimization

```kotlin
// ✅ RecyclerView with DiffUtil for incremental updates to reduce unnecessary redraws
recyclerView.apply {
    // Use setHasFixedSize(true) only when item sizes are stable and not data-dependent
    setHasFixedSize(true)
    // Tune item view cache size based on scenario; avoid oversizing without reason
    setItemViewCacheSize(20)
}

val diff = DiffUtil.calculateDiff(ItemDiffCallback(oldList, newList))
diff.dispatchUpdatesTo(adapter)
```

### Diagnostic Tools

**1. Android Profiler** - Real-time CPU/Memory/Network analysis and profiling.

**2. GPU Overdraw** - Visualize overdraw (Settings → Developer Options → Debug GPU Overdraw).

**3. StrictMode** - Detect main thread violations and slow operations (use in debug builds):

```kotlin
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
        .detectLeakedSqlLiteObjects()
        .penaltyLog()
        .build()
)
```

**4. LeakCanary** - Automatic memory leak detection.

**5. Systrace/Perfetto** - Detailed system trace and jank analysis (Frame Timeline, GC, scheduling, etc.).

### Diagnostic Workflow

1. Enable Profile GPU Rendering to inspect frame rendering times.
2. Run Android Profiler and record CPU/Memory/Network around problematic flows.
3. Enable StrictMode in debug builds to catch disk/network operations on the main thread.
4. Check overdraw via Debug GPU Overdraw and simplify layouts where needed.
5. Use Layout Inspector to analyze hierarchy depth and heavy views.
6. Use Perfetto/Systrace or Frame Timeline in Android Studio to analyze jank and long frames.
7. Measure startup time with Macrobenchmark and remove heavy work from the startup path.

---

## Дополнительные Вопросы (RU)

- Как измерять jank в продакшене с помощью кастомных метрик?
- Какие инструменты помогают находить узкие места при инфлейте layout-ов?
- Как Baseline Profiles улучшают производительность запуска?
- Когда стоит использовать Perfetto вместо Android Profiler?
- Как диагностировать проблемы рекомпозиции в Compose, вызывающие лаги?

## Ссылки (RU)

- [[q-android-performance-measurement-tools--android--medium]]
- [[q-strictmode-debugging--android--medium]]
- [Performance](https://developer.android.com/topic/performance)
- [Profiling](https://developer.android.com/studio/profile)

## Связанные Вопросы (RU)

### Предпосылки / Концепты

### Предпосылки

- [[q-android-performance-measurement-tools--android--medium]]
- [[q-strictmode-debugging--android--medium]]

### Связанные

- [[q-performance-monitoring-jank-compose--android--medium]]

---

## Follow-ups

- How to measure jank in production with custom metrics?
- What tools can detect layout inflation bottlenecks?
- How does Baseline Profiles improve startup performance?
- When should you use Perfetto instead of Android Profiler?
- How to diagnose Compose recomposition issues causing lag?

## References

- [[q-android-performance-measurement-tools--android--medium]]
- [[q-strictmode-debugging--android--medium]]
- [Performance](https://developer.android.com/topic/performance)
- [Profiling](https://developer.android.com/studio/profile)

## Related Questions

### Prerequisites / Concepts

### Prerequisites

- [[q-android-performance-measurement-tools--android--medium]]
- [[q-strictmode-debugging--android--medium]]

### Related

- [[q-performance-monitoring-jank-compose--android--medium]]
