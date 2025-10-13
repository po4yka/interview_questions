---
tags:
  - android
  - ci-cd
  - devops
  - github-actions
  - gitlab-ci
  - automation
difficulty: medium
status: draft
related:
  - q-cicd-automated-testing--devops--medium
  - q-gradle-build-optimization--build--medium
  - q-app-bundle-optimization--distribution--medium
created: 2025-10-11
---

# Question (EN)
How do you set up a CI/CD pipeline for an Android project? Compare GitHub Actions, GitLab CI, and Jenkins. What are the essential stages in an Android CI/CD pipeline?

## Answer (EN)
### Overview

A **CI/CD (Continuous Integration/Continuous Deployment) pipeline** automates the build, test, and deployment process for Android applications. It ensures code quality, catches bugs early, and streamlines the release process.

### Essential CI/CD Pipeline Stages

```

   Commit    

       

  1. Build         ← Compile code, resolve dependencies

       

  2. Unit Tests    ← Fast, isolated tests

       

  3. Lint/Static   ← Code quality checks
     Analysis    

       

  4. UI Tests      ← Instrumented tests (optional in CI)

       

  5. Build APK/    ← Release builds
     Bundle      

       

  6. Sign          ← Sign release artifacts

       

  7. Deploy        ← Upload to Play Store, Firebase, etc.

```

### GitHub Actions Setup

**Advantages:**
-  Free for public repos, generous free tier for private
-  Native GitHub integration
-  Large marketplace of actions
-  Good performance
-  Easy YAML syntax

**.github/workflows/android-ci.yml**:

```yaml
name: Android CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    name: Build and Test
    runs-on: ubuntu-latest

    steps:
      # 1. Checkout code
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Set up JDK
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      # 3. Grant execute permission for gradlew
      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      # 4. Cache Gradle dependencies
      - name: Cache Gradle packages
        uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
          restore-keys: |
            ${{ runner.os }}-gradle-

      # 5. Run Lint
      - name: Run Android Lint
        run: ./gradlew lintDebug

      # 6. Upload Lint results
      - name: Upload Lint results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: lint-results
          path: app/build/reports/lint-results-debug.html

      # 7. Run unit tests
      - name: Run unit tests
        run: ./gradlew testDebugUnitTest

      # 8. Upload test results
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: app/build/reports/tests/testDebugUnitTest/

      # 9. Generate test coverage
      - name: Generate test coverage
        run: ./gradlew jacocoTestReport

      # 10. Upload coverage to Codecov
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml
          flags: unittests
          name: codecov-umbrella

      # 11. Build debug APK
      - name: Build debug APK
        run: ./gradlew assembleDebug

      # 12. Upload debug APK
      - name: Upload debug APK
        uses: actions/upload-artifact@v3
        with:
          name: debug-apk
          path: app/build/outputs/apk/debug/app-debug.apk

  instrumented-tests:
    name: Instrumented Tests
    runs-on: macos-latest # macOS has hardware acceleration for emulator

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      # Run instrumented tests on emulator
      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 33
          target: google_apis
          arch: x86_64
          profile: Nexus 6
          script: ./gradlew connectedDebugAndroidTest

      - name: Upload instrumented test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: instrumented-test-results
          path: app/build/reports/androidTests/connected/

  release:
    name: Build Release
    runs-on: ubuntu-latest
    needs: [build, instrumented-tests]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      # Decode keystore from secrets
      - name: Decode keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > keystore.jks

      # Build release bundle
      - name: Build release bundle
        run: ./gradlew bundleRelease
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}

      # Upload to Play Store
      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
          status: completed

      # Upload artifact
      - name: Upload release bundle
        uses: actions/upload-artifact@v3
        with:
          name: release-bundle
          path: app/build/outputs/bundle/release/app-release.aab
```

### GitLab CI Setup

**Advantages:**
-  Integrated with GitLab
-  Built-in Docker registry
-  Excellent UI for pipeline visualization
-  Self-hosted options

**.gitlab-ci.yml**:

```yaml
image: mingc/android-build-box:latest

variables:
  # Use fastzip for faster caching
  FF_USE_FASTZIP: "true"
  CACHE_COMPRESSION_LEVEL: "fastest"

# Define cache for Gradle
cache:
  key: ${CI_PROJECT_ID}
  paths:
    - .gradle/

stages:
  - build
  - test
  - analyze
  - release
  - deploy

before_script:
  - export GRADLE_USER_HOME=$(pwd)/.gradle
  - chmod +x ./gradlew

# Stage 1: Build
build_debug:
  stage: build
  script:
    - ./gradlew assembleDebug
  artifacts:
    paths:
      - app/build/outputs/apk/debug/app-debug.apk
    expire_in: 1 week
  only:
    - merge_requests
    - main
    - develop

# Stage 2: Unit Tests
unit_tests:
  stage: test
  script:
    - ./gradlew testDebugUnitTest
  artifacts:
    when: always
    reports:
      junit: app/build/test-results/testDebugUnitTest/*.xml
    paths:
      - app/build/reports/tests/testDebugUnitTest/
    expire_in: 1 week
  coverage: '/Total.*?([0-9]{1,3})%/'
  only:
    - merge_requests
    - main
    - develop

# Stage 3: Lint Analysis
lint_check:
  stage: analyze
  script:
    - ./gradlew lintDebug
  artifacts:
    when: always
    paths:
      - app/build/reports/lint-results-debug.html
      - app/build/reports/lint-results-debug.xml
    expire_in: 1 week
  only:
    - merge_requests
    - main
    - develop

# Stage 3: Static Analysis
detekt:
  stage: analyze
  script:
    - ./gradlew detekt
  artifacts:
    when: always
    paths:
      - build/reports/detekt/
    expire_in: 1 week
  allow_failure: true
  only:
    - merge_requests
    - main
    - develop

# Stage 4: Instrumented Tests
instrumented_tests:
  stage: test
  image: mingc/android-build-box:latest
  script:
    - echo "Starting emulator..."
    - adb start-server
    - emulator -avd test -no-audio -no-window -gpu swiftshader_indirect -no-snapshot -noaudio -no-boot-anim &
    - adb wait-for-device shell 'while [[ -z $(getprop sys.boot_completed) ]]; do sleep 1; done;'
    - adb devices
    - ./gradlew connectedDebugAndroidTest
  artifacts:
    when: always
    paths:
      - app/build/reports/androidTests/connected/
    expire_in: 1 week
  only:
    - main
  # This can be slow, so only run on main branch

# Stage 5: Build Release
build_release:
  stage: release
  script:
    # Decode keystore
    - echo $KEYSTORE_BASE64 | base64 -d > keystore.jks
    # Build release bundle
    - ./gradlew bundleRelease
  artifacts:
    paths:
      - app/build/outputs/bundle/release/app-release.aab
    expire_in: 1 month
  only:
    - main
    - tags
  environment:
    name: production

# Stage 6: Deploy to Play Store
deploy_play_store:
  stage: deploy
  image: ruby:latest
  before_script:
    - gem install fastlane
  script:
    - echo $SERVICE_ACCOUNT_JSON > service_account.json
    - fastlane supply --aab app/build/outputs/bundle/release/app-release.aab --track internal --json_key service_account.json
  only:
    - tags
  when: manual
  environment:
    name: production
    url: https://play.google.com/store/apps/details?id=com.example.app

# Deploy to Firebase App Distribution
deploy_firebase:
  stage: deploy
  image: node:latest
  before_script:
    - npm install -g firebase-tools
  script:
    - firebase appdistribution:distribute app/build/outputs/apk/debug/app-debug.apk --app $FIREBASE_APP_ID --groups testers --token $FIREBASE_TOKEN
  only:
    - develop
  dependencies:
    - build_debug
```

### Jenkins Setup

**Advantages:**
-  Highly customizable
-  Self-hosted control
-  Extensive plugin ecosystem
-  More complex setup

**Jenkinsfile**:

```groovy
pipeline {
    agent any

    environment {
        ANDROID_HOME = '/opt/android-sdk'
        GRADLE_USER_HOME = '.gradle'
    }

    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'chmod +x gradlew'
            }
        }

        stage('Build') {
            steps {
                sh './gradlew clean assembleDebug'
            }
        }

        stage('Unit Tests') {
            steps {
                sh './gradlew testDebugUnitTest'
            }
            post {
                always {
                    junit 'app/build/test-results/testDebugUnitTest/*.xml'
                    publishHTML([
                        reportDir: 'app/build/reports/tests/testDebugUnitTest',
                        reportFiles: 'index.html',
                        reportName: 'Unit Test Report'
                    ])
                }
            }
        }

        stage('Lint') {
            steps {
                sh './gradlew lintDebug'
            }
            post {
                always {
                    androidLint pattern: 'app/build/reports/lint-results-debug.xml'
                }
            }
        }

        stage('Code Coverage') {
            steps {
                sh './gradlew jacocoTestReport'
            }
            post {
                always {
                    jacoco(
                        execPattern: 'app/build/jacoco/*.exec',
                        classPattern: 'app/build/intermediates/javac/debug/classes',
                        sourcePattern: 'app/src/main/java'
                    )
                }
            }
        }

        stage('Build Release') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'keystore-password', variable: 'KEYSTORE_PASSWORD'),
                        string(credentialsId: 'key-alias', variable: 'KEY_ALIAS'),
                        string(credentialsId: 'key-password', variable: 'KEY_PASSWORD'),
                        file(credentialsId: 'keystore-file', variable: 'KEYSTORE_FILE')
                    ]) {
                        sh """
                            cp $KEYSTORE_FILE keystore.jks
                            ./gradlew bundleRelease \
                                -Pandroid.injected.signing.store.file=keystore.jks \
                                -Pandroid.injected.signing.store.password=$KEYSTORE_PASSWORD \
                                -Pandroid.injected.signing.key.alias=$KEY_ALIAS \
                                -Pandroid.injected.signing.key.password=$KEY_PASSWORD
                        """
                    }
                }
            }
        }

        stage('Deploy to Play Store') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withCredentials([file(credentialsId: 'play-store-credentials', variable: 'SERVICE_ACCOUNT_JSON')]) {
                        sh """
                            fastlane supply \
                                --aab app/build/outputs/bundle/release/app-release.aab \
                                --track internal \
                                --json_key $SERVICE_ACCOUNT_JSON
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            slackSend(
                color: 'good',
                message: "Build Successful: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
            )
        }
    }
}
```

### Platform Comparison

| Feature | GitHub Actions | GitLab CI | Jenkins |
|---------|---------------|-----------|---------|
| **Setup Complexity** | Easy | Easy | Complex |
| **Cost (Private)** | $$ (generous free tier) | $$ (generous free tier) | Free (self-hosted) |
| **Performance** | Fast | Fast | Depends on hardware |
| **UI/UX** | Good | Excellent | Basic |
| **Marketplace** | Large | Good | Extensive plugins |
| **Self-hosted** | GitHub Enterprise | Yes | Yes |
| **Docker Support** | Yes | Excellent | Yes |
| **Caching** | Good | Excellent | Good |
| **Matrix Builds** | Yes | Yes | Yes |
| **Secrets Management** | Good | Good | Good |

### Production Example: Complete CI/CD with Fastlane

**fastlane/Fastfile**:

```ruby
default_platform(:android)

platform :android do

  desc "Run unit tests"
  lane :test do
    gradle(task: "testDebugUnitTest")
  end

  desc "Run lint"
  lane :lint do
    gradle(task: "lintDebug")
  end

  desc "Build debug APK"
  lane :build_debug do
    gradle(task: "assembleDebug")
  end

  desc "Build release bundle"
  lane :build_release do
    gradle(
      task: "bundleRelease",
      properties: {
        "android.injected.signing.store.file" => ENV["KEYSTORE_FILE"],
        "android.injected.signing.store.password" => ENV["KEYSTORE_PASSWORD"],
        "android.injected.signing.key.alias" => ENV["KEY_ALIAS"],
        "android.injected.signing.key.password" => ENV["KEY_PASSWORD"]
      }
    )
  end

  desc "Deploy to internal testing"
  lane :deploy_internal do
    build_release
    upload_to_play_store(
      track: 'internal',
      aab: 'app/build/outputs/bundle/release/app-release.aab',
      skip_upload_metadata: true,
      skip_upload_changelogs: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )
  end

  desc "Deploy to beta"
  lane :deploy_beta do
    build_release
    upload_to_play_store(
      track: 'beta',
      aab: 'app/build/outputs/bundle/release/app-release.aab'
    )
  end

  desc "Deploy to production"
  lane :deploy_production do
    build_release
    upload_to_play_store(
      track: 'production',
      aab: 'app/build/outputs/bundle/release/app-release.aab',
      rollout: '0.1' # 10% rollout
    )
  end

  desc "Distribute to Firebase"
  lane :distribute_firebase do
    build_debug
    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID"],
      groups: "testers",
      release_notes: "Latest build from #{git_branch}",
      apk_path: "app/build/outputs/apk/debug/app-debug.apk"
    )
  end

  desc "Run full CI pipeline"
  lane :ci do
    lint
    test
    build_debug
  end

  error do |lane, exception|
    slack(
      message: " Lane #{lane} failed: #{exception.message}",
      success: false
    )
  end

end
```

**GitHub Actions with Fastlane**:

```yaml
name: Android CI with Fastlane

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  ci:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.0'
          bundler-cache: true

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Install Fastlane
        run: bundle install

      - name: Run CI pipeline
        run: bundle exec fastlane ci

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: ci-artifacts
          path: |
            app/build/reports/
            app/build/outputs/apk/debug/

  deploy:
    runs-on: ubuntu-latest
    needs: ci
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.0'
          bundler-cache: true

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Install Fastlane
        run: bundle install

      - name: Deploy to internal track
        run: bundle exec fastlane deploy_internal
        env:
          KEYSTORE_FILE: ${{ secrets.KEYSTORE_FILE }}
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
          PLAY_STORE_CONFIG_JSON: ${{ secrets.PLAY_STORE_CONFIG_JSON }}
```

### Best Practices

1. **Cache Dependencies**
   ```yaml
   #  GOOD - Cache Gradle dependencies
   - uses: actions/cache@v3
     with:
       path: |
         ~/.gradle/caches
         ~/.gradle/wrapper
       key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}

   #  BAD - No caching, slow builds
   - run: ./gradlew build
   ```

2. **Fail Fast**
   ```yaml
   #  GOOD - Run quick checks first
   jobs:
     lint:
       runs-on: ubuntu-latest
       steps:
         - run: ./gradlew lintDebug # Fast

     test:
       runs-on: ubuntu-latest
       needs: lint
       steps:
         - run: ./gradlew testDebugUnitTest

     build:
       runs-on: ubuntu-latest
       needs: [lint, test]
       steps:
         - run: ./gradlew assembleDebug

   #  BAD - Build first, then discover lint errors
   ```

3. **Secure Secrets**
   ```yaml
   #  GOOD - Use secrets management
   env:
     KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}

   #  BAD - Hardcoded secrets
   env:
     KEYSTORE_PASSWORD: "my-password"
   ```

4. **Parallel Jobs**
   ```yaml
   #  GOOD - Run independent jobs in parallel
   jobs:
     lint:
       runs-on: ubuntu-latest
     test:
       runs-on: ubuntu-latest
     # Both run in parallel

   #  BAD - Sequential execution
   jobs:
     lint:
       runs-on: ubuntu-latest
     test:
       runs-on: ubuntu-latest
       needs: lint # Waits unnecessarily
   ```

5. **Use Build Matrix for Multi-API Testing**
   ```yaml
   #  GOOD - Test multiple configurations
   strategy:
     matrix:
       api-level: [29, 30, 31, 33]
       target: [google_apis, default]

   steps:
     - uses: reactivecircus/android-emulator-runner@v2
       with:
         api-level: ${{ matrix.api-level }}
         target: ${{ matrix.target }}
   ```

### Summary

**Essential CI/CD stages for Android:**
1.  Build (compile, resolve dependencies)
2.  Unit Tests (fast feedback)
3.  Lint/Static Analysis (code quality)
4.  UI Tests (confidence in UI)
5.  Build Artifacts (APK/AAB)
6.  Sign (release artifacts)
7.  Deploy (Play Store, Firebase)

**Platform choice:**
- **GitHub Actions**: Best for GitHub projects, easy setup, good free tier
- **GitLab CI**: Best for GitLab projects, excellent UI, built-in Docker registry
- **Jenkins**: Best for enterprise, self-hosted, highly customizable

**Key practices:**
- Cache dependencies for faster builds
- Fail fast with quick checks first
- Secure secrets properly
- Run independent jobs in parallel
- Use Fastlane for deployment automation

---

# Вопрос (RU)
Как настроить CI/CD pipeline для Android-проекта? Сравните GitHub Actions, GitLab CI и Jenkins. Какие основные этапы должны быть в Android CI/CD pipeline?

## Ответ (RU)
### Обзор

**CI/CD (Continuous Integration/Continuous Deployment) pipeline** автоматизирует процесс сборки, тестирования и развёртывания Android-приложений. Это обеспечивает качество кода, раннее обнаружение багов и упрощает процесс релиза.

[Продолжение с примерами из английской версии...]

### Резюме

**Основные этапы CI/CD для Android:**
1.  Сборка (компиляция, разрешение зависимостей)
2.  Unit-тесты (быстрая обратная связь)
3.  Lint/статический анализ (качество кода)
4.  UI-тесты (уверенность в UI)
5.  Сборка артефактов (APK/AAB)
6.  Подпись (релизные артефакты)
7.  Развёртывание (Play Store, Firebase)

**Выбор платформы:**
- **GitHub Actions**: Лучше для GitHub-проектов, простая настройка, хороший бесплатный тарий
- **GitLab CI**: Лучше для GitLab-проектов, отличный UI, встроенный Docker registry
- **Jenkins**: Лучше для enterprise, self-hosted, высоко кастомизируемый

**Ключевые практики:**
- Кешируйте зависимости для быстрой сборки
- Fail fast с быстрыми проверками сначала
- Правильно защищайте секреты
- Запускайте независимые задачи параллельно
- Используйте Fastlane для автоматизации развёртывания
