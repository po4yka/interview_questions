---
id: kotlin-127
title: "Flow Time Operators: debounce, sample, throttle / Временные операторы Flow"
aliases: ["Flow Time Operators: debounce, sample, throttle, Временные операторы Flow"]

# Classification
topic: kotlin
subtopics:
  - debounce
  - flow
  - sample
  - throttle
  - time-operators
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Guide to time-based Flow operators

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-flow-basics--kotlin--easy, q-flow-operators-deep-dive--kotlin--hard, q-instant-search-flow-operators--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-31

tags: [coroutines, debounce, difficulty/medium, flow, kotlin, sample, throttle, time-operators]
date created: Saturday, November 1st 2025, 9:25:30 am
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Question (EN)
> What are debounce, sample, and throttle operators in Kotlin Flow? What are the differences and use cases?

# Вопрос (RU)
> Что такое операторы debounce, sample и throttle в Kotlin Flow? В чём различия и случаи использования?

---

## Answer (EN)

Time-based operators in Kotlin Flow control the rate of emissions based on time intervals. The three main operators—**debounce**, **sample**, and **throttleFirst**—serve different purposes for handling rapid emissions.

### Quick Comparison

| Operator | Purpose | When Emits | Use Case |
|----------|---------|------------|----------|
| **debounce** | Wait for pause | After timeout since last emission | Search input, form validation |
| **sample** | Periodic sampling | At fixed intervals | Real-time data, sensor readings |
| **throttleFirst** | Rate limiting | First in time window | Button clicks, rapid events |

### Debounce: Wait for Silence

**debounce** waits for a pause in emissions before emitting the latest value:

```kotlin
searchQuery
    .debounce(300) // Wait 300ms after last emission
    .collect { query ->
        performSearch(query)
    }

// Timeline:
// Input:    A--B--C--------D---------E--F--G--------
// Output:   ---------C---------D---------G--------
//           (waits 300ms after each input)
```

**How it works**:
1. Receives a value
2. Starts a timer (300ms)
3. If another value arrives, resets timer
4. When timer completes, emits the last value

**Example: Search Input**

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300) // Wait 300ms after typing stops
        .filter { it.length >= 3 } // Min 3 characters
        .distinctUntilChanged() // Avoid duplicate searches
        .flatMapLatest { query ->
            searchRepository.search(query)
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
```

### Sample: Periodic Sampling

**sample** emits the most recent value at fixed time intervals:

```kotlin
locationUpdates
    .sample(1000) // Sample every 1 second
    .collect { location ->
        updateMapPosition(location)
    }

// Timeline:
// Input:    A-B-C-D-E-F-G-H-I-J-K-L-M-N-O-P
// Sample:   ----D-------H-------L-------P---
//           (every 1000ms, take latest value)
```

**How it works**:
1. Sets up a fixed time interval (1000ms)
2. At each interval, emits the most recent value
3. If no new value since last emission, doesn't emit

**Example: Real-time Dashboard**

```kotlin
class DashboardViewModel : ViewModel() {
    val cpuUsage: StateFlow<Float> = cpuMonitor.observe()
        .sample(1000) // Update UI every second
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = 0f
        )

    val networkSpeed: StateFlow<Long> = networkMonitor.observe()
        .sample(500) // Update twice per second
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = 0L
        )
}
```

### ThrottleFirst: Rate Limiting

**throttleFirst** emits the first value, then ignores subsequent values for a time window:

```kotlin
buttonClicks
    .throttleFirst(1000) // Ignore clicks for 1s after each click
    .collect {
        performAction()
    }

// Timeline:
// Input:    A-B-C--------D-E-F--------G-H-I-J
// Output:   A------------D------------G-------
//           (take first, ignore for 1000ms)
```

**How it works**:
1. Emits first value immediately
2. Starts a time window (1000ms)
3. Ignores all values during window
4. After window closes, emits next value

Note: `throttleFirst` is not built-in, but can be implemented:

```kotlin
fun <T> Flow<T>.throttleFirst(windowDuration: Long): Flow<T> = flow {
    var lastEmissionTime = 0L
    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmissionTime >= windowDuration) {
            lastEmissionTime = currentTime
            emit(value)
        }
    }
}

// Usage: Button click prevention
button.setOnClickListener {
    viewModel.onButtonClick()
}

val clicks = MutableSharedFlow<Unit>()

fun onButtonClick() {
    viewModelScope.launch {
        clicks.emit(Unit)
    }
}

