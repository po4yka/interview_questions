---
id: kotlin-255
title: Kotlin Script (.kts) / Kotlin скрипты (.kts)
aliases:
- Kotlin Script
- kts files
- Kotlin скрипты
topic: kotlin
subtopics:
- scripting
- build-tools
- gradle
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-scripting
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- kts
- scripting
- gradle
- difficulty/easy
anki_cards:
- slug: kotlin-255-0-en
  language: en
  anki_id: 1769170309697
  synced_at: '2026-01-23T17:03:50.785023'
- slug: kotlin-255-0-ru
  language: ru
  anki_id: 1769170309721
  synced_at: '2026-01-23T17:03:50.786164'
---
# Вопрос (RU)
> Что такое Kotlin Script (.kts)? Где он используется?

# Question (EN)
> What is Kotlin Script (.kts)? Where is it used?

---

## Ответ (RU)

**Kotlin Script (.kts)** - файлы Kotlin, которые выполняются как скрипты без явной компиляции и функции main().

**Основные применения:**

**1. Gradle Kotlin DSL:**
```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "1.9.0"
    application
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.0")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("MainKt")
}
```

**2. Standalone скрипты:**
```kotlin
// script.main.kts
@file:DependsOn("com.squareup.okhttp3:okhttp:4.10.0")

import okhttp3.OkHttpClient
import okhttp3.Request

val client = OkHttpClient()
val request = Request.Builder()
    .url("https://api.github.com")
    .build()

val response = client.newCall(request).execute()
println(response.body?.string())
```

**Запуск скрипта:**
```bash
# Через kotlinc
kotlinc -script script.main.kts

# Или сделать исполняемым
#!/usr/bin/env kotlin
println("Hello from script!")
```

**3. settings.gradle.kts:**
```kotlin
// settings.gradle.kts
rootProject.name = "my-project"

include(":app")
include(":core")

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}
```

**Преимущества Kotlin DSL над Groovy:**
- Автодополнение в IDE
- Compile-time проверка типов
- Рефакторинг
- Единый язык для проекта

**Аннотации для скриптов:**
```kotlin
@file:DependsOn("library:artifact:version")  // Зависимости
@file:Import("other-script.kts")              // Импорт скриптов
@file:CompilerOptions("-jvm-target", "17")    // Опции компилятора
```

## Answer (EN)

**Kotlin Script (.kts)** - Kotlin files that execute as scripts without explicit compilation and main() function.

**Main Use Cases:**

**1. Gradle Kotlin DSL:**
```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "1.9.0"
    application
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.0")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("MainKt")
}
```

**2. Standalone Scripts:**
```kotlin
// script.main.kts
@file:DependsOn("com.squareup.okhttp3:okhttp:4.10.0")

import okhttp3.OkHttpClient
import okhttp3.Request

val client = OkHttpClient()
val request = Request.Builder()
    .url("https://api.github.com")
    .build()

val response = client.newCall(request).execute()
println(response.body?.string())
```

**Running Scripts:**
```bash
# Via kotlinc
kotlinc -script script.main.kts

# Or make executable
#!/usr/bin/env kotlin
println("Hello from script!")
```

**3. settings.gradle.kts:**
```kotlin
// settings.gradle.kts
rootProject.name = "my-project"

include(":app")
include(":core")

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}
```

**Kotlin DSL Advantages over Groovy:**
- IDE auto-completion
- Compile-time type checking
- Refactoring support
- Single language for project

**Script Annotations:**
```kotlin
@file:DependsOn("library:artifact:version")  // Dependencies
@file:Import("other-script.kts")              // Import scripts
@file:CompilerOptions("-jvm-target", "17")    // Compiler options
```

---

## Follow-ups

- How do you cache dependencies in Kotlin scripts?
- What is the difference between .kts and .main.kts?
- How do you debug Kotlin scripts?
