---
id: android-258
title: "Play Store Publishing / Публикация в Play Store"
aliases: [App Bundle, Google Play Publishing, Play Store Publishing, Staged Rollout, Публикация в Play Store]
topic: android
subtopics: [ab-testing, app-bundle, ci-cd, play-console]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/ab-testing, android/app-bundle, android/ci-cd, android/play-console, difficulty/medium, distribution, release-management]

---

# Вопрос (RU)

> Объясните процесс публикации в Google Play Store: треки релизов, стратегии подписи приложений, управление App Bundles и версиями. Каковы best practices для staged rollouts и A/B тестирования?

# Question (EN)

> Explain the Google Play Store publishing process: release tracks, app signing strategies, App `Bundle` and version management. What are best practices for staged rollouts and A/B testing?

---

## Ответ (RU)

**Суть**: Публикация в Play Store включает настройку подписи приложения, управление релизами через треки, оптимизацию доставки через App Bundles и постепенное развертывание с мониторингом.

### 1. Play App Signing

**✅ Рекомендуемый подход**:
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file("../keystore/upload-keystore.jks")
            storePassword = System.getenv("UPLOAD_KEYSTORE_PASSWORD")
            keyAlias = System.getenv("UPLOAD_KEY_ALIAS")
            keyPassword = System.getenv("UPLOAD_KEY_PASSWORD")

            enableV3Signing = true
            enableV4Signing = true
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

**Преимущества Play App Signing**:
- Google хранит app signing key (можно сбросить upload key)
- Автоматическая оптимизация APK
- Безопасное восстановление при компрометации ключа

**❌ Частые ошибки**:
- Коммит keystore в git → утечка ключей
- Отсутствие backup → потеря доступа к приложению
- Слабые пароли → компрометация

### 2. App `Bundle` Configuration

```kotlin
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }

    // Dynamic feature modules
    dynamicFeatures.addAll(
        setOf(":feature:premium", ":feature:camera")
    )
}
```

**Dynamic Feature доставка**:
```kotlin
class FeatureManager(context: Context) {
    private val splitInstallManager = SplitInstallManagerFactory.create(context)

    fun installFeature(moduleName: String, onProgress: (Int) -> Unit) {
        val request = SplitInstallRequest.newBuilder()
            .addModule(moduleName)
            .build()

        splitInstallManager.registerListener { state ->
            when (state.status()) {
                SplitInstallSessionStatus.DOWNLOADING -> {
                    val progress = (state.bytesDownloaded() * 100 /
                        state.totalBytesToDownload()).toInt()
                    onProgress(progress)
                }
                SplitInstallSessionStatus.INSTALLED -> {
                    // Готово к использованию
                }
            }
        }
        splitInstallManager.startInstall(request)
    }
}
```

### 3. Управление Версиями

**✅ Semantic Versioning**:
```kotlin
object AppVersion {
    private const val MAJOR = 2
    private const val MINOR = 5
    private const val PATCH = 3

    const val versionCode = MAJOR * 10000 + MINOR * 100 + PATCH
    const val versionName = "$MAJOR.$MINOR.$PATCH"
}

android {
    defaultConfig {
        versionCode = AppVersion.versionCode
        versionName = AppVersion.versionName
    }
}
```

### 4. Треки Релизов

| Трек | Тестеров | Review | Использование |
|------|----------|--------|---------------|
| Internal | до 100 | Нет | QA команда, daily builds |
| Closed (Alpha) | до 50K | Нет | Early adopters, beta features |
| Open (Beta) | ∞ | Нет | Публичный beta, stress testing |
| Production | ∞ | Да | Все пользователи |

**Автоматизация с Fastlane**:
```ruby
lane :production do
  gradle(task: "bundle", build_type: "Release")

  upload_to_play_store(
    track: 'production',
    aab: 'app/build/outputs/bundle/release/app-release.aab',
    rollout: '0.05' # Начать с 5%
  )
end

lane :increase_rollout do |options|
  upload_to_play_store(
    track: 'production',
    rollout: options[:percentage].to_s,
    skip_upload_aab: true
  )
end
```

### 5. Staged Rollout Стратегия

**✅ Рекомендуемый план**:
```
День 1:  5%  → мониторить crash rate, ANR
День 3:  20% → проверить reviews, vitals
День 5:  50% → финальная проверка
День 7:  100% → полный rollout
```

**Метрики для мониторинга**:
- Crash-free rate (должен быть >99.5%)
- ANR rate (<0.47% для Android 13+)
- Negative reviews spike
- Play Console vitals (bad behavior thresholds)

**❌ Halt rollout если**:
- Crash rate вырос на >0.5%
- ANR rate вырос на >0.2%
- Critical bug reports
- Negative reviews spike >20%

### 6. A/B Testing С Firebase

```kotlin
@Singleton
class FeatureFlagManager @Inject constructor(
    private val remoteConfig: FirebaseRemoteConfig,
    private val analytics: FirebaseAnalytics
) {
    suspend fun initialize() {
        remoteConfig.setDefaultsAsync(
            mapOf("feature_new_checkout" to false)
        )
        remoteConfig.fetchAndActivate().await()
    }

    fun isNewCheckoutEnabled(): Boolean {
        return remoteConfig.getBoolean("feature_new_checkout")
    }
}

@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel) {
    val variant by viewModel.checkoutVariant.collectAsState()

    when (variant) {
        "variant_a" -> CheckoutVariantA()
        "variant_b" -> CheckoutVariantB()
    }

    LaunchedEffect(variant) {
        viewModel.trackExperimentExposure(variant)
    }
}
```

### 7. CI/CD Pipeline

```yaml
# .github/workflows/release.yml
name: Production Release
on:
  push:
    tags: ['v*.*.*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > upload-keystore.jks

      - name: Build Bundle
        env:
          UPLOAD_KEYSTORE_PASSWORD: ${{ secrets.UPLOAD_KEYSTORE_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
```

**Best Practices**:

1. **Безопасность**:
   - ✅ Play App Signing (Google управляет signing key)
   - ✅ Переменные окружения для секретов
   - ✅ Backup keystore в безопасном месте
   - ❌ Никогда не коммитьте keystore в git

2. **Release стратегия**:
   - ✅ Internal → Closed → Open → Production
   - ✅ Staged rollout: 5% → 20% → 50% → 100%
   - ✅ Мониторить метрики между этапами
   - ❌ Не пропускайте staged rollout

3. **`Bundle` оптимизация**:
   - ✅ Включить все splits (language, density, ABI)
   - ✅ Dynamic features для больших модулей (>10MB)
   - ✅ Тестировать на разных устройствах
   - ❌ Не превышать 150MB initial download

4. **Мониторинг**:
   - ✅ Play Console vitals (crash rate, ANR)
   - ✅ Pre-launch reports
   - ✅ User reviews мониторинг
   - ✅ Analytics для A/B тестов

## Answer (EN)

**Core**: Play Store publishing involves app signing setup, release management through tracks, delivery optimization via App Bundles, and gradual rollouts with monitoring.

### 1. Play App Signing

**✅ Recommended approach**:
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file("../keystore/upload-keystore.jks")
            storePassword = System.getenv("UPLOAD_KEYSTORE_PASSWORD")
            keyAlias = System.getenv("UPLOAD_KEY_ALIAS")
            keyPassword = System.getenv("UPLOAD_KEY_PASSWORD")

            enableV3Signing = true
            enableV4Signing = true
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

**Play App Signing benefits**:
- Google manages app signing key (can reset upload key)
- Automatic APK optimization
- Secure recovery on key compromise

**❌ Common mistakes**:
- Committing keystore to git → key leakage
- No backup → loss of app access
- Weak passwords → compromise risk

### 2. App `Bundle` Configuration

```kotlin
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }

    // Dynamic feature modules
    dynamicFeatures.addAll(
        setOf(":feature:premium", ":feature:camera")
    )
}
```

**Dynamic Feature delivery**:
```kotlin
class FeatureManager(context: Context) {
    private val splitInstallManager = SplitInstallManagerFactory.create(context)

    fun installFeature(moduleName: String, onProgress: (Int) -> Unit) {
        val request = SplitInstallRequest.newBuilder()
            .addModule(moduleName)
            .build()

        splitInstallManager.registerListener { state ->
            when (state.status()) {
                SplitInstallSessionStatus.DOWNLOADING -> {
                    val progress = (state.bytesDownloaded() * 100 /
                        state.totalBytesToDownload()).toInt()
                    onProgress(progress)
                }
                SplitInstallSessionStatus.INSTALLED -> {
                    // Ready to use
                }
            }
        }
        splitInstallManager.startInstall(request)
    }
}
```

### 3. Version Management

**✅ Semantic Versioning**:
```kotlin
object AppVersion {
    private const val MAJOR = 2
    private const val MINOR = 5
    private const val PATCH = 3

    const val versionCode = MAJOR * 10000 + MINOR * 100 + PATCH
    const val versionName = "$MAJOR.$MINOR.$PATCH"
}

android {
    defaultConfig {
        versionCode = AppVersion.versionCode
        versionName = AppVersion.versionName
    }
}
```

### 4. Release Tracks

| Track | Testers | Review | Use Case |
|-------|---------|--------|----------|
| Internal | up to 100 | No | QA team, daily builds |
| Closed (Alpha) | up to 50K | No | Early adopters, beta features |
| Open (Beta) | ∞ | No | Public beta, stress testing |
| Production | ∞ | Yes | All users |

**Fastlane automation**:
```ruby
lane :production do
  gradle(task: "bundle", build_type: "Release")

  upload_to_play_store(
    track: 'production',
    aab: 'app/build/outputs/bundle/release/app-release.aab',
    rollout: '0.05' # Start with 5%
  )
end

lane :increase_rollout do |options|
  upload_to_play_store(
    track: 'production',
    rollout: options[:percentage].to_s,
    skip_upload_aab: true
  )
end
```

### 5. Staged Rollout Strategy

**✅ Recommended plan**:
```
Day 1:  5%  → monitor crash rate, ANR
Day 3:  20% → check reviews, vitals
Day 5:  50% → final verification
Day 7:  100% → complete rollout
```

**Metrics to monitor**:
- Crash-free rate (should be >99.5%)
- ANR rate (<0.47% for Android 13+)
- Negative reviews spike
- Play Console vitals (bad behavior thresholds)

**❌ Halt rollout if**:
- Crash rate increased by >0.5%
- ANR rate increased by >0.2%
- Critical bug reports
- Negative reviews spike >20%

### 6. A/B Testing with Firebase

```kotlin
@Singleton
class FeatureFlagManager @Inject constructor(
    private val remoteConfig: FirebaseRemoteConfig,
    private val analytics: FirebaseAnalytics
) {
    suspend fun initialize() {
        remoteConfig.setDefaultsAsync(
            mapOf("feature_new_checkout" to false)
        )
        remoteConfig.fetchAndActivate().await()
    }

    fun isNewCheckoutEnabled(): Boolean {
        return remoteConfig.getBoolean("feature_new_checkout")
    }
}

@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel) {
    val variant by viewModel.checkoutVariant.collectAsState()

    when (variant) {
        "variant_a" -> CheckoutVariantA()
        "variant_b" -> CheckoutVariantB()
    }

    LaunchedEffect(variant) {
        viewModel.trackExperimentExposure(variant)
    }
}
```

### 7. CI/CD Pipeline

```yaml
# .github/workflows/release.yml
name: Production Release
on:
  push:
    tags: ['v*.*.*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > upload-keystore.jks

      - name: Build Bundle
        env:
          UPLOAD_KEYSTORE_PASSWORD: ${{ secrets.UPLOAD_KEYSTORE_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
```

**Best Practices**:

1. **Security**:
   - ✅ Play App Signing (Google manages signing key)
   - ✅ Environment variables for secrets
   - ✅ Backup keystore securely
   - ❌ Never commit keystore to git

2. **Release strategy**:
   - ✅ Internal → Closed → Open → Production
   - ✅ Staged rollout: 5% → 20% → 50% → 100%
   - ✅ Monitor metrics between stages
   - ❌ Don't skip staged rollout

3. **`Bundle` optimization**:
   - ✅ Enable all splits (language, density, ABI)
   - ✅ Dynamic features for large modules (>10MB)
   - ✅ Test on multiple devices
   - ❌ Don't exceed 150MB initial download

4. **Monitoring**:
   - ✅ Play Console vitals (crash rate, ANR)
   - ✅ Pre-launch reports
   - ✅ User reviews monitoring
   - ✅ Analytics for A/B tests

## Follow-ups

1. How do you handle rollback scenarios if critical issues are discovered during staged rollout?
2. What are the best practices for managing ProGuard mapping files across multiple releases?
3. How do you implement conditional delivery for dynamic features based on device capabilities?
4. What strategies exist for testing App Bundles locally before uploading to Play Console?
5. How do you manage multi-language release notes generation and localization in CI/CD?

## References

-  - App signing and keystore management
-  - Continuous integration and deployment
-  - Feature flag patterns
- [Play Console Documentation](https://developer.android.com/distribute/console)
- [App `Bundle` Guide](https://developer.android.com/guide/app-bundle)
- [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)

## Related Questions

### Prerequisites (Easy)
- [[q-android-app-bundles--android--easy]] - App `Bundle` basics and benefits

### Related (Medium)
- [[q-app-store-optimization--android--medium]] - ASO strategies and best practices
-  - In-app update implementation
-  - Build configuration management

### Advanced (Hard)
- [[q-kmm-architecture--android--hard]] - Complex modularization with dynamic features
-  - Enterprise deployment strategies
