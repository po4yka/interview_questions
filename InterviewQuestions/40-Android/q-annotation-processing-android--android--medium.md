---
id: 20251006-100012
title: "What is annotation processing in Android? / Что такое annotation processing в Android?"
aliases: []

# Classification
topic: android
subtopics: [annotations, kapt, ksp, code-generation]
question_kind: explanation
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/annotations, android/kapt, android/ksp, android/code-generation, difficulty/medium]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [q-testing-coroutines-flow--testing--hard, q-test-coverage-quality-metrics--testing--medium, q-shared-preferences--android--easy]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [en, ru, android/annotations, android/kapt, android/ksp, android/code-generation, difficulty/medium]
---
# Question (EN)
> What is annotation processing in Android?
# Вопрос (RU)
> Что такое annotation processing в Android?

---

## Answer (EN)

**Annotation processing** is a compile-time code generation technique that reads annotations in source code and generates new code based on them. This reduces boilerplate, improves type safety, and enables powerful frameworks like Room, Dagger, and Retrofit.

### How Annotation Processing Works

```
Source Code with Annotations
         ↓
Annotation Processor (compile-time)
         ↓
Generated Code
         ↓
Final Compiled App
```

### Key Technologies

**1. KAPT (Kotlin Annotation Processing Tool)** - Java annotation processing for Kotlin
**2. KSP (Kotlin Symbol Processing)** - Modern, faster alternative to KAPT
**3. APT (Annotation Processing Tool)** - Java annotation processing

### Example: Creating a Simple Annotation Processor

#### Step 1: Define Annotation

```kotlin
// annotations/src/main/java/com/example/annotations/AutoToString.kt
@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.SOURCE)
annotation class AutoToString
```

#### Step 2: Use Annotation

```kotlin
// app/src/main/java/com/example/User.kt
@AutoToString
data class User(
    val id: String,
    val name: String,
    val email: String
)
```

#### Step 3: Processor Generates Code

```kotlin
// Generated code (build/generated/source/kapt)
fun User.toDetailedString(): String {
    return """
        User {
            id=$id,
            name=$name,
            email=$email
        }
    """.trimIndent()
}

// Usage
val user = User("1", "Alice", "alice@example.com")
println(user.toDetailedString())
// Output:
// User {
//     id=1,
//     name=Alice,
//     email=alice@example.com
// }
```

### Real-World Example: Room Database

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
// 1. UserDao_Impl.kt - DAO implementation
// 2. User_Table.kt - Table creation SQL
// 3. Database schema files

// Generated UserDao_Impl (simplified)
class UserDao_Impl(private val db: RoomDatabase) : UserDao {
    override suspend fun getUserById(userId: String): User? {
        val sql = "SELECT * FROM users WHERE id = ?"
        val statement = db.compileStatement(sql)
        statement.bindString(1, userId)
        // ... cursor handling
        return user
    }

    override suspend fun insertUser(user: User) {
        val sql = "INSERT INTO users (id, user_name, email) VALUES (?, ?, ?)"
        val statement = db.compileStatement(sql)
        statement.bindString(1, user.id)
        statement.bindString(2, user.name)
        statement.bindString(3, user.email)
        statement.executeInsert()
    }
}
```

### KAPT vs KSP Comparison

#### KAPT (Kotlin Annotation Processing Tool)

```kotlin
// build.gradle.kts
plugins {
    id("kotlin-kapt")
}
```

**Pros:**
- Works with all Java annotation processors
- Mature, stable
- Wide library support

**Cons:**
- Slow (converts Kotlin to Java stubs first)
- Increases build time significantly
- Higher memory usage

#### KSP (Kotlin Symbol Processing)

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "2.1.0-1.0.29"
}
```

**Pros:**
- **2x faster** than KAPT
- Native Kotlin support
- Lower memory usage
- Better error messages

**Cons:**
- Limited library support (growing)
- Relatively newer

**Performance Comparison:**

| Task | KAPT | KSP | Improvement |
|------|------|-----|-------------|
| Clean build | 60s | 30s | 2x faster |
| Incremental build | 15s | 5s | 3x faster |
| Memory usage | 2GB | 1GB | 50% less |

### Popular Libraries Using Annotation Processing

#### 1. Room (Database)

```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// Room generates:
// - AppDatabase_Impl.kt (database implementation)
// - UserDao_Impl.kt (DAO implementation)
// - Migration helpers
```

#### 2. Dagger/Hilt (Dependency Injection)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder().build()
    }
}

// Dagger generates:
// - DaggerAppComponent.java (dependency graph)
// - NetworkModule_ProvideOkHttpClientFactory.java (provider factories)
// - Dependency injection code
```

#### 3. Retrofit (Networking)

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

// Retrofit generates:
// - ApiService implementation with HTTP call code
// - Request/response converters
```

#### 4. Moshi (JSON)

```kotlin
@JsonClass(generateAdapter = true)
data class User(
    val id: String,
    @Json(name = "user_name") val name: String,
    val email: String
)

// Moshi generates:
// - UserJsonAdapter.kt (optimized JSON adapter)
```

### Creating Custom Annotation Processor with KAPT

#### Step 1: Create Annotation Module

```kotlin
// annotations/build.gradle.kts
plugins {
    id("java-library")
    id("org.jetbrains.kotlin.jvm")
}

// annotations/src/main/java/com/example/BindView.kt
@Target(AnnotationTarget.FIELD)
@Retention(AnnotationRetention.SOURCE)
annotation class BindView(val id: Int)
```

#### Step 2: Create Processor Module

```kotlin
// processor/build.gradle.kts
plugins {
    id("java-library")
    id("org.jetbrains.kotlin.jvm")
}

// processor/src/main/java/com/example/BindViewProcessor.kt
@AutoService(Processor::class)
@SupportedSourceVersion(SourceVersion.RELEASE_8)
@SupportedAnnotationTypes("com.example.BindView")
class BindViewProcessor : AbstractProcessor() {

    override fun process(
        annotations: Set<TypeElement>,
        roundEnv: RoundEnvironment
    ): Boolean {
        val bindViewElements = roundEnv.getElementsAnnotatedWith(BindView::class.java)

        bindViewElements.groupBy { it.enclosingElement }
            .forEach { (classElement, fields) ->
                generateBindingClass(classElement, fields)
            }

        return true
    }

    private fun generateBindingClass(
        classElement: Element,
        fields: List<Element>
    ) {
        val className = classElement.simpleName.toString()
        val packageName = processingEnv.elementUtils.getPackageOf(classElement).toString()

        val fileSpec = FileSpec.builder(packageName, "${className}_ViewBinding")
            .addType(
                TypeSpec.classBuilder("${className}_ViewBinding")
                    .addFunction(createBindFunction(className, fields))
                    .build()
            )
            .build()

        fileSpec.writeTo(processingEnv.filer)
    }

    private fun createBindFunction(
        className: String,
        fields: List<Element>
    ): FunSpec {
        val bindFunction = FunSpec.builder("bind")
            .addParameter("target", ClassName("", className))
            .addParameter("view", ClassName("android.view", "View"))

        fields.forEach { field ->
            val annotation = field.getAnnotation(BindView::class.java)
            val viewId = annotation.id
            val fieldName = field.simpleName

            bindFunction.addStatement(
                "target.%N = view.findViewById(%L)",
                fieldName,
                viewId
            )
        }

        return bindFunction.build()
    }
}
```

#### Step 3: Use in App

```kotlin
// app/build.gradle.kts
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation(project(":annotations"))
    kapt(project(":processor"))
}

// app/src/main/java/com/example/MainActivity.kt
class MainActivity : AppCompatActivity() {

    @BindView(R.id.textView)
    lateinit var textView: TextView

    @BindView(R.id.button)
    lateinit var button: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Generated code:
        MainActivity_ViewBinding.bind(this, findViewById(android.R.id.content))

        textView.text = "Hello"
        button.setOnClickListener { /* ... */ }
    }
}

// Generated MainActivity_ViewBinding.kt:
class MainActivity_ViewBinding {
    companion object {
        fun bind(target: MainActivity, view: View) {
            target.textView = view.findViewById(2131296789) // R.id.textView
            target.button = view.findViewById(2131296788)   // R.id.button
        }
    }
}
```

### Creating Custom Annotation Processor with KSP

```kotlin
// processor/build.gradle.kts
plugins {
    id("java-library")
    id("org.jetbrains.kotlin.jvm")
}

// processor/src/main/kotlin/com/example/BindViewProcessorProvider.kt
class BindViewProcessorProvider : SymbolProcessorProvider {
    override fun create(environment: SymbolProcessorEnvironment): SymbolProcessor {
        return BindViewProcessor(environment.codeGenerator, environment.logger)
    }
}

// processor/src/main/kotlin/com/example/BindViewProcessor.kt
class BindViewProcessor(
    private val codeGenerator: CodeGenerator,
    private val logger: KSPLogger
) : SymbolProcessor {

    override fun process(resolver: Resolver): List<KSAnnotated> {
        val symbols = resolver.getSymbolsWithAnnotation(BindView::class.qualifiedName!!)

        symbols
            .filterIsInstance<KSPropertyDeclaration>()
            .groupBy { it.parentDeclaration as KSClassDeclaration }
            .forEach { (classDeclaration, properties) ->
                generateBindingClass(classDeclaration, properties)
            }

        return emptyList()
    }

    private fun generateBindingClass(
        classDeclaration: KSClassDeclaration,
        properties: List<KSPropertyDeclaration>
    ) {
        val className = classDeclaration.simpleName.asString()
        val packageName = classDeclaration.packageName.asString()

        val fileSpec = FileSpec.builder(packageName, "${className}_ViewBinding")
            .addType(
                TypeSpec.objectBuilder("${className}_ViewBinding")
                    .addFunction(createBindFunction(className, properties))
                    .build()
            )
            .build()

        val file = codeGenerator.createNewFile(
            Dependencies(false, classDeclaration.containingFile!!),
            packageName,
            "${className}_ViewBinding"
        )

        file.writer().use { fileSpec.writeTo(it) }
    }

    private fun createBindFunction(
        className: String,
        properties: List<KSPropertyDeclaration>
    ): FunSpec {
        val bindFunction = FunSpec.builder("bind")
            .addParameter("target", ClassName("", className))
            .addParameter("view", ClassName("android.view", "View"))

        properties.forEach { property ->
            val annotation = property.annotations
                .first { it.shortName.asString() == "BindView" }
            val viewId = annotation.arguments
                .first { it.name?.asString() == "id" }
                .value as Int
            val fieldName = property.simpleName.asString()

            bindFunction.addStatement(
                "target.%N = view.findViewById(%L)",
                fieldName,
                viewId
            )
        }

        return bindFunction.build()
    }
}
```

### Build Configuration Optimization

```kotlin
// build.gradle.kts (app module)
kapt {
    // Generate stubs for better IDE support
    correctErrorTypes = true

    // Use worker API for parallel processing
    useBuildCache = true

    // Show annotation processor stats
    arguments {
        arg("verbose", "true")
    }
}

// For KSP
ksp {
    // Pass arguments to processors
    arg("option1", "value1")
    arg("option2", "value2")
}
```

### Common Use Cases

**1. Reducing Boilerplate**
```kotlin
// Without annotation processing
class UserViewModel(
    private val repository: UserRepository,
    private val analytics: Analytics,
    private val prefs: SharedPreferences
) : ViewModel()

// Constructor has to be written manually

// With Hilt
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val analytics: Analytics,
    private val prefs: SharedPreferences
) : ViewModel()

// Hilt generates factory and injection code automatically
```

**2. Type-Safe Navigation**
```kotlin
// Manual navigation (error-prone)
fun navigate() {
    val bundle = Bundle().apply {
        putString("userId", "123")
        putInt("page", 1)
    }
    findNavController().navigate(R.id.detailsFragment, bundle)
}

// With Safe Args (annotation processing)
fun navigate() {
    val action = HomeFragmentDirections.actionHomeToDetails(
        userId = "123",
        page = 1
    )
    findNavController().navigate(action)
}

// Compile-time safety, autocomplete, refactoring support
```

**3. JSON Serialization**
```kotlin
// Manual parsing (error-prone)
fun parseUser(json: String): User {
    val jsonObject = JSONObject(json)
    return User(
        id = jsonObject.getString("id"),
        name = jsonObject.getString("user_name"),
        email = jsonObject.getString("email")
    )
}

// With Moshi (annotation processing)
@JsonClass(generateAdapter = true)
data class User(
    val id: String,
    @Json(name = "user_name") val name: String,
    val email: String
)

val moshi = Moshi.Builder().build()
val adapter = moshi.adapter(User::class.java)
val user = adapter.fromJson(json) // Type-safe, null-safe, fast
```

### Migration from KAPT to KSP

```kotlin
// Before (KAPT)
plugins {
    id("kotlin-kapt")
}

// After (KSP)
plugins {
    id("com.google.devtools.ksp") version "2.1.0-1.0.29"
}

// Update imports in code
// KAPT: import generated files from build/generated/source/kapt
// KSP: import generated files from build/generated/ksp
```

### Best Practices

1. **Prefer KSP over KAPT** for new projects (faster builds)
2. **Enable incremental processing** to speed up builds
3. **Use `correctErrorTypes = true`** for better error messages
4. **Cache annotation processing outputs** for faster rebuilds
5. **Monitor build times** to identify slow processors

### Summary

**Annotation Processing:**
- Generates code at compile-time based on annotations
- Reduces boilerplate and improves type safety
- Powers Room, Dagger, Retrofit, Moshi, etc.

**KAPT:**
- Mature, works with all Java processors
- Slow (converts Kotlin to Java stubs)

**KSP:**
- Modern, 2x faster than KAPT
- Native Kotlin support
- Growing library support

**Benefits:**
- Compile-time code generation
- Type safety
- Less boilerplate
- Better performance than reflection

## Ответ (RU)

**Annotation processing** - это техника генерации кода во время компиляции, которая читает аннотации в исходном коде и генерирует новый код на их основе. Это уменьшает шаблонный код, улучшает типобезопасность и обеспечивает работу мощных фреймворков как Room, Dagger и Retrofit.

### Как работает annotation processing

```
Исходный код с аннотациями
         ↓
Annotation Processor (время компиляции)
         ↓
Сгенерированный код
         ↓
Финальное скомпилированное приложение
```

### Ключевые технологии

**1. KAPT (Kotlin Annotation Processing Tool)** - обработка Java-аннотаций для Kotlin
**2. KSP (Kotlin Symbol Processing)** - современная, более быстрая альтернатива KAPT
**3. APT (Annotation Processing Tool)** - обработка Java-аннотаций

### Пример: Room Database

```kotlin
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
}

// Room генерирует:
// - UserDao_Impl.kt - реализацию DAO
// - User_Table.kt - SQL создания таблицы
// - Файлы схемы базы данных
```

### KAPT vs KSP

**KAPT:**
- Зрелый, стабильный
- Работает со всеми Java-процессорами
- Медленный (конвертирует Kotlin в Java-заглушки)

**KSP:**
- **В 2 раза быстрее** KAPT
- Нативная поддержка Kotlin
- Меньше использует память
- Лучшие сообщения об ошибках

**Сравнение производительности:**

| Задача | KAPT | KSP | Улучшение |
|--------|------|-----|-----------|
| Чистая сборка | 60с | 30с | 2x быстрее |
| Инкрементальная сборка | 15с | 5с | 3x быстрее |
| Использование памяти | 2ГБ | 1ГБ | На 50% меньше |

### Популярные библиотеки

**Room** - база данных
**Dagger/Hilt** - внедрение зависимостей
**Retrofit** - сетевые запросы
**Moshi** - JSON сериализация

### Типичные случаи использования

**1. Уменьшение шаблонного кода**
```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()

// Hilt автоматически генерирует фабрику и код инъекции
```

**2. Типобезопасная навигация**
```kotlin
val action = HomeFragmentDirections.actionHomeToDetails(userId = "123")
findNavController().navigate(action)

// Безопасность на этапе компиляции, автодополнение, поддержка рефакторинга
```

**3. JSON сериализация**
```kotlin
@JsonClass(generateAdapter = true)
data class User(val id: String, val name: String)

// Moshi генерирует оптимизированный адаптер
```

### Резюме

**Преимущества:**
- Генерация кода во время компиляции
- Типобезопасность
- Меньше шаблонного кода
- Лучшая производительность чем рефлексия

**KSP vs KAPT:**
- KSP в 2 раза быстрее
- KSP имеет нативную поддержку Kotlin
- Для новых проектов рекомендуется KSP

---

## Related Questions

### Related (Medium)
- [[q-annotation-processing--android--medium]] - Annotation Processing
- [[q-kapt-vs-ksp--android--medium]] - Annotation Processing
- [[q-kapt-ksp-migration--gradle--medium]] - Kapt

## References
- [KSP Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [KAPT Documentation](https://kotlinlang.org/docs/kapt.html)
- [Room Annotation Processing](https://developer.android.com/training/data-storage/room)
