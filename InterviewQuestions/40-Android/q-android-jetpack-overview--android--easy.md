---\
id: android-103
title: Android Jetpack Overview / Обзор Android Jetpack
aliases: [Android Jetpack Overview, Обзор Android Jetpack]
topic: android
subtopics: [architecture-mvvm, lifecycle, ui-compose]
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-architecture-components-libraries--android--easy, q-how-jetpack-compose-works--android--medium, q-room-library-definition--android--easy, q-viewmodel-pattern--android--easy, q-what-to-do-in-android-project-to-start-drawing-ui-on-screen--android--easy]
sources: []
created: 2025-10-13
updated: 2025-11-11
tags: [android/architecture-mvvm, android/lifecycle, android/ui-compose, difficulty/easy, jetpack]
question_kind: android

---\
# Вопрос (RU)
> Что такое Android Jetpack и какие его основные компоненты?

# Question (EN)
> What is Android Jetpack and what are its core components?

## Ответ (RU)

Android Jetpack — набор официально поддерживаемых Google библиотек и инструментов (в основном в пространстве имён AndroidX) для упрощения разработки Android-приложений. Помогает унифицировать подход к архитектуре, UI, фоновой работе и хранению данных. См. также [[c-android]].

**Четыре категории (официально):** Architecture, UI, Behavior, Foundation.
Ниже — практическая группировка ключевых компонентов.

### Architecture Components

**`ViewModel`** — сохраняет UI-данные при конфигурационных изменениях.
**`Room`** — type-safe абстракция над `SQLite` с compile-time проверками (ORM-подобный подход).
**`Lifecycle`** — отслеживает жизненный цикл `Activity`/`Fragment` и даёт lifecycle-aware API.
**Navigation** — декларативная навигация между экранами.

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

**Jetpack Compose** — декларативный UI-фреймворк.
**`Fragment`** — модульные UI-компоненты для `View`-based UI.
**ViewBinding** — type-safe доступ к Views.

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

**`WorkManager`** — надёжное выполнение отложенных задач и задач с условиями, в том числе с возможностью переживать перезагрузку устройства (при соответствующей настройке), с поддержкой ограничений и гибкой политики повторов (включая exponential backoff). Точное время запуска не жёстко гарантируется.

```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork() = try {
        repository.sync()
        Result.success()
    } catch (e: Exception) {
        Result.retry() // повтор будет согласно настроенной backoff/policy
    }
}
```

### Data & Storage

**`Room`** — SQL с compile-time проверками и удобным DAO-API.
**DataStore** — современная type-safe альтернатива `SharedPreferences` с поддержкой корутин.
**Paging** — эффективная постраничная загрузка больших списков.

```kotlin
// ✅ Room с suspend-функциями
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE active = 1")
    suspend fun getActiveUsers(): List<User>
}

// ❌ Ручная работа с SQLite
val cursor = db.rawQuery("SELECT * FROM users WHERE active = 1", null)
```

**Dependency Injection**

**`Hilt`** — рекомендуемый DI-фреймворк на базе `Dagger` с поддержкой Android-компонентов, часто используется совместно с Jetpack-компонентами.

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

## Answer (EN)

Android Jetpack is Google's set of officially supported libraries and tools (primarily shipped under the AndroidX namespace) for simplifying Android development. It helps unify approaches to architecture, UI, background work, and data storage. See also [[c-android]].

**Four official categories:** Architecture, UI, Behavior, Foundation.
Below is a practical grouping of key components.

### Architecture Components

**`ViewModel`** — survives configuration changes like screen rotation.
**`Room`** — type-safe abstraction over `SQLite` with compile-time verification (ORM-like approach).
**`Lifecycle`** — tracks `Activity`/`Fragment` lifecycle and provides lifecycle-aware APIs.
**Navigation** — declarative screen navigation.

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

**Jetpack Compose** — declarative UI framework.
**`Fragment`** — modular UI components for `View`-based UI.
**ViewBinding** — type-safe `View` access.

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

**`WorkManager`** — robust execution of deferrable and constraint-based background work, including the ability to survive device reboots when configured, with constraints and flexible retry policies (including exponential backoff). It does not strictly guarantee exact timing.

```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork() = try {
        repository.sync()
        Result.success()
    } catch (e: Exception) {
        Result.retry() // retry will follow the configured backoff/policy
    }
}
```

### Data & Storage

**`Room`** — SQL with compile-time verification and a convenient DAO API.
**DataStore** — modern type-safe alternative to `SharedPreferences` with coroutine support.
**Paging** — efficient paginated loading of large lists.

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

**`Hilt`** — recommended DI framework built on `Dagger` with first-class Android component support, commonly used together with Jetpack components.

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

## Дополнительные Вопросы (RU)

- Когда использовать `WorkManager`, а когда AlarmManager или foreground `Service`?
- Как `ViewModel` внутренне переживает конфигурационные изменения?
- Каков путь миграции с `View`-системы на Jetpack Compose?
- Чем `Hilt` отличается от ручной настройки `Dagger`?
- Каковы преимущества `Room` по сравнению с "сырым" `SQLite`?

## Follow-ups

- When to use `WorkManager` vs AlarmManager vs Foreground `Service`?
- How does `ViewModel` survive configuration changes internally?
- What's the migration path from `View` system to Jetpack Compose?
- How does `Hilt` differ from manual `Dagger` setup?
- What are the benefits of `Room` over raw `SQLite`?

## Ссылки (RU)

- Официальная документация: https://developer.android.com/jetpack

## References

- Official docs: https://developer.android.com/jetpack

## Связанные Вопросы (RU)

### Предварительные Знания
- [[q-android-app-components--android--easy]] — базовые компоненты Android

### Связанные
- [[q-viewmodel-pattern--android--easy]] — детали паттерна `ViewModel`
- [[q-room-library-definition--android--easy]] — детали базы данных `Room`

### Продвинутые
- [[q-workmanager-decision-guide--android--medium]] — стратегии фоновых задач
- [[q-compose-performance-optimization--android--hard]] — оптимизация производительности Compose

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Basic Android components

### Related
- [[q-viewmodel-pattern--android--easy]] - `ViewModel` pattern details
- [[q-room-library-definition--android--easy]] - `Room` database details

### Advanced
- [[q-workmanager-decision-guide--android--medium]] - Background work strategies
- [[q-compose-performance-optimization--android--hard]] - Compose optimization
