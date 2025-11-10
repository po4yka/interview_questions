---
id: kotlin-046
title: "Debounce vs Throttle in Flow / Debounce vs Throttle в Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, operators]
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
related: [c-flow, c-kotlin, q-request-coalescing-deduplication--kotlin--hard]

# Timestamps
created: 2025-10-06
updated: 2025-11-10

tags: [debounce, difficulty/medium, flow, kotlin, operators, throttle]
---
# Вопрос (RU)
> В чем разница между `debounce` и `throttle` в Kotlin `Flow`? Когда использовать каждый?

---

# Question (EN)
> What is the difference between `debounce` and `throttle` in Kotlin `Flow`? When to use each?

## Ответ (RU)

**Debounce** и **throttle** — операторы, завязанные на время, которые контролируют частоту эмиссий из `Flow`, но работают по-разному.

### Визуальное Сравнение

```
Вход:   A----B-C---D------E-F-G--------H
        |         |             |      |

// Упрощенная иллюстрация поведения

debounce(500мс): Ждет период тишины
        --------C-----D---------G------H
        (Эмитит последнее значение после ≥500мс тишины)

throttleFirst(500мс): Эмитит не чаще чем раз в окно
        A----------------------E--------H
        (Эмитит первое значение в окне, остальные в этом окне игнорируются)
```

### Debounce - Ожидание Периода Тишины

**Эмитит значение только после того как прошло указанное время без новых эмиссий.**

```kotlin
val searchQuery = MutableStateFlow("")

searchQuery
    .debounce(300)  // Ждать 300мс после последнего нажатия клавиши
    .collect { query ->
        searchApi(query)  // Вызывается только после того как пользователь перестал печатать
    }
```

**Как это работает:**
1. Значение приходит → запуск таймера (300мс)
2. Новое значение приходит → сброс таймера
3. Таймер завершается → эмитится последнее значение
4. Повтор

### Применение Debounce

**1. Поиск/Автозаполнение**

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: Flow<List<Product>> = _searchQuery
        .debounce(300)  // Ждать 300мс после того как пользователь перестал печатать
        .filter { it.length >= 2 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
        }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

// Пользователь печатает: "k", "ko", "kot", "kotl", "kotlin"
// Ищем только: "kotlin" (после паузы 300мс)
```

**2. Валидация формы**

```kotlin
class RegistrationViewModel : ViewModel() {
    private val email = MutableStateFlow("")

    val emailValidation: Flow<ValidationResult> = email
        .debounce(500)  // Ждать 500мс после того как пользователь перестал печатать
        .map { validateEmail(it) }

    fun onEmailChanged(value: String) {
        email.value = value
    }
}
```

**3. Авто-сохранение**

```kotlin
class EditorViewModel : ViewModel() {
    private val documentContent = MutableStateFlow("")

    init {
        documentContent
            .debounce(2000)  // Авто-сохранение через 2с после того как пользователь перестал печатать
            .onEach { content ->
                repository.saveDocument(content)
                showMessage("Авто-сохранено")
            }
            .launchIn(viewModelScope)
    }
}
```

### Throttle - Ограничение Частоты

**Throttle** в общем смысле — это операторы, ограничивающие количество эмиссий за период времени (например, не чаще одного раза в X миллисекунд).

**В Kotlin `Flow` нет встроенного `throttleFirst`/`throttleLatest`, но их можно реализовать.** Ниже — простая реализация `throttleFirst`, которая эмитит не чаще одного значения за окно времени.

```kotlin
fun <T> Flow<T>.throttleFirst(windowDurationMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L
    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmissionTime >= windowDurationMillis) {
            lastEmissionTime = currentTime
            emit(value)
        }
    }
}
```

- Первое значение проходит сразу (так как `lastEmissionTime = 0`).
- Все значения, пришедшие раньше чем через `windowDurationMillis` после последней эмиссии, игнорируются.
- Эта реализация завязана на `System.currentTimeMillis()` и упрощена: для продакшена/тестов лучше использовать источники времени, совместимые с корутинами (например, виртуальное время в тестах) и учитывать структуру корутин, отмену и диспетчеры.

**Как это работает концептуально:**
1. Приходит значение → если вне текущего окна → эмитим и начинаем окно.
2. Значения внутри окна → игнорируются.
3. Следующее значение после окончания окна → может быть эмитировано.

### Применение Throttle

**1. Предотвращение частых кликов по кнопке**

```kotlin
class ButtonViewModel : ViewModel() {
    private val _clickEvents = MutableSharedFlow<Unit>()

