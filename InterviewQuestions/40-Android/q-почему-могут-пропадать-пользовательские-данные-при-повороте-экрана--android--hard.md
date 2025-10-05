---
id: 202510031417013
title: "Why user data may disappear on screen rotation"
question_ru: "Почему могут пропадать пользовательские данные при повороте экрана"
question_en: "Почему могут пропадать пользовательские данные при повороте экрана"
topic: android
moc: moc-android
status: draft
difficulty: hard
tags:
  - activity lifecycle
  - data retention
  - lifecycle
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/377
---

# Why user data may disappear on screen rotation

## English Answer

User data disappearing during screen rotation in Android applications is a common problem related to how Android manages the Activity lifecycle. When the device rotates, the system destroys the current Activity and recreates it from scratch, leading to data loss if it wasn't saved properly.

### Why This Happens

#### Activity Recreation During Configuration Changes

```kotlin
class MainActivity : AppCompatActivity() {

    // This variable will be LOST on rotation
    private var userData: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        Log.d("Lifecycle", "onCreate called, userData = '$userData'")
        // After rotation: onCreate called, userData = ''
        // Previous value is LOST!
    }

    fun onButtonClick(view: View) {
        userData = editText.text.toString()
        Log.d("Lifecycle", "Saved userData = '$userData'")
    }
}
```

### Configuration Change Lifecycle

```
User enters text: "Hello World"
    ↓
User rotates device
    ↓
onPause() called
    ↓
onStop() called
    ↓
onSaveInstanceState(Bundle) called  ← Last chance to save!
    ↓
onDestroy() called  ← Activity DESTROYED, all fields lost
    ↓
onCreate(Bundle) called  ← New Activity instance created
    ↓
onStart() called
    ↓
onRestoreInstanceState(Bundle) called  ← Restore saved data here
    ↓
onResume() called
```

### Solutions

## Solution 1: onSaveInstanceState / onRestoreInstanceState

The traditional Android approach:

```kotlin
class MainActivity : AppCompatActivity() {

    private var userName: String = ""
    private var userAge: Int = 0
    private var selectedItems: ArrayList<String> = ArrayList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Restore data if available
        savedInstanceState?.let {
            userName = it.getString("user_name", "")
            userAge = it.getInt("user_age", 0)
            selectedItems = it.getStringArrayList("selected_items") ?: ArrayList()

            Log.d("Lifecycle", "Restored: name=$userName, age=$userAge")
        }

        updateUI()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        // Save data before destruction
        outState.putString("user_name", userName)
        outState.putInt("user_age", userAge)
        outState.putStringArrayList("selected_items", selectedItems)

        Log.d("Lifecycle", "Saved state: name=$userName, age=$userAge")
    }

    // Alternative: onRestoreInstanceState (called after onStart)
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)

        // Can also restore here instead of onCreate
        userName = savedInstanceState.getString("user_name", "")
        userAge = savedInstanceState.getInt("user_age", 0)

        updateUI()
    }

    private fun updateUI() {
        nameEditText.setText(userName)
        ageEditText.setText(userAge.toString())
    }
}
```

## Solution 2: ViewModel (Recommended)

Modern approach using Architecture Components:

```kotlin
class UserViewModel : ViewModel() {

    // This data SURVIVES configuration changes
    private val _userName = MutableLiveData<String>()
    val userName: LiveData<String> = _userName

    private val _userAge = MutableLiveData<Int>()
    val userAge: LiveData<Int> = _userAge

    private val _formData = MutableLiveData<FormData>()
    val formData: LiveData<FormData> = _formData

    fun updateUserName(name: String) {
        _userName.value = name
    }

    fun updateUserAge(age: Int) {
        _userAge.value = age
    }

    fun updateFormData(data: FormData) {
        _formData.value = data
    }

    override fun onCleared() {
        super.onCleared()
        // Called only when Activity is FINISHED, not on rotation
        Log.d("ViewModel", "ViewModel cleared")
    }
}

data class FormData(
    val name: String,
    val email: String,
    val age: Int
)

class MainActivity : AppCompatActivity() {

    // ViewModel survives rotation
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        Log.d("Lifecycle", "ViewModel hashCode: ${viewModel.hashCode()}")
        // Same hashCode after rotation - same instance!

        // Observe data
        viewModel.userName.observe(this) { name ->
            nameTextView.text = name
            // Data automatically restored after rotation
        }

        viewModel.userAge.observe(this) { age ->
            ageTextView.text = age.toString()
        }

        // Save user input
        saveButton.setOnClickListener {
            viewModel.updateUserName(nameEditText.text.toString())
            viewModel.updateUserAge(ageEditText.text.toString().toIntOrNull() ?: 0)
        }
    }
}
```

## Solution 3: ViewModel + SavedStateHandle

For data that must survive even process death:

```kotlin
class UserViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Survives configuration changes AND process death
    val userName: MutableLiveData<String> =
        savedStateHandle.getLiveData("user_name")

    val userAge: MutableLiveData<Int> =
        savedStateHandle.getLiveData("user_age")

    @Parcelize
    data class FormData(
        val name: String,
        val email: String,
        val age: Int
    ) : Parcelable

    var formData: FormData?
        get() = savedStateHandle["form_data"]
        set(value) { savedStateHandle["form_data"] = value }

    fun updateFormData(name: String, email: String, age: Int) {
        formData = FormData(name, email, age)
    }
}

class MainActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Data restored automatically from SavedStateHandle
        viewModel.userName.observe(this) { name ->
            nameEditText.setText(name)
        }

        viewModel.formData?.let { data ->
            nameEditText.setText(data.name)
            emailEditText.setText(data.email)
            ageEditText.setText(data.age.toString())
        }

        saveButton.setOnClickListener {
            viewModel.userName.value = nameEditText.text.toString()
            viewModel.updateFormData(
                nameEditText.text.toString(),
                emailEditText.text.toString(),
                ageEditText.text.toString().toIntOrNull() ?: 0
            )
        }
    }
}
```

## Solution 4: Prevent Configuration Changes (Not Recommended)

Prevent Activity recreation on rotation (usually not recommended):

```xml
<!-- AndroidManifest.xml -->
<activity
    android:name=".MainActivity"
    android:configChanges="orientation|screenSize|keyboardHidden">
    <!-- Activity won't be recreated on these config changes -->
</activity>
```

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)

        // Handle configuration change manually
        when (newConfig.orientation) {
            Configuration.ORIENTATION_LANDSCAPE -> {
                Log.d("Config", "Changed to landscape")
                // Update UI for landscape
            }
            Configuration.ORIENTATION_PORTRAIT -> {
                Log.d("Config", "Changed to portrait")
                // Update UI for portrait
            }
        }
    }
}
```

**Why not recommended:**
- Different layouts for orientations won't work
- More code to maintain
- Goes against Android design principles

## Solution 5: Retain View State

Some views automatically save their state:

```xml
<!-- Views with android:id automatically save/restore state -->
<EditText
    android:id="@+id/nameEditText"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:saveEnabled="true" />  <!-- default is true -->

<!-- Without ID, state is NOT saved -->
<EditText
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />  <!-- State LOST on rotation -->
```

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // EditText with ID will retain text after rotation automatically
        // No code needed!
    }
}
```

### Complete Example: Registration Form

