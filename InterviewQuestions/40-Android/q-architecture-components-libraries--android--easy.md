---
id: 20251012-122784
title: Architecture Components Libraries / Библиотеки Architecture Components
aliases: ["Architecture Components Libraries", "Библиотеки Architecture Components"]
topic: android
subtopics: [architecture-clean, lifecycle, room]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, q-android-jetpack-overview--android--easy, q-android-manifest-file--android--easy]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/architecture-clean, android/lifecycle, android/room, jetpack, difficulty/easy]
---

# Вопрос (RU)
> Что такое Библиотеки Architecture Components и для чего они используются?

## Ответ (RU)

Android Architecture Components — набор библиотек для построения надёжных, тестируемых, поддерживаемых приложений. Основные: ViewModel, LiveData/StateFlow, Room, WorkManager, Paging, Navigation, Lifecycle.

**Ключевые принципы**
- Разделение ответственности: UI, domain, data
- Lifecycle-aware: автоматическое управление жизненным циклом
- Однонаправленный поток данных: ViewModel → UI
- Тестируемость через чёткие границы

### 1) ViewModel — Хранение UI State

Переживает configuration changes; отделяет бизнес-логику от UI; ViewModelScope для корутин.

```kotlin
// ✅ Правильно: состояние переживает поворот
class UserViewModel : ViewModel() {
  private val _state = MutableStateFlow<User?>(null)
  val state: StateFlow<User?> = _state.asStateFlow()

  fun load(id: String) = viewModelScope.launch {
    _state.value = repository.getUser(id)
  }
}

// ❌ Неправильно: утечка Context
class BadViewModel(val context: Context) : ViewModel()
```

### 2) LiveData / StateFlow — Observable Состояние

LiveData lifecycle-aware; StateFlow требует ручного управления; Flow для потоков данных.

```kotlin
// ✅ LiveData: автоматическая отписка
vm.user.observe(viewLifecycleOwner) { render(it) }

// ✅ StateFlow с lifecycle scope
lifecycleScope.launch {
  vm.userFlow.collect { render(it) }
}
```

### 3) Room — Type-Safe SQLite

Compile-time проверка SQL; автоматическая генерация DAOs; Flow/LiveData для реактивности.

```kotlin
@Entity
data class User(@PrimaryKey val id: String, val name: String)

@Dao interface UserDao {
  @Query("SELECT * FROM User WHERE id = :id")
  suspend fun getUser(id: String): User?

  @Query("SELECT * FROM User")
  fun observeAll(): Flow<List<User>>
}

@Database(entities = [User::class], version = 1)
abstract class AppDB : RoomDatabase() {
  abstract fun userDao(): UserDao
}
```

### 4) WorkManager — Отложенные Задачи

Гарантированное выполнение с ограничениями; переживает перезагрузку; backoff policies.

```kotlin
// ✅ Отложенная синхронизация
class SyncWorker(ctx: Context, params: WorkerParameters)
  : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    return try {
      syncRepository.sync()
      Result.success()
    } catch (e: Exception) {
      Result.retry()
    }
  }
}

val request = OneTimeWorkRequestBuilder<SyncWorker>()
  .setConstraints(
    Constraints.Builder()
      .setRequiredNetworkType(NetworkType.CONNECTED)
      .build()
  )
  .build()
WorkManager.getInstance(ctx).enqueue(request)

// ❌ Неправильно: для срочных задач используй ForegroundService
```

### 5) Navigation — Type-Safe Навигация

Централизованный граф; Safe Args для аргументов; ViewModel scope к графу.

```kotlin
// ✅ Type-safe аргументы
val action = HomeFragmentDirections.actionHomeToProfile(userId = "123")
findNavController().navigate(action)

// В destination
val args: ProfileFragmentArgs by navArgs()
val userId = args.userId
```

**Интеграция**
Room → Repository → ViewModel → UI (Compose/Views) — чистая архитектура с реактивными потоками.

**Выбор решений**
- LiveData для simple UI binding; StateFlow для Kotlin-first подхода
- ViewBinding всегда; Data Binding только для простых case
- WorkManager для deferrable; ForegroundService для срочных задач

