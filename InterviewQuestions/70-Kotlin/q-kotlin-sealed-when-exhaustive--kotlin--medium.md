---
id: kotlin-149
title: "Kotlin Sealed When Exhaustive / sealed и exhaustive when в Kotlin"
aliases: [Kotlin Sealed When Exhaustive, sealed и exhaustive when в Kotlin]
topic: kotlin
subtopics: [sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-sealed-classes, q-flow-combining-zip-combine--kotlin--medium, q-sequences-detailed--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, kotlin, result, sealed-classes, state-machine, when-expression]
---

# Вопрос (RU)

> Как использовать sealed-классы и исчерпывающие when-выражения в Kotlin для реализации типобезопасных Result-типов и конечных автоматов состояния (state machines)?

# Question (EN)

> How do you use sealed classes and exhaustive when expressions in Kotlin to implement type-safe result types and state machines?

## Ответ (RU)

Sealed-классы ограничивают наследование фиксированным набором подклассов и в связке с when-выражениями позволяют компилятору проверять исчерпывающий разбор вариантов и строить типобезопасные конечные автоматы (state machines).

### Базовый sealed-класс (Result)

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Исчерпывающий when: для when-выражения компилятор требует обработать все варианты
fun <T> handleResult(result: Result<T>) = when (result) {
    is Result.Success -> println(result.data)
    is Result.Error -> println(result.exception.message)
    Result.Loading -> println("Loading...")
    // else не нужен — компилятор знает, что все случаи покрыты
}
```

### Состояние UI (UI State Machine)

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

### Результат сетевого запроса (NetworkResult)

```kotlin
sealed class NetworkResult<out T> {
    data class Success<out T>(
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

// Использование с исчерпывающим when-выражением
fun <T> handleNetworkResult(result: NetworkResult<T>) = when (result) {
    is NetworkResult.Success -> processData(result.data)
    is NetworkResult.Failure.HttpError -> handleHttpError(result.code)
    is NetworkResult.Failure.NetworkError -> handleNetworkError()
    is NetworkResult.Failure.UnknownError -> handleUnknownError(result.throwable)
    NetworkResult.Loading -> showLoading()
}
```

### Навигационное состояние (NavigationEvent)

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
        // Пример: адаптируйте под ваш API навигации и безопасную передачу аргументов
        navController.navigate(event.route)
    }
    is NavigationEvent.ShowDialog -> event.dialog.show()
    NavigationEvent.Finish -> activity.finish()
}
```

### Состояние асинхронной операции (AsyncState)

```kotlin
sealed class AsyncState<out T> {
    object Idle : AsyncState<Nothing>()
    object Loading : AsyncState<Nothing>()
    data class Success<out T>(val data: T) : AsyncState<T>()
    data class Error(val error: Throwable) : AsyncState<Nothing>()

    fun isLoading() = this is Loading
    fun isSuccess() = this is Success<*>
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

### Состояние валидации формы (ValidationResult)

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

// Исчерпывающая обработка с when-выражением
fun showValidationError(result: ValidationResult) = when (result) {
    ValidationResult.Valid -> ""
    is ValidationResult.Invalid.TooShort -> "Minimum ${result.minLength} characters"
    is ValidationResult.Invalid.TooLong -> "Maximum ${result.maxLength} characters"
    is ValidationResult.Invalid.InvalidFormat -> "Format: ${result.expectedFormat}"
    is ValidationResult.Invalid.Custom -> result.message
}
```

### Лучшие практики

1. Используйте sealed interface для "чистых" контрактов (Kotlin 1.5+).
2. Стройте вложенные sealed-иерархии для сложных состояний.
3. Используйте data class для вариантов с данными и object для единичных состояний.
4. Для when-выражений по sealed-иерархиям избегайте else и полагайтесь на проверку исчерпываемости компилятором.
5. Выносите общие операции в extension-функции.
6. Используйте обобщенные sealed-классы для переиспользуемых Result/State-паттернов.
7. Документируйте переходы состояний для state machine.
8. Комбинируйте sealed-состояния с корутинами и `Flow` для управления асинхронным состоянием.

## Answer (EN)

Sealed classes restrict inheritance to a fixed set of subclasses, enabling (in combination with when used as an expression) exhaustiveness checks and type-safe state machines.

### Basic Sealed Class

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Exhaustive when - for a when-expression the compiler enforces all cases
fun <T> handleResult(result: Result<T>) = when (result) {
    is Result.Success -> println(result.data)
    is Result.Error -> println(result.exception.message)
    Result.Loading -> println("Loading...")
    // No else needed - compiler knows all cases are covered
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
    data class Success<out T>(
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

// Usage with exhaustive when-expression
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
        // Example only: adapt to your navigation API for passing args safely
        navController.navigate(event.route)
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
    data class Success<out T>(val data: T) : AsyncState<T>()
    data class Error(val error: Throwable) : AsyncState<Nothing>()

    fun isLoading() = this is Loading
    fun isSuccess() = this is Success<*>
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

// Exhaustive handling with when-expression
fun showValidationError(result: ValidationResult) = when (result) {
    ValidationResult.Valid -> ""
    is ValidationResult.Invalid.TooShort -> "Minimum ${result.minLength} characters"
    is ValidationResult.Invalid.TooLong -> "Maximum ${result.maxLength} characters"
    is ValidationResult.Invalid.InvalidFormat -> "Format: ${result.expectedFormat}"
    is ValidationResult.Invalid.Custom -> result.message
}
```

### Best Practices

1. Use sealed interfaces for pure contracts (Kotlin 1.5+).
2. Use nested sealed hierarchies for complex states.
3. Use data classes for cases with data, objects for singletons.
4. For when-expressions over sealed hierarchies, avoid else: rely on exhaustiveness checks.
5. Provide extension functions for common operations.
6. Use generic sealed classes for reusable patterns.
7. Document state transitions for state machines.
8. Combine with coroutines and `Flow` for async state management.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## Related Questions

- [[q-sequences-detailed--kotlin--medium]]
- [[q-flow-combining-zip-combine--kotlin--medium]]
