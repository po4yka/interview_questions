---
id: android-318
title: Screenshot and Snapshot Testing / Screenshot и Snapshot тестирование
aliases:
- Screenshot and Snapshot Testing
- Screenshot и Snapshot тестирование
topic: android
subtopics:
- testing-ui
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-testing
- q-testing-viewmodels-turbine--android--medium
- q-testing-compose-ui--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/testing-ui
- difficulty/medium
---

# Вопрос (RU)

> Реализуйте screenshot тестирование с помощью Paparazzi или Shot. Как обрабатывать разные размеры экранов и темы?

# Question (EN)

> Implement screenshot testing with Paparazzi or Shot. How do you handle different screen sizes and themes?

---

## Ответ (RU)

**Screenshot тестирование** (визуальное регрессионное тестирование) делает снимки UI и сравнивает их с базовыми эталонными изображениями, чтобы выявлять непреднамеренные визуальные изменения. Для Android популярны библиотеки **Paparazzi** и **Shot**.

---

### Paparazzi

**Paparazzi** рендерит UI (Compose и `View`) на JVM без эмулятора или реального устройства, что делает тесты быстрыми и удобными для CI.

Пример настройки (app-модуль):

```gradle
plugins {
    id("com.android.library") // или com.android.application
    id("org.jetbrains.kotlin.android")
    id("app.cash.paparazzi") version "1.3.1"
}

dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.1")
}
```

Базовый пример (Compose):

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

Запуск:

```bash
./gradlew recordPaparazziDebug   # записать эталоны
./gradlew verifyPaparazziDebug   # сравнить с эталонами
```

---

### Разные конфигурации устройств

С помощью `deviceConfig` проверяйте разные размеры экранов, плотность, ориентацию, масштаб шрифта и другие параметры конфигурации.

```kotlin
class ResponsiveScreenshotTest {

    @get:Rule
    val defaultPaparazzi = Paparazzi()

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

(В реальных проектах обычно используется один `@get:Rule` на класс или параметризованные тесты; отдельные инстансы `Paparazzi` в примерах нужны только для демонстрации разных конфигураций.)

---

### Тестирование тем

Используйте `uiMode` и тематизацию для проверки светлой и тёмной тем.

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

### Параметризованные screenshot-тесты

Можно итерироваться по наборам устройств и тем, чтобы покрыть все комбинации размеров и тем.

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

                paparazzi.snapshot("${device.name}_${themeName}") {
                    UserProfileScreen()
                }
            }
        }
    }
}
```

---

### Тестирование разных состояний

Покрывайте несколько состояний одного экрана, чтобы отлавливать визуальные проблемы в каждом.

```kotlin
class StateScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun loginScreen_states() {
        // Пустое состояние
        paparazzi.snapshot("empty") {
            LoginScreen(
                email = "",
                password = "",
                isLoading = false,
                error = null
            )
        }

        // Заполненное состояние
        paparazzi.snapshot("filled") {
            LoginScreen(
                email = "user@example.com",
                password = "password",
                isLoading = false,
                error = null
            )
        }

        // Загрузка
        paparazzi.snapshot("loading") {
            LoginScreen(
                email = "user@example.com",
                password = "password",
                isLoading = true,
                error = null
            )
        }

        // Ошибка
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

### Shot (инструментальные screenshot-тесты)

**Shot** запускает screenshot-тесты как инструментальные на эмуляторе/устройстве, давая рендеринг максимально близкий к реальному.

```gradle
// build.gradle.kts (app-модуль)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.karumi.shot") version "6.1.0"
}
```

Базовый пример (`Activity` / `View`):

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
```

Для Jetpack Compose Shot предоставляет вспомогательные API, обычно через хостинг `Composable` внутри `Activity`/`Fragment` и вызов `compareScreenshot` для этого хоста (конкретные API зависят от версии Shot, см. документацию).

Запуск Shot:

```bash
./gradlew executeScreenshotTests -Precord   # записать эталоны
./gradlew executeScreenshotTests            # сравнить с эталонами
```

---

### Shot с несколькими конфигурациями (концептуально)

Можно запускать одни и те же Shot-тесты на разных эмуляторах / устройствах (телефон, планшет, разные ориентации):

- Поднимаете эмулятор с нужным разрешением и плотностью.
- Управляете ориентацией в тестах (тесты на базе `Activity`).
- Запускаете `executeScreenshotTests` для каждой конфигурации при необходимости.

Конкретная реализация зависит от ваших test rules и инфраструктуры; избегайте обращения к несуществующим API.

---

