---
id: kotlin-170
title: "Coroutines and side effects in Jetpack Compose / Корутины и side effects в Jetpack Compose"
aliases: [Coroutines Side Effects Compose, Корутины side effects Jetpack Compose]
topic: kotlin
subtopics: [coroutines, c-jetpack-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-15
updated: 2025-11-09
tags: [android, coroutines, difficulty/medium, jetpack-compose, kotlin, launchedeffect, lifecycle, rememberCoroutineScope, side-effects, state-management]
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-testing-stateflow-sharedflow--kotlin--medium]
---
# Вопрос (RU)
> Что такое side effects в Jetpack Compose и как с ними интегрируются корутины? Объясните `LaunchedEffect`, `rememberCoroutineScope`, `DisposableEffect`, `produceState` и другие обработчики побочных эффектов. Когда какой использовать? Приведите production-примеры загрузки данных, анимаций, обработки событий и коллекции `Flow` с корректным управлением жизненным циклом и стратегиями тестирования.

# Question (EN)
> What are side effects in Jetpack Compose and how do coroutines integrate with them? Explain `LaunchedEffect`, `rememberCoroutineScope`, `DisposableEffect`, `produceState`, and other side effect handlers. When should you use each? Provide production examples of data loading, animations, event handling, and `Flow` collection with proper lifecycle management and testing strategies.

## Ответ (RU)

Side effects в Compose — это операции, которые выходят за рамки composable-функции и влияют на состояние приложения вне самой композиции. Корутины являются ключевым механизмом управления асинхронными side effects в Compose.

#### 1. Что такое Side Effects?

**Определение:**
- Side effects — это операции, происходящие **вне** чистой композиции.
- Примеры: сетевые вызовы, запросы к БД, навигация, аналитика, взаимодействие с платформенными API.
- Они должны быть корректно привязаны к жизненному циклу композиции.
- Должны быть **предсказуемыми** и **управляемыми**.

**Почему side effects важны:**

```kotlin
// ПЛОХО: Side effect выполняется при каждой рекомпозиции
@Composable
fun BadExample() {
    // Это выполняется каждый раз при рекомпозиции!
    analyticsLogger.log("Экран просмотрен")

    Text("Привет")
}

// ХОРОШО: Side effect выполняется один раз
@Composable
fun GoodExample() {
    LaunchedEffect(Unit) {
        // Это выполняется только один раз при входе в композицию
        analyticsLogger.log("Экран просмотрен")
    }

    Text("Привет")
}
```

#### 2. `LaunchedEffect` — корутины, привязанные к композиции

**Назначение:** Запускает корутину, привязанную к жизненному циклу composable.

**Ключевые свойства:**
- Запускается при входе composable в композицию.
- Отменяется при выходе composable из композиции.
- Перезапускается при изменении ключей.

**Базовый пример:**

```kotlin
@Composable
fun UserProfileScreen(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }
    var isLoading by remember { mutableStateOf(true) }

    LaunchedEffect(userId) { // Ключ: userId
        isLoading = true
        try {
            user = userRepository.getUser(userId)
        } finally {
            isLoading = false
        }
    }

    when {
        isLoading -> LoadingIndicator()
        user != null -> UserProfile(user!!)
        else -> ErrorMessage()
    }
}
```

**Работа с ключами:**

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<String>>(emptyList()) }

    LaunchedEffect(query) {
        // Отменяет предыдущий поиск и перезапускается при изменении query
        delay(300) // debounce
        results = searchRepository.search(query)
    }

    Column {
        TextField(
            value = query,
            onValueChange = { query = it }
        )
        LazyColumn {
            items(results) { result ->
                Text(result)
            }
        }
    }
}
```

```kotlin
@Composable
fun DataSync(userId: String, syncType: SyncType) {
    LaunchedEffect(userId, syncType) {
        // Перезапускается, когда меняется userId или syncType
        syncData(userId, syncType)
    }
}
```

```kotlin
@Composable
fun AnalyticsScreen() {
    LaunchedEffect(Unit) {
        // Выполняется один раз при входе экрана в композицию
        analytics.logScreenView("HomeScreen")
    }
}
```

#### 3. `rememberCoroutineScope` — ручной запуск корутин

**Назначение:** Предоставляет `CoroutineScope`, привязанный к композиции, для запуска корутин из обработчиков событий.

**Когда использовать:**
- Запуск корутин из callback-ов (`onClick`, `onSwipe` и т.п.).
- Когда запуск зависит от действий пользователя, а не от ключей.

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
                    try {
                        items = repository.fetchItems()
                    } finally {
                        isRefreshing = false
                    }
                }
            }
        ) {
            Text("Обновить")
        }

        if (isRefreshing) {
            CircularProgressIndicator()
        }

        LazyColumn {
            items(items) { item ->
                ItemRow(item)
            }
        }
    }
}
```

Кратко:
- `LaunchedEffect` — автоматический запуск на вход/изменение ключей.
- `rememberCoroutineScope` — ручной запуск из событий UI.

#### 4. `DisposableEffect` — очистка ресурсов

**Назначение:** Регистрировать слушателей/ресурсы и корректно освобождать их при выходе из композиции.

```kotlin
@Composable
fun LocationScreen() {
    var location by remember { mutableStateOf<Location?>(null) }

    DisposableEffect(Unit) {
        val listener = LocationListener { newLocation ->
            location = newLocation
        }

        locationManager.addListener(listener)

        onDispose {
            locationManager.removeListener(listener)
        }
    }

    location?.let { loc ->
        Text("Lat: ${loc.latitude}, Lon: ${loc.longitude}")
    }
}
```

#### 5. `produceState` — из `suspend` / `Flow` в `State`

**Назначение:** Обернуть `suspend`-функции или `Flow` в Compose `State`.

```kotlin
@Composable
fun TimerScreen() {
    val seconds by produceState(initialValue = 0) {
        while (true) {
            delay(1000)
            value++
        }
    }

    Text("Прошло: $seconds секунд")
}
```

```kotlin
@Composable
fun UserProfile(userId: String) {
    val userState by produceState<User?>(initialValue = null, userId) {
        value = userRepository.getUser(userId)
    }

    userState?.let { user ->
        Column {
            Text("Name: ${user.name}")
            Text("Email: ${user.email}")
        }
    } ?: CircularProgressIndicator()
}
```

```kotlin
@Composable
fun MessagesScreen() {
    val messages by produceState(
        initialValue = emptyList<Message>(),
        producer = {
            messageRepository.observeMessages().collect { newMessages ->
                value = newMessages
            }
        }
    )

    LazyColumn {
        items(messages) { message ->
            MessageItem(message)
        }
    }
}
```

#### 6. `SideEffect` — несуспендящиеся эффекты

**Назначение:** Выполнить несуспендящийся побочный эффект после успешной рекомпозиции.

```kotlin
@Composable
fun AnalyticsExample(screenName: String) {
    SideEffect {
        analytics.setCurrentScreen(screenName)
    }
}
```

```kotlin
@Composable
fun VideoPlayer(isPlaying: Boolean, player: MediaPlayer) {
    SideEffect {
        if (isPlaying) {
            player.start()
        } else {
            player.pause()
        }
    }
}
```

Используйте для синхронизации с внешними объектами, когда не нужны `suspend`-операции.

#### 7. `derivedStateOf` — вычисляемое состояние

**Назначение:** Эффективно вычислять значения на основе других состояний, избегая лишних пересчетов.

```kotlin
@Composable
fun EfficientExample(items: List<Item>) {
    val expensiveItems by remember(items) {
        derivedStateOf {
            items.filter { it.price > 100 }
        }
    }

    LazyColumn {
        items(expensiveItems) { item ->
            ItemRow(item)
        }
    }
}
```

#### 8. `snapshotFlow` — State → `Flow`

**Назначение:** Преобразовать Compose-состояние в `Flow` для обработки в корутине.

```kotlin
@Composable
fun SearchWithDebounce() {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<String>>(emptyList()) }

    LaunchedEffect(Unit) {
        snapshotFlow { query }
            .debounce(300)
            .filter { it.length >= 3 }
            .collectLatest { searchQuery ->
                results = searchRepository.search(searchQuery)
            }
    }

    Column {
        TextField(
            value = query,
            onValueChange = { query = it }
        )
        LazyColumn {
            items(results) { result ->
                Text(result)
            }
        }
    }
}
```

#### 9. Production-пример: загрузка данных и `Flow`

```kotlin
@Composable
fun ArticleScreen(
    articleId: String,
    viewModel: ArticleViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(articleId) {
        viewModel.loadArticle(articleId)
    }

    when (val state = uiState) {
        is ArticleUiState.Loading -> LoadingScreen()
        is ArticleUiState.Success -> ArticleContent(state.article)
        is ArticleUiState.Error -> ErrorScreen(state.message) {
            viewModel.loadArticle(articleId)
        }
    }
}
```

