---
id: android-011
title: Gradle Build System / Система сборки Gradle
aliases:
- Gradle Build System
- Система сборки Gradle
topic: android
status: draft
created: 2025-10-05
updated: 2025-11-10
difficulty: medium
subtopics:
- build-variants
- dependency-management
- gradle
question_kind: theory
original_language: en
language_tags:
- en
- ru
tags:
- android/build-variants
- android/dependency-management
- android/gradle
- build-system
- dependency-management
- difficulty/medium
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20Gradle.md
related:
- c-gradle
- q-cache-implementation-strategies--android--medium
- q-kapt-vs-ksp--android--medium
- q-what-unites-the-main-components-of-an-android-application--android--medium
moc: moc-android

---

# Вопрос (RU)
> Что такое система сборки Gradle в Android и какие ключевые понятия (типы сборки, product flavors, build variants, настройки манифеста, зависимости, подпись, shrink, multiple APK, конфигурационные файлы) нужно знать для собеседования?

# Question (EN)
> What is the Gradle build system in Android, and which key concepts (build types, product flavors, build variants, manifest configuration, dependencies, signing, shrinking, multiple APKs, configuration files) should you know for an interview?

---

## Ответ (RU)
### Что такое Gradle?

Gradle — это инструмент автоматизации сборки с открытым исходным кодом, достаточно гибкий для сборки почти любого типа программного обеспечения. Gradle делает мало предположений о том, что вы собираете и как вы это делаете, что делает его особенно гибким.

### Gradle в Android

Android Studio использует Gradle для автоматизации и управления процессом сборки, позволяя определять гибкие, настраиваемые конфигурации сборки.

**Ключевые компоненты:**
- **Gradle**: инструментарий для сборки.
- **Android Gradle Plugin (AGP)**: интегрируется с Gradle и предоставляет задачи, соглашения и настраиваемые параметры, специфичные для сборки и тестирования Android-приложений.

**Ключевые возможности:**
- Каждая конфигурация сборки может определять свой собственный набор кода и ресурсов.
- Общие части кода и ресурсов могут использоваться совместно между вариантами.
- Сборка может выполняться независимо от Android Studio (командная строка, CI/CD-серверы).

### Поддержка языков

Gradle использует скрипты на:
- **Groovy DSL** (Domain Specific Language) — традиционный синтаксис.
- **Kotlin DSL** — современная, типобезопасная альтернатива.

### Глоссарий сборки Android

Gradle и плагин Android Gradle помогают настраивать следующие аспекты сборки:

#### 1. Типы сборки (Build Types)

**Определение**: типы сборки определяют свойства, которые Gradle использует при сборке и упаковке приложения.

**Характеристики:**
- Обычно настраиваются для разных этапов жизненного цикла разработки.
- Должен быть определён как минимум один тип сборки.
- Android Studio по умолчанию создаёт типы сборки `debug` и `release`.

**Примеры:**
- **Тип сборки Debug**: включает параметры отладки, по умолчанию использует отладочную конфигурацию подписания.
- **Тип сборки Release**: обычно включает сжатие/обфускацию кода и использует релизную конфигурацию подписания для распространения.

**Пример кода (Kotlin DSL, стиль AGP 8+):**
```kotlin
android {
    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            isDebuggable = true
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
```

#### 2. Варианты продукта (Product Flavors)

**Определение**: варианты продукта представляют разные версии приложения, которые можно выпускать для пользователей.

**Характеристики:**
- Опциональны и создаются вручную.
- Могут использовать различный код и ресурсы.
- Общие части могут переиспользоваться между вариантами.

**Примеры:**
- Бесплатная и платная версии.
- Различные white-label версии.
- Версии, специфичные для определённых уровней API.

**Пример кода:**
```kotlin
android {
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
}
```

#### 3. Варианты сборки (Build Variants)

**Определение**: вариант сборки — это декартово произведение типа сборки и по одному варианту продукта из каждого измерения.

**Характеристики:**
- Представляет конкретную конфигурацию, которую Gradle использует для сборки приложения.
- Не настраивается напрямую — формируется из типов сборки, вариантов продукта и их настроек.
- Используется для сборки различных версий во время разработки и для публикации.

**Примеры:**
- Если есть типы сборки `debug` и `release`,
- и варианты продукта `free` и `paid`,
- получится 4 варианта сборки:
  - `freeDebug`
  - `freeRelease`
  - `paidDebug`
  - `paidRelease`

#### 4. Записи манифеста (Manifest Entries)

**Определение**: некоторые свойства манифеста (например, `applicationId`, `versionName`, плейсхолдеры) могут настраиваться для разных типов сборки и вариантов продукта, чтобы итоговый манифест варианта получал нужные значения.

**Характеристики:**
- Значения из `defaultConfig`, `buildTypes`, `productFlavors` и `manifestPlaceholders` могут переопределять или параметризовать значения в `AndroidManifest.xml`.
- Полезно для генерации нескольких вариантов с различными свойствами (например, разные authorities, схемы).
- Инструмент слияния манифестов объединяет настройки из всех источников манифестов.

**Пример кода:**
```kotlin
android {
    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
}
```

#### 5. Зависимости (Dependencies)

**Определение**: система сборки управляет зависимостями проекта из локальной файловой системы и удалённых репозиториев.

**Преимущества:**
- Не нужно вручную искать, загружать и копировать бинарные пакеты.
- Автоматическое разрешение зависимостей.
- Поддержка транзитивных зависимостей.

**Пример кода:**
```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
}
```

#### 6. Подписание (Signing)

**Определение**: система сборки позволяет указать настройки подписания в конфигурации сборки.

**Характеристики:**
- Может автоматически подписывать приложение во время сборки, если для типа сборки задана конфигурация подписания.
- Debug-версии: подписываются отладочным ключом по умолчанию.
- Release-версии: по умолчанию не подписаны; обычно настраиваются с собственной конфигурацией подписания для публикации.

**Пример кода (НЕ хардкодить секреты в реальных проектах):**
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("keystore.jks")
            storePassword = "password"
            keyAlias = "key"
            keyPassword = "password"
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

#### 7. Сжатие кода и ресурсов

**Определение**: система сборки позволяет включать сжатие кода и ресурсов для отдельных типов/вариантов сборки и задавать отдельные файлы правил.

**Возможности:**
- Используется R8 как стандартный инструмент shrink/obfuscate.
- Уменьшает объём кода и ресурсов.
- Помогает снизить размер APK или AAB.
- Для разных вариантов можно использовать разные правила.

**Пример кода:**
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

#### 8. Поддержка нескольких APK

**Определение**: система сборки может автоматически собирать разные APK из одного модуля для разных конфигураций устройств.

**Возможности:**
- Каждый APK содержит только код и ресурсы, необходимые для конкретных конфигураций.
- Можно разделять по плотности экрана.
- Можно разделять по ABI (`Application` Binary Interface).

**Пример кода (ABI splits):**
```kotlin
android {
    splits {
        abi {
            isEnable = true // Для блока abi splits используется isEnable в Kotlin DSL
            reset()
            include("x86", "x86_64", "armeabi-v7a", "arm64-v8a")
            isUniversalApk = true
        }
    }
}
```

### Файлы конфигурации сборки

При создании нового проекта Android Studio автоматически создаёт Gradle-файлы на основе разумных значений по умолчанию.

#### Структура файлов проекта

```
 MyApp/                    # Проект
     build.gradle.kts      # Файл сборки верхнего уровня
     settings.gradle.kts   # Файл настроек
     app/                  # Модуль
         build.gradle.kts  # Файл сборки уровня модуля
         libs/
         src/
             main/         # Набор исходников
                 java/
                    com.example.myapp
                 res/
                    drawable/
                    values/
                    ...
                 AndroidManifest.xml
```

#### 1. Файл настроек Gradle

**Файл**: `settings.gradle.kts` (Kotlin DSL) или `settings.gradle` (Groovy DSL)

**Расположение**: корневая директория проекта.

**Назначение**:
- Определяет настройки репозиториев и управления плагинами на уровне проекта.
- Указывает, какие модули включать при сборке приложения.
- В многомодульных проектах каждый модуль должен быть явно включён, чтобы участвовать в сборке.

**Пример:**
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
```

#### 2. Файл сборки верхнего уровня

**Файл**: `build.gradle.kts` (Kotlin DSL) или `build.gradle` (Groovy DSL)

**Расположение**: корневая директория проекта.

**Назначение**:
- Задаёт версии и подключает плагины, используемые модулями (через `apply false`).
- Опционально содержит общие настройки или зависимости для модулей.
- Часто содержит вспомогательные задачи (например, `clean`) для всего проекта.

**Пример:**
```kotlin
plugins {
    id("com.android.application") version "8.1.0" apply false
    id("com.android.library") version "8.1.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
```

#### 3. Файл сборки уровня модуля

**Файл**: `build.gradle.kts` (Kotlin DSL) или `build.gradle` (Groovy DSL)

**Расположение**: каждая директория `project/module/`.

**Назначение**:
- Настраивает параметры сборки для конкретного модуля.
- Определяет параметры упаковки.
- Определяет дополнительные типы сборки и варианты продукта.
- Уточняет или переопределяет настройки относительно файла сборки верхнего уровня.

**Пример:**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
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
    implementation("androidx.appcompat:appcompat:1.6.1")
}
```

#### 4. Файлы свойств Gradle

Два файла свойств в корневой директории проекта задают настройки для инструментария сборки Gradle:

**`gradle.properties`**:
- Настройки Gradle на уровне проекта.
- Пример: максимальный размер кучи Gradle Daemon.

```properties
org.gradle.jvmargs=-Xmx2048m
android.useAndroidX=true
kotlin.code.style=official
```

**`local.properties`**:
- Настройки локального окружения.
- Не добавляется в систему контроля версий.
- Распространённые свойства:
  - `sdk.dir` — путь к Android SDK.
  - `ndk.dir` — путь к NDK (устарело, предпочтительно использовать NDK через SDK).
  - `cmake.dir` — путь к CMake.
  - `ndk.symlinkdir` — символьная ссылка на NDK (Android Studio 3.5+).

```properties
sdk.dir=/Users/username/Library/Android/sdk
```

---

## Answer (EN)
### What is Gradle?

Gradle is an open-source build automation tool flexible enough to build almost any type of software. Gradle makes few assumptions about what you're trying to build or how to build it, which makes it particularly flexible.

### Gradle in Android

Android Studio uses Gradle to automate and manage the build process while letting you define flexible, custom build configurations.

**Key components:**
- **Gradle**: The build toolkit.
- **Android Gradle Plugin (AGP)**: Integrates with Gradle to provide tasks, conventions, and configurable settings specific to building and testing Android apps.

**Key features:**
- Each build configuration can define its own set of code and resources.
- Common code and resources can be shared across variants.
- Builds can run independently of Android Studio (command line, CI/CD servers).

### Language Support

Gradle build scripts use:
- **Groovy DSL** (Domain Specific Language) — traditional syntax.
- **Kotlin DSL** — modern, type-safe alternative.

### Android Build Glossary

Gradle and the Android Gradle Plugin help you configure the following aspects of your build:

#### 1. Build Types

**Definition**: Build types define properties that Gradle uses when building and packaging your app.

**Characteristics:**
- Typically configured for different stages of your development lifecycle.
- At least one build type must be defined.
- Android Studio creates `debug` and `release` build types by default.

**Examples:**
- **Debug build type**: Enables debug options, uses the debug signing config by default.
- **Release build type**: Typically enables code shrinking/obfuscation and uses a release signing config for distribution.

**Code example (Kotlin DSL, AGP 8+ style):**
```kotlin
android {
    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            isDebuggable = true
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
```

#### 2. Product Flavors

**Definition**: Product flavors represent different variants of your app that you can release to users.

**Characteristics:**
- Optional — must be created manually.
- Can use different code and resources.
- Share and reuse parts common to all versions.

**Examples:**
- Free and paid versions.
- Different white-label versions.
- API-level specific versions.

**Code example:**
```kotlin
android {
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
}
```

#### 3. Build Variants

**Definition**: A build variant is the cross-product of a build type and one flavor from each flavor dimension.

**Characteristics:**
- Represents the concrete configuration Gradle uses to build your app.
- Not configured directly — formed from build types, product flavors, and their settings.
- Used to build different versions during development and for distribution.

**Examples:**
- With `debug` and `release` build types,
- and `free` and `paid` product flavors,
- you get 4 build variants:
  - `freeDebug`
  - `freeRelease`
  - `paidDebug`
  - `paidRelease`

#### 4. Manifest Entries

**Definition**: Certain manifest properties (for example, `applicationId`, `versionName`, placeholders) can be configured per build type/flavor so that the merged manifest for each variant gets specific values.

**Characteristics:**
- Build configuration values (e.g., from `defaultConfig`, `buildTypes`, `productFlavors`, `manifestPlaceholders`) can override or parameterize values in `AndroidManifest.xml`.
- Useful for generating multiple variants with different properties (e.g., different authorities, schemes).
- The manifest merger tool combines settings from all manifest sources.

**Code example:**
```kotlin
android {
    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
}
```

#### 5. Dependencies

**Definition**: The build system manages project dependencies from your local file system and remote repositories.

**Benefits:**
- No need to manually search, download, and copy binary packages.
- Automatic dependency resolution.
- Transitive dependency support.

**Code example:**
```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
}
```

#### 6. Signing

**Definition**: The build system lets you specify signing settings in the build configuration.

**Characteristics:**
- Can automatically sign your app during the build process when a signing configuration is associated with a build type.
- Debug builds: Signed with the default debug key and certificate.
- Release builds: Not signed by default; typically configured with a custom signing config for distribution.

**Code example (DO NOT hardcode secrets in real projects):**
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("keystore.jks")
            storePassword = "password"
            keyAlias = "key"
            keyPassword = "password"
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

#### 7. Code and Resource Shrinking

**Definition**: The build system lets you enable code and resource shrinking per build type/variant and associate specific rules files.

**Features:**
- Uses R8 as the default code shrinker.
- Shrinks code and resources.
- Helps reduce APK or AAB size.
- Different rules can be applied for different build variants.

**Code example:**
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

#### 8. Multiple APK Support

**Definition**: The build system can automatically build different APKs from the same module for different device configurations.

**Capabilities:**
- Each APK contains only the code and resources needed for specific configurations.
- Can split by screen density.
- Can split by `Application` Binary Interface (ABI).

**Code example (ABI splits):**
```kotlin
android {
    splits {
        abi {
            isEnable = true // AGP Kotlin DSL uses isEnable for the abi splits block
            reset()
            include("x86", "x86_64", "armeabi-v7a", "arm64-v8a")
            isUniversalApk = true
        }
    }
}
```

### Build Configuration Files

When starting a new project, Android Studio automatically creates Gradle files based on sensible defaults.

#### Project File Structure

```
 MyApp/                    # Project
     build.gradle.kts      # Top-level build file
     settings.gradle.kts   # Settings file
     app/                  # Module
         build.gradle.kts  # Module-level build file
         libs/
         src/
             main/         # Source set
                 java/
                    com.example.myapp
                 res/
                    drawable/
                    values/
                    ...
                 AndroidManifest.xml
```

#### 1. The Gradle Settings File

**File**: `settings.gradle.kts` (Kotlin DSL) or `settings.gradle` (Groovy DSL)

**Location**: Root project directory.

**Purpose**:
- Defines project-level repository and plugin-management settings.
- Specifies which modules to include when building your app.
- In multi-module projects, each module must be included to participate in the build.

**Example:**
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
```

#### 2. The Top-Level Build File

**File**: `build.gradle.kts` (Kotlin DSL) or `build.gradle` (Groovy DSL)

**Location**: Root project directory.

**Purpose**:
- Applies and versions plugins that can be used by modules (with `apply false`).
- Optionally defines common configuration or dependencies shared across modules.
- Often defines convenience tasks (e.g., a `clean` task) for the whole project.

**Example:**
```kotlin
plugins {
    id("com.android.application") version "8.1.0" apply false
    id("com.android.library") version "8.1.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
```

#### 3. The Module-Level Build File

**File**: `build.gradle.kts` (Kotlin DSL) or `build.gradle` (Groovy DSL)

**Location**: Each `project/module/` directory.

**Purpose**:
- Configure build settings for the specific module.
- Provide custom packaging options.
- Define additional build types and product flavors.
- Override or refine settings relative to the top-level build script.

**Example:**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
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
    implementation("androidx.appcompat:appcompat:1.6.1")
}
```

#### 4. Gradle Properties Files

Two properties files in the root project directory specify settings for the Gradle build toolkit:

**`gradle.properties`**:
- Configure project-wide Gradle settings.
- Example: Gradle daemon's maximum heap size.

```properties
org.gradle.jvmargs=-Xmx2048m
android.useAndroidX=true
kotlin.code.style=official
```

**`local.properties`**:
- Configure local environment properties.
- Not checked into version control.
- Common properties:
  - `sdk.dir` - Path to the Android SDK.
  - `ndk.dir` - Path to the NDK (deprecated in favor of using SDK-managed NDK).
  - `cmake.dir` - Path to CMake.
  - `ndk.symlinkdir` - Symlink to NDK (Android Studio 3.5+).

```properties
sdk.dir=/Users/username/Library/Android/sdk
```

---

## Ссылки (RU)

- [Android Developer Docs: Configure your build](https://developer.android.com/build)
- [Gradle Docs: What is Gradle?](https://docs.gradle.org/current/userguide/what_is_gradle.html)
- [Medium: Gradle Basics for Android Developers](https://medium.com/android-dev-corner/gradle-basics-for-android-developers-9d7a3bf062bb)
- [Kodeco: Gradle Tutorial for Android: Getting Started](https://www.kodeco.com/249-gradle-tutorial-for-android-getting-started)
- [Build Type, Product Flavor, Build Variant](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/Build%20Type%2C%20Product%20Flavor%2C%20Build%20Variant.md)
- [ProGuard](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What's%20Proguard.md)
- [App Bundles](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20App%20Bundles.md)

## References

- [Android Developer Docs: Configure your build](https://developer.android.com/build)
- [Gradle Docs: What is Gradle?](https://docs.gradle.org/current/userguide/what_is_gradle.html)
- [Medium: Gradle Basics for Android Developers](https://medium.com/android-dev-corner/gradle-basics-for-android-developers-9d7a3bf062bb)
- [Kodeco: Gradle Tutorial for Android: Getting Started](https://www.kodeco.com/249-gradle-tutorial-for-android-getting-started)
- [Build Type, Product Flavor, Build Variant](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/Build%20Type%2C%20Product%20Flavor%2C%20Build%20Variant.md)
- [ProGuard](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What's%20Proguard.md)
- [App Bundles](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20App%20Bundles.md)

---

## Дополнительные вопросы (RU)

- [[q-cache-implementation-strategies--android--medium]]
- [[q-kapt-vs-ksp--android--medium]]
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]]

## Follow-ups

- [[q-cache-implementation-strategies--android--medium]]
- [[q-kapt-vs-ksp--android--medium]]
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]]

---

## Связанные вопросы (RU)

### Предпосылки / Концепты

- [[c-gradle]]

### Предпосылки (проще)
- [[q-why-separate-ui-and-business-logic--android--easy]] - UI
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - UI

### Связанные (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Build, UI
- [[q-build-optimization-gradle--android--medium]] - Build, UI
- [[q-android-build-optimization--android--medium]] - Build, UI
- [[q-kapt-ksp-migration--android--medium]] - Build
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Build

### Продвинутые (Hard)
- [[q-kotlin-dsl-builders--android--hard]] - Build, UI

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]] - UI
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - UI

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Build, UI
- [[q-build-optimization-gradle--android--medium]] - Build, UI
- [[q-android-build-optimization--android--medium]] - Build, UI
- [[q-kapt-ksp-migration--android--medium]] - Build
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Build

### Advanced (Harder)
- [[q-kotlin-dsl-builders--android--hard]] - Build, UI
