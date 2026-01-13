---
anki_cards:
- slug: q-structured-concurrency-violations--kotlin--hard-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-structured-concurrency-violations--kotlin--hard-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-086
title: "Structured concurrency violations and escape hatches / Нарушения структурной конкурентности"
aliases: [Anti-Patterns, Escape Hatches, Structured Concurrency Violations, Нарушения конкурентности]
topic: kotlin
subtopics: [coroutines, structured-concurrency]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-structured-concurrency, q-kotlin-advantages-for-android--kotlin--easy]
created: 2025-10-12
updated: 2025-11-09
tags: [anti-patterns, architecture, best-practices, coroutines, difficulty/hard, kotlin, lifecycle, scope, structured-concurrency, violations]

---\
# Вопрос (RU)

> Нарушения структурной конкурентности в корутинах Kotlin: какие типичные анти-паттерны (GlobalScope, неуправляемые Job/CoroutineScope, утечки через архитектурные границы и т.п.), почему они опасны, и какие допустимые escape hatches существуют для работы вне строгой структуры?

# Question (EN)

> Structured concurrency violations in Kotlin coroutines: what are the typical anti-patterns (GlobalScope, unmanaged Job/CoroutineScope, leaks across architectural boundaries, etc.), why are they dangerous, and what legitimate escape hatches exist for working outside strict structure?

## Ответ (RU)

### Обзор

Структурная конкурентность — это основной принцип корутин Kotlin (см. также [[c-kotlin]] и [[c-structured-concurrency]]), который обеспечивает организацию корутин в иерархию с автоматической отменой, распространением исключений и гарантиями завершения. Нарушения структурной конкурентности могут приводить к утечкам памяти, утечкам ресурсов, необработанным исключениям и трудно отлаживаемым проблемам конкурентности.

Это руководство рассматривает:
- что такое структурная конкурентность;
- распространённые нарушения (GlobalScope, неуправляемые `Job`, фабричные `CoroutineScope`, утечки через архитектурные границы);
- когда нарушение правил допустимо (редко);
- легитимные escape hatches с явным временем жизни;
- способы обнаружения нарушений и тестирования структурной конкурентности.

### Что Такое Структурная Конкурентность

**Структурная конкурентность** — это парадигма, где:
1. Каждая корутина принадлежит некоторому `CoroutineScope`.
2. Дочерние корутины связаны с родительскими корутинами.
3. Родитель ждёт завершения всех дочерних корутин.
4. Отмена распространяется от родителя к детям.
5. Исключения распространяются от детей к родителю.
6. Ни одна корутина не переживает свой scope (за исключением явно выделенных корутин с документированным временем жизни, см. escape hatches ниже).

#### Основной Принцип

```text
Scope
   Родительская корутина
      Дочерняя корутина 1
         Внучатая 1.1
         Внучатая 1.2
      Дочерняя корутина 2
          Внучатая 2.1
   Все завершаются вместе
```

#### Пример: Структурированная Vs Неструктурированная

```kotlin
import kotlinx.coroutines.*

fun demonstrateStructuredRu() = runBlocking {
    println("=== Структурная конкурентность ===")

    // СТРУКТУРИРОВАННО: родитель ждёт детей
    coroutineScope {
        launch {
            delay(1000)
            println("Дочерняя 1 завершена")
        }

        launch {
            delay(500)
            println("Дочерняя 2 завершена")
        }

        println("Тело родителя завершено, ждём детей...")
    }

    println("Вся работа завершена\n")

    // НЕСТРУКТУРИРОВАННО: fire-and-forget
    println("=== Неструктурированная (нарушение) ===")

    GlobalScope.launch {
        delay(1000)
        println("Это может никогда не выполниться!")
    }

    println("Функция завершается немедленно")
    // Корутина GlobalScope может быть заброшена!
}
```

**Вывод:**
```text
=== Структурная конкурентность ===
Тело родителя завершено, ждём детей...
Дочерняя 2 завершена
Дочерняя 1 завершена
Вся работа завершена

=== Неструктурированная (нарушение) ===
Функция завершается немедленно
(Корутина GlobalScope может никогда не завершиться)
```

### Преимущества Структурной Конкурентности

#### 1. Автоматическая Отмена

```kotlin
import kotlinx.coroutines.*

class AutomaticCancellationDemo {
    suspend fun structuredWork() = coroutineScope {
        launch {
            repeat(10) {
                delay(100)
                println("Работаем... $it")
            }
        }

        launch {
            delay(300)
            throw Exception("Что-то пошло не так!")
        }
        // При исключении во второй корутине первая будет автоматически отменена
    }

    fun demonstrateBenefit() = runBlocking {
        try {
            structuredWork()
        } catch (e: Exception) {
            println("Поймано: ${e.message}")
            println("Все корутины были автоматически отменены")
        }
    }
}
```

#### 2. Распространение Исключений

```kotlin
import kotlinx.coroutines.*

class ExceptionPropagationDemo {
    suspend fun structuredWorkWithException() = coroutineScope {
        val deferred1 = async {
            delay(500)
            "Результат 1"
        }

        val deferred2 = async {
            delay(100)
            throw IllegalStateException("Deferred 2 провалился")
        }

        // Исключение распространяется в родительский scope
        val r1 = deferred1.await() // Не выполнится
        val r2 = deferred2.await() // Бросит

        "Никогда не вернётся"
    }

    fun demonstrate() = runBlocking {
        try {
            structuredWorkWithException()
        } catch (e: IllegalStateException) {
            println("Исключение корректно распространено: ${e.message}")
        }
    }
}
```

#### 3. Гарантии Завершения

```kotlin
import kotlinx.coroutines.*

class CompletionGuaranteesDemo {
    suspend fun structuredWorkWithGuarantees() = coroutineScope {
        launch {
            try {
                repeat(10) {
                    delay(100)
                    println("Обработка $it")
                }
            } finally {
                println("Выполнен cleanup")
            }
        }

        delay(300)
        println("Родитель завершает работу")
        // Родитель дождётся дочерней корутины, включая finally
    }

    fun demonstrate() = runBlocking {
        structuredWorkWithGuarantees()
        println("Всё завершено, включая очистку ресурсов")
    }
}
```

#### 4. Управление Ресурсами

```kotlin
import kotlinx.coroutines.*
import java.io.Closeable

class ResourceManagementDemo {
    class Resource : Closeable {
        init { println("Ресурс открыт") }
        override fun close() { println("Ресурс закрыт") }
    }

    suspend fun structuredResourceManagement() = coroutineScope {
        val resource = Resource()
        try {
            launch {
                delay(500)
                println("Используем ресурс")
            }

            launch {
                delay(300)
                throw Exception("Ошибка")
            }
        } finally {
            resource.close() // Гарантированно вызовется
        }
    }

    fun demonstrate() = runBlocking {
        try {
            structuredResourceManagement()
        } catch (e: Exception) {
            println("Исключение поймано, ресурс закрыт")
        }
    }
}
```

### Нарушение #1: GlobalScope (худший вариант)

**Почему это плохо:**
- Нет родительского scope.
- Не отменяется автоматически.
- Нет распространения исключений.
- Нет гарантий завершения.
- Риск утечек памяти и логики.

#### Проблема

```kotlin
import kotlinx.coroutines.*

class GlobalScopeViolation {
    fun processData() {
        // НАРУШЕНИЕ: неструктурированная корутина
        GlobalScope.launch {
            val data = loadData()
            process(data)
            saveResults()
        }
        // Функция возвращается сразу, корутина может жить дольше "владельца"
    }

    private suspend fun loadData(): String {
        delay(1000)
        return "data"
    }

    private fun process(data: String) {
        println("Обработка: $data")
    }

    private fun saveResults() {
        println("Сохранение результатов")
    }
}
```

#### Почему Это Нарушает Структурную Конкурентность

```kotlin
import kotlinx.coroutines.*

fun demonstrateGlobalScopeProblemsRu() = runBlocking {
    println("=== Проблемы GlobalScope ===")

    class Component {
        fun start() {
            println("Компонент запущен")

            // ПРОБЛЕМА 1: нет родителя
            GlobalScope.launch {
                delay(2000)
                println("У этой корутины нет родителя, который мог бы её отменить")
            }
        }

        fun stop() {
            println("Компонент остановлен")
            // ПРОБЛЕМА 2: корутина не отменена и продолжает работу в фоне
        }
    }

    val component = Component()
    component.start()

    delay(500)
    component.stop()

    // Компонент остановлен, но корутина всё ещё выполняется
    delay(2000)
    println("Корутина выполнилась даже после остановки компонента!")
}
```

**Вывод:**
```text
=== Проблемы GlobalScope ===
Компонент запущен
Компонент остановлен
У этой корутины нет родителя, который мог бы её отменить
Корутина выполнилась даже после остановки компонента!
```

#### Исправление

```kotlin
import kotlinx.coroutines.*

class StructuredComponentRu2 {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    fun start() {
        println("Компонент запущен")

        // ХОРОШО: структурированная корутина в управляемом scope
        scope.launch {
            delay(2000)
            println("Эта корутина будет корректно отменена")
        }
    }

    fun stop() {
        println("Компонент остановлен")
        scope.cancel()
        // Все корутины отменены!
    }
}

fun demonstrateStructuredFixRu() = runBlocking {
    val component = StructuredComponentRu2()
    component.start()

    delay(500)
    component.stop()

    delay(2000)
    println("Корутина была корректно отменена")
}
```

### Нарушение #2: Создание Job() Без Жизненного Цикла

```kotlin
import kotlinx.coroutines.*

class UnmanagedJobViolationRu {
    // НАРУШЕНИЕ: Scope создан, но нигде не отменяется
    private val customScope = CoroutineScope(Job() + Dispatchers.Main)

    fun doWork() {
        customScope.launch {
            repeat(100) {
                delay(100)
                println("Работа $it")
            }
        }
    }
    // ОТСУТСТВУЕТ: fun cleanup() { customScope.cancel() }
}
```

**Почему это нарушение:**
1. Нет явного конца жизненного цикла.
2. Нет отмены — возможны "вечные" задачи.
3. Держит ссылки → утечки памяти.
4. Нет родителя — нельзя отменить извне.

#### Исправление: Явный Жизненный Цикл

```kotlin
import kotlinx.coroutines.*

class ManagedJobComponentRu {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun doWork() {
        scope.launch {
            repeat(100) {
                delay(100)
                println("Работа $it")
            }
        }
    }

    fun cleanup() {
        // ЯВНОЕ управление временем жизни
        scope.cancel()
        println("Все корутины отменены")
    }
}

fun demonstrateExplicitLifecycleRu() = runBlocking {
    val component = ManagedJobComponentRu()

    component.doWork()
    delay(500)

    component.cleanup()
    println("Компонент очищен")
}
```

### Нарушение #3: CoroutineScope() Как Фабрика Без Жизненного Цикла

```kotlin
import kotlinx.coroutines.*

class FactoryScopeViolationRu {
    fun processItems(items: List<String>) {
        // НАРУШЕНИЕ: создаётся scope без связи с жизненным циклом владельца
        CoroutineScope(Dispatchers.Default).launch {
            items.forEach { item ->
                delay(1000)
                println("Обработка: $item")
            }
        }
        // Ссылка на scope теряется сразу, отменить нельзя
    }
}
```

#### Почему Это Проблемно

```kotlin
import kotlinx.coroutines.*

fun demonstrateFactoryProblemRu() = runBlocking {
    println("=== Проблема фабричного CoroutineScope() ===")

    fun processData() {
        CoroutineScope(Dispatchers.Default).launch {
            repeat(5) {
                delay(500)
                println("Обработка $it")
            }
        }

        println("Функция вернулась")
        // Ссылка на scope потеряна, отменить нельзя.
    }

    processData()

    delay(1000)
    println("Хотим отменить, но не можем — нет ссылки на scope!")

    delay(3000)
    println("Корутина завершилась сама по себе")
}
```

#### Исправление: Принимать Scope Параметром

```kotlin
import kotlinx.coroutines.*

class FactoryScopeFixRu {
    // Принимаем управляющий scope извне
    fun processItems(scope: CoroutineScope, items: List<String>) {
        scope.launch {
            items.forEach { item ->
                delay(1000)
                println("Обработка: $item")
            }
        }
    }
}

fun demonstrateFactoryFixRu() = runBlocking {
    val scope = CoroutineScope(Job() + Dispatchers.Default)
    val processor = FactoryScopeFixRu()

    processor.processItems(scope, listOf("A", "B", "C"))

    delay(1500)
    println("Отмена...")
    scope.cancel()
    println("Обработка отменена")
}
```

### Нарушение #4: Утечка Корутин Через Архитектурные Границы

```kotlin
import kotlinx.coroutines.*

// НАРУШЕНИЕ: репозиторий сам запускает корутины в GlobalScope
class LeakyRepositoryRu {
    fun loadData(callback: (String) -> Unit) {
        GlobalScope.launch {
            val data = fetchFromNetwork()
            callback(data)
        }
    }

    private suspend fun fetchFromNetwork(): String {
        delay(1000)
        return "Данные из сети"
    }
}

// ViewModel не контролирует работу репозитория
class LeakyViewModelRu {
    private val repository = LeakyRepositoryRu()

    fun loadData() {
        repository.loadData { data ->
            println("Получены данные: $data")
        }
    }

    fun onCleared() {
        // Нет способа отменить корутины репозитория
    }
}
```

#### Почему Это Нарушает Архитектуру

1. Нарушение границ слоёв: репозиторий управляет конкурентностью вместо уровня вызова.
2. Нет отмены: `LeakyViewModelRu` не может остановить работу.
3. Жёсткая связность: поведение репозитория скрыто.
4. Сложно тестировать и контролировать.

#### Исправление: `suspend`-функции И Управление Из Слоя Вызова

```kotlin
import kotlinx.coroutines.*

// Репозиторий только выполняет работу и возвращает результат
class StructuredRepositoryRu {
    suspend fun loadData(): String {
        return withContext(Dispatchers.IO) {
            fetchFromNetwork()
        }
    }

    private suspend fun fetchFromNetwork(): String {
        delay(1000)
        return "Данные из сети"
    }
}

// ViewModel управляет scope
class StructuredViewModelRu {
    private val repository = StructuredRepositoryRu()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun loadData() {
        scope.launch {
            try {
                val data = repository.loadData()
                println("Получены данные: $data")
            } catch (e: CancellationException) {
                println("Отменено")
                throw e
            }
        }
    }

    fun onCleared() {
        scope.cancel()
        // Отмена также прерывает работу репозитория
    }
}
```

### Когда Нарушение Структуры Допустимо (редко)

Некоторые случаи допускают осмысленное нарушение строгой структуры, если:
- время жизни явно определено;
- последствия изолированы;
- решение документировано;
- используется отдельный управляемый `CoroutineScope`.

#### Законный Кейс 1: Фоновая Работа Уровня Приложения