---

# Question (EN)
> What are Architecture Components Libraries and what are they used for?

## Answer (EN)

Android Architecture Components are libraries for building robust, testable, maintainable apps. Core libraries: ViewModel, LiveData/StateFlow, Room, WorkManager, Paging, Navigation, Lifecycle.

**Key Principles**
- Separation of concerns: UI, domain, data
- Lifecycle-aware: automatic lifecycle management
- Unidirectional data flow: ViewModel → UI
- Testability via clear boundaries

### 1) ViewModel — UI State Storage

Survives configuration changes; separates business logic from UI; ViewModelScope for coroutines.

```kotlin
// ✅ Correct: state survives rotation
class UserViewModel : ViewModel() {
  private val _state = MutableStateFlow<User?>(null)
  val state: StateFlow<User?> = _state.asStateFlow()

  fun load(id: String) = viewModelScope.launch {
    _state.value = repository.getUser(id)
  }
}

// ❌ Wrong: Context leak
class BadViewModel(val context: Context) : ViewModel()
```

### 2) LiveData / StateFlow — Observable State

LiveData is lifecycle-aware; StateFlow requires manual management; Flow for data streams.

```kotlin
// ✅ LiveData: automatic unsubscribe
vm.user.observe(viewLifecycleOwner) { render(it) }

// ✅ StateFlow with lifecycle scope
lifecycleScope.launch {
  vm.userFlow.collect { render(it) }
}
```

### 3) Room — Type-Safe SQLite

Compile-time SQL validation; auto-generated DAOs; Flow/LiveData for reactivity.

```kotlin
@Entity
data class User(@PrimaryKey val id: String, val name: String)

@Dao interface UserDao {
  @Query("SELECT * FROM User WHERE id = :id")
  suspend fun getUser(id: String): User?

  @Query("SELECT * FROM User")
  fun observeAll(): Flow<List<User>>
}

@Database(entities = [User::class], version = 1)
abstract class AppDB : RoomDatabase() {
  abstract fun userDao(): UserDao
}
```

### 4) WorkManager — Deferred Tasks

Guaranteed execution with constraints; survives reboots; backoff policies.

```kotlin
// ✅ Deferred sync
class SyncWorker(ctx: Context, params: WorkerParameters)
  : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    return try {
      syncRepository.sync()
      Result.success()
    } catch (e: Exception) {
      Result.retry()
    }
  }
}

val request = OneTimeWorkRequestBuilder<SyncWorker>()
  .setConstraints(
    Constraints.Builder()
      .setRequiredNetworkType(NetworkType.CONNECTED)
      .build()
  )
  .build()
WorkManager.getInstance(ctx).enqueue(request)

// ❌ Wrong: for urgent tasks use ForegroundService
```

### 5) Navigation — Type-Safe Navigation

Centralized graph; Safe Args for arguments; ViewModel scoped to graph.

```kotlin
// ✅ Type-safe arguments
val action = HomeFragmentDirections.actionHomeToProfile(userId = "123")
findNavController().navigate(action)

// In destination
val args: ProfileFragmentArgs by navArgs()
val userId = args.userId
```

**Integration**
Room → Repository → ViewModel → UI (Compose/Views) — clean architecture with reactive streams.

**Decision Making**
- LiveData for simple UI binding; StateFlow for Kotlin-first approach
- ViewBinding always; Data Binding only for simple cases
- WorkManager for deferrable; ForegroundService for urgent tasks

---

## Follow-ups

- When to use StateFlow vs LiveData in modern Android apps?
- How does Room ensure type safety at compile-time?
- What constraints can WorkManager enforce for background tasks?
- How do ViewModels survive configuration changes without saving state?
- When should you scope a ViewModel to a Navigation graph vs Activity?

## References

- https://developer.android.com/jetpack
- https://developer.android.com/topic/architecture
- https://developer.android.com/topic/libraries/architecture/viewmodel
- https://developer.android.com/training/data-storage/room
- https://developer.android.com/topic/libraries/architecture/workmanager

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
