---
id: android-067
title: Annotation Processing in Android / Обработка аннотаций в Android
aliases: [Annotation Processing in Android, Обработка аннотаций в Android]
topic: android
subtopics:
  - build-variants
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-hilt
  - c-room
  - q-android-build-optimization--android--medium
  - q-annotation-processing-android--android--medium
  - q-module-types-android--android--medium
sources: []
created: 2025-10-12
updated: 2025-10-30
tags: [android/build-variants, android/gradle, annotation-processing, code-generation, difficulty/medium, kapt, ksp]
date created: Saturday, November 1st 2025, 1:03:46 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Что такое обработка аннотаций в Android и чем отличаются kapt и KSP?

---

# Question (EN)
> What is annotation processing in Android and what's the difference between kapt and KSP?

---

## Ответ (RU)

**Обработка аннотаций** — это механизм генерации кода на этапе компиляции, при котором специальные процессоры анализируют аннотации в исходном коде и автоматически создают вспомогательные классы/файлы. Активно используется библиотеками Room, Hilt, Moshi для генерации boilerplate-кода.

### Принцип Работы

```text
Исходный код с аннотациями
    ↓
Компилятор запускает процессоры
    ↓
Процессоры генерируют новые классы/файлы
    ↓
Компиляция всего кода вместе
```

### Kapt Vs KSP

**kapt (Kotlin Annotation Processing Tool)**
- Мост между Java-аннотационными процессорами и Kotlin-кодом
- Генерирует Java-заглушки для совместимости (это замедляет сборку)
- Поддерживается, но развитие ограничено; для новых проектов рекомендуется KSP

**KSP (Kotlin Symbol Processing)**
- Нативная поддержка Kotlin, работает с моделью символов Kotlin (без генерации Java-заглушек)
- Обычно до ~2× быстрее kapt за счёт отсутствия заглушек и лучшей интеграции с компилятором (фактический выигрыш зависит от проекта)
- Поддерживает полноценную инкрементальную компиляцию (при корректной реализации процессоров)
- Рекомендуется для всех новых проектов и при миграции с kapt, когда библиотеки поддерживают KSP

### Настройка В build.gradle.kts

**❌ Старый подход с kapt:**
```kotlin
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime")
    kapt("androidx.room:room-compiler") // ❌ Медленнее из-за генерации заглушек
}
```

**✅ Современный подход с KSP:**
```kotlin
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("androidx.room:room-runtime")
    ksp("androidx.room:room-compiler") // ✅ Быстрее и лучше интегрируется с Kotlin-компилятором
}
```

### Пример: Room Генерирует DAO

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Long): User?
}

// ✅ Обработчик аннотаций (через kapt или KSP, в зависимости от конфигурации)
// генерирует, например:
// - UserDao_Impl (реализация DAO)
// - вспомогательные классы/метаданные для схемы
```

### Пример: Hilt Генерирует DI Компоненты

```kotlin
@HiltAndroidApp
class App : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity()

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repo: UserRepository
) : ViewModel()

// ✅ Hilt через аннотационную обработку генерирует граф зависимостей и компоненты автоматически
```

### Сравнение Производительности

| Аспект | kapt | KSP |
|--------|------|-----|
| Скорость | Базовая, медленнее из-за заглушек | Обычно быстрее (до ~2×, зависит от проекта) |
| Язык API | Java (JSR 269) | Kotlin-first API (модель символов) |
| Заглушки | Генерирует Java-заглушки | Не требуются |
| Инкрементальная компиляция | Ограниченная | Полная поддержка (при корректных процессорах) |
| Будущее | Поддерживается, но без активного развития | Активное развитие, рекомендованный путь |

Примерные цифры (условный проект: Room + Hilt + 50 модулей):
```text
kapt:  ~45 секунд
KSP:   ~23 секунды (↓≈48%)
```
Фактические значения зависят от конкретного проекта и конфигурации.

### Оптимизация Сборки

**Миграция на KSP:**
- Заменить `kotlin-kapt` на `com.google.devtools.ksp` в `plugins`
- Заменить `kapt()` на `ksp()` в `dependencies`, если библиотека предоставляет KSP-артефакт
- Проверить совместимость библиотек (многие популярные библиотеки уже поддерживают KSP)

**Отладка сгенерированного кода:**
```kotlin
ksp {
    arg("verbose", "true") // Подробное логирование
}

// Путь к сгенерированному коду (пример для debug-билда):
// build/generated/ksp/debug/kotlin/
```

## Answer (EN)

**Annotation processing** is a compile-time code generation mechanism where processors analyze annotations in source code and automatically generate helper classes/files. Widely used by libraries like Room, Hilt, and Moshi to generate boilerplate code.

### How It Works

```text
Source code with annotations
    ↓
Compiler runs processors
    ↓
Processors generate new classes/files
    ↓
All code compiled together
```

### Kapt Vs KSP

**kapt (Kotlin Annotation Processing Tool)**
- Bridge between Java annotation processors and Kotlin code
- Generates Java stubs for compatibility (which slows down the build)
- Still supported but with limited evolution; KSP is recommended for new code when available

**KSP (Kotlin Symbol Processing)**
- Kotlin-first processing API that works with Kotlin symbol model (no Java stub generation)
- Typically up to around 2× faster than kapt due to no stubs and better compiler integration (actual gains depend on the project)
- Supports full incremental compilation (assuming processors are implemented correctly)
- Recommended for all new projects and for migration from kapt where libraries provide KSP support

### Setup in build.gradle.kts

**❌ Old approach with kapt:**
```kotlin
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime")
    kapt("androidx.room:room-compiler") // ❌ Slower due to stub generation
}
```

**✅ Modern approach with KSP:**
```kotlin
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("androidx.room:room-runtime")
    ksp("androidx.room:room-compiler") // ✅ Faster and better integrated with Kotlin compiler
}
```

### Example: Room Generates DAO

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Long): User?
}

// ✅ The annotation processor (via kapt or KSP, depending on configuration)
// generates, for example:
// - UserDao_Impl (DAO implementation)
// - supporting classes/metadata for the schema
```

### Example: Hilt Generates DI Components

```kotlin
@HiltAndroidApp
class App : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity()

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repo: UserRepository
) : ViewModel()

// ✅ Hilt uses annotation processing to generate the dependency graph and components automatically
```

### Performance Comparison

| Aspect | kapt | KSP |
|--------|------|-----|
| Speed | Baseline, slower due to stubs | Typically faster (up to ~2×, project-dependent) |
| API Language | Java (JSR 269) | Kotlin-first symbol API |
| Stubs | Generates Java stubs | Not required |
| Incremental compilation | Limited | Full support (with properly implemented processors) |
| Future | Supported, but not actively evolved | Actively developed, recommended path |

Example numbers (hypothetical project: Room + Hilt + 50 modules):
```text
kapt:  ~45 seconds
KSP:   ~23 seconds (↓≈48%)
```
Actual gains vary by project and configuration.

### Build Optimization

**Migrating to KSP:**
- Replace `kotlin-kapt` with `com.google.devtools.ksp` in `plugins`
- Replace `kapt()` with `ksp()` in `dependencies` where the library exposes KSP artifacts
- Check library compatibility (many popular libraries already support KSP)

**Debugging generated code:**
```kotlin
ksp {
    arg("verbose", "true") // Verbose logging
}

// Path to generated code (example for debug build):
// build/generated/ksp/debug/kotlin/
```

---

## Follow-ups

- How do you write a custom KSP processor for your own annotations?
- What happens if kapt and KSP are used together in the same module?
- How does annotation processing affect incremental compilation and build cache?
- What are the debugging strategies when generated code doesn't compile?
- Which popular Android libraries have migrated from kapt to KSP support?

## References

- [[c-room]] - Database ORM using annotation processing
- [[c-hilt]] - Dependency injection with code generation
- [KSP Official Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [Migrating from kapt to KSP](https://developer.android.com/build/migrate-to-ksp)
- [KSP Performance Benchmarks](https://android-developers.googleblog.com/2021/09/accelerated-kotlin-build-times-with.html)

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]] - Android project structure basics
- [[q-gradle-basics--android--easy]] - Gradle build system fundamentals

### Related (Same Level)
- [[q-android-build-optimization--android--medium]] - Build performance optimization strategies
- [[q-android-modularization--android--medium]] - Module architecture and organization
- [[q-room-library-definition--android--easy]] - Room ORM basics and usage

### Advanced (Harder)
 - Writing custom KSP processors
 - Gradle build phases and hooks
 - Advanced build performance profiling
