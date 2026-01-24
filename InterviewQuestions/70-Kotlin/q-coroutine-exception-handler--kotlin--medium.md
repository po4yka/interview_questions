---
anki_cards:
- slug: q-coroutine-exception-handler--kotlin--medium-0-en
  language: en
  anki_id: 1768326284957
  synced_at: '2026-01-23T17:03:50.959120'
- slug: q-coroutine-exception-handler--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326284980
  synced_at: '2026-01-23T17:03:50.961262'
---
# Question (EN)
> What is CoroutineExceptionHandler, where can it be installed, and how does it work with different coroutine builders (launch vs async)?

## Ответ (RU)

Необработанные исключения в корутинах могут приводить к краху приложения или незаметному сбою, затрудняя отладку. **CoroutineExceptionHandler (CEH)** предоставляет механизм последней инстанции для обработки необработанных исключений в корутинах. Однако он работает не везде и подчиняется специфическим правилам взаимодействия со структурированной конкурентностью.

```kotlin
import kotlinx.coroutines.*

val handler = CoroutineExceptionHandler { _, exception ->
    println("Поймано исключение: $exception")
}

fun main() = runBlocking {
    val job = GlobalScope.launch(handler) {
        throw RuntimeException("Тестовое исключение")
    }
    job.join()
}
// Упрощённый вывод: Поймано исключение: java.lang.RuntimeException: Тестовое исключение
```

### Что Такое CoroutineExceptionHandler?

**CoroutineExceptionHandler** — это `CoroutineContext.Element`, который участвует в обработке необработанных исключений в корутинах. Он действует как **обработчик последней инстанции**, аналог `Thread.UncaughtExceptionHandler` для потоков: используется, когда исключение не перехвачено внутри корутины и не обработано вызывающей стороной.

### Ключевые Принципы

Обработка исключений в корутинах подчиняется правилам структурированной конкурентности:

- Сначала исключения обрабатываются локально (через `try-catch` внутри корутины).
- Затем они распространяются вверх по иерархии `Job` к родителю.
- Для "корневой" корутины (без родителя в текущем scope) необработанное исключение репортится в `CoroutineExceptionHandler`, присутствующий в её контексте.

**CEH гарантированно выступает как обработчик последней инстанции для:**
1. Необработанных исключений в **корневых корутинах** (прямых потомках `CoroutineScope`, не являющихся дочерними другой корутины в этом scope).
2. Корутин, запущенных через **`launch`** (fire-and-forget), если их исключения не перехвачены другими способами.
3. **`actor`**-корутин, которые по поведению соответствуют `launch`.

**Обычно CEH НЕ обрабатывает исключения для:**
1. **`async`** в нормальном сценарии, так как ошибки передаются через `Deferred` и `await()`. Ожидается, что вызывающий код обработает исключение при `await()`. (Для корневых `async`, результат которых никогда не ожидается и становится недостижимым, реализация может репортить исключения глобальному обработчику — на это нельзя опираться как на гарантированный механизм.)
2. **Промежуточных дочерних корутин**, где исключения сначала поднимаются к родительскому `Job`; CEH по факту определяется контекстом корневого/верхнего родителя.
3. **`runBlocking`**, где исключения выбрасываются непосредственно в вызывающий поток и обрабатываются обычным образом.
4. Дочерних корутин внутри `supervisorScope`, если ни у ребёнка, ни у охватывающего scope нет CEH: сбои изолированы, и для last-resort обработки нужно явно навешивать CEH на нужный scope/корутину.

По цепочке контекста ищется ближайший `CoroutineExceptionHandler`: если у дочерней корутины есть свой CEH, он имеет приоритет; иначе используется ближайший выше по иерархии.

### CEH С Launch (Работает)

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH поймал: ${exception.message}")
    }

    // РАБОТАЕТ: корневая launch с CEH в контексте
    val job = launch(handler) {
        throw RuntimeException("Исключение в launch")
    }

    job.join()
    println("Программа продолжается")
}

// Вывод:
// CEH поймал: Исключение в launch
// Программа продолжается
```

### CEH С Async (Поведение)

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH поймал: ${exception.message}")
    }

    val deferred = async(handler) {
        throw RuntimeException("Исключение в async")
    }

    try {
        deferred.await() // Исключение выбрасывается ЗДЕСЬ
    } catch (e: Exception) {
        println("Поймано в try-catch: ${e.message}")
    }
}

// Вывод:
// Поймано в try-catch: Исключение в async
// CEH не вызывается, так как исключение обработано через await()
```

Почему так? `async` по контракту передаёт результат/ошибку через `await()`. Пока вызывающая сторона может и действительно получает исключение через `await()`, `CoroutineExceptionHandler` не используется. Если корневой `Deferred` никогда не ожидается, его ошибка может быть репортнута глобальному обработчику при сборке мусора, но это недетерминированно и не должно использоваться для бизнес-логики.

### Иерархия Распространения Исключений

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: ${exception.message}")
    }

    // Корневая корутина с CEH
    launch(handler) {
        println("Родительская корутина")

        // Дочерняя корутина: её исключение поднимается к родителю;
        // CEH родителя обработает его, если оно не перехвачено локально.
        launch {
            throw RuntimeException("Исключение в дочерней корутине")
        }

        delay(100)
        println("Этот код может не выполниться, если родитель упадёт")
    }

    delay(500)
}

// Упрощённый вывод:
// Родительская корутина
// CEH: Исключение в дочерней корутине
```

Практически: исключения детей поднимаются ВВЕРХ к родителю. Необработанные исключения корневых корутин обрабатываются ближайшим CEH по цепочке контекста.

### Установка CEH В CoroutineScope

Паттерн 1: CEH на уровне scope

```kotlin
class MyRepository {
    private val handler = CoroutineExceptionHandler { _, exception ->
        Log.e("Repository", "Необработанное исключение", exception)
        // Отправить в crash-reporting
    }

    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO + handler
    )

    fun fetchData() {
        scope.launch {
            // Необработанные исключения в этом корневом launch
            // будут залогированы handler
            throw RuntimeException("Fetch failed")
        }
    }

    fun cleanup() {
        scope.cancel()
    }
}
```

Паттерн 2: CEH для конкретной корутины

```kotlin
fun fetchDataWithCustomHandler() = viewModelScope.launch {
    val handler = CoroutineExceptionHandler { _, exception ->
        _errorState.value = "Ошибка: ${exception.message}"
    }

    // У этого дочернего launch свой CEH; его необработанные исключения пойдут туда.
    launch(handler) {
        val data = api.fetchData()
        _dataState.value = data
    }
}
```

### Обработчик По Умолчанию

Если для необработанного исключения корневой корутины CEH не установлен, используется платформенный обработчик по умолчанию:

- JVM: печать стектрейса в `System.err`.
- Android: интеграция с `Thread.getDefaultUncaughtExceptionHandler()`, возможен краш приложения.
- JS: лог в консоль.
- Native: завершение процесса.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch {
        throw RuntimeException("Uncaught")
    }
    delay(100)
}

// Упрощённый вывод:
// Exception in thread "main" java.lang.RuntimeException: Uncaught
//   at ...
```

### CEH В Android Application

Глобальный обработчик на уровне `Application`:

```kotlin
class MyApplication : Application() {
    lateinit var appExceptionHandler: CoroutineExceptionHandler
        private set

    override fun onCreate() {
        super.onCreate()

        appExceptionHandler = CoroutineExceptionHandler { _, exception ->
            Log.e("App", "Необработанное исключение корутины", exception)
            FirebaseCrashlytics.getInstance().recordException(exception)
            // Для UI действий переключайтесь на Main dispatcher явно.
        }

        // Используйте этот handler в application-level scopes.
    }
}
```

`ViewModel` с CEH:

```kotlin
class UserViewModel : ViewModel() {
    private val handler = CoroutineExceptionHandler { _, exception ->
        Log.e("UserViewModel", "Ошибка", exception)
        _errorState.value = exception.toUserFriendlyMessage()
    }

    private val vmScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main + handler
    )

    private val _errorState = MutableStateFlow<String?>(null)
    val errorState: StateFlow<String?> = _errorState.asStateFlow()

    private val _userState = MutableStateFlow<User?>(null)
    val userState: StateFlow<User?> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        vmScope.launch {
            val user = userRepository.getUser(userId)
            _userState.value = user
        }
    }

    override fun onCleared() {
        super.onCleared()
        vmScope.cancel()
    }
}

fun Exception.toUserFriendlyMessage(): String {
    return when (this) {
        is NetworkException -> "Проблемы с сетью. Проверьте подключение."
        is AuthException -> "Ошибка аутентификации. Пожалуйста, войдите снова."
        else -> "Произошла непредвиденная ошибка."
    }
}
```

### Почему CEH Обычно Не Ловит Исключения В Async

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: $exception")
    }

    // Сценарий: async с корректным await()
    val deferred = async(handler) {
        throw RuntimeException("Ошибка")
    }

    try {
        deferred.await()
    } catch (e: Exception) {
        println("Поймано: ${e.message}")
    }

    // Если никогда не вызвать await() для корневого Deferred,
    // его исключение может быть репортнуто глобальным обработчиком при GC,
    // но это не гарантировано и не должно использоваться как стратегия.
}
```

Итог: всегда явно вызывайте `await()` (или иным образом потребляйте `Deferred`) и обрабатывайте ошибки; CEH предназначен для необработанных исключений, а не замены `await()`.

### Взаимодействие supervisorScope И CEH

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: ${exception.message}")
    }

    // CEH является частью контекста этого launch
    launch(handler) {
        supervisorScope {
            // Child 1: без локального CEH; его исключение
            // пойдёт к родителю (с handler) и будет там залогировано.
            launch {
                throw RuntimeException("Исключение Child 1")
            }

            // Child 2: продолжает выполнение, даже если Child 1 упал
            launch {
                delay(100)
                println("Child 2 всё ещё работает")
            }
        }
    }

    delay(300)
}

// Упрощённый вывод:
// CEH: Исключение Child 1
// Child 2 всё ещё работает
```

Если CEH навешан только на родительский `launch`, он обработает необработанные исключения дочерних корутин внутри `supervisorScope`, сохраняя их независимость. Для отдельной политики по детям добавляйте CEH на каждый нужный `launch`.

### Реальный Пример: Логирование И Аналитика

```kotlin
class ProductionCoroutineExceptionHandler(
    private val analytics: AnalyticsService,
    private val crashReporter: CrashReportingService
) : CoroutineExceptionHandler {

    override val key: CoroutineContext.Key<*> = CoroutineExceptionHandler

    override fun handleException(context: CoroutineContext, exception: Throwable) {
        Log.e("CEH", "Необработанное исключение в корутине", exception)

        val coroutineName = context[CoroutineName]?.name ?: "unnamed"
        val job = context[Job]

        analytics.logEvent("coroutine_exception") {
            param("coroutine_name", coroutineName)
            param("exception_type", exception::class.simpleName ?: "Unknown")
            param("exception_message", exception.message ?: "No message")
        }

        crashReporter.recordException(exception) {
            setCustomKey("coroutine_name", coroutineName)
            setCustomKey("job_cancelled", job?.isCancelled.toString())
        }

        when (exception) {
            is CancellationException -> {
                // Ожидаемое завершение — игнорируем
            }
            is NetworkException -> {
                // Нефатальная ошибка сети
            }
            else -> {
                // Политика: логировать, возможно, падать в debug и т.п.
            }
        }
    }
}

class MyViewModel(
    private val ceh: ProductionCoroutineExceptionHandler
) : ViewModel() {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main + ceh
    )

    fun loadData() {
        scope.launch(CoroutineName("LoadData")) {
            repository.fetchData()
        }
    }
}
```

### Ограничения CEH И Альтернативы

Ограничения:

1. Не заменяет явную обработку ошибок; это обработчик последней инстанции.
2. Не используется в обычном потоке `async`/`await`; ошибки нужно ловить при `await()`.
3. `CancellationException` обычно не считается ошибкой.
4. В некоторых конфигурациях критические сбои всё равно могут привести к крашу приложения.

Альтернативы/дополнения:

```kotlin
// Локальный try-catch
launch {
    try {
        riskyOperation()
    } catch (e: Exception) {
        handleError(e)
    }
}

// runCatching
launch {
    runCatching {
        riskyOperation()
    }.onFailure { exception ->
        handleError(exception)
    }
}

// Обёртка Result
launch {
    val result = repository.fetchData() // Возвращает Result<T>
    result.onSuccess { data ->
        updateUI(data)
    }.onFailure { exception ->
        showError(exception)
    }
}

// Flow + catch
repository.dataFlow
    .catch { exception ->
        emit(ErrorState(exception))
    }
    .collect { data ->
        updateUI(data)
    }
```

### Типичные Ошибки

Ошибка 1: Считать, что CEH заменяет структурированную обработку исключений.

```kotlin
// ПЛОХО: полагаться только на CEH, без локальной обработки
launch(handler) {
    val data = api.fetchData()
    updateUI(data)
}
```

Ошибка 2: Ожидать, что CEH обработает исключения `async`, которые потребляются через `await()`.

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Не будет вызвано для исключений, обработанных через await: $exception")
}

async(handler) {
    throw RuntimeException("Exception")
}.await() // Исключение обрабатывается await/try-catch, а не CEH
```

Ошибка 3: Отсутствие CEH (или любого логирования) на долгоживущих application scope.

```kotlin
// Без CEH: необработанные исключения идут только в обработчик по умолчанию
val appScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
```

### Лучшие Практики (RU)

1. Используйте CEH для неожиданных исключений и централизованного логирования:

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    if (exception !is CancellationException) {
        Log.e("App", "Неожиданное исключение", exception)
        reportToCrashlytics(exception)
    }
}
```

1. Комбинируйте CEH с явной обработкой ожидаемых ошибок:

```kotlin
launch(handler) {
    try {
        val data = api.fetchData()
        updateUI(data)
    } catch (e: NetworkException) {
        showNetworkError()
    }
    // CEH залогирует действительно неожиданные ошибки
}
```

1. Используйте `SupervisorJob` вместе с CEH для независимых дочерних задач:

```kotlin
val scope = CoroutineScope(
    SupervisorJob() + Dispatchers.Main + handler
)
```

1. Именуйте корутины (`CoroutineName`) для улучшения диагностики:

```kotlin
launch(handler + CoroutineName("FetchUser")) {
    // Имя корутины появится в логах CEH
}
```

1. Не полагайтесь только на CEH:

```kotlin
// ПЛОХО: только CEH
launch(handler) {
    val data = api.fetchData()
    updateUI(data)
}

// ЛУЧШЕ: явная обработка + CEH как fallback
launch(handler) {
    try {
        val data = api.fetchData()
        updateUI(data)
    } catch (e: ApiException) {
        showError(e)
    }
}
```

### Тестирование CEH (RU)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class CEHTest {
    @Test
    fun `CEH ловит исключения в launch`() = runTest {
        var caughtException: Throwable? = null

        val handler = CoroutineExceptionHandler { _, exception ->
            caughtException = exception
        }

        val job = launch(handler) {
            throw RuntimeException("Test exception")
        }

        job.join()

        assertTrue(caughtException is RuntimeException)
        assertEquals("Test exception", caughtException?.message)
    }

    @Test
    fun `CEH не обрабатывает async-исключения, потреблённые через await`() = runTest {
        var caughtByHandler = false

        val handler = CoroutineExceptionHandler { _, _ ->
            caughtByHandler = true
        }

        val deferred = async(handler) {
            throw RuntimeException("Test exception")
        }

        var caughtByTryCatch = false
        try {
            deferred.await()
        } catch (e: Exception) {
            caughtByTryCatch = true
        }

        assertTrue(caughtByTryCatch)
        assertTrue(!caughtByHandler)
    }

    @Test
    fun `CEH в детях supervisorScope`() = runTest {
        val exceptions = mutableListOf<Throwable>()

        val handler = CoroutineExceptionHandler { _, exception ->
            exceptions.add(exception)
        }

        supervisorScope {
            launch(handler) {
                throw RuntimeException("Child 1")
            }

            launch(handler) {
                throw RuntimeException("Child 2")
            }
        }

        assertEquals(2, exceptions.size)
    }
}
```

### Ключевые Выводы (RU)

1. CEH — обработчик последней инстанции для необработанных исключений.
2. Надёжно применяется к корневым `launch`/`actor`; дочерние корутины прокидывают исключения к ближайшему CEH в цепочке родителей.
3. Не заменяет обработку ошибок для `async`/`await`; там ошибки нужно ловить при `await()`.
4. Ставьте CEH на `CoroutineScope` или верхнеуровневые `launch` для централизованного логирования.
5. Комбинируйте с `SupervisorJob`, чтобы изолировать сбои и при этом логировать их.
6. Используйте `CoroutineName` + CEH для улучшения диагностики.
7. Применяйте CEH для логирования/аналитики/crash reporting, но не для маскировки ожидаемых ошибок.

---

## Answer (EN)

Unhandled exceptions in coroutines can crash your application or silently break flows, making debugging hard. **CoroutineExceptionHandler (CEH)** provides a last-resort mechanism for uncaught exceptions in coroutines. It does not apply everywhere and must be understood in the context of structured concurrency.

```kotlin
import kotlinx.coroutines.*

