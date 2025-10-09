---
tags:
  - kotlin
  - coroutines
  - scope
  - error-handling
  - structured-concurrency
difficulty: medium
status: reviewed
---

# coroutineScope vs supervisorScope: обработка ошибок

**English**: Difference between coroutineScope and supervisorScope

## Answer

`coroutineScope` и `supervisorScope` — это функции-билдеры для создания вложенных корутинных scope. Главное различие — **обработка ошибок**: в `coroutineScope` падение одной дочерней корутины отменяет все остальные, в `supervisorScope` остальные продолжают работать.

### coroutineScope — fail-fast стратегия

Если **любая** дочерняя корутина бросает исключение, **все** остальные отменяются.

```kotlin
suspend fun fetchUserData() = coroutineScope {
    val profile = async { fetchProfile() }      // Корутина 1
    val settings = async { fetchSettings() }    // Корутина 2
    val friends = async { fetchFriends() }      // Корутина 3

    // Если fetchSettings() упадет, profile и friends ОТМЕНЯТСЯ
    UserData(
        profile = profile.await(),
        settings = settings.await(),
        friends = friends.await()
    )
}

// Использование
try {
    val data = fetchUserData()
    println("Success: $data")
} catch (e: Exception) {
    println("Failed: ${e.message}")  // Вся операция провалится
}
```

**Поведение при ошибке:**
1. `fetchSettings()` бросает исключение
2. `coroutineScope` **отменяет** `profile` и `friends`
3. Исключение **пробрасывается** наверх
4. Вся функция `fetchUserData()` завершается с ошибкой

### supervisorScope — fail-tolerant стратегия

Если одна дочерняя корутина падает, **остальные продолжают** работу.

```kotlin
suspend fun fetchUserDataTolerant() = supervisorScope {
    val profile = async { fetchProfile() }      // Корутина 1
    val settings = async { fetchSettings() }    // Корутина 2 (может упасть)
    val friends = async { fetchFriends() }      // Корутина 3

    // Даже если fetchSettings() упадет, profile и friends продолжат
    UserData(
        profile = profile.await(),
        settings = try { settings.await() } catch (e: Exception) { null },
        friends = friends.await()
    )
}

// Использование
val data = fetchUserDataTolerant()
println("Success (partial): $data")  // Получим данные, даже если settings = null
```

**Поведение при ошибке:**
1. `fetchSettings()` бросает исключение
2. `supervisorScope` **НЕ отменяет** `profile` и `friends`
3. `settings.await()` **бросит** исключение (нужен try-catch)
4. Функция **продолжает** работу с частичными данными

### Сравнительная таблица

| Аспект | coroutineScope | supervisorScope |
|--------|----------------|-----------------|
| **Ошибка в дочерней корутине** | Отменяет все остальные | Остальные продолжают |
| **Пробрасывание исключений** | Автоматически | Нужен try-catch на await() |
| **Use case** | Все или ничего (all-or-nothing) | Частичный успех допустим |
| **Примеры** | Транзакции, критичные операции | Загрузка виджетов, метрики |

### Практические примеры

#### Пример 1: Загрузка экрана профиля (coroutineScope)

**Требование**: Если какая-то критичная часть упала, показываем ошибку.

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
                // coroutineScope: все критично, любая ошибка = fail
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

#### Пример 2: Дашборд с виджетами (supervisorScope)

**Требование**: Если один виджет упал, показываем остальные.

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
            // supervisorScope: каждый виджет независим
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
            // Все виджеты завершились (успешно или с ошибкой)
        }
    }
}
```

#### Пример 3: Загрузка с fallback (supervisorScope + async)

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
        // Попытка получить из основного API
        primaryApi.await()
    } catch (e: Exception) {
        Log.w("API", "Primary failed, using fallback")
        // Если основной упал, используем fallback
        fallbackApi.await()
    }
}
```

### Вложенные scope

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
                widget1.await().getOrNull(),
                widget2.await().getOrNull(),
                widget3.await().getOrNull()
            )
        }
    }

    AppData(
        critical = criticalData.await(),  // Обязательно
        widgets = optionalWidgets.await()  // Опционально
    )
}

