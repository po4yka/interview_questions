---
id: 20251017-150243
title: "Migration To Compose / Миграция на Compose"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-what-does-viewgroup-inherit-from--android--easy, q-what-is-known-about-methods-that-redraw-view--android--medium, q-recyclerview-explained--android--medium]
created: 2025-10-15
tags: [jetpack-compose, migration, xml-to-compose, architecture, difficulty/medium]
---

# Стратегия миграции большого проекта на Jetpack Compose

**English**: Migration strategy for large project to Jetpack Compose

## Answer (EN)
Миграция большого проекта на Compose требует поэтапного подхода, минимизирующего риски и позволяющего продолжать разработку новых фич во время миграции.

### Recommended strategy: Hybrid approach

**Principle**: Gradual bottom-up migration, starting with leaf UI components.

### Phase 1: Project preparation

#### Updating dependencies

```gradle
// app/build.gradle
android {
    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.3"
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }
}

dependencies {
    // Compose BOM (Bill of Materials)
    implementation platform('androidx.compose:compose-bom:2023.10.01')

    // Compose libraries
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.material3:material3'
    implementation 'androidx.compose.ui:ui-tooling-preview'
    implementation 'androidx.activity:activity-compose:1.8.0'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2'

    // Навигация
    implementation 'androidx.navigation:navigation-compose:2.7.5'

    // Интероперабельность с Views
    implementation 'androidx.compose.ui:ui-viewbinding'

    // Debugging
    debugImplementation 'androidx.compose.ui:ui-tooling'
    debugImplementation 'androidx.compose.ui:ui-test-manifest'
}
```

### Phase 2: ComposeView inside existing XML

Start small: add Compose components inside existing screens.

```kotlin
// Existing XML layout (activity_main.xml)
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Existing XML UI -->
    <TextView
        android:id="@+id/titleText"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"/>

    <!-- NEW: Compose inside XML -->
    <androidx.compose.ui.platform.ComposeView
        android:id="@+id/composeView"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"/>

    <!-- Existing RecyclerView -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"/>
</LinearLayout>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Compose integration
        findViewById<ComposeView>(R.id.composeView).setContent {
            MaterialTheme {
                // New UI in Compose
                UserProfileCard(
                    user = viewModel.currentUser.collectAsState().value
                )
            }
        }

        // Existing code for XML views
        findViewById<TextView>(R.id.titleText).text = "My App"
    }
}

@Composable
fun UserProfileCard(user: User?) {
    if (user != null) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleLarge
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}
```

### Phase 3: AndroidView for embedding XML in Compose

Reverse approach: use XML views inside Compose.

```kotlin
@Composable
fun LegacyMapView(location: Location) {
    AndroidView(
        factory = { context ->
            // Create existing XML View
            MapView(context).apply {
                onCreate(null)
                getMapAsync { googleMap ->
                    googleMap.moveCamera(
                        CameraUpdateFactory.newLatLngZoom(location.toLatLng(), 15f)
                    )
                }
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}

@Composable
fun LegacyRecyclerView(items: List<Item>) {
    AndroidView(
        factory = { context ->
            RecyclerView(context).apply {
                layoutManager = LinearLayoutManager(context)
                adapter = ItemAdapter(items)
            }
        },
        update = { recyclerView ->
            // Update adapter when items change
            (recyclerView.adapter as? ItemAdapter)?.updateItems(items)
        }
    )
}
```

### Phase 4: Modular migration

Split app into feature modules and migrate each separately.

```
app/
 feature-auth/          ← Migrate first (small module)
    xml/              (old code)
    compose/          (new code)
 feature-profile/       ← Migrate second
 feature-feed/          ← Migrate third
 feature-messaging/     ← Leave for later (complex)
 core/
     ui-xml/           (shared XML components)
     ui-compose/       (shared Compose components)
```

#### Module example after migration

```kotlin
// feature-auth/LoginScreen.kt (new Compose)
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = hiltViewModel(),
    onLoginSuccess: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Login") })
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            OutlinedTextField(
                value = uiState.email,
                onValueChange = viewModel::onEmailChanged,
                label = { Text("Email") },
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = uiState.password,
                onValueChange = viewModel::onPasswordChanged,
                label = { Text("Password") },
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = viewModel::onLoginClick,
                enabled = !uiState.isLoading,
                modifier = Modifier.fillMaxWidth()
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White
                    )
                } else {
                    Text("Login")
                }
            }

            LaunchedEffect(uiState.loginSuccess) {
                if (uiState.loginSuccess) {
                    onLoginSuccess()
                }
            }
        }
    }
}
```

### Phase 5: Navigation - hybrid approach

#### Option A: Navigation Component with Compose destinations

```kotlin
// nav_graph.xml
<navigation>
    <!-- XML screens -->
    <fragment
        android:id="@+id/homeFragment"
        android:name="com.app.HomeFragment"/>

    <!-- Compose screens as dialog/fragment -->
    <fragment
        android:id="@+id/profileScreen"
        android:name="com.app.ComposeFragment">
        <argument
            android:name="screen"
            android:defaultValue="profile"/>
    </fragment>
</navigation>

// ComposeFragment - universal container
class ComposeFragment : Fragment() {
    override fun onCreateView(...): View {
        return ComposeView(requireContext()).apply {
            setContent {
                MaterialTheme {
                    when (arguments?.getString("screen")) {
                        "profile" -> ProfileScreen()
                        "settings" -> SettingsScreen()
                        else -> Text("Unknown screen")
                    }
                }
            }
        }
    }
}
```

#### Option B: Compose Navigation for new screens

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        // New Compose screens
        composable("home") {
            HomeScreen(navController)
        }

        composable("profile/{userId}") { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            ProfileScreen(userId, navController)
        }

        // Old XML screens via AndroidViewBinding
        composable("legacy_settings") {
            AndroidViewBinding(SettingsFragmentBinding::inflate) {
                // Configure XML View
            }
        }
    }
}
```

### Phase 6: Shared components (Design System)

Create Compose versions of shared UI components in parallel with XML.

```kotlin
// Before migration: XML custom view
class CustomButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : AppCompatButton(context, attrs) {
    // Custom button logic
}

// After: Compose component
@Composable
fun CustomButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier,
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.primary
        )
    ) {
        Text(text)
    }
}

// Transition period: both versions available
// New code uses Compose version
// Old code continues using XML version
```

### Phase 7: Testing at each step

```kotlin
// Compose UI tests
@get:Rule
val composeTestRule = createComposeRule()

@Test
fun loginScreen_displaysEmailField() {
    composeTestRule.setContent {
        LoginScreen(onLoginSuccess = {})
    }

    composeTestRule
        .onNodeWithText("Email")
        .assertIsDisplayed()
}

@Test
fun loginButton_showsLoadingState() {
    val viewModel = FakeLoginViewModel(isLoading = true)

    composeTestRule.setContent {
        LoginScreen(viewModel = viewModel, onLoginSuccess = {})
    }

    composeTestRule
        .onNode(hasContentDescription("Loading"))
        .assertExists()
}
```

### Migration plan (example for 50+ screen project)

**Phase 1 (1-2 months):** Infrastructure
- Add Compose dependencies
- Create Compose Design System
- Setup testing
- Train team

**Phase 2 (2-3 months):** New features Compose-only
- All new screens Compose only
- Refactor simple screens (Login, Settings)
- Complex screens remain XML

**Phase 3 (3-6 months):** Gradual migration
- Migrate screens by priority
- Rewrite RecyclerView → LazyColumn
- Complex custom views → Canvas/Compose

**Phase 4 (1-2 months):** Finalization
- Remove XML layouts
- Remove Views dependencies
- 100% Compose

**Total**: ~9-13 months for full migration

### Common migration patterns

| XML Component | Compose Alternative |
|---------------|----------------------|
| `RecyclerView` | `LazyColumn` / `LazyRow` |
| `ViewPager2` | `HorizontalPager` |
| `ConstraintLayout` | `ConstraintLayout` (Compose version) |
| `Fragment` | `@Composable` function |
| `LiveData.observe()` | `collectAsState()` |
| `findViewById()` | State hoisting |
| `include` layout | Composable function call |

### Risks and solutions

**Risk 1: Performance degradation**
```kotlin
// Solution: Profiling and optimization
@Composable
fun HeavyList(items: List<Item>) {
    // Bad - recreated every time
    val sorted = items.sortedBy { it.name }

    // Good - cached
    val sorted = remember(items) {
        items.sortedBy { it.name }
    }

    LazyColumn {
        items(sorted, key = { it.id }) { item ->
            ItemRow(item)
        }
    }
}
```

**Risk 2: APK size increases**
```gradle
// Solution: R8 and ProGuard optimizations
android {
    buildTypes {
        release {
            minifyEnabled = true
            shrinkResources = true
        }
    }
}
```

**Risk 3: Complex custom views**
```kotlin
// Solution: Canvas API in Compose
@Composable
fun CustomChart(data: List<DataPoint>) {
    Canvas(modifier = Modifier.fillMaxSize()) {
        // Drawing with Compose Canvas
        data.forEachIndexed { index, point ->
            drawCircle(
                color = Color.Blue,
                center = Offset(point.x, point.y),
                radius = 10f
            )
        }
    }
}
```

**English**: Migrate large project to Compose using **hybrid approach**: 1) Add **ComposeView** inside existing XML layouts, 2) Use **AndroidView** for XML views inside Compose, 3) **Modular migration** - migrate feature modules one by one, 4) Create Compose **Design System** in parallel with XML, 5) New features Compose-only, 6) Gradual screen migration (simple → complex), 7) Test after each phase. Timeline: 9-13 months for 50+ screen app. Start with leaf components, progress bottom-up. Keep both XML and Compose during transition.

## Ответ (RU)

Мигрируйте большой проект на Compose используя **гибридный подход**: 1) Добавьте **ComposeView** внутри существующих XML layouts, 2) Используйте **AndroidView** для XML views внутри Compose, 3) **Модульная миграция** - мигрируйте feature модули один за другим, 4) Создайте Compose **Design System** параллельно с XML, 5) Новые фичи только на Compose, 6) Постепенная миграция экранов (простые → сложные), 7) Тестируйте после каждой фазы. Временная шкала: 9-13 месяцев для приложения с 50+ экранами. Начинайте с leaf компонентов, продвигайтесь снизу вверх. Сохраняйте и XML, и Compose во время перехода.

### Рекомендуемая стратегия: Гибридный подход

**Принцип**: Постепенная миграция снизу вверх, начиная с конечных UI компонентов.

### Фаза 1: Подготовка проекта

Обновите зависимости, добавьте Compose BOM, настройте buildFeatures.

### Фаза 2: ComposeView внутри существующего XML

Начните с малого: добавьте Compose компоненты внутри существующих экранов через ComposeView в XML layout.

### Фаза 3: AndroidView для встраивания XML в Compose

Обратный подход: используйте XML views внутри Compose через AndroidView для legacy компонентов.

### Фаза 4: Модульная миграция

Разделите приложение на feature модули и мигрируйте каждый отдельно. Начните с малых модулей (feature-auth), затем более крупные.

### Фаза 5: Навигация - гибридный подход

**Вариант A**: Navigation Component с Compose destinations
**Вариант B**: Compose Navigation для новых экранов

### Фаза 6: Общие компоненты (Design System)

Создайте Compose версии общих UI компонентов параллельно с XML. В переходный период оба варианта доступны.

### Фаза 7: Тестирование на каждом шаге

Используйте Compose UI тесты с createComposeRule для проверки новых компонентов.

### План миграции (пример для проекта с 50+ экранами)

**Фаза 1 (1-2 месяца):** Инфраструктура
**Фаза 2 (2-3 месяца):** Новые фичи только Compose
**Фаза 3 (3-6 месяцев):** Постепенная миграция
**Фаза 4 (1-2 месяца):** Финализация

**Итого**: ~9-13 месяцев для полной миграции


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
- [[q-compose-stability-skippability--android--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations

