---
id: 20251012-12271102
title: "How are VSYNC and recomposition events related?"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags:
  - android
moc: moc-android
related: [q-network-error-handling-strategies--networking--medium, q-privacy-sandbox-fledge--privacy--hard, q-how-to-create-list-like-recyclerview-in-compose--android--medium]
---
# How are VSYNC and recomposition events related?

## EN (expanded)

### What is VSYNC?

**VSYNC (Vertical Synchronization)** is a mechanism that synchronizes UI rendering with the screen's refresh rate.

**Key Characteristics:**
- Occurs 60 times per second (60Hz) on standard devices
- Can be 90Hz, 120Hz, or higher on modern high-refresh-rate devices
- Signals when the display is ready to receive a new frame
- Prevents screen tearing

### How Compose Uses VSYNC

Jetpack Compose ties recomposition to VSYNC to ensure smooth and efficient rendering:

1. **State changes** trigger a request for recomposition
2. **Recomposition** is scheduled but not executed immediately
3. **Next VSYNC signal** arrives
4. **Recomposition and rendering** happen in sync with the display refresh

```kotlin
@Composable
fun VSyncExample() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = {
            count++ // State change triggers recomposition request
            // Actual recomposition happens at next VSYNC
        }) {
            Text("Increment")
        }
    }
}
```

### The Frame Pipeline

```
User Action
    ↓
State Change
    ↓
Recomposition Request (scheduled)
    ↓
Wait for VSYNC signal
    ↓
VSYNC arrives (16.6ms @ 60Hz)
    ↓
Recomposition executes
    ↓
Layout & Drawing
    ↓
GPU Rendering
    ↓
Frame displayed on screen
```

### Timeline Example (60Hz Display)

```
Time (ms):  0    16.6   33.2   49.8   66.4
            |     |      |      |      |
VSYNC:                             
            |     |      |      |      |
Frame 1:    [Render-----------------]
Frame 2:          [Render-----------------]
Frame 3:                 [Render-----------------]
```

### Why This Matters

**Without VSYNC synchronization:**
```kotlin
// BAD: Immediate recomposition without VSYNC
@Composable
fun WithoutVSyncSync() {
    var offset by remember { mutableStateOf(0f) }

    LaunchedEffect(Unit) {
        while (true) {
            // Rapid updates without VSYNC coordination
            offset += 1f // Could cause dropped frames, jank
            delay(1) // Too frequent
        }
    }

    Box(modifier = Modifier.offset(x = offset.dp))
}
```

**With VSYNC synchronization:**
```kotlin
// GOOD: Animations tied to frame updates
@Composable
fun WithVSyncSync() {
    val offset by animateFloatAsState(
        targetValue = 100f,
        animationSpec = tween(durationMillis = 1000)
        // Compose automatically syncs with VSYNC
    )

    Box(modifier = Modifier.offset(x = offset.dp))
}
```

### Recomposition Scheduling

Compose batches state changes and schedules recomposition efficiently:

```kotlin
@Composable
fun BatchedUpdates() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Column {
        Text("Count 1: $count1")
        Text("Count 2: $count2")

        Button(onClick = {
            // Multiple state changes
            count1++ // Change 1
            count2++ // Change 2
            // Both changes batched into single recomposition
            // Executed at next VSYNC
        }) {
            Text("Update Both")
        }
    }
}
```

### Frame Budget

At 60Hz, each frame has 16.6ms budget:

```kotlin
Frame Budget (60Hz): 16.6ms
 Composition: ~2-3ms
 Layout: ~2-3ms
 Drawing: ~2-3ms
 GPU Rendering: ~8-10ms
 Buffer time: ~2ms
```

**Example of staying within budget:**
```kotlin
@Composable
fun EfficientList() {
    val items = remember { (1..1000).toList() }

    LazyColumn {
        items(
            items = items,
            key = { it } // Stable keys = efficient recomposition
        ) { item ->
            Text("Item $item")
        }
    }
    // LazyColumn only composes visible items
    // Stays well within frame budget
}
```

