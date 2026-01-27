---
id: kotlin-flow-003
title: Flow Operators / Операторы Flow
aliases:
- Flow Operators
- map filter combine zip flatMapLatest
- Операторы Flow
topic: kotlin
subtopics:
- coroutines
- flow
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: internal
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-flow
- q-flow-operators-map-filter--kotlin--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- coroutines
- difficulty/medium
- flow
- kotlin
- operators
anki_cards:
- slug: kotlin-flow-003-0-en
  language: en
  anki_id: 1769344144941
  synced_at: '2026-01-25T16:29:04.992215'
- slug: kotlin-flow-003-0-ru
  language: ru
  anki_id: 1769344144990
  synced_at: '2026-01-25T16:29:04.994280'
---
# Vopros (RU)
> Какие ключевые операторы Flow существуют? Объясните `map`, `filter`, `combine`, `zip`, `flatMapLatest`, `flatMapMerge`.

---

# Question (EN)
> What are the key Flow operators? Explain `map`, `filter`, `combine`, `zip`, `flatMapLatest`, `flatMapMerge`.

## Otvet (RU)

### Операторы Трансформации

#### map
Трансформирует каждый элемент:

```kotlin
flowOf(1, 2, 3)
    .map { it * 2 }
    .collect { println(it) }
// 2, 4, 6
```

#### filter
Фильтрует элементы по предикату:

```kotlin
flowOf(1, 2, 3, 4, 5)
    .filter { it % 2 == 0 }
    .collect { println(it) }
// 2, 4
```

#### transform
Универсальный оператор - может эмитировать 0, 1 или N значений на каждый вход:

```kotlin
flowOf(1, 2, 3)
    .transform { value ->
        emit("Processing $value")
        emit(value * 10)
    }
    .collect { println(it) }
// Processing 1, 10, Processing 2, 20, Processing 3, 30
```

### Операторы Комбинирования

#### combine
Комбинирует последние значения из нескольких Flow. Эмитирует при каждом изменении любого источника:

```kotlin
val flow1 = flowOf(1, 2, 3).onEach { delay(100) }
val flow2 = flowOf("A", "B").onEach { delay(150) }

combine(flow1, flow2) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// 1A, 2A, 2B, 3B
```

**Когда использовать:** Когда нужна реакция на изменение любого из источников.

```kotlin
// Пример: валидация формы
val nameValid = nameFlow.map { it.isNotEmpty() }
val emailValid = emailFlow.map { it.contains("@") }

combine(nameValid, emailValid) { name, email ->
    name && email
}.collect { isFormValid ->
    submitButton.isEnabled = isFormValid
}
```

#### zip
Соединяет элементы по парам (1-й с 1-м, 2-й со 2-м). Завершается когда любой из Flow завершается:

```kotlin
val flow1 = flowOf(1, 2, 3)
val flow2 = flowOf("A", "B", "C", "D")

flow1.zip(flow2) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// 1A, 2B, 3C  (D не эмитится - flow1 завершился)
```

**Когда использовать:** Когда нужно строгое соответствие элементов.

```kotlin
// Пример: объединение параллельных запросов
val userFlow = flow { emit(api.getUser()) }
val settingsFlow = flow { emit(api.getSettings()) }

userFlow.zip(settingsFlow) { user, settings ->
    ProfileData(user, settings)
}.collect { profileData ->
    updateUI(profileData)
}
```

### Операторы Flatten

#### flatMapConcat
Последовательно обрабатывает внутренние Flow:

```kotlin
flowOf(1, 2, 3)
    .flatMapConcat { value ->
        flow {
            emit("$value: start")
            delay(100)
            emit("$value: end")
        }
    }
    .collect { println(it) }
// 1: start, 1: end, 2: start, 2: end, 3: start, 3: end
```

#### flatMapMerge
Параллельно обрабатывает внутренние Flow (по умолчанию до 16 одновременно):

```kotlin
flowOf(1, 2, 3)
    .flatMapMerge { value ->
        flow {
            emit("$value: start")
            delay(100)
            emit("$value: end")
        }
    }
    .collect { println(it) }
// 1: start, 2: start, 3: start, 1: end, 2: end, 3: end
// (порядок может отличаться)
```

