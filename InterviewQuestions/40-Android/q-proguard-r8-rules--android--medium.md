---
id: android-153
title: "ProGuard/R8 Rules / Правила ProGuard и R8"
aliases: ["ProGuard/R8 Rules", "Правила ProGuard и R8"]
topic: android
subtopics: [obfuscation, build-variants, static-analysis]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-security-practices-checklist--android--medium, q-encrypted-file-storage--android--medium, q-database-encryption-android--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/obfuscation, android/build-variants, android/static-analysis, proguard, r8, security, difficulty/medium]
---
# Вопрос (RU)

Напишите комплексный набор правил ProGuard/R8 для Android библиотеки. Обработайте рефлексию, сериализацию, нативные методы и публичный API. Оптимизируйте для production, сохраняя функциональность.

# Question (EN)

Write comprehensive ProGuard/R8 rules for an Android library. Handle reflection, serialization, native methods, and public APIs. Optimize for production while maintaining functionality.

---

## Ответ (RU)

**R8** — современная замена ProGuard для Android. Выполняет уменьшение кода, оптимизацию и обфускацию с лучшей производительностью при полной совместимости с ProGuard.

### Основные возможности

**Что делает R8:**
- **Shrinking**: удаление неиспользуемых классов, методов, полей
- **Optimization**: встраивание методов, удаление неиспользуемых параметров
- **Obfuscation**: переименование классов/методов в короткие имена (a, b, c)
- **Resource shrinking**: удаление неиспользуемых ресурсов (с build config)

### Базовая конфигурация

```proguard
# proguard-rules.pro

# Сохранить номера строк для crash reports
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Сохранить сигнатуры для Kotlin reflection
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes InnerClasses,EnclosingMethod

# Настройки оптимизации
-optimizationpasses 5
-dontpreverify

# Не предупреждать о необязательных зависимостях
-dontwarn javax.annotation.**
-dontwarn org.jetbrains.annotations.**
```

### Поддержка рефлексии

```proguard
# Классы, используемые через рефлексию
-keep class com.example.api.** { *; }

# Классы с аннотацией @Keep
-keep @androidx.annotation.Keep class * { *; }
-keepclassmembers class * {
    @androidx.annotation.Keep *;
}

# Enum классы (доступ через reflection)
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

### Сериализация

```proguard
# Gson
-keepattributes Signature
-keep class com.example.models.** { *; }
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken

# kotlinx.serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keep,includedescriptorclasses class com.example.**$$serializer { *; }
-keepclassmembers class com.example.** {
    *** Companion;
}
```

### Native методы (JNI)

```proguard
# ✅ Сохранить native методы
-keepclasseswithmembernames,includedescriptorclasses class * {
    native <methods>;
}

# Классы, взаимодействующие с native кодом
-keep class com.example.nativelib.NativeBridge {
    public <methods>;
    public <fields>;
}

# Callback методы, вызываемые из native кода
-keepclassmembers class com.example.nativelib.** {
    public void on*(...);
    public void callback*(...);
}
```

### Публичный API библиотеки

```proguard
# Сохранить все public API классы и методы
-keep public class com.example.library.** {
    public protected *;
}

# Сохранить публичные интерфейсы
-keep public interface com.example.library.** { *; }

# Builder классы
-keep class com.example.library.**.Builder {
    public <init>(...);
    public <methods>;
}
```

### Android компоненты

```proguard
# Activities, Services, BroadcastReceivers
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider

# Custom Views
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}

# Parcelable
-keep class * implements android.os.Parcelable {
    public static final ** CREATOR;
}
```

### Kotlin специфика

```proguard
# Kotlin metadata
-keep class kotlin.Metadata { *; }

# Kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}

# Companion objects
-keepclassmembers class **$Companion {
    public <fields>;
    public <methods>;
}
```

### Сторонние библиотеки

```proguard
# Retrofit
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *

# OkHttp
-dontwarn okhttp3.**
-keepnames class okhttp3.internal.publicsuffix.PublicSuffixDatabase
```

### Consumer правила для библиотек

```proguard
# consumer-rules.pro
# Автоматически применяются к потребителям библиотеки

# Сохранить публичный API
-keep public class com.example.library.** {
    public protected *;
}

# Сохранить модели и callback интерфейсы
-keep class com.example.library.models.** { *; }
-keep interface com.example.library.callbacks.** { *; }

# Builder pattern
-keep class com.example.library.**.Builder {
    public <init>(...);
    public ** build();
    public ** set*(**);
}
```

### Gradle конфигурация

```kotlin
android {
    buildTypes {
        release {
            // Включить R8
            isMinifyEnabled = true
            isShrinkResources = true

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )

            // Consumer правила для библиотек
            consumerProguardFiles("consumer-rules.pro")
        }
    }
}
```

### Тестирование обфусцированных сборок

```kotlin
class ProguardRulesTest {

    @Test
    fun testPublicApiNotObfuscated() {
        val libraryClass = Class.forName("com.example.library.LibraryMain")
        assertNotNull(libraryClass)

        val method = libraryClass.getMethod("initialize", Context::class.java)
        assertEquals("initialize", method.name) // ✅ Не обфусцировано
    }

    @Test
    fun testSerializationWorks() {
        val user = User(id = 1, name = "Test")
        val json = Gson().toJson(user)
        val deserialized = Gson().fromJson(json, User::class.java)

        assertEquals(user.id, deserialized.id)
        assertEquals(user.name, deserialized.name)
    }

    @Test
    fun testEnumValuesWork() {
        // ✅ Enum.valueOf() требует специальных правил ProGuard
        val status = UserStatus.valueOf("ACTIVE")
        assertEquals(UserStatus.ACTIVE, status)
    }
}
```

### Распространенные ошибки

```proguard
# ❌ НЕПРАВИЛЬНО: Слишком широкое правило
-keep class com.example.** { *; }

# ✅ ПРАВИЛЬНО: Конкретные правила
-keep class com.example.api.** {
    public <methods>;
}

# ❌ НЕПРАВИЛЬНО: Игнорировать все предупреждения
-dontwarn **

# ✅ ПРАВИЛЬНО: Конкретные исключения
-dontwarn com.specific.optional.Dependency

# ❌ НЕПРАВИЛЬНО: Отсутствие номеров строк
# (невозможно отладить crashes)

# ✅ ПРАВИЛЬНО: Сохранить для debugging
-keepattributes SourceFile,LineNumberTable
```

### Best Practices

1. **Используйте R8 Full Mode** для максимальной оптимизации
2. **Минимизируйте public API** — сохраняйте только необходимое
3. **Используйте @Keep аннотацию** для важных классов
4. **Тестируйте release сборки** перед релизом
5. **Сохраняйте mapping файлы** для каждой версии
6. **Загружайте mapping в Firebase Crashlytics** или Play Console

### Типичные результаты

- **Размер APK**: уменьшение на 30-50%
- **Количество методов**: уменьшение на 10-30%
- **Время сборки**: увеличение на 20-40%
- **Stack traces**: требуют деобфускации через mapping.txt

---

## Answer (EN)

**R8** is the modern replacement for ProGuard in Android. It performs code shrinking, optimization, and obfuscation with better performance while maintaining full ProGuard compatibility.

### Core Capabilities

**What R8 does:**
- **Shrinking**: Remove unused classes, methods, and fields
- **Optimization**: Inline methods, remove unused parameters
- **Obfuscation**: Rename classes/methods to short names (a, b, c)
- **Resource shrinking**: Remove unused resources (with build config)

### Basic Configuration

```proguard
# proguard-rules.pro

# Keep line numbers for crash reports
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Keep signatures for Kotlin reflection
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes InnerClasses,EnclosingMethod

# Optimization settings
-optimizationpasses 5
-dontpreverify

# Don't warn about optional dependencies
-dontwarn javax.annotation.**
-dontwarn org.jetbrains.annotations.**
```

### Reflection Support

```proguard
# Classes used via reflection
-keep class com.example.api.** { *; }

# Classes with @Keep annotation
-keep @androidx.annotation.Keep class * { *; }
-keepclassmembers class * {
    @androidx.annotation.Keep *;
}

# Enum classes (accessed via reflection)
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

### Serialization

```proguard
# Gson
-keepattributes Signature
-keep class com.example.models.** { *; }
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken

# kotlinx.serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
-keep,includedescriptorclasses class com.example.**$$serializer { *; }
-keepclassmembers class com.example.** {
    *** Companion;
}
```

### Native Methods (JNI)

```proguard
# ✅ Keep native methods
-keepclasseswithmembernames,includedescriptorclasses class * {
    native <methods>;
}

# Classes that interact with native code
-keep class com.example.nativelib.NativeBridge {
    public <methods>;
    public <fields>;
}

# Callback methods called from native code
-keepclassmembers class com.example.nativelib.** {
    public void on*(...);
    public void callback*(...);
}
```

### Library Public API

```proguard
# Keep all public API classes and methods
-keep public class com.example.library.** {
    public protected *;
}

# Keep public interfaces
-keep public interface com.example.library.** { *; }

# Builder classes
-keep class com.example.library.**.Builder {
    public <init>(...);
    public <methods>;
}
```

### Android Components

```proguard
# Activities, Services, BroadcastReceivers
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider

# Custom Views
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}

# Parcelable
-keep class * implements android.os.Parcelable {
    public static final ** CREATOR;
}
```

### Kotlin Specific

```proguard
# Kotlin metadata
-keep class kotlin.Metadata { *; }

# Kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}

# Companion objects
-keepclassmembers class **$Companion {
    public <fields>;
    public <methods>;
}
```

### Third-Party Libraries

```proguard
# Retrofit
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *

# OkHttp
-dontwarn okhttp3.**
-keepnames class okhttp3.internal.publicsuffix.PublicSuffixDatabase
```

### Consumer Rules for Libraries

```proguard
# consumer-rules.pro
# Automatically applied to library consumers

# Keep public API
-keep public class com.example.library.** {
    public protected *;
}

# Keep models and callback interfaces
-keep class com.example.library.models.** { *; }
-keep interface com.example.library.callbacks.** { *; }

# Builder pattern
-keep class com.example.library.**.Builder {
    public <init>(...);
    public ** build();
    public ** set*(**);
}
```

### Gradle Configuration

```kotlin
android {
    buildTypes {
        release {
            // Enable R8
            isMinifyEnabled = true
            isShrinkResources = true

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )

            // Consumer rules for libraries
            consumerProguardFiles("consumer-rules.pro")
        }
    }
}
```

### Testing Obfuscated Builds

```kotlin
class ProguardRulesTest {

    @Test
    fun testPublicApiNotObfuscated() {
        val libraryClass = Class.forName("com.example.library.LibraryMain")
        assertNotNull(libraryClass)

        val method = libraryClass.getMethod("initialize", Context::class.java)
        assertEquals("initialize", method.name) // ✅ Not obfuscated
    }

    @Test
    fun testSerializationWorks() {
        val user = User(id = 1, name = "Test")
        val json = Gson().toJson(user)
        val deserialized = Gson().fromJson(json, User::class.java)

        assertEquals(user.id, deserialized.id)
        assertEquals(user.name, deserialized.name)
    }

    @Test
    fun testEnumValuesWork() {
        // ✅ Enum.valueOf() requires specific ProGuard rules
        val status = UserStatus.valueOf("ACTIVE")
        assertEquals(UserStatus.ACTIVE, status)
    }
}
```

### Common Mistakes

```proguard
# ❌ WRONG: Too broad
-keep class com.example.** { *; }

# ✅ CORRECT: Specific rules
-keep class com.example.api.** {
    public <methods>;
}

# ❌ WRONG: Ignoring all warnings
-dontwarn **

# ✅ CORRECT: Specific ignores
-dontwarn com.specific.optional.Dependency

# ❌ WRONG: Missing line numbers
# (can't debug crashes)

# ✅ CORRECT: Keep for debugging
-keepattributes SourceFile,LineNumberTable
```

### Best Practices

1. **Use R8 Full Mode** for maximum optimization
2. **Minimize public API** — keep only what's necessary
3. **Use @Keep annotation** for important classes
4. **Test release builds** before shipping
5. **Store mapping files** for each version
6. **Upload mapping to Firebase Crashlytics** or Play Console

### Typical Results

- **APK size**: 30-50% reduction
- **Method count**: 10-30% reduction
- **Build time**: 20-40% increase
- **Stack traces**: Require deobfuscation via mapping.txt

---

## Follow-ups

- How to debug crashes in obfuscated production builds?
- What's the difference between ProGuard and R8 optimization strategies?
- How to handle reflection in libraries when field names are obfuscated?
- Should you enable obfuscation for debug builds during development?
- How to deobfuscate stack traces manually without Play Console?

## References

- Android R8 documentation
- ProGuard manual for advanced rules

## Related Questions

### Prerequisites
- Build variants and configurations (basics)

### Related
- [[q-android-security-practices-checklist--android--medium]] - Security practices
- [[q-encrypted-file-storage--android--medium]] - Encrypted storage
- [[q-database-encryption-android--android--medium]] - Database encryption

### Advanced
- Custom Gradle plugins for build optimization
