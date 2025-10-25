---
id: 20251012-122710
title: Modifier System in Compose / Система Modifier в Compose
aliases:
- Modifier System in Compose
- Система Modifier в Compose
topic: android
subtopics:
- ui-compose
- performance-memory
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-animated-visibility-vs-content--android--medium
- q-compose-gesture-detection--android--medium
- q-compose-compiler-plugin--android--hard
created: 2025-10-06
updated: 2025-10-20
tags:
- android/ui-compose
- android/performance-memory
- difficulty/medium
source: https://developer.android.com/jetpack/compose/modifiers
source_note: Official Compose modifier docs
---

# Вопрос (RU)
> Система Modifier в Compose?

# Question (EN)
> Modifier System in Compose?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### What is Modifier
- Ordered, immutable chain that decorates or adds behavior to composables in [[c-jetpack-compose]]
- Affects measure, layout, and draw phases

### Execution model
- Measure/layout: top → bottom
- Draw: bottom → top

### Order effects (minimal patterns)
Padding vs background
```kotlin
// Background covers inner area (padding outside)
Modifier.padding(16.dp).background(Color.Red).size(100.dp)
// Background on full area (padding inside)
Modifier.background(Color.Red).padding(16.dp).size(100.dp)
```
Clickable area
```kotlin
// Small hit area (48×48)
Modifier.size(48.dp).clickable { }.padding(12.dp)
// Larger hit area (padding included)
Modifier.padding(12.dp).clickable { }.size(48.dp)
```
Clip before background
```kotlin
Modifier.clip(CircleShape).background(Color.Red) // Rounded background
```
Constrain early
```kotlin
Modifier.size(100.dp).background(Color.Blue).padding(8.dp)
```

### Best practices
- Put `modifier: Modifier = Modifier` first in parameters; apply user modifier first in chain
- Reuse chains; avoid branching with separate chains; prefer `.then(...)`
- Prefer draw‑only modifiers for effects; remember expensive objects
- Avoid deep modifier stacks and unnecessary intrinsics

### Minimal examples
Single chain with conditions
```kotlin
val base = Modifier.size(100.dp)
val mod = base
  .then(if (isClickable) Modifier.clickable { onClick() } else Modifier)
  .then(if (isSelected) Modifier.border(2.dp, Color.Blue) else Modifier)
Box(mod)
```
Avoid recompute on recomposition
```kotlin
@Composable
fun PriceTag(amount: BigDecimal) {
  val text = remember(amount) { formatter.format(amount) }
  Text(text)
}
```

## Follow-ups
- When to use draw modifiers instead of layout modifiers?
- How to profile modifier chains’ cost with Layout Inspector and Perfetto?
- How does modifier order interact with nested containers (Box/Row/Column)?

## References
- https://developer.android.com/jetpack/compose/modifiers
- https://developer.android.com/develop/ui/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-gesture-detection--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]
