---
id: android-355
title: CI/CD Deployment Automation / Автоматизация деплоя в CI/CD
aliases: [CI/CD Deployment Automation, Автоматизация деплоя в CI/CD]
topic: android
subtopics:
  - ci-cd
  - gradle
  - play-console
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-android-lint-tool--android--medium
  - q-app-store-optimization--android--medium
  - q-build-optimization-gradle--android--medium
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/ci-cd, android/gradle, android/play-console, ci-cd, deployment, difficulty/medium]
date created: Thursday, October 30th 2025, 11:19:02 am
date modified: Sunday, November 2nd 2025, 1:29:49 pm
---

# Вопрос (RU)
> Как автоматизировать деплой Android-приложения через CI/CD?

# Question (EN)
> How to automate Android app deployment through CI/CD?

---

## Ответ (RU)

### Цели
Репродуцируемые подписанные сборки с трассируемым версионированием, безопасным staged rollout и мгновенным откатом.

### Пайплайн
```
Build → Sign → Test/Lint → Upload Internal → Gates →
Promote (alpha/beta/prod) → Monitor → Rollback
```

**Gates:** тесты прошли, lint чист, порог crash-free sessions в internal track.

### Версионирование
Gradle как единый источник истины: автоинкремент `versionCode` на CI, встраивание Git SHA.

```kotlin
// ✅ Автоматизация версий
android {
    defaultConfig {
        versionCode = System.getenv("CI_BUILD_NUMBER")?.toInt() ?: 1
        versionName = "1.2.${versionCode}"
        buildConfigField("String", "GIT_SHA", "\"${getGitSha()}\"")
    }
}

fun getGitSha() = providers.exec {
    commandLine("git", "rev-parse", "--short", "HEAD")
}.standardOutput.asText.get().trim()
```

### Подписание
**Play App Signing:** Google управляет production keystore, вы используете upload keystore из CI secrets.

```kotlin
// ✅ Подписание через env-переменные
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_FILE") ?: "upload.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS")
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }
}
```

❌ Никогда не коммитить keystores/пароли в репозиторий.

### Артефакты
- **AAB** для Play Store
- **APK** для internal тестирования
- **mapping.txt** для деобфускации стектрейсов
- **Release notes** автогенерируются из conventional commits

### CI Конфигурация
```yaml
# ✅ GitHub Actions deploy
name: Deploy
on: { push: { tags: ['v*'] } }
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - name: Build & Upload
        env:
          PLAY_JSON: ${{ secrets.PLAY_SERVICE_JSON }}
        run: |
          ./gradlew bundleRelease --build-cache
          ./gradlew publishBundle -Pplay.track=internal
```

### Staged Rollout
**Internal** (PR merge) → **Alpha** (5%) → **Beta** (20%) → **Production** (100%)

Автоповышение при прохождении метрик: crash rate < 0.5%, ANR стабилен.

### Откат
Метрики для автоотката:
- Crash-free sessions < 99%
- ANR rate > baseline + 50%
- Критичные ошибки в Crashlytics

```bash
# ✅ Автоматический откат
./gradlew haltPlayRelease
./gradlew promoteArtifact --from-version <previous>
```

Сохранять последний стабильный AAB + mapping.txt.

## Answer (EN)

### Goals
Reproducible signed builds with traceable versioning, safe staged rollout, and instant rollback.

### Pipeline
```
Build → Sign → Test/Lint → Upload Internal → Gates →
Promote (alpha/beta/prod) → Monitor → Rollback
```

**Gates:** tests pass, lint clean, crash-free sessions threshold in internal track.

### Versioning
Gradle as single source of truth: auto-increment `versionCode` on CI, embed Git SHA.

```kotlin
// ✅ Automated versioning
android {
    defaultConfig {
        versionCode = System.getenv("CI_BUILD_NUMBER")?.toInt() ?: 1
        versionName = "1.2.${versionCode}"
        buildConfigField("String", "GIT_SHA", "\"${getGitSha()}\"")
    }
}

fun getGitSha() = providers.exec {
    commandLine("git", "rev-parse", "--short", "HEAD")
}.standardOutput.asText.get().trim()
```

### Signing
**Play App Signing:** Google manages production keystore, you use upload keystore from CI secrets.

```kotlin
// ✅ Signing via environment variables
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_FILE") ?: "upload.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS")
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }
}
```

❌ Never commit keystores/passwords to repository.

### Artifacts
- **AAB** for Play Store
- **APK** for internal testing
- **mapping.txt** for stack trace deobfuscation
- **Release notes** auto-generated from conventional commits

### CI Configuration
```yaml
# ✅ GitHub Actions deploy
name: Deploy
on: { push: { tags: ['v*'] } }
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - name: Build & Upload
        env:
          PLAY_JSON: ${{ secrets.PLAY_SERVICE_JSON }}
        run: |
          ./gradlew bundleRelease --build-cache
          ./gradlew publishBundle -Pplay.track=internal
```

### Staged Rollout
**Internal** (PR merge) → **Alpha** (5%) → **Beta** (20%) → **Production** (100%)

Auto-promotion on passing metrics: crash rate < 0.5%, ANR stable.

### Rollback
Metrics for auto-rollback:
- Crash-free sessions < 99%
- ANR rate > baseline + 50%
- Critical errors in Crashlytics

```bash
# ✅ Automatic rollback
./gradlew haltPlayRelease
./gradlew promoteArtifact --from-version <previous>
```

Keep last stable AAB + mapping.txt.

---

## Follow-ups

- How to implement secure keystore management with Cloud KMS or HashiCorp Vault?
- What strategies handle rollback when database migrations are incompatible?
- How to automate Play Store metadata and screenshot updates?
- What metrics define healthy staged rollout thresholds?
- How to integrate feature flags with progressive delivery?

## References

- [[c-gradle]] - Gradle build system
- https://developer.android.com/studio/publish
- https://developer.android.com/studio/publish/app-signing
- https://github.com/Triple-T/gradle-play-publisher

## Related Questions

### Prerequisites
- [[q-build-optimization-gradle--android--medium]] - Gradle optimization for CI
- [[q-android-lint-tool--android--medium]] - Static analysis in CI

### Related
- [[q-cicd-automated-testing--android--medium]] - Automated testing
- [[q-app-store-optimization--android--medium]] - Play Store optimization
- Build variants and product flavors

### Advanced
- Multi-module build caching strategies
- Feature flags with rollout integration
- Automated A/B testing in releases
