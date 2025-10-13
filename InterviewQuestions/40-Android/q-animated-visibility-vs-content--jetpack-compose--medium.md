---
topic: android
subtopics: [ui-animation, jetpack-compose]
tags:
  - jetpack-compose
  - animations
  - transitions
  - animated-visibility
  - ui
difficulty: medium
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# AnimatedVisibility vs AnimatedContent vs Crossfade

# Question (EN)
> Compare AnimatedVisibility, AnimatedContent, and Crossfade. When should you use each?

# Вопрос (RU)
> Сравните AnimatedVisibility, AnimatedContent и Crossfade. Когда следует использовать каждый из них?

---

## Answer (EN)

Compose provides three main APIs for content transitions: **AnimatedVisibility**, **AnimatedContent**, and **Crossfade**. Each serves different use cases and provides different animation capabilities.

---

### AnimatedVisibility

**Purpose:** Show/hide content with enter/exit animations.

**When to use:**
- Toggle visibility on/off
- Show/hide optional UI elements
- Expand/collapse sections
- Show modals, tooltips, etc.

**Key features:**
- Enter transitions (fade in, slide in, scale in, expand)
- Exit transitions (fade out, slide out, scale out, shrink)
- Simultaneous enter/exit animations
- Children can animate independently

```kotlin
@Composable
fun AnimatedVisibilityExample() {
    var visible by remember { mutableStateOf(false) }

    Column {
        Button(onClick = { visible = !visible }) {
            Text(if (visible) "Hide" else "Show")
        }

        AnimatedVisibility(
            visible = visible,
            enter = fadeIn() + slideInVertically(),
            exit = fadeOut() + slideOutVertically()
        ) {
            Text(
                "Hello, I'm animated!",
                modifier = Modifier
                    .padding(16.dp)
                    .background(Color.Blue, RoundedCornerShape(8.dp))
                    .padding(16.dp)
            )
        }
    }
}
```

---

**Advanced AnimatedVisibility:**

```kotlin
@Composable
fun ExpandableCard() {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded }
    ) {
        Column {
            Text(
                "Card Header",
                modifier = Modifier.padding(16.dp)
            )

            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically(
                    animationSpec = spring(
                        dampingRatio = Spring.DampingRatioLowBouncy,
                        stiffness = Spring.StiffnessLow
                    )
                ) + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Expanded content line 1")
                    Text("Expanded content line 2")
                    Text("Expanded content line 3")
                }
            }
        }
    }
}
```

---

**Individual child animations:**

```kotlin
@Composable
fun StaggeredAnimation() {
    var visible by remember { mutableStateOf(false) }

    Column {
        Button(onClick = { visible = !visible }) {
            Text("Toggle")
        }

        AnimatedVisibility(visible = visible) {
            Column {
                // Each child can have different animations
                Text(
                    "First",
                    modifier = Modifier.animateEnterExit(
                        enter = slideInHorizontally { -it },
                        exit = slideOutHorizontally { -it }
                    )
                )

                Text(
                    "Second",
                    modifier = Modifier.animateEnterExit(
                        enter = slideInHorizontally { it },
                        exit = slideOutHorizontally { it }
                    )
                )

                Text(
                    "Third",
                    modifier = Modifier.animateEnterExit(
                        enter = fadeIn(animationSpec = tween(1000)),
                        exit = fadeOut(animationSpec = tween(1000))
                    )
                )
            }
        }
    }
}
```

---

### AnimatedContent

**Purpose:** Animate between different content based on a target state.

**When to use:**
- Switching between different screens/views
- Updating content based on state (loading → success → error)
- Carousel/pager-like transitions
- Form wizard steps

**Key features:**
- Content changes based on `targetState`
- Sophisticated transition animations
- Content size changes animate automatically
- Supports custom transitions per state change

```kotlin
@Composable
fun AnimatedContentExample() {
    var count by remember { mutableStateOf(0) }

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        AnimatedContent(
            targetState = count,
            transitionSpec = {
                // Define how to transition from initialState to targetState
                if (targetState > initialState) {
                    // Increment: slide up
                    slideInVertically { it } + fadeIn() togetherWith
                        slideOutVertically { -it } + fadeOut()
                } else {
                    // Decrement: slide down
                    slideInVertically { -it } + fadeIn() togetherWith
                        slideOutVertically { it } + fadeOut()
                }.using(
                    SizeTransform(clip = false)
                )
            },
            label = "count"
        ) { targetCount ->
            // Content changes based on targetCount
            Text(
                text = "$targetCount",
                style = MaterialTheme.typography.displayLarge
            )
        }

        Row {
            Button(onClick = { count-- }) {
                Text("−")
            }
            Spacer(Modifier.width(16.dp))
            Button(onClick = { count++ }) {
                Text("+")
            }
        }
    }
}
```

---

**State machine example:**

```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: String) : UiState()
    data class Error(val message: String) : UiState()
}

@Composable
fun LoadingStateMachine() {
    var state by remember { mutableStateOf<UiState>(UiState.Loading) }

    Column {
        AnimatedContent(
            targetState = state,
            transitionSpec = {
                fadeIn(animationSpec = tween(300)) togetherWith
                    fadeOut(animationSpec = tween(300))
            },
            label = "state_machine"
        ) { targetState ->
            when (targetState) {
                is UiState.Loading -> {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        CircularProgressIndicator()
                        Text("Loading...")
                    }
                }

                is UiState.Success -> {
                    Column {
                        Icon(Icons.Default.CheckCircle, "Success")
                        Text("Success: ${targetState.data}")
                    }
                }

                is UiState.Error -> {
                    Column {
                        Icon(Icons.Default.Error, "Error")
                        Text(
                            "Error: ${targetState.message}",
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                }
            }
        }

        Row {
            Button(onClick = { state = UiState.Loading }) {
                Text("Loading")
            }
            Button(onClick = { state = UiState.Success("Data loaded!") }) {
                Text("Success")
            }
            Button(onClick = { state = UiState.Error("Failed!") }) {
                Text("Error")
            }
        }
    }
}
```

---

**Custom transitions per state pair:**

```kotlin
@Composable
fun CustomTransitions() {
    var step by remember { mutableStateOf(1) }

    AnimatedContent(
        targetState = step,
        transitionSpec = {
            when {
                // Step 1 → 2: Slide left
                initialState == 1 && targetState == 2 -> {
                    slideInHorizontally { it } togetherWith
                        slideOutHorizontally { -it }
                }
                // Step 2 → 3: Slide up
                initialState == 2 && targetState == 3 -> {
                    slideInVertically { it } togetherWith
                        slideOutVertically { -it }
                }
                // Any backward: Fade
                targetState < initialState -> {
                    fadeIn() togetherWith fadeOut()
                }
                // Default: Scale
                else -> {
                    scaleIn() togetherWith scaleOut()
                }
            }.using(SizeTransform(clip = false))
        },
        label = "steps"
    ) { currentStep ->
        when (currentStep) {
            1 -> StepOneContent()
            2 -> StepTwoContent()
            3 -> StepThreeContent()
            else -> Text("Unknown step")
        }
    }
}
```

---

### Crossfade

**Purpose:** Simple crossfade transition between content.

**When to use:**
- Simple content switching
- No directional animation needed
- Want smooth, simple fade transition
- Tab content switching

**Key features:**
- Simplest API
- Only fade animation
- No enter/exit control
- No size animation

```kotlin
@Composable
fun CrossfadeExample() {
    var screen by remember { mutableStateOf("home") }

    Column {
        Row {
            Button(onClick = { screen = "home" }) {
                Text("Home")
            }
            Button(onClick = { screen = "profile" }) {
                Text("Profile")
            }
            Button(onClick = { screen = "settings" }) {
                Text("Settings")
            }
        }

        Crossfade(
            targetState = screen,
            animationSpec = tween(300),
            label = "screen"
        ) { currentScreen ->
            when (currentScreen) {
                "home" -> HomeScreen()
                "profile" -> ProfileScreen()
                "settings" -> SettingsScreen()
            }
        }
    }
}

@Composable
fun HomeScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.LightGray),
        contentAlignment = Alignment.Center
    ) {
        Text("Home Screen")
    }
}

@Composable
fun ProfileScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Cyan),
        contentAlignment = Alignment.Center
    ) {
        Text("Profile Screen")
    }
}

@Composable
fun SettingsScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Yellow),
        contentAlignment = Alignment.Center
    ) {
        Text("Settings Screen")
    }
}
```

---

### Comparison Table

| Feature | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| **Primary use** | Show/hide | State-based content | Simple switching |
| **Animations** | Enter/Exit | Custom per transition | Fade only |
| **Direction control** |  Yes |  Yes |  No |
| **Size animation** |  Yes |  Yes |  No |
| **Child animations** |  Yes |  No |  No |
| **API complexity** | Medium | High | Low |
| **Flexibility** | High | Highest | Low |
| **Common use case** | Collapsible sections | Screen transitions | Tab content |

---

### When to Use What

**Use AnimatedVisibility when:**
```kotlin
//  Toggling visibility
var showMenu by remember { mutableStateOf(false) }
AnimatedVisibility(visible = showMenu) {
    DropdownMenu()
}

//  Expand/collapse
var expanded by remember { mutableStateOf(false) }
AnimatedVisibility(visible = expanded) {
    DetailedContent()
}

//  Conditional UI elements
AnimatedVisibility(visible = hasError) {
    ErrorMessage()
}
```

---

**Use AnimatedContent when:**
```kotlin
//  Multiple states with different content
AnimatedContent(targetState = loadingState) { state ->
    when (state) {
        Loading -> LoadingSpinner()
        Success -> SuccessView()
        Error -> ErrorView()
    }
}

//  Directional transitions
AnimatedContent(
    targetState = currentPage,
    transitionSpec = {
        if (targetState > initialState) {
            slideInHorizontally { it } togetherWith slideOutHorizontally { -it }
        } else {
            slideInHorizontally { -it } togetherWith slideOutHorizontally { it }
        }
    }
) { page ->
    PageContent(page)
}

//  Form wizards
AnimatedContent(targetState = step) { currentStep ->
    when (currentStep) {
        1 -> PersonalInfoForm()
        2 -> AddressForm()
        3 -> ConfirmationForm()
    }
}
```

---

**Use Crossfade when:**
```kotlin
//  Simple tab switching
Crossfade(targetState = selectedTab) { tab ->
    when (tab) {
        Tab.Home -> HomeContent()
        Tab.Search -> SearchContent()
        Tab.Profile -> ProfileContent()
    }
}

//  Image switching
Crossfade(targetState = currentImageUrl) { imageUrl ->
    AsyncImage(model = imageUrl, contentDescription = null)
}

//  Simple content swap
Crossfade(targetState = isLoggedIn) { loggedIn ->
    if (loggedIn) {
        MainApp()
    } else {
        LoginScreen()
    }
}
```

---

### Real-World Example: Complete UI

```kotlin
@Composable
fun CompleteAnimationExample() {
    var selectedTab by remember { mutableStateOf(0) }
    var showFilters by remember { mutableStateOf(false) }
    var loadingState by remember { mutableStateOf<LoadState>(LoadState.Success) }

    Column {
        // Tab bar
        TabRow(selectedTab) {
            Tab(
                selected = selectedTab == 0,
                onClick = { selectedTab = 0 }
            ) {
                Text("List")
            }
            Tab(
                selected = selectedTab == 1,
                onClick = { selectedTab = 1 }
            ) {
                Text("Grid")
            }
        }

        // Filter toggle
        Row {
            Button(onClick = { showFilters = !showFilters }) {
                Text("Filters")
            }
        }

        // ANIMATED VISIBILITY: Filter section
        AnimatedVisibility(
            visible = showFilters,
            enter = expandVertically() + fadeIn(),
            exit = shrinkVertically() + fadeOut()
        ) {
            FilterSection()
        }

        // ANIMATED CONTENT: Loading state
        AnimatedContent(
            targetState = loadingState,
            transitionSpec = {
                fadeIn(tween(300)) togetherWith fadeOut(tween(300))
            }
        ) { state ->
            when (state) {
                is LoadState.Loading -> LoadingView()
                is LoadState.Success -> {
                    // CROSSFADE: Tab content
                    Crossfade(targetState = selectedTab) { tab ->
                        when (tab) {
                            0 -> ListViewContent()
                            1 -> GridViewContent()
                        }
                    }
                }
                is LoadState.Error -> ErrorView(state.message)
            }
        }
    }
}

sealed class LoadState {
    object Loading : LoadState()
    object Success : LoadState()
    data class Error(val message: String) : LoadState()
}
```

---

### Best Practices

**1. Choose based on use case:**

```kotlin
//  DO: Match animation to intent
AnimatedVisibility(visible = expanded) // Reveal/hide
AnimatedContent(targetState = step)    // State changes
Crossfade(targetState = tab)          // Simple switch
```

**2. Consider performance:**

```kotlin
//  AnimatedVisibility: Most efficient
// Only one content tree, show/hide

//  AnimatedContent: Creates new content
// Old and new content exist during transition

//  Crossfade: Lightweight
// Simple fade, minimal overhead
```

**3. Use appropriate animation specs:**

```kotlin
// Quick UI feedback
enter = fadeIn(tween(150))

// Smooth natural motion
enter = slideInVertically(spring())

// Attention-grabbing
enter = scaleIn(spring(dampingRatio = Spring.DampingRatioHighBouncy))
```

**4. Consider content size:**

```kotlin
// For size-changing content
AnimatedContent(
    targetState = state,
    transitionSpec = {
        fadeIn() togetherWith fadeOut() using
            SizeTransform(clip = false) // Animate size
    }
) { /* content */ }
```

---

## Ответ (RU)

Compose предоставляет три основных API для переходов контента: **AnimatedVisibility**, **AnimatedContent** и **Crossfade**. Каждый служит разным целям и предоставляет разные возможности анимации.

### AnimatedVisibility

**Назначение:** Показать/скрыть контент с анимацией появления/исчезновения.

**Когда использовать:**
- Переключение видимости вкл/выкл
- Показ/скрытие опциональных UI элементов
- Раскрытие/сворачивание секций

**Ключевые возможности:**
- Переходы появления (fade in, slide in, scale in, expand)
- Переходы исчезновения (fade out, slide out, scale out, shrink)
- Одновременные анимации появления/исчезновения
- Дочерние элементы могут анимироваться независимо

### AnimatedContent

**Назначение:** Анимация между разным контентом на основе целевого состояния.

**Когда использовать:**
- Переключение между разными экранами/представлениями
- Обновление контента на основе состояния (загрузка → успех → ошибка)
- Переходы карусели/пейджера
- Шаги мастера форм

**Ключевые возможности:**
- Контент меняется на основе `targetState`
- Сложные переходные анимации
- Изменения размера контента анимируются автоматически
- Поддержка пользовательских переходов для каждого изменения состояния

### Crossfade

**Назначение:** Простой переход с перекрестным затуханием между контентом.

**Когда использовать:**
- Простое переключение контента
- Не нужна направленная анимация
- Нужен плавный, простой переход
- Переключение контента вкладок

**Ключевые возможности:**
- Простейший API
- Только анимация затухания
- Нет контроля появления/исчезновения
- Нет анимации размера

### Таблица сравнения

| Функция | AnimatedVisibility | AnimatedContent | Crossfade |
|---------|-------------------|-----------------|-----------|
| **Основное использование** | Показ/скрытие | Контент на основе состояния | Простое переключение |
| **Анимации** | Появление/Исчезновение | Пользовательские для перехода | Только затухание |
| **Контроль направления** |  Да |  Да |  Нет |
| **Анимация размера** |  Да |  Да |  Нет |
| **Сложность API** | Средняя | Высокая | Низкая |
| **Гибкость** | Высокая | Наивысшая | Низкая |

### Лучшие практики

1. Выбирайте на основе использования
2. Учитывайте производительность
3. Используйте подходящие спецификации анимации
4. Учитывайте размер контента

Правильный выбор API анимации делает UI более отзывчивым и приятным для пользователей.


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

