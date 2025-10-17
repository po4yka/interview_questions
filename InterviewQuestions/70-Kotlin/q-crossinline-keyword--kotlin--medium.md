---
id: "20251015082236022"
title: "Crossinline Keyword / Ключевое слово crossinline"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - kotlin
  - inline-functions
  - lambda
  - non-local-returns
---
# Зачем нужен crossinline?

# Question (EN)
> What is the `crossinline` keyword for in Kotlin inline functions?

# Вопрос (RU)
> Для чего нужно ключевое слово `crossinline` в inline-функциях Kotlin?

---

## Answer (EN)

`crossinline` is a modifier for lambda parameters in inline functions that disallows non-local returns. It's necessary when the lambda is executed in a different context (another thread, nested function, or callback).

**Without crossinline**: Lambda can `return` from the outer function, causing unexpected early exits.
**With crossinline**: Only labeled returns are allowed (`return@label`), preventing bugs.

**Use crossinline when lambda is:**
1. Called from another thread
2. Called from a nested function
3. Stored for deferred execution
4. Passed to a non-inline function

## Ответ (RU)

`crossinline` — это модификатор для параметров-лямбд inline функций, который запрещает non-local returns (возврат из внешней функции) из лямбды. Это необходимо когда лямбда выполняется в другом контексте (другой поток, вложенная функция, callback).

### Проблема: non-local returns

```kotlin
// Обычная inline функция
inline fun processItems(items: List<String>, action: (String) -> Unit) {
    items.forEach { item ->
        action(item)  // Лямбда может сделать return из caller!
    }
}

fun caller() {
    val items = listOf("a", "b", "c")

    processItems(items) { item ->
        if (item == "b") {
            return  // WARNING: Non-local return - выход из caller(), НЕ из action!
        }
        println(item)
    }

    println("After processItems")  // НЕ ВЫПОЛНИТСЯ если встретится "b"
}

// Output:
// a
// (функция caller() завершается)
```

### Решение: crossinline

```kotlin
// crossinline запрещает non-local return
inline fun processItemsSafely(
    items: List<String>,
    crossinline action: (String) -> Unit  // crossinline!
) {
    items.forEach { item ->
        action(item)  // Теперь безопасно
    }
}

fun caller() {
    val items = listOf("a", "b", "c")

    processItemsSafely(items) { item ->
        if (item == "b") {
            return  // - ОШИБКА КОМПИЛЯЦИИ: return не разрешен
            return@processItemsSafely  //  Labeled return OK
        }
        println(item)
    }

    println("After processItems")  // ВЫПОЛНИТСЯ
}
```

### Когда нужен crossinline

#### 1. Лямбда выполняется в другом потоке

```kotlin
// - БЕЗ crossinline - ошибка
inline fun runInBackground(action: () -> Unit) {
    Thread {
        action()  // ERROR: Can't inline because action может содержать return
    }.start()
}

//  С crossinline
inline fun runInBackground(crossinline action: () -> Unit) {
    Thread {
        action()  // OK - non-local return запрещен
    }.start()
}

// Использование
fun downloadFile() {
    runInBackground {
        // return  // Ошибка компиляции
        val data = fetchData()
        println("Downloaded: $data")
    }
    println("Download started")  // Всегда выполнится
}
```

#### 2. Лямбда вызывается из вложенной функции

```kotlin
inline fun transaction(crossinline block: () -> Unit) {
    fun executeTransaction() {
        database.beginTransaction()
        try {
            block()  // Вызов из вложенной функции
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
        // return  // Ошибка - нельзя
        userDao.update(user)
    }
}
```

#### 3. Лямбда сохраняется для отложенного выполнения

```kotlin
inline fun defer(crossinline action: () -> Unit): () -> Unit {
    return {
        action()  // Выполнится позже
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

### Сравнение: обычная лямбда vs crossinline

```kotlin
inline fun example(
    normalLambda: () -> Unit,           // Разрешен non-local return
    crossinline crossLambda: () -> Unit // Запрещен non-local return
) {
    // normalLambda - можно вызвать только напрямую
    normalLambda()  // OK
    // Thread { normalLambda() }.start()  // ERROR

    // crossLambda - можно вызвать откуда угодно
    crossLambda()  // OK
    Thread { crossLambda() }.start()  // OK
}

fun caller() {
    example(
        normalLambda = {
            return  // OK - выход из caller()
        },
        crossLambda = {
            return  // ERROR - non-local return запрещен
            return@example  // OK - labeled return
        }
    )
}
```

### Практические примеры

#### Пример 1: Async execution

```kotlin
inline fun asyncTask(crossinline onComplete: (Result) -> Unit) {
    CoroutineScope(Dispatchers.IO).launch {
        val result = performTask()

        withContext(Dispatchers.Main) {
            onComplete(result)
        }
    }
}

// Использование
fun loadData() {
    asyncTask { result ->
        // return  // Ошибка
        updateUI(result)
    }
    println("Loading started")  // Всегда выполнится
}
```

#### Пример 2: Event listener

```kotlin
inline fun onClick(crossinline listener: (View) -> Unit) {
    button.setOnClickListener { view ->
        listener(view)  // Вызов из другой лямбды
    }
}

fun setupButton() {
    onClick { view ->
        // return  // Ошибка
        toast("Clicked: ${view.id}")
    }
}
```

#### Пример 3: Try-catch wrapper

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
            // return  // Ошибка
            database.save(data)
        },
        catchBlock = { e ->
            // return  // Ошибка
            logError(e)
        }
    )
}
```

### Комбинация с noinline

```kotlin
inline fun process(
    immediateAction: () -> Unit,              // Inline, разрешен return
    crossinline deferredAction: () -> Unit,   // Inline, запрещен return
    noinline storedAction: () -> Unit         // Не inline, можно сохранить
) {
    // immediateAction - выполнить сразу
    immediateAction()

    // deferredAction - выполнить в callback
    Handler().post {
        deferredAction()
    }

    // storedAction - сохранить для позже
    val stored: () -> Unit = storedAction
    callbacks.add(stored)
}
```

### Ошибки без crossinline

```kotlin
// - ОШИБКА - лямбда с return в другом контексте
inline fun broken(action: () -> Unit) {
    Thread {
        action()  // ERROR: Can't inline 'action' here
    }.start()
}

// Compiler error:
// "Can't inline 'action' here: it may contain non-local returns.
// Add 'crossinline' modifier to parameter declaration 'action'"

//  ИСПРАВЛЕНО
inline fun fixed(crossinline action: () -> Unit) {
    Thread {
        action()  // OK
    }.start()
}
```

### Best Practices

**1. Используйте crossinline когда:**
- Лямбда вызывается в другом потоке
- Лямбда вызывается из вложенной функции
- Лямбда сохраняется для отложенного выполнения
- Лямбда передается в не-inline функцию

**2. НЕ используйте crossinline когда:**
- Лямбда вызывается напрямую в теле inline функции
- Хотите разрешить non-local returns

**3. Labeled returns всегда доступны:**
```kotlin
inline fun process(crossinline action: () -> Unit) {
    action()
}

fun test() {
    process {
        // return  // ERROR
        return@process  // OK - labeled return
    }
}
```

### Сравнительная таблица

| Модификатор | Non-local return | Можно сохранить | Можно передать | Вызов из других контекстов |
|-------------|------------------|-----------------|----------------|---------------------------|
| (обычная лямбда) | - Да | - Нет | - Нет | - Нет |
| `crossinline` | - Нет | - Нет | - Нет | - Да |
| `noinline` | - Нет | - Да | - Да | - Да |