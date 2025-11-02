---
id: android-024
title: Annotation Processing in Android / Обработка аннотаций в Android
aliases: ["Annotation Processing in Android", "Обработка аннотаций в Android"]
topic: android
subtopics: [gradle, build-variants, dependency-management]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-gradle, c-room, c-hilt, c-dagger, q-kapt-vs-ksp--android--medium, q-gradle-build-system--android--medium, q-build-optimization-gradle--android--medium]
sources: []
created: 2025-10-06
updated: 2025-10-30
tags: [android/gradle, android/build-variants, android/dependency-management, difficulty/medium]
date created: Thursday, October 30th 2025, 11:36:06 am
date modified: Thursday, October 30th 2025, 12:43:07 pm
---

# Вопрос (RU)
> Что такое обработка аннотаций в Android и зачем она нужна?

---

# Question (EN)
> What is annotation processing in Android and why is it needed?

---

## Ответ (RU)

**Обработка аннотаций** — compile-time механизм генерации boilerplate-кода на основе метаданных в исходниках. Процессор анализирует аннотации (@Dao, @Inject, @Entity) и создает .kt/.java файлы, которые компилируются вместе с основным кодом.

**Зачем нужна:**
- Устранение повторяющегося кода (SQL-запросы, DI-графы, сериализаторы)
- Compile-time валидация (Room проверяет SQL-синтаксис на этапе сборки)
- Type-safety без рефлексии (нет runtime-overhead)

**Пример: Room DAO**

```kotlin
// ✅ Разработчик пишет только интерфейс
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?
}

// ✅ Room генерирует UserDao_Impl с SQL-логикой
// Generated: build/generated/ksp/UserDao_Impl.kt
class UserDao_Impl : UserDao {
    override suspend fun getUser(id: String) = /* SQL execution */
}
```

**KAPT vs KSP:**

| Аспект | KAPT (legacy) | KSP (current) |
|--------|---------------|---------------|
| Скорость | Базовая (2x медленнее) | 2x быстрее |
| Workflow | Kotlin → Java stubs → Java AP → Code | Kotlin AST → Code |
| Incremental build | Ограниченная | Полная поддержка |
| Статус | Deprecated | Рекомендовано |

```kotlin
// ❌ KAPT (устарел, добавляет промежуточный Java-слой)
plugins { id("kotlin-kapt") }
dependencies { kapt("androidx.room:room-compiler") }

// ✅ KSP (работает напрямую с Kotlin AST)
plugins { id("com.google.devtools.ksp") }
dependencies { ksp("androidx.room:room-compiler") }
```

**Типичные процессоры:**
- Room — SQL-запросы и DAO
- Hilt/Dagger — DI-граф
- Moshi/kotlinx.serialization — JSON-сериализация
- Parcelize — Parcelable-имплементации

**Оптимизация сборки:**
- KSP вместо KAPT для ускорения в 2x
- Изоляция процессоров по модулям (incremental build)
- `ksp.incremental=true` в gradle.properties
- Кеширование в CI/CD

---

## Answer (EN)

**Annotation processing** is a compile-time code generation mechanism that analyzes metadata in source files (@Dao, @Inject, @Entity) and creates .kt/.java files compiled alongside main code.

**Purpose:**
- Eliminate boilerplate (SQL queries, DI graphs, serializers)
- Compile-time validation (Room validates SQL syntax at build time)
- Type-safety without reflection (no runtime overhead)

**Example: Room DAO**

```kotlin
// ✅ Developer writes only the interface
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?
}

// ✅ Room generates UserDao_Impl with SQL logic
// Generated: build/generated/ksp/UserDao_Impl.kt
class UserDao_Impl : UserDao {
    override suspend fun getUser(id: String) = /* SQL execution */
}
```

**KAPT vs KSP:**

| Aspect | KAPT (legacy) | KSP (current) |
|--------|---------------|---------------|
| Speed | Baseline (2x slower) | 2x faster |
| Workflow | Kotlin → Java stubs → Java AP → Code | Kotlin AST → Code |
| Incremental build | Limited | Full support |
| Status | Deprecated | Recommended |

```kotlin
// ❌ KAPT (legacy, adds intermediate Java layer)
plugins { id("kotlin-kapt") }
dependencies { kapt("androidx.room:room-compiler") }

// ✅ KSP (works directly with Kotlin AST)
plugins { id("com.google.devtools.ksp") }
dependencies { ksp("androidx.room:room-compiler") }
```

**Common processors:**
- Room — SQL queries and DAO
- Hilt/Dagger — DI graph
- Moshi/kotlinx.serialization — JSON serialization
- Parcelize — Parcelable implementations

**Build optimization:**
- KSP instead of KAPT for 2x speedup
- Isolate processors per module (incremental build)
- `ksp.incremental=true` in gradle.properties
- Caching in CI/CD

---

## Follow-ups

- How do you debug KSP processor errors when generated code fails to compile?
- What's the impact of multiple annotation processors on build time and how to measure it?
- How do you migrate a multi-module project from KAPT to KSP without breaking dependencies?
- When should you write a custom KSP processor instead of using reflection?
- How does KSP handle incremental compilation and what triggers full reprocessing?

## References

- [[c-gradle]] — Build system fundamentals and plugin configuration
- [[c-room]] — Room database and DAO generation
- [[c-hilt]] — Dependency injection and component generation
- [[c-dagger]] — DI framework with annotation processing
- [KSP Official Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [Android KSP Migration Guide](https://developer.android.com/build/migrate-to-ksp)

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] — Gradle build configuration and plugins
- [[q-gradle-build-system--android--medium]] — Build phases and task execution

### Related (Same Level)
- [[q-kapt-vs-ksp--android--medium]] — Detailed KAPT vs KSP comparison
- [[q-build-optimization-gradle--android--medium]] — Build performance strategies
- [[q-gradle-version-catalog--android--medium]] — Dependency management with catalogs
- [[q-dagger-build-time-optimization--android--medium]] — Optimizing DI graph generation

### Advanced (Harder)
- [[q-kotlin-dsl-builders--android--hard]] — Creating custom DSLs and code generation
- [[q-compose-compiler-plugin--android--hard]] — Compose compiler and @Composable processing
- Writing custom KSP processors for domain-specific transformations
