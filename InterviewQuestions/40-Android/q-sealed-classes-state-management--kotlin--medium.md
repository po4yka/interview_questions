---
id: 20251012-400005
title: "Sealed Classes for State Management / Sealed классы для управления состоянием"
topic: android
difficulty: medium
status: draft
created: 2025-10-12
tags: [sealed-classes, state-management, mvi, architecture, android/sealed-classes, android/state-management, android/mvi, android/architecture, difficulty/medium]
moc: moc-android
related: [q-which-layout-allows-views-to-overlap--android--easy, q-android14-permissions--permissions--medium, q-v-chyom-raznitsa-mezhdu-fragmentmanager-i-fragmenttransaction--programming-languages--medium]
  - q-mvi-architecture--android--hard
  - q-mvvm-architecture--android--medium
  - q-kotlin-coroutines-advanced--kotlin--hard
subtopics:
  - kotlin
  - sealed-classes
  - state-management
  - mvi
  - architecture
---
# Sealed Classes for State Management

## English Version

### Problem Statement

Sealed classes in Kotlin provide type-safe representation of restricted class hierarchies. They are perfect for modeling UI states, navigation events, and API results in Android architecture patterns like MVI and MVVM.

**The Question:** What are sealed classes and sealed interfaces? How do you use them for state management? What are the benefits over enums and inheritance?

### Detailed Answer

---

### SEALED CLASS BASICS

**Definition:**
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// Usage with exhaustive when
fun <T> handleResult(result: Result<T>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.exception.message}")
        is Result.Loading -> println("Loading...")
    }
    // No else needed - compiler ensures exhaustiveness 
}
```

**Key features:**
```
 Restricted type hierarchy
 All subclasses defined in same file (or nested)
 Exhaustive when expressions
 Type-safe state modeling
 Better than enums (can hold data)
 Better than abstract classes (exhaustiveness)
```

---

### UI STATE MODELING

```kotlin
sealed interface UiState<out T> {
    data object Idle : UiState<Nothing>
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String, val throwable: Throwable? = null) : UiState<Nothing>
}

// Example: User profile screen
data class UserProfile(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String
)

class ProfileViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<UserProfile>>(UiState.Idle)
    val uiState: StateFlow<UiState<UserProfile>> = _uiState.asStateFlow()

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val profile = userRepository.getProfile(userId)
                _uiState.value = UiState.Success(profile)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(
                    message = "Failed to load profile",
                    throwable = e
                )
            }
        }
    }
}

@Composable
fun ProfileScreen(viewModel: ProfileViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is UiState.Idle -> {
            // Show initial state
            Button(onClick = { viewModel.loadProfile("123") }) {
                Text("Load Profile")
            }
        }

        is UiState.Loading -> {
            CircularProgressIndicator()
        }

        is UiState.Success -> {
            ProfileContent(profile = state.data)
        }

        is UiState.Error -> {
            ErrorMessage(
                message = state.message,
                onRetry = { viewModel.loadProfile("123") }
            )
        }
    }
}
```

---

### SEALED INTERFACES (Kotlin 1.5+)

```kotlin
// Sealed interface allows multiple inheritance
sealed interface Response

sealed interface ApiResponse : Response {
    data class Success(val data: String) : ApiResponse
    data class Failure(val error: String) : ApiResponse
}

sealed interface CacheResponse : Response {
    data class Hit(val data: String) : CacheResponse
    data object Miss : CacheResponse
}

// Class can implement multiple sealed interfaces
data class HybridResponse(
    val apiData: String,
    val cacheHit: Boolean
) : ApiResponse, CacheResponse

// Usage
fun handleResponse(response: Response) {
    when (response) {
        is ApiResponse.Success -> println("API Success: ${response.data}")
        is ApiResponse.Failure -> println("API Failure: ${response.error}")
        is CacheResponse.Hit -> println("Cache Hit: ${response.data}")
        is CacheResponse.Miss -> println("Cache Miss")
        is HybridResponse -> println("Hybrid: ${response.apiData}")
    }
}
```

---

### MVI PATTERN WITH SEALED CLASSES

```kotlin
// Intent - User actions
sealed interface ProfileIntent {
    data class LoadProfile(val userId: String) : ProfileIntent
    data object RefreshProfile : ProfileIntent
    data class UpdateBio(val bio: String) : ProfileIntent
    data object Logout : ProfileIntent
}

// State - UI state
sealed interface ProfileState {
    data object Idle : ProfileState
    data object Loading : ProfileState
    data class Content(
        val profile: UserProfile,
        val isRefreshing: Boolean = false
    ) : ProfileState
    data class Error(val message: String) : ProfileState
}

// Effect - One-time events
sealed interface ProfileEffect {
    data class ShowToast(val message: String) : ProfileEffect
    data object NavigateToLogin : ProfileEffect
    data class NavigateToSettings(val userId: String) : ProfileEffect
}

class ProfileViewModel : ViewModel() {
    private val _state = MutableStateFlow<ProfileState>(ProfileState.Idle)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    private val _effect = MutableSharedFlow<ProfileEffect>()
    val effect: SharedFlow<ProfileEffect> = _effect.asSharedFlow()

    fun handleIntent(intent: ProfileIntent) {
        when (intent) {
            is ProfileIntent.LoadProfile -> loadProfile(intent.userId)
            is ProfileIntent.RefreshProfile -> refreshProfile()
            is ProfileIntent.UpdateBio -> updateBio(intent.bio)
            is ProfileIntent.Logout -> logout()
        }
    }

    private fun loadProfile(userId: String) {
        viewModelScope.launch {
            _state.value = ProfileState.Loading

            try {
                val profile = userRepository.getProfile(userId)
                _state.value = ProfileState.Content(profile)
            } catch (e: Exception) {
                _state.value = ProfileState.Error(e.message ?: "Unknown error")
                _effect.emit(ProfileEffect.ShowToast("Failed to load profile"))
            }
        }
    }

    private fun refreshProfile() {
        val currentState = _state.value
        if (currentState !is ProfileState.Content) return

        viewModelScope.launch {
            _state.value = currentState.copy(isRefreshing = true)

            try {
                val profile = userRepository.getProfile(currentState.profile.id)
                _state.value = ProfileState.Content(profile, isRefreshing = false)
                _effect.emit(ProfileEffect.ShowToast("Profile refreshed"))
            } catch (e: Exception) {
                _state.value = currentState.copy(isRefreshing = false)
                _effect.emit(ProfileEffect.ShowToast("Refresh failed"))
            }
        }
    }

    private fun updateBio(bio: String) {
        val currentState = _state.value
        if (currentState !is ProfileState.Content) return

        viewModelScope.launch {
            try {
                val updatedProfile = userRepository.updateBio(currentState.profile.id, bio)
                _state.value = ProfileState.Content(updatedProfile)
                _effect.emit(ProfileEffect.ShowToast("Bio updated"))
            } catch (e: Exception) {
                _effect.emit(ProfileEffect.ShowToast("Update failed"))
            }
        }
    }

    private fun logout() {
        viewModelScope.launch {
            userRepository.logout()
            _state.value = ProfileState.Idle
            _effect.emit(ProfileEffect.NavigateToLogin)
        }
    }
}

