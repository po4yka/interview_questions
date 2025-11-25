---
id: lang-090
title: "What Is CoroutineScope / Что такое CoroutineScope"
aliases: [What Is CoroutineScope, Что такое CoroutineScope]
topic: kotlin
subtopics: [coroutines, lifecycle, scope-management]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-hot-vs-cold-flows--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [coroutines, difficulty/medium, kotlin, scope]
date created: Saturday, November 1st 2025, 1:01:34 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---

# Вопрос (RU)
> Что такое CoroutineScope?

---

# Question (EN)
> What is CoroutineScope?

## Ответ (RU)

`CoroutineScope` — это контекст (scope), в котором выполняются корутины в Kotlin. Он задает их жизненный цикл, обеспечивает структурированную конкуррентность и позволяет отменять все дочерние корутины при отмене или завершении scope.

Распространенные scope:
- `GlobalScope` — живет всё время работы процесса, но в прикладном коде почти не рекомендуется (сложно контролировать, риск утечек и нарушений структурированной конкуррентности).
- `viewModelScope` — в `ViewModel` (Android), все корутины отменяются при уничтожении `ViewModel`.
- `lifecycleScope` — в `Activity`/`Fragment` (Android), все корутины отменяются при уничтожении соответствующего владельца жизненного цикла.

### Базовая Концепция

```kotlin
import kotlinx.coroutines.*

// CoroutineScope определяет, где запускаются корутины и каков их жизненный цикл
fun main() = runBlocking {  // Создает scope и блокирует текущий поток
    // Все корутины в этом scope являются дочерними для runBlocking
    launch {
        println("Coroutine 1")
    }

    launch {
        println("Coroutine 2")
    }

    // runBlocking ждет завершения всех дочерних корутин
    // Если scope будет отменен раньше, все дочерние корутины будут отменены
}
```

### Создание Пользовательского Scope

```kotlin
import kotlinx.coroutines.*

// Пользовательский scope с заданным жизненным циклом
class MyManager {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Default
    )

    fun startWork() {
        scope.launch {
            // Работа привязана к жизненному циклу scope
            performTask()
        }
    }

    fun cleanup() {
        scope.cancel()  // Отменяет все корутины в этом scope
    }
}
```

### Распространенные Scope

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.lifecycleScope
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*

// 1. GlobalScope — время жизни процесса
GlobalScope.launch(Dispatchers.Default) {
    // Выполняется независимо от структурированного родительского scope
    // ВАЖНО: использовать с большой осторожностью — сложно управлять, может пережить компоненты
}

// 2. viewModelScope (Android)
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // Отменяется при очистке ViewModel
            val data = repository.fetchData()
            _uiState.value = data
        }
    }
}

// 3. lifecycleScope (Android)
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Отменяется при уничтожении Activity
            collectData()
        }
    }
}

// 4. coroutineScope builder
suspend fun performTask() = coroutineScope {
    // Создает дочерний scope для структурированной конкуррентности
    launch { subtask1() }
    launch { subtask2() }
    // Возвращает управление только после завершения всех детей или отмены scope
}
```

### Иерархия Scope

```kotlin
import kotlinx.coroutines.*

fun scopeHierarchy() = runBlocking {  // Родительский scope
    launch {  // Дочерний 1 (Job — потомок runBlocking)
        println("Child 1")
        launch {  // Внук runBlocking, дочерний для этого launch
            println("Grandchild 1")
        }
    }

    launch {  // Дочерний 2
        println("Child 2")
    }

    // При отмене родительского scope (runBlocking)
    // отменяются все его дочерние и их потомки
}
```

### Структурированная Конкуррентность

```kotlin
import kotlinx.coroutines.*

// Все дочерние корутины должны завершиться до возврата из coroutineScope
suspend fun structuredConcurrency() = coroutineScope {
    val job1 = launch {
        delay(1000)
        println("Task 1 done")
    }

    val job2 = launch {
        delay(2000)
        println("Task 2 done")
    }

    // Явно ждем дочерние задачи для наглядности
    job1.join()
    job2.join()

    println("All tasks completed")  // Выведется после завершения обеих задач
}
```

### Практические Примеры

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.lifecycleScope
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Android ViewModel
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val userList = userRepository.getUsers()
                _users.value = userList
            } catch (e: Exception) {
                // Обработка ошибки
            }
        }
        // Автоматически отменяется при очистке ViewModel
    }
}

// Android Fragment
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            // Привязан к жизненному циклу view во Fragment
            viewModel.users.collect { users ->
                updateUI(users)
            }
        }
        // Автоматически отменяется, когда жизненный цикл view уничтожен
    }
}

// Пользовательский Service
class DataSyncService : Service() {
    private val serviceScope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO
    )

    fun startSync() {
        serviceScope.launch {
            while (isActive) {
                syncData()
                delay(60_000)  // Синхронизация каждую минуту
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()  // Очистка
    }
}
```