### Paparazzi vs Shot (сравнение)

| Возможность             | Paparazzi               | Shot                      |
| ----------------------- | ----------------------- | ------------------------- |
| Скорость                | Быстро (JVM)            | Медленнее (устройство)    |
| Настройка               | Простая                 | Нужен эмулятор/устройство |
| CI                      | Не нужен эмулятор       | Требуется эмулятор        |
| Точность                | Симулируемый рендеринг  | Реальный рендеринг        |
| Compose                 | Поддерживается          | Поддерживается            |
| Views                   | Поддерживается          | Поддерживается            |
| Анимации                | Ограничены (статичные)  | Реальное выполнение       |
| Аппаратные особенности  | Без реального железа    | Реальное железо           |

---

### Реалистичный пример полного набора тестов

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
        // Телефон - светлая тема
        TestConfig(
            device = DeviceConfig.PIXEL_5,
            theme = lightColorScheme(),
            themeName = "light"
        ),
        // Телефон - тёмная тема
        TestConfig(
            device = DeviceConfig.PIXEL_5,
            theme = darkColorScheme(),
            themeName = "dark"
        ),
        // Планшет - светлая тема
        TestConfig(
            device = DeviceConfig.PIXEL_C,
            theme = lightColorScheme(),
            themeName = "light"
        ),
        // Крупный шрифт
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

            // Loading
            paparazzi.snapshot("${testName}_loading") {
                MaterialTheme(colorScheme = config.theme) {
                    Surface {
                        UserProfileScreen(
                            uiState = UiState.Loading
                        )
                    }
                }
            }

            // Success
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

            // Error
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

### Обработка нестабильных скриншотов

- Анимации: отключайте или делайте детерминированными.
- Время/рандом: фиксируйте timestamp и случайные значения.
- Данные: используйте стабильные тестовые данные.

```kotlin
// Плохой пример: анимация
@Test
fun animatedButton() {
    paparazzi.snapshot {
        AnimatedButton()
    }
}

// Хороший пример: анимации отключены
@Test
fun animatedButton_static() {
    paparazzi.snapshot {
        CompositionLocalProvider(
            LocalAnimationsEnabled provides false
        ) {
            AnimatedButton()
        }
    }
}
```

```kotlin
// Плохой пример: плавающее время
@Test
fun messageView() {
    paparazzi.snapshot {
        MessageView(
            text = "Hello",
            timestamp = System.currentTimeMillis()
        )
    }
}

// Хороший пример: фиксированное время
@Test
fun messageView_deterministic() {
    paparazzi.snapshot {
        MessageView(
            text = "Hello",
            timestamp = 1234567890000L
        )
    }
}
```

---

### CI интеграция

Пример интеграции Paparazzi в GitHub Actions (без эмулятора):

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

Shot в CI потребует настроенного эмулятора или устройства и запуска `executeScreenshotTests` в соответствующей job.

---

### Лучшие практики (RU)

1. Тестируйте критичные, переиспользуемые UI-компоненты, а не только целые экраны.
2. Покрывайте несколько состояний (загрузка, успех, ошибка, пустое состояние, крайние случаи).
3. Используйте понятные имена снапшотов, включающие устройство, тему, ориентацию и состояние.
4. Держите тесты быстрыми: используйте Paparazzi для основной части покрытия, а Shot — когда нужна точность реального устройства.
5. Стабилизируйте входные данные (без случайных значений, текущего времени и неконтролируемых анимаций).

---

## Answer (EN)

**Screenshot testing** (visual regression testing) captures UI renders and compares them against baseline images to detect unintended visual changes. **Paparazzi** and **Shot** are popular libraries for Android.

---

### Paparazzi

**Paparazzi** renders Compose/`View`-based UIs on the JVM without requiring an emulator or device.

```gradle
// build.gradle.kts (app module)
plugins {
    id("com.android.library") // or com.android.application
    id("org.jetbrains.kotlin.android")
    id("app.cash.paparazzi") version "1.3.1"
}

dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.1")
}
```

**Basic usage (Compose):**

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

Use `deviceConfig` to test multiple screen sizes and characteristics.

```kotlin
class ResponsiveScreenshotTest {

    @get:Rule
    val defaultPaparazzi = Paparazzi()

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

(For production code, prefer a single `@get:Rule` per class or parameterized tests; instantiating `Paparazzi` inside each test is shown here only to illustrate different configs.)

---

### Testing Themes

Use `uiMode` and theme composition to validate light/dark themes.

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

Iterate over devices and themes to ensure coverage of screen sizes and themes.

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

                paparazzi.snapshot("${device.name}_${themeName}") {
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

**Shot** uses instrumented tests (running on an emulator or device) for screenshot comparison.

```gradle
// build.gradle.kts (app module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.karumi.shot") version "6.1.0"
}
```

**Basic usage (`Activity` / `View`):**

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
```

