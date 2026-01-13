---
anki_cards:
- slug: q-structured-concurrency-kotlin--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-structured-concurrency-kotlin--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Question (EN)
> What is structured concurrency and why is it important in Android coroutine usage?
## Ответ (RU)

**Структурированная конкурентность** — это подход к работе с конкурентностью, который привязывает время жизни корутин к области видимости (scope), формируя иерархию родитель–потомок и гарантируя, что когда область завершается (например, `Activity` уничтожается), все дочерние корутины завершаются или отменяются.

### Основные Принципы

**Определение**: Структурированная конкурентность — это принцип, который:
- Привязывает время жизни корутин к конкретной области
- Гарантирует, что все дочерние корутины завершаются или отменяются при завершении родительской области
- Предотвращает утечки корутин, когда фоновая работа продолжается после уничтожения UI
- Обеспечивает предсказуемую отмену, очистку и распространение ошибок по иерархии

### Почему Это Важно в Android

**Проблема Без Структурированной Конкурентности**:
```kotlin
// - ПЛОХО: Неструктурированный подход
class MyActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Глобальная область — живёт дольше Activity и не учитывает её жизненный цикл
        GlobalScope.launch {
            while (true) {
                delay(1000)
                // Эта корутина продолжит работу даже после уничтожения Activity,
                // если явно не отменить её.
                updateUI() // Риск: вызовы к UI после уничтожения или из неправильного потока
            }
        }
    }
}
```

**Решение Со Структурированной Конкурентностью**:
```kotlin
// - ХОРОШО: Структурированный подход
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Область, учитывающая жизненный цикл — отменяется автоматически
        lifecycleScope.launch {
            while (true) {
                delay(1000)
                updateUI() // Безопаснее: корутина отменяется при уничтожении Activity
            }
        }
    }
}
```

### Структурированная Конкурентность на Практике

**1. Иерархия Областей**:
```kotlin
class MyViewModel : ViewModel() {
    fun loadData() {
        // Родительская корутина в viewModelScope (на основе SupervisorJob)
        viewModelScope.launch {
            val user = async { fetchUser() }        // Дочерняя 1
            val posts = async { fetchPosts() }      // Дочерняя 2

            // Если viewModelScope отменяется (например, при onCleared()):
            // - Отменяется родительский scope
            // - Все дочерние корутины (async блоки) автоматически отменяются
            // - Не остается "сиротских" задач

            displayData(user.await(), posts.await())
        }
    }
}
```

**2. Автоматическая Отмена**:
```kotlin
lifecycleScope.launch {
    // Все эти корутины — дочерние относительно lifecycleScope
    launch {
        // Задача 1
    }
    launch {
        // Задача 2
    }

    // При уничтожении жизненного цикла:
    // - lifecycleScope отменяется
    // - Все дочерние корутины автоматически отменяются
    // - Это помогает предотвратить утечки памяти и лишнюю работу
}
```

**3. Распространение Ошибок (обычная иерархия Job)**:
```kotlin
viewModelScope.launch {
    try {
        val result1 = async { riskyOperation1() }
        val result2 = async { riskyOperation2() }

        // Внутри одной родительской корутины:
        // - Если один async выбрасывает исключение при await(), оно будет поймано в этом try/catch
        // - Можно отменить другие операции вручную при необходимости
        // - В обычной иерархии Job ошибка дочернего элемента приводит к отмене родителя и его детей

        processResults(result1.await(), result2.await())
    } catch (e: Exception) {
        handleError(e)
    }
}
```

### Преимущества Структурированной Конкурентности

**1. Предотвращение Утечек Памяти**:
- Корутины автоматически отменяются при завершении области
- Фоновая работа не продолжается после уничтожения UI
- Ресурсы корректно освобождаются

**2. Предсказуемая Отмена**:
- Отмена родителя → все его дочерние Job отменяются
- Четкая иерархия отмены
- Нет корутин-сирот

**3. Обработка Исключений**:
- Исключения предсказуемо распространяются по иерархии Job
- Можно установить CoroutineExceptionHandler на уровне области для необработанных исключений в корне
- Ошибки не остаются незамеченными при правильной структуре

**4. Управление Ресурсами**:
- Очистка происходит автоматически при завершении scope
- Не нужно вручную отслеживать Job корутин в большинстве случаев
- Логика следует жизненному циклу компонента

### Резюме

**Структурированная конкурентность** гарантирует:
- Корутины привязаны к областям
- Автоматическую отмену при завершении области
- Предсказуемое распространение ошибок
- Отсутствие утечек памяти
- Чистое управление ресурсами

В Android это означает использование `viewModelScope`, `lifecycleScope` или пользовательских областей, привязанных к жизненному циклу, вместо `GlobalScope` или корутин без явной области.

---

## Answer (EN)

**Structured concurrency** is a concurrency model that ties the lifetime of coroutines to a scope, forming a parent–child hierarchy and ensuring that when a scope ends (e.g., an `Activity` is destroyed), all its child coroutines are completed or cancelled.

### Core Principles

**Definition**: Structured concurrency is a principle that:
- Ties coroutine lifetimes to a specific scope
- Ensures all child coroutines complete or cancel when the parent scope ends
- Prevents coroutine leaks where background work continues after the UI is destroyed
- `Provides` predictable cancellation, cleanup, and error propagation through the hierarchy

### Why It Matters in Android

**Problem Without Structured Concurrency**:
```kotlin
// - BAD: Unstructured approach
class MyActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Global scope — lives longer than Activity and ignores its lifecycle
        GlobalScope.launch {
            while (true) {
                delay(1000)
                // This keeps running even after Activity is destroyed
                // unless you cancel it manually.
                updateUI() // Risky: UI calls after destruction or from wrong thread
            }
        }
    }
}
```

**Solution With Structured Concurrency**:
```kotlin
// - GOOD: Structured approach
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Lifecycle-aware scope — canceled automatically
        lifecycleScope.launch {
            while (true) {
                delay(1000)
                updateUI() // Safer: coroutine is canceled when Activity is destroyed
            }
        }
    }
}
```

### Structured Concurrency in Practice

**1. Scope Hierarchy**:
```kotlin
class MyViewModel : ViewModel() {
    fun loadData() {
        // Parent coroutine in viewModelScope (backed by SupervisorJob)
        viewModelScope.launch {
            val user = async { fetchUser() }        // Child 1
            val posts = async { fetchPosts() }      // Child 2

            // If viewModelScope is canceled (e.g. ViewModel.onCleared()):
            // - The scope is canceled
            // - All its child coroutines (including async blocks) are automatically canceled
            // - No orphan work remains

            displayData(user.await(), posts.await())
        }
    }
}
```

**2. Automatic Cancellation**:
```kotlin
lifecycleScope.launch {
    // All of these are children of lifecycleScope
    launch {
        // Task 1
    }
    launch {
        // Task 2
    }

    // When lifecycle is destroyed:
    // - lifecycleScope is canceled
    // - All child coroutines are automatically canceled
    // - Helps prevent memory leaks and wasted work
}
```

**3. Failure Propagation (regular Job hierarchy)**:
```kotlin
viewModelScope.launch {
    try {
        val result1 = async { riskyOperation1() }
        val result2 = async { riskyOperation2() }

        // Within a single parent coroutine:
        // - If an async throws when awaited, the exception is caught here
        // - You can cancel other operations explicitly if needed
        // - In a regular Job hierarchy, a failing child cancels its parent and siblings

        processResults(result1.await(), result2.await())
    } catch (e: Exception) {
        handleError(e)
    }
}
```

### Benefits of Structured Concurrency

**1. Memory Leak Prevention**:
- Coroutines are automatically canceled when the scope ends
- Background work doesn’t continue after UI destruction
- Resources are properly cleaned up

**2. Predictable Cancellation**:
- Cancel parent → all its child Jobs are canceled
- Clear cancellation hierarchy
- No orphan coroutines

**3. Exception Handling**:
- Exceptions propagate predictably through the Job hierarchy
- Can install a CoroutineExceptionHandler at a scope root for uncaught exceptions
- Failures are less likely to go unnoticed when scopes are structured correctly

**4. Resource Management**:
- Cleanup happens automatically when scopes complete or are canceled
- No need to manually track most coroutine Jobs
- Behavior follows the component lifecycle

### Android-Specific Scopes

**viewModelScope**:
```kotlin
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            // Automatically canceled when ViewModel.onCleared() is called
            val user = repository.getUser()
            _userData.value = user
        }
    }
}
```

**lifecycleScope**:
```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Canceled when lifecycle is destroyed
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

### Comparison: Unstructured vs Structured

| Aspect | Unstructured (GlobalScope) | Structured (lifecycleScope) |
|--------|---------------------------|-----------------------------|
| **Lifetime** | Often global / until manual cancel | Tied to component lifecycle |
| **Cancellation** | Manual | Automatic via lifecycle |
| **Memory Leaks** | Higher risk of leaks | Safer by design |
| **Error Handling** | Must manage manually | Propagates through hierarchy |
| **Resource Cleanup** | Manual cleanup needed | Automatic cleanup in scope |

### Best Practices

```kotlin
// - DO: Use lifecycle- or component-scoped builders
viewModelScope.launch { /* ... */ }
lifecycleScope.launch { /* ... */ }

// - DO: Create custom scopes tied to lifecycle/ownership
class MyRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun close() {
        scope.cancel() // Clean up when repository is no longer used
    }
}

// - DON'T: Use GlobalScope for app/business logic
GlobalScope.launch { /* ... */ } // Ignores lifecycle; easy to leak or mis-handle

// - DON'T: Launch coroutines in ad-hoc scopes without canceling
CoroutineScope(Dispatchers.Main).launch { /* ... */ }
// If you create a scope manually, you must also manage its Job and cancellation.
```

### Summary

**Structured concurrency** ensures:
- Coroutines tied to scopes
- Automatic cancellation when the scope ends
- Predictable error propagation
- Reduced risk of memory leaks
- Clean resource management

In Android, this means using `viewModelScope`, `lifecycleScope`, or well-defined custom scopes rather than `GlobalScope` or unscoped launches.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Structured Concurrency - Kotlin Docs](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
- [Coroutines on Android - Android Developers](https://developer.android.com/kotlin/coroutines)
- [ViewModel Scopes - AndroidX](https://developer.android.com/topic/libraries/architecture/coroutines)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF

---

## Related Questions

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

### Related (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - `Coroutine` dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs `Context`
- [[q-coroutine-context-explained--kotlin--medium]] - CoroutineContext explained

### Advanced (Harder)
- [[q-coroutine-context-detailed--kotlin--hard]] - Deep dive into CoroutineContext
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced patterns
- [[q-coroutine-performance-optimization--kotlin--hard]] - Performance optimization
