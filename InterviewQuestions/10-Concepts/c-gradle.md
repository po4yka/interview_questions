---
id: "20251025-140200"
title: "Gradle / Gradle"
aliases: ["Build Automation", "Gradle Build System", "Gradle", "Автоматизация сборки", "Система сборки Gradle"]
summary: "Build automation tool for Android and JVM projects using Groovy or Kotlin DSL"
topic: "android"
subtopics: ["build-system", "gradle", "kotlin-dsl"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["android", "automation", "build-system", "concept", "difficulty/medium", "gradle", "groovy", "kotlin-dsl"]
---

# Gradle / Gradle

## Summary (EN)

Gradle is a powerful, flexible build automation tool used for Android and JVM-based projects. It manages dependencies, compiles code, runs tests, and packages applications using build scripts written in Groovy or Kotlin DSL. Gradle uses a directed acyclic graph (DAG) of tasks, supports incremental builds, and provides extensive customization through plugins. Android projects use the Android Gradle Plugin (AGP) to add Android-specific build capabilities like APK/AAB generation, resource merging, and build variants.

## Краткое Описание (RU)

Gradle - это мощный, гибкий инструмент автоматизации сборки, используемый для Android и JVM-проектов. Управляет зависимостями, компилирует код, запускает тесты и упаковывает приложения с помощью скриптов сборки, написанных на Groovy или Kotlin DSL. Gradle использует направленный ациклический граф (DAG) задач, поддерживает инкрементальные сборки и предоставляет обширные возможности настройки через плагины. Android-проекты используют Android Gradle Plugin (AGP) для добавления специфичных для Android возможностей сборки, таких как генерация APK/AAB, слияние ресурсов и варианты сборки.

## Key Points (EN)

- **Build Scripts**: `build.gradle.kts` (Kotlin DSL) or `build.gradle` (Groovy DSL)
- **Project Structure**: Multi-module projects with root and module-level scripts
- **Dependency Management**: Maven Central, Google Maven, custom repositories
- **Task-based**: Everything is a task (compile, test, assemble, etc.)
- **Incremental Builds**: Only rebuilds changed parts of the project
- **Build Variants**: Combine build types (debug/release) with product flavors
- **Plugins**: Android, Kotlin, Java, custom plugins extend functionality
- **Build Cache**: Local and remote caching for faster builds
- **Configuration Cache**: Speeds up subsequent builds by caching configuration
- **Version Catalogs**: Centralized dependency management (libs.versions.toml)

## Ключевые Моменты (RU)

- **Скрипты сборки**: `build.gradle.kts` (Kotlin DSL) или `build.gradle` (Groovy DSL)
- **Структура проекта**: Многомодульные проекты с корневыми и модульными скриптами
- **Управление зависимостями**: Maven Central, Google Maven, пользовательские репозитории
- **Основанный на задачах**: Всё является задачей (compile, test, assemble и т.д.)
- **Инкрементальные сборки**: Пересобирает только изменённые части проекта
- **Варианты сборки**: Комбинация типов сборки (debug/release) с product flavors
- **Плагины**: Android, Kotlin, Java, пользовательские плагины расширяют функциональность
- **Кэш сборки**: Локальное и удалённое кэширование для более быстрых сборок
- **Кэш конфигурации**: Ускоряет последующие сборки за счёт кэширования конфигурации
- **Version Catalogs**: Централизованное управление зависимостями (libs.versions.toml)

## Use Cases

### When to Use

- **Android projects**: Standard build tool for Android development
- **Multi-module projects**: Excellent support for modular architecture
- **Complex build logic**: Custom tasks, build variants, conditional compilation
- **CI/CD pipelines**: Automated builds, testing, deployment
- **Dependency management**: Transitive dependencies, version resolution
- **Code generation**: Annotation processing, code generation tasks
- **Testing**: Unit tests, instrumentation tests, code coverage

### When to Avoid

- **Simple scripts**: Overkill for trivial automation (use bash/python)
- **Non-JVM languages**: Better alternatives exist for other ecosystems
- **Build performance critical**: Can be slow for very large monorepos (consider Bazel)

## Trade-offs

**Pros**:
- **Flexible**: Highly customizable build logic
- **Incremental builds**: Fast rebuilds by only processing changes
- **Dependency management**: Transitive dependency resolution, conflict handling
- **Plugin ecosystem**: Rich ecosystem of community and official plugins
- **Multi-project builds**: First-class support for modular projects
- **Kotlin DSL**: Type-safe, IDE-friendly build scripts
- **Build cache**: Remote cache sharing across teams
- **Parallel execution**: Builds modules in parallel when possible

**Cons**:
- **Complexity**: Steep learning curve, configuration can be complex
- **Build times**: Can be slow for large projects (though improving)
- **Debugging**: Build script errors can be cryptic
- **Breaking changes**: AGP updates can introduce breaking changes
- **Memory usage**: Can consume significant memory for large projects
- **Configuration time**: Build configuration can take time before actual build starts

## Gradle Project Structure

### Android Project Files

```
MyApp/
├── build.gradle.kts                    # Root build script
├── settings.gradle.kts                  # Project settings
├── gradle.properties                    # Gradle properties
├── gradle/
│   ├── libs.versions.toml              # Version catalog
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── app/
│   ├── build.gradle.kts                # Module build script
│   ├── proguard-rules.pro
│   └── src/
│       ├── main/
│       ├── debug/
│       └── release/
└── library-module/
    └── build.gradle.kts
```

### Root build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.hilt) apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.layout.buildDirectory)
}
```

### Module build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.kapt)
    alias(libs.plugins.hilt)
}

android {
    namespace = "com.example.myapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // Build config fields
        buildConfigField("String", "API_URL", "\"https://api.example.com\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
        debug {
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
    }

    flavorDimensions += "environment"
    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            buildConfigField("String", "API_URL", "\"https://dev.api.example.com\"")
        }
        create("prod") {
            dimension = "environment"
            buildConfigField("String", "API_URL", "\"https://api.example.com\"")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = libs.versions.compose.compiler.get()
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)

    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.material3)

    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)

    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.test.ext.junit)
}
```

## Version Catalogs (libs.versions.toml)

```toml
[versions]
agp = "8.2.0"
kotlin = "1.9.20"
compose-bom = "2024.01.00"
compose-compiler = "1.5.5"
hilt = "2.48"

[libraries]
androidx-core-ktx = { group = "androidx.core", name = "core-ktx", version = "1.12.0" }
androidx-lifecycle-runtime-ktx = { group = "androidx.lifecycle", name = "lifecycle-runtime-ktx", version = "2.6.2" }
androidx-activity-compose = { group = "androidx.activity", name = "activity-compose", version = "1.8.2" }

androidx-compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
androidx-compose-ui = { group = "androidx.compose.ui", name = "ui" }
androidx-compose-material3 = { group = "androidx.compose.material3", name = "material3" }

hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }

junit = { group = "junit", name = "junit", version = "4.13.2" }
androidx-test-ext-junit = { group = "androidx.test.ext", name = "junit", version = "1.1.5" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-kapt = { id = "org.jetbrains.kotlin.kapt", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
```

## Build Variants

### Build Types + Product Flavors

```kotlin
// Generates: devDebug, devRelease, prodDebug, prodRelease
android {
    buildTypes {
        debug { /* ... */ }
        release { /* ... */ }
    }

    flavorDimensions += listOf("environment", "api")

    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
        }
        create("prod") {
            dimension = "environment"
        }
        create("v1") {
            dimension = "api"
            buildConfigField("int", "API_VERSION", "1")
        }
        create("v2") {
            dimension = "api"
            buildConfigField("int", "API_VERSION", "2")
        }
    }
}
// Generates: devV1Debug, devV1Release, devV2Debug, devV2Release, etc.
```

### Source Sets

```
app/src/
├── main/              # Common code
├── debug/             # Debug-specific
├── release/           # Release-specific
├── dev/               # Dev flavor
├── prod/              # Prod flavor
├── devDebug/          # Dev + Debug variant
└── prodRelease/       # Prod + Release variant
```

## Dependency Management

### Dependency Configurations

```kotlin
dependencies {
    // Compile and runtime
    implementation(libs.retrofit)

    // Compile only (not in APK)
    compileOnly(libs.annotations)

    // Runtime only
    runtimeOnly(libs.sqlite)

    // API (exposes to consumers)
    api(libs.kotlin.stdlib)

    // Annotation processors
    kapt(libs.hilt.compiler)
    ksp(libs.room.compiler)

    // Test dependencies
    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso)

    // Variant-specific
    debugImplementation(libs.leakcanary)
    releaseImplementation(libs.firebase.crashlytics)
}
```

### Dependency Resolution

```kotlin
configurations.all {
    resolutionStrategy {
        // Force specific version
        force("org.jetbrains.kotlin:kotlin-stdlib:1.9.20")

        // Fail on version conflict
        failOnVersionConflict()

        // Prefer modules over dynamic versions
        preferProjectModules()

        // Cache for 24 hours
        cacheDynamicVersionsFor(24, "hours")
    }
}
```

## Custom Tasks

```kotlin
// Simple task
tasks.register("hello") {
    doLast {
        println("Hello, Gradle!")
    }
}

// Task with type
tasks.register<Copy>("copyFiles") {
    from("src/assets")
    into("build/processed-assets")
}

// Custom task class
abstract class GenerateVersionTask : DefaultTask() {
    @get:Input
    abstract val versionName: Property<String>

    @get:OutputFile
    abstract val outputFile: RegularFileProperty

    @TaskAction
    fun generate() {
        outputFile.get().asFile.writeText(
            "VERSION = \"${versionName.get()}\""
        )
    }
}

tasks.register<GenerateVersionTask>("generateVersion") {
    versionName.set("1.0.0")
    outputFile.set(layout.buildDirectory.file("version.txt"))
}
```

## Build Performance

### gradle.properties

```properties
# Parallel execution
org.gradle.parallel=true

# Configure JVM
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8

# Daemon
org.gradle.daemon=true

# Configuration cache
org.gradle.configuration-cache=true

# Build cache
org.gradle.caching=true

# Kotlin incremental compilation
kotlin.incremental=true
kotlin.incremental.js=true

# Android build features
android.useAndroidX=true
android.enableJetifier=false
android.nonTransitiveRClass=true
android.defaults.buildfeatures.buildconfig=false
android.defaults.buildfeatures.aidl=false
android.defaults.buildfeatures.renderscript=false
android.defaults.buildfeatures.resvalues=false
android.defaults.buildfeatures.shaders=false
```

### Remote Build Cache

```kotlin
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        directory = File(rootDir, "build-cache")
        removeUnusedEntriesAfterDays = 7
    }
    remote<HttpBuildCache> {
        isEnabled = true
        url = uri("https://build-cache.example.com")
        isPush = System.getenv("CI") == "true"
    }
}
```

## Common Gradle Commands

```bash
# Build debug APK
./gradlew assembleDebug

# Build release APK
./gradlew assembleRelease

# Install debug APK
./gradlew installDebug

# Run unit tests
./gradlew test

# Run instrumentation tests
./gradlew connectedAndroidTest

# Clean build
./gradlew clean

# List tasks
./gradlew tasks

# Dependency tree
./gradlew app:dependencies

# Build with stacktrace
./gradlew assembleDebug --stacktrace

# Build with info logs
./gradlew assembleDebug --info

# Build specific variant
./gradlew assembleProdRelease

# Profile build
./gradlew assembleDebug --profile --scan
```

## Multi-Module Projects

### settings.gradle.kts

```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyApp"
include(":app")
include(":feature:home")
include(":feature:profile")
include(":core:network")
include(":core:database")
include(":core:ui")
```

### Module Dependencies

```kotlin
// app/build.gradle.kts
dependencies {
    implementation(project(":feature:home"))
    implementation(project(":feature:profile"))
    implementation(project(":core:network"))
}

// feature:home/build.gradle.kts
dependencies {
    implementation(project(":core:network"))
    implementation(project(":core:ui"))
}
```

## Best Practices

1. **Use Version Catalogs** - Centralize dependency versions
2. **Enable build cache** - Significantly speeds up builds
3. **Modularize projects** - Faster incremental builds, better separation
4. **Use Kotlin DSL** - Type-safe, IDE-friendly
5. **Minimize custom tasks** - Prefer plugins when possible
6. **Configure JVM heap** - Prevent OOM errors
7. **Use configuration cache** - Faster configuration phase
8. **Avoid dynamic versions** - `+` versions break reproducibility
9. **Profile builds** - Use `--profile` and `--scan` to identify bottlenecks
10. **Keep AGP updated** - Performance improvements in newer versions

## Common Issues

### Dependency Conflicts

```kotlin
// Exclude transitive dependency
implementation(libs.retrofit) {
    exclude(group = "com.squareup.okhttp3", module = "okhttp")
}

// Force version
configurations.all {
    resolutionStrategy {
        force("com.squareup.okhttp3:okhttp:4.12.0")
    }
}
```

### Build Cache Misses

```bash
# Check why task wasn't cached
./gradlew assembleDebug --build-cache -Dorg.gradle.caching.debug=true
```

### Memory Issues

```properties
# Increase heap size
org.gradle.jvmargs=-Xmx6g -XX:MaxMetaspaceSize=512m
```

## Related Concepts

- [[c-dependency-injection]] - Hilt/Dagger setup in Gradle
- [[c-kotlin]] - Kotlin Gradle Plugin configuration
- [[c-build-variants]] - Build types and product flavors
- [[c-proguard]] - Code shrinking and obfuscation
- [[c-signing]] - APK signing configuration
- [[c-testing]] - Test configuration in Gradle
- [[c-ci-cd]] - Gradle in CI/CD pipelines

## References

- [Gradle Documentation](https://docs.gradle.org/)
- [Android Gradle Plugin Documentation](https://developer.android.com/build)
- [Gradle User Manual](https://docs.gradle.org/current/userguide/userguide.html)
- [Kotlin DSL Primer](https://docs.gradle.org/current/userguide/kotlin_dsl.html)
- [Version Catalogs](https://docs.gradle.org/current/userguide/platforms.html)
- [Build Performance](https://developer.android.com/build/optimize-your-build)
- [Gradle Build Scans](https://scans.gradle.com/)
