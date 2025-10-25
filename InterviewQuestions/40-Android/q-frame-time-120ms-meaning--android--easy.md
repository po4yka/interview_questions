---
id: 20251012-1227143
title: "Frame Time 120ms Meaning / Значение времени кадра 120мс"
topic: android
difficulty: easy
status: draft
created: 2025-10-13
tags: [android/performance, difficulty/easy, fps, frame-rate, performance, rendering, ui-performance]
moc: moc-android
related: [q-how-to-pass-parameters-to-a-fragment--android--easy, q-what-is-pendingintent--android--medium, q-why-use-fragments-when-we-have-activities--android--medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:47:07 pm
---

# Если Профайлер Показывает Тебе Что Какой-нибудь Фрейм Занял 120 Миллисекунд, Что Это Значит?

**English**: If profiler shows that a frame took 120 milliseconds, what does it mean?

## Answer (EN)
If the profiler shows that rendering a frame took **120 milliseconds**, this means the frame **executed too long**, which leads to **freezes and lags** in the user interface.

**Frame Budget:**

- **60 fps target**: 16.67ms per frame
- **120ms frame**: 7x over budget!
- **Result**: Dropped ~7 frames

**Calculation:**

```
60 fps = 1000ms / 60 = 16.67ms per frame
120ms frame = 120 / 16.67 = ~7 frames dropped

User sees: freeze/stutter for 120ms
```

**Visual Impact:**

```
Normal (16ms):     Smooth
Your frame (120ms):  JANKY!

Timeline:
0ms    16ms   32ms   48ms   64ms   80ms   96ms   112ms  120ms
|------|------|------|------|------|------|------|------|
 1      2      3      4      5      6      7      8      Your frame completes

User sees 7 dropped frames = visible stutter
```

**Profile GPU Rendering Visualization:**

```
Green line = 16ms (60 fps budget)

     |
120ms|                                     ← Your frame (BAD!)
     |                                    
     |                                    
     |                                    
     |                                    
     |                                    
 16ms|
     |           
     |           
     |__________________________|___|___|___|____
        Normal frames            ^
                                 Spike!
```

**Common Causes:**

**1. Heavy UI work on main thread:**

```kotlin
//  BAD - Blocks UI for 120ms
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Complex calculation on main thread
    val processedData = heavyProcessing(data[position])  // 120ms!
    holder.bind(processedData)
}
```

**2. Synchronous network/database:**

```kotlin
//  BAD
button.setOnClickListener {
    val data = database.query()  // Blocks UI!
    updateUI(data)
}
```

**3. Large list without recycling:**

```kotlin
//  BAD
for (item in largeList) {
    val view = inflate(R.layout.item)  // Many inflations!
    container.addView(view)
}
```

**Solutions:**

```kotlin
//  GOOD - Move work off main thread
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    viewModelScope.launch(Dispatchers.Default) {
        val processed = heavyProcessing(data[position])
        withContext(Dispatchers.Main) {
            holder.bind(processed)
        }
    }
}

//  GOOD - Async operations
button.setOnClickListener {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) {
            database.query()
        }
        updateUI(data)
    }
}

//  GOOD - Use RecyclerView
recyclerView.adapter = MyAdapter(largeList)  // Efficient recycling
```

**Measuring Frame Time:**

```kotlin
// Choreographer - frame callback
Choreographer.getInstance().postFrameCallback(object : Choreographer.FrameCallback {
    var lastFrameTime = 0L

    override fun doFrame(frameTimeNanos: Long) {
        if (lastFrameTime != 0L) {
            val frameDuration = (frameTimeNanos - lastFrameTime) / 1_000_000
            if (frameDuration > 16) {
                Log.w("Performance", "Slow frame: ${frameDuration}ms")
            }
        }
        lastFrameTime = frameTimeNanos
        Choreographer.getInstance().postFrameCallback(this)
    }
})
```

**Frame Time Guidelines:**

| Frame Time | FPS | User Experience |
|------------|-----|-----------------|
| 16ms | 60 |  Smooth |
| 33ms | 30 |  Noticeable |
| 120ms | 8 |  Janky, freezes |
| 1000ms | 1 |  ANR risk |

**Summary:**

- **120ms frame** = **7 dropped frames** at 60 fps
- **Causes**: Heavy main thread work, sync I/O, inefficient rendering
- **Effect**: Visible stuttering and lag
- **Solution**: Move work off main thread, optimize rendering, use async operations
- **Target**: Keep frames under 16ms for smooth 60 fps

## Ответ (RU)

Если профайлер показывает что отрисовка кадра заняла **120 миллисекунд**, это означает что кадр **выполнялся слишком долго**, что приводит к **зависаниям и лагам** в пользовательском интерфейсе.

**Бюджет кадра:**

- **Цель 60 fps**: 16.67мс на кадр
- **Кадр 120мс**: превышение в 7 раз!
- **Результат**: Пропущено ~7 кадров

**Расчёт:**

```
60 fps = 1000мс / 60 = 16.67мс на кадр
Кадр 120мс = 120 / 16.67 = ~7 пропущенных кадров

Пользователь видит: зависание на 120мс
```

**Визуальное воздействие:**

```
Норма (16мс):       Плавно
Ваш кадр (120мс):   РЫВОК!

Временная шкала:
0мс    16мс   32мс   48мс   64мс   80мс   96мс   112мс  120мс
|------|------|------|------|------|------|------|------|
 1      2      3      4      5      6      7      8      Ваш кадр завершён

Пользователь видит 7 пропущенных кадров = видимое заикание
```

**Основные причины:**

**1. Тяжёлая работа UI в главном потоке:**

```kotlin
//  ПЛОХО - Блокирует UI на 120мс
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Сложные вычисления в главном потоке
    val processedData = heavyProcessing(data[position])  // 120мс!
    holder.bind(processedData)
}
```

**2. Синхронные сетевые/БД операции:**

```kotlin
//  ПЛОХО
button.setOnClickListener {
    val data = database.query()  // Блокирует UI!
    updateUI(data)
}
```

**3. Большой список без переработки:**

```kotlin
//  ПЛОХО
for (item in largeList) {
    val view = inflate(R.layout.item)  // Множество инфляций!
    container.addView(view)
}
```

**Решения:**

```kotlin
//  ХОРОШО - Перенести работу из главного потока
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    viewModelScope.launch(Dispatchers.Default) {
        val processed = heavyProcessing(data[position])
        withContext(Dispatchers.Main) {
            holder.bind(processed)
        }
    }
}

//  ХОРОШО - Асинхронные операции
button.setOnClickListener {
    viewModelScope.launch {
        val data = withContext(Dispatchers.IO) {
            database.query()
        }
        updateUI(data)
    }
}

//  ХОРОШО - Использовать RecyclerView
recyclerView.adapter = MyAdapter(largeList)  // Эффективная переработка
```

**Итог:**

- **Кадр 120мс** = **7 пропущенных кадров** при 60 fps
- **Причины**: Тяжёлая работа в главном потоке, синхронный I/O, неэффективная отрисовка
- **Эффект**: Видимые заикания и лаги
- **Решение**: Перенести работу из главного потока, оптимизировать отрисовку, использовать асинхронные операции
- **Цель**: Держать кадры под 16мс для плавных 60 fps

## Related Questions

- [[q-what-is-pendingintent--android--medium]]
- [[q-why-use-fragments-when-we-have-activities--android--medium]]
- [[q-how-to-pass-parameters-to-a-fragment--android--easy]]
