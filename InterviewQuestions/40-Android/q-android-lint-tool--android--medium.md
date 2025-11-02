---
id: android-121
title: Android Lint Tool / Инструмент Android Lint
aliases: ["Android Lint Tool", "Инструмент Android Lint"]
topic: android
subtopics: [gradle, static-analysis, build-variants]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-gradle-build-system--android--medium, q-android-testing-strategies--android--medium, q-proguard-r8--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/gradle, android/static-analysis, android/build-variants, static-analysis, code-quality, difficulty/medium]
sources: [https://developer.android.com/studio/write/lint]
date created: Thursday, October 30th 2025, 11:26:40 am
date modified: Thursday, October 30th 2025, 12:42:49 pm
---

# Вопрос (RU)
> Что такое Android Lint, его основные возможности и методы настройки для проекта?

# Question (EN)
> What is Android Lint, its core capabilities, and how to configure it for a project?

---

## Ответ (RU)

**Android Lint** — встроенный инструмент статического анализа для обнаружения проблем кода, ресурсов и конфигурации без запуска приложения.

**Основные категории проверок:**
- **Correctness** — логические ошибки (NPE, неправильные callbacks)
- **Security** — хардкод credentials, небезопасные API
- **Performance** — утечки памяти, неэффективный код
- **Usability** — доступность, missing translations
- **Internationalization** — hardcoded text, неверная работа с locale

**Конфигурация через Gradle DSL:**

```kotlin
// ✅ Современная настройка
android {
    lint {
        checkReleaseBuilds = true
        abortOnError = false

        disable += listOf("ObsoleteSdkInt", "TypographyFractions")
        enable += listOf("RtlHardcoded", "UnusedResources")
    }
}
```

**Конфигурация через lint.xml:**

```xml
<!-- ✅ Детальные правила на уровне проекта -->
<lint>
    <issue id="HardcodedText" severity="error" />
    <issue id="UnusedResources" severity="warning" />
    <issue id="IconMissingDensityFolder" severity="ignore" />
</lint>
```

**Подавление в коде (минимально):**

```kotlin
// ✅ Локальное подавление с обоснованием
@SuppressLint("SetTextI18n")  // Debug UI only
textView.text = "Value: $value"

// ❌ Широкое подавление без причины
@SuppressLint("all")  // Никогда так не делайте
```

**Baseline для legacy проектов:**

```kotlin
// ✅ Игнорируем старые проблемы, ловим новые
android {
    lint {
        baseline = file("lint-baseline.xml")
    }
}

// Генерация baseline:
// ./gradlew lintBaseline
```

**Запуск через Gradle:**

```bash
# Полный анализ проекта
./gradlew lint

# Только для debug варианта
./gradlew lintDebug
```

## Answer (EN)

**Android Lint** is a built-in static analysis tool that detects code, resource, and configuration issues without running the application.

**Core check categories:**
- **Correctness** — logic errors (NPE, wrong callbacks)
- **Security** — hardcoded credentials, insecure APIs
- **Performance** — memory leaks, inefficient code
- **Usability** — accessibility, missing translations
- **Internationalization** — hardcoded text, incorrect locale handling

**Configuration via Gradle DSL:**

```kotlin
// ✅ Modern configuration
android {
    lint {
        checkReleaseBuilds = true
        abortOnError = false

        disable += listOf("ObsoleteSdkInt", "TypographyFractions")
        enable += listOf("RtlHardcoded", "UnusedResources")
    }
}
```

**Configuration via lint.xml:**

```xml
<!-- ✅ Detailed project-level rules -->
<lint>
    <issue id="HardcodedText" severity="error" />
    <issue id="UnusedResources" severity="warning" />
    <issue id="IconMissingDensityFolder" severity="ignore" />
</lint>
```

**In-code suppression (use sparingly):**

```kotlin
// ✅ Local suppression with justification
@SuppressLint("SetTextI18n")  // Debug UI only
textView.text = "Value: $value"

// ❌ Broad suppression without reason
@SuppressLint("all")  // Never do this
```

**Baseline for legacy projects:**

```kotlin
// ✅ Ignore existing issues, catch new ones
android {
    lint {
        baseline = file("lint-baseline.xml")
    }
}

// Generate baseline:
// ./gradlew lintBaseline
```

**Execution via Gradle:**

```bash
# Full project analysis
./gradlew lint

# Debug variant only
./gradlew lintDebug
```

---

## Follow-ups

- How to create custom Lint rules for project-specific architectural violations?
- What is the performance impact of running Lint in CI/CD pipelines?
- How does Lint baseline work for large legacy codebases with thousands of violations?
- Can Lint detect runtime issues or only compile-time problems?
- How to integrate Lint reports with code review tools like Danger or GitHub Actions?

## References

- [[c-gradle]] — Build system fundamentals
- [[c-static-analysis]] — Static analysis principles
- https://developer.android.com/studio/write/lint — Official documentation
- https://github.com/googlesamples/android-custom-lint-rules — Custom rules examples

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
