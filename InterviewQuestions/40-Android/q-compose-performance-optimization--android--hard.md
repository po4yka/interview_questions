---
id: android-443
title: Compose Performance Optimization / Оптимизация производительности Compose
aliases: [Compose Performance Optimization, Оптимизация производительности Compose]
topic: android
subtopics: [performance-memory, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, q-android-performance-measurement-tools--android--medium, q-compose-compiler-plugin--android--hard, q-compose-lazy-layout-optimization--android--hard, q-compose-modifier-order-performance--android--medium, q-compose-stability-skippability--android--hard]
created: 2025-10-20
updated: 2025-11-10
tags: [android/performance-memory, android/ui-compose, difficulty/hard]
sources:
  - "https://developer.android.com/jetpack/compose/mental-model"
  - "https://developer.android.com/jetpack/compose/performance"

---
# Вопрос (RU)

> Как оптимизировать производительность Jetpack Compose? Какие техники минимизации рекомпозиций и аллокаций?

# Question (EN)

> How to optimize Jetpack Compose performance? What techniques minimize recompositions and allocations?

---

## Ответ (RU)

### Краткая Версия
- Минимизируйте область рекомпозиции за счет декомпозиции UI и гранулярного состояния.
- Обеспечьте стабильность входных данных (`@Immutable`, `@Stable`, стабильные колбэки).
- Используйте `remember` и `derivedStateOf` для кэширования и производных вычислений.
- Оптимизируйте lazy-списки (ключи, `contentType`, prefetch).
- Сокращайте аллокации и измеряйте эффект с помощью инструментов профилирования.

### Подробная Версия
### Принципы Оптимизации

1. **Минимизация области рекомпозиции** — разбивать UI на мелкие компоненты, наблюдать за гранулярным состоянием; следить, чтобы каждый composable получал только реально необходимые ему данные.
2. **Стабильность входных данных** — использовать immutable/@Stable классы, по возможности стабильные колбэки и параметры.
3. **Предвычисление** — `remember`/`derivedStateOf` для тяжелых вычислений или производных значений.
4. **Переиспользование в lazy-списках** — ключи, `contentType`, item prefetch.
5. **Снижение аллокаций** — кэшировать shapes/brushes/painters, избегать лишнего создания объектов в composable-функциях.
6. **Измерение** — Layout Inspector, Perfetto, Macrobenchmark, compiler metrics для валидации оптимизаций.

### Архитектура

- Разбивайте экран на независимые composable, каждый из которых читает только свой участок состояния.
- Держите состояние как можно ближе к месту использования, избегайте избыточного проброса.
- Используйте стабильные модели и явно управляемые точки рекомпозиции (container + leaf-компоненты).

### Ключевые Техники

**1. Гранулярное наблюдение состояния**

```kotlin
// ✅ Наблюдаем за полями раздельно — ограничиваем scope рекомпозиции этого уровня
val title by vm.title.collectAsState()
val count by vm.count.collectAsState()
Header(title)  // рекомпозируется только Header при изменении title
Counter(count) // рекомпозируется только Counter при изменении count

// ⚠️ Наблюдаем за всем объектом — Screen(state) будет пересоздаваться целиком,
// если Screen пробрасывает state дальше без разделения.
// Если внутри Screen состояние грамотно "расщеплено" по дочерним composable,
// scope рекомпозиции все еще может быть локализован.
val state by vm.uiState.collectAsState()
Screen(state)
```

**2. Стабильные колбэки**

```kotlin
// ✅ Method reference обычно стабилен, если vm стабилен
Button(onClick = vm::onSubmit) { Text("Submit") }

// ✅ remember с пустыми ключами — создаст лямбду один раз,
// важно, чтобы vm был стабилен
val onClick = remember { { vm.onSubmit() } }
Button(onClick = onClick) { Text("Submit") }

// ❌ Захват изменяемого состояния без remember может порождать
// новую лямбду на каждую рекомпозицию и мешать пропускам
var count by mutableStateOf(0)
Button(onClick = { vm.submit(count) }) { Text("Go") }
```

**3. Immutable/@Stable модели**

```kotlin
// ✅ @Immutable сообщает компилятору, что экземпляры этого типа
// не меняют внутреннее состояние после создания.
// Это помогает безопасно пропускать рекомпозиции,
// когда ссылка на объект не изменилась.
@Immutable
data class Product(val id: String, val name: String, val price: Double)

// ✅ @Stable сообщает, какие свойства могут меняться, не меняя "идентичность" объекта.
// Изменения стабильных observable-свойств (mutableStateOf) триггерят только
// те composable, которые их читают.
@Stable
class UiState {
    var loading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
}
```

**4. derivedStateOf для вычислений**

```kotlin
// ✅ Вычисляется только при изменении зависимостей (firstVisibleItemIndex)
val listState = rememberLazyListState()
val showFab by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 3 }
}
if (showFab) {
    FloatingActionButton(onClick = {}) { Icon(/* ... */) }
}
```

**5. Lazy-списки: ключи и contentType**

```kotlin
// ✅ Ключи для стабильной идентификации, contentType для эффективного переиспользования
// Лучше использовать стабильные и относительно крупные contentType, а не уникальные значения для каждого item
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

- **Layout Inspector** — счетчики рекомпозиции и пропусков, визуальные границы.
- **Perfetto/Systrace** — frame timing, jank detection, корреляция всплесков нагрузки с рекомпозициями/измерениями.
- **Compiler metrics** — отчеты компилятора Compose (включаются через Gradle-флаги) для анализа stability/skippability composable-функций и типов.
- **Macrobenchmark** — измерение startup, jank и frame metrics под реальной нагрузкой.

## Answer (EN)

### Short Version
- Minimize recomposition scope via decomposition and granular state.
- Ensure stable inputs (`@Immutable`, `@Stable`, stable callbacks).
- Use `remember` and `derivedStateOf` for caching and derived calculations.
- Optimize lazy lists (keys, `contentType`, prefetch).
- Reduce allocations and validate changes with profiling tools.

### Detailed Version
### Optimization Principles

1. **Minimize recomposition scope** — split UI into small composables, expose and observe only the specific state each composable needs.
2. **Stable inputs** — use immutable/@Stable classes and, where possible, stable callbacks and parameters.
3. **Precomputation** — use `remember`/`derivedStateOf` for expensive or derived calculations.
4. **Lazy list reuse** — keys, `contentType`, item prefetch.
5. **Reduce allocations** — cache shapes/brushes/painters, avoid unnecessary object creation inside composables.
6. **Measurement** — Layout Inspector, Perfetto, Macrobenchmark, compiler metrics to validate optimizations.

### Architecture

- Split the screen into independent composables, each reading only its own slice of state.
- Keep state as close as possible to where it is used, avoid unnecessary propagation.
- Use stable models and explicit recomposition boundaries (container + leaf components).

### Key Techniques

**1. Granular state observation**

```kotlin
// ✅ Observe fields separately — limits recomposition scope at this level
val title by vm.title.collectAsState()
val count by vm.count.collectAsState()
Header(title)  // only Header recomposes when title changes
Counter(count) // only Counter recomposes when count changes

// ⚠️ Observing the whole object — Screen(state) will recompose as a whole
// if it forwards state without splitting it.
// If Screen internally decomposes state per child composable,
// recomposition can still be scoped.
val state by vm.uiState.collectAsState()
Screen(state)
```

**2. Stable callbacks**

```kotlin
// ✅ Method reference is usually stable if vm is stable
Button(onClick = vm::onSubmit) { Text("Submit") }

// ✅ remember with empty keys creates the lambda once;
// this is effective when vm itself is stable
val onClick = remember { { vm.onSubmit() } }
Button(onClick = onClick) { Text("Submit") }

// ❌ Capturing mutable state without remember may allocate
// a new lambda on each recomposition and hurt skipping
var count by mutableStateOf(0)
Button(onClick = { vm.submit(count) }) { Text("Go") }
```

**3. Immutable/@Stable models**

```kotlin
// ✅ @Immutable tells the compiler instances do not mutate internally
// so if the reference does not change, recomposition can often be skipped safely.
@Immutable
data class Product(val id: String, val name: String, val price: Double)

// ✅ @Stable declares how changes affect identity.
// Changes to observable stable properties (mutableStateOf) trigger
// recomposition only for composables that read them.
@Stable
class UiState {
    var loading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
}
```

**4. derivedStateOf for computations**

```kotlin
// ✅ Recomputes only when its dependencies (firstVisibleItemIndex) change
val listState = rememberLazyListState()
val showFab by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 3 }
}
if (showFab) {
    FloatingActionButton(onClick = {}) { Icon(/* ... */) }
}
```

**5. Lazy lists: keys and contentType**

```kotlin
// ✅ Keys for stable identification, contentType for efficient item reuse.
// Prefer stable, relatively coarse content types over per-item unique values.
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

- **Layout Inspector** — recomposition and skip counters, visual bounds.
- **Perfetto/Systrace** — frame timing, jank detection, correlating spikes with recompositions/measure phases.
- **Compiler metrics** — Compose compiler reports (enabled via Gradle flags) to inspect stability/skippability of composables and types.
- **Macrobenchmark** — startup, jank, frame metrics under realistic workloads.

---

## Дополнительные Вопросы (RU)

- Когда использовать `derivedStateOf` vs `remember { calculated }`?
- Как интерпретировать compiler metrics для проверки stability/skippability?
- Стратегии для больших lazy-списков — paging, prefetch, item prefetch?
- Как предотвратить рекомпозиции в глубоко вложенных иерархиях?
- Трейдоффы между микрооптимизациями и читаемостью кода?

## Follow-ups

- When to use `derivedStateOf` vs `remember { calculated }`?
- How to interpret compiler metrics for checking stability/skippability?
- Strategies for large lazy lists — paging, prefetch, item prefetch?
- How to prevent recompositions in deeply nested hierarchies?
- Trade-offs between micro-optimizations and code readability?

## Ссылки (RU)

- [[c-compose-recomposition]]
- [[moc-android]]
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model
- https://developer.android.com/jetpack/compose/performance/stability

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
