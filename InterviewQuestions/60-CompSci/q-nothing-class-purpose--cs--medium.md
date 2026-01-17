---
id: cs-033
title: Nothing Class Purpose / Назначение класса Nothing
aliases:
- Nothing Class
- Класс Nothing
topic: cs
subtopics:
- type-system
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-computer-science
- q-abstract-class-purpose--cs--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- control-flow
- difficulty/medium
- exceptions
- kotlin
- type-system
- unreachable-code
sources:
- https://kotlinlang.org/docs/whatsnew15.html
anki_cards:
- slug: cs-033-0-en
  language: en
  anki_id: 1768455662644
  synced_at: '2026-01-15T09:43:17.122726'
- slug: cs-033-0-ru
  language: ru
  anki_id: 1768455662670
  synced_at: '2026-01-15T09:43:17.124362'
---
# Вопрос (RU)
> Зачем нужен класс `Nothing` в Kotlin? Какую роль он играет в системе типов?

# Question (EN)
> Why is the `Nothing` class needed in Kotlin? What role does it play in the type system?

---

## Ответ (RU)

**Теория Nothing Type:**
Nothing — тип без значений, который обозначает недостижимый код и операции, которые никогда не завершаются нормально. Nothing — bottom type в иерархии типов Kotlin, является подтипом всех типов. Используется для: анализа управляющего потока, смарт-кастов, оптимизаций и обнаружения недостижимого кода.

**Определение:**

*Теория:* Nothing — специальный тип, представляющий отсутствие возможных значений. Им помечают функции, которые не возвращают управление нормально: либо бросают исключение, либо выполняются бесконечно. Компилятор использует Nothing для вывода недостижимых путей выполнения. Как bottom type (подтип всего) он может подставляться там, где ожидается любой другой тип, что безопасно с точки зрения типов.

```kotlin
// ✅ Nothing для функций, которые никогда не возвращают
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}

// ✅ Компилятор знает: код после error недостижим
fun processValue(value: String?): String {
    val result = value ?: error("Value cannot be null")
    // result здесь гарантированно non-null (smart cast через Elvis + Nothing)
    return result.uppercase()
}

// ✅ Бесконечный цикл — никогда не возвращает
fun eventLoop(): Nothing {
    while (true) {
        handleEvent(waitForEvent())
    }
}
```

**Ключевое использование:**

**1. Static Code Analysis:**
*Теория:* Компилятор использует Nothing при анализе управляющего потока. Если ветка заканчивается вызовом функции с возвращаемым типом Nothing, он знает, что после неё выполнение не продолжается. Это позволяет:
- делать смарт-касты (после "фатальной" ветки переменная считается проверенной),
- выявлять недостижимый код,
- выполнять оптимизации.

```kotlin
// ✅ Smart cast через Nothing
fun validateString(value: String?): String {
    if (value == null) {
        throw IllegalArgumentException("Null value")  // тип результата ветки: Nothing
    }
    // value здесь smart cast к String
    return value.uppercase()  // Дополнительная проверка на null не нужна
}

// ✅ Аналогично для проверок
fun divide(a: Int, b: Int): Int {
    if (b == 0) {
        throw IllegalArgumentException("Cannot divide by zero")  // ветка с Nothing
    }
    // По анализу потока b != 0 в оставшемся коде
    return a / b
}
```

**2. Error Functions:**
*Теория:* Функции `error()` и `TODO()` возвращают Nothing, потому что всегда выбрасывают исключение и не завершаются нормально. Это позволяет компилятору считать код после них недостижимым и усиливает статический анализ.

```kotlin
// ✅ Standard library error() возвращает Nothing
fun require(condition: Boolean, message: () -> String) {
    if (!condition) {
        error(message())  // Never returns (Nothing)
    }
    // При true выполнение продолжается нормально
}

// ✅ Использование: smart cast после require
fun processUser(user: User?) {
    require(user != null) { "User cannot be null" }
    // Если мы здесь, условие true, user != null по анализу потока
    println(user!!.name)
}

// ✅ TODO() тоже возвращает Nothing
fun calculateTax(amount: Double): Double {
    TODO("Not implemented yet")
    // Код здесь недостижим
}

// ✅ Кастомный helper с Nothing на "ошибочном" пути
fun requireNonNull(value: String?): String {
    return value ?: throw IllegalArgumentException("Value is null")
    // throw имеет тип Nothing, поэтому выражение имеет тип String
}
```

**3. Type Hierarchy (Bottom Type):**
*Теория:* Nothing — bottom type в Kotlin: подтип всех типов. Это позволяет значениям типа Nothing (а фактически — отсутствию значения, например ветви с `throw` или вызовами `error/TODO`) подставляться туда, где ожидается любой другой тип. Это поддерживает безопасные generic-конструкции и выражения, которые "логически возвращают T", но фактически никогда не завершаются.

```kotlin
// ✅ Nothing как подтип любого типа
val stringOrNothing: String = TODO()       // TODO(): Nothing → совместимо с String
val intOrNothing: Int = error("Error")    // Nothing → Int
val anyTypeOrNothing: Any = TODO()         // Nothing → Any

// ✅ Generic-функция, которая "может вернуть T", но фактически всегда кидает
fun <T> fail(): T = throw Exception()

val str: String = fail()  // T выводится как String, тело: Nothing
val num: Int = fail()     // T выводится как Int

// ✅ Упрощённая иерархия
// Any (top type)
//   ↓
//  ... конкретные типы ...
//   ↓
// Nothing (bottom type — подтип всех)
```

**4. Nullable Nothing:**
*Теория:* `Nothing?` — тип, чьим единственным значением на нормально достижимых путях может быть `null`. Он полезен как результат, обозначающий "может быть только null или не завершиться". Также `List<Nothing>` используется стандартной библиотекой как тип пустых коллекций: так как значений Nothing не существует, такая коллекция не может содержать элементов.

```kotlin
// ✅ Nothing? может быть только null (при нормальном завершении)
val onlyNull: Nothing? = null

// ✅ Пустые коллекции
val emptyList: List<Nothing> = emptyList()
// Такая коллекция не может содержать элементов, т.к. нет значений типа Nothing

// ✅ Функция, которая либо возвращает null, либо не завершается
fun alwaysNull(): Nothing? = null

fun validateAndReturnNull(shouldThrow: Boolean): Nothing? {
    if (shouldThrow) {
        throw Exception()  // тип Nothing, совместим с Nothing?
    }
    return null            // единственное нормальное значение Nothing?
}
```

**Компоненты Nothing:**

**1. Unreachable Code Detection:**
*Теория:* Компилятор анализирует пути выполнения. Если путь оканчивается вызовом функции с возвращаемым типом Nothing, код после этого вызова считается недостижимым: возможны предупреждения, удаление недостижимых веток и более точные смарт-касты.

```kotlin
// ✅ Предупреждение о недостижимом коде
fun process() {
    if (someCondition) {
        return
    }
    error("Should not happen")  // Returns Nothing
    println("Unreachable")       // Может быть помечено как недостижимо
}

// ✅ Exhaustive when с использованием Nothing
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

fun <T> handleResult(result: Result<T>): T {
    return when (result) {
        is Result.Success -> result.data          // T
        is Result.Error -> error(result.message)  // Nothing совместим с T
    }
}
```

**2. Smart Casts:**
*Теория:* Смарт-касты основаны на анализе условий и недостижимых веток. Nothing помогает зафиксировать ветки, где выполнение не продолжается: если в ветке "ошибки" мы вызываем функцию, возвращающую Nothing, компилятор может считать остальные варианты безопасными и опускать лишние проверки.

```kotlin
// ✅ Smart cast через Nothing в Elvis-операторе
fun safeCast(obj: Any): String {
    return obj as? String ?: error("Not a string")
    // obj as? String → String?
    // error() → Nothing
    // String? ?: Nothing → String
}

// ✅ Null-check с использованием throw (Nothing)
fun processNonNull(value: String?): Int {
    val nonNull = value ?: throw IllegalArgumentException("Value is null")
    // nonNull здесь имеет тип String
    return nonNull.length
}

// ✅ require/check используют throw (Nothing) на ошибочном пути
fun <T> List<T>.getOrThrow(index: Int): T {
    require(index in indices) { "Index out of bounds" }
    // Если мы здесь, индекс валиден
    return this[index]
}
```

