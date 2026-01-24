---
id: kotlin-248
title: Kotlin 2.0 and K2 Compiler / Kotlin 2.0 и компилятор K2
aliases:
- Kotlin 2.0
- K2 Compiler
- Kotlin 2.0 и K2
topic: kotlin
subtopics:
- compiler
- kotlin-2
- language-evolution
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-compiler
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- k2-compiler
- kotlin-2
- difficulty/medium
anki_cards:
- slug: kotlin-248-0-en
  language: en
  anki_id: 1769170332346
  synced_at: '2026-01-23T17:03:51.311379'
- slug: kotlin-248-0-ru
  language: ru
  anki_id: 1769170332371
  synced_at: '2026-01-23T17:03:51.313980'
---
# Вопрос (RU)
> Что нового в Kotlin 2.0 и компиляторе K2? Какие основные улучшения?

# Question (EN)
> What's new in Kotlin 2.0 and K2 compiler? What are the main improvements?

---

## Ответ (RU)

**K2 - новый фронтенд компилятора Kotlin:**
Полностью переписанный компилятор с улучшенной архитектурой, производительностью и расширяемостью.

**Основные улучшения K2:**

| Аспект | Улучшение |
|--------|-----------|
| Скорость | До 2x быстрее компиляция |
| Smart casts | Более умный вывод типов |
| Архитектура | Унифицированная для всех платформ |
| Расширяемость | Лучшая поддержка плагинов |

**Новые возможности Kotlin 2.0:**

**1. Улучшенные Smart Casts:**
```kotlin
// K2 понимает более сложные условия
sealed class Result<T>
class Success<T>(val data: T) : Result<T>()
class Error(val message: String) : Result<Nothing>()

fun process(result: Result<String>) {
    if (result is Success) {
        // K2: result.data доступен напрямую
        println(result.data.length)
    }
}
```

**2. Context Receivers (стабильные):**
```kotlin
context(Logger, CoroutineScope)
fun performTask() {
    log("Starting task")  // из Logger
    launch { /* ... */ }  // из CoroutineScope
}
```

**3. Улучшенная диагностика ошибок:**
- Более точные сообщения об ошибках
- Лучшие подсказки для исправления

**Миграция на K2:**
```kotlin
// gradle.properties
kotlin.experimental.tryK2=true

// или в build.gradle.kts
kotlin {
    compilerOptions {
        languageVersion.set(KotlinVersion.KOTLIN_2_0)
    }
}
```

## Answer (EN)

**K2 - New Kotlin Compiler Frontend:**
Completely rewritten compiler with improved architecture, performance, and extensibility.

**Main K2 Improvements:**

| Aspect | Improvement |
|--------|-------------|
| Speed | Up to 2x faster compilation |
| Smart casts | Smarter type inference |
| Architecture | Unified for all platforms |
| Extensibility | Better plugin support |

**New Kotlin 2.0 Features:**

**1. Improved Smart Casts:**
```kotlin
// K2 understands more complex conditions
sealed class Result<T>
class Success<T>(val data: T) : Result<T>()
class Error(val message: String) : Result<Nothing>()

fun process(result: Result<String>) {
    if (result is Success) {
        // K2: result.data accessible directly
        println(result.data.length)
    }
}
```

**2. Context Receivers (stable):**
```kotlin
context(Logger, CoroutineScope)
fun performTask() {
    log("Starting task")  // from Logger
    launch { /* ... */ }  // from CoroutineScope
}
```

**3. Improved Error Diagnostics:**
- More precise error messages
- Better suggestions for fixes

**Migration to K2:**
```kotlin
// gradle.properties
kotlin.experimental.tryK2=true

// or in build.gradle.kts
kotlin {
    compilerOptions {
        languageVersion.set(KotlinVersion.KOTLIN_2_0)
    }
}
```

---

## Follow-ups

- How do context receivers differ from extension functions?
- What breaking changes exist when migrating to Kotlin 2.0?
- How does K2 improve Kotlin Multiplatform compilation?
