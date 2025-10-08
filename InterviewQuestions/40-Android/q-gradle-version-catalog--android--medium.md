---
topic: android
tags:
  - android
  - gradle
  - version-catalog
  - dependency-management
  - toml
subtopics:
  - gradle
  - dependency-management
  - build-variants
difficulty: medium
status: reviewed
source: Kirchhoff repo
---

# Gradle Version Catalog / Gradle Version Catalog

**English**: What do you know about Gradle Version Catalog?

**Russian**: Что вы знаете о Gradle Version Catalog?

## Answer

**Gradle version catalogs** enable you to add and maintain dependencies and plugins in a scalable way. Using Gradle version catalogs makes managing dependencies and plugins easier when you have multiple modules. Instead of hardcoding dependency names and versions in individual build files and updating each entry whenever you need to upgrade a dependency, you can create a central **version catalog** of dependencies that various modules can reference in a type-safe way with Android Studio assistance.

## Advantages of Version Catalogs

A version catalog provides several advantages over declaring dependencies directly in build scripts:

1. **Type-safe accessors**: For each catalog, Gradle generates type-safe accessors so that you can easily add dependencies with autocompletion in the IDE

2. **Centralized version management**: Each catalog is visible to all projects of a build. It is a central place to declare a version of a dependency and to make sure that a change to that version applies to every subproject

3. **Dependency bundles**: Catalogs can declare dependency bundles, which are "groups of dependencies" that are commonly used together

4. **Version references**: Catalogs can separate the group and name of a dependency from its actual version and use version references instead, making it possible to share a version declaration between multiple dependencies

## Creating a Version Catalog File

### Basic Setup

Start by creating a version catalog file. In your root project's `gradle` folder, create a file called `libs.versions.toml`. Gradle looks for the catalog in the `libs.versions.toml` file by default, so we recommend using this default name.

In your `libs.versions.toml` file, add these sections:

```toml
[versions]

[libraries]

[plugins]

[bundles]
```

### TOML File Format

The TOML file consists of 4 major sections:

- **`[versions]`** - Used to declare versions which can be referenced by dependencies
- **`[libraries]`** - Used to declare the aliases to coordinates
- **`[bundles]`** - Used to declare dependency bundles
- **`[plugins]`** - Used to declare plugins

### Example Version Catalog

```toml
[versions]
groovy = "3.0.5"
checkstyle = "8.37"

[libraries]
groovy-core = { module = "org.codehaus.groovy:groovy", version.ref = "groovy" }
groovy-json = { module = "org.codehaus.groovy:groovy-json", version.ref = "groovy" }
groovy-nio = { module = "org.codehaus.groovy:groovy-nio", version.ref = "groovy" }

[bundles]
groovy = ["groovy-core", "groovy-json", "groovy-nio"]

[plugins]
versions = { id = "com.github.ben-manes.versions", version = "0.45.0" }
```

## Aliases and Type-Safe Accessors

### Alias Naming Rules

Aliases must consist of a series of identifiers separated by:
- Dash (`-`) - **recommended**
- Underscore (`_`)
- Dot (`.`)

Identifiers themselves must consist of ASCII characters, preferably lowercase, eventually followed by numbers.

**Valid aliases:**
- `guava`
- `groovy-core`
- `commons-lang3`
- `androidx.awesome.lib`

**Invalid aliases:**
- `this.#is.not` (contains special characters)

### Type-Safe Accessor Generation

For the following aliases in a version catalog named `libs`:

```toml
guava, groovy-core, groovy-xml, groovy-json, androidx.awesome.lib
```

Gradle generates the following type-safe accessors:

```kotlin
libs.guava
libs.groovy.core
libs.groovy.xml
libs.groovy.json
libs.androidx.awesome.lib
```

Where the `libs` prefix comes from the version catalog name.

### Using Dependencies in Build Files

```kotlin
dependencies {
    implementation(libs.guava)
    implementation(libs.groovy.core)
    implementation(libs.androidx.awesome.lib)
}
```

## Dependency Bundles

Because some dependencies are systematically used together in different projects, a version catalog offers the concept of **dependency bundles**. A bundle is an alias for several dependencies.

### Without Bundle

```kotlin
dependencies {
    implementation(libs.groovy.core)
    implementation(libs.groovy.json)
    implementation(libs.groovy.nio)
}
```

### With Bundle

```kotlin
dependencies {
    implementation(libs.bundles.groovy)
}
```

### Bundle Declaration

The bundle needs to be declared in the catalog:

```groovy
dependencyResolutionManagement {
    versionCatalogs {
        libs {
            version('groovy', '3.0.5')
            version('checkstyle', '8.37')
            library('groovy-core', 'org.codehaus.groovy', 'groovy').versionRef('groovy')
            library('groovy-json', 'org.codehaus.groovy', 'groovy-json').versionRef('groovy')
            library('groovy-nio', 'org.codehaus.groovy', 'groovy-nio').versionRef('groovy')
            bundle('groovy', ['groovy-core', 'groovy-json', 'groovy-nio'])
        }
    }
}
```

The semantics are equivalent: adding a single bundle is equivalent to adding all dependencies which are part of the bundle individually.

## Plugins

In addition to libraries, version catalog supports declaring plugin versions. While libraries are represented by their group, artifact and version coordinates, Gradle plugins are identified by their id and version only.

### Plugin Declaration

```groovy
dependencyResolutionManagement {
    versionCatalogs {
        libs {
            plugin('versions', 'com.github.ben-manes.versions').version('0.45.0')
        }
    }
}
```

Or in TOML:

```toml
[plugins]
versions = { id = "com.github.ben-manes.versions", version = "0.45.0" }
```

### Using Plugins

The plugin is accessible in the `plugins` block and can be consumed in any project:

```kotlin
plugins {
    id("java-library")
    id("checkstyle")
    // Use the plugin `versions` as declared in the `libs` version catalog
    alias(libs.plugins.versions)
}
```

## Real-World Android Example

### libs.versions.toml

```toml
[versions]
kotlin = "1.9.20"
compose = "1.5.4"
androidx-core = "1.12.0"
androidx-lifecycle = "2.6.2"
retrofit = "2.9.0"
room = "2.6.0"

[libraries]
# Kotlin
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }

# AndroidX Core
androidx-core-ktx = { module = "androidx.core:core-ktx", version.ref = "androidx-core" }

# Lifecycle
androidx-lifecycle-runtime = { module = "androidx.lifecycle:lifecycle-runtime-ktx", version.ref = "androidx-lifecycle" }
androidx-lifecycle-viewmodel = { module = "androidx.lifecycle:lifecycle-viewmodel-ktx", version.ref = "androidx-lifecycle" }

# Compose
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
compose-material3 = { module = "androidx.compose.material3:material3", version.ref = "compose" }
compose-ui-tooling = { module = "androidx.compose.ui:ui-tooling", version.ref = "compose" }

# Networking
retrofit = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
retrofit-gson = { module = "com.squareup.retrofit2:converter-gson", version.ref = "retrofit" }

# Room
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
room-ktx = { module = "androidx.room:room-ktx", version.ref = "room" }
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }

[bundles]
lifecycle = ["androidx-lifecycle-runtime", "androidx-lifecycle-viewmodel"]
compose = ["compose-ui", "compose-material3", "compose-ui-tooling"]
retrofit = ["retrofit", "retrofit-gson"]
room = ["room-runtime", "room-ktx"]

[plugins]
android-application = { id = "com.android.application", version = "8.1.2" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
ksp = { id = "com.google.devtools.ksp", version = "1.9.20-1.0.14" }
```

### Usage in build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.ksp)
}

dependencies {
    implementation(libs.androidx.core.ktx)

    // Using bundles
    implementation(libs.bundles.lifecycle)
    implementation(libs.bundles.compose)
    implementation(libs.bundles.retrofit)
    implementation(libs.bundles.room)

    // KSP for Room
    ksp(libs.room.compiler)
}
```

## Benefits Summary

1. **Type Safety**: IDE autocompletion and compile-time checking
2. **Centralization**: Single source of truth for all dependencies
3. **Consistency**: Same version used across all modules
4. **Maintainability**: Easy to update versions in one place
5. **Readability**: Clean, organized dependency declarations
6. **Refactoring**: Rename-safe with IDE support
7. **Bundles**: Group related dependencies together
8. **Plugin Management**: Centralized plugin version control

## Migration Strategy

When migrating to version catalogs:

1. Create `gradle/libs.versions.toml`
2. Extract versions to `[versions]` section
3. Move library declarations to `[libraries]`
4. Move plugin declarations to `[plugins]`
5. Create bundles for commonly grouped dependencies
6. Update build files to use `libs.*` accessors
7. Test build to ensure everything works
8. Remove old dependency declarations

---

## Ответ

**Gradle Version Catalog** - это механизм для управления зависимостями и плагинами в масштабируемом виде. Вместо жесткого кодирования имен и версий зависимостей в отдельных файлах сборки, можно создать центральный каталог версий, на который различные модули могут ссылаться типобезопасным способом с поддержкой автодополнения в Android Studio.

## Преимущества Version Catalog

1. **Типобезопасные аксессоры**: Gradle генерирует типобезопасные аксессоры для легкого добавления зависимостей с автодополнением в IDE

2. **Централизованное управление версиями**: Каталог виден всем проектам сборки. Это центральное место для объявления версии зависимости, гарантирующее применение изменений ко всем подпроектам

3. **Бандлы зависимостей**: Каталоги могут объявлять бандлы зависимостей - "группы зависимостей", которые обычно используются вместе

4. **Ссылки на версии**: Каталоги могут разделять группу и имя зависимости от фактической версии, позволяя делиться объявлением версии между несколькими зависимостями

## Создание файла каталога версий

### Базовая настройка

В папке `gradle` корневого проекта создайте файл `libs.versions.toml`. Gradle по умолчанию ищет каталог в файле `libs.versions.toml`.

Добавьте следующие секции:

```toml
[versions]      # Версии зависимостей

[libraries]     # Объявления библиотек

[plugins]       # Объявления плагинов

[bundles]       # Группы зависимостей
```

### Пример каталога

```toml
[versions]
groovy = "3.0.5"
checkstyle = "8.37"

[libraries]
groovy-core = { module = "org.codehaus.groovy:groovy", version.ref = "groovy" }
groovy-json = { module = "org.codehaus.groovy:groovy-json", version.ref = "groovy" }
groovy-nio = { module = "org.codehaus.groovy:groovy-nio", version.ref = "groovy" }

[bundles]
groovy = ["groovy-core", "groovy-json", "groovy-nio"]

[plugins]
versions = { id = "com.github.ben-manes.versions", version = "0.45.0" }
```

## Алиасы и типобезопасные аксессоры

### Правила именования

Алиасы должны состоять из идентификаторов, разделенных:
- Дефисом (`-`) - **рекомендуется**
- Подчеркиванием (`_`)
- Точкой (`.`)

**Валидные алиасы:**
- `guava`
- `groovy-core`
- `commons-lang3`
- `androidx.awesome.lib`

### Генерация аксессоров

Для алиасов: `guava`, `groovy-core`, `groovy-xml`, `groovy-json`, `androidx.awesome.lib`

Gradle генерирует:

```kotlin
libs.guava
libs.groovy.core
libs.groovy.xml
libs.groovy.json
libs.androidx.awesome.lib
```

### Использование в build-файлах

```kotlin
dependencies {
    implementation(libs.guava)
    implementation(libs.groovy.core)
    implementation(libs.androidx.awesome.lib)
}
```

## Бандлы зависимостей

Бандл - это алиас для нескольких зависимостей, которые обычно используются вместе.

### Без бандла

```kotlin
dependencies {
    implementation(libs.groovy.core)
    implementation(libs.groovy.json)
    implementation(libs.groovy.nio)
}
```

### С бандлом

```kotlin
dependencies {
    implementation(libs.bundles.groovy)
}
```

Семантика эквивалентна: добавление одного бандла равносильно добавлению всех зависимостей, которые в него входят.

## Плагины

Помимо библиотек, каталог версий поддерживает объявление версий плагинов.

### Объявление в TOML

```toml
[plugins]
versions = { id = "com.github.ben-manes.versions", version = "0.45.0" }
```

### Использование плагинов

```kotlin
plugins {
    id("java-library")
    id("checkstyle")
    alias(libs.plugins.versions)
}
```

## Практический пример для Android

### libs.versions.toml

```toml
[versions]
kotlin = "1.9.20"
compose = "1.5.4"
androidx-core = "1.12.0"
androidx-lifecycle = "2.6.2"
retrofit = "2.9.0"
room = "2.6.0"

[libraries]
# Kotlin
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }

# AndroidX Core
androidx-core-ktx = { module = "androidx.core:core-ktx", version.ref = "androidx-core" }

# Lifecycle
androidx-lifecycle-runtime = { module = "androidx.lifecycle:lifecycle-runtime-ktx", version.ref = "androidx-lifecycle" }
androidx-lifecycle-viewmodel = { module = "androidx.lifecycle:lifecycle-viewmodel-ktx", version.ref = "androidx-lifecycle" }

# Compose
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
compose-material3 = { module = "androidx.compose.material3:material3", version.ref = "compose" }
compose-ui-tooling = { module = "androidx.compose.ui:ui-tooling", version.ref = "compose" }

# Networking
retrofit = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
retrofit-gson = { module = "com.squareup.retrofit2:converter-gson", version.ref = "retrofit" }

# Room
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
room-ktx = { module = "androidx.room:room-ktx", version.ref = "room" }
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }

[bundles]
lifecycle = ["androidx-lifecycle-runtime", "androidx-lifecycle-viewmodel"]
compose = ["compose-ui", "compose-material3", "compose-ui-tooling"]
retrofit = ["retrofit", "retrofit-gson"]
room = ["room-runtime", "room-ktx"]

[plugins]
android-application = { id = "com.android.application", version = "8.1.2" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
ksp = { id = "com.google.devtools.ksp", version = "1.9.20-1.0.14" }
```

### Использование в build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.ksp)
}

dependencies {
    implementation(libs.androidx.core.ktx)

    // Использование бандлов
    implementation(libs.bundles.lifecycle)
    implementation(libs.bundles.compose)
    implementation(libs.bundles.retrofit)
    implementation(libs.bundles.room)

    // KSP для Room
    ksp(libs.room.compiler)
}
```

## Основные преимущества

1. **Типобезопасность**: Автодополнение в IDE и проверка на этапе компиляции
2. **Централизация**: Единый источник истины для всех зависимостей
3. **Консистентность**: Одинаковая версия используется во всех модулях
4. **Поддерживаемость**: Легко обновлять версии в одном месте
5. **Читаемость**: Чистые, организованные объявления зависимостей
6. **Рефакторинг**: Безопасное переименование с поддержкой IDE
7. **Бандлы**: Группировка связанных зависимостей
8. **Управление плагинами**: Централизованный контроль версий плагинов

## Стратегия миграции

При миграции на Version Catalog:

1. Создайте `gradle/libs.versions.toml`
2. Извлеките версии в секцию `[versions]`
3. Переместите объявления библиотек в `[libraries]`
4. Переместите объявления плагинов в `[plugins]`
5. Создайте бандлы для часто группируемых зависимостей
6. Обновите build-файлы для использования аксессоров `libs.*`
7. Протестируйте сборку
8. Удалите старые объявления зависимостей

---

## References

- [Migrate your build to version catalogs](https://developer.android.com/build/migrate-to-catalogs)
- [Sharing dependency versions between projects](https://docs.gradle.org/current/userguide/platforms.html)
- [Using Version Catalog on Android projects](https://proandroiddev.com/using-version-catalog-on-android-projects-82d88d2f79e5)
- [Is the New Gradle Version Catalog Worth It for Your Android Projects?](https://molidevwrites.com/is-the-new-gradle-version-catalog-worth-it-for-your-android-projects/)
