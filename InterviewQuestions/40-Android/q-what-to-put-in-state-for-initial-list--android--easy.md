---
id: 202510031421
title: What to put in state for displaying the initial list / Что положить в state для отображения первоначального списка
aliases: []

# Classification
topic: android
subtopics: [android, ui, state-management]
question_kind: practical
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/800
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-state-management
  - c-android-viewmodel

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [state, data loading, difficulty/easy, easy_kotlin, lang/ru, android/state-management, android/ui]
---

# Question (EN)
> What to put in state for displaying the initial list

# Вопрос (RU)
> Что положить в state для отображения первоначального списка

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

Для отображения первоначального списка в state можно положить пустой массив, если данные загружаются асинхронно, или заранее подготовленный статический список, если данные известны на момент загрузки приложения.

---

## Follow-ups
- How do you handle pagination in list state?
- What's the difference between using LiveData vs StateFlow for list state?
- How do you preserve list state during configuration changes?

## References
- [[c-android-state-management]]
- [[c-android-viewmodel]]
- [[c-android-livedata]]
- [[c-android-stateflow]]
- [[moc-android]]

## Related Questions
- [[q-viewmodel-pattern--android--easy]]
- [[q-which-layout-for-large-list--android--easy]]
