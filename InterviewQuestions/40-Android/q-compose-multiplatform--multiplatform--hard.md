---
tags:
  - Android
  - Kotlin
  - Compose
  - Multiplatform
  - UI
difficulty: hard
status: draft
---

# Compose Multiplatform for Shared UI

# Question (EN)
> 
Explain Compose Multiplatform and how it differs from KMM. How do you create shared UI components across Android, iOS, Desktop, and Web? What are the limitations and best practices for cross-platform Compose development?

## Answer (EN)
Compose Multiplatform extends Kotlin Multiplatform to share UI code across Android, iOS, Desktop, and Web using Jetpack Compose's declarative UI paradigm, enabling unprecedented code reuse while maintaining platform-specific customizations.

#### Compose Multiplatform Setup

**1. Project Configuration**
```kotlin
// settings.gradle.kts
pluginManagement {
    repositories {
        google()
        gradlePluginPortal()
        mavenCentral()
        maven("https://maven.pkg.jetbrains.space/public/p/compose/dev")
    }
}

// build.gradle.kts (project level)
plugins {
    kotlin("multiplatform") version "1.9.21" apply false
    id("org.jetbrains.compose") version "1.5.11" apply false
}

// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose")
    id("com.android.library")
}

kotlin {
    androidTarget()

    jvm("desktop")

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "ComposeApp"
            isStatic = true
        }
    }

    js(IR) {
        browser()
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation(compose.runtime)
                implementation(compose.foundation)
                implementation(compose.material3)
                implementation(compose.ui)
                implementation(compose.components.resources)
                implementation(compose.components.uiToolingPreview)

                // Navigation
                implementation("org.jetbrains.androidx.navigation:navigation-compose:2.7.0-alpha01")

                // ViewModel
                implementation("org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0-alpha01")

                // Image loading
                implementation("io.kamel:kamel-image:0.9.0")

                // Coroutines
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("androidx.activity:activity-compose:1.8.2")
                implementation("androidx.compose.ui:ui-tooling-preview:1.5.4")
            }
        }

        val iosMain by creating {
            dependsOn(commonMain)
            dependencies {
                // iOS-specific dependencies
            }
        }

        val desktopMain by getting {
            dependencies {
                implementation(compose.desktop.currentOs)
            }
        }

        val jsMain by getting {
            dependencies {
                implementation(compose.html.core)
            }
        }
    }
}

android {
    namespace = "com.example.composeapp"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

compose.experimental {
    web.application {}
}
```

**2. Directory Structure**
```
project/
 composeApp/
    src/
       commonMain/
          kotlin/
             com/example/
                 App.kt
                 ui/
                    screens/
                    components/
                    theme/
                 navigation/
          resources/
              drawable/
              font/
              values/
       androidMain/
       iosMain/
       desktopMain/
       jsMain/
    build.gradle.kts
 androidApp/
    src/main/kotlin/MainActivity.kt
 iosApp/
    iosApp/ContentView.swift
 desktopApp/
     src/jvmMain/kotlin/main.kt
```

#### Shared UI Components

**1. Common Composables**
```kotlin
// commonMain/ui/components/TaskCard.kt
@Composable
fun TaskCard(
    task: Task,
    onToggleComplete: () -> Unit,
    onDelete: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (task.completed) {
                MaterialTheme.colorScheme.surfaceVariant
            } else {
                MaterialTheme.colorScheme.surface
            }
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(
                checked = task.completed,
                onCheckedChange = { onToggleComplete() }
            )

            Spacer(modifier = Modifier.width(12.dp))

            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = task.title,
                    style = MaterialTheme.typography.titleMedium,
                    textDecoration = if (task.completed) {
                        TextDecoration.LineThrough
                    } else {
                        null
                    }
                )

                if (task.description.isNotBlank()) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = task.description,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = formatDate(task.createdAt),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Spacer(modifier = Modifier.width(8.dp))

            IconButton(onClick = onDelete) {
                Icon(
                    imageVector = Icons.Default.Delete,
                    contentDescription = "Delete task",
                    tint = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
expect fun formatDate(timestamp: Long): String
```

**2. Shared Screens**
```kotlin
// commonMain/ui/screens/TaskListScreen.kt
@Composable
fun TaskListScreen(
    viewModel: TaskListViewModel = getViewModel()
) {
    val tasks by viewModel.tasks.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()

    var showCreateDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("My Tasks") },
                actions = {
                    IconButton(onClick = { viewModel.loadTasks(forceRefresh = true) }) {
                        Icon(Icons.Default.Refresh, "Refresh")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showCreateDialog = true }
            ) {
                Icon(Icons.Default.Add, "Add task")
            }
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when {
                isLoading && tasks.isEmpty() -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }

                error != null && tasks.isEmpty() -> {
                    ErrorView(
                        message = error!!,
                        onRetry = { viewModel.loadTasks(forceRefresh = true) },
                        modifier = Modifier.align(Alignment.Center)
                    )
                }

                tasks.isEmpty() -> {
                    EmptyStateView(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }

                else -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize()
                    ) {
                        items(
                            items = tasks,
                            key = { it.id }
                        ) { task ->
                            TaskCard(
                                task = task,
                                onToggleComplete = {
                                    viewModel.toggleTaskCompletion(task.id)
                                },
                                onDelete = {
                                    viewModel.deleteTask(task.id)
                                },
                                modifier = Modifier.animateItemPlacement()
                            )
                        }
                    }
                }
            }

            // Pull to refresh indicator
            if (isLoading && tasks.isNotEmpty()) {
                LinearProgressIndicator(
                    modifier = Modifier
                        .fillMaxWidth()
                        .align(Alignment.TopCenter)
                )
            }
        }
    }

    // Create task dialog
    if (showCreateDialog) {
        CreateTaskDialog(
            onDismiss = { showCreateDialog = false },
            onCreate = { title, description ->
                viewModel.createTask(title, description)
                showCreateDialog = false
            }
        )
    }
}

@Composable
fun EmptyStateView(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = Icons.Default.CheckCircle,
            contentDescription = null,
            modifier = Modifier.size(120.dp),
            tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.3f)
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "No tasks yet",
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "Tap + to create your first task",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun ErrorView(
    message: String,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = Icons.Default.Warning,
            contentDescription = null,
            modifier = Modifier.size(120.dp),
            tint = MaterialTheme.colorScheme.error
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Something went wrong",
            style = MaterialTheme.typography.headlineSmall
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(onClick = onRetry) {
            Text("Retry")
        }
    }
}
```

**3. Create Task Dialog**
```kotlin
// commonMain/ui/components/CreateTaskDialog.kt
@Composable
fun CreateTaskDialog(
    onDismiss: () -> Unit,
    onCreate: (title: String, description: String) -> Unit
) {
    var title by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var titleError by remember { mutableStateOf<String?>(null) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text("Create Task")
        },
        text = {
            Column {
                OutlinedTextField(
                    value = title,
                    onValueChange = {
                        title = it
                        titleError = null
                    },
                    label = { Text("Title") },
                    isError = titleError != null,
                    supportingText = titleError?.let { { Text(it) } },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(16.dp))

                OutlinedTextField(
                    value = description,
                    onValueChange = { description = it },
                    label = { Text("Description (optional)") },
                    minLines = 3,
                    maxLines = 5,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    when {
                        title.isBlank() -> {
                            titleError = "Title is required"
                        }
                        else -> {
                            onCreate(title.trim(), description.trim())
                        }
                    }
                }
            ) {
                Text("Create")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
```

#### Platform-Specific Adaptations

**1. Platform Detection**
```kotlin
// commonMain/Platform.kt
enum class Platform {
    ANDROID, IOS, DESKTOP, WEB
}

expect fun getPlatform(): Platform

expect fun isDebug(): Boolean

// androidMain
actual fun getPlatform(): Platform = Platform.ANDROID
actual fun isDebug(): Boolean = BuildConfig.DEBUG

// iosMain
actual fun getPlatform(): Platform = Platform.IOS
actual fun isDebug(): Boolean = Platform.isDebugBinary

// desktopMain
actual fun getPlatform(): Platform = Platform.DESKTOP
actual fun isDebug(): Boolean = true // or check system property

// jsMain
actual fun getPlatform(): Platform = Platform.WEB
actual fun isDebug(): Boolean = js("process.env.NODE_ENV === 'development'") as Boolean
```

