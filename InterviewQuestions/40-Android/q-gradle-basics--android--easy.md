---
id: 20251012-152245
title: "Gradle Basics / Gradle Основы"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-room-transactions-dao--room--medium, q-android-runtime-art--android--medium, q-large-file-upload--android--medium]
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

**Gradle** — это инструмент автоматизации сборки для Android, который компилирует код, управляет зависимостями и создает APK/AAB файлы.

### Структура проекта

```
MyApp/
 build.gradle.kts          (Уровень проекта)
 settings.gradle.kts
 app/
    build.gradle.kts      (Уровень модуля)
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

### Зависимости

```kotlin
// Compile + Runtime
implementation("androidx.core:core-ktx:1.12.0")

// Compile-only (не включается в APK)
compileOnly("com.google.android.wearable:wearable:2.9.0")

// API (доступно потребителям)
api("com.squareup.retrofit2:retrofit:2.9.0")

// Тестовые зависимости
testImplementation("junit:junit:4.13.2")
androidTestImplementation("androidx.test:core:1.5.0")
```

### Варианты сборки

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

// Генерирует: freeDebug, freeRelease, paidDebug, paidRelease
```

### Основные задачи Gradle

```bash
# Собрать APK
./gradlew assembleDebug
./gradlew assembleRelease

# Установить приложение
./gradlew installDebug

# Запустить тесты
./gradlew test
./gradlew connectedAndroidTest

# Очистить сборку
./gradlew clean

# Показать зависимости
./gradlew app:dependencies
```


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
