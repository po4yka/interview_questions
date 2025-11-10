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
status: draft
moc: moc-android
related:
- c-compose-recomposition
- q-compose-performance-optimization--android--hard
created: 2025-10-15
updated: 2025-11-10
tags: [android/performance-memory, android/ui-compose, difficulty/hard]
sources: []

---

# Вопрос (RU)
> Как стабильность типов влияет на пропускаемость перекомпозиции в Jetpack Compose?

# Question (EN)
> How does type stability affect recomposition skippability in Jetpack Compose?

---

## Ответ (RU)

**Пропускаемость (skippability)** — механизм оптимизации, позволяющий компилятору/рантайму пропустить рекомпозицию `@Composable`-функции, если её параметры (и другие отслеживаемые входы) не изменились.

### Условия Пропускаемости

Composable-функция может быть помечена как пропускаемая, если:

1. **Все параметры стабильны** — каждый параметр имеет стабильный тип.
2. **Функция возвращает `Unit`** или является нерестартуема (не требует перезапуска звонка).
3. **Не помечена `@NonSkippableComposable`**.

Если функция не пропускаема, то при её достижении в дереве при рекомпозиции она будет пересчитываться, даже когда значения параметров не изменились.

```kotlin
// ✅ Высокий потенциал пропуска — примитивные параметры стабильны
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// ⚠️ Параметр нестабилен
// Функция будет отмечена как непропускаемая и будет рекомпозирована
// каждый раз при обходе этого узла во время рекомпозиции.
data class User(var name: String)

@Composable
fun UserProfile(user: User) {
    Text(user.name)
}
```

### Критерии Стабильности

Тип считается **стабильным**, если (упрощённо для практики):

1. Для него можно надёжно определить, изменилось ли значение между рекомпозициями (по ссылке и/или по значению).
2. При изменении значимых для UI данных это изменение не будет "скрыто" от системы (например, изменение идёт через отслеживаемое состояние, а не через незаметный для Compose сайд-эффект).
3. Все его публичные свойства также стабильны или корректно управляются.

Compose-компилятор знает о наборе типов и шаблонов, которые по этим правилам можно считать стабильными.

**Автоматически стабильные (примеры):**
- Примитивы: `Int`, `Long`, `Float`, `Boolean`.
- `String`, лямбды.
- Иммутабельные коллекции из `kotlinx.collections.immutable`.

**Типично нестабильные:**
- Классы с `var`-свойствами, изменяемыми без уведомления Compose.
- Мутабельные коллекции: `MutableList`, `MutableMap` и т.п.
- Интерфейсы (компилятор не может доказать их стабильность без аннотаций).

```kotlin
// ✅ STABLE (при условии, что поля не меняются за пределами контролируемого состояния)
data class StableUser(val id: Int, val name: String)

// ❌ UNSTABLE — var-свойство, изменение может не быть отслежено
data class UnstableUser(val id: Int, var name: String)

// ❌ UNSTABLE — мутабельная коллекция
data class UnstableList(val users: MutableList<String>)
```

### Аннотация `@Stable`

**`@Stable`** — это контракт: вы обещаете компилятору, что тип соблюдает правила стабильности, даже если он не может это вывести автоматически.

**Когда использовать:**
- Интерфейсы/абстрактные классы, стабильные по контракту.
- Классы с приватным мутабельным состоянием, изменения которого отражаются через отслеживаемые `State`/`Snapshot`-механизмы.
- Обёртки над observable-типами (`StateFlow`, `LiveData` и т.п.), которые корректно уведомляют Compose.

```kotlin
// ✅ Указываем стабильность интерфейса
@Stable
interface UserData {
    val name: String
    val email: String
}

@Composable
fun UserDisplay(user: UserData) {
    Column {
        Text(user.name)
        Text(user.email)
    }
}

// ❌ ОПАСНО — нарушение контракта стабильности
@Stable
data class LyingUser(var name: String)

@Composable
fun BuggyDisplay(user: LyingUser) {
    Text(user.name)
    // Из-за лживой аннотации компилятор может оптимистично
    // пропускать рекомпозиции, что потенциально приведёт к
    // устаревшему UI. Поведение становится неопределённым.
}
```

Важно: `@Stable` не запрещает Compose отслеживать чтения состояния. Проблема в том, что неверное использование аннотации даёт компилятору право делать агрессивные оптимизации, которые могут скрыть реальные изменения.

### Отладка Стабильности

Включите Compose Compiler Metrics в `build.gradle.kts`:
```kotlin
freeCompilerArgs += listOf(
    "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
    project.buildDir.absolutePath + "/compose_metrics"
)
```

Отчёт покажет стабильность параметров, например: `stable count: Int` и `unstable user: User`.

### Практические Решения

**Проблема: `ViewModel` как параметр**

```kotlin
// ⚠️ ViewModel по умолчанию не считается стабильным
@Composable
fun UserScreen(viewModel: UserViewModel) { // Узел, скорее всего, непропускаем
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
fun UserList(users: MutableList<User>) { // Непропускаемо, выше риск лишних рекомпозиций
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}

// ✅ Используйте ImmutableList
import kotlinx.collections.immutable.ImmutableList

@Composable
fun UserList(users: ImmutableList<User>) { // Лучше для стабильности
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}
```

### Влияние На Производительность

Примерно иллюстративно:

