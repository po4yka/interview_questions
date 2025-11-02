---
id: android-103
title: Android Jetpack Overview / Обзор Android Jetpack
aliases: [Android Jetpack Overview, Обзор Android Jetpack]
topic: android
subtopics:
  - architecture-mvvm
  - lifecycle
  - ui-compose
question_kind: android
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-room
  - c-viewmodel
  - q-room-library-definition--android--easy
  - q-viewmodel-pattern--android--easy
sources: []
created: 2025-10-13
updated: 2025-10-30
tags: [android/architecture-mvvm, android/lifecycle, android/ui-compose, difficulty/easy, jetpack]
date created: Thursday, October 30th 2025, 11:26:44 am
date modified: Sunday, November 2nd 2025, 12:47:07 pm
---

# Вопрос (RU)
> Что такое Android Jetpack и какие его основные компоненты?

# Question (EN)
> What is Android Jetpack and what are its core components?

## Ответ (RU)

Android Jetpack — набор библиотек от Google для упрощения разработки Android-приложений. Унифицирует подход к архитектуре, UI, фоновой работе и хранению данных.

**Четыре категории:**

### Architecture Components

**ViewModel** — сохраняет UI-данные при конфигурационных изменениях
**Room** — type-safe ORM для SQLite с compile-time проверками
**Lifecycle** — отслеживает жизненный цикл Activity/Fragment
**Navigation** — декларативная навигация между экранами

```kotlin
// ✅ ViewModel переживает поворот экрана
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
}

// ❌ Данные в Activity теряются
class MainActivity : AppCompatActivity() {
    var users: List<User> = emptyList() // потеряны при recreation
}
```

### UI Components

**Jetpack Compose** — декларативный UI фреймворк
**Fragment** — модульные UI-компоненты для View-based UI
**ViewBinding** — type-safe доступ к Views

```kotlin
@Composable
fun UserList(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState()
    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

### Background Work

**WorkManager** — гарантированное выполнение отложенных задач даже после перезагрузки

```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork() = try {
        repository.sync()
        Result.success()
    } catch (e: Exception) {
        Result.retry() // автоматический retry с exponential backoff
    }
}
```

### Data & Storage

**Room** — SQL с compile-time проверками
**DataStore** — type-safe замена SharedPreferences с корутинами
**Paging** — эффективная загрузка больших списков

```kotlin
// ✅ Room с suspend функциями
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE active = 1")
    suspend fun getActiveUsers(): List<User>
}

// ❌ Ручная работа с SQLite
val cursor = db.rawQuery("SELECT * FROM users WHERE active = 1", null)
```

**Dependency Injection**

**Hilt** — упрощенный DI на базе Dagger с поддержкой Android компонентов

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

## Answer (EN)

Android Jetpack is Google's suite of libraries for simplified Android development. Unifies architecture, UI, background work, and data storage.

**Four core categories:**

### Architecture Components

**ViewModel** — survives configuration changes like screen rotation
**Room** — type-safe ORM for SQLite with compile-time verification
**Lifecycle** — tracks Activity/Fragment lifecycle states
**Navigation** — declarative screen navigation

```kotlin
// ✅ ViewModel survives screen rotation
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
}

// ❌ Activity data lost on recreation
class MainActivity : AppCompatActivity() {
    var users: List<User> = emptyList() // lost on recreation
}
```

### UI Components

**Jetpack Compose** — declarative UI framework
**Fragment** — modular UI components for View-based UI
**ViewBinding** — type-safe View access

```kotlin
@Composable
fun UserList(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState()
    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

### Background Work

**WorkManager** — guaranteed execution of deferrable tasks even after device reboot

```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork() = try {
        repository.sync()
        Result.success()
    } catch (e: Exception) {
        Result.retry() // automatic retry with exponential backoff
    }
}
```

### Data & Storage

**Room** — SQL with compile-time verification
**DataStore** — type-safe SharedPreferences replacement with coroutines
**Paging** — efficient loading of large lists

```kotlin
// ✅ Room with suspend functions
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE active = 1")
    suspend fun getActiveUsers(): List<User>
}

// ❌ Raw SQLite access
val cursor = db.rawQuery("SELECT * FROM users WHERE active = 1", null)
```

**Dependency Injection**

**Hilt** — simplified DI built on Dagger with Android component support

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

## Follow-ups

- When to use WorkManager vs AlarmManager vs Foreground Service?
- How does ViewModel survive configuration changes internally?
- What's the migration path from View system to Jetpack Compose?
- How does Hilt differ from manual Dagger setup?
- What are the benefits of Room over raw SQLite?

## References

- [[c-viewmodel]] - ViewModel architecture component
- [[c-room]] - Room database library
- [[c-lifecycle]] - Android lifecycle awareness
- Official docs: https://developer.android.com/jetpack

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Basic Android components

### Related
- [[q-viewmodel-pattern--android--easy]] - ViewModel pattern details
- [[q-room-library-definition--android--easy]] - Room database details
 - State management in Compose

### Advanced
- [[q-workmanager-decision-guide--android--medium]] - Background work strategies
- [[q-compose-performance-optimization--android--hard]] - Compose optimization
