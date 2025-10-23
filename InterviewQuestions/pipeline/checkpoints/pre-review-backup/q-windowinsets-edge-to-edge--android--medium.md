---
id: 20251012-400004
title: "WindowInsets & Edge-to-Edge"
topic: android
difficulty: medium
status: draft
created: 2025-10-12
tags: [windowinsets, edge-to-edge, system-ui, immersive, android/system-ui, android/windowinsets, android/edge-to-edge, android/immersive, difficulty/medium]
moc: moc-android
related: [q-sharedpreferences-definition--android--easy, q-diffutil-background-calculation-issues--android--medium, q-build-optimization-gradle--gradle--medium]
  - q-jetpack-compose-basics--android--medium
  - q-material3-components--material-design--easy
  - q-adaptive-layouts--android--hard
subtopics:
  - ui
  - system-ui
  - windowinsets
  - edge-to-edge
  - immersive
---
# WindowInsets & Edge-to-Edge

## English Version

### Problem Statement

Edge-to-edge design allows apps to draw behind system bars (status bar, navigation bar), creating immersive experiences. WindowInsets API helps handle system UI visibility and safe content areas. Understanding this is essential for modern Android UI.

**The Question:** What are WindowInsets? How do you implement edge-to-edge design? How do you handle system bars, cutouts, and keyboard insets in Compose?

### Detailed Answer

---

### EDGE-TO-EDGE BASICS

**Enable edge-to-edge in Activity:**

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Enable edge-to-edge
        enableEdgeToEdge()

        setContent {
            MyAppTheme {
                MainScreen()
            }
        }
    }
}

// Or manually:
fun Activity.enableEdgeToEdge() {
    WindowCompat.setDecorFitsSystemWindows(window, false)
}
```

**What edge-to-edge does:**
```
Before edge-to-edge:

   Status Bar     ← System managed

                 
   App Content    ← Your content here
                 

  Navigation Bar  ← System managed


After edge-to-edge:

   Status Bar     ← Transparent, you draw behind
                 
   App Content    ← Your content fills entire screen
                 
  Navigation Bar  ← Transparent, you draw behind

```

---

### WINDOWINSETS IN COMPOSE

**Accessing WindowInsets:**

```kotlin
@Composable
fun WindowInsetsExample() {
    val insets = WindowInsets.systemBars
    val statusBarHeight = insets.asPaddingValues().calculateTopPadding()
    val navigationBarHeight = insets.asPaddingValues().calculateBottomPadding()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
    ) {
        // Status bar spacer
        Spacer(
            modifier = Modifier
                .fillMaxWidth()
                .height(statusBarHeight)
                .background(Color.Blue.copy(alpha = 0.3f))
        )

        Text(
            text = "Content below status bar",
            modifier = Modifier.padding(16.dp)
        )

        Spacer(modifier = Modifier.weight(1f))

        // Navigation bar spacer
        Spacer(
            modifier = Modifier
                .fillMaxWidth()
                .height(navigationBarHeight)
                .background(Color.Green.copy(alpha = 0.3f))
        )
    }
}
```

---

### SYSTEM BAR INSETS

```kotlin
@Composable
fun SystemBarsExample() {
    Scaffold(
        // Apply system bar padding to content
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.systemBars)
    ) { paddingValues ->
        // Content automatically avoids system bars
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            Text("This content avoids system bars")
        }
    }
}

