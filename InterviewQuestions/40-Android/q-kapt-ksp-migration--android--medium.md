---
id: android-056
title: KAPT to KSP Migration Guide / Руководство по миграции с KAPT на KSP
aliases:
- KAPT to KSP Migration Guide
- Руководство по миграции с KAPT на KSP
topic: android
subtopics:
- gradle
- performance-startup
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: Original
source_note: Annotation processing migration best practices
status: draft
moc: moc-android
related:
- c-gradle
- c-performance-optimization
created: 2025-10-11
updated: 2025-11-10
tags:
- android/gradle
- android/performance-startup
- annotation-processing
- difficulty/medium
- en
- kapt
- ksp
- ru
---

# Вопрос (RU)
> Подробно сравните KAPT и KSP для обработки аннотаций. Мигрируйте зависимости библиотек с KAPT на KSP. Измерьте и задокументируйте улучшения времени сборки.

# Question (EN)
> Compare KAPT and KSP for annotation processing in depth. Migrate library dependencies from KAPT to KSP. Measure and document build time improvements.

---

## Ответ (RU)

### Архитектура KAPT vs KSP

#### KAPT (Kotlin Annotation Processing Tool)

**Как работает:**
```
1. Kotlin-код → генерация Java-заглушек
2. Java-заглушки → запуск Java-аннотационных процессоров
3. Сгенерированный код → компиляция в байт-код

Стоимость: генерация заглушек и неинкрементальные процессоры могут быть дорогими и медленными
```

**Диаграмма архитектуры:**
```
Kotlin Source (.kt)
    ↓
[Генерация Java заглушек]
    ↓
Java Stubs (.java)
    ↓
[Java Annotation Processor]
    ↓
Сгенерированный код
    ↓
[Kotlin/Java Compiler]
    ↓
Байт-код
```

**Ограничения (на практике):**
- Дополнительный шаг генерации Java-заглушек увеличивает время сборки и потребление памяти.
- Инкрементальность зависит от конкретных процессоров; многие долгое время работали неинкрементально, что приводило к частым полным переработкам.
- Как правило, медленнее и ресурсоёмче KSP на Kotlin-ориентированных проектах.

#### KSP (Kotlin Symbol Processing)

**Как работает:**
```
1. Kotlin-код → KSP-процессор (прямой доступ к Kotlin-символам)
2. Генерация кода → компиляция в байт-код

Преимущество: нет генерации Java-заглушек, архитектура изначально под быструю и инкрементальную обработку
```

**Диаграмма архитектуры:**
```
Kotlin Source (.kt)
    ↓
[KSP Processor] ← Прямой доступ к API Kotlin-символов
    ↓
Сгенерированный код
    ↓
[Kotlin Compiler]
    ↓
Байт-код
```

**Преимущества:**
- Обычно заметно быстрее KAPT для поддерживаемых процессоров (нет шага заглушек, тесная интеграция с Kotlin).
- Поддерживает инкрементальную обработку (затрагиваются только изменённые файлы), при условии что процессоры реализуют инкрементальность.
- Нативный Kotlin API для написания процессоров (лучшая типобезопасность и работа с null).
- Часто меньшее потребление памяти.

### Сравнение производительности (пример)

Пример синтетического бенчмарка (не гарантия; измеряйте в своём проекте):

**Тестовый проект:**
- 50 исходных файлов
- БД Room (5 сущностей, 3 DAO)
- Hilt (10 модулей)
- Moshi (15 data-классов)

**KAPT (пример):**
```
Время конфигурации: 8.2с
Обработка KAPT: 45.3с
  - Генерация заглушек: 18.7с
  - Room processor: 14.2с
  - Hilt processor: 9.8с
  - Moshi processor: 2.6с
Общая сборка: 89.5с
```

**KSP (пример):**
```
Время конфигурации: 8.2с
Обработка KSP: 22.1с
  - Room processor: 7.3с
  - Hilt processor: 11.2с
  - Moshi processor: 3.6с
Общая сборка: 46.8с

Улучшение: ~47.7% быстрее в данном сценарии (89.5с → 46.8с)
```

Типичные реальные улучшения при миграции основных процессоров (Room, Hilt/Dagger, Moshi и др.) находятся примерно в диапазоне 20–50%, но всегда проверяйте на своём проекте.

### Полное руководство по миграции

#### Шаг 1: Проверка поддержки библиотек

Проверьте официальную документацию каждой библиотеки на наличие артефактов с поддержкой KSP.

Примеры (ориентировочно 2024):
```kotlin
// Библиотеки с вариантами под KSP (уточнять версии в документации):
- Room 2.6.0+ (room-compiler через ksp)
- Hilt/Dagger с KSP-совместимыми артефактами (см. dagger.dev)
- Moshi (moshi-kotlin-codegen через ksp)

// Всё ещё только KAPT или частичная поддержка:
- Некоторые конфигурации Dagger без KSP-артефактов
- Устаревшие аннотационные процессоры без реализации под KSP
```

Не предполагаете, что «все библиотеки генерации кода» поддерживают KSP — всегда проверяйте.

#### Шаг 2: Обновление файлов сборки

Пример для Gradle Kotlin DSL.

**До: конфигурация KAPT**

**build.gradle.kts (app-модуль):**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt") // плагин KAPT
    id("dagger.hilt.android.plugin")
}

android {
    // ... android configuration

    kapt {
        correctErrorTypes = true
        useBuildCache = true
    }
}

dependencies {
    // Room с KAPT
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")

    // Hilt с KAPT
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-android-compiler:2.50")

    // Moshi с KAPT
    implementation("com.squareup.moshi:moshi:1.15.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    kapt("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
}
```

**После: конфигурация KSP**

**build.gradle.kts (уровень проекта):**
```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.21" apply false
    id("com.google.dagger.hilt.android") version "2.50" apply false
    id("com.google.devtools.ksp") version "1.9.21-1.0.16" apply false // добавить KSP
}
```

**build.gradle.kts (app-модуль):**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp") // заменить kotlin-kapt на KSP для поддерживаемых процессоров
    id("dagger.hilt.android.plugin")
}

android {
    // ... android configuration

    // Пример конфигурации KSP для Room
    ksp {
        arg("room.schemaLocation", "${'$'}projectDir/schemas")
        arg("room.incremental", "true")
        arg("room.expandProjection", "true")
    }

    // В большинстве актуальных конфигураций KSP сам добавляет сгенерированные директории.
    // Явно указывать пути нужно только при проблемах с IDE/сборкой.
    // Пример (опционально):
    // kotlin.sourceSets {
    //     getByName("debug") {
    //         kotlin.srcDir("build/generated/ksp/debug/kotlin")
    //     }
    // }
}

dependencies {
    // Room с KSP
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1") // было kapt

    // Hilt/Dagger с KSP-совместимым компилятором (уточнить артефакт по документации)
    implementation("com.google.dagger:hilt-android:2.50")
    ksp("com.google.dagger:hilt-android-compiler:2.50")

    // Moshi с KSP
    implementation("com.squareup.moshi:moshi:1.15.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    ksp("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
}
```

Убедитесь, что версия KSP совместима с версией Kotlin (см. таблицу соответствий в документации KSP).

#### Шаг 3: Обновление путей к исходникам (при необходимости)

Во многих случаях KSP автоматически регистрирует директории. Если IDE или сборка не видит сгенерированный код, добавьте явно:

**KAPT (исторически):**
```kotlin
sourceSets {
    getByName("main") {
        java.srcDir("build/generated/source/kapt/main")
    }
}
```

**KSP (опционально):**
```kotlin
kotlin.sourceSets {
    getByName("main") {
        kotlin.srcDir("build/generated/ksp/main/kotlin")
    }
    getByName("debug") {
        kotlin.srcDir("build/generated/ksp/debug/kotlin")
    }
    getByName("release") {
        kotlin.srcDir("build/generated/ksp/release/kotlin")
    }
}
```

#### Шаг 4: Очистка и пересборка

```bash
# Очистка старых файлов
./gradlew clean

# (Опционально) удалить устаревшие выводы KAPT
rm -rf build/generated/source/kapt/

# Сборка с KSP
./gradlew assembleDebug --scan

# Сравнить время сборки с конфигурацией на KAPT
```

### Чек-лист миграции

```
[ ] Обновить project-level build.gradle (добавить KSP плагин)
[ ] Обновить app-level build.gradle (kotlin-kapt → ksp для поддерживаемых процессоров)
[ ] Перевести зависимости с kapt(...) на ksp(...) при наличии KSP-артефактов
[ ] Настроить аргументы KSP (например, room.schemaLocation)
[ ] Убедиться, что IDE/Gradle видят сгенерированные исходники
[ ] Очистить результаты сборки
[ ] Запустить полную сборку
[ ] Проверить корректность работы сгенерированного кода
[ ] Запустить все тесты
[ ] Измерить и зафиксировать время сборки до/после
[ ] Обновить конфигурацию CI/CD
[ ] Обновить документацию
```

### Тестирование миграции

**Проверка сгенерированного кода и путей:**

**До миграции (KAPT):**
```bash
./gradlew assembleDebug
ls -la app/build/generated/source/kapt/debug/
# например: AppDatabase_Impl.java, UserDao_Impl.java, MainActivity_GeneratedInjector.java
```

**После миграции (KSP):**
```bash
./gradlew assembleDebug
ls -la app/build/generated/ksp/debug/kotlin/
# или app/build/generated/ksp/debug/java/ в зависимости от процессора
```

Язык и структура сгенерированного кода (Java vs Kotlin) могут отличаться, важно функциональное совпадение.

При необходимости можно использовать `javap` для проверки того, что нужные классы существуют и корректно слинкованы.

### Смешанные KAPT/KSP проекты

Если часть библиотек ещё не поддерживает KSP, временно используйте оба инструмента:

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")          // для неподдерживаемых библиотек
    id("com.google.devtools.ksp") // для библиотек с поддержкой KSP
}

dependencies {
    // Библиотеки с поддержкой KSP
    implementation("androidx.room:room-runtime:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // Пример Hilt/Dagger через KSP (если поддерживается вашей конфигурацией)
    implementation("com.google.dagger:hilt-android:2.50")
    ksp("com.google.dagger:hilt-android-compiler:2.50")

    // Только KAPT (устаревшие библиотеки)
    implementation("com.some.legacy:library:1.0.0")
    kapt("com.some.legacy:library-compiler:1.0.0")
}
```

Учтите: пока существует хотя бы один KAPT-процессор, часть его накладных расходов сохраняется. Стремитесь со временем полностью перейти на KSP.

### Измерение времени сборки

**Пример скрипта:**

**measure_build_times.sh:**
```bash
#!/bin/bash

echo "=== Сравнение времени сборки: KAPT vs KSP ==="

# Измерение сборки с KAPT
echo "Измеряем KAPT..."
git checkout kapt-version
./gradlew clean > /dev/null 2>&1
KAPT_START=$(date +%s)
./gradlew assembleDebug --no-build-cache
KAPT_END=$(date +%s)
KAPT_TIME=$((KAPT_END - KAPT_START))

# Измерение сборки с KSP
echo "Измеряем KSP..."
git checkout ksp-version
./gradlew clean > /dev/null 2>&1
KSP_START=$(date +%s)
./gradlew assembleDebug --no-build-cache
KSP_END=$(date +%s)
KSP_TIME=$((KSP_END - KSP_START))

IMPROVEMENT=$(awk "BEGIN { if ($KAPT_TIME > 0) printf \"%.2f\", (($KAPT_TIME - $KSP_TIME) / $KAPT_TIME) * 100; else print 0 }")

echo ""
echo "Результаты:"
echo "  Время сборки KAPT: ${KAPT_TIME}с"
echo "  Время сборки KSP: ${KSP_TIME}с"
echo "  Улучшение: ${IMPROVEMENT}%"
```

**Примеры (не гарантии):**
```
Малый проект (< 50 файлов):
  KAPT: 25с, KSP: 15с  → ~40% быстрее
Средний проект (50-200 файлов):
  KAPT: 89с, KSP: 47с  → ~47% быстрее
Крупный проект (200+ файлов):
  KAPT: 245с, KSP: 128с → ~48% быстрее
```

### Решение проблем

**Проблема 1: Не находятся сгенерированные классы**

Проверьте:
- применён ли плагин KSP в модуле;
- используются ли ksp(...) вместо kapt(...) для соответствующих зависимостей;
- видит ли IDE/Gradle директории `build/generated/ksp/...` (при необходимости — добавить в sourceSets).

**Проблема 2: Аргументы KSP не применяются**

KAPT:
```kotlin
kapt {
    arguments {
        arg("room.schemaLocation", "${'$'}projectDir/schemas")
    }
}
```

KSP:
```kotlin
ksp {
    arg("room.schemaLocation", "${'$'}projectDir/schemas")
}
```

**Проблема 3: Нет ожидаемой инкрементальности**

- Обновите версии KSP и процессоров.
- Убедитесь, что используемые процессоры заявляют поддержку инкрементальной обработки.
- Не форсируйте параметры задач (например, `incremental = true`) без понимания поведения процессоров.

### Лучшие практики

1. Мигрировать по модулям и по процессорам, а не всем сразу.
2. После каждого шага запускать тесты и проверять функциональность.
3. Проверять наличие и корректность сгенерированных классов в build-дереве.
4. Измерять и документировать время сборки до/после.
5. Следить за совместимостью версий Kotlin, KSP и библиотек.
6. Использовать смешанный режим (KAPT+KSP) только временно.
7. Мониторить ресурсы CI/серверов сборки; фиксировать улучшения.
8. Включать и использовать инкрементальность, если её поддерживают процессоры.
9. Обращать внимание на предупреждения Gradle/KSP.
10. Документировать изменения для команды.

### Распространённые ошибки

1. Забыли заменить kapt(...) на ksp(...) для библиотек с поддержкой KSP.
2. Оставили старые KAPT-артефакты, которые мешают IDE/сборке.
3. Используют версию KSP, не соответствующую версии Kotlin.
4. Предполагают, что все процессоры поддерживают KSP.
5. Не проверяют все варианты сборки (debug/release/flavors).
6. Игнорируют предупреждения об неинкрементальных процессорах.
7. Не обновили CI/CD и получают отличия от локальных сборок.
8. Излишне настраивают sourceSets там, где KSP уже всё подключил автоматически.
9. Ожидают идентичного исходного или байт-кода вместо функционального эквивалента.
10. Принимают «2x быстрее» как гарантию, а не измеряют сами.

---

## Answer (EN)

### KAPT vs KSP Architecture

#### KAPT (Kotlin Annotation Processing Tool)

**How it works:**
```
1. Kotlin code → Generate Java stubs
2. Java stubs → Run Java annotation processors
3. Generated code → Compile to bytecode

Cost: Stub generation and non-incremental processors can be expensive and slow
```

**Architecture diagram:**
```
Kotlin Source (.kt)
    ↓
[Generate Java Stubs]
    ↓
Java Stubs (.java)
    ↓
[Java Annotation Processor]
    ↓
Generated Code
    ↓
[Kotlin/Java Compiler]
    ↓
Bytecode
```

**Limitations (in practice):**
- Additional Java stub generation step increases build time and memory usage.
- Incremental builds depend on processors being incremental-aware; many popular processors historically were not, causing frequent non-incremental runs.
- Slower compilation and higher memory footprint vs KSP on typical Kotlin-heavy projects.

#### KSP (Kotlin Symbol Processing)

**How it works:**
```
1. Kotlin code → KSP processor (direct access to Kotlin symbols)
2. Generated code → Compile to bytecode

Benefit: No Java stub generation; designed for faster and more incremental processing
```

**Architecture diagram:**
```
Kotlin Source (.kt)
    ↓
[KSP Processor] ← Direct Kotlin symbol API access
    ↓
Generated Code
    ↓
[Kotlin Compiler]
    ↓
Bytecode
```

**Benefits:**
- Typically significantly faster than KAPT for supported processors because it avoids stub generation and is integrated with the Kotlin compiler.
- Supports incremental processing (only affected files), assuming processors are implemented to be incremental.
- Kotlin-native symbol API (better type safety and null-safety for processor authors).
- Lower memory usage in many setups.

### Performance Comparison (Example)

Illustrative synthetic benchmark (not a guarantee; measure in your project):

**Benchmark project:**
- 50 source files
- Room database (5 entities, 3 DAOs)
- Hilt dependency injection (10 modules)
- Moshi JSON parsing (15 data classes)

**KAPT results (example):**
```
Configuration time: 8.2s
KAPT processing: 45.3s
  - Stub generation: 18.7s
  - Room processor: 14.2s
  - Hilt processor: 9.8s
  - Moshi processor: 2.6s
Total build: 89.5s
```

**KSP results (example):**
```
Configuration time: 8.2s
KSP processing: 22.1s
  - Room processor: 7.3s
  - Hilt processor: 11.2s
  - Moshi processor: 3.6s
Total build: 46.8s

Improvement: ~47.7% faster in this setup (89.5s → 46.8s)
```

Typical real-world improvements reported by projects migrating major processors (Room, Hilt/Dagger, Moshi, etc.) range roughly 20–50%, but always validate with your own measurements.

### Complete Migration Guide

#### Step 1: Check Library Support

Confirm KSP support and required artifact coordinates in each library’s official docs.

Examples (approx. 2024):
```kotlin
// Libraries with KSP support variants (check latest versions):
- Room 2.6.0+ (room-compiler via ksp)
- Hilt and Dagger with KSP-capable artifacts (see dagger.dev docs)
- Moshi (moshi-kotlin-codegen via ksp)

// Still KAPT-only or partial:
- Some Dagger setups without KSP-compatible artifacts
- Various legacy annotation processors without KSP implementation
```

Do not assume “all auto-generated code libraries” support KSP; always verify.

#### Step 2: Update Build Files

Example uses Gradle Kotlin DSL.

**Before: KAPT configuration**

**build.gradle.kts (app module):**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt") // KAPT plugin
    id("dagger.hilt.android.plugin")
}

android {
    // ... android configuration

    kapt {
        correctErrorTypes = true
        useBuildCache = true
    }
}

dependencies {
    // Room with KAPT
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")

    // Hilt with KAPT
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-android-compiler:2.50")

    // Moshi with KAPT
    implementation("com.squareup.moshi:moshi:1.15.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    kapt("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
}
```

**After: KSP configuration**

**build.gradle.kts (project level):**
```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.21" apply false
    id("com.google.dagger.hilt.android") version "2.50" apply false
    id("com.google.devtools.ksp") version "1.9.21-1.0.16" apply false // Add KSP
}
```

**build.gradle.kts (app module):**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp") // Replace kotlin-kapt with KSP for supported processors
    id("dagger.hilt.android.plugin")
}

android {
    // ... android configuration

    // KSP configuration (example for Room)
    ksp {
        arg("room.schemaLocation", "${'$'}projectDir/schemas")
        arg("room.incremental", "true")
        arg("room.expandProjection", "true")
    }

    // In most modern setups KSP configures source sets automatically.
    // Add explicit mappings only if your IDE/build setup requires it.
    // Example (optional):
    // kotlin.sourceSets {
    //     getByName("debug") {
    //         kotlin.srcDir("build/generated/ksp/debug/kotlin")
    //     }
    // }
}

dependencies {
    // Room with KSP
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1") // changed from kapt to ksp

    // Hilt with KSP-compatible compiler (check dagger.dev for exact artifact)
    implementation("com.google.dagger:hilt-android:2.50")
    ksp("com.google.dagger:hilt-android-compiler:2.50")

    // Moshi with KSP
    implementation("com.squareup.moshi:moshi:1.15.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    ksp("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
}
```

Ensure KSP plugin version matches your Kotlin version as per official KSP docs.

#### Step 3: Update Source Paths (If Needed)

In many cases, KSP automatically wires generated sources. If your tooling does not pick them up (especially with custom setups), configure explicitly:

**KAPT generated sources (legacy):**
```kotlin
sourceSets {
    getByName("main") {
        java.srcDir("build/generated/source/kapt/main")
    }
}
```

**KSP generated sources (optional explicit config):**
```kotlin
kotlin.sourceSets {
    getByName("main") {
        kotlin.srcDir("build/generated/ksp/main/kotlin")
    }
    getByName("debug") {
        kotlin.srcDir("build/generated/ksp/debug/kotlin")
    }
    getByName("release") {
        kotlin.srcDir("build/generated/ksp/release/kotlin")
    }
}
```

#### Step 4: Clean and Rebuild

```bash
# Clean old generated files
./gradlew clean

# (Optional) Remove stale KAPT outputs if present
rm -rf build/generated/source/kapt/

# Build with KSP
./gradlew assembleDebug --scan

# Compare build times (vs KAPT branch or configuration)
```

### Migration Checklist

```
[ ] Update project-level build.gradle (add KSP plugin)
[ ] Update app-level build.gradle (replace kotlin-kapt with ksp for supported processors)
[ ] Migrate kapt(...) dependencies to ksp(...) where KSP implementations exist
[ ] Configure KSP arguments (e.g., room.schemaLocation)
[ ] Ensure generated sources are visible to IDE/build (auto or explicit source sets)
[ ] Clean build outputs
[ ] Run full build
[ ] Verify generated code is functionally correct
[ ] Run all tests
[ ] Measure and record build times (before/after)
[ ] Update CI/CD configuration
[ ] Update documentation
```

### Testing Migration

**Verify generated code and wiring:**

**Before migration (KAPT):**
```bash
./gradlew assembleDebug
ls -la app/build/generated/source/kapt/debug/
# e.g. AppDatabase_Impl.java, UserDao_Impl.java, MainActivity_GeneratedInjector.java
```

**After migration (KSP):**
```bash
./gradlew assembleDebug
ls -la app/build/generated/ksp/debug/kotlin/
# or app/build/generated/ksp/debug/java/ depending on processor
```

Generated code structure and language (Java vs Kotlin) may differ between KAPT and KSP implementations, but behavior must be equivalent.

If desired, you can:
```bash
javap -c app/build/intermediates/javac/debug/classes/com/example/UserDao_Impl.class
```
To confirm classes are generated and linked, not to guarantee bytecode identity.

### Mixed KAPT/KSP Projects

Some libraries may not support KSP yet. You can run both processors in parallel during migration:

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")          // Keep for unsupported libraries
    id("com.google.devtools.ksp") // Use for supported libraries
}

dependencies {
    // KSP-supported libraries
    implementation("androidx.room:room-runtime:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // Example Hilt/Dagger with KSP where applicable
    implementation("com.google.dagger:hilt-android:2.50")
    ksp("com.google.dagger:hilt-android-compiler:2.50")

    // KAPT-only libraries (legacy)
    implementation("com.some.legacy:library:1.0.0")
    kapt("com.some.legacy:library-compiler:1.0.0")
}
```

Note: This reduces but does not eliminate KAPT overhead. Plan to remove KAPT once all processors have KSP support.

### Build Time Measurements

Example script to compare branches/configurations:

**measure_build_times.sh:**
```bash
#!/bin/bash

echo "=== Build Time Comparison: KAPT vs KSP ==="

# Measure KAPT build
echo "Measuring KAPT build..."
git checkout kapt-version
./gradlew clean > /dev/null 2>&1
KAPT_START=$(date +%s)
./gradlew assembleDebug --no-build-cache
KAPT_END=$(date +%s)
KAPT_TIME=$((KAPT_END - KAPT_START))

# Measure KSP build
echo "Measuring KSP build..."
git checkout ksp-version
./gradlew clean > /dev/null 2>&1
KSP_START=$(date +%s)
./gradlew assembleDebug --no-build-cache
KSP_END=$(date +%s)
KSP_TIME=$((KSP_END - KSP_START))

IMPROVEMENT=$(awk "BEGIN { if ($KAPT_TIME > 0) printf \"%.2f\", (($KAPT_TIME - $KSP_TIME) / $KAPT_TIME) * 100; else print 0 }")

echo ""
echo "Results:"
echo "  KAPT build time: ${KAPT_TIME}s"
echo "  KSP build time: ${KSP_TIME}s"
echo "  Improvement: ${IMPROVEMENT}%"
```

**Illustrative outcomes (not guaranteed):**
```
Small project (< 50 files):
  KAPT: 25s, KSP: 15s  → ~40% faster
Medium project (50-200 files):
  KAPT: 89s, KSP: 47s  → ~47% faster
Large project (200+ files):
  KAPT: 245s, KSP: 128s → ~48% faster
```

### Troubleshooting

**Issue 1: Generated files not found**

```
Error: Unresolved reference: AppDatabase_Impl
```

**Check:**
- KSP plugin applied in module.
- Dependencies use ksp(...) instead of kapt(...).
- Generated sources directory recognized (auto or via kotlin.sourceSets).

**Issue 2: KSP arguments not recognized**

KAPT style:
```kotlin
kapt {
    arguments {
        arg("room.schemaLocation", "${'$'}projectDir/schemas")
    }
}
```

KSP style:
```kotlin
ksp {
    arg("room.schemaLocation", "${'$'}projectDir/schemas")
}
```

**Issue 3: Incremental processing not working as expected**

- Ensure you are using recent versions of KSP and processors.
- Verify processors declare incremental support; otherwise builds may fall back to non-incremental.
- Avoid forcing flags like `incremental = true` on KspTask without understanding processor capabilities.

### Best Practices

1. Migrate incrementally: start with one module and one processor.
2. Run full test suite after each migration step.
3. Validate that generated code is present and runtime behavior is correct.
4. Measure and record build times before and after migration.
5. Keep KSP, Kotlin, and processor versions aligned and up to date.
6. Use mixed KAPT+KSP setup only as a temporary transition.
7. Monitor CI/build server resource usage; KSP often reduces memory and time.
8. Enable and respect incremental processing where supported.
9. Watch Gradle and compiler warnings for misconfigurations.
10. Document migration steps and decisions for the team.

### Common Pitfalls

1. Not updating dependencies from kapt(...) to ksp(...) for supported libraries.
2. Leaving stale KAPT-generated sources that confuse IDE or build.
3. Using a KSP version incompatible with the Kotlin version.
4. Assuming all processors support KSP; always check docs.
5. Not testing all build variants (debug/release/flavors).
6. Ignoring KSP or Gradle warnings about non-incremental processors.
7. Forgetting to update CI/CD to use the new configuration.
8. Over-configuring source sets when KSP already wires them automatically.
9. Expecting identical generated source code or bytecode instead of functional equivalence.
10. Assuming fixed "2x faster" improvement instead of measuring in your project.

---

## References
- https://kotlinlang.org/docs/ksp-overview.html
- https://kotlinlang.org/docs/ksp-quickstart.html
- https://developer.android.com/jetpack/androidx/releases/room#ksp
- https://dagger.dev/dev-guide/ksp.html

## Follow-ups

- How would you design a step-by-step rollout of KSP migration across a multi-module project to reduce risk?
- How do you debug issues when generated code differs between KAPT and KSP implementations of the same library?
- What metrics and tools would you integrate into CI to continuously track build performance after migration?
- How would you handle a critical library that only supports KAPT while the rest of the project is on KSP?
- How can you structure Gradle configuration to keep KSP/KAPT setup maintainable across variants and flavors?

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]
- [[c-performance-optimization]]

### Related (Medium)
- [[q-kapt-vs-ksp--android--medium]] - Annotation Processing
- [[q-annotation-processing-android--android--medium]] - Annotations
- [[q-annotation-processing--android--medium]] - Annotation Processing
- [[q-reduce-apk-size-techniques--android--medium]] - Build Optimization

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
