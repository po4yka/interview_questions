---
id: "20251015082237313"
title: "Recomposition Choreographer / Рекомпозиция и Choreographer"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: [android/jetpack-compose, android/performance, choreographer, frame-scheduling, jetpack-compose, performance, recomposition, vsync, difficulty/hard]
---
# Рекомпозиция происходит в рандомное время или по команде хореографера?

**English**: Does recomposition happen at random times or on command from Choreographer?

## Answer (EN)
Recomposition is **controlled by Android Choreographer**, which works with **VSYNC**.

**Process:**
1. **MutableState change** sets a flag "UI requires redraw"
2. **Choreographer waits** for the next VSYNC
3. **Launches recomposition** synchronized with VSYNC
4. **Only changed UI elements** are redrawn

---

## Choreographer in Android

### What is Choreographer?

**Choreographer** is Android's system component that **coordinates frame rendering** with the display's refresh rate (typically 60Hz or 120Hz).

```
Display refresh rate: 60 Hz
Frame budget: 16.67 ms per frame (1000ms / 60)

VSYNC signals arrive every ~16.67ms
          
VSYNC ... VSYNC ... VSYNC
          
  ↓           ↓           ↓
Frame 1     Frame 2     Frame 3
```

---

## Recomposition Flow with Choreographer

### Step-by-Step Process

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {  // User clicks here
            Text("Increment")
        }
    }
}
```

**What happens when user clicks the button:**

```
Time: 0ms

 User clicks button               
 count++ (state changes)          
 → Flags UI needs redraw          

                ↓

Time: 0-16ms

 Choreographer is notified        
 Waits for next VSYNC signal      

                ↓

Time: 16.67ms

 VSYNC signal arrives             
 Choreographer triggers frame     
 → Recomposition begins           

                ↓

Time: 16.67-20ms

 Compose recomposes changed parts 
 → Only Text("Count: $count")     
 → Not the entire Column/Button   

                ↓

Time: 20-32ms

 UI rendering (draw phase)        
 Frame submitted to display       

                ↓

Time: 33.34ms (next VSYNC)

 Frame appears on screen          
 User sees updated count          

```

**Key points:**
- **Not random** - Scheduled with VSYNC
- **Batched** - Multiple state changes before VSYNC are batched
- **Optimized** - Only changed Composables recompose

---

## Why Use Choreographer?

### 1. Smooth Frame Rate

Without Choreographer (random timing):
```
State changes:  
Recomposition:   
VSYNC:          
Result: Janky, inconsistent frame timing BAD
```

With Choreographer (VSYNC-aligned):
```
State changes:  
Recomposition:   [batched]  [batched]
VSYNC:          
Result: Smooth, consistent 60fps GOOD
```

### 2. Battery Efficiency

**Random recomposition:**
- CPU wakes up unpredictably
- Power-hungry
- Battery drain

**VSYNC-synchronized:**
- CPU wakes at predictable intervals
- Can enter low-power state between frames
- Battery-friendly

---

## Batching State Changes

### Multiple State Changes Before VSYNC

```kotlin
@Composable
fun MultiStateUpdate() {
    var count by remember { mutableStateOf(0) }
    var name by remember { mutableStateOf("") }
    var enabled by remember { mutableStateOf(false) }

    Button(onClick = {
        // All three changes happen "instantly" (< 1ms)
        count++
        name = "Updated"
        enabled = !enabled
    }) {
        Text("Update All")
    }

    Column {
        Text("Count: $count")
        Text("Name: $name")
        Text("Enabled: $enabled")
    }
}
```

**Without batching (hypothetical):**
```
0ms:    count++ → recompose → render
1ms:    name = "Updated" → recompose → render
2ms:    enabled = !enabled → recompose → render
Result: 3 separate recomposition/render cycles BAD
```

**With Choreographer batching:**
```
0ms:    count++
1ms:    name = "Updated"
2ms:    enabled = !enabled
3ms:    Choreographer: "UI needs redraw"
16.67ms: VSYNC → recompose all changes at once → render
Result: 1 batched recomposition/render cycle GOOD
```

**Benefit:** Prevents unnecessary intermediate frames.

---

## Frame Scheduling

### Choreographer Callbacks

Android Choreographer provides different callback types:

```kotlin
// Internal Compose implementation (simplified)
fun scheduleRecomposition() {
    Choreographer.getInstance().postFrameCallback { frameTimeNanos ->
        // This runs on next VSYNC
        performRecomposition()
    }
}
```

**Callback types:**
1. **CALLBACK_INPUT** - Touch events (highest priority)
2. **CALLBACK_ANIMATION** - Animations
3. **CALLBACK_TRAVERSAL** - Layout/draw (Compose recomposition happens here)
4. **CALLBACK_COMMIT** - Final rendering

**Compose uses CALLBACK_TRAVERSAL** to align recomposition with rendering.

---

## Practical Example: Frame Timeline

### Measuring Frame Timing

```kotlin
@Composable
fun FrameTimingDemo() {
    var count by remember { mutableStateOf(0) }
    var lastUpdateTime by remember { mutableStateOf(0L) }

    Column {
        Text("Count: $count")
        Text("Last update: ${System.currentTimeMillis() - lastUpdateTime}ms ago")

        Button(onClick = {
            val startTime = System.currentTimeMillis()
            count++
            lastUpdateTime = startTime
        }) {
            Text("Increment")
        }
    }
}
```

**Observation:**
- Click button at `t=0ms`
- UI updates at `t=16-17ms` (next VSYNC)
- Even rapid clicks are batched to VSYNC intervals

---

## Performance Implications

### 60 Hz Display (16.67ms budget)

```kotlin
@Composable
fun PerformanceExample() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Fast recomposition (< 1ms)
        Text("Count: $count")  // - Fits in 16.67ms budget

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Frame timeline:**
```
VSYNC 1 (0ms):    Idle
VSYNC 2 (16.67ms): User clicks → count++
VSYNC 3 (33.34ms): Recompose Text (1ms) + Render → - Displayed
```

