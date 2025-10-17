---
id: "20251015082237401"
title: "Gradle Basics / Gradle Основы"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [gradle, build-system, dependencies, difficulty/easy]
---
# Gradle Basics

**English**: What is Gradle? Explain project vs module build.gradle files, dependencies, build variants, and common Gradle tasks.

**Russian**: Что такое Gradle? Объясните файлы build.gradle проекта и модуля, зависимости, варианты сборки и основные задачи Gradle.

## Answer (EN)

**Gradle** is a build automation tool for Android that compiles code, manages dependencies, and creates APK/AAB files.

### Project Structure

```
MyApp/
 build.gradle.kts          (Project-level)
 settings.gradle.kts
 app/
    build.gradle.kts      (Module-level)
```

### Project-level build.gradle

```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
}
```

### Module-level build.gradle

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.compose.ui:ui:1.5.4")
    testImplementation("junit:junit:4.13.2")
}
```

### Dependencies

```kotlin
// Compile + Runtime
implementation("androidx.core:core-ktx:1.12.0")

// Compile-only (not in APK)
compileOnly("com.google.android.wearable:wearable:2.9.0")

// API (exposed to consumers)
api("com.squareup.retrofit2:retrofit:2.9.0")

// Test dependencies
testImplementation("junit:junit:4.13.2")
androidTestImplementation("androidx.test:core:1.5.0")
```

### Build Variants

```kotlin
buildTypes {
    debug {
        applicationIdSuffix = ".debug"
        buildConfigField("String", "API_URL", "\"https://dev.api.com\"")
    }

    release {
        isMinifyEnabled = true
        buildConfigField("String", "API_URL", "\"https://api.com\"")
    }
}
```

### Product Flavors

```kotlin
flavorDimensions += "version"

productFlavors {
    create("free") {
        dimension = "version"
        applicationIdSuffix = ".free"
    }

    create("paid") {
        dimension = "version"
        applicationIdSuffix = ".paid"
    }
}

// Generates: freeDebug, freeRelease, paidDebug, paidRelease
```

### Common Gradle Tasks

```bash
# Build APK
./gradlew assembleDebug
./gradlew assembleRelease

# Install app
./gradlew installDebug

# Run tests
./gradlew test
./gradlew connectedAndroidTest

# Clean build
./gradlew clean

# Show dependencies
./gradlew app:dependencies
```

## Ответ (RU)

**Gradle** - инструмент автоматизации сборки для Android.

### Зависимости

```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    testImplementation("junit:junit:4.13.2")
}
```

### Варианты сборки

```kotlin
buildTypes {
    debug { }
    release {
        isMinifyEnabled = true
    }
}
```

---

## Links

- [Gradle Build Configuration](https://developer.android.com/build)
- [Configure Your Build](https://developer.android.com/studio/build)

---

## Related Questions

### Advanced (Harder)
- [[q-build-optimization-gradle--gradle--medium]] - Build
- [[q-kapt-ksp-migration--gradle--medium]] - Build
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Build
