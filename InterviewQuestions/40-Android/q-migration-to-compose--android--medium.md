---
topic: android
tags:
  - android
  - jetpack-compose
  - migration
  - xml-to-compose
  - architecture
difficulty: medium
status: reviewed
---

# Стратегия миграции большого проекта на Jetpack Compose

**English**: Migration strategy for large project to Jetpack Compose

## Answer

Миграция большого проекта на Compose требует поэтапного подхода, минимизирующего риски и позволяющего продолжать разработку новых фич во время миграции.

### Рекомендуемая стратегия: Гибридный подход

**Принцип**: Постепенная миграция снизу вверх, начиная с листовых компонентов UI.

### Этап 1: Подготовка проекта

#### Обновление зависимостей

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

### Этап 2: ComposeView внутри существующих XML

Начните с малого: добавляйте Compose компоненты внутри существующих экранов.

```kotlin
// Существующий XML layout (activity_main.xml)
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Существующий XML UI -->
    <TextView
        android:id="@+id/titleText"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"/>

    <!-- НОВЫЙ: Compose внутри XML -->
    <androidx.compose.ui.platform.ComposeView
        android:id="@+id/composeView"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"/>

    <!-- Существующая RecyclerView -->
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

        // Интеграция Compose
        findViewById<ComposeView>(R.id.composeView).setContent {
            MaterialTheme {
                // Новый UI на Compose
                UserProfileCard(
                    user = viewModel.currentUser.collectAsState().value
                )
            }
        }

        // Существующий код для XML views
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

### Этап 3: AndroidView для встраивания XML в Compose

Обратный подход: используйте XML views внутри Compose.

```kotlin
@Composable
fun LegacyMapView(location: Location) {
    AndroidView(
        factory = { context ->
            // Создать существующий XML View
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
            // Обновить adapter при изменении items
            (recyclerView.adapter as? ItemAdapter)?.updateItems(items)
        }
    )
}
```

### Этап 4: Модульная миграция

Разделите приложение на фича-модули и мигрируйте каждый модуль отдельно.

```
app/
├── feature-auth/          ← Мигрировать первым (небольшой модуль)
│   ├── xml/              (старый код)
│   └── compose/          (новый код)
├── feature-profile/       ← Мигрировать вторым
├── feature-feed/          ← Мигрировать третьим
├── feature-messaging/     ← Оставить на потом (сложный)
└── core/
    ├── ui-xml/           (общие XML компоненты)
    └── ui-compose/       (общие Compose компоненты)
```

#### Пример модуля после миграции

```kotlin
// feature-auth/LoginScreen.kt (новый Compose)
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

### Этап 5: Навигация - гибридный подход

#### Вариант А: Navigation Component с Compose destinations

```kotlin
// nav_graph.xml
<navigation>
    <!-- XML экраны -->
    <fragment
        android:id="@+id/homeFragment"
        android:name="com.app.HomeFragment"/>

    <!-- Compose экраны как dialog/fragment -->
    <fragment
        android:id="@+id/profileScreen"
        android:name="com.app.ComposeFragment">
        <argument
            android:name="screen"
            android:defaultValue="profile"/>
    </fragment>
</navigation>

// ComposeFragment - универсальный контейнер
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

#### Вариант Б: Compose Navigation для новых экранов

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        // Новые Compose экраны
        composable("home") {
            HomeScreen(navController)
        }

        composable("profile/{userId}") { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            ProfileScreen(userId, navController)
        }

        // Старые XML экраны через AndroidViewBinding
        composable("legacy_settings") {
            AndroidViewBinding(SettingsFragmentBinding::inflate) {
                // Настроить XML View
            }
        }
    }
}
```

### Этап 6: Общие компоненты (Design System)

Создайте Compose версии общих UI компонентов параллельно с XML.

```kotlin
// До миграции: XML custom view
class CustomButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : AppCompatButton(context, attrs) {
    // Custom button logic
}

// После: Compose компонент
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

// Переходный период: оба варианта доступны
// Новый код использует Compose версию
// Старый код продолжает использовать XML версию
```

### Этап 7: Тестирование на каждом шаге

```kotlin
// Compose UI тесты
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

### План миграции (пример для проекта на 50+ экранов)

**Фаза 1 (1-2 месяца):** Инфраструктура
- - Добавить Compose зависимости
- - Создать Design System на Compose
- - Настроить тестирование
- - Обучить команду

**Фаза 2 (2-3 месяца):** Новые фичи только на Compose
- - Все новые экраны только Compose
- - Рефакторинг простых экранов (Login, Settings)
- ⏳ Сложные экраны остаются на XML

**Фаза 3 (3-6 месяцев):** Постепенная миграция
- ⏳ Миграция экранов по приоритету
- ⏳ Переписать RecyclerView → LazyColumn
- ⏳ Сложные кастомные views → Canvas/Compose

**Фаза 4 (1-2 месяца):** Финализация
- ⏳ Удалить XML layouts
- ⏳ Удалить зависимости на Views
- - 100% Compose

**Итого**: ~9-13 месяцев для полной миграции

### Общие паттерны миграции

| XML Компонент | Compose Альтернатива |
|---------------|----------------------|
| `RecyclerView` | `LazyColumn` / `LazyRow` |
| `ViewPager2` | `HorizontalPager` |
| `ConstraintLayout` | `ConstraintLayout` (Compose version) |
| `Fragment` | `@Composable` function |
| `LiveData.observe()` | `collectAsState()` |
| `findViewById()` | State hoisting |
| `include` layout | Composable function call |

### Риски и решения

**Риск 1: Performance degradation**
```kotlin
// Решение: Profiling и оптимизация
@Composable
fun HeavyList(items: List<Item>) {
    // - Плохо - пересоздается каждый раз
    val sorted = items.sortedBy { it.name }

    // ✓ Хорошо - кэшируется
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

**Риск 2: Размер APK увеличивается**
```gradle
// Решение: R8 и ProGuard оптимизации
android {
    buildTypes {
        release {
            minifyEnabled = true
            shrinkResources = true
        }
    }
}
```

**Риск 3: Сложные кастомные views**
```kotlin
// Решение: Canvas API в Compose
@Composable
fun CustomChart(data: List<DataPoint>) {
    Canvas(modifier = Modifier.fillMaxSize()) {
        // Рисование с помощью Compose Canvas
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
