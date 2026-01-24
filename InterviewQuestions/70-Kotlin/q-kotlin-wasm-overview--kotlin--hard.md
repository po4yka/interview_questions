---
id: kotlin-258
title: Kotlin/Wasm Overview / Обзор Kotlin/Wasm
aliases:
- Kotlin Wasm
- WebAssembly Kotlin
- Kotlin Wasm обзор
topic: kotlin
subtopics:
- kotlin-wasm
- webassembly
- multiplatform
question_kind: theory
difficulty: hard
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
- wasm
- webassembly
- multiplatform
- difficulty/hard
anki_cards:
- slug: kotlin-258-0-en
  language: en
  anki_id: 1769170357896
  synced_at: '2026-01-23T17:03:51.662038'
- slug: kotlin-258-0-ru
  language: ru
  anki_id: 1769170357921
  synced_at: '2026-01-23T17:03:51.663062'
---
# Вопрос (RU)
> Что такое Kotlin/Wasm? Чем он отличается от Kotlin/JS?

# Question (EN)
> What is Kotlin/Wasm? How does it differ from Kotlin/JS?

---

## Ответ (RU)

**Kotlin/Wasm** компилирует Kotlin в WebAssembly - бинарный формат для выполнения в браузере с производительностью близкой к нативной.

**Сравнение с Kotlin/JS:**

| Аспект | Kotlin/JS | Kotlin/Wasm |
|--------|-----------|-------------|
| Целевой формат | JavaScript | WebAssembly binary |
| Производительность | Интерпретируется | Близка к нативной |
| Размер бандла | Больше | Меньше |
| JS Interop | Прямой | Через JS glue code |
| Зрелость | Стабильный | Alpha/Beta |
| GC | JS GC | WasmGC |

**Настройка проекта:**
```kotlin
// build.gradle.kts
plugins {
    kotlin("multiplatform") version "2.0.0"
}

kotlin {
    wasmJs {
        browser {
            binaries.executable()
        }
    }

    sourceSets {
        val wasmJsMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-browser:0.1")
            }
        }
    }
}
```

**Compose for Web с Wasm:**
```kotlin
// Compose Multiplatform для Wasm
import androidx.compose.ui.window.CanvasBasedWindow
import androidx.compose.material.Text
import androidx.compose.material.Button

fun main() {
    CanvasBasedWindow("My App") {
        var count by remember { mutableStateOf(0) }

        Column {
            Text("Count: $count")
            Button(onClick = { count++ }) {
                Text("Increment")
            }
        }
    }
}
```

**Взаимодействие с JavaScript:**
```kotlin
// Импорт JS функций
@JsFun("(x) => console.log(x)")
external fun consoleLog(message: JsAny)

// Использование DOM API
import org.w3c.dom.*

fun updateElement() {
    val element = document.getElementById("myElement")
    element?.textContent = "Updated from Kotlin/Wasm"
}
```

**Ограничения (на момент 2024):**
- Требует WasmGC (Chrome 119+, Firefox 120+)
- Reflection ограничен
- Некоторые stdlib функции недоступны
- Размер runtime

**Когда использовать:**
- **Kotlin/Wasm**: Compute-intensive приложения, игры, Compose UI
- **Kotlin/JS**: Legacy браузеры, тесная интеграция с JS экосистемой

## Answer (EN)

**Kotlin/Wasm** compiles Kotlin to WebAssembly - a binary format for browser execution with near-native performance.

**Comparison with Kotlin/JS:**

| Aspect | Kotlin/JS | Kotlin/Wasm |
|--------|-----------|-------------|
| Target format | JavaScript | WebAssembly binary |
| Performance | Interpreted | Near-native |
| Bundle size | Larger | Smaller |
| JS Interop | Direct | Via JS glue code |
| Maturity | Stable | Alpha/Beta |
| GC | JS GC | WasmGC |

**Project Setup:**
```kotlin
// build.gradle.kts
plugins {
    kotlin("multiplatform") version "2.0.0"
}

kotlin {
    wasmJs {
        browser {
            binaries.executable()
        }
    }

    sourceSets {
        val wasmJsMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-browser:0.1")
            }
        }
    }
}
```

**Compose for Web with Wasm:**
```kotlin
// Compose Multiplatform for Wasm
import androidx.compose.ui.window.CanvasBasedWindow
import androidx.compose.material.Text
import androidx.compose.material.Button

fun main() {
    CanvasBasedWindow("My App") {
        var count by remember { mutableStateOf(0) }

        Column {
            Text("Count: $count")
            Button(onClick = { count++ }) {
                Text("Increment")
            }
        }
    }
}
```

**JavaScript Interop:**
```kotlin
// Import JS functions
@JsFun("(x) => console.log(x)")
external fun consoleLog(message: JsAny)

// Using DOM API
import org.w3c.dom.*

fun updateElement() {
    val element = document.getElementById("myElement")
    element?.textContent = "Updated from Kotlin/Wasm"
}
```

**Limitations (as of 2024):**
- Requires WasmGC (Chrome 119+, Firefox 120+)
- Limited reflection
- Some stdlib functions unavailable
- Runtime size

**When to Use:**
- **Kotlin/Wasm**: Compute-intensive apps, games, Compose UI
- **Kotlin/JS**: Legacy browsers, tight JS ecosystem integration

---

## Follow-ups

- What is WasmGC and why does Kotlin/Wasm require it?
- How do you handle existing JS libraries in Kotlin/Wasm?
- What are the differences between wasmJs and wasmWasi targets?
