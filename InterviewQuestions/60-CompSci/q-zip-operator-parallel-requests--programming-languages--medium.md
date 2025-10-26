---
id: 20251016-162812
title: "Zip Operator Parallel Requests / Оператор zip для параллельных запросов"
topic: computer-science
difficulty: medium
status: draft
moc: moc-cs
related: [q-interface-vs-abstract-class--programming-languages--medium, q-iterator-pattern--design-patterns--medium, q-regular-vs-extension-method--programming-languages--easy]
created: 2025-10-15
tags: [programming-languages]
date created: Saturday, October 4th 2025, 10:39:32 am
date modified: Sunday, October 26th 2025, 1:40:05 pm
---

# Zip Operator for Parallel Request Mapping

# Question (EN)
> How do you use the zip operator for parallel request mapping?

# Вопрос (RU)
> Как использовать оператор zip для отображения параллельных запросов?

---

## Answer (EN)

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

### Approach 2: Using Flow Zip for Streaming Data

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

### Approach 3: Using Combine for Latest Values

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

### Approach 4: RxJava Style Zip

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

### Zip Vs Combine Vs Merge

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


## Ответ (RU)

Используйте оператор **zip** (доступен в RxJava, Kotlin Flow и корутинах). Он объединяет несколько потоков данных, выполняя их параллельно, и возвращает их результаты в одном потоке.

Оператор `zip` необходим, когда нужно объединить результаты из нескольких независимых асинхронных операций. В Kotlin корутинах это достигается с помощью `async`/`await` или операторов `zip` для Flow.

### Подход 1: Использование async/await Для Параллельного Выполнения

```kotlin
import kotlinx.coroutines.*

data class UserProfile(val name: String)
data class UserPosts(val posts: List<String>)
data class UserSettings(val theme: String)
data class CombinedData(val profile: UserProfile, val posts: UserPosts, val settings: UserSettings)

suspend fun fetchUserProfile(userId: Int): UserProfile {
    delay(100)  // Симуляция сетевого вызова
    return UserProfile("User $userId")
}

suspend fun fetchUserPosts(userId: Int): UserPosts {
    delay(150)  // Симуляция сетевого вызова
    return UserPosts(listOf("Post 1", "Post 2"))
}

suspend fun fetchUserSettings(userId: Int): UserSettings {
    delay(80)  // Симуляция сетевого вызова
    return UserSettings("Dark")
}

// Выполнение трех запросов параллельно с использованием async
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

// Использование
runBlocking {
    val startTime = System.currentTimeMillis()
    val result = fetchAllUserData(1)
    val duration = System.currentTimeMillis() - startTime

    println("Profile: ${result.profile.name}")
    println("Posts: ${result.posts.posts}")
    println("Settings: ${result.settings.theme}")
    println("Duration: ${duration}ms")  // ~150ms (параллельно), а не 330ms (последовательно)
}
```

### Подход 2: Использование Zip Для Flow С Потоковыми Данными

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

// Объединение трех потоков с помощью zip
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

### Подход 3: Использование Combine Для Последних Значений

```kotlin
// combine испускает всякий раз, когда ЛЮБОЙ источник испускает (отличается от zip)
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

// Использование
runBlocking {
    observeUserData().collect { data ->
        println("Combined: ${data.profile.name}, ${data.posts.posts}, ${data.settings.theme}")
    }
}
```

### Подход 4: RxJava Стиль Zip

```kotlin
// Использование RxJava (для сравнения)
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

### Реальный Пример: Загрузка Данных Панели Управления

```kotlin
data class DashboardData(
    val userInfo: UserInfo,
    val notifications: List<Notification>,
    val activityFeed: List<Activity>
)

class DashboardRepository {
    suspend fun fetchUserInfo(): UserInfo = withContext(Dispatchers.IO) {
        // API вызов
        delay(200)
        UserInfo("John Doe", "john@example.com")
    }

    suspend fun fetchNotifications(): List<Notification> = withContext(Dispatchers.IO) {
        // API вызов
        delay(150)
        listOf(Notification("New message"), Notification("Update available"))
    }

    suspend fun fetchActivityFeed(): List<Activity> = withContext(Dispatchers.IO) {
        // API вызов
        delay(180)
        listOf(Activity("Login from new device"), Activity("Profile updated"))
    }
}

class DashboardViewModel {
    private val repository = DashboardRepository()

    suspend fun loadDashboard(): DashboardData = coroutineScope {
        // Запуск всех трех запросов параллельно
        val userInfoDeferred = async { repository.fetchUserInfo() }
        val notificationsDeferred = async { repository.fetchNotifications() }
        val activityDeferred = async { repository.fetchActivityFeed() }

        // Объединение результатов
        DashboardData(
            userInfo = userInfoDeferred.await(),
            notifications = notificationsDeferred.await(),
            activityFeed = activityDeferred.await()
        )
    }
}
```

### Zip Vs Combine Vs Merge

```kotlin
// zip: Ждет ВСЕ источники, парирует элементы по индексу
flowOf(1, 2, 3)
    .zip(flowOf("A", "B", "C")) { num, letter ->
        "$num$letter"
    }
    .collect { println(it) }  // 1A, 2B, 3C

// combine: Испускает когда ЛЮБОЙ источник испускает, использует последние из каждого
flowOf(1, 2, 3)
    .combine(flowOf("A", "B")) { num, letter ->
        "$num$letter"
    }
    .collect { println(it) }  // Множественные испускания с последними значениями

// merge: Просто объединяет все испускания из всех источников
merge(
    flowOf(1, 2, 3),
    flowOf(4, 5, 6)
).collect { println(it) }  // 1, 2, 3, 4, 5, 6 (или чередуясь)
```

### Обработка Ошибок С Параллельными Запросами

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

### Ключевые Различия

| Оператор | Поведение | Применение |
|----------|----------|----------|
| **zip** | Парирует элементы по индексу, ждет всех | Фиксированное количество параллельных запросов |
| **combine** | Использует последние из каждого, испускает при любом изменении | Синхронизация данных в реальном времени |
| **merge** | Сглаживает все источники в один | Объединение похожих потоков |
| **async/await** | Ручное управление параллельным выполнением | Лучше всего для Kotlin корутин |

## Related Questions

- [[q-regular-vs-extension-method--programming-languages--easy]]
- [[q-iterator-pattern--design-patterns--medium]]
- [[q-interface-vs-abstract-class--programming-languages--medium]]
