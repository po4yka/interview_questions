---
id: 20251012-12271195
title: "Save Data Outside Fragment / Сохранение данных вне Fragment"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/data-storage, architecture, data-persistence, data-storage, fragments, room, sharedpreferences, viewmodel, difficulty/medium]
---

# Question (EN)

> How can you save data outside a fragment?

# Вопрос (RU)

> Каким образом можно сохранить данные за пределами фрагмента?

---

## Answer (EN)

To save data **outside a fragment** (so it persists beyond the fragment's lifecycle), you can use several methods depending on your requirements.

## Main Approaches

### 1. SharedPreferences

**Purpose:** Store simple key-value data that survives fragment recreation

**Use for:** User preferences, settings, flags, small data

```kotlin
class SettingsFragment : Fragment() {
    private lateinit var prefs: SharedPreferences

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        prefs = requireContext().getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

        // Save data
        saveButton.setOnClickListener {
            prefs.edit()
                .putString("username", usernameEditText.text.toString())
                .putBoolean("notifications_enabled", notificationsSwitch.isChecked)
                .apply()
        }

        // Load data
        val username = prefs.getString("username", "")
        val notificationsEnabled = prefs.getBoolean("notifications_enabled", true)
    }
}
```

---

### 2. Room Database

**Purpose:** Store structured data with relationships

**Use for:** Complex data, lists, entities with relationships

```kotlin
// Entity
@Entity(tableName = "notes")
data class Note(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val title: String,
    val content: String,
    val timestamp: Long = System.currentTimeMillis()
)

// DAO
@Dao
interface NoteDao {
    @Query("SELECT * FROM notes ORDER BY timestamp DESC")
    fun getAllNotes(): Flow<List<Note>>

    @Insert
    suspend fun insert(note: Note)

    @Delete
    suspend fun delete(note: Note)
}

// Database
@Database(entities = [Note::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun noteDao(): NoteDao
}

// Fragment usage
class NotesFragment : Fragment() {
    private val viewModel: NotesViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe data
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.notes.collect { notes ->
                adapter.submitList(notes)
            }
        }

        // Save new note
        saveButton.setOnClickListener {
            viewModel.addNote(
                title = titleEditText.text.toString(),
                content = contentEditText.text.toString()
            )
        }
    }
}

// ViewModel
class NotesViewModel(private val noteDao: NoteDao) : ViewModel() {
    val notes: Flow<List<Note>> = noteDao.getAllNotes()

    fun addNote(title: String, content: String) {
        viewModelScope.launch {
            noteDao.insert(Note(title = title, content = content))
        }
    }
}
```

---

### 3. ViewModel (with ViewModelFactory)

**Purpose:** Survive configuration changes (rotation, language change)

**Use for:** Temporary data that should survive rotation but not process death

**Activity-scoped ViewModel (shared between fragments):**

```kotlin
class UserProfileViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun updateUser(user: User) {
        _userData.value = user
    }
}

// Fragment A - writes data
class ProfileEditFragment : Fragment() {
    // Activity-scoped ViewModel (shared)
    private val viewModel: UserProfileViewModel by activityViewModels()

    private fun saveProfile() {
        val user = User(
            name = nameEditText.text.toString(),
            email = emailEditText.text.toString()
        )
        viewModel.updateUser(user)  // Saved in ViewModel
    }
}

// Fragment B - reads data
class ProfileDisplayFragment : Fragment() {
    // Same ViewModel instance (activity-scoped)
    private val viewModel: UserProfileViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.userData.observe(viewLifecycleOwner) { user ->
            nameTextView.text = user.name
            emailTextView.text = user.email
        }
    }
}
```

**SavedStateHandle (survives process death):**

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    // Survives process death
    var username: String
        get() = savedStateHandle.get<String>("username") ?: ""
        set(value) { savedStateHandle.set("username", value) }

    // LiveData from SavedStateHandle
    val usernameLiveData: LiveData<String> = savedStateHandle.getLiveData("username", "")
}
```

---

### 4. Files (Internal/External Storage)

**Purpose:** Store larger data, documents, media

```kotlin
class DocumentFragment : Fragment() {

    // Save to internal storage
    private fun saveToFile(content: String) {
        val filename = "document.txt"
        requireContext().openFileOutput(filename, Context.MODE_PRIVATE).use { output ->
            output.write(content.toByteArray())
        }
    }

    // Read from internal storage
    private fun readFromFile(): String {
        val filename = "document.txt"
        return requireContext().openFileInput(filename).bufferedReader().use {
            it.readText()
        }
    }

