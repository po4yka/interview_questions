---
id: 20251012-12271197
title: "Screenshot and Snapshot Testing / Screenshot и Snapshot тестирование"
aliases: [Screenshot and Snapshot Testing, Screenshot и Snapshot тестирование]
topic: android
subtopics: [testing-ui]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-kmm-production-readiness--multiplatform--hard, q-hilt-entry-points--di--medium, q-privacy-sandbox-topics-api--privacy--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/testing-ui, difficulty/medium]
---

# Screenshot and Snapshot Testing

# Question (EN)

> Implement screenshot testing with Paparazzi or Shot. How do you handle different screen sizes and themes?

# Вопрос (RU)

> Реализуйте screenshot тестирование с помощью Paparazzi или Shot. Как обрабатывать разные размеры экранов и темы?

---

## Answer (EN)

**Screenshot testing** (visual regression testing) captures UI renders and compares them against baseline images to detect unintended visual changes. **Paparazzi** and **Shot** are popular libraries for Android.

---

### Paparazzi

**Paparazzi** renders Compose/View-based UIs on JVM without devices:

```gradle
// build.gradle.kts
plugins {
    id("app.cash.paparazzi") version "1.3.1"
}

dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.1")
}
```

**Basic usage:**

```kotlin
class ButtonScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun button_defaultState() {
        paparazzi.snapshot {
            Button(onClick = {}) {
                Text("Click Me")
            }
        }
    }

    @Test
    fun button_disabled() {
        paparazzi.snapshot {
            Button(
                onClick = {},
                enabled = false
            ) {
                Text("Disabled")
            }
        }
    }
}
```

**Running tests:**

```bash
# Record baseline screenshots
./gradlew recordPaparazziDebug

# Verify screenshots match baseline
./gradlew verifyPaparazziDebug
```

---

### Different Device Configurations

```kotlin
class ResponsiveScreenshotTest {
    @Test
    fun userProfile_phone() {
        val paparazzi = Paparazzi(
            deviceConfig = DeviceConfig.PIXEL_5
        )

        paparazzi.snapshot {
            UserProfileScreen()
        }
    }

    @Test
    fun userProfile_tablet() {
        val paparazzi = Paparazzi(
            deviceConfig = DeviceConfig.PIXEL_C
        )

        paparazzi.snapshot {
            UserProfileScreen()
        }
    }

    @Test
    fun userProfile_customSize() {
        val paparazzi = Paparazzi(
            deviceConfig = DeviceConfig(
                screenHeight = 1920,
                screenWidth = 1080,
                xdpi = 420,
                ydpi = 420,
                orientation = ScreenOrientation.PORTRAIT,
                uiMode = Configuration.UI_MODE_NIGHT_NO,
                locale = "en-rUS",
                fontScale = 1f,
                screenRound = ScreenRound.NOTROUND,
                softButtons = true,
                navigation = Navigation.NAV_BAR
            )
        )

        paparazzi.snapshot("custom_device") {
            UserProfileScreen()
        }
    }
}
```

---

### Testing Themes

```kotlin
class ThemeScreenshotTest {
    @Test
    fun button_lightTheme() {
        val paparazzi = Paparazzi(
            deviceConfig = DeviceConfig.PIXEL_5.copy(
                uiMode = Configuration.UI_MODE_NIGHT_NO
            )
        )

        paparazzi.snapshot {
            MaterialTheme(
                colorScheme = lightColorScheme()
            ) {
                Surface {
                    Button(onClick = {}) {
                        Text("Light Theme")
                    }
                }
            }
        }
    }

    @Test
    fun button_darkTheme() {
        val paparazzi = Paparazzi(
            deviceConfig = DeviceConfig.PIXEL_5.copy(
                uiMode = Configuration.UI_MODE_NIGHT_YES
            )
        )

        paparazzi.snapshot {
            MaterialTheme(
                colorScheme = darkColorScheme()
            ) {
                Surface {
                    Button(onClick = {}) {
                        Text("Dark Theme")
                    }
                }
            }
        }
    }
}
```

---

### Parameterized Screenshot Tests

```kotlin
class ParameterizedScreenshotTest {
    private val devices = listOf(
        DeviceConfig.PIXEL_5,
        DeviceConfig.PIXEL_6,
        DeviceConfig.PIXEL_C
    )

    private val themes = listOf(
        "light" to Configuration.UI_MODE_NIGHT_NO,
        "dark" to Configuration.UI_MODE_NIGHT_YES
    )

    @Test
    fun userProfile_allConfigurations() {
        devices.forEach { device ->
            themes.forEach { (themeName, uiMode) ->
                val paparazzi = Paparazzi(
                    deviceConfig = device.copy(uiMode = uiMode)
                )

                paparazzi.snapshot("${device.name}_$themeName") {
                    UserProfileScreen()
                }
            }
        }
    }
}
```

---

### Testing Different States

