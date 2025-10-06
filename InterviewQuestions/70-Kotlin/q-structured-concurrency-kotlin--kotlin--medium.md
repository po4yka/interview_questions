---
id: 20251006-structured-concurrency
title: Structured Concurrency in Kotlin Coroutines
topic: kotlin
subtopics:
  - coroutines
  - structured-concurrency
  - scope-management
difficulty: medium
language_tags:
  - en
  - ru
original_language: en
status: draft
source: Kotlin Coroutines Interview Questions PDF
tags:
  - kotlin
  - coroutines
  - structured-concurrency
  - scope
  - lifecycle
  - memory-leaks
  - difficulty/medium
---

# Question (EN)
> What is structured concurrency and why is it important in Android coroutine usage?

# Вопрос (RU)
> Что такое структурированная конкурентность и почему она важна при использовании корутин в Android?

---

## Answer (EN)

**Structured concurrency** is a programming paradigm that ties the lifetime of coroutines to a scope, ensuring that when a scope ends (e.g., an Activity is destroyed), all its child coroutines are completed or cancelled.

### Core Principles

**Definition**: Structured concurrency is a principle that:
- Ties coroutine lifetimes to a specific scope
- Ensures all child coroutines complete or cancel when parent scope ends
- Prevents coroutine leaks where background work continues after UI is destroyed
- Provides predictable cancellation and cleanup

### Why It Matters in Android

**Problem Without Structured Concurrency**:
```kotlin
// ❌ BAD: Unstructured approach
class MyActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Global scope - runs forever unless manually canceled
        GlobalScope.launch {
            while (true) {
                delay(1000)
                // This keeps running even after Activity is destroyed!
                updateUI() // Can cause crashes or memory leaks
            }
        }
    }
}
```

**Solution With Structured Concurrency**:
```kotlin
// ✅ GOOD: Structured approach
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Lifecycle-aware scope - cancels automatically
        lifecycleScope.launch {
            while (true) {
                delay(1000)
                updateUI() // Safe: canceled when Activity destroyed
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
        // Parent coroutine in viewModelScope
        viewModelScope.launch {
            val user = async { fetchUser() }        // Child 1
            val posts = async { fetchPosts() }      // Child 2

            // If viewModelScope is canceled:
            // - Parent coroutine is canceled
            // - All child coroutines (async blocks) are automatically canceled
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
    // - Prevents memory leaks
}
```

**3. Failure Propagation**:
```kotlin
viewModelScope.launch {
    try {
        val result1 = async { riskyOperation1() }
        val result2 = async { riskyOperation2() }

        // If either async fails:
        // - Exception propagates to parent
        // - Other sibling is automatically canceled
        // - Parent scope can handle the error

        processResults(result1.await(), result2.await())
    } catch (e: Exception) {
        handleError(e)
    }
}
```

### Benefits of Structured Concurrency

**1. Memory Leak Prevention**:
- Coroutines are automatically canceled when scope ends
- No background work continues after UI destruction
- Resources are properly cleaned up

**2. Predictable Cancellation**:
- Cancel parent → all children canceled
- Clear cancellation hierarchy
- No orphan coroutines

**3. Exception Handling**:
- Exceptions propagate predictably through scope hierarchy
- Can install CoroutineExceptionHandler at scope level
- Failures don't go unnoticed

**4. Resource Management**:
- Cleanup happens automatically
- No manual tracking of coroutine jobs
- Follows component lifecycle

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
|--------|---------------------------|----------------------------|
| **Lifetime** | Forever (until manual cancel) | Tied to component lifecycle |
| **Cancellation** | Manual | Automatic |
| **Memory Leaks** | Risk of leaks | Leak-safe |
| **Error Handling** | Must handle manually | Propagates through hierarchy |
| **Resource Cleanup** | Manual cleanup needed | Automatic cleanup |

### Best Practices

```kotlin
// ✅ DO: Use scoped builders
viewModelScope.launch { /* ... */ }
lifecycleScope.launch { /* ... */ }

// ✅ DO: Create custom scopes tied to lifecycle
class MyRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun close() {
        scope.cancel() // Clean up when repository is done
    }
}

// ❌ DON'T: Use GlobalScope
GlobalScope.launch { /* ... */ } // Ignores lifecycle!

// ❌ DON'T: Launch unscoped coroutines
CoroutineScope(Dispatchers.Main).launch { /* ... */ }
// No lifecycle tie - must cancel manually
```

