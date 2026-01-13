---
id: kotlin-157
title: Crossinline Keyword / Ключевое слово crossinline
aliases:
- Crossinline Keyword
- Crossinline ключевое слово
topic: kotlin
subtopics:
- inline-functions
question_kind: theory
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin-features
- q-abstract-class-vs-interface--kotlin--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- difficulty/medium
- inline-functions
- kotlin
- lambda
- non-local-returns
---
# Вопрос (RU)
> Для чего нужно ключевое слово `crossinline` в inline-функциях Kotlin?

---

# Question (EN)
> What is the `crossinline` keyword for in Kotlin inline functions?

## Ответ (RU)

`crossinline` — это модификатор для параметров-лямбд inline-функций, который запрещает non-local returns (возврат из внешней функции) из этой лямбды. Это нужно, когда параметр-лямбда inline-функции используется в местах, где non-local return был бы небезопасен или невозможен: например, при вызове из вложенной лямбды, из другого потока, при сохранении для отложенного выполнения или передаче дальше.

Важно: `crossinline` не "делает лямбду потокобезопасной" и не обязателен для любого вызова в другом потоке сам по себе — он нужен, когда компилятор должен запретить потенциальный non-local return из такой лямбды.

### Проблема: Non-local Returns

```kotlin
// Обычная inline-функция
inline fun processItems(items: List<String>, action: (String) -> Unit) {
    items.forEach { item ->
        action(item)  // Лямбда может сделать return из caller!
    }
}

fun caller() {
    val items = listOf("a", "b", "c")

    processItems(items) { item ->
        if (item == "b") {
            return  // Non-local return — выход из caller(), НЕ из лямбды action
        }
        println(item)
    }

    println("After processItems")  // НЕ ВЫПОЛНИТСЯ, если встретится "b"
}

// Output:
// a
// (функция caller() завершается)
```

### Решение: Crossinline

```kotlin
// crossinline запрещает non-local return
inline fun processItemsSafely(
    items: List<String>,
    crossinline action: (String) -> Unit  // crossinline!
) {
    items.forEach { item ->
        action(item)
    }
}

fun caller() {
    val items = listOf("a", "b", "c")

    processItemsSafely(items) { item ->
        if (item == "b") {
            // return  // ОШИБКА КОМПИЛЯЦИИ: запрещен non-local return
            return@processItemsSafely  // Явный labeled return (возврат из лямбды) — OK
        }
        println(item)
    }

    println("After processItems")  // ВЫПОЛНИТСЯ
}
```

### Когда Нужен Crossinline

Общая идея: если inline-параметр-лямбда используется так, что non-local return из неё был бы небезопасен или технически невозможен, компилятор требует пометить его `crossinline` (или `noinline`). Типичные случаи ниже.

#### 1. Лямбда Выполняется В Другом Потоке (через Другую лямбду)

```kotlin
// БЕЗ crossinline и с возможным non-local return — ошибка компиляции
inline fun runInBackground(action: () -> Unit) {
    Thread {
        action()  // ERROR: 'action' может содержать non-local return, недопустимо в этой позиции
    }.start()
}

// С crossinline — non-local return запрещен, вызов безопасен
inline fun runInBackground(crossinline action: () -> Unit) {
    Thread {
        action()  // OK - non-local return запрещен
    }.start()
}

// Использование
fun downloadFile() {
    runInBackground {
        // return  // Ошибка компиляции: non-local return запрещен
        val data = fetchData()
        println("Downloaded: $data")
    }
    println("Download started")
}
```

Здесь важно: причина `crossinline` — не сам факт другого потока, а то, что лямбда вызывается из вложенной лямбды, которая может "убежать" из исходной inline-функции.

#### 2. Лямбда Вызывается Из Вложенной Функции

```kotlin
inline fun transaction(crossinline block: () -> Unit) {
    fun executeTransaction() {
        database.beginTransaction()
        try {
            block()  // Вызов из вложенной функции: non-local return из block был бы небезопасен
            database.setTransactionSuccessful()
        } finally {
            database.endTransaction()
        }
    }

    executeTransaction()
}

// Использование
fun updateUser(user: User) {
    transaction {
        // return  // Ошибка: non-local return запрещен для crossinline
        userDao.update(user)
    }
}
```

#### 3. Лямбда Сохраняется Для Отложенного Выполнения

```kotlin
inline fun defer(crossinline action: () -> Unit): () -> Unit {
    return {
        action()  // Выполнится позже; non-local return отсюда был бы невозможен
    }
}

fun scheduleTask() {
    val deferredAction = defer {
        println("Delayed task")
        // return  // Ошибка компиляции
    }

    Handler(Looper.getMainLooper()).postDelayed(deferredAction, 1000)
}
```

### Сравнение: Обычная Лямбда Vs Crossinline

```kotlin
inline fun example(
    normalLambda: () -> Unit,           // Может использовать non-local return
    crossinline crossLambda: () -> Unit // Non-local return запрещен
) {
    // normalLambda: можно вызывать напрямую в теле inline-функции
    normalLambda()  // OK
    // Thread { normalLambda() }.start()  // ERROR: если попытаться так использовать, компилятор потребует crossinline/noinline

    // crossLambda: безопасно вызывать из вложенных лямбд, других потоков и т.п.
    crossLambda()  // OK
    Thread { crossLambda() }.start()  // OK
}

fun caller() {
    example(
        normalLambda = {
            return  // OK - non-local return: выход из caller()
        },
        crossLambda = {
            // return  // ERROR - non-local return запрещен
            return@example  // OK - labeled return из лямбды
        }
    )
}
```

### Практические Примеры

#### Пример 1: Async Execution

```kotlin
inline fun asyncTask(crossinline onComplete: (Result) -> Unit) {
    CoroutineScope(Dispatchers.IO).launch {
        val result = performTask()

        withContext(Dispatchers.Main) {
            onComplete(result)  // Вызов в другой корутине / потоке через вложенную лямбду
        }
    }
}

// Использование
fun loadData() {
    asyncTask { result ->
        // return  // Ошибка: non-local return запрещен
        updateUI(result)
    }
    println("Loading started")
}
```

#### Пример 2: Event Listener

```kotlin
inline fun onClick(crossinline listener: (View) -> Unit) {
    button.setOnClickListener { view ->
        listener(view)  // Вызов из другой лямбды
    }
}

fun setupButton() {
    onClick { view ->
        // return  // Ошибка: non-local return запрещен
        toast("Clicked: ${view.id}")
    }
}
```

#### Пример 3: Try-catch Wrapper

```kotlin
inline fun tryCatch(
    crossinline tryBlock: () -> Unit,
    crossinline catchBlock: (Exception) -> Unit
) {
    try {
        tryBlock()
    } catch (e: Exception) {
        catchBlock(e)
    }
}

fun saveData() {
    tryCatch(
        tryBlock = {
            // return  // Ошибка: non-local return запрещен
            database.save(data)
        },
        catchBlock = { e ->
            // return  // Ошибка: non-local return запрещен
            logError(e)
        }
    )
}
```

### Комбинация С Noinline

```kotlin
inline fun process(
    immediateAction: () -> Unit,              // Inline, разрешен non-local return (если используется напрямую)
    crossinline deferredAction: () -> Unit,   // Inline, non-local return запрещен
    noinline storedAction: () -> Unit         // Не inline, можно сохранить и передавать
) {
    // immediateAction — выполнить сразу (может использовать non-local return, если вызван напрямую)
    immediateAction()

    // deferredAction — выполнить, например, в callback (запрещаем non-local return)
    Handler().post {
        deferredAction()
    }

    // storedAction — можно сохранить для последующего вызова
    val stored: () -> Unit = storedAction
    callbacks.add(stored)
}
```

### Ошибки Без Crossinline

```kotlin
// ОШИБКА: параметр-лямбда inline-функции используется внутри вложенной лямбды,
// из которой потенциальный non-local return был бы некорректен.
inline fun broken(action: () -> Unit) {
    Thread {
        action()  // ERROR: Can't inline 'action' here: it may contain non-local returns
    }.start()
}

// Compiler error (упрощенно):
// "Can't inline 'action' here: it may contain non-local returns.
// Add 'crossinline' modifier to parameter declaration 'action'"

// ИСПРАВЛЕНО: запрещаем non-local return из action
inline fun fixed(crossinline action: () -> Unit) {
    Thread {
        action()  // OK
    }.start()
}
```

### Best Practices

**1. Используйте `crossinline` когда:**
- Параметр-лямбда inline-функции вызывается из вложенной лямбды, функции или callback'а, который может выйти за пределы исходной inline-функции.
- Лямбда может выполняться асинхронно (в другом потоке / корутине) через вложенные лямбды.
- Лямбда сохраняется для отложенного выполнения, но вы всё ещё хотите её инлайнить (возврат non-local должен быть запрещен).
- Лямбда передается в не-inline функцию или API, который вызывает её позже через вложенные вызовы.

