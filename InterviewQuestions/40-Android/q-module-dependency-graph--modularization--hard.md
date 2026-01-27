---
id: android-mod-004
title: Designing Module Dependency Graph / Проектирование графа зависимостей модулей
aliases:
- Module Dependency Graph
- Dependency Graph Design
- Граф зависимостей модулей
topic: android
subtopics:
- modularization
- architecture
- gradle
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android
- q-module-types--modularization--medium
- q-api-vs-implementation--modularization--medium
created: 2026-01-23
updated: 2026-01-23
sources: []
tags:
- android/modularization
- android/architecture
- android/gradle
- difficulty/hard
- dependency-graph
anki_cards:
- slug: android-mod-004-0-en
  language: en
- slug: android-mod-004-0-ru
  language: ru
---
# Вопрос (RU)

> Как правильно спроектировать граф зависимостей модулей? Какие принципы и анти-паттерны нужно учитывать?

# Question (EN)

> How do you properly design a module dependency graph? What principles and anti-patterns should you consider?

---

## Ответ (RU)

Правильный граф зависимостей - основа масштабируемой модульной архитектуры. Плохой граф приводит к долгим сборкам, сложному тестированию и техническому долгу.

### Ключевые Принципы

#### 1. Направленный Ациклический Граф (DAG)

```
        app
       / | \
      /  |  \
     v   v   v
   home profile settings   <- Feature layer
     \   |   /
      \  |  /
       v v v
       domain              <- Domain layer
         |
         v
        data               <- Data layer
         |
         v
       common              <- Infrastructure
```

**Правило**: Зависимости направлены ВНИЗ. Никогда вверх или в сторону на том же уровне.

#### 2. Правило Зависимостей (Dependency Rule)

```kotlin
// ПРАВИЛЬНО: Зависимость от абстракции (domain)
// core/data/build.gradle.kts
dependencies {
    implementation(project(":core:domain")) // Data зависит от Domain
}

// НЕПРАВИЛЬНО: Инверсия зависимости
// core/domain/build.gradle.kts
dependencies {
    implementation(project(":core:data")) // BAD - Domain не должен знать о Data
}
```

#### 3. Инверсия Зависимостей

```kotlin
// core/domain - определяет интерфейс
interface UserRepository {
    suspend fun getUser(id: String): User
    fun observeUser(id: String): Flow<User>
}

// core/data - реализует интерфейс
class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override suspend fun getUser(id: String) = api.getUser(id).toDomain()
    override fun observeUser(id: String) = dao.observeUser(id).map { it.toDomain() }
}

// DI связывает их
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

### Типичный Граф Модулей

```
                    +----------+
                    |   :app   |
                    +----+-----+
                         |
        +----------------+----------------+
        |                |                |
   +----v----+     +-----v-----+    +-----v-----+
   |:feature |     |:feature   |    |:feature   |
   |  :home  |     | :profile  |    |:settings  |
   +----+----+     +-----+-----+    +-----+-----+
        |                |                |
        +----------------+----------------+
                         |
        +----------------+----------------+
        |                |                |
   +----v----+     +-----v-----+    +-----v-----+
   |:core    |     |:core      |    |:core      |
   | :ui     |     | :domain   |    | :data     |
   +----+----+     +-----+-----+    +-----+-----+
        |                |                |
        +----------------+----------------+
                         |
                   +-----v-----+
                   |:core      |
                   | :common   |
                   +-----------+
```

### Слои и Их Зависимости

| Слой | Зависит от | Не зависит от |
|------|------------|---------------|
| `:app` | все features, DI setup | - |
| `:feature:*` | `:core:domain`, `:core:ui` | другие features |
| `:core:ui` | `:core:common`, design system | `:core:data` |
| `:core:domain` | `:core:common`, `:core:model` | `:core:data`, `:core:network` |
| `:core:data` | `:core:domain`, `:core:network`, `:core:database` | features |
| `:core:common` | только stdlib | все остальное |

### Анти-паттерны

#### 1. Циклические Зависимости

```kotlin
// BAD: Цикл A -> B -> C -> A
// :feature:home -> :feature:profile -> :feature:home

// РЕШЕНИЕ: Выносим общее в core-модуль
// Обе features зависят от :core:navigation
```

#### 2. Feature-to-Feature Зависимости

```kotlin
// BAD
// feature/profile/build.gradle.kts
dependencies {
    implementation(project(":feature:settings")) // WRONG
}

// GOOD: Общение через navigation API или app-модуль
```

#### 3. God Module

```kotlin
// BAD: Один модуль знает обо всем
// core/everything/build.gradle.kts
dependencies {
    api(project(":core:network"))
    api(project(":core:database"))
    api(project(":core:ui"))
    api(project(":feature:home"))  // WTF?
    api(project(":feature:profile"))
}

// GOOD: Разбить на специализированные модули
```

#### 4. Leaky Abstractions

```kotlin
// BAD: Room Entity в domain слое
// core/domain/model/UserEntity.kt
@Entity(tableName = "users")  // Room annotation в domain!
data class UserEntity(...)

// GOOD: Отдельные модели для каждого слоя
// core/model/User.kt - domain model
data class User(val id: String, val name: String)

// core/database/entity/UserEntity.kt - database model
@Entity(tableName = "users")
data class UserEntity(...)
```

### Визуализация Графа

```bash
# Генерация графа зависимостей
./gradlew :app:dependencies --configuration implementation > deps.txt

# Или используйте плагин
plugins {
    id("com.savvasdalkitsis.module-dependency-graph") version "0.12"
}

# Команда
./gradlew graphModules
```

### Метрики Здоровья Графа

```kotlin
// build-logic/convention/src/.../ModuleMetrics.kt
// Плагин для проверки правил модуляризации

tasks.register("checkModuleRules") {
    doLast {
        val violations = mutableListOf<String>()

        // Правило 1: Features не зависят от features
        project.subprojects.filter { it.path.startsWith(":feature:") }.forEach { feature ->
            feature.configurations.findByName("implementation")?.dependencies?.forEach { dep ->
                if (dep is ProjectDependency && dep.dependencyProject.path.startsWith(":feature:")) {
                    violations.add("${feature.path} depends on ${dep.dependencyProject.path}")
                }
            }
        }

        // Правило 2: Domain не зависит от data
        project.findProject(":core:domain")?.let { domain ->
            domain.configurations.findByName("implementation")?.dependencies?.forEach { dep ->
                if (dep is ProjectDependency && dep.dependencyProject.path == ":core:data") {
                    violations.add("Domain depends on Data - violates dependency rule")
                }
            }
        }

        if (violations.isNotEmpty()) {
            throw GradleException("Module rule violations:\n${violations.joinToString("\n")}")
        }
    }
}
```

### Стратегия Декомпозиции

| Когда выделять модуль? | Пример |
|------------------------|--------|
| Переиспользуется в 2+ местах | `:core:analytics` |
| Имеет отдельный домен | `:feature:payments` |
| Требует изоляции для тестов | `:core:testing` |
| Может быть опубликован | `:lib:design-system` |
| Замедляет сборку | Разбить большой модуль |

### Пример: Реальный Граф (Now in Android)

```
app
 |
 +-- feature:foryou
 |     +-- core:ui
 |     +-- core:domain
 |     +-- core:data
 |
 +-- feature:interests
 |     +-- core:ui
 |     +-- core:domain
 |     +-- core:data
 |
 +-- feature:bookmarks
 |     +-- core:ui
 |     +-- core:domain
 |
 +-- core:ui
 |     +-- core:designsystem
 |     +-- core:model
 |
 +-- core:domain
 |     +-- core:data (api)
 |     +-- core:model
 |
 +-- core:data
 |     +-- core:network
 |     +-- core:database
 |     +-- core:datastore
 |     +-- core:model
 |
 +-- core:designsystem
 |     +-- (no project dependencies)
 |
 +-- core:model
       +-- (no project dependencies)
