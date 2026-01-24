---
id: android-208
title: Architecture Components Libraries / Библиотеки Architecture Components
aliases:
- Architecture Components Libraries
- Библиотеки Architecture Components
topic: android
subtopics:
- architecture-mvvm
- lifecycle
- room
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-components
- c-lifecycle
- c-room
- q-android-jetpack-overview--android--easy
- q-compose-core-components--android--medium
- q-what-are-the-most-important-components-of-compose--android--medium
sources: []
created: 2024-10-15
updated: 2025-11-11
tags:
- android/architecture-mvvm
- android/lifecycle
- android/room
- difficulty/easy
- jetpack
anki_cards:
- slug: android-208-0-en
  language: en
  anki_id: 1768364695698
  synced_at: '2026-01-23T16:45:05.697160'
- slug: android-208-0-ru
  language: ru
  anki_id: 1768364695722
  synced_at: '2026-01-23T16:45:05.698345'
---
# Вопрос (RU)
> Что такое Android Architecture Components и зачем они нужны?

# Question (EN)
> What are Android Architecture Components and why are they needed?

---

## Ответ (RU)

**Android Architecture Components** — набор библиотек для построения надежных, тестируемых и поддерживаемых приложений. Решают проблемы lifecycle management, конфигурационных изменений, утечек памяти.

### Ключевые Принципы

- **Separation of concerns**: UI не содержит бизнес-логику
- **`Lifecycle`-aware**: компоненты автоматически реагируют на lifecycle events
- **Unidirectional data flow**: `ViewModel` → UI (предсказуемость состояния)
- **Testability**: слои изолированы через чёткие контракты

### 1) `ViewModel` — Переживает Configuration Changes

Хранит UI state; отделяет логику от UI; ViewModelScope для корутин; **не хранит `Context`**.

```kotlin
// ✅ Переживает поворот экрана
class UserViewModel : ViewModel() {
  private val _state = MutableStateFlow<User?>(null)
  val state: StateFlow<User?> = _state.asStateFlow()

  fun load(id: String) = viewModelScope.launch {
    _state.value = repo.getUser(id)
  }
}

// ❌ Context leak
class BadViewModel(val context: Context) : ViewModel()
```

**Когда использовать**: любая UI-логика, которая должна пережить recreate `Activity`/`Fragment`.

### 2) `LiveData` / `StateFlow` — `Observable` Состояние

**`LiveData`**: lifecycle-aware out-of-the-box; автоматическая отписка; legacy в новых проектах.
**`StateFlow`**: Kotlin-first; требует manual lifecycle scope; лучшая интеграция с Compose/`Flow`.

```kotlin
// ✅ LiveData: автоматически отписывается
vm.user.observe(viewLifecycleOwner) { render(it) }

// ✅ StateFlow: manual scope
lifecycleScope.launch {
  vm.userFlow.collectLatest { render(it) }
}
```

**Когда использовать**: `StateFlow` для новых проектов (Kotlin-first); `LiveData` для legacy или простых case.

### 3) Room — Type-safe SQLite ORM

Compile-time SQL validation; аннотации (@`Entity`, @`Dao`, @`Database`); поддержка `Flow`/`LiveData`; migration automation.

```kotlin
@Entity(tableName = "users")
data class User(
  @PrimaryKey val id: String,
  val name: String,
  @ColumnInfo(name = "created_at") val createdAt: Long
)

@Dao
interface UserDao {
  @Query("SELECT * FROM users WHERE id = :id")
  suspend fun getUser(id: String): User?

  @Query("SELECT * FROM users")
  fun observeAll(): Flow<List<User>>
}
```

**Когда использовать**: любое локальное хранилище structured data; замена SQLiteOpenHelper.

### 4) WorkManager — Гарантированное Выполнение

Deferrable background tasks; constraints (network, battery); backoff policies; переживает reboot.

```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters)
  : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result = try {
    syncRepo.sync()
    Result.success()
  } catch (e: Exception) {
    Result.retry()
  }
}

val request = OneTimeWorkRequestBuilder<SyncWorker>()
  .setConstraints(
    Constraints.Builder()
      .setRequiredNetworkType(NetworkType.CONNECTED)
      .build()
  )
  .build()
```

**Когда использовать**: отложенные задачи (sync, cleanup); **НЕ** для срочных (используй ForegroundService).

### 5) Navigation — Централизованная Навигация

Single-activity pattern; type-safe arguments (Safe Args); `ViewModel` scoping к графу; deep linking.

```kotlin
// ✅ Type-safe передача аргументов
val action = HomeFragmentDirections.actionHomeToProfile(userId = "123")
findNavController().navigate(action)

// В destination
val args: ProfileFragmentArgs by navArgs()
```

**Когда использовать**: multi-screen flows; shared ViewModels между экранами.

### Архитектурная Интеграция

```text
Data Layer (Room, DataStore)
    ↓
Repository (data transformations)
    ↓
ViewModel (business logic, state management)
    ↓
UI Layer (Compose / Views)
```

**Trade-offs**:
- ✅ Проверенные решения для типичных проблем
- ✅ `Lifecycle`-aware по умолчанию
- ❌ Boilerplate для простых экранов
- ❌ Learning curve для junior разработчиков

---

## Answer (EN)

**Android Architecture Components** are libraries for building robust, testable, maintainable apps. They solve lifecycle management, configuration changes, memory leaks.

### Key Principles

