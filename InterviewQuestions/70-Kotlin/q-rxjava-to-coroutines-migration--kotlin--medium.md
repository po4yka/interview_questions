---
id: kotlin-188
title: "Migrating from RxJava to Kotlin Coroutines / Миграция сRxJava на Kotlin корутины"
aliases: [Coroutines Migration, Reactive Programming, RxJava Migration, RxJava to Coroutines]
topic: kotlin
subtopics: [coroutines, functions, reactive-programming]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-testing-flow-operators--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, kotlin, migration, reactive-programming, refactoring, rxjava]

date created: Friday, October 31st 2025, 6:30:29 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---
# Вопрос (RU)

> Как грамотно мигрировать с RxJava на Kotlin Coroutines/`Flow` в Android/Kotlin-проекте: какие соответствия типов (`Observable`/Single/Completable/Maybe/Flowable ↔ `Flow`/suspend/`StateFlow`/`SharedFlow`), как заменить операторы, настроить потоки выполнения, обработку ошибок и backpressure, обеспечить совместимость и поэтапную миграцию, а также каких подводных камней избегать?

# Question (EN)

> How do you correctly migrate from RxJava to Kotlin Coroutines/`Flow` in an Android/Kotlin project: what are the type mappings (`Observable`/Single/Completable/Maybe/Flowable ↔ `Flow`/suspend/`StateFlow`/`SharedFlow`), how to map operators, configure threading, error handling, and backpressure, ensure interoperability and phased migration, and which pitfalls to avoid?

## Ответ (RU)

Ниже приведено подробное руководство по миграции с RxJava на Kotlin Coroutines/`Flow`, включая сопоставление типов, операторов, потоков выполнения, обработку ошибок, стратегии backpressure, примеры репозиториев и `ViewModel`, тестирование, поэтапную стратегию миграции и список подводных камней.

## Answer (EN)

Below is a detailed guide for migrating from RxJava to Kotlin Coroutines/`Flow`, including type mappings, operator mapping, threading, error handling, backpressure strategies, complete repository/`ViewModel` examples, testing, gradual migration strategy, and pitfalls checklist.

---

# Миграция С RxJava На Kotlin Корутины

