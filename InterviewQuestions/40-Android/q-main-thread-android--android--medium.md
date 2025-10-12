---
topic: android
tags:
  - android
  - threading
  - ui-thread
difficulty: medium
status: draft
---

# Какой основной поток выполнения приложения?

**English**: What is the main execution thread in an Android application?

## Answer (EN)
Основной поток выполнения приложения, также известный как **UI-поток (User Interface Thread)** или **Main Thread**, играет ключевую роль в функционировании Android приложения.

### Основные характеристики

#### 1. Отвечает за обработку пользовательского интерфейса

Все операции, связанные с UI, должны выполняться в главном потоке:

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Всё это выполняется в main thread
        val textView = findViewById<TextView>(R.id.textView)
        textView.text = "Hello, World!"

        button.setOnClickListener {
            // Обработка событий - тоже в main thread
            textView.text = "Button clicked"
        }
    }
}
```

#### 2. Обработка событий

Главный поток обрабатывает все события взаимодействия с пользователем:

```kotlin
// Все эти события обрабатываются в main thread
button.setOnClickListener { }
editText.addTextChangedListener { }
recyclerView.setOnScrollListener { }
```

#### 3. Запрещает длительные операции

**НЕЛЬЗЯ выполнять в main thread**:
- Сетевые запросы
- Операции с базой данных
- Тяжёлые вычисления
- Чтение/запись больших файлов

```kotlin
// - НЕПРАВИЛЬНО - блокирует UI
button.setOnClickListener {
    val data = URL("https://api.example.com/data").readText()  // NetworkOnMainThreadException!
    textView.text = data
}

// ✓ ПРАВИЛЬНО - выполнить в фоновом потоке
button.setOnClickListener {
    lifecycleScope.launch(Dispatchers.IO) {
        val data = URL("https://api.example.com/data").readText()
        withContext(Dispatchers.Main) {
            textView.text = data
        }
    }
}
```

#### 4. Event Loop (Петля событий)

Main thread работает на основе event loop, который обрабатывает события из очереди.

```kotlin
// Концептуально main thread работает так:
while (true) {
    val event = eventQueue.getNextEvent()
    handleEvent(event)
}
```

**Компоненты event loop**:

- **Looper** - управляет очередью сообщений
- **MessageQueue** - очередь событий и задач
- **Handler** - отправляет и обрабатывает сообщения

```kotlin
// Отправка задачи в main thread из фонового потока
Thread {
    // Фоновая работа
    val result = performHeavyComputation()

    // Обновление UI в main thread
    runOnUiThread {
        textView.text = result
    }
}.start()

// Или с Handler
val handler = Handler(Looper.getMainLooper())
Thread {
    val result = performHeavyComputation()
    handler.post {
        textView.text = result
    }
}.start()
```

### Правило "5 секунд"

Если main thread заблокирован более чем на 5 секунд, Android покажет диалог **"Application Not Responding" (ANR)**.

```kotlin
// - НЕПРАВИЛЬНО - вызовет ANR
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    Thread.sleep(6000)  // ANR!
}

// ✓ ПРАВИЛЬНО - длительные операции в фоне
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    lifecycleScope.launch(Dispatchers.IO) {
        performLongOperation()
    }
}
```

### Современные подходы к работе с потоками

```kotlin
// 1. Coroutines (рекомендуется)
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        fetchDataFromNetwork()
    }
    // Автоматически вернёмся в main thread
    textView.text = data
}

// 2. LiveData + ViewModel
class MyViewModel : ViewModel() {
    private val _data = MutableLiveData<String>()
    val data: LiveData<String> = _data

    fun loadData() {
        viewModelScope.launch(Dispatchers.IO) {
            val result = fetchDataFromNetwork()
            _data.postValue(result)  // Безопасно обновит UI
        }
    }
}

// 3. WorkManager (для фоновых задач)
val workRequest = OneTimeWorkRequestBuilder<MyWorker>().build()
WorkManager.getInstance(context).enqueue(workRequest)
```

**English**: Main thread (UI thread) is responsible for handling UI operations and user events in Android. It uses an event loop (Looper + MessageQueue) to process events. Long operations (network, database, heavy computations) must run on background threads to avoid ANR (Application Not Responding) dialog after 5 seconds.