    init {
        _clickEvents
            .throttleFirst(1000)  // Игнорировать клики в течение 1с после первого клика
            .onEach {
                performAction()
            }
            .launchIn(viewModelScope)
    }

    fun onButtonClick() {
        viewModelScope.launch {
            _clickEvents.emit(Unit)
        }
    }
}

// Пользователь кликает быстро: click-click-click-click
// Обрабатывается только первый клик (остальные в течение 1с игнорируются)
```

**2. Обновления локации**

```kotlin
class LocationService {
    private val _locationUpdates = MutableSharedFlow<Location>()

    val sampledLocation: Flow<Location> = _locationUpdates
        .throttleFirst(5000)  // Обновлять не чаще чем раз в 5 секунд

    // GPS может отправлять обновления каждые 500мс, но нам нужны только более редкие события
}
```

**3. События прокрутки (Scroll Events)**

```kotlin
class ScrollViewModel : ViewModel() {
    private val _scrollEvents = MutableSharedFlow<Int>()

    val processedScrollEvents: Flow<Int> = _scrollEvents
        .throttleFirst(100)  // Обрабатывать не чаще чем раз в 100мс

    fun onScroll(position: Int) {
        viewModelScope.launch {
            _scrollEvents.emit(position)
        }
    }
}
```

### Сравнительная Таблица

| Функция | debounce | throttleFirst (пример throttling) |
|--------|----------|------------------------------------|
| Эмитит | Последнее значение после периода тишины | Не чаще одного значения в окно (обычно первое) |
| Таймер | Сбрасывается при каждой эмиссии | Фиксированное окно, без сброса из-за новых значений |
| Применение | Дождаться окончания ввода/бурста | Ограничить частоту реакций |
| Пример | Ввод поиска | Клики по кнопке |
| Задержка | После последнего события | После первого события в каждом окне |

### Сравнение В Реальном Мире

**Ввод поиска (предпочтителен debounce):**

```kotlin
// Пользователь печатает: "h" "e" "l" "l" "o"
//                        100мс 100мс 100мс 100мс

// debounce(200мс):
// → Ждет 200мс после "o" → ищет "hello" (GOOD)

// throttleFirst(200мс):
// → Скорее всего выполнит поиск по первому символу и будет пропускать следующие в рамках окон → не подходит (BAD)
```

**Клики по кнопке (предпочтителен throttle):**

```kotlin
// Пользователь кликает быстро: click---click---click---click
//                               0мс     50мс    100мс   150мс

// throttleFirst(500мс):
// → Обрабатывает первый клик, игнорирует остальные 500мс (GOOD)

// debounce(500мс):
// → Ждет 500мс после последнего клика → действие выполняется с задержкой и может казаться "неоткликающейся" кнопкой (BAD)
```

### Продвинутые Замечания о Реализациях

Ниже примеры пользовательских операторов упрощены для иллюстрации идей. Для реального применения следует внимательно продумать работу с временем, конкурентностью, отменой, диспетчерами и структурированными корутинами.

**Пример упрощенного throttleLatest (эмитит последнее значение не чаще чем раз в окно):**

```kotlin
fun <T> Flow<T>.throttleLatest(windowDurationMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L
    var pending: T? = null

    suspend fun emitIfDue(now: Long) {
        if (pending != null && now - lastEmissionTime >= windowDurationMillis) {
            emit(pending as T)
            lastEmissionTime = now
            pending = null
        }
    }

    collect { value ->
        val now = System.currentTimeMillis()
        pending = value
        emitIfDue(now)
    }

    // По завершении исходного Flow можно эмитить последний pending при необходимости
    pending?.let { emit(it) }
}
```

(Это лишь иллюстрация: корректная реализация требует аккуратной работы с задержками и таймерами.)

**Пример debounce с немедленной первой эмиссией (приближенная идея):**

```kotlin
fun <T> Flow<T>.debounceImmediate(timeoutMillis: Long): Flow<T> = channelFlow {
    var lastEmissionTime = 0L
    var pendingJob: Job? = null

    collect { value ->
        val now = System.currentTimeMillis()
        if (now - lastEmissionTime >= timeoutMillis) {
            // Немедленная (leading) эмиссия
            pendingJob?.cancel()
            trySend(value)
            lastEmissionTime = now
        } else {
            // Перезапуск отложенной (trailing) эмиссии
            pendingJob?.cancel()
            pendingJob = launch {
                delay(timeoutMillis - (now - lastEmissionTime))
                trySend(value)
                lastEmissionTime = System.currentTimeMillis()
            }
        }
    }
}
```

Эти реализации демонстрируют принципы, но могут потребовать адаптации под конкретный use-case и тестирование с использованием виртуального времени.

### Комбинирование Debounce и Throttle

**Пример: "Умный" поиск с обоими подходами**

```kotlin
class SmartSearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: Flow<List<Product>> = _searchQuery
        .throttleFirst(100)  // Отсечь крайне частые события (< 100мс)
        .debounce(300)       // Ждать 300мс паузы перед запросом
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
        }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

### Соображения Производительности

**`debounce` — эффективность по памяти:**

```kotlin
// debounce хранит только последнее значение
searchQuery
    .debounce(300)
    .collect { /* ... */ }

// Память: O(1) — хранится только последнее значение
```

**`throttle` — отбрасывает значения:**

```kotlin
// throttleFirst отбрасывает промежуточные значения
rapidUpdates
    .throttleFirst(1000)
    .collect { /* ... */ }

// Если 100 обновлений за 1с → большинство будет отброшено
```

### Тестирование

**Тест debounce:**

```kotlin
@Test
fun `debounce should emit last value after quiet period`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(500)  // Период тишины
    }.debounce(300)

    val result = flow.toList()

    assertEquals(listOf(3), result)  // Только последнее значение
}
```

**Тест throttleFirst (упрощенный):**

```kotlin
@Test
fun `throttleFirst should emit at most one value per window`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(600)  // Новое окно
        emit(4)
    }.throttleFirst(500)

    val result = flow.toList()

    assertEquals(listOf(1, 4), result)
}
```

### Лучшие Практики (Best Practices)

**1. Подбирайте подходящий таймаут:**

```kotlin
// Поиск: 300-500мс (отзывчиво)
searchQuery.debounce(300)

// Авто-сохранение: 1000-2000мс (не слишком часто)
document.debounce(2000)

// Кнопка: 500-1000мс (предотвращение дабл-кликов)
button.throttleFirst(1000)
```

**2. Комбинируйте с другими операторами:**

```kotlin
searchQuery
    .debounce(300)
    .filter { it.length >= 2 }
    .distinctUntilChanged()
    .flatMapLatest { search(it) }
```

**3. Учитывайте отмену и корутинный контекст:**

```kotlin
// debounce отменяет ожидание при новых значениях
searchQuery
    .debounce(300)
    .onEach { query ->
        // Вызывается только для значений, которые не были отменены
        searchApi(query)
    }
    .launchIn(viewModelScope)
```

**Краткое содержание (RU)**: `debounce` ждёт период тишины после последней эмиссии (сбрасывает таймер на каждом значении) и эмитит последнее значение. `throttle`-подходы ограничивают частоту эмиссий (например, `throttleFirst` пропускает не чаще одного значения за окно). Используйте `debounce` для поиска, валидации форм, авто-сохранения (нужна реакция после окончания ввода). Используйте `throttle` для кликов, обновлений локации, событий прокрутки (нужно ограничить частоту). `debounce` сохраняет последнее ожидающее значение, а `throttleFirst` — первое значение в каждом окне. Типичные таймауты: поиск ~300мс, авто-сохранение ~2с, кнопка ~1с.

---

## Answer (EN)

**Debounce** and **throttle** are time-based patterns/operators that control the rate of emissions from a `Flow`, but they behave differently.

### Visual Comparison

```
Input:  A----B-C---D------E-F-G--------H
        |         |             |      |

// Simplified illustration

debounce(500ms): waits for quiet period
        --------C-----D---------G------H
        (emits the latest value after ≥500ms of silence)

throttleFirst(500ms): at most one emission per window
        A----------------------E--------H
        (emits the first value in each window, ignores the rest in that window)
```

### Debounce - Wait for Quiet Period

**Emits a value only after the specified time has passed without new emissions.**

```kotlin
val searchQuery = MutableStateFlow("")

searchQuery
    .debounce(300)  // Wait 300ms after last keystroke
    .collect { query ->
        searchApi(query)  // Only called after user stops typing
    }
```

**How it works:**
1. Value arrives → start timer (300ms)
2. New value arrives → reset timer
3. Timer completes → emit latest value
4. Repeat

### Debounce Use Cases

**1. Search/Autocomplete**

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: Flow<List<Product>> = _searchQuery
        .debounce(300)  // Wait 300ms after user stops typing
        .filter { it.length >= 2 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
        }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

