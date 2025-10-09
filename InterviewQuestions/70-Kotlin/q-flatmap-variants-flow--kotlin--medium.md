---
id: 20251006-003
title: "flatMapConcat vs flatMapMerge vs flatMapLatest / flatMapConcat vs flatMapMerge vs flatMapLatest"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, flatmap, operators, coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: reviewed
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, flow, flatmap, operators, coroutines, difficulty/medium]
---
## Question (EN)
> What is the difference between flatMapConcat, flatMapMerge, and flatMapLatest in Kotlin Flow?
## Вопрос (RU)
> В чем разница между flatMapConcat, flatMapMerge и flatMapLatest в Kotlin Flow?

---

## Answer (EN)

**flatMapConcat**, **flatMapMerge**, and **flatMapLatest** are Flow operators that transform each value into a new Flow, but differ in how they handle concurrent flows.

### Visual Comparison

```
Source:  A -----> B -----> C
         ↓        ↓        ↓
Transform to flows (each takes time):
         A1-A2-A3 B1-B2-B3 C1-C2-C3

flatMapConcat:  A1-A2-A3-B1-B2-B3-C1-C2-C3  (sequential, wait for completion)
flatMapMerge:   A1-B1-A2-C1-B2-A3-B3-C2-C3  (concurrent, interleaved)
flatMapLatest:  A1-B1-C1-C2-C3              (cancel previous, only latest)
```

### flatMapConcat - Sequential Execution

**Waits for each inner flow to complete before starting the next.**

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

// Output (sequential):
// 1-A
// 1-B
// 2-A
// 2-B
// 3-A
// 3-B
```

**Characteristics:**
- - **Preserves order** - emissions in same order as source
- - **Sequential** - one inner flow at a time
- - **Slower** - waits for each flow to complete
- **Use when**: Order matters, operations must be sequential

### flatMapMerge - Concurrent Execution

**Executes multiple inner flows concurrently.**

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

// Output (concurrent, order not guaranteed):
// 1-A
// 2-A
// 1-B
// 2-B
// 3-A
// 3-B
```

**Characteristics:**
- - **Order not preserved** - emissions can be interleaved
- - **Concurrent** - multiple flows run in parallel
- - **Faster** - doesn't wait for completion
- **Use when**: Speed matters, order doesn't matter

### flatMapLatest - Cancel Previous

**Cancels previous inner flow when new value arrives.**

```kotlin
fun flatMapLatest() {
    flow {
        emit(1)
        delay(150)  // New value before previous flow completes
        emit(2)
        delay(150)
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

// Output (only latest):
// 1-A
// 2-A
// 3-A
// 3-B
// (Previous flows cancelled before completion)
```

**Characteristics:**
- - **Cancels previous** - only latest flow completes
- - **Most recent data** - always shows latest
- - **Efficient** - doesn't waste resources on outdated data
- **Use when**: Only latest result matters (search, autocomplete)

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

**Why flatMapLatest?** If user types "kotlin", we don't need results for "k", "ko", "kot" - only final "kotlin". Previous searches are cancelled.

**Example 2: Loading User Details with flatMapConcat**

```kotlin
class UserViewModel : ViewModel() {
    fun loadUsersSequentially(userIds: List<String>): Flow<User> {
        return userIds.asFlow()
            .flatMapConcat { userId ->  // Load one user at a time
                repository.getUserById(userId)
            }
    }
}
```

**Why flatMapConcat?** Need to maintain order when displaying users in specific sequence.

**Example 3: Parallel Network Requests with flatMapMerge**

```kotlin
class DownloadViewModel : ViewModel() {
    fun downloadFiles(urls: List<String>): Flow<DownloadResult> {
        return urls.asFlow()
            .flatMapMerge(concurrency = 5) { url ->  // Download 5 files concurrently
                repository.downloadFile(url)
            }
    }
}
```

**Why flatMapMerge?** Download multiple files at once for better performance. Order doesn't matter.

### Performance Comparison

```kotlin
// Test: Process 5 items, each takes 100ms

// flatMapConcat: 500ms total (5 * 100ms sequential)
items.flatMapConcat { processItem(it) }  // 500ms

// flatMapMerge(3): ~200ms total (max 3 concurrent)
items.flatMapMerge(3) { processItem(it) }  // ~200ms

// flatMapLatest: 100ms total (only last item completes)
items.flatMapLatest { processItem(it) }  // 100ms (if items arrive quickly)
```

### Advanced Usage

**Example 4: Auto-refresh with flatMapLatest**

```kotlin
class DashboardViewModel : ViewModel() {
    private val refreshTrigger = MutableSharedFlow<Unit>()

    val dashboardData: Flow<DashboardData> = merge(
        flowOf(Unit),  // Initial load
        refreshTrigger  // Manual refresh
    )
    .flatMapLatest {  // Cancel previous load if new refresh triggered
        repository.getDashboardData()
    }

    fun refresh() {
        viewModelScope.launch {
            refreshTrigger.emit(Unit)
        }
    }
}
```

**Example 5: Load Details for List Items with flatMapMerge**

```kotlin
class ProductListViewModel : ViewModel() {
    val productsWithDetails: Flow<List<ProductDetails>> = repository
        .getProductIds()
        .flatMapConcat { productIds ->  // Get all IDs first
            productIds.asFlow()
                .flatMapMerge(concurrency = 10) { productId ->  // Load details concurrently
                    repository.getProductDetails(productId)
                }
                .toList()
                .asFlow()
        }
}
```

**Example 6: Debounced Search with Concurrent Requests**

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults: Flow<SearchResults> = searchQuery
        .debounce(300)
        .flatMapLatest { query ->  // Cancel previous search
            combine(
                repository.searchProducts(query),
                repository.searchCategories(query),
                repository.searchBrands(query)
            ) { products, categories, brands ->
                SearchResults(products, categories, brands)
            }
        }
}
```

### When to Use Each

| Operator | Use Case | Example |
|----------|----------|---------|
| **flatMapConcat** | Order matters, sequential processing | Loading ordered list, sequential API calls |
| **flatMapMerge** | Speed matters, order doesn't | Parallel downloads, concurrent requests |
| **flatMapLatest** | Only latest matters | Search, autocomplete, refresh |

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
// If source emits slowly, all items complete
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
// Only 2 concurrent flows
(1..10).asFlow()
    .flatMapMerge(concurrency = 2) { value ->
        flow {
            delay(1000)
            emit(value)
        }
    }
// Processes in batches of 2: [1,2], [3,4], [5,6], etc.
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

**English Summary**: `flatMapConcat` executes inner flows sequentially (preserves order, slower). `flatMapMerge` executes concurrently (faster, order not preserved, configurable concurrency). `flatMapLatest` cancels previous inner flow when new value arrives (only latest completes). Use `flatMapConcat` for: ordered processing, sequential operations. Use `flatMapMerge` for: parallel downloads, concurrent requests. Use `flatMapLatest` for: search, autocomplete, refresh (only latest matters).

## Ответ (RU)

**flatMapConcat**, **flatMapMerge** и **flatMapLatest** — операторы Flow, которые трансформируют каждое значение в новый Flow, но отличаются в обработке конкурентных потоков.

### Визуальное сравнение

```
Источник:  A -----> B -----> C
           ↓        ↓        ↓
Трансформация в flows (каждый требует времени):
           A1-A2-A3 B1-B2-B3 C1-C2-C3

flatMapConcat:  A1-A2-A3-B1-B2-B3-C1-C2-C3  (последовательно, ждет завершения)
flatMapMerge:   A1-B1-A2-C1-B2-A3-B3-C2-C3  (конкурентно, чередуется)
flatMapLatest:  A1-B1-C1-C2-C3              (отменяет предыдущий, только последний)
```

### flatMapConcat - Последовательное выполнение

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

// Вывод (последовательно):
// 1-A
// 1-B
// 2-A
// 2-B
// 3-A
// 3-B
```

