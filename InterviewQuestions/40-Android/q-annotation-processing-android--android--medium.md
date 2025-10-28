---
id: 20251006-100012
title: Annotation Processing in Android / Обработка аннотаций в Android
aliases: ["Annotation Processing in Android", "Обработка аннотаций в Android"]
topic: android
subtopics: [gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-build-optimization--android--medium, q-android-modularization--android--medium, q-android-project-parts--android--easy]
sources: []
created: 2025-10-06
updated: 2025-10-28
tags: [android/gradle, difficulty/medium]
---
# Вопрос (RU)
> Что такое обработка аннотаций в Android и зачем она нужна?

---

# Question (EN)
> What is annotation processing in Android and why is it needed?

---

## Ответ (RU)

**Обработка аннотаций** — это compile-time механизм генерации кода на основе аннотаций в исходном коде. Процессор анализирует аннотации во время компиляции и создает дополнительные файлы .kt/.java, которые компилируются вместе с основным кодом.

**Основной принцип:**

```kotlin
Source Code + Annotations → Annotation Processor → Generated Code → Compiled App
```

**Пример: Room Database**

```kotlin
// ✅ Аннотированный интерфейс
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?

    @Insert
    suspend fun insert(user: User)
}

// ✅ Room генерирует UserDao_Impl.kt с полной реализацией
// Разработчик пишет только интерфейс
```

**KAPT vs KSP:**

KAPT (устаревший подход) конвертирует Kotlin → Java stubs → Java annotation processors, что замедляет сборку в 2x. KSP работает напрямую с Kotlin AST и обеспечивает нативную поддержку Kotlin-специфичных конструкций.

```kotlin
// ❌ KAPT (deprecated)
plugins {
    id("kotlin-kapt")
}
dependencies {
    kapt("androidx.room:room-compiler")
}

// ✅ KSP (preferred)
plugins {
    id("com.google.devtools.ksp")
}
dependencies {
    ksp("androidx.room:room-compiler")
}
```

**Популярные библиотеки:**
- Room — генерация SQL и DAO реализаций
- Hilt/Dagger — DI граф и инъекции
- Moshi — JSON адаптеры
- Glide — RequestManager и GlideApp

**Best practices:**
- Мигрируйте на KSP для новых проектов
- Изолируйте процессоры в отдельных модулях для incremental compilation
- Кешируйте generated код в CI

---

## Answer (EN)

**Annotation processing** is a compile-time code generation mechanism that analyzes annotations in source code and generates additional .kt/.java files, which are compiled alongside the main code.

**Core principle:**

```kotlin
Source Code + Annotations → Annotation Processor → Generated Code → Compiled App
```

**Example: Room Database**

```kotlin
// ✅ Annotated interface
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?

    @Insert
    suspend fun insert(user: User)
}

// ✅ Room generates UserDao_Impl.kt with full implementation
// Developer writes only the interface
```

**KAPT vs KSP:**

KAPT (legacy approach) converts Kotlin → Java stubs → Java annotation processors, slowing builds by 2x. KSP works directly with Kotlin AST and provides native support for Kotlin-specific constructs.

```kotlin
// ❌ KAPT (deprecated)
plugins {
    id("kotlin-kapt")
}
dependencies {
    kapt("androidx.room:room-compiler")
}

// ✅ KSP (preferred)
plugins {
    id("com.google.devtools.ksp")
}
dependencies {
    ksp("androidx.room:room-compiler")
}
```

**Popular libraries:**
- Room — SQL and DAO implementation generation
- Hilt/Dagger — DI graph and injections
- Moshi — JSON adapters
- Glide — RequestManager and GlideApp

**Best practices:**
- Migrate to KSP for new projects
- Isolate processors in separate modules for incremental compilation
- Cache generated code in CI

---

## Follow-ups

- How do you debug annotation processor errors during compilation?
- What's the difference between SOURCE, CLASS, and RUNTIME retention policies?
- How do you migrate an existing project from KAPT to KSP?
- What are the build performance implications of multiple annotation processors?
- How does incremental annotation processing work?

## References

- [KSP Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [KSP vs KAPT Comparison](https://android-developers.googleblog.com/2021/09/accelerated-kotlin-build-times-with.html)

## Related Questions

### Prerequisites
- [[q-android-project-parts--android--easy]] — Understanding Gradle modules and build configuration
- Annotation basics and Java/Kotlin reflection fundamentals

### Related
- [[q-android-build-optimization--android--medium]] — Build performance and caching strategies
- [[q-android-modularization--android--medium]] — Organizing processors in separate modules
- Room database architecture and code generation patterns

### Advanced
- Writing custom KSP processors for domain-specific code generation
- Incremental annotation processing and build cache optimization