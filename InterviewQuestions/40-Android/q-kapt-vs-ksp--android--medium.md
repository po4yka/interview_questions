---
id: android-020
title: kapt vs KSP comparison / Сравнение kapt и KSP
aliases:
- kapt vs KSP comparison
- Сравнение kapt и KSP
topic: android
subtopics:
- gradle
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority
status: draft
moc: moc-android
related:
- c-gradle
- q-fix-slow-app-startup-legacy--android--hard
- q-looper-thread-connection--android--medium
- q-macrobenchmark-startup--android--medium
created: 2025-10-06
updated: 2025-11-10
tags:
- android/gradle
- difficulty/medium
- en
- ru
---

# Вопрос (RU)
> В чем разница между kapt и KSP? Какой использовать?

# Question (EN)
> What is the difference between kapt and KSP? Which one to use?

---

## Ответ (RU)

**kapt** (Kotlin Annotation Processing Tool) — это адаптер, позволяющий использовать Java annotation processors в Kotlin-проектах за счёт генерации Java-stub'ов из Kotlin-кода. **KSP** (Kotlin Symbol Processing) — Kotlin-first API, который работает напрямую с Kotlin-символами без генерации stubs и изначально спроектирован быстрее и лучше для инкрементальной компиляции.

### Сравнение

| Функция | kapt | KSP |
|---------|------|-----|
| **Скорость** | Медленнее (есть генерация Java stubs, дополнительный шаг) | Обычно заметно быстрее (нет stubs; более эффективная интеграция) |
| **Фокус по языку** | Java annotation processing (JSR 269) | Kotlin-first API для работы с символами |
| **API** | Стандартный Java Annotation Processing API (javax.annotation.processing / JSR 269) | Отдельный Kotlin Symbol Processing API |
| **Поддержка библиотек** | Любые процессоры, реализованные как Java annotation processors (напр. legacy Dagger 2, Glide, старые процессоры) | Растущая нативная поддержка (Room, Moshi, Hilt 2.44+, Dagger через KSP-артефакты и др.) |
| **Инкрементальность** | Ограниченная, возможны проблемы из-за stubs | Из коробки лучше интегрирован с инкрементальной сборкой |

### Пример использования kapt

```kotlin
// build.gradle.kts
plugins {
    kotlin("kapt")
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0")
}
```

### Пример использования KSP

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "<ksp-version>" // версия должна соответствовать версии Kotlin
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    ksp("androidx.room:room-compiler:2.6.0")
}
```

### Разница в производительности

KSP, как правило, уменьшает время сборки по сравнению с kapt, так как не генерирует Java stubs и лучше интегрируется с инкрементальной компиляцией. На реальных проектах ускорение может быть значительным (часто вплоть до примерно 2x для модулей с тяжёлой аннотационной генерацией), но точные числа зависят от конкретного кода.

Пример (иллюстративно):

```
Сборка с kapt:    45 секунд
Сборка с KSP:     23 секунды
```

### Поддержка библиотек

**Часто имеют поддержку KSP (уточняйте версии в документации):**
- Room
- Moshi
- Hilt (через поддержку KSP в Dagger, начиная примерно с 2.44+)
- Dagger (через dagger-ksp артефакты)
- Многие современные библиотеки

**Могут по-прежнему требовать kapt:**
- Старые конфигурации Dagger 2 без миграции на KSP
- Glide (процессор основан на Java APT; поддержка KSP зависит от версии/конфигурации)
- Legacy / неактивно поддерживаемые библиотеки, предоставляющие только Java annotation processors

Всегда проверяйте документацию конкретной библиотеки: если есть артефакт для KSP, предпочтителен KSP.

### Миграция с kapt на KSP (по процессорам)

Базовый пример миграции для библиотеки с поддержкой KSP (например, Room):

```kotlin
// До (kapt)
plugins {
    kotlin("kapt")
}

dependencies {
    kapt("androidx.room:room-compiler:2.6.0")
}

// После (KSP)
plugins {
    id("com.google.devtools.ksp") version "<ksp-version>"
}

dependencies {
    ksp("androidx.room:room-compiler:2.6.0")
}
```

Если проект использует несколько процессоров, можно:
- Переводить на `ksp(...)` только те зависимости, для которых есть официальные KSP-артефакты.
- Оставлять `kapt` подключённым только для тех процессоров, у которых нет поддержки KSP.

**Пути сгенерированного кода (нужны не всегда):**

```kotlin
// kapt (пример)
sourceSets.getByName("main") {
    java.srcDir("build/generated/source/kapt/main")
}