### Dropped Frames (Jank)

```kotlin
@Composable
fun SlowRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Expensive computation during composition
        val result = remember(count) {
            Thread.sleep(20)  // - 20ms > 16.67ms budget
            count * 2
        }
        Text("Result: $result")

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Frame timeline (dropped frame):**
```
VSYNC 1 (0ms):     Idle
VSYNC 2 (16.67ms): User clicks → count++
VSYNC 3 (33.34ms): Recompose starts... still working... - MISSED DEADLINE
VSYNC 4 (50.01ms): Recompose completes + Render → Displayed (delayed!)
```

**Result:** UI appears frozen for 33ms instead of 16ms → **Jank!**

---

## High Refresh Rate Displays

### 120 Hz Display (8.33ms budget)

Modern devices have 120Hz displays:
- Frame budget: **8.33ms** (half of 60Hz)
- More frequent VSYNC signals
- Tighter performance requirements

```kotlin
// Same code, different performance requirement
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Text("Count: $count")

    Button(onClick = { count++ }) {
        Text("Increment")
    }
}

// 60Hz: Recomposition has 16.67ms budget → Easy GOOD
// 120Hz: Recomposition has 8.33ms budget → Must be faster! WARNING
```

---

## Debugging Frame Performance

### Enable GPU Rendering Profiler

**Settings → Developer Options → Profile GPU Rendering → On screen as bars**

**Green line at 16ms (60Hz):**
- Bars below green = 60fps GOOD
- Bars above green = dropped frames BAD

```
Frame time bars:
     = Input
    = Animation
   = Measure/Layout
  = Draw
  ← 16ms green line (60fps threshold)

Example:
  ← 25ms (dropped frame, jank)
          ← 8ms (smooth)
        ← 12ms (smooth)
```

---

## Advanced: Recomposition Scheduling

### Deferred Recomposition

```kotlin
@Composable
fun DeferredExample() {
    var count by remember { mutableStateOf(0) }

    LaunchedEffect(count) {
        // This runs AFTER recomposition completes
        println("Count updated to $count")
    }

    Text("Count: $count")
}
```

**Timeline:**
```
1. count++ (state change)
2. Choreographer schedules recomposition
3. VSYNC arrives
4. Recomposition: Text("Count: $count")
5. LaunchedEffect runs after recomposition
```

---

## Summary

**Recomposition timing:**
- **NOT random** - Controlled by Choreographer
- **VSYNC-synchronized** - Aligned with display refresh rate
- **Batched** - Multiple state changes → single recomposition
- **Granular** - Only changed UI elements recompose

**Process:**
1. **State change** → Flag "UI needs redraw"
2. **Choreographer** → Wait for next VSYNC
3. **VSYNC arrives** → Trigger recomposition
4. **Recompose** → Only changed Composables
5. **Render** → Display new frame

**Benefits:**
- **Smooth animations** - 60fps or 120fps
- **Battery efficient** - Predictable CPU wake-ups
- **No wasted frames** - State changes batched

**Frame budget:**
- 60Hz: 16.67ms per frame
- 120Hz: 8.33ms per frame

**Best practice:** Keep recomposition **< 8ms** for smooth 120Hz support.

---

## Ответ (RU)

Рекомпозиция **контролируется Android Choreographer**, который работает с **VSYNC**.

**Процесс:**
1. **Изменение MutableState** ставит флаг "UI требует перерисовки"
2. **Choreographer ждет** следующий VSYNC
3. **Запускает рекомпозицию** синхронизированно с VSYNC
4. **Только измененные UI элементы** перерисовываются

---

### Choreographer в Android

#### Что такое Choreographer?

**Choreographer** - это системный компонент Android, который **координирует рендеринг кадров** с частотой обновления дисплея (обычно 60Hz или 120Hz).

```
Частота обновления дисплея: 60 Hz
Бюджет кадра: 16.67 мс на кадр (1000ms / 60)

