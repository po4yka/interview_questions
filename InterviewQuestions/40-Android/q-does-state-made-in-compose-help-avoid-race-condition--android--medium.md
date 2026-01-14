---
id: android-444
title: Does State in Compose Help Avoid Race Conditions / Помогает ли State в Compose
  избежать состояния гонки
aliases:
- Compose State Thread Safety
- Does State Made In Compose Help Avoid Race Condition
- Thread Safety в Compose State
- Помогает ли State в Compose избежать состояния гонки
topic: android
subtopics:
- ui-compose
- ui-state
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-recomposition
- c-compose-state
- c-jetpack-compose
- c-recomposition
- q-compose-core-components--android--medium
- q-derived-state-snapshot-system--android--hard
- q-how-does-jetpackcompose-work--android--medium
- q-state-hoisting-compose--android--medium
created: 2025-10-20
updated: 2025-11-10
anki_cards:
- slug: android-444-0-en
  language: en
  anki_id: 1768367860431
  synced_at: '2026-01-14T09:17:53.196292'
- slug: android-444-0-ru
  language: ru
  anki_id: 1768367860456
  synced_at: '2026-01-14T09:17:53.198903'
tags:
- android/ui-compose
- android/ui-state
- difficulty/medium
sources:
- https://developer.android.com/jetpack/compose/state
---
# Вопрос (RU)
> Помогает ли State в Compose избежать состояния гонки?

# Question (EN)
> Does State Made In Compose Help Avoid Race Condition?

---

## Ответ (RU)

**Нет**, `MutableState` в `Compose` сам по себе не гарантирует отсутствия race condition и не является универсальным thread-safe примитивом вроде `Atomic*` или `Mutex`. Он построен на системе snapshot-состояния, которая обеспечивает согласованность чтения/записи по своим правилам (snapshot isolation, детекция конфликтов, единая модель наблюдения), но это **не** означает, что можно бездумно изменять одно и то же состояние из разных потоков без соблюдения этих правил. При некорректном параллельном доступе (в обход snapshot-API или без потоковой дисциплины) возможно неконсистентное наблюдаемое состояние, потеря обновлений и исключения.

Важно различать:
- snapshot-состояние (включая `MutableState`) разработано так, чтобы быть безопасным для использования из разных потоков при соблюдении правил snapshot-системы;
- это не отменяет необходимости продуманной архитектуры и избежания логических race condition.

### Основные Проблемы

**1. MutableState не является общим thread-safe примитивом для произвольных гонок**

**Проблема:**

`MutableState` не предназначен как универсальный контейнер для конкурентных обновлений произвольного бизнес-кода (как `AtomicLong`/`ConcurrentHashMap`). Он интегрирован с snapshot-системой Compose, которая ожидает, что изменения будут происходить либо:
- в рамках согласованного контекста (типичный случай — main/UI dispatcher, обеспечивающий последовательные изменения UI-состояния), либо
- через корректные snapshot-операции (begin/apply), которые учитывают конкурентные изменения.

Если одновременно и без координации менять одно и то же состояние, игнорируя правила snapshot-системы, можно получить:
- **Потерю логических обновлений** — последнее записанное значение побеждает (last write wins), что может не соответствовать ожидаемой семантике;
- **Некорректное наблюдаемое состояние** — разные наблюдатели/компонуемые могут в разные моменты видеть несовместимые комбинации значений;
- **Ошибки snapshot-системы** — вплоть до `IllegalStateException` при нарушении её инвариантов.

Важно: это не «магически защищённый» от всех гонок тип. Он даёт модель snapshot-согласованности, а ответственность за корректный дизайн потоков и инвариантов остаётся на разработчике.

**Решение:**

- Для UI-состояния обновлять `MutableState` из одного, предсказуемого контекста (как правило, main dispatcher),
- Либо использовать официальные snapshot-утилиты (snapshot transactions, `snapshotFlow` и т.п.) и/или дополнительные примитивы синхронизации при сложных межпоточных изменениях.

Практический и рекомендуемый путь для UI:
- Выполнять тяжёлую работу в фоновых потоках;
- Публиковать результат обратно в UI через main dispatcher или слой, гарантирующий согласованные обновления (`ViewModel` + `Flow`/`StateFlow`).