### When Recomposition Happens

```kotlin
@Composable
fun RecompositionTiming() {
    var immediate by remember { mutableStateOf(0) }
    var deferred by remember { mutableStateOf(0) }

    Column {
        // Recomposes at next VSYNC
        Text("Immediate: $immediate")

        LaunchedEffect(immediate) {
            // Executes immediately
            println("State changed: $immediate")
            // But UI update waits for VSYNC
        }

        Button(onClick = {
            immediate++ // Triggers recomposition request
            // Recomposition happens at next VSYNC (~16ms later)
        }) {
            Text("Update")
        }
    }
}
```

### Multiple State Changes

```kotlin
@Composable
fun MultipleChanges() {
    var counter by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        // Fast state changes
        repeat(10) {
            counter++ // 10 state changes
            delay(1) // 1ms between changes
        }
        // Only composable frames actually render
        // Intermediate states may be skipped
    }

    Text("Counter: $counter")
    // Might show: 0 → 3 → 7 → 10
    // Skips values that happen between VSYNCs
}
```

### Monitoring Frame Performance

```kotlin
@Composable
fun FrameMonitoring() {
    val choreographer = remember {
        Choreographer.getInstance()
    }

    DisposableEffect(Unit) {
        val callback = object : Choreographer.FrameCallback {
            override fun doFrame(frameTimeNanos: Long) {
                // Called every VSYNC
                println("Frame at: $frameTimeNanos")
                choreographer.postFrameCallback(this)
            }
        }

        choreographer.postFrameCallback(callback)

        onDispose {
            choreographer.removeFrameCallback(callback)
        }
    }
}
```

### Optimizing for VSYNC

**1. Avoid expensive operations in composition:**
```kotlin
@Composable
fun Optimized() {
    val expensiveValue = remember {
        // Computed once, not every recomposition
        computeExpensiveValue()
    }

    Text("Value: $expensiveValue")
}
```

**2. Use derivedStateOf for computed values:**
```kotlin
@Composable
fun DerivedState(items: List<Item>) {
    val filteredCount by remember {
        derivedStateOf {
            // Only recomputed when items change
            items.count { it.isActive }
        }
    }

    Text("Active: $filteredCount")
}
```

**3. Defer reads to drawing phase:**
```kotlin
@Composable
fun DeferredRead() {
    var offset by remember { mutableStateOf(0f) }

    Box(
        modifier = Modifier.drawWithContent {
            // Reading state in draw phase
            // Doesn't trigger recomposition
            translate(left = offset) {
                this@drawWithContent.drawContent()
            }
        }
    )
}
```

### High Refresh Rate Support

```kotlin
@Composable
fun HighRefreshRateAnimation() {
    val infiniteTransition = rememberInfiniteTransition()

    // Automatically adapts to device refresh rate
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        )
    )

    Box(
        modifier = Modifier
            .size(100.dp)
            .graphicsLayer {
                rotationZ = rotation
                // Synced with VSYNC automatically
                // 60fps on 60Hz, 120fps on 120Hz
            }
            .background(Color.Blue)
    )
}
```

### Key Takeaways

1. **VSYNC** is the heartbeat of UI rendering
2. **Recomposition** is scheduled but waits for VSYNC
3. **Multiple state changes** between VSYNCs are batched
4. **Compose automatically** handles synchronization
5. **Frame budget** must be respected to avoid jank
6. **High refresh rates** automatically benefit from this system

---

## Ответ (RU)

### Что такое VSYNC?

**VSYNC (Vertical Synchronization)** — это механизм, который синхронизирует отрисовку UI с частотой обновления экрана.

**Ключевые характеристики:**
- Происходит 60 раз в секунду (60Hz) на стандартных устройствах
- Может быть 90Hz, 120Hz или выше на современных устройствах с высокой частотой обновления
- Сигнализирует, когда дисплей готов принять новый кадр
- Предотвращает разрывы изображения (screen tearing)

### Как Compose использует VSYNC

Jetpack Compose привязывает рекомпозицию к VSYNC для обеспечения плавной и эффективной отрисовки:

1. **Изменения состояния** вызывают запрос на рекомпозицию
2. **Рекомпозиция** планируется, но не выполняется немедленно
3. Приходит **следующий сигнал VSYNC**
4. **Рекомпозиция и отрисовка** происходят синхронно с обновлением дисплея

```kotlin
@Composable
fun VSyncExample() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = {
            count++ // Изменение состояния вызывает запрос рекомпозиции
            // Фактическая рекомпозиция происходит при следующем VSYNC
        }) {
            Text("Increment")
        }
    }
}
```

### Конвейер кадров

```
Действие пользователя
    ↓
Изменение состояния
    ↓
Запрос рекомпозиции (запланирован)
    ↓
Ожидание сигнала VSYNC
    ↓
VSYNC прибывает (16.6ms @ 60Hz)
    ↓
Выполняется рекомпозиция
    ↓
Layout и Drawing
    ↓
Отрисовка GPU
    ↓
Кадр отображается на экране
```

### Пример временной шкалы (дисплей 60Hz)

```
Время (мс):  0    16.6   33.2   49.8   66.4
            |     |      |      |      |
VSYNC:
            |     |      |      |      |
Кадр 1:    [Отрисовка--------------]
Кадр 2:          [Отрисовка--------------]
Кадр 3:                 [Отрисовка--------------]
```

### Почему это важно

**Без синхронизации с VSYNC:**
```kotlin
// ПЛОХО: Немедленная рекомпозиция без VSYNC
@Composable
fun WithoutVSyncSync() {
    var offset by remember { mutableStateOf(0f) }

    LaunchedEffect(Unit) {
        while (true) {
            // Быстрые обновления без координации с VSYNC
            offset += 1f // Может вызвать пропущенные кадры, рывки
            delay(1) // Слишком часто
        }
    }

    Box(modifier = Modifier.offset(x = offset.dp))
}
```

**С синхронизацией VSYNC:**
```kotlin
// ХОРОШО: Анимации привязаны к обновлениям кадров
@Composable
fun WithVSyncSync() {
    val offset by animateFloatAsState(
        targetValue = 100f,
        animationSpec = tween(durationMillis = 1000)
        // Compose автоматически синхронизируется с VSYNC
    )

    Box(modifier = Modifier.offset(x = offset.dp))
}
```

### Планирование рекомпозиции

Compose группирует изменения состояния и планирует рекомпозицию эффективно:

```kotlin
@Composable
fun BatchedUpdates() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Column {
        Text("Count 1: $count1")
        Text("Count 2: $count2")

        Button(onClick = {
            // Множественные изменения состояния
            count1++ // Изменение 1
            count2++ // Изменение 2
            // Оба изменения группируются в одну рекомпозицию
            // Выполняется при следующем VSYNC
        }) {
            Text("Update Both")
        }
    }
}
```

### Бюджет кадра

При 60Hz каждый кадр имеет бюджет 16.6мс:

```kotlin
Бюджет кадра (60Hz): 16.6мс
 Composition: ~2-3мс
 Layout: ~2-3мс
 Drawing: ~2-3мс
 GPU Rendering: ~8-10мс
 Время буфера: ~2мс
```

**Пример соблюдения бюджета:**
```kotlin
@Composable
fun EfficientList() {
    val items = remember { (1..1000).toList() }

    LazyColumn {
        items(
            items = items,
            key = { it } // Стабильные ключи = эффективная рекомпозиция
        ) { item ->
            Text("Item $item")
        }
    }
    // LazyColumn компонует только видимые элементы
    // Остается в пределах бюджета кадра
}
```

### Когда происходит рекомпозиция

```kotlin
@Composable
fun RecompositionTiming() {
    var immediate by remember { mutableStateOf(0) }
    var deferred by remember { mutableStateOf(0) }

    Column {
        // Рекомпозируется при следующем VSYNC
        Text("Immediate: $immediate")

        LaunchedEffect(immediate) {
            // Выполняется немедленно
            println("State changed: $immediate")
            // Но обновление UI ждет VSYNC
        }

        Button(onClick = {
            immediate++ // Вызывает запрос рекомпозиции
            // Рекомпозиция происходит при следующем VSYNC (~16мс позже)
        }) {
            Text("Update")
        }
    }
}
```

### Множественные изменения состояния

```kotlin
@Composable
fun MultipleChanges() {
    var counter by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        // Быстрые изменения состояния
        repeat(10) {
            counter++ // 10 изменений состояния
            delay(1) // 1мс между изменениями
        }
        // Отрисовываются только кадры, которые можно скомпоновать
        // Промежуточные состояния могут быть пропущены
    }

    Text("Counter: $counter")
    // Может показать: 0 → 3 → 7 → 10
    // Пропускает значения между VSYNC
}
```

### Мониторинг производительности кадров

```kotlin
@Composable
fun FrameMonitoring() {
    val choreographer = remember {
        Choreographer.getInstance()
    }

    DisposableEffect(Unit) {
        val callback = object : Choreographer.FrameCallback {
            override fun doFrame(frameTimeNanos: Long) {
                // Вызывается каждый VSYNC
                println("Frame at: $frameTimeNanos")
                choreographer.postFrameCallback(this)
            }
        }

        choreographer.postFrameCallback(callback)

        onDispose {
            choreographer.removeFrameCallback(callback)
        }
    }
}
```

### Оптимизация для VSYNC

**1. Избегайте дорогих операций в композиции:**
```kotlin
@Composable
fun Optimized() {
    val expensiveValue = remember {
        // Вычисляется один раз, не при каждой рекомпозиции
        computeExpensiveValue()
    }

    Text("Value: $expensiveValue")
}
```

**2. Используйте derivedStateOf для вычисляемых значений:**
```kotlin
@Composable
fun DerivedState(items: List<Item>) {
    val filteredCount by remember {
        derivedStateOf {
            // Пересчитывается только когда items изменяются
            items.count { it.isActive }
        }
    }

    Text("Active: $filteredCount")
}
```

**3. Отложите чтения до фазы рисования:**
```kotlin
@Composable
fun DeferredRead() {
    var offset by remember { mutableStateOf(0f) }

    Box(
        modifier = Modifier.drawWithContent {
            // Чтение состояния в фазе рисования
            // Не вызывает рекомпозицию
            translate(left = offset) {
                this@drawWithContent.drawContent()
            }
        }
    )
}
```

### Поддержка высокой частоты обновления

```kotlin
@Composable
fun HighRefreshRateAnimation() {
    val infiniteTransition = rememberInfiniteTransition()

    // Автоматически адаптируется к частоте обновления устройства
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        )
    )

    Box(
        modifier = Modifier
            .size(100.dp)
            .graphicsLayer {
                rotationZ = rotation
                // Синхронизировано с VSYNC автоматически
                // 60fps на 60Hz, 120fps на 120Hz
            }
            .background(Color.Blue)
    )
}
```

### Ключевые выводы

1. **VSYNC** — это сердцебиение отрисовки UI
2. **Рекомпозиция** планируется, но ожидает VSYNC
3. **Множественные изменения состояния** между VSYNC группируются
4. **Compose автоматически** управляет синхронизацией
5. **Бюджет кадра** должен соблюдаться для избежания рывков
6. **Высокие частоты обновления** автоматически выигрывают от этой системы

## Related Questions

- [[q-network-error-handling-strategies--networking--medium]]
- [[q-privacy-sandbox-fledge--privacy--hard]]
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]
