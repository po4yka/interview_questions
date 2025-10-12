---
topic: android
tags:
  - android
  - jetpack-compose
  - side-effects
  - coroutines
  - lifecycle
difficulty: hard
status: draft
---

# Side-эффекты в Compose: LaunchedEffect vs DisposableEffect

**English**: What are side-effect APIs in Compose, and when would you use LaunchedEffect vs DisposableEffect?

## Answer (EN)
**Side-effects** в Jetpack Compose — это операции, которые выполняются вне обычного цикла recomposition и могут взаимодействовать с внешним миром (API calls, database, sensors, etc.). Compose предоставляет специальные API для безопасного управления side-effects с учетом жизненного цикла.

### Проблема без Side-Effect API

```kotlin
// НЕПРАВИЛЬНО - выполнится при каждой recomposition
@Composable
fun BadExample(userId: Int) {
    val user = repository.getUser(userId) // Вызывается многократно!
    Text(user.name)
}
```

**Проблемы**:
- Выполняется при каждой recomposition
- Нет контроля жизненного цикла
- Утечки памяти
- Неконтролируемые async операции

### Основные Side-Effect API

| API | Когда использовать | Отмена при | Повторный запуск |
|-----|-------------------|-----------|------------------|
| **LaunchedEffect** | Coroutine работа | Composable покидает composition | При изменении key |
| **DisposableEffect** | Подписки/listeners | Composable покидает composition | При изменении key |
| **SideEffect** | Синхронизация состояния | Никогда | Каждая recomposition |
| **rememberCoroutineScope** | Event-driven работа | Никогда (manual) | Никогда |
| **rememberUpdatedState** | Callbacks с latest значениями | Никогда | Никогда |
| **derivedStateOf** | Вычисляемое состояние | Никогда | При изменении зависимостей |
| **produceState** | State из suspend функции | Composable покидает composition | При изменении key |

### LaunchedEffect - Запуск корутин

**Используйте** для запуска coroutine работы при входе в composition или изменении ключа.

```kotlin
@Composable
fun UserProfile(userId: Int) {
    var user by remember { mutableStateOf<User?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    // LaunchedEffect с key = userId
    // Перезапускается при изменении userId
    LaunchedEffect(userId) {
        isLoading = true
        error = null

        try {
            user = repository.getUser(userId)
        } catch (e: Exception) {
            error = e.message
        } finally {
            isLoading = false
        }
    }

    when {
        isLoading -> CircularProgressIndicator()
        error != null -> Text("Error: $error")
        user != null -> UserCard(user!!)
    }
}
```

**Поведение**:
1. При первом composition - запускается coroutine
2. При изменении `userId` - **отменяет** предыдущую coroutine, запускает новую
3. При покидании composition - **отменяет** coroutine

#### LaunchedEffect с несколькими ключами

```kotlin
@Composable
fun SearchScreen(
    query: String,
    filters: FilterState
) {
    var results by remember { mutableStateOf<List<Item>>(emptyList()) }

    // Перезапуск при изменении query ИЛИ filters
    LaunchedEffect(query, filters) {
        // Debounce для поиска
        delay(300)
        results = repository.search(query, filters)
    }

    LazyColumn {
        items(results) { item ->
            ItemCard(item)
        }
    }
}
```

#### LaunchedEffect(Unit) - один раз

```kotlin
@Composable
fun AnalyticsScreen(screenName: String) {
    // Выполнится ОДИН раз при первом composition
    LaunchedEffect(Unit) {
        analytics.logScreenView(screenName)
    }

    // UI...
}
```

#### LaunchedEffect с Flow

```kotlin
@Composable
fun OrderTracking(orderId: Int) {
    var orderStatus by remember { mutableStateOf<OrderStatus?>(null) }

    LaunchedEffect(orderId) {
        // Collect Flow до выхода из composition
        repository.observeOrderStatus(orderId)
            .collect { status ->
                orderStatus = status
            }
    }

    orderStatus?.let { status ->
        OrderStatusCard(status)
    }
}
```

### DisposableEffect - Подписки и очистка

**Используйте** для регистрации/отмены подписок, listeners, observers.

```kotlin
@Composable
fun LocationTracker() {
    var location by remember { mutableStateOf<Location?>(null) }
    val context = LocalContext.current

    DisposableEffect(Unit) {
        val locationManager = context.getSystemService<LocationManager>()!!

        val listener = object : LocationListener {
            override fun onLocationChanged(newLocation: Location) {
                location = newLocation
            }
        }

        // Регистрация listener
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            1000L,
            10f,
            listener
        )

        // ОБЯЗАТЕЛЬНО: cleanup при dispose
        onDispose {
            locationManager.removeUpdates(listener)
        }
    }

    location?.let {
        Text("Lat: ${it.latitude}, Lng: ${it.longitude}")
    }
}
```

**Ключевые особенности**:
- **onDispose** блок **обязателен**
- Вызывается при покидании composition или изменении key
- Используется для cleanup resources

#### DisposableEffect с изменяющимся ключом

```kotlin
@Composable
fun VideoPlayer(videoUrl: String) {
    val context = LocalContext.current
    val exoPlayer = remember { ExoPlayer.Builder(context).build() }

    DisposableEffect(videoUrl) {
        // Подготовка нового видео
        val mediaItem = MediaItem.fromUri(videoUrl)
        exoPlayer.setMediaItem(mediaItem)
        exoPlayer.prepare()
        exoPlayer.play()

        // Cleanup при изменении videoUrl или dispose
        onDispose {
            exoPlayer.stop()
            exoPlayer.clearMediaItems()
        }
    }

    // Release player при окончательном dispose
    DisposableEffect(Unit) {
        onDispose {
            exoPlayer.release()
        }
    }

    AndroidView(
        factory = { PlayerView(context).apply { player = exoPlayer } }
    )
}
```

#### DisposableEffect для Lifecycle observers

```kotlin
@Composable
fun LifecycleAwareComponent() {
    val lifecycleOwner = LocalLifecycleOwner.current

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_START -> {
                    // Start работа
                }
                Lifecycle.Event.ON_STOP -> {
                    // Stop работа
                }
                else -> {}
            }
        }

        lifecycleOwner.lifecycle.addObserver(observer)

        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }
}
```

### Сравнение LaunchedEffect vs DisposableEffect

```kotlin
@Composable
fun ComparisonExample(userId: Int) {
    // ✅ LaunchedEffect - для coroutine работы
    LaunchedEffect(userId) {
        val user = repository.getUser(userId) // suspend function
        // Автоматически отменится при dispose
    }

    // ✅ DisposableEffect - для подписок
    DisposableEffect(userId) {
        val listener = createListener()
        subscriptionManager.subscribe(listener)

        onDispose {
            subscriptionManager.unsubscribe(listener) // CLEANUP!
        }
    }
}
```

| Аспект | LaunchedEffect | DisposableEffect |
|--------|----------------|------------------|
| **Use case** | Coroutine работа | Подписки, listeners |
| **Cleanup** | Автоматическая отмена | Явный onDispose блок |
| **Возвращает** | Unit | DisposableEffectResult |
| **Когда cleanup** | При dispose или key change | При dispose или key change |
| **Примеры** | API calls, Flow collect | LocationManager, BroadcastReceiver |

### SideEffect - Публикация Compose state

**Используйте** для синхронизации Compose state с non-Compose кодом.

```kotlin
@Composable
fun AnalyticsExample(currentScreen: Screen) {
    // Выполнится при каждой recomposition с новым currentScreen
    SideEffect {
        analytics.setCurrentScreen(currentScreen.name)
    }
}
```

**Особенности**:
- Выполняется **после** каждой успешной recomposition
- Нет cleanup
- Нет cancellation
- Для синхронизации, не для async работы

### rememberCoroutineScope - Event-driven работа

**Используйте** для запуска coroutines из event handlers (onClick, swipe, etc.).

```kotlin
@Composable
fun RefreshableList() {
    val scope = rememberCoroutineScope()
    var items by remember { mutableStateOf<List<Item>>(emptyList()) }
    var isRefreshing by remember { mutableStateOf(false) }

    Column {
        Button(
            onClick = {
                scope.launch {
                    isRefreshing = true
                    items = repository.refreshItems()
                    isRefreshing = false
                }
            }
        ) {
            Text("Refresh")
        }

        if (isRefreshing) CircularProgressIndicator()

        LazyColumn {
            items(items) { item ->
                ItemCard(item)
            }
        }
    }
}
```

**Важно**: Scope привязан к Composable lifecycle - coroutines отменятся при dispose.

### produceState - Конвертация async в State

**Используйте** для создания State из suspend функций или Flow.

```kotlin
@Composable
fun LoadUserState(userId: Int): State<User?> {
    return produceState<User?>(initialValue = null, userId) {
        // suspend работа
        value = repository.getUser(userId)
    }
}

// Использование
@Composable
fun UserScreen(userId: Int) {
    val userState = LoadUserState(userId)

    userState.value?.let { user ->
        UserCard(user)
    } ?: CircularProgressIndicator()
}
```