init {
    clicks
        .throttleFirst(1000) // Prevent double-clicks
        .onEach {
            performExpensiveOperation()
        }
        .launchIn(viewModelScope)
}
```

### Real-World Examples

#### 1. Instant Search

```kotlin
class SearchActivity : AppCompatActivity() {
    private val viewModel: SearchViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding.searchInput.textChanges()
            .debounce(300) // Wait for user to stop typing
            .filter { it.length >= 2 } // Min length
            .distinctUntilChanged() // Skip duplicates
            .onEach { query ->
                viewModel.search(query.toString())
            }
            .launchIn(lifecycleScope)
    }
}

class SearchViewModel : ViewModel() {
    private val _results = MutableStateFlow<List<Result>>(emptyList())
    val results: StateFlow<List<Result>> = _results

    fun search(query: String) {
        viewModelScope.launch {
            _results.value = repository.search(query)
        }
    }
}
```

#### 2. Location Tracking

```kotlin
class MapViewModel : ViewModel() {
    val userLocation: StateFlow<Location?> = locationProvider
        .getLocationUpdates()
        .sample(2000) // Update map every 2 seconds
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = null
        )

    val preciseLocation: StateFlow<Location?> = locationProvider
        .getLocationUpdates()
        .debounce(1000) // Wait for stable location
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = null
        )
}
```

#### 3. Button Click Protection

```kotlin
class FormViewModel : ViewModel() {
    private val submitClicks = MutableSharedFlow<Unit>()

    init {
        submitClicks
            .throttleFirst(2000) // Prevent rapid submissions
            .onEach {
                submitForm()
            }
            .launchIn(viewModelScope)
    }

    fun onSubmitClick() {
        viewModelScope.launch {
            submitClicks.emit(Unit)
        }
    }

    private suspend fun submitForm() {
        // API call
    }
}
```

#### 4. Form Validation

```kotlin
class RegistrationViewModel : ViewModel() {
    private val _email = MutableStateFlow("")
    val email: StateFlow<String> = _email

