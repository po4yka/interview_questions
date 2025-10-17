---
id: "20251015082237239"
title: "Compose Stability Skippability / Стабильность и пропускаемость Compose"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: [compose, performance, compiler, stability, optimization, difficulty/hard]
---

# Compose Stability & Skippability

# Question (EN)

> Explain how Compose determines if a composable is skippable. What makes a class stable? How does the @Stable annotation work?

# Вопрос (RU)

> Объясните, как Compose определяет, можно ли пропустить перекомпозицию composable-функции. Что делает класс стабильным? Как работает аннотация @Stable?

---

## Answer (EN)

**Skippability** is Compose's optimization mechanism that allows the compiler to skip recomposing a composable when its inputs haven't changed. This is critical for performance in large Compose UIs.

### How Compose Determines Skippability

A composable is **skippable** if all of the following conditions are met:

1. **All parameters are stable** - Every parameter must be of a stable type
2. **No default parameter expressions** that capture unstable values
3. **Not marked with @NonSkippableComposable**
4. **Returns Unit** (or is a non-restartable composable)

```kotlin
//  SKIPPABLE - all parameters are primitives (stable)
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

//  NOT SKIPPABLE - unstable parameter
data class User(var name: String) // var makes it unstable

@Composable
fun UserProfile(user: User) { // Will always recompose
    Text(user.name)
}

//  SKIPPABLE - immutable data class
data class ImmutableUser(val name: String) // val makes it stable

@Composable
fun ImmutableUserProfile(user: ImmutableUser) { // Can be skipped
    Text(user.name)
}
```

---

### What Makes a Class Stable?

A type is **stable** if the Compose compiler can guarantee that:

1. **Result of equals() will always return the same result for the same two instances**
2. **If a public property changes, Composition will be notified**
3. **All public properties are also stable types**

**Automatically stable types:**

-   All primitive types (`Int`, `Long`, `Float`, `Boolean`, etc.)
-   `String`
-   All function types (lambdas)
-   Immutable collections from `kotlinx.collections.immutable`

**Conditionally stable:**

-   Data classes where all properties are `val` and of stable types
-   Sealed classes with stable subtypes

**Unstable:**

