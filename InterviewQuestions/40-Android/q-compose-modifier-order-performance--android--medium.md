---
id: android-317
title: Compose Modifier Order Performance / Порядок модификаторов и производительность
aliases: [Compose Modifier Order Performance, Modifier Chain Optimization, Оптимизация цепочки модификаторов, Порядок модификаторов и производительность Compose]
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
  - c-compose-modifiers
  - c-compose-phases
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/performance-memory, android/ui-compose, compose, difficulty/medium, optimization]
date created: Thursday, October 30th 2025, 11:23:09 am
date modified: Saturday, November 1st 2025, 5:43:36 pm
---

# Вопрос (RU)
> Как порядок модификаторов влияет на производительность в Jetpack Compose?

# Question (EN)
> How does modifier order affect performance in Jetpack Compose?

---

## Ответ (RU)

### Направление Обработки

Модификаторы работают в двух фазах:
- **Constraints & measurement** (верх → низ): размерные ограничения идут вниз
- **Drawing** (низ → верх): отрисовка начинается от самого вложенного

**Оптимизация**: размещайте size/width/height рано в цепочке — downstream модификаторы получают фиксированные constraints, избегая лишних измерений.

### Критические Паттерны

**1. Padding + Background**
```kotlin
// ✅ Background покрывает всю область
Modifier
    .background(Color.Blue)
    .padding(16.dp)

// ❌ Background только внутри padding
Modifier
    .padding(16.dp)
    .background(Color.Blue)
```

**2. Ранние размерные ограничения**
```kotlin
// ✅ Размер установлен — дальше по цепочке нет пересчётов
Modifier
    .size(100.dp)
    .padding(8.dp)
    .background(Color.Blue)

// ❌ Размер в конце — измерения проходят всю цепочку
Modifier
    .padding(8.dp)
    .background(Color.Blue)
    .size(100.dp)
```

**3. Область клика**
```kotlin
// ✅ Click область включает padding
Modifier
    .padding(12.dp)
    .clickable { onClick() }
    .size(48.dp)

// ❌ Click только на 48×48dp
Modifier
    .size(48.dp)
    .clickable { onClick() }
```

**4. Переиспользование с `.then()`**
```kotlin
// ✅ Одна цепочка, избегаем аллокаций
val modifier = Modifier.size(100.dp)
    .then(if (clickable) Modifier.clickable { } else Modifier)
    .then(if (selected) Modifier.border(2.dp, Color.Blue) else Modifier)

// ❌ Условные построения создают новые цепочки
val modifier = if (clickable) {
    Modifier.size(100.dp).clickable { }
} else {
    Modifier.size(100.dp)
}
```

**5. Draw vs Layout модификаторы**
```kotlin
// ✅ drawWithContent — только draw phase
fun Modifier.debugBorder() = drawWithContent {
    drawContent()
    drawRect(Color.Red, style = Stroke(2.dp.toPx()))
}

// ❌ border() — проходит layout phase
fun Modifier.debugBorder() = border(2.dp, Color.Red)
```

### Ключевые Принципы

- **Draw-only дешевле layout**: используйте `drawBehind`/`drawWithContent` для визуальных эффектов
- **Переиспользуйте объекты**: `Brush`, `Shape`, `Painter` — выносите в константы или `remember`
- **Фиксированные размеры**: `size(100.dp)` предпочтительнее `wrapContentSize()` или intrinsic measurements
- **Избегайте вложенных intrinsic**: `Row(Modifier.height(IntrinsicSize.Min))` внутри `Column(IntrinsicSize.Max)` вызывает multiple pass

### Профилирование

- **Layout Inspector**: композиции + recomposition count
- **Perfetto traces**: frame timing, skipped frames
- **Composition tracing**: включить через `adb shell setprop debug.compose.trace true`

**Целевые метрики**:
- Recompositions на UI event: <3
- Layout passes на frame: 1 (избегайте multi-pass)
- Allocations: минимизировать в hot paths

## Answer (EN)

### Processing Direction

Modifiers operate in two phases:
- **Constraints & measurement** (top → bottom): size constraints flow down
- **Drawing** (bottom → top): drawing starts from innermost modifier

**Optimization**: place size/width/height early in chain — downstream modifiers receive fixed constraints, avoiding unnecessary measurements.

### Critical Patterns

**1. Padding + Background**
```kotlin
// ✅ Background covers full area
Modifier
    .background(Color.Blue)
    .padding(16.dp)

// ❌ Background only inside padding
Modifier
    .padding(16.dp)
    .background(Color.Blue)
```

**2. Early size constraints**
```kotlin
// ✅ Size set early — no recalculations downstream
Modifier
    .size(100.dp)
    .padding(8.dp)
    .background(Color.Blue)

// ❌ Size at end — measurements traverse entire chain
Modifier
    .padding(8.dp)
    .background(Color.Blue)
    .size(100.dp)
```

**3. Click area**
```kotlin
// ✅ Click area includes padding
Modifier
    .padding(12.dp)
    .clickable { onClick() }
    .size(48.dp)

// ❌ Click only on 48×48dp
Modifier
    .size(48.dp)
    .clickable { onClick() }
```

**4. Chain reuse with `.then()`**
```kotlin
// ✅ Single chain, avoid allocations
val modifier = Modifier.size(100.dp)
    .then(if (clickable) Modifier.clickable { } else Modifier)
    .then(if (selected) Modifier.border(2.dp, Color.Blue) else Modifier)

// ❌ Conditional constructions create new chains
val modifier = if (clickable) {
    Modifier.size(100.dp).clickable { }
} else {
    Modifier.size(100.dp)
}
```

**5. Draw vs Layout modifiers**
```kotlin
// ✅ drawWithContent — draw phase only
fun Modifier.debugBorder() = drawWithContent {
    drawContent()
    drawRect(Color.Red, style = Stroke(2.dp.toPx()))
}

// ❌ border() — goes through layout phase
fun Modifier.debugBorder() = border(2.dp, Color.Red)
```

### Key Principles

- **Draw-only cheaper than layout**: use `drawBehind`/`drawWithContent` for visual effects
- **Reuse objects**: `Brush`, `Shape`, `Painter` — extract to constants or `remember`
- **Fixed sizes**: `size(100.dp)` preferred over `wrapContentSize()` or intrinsic measurements
- **Avoid nested intrinsics**: `Row(Modifier.height(IntrinsicSize.Min))` inside `Column(IntrinsicSize.Max)` causes multiple passes

### Profiling

- **Layout Inspector**: compositions + recomposition counts
- **Perfetto traces**: frame timing, skipped frames
- **Composition tracing**: enable via `adb shell setprop debug.compose.trace true`

**Target metrics**:
- Recompositions per UI event: <3
- Layout passes per frame: 1 (avoid multi-pass)
- Allocations: minimize in hot paths

---

## Follow-ups

- How does `Modifier.composed()` affect performance and when should it be avoided?
- What is the cost of conditional modifiers vs using `Modifier.then()` in hot paths?
- How do intrinsic measurements impact layout performance in nested Compose layouts?
- When should custom `LayoutModifier` be used instead of built-in modifiers?
- How can Layout Inspector be used to detect redundant recompositions caused by modifier chains?

## References

- [[c-compose-phases]]
- [[c-compose-modifiers]]
- [[c-compose-recomposition]]
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/modifiers
- https://developer.android.com/develop/ui/compose/modifiers-list

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-compose-gesture-detection--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]
