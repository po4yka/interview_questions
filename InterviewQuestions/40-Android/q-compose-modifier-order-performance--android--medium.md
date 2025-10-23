---
id: 20251012-122710
title: Compose Modifier Order Performance / Порядок модификаторов и производительность
  Compose
aliases:
- Compose Modifier Order Performance
- Порядок модификаторов и производительность Compose
topic: android
subtopics:
- ui-compose
- performance
question_kind: android
difficulty: medium
status: reviewed
moc: moc-android
related:
- q-compose-gesture-detection--jetpack-compose--medium
- q-compose-compiler-plugin--jetpack-compose--hard
- q-compose-custom-layout--jetpack-compose--hard
created: 2025-10-15
updated: 2025-10-20
original_language: en
language_tags:
- en
- ru
tags:
- android/ui-compose
- compose/modifiers
- performance
- difficulty/medium
- android/performance
---# Вопрос (RU)
> Как порядок модификаторов влияет на производительность и поведение в Jetpack Compose? Покажите минимальные паттерны для оптимизации measure/layout/draw.

---

# Question (EN)
> How does modifier order affect performance and behavior in Jetpack Compose? Show minimal patterns to optimize measure/layout/draw.

## Ответ (RU)

### Базовые правила
- Порядок меняет ограничения и отрисовку: size/padding/layout идут сверху вниз; draw снизу вверх.
- Применяйте size/constraints раньше; снижайте работу далее в цепочке.
- Padding vs background: порядок меняет область заливки/отступа.
- Область клика/скролла зависит от позиции интерактивных модификаторов.
- Переиспользуйте цепочки; избегайте ветвления; используйте `.then(...)`.
- Предпочитайте draw‑модификаторы изменению layout; кешируйте дорогие объекты.

### Минимальные паттерны

Padding vs background
```kotlin
// Background покрывает внутреннюю область (padding снаружи)
Modifier.padding(16.dp).background(Color.Blue).size(100.dp)

// Background на всю область (padding внутри)
Modifier.background(Color.Blue).padding(16.dp).size(100.dp)
```

Ранние ограничения
```kotlin
// Лучше: size раньше уменьшает работу ниже по цепочке
Modifier.size(100.dp).background(Color.Blue).padding(8.dp)
```

Семантика области клика
```kotlin
// Маленькая зона: 48×48
Modifier.size(48.dp).clickable { }.padding(12.dp)

// Большая зона (включает padding)
Modifier.padding(12.dp).clickable { }.size(48.dp)
```

Единая цепочка через .then
```kotlin
val base = Modifier.size(100.dp)
val modifier = base
  .then(if (isClickable) Modifier.clickable { onClick() } else Modifier)
  .then(if (isSelected) Modifier.border(2.dp, Color.Blue) else Modifier)
Box(modifier)
```

Draw против layout
```kotlin
// Только draw: избегает лишнего layout
fun Modifier.debugBorder() = drawWithContent {
  drawContent(); drawRect(Color.Red, style = Stroke(2.dp.toPx()))
}
```

Избежание работы при рекомпозиции
```kotlin
@Composable
fun PriceTag(amount: BigDecimal) {
  val formatted = remember(amount) { priceFormatter.format(amount) }
  Text(formatted)
}
```

### Измерение и профилирование
- Предпочитайте фиксированные размеры intrinsic‑мерам; избегайте глубоких цепочек.
- Переиспользуйте `Brush/Shape/Painter`; не выделяйте каждый кадр/элемент.
- Анализируйте Layout Inspector; записывайте Perfetto; следите за рекомпозициями.

---

## Answer (EN)

### Core rules
- Order changes constraints and draw: size/padding/layout run top→bottom; draw runs bottom→top.
- Apply size/constraints early; avoid re‑measuring work later in the chain.
- Padding vs background: order changes what area is drawn/padded.
- Click/scroll area depends on where interactive modifiers appear.
- Reuse modifier chains; avoid building different chains conditionally; prefer `.then(...)`.
- Prefer draw‑only modifiers over layout when possible; remember expensive objects.

### Minimal patterns

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

### Measurement and profiling
- Prefer fixed sizes over intrinsics; avoid deep nested modifiers.
- Reuse `Brush/Shape/Painter`; do not allocate per frame/item.
- Inspect with Layout Inspector; record with Perfetto; watch recomposition counts.

## Follow-ups
- How to detect and minimize unnecessary child re‑measurements?
- When to use draw modifiers vs layout modifiers for effects?
- How to profile modifier chains’ impact on jank?

## References
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

