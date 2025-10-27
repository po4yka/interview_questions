---
id: 20251012-122711
title: Compose Stability Skippability / Стабильность и пропускаемость Compose
aliases: [Compose Stability Skippability, Стабильность и пропускаемость Compose]
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
  - q-compose-performance-optimization--android--hard
created: 2025-10-15
updated: 2025-01-27
tags: [android/performance-memory, android/ui-compose, difficulty/hard]
sources: [https://developer.android.com/jetpack/compose/performance]
---
# Вопрос (RU)
> Как стабильность типов влияет на пропускаемость перекомпозиции в Jetpack Compose?

# Question (EN)
> How does type stability affect recomposition skippability in Jetpack Compose?

---

## Ответ (RU)

**Пропускаемость (skippability)** — это механизм оптимизации в Compose, позволяющий компилятору пропустить рекомпозицию функции, если её параметры не изменились.

### Условия пропускаемости

Composable-функция пропускаема, если:

1. **Все параметры стабильны** — каждый параметр имеет стабильный тип
2. **Функция возвращает Unit** или нерестартуема
3. **Не помечена @NonSkippableComposable**

```kotlin
// ✅ Пропускаема — все параметры примитивы (стабильны)
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// ❌ НЕ пропускаема — нестабильный параметр
data class User(var name: String) // var делает класс нестабильным

@Composable
fun UserProfile(user: User) { // Будет перекомпоноваться всегда
    Text(user.name)
}

// ✅ Пропускаема — иммутабельный data class
data class ImmutableUser(val name: String)

@Composable
fun ImmutableUserProfile(user: ImmutableUser) {
    Text(user.name)
}
```

### Критерии стабильности типа

Тип **стабилен**, если Compose-компилятор может гарантировать:

1. **equals() возвращает одинаковый результат для тех же экземпляров**
2. **При изменении публичного свойства Composition получит уведомление**
3. **Все публичные свойства также стабильны**

**Автоматически стабильные:**

- Примитивы (`Int`, `Long`, `Float`, `Boolean`)
- `String`
- Лямбды (function types)
- Immutable-коллекции из `kotlinx.collections.immutable`

**Нестабильные:**

- Классы с `var`-свойствами
- Mutable-коллекции (`MutableList`, `MutableMap`)
- Интерфейсы (компилятор не может доказать стабильность)
- Абстрактные классы

```kotlin
// ✅ STABLE
data class StableUser(val id: Int, val name: String)

// ❌ UNSTABLE — var-свойство
data class UnstableUser(val id: Int, var name: String)

// ❌ UNSTABLE — мутабельная коллекция
data class UnstableList(val users: MutableList<String>)

// ✅ STABLE — иммутабельная коллекция
data class StableList(val users: List<String>)
```

### Аннотация @Stable

**@Stable** — это **обещание** компилятору, что тип соблюдает контракт стабильности, даже если это невозможно доказать автоматически.

**Используйте @Stable:**

- Для интерфейсов/абстрактных классов, которые стабильны по контракту
- Для классов с приватным мутабельным состоянием, никогда не выходящим наружу
- Для observable-паттернов (StateFlow, LiveData), уведомляющих Compose

```kotlin
// ✅ Указываем компилятору, что интерфейс стабилен
@Stable
interface StableUserData {
    val name: String
    val email: String
}

@Composable
fun UserDisplay(user: StableUserData) { // Теперь пропускаема!
    Column {
        Text(user.name)
        Text(user.email)
    }
}

// ❌ ОПАСНО — нарушение контракта
@Stable
data class LyingUser(var name: String) // Заявили стабильность, но есть var

@Composable
fun BuggyDisplay(user: LyingUser) {
    Text(user.name) // НЕ обновится при изменении name!
}
```

### Отладка стабильности

Включите Compose Compiler Metrics:

```kotlin
// build.gradle.kts
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
                project.buildDir.absolutePath + "/compose_metrics"
        )
    }
}
```

Отчёт покажет:

```text
restartable skippable scheme("[...]") fun Counter(
  stable count: Int
  stable onIncrement: Function0<Unit>
)

restartable scheme("[...]") fun UserProfile(
  unstable user: User
)
```

### Практические примеры

**Проблема: ViewModel нестабилен**

```kotlin
// ❌ ViewModel не гарантирует стабильность
class UserViewModel : ViewModel() {
    val userState = mutableStateOf(User())
}

@Composable
fun UserScreen(viewModel: UserViewModel) { // НЕ пропускаема
    val user by viewModel.userState
    Text(user.name)
}

// ✅ Решение: передавайте состояние, а не ViewModel
@Composable
fun UserScreen(userState: State<User>) { // Стабильный параметр
    val user by userState
    Text(user.name)
}
```

**Проблема: List вызывает лишние рекомпозиции**

```kotlin
// ❌ MutableList нестабилен
@Composable
fun UserList(users: MutableList<User>) { // НЕ пропускаема
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}

// ✅ Используйте ImmutableList
import kotlinx.collections.immutable.ImmutableList
import kotlinx.collections.immutable.persistentListOf

@Composable
fun UserList(users: ImmutableList<User>) { // Пропускаема!
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}
```

### Влияние на производительность

**Без пропуска:**

- 10 000 composable на экране
- Изменение состояния затрагивает 1 элемент
- Результат: все 10 000 перекомпонуются
- Время: ~100 мс

**С правильным пропуском:**

- 10 000 composable на экране
- Изменение состояния затрагивает 1 элемент
- Результат: только 1 перекомпонуется
- Время: ~0.1 мс

**Прирост в 1000 раз!**

## Answer (EN)

**Skippability** is Compose's optimization mechanism that allows the compiler to skip recomposing a composable when its inputs haven't changed.

### Skippability Requirements

A composable is **skippable** if:

1. **All parameters are stable** — every parameter must be of a stable type
2. **Returns Unit** or is non-restartable
3. **Not marked with @NonSkippableComposable**

```kotlin
// ✅ Skippable — all parameters are primitives (stable)
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// ❌ NOT skippable — unstable parameter
data class User(var name: String) // var makes it unstable

@Composable
fun UserProfile(user: User) { // Will always recompose
    Text(user.name)
}

// ✅ Skippable — immutable data class
data class ImmutableUser(val name: String)

@Composable
fun ImmutableUserProfile(user: ImmutableUser) {
    Text(user.name)
}
```

### Stability Criteria

A type is **stable** if the Compose compiler can guarantee:

1. **equals() returns the same result for the same instances**
2. **Public property changes notify Composition**
3. **All public properties are also stable types**

**Automatically stable:**

- Primitives (`Int`, `Long`, `Float`, `Boolean`)
- `String`
- Lambdas (function types)
- Immutable collections from `kotlinx.collections.immutable`

**Unstable:**

- Classes with `var` properties
- Mutable collections (`MutableList`, `MutableMap`)
- Interfaces (compiler can't prove stability)
- Abstract classes

```kotlin
// ✅ STABLE
data class StableUser(val id: Int, val name: String)

// ❌ UNSTABLE — var property
data class UnstableUser(val id: Int, var name: String)

// ❌ UNSTABLE — mutable collection
data class UnstableList(val users: MutableList<String>)

// ✅ STABLE — immutable collection
data class StableList(val users: List<String>)
```

### The @Stable Annotation

**@Stable** is a **promise** to the Compose compiler that a type follows the stability contract, even if the compiler can't prove it automatically.

**Use @Stable:**

- For interfaces/abstract classes that are stable by contract
- For classes with private mutable state that's never exposed
- For observable patterns (StateFlow, LiveData) that notify Compose

```kotlin
// ✅ Tell compiler this interface is stable
@Stable
interface StableUserData {
    val name: String
    val email: String
}

@Composable
fun UserDisplay(user: StableUserData) { // Now skippable!
    Column {
        Text(user.name)
        Text(user.email)
    }
}

// ❌ DANGEROUS — contract violation
@Stable
data class LyingUser(var name: String) // Claimed stable but has var

@Composable
fun BuggyDisplay(user: LyingUser) {
    Text(user.name) // Won't update when name changes!
}
```

### Debugging Stability

Enable Compose Compiler Metrics:

```kotlin
// build.gradle.kts
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
                project.buildDir.absolutePath + "/compose_metrics"
        )
    }
}
```

Report shows:

```text
restartable skippable scheme("[...]") fun Counter(
  stable count: Int
  stable onIncrement: Function0<Unit>
)

restartable scheme("[...]") fun UserProfile(
  unstable user: User
)
```

### Practical Examples

**Problem: ViewModel is unstable**

```kotlin
// ❌ ViewModel doesn't guarantee stability
class UserViewModel : ViewModel() {
    val userState = mutableStateOf(User())
}

@Composable
fun UserScreen(viewModel: UserViewModel) { // NOT skippable
    val user by viewModel.userState
    Text(user.name)
}

// ✅ Solution: pass state, not ViewModel
@Composable
fun UserScreen(userState: State<User>) { // Stable parameter
    val user by userState
    Text(user.name)
}
```

**Problem: List causes unnecessary recompositions**

```kotlin
// ❌ MutableList is unstable
@Composable
fun UserList(users: MutableList<User>) { // NOT skippable
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}

// ✅ Use ImmutableList
import kotlinx.collections.immutable.ImmutableList
import kotlinx.collections.immutable.persistentListOf

@Composable
fun UserList(users: ImmutableList<User>) { // Skippable!
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}
```

### Performance Impact

**Without skipping:**

- 10,000 composables on screen
- State change affects 1 element
- Result: all 10,000 recompose
- Time: ~100 ms

**With proper skipping:**

- 10,000 composables on screen
- State change affects 1 element
- Result: only 1 recomposes
- Time: ~0.1 ms

**1000x improvement!**

---

## Follow-ups

- What are the trade-offs between @Stable and @Immutable annotations in Compose?
- How does Strong Skipping Mode affect lambda capture and recomposition behavior?
- What metrics from the Compose Compiler can help identify unexpected recompositions?
- How do derived state calculations interact with stability inference?

## References

- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)

- Description: Basic understanding of Compose state management and recomposition lifecycle

### Related (Same Level)

- [[q-compose-performance-optimization--android--hard]]
- Description: Advanced Compose performance profiling and optimization techniques

### Advanced (Harder)

- Description: Compose Compiler internals, IR transformations, and custom stability annotations
