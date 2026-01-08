---\
id: android-056
title: KAPT to KSP Migration Guide / Руководство по миграции с KAPT на KSP
aliases: [KAPT to KSP Migration Guide, Руководство по миграции с KAPT на KSP]
topic: android
subtopics: [performance-startup]
question_kind: coding
difficulty: medium
original_language: en
language_tags: [en, ru]
source: Original
source_note: Annotation processing migration best practices
status: draft
moc: moc-android
related: [c-android, c-android-profiler, q-annotation-processing-android--android--medium, q-background-tasks-decision-guide--android--medium, q-kapt-vs-ksp--android--medium, q-workmanager-decision-guide--android--medium]
created: 2025-10-11
updated: 2025-11-11
tags: [android/performance-startup, annotation-processing, difficulty/medium, en, kapt, ksp, ru]

---\
# Вопрос (RU)
> Подробно сравните KAPT и KSP для обработки аннотаций. Мигрируйте зависимости библиотек с KAPT на KSP. Измерьте и задокументируйте улучшения времени сборки.

# Question (EN)
> Compare KAPT and KSP for annotation processing in depth. Migrate library dependencies from KAPT to KSP. Measure and document build time improvements.

---

## Ответ (RU)

### Архитектура KAPT Vs KSP

#### KAPT (Kotlin Annotation Processing Tool)

**Как работает:**
```text
1. Kotlin-код → генерация Java-заглушек
2. Java-заглушки → запуск Java-аннотационных процессоров
3. Сгенерированный код → компиляция в байт-код

Стоимость: генерация заглушек и неинкрементальные процессоры могут быть дорогими и медленными
```

**Диаграмма архитектуры:**
```text
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
```text
1. Kotlin-код → KSP-процессор (прямой доступ к Kotlin-символам)
2. Генерация кода → компиляция в байт-код

Преимущество: нет генерации Java-заглушек, архитектура изначально под быструю и инкрементальную обработку
```

**Диаграмма архитектуры:**
```text
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

### Сравнение Производительности (пример)

Пример синтетического бенчмарка (не гарантия; измеряйте в своём проекте):

**Тестовый проект:**
- 50 исходных файлов
- БД `Room` (5 сущностей, 3 DAO)
- `Hilt` (10 модулей)
- `Moshi` (15 data-классов)

**KAPT (пример):**
```text
Время конфигурации: 8.2с
Обработка KAPT: 45.3с
  - Генерация заглушек: 18.7с
  - Room processor: 14.2с
  - Hilt processor: 9.8с
  - Moshi processor: 2.6с
Общая сборка: 89.5с
```

**KSP (пример):**
```text
Время конфигурации: 8.2с
Обработка KSP: 22.1с
  - Room processor: 7.3с
  - Dagger (ядро) через KSP: см. официальную документацию
  - Moshi через KSP: см. официальную документацию
Общая сборка: 46.8с

Улучшение: ~47.7% быстрее в данном сценарии (89.5с → 46.8с)
```

Типичные реальные улучшения при миграции основных процессоров (`Room`, некоторые реализации `Dagger`, `Moshi` и др., если у них есть реализация на KSP) находятся примерно в диапазоне 20–50%, но всегда проверяйте на своём проекте.

### Полное Руководство По Миграции

#### Шаг 1: Проверка Поддержки Библиотек

Проверьте официальную документацию каждой библиотеки на наличие артефактов с поддержкой KSP.

Примеры (ориентировочно 2024, обязательно уточняйте актуальные версии и артефакты):
```kotlin
// Библиотеки с вариантами под KSP (пример; проверяйте документацию):
- Room 2.6.0+ (использует room-compiler через ksp)
- Dagger (core) предоставляет KSP-поддержку: см. https://dagger.dev/dev-guide/ksp.html
- Moshi: поддерживает KSP через использование `com.squareup.moshi:moshi-kotlin-codegen` с конфигурацией ksp(...)

// Всё ещё только KAPT или частичная поддержка (пример):
- Некоторые части Hilt по-прежнему требуют kapt (проверяйте актуальную документацию)
- Устаревшие аннотационные процессоры без реализации под KSP
```

Не предполагайте, что «все библиотеки генерации кода» поддерживают KSP — всегда проверяйте.

#### Шаг 2: Обновление Файлов Сборки

Пример для Gradle Kotlin DSL.

