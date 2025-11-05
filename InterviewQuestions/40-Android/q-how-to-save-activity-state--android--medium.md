---
id: android-413
title: "How To Save Activity State / Как сохранить состояние Activity"
aliases: ["How To Save Activity State", "Save Activity State", "Как сохранить состояние Activity", "Сохранение состояния Activity"]
topic: android
subtopics: [activity, architecture-mvvm, datastore, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-in-which-thread-does-a-regular-service-run--android--medium, q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android, android/activity, android/architecture-mvvm, android/datastore, android/lifecycle, difficulty/medium, state-management]
sources: []
date created: Saturday, November 1st 2025, 12:46:54 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

> Как сохранить состояние Activity?

# Question (EN)

> How to save Activity state?

---

## Ответ (RU)

Android предоставляет несколько механизмов для сохранения и восстановления состояния Activity при изменениях конфигурации (поворот экрана) и завершении процесса. Выбор зависит от типа данных, их размера и требований к постоянству.

### 1. onSaveInstanceState() / onRestoreInstanceState()

Базовый механизм для сохранения легковесного UI-состояния.

**Основное использование:**

```kotlin
class MainActivity : AppCompatActivity() {
    private var counter = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ Восстановление состояния
        counter = savedInstanceState?.getInt("COUNTER", 0) ?: 0
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // ✅ Сохранение критичных данных UI
        outState.putInt("COUNTER", counter)
    }
}
```

**Сложные объекты через Parcelable:**

```kotlin
import kotlinx.parcelize.Parcelize

@Parcelize
data class UserProfile(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

class ProfileActivity : AppCompatActivity() {
    private var profile: UserProfile? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        profile = savedInstanceState?.getParcelable("PROFILE")
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putParcelable("PROFILE", profile)
    }
}
```

**Ограничения:**
- Максимум ~1 МБ данных
- Только примитивы и Parcelable/Serializable объекты
- Может не сработать при смерти процесса в фоне

### 2. ViewModel С SavedStateHandle (рекомендуется)

Современный подход, переживающий и изменения конфигурации, и смерть процесса.

**Базовое использование:**

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    // ✅ Автоматическое сохранение/восстановление
    var counter: Int
        get() = savedStateHandle.get<Int>("counter") ?: 0
        set(value) = savedStateHandle.set("counter", value)

    // ✅ С LiveData
    val userName: MutableLiveData<String> =
        savedStateHandle.getLiveData("userName", "")

    fun incrementCounter() {
        counter++
    }
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userName.observe(this) { name ->
            binding.nameText.text = name
        }
    }
}
```

**С StateFlow (современный подход):**

```kotlin
class ModernViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    private val _counter = MutableStateFlow(savedStateHandle.get<Int>("counter") ?: 0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    init {
        // ✅ Автоматическая синхронизация с SavedStateHandle
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
```

### 3. Постоянное Хранилище

Для данных, которые должны пережить закрытие приложения.

**DataStore (рекомендуется для настроек):**

```kotlin
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore

val Context.dataStore by preferencesDataStore(name = "settings")

class SettingsRepository(private val context: Context) {

    private val DARK_MODE = booleanPreferencesKey("dark_mode")

    val darkMode: Flow<Boolean> = context.dataStore.data
        .map { it[DARK_MODE] ?: false }

    suspend fun setDarkMode(enabled: Boolean) {
        context.dataStore.edit { it[DARK_MODE] = enabled }
    }
}
```

**Room (для больших объемов данных):**

```kotlin
@Entity(tableName = "user_state")
data class UserState(
    @PrimaryKey val id: Int = 1,
    val scrollPosition: Int,
    val selectedTab: Int
)

@Dao
interface UserStateDao {
    @Query("SELECT * FROM user_state WHERE id = 1")
    fun getUserState(): Flow<UserState?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveUserState(state: UserState)
}
```

### 4. Сравнение Подходов

| Подход | Поворот экрана | Смерть процесса | Закрытие приложения | Применение |
|--------|----------------|-----------------|---------------------|------------|
| **onSaveInstanceState** | ✅ | ⚠️ ограниченно | ❌ | Легковесное UI-состояние |
| **ViewModel (без SavedState)** | ✅ | ❌ | ❌ | UI-данные во время сессии |
| **ViewModel + SavedStateHandle** | ✅ | ✅ | ❌ | UI-состояние + смерть процесса |
| **DataStore** | ✅ | ✅ | ✅ | Настройки, preferences |
| **Room** | ✅ | ✅ | ✅ | Большие наборы данных |

### 5. Лучшие Практики

**Комбинирование подходов:**

```kotlin
class UserActivity : AppCompatActivity() {

    // ✅ ViewModel для UI-состояния
    private val viewModel: UserViewModel by viewModels()

    // ✅ Постоянное хранилище для критичных данных
    private lateinit var dataStore: SettingsRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Загрузка настроек из постоянного хранилища
        lifecycleScope.launch {
            dataStore.userSettings.collect { settings ->
                applySettings(settings)
            }
        }

        // UI-состояние из ViewModel
        viewModel.uiState.observe(this) { state ->
            updateUI(state)
        }
    }
}
```

**Рекомендации:**
- ViewModel + SavedStateHandle для большинства UI-состояния
- DataStore или Room для постоянных данных
- Избегайте хранения больших объектов в onSaveInstanceState (лимит ~1 МБ)
- Не сохраняйте Context, View, Activity в ViewModel

## Answer (EN)

Android provides multiple mechanisms to save and restore Activity state across configuration changes (like screen rotation) and process death. The choice depends on data type, size, and persistence requirements.

### 1. onSaveInstanceState() / onRestoreInstanceState()

Basic mechanism for saving lightweight UI state.

**Basic usage:**

```kotlin
class MainActivity : AppCompatActivity() {
    private var counter = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ Restore state
        counter = savedInstanceState?.getInt("COUNTER", 0) ?: 0
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // ✅ Save critical UI data
        outState.putInt("COUNTER", counter)
    }
}
```

**Complex objects via Parcelable:**

```kotlin
import kotlinx.parcelize.Parcelize

@Parcelize
data class UserProfile(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

class ProfileActivity : AppCompatActivity() {
    private var profile: UserProfile? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        profile = savedInstanceState?.getParcelable("PROFILE")
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putParcelable("PROFILE", profile)
    }
}
```

**Limitations:**
- Maximum ~1 MB of data
- Only primitives and Parcelable/Serializable objects
- May not survive process death in background

### 2. ViewModel with SavedStateHandle (recommended)

Modern approach surviving both configuration changes and process death.

**Basic usage:**

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    // ✅ Automatic save/restore
    var counter: Int
        get() = savedStateHandle.get<Int>("counter") ?: 0
        set(value) = savedStateHandle.set("counter", value)

    // ✅ With LiveData
    val userName: MutableLiveData<String> =
        savedStateHandle.getLiveData("userName", "")

    fun incrementCounter() {
        counter++
    }
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userName.observe(this) { name ->
            binding.nameText.text = name
        }
    }
}
```

**With StateFlow (modern approach):**

```kotlin
class ModernViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    private val _counter = MutableStateFlow(savedStateHandle.get<Int>("counter") ?: 0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    init {
        // ✅ Automatic sync with SavedStateHandle
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
```

### 3. Persistent Storage

For data that needs to survive app termination.

**DataStore (recommended for settings):**

```kotlin
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore

val Context.dataStore by preferencesDataStore(name = "settings")

class SettingsRepository(private val context: Context) {

    private val DARK_MODE = booleanPreferencesKey("dark_mode")

    val darkMode: Flow<Boolean> = context.dataStore.data
        .map { it[DARK_MODE] ?: false }

    suspend fun setDarkMode(enabled: Boolean) {
        context.dataStore.edit { it[DARK_MODE] = enabled }
    }
}
```

**Room (for large datasets):**

```kotlin
@Entity(tableName = "user_state")
data class UserState(
    @PrimaryKey val id: Int = 1,
    val scrollPosition: Int,
    val selectedTab: Int
)

@Dao
interface UserStateDao {
    @Query("SELECT * FROM user_state WHERE id = 1")
    fun getUserState(): Flow<UserState?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveUserState(state: UserState)
}
```

### 4. Comparison of Approaches

| Approach | Survives Rotation | Survives Process Death | Survives App Close | Use Case |
|----------|------------------|----------------------|-------------------|----------|
| **onSaveInstanceState** | ✅ | ⚠️ limited | ❌ | Lightweight UI state |
| **ViewModel (no SavedState)** | ✅ | ❌ | ❌ | UI-related data during session |
| **ViewModel + SavedStateHandle** | ✅ | ✅ | ❌ | UI state + process death |
| **DataStore** | ✅ | ✅ | ✅ | Settings, preferences |
| **Room** | ✅ | ✅ | ✅ | Large datasets |

### 5. Best Practices

**Combining approaches:**

```kotlin
class UserActivity : AppCompatActivity() {

    // ✅ ViewModel for UI state
    private val viewModel: UserViewModel by viewModels()

    // ✅ Persistent storage for critical data
    private lateinit var dataStore: SettingsRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Load settings from persistent storage
        lifecycleScope.launch {
            dataStore.userSettings.collect { settings ->
                applySettings(settings)
            }
        }

        // UI state from ViewModel
        viewModel.uiState.observe(this) { state ->
            updateUI(state)
        }
    }
}
```

**Recommendations:**
- Use ViewModel + SavedStateHandle for most UI state
- Use DataStore or Room for persistent data
- Avoid storing large objects in onSaveInstanceState (limit ~1 MB)
- Never store Context, View, Activity in ViewModel

---

## Follow-ups

1. What is the maximum size limit for data stored in onSaveInstanceState Bundle?
2. How does SavedStateHandle differ from regular ViewModel state when process is killed?
3. When should you choose DataStore over SharedPreferences?
4. Can ViewModel survive process death without SavedStateHandle?
5. What happens to saved state when user clears app data from Settings?

## References

- [[c-viewmodel]] - ViewModel architecture component
- [[c-lifecycle]] - Android lifecycle management
- [[c-coroutines]] - Kotlin coroutines for async operations
- https://developer.android.com/topic/libraries/architecture/saving-states
- https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate
- [DataStore](https://developer.android.com/topic/libraries/architecture/datastore)


## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle basics
- [[q-android-components-besides-activity--android--easy]] - Android core components

### Related (Medium)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Activity memory management
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment state management
- [[q-single-activity-pros-cons--android--medium]] - Single-activity architecture

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Advanced architectural patterns
