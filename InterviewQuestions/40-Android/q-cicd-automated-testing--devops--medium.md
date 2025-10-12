---
tags:
  - android
  - ci-cd
  - testing
  - automation
  - github-actions
  - emulator
difficulty: medium
status: draft
related:
  - q-cicd-pipeline-setup--devops--medium
  - q-compose-ui-testing--testing--medium
  - q-testing-coroutines-flow--testing--hard
created: 2025-10-11
---

# Question (EN)
How do you run automated tests (unit, instrumented, UI) in CI/CD? What are the challenges with running instrumented tests in CI and how do you solve them?

## Answer (EN)
### Overview

Automated testing in CI/CD ensures code quality and catches regressions before they reach production. Different test types have different requirements and challenges in CI environments.

### Test Types in CI/CD

```
┌─────────────────────────────────────────────────────┐
│              Test Pyramid in CI                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│                    ▲                                 │
│                   ╱ ╲     E2E Tests                 │
│                  ╱   ╲    (Slowest, Most Expensive) │
│                 ╱     ╲                              │
│                ╱───────╲                             │
│               ╱         ╲   Integration Tests       │
│              ╱           ╲  (Medium Speed/Cost)     │
│             ╱             ╲                          │
│            ╱───────────────╲                         │
│           ╱                 ╲  Unit Tests            │
│          ╱                   ╲ (Fast, Cheap)         │
│         ╱                     ╲                       │
│        ╱───────────────────────╲                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 1. Unit Tests in CI (Fast & Easy)

**Characteristics:**
- ⚡ Fast (milliseconds to seconds)
- 💰 Cheap (no special hardware)
- ✅ Always run in CI
- 🎯 High confidence per test

**build.gradle.kts**:

```kotlin
android {
    // Enable unit test coverage
    buildTypes {
        debug {
            enableUnitTestCoverage = true
        }
    }

    testOptions {
        unitTests {
            isIncludeAndroidResources = true
            isReturnDefaultValues = true

            all {
                it.useJUnitPlatform() // For JUnit 5
                it.testLogging {
                    events("passed", "skipped", "failed")
                }
            }
        }
    }
}

dependencies {
    // Unit testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("app.cash.turbine:turbine:1.0.0")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("com.google.truth:truth:1.1.5")

    // Robolectric for Android framework in unit tests
    testImplementation("org.robolectric:robolectric:4.11")
}
```

**GitHub Actions - Unit Tests**:

```yaml
name: Unit Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission
        run: chmod +x gradlew

      # Run unit tests with coverage
      - name: Run unit tests
        run: ./gradlew testDebugUnitTest jacocoTestReport

      # Upload coverage to Codecov
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          files: ./app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml
          flags: unittests
          name: codecov-unit-tests

      # Publish test results
      - name: Publish test results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: |
            app/build/test-results/**/*.xml

      # Upload HTML reports
      - name: Upload test reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-reports
          path: |
            app/build/reports/tests/
            app/build/reports/jacoco/

      # Comment PR with test results
      - name: Comment test results on PR
        uses: dorny/test-reporter@v1
        if: github.event_name == 'pull_request'
        with:
          name: Unit Test Results
          path: app/build/test-results/**/*.xml
          reporter: java-junit
```

### 2. Instrumented Tests in CI (Challenging)

**Challenges:**
1. ❌ Requires Android device or emulator
2. ❌ Slow (minutes to hours)
3. ❌ Expensive (macOS runners for hardware acceleration)
4. ❌ Flaky (timing issues, animation delays)
5. ❌ Resource intensive (memory, CPU)

**Solutions:**

#### Solution 1: Firebase Test Lab (Recommended)

**Advantages:**
- ✅ Real devices
- ✅ Fast parallel execution
- ✅ No emulator management
- ✅ Test on multiple devices/APIs
- ✅ Screenshots & videos

**GitHub Actions with Firebase Test Lab**:

```yaml
name: Instrumented Tests (Firebase)

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  instrumented-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 45

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission
        run: chmod +x gradlew

      # Build debug APK and test APK
      - name: Build APKs
        run: |
          ./gradlew assembleDebug
          ./gradlew assembleDebugAndroidTest

      # Authenticate with Google Cloud
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GOOGLE_CLOUD_SERVICE_ACCOUNT }}

      # Run tests on Firebase Test Lab
      - name: Run tests on Firebase Test Lab
        run: |
          gcloud firebase test android run \
            --type instrumentation \
            --app app/build/outputs/apk/debug/app-debug.apk \
            --test app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk \
            --device model=Pixel2,version=30,locale=en,orientation=portrait \
            --device model=Pixel6,version=33,locale=en,orientation=portrait \
            --timeout 20m \
            --results-bucket=gs://my-app-test-results \
            --results-dir=run-${{ github.run_number }}

      # Download test results
      - name: Download test results
        run: |
          gsutil -m cp -r gs://my-app-test-results/run-${{ github.run_number }}/** ./test-results/

      # Upload test results
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: firebase-test-results
          path: test-results/
