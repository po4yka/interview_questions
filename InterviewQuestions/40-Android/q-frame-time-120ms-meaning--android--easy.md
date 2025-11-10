---
id: android-094
title: "Frame Time 120ms Meaning / Значение времени кадра 120мс"
aliases: ["Frame Time 120ms Meaning", "Значение времени кадра 120мс"]
topic: android
subtopics: [performance-rendering, profiling]
question_kind: theory
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-10
tags: [android/performance-rendering, android/profiling, difficulty/easy, fps, frame-rate, performance, rendering, ui-performance]
moc: moc-android
related: [c-android-basics, c-android-profiling, q-android-performance-measurement-tools--android--medium]
sources: []
---

# Вопрос (RU)

> Если профайлер показывает что какой-нибудь фрейм занял 120 миллисекунд, что это значит?

# Question (EN)

> If profiler shows that a frame took 120 milliseconds, what does it mean?

---

## Ответ (RU)

Кадр в 120мс означает **критическое превышение бюджета**: вместо целевых 16.67мс (60 fps) приложение пропустило примерно 7 кадров подряд относительно идеального расписания, что пользователь видит как заметное зависание интерфейса (jank / hitch).

**Расчёт:**
```
Целевой бюджет: 1000мс / 60 ≈ 16.67мс на кадр
Фактическое время: 120мс
Пропущено кадров: 120 / 16.67 ≈ 7 кадров
```

Важно: один кадр в 120мс не означает «приложение работает в 8 fps» постоянно, но отражает единичный серьёзный провал по времени кадра.

**Основные причины:**

1. **Тяжёлые вычисления на главном потоке**
```kotlin
// ПЛОХО: блокирует UI-поток во время биндинга
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val processed = heavyProcessing(data[position])  // 120мс!
    holder.bind(processed)
}

// Лучше: перенести тяжёлую работу с главного потока
// (в реальном коде важно учитывать переиспользование ViewHolder и отмену работы)
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Пример для иллюстрации идеи offload, не production-ready
    CoroutineScope(Dispatchers.Default).launch {
        val processed = heavyProcessing(data[position])
        withContext(Dispatchers.Main) {
            holder.bind(processed)
        }
    }
}
```

2. **Синхронные I/O операции**
```kotlin
// ПЛОХО: блокирующий вызов БД на UI-потоке
button.setOnClickListener {
    val data = database.query()  // Блокирует UI!
    updateUI(data)
}

// ХОРОШО: асинхронно (работа уходит с главного потока)
button.setOnClickListener {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) { database.query() }
        updateUI(data)
    }
}
```

3. **Неэффективная отрисовка** — множественные layout inflations, глубокая и тяжёлая иерархия, отсутствие view recycling.

**Измерение производительности (упрощённо):**
```kotlin
Choreographer.getInstance().postFrameCallback(object : Choreographer.FrameCallback {
    var lastFrameTime = 0L
    override fun doFrame(frameTimeNanos: Long) {
        if (lastFrameTime != 0L) {
            val frameDurationMs = (frameTimeNanos - lastFrameTime) / 1_000_000
            if (frameDurationMs > 17) {
                Log.w("Perf", "Slow frame: ${frameDurationMs}ms")
            }
        }
        lastFrameTime = frameTimeNanos
        Choreographer.getInstance().postFrameCallback(this)
    }
})
```
(Это пример для понимания принципа; для детального анализа используйте системные инструменты, см. также [[c-android-basics]] и [[c-android-profiling]].)

**Критерии производительности (для 60 Гц дисплея):**
- **< ~16.67мс** — плавно (60 fps)
- **~16.67-33мс** — может быть заметно, но терпимо (30-60 fps)
- **~120мс** — явный jank / «фриз» кадра
- **≈5000мс на главном потоке** — высокий риск ANR для input/broadcast (5с), для некоторых случаев (service) порог 10с; настолько долгие блокировки недопустимы.

**Решение:** профилировать с помощью Perfetto/Trace, переносить тяжёлую работу на Dispatchers.Default/IO и off-main механизмы, оптимизировать layout hierarchy, использовать RecyclerView с корректным recycling и DiffUtil.

## Answer (EN)