```kotlin
@Parcelize
data class RegistrationForm(
    val firstName: String = "",
    val lastName: String = "",
    val email: String = "",
    val phone: String = "",
    val acceptedTerms: Boolean = false
) : Parcelable

class RegistrationViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    companion object {
        private const val FORM_KEY = "registration_form"
    }

    var form: RegistrationForm
        get() = savedStateHandle[FORM_KEY] ?: RegistrationForm()
        set(value) { savedStateHandle[FORM_KEY] = value }

    fun updateFirstName(value: String) {
        form = form.copy(firstName = value)
    }

    fun updateLastName(value: String) {
        form = form.copy(lastName = value)
    }

    fun updateEmail(value: String) {
        form = form.copy(email = value)
    }

    fun updatePhone(value: String) {
        form = form.copy(phone = value)
    }

    fun updateTerms(accepted: Boolean) {
        form = form.copy(acceptedTerms = accepted)
    }
}

class RegistrationActivity : AppCompatActivity() {

    private val viewModel: RegistrationViewModel by viewModels()
    private lateinit var binding: ActivityRegistrationBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegistrationBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Restore form data
        restoreFormData()

        // Listen to changes
        setupListeners()
    }

    private fun restoreFormData() {
        val form = viewModel.form

        binding.firstNameEditText.setText(form.firstName)
        binding.lastNameEditText.setText(form.lastName)
        binding.emailEditText.setText(form.email)
        binding.phoneEditText.setText(form.phone)
        binding.termsCheckBox.isChecked = form.acceptedTerms

        Log.d("Registration", "Form restored: $form")
    }

    private fun setupListeners() {
        binding.firstNameEditText.addTextChangedListener {
            viewModel.updateFirstName(it.toString())
        }

        binding.lastNameEditText.addTextChangedListener {
            viewModel.updateLastName(it.toString())
        }

        binding.emailEditText.addTextChangedListener {
            viewModel.updateEmail(it.toString())
        }

        binding.phoneEditText.addTextChangedListener {
            viewModel.updatePhone(it.toString())
        }

        binding.termsCheckBox.setOnCheckedChangeListener { _, isChecked ->
            viewModel.updateTerms(isChecked)
        }

        binding.submitButton.setOnClickListener {
            submitForm()
        }
    }

    private fun submitForm() {
        val form = viewModel.form

        if (validateForm(form)) {
            // Submit to server
            Log.d("Registration", "Submitting form: $form")
        }
    }

    private fun validateForm(form: RegistrationForm): Boolean {
        return form.firstName.isNotBlank() &&
                form.lastName.isNotBlank() &&
                form.email.contains("@") &&
                form.phone.isNotBlank() &&
                form.acceptedTerms
    }
}
```

### Comparison of Approaches

| Approach | Survives Rotation | Survives Process Death | Complexity | Recommended |
|----------|-------------------|------------------------|------------|-------------|
| None | ❌ No | ❌ No | Low | ❌ Never |
| onSaveInstanceState | ✅ Yes | ✅ Yes | Medium | ⚠️ For simple data |
| ViewModel | ✅ Yes | ❌ No | Low | ✅ Yes |
| ViewModel + SavedStateHandle | ✅ Yes | ✅ Yes | Low | ✅ Best |
| Prevent config changes | ✅ Yes | ❌ No | High | ❌ Not recommended |
| View state (with ID) | ✅ Yes | ✅ Yes | None | ✅ For views |

### Best Practices

1. **Use ViewModel** for UI-related data
2. **Add SavedStateHandle** for data that must survive process death
3. **Give views android:id** to auto-save their state
4. **Keep Bundle data small** (< 500KB) in onSaveInstanceState
5. **Don't prevent configuration changes** unless absolutely necessary
6. **Test with "Don't keep activities"** developer option

## Russian Answer

Пропадание пользовательских данных при повороте экрана в Android-приложениях является распространенной проблемой, связанной с тем, как Android управляет жизненным циклом активности. Когда устройство поворачивается, система уничтожает текущую активность и создает её заново, что приводит к потере данных, если они не были сохранены должным образом.

### Причины

При повороте экрана происходит изменение конфигурации (configuration change). По умолчанию Android уничтожает текущую Activity и создает новый экземпляр, чтобы применить ресурсы, соответствующие новой ориентации экрана. Все переменные класса Activity теряются при этом процессе.

### Решения

1. **onSaveInstanceState / onRestoreInstanceState**: Сохранение данных в Bundle перед уничтожением Activity и восстановление при создании

2. **ViewModel**: Современный подход, где данные хранятся в ViewModel, которая переживает изменения конфигурации

3. **ViewModel + SavedStateHandle**: Для данных, которые должны пережить даже смерть процесса

4. **Предотвращение пересоздания**: Использование `android:configChanges` в манифесте (не рекомендуется)

5. **Автосохранение View**: View с android:id автоматически сохраняют свое состояние

Рекомендуемый подход - использование ViewModel с SavedStateHandle для критических данных.
