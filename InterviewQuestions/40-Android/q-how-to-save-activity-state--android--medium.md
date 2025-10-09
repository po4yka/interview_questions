---
topic: android
tags:
  - android
difficulty: medium
status: reviewed
---

# How to save Activity state?

**English**: How to save Activity state?

## Answer

Android provides multiple mechanisms to save and restore Activity state across configuration changes (like screen rotation) and process death. The choice depends on the data type, size, and persistence requirements.

### 1. onSaveInstanceState() / onRestoreInstanceState()

The most common approach for saving lightweight UI state.

#### Basic Usage

```kotlin
class MainActivity : AppCompatActivity() {
    private var counter = 0
    private var userName = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Restore state
        if (savedInstanceState != null) {
            counter = savedInstanceState.getInt("COUNTER", 0)
            userName = savedInstanceState.getString("USER_NAME", "")
        }

        updateUI()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save state
        outState.putInt("COUNTER", counter)
        outState.putString("USER_NAME", userName)
    }

    // Alternative: restore in onRestoreInstanceState
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        counter = savedInstanceState.getInt("COUNTER", 0)
        userName = savedInstanceState.getString("USER_NAME", "")
    }

    private fun updateUI() {
        counterText.text = "Count: $counter"
        nameText.text = "User: $userName"
    }
}
```

#### Saving Complex Objects

```kotlin
data class UserProfile(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int
) : Parcelable {
    constructor(parcel: Parcel) : this(
        parcel.readInt(),
        parcel.readString() ?: "",
        parcel.readString() ?: "",
        parcel.readInt()
    )

    override fun writeToParcel(parcel: Parcel, flags: Int) {
        parcel.writeInt(id)
        parcel.writeString(name)
        parcel.writeString(email)
        parcel.writeInt(age)
    }

    override fun describeContents() = 0

    companion object CREATOR : Parcelable.Creator<UserProfile> {
        override fun createFromParcel(parcel: Parcel) = UserProfile(parcel)
        override fun newArray(size: Int): Array<UserProfile?> = arrayOfNulls(size)
    }
}

class ProfileActivity : AppCompatActivity() {
    private var userProfile: UserProfile? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        userProfile = savedInstanceState?.getParcelable("USER_PROFILE")
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putParcelable("USER_PROFILE", userProfile)
    }
}
```

#### Using @Parcelize (Kotlin)

```kotlin
import kotlinx.parcelize.Parcelize

@Parcelize
data class UserProfile(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int
) : Parcelable

// Usage is the same - no boilerplate needed!
```

### 2. ViewModel with SavedStateHandle

Recommended modern approach that survives both configuration changes and process death.

#### ViewModel with Saved State

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.SavedStateHandle

class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    // Automatically saved/restored
    var counter: Int
        get() = savedStateHandle.get<Int>("counter") ?: 0
        set(value) = savedStateHandle.set("counter", value)

    var userName: String
        get() = savedStateHandle.get<String>("userName") ?: ""
        set(value) = savedStateHandle.set("userName", value)

    // Or use LiveData
    val counterLiveData: MutableLiveData<Int> = savedStateHandle.getLiveData("counter", 0)
    val userNameLiveData: MutableLiveData<String> = savedStateHandle.getLiveData("userName", "")

    fun incrementCounter() {
        counter++
        counterLiveData.value = counter
    }
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Observe data
        viewModel.counterLiveData.observe(this) { count ->
            counterText.text = "Count: $count"
        }

        incrementButton.setOnClickListener {
            viewModel.incrementCounter()
        }
    }
}
```

#### SavedStateHandle with StateFlow

```kotlin
class ModernViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    private val _counter = MutableStateFlow(savedStateHandle.get<Int>("counter") ?: 0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    init {
        // Save to savedStateHandle whenever value changes
        viewModelScope.launch {
            _counter.collect { value ->
                savedStateHandle["counter"] = value
            }
        }
    }

    fun incrementCounter() {
        _counter.value++
    }
}

// In Activity
lifecycleScope.launch {
    viewModel.counter.collect { count ->
        counterText.text = "Count: $count"
    }
}
```

### 3. Persistent Storage

For data that needs to survive app termination.

#### SharedPreferences

```kotlin
class SettingsActivity : AppCompatActivity() {

    private val prefs by lazy {
        getSharedPreferences("app_settings", Context.MODE_PRIVATE)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        // Load saved settings
        val isDarkMode = prefs.getBoolean("dark_mode", false)
        val fontSize = prefs.getInt("font_size", 14)

        applySettings(isDarkMode, fontSize)
    }

    private fun saveSettings(isDarkMode: Boolean, fontSize: Int) {
        prefs.edit {
            putBoolean("dark_mode", isDarkMode)
            putInt("font_size", fontSize)
            apply()
        }
    }
}
```

#### DataStore (Modern Alternative)

```kotlin
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore

val Context.dataStore by preferencesDataStore(name = "settings")

class SettingsRepository(private val context: Context) {

    private val DARK_MODE_KEY = booleanPreferencesKey("dark_mode")
    private val FONT_SIZE_KEY = intPreferencesKey("font_size")

    val darkMode: Flow<Boolean> = context.dataStore.data
        .map { preferences -> preferences[DARK_MODE_KEY] ?: false }

    suspend fun setDarkMode(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[DARK_MODE_KEY] = enabled
        }
    }

    val fontSize: Flow<Int> = context.dataStore.data
        .map { preferences -> preferences[FONT_SIZE_KEY] ?: 14 }

    suspend fun setFontSize(size: Int) {
        context.dataStore.edit { preferences ->
            preferences[FONT_SIZE_KEY] = size
        }
    }
}
```

#### Room Database

```kotlin
@Entity(tableName = "user_state")
data class UserState(
    @PrimaryKey val id: Int = 1,
    val scrollPosition: Int,
    val selectedTab: Int,
    val searchQuery: String
)

