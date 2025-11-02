---
id: android-197
title: "What Is Viewmodel / Что такое ViewModel"
aliases: ["What Is ViewModel", "Что такое ViewModel"]
topic: android
subtopics: [architecture-mvvm, lifecycle, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-factory-pattern-android--android--medium, q-mvvm-pattern--android--medium, q-viewmodel-vs-onsavedinstancestate--android--medium]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/architecture-mvvm, android/lifecycle, android/ui-state, architecture, difficulty/medium, mvvm, state-management, viewmodel]
date created: Saturday, November 1st 2025, 12:47:09 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)

Что такое ViewModel в Android?

# Question (EN)

What is ViewModel in Android?

---

## Ответ (RU)

**ViewModel** — это класс Android Architecture Components, который является **держателем бизнес-логики и состояния уровня экрана**. Его главное преимущество — **автоматическое сохранение состояния при изменениях конфигурации** (поворот экрана, смена языка).

### Ключевые Характеристики

1. **Привязка к области видимости**: ViewModel создается в связке с Activity или Fragment и живет до их завершения
2. **Переживает пересоздание**: Один экземпляр ViewModel выживает через множественные вызовы `onCreate()` при изменениях конфигурации
3. **Управление данными для UI**: Единственная ответственность — хранить и управлять UI-данными
4. **Изоляция от UI**: Никогда не должен хранить ссылки на View, Activity, Fragment или Context (кроме ApplicationContext)

### Базовый Пример Использования

```kotlin
// ViewModel
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser() {
        viewModelScope.launch {  // ✅ автоматическая отмена при уничтожении
            val user = repository.getUser()
            _user.value = user
        }
    }
}

// Activity
class UserActivity : AppCompatActivity() {
    private val viewModel by viewModels<UserViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ данные переживают поворот экрана
        viewModel.user.observe(this) { user ->
            updateUI(user)
        }
    }
}
```

### Жизненный Цикл ViewModel

ViewModel создается при первом вызове `onCreate()` и **уничтожается только при финальном завершении** Activity/Fragment:

- Activity finish → `ViewModel.onCleared()` вызывается
- Configuration change (rotation) → ViewModel НЕ пересоздается, возвращается тот же экземпляр
- Fragment detach → `onCleared()` вызывается

```kotlin
class MyViewModel : ViewModel() {
    init {
        Log.d("VM", "Created once")  // ✅ вызывается один раз
    }

    override fun onCleared() {
        Log.d("VM", "Cleared")  // ❌ НЕ вызывается при rotation
                                 // ✅ вызывается при finish()
    }
}
```

### Коммуникация Между Fragment'ами

Shared ViewModel позволяет Fragment'ам общаться без прямых ссылок друг на друга:

```kotlin
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment A и B получают ОДИН экземпляр через Activity scope
class FragmentA : Fragment() {
    private val viewModel by activityViewModels<SharedViewModel>()

    fun onItemClick(item: Item) {
        viewModel.selectItem(item)  // Fragment B получит обновление
    }
}
```

### Преимущества ViewModel

**1. Автоматическое сохранение состояния**

Без ViewModel данные теряются при rotation и требуют ручного сохранения через `onSaveInstanceState()`.

**2. Разделение ответственности**

ViewModel инкапсулирует бизнес-логику, UI отвечает только за отображение.

**3. Поддержка корутин**

`viewModelScope` автоматически отменяет корутины при `onCleared()`.

**4. Тестируемость**

ViewModel легко тестировать без зависимости от Android framework.

### SavedStateHandle Для Process Death

ViewModel НЕ переживает process death (система убивает процесс при нехватке памяти). Для этого используется **SavedStateHandle**:

```kotlin
class SavedStateViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ✅ переживает и rotation, и process death
    var userName: String?
        get() = savedStateHandle["user_name"]
        set(value) { savedStateHandle["user_name"] = value }
}
```

### Dependency Injection

**С Hilt** (рекомендуется):

```kotlin
@HiltViewModel
class ProductsViewModel @Inject constructor(
    private val repository: ProductRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Hilt автоматически предоставляет зависимости
}

@AndroidEntryPoint
class ProductsActivity : AppCompatActivity() {
    private val viewModel by viewModels<ProductsViewModel>()
}
```

**С ручной фабрикой**:

```kotlin
class UserViewModelFactory(
    private val userId: String
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return UserViewModel(userId) as T
    }
}

// Usage
private val viewModel by viewModels<UserViewModel> {
    UserViewModelFactory(userId)
}
```

### Резюме

ViewModel — компонент архитектуры для управления UI-данными с учетом жизненного цикла. Переживает configuration changes, изолирует бизнес-логику от UI, поддерживает корутины и DI. Для process death нужен SavedStateHandle.

## Answer (EN)

