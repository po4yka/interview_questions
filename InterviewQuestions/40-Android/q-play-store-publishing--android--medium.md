---
id: android-258
title: "Play Store Publishing / Публикация в Play Store"
aliases: [App Bundle, Google Play Publishing, Play Store Publishing, Staged Rollout, Публикация в Play Store]
topic: android
subtopics: [ab-testing, app-bundle, play-console]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-app-bundle, q-android-app-bundles--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [android/ab-testing, android/app-bundle, android/play-console, difficulty/medium, distribution, release-management]

date created: Saturday, November 1st 2025, 1:03:34 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)

> Объясните процесс публикации в Google Play Store: треки релизов, стратегии подписи приложений, управление App Bundles и версиями. Каковы best practices для staged rollouts и A/B тестирования?

# Question (EN)

> Explain the Google Play Store publishing process: release tracks, app signing strategies, App `Bundle` and version management. What are best practices for staged rollouts and A/B testing?

---

## Ответ (RU)

**Суть**: Публикация в Play Store включает настройку подписи приложения (включая Play App Signing и upload key), управление релизами через треки, оптимизацию доставки через App Bundles и постепенное развертывание с мониторингом.

### 1. Play App Signing

**✅ Рекомендуемый подход (upload key локально, signing key у Google)**:
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // Upload key, используемый для подписи артефактов перед загрузкой в Play
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
- Google хранит основной app signing key (можно сбросить upload key при компрометации)
- Google генерирует и раздаёт оптимизированные APK из App `Bundle` (Split APKs / APKs по конфигурации)
- Возможность безопасного восстановления при компрометации upload key (без потери подписи приложения)

**❌ Частые ошибки**:
- Коммит keystore в git → утечка ключей
- Отсутствие backup upload keystore и учётных данных → сложности с управлением релизами
- Слабые пароли → компрометация ключей

### 2. App `Bundle` Configuration

```kotlin
android {
    // Пример конфигурации сплитов для App Bundle (синтаксис может отличаться в новых версиях AGP)
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
            if (!state.moduleNames().contains(moduleName)) return@registerListener

            when (state.status()) {
                SplitInstallSessionStatus.DOWNLOADING -> {
                    val totalBytes = state.totalBytesToDownload()
                    if (totalBytes > 0L) {
                        val progress = (state.bytesDownloaded() * 100 /
                            totalBytes).toInt()
                        onProgress(progress)
                    }
                }
                SplitInstallSessionStatus.INSTALLED -> {
                    // Готово к использованию
                }
                SplitInstallSessionStatus.REQUIRES_USER_CONFIRMATION -> {
                    // Требуется запросить согласие пользователя через startConfirmationDialogForResult / соответствующий API
                }
                SplitInstallSessionStatus.FAILED -> {
                    // Обработать ошибку state.errorCode()
                }
                SplitInstallSessionStatus.CANCELED -> {
                    // Обработать отмену установки
                }
                else -> {
                    // Обработка прочих статусов при необходимости
                }
            }
        }

        splitInstallManager.startInstall(request)
    }
}
```

### 3. Управление Версиями

**✅ Semantic Versioning (пример формулы для versionCode)**:
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

Важно: versionCode должен строго увеличиваться между релизами.

### 4. Треки Релизов

| Трек | Тестеров | Review | Использование |
|------|----------|--------|---------------|
| Internal | до 100 | Обычно быстрее, возможна проверка политик | QA команда, daily builds |
| Closed (Alpha) | до 50K | Проверка на соответствие требованиям может применяться | Early adopters, beta features |
| Open (Beta) | ∞ | Может применяться review и проверки | Публичный beta, нагрузочное тестирование |
| Production | ∞ | Полный review/политики | Все пользователи |

**Автоматизация с Fastlane**:
```ruby
lane :production do
  gradle(task: "bundle", build_type: "Release")

  upload_to_play_store(
    track: 'production',
    aab: 'app/build/outputs/bundle/release/app-release.aab',
    rollout: 0.05 # Начать с 5% (пример)
  )
end

lane :increase_rollout do |options|
  upload_to_play_store(
    track: 'production',
    rollout: options[:percentage],
    skip_upload_aab: true
  )
end
```

### 5. Staged Rollout Стратегия

**✅ Примерный план** (адаптируйте под метрики продукта):
```
День 1:  5%  → мониторить crash rate, ANR, ключевые бизнес-метрики
День 3:  20% → проверить reviews, vitals, технические и продуктовые сигналы
День 5:  50% → финальная проверка стабильности
День 7:  100% → полный rollout
```

**Метрики для мониторинга**:
- Crash-free rate (цель: >99.5%, ориентируйтесь на Play Console bad behavior thresholds)
- ANR rate (держать ниже порогов Play Console для "bad behavior", метрика зависит от версии и категории)
- Спайки негативных отзывов
- Play Console vitals, технические ошибки, бизнес-метрики

**❌ Остановить или откатить rollout если (примерные пороги)**:
- Crash rate вырос относительно предыдущей версии более чем на ~0.5 п.п.
- ANR rate вырос более чем на ~0.2 п.п. или приближается к bad behavior thresholds
- Появились критические баги (платежи, логин, потеря данных)
- Наблюдается значимый (>~20%) рост негативных отзывов, связанных с новым релизом

### 6. A/B Testing С Firebase

Для A/B тестов обычно используют Firebase Remote Config совместно с Firebase A/B Testing (эксперименты настраиваются в консоли, а приложение читает значения флагов).

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

Важно: сегментацию, распределение трафика и цели эксперимента настраиваем в Firebase Console, а в коде только считываем значения Remote Config / флагов и логируем события.

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
          UPLOAD_KEY_ALIAS: ${{ secrets.UPLOAD_KEY_ALIAS }}
          UPLOAD_KEY_PASSWORD: ${{ secrets.UPLOAD_KEY_PASSWORD }}
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
   - ✅ Play App Signing (Google управляет основным signing key)
   - ✅ Использовать upload key отдельно от signing key
   - ✅ Переменные окружения / секреты CI для хранения чувствительных данных
   - ✅ Backup upload keystore и доступов в безопасном месте
   - ❌ Никогда не коммитьте keystore и сервисные ключи в git

2. **Release стратегия**:
   - ✅ Internal → Closed → Open → Production (по необходимости)
   - ✅ Staged rollout: например 5% → 20% → 50% → 100%
   - ✅ Мониторить метрики между этапами и быть готовым остановить rollout
   - ❌ Не пропускайте staged rollout для крупных изменений

3. **`Bundle` оптимизация**:
   - ✅ Включить splits (language, density, ABI) для уменьшения размера доставляемых APK
   - ✅ Использовать Dynamic Feature Modules для тяжёлых/редко используемых фич
   - ✅ Тестировать App `Bundle` и dynamic features на разных устройствах и конфигурациях
   - ❌ Учитывать ограничения размера: итоговые APK/установки не должны превышать лимитов Play

4. **Мониторинг**:
   - ✅ Play Console vitals (crash rate, ANR, excessive wakeups и т.п.)
   - ✅ Pre-launch reports
   - ✅ Мониторинг пользовательских отзывов
   - ✅ Analytics / Firebase для оценки A/B тестов и поведенческих метрик

## Answer (EN)

**Core**: Play Store publishing involves app signing setup (including Play App Signing with a separate upload key), release management through tracks, delivery optimization via App Bundles, and gradual rollouts with monitoring.

### 1. Play App Signing

**✅ Recommended approach (upload key locally, signing key managed by Google)**:
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // Upload key used to sign artifacts before uploading to Play
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
- Google stores and manages the primary app signing key (you can reset the upload key if compromised)
- Google generates and serves optimized APKs from your App `Bundle` (configuration/split APKs)
- Safer recovery if the upload key is compromised without losing your package signature

**❌ Common mistakes**:
- Committing keystore to git → key leakage
- No backup of upload keystore/credentials → operational risk
- Weak passwords → increased compromise risk

### 2. App `Bundle` Configuration

```kotlin
android {
    // Example split configuration for App Bundle (syntax may differ in newer AGP versions)
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
            if (!state.moduleNames().contains(moduleName)) return@registerListener

            when (state.status()) {
                SplitInstallSessionStatus.DOWNLOADING -> {
                    val totalBytes = state.totalBytesToDownload()
                    if (totalBytes > 0L) {
                        val progress = (state.bytesDownloaded() * 100 /
                            totalBytes).toInt()
                        onProgress(progress)
                    }
                }
                SplitInstallSessionStatus.INSTALLED -> {
                    // Ready to use
                }
                SplitInstallSessionStatus.REQUIRES_USER_CONFIRMATION -> {
                    // Request user confirmation via startConfirmationDialogForResult / relevant API
                }
                SplitInstallSessionStatus.FAILED -> {
                    // Handle error via state.errorCode()
                }
                SplitInstallSessionStatus.CANCELED -> {
                    // Handle cancellation
                }
                else -> {
                    // Handle other statuses as needed
                }
            }
        }

        splitInstallManager.startInstall(request)
    }
}
```

### 3. Version Management

**✅ Semantic Versioning (example versionCode formula)**:
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

Important: versionCode must strictly increase between releases.

### 4. Release Tracks

| Track | Testers | Review | Use Case |
|-------|---------|--------|----------|
| Internal | up to 100 | Typically faster, policy checks may still apply | QA team, daily builds |
| Closed (Alpha) | up to 50K | Policy/compliance checks may apply | Early adopters, beta features |
| Open (Beta) | ∞ | Review/checks may apply | Public beta, stress testing |
| Production | ∞ | Full policy/review | All users |

**Fastlane automation**:
```ruby
lane :production do
  gradle(task: "bundle", build_type: "Release")

  upload_to_play_store(
    track: 'production',
    aab: 'app/build/outputs/bundle/release/app-release.aab',
    rollout: 0.05 # Start with 5% (example)
  )
end

lane :increase_rollout do |options|
  upload_to_play_store(
    track: 'production',
    rollout: options[:percentage],
    skip_upload_aab: true
  )
end
```

### 5. Staged Rollout Strategy

**✅ Example plan** (tune to your product and risk):
```
Day 1:  5%  → monitor crash rate, ANR, key metrics
Day 3:  20% → check reviews, vitals, technical and business signals
Day 5:  50% → final stability verification
Day 7:  100% → complete rollout
```

**Metrics to monitor**:
- Crash-free rate (target >99.5%, use Play Console bad behavior thresholds as guidance)
- ANR rate (keep below Play Console "bad behavior" thresholds; exact values depend on OS versions/category)
- Spikes in negative reviews
- Play Console vitals, technical errors, key product metrics

**❌ Halt or roll back rollout if (example guardrails)**:
- Crash rate increases vs previous version by more than ~0.5 percentage points
- ANR rate increases by more than ~0.2 percentage points or approaches bad behavior thresholds
- Critical bug reports (login, payments, data loss, etc.)
- Significant (>~20%) spike in negative reviews clearly tied to the new release

### 6. A/B Testing with Firebase

Typically use Firebase Remote Config together with Firebase A/B Testing: experiments are defined in the Firebase Console; the app simply reads Remote Config values / flags.

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

Key point: audience targeting, traffic allocation, and goals are configured in the Firebase Console; code should be responsible for reading flags and logging exposures/events.

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
          UPLOAD_KEY_ALIAS: ${{ secrets.UPLOAD_KEY_ALIAS }}
          UPLOAD_KEY_PASSWORD: ${{ secrets.UPLOAD_KEY_PASSWORD }}
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
   - ✅ Use Play App Signing (Google manages the primary signing key)
   - ✅ Use a dedicated upload key separate from the app signing key
   - ✅ Use environment/CI secrets for sensitive data
   - ✅ Store upload keystore and credentials securely with backups
   - ❌ Never commit keystores or service account keys to git

2. **Release strategy**:
   - ✅ Use Internal → Closed → Open → Production when appropriate
   - ✅ Use staged rollout (e.g., 5% → 20% → 50% → 100%)
   - ✅ Monitor metrics between stages and be ready to pause/rollback
   - ❌ Avoid skipping staged rollout for risky releases

3. **`Bundle` optimization**:
   - ✅ Enable splits (language, density, ABI) to reduce delivered APK size
   - ✅ Use Dynamic Feature Modules for large/optional features
   - ✅ Test App Bundles and dynamic features on multiple devices/configurations
   - ❌ Respect Google Play size limits: ensure delivered APK/install size stays within allowed limits

4. **Monitoring**:
   - ✅ Use Play Console vitals (crash rate, ANR, wakelocks, etc.)
   - ✅ Use Pre-launch reports
   - ✅ Monitor user reviews
   - ✅ Use analytics/Firebase to measure A/B test impact and key behaviors

## Дополнительные Вопросы (RU)

1. Как вы обрабатываете сценарии отката, если во время staged rollout обнаруживаются критические проблемы?
2. Как организовать управление файлами ProGuard mapping между несколькими релизами?
3. Как реализовать условную доставку dynamic feature-модулей в зависимости от возможностей устройства?
4. Какие стратегии вы используете для локального тестирования App Bundles до загрузки в Play Console?
5. Как вы автоматизируете генерацию и локализацию release notes в рамках CI/CD?

## Follow-ups

1. How do you handle rollback scenarios if critical issues are discovered during a staged rollout?
2. What are best practices for managing ProGuard mapping files across multiple releases?
3. How do you implement conditional delivery for dynamic features based on device capabilities?
4. What strategies exist for testing App Bundles locally before uploading to Play Console?
5. How do you manage multi-language release notes generation and localization in CI/CD?

## Ссылки (RU)

- [[c-app-bundle]]
- Play Console документация: https://developer.android.com/distribute/console
- Руководство по App `Bundle`: https://developer.android.com/guide/app-bundle
- Play App Signing: https://support.google.com/googleplay/android-developer/answer/9842756

## References

- [[c-app-bundle]]
- Play Console Documentation: https://developer.android.com/distribute/console
- App `Bundle` Guide: https://developer.android.com/guide/app-bundle
- Play App Signing: https://support.google.com/googleplay/android-developer/answer/9842756

## Связанные Вопросы (RU)

### База (Easy)
- [[q-android-app-bundles--android--easy]] - Основы и преимущества App `Bundle`

### Связанные (Medium)
- [[q-app-store-optimization--android--medium]] - Стратегии и практики ASO

### Продвинутые (Hard)
- [[q-kmm-architecture--android--hard]] - Сложная модульная архитектура с dynamic features

## Related Questions

### Prerequisites (Easy)
- [[q-android-app-bundles--android--easy]] - App `Bundle` basics and benefits

### Related (Medium)
- [[q-app-store-optimization--android--medium]] - ASO strategies and best practices

### Advanced (Hard)
- [[q-kmm-architecture--android--hard]] - Complex modularization with dynamic features