**2. Platform-Specific UI Adaptations**
```kotlin
// commonMain/ui/components/PlatformAdaptiveButton.kt
@Composable
fun PlatformAdaptiveButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    when (getPlatform()) {
        Platform.IOS -> {
            // iOS-style button
            Surface(
                modifier = modifier
                    .fillMaxWidth()
                    .height(50.dp)
                    .clickable(enabled = enabled, onClick = onClick),
                color = if (enabled) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.surfaceVariant
                },
                shape = RoundedCornerShape(10.dp)
            ) {
                Box(
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = text,
                        color = Color.White,
                        style = MaterialTheme.typography.labelLarge
                    )
                }
            }
        }

        Platform.DESKTOP -> {
            // Desktop-style button with hover effect
            var isHovered by remember { mutableStateOf(false) }

            Button(
                onClick = onClick,
                modifier = modifier
                    .onPointerEvent(PointerEventType.Enter) { isHovered = true }
                    .onPointerEvent(PointerEventType.Exit) { isHovered = false },
                enabled = enabled,
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isHovered) {
                        MaterialTheme.colorScheme.primary.copy(alpha = 0.9f)
                    } else {
                        MaterialTheme.colorScheme.primary
                    }
                )
            ) {
                Text(text)
            }
        }

        else -> {
            // Default Material button
            Button(
                onClick = onClick,
                modifier = modifier,
                enabled = enabled
            ) {
                Text(text)
            }
        }
    }
}

// Platform-specific spacing
@Composable
fun getPlatformPadding(): PaddingValues {
    return when (getPlatform()) {
        Platform.IOS -> PaddingValues(16.dp)
        Platform.DESKTOP -> PaddingValues(24.dp)
        Platform.WEB -> PaddingValues(20.dp)
        Platform.ANDROID -> PaddingValues(16.dp)
    }
}

// Platform-specific navigation
@Composable
fun PlatformBackButton(onClick: () -> Unit) {
    when (getPlatform()) {
        Platform.IOS -> {
            IconButton(onClick = onClick) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back",
                    modifier = Modifier.size(24.dp)
                )
            }
        }

        Platform.DESKTOP -> {
            // Desktop typically uses window controls
            // No back button needed
        }

        else -> {
            IconButton(onClick = onClick) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back"
                )
            }
        }
    }
}
```

**3. Responsive Layouts**
```kotlin
// commonMain/ui/utils/WindowSize.kt
enum class WindowSize {
    COMPACT,  // Phone portrait
    MEDIUM,   // Phone landscape, tablet portrait
    EXPANDED  // Tablet landscape, desktop
}

@Composable
expect fun rememberWindowSize(): WindowSize

// commonMain/ui/screens/AdaptiveLayout.kt
@Composable
fun AdaptiveTaskListScreen(
    viewModel: TaskListViewModel = getViewModel()
) {
    val windowSize = rememberWindowSize()
    val tasks by viewModel.tasks.collectAsState()

    when (windowSize) {
        WindowSize.COMPACT -> {
            // Single column layout for phones
            CompactTaskList(tasks = tasks, viewModel = viewModel)
        }

        WindowSize.MEDIUM -> {
            // Two column layout
            Row(modifier = Modifier.fillMaxSize()) {
                TaskList(
                    tasks = tasks,
                    viewModel = viewModel,
                    modifier = Modifier.weight(1f)
                )

                VerticalDivider()

                TaskDetailsPane(
                    modifier = Modifier.weight(1f)
                )
            }
        }

        WindowSize.EXPANDED -> {
            // Three column layout with navigation rail
            Row(modifier = Modifier.fillMaxSize()) {
                NavigationRail {
                    // Navigation items
                }

                TaskList(
                    tasks = tasks,
                    viewModel = viewModel,
                    modifier = Modifier.weight(0.4f)
                )

                VerticalDivider()

                TaskDetailsPane(
                    modifier = Modifier.weight(0.6f)
                )
            }
        }
    }
}

// androidMain
@Composable
actual fun rememberWindowSize(): WindowSize {
    val configuration = LocalConfiguration.current
    return when {
        configuration.screenWidthDp < 600 -> WindowSize.COMPACT
        configuration.screenWidthDp < 840 -> WindowSize.MEDIUM
        else -> WindowSize.EXPANDED
    }
}

// desktopMain
@Composable
actual fun rememberWindowSize(): WindowSize {
    val windowState = LocalWindowInfo.current
    return when {
        windowState.containerSize.width < 600.dp.value -> WindowSize.COMPACT
        windowState.containerSize.width < 840.dp.value -> WindowSize.MEDIUM
        else -> WindowSize.EXPANDED
    }
}
```

#### Theme and Styling

**1. Shared Material Theme**
```kotlin
// commonMain/ui/theme/Theme.kt
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        darkTheme -> darkColorScheme(
            primary = Color(0xFF6200EA),
            onPrimary = Color.White,
            primaryContainer = Color(0xFF3700B3),
            secondary = Color(0xFF03DAC6),
            onSecondary = Color.Black,
            background = Color(0xFF121212),
            surface = Color(0xFF1E1E1E),
            error = Color(0xFFCF6679)
        )

        else -> lightColorScheme(
            primary = Color(0xFF6200EA),
            onPrimary = Color.White,
            primaryContainer = Color(0xFFBB86FC),
            secondary = Color(0xFF03DAC6),
            onSecondary = Color.Black,
            background = Color.White,
            surface = Color(0xFFF5F5F5),
            error = Color(0xFFB00020)
        )
    }

    val typography = Typography(
        displayLarge = TextStyle(
            fontFamily = getFontFamily(),
            fontWeight = FontWeight.Bold,
            fontSize = 57.sp,
            lineHeight = 64.sp
        ),
        headlineMedium = TextStyle(
            fontFamily = getFontFamily(),
            fontWeight = FontWeight.SemiBold,
            fontSize = 28.sp,
            lineHeight = 36.sp
        ),
        titleLarge = TextStyle(
            fontFamily = getFontFamily(),
            fontWeight = FontWeight.SemiBold,
            fontSize = 22.sp,
            lineHeight = 28.sp
        ),
        bodyLarge = TextStyle(
            fontFamily = getFontFamily(),
            fontWeight = FontWeight.Normal,
            fontSize = 16.sp,
            lineHeight = 24.sp
        ),
        labelMedium = TextStyle(
            fontFamily = getFontFamily(),
            fontWeight = FontWeight.Medium,
            fontSize = 12.sp,
            lineHeight = 16.sp
        )
    )

    MaterialTheme(
        colorScheme = colorScheme,
        typography = typography,
        content = content
    )
}

@Composable
expect fun getFontFamily(): FontFamily

@Composable
expect fun isSystemInDarkTheme(): Boolean
```

**2. Resource Management**
```kotlin
// commonMain/ui/theme/Resources.kt
@Composable
fun painterResource(id: String): Painter {
    return when (getPlatform()) {
        Platform.ANDROID -> {
            // Android resources
            painterResource(getDrawableId(id))
        }

        Platform.IOS, Platform.DESKTOP -> {
            // Load from common resources
            painterResource("drawable/$id.png")
        }

        Platform.WEB -> {
            // Load from web resources
            painterResource("/assets/$id.png")
        }
    }
}

@Composable
expect fun getDrawableId(name: String): Int

// String resources
object Strings {
    const val app_name = "Task Manager"
    const val task_list_title = "My Tasks"
    const val create_task = "Create Task"
    const val task_title = "Title"
    const val task_description = "Description"
    const val delete_task = "Delete"
    const val mark_complete = "Mark as complete"
}

// Localization support
@Composable
expect fun stringResource(key: String): String
```

#### Navigation