```kotlin
import kotlinx.coroutines.*

class BackgroundSyncManagerRu(
    private val applicationScope: CoroutineScope // Явный scope уровня приложения
) {
    fun startPeriodicSync() {
        // ДОПУСТИМО: работа, живущая всё время жизни процесса
        applicationScope.launch {
            while (isActive) {
                try {
                    performSync()
                    delay(3600_000) // 1 час
                } catch (e: Exception) {
                    // Логируем и пробуем позже
                }
            }
        }
    }

    private suspend fun performSync() {
        // Синхронизация данных с сервером
    }
}

class MyApplicationRu : android.app.Application() {
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onCreate() {
        super.onCreate()
        val syncManager = BackgroundSyncManagerRu(applicationScope)
        syncManager.startPeriodicSync()
    }

    override fun onTerminate() {
        super.onTerminate()
        // В основном полезно в тестах/эмуляторе
        applicationScope.cancel()
    }
}
```

Почему допустимо:
- Явный `applicationScope` с понятной семантикой времени жизни.
- Работа действительно уровня приложения.
- Есть возможность остановки и документированное поведение.

#### Законный Кейс 2: Fire-and-forget Аналитика

```kotlin
import kotlinx.coroutines.*

class AnalyticsTrackerRu(
    private val analyticsScope: CoroutineScope // Выделенный scope для аналитики
) {
    fun trackEvent(event: String) {
        // ДОПУСТИМО: fire-and-forget в изолированном scope
        analyticsScope.launch {
            try {
                sendToAnalyticsServer(event)
            } catch (e: Exception) {
                // Ошибки аналитики не должны падать на пользователя
            }
        }
    }

    private suspend fun sendToAnalyticsServer(event: String) {
        withContext(Dispatchers.IO) {
            // Отправка события
        }
    }
}

fun setupAnalyticsRu(app: android.app.Application): AnalyticsTrackerRu {
    val analyticsScope = CoroutineScope(
        SupervisorJob() +
            Dispatchers.IO +
            CoroutineName("Analytics")
    )
    return AnalyticsTrackerRu(analyticsScope)
}
```

Почему допустимо:
- Некритично для функциональности.
- Fire-and-forget намеренный.
- Выделенный scope с `SupervisorJob`.

#### Законный Кейс 3: Отчёты О Падениях

```kotlin
import kotlinx.coroutines.*

class CrashReporterRu {
    // Допустимо: выделенный scope, переживающий обычную отмену
    private val crashScope = CoroutineScope(
        NonCancellable +
            Dispatchers.IO +
            CoroutineName("CrashReporter")
    )

    fun reportCrash(exception: Throwable) {
        crashScope.launch {
            try {
                sendCrashReport(exception)
            } catch (e: Exception) {
                println("Не удалось отправить отчёт о падении: $e")
            }
        }
    }

    private suspend fun sendCrashReport(exception: Throwable) {
        // Отправка отчёта о падении
    }
}

class MyApplicationCrashRu : android.app.Application() {
    private val crashReporter = CrashReporterRu()

    override fun onCreate() {
        super.onCreate()

        Thread.setDefaultUncaughtExceptionHandler { _, exception ->
            crashReporter.reportCrash(exception)
            Thread.sleep(1000)
            kotlin.system.exitProcess(1)
        }
    }
}
```

Почему допустимо:
- Критическая логика последнего шанса.
- Явно используется `NonCancellable`.
- Короткоживущая, целенаправленная операция.

### Паттерны Escape Hatch

#### Паттерн 1: Явный Scope Уровня Приложения

```kotlin
import kotlinx.coroutines.*

class ApplicationScopeProviderRu {
    val applicationScope = CoroutineScope(
        SupervisorJob() +
            Dispatchers.Default +
            CoroutineName("Application")
    )

    fun shutdown() {
        applicationScope.cancel()
    }
}

class LongRunningServiceRu(
    private val applicationScope: CoroutineScope
) {
    fun startBackgroundWork() {
        applicationScope.launch {
            while (isActive) {
                doWork()
                delay(60_000)
            }
        }
    }

    private suspend fun doWork() {
        // Работа, которая должна переживать UI
    }
}
```

#### Паттерн 2: supervisorScope Для Независимых Задач

```kotlin
import kotlinx.coroutines.*

class IndependentTaskRunnerRu {
    suspend fun runIndependentTasks() = supervisorScope {
        val task1 = launch {
            try {
                performTask1()
            } catch (e: Exception) {
                // Обработка ошибки задачи 1
            }
        }

        val task2 = launch {
            try {
                performTask2()
            } catch (e: Exception) {
                // Обработка ошибки задачи 2
            }
        }

        task1.join()
        task2.join()
    }

    private suspend fun performTask1() {
        delay(1000)
    }

    private suspend fun performTask2() {
        delay(500)
        throw Exception("Задача 2 упала")
    }
}

fun demonstrateSupervisorScopeRu() = runBlocking {
    val runner = IndependentTaskRunnerRu()
    runCatching { runner.runIndependentTasks() }
    println("Обе задачи завершены независимо")
}
```

#### Паттерн 3: Отделённая Корутина (использовать Крайне осторожно)

```kotlin
import kotlinx.coroutines.*

class DetachedCoroutinePatternRu {
    fun performDetachedWork(work: suspend () -> Unit) {
        // ESCAPE HATCH: логически отделённая корутина с собственным Job.
        // Важно: такой подход осознанно нарушает структурную конкурентность.
        CoroutineScope(Job() + Dispatchers.Default).launch {
            work()
        }
    }
}

fun demonstrateDetachedRu() = runBlocking {
    val pattern = DetachedCoroutinePatternRu()

    pattern.performDetachedWork {
        repeat(10) {
            delay(100)
            println("Отделённая работа $it")
        }
    }

    println("Родительский runBlocking завершён, отделённая работа может продолжаться")
    delay(1000)
}
```

### Реальные Примеры

#### Пример 1: Фоновая Синхронизация Данных

```kotlin
import kotlinx.coroutines.*

class DataSyncManagerRu(
    private val applicationScope: CoroutineScope
) {
    private var syncJob: Job? = null

    fun startSync() {
        syncJob?.cancel()
        syncJob = applicationScope.launch {
            while (isActive) {
                try {
                    performSync()
                    delay(3600_000)
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    delay(60_000)
                }
            }
        }
    }

    fun stopSync() {
        syncJob?.cancel()
        syncJob = null
    }

    private suspend fun performSync() {
        withContext(Dispatchers.IO) {
            println("Синхронизация данных...")
            delay(5000)
            println("Синхронизация завершена")
        }
    }
}

fun setupBackgroundSyncRu() {
    val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    val syncManager = DataSyncManagerRu(applicationScope)
    syncManager.startSync()

    Runtime.getRuntime().addShutdownHook(Thread {
        syncManager.stopSync()
        applicationScope.cancel()
    })
}
```

#### Пример 2: SDK Аналитики

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentLinkedQueue

data class AnalyticsEventRu(val name: String, val properties: Map<String, Any>)

class AnalyticsSDK_Ru private constructor() {
    private val analyticsScope = CoroutineScope(
        SupervisorJob() +
            Dispatchers.IO +
            CoroutineName("Analytics") +
            CoroutineExceptionHandler { _, exception ->
                println("Ошибка аналитики: $exception")
            }
    )

    private val eventQueue = ConcurrentLinkedQueue<AnalyticsEventRu>()
    private var flushJob: Job? = null

    fun initialize() {
        startPeriodicFlush()
    }