Сигналы VSYNC приходят каждые ~16.67ms

VSYNC ... VSYNC ... VSYNC

  ↓           ↓           ↓
Кадр 1      Кадр 2      Кадр 3
```

---

### Поток рекомпозиции с Choreographer

#### Пошаговый процесс

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Счетчик: $count")
        Button(onClick = { count++ }) {  // Пользователь нажимает здесь
            Text("Увеличить")
        }
    }
}
```

**Что происходит, когда пользователь нажимает кнопку:**

```
Время: 0ms

 Пользователь нажимает кнопку
 count++ (изменение состояния)
 → Флаги UI требует перерисовки

                ↓

Время: 0-16ms

 Choreographer получает уведомление
 Ждет следующего сигнала VSYNC

                ↓

Время: 16.67ms

 Сигнал VSYNC прибывает
 Choreographer запускает кадр
 → Рекомпозиция начинается

                ↓

Время: 16.67-20ms

 Compose перекомпонует измененные части
 → Только Text("Счетчик: $count")
 → Не весь Column/Button

                ↓

Время: 20-32ms

 Рендеринг UI (фаза отрисовки)
 Кадр отправлен на дисплей

                ↓

Время: 33.34ms (следующий VSYNC)

 Кадр появляется на экране
 Пользователь видит обновленный счетчик

```

**Ключевые моменты:**
- **Не случайно** - Запланировано с VSYNC
- **Батчинг** - Множественные изменения состояния до VSYNC батчируются
- **Оптимизировано** - Только измененные Composables перекомпонуются

---

### Зачем использовать Choreographer?

#### 1. Плавная частота кадров

Без Choreographer (случайное время):
```
Изменения состояния:
Рекомпозиция:
VSYNC:
Результат: Прерывистый, непостоянный таймин кадров ❌ ПЛОХО
```

С Choreographer (выравнивание по VSYNC):
```
Изменения состояния:
Рекомпозиция:   [батчинг]  [батчинг]
VSYNC:
Результат: Плавные, постоянные 60fps ✅ ХОРОШО
```

#### 2. Энергоэффективность

**Случайная рекомпозиция:**
- CPU просыпается непредсказуемо
- Энергозатратно
- Разряд батареи

**VSYNC-синхронизированная:**
- CPU просыпается через предсказуемые интервалы
- Может входить в режим низкого энергопотребления между кадрами
- Экономия батареи

---

### Батчинг изменений состояния

#### Множественные изменения состояния до VSYNC

```kotlin
@Composable
fun MultiStateUpdate() {
    var count by remember { mutableStateOf(0) }
    var name by remember { mutableStateOf("") }
    var enabled by remember { mutableStateOf(false) }

    Button(onClick = {
        // Все три изменения происходят "мгновенно" (< 1ms)
        count++
        name = "Обновлено"
        enabled = !enabled
    }) {
        Text("Обновить все")
    }

    Column {
        Text("Счетчик: $count")
        Text("Имя: $name")
        Text("Включено: $enabled")
    }
}
```

**Без батчинга (гипотетически):**
```
0ms:    count++ → рекомпозиция → рендеринг
1ms:    name = "Обновлено" → рекомпозиция → рендеринг
2ms:    enabled = !enabled → рекомпозиция → рендеринг
Результат: 3 отдельных цикла рекомпозиции/рендеринга ❌ ПЛОХО
```

**С батчингом Choreographer:**
```
0ms:    count++
1ms:    name = "Обновлено"
2ms:    enabled = !enabled
3ms:    Choreographer: "UI требует перерисовки"
16.67ms: VSYNC → перекомпоновать все изменения сразу → рендеринг
Результат: 1 батчированный цикл рекомпозиции/рендеринга ✅ ХОРОШО
```

