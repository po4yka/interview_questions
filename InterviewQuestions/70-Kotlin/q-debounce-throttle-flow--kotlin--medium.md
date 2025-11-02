---
id: kotlin-046
title: "Debounce vs Throttle in Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [debounce, flow, operators, throttle]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-object-singleton-companion--kotlin--medium, q-request-coalescing-deduplication--kotlin--hard, q-suspend-functions-deep-dive--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [debounce, difficulty/medium, flow, kotlin, operators, throttle]
date created: Thursday, October 16th 2025, 4:20:35 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Question (EN)
> What is the difference between debounce and throttle in Kotlin Flow? When to use each?
# Вопрос (RU)
> В чем разница между debounce и throttle в Kotlin Flow? Когда использовать каждый?

---

## Answer (EN)

**Debounce** and **throttle** are time-based operators that control the rate of emissions from a Flow, but they work differently.

### Visual Comparison

```
Input:  A----B-C---D------E-F-G--------H
        |         |             |      |

debounce(500ms): Waits for quiet period
        --------C-----D---------G------H
        (Only emits after 500ms of silence)

throttle(500ms): Emits first, then pauses
        A---------C-----------E--------H
        (Emits first, ignores for 500ms)
```

### Debounce - Wait for Quiet Period

**Emits value only after specified time has passed without new emissions.**

```kotlin
val searchQuery = MutableStateFlow("")

searchQuery
    .debounce(300)  // Wait 300ms after last keystroke
    .collect { query ->
        searchApi(query)  // Only called after user stops typing
    }
```

**How it works:**
1. Value arrives → Start timer (300ms)
2. New value arrives → **Reset timer**
3. Timer completes → Emit latest value
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

**Emits first value, then ignores subsequent values for specified time.**

**Note:** Kotlin Flow doesn't have built-in `throttle`, but we can implement it:

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

**How it works:**
1. Value arrives → Emit immediately
2. Start ignore window (500ms)
3. Ignore all values during window
4. Window ends → Next value emits
5. Repeat

### Throttle Use Cases

**1. Button Click Prevention (debouncing clicks)**

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
// Only processes: first click (others ignored for 1s)
```

**2. Location Updates**

```kotlin
class LocationService {
    private val _locationUpdates = MutableSharedFlow<Location>()

    val sampledLocation: Flow<Location> = _locationUpdates
        .throttleFirst(5000)  // Only update every 5 seconds

    // GPS sends updates every 500ms, but we only need every 5s
}
```

**3. Scroll Events**

```kotlin
class ScrollViewModel : ViewModel() {
    private val _scrollEvents = MutableSharedFlow<Int>()

    val processedScrollEvents: Flow<Int> = _scrollEvents
        .throttleFirst(100)  // Process scroll every 100ms max

    fun onScroll(position: Int) {
        viewModelScope.launch {
            _scrollEvents.emit(position)
        }
    }
}
```

### Comparison Table

| Feature | debounce | throttle |
|---------|----------|----------|
| **Emits** | Last value after quiet period | First value, then pauses |
| **Timer** | Resets on each emission | Fixed window |
| **Use case** | Wait for user to finish | Rate limiting |
| **Example** | Search input | Button clicks |
| **Delay** | After last event | After first event |

### Real-World Comparison

**Search Input (debounce preferred):**

```kotlin
// User types: "h" "e" "l" "l" "o"
//            100ms 100ms 100ms 100ms

// debounce(200ms):
// → Waits 200ms after "o" → searches "hello" GOOD

// throttle(200ms):
// → Searches "h", ignores "e", "l", "l", searches "o" BAD
// Not useful for search!
```

**Button Clicks (throttle preferred):**

```kotlin
// User clicks rapidly: click---click---click---click
//                      0ms     50ms    100ms   150ms

// throttle(500ms):
// → Processes first click, ignores rest for 500ms GOOD