    fun trackEvent(event: AnalyticsEventRu) {
        eventQueue.offer(event)
    }

    private fun startPeriodicFlush() {
        flushJob = analyticsScope.launch {
            while (isActive) {
                delay(10_000)
                val events = mutableListOf<AnalyticsEventRu>()
                while (eventQueue.isNotEmpty()) {
                    eventQueue.poll()?.let { events.add(it) }
                }
                if (events.isNotEmpty()) {
                    try {
                        flushEvents(events)
                    } catch (e: Exception) {
                        events.forEach { eventQueue.offer(it) }
                    }
                }
            }
        }
    }

    private suspend fun flushEvents(events: List<AnalyticsEventRu>) {
        withContext(Dispatchers.IO) {
            println("Отправка ${events.size} событий аналитики")
        }
    }

    fun shutdown() {
        flushJob?.cancel()
        analyticsScope.cancel()
    }

    companion object {
        val instance = AnalyticsSDK_Ru()
    }
}
```

#### Пример 3: Отчёт О Падениях

```kotlin
import kotlinx.coroutines.*

data class CrashReportRu(
    val exception: String,
    val stackTrace: String,
    val timestamp: Long
)

class CrashReportingSDK_Ru {
    private val crashScope = CoroutineScope(
        NonCancellable +
            Dispatchers.IO +
            CoroutineName("CrashReporter")
    )

    fun reportException(exception: Throwable) {
        crashScope.launch {
            try {
                val report = buildCrashReport(exception)
                sendCrashReport(report)
            } catch (e: Exception) {
                println("Не удалось отправить отчёт о падении: $e")
            }
        }
    }

    private fun buildCrashReport(exception: Throwable): CrashReportRu {
        return CrashReportRu(
            exception = exception.toString(),
            stackTrace = exception.stackTraceToString(),
            timestamp = System.currentTimeMillis()
        )
    }

    private suspend fun sendCrashReport(report: CrashReportRu) {
        withContext(Dispatchers.IO) {
            delay(1000)
            println("Отчёт о падении отправлен: ${report.exception}")
        }
    }
}
```

#### Пример 4: Кэш Уровня Приложения

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

class ApplicationCacheRu(
    private val applicationScope: CoroutineScope
) {
    private val cache = ConcurrentHashMap<String, CacheEntry>()
    private var cleanupJob: Job? = null

    fun initialize() {
        startPeriodicCleanup()
    }

    fun put(key: String, value: Any, ttlMs: Long = 3600_000) {
        cache[key] = CacheEntry(
            value = value,
            expiryTime = System.currentTimeMillis() + ttlMs
        )
    }

    fun get(key: String): Any? {
        val entry = cache[key] ?: return null
        return if (entry.isExpired()) {
            cache.remove(key)
            null
        } else {
            entry.value
        }
    }

    private fun startPeriodicCleanup() {
        cleanupJob = applicationScope.launch {
            while (isActive) {
                delay(60_000)
                val now = System.currentTimeMillis()
                cache.entries.removeIf { (_, entry) ->
                    entry.expiryTime < now
                }
                println("Очистка кэша: осталось ${cache.size} записей")
            }
        }
    }

    fun shutdown() {
        cleanupJob?.cancel()
        cache.clear()
    }

    private data class CacheEntry(
        val value: Any,
        val expiryTime: Long
    ) {
        fun isExpired() = System.currentTimeMillis() > expiryTime
    }
}
```

### Обнаружение Нарушений

#### Инструмент 1: Правило Detekt (упрощённый пример)

```kotlin
// Упрощённое правило Detekt для поиска GlobalScope.
class GlobalScopeUsageRuleRu : Rule() {
    override val issue = Issue(
        id = "GlobalScopeUsage",
        severity = Severity.Warning,
        description = "GlobalScope, как правило, нарушает структурную конкурентность",
        debt = Debt.FIVE_MINS
    )

    override fun visitCallExpression(expression: KtCallExpression) {
        super.visitCallExpression(expression)
        val text = expression.text
        if (text.startsWith("GlobalScope.launch") || text.startsWith("GlobalScope.async")) {
            report(
                CodeSmell(
                    issue = issue,
                    entity = Entity.from(expression),
                    message = "Обнаружен GlobalScope. Предпочитайте структурированный scope."
                )
            )
        }
    }
}
```

#### Инструмент 2: Правило Android Lint (упрощённый пример)

```kotlin
// Упрощённое правило Lint для обнаружения CoroutineScope без явной отмены.
class UncancelledScopeDetectorRu : Detector(), SourceCodeScanner {
    override fun getApplicableMethodNames(): List<String> = listOf("CoroutineScope")

    override fun visitMethodCall(
        context: JavaContext,
        node: UCallExpression,
        method: PsiMethod
    ) {
        val containingClass = node.getContainingClass()
        val hasCancelMethod = containingClass?.methods?.any { it.name == "cancel" } ?: false

        if (!hasCancelMethod) {
            context.report(
                issue = ISSUE,
                location = context.getLocation(node),
                message = "CoroutineScope создан без очевидного механизма отмены (упрощённое правило)"
            )
        }
    }

    companion object {
        val ISSUE: Issue = Issue.create(
            id = "UncancelledCoroutineScope",
            briefDescription = "CoroutineScope без отмены",
            explanation = "Каждый CoroutineScope должен иметь понятную точку отмены.",
            category = Category.CORRECTNESS,
            priority = 8,
            severity = Severity.WARNING,
            implementation = Implementation(
                UncancelledScopeDetectorRu::class.java,
                Scope.JAVA_FILE_SCOPE
            )
        )
    }
}
```

#### Инструмент 3: Чеклист Code Review

```kotlin
/**
 * Чеклист Code Review по структурной конкурентности
 *
 * КРАСНЫЕ ФЛАГИ:
 * - GlobalScope.launch / GlobalScope.async
 * - CoroutineScope(Job()) без явной отмены
 * - Долгоживущие корутины внутри Repository/UseCase
 * - Корутины, запущенные в конструкторах
 * - Scope без понятного жизненного цикла
 *
 * ЗЕЛЁНЫЕ ФЛАГИ:
 * - viewModelScope.launch
 * - lifecycleScope.launch
 * - suspend-функции в Repository/UseCase вместо скрытых корутин
 * - Явное создание + cancel для scope
 * - supervisorScope для независимых задач
 * - Документированные escape hatches
 */
```

### Тестирование Структурной Конкурентности

#### Тест 1: Проверка Отмены И Распространения Исключений

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class StructuredConcurrencyTestRu {
    @Test
    fun testCancellationPropagates() = runTest {
        var child1Cancelled = false
        var child2Cancelled = false

        val scope = CoroutineScope(Job())

        scope.launch {
            try {
                delay(10_000)
            } catch (e: CancellationException) {
                child1Cancelled = true
                throw e
            }
        }

        scope.launch {
            try {
                delay(10_000)
            } catch (e: CancellationException) {
                child2Cancelled = true
                throw e
            }
        }

        advanceTimeBy(100)
        scope.cancel()
        advanceUntilIdle()

        assertTrue(child1Cancelled, "Child 1 должен быть отменён")
        assertTrue(child2Cancelled, "Child 2 должен быть отменён")
    }

    @Test
    fun testExceptionPropagates() = runTest {
        var parentCaught = false

        try {
            coroutineScope {
                launch {
                    delay(100)
                    throw IllegalStateException("Child failed")
                }

                launch {
                    delay(10_000)
                }
            }
        } catch (e: IllegalStateException) {
            parentCaught = true
        }

        assertTrue(parentCaught, "Исключение должно дойти до родителя")
    }
}
```

#### Тест 2: Проверка Отсутствия Утечек Корутин

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class LeakDetectionTestRu {
    @Test
    fun testNoLeakedCoroutines() = runTest {
        val scope = CoroutineScope(Job())

        repeat(10) {
            scope.launch {
                delay(1_000)
            }
        }

        scope.cancel()
        advanceUntilIdle()

        val job = scope.coroutineContext[Job]!!
        assertTrue(job.isCancelled, "Scope должен быть отменён")
        assertTrue(job.children.toList().isEmpty(), "Не должно остаться дочерних задач")
    }
}
```

### Лучшие Практики

1. Отдавайте предпочтение структурной конкурентности:
   ```kotlin
   suspend fun loadDataRu() = coroutineScope {
       val data1 = async { fetchData1() }
       val data2 = async { fetchData2() }
       DataResult(data1.await(), data2.await())
   }
   ```

2. Используйте scope, привязанные к жизненному циклу (в Android — `viewModelScope`, `lifecycleScope`).

3. Репозитории и UseCase предоставляют `suspend`-функции, а не скрыто запускают долгоживущие корутины.

4. Escape hatches реализуются через явные, чётко задокументированные `CoroutineScope` с управляемым временем жизни.

5. Любое отклонение от структурной конкурентности должно быть обосновано в комментариях и покрыто тестами.

6. Регулярно проверяйте код (линтеры, чеклисты) на наличие `GlobalScope`, неотменяемых `CoroutineScope(Job())` и корутин в неправильных слоях.

## Дополнительные Вопросы (RU)

- Как вы рефакторите существующий код с активным использованием `GlobalScope` к структурированной модели?
- Как проектировать API библиотек так, чтобы вызывать код с контролируемым жизненным циклом корутин?
- Как вы будете обеспечивать соблюдение этих правил в большой команде (инструменты, code review, архитектурные гайдлайны)?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-structured-concurrency]]
- Официальная документация по Kotlin Coroutines: раздел "Structured concurrency"

## Связанные Вопросы (RU)

- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-actor-pattern--kotlin--hard]]
- [[q-android-async-primitives--android--easy]]

---

## Answer (EN)

### Overview

Structured concurrency is a core principle of Kotlin coroutines (see also [[c-kotlin]] and [[c-structured-concurrency]]) that ensures coroutines are organized in a hierarchy with automatic cancellation, exception propagation, and completion guarantees. Violations of structured concurrency can lead to memory leaks, resource leaks, unhandled exceptions, and hard-to-debug concurrency issues.

This guide covers:
- what structured concurrency is;
- common violations (GlobalScope, unmanaged `Job`, factory `CoroutineScope`, leaking across layers);
- when breaking the rules is acceptable (rarely);
- legitimate escape hatches with explicit lifetimes;
- how to detect violations and test structured concurrency.

### What Is Structured Concurrency?

Key ideas:
1. Every coroutine belongs to a `CoroutineScope`.
2. Children are tied to parents.
3. Parents wait for all children.
4. Cancellation flows from parent to children.
5. Exceptions propagate from children to parent.
6. No coroutine outlives its scope (except intentionally scoped, well-documented escape hatches; see below).

#### Core Principle

```text
Scope
   Parent Coroutine
      Child Coroutine 1
         Grandchild 1.1
         Grandchild 1.2
      Child Coroutine 2
          Grandchild 2.1
   All complete together
```

#### Example: Structured Vs Unstructured

```kotlin
import kotlinx.coroutines.*

fun demonstrateStructuredEn() = runBlocking {
    println("=== Structured Concurrency ===")

    // STRUCTURED: Parent waits for children
    coroutineScope {
        launch {
            delay(1000)
            println("Child 1 done")
        }

        launch {
            delay(500)
            println("Child 2 done")
        }

        println("Parent body done, waiting for children...")
    }

    println("All work completed\n")

    // UNSTRUCTURED: Fire and forget
    println("=== Unstructured (violation) ===")

    GlobalScope.launch {
        delay(1000)
        println("This might never execute!")
    }

    println("Function exits immediately")
    // GlobalScope coroutine might be abandoned!
}
```

**Output:**
```kotlin
=== Structured Concurrency ===
Parent body done, waiting for children...
Child 2 done
Child 1 done
All work completed

=== Unstructured (violation) ===
Function exits immediately
(GlobalScope coroutine may never complete)
```

### Benefits of Structured Concurrency

#### 1. Automatic Cancellation

```kotlin
import kotlinx.coroutines.*

class AutomaticCancellationDemoEn {
    suspend fun structuredWork() = coroutineScope {
        launch {
            repeat(10) {
                delay(100)
                println("Working... $it")
            }
        }

        launch {
            delay(300)
            throw Exception("Something went wrong!")
        }
        // On exception in the second coroutine, the first is automatically cancelled
    }

    fun demonstrateBenefit() = runBlocking {
        try {
            structuredWork()
        } catch (e: Exception) {
            println("Caught: ${e.message}")
            println("All coroutines were automatically cancelled")
        }
    }
}
```

#### 2. Exception Propagation

```kotlin
import kotlinx.coroutines.*

class ExceptionPropagationDemoEn {
    suspend fun structuredWorkWithException() = coroutineScope {
        val deferred1 = async {
            delay(500)
            "Result 1"
        }

        val deferred2 = async {
            delay(100)
            throw IllegalStateException("Deferred 2 failed")
        }

        // Exception propagates to the parent scope
        val result1 = deferred1.await() // Will not run
        val result2 = deferred2.await() // Throws

        "Never returned"
    }

    fun demonstrate() = runBlocking {
        try {
            structuredWorkWithException()
        } catch (e: IllegalStateException) {
            println("Exception properly propagated: ${e.message}")
        }
    }
}
```

#### 3. Completion Guarantees

```kotlin
import kotlinx.coroutines.*

class CompletionGuaranteesDemoEn {
    suspend fun structuredWorkWithGuarantees() = coroutineScope {
        launch {
            try {
                repeat(10) {
                    delay(100)
                    println("Processing $it")
                }
            } finally {
                println("Cleanup executed")
            }
        }

        delay(300)
        println("Parent completing")
        // Parent waits for the child coroutine, including finally
    }

    fun demonstrate() = runBlocking {
        structuredWorkWithGuarantees()
        println("Everything completed, including cleanup")
    }
}
```

#### 4. Resource Management

```kotlin
import kotlinx.coroutines.*
import java.io.Closeable

class ResourceManagementDemoEn {
    class Resource : Closeable {
        init {
            println("Resource opened")
        }

        override fun close() {
            println("Resource closed")
        }
    }

    suspend fun structuredResourceManagement() = coroutineScope {
        val resource = Resource()

        try {
            launch {
                delay(500)
                println("Using resource")
            }

            launch {
                delay(300)
                throw Exception("Error occurred")
            }
        } finally {
            resource.close()
        }
    }

    fun demonstrate() = runBlocking {
        try {
            structuredResourceManagement()
        } catch (e: Exception) {
            println("Caught exception, but resource was closed")
        }
    }
}
```

### Violation #1: GlobalScope (The Worst Offender)

Why it's bad:
- No parent scope.
- Not cancelled automatically.
- No proper exception propagation.
- No completion guarantees.
- High risk of memory and logic leaks.

