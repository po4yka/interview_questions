---
id: 20251012-160007
title: "Race conditions and data races in Kotlin coroutines / Состояния гонки и data race в Kotlin корутинах"
topic: kotlin
difficulty: hard
status: draft
created: 2025-10-12
tags:
  - kotlin
  - coroutines
  - race-conditions
  - thread-safety
  - concurrency
  - data-races
  - bugs
moc: moc-kotlin
related: [q-job-vs-supervisorjob--kotlin--medium, q-flow-time-operators--kotlin--medium, q-kotlin-partition-function--programming-languages--easy]
  - q-mutex-synchronized-coroutines--kotlin--medium
  - q-semaphore-rate-limiting--kotlin--medium
  - q-debugging-coroutines-techniques--kotlin--medium
subtopics:
  - coroutines
  - race-conditions
  - thread-safety
  - concurrency
  - bugs
---

# Question (EN)
> What are race conditions and data races in Kotlin coroutines? How do you detect and prevent them?

# Вопрос (RU)
> Что такое состояния гонки и data race в Kotlin корутинах? Как их обнаруживать и предотвращать?

---

## Answer (EN)

Coroutines make concurrent programming easier, but they don't eliminate race conditions. When multiple coroutines access shared mutable state, subtle bugs can appear. Understanding race conditions vs data races, detection techniques, and prevention strategies is critical for production-ready coroutine code.



### Race Condition vs Data Race

**Race Condition:** Bug where program behavior depends on timing/ordering of concurrent operations.

**Data Race:** Two threads access same memory location concurrently, at least one is a write, without synchronization.

**Key difference:**
- **Data race** = low-level memory access problem
- **Race condition** = high-level logic problem

```kotlin
// Data race example
var counter = 0 // Shared mutable state

launch { repeat(1000) { counter++ } }
launch { repeat(1000) { counter++ } }

// Data race: Both coroutines read/write counter without synchronization
// Final value unpredictable (less than 2000)

// Race condition example
var balance = 100

launch {
    if (balance >= 50) { // Check
        delay(10)
        balance -= 50 // Use
    }
}

launch {
    if (balance >= 50) { // Check
        delay(10)
        balance -= 50 // Use
    }
}

// Race condition: Both pass check, balance becomes 0 (should fail second)
// Even with synchronized reads/writes, logic is still racy
```

### Common Race Condition Pattern: Check-Then-Act

**Problem:** State changes between check and action.

```kotlin
class BankAccount {
    private var balance = 100

    //  RACE CONDITION
    suspend fun withdraw(amount: Int): Boolean {
        if (balance >= amount) { // Check
            delay(10) // Simulate processing
            balance -= amount // Act
            return true
        }
        return false
    }
}

// Usage
val account = BankAccount()

launch { account.withdraw(60) } // Coroutine 1
launch { account.withdraw(60) } // Coroutine 2

// Both check passes (balance = 100)
// Both withdraw 60
// Final balance = -20 (should be 40 or 100, not negative!)
```

**Timeline:**

```
Time | Coroutine 1      | Coroutine 2      | Balance
-----|------------------|------------------|--------
t0   | check (100>=60)  |                  | 100
t1   |                  | check (100>=60)  | 100  ← Both pass!
t2   | delay(10)        | delay(10)        | 100
t3   | balance -= 60    |                  | 40
t4   |                  | balance -= 60    | -20  ← Bug!
```

**Solution: Mutex**

```kotlin
class BankAccount {
    private val mutex = Mutex()
    private var balance = 100

    //  CORRECT
    suspend fun withdraw(amount: Int): Boolean {
        return mutex.withLock {
            if (balance >= amount) {
                delay(10)
                balance -= amount
                true
            } else {
                false
            }
        }
    }
}
```

### Common Race Condition Pattern: Read-Modify-Write

**Problem:** Counter increment without synchronization.

```kotlin
var counter = 0

//  RACE CONDITION
repeat(1000) {
    launch {
        counter++ // Read-modify-write
    }
}

delay(1000)
println(counter) // Expected: 1000, Actual: < 1000
```

**Why?** `counter++` is three operations:
1. Read current value
2. Add 1
3. Write back

**Interleaving:**

```
Coroutine 1: Read(0)
Coroutine 2: Read(0)
Coroutine 1: Add(0+1)
Coroutine 2: Add(0+1)
Coroutine 1: Write(1)
Coroutine 2: Write(1)  ← Lost update! Should be 2
```

**Solutions:**

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

// Solution 2: AtomicInteger (better for simple counters)
val counter = AtomicInteger(0)

repeat(1000) {
    launch {
        counter.incrementAndGet()
    }
}

