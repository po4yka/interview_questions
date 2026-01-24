---
id: android-mod-007
title: "Dynamic Feature Modules / Динамические feature-модули"
aliases: ["Dynamic Feature Modules", "Play Feature Delivery", "Динамическая доставка модулей"]
topic: android
subtopics: [modularization, play-feature-delivery, on-demand]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-module-types--modularization--medium, q-feature-module-navigation--modularization--hard]
created: 2026-01-23
updated: 2026-01-23
sources: []
tags: [android/modularization, android/play-feature-delivery, android/on-demand, difficulty/hard, dynamic-features]

---
# Вопрос (RU)

> Что такое Dynamic Feature Modules и Play Feature Delivery? Как реализовать on-demand загрузку модулей?

# Question (EN)

> What are Dynamic Feature Modules and Play Feature Delivery? How do you implement on-demand module loading?

---

## Ответ (RU)

**Dynamic Feature Modules (DFM)** позволяют доставлять части приложения по запросу, а не при первоначальной установке. **Play Feature Delivery** - сервис Google Play для управления этой доставкой.

### Зачем Нужны Dynamic Features

| Проблема | Решение с DFM |
|----------|---------------|
| Большой размер APK | Базовый APK меньше, features загружаются по необходимости |
| Функции для редких юзкейсов | AR/VR, расширенная аналитика - не в базовом APK |
| A/B тестирование | Разные features для разных пользователей |
| Региональный контент | Специфичный контент только для нужных регионов |

### Типы Доставки

| Тип | Когда устанавливается | Использование |
|-----|----------------------|---------------|
| `install-time` | При установке из Play Store | Всегда нужные, но изолированные features |
| `on-demand` | При запросе из кода | Редкие features (AR, премиум) |
| `conditional` | При выполнении условий | Регион, API level, тип устройства |

### Структура Проекта

```
my-app/
  app/                           # Base module (com.android.application)
  feature/
    home/                        # Regular library module
    profile/                     # Regular library module
  dynamic-feature/
    ar-camera/                   # Dynamic feature (com.android.dynamic-feature)
    premium-editor/              # Dynamic feature
    offline-maps/                # Dynamic feature
```

### Настройка Dynamic Feature Module

```kotlin
// dynamic-feature/ar-camera/build.gradle.kts
plugins {
    id("com.android.dynamic-feature")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.feature.arcamera"
    compileSdk = 35

    defaultConfig {
        minSdk = 26
    }
}

dependencies {
    // Dynamic feature ДОЛЖЕН зависеть от :app
    implementation(project(":app"))

    // ARCore для примера
    implementation("com.google.ar:core:1.44.0")
    implementation(project(":core:ui"))
}
```

```xml
<!-- dynamic-feature/ar-camera/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:dist="http://schemas.android.com/apk/distribution">

    <!-- Определение типа доставки -->
    <dist:module
        dist:instant="false"
        dist:title="@string/title_ar_camera">
        <dist:delivery>
            <!-- On-demand: загружается по запросу -->
            <dist:on-demand />
        </dist:delivery>
        <dist:fusing dist:include="true" />
    </dist:module>

    <application>
        <activity
            android:name=".ArCameraActivity"
            android:exported="false" />
    </application>
</manifest>
```

```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
}

android {
    // ...

    // Связь с dynamic features
    dynamicFeatures += setOf(
        ":dynamic-feature:ar-camera",
        ":dynamic-feature:premium-editor",
        ":dynamic-feature:offline-maps"
    )
}

dependencies {
    // Play Feature Delivery library
    implementation("com.google.android.play:feature-delivery:2.1.0")
    implementation("com.google.android.play:feature-delivery-ktx:2.1.0")
}
```

### Загрузка Модуля On-Demand