- **Separation of concerns**: UI doesn't contain business logic
- **`Lifecycle`-aware**: components automatically react to lifecycle events
- **Unidirectional data flow**: `ViewModel` → UI (state predictability)
- **Testability**: layers isolated via clear contracts

### 1) `ViewModel` — Survives Configuration Changes

Stores UI state; separates logic from UI; ViewModelScope for coroutines; **no `Context`**.

```kotlin
// ✅ Survives screen rotation
class UserViewModel : ViewModel() {
  private val _state = MutableStateFlow<User?>(null)
  val state: StateFlow<User?> = _state.asStateFlow()

  fun load(id: String) = viewModelScope.launch {
    _state.value = repo.getUser(id)
  }
}

// ❌ Context leak
class BadViewModel(val context: Context) : ViewModel()
```

**When to use**: any UI logic that should survive `Activity`/`Fragment` recreate.

### 2) `LiveData` / `StateFlow` — `Observable` State

**`LiveData`**: lifecycle-aware out-of-the-box; automatic unsubscribe; legacy in new projects.
**`StateFlow`**: Kotlin-first; requires manual lifecycle scope; better Compose/`Flow` integration.

```kotlin
// ✅ LiveData: auto-unsubscribes
vm.user.observe(viewLifecycleOwner) { render(it) }

// ✅ StateFlow: manual scope
lifecycleScope.launch {
  vm.userFlow.collectLatest { render(it) }
}
```

**When to use**: `StateFlow` for new projects (Kotlin-first); `LiveData` for legacy or simple cases.

### 3) Room — Type-safe SQLite ORM

Compile-time SQL validation; annotations (@`Entity`, @`Dao`, @`Database`); `Flow`/`LiveData` support; migration automation.

```kotlin
@Entity(tableName = "users")
data class User(
  @PrimaryKey val id: String,
  val name: String,
  @ColumnInfo(name = "created_at") val createdAt: Long
)

@Dao
interface UserDao {
  @Query("SELECT * FROM users WHERE id = :id")
  suspend fun getUser(id: String): User?

  @Query("SELECT * FROM users")
  fun observeAll(): Flow<List<User>>
}
```

**When to use**: any local storage of structured data; SQLiteOpenHelper replacement.

### 4) WorkManager — Guaranteed Execution

Deferrable background tasks; constraints (network, battery); backoff policies; survives reboot.

```kotlin
class SyncWorker(ctx: Context, params: WorkerParameters)
  : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result = try {
    syncRepo.sync()
    Result.success()
  } catch (e: Exception) {
    Result.retry()
  }
}

val request = OneTimeWorkRequestBuilder<SyncWorker>()
  .setConstraints(
    Constraints.Builder()
      .setRequiredNetworkType(NetworkType.CONNECTED)
      .build()
  )
  .build()
```

**When to use**: deferred tasks (sync, cleanup); **NOT** for urgent (use ForegroundService).

### 5) Navigation — Centralized Navigation

Single-activity pattern; type-safe arguments (Safe Args); `ViewModel` scoping to graph; deep linking.

```kotlin
// ✅ Type-safe argument passing
val action = HomeFragmentDirections.actionHomeToProfile(userId = "123")
findNavController().navigate(action)

// In destination
val args: ProfileFragmentArgs by navArgs()
```

**When to use**: multi-screen flows; shared ViewModels between screens.

### Architectural Integration

```text
Data Layer (Room, DataStore)
    ↓
Repository (data transformations)
    ↓
ViewModel (business logic, state management)
    ↓
UI Layer (Compose / Views)
```

**Trade-offs**:
- ✅ Battle-tested solutions for common problems
- ✅ `Lifecycle`-aware by default
- ❌ Boilerplate for simple screens
- ❌ Learning curve for juniors

---

## Дополнительные Вопросы (RU)

- Когда стоит использовать `StateFlow` вместо `LiveData` в современном Android?
- Как `ViewModel` переживает конфигурационные изменения без сохранения в state bundle?
- В чем разница между запросами `Room` с `Flow` и с `LiveData`?
- Когда следует использовать `WorkManager`, а когда ForegroundService или корутины?
- Как заскопить `ViewModel` к графу навигации по сравнению с `Activity`?

## Follow-ups

- When should you use `StateFlow` vs `LiveData` in modern Android?
- How does `ViewModel` survive configuration changes without saving state bundle?
- What's the difference between `Room`'s `Flow` vs `LiveData` queries?
- When should you use `WorkManager` vs ForegroundService vs Coroutines?
- How do you scope a `ViewModel` to a Navigation graph vs `Activity`?

## Ссылки (RU)

- [[c-android-components]]
- [[c-lifecycle]]
- [[c-room]]
- https://developer.android.com/jetpack
- https://developer.android.com/topic/architecture
- https://developer.android.com/topic/libraries/architecture/viewmodel
- https://developer.android.com/training/data-storage/room
- https://developer.android.com/topic/libraries/architecture/workmanager

## References

- [[c-android-components]]
- [[c-lifecycle]]
- [[c-room]]
- https://developer.android.com/jetpack
- https://developer.android.com/topic/architecture
- https://developer.android.com/topic/libraries/architecture/viewmodel
- https://developer.android.com/training/data-storage/room
- https://developer.android.com/topic/libraries/architecture/workmanager

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-jetpack-overview--android--easy]]

### Связанные (тот Же уровень)
- [[q-android-architectural-patterns--android--medium]]

### Продвинутое (сложнее)
- [[q-android-runtime-internals--android--hard]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