    // Save to external storage (app-specific directory)
    private fun saveToExternalFile(content: String) {
        val file = File(requireContext().getExternalFilesDir(null), "export.txt")
        file.writeText(content)
    }
}
```

---

### 5. Repository Pattern (Recommended Architecture)

**Purpose:** Central data source, combines multiple storage methods

```kotlin
// Repository
class UserRepository(
    private val userDao: UserDao,
    private val prefs: SharedPreferences,
    private val api: ApiService
) {
    // Database
    fun getUsers(): Flow<List<User>> = userDao.getAllUsers()

    suspend fun saveUser(user: User) {
        userDao.insert(user)
    }

    // SharedPreferences
    fun saveAuthToken(token: String) {
        prefs.edit().putString("auth_token", token).apply()
    }

    fun getAuthToken(): String? {
        return prefs.getString("auth_token", null)
    }

    // Network + Cache
    suspend fun refreshUsers() {
        val users = api.fetchUsers()
        userDao.deleteAll()
        userDao.insertAll(users)
    }
}

// ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    val users: Flow<List<User>> = repository.getUsers()

    fun addUser(name: String, email: String) {
        viewModelScope.launch {
            repository.saveUser(User(name = name, email = email))
        }
    }
}

// Fragment
class UserListFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels {
        UserViewModelFactory(repository)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.users.collect { users ->
                adapter.submitList(users)
            }
        }
    }
}
```

---

## Comparison Table

| Method                | Persistence | Survives Rotation | Survives Process Death | Use Case         |
| --------------------- | ----------- | ----------------- | ---------------------- | ---------------- |
| **SharedPreferences** | - Permanent | - Yes             | - Yes                  | Settings, flags  |
| **Room Database**     | - Permanent | - Yes             | - Yes                  | Structured data  |
| **ViewModel**         | - Temporary | - Yes             | - No                   | UI state         |
| **SavedStateHandle**  | - Limited   | - Yes             | - Yes                  | UI state (small) |
| **Files**             | - Permanent | - Yes             | - Yes                  | Documents, media |

## Best Practices

**1. Use ViewModel + Repository pattern:**

```kotlin
// Fragment → ViewModel → Repository → Data Source
Fragment
  ↓
ViewModel (UI logic, survives rotation)
  ↓
Repository (data logic, caching)
  ↓
Data Sources (Room, SharedPreferences, Network)
```

**2. Choose storage based on requirements:**

```kotlin
when {
    // Small settings
    data is simple key-value → SharedPreferences

    // Structured data
    data has relationships → Room Database

    // Temporary UI state
    survives rotation only → ViewModel

    // Large files
    data is media/documents → Files

    // Complex app
    multiple sources → Repository pattern
}
```

**3. Combine multiple approaches:**

```kotlin
class UserRepository(
    private val userDao: UserDao,           // Room for user entities
    private val prefs: SharedPreferences,   // Prefs for settings
    private val fileManager: FileManager    // Files for avatars
) {
    suspend fun saveUserProfile(user: User, avatar: Bitmap) {
        userDao.insert(user)                    // Save to DB
        prefs.edit().putLong("last_sync", System.currentTimeMillis()).apply()
        fileManager.saveAvatar(user.id, avatar) // Save avatar to file
    }
}
```

## Summary

**Methods to save data outside fragments:**

1. **SharedPreferences** - Simple key-value data
2. **Room Database** - Structured, relational data
3. **ViewModel** - Temporary data (survives rotation)
4. **SavedStateHandle** - UI state (survives process death)
5. **Files** - Large files, documents, media

**Recommended architecture:**
Fragment → ViewModel → Repository → (Room + SharedPreferences + Files)

## Ответ (RU)

Для сохранения данных за пределами фрагмента в Android можно использовать несколько методов. Основные способы включают SharedPreferences, базы данных SQLite, Room, файлы и ViewModel с ViewModelFactory. SharedPreference используется для хранения небольших порций данных в виде пар ключ значение. Это удобно для хранения настроек пользователя или состояния приложения. SQLite это встроенная реляционная база данных которая позволяет хранить структурированные данные для работы с ней используются sql запросы. Room это библиотека которая упрощает работу с sqlite предоставляя абстракцию в виде аннотаций и dao data access objects.

---

## Related Questions

## Follow-ups

-   When should you use DataStore instead of SharedPreferences?
-   How do you share data between fragments using activity-scoped ViewModel?
-   What are best practices for repository and caching layers?

## References

-   `https://developer.android.com/topic/libraries/architecture/viewmodel` — ViewModel
-   `https://developer.android.com/training/data-storage/shared-preferences` — SharedPreferences
-   `https://developer.android.com/topic/libraries/architecture/datastore` — DataStore
-   `https://developer.android.com/training/data-storage/room` — Room

### Related (Medium)

-   [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]]
-   [[q-how-can-data-be-saved-beyond-the-fragment-scope--android--medium]]
