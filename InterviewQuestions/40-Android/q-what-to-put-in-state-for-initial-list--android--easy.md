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
- c-android-components
- c-jetpack-compose
- q-android-architectural-patterns--android--medium
created: 2025-10-13
updated: 2025-11-10
tags:
- android/architecture-mvvm
- android/ui-state
- ui-state
- difficulty/easy
---

# Вопрос (RU)
> Состояние для начального списка

# Question (EN)
> State for Initial `List`

---

## Ответ (RU)

Для отображения начального состояния списка обычно используют:

- **пустой список**, если данные загружаются асинхронно;
- **заранее подготовленный статический список**, если данные известны при запуске приложения.

Важно явно моделировать состояние загрузки, чтобы не путать «нет данных» и «данные ещё загружаются».

### Подход с асинхронной загрузкой (без отдельного состояния загрузки)

```kotlin
class ListViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    init {
        _items.value = emptyList() // Начальное пустое состояние (данные ещё не загружены)
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

Недостаток: UI не отличает «загружаемся» от «получили пустой список».

### Подход с явными состояниями загрузки

```kotlin
sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<out T>(val data: T) : UiState<T>()
    data class Error(val throwable: Throwable) : UiState<Nothing>()
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
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

Здесь начальному состоянию однозначно соответствует `UiState.Loading`.

### Подход со статическими начальными данными

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

Этот подход подходит для подсказок, заглушек или заранее известных локальных данных.

---

## Answer (EN)

For the initial list state you typically use:

- an **empty list** when data is loaded asynchronously; or
- a **predefined static list** when data is known at app startup.

It is important to explicitly model loading state so you don’t confuse “no data yet” with “loaded empty list”.

### Async loading approach (no explicit loading state)

```kotlin
class ListViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    init {
        _items.value = emptyList() // Initial empty state (data not loaded yet)
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

Limitation: the UI cannot distinguish “loading” from “loaded empty list”.

### With explicit loading states

```kotlin
sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<out T>(val data: T) : UiState<T>()
    data class Error(val throwable: Throwable) : UiState<Nothing>()
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
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

Here the initial state is clearly `UiState.Loading`.

### Static data approach

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

This is suitable for hints, placeholders, or otherwise known local data.

---

## Дополнительные вопросы (RU)

- [[c-android-components]]
- [[c-jetpack-compose]]
- Как бы вы реализовали состояние загрузки и пустого результата в Jetpack Compose `LazyColumn`?
- Как можно обрабатывать состояние ошибки и повторной попытки загрузки списка?
- Как менять начальное состояние списка в зависимости от типа пользователя или кэша?

## Follow-ups

- [[c-android-components]]
- [[c-jetpack-compose]]
- How would you implement loading and empty states in a Jetpack Compose `LazyColumn`?
- How do you handle error and retry states for list loading?
- How can initial list state depend on user type or cached data?


## Ссылки (RU)

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)

## References

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)


## Связанные вопросы (RU)

### Базовые концепции информатики
- [[q-list-vs-sequence--programming-languages--medium]] - Структуры данных

### Особенности языка Kotlin
- [[q-array-vs-list-kotlin--kotlin--easy]] - Структуры данных
- [[q-kotlin-collections--kotlin--medium]] - Структуры данных
- [[q-list-vs-sequence--kotlin--medium]] - Структуры данных

### Связанные алгоритмы
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Структуры данных

### Концепции системного дизайна
- [[q-message-queues-event-driven--system-design--medium]] - Структуры данных

## Related Questions

### Computer Science Fundamentals
- [[q-list-vs-sequence--programming-languages--medium]] - Data Structures

### Kotlin Language Features
- [[q-array-vs-list-kotlin--kotlin--easy]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures

### Related Algorithms
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Data Structures

### System Design Concepts
- [[q-message-queues-event-driven--system-design--medium]] - Data Structures