```

#### Solution 2: GitHub Actions with Emulator

**Advantages:**
- ✅ Free (within limits)
- ✅ No external dependencies
- ❌ Slow on Linux runners
- ✅ Fast on macOS runners (hardware acceleration)

**GitHub Actions with Emulator (macOS)**:

```yaml
name: Instrumented Tests (Emulator)

on:
  push:
    branches: [ main ]

jobs:
  instrumented-tests:
    runs-on: macos-latest # Hardware acceleration
    timeout-minutes: 60

    strategy:
      matrix:
        api-level: [29, 30, 33]
        target: [google_apis]
        arch: [x86_64]

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission
        run: chmod +x gradlew

      # Cache AVD
      - name: AVD cache
        uses: actions/cache@v3
        id: avd-cache
        with:
          path: |
            ~/.android/avd/*
            ~/.android/adb*
          key: avd-${{ matrix.api-level }}-${{ matrix.arch }}

      # Create AVD if not cached
      - name: Create AVD and generate snapshot
        if: steps.avd-cache.outputs.cache-hit != 'true'
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: ${{ matrix.api-level }}
          target: ${{ matrix.target }}
          arch: ${{ matrix.arch }}
          force-avd-creation: false
          emulator-options: -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim -camera-back none
          disable-animations: true
          script: echo "Generated AVD snapshot for caching."

      # Run instrumented tests
      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: ${{ matrix.api-level }}
          target: ${{ matrix.target }}
          arch: ${{ matrix.arch }}
          force-avd-creation: false
          emulator-options: -no-snapshot-save -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim -camera-back none
          disable-animations: true
          script: ./gradlew connectedDebugAndroidTest

      # Upload test results
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: instrumented-test-results-${{ matrix.api-level }}
          path: |
            app/build/reports/androidTests/connected/
            app/build/outputs/androidTest-results/

      # Upload screenshots on failure
      - name: Upload screenshots
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: screenshots-${{ matrix.api-level }}
          path: |
            app/build/outputs/connected_android_test_additional_output/
```

#### Solution 3: Gradle Managed Devices (GMD)

**Advantages:**
- ✅ Consistent environments
- ✅ No manual emulator management
- ✅ Gradle caching support

**build.gradle.kts**:

```kotlin
android {
    testOptions {
        managedDevices {
            devices {
                pixel2Api30(com.android.build.api.dsl.ManagedVirtualDevice) {
                    device = "Pixel 2"
                    apiLevel = 30
                    systemImageSource = "aosp"
                }

                pixel6Api33(com.android.build.api.dsl.ManagedVirtualDevice) {
                    device = "Pixel 6"
                    apiLevel = 33
                    systemImageSource = "google"
                }
            }

            groups {
                allDevices {
                    targetDevices.add(devices["pixel2Api30"])
                    targetDevices.add(devices["pixel6Api33"])
                }
            }
        }
    }
}
```

**GitHub Actions with GMD**:

```yaml
name: Instrumented Tests (GMD)

on:
  push:
    branches: [ main ]

jobs:
  instrumented-tests:
    runs-on: macos-latest
    timeout-minutes: 60

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission
        run: chmod +x gradlew

      # Accept licenses
      - name: Accept Android licenses
        run: yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses || true

      # Run tests on all managed devices
      - name: Run tests on managed devices
        run: ./gradlew allDevicesDebugAndroidTest

      # Upload test results
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: gmd-test-results
          path: app/build/reports/androidTests/
```

### 3. Compose UI Tests

**Challenges:**
- Need proper synchronization
- Screenshot testing
- Semantics-based testing

**Example Test**:

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_initialState_showsEmptyFields() {
        composeTestRule.setContent {
            LoginScreen(
                onLoginClick = {},
                onSignUpClick = {}
            )
        }

        // Verify email field is empty
        composeTestRule
            .onNodeWithTag("emailField")
            .assertTextEquals("")

        // Verify password field is empty
        composeTestRule
            .onNodeWithTag("passwordField")
            .assertTextEquals("")

        // Verify login button is displayed
        composeTestRule
            .onNodeWithText("Login")
            .assertIsDisplayed()
    }

    @Test
    fun loginScreen_validCredentials_enablesLoginButton() {
        composeTestRule.setContent {
            LoginScreen(
                onLoginClick = {},
                onSignUpClick = {}
            )
        }

        // Enter email
        composeTestRule
            .onNodeWithTag("emailField")
            .performTextInput("test@example.com")

        // Enter password
        composeTestRule
            .onNodeWithTag("passwordField")
            .performTextInput("password123")

        // Verify login button is enabled
        composeTestRule
            .onNodeWithText("Login")
            .assertIsEnabled()
    }

    @Test
    fun loginScreen_clickLogin_triggersCallback() {
        var loginClicked = false

        composeTestRule.setContent {
            LoginScreen(
                onLoginClick = { loginClicked = true },
                onSignUpClick = {}
            )
        }

        // Enter credentials
        composeTestRule
            .onNodeWithTag("emailField")
            .performTextInput("test@example.com")

        composeTestRule
            .onNodeWithTag("passwordField")
            .performTextInput("password123")

        // Click login
        composeTestRule
            .onNodeWithText("Login")
            .performClick()

        // Verify callback was triggered
        assertTrue(loginClicked)
    }
}
```

**GitHub Actions for Compose UI Tests**:

```yaml
name: Compose UI Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  compose-ui-tests:
    runs-on: ubuntu-latest # Can run on Linux with Robolectric
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission
        run: chmod +x gradlew

      # Run Compose UI tests with Robolectric (no emulator needed)
      - name: Run Compose UI tests
        run: ./gradlew testDebugUnitTest --tests "*ComposeTest"

      # Upload test results
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: compose-ui-test-results
          path: |
            app/build/reports/tests/testDebugUnitTest/
            app/build/test-results/testDebugUnitTest/
```

### 4. Screenshot Testing

**Advantages:**
- ✅ Visual regression detection
- ✅ Catch UI bugs automatically
- ✅ Documentation of UI states

**Using Paparazzi (Robolectric-based)**:

```kotlin
dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.1")
}

// Plugin
plugins {
    id("app.cash.paparazzi") version "1.3.1"
}
```

**Screenshot Test**:

```kotlin
class LoginScreenScreenshotTest {

    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_5,
        theme = "Theme.MyApp"
    )

    @Test
    fun loginScreen_emptyState() {
        paparazzi.snapshot {
            LoginScreen(
                onLoginClick = {},
                onSignUpClick = {}
            )
        }
    }

    @Test
    fun loginScreen_withError() {
        paparazzi.snapshot {
            LoginScreen(
                onLoginClick = {},
                onSignUpClick = {},
                errorMessage = "Invalid credentials"
            )
        }
    }

    @Test
    fun loginScreen_loading() {
        paparazzi.snapshot {
            LoginScreen(
                onLoginClick = {},
                onSignUpClick = {},
                isLoading = true
            )
        }
    }
}
```

**GitHub Actions for Screenshot Tests**:

```yaml
name: Screenshot Tests

on:
  pull_request:
    branches: [ main ]

jobs:
  screenshot-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission
        run: chmod +x gradlew

      # Run screenshot tests
      - name: Run screenshot tests
        run: ./gradlew verifyPaparazziDebug

      # Upload screenshots on failure
      - name: Upload screenshot diffs
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: screenshot-diffs
          path: |
            **/build/paparazzi/failures/
            **/build/paparazzi/images/

      # Record new screenshots if needed
      - name: Record new screenshots
        if: failure()
        run: ./gradlew recordPaparazziDebug
```

### Test Optimization Strategies

#### 1. Test Sharding

Split tests across multiple machines for parallel execution:

```yaml
# GitHub Actions - Test Sharding
strategy:
  matrix:
    shard: [0, 1, 2, 3]

steps:
  - name: Run tests (shard ${{ matrix.shard }})
    run: |
      ./gradlew connectedDebugAndroidTest \
        -Pandroid.testInstrumentationRunnerArguments.numShards=4 \
        -Pandroid.testInstrumentationRunnerArguments.shardIndex=${{ matrix.shard }}
```

#### 2. Test Filtering

Run only tests affected by code changes:

```gradle
// build.gradle.kts
tasks.register("quickTest") {
    dependsOn("testDebugUnitTest")

    // Only run tests for changed modules
    doFirst {
        val changedFiles = getChangedFiles()
        val affectedModules = getAffectedModules(changedFiles)

        affectedModules.forEach { module ->
            tasks.getByPath(":$module:testDebugUnitTest").run()
        }
    }
}
```

#### 3. Fail Fast

```yaml
# Stop on first failure
strategy:
  fail-fast: true
  matrix:
    api-level: [29, 30, 33]
```

#### 4. Retry Flaky Tests

```yaml
# Retry failed tests
- name: Run tests with retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 30
    max_attempts: 3
    command: ./gradlew connectedDebugAndroidTest
