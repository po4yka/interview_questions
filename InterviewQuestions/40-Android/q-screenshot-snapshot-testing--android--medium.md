---
id: android-318
title: Screenshot and Snapshot Testing / Screenshot и Snapshot тестирование
aliases:
- Screenshot and Snapshot Testing
- Screenshot и Snapshot тестирование
topic: android
subtopics:
- testing-screenshot
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-testing
- q-testing-viewmodels-turbine--android--medium
- q-testing-compose-ui--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/testing-screenshot
- difficulty/medium

---

# Вопрос (RU)

> Реализуйте screenshot тестирование с помощью Paparazzi или Shot. Как обрабатывать разные размеры экранов и темы?

# Question (EN)

> Implement screenshot testing with Paparazzi or Shot. How do you handle different screen sizes and themes?

---

## Ответ (RU)

**Screenshot тестирование** (визуальное регрессионное тестирование) делает снимки UI и сравнивает их с базовыми эталонными изображениями, чтобы выявлять непреднамеренные визуальные изменения. Для Android популярны библиотеки **Paparazzi** и **Shot**.

(Версии артефактов в примерах условны; в реальном проекте нужно использовать актуальные версии из документации.)

---

### Paparazzi

**Paparazzi** рендерит UI (Compose и `View`) на JVM без эмулятора или реального устройства, что делает тесты быстрыми и удобными для CI.

Пример настройки (app-модуль):

```gradle
plugins {
    id("com.android.library") // или com.android.application
    id("org.jetbrains.kotlin.android")
    id("app.cash.paparazzi") version "1.3.1" // пример; используйте актуальную версию
}

dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.1") // пример; используйте актуальную версию
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
    val paparazzi = Paparazzi()

    @Test
    fun userProfile_phone() {
        paparazzi.unsafeUpdateConfig(deviceConfig = DeviceConfig.PIXEL_5)

        paparazzi.snapshot("userProfile_phone") {
            UserProfileScreen()
        }
    }

    @Test
    fun userProfile_tablet() {
        paparazzi.unsafeUpdateConfig(deviceConfig = DeviceConfig.PIXEL_C)

        paparazzi.snapshot("userProfile_tablet") {
            UserProfileScreen()
        }
    }

    @Test
    fun userProfile_customSize() {
        val customConfig = DeviceConfig.PIXEL_5.copy(
            // Параметры приведены как концептуальный пример,
            // используйте фактические поля DeviceConfig из текущей версии Paparazzi
            screenHeight = 1920,
            screenWidth = 1080,
            xdpi = 420f,
            ydpi = 420f,
            orientation = ScreenOrientation.PORTRAIT,
            uiMode = Configuration.UI_MODE_NIGHT_NO,
            fontScale = 1f
        )

        paparazzi.unsafeUpdateConfig(deviceConfig = customConfig)

        paparazzi.snapshot("userProfile_custom_device") {
            UserProfileScreen()
        }
    }
}
```

(В реальных проектах обычно используется один `@get:Rule` на класс и фиксированный или параметризуемый `DeviceConfig`. Конфигурации и поля выше показаны концептуально — следует сверяться с актуальным API Paparazzi.)

---

### Тестирование тем

Используйте `uiMode` и тематизацию для проверки светлой и тёмной тем.

```kotlin
class ThemeScreenshotTest {

    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_5
    )

    @Test
    fun button_lightTheme() {
        paparazzi.unsafeUpdateConfig(
            deviceConfig = paparazzi.deviceConfig.copy(
                uiMode = Configuration.UI_MODE_NIGHT_NO
            )
        )

        paparazzi.snapshot("button_light") {
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
        paparazzi.unsafeUpdateConfig(
            deviceConfig = paparazzi.deviceConfig.copy(
                uiMode = Configuration.UI_MODE_NIGHT_YES
            )
        )

        paparazzi.snapshot("button_dark") {
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

(Названия полей `uiMode` и способы смены конфигурации зависят от версии Paparazzi; концепция остаётся той же.)

---

### Параметризованные screenshot-тесты

Можно итерироваться по наборам устройств и тем, чтобы покрыть все комбинации размеров и тем. Ниже пример, концептуально демонстрирующий идею (конкретные поля `DeviceConfig` следует брать из текущего API):

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

                val testName = "${device}_${themeName}" // концептуальное имя

                paparazzi.snapshot(testName) {
                    UserProfileScreen()
                }
            }
        }
    }
}
```

