---
id: 20251012-122784
title: Architecture Components Libraries / Библиотеки Architecture Components
aliases: [Architecture Components Libraries, Библиотеки Architecture Components]
topic: android
subtopics: [architecture-clean, lifecycle]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, q-android-jetpack-overview--android--easy, q-android-manifest-file--android--easy]
created: 2025-10-15
updated: 2025-10-20
tags: [android/architecture-clean, android/lifecycle, viewmodel, livedata, room, workmanager, paging, navigation, databinding, difficulty/easy]
---

# Question (EN)
> What libraries are included in Android Architecture Components? Provide brief purpose and minimal usage.

# Вопрос (RU)
> Какие библиотеки входят в Android Architecture Components? Краткая цель и минимальный пример использования.

---

## Answer (EN)

Android Architecture Components help build robust, testable, maintainable apps. Core libraries: ViewModel, LiveData, Room, WorkManager, Data Binding (or ViewBinding), Paging, Navigation, Lifecycle.

- **Theory**: Each library addresses a specific concern: UI state (ViewModel), observable state (LiveData/Flow), persistence (Room), background work (WorkManager), UI binding (Data Binding/ViewBinding), large lists (Paging), app navigation (Navigation), and lifecycle awareness (Lifecycle). Using them reduces boilerplate and lifecycle bugs.

### 1) ViewModel — UI state holder

- **Theory**: Survives configuration changes; scoped to UI lifecycle.
```kotlin
class UserViewModel : ViewModel() {
  private val _user = MutableLiveData<User>()
  val user: LiveData<User> = _user
}
// in Fragment
private val vm: UserViewModel by viewModels()
vm.user.observe(viewLifecycleOwner) { render(it) }
```

### 2) LiveData (or StateFlow) — observable state

- **Theory**: LiveData is lifecycle-aware; StateFlow needs a lifecycle scope but offers Kotlin Flow APIs.
```kotlin
// LiveData
vm.user.observe(viewLifecycleOwner) { render(it) }
// StateFlow
lifecycleScope.launchWhenStarted { vm.userFlow.collect { render(it) } }
```

### 3) Room — SQLite with type safety

- **Theory**: Compile-time query checks, DAOs, entities, easy with Flow/LiveData.
```kotlin
@Entity data class User(@PrimaryKey val id: String, val name: String)
@Dao interface UserDao { @Query("SELECT * FROM User WHERE id=:id") suspend fun get(id: String): User? }
@Database(entities=[User::class], version=1) abstract class DB: RoomDatabase(){ abstract fun userDao(): UserDao }
```

### 4) WorkManager — deferrable guaranteed work

- **Theory**: Runs even after process death; respects constraints.
```kotlin
class SyncWorker(ctx: Context, p: WorkerParameters): CoroutineWorker(ctx,p){
  override suspend fun doWork() = Result.success()
}
WorkManager.getInstance(ctx).enqueue(OneTimeWorkRequestBuilder<SyncWorker>().build())
```

### 5) Data Binding / ViewBinding — bind views

- **Theory**: ViewBinding is preferred for type-safe view refs; Data Binding adds expressions in XML when needed.
```kotlin
// ViewBinding
val binding = ActivityMainBinding.inflate(layoutInflater)
setContentView(binding.root)
binding.text.text = "Hi"
```

### 6) Paging — large data lists

- **Theory**: Loads pages on demand; integrates with Room/Network.
```kotlin
val flow: Flow<PagingData<User>> = Pager(PagingConfig(pageSize=20)) { UserPagingSource(api) }.flow
lifecycleScope.launch { flow.collectLatest(adapter::submitData) }
```

### 7) Navigation — type-safe navigation

- **Theory**: Central graph, Safe Args, deep links.
```kotlin
val action = HomeFragmentDirections.actionHomeToProfile(userId)
findNavController().navigate(action)
```

### 8) Lifecycle — lifecycle-aware components

- **Theory**: Observe lifecycle to start/stop resources safely.
```kotlin
class LocationObserver: DefaultLifecycleObserver {
  override fun onStart(o: LifecycleOwner){ start() }
  override fun onStop(o: LifecycleOwner){ stop() }
}
lifecycle.addObserver(LocationObserver())
```

