---
id: 20251016-162851
title: "Measure Project Size / Измерение размера проекта"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-how-to-write-recyclerview-cache-ahead--android--medium, q-flow-testing-turbine--testing--medium, q-how-navigation-is-implemented-in-android--android--medium]
created: 2025-10-15
tags: [android/project-structure, apk-size, codebase-analysis, codebase-size, metrics, modules, project-metrics, project-structure, difficulty/easy]
---

# Как можно измерить размер проекта?

**English**: How can you measure project size?

## Answer (EN)
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
 app/                    ← Main app module
 core/
    network/           ← Networking library
    database/          ← Database layer
    ui/                ← Shared UI components
    utils/             ← Utility functions
 feature/
    login/             ← Login feature
    profile/           ← Profile feature
    chat/              ← Chat feature
    settings/          ← Settings feature
 test/
     shared/            ← Shared test utilities
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

## Ответ (RU)

Размер проекта можно измерить несколькими способами:
1. **Строки кода (LOC)** - общее количество строк исходного кода
2. **Количество модулей** - уровень модуляризации
3. **Размер APK** - размер финального приложения

**Типичный крупный проект:** около **100,000 строк кода**, разделённых на **5-10 модулей**.

---

## Метрики измерения

### 1. Строки кода (LOC)

**Определение:** Подсчет строк исходного кода в проекте.

**Как измерить:**

```bash
# Подсчитать все Kotlin файлы
find . -name "*.kt" | xargs wc -l

# Подсчитать все Java файлы
find . -name "*.java" | xargs wc -l

# Подсчитать и Kotlin и Java
find . \( -name "*.kt" -o -name "*.java" \) | xargs wc -l
```

**Пример вывода:**
```
   1234 ./app/src/main/java/com/example/MainActivity.kt
   567 ./app/src/main/java/com/example/ViewModel.kt
   890 ./feature/login/src/main/java/Login.kt
   ...
   102345 total
```

---

#### Использование Android Studio

**Плагин Statistic:**

1. Установить плагин "Statistic"
2. **Analyze → Statistic**
3. Просмотреть детальную разбивку:
   - Строки кода по типу файла
   - Строки по пакету
   - Соотношение комментариев
   - Пустые строки

**Пример отчета:**
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

#### Интерпретация размера кода

| Размер проекта | Диапазон LOC | Типичная сложность |
|----------------|--------------|-------------------|
| **Маленький** | < 10,000 | Приложение с одной функцией, прототип |
| **Средний** | 10,000 - 50,000 | Стандартное приложение, 2-5 функций |
| **Большой** | 50,000 - 200,000 | Корпоративное приложение, 5-10 модулей |
| **Очень большой** | > 200,000 | Сложная платформа, 10+ модулей |

**Примеры проектов:**
- **Маленький:** Приложение калькулятор (~2,000 LOC)
- **Средний:** Новостной ридер (~25,000 LOC)
- **Большой:** Банковское приложение (~120,000 LOC)
- **Очень большой:** Платформа социальных медиа (~500,000 LOC)

---

### 2. Количество модулей

**Определение:** Подсчет Gradle модулей в проекте.

**Как измерить:**

```bash
# Подсчитать файлы build.gradle.kts (у каждого модуля есть один)
find . -name "build.gradle.kts" | wc -l

# Или подсчитать includes в settings.gradle.kts
cat settings.gradle.kts | grep "include" | wc -l
```

**Пример settings.gradle.kts:**
```kotlin
include(":app")
include(":core:network")
include(":core:database")
include(":feature:login")
include(":feature:profile")
include(":feature:chat")
include(":feature:settings")
```

**Количество модулей:** 7 модулей

---

#### Организация модулей

**Типичная структура модулей:**

```
project/
 app/                    ← Главный модуль приложения
 core/
    network/           ← Библиотека сети
    database/          ← Слой базы данных
    ui/                ← Общие UI компоненты
    utils/             ← Утилиты
 feature/
    login/             ← Функция входа
    profile/           ← Функция профиля
    chat/              ← Функция чата
    settings/          ← Функция настроек
 test/
     shared/            ← Общие тестовые утилиты
```

**Всего:** 12 модулей

---

#### Интерпретация количества модулей

| Модуляризация | Количество модулей | Преимущества |
|---------------|-------------------|-------------|
| **Монолитная** | 1 | Просто, быстрые сборки (маленькие приложения) |
| **Базовая** | 2-4 | Некоторое разделение, умеренные сборки |
| **Модульная** | 5-10 | Хорошее разделение, параллельные сборки |
| **Высоко модульная** | 10-20 | Отличное разделение, сложная настройка |
| **Микросервисы** | 20+ | Независимо развертываемые единицы |

**Пример:**
```kotlin
// Типичный большой проект: 5-10 модулей
:app                    // Главный модуль
:core-network           // HTTP клиент, API вызовы
:core-database          // Room, хранение данных
:core-ui                // Общие UI компоненты
:feature-login          // Экран входа
:feature-home           // Главный экран
:feature-profile        // Профиль пользователя
:feature-settings       // Настройки приложения
```

---

### 3. Размер APK

**Определение:** Размер скомпилированного пакета Android приложения.

**Как измерить:**

#### Вариант 1: Собрать и проверить APK

```bash
# Собрать release APK
./gradlew assembleRelease

# Проверить размер APK
ls -lh app/build/outputs/apk/release/app-release.apk

# Пример вывода:
# -rw-r--r-- 1 user staff 15M Oct 4 app-release.apk
```

---

#### Вариант 2: Android Studio APK Analyzer

1. **Build → Analyze APK**
2. Выбрать файл APK
3. Просмотреть детальную разбивку:
   - Общий размер
   - Размер ресурсов
   - Размер DEX файлов
   - Размер нативных библиотек
   - Размер ассетов

**Пример разбивки:**
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

#### Интерпретация размера APK

| Категория приложения | Типичный размер | Примечания |
|---------------------|----------------|-----------|
| **Легковесное** | < 10 MB | Утилиты, простые игры |
| **Стандартное** | 10-30 MB | Большинство приложений продуктивности |
| **С медиа-контентом** | 30-100 MB | Социальные медиа, фото приложения |
| **Большое** | 100-500 MB | Игры, видео-стриминг |
| **Очень большое** | > 500 MB | AAA игры, оффлайн видео приложения |

**Примеры:**
- Калькулятор: ~2 MB
- Twitter: ~35 MB
- Instagram: ~60 MB
- PUBG Mobile: ~900 MB

---

### 4. Другие метрики

#### Количество методов

```bash
# Подсчитать методы используя плагин dexcount
./gradlew countDebugDexMethods

# Вывод:
# Total methods: 45,234
# Total fields:  12,345
```

**Лимит Android:** 65,536 методов на DEX файл (требуется MultiDex если превышено)

---

#### Количество файлов

```bash
# Подсчитать все исходные файлы
find ./src -type f | wc -l

# Подсчитать по типу
find ./src -name "*.kt" | wc -l    # Kotlin файлы
find ./src -name "*.xml" | wc -l   # XML layouts
```

---

#### Количество зависимостей

```bash
# Список всех зависимостей
./gradlew dependencies

# Подсчитать уникальные зависимости
./gradlew dependencies | grep "---" | wc -l
```

**Пример:**
```
+--- androidx.core:core-ktx:1.12.0
+--- androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.2
+--- com.squareup.retrofit2:retrofit:2.9.0
+--- org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3
...
Total: 47 dependencies
```

---

## Полный пример: Метрики реального проекта

### Пример: E-commerce приложение среднего размера

```
Метрики проекта:
================
Строки кода:       78,234 LOC
  - Kotlin:        62,187 LOC (79.5%)
  - Java:           8,456 LOC (10.8%)
  - XML:            7,591 LOC (9.7%)

Модули:           8 модулей
  - app
  - core-network
  - core-database
  - core-ui
  - feature-catalog
  - feature-cart
  - feature-checkout
  - feature-profile

Размер APK:       24.3 MB (release)
  - Код:           6.8 MB
  - Ресурсы:       9.2 MB
  - Нативные lib:  7.1 MB
  - Другое:        1.2 MB

Методы:           42,156 методов
Файлы:            523 исходных файла
Зависимости:      38 библиотек
Время сборки:     2м 15с (инкрементальная)
```

---

## Разбивка типичного большого проекта

**~100,000 LOC, 5-10 модулей:**

```
Структура проекта:
==================

1. app модуль (~10,000 LOC)
   - Класс Application
   - Главная activity
   - Настройка навигации
   - Внедрение зависимостей

2. core модули (~30,000 LOC)
   - core-network:  8,000 LOC
   - core-database: 7,000 LOC
   - core-ui:       6,000 LOC
   - core-domain:   5,000 LOC
   - core-utils:    4,000 LOC

3. feature модули (~55,000 LOC)
   - feature-auth:     12,000 LOC
   - feature-home:     10,000 LOC
   - feature-profile:   8,000 LOC
   - feature-messages:  9,000 LOC
   - feature-settings:  7,000 LOC
   - feature-search:    9,000 LOC

4. test модули (~5,000 LOC)
   - Юнит-тесты
   - Интеграционные тесты
   - UI тесты

APK: 25-35 MB (типично)
Время сборки: 3-5 минут (чистая)
```

---

## Инструменты измерения

### 1. SonarQube

```bash
# Запустить анализ SonarQube
./gradlew sonarqube
```

**Предоставляемые метрики:**
- Строки кода
- Сложность кода (цикломатическая)
- Дублирование кода
- Code smells
- Технический долг

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

**Вывод:** `app/build/reports/lint-results.html`

---

## Лучшие практики

### 1. Мониторинг роста

```kotlin
// Отслеживать метрики со временем
// Commit: 2024-01-01
LOC: 50,000
APK: 18 MB
Модули: 5

// Commit: 2024-06-01
LOC: 78,000 (+56%)
APK: 24 MB (+33%)
Модули: 8 (+3)
```

### 2. Установка лимитов

```gradle
// Применить лимит размера APK
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

### 3. Регулярная очистка

- Удалять неиспользуемые зависимости
- Удалять мертвый код
- Оптимизировать ресурсы (изображения, строки)
- Использовать R8/ProGuard shrinking

---

## Резюме

**Как измерить размер проекта:**

1. **Строки кода (LOC)**
   - Find + wc -l
   - Плагин Statistics в Android Studio
   - Типичный большой проект: **~100,000 LOC**

2. **Количество модулей**
   - Подсчитать build.gradle файлы
   - Проверить includes в settings.gradle
   - Типичный большой проект: **5-10 модулей**

3. **Размер APK**
   - Собрать и проверить размер файла
   - APK Analyzer в Android Studio
   - Типичный большой проект: **20-40 MB**

4. **Другие метрики**
   - Количество методов
   - Количество файлов
   - Количество зависимостей
   - Время сборки

**Инструменты:**
- Android Studio (APK Analyzer, плагин Statistics)
- SonarQube (качество кода)
- Detekt (статический анализ Kotlin)
- Dexcount (подсчет методов)

**Лучшие практики:**
- Мониторить метрики со временем
- Устанавливать лимиты размера
- Регулярная очистка и оптимизация

## Related Questions

- [[q-how-to-write-recyclerview-cache-ahead--android--medium]]
- [[q-flow-testing-turbine--android--medium]]
- [[q-how-navigation-is-implemented-in-android--android--medium]]
