---
id: 20251017-114546
title: "Multi-module Architecture Best Practices / Лучшие практики мульти-модульной архитектуры"
aliases: []

# Classification
topic: android
subtopics: [architecture-clean, architecture-modularization, gradle]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru, android/architecture, android/multi-module, android/gradle, android/scalability, difficulty/hard]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: [q-android-jetpack-overview--android--easy, q-shared-element-transitions--jetpack-compose--hard, q-how-compose-draws-on-screen--android--hard]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android/architecture-clean, android/architecture-modularization, android/gradle, en, ru, difficulty/hard]
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
 app/                    # Main app module
 feature/
    auth/              # Authentication feature
    profile/           # Profile feature
    settings/          # Settings feature
 core/
    ui/                # Shared UI components
    network/           # Network layer
    database/          # Database layer
 data/
     user/              # User data
     products/          # Products data
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
// - BAD - Feature depends on feature
// :feature:auth -> :feature:profile  // NO!

// - GOOD - Features depend on core/data only
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

```
app/
 app/                    # Основной модуль приложения
 feature/
    auth/              # Модуль аутентификации
    profile/           # Модуль профиля
    settings/          # Модуль настроек
 core/
    ui/                # Общие UI компоненты
    network/           # Сетевой слой
    database/          # Слой базы данных
 data/
     user/              # Данные пользователя
     products/          # Данные продуктов
```

### Структура модуля

```kotlin
// feature/auth/build.gradle.kts
plugins {
    id("com.android.library")
    id("kotlin-android")
}

dependencies {
    // Core модули
    implementation(project(":core:ui"))
    implementation(project(":core:network"))

    // Data модули
    implementation(project(":data:user"))

    // Внешние зависимости
    implementation(libs.androidx.compose)
    implementation(libs.hilt)
}
```

### Правила зависимостей

**1. Feature модули НЕ должны зависеть друг от друга**

```kotlin
// ❌ ПЛОХО - Feature зависит от feature
// :feature:auth -> :feature:profile  // НЕТ!

// ✅ ХОРОШО - Features зависят только от core/data
// :feature:auth -> :core:ui
// :feature:auth -> :data:user
// :feature:profile -> :core:ui
// :feature:profile -> :data:user
```

**2. Используйте инверсию зависимостей для коммуникации между features**

```kotlin
// core/navigation
interface Navigator {
    fun navigateToProfile(userId: String)
}

// feature/auth - использует интерфейс
class LoginViewModel(private val navigator: Navigator) {
    fun onLoginSuccess(userId: String) {
        navigator.navigateToProfile(userId)
    }
}

// app модуль - реализует интерфейс
class AppNavigator(private val navController: NavController) : Navigator {
    override fun navigateToProfile(userId: String) {
        navController.navigate("profile/$userId")
    }
}
```

### Преимущества

**1. Быстрее сборка** - Только измененные модули пересобираются
**2. Лучшая инкапсуляция** - Четкие границы между модулями
**3. Параллельная разработка** - Команды работают независимо
**4. Переиспользование кода** - Модули можно использовать в разных приложениях
**5. Dynamic delivery** - Функции по требованию

### Лучшие практики

**1. Convention plugins для общей конфигурации:**

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
    id("android.feature")  // Применяет всю общую конфигурацию
}
```

**2. Version catalog для зависимостей:**

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

**3. Чёткие границы модулей:**

Каждый модуль должен иметь четкую ответственность:
- Feature модули: Специфичная функциональность
- Core модули: Переиспользуемые утилиты
- Data модули: Работа с данными

**4. Минимизация зависимостей:**

```kotlin
// ✅ ХОРОШО - Минимальные зависимости
// :feature:auth -> :core:ui, :data:user

// ❌ ПЛОХО - Слишком много зависимостей
// :feature:auth -> :core:ui, :core:network, :core:database, :data:user, :data:products
```

**5. API vs Implementation:**

```kotlin
// Используйте implementation для скрытия транзитивных зависимостей
dependencies {
    implementation(project(":core:ui"))  // ✅ Скрыто
    api(project(":core:network"))        // ❌ Экспонировано всем потребителям
}
```

### Когда использовать мульти-модульную архитектуру

**Используйте когда:**
- Большая команда разработчиков
- 50,000+ строк кода
- Несколько приложений, использующих общий код
- Необходимы быстрые сборки
- Dynamic feature delivery

**Не обязательно для:**
- Маленькие приложения (<10,000 строк)
- Единственный разработчик
- Прототипы

### Граф зависимостей

```
        app
         |
    +---------+---------+
    |         |         |
feature:   feature:   feature:
  auth     profile   settings
    |         |         |
    +----+----+----+----+
         |         |
      core:ui  core:network
         |
      data:user
```

**Правила:**
- Зависимости только вниз (нет циклов)
- Feature модули не зависят друг от друга
- Core модули переиспользуемые
- Data модули изолированные

### Типичные ошибки

**1. Циклические зависимости**
```kotlin
// ❌ ПЛОХО
// :feature:auth -> :core:ui -> :feature:auth  // Цикл!
```

**2. Слишком много мелких модулей**
```kotlin
// ❌ ПЛОХО - Слишком детализировано
:feature:auth:login
:feature:auth:register
:feature:auth:password-reset
:feature:auth:verification

// ✅ ХОРОШО - Один модуль для всей feature
:feature:auth
```

**3. Неправильная гранулярность**
```kotlin
// ❌ ПЛОХО - Слишком крупные модули
:feature:everything  // Весь функционал в одном модуле

// ✅ ХОРОШО - Логическое разделение
:feature:auth
:feature:profile
:feature:settings
```

### Миграция на мульти-модульную архитектуру

**Шаги:**

1. **Начните с core модулей**
   - Выделите общие утилиты в :core:utils
   - Выделите UI компоненты в :core:ui

2. **Создайте data модули**
   - Изолируйте доступ к данным
   - Используйте repository pattern

3. **Разделите features**
   - Начните с самых независимых features
   - Постепенно мигрируйте остальные

4. **Настройте convention plugins**
   - Стандартизируйте конфигурацию
   - Уменьшите дублирование

**Краткое содержание**: Мульти-модуль: разделить app на feature/core/data модули. Преимущества: быстрее сборки, лучшая инкапсуляция, параллельная разработка. Правила: features не зависят от features, использовать инверсию зависимостей для коммуникации. Лучшие практики: convention plugins, version catalogs, четкие границы модулей. Когда использовать: большие команды, 50k+ строк кода, несколько приложений.

---

## References
- [Guide to Android app modularization](https://developer.android.com/topic/modularization)

## Related Questions

### Related (Hard)
- [[q-design-uber-app--android--hard]] - Location
- [[q-design-whatsapp-app--android--hard]] - Messaging
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-modularization-patterns--android--hard]] - Architecture

### Prerequisites (Easier)
- [[q-build-optimization-gradle--android--medium]] - Gradle
- [[q-usecase-pattern-android--android--medium]] - Architecture
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Gradle
