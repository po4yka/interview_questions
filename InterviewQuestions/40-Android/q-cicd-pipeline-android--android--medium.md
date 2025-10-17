---
id: "20251015082237486"
title: "Cicd Pipeline Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - cicd
  - github-actions
  - automation
  - testing
  - deployment
  - gradle
---
# CI/CD Pipeline for Android

**Сложность**: Medium
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> How do you set up a CI/CD (Continuous Integration/Continuous Deployment) pipeline for Android? What are the key stages and best practices?

# Вопрос (RU)
> Как настроить CI/CD пайплайн для Android?

---

## Answer (EN)

A robust CI/CD pipeline automates building, testing, and deploying Android apps, ensuring code quality and faster releases. Modern pipelines use GitHub Actions, GitLab CI, Jenkins, or Bitrise.

#### 1. **GitHub Actions Pipeline**

```yaml
# .github/workflows/android-ci.yml
name: Android CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      # 1. Checkout code
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Set up JDK
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          cache: 'gradle'

      # 3. Grant execute permission for gradlew
      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      # 4. Validate Gradle wrapper
      - name: Validate Gradle wrapper
        uses: gradle/wrapper-validation-action@v1

      # 5. Run unit tests
      - name: Run unit tests
        run: ./gradlew testDebugUnitTest

      # 6. Upload test results
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: '**/build/test-results/**/*.xml'

      # 7. Run lint
      - name: Run Android Lint
        run: ./gradlew lintDebug

      # 8. Upload lint reports
      - name: Upload lint reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: lint-reports
          path: '**/build/reports/lint-results-*.html'

      # 9. Build debug APK
      - name: Build debug APK
        run: ./gradlew assembleDebug

      # 10. Upload APK
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: app-debug
          path: app/build/outputs/apk/debug/app-debug.apk

  # Instrumented tests job
  instrumented-tests:
    runs-on: macos-latest
    timeout-minutes: 45

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 33
          arch: x86_64
          profile: Nexus 6
          script: ./gradlew connectedDebugAndroidTest

      - name: Upload instrumented test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: instrumented-test-results
          path: '**/build/reports/androidTests/**'
```

#### 2. **Complete Multi-Stage Pipeline**

```yaml
# .github/workflows/android-cd.yml
name: Android CD

on:
  push:
    tags:
      - 'v*'

jobs:
  # Stage 1: Validate
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          cache: 'gradle'

      - name: Validate Gradle wrapper
        uses: gradle/wrapper-validation-action@v1

      - name: Check code formatting
        run: ./gradlew ktlintCheck

      - name: Static code analysis
        run: ./gradlew detekt

  # Stage 2: Test
  test:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          cache: 'gradle'

      - name: Run unit tests
        run: ./gradlew testDebugUnitTest --continue

      - name: Generate coverage report
        run: ./gradlew jacocoTestReport

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml

  # Stage 3: Build
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          cache: 'gradle'

      # Decode signing key
      - name: Decode keystore
        env:
          ENCODED_STRING: ${{ secrets.KEYSTORE_BASE64 }}
        run: |
          echo $ENCODED_STRING | base64 -di > keystore.jks

      # Build release APK/AAB
      - name: Build release AAB
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Build release APK
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew assembleRelease

      # Upload artifacts
      - name: Upload AAB
        uses: actions/upload-artifact@v3
        with:
          name: app-release-bundle
          path: app/build/outputs/bundle/release/app-release.aab

      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: app-release
          path: app/build/outputs/apk/release/app-release.apk

  # Stage 4: Deploy to Play Store
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download AAB
        uses: actions/download-artifact@v3
        with:
          name: app-release-bundle
          path: .

      - name: Deploy to Play Store Internal Track
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
          packageName: com.example.app
          releaseFiles: app-release.aab
          track: internal
          status: completed
          whatsNewDirectory: distribution/whatsnew

  # Stage 5: Create GitHub Release
  release:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download APK
        uses: actions/download-artifact@v3
        with:
          name: app-release
          path: .

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: app-release.apk
          generate_release_notes: true
```

#### 3. **Gradle Configuration for CI/CD**

```kotlin
// build.gradle.kts (app module)

android {
    signingConfigs {
        create("release") {
            // Use environment variables from CI
            storeFile = file(System.getenv("KEYSTORE_FILE") ?: "keystore.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS")
            keyPassword = System.getenv("KEY_PASSWORD")
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

            // Build configuration from environment
            buildConfigField(
                "String",
                "API_KEY",
                "\"${System.getenv("API_KEY") ?: ""}\""
            )
        }

        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
    }

    // Version code from CI
    defaultConfig {
        versionCode = System.getenv("VERSION_CODE")?.toIntOrNull() ?: 1
        versionName = System.getenv("VERSION_NAME") ?: "1.0.0"
    }

    // Test options for CI
    testOptions {
        unitTests {
            isIncludeAndroidResources = true
            isReturnDefaultValues = true
        }

        // Generate XML reports
        unitTests.all {
            it.useJUnitPlatform()
            it.testLogging {
                events("passed", "skipped", "failed")
            }
        }
    }
}

// Task for generating version info
tasks.register("generateVersionInfo") {
    doLast {
        val versionFile = file("$buildDir/version.txt")
        versionFile.writeText("""
            Version Code: ${android.defaultConfig.versionCode}
            Version Name: ${android.defaultConfig.versionName}
            Build Time: ${System.currentTimeMillis()}
            Git Commit: ${getGitCommitHash()}
        """.trimIndent())
    }
}

fun getGitCommitHash(): String {
    return try {
        val stdout = ByteArrayOutputStream()
        exec {
            commandLine("git", "rev-parse", "--short", "HEAD")
            standardOutput = stdout
        }
        stdout.toString().trim()
    } catch (e: Exception) {
        "unknown"
    }
}
```

#### 4. **Quality Checks Integration**

```kotlin
// build.gradle.kts (app module)

plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.7"
    id("org.jlleitschuh.gradle.ktlint") version "12.1.2"
    jacoco
}

// Detekt (static code analysis)
detekt {
    config = files("$projectDir/config/detekt/detekt.yml")
    buildUponDefaultConfig = true
    reports {
        html.required.set(true)
        xml.required.set(true)
        txt.required.set(false)
    }
}

// Ktlint (code formatting)
ktlint {
    android.set(true)
    outputColorName.set("RED")
    reporters {
        reporter(org.jlleitschuh.gradle.ktlint.reporter.ReporterType.HTML)
        reporter(org.jlleitschuh.gradle.ktlint.reporter.ReporterType.CHECKSTYLE)
    }
}

// JaCoCo (code coverage)
tasks.register<JacocoReport>("jacocoTestReport") {
    dependsOn("testDebugUnitTest")

    reports {
        xml.required.set(true)
        html.required.set(true)
    }

    sourceDirectories.setFrom(files("src/main/java", "src/main/kotlin"))
    classDirectories.setFrom(files("build/intermediates/javac/debug"))
    executionData.setFrom(files("build/jacoco/testDebugUnitTest.exec"))
}

// Task to enforce minimum coverage
tasks.register<JacocoCoverageVerification>("jacocoCoverageVerification") {
    dependsOn("jacocoTestReport")

    violationRules {
        rule {
            limit {
                minimum = "0.80".toBigDecimal() // 80% coverage required
            }
        }
    }
}
```

#### 5. **Firebase App Distribution**

```yaml
# .github/workflows/firebase-distribution.yml
name: Firebase Distribution

on:
  push:
    branches: [ develop ]

jobs:
  distribute:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          cache: 'gradle'

      - name: Build debug APK
        run: ./gradlew assembleDebug

      - name: Upload to Firebase App Distribution
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{ secrets.FIREBASE_APP_ID }}
          serviceCredentialsFileContent: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          groups: testers
          file: app/build/outputs/apk/debug/app-debug.apk
          releaseNotes: |
            Branch: ${{ github.ref_name }}
            Commit: ${{ github.sha }}
            Author: ${{ github.actor }}
```

#### 6. **Docker for Consistent Builds**

```dockerfile
# Dockerfile for Android builds
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    wget \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Android SDK
ENV ANDROID_SDK_ROOT=/opt/android-sdk
RUN mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools && \
    cd ${ANDROID_SDK_ROOT}/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip

ENV PATH=${PATH}:${ANDROID_SDK_ROOT}/cmdline-tools/cmdline-tools/bin

# Accept licenses
RUN yes | sdkmanager --licenses

# Install SDK packages
RUN sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.1"

WORKDIR /app

# Copy project
COPY . .

# Build
RUN ./gradlew assembleDebug
```

```yaml
# Use Docker in GitHub Actions
- name: Build in Docker
  run: |
    docker build -t android-builder .
    docker run --rm -v $(pwd):/app android-builder
```

#### 7. **Monitoring and Notifications**

```yaml
# Send Slack notification on build status
- name: Slack Notification
  if: always()
  uses: rtCamp/action-slack-notify@v2
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
    SLACK_CHANNEL: android-builds
    SLACK_COLOR: ${{ job.status }}
    SLACK_TITLE: Build ${{ job.status }}
    SLACK_MESSAGE: |
      Branch: ${{ github.ref_name }}
      Commit: ${{ github.sha }}
      Author: ${{ github.actor }}
```

#### 8. **Best Practices Checklist**

**Setup:**
- [ ] Use caching for Gradle dependencies
- [ ] Set appropriate timeout limits
- [ ] Use matrix builds for multiple API levels
- [ ] Validate Gradle wrapper
- [ ] Use secrets for sensitive data

**Testing:**
- [ ] Run unit tests on every PR
- [ ] Run instrumented tests on critical paths
- [ ] Generate and upload test reports
- [ ] Track code coverage (target 80%+)
- [ ] Run lint and static analysis

**Building:**
- [ ] Build both debug and release variants
- [ ] Sign release builds securely
- [ ] Generate version info from git
- [ ] Upload build artifacts
- [ ] Create build reports

**Deployment:**
- [ ] Deploy to internal track first
- [ ] Automated rollout to production
- [ ] Firebase App Distribution for beta
- [ ] Create GitHub releases
- [ ] Generate changelog automatically

**Monitoring:**
- [ ] Send build notifications (Slack/Email)
- [ ] Track build times
- [ ] Monitor test flakiness
- [ ] Set up crash reporting
- [ ] Analytics for releases

**Security:**
- [ ] Never commit secrets
- [ ] Use GitHub Secrets/environment variables
- [ ] Rotate signing keys regularly
- [ ] Enable dependency scanning
- [ ] Use signed commits

### Common Pipeline Stages

```
1. Checkout → 2. Setup → 3. Validate → 4. Test → 5. Build → 6. Deploy
    ↓           ↓           ↓           ↓         ↓          ↓
  Git SCM     Java/SDK   Lint/Format  Unit/UI   APK/AAB   Play Store
                                      Tests      Signed    Firebase
                                      Coverage             Beta
```

---

## Ответ (RU)

Надёжный CI/CD pipeline автоматизирует сборку, тестирование и развертывание Android-приложений.

#### Основные этапы:

**1. Validate (Валидация):**
- Проверка Gradle wrapper
- Форматирование кода (ktlint)
- Статический анализ (detekt)

**2. Test (Тестирование):**
- Unit тесты
- Instrumented тесты
- Code coverage (Jacoco)
- Минимальное покрытие 80%

**3. Build (Сборка):**
- Debug и Release варианты
- Подписание release сборок
- Генерация APK/AAB
- Upload артефактов

**4. Deploy (Развертывание):**
- Internal track → Beta → Production
- Firebase App Distribution
- GitHub Releases

**5. Monitor (Мониторинг):**
- Уведомления (Slack/Email)
- Отслеживание метрик сборки
- Crash reporting

#### Популярные платформы:

- **GitHub Actions** - встроен в GitHub, бесплатный для public repos
- **GitLab CI/CD** - встроен в GitLab
- **Jenkins** - самостоятельный хостинг, гибкий
- **Bitrise** - специализирован для mobile
- **CircleCI** - облачный, быстрый

#### Ключевые практики:

**Безопасность:**
- Никогда не коммитить секреты
- Использовать GitHub Secrets
- Ротация ключей подписи

**Оптимизация:**
- Кэширование Gradle dependencies
- Параллельные jobs
- Matrix builds для разных API levels

**Качество:**
- Автоматические тесты на каждый PR
- Code coverage tracking
- Автоматический changelog

**Развертывание:**
- Поэтапный rollout
- Beta тестирование через Firebase
- Автоматизация релизов

Хорошо настроенный CI/CD pipeline экономит время, улучшает качество и ускоряет релизы.
