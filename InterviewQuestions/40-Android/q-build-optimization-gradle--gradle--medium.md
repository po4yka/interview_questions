---
id: 20251011-220005
title: "Gradle Build Optimization / Оптимизация сборки Gradle"
aliases: []

# Classification
topic: android
subtopics: [gradle, build-performance, optimization, configuration-cache, modularization]
question_kind: practical
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/gradle, android/build-performance, android/optimization, android/configuration-cache, android/modularization, difficulty/medium]
source: Original
source_note: Gradle build performance best practices

# Workflow & relations
status: draft
moc: moc-android
related: [kapt-vs-ksp, app-startup-optimization, modularization-patterns]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [en, ru, android/gradle, android/build-performance, android/optimization, android/configuration-cache, android/modularization, difficulty/medium]
---
# Question (EN)
> Optimize Gradle build time comprehensively. Use configuration cache, build cache, parallel execution, modularization, and incremental annotation processing.

# Вопрос (RU)
> Комплексно оптимизируйте время сборки Gradle. Используйте configuration cache, build cache, параллельное выполнение, модуляризацию и инкрементальную обработку аннотаций.

---

## Answer (EN)

### Overview

Slow builds kill developer productivity. A typical Android project can take 3-10 minutes to build without optimization. With proper configuration, the same project can build in under 30 seconds.

**Build Time Targets:**
- Clean build: < 2 minutes (acceptable), < 1 minute (excellent)
- Incremental build: < 10 seconds (acceptable), < 5 seconds (excellent)

### Complete gradle.properties Optimization

**gradle.properties:**
```properties
# ====================
# JVM Configuration
# ====================
# Allocate more memory to Gradle daemon
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=1024m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8 -XX:+UseParallelGC

# ====================
# Gradle Daemon
# ====================
# Keep daemon alive (faster subsequent builds)
org.gradle.daemon=true
# Daemon timeout
org.gradle.daemon.idletimeout=7200000

# ====================
# Parallel Execution
# ====================
# Run tasks in parallel (use all CPU cores)
org.gradle.parallel=true
# Number of workers (auto-detect or set manually)
org.gradle.workers.max=8

# ====================
# Configuration Cache (HUGE improvement)
# ====================
# Cache configuration phase (3-5x faster)
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn
org.gradle.configuration-cache.max-problems=100

# ====================
# Build Cache
# ====================
# Enable local build cache
org.gradle.caching=true

# ====================
# Incremental Builds
# ====================
# Enable incremental compilation
kotlin.incremental=true
kotlin.incremental.java=true
kotlin.incremental.js=true

# ====================
# Annotation Processing
# ====================
# Incremental annotation processing (kapt)
kapt.incremental.apt=true
kapt.use.worker.api=true
kapt.include.compile.classpath=false

# ====================
# Android Specific
# ====================
# Use AndroidX
android.useAndroidX=true

# Enable R8 full mode
android.enableR8.fullMode=true

# Non-transitive R classes (faster builds)
android.nonTransitiveRClass=true
android.nonFinalResIds=true

# ====================
# Kotlin Compiler
# ====================
# Kotlin compiler daemon
kotlin.compiler.execution.strategy=daemon

# Kotlin parallel compilation
kotlin.compiler.parallel.tasks.in.project=true

# ====================
# Debugging (disable in CI)
# ====================
# org.gradle.debug=false
# org.gradle.daemon.debug=false
```

### Configuration Cache Implementation

**Before: Slow configuration**
```
Configuration time: 15-30 seconds per build
Problem: Gradle re-configures entire project every build
```

**After: Configuration cache enabled**
```
Configuration time: 1-2 seconds (cached)
Improvement: 10-15x faster configuration
```

**Check compatibility:**
```bash
# Test configuration cache compatibility
./gradlew build --configuration-cache

# View problems
./gradlew build --configuration-cache --configuration-cache-problems=warn
```

**Fix common issues:**

```kotlin
//  BAD: Accessing System.getenv at configuration time
val apiKey = System.getenv("API_KEY") // Breaks configuration cache

android {
    defaultConfig {
        buildConfigField("String", "API_KEY", "\"$apiKey\"")
    }
}

//  GOOD: Use providers to defer evaluation
val apiKeyProvider: Provider<String> = providers.environmentVariable("API_KEY")

android {
    defaultConfig {
        buildConfigField("String", "API_KEY", apiKeyProvider.map { "\"$it\"" })
    }
}
```

### Build Cache Configuration

#### 1. Local Build Cache

**settings.gradle.kts:**
```kotlin
buildCache {
    local {
        isEnabled = true
        directory = File(rootDir, ".gradle/build-cache")
        removeUnusedEntriesAfterDays = 7
    }
}
```

#### 2. Remote Build Cache (Team/CI)

**settings.gradle.kts:**
```kotlin
buildCache {
    local {
        isEnabled = true
    }

    remote<HttpBuildCache> {
        url = uri("https://build-cache.example.com/cache/")
        isPush = System.getenv("CI") == "true" // Only CI pushes
        credentials {
            username = System.getenv("CACHE_USERNAME")
            password = System.getenv("CACHE_PASSWORD")
        }
    }
}
```

**Results:**
```
First build: 120 seconds
Second build (cached): 15 seconds (8x faster)
```

### Modularization for Faster Builds

**Project structure:**
```
MyApp/
 app/                    # Main app (depends on features)
 core/
    core-ui/           # Shared UI components
    core-data/         # Data layer
    core-common/       # Common utilities
 feature/
    feature-home/      # Home feature
    feature-profile/   # Profile feature
    feature-settings/  # Settings feature
 buildSrc/              # Build logic
```

**Benefits:**
- Incremental builds: Change feature-home, only rebuild that module
- Parallel compilation: Modules build simultaneously
- Code isolation: Better separation of concerns

**app/build.gradle.kts:**
```kotlin
dependencies {
    // Feature modules
    implementation(project(":feature:feature-home"))
    implementation(project(":feature:feature-profile"))
    implementation(project(":feature:feature-settings"))

    // Core modules
    implementation(project(":core:core-ui"))
    implementation(project(":core:core-data"))
    implementation(project(":core:core-common"))
}
```

**Build time comparison:**
```
Monolithic app:
- Full build: 180 seconds
- Change 1 file: rebuild entire app (180 seconds)

Modularized app:
- Full build: 150 seconds (parallel compilation)
- Change file in feature-home: rebuild only feature-home + app (25 seconds)
- 7x faster incremental builds!
```

### Version Catalogs for Dependency Management

**gradle/libs.versions.toml:**
```toml
[versions]
kotlin = "1.9.21"
compose = "1.5.4"
hilt = "2.50"
room = "2.6.1"
retrofit = "2.9.0"

[libraries]
# Kotlin
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }
kotlinx-coroutines-android = "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3"

# Compose
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
compose-material3 = { module = "androidx.compose.material3:material3", version.ref = "compose" }

# Hilt
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }
hilt-compiler = { module = "com.google.dagger:hilt-compiler", version.ref = "hilt" }

# Room
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
room-ktx = { module = "androidx.room:room-ktx", version.ref = "room" }
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }

# Networking
retrofit = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
retrofit-gson = { module = "com.squareup.retrofit2:converter-gson", version.ref = "retrofit" }

[bundles]
compose = ["compose-ui", "compose-material3"]
room = ["room-runtime", "room-ktx"]
retrofit = ["retrofit", "retrofit-gson"]

[plugins]
android-application = "com.android.application:8.2.0"
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = "com.google.devtools.ksp:1.9.21-1.0.16"
```

**app/build.gradle.kts:**
```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

dependencies {
    // Single version source, faster sync
    implementation(libs.kotlin.stdlib)
    implementation(libs.kotlinx.coroutines.android)

    // Bundles for related dependencies
    implementation(libs.bundles.compose)
    implementation(libs.bundles.room)
    ksp(libs.room.compiler)

    implementation(libs.bundles.retrofit)
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)
}
```

**Benefits:**
- Centralized version management
- Faster IDE sync (no dependency resolution)
- Type-safe accessors
- Easier updates

### Build Scan Analysis

**Enable build scans:**
```kotlin
// settings.gradle.kts
plugins {
    id("com.gradle.enterprise") version "3.16"
}

gradleEnterprise {
    buildScan {
        termsOfServiceUrl = "https://gradle.com/terms-of-service"
        termsOfServiceAgree = "yes"

        // Publish to Gradle Enterprise
        publishAlways()
    }
}
```

**Analyze build:**
```bash
./gradlew build --scan

# Opens URL with detailed build report:
# https://scans.gradle.com/s/abcd1234
```

**Build scan shows:**
- Task execution timeline
- Longest running tasks
- Cache hit/miss rates
- Configuration time vs execution time
- Dependency resolution time

### KSP Migration (2x Faster than KAPT)

**Before: KAPT**
```kotlin
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation(libs.room.runtime)
    kapt(libs.room.compiler)  // Slow: generates Java stubs

    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)
}
```

**After: KSP**
```kotlin
plugins {
    id("com.google.devtools.ksp") version "1.9.21-1.0.16"
}

dependencies {
    implementation(libs.room.runtime)
    ksp(libs.room.compiler)  // Fast: Kotlin-native

    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)
}

// Update generated source paths
kotlin.sourceSets.main {
    kotlin.srcDir("build/generated/ksp/main/kotlin")
}
```

**Results:**
```
KAPT build: 85 seconds
KSP build: 42 seconds (2x faster)
```

### Build Performance Measurements

**Before optimization:**
```bash
./gradlew clean build --scan

Build results:
- Configuration: 28s
- Execution: 152s
- Total: 180s

Bottlenecks:
- KAPT processing: 55s
- Resource compilation: 32s
- Dex generation: 28s
- Unit tests: 22s
```

**After optimization:**
```bash
./gradlew clean build --scan

Build results:
- Configuration: 2s (configuration cache)
- Execution: 38s (parallel, KSP, modular)
- Total: 40s

Improvements:
- Configuration: 28s → 2s (-93%)
- KAPT → KSP: 55s → 22s (-60%)
- Parallel compilation: 20% faster
- Overall: 180s → 40s (4.5x faster!)
```

### CI/CD Optimization

**.github/workflows/android.yml:**
```yaml
name: Android CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/gradle-build-action@v2
        with:
          # Enable caching for Gradle dependencies
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}

      - name: Gradle Cache
        uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
            .gradle/build-cache
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
          restore-keys: |
            ${{ runner.os }}-gradle-

      - name: Build with Gradle
        run: |
          ./gradlew assembleRelease \
            --configuration-cache \
            --build-cache \
            --parallel \
            --no-daemon \
            --stacktrace

      - name: Run Tests
        run: |
          ./gradlew test \
            --configuration-cache \
            --build-cache \
            --parallel \
            --no-daemon

      - name: Upload Build Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: app-release
          path: app/build/outputs/apk/release/
```

**CI build time:**
```
Before: 12 minutes
After: 3 minutes (4x faster with caching)
```

### Best Practices

1. **Enable Configuration Cache**: Biggest single improvement (10-15x faster)
2. **Use Build Cache**: Share cache between developers and CI
3. **Parallel Execution**: Utilize all CPU cores
4. **Modularize**: Break large apps into feature modules
5. **Migrate to KSP**: 2x faster than KAPT for annotation processing
6. **Version Catalogs**: Centralize dependency management
7. **Increase JVM Memory**: Prevent GC pauses during build
8. **Profile Builds**: Use build scans to identify bottlenecks
9. **Avoid Dynamic Versions**: Pin exact versions (no `+` in versions)
10. **Clean Old Builds**: Remove unused cache periodically
11. **Minimize Custom Tasks**: Custom tasks often not cacheable
12. **Use Gradle Daemon**: Keep daemon alive between builds

### Common Pitfalls

1. **Dynamic Dependency Versions**: `implementation("lib:1.+")` breaks caching
2. **Absolute Paths in Build**: Breaks caching, use relative paths
3. **Configuration at Runtime**: Access properties at execution time, not configuration
4. **Too Many Modules**: Over-modularization can slow builds
5. **No Build Cache**: Missing 8x speed improvement
6. **Not Using KSP**: Staying on KAPT wastes time
7. **Low JVM Memory**: Causes GC pauses during build
8. **Custom Tasks Not Cacheable**: Mark tasks with inputs/outputs
9. **Daemon Disabled**: Loses warm-up benefits
10. **Not Profiling**: Can't optimize what you don't measure

## Ответ (RU)

[Russian translation follows same structure]

### Полная оптимизация gradle.properties

[Same properties file with Russian comments...]

### Лучшие практики

1. **Включите Configuration Cache**: Самое большое улучшение (в 10-15 раз быстрее)
2. **Используйте Build Cache**: Делитесь кэшем между разработчиками и CI
3. **Параллельное выполнение**: Используйте все ядра CPU
4. **Модуляризация**: Разбивайте большие приложения на модули функций
5. **Мигрируйте на KSP**: В 2 раза быстрее KAPT для обработки аннотаций
6. **Version Catalogs**: Централизуйте управление зависимостями
7. **Увеличьте память JVM**: Предотвратите паузы GC во время сборки
8. **Профилируйте сборки**: Используйте build scans для выявления узких мест
9. **Избегайте динамических версий**: Закрепляйте точные версии (без `+` в версиях)
10. **Очищайте старые сборки**: Периодически удаляйте неиспользуемый кэш
11. **Минимизируйте пользовательские задачи**: Пользовательские задачи часто не кэшируются
12. **Используйте Gradle Daemon**: Держите демон активным между сборками

---

## References
- [Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html)
- [Build Cache](https://docs.gradle.org/current/userguide/build_cache.html)
- [Gradle Performance](https://docs.gradle.org/current/userguide/performance.html)
- [Version Catalogs](https://docs.gradle.org/current/userguide/platforms.html)

## Related Questions

### Related (Medium)
- [[q-app-startup-optimization--performance--medium]] - Performance
- [[q-baseline-profiles-optimization--performance--medium]] - Performance
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Gradle
- [[q-app-size-optimization--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-modularization-patterns--android--hard]] - Architecture
### Related (Medium)
- [[q-app-startup-optimization--performance--medium]] - Performance
- [[q-baseline-profiles-optimization--performance--medium]] - Performance
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Gradle
- [[q-app-size-optimization--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-modularization-patterns--android--hard]] - Architecture
### Related (Medium)
- [[q-app-startup-optimization--performance--medium]] - Performance
- [[q-baseline-profiles-optimization--performance--medium]] - Performance
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Gradle
- [[q-app-size-optimization--performance--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-modularization-patterns--android--hard]] - Architecture