A 120ms frame represents a **critical frame time budget overrun**: instead of the target 16.67ms (60 fps), the app missed roughly 7 vsync intervals for that frame, which appears to the user as noticeable jank / a hitch.

**Calculation:**
```
Target budget: 1000ms / 60 ≈ 16.67ms per frame
Actual time: 120ms
Missed intervals (dropped opportunities): 120 / 16.67 ≈ 7
```

Note: a single 120ms frame does not mean the app is "running at 8 fps" overall; it indicates one severe slow frame.

**Root Causes:**

1. **Heavy work on main thread**
```kotlin
// BAD: blocks UI thread during binding
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val processed = heavyProcessing(data[position])  // 120ms!
    holder.bind(processed)
}

// Better: move heavy work off the main thread
// (in real code you must respect ViewHolder recycling and cancel outdated work)
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Illustrative only, not production-ready
    CoroutineScope(Dispatchers.Default).launch {
        val processed = heavyProcessing(data[position])
        withContext(Dispatchers.Main) {
            holder.bind(processed)
        }
    }
}
```

2. **Synchronous I/O on the main thread**
```kotlin
// BAD: blocking DB call on UI thread
button.setOnClickListener {
    val data = database.query()  // Blocks UI!
    updateUI(data)
}

// GOOD: async (off main thread)
button.setOnClickListener {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) { database.query() }
        updateUI(data)
    }
}
```

3. **Inefficient rendering** — excessive layout inflations, deep / heavy hierarchies, missing view recycling.

**Performance Monitoring (simplified):**
```kotlin
Choreographer.getInstance().postFrameCallback(object : Choreographer.FrameCallback {
    var lastFrameTime = 0L
    override fun doFrame(frameTimeNanos: Long) {
        if (lastFrameTime != 0L) {
            val frameDurationMs = (frameTimeNanos - lastFrameTime) / 1_000_000
            if (frameDurationMs > 17) {
                Log.w("Perf", "Slow frame: ${frameDurationMs}ms")
            }
        }
        lastFrameTime = frameTimeNanos
        Choreographer.getInstance().postFrameCallback(this)
    }
})
```
(This is only to illustrate the idea; for real analysis, use platform tracing tools, see also [[c-android-basics]] and [[c-android-profiling]].)

**Performance Criteria (for 60Hz displays):**
- **< ~16.67ms** — smooth (60 fps)
- **~16.67-33ms** — may be noticeable but acceptable (30-60 fps)
- **~120ms** — clear jank / visible hitch
- **≈5000ms on main thread** — high ANR risk for input/broadcast (5s), with some cases (services) at 10s; such long stalls are unacceptable.

**Solution:** Profile with Perfetto/trace tools, move heavy work to Dispatchers.Default/IO or other background mechanisms, optimize layout hierarchy, use RecyclerView with proper recycling and DiffUtil.

---

## Дополнительные вопросы (RU)

- В чем разница между временем кадра и временем рендеринга?
- Как `Choreographer` связан с `vsync`?
- Когда стоит использовать `StrictMode` для обнаружения нарушений на главном потоке?
- Как определить, какая фаза (measure/layout/draw) вызывает замедление?

## Follow-ups

- What's the difference between frame time and render time?
- How does `Choreographer` relate to `vsync`?
- When would you use `StrictMode` to detect main thread violations?
- How do you diagnose which specific phase (measure/layout/draw) is slow?

## Ссылки (RU)

- Android Developer Guide: Performance & Rendering
- Perfetto/trace инструменты для детального анализа кадров

## References

- Android Developer Guide: [Performance & Rendering](https://developer.android.com/topic/performance/rendering)
- Systrace/Perfetto for detailed frame analysis

## Связанные вопросы (RU)

### Предпосылки
- Понимание конвейера рендеринга UI в Android
- Базовые знания о частоте кадров и `vsync`

### Связанные
- q-android-app-components--android--easy

### Продвинутые
- q-android-performance-measurement-tools--android--medium

## Related Questions

### Prerequisites
- Understanding of Android UI rendering pipeline
- Basic knowledge of frame rate and `vsync`

### Related
- q-android-app-components--android--easy

### Advanced
- q-android-performance-measurement-tools--android--medium