```kotlin
// ❌ НЕУДАЧНО - "сырые" фоновые потоки без понимания snapshot-правил
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        Thread {
            // ⚠️ Риск: запись в state вне структурированных корутин и без учёта snapshot-модели
            count++
        }.start()
    }) { Text("Increment: $count") }
}

// ✅ ЛУЧШЕ - все изменения происходят из одного (UI) контекста
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        count++
    }) { Text("Increment: $count") }
}

// ✅ ЛУЧШЕ - асинхронная работа в фоне, публикация результата в UI-контексте
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            // Обновление snapshot-состояния из согласованного (обычно main) контекста
            count = result
        }
    }) { Text("Count: $count") }
}
```

**2. Доступ из background потоков**

**Проблема:**

Сам по себе факт выполнения в background dispatcher не является запрещённым для snapshot-состояния, но:
- произвольные изменения из фоновых потоков, особенно из "сырых" `Thread` или несогласованных `CoroutineScope(Dispatchers.IO)`, усложняют соблюдение правил snapshot-системы и понимание порядка обновлений;
- при неаккуратном использовании можно получить логические race condition (например, несколько конкурентных `count++` без атомарности на уровне бизнес-смысла).

Проявления:
- пропущенные или неожиданно упорядоченные recomposition;
- логически некорректное состояние при last-write-wins;
- ошибки snapshot-системы при нарушении контракта.

**Важно:** snapshot-система поддерживает многопоточное использование через свои API (snapshot transactions и т.д.). Это продвинутый сценарий; для обычного UI-кода предпочтительна простая модель: фон → согласованный контекст → обновление состояния.

**Решение (рекомендуемый путь для UI-кода):**

Использовать `rememberCoroutineScope()` или scope `ViewModel` и переключаться на `Dispatchers.IO` только для фоновой работы, возвращая результат в UI-контекст перед изменением состояния (или использовать snapshot-aware операции).

```kotlin
// ❌ НЕУДАЧНО - использование отдельного IO-scope и запись в state без явной дисциплины
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            // ⚠️ Потенциально неконтролируемая запись: нет привязки к жизненному циклу и UI-контексту
            count = heavyCalculation()
        }
    }) { Text("Calculate: $count") }
}

// ✅ ЛУЧШЕ - работа в фоне, обновление из согласованного контекста
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            count = result
        }
    }) { Text("Calculate: $count") }
}

// ✅ ЛУЧШЕ - альтернатива с LaunchedEffect
@Composable
fun SafeAsyncCounterWithEffect() {
    var count by remember { mutableStateOf(0) }
    var trigger by remember { mutableStateOf(0) }

    LaunchedEffect(trigger) {
        val result = withContext(Dispatchers.IO) {
            heavyCalculation()
        }
        count = result
    }

    Button(onClick = { trigger++ }) {
        Text("Calculate: $count")
    }
}
```

**3. Shared state между компонентами**

**Проблема:**

Когда несколько `@Composable` напрямую изменяют один и тот же `MutableState`, чаще всего это проблема архитектуры, а не низкоуровневого data race:
- **Нарушение Single Source of Truth** — неочевидно, кто владеет состоянием;
- **Сложность отладки** — трудно отследить, кто и когда изменил значение;
- `remember { mutableStateOf() }` не переживает конфигурационные изменения;
- при появлении реальной конкуренции (несколько потоков/корутин без дисциплины) возникают классические race condition на уровне бизнес-логики.

Важно: два обработчика кликов в одном UI-потоке, последовательно меняющих одно значение, сами по себе не создают data race. Проблема — когда состояние разделяется без чёткого владельца или изменяется конкурентно.

**Решение:**

Использовать `ViewModel` с `StateFlow`/`MutableStateFlow` или другим чётко определённым слоем состояния как единый источник истины для shared state. `StateFlow` предоставляет потокобезопасные обновления и хорошо интегрируется с Compose.

```kotlin
// ❌ НЕУДАЧНО - общий mutable state в UI-слое без явного владельца
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }

    ChildComponent1(sharedState) {
        sharedState++
    }
    ChildComponent2(sharedState) {
        sharedState++
    }
}

// ✅ ЛУЧШЕ - ViewModel как единый источник истины
@Composable
fun ParentComponent(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}

class SharedViewModel : ViewModel() {
    private val _state = MutableStateFlow(0)
    val state: StateFlow<Int> = _state.asStateFlow()

    fun increment() {
        _state.update { it + 1 } // Потокобезопасное атомарное инкрементирование на уровне StateFlow
    }
}

// ✅ ПРИМЕР - использование того же StateFlow-источника
@Composable
fun ParentComponentWithFlow(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}
```

### Решения И Паттерны Потокобезопасности

**1. Корутины с согласованным контекстом (обычно Main/UI)**

Рекомендуется выполнять фоновые операции в соответствующих диспетчерах и обновлять UI-состояние из одного согласованного контекста (часто main dispatcher), либо использовать snapshot-aware операции.

```kotlin
@Composable
fun SafeAsyncComponent() {
    var state by remember { mutableStateOf(initialValue) }
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                performBackgroundWork()
            }
            state = result
        }
    }) {
        Text("Update")
    }
}
```

**2. `ViewModel` с `StateFlow` для shared state**

`StateFlow` и `MutableStateFlow` обеспечивают потокобезопасные, наблюдаемые обновления состояния.

```kotlin
class MyViewModel<T>(initialValue: T) : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state: StateFlow<T> = _state.asStateFlow()

    fun updateState(newValue: T) {
        _state.value = newValue
    }

    fun incrementInt(by: Int = 1) {
        // Только для Int-состояний; пример использования update для атомарной логической операции
        (_state as? MutableStateFlow<Int>)?.update { it + by }
    }
}

@Composable
fun MyScreen(viewModel: MyViewModel<SomeType> = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    // Безопасное использование shared state
}
```

**3. SnapshotFlow для интеграции со `Flow`**

Для наблюдения за snapshot-состоянием в корутинах используйте `snapshotFlow`:

```kotlin
@Composable
fun ComponentWithSnapshotFlow() {
    var count by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        snapshotFlow { count }
            .filter { it > 10 }
            .collect { value ->
                performAction(value)
            }
    }
}
```

**4. Классическая синхронизация (Mutex/Channel) для сложных случаев**

Для сценариев с реальными конкурентными писателями используйте примитивы синхронизации в бизнес-слое:

```kotlin
class ThreadSafeCounter {
    private val mutex = Mutex()
    private var _count = 0

    suspend fun increment() {
        mutex.withLock {
            _count++
        }
    }

    suspend fun getCount(): Int = mutex.withLock { _count }
}

@Composable
fun ComponentWithMutex(viewModel: ThreadSafeCounterViewModel = hiltViewModel()) {
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            viewModel.increment()
        }
    }) {
        Text("Increment")
    }
}
```

### Лучшие Практики И Рекомендации

**Архитектурные решения:**

- Использовать `MutableState` для локального UI-состояния и обновлять его из одного согласованного контекста или через snapshot-aware операции;
- Для разделяемого/долгоживущего состояния использовать `ViewModel` + `StateFlow`/`Flow` как единый источник истины;
- Не писать в `MutableState` из произвольных фоновых потоков/"сырых" `Thread`, не понимая правил snapshot-системы и жизненного цикла;
- Использовать `rememberCoroutineScope()` и `ViewModel` scope для корректного управления корутинами.

**Оптимизация производительности:**

- Минимизировать количество обновлений состояния, по возможности объединять;
- Использовать `derivedStateOf` для производных значений, чтобы снизить количество recomposition;
- Выполнять тяжёлую работу вне UI-диспетчера, возвращая в UI только применение результата.

**Когда использовать что:**

- `MutableState`: локальное состояние одного composable / небольшого дерева;
- `StateFlow` в `ViewModel`: разделяемое и долгоживущее состояние между несколькими экранами/компонентами;
- `Flow` + `collectAsState()`: реактивные внешние источники (сеть, БД и т.п.);
- `snapshotFlow`: мост между snapshot-состоянием и `Flow`.

### Типичные Ошибки

**Проблема 1: Изменение state только в фоновом контексте внутри LaunchedEffect**

```kotlin
// ❌ НЕУДАЧНО
LaunchedEffect(Unit) {
    withContext(Dispatchers.IO) {
        state = fetchData() // Запись в snapshot-состояние из фонового контекста
    }
}

// ✅ ЛУЧШЕ
LaunchedEffect(Unit) {
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }
    state = data
}
```

**Проблема 2: Нескоординированные логические записи в shared state**

