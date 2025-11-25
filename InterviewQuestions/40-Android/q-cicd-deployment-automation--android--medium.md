---
id: android-355
title: CI/CD Deployment Automation / Автоматизация деплоя в CI/CD
aliases: [CI/CD Deployment Automation, Автоматизация деплоя в CI/CD]
topic: android
subtopics:
  - build-variants
  - ci-cd
  - play-console
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-build-optimization--android--medium
  - q-android-lint-tool--android--medium
  - q-android-release-pipeline-cicd--android--hard
  - q-internal-app-distribution--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/build-variants, android/ci-cd, android/play-console, ci-cd, deployment, difficulty/medium]
date created: Saturday, November 1st 2025, 12:46:45 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Как автоматизировать деплой Android-приложения через CI/CD?

# Question (EN)
> How to automate Android app deployment through CI/CD?

---

## Ответ (RU)

### Цели
Репродуцируемые подписанные сборки с трассируемым версионированием, безопасным staged rollout и быстрым контролируемым откатом (через инструменты Play Console/API, а не ручное перекладывание файлов).

### Пайплайн
```
Build → Sign → Test/Lint → Upload Internal → Gates →
Promote (alpha/beta/prod) → Monitor → Rollback
```

**Gates:** тесты прошли, lint чист, порог crash-free sessions в internal/alpha треке.

### Версионирование
Gradle как единый источник истины: автоматическое управление `versionCode` на CI (монотоно растущее для Play Store), встраивание Git SHA.

```kotlin
// ✅ Автоматизация версий (упрощенный пример для демонстрации идеи)
android {
    defaultConfig {
        val ciBuildNumber = System.getenv("CI_BUILD_NUMBER")?.toIntOrNull()
        // CI_BUILD_NUMBER должен быть глобально монотоно растущим, не сбрасываться по веткам
        // В реальном пайплайне убедитесь, что источник versionCode надёжен (например, tag/релизный номер или отдельное хранилище).
        versionCode = ciBuildNumber ?: 1
        versionName = "1.2.$versionCode"
        buildConfigField("String", "GIT_SHA", "\"${getGitSha()}\"")
    }
}

fun getGitSha(): String = "git rev-parse --short HEAD".runCommand().trim()

fun String.runCommand(): String =
    Runtime.getRuntime().exec(this.split(" ").toTypedArray()).inputStream.bufferedReader().readText()
```

(В реальном проекте получение SHA и versionCode лучше выносить в Gradle tasks/`androidComponents` или скрипты CI, а не вызывать git на этапе конфигурации Gradle и не использовать `Runtime.exec` напрямую в продакшене.)

### Подписание
**Play App Signing:** Google управляет production keystore, вы используете upload keystore из CI secrets.

```kotlin
// ✅ Подписание через env-переменные (пример)
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
- **AAB** (основной формат для Play Store)
- **APK** при необходимости для internal тестирования или внешней дистрибуции вне Play Store
- **mapping.txt** для деобфускации стектрейсов
- **Release notes** автогенерируются из conventional commits

### CI Конфигурация
```yaml
# ✅ GitHub Actions deploy (пример с gradle-play-publisher)
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
          PLAY_SERVICE_ACCOUNT_JSON: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
        run: |
          ./gradlew bundleRelease --build-cache \
            publishReleaseBundle \
            -Pplay.serviceAccountJson="${PLAY_SERVICE_ACCOUNT_JSON}" \
            -Pplay.track=internal
```

(Точные задачи и параметры зависят от используемого плагина публикации, например, `gradle-play-publisher`; приведённый YAML — схема, а не готовый универсальный конфиг.)

### Staged Rollout
**Internal** (PR merge) → **Alpha** (5%) → **Beta** (20%) → **Production** (100%)

Автоматизация промоушена делается через Play Developer API/плагин: CI скрипт проверяет метрики (через API/отчёты) и при выполнении условий повышает rollout.

Примеры метрик:
- crash rate < 0.5%
- стабильный ANR rate

### Откат
Метрики для автоотката (через Play Developer API/скрипты CI, а не "магические" Gradle задачи):
- Crash-free sessions < 99%
- ANR rate > baseline + 50%
- Критичные ошибки в Crashlytics

```bash
# ✅ Автоматический откат (пример логики высокого уровня)
# Требуется корректная интеграция с Play Developer API или плагином публикации.
# Скрипт читает метрики и при нарушении порогов переводит rollout на предыдущую стабильную версию.
./gradlew publishRelease --track production --user-fraction 0.0
./gradlew publishRelease --track production --version-codes "<previous-stable-version-code>"
```

Хранить последний стабильный AAB + mapping.txt и историю versionCode.

## Answer (EN)

### Goals
Reproducible signed builds with traceable versioning, safe staged rollout, and fast controlled rollback (via Play Console/API tooling rather than manual file juggling).

### Pipeline
```
Build → Sign → Test/Lint → Upload Internal → Gates →
Promote (alpha/beta/prod) → Monitor → Rollback
```

**Gates:** tests pass, lint clean, crash-free sessions threshold in internal/alpha track.

### Versioning
Gradle as single source of truth: automatic `versionCode` management on CI (monotonically increasing for Play Store), embed Git SHA.

```kotlin
// ✅ Automated versioning (simplified example to illustrate the idea)
android {
    defaultConfig {
        val ciBuildNumber = System.getenv("CI_BUILD_NUMBER")?.toIntOrNull()
        // CI_BUILD_NUMBER must be globally monotonically increasing and not reset per branch.
        // In a real pipeline, ensure versionCode is derived from a reliable source (e.g., release tags or dedicated storage).
        versionCode = ciBuildNumber ?: 1
        versionName = "1.2.$versionCode"
        buildConfigField("String", "GIT_SHA", "\"${getGitSha()}\"")
    }
}

