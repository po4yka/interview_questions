---
id: 20251005-222647
title: "Kotlin Coroutines Introduction / Введение в корутины Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, concurrency, async, structured-concurrency]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, coroutines, async, concurrency, structured-concurrency, difficulty/medium]
---
# Question (EN)
> What are coroutines in Kotlin?
# Вопрос (RU)
> Что такое корутины в Kotlin?

---

## Answer (EN)

A coroutine is a concurrency design pattern that you can use on Android to simplify code that executes asynchronously. Coroutines were added to Kotlin in version 1.3 and are based on established concepts from other languages.

On Android, coroutines help to manage long-running tasks that might otherwise block the main thread and cause your app to become unresponsive.

Coroutines offer many benefits over other asynchronous solutions, including the following:

- **Lightweight**. You can run many coroutines on a single thread due to support for suspension, which doesn't block the thread where the coroutine is running. Suspending saves memory over blocking while supporting many concurrent operations.
- **Fewer memory leaks**. Use structured concurrency to run operations within a scope.
- **Built-in cancellation support**. Cancellation is propagated automatically through the running coroutine hierarchy.
- **Jetpack integration**. Many Jetpack libraries include extensions that provide full coroutines support. Some libraries also provide their own coroutine scope that you can use for structured concurrency.

### Example

```kotlin
import kotlinx.coroutines.*

fun main() {
    GlobalScope.launch { // launch a new coroutine in background and continue
        delay(1000L) // non-blocking delay for 1 second (default time unit is ms)
        println("World!") // print after delay
    }
    println("Hello,") // main thread continues while coroutine is delayed
    Thread.sleep(2000L) // block main thread for 2 seconds to keep JVM alive
}

// Output:
// Hello,
// World!
```

Essentially, coroutines are light-weight threads. They are launched with `launch` *coroutine builder* in a context of some `CoroutineScope`. Here we are launching a new coroutine in the `GlobalScope`, meaning that the lifetime of the new coroutine is limited only by the lifetime of the whole application.

The global idea behind coroutines is that a function can suspend its execution at some point and resume later on. One of the benefits however of coroutines is that when it comes to the developer, writing non-blocking code is essentially the same as writing blocking code. The programming model in itself doesn't really change.

Take for instance the following code:

```kotlin
fun postItem(item: Item) {
    launch {
        val token = preparePost()
        val post = submitPost(token, item)
        processPost(post)
    }
}

suspend fun preparePost(): Token {
    // makes a request and suspends the coroutine
    return suspendCoroutine { /* ... */ }
}
```

This code will launch a long-running operation without blocking the main thread. The `preparePost` is what's called a `suspendable function`, thus the keyword `suspend` prefixing it. What this means as stated above, is that the function will execute, pause execution and resume at some point in time.

- The function signature remains exactly the same. The only difference is `suspend` being added to it. The return type however is the type we want to be returned.
- The code is still written as if we were writing synchronous code, top-down, without the need of any special syntax, beyond the use of a function called `launch` which essentially kicks-off the coroutine
- The programming model and APIs remain the same. We can continue to use loops, exception handling, etc. and there's no need to learn a complete set of new APIs
- It is platform independent. Whether we targeting JVM, JavaScript or any other platform, the code we write is the same. Under the covers the compiler takes care of adapting it to each platform.

### Structured concurrency

There is still something to be desired for practical usage of coroutines. When we use `GlobalScope.launch`, we create a top-level coroutine. Even though it is light-weight, it still consumes some memory resources while it runs. If we forget to keep a reference to the newly launched coroutine, it still runs. What if the code in the coroutine hangs (for example, we erroneously delay for too long), what if we launched too many coroutines and ran out of memory? Having to manually keep references to all the launched coroutines and join them is error-prone.

There is a better solution. We can use structured concurrency in our code. Instead of launching coroutines in the `GlobalScope`, just like we usually do with threads (threads are always global), we can launch coroutines in the specific scope of the operation we are performing.

## Ответ (RU)

Корутина — это паттерн проектирования параллелизма, который вы можете использовать на Android для упрощения кода, выполняющегося асинхронно. Корутины были добавлены в Kotlin в версии 1.3 и основаны на установленных концепциях из других языков.

На Android корутины помогают управлять долго выполняющимися задачами, которые в противном случае могли бы заблокировать главный поток и сделать ваше приложение неотзывчивым.

Корутины предлагают множество преимуществ перед другими асинхронными решениями, включая следующие:

- **Легковесность**. Вы можете запускать множество корутин в одном потоке благодаря поддержке приостановки, которая не блокирует поток, в котором выполняется корутина. Приостановка экономит память по сравнению с блокировкой, поддерживая при этом множество параллельных операций.
- **Меньше утечек памяти**. Используйте структурированный параллелизм для выполнения операций в пределах области видимости.
- **Встроенная поддержка отмены**. Отмена автоматически распространяется по всей иерархии выполняющихся корутин.
- **Интеграция с Jetpack**. Многие библиотеки Jetpack включают расширения, обеспечивающие полную поддержку корутин. Некоторые библиотеки также предоставляют свою собственную область видимости корутин, которую вы можете использовать для структурированного параллелизма.

### Пример

```kotlin
import kotlinx.coroutines.*

fun main() {
    GlobalScope.launch { // запускаем новую корутину в фоне и продолжаем
        delay(1000L) // неблокирующая задержка на 1 секунду (по умолчанию время в мс)
        println("World!") // выводим после задержки
    }
    println("Hello,") // главный поток продолжает работу пока корутина задержана
    Thread.sleep(2000L) // блокируем главный поток на 2 секунды чтобы JVM оставалась активной
}

// Вывод:
// Hello,
// World!
```

По сути, корутины — это легковесные потоки. Они запускаются с помощью *билдера корутин* `launch` в контексте некоторого `CoroutineScope`. Здесь мы запускаем новую корутину в `GlobalScope`, что означает, что время жизни новой корутины ограничено только временем жизни всего приложения.

Основная идея корутин заключается в том, что функция может приостановить свое выполнение в некоторой точке и возобновить его позже. Однако одно из преимуществ корутин заключается в том, что для разработчика написание неблокирующего кода по сути то же самое, что написание блокирующего кода. Сама модель программирования на самом деле не меняется.

Возьмем, к примеру, следующий код:

```kotlin
fun postItem(item: Item) {
    launch {
        val token = preparePost()
        val post = submitPost(token, item)
        processPost(post)
    }
}

suspend fun preparePost(): Token {
    // делает запрос и приостанавливает корутину
    return suspendCoroutine { /* ... */ }
}
```

Этот код запустит долго выполняющуюся операцию без блокировки главного потока. `preparePost` — это то, что называется `приостанавливаемой функцией`, отсюда ключевое слово `suspend` перед ней. Это означает, как сказано выше, что функция будет выполняться, приостановит выполнение и возобновит его в какой-то момент времени.

- Сигнатура функции остается точно такой же. Единственное отличие — добавление к ней `suspend`. Тип возвращаемого значения, однако, это тот тип, который мы хотим вернуть.
- Код по-прежнему пишется так, как если бы мы писали синхронный код, сверху вниз, без необходимости какого-либо специального синтаксиса, кроме использования функции `launch`, которая по сути запускает корутину
- Модель программирования и API остаются прежними. Мы можем продолжать использовать циклы, обработку исключений и т.д., и нет необходимости изучать полный набор новых API
- Это независимо от платформы. Нацелены ли мы на JVM, JavaScript или любую другую платформу, код, который мы пишем, одинаков. Под капотом компилятор заботится об адаптации его к каждой платформе.

### Структурированный параллелизм

Все еще есть что желать для практического использования корутин. Когда мы используем `GlobalScope.launch`, мы создаем корутину верхнего уровня. Хотя она легковесна, она все еще потребляет некоторые ресурсы памяти пока работает. Если мы забудем сохранить ссылку на вновь запущенную корутину, она все еще выполняется. Что если код в корутине зависнет (например, мы ошибочно задержались слишком долго), что если мы запустили слишком много корутин и исчерпали память? Необходимость вручную хранить ссылки на все запущенные корутины и присоединять их подвержена ошибкам.

Есть лучшее решение. Мы можем использовать структурированный параллелизм в нашем коде. Вместо запуска корутин в `GlobalScope`, как мы обычно делаем с потоками (потоки всегда глобальны), мы можем запускать корутины в конкретной области видимости выполняемой нами операции.

---

## References
- [Kotlin Coroutines Overview](https://kotlinlang.org/docs/reference/coroutines-overview.html)
- [Kotlin Coroutines Basics](https://kotlinlang.org/docs/reference/coroutines/basics.html)
- [Android Coroutines Guide](https://developer.android.com/kotlin/coroutines)
- [Async Programming](https://kotlinlang.org/docs/tutorials/coroutines/async-programming.html)

## Related Questions
- [[q-kotlin-channels--kotlin--medium]]
- [[q-kotlin-flow-basics--kotlin--medium]]
