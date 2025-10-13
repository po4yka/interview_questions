---
tags:
  - testing
  - robolectric
  - instrumented-tests
  - strategy
  - comparison
  - unit-testing
difficulty: medium
status: draft
---

# Robolectric vs Instrumented Tests

# Question (EN)
> When should you use Robolectric vs instrumented tests? What are the tradeoffs in speed, reliability, and coverage?

# Вопрос (RU)
> Когда следует использовать Robolectric вместо инструментальных тестов? Какие компромиссы в скорости, надежности и покрытии?

---

## Answer (EN)

**Robolectric** runs Android tests on the JVM without a device/emulator, while **Instrumented tests** run on actual Android devices. Each has distinct advantages and tradeoffs.

---

### Robolectric Tests

**Robolectric** simulates Android framework on JVM:

```kotlin
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P])
class MainActivityTest {
    @Test
    fun buttonClick_updatesText() {
        val scenario = launchActivity<MainActivity>()

        scenario.onActivity { activity ->
            val button = activity.findViewById<Button>(R.id.button)
            val textView = activity.findViewById<TextView>(R.id.textView)

            button.performClick()

            assertEquals("Clicked!", textView.text)
        }
    }
}
```

**Key characteristics:**
-  Runs on JVM (fast)
-  No device needed
-  Works in CI without emulator
-  Simulated Android (not real)
-  May have subtle differences from real device

---

### Instrumented Tests

**Instrumented tests** run on real Android:

```kotlin
@RunWith(AndroidJUnit4::class)
class MainActivityInstrumentedTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun buttonClick_updatesText() {
        onView(withId(R.id.button))
            .perform(click())

        onView(withId(R.id.textView))
            .check(matches(withText("Clicked!")))
    }
}
```

**Key characteristics:**
-  Real Android environment
-  Tests actual device behavior
-  Hardware sensors, GPS, camera
-  Slow (requires device/emulator)
-  Requires emulator/device for CI
-  Flaky (environment-dependent)

---

### Speed Comparison

| Type | Execution Time | Feedback Loop |
|------|---------------|---------------|
| **Unit tests (pure JVM)** | 0.1 - 1s | Instant |
| **Robolectric** | 1 - 10s | Fast |
| **Instrumented** | 10 - 60s+ | Slow |

**Example benchmark:**

```
Test Suite: 100 tests

Unit tests: 5 seconds
Robolectric: 45 seconds
Instrumented: 8 minutes
```

---

### When to Use Robolectric

** GOOD use cases:**

**1. ViewModel tests with Android dependencies:**

```kotlin
@RunWith(RobolectricTestRunner::class)
class UserViewModelTest {
    private lateinit var viewModel: UserViewModel
    private lateinit var context: Context

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        viewModel = UserViewModel(context)
    }

    @Test
    fun loadUser_updatesUiState() = runTest {
        viewModel.loadUser(1)

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Success)
    }
}
```

**2. Testing Activities/Fragments without UI:**

```kotlin
@RunWith(RobolectricTestRunner::class)
class UserFragmentTest {
    @Test
    fun onCreate_loadsUserData() {
        val fragment = UserFragment()
        val scenario = launchFragmentInContainer { fragment }

        scenario.onFragment {
            assertNotNull(it.viewModel)
            assertTrue(it.isDataLoaded)
        }
    }
}
```

**3. Testing Resources and Context:**

```kotlin
@RunWith(RobolectricTestRunner::class)
class ResourceTest {
    @Test
    fun getString_returnsCorrectValue() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        val appName = context.getString(R.string.app_name)

        assertEquals("My App", appName)
    }
}
```

**4. Testing Intent handling:**

```kotlin
@RunWith(RobolectricTestRunner::class)
class IntentTest {
    @Test
    fun shareButton_launchesShareIntent() {
        val scenario = launchActivity<MainActivity>()

        scenario.onActivity { activity ->
            activity.findViewById<Button>(R.id.shareButton).performClick()

            val intent = shadowOf(activity).nextStartedActivity
            assertEquals(Intent.ACTION_SEND, intent.action)
        }
    }
}
```

---

### When to Use Instrumented Tests

** GOOD use cases:**

**1. Complex UI interactions:**

```kotlin
@RunWith(AndroidJUnit4::class)
class ComplexUiTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun swipeToDelete_removesItem() {
        composeTestRule.setContent {
            ItemList(items = listOf("Item 1", "Item 2"))
        }

        composeTestRule
            .onNodeWithText("Item 1")
            .performTouchInput { swipeLeft() }

        composeTestRule
            .onNodeWithText("Item 1")
            .assertDoesNotExist()
    }
}
```

**2. Hardware interactions:**

```kotlin
@RunWith(AndroidJUnit4::class)
class CameraTest {
    @Test
    fun capturePhoto_savesToGallery() {
        // Real camera interaction
        onView(withId(R.id.captureButton)).perform(click())

        // Wait for capture
        Thread.sleep(1000)

        // Verify image saved
        val images = getGalleryImages()
        assertTrue(images.isNotEmpty())
    }
}
```

**3. Performance testing:**

```kotlin
@RunWith(AndroidJUnit4::class)
class PerformanceTest {
    @Test
    fun scrollLargeList_measuresPerformance() {
        val metrics = mutableListOf<Long>()

        repeat(10) {
            val start = System.currentTimeMillis()

            onView(withId(R.id.recyclerView))
                .perform(scrollToPosition(1000))

            metrics.add(System.currentTimeMillis() - start)
        }

        val avgTime = metrics.average()
        assertTrue(avgTime < 100) // Should be fast
    }
}
```

**4. Third-party SDK integration:**

```kotlin
@RunWith(AndroidJUnit4::class)
class FirebaseTest {
    @Test
    fun login_authenticatesWithFirebase() {
        // Real Firebase authentication
        onView(withId(R.id.emailField))
            .perform(typeText("user@example.com"))

        onView(withId(R.id.passwordField))
            .perform(typeText("password"))

        onView(withId(R.id.loginButton))
            .perform(click())

        // Wait for auth
        onView(withId(R.id.welcomeText))
            .check(matches(isDisplayed()))
    }
}
```

---

### Comparison Table

| Aspect | Robolectric | Instrumented |
|--------|-------------|--------------|
| **Speed** |  Fast (1-10s) |  Slow (10-60s+) |
| **Setup** |  Simple |  Requires device |
| **CI Integration** |  Easy |  Needs emulator |
| **Reliability** |  Consistent |  Can be flaky |
| **Real device** |  Simulated |  Real |
| **Hardware** |  Mocked |  Real sensors |
| **Debugging** |  IDE breakpoints |  ADB/Logcat |
| **Coverage** |  Framework only |  Full stack |
| **Android versions** |  Limited |  All versions |

---

### Testing Pyramid Strategy

Use this distribution:

```
      /\
     /  \     10% - E2E Instrumented
    /    \
   /------\   20% - Integration (Robolectric)
  /        \
 /----------\  70% - Unit Tests (Pure JVM)
```

**Example breakdown:**

```kotlin
// 70% - Pure JVM Unit Tests
class CalculatorTest {
    @Test
    fun add_returnsSum() {
        val calculator = Calculator()
        assertEquals(5, calculator.add(2, 3))
    }
}

// 20% - Robolectric Integration Tests
@RunWith(RobolectricTestRunner::class)
class UserViewModelTest {
    @Test
    fun loadUser_updatesState() = runTest {
        val viewModel = UserViewModel(context)
        viewModel.loadUser(1)
        assertTrue(viewModel.uiState.value is UiState.Success)
    }
}

// 10% - Instrumented E2E Tests
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @Test
    fun completeLoginFlow_navigatesToHome() {
        // Full user journey on real device
        loginScreen {
            enterEmail("user@example.com")
            enterPassword("password")
            clickLogin()
        }

        homeScreen {
            assertIsDisplayed()
        }
    }
}
```

---

### Decision Matrix

**Use Robolectric when:**
- Testing ViewModels with Android dependencies
- Testing Fragment/Activity lifecycle
- Testing Resources, Context, SharedPreferences
- Testing Intent creation
- Need fast feedback in CI
- Don't need real device behavior

