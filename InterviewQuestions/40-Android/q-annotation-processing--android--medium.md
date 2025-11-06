---
id: android-067
title: Annotation Processing in Android / Обработка аннотаций в Android
aliases: [Annotation Processing in Android, Обработка аннотаций в Android]
topic: android
subtopics:
  - build-variants
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
  - c-hilt
  - c-room
sources: []
created: 2025-10-12
updated: 2025-10-30
tags: [android/build-variants, android/gradle, annotation-processing, code-generation, difficulty/medium, kapt, ksp]
---

# Вопрос (RU)
> Что такое обработка аннотаций в Android и чем отличаются kapt и KSP?

---

# Question (EN)
> What is annotation processing in Android and what's the difference between kapt and KSP?

---

## Ответ (RU)

**Обработка аннотаций** — это механизм генерации кода на этапе компиляции, где процессоры анализируют аннотации в исходном коде и автоматически создают вспомогательные классы. Используется библиотеками Room, Hilt, Moshi для генерации boilerplate-кода.

### Принцип Работы

```text
Исходный код с аннотациями
    ↓
Компилятор запускает процессоры
    ↓
Процессоры генерируют новые классы
    ↓
Компиляция всего кода вместе
```

### Kapt Vs KSP

**kapt (Kotlin Annotation Processing Tool)**
- Мост между Java-процессорами и Kotlin-кодом
- Генерирует Java-заглушки для совместимости (медленно)
- Устаревший подход, постепенно заменяется KSP

**KSP (Kotlin Symbol Processing)**
- Нативная поддержка Kotlin, работает напрямую с AST
- В 2× быстрее kapt благодаря отсутствию заглушек
- Полная инкрементальная компиляция
- Рекомендуется для всех новых проектов

### Настройка В build.gradle.kts

**❌ Старый подход с kapt:**
```kotlin
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime")
    kapt("androidx.room:room-compiler") // ❌ Медленная генерация
}
```

**✅ Современный подход с KSP:**
```kotlin
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("androidx.room:room-runtime")
    ksp("androidx.room:room-compiler") // ✅ Быстрая генерация
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

// ✅ KSP генерирует автоматически:
// - UserDao_Impl (реализация DAO)
// - User_Table (схема таблицы)
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

// ✅ Hilt генерирует весь граф зависимостей автоматически
```

### Сравнение Производительности

| Аспект | kapt | KSP |
|--------|------|-----|
| Скорость | Базовая | 2× быстрее |
| Язык API | Java | Kotlin |
| Заглушки | Генерирует | Не требуются |
| Инкрементальная компиляция | Ограниченная | Полная |
| Будущее | Устаревает | Активное развитие |

Реальные цифры (проект: Room + Hilt + 50 модулей):
```text
kapt:  ~45 секунд
KSP:   ~23 секунды (↓48%)
```

### Оптимизация Сборки

**Миграция на KSP:**
- Заменить `kotlin-kapt` на `com.google.devtools.ksp` в plugins
- Заменить `kapt()` на `ksp()` в dependencies
- Проверить совместимость библиотек (большинство поддерживают KSP)

**Отладка сгенерированного кода:**
```kotlin
ksp {
    arg("verbose", "true") // Подробное логирование
}

// Путь к сгенерированному коду:
// build/generated/ksp/debug/kotlin/
```

## Answer (EN)

**Annotation processing** is a compile-time code generation mechanism where processors analyze annotations in source code and automatically generate helper classes. Used by libraries like Room, Hilt, and Moshi to generate boilerplate code.

### How It Works

```text
Source code with annotations
    ↓
Compiler runs processors
    ↓
Processors generate new classes
    ↓
All code compiled together
```

### Kapt Vs KSP

**kapt (Kotlin Annotation Processing Tool)**
- Bridge between Java processors and Kotlin code
- Generates Java stubs for compatibility (slow)
- Legacy approach, gradually being replaced by KSP

**KSP (Kotlin Symbol Processing)**
- Native Kotlin support, works directly with AST
- 2× faster than kapt due to no stub generation
- Full incremental compilation support
- Recommended for all new projects

### Setup in build.gradle.kts

**❌ Old approach with kapt:**
```kotlin
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime")
    kapt("androidx.room:room-compiler") // ❌ Slow generation
}
```

**✅ Modern approach with KSP:**
```kotlin
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("androidx.room:room-runtime")
    ksp("androidx.room:room-compiler") // ✅ Fast generation
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

// ✅ KSP automatically generates:
// - UserDao_Impl (DAO implementation)
// - User_Table (table schema)
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

// ✅ Hilt generates entire dependency graph automatically
```

### Performance Comparison

| Aspect | kapt | KSP |
|--------|------|-----|
| Speed | Baseline | 2× faster |
| API Language | Java | Kotlin |
| Stubs | Generates | Not required |
| Incremental compilation | Limited | Full |
| Future | Deprecated | Active development |

Real-world numbers (project: Room + Hilt + 50 modules):
```text
kapt:  ~45 seconds
KSP:   ~23 seconds (↓48%)
```

### Build Optimization

**Migrating to KSP:**
- Replace `kotlin-kapt` with `com.google.devtools.ksp` in plugins
- Replace `kapt()` with `ksp()` in dependencies
- Check library compatibility (most support KSP)

**Debugging generated code:**
```kotlin
ksp {
    arg("verbose", "true") // Verbose logging
}

// Path to generated code:
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