```

### Best Practices

1. **Run Unit Tests Always, Instrumented Conditionally**
   ```yaml
   # ✅ GOOD - Unit tests on every push
   on:
     push:
       branches: [ main, develop ]

   jobs:
     unit-tests: # Fast, always run
       runs-on: ubuntu-latest

     instrumented-tests: # Slow, only on main
       runs-on: macos-latest
       if: github.ref == 'refs/heads/main'
   ```

2. **Use Test Tags to Control Execution**
   ```kotlin
   // ✅ GOOD - Tag expensive tests
   @LargeTest
   @Test
   fun expensiveIntegrationTest() {
       // Only run in nightly builds
   }

   // Run in CI
   ./gradlew connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.notAnnotation=androidx.test.filters.LargeTest
   ```

3. **Disable Animations in Tests**
   ```kotlin
   // ✅ GOOD - Disable animations for reliable tests
   @Before
   fun disableAnimations() {
       val context = InstrumentationRegistry.getInstrumentation().targetContext
       setAnimationsEnabled(context, false)
   }

   private fun setAnimationsEnabled(context: Context, enabled: Boolean) {
       val scale = if (enabled) 1f else 0f
       Settings.Global.putFloat(context.contentResolver,
           Settings.Global.ANIMATOR_DURATION_SCALE, scale)
       Settings.Global.putFloat(context.contentResolver,
           Settings.Global.TRANSITION_ANIMATION_SCALE, scale)
       Settings.Global.putFloat(context.contentResolver,
           Settings.Global.WINDOW_ANIMATION_SCALE, scale)
   }
   ```

4. **Use Hermetic Tests**
   ```kotlin
   // ✅ GOOD - Self-contained tests
   @Test
   fun testWithMockData() {
       val mockData = createMockData()
       val result = processData(mockData)
       assertEquals(expected, result)
   }

   // ❌ BAD - Depends on external state
   @Test
   fun testWithRealAPI() {
       val result = apiClient.fetchData() // Network call!
       assertEquals(expected, result)
   }
   ```

### Summary

**Test types in CI:**
- ✅ **Unit tests**: Always run, fast, cheap
- ✅ **Instrumented tests**: Run on main branch or nightly, slow, expensive
- ✅ **Screenshot tests**: Run on PRs, catch visual regressions
- ✅ **Compose UI tests**: Can run with Robolectric (fast) or emulator (slow)

**Instrumented test solutions:**
1. **Firebase Test Lab**: Best for production (real devices, parallel, expensive)
2. **GitHub Actions Emulator**: Good for open source (free macOS runners)
3. **Gradle Managed Devices**: Good for consistency (gradle-managed)

**Optimization strategies:**
- Shard tests across multiple machines
- Filter tests by affected modules
- Fail fast on first error
- Retry flaky tests
- Cache emulator snapshots

**Best practices:**
- Run unit tests on every push
- Run instrumented tests conditionally
- Disable animations in tests
- Use test tags to control execution
- Write hermetic (self-contained) tests

---

# Вопрос (RU)
Как запускать автоматизированные тесты (unit, instrumented, UI) в CI/CD? Какие проблемы возникают при запуске instrumented-тестов в CI и как их решать?

## Ответ (RU)
[Перевод примеров из английской версии...]

### Резюме

**Типы тестов в CI:**
- ✅ **Unit-тесты**: Всегда запускаются, быстрые, дешёвые
- ✅ **Instrumented-тесты**: Запускаются на main-ветке или ночные билды, медленные, дорогие
- ✅ **Screenshot-тесты**: Запускаются на PR, ловят визуальные регрессии
- ✅ **Compose UI тесты**: Можно запускать с Robolectric (быстро) или эмулятором (медленно)

**Решения для instrumented-тестов:**
1. **Firebase Test Lab**: Лучше для production (реальные устройства, параллельно, дорого)
2. **GitHub Actions Emulator**: Хорошо для open source (бесплатные macOS-runner'ы)
3. **Gradle Managed Devices**: Хорошо для консистентности (управляется gradle)

**Стратегии оптимизации:**
- Шардирование тестов на несколько машин
- Фильтрация тестов по затронутым модулям
- Fail fast на первой ошибке
- Retry для flaky-тестов
- Кеширование снимков эмулятора

**Лучшие практики:**
- Запускать unit-тесты на каждый push
- Запускать instrumented-тесты условно
- Отключать анимации в тестах
- Использовать теги для управления выполнением
- Писать hermetic (самодостаточные) тесты
