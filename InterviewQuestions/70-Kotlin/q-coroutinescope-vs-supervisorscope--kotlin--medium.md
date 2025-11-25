---
id: kotlin-223
title: "coroutineScope vs supervisorScope / coroutineScope против supervisorScope"
aliases: ["coroutineScope vs supervisorScope", "coroutineScope против supervisorScope"]
topic: kotlin
subtopics: [coroutines, scope]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-await--kotlin--medium, c-concurrency, q-channel-pipelines--kotlin--hard]
created: 2025-10-15
updated: 2025-11-11
tags: [coroutines, difficulty/medium, error-handling, kotlin, scope]

date created: Friday, October 31st 2025, 6:32:26 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---

# Вопрос (RU)
> В чём разница между `coroutineScope` и `supervisorScope` в корутинах Kotlin?

# Question (EN)
> What is the difference between `coroutineScope` and `supervisorScope` in Kotlin coroutines?

## Ответ (RU)

`coroutineScope` и `supervisorScope` — это функции-билдеры для создания вложенных корутинных scope. Главное различие — обработка ошибок и влияние падения одной дочерней корутины на другие: в `coroutineScope` падение одной дочерней корутины по умолчанию отменяет все остальные, в `supervisorScope` остальные продолжают работать, пока вы явно не отмените их или не завершите scope.

Важно: в `supervisorScope` ошибка дочерней корутины не отменяет сиблингов, но если её не обработать локально внутри scope (например, в самой дочерней корутине или при `await()`), весь `supervisorScope` в итоге завершится с ошибкой.

### coroutineScope — Fail-fast Стратегия

Если любая дочерняя корутина бросает неперехваченное исключение, все остальные дочерние корутины в этом scope отменяются.

```kotlin
suspend fun fetchUserData() = coroutineScope {
    val profile = async { fetchProfile() }      // Корутина 1
    val settings = async { fetchSettings() }    // Корутина 2
    val friends = async { fetchFriends() }      // Корутина 3

    // Если fetchSettings() упадет (и исключение не будет перехвачено внутри), profile и friends ОТМЕНЯТСЯ
    UserData(
        profile = profile.await(),
        settings = settings.await(),
        friends = friends.await()
    )
}

// Использование
suspend fun useFetchUserData() {
    try {
        val data = fetchUserData()
        println("Success: $data")
    } catch (e: Exception) {
        println("Failed: ${e.message}")  // Вся операция провалится
    }
}
```

Поведение при ошибке:
1. `fetchSettings()` бросает исключение (и оно не перехвачено внутри корутины).
2. `coroutineScope` отменяет `profile` и `friends`.
3. Исключение пробрасывается наверх.
4. Вся функция `fetchUserData()` завершается с ошибкой.

### supervisorScope — Fail-tolerant Стратегия

Если одна дочерняя корутина падает, остальные продолжают работу: отмена не распространяется на сиблингов. Однако:
- упавшая дочерняя корутина завершится с исключением;
- если это исключение не обработать внутри scope (например, при `await()` или в `try-catch` внутри самой корутины), весь `supervisorScope` также завершится с ошибкой по окончании блока;
- чтобы получить частичный успех, ошибки дочерних корутин нужно обрабатывать локально.

```kotlin
suspend fun fetchUserDataTolerant() = supervisorScope {
    val profile = async { fetchProfile() }      // Корутина 1
    val settings = async { fetchSettings() }    // Корутина 2 (может упасть)
    val friends = async { fetchFriends() }      // Корутина 3

    // Даже если fetchSettings() упадет, profile и friends продолжат.
    // Для частичного успеха обрабатываем ошибку settings локально.
    UserData(
        profile = profile.await(),
        settings = try { settings.await() } catch (e: Exception) { null },
        friends = friends.await()
    )
}

// Использование
suspend fun useFetchUserDataTolerant() {
    val data = fetchUserDataTolerant()
    println("Success (partial): $data")  // Получим данные, даже если settings = null
}
```

Поведение при ошибке:
1. `fetchSettings()` бросает исключение.
2. `supervisorScope` не отменяет `profile` и `friends` автоматически.
3. `settings.await()` бросит исключение; если оно перехвачено, scope может завершиться успешно.
4. Если все критичные ошибки обработаны локально, функция может вернуть частичные данные.

### Сравнительная Таблица

