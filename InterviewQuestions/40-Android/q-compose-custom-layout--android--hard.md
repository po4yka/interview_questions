---
id: 20251012-122804
title: Compose Custom Layout / Кастомный layout в Compose
aliases: [Compose Custom Layout, Кастомный layout в Compose, Custom Layout Jetpack Compose, Кастомная разметка Compose]
topic: android
subtopics: [ui-compose, ui-views]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-compose-canvas-graphics--android--hard
  - q-compose-compiler-plugin--android--hard
  - q-android-performance-measurement-tools--android--medium
sources: []
created: 2025-10-11
updated: 2025-10-28
tags: [android/ui-compose, android/ui-views, difficulty/hard, custom-layout, layout-measurement]
---

# Вопрос (RU)
> Как создать кастомный layout в Compose? Объясните механизм measurement и placement.

# Question (EN)
> How to create a custom layout in Compose? Explain the measurement and placement mechanism.

---

## Ответ (RU)

### Основные концепции

**Constraints (ограничения)** - диапазон min/max width/height от родителя. Все дочерние элементы **обязаны** измеряться и размещаться в пределах этих constraints.

**MeasurePolicy** - контракт из трех шагов:
1. Измерить дочерние элементы (measurables)
2. Вычислить итоговый размер layout
3. Разместить дочерние элементы (place)

**Ключевые правила**:
- Каждый measurable измеряется **ровно один раз**
- Нельзя аллоцировать объекты в measure/place (performance)
- Использовать `placeRelative` для RTL-поддержки
- Параметры должны быть stable/immutable для skip-оптимизации

### Минималистичный custom layout

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
        val rightWidth = constraints.maxWidth - leftWidth - gapPx

        val leftPlaceables = leftMeasurables.map {
            it.measure(constraints.copy(maxWidth = leftWidth))
        }
        val rightPlaceables = rightMeasurables.map {
            it.measure(constraints.copy(maxWidth = rightWidth))
        }

        // Вычисляем итоговую высоту
        val leftHeight = leftPlaceables.sumOf { it.height }
        val rightHeight = rightPlaceables.sumOf { it.height }
        val totalHeight = maxOf(leftHeight, rightHeight)
            .coerceIn(constraints.minHeight, constraints.maxHeight)

        layout(constraints.maxWidth, totalHeight) {
            var yLeft = 0
            leftPlaceables.forEach { placeable ->
                placeable.placeRelative(0, yLeft)
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

```kotlin
// ✅ MeasurePolicy вне composable для переиспользования
private val twoColumnMeasurePolicy = MeasurePolicy { measurables, constraints ->
    // Та же логика, но без capture composable-параметров
    // Все параметры должны быть stable
    // ...
}

@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(content, modifier, twoColumnMeasurePolicy)
}
```

### Intrinsics (опционально)

Intrinsics нужны для случаев, когда родителю нужно знать размер **до** реального measurement (например, для text wrapping).

```kotlin
val policy = object : MeasurePolicy {
    override fun MeasureScope.measure(
        measurables: List<Measurable>,
        constraints: Constraints
    ): MeasureResult {
        // Основная логика
    }

    // ❌ Без intrinsics Compose выдаст warning
    override fun IntrinsicMeasureScope.minIntrinsicHeight(
        measurables: List<IntrinsicMeasurable>,
        width: Int
    ) = measurables.sumOf { it.minIntrinsicHeight(width) }

    override fun IntrinsicMeasureScope.maxIntrinsicHeight(
        measurables: List<IntrinsicMeasurable>,
        width: Int
    ) = measurables.sumOf { it.maxIntrinsicHeight(width) }
}
```

### Performance Tips

- **Избегать аллокаций**: не создавать списки/массивы в measure-блоке
- **Stable параметры**: `gap: Dp` вместо `gap: State<Dp>` для skip
- **Детерминизм**: не читать composition state внутри measure
- **Тестирование**: проверять с разными constraints, включая min=max

## Answer (EN)

### Core Concepts

**Constraints** - min/max width/height range from parent. All children **must** measure and place within these constraints.

**MeasurePolicy** - contract with three steps:
1. Measure children (measurables)
2. Calculate final layout size
3. Place children

**Key Rules**:
- Each measurable measured **exactly once**
- No allocations in measure/place (performance)
- Use `placeRelative` for RTL support
- Parameters must be stable/immutable for skip optimization

### Minimal Custom Layout

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
        val rightWidth = constraints.maxWidth - leftWidth - gapPx

        val leftPlaceables = leftMeasurables.map {
            it.measure(constraints.copy(maxWidth = leftWidth))
        }
        val rightPlaceables = rightMeasurables.map {
            it.measure(constraints.copy(maxWidth = rightWidth))
        }

        // Calculate final height
        val leftHeight = leftPlaceables.sumOf { it.height }
        val rightHeight = rightPlaceables.sumOf { it.height }
        val totalHeight = maxOf(leftHeight, rightHeight)
            .coerceIn(constraints.minHeight, constraints.maxHeight)

        layout(constraints.maxWidth, totalHeight) {
            var yLeft = 0
            leftPlaceables.forEach { placeable ->
                placeable.placeRelative(0, yLeft)
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

```kotlin
// ✅ MeasurePolicy outside composable for reuse
private val twoColumnMeasurePolicy = MeasurePolicy { measurables, constraints ->
    // Same logic but without capturing composable parameters
    // All parameters must be stable
    // ...
}

@Composable
fun TwoColumn(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(content, modifier, twoColumnMeasurePolicy)
}
```

### Intrinsics (Optional)

Intrinsics are needed when parent needs to know size **before** actual measurement (e.g., text wrapping).

```kotlin
val policy = object : MeasurePolicy {
    override fun MeasureScope.measure(
        measurables: List<Measurable>,
        constraints: Constraints
    ): MeasureResult {
        // Main logic
    }

    // ❌ Without intrinsics Compose will show warning
    override fun IntrinsicMeasureScope.minIntrinsicHeight(
        measurables: List<IntrinsicMeasurable>,
        width: Int
    ) = measurables.sumOf { it.minIntrinsicHeight(width) }

    override fun IntrinsicMeasureScope.maxIntrinsicHeight(
        measurables: List<IntrinsicMeasurable>,
        width: Int
    ) = measurables.sumOf { it.maxIntrinsicHeight(width) }
}
```

### Performance Tips

- **Avoid allocations**: don't create lists/arrays in measure block
- **Stable parameters**: `gap: Dp` instead of `gap: State<Dp>` for skip
- **Determinism**: don't read composition state inside measure
- **Testing**: check with various constraints, including min=max

---

## Follow-ups

- How to implement efficient grid layout with dynamic cell sizes?
- When should you implement intrinsic measurements vs using default behavior?
- How to debug over-measurement issues in nested custom layouts?
- What are the performance implications of measuring all children vs lazy measurement?

## References

- [Custom layouts in Compose](https://developer.android.com/develop/ui/compose/layouts/custom)
- [Compose performance best practices](https://developer.android.com/develop/ui/compose/performance)
- [Layout basics - Constraints and measurement](https://developer.android.com/develop/ui/compose/layouts/basics)

## Related Questions

### Prerequisites (Easier)
- [[q-animated-visibility-vs-content--android--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-canvas-graphics--android--hard]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