@Composable
fun ProfileScreen(viewModel: ProfileViewModel) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current

    // Handle one-time effects
    LaunchedEffect(Unit) {
        viewModel.effect.collect { effect ->
            when (effect) {
                is ProfileEffect.ShowToast -> {
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                }
                is ProfileEffect.NavigateToLogin -> {
                    // Navigate to login
                }
                is ProfileEffect.NavigateToSettings -> {
                    // Navigate to settings
                }
            }
        }
    }

    // Render based on state
    when (val currentState = state) {
        is ProfileState.Idle -> {
            // Show initial screen
        }
        is ProfileState.Loading -> {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
        is ProfileState.Content -> {
            ProfileContent(
                profile = currentState.profile,
                isRefreshing = currentState.isRefreshing,
                onRefresh = { viewModel.handleIntent(ProfileIntent.RefreshProfile) },
                onUpdateBio = { bio ->
                    viewModel.handleIntent(ProfileIntent.UpdateBio(bio))
                },
                onLogout = { viewModel.handleIntent(ProfileIntent.Logout) }
            )
        }
        is ProfileState.Error -> {
            ErrorScreen(message = currentState.message)
        }
    }
}
```

---

### NETWORK RESPONSE MODELING

```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()

    sealed class Error : NetworkResult<Nothing>() {
        data class HttpError(val code: Int, val message: String) : Error()
        data class NetworkError(val exception: IOException) : Error()
        data class UnknownError(val throwable: Throwable) : Error()
    }

    data object Loading : NetworkResult<Nothing>()
}

class UserRepository(private val api: ApiService) {
    suspend fun getUser(id: String): NetworkResult<User> {
        return try {
            val response = api.getUser(id)

            if (response.isSuccessful) {
                response.body()?.let {
                    NetworkResult.Success(it)
                } ?: NetworkResult.Error.UnknownError(
                    NullPointerException("Response body is null")
                )
            } else {
                NetworkResult.Error.HttpError(
                    code = response.code(),
                    message = response.message()
                )
            }
        } catch (e: IOException) {
            NetworkResult.Error.NetworkError(e)
        } catch (e: Exception) {
            NetworkResult.Error.UnknownError(e)
        }
    }
}

// Usage
viewModelScope.launch {
    when (val result = userRepository.getUser("123")) {
        is NetworkResult.Success -> {
            _uiState.value = UiState.Success(result.data)
        }
        is NetworkResult.Error.HttpError -> {
            _uiState.value = UiState.Error(
                "HTTP Error ${result.code}: ${result.message}"
            )
        }
        is NetworkResult.Error.NetworkError -> {
            _uiState.value = UiState.Error("Network error: Check your connection")
        }
        is NetworkResult.Error.UnknownError -> {
            _uiState.value = UiState.Error("Unknown error occurred")
        }
        is NetworkResult.Loading -> {
            _uiState.value = UiState.Loading
        }
    }
}
```

---

### NAVIGATION EVENTS

```kotlin
sealed interface NavigationEvent {
    data object NavigateBack : NavigationEvent

    sealed interface NavigateToScreen : NavigationEvent {
        data class Profile(val userId: String) : NavigateToScreen
        data class Settings(val section: String? = null) : NavigateToScreen
        data class Detail(val itemId: String, val title: String) : NavigateToScreen
        data object Home : NavigateToScreen
    }

    sealed interface ExternalNavigation : NavigationEvent {
        data class OpenUrl(val url: String) : ExternalNavigation
        data class ShareText(val text: String) : ExternalNavigation
        data class OpenEmail(val email: String) : ExternalNavigation
    }
}

class NavigationViewModel : ViewModel() {
    private val _navigationEvent = MutableSharedFlow<NavigationEvent>()
    val navigationEvent: SharedFlow<NavigationEvent> = _navigationEvent.asSharedFlow()

    fun navigate(event: NavigationEvent) {
        viewModelScope.launch {
            _navigationEvent.emit(event)
        }
    }
}

