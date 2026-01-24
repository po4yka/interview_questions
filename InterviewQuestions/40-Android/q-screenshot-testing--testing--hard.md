---
id: android-405
title: "Screenshot Testing / Скриншот-тестирование"
aliases: ["Screenshot Testing", "Скриншот-тестирование"]
topic: android
subtopics: [testing-ui, testing]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-testing, q-testing-compose-ui--android--medium, q-compose-testing-semantics--testing--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/testing-ui, difficulty/hard, screenshot-testing, paparazzi, shot, compose, visual-regression]

---
# Vopros (RU)

> Какие подходы существуют для скриншот-тестирования в Android? Сравните Paparazzi и Shot.

# Question (EN)

> What approaches exist for screenshot testing in Android? Compare Paparazzi and Shot.

---

## Otvet (RU)

**Скриншот-тестирование** (Visual Regression Testing) - это способ обнаружения непреднамеренных визуальных изменений UI путем сравнения текущих скриншотов с эталонными (golden) изображениями.

### Краткий Ответ

| Аспект | Paparazzi | Shot |
|--------|-----------|------|
| Эмулятор | Не нужен (JVM) | Нужен |
| Скорость | Быстро | Медленно |
| Compose | Полная поддержка | Поддержка |
| Views | Ограниченно | Полная |
| CI | Просто | Сложнее |

### Подробный Ответ

### Paparazzi (Cash App)

Paparazzi рендерит UI на JVM без эмулятора, используя LayoutLib от Android Studio.

**Настройка:**

```kotlin
// build.gradle.kts (project)
plugins {
    id("app.cash.paparazzi") version "1.3.2" apply false
}

// build.gradle.kts (module)
plugins {
    id("app.cash.paparazzi")
}

dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.2")
}
```

**Базовое использование с Compose:**

```kotlin
class LoginScreenScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_6,
        theme = "android:Theme.Material3.Light.NoActionBar",
        renderingMode = SessionParams.RenderingMode.NORMAL
    )

    @Test
    fun loginScreen_default() {
        paparazzi.snapshot {
            LoginScreen(
                email = "",
                password = "",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = false
            )
        }
    }

    @Test
    fun loginScreen_loading() {
        paparazzi.snapshot {
            LoginScreen(
                email = "test@example.com",
                password = "password",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = true
            )
        }
    }

    @Test
    fun loginScreen_error() {
        paparazzi.snapshot {
            LoginScreen(
                email = "invalid",
                password = "",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = false,
                errorMessage = "Invalid email format"
            )
        }
    }
}
```

**Конфигурация устройств:**

```kotlin
class MultiDeviceScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun component_phone() {
        paparazzi.unsafeUpdateConfig(
            deviceConfig = DeviceConfig.PIXEL_6
        )
        paparazzi.snapshot { MyComponent() }
    }

    @Test
    fun component_tablet() {
        paparazzi.unsafeUpdateConfig(
            deviceConfig = DeviceConfig.NEXUS_10
        )
        paparazzi.snapshot { MyComponent() }
    }

    @Test
    fun component_foldable() {
        paparazzi.unsafeUpdateConfig(
            deviceConfig = DeviceConfig.PIXEL_FOLD
        )
        paparazzi.snapshot { MyComponent() }
    }
}
```

**Тестирование тем:**

```kotlin
class ThemeScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun component_lightTheme() {
        paparazzi.unsafeUpdateConfig(
            theme = "android:Theme.Material3.Light.NoActionBar"
        )
        paparazzi.snapshot {
            MaterialTheme(colorScheme = lightColorScheme()) {
                MyComponent()
            }
        }
    }

    @Test
    fun component_darkTheme() {
        paparazzi.unsafeUpdateConfig(
            theme = "android:Theme.Material3.Dark.NoActionBar"
        )
        paparazzi.snapshot {
            MaterialTheme(colorScheme = darkColorScheme()) {
                MyComponent()
            }
        }
    }
}
```

**Команды Gradle:**

```bash
# Записать эталонные скриншоты
./gradlew :app:recordPaparazziDebug

# Проверить скриншоты против эталонов
./gradlew :app:verifyPaparazziDebug

# Удалить все скриншоты
./gradlew :app:deletePaparazziSnapshots
```

### Shot (Karumi)

Shot использует реальный эмулятор для создания скриншотов.

**Настройка:**

```kotlin
// build.gradle.kts (project)
plugins {
    id("com.karumi.shot") version "6.1.0" apply false
}

// build.gradle.kts (module)
plugins {
    id("com.karumi.shot")
}

shot {
    applicationId = "com.example.app"
    tolerance = 0.1 // 0.1% допустимая разница
}
```

**Использование с Compose:**

