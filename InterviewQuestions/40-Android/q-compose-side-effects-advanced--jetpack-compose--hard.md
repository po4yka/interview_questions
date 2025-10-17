---
id: "20251015082237388"
title: "Compose Side Effects Advanced / Побочные эффекты Compose продвинутый уровень"
topic: jetpack-compose
difficulty: hard
status: draft
created: 2025-10-15
tags: - jetpack-compose
  - side-effects
  - lifecycle
  - launched-effect
---
# Compare Side Effect APIs and Implement Location Tracking

**English**: Compare LaunchedEffect, DisposableEffect, SideEffect, and produceState. When should you use each? Implement a location tracking composable.

**Russian**: Сравните LaunchedEffect, DisposableEffect, SideEffect и produceState. Когда использовать каждый? Реализуйте composable для отслеживания местоположения.

## Answer (EN)

Jetpack Compose provides multiple side-effect APIs, each designed for specific use cases. Understanding when to use each is crucial for building efficient, leak-free Compose applications.

### Side Effect APIs Comparison

| API | Context Object | Cleanup | Use Case | Restart Trigger |
|-----|----------------|---------|----------|-----------------|
| **LaunchedEffect** | CoroutineScope | Automatic cancellation | Coroutine-based async work | Key change or leave composition |
| **DisposableEffect** | No coroutine scope | Manual onDispose | Subscriptions, listeners | Key change or leave composition |
| **SideEffect** | No scope | No cleanup | Sync state with non-Compose | Every successful recomposition |
| **produceState** | CoroutineScope | Automatic cancellation | Convert async to State | Key change or leave composition |

### LaunchedEffect - Coroutine Side Effects

**When to use**: Launch coroutines for suspend functions, Flow collection, or delayed operations.

**Characteristics**:
- Runs in a coroutine scope tied to composition lifecycle
- Automatically cancels when leaving composition or keys change
- Restarts when any key parameter changes
- Perfect for API calls, database operations, Flow collection

```kotlin
@Composable
fun UserDataScreen(userId: String) {
    var userData by remember { mutableStateOf<UserData?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(userId) {
        // Cancels previous coroutine if userId changes
        isLoading = true
        error = null

        try {
            // Suspend function call
            userData = repository.getUserData(userId)
        } catch (e: Exception) {
            error = e.message
        } finally {
            isLoading = false
        }
    }

    when {
        isLoading -> LoadingIndicator()
        error != null -> ErrorView(error!!)
        userData != null -> UserContent(userData!!)
    }
}
```

**Multiple keys example**:
```kotlin
@Composable
fun SearchWithFilters(
    query: String,
    filters: FilterOptions
) {
    var results by remember { mutableStateOf<List<Item>>(emptyList()) }

    // Restarts when EITHER query OR filters change
    LaunchedEffect(query, filters) {
        delay(300) // Debounce
        results = searchRepository.search(query, filters)
    }

    ResultsList(results)
}
```

### DisposableEffect - Subscription Management

**When to use**: Register/unregister listeners, observers, or any resource requiring explicit cleanup.

**Characteristics**:
- Requires explicit onDispose block (mandatory)
- onDispose called when leaving composition or keys change
- No automatic coroutine support
- Perfect for LocationManager, BroadcastReceiver, lifecycle observers

```kotlin
@Composable
fun SensorMonitor(sensorType: Int) {
    var sensorData by remember { mutableStateOf<FloatArray?>(null) }
    val context = LocalContext.current

    DisposableEffect(sensorType) {
        val sensorManager = context.getSystemService<SensorManager>()!!
        val sensor = sensorManager.getDefaultSensor(sensorType)

        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent) {
                sensorData = event.values.clone()
            }
            override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {}
        }

        sensorManager.registerListener(
            listener,
            sensor,
            SensorManager.SENSOR_DELAY_NORMAL
        )

        // MANDATORY: cleanup on dispose
        onDispose {
            sensorManager.unregisterListener(listener)
        }
    }

    SensorDisplay(sensorData)
}
```

### SideEffect - State Synchronization

**When to use**: Publish Compose state to non-Compose code after successful recomposition.

**Characteristics**:
- Runs after every successful recomposition
- No cleanup or cancellation
- Executes synchronously
- Perfect for analytics, non-Compose state sync

```kotlin
@Composable
fun ScreenWithAnalytics(screenName: String, userId: String) {
    // Runs after EVERY recomposition with updated values
    SideEffect {
        analytics.logScreenView(
            screen = screenName,
            userId = userId
        )
    }

    ScreenContent()
}
```

**Important**: Use sparingly - runs on every recomposition!

### produceState - Async to State Conversion

**When to use**: Convert suspend functions or Flows into State objects.

**Characteristics**:
- Returns State<T>
- Coroutine scope provided automatically
- Cancels on dispose or key change
- Clean API for async → State transformation

```kotlin
@Composable
fun loadNetworkImage(url: String): State<ImageBitmap?> {
    return produceState<ImageBitmap?>(initialValue = null, url) {
        // Runs in coroutine, cancels on dispose
        value = imageLoader.load(url)
    }
}

// Usage
@Composable
fun NetworkImage(url: String) {
    val imageState = loadNetworkImage(url)

    imageState.value?.let { bitmap ->
        Image(bitmap, contentDescription = null)
    } ?: CircularProgressIndicator()
}
```

**With Flow**:
```kotlin
@Composable
fun <T> Flow<T>.collectAsStateWithLifecycle(
    initialValue: T,
    lifecycle: Lifecycle = LocalLifecycleOwner.current.lifecycle,
    minActiveState: Lifecycle.State = Lifecycle.State.STARTED
): State<T> {
    return produceState(initialValue, this, lifecycle, minActiveState) {
        lifecycle.repeatOnLifecycle(minActiveState) {
            collect { value = it }
        }
    }
}
```

### Decision Tree: Which Side Effect to Use?

```
Do you need coroutines?
 YES
   Converting to State?
     Use produceState
   General async work?
      Use LaunchedEffect

 NO
    Need cleanup?
      Use DisposableEffect
    Just syncing state?
       Use SideEffect
```

### Complete Location Tracking Implementation

```kotlin
data class LocationState(
    val latitude: Double = 0.0,
    val longitude: Double = 0.0,
    val accuracy: Float = 0f,
    val timestamp: Long = 0L,
    val isTracking: Boolean = false,
    val error: String? = null
)

@Composable
fun LocationTracker(
    updateIntervalMs: Long = 5000L,
    minDistanceMeters: Float = 10f,
    onLocationUpdate: (LocationState) -> Unit = {}
) {
    var locationState by remember { mutableStateOf(LocationState()) }
    val context = LocalContext.current

    // Permission check
    val hasLocationPermission = remember {
        ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
    }

    DisposableEffect(hasLocationPermission, updateIntervalMs, minDistanceMeters) {
        if (!hasLocationPermission) {
            locationState = locationState.copy(
                error = "Location permission not granted",
                isTracking = false
            )
            onDispose { }
            return@DisposableEffect
        }

        val locationManager = context.getSystemService<LocationManager>()

        if (locationManager == null) {
            locationState = locationState.copy(
                error = "LocationManager not available",
                isTracking = false
            )
            onDispose { }
            return@DisposableEffect
        }

        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                val newState = LocationState(
                    latitude = location.latitude,
                    longitude = location.longitude,
                    accuracy = location.accuracy,
                    timestamp = location.time,
                    isTracking = true,
                    error = null
                )
                locationState = newState
                onLocationUpdate(newState)
            }

            @Deprecated("Deprecated in Java")
            override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}

            override fun onProviderEnabled(provider: String) {
                locationState = locationState.copy(
                    error = null,
                    isTracking = true
                )
            }

            override fun onProviderDisabled(provider: String) {
                locationState = locationState.copy(
                    error = "Location provider disabled",
                    isTracking = false
                )
            }
        }

        try {
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                updateIntervalMs,
                minDistanceMeters,
                listener
            )

            // Get last known location immediately
            locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER)?.let { location ->
                locationState = LocationState(
                    latitude = location.latitude,
                    longitude = location.longitude,
                    accuracy = location.accuracy,
                    timestamp = location.time,
                    isTracking = true,
                    error = null
                )
            }
        } catch (e: SecurityException) {
            locationState = locationState.copy(
                error = "Security exception: ${e.message}",
                isTracking = false
            )
        }

        // CLEANUP: Unregister listener when effect disposes
        onDispose {
            try {
                locationManager.removeUpdates(listener)
            } catch (e: Exception) {
                // Handle cleanup errors silently
            }
        }
    }

    // UI display
    LocationDisplay(locationState)
}

@Composable
private fun LocationDisplay(state: LocationState) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Location Tracker",
                style = MaterialTheme.typography.titleLarge
            )

            Divider()

            if (state.error != null) {
                Text(
                    text = "Error: ${state.error}",
                    color = MaterialTheme.colorScheme.error
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Status:")
                Text(
                    text = if (state.isTracking) "Tracking" else "Not tracking",
                    color = if (state.isTracking) Color.Green else Color.Red
                )
            }

            if (state.isTracking) {
                Text("Latitude: ${state.latitude}")
                Text("Longitude: ${state.longitude}")
                Text("Accuracy: ${state.accuracy}m")
                Text(
                    "Last update: ${
                        SimpleDateFormat("HH:mm:ss", Locale.getDefault())
                            .format(Date(state.timestamp))
                    }"
                )
            }
        }
    }
}

// Usage example with permission handling
@Composable
fun LocationScreen() {
    var showPermissionRationale by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        showPermissionRationale = !isGranted
    }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
    }

    Column(modifier = Modifier.fillMaxSize()) {
        LocationTracker(
            updateIntervalMs = 3000L,
            minDistanceMeters = 5f,
            onLocationUpdate = { location ->
                Log.d("Location", "New location: ${location.latitude}, ${location.longitude}")
            }
        )

        if (showPermissionRationale) {
            PermissionRationale(
                onRequestPermission = {
                    permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
                }
            )
        }
    }
}

// Пример использования с обработкой разрешений
@Composable
fun LocationScreen() {
    var showPermissionRationale by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        showPermissionRationale = !isGranted
    }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
    }

    Column(modifier = Modifier.fillMaxSize()) {
        LocationTracker(
            updateIntervalMs = 3000L,
            minDistanceMeters = 5f,
            onLocationUpdate = { location ->
                Log.d("Location", "Новое местоположение: ${location.latitude}, ${location.longitude}")
            }
        )

        if (showPermissionRationale) {
            PermissionRationale(
                onRequestPermission = {
                    permissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
                }
            )
        }
    }
}
```

### Advanced Example: Combining Multiple Side Effects

```kotlin
@Composable
fun RealtimeChatMessage(messageId: String) {
    var message by remember { mutableStateOf<Message?>(null) }
    var isOnline by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    // LaunchedEffect: Load message data
    LaunchedEffect(messageId) {
        message = repository.getMessage(messageId)
    }

    // DisposableEffect: Subscribe to real-time updates
    DisposableEffect(messageId) {
        val listener = object : MessageListener {
            override fun onMessageUpdated(updatedMessage: Message) {
                message = updatedMessage
            }
        }

        firestore.collection("messages")
            .document(messageId)
            .addSnapshotListener(listener)

        onDispose {
            // Cleanup listener
            listener.remove()
        }
    }

    // SideEffect: Track message views
    SideEffect {
        message?.let {
            analytics.logEvent("message_viewed", bundleOf("id" to messageId))
        }
    }

    // produceState: Monitor connectivity
    val connectivityState = produceConnectivityState()

    MessageView(message, connectivityState.value)
}

@Composable
fun produceConnectivityState(): State<Boolean> {
    val context = LocalContext.current
    return produceState(initialValue = false) {
        val connectivityManager = context.getSystemService<ConnectivityManager>()!!
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                value = true
            }
            override fun onLost(network: Network) {
                value = false
            }
        }

        connectivityManager.registerDefaultNetworkCallback(callback)

        awaitDispose {
            connectivityManager.unregisterNetworkCallback(callback)
        }
    }
}
```

### Common Pitfalls

**1. Forgetting onDispose in DisposableEffect**
```kotlin
// WRONG - Memory leak!
DisposableEffect(Unit) {
    val listener = createListener()
    register(listener)
    // Missing onDispose!
}

// CORRECT
DisposableEffect(Unit) {
    val listener = createListener()
    register(listener)
    onDispose { unregister(listener) }
}
```

**2. Wrong keys causing unnecessary restarts**
```kotlin
// WRONG - Restarts on every recomposition
LaunchedEffect(viewModel) {
    loadData()
}

// CORRECT - Restarts only when needed
LaunchedEffect(viewModel.userId) {
    loadData()
}
```

**3. Overusing SideEffect**
```kotlin
// WRONG - Runs every recomposition (expensive!)
SideEffect {
    heavyComputation()
}

// CORRECT - Use LaunchedEffect with proper keys
LaunchedEffect(key) {
    heavyComputation()
}
```

