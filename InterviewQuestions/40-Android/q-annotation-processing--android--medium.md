---
id: 20251012-140600
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
related: [c-room, c-hilt, q-android-build-optimization--android--medium, q-android-modularization--android--medium]
sources: []
created: 2025-10-12
updated: 2025-10-29
tags: [android/gradle, android/build-variants, android/dependency-management, annotation-processing, kapt, ksp, code-generation, difficulty/medium]
---
# Вопрос (RU)
> Что такое обработка аннотаций в Android и чем отличаются kapt и KSP?

---

# Question (EN)
> What is annotation processing in Android and what's the difference between kapt and KSP?

---

## Ответ (RU)

**Обработка аннотаций** — это механизм генерации кода на этапе компиляции, где процессоры анализируют аннотации в исходном коде и автоматически создают вспомогательные классы. Используется библиотеками Room, Hilt, Moshi для генерации boilerplate-кода.

### Как работает обработка аннотаций

```text
Исходный код с аннотациями
    ↓
Компилятор запускает процессоры
    ↓
Процессоры генерируют новые классы
    ↓
Компиляция всего кода вместе
    ↓
APK/AAR
```

### Два основных процессора

**kapt (Kotlin Annotation Processing Tool)**
- Мост между Java-процессорами и Kotlin-кодом
- Генерирует Java-заглушки (медленно)
- Устаревший подход

**KSP (Kotlin Symbol Processing)**
- Нативная поддержка Kotlin
- В 2 раза быстрее kapt
- Не требует генерации заглушек
- Рекомендуется для новых проектов

### Примеры использования

**❌ Старый подход с kapt:**
```kotlin
// build.gradle.kts
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0")
}
```

**✅ Современный подход с KSP:**
```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    ksp("androidx.room:room-compiler:2.6.0")
}
```

### Room с обработкой аннотаций

```kotlin
// Определяем Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String
)

// Определяем DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Long): User?
}

// Процессор генерирует:
// - UserDao_Impl (реализация DAO)
// - User_Table (схема таблицы)
// - AppDatabase_Impl (реализация базы)
```

### Hilt с обработкой аннотаций

```kotlin
@HiltAndroidApp
class App : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity()

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repo: UserRepository
) : ViewModel()

// ✅ Hilt генерирует все компоненты DI автоматически
```

### Moshi с обработкой аннотаций

```kotlin
@JsonClass(generateAdapter = true)
data class ApiResponse(
    @Json(name = "user_id") val userId: Long,
    val name: String
)

// ✅ Генерируется оптимизированный ApiResponseJsonAdapter
```

### Сравнение kapt vs KSP

| Аспект | kapt | KSP |
|--------|------|-----|
| Скорость | Базовая | 2x быстрее |
| Язык API | Java | Kotlin |
| Заглушки | Генерирует | Не требуются |
| Инкрементальная компиляция | Ограничена | Полная |
| Будущее | Устаревает | Активно развивается |

**Реальные цифры:**
```text
Проект: Room + Hilt + 50 модулей
kapt:  ~45 секунд
KSP:   ~23 секунды (на 48% быстрее)
```

### Лучшие практики

**Миграция на KSP:**
```kotlin
// ❌ Старое
plugins {
    id("kotlin-kapt")
}
dependencies {
    kapt("androidx.room:room-compiler")
}

// ✅ Новое
plugins {
    id("com.google.devtools.ksp")
}
dependencies {
    ksp("androidx.room:room-compiler")
}
```

**Оптимизация времени сборки:**
- Используйте KSP вместо kapt
- Изолируйте процессоры в отдельных модулях
- Включайте инкрементальную компиляцию
- Отслеживайте время через `./gradlew --profile`

**Отладка проблем:**
```kotlin
// Включение подробного лога KSP
ksp {
    arg("verbose", "true")
}

// Путь к сгенерированному коду
build/generated/ksp/debug/kotlin/
```

