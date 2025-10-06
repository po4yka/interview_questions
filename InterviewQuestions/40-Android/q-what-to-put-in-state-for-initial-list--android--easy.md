---
tags:
  - android
  - android/state-management
  - android/ui
  - data loading
  - state
  - state-management
  - ui
difficulty: easy
---

# Что положить в state для отображения первоначального списка?

**English**: What to put in state for displaying the initial list?

## Answer

For the initial list state, you can use an **empty list** if data loads asynchronously, or a **pre-prepared static list** if data is known at app startup.

### Async Loading Approach

```kotlin
class ListViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    init {
        _items.value = emptyList() // Initial empty state
        loadItems()
    }

    private fun loadItems() {
        viewModelScope.launch {
            val data = repository.getItems()
            _items.value = data
        }
    }
}
```

### With Loading States

```kotlin
sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}

class ListViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<List<Item>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<Item>>> = _uiState

    init {
        loadItems()
    }

    private fun loadItems() {
        viewModelScope.launch {
            try {
                val items = repository.getItems()
                _uiState.value = UiState.Success(items)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

### Static Data Approach

```kotlin
class ListViewModel : ViewModel() {
    private val _items = MutableStateFlow(getInitialItems())
    val items: StateFlow<List<Item>> = _items

    private fun getInitialItems(): List<Item> {
        return listOf(
            Item(1, "Item 1"),
            Item(2, "Item 2"),
            Item(3, "Item 3")
        )
    }
}
```

## Ответ

Для отображения первоначального списка в state можно положить пустой массив, если данные загружаются асинхронно, или заранее подготовленный статический список, если данные известны на момент загрузки приложения.