---

## Ответ (RU)

Android Architecture Components помогают создавать надежные, тестируемые и поддерживаемые приложения. Основные библиотеки: ViewModel, LiveData, Room, WorkManager, Data Binding (или ViewBinding), Paging, Navigation, Lifecycle.

- **Теория**: Каждая библиотека решает отдельную задачу: состояние UI (ViewModel), наблюдаемое состояние (LiveData/Flow), хранение данных (Room), фоновые задачи (WorkManager), привязка UI (Data Binding/ViewBinding), большие списки (Paging), навигация (Navigation), осведомленность о жизненном цикле (Lifecycle). Это снижает бойлерплейт и ошибки жизненного цикла.

### 1) ViewModel — хранитель состояния UI

- **Теория**: Переживает смену конфигурации; живет в рамках UI lifecycle.
```kotlin
class UserViewModel : ViewModel() {
  private val _user = MutableLiveData<User>()
  val user: LiveData<User> = _user
}
// во Fragment
private val vm: UserViewModel by viewModels()
vm.user.observe(viewLifecycleOwner) { render(it) }
```

### 2) LiveData (или StateFlow) — наблюдаемое состояние

- **Теория**: LiveData учитывает lifecycle; StateFlow требует scope, но дает API Flow.
```kotlin
// LiveData
vm.user.observe(viewLifecycleOwner) { render(it) }
// StateFlow
lifecycleScope.launchWhenStarted { vm.userFlow.collect { render(it) } }
```

### 3) Room — SQLite с типобезопасностью

- **Теория**: Проверка запросов на компиляции, DAO, сущности, интеграция с Flow/LiveData.
```kotlin
@Entity data class User(@PrimaryKey val id: String, val name: String)
@Dao interface UserDao { @Query("SELECT * FROM User WHERE id=:id") suspend fun get(id: String): User? }
@Database(entities=[User::class], version=1) abstract class DB: RoomDatabase(){ abstract fun userDao(): UserDao }
```

### 4) WorkManager — отложенная гарантированная работа

- **Теория**: Выполнится даже после убийства процесса; учитывает ограничения.
```kotlin
class SyncWorker(ctx: Context, p: WorkerParameters): CoroutineWorker(ctx,p){
  override suspend fun doWork() = Result.success()
}
WorkManager.getInstance(ctx).enqueue(OneTimeWorkRequestBuilder<SyncWorker>().build())
```

### 5) Data Binding / ViewBinding — привязка представлений

- **Теория**: ViewBinding предпочтителен для типобезопасного доступа; Data Binding нужен для выражений в XML.
```kotlin
// ViewBinding
val binding = ActivityMainBinding.inflate(layoutInflater)
setContentView(binding.root)
binding.text.text = "Hi"
```

### 6) Paging — большие списки

- **Теория**: Дозагрузка по страницам; работает с Room/сетью.
```kotlin
val flow: Flow<PagingData<User>> = Pager(PagingConfig(pageSize=20)) { UserPagingSource(api) }.flow
lifecycleScope.launch { flow.collectLatest(adapter::submitData) }
```

### 7) Navigation — типобезопасная навигация

- **Теория**: Единый граф, Safe Args, deep links.
```kotlin
val action = HomeFragmentDirections.actionHomeToProfile(userId)
findNavController().navigate(action)
```

### 8) Lifecycle — компоненты с учетом жизненного цикла

- **Теория**: Наблюдайте lifecycle, чтобы безопасно запускать/останавливать ресурсы.
```kotlin
class LocationObserver: DefaultLifecycleObserver {
  override fun onStart(o: LifecycleOwner){ start() }
  override fun onStop(o: LifecycleOwner){ stop() }
}
lifecycle.addObserver(LocationObserver())
```

---

## Follow-ups

- When to prefer StateFlow over LiveData?
- How to migrate from AsyncTask/Services to WorkManager?
- How to structure Room with repositories and DAOs?

## References

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

