---
id: 20251012-140600
title: Annotation Processing in Android / Обработка аннотаций в Android
aliases: [Annotation Processing in Android, Обработка аннотаций в Android]
topic: android
subtopics:
  - gradle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-build-optimization--android--medium
  - q-android-modularization--android--medium
  - q-android-project-parts--android--easy
created: 2025-10-12
updated: 2025-10-28
tags: [android/gradle, difficulty/medium]
---
# Вопрос (RU)
> Что такое Обработка аннотаций в Android?

---

# Question (EN)
> What is Annotation Processing in Android?

---

## Ответ (RU)

**Обработка аннотаций** — это техника генерации кода на этапе компиляции, при которой процессоры анализируют аннотации и автоматически создают дополнительные классы, уменьшая boilerplate-код и обеспечивая мощные фреймворки.

**Теория обработки аннотаций:**
Обработка аннотаций происходит во время компиляции, когда процессоры анализируют аннотации в исходном коде и генерируют дополнительный код. Это позволяет фреймворкам, таким как [[c-room]], [[c-hilt]], и Moshi, автоматически создавать реализации без boilerplate-кода.

**Как работает обработка аннотаций:**

```text
Исходный код (.kt/.java)
    ↓
Компилятор читает аннотации
    ↓
Выполняются процессоры аннотаций
    ↓
Генерируется код (.kt/.java)
    ↓
Весь код компилируется вместе
    ↓
APK/AAR
```

**1. Базовый пример:**

```kotlin
// Определяем аннотацию
@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.SOURCE)
annotation class AutoViewModel

// Аннотируем класс
@AutoViewModel
class UserRepository(private val api: UserApi)

// Процессор генерирует код
class UserRepositoryFactory {
    fun create(api: UserApi): UserRepository {
        return UserRepository(api)
    }
}
```

**2. kapt (Kotlin Annotation Processing Tool):**
Связывает Java-процессоры аннотаций с Kotlin-кодом через генерацию Java-заглушек.

```kotlin
// build.gradle.kts
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime")
    kapt("androidx.room:room-compiler") // ✅ Используется kapt для процессора
}

// Пример Room
@Entity(tableName = "users")
data class User(@PrimaryKey val id: String, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>
}

// kapt генерирует: UserDao_Impl, User_Table и др.
```

**3. KSP (Kotlin Symbol Processing):**
Kotlin-ориентированная обработка аннотаций, в 2 раза быстрее kapt.

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("androidx.room:room-runtime")
    ksp("androidx.room:room-compiler") // ✅ Используется KSP вместо kapt
}

// Тот же код Room работает с KSP
// Генерирует тот же вывод, но быстрее
```

**4. Популярные библиотеки с обработкой аннотаций:**

**Room (Database ORM):**
```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
// Генерирует: AppDatabase_Impl, User_Table, UserDao_Impl
```

**Hilt/Dagger (Dependency Injection):**
```kotlin
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity()

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
// ✅ Генерирует компоненты DI автоматически
```

**Moshi (JSON Parsing):**
```kotlin
@JsonClass(generateAdapter = true)
data class User(
    @Json(name = "user_id") val id: String,
    val name: String
)
// Генерирует оптимизированный UserJsonAdapter
```

**Сравнение kapt vs KSP:**

| Характеристика | kapt | KSP |
|----------------|------|-----|
| **Скорость** | Базовая | В 2 раза быстрее |
| **Язык** | На основе Java | Kotlin-ориентированная |
| **API** | Java Annotation Processing | Kotlin Symbol Processing |
| **Генерация заглушек** | Да (медленно) | Нет (быстро) |
| **Поддержка Kotlin** | Ограниченная | Полная |

**Пример времени сборки:**
```text
Проект с Room + Hilt:
kapt:  45 секунд
KSP:   23 секунды  (на 48% быстрее)
```

**Лучшие практики:**
- Используйте KSP вместо kapt для новых проектов (в 2 раза быстрее)
- Изолируйте процессоры в отдельных Gradle-модулях
- Правильно объявляйте зависимости для инкрементальной компиляции
- Тестируйте сгенерированный код как обычный код
- Документируйте аннотации для разработчиков
- Сопоставляйте версии процессоров и аннотаций
- Отслеживайте время сборки с помощью `--profile`

## Answer (EN)

**Annotation Processing** is a compile-time code generation technique where processors analyze annotations and automatically generate additional classes, reducing boilerplate and enabling powerful frameworks.

**Annotation Processing Theory:**
Annotation processing occurs during compilation when processors analyze source code annotations and generate additional code. This enables frameworks like [[c-room]], [[c-hilt]], and Moshi to create boilerplate-free implementations automatically.

**How Annotation Processing Works:**

```text
Source Code (.kt/.java)
    ↓
Compiler reads annotations
    ↓
Annotation Processors execute
    ↓
Generated Code (.kt/.java)
    ↓
All code compiled together
    ↓
APK/AAR
```

**1. Basic Example:**

```kotlin
// Define annotation
@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.SOURCE)
annotation class AutoViewModel

// Annotate class
@AutoViewModel
class UserRepository(private val api: UserApi)

// Processor generates code
class UserRepositoryFactory {
    fun create(api: UserApi): UserRepository {
        return UserRepository(api)
    }
}
```

**2. kapt (Kotlin Annotation Processing Tool):**
Bridges Java annotation processors with Kotlin code by generating Java stubs.

```kotlin
// build.gradle.kts
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime")
    kapt("androidx.room:room-compiler") // ✅ Uses kapt for processor
}

// Room example
@Entity(tableName = "users")
data class User(@PrimaryKey val id: String, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>
}

// kapt generates: UserDao_Impl, User_Table, etc.
```

**3. KSP (Kotlin Symbol Processing):**
Kotlin-first annotation processing, 2x faster than kapt.

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("androidx.room:room-runtime")
    ksp("androidx.room:room-compiler") // ✅ Uses KSP instead of kapt
}

// Same Room code works with KSP
// Generates same output but faster
```

**4. Popular Libraries Using Annotation Processing:**

**Room (Database ORM):**
```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
// Generates: AppDatabase_Impl, User_Table, UserDao_Impl
```

**Hilt/Dagger (Dependency Injection):**
```kotlin
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity()

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
// ✅ Generates DI components automatically
```

**Moshi (JSON Parsing):**
```kotlin
@JsonClass(generateAdapter = true)
data class User(
    @Json(name = "user_id") val id: String,
    val name: String
)
// Generates optimized UserJsonAdapter
```

**kapt vs KSP Comparison:**

| Feature | kapt | KSP |
|---------|------|-----|
| **Speed** | Baseline | 2x faster |
| **Language** | Java-based | Kotlin-first |
| **API** | Java Annotation Processing | Kotlin Symbol Processing |
| **Stub Generation** | Yes (slow) | No (fast) |
| **Kotlin Support** | Limited | Full |

**Build Time Example:**
```text
Project with Room + Hilt:
kapt:  45 seconds
KSP:   23 seconds  (48% faster)
```

**Best Practices:**
- Use KSP instead of kapt for new projects (2x faster)
- Isolate processors in separate Gradle modules
- Declare dependencies correctly for incremental compilation
- Test generated code like regular code
- Document annotations for developers
- Match processor and annotation versions
- Monitor build times with `--profile`

---

## Follow-ups

- How do you debug annotation processing errors when generated code fails to compile?
- What's the difference between `SOURCE`, `BINARY`, and `RUNTIME` retention policies?
- How do you migrate an existing project from kapt to KSP?
- What are the performance trade-offs between compile-time and runtime code generation?
- How do you write a custom annotation processor with KSP?

## References

- [[c-room]] - ORM using annotation processing
- [[c-hilt]] - DI framework using annotation processing
- [[c-gradle]] - Build system integration
- [KSP Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [kapt Documentation](https://kotlinlang.org/docs/kapt.html)

## Related Questions

### Prerequisites
- [[q-android-project-parts--android--easy]] - Understanding Android project structure
- [[q-gradle-basics--android--easy]] - Gradle fundamentals

### Related
- [[q-android-build-optimization--android--medium]] - Optimizing build performance
- [[q-android-modularization--android--medium]] - Module structure for processors
- [[q-room-library-definition--android--easy]] - Room ORM basics
- [[q-gradle-build-system--android--medium]] - Gradle build system

### Advanced
- [[q-android-runtime-internals--android--hard]] - Runtime vs compile-time processing
- [[q-room-code-generation-timing--android--medium]] - Code generation timing