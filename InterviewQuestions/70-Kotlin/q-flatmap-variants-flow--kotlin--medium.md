---
id: kotlin-050
title: "flatMapConcat vs flatMapMerge vs flatMapLatest / flatMapConcat против flatMapMerge против flatMapLatest"
aliases: ["flatMapConcat vs flatMapMerge vs flatMapLatest", "flatMapConcat против flatMapMerge против flatMapLatest"]

# Classification
topic: kotlin
subtopics: [coroutines, flow]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, q-kotlin-inline-functions--kotlin--medium, q-test-dispatcher-types--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-11-10

tags: [coroutines, difficulty/medium, flatmap, flow, kotlin, operators]
---
# Вопрос (RU)
> В чем разница между `flatMapConcat`, `flatMapMerge` и `flatMapLatest` в Kotlin `Flow`?

---

# Question (EN)
> What is the difference between `flatMapConcat`, `flatMapMerge`, and `flatMapLatest` in Kotlin `Flow`?

## Ответ (RU)

**flatMapConcat**, **flatMapMerge** и **flatMapLatest** — операторы `Flow`, которые трансформируют каждое значение в новый `Flow`, но отличаются тем, как обрабатывают одновременные внутренние потоки и отмену.

### Визуальное Сравнение

```text
Источник:  A -----> B -----> C
           ↓        ↓        ↓
Трансформация в flows (каждый требует времени):
           A1-A2-A3 B1-B2-B3 C1-C2-C3

flatMapConcat:  A1-A2-A3-B1-B2-B3-C1-C2-C3  (строго последовательно)
flatMapMerge:   A1-B1-A2-C1-B2-A3-B3-C2-C3  (конкурентно, эмиссии чередуются; порядок не гарантирован)
flatMapLatest:  при каждом новом значении предыдущий flow отменяется,
               в каждый момент времени эмитятся элементы только из последнего активного flow
```

(Диаграммы для `flatMapMerge` и `flatMapLatest` иллюстративны: конкретный порядок эмиссий не гарантируется.)

### flatMapConcat - Последовательное Выполнение

**Ждет завершения каждого внутреннего flow перед запуском следующего.**

```kotlin
fun flatMapConcat() {
    flow {
        emit(1)
        emit(2)
        emit(3)
    }
    .flatMapConcat { value ->
        flow {
            delay(100)  // Имитация работы
            emit("$value-A")
            delay(100)
            emit("$value-B")
        }
    }
    .collect { println(it) }
}

// Возможный вывод (строго последовательно и в порядке источника):
// 1-A
// 1-B
// 2-A
// 2-B
// 3-A
// 3-B
```

**Характеристики:**
- **Сохраняет порядок** — элементы выходного `Flow` упорядочены как во входном.
- **Последовательно** — только один внутренний `Flow` активен в каждый момент времени.
- **Потенциально медленнее** — общее время ≈ сумме времен всех внутренних `Flow`.
- **Использовать когда**: важен порядок и/или операции логически должны выполняться по очереди.

### flatMapMerge - Конкурентное Выполнение

**Запускает несколько внутренних `Flow` конкурентно (до указанного `concurrency`).**

```kotlin
fun flatMapMerge() {
    flow {
        emit(1)
        emit(2)
        emit(3)
    }
    .flatMapMerge(concurrency = 2) { value ->  // Максимум 2 конкурентных flow
        flow {
            delay(100)
            emit("$value-A")
            delay(100)
            emit("$value-B")
        }
    }
    .collect { println(it) }
}

// Пример возможного вывода (конкретный порядок не гарантируется):
// 1-A
// 2-A
// 1-B
// 2-B
// 3-A
// 3-B
```

**Характеристики:**
- **Порядок не сохраняется** — эмиссии внутренних `Flow` могут чередоваться.
- **Конкурентно** — несколько внутренних `Flow` выполняются одновременно до лимита `concurrency`.
- **Часто быстрее flatMapConcat** — за счет параллельной работы внутренних `Flow`;
  при этом итоговый оператор завершится только после завершения всех внутренних `Flow`.