fun getGitSha(): String = "git rev-parse --short HEAD".runCommand().trim()

fun String.runCommand(): String =
    Runtime.getRuntime().exec(this.split(" ").toTypedArray()).inputStream.bufferedReader().readText()
```

(In a real project, prefer using Gradle tasks/`androidComponents` or CI scripts to compute SHA/versionCode instead of calling git in the Gradle configuration phase and avoid relying on `Runtime.exec` directly in production builds.)

### Signing
**Play App Signing:** Google manages the production keystore; you use an upload keystore provided via CI secrets.

```kotlin
// ✅ Signing via environment variables (example)
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

❌ Never commit keystores/passwords to the repository.

### Artifacts
- **AAB** (primary format for Play Store)
- **APK** when needed for internal testing or distribution outside Play Store
- **mapping.txt** for stack trace deobfuscation
- **Release notes** auto-generated from conventional commits

### CI Configuration
```yaml
# ✅ GitHub Actions deploy (example using gradle-play-publisher)
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
          PLAY_SERVICE_ACCOUNT_JSON: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
        run: |
          ./gradlew bundleRelease --build-cache \
            publishReleaseBundle \
            -Pplay.serviceAccountJson="${PLAY_SERVICE_ACCOUNT_JSON}" \
            -Pplay.track=internal
```

(Exact tasks/flags depend on the chosen publishing plugin, e.g., `gradle-play-publisher`; this YAML is a conceptual example, not a universal drop-in.)

### Staged Rollout
**Internal** (PR merge) → **Alpha** (5%) → **Beta** (20%) → **Production** (100%)

Automation of promotion is implemented via the Play Developer API / publishing plugin: a CI job checks metrics (via API/reports) and, when conditions are satisfied, increases the rollout.

Example metrics:
- crash rate < 0.5%
- stable ANR rate

### Rollback
Metrics for auto-rollback (implemented via Play Developer API/CI scripts, not built-in Gradle magic tasks):
- Crash-free sessions < 99%
- ANR rate > baseline + 50%
- Critical errors in Crashlytics

```bash
# ✅ Automatic rollback (high-level example logic)
# Requires proper integration with Play Developer API or a publishing plugin.
# Script reads metrics and, on threshold breach, reverts rollout to a previous stable version.
./gradlew publishRelease --track production --user-fraction 0.0
./gradlew publishRelease --track production --version-codes "<previous-stable-version-code>"
```

Keep the last stable AAB + mapping.txt and versionCode history.

---

## Дополнительные Вопросы (RU)

- Как реализовать безопасное управление keystore с использованием Cloud KMS или HashiCorp Vault?
- Какие стратегии использовать для отката при несовместимых миграциях базы данных?
- Как автоматизировать обновление метаданных Play Store и скриншотов?
- Какие метрики использовать для определения здоровых порогов staged rollout?
- Как интегрировать feature flags с прогрессивным деплоем?

## Follow-ups

- How to implement secure keystore management with Cloud KMS or HashiCorp Vault?
- What strategies handle rollback when database migrations are incompatible?
- How to automate Play Store metadata and screenshot updates?
- What metrics define healthy staged rollout thresholds?
- How to integrate feature flags with progressive delivery?

## Ссылки (RU)

- [Publishing](https://developer.android.com/studio/publish)
- https://developer.android.com/studio/publish/app-signing
- https://github.com/Triple-T/gradle-play-publisher

## References

- [Publishing](https://developer.android.com/studio/publish)
- https://developer.android.com/studio/publish/app-signing
- https://github.com/Triple-T/gradle-play-publisher

## Связанные Вопросы (RU)

### База (Prerequisites)
- [[q-build-optimization-gradle--android--medium]]
- [[q-android-lint-tool--android--medium]]

### Связанные (Related)
- [[q-android-release-pipeline-cicd--android--hard]]
- [[q-app-store-optimization--android--medium]]

### Продвинутое (Advanced)
- Стратегии кэширования сборок в multi-module проектах
- Интеграция feature flags с rollout
- Автоматизированное A/B тестирование в релизах

## Related Questions

### Prerequisites
- [[q-build-optimization-gradle--android--medium]] - Gradle optimization for CI
- [[q-android-lint-tool--android--medium]] - Static analysis in CI

### Related
- [[q-android-release-pipeline-cicd--android--hard]] - End-to-end Android release CI/CD
- [[q-app-store-optimization--android--medium]] - Play Store optimization

### Advanced
- Multi-module build caching strategies
- Feature flags with rollout integration
- Automated A/B testing in releases