```kotlin
// ❌ НЕУДАЧНО
var counter by remember { mutableStateOf(0) }
Button1 { counter++ }
Button2 { counter++ }
// В одном UI-потоке это не низкоуровневый data race, но размывает ответственность и усложняет масштабирование.

// ✅ ЛУЧШЕ
val viewModel: CounterViewModel = hiltViewModel()
val counter by viewModel.counter.collectAsState()
Button1 { viewModel.increment() }
Button2 { viewModel.increment() }
```

---

## Answer (EN)

**No**, `MutableState` in Compose does not by itself prevent race conditions and is not a universal thread-safe primitive like `Atomic*` or `Mutex`. It is built on the snapshot state system, which provides snapshot isolation, conflict detection/merge semantics, and a consistent observation model. However, this does **not** mean you can freely mutate the same state from multiple threads without respecting snapshot rules. Incorrect concurrent usage (bypassing snapshot APIs, using ad-hoc threads, or violating lifecycle/ownership) can still lead to logically inconsistent results, lost updates (from your business-logic point of view), or runtime errors.

Key distinction:
- snapshot state (including `MutableState`) is designed to be safely usable from multiple threads under the snapshot model;
- you are still responsible for avoiding logical race conditions and maintaining clear ownership.

### Main Issues

**1. MutableState is not a general-purpose concurrency primitive**

**Problem:**

`MutableState` is not meant to be used like low-level concurrent containers (e.g., `AtomicLong`, `ConcurrentHashMap`) to coordinate arbitrary concurrent writers. It is tightly integrated with Compose's snapshot system, which expects mutations to happen either:
- from a coordinated context (commonly the main/UI dispatcher for UI state), or
- via explicit snapshot operations that understand concurrent changes.

If you update the same state concurrently without coordination or outside the snapshot model, you may observe:
- **Lost logical updates** — last write wins semantics may break your intended invariants;
- **Inconsistent observations** — different readers/composables may temporarily see incompatible combinations of values;
- **Snapshot errors** — including `IllegalStateException` when invariants are violated.

It is not "magically race-free"; it provides a specific consistency model, and you must design around it.

**Solution:**

- For UI state, update `MutableState` from a single predictable context (commonly the main dispatcher), or
- Use official snapshot utilities and/or synchronization primitives for complex concurrent updates.

A practical recommended pattern for UI:
- Execute heavy work on background dispatchers;
- Publish results to the UI via a confined context (main dispatcher, `ViewModel` with `Flow`/`StateFlow`, etc.).

```kotlin
// ❌ BAD - ad-hoc background thread writing into state without structured concurrency
@Composable
fun UnsafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        Thread {
            // ⚠️ Risky: mutation from a raw thread, no lifecycle or structured snapshot usage
            count++
        }.start()
    }) { Text("Increment: $count") }
}

// ✅ GOOD - all updates from a single UI context
@Composable
fun SafeCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        count++
    }) { Text("Increment: $count") }
}

// ✅ GOOD - background work, result applied from a coordinated (UI) context
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            count = result
        }
    }) { Text("Count: $count") }
}
```

**2. Background thread access**

**Problem:**

Using background dispatchers is not inherently forbidden for snapshot state, but:
- ad-hoc background writes (e.g., `CoroutineScope(Dispatchers.IO)` not tied to lifecycle, or raw threads) make it easy to violate snapshot expectations or lose track of ordering;
- multiple concurrent writers performing non-atomic read-modify-write operations (like `count++`) can cause logical race conditions, even if the underlying snapshot mechanism remains consistent.

Typical symptoms:
- surprising recomposition timing/order;
- business-logic invariants being broken due to last-write-wins;
- snapshot-related exceptions when rules are violated.

**Note:** The snapshot system supports multi-threaded usage via its APIs (transactions, `snapshotFlow`, etc.), but that is an advanced topic. For normal app code, prefer: background work → coordinated context → state update.

**Solution (recommended for typical UI code):**

Use `rememberCoroutineScope()` or `ViewModel` scopes; switch to `Dispatchers.IO` only for heavy work and apply the final state changes from a well-defined context (usually main/UI) or via proper snapshot operations.

