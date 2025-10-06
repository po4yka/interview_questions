---
tags:
  - android
  - android/project-structure
  - apk-size
  - codebase-analysis
  - codebase-size
  - metrics
  - modules
  - project-metrics
  - project-structure
difficulty: easy
---

# Как можно измерить размер проекта?

**English**: How can you measure project size?

## Answer

Project size can be measured in several ways:
1. **Lines of Code (LOC)** - Total source code lines
2. **Number of Modules** - Modularization level
3. **APK Size** - Final application size

**Typical large project:** ~100,000 lines of code divided into 5-10 modules.

---

## Measurement Metrics

### 1. Lines of Code (LOC)

**Definition:** Count of source code lines in the project.

**How to measure:**

```bash

# Count all Kotlin files
find . -name "*.kt" | xargs wc -l

# Count all Java files
find . -name "*.java" | xargs wc -l

# Count both Kotlin and Java
find . \( -name "*.kt" -o -name "*.java" \) | xargs wc -l
```

**Example output:**
```
   1234 ./app/src/main/java/com/example/MainActivity.kt
   567 ./app/src/main/java/com/example/ViewModel.kt
   890 ./feature/login/src/main/java/Login.kt
   ...
   102345 total
```

---

#### Using Android Studio

**Statistic Plugin:**

1. Install "Statistic" plugin
2. **Analyze → Statistic**
3. View detailed breakdown:
   - Lines of code by file type
   - Lines per package
   - Comment ratio
   - Blank lines

**Example report:**
```
Total Files: 423
Total Lines: 102,345

Kotlin:  85,234 lines (83.3%)
Java:    12,456 lines (12.2%)
XML:      4,655 lines (4.5%)

Comments: 15,234 lines (14.9%)
Blank:    8,123 lines (7.9%)
Code:     79,988 lines (78.2%)
```

---

#### Code Size Interpretation

| Project Size | LOC Range | Typical Complexity |
|--------------|-----------|-------------------|
| **Small** | < 10,000 | Single feature app, prototype |
| **Medium** | 10,000 - 50,000 | Standard app, 2-5 features |
| **Large** | 50,000 - 200,000 | Enterprise app, 5-10 modules |
| **Very Large** | > 200,000 | Complex platform, 10+ modules |

**Example projects:**
- **Small:** Calculator app (~2,000 LOC)
- **Medium:** News reader (~25,000 LOC)
- **Large:** Banking app (~120,000 LOC)
- **Very Large:** Social media platform (~500,000 LOC)

---

### 2. Number of Modules

**Definition:** Count of Gradle modules in the project.

**How to measure:**

```bash

# Count build.gradle.kts files (each module has one)
find . -name "build.gradle.kts" | wc -l

# Or count settings.gradle.kts includes
cat settings.gradle.kts | grep "include" | wc -l
```

**Example settings.gradle.kts:**
```kotlin
include(":app")
include(":core:network")
include(":core:database")
include(":feature:login")
include(":feature:profile")
include(":feature:chat")
include(":feature:settings")
```

**Module count:** 7 modules

---

#### Module Organization

**Typical module structure:**

```
project/
├── app/                    ← Main app module
├── core/
│   ├── network/           ← Networking library
│   ├── database/          ← Database layer
│   ├── ui/                ← Shared UI components
│   └── utils/             ← Utility functions
├── feature/
│   ├── login/             ← Login feature
│   ├── profile/           ← Profile feature
│   ├── chat/              ← Chat feature
│   └── settings/          ← Settings feature
└── test/
    └── shared/            ← Shared test utilities
```

**Total:** 12 modules

---

#### Module Count Interpretation

| Modularization | Module Count | Benefits |
|----------------|-------------|----------|
| **Monolithic** | 1 | Simple, fast builds (small apps) |
| **Basic** | 2-4 | Some separation, moderate builds |
| **Modular** | 5-10 | Good separation, parallel builds |
| **Highly Modular** | 10-20 | Excellent separation, complex setup |
| **Micro-services** | 20+ | Independent deployable units |

**Example:**
```kotlin
// Typical large project: 5-10 modules
:app                    // Main module
:core-network           // HTTP client, API calls
:core-database          // Room, data storage
:core-ui                // Shared UI components
:feature-login          // Login screen
:feature-home           // Home screen
:feature-profile        // User profile
:feature-settings       // App settings
```

---

### 3. APK Size

**Definition:** Size of the compiled Android application package.

**How to measure:**

#### Option 1: Build and Check APK

```bash

# Build release APK
./gradlew assembleRelease

# Check APK size
ls -lh app/build/outputs/apk/release/app-release.apk

# Output example:

# -rw-r--r-- 1 user staff 15M Oct 4 app-release.apk
```

---

#### Option 2: Android Studio APK Analyzer

1. **Build → Analyze APK**
2. Select APK file
3. View detailed breakdown:
   - Total size
   - Resources size
   - DEX files size
   - Native libraries size
   - Assets size

**Example breakdown:**
```
Total APK Size: 15.2 MB

classes.dex:    5.2 MB (34.2%)
resources.arsc: 2.1 MB (13.8%)
res/:           4.8 MB (31.6%)
lib/:           2.3 MB (15.1%)
assets/:        0.5 MB (3.3%)
META-INF/:      0.3 MB (2.0%)
```

---

#### APK Size Interpretation

| App Category | Typical Size | Notes |
|--------------|-------------|-------|
| **Lightweight** | < 10 MB | Utility apps, simple games |
| **Standard** | 10-30 MB | Most productivity apps |
| **Media-Rich** | 30-100 MB | Social media, photo apps |
| **Large** | 100-500 MB | Games, video streaming |
| **Very Large** | > 500 MB | AAA games, offline video apps |

**Examples:**
- Calculator: ~2 MB
- Twitter: ~35 MB
- Instagram: ~60 MB
- PUBG Mobile: ~900 MB

---

### 4. Other Metrics

#### Method Count

```bash

# Count methods using dexcount plugin
./gradlew countDebugDexMethods

# Output:

# Total methods: 45,234

# Total fields:  12,345
```

**Android limit:** 65,536 methods per DEX file (requires MultiDex if exceeded)

---

#### File Count

```bash

# Count all source files
find ./src -type f | wc -l

# Count by type
find ./src -name "*.kt" | wc -l    # Kotlin files
find ./src -name "*.xml" | wc -l   # XML layouts
```

---

#### Dependencies Count

```bash

# List all dependencies
./gradlew dependencies

# Count unique dependencies
./gradlew dependencies | grep "---" | wc -l
```

**Example:**
```
+--- androidx.core:core-ktx:1.12.0
+--- androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.2
+--- com.squareup.retrofit2:retrofit:2.9.0
+--- org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3
...
Total: 47 dependencies
```

---

## Complete Example: Real Project Metrics

### Example: Medium-Sized E-Commerce App

```
Project Metrics:
================
Lines of Code:     78,234 LOC
  - Kotlin:        62,187 LOC (79.5%)
  - Java:           8,456 LOC (10.8%)
  - XML:            7,591 LOC (9.7%)

Modules:           8 modules
  - app
  - core-network
  - core-database
  - core-ui
  - feature-catalog
  - feature-cart
  - feature-checkout
  - feature-profile

APK Size:          24.3 MB (release)
  - Code:           6.8 MB
  - Resources:      9.2 MB
  - Native libs:    7.1 MB
  - Other:          1.2 MB

Methods:           42,156 methods
Files:             523 source files
Dependencies:      38 libraries
Build Time:        2m 15s (incremental)
```

---

## Typical Large Project Breakdown

**~100,000 LOC, 5-10 modules:**

```
Project Structure:
==================

1. app module (~10,000 LOC)
   - Application class
   - Main activity
   - Navigation setup
   - Dependency injection

2. core modules (~30,000 LOC)
   - core-network:  8,000 LOC
   - core-database: 7,000 LOC
   - core-ui:       6,000 LOC
   - core-domain:   5,000 LOC
   - core-utils:    4,000 LOC

3. feature modules (~55,000 LOC)
   - feature-auth:     12,000 LOC
   - feature-home:     10,000 LOC
   - feature-profile:   8,000 LOC
   - feature-messages:  9,000 LOC
   - feature-settings:  7,000 LOC
   - feature-search:    9,000 LOC

4. test modules (~5,000 LOC)
   - Unit tests
   - Integration tests
   - UI tests

APK: 25-35 MB (typical)
Build time: 3-5 minutes (clean)
```

---

## Measuring Tools

### 1. SonarQube

```bash

# Run SonarQube analysis
./gradlew sonarqube
```

**Metrics provided:**
- Lines of code
- Code complexity (cyclomatic)
- Code duplication
- Code smells
- Technical debt

---

### 2. Detekt

```gradle
// build.gradle.kts
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.0"
}

detekt {
    buildUponDefaultConfig = true
    config = files("$projectDir/config/detekt.yml")
}
```

```bash
./gradlew detekt
```

---

### 3. Android Lint

```bash
./gradlew lint
```

**Output:** `app/build/reports/lint-results.html`

---

## Best Practices

### 1. Monitor Growth

```kotlin
// Track metrics over time
// Commit: 2024-01-01
LOC: 50,000
APK: 18 MB
Modules: 5

// Commit: 2024-06-01
LOC: 78,000 (+56%)
APK: 24 MB (+33%)
Modules: 8 (+3)
```

### 2. Set Limits

```gradle
// Enforce APK size limit
android {
    buildTypes {
        release {
            if (variant.outputs[0].outputFile.size() > 50_000_000) {
                throw GradleException("APK size exceeds 50MB!")
            }
        }
    }
}
```

### 3. Regular Cleanup

- Remove unused dependencies
- Delete dead code
- Optimize resources (images, strings)
- Use R8/ProGuard shrinking

---

## Summary

**How to measure project size:**

1. **Lines of Code (LOC)**
   - Find + wc -l
   - Android Studio Statistics plugin
   - Typical large project: **~100,000 LOC**

2. **Number of Modules**
   - Count build.gradle files
   - Check settings.gradle includes
   - Typical large project: **5-10 modules**

3. **APK Size**
   - Build and check file size
   - APK Analyzer in Android Studio
   - Typical large project: **20-40 MB**

4. **Other Metrics**
   - Method count
   - File count
   - Dependency count
   - Build time

**Tools:**
- Android Studio (APK Analyzer, Statistics plugin)
- SonarQube (code quality)
- Detekt (Kotlin static analysis)
- Dexcount (method counting)

**Best practices:**
- Monitor metrics over time
- Set size limits
- Regular cleanup and optimization

---

## Ответ

Размер проекта можно измерить несколькими способами:

1. **Строки кода (LOC)** - общее количество строк исходного кода
2. **Количество модулей** - уровень модуляризации
3. **Размер APK** - размер финального приложения

**Типичный крупный проект:** около **100,000 строк кода**, разделённых на **5-10 модулей**.

**Как измерить:**
- LOC: `find . -name "*.kt" | xargs wc -l`
- Модули: посчитать build.gradle файлы
- APK: Android Studio → APK Analyzer

