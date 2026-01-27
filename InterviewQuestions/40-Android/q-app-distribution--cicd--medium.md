---
id: android-cicd-004
title: Firebase App Distribution and Internal Testing / Firebase App Distribution
  и Внутреннее Тестирование
aliases:
- Firebase App Distribution
- Firebase App Distribution и Внутреннее Тестирование
topic: android
subtopics:
- cicd
- app-distribution
- testing
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
- q-play-store-deployment--cicd--medium
- q-signing-in-ci--cicd--hard
created: 2026-01-23
updated: 2026-01-23
sources:
- https://firebase.google.com/docs/app-distribution
- https://developer.android.com/distribute/best-practices/launch/test-tracks
tags:
- android/cicd
- android/app-distribution
- difficulty/medium
- firebase
- testing
anki_cards:
- slug: android-cicd-004-0-en
  language: en
- slug: android-cicd-004-0-ru
  language: ru
---
# Вопрос (RU)

> Как распределять Android-приложения для тестирования через Firebase App Distribution и внутренние треки Play Console?

# Question (EN)

> How do you distribute Android applications for testing through Firebase App Distribution and Play Console internal testing tracks?

## Ответ (RU)

Существует два основных способа распределения тестовых сборок: **Firebase App Distribution** для быстрого распределения APK/AAB тестерам и **Play Console Test Tracks** для тестирования в production-близком окружении.

### Firebase App Distribution

Firebase App Distribution позволяет распределять pre-release версии приложения без публикации в Play Store.

#### Преимущества

- Быстрая доставка тестерам (минуты, не дни)
- Не требует подписи для Play Store
- Группы тестеров
- Автоматические уведомления
- Интеграция с CI/CD
- Поддержка APK и AAB

#### Настройка Firebase CLI

```bash
# Установка Firebase CLI
npm install -g firebase-tools

# Авторизация
firebase login

# Авторизация для CI (создаёт токен)
firebase login:ci
```

#### Распределение через CLI

```bash
# Базовое распределение
firebase appdistribution:distribute app-debug.apk \
  --app 1:123456789:android:abcdef \
  --groups "qa-team, beta-testers" \
  --release-notes "Bug fixes and performance improvements"

# С release notes из файла
firebase appdistribution:distribute app-release.aab \
  --app 1:123456789:android:abcdef \
  --groups "internal-testers" \
  --release-notes-file release-notes.txt
```

#### Интеграция с Gradle

```kotlin
// app/build.gradle.kts
plugins {
    id("com.google.firebase.appdistribution") version "4.2.0"
}

android {
    buildTypes {
        debug {
            firebaseAppDistribution {
                artifactType = "APK"
                groups = "qa-team"
                releaseNotes = "Debug build for QA testing"
            }
        }

        release {
            firebaseAppDistribution {
                artifactType = "AAB"
                groups = "beta-testers"
                releaseNotesFile = "release-notes.txt"
            }
        }
    }
}
```

Распределение:

```bash
./gradlew assembleDebug appDistributionUploadDebug
./gradlew bundleRelease appDistributionUploadRelease
```

#### Интеграция с GitHub Actions

```yaml
name: Distribute to Firebase

on:
  push:
    branches: [develop]

jobs:
  distribute:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Build Debug APK
        run: ./gradlew assembleDebug

      - name: Upload to Firebase App Distribution
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{ secrets.FIREBASE_APP_ID }}
          serviceCredentialsFileContent: ${{ secrets.FIREBASE_CREDENTIALS }}
          groups: qa-team
          file: app/build/outputs/apk/debug/app-debug.apk
          releaseNotes: |
            Build: ${{ github.run_number }}
            Commit: ${{ github.sha }}
            Branch: ${{ github.ref_name }}
```

#### Service Account для CI

```bash
# Создание service account
# 1. Firebase Console -> Project Settings -> Service Accounts
# 2. Generate new private key
# 3. Сохранить JSON как secret в CI

# Использование в CLI
export GOOGLE_APPLICATION_CREDENTIALS="service-account.json"
firebase appdistribution:distribute app.apk --app <app-id>
```

### Play Console Test Tracks

Play Console предоставляет три типа тестовых треков:

| Трек | Назначение | Ограничение |
|------|------------|-------------|
| Internal | Быстрое тестирование командой | До 100 тестеров |
| Closed | Ограниченная бета | Email-списки/группы Google |
| Open | Публичная бета | Любой может присоединиться |

#### Internal Testing Track

Самый быстрый способ тестирования (минуты вместо часов):

```bash
# Через Gradle Play Publisher plugin
./gradlew publishBundle --track internal
```

#### Gradle Play Publisher Plugin

```kotlin
// app/build.gradle.kts
plugins {
    id("com.github.triplet.play") version "3.9.1"
}

play {
    serviceAccountCredentials.set(file("play-service-account.json"))
    track.set("internal")
    defaultToAppBundles.set(true)

    // Автоматическое увеличение version code
    resolutionStrategy.set(ResolutionStrategy.AUTO)
}
```

```bash
# Загрузка в internal трек
./gradlew publishBundle

# Загрузка в closed alpha
./gradlew publishBundle --track alpha

# Загрузка в open beta
./gradlew publishBundle --track beta

# Promote из internal в production
./gradlew promoteArtifact --from-track internal --track production
```

#### GitHub Actions для Play Store

```yaml
name: Deploy to Internal Testing

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Decode Keystore
        env:
          ENCODED_KEYSTORE: ${{ secrets.KEYSTORE_BASE64 }}
        run: echo $ENCODED_KEYSTORE | base64 -d > app/release.keystore

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Build Release Bundle
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Deploy to Play Store Internal
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_CREDENTIALS }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
          status: completed
          whatsNewDirectory: whatsnew/
```

### Сравнение Подходов

| Аспект | Firebase App Distribution | Play Console Internal |
|--------|--------------------------|----------------------|
| Скорость | Минуты | Минуты-часы |
| Подпись | Любая | Требует upload key |
| Размер группы | Неограничен | До 100 |
| Установка | Прямая загрузка | Play Store |
| AAB поддержка | Да (конвертация в APK) | Да (native) |
| Versioning | Произвольный | Строгие правила |

### Лучшие Практики

#### 1. Стратегия Распределения

```
Feature Branch -> Firebase (QA)
     |
Develop -> Firebase (Internal Testers)
     |
Release Branch -> Play Console Internal
     |
Main/Tag -> Play Console Closed Beta -> Open Beta -> Production
```

#### 2. Автоматизация Release Notes

```yaml
# .github/workflows/release-notes.yml
- name: Generate Release Notes
  run: |
    git log --pretty=format:"- %s" ${{ github.event.before }}..${{ github.sha }} > release-notes.txt

- name: Upload with Notes
  run: |
    firebase appdistribution:distribute app.apk \
      --release-notes-file release-notes.txt
```

#### 3. Группы Тестеров

```bash
# Firebase: создание группы
firebase appdistribution:testers:add --group qa-team user@example.com

# Распределение по группам
firebase appdistribution:distribute app.apk \
  --groups "qa-team, designers, product"
```

### Резюме

| Сценарий | Рекомендация |
|----------|--------------|
| Быстрая итерация | Firebase App Distribution |
| QA тестирование | Firebase App Distribution |
| Pre-production | Play Console Internal |
| Бета с обратной связью | Play Console Closed/Open |
| Staged rollout | Play Console Production |

## Answer (EN)

There are two main ways to distribute test builds: **Firebase App Distribution** for quick APK/AAB distribution to testers and **Play Console Test Tracks** for testing in a production-like environment.

### Firebase App Distribution

Firebase App Distribution allows distributing pre-release versions without publishing to Play Store.

#### Advantages

- Fast delivery to testers (minutes, not days)
- No Play Store signing required
- Tester groups
- Automatic notifications
- CI/CD integrations
- APK and AAB support

#### Firebase CLI Setup

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Authorization
firebase login

# CI authorization (generates token)
firebase login:ci
```

#### CLI Distribution

```bash
# Basic distribution
firebase appdistribution:distribute app-debug.apk \
  --app 1:123456789:android:abcdef \
  --groups "qa-team, beta-testers" \
  --release-notes "Bug fixes and performance improvements"

# With release notes from file
firebase appdistribution:distribute app-release.aab \
  --app 1:123456789:android:abcdef \
  --groups "internal-testers" \
  --release-notes-file release-notes.txt
```

#### Gradle Integration

```kotlin
// app/build.gradle.kts
plugins {
    id("com.google.firebase.appdistribution") version "4.2.0"
}

android {
    buildTypes {
        debug {
            firebaseAppDistribution {
                artifactType = "APK"
                groups = "qa-team"
                releaseNotes = "Debug build for QA testing"
            }
        }

        release {
            firebaseAppDistribution {
                artifactType = "AAB"
                groups = "beta-testers"
                releaseNotesFile = "release-notes.txt"
            }
        }
    }
}
```

Distribution:

```bash
./gradlew assembleDebug appDistributionUploadDebug
./gradlew bundleRelease appDistributionUploadRelease
```

#### GitHub Actions Integration

```yaml
name: Distribute to Firebase

on:
  push:
    branches: [develop]

jobs:
  distribute:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Build Debug APK
        run: ./gradlew assembleDebug

      - name: Upload to Firebase App Distribution
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{ secrets.FIREBASE_APP_ID }}
          serviceCredentialsFileContent: ${{ secrets.FIREBASE_CREDENTIALS }}
          groups: qa-team
          file: app/build/outputs/apk/debug/app-debug.apk
          releaseNotes: |
            Build: ${{ github.run_number }}
            Commit: ${{ github.sha }}
            Branch: ${{ github.ref_name }}
```

#### Service Account for CI

```bash
# Creating service account
# 1. Firebase Console -> Project Settings -> Service Accounts
# 2. Generate new private key
# 3. Save JSON as CI secret

# Usage in CLI
export GOOGLE_APPLICATION_CREDENTIALS="service-account.json"
firebase appdistribution:distribute app.apk --app <app-id>
```

### Play Console Test Tracks

Play Console provides three types of test tracks:

| Track | Purpose | Limitation |
|-------|---------|------------|
| Internal | Quick team testing | Up to 100 testers |
| Closed | Limited beta | Email lists/Google Groups |
| Open | Public beta | Anyone can join |

#### Internal Testing Track

Fastest way to test (minutes vs hours):

```bash
# Via Gradle Play Publisher plugin
./gradlew publishBundle --track internal
```

#### Gradle Play Publisher Plugin

```kotlin
// app/build.gradle.kts
plugins {
    id("com.github.triplet.play") version "3.9.1"
}

play {
    serviceAccountCredentials.set(file("play-service-account.json"))
    track.set("internal")
    defaultToAppBundles.set(true)

    // Automatic version code increment
    resolutionStrategy.set(ResolutionStrategy.AUTO)
}
```

```bash
# Upload to internal track
./gradlew publishBundle

# Upload to closed alpha
./gradlew publishBundle --track alpha

# Upload to open beta
./gradlew publishBundle --track beta

# Promote from internal to production
./gradlew promoteArtifact --from-track internal --track production
```

#### GitHub Actions for Play Store

```yaml
name: Deploy to Internal Testing

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Decode Keystore
        env:
          ENCODED_KEYSTORE: ${{ secrets.KEYSTORE_BASE64 }}
        run: echo $ENCODED_KEYSTORE | base64 -d > app/release.keystore

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Build Release Bundle
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Deploy to Play Store Internal
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_CREDENTIALS }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
          status: completed
          whatsNewDirectory: whatsnew/
```

### Comparison

| Aspect | Firebase App Distribution | Play Console Internal |
|--------|--------------------------|----------------------|
| Speed | Minutes | Minutes-hours |
| Signing | Any | Requires upload key |
| Group size | Unlimited | Up to 100 |
| Installation | Direct download | Play Store |
| AAB support | Yes (converts to APK) | Yes (native) |
| Versioning | Arbitrary | Strict rules |

### Best Practices

#### 1. Distribution Strategy

```
Feature Branch -> Firebase (QA)
     |
Develop -> Firebase (Internal Testers)
     |
Release Branch -> Play Console Internal
     |
Main/Tag -> Play Console Closed Beta -> Open Beta -> Production
```

#### 2. Release Notes Automation

```yaml
# .github/workflows/release-notes.yml
- name: Generate Release Notes
  run: |
    git log --pretty=format:"- %s" ${{ github.event.before }}..${{ github.sha }} > release-notes.txt

- name: Upload with Notes
  run: |
    firebase appdistribution:distribute app.apk \
      --release-notes-file release-notes.txt
```

#### 3. Tester Groups

```bash
# Firebase: create group
firebase appdistribution:testers:add --group qa-team user@example.com

# Distribute to groups
firebase appdistribution:distribute app.apk \
  --groups "qa-team, designers, product"
```

### Summary

| Scenario | Recommendation |
|----------|----------------|
| Rapid iteration | Firebase App Distribution |
| QA testing | Firebase App Distribution |
| Pre-production | Play Console Internal |
| Beta with feedback | Play Console Closed/Open |
| Staged rollout | Play Console Production |

## Дополнительные Вопросы (RU)

1. Как обрабатывать сбор обратной связи тестеров в Firebase App Distribution?
2. В чём разница между Play App Signing и самостоятельным подписанием?
3. Как автоматизировать продвижение между тестовыми треками?
4. Как управлять несколькими вариантами приложения при распределении?

## Follow-ups

1. How do you handle tester feedback collection in Firebase App Distribution?
2. What's the difference between Play App Signing and self-signing?
3. How do you automate promotion between test tracks?
4. How do you manage multiple app variants in distribution?

## Ссылки (RU)

- [Firebase App Distribution](https://firebase.google.com/docs/app-distribution)
- [Play Console Test Tracks](https://developer.android.com/distribute/best-practices/launch/test-tracks)
- [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher)

## References

- [Firebase App Distribution](https://firebase.google.com/docs/app-distribution)
- [Play Console Test Tracks](https://developer.android.com/distribute/best-practices/launch/test-tracks)
- [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher)
- [Upload to Google Play Action](https://github.com/r0adkll/upload-google-play)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-github-actions-android--cicd--medium]] — Настройка GitHub Actions
- [[q-signing-in-ci--cicd--hard]] — Безопасное подписание

### Похожие
- [[q-play-store-deployment--cicd--medium]] — Публикация в Play Store
- [[q-build-variants-flavors--cicd--medium]] — Варианты сборки

### Продвинутое
- [[q-gradle-build-cache--cicd--medium]] — Оптимизация сборки

## Related Questions

### Prerequisites
- [[q-github-actions-android--cicd--medium]] - GitHub Actions setup
- [[q-signing-in-ci--cicd--hard]] - Secure signing

### Related
- [[q-play-store-deployment--cicd--medium]] - Play Store deployment
- [[q-build-variants-flavors--cicd--medium]] - Build variants

### Advanced
- [[q-gradle-build-cache--cicd--medium]] - Build optimization
