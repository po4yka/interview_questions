---
id: android-054
title: Compose Custom Layout / Кастомный layout в Compose
aliases:
- Compose Custom Layout
- Custom Layout Jetpack Compose
- Кастомная разметка Compose
- Кастомный layout в Compose
topic: android
subtopics:
- ui-compose
- ui-graphics
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- c-layouts
- c-compose-state
- c-views
- q-compose-canvas-graphics--android--hard
- q-compose-compiler-plugin--android--hard
sources: []
created: 2025-10-11
updated: 2025-11-02
tags:
- android/ui-compose
- android/ui-graphics
- custom-layout
- difficulty/hard
- layout-measurement
---

# Вопрос (RU)
> Как создать кастомный layout в Compose? Объясните механизм measurement и placement.

# Question (EN)
> How to create a custom layout in Compose? Explain the measurement and placement mechanism.

---

## Ответ (RU)

### Основные Концепции

`Layout` в Compose использует `MeasurePolicy` — контракт из трех шагов:
1. **Measure** — каждый дочерний элемент измеряется с переданными `Constraints` (min/max width/height)
2. **Calculate** — layout вычисляет собственный размер на основе измеренных дочерних элементов
3. **Place** — размещение дочерних элементов в координатах layout

**Ключевые правила**:
- Каждый `Measurable` измеряется **ровно один раз** (иначе exception)
- Нельзя аллоцировать объекты в `measure`/`place` (performance)
- Использовать `placeRelative` для RTL-поддержки

### Минимальный Пример: TwoColumn

```kotlin
@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    gap: Dp = 8.dp,
    content: @Composable () -> Unit
) {
    Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        val gapPx = gap.roundToPx()
        val mid = (measurables.size + 1) / 2

        // ✅ Делим на две колонки
        val leftMeasurables = measurables.subList(0, mid)
        val rightMeasurables = measurables.subList(mid, measurables.size)

        // ✅ Измеряем с уменьшенными constraints
        val leftWidth = (constraints.maxWidth - gapPx) / 2
        val leftPlaceables = leftMeasurables.map {
            it.measure(constraints.copy(maxWidth = leftWidth))
        }
        val rightPlaceables = rightMeasurables.map {
            it.measure(constraints.copy(maxWidth = constraints.maxWidth - leftWidth - gapPx))
        }

        // Вычисляем высоту
        val leftHeight = leftPlaceables.sumOf { it.height }
        val rightHeight = rightPlaceables.sumOf { it.height }
        val totalHeight = maxOf(leftHeight, rightHeight)
            .coerceIn(constraints.minHeight, constraints.maxHeight)

        layout(constraints.maxWidth, totalHeight) {
            var yLeft = 0
            leftPlaceables.forEach { placeable ->
                placeable.placeRelative(0, yLeft) // ✅ placeRelative для RTL
                yLeft += placeable.height
            }

            var yRight = 0
            rightPlaceables.forEach { placeable ->
                placeable.placeRelative(leftWidth + gapPx, yRight)
                yRight += placeable.height
            }
        }
    }
}
```

### Переиспользуемый MeasurePolicy

Для оптимизации можно вынести `MeasurePolicy` как top-level объект:

```kotlin
// ✅ MeasurePolicy вне composable для переиспользования
private val twoColumnMeasurePolicy = MeasurePolicy { measurables, constraints ->
    // Та же логика, но без capture composable-параметров
}

@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(content, modifier, twoColumnMeasurePolicy)
}
```

**Ограничение**: все параметры layout (`gap`, `spacing`) должны быть внешними, так как `MeasurePolicy` не может capture composable state.

### Intrinsics

Intrinsics позволяют parent узнать размер child **до** реального measurement (например, для text wrapping).

```kotlin
val policy = object : MeasurePolicy {
    override fun MeasureScope.measure(
        measurables: List<Measurable>,
        constraints: Constraints
    ): MeasureResult = // ...

    // ❌ Без intrinsics Compose выдаст warning
    override fun IntrinsicMeasureScope.minIntrinsicHeight(
        measurables: List<IntrinsicMeasurable>,
        width: Int
    ) = measurables.sumOf { it.minIntrinsicHeight(width) }
}
```

**Используйте intrinsics** только если parent реально зависит от размера child (например, `Row` с `Modifier.weight`).

### Performance Tips

- **Stable параметры**: `gap: Dp` вместо `gap: State<Dp>` для skip-оптимизации
- **Избегать аллокаций**: не создавать списки в `measure`-блоке, переиспользовать коллекции
- **Детерминизм**: не читать composition state внутри `measure`

## Answer (EN)

### Core Concepts

`Layout` in Compose uses `MeasurePolicy` — a three-step contract:
1. **Measure** — each child is measured with provided `Constraints` (min/max width/height)
2. **Calculate** — layout calculates its own size based on measured children
3. **Place** — position children in layout coordinates

**Key Rules**:
- Each `Measurable` measured **exactly once** (otherwise exception)
- No allocations in `measure`/`place` (performance)
- Use `placeRelative` for RTL support

### Minimal Example: TwoColumn

```kotlin
@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    gap: Dp = 8.dp,
    content: @Composable () -> Unit
) {
    Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        val gapPx = gap.roundToPx()
        val mid = (measurables.size + 1) / 2

        // ✅ Split into two columns
        val leftMeasurables = measurables.subList(0, mid)
        val rightMeasurables = measurables.subList(mid, measurables.size)

        // ✅ Measure with reduced constraints
        val leftWidth = (constraints.maxWidth - gapPx) / 2
        val leftPlaceables = leftMeasurables.map {
            it.measure(constraints.copy(maxWidth = leftWidth))
        }
        val rightPlaceables = rightMeasurables.map {
            it.measure(constraints.copy(maxWidth = constraints.maxWidth - leftWidth - gapPx))
        }

        // Calculate height
        val leftHeight = leftPlaceables.sumOf { it.height }
        val rightHeight = rightPlaceables.sumOf { it.height }
        val totalHeight = maxOf(leftHeight, rightHeight)
            .coerceIn(constraints.minHeight, constraints.maxHeight)

        layout(constraints.maxWidth, totalHeight) {
            var yLeft = 0
            leftPlaceables.forEach { placeable ->
                placeable.placeRelative(0, yLeft) // ✅ placeRelative for RTL
                yLeft += placeable.height
            }

            var yRight = 0
            rightPlaceables.forEach { placeable ->
                placeable.placeRelative(leftWidth + gapPx, yRight)
                yRight += placeable.height
            }
        }
    }
}
```

### Reusable MeasurePolicy

For optimization, extract `MeasurePolicy` as top-level object:

```kotlin
// ✅ MeasurePolicy outside composable for reuse
private val twoColumnMeasurePolicy = MeasurePolicy { measurables, constraints ->
    // Same logic but without capturing composable parameters
}

@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(content, modifier, twoColumnMeasurePolicy)
}
```

**Limitation**: all layout parameters (`gap`, `spacing`) must be external, as `MeasurePolicy` cannot capture composable state.

### Intrinsics

Intrinsics allow parent to know child size **before** actual measurement (e.g., text wrapping).

```kotlin
val policy = object : MeasurePolicy {
    override fun MeasureScope.measure(
        measurables: List<Measurable>,
        constraints: Constraints
    ): MeasureResult = // ...

    // ❌ Without intrinsics Compose will show warning
    override fun IntrinsicMeasureScope.minIntrinsicHeight(
        measurables: List<IntrinsicMeasurable>,
        width: Int
    ) = measurables.sumOf { it.minIntrinsicHeight(width) }
}
```

**Use intrinsics** only if parent really depends on child size (e.g., `Row` with `Modifier.weight`).

### Performance Tips

- **Stable parameters**: `gap: Dp` instead of `gap: State<Dp>` for skip optimization
- **Avoid allocations**: don't create lists in measure block, reuse collections
- **Determinism**: don't read composition state inside measure

---

## Follow-ups

- Как обрабатывать случаи, когда children не помещаются в `constraints`?
- В чем разница между `placeRelative` и `place`?
- Когда нужно реализовывать все 4 intrinsic метода (`minWidth`, `maxWidth`, `minHeight`, `maxHeight`)?
- Как протестировать custom layout с разными `constraints` и RTL?
- Какие проблемы performance возникают при многократном remeasure и как их избежать?

## References

- [Custom layouts in Compose](https://developer.android.com/develop/ui/compose/layouts/custom)
- [Layout basics - Constraints and measurement](https://developer.android.com/develop/ui/compose/layouts/basics)
- [Compose performance best practices](https://developer.android.com/develop/ui/compose/performance)

## Related Questions

### Prerequisites / Concepts

- [[c-layouts]]
- [[c-compose-state]]
- [[c-views]]


### Prerequisites (Easier)

### Related (Same Level)
- [[q-compose-canvas-graphics--android--hard]] — `Canvas` for custom drawing, Layout for custom measurement
- [[q-compose-compiler-plugin--android--hard]] — How Compose compiler optimizes layouts

### Advanced (Harder)
- Custom layouts with complex intrinsic calculations and nested `Constraints`
- Building layout modifiers that affect measurement behavior
- Optimizing layout performance in deep hierarchies with thousands of nodes