Важно: ниже показан образец миграции. Конкретные координаты артефактов для KSP (особенно для Dagger/Hilt и `Moshi`) необходимо брать из официальной документации; не все предыдущие kapt-артефакты можно просто заменить на `ksp(...)`.

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

    // Hilt с KAPT (пример конфигурации)
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-android-compiler:2.50")

    // Moshi с KAPT codegen (пример; см. актуальную документацию)
    implementation("com.squareup.moshi:moshi:1.15.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    kapt("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
}
```

**После: конфигурация KSP (для поддерживаемых процессоров)**

**build.gradle.kts (уровень проекта):**
```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.21" apply false
    id("com.google.dagger.hilt.android") version "2.50" apply false
    id("com.google.devtools.ksp") version "1.9.21-1.0.16" apply false // добавить KSP (версию сверить с документацией)
}
```

**build.gradle.kts (app-модуль, пример: `Room` и `Dagger` core через KSP, `Hilt` частично на KAPT при необходимости):**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")              // оставить для тех частей, которые всё ещё требуют KAPT (например, отдельные Hilt-компоненты)
    id("com.google.devtools.ksp")  // KSP для поддерживаемых процессоров
    id("dagger.hilt.android.plugin")
}

android {
    // ... android configuration

    // Пример конфигурации KSP для Room (аргументы зависят от документации Room)
    ksp {
        arg("room.schemaLocation", "${'$'}projectDir/schemas")
    }
}

dependencies {
    // Room с KSP
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // Dagger core с KSP (пример; точную конфигурацию смотрите в официальной документации Dagger)
    implementation("com.google.dagger:dagger:2.50")
    ksp("com.google.dagger:dagger-compiler:2.50")

    // Hilt: часть конфигурации по-прежнему может использовать KAPT.
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-android-compiler:2.50")

    // Moshi: использование через KSP — тот же артефакт, но подключённый через ksp(...)
    implementation("com.squareup.moshi:moshi:1.15.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    // При наличии KSP-конфигурации:
    // ksp("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
}
```

Убедитесь, что версия KSP совместима с версией Kotlin (см. таблицу соответствий в документации KSP) и что вы используете именно те артефакты, которые официально заявлены как KSP-совместимые для каждой библиотеки. Не используйте несуществующие артефакты вроде `moshi-kotlin-codegen-ksp`.

#### Шаг 3: Обновление Путей К Исходникам (при необходимости)

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

#### Шаг 4: Очистка И Пересборка

```bash
./gradlew clean
# (Опционально) удалить устаревшие выводы KAPT
rm -rf build/generated/source/kapt/
# Сборка с KSP
./gradlew assembleDebug --scan
# Сравнить время сборки с конфигурацией на KAPT
```

### Чек-лист Миграции (RU)

- [ ] Обновить project-level build.gradle (добавить плагин KSP)
- [ ] Обновить app-level build.gradle (подключить KSP и оставить KAPT только для неподдерживаемых процессоров)
- [ ] Перевести зависимости с `kapt(...)` на `ksp(...)` только для тех библиотек, у которых есть официальные KSP-артефакты (например, `Dagger` core, `Room`, `Moshi`)
- [ ] Настроить аргументы KSP (например, `room.schemaLocation`) согласно документации
- [ ] Убедиться, что IDE/Gradle видят сгенерированные исходники
- [ ] Очистить результаты сборки
- [ ] Запустить полную сборку
- [ ] Проверить корректность работы сгенерированного кода
- [ ] Запустить все тесты
- [ ] Измерить и зафиксировать время сборки до/после
- [ ] Обновить конфигурацию CI/CD
- [ ] Обновить документацию

### Тестирование Миграции (RU)

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

Язык и структура сгенерированного кода (Java vs Kotlin) могут отличаться, важно функциональное совпадение. При необходимости можно использовать `javap` для проверки того, что нужные классы существуют и корректно слинкованы.

### Смешанные KAPT/KSP Проекты (RU)

Если часть библиотек ещё не поддерживает KSP, временно используйте оба инструмента:

```kotlin
plugins {
    id("kotlin-kapt")          // для неподдерживаемых библиотек
    id("com.google.devtools.ksp") // для библиотек с поддержкой KSP
}

dependencies {
    // Библиотеки с поддержкой KSP (пример: Room, Dagger core, Moshi)
    // Hilt и другие KAPT-only библиотеки остаются на kapt

    implementation("com.some.legacy:library:1.0.0")
    kapt("com.some.legacy:library-compiler:1.0.0")
}
```

