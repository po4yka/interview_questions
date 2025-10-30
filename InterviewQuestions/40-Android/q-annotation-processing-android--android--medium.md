---
id: 20251006-100012
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
related: [q-android-build-optimization--android--medium, q-android-modularization--android--medium, q-android-project-parts--android--easy]
sources: []
created: 2025-10-06
updated: 2025-10-29
tags: [android/gradle, android/build-variants, android/dependency-management, difficulty/medium]
---
# Вопрос (RU)
> Что такое обработка аннотаций в Android и зачем она нужна?

---

# Question (EN)
> What is annotation processing in Android and why is it needed?

---

## Ответ (RU)

**Обработка аннотаций** — это compile-time механизм генерации кода на основе метаданных в исходниках. Процессор анализирует аннотации и создает дополнительные .kt/.java файлы, компилируемые вместе с основным кодом.

**Принцип работы:**

```kotlin
// Source + @Annotations → Processor → Generated Code → Compiled App
```

**Пример: Room Database**

```kotlin
// ✅ Разработчик пишет только интерфейс
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?

    @Insert
    suspend fun insert(user: User)
}

// ✅ Room генерирует UserDao_Impl.kt с SQL-логикой
```

**KAPT vs KSP:**

KAPT конвертирует Kotlin → Java stubs → Java AP, замедляя сборку в 2x. KSP работает напрямую с Kotlin AST без промежуточного Java-кода.

```kotlin
// ❌ KAPT (устарел)
plugins { id("kotlin-kapt") }
dependencies { kapt("androidx.room:room-compiler") }

// ✅ KSP (рекомендован)
plugins { id("com.google.devtools.ksp") }
dependencies { ksp("androidx.room:room-compiler") }
```

**Типичные процессоры:**
- Room — SQL-запросы и DAO
- Hilt/Dagger — DI-граф
- Moshi — JSON-сериализаторы
- Parcelize — Parcelable-имплементации

**Оптимизация:**
- Используйте KSP вместо KAPT
- Изолируйте процессоры по модулям для incremental build
- Кешируйте generated-код в CI/CD
- Применяйте `ksp.incremental=true` в gradle.properties

---

## Answer (EN)

**Annotation processing** is a compile-time code generation mechanism that analyzes metadata in source files. Processors create additional .kt/.java files compiled alongside main code.

**Workflow:**

```kotlin
// Source + @Annotations → Processor → Generated Code → Compiled App
```

**Example: Room Database**

```kotlin
// ✅ Developer writes only the interface
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?

    @Insert
    suspend fun insert(user: User)
}

// ✅ Room generates UserDao_Impl.kt with SQL logic
```

**KAPT vs KSP:**

KAPT converts Kotlin → Java stubs → Java AP, slowing builds by 2x. KSP works directly with Kotlin AST without intermediate Java code.

```kotlin
// ❌ KAPT (legacy)
plugins { id("kotlin-kapt") }
dependencies { kapt("androidx.room:room-compiler") }

// ✅ KSP (recommended)
plugins { id("com.google.devtools.ksp") }
dependencies { ksp("androidx.room:room-compiler") }
```

**Common processors:**
- Room — SQL queries and DAO
- Hilt/Dagger — DI graph
- Moshi — JSON serializers
- Parcelize — Parcelable implementations

**Optimization:**
- Use KSP instead of KAPT
- Isolate processors per module for incremental build
- Cache generated code in CI/CD
- Enable `ksp.incremental=true` in gradle.properties

---

## Follow-ups

- How do you debug KSP processor errors when generated code fails to compile?
- What's the impact of multiple annotation processors on build time and how to measure it?
- How do you migrate a multi-module project from KAPT to KSP without breaking the build?
- When should you write a custom KSP processor instead of using reflection?
- How does incremental annotation processing work with KSP and what's the cache invalidation strategy?

## References

- [KSP Official Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [Android Developers Blog: KSP vs KAPT](https://android-developers.googleblog.com/2021/09/accelerated-kotlin-build-times-with.html)
- [Room Migration Guide: KAPT to KSP](https://developer.android.com/build/migrate-to-ksp)
- [[c-gradle]] — Build system fundamentals

## Related Questions

### Prerequisites
- [[q-android-project-parts--android--easy]] — Gradle modules and build configuration basics
- Understanding Kotlin reflection and meta-programming concepts
- Java annotation fundamentals and retention policies

### Related
- [[q-android-build-optimization--android--medium]] — Build performance and caching strategies
- [[q-android-modularization--android--medium]] — Module isolation for incremental builds
- Room database architecture and DAO generation patterns
- Hilt dependency injection and compile-time code generation

### Advanced
- Writing custom KSP processors for domain-specific transformations
- Debugging annotation processor errors in multi-module projects
- Build cache optimization and incremental annotation processing strategies