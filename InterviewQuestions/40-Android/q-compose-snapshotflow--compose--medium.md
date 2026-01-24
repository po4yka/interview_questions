---
id: android-747
title: Compose snapshotFlow / snapshotFlow в Compose
aliases:
- Compose snapshotFlow
- snapshotFlow in Compose
- snapshotFlow в Compose
- Converting State to Flow
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
- c-compose-state
- c-compose-recomposition
- q-compose-remember-derived-state--android--medium
- q-compose-side-effects-advanced--android--hard
- q-compose-stability-skippability--android--hard
- q-testing-coroutines-flow--android--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- android/ui-compose
- android/ui-state
- difficulty/medium
sources:
- https://developer.android.com/develop/ui/compose/side-effects#snapshotflow
---
# Вопрос (RU)
> Что такое snapshotFlow в Jetpack Compose и как он преобразует Compose State в Flow?

# Question (EN)
> What is snapshotFlow in Jetpack Compose and how does it convert Compose State to Flow?

---

## Ответ (RU)

### Краткий Вариант

**snapshotFlow** --- это функция, которая преобразует чтение Compose State в холодный (cold) Flow. Она создает мост между реактивной системой Compose (Snapshot system) и kotlinx.coroutines Flow.

### Подробный Вариант

#### Основная Концепция

`snapshotFlow` позволяет "наблюдать" за изменениями Compose State из корутинного контекста. При каждой мутации состояния, которое читается внутри блока `snapshotFlow`, эмитится новое значение в Flow.

```kotlin
// Базовый пример: преобразование scrollState в Flow
@Composable
fun ScrollTracker() {
    val listState = rememberLazyListState()

    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex }
            .distinctUntilChanged()
            .collect { index ->
                analytics.logScroll(index)
            }
    }

    LazyColumn(state = listState) {
        items(100) { Text("Item $it") }
    }
}
```

#### Как Это Работает

1. **Создание снапшота**: при каждой композиции/рекомпозиции Compose создает "снимок" (snapshot) состояния
2. **Отслеживание чтений**: `snapshotFlow` регистрирует все чтения State внутри своего блока
3. **Реакция на изменения**: когда любое отслеживаемое состояние меняется, блок переисчисляется и новое значение эмитится в Flow
4. **Без фильтрации дубликатов по умолчанию**: `snapshotFlow` сам по себе НЕ фильтрует дубликаты --- используйте `.distinctUntilChanged()` при необходимости

#### Типичные Сценарии Использования

**1. Отслеживание позиции скролла**:

```kotlin
@Composable
fun ShowFabOnScroll() {
    val listState = rememberLazyListState()
    var showFab by remember { mutableStateOf(true) }

    LaunchedEffect(listState) {
        var previousIndex = 0
        snapshotFlow { listState.firstVisibleItemIndex }
            .collect { currentIndex ->
                showFab = currentIndex <= previousIndex // скрыть при скролле вниз
                previousIndex = currentIndex
            }
    }

    Scaffold(
        floatingActionButton = {
            AnimatedVisibility(visible = showFab) {
                FloatingActionButton(onClick = { }) { Icon(Icons.Default.Add, null) }
            }
        }
    ) { padding ->
        LazyColumn(state = listState, contentPadding = padding) {
            items(100) { Text("Item $it") }
        }
    }
}
```

**2. Синхронизация с внешними системами**:

```kotlin
@Composable
fun SyncWithDatabase(viewModel: SettingsViewModel) {
    var darkMode by rememberSaveable { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        snapshotFlow { darkMode }
            .debounce(300) // не сохранять при каждом переключении
            .collect { isDark ->
                viewModel.saveDarkModeSetting(isDark)
            }
    }

    Switch(
        checked = darkMode,
        onCheckedChange = { darkMode = it }
    )
}
```

**3. Отслеживание нескольких состояний**:

```kotlin
@Composable
fun MultiStateTracker() {
    var query by remember { mutableStateOf("") }
    var category by remember { mutableStateOf<Category?>(null) }

    LaunchedEffect(Unit) {
        snapshotFlow {
            SearchParams(query = query, category = category)
        }
            .debounce(500)
            .distinctUntilChanged()
            .collect { params ->
                performSearch(params)
            }
    }
}

data class SearchParams(val query: String, val category: Category?)
```

#### snapshotFlow vs derivedStateOf