@Composable
fun MainScreen(
    navController: NavController,
    viewModel: NavigationViewModel
) {
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        viewModel.navigationEvent.collect { event ->
            when (event) {
                is NavigationEvent.NavigateBack -> {
                    navController.popBackStack()
                }
                is NavigationEvent.NavigateToScreen.Profile -> {
                    navController.navigate("profile/${event.userId}")
                }
                is NavigationEvent.NavigateToScreen.Settings -> {
                    val route = event.section?.let { "settings/$it" } ?: "settings"
                    navController.navigate(route)
                }
                is NavigationEvent.NavigateToScreen.Detail -> {
                    navController.navigate("detail/${event.itemId}")
                }
                is NavigationEvent.NavigateToScreen.Home -> {
                    navController.navigate("home") {
                        popUpTo(navController.graph.startDestinationId) {
                            inclusive = true
                        }
                    }
                }
                is NavigationEvent.ExternalNavigation.OpenUrl -> {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(event.url))
                    context.startActivity(intent)
                }
                is NavigationEvent.ExternalNavigation.ShareText -> {
                    val intent = Intent().apply {
                        action = Intent.ACTION_SEND
                        putExtra(Intent.EXTRA_TEXT, event.text)
                        type = "text/plain"
                    }
                    context.startActivity(Intent.createChooser(intent, "Share"))
                }
                is NavigationEvent.ExternalNavigation.OpenEmail -> {
                    val intent = Intent(Intent.ACTION_SENDTO).apply {
                        data = Uri.parse("mailto:${event.email}")
                    }
                    context.startActivity(intent)
                }
            }
        }
    }

    // UI content
}
```

---

### FORM VALIDATION

```kotlin
sealed interface ValidationResult {
    data object Valid : ValidationResult

    sealed interface Invalid : ValidationResult {
        data class FieldError(val field: String, val message: String) : Invalid
        data class MultipleErrors(val errors: List<FieldError>) : Invalid
    }
}

data class RegistrationForm(
    val email: String = "",
    val password: String = "",
    val confirmPassword: String = "",
    val age: String = ""
)

object FormValidator {
    fun validateRegistration(form: RegistrationForm): ValidationResult {
        val errors = mutableListOf<ValidationResult.Invalid.FieldError>()

        // Email validation
        if (form.email.isBlank()) {
            errors.add(ValidationResult.Invalid.FieldError("email", "Email is required"))
        } else if (!form.email.contains("@")) {
            errors.add(ValidationResult.Invalid.FieldError("email", "Invalid email format"))
        }

        // Password validation
        if (form.password.length < 8) {
            errors.add(
                ValidationResult.Invalid.FieldError(
                    "password",
                    "Password must be at least 8 characters"
                )
            )
        }

        // Confirm password
        if (form.password != form.confirmPassword) {
            errors.add(
                ValidationResult.Invalid.FieldError(
                    "confirmPassword",
                    "Passwords do not match"
                )
            )
        }

        // Age validation
        val ageInt = form.age.toIntOrNull()
        if (ageInt == null) {
            errors.add(ValidationResult.Invalid.FieldError("age", "Age must be a number"))
        } else if (ageInt < 18) {
            errors.add(ValidationResult.Invalid.FieldError("age", "Must be 18 or older"))
        }

        return when {
            errors.isEmpty() -> ValidationResult.Valid
            errors.size == 1 -> errors.first()
            else -> ValidationResult.Invalid.MultipleErrors(errors)
        }
    }
}

@Composable
fun RegistrationScreen() {
    var form by remember { mutableStateOf(RegistrationForm()) }
    var validationResult by remember { mutableStateOf<ValidationResult>(ValidationResult.Valid) }

    Column(modifier = Modifier.padding(16.dp)) {
        TextField(
            value = form.email,
            onValueChange = { form = form.copy(email = it) },
            label = { Text("Email") },
            isError = validationResult is ValidationResult.Invalid.FieldError &&
                    (validationResult as ValidationResult.Invalid.FieldError).field == "email"
        )

        // Show error
        if (validationResult is ValidationResult.Invalid.FieldError &&
            (validationResult as ValidationResult.Invalid.FieldError).field == "email"
        ) {
            Text(
                text = (validationResult as ValidationResult.Invalid.FieldError).message,
                color = MaterialTheme.colorScheme.error
            )
        }

        // Other fields...

        Button(
            onClick = {
                validationResult = FormValidator.validateRegistration(form)

                when (validationResult) {
                    is ValidationResult.Valid -> {
                        // Submit form
                    }
                    is ValidationResult.Invalid -> {
                        // Show errors (already shown inline)
                    }
                }
            }
        ) {
            Text("Register")
        }
    }
}
```

---

### PERMISSION HANDLING

```kotlin
sealed interface PermissionState {
    data object NotRequested : PermissionState
    data object Granted : PermissionState

    sealed interface Denied : PermissionState {
        data object DeniedOnce : Denied
        data object PermanentlyDenied : Denied
    }

    data object Requesting : PermissionState
}

class PermissionManager(private val context: Context) {
    fun checkPermission(permission: String): PermissionState {
        return when {
            ContextCompat.checkSelfPermission(
                context,
                permission
            ) == PackageManager.PERMISSION_GRANTED -> {
                PermissionState.Granted
            }

            ActivityCompat.shouldShowRequestPermissionRationale(
                context as Activity,
                permission
            ) -> {
                PermissionState.Denied.DeniedOnce
            }

            else -> {
                PermissionState.NotRequested
            }
        }
    }

    fun handlePermissionResult(
        permission: String,
        granted: Boolean
    ): PermissionState {
        return if (granted) {
            PermissionState.Granted
        } else {
            if (ActivityCompat.shouldShowRequestPermissionRationale(
                    context as Activity,
                    permission
                )
            ) {
                PermissionState.Denied.DeniedOnce
            } else {
                PermissionState.Denied.PermanentlyDenied
            }
        }
    }
}

@Composable
fun CameraScreen() {
    var permissionState by remember {
        mutableStateOf<PermissionState>(PermissionState.NotRequested)
    }

    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        permissionState = if (granted) {
            PermissionState.Granted
        } else {
            PermissionState.Denied.PermanentlyDenied
        }
    }

    when (val state = permissionState) {
        is PermissionState.NotRequested -> {
            Button(onClick = {
                permissionState = PermissionState.Requesting
                launcher.launch(Manifest.permission.CAMERA)
            }) {
                Text("Request Camera Permission")
            }
        }

        is PermissionState.Granted -> {
            // Show camera preview
            Text("Camera permission granted!")
        }

        is PermissionState.Denied.DeniedOnce -> {
            Column {
                Text("Camera permission needed for this feature")
                Button(onClick = {
                    launcher.launch(Manifest.permission.CAMERA)
                }) {
                    Text("Grant Permission")
                }
            }
        }

        is PermissionState.Denied.PermanentlyDenied -> {
            Column {
                Text("Camera permission permanently denied")
                Button(onClick = {
                    // Open app settings
                }) {
                    Text("Open Settings")
                }
            }
        }

        is PermissionState.Requesting -> {
            CircularProgressIndicator()
        }
    }
}
```

---

### SEALED CLASS VS ENUM

```kotlin
//  Enum - limited capabilities
enum class Status {
    SUCCESS,
    ERROR,
    LOADING
}
// Can't hold data, can't have subclasses

//  Sealed class - flexible
sealed class Status {
    data class Success(val data: String) : Status()
    data class Error(val exception: Exception) : Status()
    data object Loading : Status()
}
// Can hold different data, type-safe
```

---

### KEY TAKEAWAYS

1. **Sealed classes** restrict type hierarchies to known subtypes
2. **Exhaustive when** - compiler ensures all cases handled
3. **UI state modeling** - Idle, Loading, Success, Error pattern
4. **MVI pattern** - Intent, State, Effect with sealed classes
5. **Network responses** - type-safe error handling
6. **Navigation events** - structured navigation
7. **Sealed interfaces** (Kotlin 1.5+) allow multiple inheritance
8. **Better than enums** - can hold data and have methods
9. **data object** (Kotlin 1.7+) for singleton sealed subclasses
10. **Type safety** - impossible states become impossible

---

### Подробный ответ

---

### ОСНОВЫ SEALED КЛАССОВ

**Определение:**
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// Использование с исчерпывающим when
fun <T> handleResult(result: Result<T>) {
    when (result) {
        is Result.Success -> println("Данные: ${result.data}")
        is Result.Error -> println("Ошибка: ${result.exception.message}")
        is Result.Loading -> println("Загрузка...")
    }
    // else не нужен - компилятор обеспечивает исчерпываемость
}
```

**Ключевые особенности:**
```
 Ограниченная иерархия типов
 Все подклассы определены в том же файле (или вложены)
 Исчерпывающие выражения when
 Типобезопасное моделирование состояний
 Лучше, чем enums (могут хранить данные)
 Лучше, чем абстрактные классы (исчерпываемость)
```

---

### МОДЕЛИРОВАНИЕ UI СОСТОЯНИЯ

```kotlin
sealed interface UiState<out T> {
    data object Idle : UiState<Nothing>
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String, val throwable: Throwable? = null) : UiState<Nothing>
}

// Пример: экран профиля пользователя
data class UserProfile(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String
)

class ProfileViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<UserProfile>>(UiState.Idle)
    val uiState: StateFlow<UiState<UserProfile>> = _uiState.asStateFlow()

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val profile = userRepository.getProfile(userId)
                _uiState.value = UiState.Success(profile)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(
                    message = "Не удалось загрузить профиль",
                    throwable = e
                )
            }
        }
    }
}

@Composable
fun ProfileScreen(viewModel: ProfileViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is UiState.Idle -> {
            // Показать начальное состояние
            Button(onClick = { viewModel.loadProfile("123") }) {
                Text("Загрузить профиль")
            }
        }

        is UiState.Loading -> {
            CircularProgressIndicator()
        }

        is UiState.Success -> {
            ProfileContent(profile = state.data)
        }

        is UiState.Error -> {
            ErrorMessage(
                message = state.message,
                onRetry = { viewModel.loadProfile("123") }
            )
        }
    }
}
```

---

### SEALED ИНТЕРФЕЙСЫ (Kotlin 1.5+)

```kotlin
// Sealed интерфейс позволяет множественное наследование
sealed interface Response

sealed interface ApiResponse : Response {
    data class Success(val data: String) : ApiResponse
    data class Failure(val error: String) : ApiResponse
}

sealed interface CacheResponse : Response {
    data class Hit(val data: String) : CacheResponse
    data object Miss : CacheResponse
}

// Класс может реализовывать несколько sealed интерфейсов
data class HybridResponse(
    val apiData: String,
    val cacheHit: Boolean
) : ApiResponse, CacheResponse

// Использование
fun handleResponse(response: Response) {
    when (response) {
        is ApiResponse.Success -> println("API Успех: ${response.data}")
        is ApiResponse.Failure -> println("API Ошибка: ${response.error}")
        is CacheResponse.Hit -> println("Кэш Попадание: ${response.data}")
        is CacheResponse.Miss -> println("Кэш Промах")
        is HybridResponse -> println("Гибрид: ${response.apiData}")
    }
}
```

---

### ПАТТЕРН MVI С SEALED КЛАССАМИ

```kotlin
// Intent - Действия пользователя
sealed interface ProfileIntent {
    data class LoadProfile(val userId: String) : ProfileIntent
    data object RefreshProfile : ProfileIntent
    data class UpdateBio(val bio: String) : ProfileIntent
    data object Logout : ProfileIntent
}

// State - Состояние UI
sealed interface ProfileState {
    data object Idle : ProfileState
    data object Loading : ProfileState
    data class Content(
        val profile: UserProfile,
        val isRefreshing: Boolean = false
    ) : ProfileState
    data class Error(val message: String) : ProfileState
}

// Effect - Одноразовые события
sealed interface ProfileEffect {
    data class ShowToast(val message: String) : ProfileEffect
    data object NavigateToLogin : ProfileEffect
    data class NavigateToSettings(val userId: String) : ProfileEffect
}

// ... (остальной код ViewModel и Composable как в английской версии, с переведенными строками)
```

---

### МОДЕЛИРОВАНИЕ СЕТЕВЫХ ОТВЕТОВ

```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()

    sealed class Error : NetworkResult<Nothing>() {
        data class HttpError(val code: Int, val message: String) : Error()
        data class NetworkError(val exception: IOException) : Error()
        data class UnknownError(val throwable: Throwable) : Error()
    }

    data object Loading : NetworkResult<Nothing>()
}

// ... (остальной код UserRepository и ViewModel как в английской версии, с переведенными строками)
```

---

### СОБЫТИЯ НАВИГАЦИИ

```kotlin
sealed interface NavigationEvent {
    data object NavigateBack : NavigationEvent

    sealed interface NavigateToScreen : NavigationEvent {
        data class Profile(val userId: String) : NavigateToScreen
        data class Settings(val section: String? = null) : NavigateToScreen
        data class Detail(val itemId: String, val title: String) : NavigateToScreen
        data object Home : NavigateToScreen
    }

    sealed interface ExternalNavigation : NavigationEvent {
        data class OpenUrl(val url: String) : ExternalNavigation
        data class ShareText(val text: String) : ExternalNavigation
        data class OpenEmail(val email: String) : ExternalNavigation
    }
}

// ... (остальной код NavigationViewModel и Composable как в английской версии)
```

---

### ВАЛИДАЦИЯ ФОРМ

```kotlin
sealed interface ValidationResult {
    data object Valid : ValidationResult

    sealed interface Invalid : ValidationResult {
        data class FieldError(val field: String, val message: String) : Invalid
        data class MultipleErrors(val errors: List<FieldError>) : Invalid
    }
}

// ... (остальной код FormValidator и Composable как в английской версии, с переведенными строками)
```

---

### ОБРАБОТКА РАЗРЕШЕНИЙ

```kotlin
sealed interface PermissionState {
    data object NotRequested : PermissionState
    data object Granted : PermissionState

    sealed interface Denied : PermissionState {
        data object DeniedOnce : Denied
        data object PermanentlyDenied : Denied
    }

    data object Requesting : PermissionState
}

// ... (остальной код PermissionManager и Composable как в английской версии, с переведенными строками)
```

---

### SEALED КЛАСС VS ENUM

```kotlin
// Enum - ограниченные возможности
enum class Status {
    SUCCESS,
    ERROR,
    LOADING
}
// Не может хранить данные, не может иметь подклассы

// Sealed класс - гибкий
sealed class Status {
    data class Success(val data: String) : Status()
    data class Error(val exception: Exception) : Status()
    data object Loading : Status()
}
// Может хранить разные данные, типобезопасен
```

## Follow-ups

1. How do sealed classes differ from abstract classes?
2. What is the performance impact of sealed classes?
3. How do you serialize sealed classes with kotlinx.serialization?
4. What are sealed interfaces and when to use them?
5. How do you test code with sealed classes?
6. What is the difference between sealed class and enum class?
7. How do you handle versioning with sealed classes in APIs?
8. What are the best practices for naming sealed class hierarchies?
9. How do you use sealed classes with Room database?
10. What is the relationship between sealed classes and exhaustive when?

## Related Questions

- [[q-which-layout-allows-views-to-overlap--android--easy]]
- [[q-android14-permissions--permissions--medium]]
- [[q-v-chyom-raznitsa-mezhdu-fragmentmanager-i-fragmenttransaction--programming-languages--medium]]