- Без эффективного пропуска: 10 000 composable → изменение одного элемента → может пересчитаться значительная часть дерева.
- С корректной стабильностью и пропуском: 10 000 composable → изменение одного элемента → пере-компонуется только затронутая ветка.

Это может давать порядки улучшения производительности на больших списках.

## Answer (EN)

**Skippability** is Compose's optimization mechanism that allows the compiler/runtime to skip recomposing a `@Composable` function when its parameters (and other tracked inputs) have not changed.

### Skippability Requirements

A composable can be treated as **skippable** when:

1. **All parameters are stable** — each parameter is of a stable type.
2. **It returns `Unit`** or is non-restartable (does not require restarting the call).
3. **It is not annotated with `@NonSkippableComposable`**.

If a function is non-skippable, then whenever recomposition reaches that node in the tree, it will recompose even if the parameter values are equal to previous ones.

```kotlin
// ✅ High skippability potential — primitive params are stable
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// ⚠️ Unstable parameter
data class User(var name: String)

@Composable
fun UserProfile(user: User) {
    // Marked non-skippable due to unstable type,
    // so it will recompose whenever this node is visited in recomposition.
    Text(user.name)
}
```

### Stability Criteria

A type is considered **stable** (practically speaking) if:

1. The runtime/compiler can reliably tell whether its value has changed between recompositions (via reference and/or value semantics).
2. Changes to meaningful UI data are not "hidden" from Compose (they go through tracked state mechanisms instead of invisible side effects).
3. All its public properties are also stable types or are properly managed.

The Compose compiler has built-in knowledge of certain types and patterns that satisfy these rules.

**Automatically stable (examples):**
- Primitives: `Int`, `Long`, `Float`, `Boolean`.
- `String`, lambdas.
- Immutable collections from `kotlinx.collections.immutable`.

**Typically unstable:**
- Classes with `var` properties mutated without going through tracked state.
- Mutable collections: `MutableList`, `MutableMap`, etc.
- Interfaces (the compiler cannot prove stability without annotations).

```kotlin
// ✅ STABLE (assuming fields are not mutated in ways invisible to Compose)
data class StableUser(val id: Int, val name: String)

// ❌ UNSTABLE — var property; mutation may not be tracked correctly
data class UnstableUser(val id: Int, var name: String)

// ❌ UNSTABLE — mutable collection
data class UnstableList(val users: MutableList<String>)
```

### The `@Stable` Annotation

`@Stable` is a contract with the Compose compiler: you promise that the type follows the stability rules even if the compiler cannot infer it automatically.

**When to use:**
- Interfaces/abstract classes that are stable by design.
- Classes with private mutable state whose changes are exposed via tracked `State`/`Snapshot`-based properties.
- Wrappers around observable types (`StateFlow`, `LiveData`, etc.) that properly notify Compose.

```kotlin
// ✅ Tell the compiler this interface is stable
@Stable
interface UserData {
    val name: String
    val email: String
}

@Composable
fun UserDisplay(user: UserData) {
    Column {
        Text(user.name)
        Text(user.email)
    }
}

// ❌ DANGEROUS — violates stability contract
@Stable
data class LyingUser(var name: String)

@Composable
fun BuggyDisplay(user: LyingUser) {
    Text(user.name)
    // Because of the incorrect @Stable, the compiler is allowed
    // to apply more aggressive skipping, which can lead to stale UI.
    // Behavior becomes undefined/bug-prone, not a guaranteed "no update".
}
```

Important: `@Stable` does not turn off Compose's state read tracking. The risk is that lying about stability lets the compiler assume fewer changes and over-skip recompositions.

### Debugging Stability

Enable Compose Compiler Metrics in `build.gradle.kts`:
```kotlin
freeCompilerArgs += listOf(
    "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
    project.buildDir.absolutePath + "/compose_metrics"
)
```

The report will show parameter stability, e.g.: `stable count: Int` and `unstable user: User`.

### Practical Solutions

**Problem: `ViewModel` as parameter**

```kotlin
// ⚠️ ViewModel is not inherently stable
@Composable
fun UserScreen(viewModel: UserViewModel) { // Likely non-skippable node
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
fun UserList(users: MutableList<User>) { // Non-skippable, higher risk of extra recomposition
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}

// ✅ Use ImmutableList
import kotlinx.collections.immutable.ImmutableList

@Composable
fun UserList(users: ImmutableList<User>) { // Better for stability
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}
```

### Performance Impact

Illustrative example:

- Without effective skipping: 10,000 composables → when 1 item changes, a large portion of the tree may be recomposed.
- With correct stability and skipping: 10,000 composables → when 1 item changes, only the affected branch recomposes.

This can yield order-of-magnitude performance improvements for large lists.

---

## Дополнительные вопросы (RU)

- В чем разница между аннотациями `@Stable` и `@Immutable` в Compose?
- Как режим Strong Skipping Mode влияет на поведение стабильности лямбд?
- Какие метрики компилятора помогают выявлять проблемы с рекомпозицией?
- Как `State` и `derivedStateOf` взаимодействуют с выводом стабильности?
- Когда стоит использовать `remember {}` для улучшения стабильности?

## Follow-ups

- What is the difference between `@Stable` and `@Immutable` annotations in Compose?
- How does Strong Skipping Mode change lambda stability behavior?
- What compiler metrics help identify recomposition issues?
- How do `State` and `derivedStateOf` interact with stability inference?
- When should you use `remember {}` to improve stability?

## Ссылки (RU)

- [[c-compose-recomposition]]
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model

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
