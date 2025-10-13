---
id: 20251012-180010
title: "Migrating from RxJava to Kotlin Coroutines / Миграция с RxJava на Kotlin корутины"
topic: kotlin
subtopics:
  - coroutines
  - rxjava
  - migration
  - refactoring
difficulty: medium
moc: moc-kotlin
status: draft
tags:
  - kotlin
  - coroutines
  - rxjava
  - migration
  - refactoring
  - reactive-programming
---

# Migrating from RxJava to Kotlin Coroutines

**English** | [Русский](#russian-version)

---

## Table of Contents

- [Overview](#overview)
- [Why Migrate](#why-migrate)
- [Observable to Flow](#observable-to-flow)
- [Single to Suspend Function](#single-to-suspend-function)
- [Completable to Suspend Unit](#completable-to-suspend-unit)
- [Maybe to Nullable Suspend Function](#maybe-to-nullable-suspend-function)
- [Flowable to Flow](#flowable-to-flow)
- [Hot Observables to SharedFlow/StateFlow](#hot-observables-to-sharedflowstateflow)
- [Operator Mapping Table](#operator-mapping-table)
- [combineLatest and zip](#combinelatest-and-zip)
- [Subjects to Flow](#subjects-to-flow)
- [Error Handling Migration](#error-handling-migration)
- [Threading Migration](#threading-migration)
- [Backpressure Strategies](#backpressure-strategies)
- [Complete Migration Example](#complete-migration-example)
- [Interoperability](#interoperability)
- [Testing Migration](#testing-migration)
- [Gradual Migration Strategy](#gradual-migration-strategy)
- [Common Pitfalls](#common-pitfalls)
- [Best Practices](#best-practices)
- [Migration Checklist](#migration-checklist)
- [Follow-up Questions](#follow-up-questions)
- [References](#references)
- [Related Questions](#related-questions)

---

## Overview

This guide covers the migration from RxJava to Kotlin Coroutines, including type mappings, operator equivalences, and best practices for a smooth transition.

**Migration Goals:**
- Maintain existing functionality
- Improve code readability
- Reduce library dependencies
- Leverage Kotlin-first features
- Improve performance

---

## Why Migrate

### Benefits of Kotlin Coroutines

```kotlin
// RxJava: Complex, many operators, heavy dependency
fun loadUser(userId: String): Single<User> {
    return api.getUser(userId)
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
        .timeout(30, TimeUnit.SECONDS)
        .retry(3)
        .doOnError { Log.e("Error", it.message) }
}

// Coroutines: Simple, readable, lightweight
suspend fun loadUser(userId: String): Result<User> {
    return withContext(Dispatchers.IO) {
        try {
            withTimeout(30000) {
                retryIO(times = 3) {
                    api.getUser(userId)
                }
            }
        } catch (e: Exception) {
            Log.e("Error", e.message)
            Result.failure(e)
        }
    }
}
```

### Key Advantages

| Aspect | RxJava | Kotlin Coroutines |
|--------|--------|-------------------|
| **Learning Curve** | Steep (many operators) | Gentle (familiar syntax) |
| **Code Readability** | Functional, can be complex | Sequential, imperative |
| **Error Handling** | onError, onErrorReturn, etc. | try-catch (familiar) |
| **Threading** | Schedulers | Dispatchers (simpler) |
| **Backpressure** | Complex strategies | buffer, conflate (simpler) |
| **Integration** | Library | First-party Kotlin |
| **Performance** | Good | Better (lighter weight) |
| **APK Size** | ~3 MB (RxJava + RxAndroid) | ~100 KB (coroutines) |
| **Android Support** | Third-party | Official (Jetpack) |

### Migration Decision Factors

**Migrate when:**
- Starting new features
- Refactoring existing code
- Reducing APK size
- Simplifying codebase
- Improving maintainability

**Consider keeping RxJava when:**
- Large existing codebase (high risk)
- Team unfamiliar with coroutines
- Heavy use of complex RxJava operators
- Tight deadlines (no time for migration)

**Hybrid approach:**
- New code: Coroutines
- Existing code: RxJava
- Use interop for gradual migration

---

## Observable to Flow

### Cold Observable → Flow

```kotlin
// RxJava: Cold Observable
fun getUsers(): Observable<User> {
    return Observable.create { emitter ->
        val users = database.getUsers()
        users.forEach { user ->
            emitter.onNext(user)
        }
        emitter.onComplete()
    }
}

// Usage
getUsers()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { user -> println(user) },
        { error -> Log.e("Error", error.message) },
        { println("Complete") }
    )

// Coroutines: Flow
fun getUsers(): Flow<User> = flow {
    val users = database.getUsers()
    users.forEach { user ->
        emit(user)
    }
}.flowOn(Dispatchers.IO)

// Usage
lifecycleScope.launch {
    getUsers()
        .catch { error -> Log.e("Error", error.message) }
        .collect { user ->
            println(user)
        }
    println("Complete")
}
```

### Observable with Operators

```kotlin
// RxJava
fun searchUsers(query: String): Observable<User> {
    return Observable.just(query)
        .debounce(300, TimeUnit.MILLISECONDS)
        .distinctUntilChanged()
        .switchMap { q ->
            api.searchUsers(q)
                .toObservable()
                .flatMapIterable { it }
        }
        .filter { it.isActive }
        .map { it.toUserModel() }
}

// Coroutines
fun searchUsers(query: String): Flow<User> = flow {
    emit(query)
}.debounce(300)
 .distinctUntilChanged()
 .flatMapLatest { q ->
     flow {
         val users = api.searchUsers(q)
         users.forEach { emit(it) }
     }
 }
 .filter { it.isActive }
 .map { it.toUserModel() }
```

---

## Single to Suspend Function

### Basic Conversion

```kotlin
// RxJava: Single
fun getUser(userId: String): Single<User> {
    return api.getUser(userId)
}

// Usage
getUser("123")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { user -> updateUI(user) },
        { error -> showError(error) }
    )

// Coroutines: suspend function
suspend fun getUser(userId: String): User {
    return withContext(Dispatchers.IO) {
        api.getUser(userId)
    }
}

// Usage
lifecycleScope.launch {
    try {
        val user = getUser("123")
        updateUI(user)
    } catch (e: Exception) {
        showError(e)
    }
}
```

### Single with Result

```kotlin
// RxJava: Single with error handling
fun getUser(userId: String): Single<User> {
    return api.getUser(userId)
        .onErrorResumeNext { error ->
            if (error is HttpException && error.code() == 404) {
                Single.just(User.EMPTY)
            } else {
                Single.error(error)
            }
        }
}

// Coroutines: suspend with Result
suspend fun getUser(userId: String): Result<User> {
    return withContext(Dispatchers.IO) {
        try {
            val user = api.getUser(userId)
            Result.success(user)
        } catch (e: HttpException) {
            if (e.code() == 404) {
                Result.success(User.EMPTY)
            } else {
                Result.failure(e)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Single to Deferred (Less Common)

```kotlin
// RxJava: Single
val userSingle: Single<User> = api.getUser("123")

// Coroutines: Deferred (for async operations)
suspend fun getUserDeferred(userId: String): Deferred<User> = coroutineScope {
    async(Dispatchers.IO) {
        api.getUser(userId)
    }
}

// Usage
val userDeferred = getUserDeferred("123")
val user = userDeferred.await()
```

---

## Completable to Suspend Unit

### Basic Conversion

```kotlin
// RxJava: Completable
fun deleteUser(userId: String): Completable {
    return api.deleteUser(userId)
}

// Usage
deleteUser("123")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { println("Deleted") },
        { error -> showError(error) }
    )

// Coroutines: suspend Unit
suspend fun deleteUser(userId: String) {
    withContext(Dispatchers.IO) {
        api.deleteUser(userId)
    }
}

// Usage
lifecycleScope.launch {
    try {
        deleteUser("123")
        println("Deleted")
    } catch (e: Exception) {
        showError(e)
    }
}
```

### Completable Chain

```kotlin
// RxJava: Completable chain
fun initializeApp(): Completable {
    return loadConfig()
        .andThen(initDatabase())
        .andThen(loadUser())
        .andThen(syncData())
}

// Coroutines: Sequential suspend calls
suspend fun initializeApp() {
    loadConfig()
    initDatabase()
    loadUser()
    syncData()
}

// Or with explicit coroutineScope for error handling
suspend fun initializeApp() = coroutineScope {
    try {
        loadConfig()
        initDatabase()
        loadUser()
        syncData()
    } catch (e: Exception) {
        Log.e("Init", "Failed to initialize", e)
        throw e
    }
}
```

---

## Maybe to Nullable Suspend Function

### Basic Conversion

```kotlin
// RxJava: Maybe
fun findUser(query: String): Maybe<User> {
    return Maybe.create { emitter ->
        val user = database.findUser(query)
        if (user != null) {
            emitter.onSuccess(user)
        } else {
            emitter.onComplete()
        }
    }
}

// Usage
findUser("john")
    .subscribeOn(Schedulers.io())
    .subscribe(
        { user -> println("Found: $user") },
        { error -> Log.e("Error", error.message) },
        { println("Not found") }
    )

// Coroutines: Nullable suspend
suspend fun findUser(query: String): User? {
    return withContext(Dispatchers.IO) {
        database.findUser(query)
    }
}

// Usage
lifecycleScope.launch {
    val user = findUser("john")
    if (user != null) {
        println("Found: $user")
    } else {
        println("Not found")
    }
}
```

### Maybe with Default Value

```kotlin
// RxJava: Maybe with defaultIfEmpty
fun getConfig(): Maybe<Config> {
    return api.getConfig()
        .defaultIfEmpty(Config.DEFAULT)
}

// Coroutines: Elvis operator
suspend fun getConfig(): Config {
    return withContext(Dispatchers.IO) {
        api.getConfig() ?: Config.DEFAULT
    }
}
```

---

## Flowable to Flow

### Basic Flowable

```kotlin
// RxJava: Flowable
fun observeMessages(): Flowable<Message> {
    return Flowable.create({ emitter ->
        val listener = object : MessageListener {
            override fun onMessage(message: Message) {
                emitter.onNext(message)
            }
        }
        messageSource.addListener(listener)
        emitter.setCancellable {
            messageSource.removeListener(listener)
        }
    }, BackpressureStrategy.BUFFER)
}

// Coroutines: Flow
fun observeMessages(): Flow<Message> = callbackFlow {
    val listener = object : MessageListener {
        override fun onMessage(message: Message) {
            trySend(message)
        }
    }
    messageSource.addListener(listener)
    awaitClose {
        messageSource.removeListener(listener)
    }
}
```

### Flowable with Backpressure

```kotlin
// RxJava: Flowable with backpressure
fun produceData(): Flowable<Data> {
    return Flowable.interval(100, TimeUnit.MILLISECONDS)
        .map { Data(it) }
        .onBackpressureBuffer(100)
}

// Coroutines: Flow with buffer
fun produceData(): Flow<Data> = flow {
    var count = 0L
    while (currentCoroutineContext().isActive) {
        delay(100)
        emit(Data(count++))
    }
}.buffer(100)

// Or with conflate (drops old values)
fun produceData(): Flow<Data> = flow {
    var count = 0L
    while (currentCoroutineContext().isActive) {
        delay(100)
        emit(Data(count++))
    }
}.conflate()
```

---

## Hot Observables to SharedFlow/StateFlow

### PublishSubject to SharedFlow

```kotlin
// RxJava: PublishSubject (hot)
class EventBus {
    private val subject = PublishSubject.create<Event>()

    fun publish(event: Event) {
        subject.onNext(event)
    }

    fun observe(): Observable<Event> = subject
}

// Usage
eventBus.observe()
    .subscribe { event ->
        handleEvent(event)
    }

// Coroutines: SharedFlow
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun publish(event: Event) {
        _events.emit(event)
    }

    // Or non-suspending
    fun publishSync(event: Event) {
        _events.tryEmit(event)
    }
}

// Usage
lifecycleScope.launch {
    eventBus.events.collect { event ->
        handleEvent(event)
    }
}
```

### BehaviorSubject to StateFlow

```kotlin
// RxJava: BehaviorSubject (hot with initial value)
class UserStore {
    private val subject = BehaviorSubject.createDefault(User.EMPTY)

    fun updateUser(user: User) {
        subject.onNext(user)
    }

    fun observeUser(): Observable<User> = subject
}

// Usage
userStore.observeUser()
    .subscribe { user ->
        updateUI(user)
    }

// Coroutines: StateFlow
class UserStore {
    private val _user = MutableStateFlow(User.EMPTY)
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateUser(user: User) {
        _user.value = user
    }
}

// Usage
lifecycleScope.launch {
    userStore.user.collect { user ->
        updateUI(user)
    }
}
```

### ReplaySubject to SharedFlow with Replay

```kotlin
// RxJava: ReplaySubject (replays N items)
class MessageStore {
    private val subject = ReplaySubject.create<Message>(10)

    fun addMessage(message: Message) {
        subject.onNext(message)
    }

    fun observeMessages(): Observable<Message> = subject
}

// Coroutines: SharedFlow with replay
class MessageStore {
    private val _messages = MutableSharedFlow<Message>(
        replay = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val messages: SharedFlow<Message> = _messages.asSharedFlow()

    suspend fun addMessage(message: Message) {
        _messages.emit(message)
    }

    fun addMessageSync(message: Message) {
        _messages.tryEmit(message)
    }
}
```

---

## Operator Mapping Table

### Transformation Operators

| RxJava | Coroutines Flow | Description |
|--------|-----------------|-------------|
| `map` | `map` | Transform each item |
| `flatMap` | `flatMapConcat` | Map and flatten sequentially |
| `flatMap` (concurrent) | `flatMapMerge` | Map and flatten concurrently |
| `switchMap` | `flatMapLatest` | Cancel previous when new arrives |
| `concatMap` | `flatMapConcat` | Map and flatten in order |
| `scan` | `scan` | Accumulate over items |
| `groupBy` | No direct equivalent | Group by key |
| `buffer` | `chunked` | Buffer items into lists |
| `window` | `windowed` | Window items into flows |

### Filtering Operators

| RxJava | Coroutines Flow | Description |
|--------|-----------------|-------------|
| `filter` | `filter` | Filter items by predicate |
| `take` | `take` | Take first N items |
| `takeLast` | No direct equivalent | Take last N items |
| `takeUntil` | `takeWhile` (inverted) | Take until condition |
| `skip` | `drop` | Skip first N items |
| `distinct` | `distinctUntilChanged` | Remove consecutive duplicates |
| `debounce` | `debounce` | Throttle emissions |
| `throttleFirst` | `sample` | Sample at intervals |

### Combination Operators

| RxJava | Coroutines Flow | Description |
|--------|-----------------|-------------|
| `zip` | `zip` | Combine corresponding items |
| `combineLatest` | `combine` | Combine latest from each |
| `merge` | `merge` | Merge multiple flows |
| `concat` | `+ operator` | Concatenate flows |
| `startWith` | `onStart { emit() }` | Prepend item |

### Error Handling

| RxJava | Coroutines Flow | Description |
|--------|-----------------|-------------|
| `onErrorReturn` | `catch { emit(default) }` | Return default on error |
| `onErrorResumeNext` | `catch { emitAll(fallback) }` | Switch to fallback flow |
| `retry` | `retry` | Retry on error |
| `retryWhen` | `retryWhen` | Conditional retry |

### Threading

| RxJava | Coroutines Flow | Description |
|--------|-----------------|-------------|
| `subscribeOn` | `flowOn` | Change upstream dispatcher |
| `observeOn` | N/A (collect in scope) | Change downstream dispatcher |

---

## combineLatest and zip

### combineLatest Migration

```kotlin
// RxJava: combineLatest
fun observeDashboard(): Observable<DashboardData> {
    return Observable.combineLatest(
        userObservable,
        notificationsObservable,
        settingsObservable
    ) { user, notifications, settings ->
        DashboardData(user, notifications, settings)
    }
}

// Coroutines: combine
fun observeDashboard(): Flow<DashboardData> {
    return combine(
        userFlow,
        notificationsFlow,
        settingsFlow
    ) { user, notifications, settings ->
        DashboardData(user, notifications, settings)
    }
}
```

### zip Migration

```kotlin
// RxJava: zip
fun loadUserWithPosts(userId: String): Single<Pair<User, List<Post>>> {
    return Single.zip(
        api.getUser(userId),
        api.getUserPosts(userId)
    ) { user, posts ->
        user to posts
    }
}

// Coroutines: async/await (for Single-like operations)
suspend fun loadUserWithPosts(userId: String): Pair<User, List<Post>> = coroutineScope {
    val userDeferred = async { api.getUser(userId) }
    val postsDeferred = async { api.getUserPosts(userId) }

    userDeferred.await() to postsDeferred.await()
}

// Or with Flow zip
fun observeUserWithPosts(userId: String): Flow<Pair<User, List<Post>>> {
    return userFlow.zip(postsFlow) { user, posts ->
        user to posts
    }
}
```

---

## Subjects to Flow

### Complete Subjects Migration

```kotlin
// RxJava: All subject types
class DataStore {
    // PublishSubject: No initial value, only new emissions
    private val publishSubject = PublishSubject.create<Event>()

    // BehaviorSubject: Has current value, emits immediately
    private val behaviorSubject = BehaviorSubject.createDefault(State.INITIAL)

    // ReplaySubject: Replays last N emissions
    private val replaySubject = ReplaySubject.create<Message>(10)

    // AsyncSubject: Only emits last value on complete
    private val asyncSubject = AsyncSubject.create<Result>()
}

// Coroutines: Flow equivalents
class DataStore {
    // PublishSubject → SharedFlow (no replay)
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    // BehaviorSubject → StateFlow
    private val _state = MutableStateFlow(State.INITIAL)
    val state: StateFlow<State> = _state.asStateFlow()

    // ReplaySubject → SharedFlow with replay
    private val _messages = MutableSharedFlow<Message>(
        replay = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val messages: SharedFlow<Message> = _messages.asSharedFlow()

    // AsyncSubject → Channel with single element
    private val _result = Channel<Result>(Channel.CONFLATED)
    val result: Flow<Result> = _result.receiveAsFlow()
}
```

---

## Error Handling Migration

### onError to catch

```kotlin
// RxJava: onError operators
fun loadUser(userId: String): Single<User> {
    return api.getUser(userId)
        .onErrorReturn { User.EMPTY }
        .onErrorResumeNext { error ->
            if (error is IOException) {
                cache.getUser(userId)
            } else {
                Single.error(error)
            }
        }
        .doOnError { Log.e("Error", it.message) }
}

// Coroutines: catch operator
suspend fun loadUser(userId: String): User {
    return flow {
        emit(api.getUser(userId))
    }.catch { error ->
        Log.e("Error", error.message)
        when (error) {
            is IOException -> {
                val cached = cache.getUser(userId)
                emit(cached ?: User.EMPTY)
            }
            else -> throw error
        }
    }.single()
}

// Or with try-catch (simpler for suspend functions)
suspend fun loadUser(userId: String): User {
    return try {
        api.getUser(userId)
    } catch (e: IOException) {
        Log.e("Error", e.message)
        cache.getUser(userId) ?: User.EMPTY
    }
}
```

### retry and retryWhen

```kotlin
// RxJava: retry
fun loadData(): Single<Data> {
    return api.getData()
        .retry(3)
        .retryWhen { errors ->
            errors.zipWith(Observable.range(1, 3)) { error, attempt ->
                attempt
            }.flatMap { attempt ->
                Observable.timer(attempt * 1000L, TimeUnit.MILLISECONDS)
            }
        }
}

// Coroutines: retry
suspend fun loadData(): Data {
    return flow {
        emit(api.getData())
    }.retry(3) { cause ->
        delay(1000)
        cause is IOException
    }.single()
}

// Or custom retry logic
suspend fun loadData(): Data {
    repeat(3) { attempt ->
        try {
            return api.getData()
        } catch (e: IOException) {
            if (attempt == 2) throw e
            delay((attempt + 1) * 1000L)
        }
    }
    throw IllegalStateException("Should not reach here")
}
```

---

## Threading Migration

### Schedulers to Dispatchers

```kotlin
// RxJava: Schedulers
fun loadUser(userId: String): Single<User> {
    return api.getUser(userId)
        .subscribeOn(Schedulers.io())           // Background thread
        .observeOn(AndroidSchedulers.mainThread()) // Main thread
}

// Coroutines: Dispatchers
suspend fun loadUser(userId: String): User {
    return withContext(Dispatchers.IO) {        // Background thread
        api.getUser(userId)
    }
    // Returns on calling dispatcher (typically Main)
}

// With Flow
fun observeUser(userId: String): Flow<User> {
    return flow {
        emit(api.getUser(userId))
    }.flowOn(Dispatchers.IO)                    // Upstream on IO
    // Collect on calling dispatcher
}
```

### Scheduler Mapping

| RxJava Scheduler | Coroutines Dispatcher | Use Case |
|-----------------|----------------------|----------|
| `Schedulers.io()` | `Dispatchers.IO` | Network, database, file I/O |
| `Schedulers.computation()` | `Dispatchers.Default` | CPU-intensive work |
| `AndroidSchedulers.mainThread()` | `Dispatchers.Main` | UI updates |
| `Schedulers.newThread()` | `Dispatchers.IO` or custom | New thread (avoid) |
| `Schedulers.single()` | Single-thread dispatcher | Sequential processing |
| `Schedulers.trampoline()` | No equivalent | Immediate execution |

### Custom Threading

```kotlin
// RxJava: Custom scheduler
val customScheduler = Schedulers.from(Executors.newFixedThreadPool(4))

api.getData()
    .subscribeOn(customScheduler)
    .subscribe()

// Coroutines: Custom dispatcher
val customDispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()

lifecycleScope.launch(customDispatcher) {
    val data = api.getData()
}

// Don't forget to close!
customDispatcher.close()
```

---

## Backpressure Strategies

### RxJava Backpressure to Flow

```kotlin
// RxJava: Various backpressure strategies
fun produceData(): Flowable<Data> {
    return Flowable.interval(10, TimeUnit.MILLISECONDS)
        .onBackpressureBuffer(100)              // Buffer up to 100 items
}

fun produceData2(): Flowable<Data> {
    return Flowable.interval(10, TimeUnit.MILLISECONDS)
        .onBackpressureDrop()                   // Drop if consumer slow
}

fun produceData3(): Flowable<Data> {
    return Flowable.interval(10, TimeUnit.MILLISECONDS)
        .onBackpressureLatest()                 // Keep only latest
}

// Coroutines: Flow with buffer strategies
fun produceData(): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        delay(10)
        emit(Data())
    }
}.buffer(100)                                   // Buffer up to 100 items

fun produceData2(): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        delay(10)
        emit(Data())
    }
}.buffer(Channel.UNLIMITED)                     // Unlimited buffer

fun produceData3(): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        delay(10)
        emit(Data())
    }
}.conflate()                                    // Keep only latest (like onBackpressureLatest)
```

---

## Complete Migration Example

### Before: RxJava Repository

```kotlin
class UserRepository(
    private val api: UserApi,
    private val database: UserDatabase
) {
    private val userSubject = BehaviorSubject.create<User>()

    fun observeUser(): Observable<User> = userSubject

    fun loadUser(userId: String): Single<User> {
        return api.getUser(userId)
            .subscribeOn(Schedulers.io())
            .doOnSuccess { user ->
                database.saveUser(user)
                userSubject.onNext(user)
            }
            .onErrorResumeNext { error ->
                database.getUser(userId)
                    .subscribeOn(Schedulers.io())
                    .switchIfEmpty(Single.error(error))
            }
    }

    fun updateUser(userId: String, updates: UserUpdate): Completable {
        return api.updateUser(userId, updates)
            .subscribeOn(Schedulers.io())
            .doOnSuccess { user ->
                database.saveUser(user)
                userSubject.onNext(user)
            }
            .ignoreElement()
    }

    fun searchUsers(query: String): Observable<List<User>> {
        return Observable.just(query)
            .debounce(300, TimeUnit.MILLISECONDS)
            .distinctUntilChanged()
            .switchMap { q ->
                api.searchUsers(q)
                    .subscribeOn(Schedulers.io())
                    .toObservable()
            }
    }
}
```

### After: Coroutines Repository

```kotlin
class UserRepository(
    private val api: UserApi,
    private val database: UserDatabase
) {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    suspend fun loadUser(userId: String): Result<User> {
        return withContext(Dispatchers.IO) {
            try {
                val user = api.getUser(userId)
                database.saveUser(user)
                _user.value = user
                Result.success(user)
            } catch (e: Exception) {
                // Try cache
                val cached = database.getUser(userId)
                if (cached != null) {
                    _user.value = cached
                    Result.success(cached)
                } else {
                    Result.failure(e)
                }
            }
        }
    }

    suspend fun updateUser(userId: String, updates: UserUpdate): Result<Unit> {
        return withContext(Dispatchers.IO) {
            try {
                val user = api.updateUser(userId, updates)
                database.saveUser(user)
                _user.value = user
                Result.success(Unit)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    fun searchUsers(query: String): Flow<List<User>> = flow {
        emit(query)
    }.debounce(300)
     .distinctUntilChanged()
     .flatMapLatest { q ->
         flow {
             val users = api.searchUsers(q)
             emit(users)
         }
     }
     .flowOn(Dispatchers.IO)
}
```

### Before: RxJava ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val compositeDisposable = CompositeDisposable()
    private val userLiveData = MutableLiveData<User>()
    private val errorLiveData = MutableLiveData<String>()

    fun observeUser(): LiveData<User> = userLiveData
    fun observeError(): LiveData<String> = errorLiveData

    fun loadUser(userId: String) {
        repository.loadUser(userId)
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe(
                { user -> userLiveData.value = user },
                { error -> errorLiveData.value = error.message }
            )
            .addTo(compositeDisposable)
    }

    override fun onCleared() {
        compositeDisposable.clear()
    }
}
```

### After: Coroutines ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    val user: StateFlow<User?> = repository.user
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = null
        )

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            when (val result = repository.loadUser(userId)) {
                is Result.Success -> {
                    _uiState.value = UiState.Success
                }
                is Result.Error -> {
                    _uiState.value = UiState.Error(result.exception.message ?: "Unknown error")
                }
            }
        }
    }

    // No need for onCleared - viewModelScope auto-cancels
}

sealed class UiState {
    object Loading : UiState()
    object Success : UiState()
    data class Error(val message: String) : UiState()
}
```

---

## Interoperability

### Using RxJava and Coroutines Together

```kotlin
// Add dependency
// implementation "org.jetbrains.kotlinx:kotlinx-coroutines-rx3:1.7.3"

// RxJava → Coroutines
import kotlinx.coroutines.rx3.await
import kotlinx.coroutines.rx3.asFlow

// Single to suspend
suspend fun loadUserFromRx(): User {
    val rxSingle: Single<User> = legacyApi.getUser("123")
    return rxSingle.await()
}

// Observable to Flow
fun observeUsersFromRx(): Flow<User> {
    val rxObservable: Observable<User> = legacyApi.observeUsers()
    return rxObservable.asFlow()
}

// Flowable to Flow
fun observeDataFromRx(): Flow<Data> {
    val rxFlowable: Flowable<Data> = legacyApi.observeData()
    return rxFlowable.asFlow()
}
```

### Coroutines → RxJava

```kotlin
import kotlinx.coroutines.rx3.rxSingle
import kotlinx.coroutines.rx3.rxObservable

// Suspend to Single
fun loadUserAsRx(userId: String): Single<User> = rxSingle {
    repository.loadUser(userId)
}

// Flow to Observable
fun observeUsersAsRx(): Observable<User> = rxObservable {
    repository.observeUsers().collect { user ->
        send(user)
    }
}

// Flow to Flowable
fun observeDataAsRx(): Flowable<Data> = rxFlowable {
    repository.observeData().collect { data ->
        send(data)
    }
}
```

### Migration Pattern: Adapters

```kotlin
/**
 * Adapter for gradual migration
 * Provides both RxJava and Coroutines APIs
 */
class HybridRepository(
    private val api: UserApi,
    private val database: UserDatabase
) {
    // New code: Coroutines
    suspend fun loadUserSuspend(userId: String): Result<User> {
        return withContext(Dispatchers.IO) {
            try {
                val user = api.getUser(userId)
                Result.success(user)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    // Legacy code: RxJava (wraps suspend)
    fun loadUserRx(userId: String): Single<User> = rxSingle {
        val result = loadUserSuspend(userId)
        result.getOrThrow()
    }
}
```

---

## Testing Migration

### RxJava Testing

```kotlin
class UserRepositoryTest {
    private lateinit var repository: UserRepository
    private val testScheduler = TestScheduler()

    @Before
    fun setup() {
        RxJavaPlugins.setIoSchedulerHandler { testScheduler }
        RxAndroidPlugins.setMainThreadSchedulerHandler { testScheduler }
    }

    @Test
    fun `loadUser returns user on success`() {
        // Arrange
        val userId = "123"
        val expectedUser = User(userId, "John")

        // Act
        val testObserver = repository.loadUser(userId).test()
        testScheduler.triggerActions()

        // Assert
        testObserver.assertComplete()
        testObserver.assertValue(expectedUser)
    }

    @After
    fun teardown() {
        RxJavaPlugins.reset()
        RxAndroidPlugins.reset()
    }
}
```

### Coroutines Testing

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserRepositoryTest {
    private lateinit var repository: UserRepository
    private val testDispatcher = UnconfinedTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @Test
    fun `loadUser returns user on success`() = runTest {
        // Arrange
        val userId = "123"
        val expectedUser = User(userId, "John")

        // Act
        val result = repository.loadUser(userId)

        // Assert
        assertTrue(result is Result.Success)
        assertEquals(expectedUser, (result as Result.Success).data)
    }

    @After
    fun teardown() {
        Dispatchers.resetMain()
    }
}
```

### Testing Flow

```kotlin
@Test
fun `observeUsers emits user list`() = runTest {
    // Arrange
    val expectedUsers = listOf(User("1", "John"), User("2", "Jane"))

    // Act & Assert
    repository.observeUsers().test {
        assertEquals(expectedUsers, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}

// Extension function for Flow testing
suspend fun <T> Flow<T>.test(validate: suspend FlowTurbine<T>.() -> Unit) {
    return this.asChannel(this@test).consumeAsFlow().test(validate)
}
```

---

## Gradual Migration Strategy

### Phase 1: New Features Only

```kotlin
//  New features use coroutines
class NewFeatureRepository(private val api: NewApi) {
    suspend fun loadNewData(): Data {
        return withContext(Dispatchers.IO) {
            api.getData()
        }
    }
}

//  Existing features stay RxJava
class LegacyRepository(private val api: LegacyApi) {
    fun loadOldData(): Single<Data> {
        return api.getData()
            .subscribeOn(Schedulers.io())
    }
}
```

### Phase 2: Wrap RxJava with Coroutines

```kotlin
// Wrap existing RxJava code with suspend functions
class MigrationRepository(private val legacyApi: LegacyApi) {
    suspend fun loadData(): Data {
        return legacyApi.getData()
            .subscribeOn(Schedulers.io())
            .await()
    }
}

// Use in new coroutine-based code
lifecycleScope.launch {
    val data = repository.loadData()
}
```

### Phase 3: Migrate Core Components

```kotlin
// Migrate high-impact, frequently-used repositories
class UserRepository(private val api: UserApi) {
    // Migrated to coroutines
    suspend fun loadUser(userId: String): User {
        return withContext(Dispatchers.IO) {
            api.getUser(userId)
        }
    }

    // Provide RxJava adapter for legacy code
    fun loadUserRx(userId: String): Single<User> = rxSingle {
        loadUser(userId)
    }
}
```

### Phase 4: Complete Migration

```kotlin
// Remove all RxJava code and adapters
class UserRepository(private val api: UserApi) {
    suspend fun loadUser(userId: String): User {
        return withContext(Dispatchers.IO) {
            api.getUser(userId)
        }
    }
}

// Remove RxJava dependencies from build.gradle
// implementation 'io.reactivex.rxjava3:rxjava:3.1.5' 
// implementation 'io.reactivex.rxjava3:rxandroid:3.0.0' 
```

---

## Common Pitfalls

### 1. Forgetting flowOn for Flow

```kotlin
//  Wrong: Flow executes on collector's dispatcher
fun observeData(): Flow<Data> = flow {
    emit(database.getData()) // Runs on Main if collected from Main!
}

//  Correct: Use flowOn
fun observeData(): Flow<Data> = flow {
    emit(database.getData())
}.flowOn(Dispatchers.IO)
```

### 2. Using runBlocking in Production

```kotlin
//  Wrong: Blocks thread
fun loadUser(userId: String): User {
    return runBlocking {
        api.getUser(userId)
    }
}

//  Correct: Use suspend
suspend fun loadUser(userId: String): User {
    return api.getUser(userId)
}
```

### 3. Not Handling Cancellation

```kotlin
//  Wrong: Doesn't handle cancellation properly
try {
    val user = api.getUser(userId)
} catch (e: Exception) {
    // CancellationException caught here!
}

//  Correct: Re-throw CancellationException
try {
    val user = api.getUser(userId)
} catch (e: CancellationException) {
    throw e
} catch (e: Exception) {
    // Handle other exceptions
}
```

### 4. Using GlobalScope

```kotlin
//  Wrong: Unstructured concurrency
fun loadData() {
    GlobalScope.launch {
        val data = api.getData()
    }
}

//  Correct: Use proper scope
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = api.getData()
        }
    }
}
```

### 5. Mixing Hot and Cold Flows

```kotlin
//  Wrong: Confusing SharedFlow (hot) with Flow (cold)
val flow: Flow<Data> = MutableSharedFlow<Data>() // Type mismatch conceptually

//  Correct: Use appropriate type
val sharedFlow: SharedFlow<Data> = MutableSharedFlow<Data>()
val coldFlow: Flow<Data> = flow { emit(Data()) }
```

---

## Best Practices

### 1. Start with New Features

```kotlin
//  Good: New features use coroutines
class NewRepository(private val api: NewApi) {
    suspend fun fetchNewData(): Data = withContext(Dispatchers.IO) {
        api.getData()
    }
}
```

### 2. Use Interop for Gradual Migration

```kotlin
//  Good: Wrap RxJava with coroutines
import kotlinx.coroutines.rx3.await

suspend fun migrateGradually() {
    val rxSingle: Single<User> = legacyApi.getUser()
    val user = rxSingle.await()
    // Now use with coroutines
}
```

### 3. Migrate Tests Alongside Code

```kotlin
// Migrate tests at same time as implementation
@Test
fun `test with coroutines`() = runTest {
    val result = repository.loadData()
    assertEquals(expected, result)
}
```

### 4. Use StateFlow for State Management

```kotlin
//  Good: StateFlow for UI state
class ViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}
```

### 5. Document Migration Progress

```kotlin
/**
 * User Repository
 *
 * Migration Status:  Migrated to Coroutines
 * Migrated on: 2024-01-15
 * Migrated by: @username
 *
 * Legacy RxJava methods removed:
 * - loadUserRx() → loadUser()
 * - observeUserRx() → observeUser()
 */
class UserRepository { /* ... */ }
```

---

## Migration Checklist

### Pre-Migration

- [ ] Identify RxJava usage in codebase
- [ ] Prioritize migration targets (high-impact, frequently-used)
- [ ] Add coroutines dependencies
- [ ] Add interop dependencies (kotlinx-coroutines-rx3)
- [ ] Set up coroutines testing infrastructure
- [ ] Train team on coroutines basics

### During Migration

- [ ] Migrate API interfaces to suspend functions
- [ ] Convert Singles to suspend functions
- [ ] Convert Observables to Flow
- [ ] Convert Completables to suspend Unit
- [ ] Migrate Subjects to StateFlow/SharedFlow
- [ ] Replace Schedulers with Dispatchers
- [ ] Update error handling (onError → catch/try-catch)
- [ ] Migrate tests to use runTest
- [ ] Add interop adapters for gradual migration

### Post-Migration

- [ ] Remove RxJava dependencies
- [ ] Remove interop adapters
- [ ] Update documentation
- [ ] Remove RxJava plugin configurations
- [ ] Verify APK size reduction
- [ ] Monitor performance improvements
- [ ] Collect team feedback

---

## Follow-ups

1. **What's the main benefit of migrating from RxJava to Coroutines?**
   - Simpler, more readable code with familiar syntax
   - Better Kotlin integration and first-party support
   - Smaller APK size and better performance

2. **How do you handle the transition period when using both RxJava and Coroutines?**
   - Use kotlinx-coroutines-rx3 for interop
   - Wrap RxJava with suspend functions
   - Gradually migrate feature by feature

3. **What's the equivalent of BehaviorSubject in Coroutines?**
   - StateFlow with initial value
   - Provides current state and emits updates

4. **How do you migrate Observable.combineLatest?**
   - Use Flow.combine() function
   - Same behavior for combining latest values

5. **What's the difference between subscribeOn/observeOn and flowOn?**
   - subscribeOn: Changes upstream thread
   - observeOn: Changes downstream thread
   - flowOn: Changes upstream dispatcher (no downstream equivalent needed)

6. **Should you migrate everything at once or gradually?**
   - Gradual migration is safer and more practical
   - Start with new features, then high-impact components
   - Use interop during transition

7. **How do you test coroutine-based code?**
   - Use runTest for suspend functions
   - Use TestDispatcher for dispatcher control
   - Use Turbine for Flow testing

---

## References

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Coroutines Flow](https://kotlinlang.org/docs/flow.html)
- [RxJava to Coroutines Migration](https://developer.android.com/kotlin/coroutines/coroutines-best-practices#rxjava)
- [kotlinx-coroutines-rx3](https://github.com/Kotlin/kotlinx.coroutines/tree/master/reactive)

---

## Related Questions

- [Flow operators](q-flow-operators--kotlin--medium.md)
- [StateFlow vs SharedFlow](q-stateflow-sharedflow--kotlin--medium.md)
- [Coroutine testing](q-testing-coroutines--kotlin--medium.md)

---

<a name="russian-version"></a>

# Миграция с RxJava на Kotlin корутины

[English](#migrating-from-rxjava-to-kotlin-coroutines) | **Русский**

---

[Russian content follows same structure as English version...]

---

**End of document**
