---
id: kotlin-154
title: "Inline Function Limitations / Ограничения inline функций"
aliases: [Inline function restrictions Kotlin, Kotlin inline function limitations, Ограничения inline функций Kotlin]
topic: kotlin
subtopics: [coroutines, delegation, flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-coroutine-context-elements--kotlin--hard, q-testing-stateflow-sharedflow--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium]
---
# Вопрос (RU)
> Когда нельзя или нежелательно использовать inline-функции в Kotlin, и какие ограничения при этом действуют?

# Question (EN)
> When can't or shouldn't you use inline functions in Kotlin, and what limitations apply?

## Ответ (RU)

Хотя `inline` функции могут улучшать производительность (особенно для небольших higher-order функций), есть случаи, когда их использование невозможно, ограничено или нежелательно.

### 1. Нельзя Сохранять Лямбду В Переменную (без `noinline`)

Для параметров `inline`-функции, которые инлайнатся (без модификатора `noinline`), компилятор ожидает использование только в формах, совместимых с инлайнингом. Нельзя сохранять такую лямбду для отложенного выполнения.

```kotlin
// - ОШИБКА КОМПИЛЯЦИИ
inline fun processData(callback: () -> Unit) {
    val storedCallback = callback  // ERROR: Illegal usage of inline-parameter
    // Нельзя сохранить callback для последующего использования
}

// - ОШИБКА КОМПИЛЯЦИИ (та же причина)
inline fun deferExecution(action: () -> Unit) {
    val deferredAction = action    // ERROR
    Handler(Looper.getMainLooper()).post(deferredAction)
}

//  ПРАВИЛЬНО — используйте noinline, если нужно сохранить/передать лямбду
inline fun processData(noinline callback: () -> Unit) {
    val storedCallback = callback  // OK
    Handler(Looper.getMainLooper()).post(storedCallback)
}

//  ПРАВИЛЬНО — выполнять inline-лямбду сразу
inline fun processDataNow(callback: () -> Unit) {
    callback()  // OK — прямой вызов
}
```

### 2. Нельзя Передавать Лямбду В Обычную (non-inline) Функцию (без `noinline`)

Нельзя передать инлайновый параметр (лямбду без `noinline`) туда, где от него ожидается значение-функция, которое может быть сохранено или использовано позже, например — в обычную функцию. (Передача в другую `inline`-функцию с совместимым параметром допускается.)

```kotlin
// - ОШИБКА КОМПИЛЯЦИИ
inline fun withLogging(action: () -> Unit) {
    log("Starting")
    executeInBackground(action)  // ERROR: Illegal usage of inline-parameter
    log("Finished")
}

fun executeInBackground(task: () -> Unit) {
    Thread { task() }.start()
}

//  ПРАВИЛЬНО — noinline разрешает передавать параметр как значение
inline fun withLogging(noinline action: () -> Unit) {
    log("Starting")
    executeInBackground(action)  // OK
    log("Finished")
}

//  АЛЬТЕРНАТИВА — не использовать inline
fun withLogging(action: () -> Unit) {
    log("Starting")
    executeInBackground(action)
    log("Finished")
}
```

### 3. Рекурсивные Функции Не Могут Быть Inline

`inline`-функции не могут быть напрямую рекурсивными: компилятор выдаст ошибку, так как наивный инлайнинг привёл бы к бесконечному разворачиванию.

```kotlin
// - ОШИБКА КОМПИЛЯЦИИ
inline fun factorial(n: Int): Int {  // ERROR: Inline function cannot be recursive
    return if (n <= 1) 1 else n * factorial(n - 1)
}

//  ПРАВИЛЬНО — убрать inline
fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}

//  АЛЬТЕРНАТИВА — tailrec вместо inline (другая оптимизация)
tailrec fun factorial(n: Int, acc: Int = 1): Int {
    return if (n <= 1) acc else factorial(n - 1, n * acc)
}
```

### 4. Очень Большие Inline-функции — Рост Размера Кода

Тело `inline`-функции копируется в каждую точку вызова. Инлайнинг большой функции приводит к раздуванию байткода и может ухудшать работу кеша инструкций.

