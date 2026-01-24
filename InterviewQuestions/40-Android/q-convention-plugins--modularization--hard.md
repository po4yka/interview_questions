---
id: android-mod-006
title: "Gradle Convention Plugins / Gradle Convention плагины"
aliases: ["Convention Plugins", "Build Logic", "Convention плагины Gradle"]
topic: android
subtopics: [modularization, gradle, build-logic]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-module-types--modularization--medium, q-build-time-optimization--modularization--medium]
created: 2026-01-23
updated: 2026-01-23
sources: []
tags: [android/modularization, android/gradle, android/build-logic, difficulty/hard, convention-plugins]

---
# Вопрос (RU)

> Что такое Gradle Convention Plugins и как они обеспечивают консистентность в модульном проекте?

# Question (EN)

> What are Gradle Convention Plugins and how do they ensure consistency in a modular project?

---

## Ответ (RU)

**Convention Plugins** - переиспользуемые Gradle плагины, которые инкапсулируют общую конфигурацию сборки. Они устраняют дублирование и обеспечивают единообразие настроек во всех модулях.

### Проблема Без Convention Plugins

```kotlin
// feature/home/build.gradle.kts - копипаста в каждом модуле
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    compileSdk = 35

    defaultConfig {
        minSdk = 26
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs += listOf(
            "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi"
        )
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    // Повторяется в 20+ модулях...
}

// feature/profile/build.gradle.kts - та же копипаста
// feature/settings/build.gradle.kts - та же копипаста
```

### Решение: Convention Plugins

**Структура проекта**:
```
my-app/
  build-logic/
    convention/
      src/main/kotlin/
        AndroidApplicationConventionPlugin.kt
        AndroidLibraryConventionPlugin.kt
        AndroidFeatureConventionPlugin.kt
        AndroidComposeConventionPlugin.kt
        KotlinLibraryConventionPlugin.kt
      build.gradle.kts
    settings.gradle.kts
  app/
  feature/
  core/
  settings.gradle.kts
  build.gradle.kts
```

### Настройка build-logic Модуля

```kotlin
// build-logic/settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }

    versionCatalogs {
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}

rootProject.name = "build-logic"
include(":convention")
```

```kotlin
// build-logic/convention/build.gradle.kts
plugins {
    `kotlin-dsl`
}

group = "com.example.buildlogic"

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

dependencies {
    compileOnly(libs.android.gradlePlugin)
    compileOnly(libs.kotlin.gradlePlugin)
    compileOnly(libs.compose.gradlePlugin)
    compileOnly(libs.ksp.gradlePlugin)
}

tasks {
    validatePlugins {
        enableStricterValidation = true
        failOnWarning = true
    }
}

gradlePlugin {
    plugins {
        register("androidApplication") {
            id = "myapp.android.application"
            implementationClass = "AndroidApplicationConventionPlugin"
        }
        register("androidLibrary") {
            id = "myapp.android.library"
            implementationClass = "AndroidLibraryConventionPlugin"
        }
        register("androidFeature") {
            id = "myapp.android.feature"
            implementationClass = "AndroidFeatureConventionPlugin"
        }
        register("androidCompose") {
            id = "myapp.android.compose"
            implementationClass = "AndroidComposeConventionPlugin"
        }
        register("kotlinLibrary") {
            id = "myapp.kotlin.library"
            implementationClass = "KotlinLibraryConventionPlugin"
        }
    }
}
```

### Реализация Плагинов

```kotlin
// build-logic/convention/src/main/kotlin/AndroidLibraryConventionPlugin.kt
import com.android.build.api.dsl.LibraryExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure

class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            with(pluginManager) {
                apply("com.android.library")
                apply("org.jetbrains.kotlin.android")
            }

            extensions.configure<LibraryExtension> {
                configureKotlinAndroid(this)
                defaultConfig.targetSdk = 35
            }
        }
    }
}
```

```kotlin
// build-logic/convention/src/main/kotlin/KotlinAndroid.kt
import com.android.build.api.dsl.CommonExtension
import org.gradle.api.JavaVersion
import org.gradle.api.Project
import org.gradle.kotlin.dsl.withType
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

internal fun Project.configureKotlinAndroid(
    commonExtension: CommonExtension<*, *, *, *, *, *>,
) {
    commonExtension.apply {
        compileSdk = 35

        defaultConfig {
            minSdk = 26
            testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        }

        compileOptions {
            sourceCompatibility = JavaVersion.VERSION_17
            targetCompatibility = JavaVersion.VERSION_17
        }
    }

    tasks.withType<KotlinCompile>().configureEach {
        compilerOptions {
            jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
            freeCompilerArgs.addAll(
                "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi",
                "-opt-in=kotlinx.coroutines.FlowPreview"
            )
        }
    }
}
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidFeatureConventionPlugin.kt
import com.android.build.api.dsl.LibraryExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure
import org.gradle.kotlin.dsl.dependencies

class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply {
                apply("myapp.android.library")
                apply("myapp.android.compose")
                apply("com.google.dagger.hilt.android")
                apply("com.google.devtools.ksp")
            }

            extensions.configure<LibraryExtension> {
                testOptions.animationsDisabled = true
            }

            dependencies {
                add("implementation", project(":core:ui"))
                add("implementation", project(":core:domain"))
                add("implementation", libs.findLibrary("hilt.android").get())
                add("ksp", libs.findLibrary("hilt.compiler").get())
                add("implementation", libs.findLibrary("androidx.navigation.compose").get())
                add("implementation", libs.findLibrary("androidx.hilt.navigation.compose").get())

                // Testing
                add("testImplementation", project(":core:testing"))
                add("androidTestImplementation", project(":core:testing"))
            }
        }
    }
}
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidComposeConventionPlugin.kt
import com.android.build.api.dsl.CommonExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure
import org.gradle.kotlin.dsl.dependencies

class AndroidComposeConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("org.jetbrains.kotlin.plugin.compose")

            extensions.configure<CommonExtension<*, *, *, *, *, *>> {
                buildFeatures {
                    compose = true
                }
            }

            dependencies {
                val bom = libs.findLibrary("androidx.compose.bom").get()
                add("implementation", platform(bom))
                add("androidTestImplementation", platform(bom))
                add("implementation", libs.findLibrary("androidx.compose.ui").get())
                add("implementation", libs.findLibrary("androidx.compose.ui.tooling.preview").get())
                add("debugImplementation", libs.findLibrary("androidx.compose.ui.tooling").get())
                add("implementation", libs.findLibrary("androidx.compose.material3").get())
            }
        }
    }
}
```

### Использование в Модулях

```kotlin
// feature/home/build.gradle.kts - ЧИСТО!
plugins {
    alias(libs.plugins.myapp.android.feature)
}

android {
    namespace = "com.example.feature.home"
}

dependencies {
    // Только специфичные для модуля зависимости
    implementation(libs.coil.compose)
}
```

```kotlin
// core/domain/build.gradle.kts
plugins {
    alias(libs.plugins.myapp.kotlin.library)
}

dependencies {
    api(project(":core:model"))
    implementation(libs.kotlinx.coroutines.core)
}
```

```kotlin
// app/build.gradle.kts
plugins {
    alias(libs.plugins.myapp.android.application)
    alias(libs.plugins.myapp.android.compose)
}

android {
    namespace = "com.example.app"

    defaultConfig {
        applicationId = "com.example.app"
        versionCode = 1
        versionName = "1.0.0"
    }
}
```

### Version Catalog Integration

```toml
# gradle/libs.versions.toml
[versions]
androidGradlePlugin = "8.7.3"
kotlin = "2.1.0"
compose-compiler = "1.5.15"
hilt = "2.54"

[libraries]
android-gradlePlugin = { group = "com.android.tools.build", name = "gradle", version.ref = "androidGradlePlugin" }
kotlin-gradlePlugin = { group = "org.jetbrains.kotlin", name = "kotlin-gradle-plugin", version.ref = "kotlin" }
compose-gradlePlugin = { group = "org.jetbrains.kotlin", name = "compose-compiler-gradle-plugin", version.ref = "kotlin" }

[plugins]
myapp-android-application = { id = "myapp.android.application", version = "unspecified" }
myapp-android-library = { id = "myapp.android.library", version = "unspecified" }
myapp-android-feature = { id = "myapp.android.feature", version = "unspecified" }
myapp-android-compose = { id = "myapp.android.compose", version = "unspecified" }
myapp-kotlin-library = { id = "myapp.kotlin.library", version = "unspecified" }
```

```kotlin
// settings.gradle.kts (root)
pluginManagement {
    includeBuild("build-logic")
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
```

### Преимущества

| Аспект | Без Convention Plugins | С Convention Plugins |
|--------|------------------------|---------------------|
| Дублирование | 100+ строк в каждом модуле | 5-10 строк |
| Изменение SDK | Править 20+ файлов | Править 1 файл |
| Консистентность | Расхождения, ошибки | Гарантированная |
| Новый модуль | Копипаста, забыть что-то | 1 строка plugin |
| Обновление зависимостей | Везде вручную | Централизованно |

### Типичные Convention Plugins

| Плагин | Назначение |
|--------|------------|
| `myapp.android.application` | App module config |
| `myapp.android.library` | Library module config |
| `myapp.android.feature` | Feature module + Compose + Hilt + Navigation |
| `myapp.android.compose` | Compose setup |
| `myapp.kotlin.library` | Pure Kotlin module |
| `myapp.android.test` | Test utilities |

---

## Answer (EN)

**Convention Plugins** are reusable Gradle plugins that encapsulate common build configuration. They eliminate duplication and ensure uniform settings across all modules.

### The Problem Without Convention Plugins

```kotlin
// feature/home/build.gradle.kts - copy-paste in every module
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    compileSdk = 35

    defaultConfig {
        minSdk = 26
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs += listOf(
            "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi"
        )
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    // Repeated in 20+ modules...
}

// feature/profile/build.gradle.kts - same copy-paste
// feature/settings/build.gradle.kts - same copy-paste
```

### Solution: Convention Plugins

**Project structure**:
```
my-app/
  build-logic/
    convention/
      src/main/kotlin/
        AndroidApplicationConventionPlugin.kt
        AndroidLibraryConventionPlugin.kt
        AndroidFeatureConventionPlugin.kt
        AndroidComposeConventionPlugin.kt
        KotlinLibraryConventionPlugin.kt
      build.gradle.kts
    settings.gradle.kts
  app/
  feature/
  core/
  settings.gradle.kts
  build.gradle.kts
```

### Setting Up build-logic Module

```kotlin
// build-logic/settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }

    versionCatalogs {
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}

rootProject.name = "build-logic"
include(":convention")
```

```kotlin
// build-logic/convention/build.gradle.kts
plugins {
    `kotlin-dsl`
}

group = "com.example.buildlogic"

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

dependencies {
    compileOnly(libs.android.gradlePlugin)
    compileOnly(libs.kotlin.gradlePlugin)
    compileOnly(libs.compose.gradlePlugin)
    compileOnly(libs.ksp.gradlePlugin)
}

tasks {
    validatePlugins {
        enableStricterValidation = true
        failOnWarning = true
    }
}

gradlePlugin {
    plugins {
        register("androidApplication") {
            id = "myapp.android.application"
            implementationClass = "AndroidApplicationConventionPlugin"
        }
        register("androidLibrary") {
            id = "myapp.android.library"
            implementationClass = "AndroidLibraryConventionPlugin"
        }
        register("androidFeature") {
            id = "myapp.android.feature"
            implementationClass = "AndroidFeatureConventionPlugin"
        }
        register("androidCompose") {
            id = "myapp.android.compose"
            implementationClass = "AndroidComposeConventionPlugin"
        }
        register("kotlinLibrary") {
            id = "myapp.kotlin.library"
            implementationClass = "KotlinLibraryConventionPlugin"
        }
    }
}
```

### Plugin Implementation

```kotlin
// build-logic/convention/src/main/kotlin/AndroidLibraryConventionPlugin.kt
import com.android.build.api.dsl.LibraryExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure

class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            with(pluginManager) {
                apply("com.android.library")
                apply("org.jetbrains.kotlin.android")
            }

            extensions.configure<LibraryExtension> {
                configureKotlinAndroid(this)
                defaultConfig.targetSdk = 35
            }
        }
    }
}
```

```kotlin
// build-logic/convention/src/main/kotlin/KotlinAndroid.kt
import com.android.build.api.dsl.CommonExtension
import org.gradle.api.JavaVersion
import org.gradle.api.Project
import org.gradle.kotlin.dsl.withType
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

internal fun Project.configureKotlinAndroid(
    commonExtension: CommonExtension<*, *, *, *, *, *>,
) {
    commonExtension.apply {
        compileSdk = 35

        defaultConfig {
            minSdk = 26
            testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        }

        compileOptions {
            sourceCompatibility = JavaVersion.VERSION_17
            targetCompatibility = JavaVersion.VERSION_17
        }
    }

    tasks.withType<KotlinCompile>().configureEach {
        compilerOptions {
            jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
            freeCompilerArgs.addAll(
                "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi",
                "-opt-in=kotlinx.coroutines.FlowPreview"
            )
        }
    }
}
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidFeatureConventionPlugin.kt
import com.android.build.api.dsl.LibraryExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure
import org.gradle.kotlin.dsl.dependencies

class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply {
                apply("myapp.android.library")
                apply("myapp.android.compose")
                apply("com.google.dagger.hilt.android")
                apply("com.google.devtools.ksp")
            }

            extensions.configure<LibraryExtension> {
                testOptions.animationsDisabled = true
            }

            dependencies {
                add("implementation", project(":core:ui"))
                add("implementation", project(":core:domain"))
                add("implementation", libs.findLibrary("hilt.android").get())
                add("ksp", libs.findLibrary("hilt.compiler").get())
                add("implementation", libs.findLibrary("androidx.navigation.compose").get())
                add("implementation", libs.findLibrary("androidx.hilt.navigation.compose").get())

                // Testing
                add("testImplementation", project(":core:testing"))
                add("androidTestImplementation", project(":core:testing"))
            }
        }
    }
}
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidComposeConventionPlugin.kt
import com.android.build.api.dsl.CommonExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure
import org.gradle.kotlin.dsl.dependencies

class AndroidComposeConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("org.jetbrains.kotlin.plugin.compose")

            extensions.configure<CommonExtension<*, *, *, *, *, *>> {
                buildFeatures {
                    compose = true
                }
            }

            dependencies {
                val bom = libs.findLibrary("androidx.compose.bom").get()
                add("implementation", platform(bom))
                add("androidTestImplementation", platform(bom))
                add("implementation", libs.findLibrary("androidx.compose.ui").get())
                add("implementation", libs.findLibrary("androidx.compose.ui.tooling.preview").get())
                add("debugImplementation", libs.findLibrary("androidx.compose.ui.tooling").get())
                add("implementation", libs.findLibrary("androidx.compose.material3").get())
            }
        }
    }
}
```

### Usage in Modules

```kotlin
// feature/home/build.gradle.kts - CLEAN!
plugins {
    alias(libs.plugins.myapp.android.feature)
}

android {
    namespace = "com.example.feature.home"
}

dependencies {
    // Only module-specific dependencies
    implementation(libs.coil.compose)
}
```

```kotlin
// core/domain/build.gradle.kts
plugins {
    alias(libs.plugins.myapp.kotlin.library)
}

dependencies {
    api(project(":core:model"))
    implementation(libs.kotlinx.coroutines.core)
}
```

```kotlin
// app/build.gradle.kts
plugins {
    alias(libs.plugins.myapp.android.application)
    alias(libs.plugins.myapp.android.compose)
}

android {
    namespace = "com.example.app"

    defaultConfig {
        applicationId = "com.example.app"
        versionCode = 1
        versionName = "1.0.0"
    }
}
```

### Version Catalog Integration

```toml
# gradle/libs.versions.toml
[versions]
androidGradlePlugin = "8.7.3"
kotlin = "2.1.0"
compose-compiler = "1.5.15"
hilt = "2.54"

[libraries]
android-gradlePlugin = { group = "com.android.tools.build", name = "gradle", version.ref = "androidGradlePlugin" }
kotlin-gradlePlugin = { group = "org.jetbrains.kotlin", name = "kotlin-gradle-plugin", version.ref = "kotlin" }
compose-gradlePlugin = { group = "org.jetbrains.kotlin", name = "compose-compiler-gradle-plugin", version.ref = "kotlin" }

[plugins]
myapp-android-application = { id = "myapp.android.application", version = "unspecified" }
myapp-android-library = { id = "myapp.android.library", version = "unspecified" }
myapp-android-feature = { id = "myapp.android.feature", version = "unspecified" }
myapp-android-compose = { id = "myapp.android.compose", version = "unspecified" }
myapp-kotlin-library = { id = "myapp.kotlin.library", version = "unspecified" }
```

```kotlin
// settings.gradle.kts (root)
pluginManagement {
    includeBuild("build-logic")
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
```

### Benefits

| Aspect | Without Convention Plugins | With Convention Plugins |
|--------|---------------------------|------------------------|
| Duplication | 100+ lines per module | 5-10 lines |
| SDK change | Edit 20+ files | Edit 1 file |
| Consistency | Drift, errors | Guaranteed |
| New module | Copy-paste, forget things | 1 line plugin |
| Dependency updates | Manual everywhere | Centralized |

### Typical Convention Plugins

| Plugin | Purpose |
|--------|---------|
| `myapp.android.application` | App module config |
| `myapp.android.library` | Library module config |
| `myapp.android.feature` | Feature module + Compose + Hilt + Navigation |
| `myapp.android.compose` | Compose setup |
| `myapp.kotlin.library` | Pure Kotlin module |
| `myapp.android.test` | Test utilities |

---

## Follow-ups

- How do you test convention plugins?
- How do you handle module-specific overrides?
- What's the difference between `buildSrc` and composite builds for convention plugins?

## References

- https://developer.android.com/build/migrate-to-catalogs
- https://github.com/android/nowinandroid/tree/main/build-logic
- https://docs.gradle.org/current/samples/sample_convention_plugins.html

## Related Questions

### Prerequisites

- [[q-module-types--modularization--medium]] - Module types overview
- [[q-gradle-basics--android--easy]] - Gradle fundamentals

### Related

- [[q-build-time-optimization--modularization--medium]] - Build performance
- [[q-api-vs-implementation--modularization--medium]] - Dependency configurations

### Advanced

- [[q-module-dependency-graph--modularization--hard]] - Graph design
- [[q-ci-cd-android--android--hard]] - CI/CD integration