**ViewModel** is an Android Architecture Component class that acts as a **business logic and screen-level state holder**. Its main advantage is **automatic state persistence through configuration changes** (screen rotation, language change).

### Key Characteristics

1. **Scope-bound**: ViewModel is created in association with an Activity or Fragment and lives until they finish
2. **Survives recreation**: A single ViewModel instance survives multiple `onCreate()` calls during configuration changes
3. **UI data management**: Its sole responsibility is to store and manage UI-related data
4. **UI isolation**: Should never hold references to Views, Activities, Fragments, or Context (except ApplicationContext)

### Basic Usage Example

```kotlin
// ViewModel
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser() {
        viewModelScope.launch {  // ✅ automatic cancellation on clear
            val user = repository.getUser()
            _user.value = user
        }
    }
}

// Activity
class UserActivity : AppCompatActivity() {
    private val viewModel by viewModels<UserViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ data survives screen rotation
        viewModel.user.observe(this) { user ->
            updateUI(user)
        }
    }
}
```

### ViewModel Lifecycle

ViewModel is created on the first `onCreate()` call and **destroyed only on final termination** of Activity/Fragment:

- Activity finish → `ViewModel.onCleared()` is called
- Configuration change (rotation) → ViewModel NOT recreated, same instance returned
- Fragment detach → `onCleared()` is called

```kotlin
class MyViewModel : ViewModel() {
    init {
        Log.d("VM", "Created once")  // ✅ called once
    }

    override fun onCleared() {
        Log.d("VM", "Cleared")  // ❌ NOT called on rotation
                                 // ✅ called on finish()
    }
}
```

### Inter-Fragment Communication

Shared ViewModel allows Fragments to communicate without direct references:

```kotlin
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment A and B get ONE instance through Activity scope
class FragmentA : Fragment() {
    private val viewModel by activityViewModels<SharedViewModel>()

    fun onItemClick(item: Item) {
        viewModel.selectItem(item)  // Fragment B receives update
    }
}
```

### ViewModel Benefits

**1. Automatic state retention**

Without ViewModel, data is lost on rotation and requires manual saving via `onSaveInstanceState()`.

**2. Separation of concerns**

ViewModel encapsulates business logic; UI is only responsible for display.

**3. Coroutines support**

`viewModelScope` automatically cancels coroutines in `onCleared()`.

**4. Testability**

ViewModel is easy to test without Android framework dependencies.

### SavedStateHandle for Process Death

ViewModel does NOT survive process death (system kills process under memory pressure). For this, use **SavedStateHandle**:

```kotlin
class SavedStateViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ✅ survives both rotation and process death
    var userName: String?
        get() = savedStateHandle["user_name"]
        set(value) { savedStateHandle["user_name"] = value }
}
```

### Dependency Injection

**With Hilt** (recommended):

```kotlin
@HiltViewModel
class ProductsViewModel @Inject constructor(
    private val repository: ProductRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Hilt automatically provides dependencies
}

@AndroidEntryPoint
class ProductsActivity : AppCompatActivity() {
    private val viewModel by viewModels<ProductsViewModel>()
}
```

**With manual factory**:

```kotlin
class UserViewModelFactory(
    private val userId: String
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return UserViewModel(userId) as T
    }
}

// Usage
private val viewModel by viewModels<UserViewModel> {
    UserViewModelFactory(userId)
}
```

### Summary

ViewModel is an architecture component for lifecycle-aware UI data management. Survives configuration changes, isolates business logic from UI, supports coroutines and DI. SavedStateHandle is needed for process death scenarios.

---

## Follow-ups

1. What's the difference between ViewModel and onSaveInstanceState()?
2. How does SavedStateHandle survive process death while ViewModel doesn't?
3. When should you use activityViewModels() vs viewModels()?
4. What happens if ViewModel holds a reference to Activity?
5. How to test ViewModel with viewModelScope coroutines?

## References

- [ViewModel Overview - Android Developers](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [ViewModel API Reference](https://developer.android.com/reference/androidx/lifecycle/ViewModel)
- [ViewModels: A Simple Example - Medium](https://medium.com/androiddevelopers/viewmodels-a-simple-example-ed5ac416317e)
- [[q-mvvm-pattern--android--medium]]
- [[q-factory-pattern-android--android--medium]]

## Related Questions

### Prerequisites (Easier)

- [[q-view-methods-and-their-purpose--android--medium]] - Understanding Android View lifecycle
- [[q-mvvm-pattern--android--medium]] - MVVM pattern overview

### Related (Same Level)

- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation comparison
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel internals
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - ViewModel limitations

### Advanced (Harder)

- [[q-clean-architecture-android--android--hard]] - Clean Architecture with ViewModel
- [[q-mvi-architecture--android--hard]] - MVI vs MVVM
- [[q-offline-first-architecture--android--hard]] - Offline-first patterns
