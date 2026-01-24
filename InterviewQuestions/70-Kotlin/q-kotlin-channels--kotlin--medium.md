---
'---id': kotlin-026
title: Kotlin Channels / Каналы в Kotlin
aliases:
- Kotlin Channels
- Каналы в Kotlin
topic: kotlin
subtopics:
- channels
- concurrency
- coroutines
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-kotlin
related:
- c-coroutines
- c-kotlin
- c-stateflow
- q-coroutine-dispatchers--kotlin--medium
created: 2025-10-05
updated: 2025-11-09
tags:
- async
- channels
- concurrency
- coroutines
- difficulty/medium
- kotlin
anki_cards:
- slug: q-kotlin-channels--kotlin--medium-0-en
  language: en
  anki_id: 1768326291730
  synced_at: '2026-01-23T17:03:51.523563'
- slug: q-kotlin-channels--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326291756
  synced_at: '2026-01-23T17:03:51.524491'
---
# Вопрос (RU)
> Что вы знаете о каналах (Channels) в Kotlin?

---

# Question (EN)
> What do you know about Channels in Kotlin?

---

## Ответ (RU)

Отложенные значения (`Deferred`) предоставляют удобный способ передачи одного значения между корутинами. Каналы (`Channel`) предоставляют способ передачи потока значений. **Channel** — это примитив для асинхронного взаимодействия и передачи данных между отправителем (через `SendChannel`) и получателем (через `ReceiveChannel`), основанный на приостанавливающих операциях (без блокировки потоков). См. также [[c-kotlin]] и [[c-coroutines]].

### Основы Работы С Каналами

[Channel](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/index.html) концептуально очень похож на `BlockingQueue`. Одно ключевое отличие заключается в том, что вместо блокирующей операции `put` он имеет приостанавливающую операцию [send](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-send-channel/send.html), а вместо блокирующей операции `take` — приостанавливающую операцию [receive](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-receive-channel/receive.html).

```kotlin
val channel = Channel<Int>()

runBlocking {
    launch {
        // это может быть тяжелое вычисление или асинхронная логика, но мы просто отправим пять квадратов
        for (x in 1..5) channel.send(x * x)
    }
    // здесь мы выведем пять полученных целых чисел:
    repeat(5) { println(channel.receive()) }
    println("Done!")
}
```

Вывод этого кода:
```text
1
4
9
16
25
Done!
```

### Закрытие И Итерация По Каналам

В отличие от очереди, канал может быть закрыт, чтобы указать, что больше элементов не будет. На стороне получателя удобно использовать обычный цикл `for` для получения элементов из канала.

Концептуально, [close](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-send-channel/close.html) подобна отправке специального токена закрытия в канал. Итерация останавливается, как только этот токен закрытия получен, поэтому есть гарантия, что все ранее отправленные элементы до закрытия будут получены:

```kotlin
val channel = Channel<Int>()

runBlocking {
    launch {
        for (x in 1..5) channel.send(x * x)
        channel.close() // мы закончили отправку
    }
    // здесь мы выводим полученные значения используя цикл `for` (пока канал не закрыт)
    for (y in channel) println(y)
    println("Done!")
}
```

### Создание Производителей Каналов

Паттерн, когда корутина производит последовательность элементов, довольно распространен. Это часть паттерна **производитель-потребитель**, который часто встречается в параллельном коде. Вы можете абстрагировать такого производителя в функцию, которая принимает канал в качестве параметра, но это противоречит здравому смыслу, что результаты должны возвращаться из функций.

Существует удобный билдер корутин [produce](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html), который упрощает это на стороне производителя, и функция расширения [consumeEach](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/consume-each.html) (устаревшая в новых версиях, но часто встречается в примерах), которая заменяет цикл `for` на стороне потребителя:

```kotlin
fun CoroutineScope.produceSquares() = produce<Int> {
    for (x in 1..5) send(x * x)
}

runBlocking {
    val squares = produceSquares()
    squares.consumeEach { println(it) }
    println("Done!")
}
```

