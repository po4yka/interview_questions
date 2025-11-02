---
id: android-152
title: "How Compose Draws On Screen / Как Compose рисует на экране"
aliases: ["How Compose Draws On Screen", "Как Compose рисует на экране"]
topic: android
subtopics: [ui-compose, performance-rendering]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-recomposition-compose--android--medium, q-compose-performance-optimization--android--hard, q-compose-stability-skippability--android--hard]
created: 2025-10-15
updated: 2025-01-27
tags: [android, android/ui-compose, android/performance-rendering, compose, rendering, difficulty/medium]
sources: []
date created: Monday, October 27th 2025, 4:02:03 pm
date modified: Thursday, October 30th 2025, 12:48:11 pm
---

# Вопрос (RU)

> Как Jetpack Compose отрисовывает UI на экране? Опишите трёхфазный процесс рендеринга.

# Question (EN)

> How does Jetpack Compose render UI on screen? Describe the three-phase rendering process.

---

## Ответ (RU)

Jetpack Compose использует **трёхфазный асинхронный рендеринг**, где каждая фаза может выполняться независимо для оптимизации производительности.

### Три Фазы Рендеринга

1. **Composition (Композиция)** — построение дерева UI из composable функций
2. **Layout (Размещение)** — измерение и позиционирование элементов
3. **Drawing (Рисование)** — рендеринг на Canvas через GPU

### Фаза 1: Composition

**Что происходит:**
- Compose вызывает все `@Composable` функции
- Строит дерево `LayoutNode`
- Отслеживает зависимости от state через snapshot system
- Использует **Slot Table** для хранения структуры UI, state, remember значений

**Умная рекомпозиция:**
- Пропускает функции, параметры которых не изменились (skippable composables)
- Рекомпонует только части, зависящие от изменившегося state

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter") // ✅ Рекомпонуется при изменении counter
        StaticHeader() // ✅ Не рекомпонуется (нет зависимостей от state)
    }
}
```

### Фаза 2: Layout

**Два прохода:**

1. **Measure Pass (снизу вверх):**
   - Родитель передаёт constraints детям
   - Дети измеряют себя и возвращают размер
   - Каждый элемент измеряется **только один раз** → O(n) сложность

2. **Placement Pass (сверху вниз):**
   - Родитель размещает детей в координатах
   - Устанавливаются финальные позиции

```kotlin
Layout(content = content, modifier = modifier) { measurables, constraints ->
    // ✅ Measure: каждый measurable измеряется один раз
    val placeables = measurables.map { it.measure(constraints) }

    layout(width, height) {
        // ✅ Placement: позиционирование без повторных измерений
        placeables.forEach { it.placeRelative(x, y) }
    }
}
```

### Фаза 3: Drawing

**Рисование на Skia Canvas:**
- Использует `DrawScope` для операций рисования
- GPU-ускорение через hardware layers
- `graphicsLayer` создаёт отдельный hardware layer для трансформаций

```kotlin
Box(
    modifier = Modifier
        .graphicsLayer {
            // ✅ GPU-ускоренные трансформации без recomposition
            rotationZ = 45f
            alpha = 0.8f
        }
        .drawBehind {
            drawRect(Color.Blue) // ✅ Кастомное рисование
        }
)
```

### Независимость Фаз (Ключевая Оптимизация)

Фазы выполняются независимо:

```kotlin
var offset by remember { mutableStateOf(0f) }

Box(
    modifier = Modifier
        .offset { IntOffset(offset.roundToInt(), 0) }
        // ✅ Только layout phase, без recomposition
        .pointerInput(Unit) {
            detectHorizontalDragGestures { _, dragAmount ->
                offset += dragAmount
            }
        }
)
```

**Правила:**
- Изменение структуры UI → Composition + Layout + Drawing
- Изменение размеров/позиций → Layout + Drawing
- Изменение визуальных свойств → только Drawing

### Оптимизация Производительности

**1. Отложенное чтение state:**
```kotlin
// ✅ Читаем state в draw phase вместо composition
Box(
    modifier = Modifier.drawWithContent {
        translate(left = animatedOffset.value) {
            drawContent()
        }
    }
)
```

**2. derivedStateOf для производных значений:**
```kotlin
val filteredCount by remember {
    derivedStateOf {
        items.filter { it.isValid }.size
        // ✅ Пересчёт только при изменении items
    }
}
```

**3. Stable keys для списков:**
```kotlin
LazyColumn {
    items(
        items = list,
        key = { it.id } // ✅ Предотвращает recomposition всего списка
    ) { item -> ItemView(item) }
}
```

---

## Answer (EN)

Jetpack Compose uses a **three-phase asynchronous rendering** pipeline where each phase can execute independently for optimal performance.

### Three Rendering Phases

1. **Composition** — builds UI tree from composable functions
2. **Layout** — measures and positions elements
3. **Drawing** — renders to Canvas via GPU

### Phase 1: Composition

**What happens:**
- Compose calls all `@Composable` functions
- Builds a tree of `LayoutNode` objects
- Tracks state dependencies via snapshot system
- Uses **Slot Table** to store UI structure, state values, remembered values

**Smart recomposition:**
- Skips functions whose parameters haven't changed (skippable composables)
- Recomposes only parts that depend on changed state

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter") // ✅ Recomposes when counter changes
        StaticHeader() // ✅ Never recomposes (no state dependencies)
    }
}
```

