---
id: android-139
title: "Save Data Outside Fragment / Сохранение данных вне Fragment"
aliases: ["Save Data Outside Fragment", "Сохранение данных вне Fragment"]
topic: android
subtopics: [room, architecture-mvvm, lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-viewmodel, q-what-is-layout-types-and-when-to-use--android--easy]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/room, android/architecture-mvvm, android/lifecycle, data-persistence, fragments, datastore, sharedpreferences, viewmodel, difficulty/medium]
---
# Вопрос (RU)

> Каким образом можно сохранить данные за пределами фрагмента?

# Question (EN)

> How can you save data outside a fragment?

---

## Ответ (RU)

Для сохранения данных за пределами фрагмента используется несколько подходов в зависимости от требований персистентности и объема данных.

### Основные подходы

**1. SharedPreferences**
Для простых настроек (key-value пары). Переживает пересоздание фрагмента и процесса.

```kotlin
// ✅ Подходит для настроек и флагов
val prefs = requireContext().getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit()
    .putString("username", username)
    .putBoolean("notifications", true)
    .apply()  // ✅ Асинхронная запись
```

**2. Room Database**
Для структурированных данных со связями. Полноценная SQLite ORM с compile-time проверками.

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

**3. ViewModel с SavedStateHandle**
Для временных UI-состояний. ViewModel переживает пересоздание Activity, SavedStateHandle — смерть процесса.

```kotlin
// ✅ Activity-scoped ViewModel для шаринга между фрагментами
class SharedViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData.asStateFlow()
}

// Fragment A
private val viewModel: SharedViewModel by activityViewModels()

// Fragment B получает те же данные
private val viewModel: SharedViewModel by activityViewModels()
```

**4. DataStore**
Современная замена SharedPreferences с корутинами и типобезопасностью.

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

### Сравнение методов

| Метод              | Персистентность | Переживает ротацию | Переживает смерть процесса | Use Case           |
| ------------------ | --------------- | ------------------ | -------------------------- | ------------------ |
| SharedPreferences  | Постоянная      | Да                 | Да                         | Настройки, флаги   |
| DataStore          | Постоянная      | Да                 | Да                         | Настройки (новое)  |
| Room               | Постоянная      | Да                 | Да                         | Структурированные  |
| ViewModel          | Временная       | Да                 | Нет                        | UI состояние       |
| SavedStateHandle   | Ограниченная    | Да                 | Да                         | UI состояние (малое) |

### Рекомендуемая архитектура

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
- [[c-viewmodel]] для UI-состояний и бизнес-логики
- Room + DataStore для персистентных данных
- SavedStateHandle только для минимального UI-состояния при смерти процесса

## Answer (EN)

Data persistence outside a fragment depends on requirements for scope and durability.

### Core Approaches

**1. SharedPreferences**
For simple settings (key-value pairs). Survives fragment recreation and process death.

```kotlin
// ✅ Good for settings and flags
val prefs = requireContext().getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit()
    .putString("username", username)
    .putBoolean("notifications", true)
    .apply()  // ✅ Asynchronous write
```

**2. Room Database**
For structured data with relationships. Full SQLite ORM with compile-time verification.

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

**3. ViewModel with SavedStateHandle**
For temporary UI state. ViewModel survives configuration changes, SavedStateHandle survives process death.

```kotlin
// ✅ Activity-scoped ViewModel for sharing between fragments
class SharedViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData.asStateFlow()
}

// Fragment A
private val viewModel: SharedViewModel by activityViewModels()

// Fragment B gets the same data
private val viewModel: SharedViewModel by activityViewModels()
```

**4. DataStore**
Modern replacement for SharedPreferences with coroutines and type safety.

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

| Method             | Persistence | Survives Rotation | Survives Process Death | Use Case          |
| ------------------ | ----------- | ----------------- | ---------------------- | ----------------- |
| SharedPreferences  | Permanent   | Yes               | Yes                    | Settings, flags   |
| DataStore          | Permanent   | Yes               | Yes                    | Settings (modern) |
| Room               | Permanent   | Yes               | Yes                    | Structured data   |
| ViewModel          | Temporary   | Yes               | No                     | UI state          |
| SavedStateHandle   | Limited     | Yes               | Yes                    | UI state (small)  |

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
- [[c-viewmodel]] for UI state and business logic
- Room + DataStore for persistent data
- SavedStateHandle only for minimal UI state during process death

---

## Follow-ups

- How does SavedStateHandle differ from ViewModel in handling process death?
- What are the trade-offs between DataStore Preferences and Proto DataStore?
- How do you implement proper caching strategy in Repository pattern?
- What are the migration paths from SharedPreferences to DataStore?

## References

- https://developer.android.com/topic/libraries/architecture/viewmodel
- https://developer.android.com/topic/libraries/architecture/datastore
- https://developer.android.com/training/data-storage/room
- https://developer.android.com/topic/libraries/architecture/saving-states

## Related Questions

### Prerequisites (Easier)

- [[q-what-is-layout-types-and-when-to-use--android--easy]]
- What is Fragment lifecycle?
- What is the difference between Activity and Fragment scope?

### Related (Medium)

- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]]
- How to implement offline-first architecture?
- What are the best practices for database migrations in Room?

### Advanced (Harder)

- How to implement multi-module data layer with shared Repository?
- What are the performance implications of different storage mechanisms?
- How to handle data synchronization across multiple data sources?