// KSP (пример; синтаксис может отличаться)
kotlin {
    sourceSets.main {
        kotlin.srcDir("build/generated/ksp/main/kotlin")
    }
}
```

В большинстве современных конфигураций AGP+KSP эти пути настраиваются автоматически; вручную их добавляют только при специфических требованиях.

### Когда что использовать

**Используйте KSP, когда:**
- Библиотека предоставляет официальный KSP-артефакт (Room, Moshi, Hilt с KSP, Dagger с KSP и т.п.).
- Важна скорость сборки и предсказуемая инкрементальность.
- Новый проект или активная модернизация.

**Используйте kapt, когда:**
- Нужная библиотека имеет только Java annotation processor и не поддерживает KSP.
- Большой legacy-проект, где миграция всех процессоров пока нецелесообразна.

**Краткое содержание**: kapt подключает Java annotation processors к Kotlin, но добавляет stubs и хуже по производительности/инкрементальности. KSP — Kotlin-first, обычно быстрее и лучше масштабируется. Предпочитайте KSP там, где есть поддержка; держите kapt только для тех процессоров, которые пока не могут работать через KSP.

## Answer (EN)

**kapt** (Kotlin Annotation Processing Tool) is an adapter that allows using Java annotation processors in Kotlin projects by generating Java-compiled stubs from Kotlin code. **KSP** (Kotlin Symbol Processing) is a Kotlin-first API that works directly with Kotlin symbols without stub generation and is designed to be faster and more incremental.

### Comparison

| Feature | kapt | KSP |
|---------|------|-----|
| **Speed** | Slower (generates Java stubs; extra compilation step) | Often significantly faster (no stubs; more efficient integration) |
| **Language focus** | Java annotation processing (JSR 269) | Kotlin-first symbol API |
| **API** | Uses Java annotation processing API (javax.annotation.processing / JSR 269) | Uses dedicated Kotlin Symbol Processing API |
| **Library support** | Works with processors implemented as Java annotation processors (e.g. legacy Dagger 2, Glide, older processors) | Growing native support (Room, Moshi, Hilt 2.44+, Dagger via KSP artifacts, many modern processors) |
| **Incremental processing** | Limited / can break incrementality due to stubs | Designed for better incremental and caching behavior |

### Kapt Usage (example)

```kotlin
// build.gradle.kts
plugins {
    kotlin("kapt")
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0")
}
```

### KSP Usage (example)

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "<ksp-version>" // use version compatible with your Kotlin version
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    ksp("androidx.room:room-compiler:2.6.0")
}
```

### Performance Difference

KSP typically reduces build times compared to kapt because it avoids generating Java stubs and integrates better with incremental compilation. In many real projects this can lead to noticeable improvements (often up to around 2x for annotation-processing-heavy modules), but the exact numbers depend on the codebase.

Example (illustrative only):

```
Build with kapt:    45 seconds
Build with KSP:     23 seconds
```

### Library Support

**Commonly support KSP (check docs for exact versions):**
- Room
- Moshi
- Hilt (via Dagger KSP support; e.g. 2.44+)
- Dagger (via dagger-ksp artifacts)
- Many newer or actively maintained libraries

**May still require kapt (as of many legacy setups):**
- Older Dagger 2 setups without KSP migration
- Glide (annotation processor is Java-AP based; KSP support depends on version and configuration)
- Some legacy or unmaintained libraries that only expose Java annotation processors

Always check each library's documentation: if it provides a KSP artifact, prefer KSP for that library.

### Migration from kapt to KSP (per-processor)

Basic migration for a library that supports KSP (e.g. Room):

```kotlin
// Before (kapt)
plugins {
    kotlin("kapt")
}

dependencies {
    kapt("androidx.room:room-compiler:2.6.0")
}

// After (KSP)
plugins {
    id("com.google.devtools.ksp") version "<ksp-version>"
}

dependencies {
    ksp("androidx.room:room-compiler:2.6.0")
}
```

If your project uses multiple processors, you can:
- Switch each dependency that has a KSP artifact from `kapt(...)` to `ksp(...)`.
- Keep `kapt` applied only for processors that do not yet support KSP.

**Generated sources paths (only when manual configuration is needed):**

```kotlin
// kapt-generated sources (example)
sourceSets.getByName("main") {
    java.srcDir("build/generated/source/kapt/main")
}

// KSP-generated sources (example; adjust to your Gradle/Kotlin DSL style)
kotlin {
    sourceSets.main {
        kotlin.srcDir("build/generated/ksp/main/kotlin")
    }
}
```

In most modern Android Gradle Plugin / KSP setups, these paths are wired automatically; manual configuration is only needed for custom setups.

### When to Use Each

**Use KSP when:**
- The library provides official KSP support (e.g. Room, Hilt with KSP, Moshi, modern Dagger, etc.).
- You care about build speed and incremental builds.
- You are starting a new project or modernizing an existing one.

**Use kapt when:**
- A required library only offers a Java annotation processor and has no KSP artifact.
- You maintain a legacy project where migrating all processors is risky or not yet feasible.

**English Summary**: kapt bridges Java annotation processors into Kotlin but adds stub-generation overhead and weaker incrementality. KSP is Kotlin-first, usually faster, with growing ecosystem support. Prefer KSP whenever the libraries you use support it; keep kapt only for processors that have no KSP alternative.

---

## Ссылки (RU)
- [Документация KSP](https://kotlinlang.org/docs/ksp-overview.html)

## References

- [KSP Documentation](https://kotlinlang.org/docs/ksp-overview.html)

## Дополнительные вопросы (RU)

- [[q-fix-slow-app-startup-legacy--android--hard]]
- [[q-looper-thread-connection--android--medium]]
- [[q-macrobenchmark-startup--android--medium]]

## Follow-ups

- [[q-fix-slow-app-startup-legacy--android--hard]]
- [[q-looper-thread-connection--android--medium]]
- [[q-macrobenchmark-startup--android--medium]]

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-gradle]]

### Связанные (Medium)
- [[q-kapt-ksp-migration--android--medium]] - Миграция с kapt на KSP
- [[q-annotation-processing-android--android--medium]] - Аннотации в Android
- [[q-annotation-processing--android--medium]] - Annotation Processing
- [[q-build-optimization-gradle--android--medium]] - Оптимизация Gradle-сборки

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]

### Related (Medium)
- [[q-kapt-ksp-migration--android--medium]] - Kapt / KSP migration
- [[q-annotation-processing-android--android--medium]] - Annotations in Android
- [[q-annotation-processing--android--medium]] - Annotation Processing
- [[q-build-optimization-gradle--android--medium]] - Gradle build optimization