For Jetpack Compose, Shot provides helpers to capture Composables. A typical pattern is to host the Composable in an `Activity`/`Fragment` and use `compareScreenshot` on that host, or the dedicated Shot Compose APIs. The exact call signature may vary by Shot version, so always check the Shot documentation.

**Running Shot:**

```bash
# Record baseline
./gradlew executeScreenshotTests -Precord

# Verify screenshots
./gradlew executeScreenshotTests
```

---

### Shot with Multiple Configurations (Conceptual)

You can run Shot tests on different emulators / devices (e.g., phone vs tablet, different orientations) by configuring your instrumented test environment:

- Start emulator with required resolution / density.
- Set orientation in the test (for `Activity`-based tests).
- Run `executeScreenshotTests` per configuration if needed.

(Concrete API usage depends on your test rule / host setup; avoid relying on non-existent properties.)

---

### Paparazzi Vs Shot Comparison

| Feature        | Paparazzi           | Shot                  |
| -------------- | ------------------- | --------------------- |
| Speed          | Fast (JVM)          | Slower (device)       |
| Setup          | Simple              | Needs device/emulator |
| CI             | No emulator needed  | Requires emulator     |
| Accuracy       | Simulated rendering | Real device rendering |
| Compose        | Supported           | Supported             |
| Views          | Supported           | Supported             |
| Animations     | Limited (static)    | Real runtime          |
| Hardware       | No real hardware    | Real hardware         |

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

- Disable or control animations.
- Fix timestamps and random data.
- Use stable test data.

```kotlin
// BAD: Animations cause different screenshots
@Test
fun animatedButton() {
    paparazzi.snapshot {
        AnimatedButton()
    }
}

// GOOD: Disable or control animations explicitly
@Test
fun animatedButton_static() {
    paparazzi.snapshot {
        CompositionLocalProvider(
            LocalAnimationsEnabled provides false
        ) {
            AnimatedButton()
        }
    }
}
```

```kotlin
// BAD: Timestamp changes every time
@Test
fun messageView() {
    paparazzi.snapshot {
        MessageView(
            text = "Hello",
            timestamp = System.currentTimeMillis()
        )
    }
}

// GOOD: Fixed timestamp
@Test
fun messageView_deterministic() {
    paparazzi.snapshot {
        MessageView(
            text = "Hello",
            timestamp = 1234567890000L
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

1. Test critical, reusable UI components rather than only whole screens.
2. Cover multiple states (loading, success, error, empty, edge cases).
3. Use descriptive snapshot names including device, theme, orientation, and state.
4. Keep tests fast: use Paparazzi for most coverage; use Shot when you need real-device fidelity.
5. Stabilize inputs (no random data, timestamps, or uncontrolled animations).

---

## Дополнительные вопросы (RU)

- Как вы обрабатываете падения screenshot-тестов, когда изменения в UI намеренные, а когда это регрессия?
- Какую стратегию вы используете для поддержки эталонных скриншотов для разных конфигураций устройств?
- Как можно интегрировать screenshot-тестирование в проверку/design system вашего приложения?

## Follow-ups

- How do you handle screenshot test failures when UI changes are intentional vs regressions?
- What's the best strategy for maintaining screenshot test baselines across different device configurations?
- How can you integrate screenshot testing into your design system validation workflow?

## Ссылки (RU)

- https://github.com/cashapp/paparazzi — библиотека Paparazzi
- https://developer.android.com/training/testing/instrumented-tests — руководство по инструментальным тестам Android
- https://developer.android.com/jetpack/compose/testing — руководство по тестированию Compose

## References

- https://github.com/cashapp/paparazzi — Paparazzi library
- https://developer.android.com/training/testing/instrumented-tests — Android testing guide
- https://developer.android.com/jetpack/compose/testing — Compose testing

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-testing]]

### Связанные (Medium)

- [[q-testing-viewmodels-turbine--android--medium]] - Тестирование
- [[q-testing-compose-ui--android--medium]] - Тестирование

## Related Questions

### Prerequisites / Concepts

- [[c-testing]]

### Related (Medium)

- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--android--medium]] - Testing
- [[q-fakes-vs-mocks-testing--android--medium]] - Testing

### Advanced (Harder)

- [[q-testing-coroutines-flow--android--hard]] - Testing
