---
id: android-389
title: ViewModel vs OnSavedInstanceState
aliases: [ViewModel fefdfb OnSavedInstanceState, ViewModel vs 
      OnSavedInstanceState]
topic: android
subtopics:
  - architecture-mvvm
  - lifecycle
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-activity-lifecycle
  - q-activity-lifecycle-methods--android--medium
  - q-testing-viewmodels-turbine--android--medium
  - q-what-is-viewmodel--android--medium
  - q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium
created: 2024-10-15
updated: 2025-11-11
tags: [android/architecture-mvvm, android/lifecycle, difficulty/medium, 
      state-management, viewmodel]

date created: Saturday, November 1st 2025, 12:47:06 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
anki_synced: true
anki_slugs:
  - 40-android-q-viewmodel-vs-onsavedinstancestate-android-medium-p01-en
  - 40-android-q-viewmodel-vs-onsavedinstancestate-android-medium-p01-ru
anki_last_sync: '2025-11-26T22:32:40.783101'
---
# Вопрос (RU)
> `ViewModel` vs `onSaveInstanceState`: когда что использовать для сохранения состояния в `Activity`/`Fragment`?

---

# Question (EN)
> `ViewModel` vs `onSaveInstanceState`: when to use each for preserving state in `Activity`/`Fragment`?

---

## Ответ (RU)
`ViewModel` и `onSaveInstanceState` оба помогают сохранять состояние при изменениях жизненного цикла `Activity`/`Fragment`, но решают разные задачи и имеют разные гарантии сохранения.

### Ключевые Отличия

| Аспект | `ViewModel` | `onSaveInstanceState` |
|--------|-------------|------------------------|
| Что переживает | Изменения конфигурации | Изменения конфигурации + пересоздание после убийства процесса (если система передала `Bundle`) |
| Размер данных | Крупные/сложные объекты (в пределах памяти процесса) | Только небольшой объем данных (примитивы/`Parcelable`), риск `TransactionTooLargeException` |
| Хранение | В памяти (на время жизни владельца) | В `Bundle` (сериализация) |
| Производительность | Быстро: ссылки на объекты, без сериализации | Медленнее: нужна (де)сериализация/IPC |
| Время жизни | Привязан к `LifecycleOwner`; переживает конфигурационные изменения, очищается при окончательном уничтожении владельца | Данные доступны только при следующем создании, если система вызвала `onSaveInstanceState` и передала `Bundle` |
| Типы данных | Любые объекты | Примитивы, `Parcelable`, `Serializable` и т.п. |
| Назначение | UI-состояние и логика между конфигурационными изменениями | Минимальное критичное UI-состояние для восстановления после пересоздания, включая смерть процесса |
| Потоки | Можно держать фоновые операции (`coroutines`, `Flow` и др.) | Только снимок состояния; не для долгих операций |

### `ViewModel` — Выживание При Изменениях Конфигурации

```kotlin
class UserViewModel : ViewModel() {

    // Хранит большие наборы данных в памяти (в рамках процесса)
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    // Бизнес-логика
    private val repository = UserRepository()

    // Текущая фоновая операция
    private var currentJob: Job? = null

    init {
        loadUsers()
    }

    fun loadUsers() {
        currentJob = viewModelScope.launch {
            val result = repository.getUsers()
            _users.value = result
        }
    }

    fun filterUsers(query: String): List<User> {
        // Пример фильтрации
        return users.value?.filter {
            it.name.contains(query, ignoreCase = true)
        } ?: emptyList()
    }

    override fun onCleared() {
        super.onCleared()
        // Освобождаем ресурсы, когда владелец окончательно уничтожается
        currentJob?.cancel()
    }
}

class MainActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.users.observe(this) { users ->
            // Список пользователей сохраняется при повороте экрана
            updateUI(users)
        }
    }

    // При повороте экрана создается та же самая инстанция ViewModel
}
```

Когда `ViewModel` очищается:

```kotlin
// ViewModel обычно переживает:
// - Поворот экрана
// - Смена языка/темы
// - Другие конфигурационные изменения

// ViewModel очищается, когда:
// - Вызван finish() для Activity
// - Пользователь ушел «назад» и Activity/Fragment завершен
// - Fragment удален без последующего повторного добавления
// - Процесс приложения убит (вся память теряется)
// - Приложение принудительно остановлено
```

### `onSaveInstanceState` — Выживание После Убийства Процесса

```kotlin
class MainActivity : AppCompatActivity() {

    private var scrollPosition: Int = 0
    private var searchQuery: String = ""
    private var isFilterExpanded: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Восстановление из сохраненного состояния (при конфигурационных
        // изменениях или пересоздании после убийства процесса)
        savedInstanceState?.let {
            scrollPosition = it.getInt(KEY_SCROLL_POSITION, 0)
            searchQuery = it.getString(KEY_SEARCH_QUERY, "") ?: ""
            isFilterExpanded = it.getBoolean(KEY_FILTER_EXPANDED, false)
        }

        recyclerView.scrollToPosition(scrollPosition)
        searchEditText.setText(searchQuery)
        filterPanel.isVisible = isFilterExpanded
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Сохраняем только легковесное критичное состояние UI
        outState.putInt(KEY_SCROLL_POSITION, getCurrentScrollPosition())
        outState.putString(KEY_SEARCH_QUERY, searchEditText.text.toString())
        outState.putBoolean(KEY_FILTER_EXPANDED, filterPanel.isVisible)
    }

    companion object {
        private const val KEY_SCROLL_POSITION = "scroll_position"
        private const val KEY_SEARCH_QUERY = "search_query"
        private const val KEY_FILTER_EXPANDED = "filter_expanded"
    }
}
```

Когда `onSaveInstanceState` обычно вызывается и ограничения:

```kotlin
// Система может вызвать onSaveInstanceState:
// - Перед изменением конфигурации
// - Когда Activity уходит в фон и может быть пересоздана позже
//
// Не гарантируется вызов:
// - Если процесс убит «жестко» без уведомления
// - Для некоторых путей уничтожения
// - При обычном завершении через кнопку Назад или finish(),
//   когда Activity удаляется навсегда
```

### Комбинирование Обоих Подходов (рекомендуется)

```kotlin
// ViewModel с SavedStateHandle
class UserViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: UserRepository
) : ViewModel() {

    // Тяжелые данные — только в памяти (ViewModel)
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    // Критичное состояние UI — через SavedStateHandle (переживает смерть процесса)
    var searchQuery: String
        get() = savedStateHandle.get<String>(KEY_SEARCH_QUERY) ?: ""
        set(value) { savedStateHandle[KEY_SEARCH_QUERY] = value }

    var selectedUserId: Int
        get() = savedStateHandle.get<Int>(KEY_SELECTED_USER_ID) ?: -1
        set(value) { savedStateHandle[KEY_SELECTED_USER_ID] = value }

    // Пример LiveData из SavedStateHandle
    val scrollPosition: MutableLiveData<Int> =
        savedStateHandle.getLiveData(KEY_SCROLL_POSITION, 0)

    init {
        if (_users.value == null) {
            loadUsers()
        }
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }

    companion object {
        private const val KEY_SEARCH_QUERY = "search_query"
        private const val KEY_SELECTED_USER_ID = "selected_user_id"
        private const val KEY_SCROLL_POSITION = "scroll_position"
    }
}

class MainActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Данные — из ViewModel (переживают конфигурационные изменения)
        viewModel.users.observe(this) { users ->
            adapter.submitList(users)
        }

        // Поисковый запрос — из SavedStateHandle (можно восстановить после смерти процесса)
        searchEditText.setText(viewModel.searchQuery)

        // Позиция списка — из SavedStateHandle
        viewModel.scrollPosition.observe(this) { position ->
            recyclerView.scrollToPosition(position)
        }
    }
}
```

### Ограничения По Размеру Данных

```kotlin
// ПЛОХО: сохранять большие данные в onSaveInstanceState
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // Риск TransactionTooLargeException и проблем с производительностью
    outState.putParcelableArrayList("users", ArrayList(largeUserList))
    outState.putByteArray("image", largeBitmap.toByteArray())
}

// ХОРОШО: хранить большие данные во ViewModel
class MyViewModel : ViewModel() {
    val users = MutableLiveData<List<User>>()
    val bitmap = MutableLiveData<Bitmap>()
}

// ХОРОШО: в Bundle сохранять только идентификаторы/ключи
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("user_id", currentUserId)
    outState.putString("image_path", imageCachePath)
}
```

### Полный Пример: Лучшие Практики

```kotlin
// ViewModel с SavedStateHandle
class ProductViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: ProductRepository
) : ViewModel() {

    // Большие данные — во ViewModel
    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    // Критичное UI-состояние — в SavedStateHandle
    var selectedProductId: String?
        get() = savedStateHandle[KEY_SELECTED_PRODUCT_ID]
        set(value) { savedStateHandle[KEY_SELECTED_PRODUCT_ID] = value }

    var sortOrder: SortOrder
        get() = savedStateHandle.get<SortOrder>(KEY_SORT_ORDER) ?: SortOrder.NAME
        set(value) { savedStateHandle[KEY_SORT_ORDER] = value }

    val selectedProduct: LiveData<Product?> =
        savedStateHandle.getLiveData<String?>(KEY_SELECTED_PRODUCT_ID)
            .switchMap { id ->
                liveData {
                    emit(id?.let { repository.getProduct(it) })
                }
            }

    init {
        loadProducts()
    }

    fun loadProducts() {
        viewModelScope.launch {
            _products.value = repository.getProducts()
        }
    }

    companion object {
        private const val KEY_SELECTED_PRODUCT_ID = "selected_product_id"
        private const val KEY_SORT_ORDER = "sort_order"
    }
}

class ProductActivity : AppCompatActivity() {

    private val viewModel: ProductViewModel by viewModels()

    // Временное UI-состояние
    private var isLoading: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        savedInstanceState?.let {
            isLoading = it.getBoolean(KEY_IS_LOADING, false)
        }

        viewModel.products.observe(this) { products ->
            updateProductList(products)
        }

        viewModel.selectedProduct.observe(this) { product ->
            product?.let { showProductDetails(it) }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Сохраняем только легковесное временное состояние
        outState.putBoolean(KEY_IS_LOADING, isLoading)
    }

    companion object {
        private const val KEY_IS_LOADING = "is_loading"
    }
}
```

### Матрица Выбора

```
Выбирайте ViewModel, когда:
- Нужны большие/сложные данные (в пределах памяти процесса)
- Требуется хранить репозитории/UseCase и выполнять фоновые операции
- Нужна сложная бизнес-логика
- Нужно шарить состояние между фрагментами в одной Activity
- Достаточно пережить только конфигурационные изменения

Выбирайте onSaveInstanceState, когда:
- Нужно сохранить минимальное критичное UI-состояние
- Данные малы и сериализуемы
- Состояние должно быть восстановимо после смерти процесса (если пришел `Bundle`)
- Нужно сохранить пользовательский ввод, еще не записанный в персистентное хранилище
- Достаточно простых флагов/значений

Используйте SavedStateHandle, когда:
- Нужен гибрид ViewModel + восстановление после смерти процесса
- Нужен структурированный, lifecycle-aware стор для состояния
- Строите production-навигацию и сложные сценарии восстановления
```

### Распространенные Паттерны

```kotlin
// Паттерн 1: форма, ввод должен пережить поворот и пересоздание
class FormViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val userName: MutableLiveData<String> = savedStateHandle.getLiveData("user_name")
    val userEmail: MutableLiveData<String> = savedStateHandle.getLiveData("user_email")
}

// Паттерн 2: большой список + выбранный элемент
class ListViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val items: MutableLiveData<List<Item>> = MutableLiveData()
    var selectedItemId: Int?
        get() = savedStateHandle.get("selected_item_id")
        set(value) { savedStateHandle["selected_item_id"] = value }
}

// Паттерн 3: позиция скролла
class FeedViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val feedItems: MutableLiveData<List<Post>> = MutableLiveData()
    val scrollPosition: MutableLiveData<Int> = savedStateHandle.getLiveData("scroll_pos", 0)
}
```

### Итог

- Используйте `ViewModel` для:
  - крупных и сложных данных,
  - бизнес-логики и асинхронной работы,
  - переживания конфигурационных изменений.
- Используйте `onSaveInstanceState` для:
  - небольшого, сериализуемого критичного UI-состояния,
  - восстановления после смерти процесса.
- Лучший практический подход: комбинировать `ViewModel` c `SavedStateHandle`, получая быстрый in-memory стейт + восстановление ключевых данных после пересоздания.

---

## Answer (EN)
`ViewModel` and `onSaveInstanceState` are both mechanisms for preserving data across `Activity`/`Fragment` lifecycle events, but they serve different purposes and have different survival guarantees.

### Key Differences

| Aspect | `ViewModel` | `onSaveInstanceState` |
|--------|-----------|---------------------|
| **Survives** | Configuration changes | Configuration changes + recreation after process death (when system provides `Bundle`) |
| **Data size** | Large/complex objects (bounded by app memory) | Small primitives/Parcelables (practically limited, risk of `TransactionTooLargeException`) |
| **Storage** | In-memory (per scope owner) | Serialized to `Bundle` |
| **Performance** | Fast (object references, no serialization) | Slower (serialization/IPC) |
| **Lifetime** | Tied to `LifecycleOwner` scope; survives config changes, cleared when `Activity`/`Fragment` is finished | State is available only on next recreation if system called `onSaveInstanceState` and passed the `Bundle` |
| **Data types** | Any objects | `Parcelable`, `Serializable`, primitives, etc. |
| **Purpose** | UI-related state + business logic between config changes | Minimal critical UI state needed to restore UI after recreation, including process death |
| **Threading** | Can manage/background operations (e.g., coroutines, `Flow`) | Synchronous snapshot only; no long-running work |

### `ViewModel` - Configuration Change Survival

```kotlin
class UserViewModel : ViewModel() {

    // Holds large datasets efficiently (within process memory limits)
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    // Complex business logic
    private val repository = UserRepository()

    // Ongoing operations
    private var currentJob: Job? = null

    init {
        loadUsers()
    }

    fun loadUsers() {
        currentJob = viewModelScope.launch {
            val result = repository.getUsers()
            _users.value = result
        }
    }

    fun filterUsers(query: String): List<User> {
        // Complex filtering logic
        return users.value?.filter {
            it.name.contains(query, ignoreCase = true)
        } ?: emptyList()
    }

    override fun onCleared() {
        super.onCleared()
        // Cleanup when the associated Activity/Fragment is finishing
        currentJob?.cancel()
    }
}

class MainActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.users.observe(this) { users ->
            // Users list survives rotation
            updateUI(users)
        }
    }

    // Rotate device → onCreate called again
    // viewModel is THE SAME INSTANCE for this Activity until it is finished
    // Data preserved automatically across configuration changes
}
```

When `ViewModel` is cleared:

```kotlin
// ViewModel typically survives:
// - Screen rotation
// - Language change
// - Dark mode toggle
// - Other configuration changes

// ViewModel is cleared when its owner scope is destroyed for good, e.g.:
// - finish() called
// - User presses back causing Activity/Fragment to finish
// - Fragment removed from FragmentManager without being reattached
// - Process is killed (all in-memory state is lost)
// - User force-stops app
```

### `onSaveInstanceState` - Process Death Survival

```kotlin
class MainActivity : AppCompatActivity() {

    private var scrollPosition: Int = 0
    private var searchQuery: String = ""
    private var isFilterExpanded: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Restore from previously saved instance state (e.g., after process death
        // or configuration change where the system supplied the Bundle)
        savedInstanceState?.let {
            scrollPosition = it.getInt(KEY_SCROLL_POSITION, 0)
            searchQuery = it.getString(KEY_SEARCH_QUERY, "") ?: ""
            isFilterExpanded = it.getBoolean(KEY_FILTER_EXPANDED, false)
        }

        recyclerView.scrollToPosition(scrollPosition)
        searchEditText.setText(searchQuery)
        filterPanel.isVisible = isFilterExpanded
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Save critical UI state only (must be small and serializable)
        outState.putInt(KEY_SCROLL_POSITION, getCurrentScrollPosition())
        outState.putString(KEY_SEARCH_QUERY, searchEditText.text.toString())
        outState.putBoolean(KEY_FILTER_EXPANDED, filterPanel.isVisible)
    }

    companion object {
        private const val KEY_SCROLL_POSITION = "scroll_position"
        private const val KEY_SEARCH_QUERY = "search_query"
        private const val KEY_FILTER_EXPANDED = "filter_expanded"
    }
}
```

When `onSaveInstanceState` is (typically) called:

```kotlin
// Common cases when system may call onSaveInstanceState:
// - Before a configuration change (rotation, etc.)
// - When Activity is backgrounded and the system may later recreate it
//
// Important caveats:
// - It is NOT guaranteed for all lifecycle paths; the system can kill the
//   process without calling onSaveInstanceState.
// - It is usually NOT called when:
//   - User presses back and Activity is finishing normally
//   - finish() is called explicitly to permanently destroy Activity
```

### Combining Both Approaches (Recommended)

```kotlin
// ViewModel with SavedStateHandle
class UserViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: UserRepository
) : ViewModel() {

    // Heavy data - in memory only (ViewModel)
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    // Critical UI state - survives process death (SavedStateHandle)
    var searchQuery: String
        get() = savedStateHandle.get<String>(KEY_SEARCH_QUERY) ?: ""
        set(value) { savedStateHandle[KEY_SEARCH_QUERY] = value }

    var selectedUserId: Int
        get() = savedStateHandle.get<Int>(KEY_SELECTED_USER_ID) ?: -1
        set(value) { savedStateHandle[KEY_SELECTED_USER_ID] = value }

    // LiveData backed by SavedStateHandle
    val scrollPosition: MutableLiveData<Int> =
        savedStateHandle.getLiveData(KEY_SCROLL_POSITION, 0)

    init {
        // Load data only if not already loaded
        if (_users.value == null) {
            loadUsers()
        }
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }

    companion object {
        private const val KEY_SEARCH_QUERY = "search_query"
        private const val KEY_SELECTED_USER_ID = "selected_user_id"
        private const val KEY_SCROLL_POSITION = "scroll_position"
    }
}

class MainActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Users list - from ViewModel (survives config changes)
        viewModel.users.observe(this) { users ->
            adapter.submitList(users)
        }

        // Search query - from SavedStateHandle (survives process death when restored)
        searchEditText.setText(viewModel.searchQuery)

        // Scroll position - from SavedStateHandle LiveData
        viewModel.scrollPosition.observe(this) { position ->
            recyclerView.scrollToPosition(position)
        }
    }
}
```

### Data Size Limitations

```kotlin
// - BAD: Large data in onSaveInstanceState
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // This can cause TransactionTooLargeException or performance issues
    outState.putParcelableArrayList("users", ArrayList(largeUserList)) // thousands of items
    outState.putByteArray("image", largeBitmap.toByteArray()) // several MB
}

// - GOOD: Use ViewModel for large data (still within reasonable memory limits)
class MyViewModel : ViewModel() {
    val users = MutableLiveData<List<User>>()
    val bitmap = MutableLiveData<Bitmap>()
}

// - GOOD: Only save references/keys in Bundle
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("user_id", currentUserId) // Just the ID
    outState.putString("image_path", imageCachePath) // Just the path
}
```

### Complete Example: Best Practices

```kotlin
// ViewModel with SavedStateHandle
class ProductViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: ProductRepository
) : ViewModel() {

    // Large data - ViewModel only
    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    // Critical UI state - SavedStateHandle (survives process death when restored)
    var selectedProductId: String?
        get() = savedStateHandle[KEY_SELECTED_PRODUCT_ID]
        set(value) { savedStateHandle[KEY_SELECTED_PRODUCT_ID] = value }

    var sortOrder: SortOrder
        get() = savedStateHandle.get<SortOrder>(KEY_SORT_ORDER) ?: SortOrder.NAME
        set(value) { savedStateHandle[KEY_SORT_ORDER] = value }

    // Derived state with transformation
    val selectedProduct: LiveData<Product?> =
        savedStateHandle.getLiveData<String?>(KEY_SELECTED_PRODUCT_ID)
            .switchMap { id ->
                liveData {
                    emit(id?.let { repository.getProduct(it) })
                }
            }

    init {
        loadProducts()
    }

    fun loadProducts() {
        viewModelScope.launch {
            _products.value = repository.getProducts()
        }
    }

    companion object {
        private const val KEY_SELECTED_PRODUCT_ID = "selected_product_id"
        private const val KEY_SORT_ORDER = "sort_order"
    }
}

// Activity
class ProductActivity : AppCompatActivity() {

    private val viewModel: ProductViewModel by viewModels()

    // Temporary UI state not needing SavedStateHandle
    private var isLoading: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Restore temporary UI state if provided
        savedInstanceState?.let {
            isLoading = it.getBoolean(KEY_IS_LOADING, false)
        }

        // Observe ViewModel data
        viewModel.products.observe(this) { products ->
            updateProductList(products)
        }

        viewModel.selectedProduct.observe(this) { product ->
            product?.let { showProductDetails(it) }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Save only lightweight, temporary UI state
        // Important state already kept in ViewModel / SavedStateHandle
        outState.putBoolean(KEY_IS_LOADING, isLoading)
    }

    companion object {
        private const val KEY_IS_LOADING = "is_loading"
    }
}
```

### Decision Matrix

```
Choose ViewModel when:
- Storing larger/complex datasets (within process memory limits)
- Holding references to repositories or use cases
- Running background operations
- Implementing complex business logic
- Sharing data across fragments in the same Activity
- You only need to survive configuration changes

Choose onSaveInstanceState when:
- Storing minimal critical UI state (e.g., scroll position, text input)
- Values are small and easily serializable
- State must be restorable after process death (if Bundle is provided)
- Preserving user-entered data not yet persisted
- Representing simple selection/visibility flags

Use SavedStateHandle when:
- You need ViewModel + restorable state after process death
- You want a structured, lifecycle-aware state store
- You are building production-ready navigation/state flows
```

### Common Patterns

```kotlin
// Pattern 1: User input that must survive configuration changes and process recreation
class FormViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val userName: MutableLiveData<String> = savedStateHandle.getLiveData("user_name")
    val userEmail: MutableLiveData<String> = savedStateHandle.getLiveData("user_email")
}

// Pattern 2: Large list with selected item
class ListViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val items: MutableLiveData<List<Item>> = MutableLiveData() // ViewModel only for list
    var selectedItemId: Int?
        get() = savedStateHandle.get<Int>("selected_item_id")
        set(value) { savedStateHandle["selected_item_id"] = value }
}

// Pattern 3: Scroll position
class FeedViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val feedItems: MutableLiveData<List<Post>> = MutableLiveData()
    val scrollPosition: MutableLiveData<Int> = savedStateHandle.getLiveData("scroll_pos", 0)
}
```

### Summary

Use `ViewModel` for:
- Large/complex data objects (within memory limits)
- Business logic and asynchronous work
- Surviving configuration changes

Use `onSaveInstanceState` for:
- Small, serializable UI state
- Making key UI state restorable after process death
- Critical user input not yet persisted

Best Practice: Combine `ViewModel` with `SavedStateHandle` to get both convenient in-memory state management and the ability to restore critical state after process death.

---

## Follow-ups

- How would you design state handling for a complex multi-step form that must survive both configuration changes and process death?
- When would you additionally persist state to a database or `DataStore` instead of relying only on `ViewModel`/`onSaveInstanceState`?
- How does this choice change when using `Navigation Component` and `SavedStateHandle` with back stack entries?

## References

- [[c-activity-lifecycle]]
- Official Android docs on lifecycle and saved state (developer.android.com)

## Related Questions

- [[q-activity-lifecycle-methods--android--medium]]
