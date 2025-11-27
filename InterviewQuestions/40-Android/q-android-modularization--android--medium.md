---
id: android-269
title: Android Modularization / Модуляризация Android
aliases: [Android Modularization, Модуляризация Android]
topic: android
subtopics:
  - architecture-modularization
  - dependency-management
  - gradle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-clean-architecture
  - c-dependency-injection
  - c-gradle
  - q-android-build-optimization--android--medium
  - q-annotation-processing-android--android--medium
  - q-gradle-build-system--android--medium
  - q-module-types-android--android--medium
created: 2025-10-15
updated: 2025-10-30
tags: [android/architecture-modularization, android/dependency-management, android/gradle, difficulty/medium]
sources: []
date created: Saturday, November 1st 2025, 12:46:42 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> Что такое модуляризация Android-приложений и какие основные преимущества она даёт?

# Question (EN)
> What is Android modularization and what are its main benefits?

## Ответ (RU)

**Модуляризация Android** — разделение кодовой базы на слабо связанные, независимо разрабатываемые модули Gradle. Каждый модуль инкапсулирует определённую функциональность и может собираться независимо от других.

**Типы модулей:**
- **App Module** — точка входа, координирует feature-модули
- **Feature Modules** — изолированные фичи (news, profile, settings)
- **Core Modules** — переиспользуемая логика (data, network, ui)
- **Library Modules** — общие компоненты без Android-зависимостей

**Преимущества:**

**1. Масштабируемость и изоляция**
- Изменения в модуле минимально влияют на другие части
- Контроль видимости через `internal` скрывает детали реализации
- Чёткие границы между слоями

**2. Производительность сборки**
- Gradle кеширует неизменённые модули
- Параллельная компиляция
- Инкрементальная сборка затрагивает в основном изменённый модуль

**3. Переиспользование и тестирование**
- Модули можно применять в других проектах
- Изолированное unit-тестирование
- Чёткие зависимости упрощают моки

**Структура проекта:**
```text
app/
├── app/                     # Основной application-модуль
├── feature-news/            # News feature (модуль ":feature:news")
├── feature-profile/         # Profile feature (модуль ":feature:profile")
├── core-data/               # Data layer (модуль ":core:data")
├── core-network/            # Networking (модуль ":core:network")
└── core-ui/                 # Shared UI components (модуль ":core:ui")
```

**Управление зависимостями:**
```gradle
// app/build.gradle
dependencies {
    implementation(project(":feature:news"))
    implementation(project(":core:data"))
}

// feature-news/build.gradle
dependencies {
    implementation(project(":core:data"))
    implementation(project(":core:ui"))
    // ✅ Нет прямой зависимости между feature-модулями
}
```

**Контроль видимости:**
```kotlin
// core:data module
internal class DatabaseHelper {
    // ✅ Доступен только внутри этого модуля
}

class UserRepository {
    // ✅ Публичный API для других модулей
    fun getUser(id: String): User {
        // implementation
    }
}

// feature:news module
class NewsViewModel {
    private val repo = UserRepository() // ✅ Можно использовать публичный API
    // ❌ DatabaseHelper недоступен
}
```

**Типичные ошибки:**
- **Циклические зависимости** — feature A → feature B → feature A
- **Over-modularization** — слишком мелкие модули усложняют навигацию и сборку
- **Неправильная иерархия** — feature-модули напрямую зависят друг от друга вместо зависимостей через core-модули

**Best practices:**
- Начинайте с app + core:data + core:ui
- Один модуль = одна фича или слой архитектуры
- Feature-модули общаются через core:data / core:ui / общие интерфейсы, а не напрямую
- Используйте convention plugins для единообразия конфигурации
- Рассматривайте Play Feature Delivery и dynamic feature modules для крупных приложений с on-demand функциональностью

## Answer (EN)

**Android Modularization** is organizing a codebase into loosely coupled, independently developable Gradle modules. Each module encapsulates specific functionality and can be built independently from others.

**Module Types:**
- **App Module** — entry point, coordinates feature modules
- **Feature Modules** — isolated features (news, profile, settings)
- **Core Modules** — reusable logic (data, network, ui)
- **Library Modules** — shared components without Android dependencies

**Benefits:**

**1. Scalability and Isolation**
- Changes in one module minimally affect others
- Visibility control via `internal` hides implementation details
- Clear boundaries between layers

**2. Build Performance**
- Gradle caches unchanged modules
- Parallel compilation
- Incremental builds mostly affect the changed module

**3. Reusability and Testing**
- Modules can be shared across projects
- Isolated unit testing
- Clear dependencies simplify mocking

**Project Structure:**
```text
app/
├── app/                     # Main application module
├── feature-news/            # News feature (module ":feature:news")
├── feature-profile/         # Profile feature (module ":feature:profile")
├── core-data/               # Data layer (module ":core:data")
├── core-network/            # Networking (module ":core:network")
└── core-ui/                 # Shared UI components (module ":core:ui")
```

**Dependency Management:**
```gradle
// app/build.gradle
dependencies {
    implementation(project(":feature:news"))
    implementation(project(":core:data"))
}

// feature-news/build.gradle
dependencies {
    implementation(project(":core:data"))
    implementation(project(":core:ui"))
    // ✅ No direct dependency between feature modules
}
```

**Visibility Control:**
```kotlin
// core:data module
internal class DatabaseHelper {
    // ✅ Accessible only within this module
}

class UserRepository {
    // ✅ Public API for other modules
    fun getUser(id: String): User {
        // implementation
    }
}

// feature:news module
class NewsViewModel {
    private val repo = UserRepository() // ✅ Can use public API
    // ❌ DatabaseHelper not accessible
}
```

**Common Pitfalls:**
- **Circular Dependencies** — feature A → feature B → feature A
- **Over-modularization** — too many small modules complicate navigation and build
- **Wrong Hierarchy** — feature modules depend directly on each other instead of through core modules

**Best Practices:**
- Start with app + core:data + core:ui
- One module = one feature or architecture layer
- Feature modules communicate via core:data / core:ui / shared interfaces, not directly
- Use convention plugins for consistent configuration
- Consider Play Feature Delivery and dynamic feature modules for large apps with on-demand functionality

## Follow-ups

- How do you prevent circular dependencies in a modularized project?
- What strategies help decide when to create a new module vs adding to existing one?
- How does modularization affect dependency injection setup (Hilt/Koin)?
- When should you use dynamic feature modules vs static modules?
- How do you enforce module boundaries at compile time using Gradle configurations?

## References

- [[c-gradle]] — Gradle build system fundamentals
- [[c-dependency-injection]] — DI patterns in modular apps
- [[c-clean-architecture]] — Architectural layer separation
- https://developer.android.com/topic/modularization — Official modularization guide
- https://developer.android.com/guide/playcore/feature-delivery — Dynamic feature delivery

## Related Questions

### Prerequisites
- [[q-gradle-basics--android--easy]] — Gradle fundamentals
- [[q-architecture-components-libraries--android--easy]] — Architecture components overview

### Related
- [[q-gradle-build-system--android--medium]] — Build system details
- [[q-android-build-optimization--android--medium]] — Build performance optimization
- [[q-gradle-version-catalog--android--medium]] — Centralized dependency management

### Advanced
- [[q-clean-architecture-android--android--hard]] — Clean architecture implementation
- [[q-offline-first-architecture--android--hard]] — Offline-first with modularization
- Dynamic feature delivery and on-demand module loading
