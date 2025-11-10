---
id: kotlin-108
title: "Race conditions and data races in Kotlin coroutines / Состояния гонки и data race в Kotlin корутинах"
topic: kotlin
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
aliases: []
question_kind: coding
tags: [bugs, concurrency, coroutines, data-races, difficulty/hard, kotlin, race-conditions, thread-safety]
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-debugging-coroutines-techniques--kotlin--medium, q-mutex-synchronized-coroutines--kotlin--medium, q-semaphore-rate-limiting--kotlin--medium]
subtopics:
  - concurrency
  - coroutines
  - race-conditions
---
# Вопрос (RU)
> Что такое состояния гонки и data race в Kotlin корутинах? Как их обнаруживать и предотвращать?

---

# Question (EN)
> What are race conditions and data races in Kotlin coroutines? How do you detect and prevent them?

## Ответ (RU)

Корутины упрощают конкурентное программирование, но не устраняют состояния гонки. Когда несколько корутин обращаются к общему изменяемому состоянию (особенно из разных потоков), могут появляться тонкие баги. Важно различать состояния гонки и data race, знать техники их обнаружения и стратегии предотвращения, чтобы писать production-ready код с корутинами.

### Состояние гонки vs Data Race

- "Состояние гонки" — логическая ошибка, при которой поведение программы зависит от порядка/тайминга выполнения конкурентных операций.
- "Data race" — низкоуровневая ошибка памяти: два потока одновременно обращаются к одной ячейке памяти, по крайней мере один — с записью, и обращение не защищено корректной синхронизацией (нет гарантированного happens-before).

Ключевое различие:
- Data race — нарушение правил памяти / синхронизации.
- Состояние гонки — ошибка бизнес-логики, даже если отдельные операции формально синхронизированы.

```kotlin
// Пример data race (на JVM)
var counter = 0 // разделяемое изменяемое состояние

launch { repeat(1000) { counter++ } }
launch { repeat(1000) { counter++ } }

// Data race: обе корутины читают/пишут counter без синхронизации
// Итоговое значение непредсказуемо (< 2000)

// Пример логического состояния гонки
var balance = 100

launch {
    if (balance >= 50) { // check
        delay(10)
        balance -= 50   // act
    }
}

launch {
    if (balance >= 50) { // check
        delay(10)
        balance -= 50   // act
    }
}

// Оба проходят проверку, баланс становится 0, хотя второй перевод должен был не пройти.
// Даже при атомарных чтениях/записях логика остаётся "гоночной".
```

### Общий паттерн гонки: Check-Then-Act (RU)

Проблема: между проверкой и действием состояние может измениться другой корутиной.

```kotlin
class BankAccount {
    private var balance = 100

    // СОСТОЯНИЕ ГОНКИ
    suspend fun withdraw(amount: Int): Boolean {
        if (balance >= amount) { // Check
            delay(10)            // Имитируем обработку
            balance -= amount    // Act
            return true
        }
        return false
    }
}

val account = BankAccount()

launch { account.withdraw(60) } // Корутина 1
launch { account.withdraw(60) } // Корутина 2

// Обе проверки могут пройти при balance = 100
// Обе спишут по 60
// Итоговый баланс может стать -20 (некорректно)
```

Решение: сделать check+act атомарным с помощью `Mutex`.

```kotlin
class BankAccount {
    private val mutex = Mutex()
    private var balance = 100

    // КОРРЕКТНО (для данного примера)
    suspend fun withdraw(amount: Int): Boolean = mutex.withLock {
        if (balance >= amount) {
            delay(10)
            balance -= amount
            true
        } else {
            false
        }
    }
}
```

### Общий паттерн гонки: Read-Modify-Write (RU)

Проблема: инкремент счётчика без синхронизации.

```kotlin
var counter = 0

// СОСТОЯНИЕ ГОНКИ
repeat(1000) {
    launch {
        counter++ // Read-modify-write
    }
}

delay(1000)
println(counter) // Ожидаем: 1000, фактически: < 1000
```

Почему так? `counter++` состоит из:
1. Прочитать значение.
2. Прибавить 1.
3. Записать обратно.

Возможное чередование:

```
Корутина 1: Read(0)
Корутина 2: Read(0)
Корутина 1: Add(0+1)
Корутина 2: Add(0+1)
Корутина 1: Write(1)
Корутина 2: Write(1)  ← Потерянное обновление (должно быть 2)
```

Решения:

```kotlin
// Решение 1: Mutex
val mutex = Mutex()
var counter = 0

repeat(1000) {
    launch {
        mutex.withLock {
            counter++
        }
    }
}

// Решение 2: AtomicInteger (JVM; для простых счётчиков)
val atomicCounter = java.util.concurrent.atomic.AtomicInteger(0)

repeat(1000) {
    launch {
        atomicCounter.incrementAndGet()
    }
}

// Решение 3: Ограничение одним потоком
val singleThreadContext = newSingleThreadContext("Counter")
var confinedCounter = 0

repeat(1000) {
    launch(singleThreadContext) {
        confinedCounter++ // Безопасно: всегда один поток
    }
}
```

