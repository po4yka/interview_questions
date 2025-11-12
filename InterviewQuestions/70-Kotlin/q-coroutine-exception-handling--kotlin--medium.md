---
id: kotlin-042
title: "Coroutine Exception Handling / Обработка исключений в корутинах"
aliases: ["Coroutine Exception Handling", "Обработка исключений в корутинах"]
topic: kotlin
subtopics: [coroutines, error-handling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority
status: draft
moc: moc-kotlin
related: [c--kotlin--medium, c-concurrency, q-supervisor-scope-vs-coroutine-scope--kotlin--medium]
created: 2025-10-06
updated: 2025-11-11
tags: [kotlin, coroutines, difficulty/medium, error-handling]

---

# Вопрос (RU)
> Как работает обработка исключений в Kotlin корутинах? В чем разница между coroutineScope и supervisorScope?

---

# Question (EN)
> How does exception handling work in Kotlin `Coroutines`? What is the difference between coroutineScope and supervisorScope?

## Ответ (RU)

Обработка исключений в корутинах следует специфичным правилам в зависимости от используемого билдера и скоупа. См. также [[c--kotlin--medium]] и [[c-concurrency]].

### Правила распространения исключений

**1. `launch` - Исключение немедленно завершает родительский scope**

```kotlin
viewModelScope.launch {
    launch {
        throw Exception("Child failed")  // Исключение в дочерней корутине завершает родительский scope
    }

    delay(1000)
    println("Это никогда не выполнится")  // Никогда не достигается
}
```

**2. `async` - Хранит исключение до `await()`**

```kotlin
viewModelScope.launch {
    val deferred = async {
        throw Exception("Async failed")  // Исключение сохранено до await()
    }

    delay(1000)
    println("Это выполнится")  // Все еще выполняется

    deferred.await()  // Исключение выброшено здесь
}
```

### try-catch в корутинах

**Работает для прямого (suspending) кода в той же корутине:**

```kotlin
viewModelScope.launch {
    try {
        val result = suspendingFunction()  // Поймано здесь
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**НЕ перехватывает исключения из асинхронно запущенных дочерних корутин:**

```kotlin
viewModelScope.launch {
    try {
        launch {
            throw Exception("Failed")  // Исключение уходит вверх по иерархии, не попадая в этот catch
        }
    } catch (e: Exception) {
        // Никогда не достигается, т.к. исключение выбрасывается после выхода из try-блока
    }
}
```

### coroutineScope vs supervisorScope

**`coroutineScope` - Отменяет всех братьев при сбое**

```kotlin
viewModelScope.launch {
    try {
        coroutineScope {
            launch {
                delay(1000)
                println("Task 1 complete")  // Не печатает, если Task 2 падает
            }

            launch {
                throw Exception("Task 2 failed")  // Отменяет Task 1 и завершает coroutineScope с этим исключением
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Caught: Task 2 failed
    }
}
```

**`supervisorScope` - Братья продолжают при сбое**

```kotlin
viewModelScope.launch {
    supervisorScope {
        launch {
            delay(1000)
            println("Task 1 complete")  // Все еще печатает, даже если другая корутина упала
        }

        launch {
            throw Exception("Task 2 failed")  // Не отменяет Task 1
        }
    }
}
```

### CoroutineExceptionHandler

**Глобальный обработчик для неперехваченных исключений в корнях корутин (обычно `launch`):**

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: ${exception.message}")
}

// Корневая корутина: исключение обрабатывается CoroutineExceptionHandler
viewModelScope.launch(handler) {
    throw Exception("Failed")  // Поймано handler'ом
}

// Для async handler НЕ вызывается, когда исключение захвачено; 
// оно перебрасывается при await(), где его нужно обработать явно.
viewModelScope.async(handler) {
    throw Exception("Failed")  // Handler НЕ вызывается здесь; обработка вокруг await()
}
```

### Примеры из реальной практики

**Пример 1: Параллельные запросы с `supervisorScope`**

```kotlin
class ProductViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            supervisorScope {
                // Загружаем несколько сущностей параллельно
                launch {
                    try {
                        val products = repository.getProducts()
                        _products.value = products
                    } catch (e: Exception) {
                        _productsError.value = e
                    }
                }

                launch {
                    try {
                        val categories = repository.getCategories()
                        _categories.value = categories
                    } catch (e: Exception) {
                        _categoriesError.value = e
                    }
                }

                // Если одна задача падает, другая продолжает
            }
        }
    }
}
```

**Пример 2: Последовательные операции с `coroutineScope`**

```kotlin
suspend fun processOrder(order: Order) = coroutineScope {
    // Все шаги должны успешно выполниться
    val validated = validateOrder(order)
    val processed = processPayment(validated)
    val confirmed = confirmOrder(processed)

    // Если любой шаг падает, весь scope завершается с этим исключением
    confirmed
}
```

**Пример 3: Обработчик исключений для логирования**

```kotlin
class MyViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        Log.e("MyViewModel", "Error", exception)
        analytics.logError(exception)
        _errorState.value = exception.toErrorMessage()
    }

    fun loadData() {
        viewModelScope.launch(exceptionHandler) {
            repository.getData()
        }
    }
}
```

**Пример 4: Смешанный подход**

```kotlin
fun loadDashboard() {
    viewModelScope.launch {
        supervisorScope {
            // Критичные данные — обрабатываем по отдельности
            launch {
                try {
                    _userData.value = userRepo.getUser()
                } catch (e: Exception) {
                    _userData.value = User.Error
                }
            }

            // Необязательные данные — могут упасть, не влияя на остальные
            launch {
                _notifications.value = notificationRepo.getNotifications()
            }
        }
    }
}
```

### Лучшие практики

**1. Используйте `supervisorScope` для независимых параллельных задач**

```kotlin
// ХОРОШО: Независимые задачи продолжаются, если одна падает
supervisorScope {
    launch { loadProducts() }
    launch { loadCategories() }
    launch { loadBanners() }
}
```

**2. Используйте `coroutineScope` для зависимых последовательных задач**

```kotlin
// ХОРОШО: Последовательные шаги в одной корутине
coroutineScope {
    val user = getUser()
    val profile = getProfile(user.id)
    val settings = getSettings(user.id)
}
```

**3. Обрабатывайте исключения на соответствующем уровне**

```kotlin
// ХОРОШО: Обработка на уровне UI/entry
viewModelScope.launch {
    try {
        val data = repository.getData()
        _uiState.value = UiState.Success(data)
    } catch (e: Exception) {
        _uiState.value = UiState.Error(e.message)
    }
}
```

**Краткое summary**: Исключения в корутинах: `launch` завершает родительский scope при неперехваченном исключении, `async` сохраняет исключение до `await()`. `try-catch` работает для кода в той же корутине, но не для отдельно запущенных дочерних корутин. `coroutineScope` отменяет всех братьев при сбое одного ребенка. `supervisorScope` позволяет братьям продолжить при сбое одного ребенка. `CoroutineExceptionHandler` используется для обработки неперехваченных исключений в корневых корутинах `launch` и не применяется к `async` до вызова `await()`. Используйте `supervisorScope` для независимых параллельных задач, `coroutineScope` для зависимых последовательных задач и обрабатывайте исключения на подходящем уровне абстракции.

---

## Answer (EN)

Exception handling in coroutines follows specific rules based on the coroutine builder and scope used. See also [[c--kotlin--medium]] and [[c-concurrency]].

### Exception Propagation Rules

**1. `launch` - Uncaught exception immediately completes the parent scope exceptionally**

```kotlin
viewModelScope.launch {
    launch {
        throw Exception("Child failed")  // Exception in child completes parent scope with failure
    }

    delay(1000)
    println("This never executes")  // Never reached
}
```

**2. `async` - Stores exception until `await()`**

```kotlin
viewModelScope.launch {
    val deferred = async {
        throw Exception("Async failed")  // Exception stored until await()
    }

    delay(1000)
    println("This executes")  // Still executes

    deferred.await()  // Exception thrown here
}
```

### Try-catch in Coroutines

**Works for direct (suspending) code in the same coroutine:**

```kotlin
viewModelScope.launch {
    try {
        val result = suspendingFunction()  // Caught here
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**Does NOT catch exceptions from separately launched child coroutines:**

```kotlin
viewModelScope.launch {
    try {
        launch {
            throw Exception("Failed")  // Exception propagates up the hierarchy, not into this catch
        }
    } catch (e: Exception) {
        // Never reached, because the exception is reported after the try block completes
    }
}
```

### coroutineScope vs supervisorScope

**`coroutineScope` - Cancels all siblings on failure**

```kotlin
viewModelScope.launch {
    try {
        coroutineScope {
            launch {
                delay(1000)
                println("Task 1 complete")  // Will not print if Task 2 fails
            }

            launch {
                throw Exception("Task 2 failed")  // Cancels Task 1 and completes coroutineScope with this exception
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Caught: Task 2 failed
    }
}
```

**`supervisorScope` - Siblings continue on failure**

```kotlin
viewModelScope.launch {
    supervisorScope {
        launch {
            delay(1000)
            println("Task 1 complete")  // Still prints even if another child fails
        }

        launch {
            throw Exception("Task 2 failed")  // Does not cancel Task 1
        }
    }
}
```

### CoroutineExceptionHandler

**Global-like handler for uncaught exceptions in root coroutines (typically `launch`):**

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: ${exception.message}")
}

// Root coroutine: exception is handled by CoroutineExceptionHandler
viewModelScope.launch(handler) {
    throw Exception("Failed")  // Caught by handler
}

// For async, the handler is NOT invoked when the exception is captured;
// it is rethrown on await(), where you must handle it explicitly.
viewModelScope.async(handler) {
    throw Exception("Failed")  // Handler NOT called here; handle around await()
}
```

### Real-World Examples

**Example 1: Parallel requests with `supervisorScope`**

```kotlin
class ProductViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            supervisorScope {
                // Load multiple things in parallel
                launch {
                    try {
                        val products = repository.getProducts()
                        _products.value = products
                    } catch (e: Exception) {
                        _productsError.value = e
                    }
                }

                launch {
                    try {
                        val categories = repository.getCategories()
                        _categories.value = categories
                    } catch (e: Exception) {
                        _categoriesError.value = e
                    }
                }

                // If one fails, the other continues
            }
        }
    }
}
```

**Example 2: Sequential operations with `coroutineScope`**

```kotlin
suspend fun processOrder(order: Order) = coroutineScope {
    // All steps must succeed
    val validated = validateOrder(order)
    val processed = processPayment(validated)
    val confirmed = confirmOrder(processed)

    // If any step fails, the scope completes with that exception
    confirmed
}
```

**Example 3: Exception handler for logging**

```kotlin
class MyViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        Log.e("MyViewModel", "Error", exception)
        analytics.logError(exception)
        _errorState.value = exception.toErrorMessage()
    }

    fun loadData() {
        viewModelScope.launch(exceptionHandler) {
            repository.getData()
        }
    }
}
```

**Example 4: Mixed approach**

```kotlin
fun loadDashboard() {
    viewModelScope.launch {
        supervisorScope {
            // Critical data - handle individually
            launch {
                try {
                    _userData.value = userRepo.getUser()
                } catch (e: Exception) {
                    _userData.value = User.Error
                }
            }

            // Optional data - may fail without affecting others
            launch {
                _notifications.value = notificationRepo.getNotifications()
            }
        }
    }
}
```

### Best Practices

**1. Use `supervisorScope` for independent parallel tasks**

```kotlin
// GOOD: Independent tasks can fail without cancelling others
supervisorScope {
    launch { loadProducts() }
    launch { loadCategories() }
    launch { loadBanners() }
}
```

**2. Use `coroutineScope` for dependent sequential tasks**

```kotlin
// GOOD: Sequential steps in a single coroutine
coroutineScope {
    val user = getUser()
    val profile = getProfile(user.id)
    val settings = getSettings(user.id)
}
```

**3. Handle exceptions at the appropriate level**

```kotlin
// GOOD: Handle at UI/entry level
viewModelScope.launch {
    try {
        val data = repository.getData()
        _uiState.value = UiState.Success(data)
    } catch (e: Exception) {
        _uiState.value = UiState.Error(e.message)
    }
}
```

**English Summary**: Exceptions in coroutines: `launch` completes its parent scope exceptionally on uncaught exceptions; `async` stores exceptions until `await()`. `try-catch` works for code executed within the same coroutine, not for separately launched child coroutines. `coroutineScope` cancels all siblings on failure of one child. `supervisorScope` lets siblings continue when one child fails. `CoroutineExceptionHandler` handles uncaught exceptions in root/launch coroutines and is not used for `async` until `await()`. Use `supervisorScope` for independent parallel tasks, `coroutineScope` for dependent sequential tasks, and handle exceptions at the appropriate level.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [`Coroutine` Exceptions - Kotlin Documentation](https://kotlinlang.org/docs/exception-handling.html)
- [CoroutineExceptionHandler](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-exception-handler/)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - `Coroutines`

### Related (Medium)
- [[q-flow-exception-handling--kotlin--medium]] - `Flow`
- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]] - `Coroutines`
- [[q-coroutine-timeout-withtimeout--kotlin--medium]] - `Coroutines`
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]] - `Coroutines`
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - `Coroutine` dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs `Context`
- [[q-coroutine-context-explained--kotlin--medium]] - CoroutineContext explained

### Advanced (Harder)
- [[q-structured-concurrency--kotlin--hard]] - `Coroutines`
- [[q-coroutine-profiling--kotlin--hard]] - `Coroutines`
- [[q-coroutine-context-detailed--kotlin--hard]] - Deep dive into CoroutineContext
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced patterns
- [[q-coroutine-performance-optimization--kotlin--hard]] - Performance optimization

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction
