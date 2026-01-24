---
anki_cards:
- slug: q-kotlin-coroutines-introduction--kotlin--medium-0-en
  language: en
  anki_id: 1768326283954
  synced_at: '2026-01-23T17:03:50.828423'
- slug: q-kotlin-coroutines-introduction--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326283981
  synced_at: '2026-01-23T17:03:50.830465'
---
---
---
---\
id: kotlin-009
title: "Kotlin Coroutines Introduction / Введение в корутины Kotlin"
aliases: ["Kotlin Coroutines Introduction", "Введение в корутины Kotlin"]

# Classification
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [async, concurrency, coroutines, difficulty/medium, kotlin, structured-concurrency]
---\
# Вопрос (RU)
> Что такое корутины в Kotlin?

# Question (EN)
> What are coroutines in Kotlin?

## Ответ (RU)

Корутина — это паттерн проектирования для работы с асинхронностью и конкурентностью, который вы можете использовать (в том числе на Android) для упрощения кода, выполняющегося асинхронно. Корутины были добавлены в Kotlin в версии 1.3 и основаны на установленных концепциях из других языков.

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

По сути, корутины — это легковесные единицы работы, которые выполняются на потоках, но не являются потоками сами по себе. Они запускаются с помощью *билдера корутин* `launch` в контексте некоторого `CoroutineScope`. Здесь мы запускаем новую корутину в `GlobalScope`, что означает, что время жизни новой корутины ограничено только временем жизни всего приложения.

Основная идея корутин заключается в том, что функция может приостановить свое выполнение в некоторой точке и возобновить его позже. Одно из преимуществ корутин заключается в том, что для разработчика написание неблокирующего кода по сути то же самое, что написание блокирующего кода. Модель программирования визуально почти не меняется.

Возьмем, к примеру, следующий код:

```kotlin
fun postItem(scope: CoroutineScope, item: Item) {
    scope.launch {
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

При запуске этого кода в подходящей области видимости и с корректным диспетчером (например, `Dispatchers.IO` для сетевого запроса) длительная операция выполнится без блокировки основного потока. `preparePost` — это `приостанавливаемая функция` (`suspending function`), отсюда ключевое слово `suspend` перед ней. Это означает, как сказано выше, что функция может выполнить часть работы, приостановить выполнение и возобновить его в какой-то момент времени.

- Сигнатура функции в остальном остается привычной. Единственное отличие — добавление к ней `suspend`. При этом возвращаемый тип остается тем типом, который мы хотим вернуть.
- Код по-прежнему пишется так, как если бы мы писали синхронный код, сверху вниз, без необходимости какого-либо специального синтаксиса, кроме использования функции `launch`, которая по сути запускает корутину.
- Модель программирования и многие знакомые конструкции остаются теми же. Мы можем продолжать использовать циклы, обработку исключений и т.д., и нет необходимости изучать полный набор новых API.
- Подход платформенно-независим. Нацелены ли мы на JVM, JavaScript или другую платформу, высокоуровневый код, который мы пишем, может быть одинаковым. Под капотом компилятор заботится об адаптации реализации к каждой платформе.

### Структурированный Параллелизм

Все еще есть что желать для практического использования корутин. Когда мы используем `GlobalScope.launch`, мы создаем корутину верхнего уровня. Хотя она легковесна, она все еще потребляет некоторые ресурсы памяти пока работает. Если мы забудем сохранить ссылку на вновь запущенную корутину, она все еще выполняется. Что если код в корутине зависнет (например, мы ошибочно задержались слишком долго), что если мы запустили слишком много корутин и исчерпали память? Необходимость вручную хранить ссылки на все запущенные корутины и присоединять их подвержена ошибкам.

Есть лучшее решение. Мы можем использовать структурированный параллелизм в нашем коде. Вместо запуска корутин в `GlobalScope`, как мы обычно делаем с потоками (потоки всегда глобальны), мы можем запускать корутины в конкретной области видимости выполняемой нами операции.

## Answer (EN)

A coroutine is a design pattern for dealing with asynchrony and concurrency that you can use (including on Android) to simplify code that executes asynchronously. Coroutines were added to Kotlin in version 1.3 and are based on established concepts from other languages.

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

Conceptually, coroutines are lightweight units of work that execute on threads; they are not threads themselves. They are launched with the `launch` *coroutine builder* in the context of some `CoroutineScope`. Here we are launching a new coroutine in the `GlobalScope`, meaning that the lifetime of the new coroutine is limited only by the lifetime of the whole application.

The global idea behind coroutines is that a function can suspend its execution at some point and resume later on. One of the benefits of coroutines is that for the developer, writing non-blocking code is essentially the same as writing blocking code. The programming model visually doesn't really change.

Take for instance the following code:

```kotlin
fun postItem(scope: CoroutineScope, item: Item) {
    scope.launch {
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

When this is run within an appropriate scope and dispatcher (for example, `Dispatchers.IO` for a network request), this code will perform a long-running operation without blocking the main thread. `preparePost` is what's called a `suspending function`, thus the keyword `suspend` prefixing it. As stated above, this means that the function can execute, pause execution, and resume at some point in time.

- The function signature otherwise remains familiar. The only difference is `suspend` being added to it. The return type remains the type we want to be returned.
- The code is still written as if we were writing synchronous code, top-down, without the need of any special syntax beyond using a function such as `launch` which essentially kicks off the coroutine.
- The programming model and many familiar constructs remain the same. We can continue to use loops, exception handling, etc., and there's no need to learn a completely new set of APIs.
- It is platform independent at the concept level. Whether we target JVM, JavaScript or any other platform, the high-level code we write can look the same. Under the covers the compiler and runtime take care of adapting it to each platform.

### Structured Concurrency

There is still something to be desired for practical usage of coroutines. When we use `GlobalScope.launch`, we create a top-level coroutine. Even though it is light-weight, it still consumes some memory resources while it runs. If we forget to keep a reference to the newly launched coroutine, it still runs. What if the code in the coroutine hangs (for example, we erroneously delay for too long), what if we launched too many coroutines and ran out of memory? Having to manually keep references to all the launched coroutines and join them is error-prone.

There is a better solution. We can use structured concurrency in our code. Instead of launching coroutines in the `GlobalScope`, just like we usually do with threads (threads are always global), we can launch coroutines in the specific scope of the operation we are performing.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия корутин от подхода в Java?
- Когда вы бы использовали корутины на практике?
- Каковы распространенные подводные камни при работе с корутинами?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Обзор корутин Kotlin](https://kotlinlang.org/docs/reference/coroutines-overview.html)
- [Основы корутин Kotlin](https://kotlinlang.org/docs/coroutines-basics.html)
- [Руководство по корутинам в Android](https://developer.android.com/kotlin/coroutines)
- [Асинхронное программирование](https://kotlinlang.org/docs/tutorials/coroutines/async-programming.html)

## References

- [Kotlin Coroutines Overview](https://kotlinlang.org/docs/reference/coroutines-overview.html)
- [Kotlin Coroutines Basics](https://kotlinlang.org/docs/coroutines-basics.html)
- [Android Coroutines Guide](https://developer.android.com/kotlin/coroutines)
- [Async Programming](https://kotlinlang.org/docs/tutorials/coroutines/async-programming.html)

## Связанные Вопросы (RU)

### Связанные (Средний уровень)
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Корутины
- [[q-deferred-async-patterns--kotlin--medium]] - Корутины
- [[q-coroutine-context-explained--kotlin--medium]] - Корутины
- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]] - Корутины

### Продвинутые (Сложнее)
- [[q-actor-pattern--kotlin--hard]] - Корутины
- [[q-fan-in-fan-out--kotlin--hard]] - Корутины
- [[q-structured-concurrency-patterns--kotlin--hard]] - Структурированный параллелизм

### Предварительные (Проще)
- [[q-what-is-coroutine--kotlin--easy]] - Базовые концепции корутин
- [[q-coroutine-builders-basics--kotlin--easy]] - launch, async, runBlocking
- [[q-coroutine-scope-basics--kotlin--easy]] - Основы CoroutineScope
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - delay() против `Thread`.sleep()
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Корутины против потоков на Android

### Связанные (Тот Же уровень)
- [[q-suspend-functions-basics--kotlin--easy]] - Понимание suspend-функций
- [[q-coroutine-dispatchers--kotlin--medium]] - Обзор диспетчеров корутин
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope против `CoroutineContext`
- [[q-coroutine-context-explained--kotlin--medium]] - Объяснение `CoroutineContext`
- [[q-coroutine-exception-handling--kotlin--medium]] - Обработка исключений
- [[q-structured-concurrency-kotlin--kotlin--medium]] - Структурированный параллелизм
- [[q-lifecyclescope-viewmodelscope--kotlin--medium]] - Области корутин и жизненный цикл Android
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Параллельные API-запросы

### Связанные Темы
- [[q-kotlin-channels--kotlin--medium]] - Каналы для коммуникации
- [[q-kotlin-flow-basics--kotlin--medium]] - `Flow` и реактивные потоки

## Related Questions

### Related (Medium)
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Coroutines
- [[q-deferred-async-patterns--kotlin--medium]] - Coroutines
- [[q-coroutine-context-explained--kotlin--medium]] - Coroutines
- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-actor-pattern--kotlin--hard]] - Coroutines
- [[q-fan-in-fan-out--kotlin--hard]] - Coroutines
- [[q-structured-concurrency-patterns--kotlin--hard]] - Structured concurrency

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - Basic coroutine concepts
- [[q-coroutine-builders-basics--kotlin--easy]] - launch, async, runBlocking
- [[q-coroutine-scope-basics--kotlin--easy]] - CoroutineScope fundamentals
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - delay() vs `Thread`.sleep()
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Coroutines vs Threads on Android

### Related (Same Level)
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - `Coroutine` dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs `CoroutineContext`
- [[q-coroutine-context-explained--kotlin--medium]] - `CoroutineContext` explained
- [[q-coroutine-exception-handling--kotlin--medium]] - Exception handling
- [[q-structured-concurrency-kotlin--kotlin--medium]] - Structured concurrency
- [[q-lifecyclescope-viewmodelscope--kotlin--medium]] - Android lifecycle scopes
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Parallel API calls

### Related Topics
- [[q-kotlin-channels--kotlin--medium]] - Channels for communication
- [[q-kotlin-flow-basics--kotlin--medium]] - `Flow` and reactive streams

Также см. концепции: [[c-kotlin]], [[c-coroutines]].
