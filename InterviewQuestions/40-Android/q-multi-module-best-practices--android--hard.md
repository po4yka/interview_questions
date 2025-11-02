---
id: android-018
title: "Multi-module Architecture Best Practices / Лучшие практики мульти-модульной архитектуры"
aliases: ["Multi-module Architecture", "Мульти-модульная архитектура"]

# Classification
topic: android
subtopics: [architecture-clean, architecture-modularization, gradle]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: [https://github.com/amitshekhariitbhu/android-interview-questions]

# Workflow & relations
status: draft
moc: moc-android
related: [q-android-jetpack-overview--android--easy, q-how-compose-draws-on-screen--android--hard]

# Timestamps
created: 2025-10-06
updated: 2025-01-27

tags: [android/architecture-clean, android/architecture-modularization, android/gradle, difficulty/hard]
---
# Вопрос (RU)
> Какие лучшие практики для мульти-модульной архитектуры в Android? Когда и зачем её использовать?

# Question (EN)
> What are best practices for multi-module architecture in Android? When and why to use it?

---

## Ответ (RU)

[[c-modularization|Мульти-модульная архитектура]] разделяет приложение на независимые модули для масштабируемости, быстрой сборки и параллельной разработки.

### Типы модулей

**1. app** - Главный модуль приложения, связывает feature модули
**2. feature** - Изолированные функции (auth, profile, settings)
**3. core** - Переиспользуемые утилиты (ui, network, database)
**4. data** - Слой данных с [[c-repository-pattern|repository pattern]]

```text
app/
 ├── app/                # Главный модуль
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

### Правила зависимостей

**Критическое правило**: Feature модули НЕ зависят друг от друга

```kotlin
// ❌ ПЛОХО - Feature зависит от feature
// :feature:auth -> :feature:profile

// ✅ ХОРОШО - Features зависят только от core/data
// :feature:auth -> :core:ui, :data:user
// :feature:profile -> :core:ui, :data:user
```

**Коммуникация через [[c-dependency-inversion|инверсию зависимостей]]**:

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
class AppNavigator : Navigator {
    override fun navigateToProfile(userId: String) {
        // Связывает features
        navController.navigate("profile/$userId")
    }
}
```

### Лучшие практики

**1. Convention plugins** для стандартизации [[c-gradle|Gradle]] конфигурации:

```kotlin
// buildSrc/.../AndroidFeatureConventionPlugin.kt
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            // ✅ Единая конфигурация для всех features
            pluginManager.apply("com.android.library")
            extensions.configure<LibraryExtension> {
                compileSdk = 34
                defaultConfig.minSdk = 24
            }
        }
    }
}
```

**2. Version catalogs** для управления зависимостями:

```toml
# gradle/libs.versions.toml
[libraries]
androidx-compose-ui = "androidx.compose.ui:ui"
hilt-android = "com.google.dagger:hilt-android"

# build.gradle.kts
dependencies {
    // ✅ Централизованные версии
    implementation(libs.androidx.compose.ui)
}
```

**3. API vs Implementation**:

```kotlin
dependencies {
    // ✅ implementation - скрывает зависимости
    implementation(project(":core:ui"))

    // ❌ api - экспонирует всем потребителям
    api(project(":core:network"))
}
```

### Когда использовать

**Используйте для:**
- Команды 5+ разработчиков
- 50,000+ строк кода
- Несколько приложений с общим кодом
- Долгие сборки (>5 минут)

**Не нужно для:**
- Маленькие приложения (<10,000 строк)
- Прототипы и MVP
- Единственный разработчик

### Типичные ошибки

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

[[c-modularization|Multi-module architecture]] splits app into independent modules for scalability, faster builds, and parallel development.

### Module Types

**1. app** - Main application module, wires feature modules together
**2. feature** - Isolated features (auth, profile, settings)
**3. core** - Reusable utilities (ui, network, database)
**4. data** - Data layer with [[c-repository-pattern|repository pattern]]

```text
app/
 ├── app/                # Main module
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

**Critical rule**: Feature modules do NOT depend on each other

```kotlin
// ❌ BAD - Feature depends on feature
// :feature:auth -> :feature:profile

// ✅ GOOD - Features depend only on core/data
// :feature:auth -> :core:ui, :data:user
// :feature:profile -> :core:ui, :data:user
```

**Communication via [[c-dependency-inversion|dependency inversion]]**:

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
class AppNavigator : Navigator {
    override fun navigateToProfile(userId: String) {
        // Wires features together
        navController.navigate("profile/$userId")
    }
}
```

### Best Practices

**1. Convention plugins** for standardized [[c-gradle|Gradle]] configuration:

```kotlin
// buildSrc/.../AndroidFeatureConventionPlugin.kt
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            // ✅ Single configuration for all features
            pluginManager.apply("com.android.library")
            extensions.configure<LibraryExtension> {
                compileSdk = 34
                defaultConfig.minSdk = 24
            }
        }
    }
}
```

**2. Version catalogs** for dependency management:

```toml
# gradle/libs.versions.toml
[libraries]
androidx-compose-ui = "androidx.compose.ui:ui"
hilt-android = "com.google.dagger:hilt-android"

# build.gradle.kts
dependencies {
    // ✅ Centralized versions
    implementation(libs.androidx.compose.ui)
}
```

**3. API vs Implementation**:

```kotlin
dependencies {
    // ✅ implementation - hides transitive deps
    implementation(project(":core:ui"))

    // ❌ api - exposes to all consumers
    api(project(":core:network"))
}
```

### When to Use

**Use for:**
- Teams of 5+ developers
- 50,000+ lines of code
- Multiple apps sharing code
- Long builds (>5 minutes)

**Not needed for:**
- Small apps (<10,000 lines)
- Prototypes and MVPs
- Solo developers

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
- [[c-dependency-inversion]] - Dependency inversion principle
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