#### 10. Коллекция `Flow` с учетом жизненного цикла

```kotlin
@Composable
fun MessagesScreen(viewModel: MessagesViewModel = hiltViewModel()) {
    val messages by viewModel.messages.collectAsStateWithLifecycle()

    LazyColumn {
        items(messages) { message ->
            MessageItem(message)
        }
    }
}
```

```kotlin
@Composable
fun SimpleFlowCollection(viewModel: MyViewModel) {
    val data by viewModel.dataFlow.collectAsState(initial = null)

    data?.let { value ->
        Text("Data: $value")
    }
}
```

```kotlin
@Composable
fun ManualFlowCollection(viewModel: MyViewModel) {
    var data by remember { mutableStateOf<Data?>(null) }

    LaunchedEffect(Unit) {
        viewModel.dataFlow.collect { newData ->
            data = newData
        }
    }

    data?.let { value ->
        Text("Data: $value")
    }
}
```

#### 11. Side effects для анимаций

```kotlin
@Composable
fun ProgressScreen() {
    var progress by remember { mutableStateOf(0f) }

    LaunchedEffect(Unit) {
        for (i in 0..100) {
            progress = i / 100f
            delay(50)
        }
    }

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        CircularProgressIndicator(progress = progress)
        Text("${(progress * 100).toInt()}%")
    }
}
```

```kotlin
@Composable
fun PulsingCircle() {
    val infiniteTransition = rememberInfiniteTransition()
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.5f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        )
    )

    Box(
        modifier = Modifier
            .size(100.dp)
            .scale(scale)
            .background(Color.Blue, CircleShape)
    )
}
```

#### 12. Side effects для обработки событий

```kotlin
@Composable
fun EventHandlingScreen(viewModel: EventViewModel = hiltViewModel()) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(uiState.event) {
        uiState.event?.let { event ->
            when (event) {
                is UiEvent.ShowToast -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
                is UiEvent.Navigate -> {
                    // Навигация на другой экран
                }
            }
            viewModel.eventConsumed()
        }
    }

    Button(onClick = { viewModel.performAction() }) {
        Text("Выполнить действие")
    }
}
```

#### 13. Частые ошибки и best practices

```kotlin
@Composable
fun BadExample1() {
    fetchData() // Вызывается при КАЖДОЙ рекомпозиции!
}

@Composable
fun GoodExample1() {
    LaunchedEffect(Unit) {
        fetchData()
    }
}

@Composable
fun BadExample2() {
    val data = runBlocking {
        repository.getData()
    }
    Text(data)
}

@Composable
fun GoodExample2() {
    val data by produceState<String?>(initialValue = null) {
        value = repository.getData()
    }
    data?.let { Text(it) }
}

@Composable
fun BadExample3(userId: String) {
    LaunchedEffect(Unit) {
        loadUser(userId) // Не перезапустится при смене userId
    }
}

@Composable
fun GoodExample3(userId: String) {
    LaunchedEffect(userId) {
        loadUser(userId)
    }
}

@Composable
fun BadExample4() {
    val listener = LocationListener { }
    locationManager.addListener(listener)
}

@Composable
fun GoodExample4() {
    DisposableEffect(Unit) {
        val listener = LocationListener { }
        locationManager.addListener(listener)
        onDispose {
            locationManager.removeListener(listener)
        }
    }
}
```

#### 14. Тестирование side effects

```kotlin
@Test
fun testLaunchedEffect() = runTest {
    var launched = false

    composeTestRule.setContent {
        LaunchedEffect(Unit) {
            launched = true
        }
    }

    composeTestRule.waitForIdle()
    assertTrue(launched)
}
```

```kotlin
class FakeArticleRepository : ArticleRepository {
    override suspend fun getArticle(id: String): Article {
        delay(100)
        return Article(id, "Test Title", "Test Content")
    }
}

@Test
fun testArticleLoading() = runTest {
    val repository = FakeArticleRepository()
    val viewModel = ArticleViewModel(repository)

    composeTestRule.setContent {
        ArticleScreen(articleId = "1", viewModel = viewModel)
    }

    composeTestRule.onNodeWithText("Loading").assertExists()

    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithText("Test Title").assertExists()
}
```

