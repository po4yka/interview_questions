---
id: android-153
title: ProGuard/R8 Rules / Правила ProGuard и R8
aliases:
- ProGuard/R8 Rules
- Правила ProGuard и R8
topic: android
subtopics:
- build-variants
- obfuscation
- static-analysis
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-gradle
- q-android-security-practices-checklist--android--medium
- q-database-encryption-android--android--medium
- q-encrypted-file-storage--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/build-variants
- android/obfuscation
- android/static-analysis
- difficulty/medium
- proguard
- r8
- security
anki_cards:
- slug: android-153-0-en
  language: en
  anki_id: 1768398221060
  synced_at: '2026-01-23T16:45:05.436603'
- slug: android-153-0-ru
  language: ru
  anki_id: 1768398221084
  synced_at: '2026-01-23T16:45:05.438179'
---
# Вопрос (RU)

> Напишите комплексный набор правил ProGuard/R8 для Android библиотеки. Обработайте рефлексию, сериализацию, нативные методы и публичный API. Оптимизируйте для production, сохраняя функциональность.

# Question (EN)

> Write comprehensive ProGuard/R8 rules for an Android library. Handle reflection, serialization, native methods, and public APIs. Optimize for production while maintaining functionality.

---

## Ответ (RU)

**R8** — современная замена ProGuard для Android (по умолчанию используется Android Gradle Plugin, отдельный шаг ProGuard не запускается). Выполняет уменьшение кода, оптимизацию и обфускацию, в целом совместим с синтаксисом правил ProGuard (но некоторые старые опции игнорируются).

### Основные Возможности

**Что делает R8:**
- **Shrinking**: удаление неиспользуемых классов, методов, полей
- **Optimization**: встраивание методов, удаление неиспользуемых параметров и пр.
- **Obfuscation**: переименование классов/методов в короткие имена (a, b, c)
- (В связке с Android Gradle Plugin) **Resource shrinking**: удаление неиспользуемых ресурсов на основе информации об использовании кода

### Базовая Конфигурация

```proguard
# proguard-rules.pro

# Сохранить номера строк для crash reports
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Сохранить сигнатуры и аннотации (важно для Kotlin reflection и ряда библиотек)
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes InnerClasses,EnclosingMethod

# Старые настройки оптимизации (-optimizationpasses, -dontpreverify)
# игнорируются R8 и указывать их необязательно.

# Не предупреждать о необязательных зависимостях-аннотациях
-dontwarn javax.annotation.**
-dontwarn org.jetbrains.annotations.**
```

### Поддержка Рефлексии

```proguard
# Классы, используемые через рефлексию (указывать ТОЛЬКО при реальном использовании)
-keep class com.example.api.** { *; }

# Классы с аннотацией @Keep
-keep @androidx.annotation.Keep class * { *; }
-keepclassmembers class * {
    @androidx.annotation.Keep *;
}

# Enum-классы, доступные через reflection (Enum.valueOf и values сохраняются автоматически,
# отдельные правила нужны только при нестандартном доступе/рефлексии)
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

### Сериализация

```proguard
# Gson (минимальный пример для моделей, используемых через рефлексию)
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

### Native Методы (JNI)

```proguard
# ✅ Сохранить сигнатуры native-методов, которые вызываются из JNI по имени
-keepclasseswithmembernames,includedescriptorclasses class * {
    native <methods>;
}

# Классы, взаимодействующие с native-кодом (пример — уточняйте под свою библиотеку)
-keep class com.example.nativelib.NativeBridge {
    public <methods>;
    public <fields>;
}

# Callback-методы, вызываемые из native-кода по именам
-keepclassmembers class com.example.nativelib.** {
    public void on*(...);
    public void callback*(...);
}
```

### Публичный API Библиотеки

```proguard
# Сохранить весь public API библиотеки (настройка для library module)
-keep public class com.example.library.** {
    public protected *;
}

# Сохранить публичные интерфейсы
-keep public interface com.example.library.** { *; }

# Builder-классы (если их API важно сохранить стабильно)
-keep class com.example.library.**.Builder {
    public <init>(...);
    public <methods>;
}
```

### Android Компоненты (если Библиотека Их предоставляет)

```proguard
# Activities, Services, BroadcastReceivers, ContentProviders — нужны приложению/манифесту
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

### Kotlin Специфика

```proguard
# Kotlin metadata (обычно сохраняется AGP по умолчанию; явно если требуется tooling)
-keep class kotlin.Metadata { *; }

# Kotlin coroutines: стандартно дополнительных правил почти не требуется;
# минимум для фабрик диспетчеров, если используются
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler

# Companion objects (если к ним обращаются рефлексией)
-keepclassmembers class **$Companion {
    public <fields>;
    public <methods>;
}
```

### Сторонние Библиотеки (примеры — Уточняются Под Конкретную интеграцию)

```proguard
# Retrofit — сохраняем только интерфейсы с HTTP-аннотациями
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# Room (упрощённый пример; реальные правила зависят от версии)
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
# Дополнительно обычно требуются keep для Dao и сгенерированных классов (см. официальную доку Room).

# OkHttp — глобальный dontwarn okhttp3.** нежелателен; используйте только при
# хорошо понятных ложных предупреждениях.
-keepnames class okhttp3.internal.publicsuffix.PublicSuffixDatabase
```

### Consumer Правила Для Библиотек

```proguard
# consumer-rules.pro — кладётся в модуле библиотеки и автоматически
# применяется к потребителям.

# Сохранить публичный API библиотеки
-keep public class com.example.library.** {
    public protected *;
}

# Сохранить модели и callback-интерфейсы, используемые потребителями
-keep class com.example.library.models.** { *; }
-keep interface com.example.library.callbacks.** { *; }

# Builder pattern
-keep class com.example.library.**.Builder {
    public <init>(...);
    public ** build();
    public ** set*(**);
}
```

### Gradle Конфигурация

```kotlin
android {
    buildTypes {
        release {
            // Включить R8 (по умолчанию используется R8, когда minifyEnabled = true)
            isMinifyEnabled = true
            isShrinkResources = true

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // Для библиотечного модуля consumerProguardFiles задаются на уровне android {}
    defaultConfig {
        consumerProguardFiles("consumer-rules.pro")
    }
}
```

### Тестирование Обфусцированных Сборок

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
        // ✅ Enum.valueOf() обычно поддерживается, но при агрессивных правилах стоит убедиться
        val status = UserStatus.valueOf("ACTIVE")
        assertEquals(UserStatus.ACTIVE, status)
    }
}
```

### Распространенные Ошибки

```proguard
# ❌ НЕПРАВИЛЬНО: Слишком широкое правило
-keep class com.example.** { *; }

# ✅ ПРАВИЛЬНО: Конкретные правила под публичный API и отражённое использование
-keep class com.example.api.** {
    public <methods>;
}

# ❌ НЕПРАВИЛЬНО: Игнорировать все предупреждения
-dontwarn **

# ✅ ПРАВИЛЬНО: Конкретные исключения под известные ложные warning'и
-dontwarn com.specific.optional.Dependency

# ❌ НЕПРАВИЛЬНО: Отсутствие номеров строк (невозможно отладить crashes)

# ✅ ПРАВИЛЬНО: Сохранить для debugging
-keepattributes SourceFile,LineNumberTable
```

### Best Practices

1. **Используйте R8 (Full Mode включён по умолчанию в современных AGP)** для максимальной оптимизации
2. **Минимизируйте public API** — сохраняйте только необходимое
3. **Используйте @Keep аннотацию** для важных классов, полей, методов, используемых через reflection/JNI
4. **Тестируйте release-сборки** перед релизом
5. **Сохраняйте mapping-файлы** для каждой версии
6. **Загружайте mapping в Firebase Crashlytics или Play Console** для деобфускации

### Типичные Результаты

- **Размер APK/AAB**: уменьшение (часто 20–50% в зависимости от проекта)
- **Количество методов**: уменьшение на 10–30%
- **Время сборки**: возможно увеличение за счёт оптимизаций
- **`Stack` traces**: требуют деобфускации через `mapping.txt`

---

## Answer (EN)

**R8** is the modern replacement for ProGuard in Android (it is used by the Android Gradle Plugin by default; there is no separate ProGuard step). It performs code shrinking, optimization, and obfuscation and is broadly compatible with ProGuard rule syntax (some legacy options are ignored).

### Core Capabilities

**What R8 does:**
- **Shrinking**: Remove unused classes, methods, and fields
- **Optimization**: Inline methods, remove unused parameters, etc.
- **Obfuscation**: Rename classes/methods to short names (a, b, c)
- In cooperation with the Android Gradle Plugin, **resource shrinking**: remove unused resources based on code usage

### Basic Configuration

```proguard
# proguard-rules.pro

# Keep line numbers for crash reports
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Keep signatures and annotations (important for Kotlin reflection and many libs)
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes InnerClasses,EnclosingMethod

# Legacy options like -optimizationpasses and -dontpreverify are ignored by R8
# and are not required in modern Android builds.

# Don't warn about optional annotation dependencies
-dontwarn javax.annotation.**
-dontwarn org.jetbrains.annotations.**
```

### Reflection Support

```proguard
# Classes used via reflection (ONLY if actually accessed reflectively)
-keep class com.example.api.** { *; }

# Classes with @Keep annotation
-keep @androidx.annotation.Keep class * { *; }
-keepclassmembers class * {
    @androidx.annotation.Keep *;
}

# Enum classes accessed reflectively.
# Enum.valueOf() / values() are normally kept automatically; explicit rules
# are needed only for custom reflective access patterns.
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

### Serialization

```proguard
# Gson (minimal example for models used reflectively)
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
# ✅ Keep native method signatures that are called from JNI by name
-keepclasseswithmembernames,includedescriptorclasses class * {
    native <methods>;
}

# Classes that interact with native code (example — adjust to your library)
-keep class com.example.nativelib.NativeBridge {
    public <methods>;
    public <fields>;
}

# Callback methods invoked from native code by name
-keepclassmembers class com.example.nativelib.** {
    public void on*(...);
    public void callback*(...);
}
```

### Library Public API

```proguard
# Keep all public API of the library (for a library module)
-keep public class com.example.library.** {
    public protected *;
}

# Keep public interfaces
-keep public interface com.example.library.** { *; }

# Builder classes (if their API must remain stable)
-keep class com.example.library.**.Builder {
    public <init>(...);
    public <methods>;
}
```

### Android Components (if the Library Provides them)

```proguard
# Activities, Services, BroadcastReceivers, ContentProviders referenced from manifest
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
# Kotlin metadata (AGP usually retains needed parts; keep explicitly if tooling relies on it)
-keep class kotlin.Metadata { *; }

# Kotlin coroutines: typically no extensive rules are required.
# Minimal examples when using dispatcher factories:
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler

# Companion objects (if accessed reflectively)
-keepclassmembers class **$Companion {
    public <fields>;
    public <methods>;
}
```

### Third-Party Libraries (examples; Refine per Actual usage)

```proguard
# Retrofit — keep only interfaces with Retrofit HTTP annotations
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# Room (simplified; refer to official docs for full rules)
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
# In practice, additional keeps for Dao interfaces and generated implementations are required.

# OkHttp — avoid blanket -dontwarn okhttp3.**; only add targeted rules
# if you fully understand the warnings.
-keepnames class okhttp3.internal.publicsuffix.PublicSuffixDatabase
```

### Consumer Rules for Libraries

```proguard
# consumer-rules.pro — placed in the library module and automatically
# applied to consumers.

# Keep public API
-keep public class com.example.library.** {
    public protected *;
}

# Keep models and callback interfaces exposed to consumers
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
            // Enable R8: minifyEnabled = true triggers R8 in modern AGP
            isMinifyEnabled = true
            isShrinkResources = true

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // For a library module, configure consumerProguardFiles at the android/defaultConfig level
    defaultConfig {
        consumerProguardFiles("consumer-rules.pro")
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
        // ✅ Enum.valueOf() is normally supported, but verify with aggressive rules
        val status = UserStatus.valueOf("ACTIVE")
        assertEquals(UserStatus.ACTIVE, status)
    }
}
```

### Common Mistakes

```proguard
# ❌ WRONG: Too broad
-keep class com.example.** { *; }

# ✅ CORRECT: Specific rules for public API and reflective/JNI usage
-keep class com.example.api.** {
    public <methods>;
}

# ❌ WRONG: Ignoring all warnings
-dontwarn **

# ✅ CORRECT: Specific ignores for known false positives
-dontwarn com.specific.optional.Dependency

# ❌ WRONG: Missing line numbers (can't debug crashes)

# ✅ CORRECT: Keep for debugging
-keepattributes SourceFile,LineNumberTable
```

### Best Practices

1. **Use R8 (Full Mode is enabled by default in modern AGP)** for maximum optimization
2. **Minimize public API** — keep only what must remain stable
3. **Use @Keep** for classes/fields/methods used via reflection or JNI
4. **Test release builds** before shipping
5. **Store mapping files** for each version
6. **Upload mapping to Firebase Crashlytics or Play Console** for deobfuscation

### Typical Results

- **APK/AAB size**: often 20–50% reduction depending on project
- **Method count**: 10–30% reduction
- **Build time**: may increase due to optimizations
- **`Stack` traces**: require deobfuscation via `mapping.txt`

---

## Дополнительные Вопросы (RU)

- Как отлаживать крэши в обфусцированных production-сборках?
- В чем разница в подходах к оптимизации между ProGuard и R8?
- Как корректно обрабатывать рефлексию в библиотеках при обфускации имен полей?
- Стоит ли включать обфускацию для debug-сборок во время разработки?
- Как деобфусцировать stack traces вручную без Play Console?

## Follow-ups

- How to debug crashes in obfuscated production builds?
- What's the difference between ProGuard and R8 optimization strategies?
- How to handle reflection in libraries when field names are obfuscated?
- Should you enable obfuscation for debug builds during development?
- How to deobfuscate stack traces manually without Play Console?

## Ссылки (RU)

- https://r8.googlesource.com/r8
- https://www.guardsquare.com/manual/configuration

## References

- https://r8.googlesource.com/r8
- https://www.guardsquare.com/manual/configuration

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-gradle]]

### Предпосылки

- Базовые знания о build variants и конфигурациях

### Связанные

- [[q-android-security-practices-checklist--android--medium]] — Практики безопасности
- [[q-encrypted-file-storage--android--medium]] — Шифрованное файловое хранилище
- [[q-database-encryption-android--android--medium]] — Шифрование баз данных на Android

### Продвинутое

- Кастомные Gradle-плагины для оптимизации сборки

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]

### Prerequisites

- Build variants and configurations (basics)

### Related

- [[q-android-security-practices-checklist--android--medium]] - Security practices
- [[q-encrypted-file-storage--android--medium]] - Encrypted storage
- [[q-database-encryption-android--android--medium]] - `Database` encryption

### Advanced

- Custom Gradle plugins for build optimization
