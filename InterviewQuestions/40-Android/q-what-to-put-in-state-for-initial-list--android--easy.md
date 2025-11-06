---
id: android-082
title: State for Initial List / Состояние для начального списка
aliases:
- State for Initial List
- Состояние для начального списка
topic: android
subtopics:
- architecture-mvvm
- ui-state
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-data-loading
- c-mutablestate
- c-state-management
created: 2025-10-13
updated: 2025-10-31
tags:
- android/architecture-mvvm
- android/ui-state
- data-loading
- difficulty/easy
- state-management
- ui
date created: Saturday, November 1st 2025, 1:26:06 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)
> Состояние для начального списка

# Question (EN)
> State for Initial List

---

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


# Question (EN)
> State for Initial List

---


---


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

### Подход С Асинхронной Загрузкой

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

### С Состояниями Загрузки

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

### Подход Со Статическими Данными

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


## Follow-ups

- [[c-data-loading]]
- [[c-mutablestate]]
- [[c-state-management]]


## References

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)


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