### Summary

**Structured concurrency** ensures:
- ✅ Coroutines tied to scopes
- ✅ Automatic cancellation when scope ends
- ✅ Predictable error propagation
- ✅ No memory leaks
- ✅ Clean resource management

In Android, this means using `viewModelScope`, `lifecycleScope`, or custom scopes rather than `GlobalScope` or unscoped launches.

---

## Ответ (RU)

**Структурированная конкурентность** - это парадигма программирования, которая привязывает время жизни корутин к области видимости (scope), гарантируя, что когда область завершается (например, Activity уничтожается), все дочерние корутины завершаются или отменяются.

### Основные Принципы

**Определение**: Структурированная конкурентность - это принцип, который:
- Привязывает время жизни корутин к конкретной области
- Гарантирует, что все дочерние корутины завершаются или отменяются при завершении родительской области
- Предотвращает утечки корутин, когда фоновая работа продолжается после уничтожения UI
- Обеспечивает предсказуемую отмену и очистку

### Почему Это Важно в Android

**Проблема Без Структурированной Конкурентности**:
```kotlin
// ❌ ПЛОХО: Неструктурированный подход
class MyActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Глобальная область - работает вечно без ручной отмены
        GlobalScope.launch {
            while (true) {
                delay(1000)
                // Продолжает работать даже после уничтожения Activity!
                updateUI() // Может вызвать крэши или утечки памяти
            }
        }
    }
}
```

**Решение Со Структурированной Конкурентностью**:
```kotlin
// ✅ ХОРОШО: Структурированный подход
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Область, учитывающая жизненный цикл - отменяется автоматически
        lifecycleScope.launch {
            while (true) {
                delay(1000)
                updateUI() // Безопасно: отменяется при уничтожении Activity
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
        // Родительская корутина в viewModelScope
        viewModelScope.launch {
            val user = async { fetchUser() }        // Дочерняя 1
            val posts = async { fetchPosts() }      // Дочерняя 2

            // Если viewModelScope отменяется:
            // - Родительская корутина отменяется
            // - Все дочерние корутины (async блоки) автоматически отменяются
            // - Не остается сирот

            displayData(user.await(), posts.await())
        }
    }
}
```

**2. Автоматическая Отмена**:
```kotlin
lifecycleScope.launch {
    // Все это - дочерние элементы lifecycleScope
    launch {
        // Задача 1
    }
    launch {
        // Задача 2
    }

    // При уничтожении жизненного цикла:
    // - lifecycleScope отменяется
    // - Все дочерние корутины автоматически отменяются
    // - Предотвращает утечки памяти
}
```

**3. Распространение Ошибок**:
```kotlin
viewModelScope.launch {
    try {
        val result1 = async { riskyOperation1() }
        val result2 = async { riskyOperation2() }

        // Если любой async падает:
        // - Исключение распространяется на родителя
        // - Другой соседний элемент автоматически отменяется
        // - Родительская область может обработать ошибку

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
- Отмена родителя → все дети отменены
- Четкая иерархия отмены
- Нет корутин-сирот

**3. Обработка Исключений**:
- Исключения предсказуемо распространяются через иерархию
- Можно установить CoroutineExceptionHandler на уровне области
- Ошибки не остаются незамеченными

**4. Управление Ресурсами**:
- Очистка происходит автоматически
- Не нужно вручную отслеживать Job корутин
- Следует жизненному циклу компонента

### Резюме

**Структурированная конкурентность** гарантирует:
- ✅ Корутины привязаны к областям
- ✅ Автоматическая отмена при завершении области
- ✅ Предсказуемое распространение ошибок
- ✅ Отсутствие утечек памяти
- ✅ Чистое управление ресурсами

В Android это означает использование `viewModelScope`, `lifecycleScope` или пользовательских областей вместо `GlobalScope` или неограниченных запусков.

---

## References

- [Structured Concurrency - Kotlin Docs](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
- [Coroutines on Android - Android Developers](https://developer.android.com/kotlin/coroutines)
- [ViewModel Scopes - AndroidX](https://developer.android.com/topic/libraries/architecture/coroutines)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF
