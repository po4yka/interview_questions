---
id: kotlin-247
title: KSP vs KAPT / KSP против KAPT
aliases:
- KSP vs KAPT
- Kotlin Symbol Processing
- KSP против KAPT
topic: kotlin
subtopics:
- annotation-processing
- build-tools
- ksp
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
- c-build-tools
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- ksp
- kapt
- annotation-processing
- difficulty/medium
anki_cards:
- slug: kotlin-247-0-en
  language: en
  anki_id: 1769170361346
  synced_at: '2026-01-23T17:03:51.695465'
- slug: kotlin-247-0-ru
  language: ru
  anki_id: 1769170361371
  synced_at: '2026-01-23T17:03:51.696223'
---
# Вопрос (RU)
> В чём разница между KSP и KAPT? Когда использовать каждый из них?

# Question (EN)
> What is the difference between KSP and KAPT? When should you use each?

---

## Ответ (RU)

**KAPT (Kotlin Annotation Processing Tool):**
Обёртка над Java Annotation Processing API. Генерирует Java stubs из Kotlin кода, затем запускает стандартные Java annotation processors.

**KSP (Kotlin Symbol Processing):**
Нативный API для обработки символов Kotlin. Работает напрямую с Kotlin компилятором без генерации Java stubs.

**Ключевые различия:**

| Аспект | KAPT | KSP |
|--------|------|-----|
| Скорость | Медленнее (генерирует stubs) | До 2x быстрее |
| Kotlin-специфичность | Теряет Kotlin-информацию | Сохраняет всю информацию |
| Инкрементальность | Ограниченная | Полная поддержка |
| Совместимость | Все Java AP | Требует KSP-версию |

**Пример конфигурации KSP:**
```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "1.9.0-1.0.13"
}

dependencies {
    // KSP вместо kapt
    ksp("com.google.dagger:hilt-compiler:2.48")
    // kapt("com.google.dagger:hilt-compiler:2.48") // старый способ
}
```

**Когда использовать:**
- **KSP**: Room, Hilt, Moshi (если поддерживается) - предпочтительный выбор
- **KAPT**: Только если библиотека не поддерживает KSP

**Миграция KAPT → KSP:**
```kotlin
// Замените в build.gradle.kts
// kapt("...") на ksp("...")
// id("kotlin-kapt") на id("com.google.devtools.ksp")
```

## Answer (EN)

**KAPT (Kotlin Annotation Processing Tool):**
A wrapper around Java Annotation Processing API. Generates Java stubs from Kotlin code, then runs standard Java annotation processors.

**KSP (Kotlin Symbol Processing):**
Native API for processing Kotlin symbols. Works directly with Kotlin compiler without generating Java stubs.

**Key Differences:**

| Aspect | KAPT | KSP |
|--------|------|-----|
| Speed | Slower (generates stubs) | Up to 2x faster |
| Kotlin-specific info | Loses Kotlin information | Preserves all info |
| Incremental | Limited support | Full support |
| Compatibility | All Java APs | Requires KSP version |

**KSP Configuration Example:**
```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "1.9.0-1.0.13"
}

dependencies {
    // KSP instead of kapt
    ksp("com.google.dagger:hilt-compiler:2.48")
    // kapt("com.google.dagger:hilt-compiler:2.48") // old way
}
```

**When to Use:**
- **KSP**: Room, Hilt, Moshi (if supported) - preferred choice
- **KAPT**: Only when library doesn't support KSP

**Migration KAPT → KSP:**
```kotlin
// Replace in build.gradle.kts
// kapt("...") with ksp("...")
// id("kotlin-kapt") with id("com.google.devtools.ksp")
```

---

## Follow-ups

- How do you write a custom KSP processor?
- What Kotlin-specific information does KSP preserve that KAPT loses?
- How does KSP handle incremental processing?
