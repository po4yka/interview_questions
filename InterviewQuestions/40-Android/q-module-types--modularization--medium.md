---
id: android-mod-001
title: "Module Types in Android / Типы модулей в Android"
aliases: ["Module Types", "Android Module Types", "Типы модулей Android"]
topic: android
subtopics: [modularization, architecture, gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-api-vs-implementation--modularization--medium, q-module-dependency-graph--modularization--hard]
created: 2026-01-23
updated: 2026-01-23
sources: []
tags: [android/modularization, android/architecture, android/gradle, difficulty/medium, module-types]

---
# Вопрос (RU)

> Какие типы модулей существуют в Android-проектах? Объясните назначение app, library, feature и core модулей.

# Question (EN)

> What types of modules exist in Android projects? Explain the purpose of app, library, feature, and core modules.

---

## Ответ (RU)

**Модуляризация** разделяет Android-приложение на независимые модули с четкими границами и ответственностями. Каждый тип модуля имеет определенную роль в архитектуре.

### Типы Модулей

#### 1. App Module (`:app`)

**Назначение**: Точка входа приложения. Собирает все feature-модули и конфигурирует DI-граф.

```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
}

dependencies {
    // Собирает все feature-модули
    implementation(project(":feature:home"))
    implementation(project(":feature:profile"))
    implementation(project(":feature:settings"))

    // Core-модули для DI
    implementation(project(":core:di"))
}
```

**Содержит**:
- `Application` класс
- `MainActivity` (single-activity архитектура)
- Конфигурация навигации верхнего уровня
- Hilt/Dagger modules для сборки графа

#### 2. Feature Modules (`:feature:*`)

**Назначение**: Инкапсулируют бизнес-функциональность. Один feature = один экран или группа связанных экранов.

```kotlin
// feature/profile/build.gradle.kts
plugins {
    id("com.android.library")
}

dependencies {
    // Только core-модули, НЕ другие features
    implementation(project(":core:ui"))
    implementation(project(":core:domain"))
    implementation(project(":core:data"))

    // НЕ делайте так - создает связность между features
    // implementation(project(":feature:settings")) // BAD
}
```

**Структура feature-модуля**:
```
feature/profile/
  src/main/kotlin/
    di/           # ProfileModule.kt
    ui/           # ProfileScreen.kt, ProfileViewModel.kt
    navigation/   # ProfileNavigation.kt
```

#### 3. Core Modules (`:core:*`)

**Назначение**: Переиспользуемая инфраструктура без бизнес-логики. Доступны всем feature-модулям.

| Core Module | Содержимое |
|-------------|------------|
| `:core:ui` | Тема, общие компоненты, Modifier extensions |
| `:core:domain` | Use cases, доменные модели, интерфейсы репозиториев |
| `:core:data` | Реализации репозиториев, data sources |
| `:core:network` | Retrofit/Ktor setup, API клиенты |
| `:core:database` | Room database, DAOs, entities |
| `:core:common` | Утилиты, extensions, константы |
| `:core:testing` | Test utilities, fakes, test fixtures |

```kotlin
// core/domain/build.gradle.kts
plugins {
    id("org.jetbrains.kotlin.jvm") // Чистый Kotlin, без Android
}

// core/ui/build.gradle.kts
plugins {
    id("com.android.library")
}

dependencies {
    implementation(project(":core:designsystem"))
}
```

#### 4. Library Modules

**Назначение**: Независимые библиотеки, которые можно публиковать отдельно.

```kotlin
// lib/analytics/build.gradle.kts
plugins {
    id("com.android.library")
    id("maven-publish") // Для публикации
}
```

### Граф Зависимостей

```
              +-------+
              |  app  |
              +---+---+
                  |
    +-------------+-------------+
    |             |             |
+---v---+    +----v----+   +----v----+
|feature|    |feature  |   |feature  |
| home  |    | profile |   |settings |
+---+---+    +----+----+   +----+----+
    |             |             |
    +-------------+-------------+
                  |
         +--------+--------+
         |        |        |
     +---v--+ +---v---+ +--v---+
     |core  | |core   | |core  |
     | ui   | |domain | |data  |
     +------+ +---+---+ +--+---+
                  |        |
              +---v--------v---+
              |   core:common  |
              +----------------+
```

### Правила Модуляризации

| Правило | Описание |
|---------|----------|
| Feature не зависит от feature | Связь через navigation API или app-модуль |
| Core не зависит от feature | Core-модули - фундамент |
| Data зависит от domain | Инверсия зависимостей |
| App собирает все | Единственный модуль, знающий о всех features |

### Пример Реальной Структуры

