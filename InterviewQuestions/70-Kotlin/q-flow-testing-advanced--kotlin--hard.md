---
id: kotlin-056
title: "Advanced Flow Testing / Продвинутое тестирование Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, testing, testscope, async, coroutines]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-flow-basics--kotlin--medium, q-testing-viewmodels-coroutines--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [kotlin, flow, testing, testscope, async, difficulty/hard]
---
# Question (EN)
> Test complex Flow chains with delays, errors, and multiple emissions. Use TestScope, TestDispatcher, and virtual time for deterministic testing.

# Вопрос (RU)
> Протестируйте сложные цепочки Flow с задержками, ошибками и множественными испусканиями. Используйте TestScope, TestDispatcher и виртуальное время для детерминистического тестирования.

---

## Answer (EN)

Testing Flows requires special tools to handle asynchronous behavior, delays, and timing-dependent logic deterministically.

### Test Dependencies

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("app.cash.turbine:turbine:1.0.0") // Flow testing library
    testImplementation("junit:junit:4.13.2")
}
```

### TestScope and TestDispatcher

`TestScope` and `TestDispatcher` provide virtual time control for deterministic testing.

```kotlin
@Test
fun `test flow with delays using virtual time`() = runTest {
    val flow = flow {
        emit(1)
        delay(1000) // Virtual delay
        emit(2)
        delay(1000)
        emit(3)
    }

    val results = mutableListOf<Int>()

    val job = launch {
        flow.collect { results.add(it) }
    }

    // Virtual time - instant execution
    advanceUntilIdle() // Fast-forward through all delays

    job.cancel()

    assertEquals(listOf(1, 2, 3), results)
    // Test completes instantly despite 2000ms of delays!
}
```

### Testing with Turbine

Turbine is a testing library specifically for Flows that provides a clean API.

```kotlin
@Test
fun `test flow emissions with turbine`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

### Testing Flow Transformations

```kotlin
class UserRepository(private val api: UserApi) {
    fun getUserFlow(userId: Int): Flow<User> = flow {
        emit(api.getUser(userId))
    }
    .retry(3)
    .catch { emit(User.DEFAULT) }
}

@Test
fun `test user flow with retry`() = runTest {
    var attemptCount = 0
    val mockApi = object : UserApi {
        override suspend fun getUser(id: Int): User {
            attemptCount++
            if (attemptCount < 3) {
                throw IOException("Network error")
            }
            return User(id, "John")
        }
    }

    val repository = UserRepository(mockApi)

    repository.getUserFlow(123).test {
        val user = awaitItem()
        assertEquals("John", user.name)
        assertEquals(3, attemptCount) // Retried 2 times
        awaitComplete()
    }
}
```

### Testing StateFlow

```kotlin
class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }

    fun decrement() {
        _count.value--
    }
}

@Test
fun `test stateflow updates`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        // Initial value
        assertEquals(0, awaitItem())

        viewModel.increment()
        assertEquals(1, awaitItem())

        viewModel.increment()
        assertEquals(2, awaitItem())

        viewModel.decrement()
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing SharedFlow

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun post(event: Event) {
        _events.emit(event)
    }
}

@Test
fun `test sharedflow broadcasts to multiple collectors`() = runTest {
    val eventBus = EventBus()

    val collector1 = mutableListOf<Event>()
    val collector2 = mutableListOf<Event>()

    val job1 = launch {
        eventBus.events.collect { collector1.add(it) }
    }

    val job2 = launch {
        eventBus.events.collect { collector2.add(it) }
    }

    eventBus.post(Event.UserLoggedIn(123))
    eventBus.post(Event.MessageReceived("Hello"))

    advanceUntilIdle()

    assertEquals(2, collector1.size)
    assertEquals(2, collector2.size)

    job1.cancel()
    job2.cancel()
}
```

### Testing Error Handling

```kotlin
@Test
fun `test flow error handling with catch`() = runTest {
    val flow = flow {
        emit(1)
        emit(2)
        throw IOException("Network error")
    }
    .catch { exception ->
        emit(-1) // Fallback value
    }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(-1, awaitItem()) // Fallback
        awaitComplete()
    }
}

@Test
fun `test flow propagates uncaught exception`() = runTest {
    val flow = flow {
        emit(1)
        throw IllegalStateException("Critical error")
    }

    flow.test {
        assertEquals(1, awaitItem())
        val error = awaitError()
        assertTrue(error is IllegalStateException)
        assertEquals("Critical error", error.message)
    }
}
```

### Testing Cold vs Hot Flows