**Use Instrumented when:**
- Testing complex UI interactions (swipe, drag, animations)
- Testing hardware (camera, GPS, sensors)
- Testing performance
- Testing third-party SDKs (Firebase, Google Maps)
- Testing WebView behavior
- Testing on multiple device configurations
- Need pixel-perfect screenshot testing

---

### Hybrid Approach

Combine both for optimal coverage:

```kotlin
// Robolectric: Business logic + simple UI
@RunWith(RobolectricTestRunner::class)
class UserProfileFragmentTest {
    @Test
    fun loadProfile_displaysUserInfo() {
        val fragment = launchFragment<UserProfileFragment>()

        fragment.onFragment {
            val nameView = it.view?.findViewById<TextView>(R.id.userName)
            assertEquals("John Doe", nameView?.text)
        }
    }
}

// Instrumented: Critical user flows
@RunWith(AndroidJUnit4::class)
class UserProfileE2ETest {
    @Test
    fun editProfile_updatesAndSyncs() {
        // Real UI interaction
        onView(withId(R.id.editButton)).perform(click())
        onView(withId(R.id.nameField)).perform(replaceText("Jane Doe"))
        onView(withId(R.id.saveButton)).perform(click())

        // Verify sync to backend
        onView(withText("Profile updated")).check(matches(isDisplayed()))
    }
}
```

---

### Best Practices

**1. Start with unit tests:**

```kotlin
//  DO: Test business logic without Android
class UserRepositoryTest {
    @Test
    fun getUser_returnsUser() = runTest {
        val repository = UserRepository()
        val user = repository.getUser(1)
        assertEquals("John", user.name)
    }
}
```

**2. Use Robolectric for integration:**

```kotlin
//  DO: Test Android components quickly
@RunWith(RobolectricTestRunner::class)
class FragmentIntegrationTest {
    @Test
    fun fragment_loadsData() {
        val scenario = launchFragmentInContainer<UserFragment>()
        // Fast integration test
    }
}
```

**3. Reserve instrumented for critical paths:**

```kotlin
//  DO: E2E tests for critical flows
@RunWith(AndroidJUnit4::class)
class CheckoutFlowTest {
    @Test
    fun completeCheckout_processesPayment() {
        // Full checkout flow on real device
    }
}
```

**4. Use test tags for organization:**

```gradle
android {
    testOptions {
        unitTests {
            isIncludeAndroidResources = true // For Robolectric
        }
    }
}
```

---

## Ответ (RU)

**Robolectric** запускает Android тесты на JVM без устройства/эмулятора, в то время как **Инструментальные тесты** выполняются на реальных Android устройствах. Каждый имеет свои преимущества и компромиссы.

### Robolectric тесты

Robolectric симулирует Android framework на JVM. Быстрые, работают без устройства, но симулированные.

### Инструментальные тесты

Выполняются на реальном Android. Тестируют реальное поведение устройства, но медленные и требуют эмулятора.

### Сравнение скорости

- Unit тесты: 0.1-1с
- Robolectric: 1-10с
- Инструментальные: 10-60с+

### Когда использовать Robolectric

- Тестирование ViewModel с Android зависимостями
- Тестирование жизненного цикла Activity/Fragment
- Тестирование Resources, Context
- Нужна быстрая обратная связь в CI

### Когда использовать Инструментальные тесты

- Сложные UI взаимодействия
- Взаимодействие с hardware
- Тестирование производительности
- Интеграция с третьими SDK

### Пирамида тестирования

- 70% - Unit тесты (чистый JVM)
- 20% - Интеграционные (Robolectric)
- 10% - E2E Инструментальные

### Лучшие практики

1. Начинайте с unit тестов
2. Используйте Robolectric для интеграции
3. Оставьте инструментальные тесты для критических путей
4. Комбинируйте оба подхода для оптимального покрытия

Правильная стратегия тестирования обеспечивает быструю обратную связь и высокое качество.

---

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-screenshot-snapshot-testing--testing--medium]] - Testing
- [[q-fakes-vs-mocks-testing--testing--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--testing--hard]] - Testing