### Best Practices

1. **Choose the right API** based on the decision tree
2. **Always specify correct keys** for restart behavior
3. **DisposableEffect cleanup is mandatory** - no exceptions
4. **Use rememberUpdatedState** for callbacks that shouldn't restart effects
5. **Prefer produceState** for clean async → State conversion
6. **SideEffect is for synchronization**, not async work
7. **Test side effects** with proper cleanup verification

## Ответ (RU)

Jetpack Compose предоставляет несколько API для side-эффектов, каждый разработан для конкретных случаев использования. Понимание когда использовать каждый критически важно для построения эффективных приложений без утечек памяти.

### Сравнение Side Effect API

| API | Контекст | Очистка | Случай использования | Триггер перезапуска |
|-----|----------|---------|---------------------|---------------------|
| **LaunchedEffect** | CoroutineScope | Автоматическая отмена | Асинхронная работа с корутинами | Изменение ключа или выход из composition |
| **DisposableEffect** | Нет coroutine scope | Ручной onDispose | Подписки, слушатели | Изменение ключа или выход из composition |
| **SideEffect** | Нет scope | Нет очистки | Синхронизация с не-Compose кодом | Каждая успешная recomposition |
| **produceState** | CoroutineScope | Автоматическая отмена | Конвертация async в State | Изменение ключа или выход из composition |

### LaunchedEffect - Побочные эффекты с корутинами

**Когда использовать**: Запуск корутин для suspend функций, сбора Flow, отложенных операций.

**Характеристики**:
- Выполняется в coroutine scope, привязанном к lifecycle composition
- Автоматически отменяется при выходе из composition или изменении ключей
- Перезапускается когда любой параметр-ключ изменяется
- Идеально для API вызовов, операций с БД, сбора Flow

```kotlin
@Composable
fun UserDataScreen(userId: String) {
    var userData by remember { mutableStateOf<UserData?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(userId) {
        // Отменяет предыдущую корутину если userId изменился
        isLoading = true
        error = null

        try {
            // Вызов suspend функции
            userData = repository.getUserData(userId)
        } catch (e: Exception) {
            error = e.message
        } finally {
            isLoading = false
        }
    }

    when {
        isLoading -> LoadingIndicator()
        error != null -> ErrorView(error!!)
        userData != null -> UserContent(userData!!)
    }
}
```

**Пример с несколькими ключами**:
```kotlin
@Composable
fun SearchWithFilters(
    query: String,
    filters: FilterOptions
) {
    var results by remember { mutableStateOf<List<Item>>(emptyList()) }

    // Перезапускается когда query ИЛИ filters изменяются
    LaunchedEffect(query, filters) {
        delay(300) // Debounce
        results = searchRepository.search(query, filters)
    }

    ResultsList(results)
}
```

### DisposableEffect - Управление подписками

**Когда использовать**: Регистрация/отмена слушателей, наблюдателей или любых ресурсов требующих явной очистки.

**Характеристики**:
- Требует явного блока onDispose (обязательно)
- onDispose вызывается при выходе из composition или изменении ключей
- Нет автоматической поддержки корутин
- Идеально для LocationManager, BroadcastReceiver, lifecycle наблюдателей

```kotlin
@Composable
fun SensorMonitor(sensorType: Int) {
    var sensorData by remember { mutableStateOf<FloatArray?>(null) }
    val context = LocalContext.current

    DisposableEffect(sensorType) {
        val sensorManager = context.getSystemService<SensorManager>()!!
        val sensor = sensorManager.getDefaultSensor(sensorType)

        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent) {
                sensorData = event.values.clone()
            }
            override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {}
        }

        sensorManager.registerListener(
            listener,
            sensor,
            SensorManager.SENSOR_DELAY_NORMAL
        )

        // ОБЯЗАТЕЛЬНО: очистка при dispose
        onDispose {
            sensorManager.unregisterListener(listener)
        }
    }

    SensorDisplay(sensorData)
}
```

### SideEffect - Синхронизация состояния

**Когда использовать**: Публикация Compose состояния в не-Compose код после успешной recomposition.

**Характеристики**:
- Выполняется после каждой успешной recomposition
- Нет очистки или отмены
- Выполняется синхронно
- Идеально для аналитики, синхронизации с не-Compose состоянием

```kotlin
@Composable
fun ScreenWithAnalytics(screenName: String, userId: String) {
    // Выполняется после КАЖДОЙ recomposition с обновленными значениями
    SideEffect {
        analytics.logScreenView(
            screen = screenName,
            userId = userId
        )
    }

    ScreenContent()
}
```

**Важно**: Используйте экономно - выполняется при каждой recomposition!

### produceState - Конвертация Async в State

**Когда использовать**: Конвертация suspend функций или Flows в объекты State.

**Характеристики**:
- Возвращает State<T>
- Coroutine scope предоставляется автоматически
- Отменяется при dispose или изменении ключа
- Чистый API для трансформации async → State

```kotlin
@Composable
fun loadNetworkImage(url: String): State<ImageBitmap?> {
    return produceState<ImageBitmap?>(initialValue = null, url) {
        // Выполняется в корутине, отменяется при dispose
        value = imageLoader.load(url)
    }
}

// Использование
@Composable
fun NetworkImage(url: String) {
    val imageState = loadNetworkImage(url)

    imageState.value?.let { bitmap ->
        Image(bitmap, contentDescription = null)
    } ?: CircularProgressIndicator()
}
```

**С Flow**:
```kotlin
@Composable
fun <T> Flow<T>.collectAsStateWithLifecycle(
    initialValue: T,
    lifecycle: Lifecycle = LocalLifecycleOwner.current.lifecycle,
    minActiveState: Lifecycle.State = Lifecycle.State.STARTED
): State<T> {
    return produceState(initialValue, this, lifecycle, minActiveState) {
        lifecycle.repeatOnLifecycle(minActiveState) {
            collect { value = it }
        }
    }
}
```

### Дерево решений: Какой Side Effect использовать?

```
Нужны корутины?
 ДА
   Конвертация в State?
     Используйте produceState
   Общая async работа?
      Используйте LaunchedEffect

 НЕТ
    Нужна очистка?
      Используйте DisposableEffect
    Просто синхронизация state?
       Используйте SideEffect
```

### Полная реализация отслеживания местоположения

```kotlin
data class LocationState(
    val latitude: Double = 0.0,
    val longitude: Double = 0.0,
    val accuracy: Float = 0f,
    val timestamp: Long = 0L,
    val isTracking: Boolean = false,
    val error: String? = null
)

@Composable
fun LocationTracker(
    updateIntervalMs: Long = 5000L,
    minDistanceMeters: Float = 10f,
    onLocationUpdate: (LocationState) -> Unit = {}
) {
    var locationState by remember { mutableStateOf(LocationState()) }
    val context = LocalContext.current

    // Проверка разрешений
    val hasLocationPermission = remember {
        ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
    }

    DisposableEffect(hasLocationPermission, updateIntervalMs, minDistanceMeters) {
        if (!hasLocationPermission) {
            locationState = locationState.copy(
                error = "Разрешение на местоположение не предоставлено",
                isTracking = false
            )
            onDispose { }
            return@DisposableEffect
        }

        val locationManager = context.getSystemService<LocationManager>()

        if (locationManager == null) {
            locationState = locationState.copy(
                error = "LocationManager недоступен",
                isTracking = false
            )
            onDispose { }
            return@DisposableEffect
        }

        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                val newState = LocationState(
                    latitude = location.latitude,
                    longitude = location.longitude,
                    accuracy = location.accuracy,
                    timestamp = location.time,
                    isTracking = true,
                    error = null
                )
                locationState = newState
                onLocationUpdate(newState)
            }

            @Deprecated("Deprecated in Java")
            override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}

            override fun onProviderEnabled(provider: String) {
                locationState = locationState.copy(
                    error = null,
                    isTracking = true
                )
            }

            override fun onProviderDisabled(provider: String) {
                locationState = locationState.copy(
                    error = "Провайдер местоположения отключен",
                    isTracking = false
                )
            }
        }

        try {
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                updateIntervalMs,
                minDistanceMeters,
                listener
            )

            // Получить последнее известное местоположение сразу
            locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER)?.let { location ->
                locationState = LocationState(
                    latitude = location.latitude,
                    longitude = location.longitude,
                    accuracy = location.accuracy,
                    timestamp = location.time,
                    isTracking = true,
                    error = null
                )
            }
        } catch (e: SecurityException) {
            locationState = locationState.copy(
                error = "Ошибка безопасности: ${e.message}",
                isTracking = false
            )
        }

        // ОЧИСТКА: Отменить регистрацию слушателя когда эффект завершается
        onDispose {
            try {
                locationManager.removeUpdates(listener)
            } catch (e: Exception) {
                // Обрабатываем ошибки очистки без вывода
            }
        }
    }

    // Отображение UI
    LocationDisplay(locationState)
}

@Composable
private fun LocationDisplay(state: LocationState) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Отслеживание местоположения",
                style = MaterialTheme.typography.titleLarge
            )

            Divider()

            if (state.error != null) {
                Text(
                    text = "Ошибка: ${state.error}",
                    color = MaterialTheme.colorScheme.error
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Статус:")
                Text(
                    text = if (state.isTracking) "Отслеживание" else "Не отслеживается",
                    color = if (state.isTracking) Color.Green else Color.Red
                )
            }

            if (state.isTracking) {
                Text("Широта: ${state.latitude}")
                Text("Долгота: ${state.longitude}")
                Text("Точность: ${state.accuracy}м")
                Text(
                    "Последнее обновление: ${
                        SimpleDateFormat("HH:mm:ss", Locale.getDefault())
                            .format(Date(state.timestamp))
                    }"
                )
            }
        }
    }
}
```

