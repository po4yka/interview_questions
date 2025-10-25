---
id: 20251006-100012
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
created: 2025-10-06
updated: 2025-10-15
tags:
- android/gradle
- difficulty/medium
---

# Вопрос (RU)
> Что такое Обработка аннотаций в Android?

---

# Question (EN)
> What is Annotation Processing in Android?

## Answer (EN)
**Annotation Processing** is a compile-time code generation technique that reads annotations in source code and generates new code based on them, reducing boilerplate and enabling powerful frameworks.

**Annotation Processing Theory:**
Annotation processing occurs during compilation when processors analyze source code annotations and generate additional code. This enables frameworks like [[c-room]], [[c-hilt]], and Retrofit to create boilerplate-free implementations automatically.

**How Annotation Processing Works:**

```
Source Code with Annotations
         ↓
Annotation Processor (compile-time)
         ↓
Generated Code
         ↓
Final Compiled App
```

**1. Basic Example:**

```kotlin
// Define annotation
@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.SOURCE)
annotation class AutoToString

// Use annotation
@AutoToString
data class User(val id: String, val name: String, val email: String)

// Processor generates code
fun User.toDetailedString(): String {
    return """
        User {
            id=$id,
            name=$name,
            email=$email
        }
    """.trimIndent()
}
```

**2. Room Database Example:**

```kotlin
// User defines annotation
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "user_name") val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: String): User?

    @Insert
    suspend fun insertUser(user: User)
}

// Room annotation processor generates:
// UserDao_Impl.kt - DAO implementation
// User_Table.kt - Table creation SQL
// Database schema files
```

**3. KAPT vs KSP Comparison:**

**KAPT (Kotlin Annotation Processing Tool):**
```kotlin
// build.gradle.kts
plugins {
    id("kotlin-kapt")
}
```

**KSP (Kotlin Symbol Processing):**
```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp")
}
```

**Performance Comparison:**

| Feature | KAPT | KSP | Improvement |
|---------|------|-----|-------------|
| **Speed** | Baseline | 2x faster | 2x faster |
| **Memory** | High | Low | 50% less |
| **Kotlin Support** | Limited | Native | Full support |
| **Library Support** | Wide | Growing | Expanding |

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
data class User(val id: String, val name: String)
// Generates optimized UserJsonAdapter
```

**Key Benefits:**
- Compile-time code generation
- Type safety
- Reduced boilerplate code
- Better performance than reflection
- Framework enablement

**Best Practices:**
- Use KSP instead of KAPT for new projects (2x faster)
- Isolate processors in separate Gradle modules
- Declare dependencies correctly for incremental compilation
- Test generated code like regular code
- Document annotations for developers

## Follow-ups

- How do you debug annotation processing issues?
- What's the difference between compile-time and runtime code generation?
- How do you migrate from KAPT to KSP?
- What are the performance implications of annotation processing?

## References

- [KSP Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [KAPT Documentation](https://kotlinlang.org/docs/kapt.html)

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