```kotlin
// ❌ BAD - separate IO scope writing to state without lifecycle/snapshot discipline
@Composable
fun UnsafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = {
        CoroutineScope(Dispatchers.IO).launch {
            // ⚠️ Potentially unsafe: detached from lifecycle, easy to mis-order or leak
            count = heavyCalculation()
        }
    }) { Text("Calculate: $count") }
}

// ✅ GOOD - compute in background, update from a coordinated context
@Composable
fun SafeAsyncCounter() {
    var count by remember { mutableStateOf(0) }
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                heavyCalculation()
            }
            count = result
        }
    }) { Text("Calculate: $count") }
}

// ✅ GOOD - alternative using LaunchedEffect
@Composable
fun SafeAsyncCounterWithEffect() {
    var count by remember { mutableStateOf(0) }
    var trigger by remember { mutableStateOf(0) }

    LaunchedEffect(trigger) {
        val result = withContext(Dispatchers.IO) {
            heavyCalculation()
        }
        count = result
    }

    Button(onClick = { trigger++ }) {
        Text("Calculate: $count")
    }
}
```

**3. Shared state between components**

**Problem:**

When multiple composables directly mutate the same `MutableState`, it's primarily an architectural and ownership smell rather than an automatic low-level data race:
- **Single Source of Truth violation** — unclear ownership of state;
- **Harder debugging** — many writers, no clear contract;
- `remember { mutableStateOf() }` does not survive configuration changes;
- if true concurrency is introduced (multiple threads/coroutines mutating shared state without discipline) you do get genuine race conditions at the logic level.

Note: Two click handlers incrementing the same state on the main thread is not, by itself, a data race. Issues arise with poor separation of concerns or actual concurrency.

**Solution:**

Use a `ViewModel` with `StateFlow` / `MutableStateFlow` (or equivalent) as the single source of truth for shared state. `StateFlow` is thread-safe and integrates naturally with Compose.

```kotlin
// ❌ BAD - shared mutable state in UI layer without clear owner
@Composable
fun ParentComponent() {
    var sharedState by remember { mutableStateOf(0) }

    ChildComponent1(sharedState) {
        sharedState++
    }
    ChildComponent2(sharedState) {
        sharedState++
    }
}

// ✅ GOOD - ViewModel as the single source of truth
@Composable
fun ParentComponent(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}

class SharedViewModel : ViewModel() {
    private val _state = MutableStateFlow(0)
    val state: StateFlow<Int> = _state.asStateFlow()

    fun increment() {
        _state.update { it + 1 }
    }
}

// ✅ GOOD - Flow-based reactive updates (same StateFlow source)
@Composable
fun ParentComponentWithFlow(viewModel: SharedViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    ChildComponent1(state) { viewModel.increment() }
    ChildComponent2(state) { viewModel.increment() }
}
```

### Thread Safety Solutions and Patterns

**1. Coroutines with a consistent context (usually Main/UI)**

Use background dispatchers for heavy work and apply UI state updates from a single coordinated context (often main/UI), or from snapshot-aware code.

```kotlin
@Composable
fun SafeAsyncComponent() {
    var state by remember { mutableStateOf(initialValue) }
    val scope = rememberCoroutineScope()

    Button(onClick = {
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                performBackgroundWork()
            }
            state = result
        }
    }) {
        Text("Update")
    }
}
```

**2. `ViewModel` with `StateFlow` for shared state**

`StateFlow` / `MutableStateFlow` provide thread-safe, observable state updates.

```kotlin
class MyViewModel<T>(initialValue: T) : ViewModel() {
    private val _state = MutableStateFlow(initialValue)
    val state: StateFlow<T> = _state.asStateFlow()

    fun updateState(newValue: T) {
        _state.value = newValue
    }

    fun incrementInt(by: Int = 1) {
        // Example of using update for atomic semantics on Int state
        (_state as? MutableStateFlow<Int>)?.update { it + by }
    }
}

@Composable
fun MyScreen(viewModel: MyViewModel<SomeType> = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    // Safe usage of shared state
}
```

**3. SnapshotFlow for integrating snapshot state with `Flow`**

Use `snapshotFlow` to observe snapshot state in coroutine/Flow pipelines:

```kotlin
@Composable
fun ComponentWithSnapshotFlow() {
    var count by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        snapshotFlow { count }
            .filter { it > 10 }
            .collect { value ->
                performAction(value)
            }
    }
}
```

**4. Mutex / Channels for complex concurrency**

