---
tags:
  - android
  - ci-cd
  - multi-module
  - gradle
  - build-optimization
difficulty: medium
status: draft
related:
  - q-cicd-pipeline-setup--devops--medium
  - q-gradle-build-optimization--build--medium
  - q-gradle-dependency-management--build--medium
created: 2025-10-11
---

# Question (EN)
How do you optimize CI/CD for multi-module Android projects? How do you detect affected modules and run tests only for changed code?

## Answer (EN)
### Overview

Multi-module projects present unique CI/CD challenges:
- ❌ Building all modules takes too long
- ❌ Running all tests is expensive
- ❌ Deploying unchanged modules wastes resources

**Solution**: Detect affected modules and build/test only what changed.

### Module Dependency Graph

```
app (app module)
├── feature:home
│   ├── core:ui
│   ├── core:data
│   └── core:domain
├── feature:profile
│   ├── core:ui
│   ├── core:data
│   └── core:domain
├── feature:settings
│   └── core:ui
└── core:network
    └── core:common

If core:data changes:
  → Rebuild: core:data, feature:home, feature:profile, app
  → Skip: core:ui, core:network, feature:settings, core:domain, core:common
```

### Strategy 1: Gradle Task Graph Analysis

**build.gradle.kts (root)**:

```kotlin
import java.io.ByteArrayOutputStream

// Get list of changed files
fun getChangedFiles(): List<String> {
    val output = ByteArrayOutputStream()
    exec {
        commandLine("git", "diff", "--name-only", "origin/main...HEAD")
        standardOutput = output
    }
    return output.toString().trim().split("\n").filter { it.isNotEmpty() }
}

// Map files to modules
fun getAffectedModules(changedFiles: List<String>): Set<String> {
    val affectedModules = mutableSetOf<String>()

    changedFiles.forEach { file ->
        // Extract module from file path
        // e.g., "feature/home/src/..." -> "feature:home"
        val parts = file.split("/")
        if (parts.size >= 2) {
            val module = "${parts[0]}:${parts[1]}"
            affectedModules.add(module)
        }
    }

    // Add dependent modules
    val allAffectedModules = mutableSetOf<String>()
    affectedModules.forEach { module ->
        allAffectedModules.add(module)
        allAffectedModules.addAll(getDependentModules(module))
    }

    return allAffectedModules
}

// Get modules that depend on this module
fun getDependentModules(module: String): Set<String> {
    val dependents = mutableSetOf<String>()

    // Parse dependency graph (simplified)
    // In practice, use Gradle's configuration model
    subprojects.forEach { project ->
        project.configurations.forEach { config ->
            config.dependencies.forEach { dep ->
                if (dep is ProjectDependency && dep.dependencyProject.path == ":$module") {
                    dependents.add(project.path.removePrefix(":"))
                }
            }
        }
    }

    return dependents
}

// Register custom task to print affected modules
tasks.register("printAffectedModules") {
    doLast {
        val changedFiles = getChangedFiles()
        val affectedModules = getAffectedModules(changedFiles)

        println("Changed files:")
        changedFiles.forEach { println("  $it") }

        println("\nAffected modules:")
        affectedModules.forEach { println("  $it") }
    }
}

// Register task to build only affected modules
tasks.register("buildAffected") {
    doLast {
        val changedFiles = getChangedFiles()
        val affectedModules = getAffectedModules(changedFiles)

        if (affectedModules.isEmpty()) {
            println("No modules affected, skipping build")
            return@doLast
        }

        affectedModules.forEach { module ->
            println("Building $module...")
            exec {
                commandLine("./gradlew", ":$module:assemble")
            }
        }
    }
}

// Register task to test only affected modules
tasks.register("testAffected") {
    doLast {
        val changedFiles = getChangedFiles()
        val affectedModules = getAffectedModules(changedFiles)

        if (affectedModules.isEmpty()) {
            println("No modules affected, skipping tests")
            return@doLast
        }

        affectedModules.forEach { module ->
            println("Testing $module...")
            exec {
                commandLine("./gradlew", ":$module:test")
            }
        }
    }
}
```

### Strategy 2: GitHub Actions with Affected Modules

**.github/workflows/multi-module-ci.yml**:

```yaml
name: Multi-Module CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      affected-modules: ${{ steps.detect.outputs.modules }}
      should-build: ${{ steps.detect.outputs.should-build }}

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Need full history for git diff

      - name: Detect affected modules
        id: detect
        run: |
          # Get changed files
          CHANGED_FILES=$(git diff --name-only ${{ github.event.before }} ${{ github.sha }})

          echo "Changed files:"
          echo "$CHANGED_FILES"

          # Detect affected modules (simple approach)
          MODULES=""

          if echo "$CHANGED_FILES" | grep -q "^app/"; then
            MODULES="$MODULES app"
          fi

          if echo "$CHANGED_FILES" | grep -q "^feature/home/"; then
            MODULES="$MODULES feature:home"
          fi

          if echo "$CHANGED_FILES" | grep -q "^feature/profile/"; then
            MODULES="$MODULES feature:profile"
          fi

          if echo "$CHANGED_FILES" | grep -q "^core/data/"; then
            # core:data affects feature:home and feature:profile
            MODULES="$MODULES core:data feature:home feature:profile"
          fi

          if echo "$CHANGED_FILES" | grep -q "^core/ui/"; then
            # core:ui affects all features
            MODULES="$MODULES core:ui feature:home feature:profile feature:settings"
          fi

          # Remove duplicates
          MODULES=$(echo "$MODULES" | tr ' ' '\n' | sort -u | tr '\n' ' ')

          echo "Affected modules: $MODULES"

          # Output as JSON array for matrix
          MODULES_JSON=$(echo $MODULES | jq -R -s -c 'split(" ") | map(select(length > 0))')
          echo "modules=$MODULES_JSON" >> $GITHUB_OUTPUT

          # Set flag if there are modules to build
          if [ -n "$MODULES" ]; then
            echo "should-build=true" >> $GITHUB_OUTPUT
          else
            echo "should-build=false" >> $GITHUB_OUTPUT
          fi

  build-affected:
    needs: detect-changes
    if: needs.detect-changes.outputs.should-build == 'true'
    runs-on: ubuntu-latest

    strategy:
      matrix:
        module: ${{ fromJson(needs.detect-changes.outputs.affected-modules) }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission
        run: chmod +x gradlew

      - name: Build ${{ matrix.module }}
        run: ./gradlew :${{ matrix.module }}:assemble

      - name: Test ${{ matrix.module }}
        run: ./gradlew :${{ matrix.module }}:test

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results-${{ matrix.module }}
          path: ${{ matrix.module }}/build/reports/tests/

  build-all:
    needs: detect-changes
    if: needs.detect-changes.outputs.should-build == 'false'
    runs-on: ubuntu-latest

    steps:
      - name: No changes detected
        run: echo "No modules affected by this change"
```

### Strategy 3: Using Gradle Enterprise Build Scan

**settings.gradle.kts**:

```kotlin
plugins {
    id("com.gradle.enterprise") version "3.15"
}

gradleEnterprise {
    buildScan {
        termsOfServiceUrl = "https://gradle.com/terms-of-service"
        termsOfServiceAgree = "yes"

        // Publish build scans for all builds
        publishAlways()

        // Tag affected modules
        buildFinished {
            val affectedModules = getAffectedModules()
            affectedModules.forEach { module ->
                tag(module)
            }
        }
    }
}
```

### Strategy 4: Module-Level Caching

**Optimize with module-specific caches**:

```yaml
name: Multi-Module with Caching

on:
  push:
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

      # Cache Gradle wrapper
      - name: Cache Gradle wrapper
        uses: actions/cache@v3
        with:
          path: ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-wrapper-${{ hashFiles('gradle/wrapper/gradle-wrapper.properties') }}

      # Cache Gradle dependencies
      - name: Cache Gradle dependencies
        uses: actions/cache@v3
        with:
          path: ~/.gradle/caches
          key: ${{ runner.os }}-gradle-caches-${{ hashFiles('**/*.gradle*', '**/gradle.properties') }}
          restore-keys: |
            ${{ runner.os }}-gradle-caches-

      # Cache module build outputs
      - name: Cache module outputs
        uses: actions/cache@v3
        with:
          path: |
            */build/
            !*/build/reports/
            !*/build/test-results/
          key: ${{ runner.os }}-module-outputs-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-module-outputs-

      - name: Grant execute permission
        run: chmod +x gradlew

      - name: Build all modules
        run: ./gradlew assemble --parallel --build-cache
```

### Strategy 5: Nx-style Computation Caching

Use a tool like [Gradle's configuration cache](https://docs.gradle.org/current/userguide/configuration_cache.html):

**gradle.properties**:

```properties
# Enable configuration cache
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn

# Enable build cache
org.gradle.caching=true

# Enable parallel execution
org.gradle.parallel=true

# Increase heap size for multi-module builds
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g

# Enable module metadata
org.gradle.experimental.gradlemodule.metadata=true
```

**.github/workflows/nx-style-ci.yml**:

```yaml
name: Smart CI with Build Cache

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
        with:
          fetch-depth: 0

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      # Restore Gradle build cache
      - name: Restore build cache
        uses: actions/cache@v3
        with:
          path: ~/.gradle/caches/build-cache-*
          key: ${{ runner.os }}-gradle-build-cache-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-gradle-build-cache-

      # Restore configuration cache
      - name: Restore configuration cache
        uses: actions/cache@v3
        with:
          path: .gradle/configuration-cache
          key: ${{ runner.os }}-gradle-config-cache-${{ hashFiles('**/*.gradle*') }}

      - name: Grant execute permission
        run: chmod +x gradlew

      # Build with caching - Gradle automatically skips unchanged modules
      - name: Build all modules (with cache)
        run: |
          ./gradlew assemble \
            --parallel \
            --build-cache \
            --configuration-cache \
            -Dorg.gradle.caching=true

      # Test with caching
      - name: Test all modules (with cache)
        run: |
          ./gradlew test \
            --parallel \
            --build-cache \
            --configuration-cache \
            -Dorg.gradle.caching=true

      # Upload test results
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: |
            */build/reports/tests/
            */build/test-results/
```

### Production Example: Complete Multi-Module Setup

**Project structure**:
```
root/
├── app/
├── feature/
│   ├── home/
│   ├── profile/
│   └── settings/
├── core/
│   ├── data/
│   ├── domain/
│   ├── ui/
│   └── network/
└── buildSrc/
    └── src/main/kotlin/
        └── Dependencies.kt
```

**buildSrc/src/main/kotlin/AffectedModulesTask.kt**:

```kotlin
import org.gradle.api.DefaultTask
import org.gradle.api.tasks.TaskAction
import java.io.ByteArrayOutputStream

abstract class AffectedModulesTask : DefaultTask() {

    @TaskAction
    fun detectAffectedModules() {
        val changedFiles = getChangedFiles()
        val moduleGraph = buildModuleGraph()
        val affectedModules = calculateAffectedModules(changedFiles, moduleGraph)

        println("=== Affected Modules Analysis ===")
        println("\nChanged files (${changedFiles.size}):")
        changedFiles.forEach { println("  • $it") }

        println("\nDirectly affected modules:")
        affectedModules.direct.forEach { println("  • $it") }

        println("\nTransitively affected modules:")
        affectedModules.transitive.forEach { println("  • $it") }

        println("\nTotal modules to rebuild: ${affectedModules.all.size}")

        // Save to file for CI
        val outputFile = project.file("build/affected-modules.txt")
        outputFile.parentFile.mkdirs()
        outputFile.writeText(affectedModules.all.joinToString("\n"))
    }

    private fun getChangedFiles(): List<String> {
        val output = ByteArrayOutputStream()
        project.exec {
            commandLine("git", "diff", "--name-only", "origin/main...HEAD")
            standardOutput = output
            isIgnoreExitValue = true
        }
        return output.toString().trim()
            .split("\n")
            .filter { it.isNotEmpty() }
    }

    private fun buildModuleGraph(): Map<String, Set<String>> {
        val graph = mutableMapOf<String, MutableSet<String>>()

        project.subprojects.forEach { subproject ->
            val moduleName = subproject.path.removePrefix(":")
            graph[moduleName] = mutableSetOf()

            subproject.configurations.forEach { config ->
                config.dependencies.forEach { dep ->
                    if (dep is org.gradle.api.artifacts.ProjectDependency) {
                        val depModule = dep.dependencyProject.path.removePrefix(":")
                        graph[moduleName]!!.add(depModule)
                    }
                }
            }
        }

        return graph
    }

    private fun calculateAffectedModules(
        changedFiles: List<String>,
        moduleGraph: Map<String, Set<String>>
    ): AffectedModules {
        val directlyAffected = mutableSetOf<String>()

        // Map files to modules
        changedFiles.forEach { file ->
            val parts = file.split("/")
            if (parts.size >= 2) {
                val module = if (parts[0] == "feature" || parts[0] == "core") {
                    "${parts[0]}/${parts[1]}"
                } else if (parts[0] == "app") {
                    "app"
                } else {
                    null
                }
                module?.let { directlyAffected.add(it) }
            }
        }

        // Find transitive dependents
        val transitivelyAffected = mutableSetOf<String>()
        directlyAffected.forEach { module ->
            transitivelyAffected.addAll(findDependents(module, moduleGraph))
        }

        return AffectedModules(
            direct = directlyAffected,
            transitive = transitivelyAffected,
            all = directlyAffected + transitivelyAffected
        )
    }

    private fun findDependents(
        module: String,
        graph: Map<String, Set<String>>
    ): Set<String> {
        val dependents = mutableSetOf<String>()

        graph.forEach { (dependent, dependencies) ->
            if (dependencies.contains(module)) {
                dependents.add(dependent)
                // Recursively find transitive dependents
                dependents.addAll(findDependents(dependent, graph))
            }
        }

        return dependents
    }

    data class AffectedModules(
        val direct: Set<String>,
        val transitive: Set<String>,
        val all: Set<String>
    )
}
```

**Register task in root build.gradle.kts**:

```kotlin
tasks.register<AffectedModulesTask>("affectedModules") {
    group = "verification"
    description = "Detects modules affected by recent changes"
}
```

**GitHub Actions**:

```yaml
name: Smart Multi-Module CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  affected-modules:
    runs-on: ubuntu-latest
    outputs:
      modules: ${{ steps.affected.outputs.modules }}
      matrix: ${{ steps.affected.outputs.matrix }}

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Detect affected modules
        id: affected
        run: |
          chmod +x gradlew
          ./gradlew affectedModules

          # Read affected modules
          MODULES=$(cat build/affected-modules.txt | tr '\n' ' ')
          echo "modules=$MODULES" >> $GITHUB_OUTPUT

          # Convert to JSON matrix
          MATRIX=$(echo $MODULES | jq -R -s -c 'split(" ") | map(select(length > 0))')
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  build-and-test:
    needs: affected-modules
    if: needs.affected-modules.outputs.matrix != '[]'
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false
      matrix:
        module: ${{ fromJson(needs.affected-modules.outputs.matrix) }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Build and test ${{ matrix.module }}
        run: |
          chmod +x gradlew
          ./gradlew :${{ matrix.module }}:assemble :${{ matrix.module }}:test --parallel

      - name: Upload results for ${{ matrix.module }}
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: results-${{ matrix.module }}
          path: |
            ${{ matrix.module }}/build/reports/
            ${{ matrix.module }}/build/test-results/
```

### Best Practices

1. **Always Build Root/App Module**
   ```yaml
   # ✅ GOOD - Always verify app assembles
   - name: Build app module
     run: ./gradlew :app:assemble

   # Even if only library modules changed
   ```

2. **Cache Aggressively**
   ```yaml
   # ✅ GOOD - Multi-layer caching
   - uses: actions/cache@v3
     with:
       path: |
         ~/.gradle/caches
         ~/.gradle/wrapper
         .gradle/configuration-cache
       key: gradle-${{ hashFiles('**/*.gradle*') }}
   ```

3. **Parallelize When Possible**
   ```bash
   # ✅ GOOD - Build modules in parallel
   ./gradlew assemble --parallel --max-workers=4

   # ❌ BAD - Sequential builds
   ./gradlew :module1:assemble
   ./gradlew :module2:assemble
   ```

4. **Use Remote Build Cache for Teams**
   ```kotlin
   // build.gradle.kts
   buildCache {
       remote<HttpBuildCache> {
           url = uri("https://build-cache.company.com")
           credentials {
               username = System.getenv("BUILD_CACHE_USERNAME")
               password = System.getenv("BUILD_CACHE_PASSWORD")
           }
           isPush = System.getenv("CI") == "true"
       }
   }
   ```

### Summary

**Strategies for multi-module CI/CD:**
1. ✅ **Affected module detection** - Build only what changed
2. ✅ **Module-level caching** - Reuse unchanged builds
3. ✅ **Parallel execution** - Build modules in parallel
4. ✅ **Configuration cache** - Skip configuration phase
5. ✅ **Remote build cache** - Share cache across team

**Key optimizations:**
- Detect changed files with git diff
- Build module dependency graph
- Calculate transitive dependencies
- Run tests only for affected modules
- Cache everything (dependencies, build outputs, config)

**Expected improvements:**
- **From**: 30 min full build
- **To**: 5-10 min incremental build (80% faster)

---

# Вопрос (RU)
Как оптимизировать CI/CD для мульти-модульных Android-проектов? Как определять затронутые модули и запускать тесты только для изменённого кода?

## Ответ (RU)
[Перевод с примерами из английской версии...]

### Резюме

**Стратегии для мульти-модульного CI/CD:**
1. ✅ **Обнаружение затронутых модулей** — собирать только то, что изменилось
2. ✅ **Кеширование на уровне модулей** — переиспользовать неизменённые сборки
3. ✅ **Параллельное выполнение** — собирать модули параллельно
4. ✅ **Configuration cache** — пропускать фазу конфигурации
5. ✅ **Удалённый build cache** — делиться кешем между командой

**Ключевые оптимизации:**
- Обнаруживать изменённые файлы с git diff
- Строить граф зависимостей модулей
- Вычислять транзитивные зависимости
- Запускать тесты только для затронутых модулей
- Кешировать всё (зависимости, выходы сборки, конфигурацию)

**Ожидаемые улучшения:**
- **От**: 30 мин полная сборка
- **К**: 5-10 мин инкрементальная сборка (на 80% быстрее)