// User types: "k", "ko", "kot", "kotl", "kotlin"
// Only searches for: "kotlin" (after 300ms pause)
```

**2. Form Validation**

```kotlin
class RegistrationViewModel : ViewModel() {
    private val email = MutableStateFlow("")

    val emailValidation: Flow<ValidationResult> = email
        .debounce(500)  // Wait 500ms after user stops typing
        .map { validateEmail(it) }

    fun onEmailChanged(value: String) {
        email.value = value
    }
}
```

**3. Auto-Save**

```kotlin
class EditorViewModel : ViewModel() {
    private val documentContent = MutableStateFlow("")

    init {
        documentContent
            .debounce(2000)  // Auto-save 2s after user stops typing
            .onEach { content ->
                repository.saveDocument(content)
                showMessage("Auto-saved")
            }
            .launchIn(viewModelScope)
    }
}
```

### Throttle - Rate Limiting

"Throttle" generally refers to operators that limit how often values are emitted (e.g., at most one value per X milliseconds).

Kotlin `Flow` does not provide built-in `throttleFirst`/`throttleLatest`, but we can implement them. Below is a simple `throttleFirst` implementation that emits at most one value per window:

```kotlin
fun <T> Flow<T>.throttleFirst(windowDurationMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L
    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmissionTime >= windowDurationMillis) {
            lastEmissionTime = currentTime
            emit(value)
        }
    }
}
```

- First value passes immediately (since `lastEmissionTime = 0`).
- Any value arriving sooner than `windowDurationMillis` after the last emitted one is ignored.
- This implementation is simplified and tied to `System.currentTimeMillis()`. For production and tests, prefer time sources compatible with coroutines (e.g., virtual time in tests) and be careful about clock changes.

**How it works conceptually:**
1. Value arrives → if outside the current window → emit and start a new window.
2. Values inside the window → ignored.
3. Next value after the window ends → may be emitted.

### Throttle Use Cases

**1. Button Click Prevention**

```kotlin
class ButtonViewModel : ViewModel() {
    private val _clickEvents = MutableSharedFlow<Unit>()

    init {
        _clickEvents
            .throttleFirst(1000)  // Ignore clicks for 1s after first click
            .onEach {
                performAction()
            }
            .launchIn(viewModelScope)
    }

    fun onButtonClick() {
        viewModelScope.launch {
            _clickEvents.emit(Unit)
        }
    }
}

// User clicks rapidly: click-click-click-click
// Only processes: first click (others within 1s ignored)
```

**2. Location Updates**

```kotlin
class LocationService {
    private val _locationUpdates = MutableSharedFlow<Location>()

    val sampledLocation: Flow<Location> = _locationUpdates
        .throttleFirst(5000)  // Only update at most once every 5 seconds

    // GPS may send updates every 500ms, but we only need coarser updates
}
```

**3. Scroll Events**

```kotlin
class ScrollViewModel : ViewModel() {
    private val _scrollEvents = MutableSharedFlow<Int>()

    val processedScrollEvents: Flow<Int> = _scrollEvents
        .throttleFirst(100)  // Process at most once every 100ms

    fun onScroll(position: Int) {
        viewModelScope.launch {
            _scrollEvents.emit(position)
        }
    }
}
```

### Comparison Table

| Feature | debounce | throttleFirst (example of throttling) |
|---------|----------|----------------------------------------|
| Emits | Last value after quiet period | At most one value per window (typically first) |
| Timer | Resets on each emission | Fixed window; new values don't reset it |
| Use case | Wait until user finishes / burst ends | Limit frequency of actions |
| Example | Search input | Button clicks |
| Delay | After last event | After first event in each window |

### Real-World Comparison

**Search Input (debounce preferred):**

```kotlin
// User types: "h" "e" "l" "l" "o"
//            100ms 100ms 100ms 100ms

// debounce(200ms):
// → Waits 200ms after "o" → searches "hello" (GOOD)

// throttleFirst(200ms):
// → Likely searches for the first character and then skips others within windows → BAD for search
```

**Button Clicks (throttle preferred):**

```kotlin
// User clicks rapidly: click---click---click---click
//                      0ms     50ms    100ms   150ms

// throttleFirst(500ms):
// → Processes first click, ignores others for 500ms (GOOD)

