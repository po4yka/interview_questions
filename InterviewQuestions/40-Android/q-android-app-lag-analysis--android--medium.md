---
id: 20251012-122760
title: "Android App Lag Analysis / Анализ тормозов приложения Android"
aliases: [Android App Lag Analysis, Анализ тормозов приложения Android]
topic: android
subtopics: [performance, ui-optimization]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-android-performance-measurement-tools--android--medium, q-compose-performance-optimization--android--hard, q-strictmode-debugging--android--medium]
created: 2025-10-13
updated: 2025-10-15
tags: [android/performance, android/ui-optimization, performance, ui-optimization, profiling, strictmode, difficulty/medium]
---
# Question (EN)
> Why does an Android app lag? How do you identify and fix performance issues causing UI stuttering and slowness?

# Вопрос (RU)
> Почему Android-приложение тормозит? Как выявить и исправить проблемы производительности, вызывающие зависания UI и медленную работу?

---

## Answer (EN)

App lag occurs when UI thread is blocked or frame rendering exceeds 16ms (60 FPS target). Understanding root causes and using proper diagnostic tools is essential for smooth user experience.

**Common Causes:**

**1. Main Thread Blocking:**
- Synchronous DB/network calls
- Heavy computations
- Solution: Use coroutines, Dispatchers.IO/Default

```kotlin
// BAD: Blocking main thread
fun loadData() {
    val data = database.getAllUsers() // Synchronous DB call
    val result = heavyComputation(data)
    updateUI(result)
}

// GOOD: Async operations
fun loadData() {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) {
            repository.getAllUsers()
        }
        val result = withContext(Dispatchers.Default) {
            heavyComputation(data)
        }
        _uiState.value = UiState.Success(result)
    }
}
```

**2. Memory Issues:**
- Memory leaks
- Excessive allocations
- Solution: LeakCanary, proper lifecycle management

```kotlin
// BAD: Memory leak
companion object {
    private var listener: OnDataListener? = null
}

// GOOD: Proper lifecycle
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { data ->
            updateUI(data)
        }
    }
}
```

**3. Overdraw and Complex Layouts:**
- Deep view hierarchy
- Multiple pixel redraws
- Solution: ConstraintLayout, Compose, minimize nesting

```kotlin
// BAD: Deep hierarchy
<LinearLayout>
    <RelativeLayout>
        <FrameLayout>
            <ConstraintLayout>
                <TextView />
            </ConstraintLayout>
        </FrameLayout>
    </RelativeLayout>
</LinearLayout>

// GOOD: Flat hierarchy
<ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</ConstraintLayout>
```

**4. Unoptimized Lists:**
- No recycling
- No DiffUtil
- Solution: RecyclerView with optimization

```kotlin
// RecyclerView optimization
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
    layoutManager = LinearLayoutManager(context).apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}

// Use DiffUtil for efficient updates
val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(oldItems, newItems))
diffResult.dispatchUpdatesTo(adapter)
```

**5. Poor Image Loading:**
- Loading large images
- Synchronous loading
- Solution: Glide/Coil, sampling, caching

```kotlin
// BAD: Loading large images
imageView.setImageBitmap(BitmapFactory.decodeFile(largeImagePath))

// GOOD: Proper image loading
Glide.with(imageView.context)
    .load(imagePath)
    .override(targetWidth, targetHeight)
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .into(imageView)
```

**Diagnostic Tools:**

**1. GPU Overdraw Detection:**
- Enable: Settings → Developer Options → Debug GPU overdraw
- Colors indicate overdraw levels (blue=2x, green=3x, red=4x+)

**2. Profile GPU Rendering:**
- Enable: Settings → Developer Options → Profile GPU Rendering
- Green line = 16ms target, bars above = dropped frames

**3. StrictMode:**
```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectNetwork()
        .penaltyLog()
        .build()
)
```

**4. Android Profiler:**
- CPU Profiler: Identify hot methods
- Memory Profiler: Find memory leaks
- Network Profiler: Analyze requests
- Energy Profiler: Check battery consumption

**5. LeakCanary:**
- Automatically detects memory leaks in debug builds

## Ответ (RU)

Лаги приложения возникают, когда UI-поток заблокирован или рендеринг кадра превышает 16 мс (целевая частота 60 FPS). Понимание основных причин и использование правильных диагностических инструментов необходимы для плавного пользовательского опыта.