**Преимущество:** Предотвращает ненужные промежуточные кадры.

---

### Планирование кадров

#### Колбэки Choreographer

Android Choreographer предоставляет различные типы колбэков:

```kotlin
// Внутренняя реализация Compose (упрощенная)
fun scheduleRecomposition() {
    Choreographer.getInstance().postFrameCallback { frameTimeNanos ->
        // Это выполняется на следующем VSYNC
        performRecomposition()
    }
}
```

**Типы колбэков:**
1. **CALLBACK_INPUT** - События касания (наивысший приоритет)
2. **CALLBACK_ANIMATION** - Анимации
3. **CALLBACK_TRAVERSAL** - Layout/draw (рекомпозиция Compose происходит здесь)
4. **CALLBACK_COMMIT** - Финальный рендеринг

**Compose использует CALLBACK_TRAVERSAL** для выравнивания рекомпозиции с рендерингом.

---

### Последствия для производительности

#### Дисплей 60 Hz (бюджет 16.67ms)

```kotlin
@Composable
fun PerformanceExample() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Быстрая рекомпозиция (< 1ms)
        Text("Счетчик: $count")  // ✅ Вписывается в бюджет 16.67ms

        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}
```

**Таймлайн кадра:**
```
VSYNC 1 (0ms):    Простой
VSYNC 2 (16.67ms): Пользователь нажимает → count++
VSYNC 3 (33.34ms): Рекомпоновать Text (1ms) + Рендеринг → ✅ Отображено
```

#### Пропущенные кадры (рывки)

```kotlin
@Composable
fun SlowRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Дорогое вычисление во время композиции
        val result = remember(count) {
            Thread.sleep(20)  // ❌ 20ms > бюджета 16.67ms
            count * 2
        }
        Text("Результат: $result")

        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}
```

**Таймлайн кадра (пропущенный кадр):**
```
VSYNC 1 (0ms):     Простой
VSYNC 2 (16.67ms): Пользователь нажимает → count++
VSYNC 3 (33.34ms): Рекомпозиция начинается... еще работает... ❌ ПРОПУЩЕН ДЕДЛАЙН
VSYNC 4 (50.01ms): Рекомпозиция завершена + Рендеринг → Отображено (с задержкой!)
```

**Результат:** UI выглядит замороженным на 33ms вместо 16ms → **Рывки!**

---

### Дисплеи с высокой частотой обновления

#### Дисплей 120 Hz (бюджет 8.33ms)

Современные устройства имеют дисплеи 120Hz:
- Бюджет кадра: **8.33ms** (половина от 60Hz)
- Более частые сигналы VSYNC
- Более жесткие требования к производительности

```kotlin
// Тот же код, разные требования к производительности
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Text("Счетчик: $count")

    Button(onClick = { count++ }) {
        Text("Увеличить")
    }
}

// 60Hz: Рекомпозиция имеет бюджет 16.67ms → Легко ✅ ХОРОШО
// 120Hz: Рекомпозиция имеет бюджет 8.33ms → Должна быть быстрее! ⚠️ ПРЕДУПРЕЖДЕНИЕ
```

---

### Резюме

**Время рекомпозиции:**
- **НЕ случайное** - Контролируется Choreographer
- **VSYNC-синхронизированное** - Выравнено с частотой обновления дисплея
- **Батчированное** - Множественные изменения состояния → одна рекомпозиция
- **Гранулярное** - Только измененные UI элементы перекомпонуются

**Процесс:**
1. **Изменение состояния** → Флаг "UI требует перерисовки"
2. **Choreographer** → Ждать следующий VSYNC
3. **VSYNC прибывает** → Запустить рекомпозицию
4. **Рекомпоновать** → Только измененные Composables
5. **Рендеринг** → Отобразить новый кадр

**Преимущества:**
- **Плавные анимации** - 60fps или 120fps
- **Энергоэффективность** - Предсказуемые пробуждения CPU
- **Нет потраченных кадров** - Батчинг изменений состояния

**Бюджет кадра:**
- 60Hz: 16.67ms на кадр
- 120Hz: 8.33ms на кадр

**Лучшая практика:** Держите рекомпозицию **< 8ms** для плавной поддержки 120Hz.


---

## Related Questions

### Prerequisites (Easier)
- [[q-recomposition-compose--android--medium]] - Compose
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Compose

### Related (Hard)
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Compose
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose
- [[q-compose-performance-optimization--android--hard]] - Compose
