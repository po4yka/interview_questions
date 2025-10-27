---
id: 20251012-122765
title: Android Jetpack Overview / Обзор Android Jetpack
aliases: ["Android Jetpack Overview", "Обзор Android Jetpack"]
topic: android
subtopics: [architecture-clean, ui-compose]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-room-library-definition--android--easy, q-viewmodel-pattern--android--easy]
sources: []
created: 2025-10-13
updated: 2025-10-27
tags: [android/architecture-clean, android/ui-compose, difficulty/easy]
---
# Вопрос (RU)
> Что такое Android Jetpack и какие его основные компоненты?

# Question (EN)
> What is Android Jetpack and what are its core components?

## Ответ (RU)

Android Jetpack — набор библиотек и инструментов от Google для упрощения разработки Android-приложений. Включает компоненты для архитектуры, UI, фоновой работы и управления данными.

**Основные категории:**

**Architecture** — [[c-viewmodel|ViewModel]], [[c-room|Room]], Navigation, Lifecycle
- ViewModel сохраняет данные при изменении конфигурации
- Room — ORM для SQLite с compile-time проверками
- Navigation — граф навигации между экранами

```kotlin
// ✅ ViewModel с корутинами
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
}

// ❌ Логика в Activity — потеря данных при повороте
class MainActivity : AppCompatActivity() {
    var users: List<User> = emptyList() // теряется при recreation
}
```

**Background Work** — WorkManager для отложенных и периодических задач
```kotlin
// ✅ Гарантированное выполнение даже после перезагрузки
class SyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork() = try {
        repository.sync()
        Result.success()
    } catch (e: Exception) {
        Result.retry()
    }
}
```

**UI** — Jetpack Compose для декларативного UI
```kotlin
@Composable
fun UserList(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState()
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}
```

**Data** — DataStore (замена SharedPreferences), Paging для больших списков

| Категория | Компоненты | Назначение |
|-----------|------------|------------|
| Architecture | ViewModel, Room, Navigation | Архитектура приложения |
| UI | Compose, Fragment | Пользовательский интерфейс |
| Background | WorkManager | Фоновые задачи |
| Data | DataStore, Paging | Управление данными |

## Answer (EN)

Android Jetpack is a suite of libraries and tools from Google that simplifies Android development. It provides components for architecture, UI, background work, and data management.

**Core Categories:**

**Architecture** — [[c-viewmodel|ViewModel]], [[c-room|Room]], Navigation, Lifecycle
- ViewModel survives configuration changes
- Room is an ORM for SQLite with compile-time verification
- Navigation provides graph-based screen navigation

```kotlin
// ✅ ViewModel with coroutines
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
}

// ❌ Logic in Activity — data loss on rotation
class MainActivity : AppCompatActivity() {
    var users: List<User> = emptyList() // lost on recreation
}
```

**Background Work** — WorkManager for deferrable and periodic tasks
```kotlin
// ✅ Guaranteed execution even after device reboot
class SyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork() = try {
        repository.sync()
        Result.success()
    } catch (e: Exception) {
        Result.retry()
    }
}
```

**UI** — Jetpack Compose for declarative UI
```kotlin
@Composable
fun UserList(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState()
    LazyColumn {
        items(users) { user -> UserItem(user) }
    }
}
```

**Data** — DataStore (SharedPreferences replacement), Paging for large lists

| Category | Components | Purpose |
|----------|------------|---------|
| Architecture | ViewModel, Room, Navigation | App architecture |
| UI | Compose, Fragment | User interface |
| Background | WorkManager | Background tasks |
| Data | DataStore, Paging | Data management |

## Follow-ups

- When to use WorkManager vs AlarmManager vs Foreground Service?
- How does ViewModel survive configuration changes?
- What are the benefits of Room over raw SQLite?
- When should you migrate from View system to Jetpack Compose?

## References

- [[c-viewmodel]] - ViewModel concept
- [[c-room]] - Room database concept
- https://developer.android.com/jetpack

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Android app components

### Related
- [[q-viewmodel-pattern--android--easy]] - ViewModel pattern details
- [[q-room-library-definition--android--easy]] - Room database

### Advanced
- [[q-workmanager-decision-guide--android--medium]] - Background work strategies
- [[q-compose-performance-optimization--android--hard]] - Compose optimization