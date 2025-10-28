---
id: 20251012-122784
title: Architecture Components Libraries / Библиотеки Architecture Components
aliases: [Architecture Components Libraries, Библиотеки Architecture Components, Jetpack Architecture, Android Jetpack Libraries]
topic: android
subtopics: [architecture-clean, lifecycle]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, q-android-jetpack-overview--android--easy, q-android-manifest-file--android--easy]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/architecture-clean, android/lifecycle, difficulty/easy]
---

# Вопрос (RU)
> Что такое Библиотеки Architecture Components?

## Ответ (RU)

Android Architecture Components помогают строить надёжные, тестируемые, поддерживаемые приложения. Основные библиотеки: ViewModel, LiveData/StateFlow, Room, WorkManager, Data/ViewBinding, Paging, Navigation, Lifecycle.

**Принципы проектирования**
- Единственная ответственность модулей; разделение UI, domain, data
- Lifecycle-aware по умолчанию; избегание утечек Activity/Fragment
- Однонаправленный поток данных (ViewModel → UI)
- Тестируемость через чёткие границы

**Паттерны интеграции**
- Room → Flow/LiveData → ViewModel → UI (RecyclerView/Compose)
- WorkManager для отложенных задач из репозиториев/UseCases
- Navigation управляет экранами; ViewModel привязана к destination

### 1) ViewModel — Держатель UI State

Переживает configuration changes; предоставляет UI state и события; без Android UI ссылок; ViewModelScope для корутин.

```kotlin
class UserViewModel : ViewModel() {
  private val _user = MutableLiveData<User>()
  val user: LiveData<User> = _user
}

// во Fragment
private val vm: UserViewModel by viewModels()
vm.user.observe(viewLifecycleOwner) { render(it) }
```

### 2) LiveData / StateFlow — Observable State

LiveData доставляет только когда STARTED/RESUMED; StateFlow горячий, conflated; предпочитайте Flow для потоков, LiveData для XML binding.

```kotlin
// ✅ LiveData
vm.user.observe(viewLifecycleOwner) { render(it) }

// ✅ StateFlow
lifecycleScope.launchWhenStarted {
  vm.userFlow.collect { render(it) }
}
```

### 3) Room — SQLite с Type Safety

DAOs с compile-time SQL проверками; flows реагируют на изменения таблицы; off-main-thread по умолчанию; миграции для schema evolution.

```kotlin
@Entity
data class User(@PrimaryKey val id: String, val name: String)

@Dao interface UserDao {
  @Query("SELECT * FROM User WHERE id=:id")
  suspend fun get(id: String): User?
}

@Database(entities = [User::class], version = 1)
abstract class DB : RoomDatabase() {
  abstract fun userDao(): UserDao
}
```

### 4) WorkManager — Гарантированная Отложенная Работа

Выполнение с ограничениями (network, charging); сохраняется после перезагрузки; идемпотентные задачи + backoff policies; не для точного времени.

```kotlin
class SyncWorker(ctx: Context, p: WorkerParameters)
  : CoroutineWorker(ctx, p) {
  override suspend fun doWork() = Result.success()
}

WorkManager.getInstance(ctx).enqueue(
  OneTimeWorkRequestBuilder<SyncWorker>().build()
)
```

### 5) ViewBinding / Data Binding

ViewBinding для type-safe view refs; Data Binding позволяет выражения, но скрывает логику в XML — использовать экономно.

```kotlin
// ✅ ViewBinding
val binding = ActivityMainBinding.inflate(layoutInflater)
setContentView(binding.root)
binding.text.text = "Hi"
```

### 6) Paging — Большие Списки

Постраничная загрузка снижает память/латентность; работает с Room (invalidations) и сетью (RemoteMediator); immutable paging data.

```kotlin
val flow: Flow<PagingData<User>> = Pager(
  PagingConfig(pageSize = 20)
) { UserPagingSource(api) }.flow

lifecycleScope.launch {
  flow.collectLatest(adapter::submitData)
}
```

### 7) Navigation — Type-safe Navigation

Центральный граф, Safe Args для compile-time аргументов, deep links и контроль back stack; ViewModel скопирован к графу.

```kotlin
val action = HomeFragmentDirections.actionHomeToProfile(userId)
findNavController().navigate(action)
```

### 8) Lifecycle — Lifecycle-aware Компоненты

Наблюдение lifecycle для запуска/остановки ресурсов; предпочитайте DefaultLifecycleObserver; ProcessLifecycleOwner для app-wide state.

```kotlin
class LocationObserver : DefaultLifecycleObserver {
  override fun onStart(o: LifecycleOwner) { start() }
  override fun onStop(o: LifecycleOwner) { stop() }
}

lifecycle.addObserver(LocationObserver())
```

**Выбор и сравнения**
- LiveData vs StateFlow: LiveData = lifecycle-aware binding; StateFlow = Kotlin Flow ecosystem
- ViewBinding vs Data Binding: ViewBinding предпочтительнее
- WorkManager vs ForegroundService: WorkManager для отложенной гарантированной работы

**Типичные ошибки**
- ❌ Хранение Context/View в ViewModel (утечки); используйте Application или передавайте через методы
- ❌ I/O на main thread с Room; держите запросы off main
- ❌ Сложная логика в XML Data Binding; перенесите в ViewModel
- ❌ WorkManager для точного расписания; используйте AlarmManager

**Тестирование**
- ViewModel: JUnit + coroutines test rules; Turbine для Flow
- Room: in-memory DB, Robolectric/Instrumented по необходимости
- WorkManager: WorkManagerTestInitHelper; expedited policy

---

# Question (EN)
> What are Architecture Components Libraries?

## Answer (EN)

Android Architecture Components help build robust, testable, maintainable apps. Core libraries: ViewModel, LiveData/StateFlow, Room, WorkManager, Data/ViewBinding, Paging, Navigation, Lifecycle.

**Design principles**
- Single-responsibility modules; separation of concerns (UI, domain, data)
- Lifecycle-aware by default; avoid leaking Activities/Fragments
- Unidirectional data flow (ViewModel → UI); single source of truth
- Testability via clear boundaries and deterministic state holders

**Integration patterns**
- Room → Flow/LiveData → ViewModel → UI (RecyclerView/Compose)
- WorkManager for deferrable jobs triggered from repositories/UseCases
- Navigation drives screens and argument passing; ViewModel scoped to destinations

### 1) ViewModel — UI State Holder

Survives configuration changes; exposes UI state and events; no Android UI references; use ViewModelScope for coroutines.

```kotlin
class UserViewModel : ViewModel() {
  private val _user = MutableLiveData<User>()
  val user: LiveData<User> = _user
}

// in Fragment
private val vm: UserViewModel by viewModels()
vm.user.observe(viewLifecycleOwner) { render(it) }
```

### 2) LiveData / StateFlow — Observable State

LiveData delivers only when STARTED/RESUMED; StateFlow is hot, conflated, needs lifecycle-aware collection; prefer Flow for streams, LiveData for XML binding.

```kotlin
// ✅ LiveData
vm.user.observe(viewLifecycleOwner) { render(it) }

// ✅ StateFlow
lifecycleScope.launchWhenStarted {
  vm.userFlow.collect { render(it) }
}
```

### 3) Room — SQLite with Type Safety

DAOs with compile-time SQL checks; flows emit on table invalidation; off-main-thread by default; migrations enforce schema evolution.

```kotlin
@Entity
data class User(@PrimaryKey val id: String, val name: String)

@Dao interface UserDao {
  @Query("SELECT * FROM User WHERE id=:id")
  suspend fun get(id: String): User?
}

@Database(entities = [User::class], version = 1)
abstract class DB : RoomDatabase() {
  abstract fun userDao(): UserDao
}
```

### 4) WorkManager — Deferrable Guaranteed Work

Executes with constraints (network, charging), persists across reboots; idempotent jobs + backoff policies; not for exact-time tasks.

```kotlin
class SyncWorker(ctx: Context, p: WorkerParameters)
  : CoroutineWorker(ctx, p) {
  override suspend fun doWork() = Result.success()
}

WorkManager.getInstance(ctx).enqueue(
  OneTimeWorkRequestBuilder<SyncWorker>().build()
)
```

### 5) ViewBinding / Data Binding

ViewBinding for type-safe view refs; Data Binding enables expressions but can hide logic in XML—use sparingly.

```kotlin
// ✅ ViewBinding
val binding = ActivityMainBinding.inflate(layoutInflater)
setContentView(binding.root)
binding.text.text = "Hi"
```

### 6) Paging — Large Data Lists

Paged loading reduces memory/latency; works with Room (invalidations) and network (RemoteMediator); immutable paging data.

```kotlin
val flow: Flow<PagingData<User>> = Pager(
  PagingConfig(pageSize = 20)
) { UserPagingSource(api) }.flow

lifecycleScope.launch {
  flow.collectLatest(adapter::submitData)
}
```

### 7) Navigation — Type-safe Navigation

Central graph, Safe Args for compile-time args, deep links and back stack control; scope ViewModels to graph.

```kotlin
val action = HomeFragmentDirections.actionHomeToProfile(userId)
findNavController().navigate(action)
```

### 8) Lifecycle — Lifecycle-aware Components

Observe lifecycle to start/stop resources; prefer DefaultLifecycleObserver; ProcessLifecycleOwner for app-wide state.

```kotlin
class LocationObserver : DefaultLifecycleObserver {
  override fun onStart(o: LifecycleOwner) { start() }
  override fun onStop(o: LifecycleOwner) { stop() }
}

lifecycle.addObserver(LocationObserver())
```

**Comparisons & choices**
- LiveData vs StateFlow: LiveData = lifecycle-aware binding; StateFlow = Kotlin Flow ecosystem, explicit collection
- ViewBinding vs Data Binding: ViewBinding preferred; use Data Binding only for simple, testable expressions
- WorkManager vs ForegroundService/AlarmManager: WorkManager for deferrable guaranteed work; not for real-time/foreground tasks

**Common pitfalls**
- ❌ Holding Context/View in ViewModel (leaks); use Application or pass via methods
- ❌ Doing I/O on main thread with Room; keep queries off main
- ❌ Complex logic in XML Data Binding; move to ViewModel
- ❌ Misusing WorkManager for exact scheduling; use AlarmManager/Calendar APIs

**Testing notes**
- ViewModel: JUnit + coroutines test rules; use Turbine for Flow
- Room: in-memory DB, run queries off main, use Robolectric/Instrumented as needed
- WorkManager: WorkManagerTestInitHelper; set expedited policy

---

## Follow-ups

- When to prefer StateFlow over LiveData?
- How to migrate from AsyncTask/Services to WorkManager?
- How to structure Room with repositories and DAOs?
- How to test ViewModels with coroutines?
- When to use Navigation Component vs manual fragment transactions?

## References

- [[c-viewmodel]]
- [[c-room]]
- [[c-workmanager]]
- [[c-lifecycle]]
- https://developer.android.com/jetpack
- https://developer.android.com/topic/libraries/architecture

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
