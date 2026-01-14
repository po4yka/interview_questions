---\
id: android-108
title: "How MutableState Notifies / Как MutableState уведомляет"
aliases: [MutableState notifications, MutableState уведомления, Snapshot system]
topic: android
subtopics: [architecture-mvvm, ui-compose, ui-state]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-10
tags: [android/architecture-mvvm, android/ui-compose, android/ui-state, difficulty/medium, mutablestate, observer-pattern, recomposition, snapshot-system, state-management]
moc: moc-android
related: [c-compose-state, c-recomposition, q-recomposition-choreographer--android--hard]
sources: []
anki_cards:
  - slug: android-108-0-en
    front: "How does MutableState notify Compose about changes?"
    back: |
      Uses **Snapshot system** with read/write tracking (Observer pattern):

      **1. Subscription (read phase):**
      - Reading `MutableState` during composition registers dependency
      - `Text("$count")` - this composable now depends on `count`

      **2. Notification (write phase):**
      - `count++` writes new value
      - Snapshot system marks dependent scopes invalid
      - Recomposition scheduled for those scopes only

      **Benefits:** Isolation, thread-safe reads, granular recomposition
    tags:
      - android_compose
      - difficulty::medium
  - slug: android-108-0-ru
    front: "Как MutableState уведомляет Compose об изменениях?"
    back: |
      Использует **Snapshot system** с отслеживанием чтений/записей (Observer pattern):

      **1. Подписка (фаза чтения):**
      - Чтение `MutableState` во время композиции регистрирует зависимость
      - `Text("$count")` - этот composable теперь зависит от `count`

      **2. Уведомление (фаза записи):**
      - `count++` записывает новое значение
      - Snapshot system помечает зависимые scope невалидными
      - Рекомпозиция планируется только для этих scope

      **Преимущества:** Изоляция, потокобезопасное чтение, гранулярная рекомпозиция
    tags:
      - android_compose
      - difficulty::medium

---\
# Вопрос (RU)
> Как MutableState уведомляет о том, что он изменился?

# Question (EN)
> How does MutableState notify that it has changed?

---

## Ответ (RU)

**MutableState** использует систему снимков состояния (**Snapshot system**) и механизм отслеживания чтений/записей, концептуально похожий на **`Observer` pattern**, чтобы автоматически помечать затронутые участки композиции как требующие рекомпозиции.

### Механизм Работы

**1. Подписка (фаза чтения)**
Composable «подписывается» при **чтении** состояния: во время композиции чтение `MutableState` регистрируется в Snapshot system, и этот участок дерева связывается с данным состоянием.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    // Чтение count регистрируется в Snapshot system
    Text("Count: $count")  // ✅ Этот composable зависит от count

    Button(onClick = { count++ }) {
        Text("Increment")
    }
}
```

**2. Уведомление (фаза записи)**
При изменении значения:
1. `count++` записывает новое значение в `MutableState`.
2. Snapshot system фиксирует факт изменения отслеживаемого состояния.
3. Соответствующие композиционные области помечаются как невалидные.
4. Планируется рекомпозиция этих областей.
5. Рекомпозируется минимальный контекст (scope), который читал `count` (например, тело `Counter` или вложенный composable), а не вся иерархия.

### Система Snapshot

Система Snapshot предоставляет согласованные снимки состояния и отслеживание чтений/записей. При обычном использовании `mutableStateOf` Compose автоматически управляет snapshot-ами и зависимостями.

Пример ниже иллюстрирует идею, но не является реальным кодом рабочего приложения:

```kotlin
// Псевдокод, иллюстрирующий концепцию
// Snapshot 1: count = 0
// Snapshot 2: count = 1 после изменения
```

**Преимущества (в контексте Snapshot system):**
- **Изоляция** — чтения в рамках одного snapshot-а видят консистентное состояние.
- **Потокобезопасность для чтения** — несколько потоков могут безопасно читать через snapshot-ы.
- **Возможность отката/отмены** — при использовании явных snapshot API можно отменять изменения; в типичном UI-коде с `mutableStateOf` это используется фреймворком, а не как универсальный механизм undo.

### Гранулярная Рекомпозиция

Рекомпозируются только те composable-области, которые **читали** изменённое состояние.
Важно: гранулярность — это scope рекомпозиции (обычно граница функции-компоновки), а не отдельный вызов `Text` как таковой.

```kotlin
@Composable
fun Screen() {
    var name by remember { mutableStateOf("Alice") }
    var age by remember { mutableStateOf(25) }

    Column {
        Text("Name: $name")  // ✅ Зависит от name
        Text("Age: $age")    // ✅ Зависит от age

        Button(onClick = { age++ }) {
            Text("Increment Age")
        }
    }
}
```

**При клике на кнопку:**
- `age++` помечает зависимости `age` как невалидные.
- В рекомпозицию попадает минимальный scope, который читает `age` (и может быть пересоздан соответствующий участок).
- Код, зависящий только от `name`, не будет рекомпозирован сверх необходимого.

### Упрощённая (Псевдо) Реализация

Ниже — концептуальное приближение, а не реальная реализация Compose. В реальности используется `SnapshotMutableStateImpl` и внутренняя Snapshot system, а не явный список подписчиков.

```kotlin
// Псевдокод — только для иллюстрации идей наблюдения и инвалидации
class MutableStateImpl<T>(private var _value: T) : MutableState<T> {

