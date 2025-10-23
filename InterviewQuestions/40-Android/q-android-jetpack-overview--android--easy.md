---
id: 20251012-122765
title: Android Jetpack Overview / Обзор Android Jetpack
aliases:
- Android Jetpack Overview
- Обзор Android Jetpack
topic: android
subtopics:
- architecture-clean
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
- q-viewmodel-pattern--android--easy
- q-room-library-definition--android--easy
created: 2025-10-13
updated: 2025-10-15
tags:
- android/architecture-clean
- android/ui-compose
- difficulty/easy
---

## Answer (EN)
**Architecture Components** - Modern app architecture
```kotlin
// ViewModel - survives configuration changes
class UserViewModel : ViewModel() {
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users
}

// Room - SQLite ORM
@Entity(tableName = "users")
data class User(@PrimaryKey val id: Int, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>
}
```

**Navigation Component** - Screen navigation
```kotlin
// Navigation graph
findNavController().navigate(R.id.action_home_to_details)

// With arguments
val action = HomeFragmentDirections.actionHomeToDetails(userId = 123)
findNavController().navigate(action)
```

**WorkManager** - Background tasks
```kotlin
class UploadWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return try {
            uploadFile()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```

**DataStore** - Modern SharedPreferences
```kotlin
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

suspend fun savePreference(key: String, value: String) {
    context.dataStore.edit { preferences ->
        preferences[stringPreferencesKey(key)] = value
    }
}
```

**Paging** - Large dataset loading
```kotlin
class UserPagingSource(private val apiService: ApiService) : PagingSource<Int, User>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> {
        val page = params.key ?: 1
        val response = apiService.getUsers(page, params.loadSize)
        return LoadResult.Page(data = response.users, prevKey = null, nextKey = page + 1)
    }
}
```

**Hilt** - Dependency injection
```kotlin
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**Compose** - Declarative UI
```kotlin
@Composable
fun UserListScreen(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState()

    LazyColumn {
        items(users) { user ->
            UserItem(user = user)
        }
    }
}
```

| Category | Libraries | Purpose |
|----------|-----------|---------|
| Foundation | AppCompat, KTX | Basic compatibility |
| Architecture | ViewModel, Room, Navigation | App architecture |
| UI | Compose, Fragment | User interface |
| Behavior | WorkManager, Permissions | App behavior |
| Data | DataStore, Paging | Data management |

## Follow-ups

- When to migrate from SharedPreferences to DataStore?
- View-based UI vs Jetpack Compose migration strategy?
- WorkManager vs Foreground Service for background work?

## References

- https://developer.android.com/jetpack
- https://developer.android.com/topic/libraries/architecture
- https://developer.android.com/jetpack/compose

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components overview
- [[q-viewmodel-pattern--android--easy]] - ViewModel basics

### Related (Medium)
- [[q-room-library-definition--android--easy]] - Room database
- [[q-compose-basics--kotlin--easy]] - Compose fundamentals
- [[q-workmanager-decision-guide--android--medium]] - WorkManager usage

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Compose performance
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture