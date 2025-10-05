---
tags:
  - android
difficulty: medium
---

# ViewModel vs OnSavedInstanceState

## Answer

ViewModel and onSaveInstanceState are both mechanisms for preserving data across Activity/Fragment lifecycle events, but they serve different purposes and have different survival guarantees.

### Key Differences

| Aspect | ViewModel | onSaveInstanceState |
|--------|-----------|---------------------|
| **Survives** | Configuration changes | Configuration changes + Process death |
| **Data size** | Large objects, complex data | Small primitives, limited size (~1MB) |
| **Storage** | In-memory | Serialized to Bundle |
| **Performance** | Fast (references) | Slower (serialization) |
| **Lifetime** | Until Activity finishes | Until user explicitly closes |
| **Data types** | Any objects | Parcelable, Serializable, primitives |
| **Purpose** | UI state and business logic | Critical UI state only |
| **Threading** | Can hold background operations | Synchronous only |

### ViewModel - Configuration Change Survival

```kotlin
class UserViewModel : ViewModel() {

    // Holds large datasets efficiently
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
        // Cleanup when Activity finishes
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
    // viewModel is THE SAME INSTANCE
    // Data preserved automatically
}
```

**When ViewModel is cleared**:
```kotlin
// ViewModel survives:
// ✅ Screen rotation
// ✅ Language change
// ✅ Dark mode toggle
// ✅ Activity in background

// ViewModel is lost:
// ❌ finish() called
// ❌ Back button pressed (last activity)
// ❌ Process death
// ❌ User force-stops app
```

### onSaveInstanceState - Process Death Survival

```kotlin
class MainActivity : AppCompatActivity() {

    private var scrollPosition: Int = 0
    private var searchQuery: String = ""
    private var isFilterExpanded: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Restore from process death
        savedInstanceState?.let {
            scrollPosition = it.getInt(KEY_SCROLL_POSITION, 0)
            searchQuery = it.getString(KEY_SEARCH_QUERY, "")
            isFilterExpanded = it.getBoolean(KEY_FILTER_EXPANDED, false)
        }

        recyclerView.scrollToPosition(scrollPosition)
        searchEditText.setText(searchQuery)
        filterPanel.isVisible = isFilterExpanded
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Save critical UI state only
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

**When onSaveInstanceState is called**:
```kotlin
// Called when:
// ✅ Configuration change (rotation, etc.)
// ✅ Activity going to background
// ✅ Before process death
// ✅ System needs to reclaim memory

// NOT called when:
// ❌ User presses back (Activity finishing)
// ❌ finish() called explicitly
```

### Combining Both Approaches (Recommended)

```kotlin
// ViewModel with SavedStateHandle
class UserViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Heavy data - in memory only (ViewModel)
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    // Critical UI state - survives process death (SavedStateHandle)
    var searchQuery: String
        get() = savedStateHandle.get<String>(KEY_SEARCH_QUERY) ?: ""
        set(value) { savedStateHandle.set(KEY_SEARCH_QUERY, value) }

    var selectedUserId: Int
        get() = savedStateHandle.get<Int>(KEY_SELECTED_USER_ID) ?: -1
        set(value) { savedStateHandle.set(KEY_SELECTED_USER_ID, value) }

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

        // Users list - from ViewModel (config changes only)
        viewModel.users.observe(this) { users ->
            adapter.submitList(users)
        }

        // Search query - from SavedStateHandle (survives process death)
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
// ❌ BAD: Large data in onSaveInstanceState
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // This can crash with TransactionTooLargeException!
    outState.putParcelableArrayList("users", ArrayList(largeUserList)) // 1000+ items
    outState.putByteArray("image", largeBitmap.toByteArray()) // Several MB
}

// ✅ GOOD: Use ViewModel for large data
class MyViewModel : ViewModel() {
    val users = MutableLiveData<List<User>>() // Any size
    val bitmap = MutableLiveData<Bitmap>() // Any size
}

// ✅ GOOD: Only save reference in Bundle
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

    // Critical UI state - SavedStateHandle (survives process death)
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

        // Restore temporary UI state
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

        // Save only temporary UI state
        // Important state already in SavedStateHandle
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
✅ Storing large datasets
✅ Holding references to repositories
✅ Running background operations
✅ Complex business logic
✅ Data shared across fragments
✅ Only need to survive config changes

Choose onSaveInstanceState when:
✅ Critical UI state (scroll position, text input)
✅ Small primitive values
✅ Must survive process death
✅ User-entered data not yet saved
✅ Temporary selection state

Use SavedStateHandle when:
✅ Need both ViewModel AND process death survival
✅ Want type-safe state management
✅ Building production apps (recommended)
```

### Common Patterns

```kotlin
// Pattern 1: User input that must survive everything
class FormViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val userName: MutableLiveData<String> = savedStateHandle.getLiveData("user_name")
    val userEmail: MutableLiveData<String> = savedStateHandle.getLiveData("user_email")
}

// Pattern 2: Large list with selected item
class ListViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val items: MutableLiveData<List<Item>> = MutableLiveData() // ViewModel only
    var selectedItemId: Int? by savedStateHandle.delegate() // Survives process death
}

// Pattern 3: Scroll position
class FeedViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    val feedItems: MutableLiveData<List<Post>> = MutableLiveData()
    val scrollPosition: MutableLiveData<Int> = savedStateHandle.getLiveData("scroll_pos", 0)
}
```

### Summary

**Use ViewModel for**:
- Large data objects
- Business logic
- Configuration change survival

**Use onSaveInstanceState for**:
- Small UI state
- Process death survival
- Critical user input

**Best Practice**: Combine ViewModel with SavedStateHandle for robust state management that handles both configuration changes and process death.

## Answer (RU)
ViewModel и onSaveInstanceState служат для сохранения данных при изменении конфигурации активности или фрагмента. ViewModel используется для хранения и управления данными, связанных с UI, которые сохраняются при изменении конфигурации. onSaveInstanceState() используется для сохранения данных в Bundle, который система автоматически передаёт при пересоздании Activity или Fragment. ViewModel хранит данные в памяти до полного уничтожения Activity или Fragment и удобен для сложных объектов. onSaveInstanceState сохраняет данные даже при завершении процесса и подходит для небольших данных.

## Related Topics
- SavedStateHandle
- Configuration changes
- Process death
- Bundle size limitations
- State management patterns
