---
id: android-110
title: How VSYNC and Recomposition Events Are Related / Как связаны VSYNC и события
  рекомпозиции
aliases:
- VSYNC Recomposition
- VSYNC и рекомпозиция
topic: android
subtopics:
- performance-rendering
- ui-compose
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-state
- c-jetpack-compose
- c-performance
- q-how-to-create-list-like-recyclerview-in-compose--android--medium
- q-network-error-handling-strategies--networking--medium
created: 2025-10-13
updated: 2025-10-28
sources: []
tags:
- android
- android/performance-rendering
- android/ui-compose
- compose
- difficulty/hard
- performance
- vsync
---

# Вопрос (RU)

> Как связаны VSYNC и события рекомпозиции в Jetpack Compose?

# Question (EN)

> How are VSYNC and recomposition events related in Jetpack Compose?

---

## Ответ (RU)

**VSYNC (Vertical Synchronization)** — это сигнал синхронизации, который привязывает отрисовку UI к частоте обновления экрана (обычно 60Hz, 90Hz, 120Hz). Jetpack Compose использует VSYNC как триггер для выполнения рекомпозиции и отрисовки кадров.

### Ключевой Механизм

1. **Изменение состояния** вызывает запрос рекомпозиции
2. **Рекомпозиция планируется**, но не выполняется немедленно
3. **Следующий VSYNC** запускает выполнение рекомпозиции
4. **Layout → Drawing → GPU rendering** происходят синхронно

```kotlin
@Composable
fun VSyncDemo() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        count++ // ✅ Запрос рекомпозиции — выполнится при следующем VSYNC
        // ❌ НЕ выполняется немедленно
    }) {
        Text("Count: $count")
    }
}
```

### Бюджет Кадра (60Hz = 16.6ms)

```text
Composition:     ~2-3ms
Layout:          ~2-3ms
Drawing:         ~2-3ms
GPU Rendering:   ~8-10ms
═══════════════════════
Total:           ~16.6ms
```

Если превышен бюджет — кадр пропускается (dropped frame), возникает jank.

### Батчинг Состояний

Compose группирует множественные изменения в одну рекомпозицию:

```kotlin
@Composable
fun BatchedUpdates() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Button(onClick = {
        count1++ // Изменение 1
        count2++ // Изменение 2
        // ✅ Оба объединяются в одну рекомпозицию при следующем VSYNC
    }) {
        Text("$count1 / $count2")
    }
}
```

### Пропуск Промежуточных Состояний

Если состояние меняется быстрее, чем VSYNC, промежуточные значения пропускаются:

```kotlin
LaunchedEffect(Unit) {
    repeat(10) {
        counter++ // 10 изменений за ~10ms
        delay(1)
    }
}
// ❌ UI может показать только: 0 → 4 → 8 → 10
// Промежуточные значения (1,2,3,5,6,7,9) пропущены между VSYNC
```

### Оптимизация Для VSYNC

**derivedStateOf** — пересчет только при реальных изменениях:

```kotlin
@Composable
fun Optimized(items: List<Item>) {
    val activeCount by remember {
        derivedStateOf {
            items.count { it.isActive } // ✅ Пересчет только при изменении items
        }
    }
    Text("Active: $activeCount")
}
```

**drawWithContent** — чтение состояния в фазе рисования без рекомпозиции:

```kotlin
Box(
    modifier = Modifier.drawWithContent {
        translate(left = offset) { // ✅ Не вызывает рекомпозицию
            drawContent()
        }
    }
)
```

### Автоматическая Адаптация К Частоте Обновления

Compose автоматически подстраивается под частоту экрана:

- 60Hz → 60 fps (16.6ms на кадр)
- 90Hz → 90 fps (11.1ms на кадр)
- 120Hz → 120 fps (8.3ms на кадр)

---

## Answer (EN)

**VSYNC (Vertical Synchronization)** is a synchronization signal that ties UI rendering to the screen refresh rate (typically 60Hz, 90Hz, 120Hz). Jetpack Compose uses VSYNC as a trigger to execute recomposition and render frames.

### Core Mechanism

1. **State change** requests recomposition
2. **Recomposition is scheduled** but not executed immediately
3. **Next VSYNC** triggers recomposition execution
4. **Layout → Drawing → GPU rendering** happen synchronously

```kotlin
@Composable
fun VSyncDemo() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = {
        count++ // ✅ Recomposition request — executes at next VSYNC
        // ❌ NOT executed immediately
    }) {
        Text("Count: $count")
    }
}
```

### Frame Budget (60Hz = 16.6ms)

```text
Composition:     ~2-3ms
Layout:          ~2-3ms
Drawing:         ~2-3ms
GPU Rendering:   ~8-10ms
═══════════════════════
Total:           ~16.6ms
```

If budget exceeded → dropped frame, causing jank.

### State Batching

Compose batches multiple state changes into a single recomposition:

```kotlin
@Composable
fun BatchedUpdates() {
    var count1 by remember { mutableStateOf(0) }
    var count2 by remember { mutableStateOf(0) }

    Button(onClick = {
        count1++ // Change 1
        count2++ // Change 2
        // ✅ Both batched into single recomposition at next VSYNC
    }) {
        Text("$count1 / $count2")
    }
}
```

### Skipping Intermediate States

If state changes faster than VSYNC, intermediate values are skipped:

```kotlin
LaunchedEffect(Unit) {
    repeat(10) {
        counter++ // 10 changes in ~10ms
        delay(1)
    }
}
// ❌ UI may only show: 0 → 4 → 8 → 10
// Intermediate values (1,2,3,5,6,7,9) skipped between VSYNCs
```

### Optimizing for VSYNC

**derivedStateOf** — recompute only on actual changes:

```kotlin
@Composable
fun Optimized(items: List<Item>) {
    val activeCount by remember {
        derivedStateOf {
            items.count { it.isActive } // ✅ Recomputes only when items change
        }
    }
    Text("Active: $activeCount")
}
```

**drawWithContent** — read state in draw phase without recomposition:

```kotlin
Box(
    modifier = Modifier.drawWithContent {
        translate(left = offset) { // ✅ Doesn't trigger recomposition
            drawContent()
        }
    }
)
```

### Automatic Refresh Rate Adaptation

Compose automatically adapts to screen refresh rate:

- 60Hz → 60 fps (16.6ms per frame)
- 90Hz → 90 fps (11.1ms per frame)
- 120Hz → 120 fps (8.3ms per frame)

---

## Follow-ups

- What happens if recomposition takes longer than the VSYNC interval?
- How does Compose handle rapid state changes that exceed 60fps?
- What tools can monitor VSYNC synchronization and dropped frames?
- How do side effects (LaunchedEffect, DisposableEffect) interact with VSYNC?
- What's the relationship between Choreographer and VSYNC in Compose?

## References

- [Understanding VSYNC - Android Developers](https://developer.android.com/guide/topics/graphics)
- [Compose Performance Best Practices](https://developer.android.com/jetpack/compose/performance)
- [Choreographer Documentation](https://developer.android.com/reference/android/view/Choreographer)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]
- [[c-performance]]


### Prerequisites
- Compose recomposition basics (easy level)
- Compose state management fundamentals (medium level)

### Related
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]
- Compose performance optimization techniques

### Advanced
- Choreographer and frame callbacks in Android
- Rendering optimization and overdraw reduction