### Проблемы общего изменяемого состояния (RU)

Основной источник гонок — разделяемые изменяемые структуры данных.

```kotlin
// ОПАСНО (пример для JVM)
class UserCache(private val api: Api) {
    private val cache = mutableMapOf<String, User>()

    suspend fun getUser(id: String): User {
        return cache[id] ?: run {
            val user = api.fetchUser(id)
            cache[id] = user // Гонка: параллельные изменения без синхронизации
            user
        }
    }
}

val cache = UserCache(api)
launch { cache.getUser("1") }
launch { cache.getUser("2") }
launch { cache.getUser("3") }
```

Решение 1: Mutex + корректный double-check.

```kotlin
class UserCache(private val api: Api) {
    private val mutex = Mutex()
    private val cache = mutableMapOf<String, User>()

    suspend fun getUser(id: String): User {
        mutex.withLock {
            cache[id]
        }?.let { return it }

        val fetched = api.fetchUser(id)

        return mutex.withLock {
            cache.getOrPut(id) { fetched }
        }
    }
}
```

Решение 2: ConcurrentHashMap (JVM-специфично).

```kotlin
class UserCache(private val api: Api) {
    private val cache = java.util.concurrent.ConcurrentHashMap<String, User>()

    suspend fun getUser(id: String): User {
        val cached = cache[id]
        if (cached != null) return cached

        val user = api.fetchUser(id)
        return cache.putIfAbsent(id, user) ?: user
    }
}
```

Решение 3: Актор/однопоточный владелец состояния (через Channel + scope).

```kotlin
sealed class CacheMessage
class GetUser(
    val id: String,
    val response: CompletableDeferred<User>
) : CacheMessage()

class UserCache(private val api: Api, scope: CoroutineScope) {
    private val cache = mutableMapOf<String, User>()
    private val channel = Channel<CacheMessage>()

    init {
        scope.launch {
            for (msg in channel) {
                when (msg) {
                    is GetUser -> {
                        val user = cache[msg.id] ?: run {
                            val fetched = api.fetchUser(msg.id)
                            cache[msg.id] = fetched
                            fetched
                        }
                        msg.response.complete(user)
                    }
                }
            }
        }
    }

    suspend fun getUser(id: String): User {
        val response = CompletableDeferred<User>()
        channel.send(GetUser(id, response))
        return response.await()
    }
}
```

### Техники обнаружения (RU)

1. Стресс-тесты конкурентности: много корутин, много повторений, сравнение ожидаемого и фактического результата.
2. Логирование с таймстампами и анализ межпоточных interleavings.
3. Thread Sanitizer (в первую очередь Kotlin/Native; для JVM поддержка ограничена/экспериментальна).
4. Чек-листы код-ревью:
   - Есть ли разделяемые изменяемые переменные?
   - Доступ к ним из нескольких корутин/потоков?
   - Используются ли `Mutex`, атомики, ограниченный `Dispatcher` и т.п.?
   - Есть ли паттерны check-then-act или read-modify-write без синхронизации?

Пример стресс-теста:

```kotlin
@Test
fun `stress test for race conditions`() = runTest {
    val counter = java.util.concurrent.atomic.AtomicInteger(0)
    val iterations = 10_000
    val coroutines = 100

    repeat(coroutines) {
        launch {
            repeat(iterations) {
                counter.incrementAndGet()
            }
        }
    }

    val expected = coroutines * iterations
    val actual = counter.get()

    assertEquals(expected, actual, "Race condition detected or lost increments!")
}
```

### Стратегия предотвращения 1: Mutex (RU)

Используйте, когда нужно сделать несколько операций атомарным блоком.

```kotlin
class SessionManager {
    private val mutex = Mutex()
    private var userId: String? = null
    private var sessionToken: String? = null
    private var expiresAt: Long = 0

    suspend fun login(id: String, token: String, expiresIn: Long) {
        mutex.withLock {
            userId = id
            sessionToken = token
            expiresAt = System.currentTimeMillis() + expiresIn
        }
    }

    suspend fun getSession(): Triple<String?, String?, Long> = mutex.withLock {
        Triple(userId, sessionToken, expiresAt)
    }

    suspend fun isValid(): Boolean = mutex.withLock {
        userId != null && System.currentTimeMillis() < expiresAt
    }
}
```

### Стратегия предотвращения 2: Атомарные типы (RU)

Подходят для простых счётчиков, флагов, ссылок.

```kotlin
class RequestCounter {
    private val count = java.util.concurrent.atomic.AtomicInteger(0)
    private val lastRequest = java.util.concurrent.atomic.AtomicLong(0)

    fun recordRequest() {
        count.incrementAndGet()
        lastRequest.set(System.currentTimeMillis())
    }

    fun getStats(): Pair<Int, Long> = count.get() to lastRequest.get()
}

class ConfigManager {
    private val config = java.util.concurrent.atomic.AtomicReference<Config>(Config.default)

    fun updateConfig(new: Config) {
        config.set(new)
    }

    fun getConfig(): Config = config.get()
}
```