**Русский** | [English](#migrating-from-rxjava-to-kotlin-coroutines)

---

## Оглавление

- [Обзор](#обзор)
- [Почему мигрировать](#почему-мигрировать)
- [`Observable` → `Flow`](#observable--flow)
- [Single → suspend-функция](#single--suspend-функция)
- [Completable → suspend Unit](#completable--suspend-unit)
- [Maybe → nullable suspend](#maybe--nullable-suspend)
- [Flowable → `Flow`](#flowable--flow)
- [Горячие источники и Subjects](#горячие-источники-и-subjects)
- [Таблица операторов (RU)](#таблица-операторов-ru)
- [Комбинирующие операторы: combineLatest и zip](#комбинирующие-операторы-combinelatest-и-zip)
- [Subjects → `Flow` (подробно)](#subjects--flow-подробно)
- [Обработка ошибок](#обработка-ошибок)
- [Потоки выполнения](#потоки-выполнения)
- [Backpressure](#backpressure)
- [Полный пример миграции](#полный-пример-миграции)
- [Интероперабельность RxJava и корутин](#интероперабельность-rxjava-и-корутин)
- [Тестирование миграции](#тестирование-миграции)
- [Постепенная стратегия миграции](#постепенная-стратегия-миграции)
- [Распространенные ошибки](#распространенные-ошибки)
- [Лучшие практики](#лучшие-практики)
- [Чеклист миграции](#чеклист-миграции)
- [Дополнительные вопросы (RU)](#дополнительные-вопросы-ru)
- [Ссылки (RU)](#ссылки-ru)
- [Связанные вопросы (RU)](#связанные-вопросы-ru)

---

## Обзор

Это руководство охватывает миграцию с RxJava на Kotlin корутины, включая сопоставление типов, приблизительные эквиваленты операторов и лучшие практики для плавного перехода.

Цели миграции:
- Сохранить существующую функциональность
- Улучшить читаемость кода
- Сократить зависимости от библиотек
- Использовать преимущества Kotlin и [[c-coroutines]]
- Улучшить производительность

---

## Почему Мигрировать

### Преимущества Kotlin Корутин

```kotlin
// RxJava: сложный пайплайн
fun loadUser(userId: String): Single<User> {
    return api.getUser(userId)
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
        .timeout(30, TimeUnit.SECONDS)
        .retry(3)
        .doOnError { Log.e("Error", it.message ?: "Unknown") }
}

// Корутины: проще и читаемее
suspend fun loadUser(userId: String): User = withContext(Dispatchers.IO) {
    withTimeout(30_000) {
        retryIO(times = 3) {
            api.getUser(userId)
        }
    }
}
```

Ключевые преимущества:
- Более простой и знакомый синтаксис
- Естественная интеграция с Kotlin и Android API
- Меньше зависимостей и часто меньший размер APK
- Гибкое управление потоками и обработкой ошибок

---

## Observable → Flow

### Холодный `Observable` → `Flow`

```kotlin
// RxJava: холодный Observable
fun getUsers(): Observable<User> {
    return Observable.create { emitter ->
        val users = database.getUsers()
        users.forEach { user ->
            if (!emitter.isDisposed) {
                emitter.onNext(user)
            }
        }
        if (!emitter.isDisposed) {
            emitter.onComplete()
        }
    }
}

// Coroutines: Flow
fun getUsers(): Flow<User> = flow {
    val users = database.getUsers()
    users.forEach { user ->
        emit(user)
    }
}.flowOn(Dispatchers.IO)
```

### `Observable` С Операторами

```kotlin
// RxJava
fun searchUsers(queryChanges: Observable<String>): Observable<User> {
    return queryChanges
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
fun searchUsers(queryChanges: Flow<String>): Flow<User> =
    queryChanges
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { q ->
            flow {
                val users = api.searchUsers(q)
                users.forEach { emit(it) }
            }
        }
        .filter { it.isActive }
        .map { it.toUserModel() }
        .flowOn(Dispatchers.IO)
```

---

## Single → Suspend-функция

### Базовое Преобразование

```kotlin
// RxJava: Single
fun getUser(userId: String): Single<User> {
    return api.getUser(userId)
}

// Coroutines: suspend-функция
suspend fun getUser(userId: String): User = withContext(Dispatchers.IO) {
    api.getUser(userId)
}
```

### Single С Fallback-логикой

```kotlin
// RxJava: Single с обработкой ошибок
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

// Coroutines: suspend с явной fallback-логикой
suspend fun getUserOrEmptyOn404(userId: String): User = withContext(Dispatchers.IO) {
    try {
        api.getUser(userId)
    } catch (e: HttpException) {
        if (e.code() == 404) User.EMPTY else throw e
    }
}
```

### Single → `Deferred` (реже)

```kotlin
// Coroutines: Deferred
fun CoroutineScope.getUserDeferred(userId: String): Deferred<User> = async(Dispatchers.IO) {
    api.getUser(userId)
}
```

---

## Completable → Suspend Unit

### Базовое Преобразование

```kotlin
// RxJava: Completable
fun deleteUser(userId: String): Completable {
    return api.deleteUser(userId)
}

// Coroutines: suspend Unit
suspend fun deleteUser(userId: String) = withContext(Dispatchers.IO) {
    api.deleteUser(userId)
}
```

### Цепочки Completable

```kotlin
// RxJava: цепочка Completable
fun initializeApp(): Completable {
    return loadConfig()
        .andThen(initDatabase())
        .andThen(loadUser())
        .andThen(syncData())
}

// Coroutines: последовательные suspend-вызовы
suspend fun initializeApp() {
    loadConfig()
    initDatabase()
    loadUser()
    syncData()
}
```

---

## Maybe → Nullable Suspend

### Базовое Преобразование

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

// Coroutines: nullable suspend
suspend fun findUser(query: String): User? = withContext(Dispatchers.IO) {
    database.findUser(query)
}
```

### Maybe С defaultIfEmpty

```kotlin
// RxJava
fun getConfig(): Maybe<Config> {
    return api.getConfig()
        .defaultIfEmpty(Config.DEFAULT)
}

// Coroutines
suspend fun getConfig(): Config = withContext(Dispatchers.IO) {
    api.getConfig() ?: Config.DEFAULT
}
```

---

## Flowable → Flow

### Базовый Flowable

```kotlin
// RxJava: Flowable с BackpressureStrategy.BUFFER
fun observeMessages(): Flowable<Message> {
    return Flowable.create({ emitter ->
        val listener = object : MessageListener {
            override fun onMessage(message: Message) {
                if (!emitter.isCancelled) {
                    emitter.onNext(message)
                }
            }
        }
        messageSource.addListener(listener)
        emitter.setCancellable {
            messageSource.removeListener(listener)
        }
    }, BackpressureStrategy.BUFFER)
}

// Coroutines: callbackFlow
fun observeMessages(): Flow<Message> = callbackFlow {
    val listener = object : MessageListener {
        override fun onMessage(message: Message) {
            trySend(message).isSuccess
        }
    }
    messageSource.addListener(listener)
    awaitClose {
        messageSource.removeListener(listener)
    }
}
```

### Flowable С Backpressure

```kotlin
// RxJava
fun produceData(): Flowable<Data> {
    return Flowable.interval(100, TimeUnit.MILLISECONDS)
        .map { Data(it) }
        .onBackpressureBuffer(100)
}

// Coroutines
fun produceData(): Flow<Data> = flow {
    var count = 0L
    while (currentCoroutineContext().isActive) {
        delay(100)
        emit(Data(count++))
    }
}.buffer(100)

fun produceDataConflated(): Flow<Data> = flow {
    var count = 0L
    while (currentCoroutineContext().isActive) {
        delay(100)
        emit(Data(count++))
    }
}.conflate()
```

---

## Горячие Источники И Subjects

### `PublishSubject` → `SharedFlow`

```kotlin
// RxJava: PublishSubject
class EventBusRx {
    private val subject = PublishSubject.create<Event>()

    fun publish(event: Event) {
        subject.onNext(event)
    }

    fun observe(): Observable<Event> = subject
}

// Coroutines: SharedFlow
class EventBus {
    private val _events = MutableSharedFlow<Event>(replay = 0)
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun publish(event: Event) {
        _events.emit(event)
    }

    fun tryPublish(event: Event): Boolean = _events.tryEmit(event)
}
```

### `BehaviorSubject` → `StateFlow`

```kotlin
class UserStoreRx {
    private val subject = BehaviorSubject.createDefault(User.EMPTY)

    fun updateUser(user: User) {
        subject.onNext(user)
    }

    fun observeUser(): Observable<User> = subject
}

class UserStore {
    private val _user = MutableStateFlow(User.EMPTY)
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateUser(user: User) {
        _user.value = user
    }
}
```

### `ReplaySubject` → `SharedFlow` С `replay`

```kotlin
class MessageStoreRx {
    private val subject = ReplaySubject.createWithSize<Message>(10)

    fun addMessage(message: Message) {
        subject.onNext(message)
    }

    fun observeMessages(): Observable<Message> = subject
}

class MessageStore {
    private val _messages = MutableSharedFlow<Message>(
        replay = 10,
        extraBufferCapacity = 0,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val messages: SharedFlow<Message> = _messages.asSharedFlow()

    suspend fun addMessage(message: Message) {
        _messages.emit(message)
    }

    fun tryAddMessage(message: Message): Boolean = _messages.tryEmit(message)
}
```

### `AsyncSubject` → Кастом Через `Channel`

```kotlin
class ResultStore {
    private val _resultChannel = Channel<Result>(capacity = Channel.CONFLATED)
    val result: Flow<Result> = _resultChannel.receiveAsFlow()

    suspend fun completeWith(result: Result) {
        _resultChannel.send(result)
        _resultChannel.close()
    }
}
```

---

## Таблица Операторов (RU)

Приблизительное соответствие операторов (аналогично английской таблице):

### Трансформации

| RxJava | `Flow` | Описание |
|--------|-------|----------|
| `map` | `map` | Преобразование элементов |
| `flatMap` | `flatMapConcat` | Отображение и последовательное разворачивание |
| `flatMap` (параллельно) | `flatMapMerge` | Конкурентное разворачивание |
| `switchMap` | `flatMapLatest` | Отмена предыдущего запроса |
| `concatMap` | `flatMapConcat` | Последовательная конкатенация |
| `scan` | `scan` | Накопление состояния |
| `buffer` | `buffer` | Буферизация элементов |

### Фильтрация

| RxJava | `Flow` | Описание |
|--------|-------|----------|
| `filter` | `filter` | Фильтр по предикату |
| `take` | `take` | Взять первые N элементов |
| `skip` | `drop` | Пропустить первые N элементов |
| `distinctUntilChanged` | `distinctUntilChanged` | Удалить подряд идущие дубликаты |
| `debounce` | `debounce` | Дебаунс значений |

### Комбинирование

| RxJava | `Flow` | Описание |
|--------|-------|----------|
| `zip` | `zip` | Комбинация по позициям |
| `combineLatest` | `combine` | Комбинация последних значений |
| `merge` | `merge` | Объединение нескольких источников |
| `startWith` | `onStart` | Добавить значение в начало |

### Обработка Ошибок

| RxJava | `Flow` / coroutines | Описание |
|--------|--------------------|----------|
| `onErrorReturn` | `catch { emit(default) }` | Значение по умолчанию |
| `onErrorResumeNext` | `catch { emitAll(fallback) }` | Переход на запасной поток |
| `retry` | `retry` | Повтор при ошибке |

### Потоки Выполнения

| RxJava | Coroutines | Описание |
|--------|-----------|----------|
| `subscribeOn` | `flowOn` | Контекст upstream |
| `observeOn` | контекст коллектора | Контекст downstream задается местом `collect` |

---

## Комбинирующие Операторы: combineLatest И Zip

### `combineLatest` → `combine`

```kotlin
// RxJava
fun observeDashboard(): Observable<DashboardData> {
    return Observable.combineLatest(
        userObservable,
        notificationsObservable,
        settingsObservable
    ) { user, notifications, settings ->
        DashboardData(user, notifications, settings)
    }
}

// Coroutines
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

### `zip`

```kotlin
// RxJava
fun loadUserWithPosts(userId: String): Single<Pair<User, List<Post>>> {
    return Single.zip(
        api.getUser(userId),
        api.getUserPosts(userId)
    ) { user, posts ->
        user to posts
    }
}

// Coroutines
suspend fun loadUserWithPosts(userId: String): Pair<User, List<Post>> = coroutineScope {
    val userDeferred = async { api.getUser(userId) }
    val postsDeferred = async { api.getUserPosts(userId) }
    userDeferred.await() to postsDeferred.await()
}
```

---

## Subjects → Flow (подробно)

```kotlin
class DataStoreRx {
    val publishSubject = PublishSubject.create<Event>()
    val behaviorSubject = BehaviorSubject.createDefault(State.INITIAL)
    val replaySubject = ReplaySubject.createWithSize<Message>(10)
    val asyncSubject = AsyncSubject.create<Result>()
}

class DataStore {
    private val _events = MutableSharedFlow<Event>(replay = 0)
    val events: SharedFlow<Event> = _events.asSharedFlow()

    private val _state = MutableStateFlow(State.INITIAL)
    val state: StateFlow<State> = _state.asStateFlow()

    private val _messages = MutableSharedFlow<Message>(
        replay = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val messages: SharedFlow<Message> = _messages.asSharedFlow()

    private val _resultChannel = Channel<Result>(capacity = Channel.CONFLATED)
    val result: Flow<Result> = _resultChannel.receiveAsFlow()

    suspend fun completeWith(result: Result) {
        _resultChannel.send(result)
        _resultChannel.close()
    }
}
```

---

## Обработка Ошибок

```kotlin
// RxJava
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
}

// Flow + catch
fun loadUserFlow(userId: String): Flow<User> {
    return flow {
        emit(api.getUser(userId))
    }.catch { error ->
        when (error) {
            is IOException -> {
                val cached = cache.getUser(userId)
                emit(cached ?: User.EMPTY)
            }
            else -> throw error
        }
    }
}
```

---

## Потоки Выполнения

### Schedulers → Dispatchers

```kotlin
// RxJava
fun loadUser(userId: String): Single<User> {
    return api.getUser(userId)
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
}

// Coroutines
suspend fun loadUser(userId: String): User {
    return withContext(Dispatchers.IO) {
        api.getUser(userId)
    }
}

fun observeUser(userId: String): Flow<User> {
    return flow {
        emit(api.getUser(userId))
    }.flowOn(Dispatchers.IO)
}
```

Таблица соответствий Schedulers ↔ Dispatchers аналогична EN-секции.

---

## Backpressure

```kotlin
// RxJava: onBackpressureBuffer / Drop / Latest

// Coroutines: buffer / conflate / SharedFlow
fun produceBuffered(): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        delay(10)
        emit(Data())
    }
}.buffer(100)

fun produceConflated(): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        delay(10)
        emit(Data())
    }
}.conflate()
```

---

## Полный Пример Миграции

### Репозиторий (до)

```kotlin
class UserRepositoryRx(
    private val api: UserApi,
    private val database: UserDatabase
) {
    private val userSubject = BehaviorSubject.create<User>()

    fun observeUser(): Observable<User> = userSubject.hide()

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
}
```

### Репозиторий (после)

```kotlin
class UserRepository(
    private val api: UserApi,
    private val database: UserDatabase
) {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    suspend fun loadUser(userId: String): User = withContext(Dispatchers.IO) {
        try {
            val user = api.getUser(userId)
            database.saveUser(user)
            _user.value = user
            user
        } catch (e: Throwable) {
            val cached = database.getUser(userId)
            if (cached != null) {
                _user.value = cached
                cached
            } else {
                throw e
            }
        }
    }
}
```

### ViewModel (до)

```kotlin
class UserViewModelRx(
    private val repository: UserRepositoryRx
) : ViewModel() {

    private val compositeDisposable = CompositeDisposable()
    private val userLiveData = MutableLiveData<User>()

    fun observeUser(): LiveData<User> = userLiveData

    fun loadUser(userId: String) {
        repository.loadUser(userId)
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe({ user -> userLiveData.value = user }, {})
            .addTo(compositeDisposable)
    }

    override fun onCleared() {
        compositeDisposable.clear()
    }
}
```

### ViewModel (после)

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    val user: StateFlow<User?> = repository.user
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = null
        )

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                repository.loadUser(userId)
                _uiState.value = UiState.Success
            } catch (e: Throwable) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

---

## Интероперабельность RxJava И Корутин

### RxJava → Coroutines

```kotlin
// implementation("org.jetbrains.kotlinx:kotlinx-coroutines-rx3:<version>")

import io.reactivex.rxjava3.core.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.rx3.await
import kotlinx.coroutines.rx3.asFlow

suspend fun loadUserFromRx(legacyApi: LegacyApi): User {
    val rxSingle: Single<User> = legacyApi.getUser("123")
    return rxSingle.await()
}

fun observeUsersFromRx(legacyApi: LegacyApi): Flow<User> {
    val rxObservable: Observable<User> = legacyApi.observeUsers()
    return rxObservable.asFlow()
}
```

### Coroutines → RxJava

```kotlin
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.rx3.rxSingle
import kotlinx.coroutines.rx3.rxObservable

fun loadUserAsRx(userId: String, repository: UserRepository): Single<User> = rxSingle {
    repository.loadUser(userId)
}

fun observeUsersAsRx(repository: UserRepository): Observable<User> = rxObservable {
    repository.user.collect { user ->
        if (user != null) send(user)
    }
}
```

### Гибридный Адаптер

```kotlin
class HybridRepository(
    private val api: UserApi
) {
    suspend fun loadUserSuspend(userId: String): User = withContext(Dispatchers.IO) {
        api.getUser(userId)
    }

    fun loadUserRx(userId: String): Single<User> = rxSingle {
        loadUserSuspend(userId)
    }
}
```

---

## Тестирование Миграции

### Тесты RxJava

```kotlin
class UserRepositoryRxTest {
    // Используем TestScheduler, TestObserver для проверки Rx-поведения
}
```

### Тесты Корутин (suspend)

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserRepositoryTest {
    private val testDispatcher = UnconfinedTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @Test
    fun `loadUser returns user on success`() = runTest {
        val userId = "123"
        val expectedUser = User(userId, "John")

        val user = repository.loadUser(userId)

        assertEquals(expectedUser, user)
    }
}
```

### Тестирование `Flow`

```kotlin
import app.cash.turbine.test

@Test
fun `observeUsers emits user list`() = runTest {
    val expectedUsers = listOf(User("1", "John"), User("2", "Jane"))

    repository.observeUsers().test {
        assertEquals(expectedUsers, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

---

## Постепенная Стратегия Миграции

### Этап 1: Новые Фичи На Корутинах

```kotlin
class NewFeatureRepository(private val api: NewApi) {
    suspend fun loadNewData(): Data = withContext(Dispatchers.IO) {
        api.getData()
    }
}
```

### Этап 2: Обертки Вокруг RxJava

```kotlin
class MigrationRepository(private val legacyApi: LegacyApi) {
    suspend fun loadData(): Data {
        return legacyApi.getData()
            .subscribeOn(Schedulers.io())
            .await()
    }
}
```

### Этап 3: Миграция Ядра + Адаптеры

```kotlin
class UserRepositoryMigrated(private val api: UserApi) {
    suspend fun loadUser(userId: String): User = withContext(Dispatchers.IO) {
        api.getUser(userId)
    }

    fun loadUserRx(userId: String): Single<User> = rxSingle {
        loadUser(userId)
    }
}
```

### Этап 4: Полный Отказ От RxJava

Удаляем зависимости RxJava и адаптеры после переноса всех вызовов.

---

## Распространенные Ошибки

1. Отсутствие `flowOn` для тяжелых операций — весь `Flow` выполняется в контексте коллектора.
2. Использование `runBlocking` в продакшене — блокирует поток.
3. Проглатывание `CancellationException` в широком `catch (e: Exception)` — нужно пробрасывать отмену.
4. Использование `GlobalScope` вместо структурированных скоупов (`viewModelScope`, `lifecycleScope`).
5. Путаница между холодными (`Flow`) и горячими (`SharedFlow`/`StateFlow`) потоками.

---

## Лучшие Практики

1. Начинать миграцию с новых фич.
2. Использовать interop (`await`, `asFlow`, `rxSingle`) для плавного перехода.
3. Параллельно мигрировать тесты на coroutines-тулы.
4. Применять `StateFlow` для состояния и `SharedFlow` для событий.
5. Документировать статус миграции по модулям.

---

## Чеклист Миграции

### До Миграции

- [ ] Найти все места использования RxJava
- [ ] Выделить приоритетные области миграции
- [ ] Добавить зависимости coroutines и interop
- [ ] Настроить infra для тестирования корутин

### Во Время Миграции

- [ ] Перевести `Single` на suspend-функции
- [ ] Перевести `Observable` на `Flow`
- [ ] Перевести `Completable` на suspend `Unit`
- [ ] Заменить `Subject` на `StateFlow`/`SharedFlow`
- [ ] Заменить `Schedulers` на `Dispatchers`
- [ ] Обновить обработку ошибок (на `catch` и try-catch)
- [ ] Актуализировать тесты

### После Миграции

- [ ] Удалить зависимости RxJava
- [ ] Убрать временные адаптеры
- [ ] Обновить документацию
- [ ] Проверить размер APK и perf

---

## Дополнительные Вопросы (RU)

1. В чем основное преимущество миграции с RxJava на корутины с точки зрения долгосрочного сопровождения и снижения когнитивной сложности кода?
2. Как безопасно поддерживать период, когда в проекте одновременно используются RxJava и корутины, и какие паттерны interop для этого предпочтительнее?
3. Какой эквивалент `BehaviorSubject` в экосистеме корутин и в каких сценариях выбирать `StateFlow`, а в каких — `SharedFlow`?
4. Как правильно мигрировать `Observable.combineLatest` и `zip` на `Flow`, учитывая различия в семантике и инициализации значений?
5. Чем конкретно отличаются `subscribeOn`/`observeOn` от `flowOn` и контекста коллектора при работе с `Flow` в сложных пайплайнах?

---

## Ссылки (RU)

- https://kotlinlang.org/docs/coroutines-guide.html
- https://kotlinlang.org/docs/flow.html
- https://developer.android.com/kotlin/coroutines/coroutines-best-practices#rxjava
- https://github.com/Kotlin/kotlinx.coroutines/tree/master/reactive

---

## Связанные Вопросы (RU)

- [[q-flow-operators--kotlin--medium]]

---

# Migrating from RxJava to Kotlin Coroutines

**English** | [Русский](#миграция-с-rxjava-на-kotlin-корутины)

---

## Table of Contents

- [Overview](#overview)
- [Why Migrate](#why-migrate)
- [`Observable` to `Flow`](#observable-to-flow)
- [Single to Suspend Function](#single-to-suspend-function)
- [Completable to Suspend Unit](#completable-to-suspend-unit)
- [Maybe to Nullable Suspend Function](#maybe-to-nullable-suspend-function)
- [Flowable to `Flow`](#flowable-to-flow)
- [Hot `Observables` to `SharedFlow`/`StateFlow`](#hot-observables-to-sharedflowstateflow)
- [Operator Mapping Table](#operator-mapping-table)
- [combineLatest and zip](#combinelatest-and-zip-1)
- [Subjects to `Flow`](#subjects-to-flow)
- [Error Handling Migration](#error-handling-migration)
- [Threading Migration](#threading-migration)
- [Backpressure Strategies](#backpressure-strategies)
- [Complete Migration Example](#complete-migration-example)
- [Interoperability](#interoperability-1)
- [Testing Migration](#testing-migration-1)
- [Gradual Migration Strategy](#gradual-migration-strategy-1)
- [Common Pitfalls](#common-pitfalls-1)
- [Best Practices](#best-practices-1)
- [Migration Checklist](#migration-checklist-1)
- [Follow-ups](#follow-ups)
- [References](#references)
- [Related Questions](#related-questions)

---

## Overview

This guide covers the migration from RxJava to Kotlin Coroutines, including type mappings, operator equivalences (where appropriate), and best practices for a smooth transition.

Migration Goals:
- Maintain existing functionality
- Improve code readability
- Reduce library dependencies
- Leverage Kotlin-first features
- Improve performance

Also see: [[c-kotlin]], [[c-coroutines]].

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
        .doOnError { Log.e("Error", it.message ?: "Unknown") }
}

// Coroutines: Simple, readable, lightweight
suspend fun loadUser(userId: String): User = withContext(Dispatchers.IO) {
    withTimeout(30_000) {
        retryIO(times = 3) { // assume retryIO is defined elsewhere
            api.getUser(userId)
        }
    }
}
```

Key advantages:
- Simpler, more readable syntax
- First-class Kotlin/Android integration
- Fewer dependencies and often smaller APK size
- Flexible threading and error handling

---

## Observable to Flow

### Cold `Observable` → `Flow`

```kotlin
// RxJava: Cold Observable
fun getUsers(): Observable<User> {
    return Observable.create { emitter ->
        val users = database.getUsers()
        users.forEach { user ->
            if (!emitter.isDisposed) {
                emitter.onNext(user)
            }
        }
        if (!emitter.isDisposed) {
            emitter.onComplete()
        }
    }
}

// Coroutines: Flow
fun getUsers(): Flow<User> = flow {
    val users = database.getUsers()
    users.forEach { user ->
        emit(user)
    }
}.flowOn(Dispatchers.IO)
```

### `Observable` With Operators

```kotlin
// RxJava
fun searchUsers(queryChanges: Observable<String>): Observable<User> {
    return queryChanges
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
fun searchUsers(queryChanges: Flow<String>): Flow<User> =
    queryChanges
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { q ->
            flow {
                val users = api.searchUsers(q)
                users.forEach { emit(it) }
            }
        }
        .filter { it.isActive }
        .map { it.toUserModel() }
        .flowOn(Dispatchers.IO)
```

---

## Single to Suspend Function

### Basic Conversion

```kotlin
// RxJava: Single
fun getUser(userId: String): Single<User> {
    return api.getUser(userId)
}

// Coroutines: suspend function
suspend fun getUser(userId: String): User = withContext(Dispatchers.IO) {
    api.getUser(userId)
}
```

### Single with Fallback Logic

```kotlin
// RxJava
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

// Coroutines
suspend fun getUserOrEmptyOn404(userId: String): User = withContext(Dispatchers.IO) {
    try {
        api.getUser(userId)
    } catch (e: HttpException) {
        if (e.code() == 404) User.EMPTY else throw e
    }
}
```

### Single to `Deferred`

```kotlin
fun CoroutineScope.getUserDeferred(userId: String): Deferred<User> = async(Dispatchers.IO) {
    api.getUser(userId)
}
```

---

## Completable to Suspend Unit

```kotlin
// RxJava
fun deleteUser(userId: String): Completable {
    return api.deleteUser(userId)
}

// Coroutines
suspend fun deleteUser(userId: String) = withContext(Dispatchers.IO) {
    api.deleteUser(userId)
}
```

---

## Maybe to Nullable Suspend Function

```kotlin
// RxJava
fun findUser(query: String): Maybe<User> {
    return Maybe.create { emitter ->
        val user = database.findUser(query)
        if (user != null) emitter.onSuccess(user) else emitter.onComplete()
    }
}

// Coroutines
suspend fun findUser(query: String): User? = withContext(Dispatchers.IO) {
    database.findUser(query)
}
```

---

## Flowable to Flow

```kotlin
// RxJava
fun observeMessages(): Flowable<Message> {
    return Flowable.create({ emitter ->
        val listener = object : MessageListener {
            override fun onMessage(message: Message) {
                if (!emitter.isCancelled) emitter.onNext(message)
            }
        }
        messageSource.addListener(listener)
        emitter.setCancellable { messageSource.removeListener(listener) }
    }, BackpressureStrategy.BUFFER)
}

// Coroutines
fun observeMessages(): Flow<Message> = callbackFlow {
    val listener = object : MessageListener {
        override fun onMessage(message: Message) {
            trySend(message).isSuccess
        }
    }
    messageSource.addListener(listener)
    awaitClose { messageSource.removeListener(listener) }
}
```

---

## Hot Observables to `SharedFlow`/`StateFlow`

### `PublishSubject` → `SharedFlow`

```kotlin
class EventBusRx {
    private val subject = PublishSubject.create<Event>()

    fun publish(event: Event) {
        subject.onNext(event)
    }

    fun observe(): Observable<Event> = subject
}

class EventBus {
    private val _events = MutableSharedFlow<Event>(replay = 0)
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun publish(event: Event) {
        _events.emit(event)
    }

    fun tryPublish(event: Event): Boolean = _events.tryEmit(event)
}
```

### `BehaviorSubject` → `StateFlow`

```kotlin
class UserStoreRx {
    private val subject = BehaviorSubject.createDefault(User.EMPTY)

    fun updateUser(user: User) {
        subject.onNext(user)
    }

    fun observeUser(): Observable<User> = subject
}

class UserStore {
    private val _user = MutableStateFlow(User.EMPTY)
    val user: StateFlow<User> = _user.asStateFlow()

    fun updateUser(user: User) {
        _user.value = user
    }
}
```

### `ReplaySubject` → `SharedFlow` With `replay`

```kotlin
class MessageStoreRx {
    private val subject = ReplaySubject.createWithSize<Message>(10)

    fun addMessage(message: Message) {
        subject.onNext(message)
    }

    fun observeMessages(): Observable<Message> = subject
}

class MessageStore {
    private val _messages = MutableSharedFlow<Message>(
        replay = 10,
        extraBufferCapacity = 0,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val messages: SharedFlow<Message> = _messages.asSharedFlow()

    suspend fun addMessage(message: Message) {
        _messages.emit(message)
    }

    fun tryAddMessage(message: Message): Boolean = _messages.tryEmit(message)
}
```

### `AsyncSubject` → Via `Channel`

```kotlin
class ResultStore {
    private val _resultChannel = Channel<Result>(capacity = Channel.CONFLATED)
    val result: Flow<Result> = _resultChannel.receiveAsFlow()

    suspend fun completeWith(result: Result) {
        _resultChannel.send(result)
        _resultChannel.close()
    }
}
```

---

## Operator Mapping Table

Approximate mapping of common operators from RxJava to `Flow`/coroutines:

### Transformations

| RxJava | `Flow` | Description |
|--------|-------|-------------|
| `map` | `map` | Transform each item |
| `flatMap` | `flatMapConcat` | `Map` + sequentially flatten |
| `flatMap` (parallel) | `flatMapMerge` | Concurrent flattening |
| `switchMap` | `flatMapLatest` | Cancel previous on new emission |
| `concatMap` | `flatMapConcat` | Sequential concatenation |
| `scan` | `scan` | Accumulate state |
| `buffer` | `buffer` | Buffer emissions |

### Filtering

| RxJava | `Flow` | Description |
|--------|-------|-------------|
| `filter` | `filter` | Predicate filter |
| `take` | `take` | Take first N items |
| `skip` | `drop` | Drop first N items |
| `distinctUntilChanged` | `distinctUntilChanged` | Remove consecutive duplicates |
| `debounce` | `debounce` | Debounce values |

### Combining

| RxJava | `Flow` | Description |
|--------|-------|-------------|
| `zip` | `zip` | Pair by index |
| `combineLatest` | `combine` | Combine latest values |
| `merge` | `merge` | Merge multiple sources |
| `startWith` | `onStart` | Emit value before others |

### Error Handling

| RxJava | `Flow` / coroutines | Description |
|--------|--------------------|-------------|
| `onErrorReturn` | `catch { emit(default) }` | Default on error |
| `onErrorResumeNext` | `catch { emitAll(fallback) }` | Fallback stream |
| `retry` | `retry` | Retry on error |

### Threading

| RxJava | Coroutines | Description |
|--------|-----------|-------------|
| `subscribeOn` | `flowOn` | Upstream context |
| `observeOn` | Collector context | Downstream context set by `collect` site |

---

## combineLatest and Zip

### `combineLatest` → `combine`

```kotlin
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

### `zip` Via Structured Concurrency

```kotlin
suspend fun loadUserWithPosts(userId: String): Pair<User, List<Post>> = coroutineScope {
    val userDeferred = async { api.getUser(userId) }
    val postsDeferred = async { api.getUserPosts(userId) }
    userDeferred.await() to postsDeferred.await()
}
```

---

## Subjects to Flow

```kotlin
class DataStoreRx {
    val publishSubject = PublishSubject.create<Event>()
    val behaviorSubject = BehaviorSubject.createDefault(State.INITIAL)
    val replaySubject = ReplaySubject.createWithSize<Message>(10)
    val asyncSubject = AsyncSubject.create<Result>()
}

class DataStore {
    private val _events = MutableSharedFlow<Event>(replay = 0)
    val events: SharedFlow<Event> = _events.asSharedFlow()

    private val _state = MutableStateFlow(State.INITIAL)
    val state: StateFlow<State> = _state.asStateFlow()

    private val _messages = MutableSharedFlow<Message>(
        replay = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val messages: SharedFlow<Message> = _messages.asSharedFlow()

    private val _resultChannel = Channel<Result>(capacity = Channel.CONFLATED)
    val result: Flow<Result> = _resultChannel.receiveAsFlow()

    suspend fun completeWith(result: Result) {
        _resultChannel.send(result)
        _resultChannel.close()
    }
}
```

---

## Error Handling Migration

```kotlin
// RxJava
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
}

// Flow + catch
fun loadUserFlow(userId: String): Flow<User> {
    return flow {
        emit(api.getUser(userId))
    }.catch { error ->
        when (error) {
            is IOException -> {
                val cached = cache.getUser(userId)
                emit(cached ?: User.EMPTY)
            }
            else -> throw error
        }
    }
}
```

---

## Threading Migration

```kotlin
// RxJava
fun loadUser(userId: String): Single<User> {
    return api.getUser(userId)
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
}

// Coroutines
suspend fun loadUser(userId: String): User {
    return withContext(Dispatchers.IO) {
        api.getUser(userId)
    }
}

fun observeUser(userId: String): Flow<User> {
    return flow {
        emit(api.getUser(userId))
    }.flowOn(Dispatchers.IO)
}
```

Key ideas:
- Use `Dispatchers.IO` for I/O work, `Dispatchers.Main` for UI.
- `flowOn` controls upstream, collector context controls downstream.

---

## Backpressure Strategies

```kotlin
// RxJava: uses explicit backpressure strategies on Flowable

// Coroutines:
fun bufferedFlow(): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        delay(10)
        emit(Data())
    }
}.buffer(100)

fun conflatedFlow(): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        delay(10)
        emit(Data())
    }
}.conflate()

// Use `SharedFlow` / `Channel` for fine-grained control when needed
```

---

## Complete Migration Example

```kotlin
class UserRepositoryRx(
    private val api: UserApi,
    private val database: UserDatabase
) {
    private val userSubject = BehaviorSubject.create<User>()

    fun observeUser(): Observable<User> = userSubject.hide()

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
}

class UserRepository(
    private val api: UserApi,
    private val database: UserDatabase
) {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    suspend fun loadUser(userId: String): User = withContext(Dispatchers.IO) {
        try {
            val user = api.getUser(userId)
            database.saveUser(user)
            _user.value = user
            user
        } catch (e: Throwable) {
            val cached = database.getUser(userId)
            if (cached != null) {
                _user.value = cached
                cached
            } else {
                throw e
            }
        }
    }
}
```

```kotlin
class UserViewModelRx(
    private val repository: UserRepositoryRx
) : ViewModel() {

    private val compositeDisposable = CompositeDisposable()
    private val userLiveData = MutableLiveData<User>()

    fun observeUser(): LiveData<User> = userLiveData

    fun loadUser(userId: String) {
        repository.loadUser(userId)
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe({ user -> userLiveData.value = user }, {})
            .addTo(compositeDisposable)
    }

    override fun onCleared() {
        compositeDisposable.clear()
    }
}

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    val user: StateFlow<User?> = repository.user
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = null
        )

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                repository.loadUser(userId)
                _uiState.value = UiState.Success
            } catch (e: Throwable) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

---

## Interoperability

### RxJava → Coroutines

```kotlin
// implementation("org.jetbrains.kotlinx:kotlinx-coroutines-rx3:<version>")

import io.reactivex.rxjava3.core.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.rx3.await
import kotlinx.coroutines.rx3.asFlow

suspend fun loadUserFromRx(legacyApi: LegacyApi): User {
    val rxSingle: Single<User> = legacyApi.getUser("123")
    return rxSingle.await()
}

fun observeUsersFromRx(legacyApi: LegacyApi): Flow<User> {
    val rxObservable: Observable<User> = legacyApi.observeUsers()
    return rxObservable.asFlow()
}
```

### Coroutines → RxJava

```kotlin
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.rx3.rxSingle
import kotlinx.coroutines.rx3.rxObservable

fun loadUserAsRx(userId: String, repository: UserRepository): Single<User> = rxSingle {
    repository.loadUser(userId)
}

fun observeUsersAsRx(repository: UserRepository): Observable<User> = rxObservable {
    repository.user.collect { user ->
        if (user != null) send(user)
    }
}
```

### Hybrid Adapter

```kotlin
class HybridRepository(
    private val api: UserApi
) {
    suspend fun loadUserSuspend(userId: String): User = withContext(Dispatchers.IO) {
        api.getUser(userId)
    }

    fun loadUserRx(userId: String): Single<User> = rxSingle {
        loadUserSuspend(userId)
    }
}
```

---

## Testing Migration

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserRepositoryTest {
    private val testDispatcher = UnconfinedTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @Test
    fun `loadUser returns user on success`() = runTest {
        val userId = "123"
        val expectedUser = User(userId, "John")

        val user = repository.loadUser(userId)

        assertEquals(expectedUser, user)
    }
}
```

```kotlin
import app.cash.turbine.test

@Test
fun `observeUsers emits user list`() = runTest {
    val expectedUsers = listOf(User("1", "John"), User("2", "Jane"))

    repository.observeUsers().test {
        assertEquals(expectedUsers, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

---

## Gradual Migration Strategy

```kotlin
class NewFeatureRepository(private val api: NewApi) {
    suspend fun loadNewData(): Data = withContext(Dispatchers.IO) {
        api.getData()
    }
}
```

```kotlin
class MigrationRepository(private val legacyApi: LegacyApi) {
    suspend fun loadData(): Data {
        return legacyApi.getData()
            .subscribeOn(Schedulers.io())
            .await()
    }
}
```

```kotlin
class UserRepositoryMigrated(private val api: UserApi) {
    suspend fun loadUser(userId: String): User = withContext(Dispatchers.IO) {
        api.getUser(userId)
    }

    fun loadUserRx(userId: String): Single<User> = rxSingle {
        loadUser(userId)
    }
}
```

Key steps:
- New code uses coroutines.
- Wrap existing RxJava with coroutine interop.
- Gradually migrate core APIs.
- Remove RxJava once unused.

---

## Common Pitfalls

1. Missing `flowOn` for heavy upstream work.
2. Using `runBlocking` in production.
3. Swallowing `CancellationException` in broad `catch` blocks.
4. Using `GlobalScope` instead of structured scopes.
5. Confusing cold `Flow` with hot `SharedFlow`/`StateFlow`.

---

## Best Practices

1. Start migration in new features.
2. Use interop (`await`, `asFlow`, `rxSingle`) for gradual transition.
3. Migrate tests to coroutine test utilities.
4. Use `StateFlow` for state and `SharedFlow` for events.
5. Track migration status per module.

---

## Migration Checklist

### Before Migration

- [ ] Identify all RxJava usages.
- [ ] Prioritize areas to migrate.
- [ ] Add coroutine and interop dependencies.
- [ ] Set up coroutine testing infrastructure.

### During Migration

- [ ] Convert `Single` to suspend functions.
- [ ] Convert `Observable` to `Flow`.
- [ ] Convert `Completable` to suspend `Unit`.
- [ ] Replace `Subject` with `StateFlow`/`SharedFlow`.
- [ ] Replace `Schedulers` with `Dispatchers`.
- [ ] Update error handling to `try/catch` and `catch`.
- [ ] Update tests.

### After Migration

- [ ] Remove RxJava dependencies.
- [ ] Remove temporary adapters.
- [ ] Update documentation.
- [ ] Verify APK size and performance.

---

## Follow-ups

1. What is the main benefit of migrating from RxJava to Coroutines for long-term maintainability and reduced cognitive complexity?
2. How can you safely support a period where both RxJava and Coroutines coexist in the same codebase, and which interop patterns are recommended?
3. What is the correct `StateFlow`/`SharedFlow`-based replacement for `BehaviorSubject`, and in which scenarios would you choose each?
4. How should you migrate `Observable.combineLatest` and `zip` to `Flow` while accounting for initialization and semantic differences?
5. How do `subscribeOn`/`observeOn` differ from `flowOn` and the collector context when building complex `Flow` pipelines?

---

## References

- https://kotlinlang.org/docs/coroutines-guide.html
- https://kotlinlang.org/docs/flow.html
- https://developer.android.com/kotlin/coroutines/coroutines-best-practices#rxjava
- https://github.com/Kotlin/kotlinx.coroutines/tree/master/reactive

---

## Related Questions

- [[q-flow-operators--kotlin--medium]]
