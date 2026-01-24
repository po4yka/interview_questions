---
id: android-413
title: How To Save Activity State / Как сохранить состояние Activity
aliases:
- How To Save Activity State
- Save Activity State
- Как сохранить состояние Activity
- Сохранение состояния Activity
topic: android
subtopics:
- activity
- datastore
- lifecycle
question_kind: android
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
- q-in-which-thread-does-a-regular-service-run--android--medium
- q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android
- android/activity
- android/datastore
- android/lifecycle
- difficulty/medium
- state-management
sources: []
anki_cards:
- slug: android-413-0-en
  language: en
  anki_id: 1768381036507
  synced_at: '2026-01-23T16:45:06.363377'
- slug: android-413-0-ru
  language: ru
  anki_id: 1768381036532
  synced_at: '2026-01-23T16:45:06.364309'
---
# Вопрос (RU)

> Как сохранить состояние `Activity`?

# Question (EN)

> How to save `Activity` state?

---

## Ответ (RU)

Android предоставляет несколько механизмов для сохранения и восстановления состояния `Activity` при изменениях конфигурации (поворот экрана) и возможной смерти процесса. Выбор зависит от типа данных, их размера и требований к постоянству.

### 1. onSaveInstanceState() / onRestoreInstanceState()

Базовый механизм для сохранения легковесного UI-состояния.

**Основное использование (через onCreate или onRestoreInstanceState):**

```kotlin
class MainActivity : AppCompatActivity() {
    private var counter = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ Восстановление состояния (если есть сохранённый Bundle)
        counter = savedInstanceState?.getInt("COUNTER", 0) ?: 0
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // ✅ Сохранение критичных данных UI
        outState.putInt("COUNTER", counter)
    }

    // Опционально: onRestoreInstanceState вызывается после onStart, только если состояние было сохранено
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        counter = savedInstanceState.getInt("COUNTER", 0)
    }
}
```

**Сложные объекты через `Parcelable`:**

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
- Практический лимит около 1 МБ на `Bundle` (данные сериализуются через Binder)
- Только примитивы и `Parcelable`/`Serializable` объекты
- Восстановление происходит только когда система пересоздаёт `Activity` в рамках существующей задачи (например, после изменения конфигурации или управляемой смерти процесса); при ручном перезапуске приложения или иных сценариях убийства процесса сохранённое состояние может не быть восстановлено

### 2. `ViewModel` С SavedStateHandle (рекомендуется Для UI-состояния)

Современный подход для хранения UI-состояния:
- обычный `ViewModel` переживает только изменения конфигурации;
- значения, сохранённые в `SavedStateHandle`, могут быть восстановлены после смерти процесса, если они явно записаны и укладываются в допустимый объём сохранённого состояния (аналогично `onSaveInstanceState`).