## Answer (EN)

**Annotation processing** is a compile-time code generation mechanism where processors analyze annotations in source code and automatically generate helper classes. Used by libraries like Room, Hilt, and Moshi to generate boilerplate code.

### How Annotation Processing Works

```text
Source code with annotations
    ↓
Compiler runs processors
    ↓
Processors generate new classes
    ↓
All code compiled together
    ↓
APK/AAR
```

### Two Main Processors

**kapt (Kotlin Annotation Processing Tool)**
- Bridge between Java processors and Kotlin code
- Generates Java stubs (slow)
- Legacy approach

**KSP (Kotlin Symbol Processing)**
- Native Kotlin support
- 2x faster than kapt
- No stub generation required
- Recommended for new projects

### Usage Examples

**❌ Old approach with kapt:**
```kotlin
// build.gradle.kts
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0")
}
```

**✅ Modern approach with KSP:**
```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    ksp("androidx.room:room-compiler:2.6.0")
}
```

### Room with Annotation Processing

```kotlin
// Define Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String
)

// Define DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: Long): User?
}

// Processor generates:
// - UserDao_Impl (DAO implementation)
// - User_Table (table schema)
// - AppDatabase_Impl (database implementation)
```

### Hilt with Annotation Processing

```kotlin
@HiltAndroidApp
class App : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity()

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repo: UserRepository
) : ViewModel()

// ✅ Hilt generates all DI components automatically
```

### Moshi with Annotation Processing

```kotlin
@JsonClass(generateAdapter = true)
data class ApiResponse(
    @Json(name = "user_id") val userId: Long,
    val name: String
)

// ✅ Generates optimized ApiResponseJsonAdapter
```

### Comparison: kapt vs KSP

| Aspect | kapt | KSP |
|--------|------|-----|
| Speed | Baseline | 2x faster |
| API Language | Java | Kotlin |
| Stubs | Generates | Not required |
| Incremental compilation | Limited | Full |
| Future | Deprecated | Actively developed |

**Real-world numbers:**
```text
Project: Room + Hilt + 50 modules
kapt:  ~45 seconds
KSP:   ~23 seconds (48% faster)
```

### Best Practices

**Migrating to KSP:**
```kotlin
// ❌ Old
plugins {
    id("kotlin-kapt")
}
dependencies {
    kapt("androidx.room:room-compiler")
}

// ✅ New
plugins {
    id("com.google.devtools.ksp")
}
dependencies {
    ksp("androidx.room:room-compiler")
}
```

**Build time optimization:**
- Use KSP instead of kapt
- Isolate processors in separate modules
- Enable incremental compilation
- Monitor build time with `./gradlew --profile`

**Debugging issues:**
```kotlin
// Enable verbose KSP logging
ksp {
    arg("verbose", "true")
}

// Path to generated code
build/generated/ksp/debug/kotlin/
```

---

## Follow-ups

- How do you write a custom KSP processor for your own annotations?
- What's the difference between SOURCE, BINARY, and RUNTIME retention policies?
- How does annotation processing affect incremental compilation?
- What are the debugging strategies when generated code doesn't compile?
- Can you use multiple annotation processors in the same module?

## References

- [[c-room]] - Database ORM using annotation processing
- [[c-hilt]] - Dependency injection with code generation
- [KSP Official Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [Migrating from kapt to KSP](https://developer.android.com/build/migrate-to-ksp)

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]] - Android project structure basics
- [[q-gradle-basics--android--easy]] - Gradle fundamentals

### Related (Same Level)
- [[q-android-build-optimization--android--medium]] - Build performance optimization
- [[q-android-modularization--android--medium]] - Module architecture
- [[q-room-library-definition--android--easy]] - Room ORM basics

### Advanced (Harder)
- [[q-custom-annotation-processor--android--hard]] - Writing custom processors
- [[q-gradle-build-lifecycle--android--hard]] - Gradle build phases