**Основные причины:**

**1. Блокировка главного потока:**
- Синхронные DB/Network вызовы
- Тяжелые вычисления
- Решение: использовать корутины, Dispatchers.IO/Default

```kotlin
// ПЛОХО: Блокировка главного потока
fun loadData() {
    val data = database.getAllUsers() // Синхронный DB вызов
    val result = heavyComputation(data)
    updateUI(result)
}

// ХОРОШО: Асинхронные операции
fun loadData() {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) {
            repository.getAllUsers()
        }
        val result = withContext(Dispatchers.Default) {
            heavyComputation(data)
        }
        _uiState.value = UiState.Success(result)
    }
}
```

**2. Проблемы с памятью:**
- Утечки памяти
- Избыточные аллокации
- Решение: LeakCanary, правильное управление жизненным циклом

```kotlin
// ПЛОХО: Утечка памяти
companion object {
    private var listener: OnDataListener? = null
}

// ХОРОШО: Правильный жизненный цикл
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { data ->
            updateUI(data)
        }
    }
}
```

**3. Overdraw и сложные layouts:**
- Глубокая иерархия view
- Множественная отрисовка пикселей
- Решение: ConstraintLayout, Compose, уменьшение вложенности

```kotlin
// ПЛОХО: Глубокая иерархия
<LinearLayout>
    <RelativeLayout>
        <FrameLayout>
            <ConstraintLayout>
                <TextView />
            </ConstraintLayout>
        </FrameLayout>
    </RelativeLayout>
</LinearLayout>

// ХОРОШО: Плоская иерархия
<ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</ConstraintLayout>
```

**4. Неоптимизированные списки:**
- Без recycling
- Без DiffUtil
- Решение: RecyclerView с оптимизацией

```kotlin
// Оптимизация RecyclerView
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
    layoutManager = LinearLayoutManager(context).apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}

// Использование DiffUtil для эффективных обновлений
val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(oldItems, newItems))
diffResult.dispatchUpdatesTo(adapter)
```

**5. Неправильная загрузка изображений:**
- Загрузка больших изображений
- Синхронная загрузка
- Решение: Glide/Coil, sampling, кэширование

```kotlin
// ПЛОХО: Загрузка больших изображений
imageView.setImageBitmap(BitmapFactory.decodeFile(largeImagePath))

// ХОРОШО: Правильная загрузка изображений
Glide.with(imageView.context)
    .load(imagePath)
    .override(targetWidth, targetHeight)
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .into(imageView)
```

**Инструменты диагностики:**

**1. GPU Overdraw Detection:**
- Включить: Настройки → Параметры разработчика → Отладка GPU overdraw
- Цвета показывают уровни overdraw (синий=2x, зеленый=3x, красный=4x+)

**2. Profile GPU Rendering:**
- Включить: Настройки → Параметры разработчика → Профилирование GPU
- Зеленая линия = цель 16мс, полосы выше = пропущенные кадры

**3. StrictMode:**
```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectDiskReads()
        .detectNetwork()
        .penaltyLog()
        .build()
)
```

**4. Android Profiler:**
- CPU Profiler: Определение горячих методов
- Memory Profiler: Поиск утечек памяти
- Network Profiler: Анализ запросов
- Energy Profiler: Проверка потребления батареи

**5. LeakCanary:**
- Автоматически обнаруживает утечки памяти в debug сборках

---

## Follow-ups

- How do you measure frame rendering performance in production?
- What are the differences between GPU and CPU profiling?
- How do you optimize RecyclerView for large datasets?
- What are the best practices for image loading and caching?
- How do you prevent memory leaks in long-running services?

## References

- [Android Performance Best Practices](https://developer.android.com/topic/performance)
- [GPU Profiling](https://developer.android.com/topic/performance/rendering/profile-gpu)
- [Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [LeakCanary Documentation](https://square.github.io/leakcanary/)

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools
- [[q-strictmode-debugging--android--medium]] - StrictMode debugging

### Related (Medium)
- [[q-compose-performance-optimization--android--hard]] - Compose performance
- [[q-performance-monitoring-jank-compose--android--medium]] - Jank monitoring
- [[q-performance-optimization-android--android--medium]] - Performance optimization

### Advanced (Harder)
- [[q-what-is-layout-performance-measured-in--android--medium]] - Layout performance
- [[q-performance-optimization-android--android--medium]] - Advanced optimization