```kotlin
@Test
fun `test cold flow creates new stream per collector`() = runTest {
    var collectorCount = 0

    val coldFlow = flow {
        collectorCount++
        emit(collectorCount)
    }

    coldFlow.test {
        assertEquals(1, awaitItem())
        awaitComplete()
    }

    coldFlow.test {
        assertEquals(2, awaitItem()) // New execution
        awaitComplete()
    }
}

@Test
fun `test hot flow shares stream between collectors`() = runTest {
    val coldFlow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    val hotFlow = coldFlow.shareIn(
        scope = this,
        started = SharingStarted.Eagerly,
        replay = 1
    )

    delay(150) // Let it emit some values

    hotFlow.test {
        // Gets replay of latest value
        assertEquals(2, awaitItem())
        // Then receives new emissions
        assertEquals(3, awaitItem())
        expectNoEvents()
    }
}
```

### Testing Complex Scenarios

```kotlin
class SearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

@Test
fun `test search debouncing`() = runTest {
    val mockRepo = object : SearchRepository {
        override fun search(query: String): Flow<List<Result>> = flow {
            delay(100)
            emit(listOf(Result(query)))
        }
    }

    val viewModel = SearchViewModel(mockRepo)

    viewModel.searchResults.test {
        assertEquals(emptyList<Result>(), awaitItem()) // Initial

        // Type quickly - should debounce
        viewModel.onSearchQueryChanged("kot")
        advanceTimeBy(100) // Not enough time
        expectNoEvents()

        viewModel.onSearchQueryChanged("kotl")
        advanceTimeBy(100)
        expectNoEvents()

        viewModel.onSearchQueryChanged("kotlin")
        advanceTimeBy(300) // Debounce time passed
        advanceTimeBy(100) // Repository delay

        val results = awaitItem()
        assertEquals(1, results.size)
        assertEquals("kotlin", results[0].query)

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `test search cancellation`() = runTest {
    var searchCount = 0

    val mockRepo = object : SearchRepository {
        override fun search(query: String): Flow<List<Result>> = flow {
            searchCount++
            delay(500)
            emit(listOf(Result(query)))
        }
    }

    val viewModel = SearchViewModel(mockRepo)

    viewModel.searchResults.test {
        awaitItem() // Initial

        viewModel.onSearchQueryChanged("kotlin")
        advanceTimeBy(300) // Pass debounce
        advanceTimeBy(100) // Start search

        // New query before first search completes
        viewModel.onSearchQueryChanged("java")
        advanceTimeBy(300)
        advanceTimeBy(500) // Complete second search

        val results = awaitItem()
        assertEquals("java", results[0].query)
        assertEquals(2, searchCount) // Both searches started
        // But only second completed

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing Backpressure

```kotlin
@Test
fun `test buffer strategy`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(10)
        }
    }
    .buffer(3)

    val results = mutableListOf<Int>()

    flow.collect {
        results.add(it)
        delay(50) // Slow collector
    }

    assertEquals((0..9).toList(), results)
}