### Отмена Scope

```kotlin
import kotlinx.coroutines.*

fun scopeCancellation() = runBlocking {
    val job = launch {
        repeat(5) { i ->
            println("Job $i")
            delay(500)
        }
    }

    delay(1200)
    job.cancel()  // Отмена конкретной корутины
    println("Job cancelled")
}

// Отмена всего scope
fun cancelScope() {
    val scope = CoroutineScope(Dispatchers.Default + Job())

    scope.launch { task1() }
    scope.launch { task2() }
    scope.launch { task3() }

    // Позже...
    scope.cancel()  // Отменяет все корутины, запущенные в этом scope
}
```

### Обработка Исключений В Scope

```kotlin
import kotlinx.coroutines.*

// SupervisorJob: сбой одного ребенка не отменяет остальных
val supervisorScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

supervisorScope.launch {
    launch {
        throw Exception("Child 1 failed")  // Падает только этот ребенок
    }

    launch {
        delay(1000)
        println("Child 2 still running")  // Продолжает работать
    }
}

// Обычный Job: необработанное исключение отменяет сиблингов и scope
val regularScope = CoroutineScope(Job() + Dispatchers.Default)

regularScope.launch {
    launch {
        throw Exception("Child 1 failed")  // Приводит к отмене родительского scope
    }

    launch {
        try {
            delay(1000)
            println("Child 2")
        } catch (e: CancellationException) {
            println("Child 2 cancelled")  // Будет отменен
        }
    }
}
```

### Рекомендации (Best Practices)

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.*

class ScopeBestPractices {
    // ДЕЛАЙТЕ: используйте scope, привязанный к жизненному циклу
    class GoodViewModel : ViewModel() {
        fun loadData() {
            viewModelScope.launch {  // Привязан к жизненному циклу ViewModel
                fetchData()
            }
        }
    }

    // НЕ ДЕЛАЙТЕ: не используйте GlobalScope для работы компонента
    class BadViewModel : ViewModel() {
        fun loadData() {
            GlobalScope.launch(Dispatchers.IO) {  // Может пережить ViewModel и привести к утечкам
                fetchData()
            }
        }
    }

    // ДЕЛАЙТЕ: создавайте пользовательский scope с корректным dispatcher и очисткой
    class GoodManager {
        private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

        fun start() {
            scope.launch { work() }
        }

        fun cleanup() {
            scope.cancel()  // Освобождение ресурсов
        }
    }

    // НЕ ДЕЛАЙТЕ: не создавайте scope без механизма очистки
    class BadManager {
        private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

        fun start() {
            scope.launch { work() }
        }
        // Нет cleanup — риск утечек
    }
}
```

### Контекст Scope

```kotlin
import kotlinx.coroutines.*

// Scope с конкретным контекстом
val ioScope = CoroutineScope(Dispatchers.IO + Job())

ioScope.launch {
    // Выполняется на IO dispatcher
    performIOOperation()
}

// Scope с обработчиком исключений
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught $exception")
}

val scopeWithHandler = CoroutineScope(
    Dispatchers.Default + SupervisorJob() + handler
)

scopeWithHandler.launch {
    throw Exception("Error")  // Обрабатывается handler для корневой корутины
}
```

### Тестирование С Использованием Scope

```kotlin
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