// debounce(500ms):
// → Waits 500ms after LAST click → processes too late BAD
```

### Advanced Implementations

**Custom throttleLast (emits last value in window):**

```kotlin
fun <T> Flow<T>.throttleLast(windowDuration: Long): Flow<T> = flow {
    var lastValue: T? = null
    var lastEmissionTime = 0L

    collect { value ->
        val currentTime = System.currentTimeMillis()
        lastValue = value

        if (currentTime - lastEmissionTime >= windowDuration) {
            emit(value)
            lastEmissionTime = currentTime
            lastValue = null
        }
    }

    // Emit last value if exists
    lastValue?.let { emit(it) }
}
```

**Debounce with immediate first emission:**

```kotlin
fun <T> Flow<T>.debounceImmediate(timeoutMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L

    collect { value ->
        val currentTime = System.currentTimeMillis()

        if (currentTime - lastEmissionTime >= timeoutMillis) {
            // Emit immediately if enough time passed
            emit(value)
            lastEmissionTime = currentTime
        } else {
            // Standard debounce behavior
            delay(timeoutMillis)
            emit(value)
        }
    }
}
```

### Combining Debounce and Throttle

**Example: Smart search with both**

```kotlin
class SmartSearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: Flow<List<Product>> = _searchQuery
        .throttleFirst(100)  // Ignore super-fast typing (< 100ms)
        .debounce(300)  // Then wait 300ms for user to pause
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
        }
}
```

### Performance Considerations

**debounce - Memory efficient:**

```kotlin
// debounce only keeps latest value
searchQuery
    .debounce(300)
    .collect { /* ... */ }

// Memory: O(1) - only latest value
```

**throttle - Can drop many values:**

```kotlin
// throttle drops intermediate values
rapidUpdates
    .throttleFirst(1000)
    .collect { /* ... */ }

// If 100 updates in 1s → 99 dropped
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

**Test throttle:**

```kotlin
@Test
fun `throttle should emit first value and ignore subsequent`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
        delay(600)  // New window
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
    .distinctUntilChanged()  // Avoid duplicate searches
    .flatMapLatest { search(it) }
```

**3. Handle cancellation:**

```kotlin
// debounce automatically cancels pending delays
searchQuery
    .debounce(300)
    .onEach { query ->
        // This only runs for values that weren't cancelled
        searchApi(query)
    }
    .launchIn(viewModelScope)
```

**English Summary**: `debounce` waits for quiet period after last emission (resets timer on each value). `throttle` emits first value, then ignores for fixed window. Use `debounce` for: search, form validation, auto-save (wait for user to finish). Use `throttle` for: button clicks, location updates, scroll events (rate limiting). debounce keeps latest value, throttle keeps first. Typical timeouts: search 300ms, auto-save 2s, button 1s.

## Ответ (RU)

**Debounce** и **throttle** — операторы основанные на времени, которые контролируют частоту эмиссий из Flow, но работают по-разному.

### Визуальное Сравнение

```
Вход:  A----B-C---D------E-F-G--------H
       |         |             |      |

debounce(500мс): Ждет периода тишины
       --------C-----D---------G------H
       (Эмитит только после 500мс тишины)

throttle(500мс): Эмитит первый, затем пауза
       A---------C-----------E--------H
       (Эмитит первый, игнорирует 500мс)
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
1. Значение приходит → Запуск таймера (300мс)
2. Новое значение приходит → **Сброс таймера**
3. Таймер завершается → Эмитится последнее значение
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
// Ищет только: "kotlin" (после паузы 300мс)
```

**2. Валидация формы**

```kotlin
class RegistrationViewModel : ViewModel() {
    private val email = MutableStateFlow("")

    val emailValidation: Flow<ValidationResult> = email
        .debounce(500)  // Ждать 500мс после того как пользователь перестал печатать
        .map { validateEmail(it) }
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

**Эмитит первое значение, затем игнорирует последующие значения на указанное время.**

**Примечание:** Kotlin Flow не имеет встроенного `throttle`, но мы можем его реализовать:

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

### Применение Throttle

**1. Предотвращение кликов по кнопке**

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
// Обрабатывает только: первый клик (остальные игнорируются на 1с)
```

**2. Обновления локации**

```kotlin
class LocationService {
    private val _locationUpdates = MutableSharedFlow<Location>()

    val sampledLocation: Flow<Location> = _locationUpdates
        .throttleFirst(5000)  // Обновлять только каждые 5 секунд

    // GPS отправляет обновления каждые 500мс, но нам нужны только каждые 5с
}
```

### Сравнительная Таблица

| Функция | debounce | throttle |
|---------|----------|----------|
| **Эмитит** | Последнее значение после периода тишины | Первое значение, затем пауза |
| **Таймер** | Сбрасывается при каждой эмиссии | Фиксированное окно |
| **Применение** | Ждать пока пользователь закончит | Ограничение частоты |
| **Пример** | Ввод поиска | Клики по кнопке |
| **Задержка** | После последнего события | После первого события |

