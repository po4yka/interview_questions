---
id: android-024
title: Annotation Processing in Android / Обработка аннотаций в Android
aliases: [Annotation Processing in Android, Обработка аннотаций в Android]
topic: android
subtopics: [build-variants, dependency-management, gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dagger, c-gradle, c-room, q-android-build-optimization--android--medium, q-android-modularization--android--medium, q-annotation-processing--android--medium, q-build-optimization-gradle--android--medium, q-gradle-build-system--android--medium]
sources: []
created: 2025-10-06
updated: 2025-11-10
tags: [android/build-variants, android/dependency-management, android/gradle, difficulty/medium]
---
# Вопрос (RU)
> Что такое обработка аннотаций в Android и зачем она нужна?

---

# Question (EN)
> What is annotation processing in Android and why is it needed?

---

## Ответ (RU)

**Обработка аннотаций** — compile-time механизм генерации boilerplate-кода на основе метаданных в исходниках. Процессор анализирует аннотации (@Dao, @Inject, @Entity) и создает .kt/.java файлы (или Java-классы), которые попадают в `build/generated/...` и компилируются вместе с основным кодом.

**Зачем нужна:**
- Устранение повторяющегося кода (SQL-запросы, DI-графы, сериализаторы)
- Compile-time валидация (Room проверяет SQL-схемы и SQL-синтаксис на этапе сборки)
- Type-safety без тяжелой рефлексии (меньше runtime-overhead, ошибки находят на этапе компиляции)

**Пример: Room DAO**

```kotlin
// ✅ Разработчик пишет только интерфейс
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?
}

// ✅ Room генерирует реализацию UserDao_Impl с SQL-логикой
// Пример: build/generated/.../UserDao_Impl.java (конкретный путь зависит от KAPT/KSP и настроек)
```

**KAPT vs KSP:**

| Аспект | KAPT (legacy) | KSP (current) |
|--------|---------------|---------------|
| Скорость | Медленнее, использует Java stubs | Заметно быстрее (часто до ~2x) |
| Workflow | Kotlin → Java stubs → Java AP → Code | Kotlin AST → Code |
| Incremental build | Ограниченная, зависит от процессоров | Поддерживает инкрементальность, если процессоры её реализуют |
| Статус | Legacy, использование не рекомендуется для новых интеграций | Рекомендуется, активно развивается |

```kotlin
// ⚠️ KAPT (legacy, добавляет промежуточный Java-слой)
plugins { id("kotlin-kapt") }
dependencies { kapt("androidx.room:room-compiler") }

// ✅ KSP (работает напрямую с Kotlin AST)
plugins { id("com.google.devtools.ksp") }
dependencies { ksp("androidx.room:room-compiler") }
```

**Типичные процессоры:**
- Room — SQL-запросы и DAO
- Hilt/Dagger — DI-граф
- Moshi/kotlinx.serialization — JSON-сериализация (через KAPT/KSP-зависимости, если включены)

(Аннотация `@Parcelize` реализована через compiler plugin, а не классический KAPT/KSP-процессор.)

**Оптимизация сборки:**
- Использовать KSP вместо KAPT, где возможно, для ускорения сборки
- Изоляция процессоров по модулям (улучшение инкрементальных сборок)
- Включение инкрементальности для поддерживающих это процессоров (например, `ksp.incremental=true` в gradle.properties)
- Кеширование в CI/CD

---

## Answer (EN)

**Annotation processing** is a compile-time code generation mechanism that analyzes metadata in source files (@Dao, @Inject, @Entity) and creates .kt/.java (or Java) files under `build/generated/...` that are compiled alongside the main code.

**Purpose:**
- Eliminate boilerplate (SQL queries, DI graphs, serializers)
- Compile-time validation (Room validates schemas and SQL syntax at build time)
- Type-safety without heavy reflection (reduced runtime overhead, errors caught during compilation)

**Example: Room DAO**

