---
id: 20251012-122711177
title: "What To Put In State For Initial List / Что положить в State для начального списка"
topic: android
difficulty: easy
status: draft
created: 2025-10-13
tags: [android/state-management, android/ui, data-loading, state, state-management, ui, difficulty/easy]
moc: moc-android
related: [q-mvi-architecture--android--hard, q-intent-filters-android--android--medium, q-unit-testing-coroutines-flow--android--medium]
---

# What to put in state for initial list?

**Russian**: Что положить в state для отображения первоначального списка?

**English**: What to put in state for displaying the initial list?

## Answer (EN)
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

## Ответ (RU)

Для отображения начального состояния списка вы можете использовать **пустой список**, если данные загружаются асинхронно, или **заранее подготовленный статический список**, если данные известны при запуске приложения.

### Подход с асинхронной загрузкой

```kotlin
class ListViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    init {
        _items.value = emptyList() // Начальное пустое состояние
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

### С состояниями загрузки

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

### Подход со статическими данными

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


---

## Related Questions

### Computer Science Fundamentals
- [[q-list-vs-sequence--programming-languages--medium]] - Data Structures

### Kotlin Language Features
- [[q-list-set-map-differences--programming-languages--easy]] - Data Structures
- [[q-array-vs-list-kotlin--kotlin--easy]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures

### Related Algorithms
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Data Structures

### System Design Concepts
- [[q-message-queues-event-driven--system-design--medium]] - Data Structures
