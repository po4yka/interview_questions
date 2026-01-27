---
id: android-cicd-003
title: Build Variants, Product Flavors, Build Types / Варианты сборки, Product Flavors,
  Build Types
aliases:
- Build Variants and Product Flavors
- Варианты сборки и Product Flavors
topic: android
subtopics:
- cicd
- build-configuration
- gradle
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-github-actions-android--cicd--medium
- q-gradle-build-cache--cicd--medium
- q-signing-in-ci--cicd--hard
created: 2026-01-23
updated: 2026-01-23
sources:
- https://developer.android.com/build/build-variants
- https://developer.android.com/build/configure-apk-splits
tags:
- android/cicd
- android/build-configuration
- difficulty/medium
- gradle
- build-variants
anki_cards:
- slug: android-cicd-003-0-en
  language: en
- slug: android-cicd-003-0-ru
  language: ru
---
# Вопрос (RU)

> Что такое Build Variants, Product Flavors и Build Types в Android? Как их настроить?

# Question (EN)

> What are Build Variants, Product Flavors, and Build Types in Android? How do you configure them?

## Ответ (RU)

Build Variants в Android — это комбинации **Build Types** и **Product Flavors**, которые позволяют создавать разные версии приложения из одного исходного кода. Например, `freeDebug`, `paidRelease`.

### Основные Понятия

```
Build Variant = Build Type + Product Flavor(s)

Пример:
  Build Types: debug, release
  Product Flavors: free, paid

  Варианты:
    - freeDebug
    - freeRelease
    - paidDebug
    - paidRelease
```

### Build Types

Build Types определяют **как** собирать приложение (отладка, оптимизация, подписание).

```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        debug {
            isDebuggable = true
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-DEBUG"
        }

        release {
            isDebuggable = false
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }

        // Custom build type
        create("staging") {
            initWith(getByName("release"))
            applicationIdSuffix = ".staging"
            isDebuggable = true
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}
```

### Product Flavors

Product Flavors определяют **что** собирать (разные версии приложения).

```kotlin
// app/build.gradle.kts
android {
    // Обязательно указать flavorDimensions
    flavorDimensions += listOf("version", "environment")

    productFlavors {
        // Dimension "version"
        create("free") {
            dimension = "version"
            applicationIdSuffix = ".free"
            versionNameSuffix = "-free"
            buildConfigField("boolean", "IS_PREMIUM", "false")
            resValue("string", "app_name", "MyApp Free")
        }

        create("paid") {
            dimension = "version"
            applicationIdSuffix = ".paid"
            versionNameSuffix = "-paid"
            buildConfigField("boolean", "IS_PREMIUM", "true")
            resValue("string", "app_name", "MyApp Premium")
        }

        // Dimension "environment"
        create("dev") {
            dimension = "environment"
            buildConfigField("String", "API_URL", "\"https://dev-api.example.com\"")
        }

        create("prod") {
            dimension = "environment"
            buildConfigField("String", "API_URL", "\"https://api.example.com\"")
        }
    }
}
```

### Результирующие Варианты

С двумя измерениями (version: free/paid, environment: dev/prod) и двумя build types (debug/release) получим 8 вариантов:

| Вариант | Dimension 1 | Dimension 2 | Build Type |
|---------|-------------|-------------|------------|
| freeDevDebug | free | dev | debug |
| freeDevRelease | free | dev | release |
| freeProdDebug | free | prod | debug |
| freeProdRelease | free | prod | release |
| paidDevDebug | paid | dev | debug |
| paidDevRelease | paid | dev | release |
| paidProdDebug | paid | prod | debug |
| paidProdRelease | paid | prod | release |

### Source Sets

Каждый вариант может иметь свои исходники:

```
app/src/
├── main/           # Общий код
├── debug/          # Код для debug build type
├── release/        # Код для release build type
├── free/           # Код для free flavor
├── paid/           # Код для paid flavor
├── freeDebug/      # Код для комбинации free + debug
└── paidRelease/    # Код для комбинации paid + release
```

#### Пример: Разные Реализации

```kotlin
// src/free/kotlin/com/example/FeatureManager.kt
class FeatureManager {
    fun isPremiumFeatureEnabled(): Boolean = false
}

// src/paid/kotlin/com/example/FeatureManager.kt
class FeatureManager {
    fun isPremiumFeatureEnabled(): Boolean = true
}
```

### Variant Filters

Можно исключить ненужные варианты:

```kotlin
// app/build.gradle.kts
android {
    androidComponents {
        beforeVariants { variantBuilder ->
            // Исключить staging для free версии
            if (variantBuilder.buildType == "staging" &&
                variantBuilder.productFlavors.any { it.second == "free" }) {
                variantBuilder.enable = false
            }
        }
    }
}
```

### Зависимости по Вариантам

```kotlin
// app/build.gradle.kts
dependencies {
    // Общие зависимости
    implementation("androidx.core:core-ktx:1.12.0")

    // Только для debug
    debugImplementation("com.facebook.flipper:flipper:0.250.0")

    // Только для paid flavor
    "paidImplementation"("com.example:premium-sdk:1.0.0")

    // Для конкретного варианта
    "paidReleaseImplementation"("com.example:analytics-pro:2.0.0")
}
```

### BuildConfig и ResValues

```kotlin
android {
    defaultConfig {
        buildConfigField("String", "API_KEY", "\"default-key\"")
        resValue("string", "app_name", "MyApp")
    }

    buildTypes {
        debug {
            buildConfigField("String", "API_KEY", "\"debug-key\"")
        }
    }

    productFlavors {
        create("paid") {
            dimension = "version"
            buildConfigField("String", "API_KEY", "\"premium-key\"")
            resValue("string", "app_name", "MyApp Premium")
        }
    }
}
```

Доступ в коде:

```kotlin
val apiKey = BuildConfig.API_KEY
val isPremium = BuildConfig.IS_PREMIUM
```

### Signing Configurations

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### Manifest Placeholders

```kotlin
android {
    defaultConfig {
        manifestPlaceholders["appLabel"] = "MyApp"
    }

    productFlavors {
        create("free") {
            dimension = "version"
            manifestPlaceholders["appLabel"] = "MyApp Free"
        }
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<application android:label="${appLabel}">
```

### APK Splits (ABI, Density)

```kotlin
android {
    splits {
        abi {
            isEnable = true
            reset()
            include("arm64-v8a", "armeabi-v7a", "x86_64")
            isUniversalApk = true
        }

        density {
            isEnable = true
            reset()
            include("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi")
        }
    }
}
```

### Резюме

| Концепт | Назначение | Пример |
|---------|------------|--------|
| Build Type | Как собирать | debug, release, staging |
| Product Flavor | Что собирать | free, paid, demo |
| Flavor Dimension | Группировка flavors | version, environment |
| Build Variant | Комбинация всего | freeProdRelease |
| Source Set | Код для варианта | src/free/, src/debug/ |

## Answer (EN)

Build Variants in Android are combinations of **Build Types** and **Product Flavors** that allow creating different versions of an application from a single codebase. For example, `freeDebug`, `paidRelease`.

### Core Concepts

```
Build Variant = Build Type + Product Flavor(s)

Example:
  Build Types: debug, release
  Product Flavors: free, paid

  Variants:
    - freeDebug
    - freeRelease
    - paidDebug
    - paidRelease
```

### Build Types

Build Types define **how** to build the app (debugging, optimization, signing).

```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        debug {
            isDebuggable = true
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-DEBUG"
        }

        release {
            isDebuggable = false
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }

        // Custom build type
        create("staging") {
            initWith(getByName("release"))
            applicationIdSuffix = ".staging"
            isDebuggable = true
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}
```

### Product Flavors

Product Flavors define **what** to build (different app versions).

```kotlin
// app/build.gradle.kts
android {
    // flavorDimensions is required
    flavorDimensions += listOf("version", "environment")

    productFlavors {
        // Dimension "version"
        create("free") {
            dimension = "version"
            applicationIdSuffix = ".free"
            versionNameSuffix = "-free"
            buildConfigField("boolean", "IS_PREMIUM", "false")
            resValue("string", "app_name", "MyApp Free")
        }

        create("paid") {
            dimension = "version"
            applicationIdSuffix = ".paid"
            versionNameSuffix = "-paid"
            buildConfigField("boolean", "IS_PREMIUM", "true")
            resValue("string", "app_name", "MyApp Premium")
        }

        // Dimension "environment"
        create("dev") {
            dimension = "environment"
            buildConfigField("String", "API_URL", "\"https://dev-api.example.com\"")
        }

        create("prod") {
            dimension = "environment"
            buildConfigField("String", "API_URL", "\"https://api.example.com\"")
        }
    }
}
```

### Resulting Variants

With two dimensions (version: free/paid, environment: dev/prod) and two build types (debug/release), you get 8 variants:

| Variant | Dimension 1 | Dimension 2 | Build Type |
|---------|-------------|-------------|------------|
| freeDevDebug | free | dev | debug |
| freeDevRelease | free | dev | release |
| freeProdDebug | free | prod | debug |
| freeProdRelease | free | prod | release |
| paidDevDebug | paid | dev | debug |
| paidDevRelease | paid | dev | release |
| paidProdDebug | paid | prod | debug |
| paidProdRelease | paid | prod | release |

### Source Sets

Each variant can have its own source files:

```
app/src/
├── main/           # Common code
├── debug/          # Code for debug build type
├── release/        # Code for release build type
├── free/           # Code for free flavor
├── paid/           # Code for paid flavor
├── freeDebug/      # Code for free + debug combination
└── paidRelease/    # Code for paid + release combination
```

#### Example: Different Implementations

```kotlin
// src/free/kotlin/com/example/FeatureManager.kt
class FeatureManager {
    fun isPremiumFeatureEnabled(): Boolean = false
}

// src/paid/kotlin/com/example/FeatureManager.kt
class FeatureManager {
    fun isPremiumFeatureEnabled(): Boolean = true
}
```

### Variant Filters

Exclude unnecessary variants:

```kotlin
// app/build.gradle.kts
android {
    androidComponents {
        beforeVariants { variantBuilder ->
            // Exclude staging for free version
            if (variantBuilder.buildType == "staging" &&
                variantBuilder.productFlavors.any { it.second == "free" }) {
                variantBuilder.enable = false
            }
        }
    }
}
```

### Variant-Specific Dependencies

```kotlin
// app/build.gradle.kts
dependencies {
    // Common dependencies
    implementation("androidx.core:core-ktx:1.12.0")

    // Debug only
    debugImplementation("com.facebook.flipper:flipper:0.250.0")

    // Paid flavor only
    "paidImplementation"("com.example:premium-sdk:1.0.0")

    // Specific variant
    "paidReleaseImplementation"("com.example:analytics-pro:2.0.0")
}
```

### BuildConfig and ResValues

```kotlin
android {
    defaultConfig {
        buildConfigField("String", "API_KEY", "\"default-key\"")
        resValue("string", "app_name", "MyApp")
    }

    buildTypes {
        debug {
            buildConfigField("String", "API_KEY", "\"debug-key\"")
        }
    }

    productFlavors {
        create("paid") {
            dimension = "version"
            buildConfigField("String", "API_KEY", "\"premium-key\"")
            resValue("string", "app_name", "MyApp Premium")
        }
    }
}
```

Access in code:

```kotlin
val apiKey = BuildConfig.API_KEY
val isPremium = BuildConfig.IS_PREMIUM
```

### Signing Configurations

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### Manifest Placeholders

```kotlin
android {
    defaultConfig {
        manifestPlaceholders["appLabel"] = "MyApp"
    }

    productFlavors {
        create("free") {
            dimension = "version"
            manifestPlaceholders["appLabel"] = "MyApp Free"
        }
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<application android:label="${appLabel}">
```

### APK Splits (ABI, Density)

```kotlin
android {
    splits {
        abi {
            isEnable = true
            reset()
            include("arm64-v8a", "armeabi-v7a", "x86_64")
            isUniversalApk = true
        }

        density {
            isEnable = true
            reset()
            include("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi")
        }
    }
}
```

### Summary

| Concept | Purpose | Example |
|---------|---------|---------|
| Build Type | How to build | debug, release, staging |
| Product Flavor | What to build | free, paid, demo |
| Flavor Dimension | Flavor grouping | version, environment |
| Build Variant | Combination of all | freeProdRelease |
| Source Set | Code for variant | src/free/, src/debug/ |

## Дополнительные Вопросы (RU)

1. Как управлять version codes между несколькими flavors?
2. Каковы лучшие практики организации source sets в больших проектах?
3. Как эффективно обрабатывать flavor-специфичные ресурсы?
4. Когда использовать flavor dimensions вместо отдельных модулей?

## Follow-ups

1. How do you manage version codes across multiple flavors?
2. What are the best practices for organizing source sets in large projects?
3. How do you handle flavor-specific resources efficiently?
4. When should you use flavor dimensions vs. separate modules?

## Ссылки (RU)

- [Настройка вариантов сборки](https://developer.android.com/build/build-variants)
- [Настройка APK Splits](https://developer.android.com/build/configure-apk-splits)

## References

- [Configure Build Variants](https://developer.android.com/build/build-variants)
- [Configure APK Splits](https://developer.android.com/build/configure-apk-splits)
- [Android Gradle Plugin DSL Reference](https://developer.android.com/reference/tools/gradle-api)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-gradle-build-cache--cicd--medium]] — Кеширование Gradle

### Похожие
- [[q-github-actions-android--cicd--medium]] — GitHub Actions
- [[q-signing-in-ci--cicd--hard]] — Безопасное подписание

### Продвинутое
- [[q-play-store-deployment--cicd--medium]] — Публикация в Play Store

## Related Questions

### Prerequisites
- [[q-gradle-build-cache--cicd--medium]] - Gradle caching

### Related
- [[q-github-actions-android--cicd--medium]] - GitHub Actions
- [[q-signing-in-ci--cicd--hard]] - Secure signing

### Advanced
- [[q-play-store-deployment--cicd--medium]] - Play Store deployment
