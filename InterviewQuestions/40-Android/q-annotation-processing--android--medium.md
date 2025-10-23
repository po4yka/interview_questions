---
id: 20251012-140600
title: Annotation Processing in Android / Обработка аннотаций в Android
aliases:
- Annotation Processing in Android
- Обработка аннотаций в Android
topic: android
subtopics:
- annotation-processing
- kapt
- ksp
- codegen
- build-tools
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-build-optimization--android--medium
- q-android-modularization--android--medium
- q-android-project-parts--android--easy
created: 2025-10-12
updated: 2025-10-15
tags:
- android/annotation-processing
- android/kapt
- android/ksp
- android/codegen
- android/build-tools
- annotation-processing
- kapt
- ksp
- codegen
- build-tools
- difficulty/medium
---# Вопрос (RU)
> Что такое обработка аннотаций в Android? Как это работает, какие основные инструменты (kapt, KSP) и какие популярные библиотеки используют это?

---

# Question (EN)
> What is annotation processing in Android? How does it work, what are the main tools (kapt, KSP), and what popular libraries use it?

## Ответ (RU)

**Обработка аннотаций** — это техника генерации кода во время компиляции, когда процессоры анализируют аннотации и автоматически генерируют дополнительные классы, уменьшая шаблонный код и обеспечивая мощные фреймворки.

**Теория обработки аннотаций:**
Обработка аннотаций происходит во время компиляции, когда процессоры анализируют аннотации исходного кода и генерируют дополнительный код. Это позволяет фреймворкам как Room, Hilt и Moshi автоматически создавать реализации без шаблонного кода.

**Как работает обработка аннотаций:**

```
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
// Определить аннотацию
@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.SOURCE)
annotation class AutoViewModel

// Аннотировать класс
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
Связывает Java процессоры аннотаций с Kotlin кодом через генерацию Java stubs.

```kotlin
// build.gradle.kts
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime")
    kapt("androidx.room:room-compiler")
}

// Пример Room
@Entity(tableName = "users")
data class User(@PrimaryKey val id: String, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>
}

// kapt генерирует UserDao_Impl, User_Table и т.д.
```

**3. KSP (Kotlin Symbol Processing):**
Обработка аннотаций, ориентированная на Kotlin, в 2 раза быстрее kapt.

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    implementation("androidx.room:room-runtime")
    ksp("androidx.room:room-compiler")
}

// Тот же код Room работает с KSP
// Генерирует тот же результат, но быстрее
```

**4. Популярные библиотеки использующие обработку аннотаций:**

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
// Генерирует компоненты DI
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

| Функция | kapt | KSP |
|---------|------|-----|
| **Скорость** | Базовая | В 2 раза быстрее |
| **Язык** | На основе Java | Ориентирован на Kotlin |
| **API** | Java Annotation Processing | Kotlin Symbol Processing |
| **Генерация stubs** | Да (медленно) | Нет (быстро) |
| **Поддержка Kotlin** | Ограниченная | Полная |

**Пример времени сборки:**
```
Проект с Room + Hilt:
kapt:  45 секунд
KSP:   23 секунды  (на 48% быстрее)
```

**Лучшие практики:**
- Используйте KSP вместо kapt для новых проектов (в 2 раза быстрее)
- Изолируйте процессоры в отдельных Gradle модулях
- Правильно объявляйте зависимости для инкрементальной компиляции
- Тестируйте сгенерированный код как обычный код
- Документируйте аннотации для разработчиков
- Совпадайте версии процессора и аннотаций
- Мониторьте время сборки с `--profile`

---

## Answer (EN)

**Annotation Processing** is a compile-time code generation technique where processors analyze annotations and automatically generate additional classes, reducing boilerplate and enabling powerful frameworks.

**Annotation Processing Theory:**
Annotation processing occurs during compilation when processors analyze source code annotations and generate additional code. This enables frameworks like Room, Hilt, and Moshi to create boilerplate-free implementations automatically.

**How Annotation Processing Works:**

```
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
    kapt("androidx.room:room-compiler")
}

// Room example
@Entity(tableName = "users")
data class User(@PrimaryKey val id: String, val name: String)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>
}

// kapt generates UserDao_Impl, User_Table, etc.
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
    ksp("androidx.room:room-compiler")
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
// Generates DI components
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
```
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

## Follow-ups

- How do you debug annotation processing issues?
- What's the difference between compile-time and runtime code generation?
- How do you migrate from kapt to KSP?
- What are the performance implications of annotation processing?

## References

- [[c-annotation-processing]]
- [KSP Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [kapt Documentation](https://kotlinlang.org/docs/kapt.html)

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]]
- [[q-android-app-components--android--easy]]

### Related (Same Level)
- [[q-android-build-optimization--android--medium]]
- [[q-android-modularization--android--medium]]
- [[q-android-testing-strategies--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]

