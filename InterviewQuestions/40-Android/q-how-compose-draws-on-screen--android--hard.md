---\
id: android-152
title: How Compose Draws On Screen / Как Compose рисует на экране
aliases: [How Compose Draws On Screen, Как Compose рисует на экране]
topic: android
subtopics: [performance-rendering, ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-jetpack-compose, c-performance, q-compose-core-components--android--medium, q-compose-custom-animations--android--medium, q-compose-performance-optimization--android--hard, q-compose-stability-skippability--android--hard, q-how-does-jetpackcompose-work--android--medium, q-recomposition-compose--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android, android/performance-rendering, android/ui-compose, difficulty/medium, rendering]
sources: []
---\
# Вопрос (RU)

> Как Jetpack Compose отрисовывает UI на экране? Опишите трёхфазный процесс рендеринга.

# Question (EN)

> How does Jetpack Compose render UI on screen? Describe the three-phase rendering process.

---

## Ответ (RU)

Jetpack Compose использует **трёхфазный пайплайн рендеринга**, в котором логически разделены этапы Composition, Layout и Drawing. Эти фазы могут выполняться отдельно (например, только Layout/Drawing без изменения Composition), что позволяет оптимизировать производительность, но они остаются упорядоченными в рамках кадра и не являются полностью независимыми или произвольно асинхронными.

### Три Фазы Рендеринга

1. **Composition (Композиция)** — построение дерева UI из composable-функций
2. **Layout (Размещение)** — измерение и позиционирование элементов
3. **Drawing (Рисование)** — рисование на `Canvas` (через Skia), с аппаратным ускорением

### Фаза 1: Composition

**Что происходит:**
- Compose вызывает `@Composable` функции
- Строится дерево `LayoutNode`
- Отслеживаются зависимости от state через snapshot system
- Используется **Slot Table** для хранения структуры UI и значений `remember`

**Умная рекомпозиция:**
- Пропускает функции, параметры и наблюдаемый state которых не изменились (skippable composables)
- Рекомпонует только части, зависящие от изменившегося state

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter") // ✅ Рекомпонуется при изменении counter
        StaticHeader() // ✅ Не рекомпонуется из-за counter (если параметры стабильны)
    }
}
```

### Фаза 2: Layout

**Два прохода:**

1. **Measure Pass (снизу вверх):**
   - Родитель передаёт constraints детям
   - Дети измеряют себя и возвращают размер
   - Каждый measurable должен быть измерен не более одного раза для данного набора constraints в корректной реализации (на практике возможны дополнительные измерения при других constraints)

2. **Placement Pass (сверху вниз):**
   - Родитель размещает детей в координатах
   - Устанавливаются финальные позиции

```kotlin
@Composable
fun SimpleCustomLayout(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        // ✅ Measure: измеряем каждого ребёнка с переданными constraints
        val placeables = measurables.map { it.measure(constraints) }

        // Для примера используем максимальную ширину и суммарную высоту
        val width = constraints.maxWidth
        val height = placeables.sumOf { it.height }

        layout(width, height) {
            var y = 0
            // ✅ Placement: позиционирование без повторного измерения
            placeables.forEach { placeable ->
                placeable.placeRelative(x = 0, y = y)
                y += placeable.height
            }
        }
    }
}
```

### Фаза 3: Drawing

**Рисование на Skia `Canvas`:**
- Используется `DrawScope` для операций рисования
- GPU-ускорение через аппаратные слои
- `graphicsLayer` может создавать отдельный слой для трансформаций и эффектов

```kotlin
Box(
    modifier = Modifier
        .graphicsLayer {
            // ✅ GPU-ускоренные трансформации без изменения Composition
            rotationZ = 45f
            alpha = 0.8f
        }
        .drawBehind {
            drawRect(Color.Blue) // ✅ Кастомное рисование
        }
)
```

### Взаимосвязь И Разделение Фаз (Ключевая Идея)

Фазы могут запускаться выборочно в ответ на изменения:

```kotlin
var offset by remember { mutableStateOf(0f) }

Box(
    modifier = Modifier
        .offset { IntOffset(offset.roundToInt(), 0) }
        .pointerInput(Unit) {
            detectHorizontalDragGestures { _, dragAmount ->
                offset += dragAmount
            }
        }
)
```

- Обновление `offset` — это изменение state, которое триггерит рекомпозицию того scope, где `offset` читается, а также обновление Layout/Drawing для затронутых элементов.
- На практике возможно обновлять только Layout/Drawing без повторной Composition, если состояние читается в соответствующих фазах или изменения изолированы.

**Эмпирические правила:**
- Изменение структуры UI (какие composables существуют) → Composition + Layout + Drawing
- Изменение размеров/позиций (layout-зависимые параметры) → Layout + Drawing (может сопровождаться рекомпозицией, если меняется state в Composition)
- Изменение чисто визуальных свойств, читаемых в draw-фазе (например, через `drawWithContent`) → преимущественно Drawing; однако если свойство читается в Composition, изменение вызовет и рекомпозицию

### Оптимизация Производительности

**1. Отложенное чтение state:**
```kotlin
// ✅ Читаем state в draw phase вместо composition, чтобы избежать лишней рекомпозиции
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
        items.count { it.isValid }
        // ✅ Пересчёт только при изменении items или их isValid
    }
}
```

**3. Stable keys для списков:**
```kotlin
LazyColumn {
    items(
        items = list,
        key = { it.id } // ✅ Сохраняет идентичность элементов и уменьшает ненужные перевычеркивания/пересоздания
    ) { item ->
        ItemView(item)
    }
}
```

---

## Дополнительные Вопросы (RU)

- Как Compose обрабатывает анимации без избыточной рекомпозиции?
- Что делает composable-функцию "skippable"?
- Когда следует использовать `graphicsLayer` по сравнению с `drawWithContent`?
- Как Slot Table помогает отслеживать композицию и состояние?
- Каково влияние на производительность при использовании вложенных lazy-списков?

## Ссылки (RU)

- [[q-recomposition-compose--android--medium]] — детали умной рекомпозиции
- [[q-compose-slot-table-recomposition--android--hard]] — Slot Table и отслеживание рекомпозиции
- [[q-mutable-state-compose--android--medium]] — основы управления состоянием

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-compose-state]]
- [[c-jetpack-compose]]
- [[c-performance]]

### Предпосылки

- [[q-jetpack-compose-basics--android--medium]] — основы Compose
- [[q-how-jetpack-compose-works--android--medium]] — как работает Compose

### Связанные

- [[q-compose-stability-skippability--android--hard]] — стабильность и skippability
- [[q-compose-modifier-system--android--medium]] — система модификаторов
- [[q-compose-custom-layout--android--hard]] — реализация кастомного layout

### Продвинутое

- [[q-compose-performance-optimization--android--hard]] — техники оптимизации производительности
- [[q-compose-compiler-plugin--android--hard]] — трансформации компилятором

---

## Answer (EN)

Jetpack Compose uses a **three-stage rendering pipeline** with distinct Composition, Layout, and Drawing phases. These phases can be run selectively (e.g., layout/draw updates without structural recomposition), enabling performance optimizations, but they remain ordered within a frame and are not fully independent or arbitrarily asynchronous.

### Three Rendering Phases

1. **Composition** — builds the UI tree from composable functions
2. **Layout** — measures and positions elements
3. **Drawing** — draws onto a `Canvas` (via Skia) with hardware acceleration

### Phase 1: Composition

**What happens:**
- Compose invokes `@Composable` functions
- Builds a tree of `LayoutNode` objects
- Tracks state dependencies via the snapshot system
- Uses the **Slot Table** to store UI structure and `remember` values

**Smart recomposition:**
- Skips functions whose parameters and observed state haven't changed (skippable composables)
- Recomposes only the parts that depend on changed state

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter") // ✅ Recomposes when counter changes
        StaticHeader() // ✅ Not recomposed due to counter changes (if its inputs are stable)
    }
}
```

### Phase 2: Layout

**Two passes:**

1. **Measure Pass (bottom-up):**
   - Parent passes constraints to children
   - Children measure themselves and report size
   - In a correct layout, each measurable is measured at most once per constraint set; additional measurements may occur with different constraints when needed

2. **Placement Pass (top-down):**
   - Parent positions children at coordinates
   - Final positions are assigned

```kotlin
@Composable
fun SimpleCustomLayout(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        // ✅ Measure: measure each child with provided constraints
        val placeables = measurables.map { it.measure(constraints) }

        // For example, use max width and sum of heights
        val width = constraints.maxWidth
        val height = placeables.sumOf { it.height }

        layout(width, height) {
            var y = 0
            // ✅ Placement: position children without re-measuring
            placeables.forEach { placeable ->
                placeable.placeRelative(x = 0, y = y)
                y += placeable.height
            }
        }
    }
}
```

### Phase 3: Drawing

**Rendering to Skia `Canvas`:**
- Uses `DrawScope` for drawing operations
- Hardware acceleration via GPU-backed layers
- `graphicsLayer` can create separate layers for transformations and effects

```kotlin
Box(
    modifier = Modifier
        .graphicsLayer {
            // ✅ GPU-accelerated transforms without changing Composition
            rotationZ = 45f
            alpha = 0.8f
        }
        .drawBehind {
            drawRect(Color.Blue) // ✅ Custom drawing
        }
)
```

### Phase Interaction and Separation (Key Idea)

Phases can be triggered selectively in response to changes:

```kotlin
var offset by remember { mutableStateOf(0f) }

Box(
    modifier = Modifier
        .offset { IntOffset(offset.roundToInt(), 0) }
        .pointerInput(Unit) {
            detectHorizontalDragGestures { _, dragAmount ->
                offset += dragAmount
            }
        }
)
```

- Updating `offset` is a state change; it will trigger recomposition of the scope that reads it and corresponding layout/draw updates.
- In practice you can structure code so that some changes affect only layout/draw (e.g., reading state inside layout/draw lambdas) without forcing a full structural recomposition.

**Heuristic rules:**
- Structural changes (which composables are present) → Composition + Layout + Drawing
- Size/position changes (layout-affecting parameters) → Layout + Drawing (may involve recomposition if driven by state read in Composition)
- Pure visual changes read in the draw phase (e.g., inside `drawWithContent`) → primarily Drawing; if the value is read in Composition, its change also triggers recomposition

### Performance Optimization

**1. Deferred state reads:**
```kotlin
// ✅ Read state in the draw phase instead of composition to avoid unnecessary recompositions
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
        items.count { it.isValid }
        // ✅ Recomputes only when items or their isValid flags change
    }
}
```

**3. Stable keys for lists:**
```kotlin
LazyColumn {
    items(
        items = list,
        key = { it.id } // ✅ Preserves item identity and reduces unnecessary item disposal/moves
    ) { item ->
        ItemView(item)
    }
}
```

---

## Follow-ups

- How does Compose handle animations without triggering unnecessary recomposition?
- What makes a composable function "skippable"?
- When should you use `graphicsLayer` vs `drawWithContent`?
- How does the Slot Table help track composition and state?
- What is the performance impact of nested lazy lists?

## References

- [[q-recomposition-compose--android--medium]] - Smart recomposition internals
- [[q-compose-slot-table-recomposition--android--hard]] - Slot table and recomposition tracking
- [[q-mutable-state-compose--android--medium]] - State management fundamentals

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]
- [[c-performance]]

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
