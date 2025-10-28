---
id: 20251012-122710
title: Compose Modifier Order Performance / Порядок модификаторов и производительность
aliases:
  - Compose Modifier Order Performance
  - Порядок модификаторов и производительность Compose
  - Modifier Chain Optimization
  - Оптимизация цепочки модификаторов
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
  - q-compose-recomposition-optimization--android--hard
sources: []
created: 2025-10-15
updated: 2025-10-28
tags:
  - android/performance-memory
  - android/ui-compose
  - difficulty/medium
---

# Вопрос (RU)
> Как порядок модификаторов влияет на производительность в Jetpack Compose?

# Question (EN)
> How does modifier order affect performance in Jetpack Compose?

---

## Ответ (RU)

### Основные правила

**Направление обработки**:
- Размер и ограничения: верх → низ
- Отрисовка: низ → верх
- Размещайте размерные модификаторы рано — сокращаете работу вниз по цепочке

**Критичные зоны**:
- Padding vs background: порядок меняет область отрисовки
- Clickable area: где стоит модификатор — такая область клика
- Переиспользуйте цепочки: избегайте условного построения, используйте `.then()`

**Производительность**:
- Draw-only модификаторы дешевле layout-модификаторов
- Переиспользуйте дорогие объекты (`Brush`, `Shape`, `Painter`)
- Фиксированные размеры предпочтительнее intrinsic измерений

### Паттерны

**Padding + Background**
```kotlin
// ❌ Background покрывает только внутреннюю область
Modifier
    .padding(16.dp)
    .background(Color.Blue)

// ✅ Background покрывает всю область
Modifier
    .background(Color.Blue)
    .padding(16.dp)
```

**Ранние ограничения**
```kotlin
// ✅ Размер рано → меньше работы downstream
Modifier
    .size(100.dp)
    .background(Color.Blue)
    .padding(8.dp)

// ❌ Размер поздно → измерения проходят весь путь
Modifier
    .padding(8.dp)
    .background(Color.Blue)
    .size(100.dp)
```

**Область клика**
```kotlin
// ❌ Маленькая область: 48×48dp
Modifier
    .size(48.dp)
    .clickable { }

// ✅ Большая область: 48dp + padding
Modifier
    .padding(12.dp)
    .clickable { }
    .size(48.dp)
```

**Переиспользование цепочек**
```kotlin
// ✅ Одна цепочка с .then()
val baseModifier = Modifier.size(100.dp)
val finalModifier = baseModifier
    .then(if (isClickable) Modifier.clickable { onClick() } else Modifier)
    .then(if (selected) Modifier.border(2.dp, Color.Blue) else Modifier)

// ❌ Разные цепочки — реаллокации
val modifier = if (isClickable) {
    Modifier.size(100.dp).clickable { onClick() }
} else {
    Modifier.size(100.dp)
}
```

**Draw vs Layout**
```kotlin
// ✅ Draw-only: без layout прохода
fun Modifier.debugBorder() = drawWithContent {
    drawContent()
    drawRect(Color.Red, style = Stroke(2.dp.toPx()))
}

// ❌ Layout модификатор: дороже
fun Modifier.debugBorder() = border(2.dp, Color.Red)
```

### Профилирование

**Инструменты**:
- Layout Inspector: визуализация recomposition
- Perfetto: трейсинг frame timing
- Composition tracing: счётчик перекомпозиций

**Метрики**:
- Recomposition count: <3 на UI событие
- Layout passes: избегайте вложенных intrinsic измерений
- Аллокации: `Brush`/`Shape` переиспользуются

## Answer (EN)

### Core Rules

**Processing direction**:
- Size and constraints: top → bottom
- Drawing: bottom → top
- Place sizing modifiers early — reduces downstream work

**Critical zones**:
- Padding vs background: order changes draw area
- Clickable area: modifier placement defines touch target
- Reuse chains: avoid conditional construction, use `.then()`

**Performance**:
- Draw-only modifiers cheaper than layout modifiers
- Reuse expensive objects (`Brush`, `Shape`, `Painter`)
- Fixed sizes preferred over intrinsic measurements

### Patterns

**Padding + Background**
```kotlin
// ❌ Background covers only inner area
Modifier
    .padding(16.dp)
    .background(Color.Blue)

// ✅ Background covers full area
Modifier
    .background(Color.Blue)
    .padding(16.dp)
```

**Early constraints**
```kotlin
// ✅ Size early → less downstream work
Modifier
    .size(100.dp)
    .background(Color.Blue)
    .padding(8.dp)

// ❌ Size late → measurements traverse entire chain
Modifier
    .padding(8.dp)
    .background(Color.Blue)
    .size(100.dp)
```

**Click area**
```kotlin
// ❌ Small area: 48×48dp
Modifier
    .size(48.dp)
    .clickable { }

// ✅ Large area: 48dp + padding
Modifier
    .padding(12.dp)
    .clickable { }
    .size(48.dp)
```

**Chain reuse**
```kotlin
// ✅ Single chain with .then()
val baseModifier = Modifier.size(100.dp)
val finalModifier = baseModifier
    .then(if (isClickable) Modifier.clickable { onClick() } else Modifier)
    .then(if (selected) Modifier.border(2.dp, Color.Blue) else Modifier)

// ❌ Different chains — reallocations
val modifier = if (isClickable) {
    Modifier.size(100.dp).clickable { onClick() }
} else {
    Modifier.size(100.dp)
}
```

**Draw vs Layout**
```kotlin
// ✅ Draw-only: no layout pass
fun Modifier.debugBorder() = drawWithContent {
    drawContent()
    drawRect(Color.Red, style = Stroke(2.dp.toPx()))
}

// ❌ Layout modifier: more expensive
fun Modifier.debugBorder() = border(2.dp, Color.Red)
```

### Profiling

**Tools**:
- Layout Inspector: recomposition visualization
- Perfetto: frame timing traces
- Composition tracing: recomposition counters

**Metrics**:
- Recomposition count: <3 per UI event
- Layout passes: avoid nested intrinsic measurements
- Allocations: `Brush`/`Shape` reuse

---

## Follow-ups

- How to detect unnecessary re-measurements in modifier chains?
- When to use `drawBehind` vs `drawWithContent` vs `drawWithCache`?
- How does modifier chain allocation affect scrolling performance?
- What's the impact of conditional modifiers on composition locality?

## References

- [[c-data-structures]]
- [[c-compose-phases]]
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/modifiers

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]
- [[q-compose-state-vs-remember--android--easy]]

### Related (Same Level)
- [[q-compose-gesture-detection--android--medium]]
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]
- [[q-compose-recomposition-optimization--android--hard]]
