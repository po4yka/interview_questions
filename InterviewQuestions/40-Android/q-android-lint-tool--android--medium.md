---
id: 20251012-122748
title: Android Lint Tool / Инструмент Android Lint
aliases:
- Android Lint Tool
- Инструмент Android Lint
topic: android
subtopics:
- static-analysis
- gradle
- build-variants
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-parcelable-implementation--android--medium
- q-room-vs-sqlite--android--medium
- q-gradle-build-system--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/static-analysis
- android/gradle
- android/build-variants
- difficulty/medium
source: https://github.com/Kirchhoff-/Android-Interview-Questions
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