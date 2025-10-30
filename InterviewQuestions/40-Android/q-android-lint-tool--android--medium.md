---
id: 20251012-122748
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
updated: 2025-10-29
tags: [android/gradle, android/static-analysis, android/build-variants, static-analysis, code-quality, difficulty/medium]
sources: [https://developer.android.com/studio/write/lint]
---
# Вопрос (RU)
> Что такое Android Lint и как его использовать для анализа кода?

# Question (EN)
> What is Android Lint and how to use it for code analysis?

---

## Ответ (RU)

**Android Lint** — встроенный инструмент статического анализа для обнаружения проблем кода, ресурсов и конфигурации без запуска приложения.

**Основные возможности:**
- Анализ Java/Kotlin/XML файлов на структурные ошибки
- Проверка ресурсов (layouts, drawables, strings) на несоответствия
- Обнаружение проблем безопасности (hardcoded credentials, insecure APIs)
- Выявление неоптимальных паттернов (unused resources, overdraw)
- Настраиваемые правила через lint.xml и Gradle DSL

**Категории проверок:**
- **Correctness** — логические ошибки, NPE, wrong callbacks
- **Security** — хардкод секретов, небезопасные сетевые запросы
- **Performance** — утечки памяти, неэффективный код
- **Usability** — доступность, missing translations
- **Internationalization** — hardcoded text, wrong locale handling

**Конфигурация через lint.xml:**

```xml
<!-- ✅ Project-specific rules -->
<lint>
    <issue id="HardcodedText" severity="error" />
    <issue id="UnusedResources" severity="warning" />
    <issue id="IconMissingDensityFolder" severity="ignore" />
</lint>
```

**Конфигурация через Gradle DSL:**

```kotlin
// ✅ Modern configuration (AGP 7.0+)
android {
    lint {
        checkReleaseBuilds = true
        abortOnError = false
        warningsAsErrors = false

        disable += listOf("TypographyFractions", "ObsoleteSdkInt")
        enable += listOf("RtlHardcoded", "UnusedResources")
    }
}
```

**Подавление в коде (используйте осторожно):**

```kotlin
// ✅ Local suppression with justification
@SuppressLint("SetTextI18n")  // Debug-only code
textView.text = "Value: $value"

// ❌ Broad suppression without explanation
@SuppressLint("all")  // Never do this
class MyActivity : AppCompatActivity()
```

**Запуск и отчёты:**

```bash
# Анализ всего проекта
./gradlew lint

# Конкретный build variant
./gradlew lintDebug

# Baseline для legacy проектов
./gradlew lintBaseline
```

**Baseline для постепенной миграции:**

```kotlin
// ✅ Ignore existing issues, catch new ones
android {
    lint {
        baseline = file("lint-baseline.xml")
    }
}
```

## Answer (EN)

**Android Lint** is a built-in static analysis tool that detects code, resource, and configuration issues without running the application.

**Key capabilities:**
- Analyzes Java/Kotlin/XML files for structural errors
- Validates resources (layouts, drawables, strings) for inconsistencies
- Detects security issues (hardcoded credentials, insecure APIs)
- Identifies inefficient patterns (unused resources, overdraw)
- Customizable rules via lint.xml and Gradle DSL

**Check categories:**
- **Correctness** — logic errors, NPE, wrong callbacks
- **Security** — hardcoded secrets, insecure network calls
- **Performance** — memory leaks, inefficient code
- **Usability** — accessibility, missing translations
- **Internationalization** — hardcoded text, wrong locale handling

**Configuration via lint.xml:**

```xml
<!-- ✅ Project-specific rules -->
<lint>
    <issue id="HardcodedText" severity="error" />
    <issue id="UnusedResources" severity="warning" />
    <issue id="IconMissingDensityFolder" severity="ignore" />
</lint>
```

**Configuration via Gradle DSL:**

```kotlin
// ✅ Modern configuration (AGP 7.0+)
android {
    lint {
        checkReleaseBuilds = true
        abortOnError = false
        warningsAsErrors = false

        disable += listOf("TypographyFractions", "ObsoleteSdkInt")
        enable += listOf("RtlHardcoded", "UnusedResources")
    }
}
```

**In-code suppression (use sparingly):**

```kotlin
// ✅ Local suppression with justification
@SuppressLint("SetTextI18n")  // Debug-only code
textView.text = "Value: $value"

// ❌ Broad suppression without explanation
@SuppressLint("all")  // Never do this
class MyActivity : AppCompatActivity()
```

**Execution and reports:**

```bash
# Analyze entire project
./gradlew lint

# Specific build variant
./gradlew lintDebug

# Generate baseline for legacy projects
./gradlew lintBaseline
```

**Baseline for gradual migration:**

```kotlin
// ✅ Ignore existing issues, catch new ones
android {
    lint {
        baseline = file("lint-baseline.xml")
    }
}
```

---

## Follow-ups

- How to create custom Lint rules for project-specific architectural violations?
- What is the performance impact of running Lint checks in CI/CD pipelines?
- How does Lint baseline work for large legacy codebases?
- Can Lint detect runtime issues or only static problems?
- How to integrate Lint with code review tools (GitHub Actions, Danger)?

## References

- [[c-gradle]] — Gradle build system fundamentals
- [[q-gradle-build-system--android--medium]] — Gradle configuration and build system
- [[q-proguard-r8--android--medium]] — Code optimization and obfuscation
- https://developer.android.com/studio/write/lint — Official documentation
- https://github.com/googlesamples/android-custom-lint-rules — Custom rules examples

## Related Questions

### Prerequisites
- [[q-gradle-build-system--android--medium]] — Understanding Gradle configuration
- Android Studio basics — IDE integration with Lint

### Related
- [[q-android-testing-strategies--android--medium]] — Comprehensive quality assurance
- [[q-proguard-r8--android--medium]] — Code optimization tools
- Build variants and flavors — Lint per configuration

### Advanced
- Custom Lint rule development with PSI (Program Structure Interface)
- Lint baseline strategy for gradual technical debt reduction
- Integrating third-party Lint rules (Detekt, ktlint) into unified analysis