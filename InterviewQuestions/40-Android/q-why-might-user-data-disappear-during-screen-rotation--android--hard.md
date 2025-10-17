---
id: "20251015082237553"
title: "Why might user data disappear during screen rotation?"
topic: android
difficulty: hard
status: draft
created: 2025-10-13
tags: - android
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---
# Why might user data disappear during screen rotation?

## Answer (EN)
User data disappears during screen rotation because Android destroys and recreates the Activity by default when a configuration change occurs. If data is not properly saved and restored, it will be lost during this process.

### Why Android Destroys Activity on Rotation

Android recreates the Activity to:
1. Apply new resource configurations (layout-land, values-sw600dp, etc.)
2. Load appropriate resources for new orientation
3. Recalculate layout dimensions
4. Apply new density/language/theme settings

### The Problem

```kotlin
// - Data will be lost on rotation
class FormActivity : AppCompatActivity() {

    private var userInput: String = ""
    private var selectedItemPosition: Int = 0
    private var isCheckboxChecked: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        // User enters data
        findViewById<EditText>(R.id.editText).addTextChangedListener { text ->
            userInput = text.toString()
        }

        // User selects item
        findViewById<Spinner>(R.id.spinner).onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                selectedItemPosition = position
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    //  Device rotated
    //  onCreate() called again
    // - userInput = "" (lost)
    // - selectedItemPosition = 0 (lost)
}
```

### Lifecycle During Rotation

```
User rotates device
      ↓
onPause()           ← Activity losing focus
      ↓
onSaveInstanceState()  ← SAVE STATE HERE
      ↓
onStop()            ← Activity no longer visible
      ↓
onDestroy()         ← Activity destroyed
      ↓
[New Activity Instance Created]
      ↓
onCreate(savedInstanceState)  ← RESTORE STATE HERE
      ↓
onStart()
      ↓
onRestoreInstanceState()      ← Alternative restore point
      ↓
onResume()          ← Activity interactive again
```

### Solution 1: onSaveInstanceState (For UI State)

```kotlin
class FormActivity : AppCompatActivity() {

    private lateinit var editText: EditText
    private lateinit var spinner: Spinner
    private lateinit var checkBox: CheckBox

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        editText = findViewById(R.id.editText)
        spinner = findViewById(R.id.spinner)
        checkBox = findViewById(R.id.checkBox)

        // - Restore saved state
        savedInstanceState?.let {
            editText.setText(it.getString(KEY_USER_INPUT, ""))
            spinner.setSelection(it.getInt(KEY_SELECTED_POSITION, 0))
            checkBox.isChecked = it.getBoolean(KEY_CHECKBOX_STATE, false)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // - Save current state
        outState.putString(KEY_USER_INPUT, editText.text.toString())
        outState.putInt(KEY_SELECTED_POSITION, spinner.selectedItemPosition)
        outState.putBoolean(KEY_CHECKBOX_STATE, checkBox.isChecked)
    }

    companion object {
        private const val KEY_USER_INPUT = "user_input"
        private const val KEY_SELECTED_POSITION = "selected_position"
        private const val KEY_CHECKBOX_STATE = "checkbox_state"
    }
}
```

### Solution 2: ViewModel (For Complex Data)

```kotlin
// ViewModel - survives configuration changes
class FormViewModel : ViewModel() {

    val userInput = MutableLiveData<String>()
    val selectedPosition = MutableLiveData<Int>()
    val isCheckboxChecked = MutableLiveData<Boolean>()

    // Heavy data that shouldn't be in Bundle
    val productList = MutableLiveData<List<Product>>()

    init {
        loadProducts()
    }

    private fun loadProducts() {
        viewModelScope.launch {
            productList.value = repository.getProducts()
        }
    }
}

class FormActivity : AppCompatActivity() {

    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        // - ViewModel survives rotation
        // Data automatically preserved

        viewModel.userInput.observe(this) { input ->
            // Update UI
        }

        viewModel.productList.observe(this) { products ->
            // Products not reloaded on rotation
            updateProductList(products)
        }

        findViewById<EditText>(R.id.editText).addTextChangedListener { text ->
            viewModel.userInput.value = text.toString()
        }
    }
}
```

### Solution 3: SavedStateHandle in ViewModel (Best Practice)

```kotlin
class FormViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Survives both configuration changes AND process death
    var userInput: String
        get() = savedStateHandle.get<String>(KEY_USER_INPUT) ?: ""
        set(value) { savedStateHandle.set(KEY_USER_INPUT, value) }

    var selectedPosition: Int
        get() = savedStateHandle.get<Int>(KEY_POSITION) ?: 0
        set(value) { savedStateHandle.set(KEY_POSITION, value) }

    // LiveData backed by SavedStateHandle
    val isChecked: MutableLiveData<Boolean> =
        savedStateHandle.getLiveData(KEY_CHECKED, false)

    companion object {
        private const val KEY_USER_INPUT = "user_input"
        private const val KEY_POSITION = "position"
        private const val KEY_CHECKED = "checked"
    }
}

class FormActivity : AppCompatActivity() {

    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        // - Restores automatically
        findViewById<EditText>(R.id.editText).apply {
            setText(viewModel.userInput)
            addTextChangedListener { text ->
                viewModel.userInput = text.toString()
            }
        }
    }
}
```

### Solution 4: retainInstance (Deprecated for Fragments)

```kotlin
// WARNING: Deprecated - use ViewModel instead
class DataFragment : Fragment() {

    private var data: LargeDataSet? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        retainInstance = true // Fragment instance retained

        if (data == null) {
            data = loadLargeDataSet()
        }
    }
}
```

