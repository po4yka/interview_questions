---
id: 20251020-200000
title: "Compose Performance Optimization / Оптимизация производительности Compose"
aliases: [Compose Performance Optimization, Оптимизация производительности Compose]
topic: android
subtopics: [ui-compose, performance]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/jetpack/compose/performance
source_note: Official Compose performance guide
status: reviewed
related: [q-compose-compiler-plugin--jetpack-compose--hard, q-compose-lazy-layout-optimization--jetpack-compose--hard, q-android-performance-measurement-tools--android--medium]
created: 2025-10-20
updated: 2025-10-20
tags: [android/ui-compose, android/performance, performance, recomposition, stability, difficulty/hard]
moc: moc-android
---

# Question (EN)
> How do you optimize Jetpack Compose performance and avoid unnecessary recompositions? Provide minimal patterns and when to use them.

# Вопрос (RU)
> Как оптимизировать производительность Jetpack Compose и избегать лишних рекомпозиций? Приведите минимальные паттерны и когда их применять.

---

## Answer (EN)

### Principles

- Minimize recomposition scope (observe granular state, split UI).
- Prefer stable inputs (immutable/@Stable) and stable callbacks.
- Precompute/derive values with `remember`/`derivedStateOf`.
- Use keys and content types in lazy lists for reuse and diffing.
- Avoid allocations in hot paths; reuse shapes/brushes/painters.
- Measure and verify with tools; optimize only confirmed hotspots.

### Minimal patterns

Granular state observation

```kotlin
// Observe fields separately to limit recomposition
val title by vm.title.collectAsState()
val body by vm.body.collectAsState()
Header(title); Body(body)
```

Stable callbacks

```kotlin
// Avoid capturing changing state in lambdas
val onClick = remember { { vm.onClick() } }
Button(onClick) { Text("Go") }
// or method reference
Button(onClick = vm::onClick) { Text("Go") }
```

Immutable/@Stable models

```kotlin
@Immutable data class Product(val id: String, val name: String)
@Stable class UiState { var selected by mutableStateOf<String?>(null) }
```

Derived values

```kotlin
val listState = rememberLazyListState()
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

Lazy reuse (keys, contentType)

```kotlin
LazyColumn {
  items(items = data, key = { it.id }, contentType = { it.type }) { item ->
    Row { Text(item.title) }
  }
}
```

Avoid recomposition propagation

```kotlin
// Do not pass frequently changing primitives down if not needed
var counter by remember { mutableStateOf(0) }
Button({ counter++ }) { Text("$counter") }
ExpensiveChild() // independent of counter
```

Remember expensive work

```kotlin
val formatted = remember(price) { priceFormatter.format(price) }
Text(formatted)
```

### Measurement and tooling

- Use Layout Inspector (Recomposition counts), Perfetto, tracing.
- Track jank and long frames; correlate with recomposition spikes.
- Verify skips with compiler metrics (Compose compiler reports).

## Ответ (RU)

### Принципы

- Минимизируйте область рекомпозиции (наблюдайте поля отдельно, делите UI).
- Используйте стабильные входы (immutable/@Stable) и стабильные колбэки.
- Предвычисляйте/выводите значения через `remember`/`derivedStateOf`.
- В списках используйте keys и contentType для переиспользования и диффинга.
- Избегайте аллокаций в горячих участках; переиспользуйте shape/brush/painter.
- Измеряйте перед оптимизацией; подтверждайте узкие места.

### Минимальные паттерны

Гранулярное наблюдение состояния

```kotlin
val title by vm.title.collectAsState()
val body by vm.body.collectAsState()
Header(title); Body(body)
```

Стабильные колбэки

```kotlin
val onClick = remember { { vm.onClick() } }
Button(onClick) { Text("Go") }
// или ссылка на метод
Button(onClick = vm::onClick) { Text("Go") }
```

Immutable/@Stable модели

```kotlin
@Immutable data class Product(val id: String, val name: String)
@Stable class UiState { var selected by mutableStateOf<String?>(null) }
```

Производные значения

```kotlin
val listState = rememberLazyListState()
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

Переиспользование в списках (keys, contentType)

```kotlin
LazyColumn {
  items(items = data, key = { it.id }, contentType = { it.type }) { item ->
    Row { Text(item.title) }
  }
}
```

Избегание распространения рекомпозиции

```kotlin
var counter by remember { mutableStateOf(0) }
Button({ counter++ }) { Text("$counter") }
ExpensiveChild()
```

Кэширование дорогих вычислений

```kotlin
val formatted = remember(price) { priceFormatter.format(price) }
Text(formatted)
```

### Измерение и инструменты

- Layout Inspector (Recomposition counts), Perfetto, трассировка.
- Отслеживайте jank/длинные кадры и соотносите со всплесками рекомпозиций.
- Проверяйте пропуски фаз отчётами компилятора Compose.

---

## Follow-ups

- When to use `derivedStateOf` vs memoizing with `remember`?
- How to validate stability/skippability using compiler metrics?
- Strategies for large lazy lists (paging, prefetch, snapshots)?

## References

- [Compose Performance Guide](https://developer.android.com/jetpack/compose/performance)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)

## Related Questions

### Prerequisites (Easier)

- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)

- [[q-compose-compiler-plugin--jetpack-compose--hard]]
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]]

### Advanced (Harder)

- [[q-compose-custom-layout--jetpack-compose--hard]]
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]]
