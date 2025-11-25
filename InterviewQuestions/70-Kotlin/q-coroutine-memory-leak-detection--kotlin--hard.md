---
topic: kotlin
id: kotlin-131
title: "Detecting and preventing coroutine memory leaks / Обнаружение и предотвращение утечек памяти"
aliases: [Coroutine Memory Leaks, Утечки памяти в корутинах]
subtopics: [coroutines]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
moc: moc-kotlin
related: [c-android-profiling, c-concurrency, q-coroutine-resource-cleanup--kotlin--medium]
status: draft
created: 2025-10-12
updated: 2025-11-11
tags: [android, coroutines, debugging, difficulty/hard, kotlin, leakcanary, lifecycle, memory-leaks, profiling]

date created: Saturday, November 1st 2025, 1:28:52 pm
date modified: Tuesday, November 25th 2025, 8:53:52 pm
---

# Вопрос (RU)

> Как обнаруживать и предотвращать утечки памяти, связанные с корутинами, в Kotlin/Android (LeakCanary, профилировщики, типичные паттерны утечек и лучшие практики)?

# Question (EN)

> How to detect and prevent coroutine-related memory leaks in Kotlin/Android (LeakCanary, profilers, common leak patterns, and best practices)?

## Ответ (RU)

### Обзор

Утечки памяти в приложениях с корутинами часто малозаметны и при этом опасны. Долгоживущая `Coroutine` может удерживать ссылки на тяжёлые объекты (`Activity`, `Fragment`, `View`, `ViewModel`), мешая сборке мусора и в итоге приводя к OutOfMemoryError, если она живёт дольше предполагаемого жизненного цикла этих объектов.

Важно понимать типичные паттерны утечек, способы их обнаружения и стратегии предотвращения, особенно в Android.

### Что Такое Утечка Памяти, Связанная С Корутинами?

Строго говоря, утечка памяти возникает, когда объекты, которые больше не нужны, остаются достижимыми бесконечно долго.

Типичный сценарий утечки с корутинами:
1. Корутина продолжает выполняться после того, как связанный компонент (`Activity`, `Fragment`, `View`, `ViewModel` и т.п.) должен считаться завершённым.
2. Корутина (её `Job`, scope или лямбды) удерживает сильные ссылки на эти устаревшие объекты.
3. Эти объекты не могут быть собраны GC.
4. Память накапливается с течением времени.

Важно отличать:
- Временное удержание (например, долгий `delay` внутри `lifecycleScope`, который будет отменён в `onDestroy`) — не утечка, но может быть проблемой производительности/UX.
- Реальную утечку — когда корутина живёт за пределами ожидаемого жизненного цикла владельца и не освобождает ссылки.

```kotlin
// ПРИМЕР УТЕЧКИ (концептуальный)
class LeakyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ПЛОХО: корутина переживает Activity, если не отменена
        GlobalScope.launch(Dispatchers.Main) {
            while (true) {
                delay(1000)
                updateUI() // Захватывает Activity (this) и её View
            }
        }
    }

    private fun updateUI() {
        // Доступ к Activity/View
    }
}
```

### Обзор Типичных Источников Утечек

| Тип утечки | Причина | Тяжесть | Сложность обнаружения |
|-----------|---------|--------|------------------------|
| `GlobalScope` | Скоуп с временем жизни `Application` используется для UI/компонентной логики, нет автоотмены | Критично | Легко |
| Нет отмены | Кастомные scope не отменяются при уничтожении компонента | Высокая | Средняя |
| Захваченный контекст | Лямбды захватывают `Activity`/`View`/`Context` в долгоживущих задачах | Высокая | Средне–сложно |
| Длинные операции | Долгие I/O/CPU задачи жёстко связаны с UI или запускаются в скоупах, живущих дольше UI | Средне–высокая | Средняя |
| Утечки коллектора `Flow` | `collect` живёт дольше жизненного цикла (например, в `GlobalScope`) | Высокая | Сложно |

### Утечка #1: Использование GlobalScope

Проблема: `GlobalScope` живёт всё время работы процесса и не отменяется автоматически. Использование его для работы, логически принадлежащей компоненту UI, может привести к удержанию этого компонента.

#### Проблема

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*

class GlobalScopeLeakActivity : AppCompatActivity() {
    private var data: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ПЛОХО: работа Activity запускается в GlobalScope
        GlobalScope.launch(Dispatchers.IO) {
            delay(10_000)

            // Activity могла быть уничтожена, но корутина продолжает работать
            val result = fetchDataFromNetwork()

            // Захватывает Activity через withContext/this
            withContext(Dispatchers.Main) {
                updateUI(result)
            }
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(5_000)
        return "Network data"
    }

    private fun updateUI(data: String) {
        // Доступ к View — может привести к крэшу или утечке
    }
}
```

#### Почему Это Приводит К Утечке

1. `GlobalScope` никогда не отменяется автоматически.
2. Лямбды внутри корутины захватывают экземпляр `Activity` и её `View`.
3. Пока корутина жива, `Activity` не может быть собрана GC.
4. При поворотах/навигации такие корутины накапливаются, удерживая старые экземпляры.

#### Концептуальное Влияние На Память

```kotlin
class GlobalScopeLeakSimulation {
    fun demonstrateLeak() {
        repeat(10) {
            GlobalScopeLeakActivity().onCreate(null)
            // Допустим, система затем уничтожает каждую Activity
        }

        // Если корутины не отменены, они могут удерживать все эти Activity и их иерархии View.
    }
}
```

#### Исправление

Привязывайте корутины к корректному lifecycle-aware scope.

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class FixedActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ХОРОШО: работа привязана к lifecycleScope Activity
        lifecycleScope.launch {
            try {
                val data = fetchDataFromNetwork()
                updateUI(data)
            } catch (e: CancellationException) {
                // Отмена произойдёт автоматически в onDestroy
                throw e
            }
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(5_000)
        return "Network data"
    }

    private fun updateUI(data: String) {
        // Не будет вызвано после отмены lifecycleScope
    }
}
```