```

---

## Answer (EN)

A proper dependency graph is the foundation of scalable modular architecture. A bad graph leads to slow builds, difficult testing, and technical debt.

### Key Principles

#### 1. Directed Acyclic Graph (DAG)

```
        app
       / | \
      /  |  \
     v   v   v
   home profile settings   <- Feature layer
     \   |   /
      \  |  /
       v v v
       domain              <- Domain layer
         |
         v
        data               <- Data layer
         |
         v
       common              <- Infrastructure
```

**Rule**: Dependencies flow DOWN. Never up or sideways at the same level.

#### 2. Dependency Rule

```kotlin
// CORRECT: Depend on abstraction (domain)
// core/data/build.gradle.kts
dependencies {
    implementation(project(":core:domain")) // Data depends on Domain
}

// INCORRECT: Dependency inversion
// core/domain/build.gradle.kts
dependencies {
    implementation(project(":core:data")) // BAD - Domain shouldn't know about Data
}
```

#### 3. Dependency Inversion

```kotlin
// core/domain - defines interface
interface UserRepository {
    suspend fun getUser(id: String): User
    fun observeUser(id: String): Flow<User>
}

// core/data - implements interface
class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override suspend fun getUser(id: String) = api.getUser(id).toDomain()
    override fun observeUser(id: String) = dao.observeUser(id).map { it.toDomain() }
}

// DI wires them together
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

### Typical Module Graph

```
                    +----------+
                    |   :app   |
                    +----+-----+
                         |
        +----------------+----------------+
        |                |                |
   +----v----+     +-----v-----+    +-----v-----+
   |:feature |     |:feature   |    |:feature   |
   |  :home  |     | :profile  |    |:settings  |
   +----+----+     +-----+-----+    +-----+-----+
        |                |                |
        +----------------+----------------+
                         |
        +----------------+----------------+
        |                |                |
   +----v----+     +-----v-----+    +-----v-----+
   |:core    |     |:core      |    |:core      |
   | :ui     |     | :domain   |    | :data     |
   +----+----+     +-----+-----+    +-----+-----+
        |                |                |
        +----------------+----------------+
                         |
                   +-----v-----+
                   |:core      |
                   | :common   |
                   +-----------+
```

### Layers and Their Dependencies

| Layer | Depends On | Does Not Depend On |
|-------|------------|-------------------|
| `:app` | all features, DI setup | - |
| `:feature:*` | `:core:domain`, `:core:ui` | other features |
| `:core:ui` | `:core:common`, design system | `:core:data` |
| `:core:domain` | `:core:common`, `:core:model` | `:core:data`, `:core:network` |
| `:core:data` | `:core:domain`, `:core:network`, `:core:database` | features |
| `:core:common` | stdlib only | everything else |

### Anti-patterns

#### 1. Circular Dependencies

```kotlin
// BAD: Cycle A -> B -> C -> A
// :feature:home -> :feature:profile -> :feature:home

// SOLUTION: Extract shared code to core module
// Both features depend on :core:navigation
```

#### 2. Feature-to-Feature Dependencies

```kotlin
// BAD
// feature/profile/build.gradle.kts
dependencies {
    implementation(project(":feature:settings")) // WRONG
}

// GOOD: Communicate via navigation API or app module
```

#### 3. God Module

```kotlin
// BAD: One module knows everything
// core/everything/build.gradle.kts
dependencies {
    api(project(":core:network"))
    api(project(":core:database"))
    api(project(":core:ui"))
    api(project(":feature:home"))  // WTF?
    api(project(":feature:profile"))
}

// GOOD: Split into specialized modules
```

#### 4. Leaky Abstractions

```kotlin
// BAD: Room Entity in domain layer
// core/domain/model/UserEntity.kt
@Entity(tableName = "users")  // Room annotation in domain!
data class UserEntity(...)

// GOOD: Separate models for each layer
// core/model/User.kt - domain model
data class User(val id: String, val name: String)

// core/database/entity/UserEntity.kt - database model
@Entity(tableName = "users")
data class UserEntity(...)
```

### Visualizing the Graph

```bash
# Generate dependency graph
./gradlew :app:dependencies --configuration implementation > deps.txt

# Or use a plugin
plugins {
    id("com.savvasdalkitsis.module-dependency-graph") version "0.12"
}

# Command
./gradlew graphModules
```

### Graph Health Metrics

```kotlin
// build-logic/convention/src/.../ModuleMetrics.kt
// Plugin to check modularization rules

tasks.register("checkModuleRules") {
    doLast {
        val violations = mutableListOf<String>()

        // Rule 1: Features don't depend on features
        project.subprojects.filter { it.path.startsWith(":feature:") }.forEach { feature ->
            feature.configurations.findByName("implementation")?.dependencies?.forEach { dep ->
                if (dep is ProjectDependency && dep.dependencyProject.path.startsWith(":feature:")) {
                    violations.add("${feature.path} depends on ${dep.dependencyProject.path}")
                }
            }
        }

        // Rule 2: Domain doesn't depend on data
        project.findProject(":core:domain")?.let { domain ->
            domain.configurations.findByName("implementation")?.dependencies?.forEach { dep ->
                if (dep is ProjectDependency && dep.dependencyProject.path == ":core:data") {
                    violations.add("Domain depends on Data - violates dependency rule")
                }
            }
        }

        if (violations.isNotEmpty()) {
            throw GradleException("Module rule violations:\n${violations.joinToString("\n")}")
        }
    }
}
```

### Decomposition Strategy

| When to extract a module? | Example |
|---------------------------|---------|
| Reused in 2+ places | `:core:analytics` |
| Has separate domain | `:feature:payments` |
| Needs test isolation | `:core:testing` |
| Can be published | `:lib:design-system` |
| Slows down builds | Split large module |

### Example: Real Graph (Now in Android)

```
app
 |
 +-- feature:foryou
 |     +-- core:ui
 |     +-- core:domain
 |     +-- core:data
 |
 +-- feature:interests
 |     +-- core:ui
 |     +-- core:domain
 |     +-- core:data
 |
 +-- feature:bookmarks
 |     +-- core:ui
 |     +-- core:domain
 |
 +-- core:ui
 |     +-- core:designsystem
 |     +-- core:model
 |
 +-- core:domain
 |     +-- core:data (api)
 |     +-- core:model
 |
 +-- core:data
 |     +-- core:network
 |     +-- core:database
 |     +-- core:datastore
 |     +-- core:model
 |
 +-- core:designsystem
 |     +-- (no project dependencies)
 |
 +-- core:model
       +-- (no project dependencies)
```

---

## Follow-ups

- How do you handle database migrations across modules?
- What tools can validate the dependency graph in CI?
- How do you refactor a monolith into modules incrementally?

## References

- https://developer.android.com/topic/modularization/patterns
- https://github.com/android/nowinandroid
- https://www.droidcon.com/2022/06/28/modularization-patterns/

## Related Questions

### Prerequisites

- [[q-module-types--modularization--medium]] - Module types overview
- [[q-api-vs-implementation--modularization--medium]] - API boundaries

### Related

- [[q-build-time-optimization--modularization--medium]] - Build performance
- [[q-feature-module-navigation--modularization--hard]] - Navigation patterns

### Advanced

- [[q-convention-plugins--modularization--hard]] - Gradle convention plugins
- [[q-dynamic-feature-modules--modularization--hard]] - Dynamic feature delivery
