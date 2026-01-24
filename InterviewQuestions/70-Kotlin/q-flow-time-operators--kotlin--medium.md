---
anki_cards:
- slug: q-flow-time-operators--kotlin--medium-0-en
  language: en
  anki_id: 1768326293881
  synced_at: '2026-01-23T17:03:51.615339'
- slug: q-flow-time-operators--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326293907
  synced_at: '2026-01-23T17:03:51.616930'
---
# Question (EN)
> What are `debounce`, `sample`, and throttle operators in Kotlin `Flow`? What are the differences and use cases?

## Ответ (RU)

Временные операторы в Kotlin `Flow` контролируют частоту эмиссий на основе временных интервалов. Два стандартных оператора — **`debounce`** и **`sample`** — и часто используемый паттерн **`throttleFirst`** (реализуется вручную как расширение, так как не является встроенным оператором) служат разным целям для обработки быстрых эмиссий.

### Быстрое Сравнение

| Оператор | Назначение | Когда излучает | Случай использования |
|----------|------------|----------------|----------------------|
| **`debounce`** | Ждать паузы | После таймаута с последней эмиссии | Поиск, валидация формы |
| **`sample`** | Периодическая выборка | В точках фиксированных интервалов, если были новые значения | Real-time данные, сенсоры |
| **`throttleFirst`** (кастомный) | Ограничение частоты | Первое в временном окне | Клики кнопки, быстрые события |

### Debounce: Ждать Тишины

**`debounce`** ждёт паузу в эмиссиях перед излучением последнего значения:

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

**`sample`** излучает самое недавнее значение в моменты, разделённые фиксированными временными интервалами (если за интервал было хотя бы одно новое значение):

```kotlin
locationUpdates
    .sample(1000) // Выборка каждую секунду
    .collect { location ->
        updateMapPosition(location)
    }

// Таймлайн:
// Вход:    A-B-C-D-E-F-G-H-I-J-K-L-M-N-O-P
// Выход:   ----D-------H-------L-------P---
//          (каждые 1000мс берётся последнее значение, если оно было)
```

**Как работает** (упрощённо):
1. Определяется фиксированный интервал (например, 1000мс)
2. В конце каждого интервала оператор излучает последнее полученное за интервал значение, если оно есть
3. Если в интервале не было новых значений, в этот момент ничего не излучается

**Пример: Real-time дашборд**

```kotlin
class DashboardViewModel : ViewModel() {
    val cpuUsage: StateFlow<Float> = cpuMonitor.observe()
        .sample(1000) // Обновлять UI раз в секунду
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = 0f
        )

    val networkSpeed: StateFlow<Long> = networkMonitor.observe()
        .sample(500) // Обновлять дважды в секунду
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = 0L
        )
}
```

### ThrottleFirst: Ограничение Частоты (кастомный)

**`throttleFirst`** — распространённый паттерн (не встроенный оператор `Flow`), который можно реализовать как оператор-расширение. Он излучает первое значение, затем игнорирует последующие значения в течение временного окна:

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

Реализация (упрощённый пример для иллюстрации идеи, использует системное время):

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
```

Эта реализация основана на `System.currentTimeMillis()` и ограничивает частоту относительно времени обработки коллекции; в продакшене и для тестов обычно предпочтительно использовать управляемый источник времени или подход с `delay`, если требуется точная интеграция с корутинным временем.

Пример использования (защита от дорогих операций по клику):

```kotlin
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
        .throttleFirst(1000) // Предотвращать двойные клики
        .onEach {
            performExpensiveOperation()
        }
        .launchIn(viewModelScope)
}
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

    val preciseLocation: StateFlow<Location?> = locationProvider
        .getLocationUpdates()
        .debounce(1000) // Ждать более стабильного положения
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

#### 4. Валидация Формы

```kotlin
class RegistrationViewModel : ViewModel() {
    private val _email = MutableStateFlow("")
    val email: StateFlow<String> = _email

    val emailValidation: StateFlow<ValidationResult> = _email
        .debounce(500) // Ждать, пока пользователь закончит ввод
        .map { email ->
            when {
                email.isBlank() -> ValidationResult.Empty
                !email.contains("@") -> ValidationResult.Invalid("Неверный формат email")
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

### Соображения По Производительности

```kotlin
// ПЛОХО: без debounce для поиска
searchInput.textChanges()
    .onEach { query ->
        // Вызов API на каждый ввод символа
        performSearch(query.toString())
    }
    .launchIn(lifecycleScope)