### Phase 2: Layout

**Two passes:**

1. **Measure Pass (bottom-up):**
   - Parent passes constraints to children
   - Children measure themselves and report size
   - Each element measured **only once** → O(n) complexity

2. **Placement Pass (top-down):**
   - Parent positions children at coordinates
   - Final positions are established

```kotlin
Layout(content = content, modifier = modifier) { measurables, constraints ->
    // ✅ Measure: each measurable measured once
    val placeables = measurables.map { it.measure(constraints) }

    layout(width, height) {
        // ✅ Placement: positioning without remeasuring
        placeables.forEach { it.placeRelative(x, y) }
    }
}
```

### Phase 3: Drawing

**Rendering to Skia Canvas:**
- Uses `DrawScope` for drawing operations
- GPU acceleration via hardware layers
- `graphicsLayer` creates separate hardware layer for transformations

```kotlin
Box(
    modifier = Modifier
        .graphicsLayer {
            // ✅ GPU-accelerated transformations without recomposition
            rotationZ = 45f
            alpha = 0.8f
        }
        .drawBehind {
            drawRect(Color.Blue) // ✅ Custom drawing
        }
)
```

### Phase Independence (Key Optimization)

Phases execute independently:

```kotlin
var offset by remember { mutableStateOf(0f) }

Box(
    modifier = Modifier
        .offset { IntOffset(offset.roundToInt(), 0) }
        // ✅ Only layout phase, no recomposition
        .pointerInput(Unit) {
            detectHorizontalDragGestures { _, dragAmount ->
                offset += dragAmount
            }
        }
)
```

**Rules:**
- Structure changes → Composition + Layout + Drawing
- Size/position changes → Layout + Drawing
- Visual property changes → Drawing only

### Performance Optimization

**1. Deferred state reads:**
```kotlin
// ✅ Read state in draw phase instead of composition
Box(
    modifier = Modifier.drawWithContent {
        translate(left = animatedOffset.value) {
            drawContent()
        }
    }
)
```

**2. derivedStateOf for computed values:**
```kotlin
val filteredCount by remember {
    derivedStateOf {
        items.filter { it.isValid }.size
        // ✅ Recalculates only when items change
    }
}
```

**3. Stable keys for lists:**
```kotlin
LazyColumn {
    items(
        items = list,
        key = { it.id } // ✅ Prevents recomposition of entire list
    ) { item -> ItemView(item) }
}
```

---

## Follow-ups

- How does Compose handle animations without triggering recomposition?
- What makes a composable function "skippable"?
- When should you use `graphicsLayer` vs `drawWithContent`?
- How does Slot Table track state dependencies?
- What is the performance impact of nested lazy lists?

## References

- [[q-recomposition-compose--android--medium]] - Smart recomposition internals
- [[q-compose-slot-table-recomposition--android--hard]] - Slot table and recomposition tracking
- [[q-mutable-state-compose--android--medium]] - State management fundamentals

## Related Questions

### Prerequisites
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals
- [[q-how-jetpack-compose-works--android--medium]] - How Compose works

### Related
- [[q-compose-stability-skippability--android--hard]] - Stability & skippability
- [[q-compose-modifier-system--android--medium]] - Modifier system
- [[q-compose-custom-layout--android--hard]] - Custom layout implementation

### Advanced
- [[q-compose-performance-optimization--android--hard]] - Performance optimization techniques
- [[q-compose-compiler-plugin--android--hard]] - Compiler transformations