| Аспект | snapshotFlow | derivedStateOf |
|--------|--------------|----------------|
| Результат | Cold Flow | State<T> |
| Контекст | Внутри LaunchedEffect/корутины | Внутри композиции |
| Использование | Асинхронная обработка | Синхронные вычисления |
| Пример | Аналитика, сохранение в БД | Отфильтрованный список, computed UI |

```kotlin
// derivedStateOf: синхронное производное значение для UI
val showButton by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 5 }
}

// snapshotFlow: асинхронная реакция на изменения
LaunchedEffect(listState) {
    snapshotFlow { listState.firstVisibleItemIndex > 5 }
        .collect { shouldShow ->
            analytics.log("button_visibility", shouldShow)
        }
}
```

#### Важные Ограничения

1. **Только для State, не для произвольных переменных**:
```kotlin
// НЕПРАВИЛЬНО: обычная переменная не отслеживается
var counter = 0
snapshotFlow { counter } // НЕ сработает

// ПРАВИЛЬНО: используйте MutableState
var counter by mutableStateOf(0)
snapshotFlow { counter } // Сработает
```

2. **Не захватывать state вне блока**:
```kotlin
// НЕПРАВИЛЬНО: захвачено вне snapshotFlow
val currentValue = someState.value
snapshotFlow { currentValue } // всегда одно и то же значение

// ПРАВИЛЬНО: читайте внутри блока
snapshotFlow { someState.value }
```

3. **Используйте distinctUntilChanged при необходимости**:
```kotlin
snapshotFlow { listState.firstVisibleItemIndex }
    .distinctUntilChanged() // избежим дубликатов
    .collect { /* ... */ }
```

#### Производительность

- `snapshotFlow` эффективен, так как использует механизм Snapshot invalidation
- Блок snapshotFlow переисчисляется только при изменении отслеживаемых состояний
- Для частых изменений используйте операторы `debounce()` или `throttle()`

---

## Answer (EN)

### Short Version

**snapshotFlow** is a function that converts Compose State reads into a cold Flow. It bridges Compose's reactive system (Snapshot system) with kotlinx.coroutines Flow.

### Detailed Version

#### Core Concept

`snapshotFlow` allows you to "observe" Compose State changes from a coroutine context. Each time any State read inside the `snapshotFlow` block mutates, a new value is emitted to the Flow.

```kotlin
// Basic example: converting scrollState to Flow
@Composable
fun ScrollTracker() {
    val listState = rememberLazyListState()

    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex }
            .distinctUntilChanged()
            .collect { index ->
                analytics.logScroll(index)
            }
    }

    LazyColumn(state = listState) {
        items(100) { Text("Item $it") }
    }
}
```

#### How It Works

1. **Snapshot creation**: on each composition/recomposition, Compose creates a "snapshot" of state
2. **Read tracking**: `snapshotFlow` registers all State reads inside its block
3. **Change reaction**: when any tracked state changes, the block is re-evaluated and the new value is emitted
4. **Not distinct by default**: `snapshotFlow` does NOT filter duplicates itself --- use `.distinctUntilChanged()` when needed

#### Common Use Cases

**1. Tracking scroll position**:

```kotlin
@Composable
fun ShowFabOnScroll() {
    val listState = rememberLazyListState()
    var showFab by remember { mutableStateOf(true) }

    LaunchedEffect(listState) {
        var previousIndex = 0
        snapshotFlow { listState.firstVisibleItemIndex }
            .collect { currentIndex ->
                showFab = currentIndex <= previousIndex // hide on scroll down
                previousIndex = currentIndex
            }
    }

    Scaffold(
        floatingActionButton = {
            AnimatedVisibility(visible = showFab) {
                FloatingActionButton(onClick = { }) { Icon(Icons.Default.Add, null) }
            }
        }
    ) { padding ->
        LazyColumn(state = listState, contentPadding = padding) {
            items(100) { Text("Item $it") }
        }
    }
}
```

**2. Syncing with external systems**:

```kotlin
@Composable
fun SyncWithDatabase(viewModel: SettingsViewModel) {
    var darkMode by rememberSaveable { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        snapshotFlow { darkMode }
            .debounce(300) // don't save on every toggle
            .collect { isDark ->
                viewModel.saveDarkModeSetting(isDark)
            }
    }

    Switch(
        checked = darkMode,
        onCheckedChange = { darkMode = it }
    )
}
```