Учтите: пока существует хотя бы один KAPT-процессор, часть его накладных расходов сохраняется. Стремитесь со временем полностью перейти на KSP для всех поддерживаемых библиотек.

### Измерение Времени Сборки (RU)

**Пример скрипта для сравнения KAPT и KSP:**

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
- Малый проект (< 50 файлов): KAPT 25с, KSP 15с → ~40% быстрее
- Средний проект (50–200 файлов): KAPT 89с, KSP 47с → ~47% быстрее
- Крупный проект (200+ файлов): KAPT 245с, KSP 128с → ~48% быстрее

### Решение Проблем (RU)

**Проблема 1: Не находятся сгенерированные классы**
- Проверьте, применён ли плагин KSP в модуле.
- Проверьте, что для KSP-совместимых библиотек используется `ksp(...)`, а не `kapt(...)`.
- Убедитесь, что IDE/Gradle видят директории `build/generated/ksp/...` (при необходимости добавьте в sourceSets).

**Проблема 2: Аргументы KSP не применяются**
- Для KAPT использовалась секция `kapt { arguments { ... } }`.
- Для KSP используйте блок `ksp { arg("key", "value") }`.

**Проблема 3: Нет ожидаемой инкрементальности**
- Обновите версии KSP и процессоров.
- Проверьте, что используемые процессоры заявляют поддержку инкрементальной обработки.
- Не форсируйте параметры задач без понимания поведения процессоров.

### Лучшие Практики (RU)

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

### Распространённые Ошибки (RU)

1. Механически заменяют `kapt(...)` на `ksp(...)` без подтверждённой поддержки KSP.
2. Оставляют старые KAPT-артефакты, мешающие IDE/сборке.
3. Используют версию KSP, не соответствующую версии Kotlin.
4. Предполагают, что все процессоры поддерживают KSP.
5. Не проверяют все варианты сборки (debug/release/flavors).
6. Игнорируют предупреждения о неинкрементальных процессорах.
7. Не обновляют CI/CD и получают отличия от локальных сборок.
8. Лишний раз настраивают sourceSets там, где KSP уже всё сделал автоматически.
9. Ожидают идентичного исходного или байт-кода вместо функционального эквивалента.
10. Воспринимают заявленные ускорения как гарантию, не измеряя в своём проекте.

## Answer (EN)

### KAPT Vs KSP Architecture

#### KAPT (Kotlin Annotation Processing Tool)

**How it works:**
```text
1. Kotlin code → Generate Java stubs
2. Java stubs → Run Java annotation processors
3. Generated code → Compile to bytecode

Cost: Stub generation and non-incremental processors can be expensive and slow
```

**Architecture diagram:**
```text
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
```text
1. Kotlin code → KSP processor (direct access to Kotlin symbols)
2. Generated code → Compile to bytecode

Benefit: No Java stub generation; designed for faster and more incremental processing
```

**Architecture diagram:**
```text
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
- `Room` database (5 entities, 3 DAOs)
- `Hilt` dependency injection (10 modules)
- `Moshi` JSON parsing (15 data classes)

**KAPT results (example):**
```text
Configuration time: 8.2s
KAPT processing: 45.3s
  - Stub generation: 18.7s
  - Room processor: 14.2s
  - Hilt processor: 9.8s
  - Moshi processor: 2.6s
Total build: 89.5s
```

**KSP results (example):**
```text
Configuration time: 8.2s
KSP processing: 22.1s
  - Room processor: 7.3s
  - Dagger core via KSP: see official docs
  - Moshi via KSP: see official docs
Total build: 46.8s

Improvement: ~47.7% faster in this setup (89.5s → 46.8s)
```

Typical real-world improvements reported by projects migrating major processors (`Room`, `Dagger` core, `Moshi` etc. where KSP implementations exist) range roughly 20–50%, but always validate with your own measurements.

### Complete Migration Guide

#### Step 1: Check Library Support

Confirm KSP support and required artifact coordinates in each library’s official docs.

Examples (approx. 2024; always re-check current docs):
```kotlin
// Libraries with KSP support (examples; verify):
- Room 2.6.0+ (uses room-compiler via ksp)
- Dagger core has KSP support: see https://dagger.dev/dev-guide/ksp.html
- Moshi: supports KSP by using `com.squareup.moshi:moshi-kotlin-codegen` with ksp(...)

// Still KAPT-only or partial:
- Some Hilt components/setups still require kapt
- Legacy processors without KSP implementation
```

