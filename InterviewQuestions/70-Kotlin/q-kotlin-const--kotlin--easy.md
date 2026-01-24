---
anki_cards:
- slug: q-kotlin-const--kotlin--easy-0-en
  language: en
  anki_id: 1768326289030
  synced_at: '2026-01-23T17:03:51.325776'
- slug: q-kotlin-const--kotlin--easy-0-ru
  language: ru
  anki_id: 1768326289055
  synced_at: '2026-01-23T17:03:51.327673'
---
# Question (EN)
> What is the `const` keyword in Kotlin?

## Ответ (RU)

Если значение свойства только для чтения известно во время компиляции и может быть выражено в виде допустимого константного выражения, пометьте его как **константу времени компиляции**, используя модификатор `const`. Такие свойства должны соответствовать следующим требованиям:

### Требования К `const`

1. **Являться свойством `val` верхнего уровня или членом `object`/`companion object`** — Константа должна быть объявлена на верхнем уровне файла, внутри `object` или внутри `companion object`. Нельзя использовать `const` с `var` или для локальных переменных внутри функций.
2. **Инициализироваться значением типа `String` или примитивного типа** — Только `String` или примитивные типы (`Int`, `Long`, `Float`, `Double`, `Boolean`, `Char`, `Byte`, `Short`). Инициализация должна быть константным выражением (литерал или выражение, составленное только из других `const`-значений и разрешённых операций), без вычислений времени выполнения. Нельзя использовать `const` для nullable-типов или пользовательских типов.
3. **Без пользовательского getter** — Свойство не может иметь пользовательский getter.

### Пример

```kotlin
// const на верхнем уровне
const val MAX_USERS = 100
const val API_KEY = "your-api-key-here"

class Configuration {
    companion object {
        // const в companion object
        const val TIMEOUT = 5000
        const val BASE_URL = "https://api.example.com"
    }
}

object AppConstants {
    // const в object
    const val VERSION = "1.0.0"
    const val DEBUG_MODE = true
}
```

### `const val` Vs `val`

Основные различия между `const val` и `val`:

```kotlin
// Константа времени компиляции — значение встраивается во время компиляции
const val COMPILE_TIME = 100

// Константа времени выполнения — значение вычисляется при инициализации во время выполнения
val RUNTIME = calculateValue()

class Example {
    companion object {
        const val CONST_VALUE = 42  // Встраивается везде, где используется
        val REGULAR_VALUE = 42      // Чтение значения через поле во время выполнения
    }
}
```

### Когда Использовать `const`

- **Значения конфигурации**, которые логически не меняются (API endpoints, таймауты и т.д.)
- **Магические числа**, которым нужны осмысленные имена
- **Строковые константы**, используемые во всем приложении
- Когда важно, чтобы значение было **доступно как compile-time constant** (например, для аннотаций или inlining в другом коде)

### Замечание О Производительности

Использование `const` приводит к встраиванию значения в байткод как литерала (inlining), что убирает обращение к полю. Это может немного упростить доступ, но не следует рассматривать `const` как средство значительного ускорения кода; его основное назначение — корректное отражение compile-time констант и соответствие требованиям к таким значениям (например, в аннотациях).

```kotlin
const val MAX_SIZE = 1000

fun checkSize(size: Int) {
    if (size > MAX_SIZE) {  // MAX_SIZE встраивается как литерал 1000
        throw IllegalArgumentException()
    }
}

// После компиляции фактически становится примерно:
// if (size > 1000) { ... }
```

**Краткое содержание**: Модификатор `const` помечает свойство `val` как константу времени компиляции. Оно может использоваться только для примитивных типов или `String`, должно быть верхнего уровня или в `object`/`companion object`, не может иметь пользовательский getter или зависимость от вычислений времени выполнения. Значение встраивается во время компиляции и может использоваться там, где требуется compile-time constant.

---

## Answer (EN)

If the value of a read-only property is known at compile time and can be expressed as a valid constant expression, you can mark it as a **compile-time constant** using the `const` modifier. Such properties must satisfy the following requirements:

### Requirements for `const`

1. **Must be a `val` at the top level or a member of an `object`/`companion object`** — The constant must be declared at the top level of a file, inside an `object`, or inside a `companion object`. You cannot use `const` with `var` or for local variables inside functions.
2. **Initialized with a value of type `String` or a primitive type** — Only `String` or primitive types (`Int`, `Long`, `Float`, `Double`, `Boolean`, `Char`, `Byte`, `Short`) are allowed. The initializer must be a constant expression (a literal or an expression composed only of other `const` values and allowed operations), without any runtime computation. You cannot use `const` with nullable types or custom types.
3. **No custom getter** — The property cannot have a custom getter.

### Example

```kotlin
// Top-level const
const val MAX_USERS = 100
const val API_KEY = "your-api-key-here"

class Configuration {
    companion object {
        // Const in companion object
        const val TIMEOUT = 5000
        const val BASE_URL = "https://api.example.com"
    }
}

object AppConstants {
    // Const in object
    const val VERSION = "1.0.0"
    const val DEBUG_MODE = true
}
```

### `const val` Vs `val`

The main differences between `const val` and `val`:

```kotlin
// Compile-time constant — value is inlined at compile time
const val COMPILE_TIME = 100

// Runtime constant — value is computed during initialization at runtime
val RUNTIME = calculateValue()

class Example {
    companion object {
        const val CONST_VALUE = 42  // Inlined everywhere it's used
        val REGULAR_VALUE = 42      // Accessed via a field at runtime
    }
}
```

### When to Use `const`

- **Configuration values** that are logically immutable (API endpoints, timeouts, etc.)
- **Magic numbers** that need meaningful names
- **`String` constants** used throughout the application
- When you need a value that is a **true compile-time constant** (e.g., for annotations or inlined usage in other code)

### Performance Note

Using `const` causes the value to be inlined as a literal in bytecode, removing the need for a field access. This can slightly simplify access, but it should not be treated as a major performance optimization. Its primary purpose is to represent proper compile-time constants and satisfy places that require such constants (such as annotation arguments).

```kotlin
const val MAX_SIZE = 1000

fun checkSize(size: Int) {
    if (size > MAX_SIZE) {  // MAX_SIZE is inlined as literal 1000
        throw IllegalArgumentException()
    }
}

// After compilation, this effectively becomes approximately:
// if (size > 1000) { ... }
```

**English Summary**: The `const` modifier marks a `val` property as a compile-time constant. It can only be used with primitive types or `String`, must be declared at the top level or in an `object`/`companion object`, cannot have a custom getter or runtime-dependent initializer, and its value is inlined at compile time so it can be used where a compile-time constant is required.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Properties - Kotlin Documentation](https://kotlinlang.org/docs/reference/properties.html)
- [[c-kotlin]]

## Related Questions
- [[q-kotlin-val-vs-var--kotlin--easy]]
- [[q-object-companion-object--kotlin--medium]]
