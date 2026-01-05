---
id: ivc-20251030-140000
title: Compose Recomposition / Рекомпозиция в Compose
aliases: [Compose Recomposition, Recomposition, Перерисовка Compose, Рекомпозиция]
kind: concept
summary: Recomposition process in Jetpack Compose - how UI updates in response to state changes
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, jetpack-compose, performance, recomposition, ui]
---

# Summary (EN)

**Recomposition** is the process in Jetpack Compose where composable functions are re-executed to update the UI when state changes. Unlike traditional view systems with explicit update methods, Compose automatically observes state reads and re-invokes only the affected composables.

**Key characteristics**:
- **Triggered by state changes**: Any read of `State<T>`, `MutableState<T>`, or flow collections triggers observation
- **Smart and scoped**: Compose skips composables whose inputs haven't changed (skip optimization)
- **Can happen anytime**: Recomposition may occur on different threads, out of order, or be cancelled mid-execution
- **Should be idempotent**: Composables must produce the same result for the same inputs

# Сводка (RU)

**Рекомпозиция** — это процесс в Jetpack Compose, при котором composable-функции выполняются повторно для обновления UI при изменении состояния. В отличие от традиционных систем представлений с явными методами обновления, Compose автоматически отслеживает чтение состояния и повторно вызывает только затронутые composable-функции.

**Ключевые характеристики**:
- **Триггер — изменения состояния**: Любое чтение `State<T>`, `MutableState<T>` или сборка flow запускает наблюдение
- **Умная и ограниченная по области**: Compose пропускает composable-функции, входные данные которых не изменились (skip-оптимизация)
- **Может происходить в любое время**: Рекомпозиция может выполняться в разных потоках, не по порядку или отменяться в процессе
- **Должна быть идемпотентной**: Composable-функции должны выдавать одинаковый результат при одинаковых входных данных

---

## Core Concept / Основная Концепция

### Recomposition Triggers (EN)

Recomposition occurs when:
1. **State read during composition changes**: `state.value`, `derivedStateOf`, `remember`
2. **Observable types update**: `Flow.collectAsState()`, `LiveData.observeAsState()`
3. **Parent recomposes**: Child may recompose if not skippable

**Scope of recomposition**:
- Only composables that read the changed state recompose
- Compose uses positional memoization to track which composables read which state
- Siblings and unrelated subtrees remain unchanged

### Триггеры Рекомпозиции (RU)

Рекомпозиция происходит когда:
1. **Изменяется состояние, прочитанное при композиции**: `state.value`, `derivedStateOf`, `remember`
2. **Обновляются observable-типы**: `Flow.collectAsState()`, `LiveData.observeAsState()`
3. **Родительский элемент перекомпонуется**: Дочерний может рекомпоноваться, если не пропускается

**Область рекомпозиции**:
- Рекомпонуются только composable-функции, которые читают измененное состояние
- Compose использует позиционную мемоизацию для отслеживания того, какие composable-функции читают какое состояние
- Соседние и несвязанные поддеревья остаются без изменений

---

## Smart Recomposition / Умная Рекомпозиция

### Skip Optimization (EN)

Compose can **skip** recomposing a function if:
- All parameters are **stable** (immutable or annotated with `@Stable`)
- Parameters haven't changed since last composition (equality check)

```kotlin
// Skippable: All parameters are primitives (stable)
@Composable
fun Counter(count: Int) {
    Text("Count: $count")
}

// NOT skippable: Unstable lambda parameter
@Composable
fun Item(onClick: () -> Unit) {  // Lambda not stable by default
    Button(onClick) { Text("Click") }
}

// Skippable: Stable lambda via remember
@Composable
fun ItemOptimized(onClick: () -> Unit) {
    val stableOnClick = remember { onClick }  // Stabilized
    Button(stableOnClick) { Text("Click") }
}
```

### Skip-оптимизация (RU)

Compose может **пропустить** рекомпозицию функции, если:
- Все параметры **стабильны** (неизменяемые или помечены `@Stable`)
- Параметры не изменились с последней композиции (проверка равенства)

```kotlin
// Пропускается: Все параметры — примитивы (стабильны)
@Composable
fun Counter(count: Int) {
    Text("Count: $count")
}

// НЕ пропускается: Нестабильный лямбда-параметр
@Composable
fun Item(onClick: () -> Unit) {  // Лямбда не стабильна по умолчанию
    Button(onClick) { Text("Click") }
}

// Пропускается: Стабильная лямбда через remember
@Composable
fun ItemOptimized(onClick: () -> Unit) {
    val stableOnClick = remember { onClick }  // Стабилизирована
    Button(stableOnClick) { Text("Click") }
}
```

---

## Performance Best Practices / Лучшие Практики Производительности

### 1. Use derivedStateOf for Computed Values (EN)

Avoid triggering recomposition for intermediate calculations:

```kotlin
// BAD: Recomposes on every scroll position change
@Composable
fun List(items: List<Item>, scrollPosition: Int) {
    val isAtTop = scrollPosition < 100  // Reads scrollPosition
    if (isAtTop) ShowScrollToTopButton()
}

// GOOD: Only recomposes when isAtTop changes (0→1 or 1→0)
@Composable
fun ListOptimized(items: List<Item>, scrollPosition: State<Int>) {
    val isAtTop by remember {
        derivedStateOf { scrollPosition.value < 100 }
    }
    if (isAtTop) ShowScrollToTopButton()
}
```

### 1. Использование derivedStateOf Для Вычисляемых Значений (RU)

Избегайте запуска рекомпозиции для промежуточных вычислений:

```kotlin
// ПЛОХО: Рекомпонуется при каждом изменении позиции прокрутки
@Composable
fun List(items: List<Item>, scrollPosition: Int) {
    val isAtTop = scrollPosition < 100  // Читает scrollPosition
    if (isAtTop) ShowScrollToTopButton()
}

// ХОРОШО: Рекомпонуется только при изменении isAtTop (0→1 или 1→0)
@Composable
fun ListOptimized(items: List<Item>, scrollPosition: State<Int>) {
    val isAtTop by remember {
        derivedStateOf { scrollPosition.value < 100 }
    }
    if (isAtTop) ShowScrollToTopButton()
}
```

### 2. Mark Custom Classes as Stable (EN)

```kotlin
// NOT stable: Mutable var
data class User(var name: String, var age: Int)

// Stable: Immutable properties, marked with @Stable
@Stable
data class User(val name: String, val age: Int)

// Stable: Observable state wrapped
@Stable
class UserViewModel(private val _user: MutableState<User>) {
    val user: State<User> = _user
}
```

### 2. Пометка Пользовательских Классов Как Stable (RU)

```kotlin
// НЕ стабильно: Изменяемый var
data class User(var name: String, var age: Int)

// Стабильно: Неизменяемые свойства, помечено @Stable
@Stable
data class User(val name: String, val age: Int)

// Стабильно: Observable-состояние обернуто
@Stable
class UserViewModel(private val _user: MutableState<User>) {
    val user: State<User> = _user
}
```

### 3. Avoid Reading State in Composition Unnecessarily (EN)

```kotlin
// BAD: Reads state on every composition
@Composable
fun Profile(user: State<User>) {
    Text("Name: ${user.value.name}")  // Subscribes to all user changes
    Button(onClick = { /* update age */ })
}

// GOOD: Only subscribe to name changes
@Composable
fun ProfileOptimized(user: State<User>) {
    val name by remember { derivedStateOf { user.value.name } }
    Text("Name: $name")  // Only recomposes when name changes
    Button(onClick = { /* update age */ })
}
```

### 3. Избегание Ненужного Чтения Состояния При Композиции (RU)

```kotlin
// ПЛОХО: Читает состояние при каждой композиции
@Composable
fun Profile(user: State<User>) {
    Text("Name: ${user.value.name}")  // Подписывается на все изменения user
    Button(onClick = { /* обновить возраст */ })
}

// ХОРОШО: Подписывается только на изменения имени
@Composable
fun ProfileOptimized(user: State<User>) {
    val name by remember { derivedStateOf { user.value.name } }
    Text("Name: $name")  // Рекомпонуется только при изменении name
    Button(onClick = { /* обновить возраст */ })
}
```

---

## Use Cases / Trade-offs

**When recomposition is efficient**:
- Small, focused composables with minimal state reads
- Stable, immutable data classes
- Proper use of `remember`, `derivedStateOf`, and `key()`

**When recomposition becomes expensive**:
- Large composable trees recomposing unnecessarily
- Unstable lambda parameters causing skip optimization failures
- Reading high-frequency state (scroll position, animation progress) without `derivedStateOf`

**Trade-offs**:
- **Over-optimization**: Premature use of `@Stable` or excessive `remember` can reduce code readability
- **Under-optimization**: Missing skip optimization can cause performance issues in large lists or frequent updates
- **Balance**: Measure with Compose Layout Inspector and optimize hot paths only

---

## References

- [Jetpack Compose Performance - Recomposition](https://developer.android.com/jetpack/compose/performance/recomposition)
- [Understanding Compose - Recomposition](https://developer.android.com/jetpack/compose/mental-model#recomposition)
- [Compose Compiler Metrics](https://github.com/androidx/androidx/blob/androidx-main/compose/compiler/design/compiler-metrics.md)
- [derivedStateOf Documentation](https://developer.android.com/reference/kotlin/androidx/compose/runtime/package-summary#derivedStateOf(kotlin.Function0))
- [Stability in Compose](https://developer.android.com/jetpack/compose/performance/stability)