val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught exception: $exception")
}

fun main() = runBlocking {
    val job = GlobalScope.launch(handler) {
        throw RuntimeException("Test exception")
    }
    job.join()
}
// Output (simplified): Caught exception: java.lang.RuntimeException: Test exception
```

### What is CoroutineExceptionHandler?

**CoroutineExceptionHandler** is a `CoroutineContext.Element` that participates in handling uncaught exceptions in coroutines. It acts as a **last-resort handler**, similar in spirit to `Thread.UncaughtExceptionHandler` for threads: it's consulted when exceptions are not caught inside the coroutine and not handled by callers.

### Key Principles

`Coroutine` exception handling follows structured concurrency rules:

- Exceptions are first handled locally (try-catch inside the coroutine).
- Then they propagate up the Job hierarchy to the parent.
- For a "root" coroutine (one that has no parent within the current scope), an uncaught exception is reported to the `CoroutineExceptionHandler` present in its context.

**CEH reliably acts as last-resort handler for:**
1. Uncaught exceptions in **root coroutines** (direct children of a `CoroutineScope` that are not themselves children of another coroutine in that scope).
2. Coroutines started with **`launch`** (fire-and-forget style) when their exceptions are not otherwise consumed.
3. **`actor`** coroutines, which behave like `launch` regarding exceptions.

**Typically, CEH does NOT handle exceptions for:**
1. **`async`** on its normal path, because it exposes failures via `Deferred` and `await()`. You are expected to handle exceptions when awaiting. (For root async coroutines whose result is never awaited and becomes unreachable, the implementation may report their exceptions to a global handler; do not rely on this as a control-flow mechanism.)
2. **Intermediate child coroutines** where exceptions propagate to their parent job; CEH is effectively determined by the context of the root/parent with no further parent, not by every nested child.
3. **`runBlocking`**, which throws exceptions directly to the caller; you handle them as regular exceptions.
4. Children inside `supervisorScope` if neither the child nor its enclosing scope has a CEH: failures are isolated, and you must attach CEH where you need last-resort handling.

Exception propagation looks for the nearest `CoroutineExceptionHandler` in the context chain: a CEH attached directly to a child takes precedence over one in its parent; otherwise, the nearest one up the hierarchy is used.

### CEH with Launch (Works)

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH caught: ${exception.message}")
    }

    // WORKS: root launch with CEH in context
    val job = launch(handler) {
        throw RuntimeException("Exception in launch")
    }

    job.join()
    println("Program continues")
}

// Output:
// CEH caught: Exception in launch
// Program continues
```

### CEH with Async (Behavior)

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH caught: ${exception.message}")
    }

    val deferred = async(handler) {
        throw RuntimeException("Exception in async")
    }

    try {
        deferred.await() // Exception thrown HERE
    } catch (e: Exception) {
        println("Caught in try-catch: ${e.message}")
    }
}