#### Обнаружение

Используйте статический анализ (Detekt, Lint) для флага `GlobalScope` в UI/компонентном коде и рассматривайте его как smell, кроме чётко процесс-широких задач.

### Утечка #2: Неотмена При Уничтожении Компонента

Проблема: создаются собственные `CoroutineScope`, но не отменяются при уничтожении компонента.

#### Пример С `Fragment`

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*

class LeakyFragment : Fragment() {
    // ПЛОХО: кастомный scope никогда не отменяется
    private val customScope = CoroutineScope(Dispatchers.Main + Job())

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        customScope.launch {
            while (isActive) {
                delay(1_000)
                updateCounter() // Удерживает Fragment/View
            }
        }
    }

    private fun updateCounter() {
        view?.findViewById<TextView>(R.id.counter)?.text = "Updated"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // ОШИБКА: customScope не отменён; Fragment и View могут удерживаться
        // customScope.cancel()
    }
}
```

#### Исправление: Lifecycle-aware Scope

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class FixedFragment : Fragment() {
    // Вариант 1: использовать viewLifecycleOwner.lifecycleScope для UI-логики
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            while (isActive) {
                delay(1_000)
                updateCounter()
            }
        }
    }

    private fun updateCounter() {
        view?.findViewById<TextView>(R.id.counter)?.text = "Updated"
    }
}
```

```kotlin
// Вариант 2: ручное управление scope для не-UI времени жизни
import android.os.Bundle
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*

class FixedFragmentWithCustomScope : Fragment() {
    private var customScope: CoroutineScope? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        customScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    }

    override fun onDestroy() {
        super.onDestroy()
        customScope?.cancel()
        customScope = null
    }
}
```

#### Пример С `ViewModel`

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.*

class LeakyViewModel : ViewModel() {
    // ПЛОХО: кастомный scope, не отменяемый в onCleared
    private val customScope = CoroutineScope(Dispatchers.IO + Job())

    fun loadData() {
        customScope.launch {
            val data = fetchData()
            processData(data)
        }
    }

    override fun onCleared() {
        super.onCleared()
        // ОШИБКА: нет customScope.cancel()
    }

    private suspend fun fetchData(): String {
        delay(1_000)
        return "data"
    }

    private fun processData(data: String) {
        // ...
    }
}

class FixedViewModel : ViewModel() {
    // ХОРОШО: использовать viewModelScope
    fun loadData() {
        viewModelScope.launch {
            val data = fetchData()
            processData(data)
        }
    }

    private suspend fun fetchData(): String {
        delay(1_000)
        return "data"
    }

    private fun processData(data: String) {
        // ...
    }
}
```

### Утечка #3: Захваченные Сильные Ссылки

Проблема: корутины захватывают сильные ссылки на `Activity`, `View` или `Context` в долгих операциях и выполняются в scope, который может жить дольше владельца.

#### Пример (удержание, А Не Утечка При Правильном scope)

```kotlin
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class CapturedReferenceLeakActivity : AppCompatActivity() {
    private lateinit var textView: TextView
    private var userData: LargeUserData? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textView = findViewById(R.id.textView)
        userData = LargeUserData() // Большой объект

        // Здесь используется lifecycleScope, поэтому корутина будет отменена в onDestroy.
        lifecycleScope.launch {
            delay(30_000)
            textView.text = "Updated: ${userData?.info}"
        }
    }
}

data class LargeUserData(
    val info: String = "User info",
    val largeArray: ByteArray = ByteArray(1024 * 1024) // 1MB
)
```

Это пример временного удержания, а не утечки, пока используется правильный scope. Утечка появится, если аналогичный код поместить в scope, который живёт дольше `Activity`.

#### Безопасные Паттерны

- Не захватывать `Activity`/`View` в долгоживущих задачах; выносить обработку в независимые слои (`ViewModel`/репозиторий).
- Использовать проверки `Lifecycle` перед обновлением UI.
- При необходимости — `WeakReference`, но не как замену правильной архитектуре.

##### Вариант Исправления: WeakReference (точечно)

```kotlin
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*
import java.lang.ref.WeakReference

class FixedCapturedReferenceActivity : AppCompatActivity() {
    private lateinit var textView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textView = findViewById(R.id.textView)
        val textViewRef = WeakReference(textView)
        val userData = LargeUserData()

        lifecycleScope.launch {
            val result = withContext(Dispatchers.Default) {
                delay(5_000)
                "Updated: ${userData.info}"
            }

            textViewRef.get()?.text = result
        }
    }
}
```

##### Вариант Исправления: Проверка Lifecycle

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class LifecycleAwareActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val data = fetchData()

            if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
                updateUI(data)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(5_000)
        return "data"
    }

    private fun updateUI(data: String) {
        // Обновление UI только если Activity ещё жива
    }
}
```

##### Вариант Исправления: Вынести Обработку Из UI

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class ExtractedProcessingActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val result = processDataWithoutContext()
            updateUI(result)
        }
    }

    private suspend fun processDataWithoutContext(): String = withContext(Dispatchers.Default) {
        delay(5_000)
        "Processed result"
    }

    private fun updateUI(result: String) {
        // Быстрое обновление UI без тяжёлых ссылок
    }
}
```

### Утечка #4: Длительные Операции Удерживают Ссылки

Проблема: долгие I/O или CPU-задачи напрямую удерживают UI-объекты или запускаются из scope, живущего дольше UI.

#### Пример

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class LongOperationLeakActivity : AppCompatActivity() {
    private lateinit var progressBar: ProgressBar
    private val results = mutableListOf<String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)
        // progressBar = findViewById(...)
    }

    fun downloadLargeFile() {
        // Привязано к lifecycleScope, поэтому это не утечка при корректном использовании,
        // но удерживает память на длительное время.
        lifecycleScope.launch {
            progressBar.visibility = View.VISIBLE

            repeat(100) { i ->
                val chunk = withContext(Dispatchers.IO) {
                    downloadChunk(i)
                }
                results.add(chunk)
                progressBar.progress = i
            }

            progressBar.visibility = View.GONE
        }
    }

    private suspend fun downloadChunk(index: Int): String {
        delay(1_000)
        return "Chunk $index"
    }
}
```

Если запустить подобное из `GlobalScope` или не отменять при уничтожении компонента, это превращается в утечку.

#### Исправление: `Flow` + Lifecycle-aware Сбор

```kotlin
import android.os.Bundle
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class FixedLongOperationActivity : AppCompatActivity() {
    private lateinit var progressBar: ProgressBar

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)
        // progressBar = findViewById(...)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                downloadFlow()
                    .flowOn(Dispatchers.IO)
                    .collect { progress ->
                        updateProgress(progress)
                    }
            }
        }
    }

    private fun downloadFlow(): Flow<DownloadProgress> = flow {
        repeat(100) { i ->
            delay(1_000)
            val chunk = "Chunk $i"
            emit(DownloadProgress(i, chunk))
        }
    }

    private fun updateProgress(progress: DownloadProgress) {
        progressBar.progress = progress.percentage
    }
}

data class DownloadProgress(val percentage: Int, val data: String)
```

#### Исправление: Разделение UI И Бизнес-логики

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class DownloadViewModel : ViewModel() {
    private val _downloadProgress = MutableStateFlow<DownloadState>(DownloadState.Idle)
    val downloadProgress: StateFlow<DownloadState> = _downloadProgress.asStateFlow()

    fun startDownload() {
        viewModelScope.launch {
            _downloadProgress.value = DownloadState.Downloading(0)

            repeat(100) { i ->
                delay(1_000)
                _downloadProgress.value = DownloadState.Downloading(i)
            }

            _downloadProgress.value = DownloadState.Complete
        }
    }
}

sealed class DownloadState {
    object Idle : DownloadState()
    data class Downloading(val progress: Int) : DownloadState()
    object Complete : DownloadState()
}
```

```kotlin
import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch

class DownloadActivity : AppCompatActivity() {
    private val viewModel: DownloadViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.downloadProgress.collect { state ->
                    updateUI(state)
                }
            }
        }

        viewModel.startDownload()
    }

    private fun updateUI(state: DownloadState) {
        when (state) {
            DownloadState.Idle -> { /* ... */ }
            is DownloadState.Downloading -> { /* ... */ }
            DownloadState.Complete -> { /* ... */ }
        }
    }
}
```

### Утечка #5: Коллекторы `Flow` Не Отменены

Проблема: сбор `Flow` выполняется в scope, который живёт дольше UI-компонента (`GlobalScope` и т.п.), удерживая `Fragment`/`Activity`.

#### Пример

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.collect

class LeakyFlowFragment : Fragment() {
    private val dataFlow = MutableSharedFlow<String>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ПЛОХО: коллектор не привязан к жизненному циклу
        GlobalScope.launch {
            dataFlow.collect { data ->
                updateUI(data)
            }
        }
    }

    private fun updateUI(data: String) {
        view?.findViewById<TextView>(R.id.textView)?.text = data
    }
}
```

#### Исправление

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.collect

class FixedFlowFragment : Fragment() {
    private val dataFlow = MutableSharedFlow<String>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                dataFlow.collect { data ->
                    updateUI(data)
                }
            }
        }
    }

    private fun updateUI(data: String) {
        view?.findViewById<TextView>(R.id.textView)?.text = data
    }
}
```

### Инструмент Обнаружения #1: LeakCanary 2.x

LeakCanary 2.x помогает находить случаи, когда корутины/`Job`/`CoroutineScope` удерживают уничтоженные `Activity`, `Fragment` или `View`.

#### Настройка

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
// Дополнительной инициализации в типичном случае не требуется.
```

#### Интерпретация Отчётов

Признаки корутинных утечек:
- GC-root — поток (например, `DefaultDispatcher-worker-1`) или долгоживущий scope.
- В цепочке ссылок видны `CoroutineScope`, `Job`, диспетчеры, ведущие к экземплярам `Activity`/`Fragment`.

### Инструмент Обнаружения #2: Android Studio Memory Profiler

Подход:
1. Воспроизвести сценарий: создать и уничтожить подозряемый компонент.
2. Сделать heap dump.
3. Найти несколько экземпляров класса и проверить, удерживаются ли они через `Job`/`CoroutineScope`/диспетчеры.

```kotlin
import android.content.Context
import android.os.Debug
import java.io.File

class MemoryProfilerHelper(private val context: Context) {
    fun dumpHeap() {
        val heapDumpFile = File(context.filesDir, "heap_dump.hprof")
        Debug.dumpHprofData(heapDumpFile.absolutePath)
    }
}
```

### Инструмент Обнаружения #3: DebugProbes Для Корутин

`kotlinx-coroutines-debug` даёт возможность видеть активные корутины и их состояния (использовать только в debug-билдах).