### Solution 5: Prevent Recreation (Use Carefully)

```xml
<!-- AndroidManifest.xml -->
<!-- WARNING: Not recommended - handle rotation properly instead -->
<activity
    android:name=".MainActivity"
    android:configChanges="orientation|screenSize|keyboardHidden">
    <!-- Activity won't be recreated on these changes -->
</activity>
```

```kotlin
// Handle configuration changes manually
class MainActivity : AppCompatActivity() {

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)

        // Handle rotation manually
        if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            // Update UI for landscape
        } else {
            // Update UI for portrait
        }
    }
}
```

**Downsides**:
- Must manually handle all configuration changes
- Won't load orientation-specific resources automatically
- More complex code
- Generally considered bad practice

### What Gets Automatically Saved

Views with IDs automatically save basic state:

```xml
<!-- Views with android:id automatically save state -->
<EditText
    android:id="@+id/editText"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
    <!-- Text automatically saved/restored -->

<CheckBox
    android:id="@+id/checkBox"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
    <!-- Checked state automatically saved/restored -->

<RecyclerView
    android:id="@+id/recyclerView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
    <!-- Scroll position automatically saved/restored -->
```

### What Needs Manual Saving

```kotlin
class ComplexActivity : AppCompatActivity() {

    // - Need manual save
    private var userScore: Int = 0
    private var currentLevel: Int = 1
    private lateinit var gameState: GameState
    private val selectedItems = mutableListOf<Int>()

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // - Save manually
        outState.putInt("score", userScore)
        outState.putInt("level", currentLevel)
        outState.putParcelable("game_state", gameState)
        outState.putIntegerArrayList("selected_items", ArrayList(selectedItems))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // - Restore manually
        savedInstanceState?.let {
            userScore = it.getInt("score", 0)
            currentLevel = it.getInt("level", 1)
            gameState = it.getParcelable("game_state") ?: GameState()
            selectedItems.clear()
            selectedItems.addAll(it.getIntegerArrayList("selected_items") ?: emptyList())
        }
    }
}
```

### Common Mistakes

```kotlin
// - Mistake 1: Not using savedInstanceState
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Always initializing with defaults
    var counter = 0 // Lost on rotation!
}

// - Mistake 2: Calling super after restoring
override fun onCreate(savedInstanceState: Bundle?) {
    restoreState(savedInstanceState) // Wrong order!
    super.onCreate(savedInstanceState)
}

// - Mistake 3: Not calling super in onSaveInstanceState
override fun onSaveInstanceState(outState: Bundle) {
    // super.onSaveInstanceState(outState) // Missing!
    outState.putString("key", "value")
}

// - Mistake 4: Saving large data in Bundle
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putParcelableArrayList("huge_list", ArrayList(millionItems))
    // TransactionTooLargeException!
}

// - Correct approach
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    savedInstanceState?.let {
        // Restore state
    } ?: run {
        // First time creation
    }
}
```

### Decision Matrix

| Data Type | Solution | Reason |
|-----------|----------|--------|
| EditText value (with ID) | Automatic | View saves own state |
| Custom variable | onSaveInstanceState | Small data, survives process death |
| Large object | ViewModel | Complex data, config changes only |
| Critical small data | SavedStateHandle | Survives both config changes and process death |
| Temporary UI state | onSaveInstanceState | Recreated quickly |
| Network data | ViewModel + Repository | Should not reload on rotation |
| Form input | SavedStateHandle | Must survive process death |

### Complete Example

```kotlin
// Best practice: Combine ViewModel + SavedStateHandle
class RegistrationViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Critical data - survives process death
    var email: String
        get() = savedStateHandle.get<String>("email") ?: ""
        set(value) { savedStateHandle.set("email", value) }

    var password: String
        get() = savedStateHandle.get<String>("password") ?: ""
        set(value) { savedStateHandle.set("password", value) }

    // Non-critical data - ViewModel only
    val countries = MutableLiveData<List<Country>>()

    init {
        if (countries.value == null) {
            loadCountries()
        }
    }

    private fun loadCountries() {
        viewModelScope.launch {
            countries.value = repository.getCountries()
        }
    }
}

class RegistrationActivity : AppCompatActivity() {

    private val viewModel: RegistrationViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_registration)

        // - All data preserved on rotation
        setupViews()
    }

    private fun setupViews() {
        findViewById<EditText>(R.id.emailEditText).apply {
            setText(viewModel.email)
            addTextChangedListener { text ->
                viewModel.email = text.toString()
            }
        }

        findViewById<EditText>(R.id.passwordEditText).apply {
            setText(viewModel.password)
            addTextChangedListener { text ->
                viewModel.password = text.toString()
            }
        }

        viewModel.countries.observe(this) { countries ->
            updateCountrySpinner(countries)
        }
    }
}
```

### Summary

Data disappears on rotation because:
1. **Activity is destroyed and recreated** by default
2. **Variables reset** to initial values
3. **Data not saved** in onSaveInstanceState
4. **ViewModel not used** for complex data

**Solutions**:
- Use **onSaveInstanceState** for small UI state
- Use **ViewModel** for complex data
- Use **SavedStateHandle** for critical data (best practice)
- Ensure views have **IDs** for automatic state saving

## Ответ (RU)
Пропадание пользовательских данных при повороте экрана в Android-приложениях является распространенной проблемой, связанной с тем, как Android управляет жизненным циклом активности. Когда устройство поворачивается, система уничтожает текущую активность и создает её заново, что приводит к потере данных, если они не были сохранены должным образом.

## Related Topics
- onSaveInstanceState
- ViewModel
- SavedStateHandle
- Configuration changes
- retainInstance (deprecated)
