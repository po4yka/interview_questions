---
id: android-094
title: "Frame Time 120ms Meaning / Значение времени кадра 120мс"
aliases: ["Frame Time 120ms Meaning", "Значение времени кадра 120мс"]
topic: android
subtopics: [performance-rendering, profiling, strictmode-anr]
question_kind: theory
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-28
tags: [android/performance-rendering, android/profiling, android/strictmode-anr, difficulty/easy, fps, frame-rate, performance, rendering, ui-performance]
moc: moc-android
related: [c-android-frame-budget, c-choreographer]
sources: []
date created: Tuesday, October 28th 2025, 7:38:35 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

Если профайлер показывает что какой-нибудь фрейм занял 120 миллисекунд, что это значит?

# Question (EN)

If profiler shows that a frame took 120 milliseconds, what does it mean?

---

## Ответ (RU)

Кадр в 120мс означает **критическое превышение бюджета**: вместо целевых 16.67мс (60 fps) приложение пропустило ~7 кадров, что пользователь видит как заметное зависание интерфейса.

**Расчёт:**
```
Целевой бюджет: 1000мс / 60 = 16.67мс на кадр
Фактическое время: 120мс
Пропущено кадров: 120 / 16.67 ≈ 7 кадров
```

**Основные причины:**

1. **Тяжёлые вычисления на главном потоке**
```kotlin
// ПЛОХО: блокирует UI-поток
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val processed = heavyProcessing(data[position])  // 120мс!
    holder.bind(processed)
}

// ХОРОШО: переносим в фоновый поток
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    viewModelScope.launch(Dispatchers.Default) {
        val processed = heavyProcessing(data[position])
        withContext(Dispatchers.Main) { holder.bind(processed) }
    }
}
```

2. **Синхронные I/O операции**
```kotlin
// ПЛОХО: блокирующий вызов БД
button.setOnClickListener {
    val data = database.query()  // Блокирует UI!
    updateUI(data)
}

// ХОРОШО: асинхронно
button.setOnClickListener {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) { database.query() }
        updateUI(data)
    }
}
```

3. **Неэффективная отрисовка** — множественные layout inflations, отсутствие view recycling

**Измерение производительности:**
```kotlin
Choreographer.getInstance().postFrameCallback(object : Choreographer.FrameCallback {
    var lastFrameTime = 0L
    override fun doFrame(frameTimeNanos: Long) {
        if (lastFrameTime != 0L) {
            val frameDuration = (frameTimeNanos - lastFrameTime) / 1_000_000
            if (frameDuration > 16) Log.w("Perf", "Slow frame: ${frameDuration}ms")
        }
        lastFrameTime = frameTimeNanos
        Choreographer.getInstance().postFrameCallback(this)
    }
})
```

**Критерии производительности:**
- **< 16мс** — плавно (60 fps)
- **16-33мс** — заметно, но терпимо (30-60 fps)
- **120мс** — явные тормоза (8 fps)
- **> 5000мс** — риск ANR

**Решение:** профилировать с помощью Systrace/Perfetto, переносить тяжёлую работу на Dispatchers.Default/IO, оптимизировать layout hierarchy, использовать RecyclerView с DiffUtil.

## Answer (EN)

A 120ms frame represents a **critical budget overrun**: instead of the target 16.67ms (60 fps), the app dropped ~7 frames, resulting in visible UI stuttering.

**Calculation:**
```
Target budget: 1000ms / 60 = 16.67ms per frame
Actual time: 120ms
Dropped frames: 120 / 16.67 ≈ 7 frames
```

**Root Causes:**

1. **Heavy work on main thread**
```kotlin
// BAD: blocks UI thread
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val processed = heavyProcessing(data[position])  // 120ms!
    holder.bind(processed)
}

// GOOD: offload to background
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    viewModelScope.launch(Dispatchers.Default) {
        val processed = heavyProcessing(data[position])
        withContext(Dispatchers.Main) { holder.bind(processed) }
    }
}
```

2. **Synchronous I/O**
```kotlin
// BAD: blocking database call
button.setOnClickListener {
    val data = database.query()  // Blocks UI!
    updateUI(data)
}

// GOOD: async
button.setOnClickListener {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) { database.query() }
        updateUI(data)
    }
}
```

3. **Inefficient rendering** — multiple layout inflations, missing view recycling

**Performance Monitoring:**
```kotlin
Choreographer.getInstance().postFrameCallback(object : Choreographer.FrameCallback {
    var lastFrameTime = 0L
    override fun doFrame(frameTimeNanos: Long) {
        if (lastFrameTime != 0L) {
            val frameDuration = (frameTimeNanos - lastFrameTime) / 1_000_000
            if (frameDuration > 16) Log.w("Perf", "Slow frame: ${frameDuration}ms")
        }
        lastFrameTime = frameTimeNanos
        Choreographer.getInstance().postFrameCallback(this)
    }
})
```

**Performance Criteria:**
- **< 16ms** — smooth (60 fps)
- **16-33ms** — noticeable but acceptable (30-60 fps)
- **120ms** — janky (8 fps)
- **> 5000ms** — ANR risk

**Solution:** Profile with Systrace/Perfetto, move heavy work to Dispatchers.Default/IO, optimize layout hierarchy, use RecyclerView with DiffUtil.

---

## Follow-ups

- What's the difference between frame time and render time?
- How does Choreographer relate to vsync?
- When would you use strictMode to detect main thread violations?
- How do you diagnose which specific phase (measure/layout/draw) is slow?

## References

- Android Developer Guide: [Performance & Rendering](https://developer.android.com/topic/performance/rendering)
- Systrace/Perfetto for detailed frame analysis
- [[c-android-frame-budget]] — frame budget and vsync concepts
- [[c-choreographer]] — frame scheduling and callbacks

## Related Questions

### Prerequisites
- Understanding of Android UI rendering pipeline
- Basic knowledge of frame rate and vsync

### Related

### Advanced
- [[q-systrace-analysis--android--hard]] — advanced profiling techniques
- [[q-custom-view-performance--android--medium]] — optimizing custom drawing
