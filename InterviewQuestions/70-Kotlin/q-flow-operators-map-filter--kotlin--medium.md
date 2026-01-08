---id: kotlin-074
title: "Операторы Flow: map, filter, transform / Flow Operators: map, filter, transform"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, flow]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: "Comprehensive Kotlin Coroutines Guide - Question 140018"

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-flow, c-stateflow, q-flow-operators--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-11

tags: [coroutines, difficulty/medium, kotlin]
---
# Вопрос (RU)
> Как использовать операторы `Flow` `map`, `filter`, `transform`? Объясните цепочки операторов и практические паттерны.

---

# Question (EN)
> How to use `Flow` operators `map`, `filter`, `transform`? Explain operator chaining and practical patterns.

## Ответ (RU)

Операторы `Flow` `map`, `filter` и `transform` являются фундаментальными инструментами для обработки холодных потоков данных в Kotlin Coroutines. Они позволяют трансформировать, фильтровать и манипулировать значениями, испускаемыми `Flow`, декларативным способом.

### Базовые Операторы

**map** - Трансформирует каждое испущенное значение:
```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { it * 2 }
 .collect { println(it) }  // Выводит: 2, 4, 6
```

**filter** - Фильтрует испускаемые значения на основе предиката:
```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
}.filter { it % 2 == 0 }
 .collect { println(it) }  // Выводит: 2, 4
```

**transform** - Универсальный оператор, который может испускать несколько значений на один вход и выполнять произвольную логику:
```kotlin
flow {
    emit("A")
    emit("B")
}.transform { value ->
    emit("Start: $value")
    emit("End: $value")
}.collect { println(it) }
// Выводит: Start: A, End: A, Start: B, End: B
```

### Цепочки Операторов

Операторы можно объединять в цепочки для создания сложных конвейеров обработки данных:

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
    emit(5)
}.filter { it % 2 == 0 }      // Оставляем только четные числа
 .map { it * it }             // Возводим в квадрат
 .map { "Result: $it" }       // Преобразуем в строку
 .collect { println(it) }
// Выводит: Result: 4, Result: 16
```

### Практические Паттерны

**Паттерн 1: Конвейер трансформации данных**
```kotlin
userInputFlow
    .filter { it.isNotEmpty() }
    .map { it.trim() }
    .map { it.lowercase() }
    .collect { processInput(it) }
```

**Паттерн 2: Обработка ответов API**
```kotlin
apiFlow
    .map { response -> response.data }
    .filter { data -> data.isValid }
    .map { data -> data.toUiModel() }
    .collect { uiModel -> updateUI(uiModel) }
```

**Паттерн 3: Множественные испускания на одно входное значение**
```kotlin
searchQueryFlow
    .transform { query ->
        emit(LoadingState)
        try {
            val results = searchApi(query)
            emit(SuccessState(results))
        } catch (e: Exception) {
            emit(ErrorState(e))
        }
    }
    .collect { state -> updateState(state) }
```

**Паттерн 4: Условная трансформация**
```kotlin
dataFlow
    .transform { value ->
        if (value > 0) {
            emit(value)
            emit(value * 2)
        }
        // Отрицательные значения отбрасываются
    }
    .collect { println(it) }
```

### Соображения Производительности

- По умолчанию операторы выполняются последовательно для каждого значения в том же контексте корутины, пока вы явно не измените это (например, с помощью `buffer`/`conflate`/`flowOn`).
- Промежуточные коллекции не создаются, операторы `Flow` ленивые и обрабатывают элементы по мере запроса `collect`-ом.
- Операторы сохраняют семантику поддержки отмены и кооперативной обработки.
- Каждая операция в цепочке добавляет небольшие накладные расходы, но обычно это приемлемо; избегайте чрезмерно длинных цепочек без необходимости.

### Типичные Ошибки

1. Ненужный запуск корутин внутри `map`: `map` — suspending-оператор, внутри него можно вызывать suspend-функции напрямую. Проблемой является создание дополнительных корутин (`async`/`launch`) без необходимости.
```kotlin
// Избегайте: избыточный async внутри map
flow.map { async { heavyOperation(it) }.await() }

// Предпочтительно: просто вызвать suspend-функцию
flow.map { heavyOperation(it) }

// Или использовать transform, если нужно несколько emit или сложная логика
flow.transform { value ->
    emit(heavyOperation(value))
}
```

2. Побочные эффекты в операторе преобразования: Старайтесь, чтобы `map`/`filter`/`transform` оставались как можно более чистыми.
```kotlin
// Избегайте
flow.map {
    updateDatabase(it)  // Побочный эффект!
    it
}

// Предпочтительно: выносить побочные эффекты в onEach или collect
flow.onEach { updateDatabase(it) }
    .map { it }
```

---

## Answer (EN)

`Flow` operators `map`, `filter`, and `transform` are fundamental tools for processing cold data streams in Kotlin Coroutines. They allow you to transform, filter, and manipulate `Flow` emissions in a declarative way.

### Basic Operators

**map** - Transforms each emitted value:
```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { it * 2 }
 .collect { println(it) }  // Prints: 2, 4, 6
```

**filter** - Filters emissions based on a predicate:
```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
}.filter { it % 2 == 0 }
 .collect { println(it) }  // Prints: 2, 4
```

**transform** - General-purpose operator that can emit multiple values per input and run arbitrary logic:
```kotlin
flow {
    emit("A")
    emit("B")
}.transform { value ->
    emit("Start: $value")
    emit("End: $value")
}.collect { println(it) }
// Prints: Start: A, End: A, Start: B, End: B
```

### Operator Chaining

Operators can be chained to create complex data processing pipelines:

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
    emit(5)
}.filter { it % 2 == 0 }      // Keep only even numbers
 .map { it * it }             // Square each number
 .map { "Result: $it" }       // Convert to string
 .collect { println(it) }
// Prints: Result: 4, Result: 16
```

### Practical Patterns

**Pattern 1: Data transformation pipeline**
```kotlin
userInputFlow
    .filter { it.isNotEmpty() }
    .map { it.trim() }
    .map { it.lowercase() }
    .collect { processInput(it) }
```

**Pattern 2: API response processing**
```kotlin
apiFlow
    .map { response -> response.data }
    .filter { data -> data.isValid }
    .map { data -> data.toUiModel() }
    .collect { uiModel -> updateUI(uiModel) }
```

**Pattern 3: Multiple emissions per input**
```kotlin
searchQueryFlow
    .transform { query ->
        emit(LoadingState)
        try {
            val results = searchApi(query)
            emit(SuccessState(results))
        } catch (e: Exception) {
            emit(ErrorState(e))
        }
    }
    .collect { state -> updateState(state) }
```

**Pattern 4: Conditional transformation**
```kotlin
dataFlow
    .transform { value ->
        if (value > 0) {
            emit(value)
            emit(value * 2)
        }
        // Negative values are dropped
    }
    .collect { println(it) }
```

### Performance Considerations

- Operators by default are executed sequentially for each emission in the same coroutine context, unless you explicitly change it (e.g., with `buffer`/`conflate`/`flowOn`).
- No intermediate collections are created; `Flow` operators are lazy and process values on demand as `collect` requests them.
- Operators preserve cooperative cancellation semantics.
- Each operator adds a small overhead; in most real-world pipelines this is negligible, but avoid excessively deep chains without purpose.

### Common Pitfalls

1. Unnecessary coroutine launches inside `map`: `map` is a suspending operator, you can call suspend functions directly. The issue is spawning extra coroutines (`async`/`launch`) when not needed.
```kotlin
// Avoid: redundant async inside map
flow.map { async { heavyOperation(it) }.await() }

// Prefer: call the suspend function directly
flow.map { heavyOperation(it) }

// Or use transform when you need multiple emits or more complex logic
flow.transform { value ->
    emit(heavyOperation(value))
}
```

2. Side effects inside transformation operators: Keep `map`/`filter`/`transform` as pure as possible.
```kotlin
// Avoid
flow.map {
    updateDatabase(it)  // Side effect!
    it
}

// Prefer: move side effects to onEach or collect
flow.onEach { updateDatabase(it) }
    .map { it }
```

---

## Дополнительные Вопросы (RU)

1. Как отличить использование `map`, `mapLatest`, `flatMapLatest` и `transform` для асинхронных операций в `Flow`?
2. В каких случаях стоит использовать `buffer`, `conflate` или `flowOn` вместе с операторами `map`/`filter`/`transform` для оптимизации производительности?
3. Как организовать обработку ошибок в цепочках операторов `Flow` (например, с помощью `catch`, `retry`) без нарушения чистоты операторов?
4. Чем отличаются операторы для холодных потоков `Flow` от операторов на `Channel` или горячих источниках (например, `StateFlow`/`SharedFlow`)?
5. Как обеспечить тестируемость сложных цепочек операторов `Flow` и какие подходы использовать в юнит-тестах?

---

## Follow-ups

1. How do `map`, `mapLatest`, `flatMapLatest`, and `transform` differ when used for asynchronous operations in `Flow`?
2. When should you use `buffer`, `conflate`, or `flowOn` together with `map`/`filter`/`transform` to optimize performance?
3. How can you structure error handling in `Flow` operator chains (e.g., with `catch`, `retry`) while keeping operators pure?
4. How do operators on cold `Flow` differ from operators on `Channel` or hot streams (such as `StateFlow`/`SharedFlow`)?
5. How can you ensure testability of complex `Flow` operator chains and what patterns to use in unit tests?

---

## Ссылки (RU)

- Официальная документация по Kotlin Coroutines: https://kotlinlang.org/docs/coroutines-overview.html
- [[c-flow]]
- [[c-coroutines]]

---

## References

- Kotlin Coroutines Documentation: https://kotlinlang.org/docs/coroutines-overview.html
- [[c-flow]]
- [[c-coroutines]]

---

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-flow-operators--kotlin--medium]] — Базовые операторы `Flow`
- [[q-retry-operators-flow--kotlin--medium]] — Повтор и обработка ошибок в `Flow`
- [[q-flow-time-operators--kotlin--medium]] — Временные операторы в `Flow`

### Продвинутый Уровень
- [[q-testing-flow-operators--kotlin--hard]] — Тестирование операторов `Flow`

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] — Введение в `Flow`

---

## Related Questions

### Related (Medium)
- [[q-flow-operators--kotlin--medium]] - Basic `Flow` operators
- [[q-retry-operators-flow--kotlin--medium]] - Retry and error handling with `Flow`
- [[q-flow-time-operators--kotlin--medium]] - Time-based operators in `Flow`

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Testing `Flow` operators

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