(В реальных проектах лучше использовать JUnit параметризованные тесты и один `Paparazzi` rule, чем создавать инстансы внутри цикла.)

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
    id("com.karumi.shot") version "6.1.0" // пример; используйте актуальную версию
}
```

Для корректной работы Shot обычно используются:

- плагин `com.karumi.shot` в Gradle;
- базовый тестовый класс или JUnit Rule/extension, предоставляемый Shot, который инициализирует библиотеку.

Базовый пример (`Activity` / `View`), схематично:

```kotlin
@RunWith(AndroidJUnit4::class)
class MainActivityScreenshotTest : ShotTest { // интерфейс/базовый класс зависит от версии Shot

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun mainActivity_screenshot() {
        // Конкретный API (ShotTest, compareScreenshot и т.п.) зависит от версии Shot.
        // Здесь показана концепция: передать activity/вью в compareScreenshot.
        compareScreenshot(activityRule.scenario)
    }
}
```

Для Jetpack Compose Shot также предоставляет вспомогательные API для снятия скриншотов `Composable`-ов. Конкретные сигнатуры и базовые классы регулярно обновляются, поэтому всегда нужно сверяться с официальной документацией Shot.

Запуск Shot:

```bash
./gradlew executeScreenshotTests -Precord   # записать эталоны (baseline)
./gradlew executeScreenshotTests            # сравнить с эталонами
```

---

### Shot с несколькими конфигурациями (концептуально)

Можно запускать одни и те же Shot-тесты на разных эмуляторах / устройствах (телефон, планшет, разные ориентации):

- Поднимаете эмулятор с нужным разрешением и плотностью.
- Управляете ориентацией в тестах (тесты на базе `Activity`).
- Запускаете `executeScreenshotTests` для каждой конфигурации при необходимости.

Конкретная реализация зависит от используемой версии Shot, ваших test rules и инфраструктуры CI; не полагайтесь на несуществующие API.

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

Ниже пример, иллюстрирующий стратегию покрытия разных конфигураций. Конфигурации и сигнатуры Paparazzi/DeviceConfig могут отличаться в зависимости от версии, поэтому рассматривайте это как шаблон.

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

            val testName = "${config.device}_${config.themeName}" // имя снапшота, построенное из конфигурации

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

// Хороший пример: анимации отключены (концептуально)
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

(В примерах с анимациями и временем используются условные API; важно донести идею стабилизации входных данных.)

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

Screenshot testing (visual regression testing) captures UI renders and compares them against baseline images to detect unintended visual changes. Paparazzi and Shot are popular libraries for Android.

(Versions used in snippets are examples; in real projects always use the latest versions from official docs.)

---

### Paparazzi

Paparazzi renders Compose/`View`-based UIs on the JVM without requiring an emulator or device.

```gradle
// build.gradle.kts (app module)
plugins {
    id("com.android.library") // or com.android.application
    id("org.jetbrains.kotlin.android")
    id("app.cash.paparazzi") version "1.3.1" // example; use the latest version
}

dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.1") // example; use the latest version
}
```

Basic usage (Compose):

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

Running tests:

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
    val paparazzi = Paparazzi()

    @Test
    fun userProfile_phone() {
        paparazzi.unsafeUpdateConfig(deviceConfig = DeviceConfig.PIXEL_5)

        paparazzi.snapshot("userProfile_phone") {
            UserProfileScreen()
        }
    }

    @Test
    fun userProfile_tablet() {
        paparazzi.unsafeUpdateConfig(deviceConfig = DeviceConfig.PIXEL_C)

        paparazzi.snapshot("userProfile_tablet") {
            UserProfileScreen()
        }
    }

    @Test
    fun userProfile_customSize() {
        val customConfig = DeviceConfig.PIXEL_5.copy(
            // These fields are illustrative; use the actual fields from your Paparazzi version
            screenHeight = 1920,
            screenWidth = 1080,
            xdpi = 420f,
            ydpi = 420f,
            orientation = ScreenOrientation.PORTRAIT,
            uiMode = Configuration.UI_MODE_NIGHT_NO,
            fontScale = 1f
        )

        paparazzi.unsafeUpdateConfig(deviceConfig = customConfig)

        paparazzi.snapshot("userProfile_custom_device") {
            UserProfileScreen()
        }
    }
}
```