```kotlin
class LoginScreenShotTest : ScreenshotTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_default() {
        composeTestRule.setContent {
            LoginScreen(
                email = "",
                password = "",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = false
            )
        }

        compareScreenshot(composeTestRule)
    }

    @Test
    fun loginScreen_withData() {
        composeTestRule.setContent {
            LoginScreen(
                email = "test@example.com",
                password = "password",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = false
            )
        }

        compareScreenshot(composeTestRule)
    }
}
```

**Использование с Views:**

```kotlin
class ViewScreenshotTest : ScreenshotTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun mainActivity_screenshot() {
        activityRule.scenario.onActivity { activity ->
            compareScreenshot(activity)
        }
    }

    @Test
    fun specificView_screenshot() {
        activityRule.scenario.onActivity { activity ->
            val view = activity.findViewById<View>(R.id.my_view)
            compareScreenshot(view)
        }
    }
}
```

**Команды Gradle:**

```bash
# Записать эталоны (нужен подключенный эмулятор)
./gradlew :app:executeScreenshotTests -Precord

# Проверить скриншоты
./gradlew :app:executeScreenshotTests

# С конкретным устройством
./gradlew :app:executeScreenshotTests -Pandroid.testInstrumentationRunnerArguments.device=Pixel_6
```

### Сравнение Paparazzi vs Shot

**Paparazzi - Преимущества:**

```kotlin
// 1. Не нужен эмулятор - быстрее CI
// 2. Работает как unit-тест
// 3. Детерминированный рендеринг
// 4. Отличная поддержка Compose

class FastScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun quickTest() {
        // Выполняется за миллисекунды
        paparazzi.snapshot { MyComponent() }
    }
}
```

**Paparazzi - Ограничения:**

```kotlin
// 1. Не поддерживает некоторые Android APIs
// 2. Ограниченная поддержка анимаций
// 3. Может отличаться от реального рендеринга

// Workaround для View-based компонентов
class ViewPaparazziTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun viewTest() {
        // Работает, но с ограничениями
        val view = paparazzi.inflate<LinearLayout>(R.layout.my_layout)
        paparazzi.snapshot(view)
    }
}
```

**Shot - Преимущества:**

```kotlin
// 1. Реальный рендеринг на устройстве
// 2. Полная поддержка всех Android APIs
// 3. Тестирует как пользователь видит
// 4. Хорошо для View-based UI

class AccurateScreenshotTest : ScreenshotTest {
    @Test
    fun realDeviceRendering() {
        // Точно как на устройстве
        compareScreenshot(activity)
    }
}
```

**Shot - Ограничения:**

```kotlin
// 1. Требует эмулятор/устройство
// 2. Медленнее
// 3. Зависит от версии Android
// 4. Сложнее настроить CI
```

### Roborazzi (Alternative)

Roborazzi работает с Robolectric - компромисс между Paparazzi и Shot.

```kotlin
// build.gradle.kts
plugins {
    id("io.github.takahirom.roborazzi") version "1.8.0"
}

dependencies {
    testImplementation("io.github.takahirom.roborazzi:roborazzi:1.8.0")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-compose:1.8.0")
}
```

```kotlin
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class RoborazziTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun myComponent_screenshot() {
        composeTestRule.setContent {
            MyComponent()
        }

        composeTestRule.onRoot().captureRoboImage()
    }
}
```

### Best Practices

```kotlin
// 1. Изолируйте компоненты для тестирования
@Composable
fun PreviewableComponent(
    state: ComponentState = ComponentState.Default
) {
    // Компонент без внешних зависимостей
}

// 2. Тестируйте различные состояния
class ComponentStatesTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun component_default() {
        paparazzi.snapshot { PreviewableComponent(ComponentState.Default) }
    }

    @Test
    fun component_loading() {
        paparazzi.snapshot { PreviewableComponent(ComponentState.Loading) }
    }

    @Test
    fun component_error() {
        paparazzi.snapshot { PreviewableComponent(ComponentState.Error("Error")) }
    }

    @Test
    fun component_success() {
        paparazzi.snapshot { PreviewableComponent(ComponentState.Success(data)) }
    }
}

// 3. Используйте фиксированные данные
val testUser = User(
    id = "test-id",
    name = "John Doe",
    avatar = "https://example.com/avatar.png"
)

// 4. Организуйте скриншоты по фичам
// src/test/snapshots/images/
//   login/
//     loginScreen_default.png
//     loginScreen_loading.png
//   profile/
//     profileScreen_default.png

// 5. Настройте tolerance для CI
shot {
    tolerance = 0.1 // Допускается 0.1% различий
}
```

### CI/CD Интеграция

```yaml
# GitHub Actions для Paparazzi
name: Screenshot Tests

on: [pull_request]

jobs:
  screenshot-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Verify Screenshots
        run: ./gradlew verifyPaparazziDebug

      - name: Upload failed screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: failed-screenshots
          path: '**/build/paparazzi/failures/'
```

---

## Answer (EN)

**Screenshot testing** (Visual Regression Testing) is a way to detect unintended visual changes in UI by comparing current screenshots with golden (reference) images.

### Short Version

| Aspect | Paparazzi | Shot |
|--------|-----------|------|
| Emulator | Not needed (JVM) | Required |
| Speed | Fast | Slow |
| Compose | Full support | Supported |
| Views | Limited | Full |
| CI | Simple | Complex |

### Detailed Version

### Paparazzi (Cash App)

Paparazzi renders UI on JVM without an emulator using LayoutLib from Android Studio.

**Setup:**

```kotlin
// build.gradle.kts (project)
plugins {
    id("app.cash.paparazzi") version "1.3.2" apply false
}

// build.gradle.kts (module)
plugins {
    id("app.cash.paparazzi")
}

dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.2")
}
```

**Basic usage with Compose:**

```kotlin
class LoginScreenScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_6,
        theme = "android:Theme.Material3.Light.NoActionBar",
        renderingMode = SessionParams.RenderingMode.NORMAL
    )

    @Test
    fun loginScreen_default() {
        paparazzi.snapshot {
            LoginScreen(
                email = "",
                password = "",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = false
            )
        }
    }

    @Test
    fun loginScreen_loading() {
        paparazzi.snapshot {
            LoginScreen(
                email = "test@example.com",
                password = "password",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = true
            )
        }
    }

    @Test
    fun loginScreen_error() {
        paparazzi.snapshot {
            LoginScreen(
                email = "invalid",
                password = "",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = false,
                errorMessage = "Invalid email format"
            )
        }
    }
}
```

**Device configuration:**

```kotlin
class MultiDeviceScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun component_phone() {
        paparazzi.unsafeUpdateConfig(
            deviceConfig = DeviceConfig.PIXEL_6
        )
        paparazzi.snapshot { MyComponent() }
    }

    @Test
    fun component_tablet() {
        paparazzi.unsafeUpdateConfig(
            deviceConfig = DeviceConfig.NEXUS_10
        )
        paparazzi.snapshot { MyComponent() }
    }

    @Test
    fun component_foldable() {
        paparazzi.unsafeUpdateConfig(
            deviceConfig = DeviceConfig.PIXEL_FOLD
        )
        paparazzi.snapshot { MyComponent() }
    }
}
```

**Theme testing:**

```kotlin
class ThemeScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun component_lightTheme() {
        paparazzi.unsafeUpdateConfig(
            theme = "android:Theme.Material3.Light.NoActionBar"
        )
        paparazzi.snapshot {
            MaterialTheme(colorScheme = lightColorScheme()) {
                MyComponent()
            }
        }
    }

    @Test
    fun component_darkTheme() {
        paparazzi.unsafeUpdateConfig(
            theme = "android:Theme.Material3.Dark.NoActionBar"
        )
        paparazzi.snapshot {
            MaterialTheme(colorScheme = darkColorScheme()) {
                MyComponent()
            }
        }
    }
}
```

**Gradle commands:**

```bash
# Record golden screenshots
./gradlew :app:recordPaparazziDebug

# Verify screenshots against golden
./gradlew :app:verifyPaparazziDebug

# Delete all snapshots
./gradlew :app:deletePaparazziSnapshots
```

### Shot (Karumi)

Shot uses a real emulator to create screenshots.

**Setup:**

```kotlin
// build.gradle.kts (project)
plugins {
    id("com.karumi.shot") version "6.1.0" apply false
}

// build.gradle.kts (module)
plugins {
    id("com.karumi.shot")
}

shot {
    applicationId = "com.example.app"
    tolerance = 0.1 // 0.1% allowed difference
}
```

**Usage with Compose:**

```kotlin
class LoginScreenShotTest : ScreenshotTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_default() {
        composeTestRule.setContent {
            LoginScreen(
                email = "",
                password = "",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = false
            )
        }

        compareScreenshot(composeTestRule)
    }

    @Test
    fun loginScreen_withData() {
        composeTestRule.setContent {
            LoginScreen(
                email = "test@example.com",
                password = "password",
                onEmailChange = {},
                onPasswordChange = {},
                onLogin = {},
                isLoading = false
            )
        }

        compareScreenshot(composeTestRule)
    }
}
```

**Usage with Views:**

