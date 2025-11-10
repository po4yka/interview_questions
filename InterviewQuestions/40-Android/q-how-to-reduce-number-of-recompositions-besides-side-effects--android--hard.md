---
id: android-281
title: "How To Reduce Number Of Recompositions Besides Side Effects / Как уменьшить количество рекомпозиций кроме побочных эффектов"
aliases: ["Compose Performance", "Reduce Recompositions", "Производительность Compose", "Уменьшить рекомпозиции"]
topic: android
subtopics: [performance-rendering, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, q-compose-performance-optimization--android--hard, q-compose-remember-derived-state--android--medium, q-compose-stability-skippability--android--hard, q-recomposition-compose--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/performance-rendering, android/ui-compose, compose, difficulty/hard, recomposition]
---

# Вопрос (RU)

> Как можно уменьшить количество рекомпозиций помимо `side`-эффектов?

# Question (EN)

> How can you reduce the number of recompositions besides using side effects?

---

## Ответ (RU)

Уменьшение рекомпозиций улучшает производительность [[c-compose-recomposition]]. Ключевые техники: `remember`, `derivedStateOf`, стабильные и корректно аннотированные модели данных, неизменяемые коллекции, правильное размещение состояния и использование `key()`.

### 1. Remember Для Дорогих Вычислений

```kotlin
@Composable
fun ExpensiveCalculation(items: List<Item>) {
    // ❌ Пересчитывает при каждой рекомпозиции
    val result = items.map { it.value * 2 }.sum()

    // ✅ Пересчитывает только при изменении items (или их ссылок)
    val result = remember(items) {
        items.map { it.value * 2 }.sum()
    }

    Text("Result: $result")
}
```

### 2. derivedStateOf Для Производного Состояния

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    val items = remember { List(1000) { "Item $it" } }

    // ❌ Фильтрует при каждой рекомпозиции этого scope
    val filteredItems = items.filter { it.contains(query, ignoreCase = true) }

    // ✅ Фильтрует только при изменении query / items
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.contains(query, ignoreCase = true) }
        }
    }

    LazyColumn {
        items(filteredItems) { Text(it) }
    }
}
```

### 3. Стабильные Модели Данных и Аннотации

(Альтернативные варианты, не компилируются вместе, показаны для иллюстрации.)

```kotlin
// ❌ Потенциально нестабильный класс из-за mutable коллекции
//    Изменения friends могут не приводить к новому экземпляру
//    и усложняют отслеживание изменений.
data class UserMutableFriends(
    val name: String,
    val friends: MutableList<String>
)

// ✅ Предпочтительно: неизменяемые поля + @Immutable для ручной подсказки компилятору
@Immutable
data class UserImmutableFriends(
    val name: String,
    val friends: List<String>
)

// ✅ Вариант с persistent коллекциями, аннотированными @Stable
@Stable
data class UserPersistentFriends(
    val name: String,
    val friends: PersistentList<String>
)
```

Аннотации и неизменяемые коллекции сами по себе не уменьшают количество изменений, но помогают компилятору корректно определять стабильность и чаще пропускать рекомпозиции.

### 4. Стабильные Ссылки На Лямбды

```kotlin
// ✅ Обычное использование: лямбда захватывает стабильный viewModel,
//    Compose рассматривает это как стабильный параметр, отдельный remember не нужен.
@Composable
fun ParentScreen(viewModel: ViewModel) {
    ChildScreen(onClick = { viewModel.handleClick() })
}

// ✅ Явная стабилизация полезна, когда лямбда зависит от меняющихся значений,
//    но вы хотите контролировать, когда именно она пересоздаётся.
@Composable
fun ParentScreenControlled(viewModel: ViewModel, enabled: Boolean) {
    val onClick = remember(enabled) {
        { if (enabled) viewModel.handleClick() }
    }
    ChildScreen(onClick = onClick)
}
```

Ключевая идея: избегать создания новых функциональных значений без необходимости, когда это мешает пропускать рекомпозиции дочерних компонентов.

### 5. Правильное Размещение Состояния

```kotlin
// ❌ Состояние слишком высоко: любое изменение текста триггерит пересмотр всего содержимого BadParent
@Composable
fun BadParent() {
    var text1 by remember { mutableStateOf("") }
    var text2 by remember { mutableStateOf("") }

    Column {
        TextField(text1, { text1 = it })
        TextField(text2, { text2 = it })
        StaticContent() // Будет участвовать в рекомпозиции этого scope
    }
}

// ✅ Состояние ближе к использованию, StaticContent не зависит от него
//    и потому не будет вынужденно перерассчитываться при изменении текста
@Composable
fun GoodParent() {
    Column {
        TextFieldWithState()
        TextFieldWithState()
        StaticContent() // Не вынуждена рекомпозироваться из-за текстовых полей, если её параметры стабильны
    }
}
```

### 6. `key()` В Списках

```kotlin
@Composable
fun UserList(users: List<UserImmutableFriends>) {
    LazyColumn {
        items(
            items = users,
            key = { user -> user.name } // Пример стабильного ключа, в реальном коде лучше использовать уникальный id
        ) { user ->
            UserRow(user)
        }
    }
}
```

### 7. Минимизация Чтений Состояния

```kotlin
// ❌ Читает состояние в общем scope, из-за чего весь Column участвует в рекомпозиции при изменении count
@Composable
fun BadCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        Text("Count: ${count.value}")
        Button(onClick = { count.value++ }) { Text("Increment") }
    }
}

// ✅ Локализуем чтения: только дочерние, читающие count.value, рекомпозируются
@Composable
fun CountDisplay(count: Int) {
    Text("Count: $count")
}

@Composable
fun GoodCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        CountDisplay(count.value) // Рекомпозируется при изменении count
        Button(onClick = { count.value++ }) { Text("Increment") }
    }
}
```

### 8. Immutable Коллекции

```kotlin
// Зависимость: kotlinx-collections-immutable

// ❌ Mutable список может меняться по месту, что осложняет отслеживание изменений
@Composable
fun MutableListExample(items: MutableList<String>) {
    LazyColumn {
        items(items) { Text(it) }
    }
}

// ✅ Immutable список / persistent коллекция — изменения отражаются через новые экземпляры,
//    что упрощает определение изменений и пропуск рекомпозиций
@Composable
fun ImmutableListExample(items: ImmutableList<String>) {
    LazyColumn {
        items(items.size) { Text(items[it]) }
    }
}
```

### Чеклист Производительности

1. ✅ Использовать `remember` для дорогих вычислений
2. ✅ Использовать `derivedStateOf` для производного состояния
3. ✅ Использовать стабильные `key()` в списках
4. ✅ Проектировать модели так, чтобы они были стабильными; при необходимости помечать `@Immutable` / `@Stable`
5. ✅ Использовать неизменяемые / persistent коллекции вместо мутабельных
6. ✅ Размещать состояние рядом с местом использования (не поднимать чрезмерно высоко)
7. ✅ Избегать лишнего создания новых лямбд и объектов в параметрах
8. ✅ Минимизировать и локализовать чтения состояния внутри иерархии

### Отладка Рекомпозиций

```kotlin
// Счётчик показывает, сколько раз был успешно применён этот composable.
// SideEffect выполняется после каждого успешного применения RecompositionCounter.
@Composable
fun RecompositionCounter() {
    val count = remember { mutableStateOf(0) }

    SideEffect {
        count.value++
    }

    Text("Recompositions: ${count.value}")
}
```

## Answer (EN)

Reducing recompositions improves [[c-compose-recomposition]] performance. Key techniques: `remember`, `derivedStateOf`, stable and properly annotated data models, immutable collections, proper state placement, and using `key()`.

### 1. Remember For Expensive Calculations

```kotlin
@Composable
fun ExpensiveCalculation(items: List<Item>) {
    // ❌ Recalculates on every recomposition
    val result = items.map { it.value * 2 }.sum()

    // ✅ Only recalculates when items (or their references) change
    val result = remember(items) {
        items.map { it.value * 2 }.sum()
    }

    Text("Result: $result")
}
```

### 2. derivedStateOf For Derived State

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    val items = remember { List(1000) { "Item $it" } }

    // ❌ Filters on every recomposition of this scope
    val filteredItems = items.filter { it.contains(query, ignoreCase = true) }

    // ✅ Only filters when query / items change
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.contains(query, ignoreCase = true) }
        }
    }

    LazyColumn {
        items(filteredItems) { Text(it) }
    }
}
```