```kotlin
// app/src/.../feature/DynamicFeatureManager.kt
import com.google.android.play.core.splitinstall.*
import com.google.android.play.core.splitinstall.model.SplitInstallSessionStatus
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

sealed class InstallState {
    data object NotInstalled : InstallState()
    data object Pending : InstallState()
    data class Downloading(val progress: Int) : InstallState()
    data object Installing : InstallState()
    data object Installed : InstallState()
    data class Failed(val errorCode: Int) : InstallState()
    data object RequiresConfirmation : InstallState()
}

class DynamicFeatureManager(
    private val context: Context
) {
    private val splitInstallManager = SplitInstallManagerFactory.create(context)

    private val _installState = MutableStateFlow<InstallState>(InstallState.NotInstalled)
    val installState: StateFlow<InstallState> = _installState

    private var sessionId = 0

    private val listener = SplitInstallStateUpdatedListener { state ->
        if (state.sessionId() == sessionId) {
            _installState.value = when (state.status()) {
                SplitInstallSessionStatus.PENDING -> InstallState.Pending
                SplitInstallSessionStatus.DOWNLOADING -> {
                    val progress = (state.bytesDownloaded() * 100 / state.totalBytesToDownload()).toInt()
                    InstallState.Downloading(progress)
                }
                SplitInstallSessionStatus.INSTALLING -> InstallState.Installing
                SplitInstallSessionStatus.INSTALLED -> InstallState.Installed
                SplitInstallSessionStatus.FAILED -> InstallState.Failed(state.errorCode())
                SplitInstallSessionStatus.REQUIRES_USER_CONFIRMATION -> InstallState.RequiresConfirmation
                SplitInstallSessionStatus.CANCELING -> InstallState.NotInstalled
                SplitInstallSessionStatus.CANCELED -> InstallState.NotInstalled
                else -> _installState.value
            }
        }
    }

    init {
        splitInstallManager.registerListener(listener)
    }

    fun isModuleInstalled(moduleName: String): Boolean {
        return splitInstallManager.installedModules.contains(moduleName)
    }

    fun requestInstall(moduleName: String) {
        if (isModuleInstalled(moduleName)) {
            _installState.value = InstallState.Installed
            return
        }

        val request = SplitInstallRequest.newBuilder()
            .addModule(moduleName)
            .build()

        splitInstallManager.startInstall(request)
            .addOnSuccessListener { id ->
                sessionId = id
                _installState.value = InstallState.Pending
            }
            .addOnFailureListener { exception ->
                _installState.value = InstallState.Failed(
                    (exception as? SplitInstallException)?.errorCode ?: -1
                )
            }
    }

    fun cancelInstall() {
        if (sessionId != 0) {
            splitInstallManager.cancelInstall(sessionId)
        }
    }

    fun cleanup() {
        splitInstallManager.unregisterListener(listener)
    }
}
```

### Использование в UI

```kotlin
// app/src/.../ui/ArCameraButton.kt
@Composable
fun ArCameraFeatureButton(
    featureManager: DynamicFeatureManager = remember { DynamicFeatureManager(LocalContext.current) },
    onFeatureReady: () -> Unit
) {
    val installState by featureManager.installState.collectAsStateWithLifecycle()
    val context = LocalContext.current

    LaunchedEffect(installState) {
        if (installState is InstallState.Installed) {
            onFeatureReady()
        }
    }

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        when (val state = installState) {
            is InstallState.NotInstalled -> {
                Button(onClick = { featureManager.requestInstall("ar_camera") }) {
                    Text("Download AR Camera")
                }
            }
            is InstallState.Pending -> {
                CircularProgressIndicator()
                Text("Preparing download...")
            }
            is InstallState.Downloading -> {
                LinearProgressIndicator(progress = { state.progress / 100f })
                Text("Downloading: ${state.progress}%")
            }
            is InstallState.Installing -> {
                CircularProgressIndicator()
                Text("Installing...")
            }
            is InstallState.Installed -> {
                Button(onClick = onFeatureReady) {
                    Text("Open AR Camera")
                }
            }
            is InstallState.Failed -> {
                Text("Installation failed: ${state.errorCode}", color = Color.Red)
                Button(onClick = { featureManager.requestInstall("ar_camera") }) {
                    Text("Retry")
                }
            }
            is InstallState.RequiresConfirmation -> {
                // Показать диалог подтверждения для больших модулей
                Text("User confirmation required")
            }
        }
    }
}
```

### Навигация к Dynamic Feature

```kotlin
// app/src/.../navigation/DynamicFeatureNavigation.kt
object DynamicFeatureRoutes {
    const val AR_CAMERA = "ar_camera"
    const val AR_CAMERA_ACTIVITY = "com.example.feature.arcamera.ArCameraActivity"
}

fun NavGraphBuilder.arCameraNavigation(
    featureManager: DynamicFeatureManager,
    onNavigateToArCamera: () -> Unit
) {
    composable(DynamicFeatureRoutes.AR_CAMERA) {
        ArCameraFeatureButton(
            featureManager = featureManager,
            onFeatureReady = onNavigateToArCamera
        )
    }
}

// Запуск Activity из dynamic feature
fun Context.launchArCamera() {
    val intent = Intent().apply {
        setClassName(packageName, DynamicFeatureRoutes.AR_CAMERA_ACTIVITY)
    }
    startActivity(intent)
}
```

### Conditional Delivery

```xml
<!-- Доставка только для определенных условий -->
<dist:delivery>
    <dist:install-time>
        <dist:conditions>
            <!-- Только для устройств с минимум 4GB RAM -->
            <dist:min-sdk dist:value="26" />

            <!-- Только для определенных стран -->
            <dist:user-countries dist:exclude="false">
                <dist:country dist:code="US" />
                <dist:country dist:code="GB" />
            </dist:user-countries>

            <!-- Только для устройств с определенными features -->
            <dist:device-feature dist:name="android.hardware.camera.ar" />
        </dist:conditions>
    </dist:install-time>
</dist:delivery>
```

### Тестирование

```bash
# Локальное тестирование с bundletool
# 1. Создать AAB
./gradlew :app:bundleDebug

# 2. Создать APKs для тестирования
bundletool build-apks \
  --bundle=app/build/outputs/bundle/debug/app-debug.aab \
  --output=app-debug.apks \
  --local-testing

# 3. Установить на устройство
bundletool install-apks --apks=app-debug.apks

# 4. Эмуляция on-demand установки
# FakeSplitInstallManager автоматически используется при local-testing
```

```kotlin
// Тест
@Test
fun testDynamicFeatureInstallation() = runTest {
    val fakeManager = FakeSplitInstallManager(context)
    fakeManager.setShouldNetworkError(false)

    val featureManager = DynamicFeatureManager(context, fakeManager)
    featureManager.requestInstall("ar_camera")

    // Эмулируем успешную установку
    advanceUntilIdle()

    assertEquals(InstallState.Installed, featureManager.installState.value)
}
```

### Обработка Обратной Совместимости

```kotlin
// SplitCompatApplication для поддержки DFM
class MyApplication : SplitCompatApplication() {
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(base)
        // Автоматически вызывается SplitCompat.install(this)
    }
}

// Или вручную в Activity
class MainActivity : AppCompatActivity() {
    override fun attachBaseContext(newBase: Context) {
        super.attachBaseContext(newBase)
        SplitCompat.installActivity(this)
    }
}
```

### Best Practices

| Практика | Описание |
|----------|----------|
| Минимизировать размер DFM | Чем меньше модуль, тем быстрее загрузка |
| Graceful degradation | UI должен работать без DFM |
| Предзагрузка | Загружать features заранее при Wi-Fi |
| Метрики | Отслеживать успешность и время загрузки |
| Fallback | Иметь план B если загрузка не удалась |

---

## Answer (EN)

**Dynamic Feature Modules (DFM)** allow delivering parts of an application on-demand rather than at initial installation. **Play Feature Delivery** is Google Play's service for managing this delivery.

### Why Dynamic Features

| Problem | DFM Solution |
|---------|-------------|
| Large APK size | Smaller base APK, features load as needed |
| Rarely used features | AR/VR, advanced analytics - not in base APK |
| A/B testing | Different features for different users |
| Regional content | Specific content only for needed regions |

### Delivery Types

| Type | When Installed | Use Case |
|------|---------------|----------|
| `install-time` | At Play Store installation | Always needed but isolated features |
| `on-demand` | When requested from code | Rare features (AR, premium) |
| `conditional` | When conditions met | Region, API level, device type |

### Project Structure

```
my-app/
  app/                           # Base module (com.android.application)
  feature/
    home/                        # Regular library module
    profile/                     # Regular library module
  dynamic-feature/
    ar-camera/                   # Dynamic feature (com.android.dynamic-feature)
    premium-editor/              # Dynamic feature
    offline-maps/                # Dynamic feature
```

### Dynamic Feature Module Setup

```kotlin
// dynamic-feature/ar-camera/build.gradle.kts
plugins {
    id("com.android.dynamic-feature")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.feature.arcamera"
    compileSdk = 35

    defaultConfig {
        minSdk = 26
    }
}

dependencies {
    // Dynamic feature MUST depend on :app
    implementation(project(":app"))

    // ARCore for example
    implementation("com.google.ar:core:1.44.0")
    implementation(project(":core:ui"))
}
```

```xml
<!-- dynamic-feature/ar-camera/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:dist="http://schemas.android.com/apk/distribution">

    <!-- Define delivery type -->
    <dist:module
        dist:instant="false"
        dist:title="@string/title_ar_camera">
        <dist:delivery>
            <!-- On-demand: loaded on request -->
            <dist:on-demand />
        </dist:delivery>
        <dist:fusing dist:include="true" />
    </dist:module>

    <application>
        <activity
            android:name=".ArCameraActivity"
            android:exported="false" />
    </application>
</manifest>
```

```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
}

android {
    // ...

    // Link to dynamic features
    dynamicFeatures += setOf(
        ":dynamic-feature:ar-camera",
        ":dynamic-feature:premium-editor",
        ":dynamic-feature:offline-maps"
    )
}

dependencies {
    // Play Feature Delivery library
    implementation("com.google.android.play:feature-delivery:2.1.0")
    implementation("com.google.android.play:feature-delivery-ktx:2.1.0")
}
```

### On-Demand Module Loading

```kotlin
// app/src/.../feature/DynamicFeatureManager.kt
import com.google.android.play.core.splitinstall.*
import com.google.android.play.core.splitinstall.model.SplitInstallSessionStatus
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

sealed class InstallState {
    data object NotInstalled : InstallState()
    data object Pending : InstallState()
    data class Downloading(val progress: Int) : InstallState()
    data object Installing : InstallState()
    data object Installed : InstallState()
    data class Failed(val errorCode: Int) : InstallState()
    data object RequiresConfirmation : InstallState()
}

class DynamicFeatureManager(
    private val context: Context
) {
    private val splitInstallManager = SplitInstallManagerFactory.create(context)

    private val _installState = MutableStateFlow<InstallState>(InstallState.NotInstalled)
    val installState: StateFlow<InstallState> = _installState

    private var sessionId = 0

    private val listener = SplitInstallStateUpdatedListener { state ->
        if (state.sessionId() == sessionId) {
            _installState.value = when (state.status()) {
                SplitInstallSessionStatus.PENDING -> InstallState.Pending
                SplitInstallSessionStatus.DOWNLOADING -> {
                    val progress = (state.bytesDownloaded() * 100 / state.totalBytesToDownload()).toInt()
                    InstallState.Downloading(progress)
                }
                SplitInstallSessionStatus.INSTALLING -> InstallState.Installing
                SplitInstallSessionStatus.INSTALLED -> InstallState.Installed
                SplitInstallSessionStatus.FAILED -> InstallState.Failed(state.errorCode())
                SplitInstallSessionStatus.REQUIRES_USER_CONFIRMATION -> InstallState.RequiresConfirmation
                SplitInstallSessionStatus.CANCELING -> InstallState.NotInstalled
                SplitInstallSessionStatus.CANCELED -> InstallState.NotInstalled
                else -> _installState.value
            }
        }
    }

    init {
        splitInstallManager.registerListener(listener)
    }

    fun isModuleInstalled(moduleName: String): Boolean {
        return splitInstallManager.installedModules.contains(moduleName)
    }

    fun requestInstall(moduleName: String) {
        if (isModuleInstalled(moduleName)) {
            _installState.value = InstallState.Installed
            return
        }

        val request = SplitInstallRequest.newBuilder()
            .addModule(moduleName)
            .build()

        splitInstallManager.startInstall(request)
            .addOnSuccessListener { id ->
                sessionId = id
                _installState.value = InstallState.Pending
            }
            .addOnFailureListener { exception ->
                _installState.value = InstallState.Failed(
                    (exception as? SplitInstallException)?.errorCode ?: -1
                )
            }
    }

    fun cancelInstall() {
        if (sessionId != 0) {
            splitInstallManager.cancelInstall(sessionId)
        }
    }

    fun cleanup() {
        splitInstallManager.unregisterListener(listener)
    }
}
```

### Usage in UI

```kotlin
// app/src/.../ui/ArCameraButton.kt
@Composable
fun ArCameraFeatureButton(
    featureManager: DynamicFeatureManager = remember { DynamicFeatureManager(LocalContext.current) },
    onFeatureReady: () -> Unit
) {
    val installState by featureManager.installState.collectAsStateWithLifecycle()
    val context = LocalContext.current

    LaunchedEffect(installState) {
        if (installState is InstallState.Installed) {
            onFeatureReady()
        }
    }

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        when (val state = installState) {
            is InstallState.NotInstalled -> {
                Button(onClick = { featureManager.requestInstall("ar_camera") }) {
                    Text("Download AR Camera")
                }
            }
            is InstallState.Pending -> {
                CircularProgressIndicator()
                Text("Preparing download...")
            }
            is InstallState.Downloading -> {
                LinearProgressIndicator(progress = { state.progress / 100f })
                Text("Downloading: ${state.progress}%")
            }
            is InstallState.Installing -> {
                CircularProgressIndicator()
                Text("Installing...")
            }
            is InstallState.Installed -> {
                Button(onClick = onFeatureReady) {
                    Text("Open AR Camera")
                }
            }
            is InstallState.Failed -> {
                Text("Installation failed: ${state.errorCode}", color = Color.Red)
                Button(onClick = { featureManager.requestInstall("ar_camera") }) {
                    Text("Retry")
                }
            }
            is InstallState.RequiresConfirmation -> {
                // Show confirmation dialog for large modules
                Text("User confirmation required")
            }
        }
    }
}
```

