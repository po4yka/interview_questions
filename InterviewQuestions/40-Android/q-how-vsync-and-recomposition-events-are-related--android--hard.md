---id: android-110
title: How VSYNC and Recomposition Events Are Related / Как связаны VSYNC и события рекомпозиции
aliases: [VSYNC Recomposition, VSYNC и рекомпозиция]
topic: android
subtopics: [performance-rendering, ui-compose]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, c-compose-state, c-recomposition, q-how-to-create-list-like-recyclerview-in-compose--android--medium, q-mvi-one-time-events--android--medium, q-recomposition-choreographer--android--hard, q-recomposition-compose--android--medium]
created: 2025-10-13
updated: 2025-10-28
sources: []
tags: [android, android/performance-rendering, android/ui-compose, difficulty/hard]
---
# Вопрос (RU)

> Как связаны VSYNC и события рекомпозиции в Jetpack Compose?

# Question (EN)

> How are VSYNC and recomposition events related in Jetpack Compose?

---

## Ответ (RU)

**VSYNC (Vertical Synchronization)** — это сигнал синхронизации, который привязывает отрисовку UI к частоте обновления экрана (обычно 60Hz, 90Hz, 120Hz). На Android отрисовка кадров синхронизируется с VSYNC через `Choreographer`. Jetpack Compose использует этот механизм: рекомпозиции и измерение/рисование планируются в рамках коллбеков кадра (frame callbacks), которые синхронизированы с VSYNC, но изменение состояния само по себе не блокируется до VSYNC.

### Ключевой Механизм

1. **Изменение состояния** помечает затронутые composable как требующие рекомпозиции.
2. **Рекомпозиция планируется** на ближайший tick frame clock (коллбек `Choreographer`), а не выполняется синхронно с записью состояния.
3. **Следующий кадр (VSYNC-синхронизированный коллбек)** запускает обработку накопленных запросов рекомпозиции и фаз `Layout` / `Draw` для этих участков.
4. **CPU-работа (Composition → Layout → Drawing)** должна уложиться в бюджет кадра до следующего VSYNC; затем команды передаются на GPU, а отображение кадра происходит конвейерно.

```kotlin
@Composable
fun VSyncDemo() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        count++ // ✅ Запрос рекомпозиции — будет обработан в ближайшем кадре
        // ❌ Рекомпозиция не выполняется немедленно в этом же обработчике клика
    }) {
        Text("Count: $count")
    }
}
```

### Бюджет Кадра (60Hz ≈ 16.6ms)

Ниже — иллюстративный пример распределения времени внутри одного кадра, а не жестко гарантированные значения:

```text
Composition:     ~2-3ms
Layout:          ~2-3ms
Drawing (CPU):   ~2-3ms
GPU Rendering:   ~8-10ms
═══════════════════════
Total:           ~16.6ms
```

Если суммарная CPU+GPU-работа стабильно не укладывается в интервал между VSYNC-сигналами, кадры пропускаются (dropped frames), появляется jank.

### Батчинг Состояний

Compose старается объединять множественные изменения состояния, произошедшие в одном цикле обработки событий, в одну рекомпозицию кадра:

```kotlin
@Composable
fun BatchedUpdates() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Button(onClick = {
        count1++ // Изменение 1
        count2++ // Изменение 2
        // ✅ Обычно оба будут обработаны в общей рекомпозиции ближайшего кадра
    }) {
        Text("$count1 / $count2")
    }
}
```

Это уменьшает количество лишних проходов и помогает лучше использовать бюджет кадра, но не является строгой гарантией "ровно одна рекомпозиция только на следующем VSYNC" — решения принимает планировщик Compose/Choreographer.

### Пропуск Промежуточных Состояний

Если состояние обновляется чаще, чем приходят кадры, UI может отобразить только последние доступные значения к моменту следующего VSYNC. Промежуточные значения фактически "перескакиваются":

