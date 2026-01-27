---
id: android-mod-002
title: API vs Implementation Dependency / API vs Implementation зависимость
aliases:
- API vs Implementation
- Gradle Dependencies
- API vs Implementation в Gradle
topic: android
subtopics:
- modularization
- gradle
- dependencies
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android
- q-module-types--modularization--medium
- q-build-time-optimization--modularization--medium
created: 2026-01-23
updated: 2026-01-23
sources: []
tags:
- android/modularization
- android/gradle
- android/dependencies
- difficulty/medium
- api-implementation
anki_cards:
- slug: android-mod-002-0-en
  language: en
- slug: android-mod-002-0-ru
  language: ru
---
# Вопрос (RU)

> В чем разница между `api` и `implementation` зависимостями в Gradle? Когда использовать каждую из них?

# Question (EN)

> What is the difference between `api` and `implementation` dependencies in Gradle? When should you use each?

---

## Ответ (RU)

**`api`** и **`implementation`** определяют видимость транзитивных зависимостей в Gradle. Правильный выбор влияет на время сборки и инкапсуляцию модулей.

### Ключевое Различие

| Аспект | `implementation` | `api` |
|--------|------------------|-------|
| Видимость | Скрыта от потребителей модуля | Видна потребителям модуля |
| Перекомпиляция | Только текущий модуль | Текущий + все зависимые модули |
| Время сборки | Быстрее | Медленнее |
| Инкапсуляция | Лучше | Хуже |

### Визуальное Объяснение

```
Module A (app)
    |
    | implementation(B)
    v
Module B (feature)
    |
    | api(C)           <- C видна для A
    | implementation(D) <- D НЕ видна для A
    v
Module C (core:domain)
Module D (internal-utils)
```

**Результат**: Модуль A может использовать классы из C, но НЕ из D.

### Примеры Использования

#### Когда использовать `implementation` (по умолчанию)

```kotlin
// feature/profile/build.gradle.kts
dependencies {
    // Внутренние зависимости - скрыты от потребителей
    implementation(project(":core:network"))
    implementation(libs.retrofit)
    implementation(libs.okhttp)
    implementation(libs.moshi)
}
```

**Используйте `implementation` когда**:
- Зависимость - деталь реализации
- Типы зависимости не появляются в public API модуля
- Хотите изолировать изменения (локальная перекомпиляция)

#### Когда использовать `api`

```kotlin
// core/domain/build.gradle.kts
dependencies {
    // Public API - типы видны потребителям
    api(project(":core:model"))  // User, Product - используются везде
    api(libs.kotlinx.coroutines) // Flow, suspend - в публичных сигнатурах

    // Внутренняя реализация
    implementation(libs.kotlinx.datetime)
}
```

**Используйте `api` когда**:
- Типы зависимости появляются в public API (возвращаемые типы, параметры)
- Зависимость - часть контракта модуля
- Потребители модуля должны напрямую использовать типы зависимости

### Практический Пример

```kotlin
// core/domain/src/.../UserRepository.kt
interface UserRepository {
    // Flow из kotlinx.coroutines - должна быть api зависимостью
    fun getUsers(): Flow<List<User>>

    // User из core:model - должна быть api зависимостью
    suspend fun getUser(id: String): User
}

// core/domain/build.gradle.kts
dependencies {
    api(project(":core:model"))        // User виден потребителям
    api(libs.kotlinx.coroutines.core)  // Flow виден потребителям
}
```

```kotlin
// core/data/src/.../UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val api: UserApi,      // Retrofit interface - implementation
    private val mapper: UserMapper // Internal - implementation
) : UserRepository {
    override fun getUsers() = api.getUsers().map { mapper.toDomain(it) }
}

// core/data/build.gradle.kts
dependencies {
    api(project(":core:domain"))       // Контракт доступен потребителям
    implementation(project(":core:network")) // Детали скрыты
    implementation(libs.retrofit)
}
```

### Влияние на Время Сборки

```
Изменение в модуле D:

С implementation:
  D перекомпилируется -> Готово

С api:
  D перекомпилируется -> C перекомпилируется -> B перекомпилируется -> A перекомпилируется
```

**Правило**: Максимизируйте `implementation`, минимизируйте `api` для быстрых инкрементальных сборок.

### Распространенные Ошибки

```kotlin
// BAD: Все зависимости как api
dependencies {
    api(libs.retrofit)        // Зачем? Retrofit не в public API
    api(libs.gson)            // Зачем? Детали сериализации
    api(project(":internal")) // Зачем? Утечка внутренних деталей
}

// GOOD: Явное разделение
dependencies {
    // Public contract
    api(project(":core:model"))
    api(libs.kotlinx.coroutines.core)

    // Implementation details
    implementation(libs.retrofit)
    implementation(libs.gson)
    implementation(project(":internal"))
}
```

### Проверка Транзитивных Зависимостей

```bash
# Показать все зависимости модуля
./gradlew :feature:profile:dependencies --configuration implementation

# Показать, почему зависимость включена
./gradlew :app:dependencyInsight --dependency kotlinx-coroutines-core
```

### Таблица Решений

| Вопрос | Если "Да" | Если "Нет" |
|--------|-----------|------------|
| Тип в public API? | `api` | `implementation` |
| Потребители используют напрямую? | `api` | `implementation` |
| Внутренняя утилита? | `implementation` | - |
| Сомневаетесь? | `implementation` | - |

---

## Answer (EN)

**`api`** and **`implementation`** define the visibility of transitive dependencies in Gradle. The correct choice affects build time and module encapsulation.

### Key Difference

| Aspect | `implementation` | `api` |
|--------|------------------|-------|
| Visibility | Hidden from module consumers | Visible to module consumers |
| Recompilation | Only current module | Current + all dependent modules |
| Build time | Faster | Slower |
| Encapsulation | Better | Worse |

### Visual Explanation

```
Module A (app)
    |
    | implementation(B)
    v
Module B (feature)
    |
    | api(C)           <- C is visible to A
    | implementation(D) <- D is NOT visible to A
    v
Module C (core:domain)
Module D (internal-utils)
```

**Result**: Module A can use classes from C, but NOT from D.

### Usage Examples

#### When to use `implementation` (default choice)

```kotlin
// feature/profile/build.gradle.kts
dependencies {
    // Internal dependencies - hidden from consumers
    implementation(project(":core:network"))
    implementation(libs.retrofit)
    implementation(libs.okhttp)
    implementation(libs.moshi)
}
```

**Use `implementation` when**:
- Dependency is an implementation detail
- Dependency types don't appear in module's public API
- You want to isolate changes (local recompilation only)

#### When to use `api`

```kotlin
// core/domain/build.gradle.kts
dependencies {
    // Public API - types visible to consumers
    api(project(":core:model"))  // User, Product - used everywhere
    api(libs.kotlinx.coroutines) // Flow, suspend - in public signatures

    // Internal implementation
    implementation(libs.kotlinx.datetime)
}
```

**Use `api` when**:
- Dependency types appear in public API (return types, parameters)
- Dependency is part of module's contract
- Consumers need to directly use dependency's types

### Practical Example

```kotlin
// core/domain/src/.../UserRepository.kt
interface UserRepository {
    // Flow from kotlinx.coroutines - must be api dependency
    fun getUsers(): Flow<List<User>>

    // User from core:model - must be api dependency
    suspend fun getUser(id: String): User
}

// core/domain/build.gradle.kts
dependencies {
    api(project(":core:model"))        // User visible to consumers
    api(libs.kotlinx.coroutines.core)  // Flow visible to consumers
}
```

```kotlin
// core/data/src/.../UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val api: UserApi,      // Retrofit interface - implementation
    private val mapper: UserMapper // Internal - implementation
) : UserRepository {
    override fun getUsers() = api.getUsers().map { mapper.toDomain(it) }
}

// core/data/build.gradle.kts
dependencies {
    api(project(":core:domain"))       // Contract available to consumers
    implementation(project(":core:network")) // Details hidden
    implementation(libs.retrofit)
}
```

### Build Time Impact

```
Change in module D:

With implementation:
  D recompiles -> Done

With api:
  D recompiles -> C recompiles -> B recompiles -> A recompiles
```

**Rule**: Maximize `implementation`, minimize `api` for fast incremental builds.

### Common Mistakes

```kotlin
// BAD: All dependencies as api
dependencies {
    api(libs.retrofit)        // Why? Retrofit not in public API
    api(libs.gson)            // Why? Serialization details
    api(project(":internal")) // Why? Leaking internal details
}

// GOOD: Explicit separation
dependencies {
    // Public contract
    api(project(":core:model"))
    api(libs.kotlinx.coroutines.core)

    // Implementation details
    implementation(libs.retrofit)
    implementation(libs.gson)
    implementation(project(":internal"))
}
```

### Checking Transitive Dependencies

```bash
# Show all dependencies of a module
./gradlew :feature:profile:dependencies --configuration implementation

# Show why a dependency is included
./gradlew :app:dependencyInsight --dependency kotlinx-coroutines-core
```

### Decision Table

| Question | If "Yes" | If "No" |
|----------|----------|---------|
| Type in public API? | `api` | `implementation` |
| Consumers use directly? | `api` | `implementation` |
| Internal utility? | `implementation` | - |
| Not sure? | `implementation` | - |

---

## Follow-ups

- How does `compileOnly` differ from `implementation`?
- What is `runtimeOnly` used for?
- How do you handle version conflicts between `api` dependencies?

## References

- https://docs.gradle.org/current/userguide/java_library_plugin.html
- https://developer.android.com/build/dependencies
- https://developer.android.com/topic/modularization/patterns

## Related Questions

### Prerequisites

- [[q-gradle-basics--android--easy]] - Gradle fundamentals
- [[q-module-types--modularization--medium]] - Module types overview

### Related

- [[q-build-time-optimization--modularization--medium]] - Build performance
- [[q-module-dependency-graph--modularization--hard]] - Dependency graph design

### Advanced

- [[q-convention-plugins--modularization--hard]] - Standardizing dependency configurations