@Test
fun `test conflate drops intermediate values`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(10)
        }
    }
    .conflate()

    val results = mutableListOf<Int>()

    flow.collect {
        results.add(it)
        delay(50)
    }

    // Only some values collected
    assertTrue(results.size < 10)
    assertTrue(results.contains(0)) // First
    assertTrue(results.contains(9)) // Last
}
```

### Best Practices

1. **Use runTest for coroutine tests**:
   ```kotlin
   @Test
   fun myTest() = runTest { // Auto TestScope
       // Virtual time available here
   }
   ```

2. **Use Turbine for cleaner Flow tests**:
   ```kotlin
   //  Clean with Turbine
   flow.test {
       assertEquals(1, awaitItem())
       awaitComplete()
   }

   //  Manual collection is verbose
   val results = mutableListOf<Int>()
   flow.collect { results.add(it) }
   assertEquals(listOf(1), results)
   ```

3. **Test all emissions and completion**:
   ```kotlin
   flow.test {
       assertEquals(1, awaitItem())
       assertEquals(2, awaitItem())
       awaitComplete() // Ensure flow completed
   }
   ```

4. **Test error scenarios**:
   ```kotlin
   errorFlow.test {
       val error = awaitError()
       assertTrue(error is ExpectedException)
   }
   ```

5. **Use virtual time for delays**:
   ```kotlin
   @Test
   fun testDelays() = runTest {
       val flow = flow {
           delay(1000)
           emit(1)
       }

       flow.test {
           advanceTimeBy(1000) // Virtual
           assertEquals(1, awaitItem())
       }
       // Completes instantly!
   }
   ```

### Common Pitfalls

1. **Not using runTest**:
   ```kotlin
   //  Real delays
   @Test
   fun test() {
       runBlocking {
           delay(1000) // Actually waits!
       }
   }

   //  Virtual time
   @Test
   fun test() = runTest {
       delay(1000) // Instant
   }
   ```

2. **Not advancing time**:
   ```kotlin
   @Test
   fun test() = runTest {
       val flow = flow {
           delay(100)
           emit(1)
       }

       flow.test {
           //  Will timeout without advancing
           awaitItem()

           //  Advance time first
           advanceTimeBy(100)
           awaitItem()
       }
   }
   ```

3. **Forgetting awaitComplete**:
   ```kotlin
   //  Doesn't verify completion
   flow.test {
       assertEquals(1, awaitItem())
   }

   //  Verifies flow completes
   flow.test {
       assertEquals(1, awaitItem())
       awaitComplete()
   }
   ```

**English Summary**: Flow testing uses TestScope and TestDispatcher for virtual time control, making tests deterministic and fast. Turbine library provides clean API for testing emissions. Test all aspects: emissions, errors, completion, delays, backpressure, and cancellation. Use runTest for automatic TestScope, advanceTimeBy/advanceUntilIdle for time control, and always verify flow completion with awaitComplete().

## Ответ (RU)

Тестирование Flow требует специальных инструментов для обработки асинхронного поведения детерминистично.

### TestScope и TestDispatcher

```kotlin
@Test
fun `test flow with delays`() = runTest {
    val flow = flow {
        emit(1)
        delay(1000) // Виртуальная задержка
        emit(2)
    }

    flow.test {
        assertEquals(1, awaitItem())
        advanceTimeBy(1000) // Продвинуть виртуальное время
        assertEquals(2, awaitItem())
        awaitComplete()
    }
    // Тест завершается мгновенно несмотря на задержки!
}
```

### Тестирование с Turbine

```kotlin
@Test
fun `test flow emissions`() = runTest {
    val flow = flowOf(1, 2, 3)

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование обработки ошибок

```kotlin
@Test
fun `test flow error handling`() = runTest {
    val flow = flow {
        emit(1)
        throw IOException("Error")
    }
    .catch { emit(-1) }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(-1, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование StateFlow

```kotlin
@Test
fun `test stateflow updates`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        assertEquals(0, awaitItem()) // Начальное значение

        viewModel.increment()
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование сложных сценариев

```kotlin
@Test
fun `test search debouncing`() = runTest {
    val viewModel = SearchViewModel(mockRepo)

    viewModel.searchResults.test {
        awaitItem() // Начальное

        viewModel.onSearchQueryChanged("kotlin")
        advanceTimeBy(300) // Пройти debounce
        advanceTimeBy(100) // Задержка репозитория

        val results = awaitItem()
        assertEquals("kotlin", results[0].query)

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Лучшие практики

1. **Используйте runTest**:
   ```kotlin
   @Test
   fun myTest() = runTest {
       // Виртуальное время доступно
   }
   ```

2. **Используйте Turbine для чистых тестов**:
   ```kotlin
   flow.test {
       assertEquals(1, awaitItem())
       awaitComplete()
   }
   ```

3. **Тестируйте все испускания**:
   ```kotlin
   flow.test {
       assertEquals(1, awaitItem())
       awaitComplete() // Убедиться что завершен
   }
   ```

4. **Используйте виртуальное время**:
   ```kotlin
   @Test
   fun test() = runTest {
       delay(1000) // Мгновенно!
       advanceTimeBy(1000)
   }
   ```

**Краткое содержание**: Тестирование Flow использует TestScope и TestDispatcher для контроля виртуального времени, делая тесты детерминистическими и быстрыми. Библиотека Turbine предоставляет чистый API. Тестируйте все аспекты: испускания, ошибки, завершение, задержки, противодавление, отмену. Используйте runTest для автоматического TestScope, advanceTimeBy для контроля времени, всегда проверяйте завершение с awaitComplete().

---

## References
- [Testing Kotlin coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Turbine - Flow testing library](https://github.com/cashapp/turbine)
- [Testing Flows - Android Developers](https://developer.android.com/kotlin/flow/test)

## Related Questions

### Related (Hard)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow

### Prerequisites (Easier)
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - Testing
- [[q-catch-operator-flow--kotlin--medium]] - Flow

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