**Базовое использование (упрощённый пример):**

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    // ✅ Сохранение/восстановление через SavedStateHandle
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
    // На практике нужен ViewModelProvider.Factory (или Hilt/другой DI),
    // чтобы MyViewModel с SavedStateHandle корректно создавался.
    private val viewModel: MyViewModel by viewModels { /* SavedStateViewModelFactory / Hilt */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userName.observe(this) { name ->
            binding.nameText.text = name
        }
    }
}
```

**С `StateFlow` (современный подход):**

```kotlin
class ModernViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    private val _counter = MutableStateFlow(savedStateHandle.get<Int>("counter") ?: 0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    init {
        // ✅ Синхронизация с SavedStateHandle: сохраняем только нужные значения
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

Важно: `ViewModel` сам по себе не переживает смерть процесса. После убийства процесса при пересоздании `Activity` будет создан новый экземпляр `ViewModel`, и только данные, сохранённые через `SavedStateHandle` (т.е. прошедшие через механизм сохранённого состояния, аналогичный `onSaveInstanceState`), могут быть восстановлены.

### 3. Постоянное Хранилище

Для данных, которые должны пережить закрытие приложения и не зависят от жизненного цикла отдельной `Activity`.

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

**`Room` (для больших объёмов данных):**

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

Здесь DataStore и `Room` выступают как примеры устойчивого хранилища. Аналогичные свойства (переживают закрытие приложения и смерть процесса) имеют и другие постоянные механизмы (например, `SharedPreferences`, файлы), при условии, что данные были записаны на диск.

### 4. Сравнение Подходов

| Подход | Поворот экрана | Смерть процесса | Закрытие приложения | Применение |
|--------|----------------|-----------------|---------------------|------------|
| **onSaveInstanceState** | ✅ | ⚠️ зависит от сценария, лимит по размеру | ❌ | Легковесное UI-состояние |
| **`ViewModel` (без SavedState)** | ✅ | ❌ | ❌ | UI-данные во время сессии |
| **`ViewModel` + SavedStateHandle** | ✅ | ✅* | ❌ | UI-состояние, важное для восстановления; *только для явно сохранённых ключей в рамках `Bundle`-лимитов |
| **DataStore** | ✅ | ✅ | ✅ | Настройки, preferences (как один из вариантов постоянного хранилища) |
| **`Room`** | ✅ | ✅ | ✅ | Большие наборы данных, сложные структуры |

### 5. Лучшие Практики

**Комбинирование подходов:**

```kotlin
class UserActivity : AppCompatActivity() {

    // ✅ ViewModel для UI-состояния
    private val viewModel: UserViewModel by viewModels()

    // ✅ Постоянное хранилище для критичных данных (настройки и пр.)
    private lateinit var settingsRepository: SettingsRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Пример: загрузка настроек из постоянного хранилища
        lifecycleScope.launch {
            settingsRepository.darkMode.collect { isDarkMode ->
                applyDarkMode(isDarkMode)
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
- Используйте `ViewModel` + `SavedStateHandle` для большинства важного UI-состояния, которое должно восстановиться после поворота и потенциальной смерти процесса (через механизм сохранённого состояния).
- Используйте DataStore, `Room` или другие постоянные механизмы для данных, которые должны переживать закрытие приложения.
- Избегайте хранения больших объектов в `onSaveInstanceState` (лимит по размеру `Bundle` ~1 МБ).
- Не сохраняйте `Context`, `View`, `Activity` в `ViewModel`.

## Answer (EN)

Android provides multiple mechanisms to save and restore `Activity` state across configuration changes (like screen rotation) and possible process death. The choice depends on data type, size, and persistence requirements.

### 1. onSaveInstanceState() / onRestoreInstanceState()

Basic mechanism for saving lightweight UI state.

**Basic usage (via onCreate or onRestoreInstanceState):**

```kotlin
class MainActivity : AppCompatActivity() {
    private var counter = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // ✅ Restore state if a saved Bundle is available
        counter = savedInstanceState?.getInt("COUNTER", 0) ?: 0
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // ✅ Save critical UI data
        outState.putInt("COUNTER", counter)
    }

    // Optional: onRestoreInstanceState is called after onStart only if there is saved state
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        counter = savedInstanceState.getInt("COUNTER", 0)
    }
}
```

**Complex objects via `Parcelable`:**

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
- Practical limit of about 1 MB per `Bundle` (data goes through Binder)
- Only primitives and `Parcelable`/`Serializable` objects
- State is restored only when the system recreates the `Activity` as part of the same task/flow (e.g., configuration change or managed process recreation); on manual app relaunch or other kill scenarios the previously saved instance state may not be restored

### 2. `ViewModel` With SavedStateHandle (recommended for UI state)

Modern approach for holding UI state:
- a regular `ViewModel` survives only configuration changes;
- values written into `SavedStateHandle` can be restored after process death if they are explicitly saved and fit into the allowed saved-state size (similar to `onSaveInstanceState`).

**Basic usage (simplified example):**

```kotlin
class MyViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    // ✅ Save/restore via SavedStateHandle
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
    // In practice you need a ViewModelProvider.Factory (or Hilt/other DI)
    // so that MyViewModel with SavedStateHandle is created correctly.
    private val viewModel: MyViewModel by viewModels { /* SavedStateViewModelFactory / Hilt */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.userName.observe(this) { name ->
            binding.nameText.text = name
        }
    }
}
```

**With `StateFlow` (modern approach):**

```kotlin
class ModernViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {

    private val _counter = MutableStateFlow(savedStateHandle.get<Int>("counter") ?: 0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    init {
        // ✅ Sync with SavedStateHandle: persist only required values
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

Important: a `ViewModel` itself does not survive process death. After the process is killed and the `Activity` is recreated, a new `ViewModel` instance is created; only data persisted via `SavedStateHandle` (i.e., written into the saved-state mechanism similar to `onSaveInstanceState`) can be restored.

### 3. Persistent Storage

For data that needs to survive app termination and is not tied to a specific `Activity` lifecycle.

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

**`Room` (for large datasets):**

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

Here DataStore and `Room` are examples of persistent storage. Other mechanisms (e.g., `SharedPreferences`, files) also survive app close and process death as long as data is written to disk.

### 4. Comparison of Approaches

| Approach | Survives Rotation | Survives Process Death | Survives App Close | Use Case |
|----------|------------------|------------------------|--------------------|----------|
| **onSaveInstanceState** | ✅ | ⚠️ scenario-dependent, size-limited | ❌ | Lightweight UI state |
| **`ViewModel` (no SavedState)** | ✅ | ❌ | ❌ | UI-related data during session |
| **`ViewModel` + SavedStateHandle** | ✅ | ✅* | ❌ | UI state important for restoration; *only for explicitly saved keys within `Bundle` limits |
| **DataStore** | ✅ | ✅ | ✅ | Settings, preferences (one of persistent options) |
| **`Room`** | ✅ | ✅ | ✅ | Large datasets, complex data |

### 5. Best Practices

**Combining approaches:**

```kotlin
class UserActivity : AppCompatActivity() {

    // ✅ ViewModel for UI state
    private val viewModel: UserViewModel by viewModels()

    // ✅ Persistent storage for critical data (settings, etc.)
    private lateinit var settingsRepository: SettingsRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Example: load settings from persistent storage
        lifecycleScope.launch {
            settingsRepository.darkMode.collect { isDarkMode ->
                applyDarkMode(isDarkMode)
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
- Use `ViewModel` + `SavedStateHandle` for most important UI state that should be restored after rotation and potential process death (via the saved-state mechanism).
- Use DataStore, `Room`, or other persistent mechanisms for data that must survive app closure.
- Avoid storing large objects in `onSaveInstanceState` (`Bundle` size is limited to about 1 MB).
- Never store `Context`, `View`, `Activity` in `ViewModel`.

---

## Дополнительные Вопросы (RU)

1. Каков практический лимит по размеру данных, сохраняемых в `Bundle` через `onSaveInstanceState`?
2. Чем `SavedStateHandle` отличается от обычного состояния во `ViewModel` при убийстве процесса?
3. В каких случаях следует использовать `DataStore` вместо `SharedPreferences`?
4. Может ли `ViewModel` пережить смерть процесса без `SavedStateHandle`?
5. Что произойдет с сохраненным состоянием, если пользователь очистит данные приложения в настройках?

## Follow-ups

1. What is the practical size limit for data stored in the `onSaveInstanceState` `Bundle`?
2. How does `SavedStateHandle` differ from regular `ViewModel` state when the process is killed?
3. When should you choose `DataStore` over `SharedPreferences`?
4. Can a `ViewModel` survive process death without `SavedStateHandle`?
5. What happens to saved state when the user clears app data from system Settings?

## References

- [[c-activity-lifecycle]]
- [[c-coroutines]]
- https://developer.android.com/topic/libraries/architecture/saving-states
- https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate
- https://developer.android.com/topic/libraries/architecture/datastore

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] - `Activity` lifecycle basics
- [[q-android-components-besides-activity--android--easy]] - Android core components

### Related (Medium)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - `Activity` memory management
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment` state management
- [[q-single-activity-pros-cons--android--medium]] - Single-activity architecture

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Advanced architectural patterns