    val emailValidation: StateFlow<ValidationResult> = _email
        .debounce(500) // Wait for user to finish typing
        .map { email ->
            when {
                email.isBlank() -> ValidationResult.Empty
                !email.contains("@") -> ValidationResult.Invalid("Invalid email format")
                else -> ValidationResult.Valid
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = ValidationResult.Empty
        )

    fun onEmailChanged(newEmail: String) {
        _email.value = newEmail
    }
}

sealed class ValidationResult {
    object Empty : ValidationResult()
    object Valid : ValidationResult()
    data class Invalid(val message: String) : ValidationResult()
}
```

### Performance Considerations

```kotlin
// BAD: No debounce on search
searchInput.textChanges()
    .onEach { query ->
        // Makes API call on every keystroke!
        performSearch(query.toString())
    }
    .launchIn(lifecycleScope)

// GOOD: Debounce to reduce API calls
searchInput.textChanges()
    .debounce(300)
    .onEach { query ->
        performSearch(query.toString())
    }
    .launchIn(lifecycleScope)
```

### Combining Time Operators

```kotlin
class DataSyncViewModel : ViewModel() {
    val syncStatus: StateFlow<SyncStatus> = dataSource
        .observe()
        .debounce(100) // Wait for burst of changes to settle
        .sample(1000) // Then update UI max once per second
        .map { data -> SyncStatus.Synced(data.size) }
        .catch { e -> emit(SyncStatus.Error(e.message)) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = SyncStatus.Idle
        )
}
```

### Best Practices

#### DO:
```kotlin
// Use debounce for user input
searchQuery
    .debounce(300)
    .collect { performSearch(it) }

// Use sample for high-frequency updates
sensorData
    .sample(100)
    .collect { updateUI(it) }

// Use throttleFirst for click prevention
clicks
    .throttleFirst(1000)
    .collect { performAction() }

// Combine with other operators
input
    .debounce(300)
    .filter { it.length >= 3 }
    .distinctUntilChanged()
    .collect { search(it) }
```

#### DON'T:
```kotlin
// Don't use wrong operator
clicks
    .debounce(1000) // Wrong: waits after all clicks stop
    // Use throttleFirst instead

// Don't use sample for user input
searchQuery
    .sample(300) // Wrong: might miss final input
    // Use debounce instead

// Don't forget to handle edge cases
input
    .debounce(300) // What if user types and immediately submits?
    .collect { search(it) }
```

---

## Ответ (RU)

Временные операторы в Kotlin Flow контролируют частоту эмиссий на основе временных интервалов. Три основных оператора—**debounce**, **sample** и **throttleFirst**—служат разным целям для обработки быстрых эмиссий.

### Быстрое Сравнение

| Оператор | Назначение | Когда излучает | Случай использования |
|----------|---------|------------|----------|
| **debounce** | Ждать паузы | После таймаута с последней эмиссии | Поиск, валидация формы |
| **sample** | Периодическая выборка | В фиксированные интервалы | Real-time данные, сенсоры |
| **throttleFirst** | Ограничение частоты | Первое в временном окне | Клики кнопки, быстрые события |

### Debounce: Ждать Тишины

**debounce** ждёт паузу в эмиссиях перед излучением последнего значения:

```kotlin
searchQuery
    .debounce(300) // Ждать 300мс после последней эмиссии
    .collect { query ->
        performSearch(query)
    }

// Таймлайн:
// Вход:    A--B--C--------D---------E--F--G--------
// Выход:   ---------C---------D---------G--------
//          (ждёт 300мс после каждого ввода)
```

**Как работает**:
1. Получает значение
2. Запускает таймер (300мс)
3. Если приходит другое значение, сбрасывает таймер
4. Когда таймер завершается, излучает последнее значение

**Пример: Поисковый ввод**

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300) // Ждать 300мс после окончания набора
        .filter { it.length >= 3 } // Минимум 3 символа
        .distinctUntilChanged() // Избегать дублирующих поисков
        .flatMapLatest { query ->
            searchRepository.search(query)
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
```

### Sample: Периодическая Выборка

**sample** излучает самое недавнее значение через фиксированные временные интервалы:

```kotlin
locationUpdates
    .sample(1000) // Выборка каждую секунду
    .collect { location ->
        updateMapPosition(location)
    }

// Таймлайн:
// Вход:    A-B-C-D-E-F-G-H-I-J-K-L-M-N-O-P
// Sample:  ----D-------H-------L-------P---
//          (каждые 1000мс, берём последнее значение)
```

### ThrottleFirst: Ограничение Частоты

**throttleFirst** излучает первое значение, затем игнорирует последующие значения в течение временного окна:

```kotlin
buttonClicks
    .throttleFirst(1000) // Игнорировать клики на 1с после каждого клика
    .collect {
        performAction()
    }

// Таймлайн:
// Вход:    A-B-C--------D-E-F--------G-H-I-J
// Выход:   A------------D------------G-------
//          (взять первое, игнорировать 1000мс)
```

### Реальные Примеры

#### 1. Мгновенный Поиск

```kotlin
class SearchActivity : AppCompatActivity() {
    private val viewModel: SearchViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding.searchInput.textChanges()
            .debounce(300) // Ждать пока пользователь перестанет печатать
            .filter { it.length >= 2 } // Минимальная длина
            .distinctUntilChanged() // Пропускать дубликаты
            .onEach { query ->
                viewModel.search(query.toString())
            }
            .launchIn(lifecycleScope)
    }
}
```

#### 2. Отслеживание Местоположения

```kotlin
class MapViewModel : ViewModel() {
    val userLocation: StateFlow<Location?> = locationProvider
        .getLocationUpdates()
        .sample(2000) // Обновлять карту каждые 2 секунды
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = null
        )
}
```

#### 3. Защита От Двойных Кликов

```kotlin
class FormViewModel : ViewModel() {
    private val submitClicks = MutableSharedFlow<Unit>()

    init {
        submitClicks
            .throttleFirst(2000) // Предотвращать быстрые отправки
            .onEach {
                submitForm()
            }
            .launchIn(viewModelScope)
    }

    fun onSubmitClick() {
        viewModelScope.launch {
            submitClicks.emit(Unit)
        }
    }

    private suspend fun submitForm() {
        // API вызов
    }
}
```

### Лучшие Практики

#### ДЕЛАТЬ:
```kotlin
// Использовать debounce для пользовательского ввода
searchQuery
    .debounce(300)
    .collect { performSearch(it) }

// Использовать sample для высокочастотных обновлений
sensorData
    .sample(100)
    .collect { updateUI(it) }

// Использовать throttleFirst для предотвращения кликов
clicks
    .throttleFirst(1000)
    .collect { performAction() }
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не использовать неправильный оператор
clicks
    .debounce(1000) // Неправильно: ждёт после всех кликов
    // Использовать throttleFirst

// Не использовать sample для пользовательского ввода
searchQuery
    .sample(300) // Неправильно: может пропустить финальный ввод
    // Использовать debounce
```

---

## References

- [Kotlin Flow debounce](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/debounce.html)
- [Kotlin Flow sample](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/sample.html)
- [Flow Time-based Operators](https://elizarov.medium.com/callbacks-and-kotlin-flows-2b53aa2525cf)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure--kotlin--hard]] - Flow

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - Flow

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## MOC Links

- [[moc-kotlin]]