// Or apply specific insets:
@Composable
fun SpecificInsetsExample() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            // Only apply status bar padding
            .windowInsetsPadding(WindowInsets.statusBars)
    ) {
        TopAppBar()

        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
        ) {
            Content()
        }

        BottomBar(
            modifier = Modifier
                // Only apply navigation bar padding
                .windowInsetsPadding(WindowInsets.navigationBars)
        )
    }
}
```

---

### AVAILABLE WINDOWINSETS TYPES

```kotlin
@Composable
fun AllWindowInsetsTypes() {
    // System bars (status + navigation)
    val systemBars = WindowInsets.systemBars

    // Status bar only
    val statusBars = WindowInsets.statusBars

    // Navigation bar only
    val navigationBars = WindowInsets.navigationBars

    // Caption bar (desktop mode)
    val captionBar = WindowInsets.captionBar

    // Display cutout (notch, camera hole)
    val displayCutout = WindowInsets.displayCutout

    // IME (keyboard)
    val ime = WindowInsets.ime

    // Waterfall insets (curved edges)
    val waterfall = WindowInsets.waterfall

    // System gestures
    val systemGestures = WindowInsets.systemGestures

    // Mandatory system gestures
    val mandatorySystemGestures = WindowInsets.mandatorySystemGestures

    // Tappable element
    val tappableElement = WindowInsets.tappableElement

    // Safe drawing area
    val safeDrawing = WindowInsets.safeDrawing

    // Safe gestures
    val safeGestures = WindowInsets.safeGestures

    // Safe content
    val safeContent = WindowInsets.safeContent
}
```

---

### IME (KEYBOARD) INSETS

```kotlin
@Composable
fun KeyboardHandlingExample() {
    val imeVisible = WindowInsets.ime.asPaddingValues().calculateBottomPadding() > 0.dp

    var text by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding()  //  Automatically handle keyboard
    ) {
        // Content that scrolls above keyboard
        LazyColumn(
            modifier = Modifier.weight(1f)
        ) {
            items(50) { index ->
                Text(
                    text = "Item $index",
                    modifier = Modifier.padding(16.dp)
                )
            }
        }

        // Input field that stays above keyboard
        TextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        )

        if (imeVisible) {
            Text(
                text = "Keyboard is visible",
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
```

---

### DISPLAY CUTOUT (NOTCH) HANDLING

```kotlin
@Composable
fun DisplayCutoutExample() {
    val displayCutout = WindowInsets.displayCutout
    val topInset = displayCutout.asPaddingValues().calculateTopPadding()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)  // Background behind cutout
    ) {
        // Content that avoids cutout
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(topInset)
                .background(Color.Red.copy(alpha = 0.3f))
        ) {
            Text(
                text = "Cutout area",
                color = Color.White,
                modifier = Modifier.align(Alignment.Center)
            )
        }

        // Main content
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.White)
        ) {
            Text("Main content", modifier = Modifier.padding(16.dp))
        }
    }
}

// Or let content draw behind cutout but pad specific items:
@Composable
fun ContentBehindCutout() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(Color.Blue, Color.Cyan)
                )
            )
    ) {
        // AppBar that avoids cutout
        TopAppBar(
            title = { Text("Title") },
            modifier = Modifier
                .fillMaxWidth()
                .windowInsetsPadding(WindowInsets.displayCutout)
                .windowInsetsPadding(WindowInsets.statusBars)
        )
    }
}
```

---

### COMBINING MULTIPLE INSETS

```kotlin
@Composable
fun CombinedInsetsExample() {
    // Union of multiple insets
    val combinedInsets = WindowInsets.systemBars
        .union(WindowInsets.displayCutout)
        .union(WindowInsets.ime)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(combinedInsets)
    ) {
        Text("Content avoids all system UI")
    }
}

