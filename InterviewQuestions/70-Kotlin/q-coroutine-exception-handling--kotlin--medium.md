---
id: 20251012-135616
title: "Coroutine Exception Handling / Обработка исключений в корутинах"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, exceptions, error-handling, supervisorscope]
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
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, coroutines, exceptions, error-handling, supervisorscope, difficulty/medium]
---
# Question (EN)
> How does exception handling work in Kotlin Coroutines? What is the difference between coroutineScope and supervisorScope?
# Вопрос (RU)
> Как работает обработка исключений в Kotlin корутинах? В чем разница между coroutineScope и supervisorScope?

---

## Answer (EN)

Exception handling in coroutines follows specific rules based on the coroutine builder and scope used.

### Exception Propagation Rules

**1. launch - Propagates immediately to parent**

```kotlin
viewModelScope.launch {
    launch {
        throw Exception("Child failed")  // Crashes parent immediately
    }

    delay(1000)
    println("This never executes")  // Never reached
}
```

**2. async - Stores exception until await()**

```kotlin
viewModelScope.launch {
    val deferred = async {
        throw Exception("Async failed")  // Exception stored
    }

    delay(1000)
    println("This executes")  // Still executes

    deferred.await()  // Exception thrown here
}
```

### try-catch in Coroutines

**Works for direct code:**

```kotlin
viewModelScope.launch {
    try {
        val result = suspendingFunction()  // - Caught
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**Does NOT work for child coroutines:**

```kotlin
viewModelScope.launch {
    try {
        launch {
            throw Exception("Failed")  // - NOT caught
        }
    } catch (e: Exception) {
        // Never reached!
    }
}
```

### coroutineScope vs supervisorScope

**coroutineScope - Cancels all siblings on failure**

```kotlin
viewModelScope.launch {
    try {
        coroutineScope {
            launch {
                delay(1000)
                println("Task 1 complete")  // Never prints
            }

            launch {
                throw Exception("Task 2 failed")  // Cancels Task 1
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Caught: Task 2 failed
    }
}
```

**supervisorScope - Siblings continue on failure**

```kotlin
viewModelScope.launch {
    supervisorScope {
        launch {
            delay(1000)
            println("Task 1 complete")  // Still prints!
        }

        launch {
            throw Exception("Task 2 failed")  // Doesn't affect Task 1
        }
    }
}
```

### CoroutineExceptionHandler

**Global exception handler for launch:**

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: ${exception.message}")
}

viewModelScope.launch(handler) {
    throw Exception("Failed")  // Caught by handler
}

// Note: Only works for launch, not async
viewModelScope.async(handler) {
    throw Exception("Failed")  // Handler NOT called
}
```

### Real-World Examples

**Example 1: Parallel requests with supervisorScope**

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

                // If one fails, other continues
            }
        }
    }
}
```

**Example 2: Sequential operations with coroutineScope**

```kotlin
suspend fun processOrder(order: Order) = coroutineScope {
    // All steps must succeed
    val validated = validateOrder(order)
    val processed = processPayment(validated)
    val confirmed = confirmOrder(processed)

    // If any step fails, all are cancelled
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

            // Optional data - can fail silently
            launch {
                _notifications.value = notificationRepo.getNotifications()
            }
        }
    }
}
```

### Best Practices

**1. Use supervisorScope for independent parallel tasks**

```kotlin
// - GOOD - Independent tasks
supervisorScope {
    launch { loadProducts() }
    launch { loadCategories() }
    launch { loadBanners() }
}
```

**2. Use coroutineScope for dependent sequential tasks**

```kotlin
// - GOOD - Sequential steps
coroutineScope {
    val user = getUser()
    val profile = getProfile(user.id)
    val settings = getSettings(user.id)
}
```

**3. Handle exceptions at appropriate level**

```kotlin
// - GOOD - Handle at UI level
viewModelScope.launch {
    try {
        val data = repository.getData()
        _uiState.value = UiState.Success(data)
    } catch (e: Exception) {
        _uiState.value = UiState.Error(e.message)
    }
}
```

**English Summary**: Exceptions in coroutines: `launch` propagates immediately, `async` stores until `await()`. `try-catch` works for direct code, not child coroutines. `coroutineScope` cancels all siblings on failure. `supervisorScope` lets siblings continue. `CoroutineExceptionHandler` for global handling (launch only). Use `supervisorScope` for independent parallel tasks, `coroutineScope` for dependent sequential tasks.

## Ответ (RU)

Обработка исключений в корутинах следует специфичным правилам в зависимости от используемого билдера и скоупа.

### Правила распространения исключений

**1. launch - Распространяет немедленно к родителю**

```kotlin
viewModelScope.launch {
    launch {
        throw Exception("Child failed")  // Крашит родителя немедленно
    }

    delay(1000)
    println("Это никогда не выполнится")  // Никогда не достигается
}
```

**2. async - Хранит исключение до await()**

```kotlin
viewModelScope.launch {
    val deferred = async {
        throw Exception("Async failed")  // Исключение сохранено
    }

    delay(1000)
    println("Это выполнится")  // Все еще выполняется

    deferred.await()  // Исключение выброшено здесь
}
```

### try-catch в корутинах

**Работает для прямого кода:**

```kotlin
viewModelScope.launch {
    try {
        val result = suspendingFunction()  // - Поймано
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**НЕ работает для дочерних корутин:**

```kotlin
viewModelScope.launch {
    try {
        launch {
            throw Exception("Failed")  // - НЕ поймано
        }
    } catch (e: Exception) {
        // Никогда не достигается!
    }
}
```

### coroutineScope vs supervisorScope

**coroutineScope - Отменяет всех братьев при сбое**

```kotlin
viewModelScope.launch {
    try {
        coroutineScope {
            launch {
                delay(1000)
                println("Task 1 complete")  // Никогда не печатает
            }

            launch {
                throw Exception("Task 2 failed")  // Отменяет Task 1
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Caught: Task 2 failed
    }
}
```

**supervisorScope - Братья продолжают при сбое**

```kotlin
viewModelScope.launch {
    supervisorScope {
        launch {
            delay(1000)
            println("Task 1 complete")  // Все еще печатает!
        }

        launch {
            throw Exception("Task 2 failed")  // Не влияет на Task 1
        }
    }
}
```

### Примеры из реальной практики

**Пример 1: Параллельные запросы с supervisorScope**

```kotlin
class ProductViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            supervisorScope {
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
            }
        }
    }
}
```

**Пример 2: Последовательные операции с coroutineScope**

```kotlin
suspend fun processOrder(order: Order) = coroutineScope {
    // Все шаги должны успешно выполниться
    val validated = validateOrder(order)
    val processed = processPayment(validated)
    val confirmed = confirmOrder(processed)

    // Если любой шаг падает, все отменяются
    confirmed
}
```

### Лучшие практики

**1. Используйте supervisorScope для независимых параллельных задач**

```kotlin
// - ХОРОШО - Независимые задачи
supervisorScope {
    launch { loadProducts() }
    launch { loadCategories() }
    launch { loadBanners() }
}
```

**2. Используйте coroutineScope для зависимых последовательных задач**

```kotlin
// - ХОРОШО - Последовательные шаги
coroutineScope {
    val user = getUser()
    val profile = getProfile(user.id)
    val settings = getSettings(user.id)
}
```

**Краткое содержание**: Исключения в корутинах: `launch` распространяет немедленно, `async` хранит до `await()`. `try-catch` работает для прямого кода, не для дочерних корутин. `coroutineScope` отменяет всех братьев при сбое. `supervisorScope` позволяет братьям продолжить. `CoroutineExceptionHandler` для глобальной обработки (только launch). Используйте `supervisorScope` для независимых параллельных задач, `coroutineScope` для зависимых последовательных задач.

---

## References
- [Coroutine Exceptions - Kotlin Documentation](https://kotlinlang.org/docs/exception-handling.html)
- [CoroutineExceptionHandler](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-exception-handler/)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
### Related (Medium)
- [[q-flow-exception-handling--kotlin--medium]] - Flow
- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]] - Coroutines
- [[q-coroutine-timeout-withtimeout--kotlin--medium]] - Coroutines
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]] - Coroutines
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - Coroutine dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs Context
- [[q-coroutine-context-explained--kotlin--medium]] - CoroutineContext explained
### Advanced (Harder)
- [[q-structured-concurrency--kotlin--hard]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-context-detailed--kotlin--hard]] - Deep dive into CoroutineContext
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced patterns
- [[q-coroutine-performance-optimization--kotlin--hard]] - Performance optimization
### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

