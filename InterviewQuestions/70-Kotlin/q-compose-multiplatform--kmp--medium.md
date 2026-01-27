---
id: kotlin-kmp-004
title: Compose Multiplatform / Compose Multiplatform
aliases:
- Compose Multiplatform
- Shared UI KMP
- Cross-Platform Compose
topic: kotlin
subtopics:
- kmp
- multiplatform
- compose
- ui
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- kmp
- multiplatform
- compose
- ui
- difficulty/medium
anki_cards:
- slug: kotlin-kmp-004-0-en
  language: en
  anki_id: 1769344142240
  synced_at: '2026-01-25T16:29:02.292369'
- slug: kotlin-kmp-004-0-ru
  language: ru
  anki_id: 1769344142290
  synced_at: '2026-01-25T16:29:02.294059'
---
# Question (EN)
> What is Compose Multiplatform and how does it enable UI sharing in KMP projects?

# Vopros (RU)
> Что такое Compose Multiplatform и как он позволяет разделять UI в KMP проектах?

## Answer (EN)

**Compose Multiplatform** is JetBrains' declarative UI framework that extends Jetpack Compose beyond Android to iOS, Desktop (JVM), and Web. As of 2026, it is stable for production use on all major platforms.

### Core Concept

Write UI once in Kotlin, run on multiple platforms:

```kotlin
// commonMain - Shared UI code
@Composable
fun UserCard(user: User, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )
            Spacer(Modifier.width(16.dp))
            Column {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
```

### Platform Support (2026)

| Platform | Status | Notes |
|----------|--------|-------|
| **Android** | Stable | Native Jetpack Compose |
| **iOS** | Stable | Uses Skia/Skiko for rendering |
| **Desktop** | Stable | JVM-based, uses Skia |
| **Web** | Stable | Kotlin/Wasm (Canvas) or Kotlin/JS |

### Project Setup

```kotlin
// build.gradle.kts (shared module)
plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose")
}

kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()
    jvm("desktop")

    sourceSets {
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)
            implementation(compose.components.uiToolingPreview)
        }

        androidMain.dependencies {
            implementation(compose.preview)
            implementation(libs.androidx.activity.compose)
        }

        val desktopMain by getting {
            dependencies {
                implementation(compose.desktop.currentOs)
            }
        }
    }
}
```

### Shared Navigation

```kotlin
// commonMain - Shared navigation with Voyager or Decompose
class AppNavigator {
    private val _currentScreen = MutableStateFlow<Screen>(Screen.Home)
    val currentScreen: StateFlow<Screen> = _currentScreen.asStateFlow()

    fun navigateTo(screen: Screen) {
        _currentScreen.value = screen
    }
}

@Composable
fun App(navigator: AppNavigator) {
    val currentScreen by navigator.currentScreen.collectAsState()

    MaterialTheme {
        when (currentScreen) {
            is Screen.Home -> HomeScreen(
                onUserClick = { navigator.navigateTo(Screen.UserDetail(it)) }
            )
            is Screen.UserDetail -> UserDetailScreen(
                userId = (currentScreen as Screen.UserDetail).userId,
                onBack = { navigator.navigateTo(Screen.Home) }
            )
        }
    }
}
```

### Platform-Specific Customization

```kotlin
// commonMain - expect for platform customization
expect fun getPlatformName(): String
expect val platformScrollBehavior: ScrollBehavior

@Composable
fun PlatformAwareScreen() {
    val scrollBehavior = platformScrollBehavior

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Running on ${getPlatformName()}") },
                scrollBehavior = scrollBehavior
            )
        }
    ) { padding ->
        // Content
    }
}

// androidMain
actual fun getPlatformName(): String = "Android"
actual val platformScrollBehavior: ScrollBehavior
    @Composable get() = TopAppBarDefaults.enterAlwaysScrollBehavior()

// iosMain
actual fun getPlatformName(): String = "iOS"
actual val platformScrollBehavior: ScrollBehavior
    @Composable get() = TopAppBarDefaults.pinnedScrollBehavior()
```

### Resource Management

