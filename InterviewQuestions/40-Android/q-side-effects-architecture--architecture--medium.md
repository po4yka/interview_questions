---
id: android-arch-004
title: Side Effects in Reactive Architecture / Побочные эффекты в реактивной архитектуре
aliases:
- Side Effects
- Effects in MVI
- Побочные эффекты
- Эффекты в MVI
topic: android
subtopics:
- architecture
- state-management
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-mvi-architecture--android--hard
- q-mvi-one-time-events--android--medium
- q-unidirectional-data-flow--architecture--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- https://developer.android.com/topic/architecture/ui-layer/events
- https://orbit-mvi.org/Core/side-effects
tags:
- android/architecture
- android/state-management
- difficulty/medium
- side-effects
anki_cards:
- slug: android-arch-004-0-en
  language: en
- slug: android-arch-004-0-ru
  language: ru
---
# Vopros (RU)

> Как правильно обрабатывать побочные эффекты (side effects) в реактивной архитектуре? Объясните разницу между state и effects.

# Question (EN)

> How to properly handle side effects in reactive architecture? Explain the difference between state and effects.

---

## Otvet (RU)

**Side Effects (побочные эффекты)** - это действия, которые не влияют на UI state напрямую, но должны быть выполнены в ответ на события: навигация, показ toast/snackbar, аналитика, вибрация.

### State vs Side Effects

| Характеристика | State | Side Effect |
|----------------|-------|-------------|
| **Персистентность** | Сохраняется между recomposition | Одноразовый |
| **При повороте экрана** | Восстанавливается | Не должен повторяться |
| **Пример** | `isLoading`, `items`, `error` | `navigateTo`, `showToast` |
| **Хранение** | `StateFlow` | `Channel` / `SharedFlow(replay=0)` |

### Типы Side Effects

```kotlin
sealed interface SideEffect {
    // Навигация
    data class Navigate(val route: String) : SideEffect
    data object NavigateBack : SideEffect

    // Уведомления пользователю
    data class ShowSnackbar(val message: String, val action: String? = null) : SideEffect
    data class ShowToast(val message: String) : SideEffect

    // Внешние действия
    data class OpenUrl(val url: String) : SideEffect
    data class ShareContent(val text: String) : SideEffect
    data class CopyToClipboard(val text: String) : SideEffect

    // Системные
    data object HideKeyboard : SideEffect
    data class Vibrate(val duration: Long = 50) : SideEffect

    // Аналитика
    data class TrackEvent(val name: String, val params: Map<String, Any> = emptyMap()) : SideEffect
}
```

### Реализация Side Effects

#### 1. Channel (рекомендуется для единственного потребителя)

```kotlin
@HiltViewModel
class ProductViewModel @Inject constructor(
    private val productRepository: ProductRepository,
    private val cartRepository: CartRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ProductState())
    val state: StateFlow<ProductState> = _state.asStateFlow()

    // Channel для side effects - гарантирует доставку
    private val _effects = Channel<SideEffect>(Channel.BUFFERED)
    val effects: Flow<SideEffect> = _effects.receiveAsFlow()

    fun onAddToCart(productId: String) {
        viewModelScope.launch {
            _state.update { it.copy(isAddingToCart = true) }

            cartRepository.addToCart(productId)
                .onSuccess {
                    _state.update { it.copy(isAddingToCart = false) }
                    // Side effect: показать snackbar
                    _effects.send(SideEffect.ShowSnackbar("Added to cart", "View Cart"))
                    // Side effect: аналитика
                    _effects.send(SideEffect.TrackEvent("add_to_cart", mapOf("product_id" to productId)))
                }
                .onFailure { error ->
                    _state.update { it.copy(isAddingToCart = false) }
                    _effects.send(SideEffect.ShowToast(error.message ?: "Error"))
                }
        }
    }

    fun onBuyNow(productId: String) {
        viewModelScope.launch {
            _effects.send(SideEffect.Navigate("checkout/$productId"))
        }
    }
}
```

#### 2. Обработка в UI (Compose)

```kotlin
@Composable
fun ProductScreen(
    viewModel: ProductViewModel = hiltViewModel(),
    onNavigate: (String) -> Unit
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }

    // Обработка side effects
    LaunchedEffect(Unit) {
        viewModel.effects.collect { effect ->
            when (effect) {
                is SideEffect.Navigate -> {
                    onNavigate(effect.route)
                }
                is SideEffect.NavigateBack -> {
                    // handled by navigation
                }
                is SideEffect.ShowSnackbar -> {
                    val result = snackbarHostState.showSnackbar(
                        message = effect.message,
                        actionLabel = effect.action,
                        duration = SnackbarDuration.Short
                    )
                    if (result == SnackbarResult.ActionPerformed) {
                        onNavigate("cart")
                    }
                }
                is SideEffect.ShowToast -> {
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                }
                is SideEffect.OpenUrl -> {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(effect.url))
                    context.startActivity(intent)
                }
                is SideEffect.CopyToClipboard -> {
                    val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    clipboard.setPrimaryClip(ClipData.newPlainText("text", effect.text))
                }
                is SideEffect.HideKeyboard -> {
                    val imm = context.getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
                    imm.hideSoftInputFromWindow(null, 0)
                }
                is SideEffect.Vibrate -> {
                    val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        vibrator.vibrate(VibrationEffect.createOneShot(effect.duration, VibrationEffect.DEFAULT_AMPLITUDE))
                    }
                }
                is SideEffect.TrackEvent -> {
                    // Analytics tracking
                }
                is SideEffect.ShareContent -> {
                    val intent = Intent(Intent.ACTION_SEND).apply {
                        type = "text/plain"
                        putExtra(Intent.EXTRA_TEXT, effect.text)
                    }
                    context.startActivity(Intent.createChooser(intent, "Share"))
                }
            }
        }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { padding ->
        ProductContent(
            state = state,
            onAddToCart = viewModel::onAddToCart,
            onBuyNow = viewModel::onBuyNow,
            modifier = Modifier.padding(padding)
        )
    }
}
```

### Паттерн Effect Handler

Для переиспользования логики обработки effects:

```kotlin
// Централизованный обработчик effects
class EffectHandler(
    private val context: Context,
    private val snackbarHostState: SnackbarHostState,
    private val navigator: Navigator,
    private val analytics: Analytics
) {
    suspend fun handle(effect: SideEffect) {
        when (effect) {
            is SideEffect.Navigate -> navigator.navigate(effect.route)
            is SideEffect.NavigateBack -> navigator.navigateBack()
            is SideEffect.ShowSnackbar -> {
                snackbarHostState.showSnackbar(effect.message, effect.action)
            }
            is SideEffect.ShowToast -> {
                Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
            }
            is SideEffect.TrackEvent -> {
                analytics.track(effect.name, effect.params)
            }
            // ... остальные
            else -> Unit
        }
    }
}

// Composable helper
@Composable
fun HandleEffects(
    effects: Flow<SideEffect>,
    onNavigate: (String) -> Unit = {},
    onNavigateBack: () -> Unit = {}
) {
    val context = LocalContext.current
    val snackbarHostState = LocalSnackbarHostState.current

    LaunchedEffect(Unit) {
        effects.collect { effect ->
            when (effect) {
                is SideEffect.Navigate -> onNavigate(effect.route)
                is SideEffect.NavigateBack -> onNavigateBack()
                is SideEffect.ShowSnackbar -> {
                    snackbarHostState.showSnackbar(effect.message, effect.action)
                }
                is SideEffect.ShowToast -> {
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                }
                else -> Unit
            }
        }
    }
}

// Использование
@Composable
fun ProductScreen(viewModel: ProductViewModel = hiltViewModel()) {
    HandleEffects(
        effects = viewModel.effects,
        onNavigate = { route -> navController.navigate(route) },
        onNavigateBack = { navController.popBackStack() }
    )

    // UI content
}
```

### Conditional Side Effects

```kotlin
// Side effects с условиями
class LoginViewModel : ViewModel() {

    fun onLoginClicked(email: String, password: String) {
        viewModelScope.launch {
            // Валидация перед side effect
            if (!isValidEmail(email)) {
                _state.update { it.copy(emailError = "Invalid email") }
                return@launch
            }

            _state.update { it.copy(isLoading = true) }

            authRepository.login(email, password)
                .onSuccess { user ->
                    _state.update { it.copy(isLoading = false) }

                    // Conditional navigation
                    val route = if (user.isNewUser) {
                        "onboarding"
                    } else {
                        "home"
                    }
                    _effects.send(SideEffect.Navigate(route))

                    // Conditional analytics
                    if (user.isNewUser) {
                        _effects.send(SideEffect.TrackEvent("new_user_login"))
                    } else {
                        _effects.send(SideEffect.TrackEvent("returning_user_login"))
                    }
                }
                .onFailure { error ->
                    _state.update { it.copy(isLoading = false) }
                    _effects.send(SideEffect.ShowSnackbar(error.message ?: "Login failed"))
                }
        }
    }
}
```

### Side Effects в Compose (LaunchedEffect, SideEffect)

```kotlin
@Composable
fun ProductScreen(viewModel: ProductViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // LaunchedEffect - для coroutine side effects
    LaunchedEffect(state.searchQuery) {
        delay(300) // Debounce
        viewModel.search(state.searchQuery)
    }

    // SideEffect - для non-suspend side effects каждой recomposition
    SideEffect {
        // Вызывается при каждой успешной recomposition
        // Используйте осторожно!
        analytics.trackScreenView("ProductScreen")
    }

    // DisposableEffect - для cleanup
    DisposableEffect(Unit) {
        val listener = viewModel.registerListener()
        onDispose {
            listener.unregister()
        }
    }

    // Content
}
```

### Тестирование Side Effects

```kotlin
class ProductViewModelTest {

    @Test
    fun `addToCart success emits snackbar effect`() = runTest {
        // Given
        val repository = mockk<CartRepository> {
            coEvery { addToCart(any()) } returns Result.success(Unit)
        }
        val viewModel = ProductViewModel(mockk(), repository)

        // When
        val effects = mutableListOf<SideEffect>()
        val job = launch {
            viewModel.effects.toList(effects)
        }

        viewModel.onAddToCart("product-1")
        advanceUntilIdle()

        // Then
        assertTrue(effects.any { it is SideEffect.ShowSnackbar })
        assertTrue(effects.any { it is SideEffect.TrackEvent })

        job.cancel()
    }

    @Test
    fun `buyNow emits navigation effect`() = runTest {
        val viewModel = ProductViewModel(mockk(), mockk())

        val effects = mutableListOf<SideEffect>()
        val job = launch {
            viewModel.effects.toList(effects)
        }

        viewModel.onBuyNow("product-1")
        advanceUntilIdle()

        val navEffect = effects.filterIsInstance<SideEffect.Navigate>().first()
        assertEquals("checkout/product-1", navEffect.route)

        job.cancel()
    }
}
```

### Best Practices

| DO | DON'T |
|----|----- |
| Используйте Channel для one-time effects | SharedFlow с replay > 0 для events |
| Обрабатывайте effects в LaunchedEffect | Обработка в Composable напрямую |
| Типизируйте effects через sealed class | String-based effects |
| Тестируйте effects отдельно от state | Игнорирование тестов effects |
| Централизуйте обработку в handler | Дублирование логики в каждом экране |

---

## Answer (EN)

**Side Effects** are actions that don't directly affect UI state but must be performed in response to events: navigation, showing toast/snackbar, analytics, vibration.

### State vs Side Effects

| Characteristic | State | Side Effect |
|----------------|-------|-------------|
| **Persistence** | Preserved across recomposition | One-time |
| **On rotation** | Restored | Should not repeat |
| **Example** | `isLoading`, `items`, `error` | `navigateTo`, `showToast` |
| **Storage** | `StateFlow` | `Channel` / `SharedFlow(replay=0)` |

### Types of Side Effects