### Связанные Вопросы (RU)
- [[q-testing-stateflow-sharedflow--kotlin--medium]] — `StateFlow` и `SharedFlow`

### Дополнительные Вопросы (RU)
1. Когда выбрать `LaunchedEffect` вместо `produceState` для загрузки данных?
2. Как `collectAsStateWithLifecycle` отличается от `collectAsState` с точки зрения управления жизненным циклом?
3. Что происходит с `LaunchedEffect`, когда меняется его ключ? Объясните жизненный цикл.
4. Как реализовать таймер обратного отсчета, который приостанавливается, когда приложение уходит в фон?
5. Как обрабатывать одноразовые события (например, показ toast) в Compose без потери при изменении конфигурации?
6. В чем разница между `SideEffect` и `LaunchedEffect` с точки зрения времени выполнения?
7. Как тестировать composable, который использует `DisposableEffect` с реальным listener?

### Ссылки (RU)
- [Документация Compose Side Effects](https://developer.android.com/jetpack/compose/side-effects)
- [LaunchedEffect](https://developer.android.com/reference/kotlin/androidx/compose/runtime/package-summary#LaunchedEffect(kotlin.Any,kotlin.coroutines.SuspendFunction1))
- [Lifecycle-aware сбор `Flow`](https://developer.android.com/topic/libraries/architecture/coroutines#lifecycle-aware)
- [Тестирование Compose](https://developer.android.com/jetpack/compose/testing)

## Answer (EN)

Side effects in Compose are operations that escape the scope of a composable function and affect the state of the app outside of the composition itself. Coroutines are central to managing async side effects in Compose.

#### 1. What Are Side Effects?

**Definition:**
- Side effects are operations that happen **outside** the composition.
- Examples: API calls, database writes, navigation, analytics.
- Must be properly scoped to composition lifecycle.
- Should be **predictable** and **manageable**.

```kotlin
//  BAD: Side effect executed on every recomposition
@Composable
fun BadExample() {
    // This runs every time the composable recomposes!
    analyticsLogger.log("Screen viewed")

    Text("Hello")
}

//  GOOD: Side effect executed once
@Composable
fun GoodExample() {
    LaunchedEffect(Unit) {
        // This runs only once when composable enters composition
        analyticsLogger.log("Screen viewed")
    }

    Text("Hello")
}
```

#### 2. `LaunchedEffect` - Launch Coroutines Tied to Composition

**Purpose:** Launch a coroutine that's tied to the lifecycle of the composable.

**Key characteristics:**
- Launches when composable **enters** composition.
- Cancels when composable **leaves** composition.
- Relaunches when **keys change**.

```kotlin
@Composable
fun UserProfileScreen(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }
    var isLoading by remember { mutableStateOf(true) }

    LaunchedEffect(userId) {
        isLoading = true
        try {
            user = userRepository.getUser(userId)
        } finally {
            isLoading = false
        }
    }

    when {
        isLoading -> LoadingIndicator()
        user != null -> UserProfile(user!!)
        else -> ErrorMessage()
    }
}
```

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<String>>(emptyList()) }

    LaunchedEffect(query) {
        delay(300)
        results = searchRepository.search(query)
    }

    Column {
        TextField(
            value = query,
            onValueChange = { query = it }
        )
        LazyColumn {
            items(results) { result ->
                Text(result)
            }
        }
    }
}
```

```kotlin
@Composable
fun DataSync(userId: String, syncType: SyncType) {
    LaunchedEffect(userId, syncType) {
        syncData(userId, syncType)
    }
}
```

```kotlin
@Composable
fun AnalyticsScreen() {
    LaunchedEffect(Unit) {
        analytics.logScreenView("HomeScreen")
    }
}
```

#### 3. `rememberCoroutineScope` - Manual Coroutine Launching

**Purpose:** Get a `CoroutineScope` that's bound to the composition, but launch coroutines manually (e.g., from event handlers).

**When to use:**
- Launch coroutines from callbacks (`onClick`, `onSwipe`, etc.).
- Manual control over coroutine timing.

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
                    try {
                        items = repository.fetchItems()
                    } finally {
                        isRefreshing = false
                    }
                }
            }
        ) {
            Text("Refresh")
        }

        if (isRefreshing) {
            CircularProgressIndicator()
        }

        LazyColumn {
            items(items) { item ->
                ItemRow(item)
            }
        }
    }
}
```

#### 4. `DisposableEffect` - Cleanup Resources

```kotlin
@Composable
fun LocationScreen() {
    var location by remember { mutableStateOf<Location?>(null) }

    DisposableEffect(Unit) {
        val listener = LocationListener { newLocation ->
            location = newLocation
        }

        locationManager.addListener(listener)

        onDispose {
            locationManager.removeListener(listener)
        }
    }

    location?.let { loc ->
        Text("Lat: ${loc.latitude}, Lon: ${loc.longitude}")
    }
}
```

#### 5. `produceState` - Convert Suspend Functions / `Flow` to State

```kotlin
@Composable
fun TimerScreen() {
    val seconds by produceState(initialValue = 0) {
        while (true) {
            delay(1000)
            value++
        }
    }

    Text("Elapsed: $seconds seconds")
}
```

```kotlin
@Composable
fun UserProfile(userId: String) {
    val userState by produceState<User?>(initialValue = null, userId) {
        value = userRepository.getUser(userId)
    }

    userState?.let { user ->
        Column {
            Text("Name: ${user.name}")
            Text("Email: ${user.email}")
        }
    } ?: CircularProgressIndicator()
}
```

```kotlin
@Composable
fun MessagesScreen() {
    val messages by produceState(
        initialValue = emptyList<Message>(),
        producer = {
            messageRepository.observeMessages().collect { newMessages ->
                value = newMessages
            }
        }
    )

    LazyColumn {
        items(messages) { message ->
            MessageItem(message)
        }
    }
}
```

#### 6. `SideEffect` - Non-Suspending Side Effects

```kotlin
@Composable
fun AnalyticsExample(screenName: String) {
    SideEffect {
        analytics.setCurrentScreen(screenName)
    }
}
```

```kotlin
@Composable
fun VideoPlayer(isPlaying: Boolean, player: MediaPlayer) {
    SideEffect {
        if (isPlaying) {
            player.start()
        } else {
            player.pause()
        }
    }
}
```

#### 7. `derivedStateOf` - Computed State

```kotlin
@Composable
fun EfficientExample(items: List<Item>) {
    val expensiveItems by remember(items) {
        derivedStateOf {
            items.filter { it.price > 100 }
        }
    }

    LazyColumn {
        items(expensiveItems) { item ->
            ItemRow(item)
        }
    }
}
```

#### 8. `snapshotFlow` - Convert State to `Flow`

```kotlin
@Composable
fun SearchWithDebounce() {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<String>>(emptyList()) }

    LaunchedEffect(Unit) {
        snapshotFlow { query }
            .debounce(300)
            .filter { it.length >= 3 }
            .collectLatest { searchQuery ->
                results = searchRepository.search(searchQuery)
            }
    }

    Column {
        TextField(
            value = query,
            onValueChange = { query = it }
        )
        LazyColumn {
            items(results) { result ->
                Text(result)
            }
        }
    }
}
```

#### 9. Production Example: Data Loading

```kotlin
@Composable
fun ArticleScreen(
    articleId: String,
    viewModel: ArticleViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(articleId) {
        viewModel.loadArticle(articleId)
    }

    when (val state = uiState) {
        is ArticleUiState.Loading -> LoadingScreen()
        is ArticleUiState.Success -> ArticleContent(state.article)
        is ArticleUiState.Error -> ErrorScreen(state.message) {
            viewModel.loadArticle(articleId)
        }
    }
}
```

#### 10. `Flow` Collection with Lifecycle Awareness

```kotlin
@Composable
fun MessagesScreen(viewModel: MessagesViewModel = hiltViewModel()) {
    val messages by viewModel.messages.collectAsStateWithLifecycle()

    LazyColumn {
        items(messages) { message ->
            MessageItem(message)
        }
    }
}
```

```kotlin
@Composable
fun SimpleFlowCollection(viewModel: MyViewModel) {
    val data by viewModel.dataFlow.collectAsState(initial = null)

    data?.let { value ->
        Text("Data: $value")
    }
}
```

```kotlin
@Composable
fun ManualFlowCollection(viewModel: MyViewModel) {
    var data by remember { mutableStateOf<Data?>(null) }

    LaunchedEffect(Unit) {
        viewModel.dataFlow.collect { newData ->
            data = newData
        }
    }

    data?.let { value ->
        Text("Data: $value")
    }
}
```

#### 11. Animation Side Effects

```kotlin
@Composable
fun ProgressScreen() {
    var progress by remember { mutableStateOf(0f) }

    LaunchedEffect(Unit) {
        for (i in 0..100) {
            progress = i / 100f
            delay(50)
        }
    }

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        CircularProgressIndicator(progress = progress)
        Text("${(progress * 100).toInt()}%")
    }
}
```

```kotlin
@Composable
fun PulsingCircle() {
    val infiniteTransition = rememberInfiniteTransition()
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.5f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        )
    )

    Box(
        modifier = Modifier
            .size(100.dp)
            .scale(scale)
            .background(Color.Blue, CircleShape)
    )
}
```

#### 12. Event Handling Side Effects

```kotlin
@Composable
fun EventHandlingScreen(viewModel: EventViewModel = hiltViewModel()) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(uiState.event) {
        uiState.event?.let { event ->
            when (event) {
                is UiEvent.ShowToast -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
                is UiEvent.Navigate -> {
                    // Navigate to screen
                }
            }
            viewModel.eventConsumed()
        }
    }

    Button(onClick = { viewModel.performAction() }) {
        Text("Perform Action")
    }
}
```

#### 13. Common Mistakes and Best Practices

```kotlin
@Composable
fun BadExample1() {
    fetchData() // Called on EVERY recomposition!
}

@Composable
fun GoodExample1() {
    LaunchedEffect(Unit) {
        fetchData()
    }
}

@Composable
fun BadExample2() {
    val data = runBlocking {
        repository.getData()
    }
    Text(data)
}

@Composable
fun GoodExample2() {
    val data by produceState<String?>(initialValue = null) {
        value = repository.getData()
    }
    data?.let { Text(it) }
}

@Composable
fun BadExample3(userId: String) {
    LaunchedEffect(Unit) {
        loadUser(userId) // Won't reload when userId changes
    }
}

@Composable
fun GoodExample3(userId: String) {
    LaunchedEffect(userId) {
        loadUser(userId)
    }
}

@Composable
fun BadExample4() {
    val listener = LocationListener { }
    locationManager.addListener(listener)
}

@Composable
fun GoodExample4() {
    DisposableEffect(Unit) {
        val listener = LocationListener { }
        locationManager.addListener(listener)
        onDispose {
            locationManager.removeListener(listener)
        }
    }
}
```

#### 14. Testing Side Effects

```kotlin
@Test
fun testLaunchedEffect() = runTest {
    var launched = false

    composeTestRule.setContent {
        LaunchedEffect(Unit) {
            launched = true
        }
    }

    composeTestRule.waitForIdle()
    assertTrue(launched)
}
```

```kotlin
class FakeArticleRepository : ArticleRepository {
    override suspend fun getArticle(id: String): Article {
        delay(100)
        return Article(id, "Test Title", "Test Content")
    }
}

@Test
fun testArticleLoading() = runTest {
    val repository = FakeArticleRepository()
    val viewModel = ArticleViewModel(repository)

    composeTestRule.setContent {
        ArticleScreen(articleId = "1", viewModel = viewModel)
    }

    composeTestRule.onNodeWithText("Loading").assertExists()

    composeTestRule.waitForIdle()

    composeTestRule.onNodeWithText("Test Title").assertExists()
}
```

## Related Questions
- [[q-testing-stateflow-sharedflow--kotlin--medium]]

## Follow-ups
- When would you choose `LaunchedEffect` over `produceState` for data loading?
- How does `collectAsStateWithLifecycle` differ from `collectAsState` regarding lifecycle awareness?
- What happens to `LaunchedEffect` when its key changes? Explain its lifecycle.
- How to implement a countdown timer that pauses when the app goes to background?
- How to handle one-off events (e.g., toast) in Compose without losing them on configuration change?
- What is the difference between `SideEffect` and `LaunchedEffect` in terms of execution timing?
- How to test a composable that uses `DisposableEffect` with a real listener?

## References
- [Compose Side Effects documentation](https://developer.android.com/jetpack/compose/side-effects)
- [LaunchedEffect](https://developer.android.com/reference/kotlin/androidx/compose/runtime/package-summary#LaunchedEffect(kotlin.Any,kotlin.coroutines.SuspendFunction1))
- [Lifecycle-aware `Flow` collection](https://developer.android.com/topic/libraries/architecture/coroutines#lifecycle-aware)
- [Compose Testing](https://developer.android.com/jetpack/compose/testing)
- [[c-kotlin]]
- [[c-coroutines]]
