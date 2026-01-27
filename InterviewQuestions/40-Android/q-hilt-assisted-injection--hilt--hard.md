---
id: android-hilt-005
title: Hilt Assisted Injection / Assisted Injection в Hilt
aliases:
- Assisted Injection
- AssistedInject
- AssistedFactory
- Runtime Parameters DI
topic: android
subtopics:
- di-hilt
- architecture
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-hilt-viewmodel-injection--hilt--medium
- q-hilt-modules-provides--hilt--medium
- q-hilt-scopes--hilt--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/architecture
- difficulty/hard
- hilt
- assisted-injection
- dependency-injection
anki_cards:
- slug: android-hilt-005-0-en
  language: en
- slug: android-hilt-005-0-ru
  language: ru
---
# Vopros (RU)
> Что такое Assisted Injection в Hilt? Когда и как использовать @AssistedInject и @AssistedFactory?

# Question (EN)
> What is Assisted Injection in Hilt? When and how to use @AssistedInject and @AssistedFactory?

---

## Otvet (RU)

Assisted Injection - это паттерн, позволяющий создавать объекты, которые требуют как зависимости из DI-графа, так и параметры, известные только в runtime. Это особенно полезно, когда некоторые значения не могут быть предоставлены через Hilt (например, ID пользователя, конфигурация из Intent).

### Проблема

```kotlin
// Этот класс требует userId, который известен только в runtime
class UserDetailPresenter(
    private val userRepository: UserRepository, // Из DI
    private val analyticsService: AnalyticsService, // Из DI
    private val userId: String // Runtime параметр - как его передать?
)

// БЕЗ Assisted Injection - приходится создавать вручную
class UserDetailActivity : AppCompatActivity() {

    @Inject lateinit var userRepository: UserRepository
    @Inject lateinit var analyticsService: AnalyticsService

    private lateinit var presenter: UserDetailPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getStringExtra("userId")!!

        // Ручное создание - плохо для тестирования
        presenter = UserDetailPresenter(
            userRepository = userRepository,
            analyticsService = analyticsService,
            userId = userId
        )
    }
}
```

### Решение с Assisted Injection

```kotlin
// 1. Помечаем класс @AssistedInject и параметр @Assisted
class UserDetailPresenter @AssistedInject constructor(
    private val userRepository: UserRepository,      // Из DI графа
    private val analyticsService: AnalyticsService,  // Из DI графа
    @Assisted private val userId: String             // Runtime параметр
) {

    suspend fun loadUser(): User {
        analyticsService.logEvent("load_user", mapOf("userId" to userId))
        return userRepository.getUser(userId)
    }
}

// 2. Создаем Factory интерфейс
@AssistedFactory
interface UserDetailPresenterFactory {
    fun create(userId: String): UserDetailPresenter
}

// 3. Используем Factory
@AndroidEntryPoint
class UserDetailActivity : AppCompatActivity() {

    @Inject
    lateinit var presenterFactory: UserDetailPresenterFactory

    private lateinit var presenter: UserDetailPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getStringExtra("userId")!!

        // Создание через factory - легко тестировать
        presenter = presenterFactory.create(userId)
    }
}
```

### Множественные @Assisted параметры

Если несколько параметров одного типа, используйте именованные assisted:

```kotlin
class ChatMessageSender @AssistedInject constructor(
    private val messageRepository: MessageRepository,
    private val encryptionService: EncryptionService,
    @Assisted("senderId") private val senderId: String,
    @Assisted("receiverId") private val receiverId: String,
    @Assisted private val chatRoomId: String
) {

    suspend fun sendMessage(text: String) {
        val encrypted = encryptionService.encrypt(text)
        messageRepository.send(
            from = senderId,
            to = receiverId,
            room = chatRoomId,
            message = encrypted
        )
    }
}

@AssistedFactory
interface ChatMessageSenderFactory {
    fun create(
        @Assisted("senderId") senderId: String,
        @Assisted("receiverId") receiverId: String,
        chatRoomId: String
    ): ChatMessageSender
}
```

### Assisted Injection с ViewModel

Для ViewModel с runtime-параметрами используется другой подход - через `SavedStateHandle`:

```kotlin
// Рекомендуемый способ для ViewModel - SavedStateHandle
@HiltViewModel
class UserDetailViewModel @Inject constructor(
    private val userRepository: UserRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Runtime параметр из navigation/intent
    private val userId: String = checkNotNull(savedStateHandle["userId"])

    val user = flow {
        emit(userRepository.getUser(userId))
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = null
    )
}
```

