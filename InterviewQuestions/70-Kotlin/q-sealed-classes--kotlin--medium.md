---
id: 20251012-154386
title: "Sealed Classes"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-13
tags:
  - kotlin
  - sealed-classes
  - type-safety
moc: moc-kotlin
related: [q-heap-pollution-generics--kotlin--hard, q-kotlin-safe-cast--programming-languages--easy, q-channelflow-callbackflow-flow--kotlin--medium]
  - q-sealed-class-sealed-interface--kotlin--medium.md
subtopics: [sealed-classes, enums, when-expression]
---
# What is special about sealed classes in Kotlin?

# Вопрос (RU)
> В чем особенность sealed классов

## Answer (EN)

The special feature of sealed classes is the restriction of the inheritance hierarchy: all their subclasses must be declared in the same file as the sealed class itself.

### Main Idea

Sealed classes are ideal for creating restricted class hierarchies where you need to strictly control the set of possible subtypes, especially when modeling states or operation results.

```kotlin
// Sealed class for modeling UI states
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<User>) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Advantages with `when`

The compiler knows all possible subtypes, so no `else` branch is needed.

```kotlin
fun handleState(state: UiState) {
    when (state) {
        is UiState.Loading -> showLoading()
        is UiState.Success -> showData(state.data)
        is UiState.Error -> showError(state.message)
        // no else needed - compiler knows all variants!
    }
}
```

If you add a new subtype:

```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<User>) : UiState()
    data class Error(val message: String) : UiState()
    object Empty : UiState()  // New subtype
}

// The compiler will show an error in all `when` expressions without handling Empty!
```

### Use Cases

#### 1. Modeling Operation Results

```kotlin
sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Usage
suspend fun loadUser(id: Int): Result<User> {
    return try {
        val user = apiService.getUser(id)
        Result.Success(user)
    } catch (e: Exception) {
        Result.Error(e)
    }
}

// In ViewModel
viewModelScope.launch {
    _uiState.value = Result.Loading
    val result = loadUser(123)
    _uiState.value = result
}

// In UI
result.observe(this) { result ->
    when (result) {
        is Result.Loading -> showProgressBar()
        is Result.Success -> updateUI(result.value)
        is Result.Error -> showError(result.exception.message)
    }
}
```

#### 2. Modeling Network Requests

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

#### 3. Navigation Events

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

// In Fragment
viewModel.navigationEvent.observe(viewLifecycleOwner) { event ->
    when (event) {
        is NavigationEvent.Back -> findNavController().navigateUp()
        is NavigationEvent.ToDetail -> navigateToDetail(event.itemId)
        is NavigationEvent.ToProfile -> navigateToProfile(event.userId)
        is NavigationEvent.ToSettings -> navigateToSettings()
    }
}
```

### Sealed class vs Enum

| Aspect | Enum | Sealed Class |
|---|---|---|
| **Instances** | Single | Multiple |
| **Data** | Same for all | Different for each subtype |
| **Inheritance** | Not possible | Possible |
| **Use case** | Fixed set of values | Hierarchy of related types |

```kotlin
// Enum - fixed values
enum class Status {
    LOADING, SUCCESS, ERROR
}

// Sealed class - different data for each subtype
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

// A class can implement multiple sealed interfaces
class MyAction : Action, AnotherInterface {
    // ...
}
```

## Ответ (RU)
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

## Related Questions

- [[q-heap-pollution-generics--kotlin--hard]]
- [[q-kotlin-safe-cast--programming-languages--easy]]
- [[q-channelflow-callbackflow-flow--kotlin--medium]]
