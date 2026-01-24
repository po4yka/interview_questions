---
id: kotlin-kmp-009
title: "KMP Gradle Configuration / Настройка Gradle для KMP"
aliases: [KMP Gradle Setup, Multiplatform Build Configuration, KMP Build Script]
topic: kotlin
subtopics: [kmp, multiplatform, gradle, build]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin]
created: 2026-01-23
updated: 2026-01-23
tags: [kotlin, kmp, multiplatform, gradle, build, difficulty/medium]
---

# Question (EN)
> How do you configure Gradle for Kotlin Multiplatform projects?

# Vopros (RU)
> Как настроить Gradle для проектов Kotlin Multiplatform?

## Answer (EN)

Gradle configuration is central to KMP projects. Proper setup determines target platforms, dependencies, and build outputs.

### Project Structure

```
my-kmp-project/
  build.gradle.kts           # Root build file
  settings.gradle.kts        # Module configuration
  gradle.properties          # Gradle settings
  gradle/
    libs.versions.toml       # Version catalog
  shared/
    build.gradle.kts         # KMP module
  androidApp/
    build.gradle.kts         # Android app
  iosApp/
    iosApp.xcodeproj         # iOS project (Xcode)
```

### Root build.gradle.kts

```kotlin
// build.gradle.kts (root)
plugins {
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.kotlin.serialization) apply false
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.compose.multiplatform) apply false
    alias(libs.plugins.sqldelight) apply false
}
```

### settings.gradle.kts

```kotlin
// settings.gradle.kts
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyKmpProject"

include(":shared")
include(":androidApp")
// iOS app is managed by Xcode, not included here
```

### Version Catalog (libs.versions.toml)

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.0.0"
agp = "8.2.0"
compose-multiplatform = "1.6.0"
coroutines = "1.8.0"
ktor = "3.0.0"
sqldelight = "2.0.0"
koin = "3.5.0"
serialization = "1.6.3"

# Android specific
androidx-lifecycle = "2.7.0"
androidx-activity = "1.8.2"

[libraries]
# Kotlin
kotlin-test = { module = "org.jetbrains.kotlin:kotlin-test", version.ref = "kotlin" }

# Coroutines
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
kotlinx-coroutines-android = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-android", version.ref = "coroutines" }
kotlinx-coroutines-test = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-test", version.ref = "coroutines" }

# Serialization
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "serialization" }

# Ktor
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
ktor-serialization-kotlinx-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }
ktor-client-android = { module = "io.ktor:ktor-client-android", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }
ktor-client-logging = { module = "io.ktor:ktor-client-logging", version.ref = "ktor" }

# SQLDelight
sqldelight-runtime = { module = "app.cash.sqldelight:runtime", version.ref = "sqldelight" }
sqldelight-coroutines = { module = "app.cash.sqldelight:coroutines-extensions", version.ref = "sqldelight" }
sqldelight-android-driver = { module = "app.cash.sqldelight:android-driver", version.ref = "sqldelight" }
sqldelight-native-driver = { module = "app.cash.sqldelight:native-driver", version.ref = "sqldelight" }

# Koin
koin-core = { module = "io.insert-koin:koin-core", version.ref = "koin" }
koin-android = { module = "io.insert-koin:koin-android", version.ref = "koin" }

# AndroidX
androidx-lifecycle-viewmodel = { module = "androidx.lifecycle:lifecycle-viewmodel-ktx", version.ref = "androidx-lifecycle" }
androidx-activity-compose = { module = "androidx.activity:activity-compose", version.ref = "androidx-activity" }

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
compose-multiplatform = { id = "org.jetbrains.compose", version.ref = "compose-multiplatform" }
sqldelight = { id = "app.cash.sqldelight", version.ref = "sqldelight" }
```

### Shared Module Configuration

```kotlin
// shared/build.gradle.kts
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.android.library)
    alias(libs.plugins.compose.multiplatform)
    alias(libs.plugins.sqldelight)
}

kotlin {
    // Android target
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }

    // iOS targets
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "SharedKit"
            isStatic = true

            // Export dependencies to iOS
            export(libs.kotlinx.coroutines.core)
        }
    }

    // Desktop target (optional)
    jvm("desktop") {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }

    // Apply default hierarchy template (recommended)
    applyDefaultHierarchyTemplate()

    sourceSets {
        // Common code
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)

            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)

            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.kotlinx.json)
            implementation(libs.ktor.client.logging)

            implementation(libs.sqldelight.runtime)
            implementation(libs.sqldelight.coroutines)

            implementation(libs.koin.core)
        }

        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }

        // Android-specific
        androidMain.dependencies {
            implementation(libs.ktor.client.android)
            implementation(libs.sqldelight.android.driver)
            implementation(libs.koin.android)
            implementation(libs.kotlinx.coroutines.android)

            implementation(compose.preview)
            implementation(libs.androidx.activity.compose)
            implementation(libs.androidx.lifecycle.viewmodel)
        }

        // iOS-specific
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
            implementation(libs.sqldelight.native.driver)
        }

        // Desktop-specific
        val desktopMain by getting {
            dependencies {
                implementation(compose.desktop.currentOs)
                implementation(libs.ktor.client.cio)
                implementation(libs.sqldelight.sqlite.driver)
            }
        }
    }
}

// Android configuration
android {
    namespace = "com.example.shared"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

// SQLDelight configuration
sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.db")
            generateAsync.set(true)
        }
    }
}

// Compose configuration
compose {
    kotlinCompilerPlugin.set(dependencies.compiler.forKotlin("2.0.0"))
}
```

### gradle.properties

```properties
# gradle.properties
org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8

# Kotlin
kotlin.code.style=official
kotlin.native.binary.memoryModel=experimental
kotlin.mpp.stability.nowarn=true
kotlin.mpp.androidSourceSetLayoutVersion=2

# Android
android.useAndroidX=true
android.nonTransitiveRClass=true

# Compose
org.jetbrains.compose.experimental.uikit.enabled=true

# Enable parallel builds
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
```

### Custom Source Sets

```kotlin
// For intermediate source sets
kotlin {
    sourceSets {
        // Create mobile-specific source set
        val mobileMain by creating {
            dependsOn(commonMain.get())
        }

        androidMain.get().dependsOn(mobileMain)
        iosMain.get().dependsOn(mobileMain)

        // Native-specific intermediate
        val nativeMain by creating {
            dependsOn(commonMain.get())
        }

        iosMain.get().dependsOn(nativeMain)
        // Add other native targets here
    }
}
```

### iOS Framework Tasks

```kotlin
// Custom task for iOS framework
tasks.register("assembleXCFramework") {
    dependsOn(
        "linkReleaseFrameworkIosArm64",
        "linkReleaseFrameworkIosSimulatorArm64"
    )

    doLast {
        exec {
            commandLine(
                "xcodebuild", "-create-xcframework",
                "-framework", "build/bin/iosArm64/releaseFramework/SharedKit.framework",
                "-framework", "build/bin/iosSimulatorArm64/releaseFramework/SharedKit.framework",
                "-output", "build/xcframework/SharedKit.xcframework"
            )
        }
    }
}
```

### Common Build Tasks

```bash
# Build all targets
./gradlew build

# Build Android only
./gradlew :shared:assembleRelease

# Build iOS framework
./gradlew :shared:linkReleaseFrameworkIosArm64

# Run tests
./gradlew :shared:allTests
./gradlew :shared:iosSimulatorArm64Test

# Clean
./gradlew clean
```

### Troubleshooting

```kotlin
// Debug Kotlin/Native issues
kotlin {
    targets.withType<KotlinNativeTarget> {
        binaries.all {
            freeCompilerArgs += listOf(
                "-Xruntime-logs=gc=info",
                "-Xg0"  // Enable debug info
            )
        }
    }
}

// Fix duplicate class issues
android {
    packagingOptions {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
            excludes += "/META-INF/versions/9/previous-compilation-data.bin"
        }
    }
}
```

---

## Otvet (RU)

Конфигурация Gradle является центральной для KMP проектов. Правильная настройка определяет целевые платформы, зависимости и результаты сборки.

### Структура проекта

```
my-kmp-project/
  build.gradle.kts           # Корневой build файл
  settings.gradle.kts        # Конфигурация модулей
  gradle.properties          # Настройки Gradle
  gradle/
    libs.versions.toml       # Каталог версий
  shared/
    build.gradle.kts         # KMP модуль
  androidApp/
    build.gradle.kts         # Android приложение
  iosApp/
    iosApp.xcodeproj         # iOS проект (Xcode)
```

### Каталог версий (libs.versions.toml)

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.0.0"
agp = "8.2.0"
compose-multiplatform = "1.6.0"
coroutines = "1.8.0"
ktor = "3.0.0"
sqldelight = "2.0.0"

[libraries]
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "serialization" }
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-android = { module = "io.ktor:ktor-client-android", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
android-library = { id = "com.android.library", version.ref = "agp" }
compose-multiplatform = { id = "org.jetbrains.compose", version.ref = "compose-multiplatform" }
```

### Конфигурация Shared модуля

```kotlin
// shared/build.gradle.kts
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.android.library)
    alias(libs.plugins.compose.multiplatform)
}

kotlin {
    // Android таргет
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }

    // iOS таргеты
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "SharedKit"
            isStatic = true
        }
    }

    // Применить шаблон иерархии по умолчанию (рекомендуется)
    applyDefaultHierarchyTemplate()

    sourceSets {
        // Общий код
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)

            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.ktor.client.core)
        }

        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }

        // Android-специфичное
        androidMain.dependencies {
            implementation(libs.ktor.client.android)
            implementation(compose.preview)
        }

        // iOS-специфичное
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }
    }
}

// Android конфигурация
android {
    namespace = "com.example.shared"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
```

### gradle.properties

```properties
# gradle.properties
org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8

# Kotlin
kotlin.code.style=official
kotlin.mpp.stability.nowarn=true
kotlin.mpp.androidSourceSetLayoutVersion=2

# Android
android.useAndroidX=true
android.nonTransitiveRClass=true

# Включить параллельные сборки
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
```

### Кастомные Source Sets

```kotlin
// Для промежуточных source sets
kotlin {
    sourceSets {
        // Создать mobile-специфичный source set
        val mobileMain by creating {
            dependsOn(commonMain.get())
        }

        androidMain.get().dependsOn(mobileMain)
        iosMain.get().dependsOn(mobileMain)
    }
}
```

### Общие задачи сборки

```bash
# Собрать все таргеты
./gradlew build

# Собрать только Android
./gradlew :shared:assembleRelease

# Собрать iOS фреймворк
./gradlew :shared:linkReleaseFrameworkIosArm64

# Запустить тесты
./gradlew :shared:allTests

# Очистить
./gradlew clean
```

---

## Follow-ups

- How do you configure Gradle for different build variants in KMP?
- What are the differences between static and dynamic iOS frameworks?
- How do you optimize KMP build times?
- How do you configure CI/CD for KMP projects?

## Dopolnitelnye Voprosy (RU)

- Как настроить Gradle для разных build variants в KMP?
- В чём различия между статическими и динамическими iOS фреймворками?
- Как оптимизировать время сборки KMP?
- Как настроить CI/CD для KMP проектов?

## References

- [KMP Gradle DSL Reference](https://kotlinlang.org/docs/multiplatform-dsl-reference.html)
- [Gradle Version Catalog](https://docs.gradle.org/current/userguide/platforms.html)

## Ssylki (RU)

- [[c-kotlin]]
- [Справочник KMP Gradle DSL](https://kotlinlang.org/docs/multiplatform-dsl-reference.html)

## Related Questions

- [[q-kmp-project-structure--kmp--medium]]
- [[q-kmp-testing--kmp--medium]]
