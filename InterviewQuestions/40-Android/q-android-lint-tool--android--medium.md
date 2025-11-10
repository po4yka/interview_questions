---
id: android-121
title: Android Lint Tool / Инструмент Android Lint
aliases: [Android Lint Tool, Инструмент Android Lint]
topic: android
subtopics:
  - build-variants
  - static-analysis
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-components
  - q-android-testing-strategies--android--medium
  - q-gradle-build-system--android--medium
  - q-proguard-r8--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/build-variants, android/static-analysis, code-quality, difficulty/medium, static-analysis]
sources:
  - "https://developer.android.com/studio/write/lint"
---

# Вопрос (RU)
> Что такое Android Lint, его основные возможности и методы настройки для проекта?

# Question (EN)
> What is Android Lint, its core capabilities, and how to configure it for a project?

---

## Ответ (RU)

**Android Lint** — встроенный инструмент статического анализа для обнаружения потенциальных проблем в коде, ресурсах и конфигурации без выполнения приложения (то есть не обнаруживает чисто рантайм-ошибки).

**Основные категории проверок:**
- **Correctness** — логические и API-ошибки (NPE, неправильные callbacks, неверное использование API)
- **Security** — хардкод credentials, небезопасные API, использование слабой криптографии
- **Performance** — потенциальные утечки памяти, неэффективный или избыточный код
- **Usability** — доступность, отсутствие важных ресурсов (например, missing translations)
- **Internationalization** — hardcoded text, неверная работа с locale и форматом

**Конфигурация через Gradle DSL (AGP 7+/8+):**

```kotlin
// Современная базовая настройка через lint-DSL
android {
    lint {
        checkReleaseBuilds = true
        abortOnError = false

        // Управление правилами
        disable("ObsoleteSdkInt", "TypographyFractions")
        enable("RtlHardcoded", "UnusedResources")
    }
}
```

**Конфигурация через lint.xml:**

```xml
<!-- Детальные правила на уровне проекта -->
<lint>
    <issue id="HardcodedText" severity="error" />
    <issue id="UnusedResources" severity="warning" />
    <issue id="IconMissingDensityFolder" severity="ignore" />
</lint>
```

**Подавление в коде (минимально):**

```kotlin
// Локальное подавление с обоснованием
@SuppressLint("SetTextI18n")  // Только для debug UI / осознанный кейс
textView.text = "Value: $value"

// Широкое подавление без причины
@SuppressLint("all")  // Не используйте без крайней необходимости
```

**Baseline для legacy проектов:**

```kotlin
// Игнорируем существующие проблемы, ловим новые
android {
    lint {
        baseline = file("lint-baseline.xml")
    }
}

// Генерация или обновление baseline (AGP 7+/8+):
// Выполните lint-задачу с обновлением baseline, например:
// ./gradlew lintDebug --update-baseline
// или соответствующую variant-специфичную lint-задачу.
```

**Запуск через Gradle:**

```bash
# Полный анализ проекта
./gradlew lint

# Только для debug варианта
./gradlew lintDebug
```

См. также: [[c-android-components]] для контекста компонентов и их взаимодействия с Lint.

## Answer (EN)

**Android Lint** is a built-in static analysis tool that detects potential issues in code, resources, and configuration without running the application (i.e., it does not catch purely runtime-only problems).

**Core check categories:**
- **Correctness** — logic/API issues (NPE, wrong callbacks, incorrect API usage)
- **Security** — hardcoded credentials, insecure APIs, weak cryptography
- **Performance** — potential memory leaks, inefficient or excessive code
- **Usability** — accessibility, missing important resources (e.g., missing translations)
- **Internationalization** — hardcoded text, incorrect locale/format handling

**Configuration via Gradle DSL (AGP 7+/8+):**

```kotlin
// Modern basic configuration via lint DSL
android {
    lint {
        checkReleaseBuilds = true
        abortOnError = false

        // Rule management
        disable("ObsoleteSdkInt", "TypographyFractions")
        enable("RtlHardcoded", "UnusedResources")
    }
}
```

**Configuration via lint.xml:**

```xml
<!-- Detailed project-level rules -->
<lint>
    <issue id="HardcodedText" severity="error" />
    <issue id="UnusedResources" severity="warning" />
    <issue id="IconMissingDensityFolder" severity="ignore" />
</lint>
```

**In-code suppression (use sparingly):**

```kotlin
// Local suppression with justification
@SuppressLint("SetTextI18n")  // Debug UI only / intentional exception
textView.text = "Value: $value"

// Broad suppression without reason
@SuppressLint("all")  // Avoid unless absolutely necessary
```

**Baseline for legacy projects:**

```kotlin
// Ignore existing issues, catch new ones
android {
    lint {
        baseline = file("lint-baseline.xml")
    }
}

// Generate or update baseline (AGP 7+/8+):
// Run a lint task with baseline update, for example:
// ./gradlew lintDebug --update-baseline
// or the corresponding variant-specific lint task.
```

**Execution via Gradle:**

```bash
# Full project analysis
./gradlew lint

# Debug variant only
./gradlew lintDebug
```

See also: [[c-android-components]] for context on components and how Lint interacts with their usage.

---

## Дополнительные вопросы (RU)

- Как создавать собственные правила Lint для проверки архитектурных ограничений проекта?
- Каков влияние запуска Lint на производительность CI/CD-конвейера?
- Как работает baseline Lint для крупных legacy-кодовых баз с тысячами нарушений?
- Может ли Lint обнаруживать runtime-проблемы или только проблемы на этапе сборки/анализа?
- Как интегрировать отчеты Lint с инструментами code review, такими как Danger или GitHub Actions?

## Follow-ups

- How to create custom Lint rules for project-specific architectural violations?
- What is the performance impact of running Lint in CI/CD pipelines?
- How does Lint baseline work for large legacy codebases with thousands of violations?
- Can Lint detect runtime issues or only compile-time problems?
- How to integrate Lint reports with code review tools like Danger or GitHub Actions?

## Ссылки (RU)

- "https://developer.android.com/studio/write/lint" — Официальная документация
- "https://github.com/googlesamples/android-custom-lint-rules" — Примеры кастомных правил

## References

- https://developer.android.com/studio/write/lint — Official documentation
- https://github.com/googlesamples/android-custom-lint-rules — Custom rules examples

## Связанные вопросы (RU)

### Предварительные знания
- [[q-gradle-build-system--android--medium]] — Понимание Gradle-конфигурации и build variants

### Связанные
- [[q-android-testing-strategies--android--medium]] — Стратегии обеспечения качества и тестирования
- [[q-proguard-r8--android--medium]] — Инструменты оптимизации и обфускации кода
- Инструменты статического анализа (Detekt, ktlint, SonarQube)

### Продвинутые
- Разработка собственных Lint-детекторов с использованием PSI (Program Structure Interface)
- Стратегии использования baseline Lint для поэтапного снижения технического долга
- Интеграция Lint в CI/CD с параллельным запуском по модулям

## Related Questions

### Prerequisites
- [[q-gradle-build-system--android--medium]] — Understanding Gradle configuration and build variants

### Related
- [[q-android-testing-strategies--android--medium]] — Comprehensive quality assurance approaches
- [[q-proguard-r8--android--medium]] — Code optimization and obfuscation tools
- Static code analysis tools (Detekt, ktlint, SonarQube)

### Advanced
- Writing custom Lint detectors using PSI (Program Structure Interface)
- Lint baseline strategies for gradual technical debt reduction
- CI/CD integration with parallel Lint execution per module