// ХОРОШО: использовать debounce для сокращения числа вызовов
searchInput.textChanges()
    .debounce(300)
    .onEach { query ->
        performSearch(query.toString())
    }
    .launchIn(lifecycleScope)
```

### Комбинация Временных Операторов

```kotlin
class DataSyncViewModel : ViewModel() {
    val syncStatus: StateFlow<SyncStatus> = dataSource
        .observe()
        .debounce(100) // Подождать, пока схлынет серия изменений
        .sample(1000) // Обновлять UI не чаще раза в секунду
        .map { data -> SyncStatus.Synced(data.size) }
        .catch { e -> emit(SyncStatus.Error(e.message)) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = SyncStatus.Idle
        )
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

// Использовать throttleFirst-подход для предотвращения частых кликов
clicks
    .throttleFirst(1000)
    .collect { performAction() }

// Комбинировать с другими операторами
input
    .debounce(300)
    .filter { it.length >= 3 }
    .distinctUntilChanged()
    .collect { search(it) }
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не путать семантику операторов
clicks
    .debounce(1000) // Обычно не подходит для основных кликов: сработает только после паузы
    // Для такого кейса лучше throttleFirst-подход

// Не использовать sample для ввода, где важен финальный результат
searchQuery
    .sample(300) // Может пропустить финальный ввод пользователя
    // Используйте debounce

// Не забывать про крайние случаи с debounce
input
    .debounce(300)
    // Продумайте, что произойдёт, если пользователь вводит текст и сразу триггерит submit другим событием
    .collect { search(it) }
```

---

## Answer (EN)

Time-based operators in Kotlin `Flow` control the rate of emissions based on time intervals. Two standard operators — **`debounce`** and **`sample`** — plus a commonly used pattern **`throttleFirst`** (implemented as an extension, not a built-in `Flow` operator) serve different purposes for handling rapid emissions.

### Quick Comparison

| Operator | Purpose | When Emits | Use Case |
|----------|---------|------------|----------|
| **`debounce`** | Wait for pause | After timeout since last emission | Search input, form validation |
| **`sample`** | Periodic sampling | At fixed interval points, if there were new values | Real-time data, sensor readings |
| **`throttleFirst`** (custom) | Rate limiting | First in time window | `Button` clicks, rapid events |

### Debounce: Wait for Silence

**`debounce`** waits for a pause in emissions before emitting the latest value:

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

**`sample`** emits the most recent value at points separated by fixed time intervals, if at least one new value arrived during the interval:

```kotlin
locationUpdates
    .sample(1000) // Sample every 1 second
    .collect { location ->
        updateMapPosition(location)
    }

// Timeline:
// Input:    A-B-C-D-E-F-G-H-I-J-K-L-M-N-O-P
// Output:   ----D-------H-------L-------P---
//           (every 1000ms, take the latest value if there was one)
```

**How it works** (simplified):
1. Define a fixed interval (e.g., 1000ms)
2. At the end of each interval, emit the last value received during that interval, if any
3. If no new value since last emission, nothing is emitted for that tick

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

### ThrottleFirst: Rate Limiting (custom)

**`throttleFirst`** is not a built-in `Flow` operator; it is typically implemented as an extension that emits the first value, then ignores subsequent values for a time window:

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

One possible (simplified) implementation for illustration:

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
```

This implementation relies on `System.currentTimeMillis()` and throttles relative to collection time; for production code and tests it's usually preferable to use a controllable time source or a `delay`-based approach if you need precise alignment with coroutine/virtual time.

Usage example (button click prevention):

```kotlin
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
        .debounce(1000) // Wait for a more stable location
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

// Use throttleFirst-style pattern for click prevention
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
// Don't confuse operator semantics
clicks
    .debounce(1000) // Typically not ideal for primary click handling: fires only after a quiet period
    // Prefer a throttleFirst-style pattern when you want to accept the first click and ignore the rest for a window

// Don't use sample for user input where the final value must not be lost
searchQuery
    .sample(300) // Might miss the final user input
    // Use debounce instead

// Don't forget edge cases with debounce
input
    .debounce(300)
    // Consider what happens if the user types and immediately triggers submit via another event
    .collect { search(it) }
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin `Flow` debounce](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/debounce.html)
- [Kotlin `Flow` sample](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/sample.html)
- [Flow Time-based Operators](https://elizarov.medium.com/callbacks-and-kotlin-flows-2b53aa2525cf)

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-catch-operator-flow--kotlin--medium]] - `Flow`
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure--kotlin--hard]] - `Flow`

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - `Flow`

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

## MOC Links

- [[moc-kotlin]]