// Solution 3: Single-threaded confined dispatcher
val singleThreadContext = newSingleThreadContext("Counter")
var counter = 0

repeat(1000) {
    launch(singleThreadContext) {
        counter++ // Safe: always same thread
    }
}
```

### Shared Mutable State Problems

**Problem:** Multiple coroutines modifying shared state.

```kotlin
//  DANGEROUS
class UserCache {
    private val cache = mutableMapOf<String, User>()

    suspend fun getUser(id: String): User {
        return cache[id] ?: run {
            val user = api.fetchUser(id)
            cache[id] = user // RACE: Concurrent modification!
            user
        }
    }
}

// Concurrent calls can corrupt the map
launch { cache.getUser("1") }
launch { cache.getUser("2") }
launch { cache.getUser("3") }
```

**Solution 1: Mutex**

```kotlin
class UserCache {
    private val mutex = Mutex()
    private val cache = mutableMapOf<String, User>()

    suspend fun getUser(id: String): User {
        // Check outside lock for performance
        mutex.withLock { cache[id] }?.let { return it }

        // Fetch outside lock (expensive operation)
        val user = api.fetchUser(id)

        // Store inside lock
        mutex.withLock {
            cache.getOrPut(id) { user }
        }
    }
}
```

**Solution 2: ConcurrentHashMap**

```kotlin
class UserCache {
    private val cache = ConcurrentHashMap<String, User>()

    suspend fun getUser(id: String): User {
        return cache[id] ?: run {
            val user = api.fetchUser(id)
            cache.putIfAbsent(id, user) ?: user
        }
    }
}
```

**Solution 3: Actor pattern**

```kotlin
sealed class CacheMessage
data class GetUser(val id: String, val response: CompletableDeferred<User>) : CacheMessage()

class UserCache {
    private val cache = mutableMapOf<String, User>()
    private val actor = actor<CacheMessage> {
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

    suspend fun getUser(id: String): User {
        val response = CompletableDeferred<User>()
        actor.send(GetUser(id, response))
        return response.await()
    }
}
```

### Detection Techniques

**Technique 1: Stress testing**

```kotlin
@Test
fun `stress test for race conditions`() = runTest {
    val counter = AtomicInteger(0)
    val iterations = 10_000
    val coroutines = 100

    repeat(coroutines) {
        launch {
            repeat(iterations) {
                // Test concurrent access
                counter.incrementAndGet()
            }
        }
    }

    // Expected: coroutines * iterations
    val expected = coroutines * iterations
    val actual = counter.get()

    assertEquals(expected, actual, "Race condition detected!")
}
```

**Technique 2: Logging with timestamps**

```kotlin
var sharedState = 0
val log = ConcurrentLinkedQueue<String>()

suspend fun operation(id: Int) {
    val before = sharedState
    log.add("[$id] Read: $before at ${System.nanoTime()}")

    delay(10)

    sharedState = before + 1
    log.add("[$id] Wrote: ${sharedState} at ${System.nanoTime()}")
}

// Run concurrently
launch { operation(1) }
launch { operation(2) }

delay(100)

// Analyze log
log.forEach { println(it) }

// Output shows interleaving:
// [1] Read: 0 at 1234567890
// [2] Read: 0 at 1234567891  ← Both read 0!
// [1] Wrote: 1 at 1234577890
// [2] Wrote: 1 at 1234577891  ← Lost update!
```

**Technique 3: Thread Sanitizer (Native)**

```kotlin
// In Kotlin/Native, use Thread Sanitizer
// Add to gradle:
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

**Technique 4: Code review checklist**

- [ ] Are there shared mutable variables?
- [ ] Are they accessed from multiple coroutines?
- [ ] Is access synchronized (Mutex, Atomic, etc.)?
- [ ] Are there check-then-act patterns?
- [ ] Are there read-modify-write operations?

### Prevention Strategy 1: Mutex

**When to use:** Multiple operations need atomicity.

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

    suspend fun getSession(): Triple<String?, String?, Long> {
        return mutex.withLock {
            Triple(userId, sessionToken, expiresAt)
        }
    }

    suspend fun isValid(): Boolean {
        return mutex.withLock {
            userId != null && System.currentTimeMillis() < expiresAt
        }
    }
}
```

### Prevention Strategy 2: Atomic Types

**When to use:** Simple counters, flags, references.

```kotlin
class RequestCounter {
    private val count = AtomicInteger(0)
    private val lastRequest = AtomicLong(0)

    fun recordRequest() {
        count.incrementAndGet()
        lastRequest.set(System.currentTimeMillis())
    }

    fun getStats(): Pair<Int, Long> {
        return count.get() to lastRequest.get()
    }
}