### 3. Stable Data Models and Annotations

(Alternative variants for illustration; they are not meant to compile together.)

```kotlin
// ❌ Potentially unstable due to mutable collection:
//    friends can change in-place without a new instance.
data class UserMutableFriends(
    val name: String,
    val friends: MutableList<String>
)

// ✅ Prefer immutable properties + @Immutable to hint stability
@Immutable
data class UserImmutableFriends(
    val name: String,
    val friends: List<String>
)

// ✅ Variant using persistent collections annotated as @Stable
@Stable
data class UserPersistentFriends(
    val name: String,
    val friends: PersistentList<String>
)
```

Annotations and immutable collections do not magically reduce recompositions; they help the compiler infer stability correctly and enable more recomposition skipping.

### 4. Stable Lambda References

```kotlin
// ✅ Typical usage: lambda captures a stable viewModel.
//    Compose considers this a stable parameter; no extra remember is needed.
@Composable
fun ParentScreen(viewModel: ViewModel) {
    ChildScreen(onClick = { viewModel.handleClick() })
}

// ✅ Explicit stabilization is useful when lambda depends on changing inputs
//    and you want finer control over when it is recreated.
@Composable
fun ParentScreenControlled(viewModel: ViewModel, enabled: Boolean) {
    val onClick = remember(enabled) {
        { if (enabled) viewModel.handleClick() }
    }
    ChildScreen(onClick = onClick)
}
```

Key idea: avoid unnecessarily creating new functional objects in parameters when it prevents children from being skippable.

### 5. Proper State Placement

```kotlin
// ❌ State is too high: any text change forces recomposition of the whole BadParent content
@Composable
fun BadParent() {
    var text1 by remember { mutableStateOf("") }
    var text2 by remember { mutableStateOf("") }

    Column {
        TextField(text1, { text1 = it })
        TextField(text2, { text2 = it })
        StaticContent() // Participates in recomposition of this scope
    }
}

// ✅ State is closer to where it is used; StaticContent does not depend on it
//    and thus is not forced to recompose due to text changes, assuming stable inputs
@Composable
fun GoodParent() {
    Column {
        TextFieldWithState()
        TextFieldWithState()
        StaticContent() // Not forced to recompose due to text fields if its parameters are stable
    }
}
```

### 6. `key()` In Lists

```kotlin
@Composable
fun UserList(users: List<UserImmutableFriends>) {
    LazyColumn {
        items(
            items = users,
            key = { user -> user.name } // Example of a stable key; in real apps prefer a unique id
        ) { user ->
            UserRow(user)
        }
    }
}
```

### 7. Minimize State Reads

```kotlin
// ❌ Reads state in the parent scope, making the whole Column participate in recomposition
@Composable
fun BadCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        Text("Count: ${count.value}")
        Button(onClick = { count.value++ }) { Text("Increment") }
    }
}

// ✅ Localize reads: only children that read count.value recompose
@Composable
fun CountDisplay(count: Int) {
    Text("Count: $count")
}

@Composable
fun GoodCounter() {
    val count = remember { mutableStateOf(0) }

    Column {
        CountDisplay(count.value) // This recomposes when count changes
        Button(onClick = { count.value++ }) { Text("Increment") }
    }
}
```

### 8. Immutable Collections

```kotlin
// Dependency: kotlinx-collections-immutable

// ❌ Mutable list can change in place, making it harder to track modifications
@Composable
fun MutableListExample(items: MutableList<String>) {
    LazyColumn {
        items(items) { Text(it) }
    }
}

// ✅ Immutable / persistent list: modifications are represented as new instances,
//    which simplifies change detection and can improve skipping behavior
@Composable
fun ImmutableListExample(items: ImmutableList<String>) {
    LazyColumn {
        items(items.size) { Text(items[it]) }
    }
}
```

### Performance Checklist

1. ✅ Use `remember` for expensive calculations
2. ✅ Use `derivedStateOf` for derived state
3. ✅ Use stable `key()` in lists
4. ✅ Design models to be stable; annotate with `@Immutable` / `@Stable` when appropriate
5. ✅ Prefer immutable / persistent collections over mutable ones
6. ✅ Place state close to where it is used (avoid hoisting too high)
7. ✅ Avoid unnecessary creation of new lambdas and objects in parameters
8. ✅ Minimize and localize state reads within the hierarchy

### Debugging Recompositions

```kotlin
// Counts how many times this composable has been successfully applied.
// SideEffect runs after every successful recomposition of RecompositionCounter.
@Composable
fun RecompositionCounter() {
    val count = remember { mutableStateOf(0) }

    SideEffect {
        count.value++
    }

    Text("Recompositions: ${count.value}")
}
```

---

## Дополнительные вопросы (RU)

- Как Compose определяет, когда можно пропустить рекомпозицию?
- В чем разница между аннотациями `@Stable` и `@Immutable`?
- Как можно измерять количество рекомпозиций в продакшене?
- Когда следует использовать `key()` по сравнению со стабильными параметрами?
- Как persistent-коллекции улучшают производительность Compose?

## Follow-ups

- How does Compose determine when to skip recomposition?
- What is the difference between `@Stable` and `@Immutable` annotations?
- How can you measure recomposition count in production?
- When should you use `key()` vs stable parameters?
- How do persistent collections improve Compose performance?

## Ссылки (RU)

- [[q-compose-stability-skippability--android--hard]] - Вывод стабильности и пропуск рекомпозиций в Compose
- [[q-compose-performance-optimization--android--hard]] - Комплексная оптимизация производительности
- [[q-recomposition-compose--android--medium]] - Основы рекомпозиции
- [[q-compose-remember-derived-state--android--medium]] - Паттерны управления состоянием
- [Jetpack Compose Performance](https://developer.android.com/jetpack/compose/performance)
- [Compose Stability](https://developer.android.com/jetpack/compose/performance/stability)

## References

- [[q-compose-stability-skippability--android--hard]] - Compose stability inference and skippability
- [[q-compose-performance-optimization--android--hard]] - Comprehensive performance optimization
- [[q-recomposition-compose--android--medium]] - Recomposition basics
- [[q-compose-remember-derived-state--android--medium]] - State management patterns
- [Jetpack Compose Performance](https://developer.android.com/jetpack/compose/performance)
- [Compose Stability](https://developer.android.com/jetpack/compose/performance/stability)

## Связанные вопросы (RU)

### Предпосылки (проще)

- [[q-recomposition-compose--android--medium]] - Понимание основ рекомпозиции
- [[q-compose-remember-derived-state--android--medium]] - Базовые подходы к управлению состоянием

### Связанные (тот же уровень)

- [[q-compose-performance-optimization--android--hard]] - Стратегии оптимизации производительности
- [[q-compose-stability-skippability--android--hard]] - Детали стабильности и skippability
- [[q-compose-slot-table-recomposition--android--hard]] - Внутренние механизмы рекомпозиции

### Продвинутые

- [[q-compose-compiler-plugin--android--hard]] - Оптимизации компилятором
- [[q-derived-state-snapshot-system--android--hard]] - Продвинутое управление состоянием

## Related Questions

### Prerequisites (Easier)
- [[q-recomposition-compose--android--medium]] - Understanding recomposition basics
- [[q-compose-remember-derived-state--android--medium]] - State management fundamentals

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]] - Comprehensive performance strategies
- [[q-compose-stability-skippability--android--hard]] - Stability and skippability details
- [[q-compose-slot-table-recomposition--android--hard]] - Internal recomposition mechanics

### Advanced
- [[q-compose-compiler-plugin--android--hard]] - Compiler optimizations
- [[q-derived-state-snapshot-system--android--hard]] - Advanced state management
