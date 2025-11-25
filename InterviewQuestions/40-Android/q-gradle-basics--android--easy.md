---
id: android-236
title: Gradle Basics / Gradle Основы
aliases: [Gradle Basics, Gradle Основы]
topic: android
subtopics:
  - build-variants
  - gradle
question_kind: theory
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-gradle
  - q-android-runtime-art--android--medium
  - q-build-optimization-gradle--android--medium
  - q-gradle-version-catalog--android--medium
  - q-jetpack-compose-basics--android--medium
  - q-large-file-upload--android--medium
  - q-room-transactions-dao--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/build-variants, android/gradle, build-system, dependencies, difficulty/easy]

date created: Saturday, November 1st 2025, 12:46:50 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---

# Вопрос (RU)
> Gradle Основы

# Question (EN)
> Gradle Basics

---

## Ответ (RU)

Gradle — это универсальный инструмент автоматизации сборки. В Android-проектах он используется вместе с Android Gradle Plugin для компиляции кода, управления зависимостями и создания APK/AAB артефактов.

### Структура Проекта

```
MyApp/
 build.gradle.kts          (уровень проекта)
 settings.gradle.kts
 app/
    build.gradle.kts      (уровень модуля: модуль app)
```

### Файл build.gradle.kts На Уровне Проекта

```kotlin
plugins {
    // Примеры версий; в реальных проектах используйте актуальные стабильные версии
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
}
```

### Файл build.gradle.kts На Уровне Модуля (модуль приложения)

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
        debug {
            // настройки для debug-сборки (например, дополнительный логгинг)
        }
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
// implementation: доступно при компиляции и в рантайме
implementation("androidx.core:core-ktx:1.12.0")

// compileOnly: только в compile-класспате, не попадает в итоговый APK/AAB
compileOnly("com.google.android.wearable:wearable:2.9.0")

// api: для модулей-библиотек делает зависимость доступной потребителям на этапе компиляции
// (в модуле приложения ведет себя по сути как implementation для самого приложения)
api("com.squareup.retrofit2:retrofit:2.9.0")

// Тестовые зависимости
testImplementation("junit:junit:4.13.2")
androidTestImplementation("androidx.test:core:1.5.0")
```

### Варианты Сборки (Build Types)

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

// Генерируются варианты: freeDebug, freeRelease, paidDebug, paidRelease
```

### Основные Задачи Gradle

```bash
# Сборка APK (debug / release)
./gradlew assembleDebug
./gradlew assembleRelease

# Установка debug-сборки на подключенное устройство или эмулятор
./gradlew installDebug

# Запуск unit-тестов (на JVM)
./gradlew test

# Запуск инструментальных тестов (на устройстве/эмуляторе)
./gradlew connectedAndroidTest

# Очистка результатов сборки
./gradlew clean

# Показать дерево зависимостей для модуля app
./gradlew app:dependencies
```

---

## Answer (EN)

Gradle is a general build automation tool. In Android projects, it is used together with the Android Gradle Plugin to compile code, manage dependencies, and produce APK/AAB artifacts.

### Project Structure

```
MyApp/
 build.gradle.kts          (project-level)
 settings.gradle.kts
 app/
    build.gradle.kts      (module-level: app module)
```

### Project-level build.gradle.kts

```kotlin
plugins {
    // Example versions; use current stable versions in real projects
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
}
```

### Module-level build.gradle.kts (`Application` module)

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
        debug {
            // debug-specific options (e.g., extra logging)
        }
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
// Implementation dependency: available at compile and runtime
implementation("androidx.core:core-ktx:1.12.0")

// Compile-only: on compile classpath only, not packaged into the final APK/AAB
compileOnly("com.google.android.wearable:wearable:2.9.0")

// API: for library modules, exposes this dependency to consumers' compilation classpath
// (in application modules it behaves effectively like implementation for the app itself)
api("com.squareup.retrofit2:retrofit:2.9.0")

// Test dependencies
testImplementation("junit:junit:4.13.2")
androidTestImplementation("androidx.test:core:1.5.0")
```

### Build Variants (Build Types)

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

// Generates variants: freeDebug, freeRelease, paidDebug, paidRelease
```

### Common Gradle Tasks

```bash
# Build APK (debug / release variants)
./gradlew assembleDebug
./gradlew assembleRelease

# Install debug build on a connected device or emulator
./gradlew installDebug

# Run unit tests (on JVM)
./gradlew test

# Run instrumented tests (on device/emulator)
./gradlew connectedAndroidTest

# Clean build outputs
./gradlew clean

# Show dependency tree for the app module
./gradlew app:dependencies
```

---

## Links

- [Gradle Build Configuration](https://developer.android.com/build)
- [Configure Your Build](https://developer.android.com/studio/build)

---

## Follow-ups

- [[q-android-runtime-art--android--medium]]
- [[q-large-file-upload--android--medium]]
- [[q-room-transactions-dao--android--medium]]

## References

- [Build Variants](https://developer.android.com/build/build-variants)
- [Gradle Build](https://developer.android.com/build)

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]

### Advanced (Harder)
- [[q-build-optimization-gradle--android--medium]] - Build
- [[q-kapt-ksp-migration--android--medium]] - Build
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Build
