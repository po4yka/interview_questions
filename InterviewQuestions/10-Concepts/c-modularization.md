---
id: ivc-20251030-120000
title: Modularization / Модуляризация
aliases: [Modularization, Multi-Module, Модульность, Модуляризация]
kind: concept
summary: Splitting Android app into independent, reusable Gradle modules
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, architecture, concept, gradle, modularization]
date created: Thursday, October 30th 2025, 12:30:11 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

**Modularization** is the practice of dividing an Android application into multiple independent Gradle modules, each with clear responsibilities and dependencies. This architectural approach improves build performance through parallel compilation and incremental builds, enables code reusability across projects, and supports team scalability by allowing parallel development on isolated modules.

## Core Concept

**Module Types**:
- **App module** (`com.android.application`): Entry point, depends on feature modules
- **Library modules** (`com.android.library`): Reusable Android components
- **Feature modules**: Self-contained user-facing features (e.g., `:feature:login`, `:feature:profile`)
- **Core/Common modules**: Shared utilities, domain models, base classes (e.g., `:core:ui`, `:core:data`)
- **Data modules**: Repository implementations, API clients (e.g., `:data:auth`, `:data:user`)

**Module Structure Example**:
```
:app
:feature:home
:feature:profile
:core:ui           // Shared UI components
:core:domain       // Business logic, use cases
:core:data         // Repository interfaces
:data:network      // API implementation
:data:database     // Room database
```

## Benefits

1. **Build Performance**:
   - Parallel module compilation reduces build time
   - Incremental builds only recompile changed modules
   - Smaller modules compile faster than monolithic codebase

2. **Code Reusability**:
   - Core modules shared across features
   - Library modules reusable in multiple apps
   - Clear API boundaries via public interfaces

3. **Team Scalability**:
   - Teams own specific modules
   - Reduced merge conflicts
   - Independent feature development and testing

4. **Encapsulation**:
   - Internal implementation details hidden
   - Enforced dependency rules prevent circular dependencies
   - Clear separation of concerns

## Dependency Rules

**Acyclic Dependency Graph**:
- Feature modules depend on core modules (`:feature:home` → `:core:ui`)
- Feature modules NEVER depend on other feature modules
- Core modules can depend on other core modules (`:core:data` → `:core:domain`)
- Data modules depend on core modules (`:data:network` → `:core:domain`)

**Layered Architecture**:
```
        :app
          ↓
    Feature Layer (:feature:*)
          ↓
     Core Layer (:core:*)
          ↓
     Data Layer (:data:*)
```

## Best Practices

**Public API Surface**:
- Minimize exposed classes (use `internal` visibility)
- Define clear module contracts via interfaces
- Use Kotlin's visibility modifiers effectively

**Module Boundaries**:
- Keep modules focused (Single Responsibility Principle)
- Avoid tight coupling between modules
- Use dependency inversion (depend on abstractions, not implementations)

**Dependency Injection**:
- Use Hilt/Dagger for cross-module dependencies
- Define component interfaces in core modules
- Implement in data/feature modules

**Gradle Configuration**:
```kotlin
// Convention plugins for shared configuration
plugins {
    id("android.library.conventions")
}

dependencies {
    api(project(":core:domain"))        // Expose to consumers
    implementation(project(":core:ui"))  // Hide from consumers
}
```

**Testing**:
- Test modules in isolation
- Mock dependencies from other modules
- Faster test execution on smaller modules

## Use Cases / Trade-offs

**When to Modularize**:
- Large codebases (50k+ lines)
- Multiple teams working on same app
- Slow build times (5+ minutes)
- Need to share code across apps

**Trade-offs**:
- BENEFIT: Faster incremental builds, parallel development
- COST: Initial setup complexity, Gradle configuration overhead
- BENEFIT: Enforced boundaries, better architecture
- COST: Boilerplate (dependency injection setup)
- BENEFIT: Testability, isolation
- COST: Navigation between modules requires abstraction

**Anti-patterns to Avoid**:
- Too many small modules (excessive fragmentation)
- Circular dependencies between modules
- Feature modules depending on each other
- Leaking internal implementation details

## References

- [Android Modularization Guide](https://developer.android.com/topic/modularization)
- [Now in Android (Sample App)](https://github.com/android/nowinandroid)
- [Guide to Android app modularization (Google I/O)](https://www.youtube.com/watch?v=PZBg5DIzNww)

---

# Сводка (RU)

**Модуляризация** — это практика разделения Android-приложения на несколько независимых Gradle-модулей, каждый из которых имеет четкие обязанности и зависимости. Этот архитектурный подход улучшает производительность сборки за счет параллельной компиляции и инкрементальных сборок, обеспечивает переиспользование кода между проектами и поддерживает масштабируемость команды, позволяя параллельную разработку изолированных модулей.

## Основная Концепция

**Типы модулей**:
- **App-модуль** (`com.android.application`): Точка входа, зависит от feature-модулей
- **Library-модули** (`com.android.library`): Переиспользуемые Android-компоненты
- **Feature-модули**: Самодостаточные пользовательские функции (например, `:feature:login`, `:feature:profile`)
- **Core/Common-модули**: Общие утилиты, доменные модели, базовые классы (например, `:core:ui`, `:core:data`)
- **Data-модули**: Реализации репозиториев, API-клиенты (например, `:data:auth`, `:data:user`)

## Преимущества

1. **Производительность сборки**: параллельная компиляция модулей, инкрементальные сборки
2. **Переиспользование кода**: общие core-модули, четкие API-границы
3. **Масштабируемость команды**: команды владеют модулями, меньше конфликтов при слиянии
4. **Инкапсуляция**: скрытые детали реализации, принудительные правила зависимостей

## Правила Зависимостей

**Ациклический граф зависимостей**:
- Feature-модули зависят от core-модулей
- Feature-модули НИКОГДА не зависят друг от друга
- Core-модули могут зависеть от других core-модулей
- Data-модули зависят от core-модулей

## Лучшие Практики

- **Минимизировать публичный API** (использовать `internal`)
- **Четкие границы модулей** (Single Responsibility)
- **Dependency Injection** (Hilt/Dagger для кроссмодульных зависимостей)
- **Convention plugins** для общей конфигурации Gradle
- **Изолированное тестирование** модулей

## Когда Использовать

- Большие кодовые базы (50k+ строк)
- Множество команд работают над одним приложением
- Медленные сборки (5+ минут)
- Необходимость переиспользования кода между приложениями

**Компромиссы**:
- ПЛЮС: Быстрые инкрементальные сборки, параллельная разработка
- МИНУС: Сложность начальной настройки, overhead конфигурации Gradle
- ПЛЮС: Принудительные границы, лучшая архитектура
- МИНУС: Boilerplate (настройка dependency injection)