**Ключевой критерий:** необходимо запретить потенциальные non-local returns из этой лямбды в местах её использования.

**2. НЕ используйте `crossinline` когда:**
- Лямбда вызывается только напрямую в теле inline-функции.
- Вам нужно разрешить non-local returns из лямбды для управления потоком выполнения вызывающей функции.

**3. Labeled returns всегда доступны (вместо non-local):**

```kotlin
inline fun process(crossinline action: () -> Unit) {
    action()
}

fun test() {
    process {
        // return  // ERROR - non-local return запрещен
        return@process  // OK - labeled return (возврат только из лямбды)
    }
}
```

### Сравнительная Таблица

| Модификатор        | Non-local return | Можно сохранить/передать дальше | Можно вызывать из вложенных контекстов (другие лямбды/потоки) |
|--------------------|------------------|----------------------------------|--------------------------------------------------------------|
| (inline-параметр)  | Да               | Нет (если попытаться — ошибка)  | Да, только при прямом вызове в inline-функции                |
| `crossinline`      | Нет              | Нет (если попытаться — ошибка)  | Да, безопасно                                                |
| `noinline`         | Нет              | Да                              | Да                                                           |

## Answer (EN)

`crossinline` is a modifier for lambda parameters in inline functions that disallows non-local returns (i.e., `return` that exits the caller of the inline function) from that lambda. It is required when the inline lambda parameter is used in positions where such non-local returns would be unsafe or technically impossible.

Important clarifications:
- `crossinline` does NOT make a lambda thread-safe.
- The problem is not "other thread" by itself, but when the lambda is invoked from nested lambdas/functions or callbacks that can escape the inline function scope (including background threads, coroutines, deferred execution).
- With `crossinline`, only local or labeled returns (e.g. `return@foo`) are allowed; non-local returns are prohibited.

### Problem: Non-local Returns

```kotlin
inline fun processItems(items: List<String>, action: (String) -> Unit) {
    items.forEach { item ->
        action(item)  // May non-locally return from caller
    }
}

fun caller() {
    val items = listOf("a", "b", "c")

    processItems(items) { item ->
        if (item == "b") {
            return  // Non-local return from caller()
        }
        println(item)
    }

    println("After processItems")  // Not executed if "b" is found
}
```

### Solution: `crossinline`

```kotlin
inline fun processItemsSafely(
    items: List<String>,
    crossinline action: (String) -> Unit
) {
    items.forEach { item ->
        action(item)
    }
}

fun caller() {
    val items = listOf("a", "b", "c")

    processItemsSafely(items) { item ->
        if (item == "b") {
            // return  // Compilation error: non-local return not allowed
            return@processItemsSafely  // Labeled return from lambda: OK
        }
        println(item)
    }

    println("After processItems")  // Will be executed
}
```

### When `crossinline` Is Needed

General rule: if an inline lambda parameter is used in a position where a non-local return would be unsafe or impossible, the compiler requires `crossinline` (or `noinline`). Typical cases:

#### 1. Lambda Executed on Another Thread (via Nested lambda)

```kotlin
inline fun runInBackground(action: () -> Unit) {
    Thread {
        action()  // ERROR: may contain non-local return, invalid position
    }.start()
}

inline fun runInBackground(crossinline action: () -> Unit) {
    Thread {
        action()  // OK: non-local returns are forbidden
    }.start()
}

fun downloadFile() {
    runInBackground {
        // return  // Compilation error: non-local return not allowed
        val data = fetchData()
        println("Downloaded: $data")
    }
    println("Download started")
}
```

Here the reason for `crossinline` is that `action` is called from a nested lambda that escapes the inline call, not merely that it runs on a different thread.

#### 2. Lambda Called from Nested Function

```kotlin
inline fun transaction(crossinline block: () -> Unit) {
    fun executeTransaction() {
        database.beginTransaction()
        try {
            block()  // Non-local return from here would be unsafe
            database.setTransactionSuccessful()
        } finally {
            database.endTransaction()
        }
    }

    executeTransaction()
}

fun updateUser(user: User) {
    transaction {
        // return  // Error: non-local return not allowed for crossinline
        userDao.update(user)
    }
}
```

#### 3. Lambda Stored for Deferred Execution

```kotlin
inline fun defer(crossinline action: () -> Unit): () -> Unit {
    return {
        action()  // Will run later; non-local return would be impossible
    }
}

fun scheduleTask() {
    val deferredAction = defer {
        println("Delayed task")
        // return  // Compilation error
    }

    Handler(Looper.getMainLooper()).postDelayed(deferredAction, 1000)
}
```

### Comparison: Regular Vs `crossinline` Lambda

```kotlin
inline fun example(
    normalLambda: () -> Unit,           // May use non-local return (if called directly)
    crossinline crossLambda: () -> Unit // Non-local return is forbidden
) {
    normalLambda()  // OK
    // Thread { normalLambda() }.start()  // ERROR: would require crossinline/noinline

    crossLambda()  // OK
    Thread { crossLambda() }.start()  // OK
}

fun caller() {
    example(
        normalLambda = {
            return  // OK: non-local return from caller()
        },
        crossLambda = {
            // return  // ERROR: non-local return forbidden
            return@example  // OK: labeled return from lambda
        }
    )
}
```

### Practical Examples

#### Example 1: Async Execution

```kotlin
inline fun asyncTask(crossinline onComplete: (Result) -> Unit) {
    CoroutineScope(Dispatchers.IO).launch {
        val result = performTask()

        withContext(Dispatchers.Main) {
            onComplete(result)  // Called via nested lambda in another coroutine/thread
        }
    }
}

fun loadData() {
    asyncTask { result ->
        // return  // Error: non-local return forbidden
        updateUI(result)
    }
    println("Loading started")
}
```

#### Example 2: Event Listener

```kotlin
inline fun onClick(crossinline listener: (View) -> Unit) {
    button.setOnClickListener { view ->
        listener(view)  // Called from another lambda
    }
}

fun setupButton() {
    onClick { view ->
        // return  // Error: non-local return forbidden
        toast("Clicked: ${view.id}")
    }
}
```

#### Example 3: Try-catch Wrapper

```kotlin
inline fun tryCatch(
    crossinline tryBlock: () -> Unit,
    crossinline catchBlock: (Exception) -> Unit
) {
    try {
        tryBlock()
    } catch (e: Exception) {
        catchBlock(e)
    }
}

fun saveData() {
    tryCatch(
        tryBlock = {
            // return  // Error: non-local return forbidden
            database.save(data)
        },
        catchBlock = { e ->
            // return  // Error: non-local return forbidden
            logError(e)
        }
    )
}
```

### Combination with `noinline`

```kotlin
inline fun process(
    immediateAction: () -> Unit,            // Inline, non-local return allowed if called directly
    crossinline deferredAction: () -> Unit, // Inline, non-local return forbidden
    noinline storedAction: () -> Unit       // Not inlined, can be stored/passed freely
) {
    immediateAction()

    Handler().post {
        deferredAction()
    }

    val stored: () -> Unit = storedAction
    callbacks.add(stored)
}
```

### What Goes Wrong Without `crossinline`

```kotlin
inline fun broken(action: () -> Unit) {
    Thread {
        action()  // ERROR: may contain non-local returns
    }.start()
}

inline fun fixed(crossinline action: () -> Unit) {
    Thread {
        action()  // OK: non-local returns forbidden
    }.start()
}
```

### Best Practices

Use `crossinline` when:
- The inline lambda is invoked from nested lambdas/functions or callbacks that can escape the inline call.
- The lambda may be run asynchronously (different thread/coroutine) via nested lambdas.
- The lambda is wrapped or stored for deferred execution, but you still want inlining and must forbid non-local returns.
- The lambda is passed into non-inline APIs that will call it later from nested contexts.

Avoid `crossinline` when:
- The lambda is called only directly in the inline function body.
- You rely on non-local returns from that lambda for caller control flow.

Remember: labeled returns (e.g. `return@foo`) remain available with `crossinline`.

## Дополнительные Вопросы (RU)

- В чем отличие `crossinline` от поведения лямбд в Java?
- Когда вы бы применили `crossinline` на практике?
- Какие типичные ошибки возникают при неправильном использовании `crossinline`?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/reference/inline-functions.html)

## Связанные Вопросы (RU)

- [[q-abstract-class-vs-interface--kotlin--medium]]
- [[q-star-projection-vs-any-generics--kotlin--hard]]

## Related Questions

- [[q-abstract-class-vs-interface--kotlin--medium]]
- [[q-star-projection-vs-any-generics--kotlin--hard]]