```kotlin
// commonMain/composeResources/drawable/logo.png
// commonMain/composeResources/values/strings.xml

@Composable
fun BrandingHeader() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Image(
            painter = painterResource(Res.drawable.logo),
            contentDescription = "Logo"
        )
        Text(
            text = stringResource(Res.string.app_name),
            style = MaterialTheme.typography.headlineLarge
        )
    }
}
```

### ViewModel Integration

```kotlin
// commonMain - Shared ViewModel
class UserListViewModel(
    private val userRepository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(UserListUiState())
    val uiState: StateFlow<UserListUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val users = userRepository.getUsers()
                _uiState.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }
}

@Composable
fun UserListScreen(viewModel: UserListViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    when {
        uiState.isLoading -> LoadingIndicator()
        uiState.error != null -> ErrorMessage(uiState.error!!)
        else -> UserList(users = uiState.users)
    }
}
```

### iOS-Specific Considerations

```kotlin
// iosMain - Entry point for iOS
fun MainViewController(): UIViewController {
    return ComposeUIViewController {
        App()
    }
}

// SwiftUI integration
struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}

// In SwiftUI App
@main
struct iOSApp: App {
    var body: some Scene {
        WindowGroup {
            ComposeView()
                .ignoresSafeArea()
        }
    }
}
```

### When to Use Compose Multiplatform

| Use Case | Recommendation |
|----------|----------------|
| New greenfield project | Strongly consider |
| Need rapid cross-platform development | Yes |
| Complex custom UI components | Yes |
| Platform-native look and feel critical | Evaluate carefully |
| Heavy platform-specific animations | May need native code |
| Existing native iOS team | Gradual adoption |

### Benefits and Trade-offs

**Benefits:**
- Single UI codebase (up to 95% shared)
- Kotlin everywhere (type-safety, coroutines)
- Declarative, reactive UI model
- Rapid iteration across platforms

**Trade-offs:**
- iOS renders via Skia (not native UIKit)
- Some platform behaviors differ
- Larger app size on iOS
- Learning curve for iOS developers

---

## Otvet (RU)

**Compose Multiplatform** - это декларативный UI фреймворк от JetBrains, который расширяет Jetpack Compose за пределы Android на iOS, Desktop (JVM) и Web. По состоянию на 2026 год он стабилен для продакшена на всех основных платформах.

### Основная концепция

Пишите UI один раз на Kotlin, запускайте на нескольких платформах:

```kotlin
// commonMain - Общий UI код
@Composable
fun UserCard(user: User, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Аватар",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )
            Spacer(Modifier.width(16.dp))
            Column {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
```

### Поддержка платформ (2026)

| Платформа | Статус | Примечания |
|-----------|--------|------------|
| **Android** | Стабильно | Нативный Jetpack Compose |
| **iOS** | Стабильно | Использует Skia/Skiko для рендеринга |
| **Desktop** | Стабильно | На основе JVM, использует Skia |
| **Web** | Стабильно | Kotlin/Wasm (Canvas) или Kotlin/JS |

### Настройка проекта

```kotlin
// build.gradle.kts (shared модуль)
plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose")
}

kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()
    jvm("desktop")

    sourceSets {
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)
            implementation(compose.components.uiToolingPreview)
        }

        androidMain.dependencies {
            implementation(compose.preview)
            implementation(libs.androidx.activity.compose)
        }

        val desktopMain by getting {
            dependencies {
                implementation(compose.desktop.currentOs)
            }
        }
    }
}
```

### Общая навигация

```kotlin
// commonMain - Общая навигация с Voyager или Decompose
class AppNavigator {
    private val _currentScreen = MutableStateFlow<Screen>(Screen.Home)
    val currentScreen: StateFlow<Screen> = _currentScreen.asStateFlow()

    fun navigateTo(screen: Screen) {
        _currentScreen.value = screen
    }
}

@Composable
fun App(navigator: AppNavigator) {
    val currentScreen by navigator.currentScreen.collectAsState()

    MaterialTheme {
        when (currentScreen) {
            is Screen.Home -> HomeScreen(
                onUserClick = { navigator.navigateTo(Screen.UserDetail(it)) }
            )
            is Screen.UserDetail -> UserDetailScreen(
                userId = (currentScreen as Screen.UserDetail).userId,
                onBack = { navigator.navigateTo(Screen.Home) }
            )
        }
    }
}
```