// Output:
// Caught in try-catch: Exception in async
// CEH is not called because the exception is consumed via await()
```

**Why?** `async` is designed to deliver its result (or failure) through `await()`. As long as the caller can and does observe the exception via `await()`, `CoroutineExceptionHandler` is not used. If you never `await()` a root `Deferred`, its failure may eventually get reported as an unhandled exception when the `Deferred` is garbage-collected, but this is an implementation detail and not a robust error-handling strategy.

### Exception Propagation Hierarchy

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: ${exception.message}")
    }

    // Root coroutine with CEH
    launch(handler) {
        println("Parent coroutine")

        // Child coroutine: its exception propagates to parent;
        // parent's CEH will handle it if uncaught.
        launch {
            throw RuntimeException("Child exception")
        }

        delay(100)
        println("This may not execute if parent fails")
    }

    delay(500)
}

// Output (simplified):
// Parent coroutine
// CEH: Child exception
```

Rule of thumb: Exceptions in child coroutines propagate UP to their parent job. The nearest `CoroutineExceptionHandler` found in the effective context/parent chain handles uncaught exceptions of a failing root.

### Installing CEH in CoroutineScope

Pattern 1: Scope-level CEH

```kotlin
class MyRepository {
    private val handler = CoroutineExceptionHandler { _, exception ->
        Log.e("Repository", "Uncaught exception", exception)
        // Send to crash reporting (Firebase Crashlytics, Sentry)
    }

    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO + handler
    )

    fun fetchData() {
        scope.launch {
            // Uncaught exceptions in this root launch will be logged by handler
            throw RuntimeException("Fetch failed")
        }
    }

    fun cleanup() {
        scope.cancel()
    }
}
```

Pattern 2: Per-coroutine CEH

```kotlin
fun fetchDataWithCustomHandler() = viewModelScope.launch {
    val handler = CoroutineExceptionHandler { _, exception ->
        _errorState.value = "Error: ${exception.message}"
    }

    // This child launch has its own CEH; its uncaught exceptions go there.
    launch(handler) {
        val data = api.fetchData()
        _dataState.value = data
    }
}
```

### Default Exception Handler

If no `CoroutineExceptionHandler` is installed for an uncaught exception in a root coroutine, the default platform handler is used:

- JVM: prints stack trace to `System.err`.
- Android: integrates with `Thread.getDefaultUncaughtExceptionHandler()`; may crash the app.
- JS: logs to console.
- Native: terminates the program.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch {
        throw RuntimeException("Uncaught")
    }
    delay(100)
}

// Output (simplified):
// Exception in thread "main" java.lang.RuntimeException: Uncaught
//   at ...
```

### CEH in Android Application

Global-style crash/report handler in `Application`:

```kotlin
class MyApplication : Application() {
    lateinit var appExceptionHandler: CoroutineExceptionHandler
        private set

    override fun onCreate() {
        super.onCreate()

        appExceptionHandler = CoroutineExceptionHandler { _, exception ->
            Log.e("App", "Uncaught coroutine exception", exception)
            FirebaseCrashlytics.getInstance().recordException(exception)
            // If you need to touch UI (e.g., Toast), switch to Main dispatcher explicitly.
        }

        // Use this handler in your application-level scopes.
    }
}
```

`ViewModel` with CEH:

```kotlin
class UserViewModel : ViewModel() {
    private val handler = CoroutineExceptionHandler { _, exception ->
        Log.e("UserViewModel", "Error", exception)
        _errorState.value = exception.toUserFriendlyMessage()
    }

    private val vmScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main + handler
    )

    private val _errorState = MutableStateFlow<String?>(null)
    val errorState: StateFlow<String?> = _errorState.asStateFlow()

    private val _userState = MutableStateFlow<User?>(null)
    val userState: StateFlow<User?> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        vmScope.launch {
            val user = userRepository.getUser(userId)
            _userState.value = user
        }
    }

    override fun onCleared() {
        super.onCleared()
        vmScope.cancel()
    }
}

fun Exception.toUserFriendlyMessage(): String {
    return when (this) {
        is NetworkException -> "Network error. Please check your connection."
        is AuthException -> "Authentication failed. Please log in again."
        else -> "An unexpected error occurred."
    }
}
```

### Why CEH Doesn't Normally Catch Exceptions in Async

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: $exception")
    }

    // Scenario: async with proper await()
    val deferred = async(handler) {
        throw RuntimeException("Error")
    }

    try {
        deferred.await()
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }

    // If you never await() a root Deferred, its exception may
    // eventually be reported via the global handler when GC'ed,
    // but this is not deterministic and must not be relied upon.
}
```