// debounce(500ms):
// → Waits 500ms after LAST click → action may feel delayed / unresponsive (BAD)
```

### Advanced Implementation Notes

The following operators are illustrative only. A production-ready implementation must consider dispatcher, structured concurrency, cancellation, and consistent time sources.

**Example of a simplified throttleLatest (emit latest value at most once per window):**

```kotlin
fun <T> Flow<T>.throttleLatest(windowDurationMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L
    var pending: T? = null

    suspend fun emitIfDue(now: Long) {
        if (pending != null && now - lastEmissionTime >= windowDurationMillis) {
            emit(pending as T)
            lastEmissionTime = now
            pending = null
        }
    }

    collect { value ->
        val now = System.currentTimeMillis()
        pending = value
        emitIfDue(now)
    }

    // On completion, you may choose to emit pending
    pending?.let { emit(it) }
}
```

**Example of debounce with immediate first emission (leading+trailing idea):**

```kotlin
fun <T> Flow<T>.debounceImmediate(timeoutMillis: Long): Flow<T> = channelFlow {
    var lastEmissionTime = 0L
    var pendingJob: Job? = null

    collect { value ->
        val now = System.currentTimeMillis()
        if (now - lastEmissionTime >= timeoutMillis) {
            // Immediate (leading) emission
            pendingJob?.cancel()
            trySend(value)
            lastEmissionTime = now
        } else {
            // Restart trailing emission
            pendingJob?.cancel()
            pendingJob = launch {
                delay(timeoutMillis - (now - lastEmissionTime))
                trySend(value)
                lastEmissionTime = System.currentTimeMillis()
            }
        }
    }
}
```

Again, this is an approximation used for explanation; real-world code should be tested with virtual time and aligned with your UX requirements.

### Combining Debounce and Throttle

**Example: Smart search with both**

```kotlin
class SmartSearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: Flow<List<Product>> = _searchQuery
        .throttleFirst(100)  // Drop ultra-frequent events (< 100ms)
        .debounce(300)       // Wait 300ms pause before searching
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
        }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

### Performance Considerations

**`debounce` - Memory efficient:**

```kotlin
// debounce keeps only the latest value
searchQuery
    .debounce(300)
    .collect { /* ... */ }

// Memory: O(1) - only latest value stored
```

**`throttle` - Drops values:**

```kotlin
// throttleFirst drops intermediate values
rapidUpdates
    .throttleFirst(1000)
    .collect { /* ... */ }

// If 100 updates in 1s → most are dropped
```

### Testing

**Test debounce:**

```kotlin
@Test
fun `debounce should emit last value after quiet period`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(500)  // Quiet period
    }.debounce(300)

    val result = flow.toList()

    assertEquals(listOf(3), result)  // Only last value
}
```

**Test throttleFirst (simplified):**

```kotlin
@Test
fun `throttleFirst should emit at most one value per window`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(600)
        emit(4)
    }.throttleFirst(500)

    val result = flow.toList()

    assertEquals(listOf(1, 4), result)
}
```

### Best Practices

**1. Choose appropriate timeout:**

```kotlin
// - Search: 300-500ms (feels responsive)
searchQuery.debounce(300)

// - Auto-save: 1000-2000ms (not too frequent)
document.debounce(2000)

// - Button click: 500-1000ms (prevents double-click)
button.throttleFirst(1000)
```

**2. Combine with other operators:**

```kotlin
searchQuery
    .debounce(300)
    .filter { it.length >= 2 }  // Min length
    .distinctUntilChanged()     // Avoid duplicate searches
    .flatMapLatest { search(it) }
```

**3. Handle cancellation:**

```kotlin
// debounce cancels pending delays on new values
searchQuery
    .debounce(300)
    .onEach { query ->
        // This runs only for values that weren't cancelled
        searchApi(query)
    }
    .launchIn(viewModelScope)
```

**English Summary**: `debounce` waits for a quiet period after the last emission (timer resets on each value) and emits the latest value. Throttling operators (e.g., `throttleFirst`) limit how often values are emitted (e.g., at most one value per window). Use `debounce` for search inputs, form validation, and auto-save (wait until user finishes). Use `throttle` for button clicks, location updates, and scroll events (rate limiting). `debounce` keeps the latest pending value; `throttleFirst` keeps the first in each window. Typical timeouts: search ~300ms, auto-save ~2s, button ~1s.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Flow Operators - Kotlin Documentation]("https://kotlinlang.org/docs/flow.html#intermediate-flow-operators")
- [Debounce and Throttle]("https://medium.com/androiddevelopers/effective-state-management-for-textfield-in-compose-d6e5b070fbe5")
- [[c-flow]]

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction
