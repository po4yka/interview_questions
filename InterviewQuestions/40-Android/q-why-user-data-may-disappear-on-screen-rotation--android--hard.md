---
id: "20251015082238632"
title: "Why User Data May Disappear On Screen Rotation / Почему данные пользователя могут пропасть при повороте экрана"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: - android
---
# Why user data may disappear on screen rotation?

**Russian**: Почему пользовательские данные могут исчезнуть при повороте экрана?

## Answer (EN)
User data disappears on screen rotation because **Android destroys and recreates the Activity** during configuration changes. If the state isn't properly saved and restored, all transient data (variables, user input, UI state) is lost.

### Why Activity is Recreated

When the screen rotates, Android treats it as a **configuration change**. The system:

1. **Destroys** the current Activity (calls `onDestroy()`)
2. **Recreates** a new Activity instance (calls `onCreate()`)
3. **Loads** the appropriate layout for the new orientation (portrait/landscape)

**This means:**
- All non-static variables are reset
- UI state (EditText content, scroll position, etc.) can be lost
- Network requests, downloads, or async operations may be interrupted

---

## Common Causes of Data Loss

### 1. Transient Data Not Saved

**Problem:**

```kotlin
class LoginActivity : AppCompatActivity() {
    private var username: String = ""
    private var password: String = ""
    private var isLoggingIn: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        loginButton.setOnClickListener {
            username = usernameField.text.toString()
            password = passwordField.text.toString()
            isLoggingIn = true
            performLogin() // Async operation
        }
    }

    // - On rotation, username, password, and isLoggingIn are LOST!
}
```

**Result:** After rotation:
- `username` and `password` become empty strings
- `isLoggingIn` resets to `false`
- Login progress is lost

---

### 2. EditText Content Lost (No ID)

**Problem:**

```xml
<!-- - BAD: EditText without android:id -->
<EditText
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:hint="Enter name" />
```

**Solution:**

```xml
<!-- - GOOD: EditText with android:id -->
<EditText
    android:id="@+id/nameField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:hint="Enter name" />
```

**Why?**
- Views with `android:id` automatically save/restore their state
- EditText, CheckBox, RadioButton, etc. handle state preservation internally
- **Without ID:** Android doesn't know which view to restore

---

### 3. Not Using ViewModel

**Problem:**

```kotlin
class UserListActivity : AppCompatActivity() {
    private var users: List<User> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user_list)

        // Load data
        lifecycleScope.launch {
            users = repository.getUsers() // Expensive network call
            displayUsers(users)
        }
    }

    // - On rotation, users list is lost
    // Network call is made AGAIN unnecessarily
}
```

**Solution with ViewModel:**

```kotlin
class UserListViewModel : ViewModel() {
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }
}

class UserListActivity : AppCompatActivity() {
    private val viewModel: UserListViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user_list)

        // - Data survives rotation
        // Network call happens ONCE
        viewModel.users.observe(this) { users ->
            displayUsers(users)
        }
    }
}
```

---

### 4. Not Implementing onSaveInstanceState()

**Problem:**

```kotlin
class GameActivity : AppCompatActivity() {
    private var score: Int = 0
    private var level: Int = 1
    private var playerName: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_game)

        // Initialize game state
        scoreText.text = "Score: $score"
    }

    // - No onSaveInstanceState() implementation
    // All game state lost on rotation!
}
```

**Solution:**

```kotlin
class GameActivity : AppCompatActivity() {
    private var score: Int = 0
    private var level: Int = 1
    private var playerName: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_game)

        // Restore state
        if (savedInstanceState != null) {
            score = savedInstanceState.getInt("SCORE", 0)
            level = savedInstanceState.getInt("LEVEL", 1)
            playerName = savedInstanceState.getString("PLAYER_NAME", "")
        }

        scoreText.text = "Score: $score"
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // - Save state before destruction
        outState.putInt("SCORE", score)
        outState.putInt("LEVEL", level)
        outState.putString("PLAYER_NAME", playerName)
    }
}
```

---

### 5. Async Operations Not Handled

**Problem:**

```kotlin
class DownloadActivity : AppCompatActivity() {
    private var downloadJob: Job? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_download)

        downloadButton.setOnClickListener {
            downloadJob = lifecycleScope.launch {
                downloadFile() // Long-running operation
            }
        }
    }

    // - On rotation:
    // - downloadJob reference is lost
    // - Download continues but UI can't update
    // - No way to track download progress
}
```

**Solution with ViewModel:**

```kotlin
class DownloadViewModel : ViewModel() {
    private val _downloadProgress = MutableLiveData<Int>()
    val downloadProgress: LiveData<Int> = _downloadProgress

    private var downloadJob: Job? = null

    fun startDownload() {
        if (downloadJob?.isActive == true) return // Already downloading

        downloadJob = viewModelScope.launch {
            for (progress in 0..100 step 10) {
                delay(500)
                _downloadProgress.value = progress
            }
        }
    }

    fun cancelDownload() {
        downloadJob?.cancel()
    }
}

class DownloadActivity : AppCompatActivity() {
    private val viewModel: DownloadViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_download)

        // - Download survives rotation
        viewModel.downloadProgress.observe(this) { progress ->
            progressBar.progress = progress
            progressText.text = "$progress%"
        }

        downloadButton.setOnClickListener {
            viewModel.startDownload()
        }
    }
}
```

---

### 6. Fragment Data Loss

**Problem:**

```kotlin
class UserFragment : Fragment() {
    private var userId: Int = -1
    private var userData: User? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        userId = arguments?.getInt("USER_ID") ?: -1
        loadUserData(userId)
    }

    private fun loadUserData(id: Int) {
        lifecycleScope.launch {
            userData = repository.getUser(id)
            displayUser(userData)
        }
    }

    // - userData lost on configuration change
}
```

**Solution:**

```kotlin
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = arguments?.getInt("USER_ID") ?: -1
        viewModel.loadUser(userId)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // - Data survives rotation
        viewModel.user.observe(viewLifecycleOwner) { user ->
            displayUser(user)
        }
    }
}
```

---

## Complete Example: Data Loss vs. Proper Handling

### - Bad Example (Data Lost)

```kotlin
class BadActivity : AppCompatActivity() {
    private var counter = 0
    private var userName = ""
    private var selectedItems = mutableListOf<Int>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_bad)

        incrementButton.setOnClickListener {
            counter++
            counterText.text = "Count: $counter"
        }

        saveButton.setOnClickListener {
            userName = nameField.text.toString()
            Toast.makeText(this, "Saved: $userName", Toast.LENGTH_SHORT).show()
        }
    }

    // No onSaveInstanceState() implementation
    // All data lost on rotation!
}
```

**After rotation:**
- `counter` resets to `0`
- `userName` becomes empty string
- `selectedItems` list is empty
- User has to re-enter everything

---

### - Good Example (Data Preserved)

```kotlin
class GoodViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    var counter: Int
        get() = savedStateHandle.get<Int>("counter") ?: 0
        set(value) = savedStateHandle.set("counter", value)

    var userName: String
        get() = savedStateHandle.get<String>("userName") ?: ""
        set(value) = savedStateHandle.set("userName", value)

    private val _selectedItems = MutableLiveData<List<Int>>(emptyList())
    val selectedItems: LiveData<List<Int>> = _selectedItems

    fun incrementCounter() {
        counter++
    }

    fun saveUserName(name: String) {
        userName = name
    }

    fun toggleItem(itemId: Int) {
        val current = _selectedItems.value ?: emptyList()
        _selectedItems.value = if (itemId in current) {
            current - itemId
        } else {
            current + itemId
        }
    }
}

class GoodActivity : AppCompatActivity() {
    private val viewModel: GoodViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_good)

        // Initialize UI with saved state
        counterText.text = "Count: ${viewModel.counter}"
        nameField.setText(viewModel.userName)

        // Observe data
        viewModel.selectedItems.observe(this) { items ->
            displaySelectedItems(items)
        }

        incrementButton.setOnClickListener {
            viewModel.incrementCounter()
            counterText.text = "Count: ${viewModel.counter}"
        }

        saveButton.setOnClickListener {
            val name = nameField.text.toString()
            viewModel.saveUserName(name)
            Toast.makeText(this, "Saved: $name", Toast.LENGTH_SHORT).show()
        }
    }
}
```

**After rotation:**
- - `counter` value preserved
- - `userName` preserved
- - `selectedItems` list intact
- - User experience seamless

---

## Solutions Summary

### 1. Use ViewModel for UI-related data

```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
    // Survives rotation automatically
}
```

### 2. Use SavedStateHandle for critical state

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    var importantData: String
        get() = savedStateHandle["data"] ?: ""
        set(value) = savedStateHandle.set("data", value)
    // Survives rotation AND process death
}
```

### 3. Add android:id to Views

```xml
<EditText
    android:id="@+id/inputField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
<!-- View state saved automatically -->
```

### 4. Implement onSaveInstanceState()

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("score", score)
}
```

### 5. Use Persistent Storage

```kotlin
// For data that should survive app restart
val prefs = getSharedPreferences("app_data", Context.MODE_PRIVATE)
prefs.edit {
    putString("user_id", userId)
    apply()
}
```

---

## Configuration Changes Lifecycle

```
User rotates screen
    ↓
onPause()
    ↓
onSaveInstanceState(outState)  ← SAVE DATA HERE!
    ↓
onStop()
    ↓
onDestroy()  ← Activity DESTROYED
    ↓
onCreate(savedInstanceState)  ← NEW Activity created
    ↓
onStart()
    ↓
onRestoreInstanceState(savedInstanceState)  ← RESTORE DATA HERE
    ↓
onResume()
```

---

## Testing Data Persistence

### Enable "Don't keep activities" in Developer Options

```
Settings → Developer Options → Don't keep activities (ON)
```

This simulates process death and helps test data persistence.

### Test Rotation

```kotlin
@Test
fun testRotation() {
    val scenario = ActivityScenario.launch(MainActivity::class.java)

    // Enter data
    onView(withId(R.id.nameField)).perform(typeText("John"))

    // Rotate
    scenario.onActivity { activity ->
        activity.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
    }

    // Verify data preserved
    onView(withId(R.id.nameField)).check(matches(withText("John")))
}
```

---

## Best Practices

1. - **Use ViewModel** for all UI-related data
2. - **Add SavedStateHandle** for critical state that must survive process death
3. - **Add android:id** to all Views that hold user input
4. - **Use persistent storage** (DataStore, Room) for data that should survive app restart
5. - **Test with rotation** during development
6. - **Enable "Don't keep activities"** during testing
7. - **Don't rely on** Activity/Fragment instance variables for important state
8. - **Don't make** unnecessary network calls after rotation

---

## Common Mistakes

| Mistake | Consequence | Solution |
|---------|-------------|----------|
| No ViewModel | Data reloaded on every rotation | Use ViewModel |
| No SavedStateHandle | Data lost on process death | Add SavedStateHandle |
| Views without ID | View state not restored | Add android:id |
| No onSaveInstanceState() | Transient data lost | Implement lifecycle callback |
| Async work in Activity | Operations interrupted/lost | Move to ViewModel |

---

## Summary

User data disappears on screen rotation because:

1. **Activity is destroyed and recreated**
2. **All instance variables are reset** to their initial values
3. **Async operations are interrupted** or references are lost
4. **Views without ID don't restore** their state

**Solutions:**
- Use **ViewModel** (survives rotation)
- Use **SavedStateHandle** (survives process death)
- Add **android:id** to Views (auto-save/restore)
- Implement **onSaveInstanceState()** (for transient data)
- Use **persistent storage** (DataStore, Room) for long-term data

**Modern Best Practice:**
```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    var uiState: UiState
        get() = savedStateHandle["state"] ?: UiState.default()
        set(value) = savedStateHandle.set("state", value)
}
```

This ensures data survives both configuration changes and process death.

---

## Ответ (RU)
Пользовательские данные исчезают при повороте экрана, потому что **Android уничтожает и пересоздаёт Activity** при изменении конфигурации. Если состояние не сохранено должным образом, все временные данные (переменные, пользовательский ввод, UI состояние) теряются.

### Почему Activity пересоздаётся

При повороте экрана Android:
1. **Уничтожает** текущую Activity (`onDestroy()`)
2. **Создаёт** новый экземпляр Activity (`onCreate()`)
3. **Загружает** соответствующий layout для новой ориентации

**Это означает:**
- Все нестатические переменные сбрасываются
- UI состояние может быть потеряно
- Асинхронные операции могут быть прерваны

### Основные причины потери данных

**1. Данные не сохранены**
```kotlin
// - Данные теряются при повороте
private var username: String = ""
private var score: Int = 0
```

**2. EditText без android:id**
```xml
<!-- - Состояние не сохраняется -->
<EditText
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<!-- - Состояние сохраняется автоматически -->
<EditText
    android:id="@+id/nameField"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**3. Не используется ViewModel**
```kotlin
// - БЕЗ ViewModel - данные теряются
class BadActivity : AppCompatActivity() {
    private var users: List<User> = emptyList()
}

// - С ViewModel - данные сохраняются
class GoodActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
}
```

### Решения

**1. Используйте ViewModel**
```kotlin
class MyViewModel : ViewModel() {
    val data = MutableLiveData<String>()
    // Переживает поворот автоматически
}
```

**2. Используйте SavedStateHandle**
```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    var data: String
        get() = savedStateHandle["data"] ?: ""
        set(value) = savedStateHandle.set("data", value)
    // Переживает поворот И смерть процесса
}
```

**3. Добавьте android:id к View**
```xml
<EditText android:id="@+id/field" />
```

**4. Реализуйте onSaveInstanceState()**
```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("score", score)
}
```

### Лучшие практики

1. - Используйте **ViewModel** для UI данных
2. - Добавьте **SavedStateHandle** для критического состояния
3. - Добавляйте **android:id** ко всем View с пользовательским вводом
4. - Используйте **постоянное хранилище** (DataStore, Room) для долгосрочных данных
5. - Тестируйте с поворотом экрана
6. - Не полагайтесь на переменные экземпляра Activity/Fragment