class MyRepositoryTest {
    @Test
    fun testDataFetch() = runTest {  // Тестовый scope
        val repository = MyRepository()

        val result = repository.fetchData()

        assertEquals(expected, result)
    }
}
```

### Резюме

`CoroutineScope`:
- Определяет жизненный цикл корутин и их контекст.
- Обеспечивает структурированную конкуррентность.
- Позволяет автоматически отменять дочерние корутины при отмене scope.
- Помогает избежать утечек, когда scope привязан к жизненному циклу компонента.
- Управляет отношениями родитель–потомок между задачами.

Ключевые моменты:
- Привязывайте scopes к жизненному циклу компонентов (`ViewModel`, `Activity`, сервисы, менеджеры и т.д.).
- Используйте `viewModelScope` во `ViewModel`.
- Используйте `lifecycleScope` в `Activity`/`Fragment` (и `viewLifecycleOwner.lifecycleScope` для `Fragment`-view).
- Избегайте `GlobalScope`, если нет очень веской причины.
- Не забывайте вызывать `cancel()` у пользовательских scopes в `onCleared`/`onDestroy`/cleanup.

## Answer (EN)

CoroutineScope is the context (scope) in which coroutines execute in Kotlin. It defines their lifecycle, provides structured concurrency, and allows cancelling all child coroutines when the scope is cancelled or completes.

Common scopes:
- `GlobalScope`: Lives for the whole process lifetime; generally discouraged in application code (hard to control, leaks/structured concurrency issues).
- `viewModelScope`: In `ViewModel` (Android), cancelled when the `ViewModel` is cleared.
- `lifecycleScope`: In `Activity`/`Fragment` (Android), cancelled when the corresponding lifecycle owner is destroyed.

[[c-kotlin]] [[c-coroutines]]

### Basic Concept

```kotlin
import kotlinx.coroutines.*

// CoroutineScope defines where coroutines run and their lifecycle
fun main() = runBlocking {  // Creates a scope and blocks the current thread
    // All coroutines in this scope are children of runBlocking
    launch {
        println("Coroutine 1")
    }

    launch {
        println("Coroutine 2")
    }

    // runBlocking waits until all its child coroutines complete
    // If the scope were cancelled earlier, all running children would be cancelled
}
```

### Creating Custom Scope

```kotlin
import kotlinx.coroutines.*

// Custom scope with specific lifecycle
class MyManager {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Default
    )

    fun startWork() {
        scope.launch {
            // Work is tied to scope lifecycle
            performTask()
        }
    }

    fun cleanup() {
        scope.cancel()  // Cancels all coroutines in this scope
    }
}
```

### Common Scopes

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.lifecycleScope
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*

// 1. GlobalScope - process lifetime
GlobalScope.launch(Dispatchers.Default) {
    // Runs independently of any structured parent scope
    // WARNING: Use with great caution - hard to manage, can outlive components
}

// 2. viewModelScope (Android)
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // Cancelled when ViewModel is cleared
            val data = repository.fetchData()
            _uiState.value = data
        }
    }
}

// 3. lifecycleScope (Android)
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Cancelled when Activity is destroyed
            collectData()
        }
    }
}

// 4. coroutineScope builder
suspend fun performTask() = coroutineScope {
    // Creates a child scope for structured concurrency
    launch { subtask1() }
    launch { subtask2() }
    // Returns only after all children complete or the scope is cancelled
}
```

### Scope Hierarchy

```kotlin
import kotlinx.coroutines.*

fun scopeHierarchy() = runBlocking {  // Parent scope
    launch {  // Child 1 (Job is a child of runBlocking)
        println("Child 1")
        launch {  // Grandchild of runBlocking, child of this launch
            println("Grandchild 1")
        }
    }

    launch {  // Child 2
        println("Child 2")
    }

    // If the parent scope (runBlocking) is cancelled,
    // all its running children and their descendants are cancelled
}
```

### Structured Concurrency

```kotlin
import kotlinx.coroutines.*

// All children must complete before coroutineScope returns
suspend fun structuredConcurrency() = coroutineScope {
    val job1 = launch {
        delay(1000)
        println("Task 1 done")
    }

    val job2 = launch {
        delay(2000)
        println("Task 2 done")
    }

    // Explicitly wait for children for clarity in examples
    job1.join()
    job2.join()

    println("All tasks completed")  // Printed after both tasks are done
}
```

### Real-World Examples

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.lifecycleScope
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Android ViewModel
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val userList = userRepository.getUsers()
                _users.value = userList
            } catch (e: Exception) {
                // Handle error
            }
        }
        // Automatically cancelled when ViewModel is cleared
    }
}

// Android Fragment
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            // Tied to the Fragment view lifecycle
            viewModel.users.collect { users ->
                updateUI(users)
            }
        }
        // Automatically cancelled when the view lifecycle is destroyed
    }
}