#### Настройка

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-debug:1.7.3")
}
```

```kotlin
import android.app.Application
import kotlinx.coroutines.debug.DebugProbes

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            DebugProbes.install()
        }
    }
}
```

#### Выгрузка Информации О Корутинах

```kotlin
import kotlinx.coroutines.debug.DebugProbes

class CoroutineDebugger {
    fun dumpActiveCoroutines() {
        val coroutines = DebugProbes.dumpCoroutinesInfo()
        println("Active coroutines: ${coroutines.size}")

        coroutines.forEach { info ->
            println("Coroutine context: ${info.context}")
            println("State: ${info.state}")
        }
    }
}
```

### Инспекция Дерева `Job`

Ручная проверка иерархии `Job` помогает убедиться, что scope корректно отменяются.

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job

class JobTreeInspector {
    fun inspectJobTree(job: Job, indent: String = "") {
        println("${indent}Job: $job")
        println("${indent}  isActive: ${job.isActive}")
        println("${indent}  isCompleted: ${job.isCompleted}")
        println("${indent}  isCancelled: ${job.isCancelled}")

        job.children.forEach { child ->
            inspectJobTree(child, "${indent}  ")
        }
    }

    fun findActiveJobs(scope: CoroutineScope): List<Job> {
        val root = scope.coroutineContext[Job] ?: return emptyList()
        return collectActiveJobs(root)
    }

    private fun collectActiveJobs(job: Job): List<Job> {
        val active = mutableListOf<Job>()
        if (job.isActive) active.add(job)
        job.children.forEach { child ->
            active += collectActiveJobs(child)
        }
        return active
    }
}
```

### Предотвращение: Lifecycle-aware Scope

Используйте стандартные Android lifecycle-aware scope:

```kotlin
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModel
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

class LifecycleScopesDemo : AppCompatActivity() {
    fun demonstrateScopes() {
        // Scope Activity — отменяется в onDestroy
        lifecycleScope.launch {
            // Безопасно: корутина не переживёт Activity
        }
    }
}

class FragmentScopesDemo : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Для логики, завязанной на View
        viewLifecycleOwner.lifecycleScope.launch {
            // Живёт столько же, сколько View
        }
    }
}

class MyViewModel : ViewModel() {
    init {
        // viewModelScope — отменяется в onCleared
        viewModelScope.launch {
            // Бизнес-логика
        }
    }
}
```

#### Выбор Правильного Scope

- `GlobalScope`: только для действительно процесс-широких задач; почти никогда не подходит для UI.
- `lifecycleScope` (`Activity`/`Fragment`): для задач, привязанных к жизненному циклу компонента.
- `viewLifecycleOwner.lifecycleScope`: для задач, завязанных на `View` фрагмента.
- `viewModelScope`: для логики `ViewModel`, независимой от конкретных `View`.

### Предотвращение: Структурированная Конкуррентность

```kotlin
import kotlinx.coroutines.*

class StructuredConcurrencyDemo {
    // ПЛОХО: неструктурированная конкуррентность
    fun unstructuredExample() {
        GlobalScope.launch {
            // Родитель не знает об этой корутине
        }
    }

    // ХОРОШО: структурированная конкуррентность
    suspend fun structuredExample() = coroutineScope {
        launch {
            // Child 1
        }

        launch {
            // Child 2
        }
        // coroutineScope ждёт всех детей; отмена распространяется.
    }
}
```

### Тестирование На Утечки (концептуально)

Можно проверять, что scope корректно отменяется и не оставляет активных `Job`.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class LeakDetectionTest {
    @Test
    fun testNoLeakedCoroutines() = runTest {
        val scope = CoroutineScope(Job() + Dispatchers.Default)

        scope.launch {
            delay(1_000)
        }

        scope.cancel()
        advanceUntilIdle()

        val job = scope.coroutineContext[Job]!!
        assertFalse(job.isActive, "Scope should be cancelled")
        assertTrue(job.children.none(), "All children should be cancelled")
    }
}
```

Для Android интеграции можно использовать LeakCanary-подходы (например, `DetectLeaksAfterTestSuccess`).

### Статический Анализ: Правила Detekt (концептуально)

```yaml
# detekt.yml (концептуальный пример)
coroutines:
  # Идеи для правил:
  # - флагать использование GlobalScope
  # - флагать поля CoroutineScope без явной отмены в onCleared/onDestroy/close
```

### Мониторинг В Продакшене (концептуально)

```kotlin
import kotlinx.coroutines.*

class CoroutineLeakMonitor {
    @Volatile
    private var activeScopes = 0

    fun onScopeCreated() {
        activeScopes++
        if (activeScopes > 100) {
            logWarning("Too many active scopes: $activeScopes")
        }
    }

    fun onScopeCancelled() {
        activeScopes--
    }

    private fun logWarning(message: String) {
        // Логирование / репортинг
    }
}

