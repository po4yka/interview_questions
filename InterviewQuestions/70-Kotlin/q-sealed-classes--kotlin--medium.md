---
tags:
  - kotlin
  - sealed-classes
  - type-safety
difficulty: medium
status: draft
---

# В чем особенность sealed классов

**English**: What is special about sealed classes in Kotlin?

## Answer (EN)
Особенность запечатанных (sealed) классов заключается в ограничении иерархии наследования: все их подклассы должны быть объявлены в том же файле, что и сам запечатанный класс.

### Основная идея

Sealed классы идеальны для создания ограниченных иерархий классов, где требуется строго контролировать набор возможных подтипов, особенно при моделировании состояний или результатов операций.

```kotlin
// Sealed class для моделирования состояний UI
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<User>) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Преимущества при использовании с when

Компилятор знает все возможные подтипы, поэтому не требуется `else` ветка.

```kotlin
fun handleState(state: UiState) {
    when (state) {
        is UiState.Loading -> showLoading()
        is UiState.Success -> showData(state.data)
        is UiState.Error -> showError(state.message)
        // else не нужен - компилятор знает все варианты!
    }
}
```

Если добавить новый подтип:

```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<User>) : UiState()
    data class Error(val message: String) : UiState()
    object Empty : UiState()  // Новый подтип
}

// Компилятор покажет ошибку во всех when без обработки Empty!
```

### Примеры использования

#### 1. Моделирование результата операции

```kotlin
sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Использование
suspend fun loadUser(id: Int): Result<User> {
    return try {
        val user = apiService.getUser(id)
        Result.Success(user)
    } catch (e: Exception) {
        Result.Error(e)
    }
}

// В ViewModel
viewModelScope.launch {
    _uiState.value = Result.Loading
    val result = loadUser(123)
    _uiState.value = result
}

// В UI
result.observe(this) { result ->
    when (result) {
        is Result.Loading -> showProgressBar()
        is Result.Success -> updateUI(result.value)
        is Result.Error -> showError(result.exception.message)
    }
}
```

#### 2. Моделирование сетевых запросов

```kotlin
sealed class NetworkResponse<out T> {
    data class Success<T>(val data: T) : NetworkResponse<T>()
    data class HttpError(val code: Int, val message: String) : NetworkResponse<Nothing>()
    data class NetworkError(val exception: IOException) : NetworkResponse<Nothing>()
    object Timeout : NetworkResponse<Nothing>()
}

suspend fun fetchData(): NetworkResponse<List<Item>> {
    return try {
        val response = apiCall()
        when {
            response.isSuccessful -> NetworkResponse.Success(response.body()!!)
            response.code() == 404 -> NetworkResponse.HttpError(404, "Not Found")
            else -> NetworkResponse.HttpError(response.code(), response.message())
        }
    } catch (e: SocketTimeoutException) {
        NetworkResponse.Timeout
    } catch (e: IOException) {
        NetworkResponse.NetworkError(e)
    }
}
```

#### 3. Навигационные события

```kotlin
sealed class NavigationEvent {
    object Back : NavigationEvent()
    data class ToDetail(val itemId: Int) : NavigationEvent()
    data class ToProfile(val userId: Int) : NavigationEvent()
    object ToSettings : NavigationEvent()
}

class NavigationViewModel : ViewModel() {
    private val _navigationEvent = MutableLiveData<NavigationEvent>()
    val navigationEvent: LiveData<NavigationEvent> = _navigationEvent

    fun onItemClicked(itemId: Int) {
        _navigationEvent.value = NavigationEvent.ToDetail(itemId)
    }

    fun onBackPressed() {
        _navigationEvent.value = NavigationEvent.Back
    }
}

// В Fragment
viewModel.navigationEvent.observe(viewLifecycleOwner) { event ->
    when (event) {
        is NavigationEvent.Back -> findNavController().navigateUp()
        is NavigationEvent.ToDetail -> navigateToDetail(event.itemId)
        is NavigationEvent.ToProfile -> navigateToProfile(event.userId)
        is NavigationEvent.ToSettings -> navigateToSettings()
    }
}
```

#### 4. Формы и валидация

```kotlin
sealed class ValidationResult {
    object Valid : ValidationResult()
    sealed class Invalid : ValidationResult() {
        object EmptyField : Invalid()
        object TooShort : Invalid()
        object InvalidFormat : Invalid()
        data class Custom(val message: String) : Invalid()
    }
}

fun validateEmail(email: String): ValidationResult {
    return when {
        email.isBlank() -> ValidationResult.Invalid.EmptyField
        email.length < 5 -> ValidationResult.Invalid.TooShort
        !email.contains("@") -> ValidationResult.Invalid.InvalidFormat
        else -> ValidationResult.Valid
    }
}

val result = validateEmail(userInput)
when (result) {
    is ValidationResult.Valid -> submitForm()
    is ValidationResult.Invalid.EmptyField -> showError("Email cannot be empty")
    is ValidationResult.Invalid.TooShort -> showError("Email too short")
    is ValidationResult.Invalid.InvalidFormat -> showError("Invalid email format")
    is ValidationResult.Invalid.Custom -> showError(result.message)
}
```

### Sealed class vs Enum

| Аспект | Enum | Sealed Class |
|--------|------|--------------|
| **Экземпляры** | Одиночные | Множественные |
| **Данные** | Одинаковые для всех | Разные для каждого подтипа |
| **Наследование** | Невозможно | Возможно |
| **Use case** | Фиксированный набор значений | Иерархия связанных типов |

```kotlin
// Enum - фиксированные значения
enum class Status {
    LOADING, SUCCESS, ERROR
}

// Sealed class - разные данные для каждого подтипа
sealed class Status {
    object Loading : Status()
    data class Success(val data: String) : Status()
    data class Error(val message: String, val code: Int) : Status()
}
```

### Sealed interface (Kotlin 1.5+)

```kotlin
sealed interface Action {
    data class Click(val x: Int, val y: Int) : Action
    data class Scroll(val delta: Int) : Action
    object Refresh : Action
}

// Класс может реализовывать несколько sealed interface
class MyAction : Action, AnotherInterface {
    // ...
}
```

**English**: Sealed classes restrict class hierarchy - all subclasses must be declared in the same file. Ideal for modeling states and results with exhaustive `when` expressions (no `else` needed). Compiler knows all possible subtypes, providing compile-time safety. Unlike enums, sealed classes can have multiple instances and different data for each subtype.
