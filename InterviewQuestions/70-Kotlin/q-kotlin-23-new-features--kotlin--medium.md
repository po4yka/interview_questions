---
anki_cards:
- slug: q-kotlin-23-new-features--kotlin--medium-0-en
  language: en
  anki_id: 1769173374934
  synced_at: '2026-01-23T17:03:50.424921'
- slug: q-kotlin-23-new-features--kotlin--medium-0-ru
  language: ru
  anki_id: 1769173374959
  synced_at: '2026-01-23T17:03:50.427255'
---
# Вопрос (RU)
> Какие новые функции появились в Kotlin 2.3? Перечислите основные улучшения и дополнения.

# Question (EN)
> What are the new features in Kotlin 2.3? Summarize the main improvements and additions.

## Ответ (RU)

**Kotlin 2.3.0 выпущен в декабре 2025**

Kotlin 2.3 содержит множество улучшений стандартной библиотеки, инструментов и совместимости. Вот основные нововведения.

---

### Стандартная библиотека

**1. UUID улучшения:**

```kotlin
import kotlin.uuid.Uuid

// UUID v7 (time-ordered) теперь стабилен
val timeBasedUuid = Uuid.random()  // v4 по умолчанию

// Парсинг с валидацией
val parsed = Uuid.parseOrNull("invalid")  // null вместо исключения

// Сравнение UUID
val uuid1 = Uuid.random()
val uuid2 = Uuid.random()
println(uuid1 < uuid2)  // для v7 это хронологический порядок
```

**2. kotlin.time стабилен:**

```kotlin
import kotlin.time.*
import kotlin.time.Duration.Companion.seconds

// Измерение времени
val elapsed = measureTime {
    performOperation()
}

// TimeSource для тестирования
val testTimeSource = TestTimeSource()
val mark = testTimeSource.markNow()
testTimeSource += 5.seconds
println(mark.elapsedNow())  // 5s
```

**3. Unused Return Value Checker:**

```kotlin
fun compute(): Int = 42

fun process() {
    compute()  // Warning: unused return value
}

// Явное игнорирование
fun processExplicit() {
    val _ = compute()  // OK, явно проигнорировано
}
```

---

### K2 Compiler улучшения

**Производительность:**
- Быстрее инкрементальная компиляция
- Улучшенный анализ smart casts
- Оптимизация памяти

**Диагностика:**
- Более точные сообщения об ошибках
- Лучшие подсказки для исправления
- Улучшенные warnings

---

### Kotlin/Native

**Swift Export улучшения:**

```kotlin
// Kotlin
@ObjCName("KotlinUser")
data class User(val name: String, val age: Int)

// Автоматически генерируется Swift-совместимый код
// с правильными типами и именованием
```

**Улучшения:**
- Лучшая совместимость типов с Swift
- Автоматическая генерация bridging headers
- Поддержка Swift async/await

---

### Kotlin/Wasm

**WebAssembly Component Model (preview):**

```kotlin
// Kotlin/Wasm теперь поддерживает Component Model
@WasmExport
fun greet(name: String): String {
    return "Hello, $name!"
}
```

**Улучшения:**
- Меньший размер бинарников
- Лучшая интеграция с JavaScript
- Поддержка WASI preview2

---

### Gradle интеграция

**Gradle 9.0 совместимость:**

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "2.3.0"
}

kotlin {
    jvmToolchain(25)  // Java 25 поддержка
}
```

**Configuration Cache полностью поддерживается**

---

### Compose Compiler

**Улучшения:**
- Более быстрая компиляция
- Лучшая стабильность детекции
- Улучшенные skip оптимизации

```kotlin
// Compose Compiler теперь часть Kotlin репозитория
plugins {
    id("org.jetbrains.kotlin.plugin.compose") version "2.3.0"
}
```

---

### Другие улучшения

**1. Explicit API mode улучшения:**

```kotlin
// build.gradle.kts
kotlin {
    explicitApi()  // требует явных модификаторов видимости
}

// Все public API должны иметь явные типы
public fun calculate(): Int = 42  // OK
fun calculate() = 42  // Warning: no explicit visibility
```

**2. Улучшенная Java interop:**

- Поддержка Java 25 features
- Лучшая nullability inference
- Улучшенный SAM conversion

**3. Multiplatform:**

```kotlin
// Улучшенная поддержка expect/actual
expect class PlatformLogger {
    fun log(message: String)
}

// actual реализации теперь проще проверяются компилятором
```

---

### Миграция

**От 2.2 к 2.3:**

1. Обновить версию плагина:
```kotlin
plugins {
    kotlin("jvm") version "2.3.0"
}
```

2. Проверить deprecated API:
```bash
./gradlew compileKotlin --warning-mode all
```

3. Включить новые оптимизации:
```kotlin
kotlin {
    compilerOptions {
        progressiveMode.set(true)
    }
}
```

---

### Сводка изменений

| Область | Изменение |
|---------|-----------|
| stdlib | UUID v7, kotlin.time stable |
| K2 | Производительность, диагностика |
| Native | Swift export, async support |
| Wasm | Component Model preview |
| Gradle | 9.0 support, Java 25 |
| Compose | Faster compilation |

---

## Answer (EN)

**Kotlin 2.3.0 released December 2025**

Kotlin 2.3 contains numerous improvements to the standard library, tooling, and compatibility. Here are the main additions.

---

### Standard Library

**1. UUID Improvements:**

```kotlin
import kotlin.uuid.Uuid

// UUID v7 (time-ordered) now stable
val timeBasedUuid = Uuid.random()  // v4 by default

// Parsing with validation
val parsed = Uuid.parseOrNull("invalid")  // null instead of exception

// UUID comparison
val uuid1 = Uuid.random()
val uuid2 = Uuid.random()
println(uuid1 < uuid2)  // for v7 this is chronological order
```

**2. kotlin.time Stable:**

```kotlin
import kotlin.time.*
import kotlin.time.Duration.Companion.seconds

// Time measurement
val elapsed = measureTime {
    performOperation()
}

// TimeSource for testing
val testTimeSource = TestTimeSource()
val mark = testTimeSource.markNow()
testTimeSource += 5.seconds
println(mark.elapsedNow())  // 5s
```

**3. Unused Return Value Checker:**

```kotlin
fun compute(): Int = 42

fun process() {
    compute()  // Warning: unused return value
}

// Explicit ignore
fun processExplicit() {
    val _ = compute()  // OK, explicitly ignored
}
```

---

### K2 Compiler Improvements

**Performance:**
- Faster incremental compilation
- Improved smart cast analysis
- Memory optimization

**Diagnostics:**
- More precise error messages
- Better fix suggestions
- Improved warnings

---

### Kotlin/Native

**Swift Export Improvements:**

```kotlin
// Kotlin
@ObjCName("KotlinUser")
data class User(val name: String, val age: Int)

// Automatically generates Swift-compatible code
// with correct types and naming
```

**Improvements:**
- Better type compatibility with Swift
- Automatic bridging header generation
- Swift async/await support

---

### Kotlin/Wasm

**WebAssembly Component Model (preview):**

```kotlin
// Kotlin/Wasm now supports Component Model
@WasmExport
fun greet(name: String): String {
    return "Hello, $name!"
}
```

**Improvements:**
- Smaller binary size
- Better JavaScript integration
- WASI preview2 support

---

### Gradle Integration

**Gradle 9.0 Compatibility:**

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm") version "2.3.0"
}

kotlin {
    jvmToolchain(25)  // Java 25 support
}
```

**Configuration Cache fully supported**

---

### Compose Compiler

**Improvements:**
- Faster compilation
- Better stability detection
- Improved skip optimizations

```kotlin
// Compose Compiler is now part of Kotlin repository
plugins {
    id("org.jetbrains.kotlin.plugin.compose") version "2.3.0"
}
```

---

### Other Improvements

**1. Explicit API Mode Improvements:**

```kotlin
// build.gradle.kts
kotlin {
    explicitApi()  // requires explicit visibility modifiers
}

// All public API must have explicit types
public fun calculate(): Int = 42  // OK
fun calculate() = 42  // Warning: no explicit visibility
```

**2. Improved Java Interop:**

- Java 25 features support
- Better nullability inference
- Improved SAM conversion

**3. Multiplatform:**

```kotlin
// Improved expect/actual support
expect class PlatformLogger {
    fun log(message: String)
}

// actual implementations are now easier for compiler to verify
```

---

### Migration

**From 2.2 to 2.3:**

1. Update plugin version:
```kotlin
plugins {
    kotlin("jvm") version "2.3.0"
}
```

2. Check deprecated API:
```bash
./gradlew compileKotlin --warning-mode all
```

3. Enable new optimizations:
```kotlin
kotlin {
    compilerOptions {
        progressiveMode.set(true)
    }
}
```

---

### Summary of Changes

| Area | Change |
|------|--------|
| stdlib | UUID v7, kotlin.time stable |
| K2 | Performance, diagnostics |
| Native | Swift export, async support |
| Wasm | Component Model preview |
| Gradle | 9.0 support, Java 25 |
| Compose | Faster compilation |

---

## Follow-ups

- What breaking changes are in Kotlin 2.3?
- How does the new Swift export compare to the old approach?
- What is the WebAssembly Component Model?

## Related Questions

- [[q-kotlin-2-k2-compiler--kotlin--medium]]
- [[q-uuid-api-kotlin--kotlin--medium]]
- [[q-time-tracking-kotlin--kotlin--medium]]

## References

- https://blog.jetbrains.com/kotlin/2025/12/kotlin-2-3-0-released/
- https://kotlinlang.org/docs/whatsnew23.html
- https://kotlinlang.org/docs/roadmap.html
