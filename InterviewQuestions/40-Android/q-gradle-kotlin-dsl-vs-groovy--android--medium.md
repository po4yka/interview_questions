---
id: 20251012-1227145
title: "Gradle Kotlin DSL vs Groovy"
aliases: []

# Classification
topic: android
subtopics: [gradle, kotlin-dsl, groovy, build-tools]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/gradle, android/kotlin-dsl, android/groovy, android/build-tools, difficulty/medium]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: [q-what-is-workmanager--android--medium, q-how-does-jetpackcompose-work--android--medium, q-compose-custom-animations--jetpack-compose--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [en, ru, android/gradle, android/kotlin-dsl, android/groovy, android/build-tools, difficulty/medium]
---
# Question (EN)
> What are the differences between Gradle Kotlin DSL and Groovy? When to use each?
# Вопрос (RU)
> Какие различия между Gradle Kotlin DSL и Groovy? Когда использовать каждый?

---

## Answer (EN)

**Gradle Kotlin DSL** (.gradle.kts) provides type-safe build scripts with IDE support. **Groovy** (.gradle) is more concise but lacks type safety.

### Syntax Comparison

**Groovy:**

```groovy
// build.gradle
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.example.app'
    compileSdk 34

    defaultConfig {
        applicationId "com.example.app"
        minSdk 24
        targetSdk 34
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.2'
}
```

**Kotlin DSL:**

```kotlin
// build.gradle.kts
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
}
```

### Key Differences

| Feature | Kotlin DSL | Groovy |
|---------|-----------|--------|
| **File extension** | .gradle.kts | .gradle |
| **Type safety** |  Compile-time |  Runtime only |
| **IDE support** |  Autocomplete, refactoring |  Limited |
| **Performance** | Slower first build | Faster first build |
| **Syntax** | More verbose | More concise |
| **String quotes** | Required ("") | Optional |
| **Assignment** | = required | = optional |

### Advantages of Kotlin DSL

**1. Type safety:**

```kotlin
// GOOD - Compile error if wrong type
android {
    compileSdk = "34"  // Compile error: Type mismatch
}

// Groovy - No error until runtime
android {
    compileSdk "34"  //  Works but wrong type
}
```

**2. IDE autocomplete:**

```kotlin
android {
    default  // IDE suggests: defaultConfig, defaultPublishConfig
}
```

**3. Refactoring support:**

```kotlin
// Rename variable - all usages updated
val myMinSdk = 24
android.defaultConfig.minSdk = myMinSdk
```

### Version Catalogs (Recommended for both)

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "1.9.20"
compose = "1.5.4"

[libraries]
androidx-core = { module = "androidx.core:core-ktx", version = "1.12.0" }
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }

[plugins]
android-application = { id = "com.android.application", version = "8.1.4" }
```

**Kotlin DSL:**

```kotlin
dependencies {
    implementation(libs.androidx.core)
    implementation(libs.compose.ui)
}
```

**Groovy:**

```groovy
dependencies {
    implementation libs.androidx.core
    implementation libs.compose.ui
}
```

### When to Use Each

**Use Kotlin DSL when:**
- New projects
- Large team (type safety helps)
- Complex build logic
- Want refactoring support

**Use Groovy when:**
- Legacy projects (migration cost)
- Simple build scripts
- Build performance critical
- Team unfamiliar with Kotlin

**English Summary**: Kotlin DSL (.gradle.kts): type-safe, IDE support, autocomplete, refactoring. Groovy (.gradle): more concise, faster first build, no type safety. Kotlin DSL uses `=` for assignment, requires quotes. Both support version catalogs. Use Kotlin DSL for new projects, Groovy for legacy.

## Ответ (RU)

**Gradle Kotlin DSL** (.gradle.kts) предоставляет типобезопасные build скрипты с поддержкой IDE. **Groovy** (.gradle) более лаконичен но не имеет типобезопасности.

### Ключевые различия

| Функция | Kotlin DSL | Groovy |
|---------|-----------|--------|
| **Расширение файла** | .gradle.kts | .gradle |
| **Типобезопасность** |  Во время компиляции |  Только во время выполнения |
| **Поддержка IDE** |  Автодополнение, рефакторинг |  Ограниченная |
| **Синтаксис** | Более многословный | Более лаконичный |
| **Присваивание** | = обязательно | = опционально |

### Преимущества Kotlin DSL

**1. Типобезопасность:**

```kotlin
// ХОРОШО - Ошибка компиляции если неправильный тип
android {
    compileSdk = "34"  // Ошибка компиляции: Type mismatch
}
```

**2. Автодополнение IDE**
**3. Поддержка рефакторинга**

### Когда использовать каждый

**Используйте Kotlin DSL когда:**
- Новые проекты
- Большая команда (типобезопасность помогает)
- Сложная build логика

**Используйте Groovy когда:**
- Legacy проекты (стоимость миграции)
- Простые build скрипты
- Команда не знакома с Kotlin

**Краткое содержание**: Kotlin DSL (.gradle.kts): типобезопасный, поддержка IDE, автодополнение, рефакторинг. Groovy (.gradle): более лаконичен, быстрее первая сборка, нет типобезопасности. Kotlin DSL использует `=` для присваивания, требует кавычки. Используйте Kotlin DSL для новых проектов, Groovy для legacy.

---

## References
- [Gradle Kotlin DSL](https://docs.gradle.org/current/userguide/kotlin_dsl.html)

## Related Questions

### Related (Medium)
- [[q-build-optimization-gradle--gradle--medium]] - Gradle
- [[q-proguard-r8--android--medium]] - Build Tools
- [[q-annotation-processing--android--medium]] - Annotation Processing

### Advanced (Harder)
- [[q-multi-module-best-practices--android--hard]] - Architecture