(In production, prefer a single `@get:Rule` per class and parameterized tests or predefined `DeviceConfig`s. The configs and fields above are conceptual—always check the current Paparazzi API.)

---

### Testing Themes

Use `uiMode` and theme composition to validate light/dark themes.

```kotlin
class ThemeScreenshotTest {

    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_5
    )

    @Test
    fun button_lightTheme() {
        paparazzi.unsafeUpdateConfig(
            deviceConfig = paparazzi.deviceConfig.copy(
                uiMode = Configuration.UI_MODE_NIGHT_NO
            )
        )

        paparazzi.snapshot("button_light") {
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
        paparazzi.unsafeUpdateConfig(
            deviceConfig = paparazzi.deviceConfig.copy(
                uiMode = Configuration.UI_MODE_NIGHT_YES
            )
        )

        paparazzi.snapshot("button_dark") {
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

(The exact way to update `uiMode` depends on the Paparazzi version; conceptually, you parameterize device configuration.)

---

### Parameterized Screenshot Tests

Iterate over devices and themes to ensure coverage of screen sizes and themes. The snippet below is conceptual; adjust to your Paparazzi API and testing style.

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

                val testName = "${device}_${themeName}"

                paparazzi.snapshot(testName) {
                    UserProfileScreen()
                }
            }
        }
    }
}
```

(For real-world use prefer JUnit parameterized tests and a single rule.)

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

Shot uses instrumented tests (running on an emulator or device) for screenshot comparison.

```gradle
// build.gradle.kts (app module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.karumi.shot") version "6.1.0" // example; use the latest version
}
```

For correct integration, Shot typically relies on:

- the `com.karumi.shot` Gradle plugin;
- a base test class or JUnit Rule/extension provided by Shot to initialize the library.

Basic usage (`Activity` / `View`), schematically:

```kotlin
@RunWith(AndroidJUnit4::class)
class MainActivityScreenshotTest : ShotTest { // actual base type depends on Shot version

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun mainActivity_screenshot() {
        // The exact compareScreenshot overload depends on the Shot version.
        compareScreenshot(activityRule.scenario)
    }
}
```

For Jetpack Compose, Shot exposes helpers to capture Composables (for example by hosting the Composable in an Activity/Fragment and invoking `compareScreenshot`). Always refer to the Shot documentation for the current, correct APIs.

Running Shot:

```bash
# Record baseline
./gradlew executeScreenshotTests -Precord

# Verify screenshots
./gradlew executeScreenshotTests
```

---

### Shot with Multiple Configurations (Conceptual)

You can run Shot tests on different emulators/devices (phone vs tablet, different orientations) by configuring your instrumented test environment:

- Start emulator with desired resolution/density.
- Control orientation in your tests (for Activity-based tests).
- Run `executeScreenshotTests` for each configuration as needed.

Concrete API usage depends on your Shot version, test rules, and CI setup; avoid relying on undocumented APIs.

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

The following example illustrates a coverage strategy; adjust the types and configuration to your Paparazzi version.

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

            val testName = "${config.device}_${config.themeName}"

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
- Use stable, deterministic test data.

```kotlin
// BAD: Animations cause different screenshots
@Test
fun animatedButton() {
    paparazzi.snapshot {
        AnimatedButton()
    }
}

// GOOD: Disable or control animations explicitly (conceptual)
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

(The above uses hypothetical APIs for controlling animations; the key idea is to make screenshots reproducible.)

---

### CI Integration

GitHub Actions with Paparazzi:

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

Shot in CI requires a configured emulator or device and running `executeScreenshotTests` in the appropriate job.

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

- [[c-android-testing]]

### Связанные (Medium)

- [[q-testing-viewmodels-turbine--android--medium]] - Тестирование
- [[q-testing-compose-ui--android--medium]] - Тестирование

## Related Questions

### Prerequisites / Concepts

- [[c-android-testing]]

### Related (Medium)

- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