### Сравнение В Реальном Мире

**Ввод поиска (предпочтителен debounce):**

```kotlin
// Пользователь печатает: "h" "e" "l" "l" "o"
//                        100мс 100мс 100мс 100мс

// debounce(200мс):
// → Ждет 200мс после "o" → ищет "hello" GOOD

// throttle(200мс):
// → Ищет "h", игнорирует "e", "l", "l", ищет "o" BAD
// Не полезно для поиска!
```

**Клики по кнопке (предпочтителен throttle):**

```kotlin
// Пользователь кликает быстро: click---click---click---click
//                               0мс     50мс    100мс   150мс

// throttle(500мс):
// → Обрабатывает первый клик, игнорирует остальные на 500мс GOOD

// debounce(500мс):
// → Ждет 500мс после ПОСЛЕДНЕГО клика → обрабатывает слишком поздно BAD
```

### Лучшие Практики

**1. Выбирайте подходящий таймаут:**

```kotlin
// - Поиск: 300-500мс (ощущается отзывчиво)
searchQuery.debounce(300)

// - Авто-сохранение: 1000-2000мс (не слишком часто)
document.debounce(2000)

// - Клик по кнопке: 500-1000мс (предотвращает двойной клик)
button.throttleFirst(1000)
```

**2. Комбинируйте с другими операторами:**

```kotlin
searchQuery
    .debounce(300)
    .filter { it.length >= 2 }  // Мин. длина
    .distinctUntilChanged()  // Избегать дублирующих поисков
    .flatMapLatest { search(it) }
```

### Продвинутые Реализации

**Пользовательский throttleLast (эмитит последнее значение в окне):**

```kotlin
fun <T> Flow<T>.throttleLast(windowDuration: Long): Flow<T> = flow {
    var lastValue: T? = null
    var lastEmissionTime = 0L

    collect { value ->
        val currentTime = System.currentTimeMillis()
        lastValue = value

        if (currentTime - lastEmissionTime >= windowDuration) {
            emit(value)
            lastEmissionTime = currentTime
            lastValue = null
        }
    }

    // Эмитировать последнее значение если существует
    lastValue?.let { emit(it) }
}
```

**Debounce с немедленной первой эмиссией:**

```kotlin
fun <T> Flow<T>.debounceImmediate(timeoutMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L

    collect { value ->
        val currentTime = System.currentTimeMillis()

        if (currentTime - lastEmissionTime >= timeoutMillis) {
            // Эмитировать немедленно если прошло достаточно времени
            emit(value)
            lastEmissionTime = currentTime
        } else {
            // Стандартное поведение debounce
            delay(timeoutMillis)
            emit(value)
        }
    }
}
```

### Комбинирование Debounce И Throttle

**Пример: Умный поиск с обоими**

```kotlin
class SmartSearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: Flow<List<Product>> = _searchQuery
        .throttleFirst(100)  // Игнорировать супербыструю печать (< 100мс)
        .debounce(300)  // Затем ждать 300мс пока пользователь приостановится
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
        }
}
```

### Соображения Производительности

**debounce - Эффективность по памяти:**

```kotlin
// debounce хранит только последнее значение
searchQuery
    .debounce(300)
    .collect { /* ... */ }

// Память: O(1) - только последнее значение
```

**throttle - Может отбрасывать много значений:**

```kotlin
// throttle отбрасывает промежуточные значения
rapidUpdates
    .throttleFirst(1000)
    .collect { /* ... */ }

// Если 100 обновлений за 1с → 99 отброшено
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

**Тест throttle:**

```kotlin
@Test
fun `throttle should emit first value and ignore subsequent`() = runTest {
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

**Краткое содержание**: `debounce` ждет период тишины после последней эмиссии (сбрасывает таймер на каждом значении). `throttle` эмитит первое значение, затем игнорирует на фиксированное окно. Используйте `debounce` для: поиска, валидации формы, авто-сохранения (ждать пока пользователь закончит). Используйте `throttle` для: кликов по кнопке, обновлений локации, событий прокрутки (ограничение частоты). Типичные таймауты: поиск 300мс, авто-сохранение 2с, кнопка 1с.

---

## References
- [Flow Operators - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#intermediate-flow-operators)
- [Debounce and Throttle](https://medium.com/androiddevelopers/effective-state-management-for-textfield-in-compose-d6e5b070fbe5)

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
-  - Flow
- [[q-flow-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