    override var value: T
        get() {
            // Реально Compose регистрирует чтение в Snapshot system,
            // чтобы знать, какие composable зависят от этого состояния.
            return _value
        }
        set(newValue) {
            if (_value != newValue) {
                _value = newValue
                // Реально: пометить связанные snapshot-читатели как невалидные,
                // что приведёт к планированию рекомпозиции.
            }
        }
}
```

### Интеграция С `ViewModel`

Этот пример показывает, как `StateFlow` интегрируется с Compose, а не то, как сам `MutableState` устроен внутри.

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++  // ✅ Уведомляет коллекторов StateFlow
    }
}

@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    val count by viewModel.count.collectAsState()

    Text("Count: $count")  // ✅ Рекомпозиция при новых значениях из StateFlow
}
```

**Поток:**
1. `viewModel.increment()` изменяет `_count.value`.
2. `StateFlow` эмитит новое значение.
3. `collectAsState()` получает значение.
4. Обновляет внутренний `State`/`MutableState`, отслеживаемый Compose.
5. Snapshot system помечает зависимости как невалидные.
6. `Text` рекомпозируется.

### Жизненный Цикл Подписок

```kotlin
@Composable
fun ConditionalDisplay() {
    var count by remember { mutableStateOf(0) }
    var showDetails by remember { mutableStateOf(false) }

    Column {
        Button(onClick = { showDetails = !showDetails }) {
            Text("Toggle Details")
        }

        if (showDetails) {
            Text("Count: $count")  // ✅ Читает count только когда в композиции
        }
    }
}
```

Compose автоматически управляет зависимостями и инвалидацией:
- Зависимость регистрируется, когда composable входит в композицию и читает состояние.
- При выходе composable из композиции соответствующие зависимости больше не учитываются.

---

## Answer (EN)

**MutableState** uses Compose's **Snapshot system** and read/write tracking (conceptually similar to an **`Observer` pattern**) to automatically mark dependent parts of the composition as needing recomposition when its value changes.

### How It Works

