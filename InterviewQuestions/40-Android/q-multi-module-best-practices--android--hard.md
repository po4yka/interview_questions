---
id: 20251006-014
title: "Multi-module Architecture Best Practices / Лучшие практики мульти-модульной архитектуры"
aliases: []

# Classification
topic: android
subtopics: [architecture, multi-module, gradle, scalability]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, architecture, multi-module, gradle, scalability, difficulty/hard]
---

# Question (EN)
> What are best practices for multi-module architecture in Android? When and why to use it?

# Вопрос (RU)
> Какие лучшие практики для мульти-модульной архитектуры в Android? Когда и зачем её использовать?

---

## Answer (EN)

**Multi-module architecture** splits app into independent modules for better scalability, build times, and team collaboration.

### Module Types

**1. app** - Main application module
**2. feature modules** - Independent features
**3. core modules** - Shared utilities
**4. data modules** - Data layer

```
app/
├── app/                    # Main app module
├── feature/
│   ├── auth/              # Authentication feature
│   ├── profile/           # Profile feature
│   └── settings/          # Settings feature
├── core/
│   ├── ui/                # Shared UI components
│   ├── network/           # Network layer
│   └── database/          # Database layer
└── data/
    ├── user/              # User data
    └── products/          # Products data
```

### Module Structure

```kotlin
// feature/auth/build.gradle.kts
plugins {
    id("com.android.library")
    id("kotlin-android")
}

dependencies {
    // Core modules
    implementation(project(":core:ui"))
    implementation(project(":core:network"))

    // Data modules
    implementation(project(":data:user"))

    // External dependencies
    implementation(libs.androidx.compose)
    implementation(libs.hilt)
}
```

### Dependency Rules

**1. Feature modules should NOT depend on each other**

```kotlin
// ❌ BAD - Feature depends on feature
// :feature:auth -> :feature:profile  // NO!

// ✅ GOOD - Features depend on core/data only
// :feature:auth -> :core:ui
// :feature:auth -> :data:user
// :feature:profile -> :core:ui
// :feature:profile -> :data:user
```

**2. Use dependency inversion for feature communication**

```kotlin
// core/navigation
interface Navigator {
    fun navigateToProfile(userId: String)
}

// feature/auth - uses interface
class LoginViewModel(private val navigator: Navigator) {
    fun onLoginSuccess(userId: String) {
        navigator.navigateToProfile(userId)
    }
}

// app module - implements interface
class AppNavigator(private val navController: NavController) : Navigator {
    override fun navigateToProfile(userId: String) {
        navController.navigate("profile/$userId")
    }
}
```

### Benefits

**1. Faster build times** - Only modified modules rebuild
**2. Better encapsulation** - Clear boundaries
**3. Parallel development** - Teams work independently
**4. Code reusability** - Share modules across apps
**5. Dynamic delivery** - On-demand features

### Best Practices

**1. Convention plugins for shared config:**

```kotlin
// buildSrc/src/main/kotlin/AndroidFeatureConventionPlugin.kt
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("com.android.library")
            pluginManager.apply("org.jetbrains.kotlin.android")

            extensions.configure<LibraryExtension> {
                compileSdk = 34
                defaultConfig.minSdk = 24
            }
        }
    }
}

// feature/auth/build.gradle.kts
plugins {
    id("android.feature")  // Applies all common config
}
```

**2. Version catalog for dependencies:**

```toml
# gradle/libs.versions.toml
[versions]
compose = "1.5.4"
hilt = "2.48"

[libraries]
androidx-compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }

# build.gradle.kts
dependencies {
    implementation(libs.androidx.compose.ui)
    implementation(libs.hilt.android)
}
```

**English Summary**: Multi-module: split app into feature/core/data modules. Benefits: faster builds, better encapsulation, parallel development. Rules: features don't depend on features, use dependency inversion for communication. Best practices: convention plugins, version catalogs, clear module boundaries. When to use: large teams, 50k+ lines of code, multiple apps sharing code.

## Ответ (RU)

**Мульти-модульная архитектура** разделяет приложение на независимые модули для лучшей масштабируемости, времени сборки и командной работы.

### Типы модулей

**1. app** - Основной модуль приложения
**2. feature модули** - Независимые функции
**3. core модули** - Общие утилиты
**4. data модули** - Слой данных

### Правила зависимостей

**1. Feature модули НЕ должны зависеть друг от друга**

```kotlin
// ❌ ПЛОХО - Feature зависит от feature
// :feature:auth -> :feature:profile  // НЕТ!

// ✅ ХОРОШО - Features зависят только от core/data
// :feature:auth -> :core:ui
// :feature:auth -> :data:user
```

**2. Используйте инверсию зависимостей для коммуникации между features**

### Преимущества

**1. Быстрее сборка** - Только измененные модули пересобираются
**2. Лучшая инкапсуляция** - Четкие границы
**3. Параллельная разработка** - Команды работают независимо
**4. Переиспользование кода** - Разделяйте модули между приложениями

**Краткое содержание**: Мульти-модуль: разделить app на feature/core/data модули. Преимущества: быстрее сборки, лучшая инкапсуляция, параллельная разработка. Правила: features не зависят от features, использовать инверсию зависимостей для коммуникации. Лучшие практики: convention plugins, version catalogs, четкие границы модулей.

---

## References
- [Guide to Android app modularization](https://developer.android.com/topic/modularization)

## Related Questions
- [[q-clean-architecture-android--android--hard]]