**Практические примеры:**

**1. Validation Helpers:**
*Теория:* Стандартные функции `require`, `check`, `assert` сами по себе имеют обычные возвращаемые типы (`Unit`), но в ветке нарушения условия они бросают исключение (то есть фактически возвращают Nothing и не продолжают выполнение). Это позволяет после успешного вызова использовать результаты проверок для смарт-кастов и безопасного кода без лишних null-check'ов.

```kotlin
// ✅ Preconditions
fun divide(a: Int, b: Int): Int {
    require(b != 0) { "Divisor cannot be zero" }
    // После успешного require по анализу потока b != 0
    return a / b
}

// ✅ Проверка и smart cast
fun processUser(user: User?) {
    check(user != null) { "User must not be null" }
    // Если мы здесь, user != null
    println(user!!.name)
}

// ✅ Assert в debug-сборках бросает при нарушении
fun calculate(value: Int): Int {
    val result = value * 2
    assert(result >= 0) { "Result should be positive" }
    return result
}
```

**2. Early Returns:**
*Теория:* Использование выражений с типом Nothing (броски исключений, `error`, `TODO`) в ветках валидации позволяет раннее завершение и делает оставшийся код безопасным и более читаемым.

```kotlin
// ✅ Ранний выход через исключение
fun findUser(id: Int): User {
    val user = database.findById(id) ?: throw NotFoundException("User not found")
    // user гарантированно non-null
    return user
}

// ✅ Проверки предусловий
fun processConfig(config: Config) {
    require(config.isValid()) { "Invalid configuration" }
    // Если мы здесь, конфиг валиден
    initializeWith(config)
}
```

**Nothing vs Unit vs Void:**

*Теория:* `Unit` — функция завершается успешно, но не возвращает полезного значения. `Nothing` — функция не завершается нормально (всегда бросает исключение или зависает). `void` в Java ближе к `Unit`: обозначает отсутствие возвращаемого значения, но не является bottom type. Nothing уникален тем, что одновременно обозначает недостижимый код и является bottom type, подтипом всех типов.

```kotlin
// ✅ Unit — успешно завершается, без значения
fun printMessage(msg: String): Unit {
    println(msg)
    // Возврат нормальный
}

// ✅ Nothing — никогда не возвращает
fun failWithMessage(msg: String): Nothing {
    throw Exception(msg)
    // Никогда не возвращает
}

// Сравнение:
// Unit: функция завершается, но без значения
// Nothing: функция не завершается нормально
// Void (Java): аналог Unit, не bottom type
```

## Answer (EN)

**Nothing Type Theory:**
Nothing is a type that has no values, represents unreachable code, and denotes operations that never complete normally. Nothing is the bottom type in Kotlin's type hierarchy and is a subtype of all types. It is used for control-flow analysis, smart casts, optimizations, and unreachable code detection.

**Definition:**

*Theory:* Nothing is a special type representing no possible value. It is used for functions that never return normally: they either throw an exception or run forever. The compiler uses Nothing to model unreachable code paths. As the bottom type (a subtype of everything), it can safely appear where any other type is expected.

```kotlin
// ✅ Nothing for functions that never return
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}

// ✅ Compiler knows: code after error is unreachable on that branch
fun processValue(value: String?): String {
    val result = value ?: error("Value cannot be null")
    // result is guaranteed non-null here (Elvis + Nothing)
    return result.uppercase()
}

// ✅ Infinite loop - never returns
fun eventLoop(): Nothing {
    while (true) {
        handleEvent(waitForEvent())
    }
}
```

**Key Uses:**

**1. Static Code Analysis:**
*Theory:* The compiler uses Nothing during control-flow analysis. If a branch ends with a call to a function returning Nothing, it knows execution does not continue past that point. This enables:
- smart casts (after a "fatal" branch, remaining paths are refined),
- unreachable code detection,
- optimizations.

```kotlin
// ✅ Smart cast via Nothing
fun validateString(value: String?): String {
    if (value == null) {
        throw IllegalArgumentException("Null value")  // branch has type Nothing
    }
    // value here smart-cast to String
    return value.uppercase()
}

// ✅ Similarly for other checks
fun divide(a: Int, b: Int): Int {
    if (b == 0) {
        throw IllegalArgumentException("Cannot divide by zero")  // Nothing branch
    }
    // By flow analysis, b != 0 here
    return a / b
}
```

**2. Error Functions:**
*Theory:* `error()` and `TODO()` return Nothing because they always throw exceptions and never complete normally. This lets the compiler treat code after them as unreachable and strengthens static analysis.

```kotlin
// ✅ Standard library error() returns Nothing
fun require(condition: Boolean, message: () -> String) {
    if (!condition) {
        error(message())  // Never returns (Nothing)
    }
    // When condition is true, execution continues normally
}

// ✅ Usage: smart cast after require
fun processUser(user: User?) {
    require(user != null) { "User cannot be null" }
    // If we're here, condition is true, so user != null by flow analysis
    println(user!!.name)
}

// ✅ TODO() also returns Nothing
fun calculateTax(amount: Double): Double {
    TODO("Not implemented yet")
    // Code here is unreachable
}

// ✅ Custom helper: Nothing on the failing path
fun requireNonNull(value: String?): String {
    return value ?: throw IllegalArgumentException("Value is null")
    // throw has type Nothing, so the whole expression has type String
}
```

**3. Type Hierarchy (Bottom Type):**
*Theory:* Nothing is the bottom type in Kotlin: it is a subtype of all types. That allows expressions of type Nothing (such as `throw` or calls to `error`/`TODO`) to be used wherever any other type is expected. This supports type safety in generic APIs and expressions that "conceptually return T" but never complete.

```kotlin
// ✅ Nothing as subtype of any type
val stringOrNothing: String = TODO()       // TODO(): Nothing → compatible with String
val intOrNothing: Int = error("Error")    // Nothing → Int
val anyTypeOrNothing: Any = TODO()         // Nothing → Any

// ✅ Generic function that "returns T" but actually never completes
fun <T> fail(): T = throw Exception()

val str: String = fail()  // T inferred as String, body is Nothing
val num: Int = fail()     // T inferred as Int

// ✅ Simplified hierarchy
// Any (top type)
//   ↓
//  ... concrete types ...
//   ↓
// Nothing (bottom type - subtype of all)
```

**4. Nullable Nothing:**
*Theory:* `Nothing?` is a type whose only normal value is `null`. A function of type `Nothing?` may either return `null` or never complete (throw / loop); `throw` expressions have type Nothing, which is compatible with Nothing?. `List<Nothing>` is used by the standard library as the type of empty collections: since there are no values of type Nothing, such a list cannot contain elements.

```kotlin
// ✅ Nothing? can only be null on normal completion
val onlyNull: Nothing? = null

// ✅ Empty collections
val emptyList: List<Nothing> = emptyList()
// This list cannot contain elements because there are no values of type Nothing

// ✅ Function that either returns null or does not complete
fun alwaysNull(): Nothing? = null

fun validateAndReturnNull(shouldThrow: Boolean): Nothing? {
    if (shouldThrow) {
        throw Exception()  // type Nothing, compatible with Nothing?
    }
    return null            // the only normal value of Nothing?
}
```

**Nothing Components:**

**1. Unreachable Code Detection:**
*Theory:* The compiler analyzes control flow. If a path ends with a function returning Nothing, code after that call is considered unreachable: it may emit warnings, remove unreachable branches, and apply more precise smart casts.

```kotlin
// ✅ Unreachable code warning
fun process() {
    if (someCondition) {
        return
    }
    error("Should not happen")  // Returns Nothing
    println("Unreachable")       // May be reported as unreachable
}

// ✅ Exhaustive when leveraging Nothing
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

fun <T> handleResult(result: Result<T>): T {
    return when (result) {
        is Result.Success -> result.data          // T
        is Result.Error -> error(result.message)  // Nothing is compatible with T
    }
}
```

**2. Smart Casts:**
*Theory:* Smart casts are based on control-flow analysis. Nothing marks paths where execution does not continue. If the "error" branch calls a Nothing-returning function, the remaining paths get refined types (e.g., non-null), eliminating the need for extra `!!` or `?.` checks.

```kotlin
// ✅ Smart cast via Nothing in Elvis
fun safeCast(obj: Any): String {
    return obj as? String ?: error("Not a string")
    // obj as? String → String?
    // error() → Nothing
    // String? ?: Nothing → String
}

// ✅ Null checks with throw (Nothing)
fun processNonNull(value: String?): Int {
    val nonNull = value ?: throw IllegalArgumentException("Value is null")
    // nonNull now has type String
    return nonNull.length
}

// ✅ require/check rely on throwing (Nothing) on the failing path
fun <T> List<T>.getOrThrow(index: Int): T {
    require(index in indices) { "Index out of bounds" }
    // If we're here, index is valid
    return this[index]
}
```

**Practical Examples:**

**1. Validation Helpers:**
*Theory:* Standard helpers `require`, `check`, and `assert` have regular return types (typically Unit) on success, but throw on failure; those throwing branches have type Nothing. This pattern, combined with control-flow analysis, enables type-safe validation without manual null checks.

```kotlin
// ✅ Preconditions
fun divide(a: Int, b: Int): Int {
    require(b != 0) { "Divisor cannot be zero" }
    // After a successful require, b != 0 by flow analysis
    return a / b
}

// ✅ Check condition
fun processUser(user: User?) {
    check(user != null) { "User must not be null" }
    // If we're here, user != null
    println(user!!.name)
}

// ✅ Assert in debug builds throws on violation
fun calculate(value: Int): Int {
    val result = value * 2
    assert(result >= 0) { "Result should be positive" }
    return result
}
```

**2. Early Returns:**
*Theory:* Using expressions of type Nothing (throws, `error`, `TODO`) in validation branches provides early exits and makes the remaining code safe and simpler.

```kotlin
// ✅ Early exit via exception
fun findUser(id: Int): User {
    val user = database.findById(id) ?: throw NotFoundException("User not found")
    // user is guaranteed non-null
    return user
}

// ✅ Precondition checks
fun processConfig(config: Config) {
    require(config.isValid()) { "Invalid configuration" }
    // If we're here, config is valid
    initializeWith(config)
}
```

**Nothing vs Unit vs Void:**

*Theory:* Unit means a function completes successfully but does not return a useful value. Nothing means a function never completes normally (it always throws or loops forever). Java's void is similar to Unit (no value) but is not a bottom type. Nothing is unique in that it both models unreachable code paths and is the bottom type, a subtype of all types.

```kotlin
// ✅ Unit - returns successfully, no value
fun printMessage(msg: String): Unit {
    println(msg)
    // Returns normally
}

// ✅ Nothing - never returns normally
fun failWithMessage(msg: String): Nothing {
    throw Exception(msg)
    // Never returns
}

// Comparison:
// Unit: function completes but has no value
// Nothing: function never completes normally
// Void (Java): similar to Unit, not a bottom type
```

---

## Дополнительные Вопросы (RU)

- В чем разница между `Nothing` и `Unit`?
- Как `Nothing` помогает реализовать smart cast в Kotlin?
- Когда стоит использовать `Nothing?` вместо `Nothing`?

## Follow-ups

- What is the difference between `Nothing` and `Unit`?
- How does `Nothing` enable smart casts in Kotlin?
- When should you use `Nothing?` instead of `Nothing`?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые понятия системы типов Kotlin
- Null-safety и smart cast'ы

### Связанные (тот Же уровень)
- Тип `Unit`
- Smart cast'ы и их использование
- Sealed-классы и исчерпывающие `when`

### Продвинутые (сложнее)
- Продвинутые концепции системы типов
- Обобщенное программирование с использованием `Nothing`
- Типобезопасные паттерны обработки ошибок

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin type system concepts
- Null safety and smart casts

### Related (Same Level)
- Unit type
- Smart casts
- Sealed classes and exhaustive `when`

### Advanced (Harder)
- Advanced type system concepts
- Generic programming with `Nothing`
- Type-safe error handling patterns

## References

- "Kotlin 1.5: What's new" - Kotlin documentation
