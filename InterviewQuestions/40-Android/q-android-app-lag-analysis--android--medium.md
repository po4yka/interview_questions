---
id: 20251012-122700
title: Анализ тормозов приложения Android / Android App Lag Analysis
aliases:
  - Анализ тормозов приложения Android
  - Android App Lag Analysis
  - App Performance Analysis
  - Анализ производительности приложения
topic: android
subtopics: [performance-memory, performance-rendering]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-performance-measurement-tools--android--medium
  - q-compose-performance-optimization--android--hard
  - q-strictmode-debugging--android--medium
created: 2025-10-13
updated: 2025-10-27
sources:
  - https://developer.android.com/topic/performance
  - https://developer.android.com/studio/profile
tags:
  - android/performance-memory
  - android/performance-rendering
  - profiling
  - strictmode
  - difficulty/medium
---

# Вопрос (RU)

> Как диагностировать и устранить задержки (лаги) в Android приложении?

---

# Question (EN)

> How to diagnose and fix lag in Android applications?

---

## Ответ (RU)

Лаги возникают при блокировке UI-потока или когда рендеринг кадра превышает 16ms (цель 60 FPS). Необходимо понимать причины и использовать инструменты профилирования.

**Основные причины лагов:**

**1. Блокировка главного потока:**
- Синхронные вызовы БД/сети
- Тяжелые вычисления на UI-потоке

```kotlin
// ❌ Плохо: блокировка главного потока
fun loadData() {
    val data = database.getAllUsers() // Синхронный вызов БД
    val result = heavyComputation(data)
    updateUI(result)
}

// ✅ Хорошо: асинхронные операции
fun loadData() {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) {
            repository.getAllUsers() // В фоне
        }
        val result = withContext(Dispatchers.Default) {
            heavyComputation(data) // В фоне
        }
        _uiState.value = UiState.Success(result)
    }
}
```

**2. Утечки памяти:**
- Статические ссылки на Context/View
- Несвоевременная отписка от слушателей

```kotlin
// ❌ Плохо: утечка памяти
companion object {
    private var listener: OnDataListener? = null
}

// ✅ Хорошо: корректное управление жизненным циклом
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { data ->
            updateUI(data)
        }
    }
}
```

**3. Сложные layouts:**
- Глубокая вложенность View
- Множественная перерисовка пикселей (overdraw)

**4. Неоптимизированные списки:**
- Отсутствие RecyclerView
- Неиспользование DiffUtil

```kotlin
// Оптимизация RecyclerView
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
}

val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(oldItems, newItems))
diffResult.dispatchUpdatesTo(adapter)
```

**Инструменты диагностики:**

1. **Android Profiler** - CPU/Memory/Network анализ
2. **GPU Overdraw** - визуализация перерисовок
3. **StrictMode** - обнаружение блокировок потока
4. **LeakCanary** - автоматическое обнаружение утечек памяти

## Answer (EN)

App lag occurs when the UI thread is blocked or frame rendering exceeds 16ms (60 FPS target). Understanding root causes and using proper diagnostic tools is essential.

**Common Causes:**

**1. Main Thread Blocking:**
- Synchronous DB/network calls on UI thread
- Heavy computations blocking rendering

```kotlin
// ❌ Bad: Blocking main thread
fun loadData() {
    val data = database.getAllUsers() // Synchronous DB call
    updateUI(data)
}

// ✅ Good: Async operations
fun loadData() {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) {
            repository.getAllUsers() // Background thread
        }
        _uiState.value = UiState.Success(data)
    }
}
```

**2. Memory Leaks:**
- Static references to Context/View
- Unsubscribed listeners

```kotlin
// ❌ Bad: Memory leak
companion object {
    private var listener: OnDataListener? = null
}

// ✅ Good: Proper lifecycle management
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { data ->
            updateUI(data)
        }
    }
}
```

**3. Complex Layouts:**
- Deep view hierarchy
- Multiple overdraw passes

**4. Unoptimized Lists:**
- Missing RecyclerView optimizations
- No DiffUtil usage

```kotlin
// RecyclerView optimization
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
}

val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(oldList, newList))
diffResult.dispatchUpdatesTo(adapter)
```

**Diagnostic Tools:**

1. **Android Profiler** - CPU/Memory/Network analysis
2. **GPU Overdraw** - Visualize pixel redraws
3. **StrictMode** - Detect thread violations
4. **LeakCanary** - Automatic leak detection

```kotlin
// StrictMode setup
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectNetwork()
        .penaltyLog()
        .build()
)
```

---

## Follow-ups

- How to measure frame rendering in production?
- What's the difference between GPU and CPU profiling?
- How to optimize RecyclerView for large datasets?

## References

- [[q-strictmode-debugging--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

## Related Questions

### Same Level
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-performance-monitoring-jank-compose--android--medium]]

### Advanced
- [[q-compose-performance-optimization--android--hard]]