| Аспект | `coroutineScope` | `supervisorScope` |
|--------|------------------|-------------------|
| Ошибка в дочерней корутине | Отменяет все остальные (fail-fast) | Остальные не отменяются автоматически |
| Пробрасывание исключений | Необработанное исключение завершает scope с ошибкой | Необработанное исключение завершит scope с ошибкой, но не отменит сиблингов; для частичного успеха нужны локальные обработчики |
| Use case | Все или ничего (all-or-nothing) | Частичный успех допустим |
| Примеры | Транзакции, критичные операции | Загрузка виджетов, метрики |

### Практические Примеры

#### Пример 1: Загрузка Экрана Профиля (`coroutineScope`)

Требование: если какая-то критичная часть упала, показываем ошибку.

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun loadProfile(userId: Int) {
        viewModelScope.launch {
            _uiState.value = ProfileUiState.Loading

            try {
                // coroutineScope: все критично, любая необработанная ошибка = fail
                val data = coroutineScope {
                    val profile = async { repository.getProfile(userId) }
                    val posts = async { repository.getPosts(userId) }
                    val followers = async { repository.getFollowers(userId) }

                    ProfileData(
                        profile = profile.await(),
                        posts = posts.await(),
                        followers = followers.await()
                    )
                }

                _uiState.value = ProfileUiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = ProfileUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class ProfileUiState {
    object Loading : ProfileUiState()
    data class Success(val data: ProfileData) : ProfileUiState()
    data class Error(val message: String) : ProfileUiState()
}
```

#### Пример 2: Дашборд С Виджетами (`supervisorScope`)

Требование: если один виджет упал, показываем остальные.

```kotlin
@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val analyticsRepo: AnalyticsRepository,
    private val weatherRepo: WeatherRepository,
    private val newsRepo: NewsRepository
) : ViewModel() {

    data class DashboardData(
        val analytics: Analytics? = null,
        val weather: Weather? = null,
        val news: List<Article>? = null
    )

    private val _dashboard = MutableStateFlow(DashboardData())
    val dashboard: StateFlow<DashboardData> = _dashboard.asStateFlow()

    fun loadDashboard() {
        viewModelScope.launch {
            // supervisorScope: каждый виджет независим; ошибки обрабатываем локально
            supervisorScope {
                // Виджет 1: Аналитика
                launch {
                    try {
                        val analytics = analyticsRepo.getAnalytics()
                        _dashboard.update { it.copy(analytics = analytics) }
                    } catch (e: Exception) {
                        Log.e("Dashboard", "Analytics failed: ${e.message}")
                    }
                }

                // Виджет 2: Погода
                launch {
                    try {
                        val weather = weatherRepo.getWeather()
                        _dashboard.update { it.copy(weather = weather) }
                    } catch (e: Exception) {
                        Log.e("Dashboard", "Weather failed: ${e.message}")
                    }
                }

                // Виджет 3: Новости
                launch {
                    try {
                        val news = newsRepo.getLatestNews()
                        _dashboard.update { it.copy(news = news) }
                    } catch (e: Exception) {
                        Log.e("Dashboard", "News failed: ${e.message}")
                    }
                }
            }
            // Все виджеты завершились (успешно или с ошибкой, но ошибки не обрушили весь экран)
        }
    }
}
```

#### Пример 3: Загрузка С Fallback (`supervisorScope` + `async`)

```kotlin
suspend fun loadUserWithFallback(userId: Int): User = supervisorScope {
    val primaryApi = async {
        delay(1000)
        primaryService.getUser(userId)
    }

    val fallbackApi = async {
        delay(2000)
        fallbackService.getUser(userId)
    }

    try {
        // Попытка получить из основного API (при успехе fallback все равно запущен, но результат можно игнорировать)
        primaryApi.await()
    } catch (e: Exception) {
        Log.w("API", "Primary failed, using fallback")
        // Если основной упал, используем fallback; его ошибка не отменяет primary и наоборот
        fallbackApi.await()
    }
}
```

### Вложенные Scope

```kotlin
suspend fun complexOperation() = coroutineScope {
    // Внешний scope: coroutineScope (все критично)

    val criticalData = async {
        // Критичные данные
        fetchCriticalData()
    }

    val optionalWidgets = async {
        // Внутренний scope: supervisorScope (опциональные виджеты)
        supervisorScope {
            val widget1 = async { fetchWidget1() }
            val widget2 = async { fetchWidget2() }
            val widget3 = async { fetchWidget3() }

            listOfNotNull(
                widget1.getOrNull(),
                widget2.getOrNull(),
                widget3.getOrNull()
            )
        }
    }

    AppData(
        critical = criticalData.await(),  // Обязательно
        widgets = optionalWidgets.await()  // Опционально
    )
}

suspend fun <T> Deferred<T>.getOrNull(): T? = try {
    await()
} catch (e: Exception) {
    null
}
```

### SupervisorJob Vs `supervisorScope`

Похожие, но разные концепции:

```kotlin
// SupervisorJob задаёт стратегию отмены для дочерних корутин: сбой одного ребёнка
// не отменяет автоматически других (как и supervisorScope).

val scope = CoroutineScope(SupervisorJob())
scope.launch {
    val a = async { throw Exception("Error") }
    val b = async {
        delay(1000)
        "Success"
    }

    try {
        a.await()
    } catch (e: Exception) {
        // Ошибка a обработана локально, scope не падает
    }

    // b не будет отменён из-за ошибки a и успешно завершится
    println(b.await())  // "Success"
}

// supervisorScope — suspend-билдер с теми же семантиками над дочерними корутинами,
// но ограниченный временем жизни вызова suspend-функции.
suspend fun correct() = supervisorScope {
    val a = async { throw Exception("Error") }
    val b = async { delay(1000); "Success" }

    try {
        a.await()
    } catch (e: Exception) {
        // обрабатываем локально
    }

    println(b.await())  // "Success" - b не отменится
}
```

Ключевые моменты:
- И `SupervisorJob`, и `supervisorScope` распространяют сбой родителя на детей, но не сбой одного ребёнка на других.
- Необработанное исключение дочерней корутины внутри `supervisorScope` приведёт к ошибочному завершению scope при выходе из него, если не перехвачено внутри.
- Семантика одинакова для `launch` и `async`; важно корректно обрабатывать исключения (например, через `await()` внутри try-catch).

### `withContext` Vs `coroutineScope` / `supervisorScope`

```kotlin
// withContext - для смены контекста (Dispatcher, например) + структурное ожидание, как у coroutineScope
suspend fun loadData() = withContext(Dispatchers.IO) {
    repository.fetchData()
}

// coroutineScope - для группировки корутин с fail-fast
suspend fun loadAll() = coroutineScope {
    val a = async { loadA() }
    val b = async { loadB() }
    Pair(a.await(), b.await())
}

// supervisorScope - для независимых задач (ошибки обрабатываются локально)
suspend fun loadIndependent() = supervisorScope {
    launch { task1() }
    launch { task2() }
    launch { task3() }
}
```

### Обработка Ошибок

```kotlin
// coroutineScope: один try-catch на всю операцию
suspend fun loadWithCoroutineScope() {
    try {
        coroutineScope {
            async { task1() }
            async { task2() }
        }
    } catch (e: Exception) {
        // Любая необработанная ошибка дочерней корутины попадет сюда
    }
}

// supervisorScope: локальная обработка для частичного успеха
suspend fun loadWithSupervisorScope() = supervisorScope {
    val result1 = async { task1() }
    val result2 = async { task2() }

    val data1 = try {
        result1.await()
    } catch (e: Exception) {
        null
    }

    val data2 = try {
        result2.await()
    } catch (e: Exception) {
        null
    }

    Pair(data1, data2)
}
```

### Тестирование

```kotlin
@Test
fun `coroutineScope cancels all on failure`() = runTest {
    var task2Executed = false

    val exception = assertFailsWith<Exception> {
        coroutineScope {
            async { throw Exception("Task 1 failed") }
            async {
                delay(1000)
                task2Executed = true
            }
        }
    }

    assertEquals("Task 1 failed", exception.message)
    assertFalse(task2Executed)  // Task 2 был отменен
}

@Test
fun `supervisorScope continues siblings on failure when errors handled`() = runTest {
    var task2Executed = false

    supervisorScope {
        val job1 = async { throw Exception("Task 1 failed") }
        val job2 = async {
            delay(100)
            task2Executed = true
        }

        // Обрабатываем ошибку первой корутины, чтобы она не завершила весь scope
        try {
            job1.await()
        } catch (e: Exception) {
            // ignore
        }

        job2.await()
    }

    assertTrue(task2Executed)  // Task 2 завершился
}
```

## Answer (EN)

`coroutineScope` and `supervisorScope` are suspend builder functions for creating nested coroutine scopes. The key difference is how they propagate failures between siblings.

- In `coroutineScope`, if any child coroutine fails with an unhandled exception, the scope is cancelled, all siblings are cancelled, and the exception is rethrown (fail-fast, all-or-nothing).
- In `supervisorScope`, a failure of one child does not automatically cancel its siblings. Siblings can continue; failed children complete exceptionally and must be observed/handled (for example, via `await()` in `try/catch` or local handling inside the child) if you want partial success. An unhandled child exception inside the `supervisorScope` block will still cause the scope to complete exceptionally when the block finishes.

### Comparative Table

| Aspect | `coroutineScope` | `supervisorScope` |
|--------|------------------|-------------------|
| Child failure | Cancels all other children (fail-fast) | Does not cancel siblings automatically |
| Exception propagation | Unhandled child exception fails the whole scope | Unhandled child exception fails the scope on completion, but siblings are not retro-cancelled; handle locally for partial success |
| Typical use case | All-or-nothing operations | Partial success, independent tasks |
| Examples | Transactions, critical data loading | Dashboard widgets, metrics, best-effort tasks |

### Practical Examples

#### Example 1: Profile Screen Loading (`coroutineScope`)

Requirement: if any critical part fails, show an error.

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun loadProfile(userId: Int) {
        viewModelScope.launch {
            _uiState.value = ProfileUiState.Loading

            try {
                val data = coroutineScope {
                    val profile = async { repository.getProfile(userId) }
                    val posts = async { repository.getPosts(userId) }
                    val followers = async { repository.getFollowers(userId) }

                    ProfileData(
                        profile = profile.await(),
                        posts = posts.await(),
                        followers = followers.await()
                    )
                }

                _uiState.value = ProfileUiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = ProfileUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class ProfileUiState {
    object Loading : ProfileUiState()
    data class Success(val data: ProfileData) : ProfileUiState()
    data class Error(val message: String) : ProfileUiState()
}
```

#### Example 2: Dashboard Widgets (`supervisorScope`)

Requirement: if one widget fails, show the others.

```kotlin
@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val analyticsRepo: AnalyticsRepository,
    private val weatherRepo: WeatherRepository,
    private val newsRepo: NewsRepository
) : ViewModel() {

    data class DashboardData(
        val analytics: Analytics? = null,
        val weather: Weather? = null,
        val news: List<Article>? = null
    )

    private val _dashboard = MutableStateFlow(DashboardData())
    val dashboard: StateFlow<DashboardData> = _dashboard.asStateFlow()

    fun loadDashboard() {
        viewModelScope.launch {
            supervisorScope {
                launch {
                    try {
                        val analytics = analyticsRepo.getAnalytics()
                        _dashboard.update { it.copy(analytics = analytics) }
                    } catch (e: Exception) {
                        Log.e("Dashboard", "Analytics failed: ${e.message}")
                    }
                }

                launch {
                    try {
                        val weather = weatherRepo.getWeather()
                        _dashboard.update { it.copy(weather = weather) }
                    } catch (e: Exception) {
                        Log.e("Dashboard", "Weather failed: ${e.message}")
                    }
                }

                launch {
                    try {
                        val news = newsRepo.getLatestNews()
                        _dashboard.update { it.copy(news = news) }
                    } catch (e: Exception) {
                        Log.e("Dashboard", "News failed: ${e.message}")
                    }
                }
            }
        }
    }
}
```

#### Example 3: Fallback Loading (`supervisorScope` + `async`)

```kotlin
suspend fun loadUserWithFallback(userId: Int): User = supervisorScope {
    val primaryApi = async {
        delay(1000)
        primaryService.getUser(userId)
    }

    val fallbackApi = async {
        delay(2000)
        fallbackService.getUser(userId)
    }

    try {
        // Try primary first; fallback is started but its result will be ignored if primary succeeds.
        primaryApi.await()
    } catch (e: Exception) {
        Log.w("API", "Primary failed, using fallback")
        // If primary fails, rely on fallback; failure of one does not cancel the other.
        fallbackApi.await()
    }
}
```

### Nested Scopes

```kotlin
suspend fun complexOperation() = coroutineScope {
    val criticalData = async {
        fetchCriticalData()
    }

    val optionalWidgets = async {
        supervisorScope {
            val widget1 = async { fetchWidget1() }
            val widget2 = async { fetchWidget2() }
            val widget3 = async { fetchWidget3() }

            listOfNotNull(
                widget1.getOrNull(),
                widget2.getOrNull(),
                widget3.getOrNull()
            )
        }
    }

    AppData(
        critical = criticalData.await(),
        widgets = optionalWidgets.await()
    )
}

suspend fun <T> Deferred<T>.getOrNull(): T? = try {
    await()
} catch (e: Exception) {
    null
}
```

### SupervisorJob Vs `supervisorScope`

```kotlin
val scope = CoroutineScope(SupervisorJob())
scope.launch {
    val a = async { throw Exception("Error") }
    val b = async {
        delay(1000)
        "Success"
    }

    try {
        a.await()
    } catch (e: Exception) {
        // child failure handled locally, scope survives
    }

    println(b.await())  // "Success"
}

suspend fun correct() = supervisorScope {
    val a = async { throw Exception("Error") }
    val b = async { delay(1000); "Success" }

    try {
        a.await()
    } catch (e: Exception) {
        // handle locally
    }

    println(b.await())  // "Success"
}
```

Key points:
- Both `SupervisorJob` and `supervisorScope` propagate parent failure to children, but do not propagate one child's failure to siblings.
- An unhandled child exception inside a `supervisorScope` will cause the scope to complete exceptionally when the block ends, unless it is caught inside the scope.
- Semantics are consistent for both `launch` and `async`; make sure to observe and handle exceptions properly (for example, via `await()` in `try/catch`).

### `withContext` Vs `coroutineScope` / `supervisorScope`

```kotlin
// withContext: switch context (for example, dispatcher) and run a block, structurally similar to coroutineScope
suspend fun loadData() = withContext(Dispatchers.IO) {
    repository.fetchData()
}

// coroutineScope: group children with fail-fast semantics
suspend fun loadAll() = coroutineScope {
    val a = async { loadA() }
    val b = async { loadB() }
    Pair(a.await(), b.await())
}

// supervisorScope: group independent tasks with local error handling
suspend fun loadIndependent() = supervisorScope {
    launch { task1() }
    launch { task2() }
    launch { task3() }
}
```

### Error Handling

```kotlin
// coroutineScope: one try-catch for the whole group
suspend fun loadWithCoroutineScope() {
    try {
        coroutineScope {
            async { task1() }
            async { task2() }
        }
    } catch (e: Exception) {
        // any unhandled child exception ends up here
    }
}

// supervisorScope: local handling for partial success
suspend fun loadWithSupervisorScope() = supervisorScope {
    val result1 = async { task1() }
    val result2 = async { task2() }

    val data1 = try {
        result1.await()
    } catch (e: Exception) {
        null
    }

    val data2 = try {
        result2.await()
    } catch (e: Exception) {
        null
    }

    Pair(data1, data2)
}
```

### Testing

```kotlin
@Test
fun `coroutineScope cancels all on failure`() = runTest {
    var task2Executed = false

    val exception = assertFailsWith<Exception> {
        coroutineScope {
            async { throw Exception("Task 1 failed") }
            async {
                delay(1000)
                task2Executed = true
            }
        }
    }

    assertEquals("Task 1 failed", exception.message)
    assertFalse(task2Executed)
}

@Test
fun `supervisorScope continues siblings on failure when errors handled`() = runTest {
    var task2Executed = false

    supervisorScope {
        val job1 = async { throw Exception("Task 1 failed") }
        val job2 = async {
            delay(100)
            task2Executed = true
        }

        try {
            job1.await()
        } catch (e: Exception) {
            // ignore
        }

        job2.await()
    }

    assertTrue(task2Executed)
}
```

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-concurrency]]

## Related Questions

- [[q-channel-pipelines--kotlin--hard]]
- [[q-inline-value-classes-performance--kotlin--medium]]
- [[q-kotlin-inline-functions--kotlin--medium]]

## Дополнительные Вопросы (RU)
- В чём ключевые отличия такого подхода от Java-подходов к конкурентности?
- В каких практических сценариях вы бы использовали `coroutineScope` и `supervisorScope`?
- Как избежать распространённых ошибок при использовании этих scope?
## Ссылки (RU)
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
## Связанные Вопросы (RU)