### Navigation to Dynamic Feature

```kotlin
// app/src/.../navigation/DynamicFeatureNavigation.kt
object DynamicFeatureRoutes {
    const val AR_CAMERA = "ar_camera"
    const val AR_CAMERA_ACTIVITY = "com.example.feature.arcamera.ArCameraActivity"
}

fun NavGraphBuilder.arCameraNavigation(
    featureManager: DynamicFeatureManager,
    onNavigateToArCamera: () -> Unit
) {
    composable(DynamicFeatureRoutes.AR_CAMERA) {
        ArCameraFeatureButton(
            featureManager = featureManager,
            onFeatureReady = onNavigateToArCamera
        )
    }
}

// Launch Activity from dynamic feature
fun Context.launchArCamera() {
    val intent = Intent().apply {
        setClassName(packageName, DynamicFeatureRoutes.AR_CAMERA_ACTIVITY)
    }
    startActivity(intent)
}
```

### Conditional Delivery

```xml
<!-- Delivery only for specific conditions -->
<dist:delivery>
    <dist:install-time>
        <dist:conditions>
            <!-- Only for devices with at least 4GB RAM -->
            <dist:min-sdk dist:value="26" />

            <!-- Only for specific countries -->
            <dist:user-countries dist:exclude="false">
                <dist:country dist:code="US" />
                <dist:country dist:code="GB" />
            </dist:user-countries>

            <!-- Only for devices with specific features -->
            <dist:device-feature dist:name="android.hardware.camera.ar" />
        </dist:conditions>
    </dist:install-time>
</dist:delivery>
```

### Testing

```bash
# Local testing with bundletool
# 1. Create AAB
./gradlew :app:bundleDebug

# 2. Create APKs for testing
bundletool build-apks \
  --bundle=app/build/outputs/bundle/debug/app-debug.aab \
  --output=app-debug.apks \
  --local-testing

# 3. Install on device
bundletool install-apks --apks=app-debug.apks

# 4. Emulate on-demand installation
# FakeSplitInstallManager is automatically used with local-testing
```

```kotlin
// Test
@Test
fun testDynamicFeatureInstallation() = runTest {
    val fakeManager = FakeSplitInstallManager(context)
    fakeManager.setShouldNetworkError(false)

    val featureManager = DynamicFeatureManager(context, fakeManager)
    featureManager.requestInstall("ar_camera")

    // Emulate successful installation
    advanceUntilIdle()

    assertEquals(InstallState.Installed, featureManager.installState.value)
}
```

### Backwards Compatibility Handling

```kotlin
// SplitCompatApplication for DFM support
class MyApplication : SplitCompatApplication() {
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(base)
        // Automatically calls SplitCompat.install(this)
    }
}

// Or manually in Activity
class MainActivity : AppCompatActivity() {
    override fun attachBaseContext(newBase: Context) {
        super.attachBaseContext(newBase)
        SplitCompat.installActivity(this)
    }
}
```

### Best Practices

| Practice | Description |
|----------|-------------|
| Minimize DFM size | Smaller module = faster download |
| Graceful degradation | UI should work without DFM |
| Prefetching | Load features ahead of time on Wi-Fi |
| Metrics | Track success rate and download time |
| Fallback | Have a plan B if download fails |

---

## Follow-ups

- How do you handle resources (strings, images) in dynamic feature modules?
- What happens when a user uninstalls a dynamic feature?
- How do you implement instant apps with dynamic features?

## References

- https://developer.android.com/guide/playcore/feature-delivery
- https://developer.android.com/guide/app-bundle/dynamic-delivery
- https://github.com/android/app-bundle-samples

## Related Questions

### Prerequisites

- [[q-module-types--modularization--medium]] - Module types overview
- [[q-feature-module-navigation--modularization--hard]] - Feature navigation

### Related

- [[q-module-dependency-graph--modularization--hard]] - Dependency graph with DFM
- [[q-play-store-publishing--android--medium]] - App Bundle publishing

### Advanced

- [[q-instant-apps--android--hard]] - Instant Apps integration
- [[q-app-size-optimization--android--hard]] - APK/AAB size optimization