**1. Subscription (Read Phase)**
A composable "subscribes" when it **reads** the state: during composition, reading a `MutableState` is recorded by the Snapshot system and associates that part of the composition with this state.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    // Reading count is tracked by the Snapshot system
    Text("Count: $count")  // ✅ This composable depends on count

    Button(onClick = { count++ }) {
        Text("Increment")
    }
}
```

**2. Notification (Write Phase)**
When the value is updated:
1. `count++` writes the new value to `MutableState`.
2. The Snapshot system records that a tracked state has changed.
3. The corresponding composition scopes are marked invalid.
4. Recomposition is scheduled for those scopes.
5. The smallest recomposition scope that read `count` (e.g., the composable function body) is recomposed, not the entire hierarchy.

### Snapshot System

The Snapshot system provides consistent views of state and tracks reads/writes. With typical `mutableStateOf` usage, Compose manages snapshots for you automatically.

The example below illustrates the idea and is not real production code:

```kotlin
// Pseudo-code illustrating the concept
// Snapshot 1: count = 0
// Snapshot 2: count = 1 after the change
```

**Benefits (in the context of the Snapshot system):**
- **Isolation** – reads within a snapshot see a consistent view of state.
- **`Thread`-safe reads** – multiple threads can safely read using snapshots.
- **Rollback capability** – with explicit snapshot APIs you can discard changes; in typical UI code with `mutableStateOf`, this is handled by the framework rather than as a general undo mechanism.

### Granular Recomposition

Only composable scopes that **read** the changed state are recomposed.
Important: granularity is defined by recomposition scopes (often composable function boundaries), not by individual `Text` calls in isolation.

```kotlin
@Composable
fun Screen() {
    var name by remember { mutableStateOf("Alice") }
    var age by remember { mutableStateOf(25) }

    Column {
        Text("Name: $name")  // ✅ Depends on name
        Text("Age: $age")    // ✅ Depends on age

        Button(onClick = { age++ }) {
            Text("Increment Age")
        }
    }
}
```

**When user clicks the button:**
- `age++` marks the dependencies of `age` as invalid.
- The minimal scope that reads `age` is recomposed.
- Code that only depends on `name` is not recomposed beyond what is necessary.

### Simplified (Pseudo) Implementation

The following is a conceptual sketch, not the actual Compose implementation. In reality, `SnapshotMutableStateImpl` and the Snapshot system manage tracking and invalidation; there is no public manual subscriber list.

```kotlin
// Pseudo-code — for illustrating observation and invalidation concepts only
class MutableStateImpl<T>(private var _value: T) : MutableState<T> {

    override var value: T
        get() {
            // In reality, reading registers with the Snapshot system
            // so Compose knows this scope depends on this state.
            return _value
        }
        set(newValue) {
            if (_value != newValue) {
                _value = newValue
                // In reality: mark snapshot readers as invalid,
                // leading to scheduled recomposition of dependent scopes.
            }
        }
}
```

### `ViewModel` Integration

This example shows how `StateFlow` interoperates with Compose; it is related to how state changes trigger recomposition, but is separate from `MutableState`'s internal mechanics.

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++  // ✅ Notifies StateFlow collectors
    }
}

@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    val count by viewModel.count.collectAsState()

    Text("Count: $count")  // ✅ Recomposes when StateFlow emits
}
```

**`Flow`:**
1. `viewModel.increment()` changes `_count.value`.
2. `StateFlow` emits a new value.
3. `collectAsState()` receives the value.
4. It updates an internal Compose `State`/`MutableState` instance.
5. The Snapshot system marks dependents as invalid.
6. `Text` is recomposed.

### Subscription Lifecycle

```kotlin
@Composable
fun ConditionalDisplay() {
    var count by remember { mutableStateOf(0) }
    var showDetails by remember { mutableStateOf(false) }

    Column {
        Button(onClick = { showDetails = !showDetails }) {
            Text("Toggle Details")
        }

        if (showDetails) {
            Text("Count: $count")  // ✅ Reads count only while in composition
        }
    }
}
```

Compose automatically manages dependencies and invalidation:
- Dependencies are registered when a composable enters the composition and reads state.
- When it leaves the composition, those dependencies are no longer considered.

---

## Follow-ups

- How does Compose avoid unnecessary recompositions with structural equality checks?
- What happens if MutableState is modified from multiple threads?
- How does remember preserve state across recompositions?
- Can you manually control which Composables subscribe to a state?
- How does derivedStateOf optimize recompositions?

## References

- [[c-compose-state]]
- [[c-recomposition]]

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)

### Advanced (Harder)
- [[q-recomposition-choreographer--android--hard]]