// Or use safeDrawing (includes all safe areas)
@Composable
fun SafeDrawingExample() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.safeDrawing)
    ) {
        Text("Content in safe drawing area")
    }
}
```

---

### CONSUMING INSETS

```kotlin
@Composable
fun ConsumeInsetsExample() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.LightGray)
    ) {
        // AppBar consumes status bar insets
        TopAppBar(
            title = { Text("Title") },
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.Blue)
                // Consume status bar insets
                .windowInsetsPadding(WindowInsets.statusBars)
        )

        // Content below doesn't need status bar padding
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                // Only apply navigation bar padding
                .windowInsetsPadding(WindowInsets.navigationBars)
        ) {
            items(50) { index ->
                Text(
                    text = "Item $index",
                    modifier = Modifier.padding(16.dp)
                )
            }
        }
    }
}
```

---

### SYSTEM BAR COLORS

```kotlin
@Composable
fun SystemBarColorsExample() {
    val view = LocalView.current
    val darkTheme = isSystemInDarkTheme()

    // Set system bar colors
    DisposableEffect(darkTheme) {
        val window = (view.context as Activity).window

        // Status bar color
        window.statusBarColor = Color.Transparent.toArgb()

        // Navigation bar color
        window.navigationBarColor = Color.Transparent.toArgb()

        // System bar appearance (light or dark icons)
        WindowCompat.getInsetsController(window, view).apply {
            isAppearanceLightStatusBars = !darkTheme
            isAppearanceLightNavigationBars = !darkTheme
        }

        onDispose { }
    }

    Content()
}
```

---

### SCAFFOLD WITH EDGE-TO-EDGE

```kotlin
@Composable
fun EdgeToEdgeScaffold() {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Edge-to-Edge") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Transparent
                ),
                modifier = Modifier
                    // Draw behind status bar
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(
                                Color.Blue.copy(alpha = 0.9f),
                                Color.Blue.copy(alpha = 0.7f)
                            )
                        )
                    )
                    .windowInsetsPadding(WindowInsets.statusBars)
            )
        },
        bottomBar = {
            NavigationBar(
                containerColor = Color.Transparent,
                modifier = Modifier
                    // Draw behind navigation bar
                    .background(
                        Color.White.copy(alpha = 0.95f)
                    )
                    .windowInsetsPadding(WindowInsets.navigationBars)
            ) {
                // Navigation items
            }
        },
        // Don't apply contentWindowInsets - we handle manually
        contentWindowInsets = WindowInsets(0)
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            items(50) { index ->
                ListItem(
                    headlineContent = { Text("Item $index") }
                )
            }
        }
    }
}
```

---

### IMMERSIVE MODE

```kotlin
@Composable
fun ImmersiveContent() {
    val view = LocalView.current
    var isImmersive by remember { mutableStateOf(false) }

    DisposableEffect(isImmersive) {
        val window = (view.context as Activity).window
        val insetsController = WindowCompat.getInsetsController(window, view)

        if (isImmersive) {
            // Hide system bars
            insetsController.hide(WindowInsetsCompat.Type.systemBars())
            insetsController.systemBarsBehavior =
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        } else {
            // Show system bars
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }

        onDispose {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .clickable { isImmersive = !isImmersive }
    ) {
        Text(
            text = if (isImmersive) "Immersive Mode (tap to exit)" else "Tap for immersive",
            color = Color.White,
            modifier = Modifier.align(Alignment.Center)
        )
    }
}
```

---

### REAL-WORLD EXAMPLES

#### Video Player

```kotlin
@Composable
fun VideoPlayerScreen() {
    var isFullscreen by remember { mutableStateOf(false) }
    val view = LocalView.current

    DisposableEffect(isFullscreen) {
        val window = (view.context as Activity).window
        val insetsController = WindowCompat.getInsetsController(window, view)

        if (isFullscreen) {
            // Hide system bars for fullscreen video
            insetsController.hide(WindowInsetsCompat.Type.systemBars())
            insetsController.systemBarsBehavior =
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        } else {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }

        onDispose {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        if (isFullscreen) {
            // Full screen video player
            VideoPlayer(
                modifier = Modifier.fillMaxSize()
            )
        } else {
            // Normal layout
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .windowInsetsPadding(WindowInsets.systemBars)
            ) {
                VideoPlayer(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(16f / 9f)
                )

                VideoDetails()
            }
        }

        // Fullscreen toggle
        IconButton(
            onClick = { isFullscreen = !isFullscreen },
            modifier = Modifier
                .align(if (isFullscreen) Alignment.TopEnd else Alignment.BottomEnd)
                .padding(16.dp)
        ) {
            Icon(
                imageVector = if (isFullscreen) {
                    Icons.Default.FullscreenExit
                } else {
                    Icons.Default.Fullscreen
                },
                contentDescription = "Toggle fullscreen",
                tint = Color.White
            )
        }
    }
}

@Composable
fun VideoPlayer(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier.background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        Text("Video Player", color = Color.White)
    }
}

@Composable
fun VideoDetails() {
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        item {
            Text(
                text = "Video Title",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(16.dp)
            )
        }
        item {
            Text(
                text = "Video description...",
                modifier = Modifier.padding(horizontal = 16.dp)
            )
        }
        items(20) { index ->
            ListItem(
                headlineContent = { Text("Comment $index") }
            )
        }
    }
}
```

---

#### Image Viewer

```kotlin
@Composable
fun ImageViewerScreen(imageUrl: String) {
    var isZoomed by remember { mutableStateOf(false) }
    val view = LocalView.current

    DisposableEffect(isZoomed) {
        val window = (view.context as Activity).window
        val insetsController = WindowCompat.getInsetsController(window, view)

        if (isZoomed) {
            window.statusBarColor = Color.Black.toArgb()
            window.navigationBarColor = Color.Black.toArgb()
            insetsController.hide(WindowInsetsCompat.Type.systemBars())
        } else {
            window.statusBarColor = Color.Transparent.toArgb()
            window.navigationBarColor = Color.Transparent.toArgb()
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }

        onDispose {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(if (isZoomed) Color.Black else Color.White)
            .clickable { isZoomed = !isZoomed }
    ) {
        AsyncImage(
            model = imageUrl,
            contentDescription = "Image",
            modifier = Modifier.fillMaxSize(),
            contentScale = if (isZoomed) ContentScale.Fit else ContentScale.Crop
        )

        if (!isZoomed) {
            // Show UI elements
            IconButton(
                onClick = { /* Back */ },
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .windowInsetsPadding(WindowInsets.statusBars)
                    .padding(8.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Back"
                )
            }
        }
    }
}
```

---

#### Chat Screen with Keyboard

```kotlin
@Composable
fun ChatScreen(messages: List<Message>) {
    var messageText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()

    // Scroll to bottom when keyboard appears
    val imeVisible = WindowInsets.ime.asPaddingValues().calculateBottomPadding() > 0.dp

    LaunchedEffect(imeVisible) {
        if (imeVisible && messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Chat") },
                modifier = Modifier.windowInsetsPadding(WindowInsets.statusBars)
            )
        },
        bottomBar = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .imePadding()  // Move above keyboard
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextField(
                    value = messageText,
                    onValueChange = { messageText = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Message") }
                )

                IconButton(
                    onClick = {
                        // Send message
                        messageText = ""
                    }
                ) {
                    Icon(Icons.Default.Send, contentDescription = "Send")
                }
            }
        },
        contentWindowInsets = WindowInsets(0)
    ) { paddingValues ->
        LazyColumn(
            state = listState,
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp)
        ) {
            items(messages) { message ->
                MessageBubble(message)
            }
        }
    }
}