```kotlin
class StateScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun loginScreen_states() {
        // Empty state
        paparazzi.snapshot("empty") {
            LoginScreen(
                email = "",
                password = "",
                isLoading = false,
                error = null
            )
        }

        // Filled state
        paparazzi.snapshot("filled") {
            LoginScreen(
                email = "user@example.com",
                password = "password",
                isLoading = false,
                error = null
            )
        }

        // Loading state
        paparazzi.snapshot("loading") {
            LoginScreen(
                email = "user@example.com",
                password = "password",
                isLoading = true,
                error = null
            )
        }

        // Error state
        paparazzi.snapshot("error") {
            LoginScreen(
                email = "user@example.com",
                password = "password",
                isLoading = false,
                error = "Invalid credentials"
            )
        }
    }
}
```

---

### Shot Library

**Shot** uses instrumented tests for screenshot comparison:

```gradle
// build.gradle.kts (project)
plugins {
    id("com.karumi.shot") version "6.1.0"
}

// build.gradle.kts (app)
apply(plugin = "shot")
```

**Basic usage:**

```kotlin
@RunWith(AndroidJUnit4::class)
class MainActivityScreenshotTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun mainActivity_screenshot() {
        compareScreenshot(activityRule.scenario)
    }
}

// Compose
@RunWith(AndroidJUnit4::class)
class ComposeScreenshotTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun button_screenshot() {
        composeTestRule.setContent {
            Button(onClick = {}) {
                Text("Click Me")
            }
        }

        compareScreenshot(composeTestRule)
    }
}
```

**Running Shot:**

```bash
# Record baseline
./gradlew executeScreenshotTests -Precord

# Verify screenshots
./gradlew executeScreenshotTests
```

---

### Shot with Multiple Devices

```kotlin
@RunWith(AndroidJUnit4::class)
class ResponsiveShotTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun userProfile_phone() {
        composeTestRule.activity.requestedOrientation =
            ActivityInfo.SCREEN_ORIENTATION_PORTRAIT

        composeTestRule.setContent {
            UserProfileScreen()
        }

        compareScreenshot(
            composeTestRule,
            name = "user_profile_phone"
        )
    }

    @Test
    fun userProfile_landscape() {
        composeTestRule.activity.requestedOrientation =
            ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE

        composeTestRule.setContent {
            UserProfileScreen()
        }

        compareScreenshot(
            composeTestRule,
            name = "user_profile_landscape"
        )
    }
}
```

---

### Paparazzi vs Shot Comparison

| Feature        | Paparazzi           | Shot                  |
| -------------- | ------------------- | --------------------- |
| **Speed**      | Fast (JVM)          | Slow (Device)         |
| **Setup**      | Simple              | Requires device       |
| **CI**         | No emulator needed  | Needs emulator        |
| **Accuracy**   | Simulated rendering | Real device rendering |
| **Compose**    | Full support        | Full support          |
| **Views**      | Supported           | Supported             |
| **Animations** | Limited             | Full support          |
| **Hardware**   | No real hardware    | Real hardware         |

---

### Real-World Example: Complete Test Suite

```kotlin
@RunWith(JUnit4::class)
class UserProfileScreenshotSuite {
    data class TestConfig(
        val device: DeviceConfig,
        val theme: ColorScheme,
        val themeName: String,
        val fontScale: Float = 1f
    )

    private val testConfigs = listOf(
        // Phone - Light
        TestConfig(
            device = DeviceConfig.PIXEL_5,
            theme = lightColorScheme(),
            themeName = "light"
        ),
        // Phone - Dark
        TestConfig(
            device = DeviceConfig.PIXEL_5,
            theme = darkColorScheme(),
            themeName = "dark"
        ),
        // Tablet - Light
        TestConfig(
            device = DeviceConfig.PIXEL_C,
            theme = lightColorScheme(),
            themeName = "light"
        ),
        // Large font
        TestConfig(
            device = DeviceConfig.PIXEL_5,
            theme = lightColorScheme(),
            themeName = "light_large_font",
            fontScale = 1.5f
        )
    )

    @Test
    fun userProfile_allConfigurations() {
        testConfigs.forEach { config ->
            val paparazzi = Paparazzi(
                deviceConfig = config.device.copy(
                    fontScale = config.fontScale
                )
            )

            val testName = "${config.device.name}_${config.themeName}"

            // Loading state
            paparazzi.snapshot("${testName}_loading") {
                MaterialTheme(colorScheme = config.theme) {
                    Surface {
                        UserProfileScreen(
                            uiState = UiState.Loading
                        )
                    }
                }
            }

            // Success state
            paparazzi.snapshot("${testName}_success") {
                MaterialTheme(colorScheme = config.theme) {
                    Surface {
                        UserProfileScreen(
                            uiState = UiState.Success(
                                user = User(
                                    name = "John Doe",
                                    email = "john@example.com",
                                    avatar = null
                                )
                            )
                        )
                    }
                }
            }

            // Error state
            paparazzi.snapshot("${testName}_error") {
                MaterialTheme(colorScheme = config.theme) {
                    Surface {
                        UserProfileScreen(
                            uiState = UiState.Error("Failed to load user")
                        )
                    }
                }
            }
        }
    }
}
```