Summary: always `await()` async results (or otherwise consume `Deferred`) and handle failures explicitly; CEH is for uncaught exceptions, not for replacing `await()` handling.

### supervisorScope and CEH Interaction

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: ${exception.message}")
    }

    // CEH is part of this launch's context
    launch(handler) {
        supervisorScope {
            // Child 1: no local CEH; its exception propagates
            // to the parent (which has handler) and is logged there.
            launch {
                throw RuntimeException("Child 1 exception")
            }

            // Child 2: continues even if child 1 fails
            launch {
                delay(100)
                println("Child 2 still running")
            }
        }
    }

    delay(300)
}

// Output (simplified):
// CEH: Child 1 exception
// Child 2 still running
```

If you attach CEH only at the parent launch, it will handle uncaught exceptions from its `supervisorScope` children while preserving their independence. If you need different handling per child, attach CEH directly to those child coroutines.

### Real-World Example: Logging and Analytics

```kotlin
class ProductionCoroutineExceptionHandler(
    private val analytics: AnalyticsService,
    private val crashReporter: CrashReportingService
) : CoroutineExceptionHandler {

    override val key: CoroutineContext.Key<*> = CoroutineExceptionHandler

    override fun handleException(context: CoroutineContext, exception: Throwable) {
        Log.e("CEH", "Unhandled exception in coroutine", exception)

        val coroutineName = context[CoroutineName]?.name ?: "unnamed"
        val job = context[Job]

        analytics.logEvent("coroutine_exception") {
            param("coroutine_name", coroutineName)
            param("exception_type", exception::class.simpleName ?: "Unknown")
            param("exception_message", exception.message ?: "No message")
        }

        crashReporter.recordException(exception) {
            setCustomKey("coroutine_name", coroutineName)
            setCustomKey("job_cancelled", job?.isCancelled.toString())
        }

        when (exception) {
            is CancellationException -> {
                // Expected, ignore
            }
            is NetworkException -> {
                // Non-fatal, maybe show transient error
            }
            else -> {
                // Decide policy: log only, or rethrow in debug builds, etc.
            }
        }
    }
}

class MyViewModel(
    private val ceh: ProductionCoroutineExceptionHandler
) : ViewModel() {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main + ceh
    )

    fun loadData() {
        scope.launch(CoroutineName("LoadData")) {
            repository.fetchData()
        }
    }
}
```

### CEH Limitations and Alternatives

Limitations:

1. Does not replace proper error handling; it is last-resort.
2. Not used for the normal `async`/`await` flow; handle exceptions via `await()`.
3. Cancellation (`CancellationException`) is not treated as an error.
4. In some configurations, certain fatal failures may still crash the app despite CEH.

Alternatives / complements:

```kotlin
// Try-catch inside coroutine
launch {
    try {
        riskyOperation()
    } catch (e: Exception) {
        handleError(e)
    }
}

// runCatching
launch {
    runCatching {
        riskyOperation()
    }.onFailure { exception ->
        handleError(exception)
    }
}

// Result wrapper
launch {
    val result = repository.fetchData() // Returns Result<T>
    result.onSuccess { data ->
        updateUI(data)
    }.onFailure { exception ->
        showError(exception)
    }
}

// Flow with catch
repository.dataFlow
    .catch { exception ->
        emit(ErrorState(exception))
    }
    .collect { data ->
        updateUI(data)
    }
```

### Best Practices

1. Use CEH for unexpected exceptions and centralized logging:

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    if (exception !is CancellationException) {
        Log.e("App", "Unexpected exception", exception)
        reportToCrashlytics(exception)
    }
}
```

1. Combine CEH with explicit handling for expected errors:

```kotlin
launch(handler) {
    try {
        val data = api.fetchData()
        updateUI(data)
    } catch (e: NetworkException) {
        showNetworkError()
    }
    // CEH logs truly unexpected exceptions
}
```

1. Use `SupervisorJob` with CEH for independent children:

```kotlin
val scope = CoroutineScope(
    SupervisorJob() + Dispatchers.Main + handler
)
```

1. Name coroutines for debugging:

```kotlin
launch(handler + CoroutineName("FetchUser")) {
    // Exception reports include coroutine name
}
```

