---
id: 20251012-122763
title: "Android Build Optimization / Оптимизация сборки Android"
aliases: [Android Build Optimization, Оптимизация сборки Android]
topic: android
subtopics: [build-optimization, gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-gradle-basics--android--easy, q-android-app-bundles--android--easy, q-kotlin-compilation--kotlin--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/build-optimization, android/gradle, build-optimization, gradle, performance, difficulty/medium]
---
# Android Build Optimization

# Question (EN)
> How do you optimize Android build times? What are the best practices and techniques to speed up Gradle builds?

# Вопрос (RU)
> Как оптимизировать время сборки Android? Какие есть best practices и техники для ускорения Gradle-сборок?

---

## Answer (EN)

Build optimization is crucial for developer productivity. Long build times slow down development iterations, testing, and CI/CD pipelines. A comprehensive optimization strategy can reduce build times by 50-80%.

#### 1. **Gradle Configuration Optimization**

**1.1 gradle.properties**

```properties
# Enable parallel build
org.gradle.parallel=true

# Configure JVM heap
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError

# Enable caching
org.gradle.caching=true

# Enable configuration cache (Gradle 7.0+)
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn

# Enable daemon
org.gradle.daemon=true

# Enable file system watching (Gradle 7.0+)
org.gradle.vfs.watch=true

# Android specific
android.enableJetifier=false  # If not using legacy support libraries
android.useAndroidX=true

# Kotlin compiler
kotlin.incremental=true
kotlin.incremental.java=true
kotlin.incremental.js=false

# R8/ProGuard
android.enableR8.fullMode=true
android.enableR8=true

# Build features
android.defaults.buildfeatures.buildconfig=false  # If not needed
android.defaults.buildfeatures.aidl=false
android.defaults.buildfeatures.renderscript=false
android.defaults.buildfeatures.resvalues=false
android.defaults.buildfeatures.shaders=false

# NonTransitiveRClass (AGP 8.0+)
android.nonTransitiveRClass=true
android.nonFinalResIds=true
```

**1.2 Build Script Optimization**

```kotlin
// build.gradle.kts (project level)
buildscript {
    // Use specific versions, not '+' or 'latest'
    val kotlinVersion = "1.9.20"  //  Specific version
    // val kotlinVersion = "1.9.+" //  Dynamic version

    repositories {
        // Order matters - most used first
        google()
        mavenCentral()
    }
}

plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
    id("com.google.dagger.hilt.android") version "2.48" apply false
}

// Dependency resolution strategy
allprojects {
    configurations.all {
        resolutionStrategy {
            // Cache changing modules for build session
            cacheDynamicVersionsFor(0, "seconds")
            cacheChangingModulesFor(0, "seconds")

            // Force specific versions to avoid resolution
            force("com.google.code.gson:gson:2.10.1")
        }
    }
}
```

**1.3 Module-Level Configuration**

```kotlin
// build.gradle.kts (app module)
android {
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        // Only include needed resources
        resourceConfigurations += listOf("en", "ru")

        // Disable unnecessary features
        vectorDrawables.useSupportLibrary = true
    }

    buildTypes {
        debug {
            // Disable optimizations for faster builds
            isMinifyEnabled = false
            isShrinkResources = false

            // Disable Crashlytics in debug
            configure<CrashlyticsExtension> {
                mappingFileUploadEnabled = false
            }
        }

        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // Packaging options
    packaging {
        resources {
            excludes += setOf(
                "META-INF/LICENSE",
                "META-INF/NOTICE",
                "META-INF/*.kotlin_module"
            )
        }
    }

    // Build features - disable what you don't use
    buildFeatures {
        viewBinding = true
        buildConfig = false  // If not needed
        compose = true
        aidl = false
        renderScript = false
        resValues = false
        shaders = false
    }

    // Lint options
    lint {
        checkReleaseBuilds = false  // Only in CI
        abortOnError = false
        checkDependencies = false   // Slow, only in CI
    }

    // Test options
    testOptions {
        unitTests {
            isReturnDefaultValues = true
            isIncludeAndroidResources = false  // Faster, but less accurate
        }
    }

    // Compile options
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"

        // Disable unused compiler features
        freeCompilerArgs = listOf(
            "-Xno-param-assertions",
            "-Xno-call-assertions",
            "-Xno-receiver-assertions"
        )
    }
}
```

#### 2. **Dependency Management**

```kotlin
// Use version catalogs (libs.versions.toml)
[versions]
kotlin = "1.9.20"
compose = "1.5.4"
hilt = "2.48"

[libraries]
androidx-core = { module = "androidx.core:core-ktx", version = "1.12.0" }
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }

[plugins]
android-application = { id = "com.android.application", version = "8.2.0" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }

// In build.gradle.kts
dependencies {
    //  Use implementation instead of api when possible
    implementation(libs.androidx.core)

    //  Avoid large dependencies if not needed
    // implementation("com.google.guava:guava:32.1.3-android")  // 2.7 MB

    //  Use specific modules
    implementation("androidx.compose.ui:ui:1.5.4")  // Only UI, not all Compose

    //  Exclude transitive dependencies you don't need
    implementation("com.squareup.retrofit2:retrofit:2.9.0") {
        exclude(group = "com.squareup.okio", module = "okio")
    }

    //  Use debugImplementation for debug-only deps
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")

    //  Don't duplicate dependencies
    // Check: ./gradlew :app:dependencies
}
```

#### 3. **Modularization**

```kotlin
// Split into modules for parallel compilation

// Project structure:
// :app
// :feature:home
// :feature:profile
// :core:network
// :core:database
// :core:ui

// settings.gradle.kts
include(":app")
include(":feature:home")
include(":feature:profile")
include(":core:network")
include(":core:database")
include(":core:ui")

// Benefits:
// 1. Parallel compilation of modules
// 2. Smaller incremental builds
// 3. Better caching
// 4. Improved code organization

// :feature:home/build.gradle.kts
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.feature.home"
    // ... configuration
}

dependencies {
    implementation(project(":core:network"))
    implementation(project(":core:ui"))
    // ... other dependencies
}
```

#### 4. **Build Cache**

```kotlin
// Enable build cache
// gradle.properties
org.gradle.caching=true

// Configure remote cache (for teams)
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        directory = File(rootDir, ".gradle/build-cache")
        removeUnusedEntriesAfterDays = 30
    }

    remote<HttpBuildCache> {
        url = uri("https://your-build-cache-server.com/cache/")
        credentials {
            username = System.getenv("CACHE_USERNAME")
            password = System.getenv("CACHE_PASSWORD")
        }
        isEnabled = true
        isPush = System.getenv("CI") == "true"  // Only push from CI
    }
}

// Make tasks cacheable
tasks.register<MyCustomTask>("myTask") {
    inputs.files(fileTree("src"))
    outputs.file("$buildDir/output.txt")

    // Enable caching
    outputs.cacheIf { true }
}
```

#### 5. **Kotlin Compilation Optimization**

```kotlin
// build.gradle.kts (app module)
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        // Use parallel compilation
        freeCompilerArgs += "-Xbackend-threads=0"  // Use all CPU cores

        // Enable incremental compilation
        incremental = true

        // Disable verbose output
        verbose = false

        // Use K2 compiler (experimental, faster)
        // languageVersion = "2.0"

        // Optimize for build speed in debug
        if (project.gradle.startParameter.taskNames.any { it.contains("Debug") }) {
            freeCompilerArgs += listOf(
                "-Xno-param-assertions",
                "-Xno-call-assertions",
                "-Xno-receiver-assertions"
            )
        }
    }
}

// Kapt optimization (if using annotation processors)
kapt {
    useBuildCache = true
    correctErrorTypes = true

    // Enable parallel execution
    arguments {
        arg("key", "value")
    }

    // Limit workers
    javacOptions {
        option("-Xmaxerrs", 500)
    }
}

// KSP (faster alternative to Kapt)
plugins {
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
}

// Use KSP instead of Kapt when possible
dependencies {
    ksp(libs.hilt.compiler)      //  Faster
    // kapt(libs.hilt.compiler)  //  Slower
}
```

#### 6. **Profiling and Analysis**

**6.1 Build Scan**

```bash
# Generate build scan
./gradlew build --scan

# Outputs URL to detailed build report
# Shows:
# - Task execution times
# - Dependency resolution
# - Configuration time
# - Compilation time
# - Cache effectiveness
```

**6.2 Profile Report**

```bash
# Generate profile report
./gradlew assembleDebug --profile

# Output: build/reports/profile/profile-*.html
# Analyze:
# - Slowest tasks
# - Configuration vs execution time
# - Task dependencies
```

**6.3 Custom Profiling**

```kotlin
// build.gradle.kts
gradle.taskGraph.whenReady {
    val startTime = System.currentTimeMillis()

    allTasks.forEach { task ->
        task.doFirst {
            task.ext.set("startTime", System.currentTimeMillis())
        }

        task.doLast {
            val start = task.ext.get("startTime") as Long
            val duration = System.currentTimeMillis() - start

            if (duration > 1000) {  // Log tasks > 1 second
                println("Task ${task.path} took ${duration}ms")
            }
        }
    }
}
```

#### 7. **CI/CD Optimization**

```yaml
# .github/workflows/android-optimized.yml
name: Android Optimized Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          cache: 'gradle'  #  Enable caching

      - name: Cache Gradle dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
          restore-keys: |
            ${{ runner.os }}-gradle-

      - name: Validate Gradle wrapper
        uses: gradle/wrapper-validation-action@v1

      - name: Build with Gradle
        run: ./gradlew assembleDebug --parallel --build-cache --configuration-cache

      #  Only run necessary tasks
      - name: Run unit tests (only changed modules)
        run: ./gradlew testDebugUnitTest --parallel
```

#### 8. **Development Workflow Optimization**

```bash
# Use specific tasks instead of building everything
./gradlew :app:assembleDebug          #  Only app module
# ./gradlew build                      #  Builds all modules

# Use --dry-run to see what will execute
./gradlew assembleDebug --dry-run

# Use continuous build for auto-rebuild
./gradlew assembleDebug --continuous

# Skip tests during development
./gradlew assembleDebug -x test

# Assemble specific variant
./gradlew assembleDevelopmentDebug    # Faster than all variants

# Parallel execution
./gradlew clean assembleDebug --parallel --max-workers=8
```

#### 9. **Quick Wins Checklist**

```kotlin
//  Enable in gradle.properties
org.gradle.parallel=true              // 20-40% faster
org.gradle.caching=true               // 30-50% faster (incremental)
org.gradle.configuration-cache=true   // 10-30% faster
org.gradle.vfs.watch=true            // 5-15% faster
org.gradle.jvmargs=-Xmx4096m         // Prevent OOM, faster GC

//  In build.gradle.kts
android.nonTransitiveRClass=true      // Faster R class generation
kapt.useBuildCache=true              // Cache annotation processing
ksp instead of kapt                  // 2x faster annotation processing

//  Development workflow
Use specific build variants          // Don't build all
Modularize project                   // Parallel compilation
Disable lint in debug                // Run only in CI
Use build scans                      // Identify bottlenecks

//  Dependencies
Remove unused dependencies           // Less to compile
Use implementation over api          // Smaller recompilation scope
Version catalog                      // Faster resolution
```

### Build Time Comparison

```kotlin
data class BuildMetrics(
    val scenario: String,
    val cleanBuild: Int,    // seconds
    val incrementalBuild: Int
)

val buildComparison = listOf(
    BuildMetrics("Unoptimized", 180, 45),
    BuildMetrics("gradle.properties optimized", 120, 30),
    BuildMetrics("+ Modularization", 90, 15),
    BuildMetrics("+ Build cache", 60, 5),
    BuildMetrics("+ All optimizations", 40, 3)
)

// 78% clean build improvement
// 93% incremental build improvement
```

### Common Issues

**1. Configuration time too long:**
```kotlin
//  Don't resolve dependencies at configuration time
val myDeps = configurations.implementation.resolve()  // Slow!

//  Do it at execution time
tasks.register("myTask") {
    doLast {
        val myDeps = configurations.implementation.resolve()  // Fast
    }
}
```

**2. Too many variants:**
```kotlin
//  Excessive build types and flavors
productFlavors {
    create("dev") { ... }
    create("staging") { ... }
    create("prod") { ... }
}
buildTypes {
    debug { ... }
    release { ... }
}
// = 6 variants, slow

//  Minimize variants or use build parameters
```

**3. Large dependencies:**
```bash
# Analyze dependency sizes
./gradlew :app:dependencies --configuration releaseRuntimeClasspath

# Find largest dependencies
./gradlew :app:dependencies | grep -E "\+---|\---" | sort | uniq -c | sort -rn
```

---

## Ответ (RU)

Оптимизация сборки критична для продуктивности разработчиков. Комплексная стратегия может сократить время на 50-80%.

#### Ключевые области:

**1. Конфигурация Gradle:**
```properties
org.gradle.parallel=true              # 20-40% быстрее
org.gradle.caching=true               # 30-50% быстрее
org.gradle.configuration-cache=true   # 10-30% быстрее
org.gradle.jvmargs=-Xmx4096m         # Больше памяти
```

**2. Управление зависимостями:**
- Используйте конкретные версии (не '+')
- implementation вместо api
- Version catalogs
- Удаляйте неиспользуемые зависимости

**3. Модуляризация:**
- Разделение на модули
- Параллельная компиляция
- Меньший scope перекомпиляции
- Улучшенное кэширование

**4. Build Cache:**
- Локальный кэш
- Удалённый кэш для команд
- Кэширование задач

**5. Kotlin оптимизации:**
- Инкрементальная компиляция
- Параллельная компиляция
- KSP вместо Kapt (2x быстрее)

**6. Профилирование:**
```bash
./gradlew build --scan      # Детальный отчёт
./gradlew build --profile   # HTML профиль
```

**7. CI/CD оптимизации:**
- Кэширование в actions
- Параллельная сборка
- Только необходимые задачи

**8. Быстрые победы:**
- Отключите lint в debug
- Минимизируйте build варианты
- Используйте конкретные задачи
- Модульная сборка

### Сравнение времени:

| Сценарий | Clean | Incremental |
|----------|-------|-------------|
| Без оптимизаций | 180s | 45s |
| С оптимизациями | 40s | 3s |
| **Улучшение** | **78%** | **93%** |

Систематическая оптимизация всех областей даёт максимальный эффект.

---

## Related Questions

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Performance, Build
- [[q-build-optimization-gradle--gradle--medium]] - Performance, Build
- [[q-gradle-build-system--android--medium]] - Build, Ui
- [[q-main-causes-ui-lag--android--medium]] - Performance, Ui
- [[q-performance-optimization-android--android--medium]] - Performance

### Advanced (Harder)
- [[q-kotlin-dsl-builders--kotlin--hard]] - Build, Ui
- [[q-compose-performance-optimization--android--hard]] - Performance
