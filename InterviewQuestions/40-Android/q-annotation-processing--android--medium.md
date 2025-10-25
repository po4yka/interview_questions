---
id: 20251012-140600
title: Annotation Processing in Android / Обработка аннотаций в Android
aliases:
- Annotation Processing in Android
- Обработка аннотаций в Android
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
updated: 2025-10-15
tags:
- android/gradle
- difficulty/medium
kapt: 45 секунд
---

# Вопрос (RU)
> Что такое Обработка аннотаций в Android?

---

# Question (EN)
> What is Annotation Processing in Android?

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

- c-annotation-processing
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