class InstrumentedScopeFactory(private val monitor: CoroutineLeakMonitor) {
    fun createScope(): CoroutineScope {
        monitor.onScopeCreated()
        val job = SupervisorJob().apply {
            invokeOnCompletion { monitor.onScopeCancelled() }
        }
        return CoroutineScope(job + Dispatchers.Main)
    }
}
```

### Резюме Лучших Практик

1. Используйте lifecycle-aware scope (`lifecycleScope`, `viewModelScope`, `viewLifecycleOwner.lifecycleScope`).
2. Не используйте `GlobalScope` для логики, связанной с `Activity`/`Fragment`/`View`.
3. Любой созданный вручную `CoroutineScope` должен быть явно отменён.
4. Избегайте захвата ссылок на `Activity`/`View`/`Context` в долгоживущих корутинах; передавайте только необходимые данные или выносите логику в отдельные слои.
5. Для коллекции `Flow` используйте `repeatOnLifecycle` и соответствующие lifecycle-aware scope.
6. Подключайте LeakCanary в debug-сборках для раннего обнаружения утечек.
7. На code review системно проверяйте использование корутин (scope, отмена, `GlobalScope`, коллекция `Flow`).
8. Отличайте реальные утечки от временного удержания — стратегии их устранения различаются.

## Answer (EN)

### Overview

Memory leaks in coroutine-based applications can be subtle and devastating. A single long-lived `Coroutine` can hold references to large objects (`Activity`, `Fragment`, `View`, `ViewModel`), preventing garbage collection and causing OutOfMemoryErrors if it outlives their intended lifecycle. Understanding common leak patterns, detection techniques, and prevention strategies is essential for production Android development.

This guide covers common coroutine-related leak patterns, detection tools (LeakCanary, Memory Profiler, DebugProbes), prevention strategies, and high-level testing approaches.

### What Is a Coroutine Memory Leak?

Strictly speaking, a memory leak occurs when objects that are no longer needed remain strongly reachable indefinitely.

A coroutine-related leak pattern typically occurs when:
1. A coroutine continues running after its associated component (`Activity`, `Fragment`, `View`, `ViewModel`, etc.) should be considered finished.
2. The coroutine (its `Job`, scope, or captured lambdas) holds strong references to those obsolete objects.
3. These objects cannot be garbage collected.
4. Memory usage accumulates over time.

Note: Temporary retention during a valid lifecycle (e.g., a long `delay` in a scope that will be cancelled in `onDestroy`) is not a leak, but can still be a performance/UX issue.

```kotlin
// LEAK EXAMPLE (conceptual)
class LeakyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // BAD: Coroutine outlives Activity if not cancelled
        GlobalScope.launch(Dispatchers.Main) {
            while (true) {
                delay(1000)
                updateUI() // Captures Activity (this) and its Views
            }
        }
    }

    private fun updateUI() {
        // Access Activity/Views
    }
}
```

### Common Leak Sources Overview

| Leak Type | Root Cause | Severity | Detection Difficulty |
|-----------|-----------|----------|---------------------|
| `GlobalScope` | `Application`-lifetime scope used for UI / component work, no automatic cancellation | Critical | Easy |
| Missing cancellation | Custom scopes not cancelled on component teardown | High | Medium |
| Captured context | Lambdas capture `Activity`/`View`/`Context` in long-running work | High | Medium–Hard |
| `Long` operations | Tightly couple long I/O/CPU work with UI scope, or run off-scope work that still references UI | Medium–High | Medium |
| Leaked collectors | `Flow` collectors live beyond lifecycle (e.g., `GlobalScope.collect`) | High | Hard |

### Leak #1: `GlobalScope` Usage

Problem: `GlobalScope` coroutines live for the entire process lifetime and are never cancelled automatically. Using it for work that conceptually belongs to a UI component will leak that component.

#### The Problem

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*

class GlobalScopeLeakActivity : AppCompatActivity() {
    private var data: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // BAD: GlobalScope coroutine on Activity work
        GlobalScope.launch(Dispatchers.IO) {
            // Simulate loading data
            delay(10_000)

            // Activity might be destroyed, but coroutine continues
            val result = fetchDataFromNetwork()

            // Captures this Activity via runOnUiThread / outer scope
            withContext(Dispatchers.Main) {
                updateUI(result)
            }
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(5_000)
        return "Network data"
    }

    private fun updateUI(data: String) {
        // Access views - may crash or leak if Activity is destroyed
    }
}
```

#### Why It Leaks

1. `GlobalScope` is never cancelled automatically.
2. The launched coroutine captures the enclosing `Activity` instance and its views via lambdas.
3. As long as the coroutine is running, the `Activity` cannot be collected.
4. Rotations / navigations can start more such coroutines → accumulated leaked `Activities`.

#### Memory Impact (Conceptual)

```kotlin
class GlobalScopeLeakSimulation {
    fun demonstrateLeak() {
        repeat(10) {
            // Each new instance would start a GlobalScope coroutine
            GlobalScopeLeakActivity().onCreate(null)
            // Assume each corresponding Activity is later destroyed by the system
        }

        // If none of those coroutines are cancelled, they may all retain their
        // respective Activity instances and view hierarchies until completion.
    }
}
```

#### The Fix

Tie coroutines to the appropriate lifecycle-aware scope:

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class FixedActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // GOOD: Use lifecycleScope for Activity-bound work
        lifecycleScope.launch {
            try {
                val data = fetchDataFromNetwork()
                updateUI(data)
            } catch (e: CancellationException) {
                // Cancelled automatically in onDestroy
                throw e
            }
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(5_000)
        return "Network data"
    }

    private fun updateUI(data: String) {
        // Safe: will not be called after lifecycleScope is cancelled
    }
}
```

#### Detection

Use static analysis to flag `GlobalScope` usage in UI / component code (Detekt, custom Lint, etc.) and treat it as a code smell except for clearly process-lifetime work.

### Leak #2: Not Cancelling When Component Dies

Problem: Creating custom `CoroutineScope`s and forgetting to cancel them on component teardown.

#### The Problem

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*

class LeakyFragment : Fragment() {
    // BAD: Custom scope never cancelled
    private val customScope = CoroutineScope(Dispatchers.Main + Job())

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        customScope.launch {
            while (isActive) {
                delay(1_000)
                updateCounter() // Holds Fragment / View references
            }
        }
    }

    private fun updateCounter() {
        view?.findViewById<TextView>(R.id.counter)?.text = "Updated"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // MISTAKE: forgot to cancel; Fragment and Views may be retained
        // customScope.cancel()
    }
}
```

#### The Fix

Prefer lifecycle-aware scopes, or ensure manual cancellation.

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class FixedFragment : Fragment() {
    // Option 1: Use viewLifecycleOwner.lifecycleScope for UI-related work
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            while (isActive) {
                delay(1_000)
                updateCounter()
            }
        }
    }

    private fun updateCounter() {
        view?.findViewById<TextView>(R.id.counter)?.text = "Updated"
    }
}
```

```kotlin
// Option 2: Manual scope management for non-View lifetimes
import android.os.Bundle
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*

class FixedFragmentWithCustomScope : Fragment() {
    private var customScope: CoroutineScope? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        customScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    }

    override fun onDestroy() {
        super.onDestroy()
        customScope?.cancel()
        customScope = null
    }
}
```

#### ViewModel Example

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.*

class LeakyViewModel : ViewModel() {
    // BAD: Custom scope never cancelled
    private val customScope = CoroutineScope(Dispatchers.IO + Job())

    fun loadData() {
        customScope.launch {
            val data = fetchData()
            processData(data)
        }
    }

    override fun onCleared() {
        super.onCleared()
        // MISTAKE: Forgot to cancel!
        // customScope.cancel()
    }

    private suspend fun fetchData(): String {
        delay(1_000)
        return "data"
    }

    private fun processData(data: String) {
        // ...
    }
}

class FixedViewModel : ViewModel() {
    // GOOD: Use viewModelScope
    fun loadData() {
        viewModelScope.launch {
            val data = fetchData()
            processData(data)
        }
    }

    private suspend fun fetchData(): String {
        delay(1_000)
        return "data"
    }

    private fun processData(data: String) {
        // ...
    }
}
```

### Leak #3: Captured Strong References

Problem: Coroutines capture strong references to `Activities`, `Views`, or `Context`s in lambdas used for long-running work that may outlive those owners.

#### The Problem

```kotlin
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class CapturedReferenceLeakActivity : AppCompatActivity() {
    private lateinit var textView: TextView
    private var userData: LargeUserData? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textView = findViewById(R.id.textView)
        userData = LargeUserData() // Large object

        // NOTE: Using lifecycleScope means this coroutine is cancelled in onDestroy,
        // so this is not a true leak. But the references are retained until then.
        lifecycleScope.launch {
            delay(30_000) // Long operation within Activity lifetime

            textView.text = "Updated: ${userData?.info}"
        }
    }
}

data class LargeUserData(
    val info: String = "User info",
    val largeArray: ByteArray = ByteArray(1024 * 1024) // 1MB
)
```

This example illustrates retention, not a leak, because `lifecycleScope` cancels in `onDestroy`. It becomes a leak only if the coroutine is in a scope that outlives the `Activity`.

#### Safer Patterns

- Avoid capturing `Activity`/`View` in long-running background work.
- Use separate layers (e.g., `ViewModel`, repository) that do not depend on UI references.
- Optionally, use weak references or lifecycle checks when necessary.

##### Fix Variant: Weak References (use sparingly)

```kotlin
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*
import java.lang.ref.WeakReference

class FixedCapturedReferenceActivity : AppCompatActivity() {
    private lateinit var textView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textView = findViewById(R.id.textView)
        val textViewRef = WeakReference(textView)
        val userData = LargeUserData()

        lifecycleScope.launch {
            val result = withContext(Dispatchers.Default) {
                delay(5_000)
                "Updated: ${userData.info}"
            }

            textViewRef.get()?.text = result
        }
    }
}
```

##### Fix Variant: Check Lifecycle State

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class LifecycleAwareActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val data = fetchData()

            if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
                updateUI(data)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(5_000)
        return "data"
    }

    private fun updateUI(data: String) {
        // Update UI
    }
}
```

##### Fix Variant: Extract Processing Away From UI

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class ExtractedProcessingActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val result = processDataWithoutContext()
            updateUI(result)
        }
    }

    private suspend fun processDataWithoutContext(): String = withContext(Dispatchers.Default) {
        delay(5_000)
        "Processed result"
    }

    private fun updateUI(result: String) {
        // Quick UI update
    }
}
```

### Leak #4: Long-Running Operations Holding References

Problem: `Long`-running I/O or CPU operations that are coupled directly to UI scopes and capture UI objects, or operations started from a scope that outlives the UI (e.g., `GlobalScope`).

#### The Problem

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.*

class LongOperationLeakActivity : AppCompatActivity() {
    private lateinit var progressBar: ProgressBar
    private val results = mutableListOf<String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)
        // progressBar = findViewById(...)
    }

    fun downloadLargeFile() {
        // Tied to Activity lifecycle, so not a leak if correctly scoped,
        // but can retain large objects for a long time.
        lifecycleScope.launch {
            progressBar.visibility = View.VISIBLE

            repeat(100) { i ->
                val chunk = withContext(Dispatchers.IO) {
                    downloadChunk(i)
                }
                results.add(chunk)
                progressBar.progress = i
            }

            progressBar.visibility = View.GONE
        }
    }

    private suspend fun downloadChunk(index: Int): String {
        delay(1_000)
        return "Chunk $index"
    }
}
```

This is lifecycle-safe but can cause high memory usage. It becomes a leak if launched from a scope outliving the `Activity` or if the `Job` is not cancelled.

#### The Fix: Use `Flow` with Lifecycle-Aware Collection

```kotlin
import android.os.Bundle
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class FixedLongOperationActivity : AppCompatActivity() {
    private lateinit var progressBar: ProgressBar

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)
        // progressBar = findViewById(...)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                downloadFlow()
                    .flowOn(Dispatchers.IO)
                    .collect { progress ->
                        updateProgress(progress)
                    }
            }
        }
    }

    private fun downloadFlow(): Flow<DownloadProgress> = flow {
        repeat(100) { i ->
            delay(1_000)
            val chunk = "Chunk $i"
            emit(DownloadProgress(i, chunk))
        }
    }

    private fun updateProgress(progress: DownloadProgress) {
        progressBar.progress = progress.percentage
    }
}

