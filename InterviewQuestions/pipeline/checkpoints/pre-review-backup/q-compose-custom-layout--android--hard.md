---
id: 20251012-122804
title: Compose Custom Layout / Кастомный layout в Compose
aliases:
- Compose Custom Layout
- Кастомный layout в Compose
topic: android
subtopics:
- ui-compose
- ui-views
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-compose-compiler-plugin--android--hard
- q-compose-canvas-graphics--android--hard
- q-android-performance-measurement-tools--android--medium
created: 2025-10-11
updated: 2025-10-20
tags:
- android/ui-compose
- android/ui-views
- difficulty/hard
---

# Вопрос (RU)
> Кастомный layout в Compose?

# Question (EN)
> Compose Custom Layout?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core concepts
- Constraints: min/max width/height from parent; all measuring/placement must respect them
- MeasurePolicy: measure children → compute layout size → place children
- Intrinsics: optional size hints for pre‑measurement (text wrap, etc.)
- Performance: no allocation in measure/place; reuse arrays/positions; stable params
- Uses [[c-algorithms]] for layout calculations and [[c-data-structures]] for efficient measurement

### Minimal custom Layout
```kotlin
@Composable
fun TwoColumn(modifier: Modifier = Modifier, gap: Int = 8, content: @Composable () -> Unit) {
  Layout(content = content, modifier = modifier) { measurables, constraints ->
    val mid = (measurables.size + 1) / 2
    val leftMs = measurables.subList(0, mid)
    val rightMs = measurables.subList(mid, measurables.size)

    val left = leftMs.map { it.measure(constraints.copy(maxWidth = constraints.maxWidth / 2 - gap)) }
    val right = rightMs.map { it.measure(constraints.copy(maxWidth = constraints.maxWidth / 2)) }

    val colH1 = left.sumOf { it.height }
    val colH2 = right.sumOf { it.height }
    val width = constraints.maxWidth
    val height = (maxOf(colH1, colH2)).coerceIn(constraints.minHeight, constraints.maxHeight)

    layout(width, height) {
      var y = 0
      left.forEach { p -> p.placeRelative(0, y); y += p.height }
      y = 0
      right.forEach { p -> p.placeRelative(width / 2 + gap, y); y += p.height }
    }
  }
}
```

### With MeasurePolicy (reusable)
```kotlin
val twoColumnPolicy = MeasurePolicy { measurables, constraints ->
  // same logic as above; keep pure and allocation‑free
}
@Composable fun TwoColumn2(mod: Modifier = Modifier, content: @Composable () -> Unit) {
  Layout(content, mod, twoColumnPolicy)
}
```

### Intrinsics (optional)
```kotlin
val policy = object : MeasurePolicy {
  override fun MeasureScope.measure(measurables: List<Measurable>, constraints: Constraints): MeasureResult { /* ... */ }
  override fun IntrinsicMeasureScope.minIntrinsicHeight(measurables: List<IntrinsicMeasurable>, w: Int) =
    measurables.sumOf { it.minIntrinsicHeight(w) }
}
```

### Tips
- Keep calculations deterministic; avoid reading composition state during measure
- Prefer stable/immutable params to maximize skip; precompute constants with remember
- Use placeRelative for RTL; avoid nested measurements; test with different constraints

## Follow-ups
- How to design constraint‑driven APIs that scale to complex grids?
- When to expose intrinsics and how to validate them?
- How to detect over‑measurement and fix performance regressions?

## References
- https://developer.android.com/develop/ui/compose/layouts/custom
- https://developer.android.com/develop/ui/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-animated-visibility-vs-content--android--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-canvas-graphics--android--hard]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
