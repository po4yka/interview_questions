---
id: android-139
title: "Save Data Outside Fragment / Сохранение данных вне Fragment"
aliases: ["Save Data Outside Fragment", "Сохранение данных вне Fragment"]
topic: android
subtopics: [architecture-mvvm, lifecycle, room]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-components, q-what-is-layout-types-and-when-to-use--android--easy]
created: 2024-10-15
updated: 2025-11-10
sources: []
tags: [android/architecture-mvvm, android/lifecycle, android/room, data-persistence, datastore, difficulty/medium, fragments, sharedpreferences, viewmodel]

date created: Saturday, November 1st 2025, 12:47:03 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)

> Каким образом можно сохранить данные за пределами фрагмента?

# Question (EN)

> How can you save data outside a fragment?

---

## Ответ (RU)

Для сохранения данных за пределами фрагмента используется несколько подходов в зависимости от требований персистентности, объема данных и необходимости восстановления после убийства процесса.

### Основные Подходы

**1. SharedPreferences**
Для простых настроек (key-value пары). Данные записываются на диск, переживают пересоздание фрагмента, активити и смерть процесса.

```kotlin
// ✅ Подходит для настроек и флагов
val prefs = requireContext().getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit()
    .putString("username", username)
    .putBoolean("notifications", true)
    .apply()  // ✅ Асинхронная запись
```

**2. Room Database**
Для структурированных данных со связями. Полноценная абстракция над SQLite с compile-time проверками запросов. Данные хранятся на диске и сохраняются при пересоздании компонентов и смерти процесса.

```kotlin
// ✅ Repository паттерн для доступа к данным
class UserRepository(private val userDao: UserDao) {
    val users: Flow<List<User>> = userDao.getAllUsers()

    suspend fun insert(user: User) = userDao.insert(user)
}

// Fragment получает данные через ViewModel
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.users.collect { users ->
                adapter.submitList(users)  // ✅ Реактивное обновление UI
            }
        }
    }
}
```

**3. `ViewModel` и SavedStateHandle**
Для временных UI-состояний и шаринга данных между фрагментами в рамках одной `Activity`.
- `ViewModel` переживает изменения конфигурации (например, ротацию), но не смерть процесса.
- SavedStateHandle позволяет явно сохранять небольшой объем состояния так, чтобы его можно было восстановить после смерти процесса (на основе SavedInstanceState).

```kotlin
// ✅ Activity-scoped ViewModel для шаринга между фрагментами
class SharedViewModel(private val state: SavedStateHandle) : ViewModel() {
    private val _userData = MutableStateFlow(state.get<User?>("user"))
    val userData: StateFlow<User?> = _userData.asStateFlow()

    fun setUser(user: User?) {
        _userData.value = user
        state["user"] = user  // ✅ сохраняем минимальное состояние в SavedStateHandle
    }
}

// Fragment A
private val viewModel: SharedViewModel by activityViewModels()

// Fragment B получает те же данные
private val viewModel: SharedViewModel by activityViewModels()
```

**4. DataStore**
Современная замена SharedPreferences с корутинами и (в случае Proto DataStore) явной схемой. Данные хранятся на диске и переживают пересоздание компонентов и смерть процесса.

```kotlin
// ✅ Type-safe, асинхронный, поддерживает миграцию
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

class SettingsRepository(private val dataStore: DataStore<Preferences>) {
    val userSettings: Flow<UserSettings> = dataStore.data.map { prefs ->
        UserSettings(
            username = prefs[USERNAME_KEY] ?: "",
            notificationsEnabled = prefs[NOTIFICATIONS_KEY] ?: true
        )
    }

    suspend fun updateUsername(name: String) {
        dataStore.edit { prefs ->
            prefs[USERNAME_KEY] = name
        }
    }
}
```

### Сравнение Методов

| Метод             | Персистентность | Переживает ротацию | Переживает смерть процесса | Use Case                    |
| ----------------- | --------------- | ------------------ | -------------------------- | --------------------------- |
| SharedPreferences | Постоянная      | Да                 | Да                         | Настройки, флаги            |
| DataStore         | Постоянная      | Да                 | Да                         | Настройки (современный API) |
| Room              | Постоянная      | Да                 | Да                         | Структурированные данные    |
| `ViewModel`       | Временная       | Да                 | Нет                        | UI-состояние                |
| SavedStateHandle  | Ограниченная    | Да                 | Да                         | Малый UI-state, ключевые ID |

### Рекомендуемая Архитектура

```kotlin
// ✅ Слоистая архитектура для управления данными
Fragment
  ↓
ViewModel (UI логика, переживает ротацию)
  ↓
Repository (управление источниками данных)
  ↓
Data Sources (Room, DataStore, Network)
```

**Ключевые принципы:**
- Используйте Repository pattern для централизованного доступа к данным
- `ViewModel` для UI-состояний и бизнес-логики
- Room + DataStore/SharedPreferences для персистентных данных
- SavedStateHandle только для минимального UI-состояния, которое нужно восстановить после смерти процесса (например, id выбранного элемента)

Также см. [[c-android-components]] для общего контекста архитектуры Android.

## Answer (EN)

Data persistence outside a fragment depends on requirements for scope, durability, and process-death recovery.

### Core Approaches

**1. SharedPreferences**
For simple settings (key-value pairs). Data is stored on disk and survives fragment/activity recreation and process death.

```kotlin
// ✅ Good for settings and flags
val prefs = requireContext().getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit()
    .putString("username", username)
    .putBoolean("notifications", true)
    .apply()  // ✅ Asynchronous write
```

**2. Room Database**
For structured data with relationships. A high-level abstraction over SQLite with compile-time query verification. Data is persisted on disk and survives component recreation and process death.

```kotlin
// ✅ Repository pattern for data access
class UserRepository(private val userDao: UserDao) {
    val users: Flow<List<User>> = userDao.getAllUsers()

    suspend fun insert(user: User) = userDao.insert(user)
}

// Fragment receives data via ViewModel
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.users.collect { users ->
                adapter.submitList(users)  // ✅ Reactive UI updates
            }
        }
    }
}
```

**3. `ViewModel` and SavedStateHandle**
For temporary UI state and sharing data between fragments within the same `Activity`.
- `ViewModel` survives configuration changes (e.g., rotation) but not process death.
- SavedStateHandle lets you explicitly save a small subset of state so it can be restored after process death (backed by SavedInstanceState).

```kotlin
// ✅ Activity-scoped ViewModel for sharing between fragments
class SharedViewModel(private val state: SavedStateHandle) : ViewModel() {
    private val _userData = MutableStateFlow(state.get<User?>("user"))
    val userData: StateFlow<User?> = _userData.asStateFlow()

    fun setUser(user: User?) {
        _userData.value = user
        state["user"] = user  // ✅ persist minimal state in SavedStateHandle
    }
}

// Fragment A
private val viewModel: SharedViewModel by activityViewModels()

// Fragment B gets the same data
private val viewModel: SharedViewModel by activityViewModels()
```

**4. DataStore**
Modern replacement for SharedPreferences with coroutines and, for Proto DataStore, an explicit schema. Data is stored on disk and survives component recreation and process death.

```kotlin
// ✅ Type-safe, async, supports migration
val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

class SettingsRepository(private val dataStore: DataStore<Preferences>) {
    val userSettings: Flow<UserSettings> = dataStore.data.map { prefs ->
        UserSettings(
            username = prefs[USERNAME_KEY] ?: "",
            notificationsEnabled = prefs[NOTIFICATIONS_KEY] ?: true
        )
    }

    suspend fun updateUsername(name: String) {
        dataStore.edit { prefs ->
            prefs[USERNAME_KEY] = name
        }
    }
}
```

### Method Comparison

| Method            | Persistence | Survives Rotation | Survives Process Death | Use Case                       |
| ----------------- | ----------- | ----------------- | ---------------------- | ------------------------------ |
| SharedPreferences | Persistent  | Yes               | Yes                    | Settings, flags                |
| DataStore         | Persistent  | Yes               | Yes                    | Settings (modern API)          |
| Room              | Persistent  | Yes               | Yes                    | Structured/relational data     |
| `ViewModel`       | Temporary   | Yes               | No                     | UI state                       |
| SavedStateHandle  | Limited     | Yes               | Yes                    | Small UI state, key IDs, etc.  |

### Recommended Architecture

```kotlin
// ✅ Layered architecture for data management
Fragment
  ↓
ViewModel (UI logic, survives rotation)
  ↓
Repository (manages data sources)
  ↓
Data Sources (Room, DataStore, Network)
```

**Key Principles:**
- Use Repository pattern for centralized data access
- `ViewModel` for UI state and business logic
- Room + DataStore/SharedPreferences for persistent data
- SavedStateHandle only for minimal UI state that must be restored after process death (e.g., selected item ID)

Also see [[c-android-components]] for broader Android architecture context.

---

## Дополнительные Вопросы (RU)

- В чем отличие SavedStateHandle от `ViewModel` в контексте обработки смерти процесса?
- Каковы компромиссы между DataStore Preferences и Proto DataStore?
- Как реализовать корректную стратегию кэширования в паттерне Repository?
- Каковы варианты миграции с SharedPreferences на DataStore?

## Follow-ups

- How does SavedStateHandle differ from `ViewModel` in handling process death?
- What are the trade-offs between DataStore Preferences and Proto DataStore?
- How do you implement proper caching strategy in Repository pattern?
- What are the migration paths from SharedPreferences to DataStore?

## Ссылки (RU)

- [`ViewModel`](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [DataStore](https://developer.android.com/topic/libraries/architecture/datastore)
- [Room Database](https://developer.android.com/training/data-storage/room)
- https://developer.android.com/topic/libraries/architecture/saving-states

## References

- [`ViewModel`](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [DataStore](https://developer.android.com/topic/libraries/architecture/datastore)
- [Room Database](https://developer.android.com/training/data-storage/room)
- https://developer.android.com/topic/libraries/architecture/saving-states

## Related Questions

### Prerequisites (Easier)

- [[q-what-is-layout-types-and-when-to-use--android--easy]]
- What is `Fragment` lifecycle?
- What is the difference between `Activity` and `Fragment` scope?

### Related (Medium)

- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]]
- How to implement offline-first architecture?
- What are the best practices for database migrations in Room?

### Advanced (Harder)

- How to implement multi-module data layer with shared Repository?
- What are the performance implications of different storage mechanisms?
- How to handle data synchronization across multiple data sources?