- **Использовать когда**: важна производительность, порядок не критичен.

### flatMapLatest - Отмена Предыдущего

**Отменяет предыдущий внутренний `Flow`, когда приходит новое значение источника, и начинает новый. В каждый момент времени активен только последний внутренний `Flow`.**

```kotlin
fun flatMapLatest() {
    flow {
        emit(1)
        delay(150)  // 2 приходит до завершения flow для 1
        emit(2)
        delay(150)  // 3 приходит до завершения flow для 2
        emit(3)
    }
    .flatMapLatest { value ->
        flow {
            delay(100)
            emit("$value-A")
            delay(100)
            emit("$value-B")
        }
    }
    .collect { println(it) }
}

// Возможный вывод с указанными задержками:
// 1-A        (flow(1) стартует и успевает выдать A до 2)
// 2-A        (flow(1) отменен перед 1-B; flow(2) успевает выдать A до 3)
// 3-A
// 3-B        (flow(2) отменен перед 2-B; flow(3) дорабатывает до конца)
// Предыдущие flows отменяются в момент новой эмиссии источника.
```

**Характеристики:**
- **Отменяет предыдущие** — продолжается только последний запущенный внутренний `Flow`.
- **Отдает самые свежие данные** — подходит для сценариев, где важен только актуальный результат.
- **Эффективно** — не расходует ресурсы на устаревшие операции.
- **Использовать когда**: важен только последний результат (поиск, автодополнение, обновление экрана).

### Примеры Из Реальной Практики

**Пример 1: Поиск с flatMapLatest**

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults: Flow<List<Product>> = searchQuery
        .debounce(300)
        .filter { it.length >= 2 }
        .flatMapLatest { query ->  // Отменить предыдущий поиск при изменении запроса
            repository.search(query)
        }

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

**Почему flatMapLatest?** Если пользователь печатает "kotlin", нам не нужны результаты для "k", "ko", "kot" — только для финального значения. Предыдущие поиски отменяются.

**Пример 2: Загрузка пользователей последовательно с flatMapConcat**

```kotlin
class UserViewModel : ViewModel() {
    fun loadUsersSequentially(userIds: List<String>): Flow<User> {
        return userIds.asFlow()
            .flatMapConcat { userId ->  // Загружать по одному пользователю, сохраняя порядок
                repository.getUserById(userId)
            }
    }
}
```

**Почему flatMapConcat?** Нужно сохранить порядок при отображении пользователей или при цепочке зависимых вызовов.

**Пример 3: Параллельные сетевые запросы с flatMapMerge**

```kotlin
class DownloadViewModel : ViewModel() {
    fun downloadFiles(urls: List<String>): Flow<DownloadResult> {
        return urls.asFlow()
            .flatMapMerge(concurrency = 5) { url ->  // Загрузка до 5 файлов конкурентно
                repository.downloadFile(url)
            }
    }
}
```

**Почему flatMapMerge?** Загружаем несколько файлов одновременно для лучшей производительности, порядок результатов не важен.

### Сравнение Производительности (Иллюстративно)

```kotlin
// Тестовый сценарий: 5 элементов, обработка каждого занимает 100 мс,
// новые элементы приходят достаточно быстро.

// flatMapConcat: ≈500 мс (5 * 100 мс последовательно)
items.flatMapConcat { processItem(it) }

// flatMapMerge(3): ≈200 мс (до 3 элементов обрабатываются параллельно)
items.flatMapMerge(3) { processItem(it) }

// flatMapLatest: ≈100 мс (если новые элементы приходят до
// завершения предыдущих, реально завершается только последний)
items.flatMapLatest { processItem(it) }
```

(Цифры приведены для иллюстрации принципа; фактическое время зависит от задержек и шаблона эмиссий.)

### Когда Использовать Каждый

| Оператор | Применение | Пример |
|----------|------------|--------|
| **flatMapConcat** | Важен порядок, последовательная обработка | Загрузка упорядоченного списка, цепочка API вызовов |
| **flatMapMerge** | Важна скорость, порядок не важен | Параллельные загрузки, конкурентные запросы |
| **flatMapLatest** | Важен только последний результат | Поиск, автозаполнение, обновление данных |

### Общие Паттерны

**Паттерн 1: Поиск (flatMapLatest)**

```kotlin
searchQueryFlow
    .debounce(300)
    .flatMapLatest { query -> repository.search(query) }
```

**Паттерн 2: Пагинация (flatMapConcat)**

```kotlin
pageNumberFlow
    .flatMapConcat { page -> repository.loadPage(page) }
```

**Паттерн 3: Пакетная обработка (flatMapMerge)**

```kotlin
itemsFlow
    .flatMapMerge(concurrency = 10) { item -> processItem(item) }
```

### Граничные Случаи

**flatMapLatest с медленным источником:**

```kotlin
// Если источник эмитит редко и каждый внутренний flow успевает завершиться до следующей эмиссии,
// отмен не произойдет, и будут получены результаты всех значений.
flow {
    emit(1)
    delay(1000)
    emit(2)
    delay(1000)
    emit(3)
}
.flatMapLatest { value ->
    flow {
        delay(100)
        emit("$value-complete")
    }
}
// Вывод: 1-complete, 2-complete, 3-complete
```

**flatMapMerge с ограничением конкурентности:**

```kotlin
// Только 2 конкурентных flow одновременно
(1..10).asFlow()
    .flatMapMerge(concurrency = 2) { value ->
        flow {
            delay(1000)
            emit(value)
        }
    }
// Элементы обрабатываются максимум по 2 параллельно;
// конкретные пары и порядок зависят от времени выполнения.
```

### Комбинация С Другими Операторами

**flatMapLatest + retry:**

```kotlin
searchQuery
    .flatMapLatest { query ->
        repository.search(query)
            .retry(3) { e -> e is IOException }
    }
```

**flatMapMerge + catch:**

```kotlin
urls.asFlow()
    .flatMapMerge(5) { url ->
        repository.download(url)
            .catch { emit(DownloadResult.Error(it)) }
    }
```

**Краткое содержание**: `flatMapConcat` выполняет внутренние `Flow` последовательно и сохраняет порядок. `flatMapMerge` выполняет внутренние `Flow` конкурентно до заданного лимита и не гарантирует порядок, завершается после завершения всех внутренних `Flow`. `flatMapLatest` при каждом новом элементе источника отменяет предыдущий внутренний `Flow` и продолжает только с последним, поэтому подходит для сценариев, где важен только актуальный результат.

---

## Answer (EN)

**flatMapConcat**, **flatMapMerge**, and **flatMapLatest** are `Flow` operators that transform each value into a new `Flow`, but differ in how they handle concurrent inner flows and cancellation.

### Visual Comparison

```kotlin
Source:  A -----> B -----> C
         ↓        ↓        ↓
Transform to flows (each takes time):
         A1-A2-A3 B1-B2-B3 C1-C2-C3

flatMapConcat:  A1-A2-A3-B1-B2-B3-C1-C2-C3  (strictly sequential)
flatMapMerge:   A1-B1-A2-C1-B2-A3-B3-C2-C3  (concurrent, interleaved; order not guaranteed)
flatMapLatest:  on each new value, the previous inner flow is cancelled;
               at any time, emissions come only from the latest active flow
```

(The diagrams for `flatMapMerge` and `flatMapLatest` are illustrative: exact emission order is not guaranteed.)

### flatMapConcat - Sequential Execution

**Waits for each inner `Flow` to complete before starting the next.**

```kotlin
fun flatMapConcat() {
    flow {
        emit(1)
        emit(2)
        emit(3)
    }
    .flatMapConcat { value ->
        flow {
            delay(100)  // Simulate work
            emit("$value-A")
            delay(100)
            emit("$value-B")
        }
    }
    .collect { println(it) }
}

// Possible output (strictly sequential, source order preserved):
// 1-A
// 1-B
// 2-A
// 2-B
// 3-A
// 3-B
```