### Стратегия предотвращения 3: Ограниченный диспетчер / Конфайнмент контекста (RU)

Держите изменяемое состояние в одном потоке или под одним сериализующим диспетчером.

```kotlin
class DatabaseManager(private val database: Database) {
    private val dbDispatcher = newSingleThreadContext("Database")
    private val cache = mutableMapOf<String, Data>()

    suspend fun getData(id: String): Data = withContext(dbDispatcher) {
        cache[id] ?: run {
            val data = database.query(id)
            cache[id] = data
            data
        }
    }

    suspend fun updateData(id: String, data: Data) = withContext(dbDispatcher) {
        cache[id] = data
        database.update(id, data)
    }
}
```

```kotlin
// Пример конфайнмента через limitedParallelism
class Repository(private val fetcher: suspend () -> Data) {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO.limitedParallelism(1)
    )

    private var cache: Data? = null

    fun getData(): Deferred<Data> = scope.async {
        cache ?: run {
            val data = fetcher()
            cache = data
            data
        }
    }
}
```

### Стратегия предотвращения 4: `StateFlow` (атомарные обновления) (RU)

Подходит для наблюдаемого состояния с заменой значения целиком.

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _userState = MutableStateFlow<UserState>(UserState.Loading)
    val userState: StateFlow<UserState> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _userState.value = UserState.Loading
            try {
                val user = repository.getUser(userId)
                _userState.value = UserState.Success(user) // Атомарная замена значения
            } catch (e: Exception) {
                _userState.value = UserState.Error(e.message)
            }
        }
    }
}

sealed class UserState {
    object Loading : UserState()
    data class Success(val user: User) : UserState()
    data class Error(val message: String?) : UserState()
}
```

Почему это относительно безопасно:
- Каждая запись в `StateFlow.value` атомарна целиком.
- Для инвариантов между несколькими переменными всё равно нужна синхронизация.

### Отношения happens-before (Kotlin корутины + JVM) (RU)

Happens-before гарантирует, что эффекты одной операции видимы для другой.

В контексте корутин (с учётом JVM-модели памяти):

1. Запуск корутины (`launch`/`async`) задаёт порядок между местом запуска и началом выполнения в её контексте.
2. Завершение корутины happens-before успешным `join`/`await` другой корутины.
3. `send` в `Channel` happens-before соответствующего `receive` этого элемента.
4. Для `Mutex`: все записи до `unlock` видимы после следующего успешного `lock`.

```kotlin
var x = 0
val channel = Channel<Unit>()

// Корутина 1
launch {
    x = 42
    channel.send(Unit) // Запись x happens-before этого send
}

// Корутина 2
launch {
    channel.receive()  // После send
    println(x)         // Обязан увидеть 42
}
```

### Volatile и `@Volatile` в Kotlin (JVM) (RU)

`@Volatile` гарантирует видимость между потоками, но не атомарность и не взаимное исключение.

```kotlin
// ВСЁ ЕЩЁ ГОНОЧНО
@Volatile
var counter = 0

launch(Dispatchers.Default) { repeat(1000) { counter++ } }
launch(Dispatchers.Default) { repeat(1000) { counter++ } }

// counter++ остаётся неатомарной read-modify-write операцией.
```

Когда использовать `@Volatile`: для простых флагов/публикации, где каждая запись самодостаточна.

```kotlin
@Volatile
var isRunning = true

fun startWorker() = thread {
    while (isRunning) {
        // Работа
    }
}

// Из другого потока:
isRunning = false // Быстро становится видимым worker-потоку
```

Ключевое отличие:
- `@Volatile`: только видимость; не делает инкременты или сложные операции атомарными.
- Атомарные типы: видимость + атомарные операции read-modify-write.

### Тестирование на состояния гонки (RU)

Подход: интенсивный параллельный доступ + многократные прогоны.

```kotlin
@Test
fun `test no race condition in counter`() = runTest {
    val counter = SafeCounter() // Ваша реализация
    val iterations = 1000
    val coroutines = 100

    val jobs = List(coroutines) {
        launch {
            repeat(iterations) {
                counter.increment()
            }
        }
    }

    jobs.joinAll()

    val expected = coroutines * iterations
    val actual = counter.get()

    assertEquals(expected, actual)
}

@Test
fun `stress test 100 times`() {
    repeat(100) {
        `test no race condition in counter`()
    }
}
```

### Реальный пример: управление сессией (RU)

Проблема: конкурирующие login/logout приводят к неконсистентному состоянию.

```kotlin
// ГОНОЧНО
class SessionManager {
    private var currentUser: User? = null
    private var loginTime: Long = 0

    suspend fun login(user: User) {
        currentUser = user
        delay(10) // Имитируем получение токена
        loginTime = System.currentTimeMillis()
    }

    suspend fun logout() {
        currentUser = null
        loginTime = 0
    }

    fun isLoggedIn(): Boolean = currentUser != null
}

// Параллельные вызовы могут оставить currentUser установленным, а loginTime = 0 и т.п.
```

Решение: защищать инвариант целиком.

```kotlin
// БЕЗОПАСНО
class SafeSessionManager {
    private val mutex = Mutex()
    private var session: Session? = null

    suspend fun login(user: User) {
        val token = fetchToken(user)
        val newSession = Session(user, token, System.currentTimeMillis())
        mutex.withLock {
            session = newSession
        }
    }

    suspend fun logout() {
        mutex.withLock {
            session = null
        }
    }

    suspend fun getSession(): Session? = mutex.withLock { session }
}

data class Session(
    val user: User,
    val token: String,
    val loginTime: Long
)
```

### Реальный пример: обновление кеша (RU)

Проблема: потерянные обновления / дублирующаяся работа.

```kotlin
// ГОНОЧНО
class ImageCache(private val downloader: suspend (String) -> Bitmap) {
    private val cache = mutableMapOf<String, Bitmap>()

    suspend fun getImage(url: String): Bitmap {
        cache[url]?.let { return it }

        val bitmap = downloader(url)
        cache[url] = bitmap
        return bitmap
    }
}

// Параллельные запросы к одному URL могут запустить несколько скачиваний.
```

Безопасное решение: совместно использовать in-flight работу и обновлять кеш под блокировкой.

```kotlin
// БЕЗОПАСНО
class ImageCache(
    private val scope: CoroutineScope,
    private val downloader: suspend (String) -> Bitmap
) {
    private val mutex = Mutex()
    private val cache = mutableMapOf<String, Bitmap>()
    private val pending = mutableMapOf<String, Deferred<Bitmap>>()

    suspend fun getImage(url: String): Bitmap {
        mutex.withLock { cache[url] }?.let { return it }

        val deferred = mutex.withLock {
            pending[url] ?: scope.async(Dispatchers.IO) {
                downloader(url)
            }.also { pending[url] = it }
        }

        val bitmap = deferred.await()

        return mutex.withLock {
            cache.getOrPut(url) { bitmap }.also {
                pending.remove(url)
            }
        }
    }
}
```

### Примитивы `kotlinx.coroutines.sync` (RU)

Основные примитивы (JVM/Multiplatform):

1. `Mutex` — взаимное исключение для критических секций.
2. `Semaphore` — ограничение количества одновременных корутин.
3. `Channel` — обмен сообщениями / акторный стиль.
4. Атомарные типы — безлоковые операции (JVM: `java.util.concurrent.atomic`; платформенно-специфичные альтернативы в других средах).

```kotlin
import kotlinx.coroutines.sync.*

val mutex = Mutex()
mutex.withLock {
    // критическая секция
}

val semaphore = Semaphore(permits = 3)
semaphore.withPermit {
    // не более 3 одновременных выполнений
}

val channel = Channel<Int>()
launch { channel.send(42) }
launch { val value = channel.receive() }
```

### Лучшие практики конкурентного кода с корутинами (RU)

1. Минимизируйте общее изменяемое состояние, предпочитайте неизменяемые данные.
2. Используйте потокобезопасные коллекции там, где это уместно.
3. Синхронизируйте доступ (`Mutex`, атомики, конфайнмент, акторы).
4. Делайте составные операции атомарными (check-then-act внутри синхронизации).
5. Используйте `StateFlow`/`SharedFlow` для наблюдаемого состояния с атомарными заменами.
6. Документируйте гарантии потокобезопасности API.
7. Тестируйте конкурентность стресс-тестами.
8. Ищите в коде типичные паттерны гонок.
9. Используйте акторный стиль для сложных машин состояний.
10. Следите за производительностью синхронизации.

### Ключевые выводы (RU)

1. Корутины не устраняют состояния гонки автоматически.
2. Паттерн check-then-act опасен — делайте его атомарным (`Mutex`, акторы, конфайнмент).
3. Операции read-modify-write требуют синхронизации (атомики или `Mutex`).
4. Общие изменяемые данные — корень проблем, минимизируйте или защищайте их.
5. `Mutex` подходит для сложных атомарных последовательностей.
6. Атомарные типы — для простых счётчиков/флагов.
7. `StateFlow`/`SharedFlow` помогают с наблюдаемым состоянием и атомарными обновлениями.
8. Тестируйте конкурентность и используйте стресс-тесты.
9. `@Volatile` даёт только видимость, не атомарность.
10. Конфайнмент контекста (однопоточные диспетчеры) сериализует доступ и устраняет гонки по этому состоянию.

---

## Answer (EN)

Coroutines make concurrent programming easier, but they don't eliminate race conditions. When multiple coroutines access shared mutable state (especially from different threads), subtle bugs can appear. Understanding race conditions vs data races, detection techniques, and prevention strategies is critical for production-ready coroutine code.

### Race Condition Vs Data Race

- Race condition: A bug where program behavior depends on the timing/ordering of concurrent operations.
- Data race: Two threads access the same memory location concurrently, at least one is a write, and the access is not properly synchronized (no happens-before relation), violating the memory model.

Key difference:
- Data race = low-level memory access/synchronization problem.
- Race condition = high-level logic bug that can exist even when individual operations are synchronized.

```kotlin
// Data race example (JVM)
var counter = 0 // Shared mutable state