data class DownloadProgress(val percentage: Int, val data: String)
```

#### The Fix: Separate Business Logic from UI

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class DownloadViewModel : ViewModel() {
    private val _downloadProgress = MutableStateFlow<DownloadState>(DownloadState.Idle)
    val downloadProgress: StateFlow<DownloadState> = _downloadProgress.asStateFlow()

    fun startDownload() {
        viewModelScope.launch {
            _downloadProgress.value = DownloadState.Downloading(0)

            repeat(100) { i ->
                delay(1_000)
                _downloadProgress.value = DownloadState.Downloading(i)
            }

            _downloadProgress.value = DownloadState.Complete
        }
    }
}

sealed class DownloadState {
    object Idle : DownloadState()
    data class Downloading(val progress: Int) : DownloadState()
    object Complete : DownloadState()
}
```

```kotlin
import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch

class DownloadActivity : AppCompatActivity() {
    private val viewModel: DownloadViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.downloadProgress.collect { state ->
                    updateUI(state)
                }
            }
        }

        viewModel.startDownload()
    }

    private fun updateUI(state: DownloadState) {
        when (state) {
            DownloadState.Idle -> { /* ... */ }
            is DownloadState.Downloading -> { /* ... */ }
            DownloadState.Complete -> { /* ... */ }
        }
    }
}
```

### Leak #5: `Flow` Collectors Not Cancelled

Problem: `Flow` collectors run in scopes that outlive their UI/component, e.g., `GlobalScope.launch { flow.collect { ... } }` from a `Fragment`, retaining the `Fragment`.

#### The Problem

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.collect

class LeakyFlowFragment : Fragment() {
    private val dataFlow = MutableSharedFlow<String>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // BAD: Collector not bound to lifecycle
        GlobalScope.launch {
            dataFlow.collect { data ->
                updateUI(data)
            }
        }
    }

    private fun updateUI(data: String) {
        view?.findViewById<TextView>(R.id.textView)?.text = data
    }
}
```

#### The Fix

Bind collection to the appropriate lifecycle.

```kotlin
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.collect

class FixedFlowFragment : Fragment() {
    private val dataFlow = MutableSharedFlow<String>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                dataFlow.collect { data ->
                    updateUI(data)
                }
            }
        }
    }

    private fun updateUI(data: String) {
        view?.findViewById<TextView>(R.id.textView)?.text = data
    }
}
```

### Detection Tool #1: LeakCanary 2.x

LeakCanary 2.x can detect leaks where coroutines (and their contexts/scopes) retain destroyed `Activity`/`Fragment`/`View`.

#### Setup

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
// No manual initialization required for standard setup.
```

#### Reading LeakCanary Reports

Typical signs of coroutine-related leaks:

- GC root is a thread (e.g., `DefaultDispatcher-worker-1`) or a long-lived scope.
- Trace shows `CoroutineScope`, `Job`, or dispatcher holding an `Activity`/`Fragment` instance.

### Detection Tool #2: Android Studio Memory Profiler

Use heap dumps to:

1. Trigger a heap dump after destroying the suspected `Activity`/`Fragment`.
2. Look for multiple instances of that class.
3. Inspect references to see if they are retained via coroutine jobs/scopes/dispatchers.

```kotlin
// Example: trigger heap dump in debug-only helper
import android.content.Context
import android.os.Debug
import java.io.File

class MemoryProfilerHelper(private val context: Context) {
    fun dumpHeap() {
        val heapDumpFile = File(context.filesDir, "heap_dump.hprof")
        Debug.dumpHprofData(heapDumpFile.absolutePath)
    }
}
```

### Detection Tool #3: DebugProbes for Coroutines

`kotlinx-coroutines-debug` provides coroutine-specific debugging. Use only in debug builds.

#### Setup

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-debug:1.7.3")
}
```

```kotlin
import android.app.Application
import kotlinx.coroutines.debug.DebugProbes

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            DebugProbes.install()
        }
    }
}
```

#### Dumping Active Coroutines

```kotlin
import kotlinx.coroutines.debug.DebugProbes

class CoroutineDebugger {
    fun dumpActiveCoroutines() {
        val coroutines = DebugProbes.dumpCoroutinesInfo()
        println("Active coroutines: ${coroutines.size}")

        coroutines.forEach { info ->
            println("Coroutine context: ${info.context}")
            println("State: ${info.state}")
        }
    }
}
```

### Job Tree Inspection

Manual inspection of a `Job` hierarchy can help ensure scopes are cancelled.

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job

class JobTreeInspector {
    fun inspectJobTree(job: Job, indent: String = "") {
        println("${indent}Job: $job")
        println("${indent}  isActive: ${job.isActive}")
        println("${indent}  isCompleted: ${job.isCompleted}")
        println("${indent}  isCancelled: ${job.isCancelled}")

        job.children.forEach { child ->
            inspectJobTree(child, "${indent}  ")
        }
    }

    fun findActiveJobs(scope: CoroutineScope): List<Job> {
        val root = scope.coroutineContext[Job] ?: return emptyList()
        return collectActiveJobs(root)
    }

    private fun collectActiveJobs(job: Job): List<Job> {
        val active = mutableListOf<Job>()
        if (job.isActive) active.add(job)
        job.children.forEach { child ->
            active += collectActiveJobs(child)
        }
        return active
    }
}
```

