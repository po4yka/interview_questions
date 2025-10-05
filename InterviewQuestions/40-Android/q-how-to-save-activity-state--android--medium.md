---
id: 202510031417012
title: "How to save ViewModel state in architecture components"
question_ru: "Как в архитектурных компонентах андроид сохранить состояние view модели"
question_en: "How to save Activity state"
topic: android
moc: moc-android
status: draft
difficulty: medium
tags:
  - ViewModel
  - SavedStateHandle
  - android/viewmodel
  - lifecycle
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/281
---

# How to save ViewModel state in architecture components

## English Answer

In Android architecture components, to save the state of a ViewModel, a special class called **SavedStateHandle** is used. This class allows you to save and restore ViewModel state during configuration changes or when an Activity or Fragment is recreated.

### What is SavedStateHandle?

SavedStateHandle is a key-value map that allows ViewModel to save and restore its state, surviving both configuration changes (like screen rotation) and **process death** (when the system kills the app process to free memory).

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // SavedStateHandle survives:
    // 1. Configuration changes (rotation)
    // 2. Process death (system kills app)

    // Regular LiveData - survives config changes only
    private val _tempData = MutableLiveData<String>()
    val tempData: LiveData<String> = _tempData

    // SavedStateHandle LiveData - survives process death too
    val persistentData: MutableLiveData<String> =
        savedStateHandle.getLiveData("key_persistent_data")
}
```

### Basic Usage

#### 1. Add Dependencies

```gradle
dependencies {
    implementation "androidx.lifecycle:lifecycle-viewmodel-savedstate:2.6.2"
    implementation "androidx.activity:activity-ktx:1.8.0"
    implementation "androidx.fragment:fragment-ktx:1.6.1"
}
```

#### 2. Create ViewModel with SavedStateHandle

```kotlin
class UserViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Save and retrieve primitive types
    var userId: String?
        get() = savedStateHandle["user_id"]
        set(value) { savedStateHandle["user_id"] = value }

    var age: Int
        get() = savedStateHandle["age"] ?: 0
        set(value) { savedStateHandle["age"] = value }

    // Save and retrieve using LiveData
    val userName: MutableLiveData<String> = savedStateHandle.getLiveData("user_name")

    // Save complex objects (must be Parcelable)
    var user: User?
        get() = savedStateHandle["user_object"]
        set(value) { savedStateHandle["user_object"] = value }

    fun updateUserName(name: String) {
        userName.value = name
        // Automatically saved to savedStateHandle
    }
}

@Parcelize
data class User(
    val id: String,
    val name: String,
    val email: String
) : Parcelable
```

#### 3. Use in Activity

```kotlin
class MainActivity : AppCompatActivity() {

    // ViewModel automatically receives SavedStateHandle
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Observe LiveData from SavedStateHandle
        viewModel.userName.observe(this) { name ->
            textView.text = name
        }

        // Set value
        button.setOnClickListener {
            viewModel.updateUserName("John Doe")
        }

        // Access saved values
        Log.d("MainActivity", "UserId: ${viewModel.userId}")
    }
}
```

#### 4. Use in Fragment

```kotlin
class UserFragment : Fragment() {

    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ViewModel with SavedStateHandle works same as in Activity
        viewModel.userName.observe(viewLifecycleOwner) { name ->
            binding.nameTextView.text = name
        }
    }
}
```

### Different Ways to Save Data

#### 1. Direct Key-Value Storage

```kotlin
class CounterViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val COUNTER_KEY = "counter"

    var counter: Int
        get() = savedStateHandle[COUNTER_KEY] ?: 0
        set(value) {
            savedStateHandle[COUNTER_KEY] = value
        }

    fun increment() {
        counter++
    }

    fun decrement() {
        counter--
    }
}
```

#### 2. LiveData from SavedStateHandle

```kotlin
class SearchViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // LiveData that automatically saves to savedStateHandle
    val searchQuery: MutableLiveData<String> =
        savedStateHandle.getLiveData("search_query", "")  // default value

    val searchResults: LiveData<List<String>> = searchQuery.switchMap { query ->
        liveData {
            emit(performSearch(query))
        }
    }

    private suspend fun performSearch(query: String): List<String> {
        // Search implementation
        return emptyList()
    }
}
```

#### 3. StateFlow from SavedStateHandle

```kotlin
class ModernViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Convert SavedStateHandle LiveData to StateFlow
    val userName: StateFlow<String> = savedStateHandle
        .getLiveData<String>("user_name", "")
        .asFlow()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = ""
        )

    fun updateUserName(name: String) {
        savedStateHandle["user_name"] = name
    }
}
```

### Complete Example: Form State Preservation

```kotlin
@Parcelize
data class FormState(
    val name: String = "",
    val email: String = "",
    val age: Int = 0,
    val acceptedTerms: Boolean = false
) : Parcelable

class RegistrationViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    companion object {
        private const val FORM_STATE_KEY = "form_state"
    }

    // Restore form state if available
    private val _formState = MutableLiveData<FormState>(
        savedStateHandle[FORM_STATE_KEY] ?: FormState()
    )
    val formState: LiveData<FormState> = _formState

    fun updateName(name: String) {
        val updatedState = _formState.value?.copy(name = name) ?: FormState(name = name)
        saveFormState(updatedState)
    }

    fun updateEmail(email: String) {
        val updatedState = _formState.value?.copy(email = email) ?: FormState(email = email)
        saveFormState(updatedState)
    }

    fun updateAge(age: Int) {
        val updatedState = _formState.value?.copy(age = age) ?: FormState(age = age)
        saveFormState(updatedState)
    }

    fun toggleTerms(accepted: Boolean) {
        val updatedState = _formState.value?.copy(acceptedTerms = accepted)
            ?: FormState(acceptedTerms = accepted)
        saveFormState(updatedState)
    }

    private fun saveFormState(state: FormState) {
        _formState.value = state
        savedStateHandle[FORM_STATE_KEY] = state
    }

    fun submitForm() {
        val state = _formState.value ?: return

        if (validateForm(state)) {
            viewModelScope.launch {
                // Submit form
                submitRegistration(state)
                clearForm()
            }
        }
    }

    private fun validateForm(state: FormState): Boolean {
        return state.name.isNotBlank() &&
                state.email.contains("@") &&
                state.age >= 18 &&
                state.acceptedTerms
    }

    private suspend fun submitRegistration(state: FormState) {
        // API call
    }

    private fun clearForm() {
        saveFormState(FormState())
    }
}

// Using in Activity
class RegistrationActivity : AppCompatActivity() {

    private val viewModel: RegistrationViewModel by viewModels()
    private lateinit var binding: ActivityRegistrationBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegistrationBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Restore form state
        viewModel.formState.observe(this) { state ->
            // Update UI without triggering observers
            binding.nameEditText.setText(state.name)
            binding.emailEditText.setText(state.email)
            binding.ageEditText.setText(state.age.toString())
            binding.termsCheckBox.isChecked = state.acceptedTerms
        }

        // Listen to user input
        binding.nameEditText.addTextChangedListener {
            viewModel.updateName(it.toString())
        }

        binding.emailEditText.addTextChangedListener {
            viewModel.updateEmail(it.toString())
        }

        binding.ageEditText.addTextChangedListener {
            it.toString().toIntOrNull()?.let { age ->
                viewModel.updateAge(age)
            }
        }

        binding.termsCheckBox.setOnCheckedChangeListener { _, isChecked ->
            viewModel.toggleTerms(isChecked)
        }

        binding.submitButton.setOnClickListener {
            viewModel.submitForm()
        }
    }
}
```

### Getting Initial Arguments

```kotlin
class ProductViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Get productId from Activity/Fragment arguments
    private val productId: String = savedStateHandle["product_id"]
        ?: throw IllegalStateException("Product ID is required")

    private val _product = MutableLiveData<Product>()
    val product: LiveData<Product> = _product

    init {
        loadProduct()
    }

    private fun loadProduct() {
        viewModelScope.launch {
            _product.value = repository.getProduct(productId)
        }
    }
}

// In Activity
class ProductActivity : AppCompatActivity() {

    private val viewModel: ProductViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ViewModel gets productId from intent automatically
        // if you pass it correctly
    }

    companion object {
        fun newIntent(context: Context, productId: String): Intent {
            return Intent(context, ProductActivity::class.java).apply {
                putExtra("product_id", productId)
            }
        }
    }
}
```

### Custom ViewModel Factory (if needed)

```kotlin
class UserViewModelFactory(
    private val userRepository: UserRepository,
    owner: SavedStateRegistryOwner,
    defaultArgs: Bundle? = null
) : AbstractSavedStateViewModelFactory(owner, defaultArgs) {

    override fun <T : ViewModel> create(
        key: String,
        modelClass: Class<T>,
        handle: SavedStateHandle
    ): T {
        if (modelClass.isAssignableFrom(UserViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return UserViewModel(userRepository, handle) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

class UserViewModel(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Implementation
}

// Usage
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels {
        UserViewModelFactory(
            (application as MyApp).userRepository,
            this
        )
    }
}
```

### What Can Be Saved in SavedStateHandle?

SavedStateHandle supports types that can be put in a Bundle:

- **Primitive types**: Int, Long, Float, Double, Boolean, String
- **Primitive arrays**: IntArray, LongArray, etc.
- **Parcelable objects**
- **Serializable objects** (not recommended)
- **ArrayList** of supported types

```kotlin
class ExampleViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // ✅ Supported types
    var intValue: Int
        get() = savedStateHandle["int"] ?: 0
        set(value) { savedStateHandle["int"] = value }

    var stringValue: String?
        get() = savedStateHandle["string"]
        set(value) { savedStateHandle["string"] = value }

    var parcelableUser: User?
        get() = savedStateHandle["user"]
        set(value) { savedStateHandle["user"] = value }

    var stringList: ArrayList<String>?
        get() = savedStateHandle["list"]
        set(value) { savedStateHandle["list"] = value }

    // ❌ NOT supported - custom objects must be Parcelable
    // var customObject: MyClass?
}
```

### Best Practices

1. **Use SavedStateHandle for UI state** that needs to survive process death
2. **Keep data small** - Bundle has size limitations (~500KB)
3. **Use Parcelable** instead of Serializable for better performance
4. **Don't save transient data** - only UI state
5. **Combine with Repository** - SavedStateHandle for UI state, Repository for data

## Russian Answer

В архитектурных компонентах Android для сохранения состояния ViewModel используется специальный класс **SavedStateHandle**. Этот класс позволяет сохранить и восстановить состояние ViewModel при изменении конфигурации или при пересоздании активности или фрагмента.

### Использование SavedStateHandle

Для использования SavedStateHandle в вашей ViewModel, убедитесь, что ваш ViewModel принимает его в конструкторе. Это можно сделать, используя фабрику ViewModel при создании ViewModel.

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Сохранение значения
    fun saveValue(key: String, value: String) {
        savedStateHandle[key] = value
    }

    // Восстановление значения
    fun getValue(key: String): String? {
        return savedStateHandle[key]
    }

    // Использование LiveData с автосохранением
    val userName: MutableLiveData<String> = savedStateHandle.getLiveData("user_name")
}
```

### В Activity

```kotlin
class MainActivity : AppCompatActivity() {

    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ViewModel автоматически получает SavedStateHandle
        viewModel.userName.observe(this) { name ->
            // Обновить UI
        }
    }
}
```

SavedStateHandle автоматически сохраняет данные при пересоздании Activity или Fragment и восстанавливает их при создании нового экземпляра ViewModel.
