---
id: android-142
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
status: reviewed
moc: moc-android
related:
  - c-compose-recomposition
  - q-compose-performance-optimization--android--hard
created: 2025-10-15
updated: 2025-11-02
tags: [android/performance-memory, android/ui-compose, difficulty/hard]
sources: []
---

# Вопрос (RU)
> Как стабильность типов влияет на пропускаемость перекомпозиции в Jetpack Compose?

# Question (EN)
> How does type stability affect recomposition skippability in Jetpack Compose?

---

## Ответ (RU)

**Пропускаемость (skippability)** — механизм оптимизации, позволяющий компилятору пропустить рекомпозицию функции, если её параметры не изменились.

### Условия Пропускаемости

Composable-функция пропускаема, если:

1. **Все параметры стабильны** — каждый параметр имеет стабильный тип
2. **Функция возвращает `Unit`** или нерестартуема
3. **Не помечена `@NonSkippableComposable`**

```kotlin
// ✅ Пропускаема — примитивные параметры
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// ❌ НЕ пропускаема — нестабильный параметр
data class User(var name: String)

@Composable
fun UserProfile(user: User) { // Всегда перекомпонуется
    Text(user.name)
}
```

### Критерии Стабильности

Тип **стабилен**, если Compose-компилятор гарантирует:

1. **equals() возвращает одинаковый результат для тех же экземпляров**
2. **При изменении публичного свойства Composition получит уведомление**
3. **Все публичные свойства также стабильны**

**Автоматически стабильные:**
- Примитивы: `Int`, `Long`, `Float`, `Boolean`
- `String`, лямбды
- Immutable-коллекции из `kotlinx.collections.immutable`

**Нестабильные:**
- Классы с `var`-свойствами
- Mutable-коллекции: `MutableList`, `MutableMap`
- Интерфейсы (компилятор не может доказать стабильность)

```kotlin
// ✅ STABLE
data class StableUser(val id: Int, val name: String)

// ❌ UNSTABLE — var-свойство
data class UnstableUser(val id: Int, var name: String)

// ❌ UNSTABLE — мутабельная коллекция
data class UnstableList(val users: MutableList<String>)
```

### Аннотация `@Stable`

**`@Stable`** — обещание компилятору, что тип соблюдает контракт стабильности, даже если это невозможно доказать автоматически.

**Когда использовать:**
- Интерфейсы/абстрактные классы, стабильные по контракту
- Классы с приватным мутабельным состоянием
- Observable-паттерны (`StateFlow`, `LiveData`), уведомляющие Compose

```kotlin
// ✅ Указываем стабильность интерфейса
@Stable
interface UserData {
    val name: String
    val email: String
}

@Composable
fun UserDisplay(user: UserData) { // Теперь пропускаема
    Column {
        Text(user.name)
        Text(user.email)
    }
}

// ❌ ОПАСНО — нарушение контракта
@Stable
data class LyingUser(var name: String)

@Composable
fun BuggyDisplay(user: LyingUser) {
    Text(user.name) // НЕ обновится при изменении!
}
```

### Отладка Стабильности

Включите Compose Compiler Metrics в `build.gradle.kts`:
```kotlin
freeCompilerArgs += listOf(
    "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
    project.buildDir.absolutePath + "/compose_metrics"
)
```

Отчёт показывает стабильность параметров: `stable count: Int` vs `unstable user: User`.

### Практические Решения

**Проблема: `ViewModel` нестабилен**

```kotlin
// ❌ ViewModel не гарантирует стабильность
@Composable
fun UserScreen(viewModel: UserViewModel) { // НЕ пропускаема
    val user by viewModel.userState
    Text(user.name)
}

// ✅ Передавайте состояние, а не ViewModel
@Composable
fun UserScreen(userState: State<User>) {
    val user by userState
    Text(user.name)
}
```

**Проблема: `List` вызывает лишние рекомпозиции**

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