launch { repeat(1000) { counter++ } }
launch { repeat(1000) { counter++ } }

// Data race: Both coroutines read/write counter without proper synchronization
// Final value is unpredictable (< 2000)

// Race condition example
var balance = 100

launch {
    if (balance >= 50) { // Check
        delay(10)
        balance -= 50    // Act
    }
}

launch {
    if (balance >= 50) { // Check
        delay(10)
        balance -= 50    // Act
    }
}

// Both pass the check, balance becomes 0, even though the second withdrawal should fail.
// Even with atomic reads/writes, this pattern remains logically racy.
```

### Common Race Condition Pattern: Check-Then-Act

Problem: State may change between the check and the action.

```kotlin
class BankAccount {
    private var balance = 100

    // RACE CONDITION
    suspend fun withdraw(amount: Int): Boolean {
        if (balance >= amount) { // Check
            delay(10)           // Simulate processing
            balance -= amount   // Act
            return true
        }
        return false
    }
}

val account = BankAccount()

launch { account.withdraw(60) } // Coroutine 1
launch { account.withdraw(60) } // Coroutine 2

// Both checks may pass with balance = 100
// Both withdraw 60
// Final balance can become -20 (invalid)
```

Solution: use `Mutex` to make check+act atomic.

```kotlin
class BankAccount {
    private val mutex = Mutex()
    private var balance = 100

    // CORRECT (for this example)
    suspend fun withdraw(amount: Int): Boolean = mutex.withLock {
        if (balance >= amount) {
            delay(10)
            balance -= amount
            true
        } else {
            false
        }
    }
}
```

### Common Race Condition Pattern: Read-Modify-Write

Problem: Counter increment without synchronization.

```kotlin
var counter = 0

// RACE CONDITION
repeat(1000) {
    launch {
        counter++ // Read-modify-write
    }
}

delay(1000)
println(counter) // Expected: 1000, Actual: < 1000
```

Why? `counter++` is:
1. Read current value.
2. Add 1.
3. Write back.

Interleaving:

```
Coroutine 1: Read(0)
Coroutine 2: Read(0)
Coroutine 1: Add(0+1)
Coroutine 2: Add(0+1)
Coroutine 1: Write(1)
Coroutine 2: Write(1)  ← Lost update! Should be 2
```

Solutions:

```kotlin
// Solution 1: Mutex
val mutex = Mutex()
var counter = 0

repeat(1000) {
    launch {
        mutex.withLock {
            counter++
        }
    }
}

// Solution 2: AtomicInteger (on JVM; good for simple counters)
val atomicCounter = java.util.concurrent.atomic.AtomicInteger(0)

repeat(1000) {
    launch {
        atomicCounter.incrementAndGet()
    }
}

// Solution 3: Single-threaded confined dispatcher
val singleThreadContext = newSingleThreadContext("Counter")
var confinedCounter = 0

repeat(1000) {
    launch(singleThreadContext) {
        confinedCounter++ // Safe: always same thread
    }
}
```

### Shared Mutable State Problems

Problem: Multiple coroutines modifying shared state.

```kotlin
// DANGEROUS (JVM example)
class UserCache(private val api: Api) {
    private val cache = mutableMapOf<String, User>()

    suspend fun getUser(id: String): User {
        return cache[id] ?: run {
            val user = api.fetchUser(id)
            cache[id] = user // RACE: concurrent modifications not synchronized
            user
        }
    }
}

val cache = UserCache(api)
launch { cache.getUser("1") }
launch { cache.getUser("2") }
launch { cache.getUser("3") }
```

Corrected Solution 1: `Mutex` with proper double-checked logic.

```kotlin
class UserCache(private val api: Api) {
    private val mutex = Mutex()
    private val cache = mutableMapOf<String, User>()

    suspend fun getUser(id: String): User {
        // Fast path: read under lock to avoid races on the map
        mutex.withLock {
            cache[id]
        }?.let { return it }

        // Fetch outside the lock (expensive work)
        val fetched = api.fetchUser(id)

        // Publish result under lock with get-or-put to avoid duplicates
        return mutex.withLock {
            cache.getOrPut(id) { fetched }
        }
    }
}
```

Solution 2: `ConcurrentHashMap` (JVM-specific).

```kotlin
class UserCache(private val api: Api) {
    private val cache = java.util.concurrent.ConcurrentHashMap<String, User>()