```kotlin
sealed interface SideEffect {
    // Navigation
    data class Navigate(val route: String) : SideEffect
    data object NavigateBack : SideEffect

    // User notifications
    data class ShowSnackbar(val message: String, val action: String? = null) : SideEffect
    data class ShowToast(val message: String) : SideEffect

    // External actions
    data class OpenUrl(val url: String) : SideEffect
    data class ShareContent(val text: String) : SideEffect
    data class CopyToClipboard(val text: String) : SideEffect

    // System
    data object HideKeyboard : SideEffect
    data class Vibrate(val duration: Long = 50) : SideEffect

    // Analytics
    data class TrackEvent(val name: String, val params: Map<String, Any> = emptyMap()) : SideEffect
}
```

### Implementation

#### 1. Channel (recommended for single consumer)

```kotlin
@HiltViewModel
class ProductViewModel @Inject constructor(
    private val cartRepository: CartRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ProductState())
    val state: StateFlow<ProductState> = _state.asStateFlow()

    // Channel for side effects - guarantees delivery
    private val _effects = Channel<SideEffect>(Channel.BUFFERED)
    val effects: Flow<SideEffect> = _effects.receiveAsFlow()

    fun onAddToCart(productId: String) {
        viewModelScope.launch {
            _state.update { it.copy(isAddingToCart = true) }

            cartRepository.addToCart(productId)
                .onSuccess {
                    _state.update { it.copy(isAddingToCart = false) }
                    _effects.send(SideEffect.ShowSnackbar("Added to cart"))
                    _effects.send(SideEffect.TrackEvent("add_to_cart"))
                }
                .onFailure { error ->
                    _state.update { it.copy(isAddingToCart = false) }
                    _effects.send(SideEffect.ShowToast(error.message ?: "Error"))
                }
        }
    }
}
```

#### 2. Handling in UI (Compose)

```kotlin
@Composable
fun ProductScreen(
    viewModel: ProductViewModel = hiltViewModel(),
    onNavigate: (String) -> Unit
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }

    // Handle side effects
    LaunchedEffect(Unit) {
        viewModel.effects.collect { effect ->
            when (effect) {
                is SideEffect.Navigate -> onNavigate(effect.route)
                is SideEffect.ShowSnackbar -> {
                    snackbarHostState.showSnackbar(effect.message, effect.action)
                }
                is SideEffect.ShowToast -> {
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                }
                // ... handle other effects
                else -> Unit
            }
        }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { padding ->
        ProductContent(state = state, modifier = Modifier.padding(padding))
    }
}
```

### Testing Side Effects

```kotlin
@Test
fun `addToCart success emits snackbar effect`() = runTest {
    val repository = mockk<CartRepository> {
        coEvery { addToCart(any()) } returns Result.success(Unit)
    }
    val viewModel = ProductViewModel(repository)

    val effects = mutableListOf<SideEffect>()
    val job = launch { viewModel.effects.toList(effects) }

    viewModel.onAddToCart("product-1")
    advanceUntilIdle()

    assertTrue(effects.any { it is SideEffect.ShowSnackbar })
    job.cancel()
}
```

### Best Practices

| DO | DON'T |
|----|----- |
| Use Channel for one-time effects | SharedFlow with replay > 0 for events |
| Handle effects in LaunchedEffect | Handle directly in Composable |
| Type effects with sealed class | String-based effects |
| Test effects separately from state | Ignore effect tests |

---

## Follow-ups

- How do you handle side effects that need a response (e.g., confirm dialog)?
- What happens to effects emitted when UI is in background?
- How do you batch multiple side effects?
- When should you use SideEffect composable vs LaunchedEffect?

## References

- https://developer.android.com/topic/architecture/ui-layer/events
- [[q-mvi-one-time-events--android--medium]] - One-time events in MVI

## Related Questions

### Prerequisites

- [[q-mvi-architecture--android--hard]] - MVI basics
- [[q-channel-flow-comparison--kotlin--medium]] - Channel vs Flow

### Related

- [[q-mvi-one-time-events--android--medium]] - One-time events
- [[q-unidirectional-data-flow--architecture--medium]] - UDF principles

### Advanced

- [[q-orbit-mvi--architecture--medium]] - Orbit side effects
- [[q-circuit-framework--architecture--medium]] - Circuit overlay effects