**Когда использовать:** Параллельная загрузка данных:

```kotlin
// Загрузка деталей для списка ID
flowOf(listOf(1, 2, 3, 4, 5))
    .flatMapMerge(concurrency = 3) { ids ->
        ids.asFlow().map { id ->
            repository.getDetails(id)
        }
    }
    .collect { details -> processDetails(details) }
```

#### flatMapLatest
Отменяет предыдущий внутренний Flow при новой эмиссии:

```kotlin
flowOf(1, 2, 3)
    .onEach { delay(50) }
    .flatMapLatest { value ->
        flow {
            emit("$value: start")
            delay(100)
            emit("$value: end")
        }
    }
    .collect { println(it) }
// 1: start, 2: start, 3: start, 3: end
// (1: end и 2: end отменены)
```

**Когда использовать:** Поиск с debounce - отмена устаревших запросов:

```kotlin
searchQuery
    .debounce(300)
    .flatMapLatest { query ->
        if (query.isEmpty()) {
            flowOf(emptyList())
        } else {
            repository.search(query)
        }
    }
    .collect { results ->
        showResults(results)
    }
```

### Сравнение Flatten Операторов

| Оператор | Поведение | Использование |
|----------|-----------|---------------|
| `flatMapConcat` | Последовательно | Когда порядок важен |
| `flatMapMerge` | Параллельно | Когда нужна скорость |
| `flatMapLatest` | Только последний | Поиск, отмена устаревших |

### Дополнительные Операторы

```kotlin
// take - взять первые N
flowOf(1, 2, 3, 4, 5).take(3)  // 1, 2, 3

// drop - пропустить первые N
flowOf(1, 2, 3, 4, 5).drop(2)  // 3, 4, 5

// distinctUntilChanged - убрать последовательные дубликаты
flowOf(1, 1, 2, 2, 1).distinctUntilChanged()  // 1, 2, 1

// debounce - эмитировать только после паузы
searchFlow.debounce(300)

// sample - эмитировать последнее значение с интервалом
dataFlow.sample(1000)

// onEach - побочные эффекты
flow.onEach { log("Received: $it") }
```

---

## Answer (EN)

### Transformation Operators

#### map
Transforms each element:

```kotlin
flowOf(1, 2, 3)
    .map { it * 2 }
    .collect { println(it) }
// 2, 4, 6
```

#### filter
Filters elements by predicate:

```kotlin
flowOf(1, 2, 3, 4, 5)
    .filter { it % 2 == 0 }
    .collect { println(it) }
// 2, 4
```

#### transform
Universal operator - can emit 0, 1, or N values per input:

```kotlin
flowOf(1, 2, 3)
    .transform { value ->
        emit("Processing $value")
        emit(value * 10)
    }
    .collect { println(it) }
// Processing 1, 10, Processing 2, 20, Processing 3, 30
```

### Combining Operators

#### combine
Combines latest values from multiple Flows. Emits on each change from any source:

```kotlin
val flow1 = flowOf(1, 2, 3).onEach { delay(100) }
val flow2 = flowOf("A", "B").onEach { delay(150) }

combine(flow1, flow2) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// 1A, 2A, 2B, 3B
```

**When to use:** When you need reaction to any source change.

```kotlin
// Example: form validation
val nameValid = nameFlow.map { it.isNotEmpty() }
val emailValid = emailFlow.map { it.contains("@") }

combine(nameValid, emailValid) { name, email ->
    name && email
}.collect { isFormValid ->
    submitButton.isEnabled = isFormValid
}
```

#### zip
Pairs elements strictly (1st with 1st, 2nd with 2nd). Completes when any Flow completes:

```kotlin
val flow1 = flowOf(1, 2, 3)
val flow2 = flowOf("A", "B", "C", "D")

flow1.zip(flow2) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// 1A, 2B, 3C  (D not emitted - flow1 completed)
```

**When to use:** When you need strict element correspondence.

```kotlin
// Example: combining parallel requests
val userFlow = flow { emit(api.getUser()) }
val settingsFlow = flow { emit(api.getSettings()) }

userFlow.zip(settingsFlow) { user, settings ->
    ProfileData(user, settings)
}.collect { profileData ->
    updateUI(profileData)
}
```

### Flattening Operators

#### flatMapConcat
Processes inner Flows sequentially:

```kotlin
flowOf(1, 2, 3)
    .flatMapConcat { value ->
        flow {
            emit("$value: start")
            delay(100)
            emit("$value: end")
        }
    }
    .collect { println(it) }
// 1: start, 1: end, 2: start, 2: end, 3: start, 3: end
```

#### flatMapMerge
Processes inner Flows in parallel (up to 16 by default):

```kotlin
flowOf(1, 2, 3)
    .flatMapMerge { value ->
        flow {
            emit("$value: start")
            delay(100)
            emit("$value: end")
        }
    }
    .collect { println(it) }
// 1: start, 2: start, 3: start, 1: end, 2: end, 3: end
// (order may vary)
```

**When to use:** Parallel data loading:

```kotlin
// Load details for list of IDs
flowOf(listOf(1, 2, 3, 4, 5))
    .flatMapMerge(concurrency = 3) { ids ->
        ids.asFlow().map { id ->
            repository.getDetails(id)
        }
    }
    .collect { details -> processDetails(details) }
```

#### flatMapLatest
Cancels previous inner Flow on new emission:

```kotlin
flowOf(1, 2, 3)
    .onEach { delay(50) }
    .flatMapLatest { value ->
        flow {
            emit("$value: start")
            delay(100)
            emit("$value: end")
        }
    }
    .collect { println(it) }
// 1: start, 2: start, 3: start, 3: end
// (1: end and 2: end cancelled)
```

**When to use:** Search with debounce - cancel stale requests:

```kotlin
searchQuery
    .debounce(300)
    .flatMapLatest { query ->
        if (query.isEmpty()) {
            flowOf(emptyList())
        } else {
            repository.search(query)
        }
    }
    .collect { results ->
        showResults(results)
    }
```

### Flatten Operators Comparison

| Operator | Behavior | Use Case |
|----------|----------|----------|
| `flatMapConcat` | Sequential | When order matters |
| `flatMapMerge` | Parallel | When speed matters |
| `flatMapLatest` | Latest only | Search, cancel stale |

### Additional Operators

```kotlin
// take - take first N
flowOf(1, 2, 3, 4, 5).take(3)  // 1, 2, 3

// drop - skip first N
flowOf(1, 2, 3, 4, 5).drop(2)  // 3, 4, 5

// distinctUntilChanged - remove consecutive duplicates
flowOf(1, 1, 2, 2, 1).distinctUntilChanged()  // 1, 2, 1

// debounce - emit only after pause
searchFlow.debounce(300)

// sample - emit latest value at intervals
dataFlow.sample(1000)

// onEach - side effects
flow.onEach { log("Received: $it") }
```

---

## Dopolnitelnye Voprosy (RU)

1. Как выбрать между `combine` и `zip` для конкретной задачи?
2. Как ограничить параллелизм в `flatMapMerge`?
3. Чем `mapLatest` отличается от `flatMapLatest`?
4. Как реализовать retry с exponential backoff?
5. Как тестировать цепочки операторов Flow?

---

## Follow-ups

1. How to choose between `combine` and `zip` for a specific task?
2. How to limit parallelism in `flatMapMerge`?
3. How does `mapLatest` differ from `flatMapLatest`?
4. How to implement retry with exponential backoff?
5. How to test Flow operator chains?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Flow Operators Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [Flow Operators Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-instant-search-flow-operators--kotlin--medium]]
- [[q-flow-exception-handling--flow--medium]]

---

## Related Questions

### Related (Medium)
- [[q-flow-operators-map-filter--kotlin--medium]] - Basic Flow operators
- [[q-instant-search-flow-operators--kotlin--medium]] - Instant search implementation
- [[q-flow-exception-handling--flow--medium]] - Error handling in Flow
