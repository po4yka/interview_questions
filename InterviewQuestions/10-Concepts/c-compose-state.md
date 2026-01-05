---
id: ivc-20251030-140000
title: Compose State / Состояние в Compose
aliases: [Compose State, State Management Compose, Состояние Compose, Управление состоянием Compose]
kind: concept
summary: State management in Jetpack Compose using mutableStateOf, derivedStateOf, and state hoisting patterns
links: []
related: [c-jetpack-compose, c-compose-recomposition, c-viewmodel, c-state-flow, c-unidirectional-data-flow]
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, jetpack-compose, state-management, ui]
---

# Summary (EN)

**State** in Jetpack Compose represents data that, when changed, triggers UI recomposition. Compose uses a declarative model where UI is a function of state. State objects are typically created using `mutableStateOf()` and persisted across recompositions with `remember {}`. Immutability is critical: state changes must create new objects rather than mutating existing ones to ensure Compose detects changes and recomposes correctly.

## Core Concepts

**State APIs**:
- `mutableStateOf(initialValue)`: Creates observable state that triggers recomposition when changed
- `remember { }`: Caches values across recompositions (survives recomposition, not configuration changes)
- `rememberSaveable { }`: Persists state across configuration changes using Bundle
- `derivedStateOf { }`: Computes state from other state, only recomposes when result changes

**State Hoisting**: Moving state up to a composable's caller to make the composable stateless and reusable. The pattern separates state ownership (parent) from state usage (child).

## Best Practices

1. **Hoist state as high as necessary**, but no higher - keep state close to where it's used
2. **Use `derivedStateOf` for computed state** to avoid unnecessary recompositions when inputs change but output doesn't
3. **Prefer immutable data structures** - use `copy()` for data classes, create new collections
4. **Keep composables stateless when possible** - pass state and callbacks as parameters

## Code Examples

### Basic State Usage

```kotlin
// ✅ CORRECT: Remember state to survive recomposition
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Clicked $count times")
    }
}

// ❌ WRONG: State recreated on every recomposition
@Composable
fun CounterBroken() {
    var count by mutableStateOf(0) // Lost on recomposition!
    Button(onClick = { count++ }) {
        Text("Clicked $count times")
    }
}
```

### State Hoisting Pattern

```kotlin
// ✅ CORRECT: Stateless, reusable composable
@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit
) {
    TextField(value = query, onValueChange = onQueryChange)
}

// Parent owns state
@Composable
fun SearchScreen() {
    var searchQuery by remember { mutableStateOf("") }
    SearchBar(query = searchQuery, onQueryChange = { searchQuery = it })
    SearchResults(query = searchQuery)
}
```

### Derived State Optimization

```kotlin
// ✅ CORRECT: Only recomposes when hasErrors changes
@Composable
fun FormValidator(fields: List<Field>) {
    val hasErrors by remember {
        derivedStateOf { fields.any { !it.isValid } }
    }
    if (hasErrors) {
        Text("Please fix errors", color = Color.Red)
    }
}

// ❌ WRONG: Recomposes whenever any field changes
@Composable
fun FormValidatorInefficient(fields: List<Field>) {
    val hasErrors = fields.any { !it.isValid }
    if (hasErrors) {
        Text("Please fix errors", color = Color.Red)
    }
}
```

## Common Pitfalls

- Mutating state objects directly (`list.add()` instead of `list = list + item`)
- Forgetting `remember {}` - state resets on recomposition
- Over-hoisting state - making state management unnecessarily complex
- Not using `derivedStateOf` for expensive computations

---

# Сводка (RU)

**Состояние** в Jetpack Compose представляет данные, изменение которых вызывает перекомпоновку (recomposition) UI. Compose использует декларативную модель, где UI является функцией от состояния. Объекты состояния обычно создаются через `mutableStateOf()` и сохраняются между перекомпоновками с помощью `remember {}`. Неизменяемость критична: изменения состояния должны создавать новые объекты, а не мутировать существующие, чтобы Compose обнаруживал изменения и корректно перекомпоновывал UI.

## Основные Концепции

**API для работы с состоянием**:
- `mutableStateOf(initialValue)`: Создает наблюдаемое состояние, вызывающее recomposition при изменении
- `remember { }`: Кэширует значения между recomposition (сохраняется при recomposition, но не при configuration changes)
- `rememberSaveable { }`: Сохраняет состояние между configuration changes через Bundle
- `derivedStateOf { }`: Вычисляет состояние из другого состояния, вызывает recomposition только при изменении результата

**Поднятие состояния (State Hoisting)**: Перемещение состояния вверх к вызывающей функции, чтобы сделать composable функцию stateless и переиспользуемой. Паттерн разделяет владение состоянием (родитель) и использование состояния (потомок).

## Лучшие Практики

1. **Поднимайте состояние настолько высоко, насколько необходимо**, но не выше - держите состояние близко к месту использования
2. **Используйте `derivedStateOf` для вычисляемого состояния**, чтобы избежать лишних recomposition когда входные данные меняются, но результат остается прежним
3. **Предпочитайте неизменяемые структуры данных** - используйте `copy()` для data классов, создавайте новые коллекции
4. **Делайте composable функции stateless когда возможно** - передавайте состояние и коллбэки как параметры

## Примеры Кода

См. примеры выше (Code Examples) - код одинаков для обоих языков.

## Типичные Ошибки

- Прямая мутация объектов состояния (`list.add()` вместо `list = list + item`)
- Забытый `remember {}` - состояние сбрасывается при recomposition
- Излишнее поднятие состояния - делает управление состоянием неоправданно сложным
- Неиспользование `derivedStateOf` для дорогих вычислений

---

## Use Cases / Trade-offs

**When to use mutableStateOf**:
- Simple UI state (text input, toggle, counter)
- State scoped to single composable
- Direct user interactions

**When to use derivedStateOf**:
- Computed/calculated state based on other state
- Filtering, sorting, or aggregating collections
- Avoiding recomposition when inputs change but output stays same

**When to hoist state**:
- Need to share state between multiple composables
- Parent needs to control child behavior
- Testing composable in isolation
- Making composable reusable

**Trade-offs**:
- More state hoisting = more boilerplate but better testability and reusability
- `remember` is fast but doesn't survive process death
- `rememberSaveable` survives config changes but requires Bundle-compatible types

## References

- [Official Compose State Documentation](https://developer.android.com/jetpack/compose/state)
- [State and Jetpack Compose](https://developer.android.com/jetpack/compose/state-hoisting)
- [Thinking in Compose](https://developer.android.com/jetpack/compose/mental-model)
- [Compose Performance: derivedStateOf](https://developer.android.com/jetpack/compose/performance/stability#derivedstateof)