### Prevention: Lifecycle-Aware Scopes

Use the standard Android lifecycle-aware scopes:

```kotlin
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModel
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

class LifecycleScopesDemo : AppCompatActivity() {
    fun demonstrateScopes() {
        // Activity scope - cancelled in onDestroy
        lifecycleScope.launch {
            // Safe: cancelled when Activity destroyed
        }
    }
}

class FragmentScopesDemo : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Fragment lifecycle scope - cancelled with the View
        viewLifecycleOwner.lifecycleScope.launch {
            // Lives as long as the View
        }
    }
}

class MyViewModel : ViewModel() {
    init {
        // viewModelScope - cancelled in onCleared
        viewModelScope.launch {
            // Business logic
        }
    }
}
```

#### Choosing the Right Scope

- `GlobalScope`: process-lifetime work only; almost never appropriate for UI.
- `lifecycleScope` (`Activity`/`Fragment`): for work bound to that component.
- `viewLifecycleOwner.lifecycleScope`: for work bound to `Fragment` view.
- `viewModelScope`: for `ViewModel`/business logic, independent of specific views.

### Prevention: Structured Concurrency

```kotlin
import kotlinx.coroutines.*

class StructuredConcurrencyDemo {
    // BAD: Unstructured
    fun unstructuredExample() {
        GlobalScope.launch {
            // Parent doesn't know about this
        }
    }

    // GOOD: Structured
    suspend fun structuredExample() = coroutineScope {
        launch {
            // Child 1
        }

        launch {
            // Child 2
        }
        // coroutineScope waits for all children; cancellation is propagated.
    }
}
```

### Testing for Leaks (Conceptual)

You can test that your scopes cancel correctly.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class LeakDetectionTest {
    @Test
    fun testNoLeakedCoroutines() = runTest {
        val scope = CoroutineScope(Job() + Dispatchers.Default)

        scope.launch {
            delay(1_000)
        }

        scope.cancel()
        advanceUntilIdle()

        val job = scope.coroutineContext[Job]!!
        assertFalse(job.isActive, "Scope should be cancelled")
        assertTrue(job.children.none(), "All children should be cancelled")
    }
}
```

For Android integration, LeakCanary tests (`DetectLeaksAfterTestSuccess`) can be used as in official docs.

### Static Analysis: Detekt Rules (Conceptual)

```yaml
# detekt.yml (conceptual snippet)
coroutines:
  # Use existing coroutine rules and/or custom rules
  # - flag GlobalScope usage
  # - flag CoroutineScope fields without corresponding cancel in onCleared/onDestroy/close
```

### Production Monitoring (Conceptual)

```kotlin
import kotlinx.coroutines.*

class CoroutineLeakMonitor {
    @Volatile
    private var activeScopes = 0

    fun onScopeCreated() {
        activeScopes++
        if (activeScopes > 100) {
            logWarning("Too many active scopes: $activeScopes")
        }
    }

    fun onScopeCancelled() {
        activeScopes--
    }

    private fun logWarning(message: String) {
        // Send to logging / crash reporting
    }
}

class InstrumentedScopeFactory(private val monitor: CoroutineLeakMonitor) {
    fun createScope(): CoroutineScope {
        monitor.onScopeCreated()
        val job = SupervisorJob().apply {
            invokeOnCompletion { monitor.onScopeCancelled() }
        }
        return CoroutineScope(job + Dispatchers.Main)
    }
}
```

### Best Practices Summary

1. Use lifecycle-aware scopes (`lifecycleScope`, `viewModelScope`, `viewLifecycleOwner.lifecycleScope`).
2. Avoid `GlobalScope` for anything tied to a component lifecycle.
3. If you create a custom `CoroutineScope`, you are responsible for cancelling it.
4. Avoid capturing `Activity`/`View`/`Context` references in long-running operations; prefer passing minimal data or using separate layers.
5. Use `repeatOnLifecycle` (or similar) for `Flow` collection to auto-start/stop collectors.
6. Enable LeakCanary in debug builds to catch leaks early.
7. Review coroutine usage in code reviews (scope ownership, cancellation, `GlobalScope`, `Flow` collectors).
8. Distinguish between true leaks (never-released objects) and temporary retention; both matter, but fixes differ.

## Follow-ups (RU)

1. Как вы будете обнаруживать утечку памяти, если корутина в итоге завершается, но работает «слишком долго»?
2. В чём разница между реальной утечкой памяти и временным удержанием памяти в корутинах?
3. Как использовать heap dump для явного выявления утечек, связанных с корутинами?
4. В каких случаях допустимо использовать `GlobalScope` и как сделать это безопасно?
5. Как протестировать, что `ViewModel` корректно отменяет все корутины в `onCleared()`?
6. Каковы накладные расходы использования `WeakReference` в корутинах?
7. Как отслеживать потенциальные утечки корутин в продакшене без LeakCanary?

## Follow-ups (EN)

1. How do you detect a memory leak caused by a coroutine that completes eventually but takes too long?
2. What's the difference between a memory leak and a memory retention issue in coroutines?
3. How can you use Java heap dumps to specifically identify coroutine-related leaks?
4. When is it acceptable to use `GlobalScope`, and how do you do it safely?
5. How do you test that a `ViewModel` properly cancels all coroutines in `onCleared()`?
6. What are the performance implications of using `WeakReference` in coroutines?
7. How do you monitor coroutine memory usage in production without LeakCanary?

## References

- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Android Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)
- [Coroutines Debug Mode](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html#debugging-coroutines-and-threads)
- [Lifecycle-aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

- [[q-coroutine-resource-cleanup--kotlin--medium|Resource cleanup in coroutines]]
- [[c-concurrency]]
- [[c-android-profiling]]