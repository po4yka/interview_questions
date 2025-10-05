---
tags:
  - programming-languages
difficulty: medium
---

# Zip Operator for Parallel Request Mapping

## Answer

Use **zip** operator (available in RxJava, Kotlin Flow, and coroutines). It combines multiple data streams executing them in parallel and returns their results in a single stream.

The `zip` operator is essential when you need to combine results from multiple independent async operations. In Kotlin coroutines, this is achieved using `async`/`await` or Flow's `zip` operators.

### Approach 1: Using async/await for Parallel Execution

```kotlin
import kotlinx.coroutines.*

data class UserProfile(val name: String)
data class UserPosts(val posts: List<String>)
data class UserSettings(val theme: String)
data class CombinedData(val profile: UserProfile, val posts: UserPosts, val settings: UserSettings)

suspend fun fetchUserProfile(userId: Int): UserProfile {
    delay(100)  // Simulate network call
    return UserProfile("User $userId")
}

suspend fun fetchUserPosts(userId: Int): UserPosts {
    delay(150)  // Simulate network call
    return UserPosts(listOf("Post 1", "Post 2"))
}

suspend fun fetchUserSettings(userId: Int): UserSettings {
    delay(80)  // Simulate network call
    return UserSettings("Dark")
}

// Execute three requests in parallel using async
suspend fun fetchAllUserData(userId: Int): CombinedData = coroutineScope {
    val profileDeferred = async { fetchUserProfile(userId) }
    val postsDeferred = async { fetchUserPosts(userId) }
    val settingsDeferred = async { fetchUserSettings(userId) }

    CombinedData(
        profile = profileDeferred.await(),
        posts = postsDeferred.await(),
        settings = settingsDeferred.await()
    )
}

// Usage
runBlocking {
    val startTime = System.currentTimeMillis()
    val result = fetchAllUserData(1)
    val duration = System.currentTimeMillis() - startTime

    println("Profile: ${result.profile.name}")
    println("Posts: ${result.posts.posts}")
    println("Settings: ${result.settings.theme}")
    println("Duration: ${duration}ms")  // ~150ms (parallel), not 330ms (sequential)
}
```

### Approach 2: Using Flow zip for Streaming Data

```kotlin
import kotlinx.coroutines.flow.*

fun getProfileFlow(): Flow<String> = flow {
    delay(100)
    emit("Profile Data")
}

fun getPostsFlow(): Flow<String> = flow {
    delay(150)
    emit("Posts Data")
}

fun getSettingsFlow(): Flow<String> = flow {
    delay(80)
    emit("Settings Data")
}

// Combine three flows using zip
suspend fun combineFlows() {
    getProfileFlow()
        .zip(getPostsFlow()) { profile, posts ->
            Pair(profile, posts)
        }
        .zip(getSettingsFlow()) { (profile, posts), settings ->
            Triple(profile, posts, settings)
        }
        .collect { (profile, posts, settings) ->
            println("Profile: $profile")
            println("Posts: $posts")
            println("Settings: $settings")
        }
}
```

### Approach 3: Using combine for Latest Values

```kotlin
// combine emits whenever ANY source emits (different from zip)
fun observeUserData(): Flow<CombinedData> {
    val profileFlow = flow {
        repeat(3) {
            delay(100)
            emit(UserProfile("User $it"))
        }
    }

    val postsFlow = flow {
        delay(50)
        emit(UserPosts(listOf("Post A")))
        delay(200)
        emit(UserPosts(listOf("Post B")))
    }

    val settingsFlow = flow {
        delay(75)
        emit(UserSettings("Light"))
    }

    return combine(profileFlow, postsFlow, settingsFlow) { profile, posts, settings ->
        CombinedData(profile, posts, settings)
    }
}

// Usage
runBlocking {
    observeUserData().collect { data ->
        println("Combined: ${data.profile.name}, ${data.posts.posts}, ${data.settings.theme}")
    }
}
```

### Approach 4: RxJava Style zip

```kotlin
// Using RxJava (for comparison)
import io.reactivex.rxjava3.core.Observable
import io.reactivex.rxjava3.kotlin.Observables

fun rxZipExample() {
    val observable1 = Observable.just("Profile")
    val observable2 = Observable.just("Posts")
    val observable3 = Observable.just("Settings")

    Observable.zip(
        observable1,
        observable2,
        observable3
    ) { profile, posts, settings ->
        Triple(profile, posts, settings)
    }.subscribe { (profile, posts, settings) ->
        println("$profile, $posts, $settings")
    }
}
```

### Real-World Example: Dashboard Data Loading

```kotlin
data class DashboardData(
    val userInfo: UserInfo,
    val notifications: List<Notification>,
    val activityFeed: List<Activity>
)

class DashboardRepository {
    suspend fun fetchUserInfo(): UserInfo = withContext(Dispatchers.IO) {
        // API call
        delay(200)
        UserInfo("John Doe", "john@example.com")
    }

    suspend fun fetchNotifications(): List<Notification> = withContext(Dispatchers.IO) {
        // API call
        delay(150)
        listOf(Notification("New message"), Notification("Update available"))
    }

    suspend fun fetchActivityFeed(): List<Activity> = withContext(Dispatchers.IO) {
        // API call
        delay(180)
        listOf(Activity("Login from new device"), Activity("Profile updated"))
    }
}

class DashboardViewModel {
    private val repository = DashboardRepository()

    suspend fun loadDashboard(): DashboardData = coroutineScope {
        // Launch all three requests in parallel
        val userInfoDeferred = async { repository.fetchUserInfo() }
        val notificationsDeferred = async { repository.fetchNotifications() }
        val activityDeferred = async { repository.fetchActivityFeed() }

        // Combine results
        DashboardData(
            userInfo = userInfoDeferred.await(),
            notifications = notificationsDeferred.await(),
            activityFeed = activityDeferred.await()
        )
    }
}
```

### zip vs combine vs merge

```kotlin
// zip: Waits for ALL sources, pairs elements by index
flowOf(1, 2, 3)
    .zip(flowOf("A", "B", "C")) { num, letter ->
        "$num$letter"
    }
    .collect { println(it) }  // 1A, 2B, 3C

// combine: Emits when ANY source emits, uses latest from each
flowOf(1, 2, 3)
    .combine(flowOf("A", "B")) { num, letter ->
        "$num$letter"
    }
    .collect { println(it) }  // Multiple emissions with latest values

// merge: Simply merges all emissions from all sources
merge(
    flowOf(1, 2, 3),
    flowOf(4, 5, 6)
).collect { println(it) }  // 1, 2, 3, 4, 5, 6 (or interleaved)
```

### Error Handling with Parallel Requests

```kotlin
suspend fun fetchWithErrorHandling(): Result<CombinedData> = coroutineScope {
    try {
        val profile = async { fetchUserProfile(1) }
        val posts = async { fetchUserPosts(1) }
        val settings = async { fetchUserSettings(1) }

        Result.success(
            CombinedData(
                profile.await(),
                posts.await(),
                settings.await()
            )
        )
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

### Key Differences

| Operator | Behavior | Use Case |
|----------|----------|----------|
| **zip** | Pairs elements by index, waits for all | Fixed number of parallel requests |
| **combine** | Uses latest from each, emits on any change | Real-time data synchronization |
| **merge** | Flattens all sources into one | Combining similar streams |
| **async/await** | Manual parallel execution control | Best for Kotlin coroutines |

---

## Вопрос (RU)

Чем воспользоваться когда нужно три разных запроса мапить между собой дернуть одновременно

## Ответ

Используйте zip например в RxJava Объединяет несколько потоков данных выполняя их параллельно и возвращает их результаты в одном потоке