```kotlin
import kotlinx.coroutines.*

class GlobalScopeViolationEn {
    fun processData() {
        // VIOLATION: unstructured coroutine
        GlobalScope.launch {
            val data = loadData()
            process(data)
            saveResults()
        }
        // Function returns immediately; coroutine may outlive its owner
    }

    private suspend fun loadData(): String {
        delay(1000)
        return "data"
    }

    private fun process(data: String) {
        println("Processing: $data")
    }

    private fun saveResults() {
        println("Saving results")
    }
}
```

#### Why It Violates Structured Concurrency

```kotlin
import kotlinx.coroutines.*

fun demonstrateGlobalScopeProblemsEn() = runBlocking {
    println("=== GlobalScope Problems ===")

    class Component {
        fun start() {
            println("Component started")

            // PROBLEM: no parent to cancel the coroutine
            GlobalScope.launch {
                delay(2000)
                println("This coroutine has no parent to cancel it")
            }
        }

        fun stop() {
            println("Component stopped")
            // Coroutine keeps running in the background
        }
    }

    val component = Component()
    component.start()

    delay(500)
    component.stop()

    delay(2000)
    println("Coroutine still executed after component stopped!")
}
```

#### The Fix

```kotlin
import kotlinx.coroutines.*

class StructuredComponentEn {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    fun start() {
        println("Component started")

        // GOOD: structured coroutine in a managed scope
        scope.launch {
            delay(2000)
            println("This coroutine will be cancelled correctly")
        }
    }

    fun stop() {
        println("Component stopped")
        scope.cancel()
        // All coroutines are cancelled
    }
}

fun demonstrateStructuredFixEn() = runBlocking {
    val component = StructuredComponentEn()
    component.start()

    delay(500)
    component.stop()

    delay(2000)
    println("Coroutine was properly cancelled")
}
```

### Violation #2: Creating Job() Without Lifecycle

```kotlin
import kotlinx.coroutines.*

class UnmanagedJobViolationEn {
    // VIOLATION: scope is created but never cancelled
    private val customScope = CoroutineScope(Job() + Dispatchers.Main)

    fun doWork() {
        customScope.launch {
            repeat(100) {
                delay(100)
                println("Working $it")
            }
        }
    }
    // MISSING: fun cleanup() { customScope.cancel() }
}
```

Why it's a violation:
1. No explicit end of lifecycle.
2. No cancellation → potentially "eternal" tasks.
3. Holds references → memory leaks.
4. No parent → cannot be cancelled from outside.

#### The Fix: Explicit Lifecycle

```kotlin
import kotlinx.coroutines.*

class ManagedJobComponentEn {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun doWork() {
        scope.launch {
            repeat(100) {
                delay(100)
                println("Working $it")
            }
        }
    }

    fun cleanup() {
        scope.cancel()
        println("All coroutines cancelled")
    }
}

fun demonstrateExplicitLifecycleEn() = runBlocking {
    val component = ManagedJobComponentEn()

    component.doWork()
    delay(500)

    component.cleanup()
    println("Component cleaned up")
}
```

### Violation #3: CoroutineScope() Factory Without Lifecycle

```kotlin
import kotlinx.coroutines.*

class FactoryScopeViolationEn {
    fun processItems(items: List<String>) {
        // VIOLATION: scope created without any lifecycle owner
        CoroutineScope(Dispatchers.Default).launch {
            items.forEach { item ->
                delay(1000)
                println("Processing: $item")
            }
        }
        // Scope reference is lost immediately; cannot cancel
    }
}
```

#### Why It's Problematic

```kotlin
import kotlinx.coroutines.*

fun demonstrateFactoryProblemEn() = runBlocking {
    println("=== CoroutineScope() Factory Problem ===")

    fun processData() {
        CoroutineScope(Dispatchers.Default).launch {
            repeat(5) {
                delay(500)
                println("Processing $it")
            }
        }

        println("Function returned")
        // Scope reference is lost; no way to cancel
    }

    processData()

    delay(1000)
    println("We'd like to cancel, but can't — no scope reference!")

    delay(3000)
    println("Coroutine finished on its own")
}
```

#### The Fix: Pass Scope as Parameter

```kotlin
import kotlinx.coroutines.*

class FactoryScopeFixEn {
    // Accept managed scope from the caller
    fun processItems(scope: CoroutineScope, items: List<String>) {
        scope.launch {
            items.forEach { item ->
                delay(1000)
                println("Processing: $item")
            }
        }
    }
}

fun demonstrateFactoryFixEn() = runBlocking {
    val scope = CoroutineScope(Job() + Dispatchers.Default)
    val processor = FactoryScopeFixEn()

    processor.processItems(scope, listOf("A", "B", "C"))

    delay(1500)
    println("Cancelling...")
    scope.cancel()
    println("Processing cancelled")
}
```

### Violation #4: Leaking Coroutines Across Architectural Boundaries

```kotlin
import kotlinx.coroutines.*

// VIOLATION: repository launches its own GlobalScope coroutines
class LeakyRepositoryEn {
    fun loadData(callback: (String) -> Unit) {
        GlobalScope.launch {
            val data = fetchFromNetwork()
            callback(data)
        }
    }

    private suspend fun fetchFromNetwork(): String {
        delay(1000)
        return "Network data"
    }
}

// ViewModel cannot control repository work
class LeakyViewModelEn {
    private val repository = LeakyRepositoryEn()

    fun loadData() {
        repository.loadData { data ->
            println("Got data: $data")
        }
    }

    fun onCleared() {
        // No way to cancel repository coroutines
    }
}
```

#### The Fix: Suspend Functions and Call-Site Control

```kotlin
import kotlinx.coroutines.*

class StructuredRepositoryEn {
    suspend fun loadData(): String = withContext(Dispatchers.IO) {
        fetchFromNetwork()
    }

    private suspend fun fetchFromNetwork(): String {
        delay(1000)
        return "Network data"
    }
}

class StructuredViewModelEn {
    private val repository = StructuredRepositoryEn()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun loadData() {
        scope.launch {
            try {
                val data = repository.loadData()
                println("Got data: $data")
            } catch (e: CancellationException) {
                println("Cancelled")
                throw e
            }
        }
    }

    fun onCleared() {
        scope.cancel()
        // Cancelling the scope also cancels work in the repository
    }
}
```

### When Breaking Structure Is Acceptable (Rare)

Some cases allow carefully controlled deviations from strict structure when:
- lifetime is explicit and well-documented;
- side effects are isolated;
- a dedicated, managed `CoroutineScope` is used.

#### Legitimate Case 1: Application-Level Background Work

```kotlin
import kotlinx.coroutines.*

class BackgroundSyncManagerEn(
    private val applicationScope: CoroutineScope // Explicit application-level scope
) {
    fun startPeriodicSync() {
        // ACCEPTABLE: work that lives as long as the process
        applicationScope.launch {
            while (isActive) {
                try {
                    performSync()
                    delay(3600_000) // 1 hour
                } catch (e: Exception) {
                    // Log and retry later
                }
            }
        }
    }

    private suspend fun performSync() {
        // Data sync with server
    }
}

class MyApplicationEn : android.app.Application() {
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onCreate() {
        super.onCreate()
        val syncManager = BackgroundSyncManagerEn(applicationScope)
        syncManager.startPeriodicSync()
    }

    override fun onTerminate() {
        super.onTerminate()
        applicationScope.cancel()
    }
}
```

Why acceptable:
- Explicit `applicationScope` with clear lifetime.
- Truly application-level work.
- Ability to shut down.

#### Legitimate Case 2: Fire-and-Forget Analytics

