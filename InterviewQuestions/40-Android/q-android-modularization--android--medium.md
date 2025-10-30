---
id: 20251012-122767
title: Android Modularization / Модуляризация Android
aliases: ["Android Modularization", "Модуляризация Android"]
topic: android
subtopics: [architecture-modularization, gradle, dependency-management]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, q-android-build-optimization--android--medium, q-gradle-build-system--android--medium]
created: 2025-10-15
updated: 2025-10-29
tags: [android/architecture-modularization, android/gradle, android/dependency-management, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Что такое модуляризация Android-приложений и какие основные преимущества она даёт?

# Question (EN)
> What is Android modularization and what are its main benefits?

## Ответ (RU)

**Модуляризация Android** — это разделение кодовой базы на слабо связанные, самостоятельные модули. Каждый модуль инкапсулирует определённую функциональность и может разрабатываться, тестироваться и поддерживаться независимо.

**Основные типы модулей:**
- **App Module** — точка входа приложения, координирует feature-модули
- **Feature Modules** — изолированные функции (новости, профиль, настройки)
- **Core Modules** — общая логика (data, network, UI)
- **Library Modules** — переиспользуемые компоненты

**Ключевые преимущества:**
- **Масштабируемость** — изменения в одном модуле не затрагивают другие
- **Переиспользование** — модули можно применять в других приложениях
- **Контроль видимости** — внутренняя реализация скрыта через `internal`
- **Параллельная разработка** — команды работают над модулями независимо
- **Быстрая сборка** — Gradle кеширует неизменённые модули
- **Тестируемость** — модули тестируются изолированно

**Пример структуры:**
```text
app/
├── app/                  # Главный модуль
├── feature:news/         # Фича "Новости"
├── feature:profile/      # Фича "Профиль"
├── core:data/           # Слой данных
├── core:network/        # Сетевой слой
└── core:ui/             # UI-компоненты
```

**Управление зависимостями:**
```gradle
// app/build.gradle
dependencies {
    implementation(project(":feature:news"))
    implementation(project(":core:data"))
}

// feature:news/build.gradle
dependencies {
    implementation(project(":core:data"))
    implementation(project(":core:ui"))
    // ✅ Нет прямой зависимости между фичами
}
```

**Контроль видимости:**
```kotlin
// core:data module
internal class DatabaseHelper {
    // ✅ Доступен только внутри модуля
}

class UserRepository {
    // ✅ Публичное API для других модулей
    fun getUser(id: String): User = TODO()
}

// feature:news module
class NewsViewModel {
    private val repo = UserRepository() // ✅ Можно использовать
    // ❌ DatabaseHelper недоступен напрямую
}
```

**Типичные ошибки:**
- **Циклические зависимости** — модули зависят друг от друга
- **Слишком мелкое дробление** — усложняет сборку
- **Монолитные модули** — теряется польза модуляризации

**Best practices:**
- Начинайте с app и core модулей
- Добавляйте feature-модули по мере роста функциональности
- Используйте чёткую иерархию зависимостей
- Применяйте Play Feature Delivery для больших приложений

## Answer (EN)

**Android Modularization** is the practice of organizing a codebase into loosely coupled, self-contained modules. Each module encapsulates specific functionality and can be developed, tested, and maintained independently.

**Main Module Types:**
- **App Module** — application entry point, coordinates feature modules
- **Feature Modules** — isolated features (news, profile, settings)
- **Core Modules** — shared logic (data, network, UI)
- **Library Modules** — reusable components

**Key Benefits:**
- **Scalability** — changes in one module don't affect others
- **Reusability** — modules can be shared across apps
- **Visibility Control** — internal implementation hidden via `internal`
- **Parallel Development** — teams work on modules independently
- **Faster Builds** — Gradle caches unchanged modules
- **Testability** — modules can be tested in isolation

**Example Structure:**
```text
app/
├── app/                  # Main module
├── feature:news/         # News feature
├── feature:profile/      # Profile feature
├── core:data/           # Data layer
├── core:network/        # Network layer
└── core:ui/             # UI components
```

**Dependency Management:**
```gradle
// app/build.gradle
dependencies {
    implementation(project(":feature:news"))
    implementation(project(":core:data"))
}

// feature:news/build.gradle
dependencies {
    implementation(project(":core:data"))
    implementation(project(":core:ui"))
    // ✅ No direct dependency between features
}
```

**Visibility Control:**
```kotlin
// core:data module
internal class DatabaseHelper {
    // ✅ Only accessible within this module
}

class UserRepository {
    // ✅ Public API for other modules
    fun getUser(id: String): User = TODO()
}

// feature:news module
class NewsViewModel {
    private val repo = UserRepository() // ✅ Can use
    // ❌ DatabaseHelper not accessible directly
}
```

**Common Pitfalls:**
- **Circular Dependencies** — modules depend on each other
- **Over-modularization** — too many small modules complicate builds
- **Monolithic Modules** — defeats the purpose of modularization

**Best Practices:**
- Start with app and core modules
- Add feature modules as functionality grows
- Use clear dependency hierarchy
- Apply Play Feature Delivery for large apps

## Follow-ups

- How do you handle shared dependencies between multiple feature modules?
- What strategies prevent circular dependencies in modularized projects?
- When should you use dynamic feature modules vs static modules?
- How does modularization affect build time and app performance?
- How do you enforce module boundaries and prevent unauthorized access between modules?

## References

- [[c-dependency-injection]] — DI patterns in modular apps
- [[c-gradle-build-system]] — Gradle fundamentals
- [[c-clean-architecture]] — Architectural principles
- https://developer.android.com/topic/modularization
- https://developer.android.com/guide/playcore/feature-delivery

## Related Questions

### Prerequisites
- [[q-gradle-build-system--android--medium]] — Build system fundamentals
- [[q-android-app-components--android--easy]] — App components overview

### Related
- [[q-android-architectural-patterns--android--medium]] — Architecture patterns
- [[q-android-build-optimization--android--medium]] — Build optimization techniques

### Advanced
- [[q-android-testing-strategies--android--medium]] — Testing in modular apps
- Dynamic feature delivery implementation
- Convention plugins for module configuration