Однако, если вам нужны параметры, которые нельзя сериализовать в `SavedStateHandle`:

```kotlin
// Для сложных объектов - Assisted Injection
class UserDetailViewModel @AssistedInject constructor(
    private val userRepository: UserRepository,
    @Assisted private val userConfig: UserConfig // Сложный объект
) : ViewModel() {

    @AssistedFactory
    interface Factory {
        fun create(userConfig: UserConfig): UserDetailViewModel
    }
}

// Кастомный ViewModelProvider.Factory
@AndroidEntryPoint
class UserDetailFragment : Fragment() {

    @Inject
    lateinit var viewModelFactory: UserDetailViewModel.Factory

    private val viewModel: UserDetailViewModel by viewModels {
        object : ViewModelProvider.Factory {
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                val config = arguments?.getParcelable<UserConfig>("config")!!
                @Suppress("UNCHECKED_CAST")
                return viewModelFactory.create(config) as T
            }
        }
    }
}
```

### Assisted Injection для Worker (WorkManager)

```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted appContext: Context,
    @Assisted workerParams: WorkerParameters,
    private val syncRepository: SyncRepository,
    private val notificationManager: NotificationManager
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        return try {
            val userId = inputData.getString("userId") ?: return Result.failure()
            syncRepository.syncUser(userId)
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
}

// Использование
class SyncManager @Inject constructor(
    private val workManager: WorkManager
) {

    fun scheduleSync(userId: String) {
        val inputData = Data.Builder()
            .putString("userId", userId)
            .build()

        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setInputData(inputData)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        workManager.enqueue(request)
    }
}
```

### Комплексный пример: Экран с динамической конфигурацией

```kotlin
// Domain model
data class ScreenConfig(
    val screenId: String,
    val featureFlags: FeatureFlags,
    val analyticsContext: AnalyticsContext
)

// Presenter с Assisted Injection
class DynamicScreenPresenter @AssistedInject constructor(
    private val contentRepository: ContentRepository,
    private val analyticsService: AnalyticsService,
    private val featureFlagManager: FeatureFlagManager,
    @Assisted private val config: ScreenConfig
) {

    private val _state = MutableStateFlow<ScreenState>(ScreenState.Loading)
    val state: StateFlow<ScreenState> = _state.asStateFlow()

    suspend fun loadContent() {
        _state.value = ScreenState.Loading

        try {
            val content = contentRepository.getContent(config.screenId)
            val processedContent = applyFeatureFlags(content)

            analyticsService.logScreenView(
                screenId = config.screenId,
                context = config.analyticsContext
            )

            _state.value = ScreenState.Success(processedContent)
        } catch (e: Exception) {
            _state.value = ScreenState.Error(e.message ?: "Unknown error")
        }
    }

    private fun applyFeatureFlags(content: Content): Content {
        return if (config.featureFlags.newLayoutEnabled) {
            content.withNewLayout()
        } else {
            content
        }
    }

    @AssistedFactory
    interface Factory {
        fun create(config: ScreenConfig): DynamicScreenPresenter
    }
}

sealed interface ScreenState {
    data object Loading : ScreenState
    data class Success(val content: Content) : ScreenState
    data class Error(val message: String) : ScreenState
}

// Использование в Compose
@Composable
fun DynamicScreen(
    config: ScreenConfig,
    presenterFactory: DynamicScreenPresenter.Factory =
        LocalDynamicScreenPresenterFactory.current
) {
    val presenter = remember(config) {
        presenterFactory.create(config)
    }

    val state by presenter.state.collectAsStateWithLifecycle()

    LaunchedEffect(config) {
        presenter.loadContent()
    }

    when (val currentState = state) {
        is ScreenState.Loading -> LoadingIndicator()
        is ScreenState.Success -> ContentView(currentState.content)
        is ScreenState.Error -> ErrorView(currentState.message)
    }
}

// CompositionLocal для factory
val LocalDynamicScreenPresenterFactory = staticCompositionLocalOf<DynamicScreenPresenter.Factory> {
    error("DynamicScreenPresenterFactory not provided")
}

// Предоставление в Activity
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var presenterFactory: DynamicScreenPresenter.Factory

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            CompositionLocalProvider(
                LocalDynamicScreenPresenterFactory provides presenterFactory
            ) {
                AppContent()
            }
        }
    }
}
```

### Правила и ограничения

1. **@AssistedInject** применяется к конструктору класса
2. **@Assisted** помечает runtime-параметры
3. **@AssistedFactory** - интерфейс с одним методом создания
4. Factory автоматически реализуется Hilt
5. Нельзя использовать scope-аннотации (@Singleton и т.д.) с Assisted Injection
6. Для ViewModel лучше использовать SavedStateHandle, если параметры сериализуемы

---

## Answer (EN)

Assisted Injection is a pattern that allows creating objects that require both dependencies from the DI graph and parameters known only at runtime. This is especially useful when some values cannot be provided through Hilt (e.g., user ID, configuration from Intent).

### The Problem

```kotlin
// This class requires userId which is only known at runtime
class UserDetailPresenter(
    private val userRepository: UserRepository, // From DI
    private val analyticsService: AnalyticsService, // From DI
    private val userId: String // Runtime parameter - how to pass it?
)

// WITHOUT Assisted Injection - manual creation required
class UserDetailActivity : AppCompatActivity() {

    @Inject lateinit var userRepository: UserRepository
    @Inject lateinit var analyticsService: AnalyticsService

    private lateinit var presenter: UserDetailPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getStringExtra("userId")!!

        // Manual creation - bad for testing
        presenter = UserDetailPresenter(
            userRepository = userRepository,
            analyticsService = analyticsService,
            userId = userId
        )
    }
}
```

### Solution with Assisted Injection

```kotlin
// 1. Mark the class with @AssistedInject and parameters with @Assisted
class UserDetailPresenter @AssistedInject constructor(
    private val userRepository: UserRepository,      // From DI graph
    private val analyticsService: AnalyticsService,  // From DI graph
    @Assisted private val userId: String             // Runtime parameter
) {

    suspend fun loadUser(): User {
        analyticsService.logEvent("load_user", mapOf("userId" to userId))
        return userRepository.getUser(userId)
    }
}

// 2. Create Factory interface
@AssistedFactory
interface UserDetailPresenterFactory {
    fun create(userId: String): UserDetailPresenter
}

// 3. Use the Factory
@AndroidEntryPoint
class UserDetailActivity : AppCompatActivity() {

    @Inject
    lateinit var presenterFactory: UserDetailPresenterFactory

    private lateinit var presenter: UserDetailPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getStringExtra("userId")!!

        // Creation via factory - easy to test
        presenter = presenterFactory.create(userId)
    }
}
```

### Multiple @Assisted Parameters

If multiple parameters have the same type, use named assisted:

```kotlin
class ChatMessageSender @AssistedInject constructor(
    private val messageRepository: MessageRepository,
    private val encryptionService: EncryptionService,
    @Assisted("senderId") private val senderId: String,
    @Assisted("receiverId") private val receiverId: String,
    @Assisted private val chatRoomId: String
) {

    suspend fun sendMessage(text: String) {
        val encrypted = encryptionService.encrypt(text)
        messageRepository.send(
            from = senderId,
            to = receiverId,
            room = chatRoomId,
            message = encrypted
        )
    }
}

@AssistedFactory
interface ChatMessageSenderFactory {
    fun create(
        @Assisted("senderId") senderId: String,
        @Assisted("receiverId") receiverId: String,
        chatRoomId: String
    ): ChatMessageSender
}
```

### Assisted Injection with ViewModel

For ViewModel with runtime parameters, a different approach is used - through `SavedStateHandle`:

```kotlin
// Recommended approach for ViewModel - SavedStateHandle
@HiltViewModel
class UserDetailViewModel @Inject constructor(
    private val userRepository: UserRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Runtime parameter from navigation/intent
    private val userId: String = checkNotNull(savedStateHandle["userId"])

    val user = flow {
        emit(userRepository.getUser(userId))
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = null
    )
}
```

However, if you need parameters that cannot be serialized into `SavedStateHandle`:

```kotlin
// For complex objects - Assisted Injection
class UserDetailViewModel @AssistedInject constructor(
    private val userRepository: UserRepository,
    @Assisted private val userConfig: UserConfig // Complex object
) : ViewModel() {

    @AssistedFactory
    interface Factory {
        fun create(userConfig: UserConfig): UserDetailViewModel
    }
}

// Custom ViewModelProvider.Factory
@AndroidEntryPoint
class UserDetailFragment : Fragment() {

    @Inject
    lateinit var viewModelFactory: UserDetailViewModel.Factory

    private val viewModel: UserDetailViewModel by viewModels {
        object : ViewModelProvider.Factory {
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                val config = arguments?.getParcelable<UserConfig>("config")!!
                @Suppress("UNCHECKED_CAST")
                return viewModelFactory.create(config) as T
            }
        }
    }
}
```

### Assisted Injection for Worker (WorkManager)

```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted appContext: Context,
    @Assisted workerParams: WorkerParameters,
    private val syncRepository: SyncRepository,
    private val notificationManager: NotificationManager
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        return try {
            val userId = inputData.getString("userId") ?: return Result.failure()
            syncRepository.syncUser(userId)
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
}

// Usage
class SyncManager @Inject constructor(
    private val workManager: WorkManager
) {

    fun scheduleSync(userId: String) {
        val inputData = Data.Builder()
            .putString("userId", userId)
            .build()

        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setInputData(inputData)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        workManager.enqueue(request)
    }
}
```

### Complex Example: Screen with Dynamic Configuration

```kotlin
// Domain model
data class ScreenConfig(
    val screenId: String,
    val featureFlags: FeatureFlags,
    val analyticsContext: AnalyticsContext
)

// Presenter with Assisted Injection
class DynamicScreenPresenter @AssistedInject constructor(
    private val contentRepository: ContentRepository,
    private val analyticsService: AnalyticsService,
    private val featureFlagManager: FeatureFlagManager,
    @Assisted private val config: ScreenConfig
) {

    private val _state = MutableStateFlow<ScreenState>(ScreenState.Loading)
    val state: StateFlow<ScreenState> = _state.asStateFlow()

    suspend fun loadContent() {
        _state.value = ScreenState.Loading

        try {
            val content = contentRepository.getContent(config.screenId)
            val processedContent = applyFeatureFlags(content)

            analyticsService.logScreenView(
                screenId = config.screenId,
                context = config.analyticsContext
            )

            _state.value = ScreenState.Success(processedContent)
        } catch (e: Exception) {
            _state.value = ScreenState.Error(e.message ?: "Unknown error")
        }
    }

    private fun applyFeatureFlags(content: Content): Content {
        return if (config.featureFlags.newLayoutEnabled) {
            content.withNewLayout()
        } else {
            content
        }
    }

    @AssistedFactory
    interface Factory {
        fun create(config: ScreenConfig): DynamicScreenPresenter
    }
}

sealed interface ScreenState {
    data object Loading : ScreenState
    data class Success(val content: Content) : ScreenState
    data class Error(val message: String) : ScreenState
}
```

### Rules and Limitations

1. **@AssistedInject** is applied to the class constructor
2. **@Assisted** marks runtime parameters
3. **@AssistedFactory** - interface with a single creation method
4. Factory is automatically implemented by Hilt
5. Cannot use scope annotations (@Singleton, etc.) with Assisted Injection
6. For ViewModel, prefer SavedStateHandle if parameters are serializable

---

## Dopolnitelnye Voprosy (RU)

- Почему нельзя использовать scope-аннотации с Assisted Injection?
- Как тестировать классы с Assisted Injection?
- В каких случаях SavedStateHandle лучше, чем Assisted Injection для ViewModel?
- Как Assisted Injection работает с Dagger Multibinding?

## Follow-ups

- Why can't you use scope annotations with Assisted Injection?
- How do you test classes with Assisted Injection?
- When is SavedStateHandle better than Assisted Injection for ViewModel?
- How does Assisted Injection work with Dagger Multibinding?

---

## Ssylki (RU)

- [Dagger Assisted Injection](https://dagger.dev/dev-guide/assisted-injection.html)
- [Hilt and WorkManager](https://developer.android.com/training/dependency-injection/hilt-jetpack#workmanager)

## References

- [Dagger Assisted Injection](https://dagger.dev/dev-guide/assisted-injection.html)
- [Hilt and WorkManager](https://developer.android.com/training/dependency-injection/hilt-jetpack#workmanager)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-viewmodel-injection--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-custom-components--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-viewmodel-injection--hilt--medium]]
- [[q-hilt-modules-provides--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-custom-components--hilt--hard]]
- [[q-hilt-entry-points--hilt--hard]]