    suspend fun getUser(id: String): User {
        val cached = cache[id]
        if (cached != null) return cached

        val user = api.fetchUser(id)
        return cache.putIfAbsent(id, user) ?: user
    }
}
```

Solution 3: Actor-style single-threaded state owner (`Channel` + scope).

```kotlin
sealed class CacheMessage
class GetUser(
    val id: String,
    val response: CompletableDeferred<User>
) : CacheMessage()

class UserCache(private val api: Api, scope: CoroutineScope) {
    private val cache = mutableMapOf<String, User>()
    private val channel = Channel<CacheMessage>()

    init {
        scope.launch {
            for (msg in channel) {
                when (msg) {
                    is GetUser -> {
                        val user = cache[msg.id] ?: run {
                            val fetched = api.fetchUser(msg.id)
                            cache[msg.id] = fetched
                            fetched
                        }
                        msg.response.complete(user)
                    }
                }
            }
        }
    }

    suspend fun getUser(id: String): User {
        val response = CompletableDeferred<User>()
        channel.send(GetUser(id, response))
        return response.await()
    }
}
```

### Detection Techniques

1. Stress testing: many coroutines, many iterations, compare expected vs actual.

```kotlin
@Test
fun `stress test for race conditions`() = runTest {
    val counter = java.util.concurrent.atomic.AtomicInteger(0)
    val iterations = 10_000
    val coroutines = 100

    repeat(coroutines) {
        launch {
            repeat(iterations) {
                // Exercise concurrent access
                counter.incrementAndGet()
            }
        }
    }

    val expected = coroutines * iterations
    val actual = counter.get()

    assertEquals(expected, actual, "Race condition detected or lost increments!")
}
```

2. Logging with timestamps / tracing interleavings.

```kotlin
var sharedState = 0
val log = ConcurrentLinkedQueue<String>()

suspend fun operation(id: Int) {
    val before = sharedState
    log.add("[$id] Read: $before at ${'$'}{System.nanoTime()}")

    delay(10)

    sharedState = before + 1
    log.add("[$id] Wrote: ${'$'}sharedState at ${'$'}{System.nanoTime()}")
}

launch { operation(1) }
launch { operation(2) }

delay(100)

log.forEach { println(it) }
```

3. Thread Sanitizer (primarily Kotlin/Native; JVM support limited/experimental).

```kotlin
// Kotlin/Native example
kotlin {
    linuxX64 {
        binaries {
            executable {
                freeCompilerArgs += listOf("-Xbinary=sanitizer=thread")
            }
        }
    }
}
```

4. Code review checklist:

- Are there shared mutable variables?
- Are they accessed from multiple coroutines/threads?
- Is access synchronized (`Mutex`, Atomics, confined context, etc.)?
- Are there check-then-act patterns?
- Are there read-modify-write operations?

### Prevention Strategy 1: Mutex

When to use: multiple operations must be atomic as a group.

```kotlin
class SessionManager {
    private val mutex = Mutex()
    private var userId: String? = null
    private var sessionToken: String? = null
    private var expiresAt: Long = 0

    suspend fun login(id: String, token: String, expiresIn: Long) {
        mutex.withLock {
            userId = id
            sessionToken = token
            expiresAt = System.currentTimeMillis() + expiresIn
        }
    }

    suspend fun getSession(): Triple<String?, String?, Long> = mutex.withLock {
        Triple(userId, sessionToken, expiresAt)
    }

    suspend fun isValid(): Boolean = mutex.withLock {
        userId != null && System.currentTimeMillis() < expiresAt
    }
}
```

### Prevention Strategy 2: Atomic Types

When to use: simple counters, flags, references.

```kotlin
class RequestCounter {
    private val count = java.util.concurrent.atomic.AtomicInteger(0)
    private val lastRequest = java.util.concurrent.atomic.AtomicLong(0)

    fun recordRequest() {
        count.incrementAndGet()
        lastRequest.set(System.currentTimeMillis())
    }

    fun getStats(): Pair<Int, Long> = count.get() to lastRequest.get()
}

// AtomicReference for complex objects
class ConfigManager {
    private val config = java.util.concurrent.atomic.AtomicReference<Config>(Config.default)

    fun updateConfig(new: Config) {
        config.set(new)
    }

    fun getConfig(): Config = config.get()
}
```

### Prevention Strategy 3: Confined Dispatcher / Context Confinement

When to use: keep mutable state confined to a single thread or a single serialized dispatcher.

```kotlin
class DatabaseManager(private val database: Database) {
    private val dbDispatcher = newSingleThreadContext("Database")
    private val cache = mutableMapOf<String, Data>()

    suspend fun getData(id: String): Data = withContext(dbDispatcher) {
        cache[id] ?: run {
            val data = database.query(id)
            cache[id] = data
            data
        }
    }

    suspend fun updateData(id: String, data: Data) = withContext(dbDispatcher) {
        cache[id] = data
        database.update(id, data)
    }
}
```

```kotlin
// Example of context confinement via limitedParallelism
class Repository(private val fetcher: suspend () -> Data) {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO.limitedParallelism(1)
    )

    private var cache: Data? = null

    fun getData(): Deferred<Data> = scope.async {
        cache ?: run {
            val data = fetcher()
            cache = data
            data
        }
    }
}
```

### Prevention Strategy 4: `StateFlow` (Immutable Updates)

When to use: observable state with atomic value replacement.

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _userState = MutableStateFlow<UserState>(UserState.Loading)
    val userState: StateFlow<UserState> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _userState.value = UserState.Loading
            try {
                val user = repository.getUser(userId)
                _userState.value = UserState.Success(user) // Atomic value update
            } catch (e: Exception) {
                _userState.value = UserState.Error(e.message)
            }
        }
    }
}

sealed class UserState {
    object Loading : UserState()
    data class Success(val user: User) : UserState()
    data class Error(val message: String?) : UserState()
}
```

Why relatively safe:
- Each write to `StateFlow`'s value is atomic as a whole.
- For invariants across multiple flows/variables you still need synchronization.

### Happens-Before Relationships (Coroutines + JVM)

Happens-before: a guarantee that effects of one operation are visible to another.

In coroutines (aligned with JVM semantics):

1. Starting a coroutine (`launch`/`async`) establishes order between the start call and the coroutine body execution.
2. Completion of a coroutine happens-before successful `join`/`await` by another coroutine.
3. `send` on a `Channel` happens-before the corresponding `receive` of that element.
4. For `Mutex`: all writes before `unlock` happen-before subsequent successful `lock` acquisitions that observe those writes.

```kotlin
var x = 0
val channel = Channel<Unit>()

// Coroutine 1
launch {
    x = 42
    channel.send(Unit) // Writes to x happen-before this send
}

// Coroutine 2
launch {
    channel.receive()  // Happens-after the send
    println(x)         // Must see 42
}
```

### Volatile and `@Volatile` in Kotlin (JVM)

`@Volatile` ensures visibility across threads but NOT atomicity or mutual exclusion.

```kotlin
// STILL RACY
@Volatile
var counter = 0

launch(Dispatchers.Default) { repeat(1000) { counter++ } }
launch(Dispatchers.Default) { repeat(1000) { counter++ } }

// counter++ is read-modify-write and remains non-atomic.
```

When to use `@Volatile` (JVM): simple publication/flags where each write is independent.

```kotlin
@Volatile
var isRunning = true

fun startWorker() = thread {
    while (isRunning) {
        // Do work
    }
}

// From another thread:
isRunning = false // Visible promptly to the worker thread
```

Key difference:
- `@Volatile`: visibility only; does not make increments or composite operations atomic.
- Atomic types (e.g., `AtomicInteger`): visibility + atomic read-modify-write operations.

### Testing for Race Conditions

Pattern: heavy concurrent access + repeated runs to increase the chance of catching races.

```kotlin
@Test
fun `test no race condition in counter`() = runTest {
    val counter = SafeCounter() // Your implementation
    val iterations = 1000
    val coroutines = 100

    val jobs = List(coroutines) {
        launch {
            repeat(iterations) {
                counter.increment()
            }
        }
    }

    jobs.joinAll()

    val expected = coroutines * iterations
    val actual = counter.get()

    assertEquals(expected, actual)
}

@Test
fun `stress test 100 times`() {
    repeat(100) {
        `test no race condition in counter`()
    }
}
```

### Real-World Example: Session Management

Problem: concurrent login/logout causing inconsistent state.

```kotlin
// RACY
class SessionManager {
    private var currentUser: User? = null
    private var loginTime: Long = 0

    suspend fun login(user: User) {
        currentUser = user
        delay(10) // Simulate token fetch
        loginTime = System.currentTimeMillis()
    }

    suspend fun logout() {
        currentUser = null
        loginTime = 0
    }

    fun isLoggedIn(): Boolean = currentUser != null
}

// Concurrent login/logout can leave currentUser set but loginTime = 0, etc.
```

Solution: protect the invariant as a whole.

```kotlin
// SAFE
class SafeSessionManager {
    private val mutex = Mutex()
    private var session: Session? = null

    suspend fun login(user: User) {
        val token = fetchToken(user)
        val newSession = Session(user, token, System.currentTimeMillis())
        mutex.withLock {
            session = newSession
        }
    }

    suspend fun logout() {
        mutex.withLock {
            session = null
        }
    }

    suspend fun getSession(): Session? = mutex.withLock { session }
}

data class Session(
    val user: User,
    val token: String,
    val loginTime: Long
)
```

### Real-World Example: Cache Updates

Problem: lost updates / duplicate work.

```kotlin
// RACY
class ImageCache(private val downloader: suspend (String) -> Bitmap) {
    private val cache = mutableMapOf<String, Bitmap>()

    suspend fun getImage(url: String): Bitmap {
        cache[url]?.let { return it }

        val bitmap = downloader(url)
        cache[url] = bitmap
        return bitmap
    }
}

// Concurrent requests for the same URL can trigger multiple downloads.
```

Safe solution: share in-flight work and update cache under lock.

```kotlin
// SAFE
class ImageCache(
    private val scope: CoroutineScope,
    private val downloader: suspend (String) -> Bitmap
) {
    private val mutex = Mutex()
    private val cache = mutableMapOf<String, Bitmap>()
    private val pending = mutableMapOf<String, Deferred<Bitmap>>()

    suspend fun getImage(url: String): Bitmap {
        // Check cache under lock
        mutex.withLock { cache[url] }?.let { return it }

        // Check or create pending download under lock
        val deferred = mutex.withLock {
            pending[url] ?: scope.async(Dispatchers.IO) {
                downloader(url)
            }.also { pending[url] = it }
        }

        // Await result
        val bitmap = deferred.await()

        // Publish result under lock and clear pending
        return mutex.withLock {
            cache.getOrPut(url) { bitmap }.also {
                pending.remove(url)
            }
        }
    }
}
```

### `kotlinx.coroutines.sync` Primitives (JVM/Multiplatform)

Common primitives:

1. `Mutex` — mutual exclusion for critical sections.
2. `Semaphore` — limit concurrent coroutines.
3. `Channel` — message passing / actor-style confinement.
4. Atomic types — lock-free atomic operations (JVM via `java.util.concurrent.atomic`; platform-specific elsewhere).

```kotlin
import kotlinx.coroutines.sync.*

val mutex = Mutex()
mutex.withLock {
    // critical section
}

val semaphore = Semaphore(permits = 3)
semaphore.withPermit {
    // at most 3 concurrent executions
}

val channel = Channel<Int>()
launch { channel.send(42) }
launch { val value = channel.receive() }
```

### Best Practices for Concurrent Coroutine Code

1. Minimize shared mutable state; prefer immutable data.
2. Use thread-safe collections where appropriate (e.g., `ConcurrentHashMap` on JVM).
3. Synchronize access to shared state (`Mutex`, Atomics, confined dispatcher, actors).
4. Make compound operations atomic (merge check-then-act inside synchronization).
5. Use `StateFlow`/`SharedFlow` for observable state with atomic value replacements.
6. Document thread-safety guarantees for your APIs.
7. Test concurrency with stress tests and repeated runs.
8. Review code for known race patterns (check-then-act, read-modify-write, unsynchronized caches).
9. Use actor-style patterns for complex state machines and serialized mutation.
10. Monitor synchronization performance.

### Key Takeaways

1. Race conditions still happen: coroutines do not remove them.
2. Check-then-act is dangerous: make it atomic (`Mutex`, actors, confinement).
3. Read-modify-write requires synchronization: use Atomics or `Mutex`.
4. Shared mutable state is the root cause: minimize or protect it.
5. Use `Mutex` for complex atomicity across multiple operations.
6. Use Atomic types for simple counters/flags.
7. Use `StateFlow`/`SharedFlow` for observable state with atomic value updates.
8. Test concurrency thoroughly; stress tests can expose races.
9. `@Volatile` != atomic: it only ensures visibility (JVM).
10. Confined dispatchers/contexts serialize access: single owner = no races on that state.

---

## Дополнительные вопросы (RU)

1. Как вы обнаруживаете data race в Kotlin/JVM и Kotlin/Native, какие инструменты используете?
2. Как сравнить накладные расходы `Mutex`, атомарных типов и конфайнмента по потокам?
3. Какие подходы к lock-free алгоритмам применимы в экосистеме Kotlin корутин?
4. Как Java Memory Model влияет на поведение корутин на JVM?
5. Как вы предотвращаете состояния гонки при использовании операторов `Flow`?
6. Какие средства автоматического поиска гонок доступны для JVM и Native-проектов?
7. Как спроектировать API coroutine-библиотеки так, чтобы минимизировать вероятность гонок?

## Follow-ups

1. How do you detect data races in Kotlin/JVM vs Kotlin/Native?
2. What's the performance impact of different synchronization strategies?
3. How do you implement lock-free algorithms in Kotlin coroutines?
4. Can you explain the Java Memory Model's relation to coroutines on JVM?
5. How do you handle race conditions in `Flow` operators?
6. What tools exist for automated race condition detection on JVM vs Native?
7. How do you design race-free APIs for coroutine-based libraries?

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-debugging-coroutines-techniques--kotlin--medium]]
- [[q-mutex-synchronized-coroutines--kotlin--medium]]
- [[q-semaphore-rate-limiting--kotlin--medium]]

## References

- https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html
- https://docs.oracle.com/javase/specs/jls/se8/html/jls-17.html#jls-17.4
- https://kotlinlang.org/docs/native-testing.html#thread-sanitizer
- https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/atomic/package-summary.html
- [[c-kotlin]]
- [[c-coroutines]]
