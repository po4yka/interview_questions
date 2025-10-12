---
topic: android
tags:
  - android
  - polling
  - background-tasks
  - coroutines
  - workmanager
difficulty: medium
status: draft
---

# Как реализовать polling в Android?

**English**: How to implement polling in Android?

## Answer (EN)
Polling — это техника периодического получения обновленных данных с сервера. В Android можно использовать различные подходы в зависимости от требований к частоте опроса, надежности и энергоэффективности.

### 1. Coroutines + Flow (рекомендуется для UI)

Современный подход с использованием корутин для периодического опроса.

```kotlin
// Repository с polling
class DataRepository(private val apiService: ApiService) {

    // Простой polling с фиксированным интервалом
    fun pollData(intervalMs: Long = 5000): Flow<Result<Data>> = flow {
        while (currentCoroutineContext().isActive) {
            try {
                val data = apiService.getData()
                emit(Result.success(data))
            } catch (e: Exception) {
                emit(Result.failure(e))
            }
            delay(intervalMs)
        }
    }.flowOn(Dispatchers.IO)

    // Polling с условием остановки
    fun pollUntilComplete(orderId: Int): Flow<Order> = flow {
        while (currentCoroutineContext().isActive) {
            val order = apiService.getOrder(orderId)
            emit(order)

            // Остановить polling когда заказ завершен
            if (order.status == OrderStatus.COMPLETED) {
                break
            }

            delay(3000) // 3 seconds
        }
    }.flowOn(Dispatchers.IO)

    // Polling с экспоненциальной задержкой
    fun pollWithBackoff(
        maxAttempts: Int = 5,
        initialDelayMs: Long = 1000
    ): Flow<Result<Data>> = flow {
        var attempt = 0
        var delay = initialDelayMs

        while (attempt < maxAttempts && currentCoroutineContext().isActive) {
            try {
                val data = apiService.getData()
                emit(Result.success(data))

                // Reset delay on success
                delay = initialDelayMs
                attempt = 0
            } catch (e: Exception) {
                emit(Result.failure(e))
                attempt++

                // Exponential backoff: 1s, 2s, 4s, 8s, 16s
                delay *= 2
            }

            delay(delay)
        }
    }.flowOn(Dispatchers.IO)
}

// ViewModel
class OrderViewModel(
    private val repository: DataRepository
) : ViewModel() {

    private val _orderStatus = MutableStateFlow<Order?>(null)
    val orderStatus: StateFlow<Order?> = _orderStatus.asStateFlow()

    fun startPolling(orderId: Int) {
        viewModelScope.launch {
            repository.pollUntilComplete(orderId)
                .catch { e ->
                    // Handle error
                    Log.e("OrderViewModel", "Polling error", e)
                }
                .collect { order ->
                    _orderStatus.value = order
                }
        }
    }

    fun stopPolling() {
        // Автоматически останавливается при отмене корутины
        viewModelScope.coroutineContext.cancelChildren()
    }
}

// В Fragment/Activity
class OrderFragment : Fragment() {
    private val viewModel: OrderViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Начать polling
        viewModel.startPolling(orderId = 123)

        // Наблюдать за результатами
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.orderStatus.collect { order ->
                order?.let { updateUI(it) }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Остановить polling при уничтожении view
        viewModel.stopPolling()
    }
}
```

### 2. WorkManager (для фоновых задач)

Гарантированное выполнение периодических задач даже при перезагрузке устройства.

