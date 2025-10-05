---
tags:
  - android
  - testing
  - junit
  - espresso
  - mockito
  - quality-assurance
difficulty: medium
---

# Методы тестирования Android приложений

**English**: What testing methods are used in Android besides UI tests?

## Answer

Для проверки кода на наличие багов в Android приложениях кроме UI тестов применяются различные виды тестирования и инструменты. Эти методы помогают обнаружить ошибки на разных уровнях и стадиях разработки.

### 1. Модульное тестирование (Unit Tests)

Проверяет отдельные модули или компоненты приложения. Выполняется на JVM без Android-зависимостей.

**Инструменты**: JUnit, Mockito, MockK

```kotlin
// ViewModel Unit Test
class UserViewModelTest {
    private lateinit var viewModel: UserViewModel
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        // Mock repository
        repository = mockk()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUsers should update users LiveData`() = runTest {
        // Given
        val expectedUsers = listOf(
            User(1, "Alice", "alice@example.com"),
            User(2, "Bob", "bob@example.com")
        )
        coEvery { repository.getUsers() } returns expectedUsers

        // When
        viewModel.loadUsers()

        // Then
        assertEquals(expectedUsers, viewModel.users.value)
    }

    @Test
    fun `loadUsers should handle error`() = runTest {
        // Given
        val exception = IOException("Network error")
        coEvery { repository.getUsers() } throws exception

        // When
        viewModel.loadUsers()

        // Then
        assertEquals("Network error", viewModel.error.value)
        assertTrue(viewModel.users.value.isNullOrEmpty())
    }
}

// Business Logic Unit Test
class CalculatorTest {
    private lateinit var calculator: Calculator

    @Before
    fun setup() {
        calculator = Calculator()
    }

    @Test
    fun `add should return sum of two numbers`() {
        // Given
        val a = 5
        val b = 3

        // When
        val result = calculator.add(a, b)

        // Then
        assertEquals(8, result)
    }

    @Test
    fun `divide should throw exception when dividing by zero`() {
        assertThrows<ArithmeticException> {
            calculator.divide(10, 0)
        }
    }
}
```

**Структура теста (Given-When-Then)**:

```kotlin
@Test
fun `user login should succeed with valid credentials`() {
    // Given (Arrange) - подготовка данных
    val username = "user@example.com"
    val password = "password123"
    val expectedUser = User(1, "User", username)

    coEvery { authRepository.login(username, password) } returns Result.Success(expectedUser)

    // When (Act) - выполнение действия
    viewModel.login(username, password)

    // Then (Assert) - проверка результата
    assertEquals(expectedUser, viewModel.currentUser.value)
    assertFalse(viewModel.isLoading.value)
    assertNull(viewModel.error.value)
}
```

### 2. Интеграционное тестирование

Проверяет взаимодействие между различными модулями приложения.

**Инструменты**: Espresso, Robolectric, AndroidX Test

```kotlin
// Robolectric Test (выполняется на JVM)
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P])
class MainActivityTest {
    private lateinit var activity: MainActivity

    @Before
    fun setup() {
        activity = Robolectric.buildActivity(MainActivity::class.java)
            .create()
            .start()
            .resume()
            .get()
    }

    @Test
    fun `clicking button should update text view`() {
        // Given
        val button = activity.findViewById<Button>(R.id.button)
        val textView = activity.findViewById<TextView>(R.id.textView)

        // When
        button.performClick()

        // Then
        assertEquals("Button clicked!", textView.text.toString())
    }

    @Test
    fun `activity should show user data from ViewModel`() {
        // Given
        val viewModel = activity.viewModel
        val expectedUser = User(1, "Alice", "alice@example.com")

        // When
        viewModel.setUser(expectedUser)

        // Then
        val nameTextView = activity.findViewById<TextView>(R.id.userName)
        assertEquals("Alice", nameTextView.text.toString())
    }
}

// Integration Test с Room Database
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        userDao = database.userDao()
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun insertAndRetrieveUser() = runBlocking {
        // Given
        val user = User(1, "Alice", "alice@example.com")

        // When
        userDao.insertUser(user)
        val retrievedUsers = userDao.getAllUsers()

        // Then
        assertEquals(1, retrievedUsers.size)
        assertEquals(user, retrievedUsers[0])
    }

    @Test
    fun updateUser() = runBlocking {
        // Given
        val user = User(1, "Alice", "alice@example.com")
        userDao.insertUser(user)

        // When
        val updatedUser = user.copy(name = "Alice Smith")
        userDao.updateUser(updatedUser)

        // Then
        val retrievedUser = userDao.getUserById(1)
        assertEquals("Alice Smith", retrievedUser.name)
    }
}
```

### 3. UI тестирование (Instrumented Tests)

Выполняется на реальном устройстве или эмуляторе.

**Инструменты**: Espresso, UI Automator

```kotlin
@RunWith(AndroidJUnit4::class)
@LargeTest
class LoginActivityEspressoTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun loginWithValidCredentials_shouldNavigateToHome() {
        // Given - вводим данные
        onView(withId(R.id.emailEditText))
            .perform(typeText("user@example.com"), closeSoftKeyboard())

        onView(withId(R.id.passwordEditText))
            .perform(typeText("password123"), closeSoftKeyboard())

        // When - нажимаем кнопку
        onView(withId(R.id.loginButton))
            .perform(click())

        // Then - проверяем переход на главный экран
        onView(withId(R.id.homeScreen))
            .check(matches(isDisplayed()))
    }

    @Test
    fun loginWithInvalidCredentials_shouldShowError() {
        // Given
        onView(withId(R.id.emailEditText))
            .perform(typeText("invalid@example.com"))

        onView(withId(R.id.passwordEditText))
            .perform(typeText("wrong"), closeSoftKeyboard())

        // When
        onView(withId(R.id.loginButton))
            .perform(click())

        // Then
        onView(withText("Invalid credentials"))
            .check(matches(isDisplayed()))
    }

    @Test
    fun recyclerViewScrollAndClick() {
        // Scroll to position
        onView(withId(R.id.recyclerView))
            .perform(RecyclerViewActions.scrollToPosition<RecyclerView.ViewHolder>(10))

        // Click on item
        onView(withId(R.id.recyclerView))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                    10,
                    click()
                )
            )

        // Verify detail screen
        onView(withId(R.id.detailScreen))
            .check(matches(isDisplayed()))
    }
}

// UI Automator для тестирования вне приложения
@RunWith(AndroidJUnit4::class)
class SystemUITest {
    private lateinit var device: UiDevice

    @Before
    fun setup() {
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
    }

    @Test
    fun testShareIntent() {
        // Launch app
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = context.packageManager.getLaunchIntentForPackage(PACKAGE_NAME)
        context.startActivity(intent)

        // Click share button
        device.findObject(UiSelector().resourceId("$PACKAGE_NAME:id/shareButton"))
            .click()

        // Verify share sheet appears
        val shareSheet = device.findObject(UiSelector().text("Share via"))
        assertTrue(shareSheet.exists())
    }
}
```

### 4. Регрессионное тестирование

Обеспечивает что новые изменения в коде не приводят к появлению новых багов.

```kotlin
// Автоматизация регрессионных тестов
@RunWith(Suite::class)
@Suite.SuiteClasses(
    LoginFlowTest::class,
    RegistrationFlowTest::class,
    ProfileUpdateTest::class,
    PaymentFlowTest::class
)
class RegressionTestSuite

// Параметризованные тесты для проверки разных сценариев
@RunWith(Parameterized::class)
class EmailValidationTest(
    private val email: String,
    private val expected: Boolean
) {
    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "{index}: email={0}, valid={1}")
        fun data() = listOf(
            arrayOf("valid@example.com", true),
            arrayOf("invalid.email", false),
            arrayOf("@example.com", false),
            arrayOf("user@", false),
            arrayOf("user@domain.co.uk", true)
        )
    }

    @Test
    fun testEmailValidation() {
        val validator = EmailValidator()
        assertEquals(expected, validator.isValid(email))
    }
}
```

### 5. Тестирование производительности

Оценивает производительность приложения под разной нагрузкой.

**Инструменты**: Android Profiler, Firebase Performance, Benchmark library

```kotlin
// Benchmark Test
@RunWith(AndroidJUnit4::class)
class DatabaseBenchmark {
    @get:Rule
    val benchmarkRule = BenchmarkRule()

    @Test
    fun benchmarkDatabaseQuery() {
        benchmarkRule.measureRepeated {
            // Код для тестирования производительности
            val users = database.userDao().getAllUsers()
            require(users.isNotEmpty())
        }
    }
}

// Performance profiling in code
fun startPerformanceMonitoring() {
    val trace = FirebasePerformance.getInstance().newTrace("user_load")
    trace.start()

    try {
        // Код для измерения
        loadUsers()
    } finally {
        trace.stop()
    }
}

// Memory leak detection with LeakCanary
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            // LeakCanary автоматически обнаруживает утечки памяти
            LeakCanary.config = LeakCanary.config.copy(
                dumpHeap = true,
                dumpHeapWhenDebugging = true
            )
        }
    }
}
```

### 6. Статический анализ кода

Анализирует исходный код без выполнения программы.

**Инструменты**: Lint, Detekt, SonarQube, Checkstyle

```kotlin
// build.gradle - настройка Lint
android {
    lint {
        checkReleaseBuilds = true
        abortOnError = true
        warningsAsErrors = true

        disable += listOf("MissingTranslation", "ExtraTranslation")
        enable += listOf("RtlHardcoded", "ObsoleteSdkInt")

        textReport = true
        textOutput = file("stdout")

        htmlReport = true
        htmlOutput = file("$buildDir/reports/lint-report.html")

        xmlReport = true
        xmlOutput = file("$buildDir/reports/lint-report.xml")
    }
}

// Detekt configuration (detekt.yml)
detekt {
    buildUponDefaultConfig = true
    allRules = false
    config = files("$projectDir/config/detekt.yml")

    reports {
        html.enabled = true
        xml.enabled = true
        txt.enabled = true
    }
}

// Suppressing warnings
@Suppress("MagicNumber")
fun calculatePrice(quantity: Int): Double {
    return quantity * 19.99
}
```

### 7. Тестирование безопасности

Проверяет уязвимости приложения.

**Инструменты**: OWASP ZAP, ProGuard, R8

```kotlin
// ProGuard configuration (proguard-rules.pro)

# Обфускация кода
-keep class com.example.model.** { *; }
-dontwarn com.example.external.**

# Защита от reverse engineering
-optimizationpasses 5
-dontusemixedcaseclassnames
-dontskipnonpubliclibraryclasses
-dontpreverify
-verbose

# Certificate pinning для защиты от MITM
class SecureNetworkConfig {
    fun createOkHttpClient(): OkHttpClient {
        val certificatePinner = CertificatePinner.Builder()
            .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            .build()

        return OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .build()
    }
}

// Encrypted SharedPreferences
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

### 8. Snapshot Testing (Screenshot Testing)

Проверяет визуальную регрессию UI.

```kotlin
// Screenshot Test с Shot
@RunWith(AndroidJUnit4::class)
class ScreenshotTest : ScreenshotTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun homeScreenSnapshot() {
        compareScreenshot(activityRule.scenario, name = "home_screen")
    }

    @Test
    fun composableSnapshot() {
        composeTestRule.setContent {
            UserProfileScreen(
                user = User(1, "Alice", "alice@example.com")
            )
        }

        composeTestRule.onRoot()
            .captureToImage()
            .assertAgainstGolden("user_profile")
    }
}
```

### Сравнительная таблица тестов

| Тип теста | Скорость | Покрытие | Надежность | Инструменты | Когда использовать |
|-----------|----------|----------|------------|-------------|-------------------|
| **Unit** | ⚡⚡⚡ Быстрые | ⭐ Низкое | ⭐⭐⭐ Высокая | JUnit, Mockito | Бизнес-логика, утилиты |
| **Integration** | ⚡⚡ Средние | ⭐⭐ Среднее | ⭐⭐⭐ Высокая | Robolectric, Room | Взаимодействие модулей |
| **UI** | ⚡ Медленные | ⭐⭐⭐ Высокое | ⭐⭐ Средняя | Espresso, UI Automator | E2E сценарии |
| **Snapshot** | ⚡⚡ Средние | ⭐⭐ Среднее | ⭐⭐ Средняя | Shot, Paparazzi | Визуальная регрессия |
| **Performance** | ⚡ Медленные | ⭐ Низкое | ⭐⭐ Средняя | Profiler, Benchmark | Оптимизация |

### Best Practices

**1. Пирамида тестирования**

```
         UI Tests (10%)
        /              \
   Integration (20%)
  /                    \
Unit Tests (70%)
```

```kotlin
// ✓ ПРАВИЛЬНО - большинство тестов на уровне Unit
class UserRepositoryTest {
    @Test fun getAllUsers() { /* ... */ }
    @Test fun getUserById() { /* ... */ }
    @Test fun createUser() { /* ... */ }
    @Test fun updateUser() { /* ... */ }
    @Test fun deleteUser() { /* ... */ }
}

// ✓ ПРАВИЛЬНО - меньше интеграционных тестов
class UserDaoIntegrationTest {
    @Test fun insertAndRetrieve() { /* ... */ }
    @Test fun complexQuery() { /* ... */ }
}

// ✓ ПРАВИЛЬНО - минимум UI тестов для критических флоу
class LoginFlowUITest {
    @Test fun successfulLoginFlow() { /* ... */ }
}
```

**2. Изоляция тестов**

```kotlin
// ✓ ПРАВИЛЬНО - каждый тест независим
@Test
fun test1() {
    val repository = createRepository()
    // Test logic
}

@Test
fun test2() {
    val repository = createRepository()
    // Test logic - не зависит от test1
}

// ❌ НЕПРАВИЛЬНО - тесты зависят друг от друга
private var sharedRepository: Repository? = null

@Test
fun test1() {
    sharedRepository = createRepository()
    sharedRepository?.addUser(user)
}

@Test
fun test2() {
    // Зависит от выполнения test1!
    assertEquals(1, sharedRepository?.getUserCount())
}
```

**3. Тестовое покрытие**

```kotlin
// build.gradle - включение отчетов о покрытии
android {
    buildTypes {
        debug {
            testCoverageEnabled = true
        }
    }
}

// Запуск тестов с покрытием
// ./gradlew testDebugUnitTestCoverage
// ./gradlew createDebugCoverageReport

// Минимальное покрытие (рекомендации)
// Unit tests: 70-80%
// Integration: 50-60%
// UI tests: 20-30%
```

**English**: Android testing strategies include: **Unit tests** (JUnit, Mockito for logic), **Integration tests** (Robolectric, Room tests for module interaction), **UI tests** (Espresso, UI Automator for end-to-end flows), **Regression tests** (automated suites), **Performance tests** (Profiler, Benchmark), **Static analysis** (Lint, Detekt, SonarQube), **Security tests** (ProGuard, certificate pinning), **Snapshot tests** (Screenshot testing). Follow testing pyramid: 70% unit, 20% integration, 10% UI. Use Given-When-Then pattern for clear tests.
