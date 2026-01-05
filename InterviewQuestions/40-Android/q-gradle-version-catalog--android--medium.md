---
id: android-179
title: "Gradle Version Catalog / Каталог версий Gradle"
aliases: [Gradle Version Catalog, libs.versions.toml, Version Catalog, Каталог версий Gradle]
topic: android
subtopics: [gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-gradle, q-gradle-build-system--android--medium, q-gradle-kotlin-dsl-vs-groovy--android--medium, q-kapt-ksp-migration--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/gradle, difficulty/medium, gradle, toml]
sources: ["https://developer.android.com/build/migrate-to-catalogs", "https://docs.gradle.org/current/userguide/platforms.html"]
---
# Вопрос (RU)

> Что вы знаете о Gradle Version Catalog?

# Question (EN)

> What do you know about Gradle Version Catalog?

---

## Ответ (RU)

**Gradle Version Catalog** — это механизм для централизованного управления зависимостями и плагинами в Gradle-проектах через файл `libs.versions.toml` (или несколько каталогов). Вместо дублирования версий в каждом модуле создается единый каталог, на основе которого Gradle генерирует удобные, структурированные аксессоры ("типизированные"/type-safe-style) для Kotlin DSL и Groovy DSL с поддержкой автодополнения в IDE.

См. также: [[c-gradle]]

### Ключевые Преимущества

1. **Структурированные аксессоры**: Gradle генерирует аксессоры для автодополнения (`libs.retrofit.core`).
2. **Централизация**: Единый источник истины для версий и координат зависимостей.
3. **Бандлы**: Группировка часто используемых вместе зависимостей.
4. **Консистентность**: Одна версия применяется во всех модулях.

### Структура libs.versions.toml

```toml
[versions]              # ✅ Объявление версий
kotlin = "1.9.20"
compose = "1.5.4"
retrofit = "2.9.0"

[libraries]             # ✅ Координаты библиотек
retrofit-core = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
retrofit-gson = { module = "com.squareup.retrofit2:converter-gson", version.ref = "retrofit" }

[bundles]               # ✅ Группы зависимостей
retrofit = ["retrofit-core", "retrofit-gson"]

[plugins]               # ✅ Плагины
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
```

### Использование В build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.kotlin.android)  // ✅ Плагин из каталога
}

dependencies {
    // ✅ Отдельные зависимости через сгенерированные аксессоры
    implementation(libs.retrofit.core)

    // ✅ Бандл — все зависимости группы сразу
    implementation(libs.bundles.retrofit)
}
```

### Правила Именования Алиасов

Gradle на основе ключей в TOML генерирует Kotlin/Groovy аксессоры. Важно понимать, как символы преобразуются:

- Дефис `-` в алиасе библиотеки (`retrofit-core`) приводит к вложенному аксессору: `libs.retrofit.core`.
- Точка `.` используется как уже вложенная структура: `androidx.core.ktx` → `libs.androidx.core.ktx`.
- Подчёркивание `_` в ключах (`room_runtime`) допускается и транслируется в валидные имена аксессоров (например, `libs.room_runtime` или эквивалентный camelCase в Groovy); его не следует воспринимать как гарантированное преобразование в точку.

**Валидные алиасы**: `guava`, `compose-ui`, `androidx.lifecycle.runtime`, `room_runtime`.

**Невалидные**: `this.#invalid` (спецсимволы запрещены).

### Пример Для Android-проекта

```toml
[versions]
compose = "1.5.4"
room = "2.6.0"

[libraries]
# Compose UI
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
compose-material3 = { module = "androidx.compose.material3:material3", version.ref = "compose" }

# Room Database
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
room-ktx = { module = "androidx.room:room-ktx", version.ref = "room" }
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }  # ✅ Для kapt/ksp в зависимости от используемого варианта

[bundles]
compose = ["compose-ui", "compose-material3"]
room = ["room-runtime", "room-ktx"]

[plugins]
ksp = { id = "com.google.devtools.ksp", version = "1.9.20-1.0.14" }
```

**Использование**:

```kotlin
dependencies {
    implementation(libs.bundles.compose)     // ✅ Весь Compose UI сразу
    implementation(libs.bundles.room)        // ✅ Room runtime и KTX-расширения
    ksp(libs.room.compiler)                  // ✅ Используем room-compiler с KSP-плагином (при конфигурации KSP)
}
```

### Стратегия Миграции

1. Создайте `gradle/libs.versions.toml` (при этом стандартный каталог `libs` поддерживается Gradle без дополнительной конфигурации).
2. Вынесите версии из `build.gradle` файлов в секцию `[versions]`.
3. Объявите библиотеки в `[libraries]` с `version.ref`.
4. Сгруппируйте связанные зависимости в `[bundles]`.
5. Замените `implementation("group:artifact:version")` на `implementation(libs.<alias>)`.
6. Убедитесь, что проект собирается. При использовании дополнительных каталогов (помимо стандартного `libs`) объявите их в `settings.gradle` через `dependencyResolutionManagement.versionCatalogs`.

## Answer (EN)

**Gradle Version Catalog** is a mechanism for centralized dependency and plugin management via the `libs.versions.toml` file (or multiple catalogs). Instead of hardcoding versions in each module, you define a shared catalog from which Gradle generates convenient, structured type-safe-style accessors for both Kotlin DSL and Groovy DSL with IDE autocompletion support.

See also: [[c-gradle]]

### Key Benefits

1. **Structured accessors**: Gradle generates accessors for autocompletion (`libs.retrofit.core`).
2. **Centralization**: Single source of truth for versions and dependency coordinates.
3. **Bundles**: Group commonly used dependencies together.
4. **Consistency**: One version applied across all modules.

### Structure of libs.versions.toml

```toml
[versions]              # ✅ Version declarations
kotlin = "1.9.20"
compose = "1.5.4"
retrofit = "2.9.0"

[libraries]             # ✅ Library coordinates
retrofit-core = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
retrofit-gson = { module = "com.squareup.retrofit2:converter-gson", version.ref = "retrofit" }

[bundles]               # ✅ Dependency groups
retrofit = ["retrofit-core", "retrofit-gson"]

[plugins]               # ✅ Plugin declarations
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
```

### Usage in build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.kotlin.android)  // ✅ Plugin from catalog
}

dependencies {
    // ✅ Individual dependencies via generated accessors
    implementation(libs.retrofit.core)

    // ✅ Bundle - all group dependencies at once
    implementation(libs.bundles.retrofit)
}
```

### Alias Naming Rules

Gradle generates Kotlin/Groovy accessors based on TOML keys. Key transformation rules:

- Dash `-` in library aliases (`retrofit-core`) becomes a nested accessor: `libs.retrofit.core`.
- Dot `.` represents nested structure directly: `androidx.core.ktx` → `libs.androidx.core.ktx`.
- Underscore `_` in keys (`room_runtime`) is allowed and mapped to a valid accessor name (for example, `libs.room_runtime` or an equivalent camelCase accessor in Groovy); it should not be assumed to always turn into a dot.

**Valid aliases**: `guava`, `compose-ui`, `androidx.lifecycle.runtime`, `room_runtime`.

**Invalid**: `this.#invalid` (special characters are forbidden).

### Android Project Example

```toml
[versions]
compose = "1.5.4"
room = "2.6.0"

[libraries]
# Compose UI
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
compose-material3 = { module = "androidx.compose.material3:material3", version.ref = "compose" }

# Room Database
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
room-ktx = { module = "androidx.room:room-ktx", version.ref = "room" }
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }  # ✅ Used with kapt or KSP depending on your setup

[bundles]
compose = ["compose-ui", "compose-material3"]
room = ["room-runtime", "room-ktx"]

[plugins]
ksp = { id = "com.google.devtools.ksp", version = "1.9.20-1.0.14" }
```

**Usage**:

```kotlin
dependencies {
    implementation(libs.bundles.compose)     // ✅ All Compose UI at once
    implementation(libs.bundles.room)        // ✅ Room runtime and KTX extensions
    ksp(libs.room.compiler)                  // ✅ Use room-compiler with the KSP plugin (when configured for KSP)
}
```

### Migration Strategy

1. Create `gradle/libs.versions.toml` (the default `libs` catalog is recognized by Gradle without additional configuration).
2. Extract versions from existing `build.gradle` files into the `[versions]` section.
3. Declare libraries in `[libraries]` using `version.ref` where appropriate.
4. Group related dependencies in `[bundles]`.
5. Replace `implementation("group:artifact:version")` with `implementation(libs.<alias>)`.
6. Verify the build. When using additional catalogs (beyond the default `libs`), declare them in `settings.gradle` via `dependencyResolutionManagement.versionCatalogs`.

---

## Follow-ups

- How to handle version conflicts in multi-module projects?
- Can you use multiple version catalogs in one project?
- How to migrate from buildSrc to version catalog?
- What happens when an alias name conflicts with existing code?

## References

- [Android Developer Docs: Migrate to version catalogs](https://developer.android.com/build/migrate-to-catalogs)
- [Gradle User Guide: Sharing dependency versions](https://docs.gradle.org/current/userguide/platforms.html)
- [ProAndroidDev: Version Catalog on Android](https://proandroiddev.com/using-version-catalog-on-android-projects-82d88d2f79e5)

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] - Gradle fundamentals

### Related (Same Level)
- [[q-gradle-build-system--android--medium]] - Build system overview
- [[q-kapt-ksp-migration--android--medium]] - Annotation processing
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Build script languages