// Custom Service
class DataSyncService : Service() {
    private val serviceScope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO
    )

    fun startSync() {
        serviceScope.launch {
            while (isActive) {
                syncData()
                delay(60_000)  // Sync every minute
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()  // Clean up
    }
}
```

### Scope Cancellation

```kotlin
import kotlinx.coroutines.*

fun scopeCancellation() = runBlocking {
    val job = launch {
        repeat(5) { i ->
            println("Job $i")
            delay(500)
        }
    }

    delay(1200)
    job.cancel()  // Cancel specific job
    println("Job cancelled")
}

// Cancel entire scope
fun cancelScope() {
    val scope = CoroutineScope(Dispatchers.Default + Job())

    scope.launch { task1() }
    scope.launch { task2() }
    scope.launch { task3() }

    // Later...
    scope.cancel()  // Cancels all coroutines launched in this scope
}
```

### Exception Handling in Scope

```kotlin
import kotlinx.coroutines.*

// SupervisorJob: children failures don't cancel siblings
val supervisorScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

supervisorScope.launch {
    launch {
        throw Exception("Child 1 failed")  // Only this child fails
    }

    launch {
        delay(1000)
        println("Child 2 still running")  // Continues to run
    }
}

// Regular Job: an unhandled child failure cancels siblings and the scope
val regularScope = CoroutineScope(Job() + Dispatchers.Default)

regularScope.launch {
    launch {
        throw Exception("Child 1 failed")  // Fails and cancels the parent scope
    }

    launch {
        try {
            delay(1000)
            println("Child 2")
        } catch (e: CancellationException) {
            println("Child 2 cancelled")  // Will be cancelled
        }
    }
}
```

### Best Practices

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.*

class ScopeBestPractices {
    // DO: Use lifecycle-aware scopes in Android
    class GoodViewModel : ViewModel() {
        fun loadData() {
            viewModelScope.launch {  // Tied to ViewModel lifecycle
                fetchData()
            }
        }
    }

    // DON'T: Use GlobalScope in Android for component work
    class BadViewModel : ViewModel() {
        fun loadData() {
            GlobalScope.launch(Dispatchers.IO) {  // May outlive ViewModel and leak
                fetchData()
            }
        }
    }

    // DO: Create a custom scope with proper dispatcher and cleanup
    class GoodManager {
        private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

        fun start() {
            scope.launch { work() }
        }

        fun cleanup() {
            scope.cancel()  // Clean up resources
        }
    }

    // DON'T: Create a scope without cleanup mechanism
    class BadManager {
        private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

        fun start() {
            scope.launch { work() }
        }
        // No cleanup - potential leak
    }
}
```

### Scope Context

```kotlin
import kotlinx.coroutines.*

// Scope with specific context
val ioScope = CoroutineScope(Dispatchers.IO + Job())

ioScope.launch {
    // Runs on IO dispatcher
    performIOOperation()
}

// Scope with exception handler
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught $exception")
}

val scopeWithHandler = CoroutineScope(
    Dispatchers.Default + SupervisorJob() + handler
)

scopeWithHandler.launch {
    throw Exception("Error")  // Caught by handler (for this root coroutine)
}
```

### Testing with Scopes

```kotlin
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

class MyRepositoryTest {
    @Test
    fun testDataFetch() = runTest {  // Test scope
        val repository = MyRepository()

        val result = repository.fetchData()

        assertEquals(expected, result)
    }
}
```

### Summary

CoroutineScope:
- Defines coroutine lifecycle and context.
- Enables structured concurrency.
- Provides automatic child cancellation when the scope is cancelled.
- Helps prevent leaks when tied to component lifecycle.
- Manages parent-child relationships between coroutines.

Key Points:
- Always tie scopes to component lifecycle (`ViewModel`, `Activity`, services, managers, etc.).
- Use `viewModelScope` in `ViewModel`s.
- Use `lifecycleScope` in `Activity`/`Fragment` (and `viewLifecycleOwner.lifecycleScope` for Fragment views).
- Avoid `GlobalScope` unless absolutely necessary.
- Cancel custom scopes appropriately in `onCleared`/`onDestroy`/cleanup.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия корутинного подхода от Java-потоков?
- Когда на практике стоит использовать `CoroutineScope` и какие scopes выбирать?
- Какие распространенные ошибки при работе с `CoroutineScope` стоит избегать?

## Follow-ups

- What are the key differences between this and Java threads?
- When would you use `CoroutineScope` in practice, and which scopes would you choose?
- What are common pitfalls to avoid when working with `CoroutineScope`?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-hot-vs-cold-flows--programming-languages--medium]]

## Related Questions

- [[q-hot-vs-cold-flows--programming-languages--medium]]
