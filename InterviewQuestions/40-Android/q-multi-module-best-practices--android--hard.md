---
id: android-018
title: "Multi-module Architecture Best Practices / Лучшие практики мульти-модульной архитектуры"
aliases: ["Multi-module Architecture", "Мульти-модульная архитектура"]
topic: android
subtopics: [architecture-clean, architecture-modularization, gradle]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
sources: ["https://github.com/amitshekhariitbhu/android-interview-questions"]
status: draft
moc: moc-android
related: [c-modularization, c-gradle, q-android-jetpack-overview--android--easy, q-how-compose-draws-on-screen--android--hard]
created: 2025-10-06
updated: 2025-11-10
tags: [android/architecture-clean, android/architecture-modularization, android/gradle, difficulty/hard]

---

# Вопрос (RU)
> Какие лучшие практики для мульти-модульной архитектуры в Android? Когда и зачем её использовать?

# Question (EN)
> What are best practices for multi-module architecture in Android? When and why to use it?

---

## Ответ (RU)

[[c-modularization|Мульти-модульная архитектура]] разделяет приложение на независимые модули для масштабируемости, более быстрых сборок и параллельной разработки.

### Типы Модулей

**1. app** - Главный модуль приложения (`:app`), связывает feature-модули и навигацию
**2. feature** - Изолированные фичи (auth, profile, settings)
**3. core** - Переиспользуемые утилиты (ui, network, database)
**4. data** - Слой данных с [[c-repository-pattern|repository pattern]]

```text
app/
 ├── app/                # Главный модуль (:app)
 ├── feature/
 │   ├── auth/          # ✅ Независимый feature
 │   ├── profile/       # ✅ Независимый feature
 │   └── settings/
 ├── core/
 │   ├── ui/            # Общие UI компоненты
 │   ├── network/       # Сетевой слой
 │   └── database/
 └── data/
     ├── user/          # Данные пользователя
     └── products/
```

### Правила Зависимостей

**Критическое правило**: Feature-модули НЕ зависят друг от друга напрямую.

```kotlin
// ❌ ПЛОХО - Feature зависит от feature
// :feature:auth -> :feature:profile

// ✅ ХОРОШО - Features зависят только от core/data
// :feature:auth -> :core:ui, :data:user
// :feature:profile -> :core:ui, :data:user
```

**Коммуникация через [[c-dependency-injection|инверсию зависимостей]]** (псевдокод для иллюстрации):

```kotlin
// core/navigation
interface Navigator {
    fun navigateToProfile(userId: String)
}

// feature/auth - использует интерфейс
class LoginViewModel(private val navigator: Navigator) {
    fun onLoginSuccess(userId: String) {
        // ✅ Не знает о feature:profile
        navigator.navigateToProfile(userId)
    }
}

// app - реализует интерфейс
class AppNavigator(private val navController: NavController) : Navigator {
    override fun navigateToProfile(userId: String) {
        // Связывает features (детали NavController опущены)
        navController.navigate("profile/$userId")
    }
}
```

### Лучшие Практики

**1. Convention plugins** для стандартизации [[c-gradle|Gradle]] конфигурации:

```kotlin
// buildSrc/.../AndroidFeatureConventionPlugin.kt
// (или предпочтительно отдельный convention-проект через includedBuild)
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            // ✅ Единая конфигурация для всех feature-модулей
            pluginManager.apply("com.android.library")
            extensions.configure<LibraryExtension> {
                compileSdk = 34
                defaultConfig.minSdk = 24
            }
        }
    }
}
```

**2. Version catalogs** для управления зависимостями (упрощённый пример):

```toml
# gradle/libs.versions.toml
[versions]
compose = "1.7.0"

[libraries]
androidx-compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
hilt-android = { module = "com.google.dagger:hilt-android", version = "2.52" }
```

```kotlin
// build.gradle.kts
dependencies {
    // ✅ Централизованные версии через aliases
    implementation(libs.androidx.compose.ui)
}
```

**3. API vs implementation**:

```kotlin
dependencies {
    // ✅ implementation - скрывает транзитивные зависимости
    implementation(project(":core:ui"))

    // ❌ api - экспонирует транзитивные зависимости всем потребителям, используйте осознанно
    api(project(":core:network"))
}
```

### Когда Использовать

(Практические ориентиры, а не жёсткие правила.)

**Используйте, когда:**
- Команда 5+ разработчиков
- Кодовая база около 50 000+ строк или активно растёт
- Несколько приложений с общим кодом
- Долгие сборки (например, > 5 минут) мешают развитию

**Можно не усложнять архитектуру, когда:**
- Маленькие приложения (< 10 000 строк)
- Прототипы и MVP
- Единственный разработчик и короткие времена сборки

### Типичные Ошибки

**1. Циклические зависимости**:
```kotlin
// ❌ ПЛОХО - цикл
// :feature:auth -> :core:ui -> :feature:auth
```

