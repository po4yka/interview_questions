---
id: android-142
title: Compose Stability Skippability / Стабильность и пропускаемость Compose
aliases:
- Compose Stability Skippability
- Стабильность и пропускаемость Compose
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
- c-recomposition
- q-compose-compiler-plugin--android--hard
- q-compose-lazy-layout-optimization--android--hard
- q-compose-performance-optimization--android--hard
created: 2025-10-15
updated: 2025-11-10
tags:
- android/performance-memory
- android/ui-compose
- difficulty/hard
sources: []
anki_cards:
- slug: android-142-0-en
  language: en
  anki_id: 1768366065529
  synced_at: '2026-01-23T16:45:05.350851'
- slug: android-142-0-ru
  language: ru
  anki_id: 1768366065552
  synced_at: '2026-01-23T16:45:05.352940'
---
# Вопрос (RU)
> Как стабильность типов влияет на пропускаемость перекомпозиции в Jetpack Compose?

# Question (EN)
> How does type stability affect recomposition skippability in Jetpack Compose?

---

## Ответ (RU)

**Пропускаемость (skippability)** — механизм оптимизации, позволяющий рантайму Compose пропустить рекомпозицию `@Composable`-функции, если для данного вызова можно надёжно определить, что отслеживаемые входы (включая параметры стабильных типов) не изменились.

### Условия Пропускаемости

Composable-функция (конкретный вызов) может быть помечена как пропускаемая, если выполняются, в упрощённом виде:

1. **Все параметры имеют стабильные типы** — для каждого параметра компилятор может применить проверку «изменилось / не изменилось».
2. **Функция возвращает `Unit`** (не влияет на последующую композицию своим возвращаемым значением).
3. **Функция не помечена `@NonSkippableComposable`.**

Стабильность типов прямо влияет на пункт (1): если тип нестабилен, компилятор не может безопасно сделать вывод об отсутствии изменений и вынужден рекомпозировать при обходе этого узла.

Если функция помечена как непропускаемая, то при достижении соответствующего узла в дереве во время рекомпозиции она будет выполняться снова, даже при логически тех же значениях параметров (с точки зрения разработчика).

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

Тип считается **стабильным** (упрощённо для практики), если:

1. Для него можно надёжно определить, изменилось ли значение между рекомпозициями (по ссылке и/или по значимым полям).
2. При изменении значимых для UI данных это изменение не будет скрыто от Compose (идёт через отслеживаемое состояние, снапшоты и т.п., а не через незаметный сайд-эффект).
3. Все его публичные свойства также стабильны или корректно управляются.

Compose-компилятор знает о наборе типов и шаблонов, которые по этим правилам можно считать стабильными.

**Автоматически стабильные (примеры):**
- Примитивы: `Int`, `Long`, `Float`, `Boolean`.
- `String`.
- Некоторые лямбды и функциональные типы, когда компилятор может доказать их неизменяемость и безопасное переиспользование (особенно в режиме Strong Skipping). В общем случае функции не считаются стабильными по умолчанию.
- Иммутабельные коллекции из `kotlinx.collections.immutable`.

**Типично нестабильные:**
- Классы с `var`-свойствами, изменяемыми без уведомления Compose.
- Мутабельные коллекции: `MutableList`, `MutableMap` и т.п.
- Интерфейсы (компилятор не может доказать их стабильность без аннотаций).

```kotlin
// ✅ STABLE (при условии, что поля не меняются способами, невидимыми для Compose)
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
    // Из-за некорректной аннотации компилятор может агрессивнее пропускать
    // рекомпозиции, что приведёт к потенциально несвоевременному обновлению UI.
}
```

Важно: `@Stable` не отключает механизм отслеживания чтений состояния. Проблема в том, что неверное использование аннотации даёт компилятору право делать более агрессивные оптимизации пропуска, из-за чего реальные изменения могут быть не отображены.

### Отладка Стабильности

Включите Compose Compiler Metrics в `build.gradle.kts`:
```kotlin
freeCompilerArgs += listOf(
    "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
    project.buildDir.absolutePath + "/compose_metrics"
)
```

Отчёт покажет, как компилятор классифицирует стабильность параметров и пропускаемость вызовов, например: `stable count: Int` и `unstable user: User`.

### Практические Решения

**Проблема: `ViewModel` как параметр**

```kotlin
// ⚠️ ViewModel по умолчанию не считается стабильным типом
@Composable
fun UserScreen(viewModel: UserViewModel) { // Узел с меньшим потенциалом пропускаемости
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

Это может давать кратные улучшения производительности на больших списках.

## Answer (EN)

"Skippability" is Compose's optimization mechanism that allows the runtime to skip recomposing a `@Composable` function call when, for that call, it can reliably determine that tracked inputs (including parameters of stable types) have not changed.

### Skippability Requirements

A composable call can be treated as **skippable** when, in simplified form:

1. **All parameters are of stable types** — for each parameter the compiler can apply an efficient "changed / not changed" check.
2. **It returns `Unit`** (its return value does not affect subsequent composition nodes).
3. **It is not annotated with `@NonSkippableComposable`.**

Type stability directly affects (1): if a parameter type is unstable, the compiler cannot safely infer "unchanged" and must conservatively recompose when visiting that node.

If a function (or specific call site) is non-skippable, then whenever recomposition reaches that node, it will run again even when, logically, the values seem equal from the developer's point of view.

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

1. The runtime/compiler can reliably tell whether its value has changed between recompositions (via reference and/or relevant field comparisons).
2. Changes to UI-relevant data are not hidden from Compose (they go through tracked state / snapshot mechanisms instead of invisible side effects).
3. All its public properties are also stable types or are properly managed.

The Compose compiler has built-in knowledge of certain types and patterns that satisfy these rules.

**Automatically stable (examples):**
- Primitives: `Int`, `Long`, `Float`, `Boolean`.
- `String`.
- Some lambdas / function types when the compiler can prove they are stable to reuse (especially with Strong Skipping enabled). In general, function types are not assumed stable by default.
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
}
```

Important: `@Stable` does not disable Compose's state read tracking. The issue with misuse is that by lying about stability you allow the compiler to assume fewer changes and skip recompositions more aggressively, which can result in incorrect, stale UI.

### Debugging Stability

Enable Compose Compiler Metrics in `build.gradle.kts`:
```kotlin
freeCompilerArgs += listOf(
    "-P", "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
    project.buildDir.absolutePath + "/compose_metrics"
)
```

The report shows how the compiler classifies parameter stability and call-site skippability, e.g.: `stable count: Int` and `unstable user: User`.

### Practical Solutions

**Problem: `ViewModel` as parameter**

```kotlin
// ⚠️ ViewModel is not considered a stable type by default
@Composable
fun UserScreen(viewModel: UserViewModel) { // Node with lower skippability potential
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

- Without effective skipping: 10,000 composables → when 1 item changes, a large portion of the tree may recompose.
- With correct stability and skipping: 10,000 composables → when 1 item changes, only the affected branch recomposes.

This can yield order-of-magnitude performance improvements for large lists.

---

## Дополнительные Вопросы (RU)

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
