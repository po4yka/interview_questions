---
id: 20251020-200000
title: Compose Performance Optimization / Оптимизация производительности Compose
aliases: [Compose Performance Optimization, Оптимизация производительности Compose]
topic: android
subtopics:
  - performance-memory
  - ui-compose
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-performance-measurement-tools--android--medium
  - q-compose-compiler-plugin--android--hard
  - q-compose-lazy-layout-optimization--android--hard
created: 2025-10-20
updated: 2025-01-27
tags: [android/performance-memory, android/ui-compose, difficulty/hard]
sources: [https://developer.android.com/jetpack/compose/performance]
---
# Вопрос (RU)
> Как оптимизировать производительность Jetpack Compose?

# Question (EN)
> How to optimize Jetpack Compose performance?

---

## Ответ (RU)

### Принципы

- Минимизировать область рекомпозиции (наблюдать за гранулярным состоянием, разделять UI)
- Использовать стабильные входные данные (immutable/@Stable) и стабильные колбэки
- Вычислять значения заранее с помощью `remember`/`derivedStateOf`
- Применять ключи и типы контента в lazy-списках для переиспользования
- Избегать аллокаций в горячих путях; переиспользовать shapes/brushes/painters
- Измерять и верифицировать инструментами; оптимизировать только подтвержденные узкие места

### Ключевые паттерны

**Гранулярное наблюдение состояния**

```kotlin
// ✅ Наблюдаем за полями раздельно — ограничивает рекомпозицию
val title by vm.title.collectAsState()
val body by vm.body.collectAsState()
Header(title); Body(body)

// ❌ Не наблюдаем за всем объектом сразу
val state by vm.uiState.collectAsState()
Screen(state)  // рекомпозирует весь экран при любом изменении
```

**Стабильные колбэки**

```kotlin
// ✅ Избегаем захвата изменяемого состояния в лямбдах
val onClick = remember { { vm.onClick() } }
Button(onClick) { Text("Go") }

// ✅ Используем method reference
Button(onClick = vm::onClick) { Text("Go") }

// ❌ Захватываем переменную состояние — колбэк нестабилен
var count by mutableStateOf(0)
Button({ vm.onClick(count) }) { Text("Go") }
```

**Immutable/@Stable модели**

```kotlin
// ✅ Компилятор пропускает рекомпозицию при неизмененных данных
@Immutable data class Product(val id: String, val name: String)
@Stable class UiState { var selected by mutableStateOf<String?>(null) }
```

**Вычисляемые значения**

```kotlin
// ✅ derivedStateOf вычисляется только при изменении зависимости
val listState = rememberLazyListState()
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

**Переиспользование в Lazy-списках**

```kotlin
// ✅ Ключи и contentType ускоряют диффинг и переиспользование элементов
LazyColumn {
  items(items = data, key = { it.id }, contentType = { it.type }) { item ->
    Row { Text(item.title) }
  }
}
```

### Инструменты измерения

- Layout Inspector (счетчики рекомпозиции), Perfetto, tracing
- Отслеживание jank и long frames; корреляция со всплесками рекомпозиций
- Проверка пропуска рекомпозиций через compiler metrics

## Answer (EN)

### Principles

- Minimize recomposition scope (observe granular state, split UI)
- Prefer stable inputs (immutable/@Stable) and stable callbacks
- Precompute/derive values with `remember`/`derivedStateOf`
- Use keys and content types in lazy lists for reuse and diffing
- Avoid allocations in hot paths; reuse shapes/brushes/painters
- Measure and verify with tools; optimize only confirmed hotspots

### Key Patterns

**Granular state observation**

```kotlin
// ✅ Observe fields separately — limits recomposition
val title by vm.title.collectAsState()
val body by vm.body.collectAsState()
Header(title); Body(body)

// ❌ Don't observe entire object
val state by vm.uiState.collectAsState()
Screen(state)  // recomposes entire screen on any change
```

**Stable callbacks**

```kotlin
// ✅ Avoid capturing changing state in lambdas
val onClick = remember { { vm.onClick() } }
Button(onClick) { Text("Go") }

// ✅ Use method reference
Button(onClick = vm::onClick) { Text("Go") }

// ❌ Capturing state variable — callback is unstable
var count by mutableStateOf(0)
Button({ vm.onClick(count) }) { Text("Go") }
```

**Immutable/@Stable models**

```kotlin
// ✅ Compiler skips recomposition when data unchanged
@Immutable data class Product(val id: String, val name: String)
@Stable class UiState { var selected by mutableStateOf<String?>(null) }
```

**Derived values**

```kotlin
// ✅ derivedStateOf recomputes only when dependency changes
val listState = rememberLazyListState()
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

**Lazy list reuse**

```kotlin
// ✅ Keys and contentType accelerate diffing and item reuse
LazyColumn {
  items(items = data, key = { it.id }, contentType = { it.type }) { item ->
    Row { Text(item.title) }
  }
}
```

### Measurement Tools

- Layout Inspector (recomposition counts), Perfetto, tracing
- Track jank and long frames; correlate with recomposition spikes
- Verify skipping via compiler metrics

## Follow-ups

- When to use `derivedStateOf` vs memoizing with `remember`?
- How to validate stability/skippability using compiler metrics?
- Strategies for large lazy lists (paging, prefetch, item prefetch)?
- How to prevent unnecessary recompositions in deeply nested hierarchies?

## References

- [Compose Performance Guide](https://developer.android.com/jetpack/compose/performance)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)

## Related Questions

### Prerequisites (Easier)

- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)

- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]

### Advanced (Harder)

- [[q-compose-custom-layout--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]
