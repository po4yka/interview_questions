---
id: 20251012-1227104
title: Modifier System in Compose / Система Modifier в Compose
aliases: [Modifier System in Compose, Система Modifier в Compose]
topic: android
subtopics: [ui-compose, performance]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/jetpack/compose/modifiers
source_note: Official Compose modifier docs
status: reviewed
moc: moc-android
related: [q-animated-visibility-vs-content--jetpack-compose--medium, q-compose-gesture-detection--jetpack-compose--medium, q-compose-compiler-plugin--jetpack-compose--hard]
created: 2025-10-06
updated: 2025-10-20
tags: [android/ui-compose, compose/modifiers, performance, difficulty/medium]
---
# Question (EN)
> How does the Modifier system work in Jetpack Compose, and why does order matter for performance and behavior?

# Вопрос (RU)
> Как работает система Modifier в Jetpack Compose и почему порядок влияет на поведение и производительность?

---

## Answer (EN)

### What is Modifier
- Ordered, immutable chain that decorates or adds behavior to composables
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

## Ответ (RU)

### Что такое Modifier
- Упорядоченная, неизменяемая цепочка, декорирующая/добавляющая поведение
- Влияет на фазы measure, layout и draw

### Модель выполнения
- Measure/layout: сверху вниз
- Draw: снизу вверх

### Эффекты порядка (минимальные паттерны)
Padding vs background
```kotlin
// Фон покрывает внутреннюю область (padding снаружи)
Modifier.padding(16.dp).background(Color.Red).size(100.dp)
// Фон на всю область (padding внутри)
Modifier.background(Color.Red).padding(16.dp).size(100.dp)
```
Область клика
```kotlin
// Маленькая зона (48×48)
Modifier.size(48.dp).clickable { }.padding(12.dp)
// Большая зона (включает padding)
Modifier.padding(12.dp).clickable { }.size(48.dp)
```
Clip перед background
```kotlin
Modifier.clip(CircleShape).background(Color.Red) // Скруглённый фон
```
Ранние ограничения
```kotlin
Modifier.size(100.dp).background(Color.Blue).padding(8.dp)
```

### Лучшие практики
- `modifier: Modifier = Modifier` — первым параметром; применять модификатор пользователя первым в цепочке
- Переиспользовать цепочки; избегать ветвления; использовать `.then(...)`
- Предпочитать draw‑модификаторы для эффектов; кешировать дорогие объекты
- Избегать глубоких цепочек и лишних intrinsic‑мер

### Минимальные примеры
Единая цепочка с условиями
```kotlin
val base = Modifier.size(100.dp)
val mod = base
  .then(if (isClickable) Modifier.clickable { onClick() } else Modifier)
  .then(if (isSelected) Modifier.border(2.dp, Color.Blue) else Modifier)
Box(mod)
```
Избежать перерасчёта при рекомпозиции
```kotlin
@Composable
fun PriceTag(amount: BigDecimal) {
  val text = remember(amount) { formatter.format(amount) }
  Text(text)
}
```

---

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
- [[q-animated-visibility-vs-content--jetpack-compose--medium]]
- [[q-compose-gesture-detection--jetpack-compose--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--jetpack-compose--hard]]
- [[q-compose-custom-layout--jetpack-compose--hard]]
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]]

