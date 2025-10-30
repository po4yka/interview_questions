---
id: 20251012-1227163
title: "How MutableState Notifies / Как MutableState уведомляет"
aliases: [MutableState notifications, MutableState уведомления, Snapshot system]
topic: android
subtopics: [ui-compose, ui-state, architecture-mvvm]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-28
tags: [android/ui-compose, android/ui-state, android/architecture-mvvm, difficulty/medium, jetpack-compose, mutablestate, observer-pattern, recomposition, snapshot-system, state-management]
moc: moc-android
related: [c-compose-state, c-recomposition, q-recomposition-choreographer--android--hard]
sources: []
date created: Tuesday, October 28th 2025, 9:34:15 am
date modified: Thursday, October 30th 2025, 12:48:18 pm
---

# Вопрос (RU)
> Как MutableState уведомляет о том, что он изменился?

# Question (EN)
> How does MutableState notify that it has changed?

---

## Ответ (RU)

**MutableState** использует **Observer pattern** с **Snapshot system** для автоматического уведомления подписчиков об изменениях.

### Механизм работы

**1. Подписка (Read Phase)**
Composable автоматически подписывается при **чтении** state:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    // Чтение count - автоматическая подписка
    Text("Count: $count")  // ✅ Подписка на count

    Button(onClick = { count++ }) {
        Text("Increment")
    }
}
```

**2. Уведомление (Write Phase)**
При изменении значения:
1. `count++` записывает новое значение
2. `MutableState` обнаруживает изменение
3. Уведомляются все подписчики
4. Compose планирует рекомпозицию
5. **Только** `Text("Count: $count")` перерисовывается

### Система Snapshot

**Snapshot** - неизменяемый снимок всех состояний в конкретный момент:

```kotlin
// Snapshot 1: count = 0
Snapshot { count = 0 }

// User clicks increment

// Snapshot 2: count = 1
Snapshot { count = 1 }
```

**Преимущества:**
- **Изоляция** - чтения видят консистентное состояние
- **Потокобезопасность** - несколько потоков могут безопасно читать
- **Откат** - можно отменить изменения

### Гранулярная рекомпозиция

Только Composable, которые **читают** изменённое состояние, перерисовываются:

```kotlin
@Composable
fun Screen() {
    var name by remember { mutableStateOf("Alice") }
    var age by remember { mutableStateOf(25) }

    Column {
        Text("Name: $name")  // ✅ Рекомпозиция только при изменении name
        Text("Age: $age")    // ✅ Рекомпозиция только при изменении age

        Button(onClick = { age++ }) {
            Text("Increment Age")
        }
    }
}
```

**При клике на кнопку:**
- `age++` уведомляет подписчиков
- Только `Text("Age: $age")` перерисовывается
- `Text("Name: $name")` **НЕ** перерисовывается

### Упрощённая реализация

```kotlin
class MutableStateImpl<T>(private var _value: T) : MutableState<T> {
    private val subscribers = mutableListOf<() -> Unit>()

    override var value: T
        get() {
            Snapshot.registerRead(this)  // Регистрация подписчика
            return _value
        }
        set(newValue) {
            if (_value != newValue) {
                _value = newValue
                notifySubscribers()  // Уведомление
            }
        }

    private fun notifySubscribers() {
        subscribers.forEach { it.invoke() }
    }
}
```

### Интеграция с ViewModel

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++  // ✅ Уведомляет коллекторов
    }
}

@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    val count by viewModel.count.collectAsState()

    Text("Count: $count")  // ✅ Рекомпозиция при изменении StateFlow
}
```

**Поток:**
1. `viewModel.increment()` изменяет `_count.value`
2. `StateFlow` эмитит новое значение
3. `collectAsState()` получает значение
4. Обновляет внутренний `MutableState`
5. `MutableState` уведомляет подписчиков
6. `Text` перерисовывается

### Жизненный цикл подписок

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
            Text("Count: $count")  // ✅ Подписка только когда видимо
        }
    }
}
```

Compose автоматически управляет подписками:
- Подписка при входе в композицию
- Отписка при выходе из композиции

---

## Answer (EN)

**MutableState** uses the **Observer pattern** with Compose's **Snapshot system** to automatically notify subscribers about changes.

### How It Works

**1. Subscription (Read Phase)**
Composables automatically subscribe when they **read** the state:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    // Reading count subscribes this Text
    Text("Count: $count")  // ✅ Subscribes to count

    Button(onClick = { count++ }) {
        Text("Increment")
    }
}
```

**2. Notification (Write Phase)**
When the value is updated:
1. `count++` writes new value
2. `MutableState` detects the change
3. All subscribers are notified
4. Compose schedules recomposition
5. **Only** `Text("Count: $count")` recomposes

### Snapshot System

A **Snapshot** is an immutable view of all state at a specific point in time:

```kotlin
// Snapshot 1: count = 0
Snapshot { count = 0 }

// User clicks increment

// Snapshot 2: count = 1
Snapshot { count = 1 }
```

**Benefits:**
- **Isolation** - reads always see consistent state
- **Thread-safety** - multiple threads can read safely
- **Rollback** - can discard changes if needed

### Granular Recomposition

Only Composables that **read** the changed state are recomposed:

```kotlin
@Composable
fun Screen() {
    var name by remember { mutableStateOf("Alice") }
    var age by remember { mutableStateOf(25) }

    Column {
        Text("Name: $name")  // ✅ Recomposes only when name changes
        Text("Age: $age")    // ✅ Recomposes only when age changes

        Button(onClick = { age++ }) {
            Text("Increment Age")
        }
    }
}
```

**When user clicks the button:**
- `age++` notifies subscribers
- Only `Text("Age: $age")` recomposes
- `Text("Name: $name")` is **NOT** recomposed

### Simplified Implementation

```kotlin
class MutableStateImpl<T>(private var _value: T) : MutableState<T> {
    private val subscribers = mutableListOf<() -> Unit>()

    override var value: T
        get() {
            Snapshot.registerRead(this)  // Register subscriber
            return _value
        }
        set(newValue) {
            if (_value != newValue) {
                _value = newValue
                notifySubscribers()  // Notify
            }
        }

    private fun notifySubscribers() {
        subscribers.forEach { it.invoke() }
    }
}
```

### ViewModel Integration

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++  // ✅ Notifies collectors
    }
}

@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    val count by viewModel.count.collectAsState()

    Text("Count: $count")  // ✅ Recomposes when StateFlow emits
}
```

**Flow:**
1. `viewModel.increment()` changes `_count.value`
2. `StateFlow` emits new value
3. `collectAsState()` receives value
4. Updates internal `MutableState`
5. `MutableState` notifies subscribers
6. `Text` recomposes

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
            Text("Count: $count")  // ✅ Subscribes only when visible
        }
    }
}
```

Compose automatically manages subscriptions:
- Subscribe when Composable enters composition
- Unsubscribe when Composable leaves composition

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
- [[c-snapshot-system]]
- [[moc-android]]

## Related Questions

### Prerequisites (Easier)
- [[q-compose-state-basics--android--easy]]
- [[q-remember-mutablestateof--android--easy]]

### Related (Same Level)
- [[q-compose-state--android--medium]]
- [[q-derivedstateof-optimization--android--medium]]

### Advanced (Harder)
- [[q-recomposition-choreographer--android--hard]]
- [[q-snapshot-isolation--android--hard]]
