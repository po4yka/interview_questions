---
id: android-443
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
status: reviewed
moc: moc-android
related:
  - c-compose-recomposition
  - q-android-performance-measurement-tools--android--medium
  - q-compose-compiler-plugin--android--hard
  - q-compose-lazy-layout-optimization--android--hard
created: 2025-10-20
updated: 2025-10-30
tags: [android/performance-memory, android/ui-compose, difficulty/hard]
sources:
  - https://developer.android.com/jetpack/compose/mental-model
  - https://developer.android.com/jetpack/compose/performance
---

# Вопрос (RU)

> Как оптимизировать производительность Jetpack Compose? Какие техники минимизации рекомпозиций и аллокаций?

# Question (EN)

> How to optimize Jetpack Compose performance? What techniques minimize recompositions and allocations?

---

## Ответ (RU)

### Принципы Оптимизации

1. **Минимизация области рекомпозиции** — разбивать UI на мелкие компоненты, наблюдать за гранулярным состоянием
2. **Стабильность входных данных** — использовать immutable/@Stable классы, стабильные колбэки
3. **Предвычисление** — `remember`/`derivedStateOf` для тяжелых вычислений
4. **Переиспользование в lazy-списках** — ключи, contentType, item prefetch
5. **Снижение аллокаций** — кэшировать shapes/brushes/painters, избегать создания объектов в composable
6. **Измерение** — Layout Inspector, Perfetto, compiler metrics для валидации оптимизаций

### Ключевые Техники

**1. Гранулярное наблюдение состояния**

```kotlin
// ✅ Наблюдаем за полями раздельно — ограничивает scope рекомпозиции
val title by vm.title.collectAsState()
val count by vm.count.collectAsState()
Header(title)  // рекомпозирует только Header при изменении title
Counter(count) // рекомпозирует только Counter при изменении count

// ❌ Наблюдаем за всем объектом — рекомпозирует весь Screen
val state by vm.uiState.collectAsState()
Screen(state)
```

**2. Стабильные колбэки**

```kotlin
// ✅ Method reference стабилен
Button(onClick = vm::onSubmit) { Text("Submit") }

// ✅ remember с пустыми ключами стабилен
val onClick = remember { { vm.onSubmit() } }

// ❌ Захват изменяемого состояния — нестабильный колбэк
var count by mutableStateOf(0)
Button({ vm.submit(count) }) { Text("Go") }
```

**3. Immutable/@Stable модели**

```kotlin
// ✅ Компилятор пропускает рекомпозицию при equals
@Immutable data class Product(val id: String, val name: String, val price: Double)

// ✅ Стабильный класс с изменяемым состоянием
@Stable class UiState {
    var loading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
}
```

**4. derivedStateOf для вычислений**

```kotlin
// ✅ Вычисляется только при изменении firstVisibleItemIndex
val listState = rememberLazyListState()
val showFab by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 3 }
}
if (showFab) FloatingActionButton(onClick = {}) { Icon(...) }
```

**5. Lazy-списки: ключи и contentType**

```kotlin
// ✅ Ключи для стабильности, contentType для переиспользования
LazyColumn {
    items(
        items = products,
        key = { it.id },
        contentType = { it.category }
    ) { product ->
        ProductCard(product)
    }
}
```

### Инструменты Измерения

- **Layout Inspector** — счетчики рекомпозиции, пропусков, visual bounds
- **Perfetto/Systrace** — frame timing, jank detection, correlation со всплесками
- **Compiler metrics** — проверка skippability/stability классов
- **Macrobenchmark** — startup, jank, frame metrics под реальной нагрузкой

## Answer (EN)

### Optimization Principles

1. **Minimize recomposition scope** — split UI into granular composables, observe fine-grained state
2. **Stable inputs** — use immutable/@Stable classes, stable callbacks
3. **Precomputation** — `remember`/`derivedStateOf` for expensive calculations
4. **Lazy list reuse** — keys, contentType, item prefetch
5. **Reduce allocations** — cache shapes/brushes/painters, avoid object creation in composables
6. **Measurement** — Layout Inspector, Perfetto, compiler metrics to validate optimizations

### Key Techniques

**1. Granular state observation**

```kotlin
// ✅ Observe fields separately — limits recomposition scope
val title by vm.title.collectAsState()
val count by vm.count.collectAsState()
Header(title)  // recomposes only Header when title changes
Counter(count) // recomposes only Counter when count changes

// ❌ Observe entire object — recomposes entire Screen
val state by vm.uiState.collectAsState()
Screen(state)
```

**2. Stable callbacks**

```kotlin
// ✅ Method reference is stable
Button(onClick = vm::onSubmit) { Text("Submit") }

// ✅ remember with empty keys is stable
val onClick = remember { { vm.onSubmit() } }

// ❌ Capturing mutable state — unstable callback
var count by mutableStateOf(0)
Button({ vm.submit(count) }) { Text("Go") }
```

**3. Immutable/@Stable models**

```kotlin
// ✅ Compiler skips recomposition on equals
@Immutable data class Product(val id: String, val name: String, val price: Double)

// ✅ Stable class with mutable state
@Stable class UiState {
    var loading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
}
```

**4. derivedStateOf for computations**

```kotlin
// ✅ Recomputes only when firstVisibleItemIndex changes
val listState = rememberLazyListState()
val showFab by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 3 }
}
if (showFab) FloatingActionButton(onClick = {}) { Icon(...) }
```

**5. Lazy lists: keys and contentType**

```kotlin
// ✅ Keys for stability, contentType for item reuse
LazyColumn {
    items(
        items = products,
        key = { it.id },
        contentType = { it.category }
    ) { product ->
        ProductCard(product)
    }
}
```

### Measurement Tools

- **Layout Inspector** — recomposition counts, skips, visual bounds
- **Perfetto/Systrace** — frame timing, jank detection, correlation with recomposition spikes
- **Compiler metrics** — validate class skippability/stability
- **Macrobenchmark** — startup, jank, frame metrics under real load

---

## Follow-ups

- Когда использовать `derivedStateOf` vs `remember { calculated }`?
- Как интерпретировать compiler metrics для проверки stability/skippability?
- Стратегии для больших lazy-списков — paging, prefetch, item prefetch?
- Как предотвратить рекомпозиции в глубоко вложенных иерархиях?
- Трейдоффы между микрооптимизациями и читаемостью кода?

## References

- [[c-compose-recomposition]]
- [[moc-android]]
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model
- https://developer.android.com/jetpack/compose/performance/stability

## Related Questions

### Prerequisites (Easier)

- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)

- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]

### Advanced (Harder)

- [[q-compose-custom-layout--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]
