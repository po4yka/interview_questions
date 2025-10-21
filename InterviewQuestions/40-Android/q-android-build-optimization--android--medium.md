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
status: reviewed
moc: moc-android
related: [q-gradle-basics--android--easy, q-android-app-bundles--android--easy, q-kotlin-compilation--kotlin--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/build-optimization, android/gradle, build-optimization, gradle, performance, difficulty/medium]
---
# Question (EN)
> How do you optimize Android build times? What are the best practices and techniques to speed up Gradle builds?

# Вопрос (RU)
> Как оптимизировать время сборки Android? Какие есть best practices и техники для ускорения Gradle-сборок?

---

## Answer (EN)


**1. Gradle Configuration Optimization**

**gradle.properties:**
```properties
# Enable parallel build - uses multiple CPU cores for independent tasks
org.gradle.parallel=true

# Configure JVM heap - prevents OutOfMemoryError, optimizes garbage collection
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# Enable caching - stores build outputs to avoid recompilation
org.gradle.caching=true

# Enable configuration cache - caches configuration phase (10-30% faster)
org.gradle.configuration-cache=true

# Enable daemon - keeps Gradle process alive between builds
org.gradle.daemon=true

# Enable file system watching - detects file changes without polling
org.gradle.vfs.watch=true

# Android specific
android.enableJetifier=false              # Disable if fully migrated to AndroidX
android.useAndroidX=true                  # Use AndroidX instead of Support Library

# Kotlin compiler
kotlin.incremental=true                   # Only recompile changed Kotlin files
kotlin.incremental.java=true              # Track Java changes affecting Kotlin

# R8/ProGuard
android.enableR8.fullMode=true            # Enable full R8 optimization
android.enableR8=true                     # Enable R8 code shrinking

# Build features - disable unused features to reduce build time
android.defaults.buildfeatures.buildconfig=false    # Disable BuildConfig generation
android.defaults.buildfeatures.aidl=false           # Disable AIDL processing
android.defaults.buildfeatures.renderscript=false   # Disable RenderScript processing

# NonTransitiveRClass
android.nonTransitiveRClass=true          # Generate non-transitive R classes (faster compilation)
android.nonFinalResIds=true               # Make resource IDs non-final (faster R class generation)
```

**How it works:**
- **Parallel execution**: Gradle analyzes task dependencies and runs independent tasks simultaneously using multiple CPU cores
- **Build cache**: Stores task outputs with content hashes, skips execution if inputs unchanged
- **Configuration cache**: Serializes configuration phase results, skips re-evaluation on subsequent builds
- **VFS watching**: Uses native file system events instead of periodic directory scanning
- **Non-transitive R classes**: Each module gets its own R class, reducing compilation dependencies
- **Incremental compilation**: Only recompiles changed files and their dependents

**Build Script Optimization:**
```kotlin
// build.gradle.kts (project level)
buildscript {
    val kotlinVersion = "1.9.20"  // Specific version, not '+'

    repositories {
        google()  // Most used first
        mavenCentral()
    }
}

plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
}

// Dependency resolution strategy
allprojects {
    configurations.all {
        resolutionStrategy {
            // Don't cache dynamic versions (e.g., "1.9.+") to get latest
            cacheDynamicVersionsFor(0, "seconds")
            // Don't cache changing modules to get latest snapshots
            cacheChangingModulesFor(0, "seconds")
            // Force specific version to avoid conflicts
            force("com.google.code.gson:gson:2.10.1")
        }
    }
}
```

**Explanation:**
- **Specific versions**: Avoid `"1.9.+"` or `"latest"` - they cause dependency resolution overhead
- **Repository order**: Place most-used repositories first to reduce lookup time
- **Resolution strategy**: Prevents version conflicts and reduces resolution time
- **apply false**: Plugins are applied in modules, not at project level

**2. Module-Level Configuration**

```kotlin
// build.gradle.kts (app module)
android {
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34

        // Only include needed resources - reduces APK size and build time
        resourceConfigurations += listOf("en", "ru")

        // Use support library for vector drawables - faster than native
        vectorDrawables.useSupportLibrary = true
    }

    buildTypes {
        debug {
            // Disable optimizations for faster debug builds
            isMinifyEnabled = false
            isShrinkResources = false
        }

        release {
            // Enable optimizations for production
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // Build features - disable what you don't use to reduce build time
    buildFeatures {
        viewBinding = true
        buildConfig = false  // Disable if not using BuildConfig
        compose = true
        aidl = false         // Disable if not using AIDL
        renderScript = false // Disable if not using RenderScript
    }

    // Lint options - disable in debug for faster builds
    lint {
        checkReleaseBuilds = false  // Only run in CI
        abortOnError = false        // Don't fail build on lint errors
        checkDependencies = false   // Skip dependency linting (slow)
    }

    // Test options - optimize for speed
    testOptions {
        unitTests {
            isReturnDefaultValues = true      // Mock Android APIs
            isIncludeAndroidResources = false // Faster but less accurate
        }
    }

    // Compile options - use latest Java for better performance
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
        // Disable assertions in debug builds for faster compilation
        freeCompilerArgs = listOf(
            "-Xno-param-assertions",    // Disable parameter assertions
            "-Xno-call-assertions",     // Disable call assertions
            "-Xno-receiver-assertions"  // Disable receiver assertions
        )
    }
}
```

**Explanation:**
- **Resource configurations**: Only include needed languages/resources to reduce APK size
- **Build features**: Disable unused features (AIDL, RenderScript) to skip unnecessary processing
- **Lint options**: Disable slow checks in debug builds, run only in CI
- **Test options**: Use mocks instead of real Android resources for faster unit tests
- **Kotlin options**: Disable assertions in debug builds for faster compilation

**3. Dependency Management**

```kotlin
// Use version catalogs (libs.versions.toml) for centralized version management
[versions]
kotlin = "1.9.20"
compose = "1.5.4"
hilt = "2.48"

[libraries]
androidx-core = { module = "androidx.core:core-ktx", version = "1.12.0" }
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }

// In build.gradle.kts
dependencies {
    // Use implementation instead of api when possible - reduces recompilation scope
    implementation(libs.androidx.core)

    // Use specific modules instead of full libraries - smaller dependency tree
    implementation("androidx.compose.ui:ui:1.5.4")
    // Instead of: implementation("androidx.compose:compose-bom:1.5.4")

    // Exclude transitive dependencies you don't need - reduces compilation time
    implementation("com.squareup.retrofit2:retrofit:2.9.0") {
        exclude(group = "com.squareup.okio", module = "okio")
    }

    // Use debugImplementation for debug-only deps - not included in release builds
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
```

**Explanation:**
- **Version catalogs**: Centralized version management prevents conflicts and speeds resolution
- **implementation vs api**: `implementation` hides dependencies from consumers, reducing recompilation
- **Specific modules**: Import only needed parts instead of entire libraries
- **Exclude transitive deps**: Remove unused dependencies to reduce compilation overhead
- **debugImplementation**: Debug-only dependencies don't affect release build performance

**4. Modularization**

```kotlin
// Split into modules for parallel compilation
// Project structure:
// :app                    - Main application module
// :feature:home          - Home feature module
// :feature:profile       - Profile feature module
// :core:network          - Network layer module
// :core:database         - Database layer module
// :core:ui              - UI components module

// settings.gradle.kts
include(":app")
include(":feature:home")
include(":feature:profile")
include(":core:network")
include(":core:database")
include(":core:ui")

// Benefits:
// 1. Parallel compilation of modules - multiple modules compile simultaneously
// 2. Smaller incremental builds - only changed modules recompile
// 3. Better caching - Gradle can cache individual modules
// 4. Improved code organization - clear separation of concerns

// :feature:home/build.gradle.kts
plugins {
    id("com.android.library")  // Library module, not application
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.feature.home"
    // Library modules have different configuration than app modules
}

dependencies {
    // Feature modules depend on core modules
    implementation(project(":core:network"))  // Access network layer
    implementation(project(":core:ui"))       // Access UI components
    // No direct dependencies on other feature modules
}
```

**Explanation:**
- **Parallel compilation**: Gradle compiles independent modules simultaneously using multiple CPU cores
- **Incremental builds**: Only changed modules and their dependents recompile, not the entire project
- **Module boundaries**: Clear dependencies prevent circular references and improve build predictability
- **Library modules**: Use `com.android.library` for feature/core modules, `com.android.application` only for `:app`

**5. Build Cache**

```kotlin
// Enable build cache
// gradle.properties
org.gradle.caching=true

// Configure remote cache (for teams)
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        // Local cache directory - stores build outputs locally
        directory = File(rootDir, ".gradle/build-cache")
        // Clean up old cache entries to prevent disk space issues
        removeUnusedEntriesAfterDays = 30
    }

    remote<HttpBuildCache> {
        // Remote cache server for team sharing
        url = uri("https://your-build-cache-server.com/cache/")
        credentials {
            username = System.getenv("CACHE_USERNAME")
            password = System.getenv("CACHE_PASSWORD")
        }
        isEnabled = true
        // Only push to remote cache from CI, not local development
        isPush = System.getenv("CI") == "true"
    }
}
```

**Explanation:**
- **Local cache**: Stores build outputs locally to avoid recompilation of unchanged code
- **Remote cache**: Team members can share cache entries, especially useful for CI/CD
- **Cache cleanup**: Prevents unlimited disk usage by removing old entries
- **Push control**: Only CI pushes to remote cache to avoid conflicts from different local environments

**6. Kotlin Compilation Optimization**

```kotlin
// build.gradle.kts (app module)
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        // Use parallel compilation - utilize all CPU cores
        freeCompilerArgs += "-Xbackend-threads=0"  // 0 = use all available cores

        // Enable incremental compilation - only recompile changed files
        incremental = true

        // Disable verbose output - reduces I/O overhead
        verbose = false
    }
}

// Kapt optimization (if using annotation processors)
kapt {
    useBuildCache = true        // Cache annotation processing results
    correctErrorTypes = true    // Better error messages, slightly slower
}

// KSP (faster alternative to Kapt)
plugins {
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
}

// Use KSP instead of Kapt when possible
dependencies {
    ksp(libs.hilt.compiler)      // 2x faster than Kapt
    // kapt(libs.hilt.compiler)  // Legacy annotation processing
}
```

**Explanation:**
- **Parallel compilation**: Uses all CPU cores for Kotlin compilation, significantly faster on multi-core machines
- **Incremental compilation**: Only recompiles changed Kotlin files, not the entire codebase
- **KSP vs Kapt**: KSP is the modern replacement for Kapt, offering 2x faster annotation processing
- **Build cache**: Caches annotation processing results to avoid reprocessing unchanged code

**7. Profiling and Analysis**

```bash
# Generate build scan - detailed build analysis
./gradlew build --scan
# Outputs URL to comprehensive build report showing:
# - Task execution times and dependencies
# - Configuration vs execution time breakdown
# - Cache hit rates and effectiveness
# - Memory usage and GC performance

# Generate profile report - local HTML analysis
./gradlew assembleDebug --profile
# Output: build/reports/profile/profile-*.html
# Analyze in browser:
# - Slowest tasks (identify bottlenecks)
# - Configuration vs execution time (find config issues)
# - Task dependencies (understand build flow)
# - Parallel execution efficiency
```

**Explanation:**
- **Build scan**: Comprehensive cloud-based analysis with detailed metrics and recommendations
- **Profile report**: Local HTML report for offline analysis of build performance
- **Task analysis**: Identify which tasks take the most time and why
- **Dependency analysis**: Understand task execution order and parallelization opportunities

**8. CI/CD Optimization**

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
          distribution: 'temurin'    # OpenJDK distribution
          java-version: '17'         # Use Java 17 for better performance
          cache: 'gradle'            # Enable Gradle dependency caching

      - name: Cache Gradle dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches         # Gradle dependency cache
            ~/.gradle/wrapper        # Gradle wrapper cache
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
          # Cache key based on OS and Gradle files hash

      - name: Build with Gradle
        run: ./gradlew assembleDebug --parallel --build-cache --configuration-cache
        # --parallel: Use multiple workers
        # --build-cache: Enable build caching
        # --configuration-cache: Cache configuration phase

      - name: Run unit tests
        run: ./gradlew testDebugUnitTest --parallel
        # Run tests in parallel for faster execution
```

**Explanation:**
- **JDK caching**: GitHub Actions caches JDK installation to avoid re-downloading
- **Gradle dependency cache**: Caches downloaded dependencies between CI runs
- **Cache key strategy**: Uses file hashes to invalidate cache when dependencies change
- **Parallel execution**: Uses multiple workers for both build and test phases
- **Build cache flags**: Enables all available caching mechanisms for maximum speed

**9. Development Workflow Optimization**

```bash
# Use specific tasks instead of building everything
./gradlew :app:assembleDebug          # Only app module - fastest
# ./gradlew build                      # Builds all modules - slower

# Use --dry-run to see what will execute without actually running
./gradlew assembleDebug --dry-run
# Shows which tasks would run without executing them

# Use continuous build for auto-rebuild on file changes
./gradlew assembleDebug --continuous
# Automatically rebuilds when source files change

# Skip tests during development for faster builds
./gradlew assembleDebug -x test
# -x test excludes test tasks from execution

# Parallel execution with worker limit
./gradlew clean assembleDebug --parallel --max-workers=8
# --parallel: Use multiple workers
# --max-workers=8: Limit to 8 workers (adjust based on CPU cores)
```

**Explanation:**
- **Specific tasks**: Build only what you need instead of entire project
- **Dry run**: Preview what tasks will execute without running them
- **Continuous build**: Automatically rebuilds on file changes, great for development
- **Skip tests**: Exclude slow test tasks during development iterations
- **Worker limits**: Control parallel execution to avoid overwhelming the system

**10. Quick Wins Checklist**

```kotlin
// Enable in gradle.properties - immediate 20-80% improvement
org.gradle.parallel=true              // 20-40% faster - use multiple workers
org.gradle.caching=true               // 30-50% faster (incremental) - cache build outputs
org.gradle.configuration-cache=true   // 10-30% faster - cache configuration phase
org.gradle.vfs.watch=true            // 5-15% faster - watch file system changes
org.gradle.jvmargs=-Xmx4096m         // Prevent OOM, faster GC - allocate more memory

// In build.gradle.kts - Android-specific optimizations
android.nonTransitiveRClass=true      // Faster R class generation - non-transitive R classes
kapt.useBuildCache=true              // Cache annotation processing - reuse Kapt results
ksp instead of kapt                  // 2x faster annotation processing - modern alternative

// Development workflow - daily productivity improvements
Use specific build variants          // Don't build all - target specific variants
Modularize project                   // Parallel compilation - split into modules
Disable lint in debug                // Run only in CI - skip slow checks locally
Use build scans                      // Identify bottlenecks - analyze performance

// Dependencies - reduce compilation overhead
Remove unused dependencies           // Less to compile - smaller dependency tree
Use implementation over api          // Smaller recompilation scope - hide dependencies
Version catalog                      // Faster resolution - centralized version management
```

**Explanation:**
- **gradle.properties**: These settings provide immediate performance improvements with minimal effort
- **Android optimizations**: Specific to Android build system for maximum impact
- **Workflow changes**: Daily habits that compound over time for significant productivity gains
- **Dependency management**: Reduces compilation scope and resolution time

**Common Issues:**

1. **Configuration time too long:**
```kotlin
// Don't resolve dependencies at configuration time
val myDeps = configurations.implementation.resolve()  // Slow!

// Do it at execution time
tasks.register("myTask") {
    doLast {
        val myDeps = configurations.implementation.resolve()  // Fast
    }
}
```

2. **Too many variants:**
```kotlin
// Excessive build types and flavors
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

// Minimize variants or use build parameters
```

3. **Large dependencies:**
```bash
# Analyze dependency sizes
./gradlew :app:dependencies --configuration releaseRuntimeClasspath

# Find largest dependencies
./gradlew :app:dependencies | grep -E "\+---|\---" | sort | uniq -c | sort -rn
```

## Ответ (RU)


**1. Оптимизация конфигурации Gradle**

**gradle.properties:**
```properties
# Включить параллельную сборку - использует несколько ядер CPU для независимых задач
org.gradle.parallel=true

# Настроить JVM heap - предотвращает OutOfMemoryError, оптимизирует сборку мусора
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# Включить кэширование - сохраняет результаты сборки для избежания перекомпиляции
org.gradle.caching=true

# Включить configuration cache - кэширует фазу конфигурации (на 10-30% быстрее)
org.gradle.configuration-cache=true

# Включить daemon - держит процесс Gradle живым между сборками
org.gradle.daemon=true

# Включить file system watching - отслеживает изменения файлов без опроса
org.gradle.vfs.watch=true

# Android специфичные
android.enableJetifier=false              # Отключить если полностью мигрировали на AndroidX
android.useAndroidX=true                  # Использовать AndroidX вместо Support Library

# Kotlin компилятор
kotlin.incremental=true                   # Перекомпилировать только измененные Kotlin файлы
kotlin.incremental.java=true              # Отслеживать изменения Java, влияющие на Kotlin

# R8/ProGuard
android.enableR8.fullMode=true            # Включить полную оптимизацию R8
android.enableR8=true                     # Включить сжатие кода R8

# Build features - отключить неиспользуемые функции для сокращения времени сборки
android.defaults.buildfeatures.buildconfig=false    # Отключить генерацию BuildConfig
android.defaults.buildfeatures.aidl=false           # Отключить обработку AIDL
android.defaults.buildfeatures.renderscript=false   # Отключить обработку RenderScript

# NonTransitiveRClass
android.nonTransitiveRClass=true          # Генерировать нетранзитивные R классы (быстрее компиляция)
android.nonFinalResIds=true               # Сделать ID ресурсов нефинальными (быстрее генерация R класса)
```

**Как это работает:**
- **Параллельное выполнение**: Gradle анализирует зависимости задач и выполняет независимые задачи одновременно используя несколько ядер CPU
- **Кэш сборки**: Сохраняет результаты задач с хешами содержимого, пропускает выполнение если входы не изменились
- **Configuration cache**: Сериализует результаты фазы конфигурации, пропускает переоценку при последующих сборках
- **VFS watching**: Использует нативные события файловой системы вместо периодического сканирования директорий
- **Нетранзитивные R классы**: Каждый модуль получает свой R класс, уменьшая зависимости компиляции
- **Инкрементальная компиляция**: Перекомпилирует только измененные файлы и их зависимости

**Оптимизация Build Script:**
```kotlin
// build.gradle.kts (project level)
buildscript {
    val kotlinVersion = "1.9.20"  // Конкретная версия, не '+'

    repositories {
        google()  // Самые используемые первыми
        mavenCentral()
    }
}

plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
}

// Стратегия разрешения зависимостей
allprojects {
    configurations.all {
        resolutionStrategy {
            // Не кэшировать динамические версии (например, "1.9.+") для получения последних
            cacheDynamicVersionsFor(0, "seconds")
            // Не кэшировать изменяющиеся модули для получения последних снапшотов
            cacheChangingModulesFor(0, "seconds")
            // Принудительно использовать конкретную версию для избежания конфликтов
            force("com.google.code.gson:gson:2.10.1")
        }
    }
}
```

**Объяснение:**
- **Конкретные версии**: Избегайте `"1.9.+"` или `"latest"` - они вызывают накладные расходы на разрешение зависимостей
- **Порядок репозиториев**: Размещайте наиболее используемые репозитории первыми для сокращения времени поиска
- **Стратегия разрешения**: Предотвращает конфликты версий и сокращает время разрешения
- **apply false**: Плагины применяются в модулях, а не на уровне проекта

**2. Конфигурация на уровне модуля**

```kotlin
// build.gradle.kts (app module)
android {
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34

        // Только нужные ресурсы
        resourceConfigurations += listOf("en", "ru")

        vectorDrawables.useSupportLibrary = true
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
            isShrinkResources = false
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

    // Build features - отключите что не используете
    buildFeatures {
        viewBinding = true
        buildConfig = false
        compose = true
        aidl = false
        renderScript = false
    }

    // Lint опции
    lint {
        checkReleaseBuilds = false
        abortOnError = false
        checkDependencies = false
    }

    // Test опции
    testOptions {
        unitTests {
            isReturnDefaultValues = true
            isIncludeAndroidResources = false
        }
    }

    // Compile опции
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs = listOf(
            "-Xno-param-assertions",
            "-Xno-call-assertions",
            "-Xno-receiver-assertions"
        )
    }
}
```

**3. Управление зависимостями**

```kotlin
// Используйте version catalogs (libs.versions.toml)
[versions]
kotlin = "1.9.20"
compose = "1.5.4"
hilt = "2.48"

[libraries]
androidx-core = { module = "androidx.core:core-ktx", version = "1.12.0" }
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }

// В build.gradle.kts
dependencies {
    // Используйте implementation вместо api когда возможно
    implementation(libs.androidx.core)

    // Используйте конкретные модули
    implementation("androidx.compose.ui:ui:1.5.4")

    // Исключите транзитивные зависимости которые не нужны
    implementation("com.squareup.retrofit2:retrofit:2.9.0") {
        exclude(group = "com.squareup.okio", module = "okio")
    }

    // Используйте debugImplementation для debug-only зависимостей
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
```

**4. Модуляризация**

```kotlin
// Разделите на модули для параллельной компиляции
// Структура проекта:
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

// Преимущества:
// 1. Параллельная компиляция модулей
// 2. Меньшие инкрементальные сборки
// 3. Лучшее кэширование
// 4. Улучшенная организация кода

// :feature:home/build.gradle.kts
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.feature.home"
}

dependencies {
    implementation(project(":core:network"))
    implementation(project(":core:ui"))
}
```

**5. Build Cache**

```kotlin
// Включить build cache
// gradle.properties
org.gradle.caching=true

// Настроить удалённый кэш (для команд)
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
        isPush = System.getenv("CI") == "true"
    }
}
```

**6. Оптимизация компиляции Kotlin**

```kotlin
// build.gradle.kts (app module)
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        // Используйте параллельную компиляцию
        freeCompilerArgs += "-Xbackend-threads=0"

        // Включить инкрементальную компиляцию
        incremental = true

        // Отключить verbose вывод
        verbose = false
    }
}

// Оптимизация Kapt (если используете annotation processors)
kapt {
    useBuildCache = true
    correctErrorTypes = true
}

// KSP (быстрая альтернатива Kapt)
plugins {
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
}

// Используйте KSP вместо Kapt когда возможно
dependencies {
    ksp(libs.hilt.compiler)      // Быстрее
    // kapt(libs.hilt.compiler)  // Медленнее
}
```

**7. Профилирование и анализ**

```bash
# Генерировать build scan
./gradlew build --scan

# Генерировать profile report
./gradlew assembleDebug --profile

# Вывод: build/reports/profile/profile-*.html
# Анализируйте:
# - Самые медленные задачи
# - Время конфигурации vs выполнения
# - Зависимости задач
```

**8. Оптимизация CI/CD**

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
          cache: 'gradle'

      - name: Cache Gradle dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

      - name: Build with Gradle
        run: ./gradlew assembleDebug --parallel --build-cache --configuration-cache

      - name: Run unit tests
        run: ./gradlew testDebugUnitTest --parallel
```

**9. Оптимизация рабочего процесса разработки**

```bash
# Используйте конкретные задачи вместо сборки всего
./gradlew :app:assembleDebug          # Только app модуль
# ./gradlew build                      # Собирает все модули

# Используйте --dry-run чтобы увидеть что выполнится
./gradlew assembleDebug --dry-run

# Используйте continuous build для авто-пересборки
./gradlew assembleDebug --continuous

# Пропускайте тесты во время разработки
./gradlew assembleDebug -x test

# Параллельное выполнение
./gradlew clean assembleDebug --parallel --max-workers=8
```

**10. Чеклист быстрых побед**

```kotlin
// Включить в gradle.properties
org.gradle.parallel=true              // 20-40% быстрее
org.gradle.caching=true               // 30-50% быстрее (инкрементальная)
org.gradle.configuration-cache=true   // 10-30% быстрее
org.gradle.vfs.watch=true            // 5-15% быстрее
org.gradle.jvmargs=-Xmx4096m         // Предотвратить OOM, быстрее GC

// В build.gradle.kts
android.nonTransitiveRClass=true      // Быстрее генерация R класса
kapt.useBuildCache=true              // Кэширование annotation processing
ksp вместо kapt                      // 2x быстрее annotation processing

// Рабочий процесс разработки
Используйте конкретные build варианты  // Не собирайте все
Модуляризируйте проект                // Параллельная компиляция
Отключите lint в debug               // Запускайте только в CI
Используйте build scans              // Определите узкие места

// Зависимости
Удалите неиспользуемые зависимости   // Меньше компилировать
Используйте implementation вместо api // Меньший scope перекомпиляции
Version catalog                      // Быстрее разрешение
```

**Частые проблемы:**

1. **Слишком долгое время конфигурации:**
```kotlin
// Не разрешайте зависимости во время конфигурации
val myDeps = configurations.implementation.resolve()  // Медленно!

// Делайте это во время выполнения
tasks.register("myTask") {
    doLast {
        val myDeps = configurations.implementation.resolve()  // Быстро
    }
}
```

2. **Слишком много вариантов:**
```kotlin
// Избыточные build types и flavors
productFlavors {
    create("dev") { ... }
    create("staging") { ... }
    create("prod") { ... }
}
buildTypes {
    debug { ... }
    release { ... }
}
// = 6 вариантов, медленно

// Минимизируйте варианты или используйте build параметры
```

3. **Большие зависимости:**
```bash
# Анализируйте размеры зависимостей
./gradlew :app:dependencies --configuration releaseRuntimeClasspath

# Найдите самые большие зависимости
./gradlew :app:dependencies | grep -E "\+---|\---" | sort | uniq -c | sort -rn
```

---

## Follow-ups

- How do you measure build performance improvements?
- What are the trade-offs of using build cache vs local compilation?
- How do you optimize builds for large multi-module projects?
- What are the best practices for CI/CD build optimization?
- How do you debug slow build tasks?

## References

- [Gradle Performance](https://docs.gradle.org/current/userguide/performance.html)
- [Android Build Optimization](https://developer.android.com/studio/build/optimize-your-build)
- [Build Cache](https://docs.gradle.org/current/userguide/build_cache.html)
- [Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html)

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] - Gradle fundamentals
- [[q-android-app-bundles--android--easy]] - App bundles

### Related (Medium)
- [[q-gradle-build-system--android--medium]] - Gradle build system
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools
- [[q-gradle-version-catalog--android--medium]] - Version catalogs

### Advanced (Harder)
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Gradle Kotlin DSL
- [[q-compose-performance-optimization--android--hard]] - Compose performance