### Продвинутый пример: Комбинирование нескольких Side Effects

```kotlin
@Composable
fun RealtimeChatMessage(messageId: String) {
    var message by remember { mutableStateOf<Message?>(null) }
    var isOnline by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    // LaunchedEffect: Загрузка данных сообщения
    LaunchedEffect(messageId) {
        message = repository.getMessage(messageId)
    }

    // DisposableEffect: Подписка на real-time обновления
    DisposableEffect(messageId) {
        val listener = object : MessageListener {
            override fun onMessageUpdated(updatedMessage: Message) {
                message = updatedMessage
            }
        }

        firestore.collection("messages")
            .document(messageId)
            .addSnapshotListener(listener)

        onDispose {
            // Очистка слушателя
            listener.remove()
        }
    }

    // SideEffect: Отслеживание просмотров сообщения
    SideEffect {
        message?.let {
            analytics.logEvent("message_viewed", bundleOf("id" to messageId))
        }
    }

    // produceState: Мониторинг подключения
    val connectivityState = produceConnectivityState()

    MessageView(message, connectivityState.value)
}

@Composable
fun produceConnectivityState(): State<Boolean> {
    val context = LocalContext.current
    return produceState(initialValue = false) {
        val connectivityManager = context.getSystemService<ConnectivityManager>()!!
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                value = true
            }
            override fun onLost(network: Network) {
                value = false
            }
        }

        connectivityManager.registerDefaultNetworkCallback(callback)

        awaitDispose {
            connectivityManager.unregisterNetworkCallback(callback)
        }
    }
}
```

### Распространенные ошибки

**1. Забытый onDispose в DisposableEffect**
```kotlin
// НЕПРАВИЛЬНО - Утечка памяти!
DisposableEffect(Unit) {
    val listener = createListener()
    register(listener)
    // Отсутствует onDispose!
}

// ПРАВИЛЬНО
DisposableEffect(Unit) {
    val listener = createListener()
    register(listener)
    onDispose { unregister(listener) }
}
```

**2. Неправильные ключи вызывают ненужные перезапуски**
```kotlin
// НЕПРАВИЛЬНО - Перезапускается при каждой recomposition
LaunchedEffect(viewModel) {
    loadData()
}

// ПРАВИЛЬНО - Перезапускается только когда нужно
LaunchedEffect(viewModel.userId) {
    loadData()
}
```

**3. Чрезмерное использование SideEffect**
```kotlin
// НЕПРАВИЛЬНО - Выполняется каждую recomposition (дорого!)
SideEffect {
    heavyComputation()
}

// ПРАВИЛЬНО - Используйте LaunchedEffect с правильными ключами
LaunchedEffect(key) {
    heavyComputation()
}
```

### Лучшие практики

1. **Выбирайте правильный API** на основе дерева решений
2. **Всегда указывайте правильные ключи** для поведения перезапуска
3. **Очистка DisposableEffect обязательна** - без исключений
4. **Используйте rememberUpdatedState** для callback'ов, которые не должны перезапускать эффекты
5. **Предпочитайте produceState** для чистой конвертации async → State
6. **SideEffect для синхронизации**, не для async работы
7. **Тестируйте side effects** с проверкой корректной очистки


---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Slot table internals
- [[q-compose-performance-optimization--android--hard]] - Performance optimization