For complex scenarios with multiple true concurrent writers, use explicit synchronization in your domain layer:

```kotlin
class ThreadSafeCounter {
    private val mutex = Mutex()
    private var _count = 0

    suspend fun increment() {
        mutex.withLock {
            _count++
        }
    }

    suspend fun getCount(): Int = mutex.withLock { _count }
}

@Composable
fun ComponentWithMutex(viewModel: ThreadSafeCounterViewModel = hiltViewModel()) {
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            viewModel.increment()
        }
    }) {
        Text("Increment")
    }
}
```

### Best Practices and Recommendations

**Architectural decisions:**

- Use `MutableState` for local UI state; mutate it from a single coordinated context or via snapshot-aware operations;
- Use `ViewModel` + `StateFlow`/`Flow` for shared or long-lived state as the single source of truth;
- Avoid writing into `MutableState` from arbitrary background threads/raw threads without understanding snapshot rules and lifecycle;
- Use `rememberCoroutineScope()` and `ViewModel` scopes for proper coroutine management.

**Performance optimization:**

- Minimize the frequency of state writes; batch where reasonable;
- Use `derivedStateOf` for computed values to avoid unnecessary recompositions;
- Keep heavy work off the main dispatcher; only apply results on the coordinated/UI context.

**When to use what:**

- `MutableState`: local state within a single composable or small tree;
- `StateFlow` in `ViewModel`: shared state across screens/components;
- `Flow` + `collectAsState()`: reactive external sources (network, DB, etc.);
- `snapshotFlow`: bridging snapshot state to `Flow`.

### Common Pitfalls

**Problem 1: Updating state only from a background context inside LaunchedEffect**

```kotlin
// ❌ BAD
LaunchedEffect(Unit) {
    withContext(Dispatchers.IO) {
        state = fetchData() // Writing into snapshot state from a background context
    }
}

// ✅ GOOD
LaunchedEffect(Unit) {
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }
    state = data
}
```

**Problem 2: Uncoordinated logical writers to shared state**

```kotlin
// ❌ BAD
var counter by remember { mutableStateOf(0) }
Button1 { counter++ }
Button2 { counter++ }
// While single-threaded here, this blurs responsibilities and scales poorly.

// ✅ GOOD
val viewModel: CounterViewModel = hiltViewModel()
val counter by viewModel.counter.collectAsState()
Button1 { viewModel.increment() }
Button2 { viewModel.increment() }
```

---

## Дополнительные Вопросы (RU)

- Когда использовать `StateFlow` vs `MutableState` в архитектуре на основе Compose?
- Как snapshot-система в Compose концептуально обрабатывает конкурентные изменения?
- Как правильно обновлять состояние Compose из фоновых корутин, не нарушая правила snapshot-системы?
- Как выстроить разделяемое состояние с `ViewModel` и `StateFlow`, чтобы избежать логических гонок?
- Как отлаживать и обнаруживать race condition, связанные с обновлениями состояния в Compose?

## Follow-ups

- When to use `StateFlow` vs `MutableState` in Compose-based architecture?
- How does the snapshot system in Compose handle concurrent modifications conceptually?
- How to correctly update Compose state from background coroutines without violating snapshot rules?
- How to structure shared state with `ViewModel` and `StateFlow` to avoid logical race conditions?
- How to debug and detect race conditions related to Compose state updates?

## Ссылки (RU)

- [Документация по состоянию в Compose](https://developer.android.com/jetpack/compose/state)
- [`StateFlow` и `SharedFlow`](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Hoisting состояния в Compose](https://developer.android.com/jetpack/compose/state-hoisting)
- [Потокобезопасность в Kotlin](https://kotlinlang.org/docs/thread-safety.html)
- [Диспетчеры корутин](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

## References

- [Compose State Documentation](https://developer.android.com/jetpack/compose/state)
- [`StateFlow` and `SharedFlow`](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Compose State Hoisting](https://developer.android.com/jetpack/compose/state-hoisting)
- [Thread Safety in Kotlin](https://kotlinlang.org/docs/thread-safety.html)
- [Coroutines Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

## Связанные Вопросы (RU)

### Предпосылки / Концепты

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Связанные (того Же уровня)

- [[q-derived-state-snapshot-system--android--hard]]

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Related (Same Level)

- [[q-derived-state-snapshot-system--android--hard]]
