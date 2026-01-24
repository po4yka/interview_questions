---
id: kotlin-257
title: Kotlin/JS Interop / Kotlin/JS взаимодействие
aliases:
- Kotlin JS
- JavaScript Interop
- Kotlin JS взаимодействие
topic: kotlin
subtopics:
- kotlin-js
- interop
- multiplatform
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
- c-multiplatform
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- kotlin-js
- javascript
- interop
- difficulty/medium
anki_cards:
- slug: kotlin-257-0-en
  language: en
  anki_id: 1769170344046
  synced_at: '2026-01-23T17:03:51.518051'
- slug: kotlin-257-0-ru
  language: ru
  anki_id: 1769170344071
  synced_at: '2026-01-23T17:03:51.518934'
---
# Вопрос (RU)
> Как работает Kotlin/JS? Как взаимодействовать с JavaScript кодом из Kotlin?

# Question (EN)
> How does Kotlin/JS work? How do you interact with JavaScript code from Kotlin?

---

## Ответ (RU)

**Kotlin/JS** компилирует Kotlin код в JavaScript, позволяя использовать Kotlin для браузера и Node.js.

**Настройка проекта:**
```kotlin
// build.gradle.kts
plugins {
    kotlin("multiplatform") version "1.9.0"
}

kotlin {
    js(IR) {  // IR - новый компилятор
        browser {
            binaries.executable()
        }
        // или nodejs()
    }
}
```

**external - объявление JS типов:**
```kotlin
// Объявление внешней JS функции
external fun alert(message: String)

// Внешний класс
external class Date {
    constructor()
    constructor(milliseconds: Number)
    fun getFullYear(): Int
    fun getMonth(): Int
}

// Использование
fun main() {
    alert("Hello from Kotlin!")
    val date = Date()
    println("Year: ${date.getFullYear()}")
}
```

**dynamic тип - обход типизации:**
```kotlin
// dynamic отключает проверку типов
fun useJsLibrary() {
    val obj: dynamic = js("{}")
    obj.name = "Kotlin"
    obj.greet = { println("Hello!") }
    obj.greet()
}

// Доступ к глобальным объектам
val window: dynamic = js("window")
window.location.href = "https://example.com"
```

**@JsModule - импорт npm пакетов:**
```kotlin
@JsModule("lodash")
@JsNonModule
external fun <T> chunk(array: Array<T>, size: Int): Array<Array<T>>

// Использование
val result = chunk(arrayOf(1, 2, 3, 4), 2)
// [[1, 2], [3, 4]]
```

**@JsExport - экспорт для JS:**
```kotlin
@JsExport
class Calculator {
    fun add(a: Int, b: Int) = a + b
}

// В JS:
// const calc = new Calculator();
// calc.add(2, 3);
```

**Корутины в браузере:**
```kotlin
import kotlinx.coroutines.*
import kotlinx.browser.window

fun main() {
    GlobalScope.launch {
        val response = window.fetch("https://api.example.com/data").await()
        val json = response.json().await()
        console.log(json)
    }
}
```

**Dukat - генерация типов из TypeScript:**
```bash
# Генерация Kotlin деклараций из .d.ts
./gradlew generateExternals
```

## Answer (EN)

**Kotlin/JS** compiles Kotlin code to JavaScript, enabling Kotlin for browser and Node.js.

**Project Setup:**
```kotlin
// build.gradle.kts
plugins {
    kotlin("multiplatform") version "1.9.0"
}

kotlin {
    js(IR) {  // IR - new compiler
        browser {
            binaries.executable()
        }
        // or nodejs()
    }
}
```

**external - Declaring JS Types:**
```kotlin
// Declare external JS function
external fun alert(message: String)

// External class
external class Date {
    constructor()
    constructor(milliseconds: Number)
    fun getFullYear(): Int
    fun getMonth(): Int
}

// Usage
fun main() {
    alert("Hello from Kotlin!")
    val date = Date()
    println("Year: ${date.getFullYear()}")
}
```

**dynamic Type - Bypassing Type Checking:**
```kotlin
// dynamic disables type checking
fun useJsLibrary() {
    val obj: dynamic = js("{}")
    obj.name = "Kotlin"
    obj.greet = { println("Hello!") }
    obj.greet()
}

// Access global objects
val window: dynamic = js("window")
window.location.href = "https://example.com"
```

**@JsModule - Importing npm Packages:**
```kotlin
@JsModule("lodash")
@JsNonModule
external fun <T> chunk(array: Array<T>, size: Int): Array<Array<T>>

// Usage
val result = chunk(arrayOf(1, 2, 3, 4), 2)
// [[1, 2], [3, 4]]
```

**@JsExport - Exporting to JS:**
```kotlin
@JsExport
class Calculator {
    fun add(a: Int, b: Int) = a + b
}

// In JS:
// const calc = new Calculator();
// calc.add(2, 3);
```

**Coroutines in Browser:**
```kotlin
import kotlinx.coroutines.*
import kotlinx.browser.window

fun main() {
    GlobalScope.launch {
        val response = window.fetch("https://api.example.com/data").await()
        val json = response.json().await()
        console.log(json)
    }
}
```

**Dukat - Generating Types from TypeScript:**
```bash
# Generate Kotlin declarations from .d.ts
./gradlew generateExternals
```

---

## Follow-ups

- What is the difference between Kotlin/JS IR and legacy compiler?
- How do you handle null vs undefined in Kotlin/JS?
- How do you bundle Kotlin/JS with webpack?