fun <T> Deferred<T>.getOrNull(): T? = try {
    await()
} catch (e: Exception) {
    null
}
```

### SupervisorJob vs supervisorScope

Похожие, но разные концепции:

```kotlin
// ❌ НЕПРАВИЛЬНО - SupervisorJob не работает с async
val scope = CoroutineScope(SupervisorJob())
scope.launch {
    val a = async { throw Exception("Error") }
    val b = async { delay(1000); "Success" }

    // b ВСЕ РАВНО отменится! SupervisorJob работает только для launch, не async
    println(b.await())
}

// ✅ ПРАВИЛЬНО - supervisorScope
suspend fun correct() = supervisorScope {
    val a = async { throw Exception("Error") }
    val b = async { delay(1000); "Success" }

    try { a.await() } catch (e: Exception) { }
    println(b.await())  // "Success" - b не отменится
}
```

### withContext vs coroutineScope/supervisorScope

```kotlin
// withContext - для смены контекста (Dispatcher, например)
suspend fun loadData() = withContext(Dispatchers.IO) {
    repository.fetchData()
}

// coroutineScope - для группировки корутин с fail-fast
suspend fun loadAll() = coroutineScope {
    val a = async { loadA() }
    val b = async { loadB() }
    Pair(a.await(), b.await())
}

// supervisorScope - для независимых задач
suspend fun loadIndependent() = supervisorScope {
    launch { task1() }
    launch { task2() }
    launch { task3() }
}
```

### Обработка ошибок

```kotlin
// coroutineScope: один try-catch на всю операцию
suspend fun loadWithCoroutineScope() {
    try {
        coroutineScope {
            async { task1() }
            async { task2() }
        }
    } catch (e: Exception) {
        // Любая ошибка попадет сюда
    }
}

// supervisorScope: try-catch на каждый await
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

    assertThrows<Exception> {
        coroutineScope {
            async { throw Exception("Task 1 failed") }
            async {
                delay(1000)
                task2Executed = true
            }
        }
    }

    assertFalse(task2Executed)  // Task 2 был отменен
}

@Test
fun `supervisorScope continues on failure`() = runTest {
    var task2Executed = false

    supervisorScope {
        async { throw Exception("Task 1 failed") }
        async {
            delay(100)
            task2Executed = true
        }
    }

    assertTrue(task2Executed)  // Task 2 завершился
}
```

### Best Practices

**1. Используйте coroutineScope для связанных операций**

```kotlin
// ✅ ПРАВИЛЬНО - все данные нужны для результата
suspend fun loadOrder(orderId: Int) = coroutineScope {
    val order = async { orderRepo.getOrder(orderId) }
    val customer = async { customerRepo.getCustomer(order.await().customerId) }
    val items = async { itemRepo.getItems(orderId) }

    OrderDetails(order.await(), customer.await(), items.await())
}
```

**2. Используйте supervisorScope для независимых задач**

```kotlin
// ✅ ПРАВИЛЬНО - виджеты независимы
suspend fun loadHomeScreen() = supervisorScope {
    launch { loadBanner() }
    launch { loadCategories() }
    launch { loadRecommendations() }
}
```

**3. Не смешивайте стратегии**

```kotlin
// ❌ НЕПРАВИЛЬНО - непонятное поведение
suspend fun mixed() = supervisorScope {
    val a = async {
        coroutineScope {
            async { task1() }
            async { task2() }
        }
    }
}
```

**English**: `coroutineScope` creates scope where **any child failure cancels all** siblings (fail-fast). `supervisorScope` creates scope where **children are independent** - one failure doesn't cancel others (fail-tolerant). Use `coroutineScope` for all-or-nothing operations (transactions, critical data loading). Use `supervisorScope` for independent tasks (dashboard widgets, metrics collection). In `coroutineScope`, one try-catch wraps entire block. In `supervisorScope`, need try-catch on each `await()`. `SupervisorJob` doesn't work with `async` - use `supervisorScope` instead.

