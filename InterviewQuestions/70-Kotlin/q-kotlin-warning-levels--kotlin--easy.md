---
anki_cards:
- slug: q-kotlin-warning-levels--kotlin--easy-0-en
  language: en
  anki_id: 1769173378562
  synced_at: '2026-01-23T17:03:50.546445'
- slug: q-kotlin-warning-levels--kotlin--easy-0-ru
  language: ru
  anki_id: 1769173378584
  synced_at: '2026-01-23T17:03:50.549854'
---
# Вопрос (RU)
> Объясните уровни предупреждений компилятора в Kotlin. Как настроить предупреждения и сделать их ошибками?

# Question (EN)
> Explain compiler warning levels in Kotlin. How do you configure warnings and treat them as errors?

## Ответ (RU)

**Улучшено в Kotlin 2.3**

Kotlin предоставляет гибкие настройки для управления предупреждениями компилятора. Можно повышать предупреждения до ошибок или подавлять их по необходимости.

---

### Основные флаги

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        // Все предупреждения как ошибки
        allWarningsAsErrors.set(true)

        // Конкретные флаги
        freeCompilerArgs.addAll(
            "-Werror",           // все warnings -> errors
            "-Wextra",           // дополнительные проверки
            "-Xjsr305=strict"    // строгая проверка nullability из Java
        )
    }
}
```

---

### Уровни предупреждений (Kotlin 2.3+)

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        // Установка уровня для конкретного предупреждения
        freeCompilerArgs.addAll(
            "-Xwarning-level=DEPRECATION:error",   // deprecation -> error
            "-Xwarning-level=UNCHECKED_CAST:warning", // остается warning
            "-Xwarning-level=UNUSED:ignore"        // игнорировать unused
        )
    }
}
```

---

### Подавление предупреждений

**В коде:**

```kotlin
@Suppress("UNCHECKED_CAST")
val list = items as List<String>

@Suppress("DEPRECATION")
fun useOldApi() {
    oldMethod()
}

@Suppress("UNUSED_PARAMETER")
fun callback(unused: String) {
    // параметр не используется намеренно
}
```

**На уровне файла:**

```kotlin
@file:Suppress("DEPRECATION", "UNCHECKED_CAST")

package com.example
```

**На уровне класса:**

```kotlin
@Suppress("DEPRECATION")
class LegacyAdapter {
    // весь класс использует deprecated API
}
```

---

### Распространенные предупреждения

| Предупреждение | Описание |
|----------------|----------|
| `DEPRECATION` | Использование deprecated API |
| `UNCHECKED_CAST` | Непроверяемое приведение типов |
| `UNUSED_PARAMETER` | Неиспользуемый параметр |
| `UNUSED_VARIABLE` | Неиспользуемая переменная |
| `REDUNDANT_NULLABLE` | Избыточный nullable тип |
| `NOTHING_TO_INLINE` | Inline функция без inline-операций |
| `EXPERIMENTAL_API_USAGE` | Использование экспериментального API |

---

### Progressive mode

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        progressiveMode.set(true)
    }
}
```

Progressive mode активирует:
- Новые проверки, которые станут ошибками в будущих версиях
- Более строгую типизацию
- Предупреждения о будущих несовместимостях

---

### Практические примеры

**Строгий режим для production:**

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        allWarningsAsErrors.set(true)
        progressiveMode.set(true)
        freeCompilerArgs.addAll(
            "-Xjsr305=strict",
            "-Xemit-jvm-type-annotations"
        )
    }
}
```

**Мягкий режим для разработки:**

```kotlin
// build.gradle.kts (development)
kotlin {
    compilerOptions {
        allWarningsAsErrors.set(false)
        freeCompilerArgs.addAll(
            "-Xwarning-level=DEPRECATION:warning",
            "-Xwarning-level=UNUSED:ignore"
        )
    }
}
```

**CI/CD конфигурация:**

```kotlin
// build.gradle.kts
val isCI = System.getenv("CI")?.toBoolean() ?: false

kotlin {
    compilerOptions {
        allWarningsAsErrors.set(isCI)
    }
}
```

---

### Lint интеграция

```kotlin
// Gradle task для проверки warnings
tasks.register("checkWarnings") {
    dependsOn("compileKotlin")
    doLast {
        // Компиляция пройдет с allWarningsAsErrors
    }
}
```

---

### Kotlin 2.3: Unused Return Value Checker

Новая проверка в Kotlin 2.3:

```kotlin
fun getValue(): Int = 42

fun process() {
    getValue()  // Warning: возвращаемое значение не используется
}

// Чтобы явно проигнорировать:
fun process() {
    @Suppress("UNUSED_EXPRESSION")
    getValue()
}
```

---

### Сравнение с Java

| Аспект | Java | Kotlin |
|--------|------|--------|
| Все warnings как errors | `-Werror` | `-Werror` или `allWarningsAsErrors` |
| Подавление | `@SuppressWarnings` | `@Suppress` |
| Уровни | `-Xlint:...` | `-Xwarning-level=...` |
| Progressive | Нет | Есть |

---

## Answer (EN)

**Enhanced in Kotlin 2.3**

Kotlin provides flexible settings for managing compiler warnings. You can promote warnings to errors or suppress them as needed.

---

### Core Flags

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        // All warnings as errors
        allWarningsAsErrors.set(true)

        // Specific flags
        freeCompilerArgs.addAll(
            "-Werror",           // all warnings -> errors
            "-Wextra",           // additional checks
            "-Xjsr305=strict"    // strict nullability checking from Java
        )
    }
}
```

---

### Warning Levels (Kotlin 2.3+)

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        // Set level for specific warning
        freeCompilerArgs.addAll(
            "-Xwarning-level=DEPRECATION:error",   // deprecation -> error
            "-Xwarning-level=UNCHECKED_CAST:warning", // stays warning
            "-Xwarning-level=UNUSED:ignore"        // ignore unused
        )
    }
}
```

---

### Suppressing Warnings

**In code:**

```kotlin
@Suppress("UNCHECKED_CAST")
val list = items as List<String>

@Suppress("DEPRECATION")
fun useOldApi() {
    oldMethod()
}

@Suppress("UNUSED_PARAMETER")
fun callback(unused: String) {
    // parameter intentionally unused
}
```

**At file level:**

```kotlin
@file:Suppress("DEPRECATION", "UNCHECKED_CAST")

package com.example
```

**At class level:**

```kotlin
@Suppress("DEPRECATION")
class LegacyAdapter {
    // entire class uses deprecated API
}
```

---

### Common Warnings

| Warning | Description |
|---------|-------------|
| `DEPRECATION` | Using deprecated API |
| `UNCHECKED_CAST` | Unchecked type cast |
| `UNUSED_PARAMETER` | Unused parameter |
| `UNUSED_VARIABLE` | Unused variable |
| `REDUNDANT_NULLABLE` | Redundant nullable type |
| `NOTHING_TO_INLINE` | Inline function with no inline operations |
| `EXPERIMENTAL_API_USAGE` | Using experimental API |

---

### Progressive Mode

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        progressiveMode.set(true)
    }
}
```

Progressive mode enables:
- New checks that will become errors in future versions
- Stricter type checking
- Warnings about future incompatibilities

---

### Practical Examples

**Strict Mode for Production:**

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        allWarningsAsErrors.set(true)
        progressiveMode.set(true)
        freeCompilerArgs.addAll(
            "-Xjsr305=strict",
            "-Xemit-jvm-type-annotations"
        )
    }
}
```

**Relaxed Mode for Development:**

```kotlin
// build.gradle.kts (development)
kotlin {
    compilerOptions {
        allWarningsAsErrors.set(false)
        freeCompilerArgs.addAll(
            "-Xwarning-level=DEPRECATION:warning",
            "-Xwarning-level=UNUSED:ignore"
        )
    }
}
```

**CI/CD Configuration:**

```kotlin
// build.gradle.kts
val isCI = System.getenv("CI")?.toBoolean() ?: false

kotlin {
    compilerOptions {
        allWarningsAsErrors.set(isCI)
    }
}
```

---

### Lint Integration

```kotlin
// Gradle task for checking warnings
tasks.register("checkWarnings") {
    dependsOn("compileKotlin")
    doLast {
        // Compilation will run with allWarningsAsErrors
    }
}
```

---

### Kotlin 2.3: Unused Return Value Checker

New check in Kotlin 2.3:

```kotlin
fun getValue(): Int = 42

fun process() {
    getValue()  // Warning: return value is unused
}

// To explicitly ignore:
fun process() {
    @Suppress("UNUSED_EXPRESSION")
    getValue()
}
```

---

### Comparison with Java

| Aspect | Java | Kotlin |
|--------|------|--------|
| All warnings as errors | `-Werror` | `-Werror` or `allWarningsAsErrors` |
| Suppression | `@SuppressWarnings` | `@Suppress` |
| Levels | `-Xlint:...` | `-Xwarning-level=...` |
| Progressive | No | Yes |

---

## Follow-ups

- How do you configure warnings differently for different source sets?
- What warnings are enabled in progressive mode?
- Can you create custom warning suppressions?

## Related Questions

- [[q-kotlin-java-interop--kotlin--medium]]

## References

- https://kotlinlang.org/docs/compiler-reference.html
- https://kotlinlang.org/docs/whatsnew23.html