**3. Tracking multiple states**:

```kotlin
@Composable
fun MultiStateTracker() {
    var query by remember { mutableStateOf("") }
    var category by remember { mutableStateOf<Category?>(null) }

    LaunchedEffect(Unit) {
        snapshotFlow {
            SearchParams(query = query, category = category)
        }
            .debounce(500)
            .distinctUntilChanged()
            .collect { params ->
                performSearch(params)
            }
    }
}

data class SearchParams(val query: String, val category: Category?)
```

#### snapshotFlow vs derivedStateOf

| Aspect | snapshotFlow | derivedStateOf |
|--------|--------------|----------------|
| Result | Cold Flow | State<T> |
| Context | Inside LaunchedEffect/coroutine | Inside composition |
| Use case | Async handling | Synchronous computations |
| Example | Analytics, save to DB | Filtered list, computed UI |

```kotlin
// derivedStateOf: synchronous derived value for UI
val showButton by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 5 }
}

// snapshotFlow: async reaction to changes
LaunchedEffect(listState) {
    snapshotFlow { listState.firstVisibleItemIndex > 5 }
        .collect { shouldShow ->
            analytics.log("button_visibility", shouldShow)
        }
}
```

#### Important Constraints

1. **Only for State, not arbitrary variables**:
```kotlin
// WRONG: regular variable is not tracked
var counter = 0
snapshotFlow { counter } // Will NOT work

// CORRECT: use MutableState
var counter by mutableStateOf(0)
snapshotFlow { counter } // Works
```

2. **Read state inside the block**:
```kotlin
// WRONG: captured outside snapshotFlow
val currentValue = someState.value
snapshotFlow { currentValue } // always the same value

// CORRECT: read inside the block
snapshotFlow { someState.value }
```

3. **Use distinctUntilChanged when needed**:
```kotlin
snapshotFlow { listState.firstVisibleItemIndex }
    .distinctUntilChanged() // avoid duplicates
    .collect { /* ... */ }
```

#### Performance

- `snapshotFlow` is efficient as it uses Compose's Snapshot invalidation mechanism
- The snapshotFlow block is only re-evaluated when tracked states change
- For frequent changes, use `debounce()` or `throttle()` operators

---

## Дополнительные Вопросы (Follow-ups, RU)

- Как snapshotFlow взаимодействует с Compose Snapshot system?
- В чём разница между snapshotFlow и produceState?
- Как правильно отменять Flow, созданный через snapshotFlow?
- Можно ли использовать snapshotFlow вне Compose (в чистом Kotlin)?
- Как отлаживать проблемы с snapshotFlow, когда эмиссии не происходят?

## Follow-ups

- How does snapshotFlow interact with the Compose Snapshot system?
- What is the difference between snapshotFlow and produceState?
- How to properly cancel a Flow created via snapshotFlow?
- Can snapshotFlow be used outside Compose (in pure Kotlin)?
- How to debug issues with snapshotFlow when emissions don't occur?

## Ссылки (RU)

- [[c-compose-state]]
- [[c-compose-recomposition]]
- https://developer.android.com/develop/ui/compose/side-effects#snapshotflow
- https://developer.android.com/develop/ui/compose/state

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- https://developer.android.com/develop/ui/compose/side-effects#snapshotflow
- https://developer.android.com/develop/ui/compose/state

## Связанные Вопросы (RU)

### Предпосылки (проще)

- [[q-compose-remember-derived-state--android--medium]] --- основы remember и derivedStateOf

### Связанные (тот же уровень)

- [[q-compose-side-effects-advanced--android--hard]] --- LaunchedEffect и другие эффекты
- [[q-testing-coroutines-flow--android--hard]] --- тестирование Flow

### Продвинутые (сложнее)

- [[q-compose-slot-table-recomposition--android--hard]] --- внутренняя механика Compose

## Related Questions

### Prerequisites (Easier)

- [[q-compose-remember-derived-state--android--medium]] --- remember and derivedStateOf basics

### Related (Same Level)

- [[q-compose-side-effects-advanced--android--hard]] --- LaunchedEffect and other effects
- [[q-testing-coroutines-flow--android--hard]] --- testing Flow

### Advanced (Harder)

- [[q-compose-slot-table-recomposition--android--hard]] --- Compose internal mechanics
