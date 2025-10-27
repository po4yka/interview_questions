---
id: 20251012-122748
title: Android Lint Tool / Инструмент Android Lint
aliases: [Android Lint Tool, Инструмент Android Lint]
topic: android
subtopics: [build-variants, gradle, static-analysis]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-gradle-build-system--android--medium, q-android-testing-strategies--android--medium]
created: 2025-10-15
updated: 2025-01-27
tags: [android/build-variants, android/gradle, android/static-analysis, difficulty/medium]
sources: [https://developer.android.com/studio/write/lint]
---
# Вопрос (RU)
> Что такое инструмент Android Lint и как он работает?

## Ответ (RU)

**Android Lint** — инструмент статического анализа кода для Android-проектов. Анализирует исходный код без выполнения, выявляя структурные проблемы, баги, уязвимости безопасности и нарушения производительности.

**Основные возможности:**
- Анализ Java/Kotlin/XML без запуска приложения
- Проверка ресурсов (layouts, drawables, strings)
- Настройка правил через `lint.xml` и [[c-gradle]]
- Генерация отчётов с уровнями критичности

**Конфигурация через lint.xml:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<lint>
    <!-- ❌ Игнорировать проверку -->
    <issue id="IconMissingDensityFolder" severity="ignore" />

    <!-- ✅ Повысить уровень критичности -->
    <issue id="HardcodedText" severity="error" />
</lint>
```

**Конфигурация через Gradle:**
```gradle
android {
    lintOptions {
        // ✅ Отключить некритичные проверки
        disable 'TypographyFractions'

        // ✅ Включить важные проверки
        enable 'RtlHardcoded'

        // ❌ Игнорировать все предупреждения
        ignoreWarnings true
        abortOnError false
    }
}
```

**Категории проверок:**
- **Correctness** — логические ошибки, NPE
- **Security** — хардкод секретов, небезопасные практики
- **Performance** — утечки памяти, неэффективные операции
- **Usability** — доступность, UI-проблемы

**Запуск через командную строку:**
```bash
./gradlew lint           # Весь проект
./gradlew lintDebug      # Конкретный вариант сборки
```

---

# Question (EN)
> What is Android Lint tool and how does it work?

## Answer (EN)

**Android Lint** is a static code analysis tool for Android projects. It analyzes source code without execution, detecting structural issues, bugs, security vulnerabilities, and performance violations.

**Key capabilities:**
- Analyzes Java/Kotlin/XML without running the app
- Validates resources (layouts, drawables, strings)
- Configurable via `lint.xml` and [[c-gradle]]
- Generates reports with severity levels

**Configuration via lint.xml:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<lint>
    <!-- ❌ Ignore check -->
    <issue id="IconMissingDensityFolder" severity="ignore" />

    <!-- ✅ Elevate severity level -->
    <issue id="HardcodedText" severity="error" />
</lint>
```

**Configuration via Gradle:**
```gradle
android {
    lintOptions {
        // ✅ Disable non-critical checks
        disable 'TypographyFractions'

        // ✅ Enable important checks
        enable 'RtlHardcoded'

        // ❌ Ignore all warnings
        ignoreWarnings true
        abortOnError false
    }
}
```

**Check categories:**
- **Correctness** — logic errors, NPE
- **Security** — hardcoded secrets, insecure practices
- **Performance** — memory leaks, inefficient operations
- **Usability** — accessibility, UI issues

**Command line execution:**
```bash
./gradlew lint           # Entire project
./gradlew lintDebug      # Specific build variant
```

## Follow-ups

- How to create custom Lint rules for project-specific violations?
- What's the performance impact of enabling all Lint checks in CI/CD?
- How does Lint integrate with Android Studio's real-time analysis?

## References

- [[c-gradle]] — Build system integration
- https://developer.android.com/studio/write/lint
- https://github.com/googlesamples/android-custom-lint-rules

## Related Questions

### Prerequisites
- [[q-gradle-build-system--android--medium]] — Build system fundamentals

### Related
- [[q-android-testing-strategies--android--medium]] — Quality assurance approaches

### Advanced
- Custom Lint rule development for domain-specific checks
- Baseline configuration for legacy projects