```kotlin
import kotlinx.coroutines.*

class AnalyticsTrackerEn(
    private val analyticsScope: CoroutineScope // Dedicated analytics scope
) {
    fun trackEvent(event: String) {
        // ACCEPTABLE: fire-and-forget in isolated scope
        analyticsScope.launch {
            try {
                sendToAnalyticsServer(event)
            } catch (e: Exception) {
                // Analytics failures should not affect user
            }
        }
    }

    private suspend fun sendToAnalyticsServer(event: String) {
        withContext(Dispatchers.IO) {
            // Send event
        }
    }
}

fun setupAnalyticsEn(app: android.app.Application): AnalyticsTrackerEn {
    val analyticsScope = CoroutineScope(
        SupervisorJob() +
            Dispatchers.IO +
            CoroutineName("Analytics")
    )
    return AnalyticsTrackerEn(analyticsScope)
}
```

Why acceptable:
- Non-critical.
- Intentional fire-and-forget.
- Dedicated scope with `SupervisorJob`.

#### Legitimate Case 3: Crash Reporting

```kotlin
import kotlinx.coroutines.*

class CrashReporterEn {
    // Dedicated scope that can outlive normal cancellation
    private val crashScope = CoroutineScope(
        NonCancellable +
            Dispatchers.IO +
            CoroutineName("CrashReporter")
    )

    fun reportCrash(exception: Throwable) {
        crashScope.launch {
            try {
                sendCrashReport(exception)
            } catch (e: Exception) {
                println("Failed to send crash report: $e")
            }
        }
    }

    private suspend fun sendCrashReport(exception: Throwable) {
        // Send crash report
    }
}

class MyApplicationCrashEn : android.app.Application() {
    private val crashReporter = CrashReporterEn()

    override fun onCreate() {
        super.onCreate()

        Thread.setDefaultUncaughtExceptionHandler { _, exception ->
            crashReporter.reportCrash(exception)
            Thread.sleep(1000)
            kotlin.system.exitProcess(1)
        }
    }
}
```

Why acceptable:
- Last-chance critical reporting.
- Explicit `NonCancellable` usage.
- `Short`, well-defined work.

### Escape Hatch Patterns

#### Pattern 1: Explicit Application-Level Scope

```kotlin
import kotlinx.coroutines.*

class ApplicationScopeProviderEn {
    val applicationScope = CoroutineScope(
        SupervisorJob() +
            Dispatchers.Default +
            CoroutineName("Application")
    )

    fun shutdown() {
        applicationScope.cancel()
    }
}

class LongRunningServiceEn(
    private val applicationScope: CoroutineScope
) {
    fun startBackgroundWork() {
        applicationScope.launch {
            while (isActive) {
                doWork()
                delay(60_000)
            }
        }
    }

    private suspend fun doWork() {
        // Work that should outlive UI
    }
}
```

#### Pattern 2: supervisorScope for Independent Tasks

```kotlin
import kotlinx.coroutines.*

class IndependentTaskRunnerEn {
    suspend fun runIndependentTasks() = supervisorScope {
        val task1 = launch {
            try {
                performTask1()
            } catch (e: Exception) {
                // Handle task 1 failure
            }
        }

        val task2 = launch {
            try {
                performTask2()
            } catch (e: Exception) {
                // Handle task 2 failure
            }
        }

        task1.join()
        task2.join()
    }

    private suspend fun performTask1() {
        delay(1000)
    }

    private suspend fun performTask2() {
        delay(500)
        throw Exception("Task 2 failed")
    }
}

fun demonstrateSupervisorScopeEn() = runBlocking {
    val runner = IndependentTaskRunnerEn()
    runCatching { runner.runIndependentTasks() }
    println("Both tasks completed independently")
}
```

#### Pattern 3: Detached Coroutine (Use with Extreme Care)

```kotlin
import kotlinx.coroutines.*

class DetachedCoroutinePatternEn {
    fun performDetachedWork(work: suspend () -> Unit) {
        // ESCAPE HATCH: logically detached coroutine with its own Job.
        // Important: this intentionally breaks structured concurrency.
        CoroutineScope(Job() + Dispatchers.Default).launch {
            work()
        }
    }
}

fun demonstrateDetachedEn() = runBlocking {
    val pattern = DetachedCoroutinePatternEn()

    pattern.performDetachedWork {
        repeat(10) {
            delay(100)
            println("Detached work $it")
        }
    }

    println("Parent runBlocking completed, detached work may continue")
    delay(1000)
}
```

### Real-World Examples

#### Example 1: Background Data Sync

```kotlin
import kotlinx.coroutines.*

class DataSyncManagerEn(
    private val applicationScope: CoroutineScope
) {
    private var syncJob: Job? = null

    fun startSync() {
        syncJob?.cancel()
        syncJob = applicationScope.launch {
            while (isActive) {
                try {
                    performSync()
                    delay(3600_000)
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    delay(60_000)
                }
            }
        }
    }

    fun stopSync() {
        syncJob?.cancel()
        syncJob = null
    }

    private suspend fun performSync() {
        withContext(Dispatchers.IO) {
            println("Syncing data...")
            delay(5000)
            println("Sync completed")
        }
    }
}

fun setupBackgroundSyncEn() {
    val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    val syncManager = DataSyncManagerEn(applicationScope)
    syncManager.startSync()

    Runtime.getRuntime().addShutdownHook(Thread {
        syncManager.stopSync()
        applicationScope.cancel()
    })
}
```

#### Example 2: Analytics SDK

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentLinkedQueue

data class AnalyticsEventEn(val name: String, val properties: Map<String, Any>)

class AnalyticsSDK_En private constructor() {
    private val analyticsScope = CoroutineScope(
        SupervisorJob() +
            Dispatchers.IO +
            CoroutineName("Analytics") +
            CoroutineExceptionHandler { _, exception ->
                println("Analytics error: $exception")
            }
    )

    private val eventQueue = ConcurrentLinkedQueue<AnalyticsEventEn>()
    private var flushJob: Job? = null

    fun initialize() {
        startPeriodicFlush()
    }

    fun trackEvent(event: AnalyticsEventEn) {
        eventQueue.offer(event)
    }

    private fun startPeriodicFlush() {
        flushJob = analyticsScope.launch {
            while (isActive) {
                delay(10_000)
                val events = mutableListOf<AnalyticsEventEn>()
                while (eventQueue.isNotEmpty()) {
                    eventQueue.poll()?.let { events.add(it) }
                }
                if (events.isNotEmpty()) {
                    try {
                        flushEvents(events)
                    } catch (e: Exception) {
                        events.forEach { eventQueue.offer(it) }
                    }
                }
            }
        }
    }

    private suspend fun flushEvents(events: List<AnalyticsEventEn>) {
        withContext(Dispatchers.IO) {
            println("Sending ${events.size} analytics events")
        }
    }

    fun shutdown() {
        flushJob?.cancel()
        analyticsScope.cancel()
    }

    companion object {
        val instance = AnalyticsSDK_En()
    }
}
```

#### Example 3: Crash Reporting SDK

```kotlin
import kotlinx.coroutines.*

data class CrashReportEn(
    val exception: String,
    val stackTrace: String,
    val timestamp: Long
)

class CrashReportingSDK_En {
    private val crashScope = CoroutineScope(
        NonCancellable +
            Dispatchers.IO +
            CoroutineName("CrashReporter")
    )

    fun reportException(exception: Throwable) {
        crashScope.launch {
            try {
                val report = buildCrashReport(exception)
                sendCrashReport(report)
            } catch (e: Exception) {
                println("Failed to send crash report: $e")
            }
        }
    }