@Composable
fun MessageBubble(message: Message) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = if (message.isMine) {
            Arrangement.End
        } else {
            Arrangement.Start
        }
    ) {
        Card(
            colors = CardDefaults.cardColors(
                containerColor = if (message.isMine) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.surfaceVariant
                }
            )
        ) {
            Text(
                text = message.text,
                modifier = Modifier.padding(12.dp),
                color = if (message.isMine) {
                    MaterialTheme.colorScheme.onPrimary
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                }
            )
        }
    }
}

data class Message(val text: String, val isMine: Boolean)
```

---

### WINDOWINSETS IN XML (View System)

```kotlin
// For Views (not Compose)
class EdgeToEdgeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Enable edge-to-edge
        WindowCompat.setDecorFitsSystemWindows(window, false)

        setContentView(R.layout.activity_edge_to_edge)

        val rootView = findViewById<View>(R.id.root)

        ViewCompat.setOnApplyWindowInsetsListener(rootView) { view, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())

            view.updatePadding(
                top = systemBars.top,
                bottom = systemBars.bottom
            )

            insets
        }
    }
}
```

---

### KEY TAKEAWAYS

1. **enableEdgeToEdge()** or `WindowCompat.setDecorFitsSystemWindows(window, false)`
2. **WindowInsets.systemBars** includes status + navigation bars
3. **windowInsetsPadding()** modifier applies insets as padding
4. **imePadding()** automatically handles keyboard
5. **WindowInsets.displayCutout** handles notches/cutouts
6. **Combine insets** with union() for complex layouts
7. **System bar colors** should be transparent for edge-to-edge
8. **Hide system bars** with WindowInsetsController for immersive
9. **Consume insets** to prevent double-padding
10. **Test on devices** with different notches, gesture navigation

---

## Russian Version

### Постановка задачи

Edge-to-edge дизайн позволяет приложениям рисовать за системными барами (status bar, navigation bar), создавая иммерсивный опыт. WindowInsets API помогает обрабатывать видимость системного UI и безопасные области контента. Понимание этого критично для современного Android UI.

**Вопрос:** Что такое WindowInsets? Как реализовать edge-to-edge дизайн? Как обрабатывать системные бары, вырезы и insets клавиатуры в Compose?

### Ключевые выводы

1. **enableEdgeToEdge()** или `WindowCompat.setDecorFitsSystemWindows(window, false)`
2. **WindowInsets.systemBars** включает status + navigation bars
3. **windowInsetsPadding()** modifier применяет insets как padding
4. **imePadding()** автоматически обрабатывает клавиатуру
5. **WindowInsets.displayCutout** обрабатывает notches/cutouts
6. **Комбинируйте insets** с union() для сложных layouts
7. **Цвета системных баров** должны быть прозрачными для edge-to-edge
8. **Скрывайте системные бары** с WindowInsetsController для immersive
9. **Consume insets** чтобы избежать двойного padding
10. **Тестируйте на устройствах** с разными notches, жестовой навигацией

## Follow-ups

1. How do you handle WindowInsets in landscape orientation?
2. What's the difference between windowInsetsPadding and padding?
3. How do you implement edge-to-edge with bottom sheets?
4. What are the performance implications of WindowInsets?
5. How do you test edge-to-edge layouts?
6. What is the relationship between WindowInsets and Modifier.safeDrawingPadding?
7. How do you handle WindowInsets in multi-window mode?
8. What are the accessibility considerations for edge-to-edge?
9. How do you animate WindowInsets changes?
10. What is WindowInsetsAnimationCompat?

## Related Questions

- [[q-sharedpreferences-definition--android--easy]]
- [[q-diffutil-background-calculation-issues--android--medium]]
- [[q-build-optimization-gradle--android--medium]]
