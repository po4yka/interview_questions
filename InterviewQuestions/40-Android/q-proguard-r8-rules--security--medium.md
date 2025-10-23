---
id: 20251012-12271173
title: "Proguard R8 Rules / Правила ProGuard и R8"
topic: security
difficulty: medium
status: draft
moc: moc-android
related: [q-kotlin-context-receivers--kotlin--hard, q-lazy-grid-staggered-grid--jetpack-compose--medium, q-is-layoutinflater-a-singleton-and-why--programming-languages--medium]
created: 2025-10-15
tags: [proguard, r8, obfuscation, optimization, library, difficulty/medium]
---
# ProGuard/R8 Rules / Правила ProGuard/R8

**English**: Write comprehensive ProGuard/R8 rules for an Android library. Handle reflection, serialization, native methods, and APIs. Optimize for production while maintaining functionality.

## Answer (EN)
**ProGuard** and **R8** are code shrinkers, optimizers, and obfuscators for Android apps. R8 is the modern replacement for ProGuard, offering better performance and more aggressive optimization while maintaining full ProGuard compatibility.

### Key Concepts

#### ProGuard/R8 Capabilities

1. **Code Shrinking**: Remove unused classes, methods, and fields
2. **Optimization**: Inline methods, remove unused parameters
3. **Obfuscation**: Rename classes/methods to short names (a, b, c)
4. **Resource Shrinking**: Remove unused resources (with build config)

#### How R8 Works

```
Source Code → R8 → Optimized/Obfuscated Code
                ↓
           mapping.txt (for crash deobfuscation)
```

### Complete ProGuard Rules File

#### 1. Basic Configuration

```proguard
# proguard-rules.pro - Comprehensive configuration

###########################################
# BASIC CONFIGURATION
###########################################

# Keep line numbers for crash reports
-keepattributes SourceFile,LineNumberTable

# Rename source file to "SourceFile" for obfuscation
-renamesourcefileattribute SourceFile

# Keep generic signatures for Kotlin reflection
-keepattributes Signature

# Keep annotations for runtime usage
-keepattributes *Annotation*

# Keep inner classes
-keepattributes InnerClasses,EnclosingMethod

# Optimization settings
-optimizationpasses 5
-dontpreverify

# Don't warn about missing classes (for optional dependencies)
-dontwarn javax.annotation.**
-dontwarn org.jetbrains.annotations.**

###########################################
# REFLECTION SUPPORT
###########################################

# Keep classes used via reflection
-keep class com.example.api.** { *; }

# Keep all classes with @Keep annotation
-keep @androidx.annotation.Keep class * { *; }

# Keep all methods with @Keep annotation
-keepclassmembers class * {
    @androidx.annotation.Keep *;
}

# Keep Enum classes (commonly accessed via reflection)
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

###########################################
# SERIALIZATION
###########################################

# Gson specific rules
-keepattributes Signature
-keepattributes *Annotation*

# Keep all model classes
-keep class com.example.models.** { *; }

# Gson uses generic type information during reflection
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken

# Keep JsonAdapter classes
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# Application classes that will be serialized/deserialized
-keep class com.example.data.** { <fields>; }

# Moshi specific rules
-keepclasseswithmembers class * {
    @com.squareup.moshi.* <methods>;
}

-keep @com.squareup.moshi.JsonQualifier interface *

-keepclassmembers class kotlin.Metadata {
    public <methods>;
}

# kotlinx.serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt

-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}

-keep,includedescriptorclasses class com.example.**$$serializer { *; }
-keepclassmembers class com.example.** {
    *** Companion;
}
-keepclasseswithmembers class com.example.** {
    kotlinx.serialization.KSerializer serializer(...);
}

###########################################
# NATIVE METHODS (JNI)
###########################################

# Keep native methods
-keepclasseswithmembernames,includedescriptorclasses class * {
    native <methods>;
}

# Keep classes that interact with native code
-keep class com.example.nativelib.NativeBridge {
    public <methods>;
    public <fields>;
}

# Keep callback methods called from native code
-keepclassmembers class com.example.nativelib.** {
    public void on*(...);
    public void callback*(...);
}

###########################################
# LIBRARY PUBLIC API
###########################################

# Keep all public API classes and methods
-keep public class com.example.library.** {
    public protected *;
}

# Keep all public interfaces
-keep public interface com.example.library.** {
    *;
}

# Keep specific API entry points
-keep class com.example.library.LibraryMain {
    public <init>(...);
    public <methods>;
}

# Keep builder classes
-keep class com.example.library.**.Builder {
    public <init>(...);
    public <methods>;
}

# Keep data classes used in public API
-keep class com.example.library.models.** {
    public <fields>;
    public <methods>;
}

###########################################
# ANDROID COMPONENTS
###########################################

# Keep Activities, Services, BroadcastReceivers
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider

# Keep Application class
-keep class * extends android.app.Application {
    public <init>();
}

# Keep custom views
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
    public void set*(...);
}

# Keep onclick methods
-keepclassmembers class * extends android.app.Activity {
    public void *(android.view.View);
}

# Keep Parcelable implementations
-keep class * implements android.os.Parcelable {
    public static final ** CREATOR;
}

-keepclassmembers class * implements android.os.Parcelable {
    public <fields>;
}

###########################################
# KOTLIN SPECIFIC
###########################################

# Keep Kotlin metadata
-keep class kotlin.Metadata { *; }

# Keep Kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}

# Kotlin companion objects
-keepclassmembers class **$Companion {
    public <fields>;
    public <methods>;
}

# Sealed classes
-keep class com.example.**.sealed.** {
    *;
}

###########################################
# THIRD-PARTY LIBRARIES
###########################################

# Retrofit
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepattributes RuntimeVisibleAnnotations, RuntimeVisibleParameterAnnotations
-keepattributes AnnotationDefault

-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

-dontwarn org.codehaus.mojo.animal_sniffer.IgnoreJRERequirement
-dontwarn javax.annotation.**
-dontwarn kotlin.Unit
-dontwarn retrofit2.KotlinExtensions
-dontwarn retrofit2.KotlinExtensions$*

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**
-keepnames class okhttp3.internal.publicsuffix.PublicSuffixDatabase

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-dontwarn androidx.room.paging.**

# Dagger/Hilt
-keep class dagger.** { *; }
-keep class javax.inject.** { *; }
-keep class * extends dagger.internal.Binding
-keep class * extends dagger.internal.ModuleAdapter
-keep class * extends dagger.internal.StaticInjection

###########################################
# DEBUGGING (Remove in production)
###########################################

# Print configuration details
# -printconfiguration proguard-config.txt

# Print mapping for obfuscated names
# -printmapping mapping.txt

# Print removed code
# -printusage unused.txt

# Print kept code
# -printseeds seeds.txt
```

#### 2. Consumer ProGuard Rules (for Library Projects)

```proguard
# consumer-rules.pro
# These rules are automatically applied to consumers of this library

###########################################
# LIBRARY CONSUMER RULES
###########################################

# Keep public API
-keep public class com.example.library.** {
    public protected *;
}

# Keep model classes
-keep class com.example.library.models.** { *; }

# Keep callback interfaces
-keep interface com.example.library.callbacks.** { *; }

# Keep exceptions
-keep class com.example.library.exceptions.** { *; }

# Keep builder pattern
-keep class com.example.library.**.Builder {
    public <init>(...);
    public ** build();
    public ** set*(**);
}

# Keep annotation processors
-keep class * extends java.lang.annotation.Annotation { *; }

###########################################
# REFLECTION USED BY LIBRARY
###########################################

-keepclassmembers class * {
    @com.example.library.annotations.Inject <fields>;
    @com.example.library.annotations.Bind <methods>;
}

###########################################
# SERIALIZATION
###########################################

# If library uses Gson
-keepattributes Signature
-keep class com.example.library.data.** { <fields>; }

# If library uses kotlinx.serialization
-keep,includedescriptorclasses class com.example.library.**$$serializer { *; }
```

### Testing Obfuscated Builds

```kotlin
/**
 * Test suite for verifying ProGuard/R8 rules
 */
class ProguardRulesTest {

    @Test
    fun testPublicApiClassesKept() {
        // Verify public API classes are not obfuscated
        val libraryClass = Class.forName("com.example.library.LibraryMain")
        assertNotNull(libraryClass)

        val method = libraryClass.getMethod("initialize", Context::class.java)
        assertNotNull(method)
        assertEquals("initialize", method.name) // Not obfuscated
    }

    @Test
    fun testSerializationWorks() {
        // Test Gson serialization
        val user = User(id = 1, name = "Test")
        val json = Gson().toJson(user)
        val deserialized = Gson().fromJson(json, User::class.java)

        assertEquals(user.id, deserialized.id)
        assertEquals(user.name, deserialized.name)
    }

    @Test
    fun testReflectionWorks() {
        // Test reflection-based access
        val apiClass = Class.forName("com.example.library.api.ApiClient")
        val instance = apiClass.getDeclaredConstructor().newInstance()

        assertNotNull(instance)
    }

    @Test
    fun testEnumValuesWork() {
        // Enum.valueOf() requires specific ProGuard rules
        val status = UserStatus.valueOf("ACTIVE")
        assertEquals(UserStatus.ACTIVE, status)

        val allValues = UserStatus.values()
        assertTrue(allValues.isNotEmpty())
    }

    @Test
    fun testParcelableWorks() {
        // Test Parcelable implementation
        val user = ParcelableUser(1, "Test")
        val parcel = Parcel.obtain()

        user.writeToParcel(parcel, 0)
        parcel.setDataPosition(0)

        val creator = ParcelableUser::class.java.getField("CREATOR").get(null)
        assertNotNull(creator)
    }

    @Test
    fun testNativeMethodsKept() {
        // Verify native methods are not removed
        val nativeBridge = NativeBridge()
        val methods = nativeBridge.javaClass.declaredMethods
            .filter { it.modifiers and Modifier.NATIVE != 0 }

        assertTrue(methods.isNotEmpty())
    }

    @Test
    fun testBuilderPatternWorks() {
        // Test builder classes are kept
        val config = Config.Builder()
            .setApiKey("test")
            .setTimeout(30)
            .build()

        assertEquals("test", config.apiKey)
        assertEquals(30, config.timeout)
    }

    @Test
    fun testKotlinCoroutinesWork() {
        runBlocking {
            // Verify coroutines work after obfuscation
            val result = withContext(Dispatchers.Default) {
                delay(100)
                "success"
            }

            assertEquals("success", result)
        }
    }
}
```

### Mapping File Analysis

```kotlin
/**
 * Analyze ProGuard mapping file for debugging crashes
 */
class MappingFileAnalyzer {

    data class MappingEntry(
        val originalClass: String,
        val obfuscatedClass: String,
        val methods: List<MethodMapping>
    )

    data class MethodMapping(
        val originalSignature: String,
        val obfuscatedName: String,
        val lineNumbers: String
    )

    /**
     * Parse mapping.txt file
     */
    fun parseMappingFile(mappingFile: File): List<MappingEntry> {
        val entries = mutableListOf<MappingEntry>()
        var currentEntry: MappingEntry? = null
        val methods = mutableListOf<MethodMapping>()

        mappingFile.forEachLine { line ->
            when {
                // Class mapping: com.example.MyClass -> a.b.c:
                line.contains(" -> ") && line.endsWith(":") -> {
                    currentEntry?.let {
                        entries.add(it.copy(methods = methods.toList()))
                    }
                    methods.clear()

                    val parts = line.split(" -> ")
                    val originalClass = parts[0].trim()
                    val obfuscatedClass = parts[1].removeSuffix(":").trim()

                    currentEntry = MappingEntry(
                        originalClass = originalClass,
                        obfuscatedClass = obfuscatedClass,
                        methods = emptyList()
                    )
                }

                // Method mapping: 15:20:void myMethod() -> a
                line.startsWith("    ") -> {
                    val trimmed = line.trim()
                    if (trimmed.contains(" -> ")) {
                        val parts = trimmed.split(" -> ")
                        val signature = parts[0].trim()
                        val obfuscatedName = parts[1].trim()

                        val lineNumbers = if (signature.contains(":")) {
                            signature.substringBefore(":")
                        } else ""

                        methods.add(
                            MethodMapping(
                                originalSignature = signature,
                                obfuscatedName = obfuscatedName,
                                lineNumbers = lineNumbers
                            )
                        )
                    }
                }
            }
        }

        currentEntry?.let {
            entries.add(it.copy(methods = methods.toList()))
        }

        return entries
    }

    /**
     * Deobfuscate stack trace line
     */
    fun deobfuscateStackTrace(
        obfuscatedLine: String,
        mappings: List<MappingEntry>
    ): String {
        // Example: at a.b.c.a(SourceFile:15)
        val regex = """at\s+([a-zA-Z0-9.$]+)\.([a-zA-Z0-9]+)\(.*:(\d+)\)""".toRegex()
        val match = regex.find(obfuscatedLine) ?: return obfuscatedLine

        val (obfuscatedClass, obfuscatedMethod, lineNumber) = match.destructured

        val mapping = mappings.find { it.obfuscatedClass == obfuscatedClass }
            ?: return obfuscatedLine

        val methodMapping = mapping.methods.find { it.obfuscatedName == obfuscatedMethod }

        return if (methodMapping != null) {
            "at ${mapping.originalClass}.${methodMapping.originalSignature}(${mapping.originalClass.substringAfterLast('.')}.java:$lineNumber)"
        } else {
            "at ${mapping.originalClass}.$obfuscatedMethod(?:$lineNumber)"
        }
    }

    /**
     * Deobfuscate entire stack trace
     */
    fun deobfuscateStackTrace(
        stackTrace: String,
        mappingFile: File
    ): String {
        val mappings = parseMappingFile(mappingFile)

        return stackTrace.lines().joinToString("\n") { line ->
            if (line.trim().startsWith("at ")) {
                deobfuscateStackTrace(line, mappings)
            } else {
                line
            }
        }
    }
}
```

### Gradle Configuration

```kotlin
// build.gradle.kts

android {
    buildTypes {
        release {
            // Enable R8
            isMinifyEnabled = true

            // Enable resource shrinking
            isShrinkResources = true

            // ProGuard files
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )

            // Consumer rules for library projects
            consumerProguardFiles("consumer-rules.pro")
        }

        debug {
            // Optional: Enable for testing
            isMinifyEnabled = false
        }
    }

    // Keep mapping file for crash analysis
    buildTypes.all {
        // Mapping file location
        // build/outputs/mapping/{variant}/mapping.txt
    }
}
```

### Advanced Rules Examples

#### 1. Custom Annotations

```kotlin
// Keep classes with custom annotation
@Retention(AnnotationRetention.RUNTIME)
@Target(AnnotationTarget.CLASS)
annotation class KeepClass

// ProGuard rule
-keep @com.example.KeepClass class * { *; }
```

```proguard
# Keep classes annotated with @KeepClass
-keep @com.example.annotations.KeepClass class * { *; }

# Keep methods annotated with @PublicApi
-keepclassmembers class * {
    @com.example.annotations.PublicApi *;
}
```

#### 2. Conditional Rules

```proguard
# Only if a class exists (for optional dependencies)
-if class com.example.OptionalFeature
-keep class com.example.OptionalFeatureImpl { *; }

# Keep class if used
-if class com.example.DataClass
-keep class com.example.DataClassSerializer { *; }
```

#### 3. Generic Type Preservation

```proguard
# Keep generic signatures for libraries using type parameters
-keepattributes Signature

# Specific example for Repository pattern
-keep class * implements com.example.Repository {
    <methods>;
}
```

#### 4. WebView JavaScript Interface

```proguard
# Keep JavaScript interface methods
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

-keep class com.example.JsBridge {
    public <methods>;
}
```

### Performance Impact

```kotlin
/**
 * Measure R8 optimization impact
 */
class R8PerformanceAnalysis {

    data class BuildMetrics(
        val apkSize: Long,
        val methodCount: Int,
        val classCount: Int,
        val buildTimeMs: Long
    )

    fun compareBuilds(
        debugApk: File,
        releaseApk: File
    ): Comparison {
        val debugMetrics = analyzeApk(debugApk)
        val releaseMetrics = analyzeApk(releaseApk)

        return Comparison(
            sizeReduction = calculateReduction(debugMetrics.apkSize, releaseMetrics.apkSize),
            methodReduction = calculateReduction(debugMetrics.methodCount, releaseMetrics.methodCount),
            classReduction = calculateReduction(debugMetrics.classCount, releaseMetrics.classCount)
        )
    }

    private fun calculateReduction(before: Number, after: Number): Double {
        val beforeValue = before.toDouble()
        val afterValue = after.toDouble()
        return ((beforeValue - afterValue) / beforeValue) * 100
    }

    data class Comparison(
        val sizeReduction: Double,      // Typically 30-50%
        val methodReduction: Double,    // Typically 10-30%
        val classReduction: Double      // Typically 15-40%
    )
}
```

### Common Pitfalls

1. **Over-keeping Classes**
   ```proguard
   # BAD: Too broad
   -keep class com.example.** { *; }

   # GOOD: Specific
   -keep class com.example.api.** {
       public <methods>;
   }
   ```

2. **Missing Reflection Rules**
   ```proguard
   # Classes instantiated via Class.forName need keep rules
   -keep class com.example.DynamicallyLoaded { *; }
   ```

3. **Ignoring Warnings**
   ```proguard
   # BAD: Hiding real issues
   -dontwarn **

   # GOOD: Specific ignores
   -dontwarn com.specific.optional.Dependency
   ```

4. **Forgetting Line Numbers**
   ```proguard
   # Essential for crash debugging
   -keepattributes SourceFile,LineNumberTable
   ```

5. **Not Testing Obfuscated Builds**
   ```kotlin
   // Always test release builds before shipping
   ./gradlew assembleRelease
   ./gradlew connectedAndroidTest -PtestBuildType=release
   ```

### Best Practices

1. **Use R8 Full Mode**
   ```properties
   # gradle.properties
   android.enableR8.fullMode=true
   ```

2. **Keep Minimal Public API**
   ```proguard
   -keep public class com.example.Library {
       public <init>(...);
       public <methods>;
   }
   ```

3. **Use @Keep Annotation**
   ```kotlin
   @Keep
   class ImportantClass {
       @Keep
       fun importantMethod() {}
   }
   ```

4. **Test with Multiple ProGuard Configurations**
   ```kotlin
   testBuildType "release"
   ```

5. **Upload Mapping Files**
   ```kotlin
   // Firebase Crashlytics automatically uploads
   // Or manually upload to Play Console
   ```

6. **Version Mapping Files**
   ```bash
   # Store mapping files per version
   mapping-v1.0.0.txt
   mapping-v1.0.1.txt
   ```

7. **Use Dictionary for Obfuscation**
   ```proguard
   -obfuscationdictionary dictionary.txt
   -classobfuscationdictionary dictionary.txt
   -packageobfuscationdictionary dictionary.txt
   ```

8. **Optimize Aggressively**
   ```proguard
   -optimizations !code/simplification/arithmetic,!code/simplification/cast,!field/*,!class/merging/*
   -optimizationpasses 5
   -allowaccessmodification
   -mergeinterfacesaggressively
   ```

9. **Keep Debug Info in Release**
   ```proguard
   -keepattributes SourceFile,LineNumberTable
   -renamesourcefileattribute SourceFile
   ```

10. **Document Custom Rules**
    ```proguard
    # Keep user models for JSON serialization
    # Used by Gson in UserRepository
    -keep class com.example.models.User { *; }
    ```

### Summary

ProGuard/R8 provides:

- **Code Shrinking**: Remove unused code (30-50% size reduction)
- **Optimization**: Faster and smaller bytecode
- **Obfuscation**: Protect intellectual property
- **Crash Debugging**: Mapping files for deobfuscation

**Key considerations**:
- Always test obfuscated builds
- Keep mapping files for each release
- Use specific keep rules, not blanket wildcards
- Enable in release builds only (typically)
- Upload mapping files to crash reporting services

**Typical results**:
- APK size: 30-50% smaller
- Method count: 10-30% fewer
- Build time: +20-40% longer
- Crash stack traces: Require deobfuscation

---

## Ответ (RU)
**ProGuard** и **R8** - это инструменты для уменьшения размера, оптимизации и обфускации кода Android приложений. R8 - современная замена ProGuard с лучшей производительностью и более агрессивной оптимизацией.

### Основные концепции

**Возможности R8/ProGuard:**
- Уменьшение кода: Удаление неиспользуемых классов и методов
- Оптимизация: Встраивание методов, удаление неиспользуемых параметров
- Обфускация: Переименование классов/методов в короткие имена
- Уменьшение ресурсов: Удаление неиспользуемых ресурсов

### Полный файл правил

```proguard
# proguard-rules.pro

# Сохранить номера строк для отчетов о сбоях
-keepattributes SourceFile,LineNumberTable

# Сохранить сигнатуры для Kotlin reflection
-keepattributes Signature

# Сохранить аннотации
-keepattributes *Annotation*

# Поддержка рефлексии
-keep class com.example.api.** { *; }

# Классы с аннотацией @Keep
-keep @androidx.annotation.Keep class * { *; }

# Enum классы
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Gson правила
-keepattributes Signature
-keep class com.example.models.** { *; }

# Native методы
-keepclasseswithmembernames class * {
    native <methods>;
}

# Публичный API библиотеки
-keep public class com.example.library.** {
    public protected *;
}

# Kotlin корутины
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# Retrofit
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}
```

### Consumer Rules для библиотек

```proguard
# consumer-rules.pro
# Автоматически применяются к потребителям библиотеки

-keep public class com.example.library.** {
    public protected *;
}

-keep class com.example.library.models.** { *; }

-keep interface com.example.library.callbacks.** { *; }
```

### Тестирование обфусцированных сборок

```kotlin
class ProguardRulesTest {

    @Test
    fun testPublicApiClassesKept() {
        val libraryClass = Class.forName("com.example.library.LibraryMain")
        assertNotNull(libraryClass)

        val method = libraryClass.getMethod("initialize", Context::class.java)
        assertEquals("initialize", method.name) // Не обфусцировано
    }

    @Test
    fun testSerializationWorks() {
        val user = User(id = 1, name = "Test")
        val json = Gson().toJson(user)
        val deserialized = Gson().fromJson(json, User::class.java)

        assertEquals(user.id, deserialized.id)
    }
}
```

### Анализ mapping файла

```kotlin
class MappingFileAnalyzer {

    fun deobfuscateStackTrace(
        stackTrace: String,
        mappingFile: File
    ): String {
        val mappings = parseMappingFile(mappingFile)

        return stackTrace.lines().joinToString("\n") { line ->
            if (line.trim().startsWith("at ")) {
                deobfuscateStackTrace(line, mappings)
            } else {
                line
            }
        }
    }
}
```

### Gradle конфигурация

```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )

            consumerProguardFiles("consumer-rules.pro")
        }
    }
}
```

### Best Practices

1. **Используйте R8 Full Mode**
2. **Минимальный публичный API**
3. **Аннотация @Keep для важных классов**
4. **Тестируйте обфусцированные сборки**
5. **Загружайте mapping файлы**
6. **Версионируйте mapping файлы**
7. **Оптимизируйте агрессивно**
8. **Сохраняйте debug информацию**
9. **Документируйте кастомные правила**

### Типичные результаты

- Размер APK: на 30-50% меньше
- Количество методов: на 10-30% меньше
- Время сборки: на 20-40% дольше
- Stack traces: Требуют деобфускации

### Резюме

ProGuard/R8 обеспечивает:

- **Уменьшение кода**: 30-50% сокращение размера
- **Оптимизацию**: Более быстрый байткод
- **Обфускацию**: Защита интеллектуальной собственности
- **Отладку**: Mapping файлы для деобфускации

Всегда тестируйте обфусцированные сборки и сохраняйте mapping файлы для каждого релиза.

---

## Related Questions

### Related (Medium)
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-encrypted-file-storage--android--medium]] - Security
- [[q-proguard-r8--android--medium]] - Build
- [[q-database-encryption-android--android--medium]] - Security
- [[q-dagger-build-time-optimization--android--medium]] - Build
