---
id: kotlin-170
title: "Coroutines and side effects in Jetpack Compose / Корутины и side effects в Jetpack Compose"
aliases: [Coroutines Side Effects Compose, Корутины side effects Jetpack Compose]
topic: kotlin
subtopics: [compose-integration, coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-15
updated: 2025-10-31
tags: [android, coroutines, difficulty/medium, jetpack-compose, kotlin, launchedeffect, lifecycle, rememberCoroutineScope, side-effects, state-management]
moc: moc-kotlin
related: [q-stateflow-sharedflow--kotlin--medium]
date created: Saturday, November 1st 2025, 1:28:03 pm
date modified: Saturday, November 1st 2025, 5:43:27 pm
---

# Coroutines and Side Effects in Jetpack Compose

## English

### Question
What are side effects in Jetpack Compose and how do coroutines integrate with them? Explain LaunchedEffect, rememberCoroutineScope, DisposableEffect, produceState, and other side effect handlers. When should you use each? Provide production examples of data loading, animations, event handling, and Flow collection with proper lifecycle management and testing strategies.

# Question (EN)
> What are side effects in Jetpack Compose and how do coroutines integrate with them? Explain LaunchedEffect, rememberCoroutineScope, DisposableEffect, produceState, and other side effect handlers. When should you use each? Provide production examples of data loading, animations, event handling, and Flow collection with proper lifecycle management and testing strategies.

# Вопрос (RU)
> What are side effects in Jetpack Compose and how do coroutines integrate with them? Explain LaunchedEffect, rememberCoroutineScope, DisposableEffect, produceState, and other side effect handlers. When should you use each? Provide production examples of data loading, animations, event handling, and Flow collection with proper lifecycle management and testing strategies.

---

## Answer (EN)



**Side effects** in Compose are operations that escape the scope of a composable function and affect the state of the app outside of the composition itself. Coroutines are central to managing async side effects in Compose.

#### 1. What Are Side Effects?

**Definition:**
- Side effects are operations that happen **outside** the composition
- Examples: API calls, database writes, navigation, analytics
- Must be properly scoped to composition lifecycle
- Should be **predictable** and **manageable**

**Why side effects matter:**

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

#### 2. LaunchedEffect - Launch Coroutines Tied to Composition

**Purpose:** Launch a coroutine that's tied to the lifecycle of the composable.

**Key characteristics:**
- Launches when composable **enters** composition
- Cancels when composable **leaves** composition
- Relaunches when **keys change**

**Basic usage:**

```kotlin
@Composable
fun UserProfileScreen(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }
    var isLoading by remember { mutableStateOf(true) }

    // Launch coroutine tied to composition
    LaunchedEffect(userId) { // Key: userId
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

**How keys work:**

```kotlin
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<String>>(emptyList()) }

    LaunchedEffect(query) {
        // Cancel previous search and restart when query changes
        delay(300) // Debounce
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

**Multiple keys:**

```kotlin
@Composable
fun DataSync(userId: String, syncType: SyncType) {
    LaunchedEffect(userId, syncType) {
        // Relaunches when either userId OR syncType changes
        syncData(userId, syncType)
    }
}
```

**Key is Unit (runs once):**

```kotlin
@Composable
fun AnalyticsScreen() {
    LaunchedEffect(Unit) {
        // Runs only once when screen enters composition
        analytics.logScreenView("HomeScreen")
    }
}
```

#### 3. rememberCoroutineScope - Manual Coroutine Launching

**Purpose:** Get a CoroutineScope that's bound to the composition, but launch coroutines **manually** (e.g., from event handlers).

**When to use:**
- Launch coroutines from **callbacks** (onClick, onSwipe, etc.)
- Manual control over coroutine timing
- Not tied to specific keys

**Basic usage:**

```kotlin
@Composable
fun RefreshableList() {
    val scope = rememberCoroutineScope()
    var items by remember { mutableStateOf<List<Item>>(emptyList()) }
    var isRefreshing by remember { mutableStateOf(false) }

    Column {
        Button(
            onClick = {
                // Launch coroutine manually from callback
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

**LaunchedEffect vs rememberCoroutineScope:**

| Aspect | LaunchedEffect | rememberCoroutineScope |
|--------|----------------|------------------------|
| Launch timing | Automatically on composition/key change | Manually from callback |
| Use case | Load data when screen appears | Handle button clicks |
| Keys | Relaunches when keys change | No key mechanism |
| Example | `LaunchedEffect(userId) { loadUser() }` | `scope.launch { refresh() }` |

#### 4. DisposableEffect - Cleanup Resources

**Purpose:** Register observers/listeners and clean them up when composition leaves.

**When to use:**
- Register/unregister listeners
- Subscribe/unsubscribe
- Acquire/release resources

**Basic usage:**

```kotlin
@Composable
fun LocationScreen() {
    var location by remember { mutableStateOf<Location?>(null) }

    DisposableEffect(Unit) {
        val listener = LocationListener { newLocation ->
            location = newLocation
        }

        // Register listener
        locationManager.addListener(listener)

        // Cleanup when leaving composition
        onDispose {
            locationManager.removeListener(listener)
        }
    }

    location?.let { loc ->
        Text("Lat: ${loc.latitude}, Lon: ${loc.longitude}")
    }
}
```

**Lifecycle observation:**

```kotlin
@Composable
fun LifecycleAwareScreen(lifecycleOwner: LifecycleOwner) {
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_RESUME -> println("Screen resumed")
                Lifecycle.Event.ON_PAUSE -> println("Screen paused")
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

#### 5. produceState - Convert Suspend Functions to State

**Purpose:** Convert a suspend function or Flow into Compose State.

**When to use:**
- Wrap existing suspend functions
- Integrate with non-Compose code
- Create stateful data sources

**Basic usage:**

```kotlin
@Composable
fun TimerScreen() {
    // Convert suspend function to State<Int>
    val seconds by produceState(initialValue = 0) {
        while (true) {
            delay(1000)
            value++ // Update state
        }
    }

    Text("Elapsed: $seconds seconds")
}
```

**Loading data with produceState:**

```kotlin
@Composable
fun UserProfile(userId: String) {
    val userState by produceState<User?>(initialValue = null, userId) {
        // Automatically reloads when userId changes
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

**Flow to State:**

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

#### 6. SideEffect - Non-Suspending Side Effects

**Purpose:** Publish state to non-Compose code **after successful recomposition**.

**When to use:**
- Update non-Compose objects with Compose state
- Analytics logging
- Synchronize with external state

**Basic usage:**

```kotlin
@Composable
fun AnalyticsExample(screenName: String) {
    SideEffect {
        // Runs after every successful recomposition
        analytics.setCurrentScreen(screenName)
    }
}
```

**Update external state:**

```kotlin
@Composable
fun VideoPlayer(isPlaying: Boolean, player: MediaPlayer) {
    SideEffect {
        // Synchronize MediaPlayer state with Compose state
        if (isPlaying) {
            player.start()
        } else {
            player.pause()
        }
    }
}
```

**SideEffect vs LaunchedEffect:**

| Aspect | SideEffect | LaunchedEffect |
|--------|------------|----------------|
| Suspending | No | Yes |
| Timing | After recomposition | On composition/key change |
| Use case | Non-suspending updates | Suspending operations |
| Example | `analytics.log()` | `repository.fetch()` |

#### 7. derivedStateOf - Computed State

**Purpose:** Create state that's derived from other state, minimizing recompositions.

**When to use:**
- Expensive calculations based on state
- Filtering/transforming lists
- Computed properties

**Without derivedStateOf (inefficient):**

```kotlin
@Composable
fun IneffcientExample(items: List<Item>) {
    // Recomputes on EVERY recomposition!
    val expensiveItems = items.filter { it.price > 100 }

    LazyColumn {
        items(expensiveItems) { item ->
            ItemRow(item)
        }
    }
}
```

**With derivedStateOf (efficient):**

```kotlin
@Composable
fun EfficientExample(items: List<Item>) {
    // Only recomputes when items actually change
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

#### 8. snapshotFlow - Convert State to Flow

**Purpose:** Convert Compose State into a Flow for observation.

**When to use:**
- Observe state changes in coroutines
- Integrate Compose state with Flow-based code
- Debounce state changes

**Basic usage:**

```kotlin
@Composable
fun SearchWithDebounce() {
    var query by remember { mutableStateOf("") }
    var results by remember { mutableStateOf<List<String>>(emptyList()) }

    LaunchedEffect(Unit) {
        // Convert state to flow and apply operators
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

**Observe multiple state values:**

```kotlin
@Composable
fun CombinedStateObservation() {
    var firstName by remember { mutableStateOf("") }
    var lastName by remember { mutableStateOf("") }
    var fullName by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        snapshotFlow { "$firstName $lastName" }
            .collect { combined ->
                fullName = combined.trim()
            }
    }

    Column {
        TextField(value = firstName, onValueChange = { firstName = it })
        TextField(value = lastName, onValueChange = { lastName = it })
        Text("Full name: $fullName")
    }
}
```

#### 9. Production Example: Data Loading

**Complete data loading pattern:**

```kotlin
@Composable
fun ArticleScreen(
    articleId: String,
    viewModel: ArticleViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // Load data when screen appears or articleId changes
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

sealed class ArticleUiState {
    object Loading : ArticleUiState()
    data class Success(val article: Article) : ArticleUiState()
    data class Error(val message: String) : ArticleUiState()
}

class ArticleViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ArticleUiState>(ArticleUiState.Loading)
    val uiState: StateFlow<ArticleUiState> = _uiState.asStateFlow()

    fun loadArticle(articleId: String) {
        viewModelScope.launch {
            _uiState.value = ArticleUiState.Loading
            try {
                val article = repository.getArticle(articleId)
                _uiState.value = ArticleUiState.Success(article)
            } catch (e: Exception) {
                _uiState.value = ArticleUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

@Composable
fun ArticleContent(article: Article) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text(
            text = article.title,
            style = MaterialTheme.typography.h4
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(text = article.content)
    }
}
```

#### 10. Flow Collection with Lifecycle Awareness

**collectAsStateWithLifecycle - Recommended approach:**

```kotlin
@Composable
fun MessagesScreen(viewModel: MessagesViewModel = hiltViewModel()) {
    // Automatically starts/stops collection based on lifecycle
    val messages by viewModel.messages.collectAsStateWithLifecycle()

    LazyColumn {
        items(messages) { message ->
            MessageItem(message)
        }
    }
}

class MessagesViewModel @Inject constructor(
    private val repository: MessagesRepository
) : ViewModel() {

    val messages: StateFlow<List<Message>> = repository.observeMessages()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

**collectAsState (simpler, but no lifecycle awareness):**

```kotlin
@Composable
fun SimpleFlowCollection(viewModel: MyViewModel) {
    // Collects as long as composable is in composition
    val data by viewModel.dataFlow.collectAsState(initial = null)

    data?.let { value ->
        Text("Data: $value")
    }
}
```

**Manual collection with LaunchedEffect:**

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

**Animated progress with LaunchedEffect:**

```kotlin
@Composable
fun ProgressScreen() {
    var progress by remember { mutableStateOf(0f) }

    LaunchedEffect(Unit) {
        // Animate progress from 0 to 1
        for (i in 0..100) {
            progress = i / 100f
            delay(50)
        }
    }

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalAlignment = Alignment.CenterVertically
    ) {
        CircularProgressIndicator(progress = progress)
        Text("${(progress * 100).toInt()}%")
    }
}
```

**Infinite animation:**

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

**One-time events with LaunchedEffect:**

```kotlin
@Composable
fun EventHandlingScreen(viewModel: EventViewModel = hiltViewModel()) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // Handle one-time events
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

    // UI content
    Button(onClick = { viewModel.performAction() }) {
        Text("Perform Action")
    }
}

sealed class UiEvent {
    data class ShowToast(val message: String) : UiEvent()
    data class Navigate(val route: String) : UiEvent()
}

data class UiState(
    val isLoading: Boolean = false,
    val event: UiEvent? = null
)

class EventViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun performAction() {
        viewModelScope.launch {
            // Perform action
            _uiState.value = UiState(event = UiEvent.ShowToast("Action completed"))
        }
    }

    fun eventConsumed() {
        _uiState.value = _uiState.value.copy(event = null)
    }
}
```

#### 13. Common Mistakes and Best Practices

**Mistakes to avoid:**

```kotlin
//  BAD: Side effect on every recomposition
@Composable
fun BadExample1() {
    fetchData() // Called on EVERY recomposition!
}

//  GOOD: Wrap in LaunchedEffect
@Composable
fun GoodExample1() {
    LaunchedEffect(Unit) {
        fetchData()
    }
}

//  BAD: Blocking operation in composable
@Composable
fun BadExample2() {
    val data = runBlocking {
        repository.getData() // Blocks composition!
    }
    Text(data)
}

//  GOOD: Use produceState or LaunchedEffect
@Composable
fun GoodExample2() {
    val data by produceState<String?>(null) {
        value = repository.getData()
    }
    data?.let { Text(it) }
}

//  BAD: Forgetting key in LaunchedEffect
@Composable
fun BadExample3(userId: String) {
    LaunchedEffect(Unit) {
        // Won't reload when userId changes!
        loadUser(userId)
    }
}

//  GOOD: Include dependencies in keys
@Composable
fun GoodExample3(userId: String) {
    LaunchedEffect(userId) {
        loadUser(userId)
    }
}

//  BAD: Not cleaning up resources
@Composable
fun BadExample4() {
    val listener = LocationListener { }
    locationManager.addListener(listener)
    // Never removed!
}

//  GOOD: Use DisposableEffect for cleanup
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

**Best practices summary:**

| Do | Don't |
|----|-------|
| Use LaunchedEffect for async operations | Call suspend functions directly in composable |
| Use rememberCoroutineScope for event handlers | Use GlobalScope |
| Use DisposableEffect for cleanup | Forget to unregister listeners |
| Use produceState for suspend → State | Use runBlocking in composables |
| Include dependencies in LaunchedEffect keys | Use Unit when data can change |
| Use collectAsStateWithLifecycle for Flows | Collect flows without lifecycle awareness |

#### 14. Testing Side Effects

**Testing LaunchedEffect:**

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

**Testing with fake repository:**

```kotlin
class FakeArticleRepository : ArticleRepository {
    override suspend fun getArticle(id: String): Article {
        delay(100) // Simulate network delay
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

    // Initially shows loading
    composeTestRule.onNodeWithText("Loading").assertExists()

    // Wait for data to load
    composeTestRule.waitForIdle()

    // Shows article content
    composeTestRule.onNodeWithText("Test Title").assertExists()
}
```

### Related Questions
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - StateFlow and SharedFlow

## Follow-ups
1. When would you choose LaunchedEffect over produceState for loading data?
2. How does collectAsStateWithLifecycle differ from collectAsState in terms of performance and lifecycle management?
3. What happens to a LaunchedEffect when its key changes? Explain the lifecycle.
4. How would you implement a countdown timer that pauses when the app goes to background?
5. Explain how to handle one-time events (like showing a toast) in Compose without losing them on configuration changes.
6. What's the difference between SideEffect and LaunchedEffect in terms of execution timing?
7. How do you test a composable that uses DisposableEffect with a real listener?

### References
- [Compose Side Effects Documentation](https://developer.android.com/jetpack/compose/side-effects)
- [LaunchedEffect](https://developer.android.com/reference/kotlin/androidx/compose/runtime/package-summary#LaunchedEffect(kotlin.Any,kotlin.coroutines.SuspendFunction1))
- [Lifecycle-aware Flow collection](https://developer.android.com/topic/libraries/architecture/coroutines#lifecycle-aware)
- [Testing Compose](https://developer.android.com/jetpack/compose/testing)

---


## Ответ (RU)

*(Краткое содержание основных пунктов из английской версии)*
Что такое side effects в Jetpack Compose и как корутины интегрируются с ними? Объясните LaunchedEffect, rememberCoroutineScope, DisposableEffect, produceState и другие обработчики side effects. Когда следует использовать каждый из них? Приведите production примеры загрузки данных, анимаций, обработки событий и сбора Flow с правильным управлением жизненным циклом и стратегиями тестирования.

**Side effects** в Compose — это операции, которые выходят за рамки composable функции и влияют на состояние приложения вне самой композиции.

#### 1. Что Такое Side Effects?

**Определение:**
- Side effects — это операции **вне** композиции
- Примеры: API вызовы, запись в БД, навигация, аналитика
- Должны быть правильно привязаны к жизненному циклу композиции
- Должны быть **предсказуемыми** и **управляемыми**

**Почему side effects важны:**

```kotlin
//  ПЛОХО: Side effect выполняется при каждой рекомпозиции
@Composable
fun BadExample() {
    // Это выполняется каждый раз при рекомпозиции!
    analyticsLogger.log("Экран просмотрен")

    Text("Привет")
}

//  ХОРОШО: Side effect выполняется один раз
@Composable
fun GoodExample() {
    LaunchedEffect(Unit) {
        // Это выполняется только один раз при входе в композицию
        analyticsLogger.log("Экран просмотрен")
    }

    Text("Привет")
}
```

*(Продолжение следует той же структуре с подробными примерами всех side effects на русском языке, включая LaunchedEffect, rememberCoroutineScope, DisposableEffect, produceState, SideEffect, derivedStateOf, snapshotFlow, production примеры, тестирование и best practices)*

### Связанные Вопросы
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - StateFlow и SharedFlow

### Дополнительные Вопросы
1. Когда выбрать LaunchedEffect вместо produceState для загрузки данных?
2. Как collectAsStateWithLifecycle отличается от collectAsState с точки зрения производительности и управления жизненным циклом?
3. Что происходит с LaunchedEffect когда меняется его ключ? Объясните жизненный цикл.
4. Как реализовать таймер обратного отсчета, который приостанавливается когда приложение уходит в фон?
5. Объясните, как обрабатывать одноразовые события (например, показ toast) в Compose без потери при изменении конфигурации.
6. В чем разница между SideEffect и LaunchedEffect с точки зрения времени выполнения?
7. Как тестировать composable, который использует DisposableEffect с реальным listener?

### Ссылки
- [Документация Compose Side Effects](https://developer.android.com/jetpack/compose/side-effects)
- [LaunchedEffect](https://developer.android.com/reference/kotlin/androidx/compose/runtime/package-summary#LaunchedEffect(kotlin.Any,kotlin.coroutines.SuspendFunction1))
- [Lifecycle-aware сбор Flow](https://developer.android.com/topic/libraries/architecture/coroutines#lifecycle-aware)
- [Тестирование Compose](https://developer.android.com/jetpack/compose/testing)
