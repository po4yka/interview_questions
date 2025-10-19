---
id: 20251012-122748
title: Android Lint Tool / Инструмент Android Lint
aliases: [Android Lint Tool, Инструмент Android Lint]
topic: android
subtopics: [static-analysis, gradle, build-variants]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
created: 2025-10-15
updated: 2025-10-15
tags: [android/static-analysis, android/gradle, android/build-variants, lint, static-analysis, code-quality, gradle, difficulty/medium]
related: [q-parcelable-implementation--android--medium, q-room-vs-sqlite--android--medium, q-gradle-build-system--android--medium]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
---
# Question (EN)
> What do you know about Android Lint?

# Вопрос (RU)
> Что вы знаете о Lint в Android?

---

## Answer (EN)

**Android Lint** is a static code analysis tool that identifies structural problems in Android projects without executing the app. It checks for bugs, performance issues, security vulnerabilities, and code quality problems.

**Static Analysis Theory:**
Static analysis examines code without execution, analyzing syntax, structure, and patterns to detect potential issues. Lint performs this analysis on Android-specific files (Java, Kotlin, XML, resources) to catch problems early in development.

**Lint Architecture:**
- **Source Analysis**: Scans Java/Kotlin/XML files for structural issues
- **Resource Validation**: Checks drawables, layouts, strings for consistency
- **Configuration**: Uses `lint.xml` and Gradle settings to customize checks
- **Reporting**: Generates warnings with severity levels and descriptions

**Basic Lint Configuration:**
```xml
<!-- lint.xml - Project-level configuration -->
<?xml version="1.0" encoding="UTF-8"?>
<lint>
    <!-- Disable specific checks -->
    <issue id="IconMissingDensityFolder" severity="ignore" />

    <!-- Ignore issues in specific files -->
    <issue id="ObsoleteLayoutParam">
        <ignore path="res/layout/activation.xml" />
    </issue>

    <!-- Change severity levels -->
    <issue id="HardcodedText" severity="error" />
</lint>
```

**Gradle Lint Configuration:**
```gradle
android {
    lintOptions {
        // Disable specific checks
        disable 'TypographyFractions', 'TypographyQuotes'

        // Enable specific checks
        enable 'RtlHardcoded', 'RtlCompat', 'RtlEnabled'

        // Control reporting
        quiet true
        abortOnError false
        ignoreWarnings true

        // Generate reports
        htmlReport true
        xmlReport true
        textReport true
    }
}
```

**Common Lint Categories:**
- **Correctness**: Logic errors, null pointer exceptions
- **Security**: Hardcoded secrets, insecure practices
- **Performance**: Memory leaks, inefficient operations
- **Usability**: Accessibility issues, UI problems
- **Internationalization**: Missing translations, locale issues

**Lint Check Levels:**
- **Error**: Critical issues that should be fixed
- **Warning**: Issues that should be addressed
- **Information**: Suggestions for improvement
- **Ignore**: Disabled checks

**Command Line Usage:**
```bash
# Run lint on entire project
./gradlew lint

# Run lint on specific variant
./gradlew lintDebug

# Generate HTML report
./gradlew lintDebug -Dlint.output=lint-results.html
```

## Ответ (RU)

**Android Lint** - это инструмент статического анализа кода, который выявляет структурные проблемы в Android-проектах без выполнения приложения. Проверяет ошибки, проблемы производительности, уязвимости безопасности и качество кода.

**Теория статического анализа:**
Статический анализ исследует код без выполнения, анализируя синтаксис, структуру и паттерны для обнаружения потенциальных проблем. Lint выполняет этот анализ для Android-специфичных файлов (Java, Kotlin, XML, ресурсы) для раннего обнаружения проблем в разработке.

**Архитектура Lint:**
- **Анализ исходного кода**: Сканирует Java/Kotlin/XML файлы на структурные проблемы
- **Валидация ресурсов**: Проверяет drawable, layout, строки на консистентность
- **Конфигурация**: Использует `lint.xml` и настройки Gradle для кастомизации проверок
- **Отчётность**: Генерирует предупреждения с уровнями серьёзности и описаниями

**Базовая конфигурация Lint:**
```xml
<!-- lint.xml - Конфигурация уровня проекта -->
<?xml version="1.0" encoding="UTF-8"?>
<lint>
    <!-- Отключить конкретные проверки -->
    <issue id="IconMissingDensityFolder" severity="ignore" />

    <!-- Игнорировать проблемы в конкретных файлах -->
    <issue id="ObsoleteLayoutParam">
        <ignore path="res/layout/activation.xml" />
    </issue>

    <!-- Изменить уровни серьёзности -->
    <issue id="HardcodedText" severity="error" />
</lint>
```

**Конфигурация Lint в Gradle:**
```gradle
android {
    lintOptions {
        // Отключить конкретные проверки
        disable 'TypographyFractions', 'TypographyQuotes'

        // Включить конкретные проверки
        enable 'RtlHardcoded', 'RtlCompat', 'RtlEnabled'

        // Управление отчётностью
        quiet true
        abortOnError false
        ignoreWarnings true

        // Генерировать отчёты
        htmlReport true
        xmlReport true
        textReport true
    }
}
```

**Общие категории Lint:**
- **Корректность**: Логические ошибки, исключения null pointer
- **Безопасность**: Жёстко закодированные секреты, небезопасные практики
- **Производительность**: Утечки памяти, неэффективные операции
- **Удобство использования**: Проблемы доступности, UI проблемы
- **Интернационализация**: Отсутствующие переводы, проблемы локали

**Уровни проверок Lint:**
- **Error**: Критические проблемы, которые должны быть исправлены
- **Warning**: Проблемы, которые должны быть решены
- **Information**: Предложения по улучшению
- **Ignore**: Отключённые проверки

**Использование из командной строки:**
```bash
# Запустить lint на весь проект
./gradlew lint

# Запустить lint на конкретный вариант
./gradlew lintDebug

# Генерировать HTML отчёт
./gradlew lintDebug -Dlint.output=lint-results.html
```

---

## Follow-ups

- How to integrate Lint with CI/CD pipelines?
- Custom Lint rules development and implementation?
- Lint performance impact on large projects?

## References

- https://developer.android.com/studio/write/lint
- https://developer.android.com/studio/write/lint#gradle

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-build-system--android--medium]] - Build system basics
### Related (Medium)
- [[q-parcelable-implementation--android--medium]] - Code quality
- [[q-room-vs-sqlite--android--medium]] - Database implementation
- [[q-android-testing-strategies--android--medium]] - Testing approaches