```kotlin
@Composable
fun FastUpdates(counter: Int) {
    Text("Counter: $counter")
}

// Где-то во внешнем scope:
LaunchedEffect(Unit) {
    repeat(10) {
        // counter обновляется 10 раз примерно за 10ms
        // (пример: через mutableStateOf или StateFlow)
        counter++
        delay(1)
    }
}
// UI может показать только часть последовательности (например: 0 → 4 → 8 → 10),
// т.к. кадры ограничены VSYNC. Конкретные значения зависят от таймингов и не детерминированы.
```

Важно понимать: привязка к VSYNC означает, что визуально имеют значение только значения состояния, "зафиксированные" к моменту подготовки следующего кадра.

### Оптимизация Под VSYNC

**`derivedStateOf`** — позволяет пересчитывать производные значения только при реальном изменении зависимостей, уменьшая работу в кадре:

```kotlin
@Composable
fun Optimized(items: List<Item>) {
    val activeCount by remember {
        derivedStateOf {
            items.count { it.isActive } // ✅ Пересчет только при изменении items/их флагов
        }
    }
    Text("Active: $activeCount")
}
```

**`drawWithContent`** — позволяет выполнять логику рисования в фазе Draw без дополнительной рекомпозиции. Внутри следует читать только стабильное/неизменяемое или snapshot-состояние, безопасное для использования в этой фазе:

```kotlin
Box(
    modifier = Modifier.drawWithContent {
        // offset должен приходить из стабильного состояния или быть параметром Modifier
        translate(left = offset) { // ✅ Не инициирует новую рекомпозицию сам по себе
            drawContent()
        }
    }
)
```

Это помогает переносить часть работы в фазу рисования и лучше использовать каждый VSYNC-синхронизированный кадр.

### Автоматическая Адаптация К Частоте Обновления

Compose использует `Choreographer`/frame clock, который синхронизирован с частотой обновления устройства:

- 60Hz → целевой бюджет ~16.6ms на кадр
- 90Hz → ~11.1ms на кадр
- 120Hz → ~8.3ms на кадр

Приложению обычно не нужно специально перенастраивать Compose — оно следует частоте, с которой система генерирует кадры, но фактический fps ограничен способностью кода укладываться в этот бюджет.

---

## Answer (EN)

**VSYNC (Vertical Synchronization)** is a synchronization signal tying UI rendering to the display refresh rate (typically 60Hz, 90Hz, 120Hz). On Android, frame rendering is aligned with VSYNC via `Choreographer`. Jetpack Compose uses this pipeline: recomposition, layout, and drawing work are scheduled on VSYNC-synchronized frame callbacks, but a state write itself is not blocked waiting for VSYNC.

### Core Mechanism

1. **State change** marks affected composables as needing recomposition.
2. **Recomposition is scheduled** on the nearest frame clock tick (`Choreographer` callback), rather than executed inline with the state mutation.
3. **The next frame (VSYNC-synchronized callback)** processes the accumulated recomposition requests and runs `Layout` / `Draw` for the affected parts.
4. **CPU work (Composition → Layout → Drawing)** must complete within the frame budget before the next VSYNC; then GPU commands are submitted and the frame is displayed via a pipelined rendering process.

```kotlin
@Composable
fun VSyncDemo() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        count++ // ✅ Requests recomposition — handled in the next frame
        // ❌ Recomposition is not executed immediately inside this click handler
    }) {
        Text("Count: $count")
    }
}
```

### Frame Budget (60Hz ≈ 16.6ms)

Below is an illustrative breakdown of how time may be spent in a frame; these are not fixed or guaranteed values:

```text
Composition:     ~2-3ms
Layout:          ~2-3ms
Drawing (CPU):   ~2-3ms
GPU Rendering:   ~8-10ms
═══════════════════════
Total:           ~16.6ms
```

If combined CPU + GPU work repeatedly exceeds the interval between VSYNCs, frames are dropped and jank becomes visible.

### State Batching

Compose attempts to batch multiple state changes that occur within the same event loop turn into a single recomposition for the next frame:

```kotlin
@Composable
fun BatchedUpdates() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Button(onClick = {
        count1++ // Change 1
        count2++ // Change 2
        // ✅ Typically both will be handled in one recomposition in the upcoming frame
    }) {
        Text("$count1 / $count2")
    }
}
```

This reduces redundant work and helps fit within the frame budget, but it's not a strict "exactly one recomposition only at next VSYNC" guarantee; scheduling is managed by Compose and `Choreographer`.

### Skipping Intermediate States

If state updates happen more frequently than frames are produced, the UI will effectively display only the latest values at each rendered frame. Intermediate values may never be rendered:

```kotlin
@Composable
fun FastUpdates(counter: Int) {
    Text("Counter: $counter")
}

// Somewhere in a side-effect or ViewModel:
LaunchedEffect(Unit) {
    repeat(10) {
        // counter is updated 10 times in about 10ms
        counter++
        delay(1)
    }
}
// The UI may show only a subset (e.g., 0 → 4 → 8 → 10);
// exact values depend on timing and are not deterministic.
```

Link to VSYNC: because frame rendering is VSYNC-bound, only the state snapshot observed when preparing each frame is visible to the user.

### Optimizing for VSYNC

**`derivedStateOf`** — recomputes expensive derived values only when dependencies actually change, reducing per-frame work:

```kotlin
@Composable
fun Optimized(items: List<Item>) {
    val activeCount by remember {
        derivedStateOf {
            items.count { it.isActive } // ✅ Recomputes only when items/their flags change
        }
    }
    Text("Active: $activeCount")
}
```

**`drawWithContent`** — allows custom drawing during the Draw phase without triggering additional recompositions. Inside it, you should read only stable or otherwise safe state for drawing:

```kotlin
Box(
    modifier = Modifier.drawWithContent {
        // `offset` should be backed by stable state, e.g., from remember/animatable/Modifier param
        translate(left = offset) { // ✅ Does not itself schedule new recompositions
            drawContent()
        }
    }
)
```

This lets you shift some logic into the drawing phase and better utilize each VSYNC-driven frame.

### Automatic Refresh Rate Adaptation

Compose relies on the `Choreographer`/frame clock, which is synchronized with the device's display refresh rate:

- 60Hz → target ~16.6ms per frame
- 90Hz → ~11.1ms per frame
- 120Hz → ~8.3ms per frame

No special app-side configuration is usually needed: Compose runs on the frame callbacks provided by the system. Actual fps is bounded by both the hardware refresh rate and the app's ability to complete work within each frame interval.

---

## Дополнительные Вопросы (RU)

- Что происходит, если рекомпозиция занимает больше времени, чем интервал между VSYNC-сигналами?
- Как Compose обрабатывает быстрые изменения состояния, которые происходят чаще, чем обновляется дисплей?
- Какие инструменты можно использовать для мониторинга синхронизации с VSYNC и пропущенных кадров?
- Как сайд-эффекты (`LaunchedEffect`, `DisposableEffect`) взаимодействуют с планированием кадров и VSYNC?
- Какова связь между `Choreographer` и VSYNC в контексте Compose?

## Follow-ups

- What happens if recomposition takes longer than the VSYNC interval?
- How does Compose handle rapid state changes that exceed the display's refresh rate?
- What tools can monitor VSYNC synchronization and dropped frames?
- How do side effects (`LaunchedEffect`, `DisposableEffect`) interact with frame scheduling and VSYNC?
- What's the relationship between `Choreographer` and VSYNC in Compose?

## Ссылки (RU)

- [Understanding VSYNC - Android Developers](https://developer.android.com/guide/topics/graphics)
- [Compose Performance Best Practices](https://developer.android.com/jetpack/compose/performance)
- [Choreographer Documentation](https://developer.android.com/reference/android/view/Choreographer)

## References

- [Understanding VSYNC - Android Developers](https://developer.android.com/guide/topics/graphics)
- [Compose Performance Best Practices](https://developer.android.com/jetpack/compose/performance)
- [Choreographer Documentation](https://developer.android.com/reference/android/view/Choreographer)

## Связанные Вопросы (RU)

### Базовые Концепции

- [[c-compose-state]]

### Связанные Вопросы

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]

### Продвинутые Темы

- Использование `Choreographer` и коллбеков кадров в Android
- Оптимизация рендеринга и снижение overdraw

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]

### Related

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]

### Advanced

- Choreographer and frame callbacks in Android
- Rendering optimization and overdraw reduction