```kotlin
// - ПЛОХАЯ ПРАКТИКА — большая inline-функция
inline fun processUserData(user: User, callback: (Result) -> Unit) {
    // 100+ строк кода
    val validatedUser = validateUser(user)
    val enrichedUser = enrichUserData(validatedUser)
    val processedUser = applyBusinessLogic(enrichedUser)
    val savedUser = saveToDatabase(processedUser)
    val notificationSent = sendNotification(savedUser)
    val analyticsLogged = logAnalytics(savedUser)
    // ... ещё много логики

    callback(Result.Success(savedUser))
}

// Каждый вызов дублирует тело в байткоде.
processUserData(user1) { }
processUserData(user2) { }
processUserData(user3) { }

//  РЕКОМЕНДАЦИЯ — большие функции обычно не должны быть inline
fun processUserData(user: User, callback: (Result) -> Unit) {
    // Код в одном месте; все вызовы ссылаются на эту функцию.
}
```

Рекомендация: использовать `inline` для маленьких функций и утилит высшего порядка; избегать для больших тел.

### 5. Часто Вызываемые Функции: Баланс Выгод И Размера

Для очень маленьких функций инлайнинг, даже при частых вызовах, может быть полезен (меньше накладных расходов вызова, лучше оптимизации). Для нетривиальных тел при множестве вызовов инлайнинг может излишне раздувать код.

```kotlin
// Пример, где inline разумен (крошечный wrapper)
inline fun logInline(message: String) {
    println("[${System.currentTimeMillis()}] $message")
}

// Если тело становится больше/сложнее и вызывается часто,
// лучше обычная функция, чтобы избежать дублирования кода.
fun log(message: String) {
    println("[${System.currentTimeMillis()}] $message")
}
```

Ключевая мысль: «часто вызывается» само по себе не аргумент против или за `inline`; нужно учитывать размер тела, избегание аллокаций и накладные расходы вызова (при этом JIT/HotSpot способен сам инлайнить небольшие функции).

### 6. `reified` Без Реальной Необходимости

`reified` тип-параметры требуют `inline`. Но их использование добавляет ограничения (например, необходимость инлайнинга в вызывающий код). Не стоит добавлять `reified`/`inline`, если не нужен доступ к типу в runtime. При этом наличие `inline`/`reified` не делает функцию автоматически "недоступной" из Java — это зависит от итоговой сигнатуры (например, будет ли параметр `Class<T>` и т.п.).

```kotlin
// - СОМНИТЕЛЬНО — создание инстанса через reflection
inline fun <reified T> createInstance(): T {
    return T::class.java.getDeclaredConstructor().newInstance()
}

// Используем reified, когда реально нужен T в runtime
inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}

// Пример с Android Activity
inline fun <reified T : Activity> Context.startActivity() {
    val intent = Intent(this, T::class.java)
    startActivity(intent)
}

// Использование
context.startActivity<MainActivity>()
```

### 7. Публичный API Библиотеки

`inline`-функции встраиваются в байткод клиента. Изменение реализации/сигнатуры такой функции влияет на бинарную совместимость иначе, чем для обычных функций, и может ломать клиентов, собранных против старой версии (если они не пересобраны).

```kotlin
// - РИСКОВАНО — inline в публичном API библиотеки
// версия 1.0
public inline fun processRequest(url: String, callback: (Response) -> Unit) {
    // Реализация v1.0
    val response = httpClient.get(url)
    callback(response)
}

// версия 1.1
public inline fun processRequest(url: String, callback: (Response) -> Unit) {
    // Новая реализация v1.1
    val response = newHttpClient.get(url)
    callback(response)
}

// Приложения, собранные с 1.0, продолжают содержать старое inlined-тело,
// пока не будут пересобраны против новой версии.

//  БОЛЕЕ БЕЗОПАСНО — обычная функция в публичном API
public fun processRequest(url: String, callback: (Response) -> Unit) {
    val response = httpClient.get(url)
    callback(response)
}

// Обновление библиотеки меняет поведение без необходимости пересборки клиента.
```

### 8. Public Inline Функции И Зависимости С Меньшей Видимостью

Так как тело `public inline` функции раскрывается в коде вызвавшей стороны, оно фактически становится частью публичного API. Оно не должно опираться на объявления, которые недоступны из модулей-клиентов с точки зрения бинарной совместимости (например, `internal` из другого модуля), иначе использование такой функции снаружи станет невозможно. При этом доступ к `private`/`internal` членам того же файла/модуля в теле `inline` технически допустим: код разворачивается там же, где эти члены видимы при компиляции.

```kotlin
class UserManager {
    private val cache = mutableMapOf<Int, User>()

    public inline fun getUser(id: Int): User? {
        return cache[id]  // OK: инлайнинг происходит в том же модуле, где cache виден
    }
}

//  ВАРИАНТ — если функция должна быть доступна из других модулей
//  и не должна раскрывать детали реализации, лучше не делать её inline.
class UserManagerApi {
    private val cache = mutableMapOf<Int, User>()

    public fun getUser(id: Int): User? {
        return cache[id]  // Реализация остаётся внутри модуля
    }
}
```

### 9. Нелокальные Возвраты: Поведенческая Ловушка

`inline`-функции позволяют нелокальные `return` из лямбда-параметров (если они не помечены `crossinline`). Это легально, но может запутывать логику.

```kotlin
inline fun processItems(items: List<String>) {
    items.forEach { item ->
        if (item.isEmpty()) {
            return  // Нелокальный return из processItems, а не из forEach
        }
        println(item)
    }
}

fun caller() {
    processItems(listOf("a", "", "c"))
    println("After processItems")  // НЕ выполнится, если встретится пустая строка
}

//  АЛЬТЕРНАТИВА — только локальный возврат
fun processItemsSafe(items: List<String>) {
    items.forEach { item ->
        if (item.isEmpty()) {
            return@forEach  // Локальный return только из forEach
        }
        println(item)
    }
}
```

Чтобы запретить нелокальные возвраты для конкретного параметра, используйте `crossinline`.

### 10. Когда Производительность Не Критична

Инлайнинг уменьшает накладные расходы вызова и может убрать аллокации лямбд, но увеличивает размер кода и раскрывает реализацию. Если функция тривиальна, часто используется из Java, или важнее стабильность бинарного контракта и читаемость, `inline` может быть излишним — особенно учитывая, что JVM JIT способен самостоятельно инлайнить небольшие методы.

```kotlin
// - ЧАЩЕ ВСЕГО НЕОБЯЗАТЕЛЬНО — выигрыш от inline минимален
inline fun formatUserNameInline(firstName: String, lastName: String): String {
    return "$firstName $lastName"
}

// Часто достаточно обычной функции
fun formatUserName(firstName: String, lastName: String): String {
    return "$firstName $lastName"
}

// Inline особенно полезен, когда:
// 1. Функция маленькая.
// 2. Это higher-order функция, и можно избежать аллокаций лямбд.
// 3. Нужны reified тип-параметры.
```

### Когда Использовать Inline

```kotlin
// Маленькие утилиты высшего порядка
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// Inline с reified типом
inline fun <reified T> Intent.getParcelableExtraCompat(key: String): T? {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        getParcelableExtra(key, T::class.java)
    } else {
        @Suppress("DEPRECATION")
        getParcelableExtra(key) as? T
    }
}

// Небольшая утилита с лямбдой
inline fun <R> synchronized(lock: Any, block: () -> R): R {
    return kotlin.synchronized(lock) {
        block()
    }
}

// DSL builder
inline fun buildUser(init: UserBuilder.() -> Unit): User {
    val builder = UserBuilder()
    builder.init()
    return builder.build()
}
```

### Ключевые Правила

| Ситуация | Можно inline? | Причина |
|----------|---------------|---------|
| Маленькая функция с лямбдой | Да | Снижение накладных расходов вызова и аллокаций |
| Большая функция (много строк) | Обычно нет | Риск раздувания кода |
| Рекурсивная функция | Нет | Прямой inline-рекурс не разрешён |
| Функция с `reified` типом | Да (inline обязателен) | Нужен доступ к типу `T` во время выполнения |
| Публичный API библиотеки | Осторожно | Вопросы бинарной совместимости и обновлений |
| Хранение/передача лямбды как значения | Использовать `noinline` | Нужна обычная семантика значения |
| Часто вызываемая функция | Зависит | Баланс между размером и скоростью, JIT-инлайнингом |

### Использование `noinline` И `crossinline`

```kotlin
// noinline — отключает инлайнинг для параметра, чтобы его можно было хранить/передавать
// crossinline — запрещает нелокальные return из этой лямбды
inline fun transaction(
    noinline onError: (Exception) -> Unit,
    crossinline onSuccess: () -> Unit
) {
    try {
        db.beginTransaction()
        onSuccess()
        db.setTransactionSuccessful()
    } catch (e: Exception) {
        errorHandler.handle(onError)  // onError можно сохранить/передать
    } finally {
        db.endTransaction()
    }
}
```

## Answer (EN)

Although `inline` functions can improve performance (especially for small higher-order functions), there are cases when their use is impossible, restricted, or undesirable.

### 1. Cannot Store Lambda in Variable

For parameters of an `inline` function that are inlined (i.e., not marked `noinline`), the compiler expects them to be used only in ways compatible with inlining. You cannot store such a lambda for deferred execution.

```kotlin
// - COMPILATION ERROR
inline fun processData(callback: () -> Unit) {
    val storedCallback = callback  // ERROR: Illegal usage of inline-parameter
    // Cannot store callback for later use
}

// - COMPILATION ERROR (same reason)
inline fun deferExecution(action: () -> Unit) {
    val deferredAction = action    // ERROR
    Handler(Looper.getMainLooper()).post(deferredAction)
}

//  CORRECT - use noinline when you need to store/pass lambda
inline fun processData(noinline callback: () -> Unit) {
    val storedCallback = callback  // OK
    Handler(Looper.getMainLooper()).post(storedCallback)
}

//  CORRECT - execute inline lambda immediately
inline fun processDataNow(callback: () -> Unit) {
    callback()  // OK - direct call
}
```

### 2. Cannot Pass Lambda to Regular (non-inline) Function (Without noinline)

You cannot pass an inlined parameter (lambda without `noinline`) where it is expected to be a regular function value that may be stored or used later, such as a regular non-inline function. (Passing to another `inline` function with a compatible inline parameter is allowed.)

```kotlin
// - COMPILATION ERROR
inline fun withLogging(action: () -> Unit) {
    log("Starting")
    executeInBackground(action)  // ERROR: Illegal usage of inline-parameter
    log("Finished")
}

fun executeInBackground(task: () -> Unit) {
    Thread { task() }.start()
}

//  CORRECT - use noinline to allow passing
inline fun withLogging(noinline action: () -> Unit) {
    log("Starting")
    executeInBackground(action)  // OK
    log("Finished")
}

//  ALTERNATIVE - do not use inline
fun withLogging(action: () -> Unit) {
    log("Starting")
    executeInBackground(action)
    log("Finished")
}
```

### 3. Recursive Functions Cannot Be Inline

Inline functions cannot be directly recursive: the compiler will report an error because naive inlining would lead to infinite expansion.

```kotlin
// - COMPILATION ERROR
inline fun factorial(n: Int): Int {  // ERROR: Inline function cannot be recursive
    return if (n <= 1) 1 else n * factorial(n - 1)
}

//  CORRECT - remove inline
fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}

//  ALTERNATIVE - tailrec instead of inline (different optimization)
tailrec fun factorial(n: Int, acc: Int = 1): Int {
    return if (n <= 1) acc else factorial(n - 1, n * acc)
}
```

### 4. Very Large Inline Functions - Code Size Increase

Inline functions copy their body to every call site. Inlining a large body can cause code bloat and negatively affect binary size and instruction cache.

```kotlin
// - BAD PRACTICE - large inline function
inline fun processUserData(user: User, callback: (Result) -> Unit) {
    // 100+ lines of code
    val validatedUser = validateUser(user)
    val enrichedUser = enrichUserData(validatedUser)
    val processedUser = applyBusinessLogic(enrichedUser)
    val savedUser = saveToDatabase(processedUser)
    val notificationSent = sendNotification(savedUser)
    val analyticsLogged = logAnalytics(savedUser)
    // ... another 90 lines

    callback(Result.Success(savedUser))
}

// Each call duplicates the inlined body in bytecode.
processUserData(user1) { }
processUserData(user2) { }
processUserData(user3) { }

//  RECOMMENDED - large functions should usually NOT be inline
fun processUserData(user: User, callback: (Result) -> Unit) {
    // Code exists in one place; all calls reference this function.
}
```

Recommendation: Prefer inline for small functions and higher-order utilities; avoid it for large bodies.

### 5. Frequently Called Functions: Consider Trade-offs

For very small functions, inlining even when called frequently can be beneficial (less call overhead, better optimizations). For non-trivial bodies with many call sites, inlining may produce excessive code size.

```kotlin
// Example where inline is reasonable (tiny wrapper)
inline fun logInline(message: String) {
    println("[${System.currentTimeMillis()}] $message")
}

// If the body becomes larger/complex and is called many times,
// prefer a regular function to avoid code bloat.
fun log(message: String) {
    println("[${System.currentTimeMillis()}] $message")
}
```

Key point: "frequently called" alone is neither a reason for nor against `inline`; you must balance body size, allocation-avoidance, call overhead, and remember that the JVM JIT can inline small methods automatically.

### 6. Functions with Reified Types without Necessity

`reified` type parameters require `inline`. But using `reified`/`inline` adds constraints (e.g., it forces inlining into caller bytecode). Avoid them when you don't actually need type information at runtime. Also, using `inline`/`reified` does not automatically forbid Java callers; Java interop depends on the resulting signature (for example, parameters like `Class<T>` vs relying purely on reified semantics inside Kotlin).

```kotlin
// - QUESTIONABLE - uses reflection, may be unnecessary
inline fun <reified T> createInstance(): T {
    return T::class.java.getDeclaredConstructor().newInstance()
}

// Use reified when you actually need T at runtime, e.g., to pass T::class.java
inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}

// Correct usage with Android Activity
inline fun <reified T : Activity> Context.startActivity() {
    val intent = Intent(this, T::class.java)
    startActivity(intent)
}

// Usage
context.startActivity<MainActivity>()
```

### 7. Public Library API

Inline functions are inlined into client bytecode. Changing their implementation/signature affects binary compatibility differently from regular functions and may break clients compiled against old versions (until they are recompiled).

```kotlin
// - RISKY - inline in public API of a library
// library version 1.0
public inline fun processRequest(url: String, callback: (Response) -> Unit) {
    // Implementation v1.0
    val response = httpClient.get(url)
    callback(response)
}

// version 1.1
public inline fun processRequest(url: String, callback: (Response) -> Unit) {
    // New implementation v1.1
    val response = newHttpClient.get(url)
    callback(response)
}

// Apps compiled with 1.0 keep the old inlined body
// until they are recompiled against the new version.

//  SAFER - regular function in public API
public fun processRequest(url: String, callback: (Response) -> Unit) {
    val response = httpClient.get(url)
    callback(response)
}

// Updating the library updates behavior without requiring client recompilation.
```

### 8. Public Inline Functions with Less-visible Dependencies

Because the body of a `public inline` function is effectively part of the public API surface (it is inlined into callers), it should not rely on declarations that will be invisible or unavailable to client modules (e.g., `internal` declarations from another module), or the function will not be usable externally. Accessing `private`/`internal` members from the same file/module in an inline function is technically allowed because inlining happens where those members are visible at compile time.

```kotlin
class UserManager {
    private val cache = mutableMapOf<Int, User>()

    public inline fun getUser(id: Int): User? {
        return cache[id]  // OK: inlining occurs in the same module where cache is visible
    }
}

//  OPTION - if the function is part of a public API for other modules
//  and you don't want to expose implementation details, prefer non-inline.
class UserManagerApi {
    private val cache = mutableMapOf<Int, User>()

    public fun getUser(id: Int): User? {
        return cache[id]
    }
}
```

### 9. Non-local Returns: Behavioral Pitfall

Inline functions allow non-local returns from lambda parameters (unless marked `crossinline`). This is legal but can be confusing, so it's more of a semantics caveat than a strict prohibition.

```kotlin
inline fun processItems(items: List<String>) {
    items.forEach { item ->
        if (item.isEmpty()) {
            return  // Non-local return from processItems, NOT from forEach
        }
        println(item)
    }
}

fun caller() {
    processItems(listOf("a", "", "c"))
    println("After processItems")  // Will NOT execute if there is an empty string
}

//  ALTERNATIVE - avoid non-local return for clarity
fun processItemsSafe(items: List<String>) {
    items.forEach { item ->
        if (item.isEmpty()) {
            return@forEach  // Local return from forEach only
        }
        println(item)
    }
}
```

To forbid non-local returns for a particular parameter, use `crossinline`.

### 10. When Performance is not Critical

Inlining reduces call overhead and can eliminate lambda allocations, but increases code size and exposes implementation details. If performance is not critical, the function is trivial, or binary compatibility and readability are more important, `inline` may be unnecessary — especially given that the JVM JIT can inline small methods on its own.

```kotlin
// - OFTEN UNNECESSARY - inline gives minimal benefit here
inline fun formatUserNameInline(firstName: String, lastName: String): String {
    return "$firstName $lastName"
}

// Regular function is often sufficient
fun formatUserName(firstName: String, lastName: String): String {
    return "$firstName $lastName"
}

// Inline is most useful when:
// 1. The function is small.
// 2. It is higher-order and can avoid lambda allocations.
// 3. You need reified type parameters.
```

### When You SHOULD Use Inline

```kotlin
// Inline for small higher-order utilities
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// Inline with reified type
inline fun <reified T> Intent.getParcelableExtraCompat(key: String): T? {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        getParcelableExtra(key, T::class.java)
    } else {
        @Suppress("DEPRECATION")
        getParcelableExtra(key) as? T
    }
}

// Small utility with lambda
inline fun <R> synchronized(lock: Any, block: () -> R): R {
    return kotlin.synchronized(lock) {
        block()
    }
}

// DSL builders
inline fun buildUser(init: UserBuilder.() -> Unit): User {
    val builder = UserBuilder()
    builder.init()
    return builder.build()
}
```

### Key Rules

| Situation | Can inline? | Reason |
|----------|-------------|--------|
| Small function with lambda | Yes | Avoid call + lambda overhead |
| Large function (many lines) | Usually no | Risk of code bloat |
| Recursive function | No | Inline recursive not allowed |
| Function with `reified` type | Yes (inline required) | Needs T at runtime |
| Public library API | Careful | Binary compatibility & update issues |
| Storing/passing lambda as value | Use noinline | Normal value semantics needed |
| Frequently called function | Depends | Trade off size vs speed, JIT inlining |

### Using Noinline and Crossinline

```kotlin
// noinline - disables inlining for specific parameter so it can be stored/passed
// crossinline - disallows non-local returns from that lambda
inline fun transaction(
    noinline onError: (Exception) -> Unit,
    crossinline onSuccess: () -> Unit
) {
    try {
        db.beginTransaction()
        onSuccess()
        db.setTransactionSuccessful()
    } catch (e: Exception) {
        errorHandler.handle(onError)  // onError can be stored/passed
    } finally {
        db.endTransaction()
    }
}
```

## Дополнительные Вопросы (RU)

- В чем ключевые отличия inline-функций в Kotlin по сравнению с Java-подходом?
- В каких практических ситуациях вы бы использовали inline-функции?
- Какие распространенные ошибки и подводные камни при использовании inline стоит учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-coroutine-context-elements--kotlin--hard]]

## Related Questions

- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-coroutine-context-elements--kotlin--hard]]
