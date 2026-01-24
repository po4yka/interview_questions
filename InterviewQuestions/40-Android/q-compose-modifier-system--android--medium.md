---
id: android-021
title: Modifier System in Compose / Система модификаторов в Compose
aliases:
- Modifier System in Compose
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
- c-compose-recomposition
- c-recomposition
- q-android-performance-measurement-tools--android--medium
- q-animated-visibility-vs-content--android--medium
- q-compose-compiler-plugin--android--hard
- q-compose-core-components--android--medium
- q-compose-custom-animations--android--medium
- q-compose-gesture-detection--android--medium
- q-compose-modifier-order-performance--android--medium
created: 2025-10-06
updated: 2025-10-30
tags:
- android/performance-memory
- android/ui-compose
- difficulty/medium
sources:
- https://developer.android.com/jetpack/compose/modifiers
anki_cards:
- slug: android-021-0-en
  language: en
  anki_id: 1768366068275
  synced_at: '2026-01-23T16:45:05.818050'
- slug: android-021-0-ru
  language: ru
  anki_id: 1768366068299
  synced_at: '2026-01-23T16:45:05.819199'
---
# Вопрос (RU)

> Как работает система Modifier в Jetpack Compose? Объясните порядок выполнения, влияние на производительность и ключевые паттерны использования.

# Question (EN)

> How does the Modifier system work in Jetpack Compose? Explain execution order, performance implications, and key usage patterns.

---

## Ответ (RU)

### Архитектура И Концепция

Modifier представляет собой упорядоченную, неизменяемую цепочку элементов-модификаторов, применяемых к компонуемому элементу. Каждый элемент может участвовать в одной или нескольких фазах измерения,布局 и отрисовки, формируя конвейер трансформации и поведения.

**Модель выполнения**:

- Измерение/Layout (обход сверху вниз): концептуально, внешние модификаторы обрабатывают и могут корректировать входящие ограничения/позиционирование перед делегированием внутренним. На практике каждый Modifier.Element определяет, как он обрабатывает измерение/layout; не каждый модификатор влияет на все фазы.
- Отрисовка/Draw (обход снизу вверх): модификаторы отрисовки вызываются так, чтобы внутреннее содержимое рисовалось первым, затем внешние модификаторы могут рисовать поверх или вокруг него. Позднее добавленные модификаторы в цепочке становятся логически более "внешними" и могут накладываться на более ранние.

Примечание: Эффективный порядок зависит от того, как реализован каждый элемент, но рассуждение в терминах конвейера внешний-внутренний (измерение/layout) и внутренний-внешний (отрисовка) точно для понимания типичного поведения.

### Критическое Влияние Порядка

**Padding и background**:

```kotlin
// ❌ Фон только внутри (исключает область padding)
Modifier
  .padding(16.dp)
  .background(Color.Red)
  .size(100.dp)

// ✅ Фон на всей визуальной области (включая padding)
Modifier
  .background(Color.Red)
  .padding(16.dp)
  .size(100.dp)
```

**Область касания (hit area)**:

```kotlin
// ❌ Маленькая область касания
Modifier
  .size(48.dp)
  .clickable { /* action */ }
  .padding(12.dp)

// ✅ Расширенная область касания
Modifier
  .padding(12.dp)
  .clickable { /* action */ }
  .size(48.dp)
```

**Обрезка перед отрисовкой**:

```kotlin
// ✅ Обрезка должна предшествовать модификаторам отрисовки, если вы хотите обрезать их отрисовку
Modifier
  .clip(CircleShape)
  .background(Color.Red)
```

### Лучшие Практики

**Параметр modifier в компонентах**:

```kotlin
// ✅ Параметр modifier первым в сигнатуре (соглашение)
//    и размещенный первым во внутренней цепочке, чтобы внешние модификаторы были outermost
@Composable
fun CustomButton(
  modifier: Modifier = Modifier,
  onClick: () -> Unit,
  content: @Composable () -> Unit
) {
  Box(
    modifier = modifier // Вызывающие модификаторы применяются первыми (outermost)
      .clickable(onClick = onClick)
      .padding(16.dp)
  ) {
    content()
  }
}
```

Примечание: Порядок сигнатуры является стилевым соглашением; порядок выполнения определяется тем, как вы комбинируете `modifier` с внутренними модификаторами (например, `modifier.then(...)`).

**Условные цепочки**:

```kotlin
// ✅ Используйте then() для условной логики без разрыва цепочки
val modifier = Modifier
  .size(100.dp)
  .then(if (isClickable) Modifier.clickable { onClick() } else Modifier)
  .then(if (isSelected) Modifier.border(2.dp, Color.Blue) else Modifier)
```

### Оптимизация Производительности