**Преимущества**:
- Чистый API для async → State
- Автоматическая отмена при dispose
- Перезапуск при изменении key

#### produceState с Flow

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

// Использование
@Composable
fun OrdersScreen(viewModel: OrdersViewModel) {
    val orders by viewModel.ordersFlow.collectAsStateWithLifecycle(emptyList())

    LazyColumn {
        items(orders) { order ->
            OrderCard(order)
        }
    }
}
```

### derivedStateOf - Вычисляемое состояние

**Используйте** для оптимизации - вычисляет state только при изменении зависимостей.

```kotlin
@Composable
fun TodoList(todos: List<Todo>) {
    // НЕПРАВИЛЬНО - recomposes при любом изменении todos
    val completedCount = todos.count { it.completed }

    // ПРАВИЛЬНО - recomposes только при изменении КОЛИЧЕСТВА completed
    val completedCount by remember(todos) {
        derivedStateOf {
            todos.count { it.completed }
        }
    }

    Text("Completed: $completedCount")
}
```

### rememberUpdatedState - Всегда актуальное значение

**Используйте** для callbacks, которые должны видеть последнее значение без перезапуска effect.

```kotlin
@Composable
fun Timer(onTimeout: () -> Unit) {
    // onTimeout может измениться, но LaunchedEffect не должен перезапускаться
    val currentOnTimeout by rememberUpdatedState(onTimeout)

    LaunchedEffect(Unit) { // key = Unit - запуск один раз
        delay(5000)
        currentOnTimeout() // Вызовет ПОСЛЕДНЮЮ версию callback
    }
}
```

**Без rememberUpdatedState**:
```kotlin
// НЕПРАВИЛЬНО - будет вызвана СТАРАЯ версия callback
LaunchedEffect(Unit) {
    delay(5000)
    onTimeout() // Closure захватывает старое значение
}

// НЕПРАВИЛЬНО - перезапуск эффекта при каждом изменении
LaunchedEffect(onTimeout) {
    delay(5000)
    onTimeout() // Эффект перезапускается, delay начинается заново!
}
```

### Практические примеры

#### Пример 1: Подписка на Firebase реал-тайм обновления

```kotlin
@Composable
fun ChatMessages(chatId: String) {
    var messages by remember { mutableStateOf<List<Message>>(emptyList()) }

    DisposableEffect(chatId) {
        val listener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                messages = snapshot.children.mapNotNull {
                    it.getValue(Message::class.java)
                }
            }

            override fun onCancelled(error: DatabaseError) {}
        }

        val messagesRef = Firebase.database
            .getReference("chats/$chatId/messages")

        messagesRef.addValueEventListener(listener)

        onDispose {
            messagesRef.removeEventListener(listener)
        }
    }

    LazyColumn {
        items(messages) { message ->
            MessageBubble(message)
        }
    }
}
```

#### Пример 2: Sensor tracking с cleanup

```kotlin
@Composable
fun AccelerometerTracker() {
    var acceleration by remember { mutableStateOf<FloatArray?>(null) }
    val context = LocalContext.current

    DisposableEffect(Unit) {
        val sensorManager = context.getSystemService<SensorManager>()!!
        val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent) {
                acceleration = event.values.clone()
            }

            override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {}
        }

        sensorManager.registerListener(
            listener,
            accelerometer,
            SensorManager.SENSOR_DELAY_NORMAL
        )

        onDispose {
            sensorManager.unregisterListener(listener)
        }
    }

    acceleration?.let { acc ->
        Column {
            Text("X: ${acc[0]}")
            Text("Y: ${acc[1]}")
            Text("Z: ${acc[2]}")
        }
    }
}
```

#### Пример 3: Pagination с LaunchedEffect

```kotlin
@Composable
fun PaginatedList(viewModel: ListViewModel) {
    val items by viewModel.items.collectAsState()
    val listState = rememberLazyListState()

    // Загрузка следующей страницы при scroll к концу
    LaunchedEffect(listState) {
        snapshotFlow { listState.layoutInfo.visibleItemsInfo.lastOrNull()?.index }
            .collect { lastVisibleIndex ->
                if (lastVisibleIndex != null &&
                    lastVisibleIndex >= items.size - 5) {
                    viewModel.loadNextPage()
                }
            }
    }

    LazyColumn(state = listState) {
        items(items) { item ->
            ItemCard(item)
        }
    }
}
```

#### Пример 4: Back press handling

```kotlin
@Composable
fun BackPressHandler(
    enabled: Boolean = true,
    onBackPressed: () -> Unit
) {
    val currentOnBackPressed by rememberUpdatedState(onBackPressed)
    val backDispatcher = LocalOnBackPressedDispatcherOwner.current?.onBackPressedDispatcher

    DisposableEffect(enabled, backDispatcher) {
        val callback = object : OnBackPressedCallback(enabled) {
            override fun handleOnBackPressed() {
                currentOnBackPressed()
            }
        }

        backDispatcher?.addCallback(callback)

        onDispose {
            callback.remove()
        }
    }
}

