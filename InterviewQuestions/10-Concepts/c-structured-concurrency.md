---
id: ivc-20251030-140000
title: Structured Concurrency / Структурированная конкурентность
aliases: [Coroutine Scoping, Structured Concurrency, Структурированная конкурентность]
kind: concept
summary: Kotlin Coroutines paradigm ensuring proper scope and cleanup
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [concept, concurrency, coroutines, kotlin, structured-concurrency]
---

# Summary (EN)

Structured concurrency is a programming paradigm in Kotlin Coroutines that ensures coroutines are properly scoped, hierarchically organized, and automatically cleaned up. It establishes a parent-child relationship between coroutines where the parent waits for all children to complete and cancellation propagates through the hierarchy.

Key principles:
- **Scope defines lifetime**: Coroutines must be launched within a CoroutineScope that controls their lifecycle
- **Hierarchical structure**: Child coroutines inherit context from parent and form a tree structure
- **Cancellation propagation**: When parent is cancelled, all children are cancelled automatically
- **No leaked coroutines**: Scope ensures all coroutines complete or are cancelled when scope ends

# Сводка (RU)

Структурированная конкурентность — это парадигма программирования в Kotlin Coroutines, которая обеспечивает правильную область видимости корутин, их иерархическую организацию и автоматическую очистку. Она устанавливает отношения родитель-потомок между корутинами, где родитель ждет завершения всех потомков, а отмена распространяется по иерархии.

Ключевые принципы:
- **Область определяет время жизни**: Корутины должны запускаться в CoroutineScope, который контролирует их жизненный цикл
- **Иерархическая структура**: Дочерние корутины наследуют контекст от родителя и формируют древовидную структуру
- **Распространение отмены**: При отмене родителя все дочерние корутины отменяются автоматически
- **Нет утечек корутин**: Область гарантирует, что все корутины завершатся или будут отменены при завершении области

## Core Concept / Основная Концепция

**EN**: In structured concurrency, every coroutine must belong to a scope. When you launch a coroutine using `launch` or `async`, it becomes a child of the scope. The scope tracks all its children and:
- Waits for all children to complete before completing itself
- Cancels all children when the scope is cancelled
- Propagates exceptions from children to parent

**RU**: В структурированной конкурентности каждая корутина должна принадлежать области видимости. Когда вы запускаете корутину через `launch` или `async`, она становится дочерней для области. Область отслеживает всех своих потомков и:
- Ожидает завершения всех потомков перед собственным завершением
- Отменяет всех потомков при отмене области
- Распространяет исключения от потомков к родителю

## Benefits / Преимущества

**EN**:
- **Resource safety**: Guaranteed cleanup when scope ends (no resource leaks)
- **Predictable behavior**: Clear lifecycle boundaries and cancellation semantics
- **Error handling**: Exceptions propagate up the hierarchy for centralized handling
- **Testing**: Easy to test by controlling scope lifecycle

**RU**:
- **Безопасность ресурсов**: Гарантированная очистка при завершении области (нет утечек ресурсов)
- **Предсказуемое поведение**: Четкие границы жизненного цикла и семантика отмены
- **Обработка ошибок**: Исключения распространяются вверх по иерархии для централизованной обработки
- **Тестирование**: Легко тестировать, контролируя жизненный цикл области

## Best Practices / Лучшие Практики

**EN**:
- Use `viewModelScope` in Android ViewModels for automatic cleanup on ViewModel clear
- Use `lifecycleScope` in Activities/Fragments tied to lifecycle
- Create custom scopes with `CoroutineScope(SupervisorJob() + Dispatchers.Main)` for independent components
- Use `supervisorScope` when you want child failures to not cancel siblings
- Always cancel scopes explicitly when they're no longer needed

**RU**:
- Используйте `viewModelScope` в Android ViewModels для автоматической очистки при уничтожении ViewModel
- Используйте `lifecycleScope` в Activity/Fragment, привязанные к жизненному циклу
- Создавайте пользовательские области с `CoroutineScope(SupervisorJob() + Dispatchers.Main)` для независимых компонентов
- Используйте `supervisorScope`, когда отказ дочерних корутин не должен отменять соседние
- Всегда явно отменяйте области, когда они больше не нужны

## Code Example / Пример Кода

```kotlin
class UserRepository {
    // Custom scope for repository
    // Пользовательская область для репозитория
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun loadUser(userId: String) {
        scope.launch {
            try {
                // Parent coroutine / Родительская корутина
                val user = async { fetchUserFromApi(userId) }
                val posts = async { fetchUserPosts(userId) }

                // Both children must complete / Оба потомка должны завершиться
                updateUI(user.await(), posts.await())
            } catch (e: CancellationException) {
                // Scope was cancelled / Область была отменена
                throw e
            } catch (e: Exception) {
                // Handle error / Обработка ошибки
                handleError(e)
            }
        }
    }

    fun cleanup() {
        // Cancel all coroutines in scope
        // Отменить все корутины в области
        scope.cancel()
    }
}

// Android ViewModel example / Пример Android ViewModel
class UserViewModel : ViewModel() {
    fun loadData() {
        // viewModelScope automatically cancelled when ViewModel is cleared
        // viewModelScope автоматически отменяется при уничтожении ViewModel
        viewModelScope.launch {
            val result = withContext(Dispatchers.IO) {
                repository.fetchData()
            }
            updateState(result)
        }
    }
}
```

## Use Cases / Trade-offs

**Use structured concurrency when**:
- Building Android apps with lifecycle-aware components
- Managing concurrent operations that should be cancelled together
- Ensuring resource cleanup (network connections, file handles)
- Implementing request-scoped operations in backend services

**Trade-offs**:
- **Pro**: Prevents resource leaks, simplifies cancellation, clear lifecycle
- **Pro**: Easier to reason about concurrent code flow
- **Con**: Requires understanding of scope and context propagation
- **Con**: May need custom scopes for complex scenarios (e.g., independent operations)

## References

- [Kotlin Coroutines Guide: Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Kotlin Coroutines Guide: Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Roman Elizarov: Structured Concurrency](https://medium.com/@elizarov/structured-concurrency-722d765aa952)
- [Android Developers: Coroutines on Android](https://developer.android.com/kotlin/coroutines)
