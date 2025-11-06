---
id: ivc-20251030-150000
title: Recomposition / Рекомпозиция
aliases: [Recomposition, Рекомпозиция]
kind: concept
summary: Core Compose mechanism for updating UI when state changes
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, jetpack-compose, recomposition, ui]
---

# Summary (EN)

**Recomposition** is the fundamental mechanism in Jetpack Compose for updating the UI in response to state changes. Instead of manually updating views, Compose automatically re-executes composable functions when their observed state changes. This declarative approach makes UI updates predictable and efficient through smart scoping and skip optimizations.

**Core principle**: When state changes, only the composables that read that state are re-executed, minimizing unnecessary work.

# Сводка (RU)

**Рекомпозиция** — это фундаментальный механизм в Jetpack Compose для обновления UI в ответ на изменения состояния. Вместо ручного обновления представлений, Compose автоматически повторно выполняет composable-функции при изменении отслеживаемого ими состояния. Этот декларативный подход делает обновления UI предсказуемыми и эффективными благодаря умной области действия и skip-оптимизациям.

**Основной принцип**: При изменении состояния повторно выполняются только те composable-функции, которые читают это состояние, минимизируя ненужную работу.

---

## Core Concept / Основная Концепция

### What Triggers Recomposition (EN)

1. **State changes**: Reading `State<T>` or `MutableState<T>` creates an observation
2. **Observable collections**: `Flow.collectAsState()`, `LiveData.observeAsState()`
3. **Remembered values**: Changes to `remember { }` dependencies

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    // Button recomposes when count changes
    Button(onClick = { count++ }) {
        Text("Count: $count")  // Reads state → subscribes to changes
    }
}
```

### Что Запускает Рекомпозицию (RU)

1. **Изменения состояния**: Чтение `State<T>` или `MutableState<T>` создает наблюдение
2. **Observable-коллекции**: `Flow.collectAsState()`, `LiveData.observeAsState()`
3. **Запомненные значения**: Изменения в зависимостях `remember { }`

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    // Button рекомпонуется при изменении count
    Button(onClick = { count++ }) {
        Text("Count: $count")  // Читает состояние → подписывается на изменения
    }
}
```

---

## Smart Recomposition / Умная Рекомпозиция

### Scoped Updates (EN)

Compose uses **positional memoization** to track which composables read which state. Only affected subtrees recompose.

```kotlin
@Composable
fun Screen() {
    var counter by remember { mutableStateOf(0) }
    var text by remember { mutableStateOf("") }

    Column {
        // Recomposes ONLY when counter changes
        Text("Counter: $counter")

        // Recomposes ONLY when text changes
        TextField(value = text, onValueChange = { text = it })

        // Recomposes when counter changes
        Button(onClick = { counter++ }) { Text("Increment") }
    }
}
```

### Ограниченные Обновления (RU)

Compose использует **позиционную мемоизацию** для отслеживания того, какие composable-функции читают какое состояние. Рекомпонуются только затронутые поддеревья.

```kotlin
@Composable
fun Screen() {
    var counter by remember { mutableStateOf(0) }
    var text by remember { mutableStateOf("") }

    Column {
        // Рекомпонуется ТОЛЬКО при изменении counter
        Text("Counter: $counter")

        // Рекомпонуется ТОЛЬКО при изменении text
        TextField(value = text, onValueChange = { text = it })

        // Рекомпонуется при изменении counter
        Button(onClick = { counter++ }) { Text("Increment") }
    }
}
```

---

## Optimization Strategies / Стратегии Оптимизации

### 1. Stable Parameters (EN)

Composables with **stable** parameters (primitives, immutable data classes) can be **skipped** if parameters haven't changed.

```kotlin
@Stable
data class User(val name: String, val age: Int)

@Composable
fun UserCard(user: User) {  // Skippable: User is @Stable
    Text("${user.name}, ${user.age}")
}
```

### 1. Стабильные Параметры (RU)

Composable-функции со **стабильными** параметрами (примитивы, неизменяемые data-классы) могут быть **пропущены**, если параметры не изменились.

```kotlin
@Stable
data class User(val name: String, val age: Int)

@Composable
fun UserCard(user: User) {  // Пропускается: User помечен @Stable
    Text("${user.name}, ${user.age}")
}
```

### 2. derivedStateOf for Computed Values (EN)

Reduces recomposition frequency by recomposing only when derived value changes.

```kotlin
@Composable
fun List(scrollPosition: State<Int>) {
    val showButton by remember {
        derivedStateOf { scrollPosition.value > 100 }  // Boolean changes rarely
    }
    if (showButton) FloatingActionButton()
}
```

### 2. derivedStateOf Для Вычисляемых Значений (RU)

Снижает частоту рекомпозиции, выполняя её только при изменении производного значения.

```kotlin
@Composable
fun List(scrollPosition: State<Int>) {
    val showButton by remember {
        derivedStateOf { scrollPosition.value > 100 }  // Boolean изменяется редко
    }
    if (showButton) FloatingActionButton()
}
```

---

## Use Cases / Trade-offs

**When recomposition shines**:
- Declarative UI: State automatically drives UI without manual updates
- Performance: Smart scoping minimizes work
- Predictability: Same inputs always produce same outputs

**Challenges**:
- **Side effects**: Must use `LaunchedEffect`, `DisposableEffect` for non-UI work
- **Unstable lambdas**: Can prevent skip optimization
- **High-frequency updates**: Require `derivedStateOf` or throttling

**Best practices**:
- Keep composables small and focused
- Use immutable data classes
- Avoid side effects in composition
- Measure performance before optimizing

---

## References

- [Jetpack Compose Mental Model](https://developer.android.com/jetpack/compose/mental-model#recomposition)
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)
- [State and Recomposition](https://developer.android.com/jetpack/compose/state#recomposition)
- [[c-compose-recomposition]] - Detailed implementation guide
