---
id: android-179
title: "Gradle Version Catalog / Каталог версий Gradle"
aliases: [Gradle Version Catalog, libs.versions.toml, Version Catalog, Каталог версий Gradle]
topic: android
subtopics: [build-variants, dependency-management, gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-gradle-build-system--android--medium, q-gradle-kotlin-dsl-vs-groovy--android--medium, q-kapt-ksp-migration--android--medium]
created: 2025-10-15
updated: 2025-10-27
tags: [android/build-variants, android/dependency-management, android/gradle, dependency-management, difficulty/medium, gradle, toml]
sources: [Android Developer Docs, Kirchhoff repo]
date created: Monday, October 27th 2025, 6:55:47 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

Что вы знаете о Gradle Version Catalog?

# Question (EN)

What do you know about Gradle Version Catalog?

---

## Ответ (RU)

**Gradle Version Catalog** - это механизм для централизованного управления зависимостями и плагинами в Gradle-проектах через файл `libs.versions.toml`. Вместо дублирования версий в каждом модуле, создается единый каталог с типобезопасными аксессорами и поддержкой автодополнения в IDE. См. также [[c-dependency-injection]] для паттернов управления зависимостями.

### Ключевые Преимущества

1. **Типобезопасность**: Gradle генерирует аксессоры для автодополнения (`libs.retrofit.core`)
2. **Централизация**: Единый источник истины для всех версий
3. **Бандлы**: Группировка часто используемых вместе зависимостей
4. **Консистентность**: Одна версия применяется во всех модулях

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
    // ✅ Отдельные зависимости с типобезопасностью
    implementation(libs.retrofit.core)

    // ✅ Бандл - все зависимости группы сразу
    implementation(libs.bundles.retrofit)
}
```

### Правила Именования Алиасов

**Разделители** (dash рекомендуется):
- Дефис `-`: `retrofit-core` → `libs.retrofit.core`
- Точка `.`: `androidx.core.ktx` → `libs.androidx.core.ktx`
- Подчеркивание `_`: `room_runtime` → `libs.room.runtime`

**Валидные алиасы**: `guava`, `compose-ui`, `androidx.lifecycle.runtime`

**Невалидные**: `this.#invalid` (спецсимволы запрещены)

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
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }  # ✅ KSP dependency

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
    implementation(libs.bundles.room)        // ✅ Room runtime и extensions
    ksp(libs.room.compiler)                  // ✅ Аннотация-процессор через KSP
}
```

### Стратегия Миграции

1. Создайте `gradle/libs.versions.toml`
2. Извлеките версии из build-файлов в `[versions]`
3. Объявите библиотеки в `[libraries]` с `version.ref`
4. Группируйте связанные зависимости в `[bundles]`
5. Замените `implementation("group:artifact:version")` на `implementation(libs.artifact)`
6. Протестируйте сборку

## Answer (EN)

**Gradle Version Catalog** is a centralized dependency and plugin management mechanism through `libs.versions.toml` file. Instead of hardcoding versions in each module, you create a single catalog with type-safe accessors and IDE autocompletion support.

### Key Benefits

1. **Type Safety**: Gradle generates accessors for autocompletion (`libs.retrofit.core`)
2. **Centralization**: Single source of truth for all versions
3. **Bundles**: Group commonly used dependencies together
4. **Consistency**: One version applied across all modules

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
    // ✅ Individual dependencies with type safety
    implementation(libs.retrofit.core)

    // ✅ Bundle - all group dependencies at once
    implementation(libs.bundles.retrofit)
}
```

### Alias Naming Rules

**Separators** (dash recommended):
- Dash `-`: `retrofit-core` → `libs.retrofit.core`
- Dot `.`: `androidx.core.ktx` → `libs.androidx.core.ktx`
- Underscore `_`: `room_runtime` → `libs.room.runtime`

**Valid aliases**: `guava`, `compose-ui`, `androidx.lifecycle.runtime`

**Invalid**: `this.#invalid` (special characters forbidden)

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
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }  # ✅ KSP dependency

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
    implementation(libs.bundles.room)        // ✅ Room runtime and extensions
    ksp(libs.room.compiler)                  // ✅ Annotation processor via KSP
}
```

### Migration Strategy

1. Create `gradle/libs.versions.toml` file
2. Extract versions from build files to `[versions]` section
3. Declare libraries in `[libraries]` with `version.ref`
4. Group related dependencies in `[bundles]`
5. Replace `implementation("group:artifact:version")` with `implementation(libs.artifact)`
6. Test the build

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