```kotlin
// Worker для polling
class DataPollingWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val apiService = RetrofitClient.apiService

            // Получить данные
            val data = apiService.getData()

            // Сохранить в БД
            val database = AppDatabase.getInstance(applicationContext)
            database.dataDao().insertData(data)

            // Показать уведомление если есть обновления
            if (data.hasUpdates) {
                showNotification(data)
            }

            Result.success()
        } catch (e: Exception) {
            Log.e("DataPollingWorker", "Polling failed", e)

            // Retry with backoff
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }

    private fun showNotification(data: Data) {
        val notificationManager = applicationContext.getSystemService(
            Context.NOTIFICATION_SERVICE
        ) as NotificationManager

        val notification = NotificationCompat.Builder(
            applicationContext,
            "polling_channel"
        )
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("New Updates")
            .setContentText(data.message)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        notificationManager.notify(1, notification)
    }
}

// Настройка периодического polling
class PollingScheduler(private val context: Context) {

    fun startPeriodicPolling(intervalMinutes: Long = 15) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()

        val pollingRequest = PeriodicWorkRequestBuilder<DataPollingWorker>(
            repeatInterval = intervalMinutes,
            repeatIntervalTimeUnit = TimeUnit.MINUTES
        )
            .setConstraints(constraints)
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .addTag("data_polling")
            .build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            "data_polling",
            ExistingPeriodicWorkPolicy.KEEP,
            pollingRequest
        )
    }

    fun stopPolling() {
        WorkManager.getInstance(context).cancelAllWorkByTag("data_polling")
    }

    fun checkPollingStatus(): LiveData<WorkInfo> {
        return WorkManager.getInstance(context)
            .getWorkInfosForUniqueWorkLiveData("data_polling")
            .map { workInfos -> workInfos.firstOrNull() }
    }
}

// Использование
class MainActivity : AppCompatActivity() {
    private val pollingScheduler by lazy { PollingScheduler(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Начать периодический polling каждые 15 минут
        pollingScheduler.startPeriodicPolling(intervalMinutes = 15)

        // Наблюдать за статусом
        pollingScheduler.checkPollingStatus().observe(this) { workInfo ->
            when (workInfo?.state) {
                WorkInfo.State.RUNNING -> Log.d("Polling", "Running")
                WorkInfo.State.SUCCEEDED -> Log.d("Polling", "Succeeded")
                WorkInfo.State.FAILED -> Log.d("Polling", "Failed")
                else -> Unit
            }
        }
    }
}
```

### 3. Handler + Runnable (простой способ)

Для простых задач, которые выполняются пока Activity/Fragment активны.

```kotlin
class PollingHandler {
    private val handler = Handler(Looper.getMainLooper())
    private var pollingRunnable: Runnable? = null

    fun startPolling(
        intervalMs: Long = 5000,
        onPoll: suspend () -> Unit
    ) {
        pollingRunnable = object : Runnable {
            override fun run() {
                // Выполнить polling в корутине
                CoroutineScope(Dispatchers.IO).launch {
                    try {
                        onPoll()
                    } catch (e: Exception) {
                        Log.e("PollingHandler", "Error", e)
                    }
                }

                // Запланировать следующий запуск
                handler.postDelayed(this, intervalMs)
            }
        }

        // Запустить первый раз
        handler.post(pollingRunnable!!)
    }

    fun stopPolling() {
        pollingRunnable?.let { handler.removeCallbacks(it) }
        pollingRunnable = null
    }
}

// Использование в Fragment
class StatusFragment : Fragment() {
    private val pollingHandler = PollingHandler()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Начать polling
        pollingHandler.startPolling(intervalMs = 5000) {
            val status = repository.getStatus()
            withContext(Dispatchers.Main) {
                updateUI(status)
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        pollingHandler.stopPolling()
    }
}
```

### 4. AlarmManager (для точных интервалов)

Для задач, которые требуют выполнения в точное время.

```kotlin
class AlarmPollingScheduler(private val context: Context) {

    fun schedulePolling(intervalMinutes: Long = 15) {
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager

        val intent = Intent(context, PollingBroadcastReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val intervalMillis = TimeUnit.MINUTES.toMillis(intervalMinutes)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            // Exact alarm (Android 6.0+)
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                System.currentTimeMillis() + intervalMillis,
                pendingIntent
            )
        } else {
            // Repeating alarm
            alarmManager.setRepeating(
                AlarmManager.RTC_WAKEUP,
                System.currentTimeMillis() + intervalMillis,
                intervalMillis,
                pendingIntent
            )
        }
    }

    fun cancelPolling() {
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val intent = Intent(context, PollingBroadcastReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            intent,
            PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
        )

        pendingIntent?.let { alarmManager.cancel(it) }
    }
}

// BroadcastReceiver
class PollingBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Запустить работу в фоне
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val data = RetrofitClient.apiService.getData()
                // Обработать данные
                processData(data)

                // Запланировать следующий опрос
                AlarmPollingScheduler(context).schedulePolling()
            } catch (e: Exception) {
                Log.e("PollingReceiver", "Error", e)
            }
        }
    }
}
```

### 5. RxJava Observable.interval (альтернатива)

```kotlin
class RxPollingManager {
    private var disposable: Disposable? = null

    fun startPolling(
        intervalSeconds: Long = 5,
        apiService: ApiService
    ): Observable<Data> {
        return Observable.interval(0, intervalSeconds, TimeUnit.SECONDS)
            .flatMap {
                apiService.getDataRx()
                    .toObservable()
                    .onErrorResumeNext { error: Throwable ->
                        Observable.error(error)
                    }
            }
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
    }

    fun subscribe(
        intervalSeconds: Long,
        apiService: ApiService,
        onNext: (Data) -> Unit,
        onError: (Throwable) -> Unit
    ) {
        disposable = startPolling(intervalSeconds, apiService)
            .subscribe(onNext, onError)
    }

    fun stop() {
        disposable?.dispose()
    }
}
```

### 6. Smart Polling с адаптивными интервалами

```kotlin
class SmartPollingManager(
    private val repository: DataRepository
) {
    private var currentInterval = 5000L // Start with 5 seconds
    private val minInterval = 1000L
    private val maxInterval = 60000L

    fun startAdaptivePolling(): Flow<Data> = flow {
        while (currentCoroutineContext().isActive) {
            try {
                val data = repository.getData()
                emit(data)

                // Adjust interval based on data changes
                if (data.hasChanges) {
                    // Data is changing, poll more frequently
                    currentInterval = max(minInterval, currentInterval / 2)
                } else {
                    // No changes, slow down polling
                    currentInterval = min(maxInterval, currentInterval * 2)
                }
            } catch (e: Exception) {
                // On error, increase interval
                currentInterval = min(maxInterval, currentInterval * 2)
                throw e
            }

            delay(currentInterval)
        }
    }.flowOn(Dispatchers.IO)
}
```

### 7. Polling с WebSocket fallback

```kotlin
class DataSyncManager(
    private val apiService: ApiService,
    private val webSocketClient: WebSocketClient
) {
    private var useWebSocket = true

    fun startDataSync(): Flow<Data> = flow {
        if (useWebSocket) {
            try {
                // Try WebSocket first
                webSocketClient.observeData()
                    .collect { emit(it) }
            } catch (e: Exception) {
                // Fallback to polling
                useWebSocket = false
                pollData().collect { emit(it) }
            }
        } else {
            pollData().collect { emit(it) }
        }
    }

    private fun pollData(): Flow<Data> = flow {
        while (currentCoroutineContext().isActive) {
            val data = apiService.getData()
            emit(data)
            delay(5000)
        }
    }
}
```

### Best Practices

**1. Использовать lifecycle-aware компоненты**

```kotlin
class PollingViewModel : ViewModel() {
    private var pollingJob: Job? = null

    fun startPolling() {
        pollingJob = viewModelScope.launch {
            repository.pollData()
                .collect { data ->
                    // Process data
                }
        }
    }

    fun stopPolling() {
        pollingJob?.cancel()
    }

    override fun onCleared() {
        super.onCleared()
        stopPolling()
    }
}
```

**2. Обработка ошибок и retry**

```kotlin
fun pollWithRetry(): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        try {
            val data = apiService.getData()
            emit(data)
            delay(5000)
        } catch (e: Exception) {
            // Log error but continue polling
            Log.e("Polling", "Error: ${e.message}")
            delay(10000) // Wait longer after error
        }
    }
}
```

**3. Проверка сетевого подключения**

```kotlin
fun pollWhenOnline(context: Context): Flow<Data> = flow {
    while (currentCoroutineContext().isActive) {
        if (isNetworkAvailable(context)) {
            try {
                val data = apiService.getData()
                emit(data)
            } catch (e: Exception) {
                // Handle error
            }
        }
        delay(5000)
    }
}
```

### Сравнительная таблица

| Метод | Use Case | Преимущества | Недостатки |
|-------|----------|--------------|------------|
| **Coroutines + Flow** | UI-bound polling | Простота, lifecycle-aware | Работает только пока app активно |
| **WorkManager** | Фоновые задачи | Гарантированное выполнение | Минимум 15 минут интервал |
| **Handler** | Простые задачи | Легкость реализации | Ручное управление lifecycle |
| **AlarmManager** | Точные интервалы | Работает в фоне | Battery drain |
| **WebSocket** | Real-time данные | Мгновенные обновления | Сложность реализации |

**English**: Polling implementation methods: **Coroutines + Flow** (recommended for UI, lifecycle-aware), **WorkManager** (background tasks, guaranteed execution, min 15min interval), **Handler + Runnable** (simple tasks), **AlarmManager** (exact timing). Best practices: adaptive intervals, exponential backoff on errors, check network availability, lifecycle-aware cancellation. Use `flow { while(isActive) { fetchData(); delay(interval) } }` pattern for coroutines. WorkManager for reliable background polling with constraints.