### Платформо-специфичная кастомизация

```kotlin
// commonMain - expect для платформенной кастомизации
expect fun getPlatformName(): String
expect val platformScrollBehavior: ScrollBehavior

@Composable
fun PlatformAwareScreen() {
    val scrollBehavior = platformScrollBehavior

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Запущено на ${getPlatformName()}") },
                scrollBehavior = scrollBehavior
            )
        }
    ) { padding ->
        // Контент
    }
}

// androidMain
actual fun getPlatformName(): String = "Android"
actual val platformScrollBehavior: ScrollBehavior
    @Composable get() = TopAppBarDefaults.enterAlwaysScrollBehavior()

// iosMain
actual fun getPlatformName(): String = "iOS"
actual val platformScrollBehavior: ScrollBehavior
    @Composable get() = TopAppBarDefaults.pinnedScrollBehavior()
```

### Управление ресурсами

```kotlin
// commonMain/composeResources/drawable/logo.png
// commonMain/composeResources/values/strings.xml

@Composable
fun BrandingHeader() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Image(
            painter = painterResource(Res.drawable.logo),
            contentDescription = "Логотип"
        )
        Text(
            text = stringResource(Res.string.app_name),
            style = MaterialTheme.typography.headlineLarge
        )
    }
}
```

### Интеграция с ViewModel

```kotlin
// commonMain - Общая ViewModel
class UserListViewModel(
    private val userRepository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(UserListUiState())
    val uiState: StateFlow<UserListUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val users = userRepository.getUsers()
                _uiState.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }
}

@Composable
fun UserListScreen(viewModel: UserListViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    when {
        uiState.isLoading -> LoadingIndicator()
        uiState.error != null -> ErrorMessage(uiState.error!!)
        else -> UserList(users = uiState.users)
    }
}
```

### iOS-специфичные соображения

```kotlin
// iosMain - Точка входа для iOS
fun MainViewController(): UIViewController {
    return ComposeUIViewController {
        App()
    }
}

// Интеграция со SwiftUI
struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}

// В SwiftUI App
@main
struct iOSApp: App {
    var body: some Scene {
        WindowGroup {
            ComposeView()
                .ignoresSafeArea()
        }
    }
}
```

### Когда использовать Compose Multiplatform

| Случай использования | Рекомендация |
|---------------------|--------------|
| Новый проект с нуля | Настоятельно рассмотреть |
| Нужна быстрая кросс-платформенная разработка | Да |
| Сложные кастомные UI компоненты | Да |
| Критичен нативный внешний вид платформы | Тщательно оценить |
| Тяжёлые платформо-специфичные анимации | Может потребоваться нативный код |
| Существующая нативная iOS команда | Постепенное внедрение |

### Преимущества и компромиссы

**Преимущества:**
- Единая UI кодовая база (до 95% общего кода)
- Kotlin везде (типобезопасность, корутины)
- Декларативная, реактивная UI модель
- Быстрая итерация на всех платформах

**Компромиссы:**
- iOS рендерится через Skia (не нативный UIKit)
- Некоторые платформенные поведения отличаются
- Больший размер приложения на iOS
- Кривая обучения для iOS разработчиков

---

## Follow-ups

- How does Compose Multiplatform handle iOS-specific gestures?
- What navigation libraries work with Compose Multiplatform?
- How do you handle platform-specific theming?
- What is the performance comparison with native SwiftUI?

## Dopolnitelnye Voprosy (RU)

- Как Compose Multiplatform обрабатывает iOS-специфичные жесты?
- Какие библиотеки навигации работают с Compose Multiplatform?
- Как обрабатывать платформо-специфичные темы?
- Как производительность сравнивается с нативным SwiftUI?

## References

- [Compose Multiplatform Documentation](https://www.jetbrains.com/lp/compose-multiplatform/)
- [Compose Multiplatform GitHub](https://github.com/JetBrains/compose-multiplatform)

## Ssylki (RU)

- [[c-kotlin]]
- [Документация Compose Multiplatform](https://www.jetbrains.com/lp/compose-multiplatform/)

## Related Questions

- [[q-kmp-shared-code-strategy--kmp--hard]]
- [[q-kmp-architecture--kmp--hard]]
