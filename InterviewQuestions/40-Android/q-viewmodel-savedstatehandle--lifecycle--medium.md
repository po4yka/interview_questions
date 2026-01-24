---
id: android-lc-008
title: ViewModel with SavedStateHandle / ViewModel с SavedStateHandle
aliases: []
topic: android
subtopics:
- lifecycle
- viewmodel
- state
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-viewmodel
- c-state
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/viewmodel
- android/state
- difficulty/medium
anki_cards:
- slug: android-lc-008-0-en
  language: en
  anki_id: 1769172286682
  synced_at: '2026-01-23T16:45:06.237471'
- slug: android-lc-008-0-ru
  language: ru
  anki_id: 1769172286707
  synced_at: '2026-01-23T16:45:06.238541'
---
# Question (EN)
> What is SavedStateHandle and how to use it in ViewModel?

# Vopros (RU)
> Что такое SavedStateHandle и как его использовать в ViewModel?

---

## Answer (EN)

**SavedStateHandle** is a key-value map that survives **process death**, unlike regular ViewModel properties.

**Why needed:**
- ViewModel survives config changes but NOT process death
- SavedStateHandle survives BOTH
- Bridges the gap between ViewModel and savedInstanceState

**Usage:**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Survives process death
    val searchQuery: StateFlow<String> =
        savedStateHandle.getStateFlow("query", "")

    fun setQuery(query: String) {
        savedStateHandle["query"] = query
    }

    // Does NOT survive process death
    var cachedResults: List<Item>? = null
}
```

**What to store:**
| Use SavedStateHandle | Use regular properties |
|---------------------|------------------------|
| User input (search query) | Cached network data |
| Selected item ID | Derived state |
| Scroll position | Large objects |
| Form draft state | Computed values |

**Size limit:** Same as Bundle (~1MB for process)

**Getting SavedStateHandle:**
```kotlin
// With Hilt (automatic injection)
@HiltViewModel
class MyViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle,
    private val repository: Repository
) : ViewModel()

// Without Hilt (factory)
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    companion object {
        val Factory: ViewModelProvider.Factory = viewModelFactory {
            initializer {
                val savedStateHandle = createSavedStateHandle()
                MyViewModel(savedStateHandle)
            }
        }
    }
}
```

**LiveData vs StateFlow:**
```kotlin
// LiveData approach
val query: MutableLiveData<String> = savedStateHandle.getLiveData("query")

// StateFlow approach (preferred with Compose)
val query: StateFlow<String> = savedStateHandle.getStateFlow("query", "")
```

## Otvet (RU)

**SavedStateHandle** - это map ключ-значение, который переживает **смерть процесса**, в отличие от обычных свойств ViewModel.

**Зачем нужен:**
- ViewModel переживает изменения конфигурации, но НЕ смерть процесса
- SavedStateHandle переживает ОБА
- Связывает ViewModel и savedInstanceState

**Использование:**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Переживает смерть процесса
    val searchQuery: StateFlow<String> =
        savedStateHandle.getStateFlow("query", "")

    fun setQuery(query: String) {
        savedStateHandle["query"] = query
    }

    // НЕ переживает смерть процесса
    var cachedResults: List<Item>? = null
}
```

**Что хранить:**
| Используйте SavedStateHandle | Используйте обычные свойства |
|-----------------------------|------------------------------|
| Ввод пользователя (поисковый запрос) | Кэшированные данные из сети |
| ID выбранного элемента | Производное состояние |
| Позиция прокрутки | Большие объекты |
| Черновик формы | Вычисляемые значения |

**Лимит размера:** Такой же как Bundle (~1МБ на процесс)

**Получение SavedStateHandle:**
```kotlin
// С Hilt (автоматическая инъекция)
@HiltViewModel
class MyViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle,
    private val repository: Repository
) : ViewModel()

// Без Hilt (фабрика)
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    companion object {
        val Factory: ViewModelProvider.Factory = viewModelFactory {
            initializer {
                val savedStateHandle = createSavedStateHandle()
                MyViewModel(savedStateHandle)
            }
        }
    }
}
```

**LiveData vs StateFlow:**
```kotlin
// Подход LiveData
val query: MutableLiveData<String> = savedStateHandle.getLiveData("query")

// Подход StateFlow (предпочтительнее с Compose)
val query: StateFlow<String> = savedStateHandle.getStateFlow("query", "")
```

---

## Follow-ups
- What are the size limits of SavedStateHandle?
- How does SavedStateHandle work with Navigation arguments?
- When to use SavedStateHandle vs Room for persistence?

## References
- [[c-lifecycle]]
- [[c-viewmodel]]
- [[c-state]]
- [[moc-android]]
