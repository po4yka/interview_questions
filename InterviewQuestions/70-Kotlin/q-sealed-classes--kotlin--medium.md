---
id: kotlin-136
title: Sealed Classes / Sealed классы в Kotlin
topic: kotlin
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
created: 2025-10-13
updated: 2025-11-09
tags:
- difficulty/medium
- kotlin
- sealed-classes
- type-safety
moc: moc-kotlin
aliases:
- What is special about sealed classes in Kotlin?
- Особенности sealed классов в Kotlin
question_kind: theory
related:
- c-kotlin
- c-sealed-classes
- q-channelflow-callbackflow-flow--kotlin--medium
subtopics:
- enums
- sealed-classes
- when-expression
---
# Вопрос (RU)
> В чем особенность sealed классов в Kotlin?

# Question (EN)
> What is special about sealed classes in Kotlin?

## Ответ (RU)
Особенность запечатанных (sealed) классов заключается в том, что они задают ограниченную (закрытую) иерархию типов: компилятор знает полный набор допустимых подтипов и может проверять их исчерпывающим образом (при соблюдении правил видимости и размещения). В современных версиях Kotlin их прямые наследники должны находиться в том же модуле (ранее — в одном файле; затем — в том же пакете и модуле), с возможностью объявления в разных файлах, что сохраняет строгий контроль над иерархией.

### Основная Идея

Sealed классы идеальны для создания ограниченных иерархий, где требуется строго контролировать набор возможных подтипов, особенно при моделировании состояний или результатов операций (см. [[c-kotlin]], [[c-sealed-classes]]).

```kotlin
// Sealed class для моделирования состояний UI
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<User>) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Преимущества При Использовании `when`

Так как компилятор может знать все допустимые подтипы sealed-класса (когда вся иерархия видима в текущем модуле), он может проверять `when` на исчерпываемость, и ветка `else` может быть не нужна.

```kotlin
fun handleState(state: UiState) {
    when (state) {
        is UiState.Loading -> showLoading()
        is UiState.Success -> showData(state.data)
        is UiState.Error -> showError(state.message)
        // else не нужен - компилятор знает все варианты здесь
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

// Все исчерпывающие when по UiState без обработки Empty
// перестанут компилироваться.
```

### Примеры Использования

#### 1. Моделирование Результата Операции

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val value: T) : Result<T>()
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

// В UI (пример с LiveData)
result.observe(this) { resultValue ->
    when (resultValue) {
        is Result.Loading -> showProgressBar()
        is Result.Success -> updateUI(resultValue.value)
        is Result.Error -> showError(resultValue.exception.message)
    }
}
```

#### 2. Моделирование Сетевых Запросов

```kotlin
sealed class NetworkResponse<out T> {
    data class Success<out T>(val data: T) : NetworkResponse<T>()
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

#### 3. Навигационные События

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

// Во Fragment
viewModel.navigationEvent.observe(viewLifecycleOwner) { event ->
    when (event) {
        is NavigationEvent.Back -> findNavController().navigateUp()
        is NavigationEvent.ToDetail -> navigateToDetail(event.itemId)
        is NavigationEvent.ToProfile -> navigateToProfile(event.userId)
        is NavigationEvent.ToSettings -> navigateToSettings()
    }
}
```

### Sealed Class Vs Enum

| Аспект | Enum | Sealed Class |
|--------|------|--------------|
| **Экземпляры** | Один экземпляр на константу | Потенциально много экземпляров каждого подтипа |
| **Данные** | Одинаковая фиксированная структура для всех констант | У каждого подтипа свои поля и состояние |
| **Наследование** | Константы enum нельзя произвольно расширять | Sealed class может иметь множество различных наследников |
| **Use case** | Фиксированный набор простых значений | Иерархия связанных типов с данными/поведением |

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

### Sealed Interface (Kotlin 1.5+)

Sealed-интерфейсы работают аналогично sealed-классам: они ограничивают набор реализаций в рамках модуля (ранее также действовало требование к размещению в том же пакете/файле), что позволяет компилятору выполнять исчерпывающую проверку `when`, когда все реализации видимы.

```kotlin
sealed interface Action {
    data class Click(val x: Int, val y: Int) : Action
    data class Scroll(val delta: Int) : Action
    object Refresh : Action
}

// Класс может реализовывать несколько sealed-интерфейсов
class MyAction : Action, AnotherInterface {
    // ...
}
```

## Answer (EN)

The key feature of sealed classes is the restricted inheritance hierarchy: they define a closed set of subclasses that the compiler can be aware of and check exhaustively (subject to visibility and placement rules). In modern Kotlin, their direct subclasses must be declared in the same module (originally: same file; later: same package and module), potentially in different files, which still provides strong control over the type hierarchy.

### Main Idea

Sealed classes are ideal for creating restricted class hierarchies where you need to strictly control the set of possible subtypes, especially when modeling states or operation results (see [[c-kotlin]], [[c-sealed-classes]]).

```kotlin
// Sealed class for modeling UI states
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<User>) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Advantages with `when`

Because the compiler can know all permitted subtypes of a sealed class (when the whole hierarchy is visible within the current module), `when` expressions over them can be exhaustiveness-checked and may not require an `else` branch.

```kotlin
fun handleState(state: UiState) {
    when (state) {
        is UiState.Loading -> showLoading()
        is UiState.Success -> showData(state.data)
        is UiState.Error -> showError(state.message)
        // no else needed - compiler knows all variants here
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

// All exhaustive `when` expressions on UiState
// that don't handle Empty will now fail to compile.
```

### Use Cases

#### 1. Modeling Operation Results

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val value: T) : Result<T>()
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

// In UI (example with LiveData)
result.observe(this) { resultValue ->
    when (resultValue) {
        is Result.Loading -> showProgressBar()
        is Result.Success -> updateUI(resultValue.value)
        is Result.Error -> showError(resultValue.exception.message)
    }
}
```

#### 2. Modeling Network Requests

```kotlin
sealed class NetworkResponse<out T> {
    data class Success<out T>(val data: T) : NetworkResponse<T>()
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

### Sealed Class Vs Enum

| Aspect | Enum | Sealed Class |
|---|---|---|
| **Instances** | One instance per constant | Potentially multiple instances per subtype |
| **Data** | Same fixed fields for all constants | Each subtype can have its own fields and state |
| **Inheritance** | Enum constants can't be extended arbitrarily | Sealed class can have multiple distinct subclasses |
| **Use case** | Fixed set of simple values | Hierarchy of related types with data/behavior |

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

### Sealed Interface (Kotlin 1.5+)

Sealed interfaces work similarly to sealed classes: they declare a restricted set of implementations within the same module (historically also constrained to the same package/file), enabling exhaustiveness checks with `when` when all implementations are visible.

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

## Дополнительные Вопросы (RU)

- В чем ключевые отличия sealed-классов от подхода в Java?
- Когда вы бы использовали sealed-классы на практике?
- Каковы распространенные ошибки при работе с sealed-классами?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-heap-pollution-generics--kotlin--hard]]
- [[q-channelflow-callbackflow-flow--kotlin--medium]]

## Related Questions

- [[q-heap-pollution-generics--kotlin--hard]]
- [[q-channelflow-callbackflow-flow--kotlin--medium]]