@Dao
interface UserStateDao {
    @Query("SELECT * FROM user_state WHERE id = 1")
    fun getUserState(): Flow<UserState?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveUserState(state: UserState)
}

class MyViewModel(private val dao: UserStateDao) : ViewModel() {

    val userState: Flow<UserState?> = dao.getUserState()

    fun saveState(scrollPosition: Int, selectedTab: Int, searchQuery: String) {
        viewModelScope.launch {
            dao.saveUserState(UserState(1, scrollPosition, selectedTab, searchQuery))
        }
    }
}
```

### 4. Handling Fragment State

#### Fragment with onSaveInstanceState

```kotlin
class MyFragment : Fragment() {
    private var selectedItemId: Int = -1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        selectedItemId = savedInstanceState?.getInt("SELECTED_ITEM") ?: -1
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("SELECTED_ITEM", selectedItemId)
    }
}
```

#### Fragment with ViewModel and SavedStateHandle

```kotlin
class FragmentViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    var selectedItemId: Int
        get() = savedStateHandle.get<Int>("selectedItem") ?: -1
        set(value) = savedStateHandle.set("selectedItem", value)
}

class MyFragment : Fragment() {
    private val viewModel: FragmentViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // selectedItemId automatically restored
        displayItem(viewModel.selectedItemId)
    }
}
```

### 5. Comparison of Approaches

| Approach | Survives Rotation | Survives Process Death | Survives App Close | Use Case |
|----------|------------------|----------------------|-------------------|----------|
| **onSaveInstanceState** | - Yes | - Yes (limited) | - No | Lightweight UI state |
| **ViewModel (no SavedState)** | - Yes | - No | - No | UI-related data during session |
| **ViewModel + SavedStateHandle** | - Yes | - Yes | - No | UI state across process death |
| **SharedPreferences** | - Yes | - Yes | - Yes | User settings, small data |
| **DataStore** | - Yes | - Yes | - Yes | Settings, preferences (modern) |
| **Room Database** | - Yes | - Yes | - Yes | Large datasets, complex queries |

### 6. Best Practices

#### Combine Multiple Approaches

```kotlin
class UserActivity : AppCompatActivity() {

    // ViewModel for UI state
    private val viewModel: UserViewModel by viewModels()

    // Persistent storage
    private val prefs by lazy {
        getSharedPreferences("user_prefs", Context.MODE_PRIVATE)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Restore from persistent storage
        val userId = prefs.getInt("user_id", -1)
        if (userId != -1) {
            viewModel.loadUser(userId)
        }

        // UI state handled by ViewModel + SavedStateHandle
        viewModel.userName.observe(this) { name ->
            nameText.text = name
        }
    }

    override fun onPause() {
        super.onPause()
        // Save important data persistently
        prefs.edit {
            putInt("user_id", viewModel.currentUserId)
            apply()
        }
    }
}
```

#### State Management Summary

```kotlin
class ComprehensiveActivity : AppCompatActivity() {

    // 1. ViewModel for UI state (survives rotation)
    private val viewModel: MyViewModel by viewModels()

    // 2. SavedStateHandle for critical UI state (survives process death)
    // Already integrated in ViewModel

    // 3. Persistent storage for user data
    private val dataStore by lazy { DataStoreRepository(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Load persistent user preferences
        lifecycleScope.launch {
            dataStore.userSettings.collect { settings ->
                applySettings(settings)
            }
        }

        // Observe UI state from ViewModel
        viewModel.uiState.observe(this) { state ->
            updateUI(state)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Only if ViewModel + SavedStateHandle not used
        // outState.putString("temp_data", tempValue)
    }
}
```

### Summary

**Choose the right approach:**

1. **Light UI state** (scroll position, selected tab) → `onSaveInstanceState()` or `SavedStateHandle`
2. **UI-related data during session** → `ViewModel` (without SavedStateHandle)
3. **Critical UI state across process death** → `ViewModel` + `SavedStateHandle`
4. **User settings** → `SharedPreferences` or `DataStore`
5. **Large datasets** → `Room` database
6. **Combine approaches** for robust state management

**Best Practice:**
- Use `ViewModel + SavedStateHandle` for most UI state
- Use `DataStore` or `Room` for persistent data
- Avoid relying solely on `onSaveInstanceState()` (limited data size)

## Ответ

Android предоставляет несколько механизмов для сохранения и восстановления состояния Activity.

### 1. onSaveInstanceState() / onRestoreInstanceState()

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("counter", counter)
    outState.putString("name", userName)
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (savedInstanceState != null) {
        counter = savedInstanceState.getInt("counter", 0)
        userName = savedInstanceState.getString("name", "")
    }
}
```

### 2. ViewModel с SavedStateHandle (рекомендуется)

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    var counter: Int
        get() = savedStateHandle.get<Int>("counter") ?: 0
        set(value) = savedStateHandle.set("counter", value)
}
```

### 3. Постоянное хранилище

- **SharedPreferences** - для настроек
- **DataStore** - современная альтернатива SharedPreferences
- **Room** - для больших данных

### Сравнение

| Подход | Переживает поворот | Переживает смерть процесса | Переживает закрытие |
|--------|-------------------|---------------------------|-------------------|
| onSaveInstanceState | - | - (ограниченно) | - |
| ViewModel | - | - | - |
| ViewModel + SavedStateHandle | - | - | - |
| SharedPreferences/DataStore | - | - | - |
| Room | - | - | - |

**Лучшая практика:** Используйте ViewModel + SavedStateHandle для UI состояния и DataStore/Room для постоянных данных.

