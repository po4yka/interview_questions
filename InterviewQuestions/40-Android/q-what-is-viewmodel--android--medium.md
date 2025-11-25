---
id: android-197
title: What Is Viewmodel / Что такое ViewModel
aliases: [What Is ViewModel, Что такое ViewModel]
topic: android
subtopics:
  - architecture-mvvm
  - lifecycle
  - ui-state
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-lifecycle
  - c-mvvm
  - q-mvvm-pattern--android--medium
  - q-testing-viewmodels-turbine--android--medium
  - q-viewmodel-pattern--android--easy
  - q-viewmodel-vs-onsavedinstancestate--android--medium
  - q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/architecture-mvvm, android/lifecycle, android/ui-state, architecture, difficulty/medium, mvvm, state-management, viewmodel]

date created: Saturday, November 1st 2025, 12:47:09 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Что такое `ViewModel` в Android?

# Question (EN)

> What is `ViewModel` in Android?

---

## Ответ (RU)

**`ViewModel`** — это класс Android Architecture Components, который является **держателем состояния и UI-ориентированной логики уровня экрана**. Его главное преимущество — **сохранение состояний в памяти при изменениях конфигурации** (поворот экрана, смена языка) без повторной загрузки данных. При этом сам по себе `ViewModel` не переживает уничтожение процесса системой.

### Ключевые Характеристики

1. **Привязка к области видимости**: `ViewModel` создается в связке с `Activity`, `Fragment` или другим `ViewModelStoreOwner` и живет до их окончательного уничтожения.
2. **Переживает пересоздание**: Один экземпляр `ViewModel` выживает через множественные вызовы `onCreate()` при изменениях конфигурации.
3. **Управление данными для UI**: Основная ответственность — хранить и управлять UI-данными и UI-ориентированной логикой, делегируя «чистую» бизнес-логику в репозитории/UseCase-слой.
4. **Изоляция от UI**: Не должен хранить ссылки на `View`, `Activity`, `Fragment` или `Context` (кроме безопасного `Application`-context при использовании `AndroidViewModel`).

### Базовый Пример Использования

```kotlin
// ViewModel
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser() {
        viewModelScope.launch {  // ✅ автоматическая отмена при onCleared()
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

        // ✅ данные переживают поворот экрана в рамках того же процесса и scope
        viewModel.user.observe(this) { user ->
            updateUI(user)
        }
    }
}
```

### Жизненный Цикл `ViewModel`

`ViewModel` создается при первом запросе через `ViewModelProvider` (часто в `onCreate()`/`onViewCreated()`) и **уничтожается только при финальном завершении** соответствующего `ViewModelStoreOwner`:

- `Activity` finish → вызывается `ViewModel.onCleared()`.
- Configuration change (rotation) → `ViewModel` НЕ пересоздается, возвращается тот же экземпляр.
- `Fragment` окончательно уничтожен (owner удален из иерархии / `Fragment` не пересоздается) → вызывается `onCleared()`.

```kotlin
class MyViewModel : ViewModel() {
    init {
        Log.d("VM", "Created")  // ✅ вызывается один раз для каждого экземпляра ViewModel
    }

    override fun onCleared() {
        Log.d("VM", "Cleared")  // ❌ НЕ вызывается при rotation, пока владелец реконфигурируется
                                   // ✅ вызывается при финальном уничтожении владельца
    }
}
```

### Коммуникация Между `Fragment`'ами

Shared `ViewModel` позволяет `Fragment`'ам общаться без прямых ссылок друг на друга, если они используют один и тот же `ViewModelStoreOwner` (обычно `Activity`):

```kotlin
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment A и Fragment B получают ОДИН экземпляр через Activity scope
class FragmentA : Fragment() {
    private val viewModel by activityViewModels<SharedViewModel>()

    fun onItemClick(item: Item) {
        viewModel.selectItem(item)  // Fragment B получит обновление
    }
}

class FragmentB : Fragment() {
    private val viewModel by activityViewModels<SharedViewModel>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            // обрабатываем выбранный элемент
        }
    }
}
```

### Преимущества `ViewModel`

**1. Сохранение состояния при конфигурационных изменениях**

Без `ViewModel` данные легко теряются при rotation и требуют ручного сохранения через `onSaveInstanceState()`. `ViewModel` позволяет держать их в памяти между пересозданиями.

**2. Разделение ответственности**

`ViewModel` инкапсулирует UI-ориентированную логику и работу с источниками данных; UI отвечает только за отображение.

**3. Поддержка корутин**

`viewModelScope` автоматически отменяет корутины при `onCleared()`.

**4. Тестируемость**

`ViewModel` легко тестировать без зависимости от Android framework.

### SavedStateHandle Для Process Death

`ViewModel` НЕ переживает уничтожение процесса (system process death). Для восстановления критичных данных используется **SavedStateHandle**, который интегрирован с механизмом сохранения состояния (`SavedStateRegistry` / `onSaveInstanceState()`): при пересоздании процесса значения из него восстанавливаются и передаются в новый экземпляр `ViewModel`.