---

### Handling Flaky Screenshots

**Problem: Non-deterministic rendering**

```kotlin
//  BAD: Animations cause different screenshots
@Test
fun animatedButton() {
    paparazzi.snapshot {
        AnimatedButton() // Animation might be at different frame
    }
}

//  GOOD: Disable animations
@Test
fun animatedButton() {
    paparazzi.snapshot {
        CompositionLocalProvider(
            LocalAnimationEnabled provides false
        ) {
            AnimatedButton()
        }
    }
}
```

**Problem: Timestamps/dynamic content**

```kotlin
//  BAD: Timestamp changes every time
@Test
fun messageView() {
    paparazzi.snapshot {
        MessageView(
            text = "Hello",
            timestamp = System.currentTimeMillis()
        )
    }
}

//  GOOD: Fixed timestamp
@Test
fun messageView() {
    paparazzi.snapshot {
        MessageView(
            text = "Hello",
            timestamp = 1234567890000L // Fixed
        )
    }
}
```

---

### CI Integration

**GitHub Actions with Paparazzi:**

```yaml
name: Screenshot Tests

on: [pull_request]

jobs:
    screenshot-tests:
        runs-on: ubuntu-latest

        steps:
            - uses: actions/checkout@v3

            - name: Set up JDK
              uses: actions/setup-java@v3
              with:
                  java-version: "17"

            - name: Run Paparazzi Tests
              run: ./gradlew verifyPaparazziDebug

            - name: Upload test results
              if: failure()
              uses: actions/upload-artifact@v3
              with:
                  name: paparazzi-failures
                  path: app/build/paparazzi/failures
```

---

### Best Practices

**1. Test critical UI components:**

```kotlin
//  DO: Test reusable components
@Test fun testButton()
@Test fun testCard()
@Test fun testNavigationBar()
```

**2. Test multiple states:**

```kotlin
//  DO: Test all states
@Test fun loading()
@Test fun success()
@Test fun error()
@Test fun empty()
```

**3. Use descriptive names:**

```kotlin
//  DO: Clear names
paparazzi.snapshot("user_profile_light_phone_portrait") { }

//  DON'T: Vague names
paparazzi.snapshot("test1") { }
```

**4. Keep tests fast:**

```kotlin
//  DO: Use Paparazzi for most tests
//  DO: Use Shot only for critical flows
```

---

## Ответ (RU)

**Screenshot тестирование** (визуальное регрессионное тестирование) захватывает рендеры UI и сравнивает их с базовыми изображениями для обнаружения непреднамеренных визуальных изменений. **Paparazzi** и **Shot** — популярные библиотеки для Android.

### Paparazzi

**Paparazzi** рендерит Compose/View UI на JVM без устройств. Быстро, работает в CI без эмулятора.

### Shot

**Shot** использует инструментальные тесты для сравнения screenshots. Точный рендеринг, но медленнее.

### Разные конфигурации устройств

Тестируйте разные размеры экранов (телефон, планшет), ориентации и масштабы шрифтов.

### Тестирование тем

Тестируйте светлую и темную темы для всех компонентов.

### Параметризованные тесты

Создавайте тесты для всех комбинаций устройств, тем и состояний.

### Обработка нестабильных screenshots

-   Отключайте анимации
-   Используйте фиксированные timestamps
-   Избегайте динамического контента

### CI интеграция

Автоматизируйте screenshot тесты в CI/CD pipeline.

### Лучшие практики

1. Тестируйте критические UI компоненты
2. Тестируйте множество состояний
3. Используйте описательные имена
4. Держите тесты быстрыми (предпочитайте Paparazzi)

Screenshot тестирование предотвращает визуальные регрессии и поддерживает консистентность UI.

---

## Follow-ups

-   How do you handle screenshot test failures when UI changes are intentional vs regressions?
-   What's the best strategy for maintaining screenshot test baselines across different device configurations?
-   How can you integrate screenshot testing into your design system validation workflow?

## References

-   `https://github.com/cashapp/paparazzi` — Paparazzi library
-   `https://developer.android.com/training/testing/instrumented-tests` — Android testing guide
-   `https://developer.android.com/jetpack/compose/testing` — Compose testing

## Related Questions

### Related (Medium)

-   [[q-testing-viewmodels-turbine--android--medium]] - Testing
-   [[q-testing-compose-ui--android--medium]] - Testing
-   [[q-compose-testing--android--medium]] - Testing
-   [[q-robolectric-vs-instrumented--android--medium]] - Testing
-   [[q-fakes-vs-mocks-testing--android--medium]] - Testing

### Advanced (Harder)

-   [[q-testing-coroutines-flow--android--hard]] - Testing