**Характеристики:**
- - **Сохраняет порядок** - эмиссии в том же порядке что и источник
- - **Последовательно** - один внутренний flow за раз
- - **Медленнее** - ждет завершения каждого flow
- **Использовать когда**: Важен порядок, операции должны быть последовательными

### flatMapMerge - Конкурентное выполнение

**Выполняет несколько внутренних flows конкурентно.**

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

// Вывод (конкурентно, порядок не гарантирован):
// 1-A
// 2-A
// 1-B
// 2-B
// 3-A
// 3-B
```

**Характеристики:**
- - **Порядок не сохраняется** - эмиссии могут чередоваться
- - **Конкурентно** - множественные flows работают параллельно
- - **Быстрее** - не ждет завершения
- **Использовать когда**: Важна скорость, порядок не важен

### flatMapLatest - Отмена предыдущего

**Отменяет предыдущий внутренний flow когда приходит новое значение.**

```kotlin
fun flatMapLatest() {
    flow {
        emit(1)
        delay(150)  // Новое значение до завершения предыдущего flow
        emit(2)
        delay(150)
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

// Вывод (только последний):
// 1-A
// 2-A
// 3-A
// 3-B
// (Предыдущие flows отменены до завершения)
```

**Характеристики:**
- - **Отменяет предыдущий** - только последний flow завершается
- - **Самые свежие данные** - всегда показывает последнее
- - **Эффективно** - не тратит ресурсы на устаревшие данные
- **Использовать когда**: Важен только последний результат (поиск, автозаполнение)

### Примеры из реальной практики

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

**Почему flatMapLatest?** Если пользователь печатает "kotlin", нам не нужны результаты для "k", "ko", "kot" - только для финального "kotlin". Предыдущие поиски отменяются.

**Пример 2: Параллельные сетевые запросы с flatMapMerge**

```kotlin
class DownloadViewModel : ViewModel() {
    fun downloadFiles(urls: List<String>): Flow<DownloadResult> {
        return urls.asFlow()
            .flatMapMerge(concurrency = 5) { url ->  // Загрузка 5 файлов конкурентно
                repository.downloadFile(url)
            }
    }
}
```

**Почему flatMapMerge?** Загружаем несколько файлов одновременно для лучшей производительности. Порядок не важен.

### Сравнение производительности

```kotlin
// Тест: Обработать 5 элементов, каждый требует 100мс

// flatMapConcat: 500мс всего (5 * 100мс последовательно)
items.flatMapConcat { processItem(it) }  // 500мс

// flatMapMerge(3): ~200мс всего (максимум 3 конкурентных)
items.flatMapMerge(3) { processItem(it) }  // ~200мс

// flatMapLatest: 100мс всего (только последний элемент завершается)
items.flatMapLatest { processItem(it) }  // 100мс (если элементы приходят быстро)
```

### Когда использовать каждый

| Оператор | Применение | Пример |
|----------|------------|--------|
| **flatMapConcat** | Важен порядок, последовательная обработка | Загрузка упорядоченного списка, последовательные API вызовы |
| **flatMapMerge** | Важна скорость, порядок не важен | Параллельные загрузки, конкурентные запросы |
| **flatMapLatest** | Важен только последний | Поиск, автозаполнение, обновление |

**Краткое содержание**: `flatMapConcat` выполняет внутренние flows последовательно (сохраняет порядок, медленнее). `flatMapMerge` выполняет конкурентно (быстрее, порядок не сохраняется, настраиваемая конкурентность). `flatMapLatest` отменяет предыдущий внутренний flow когда приходит новое значение (завершается только последний). Используйте `flatMapConcat` для: упорядоченной обработки, последовательных операций. Используйте `flatMapMerge` для: параллельных загрузок, конкурентных запросов. Используйте `flatMapLatest` для: поиска, автозаполнения, обновления.

---

## References
- [Flow Operators - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#flattening-flows)
- [flatMap variants in Flow](https://elizarov.medium.com/reactive-streams-and-kotlin-flows-bfd12772cda4)

## Related Questions
- [[q-flow-operators--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]