-   Classes with `var` properties
-   Mutable collections (`MutableList`, `MutableMap`, etc.)
-   Interfaces (Compose can't prove stability)
-   Abstract classes

```kotlin
//  STABLE - all properties are val and stable types
data class StableUser(
    val id: Int,
    val name: String,
    val email: String
)

//  UNSTABLE - has var property
data class UnstableUser(
    val id: Int,
    var name: String, // var makes entire class unstable
    val email: String
)

//  UNSTABLE - has mutable collection
data class UnstableUserList(
    val users: MutableList<String> // Mutable collection is unstable
)

//  STABLE - immutable collection
data class StableUserList(
    val users: List<String> // Immutable List is stable
)

//  UNSTABLE - interface
interface UserData {
    val name: String
}

//  UNSTABLE - uses unstable interface
@Composable
fun UserDisplay(user: UserData) { // Will recompose every time
    Text(user.name)
}
```

---

### The @Stable Annotation

The **@Stable** annotation is a **promise** to the Compose compiler that a type follows the stability contract, even if the compiler can't prove it automatically.

**Use @Stable when:**

-   You have an interface or abstract class that you know is stable
-   You have a class with private mutable state that's never exposed
-   You're using observable patterns (StateFlow, LiveData) that notify Compose

```kotlin
// Tell Compose this interface is stable
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

// Implementation is actually stable
class UserImpl(
    override val name: String,
    override val email: String
) : StableUserData
```

**@Stable with private mutable state:**

```kotlin
@Stable
class Counter {
    private var _count = mutableStateOf(0)
    val count: State<Int> = _count

    fun increment() {
        _count.value++
    }
}

@Composable
fun CounterDisplay(counter: Counter) { // Skippable!
    Text("Count: ${counter.count.value}")
}
```

**Warning: @Stable is a contract** - if you lie to the compiler, you'll get incorrect skipping behavior and bugs:

```kotlin
//  INCORRECT - lying about stability
@Stable
data class LyingUser(
    var name: String // This is mutable but we claimed stable!
)

@Composable
fun UserDisplay(user: LyingUser) {
    Text(user.name) // Won't recompose when name changes! BUG!
}
```

---

### Debugging Stability

**Check if a composable is skippable** using the Compose Compiler Metrics:

```gradle
// build.gradle.kts
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
                project.buildDir.absolutePath + "/compose_metrics"
        )
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=" +
                project.buildDir.absolutePath + "/compose_metrics"
        )
    }
}
```

This generates reports showing:

-   Which composables are skippable
-   Which parameters are unstable
-   Stability inference for your classes

**Example report:**

```
restartable skippable scheme("[androidx.compose.ui.UiComposable]") fun Counter(
  stable count: Int
  stable onIncrement: Function0<Unit>
)

restartable scheme("[androidx.compose.ui.UiComposable]") fun UserProfile(
  unstable user: User
)
```

---

### Real-World Examples

**Problem: ViewModel parameters are unstable**

```kotlin
//  UNSTABLE - ViewModel is a class, not guaranteed stable
class UserViewModel : ViewModel() {
    val userState = mutableStateOf(User())
}

@Composable
fun UserScreen(viewModel: UserViewModel) { // NOT skippable
    val user by viewModel.userState
    Text(user.name)
}
```

**Solution 1: Use @Stable (if you control the class)**

```kotlin
@Stable
class UserViewModel : ViewModel() {
    private val _userState = mutableStateOf(User())
    val userState: State<User> = _userState
}

@Composable
fun UserScreen(viewModel: UserViewModel) { // Now skippable!
    val user by viewModel.userState
    Text(user.name)
}
```

**Solution 2: Don't pass ViewModel, pass state**

```kotlin
@Composable
fun UserScreen(userState: State<User>) { // Stable parameter
    val user by userState
    Text(user.name)
}

// Call site
@Composable
fun UserScreenContainer(viewModel: UserViewModel) {
    UserScreen(userState = viewModel.userState)
}
```

---

**Problem: List causing unnecessary recompositions**

```kotlin
//  UNSTABLE - MutableList is unstable
@Composable
fun UserList(users: MutableList<User>) { // NOT skippable
    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

**Solution: Use immutable collections**

```kotlin
import kotlinx.collections.immutable.ImmutableList
import kotlinx.collections.immutable.persistentListOf

//  STABLE - ImmutableList is stable
@Composable
fun UserList(users: ImmutableList<User>) { // Skippable!
    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}

// Usage
val users = persistentListOf(
    User(1, "Alice"),
    User(2, "Bob")
)
UserList(users)
```

---

### Advanced: Strong Skipping Mode

Compose 1.5.4+ introduced **Strong Skipping Mode** which makes skipping more aggressive:

```gradle
// build.gradle.kts
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:experimentalStrongSkipping=true"
        )
    }
}
```

**What it does:**

-   Treats lambdas as stable even if they capture unstable values
-   Makes more composables skippable by default
-   Experimental feature, use with caution

```kotlin
// Without strong skipping: NOT skippable (lambda captures unstable user)
// With strong skipping: SKIPPABLE

var user by remember { mutableStateOf(User("Alice")) }

Button(onClick = { user = User("Bob") }) { // Lambda captures user
    Text("Change User")
}
```

---

### Best Practices

1. **Use immutable data classes** for Compose parameters

```kotlin
//  DO
data class User(val name: String, val age: Int)

//  DON'T
data class User(var name: String, var age: Int)
```

2. **Use kotlinx-collections-immutable** for lists

```kotlin
//  DO
fun getUsers(): ImmutableList<User> = persistentListOf(...)

//  DON'T
fun getUsers(): List<User> = mutableListOf(...) // Still unstable!
```

3. **Add @Stable to interfaces you control**

```kotlin
@Stable
interface Repository {
    val data: StateFlow<List<User>>
}
```

4. **Check compiler reports** regularly

5. **Don't overuse @Stable** - only when you're certain about stability

6. **Consider strong skipping mode** for better default behavior

---

### Performance Impact

**Without skipping:**

-   10,000 composables on screen
-   State change affects 1 composable
-   Result: All 10,000 recompose
-   Time: ~100ms

**With proper skipping:**

-   10,000 composables on screen
-   State change affects 1 composable
-   Result: Only 1 recomposes
-   Time: ~0.1ms

**1000x performance improvement!**

---

## Ответ (RU)

**Возможность пропуска (Skippability)** — это механизм оптимизации Compose, который позволяет компилятору пропускать перекомпозицию composable-функции, когда её входные параметры не изменились. Это критично для производительности в больших Compose UI.

### Как Compose определяет возможность пропуска

Composable-функция **может быть пропущена**, если выполнены все следующие условия:

1. **Все параметры стабильны** - каждый параметр должен быть стабильного типа
2. **Нет выражений параметров по умолчанию**, которые захватывают нестабильные значения
3. **Не помечена @NonSkippableComposable**
4. **Возвращает Unit** (или является неперезапускаемой composable)

```kotlin
//  ПРОПУСКАЕТСЯ - все параметры примитивы (стабильны)
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

//  НЕ ПРОПУСКАЕТСЯ - нестабильный параметр
data class User(var name: String) // var делает его нестабильным

@Composable
fun UserProfile(user: User) { // Будет всегда перекомпоноваться
    Text(user.name)
}
```

### Что делает класс стабильным?

Тип является **стабильным**, если компилятор Compose может гарантировать:

1. **Результат equals() всегда возвращает одинаковый результат для одних и тех же экземпляров**
2. **Если публичное свойство изменяется, Composition получит уведомление**
3. **Все публичные свойства также являются стабильными типами**

**Автоматически стабильные типы:**

-   Все примитивные типы (`Int`, `Long`, `Float`, `Boolean` и т.д.)
-   `String`
-   Все функциональные типы (лямбды)
-   Неизменяемые коллекции из `kotlinx.collections.immutable`

**Условно стабильные:**

-   Data классы, где все свойства `val` и стабильных типов
-   Sealed классы со стабильными подтипами

**Нестабильные:**

-   Классы со свойствами `var`
-   Изменяемые коллекции (`MutableList`, `MutableMap` и т.д.)
-   Интерфейсы (Compose не может доказать стабильность)
-   Абстрактные классы

### Аннотация @Stable

Аннотация **@Stable** — это **обещание** компилятору Compose, что тип следует контракту стабильности, даже если компилятор не может это доказать автоматически.

**Используйте @Stable когда:**

-   У вас есть интерфейс или абстрактный класс, о котором вы знаете, что он стабилен
-   У вас есть класс с приватным изменяемым состоянием, которое никогда не раскрывается
-   Вы используете observable паттерны (StateFlow, LiveData), которые уведомляют Compose

```kotlin
@Stable
interface StableUserData {
    val name: String
    val email: String
}

@Composable
fun UserDisplay(user: StableUserData) { // Теперь пропускается!
    Column {
        Text(user.name)
        Text(user.email)
    }
}
```

**Влияние на производительность:**

Без пропуска: 10,000 composables, изменение 1 состояния = все 10,000 перекомпонуются (~100ms)
С правильным пропуском: только 1 перекомпонуется (~0.1ms)

**Улучшение производительности в 1000 раз!**

---

## Follow-ups

-   How does Compose's stability analysis compare to React's memo optimization?
-   What are the performance implications of using @Immutable vs @Stable annotations?
-   How can you debug and profile Compose recomposition to identify stability issues?

## References

-   `https://developer.android.com/jetpack/compose/mental-model` — Compose mental model
-   `https://developer.android.com/jetpack/compose/performance` — Compose performance
-   `https://developer.android.com/jetpack/compose/state` — State management in Compose

## Related Questions

### Hub

-   [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Hard)

-   [[q-stable-classes-compose--android--hard]] - @Stable annotation
-   [[q-stable-annotation-compose--android--hard]] - Stability annotations
-   [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Slot table internals
-   [[q-compose-performance-optimization--android--hard]] - Performance optimization
-   [[q-compose-custom-layout--jetpack-compose--hard]] - Custom layouts