**1. Shared Navigation Graph**
```kotlin
// commonMain/navigation/Navigation.kt
sealed class Screen(val route: String) {
    object TaskList : Screen("task_list")
    object TaskDetail : Screen("task_detail/{taskId}") {
        fun createRoute(taskId: String) = "task_detail/$taskId"
    }
    object Settings : Screen("settings")
    object About : Screen("about")
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Screen.TaskList.route
    ) {
        composable(Screen.TaskList.route) {
            TaskListScreen(
                onTaskClick = { taskId ->
                    navController.navigate(Screen.TaskDetail.createRoute(taskId))
                },
                onSettingsClick = {
                    navController.navigate(Screen.Settings.route)
                }
            )
        }

        composable(
            route = Screen.TaskDetail.route,
            arguments = listOf(
                navArgument("taskId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val taskId = backStackEntry.arguments?.getString("taskId")
            taskId?.let {
                TaskDetailScreen(
                    taskId = it,
                    onBack = { navController.popBackStack() }
                )
            }
        }

        composable(Screen.Settings.route) {
            SettingsScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.About.route) {
            AboutScreen(
                onBack = { navController.popBackStack() }
            )
        }
    }
}
```

#### Platform Entry Points

**1. Android**
```kotlin
// androidApp/MainActivity.kt
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            AppTheme {
                App()
            }
        }
    }
}

// commonMain/App.kt
@Composable
fun App() {
    AppNavigation()
}
```

**2. iOS**
```swift
// iosApp/ComposeView.swift
import SwiftUI
import ComposeApp

struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}

struct ContentView: View {
    var body: some View {
        ComposeView()
            .ignoresSafeArea(.all)
    }
}

// iosMain/MainViewController.kt
import androidx.compose.ui.window.ComposeUIViewController

fun MainViewController() = ComposeUIViewController {
    AppTheme {
        App()
    }
}
```

**3. Desktop**
```kotlin
// desktopApp/main.kt
fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "Task Manager",
        state = rememberWindowState(
            width = 1200.dp,
            height = 800.dp,
            position = WindowPosition(Alignment.Center)
        )
    ) {
        AppTheme {
            App()
        }
    }
}
```

**4. Web**
```kotlin
// jsMain/main.kt
fun main() {
    CanvasBasedWindow(canvasElementId = "ComposeTarget") {
        AppTheme {
            App()
        }
    }
}

// HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Task Manager</title>
</head>
<body>
    <canvas id="ComposeTarget"></canvas>
    <script src="composeApp.js"></script>
</body>
</html>
```

#### Best Practices

1. **Code Sharing Strategy**:
   - Share UI components, screens, navigation
   - Keep platform-specific code minimal
   - Use expect/actual for platform differences
   - Design responsive layouts from start

2. **Performance**:
   - Use LazyColumn/LazyRow for lists
   - Avoid unnecessary recompositions
   - Use remember for expensive calculations
   - Profile on all target platforms

3. **Platform Adaptation**:
   - Respect platform conventions
   - Use platform-appropriate spacing
   - Adapt navigation patterns
   - Handle platform-specific gestures

4. **Resources**:
   - Use Compose Resources for images
   - Centralize string constants
   - Support dark/light themes
   - Plan for localization

5. **Testing**:
   - Write UI tests in commonTest
   - Test on all target platforms
   - Use screenshot testing
   - Verify responsive layouts

#### Limitations

1. **iOS Limitations**:
   - No direct SwiftUI interop (yet)
   - UIViewController wrapper required
   - Some animations may differ
   - Platform feel requires customization

2. **Web Limitations**:
   - Canvas-based (not DOM)
   - Larger bundle size
   - Limited SEO
   - Accessibility challenges

3. **Desktop Limitations**:
   - Window management differences
   - Different input methods (mouse vs touch)
   - Platform-specific shortcuts

4. **General**:
   - Learning curve for all platforms
   - Build times can be long
   - Debugging across platforms
   - Third-party library support

#### Common Pitfalls

1. **Over-sharing**: Forcing same UI on all platforms
2. **Ignoring Platform Conventions**: Android UI on iOS
3. **Performance**: Not optimizing for each platform
4. **Resources**: Platform-specific resource handling
5. **Navigation**: Different patterns per platform
6. **Gestures**: Touch vs mouse vs keyboard

### Summary

Compose Multiplatform enables UI code sharing across platforms:
- **Targets**: Android, iOS, Desktop, Web
- **Shared Code**: UI components, screens, navigation, themes
- **Platform-Specific**: Entry points, resources, platform conventions
- **Responsive**: Adaptive layouts for different screen sizes
- **Limitations**: Platform-specific behaviors, performance considerations

Key considerations: appropriate abstraction levels, platform conventions, responsive design, performance optimization, and comprehensive testing across all targets.

---

# Вопрос (RU)
> 
Объясните Compose Multiplatform и чем он отличается от KMM. Как создавать shared UI компоненты для Android, iOS, Desktop и Web? Каковы ограничения и best practices для кросс-платформенной Compose разработки?

## Ответ (RU)
Compose Multiplatform расширяет Kotlin Multiplatform для sharing UI кода между Android, iOS, Desktop и Web, используя декларативную UI парадигму Jetpack Compose, обеспечивая беспрецедентное переиспользование кода с сохранением platform-specific кастомизаций.

#### Отличия от KMM

**KMM**:
- Только бизнес-логика, данные, сеть
- UI остается platform-specific
- Android: Compose, iOS: SwiftUI

**Compose Multiplatform**:
- Shared UI + бизнес-логика
- Один UI фреймворк для всех платформ
- Compose везде (Android, iOS, Desktop, Web)

#### Shared UI

**Что можно делить**:
-  UI компоненты
-  Screens
-  Navigation
-  Themes
-  Layouts

**Platform-specific**:
- Entry points (Activity, UIViewController, Window)
- Platform conventions
- Specific gestures
- Resources handling

#### Responsive Design

**WindowSize**:
- COMPACT: телефон portrait
- MEDIUM: телефон landscape, планшет portrait
- EXPANDED: планшет landscape, desktop

**Adaptive layouts**:
- Single column для COMPACT
- Two column для MEDIUM
- Three column + NavigationRail для EXPANDED

#### Платформы

**Android**:
- Activity с setContent
- Standard Compose
- Material 3

**iOS**:
- UIViewController wrapper
- ComposeUIViewController
- Platform adaptations

**Desktop**:
- Window application
- Mouse hover effects
- Keyboard shortcuts

**Web**:
- Canvas-based rendering
- Browser compatibility
- Bundle size considerations

#### Best Practices

1. **Code Sharing**:
   - Максимизировать shared UI
   - Minimize platform-specific код
   - Responsive from start
   - Platform conventions

2. **Performance**:
   - LazyColumn/LazyRow
   - Избегать recompositions
   - remember для дорогих вычислений
   - Profile на всех платформах

3. **Platform Adaptation**:
   - Уважать platform conventions
   - Platform-specific spacing
   - Adaptive navigation
   - Platform gestures

4. **Resources**:
   - Compose Resources
   - Centralized strings
   - Dark/light themes
   - Localization ready

#### Ограничения

**iOS**:
- No direct SwiftUI interop
- UIViewController wrapper
- Анимации могут отличаться

**Web**:
- Canvas-based (не DOM)
- Большой bundle size
- Limited SEO
- Accessibility сложности

**Desktop**:
- Window management
- Input methods (mouse vs touch)
- Platform shortcuts

### Резюме

Compose Multiplatform обеспечивает UI code sharing:
- **Targets**: Android, iOS, Desktop, Web
- **Shared**: UI components, screens, navigation, themes
- **Platform-Specific**: Entry points, resources, conventions
- **Responsive**: Adaptive layouts
- **Limitations**: Platform behaviors, performance

Ключевые моменты: правильная абстракция, platform conventions, responsive design, оптимизация производительности, тестирование на всех платформах.

---

## Related Questions

### Prerequisites (Easier)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Compose
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose
- [[q-compose-performance-optimization--android--hard]] - Compose
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Compose
