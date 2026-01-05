---
id: "20251025-143000"
title: "Android App Bundle / Android App Bundle"
aliases: ["AAB", "Android App Bundle", "App Bundle", "Формат App Bundle"]
summary: "Publishing format for Android apps that enables Google Play to generate optimized APKs for each device configuration"
topic: "android"
subtopics: ["app-bundle", "gradle", "publishing"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: [c-gradle, c-release-engineering, c-app-signing, c-play-console, c-play-feature-delivery]
created: "2025-10-25"
updated: "2025-10-25"
tags: ["android", "app-bundle", "build", "concept", "difficulty/medium", "gradle", "publishing"]
---

# Android App Bundle / Android App Bundle

## Summary (EN)

Android App Bundle (AAB) is the official publishing format for Android apps, replacing the traditional APK format. It's a publishing format that includes all your app's compiled code and resources, but defers APK generation and signing to Google Play. This allows Google Play to generate optimized APKs tailored to each user's device configuration, reducing download size by up to 50%. App Bundles support Dynamic Feature Modules, allowing apps to deliver features on-demand, and enable Play Asset Delivery for large game assets.

## Краткое Описание (RU)

Android App Bundle (AAB) - официальный формат публикации приложений Android, заменяющий традиционный формат APK. Это формат публикации, который включает весь скомпилированный код и ресурсы приложения, но делегирует генерацию и подписание APK Google Play. Это позволяет Google Play генерировать оптимизированные APK для конфигурации устройства каждого пользователя, уменьшая размер загрузки до 50%. App Bundle поддерживает динамические функциональные модули, позволяя приложениям доставлять функции по требованию, и включает Play Asset Delivery для больших игровых ресурсов.

## Key Points (EN)

- Official publishing format required for new apps on Google Play since August 2021
- Reduces download size by excluding unused resources (density, ABI, language)
- Google Play generates optimized APKs for each device configuration
- Supports Dynamic Feature Modules for on-demand feature delivery
- Enables Play Asset Delivery for games with large assets
- Signed bundles allow Google Play to sign APKs with app signing key
- Can be tested locally using bundletool before publishing
- Supports app signing by Google Play (recommended) or manual signing

## Ключевые Моменты (RU)

- Официальный формат публикации, обязательный для новых приложений в Google Play с августа 2021
- Уменьшает размер загрузки, исключая неиспользуемые ресурсы (плотность, ABI, язык)
- Google Play генерирует оптимизированные APK для каждой конфигурации устройства
- Поддерживает динамические функциональные модули для доставки функций по требованию
- Включает Play Asset Delivery для игр с большими ресурсами
- Подписанные bundle позволяют Google Play подписывать APK ключом подписи приложения
- Можно тестировать локально с помощью bundletool перед публикацией
- Поддерживает подписание приложения Google Play (рекомендуется) или ручное подписание

## App Bundle Structure

```
app-bundle.aab
├── base/                  # Base module (always included)
│   ├── dex/              # DEX files
│   ├── manifest/         # AndroidManifest.xml
│   ├── res/              # Resources
│   ├── lib/              # Native libraries (per ABI)
│   ├── assets/           # Assets
│   └── resources.pb      # Resource table
├── feature1/             # Dynamic feature module 1
│   ├── dex/
│   ├── manifest/
│   └── res/
├── feature2/             # Dynamic feature module 2
└── BundleConfig.pb       # Bundle metadata and configuration
```

## Building an App Bundle

### Gradle Configuration

```kotlin
// app/build.gradle.kts
android {
    bundle {
        language {
            // Split by language (enabled by default)
            enableSplit = true
        }
        density {
            // Split by screen density (enabled by default)
            enableSplit = true
        }
        abi {
            // Split by CPU architecture (enabled by default)
            enableSplit = true
        }
    }
}
```

### Generate App Bundle

```bash
# Via Gradle
./gradlew :app:bundleRelease

# Output: app/build/outputs/bundle/release/app-release.aab
```

## Testing App Bundle Locally

### Using Bundletool

```bash
# Download bundletool
wget https://github.com/google/bundletool/releases/latest/download/bundletool-all.jar

# Generate APK set from AAB
java -jar bundletool-all.jar build-apks \
  --bundle=app-release.aab \
  --output=app.apks \
  --ks=keystore.jks \
  --ks-pass=pass:keystore_password \
  --ks-key-alias=key_alias \
  --key-pass=pass:key_password

# Install APKs to connected device (automatically selects device config)
java -jar bundletool-all.jar install-apks --apks=app.apks

# Generate specific APKs for testing
java -jar bundletool-all.jar build-apks \
  --bundle=app-release.aab \
  --output=app.apks \
  --mode=universal  # Single APK with all resources
```

### Extract APKs for Inspection

```bash
# Extract APKs from APK set
unzip app.apks -d extracted_apks/

# View bundle config
java -jar bundletool-all.jar dump config --bundle=app-release.aab

# View bundle manifest
java -jar bundletool-all.jar dump manifest --bundle=app-release.aab
```

## Dynamic Feature Modules

### Creating a Dynamic Feature Module

```kotlin
// feature/build.gradle.kts
plugins {
    id("com.android.dynamic-feature")
    kotlin("android")
}

android {
    namespace = "com.example.feature"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }
}

dependencies {
    implementation(project(":app"))  // Base module dependency
}
```

```xml
<!-- feature/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:dist="http://schemas.android.com/apk/distribution">

    <dist:module
        dist:instant="false"
        dist:title="@string/feature_title">
        <dist:delivery>
            <dist:on-demand />
            <!-- Or install-time: <dist:install-time /> -->
        </dist:delivery>
        <dist:fusing dist:include="true" />
    </dist:module>

    <application />
</manifest>
```

### Installing Dynamic Features

```kotlin
class MainActivity : AppCompatActivity() {

    private val splitInstallManager by lazy {
        SplitInstallManagerFactory.create(this)
    }

    fun installFeature(moduleName: String) {
        val request = SplitInstallRequest.newBuilder()
            .addModule(moduleName)
            .build()

        splitInstallManager.startInstall(request)
            .addOnSuccessListener { sessionId ->
                Log.d("DFM", "Install started: $sessionId")
            }
            .addOnFailureListener { exception ->
                Log.e("DFM", "Install failed", exception)
            }
    }

    fun checkFeatureInstalled(moduleName: String): Boolean {
        return splitInstallManager.installedModules.contains(moduleName)
    }

    // Monitor installation progress
    private val installListener = SplitInstallStateUpdatedListener { state ->
        when (state.status()) {
            SplitInstallSessionStatus.DOWNLOADING -> {
                val progress = (state.bytesDownloaded() * 100) / state.totalBytesToDownload()
                updateProgressBar(progress.toInt())
            }
            SplitInstallSessionStatus.INSTALLING -> {
                showInstalling()
            }
            SplitInstallSessionStatus.INSTALLED -> {
                showInstallSuccess()
            }
            SplitInstallSessionStatus.FAILED -> {
                showInstallFailed(state.errorCode())
            }
        }
    }

    override fun onResume() {
        super.onResume()
        splitInstallManager.registerListener(installListener)
    }

    override fun onPause() {
        super.onPause()
        splitInstallManager.unregisterListener(installListener)
    }
}
```

## App Bundle Vs APK

| Aspect | App Bundle (AAB) | APK |
|--------|-----------------|-----|
| Publishing | Official format since 2021 | Legacy format |
| Size optimization | Automatic per-device splits | Manual multi-APK |
| Google Play requirement | Required for new apps | Not accepted for new apps |
| APK generation | Google Play generates | Developer generates |
| Signing | Managed by Google Play | Developer signs |
| Dynamic delivery | Supported (DFM, PAD) | Not supported |
| Download size | Smaller (optimized) | Larger (all resources) |
| Testing | Requires bundletool | Direct install |

## Size Optimization Example

```
Traditional APK:
- arm64-v8a libs: 10 MB
- armeabi-v7a libs: 8 MB
- x86_64 libs: 12 MB
- x86 libs: 10 MB
- xxhdpi resources: 15 MB
- xhdpi resources: 12 MB
- hdpi resources: 10 MB
- All languages: 5 MB
Total: ~82 MB download for any device

With App Bundle:
- arm64-v8a libs: 10 MB (only for arm64 devices)
- xxhdpi resources: 15 MB (only for xxhdpi screens)
- English language: 1 MB (only selected language)
Total: ~26 MB download (68% reduction!)
```

## Use Cases

### When to Use App Bundle

- **All Google Play apps**: Required for new apps since August 2021
- **Size-sensitive apps**: Apps with large native libraries or resources
- **Multilingual apps**: Apps supporting many languages
- **Feature-rich apps**: Apps with features used by subset of users
- **Game apps**: Games with large asset packs (via Play Asset Delivery)
- **Modular apps**: Apps with on-demand features (Dynamic Feature Modules)

### When APK is Still Needed

- **Non-Play distribution**: Enterprise apps, direct downloads, other stores
- **Testing specific configs**: Testing specific device configurations locally
- **Legacy systems**: Apps for devices without Google Play Services
- **Instant apps**: Building instant app experiences (APK-based)

## Trade-offs

**Pros**:
- Significantly smaller download size (up to 50% reduction)
- Automatic optimization per device configuration
- Supports on-demand feature delivery (Dynamic Feature Modules)
- Managed app signing by Google Play (secure key management)
- Play Asset Delivery for large game assets
- No need to manage multiple APKs manually
- Future-proof (official Google format)
- Better user experience (faster downloads, less storage)

**Cons**:
- Requires Google Play for APK generation (not self-contained)
- More complex testing workflow (need bundletool)
- Debugging APK generation issues harder
- Cannot directly install AAB on device
- Requires Play Core library for dynamic features
- Need to trust Google Play with app signing
- Learning curve for Dynamic Feature Modules
- May complicate CI/CD pipelines initially

## Best Practices

- **Enable all splits**: Language, density, and ABI splits for maximum size reduction
- **Use Play App Signing**: Let Google manage your app signing key securely
- **Test with bundletool**: Always test AAB locally before publishing
- **Modularize features**: Use Dynamic Feature Modules for rarely-used features
- **Monitor download sizes**: Use Play Console to track APK sizes per configuration
- **Handle installation failures**: Gracefully handle DFM installation errors
- **Provide fallbacks**: Don't require dynamic features for core functionality
- **Version carefully**: Coordinate base and dynamic feature module versions
- **Keep base module small**: Move optional features to dynamic modules
- **Document module dependencies**: Clearly document which modules depend on others

## Common Patterns

### Conditional Feature Loading

```kotlin
class FeatureManager(private val context: Context) {

    private val splitInstallManager = SplitInstallManagerFactory.create(context)

    suspend fun loadFeature(featureName: String): Result<Unit> = suspendCancellableCoroutine { cont ->
        if (splitInstallManager.installedModules.contains(featureName)) {
            cont.resume(Result.success(Unit))
            return@suspendCancellableCoroutine
        }

        val request = SplitInstallRequest.newBuilder()
            .addModule(featureName)
            .build()

        splitInstallManager.startInstall(request)
            .addOnSuccessListener {
                cont.resume(Result.success(Unit))
            }
            .addOnFailureListener { exception ->
                cont.resume(Result.failure(exception))
            }
    }

    fun uninstallFeature(featureName: String) {
        splitInstallManager.deferredUninstall(listOf(featureName))
    }
}
```

### Monitoring Installation Progress

```kotlin
sealed class InstallState {
    object NotStarted : InstallState()
    data class Downloading(val progress: Int) : InstallState()
    object Installing : InstallState()
    object Installed : InstallState()
    data class Failed(val errorCode: Int) : InstallState()
}

class FeatureInstallViewModel : ViewModel() {

    private val _installState = MutableStateFlow<InstallState>(InstallState.NotStarted)
    val installState: StateFlow<InstallState> = _installState.asStateFlow()

    private val listener = SplitInstallStateUpdatedListener { state ->
        _installState.value = when (state.status()) {
            SplitInstallSessionStatus.DOWNLOADING -> {
                val progress = if (state.totalBytesToDownload() > 0) {
                    (state.bytesDownloaded() * 100 / state.totalBytesToDownload()).toInt()
                } else 0
                InstallState.Downloading(progress)
            }
            SplitInstallSessionStatus.INSTALLING -> InstallState.Installing
            SplitInstallSessionStatus.INSTALLED -> InstallState.Installed
            SplitInstallSessionStatus.FAILED -> InstallState.Failed(state.errorCode())
            else -> _installState.value
        }
    }

    fun registerListener(manager: SplitInstallManager) {
        manager.registerListener(listener)
    }

    fun unregisterListener(manager: SplitInstallManager) {
        manager.unregisterListener(listener)
    }
}
```

## Related Concepts

- [[c-gradle]]
- [[c-build-variants]]
- [[c-apk-signing]]
- [[c-proguard-r8]]
- [[c-dependency-management]]
- [[c-continuous-delivery]]

## References

- [Android App Bundle Overview](https://developer.android.com/guide/app-bundle)
- [Build and Test an App Bundle](https://developer.android.com/studio/build/building-cmdline#build_bundle)
- [Dynamic Feature Modules](https://developer.android.com/guide/app-bundle/dynamic-delivery)
- [Play Asset Delivery](https://developer.android.com/guide/playcore/asset-delivery)
- [bundletool Documentation](https://developer.android.com/tools/bundletool)
- [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)