@Composable
fun UserList(users: ImmutableList<User>) { // Пропускаема
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}
```

### Влияние На Производительность

**Без пропуска**: 10,000 composable → изменение 1 элемента → все 10,000 перекомпонуются (~100 мс)

**С правильным пропуском**: 10,000 composable → изменение 1 элемента → только 1 перекомпонуется (~0.1 мс)

**Прирост в 1000 раз.**

## Answer (EN)

**Skippability** is Compose's optimization mechanism allowing the compiler to skip recomposing a function when its inputs haven't changed.

### Skippability Requirements

A composable is **skippable** if:

1. **All parameters are stable** — every parameter must be of a stable type
2. **Returns `Unit`** or is non-restartable
3. **Not marked with `@NonSkippableComposable`**

```kotlin
// ✅ Skippable — primitive parameters
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// ❌ NOT skippable — unstable parameter
data class User(var name: String)

@Composable
fun UserProfile(user: User) { // Always recomposes
    Text(user.name)
}
```

### Stability Criteria

A type is **stable** if the Compose compiler guarantees:

1. **equals() returns the same result for the same instances**
2. **Public property changes notify Composition**
3. **All public properties are also stable types**

**Automatically stable:**
- Primitives: `Int`, `Long`, `Float`, `Boolean`
- `String`, lambdas
- Immutable collections from `kotlinx.collections.immutable`

**Unstable:**
- Classes with `var` properties
- Mutable collections: `MutableList`, `MutableMap`
- Interfaces (compiler can't prove stability)

```kotlin
// ✅ STABLE
data class StableUser(val id: Int, val name: String)

// ❌ UNSTABLE — var property
data class UnstableUser(val id: Int, var name: String)

// ❌ UNSTABLE — mutable collection
data class UnstableList(val users: MutableList<String>)
```

### The `@Stable` Annotation

**`@Stable`** is a promise to the Compose compiler that a type follows the stability contract, even if the compiler can't prove it automatically.

**When to use:**
- Interfaces/abstract classes stable by contract
- Classes with private mutable state never exposed
- Observable patterns (`StateFlow`, `LiveData`) that notify Compose

```kotlin
// ✅ Tell compiler this interface is stable
@Stable
interface UserData {
    val name: String
    val email: String
}

@Composable
fun UserDisplay(user: UserData) { // Now skippable
    Column {
        Text(user.name)
        Text(user.email)
    }
}

// ❌ DANGEROUS — contract violation
@Stable
data class LyingUser(var name: String)

@Composable
fun BuggyDisplay(user: LyingUser) {
    Text(user.name) // Won't update when name changes!
}
```

### Debugging Stability

Enable Compose Compiler Metrics in `build.gradle.kts`:
```kotlin
freeCompilerArgs += listOf(
    "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
    project.buildDir.absolutePath + "/compose_metrics"
)
```

Report shows parameter stability: `stable count: Int` vs `unstable user: User`.

### Practical Solutions

**Problem: `ViewModel` is unstable**

```kotlin
// ❌ ViewModel doesn't guarantee stability
@Composable
fun UserScreen(viewModel: UserViewModel) { // NOT skippable
    val user by viewModel.userState
    Text(user.name)
}

// ✅ Pass state, not ViewModel
@Composable
fun UserScreen(userState: State<User>) {
    val user by userState
    Text(user.name)
}
```

**Problem: `List` causes unnecessary recompositions**

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

@Composable
fun UserList(users: ImmutableList<User>) { // Skippable
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}
```

### Performance Impact

**Without skipping**: 10,000 composables → 1 element changes → all 10,000 recompose (~100 ms)

**With proper skipping**: 10,000 composables → 1 element changes → only 1 recomposes (~0.1 ms)

**1000x improvement.**

---

## Follow-ups

- What is the difference between `@Stable` and `@Immutable` annotations in Compose?
- How does Strong Skipping Mode change lambda stability behavior?
- What compiler metrics help identify recomposition issues?
- How do `State` and `derivedStateOf` interact with stability inference?
- When should you use `remember {}` to improve stability?

## References

- [[c-compose-recomposition]]
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)
- Understanding of Compose recomposition basics
- Basic knowledge of immutable data structures

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]] — Advanced Compose performance techniques
- Recomposition optimization strategies

### Advanced (Harder)
- Compose compiler plugin internals and stability inference
