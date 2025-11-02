---
id: android-105
title: Анализ тормозов приложения Android / Android App Lag Analysis
aliases: ["Android App Lag Analysis", "Анализ тормозов приложения Android"]
topic: android
subtopics: [performance-memory, performance-rendering, profiling]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - c-android-profiler
  - c-strictmode
  - q-android-performance-measurement-tools--android--medium
created: 2025-10-13
updated: 2025-10-29
sources: []
tags: [android/performance-memory, android/performance-rendering, android/profiling, difficulty/medium, fps, lag, ui-thread]
date created: Wednesday, October 29th 2025, 4:46:47 pm
date modified: Saturday, November 1st 2025, 5:43:37 pm
---

# Вопрос (RU)

> Как диагностировать и устранить задержки (лаги) в Android приложении?

---

# Question (EN)

> How to diagnose and fix lag in Android applications?

---

## Ответ (RU)

### Причина Лагов

Лаги возникают когда рендеринг кадра превышает 16ms (60 FPS) или UI-поток блокирован. Основные причины: блокировка главного потока, утечки памяти, сложная иерархия View, неоптимизированные списки.

### Блокировка Главного Потока

```kotlin
// ❌ Синхронный вызов блокирует UI
fun loadData() {
    val users = database.getAllUsers() // Блокировка!
    val result = heavyComputation(users)
    updateUI(result)
}

// ✅ Асинхронное выполнение
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
// ❌ Статическая ссылка на listener
companion object {
    private var listener: OnDataListener? = null
}

// ✅ Привязка к жизненному циклу
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { updateUI(it) }
    }
}
```

### Оптимизация Списков

```kotlin
// ✅ RecyclerView с DiffUtil
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
}

val diff = DiffUtil.calculateDiff(ItemDiffCallback(oldList, newList))
diff.dispatchUpdatesTo(adapter)
```

### Инструменты Диагностики

**1. Android Profiler** - CPU/Memory/Network анализ в реальном времени

**2. GPU Overdraw** - визуализация перерисовок (Settings → Developer Options)

**3. StrictMode** - обнаружение блокировок потока:

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectNetwork()
        .penaltyLog()
        .build()
)
```

**4. LeakCanary** - автоматическое обнаружение утечек памяти

**5. Systrace/Perfetto** - детальный анализ системных вызовов

### Алгоритм Диагностики

1. Включить GPU Profiling (Settings → Profile GPU Rendering)
2. Запустить Android Profiler и записать сессию
3. Включить StrictMode в debug-сборке
4. Проверить overdraw через Debug GPU Overdraw
5. Использовать Layout Inspector для анализа иерархии
6. Измерить startup time через Macrobenchmark

---

## Answer (EN)

### Root Cause

Lag occurs when frame rendering exceeds 16ms (60 FPS) or the UI thread is blocked. Main causes: main thread blocking, memory leaks, complex view hierarchies, unoptimized lists.

### Main Thread Blocking

```kotlin
// ❌ Synchronous call blocks UI
fun loadData() {
    val users = database.getAllUsers() // Blocks UI!
    val result = heavyComputation(users)
    updateUI(result)
}

// ✅ Async execution
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
// ❌ Static reference to listener
companion object {
    private var listener: OnDataListener? = null
}

// ✅ Lifecycle-aware collection
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { updateUI(it) }
    }
}
```

### List Optimization

```kotlin
// ✅ RecyclerView with DiffUtil
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
}

val diff = DiffUtil.calculateDiff(ItemDiffCallback(oldList, newList))
diff.dispatchUpdatesTo(adapter)
```

### Diagnostic Tools

**1. Android Profiler** - Real-time CPU/Memory/Network analysis

**2. GPU Overdraw** - Visualize pixel redraws (Settings → Developer Options)

**3. StrictMode** - Detect thread violations:

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectNetwork()
        .penaltyLog()
        .build()
)
```

**4. LeakCanary** - Automatic memory leak detection

**5. Systrace/Perfetto** - Detailed system call analysis

### Diagnostic Workflow

1. Enable GPU Profiling (Settings → Profile GPU Rendering)
2. Run Android Profiler and record session
3. Enable StrictMode in debug builds
4. Check overdraw via Debug GPU Overdraw
5. Use Layout Inspector for hierarchy analysis
6. Measure startup time with Macrobenchmark

---

## Follow-ups

- How to measure jank in production with custom metrics?
- What tools can detect layout inflation bottlenecks?
- How does Baseline Profiles improve startup performance?
- When should you use Perfetto instead of Android Profiler?
- How to diagnose Compose recomposition issues causing lag?

## References

- [[c-android-profiler]]
- [[c-strictmode]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-strictmode-debugging--android--medium]]
- https://developer.android.com/topic/performance
- https://developer.android.com/studio/profile

## Related Questions

### Prerequisites
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-strictmode-debugging--android--medium]]

### Related
- [[q-performance-monitoring-jank-compose--android--medium]]

### Advanced