```
my-app/
  app/
  feature/
    home/
    profile/
    settings/
    onboarding/
  core/
    ui/
    domain/
    data/
    network/
    database/
    common/
    testing/
  lib/
    analytics/
    logging/
```

---

## Answer (EN)

**Modularization** splits an Android application into independent modules with clear boundaries and responsibilities. Each module type has a specific role in the architecture.

### Module Types

#### 1. App Module (`:app`)

**Purpose**: Application entry point. Assembles all feature modules and configures the DI graph.

```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
}

dependencies {
    // Assembles all feature modules
    implementation(project(":feature:home"))
    implementation(project(":feature:profile"))
    implementation(project(":feature:settings"))

    // Core modules for DI
    implementation(project(":core:di"))
}
```

**Contains**:
- `Application` class
- `MainActivity` (single-activity architecture)
- Top-level navigation configuration
- Hilt/Dagger modules for graph assembly

#### 2. Feature Modules (`:feature:*`)

**Purpose**: Encapsulate business functionality. One feature = one screen or a group of related screens.

```kotlin
// feature/profile/build.gradle.kts
plugins {
    id("com.android.library")
}

dependencies {
    // Only core modules, NOT other features
    implementation(project(":core:ui"))
    implementation(project(":core:domain"))
    implementation(project(":core:data"))

    // DON'T do this - creates coupling between features
    // implementation(project(":feature:settings")) // BAD
}
```

**Feature module structure**:
```
feature/profile/
  src/main/kotlin/
    di/           # ProfileModule.kt
    ui/           # ProfileScreen.kt, ProfileViewModel.kt
    navigation/   # ProfileNavigation.kt
```

#### 3. Core Modules (`:core:*`)

**Purpose**: Reusable infrastructure without business logic. Available to all feature modules.

| Core Module | Contents |
|-------------|----------|
| `:core:ui` | Theme, shared components, Modifier extensions |
| `:core:domain` | Use cases, domain models, repository interfaces |
| `:core:data` | Repository implementations, data sources |
| `:core:network` | Retrofit/Ktor setup, API clients |
| `:core:database` | Room database, DAOs, entities |
| `:core:common` | Utilities, extensions, constants |
| `:core:testing` | Test utilities, fakes, test fixtures |

```kotlin
// core/domain/build.gradle.kts
plugins {
    id("org.jetbrains.kotlin.jvm") // Pure Kotlin, no Android
}

// core/ui/build.gradle.kts
plugins {
    id("com.android.library")
}

dependencies {
    implementation(project(":core:designsystem"))
}
```

#### 4. Library Modules

**Purpose**: Independent libraries that can be published separately.

```kotlin
// lib/analytics/build.gradle.kts
plugins {
    id("com.android.library")
    id("maven-publish") // For publishing
}
```

### Dependency Graph

```
              +-------+
              |  app  |
              +---+---+
                  |
    +-------------+-------------+
    |             |             |
+---v---+    +----v----+   +----v----+
|feature|    |feature  |   |feature  |
| home  |    | profile |   |settings |
+---+---+    +----+----+   +----+----+
    |             |             |
    +-------------+-------------+
                  |
         +--------+--------+
         |        |        |
     +---v--+ +---v---+ +--v---+
     |core  | |core   | |core  |
     | ui   | |domain | |data  |
     +------+ +---+---+ +--+---+
                  |        |
              +---v--------v---+
              |   core:common  |
              +----------------+
```

### Modularization Rules

| Rule | Description |
|------|-------------|
| Feature does not depend on feature | Communication via navigation API or app module |
| Core does not depend on feature | Core modules are the foundation |
| Data depends on domain | Dependency inversion |
| App assembles everything | The only module aware of all features |

### Real-World Structure Example

```
my-app/
  app/
  feature/
    home/
    profile/
    settings/
    onboarding/
  core/
    ui/
    domain/
    data/
    network/
    database/
    common/
    testing/
  lib/
    analytics/
    logging/
```

---

## Follow-ups

- How do you handle shared resources (strings, drawables) across feature modules?
- What criteria do you use to decide when to create a new module?
- How do you manage version catalogs across multiple modules?

## References

- https://developer.android.com/topic/modularization
- https://github.com/android/nowinandroid - Official modularization example
- https://developer.android.com/topic/modularization/patterns

## Related Questions

### Prerequisites

- [[q-gradle-basics--android--easy]] - Gradle build system fundamentals
- [[q-dependency-injection--android--medium]] - DI in Android

### Related

- [[q-api-vs-implementation--modularization--medium]] - API vs implementation dependencies
- [[q-build-time-optimization--modularization--medium]] - Build time benefits

### Advanced

- [[q-module-dependency-graph--modularization--hard]] - Designing module graphs
- [[q-convention-plugins--modularization--hard]] - Gradle convention plugins