```kotlin
class ViewScreenshotTest : ScreenshotTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun mainActivity_screenshot() {
        activityRule.scenario.onActivity { activity ->
            compareScreenshot(activity)
        }
    }

    @Test
    fun specificView_screenshot() {
        activityRule.scenario.onActivity { activity ->
            val view = activity.findViewById<View>(R.id.my_view)
            compareScreenshot(view)
        }
    }
}
```

**Gradle commands:**

```bash
# Record golden (needs connected emulator)
./gradlew :app:executeScreenshotTests -Precord

# Verify screenshots
./gradlew :app:executeScreenshotTests

# With specific device
./gradlew :app:executeScreenshotTests -Pandroid.testInstrumentationRunnerArguments.device=Pixel_6
```

### Paparazzi vs Shot Comparison

**Paparazzi - Advantages:**

```kotlin
// 1. No emulator needed - faster CI
// 2. Runs as unit test
// 3. Deterministic rendering
// 4. Excellent Compose support

class FastScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun quickTest() {
        // Executes in milliseconds
        paparazzi.snapshot { MyComponent() }
    }
}
```

**Paparazzi - Limitations:**

```kotlin
// 1. Doesn't support some Android APIs
// 2. Limited animation support
// 3. May differ from real rendering

// Workaround for View-based components
class ViewPaparazziTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun viewTest() {
        // Works but with limitations
        val view = paparazzi.inflate<LinearLayout>(R.layout.my_layout)
        paparazzi.snapshot(view)
    }
}
```

**Shot - Advantages:**

```kotlin
// 1. Real device rendering
// 2. Full support for all Android APIs
// 3. Tests exactly what user sees
// 4. Good for View-based UI

class AccurateScreenshotTest : ScreenshotTest {
    @Test
    fun realDeviceRendering() {
        // Exactly as on device
        compareScreenshot(activity)
    }
}
```

**Shot - Limitations:**

```kotlin
// 1. Requires emulator/device
// 2. Slower
// 3. Depends on Android version
// 4. More complex CI setup
```

### Roborazzi (Alternative)

Roborazzi works with Robolectric - a compromise between Paparazzi and Shot.

```kotlin
// build.gradle.kts
plugins {
    id("io.github.takahirom.roborazzi") version "1.8.0"
}

dependencies {
    testImplementation("io.github.takahirom.roborazzi:roborazzi:1.8.0")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-compose:1.8.0")
}
```

```kotlin
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class RoborazziTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun myComponent_screenshot() {
        composeTestRule.setContent {
            MyComponent()
        }

        composeTestRule.onRoot().captureRoboImage()
    }
}
```

### Best Practices

```kotlin
// 1. Isolate components for testing
@Composable
fun PreviewableComponent(
    state: ComponentState = ComponentState.Default
) {
    // Component without external dependencies
}

// 2. Test various states
class ComponentStatesTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun component_default() {
        paparazzi.snapshot { PreviewableComponent(ComponentState.Default) }
    }

    @Test
    fun component_loading() {
        paparazzi.snapshot { PreviewableComponent(ComponentState.Loading) }
    }

    @Test
    fun component_error() {
        paparazzi.snapshot { PreviewableComponent(ComponentState.Error("Error")) }
    }

    @Test
    fun component_success() {
        paparazzi.snapshot { PreviewableComponent(ComponentState.Success(data)) }
    }
}

// 3. Use fixed test data
val testUser = User(
    id = "test-id",
    name = "John Doe",
    avatar = "https://example.com/avatar.png"
)

// 4. Organize screenshots by feature
// src/test/snapshots/images/
//   login/
//     loginScreen_default.png
//     loginScreen_loading.png
//   profile/
//     profileScreen_default.png

// 5. Configure tolerance for CI
shot {
    tolerance = 0.1 // Allow 0.1% difference
}
```

### CI/CD Integration

```yaml
# GitHub Actions for Paparazzi
name: Screenshot Tests

on: [pull_request]

jobs:
  screenshot-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Verify Screenshots
        run: ./gradlew verifyPaparazziDebug

      - name: Upload failed screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: failed-screenshots
          path: '**/build/paparazzi/failures/'
```

---

## Follow-ups

- How do you handle dynamic content like timestamps in screenshots?
- How do you organize screenshot tests for a large design system?
- What's the best approach for testing responsive layouts?

## References

- https://github.com/cashapp/paparazzi
- https://github.com/pedrovgs/Shot
- https://github.com/takahirom/roborazzi
- https://developer.android.com/jetpack/compose/testing

## Related Questions

### Prerequisites (Easier)
- [[q-testing-compose-ui--android--medium]] - Compose UI testing basics
- [[q-compose-testing-semantics--testing--medium]] - Semantics for testing

### Related (Same Level)
- [[q-robolectric-usage--testing--medium]] - Robolectric testing

### Advanced (Harder)
- Design system testing strategies