1. Do not rely solely on CEH:

```kotlin
// BAD: relying only on CEH
launch(handler) {
    val data = api.fetchData()
    updateUI(data)
}

// BETTER: explicit handling + CEH as backup
launch(handler) {
    try {
        val data = api.fetchData()
        updateUI(data)
    } catch (e: ApiException) {
        showError(e)
    }
}
```

### Testing CEH

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class CEHTest {
    @Test
    fun `CEH catches launch exceptions`() = runTest {
        var caughtException: Throwable? = null

        val handler = CoroutineExceptionHandler { _, exception ->
            caughtException = exception
        }

        val job = launch(handler) {
            throw RuntimeException("Test exception")
        }

        job.join()

        assertTrue(caughtException is RuntimeException)
        assertEquals("Test exception", caughtException?.message)
    }

    @Test
    fun `CEH does not handle async exceptions consumed via await`() = runTest {
        var caughtByHandler = false

        val handler = CoroutineExceptionHandler { _, _ ->
            caughtByHandler = true
        }

        val deferred = async(handler) {
            throw RuntimeException("Test exception")
        }

        var caughtByTryCatch = false
        try {
            deferred.await()
        } catch (e: Exception) {
            caughtByTryCatch = true
        }

        assertTrue(caughtByTryCatch)
        assertTrue(!caughtByHandler)
    }

    @Test
    fun `CEH in supervisorScope children`() = runTest {
        val exceptions = mutableListOf<Throwable>()

        val handler = CoroutineExceptionHandler { _, exception ->
            exceptions.add(exception)
        }

        supervisorScope {
            launch(handler) {
                throw RuntimeException("Child 1")
            }

            launch(handler) {
                throw RuntimeException("Child 2")
            }
        }

        assertEquals(2, exceptions.size)
    }
}
```

### Common Mistakes

Mistake 1: Assuming CEH replaces structured exception handling.

```kotlin
// WRONG: relying only on CEH, no local handling
launch(handler) {
    val data = api.fetchData()
    updateUI(data)
}
```

Mistake 2: Expecting CEH to handle async exceptions consumed via await.

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Not called for await-consumed exceptions: $exception")
}

async(handler) {
    throw RuntimeException("Exception")
}.await() // Handled by await/try-catch, not CEH
```

Mistake 3: Forgetting to attach CEH (or any logging) on long-lived application scopes.

```kotlin
// No CEH: uncaught exceptions go only to default handler, harder to debug
val appScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
```

### Key Takeaways

1. CEH is a last-resort handler for uncaught exceptions.
2. It reliably applies to root `launch`/`actor` coroutines; nested children propagate to the nearest CEH in their parent chain.
3. It does not replace error handling for `async`/`await`; handle those via `await()`.
4. Install CEH on `CoroutineScope` or top-level launches to centralize logging.
5. Combine with `SupervisorJob` to isolate failures while still logging them.
6. Use `CoroutineName` and CEH together to improve diagnostics.
7. Use CEH to feed logging/analytics/crash reporting, not to hide expected errors.

---

## Follow-ups

1. How does `CoroutineExceptionHandler` interact with structured concurrency and parent/child coroutine hierarchies?
2. In which scenarios would you prefer `CoroutineExceptionHandler` over local try-catch inside coroutines?
3. How do you correctly test that `CoroutineExceptionHandler` is invoked for uncaught exceptions?
4. What are the pitfalls of relying on `CoroutineExceptionHandler` with `async`/`await`?
5. How would you structure a global coroutine scope and CEH in an Android app for logging and crash reporting?

## References

- [Kotlin Coroutines Exception Handling](https://kotlinlang.org/docs/exception-handling.html)
- [CoroutineExceptionHandler Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-exception-handler/)
- [Exceptions in Coroutines](https://medium.com/androiddevelopers/exceptions-in-coroutines-ce8da1ec060c)

## Related Questions

- [[q-common-coroutine-mistakes--kotlin--medium|Common Kotlin coroutines mistakes]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging Kotlin coroutines]]
- [[q-suspend-cancellable-coroutine--kotlin--hard|Converting callbacks with suspendCancellableCoroutine]]