Do not assume “all codegen libraries” support KSP; always verify.

#### Step 2: Update Build Files

Example uses Gradle Kotlin DSL.

Important: This is a migration pattern. For each library, use the actual KSP-compatible artifact names as documented; do not blindly switch `kapt(...)` to `ksp(...)`.

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

    // Moshi with kapt-based codegen
    implementation("com.squareup.moshi:moshi:1.15.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    kapt("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
}
```

**After: KSP configuration (for supported processors)**

**build.gradle.kts (project level):**
```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.21" apply false
    id("com.google.dagger.hilt.android") version "2.50" apply false
    id("com.google.devtools.ksp") version "1.9.21-1.0.16" apply false // Add KSP (ensure compatibility)
}
```

**build.gradle.kts (app module; example: `Room` and `Dagger` core on KSP, `Hilt` partly on KAPT):**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")              // keep for processors that still require KAPT (e.g., some Hilt parts)
    id("com.google.devtools.ksp")  // use for KSP-supported processors
    id("dagger.hilt.android.plugin")
}

android {
    // ... android configuration

    ksp {
        arg("room.schemaLocation", "${'$'}projectDir/schemas")
    }
}

dependencies {
    // Room with KSP
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // Dagger core with KSP (see official docs for latest coordinates)
    implementation("com.google.dagger:dagger:2.50")
    ksp("com.google.dagger:dagger-compiler:2.50")

    // Hilt remains on KAPT where required
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-android-compiler:2.50")

    // Moshi: same artifact, wired via ksp(...)
    implementation("com.squareup.moshi:moshi:1.15.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    // Enable Moshi KSP codegen if configured in your project:
    // ksp("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
}
```

Ensure the KSP plugin version matches your Kotlin version as per official KSP docs, and only switch dependencies from `kapt(...)` to `ksp(...)` when the library provides a KSP-compatible artifact. Do not use fictitious artifacts like `moshi-kotlin-codegen-ksp`.

#### Step 3: Update Source Paths (If Needed)

In many cases, KSP automatically wires generated sources. If your IDE/build does not see generated code, configure explicitly:

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
./gradlew clean
# (Optional) Remove stale KAPT outputs
rm -rf build/generated/source/kapt/
# Build with KSP
./gradlew assembleDebug --scan
# Compare build times (vs KAPT configuration or branch)
```

### Migration Checklist (EN)

- [ ] Update project-level build.gradle (add KSP plugin)
- [ ] Update app-level build.gradle (enable KSP; keep KAPT only for unsupported processors)
- [ ] Migrate `kapt(...)` dependencies to `ksp(...)` only where official KSP artifacts exist (e.g., `Room`, `Dagger` core, `Moshi`)
- [ ] Configure KSP arguments (e.g., `room.schemaLocation`) per library docs
- [ ] Ensure generated sources are visible to IDE/build
- [ ] Clean build outputs
- [ ] Run full build
- [ ] Verify generated code is functionally correct
- [ ] Run all tests
- [ ] Measure and record build times (before/after)
- [ ] Update CI/CD configuration
- [ ] Update documentation

### Testing Migration (EN)

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

### Mixed KAPT/KSP Projects (EN)

Some libraries may not support KSP yet. You can run both processors during migration:

```kotlin
plugins {
    id("kotlin-kapt")          // Keep for unsupported libraries
    id("com.google.devtools.ksp") // Use for supported libraries
}

dependencies {
    // KSP-supported libraries (e.g., Room, Dagger core, Moshi)
    // Hilt/Dagger parts that are KAPT-only stay on kapt

    implementation("com.some.legacy:library:1.0.0")
    kapt("com.some.legacy:library-compiler:1.0.0")
}
```

Note: As long as any KAPT processor remains, some KAPT overhead persists. Aim to move all supported libraries to KSP over time.

### Build Time Measurements (EN)

Example script to compare KAPT vs KSP configurations:

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
- Small project (< 50 files): KAPT 25s, KSP 15s → ~40% faster
- Medium project (50–200 files): KAPT 89s, KSP 47s → ~47% faster
- Large project (200+ files): KAPT 245s, KSP 128s → ~48% faster

### Troubleshooting (EN)

**Issue 1: Generated files not found**
- Check that the KSP plugin is applied in the module.
- Ensure `ksp(...)` is used for KSP-supported libraries and `kapt(...)` only where needed.
- Verify the `build/generated/ksp/...` directories are recognized by IDE/Gradle.

**Issue 2: KSP arguments not recognized**
- KAPT style:
```kotlin
kapt {
    arguments {
        // ...
    }
}
```
- KSP style:
```kotlin
ksp {
    arg("room.schemaLocation", "${'$'}projectDir/schemas")
}
```

**Issue 3: Incremental processing not working as expected**
- Use recent versions of KSP and processors.
- Confirm processors declare incremental support.
- Avoid forcing flags on KSP tasks without understanding processor capabilities.

### Best Practices (EN)

1. Migrate incrementally: by module and by processor.
2. Run full tests after each migration step.
3. Verify generated code presence and runtime behavior.
4. Measure and record build times before/after.
5. Keep KSP, Kotlin, and processor versions aligned.
6. Use mixed KAPT+KSP only as a temporary transition.
7. Monitor CI/build server resource usage.
8. Enable and respect incremental processing where supported.
9. Watch Gradle/compiler warnings for misconfigurations.
10. Document migration steps and decisions.

### Common Pitfalls (EN)

1. Blindly changing `kapt(...)` to `ksp(...)` without confirmed KSP support.
2. Leaving stale KAPT-generated sources that confuse IDE/build.
3. Using a KSP version incompatible with Kotlin.
4. Assuming all processors support KSP.
5. Not testing all build variants (debug/release/flavors).
6. Ignoring KSP or Gradle warnings about non-incremental processors.
7. Forgetting to update CI/CD.
8. Over-configuring source sets when KSP already wires them automatically.
9. Expecting identical generated source or bytecode instead of functional equivalence.
10. Treating reported speedups as guaranteed without measuring.

## Дополнительные Вопросы (RU)

- Как вы спланируете поэтапный rollout миграции на KSP в многомодульном проекте для снижения рисков?
- Как отлаживать проблемы, когда сгенерированный код отличается между реализациями библиотеки на KAPT и KSP?
- Какие метрики и инструменты вы встроите в CI для постоянного отслеживания производительности сборки после миграции?
- Как вы будете работать с критичной библиотекой, которая поддерживает только KAPT, когда остальная часть проекта уже на KSP?
- Как организовать конфигурацию Gradle, чтобы поддерживать читаемую и масштабируемую настройку KSP/KAPT для разных вариантов и flavor-ов?

## Follow-ups (EN)

- How would you design a step-by-step rollout of KSP migration across a multi-module project to reduce risk?
- How do you debug issues when generated code differs between KAPT and KSP implementations of the same library?
- What metrics and tools would you integrate into CI to continuously track build performance after migration?
- How would you handle a critical library that only supports KAPT while the rest of the project is on KSP?
- How can you structure Gradle configuration to keep KSP/KAPT setup maintainable across variants and flavors?

## Ссылки (RU)

- https://kotlinlang.org/docs/ksp-overview.html
- https://kotlinlang.org/docs/ksp-quickstart.html
- https://developer.android.com/jetpack/androidx/releases/room#ksp
- https://dagger.dev/dev-guide/ksp.html
- Официальная документация используемых библиотек (`Room`, Dagger/Hilt, `Moshi` и др.) для актуальных артефактов KSP

## References (EN)

- https://kotlinlang.org/docs/ksp-overview.html
- https://kotlinlang.org/docs/ksp-quickstart.html
- https://developer.android.com/jetpack/androidx/releases/room#ksp
- https://dagger.dev/dev-guide/ksp.html
- Official docs for the libraries you use (`Room`, Dagger/Hilt, `Moshi`, etc.) for up-to-date KSP artifacts

## Связанные Вопросы (RU)

### Предварительные Материалы / Концепции
- [[c-android]]
- [[c-android-profiler]]

### Похожие (Medium)
- [[q-annotation-processing-android--android--medium]] — Обработка аннотаций в Android
- [[q-annotation-processing--android--medium]] — Общие принципы обработки аннотаций

### Продвинутые (Harder)
- [[q-compose-performance-optimization--android--hard]] — Оптимизация производительности Compose

## Related Questions (EN)

### Prerequisites / Concepts
- [[c-android]]
- [[c-android-profiler]]

### Related (Medium)
- [[q-annotation-processing-android--android--medium]] - Annotation processing in Android
- [[q-annotation-processing--android--medium]] - Annotation processing principles

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose performance optimization
