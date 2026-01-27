---
id: sec-006
title: ProGuard and R8 Code Obfuscation / Obfuskaciya koda s ProGuard i R8
aliases:
- ProGuard
- R8
- Code Obfuscation
- Minification
topic: android
subtopics:
- security
- build
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
created: 2026-01-23
updated: 2026-01-23
tags:
- android/security
- android/build
- difficulty/medium
related:
- q-root-detection--security--medium
- q-app-signing--security--medium
sources:
- https://developer.android.com/build/shrink-code
- https://www.guardsquare.com/manual/configuration/usage
anki_cards:
- slug: sec-006-0-en
  language: en
- slug: sec-006-0-ru
  language: ru
---
# Vopros (RU)
> Kak nastroit' R8/ProGuard dlya obfuskacii koda i kakie pravila keep ispol'zovat'?

# Question (EN)
> How do you configure R8/ProGuard for code obfuscation and what keep rules should you use?

---

## Otvet (RU)

**Teoriya:**
**R8** - eto sovremennyj kompilator dlya Android (zamenil ProGuard v 2018), kotoryj vypolnyaet:
- **Shrinking**: udalenie neispol'zuemogo koda
- **Obfuscation**: pereimenovanie klassov/metodov v korotkie imena
- **Optimization**: optimizaciya bayt-koda
- **Desugaring**: podderzhka novyh Java/Kotlin features na staryh API

### Vklyuchenie R8
```kotlin
// build.gradle.kts (module)
android {
    buildTypes {
        release {
            isMinifyEnabled = true      // Vklyuchaet R8
            isShrinkResources = true    // Udalyaet neispol'zuemye resursy
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### Bazovye pravila (proguard-rules.pro)
```proguard
# ======= OSNOVNYE PRAVILA =======

# Sohranyaem atributy dlya stack traces
-keepattributes SourceFile,LineNumberTable

# Sohranyaem annotacii (vazno dlya DI, serialization)
-keepattributes *Annotation*

# Sohranyaem signatury dlya Kotlin generics
-keepattributes Signature

# ======= KOTLIN =======

# Kotlin Metadata (dlya reflection)
-keep class kotlin.Metadata { *; }

# Kotlin coroutines
-keepclassmembernames class kotlinx.** {
    volatile <fields>;
}

# ======= SERIALIZATION =======

# Kotlinx Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt

-keepclassmembers @kotlinx.serialization.Serializable class ** {
    *** Companion;
}

-keepclasseswithmembers class ** {
    @kotlinx.serialization.Serializable <methods>;
}

# Gson
-keepattributes Signature
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.TypeAdapter

# Moshi
-keepclasseswithmembers class * {
    @com.squareup.moshi.* <methods>;
}

# ======= NETWORKING =======

# Retrofit
-keepattributes Signature, Exceptions
-keepclasseswithmembers class * {
    @retrofit2.http.* <methods>;
}

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**

# ======= ANDROID =======

# ViewBinding
-keep class * implements androidx.viewbinding.ViewBinding {
    public static *** bind(android.view.View);
    public static *** inflate(...);
}

# ViewModel
-keep class * extends androidx.lifecycle.ViewModel {
    <init>(...);
}

# Room
-keep class * extends androidx.room.RoomDatabase
-keepclassmembers class * {
    @androidx.room.* <methods>;
}

# Navigation SafeArgs
-keepnames class * extends android.os.Parcelable
-keepnames class * extends java.io.Serializable

# ======= MODEL CLASSES =======

# Data classes (obychno API modeli)
-keep class com.example.app.data.model.** { *; }

# Enums
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

### Pravila dlya konkretnyh sluchaev
```proguard
# ======= REFLECTION =======

# Esli ispol'zuete reflection dlya opredelennyh klassov
-keep class com.example.app.reflection.** { *; }

# ======= JNI / NATIVE =======

# Native metody
-keepclasseswithmembernames class * {
    native <methods>;
}

# ======= CRASHLYTICS =======

# Firebase Crashlytics
-keepattributes SourceFile,LineNumberTable
-keep public class * extends java.lang.Exception
-keep class com.google.firebase.crashlytics.** { *; }

# ======= CUSTOM VIEWS =======

# Custom views sozdavayutsya cherez XML (reflection)
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}

# ======= PARCELABLE =======

-keepclassmembers class * implements android.os.Parcelable {
    public static final ** CREATOR;
}
```

### Diagnostika problem
```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            // Sohranyaet mapping.txt dlya deobfuskacii stack traces
            isMinifyEnabled = true
        }
    }

    // Sohranyaet informaciyu o tom, chto bylo udaleno
    buildFeatures {
        buildConfig = true
    }
}

// Proverka chto bylo udaleno
// app/build/outputs/mapping/release/
//   - mapping.txt      : Kartirovanie originalnyh -> obfuscirovannyh imen
//   - seeds.txt        : Klassy kotorye sohraneny pravilami keep
//   - usage.txt        : Kod kotoryj byl udalen
//   - configuration.txt: Final'naya konfiguraciya
```

### Obrabotka oshibok pri sborke
```proguard
# Esli biblioteka vydaet warning
-dontwarn com.some.library.**

# Esli nuzhno proverit' chto ostaetsya (debugging)
-printseeds seeds.txt
-printusage unused.txt
-printmapping mapping.txt
```

### Optimizaciya dlya bezopasnosti
```proguard
# Maksimal'naya obfuskaciya
-optimizationpasses 5
-allowaccessmodification
-repackageclasses ''

# Peremeshivaet klassy v odin paket (uslozhnyaet analiz)
-flattenpackagehierarchy

# Udalyaet Log vyzyvy v release
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}

# Udalyaet println (debugging)
-assumenosideeffects class java.io.PrintStream {
    public void println(...);
}
```

### Proverka rezul'tata obfuskacii
```bash
# Dekompilirovanie APK dlya proverki
jadx -d output/ app-release.apk

# APK Analyzer v Android Studio
# Build -> Analyze APK -> Vybrat' app-release.apk
```

### Vazhno
| Aspekt | Opisanie |
|--------|----------|
| R8 vs ProGuard | R8 bystree i luchshe optimiziruet, no ispol'zuet ProGuard pravila |
| Keep rules | Slishkom mnogo keep = plohaya obfuskaciya; slishkom malo = crashes |
| Testing | VSEGDA testiruyte release build |
| Mapping | Sohranyajte mapping.txt dlya kazhdogo release |

---

## Answer (EN)

**Theory:**
**R8** is the modern compiler for Android (replaced ProGuard in 2018), which performs:
- **Shrinking**: removal of unused code
- **Obfuscation**: renaming classes/methods to short names
- **Optimization**: bytecode optimization
- **Desugaring**: support for new Java/Kotlin features on old APIs

### Enabling R8
```kotlin
// build.gradle.kts (module)
android {
    buildTypes {
        release {
            isMinifyEnabled = true      // Enables R8
            isShrinkResources = true    // Removes unused resources
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### Basic rules (proguard-rules.pro)
```proguard
# ======= BASIC RULES =======

# Keep attributes for stack traces
-keepattributes SourceFile,LineNumberTable

# Keep annotations (important for DI, serialization)
-keepattributes *Annotation*

# Keep signatures for Kotlin generics
-keepattributes Signature

# ======= KOTLIN =======

# Kotlin Metadata (for reflection)
-keep class kotlin.Metadata { *; }

# Kotlin coroutines
-keepclassmembernames class kotlinx.** {
    volatile <fields>;
}

# ======= SERIALIZATION =======

# Kotlinx Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt

-keepclassmembers @kotlinx.serialization.Serializable class ** {
    *** Companion;
}

-keepclasseswithmembers class ** {
    @kotlinx.serialization.Serializable <methods>;
}

# Gson
-keepattributes Signature
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.TypeAdapter

# Moshi
-keepclasseswithmembers class * {
    @com.squareup.moshi.* <methods>;
}

# ======= NETWORKING =======

# Retrofit
-keepattributes Signature, Exceptions
-keepclasseswithmembers class * {
    @retrofit2.http.* <methods>;
}

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**

# ======= ANDROID =======

# ViewBinding
-keep class * implements androidx.viewbinding.ViewBinding {
    public static *** bind(android.view.View);
    public static *** inflate(...);
}

# ViewModel
-keep class * extends androidx.lifecycle.ViewModel {
    <init>(...);
}

# Room
-keep class * extends androidx.room.RoomDatabase
-keepclassmembers class * {
    @androidx.room.* <methods>;
}

# Navigation SafeArgs
-keepnames class * extends android.os.Parcelable
-keepnames class * extends java.io.Serializable

# ======= MODEL CLASSES =======

# Data classes (usually API models)
-keep class com.example.app.data.model.** { *; }

# Enums
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

### Rules for specific cases
```proguard
# ======= REFLECTION =======

# If using reflection for specific classes
-keep class com.example.app.reflection.** { *; }

# ======= JNI / NATIVE =======

# Native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# ======= CRASHLYTICS =======

# Firebase Crashlytics
-keepattributes SourceFile,LineNumberTable
-keep public class * extends java.lang.Exception
-keep class com.google.firebase.crashlytics.** { *; }

# ======= CUSTOM VIEWS =======

# Custom views created via XML (reflection)
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}

# ======= PARCELABLE =======

-keepclassmembers class * implements android.os.Parcelable {
    public static final ** CREATOR;
}
```

### Diagnosing problems
```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            // Keeps mapping.txt for deobfuscating stack traces
            isMinifyEnabled = true
        }
    }

    // Keeps information about what was removed
    buildFeatures {
        buildConfig = true
    }
}

// Check what was removed
// app/build/outputs/mapping/release/
//   - mapping.txt      : Mapping of original -> obfuscated names
//   - seeds.txt        : Classes kept by keep rules
//   - usage.txt        : Code that was removed
//   - configuration.txt: Final configuration
```

### Handling build errors
```proguard
# If library produces warning
-dontwarn com.some.library.**

# If need to check what remains (debugging)
-printseeds seeds.txt
-printusage unused.txt
-printmapping mapping.txt
```

### Security optimization
```proguard
# Maximum obfuscation
-optimizationpasses 5
-allowaccessmodification
-repackageclasses ''

# Moves classes to single package (complicates analysis)
-flattenpackagehierarchy

# Remove Log calls in release
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}

# Remove println (debugging)
-assumenosideeffects class java.io.PrintStream {
    public void println(...);
}
```

### Verifying obfuscation result
```bash
# Decompile APK for verification
jadx -d output/ app-release.apk

# APK Analyzer in Android Studio
# Build -> Analyze APK -> Select app-release.apk
```

### Important notes
| Aspect | Description |
|--------|-------------|
| R8 vs ProGuard | R8 is faster and optimizes better, but uses ProGuard rules |
| Keep rules | Too many keep = poor obfuscation; too few = crashes |
| Testing | ALWAYS test release build |
| Mapping | Save mapping.txt for each release |

---

## Follow-ups

- How do you debug crashes in obfuscated code?
- What is the difference between R8 full mode and compatibility mode?
- How do you handle library-specific ProGuard rules?
- What additional obfuscation tools exist beyond R8?

## References

- https://developer.android.com/build/shrink-code
- https://www.guardsquare.com/manual/configuration/usage
- https://r8.googlesource.com/r8

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android basics

### Related (Same Level)
- [[q-root-detection--security--medium]] - Root detection
- [[q-app-signing--security--medium]] - App signing
