---
id: kotlin-154
title: "Inline Function Limitations / Ограничения inline функций"
aliases: [Function, Inline, Limitations]
topic: kotlin
subtopics: [coroutines, delegation, flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-coroutine-context-elements--kotlin--hard, q-testing-stateflow-sharedflow--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium]
date created: Friday, October 17th 2025, 3:04:07 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Когда Нельзя Использовать Inline Функции?

**English**: When can't you use inline functions?

## Answer (EN)
Although `inline` functions improve performance through code inlining, there are cases when their use is impossible, undesirable, or even harmful.

### 1. Cannot Store Lambda in Variable

Inline function embeds lambda code at call site, so you cannot store lambda for deferred execution.

```kotlin
// - COMPILATION ERROR
inline fun processData(callback: () -> Unit) {
    val storedCallback = callback  // ERROR: Illegal usage of inline-parameter
    // Cannot store callback for later use
}

// - ERROR
inline fun deferExecution(action: () -> Unit) {
    val deferredAction = action
    Handler(Looper.getMainLooper()).post(deferredAction)  // ERROR
}

//  CORRECT - use noinline
inline fun processData(noinline callback: () -> Unit) {
    val storedCallback = callback  // OK
    Handler(Looper.getMainLooper()).post(storedCallback)
}

//  CORRECT - execute inline lambda immediately
inline fun processDataNow(callback: () -> Unit) {
    callback()  // OK - direct call
}
```

### 2. Cannot Pass Lambda to Regular (non-inline) Function

```kotlin
// - ОШИБКА КОМПИЛЯЦИИ
inline fun withLogging(action: () -> Unit) {
    log("Starting")
    executeInBackground(action)  // ERROR: Illegal usage
    log("Finished")
}

fun executeInBackground(task: () -> Unit) {
    Thread { task() }.start()
}

//  ПРАВИЛЬНО - использовать noinline
inline fun withLogging(noinline action: () -> Unit) {
    log("Starting")
    executeInBackground(action)  // OK
    log("Finished")
}

//  АЛЬТЕРНАТИВА - не использовать inline
fun withLogging(action: () -> Unit) {
    log("Starting")
    executeInBackground(action)
    log("Finished")
}
```

### 3. Recursive Functions Cannot Be Inline

Inlining a recursive function would lead to infinite code growth.

```kotlin
// - ОШИБКА КОМПИЛЯЦИИ
inline fun factorial(n: Int): Int {  // ERROR: Inline function cannot be recursive
    return if (n <= 1) 1 else n * factorial(n - 1)
}

//  ПРАВИЛЬНО - убрать inline
fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}

//  ALTERNATIVE - tailrec instead of inline
tailrec fun factorial(n: Int, acc: Int = 1): Int {
    return if (n <= 1) acc else factorial(n - 1, n * acc)
}
```

### 4. Large Functions - Code Size Increase

Inline functions copy their code to every call site, which can significantly increase APK size.

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
    // ... еще 90 строк

    callback(Result.Success(savedUser))
}

// Each call adds ~100 lines of code!
processUserData(user1) { }  // +100 lines in bytecode
processUserData(user2) { }  // +100 lines in bytecode
processUserData(user3) { }  // +100 lines in bytecode

//  CORRECT - large functions should NOT be inline
fun processUserData(user: User, callback: (Result) -> Unit) {
    // Code executes in only one place
    // All calls reference one function
}
```

**Recommendation**: Use inline only for small functions (1-3 lines).

### 5. Functions with High Call Frequency

```kotlin
// - ПЛОХАЯ ПРАКТИКА - inline функция вызывается очень часто
inline fun log(message: String) {
    println("[${System.currentTimeMillis()}] $message")
}

// Если вызывается 10,000 раз, код будет продублирован 10,000 раз
repeat(10_000) {
    log("Iteration $it")  // Раздутие кода!
}

//  ПРАВИЛЬНО - обычная функция
fun log(message: String) {
    println("[${System.currentTimeMillis()}] $message")
}
```

### 6. Functions with Reified Types without Necessity

```kotlin
// - ИЗБЫТОЧНО - reified без реальной необходимости
inline fun <reified T> createInstance(): T {
    // Просто создаем объект, reified не нужен
    return T::class.java.newInstance()
}

//  ПРАВИЛЬНО - использовать reified только когда нужен тип в runtime
inline fun <reified T> Gson.fromJson(json: String): T {
    // Reified нужен чтобы передать T::class.java в Gson
    return fromJson(json, T::class.java)
}

// Правильное использование reified
inline fun <reified T : Activity> Context.startActivity() {
    val intent = Intent(this, T::class.java)
    startActivity(intent)
}

// Использование
context.startActivity<MainActivity>()  // Без явного .java
```

### 7. Public Library API

Inline functions are embedded into client code, complicating library updates.

```kotlin
// - ПЛОХАЯ ПРАКТИКА - inline в public API библиотеки
// library version 1.0
inline fun processRequest(url: String, callback: (Response) -> Unit) {
    // Реализация версии 1.0
    val response = httpClient.get(url)
    callback(response)
}

// Если изменить реализацию в version 1.1:
inline fun processRequest(url: String, callback: (Response) -> Unit) {
    // Новая реализация версии 1.1
    val response = newHttpClient.get(url)  // Новый клиент!
    callback(response)
}

// Проблема: приложения, скомпилированные с 1.0, используют СТАРЫЙ код
// даже если обновили библиотеку до 1.1!

//  ПРАВИЛЬНО - обычная функция в public API
fun processRequest(url: String, callback: (Response) -> Unit) {
    val response = httpClient.get(url)
    callback(response)
}

// Теперь обновление библиотеки сразу применит новую реализацию
```

### 8. Functions with internal/private Dependencies

```kotlin
// - ОШИБКА - inline функция обращается к private полю
class UserManager {
    private val cache = mutableMapOf<Int, User>()

    inline fun getUser(id: Int): User? {
        // ERROR: Public-API inline function cannot access non-public-API 'cache'
        return cache[id]
    }
}

//  ПРАВИЛЬНО - убрать inline или сделать cache internal
class UserManager {
    internal val cache = mutableMapOf<Int, User>()

    inline fun getUser(id: Int): User? {
        return cache[id]  // OK
    }
}

//  АЛЬТЕРНАТИВА - не использовать inline
class UserManager {
    private val cache = mutableMapOf<Int, User>()

    fun getUser(id: Int): User? {
        return cache[id]
    }
}
```

### 9. Functions with Non-local Returns in Complex Constructs

```kotlin
// - СЛОЖНО ДЛЯ ПОНИМАНИЯ
inline fun processItems(items: List<String>) {
    items.forEach { item ->
        if (item.isEmpty()) {
            return  // Non-local return из processItems, НЕ из forEach!
        }
        println(item)
    }
}

fun caller() {
    processItems(listOf("a", "", "c"))
    println("After processItems")  // НЕ ВЫПОЛНИТСЯ если есть пустая строка!
}

//  ПРАВИЛЬНО - использовать явные return или не inline
fun processItems(items: List<String>) {
    items.forEach { item ->
        if (item.isEmpty()) {
            return@forEach  // Локальный return из forEach
        }
        println(item)
    }
}
```

### 10. When Performance is not Critical

```kotlin
// - ИЗБЫТОЧНО - inline без выигрыша в производительности
inline fun formatUserName(firstName: String, lastName: String): String {
    return "$firstName $lastName"
}

// Вызывается 1 раз при загрузке профиля
val name = formatUserName(user.first, user.last)

//  ПРАВИЛЬНО - обычная функция
fun formatUserName(firstName: String, lastName: String): String {
    return "$firstName $lastName"
}

// Inline стоит использовать только когда:
// 1. Функция вызывается часто (в циклах)
// 2. Принимает лямбды (избегает создания объектов)
// 3. Очень маленькая (1-3 строки)
```

### When You SHOULD Use Inline

```kotlin
//  ПРАВИЛЬНО - inline для higher-order функций
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

//  ПРАВИЛЬНО - inline с reified
inline fun <reified T> Intent.getParcelableExtraCompat(key: String): T? {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        getParcelableExtra(key, T::class.java)
    } else {
        @Suppress("DEPRECATION")
        getParcelableExtra(key) as? T
    }
}

//  ПРАВИЛЬНО - маленькие утилиты с лямбдами
inline fun <R> synchronized(lock: Any, block: () -> R): R {
    kotlin.synchronized(lock) {
        return block()
    }
}

//  ПРАВИЛЬНО - DSL builders
inline fun buildUser(init: UserBuilder.() -> Unit): User {
    val builder = UserBuilder()
    builder.init()
    return builder.build()
}
```

### Key Rules

| Situation | Can inline? | Reason |
|----------|---------------|---------|
| Small function with lambda | - Yes | Optimization |
| Large function (50+ lines) | - No | Code bloat |
| Recursive function | - No | Infinite inlining |
| Function with reified type | - Yes | Inline required |
| Public library API | WARNING: Careful | Update issues |
| Storing lambda | - No | Use noinline |
| Frequently called function | WARNING: Depends | Size/speed balance |

### Using Noinline and Crossinline

```kotlin
// noinline - disable inline for specific parameter
inline fun transaction(
    noinline onError: (Exception) -> Unit,  // Can be stored
    crossinline onSuccess: () -> Unit       // Cannot non-local return
) {
    try {
        db.beginTransaction()
        onSuccess()
        db.setTransactionSuccessful()
    } catch (e: Exception) {
        errorHandler.handle(onError)  // onError можно передать
    } finally {
        db.endTransaction()
    }
}
```

**English**: Cannot use inline when: 1) **Storing lambda** in variable (use `noinline`), 2) **Passing lambda** to non-inline function (`noinline`), 3) **Recursive functions** (infinite inlining), 4) **Large functions** (code bloat), 5) **Frequently called** simple functions (bloat), 6) **Public library API** (update issues), 7) **Accessing private members** from public inline. Use inline only for: small functions with lambdas, `reified` type parameters, DSL builders. Use `noinline` to exclude specific parameters from inlining.

## Ответ (RU)

Нельзя использовать inline когда:

### Основные Ограничения

1. **Нельзя сохранить лямбду в переменную** - inline функция встраивает код лямбды в место вызова, поэтому нельзя сохранить для отложенного выполнения (используйте `noinline`)

2. **Нельзя передать лямбду в не-inline функцию** - inline лямбду нельзя передать в обычную функцию (используйте `noinline`)

3. **Рекурсивные функции нельзя inline** - приведет к бесконечному росту кода

4. **Большие функции** - inline копирует код в каждое место вызова, раздувая размер APK

5. **Часто вызываемые функции** - если вызывается 10,000 раз, код будет продублирован 10,000 раз

6. **Public library API** - inline функции встраиваются в код клиента, усложняя обновление библиотеки

7. **Доступ к private членам** - public inline функция не может обращаться к private полям

### Когда ИСПОЛЬЗОВАТЬ Inline

- Маленькие функции с лямбдами (1-3 строки)
- Функции с `reified` параметрами типов (inline обязателен)
- DSL builders
- Higher-order функции где важна производительность

Используйте `noinline` чтобы исключить конкретные параметры из inlining, и `crossinline` когда нельзя делать non-local return.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-coroutine-context-elements--kotlin--hard]]
-
