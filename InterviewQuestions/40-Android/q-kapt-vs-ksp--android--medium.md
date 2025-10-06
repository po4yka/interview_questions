---
id: 20251006-019
title: "kapt vs KSP comparison / Сравнение kapt и KSP"
aliases: []

# Classification
topic: android
subtopics: [annotation-processing, kapt, ksp, build-performance]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, annotation-processing, kapt, ksp, build-performance, difficulty/medium]
---

# Question (EN)
> What is the difference between kapt and KSP? Which one to use?

# Вопрос (RU)
> В чем разница между kapt и KSP? Какой использовать?

---

## Answer (EN)

**kapt** (Kotlin Annotation Processing Tool) runs Java annotation processors. **KSP** (Kotlin Symbol Processing) is Kotlin-first, up to 2x faster.

### Comparison

| Feature | kapt | KSP |
|---------|------|-----|
| **Speed** | Slower (generates Java stubs) | 2x faster |
| **Language** | Java-based | Kotlin-first |
| **API** | Java annotation processing | Kotlin Symbol Processing |
| **Libraries support** | All (Room, Dagger, Glide) | Growing (Room, Moshi, Hilt) |
| **Incremental** | Limited | Better |

### kapt Usage

```kotlin
// build.gradle.kts
plugins {
    id("kotlin-kapt")
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0")  // kapt
}
```

### KSP Usage

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    ksp("androidx.room:room-compiler:2.6.0")  // KSP
}
```

### Performance Difference

```
Build with kapt:    45 seconds
Build with KSP:     23 seconds  (2x faster!)
```

### Library Support

**KSP supported:**
- Room
- Moshi
- Hilt (since 2.44)

**kapt only:**
- Dagger 2 (without Hilt)
- Glide
- Some legacy libraries

### Migration from kapt to KSP

```kotlin
// Before (kapt)
plugins {
    id("kotlin-kapt")
}
dependencies {
    kapt("androidx.room:room-compiler:2.6.0")
}

// After (KSP)
plugins {
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
}
dependencies {
    ksp("androidx.room:room-compiler:2.6.0")
}
```

**Update paths:**

```kotlin
// Before
sourceSets.getByName("main") {
    java.srcDir("build/generated/source/kapt/main")
}

// After
kotlin.sourceSets.main {
    kotlin.srcDir("build/generated/ksp/main/kotlin")
}
```

### When to Use Each

**Use KSP when:**
- Library supports it (Room, Hilt, Moshi)
- Build speed matters
- New project

**Use kapt when:**
- Library doesn't support KSP yet
- Legacy project with dependencies on kapt

**English Summary**: kapt: Java-based, slower, works with all libraries. KSP: Kotlin-first, 2x faster, growing library support. Use KSP for Room, Hilt, Moshi. Use kapt for legacy libraries. Migration: replace `kapt()` with `ksp()`, update plugin.

## Ответ (RU)

**kapt** (Kotlin Annotation Processing Tool) запускает Java annotation processors. **KSP** (Kotlin Symbol Processing) ориентирован на Kotlin, до 2x быстрее.

### Сравнение

| Функция | kapt | KSP |
|---------|------|-----|
| **Скорость** | Медленнее (генерирует Java stubs) | 2x быстрее |
| **Язык** | На основе Java | Ориентирован на Kotlin |
| **Поддержка библиотек** | Все (Room, Dagger, Glide) | Растущая (Room, Moshi, Hilt) |
| **Инкрементальная** | Ограниченная | Лучше |

### Использование KSP

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
}

dependencies {
    implementation("androidx.room:room-runtime:2.6.0")
    ksp("androidx.room:room-compiler:2.6.0")  // KSP
}
```

### Разница в производительности

```
Сборка с kapt:    45 секунд
Сборка с KSP:     23 секунды  (2x быстрее!)
```

### Поддержка библиотек

**KSP поддерживается:**
- Room
- Moshi
- Hilt (с версии 2.44)

**Только kapt:**
- Dagger 2 (без Hilt)
- Glide
- Некоторые legacy библиотеки

### Когда использовать каждый

**Используйте KSP когда:**
- Библиотека поддерживает (Room, Hilt, Moshi)
- Важна скорость сборки
- Новый проект

**Используйте kapt когда:**
- Библиотека еще не поддерживает KSP
- Legacy проект с зависимостями от kapt

**Краткое содержание**: kapt: на основе Java, медленнее, работает со всеми библиотеками. KSP: ориентирован на Kotlin, 2x быстрее, растущая поддержка библиотек. Используйте KSP для Room, Hilt, Moshi. Используйте kapt для legacy библиотек. Миграция: заменить `kapt()` на `ksp()`, обновить плагин.

---

## References
- [KSP Documentation](https://kotlinlang.org/docs/ksp-overview.html)

## Related Questions
- [[q-annotation-processing--android--medium]]