    private fun buildCrashReport(exception: Throwable): CrashReportEn {
        return CrashReportEn(
            exception = exception.toString(),
            stackTrace = exception.stackTraceToString(),
            timestamp = System.currentTimeMillis()
        )
    }

    private suspend fun sendCrashReport(report: CrashReportEn) {
        withContext(Dispatchers.IO) {
            delay(1000)
            println("Crash report sent: ${report.exception}")
        }
    }
}
```

#### Example 4: Application-Level Cache

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

class ApplicationCacheEn(
    private val applicationScope: CoroutineScope
) {
    private val cache = ConcurrentHashMap<String, CacheEntry>()
    private var cleanupJob: Job? = null

    fun initialize() {
        startPeriodicCleanup()
    }

    fun put(key: String, value: Any, ttlMs: Long = 3600_000) {
        cache[key] = CacheEntry(
            value = value,
            expiryTime = System.currentTimeMillis() + ttlMs
        )
    }

    fun get(key: String): Any? {
        val entry = cache[key] ?: return null
        return if (entry.isExpired()) {
            cache.remove(key)
            null
        } else {
            entry.value
        }
    }

    private fun startPeriodicCleanup() {
        cleanupJob = applicationScope.launch {
            while (isActive) {
                delay(60_000)
                val now = System.currentTimeMillis()
                cache.entries.removeIf { (_, entry) ->
                    entry.expiryTime < now
                }
                println("Cache cleanup: ${cache.size} entries left")
            }
        }
    }

    fun shutdown() {
        cleanupJob?.cancel()
        cache.clear()
    }

    private data class CacheEntry(
        val value: Any,
        val expiryTime: Long
    ) {
        fun isExpired() = System.currentTimeMillis() > expiryTime
    }
}
```

### Detecting Violations

#### Tool 1: Detekt Rule (Simplified)

```kotlin
// Simplified Detekt rule to detect GlobalScope usage.
class GlobalScopeUsageRuleEn : Rule() {
    override val issue = Issue(
        id = "GlobalScopeUsage",
        severity = Severity.Warning,
        description = "GlobalScope usually violates structured concurrency",
        debt = Debt.FIVE_MINS
    )

    override fun visitCallExpression(expression: KtCallExpression) {
        super.visitCallExpression(expression)
        val text = expression.text
        if (text.startsWith("GlobalScope.launch") || text.startsWith("GlobalScope.async")) {
            report(
                CodeSmell(
                    issue = issue,
                    entity = Entity.from(expression),
                    message = "Detected GlobalScope. Prefer a structured scope."
                )
            )
        }
    }
}
```

#### Tool 2: Android Lint Rule (Simplified)

```kotlin
// Simplified Lint rule to detect CoroutineScope without an obvious cancel.
class UncancelledScopeDetectorEn : Detector(), SourceCodeScanner {
    override fun getApplicableMethodNames(): List<String> = listOf("CoroutineScope")

    override fun visitMethodCall(
        context: JavaContext,
        node: UCallExpression,
        method: PsiMethod
    ) {
        val containingClass = node.getContainingClass()
        val hasCancelMethod = containingClass?.methods?.any { it.name == "cancel" } ?: false

        if (!hasCancelMethod) {
            context.report(
                issue = ISSUE,
                location = context.getLocation(node),
                message = "CoroutineScope is created without an obvious cancellation mechanism (simplified rule)."
            )
        }
    }

    companion object {
        val ISSUE: Issue = Issue.create(
            id = "UncancelledCoroutineScope",
            briefDescription = "CoroutineScope without cancel",
            explanation = "Every CoroutineScope should have a clear cancellation point.",
            category = Category.CORRECTNESS,
            priority = 8,
            severity = Severity.WARNING,
            implementation = Implementation(
                UncancelledScopeDetectorEn::class.java,
                Scope.JAVA_FILE_SCOPE
            )
        )
    }
}
```

#### Tool 3: Code Review Checklist

```kotlin
/**
 * Structured Concurrency Code Review Checklist
 *
 * RED FLAGS:
 * - GlobalScope.launch / GlobalScope.async
 * - CoroutineScope(Job()) without explicit cancel
 * - Long-lived coroutines inside Repository/UseCase
 * - Coroutines started in constructors
 * - Scopes without clear lifecycle owner
 *
 * GREEN FLAGS:
 * - viewModelScope.launch
 * - lifecycleScope.launch
 * - Repositories/UseCases expose suspend functions instead of hidden long-running coroutines
 * - Explicit scope + cancel
 * - supervisorScope for independent tasks
 * - Documented escape hatches
 */
```

### Testing Structured Concurrency

#### Test 1: Cancellation and Exception Propagation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class StructuredConcurrencyTestEn {
    @Test
    fun testCancellationPropagates() = runTest {
        var child1Cancelled = false
        var child2Cancelled = false

        val scope = CoroutineScope(Job())

        scope.launch {
            try {
                delay(10_000)
            } catch (e: CancellationException) {
                child1Cancelled = true
                throw e
            }
        }

        scope.launch {
            try {
                delay(10_000)
            } catch (e: CancellationException) {
                child2Cancelled = true
                throw e
            }
        }

        advanceTimeBy(100)
        scope.cancel()
        advanceUntilIdle()

        assertTrue(child1Cancelled, "Child 1 should be cancelled")
        assertTrue(child2Cancelled, "Child 2 should be cancelled")
    }

    @Test
    fun testExceptionPropagates() = runTest {
        var parentCaught = false

        try {
            coroutineScope {
                launch {
                    delay(100)
                    throw IllegalStateException("Child failed")
                }

                launch {
                    delay(10_000)
                }
            }
        } catch (e: IllegalStateException) {
            parentCaught = true
        }

        assertTrue(parentCaught, "Exception should propagate to parent")
    }
}
```

#### Test 2: No Leaked Coroutines

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class LeakDetectionTestEn {
    @Test
    fun testNoLeakedCoroutines() = runTest {
        val scope = CoroutineScope(Job())

        repeat(10) {
            scope.launch {
                delay(1_000)
            }
        }

        scope.cancel()
        advanceUntilIdle()

        val job = scope.coroutineContext[Job]!!
        assertTrue(job.isCancelled, "Scope should be cancelled")
        assertTrue(job.children.toList().isEmpty(), "No child jobs should remain")
    }
}
```

### Best Practices

1. Prefer structured concurrency:
   ```kotlin
   suspend fun loadDataEn() = coroutineScope {
       val data1 = async { fetchData1() }
       val data2 = async { fetchData2() }
       DataResult(data1.await(), data2.await())
   }
   ```

2. Use lifecycle-bound scopes (`viewModelScope`, `lifecycleScope`) where appropriate.

3. Repositories and use cases should expose `suspend` functions instead of spawning hidden, long-lived coroutines.

4. Implement escape hatches via explicit, well-documented `CoroutineScope` instances with controlled lifetimes.

5. Any deviation from structured concurrency must be justified in comments and covered by tests.

6. Continuously scan code (linters, checklists) for `GlobalScope`, unmanaged `CoroutineScope(Job())`, and coroutines in the wrong architectural layer.

## Follow-ups

- How would you refactor an existing codebase heavily using `GlobalScope` to a structured model?
- How do you design library APIs to let callers control coroutine lifecycles?
- How would you enforce these rules in a large team (tooling, code review, architecture guidelines)?

## References

- [[c-kotlin]]
- [[c-structured-concurrency]]
- Official Kotlin Coroutines documentation: "Structured concurrency" section

## Related Questions

- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-actor-pattern--kotlin--hard]]
- [[q-android-async-primitives--android--easy]]