### Конвейеры

Конвейер — это паттерн, где одна корутина производит, возможно бесконечный, поток значений:

```kotlin
fun CoroutineScope.produceNumbers() = produce<Int> {
    var x = 1
    while (true) send(x++) // бесконечный поток целых чисел начиная с 1
}
```

А другая корутина или корутины потребляют этот поток, выполняя некоторую обработку и производя другие результаты. В примере ниже числа просто возводятся в квадрат:

```kotlin
fun CoroutineScope.square(numbers: ReceiveChannel<Int>): ReceiveChannel<Int> = produce {
    for (x in numbers) send(x * x)
}
```

Основной код запускает и соединяет весь конвейер (ниже предполагается выполнение внутри `runBlocking` или иного `CoroutineScope`):

```kotlin
runBlocking {
    val numbers = produceNumbers() // производит целые числа начиная с 1
    val squares = square(numbers) // возводит целые числа в квадрат
    repeat(5) {
        println(squares.receive()) // выводит первые пять
    }
    println("Done!") // мы закончили
    coroutineContext.cancelChildren() // отменяем дочерние корутины
}
```

### Буферизованные Каналы

Показанные до сих пор каналы не имели буфера. Небуферизованные каналы передают элементы, когда отправитель и получатель встречаются друг с другом (aka rendezvous). Если `send` вызван первым, то он приостанавливается до вызова `receive`, если `receive` вызван первым, он приостанавливается до вызова `send`.

Как фабричная функция [Channel()](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel.html), так и билдер [produce](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html) принимают необязательный параметр `capacity` для указания **размера буфера**. Буфер позволяет отправителям отправлять несколько элементов до приостановки, аналогично `BlockingQueue` с указанной емкостью, который блокируется, когда буфер заполнен.

Взгляните на поведение следующего кода (выполняется внутри `runBlocking`):

```kotlin
runBlocking {
    val channel = Channel<Int>(4) // создаем буферизованный канал
    val sender = launch { // запускаем корутину-отправителя
        repeat(10) {
            println("Sending $it") // выводим перед отправкой каждого элемента
            channel.send(it) // приостановится когда буфер заполнен
        }
    }
    // ничего не получаем... просто ждем....
    delay(1000)
    sender.cancel() // отменяем корутину-отправителя
}
```

Он выводит "Sending" **пять** раз используя буферизованный канал с емкостью **четыре**:
```text
Sending 0
Sending 1
Sending 2
Sending 3
Sending 4
```

Первые четыре элемента добавляются в буфер, и отправитель приостанавливается при попытке отправить пятый.

### Создание Каналов

Фабричная функция `Channel(capacity)` используется для создания каналов различных типов в зависимости от значения целочисленного параметра `capacity`:

- Когда `capacity` равен 0 — создается канал **rendezvous**. Этот канал вообще не имеет буфера. Элемент передается от отправителя к получателю только когда вызовы `send` и `receive` встречаются во времени (rendezvous), поэтому `send` приостанавливается до тех пор, пока другая корутина не вызовет `receive`, а `receive` приостанавливается до тех пор, пока другая корутина не вызовет `send`.

- Когда `capacity` равен `Channel.UNLIMITED` — создается канал с эффективно неограниченным буфером. Этот канал имеет буфер в виде связанного списка неограниченной емкости (ограниченной только доступной памятью). Отправка (`send`) в этот канал не приостанавливается из-за размера буфера.

- Когда `capacity` равен `Channel.CONFLATED` — создается **conflated** канал. Этот канал буферизует не более одного элемента и объединяет все последующие вызовы `send`, так что получатель всегда получает последний отправленный элемент. Ранее отправленные элементы "сливаются" — получается только последний отправленный элемент, в то время как ранее отправленные элементы **теряются**. Отправка (`send`) в этот канал не приостанавливается из-за размера буфера.

- Когда `capacity` положительный, но меньше `UNLIMITED` — создается канал на основе массива с указанной емкостью. Этот канал имеет буфер в виде массива фиксированной емкости `capacity`. Отправка приостанавливается только когда буфер заполнен, а получение приостанавливается только когда буфер пуст.

Буферизованные каналы могут быть настроены с дополнительным параметром `onBufferOverflow`. Он управляет поведением функции `send` канала при переполнении буфера:
- `SUSPEND` — по умолчанию, приостановить `send` при переполнении буфера до тех пор, пока не появится свободное место в буфере.
- `DROP_OLDEST` — не приостанавливать `send`, добавить последнее значение в буфер, удалить самое старое из буфера. Канал с `capacity = 1` и `onBufferOverflow = DROP_OLDEST` является **conflated** каналом.
- `DROP_LATEST` — не приостанавливать `send`, отбросить отправляемое значение, сохранить содержимое буфера нетронутым.

---

## Answer (EN)

Deferred values (`Deferred`) provide a convenient way to transfer a single value between coroutines. Channels (`Channel`) provide a way to transfer a stream of values. **Channel** is a primitive for asynchronous communication and data transfer between a sender (via `SendChannel`) and a receiver (via `ReceiveChannel`), based on suspending operations (non-blocking for threads). See also [[c-kotlin]] and [[c-coroutines]].

### Channel Basics

A [Channel](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/index.html) is conceptually very similar to `BlockingQueue`. One key difference is that instead of a blocking `put` operation it has a suspending [send](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-send-channel/send.html), and instead of a blocking `take` operation it has a suspending [receive](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-receive-channel/receive.html).

```kotlin
val channel = Channel<Int>()

runBlocking {
    launch {
        // this might be heavy CPU-consuming computation or async logic, we'll just send five squares
        for (x in 1..5) channel.send(x * x)
    }
    // here we print five received integers:
    repeat(5) { println(channel.receive()) }
    println("Done!")
}
```

The output of this code is:
```text
1
4
9
16
25
Done!
```

### Closing and Iteration over Channels

Unlike a queue, a channel can be closed to indicate that no more elements are coming. On the receiver side it is convenient to use a regular `for` loop to receive elements from the channel.

Conceptually, a [close](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-send-channel/close.html) is like sending a special close token to the channel. The iteration stops as soon as this close token is received, so there is a guarantee that all previously sent elements before the close are received:

```kotlin
val channel = Channel<Int>()

runBlocking {
    launch {
        for (x in 1..5) channel.send(x * x)
        channel.close() // we're done sending
    }
    // here we print received values using `for` loop (until the channel is closed)
    for (y in channel) println(y)
    println("Done!")
}
```

### Building Channel Producers

The pattern where a coroutine is producing a sequence of elements is quite common. This is a part of **producer-consumer** pattern that is often found in concurrent code. You could abstract such a producer into a function that takes a channel as its parameter, but this goes contrary to common sense that results must be returned from functions.

There is a convenient coroutine builder named [produce](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html) that makes it easy to do it right on the producer side, and an extension function [consumeEach](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/consume-each.html) (deprecated in newer versions but common in examples), that replaces a `for` loop on the consumer side:

```kotlin
fun CoroutineScope.produceSquares() = produce<Int> {
    for (x in 1..5) send(x * x)
}

runBlocking {
    val squares = produceSquares()
    squares.consumeEach { println(it) }
    println("Done!")
}
```

### Pipelines

A pipeline is a pattern where one coroutine is producing a, possibly infinite, stream of values:

```kotlin
fun CoroutineScope.produceNumbers() = produce<Int> {
    var x = 1
    while (true) send(x++) // infinite stream of integers starting from 1
}
```

And another coroutine or coroutines are consuming that stream, doing some processing, and producing some other results. In the example below, the numbers are just squared:

```kotlin
fun CoroutineScope.square(numbers: ReceiveChannel<Int>): ReceiveChannel<Int> = produce {
    for (x in numbers) send(x * x)
}
```

The main code starts and connects the whole pipeline (assumed to run inside `runBlocking` or another `CoroutineScope`):

```kotlin
runBlocking {
    val numbers = produceNumbers() // produces integers from 1 and on
    val squares = square(numbers) // squares integers
    repeat(5) {
        println(squares.receive()) // print first five
    }
    println("Done!") // we are done
    coroutineContext.cancelChildren() // cancel children coroutines
}
```

### Buffered Channels

The channels shown so far had no buffer. Unbuffered channels transfer elements when sender and receiver meet each other (aka rendezvous). If `send` is invoked first, then it is suspended until `receive` is invoked; if `receive` is invoked first, it is suspended until `send` is invoked.

Both [Channel()](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel.html) factory function and [produce](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html) builder take an optional `capacity` parameter to specify **buffer size**. Buffer allows senders to send multiple elements before suspending, similar to the `BlockingQueue` with a specified capacity, which blocks when buffer is full.

Take a look at the behavior of the following code (executed inside `runBlocking`):

```kotlin
runBlocking {
    val channel = Channel<Int>(4) // create buffered channel
    val sender = launch { // launch sender coroutine
        repeat(10) {
            println("Sending $it") // print before sending each element
            channel.send(it) // will suspend when buffer is full
        }
    }
    // don't receive anything... just wait....
    delay(1000)
    sender.cancel() // cancel sender coroutine
}
```

It prints "Sending" **five** times using a buffered channel with capacity of **four**:
```text
Sending 0
Sending 1
Sending 2
Sending 3
Sending 4
```

The first four elements are added to the buffer and the sender suspends when trying to send the fifth one.

### Creating Channels

The `Channel(capacity)` factory function is used to create channels of different kinds depending on the value of the `capacity` integer:

- When `capacity` is 0 — it creates a **rendezvous** channel. This channel does not have any buffer at all. An element is transferred from the sender to the receiver only when `send` and `receive` invocations meet in time (rendezvous), so `send` suspends until another coroutine invokes `receive`, and `receive` suspends until another coroutine invokes `send`.

- When `capacity` is `Channel.UNLIMITED` — it creates a channel with effectively unlimited buffer. This channel has a linked-list buffer of unlimited capacity (limited only by available memory). Sending (`send`) to this channel does not suspend due to buffer size.

- When `capacity` is `Channel.CONFLATED` — it creates a **conflated** channel. This channel buffers at most one element and conflates all subsequent `send` invocations, so that the receiver always gets the last element sent. Previously sent elements are conflated — only the last sent element is received, while earlier elements **are lost**. Sending (`send`) to this channel does not suspend due to buffer size.

- When `capacity` is positive but less than `UNLIMITED` — it creates an array-based channel with the specified capacity. This channel has an array buffer of a fixed `capacity`. Sending suspends only when the buffer is full, and receiving suspends only when the buffer is empty.

Buffered channels can be configured with an additional `onBufferOverflow` parameter. It controls the behaviour of the channel's `send` function on buffer overflow:
- `SUSPEND` — the default, suspend `send` on buffer overflow until there is free space in the buffer.
- `DROP_OLDEST` — do not suspend the `send`, add the latest value to the buffer, drop the oldest one from the buffer. A channel with `capacity = 1` and `onBufferOverflow = DROP_OLDEST` is a **conflated** channel.
- `DROP_LATEST` — do not suspend the `send`, drop the value that is being sent, keep the buffer contents intact.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия каналов от подхода в Java?
- Когда вы бы использовали каналы на практике?
- Какие распространенные ошибки и подводные камни следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Документация по каналам корутин Kotlin: https://kotlinlang.org/docs/coroutines-channels.html
- Channel API Reference: https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/index.html

## References

- [Kotlin Coroutines Channels Documentation](https://kotlinlang.org/docs/coroutines-channels.html)
- [Channel API Reference](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/index.html)

## Связанные Вопросы (RU)

- [[q-kotlin-flow-basics--kotlin--medium]]
- [[q-kotlin-coroutines-introduction--kotlin--medium]]

## Related Questions

- [[q-kotlin-flow-basics--kotlin--medium]]
- [[q-kotlin-coroutines-introduction--kotlin--medium]]