// Использование
@Composable
fun UnsavedChangesScreen() {
    var hasUnsavedChanges by remember { mutableStateOf(false) }
    var showDialog by remember { mutableStateOf(false) }

    BackPressHandler(enabled = hasUnsavedChanges) {
        showDialog = true
    }

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false },
            title = { Text("Несохраненные изменения") },
            confirmButton = {
                TextButton(onClick = { /* Discard and exit */ }) {
                    Text("Выйти")
                }
            }
        )
    }
}
```

### Распространенные ошибки

#### Ошибка 1: Бесконечная recomposition

```kotlin
// НЕПРАВИЛЬНО
@Composable
fun BadExample() {
    var count by remember { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        count++ // Изменяет state -> recomposition -> бесконечный цикл!
    }
}

// ПРАВИЛЬНО
@Composable
fun GoodExample() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

#### Ошибка 2: Забытый onDispose

```kotlin
// НЕПРАВИЛЬНО - утечка памяти
@Composable
fun BadDisposableEffect() {
    DisposableEffect(Unit) {
        val listener = createListener()
        register(listener)
        // Забыли onDispose - listener не удалится!
    }
}

// ПРАВИЛЬНО
@Composable
fun GoodDisposableEffect() {
    DisposableEffect(Unit) {
        val listener = createListener()
        register(listener)

        onDispose {
            unregister(listener)
        }
    }
}
```

#### Ошибка 3: Неправильный ключ

```kotlin
// НЕПРАВИЛЬНО - не перезапустится при изменении userId
@Composable
fun BadKey(userId: Int) {
    var user by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(Unit) { // Запуск ОДИН раз
        user = repository.getUser(userId) // Старый userId!
    }
}

// ПРАВИЛЬНО - перезапуск при изменении userId
@Composable
fun GoodKey(userId: Int) {
    var user by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(userId) { // key = userId
        user = repository.getUser(userId)
    }
}
```

### Best Practices

**1. Используйте правильный API для задачи**

```kotlin
// LaunchedEffect для coroutine работы
LaunchedEffect(key) {
    val data = repository.getData()
}

// DisposableEffect для subscriptions
DisposableEffect(key) {
    val listener = createListener()
    onDispose { cleanup(listener) }
}

// rememberCoroutineScope для event handlers
val scope = rememberCoroutineScope()
Button(onClick = { scope.launch { /* работа */ } })
```

**2. Всегда указывайте правильные ключи**

```kotlin
// ПРАВИЛЬНО - перезапуск при изменении параметров
LaunchedEffect(userId, filter) {
    loadData(userId, filter)
}
```

**3. Cleanup в DisposableEffect обязателен**

```kotlin
// ПРАВИЛЬНО
DisposableEffect(key) {
    setup()
    onDispose { cleanup() } // ОБЯЗАТЕЛЬНО!
}
```

**4. Используйте rememberUpdatedState для callbacks**

```kotlin
// ПРАВИЛЬНО
val currentCallback by rememberUpdatedState(callback)
LaunchedEffect(Unit) {
    delay(5000)
    currentCallback() // Всегда последняя версия
}
```

**English**: Compose provides side-effect APIs for safely managing effects outside recomposition: **LaunchedEffect** - launches coroutines (auto-cancels on dispose/key change), use for API calls, Flow collection. **DisposableEffect** - manages subscriptions with mandatory onDispose cleanup, use for LocationManager, sensors, listeners. **SideEffect** - runs after each recomposition for syncing with non-Compose code. **rememberCoroutineScope** - event-driven coroutine launch (onClick). **produceState** - converts suspend/Flow to State. **derivedStateOf** - computed state (optimization). **rememberUpdatedState** - always-current values in callbacks. Key differences: LaunchedEffect auto-cleanup (coroutines), DisposableEffect explicit cleanup (subscriptions). Always specify correct keys for restart behavior.



---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations

