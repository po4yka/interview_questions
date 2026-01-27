---
id: android-cicd-005
title: Play Store Deployment and Staged Rollout / Публикация в Play Store и Поэтапное
  Развёртывание
aliases:
- Play Store Deployment
- Публикация в Play Store и Поэтапное Развёртывание
topic: android
subtopics:
- cicd
- deployment
- play-store
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-github-actions-android--cicd--medium
- q-app-distribution--cicd--medium
- q-signing-in-ci--cicd--hard
created: 2026-01-23
updated: 2026-01-23
sources:
- https://developer.android.com/distribute
- https://support.google.com/googleplay/android-developer/answer/6346149
tags:
- android/cicd
- android/deployment
- difficulty/medium
- play-store
- staged-rollout
anki_cards:
- slug: android-cicd-005-0-en
  language: en
- slug: android-cicd-005-0-ru
  language: ru
---
# Вопрос (RU)

> Как автоматизировать публикацию в Google Play Store с использованием staged rollout?

# Question (EN)

> How do you automate Google Play Store deployment with staged rollout?

## Ответ (RU)

Google Play Console предоставляет мощные инструменты для управляемой публикации: **release tracks** (треки релизов), **staged rollout** (поэтапное развёртывание) и **Play App Signing**. Автоматизация доступна через Google Play Developer API или Gradle плагины.

### Release Tracks

Play Console имеет несколько треков:

| Трек | Назначение | Аудитория |
|------|------------|-----------|
| Internal | Быстрые тесты (минуты) | До 100 внутренних тестеров |
| Closed | Закрытая бета | Приглашённые по email/группы |
| Open | Открытая бета | Любой в Play Store |
| Production | Публичная версия | Все пользователи |

### Staged Rollout

Поэтапное развёртывание позволяет выпускать обновление для части пользователей:

```
5% -> 10% -> 25% -> 50% -> 100%
```

#### Преимущества

- **Раннее обнаружение проблем** — crash rate, ANR, отзывы
- **Ограничение ущерба** — проблема затронет мало пользователей
- **A/B тестирование** — сравнение метрик старой и новой версий
- **Возврат** — можно остановить rollout и откатиться

### Автоматизация с Gradle Play Publisher

```kotlin
// app/build.gradle.kts
plugins {
    id("com.github.triplet.play") version "3.9.1"
}

play {
    // Service account credentials
    serviceAccountCredentials.set(file("play-service-account.json"))

    // Default track
    track.set("production")

    // Staged rollout percentage (0.0 to 1.0)
    userFraction.set(0.1)  // 10% rollout

    // Use App Bundles
    defaultToAppBundles.set(true)

    // Version code strategy
    resolutionStrategy.set(ResolutionStrategy.AUTO)
}
```

#### Команды

```bash
# Публикация в production с 10% rollout
./gradlew publishBundle

# Публикация в internal testing
./gradlew publishBundle --track internal

# Увеличение rollout до 50%
./gradlew promoteArtifact --update 0.5

# Полный rollout (100%)
./gradlew promoteArtifact --update 1.0

# Promote из internal в production
./gradlew promoteArtifact --from-track internal --track production

# Halt rollout (остановка)
./gradlew publishBundle --user-fraction 0.0
```

### GitHub Actions Workflow

```yaml
name: Play Store Release

on:
  push:
    tags:
      - 'v*'

env:
  JAVA_VERSION: '17'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Decode Keystore
        run: echo ${{ secrets.KEYSTORE_BASE64 }} | base64 -d > app/release.keystore

      - name: Decode Play Store Credentials
        run: echo ${{ secrets.PLAY_STORE_CREDENTIALS }} | base64 -d > play-service-account.json

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Build Release Bundle
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Deploy to Production (10% rollout)
        run: ./gradlew publishBundle --track production --user-fraction 0.1

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: app/build/outputs/bundle/release/app-release.aab
          body: |
            Release ${{ steps.version.outputs.VERSION }}
            Deployed to 10% of users
```

### Стратегия Релизов

```yaml
# .github/workflows/release-strategy.yml
name: Release Strategy

on:
  workflow_dispatch:
    inputs:
      action:
        description: 'Release action'
        required: true
        type: choice
        options:
          - deploy-internal
          - promote-to-closed
          - promote-to-production
          - increase-rollout
          - full-rollout
          - halt-rollout
      rollout_percentage:
        description: 'Rollout percentage (for increase-rollout)'
        required: false
        default: '0.25'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup
        # ... setup steps ...

      - name: Deploy to Internal
        if: ${{ github.event.inputs.action == 'deploy-internal' }}
        run: ./gradlew publishBundle --track internal

      - name: Promote to Closed
        if: ${{ github.event.inputs.action == 'promote-to-closed' }}
        run: ./gradlew promoteArtifact --from-track internal --track alpha

      - name: Promote to Production
        if: ${{ github.event.inputs.action == 'promote-to-production' }}
        run: ./gradlew promoteArtifact --from-track alpha --track production --user-fraction 0.05

      - name: Increase Rollout
        if: ${{ github.event.inputs.action == 'increase-rollout' }}
        run: ./gradlew promoteArtifact --update ${{ github.event.inputs.rollout_percentage }}

      - name: Full Rollout
        if: ${{ github.event.inputs.action == 'full-rollout' }}
        run: ./gradlew promoteArtifact --update 1.0

      - name: Halt Rollout
        if: ${{ github.event.inputs.action == 'halt-rollout' }}
        run: ./gradlew promoteArtifact --update 0.0
```

### Play App Signing

Google рекомендует использовать Play App Signing, где Google управляет ключом подписи:

```
Developer          Google Play
    |                   |
Upload Key -----> Play App Signing
    |                   |
    |            Signing Key
    |                   |
    +------ AAB ------->|
                        |
                   APK (signed)
                        |
                   Users
```

#### Преимущества

- **Безопасность** — ключ подписи никогда не покидает Google
- **Восстановление** — можно сбросить upload key при утере
- **App Bundle** — оптимизированная доставка

#### Настройка в build.gradle.kts

```kotlin
android {
    signingConfigs {
        create("release") {
            // Это upload key, не signing key
            storeFile = file(System.getenv("UPLOAD_KEYSTORE_PATH") ?: "upload.keystore")
            storePassword = System.getenv("UPLOAD_KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("UPLOAD_KEY_ALIAS") ?: ""
            keyPassword = System.getenv("UPLOAD_KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### Мониторинг и Откат

#### Автоматический Мониторинг

```yaml
# Проверка crash rate после деплоя
- name: Wait and Check Crash Rate
  run: |
    sleep 3600  # Wait 1 hour
    CRASH_RATE=$(curl -s "$FIREBASE_CRASHLYTICS_API/crash-rate")
    if (( $(echo "$CRASH_RATE > 0.5" | bc -l) )); then
      echo "High crash rate detected, halting rollout"
      ./gradlew promoteArtifact --update 0.0
      exit 1
    fi
```

#### Ручной Откат

```bash
# Остановить текущий rollout
./gradlew promoteArtifact --update 0.0

# Откатиться к предыдущей версии
./gradlew promoteArtifact --from-track archive --track production
```

### What's New (Release Notes)

```
whatsnew/
├── en-US
│   └── default.txt
├── ru-RU
│   └── default.txt
└── de-DE
    └── default.txt
```

```kotlin
// build.gradle.kts
play {
    releaseNotesDir.set(file("whatsnew"))
}
```

### Настройка Service Account

1. **Создание Service Account**:
   - Google Cloud Console -> IAM & Admin -> Service Accounts
   - Create service account
   - Grant role: "Service Account User"

2. **Настройка в Play Console**:
   - Play Console -> Settings -> API access
   - Link Google Cloud project
   - Grant access to service account

3. **Разрешения**:
   - View app info and download bulk reports
   - Manage production releases
   - Manage testing track releases

### Резюме Workflow

```
1. Build & Test (CI)
        |
2. Deploy to Internal Testing
        |
3. QA Validation (manual)
        |
4. Promote to Closed Beta
        |
5. Beta Testing (1-2 weeks)
        |
6. Promote to Production (5%)
        |
7. Monitor Metrics (1-3 days)
        |
8. Increase Rollout (25% -> 50% -> 100%)
```

## Answer (EN)

Google Play Console provides powerful tools for managed deployment: **release tracks**, **staged rollout**, and **Play App Signing**. Automation is available through Google Play Developer API or Gradle plugins.

### Release Tracks

Play Console has multiple tracks:

| Track | Purpose | Audience |
|-------|---------|----------|
| Internal | Quick tests (minutes) | Up to 100 internal testers |
| Closed | Closed beta | Invited via email/groups |
| Open | Open beta | Anyone in Play Store |
| Production | Public release | All users |

### Staged Rollout

Staged rollout allows releasing updates to a portion of users:

```
5% -> 10% -> 25% -> 50% -> 100%
```

#### Benefits

- **Early problem detection** — crash rate, ANR, reviews
- **Limited damage** — issues affect fewer users
- **A/B testing** — compare old vs new version metrics
- **Rollback** — can halt rollout and revert

### Automation with Gradle Play Publisher

```kotlin
// app/build.gradle.kts
plugins {
    id("com.github.triplet.play") version "3.9.1"
}

play {
    // Service account credentials
    serviceAccountCredentials.set(file("play-service-account.json"))

    // Default track
    track.set("production")

    // Staged rollout percentage (0.0 to 1.0)
    userFraction.set(0.1)  // 10% rollout

    // Use App Bundles
    defaultToAppBundles.set(true)

    // Version code strategy
    resolutionStrategy.set(ResolutionStrategy.AUTO)
}
```

#### Commands

```bash
# Publish to production with 10% rollout
./gradlew publishBundle

# Publish to internal testing
./gradlew publishBundle --track internal

# Increase rollout to 50%
./gradlew promoteArtifact --update 0.5

# Full rollout (100%)
./gradlew promoteArtifact --update 1.0

# Promote from internal to production
./gradlew promoteArtifact --from-track internal --track production

# Halt rollout
./gradlew publishBundle --user-fraction 0.0
```

### GitHub Actions Workflow

```yaml
name: Play Store Release

on:
  push:
    tags:
      - 'v*'

env:
  JAVA_VERSION: '17'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Decode Keystore
        run: echo ${{ secrets.KEYSTORE_BASE64 }} | base64 -d > app/release.keystore

      - name: Decode Play Store Credentials
        run: echo ${{ secrets.PLAY_STORE_CREDENTIALS }} | base64 -d > play-service-account.json

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Build Release Bundle
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Deploy to Production (10% rollout)
        run: ./gradlew publishBundle --track production --user-fraction 0.1

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: app/build/outputs/bundle/release/app-release.aab
          body: |
            Release ${{ steps.version.outputs.VERSION }}
            Deployed to 10% of users
```

### Release Strategy

```yaml
# .github/workflows/release-strategy.yml
name: Release Strategy

on:
  workflow_dispatch:
    inputs:
      action:
        description: 'Release action'
        required: true
        type: choice
        options:
          - deploy-internal
          - promote-to-closed
          - promote-to-production
          - increase-rollout
          - full-rollout
          - halt-rollout
      rollout_percentage:
        description: 'Rollout percentage (for increase-rollout)'
        required: false
        default: '0.25'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup
        # ... setup steps ...

      - name: Deploy to Internal
        if: ${{ github.event.inputs.action == 'deploy-internal' }}
        run: ./gradlew publishBundle --track internal

      - name: Promote to Closed
        if: ${{ github.event.inputs.action == 'promote-to-closed' }}
        run: ./gradlew promoteArtifact --from-track internal --track alpha

      - name: Promote to Production
        if: ${{ github.event.inputs.action == 'promote-to-production' }}
        run: ./gradlew promoteArtifact --from-track alpha --track production --user-fraction 0.05

      - name: Increase Rollout
        if: ${{ github.event.inputs.action == 'increase-rollout' }}
        run: ./gradlew promoteArtifact --update ${{ github.event.inputs.rollout_percentage }}

      - name: Full Rollout
        if: ${{ github.event.inputs.action == 'full-rollout' }}
        run: ./gradlew promoteArtifact --update 1.0

      - name: Halt Rollout
        if: ${{ github.event.inputs.action == 'halt-rollout' }}
        run: ./gradlew promoteArtifact --update 0.0
```

### Play App Signing

Google recommends Play App Signing where Google manages the signing key:

```
Developer          Google Play
    |                   |
Upload Key -----> Play App Signing
    |                   |
    |            Signing Key
    |                   |
    +------ AAB ------->|
                        |
                   APK (signed)
                        |
                   Users
```

#### Benefits

- **Security** — signing key never leaves Google
- **Recovery** — can reset upload key if lost
- **App Bundle** — optimized delivery

#### Configuration in build.gradle.kts

```kotlin
android {
    signingConfigs {
        create("release") {
            // This is upload key, not signing key
            storeFile = file(System.getenv("UPLOAD_KEYSTORE_PATH") ?: "upload.keystore")
            storePassword = System.getenv("UPLOAD_KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("UPLOAD_KEY_ALIAS") ?: ""
            keyPassword = System.getenv("UPLOAD_KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### Monitoring and Rollback

#### Automated Monitoring

```yaml
# Check crash rate after deploy
- name: Wait and Check Crash Rate
  run: |
    sleep 3600  # Wait 1 hour
    CRASH_RATE=$(curl -s "$FIREBASE_CRASHLYTICS_API/crash-rate")
    if (( $(echo "$CRASH_RATE > 0.5" | bc -l) )); then
      echo "High crash rate detected, halting rollout"
      ./gradlew promoteArtifact --update 0.0
      exit 1
    fi
```

#### Manual Rollback

```bash
# Halt current rollout
./gradlew promoteArtifact --update 0.0

# Rollback to previous version
./gradlew promoteArtifact --from-track archive --track production
```

### What's New (Release Notes)

```
whatsnew/
├── en-US
│   └── default.txt
├── ru-RU
│   └── default.txt
└── de-DE
    └── default.txt
```

```kotlin
// build.gradle.kts
play {
    releaseNotesDir.set(file("whatsnew"))
}
```

### Service Account Setup

1. **Create Service Account**:
   - Google Cloud Console -> IAM & Admin -> Service Accounts
   - Create service account
   - Grant role: "Service Account User"

2. **Configure in Play Console**:
   - Play Console -> Settings -> API access
   - Link Google Cloud project
   - Grant access to service account

3. **Permissions**:
   - View app info and download bulk reports
   - Manage production releases
   - Manage testing track releases

### Workflow Summary

```
1. Build & Test (CI)
        |
2. Deploy to Internal Testing
        |
3. QA Validation (manual)
        |
4. Promote to Closed Beta
        |
5. Beta Testing (1-2 weeks)
        |
6. Promote to Production (5%)
        |
7. Monitor Metrics (1-3 days)
        |
8. Increase Rollout (25% -> 50% -> 100%)
```

## Дополнительные Вопросы (RU)

1. Как обрабатывать hotfix релизы, которым нужно пропустить staged rollout?
2. Какие метрики следует отслеживать во время staged rollout?
3. Как координировать релизы между несколькими приложениями/модулями?
4. В чём разница между остановкой и отменой rollout?

## Follow-ups

1. How do you handle hotfix releases that need to skip staged rollout?
2. What metrics should you monitor during staged rollout?
3. How do you coordinate releases across multiple apps/modules?
4. What's the difference between halting and reversing a rollout?

## Ссылки (RU)

- [Play Console Release Tracks](https://support.google.com/googleplay/android-developer/answer/6346149)
- [Staged Rollouts](https://support.google.com/googleplay/android-developer/answer/6346149#staged)
- [Play App Signing](https://developer.android.com/studio/publish/app-signing)

## References

- [Play Console Release Tracks](https://support.google.com/googleplay/android-developer/answer/6346149)
- [Staged Rollouts](https://support.google.com/googleplay/android-developer/answer/6346149#staged)
- [Play App Signing](https://developer.android.com/studio/publish/app-signing)
- [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-signing-in-ci--cicd--hard]] — Безопасное подписание
- [[q-app-distribution--cicd--medium]] — Распределение приложений

### Похожие
- [[q-github-actions-android--cicd--medium]] — GitHub Actions
- [[q-build-variants-flavors--cicd--medium]] — Варианты сборки

### Продвинутое
- [[q-gradle-build-cache--cicd--medium]] — Оптимизация сборки

## Related Questions

### Prerequisites
- [[q-signing-in-ci--cicd--hard]] - Secure signing
- [[q-app-distribution--cicd--medium]] - App distribution

### Related
- [[q-github-actions-android--cicd--medium]] - GitHub Actions
- [[q-build-variants-flavors--cicd--medium]] - Build variants

### Advanced
- [[q-gradle-build-cache--cicd--medium]] - Build optimization