```kotlin
class SavedStateViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ✅ значения могут быть восстановлены после rotation и process death,
    // если они были сохранены в SavedStateHandle
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

`ViewModel` — компонент архитектуры для управления UI-данными с учетом жизненного цикла владельца. Переживает configuration changes в рамках процесса и выбранного scope, изолирует UI-ориентированную логику от UI-слоя, поддерживает корутины и DI. Для восстановления состояния после process death используются механизмы сохранения состояния, такие как `SavedStateHandle`.

## Answer (EN)

**`ViewModel`** is an Android Architecture Component class that acts as a **screen-level state holder and UI-related logic holder**. Its main advantage is **keeping state in memory across configuration changes** (screen rotation, language change) without refetching data. By itself, a `ViewModel` does not survive system process death.

### Key Characteristics

1. **Scope-bound**: A `ViewModel` is created in association with an `Activity`, `Fragment`, or other `ViewModelStoreOwner` and lives until that owner is finally destroyed.
2. **Survives recreation**: A single `ViewModel` instance survives multiple `onCreate()` calls during configuration changes.
3. **UI data management**: Its primary responsibility is to store and manage UI-related data and UI logic, delegating core business logic to repositories/use cases.
4. **UI isolation**: It should not hold references to `View`, `Activity`, `Fragment`, or `Context` (except a safe `Application` context when using `AndroidViewModel`).

### Basic Usage Example

```kotlin
// ViewModel
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser() {
        viewModelScope.launch {  // ✅ automatic cancellation in onCleared()
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

        // ✅ data survives screen rotation within the same process and scope
        viewModel.user.observe(this) { user ->
            updateUI(user)
        }
    }
}
```

### `ViewModel` Lifecycle

A `ViewModel` is created when first requested via `ViewModelProvider` (often in `onCreate()`/`onViewCreated()`) and **destroyed only when its `ViewModelStoreOwner` is finally finished**:

- `Activity` finish → `ViewModel.onCleared()` is called.
- Configuration change (rotation) → `ViewModel` is NOT recreated; the same instance is returned.
- `Fragment` is permanently destroyed (owner removed from hierarchy / `Fragment` not recreated) → `onCleared()` is called.

```kotlin
class MyViewModel : ViewModel() {
    init {
        Log.d("VM", "Created")  // ✅ called once per ViewModel instance
    }

    override fun onCleared() {
        Log.d("VM", "Cleared")  // ❌ NOT called during a transient rotation while owner is being recreated
                                   // ✅ called when the owner is finally destroyed
    }
}
```

### Inter-`Fragment` Communication

A shared `ViewModel` allows Fragments to communicate without direct references, as long as they use the same `ViewModelStoreOwner` (typically the host `Activity`):

```kotlin
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment A and Fragment B obtain ONE shared instance via Activity scope
class FragmentA : Fragment() {
    private val viewModel by activityViewModels<SharedViewModel>()

    fun onItemClick(item: Item) {
        viewModel.selectItem(item)  // Fragment B receives update
    }
}

class FragmentB : Fragment() {
    private val viewModel by activityViewModels<SharedViewModel>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            // handle selected item
        }
    }
}
```

### `ViewModel` Benefits

**1. State retention across configuration changes**

Without a `ViewModel`, data is easily lost on rotation and requires manual saving via `onSaveInstanceState()`. `ViewModel` keeps it in memory between recreations.

**2. Separation of concerns**

`ViewModel` encapsulates UI-related logic and interactions with data sources; the UI layer is only responsible for rendering.

**3. Coroutines support**

`viewModelScope` automatically cancels coroutines in `onCleared()`.

**4. Testability**

`ViewModel` is easy to test without Android framework dependencies.

### SavedStateHandle for Process Death

A `ViewModel` does NOT survive process death. To restore essential state, use **SavedStateHandle**, which is integrated with the SavedStateRegistry / `onSaveInstanceState()` mechanism: on process recreation, previously saved values are restored and provided to the new `ViewModel` instance.

```kotlin
class SavedStateViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ✅ values can be restored after rotation and process death,
    // if they were previously saved into SavedStateHandle
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

`ViewModel` is an architecture component for lifecycle-aware management of UI data. It survives configuration changes within the same process and scope, isolates UI-related logic from the UI layer, and integrates well with coroutines and DI. For recovering state after process death, use state saving mechanisms such as `SavedStateHandle`.

---

## Follow-ups (RU)

1. В чем разница между `ViewModel` и `onSaveInstanceState()`?
2. Как `SavedStateHandle` помогает восстанавливать данные после уничтожения процесса, если `ViewModel` этого не делает?
3. Когда следует использовать `activityViewModels()` вместо `viewModels()`?
4. Что произойдет, если `ViewModel` будет хранить ссылку на `Activity`?
5. Как тестировать `ViewModel`, использующий корутины во `viewModelScope`?

## Follow-ups (EN)

1. What's the difference between `ViewModel` and `onSaveInstanceState()`?
2. How does `SavedStateHandle` help restore data after process death while `ViewModel` doesn't?
3. When should you use `activityViewModels()` vs `viewModels()`?
4. What happens if a `ViewModel` holds a reference to an `Activity`?
5. How do you test a `ViewModel` that uses coroutines in `viewModelScope`?

## References

- ["ViewModel" Overview - Android Developers](https://developer.android.com/topic/libraries/architecture/viewmodel)
- ["ViewModel" API Reference](https://developer.android.com/reference/androidx/lifecycle/ViewModel)
- [ViewModels: A Simple Example - Medium](https://medium.com/androiddevelopers/viewmodels-a-simple-example-ed5ac416317e)
- [[q-mvvm-pattern--android--medium]]
- [[q-factory-pattern-android--android--medium]]

## Related Questions

### Prerequisites / Concepts

- [[c-lifecycle]]
- [[c-mvvm]]

### Prerequisites (Easier)

- [[q-mvvm-pattern--android--medium]] - MVVM pattern overview

### Related (Same Level)

- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation comparison

### Advanced (Harder)

- [[q-clean-architecture-android--android--hard]] - Clean Architecture with `ViewModel`
- [[q-mvi-architecture--android--hard]] - MVI vs MVVM