**2. Слишком мелкая гранулярность**:
```kotlin
// ❌ ПЛОХО - избыточное разделение
:feature:auth:login
:feature:auth:register

// ✅ ХОРОШО - логичная группировка
:feature:auth
```

## Answer (EN)

[[c-modularization|Multi-module architecture]] splits the app into independent modules for scalability, faster builds, and parallel development.

### Module Types

**1. app** - Main application module (`:app`), wires feature modules and navigation
**2. feature** - Isolated features (auth, profile, settings)
**3. core** - Reusable utilities (ui, network, database)
**4. data** - Data layer with [[c-repository-pattern|repository pattern]]

```text
app/
 ├── app/                # Main module (:app)
 ├── feature/
 │   ├── auth/          # ✅ Independent feature
 │   ├── profile/       # ✅ Independent feature
 │   └── settings/
 ├── core/
 │   ├── ui/            # Shared UI components
 │   ├── network/       # Network layer
 │   └── database/
 └── data/
     ├── user/          # User data
     └── products/
```

### Dependency Rules

**Critical rule**: Feature modules do NOT depend on each other directly.

```kotlin
// ❌ BAD - Feature depends on feature
// :feature:auth -> :feature:profile

// ✅ GOOD - Features depend only on core/data
// :feature:auth -> :core:ui, :data:user
// :feature:profile -> :core:ui, :data:user
```

**Communication via [[c-dependency-injection|dependency inversion]]** (pseudo-code for illustration):

```kotlin
// core/navigation
interface Navigator {
    fun navigateToProfile(userId: String)
}

// feature/auth - uses interface
class LoginViewModel(private val navigator: Navigator) {
    fun onLoginSuccess(userId: String) {
        // ✅ Doesn't know about feature:profile
        navigator.navigateToProfile(userId)
    }
}

// app - implements interface
class AppNavigator(private val navController: NavController) : Navigator {
    override fun navigateToProfile(userId: String) {
        // Wires features (NavController wiring omitted)
        navController.navigate("profile/$userId")
    }
}
```

### Best Practices

**1. Convention plugins** for standardized [[c-gradle|Gradle]] configuration:

```kotlin
// buildSrc/.../AndroidFeatureConventionPlugin.kt
// (or preferably a separate convention module via includedBuild)
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            // ✅ Single configuration for all feature modules
            pluginManager.apply("com.android.library")
            extensions.configure<LibraryExtension> {
                compileSdk = 34
                defaultConfig.minSdk = 24
            }
        }
    }
}
```

**2. Version catalogs** for dependency management (simplified example):

```toml
# gradle/libs.versions.toml
[versions]
compose = "1.7.0"

[libraries]
androidx-compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
hilt-android = { module = "com.google.dagger:hilt-android", version = "2.52" }
```

```kotlin
// build.gradle.kts
dependencies {
    // ✅ Centralized versions via aliases
    implementation(libs.androidx.compose.ui)
}
```

**3. API vs implementation**:

```kotlin
dependencies {
    // ✅ implementation - hides transitive deps
    implementation(project(":core:ui"))

    // ❌ api - exposes transitive deps to all consumers; use intentionally
    api(project(":core:network"))
}
```

### When to Use

(Pragmatic guidelines, not strict thresholds.)

**Use when:**
- Team of ~5+ developers
- Codebase around 50,000+ LOC or actively growing
- Multiple apps share code
- Long build times (e.g., > 5 minutes) slow down development

**You may skip complex modularization when:**
- Small apps (<10,000 LOC)
- Prototypes and MVPs
- Solo developers with fast builds

### Common Mistakes

**1. Circular dependencies**:
```kotlin
// ❌ BAD - circular
// :feature:auth -> :core:ui -> :feature:auth
```

**2. Over-granular modules**:
```kotlin
// ❌ BAD - excessive splitting
:feature:auth:login
:feature:auth:register

// ✅ GOOD - logical grouping
:feature:auth
```

---

## Follow-ups

- How to handle shared UI themes across feature modules?
- What strategies prevent circular dependencies in large module graphs?
- How to test inter-module communication with dependency inversion?
- When to split a feature module into smaller modules?
- How to implement dynamic feature modules for on-demand delivery?

## References

- [[c-modularization]] - Modularization concepts
- [[c-dependency-injection]] - Dependency inversion principle
- [[c-repository-pattern]] - Repository pattern
- [[c-gradle]] - Gradle build system
- [Guide to Android app modularization](https://developer.android.com/topic/modularization)

## Related Questions

### Prerequisites
- [[q-build-optimization-gradle--android--medium]] - Gradle optimization basics
- Understanding Clean Architecture principles
- Gradle Kotlin DSL fundamentals

### Related
- [[q-android-jetpack-overview--android--easy]] - Jetpack components in modules
- [[q-how-compose-draws-on-screen--android--hard]] - Compose in feature modules
- Build configuration and convention plugins
- Dynamic feature modules implementation

### Advanced
- Large-scale multi-module architecture (100+ modules)
- Automated module dependency validation
- Module-level performance optimization
