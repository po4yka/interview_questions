---
id: 20251012-12271167
title: "Play Store Publishing / Публикация в Play Store"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-privacy-sandbox-attribution--privacy--medium, q-why-diffutil-needed--android--medium, q-what-are-the-most-important-components-of-compose--android--medium]
created: 2025-10-15
tags: [Kotlin, Distribution, PlayStore, Publishing, difficulty/medium]
---
# Google Play Store Publishing and Release Management

# Question (EN)
> 
Explain the Google Play Store publishing process, release tracks, and app signing strategies. How do you manage app bundles, release configurations, and version management? What are best practices for staged rollouts and A/B testing?

## Answer (EN)
Google Play Store publishing involves comprehensive release management, from app signing to staged rollouts, with modern approaches using App Bundles and automated deployment strategies.

#### App Signing Strategies

**1. Play App Signing (Recommended)**
```gradle
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // Upload key - you keep this
            storeFile = file("../keystore/upload-keystore.jks")
            storePassword = System.getenv("UPLOAD_KEYSTORE_PASSWORD")
            keyAlias = System.getenv("UPLOAD_KEY_ALIAS")
            keyPassword = System.getenv("UPLOAD_KEY_PASSWORD")

            // Enable V1 and V2 signing
            enableV1Signing = true
            enableV2Signing = true
            enableV3Signing = true
            enableV4Signing = true
        }

        create("debug") {
            storeFile = file("../keystore/debug.keystore")
            storePassword = "android"
            keyAlias = "androiddebugkey"
            keyPassword = "android"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

**2. Secure Keystore Management**
```kotlin
// gradle.properties (DO NOT commit - add to .gitignore)
UPLOAD_KEYSTORE_PASSWORD=your_keystore_password
UPLOAD_KEY_ALIAS=your_key_alias
UPLOAD_KEY_PASSWORD=your_key_password

// Or use environment variables in CI/CD
// GitHub Actions secrets
// env:
//   UPLOAD_KEYSTORE_PASSWORD: ${{ secrets.UPLOAD_KEYSTORE_PASSWORD }}
//   UPLOAD_KEY_ALIAS: ${{ secrets.UPLOAD_KEY_ALIAS }}
//   UPLOAD_KEY_PASSWORD: ${{ secrets.UPLOAD_KEY_PASSWORD }}
```

**3. Keystore Generation Script**
```bash
#!/bin/bash
# generate-keystore.sh

# Generate upload keystore
keytool -genkeypair \
  -v \
  -storetype PKCS12 \
  -keystore upload-keystore.jks \
  -alias upload-key \
  -keyalg RSA \
  -keysize 4096 \
  -validity 10000 \
  -dname "CN=YourCompany, OU=Mobile, O=YourCompany Inc, L=City, ST=State, C=US"

# Verify keystore
keytool -list -v -keystore upload-keystore.jks

# Export certificate (for migration)
keytool -export \
  -rfc \
  -keystore upload-keystore.jks \
  -alias upload-key \
  -file upload-certificate.pem

echo "Keystore created successfully!"
echo "Store this file securely and NEVER commit to version control"
```

#### App Bundle Configuration

**1. Build Configuration**
```kotlin
// app/build.gradle.kts
android {
    bundle {
        language {
            // Disable split for specific languages
            enableSplit = true
        }
        density {
            // Enable density splits
            enableSplit = true
        }
        abi {
            // Enable ABI splits
            enableSplit = true
        }

        // Additional configuration
        texture {
            enableSplit = false
        }
    }

    // Dynamic feature modules
    dynamicFeatures.addAll(
        setOf(
            ":feature:premium",
            ":feature:camera",
            ":feature:analytics"
        )
    )
}

// Build bundle
tasks.register("buildReleaseBundle") {
    dependsOn("bundleRelease")
    doLast {
        println("Release bundle created successfully")
        println("Location: app/build/outputs/bundle/release/app-release.aab")
    }
}
```

**2. Dynamic Feature Module**
```kotlin
// feature/premium/build.gradle.kts
plugins {
    id("com.android.dynamic-feature")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.app.feature.premium"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles("proguard-rules.pro")
        }
    }
}

dependencies {
    implementation(project(":app"))
}
```

**3. Dynamic Feature Delivery**
```kotlin
class PremiumFeatureManager @Inject constructor(
    private val context: Context
) {
    private val splitInstallManager = SplitInstallManagerFactory.create(context)

    fun installPremiumFeature(
        onProgress: (Int) -> Unit,
        onSuccess: () -> Unit,
        onFailure: (Int) -> Unit
    ) {
        val request = SplitInstallRequest.newBuilder()
            .addModule("premium")
            .build()

        splitInstallManager.registerListener { state ->
            when (state.status()) {
                SplitInstallSessionStatus.DOWNLOADING -> {
                    val progress = (state.bytesDownloaded() * 100 / state.totalBytesToDownload()).toInt()
                    onProgress(progress)
                }
                SplitInstallSessionStatus.INSTALLING -> {
                    onProgress(100)
                }
                SplitInstallSessionStatus.INSTALLED -> {
                    onSuccess()
                    splitInstallManager.unregisterListener(this)
                }
                SplitInstallSessionStatus.FAILED -> {
                    onFailure(state.errorCode())
                    splitInstallManager.unregisterListener(this)
                }
                SplitInstallSessionStatus.CANCELED -> {
                    onFailure(SplitInstallErrorCode.CANCELED)
                    splitInstallManager.unregisterListener(this)
                }
            }
        }

        splitInstallManager.startInstall(request)
            .addOnFailureListener { exception ->
                onFailure(SplitInstallErrorCode.INTERNAL_ERROR)
            }
    }

    fun isPremiumFeatureInstalled(): Boolean {
        return splitInstallManager.installedModules.contains("premium")
    }

    fun launchPremiumFeature() {
        if (isPremiumFeatureInstalled()) {
            // Launch feature
            val intent = Intent().setClassName(
                context.packageName,
                "com.example.app.feature.premium.PremiumActivity"
            )
            context.startActivity(intent)
        }
    }

    fun uninstallPremiumFeature(onSuccess: () -> Unit) {
        splitInstallManager.deferredUninstall(listOf("premium"))
            .addOnSuccessListener { onSuccess() }
    }
}
```

#### Version Management

**1. Semantic Versioning**
```kotlin
// buildSrc/src/main/kotlin/AppVersion.kt
object AppVersion {
    private const val MAJOR = 2
    private const val MINOR = 5
    private const val PATCH = 3
    private const val BUILD = 127

    const val versionCode = MAJOR * 10000 + MINOR * 100 + PATCH * 10 + BUILD
    const val versionName = "$MAJOR.$MINOR.$PATCH"

    // For internal builds
    fun getFullVersionName(buildType: String): String {
        return when (buildType) {
            "debug" -> "$versionName-debug-$BUILD"
            "qa" -> "$versionName-qa-$BUILD"
            else -> versionName
        }
    }
}

// app/build.gradle.kts
android {
    defaultConfig {
        versionCode = AppVersion.versionCode
        versionName = AppVersion.versionName
    }

    buildTypes {
        debug {
            versionNameSuffix = "-debug-${AppVersion.versionCode}"
            applicationIdSuffix = ".debug"
        }

        create("qa") {
            versionNameSuffix = "-qa-${AppVersion.versionCode}"
            applicationIdSuffix = ".qa"
            matchingFallbacks += listOf("debug")
        }

        release {
            // Production version
        }
    }
}
```

**2. Git-Based Versioning**
```bash
#!/bin/bash
# get-version.sh

# Get version from git tags
GIT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
VERSION_NAME=${GIT_TAG#v}

# Calculate version code from commits
COMMIT_COUNT=$(git rev-list --count HEAD)
VERSION_CODE=$((10000 + COMMIT_COUNT))

echo "versionName=$VERSION_NAME"
echo "versionCode=$VERSION_CODE"

# Save to file for Gradle
echo "VERSION_NAME=$VERSION_NAME" > version.properties
echo "VERSION_CODE=$VERSION_CODE" >> version.properties
```

```kotlin
// Read in build.gradle.kts
val versionPropsFile = file("version.properties")
val versionProps = Properties()

if (versionPropsFile.exists()) {
    versionProps.load(FileInputStream(versionPropsFile))
}

android {
    defaultConfig {
        versionCode = versionProps.getProperty("VERSION_CODE", "1").toInt()
        versionName = versionProps.getProperty("VERSION_NAME", "1.0.0")
    }
}
```

#### Release Tracks

**1. Internal Testing Track**
```kotlin
// Quick internal testing for QA team
// - Instant access (no review)
// - Up to 100 testers
// - Email-based distribution
// - Useful for: daily builds, feature testing

// Fastlane configuration
lane :internal do
  gradle(
    task: "bundle",
    build_type: "Release",
    properties: {
      "android.injected.version.code" => number_of_commits,
      "android.injected.version.name" => get_version_name
    }
  )

  upload_to_play_store(
    track: 'internal',
    aab: 'app/build/outputs/bundle/release/app-release.aab',
    skip_upload_metadata: true,
    skip_upload_images: true,
    skip_upload_screenshots: true
  )
end
```

**2. Closed Testing (Alpha) Track**
```kotlin
// Closed testing with selected users
// - Up to 50,000 testers
// - Google account or email list
// - Opt-in via link
// - Useful for: beta features, early adopters

lane :alpha do
  gradle(task: "bundle", build_type: "Release")

  upload_to_play_store(
    track: 'alpha',
    aab: 'app/build/outputs/bundle/release/app-release.aab',
    rollout: '1.0', // Full rollout to alpha testers
    skip_upload_metadata: false,
    skip_upload_images: false
  )
end
```

**3. Open Testing (Beta) Track**
```kotlin
// Open testing - anyone can join
// - Unlimited testers
// - Public opt-in link
// - App Store listing badge
// - Useful for: public beta, stress testing

lane :beta do
  gradle(task: "bundle", build_type: "Release")

  upload_to_play_store(
    track: 'beta',
    aab: 'app/build/outputs/bundle/release/app-release.aab',
    rollout: '0.1', // 10% staged rollout
    skip_upload_metadata: false,
    skip_upload_images: false,
    skip_upload_screenshots: false
  )
end
```

**4. Production Track with Staged Rollout**
```kotlin
// Production release
// - All users
// - Staged rollout support
// - Full Play Store listing

lane :production do
  # Build release
  gradle(task: "bundle", build_type: "Release")

  # Upload to production with 5% rollout
  upload_to_play_store(
    track: 'production',
    aab: 'app/build/outputs/bundle/release/app-release.aab',
    rollout: '0.05', # Start with 5%
    skip_upload_metadata: false,
    skip_upload_images: false,
    skip_upload_screenshots: false,
    release_status: 'inProgress' # Staged rollout
  )
end

# Increase rollout percentage
lane :increase_rollout do |options|
  percentage = options[:percentage] || 0.5

  upload_to_play_store(
    track: 'production',
    rollout: percentage.to_s,
    skip_upload_apk: true,
    skip_upload_aab: true,
    skip_upload_metadata: true,
    skip_upload_images: true,
    skip_upload_screenshots: true
  )
end

# Complete rollout to 100%
lane :complete_rollout do
  upload_to_play_store(
    track: 'production',
    rollout: '1.0',
    skip_upload_apk: true,
    skip_upload_aab: true,
    skip_upload_metadata: true,
    skip_upload_images: true,
    skip_upload_screenshots: true
  )
end
```

#### Release Management

**1. Automated Release Pipeline**
```yaml
# .github/workflows/release.yml
name: Production Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Decode keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > upload-keystore.jks

      - name: Build Release Bundle
        env:
          UPLOAD_KEYSTORE_PASSWORD: ${{ secrets.UPLOAD_KEYSTORE_PASSWORD }}
          UPLOAD_KEY_ALIAS: ${{ secrets.UPLOAD_KEY_ALIAS }}
          UPLOAD_KEY_PASSWORD: ${{ secrets.UPLOAD_KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Upload to Play Store (Internal)
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
          status: completed

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            app/build/outputs/bundle/release/app-release.aab
            app/build/outputs/mapping/release/mapping.txt
          generate_release_notes: true
```

**2. Release Notes Management**
```kotlin
// buildSrc/src/main/kotlin/ReleaseNotesGenerator.kt
object ReleaseNotesGenerator {
    fun generate(
        version: String,
        language: String = "en-US"
    ): String {
        val changelog = readChangelog()
        val versionChanges = extractVersionChanges(changelog, version)

        return when (language) {
            "en-US" -> formatEnglish(versionChanges)
            "ru-RU" -> formatRussian(versionChanges)
            else -> formatEnglish(versionChanges)
        }
    }

    private fun readChangelog(): String {
        return File("CHANGELOG.md").readText()
    }

    private fun extractVersionChanges(changelog: String, version: String): List<String> {
        // Parse CHANGELOG.md and extract changes for specific version
        val versionRegex = "## \\[$version\\].*?(?=## |$)".toRegex(RegexOption.DOT_MATCHES_ALL)
        val match = versionRegex.find(changelog) ?: return emptyList()

        return match.value
            .lines()
            .drop(1) // Skip version header
            .filter { it.startsWith("- ") }
            .map { it.removePrefix("- ").trim() }
    }

    private fun formatEnglish(changes: List<String>): String {
        return buildString {
            appendLine("What's New:")
            appendLine()
            changes.forEach { change ->
                appendLine("• $change")
            }
        }
    }

    private fun formatRussian(changes: List<String>): String {
        // Translate or use pre-translated changelog
        return buildString {
            appendLine("Что нового:")
            appendLine()
            changes.forEach { change ->
                val translated = translateChange(change)
                appendLine("• $translated")
            }
        }
    }
}

// Gradle task to generate release notes
tasks.register("generateReleaseNotes") {
    doLast {
        val version = AppVersion.versionName
        val languages = listOf("en-US", "ru-RU", "de-DE", "fr-FR")

        languages.forEach { lang ->
            val notes = ReleaseNotesGenerator.generate(version, lang)
            val outputDir = file("distribution/release-notes/$lang")
            outputDir.mkdirs()
            File(outputDir, "default.txt").writeText(notes)
        }

        println("Release notes generated for version $version")
    }
}
```

#### A/B Testing with Firebase

**1. Remote Config for Feature Flags**
```kotlin
@Singleton
class FeatureFlagManager @Inject constructor(
    private val remoteConfig: FirebaseRemoteConfig,
    private val analytics: FirebaseAnalytics
) {
    suspend fun initialize() {
        remoteConfig.setConfigSettingsAsync(
            remoteConfigSettings {
                minimumFetchIntervalInSeconds = if (BuildConfig.DEBUG) {
                    0 // Instant fetch for debug
                } else {
                    3600 // 1 hour for production
                }
            }
        )

        // Set defaults
        remoteConfig.setDefaultsAsync(
            mapOf(
                FEATURE_NEW_CHECKOUT to false,
                FEATURE_REDESIGNED_HOME to false,
                FEATURE_PREMIUM_BADGE to true
            )
        )

        // Fetch and activate
        remoteConfig.fetchAndActivate().await()
    }

    fun isNewCheckoutEnabled(): Boolean {
        val enabled = remoteConfig.getBoolean(FEATURE_NEW_CHECKOUT)
        analytics.logEvent("feature_flag_checked") {
            param("flag_name", FEATURE_NEW_CHECKOUT)
            param("flag_value", enabled.toString())
        }
        return enabled
    }

    fun getCheckoutVariant(): String {
        return remoteConfig.getString(CONFIG_CHECKOUT_VARIANT)
    }

    companion object {
        private const val FEATURE_NEW_CHECKOUT = "feature_new_checkout"
        private const val FEATURE_REDESIGNED_HOME = "feature_redesigned_home"
        private const val FEATURE_PREMIUM_BADGE = "feature_premium_badge"
        private const val CONFIG_CHECKOUT_VARIANT = "checkout_variant"
    }
}
```

**2. A/B Test Implementation**
```kotlin
@Composable
fun CheckoutScreen(
    viewModel: CheckoutViewModel = hiltViewModel()
) {
    val variant by viewModel.checkoutVariant.collectAsState()

    when (variant) {
        "variant_a" -> CheckoutScreenVariantA()
        "variant_b" -> CheckoutScreenVariantB()
        else -> CheckoutScreenDefault()
    }

    // Track experiment exposure
    LaunchedEffect(variant) {
        viewModel.trackExperimentExposure(variant)
    }
}

@HiltViewModel
class CheckoutViewModel @Inject constructor(
    private val featureFlagManager: FeatureFlagManager,
    private val analytics: FirebaseAnalytics
) : ViewModel() {

    val checkoutVariant = MutableStateFlow(
        featureFlagManager.getCheckoutVariant()
    )

    fun trackExperimentExposure(variant: String) {
        analytics.logEvent("experiment_exposure") {
            param("experiment_name", "checkout_redesign")
            param("variant", variant)
        }
    }

    fun trackCheckoutCompleted(orderValue: Double) {
        analytics.logEvent("checkout_completed") {
            param("variant", checkoutVariant.value)
            param("order_value", orderValue)
        }
    }
}
```

#### Best Practices

1. **App Signing**:
   - Use Play App Signing
   - Keep upload key secure
   - Never commit keystores
   - Rotate keys when compromised
   - Backup keys securely

2. **Release Strategy**:
   - Start with internal track
   - Graduate to closed testing
   - Use open testing for public beta
   - Staged rollout to production (5% → 20% → 50% → 100%)
   - Monitor crash rates between increases

3. **Version Management**:
   - Use semantic versioning
   - Automate version bumping
   - Keep changelog updated
   - Tag releases in git
   - Archive release artifacts

4. **Bundle Optimization**:
   - Enable all splits
   - Use dynamic features for large modules
   - Test on multiple devices
   - Monitor bundle size
   - Analyze using bundletool

5. **Monitoring**:
   - Track crash-free rate
   - Monitor ANR rate
   - Watch Play Console vitals
   - Set up alerts for regressions
   - Use pre-launch reports

#### Common Pitfalls

1. **Keystore Loss**: No backup of keystore = permanent loss of app
2. **No Staged Rollout**: Issues affect all users immediately
3. **Missing ProGuard Mappings**: Can't deobfuscate crash reports
4. **Large Bundle Size**: Users won't download
5. **No Release Notes**: Users don't know what changed
6. **Ignoring Vitals**: App gets deprioritized in Play Store

### Summary

Google Play Store publishing requires comprehensive release management:
- **App Signing**: Use Play App Signing with secure keystore management
- **App Bundles**: Optimize delivery with splits and dynamic features
- **Release Tracks**: Internal → Alpha → Beta → Production
- **Staged Rollouts**: Gradual increase from 5% to 100%
- **A/B Testing**: Firebase Remote Config for experiments
- **Automation**: CI/CD pipelines for consistent releases

Key considerations: security, staged rollouts, monitoring, and automation.

---

# Вопрос (RU)
> 
Объясните процесс публикации в Google Play Store, треки релизов и стратегии подписи приложений. Как управлять app bundles, конфигурациями релизов и версиями? Каковы best practices для staged rollouts и A/B тестирования?

## Ответ (RU)
Публикация в Google Play Store включает комплексное управление релизами — от подписи приложения до поэтапного развертывания, с современными подходами через App Bundles и автоматизированные стратегии развертывания.

#### Стратегии подписи

**Play App Signing (рекомендуется)**:
- Google хранит app signing key
- Вы храните upload key
- Автоматическая оптимизация при публикации
- Возможность сброса upload key

**Безопасность**:
- Никогда не коммитьте keystore
- Используйте переменные окружения
- Храните резервные копии
- Используйте сильные пароли

#### App Bundles

**Преимущества**:
- Меньший размер скачивания (~35% экономия)
- Оптимизация по плотности, ABI, языку
- Dynamic Feature Modules
- On-demand установка модулей

**Dynamic Features**:
- Условная доставка (по API level, стране и т.д.)
- On-demand установка
- Instant delivery для маленьких модулей

#### Треки релизов

1. **Internal** (до 100 тестеров):
   - Мгновенный доступ
   - Без review
   - Для QA команды

2. **Closed Testing/Alpha** (до 50,000):
   - Закрытая группа
   - Opt-in через ссылку
   - Для early adopters

3. **Open Testing/Beta** (без лимита):
   - Публичная opt-in ссылка
   - Badge на странице в Store
   - Для публичного beta

4. **Production**:
   - Все пользователи
   - Staged rollout support
   - Monitoring и rollback

#### Staged Rollout

**Стратегия**:
- Начать с 5%
- Мониторить crash rate, ANR, reviews
- Увеличивать: 5% → 20% → 50% → 100%
- Halt при проблемах
- Автоматический rollback при критических метриках

#### A/B Тестирование

**Firebase Remote Config**:
- Feature flags
- Варианты UI
- Персонализация
- Real-time обновления

**Best Practices**:
- Измеряйте ключевые метрики
- Статистическая значимость
- Один тест за раз
- Документируйте результаты

### Резюме

Публикация в Google Play требует комплексного управления релизами:
- **App Signing**: Play App Signing с безопасным управлением ключами
- **App Bundles**: Оптимизация доставки через splits и dynamic features
- **Release Tracks**: Internal → Alpha → Beta → Production
- **Staged Rollouts**: Постепенное увеличение с 5% до 100%
- **A/B Testing**: Firebase Remote Config для экспериментов
- **Automation**: CI/CD пайплайны для консистентных релизов

Ключевые моменты: безопасность, поэтапное развертывание, мониторинг, автоматизация.

---

## Related Questions

### Related (Medium)
- [[q-internal-app-distribution--distribution--medium]] - Distribution
- [[q-app-store-optimization--distribution--medium]] - Distribution
- [[q-alternative-distribution--distribution--medium]] - Distribution
- [[q-android-app-bundles--android--easy]] - Distribution