// AtomicReference for complex objects
class ConfigManager {
    private val config = AtomicReference<Config>(Config.default)

    fun updateConfig(new: Config) {
        config.set(new) // Atomic update
    }

    fun getConfig(): Config {
        return config.get()
    }
}
```

### Prevention Strategy 3: Confined Dispatcher

**When to use:** State confined to single thread.

```kotlin
class DatabaseManager {
    private val dbDispatcher = newSingleThreadContext("Database")
    private val cache = mutableMapOf<String, Data>()

    suspend fun getData(id: String): Data = withContext(dbDispatcher) {
        // All access on same thread - no races!
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

### Prevention Strategy 4: StateFlow (Immutable Updates)

**When to use:** Observable state with atomic updates.

```kotlin
class UserViewModel : ViewModel() {
    private val _userState = MutableStateFlow<UserState>(UserState.Loading)
    val userState: StateFlow<UserState> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _userState.value = UserState.Loading

            try {
                val user = repository.getUser(userId)
                _userState.value = UserState.Success(user) // Atomic update
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

**Why safe?** StateFlow updates are atomic - no partial updates visible.

### Happens-Before Relationships

**Happens-before:** Guarantees that effects of one operation are visible to another.

**In coroutines:**

1. **launch/async start** happens-before **coroutine body**
2. **Coroutine body** happens-before **join/await**
3. **send** to channel happens-before **receive**
4. **Mutex lock** happens-before **code in lock**
5. **Code in lock** happens-before **mutex unlock**

```kotlin
var x = 0

// Thread 1
launch {
    x = 42
    channel.send(Unit) // Happens-before send
}

// Thread 2
launch {
    channel.receive() // Happens-after send
    println(x) // Always sees 42
}
```

### Volatile and @Volatile in Kotlin

**@Volatile:** Ensures visibility across threads, but NOT atomicity.

```kotlin
//  STILL RACY
@Volatile
var counter = 0

launch { repeat(1000) { counter++ } } // Not atomic!
launch { repeat(1000) { counter++ } }

// Counter++ is still read-modify-write, not atomic
```

**When to use @Volatile:**

```kotlin
//  CORRECT: Simple flag
@Volatile
var isRunning = false

launch {
    while (isRunning) {
        // Do work
    }
}

// From another thread
isRunning = false // Visible immediately
```

**Key difference:**
- `@Volatile`: Visibility only
- `Atomic*`: Visibility + atomicity

### Coroutine Context Confinement

**Pattern:** Confine mutable state to specific context.

```kotlin
class Repository {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO.limitedParallelism(1)
    )

    private var cache: Data? = null

    fun getData(): Deferred<Data> = scope.async {
        // All access serialized on single-thread dispatcher
        cache ?: run {
            val data = fetchData()
            cache = data
            data
        }
    }
}
```

### Testing for Race Conditions

**Test pattern: Concurrent access**

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

// Run multiple times to catch intermittent failures
@Test
fun `stress test 100 times`() {
    repeat(100) {
        `test no race condition in counter`()
    }
}
```

### Real-World Example: Session Management

**Problem: Concurrent login/logout**

```kotlin
//  RACY
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

    fun isLoggedIn(): Boolean {
        return currentUser != null
    }
}

// Concurrent login/logout can leave inconsistent state:
launch { manager.login(user) }
launch { manager.logout() }
// currentUser might be set but loginTime is 0!
```

**Solution:**

```kotlin
//  SAFE
class SessionManager {
    private val mutex = Mutex()
    private var session: Session? = null

    suspend fun login(user: User) {
        mutex.withLock {
            val token = fetchToken(user)
            session = Session(user, token, System.currentTimeMillis())
        }
    }

    suspend fun logout() {
        mutex.withLock {
            session = null
        }
    }

    suspend fun getSession(): Session? {
        return mutex.withLock { session }
    }
}

data class Session(
    val user: User,
    val token: String,
    val loginTime: Long
)
```

### Real-World Example: Cache Updates

**Problem: Lost cache updates**

```kotlin
//  RACY
class ImageCache {
    private val cache = mutableMapOf<String, Bitmap>()

    suspend fun getImage(url: String): Bitmap {
        cache[url]?.let { return it }

        val bitmap = downloadImage(url)
        cache[url] = bitmap
        return bitmap
    }
}

// Concurrent requests for same URL download twice
launch { cache.getImage("url1") }
launch { cache.getImage("url1") } // Downloads again!
```

**Solution: Deferred result**

```kotlin
//  SAFE
class ImageCache {
    private val mutex = Mutex()
    private val cache = mutableMapOf<String, Bitmap>()
    private val pending = mutableMapOf<String, Deferred<Bitmap>>()

    suspend fun getImage(url: String): Bitmap {
        // Check cache
        mutex.withLock { cache[url] }?.let { return it }

        // Check if download in progress
        val deferred = mutex.withLock {
            pending[url] ?: run {
                val newDeferred = CoroutineScope(Dispatchers.IO).async {
                    downloadImage(url)
                }
                pending[url] = newDeferred
                newDeferred
            }
        }

        // Wait for download
        val bitmap = deferred.await()

        // Store in cache
        mutex.withLock {
            cache[url] = bitmap
            pending.remove(url)
        }

        return bitmap
    }
}

// Now concurrent requests share single download
```

### kotlinx.coroutines.sync Primitives

**Available primitives:**

1. **Mutex** - Mutual exclusion (1 coroutine)
2. **Semaphore** - Limited concurrency (N coroutines)
3. **Channel** - Message passing
4. **Atomic*** - Lock-free atomic operations

```kotlin
import kotlinx.coroutines.sync.*

// Mutex
val mutex = Mutex()
mutex.withLock { /* critical section */ }

// Semaphore
val semaphore = Semaphore(permits = 3)
semaphore.withPermit { /* at most 3 concurrent */ }

// Channel
val channel = Channel<Int>()
launch { channel.send(42) }
launch { val value = channel.receive() }
```

### Best Practices for Concurrent Code

1.  **Minimize shared mutable state** - Prefer immutable data
2.  **Use thread-safe collections** - ConcurrentHashMap, etc.
3.  **Synchronize access** - Mutex, Atomic, confined dispatcher
4.  **Make operations atomic** - Combine check-then-act in lock
5.  **Use StateFlow for UI state** - Atomic updates
6.  **Document thread-safety** - Annotate thread-safe classes
7.  **Test concurrency** - Stress tests, multiple iterations
8.  **Code review** - Check for race patterns
9.  **Use actor pattern** - For complex state machines
10.  **Profile and measure** - Ensure synchronization isn't bottleneck

### Key Takeaways

1. **Race conditions still happen** - Coroutines don't eliminate them
2. **Check-then-act is dangerous** - Atomicize with Mutex
3. **Read-modify-write needs sync** - Use Atomic or Mutex
4. **Shared mutable state is root cause** - Minimize or protect
5. **Mutex for complex atomicity** - Multiple operations together
6. **Atomic for simple counters** - Lock-free, fast
7. **StateFlow for observable state** - Atomic updates
8. **Test concurrency thoroughly** - Stress tests catch races
9. **@Volatile ≠ atomic** - Only ensures visibility
10. **Confined dispatcher serializes** - Single-thread = no races

---

## Ответ (RU)

Корутины упрощают конкурентное программирование, но не устраняют состояния гонки. Когда несколько корутин обращаются к общему изменяемому состоянию, могут появиться тонкие баги. Понимание состояний гонки vs data race, техник обнаружения и стратегий предотвращения критично для production-ready корутинного кода.



[Полный русский перевод следует той же структуре]

### Ключевые выводы

1. **Состояния гонки все еще происходят** - Корутины не устраняют их
2. **Check-then-act опасен** - Атомизируйте с Mutex
3. **Read-modify-write требует синхронизации** - Используйте Atomic или Mutex
4. **Общее изменяемое состояние - корень зла** - Минимизируйте или защищайте
5. **Mutex для сложной атомарности** - Несколько операций вместе
6. **Atomic для простых счетчиков** - Без блокировок, быстро
7. **StateFlow для наблюдаемого состояния** - Атомарные обновления
8. **Тщательно тестируйте конкурентность** - Стресс-тесты ловят гонки
9. **@Volatile ≠ атомарность** - Только гарантирует видимость
10. **Ограниченный диспетчер сериализует** - Один поток = нет гонок

---

## Follow-ups

1. How do you detect data races in Kotlin/JVM vs Kotlin/Native?
2. What's the performance impact of different synchronization strategies?
3. How do you implement lock-free algorithms in Kotlin coroutines?
4. Can you explain the Java Memory Model's relation to coroutines?
5. How do you handle race conditions in Flow operators?
6. What tools exist for automated race condition detection?
7. How do you design race-free APIs for libraries?

## References

- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Java Memory Model](https://docs.oracle.com/javase/specs/jls/se8/html/jls-17.html#jls-17.4)
- [Kotlin Atomics](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.concurrent/)
- [ThreadSanitizer](https://github.com/google/sanitizers/wiki/ThreadSanitizerCppManual)

## Related Questions

- [[q-mutex-synchronized-coroutines--kotlin--medium|Mutex vs synchronized]]
- [[q-semaphore-rate-limiting--kotlin--medium|Semaphore usage]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging coroutines]]