- Предпочитайте модификаторы только для отрисовки (например, background, border, drawBehind) для чисто визуальных эффектов, когда они не влияют на размер или layout. Они обычно избегают дополнительной работы measure/layout по сравнению с введением дополнительных модификаторов layout.
- Используйте `remember {}` (или remember-calculated значения) для дорогих вычислений, используемых внутри модификаторов, чтобы избежать повторного вычисления на каждой рекомпозиции.
- Избегайте unnecessarily глубоких или overly фрагментированных цепочек модификаторов; компилятор/рантайм оптимизирует модификаторы, но чрезмерные цепочки все равно могут добавить накладные расходы.
- Минимизируйте intrinsic measurements (например, API на основе intrinsicSize), поскольку они требуют дополнительных проходов измерения и могут быть costly.

## Answer (EN)

### Concept and Architecture

A Modifier is an ordered, immutable chain of modifier elements applied to a composable. Each element can participate in one or more of the measure, layout, and draw phases, forming a transformation and behavior pipeline.

**Execution Model**:

- Measure/Layout (traversal top to bottom): conceptually, outer modifiers process and may adjust the incoming constraints/placement before delegating to inner ones. In practice, each Modifier.Element defines how it handles measurement/layout; not every modifier affects all phases.
- Draw (traversal bottom to top): draw modifiers are invoked so that inner content is drawn first, then outer modifiers can draw on top or around it. Later-added modifiers in the chain become logically more "outer" and can overlay earlier ones.

Note: The effective order depends on how each element is implemented, but reasoning in terms of an outer-to-inner (measure/layout) and inner-to-outer (draw) pipeline is accurate for understanding typical behavior.

### Critical Order Impact

**Padding and background**:

```kotlin
// ❌ Background only inside (excludes padding area)
Modifier
  .padding(16.dp)
  .background(Color.Red)
  .size(100.dp)

// ✅ Background over the full visual area (including padding)
Modifier
  .background(Color.Red)
  .padding(16.dp)
  .size(100.dp)
```

**Hit area**:

```kotlin
// ❌ Small click area
Modifier
  .size(48.dp)
  .clickable { /* action */ }
  .padding(12.dp)

// ✅ Extended click area
Modifier
  .padding(12.dp)
  .clickable { /* action */ }
  .size(48.dp)
```

**Clipping before draw**:

```kotlin
// ✅ Clip should precede draw-related modifiers when you want their drawing clipped
Modifier
  .clip(CircleShape)
  .background(Color.Red)
```

### Best Practices

**Modifier parameter in components**:

```kotlin
// ✅ Modifier as the first parameter in signature (convention)
//    and placed first in the internal chain so external modifiers are outermost
@Composable
fun CustomButton(
  modifier: Modifier = Modifier,
  onClick: () -> Unit,
  content: @Composable () -> Unit
) {
  Box(
    modifier = modifier // Caller-supplied modifiers are applied first (outermost)
      .clickable(onClick = onClick)
      .padding(16.dp)
  ) {
    content()
  }
}
```

Note: The signature order is a style convention; execution order is defined by how you combine `modifier` with internal modifiers (e.g., `modifier.then(...)`).

**Conditional chains**:

```kotlin
// ✅ Use then() for conditional logic without breaking the chain
val modifier = Modifier
  .size(100.dp)
  .then(if (isClickable) Modifier.clickable { onClick() } else Modifier)
  .then(if (isSelected) Modifier.border(2.dp, Color.Blue) else Modifier)
```

### Performance Optimization

- Prefer draw-only modifiers (e.g., background, border, drawBehind) for purely visual effects when they don't need to affect size or layout. They typically avoid extra measure/layout work compared to introducing additional layout modifiers.
- Use `remember {}` (or remember-calculated values) for expensive computations used inside modifiers to avoid recomputing them on each recomposition.
- Avoid unnecessarily deep or overly fragmented modifier chains; the compiler/runtime optimize modifiers, but excessive chains can still add overhead.
- Minimize intrinsic measurements (e.g., intrinsicSize-based APIs) because they require additional measure passes and can be costly.

## Follow-ups

- When should you implement a custom Modifier via `Modifier.Element` vs using built-in modifiers?
- How does the Compose compiler optimize Modifier chains during recomposition?
- What's the performance difference between `.padding().background()` and `.background().padding()`?
- How to debug Modifier execution order with Layout Inspector?
- Why is `Modifier.then()` preferred over conditional `.let {}` blocks?

## References

- [[c-jetpack-compose]]
- [[c-compose-recomposition]]
- [[c-performance-optimization]]
- https://developer.android.com/jetpack/compose/modifiers
- https://developer.android.com/jetpack/compose/modifiers-list
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
