---
id: kotlin-227
title: Kotlin Contracts Smart Casts / Контракты и smart casts в Kotlin
aliases:
- Casts
- Contracts
- Kotlin
- Smart
topic: kotlin
subtopics:
- coroutines
- flow
- type-system
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
- q-coroutine-cancellation-cooperation--kotlin--medium
- q-flow-operators-deep-dive--kotlin--hard
created: 2025-10-15
updated: 2025-11-10
tags:
- difficulty/hard
anki_cards:
- slug: kotlin-227-0-en
  language: en
  anki_id: 1768326296331
  synced_at: '2026-01-23T17:03:51.716213'
- slug: kotlin-227-0-ru
  language: ru
  anki_id: 1768326296357
  synced_at: '2026-01-23T17:03:51.717098'
---
# Вопрос (RU)
> Что такое контракты Kotlin? Как они обеспечивают умные приведения типов (smart casts)? Реализуйте пользовательский контракт для функции валидации.

# Question (EN)
> What are Kotlin contracts? How do they enable smart casts? Implement a custom contract for a validation function.

## Ответ (RU)

**Контракты Kotlin** — это экспериментальная функциональность, позволяющая функциям явно описывать гарантии о своём поведении для компилятора. Это улучшает умные приведения типов, null-безопасность и даёт почву для некоторых оптимизаций.

---

### Что Такое Умные Приведения Типов?

Умные приведения позволяют компилятору автоматически использовать более конкретный тип, когда он может формально вывести безопасность такого приведения:

```kotlin
fun printLength(obj: Any) {
    if (obj is String) {
        // Smart cast к String
        println(obj.length)
    }
}

fun printUser(user: User?) {
    if (user != null) {
        // Smart cast к User (non-null)
        println(user.name)
    }
}
```

---

### Проблема Без Контрактов

Пользовательские функции валидации по умолчанию не обеспечивают умные приведения — компилятор не знает, какие гарантии они дают:

```kotlin
fun isNotNull(value: Any?): Boolean {
    return value != null
}

fun example(name: String?) {
    if (isNotNull(name)) {
        // Smart cast невозможен: компилятор не знает гарантий isNotNull
        println(name.length) // Ошибка: только безопасные вызовы
    }
}
```

---

### Решение: Контракты

Контракты сообщают компилятору о гарантиях функции через блок `contract { ... }`:

```kotlin
import kotlin.contracts.*

@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null
}

fun example(name: String?) {
    if (isNotNull(name)) {
        // Smart cast на основе контракта
        println(name.length)
    }
}
```

---

### Типы Контрактов

1. `returns(value) implies (condition)` — гарантирует, что `condition == true`, если функция вернула указанное значение.

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValid(user: User?): Boolean {
    contract {
        returns(true) implies (user != null)
    }
    return user != null && user.isActive
}

fun process(user: User?) {
    if (isValid(user)) {
        // user smart-cast к User (non-null)
        println(user.name)
    }
}
```

1. `returns() implies (condition)` — гарантирует условие при нормальном возврате (без исключений).

```kotlin
@OptIn(ExperimentalContracts::class)
fun requireNotNull(value: Any?) {
    contract {
        returns() implies (value != null)
    }
    if (value == null) {
        throw IllegalArgumentException("Value must not be null")
    }
}

fun example(name: String?) {
    requireNotNull(name)
    // После этого name smart-cast к не-null String
    println(name.length)
}
```

1. `returnsNotNull()` — гарантирует, что возвращаемое значение самой функции не равно `null`.

```kotlin
@OptIn(ExperimentalContracts::class)
fun String?.ifNotEmpty(): String? {
    contract {
        returnsNotNull()
    }
    return if (this != null && this.isNotEmpty()) this else null
}

fun example(text: String?) {
    val result = text.ifNotEmpty()
    if (result != null) {
        // result smart-cast к String, так как мы явно проверили его на null
        println(result.length)
    }
}
```

1. `callsInPlace(lambda, InvocationKind)` — описывает количество вызовов лямбды-аргумента.

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun <T> myRun(block: () -> T): T {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block()
}

fun example() {
    val name: String

    myRun {
        name = "John" // Компилятор знает, что лямбда вызовется ровно один раз
    }

    println(name)
}
```

---

### Параметры InvocationKind

```kotlin
// Вызывается ровно один раз
callsInPlace(block, InvocationKind.EXACTLY_ONCE)

// Вызывается не более одного раза (0 или 1)
callsInPlace(block, InvocationKind.AT_MOST_ONCE)

// Вызывается как минимум один раз (1+)
callsInPlace(block, InvocationKind.AT_LEAST_ONCE)

// Неизвестное количество вызовов
callsInPlace(block, InvocationKind.UNKNOWN)
```

---

### Контракты В Стандартной Библиотеке

(упрощённые схемы; реальные реализации и сигнатуры в stdlib используют контракты похожим образом, но могут отличаться по деталям.)

**`require` и `check`:**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun require(value: Boolean) {
    contract {
        returns() implies value
    }
    if (!value) {
        throw IllegalArgumentException("Failed requirement.")
    }
}

fun divide(a: Int, b: Int): Int {
    require(b != 0) // После этого компилятор знает, что b != 0
    return a / b
}
```

**`isNullOrEmpty`:**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun CharSequence?.isNullOrEmpty(): Boolean {
    contract {
        returns(false) implies (this@isNullOrEmpty != null)
    }
    return this == null || this.isEmpty()
}

fun example(text: String?) {
    if (!text.isNullOrEmpty()) {
        // text smart-cast к String
        println(text.length)
    }
}
```

**`let` / `run` / `apply` / `also` (пример для `let`):**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun <T, R> T.let(block: (T) -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block(this)
}

fun example() {
    val name: String

    "John".let {
        name = it
    }

    println(name)
}
```

---

### Пользовательские Контракты Для Валидации

**Валидация email:**

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValidEmail(email: String?): Boolean {
    contract {
        returns(true) implies (email != null)
    }
    return email != null && email.matches(Regex("^[A-Za-z0-9+_.-]+@(.+)$"))
}

fun sendEmail(email: String?) {
    if (isValidEmail(email)) {
        // email smart-cast к не-null String
        println("Sending to ${email!!.lowercase()}")
    }
}
```

**Проверка диапазона:**

```kotlin
@OptIn(ExperimentalContracts::class)
fun isInRange(value: Int?, min: Int, max: Int): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null && value in min..max
}

fun processAge(age: Int?) {
    if (isInRange(age, 0, 120)) {
        // age smart-cast к не-null Int
        println("Valid age: $age")
    }
}
```

**Проверка коллекции:**

```kotlin
@OptIn(ExperimentalContracts::class)
fun <T> isNotNullOrEmpty(collection: Collection<T>?): Boolean {
    contract {
        returns(true) implies (collection != null)
    }
    return collection != null && collection.isNotEmpty()
}

fun processItems(items: List<String>?) {
    if (isNotNullOrEmpty(items)) {
        // items smart-cast к не-null List<String>
        items!!.forEach { println(it) }
    }
}
```

---

### Продвинутый Пример: Несколько Импликаций

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValidUser(user: User?, requireActive: Boolean): Boolean {
    contract {
        returns(true) implies (user != null)
    }
    return user != null && (!requireActive || user.isActive)
}
```

Здесь контракт гарантирует, что при `returns(true)` `user` не равен `null`. Дополнительные зависимости должны формулироваться только в допустимой форме.

---

### Реальный Пример: Валидация Формы

```kotlin
data class RegistrationForm(
    val email: String?,
    val password: String?,
    val age: Int?,
    val terms: Boolean
)

@OptIn(ExperimentalContracts::class)
fun isValidEmail(email: String?): Boolean {
    contract {
        returns(true) implies (email != null)
    }
    return email != null && email.contains("@")
}

@OptIn(ExperimentalContracts::class)
fun isValidPassword(password: String?): Boolean {
    contract {
        returns(true) implies (password != null)
    }
    return password != null && password.length >= 8
}

@OptIn(ExperimentalContracts::class)
fun isValidAge(age: Int?): Boolean {
    contract {
        returns(true) implies (age != null)
    }
    return age != null && age in 13..120
}

@OptIn(ExperimentalContracts::class)
fun isValidForm(form: RegistrationForm): Boolean {
    return isValidEmail(form.email) &&
        isValidPassword(form.password) &&
        isValidAge(form.age) &&
        form.terms
}

fun register(form: RegistrationForm) {
    if (isValidForm(form)) {
        val user = User(
            email = form.email!!,
            password = form.password!!,
            age = form.age!!
        )

        saveUser(user)
    } else {
        showError("Invalid form")
    }
}
```

---

### Контракт С `callsInPlace`

**Безопасная работа с ресурсами:**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun <T : AutoCloseable, R> T.safeUse(block: (T) -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return try {
        block(this)
    } finally {
        close()
    }
}

fun example() {
    val data: String

    FileInputStream("file.txt").safeUse { stream ->
        data = stream.readBytes().decodeToString()
    }

    println(data)
}
```

**Гарантия инициализации:**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun initialize(block: () -> Unit) {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    block()
}

fun example() {
    val name: String

    initialize {
        name = "John"
    }

    println(name)
}
```

---

### Ограничения

1. Вызов `contract { ... }` должен быть первым оператором в теле функции.

```kotlin
@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract { // Должен быть первым
        returns(true) implies (value != null)
    }
    println("Checking...")
    return value != null
}
```

1. Контракты не должны описывать поведение, которое функция не гарантирует. Они могут ссылаться на параметры / свойства, но не на произвольную недетерминированную логику.

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValid(value: Int?, threshold: Int): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null && value > threshold
}
```

1. Контракты не проверяются компилятором на корректность — ответственность на разработчике. Неправдивые ("лживые") контракты опасны и могут приводить к NPE и некорректному поведению.

```kotlin
// ПЛОХОЙ ПРИМЕР: контракт "лжёт"
@OptIn(ExperimentalContracts::class)
fun alwaysFalse(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return false
}

fun example(name: String?) {
    if (alwaysFalse(name)) {
        // Компилятор считает, что name не null на основании контракта
        println(name!!.length) // Возможен NPE из-за неверного контракта
    }
}
```

---

### Лучшие Практики

1. Используйте контракты только там, где это даёт реальную пользу (умные приведения, анализ инициализации, читабельность управления потоком).

```kotlin
@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null
}

@OptIn(ExperimentalContracts::class)
fun add(a: Int, b: Int): Int {
    // Контракт не нужен
    return a + b
}
```

1. Контракты должны быть правдивыми; "лживые" контракты ломают анализ и могут привести к ошибкам во время выполнения.

```kotlin
@OptIn(ExperimentalContracts::class)
fun isPositive(value: Int?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null && value > 0
}

@OptIn(ExperimentalContracts::class)
fun isPositiveBad(value: Int?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return true // Ложный контракт, опасен
}
```

1. Хорошие сценарии использования — функции валидации и вспомогательные функции управления потоком исполнения.

```kotlin
// Примеры хороших сценариев:
// - isNotNull(value)
// - isValidEmail(email)
// - isInRange(value, min, max)
// - require/check условий
```

---

## Answer (EN)

**Kotlin Contracts** are an experimental feature that let functions explicitly describe guarantees about their behavior to the compiler, enabling better smart casts, null-safety, and some optimizations.

---

### What Are Smart Casts?

Smart casts automatically use a more specific type when the compiler can prove type safety:

```kotlin
fun printLength(obj: Any) {
    if (obj is String) {
        // Smart cast to String
        println(obj.length)
    }
}

fun printUser(user: User?) {
    if (user != null) {
        // Smart cast to User (non-null)
        println(user.name)
    }
}
```

---

### Problem Without Contracts

Custom validation functions don't enable smart casts by default:

```kotlin
fun isNotNull(value: Any?): Boolean {
    return value != null
}

fun example(name: String?) {
    if (isNotNull(name)) {
        // Smart cast is impossible:
        // compiler doesn't know isNotNull guarantees non-null
        println(name.length) // Error: Only safe calls are allowed
    }
}
```

---

### Solution: Contracts

Contracts tell the compiler about guarantees via `contract { ... }` blocks:

```kotlin
import kotlin.contracts.*

@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null
}

fun example(name: String?) {
    if (isNotNull(name)) {
        // Smart cast works based on the contract
        println(name.length)
    }
}
```

---

### Contract Types

**1. `returns(value) implies (condition)`**

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValid(user: User?): Boolean {
    contract {
        returns(true) implies (user != null)
    }
    return user != null && user.isActive
}

fun process(user: User?) {
    if (isValid(user)) {
        // user is smart-cast to User (non-null)
        println(user.name)
    }
}
```

**2. `returns() implies (condition)`**

```kotlin
@OptIn(ExperimentalContracts::class)
fun requireNotNull(value: Any?) {
    contract {
        returns() implies (value != null)
    }
    if (value == null) {
        throw IllegalArgumentException("Value must not be null")
    }
}

fun example(name: String?) {
    requireNotNull(name)
    // After this point, name is smart-cast to non-null String
    println(name.length)
}
```

**3. `returnsNotNull()`**

```kotlin
@OptIn(ExperimentalContracts::class)
fun String?.ifNotEmpty(): String? {
    contract {
        returnsNotNull()
    }
    return if (this != null && this.isNotEmpty()) this else null
}

fun example(text: String?) {
    val result = text.ifNotEmpty()
    if (result != null) {
        // result is smart-cast to String because we explicitly checked it for null
        println(result.length)
    }
}
```

**4. `callsInPlace(lambda, InvocationKind)`**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun <T> myRun(block: () -> T): T {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block()
}

fun example() {
    val name: String

    myRun {
        name = "John" // Compiler knows 'name' is initialized exactly once
    }

    println(name)
}
```

---

### InvocationKind Options

```kotlin
// Called exactly once
callsInPlace(block, InvocationKind.EXACTLY_ONCE)

// Called at most once (0 or 1)
callsInPlace(block, InvocationKind.AT_MOST_ONCE)

// Called at least once (1+)
callsInPlace(block, InvocationKind.AT_LEAST_ONCE)

// Unknown number of calls
callsInPlace(block, InvocationKind.UNKNOWN)
```

---

### Standard Library Contracts

The following simplified examples mirror what the standard library achieves conceptually; real stdlib implementations and signatures use contracts in a similar but not necessarily identical way.

**`require` / `check`:**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun require(value: Boolean) {
    contract {
        returns() implies value
    }
    if (!value) {
        throw IllegalArgumentException("Failed requirement.")
    }
}

fun divide(a: Int, b: Int): Int {
    require(b != 0)
    // After this point the compiler knows that b != 0
    return a / b
}
```

**`isNullOrEmpty`:**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun CharSequence?.isNullOrEmpty(): Boolean {
    contract {
        returns(false) implies (this@isNullOrEmpty != null)
    }
    return this == null || this.isEmpty()
}

fun example(text: String?) {
    if (!text.isNullOrEmpty()) {
        // text is smart-cast to String
        println(text.length)
    }
}
```

**`let` / similar scope functions (example for `let`):**

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun <T, R> T.let(block: (T) -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block(this)
}

fun example() {
    val name: String

    "John".let {
        name = it
    }

    println(name)
}
```

---

### Custom Validation Contracts

These helpers declare that a `true` result means the argument is not null, enabling smart casts.

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValidEmail(email: String?): Boolean {
    contract {
        returns(true) implies (email != null)
    }
    return email != null && email.matches(Regex("^[A-Za-z0-9+_.-]+@(.+)$"))
}
```

```kotlin
@OptIn(ExperimentalContracts::class)
fun isInRange(value: Int?, min: Int, max: Int): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null && value in min..max
}
```

```kotlin
@OptIn(ExperimentalContracts::class)
fun <T> isNotNullOrEmpty(collection: Collection<T>?): Boolean {
    contract {
        returns(true) implies (collection != null)
    }
    return collection != null && collection.isNotEmpty()
}
```

---

### Advanced: Multiple Implications

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValidUser(user: User?, requireActive: Boolean): Boolean {
    contract {
        returns(true) implies (user != null)
    }
    return user != null && (!requireActive || user.isActive)
}
```

This contract tells the compiler that if the function returns `true`, `user` is non-null. Extra constraints like `requireActive` are encoded in the implementation.

---

### Real-World Example: Form Validation

```kotlin
data class RegistrationForm(
    val email: String?,
    val password: String?,
    val age: Int?,
    val terms: Boolean
)

@OptIn(ExperimentalContracts::class)
fun isValidEmail(email: String?): Boolean {
    contract {
        returns(true) implies (email != null)
    }
    return email != null && email.contains("@")
}

@OptIn(ExperimentalContracts::class)
fun isValidPassword(password: String?): Boolean {
    contract {
        returns(true) implies (password != null)
    }
    return password != null && password.length >= 8
}

@OptIn(ExperimentalContracts::class)
fun isValidAge(age: Int?): Boolean {
    contract {
        returns(true) implies (age != null)
    }
    return age != null && age in 13..120
}

@OptIn(ExperimentalContracts::class)
fun isValidForm(form: RegistrationForm): Boolean {
    return isValidEmail(form.email) &&
        isValidPassword(form.password) &&
        isValidAge(form.age) &&
        form.terms
}

fun register(form: RegistrationForm) {
    if (isValidForm(form)) {
        val user = User(
            email = form.email!!,
            password = form.password!!,
            age = form.age!!
        )

        saveUser(user)
    } else {
        showError("Invalid form")
    }
}
```

---

### Contract with `callsInPlace`

These examples show how contracts help with initialization and resource safety.

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun <T : AutoCloseable, R> T.safeUse(block: (T) -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return try {
        block(this)
    } finally {
        close()
    }
}

fun example() {
    val data: String

    FileInputStream("file.txt").safeUse { stream ->
        data = stream.readBytes().decodeToString()
    }

    println(data)
}
```

```kotlin
@OptIn(ExperimentalContracts::class)
inline fun initialize(block: () -> Unit) {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    block()
}

fun example() {
    val name: String

    initialize {
        name = "John"
    }

    println(name)
}
```

---

### Limitations

1. `contract { ... }` must be the first statement in the function body.

```kotlin
@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    println("Checking...")
    return value != null
}
```

1. Contracts must not describe behavior the function does not actually guarantee. They should be based on parameters / properties, not arbitrary nondeterministic logic.

```kotlin
@OptIn(ExperimentalContracts::class)
fun isValid(value: Int?, threshold: Int): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null && value > threshold
}
```

1. Contracts are not verified by the compiler; correctness is the developer's responsibility. Lying contracts are dangerous and can break type/flow analysis and lead to runtime issues such as NPE.

```kotlin
// BAD EXAMPLE: lying contract
@OptIn(ExperimentalContracts::class)
fun alwaysFalse(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return false
}

fun example(name: String?) {
    if (alwaysFalse(name)) {
        // Compiler assumes 'name' is non-null based on the contract
        println(name!!.length) // Potential NPE if the contract is wrong
    }
}
```

---

### Best Practices

- Use contracts only when they provide real benefits (smart casts, initialization analysis, clear control-flow helpers).

```kotlin
@OptIn(ExperimentalContracts::class)
fun isNotNull(value: Any?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null
}
```

```kotlin
@OptIn(ExperimentalContracts::class)
fun add(a: Int, b: Int): Int {
    return a + b // no contract needed
}
```

- Contracts must be truthful; lying contracts break analysis and can cause runtime errors.

```kotlin
@OptIn(ExperimentalContracts::class)
fun isPositive(value: Int?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return value != null && value > 0
}
```

```kotlin
@OptIn(ExperimentalContracts::class)
fun isPositiveBad(value: Int?): Boolean {
    contract {
        returns(true) implies (value != null)
    }
    return true // lying contract, unsafe
}
```

- Good usage scenarios: validation helpers and flow-control helpers (`isNotNull`, `isValidEmail`, `isInRange`, `require`/`check`, etc.).

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия контрактов Kotlin от подходов в Java (assertions, аннотации и т.п.)?
- В каких практических сценариях вы бы стали использовать контракты в продакшене?
- Какие типичные ошибки и подводные камни при использовании контрактов нужно учитывать?

## Follow-ups (EN)

- What are the key differences between Kotlin contracts and Java approaches (assertions, annotations, etc.)?
- When would you use contracts in real-world production code?
- What common mistakes and pitfalls should be considered when using contracts?

## References (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References (EN)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions (RU)

- [[q-coroutine-cancellation-cooperation--kotlin--medium]]
- [[q-flow-operators-deep-dive--kotlin--hard]]

## Related Questions (EN)

- [[q-coroutine-cancellation-cooperation--kotlin--medium]]
- [[q-flow-operators-deep-dive--kotlin--hard]]
