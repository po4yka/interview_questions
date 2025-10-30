---
id: 20251012-122765
title: Android Jetpack Overview / Обзор Android Jetpack
aliases: ["Android Jetpack Overview", "Обзор Android Jetpack"]
topic: android
subtopics: [architecture-mvvm, ui-compose, lifecycle, room]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-viewmodel, c-room, q-viewmodel-pattern--android--easy, q-room-library-definition--android--easy, q-workmanager-decision-guide--android--medium]
sources: []
created: 2025-10-13
updated: 2025-10-29
tags: [android/architecture-mvvm, android/ui-compose, android/lifecycle, android/room, jetpack, difficulty/easy]
---
# Вопрос (RU)
> Что такое Android Jetpack и какие его основные компоненты?

# Question (EN)
> What is Android Jetpack and what are its core components?

## Ответ (RU)

Android Jetpack — набор библиотек от Google для упрощения разработки. Четыре основные категории: Architecture, UI, Background, Data.

**Architecture Components**

[[c-viewmodel|ViewModel]] — сохраняет UI-данные при конфигурационных изменениях (поворот экрана)
[[c-room|Room]] — type-safe ORM для SQLite с compile-time проверками
Lifecycle — отслеживает жизненный цикл Activity/Fragment
Navigation — декларативная навигация между экранами

```kotlin
// ✅ ViewModel переживает поворот экрана
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
}

// ❌ Данные в Activity теряются при recreation
class MainActivity : AppCompatActivity() {
    var users: List<User> = emptyList()
}
```

**UI Components**

Jetpack Compose — декларативный UI фреймворк
Fragment — модульные UI-компоненты (для Views)
ViewBinding — type-safe доступ к Views

```kotlin
@Composable
fun UserList(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState()
    LazyColumn {
        items(users) { UserItem(it) }
    }
}
```

**Background Work**

WorkManager — гарантированное выполнение отложенных задач

```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork() = try {
        repository.sync()
        Result.success()
    } catch (e: Exception) {
        Result.retry()
    }
}
```

**Data & Storage**

Room — локальная БД с SQL-запросами в compile-time
DataStore — type-safe замена SharedPreferences
Paging — эффективная загрузка больших списков

```kotlin
// ✅ Room с suspend функциями
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAll(): List<User>
}

// ❌ Прямая работа с SQLite
val cursor = db.query("SELECT * FROM users")
```

**Dependency Injection**

Hilt — упрощенный DI на базе Dagger

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

## Answer (EN)

Android Jetpack is Google's suite of libraries for simplified development. Four core categories: Architecture, UI, Background, Data.

**Architecture Components**

[[c-viewmodel|ViewModel]] — survives configuration changes like screen rotation
[[c-room|Room]] — type-safe ORM for SQLite with compile-time verification
Lifecycle — tracks Activity/Fragment lifecycle states
Navigation — declarative screen navigation

```kotlin
// ✅ ViewModel survives screen rotation
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
}

// ❌ Activity data lost on recreation
class MainActivity : AppCompatActivity() {
    var users: List<User> = emptyList()
}
```

**UI Components**

Jetpack Compose — declarative UI framework
Fragment — modular UI components (for Views)
ViewBinding — type-safe View access

```kotlin
@Composable
fun UserList(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState()
    LazyColumn {
        items(users) { UserItem(it) }
    }
}
```

**Background Work**

WorkManager — guaranteed execution of deferrable tasks

```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork() = try {
        repository.sync()
        Result.success()
    } catch (e: Exception) {
        Result.retry()
    }
}
```

**Data & Storage**

Room — local database with compile-time SQL verification
DataStore — type-safe SharedPreferences replacement
Paging — efficient loading of large lists

```kotlin
// ✅ Room with suspend functions
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAll(): List<User>
}

// ❌ Raw SQLite access
val cursor = db.query("SELECT * FROM users")
```

**Dependency Injection**

Hilt — simplified DI built on Dagger

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

## Follow-ups

- When to use WorkManager vs AlarmManager vs Foreground Service?
- How does ViewModel survive configuration changes internally?
- What are the benefits of Room over raw SQLite?
- When to migrate from View system to Jetpack Compose?
- How does Hilt differ from manual Dagger setup?

## References

- [[c-viewmodel]] - ViewModel architecture component
- [[c-room]] - Room database library
- Official docs: https://developer.android.com/jetpack

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Basic Android components

### Related
- [[q-viewmodel-pattern--android--easy]] - ViewModel pattern
- [[q-room-library-definition--android--easy]] - Room database details
- [[q-compose-state--android--medium]] - State management in Compose

### Advanced
- [[q-workmanager-decision-guide--android--medium]] - Background work strategies
- [[q-compose-performance-optimization--android--hard]] - Compose optimization