```kotlin
// ✅ Developer writes only the interface
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User?
}

// ✅ Room generates a UserDao_Impl implementation with SQL logic
// Example: build/generated/.../UserDao_Impl.java (exact path depends on KAPT/KSP and configuration)
```

**KAPT vs KSP:**

| Aspect | KAPT (legacy) | KSP (current) |
|--------|---------------|---------------|
| Speed | Slower, uses Java stubs | Noticeably faster (often up to ~2x) |
| Workflow | Kotlin → Java stubs → Java AP → Code | Kotlin AST → Code |
| Incremental build | Limited, depends on processors | Supports incremental builds when processors implement it |
| Status | Legacy; discouraged for new integrations | Recommended and actively developed |

```kotlin
// ⚠️ KAPT (legacy, adds intermediate Java layer)
plugins { id("kotlin-kapt") }
dependencies { kapt("androidx.room:room-compiler") }

// ✅ KSP (works directly with Kotlin AST)
plugins { id("com.google.devtools.ksp") }
dependencies { ksp("androidx.room:room-compiler") }
```

**Common processors:**
- Room — SQL queries and DAO implementations
- Hilt/Dagger — DI graph generation
- Moshi/kotlinx.serialization — JSON serialization (via their KAPT/KSP integrations when enabled)

(`@Parcelize` is implemented via a compiler plugin rather than a traditional KAPT/KSP annotation processor.)

**Build optimization:**
- Prefer KSP over KAPT where possible to speed up builds
- Isolate processors per module to improve incremental builds
- Enable incremental processing for supported processors (e.g., `ksp.incremental=true` in gradle.properties)
- Use build cache in CI/CD

---

## Дополнительные Вопросы (RU)

- Как отлаживать ошибки процессоров KSP, когда сгенерированный код не компилируется?
- Каково влияние нескольких процессоров аннотаций на время сборки и как его измерить?
- Как мигрировать мультимодульный проект с KAPT на KSP, не ломая зависимости?
- Когда стоит писать собственный процессор KSP вместо использования рефлексии?
- Как KSP обрабатывает инкрементальную компиляцию и что приводит к полному перерасчету?

## Follow-ups

- How do you debug KSP processor errors when generated code fails to compile?
- What's the impact of multiple annotation processors on build time and how to measure it?
- How do you migrate a multi-module project from KAPT to KSP without breaking dependencies?
- When should you write a custom KSP processor instead of using reflection?
- How does KSP handle incremental compilation and what triggers full reprocessing?

## Ссылки (RU)

- [[c-gradle]] — Основы build-системы и конфигурация плагинов
- [[c-room]] — База данных Room и генерация DAO
- [[c-dagger]] — Фреймворк DI с обработкой аннотаций
- [KSP Official Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [Android KSP Migration Guide](https://developer.android.com/build/migrate-to-ksp)

## References

- [[c-gradle]] — Build system fundamentals and plugin configuration
- [[c-room]] — Room database and DAO generation
- [[c-dagger]] — DI framework with annotation processing
- [KSP Official Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [Android KSP Migration Guide](https://developer.android.com/build/migrate-to-ksp)

## Связанные Вопросы (RU)

### База (проще)
- [[q-gradle-build-system--android--medium]] — Фазы сборки и выполнение задач

### Связанные (тот Же уровень)
- [[q-kapt-vs-ksp--android--medium]] — Подробное сравнение KAPT и KSP
- [[q-build-optimization-gradle--android--medium]] — Стратегии оптимизации сборки

### Продвинутые (сложнее)
- Написание собственных процессоров KSP для доменно-специфичных трансформаций

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-build-system--android--medium]] — Build phases and task execution

### Related (Same Level)
- [[q-kapt-vs-ksp--android--medium]] — Detailed KAPT vs KSP comparison
- [[q-build-optimization-gradle--android--medium]] — Build performance strategies

### Advanced (Harder)
- Writing custom KSP processors for domain-specific transformations
