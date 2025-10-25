---
id: 20251012-122710
title: Compose Modifier Order Performance / Порядок модификаторов и производительность
aliases: [Compose Modifier Order Performance, Порядок модификаторов и производительность Compose]
topic: android
subtopics:
  - performance-memory
  - ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-compose-compiler-plugin--android--hard
  - q-compose-custom-layout--android--hard
  - q-compose-gesture-detection--android--medium
created: 2025-10-15
updated: 2025-10-20
tags: [android/performance-memory, android/ui-compose, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:39 pm
---

# Вопрос (RU)
> Порядок модификаторов и производительность?

# Question (EN)
> Compose Modifier Order Performance?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core Rules
- Order changes constraints and draw: size/padding/layout run top→bottom; draw runs bottom→top.
- Apply size/constraints early; avoid re‑measuring work later in the chain.
- Padding vs background: order changes what area is drawn/padded.
- Click/scroll area depends on where interactive modifiers appear.
- Reuse modifier chains; avoid building different chains conditionally; prefer `.then(...)`.
- Prefer draw‑only modifiers over layout when possible; remember expensive objects.

### Minimal Patterns

Padding vs background
```kotlin
// Background covers inner area (padding outside)
Modifier.padding(16.dp).background(Color.Blue).size(100.dp)

// Background covers full area (padding inside)
Modifier.background(Color.Blue).padding(16.dp).size(100.dp)
```

Constrain early
```kotlin
// Better: size early reduces downstream work
Modifier.size(100.dp).background(Color.Blue).padding(8.dp)
```

Clickable area semantics
```kotlin
// Small hit area: 48×48
Modifier.size(48.dp).clickable { }.padding(12.dp)

// Larger hit area (includes padding)
Modifier.padding(12.dp).clickable { }.size(48.dp)
```

Single chain with .then
```kotlin
val base = Modifier.size(100.dp)
val modifier = base
  .then(if (isClickable) Modifier.clickable { onClick() } else Modifier)
  .then(if (isSelected) Modifier.border(2.dp, Color.Blue) else Modifier)
Box(modifier)
```

Draw vs layout
```kotlin
// Draw‑only border: avoids layout cost
fun Modifier.debugBorder() = drawWithContent {
  drawContent(); drawRect(Color.Red, style = Stroke(2.dp.toPx()))
}
```

Avoid recomposition work
```kotlin
@Composable
fun PriceTag(amount: BigDecimal) {
  val formatted = remember(amount) { priceFormatter.format(amount) }
  Text(formatted)
}
```

### Measurement and Profiling
- Prefer fixed sizes over intrinsics; avoid deep nested modifiers.
- Reuse `Brush/Shape/Painter`; do not allocate per frame/item.
- Inspect with Layout Inspector; record with Perfetto; watch recomposition counts.

## Follow-ups
- How to detect and minimize unnecessary child re‑measurements?
- When to use draw modifiers vs layout modifiers for effects?
- How to profile modifier chains’ impact on jank?

## References
- [[c-data-structures]] - Chain structure for modifier composition
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/modifiers

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-compose-gesture-detection--android--medium]]
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]