**Characteristics:**
- **Preserves order** — output `Flow` emissions follow the source order.
- **Sequential** — only one inner `Flow` is active at a time.
- **Potentially slower** — total time ≈ sum of all inner `Flow` times.
- **Use when**: order matters and/or operations must logically be performed one by one.

### flatMapMerge - Concurrent Execution

**Runs multiple inner `Flow`s concurrently (up to the given `concurrency`).**

```kotlin
fun flatMapMerge() {
    flow {
        emit(1)
        emit(2)
        emit(3)
    }
    .flatMapMerge(concurrency = 2) { value ->  // Max 2 concurrent flows
        flow {
            delay(100)
            emit("$value-A")
            delay(100)
            emit("$value-B")
        }
    }
    .collect { println(it) }
}

// Example of a possible output (exact order is not guaranteed):
// 1-A
// 2-A
// 1-B
// 2-B
// 3-A
// 3-B
```

**Characteristics:**
- **Order not preserved** — inner `Flow` emissions may be interleaved.
- **Concurrent** — multiple inner `Flow`s run at the same time up to the `concurrency` limit.
- **Often faster than flatMapConcat** — due to parallel execution of inner `Flow`s;
  the resulting `Flow` completes only after all inner flows complete.
- **Use when**: performance matters and you do not require ordered results.

### flatMapLatest - Cancel Previous

**Cancels the previous inner `Flow` when a new value is emitted by the source and starts a new inner `Flow`. At any time, only the latest inner `Flow` is active.**

```kotlin
fun flatMapLatest() {
    flow {
        emit(1)
        delay(150)  // 2 arrives before flow for 1 completes
        emit(2)
        delay(150)  // 3 arrives before flow for 2 completes
        emit(3)
    }
    .flatMapLatest { value ->
        flow {
            delay(100)
            emit("$value-A")
            delay(100)
            emit("$value-B")
        }
    }
    .collect { println(it) }
}

// Possible output with the given delays:
// 1-A        (flow(1) starts and emits A before 2)
// 2-A        (flow(1) is cancelled before 1-B; flow(2) emits A before 3)
// 3-A
// 3-B        (flow(2) is cancelled before 2-B; flow(3) runs to completion)
// Previous inner flows are cancelled at the moment of new source emissions.
```

**Characteristics:**
- **Cancels previous** — only the latest started inner `Flow` is allowed to continue.
- **Most recent data** — always reflects the latest relevant result.
- **Efficient** — avoids spending resources on outdated work.
- **Use when**: only the latest result matters (search, autocomplete, refreshing UI data).

### Real-World Examples

**Example 1: Search with flatMapLatest**

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults: Flow<List<Product>> = searchQuery
        .debounce(300)
        .filter { it.length >= 2 }
        .flatMapLatest { query ->  // Cancel previous search when query changes
            repository.search(query)
        }

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

**Why flatMapLatest?** When the user types "kotlin", results for "k", "ko", "kot" are not needed — only for the final query. Previous searches are cancelled.

**Example 2: Loading User Details with flatMapConcat**

```kotlin
class UserViewModel : ViewModel() {
    fun loadUsersSequentially(userIds: List<String>): Flow<User> {
        return userIds.asFlow()
            .flatMapConcat { userId ->  // Load one user at a time, in order
                repository.getUserById(userId)
            }
    }
}
```

**Why flatMapConcat?** You need to maintain ordering when displaying users in a specific sequence or chaining dependent calls.

**Example 3: Parallel Network Requests with flatMapMerge**

```kotlin
class DownloadViewModel : ViewModel() {
    fun downloadFiles(urls: List<String>): Flow<DownloadResult> {
        return urls.asFlow()
            .flatMapMerge(concurrency = 5) { url ->  // Download up to 5 files concurrently
                repository.downloadFile(url)
            }
    }
}
```

**Why flatMapMerge?** Download multiple files in parallel for better performance; result order is not important.

### Performance Comparison (Illustrative)

```kotlin
// Scenario: process 5 items, each inner flow takes 100 ms,
// and items are available quickly.

// flatMapConcat: ≈500 ms total (5 * 100 ms sequential)
items.flatMapConcat { processItem(it) }

// flatMapMerge(3): ≈200 ms total (up to 3 concurrent flows)
items.flatMapMerge(3) { processItem(it) }

// flatMapLatest: ≈100 ms total if new items arrive before previous
// inner flows finish, so effectively only the last one completes
items.flatMapLatest { processItem(it) }
```

(The numbers are illustrative; real timings depend on delays and emission patterns.)

### When to Use Each

| Operator | Use Case | Example |
|----------|----------|---------|
| **flatMapConcat** | Order matters, sequential processing | Loading an ordered list, dependent API calls |
| **flatMapMerge** | Speed matters, order does not | Parallel downloads, concurrent requests |
| **flatMapLatest** | Only latest result matters | Search, autocomplete, refresh / live updates |

### Common Patterns

**Pattern 1: Search (flatMapLatest)**

```kotlin
searchQueryFlow
    .debounce(300)
    .flatMapLatest { query -> repository.search(query) }
```

**Pattern 2: Pagination (flatMapConcat)**

```kotlin
pageNumberFlow
    .flatMapConcat { page -> repository.loadPage(page) }
```

**Pattern 3: Batch Processing (flatMapMerge)**

```kotlin
itemsFlow
    .flatMapMerge(concurrency = 10) { item -> processItem(item) }
```

### Edge Cases

**flatMapLatest with slow source:**

```kotlin
// If the source emits slowly and each inner flow completes
// before the next emission, no cancellations occur and all results are seen.
flow {
    emit(1)
    delay(1000)  // Enough time for inner flow to complete
    emit(2)
    delay(1000)
    emit(3)
}
.flatMapLatest { value ->
    flow {
        delay(100)
        emit("$value-complete")
    }
}
// Output: 1-complete, 2-complete, 3-complete
```

**flatMapMerge with concurrency limit:**

```kotlin
// Only 2 concurrent inner flows at a time
(1..10).asFlow()
    .flatMapMerge(concurrency = 2) { value ->
        flow {
            delay(1000)
            emit(value)
        }
    }
// Items are processed with at most 2 running concurrently;
// exact grouping and order depend on timing.
```

### Combination with Other Operators

**flatMapLatest + retry:**

```kotlin
searchQuery
    .flatMapLatest { query ->
        repository.search(query)
            .retry(3) { e -> e is IOException }
    }
```

**flatMapMerge + catch:**

```kotlin
urls.asFlow()
    .flatMapMerge(5) { url ->
        repository.download(url)
            .catch { emit(DownloadResult.Error(it)) }
    }
```

**English Summary**: `flatMapConcat` runs inner `Flow`s sequentially and preserves order. `flatMapMerge` runs inner `Flow`s concurrently up to a configurable limit and does not preserve order; it completes when all inner flows are done. `flatMapLatest` cancels the previous inner `Flow` whenever a new value arrives from the source and continues only with the latest, making it ideal when only the freshest result matters.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этих операторов от подходов в Java?
- Когда вы бы использовали каждый из этих операторов на практике?
- Каковы распространенные подводные камни при использовании этих операторов?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Операторы Flow - документация Kotlin](https://kotlinlang.org/docs/flow.html#flattening-flows)
- [flatMap variants in Flow](https://elizarov.medium.com/reactive-streams-and-kotlin-flows-bfd12772cda4)

## References

- [[c-kotlin]]
- [[c-flow]]
- [Flow Operators - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#flattening-flows)
- [flatMap variants in Flow](https://elizarov.medium.com/reactive-streams-and-kotlin-flows-bfd12772cda4)

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-instant-search-flow-operators--kotlin--medium]] — Flow
- [[q-catch-operator-flow--kotlin--medium]] — Flow
- [[q-flow-operators-map-filter--kotlin--medium]] — Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] — Coroutines

### Продвинутый Уровень
- [[q-testing-flow-operators--kotlin--hard]] — Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] — Flow

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] — Введение в Flow

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction
