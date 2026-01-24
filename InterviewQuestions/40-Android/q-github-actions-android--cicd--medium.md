---
id: android-cicd-001
title: "GitHub Actions for Android Builds / GitHub Actions для сборки Android"
aliases: ["GitHub Actions for Android Builds", "GitHub Actions для сборки Android"]
topic: android
subtopics: [cicd, build-automation, continuous-integration]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-gradle-build-cache--cicd--medium, q-build-variants-flavors--cicd--medium, q-signing-in-ci--cicd--hard]
created: 2026-01-23
updated: 2026-01-23
sources: ["https://docs.github.com/en/actions", "https://developer.android.com/build"]
tags: [android/cicd, android/build-automation, difficulty/medium, github-actions, continuous-integration]

---
# Вопрос (RU)

> Как настроить GitHub Actions для сборки Android-приложения?

# Question (EN)

> How do you set up GitHub Actions for building an Android application?

## Ответ (RU)

GitHub Actions позволяет автоматизировать сборку, тестирование и развёртывание Android-приложений прямо в репозитории. Основные преимущества: интеграция с GitHub, бесплатные минуты для публичных репозиториев, богатая экосистема готовых actions.

### Базовая Конфигурация

Создай файл `.github/workflows/android.yml`:

```yaml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  JAVA_VERSION: '17'
  GRADLE_OPTS: "-Dorg.gradle.daemon=false -Dorg.gradle.parallel=true"

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4
        with:
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      - name: Build Debug APK
        run: ./gradlew assembleDebug

      - name: Run Unit Tests
        run: ./gradlew testDebugUnitTest

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: debug-apk
          path: app/build/outputs/apk/debug/*.apk
```

### Ключевые Компоненты

#### 1. Триггеры (on)

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'app/**'
      - 'build.gradle.kts'
      - '.github/workflows/**'
  pull_request:
    branches: [main]
  workflow_dispatch:  # Ручной запуск
  schedule:
    - cron: '0 6 * * 1'  # Каждый понедельник в 6:00 UTC
```

#### 2. Кеширование Gradle

```yaml
- name: Setup Gradle
  uses: gradle/actions/setup-gradle@v4
  with:
    cache-read-only: ${{ github.ref != 'refs/heads/main' }}
    gradle-home-cache-includes: |
      caches
      notifications
      jdks
```

Это автоматически кеширует:
- Gradle wrapper
- Зависимости
- Build cache

#### 3. Матрица Сборок

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        api-level: [29, 33, 34]
        variant: [debug, release]
      fail-fast: false

    steps:
      - name: Build ${{ matrix.variant }}
        run: ./gradlew assemble${{ matrix.variant }}
```

### Инструментированные Тесты

```yaml
  instrumented-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Run Instrumented Tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 33
          arch: x86_64
          profile: pixel_6
          heap-size: 512M
          ram-size: 4096M
          emulator-options: -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim
          disable-animations: true
          script: ./gradlew connectedDebugAndroidTest
```

### Параллельные Задачи

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew lint

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew testDebugUnitTest

  build:
    needs: [lint, unit-tests]  # Зависит от успеха lint и тестов
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew assembleRelease
```

### Секреты и Подписание

```yaml
- name: Decode Keystore
  env:
    ENCODED_KEYSTORE: ${{ secrets.KEYSTORE_BASE64 }}
  run: |
    echo $ENCODED_KEYSTORE | base64 -d > app/release.keystore

- name: Build Signed Release
  env:
    KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
    KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
    KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
  run: ./gradlew assembleRelease
```

### Лучшие Практики

| Практика | Описание |
|----------|----------|
| Кеширование | Используй `gradle/actions/setup-gradle` для автоматического кеширования |
| Параллельность | Разделяй lint, тесты и сборку на отдельные jobs |
| Fail-fast | Отключай для матрицы, чтобы увидеть все ошибки |
| Артефакты | Сохраняй APK/AAB для отладки и распределения |
| Timeouts | Устанавливай разумные лимиты времени |

### Оптимизация Времени Сборки

```yaml
env:
  GRADLE_OPTS: >-
    -Dorg.gradle.daemon=false
    -Dorg.gradle.parallel=true
    -Dorg.gradle.workers.max=4
    -Dorg.gradle.caching=true
    -Dkotlin.incremental=false
```

### Резюме

GitHub Actions для Android предоставляет:
- **Интеграцию с GitHub** — автоматический запуск на push/PR
- **Кеширование** — ускорение сборок через cache Gradle
- **Матрицу сборок** — тестирование на разных API level
- **Параллельность** — одновременный запуск lint, тестов, сборки
- **Секреты** — безопасное хранение ключей подписи
- **Артефакты** — сохранение APK/AAB для скачивания

## Answer (EN)

GitHub Actions automates building, testing, and deploying Android applications directly in your repository. Key advantages: native GitHub integration, free minutes for public repositories, rich ecosystem of pre-built actions.

### Basic Configuration

Create `.github/workflows/android.yml`:

```yaml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  JAVA_VERSION: '17'
  GRADLE_OPTS: "-Dorg.gradle.daemon=false -Dorg.gradle.parallel=true"

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4
        with:
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      - name: Build Debug APK
        run: ./gradlew assembleDebug

      - name: Run Unit Tests
        run: ./gradlew testDebugUnitTest

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: debug-apk
          path: app/build/outputs/apk/debug/*.apk
```

### Key Components

#### 1. Triggers (on)

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'app/**'
      - 'build.gradle.kts'
      - '.github/workflows/**'
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 6:00 UTC
```

#### 2. Gradle Caching

```yaml
- name: Setup Gradle
  uses: gradle/actions/setup-gradle@v4
  with:
    cache-read-only: ${{ github.ref != 'refs/heads/main' }}
    gradle-home-cache-includes: |
      caches
      notifications
      jdks
```

This automatically caches:
- Gradle wrapper
- Dependencies
- Build cache

#### 3. Build Matrix

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        api-level: [29, 33, 34]
        variant: [debug, release]
      fail-fast: false

    steps:
      - name: Build ${{ matrix.variant }}
        run: ./gradlew assemble${{ matrix.variant }}
```

### Instrumented Tests

```yaml
  instrumented-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Run Instrumented Tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 33
          arch: x86_64
          profile: pixel_6
          heap-size: 512M
          ram-size: 4096M
          emulator-options: -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim
          disable-animations: true
          script: ./gradlew connectedDebugAndroidTest
```

### Parallel Jobs

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew lint

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew testDebugUnitTest

  build:
    needs: [lint, unit-tests]  # Depends on lint and tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew assembleRelease
```

### Secrets and Signing

```yaml
- name: Decode Keystore
  env:
    ENCODED_KEYSTORE: ${{ secrets.KEYSTORE_BASE64 }}
  run: |
    echo $ENCODED_KEYSTORE | base64 -d > app/release.keystore

- name: Build Signed Release
  env:
    KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
    KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
    KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
  run: ./gradlew assembleRelease
```

### Best Practices

| Practice | Description |
|----------|-------------|
| Caching | Use `gradle/actions/setup-gradle` for automatic caching |
| Parallelism | Split lint, tests, and build into separate jobs |
| Fail-fast | Disable for matrix to see all failures |
| Artifacts | Save APK/AAB for debugging and distribution |
| Timeouts | Set reasonable time limits |

### Build Time Optimization

```yaml
env:
  GRADLE_OPTS: >-
    -Dorg.gradle.daemon=false
    -Dorg.gradle.parallel=true
    -Dorg.gradle.workers.max=4
    -Dorg.gradle.caching=true
    -Dkotlin.incremental=false
```

### Summary

GitHub Actions for Android provides:
- **GitHub Integration** — automatic triggers on push/PR
- **Caching** — faster builds through Gradle cache
- **Build Matrix** — testing across multiple API levels
- **Parallelism** — concurrent lint, tests, and build
- **Secrets** — secure storage of signing keys
- **Artifacts** — APK/AAB preservation for download

## Дополнительные Вопросы (RU)

1. Как обрабатывать нестабильные инструментированные тесты в CI?
2. Каковы компромиссы между GitHub Actions и другими CI системами (CircleCI, Bitrise)?
3. Как оптимизировать затраты на CI для больших Android-проектов?
4. Как реализовать CI/CD для многомодульных Android-проектов?

## Follow-ups

1. How do you handle flaky instrumented tests in CI?
2. What are the trade-offs between GitHub Actions and other CI systems (CircleCI, Bitrise)?
3. How do you optimize CI costs for large Android projects?
4. How do you implement CI/CD for multi-module Android projects?

## Ссылки (RU)

- [Документация GitHub Actions](https://docs.github.com/en/actions)
- [Документация сборки Android](https://developer.android.com/build)
- [Gradle Actions](https://github.com/gradle/actions)

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Android Build Documentation](https://developer.android.com/build)
- [Gradle Actions](https://github.com/gradle/actions)
- [Android Emulator Runner](https://github.com/ReactiveCircus/android-emulator-runner)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-gradle-build-cache--cicd--medium]] — Понимание кеширования Gradle
- [[q-build-variants-flavors--cicd--medium]] — Варианты сборки и flavors

### Похожие
- [[q-signing-in-ci--cicd--hard]] — Безопасное подписание в CI
- [[q-app-distribution--cicd--medium]] — Распределение приложений

### Продвинутое
- [[q-play-store-deployment--cicd--medium]] — Публикация в Play Store

## Related Questions

### Prerequisites
- [[q-gradle-build-cache--cicd--medium]] - Understanding Gradle caching
- [[q-build-variants-flavors--cicd--medium]] - Build variants and flavors

### Related
- [[q-signing-in-ci--cicd--hard]] - Secure signing in CI
- [[q-app-distribution--cicd--medium]] - App distribution

### Advanced
- [[q-play-store-deployment--cicd--medium]] - Play Store deployment
