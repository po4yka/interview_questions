---
id: 20251012-12271111155
title: "Kotlin Sealed When Exhaustive / sealed и exhaustive when в Kotlin"
aliases: [Kotlin Sealed When Exhaustive, sealed и exhaustive when в Kotlin]
topic: kotlin
subtopics: [sealed-classes, pattern-matching]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-java-kotlin-abstract-classes-difference--programming-languages--medium, q-sequences-detailed--kotlin--medium, q-flow-combining-zip-combine--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - sealed-classes
  - when-expression
  - state-machine
  - result
  - difficulty/medium
---
# Sealed Classes and Exhaustive When

**English**: Leverage sealed classes for exhaustive when expressions. Implement state machines and result types with sealed hierarchies.

**Russian**: Используйте sealed классы для exhaustive when выражений. Реализуйте state machines и result типы с sealed иерархиями.

## Answer (EN)

Sealed classes restrict inheritance to a fixed set of subclasses, enabling exhaustive when expressions and type-safe state machines.

### Basic Sealed Class

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Exhaustive when - compiler enforces all cases
fun <T> handleResult(result: Result<T>) = when (result) {
    is Result.Success -> println(result.data)
    is Result.Error -> println(result.exception.message)
    Result.Loading -> println("Loading...")
    // No else needed - compiler knows all cases covered
}
```

### UI State Machine

```kotlin
sealed interface UiState {
    object Initial : UiState
    object Loading : UiState
    data class Success(val users: List<User>) : UiState
    data class Error(val message: String, val canRetry: Boolean = true) : UiState
    object Empty : UiState
}

@Composable
fun UserListScreen(state: UiState) {
    when (state) {
        UiState.Initial -> InitialView()
        UiState.Loading -> LoadingIndicator()
        is UiState.Success -> UserList(state.users)
        is UiState.Error -> ErrorView(state.message, state.canRetry)
        UiState.Empty -> EmptyState()
    }
}
```

### Network Result Type

```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(
        val data: T,
        val code: Int = 200
    ) : NetworkResult<T>()

    sealed class Failure : NetworkResult<Nothing>() {
        data class HttpError(val code: Int, val message: String) : Failure()
        data class NetworkError(val exception: IOException) : Failure()
        data class UnknownError(val throwable: Throwable) : Failure()
    }

    object Loading : NetworkResult<Nothing>()
}

suspend fun <T> apiCall(call: suspend () -> T): NetworkResult<T> {
    return try {
        NetworkResult.Success(call())
    } catch (e: IOException) {
        NetworkResult.Failure.NetworkError(e)
    } catch (e: HttpException) {
        NetworkResult.Failure.HttpError(e.code(), e.message())
    } catch (e: Exception) {
        NetworkResult.Failure.UnknownError(e)
    }
}

// Usage with exhaustive when
fun <T> handleNetworkResult(result: NetworkResult<T>) = when (result) {
    is NetworkResult.Success -> processData(result.data)
    is NetworkResult.Failure.HttpError -> handleHttpError(result.code)
    is NetworkResult.Failure.NetworkError -> handleNetworkError()
    is NetworkResult.Failure.UnknownError -> handleUnknownError(result.throwable)
    NetworkResult.Loading -> showLoading()
}
```

### Navigation State

```kotlin
sealed class NavigationEvent {
    object Back : NavigationEvent()
    data class ToScreen(val route: String) : NavigationEvent()
    data class ToScreenWithArgs(val route: String, val args: Bundle) : NavigationEvent()
    data class ShowDialog(val dialog: Dialog) : NavigationEvent()
    object Finish : NavigationEvent()
}

fun handleNavigation(event: NavigationEvent) = when (event) {
    NavigationEvent.Back -> navController.popBackStack()
    is NavigationEvent.ToScreen -> navController.navigate(event.route)
    is NavigationEvent.ToScreenWithArgs -> {
        navController.navigate(event.route) {
            event.args.forEach { key, value ->
                arguments?.putString(key, value.toString())
            }
        }
    }
    is NavigationEvent.ShowDialog -> event.dialog.show()
    NavigationEvent.Finish -> activity.finish()
}
```

### Async Operation State

```kotlin
sealed class AsyncState<out T> {
    object Idle : AsyncState<Nothing>()
    object Loading : AsyncState<Nothing>()
    data class Success<T>(val data: T) : AsyncState<T>()
    data class Error(val error: Throwable) : AsyncState<Nothing>()

    fun isLoading() = this is Loading
    fun isSuccess() = this is Success
    fun isError() = this is Error

    fun getOrNull(): T? = (this as? Success)?.data

    fun getOrElse(default: T): T = when (this) {
        is Success -> data
        else -> default
    }

    suspend fun onSuccess(action: suspend (T) -> Unit): AsyncState<T> {
        if (this is Success) action(data)
        return this
    }

    suspend fun onError(action: suspend (Throwable) -> Unit): AsyncState<T> {
        if (this is Error) action(error)
        return this
    }
}
```

### Form Validation State

```kotlin
sealed class ValidationResult {
    object Valid : ValidationResult()

    sealed class Invalid : ValidationResult() {
        data class TooShort(val minLength: Int) : Invalid()
        data class TooLong(val maxLength: Int) : Invalid()
        data class InvalidFormat(val expectedFormat: String) : Invalid()
        data class Custom(val message: String) : Invalid()
    }
}

fun validateEmail(email: String): ValidationResult {
    return when {
        email.length < 5 -> ValidationResult.Invalid.TooShort(5)
        email.length > 100 -> ValidationResult.Invalid.TooLong(100)
        !email.contains('@') -> ValidationResult.Invalid.InvalidFormat("email@domain.com")
        else -> ValidationResult.Valid
    }
}

// Exhaustive handling
fun showValidationError(result: ValidationResult) = when (result) {
    ValidationResult.Valid -> ""
    is ValidationResult.Invalid.TooShort -> "Minimum ${result.minLength} characters"
    is ValidationResult.Invalid.TooLong -> "Maximum ${result.maxLength} characters"
    is ValidationResult.Invalid.InvalidFormat -> "Format: ${result.expectedFormat}"
    is ValidationResult.Invalid.Custom -> result.message
}
```

### Best Practices

1. **Use sealed interfaces** for pure contracts (Kotlin 1.5+)
2. **Nested sealed hierarchies** for complex states
3. **data classes for cases with data**, objects for singletons
4. **Exhaustive when** - avoid else clause
5. **Extension functions** for common operations
6. **Generic sealed classes** for reusable patterns
7. **Document state transitions** for state machines
8. **Combine with coroutines** for async state management

## Ответ (RU)

Sealed классы ограничивают наследование фиксированным набором подклассов, обеспечивая exhaustive when выражения.

### Основные паттерны

1. **Result типы**: Success, Error, Loading
2. **UI State machines**: различные состояния экрана
3. **Navigation events**: события навигации
4. **Validation results**: результаты валидации
5. **Async operations**: асинхронные операции

[Полные примеры приведены в английском разделе]

### Лучшие практики

1. **Используйте sealed interfaces** для чистых контрактов
2. **Вложенные sealed иерархии** для сложных состояний
3. **data classes для данных**, objects для singleton'ов
4. **Exhaustive when** - избегайте else
5. **Extension functions** для общих операций
6. **Generic sealed classes** для переиспользуемых паттернов

## Related Questions

- [[q-java-kotlin-abstract-classes-difference--programming-languages--medium]]
- [[q-sequences-detailed--kotlin--medium]]
- [[q-flow-combining-zip-combine--kotlin--medium]]
