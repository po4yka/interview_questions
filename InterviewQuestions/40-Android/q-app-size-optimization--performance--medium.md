---
id: 20251011-220007
title: "App Size Optimization / Оптимизация размера приложения"
aliases: []

# Classification
topic: android
subtopics: [performance, app-size, optimization, proguard, r8, app-bundle, splits]
question_kind: practical
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: Original
source_note: App size reduction best practices

# Workflow & relations
status: draft
moc: moc-android
related: [build-optimization-gradle, proguard-r8, play-feature-delivery]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [android, performance, app-size, optimization, proguard, r8, app-bundle, splits, difficulty/medium]
---
# Question (EN)
> Comprehensively reduce APK/AAB size. Use resource shrinking, code minification with R8, native library filtering, split APKs, and Android App Bundle configuration.

# Вопрос (RU)
> Комплексно уменьшите размер APK/AAB. Используйте сжатие ресурсов, минификацию кода с R8, фильтрацию нативных библиотек, split APK и конфигурацию Android App Bundle.

---

## Answer (EN)

### Overview

**Why app size matters:**
- Download conversion rates drop 1% per 6MB
- Users on limited data plans abandon large downloads
- Play Store shows install size prominently
- Faster downloads = better user experience

**Size targets:**
- Small app: < 10MB
- Medium app: 10-50MB
- Large app: 50-100MB
- Too large: > 100MB (requires WiFi on some devices)

### Complete R8 Configuration

**app/build.gradle.kts:**
```kotlin
android {
    buildTypes {
        release {
            // Enable code shrinking and obfuscation
            isMinifyEnabled = true

            // Enable resource shrinking
            isShrinkResources = true

            // ProGuard rules
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // Enable R8 full mode for maximum optimization
    buildFeatures {
        buildConfig = true
    }
}
```

**proguard-rules.pro:**
```proguard
# Aggressive optimization
-optimizationpasses 5
-dontusemixedcaseclassnames
-dontskipnonpubliclibraryclasses
-verbose

# Remove logging in release
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
    public static *** w(...);
    public static *** e(...);
}

# Remove debug code
-assumenosideeffects class kotlin.jvm.internal.Intrinsics {
    public static void check*(...);
    public static void throw*(...);
}

# Keep data classes for serialization
-keep class com.example.model.** { *; }
-keepclassmembers class com.example.model.** { *; }

# Keep Parcelable implementations
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Remove unused resources
-keep class **.R$*
```

### Resource Shrinking

#### 1. Remove Unused Resources

**app/build.gradle.kts:**
```kotlin
android {
    buildTypes {
        release {
            isShrinkResources = true  // Automatically removes unused resources
            isMinifyEnabled = true     // Must be enabled for resource shrinking
        }
    }

    // Keep specific resources
    resourceConfigurations += listOf("en", "ru")  // Only English and Russian
}
```

**res/raw/keep.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools"
    tools:keep="@layout/used_by_reflection,@drawable/used_in_code"
    tools:discard="@layout/unused*,@drawable/unused*" />
```

#### 2. Language Filtering (resConfigs)

**Before: All languages (125 languages)**
```
APK size with all translations: 8.2MB
```

**After: Only supported languages**
```kotlin
android {
    defaultConfig {
        // Only include English, Russian, Spanish
        resourceConfigurations += listOf("en", "ru", "es")
    }
}

// APK size: 8.2MB → 5.1MB (38% reduction)
```

#### 3. Density Filtering

```kotlin
android {
    defaultConfig {
        // Support common densities only
        resourceConfigurations += listOf(
            "mdpi",
            "hdpi",
            "xhdpi",
            "xxhdpi",
            "xxxhdpi"
        )
        // Omit ldpi (rare), tvdpi (handled by scaling)
    }
}
```

### Image Optimization

#### 1. Convert PNG to WebP

**Before: PNG images**
```
PNG images: 15.2MB
  - icon_large.png: 2.4MB
  - background.png: 3.8MB
  - splash.png: 1.9MB
  ...
```

**Convert to WebP:**
```bash
# Android Studio: Right-click image → Convert to WebP
# Or use command line:
cwebp -q 80 input.png -o output.webp

# Batch convert
for f in *.png; do
    cwebp -q 80 "$f" -o "${f%.png}.webp"
done
```

**After: WebP images**
```
WebP images: 4.6MB (70% reduction)
  - icon_large.webp: 0.7MB
  - background.webp: 1.1MB
  - splash.webp: 0.6MB
```

#### 2. Use Vector Drawables

**Before: Multiple PNG densities**
```
res/
├── drawable-mdpi/icon.png (2KB)
├── drawable-hdpi/icon.png (4KB)
├── drawable-xhdpi/icon.png (8KB)
├── drawable-xxhdpi/icon.png (16KB)
└── drawable-xxxhdpi/icon.png (32KB)
Total: 62KB for one icon
```

**After: Single vector drawable**
```
res/drawable/icon.xml (< 1KB)
Total: 1KB (98% reduction)
```

**icon.xml:**
```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="@color/primary"
        android:pathData="M12,2L2,7v10c0,5.55,3.84,10.74,9,12c5.16,-1.26,9,-6.45,9,-12V7L12,2z" />
</vector>
```

#### 3. Image Compression

**build.gradle.kts:**
```kotlin
android {
    buildTypes {
        release {
            // Enable AAPT2 PNG crunching
            isCrunchPngs = true
        }
    }
}
```

### Native Library Filtering

#### 1. ABI Splits

**Before: Universal APK with all ABIs**
```
APK contains:
├── lib/armeabi-v7a/libnative.so (4.2MB)
├── lib/arm64-v8a/libnative.so (5.1MB)
├── lib/x86/libnative.so (6.8MB)
└── lib/x86_64/libnative.so (7.3MB)
Total: 23.4MB
```

**After: ABI splits**
```kotlin
android {
    splits {
        abi {
            isEnable = true
            reset()
            include("armeabi-v7a", "arm64-v8a", "x86", "x86_64")
            isUniversalApk = false  // Don't generate universal APK
        }
    }
}

// Generates separate APKs:
// app-armeabi-v7a-release.apk (7.2MB) - 32-bit ARM
// app-arm64-v8a-release.apk (8.1MB) - 64-bit ARM
// app-x86-release.apk (9.8MB) - 32-bit x86
// app-x86_64-release.apk (10.3MB) - 64-bit x86

// User only downloads one APK for their device
```

#### 2. App Bundle with ABI Filtering

**Best approach: Android App Bundle**
```kotlin
android {
    bundle {
        language {
            enableSplit = true  // Separate language APKs
        }
        density {
            enableSplit = true  // Separate density APKs
        }
        abi {
            enableSplit = true  // Separate ABI APKs
        }
    }

    defaultConfig {
        ndk {
            // Only include required ABIs
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }
}
```

**Result:**
```
Before (universal APK): 35MB
After (App Bundle):
  - Download size: 12MB (device-specific)
  - Install size: 18MB
  - Reduction: 66% smaller download
```

### Android App Bundle Configuration

**app/build.gradle.kts:**
```kotlin
android {
    bundle {
        // Language splits
        language {
            enableSplit = true
        }

        // Density splits
        density {
            enableSplit = true
        }

        // ABI splits
        abi {
            enableSplit = true
        }

        // Disable uncompressed native libraries (save space)
        enableUncompressedNativeLibs = false
    }

    // Signing configuration for bundle
    signingConfigs {
        create("release") {
            storeFile = file("keystore.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS")
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

**Build and upload:**
```bash
# Build App Bundle
./gradlew bundleRelease

# Output: app/build/outputs/bundle/release/app-release.aab

# Test locally
bundletool build-apks \
    --bundle=app-release.aab \
    --output=app.apks \
    --mode=universal

# Install on device
bundletool install-apks --apks=app.apks
```

### Dynamic Feature Modules

**settings.gradle.kts:**
```kotlin
include(":app")
include(":feature:camera")  // Dynamic feature
include(":feature:premium")  // Dynamic feature
```

**app/build.gradle.kts:**
```kotlin
android {
    dynamicFeatures += setOf(":feature:camera", ":feature:premium")
}
```

**feature/camera/build.gradle.kts:**
```kotlin
plugins {
    id("com.android.dynamic-feature")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.feature.camera"
}

dependencies {
    implementation(project(":app"))
}
```

**feature/camera/src/main/AndroidManifest.xml:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:dist="http://schemas.android.com/apk/distribution">

    <dist:module
        dist:instant="false"
        dist:title="@string/feature_camera_title">
        <dist:delivery>
            <dist:on-demand />
        </dist:delivery>
        <dist:fusing dist:include="true" />
    </dist:module>
</manifest>
```

**Load dynamic feature:**
```kotlin
class MainActivity : AppCompatActivity() {

    private val splitInstallManager by lazy {
        SplitInstallManagerFactory.create(this)
    }

    fun openCamera() {
        val request = SplitInstallRequest.newBuilder()
            .addModule("camera")
            .build()

        splitInstallManager.startInstall(request)
            .addOnSuccessListener {
                // Module downloaded, open camera
                startActivity(Intent(this, CameraActivity::class.java))
            }
            .addOnFailureListener { exception ->
                Log.e("DynamicFeature", "Failed to install", exception)
            }
    }
}
```

**Result:**
```
Base APK: 10MB (always downloaded)
Camera feature: 3MB (on-demand)
Premium feature: 5MB (on-demand)

Users without camera: Save 3MB
Users without premium: Save 5MB
```

### Dependency Optimization

#### 1. Exclude Unused Dependencies

```kotlin
dependencies {
    // Before: Full library (5MB)
    implementation("com.google.android.gms:play-services-maps:18.2.0")

    // After: Only required modules (1.2MB)
    implementation("com.google.android.gms:play-services-maps:18.2.0") {
        exclude(group = "com.google.android.gms", module = "play-services-basement")
        exclude(group = "com.google.android.gms", module = "play-services-tasks")
    }
}
```

#### 2. Use Lightweight Alternatives

```kotlin
// Before: Heavyweight library
implementation("com.google.code.gson:gson:2.10")  // 500KB

// After: Lightweight alternative
implementation("com.squareup.moshi:moshi:1.15.0")  // 180KB
ksp("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
```

### APK Analyzer

**Analyze APK:**
```
Android Studio → Build → Analyze APK
Select: app/build/outputs/apk/release/app-release.apk
```

**What to look for:**
```
Size breakdown:
├── classes.dex: 8.2MB
│   └── Check for duplicate classes
├── resources.arsc: 1.8MB
│   └── Check for unused resources
├── res/: 12.4MB
│   ├── drawable/: 8.6MB (optimize images)
│   ├── layout/: 1.2MB
│   └── values/: 2.6MB (many translations?)
├── lib/: 15.6MB
│   └── Check for unnecessary ABIs
└── META-INF/: 0.2MB
```

### Complete Optimization Example

**Before optimization:**
```
APK size: 48.2MB

Breakdown:
- DEX files: 12.4MB
- Resources: 18.6MB (PNG images)
- Native libs: 15.2MB (all ABIs)
- Other: 2.0MB
```

**After optimization:**
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
        }
    }

    defaultConfig {
        // Language filtering
        resourceConfigurations += listOf("en", "ru")

        // ABI filtering
        ndk {
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }

    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}
```

**After optimization (App Bundle):**
```
Download size: 12.1MB (75% reduction!)

Breakdown:
- DEX files: 6.8MB (R8 optimization)
- Resources: 3.2MB (WebP + shrinking)
- Native libs: 2.0MB (single ABI)
- Other: 0.1MB

User downloads only:
- Their language
- Their screen density
- Their device ABI
```

### Best Practices

1. **Use App Bundles**: 40-60% size reduction vs APK
2. **Enable R8 Full Mode**: Maximum code optimization
3. **Shrink Resources**: Remove unused resources automatically
4. **Convert to WebP**: 70-80% smaller than PNG
5. **Vector Drawables**: 90%+ smaller than PNG
6. **Filter Languages**: Only ship supported languages
7. **ABI Splits**: Only one ABI per device
8. **Dynamic Features**: On-demand module loading
9. **Analyze Regularly**: Use APK Analyzer to find bloat
10. **Exclude Unused**: Remove unnecessary library modules
11. **Compress Assets**: Use compressed formats
12. **Lint Resources**: Remove unused files

### Common Pitfalls

1. **Not Using App Bundles**: Missing 40-60% size reduction
2. **Shipping All ABIs**: 4x larger than necessary
3. **PNG Instead of WebP**: 3-5x larger images
4. **All Languages**: 100+ unnecessary translations
5. **Not Enabling R8**: Missing code optimization
6. **Heavy Dependencies**: Full libraries when only need subset
7. **Unused Resources**: Dead code and assets
8. **Large Assets**: Uncompressed images, videos
9. **Debug Symbols in Release**: ProGuard mapping files
10. **Not Monitoring Size**: Size creep over time

## Ответ (RU)

[Russian translation with all sections...]

---

## References
- [Shrink Your App](https://developer.android.com/studio/build/shrink-code)
- [Android App Bundle](https://developer.android.com/guide/app-bundle)
- [APK Analyzer](https://developer.android.com/studio/build/apk-analyzer)

## Related Questions
- What is R8 and how does it work?
- How to create dynamic feature modules?
- What are ABI splits?
- How to analyze APK size?
- What is ProGuard?
