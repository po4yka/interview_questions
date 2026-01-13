---
---
---\
id: kotlin-078
title: "Channel Closing and Completion / Закрытие и завершение каналов"
aliases: ["Channel Closing and Completion", "Закрытие и завершение каналов"]

# Classification
topic: kotlin
subtopics: [channels, cleanup, coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Channel Lifecycle Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-channels-basics-types--kotlin--medium, q-produce-actor-builders--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [channels, cleanup, closing, completion, coroutines, difficulty/medium, kotlin]
---\
# Вопрос (RU)
> Как правильно закрывать и завершать каналы? Объясните close(), cancel(), разницу между ClosedSendChannelException и ClosedReceiveChannelException и лучшие практики очистки ресурсов.

# Question (EN)
> How do you properly close and complete channels? Explain close(), cancel(), the difference between ClosedSendChannelException and ClosedReceiveChannelException, and best practices for cleanup.

---

## Ответ (RU)

Правильное управление жизненным циклом каналов критически важно для предотвращения утечек ресурсов, корректной обработки ошибок и управляемого завершения работы корутинных систем.

### Понимание Состояний Канала

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Канал имеет три основных состояния
fun channelStates() = runBlocking {
    val channel = Channel<Int>()

    // 1. АКТИВЕН: можно отправлять и получать
    println("isClosedForSend: ${channel.isClosedForSend}") // false
    println("isClosedForReceive: ${channel.isClosedForReceive}") // false

    channel.send(1)

    // 2. ЗАКРЫТ ДЛЯ ОТПРАВКИ: новые send() запрещены, но можно получать
    channel.close()
    println("isClosedForSend: ${channel.isClosedForSend}") // true
    println("isClosedForReceive: ${channel.isClosedForReceive}") // false

    // Все еще можно получить буферизованные значения
    println("Received: ${channel.receive()}") // 1

    // 3. ЗАКРЫТ ДЛЯ ПОЛУЧЕНИЯ: все значения прочитаны
    println("isClosedForReceive: ${channel.isClosedForReceive}") // true
}
```

Кратко:
- isClosedForSend == true: новые send/trySend недопустимы, но чтение возможно, пока есть элементы.
- isClosedForReceive == true: канал полностью исчерпан, дальнейшие receive() приведут к ClosedReceiveChannelException.

### close() Vs cancel() Vs close(cause)

Ключевые идеи:
- close(): мягкое (graceful) завершение, сигнал "значений больше не будет"; уже отправленные элементы остаются доступны для чтения.
- cancel(cause): немедленная отмена с причиной; операции send/receive возобновляются с исключением; на сохранность буфера полагаться нельзя.
- close(cause): как close(), но дополнительно фиксирует причину завершения для диагностики/проброса; эту причину можно получить через getCompletionExceptionOrNull().

```kotlin
class ChannelClosingMethodsRu(private val scope: CoroutineScope) {

    // close(): изящное завершение
    suspend fun closeExample() = coroutineScope {
        val channel = Channel<Int>(capacity = 10)

        val producer = launch {
            try {
                for (i in 1..5) {
                    channel.send(i)
                }
            } finally {
                channel.close() // Сигнал, что значений больше не будет
                println("Channel closed normally")
            }
        }

        // Потребитель читает все значения
        for (value in channel) {
            println("Received: $value")
        }
        producer.join()
        println("All values consumed")
    }

    // cancel(): немедленная отмена с причиной, буфер может быть отброшен
    suspend fun cancelExample() = coroutineScope {
        val channel = Channel<Int>(capacity = 10)

        val producerJob = launch {
            try {
                for (i in 1..100) {
                    channel.send(i)
                    delay(100)
                }
            } catch (e: CancellationException) {
                println("Producer cancelled")
                throw e
            }
        }

        delay(250)

        // Останавливаем продюсера и канал
        producerJob.cancel()
        channel.cancel()

        println("Channel cancelled")
    }

    // close(cause): закрытие с причиной для диагностики
    suspend fun closeWithCauseExample() = coroutineScope {
        val channel = Channel<Int>()

        val producer = launch {
            try {
                repeat(10) {
                    if (it == 5) {
                        throw IllegalStateException("Something went wrong")
                    }
                    channel.send(it)
                }
            } catch (e: Exception) {
                channel.close(e) // Закрываем с причиной
            }
        }

        for (value in channel) {
            println("Received: $value")
        }

        producer.join()

        // ВАЖНО: причину берем через getCompletionExceptionOrNull()
        val cause = channel.getCompletionExceptionOrNull()
        if (cause != null) {
            println("Channel closed due to: ${cause.message}")
        }
    }
}
```

### Исключения: ClosedSendChannelException Vs ClosedReceiveChannelException

```kotlin
class ChannelExceptionsRu(private val scope: CoroutineScope) {

    // ClosedSendChannelException: send() в закрытый канал
    suspend fun closedSendExample() = coroutineScope {
        val channel = Channel<Int>()

        channel.close()

        try {
            channel.send(1) // Бросит ClosedSendChannelException
        } catch (e: ClosedSendChannelException) {
            println("Cannot send to closed channel: $e")
        }

        // Безопасная альтернатива: trySend
        val result = channel.trySend(1)
        if (result.isFailure) {
            println("trySend failed; closed=${result.isClosed}")
        }
    }

    // ClosedReceiveChannelException: receive() из пустого закрытого канала
    suspend fun closedReceiveExample() = coroutineScope {
        val channel = Channel<Int>()

        channel.send(1)
        channel.close()

        // Первое чтение успешно
        println("First: ${channel.receive()}") // 1

        try {
            // Второе чтение — элементов нет
            channel.receive() // ClosedReceiveChannelException
        } catch (e: ClosedReceiveChannelException) {
            println("No more values: $e")
        }

        // Безопасная альтернатива: tryReceive
        val result = channel.tryReceive()
        if (result.isFailure) {
            println("tryReceive failed; closed=${result.isClosed}")
        }

        // Рекомендуется: итерация for (x in channel)
        val channel2 = Channel<Int>()
        channel2.send(1)
        channel2.send(2)
        channel2.close()

        for (value in channel2) {
            println(value) // Без исключений, цикл завершится по закрытию канала
        }
    }

    // Обработка причины закрытия (не полагаться на e.cause, использовать состояние канала)
    suspend fun closeCauseExample() = coroutineScope {
        val channel = Channel<String>()

        val producer = launch {
            try {
                channel.send("First")
                throw java.io.IOException("Network error")
            } catch (e: Exception) {
                channel.close(e) // Пробрасываем ошибку как причину завершения
            }
        }

        for (value in channel) {
            println("Received: $value")
        }

        producer.join()

        val completionCause = channel.getCompletionExceptionOrNull()
        if (completionCause is java.io.IOException) {
            println("Channel closed due to network error: ${completionCause.message}")
        }
    }
}
```

### Паттерны Producer-consumer С Корректной Очисткой

```kotlin
class ProperCleanupPatternsRu(private val scope: CoroutineScope) {

    // Паттерн 1: продюсер закрывает канал
    suspend fun producerClosesChannel() = coroutineScope {
        val channel = Channel<Int>()

        val producer = launch {
            try {
                for (i in 1..10) {
                    channel.send(i)
                }
            } catch (e: Exception) {
                println("Producer error: $e")
            } finally {
                channel.close()
                println("Producer closed channel")
            }
        }

        for (value in channel) {
            println("Processed: $value")
        }

        producer.join()
    }

    // Паттерн 2: несколько продюсеров, координатор закрывает канал
    suspend fun multipleProducersPattern() = coroutineScope {
        val channel = Channel<Int>(capacity = 100)

        val producers = List(3) { id ->
            launch {
                try {
                    repeat(10) {
                        channel.send(id * 100 + it)
                    }
                } catch (e: ClosedSendChannelException) {
                    println("Producer $id: Channel already closed")
                }
            }
        }

        producers.joinAll()

        channel.close()
        println("All producers finished, channel closed")

        for (value in channel) {
            println("Received: $value")
        }
    }

    // Паттерн 3: потребитель завершает работу раньше и инициирует отмену
    suspend fun consumerCancelsEarly() = coroutineScope {
        val channel = Channel<Int>()

        val producer = launch {
            try {
                var i = 0
                while (true) {
                    channel.send(i++)
                    delay(100)
                }
            } catch (e: ClosedSendChannelException) {
                println("Channel closed by consumer")
            } finally {
                println("Producer cleaning up")
            }
        }

        val consumer = launch {
            repeat(5) {
                println("Received: ${channel.receive()}")
            }
            channel.cancel()
            producer.cancel()
        }

        consumer.join()
    }

    // Паттерн 4: закрытие по тайм-ауту
    suspend fun timeoutBasedClosure() = coroutineScope {
        val channel = Channel<Int>()

        val producer = launch {
            try {
                var i = 0
                while (true) {
                    channel.send(i++)
                    delay(50)
                }
            } catch (e: ClosedSendChannelException) {
                println("Channel closed")
            }
        }

        try {
            withTimeout(500) {
                for (value in channel) {
                    println("Received: $value")
                }
            }
        } catch (e: TimeoutCancellationException) {
            println("Timeout reached")
        } finally {
            channel.cancel()
            producer.cancel()
        }
    }
}
```

### Использование Produce Builder (рекомендуется)

```kotlin
class ProduceBuilderPatternRu {

    // produce автоматически закрывает канал при завершении корутины-продюсера
    fun produceExample() = runBlocking {
        val numbers = produce {
            for (i in 1..10) {
                send(i)
            }
            // Явный close() не нужен
        }

        for (num in numbers) {
            println(num)
        }
    }

    // produce с обработкой исключений: канал закрывается с причиной
    fun produceWithException() = runBlocking {
        val numbers = produce {
            for (i in 1..10) {
                if (i == 5) throw IllegalStateException("Error at 5")
                send(i)
            }
        }

        try {
            for (num in numbers) {
                println(num)
            }
        } catch (e: ClosedReceiveChannelException) {
            // Исключение при receive() сигнализирует о закрытии; причину читаем из канала
            val cause = numbers.getCompletionExceptionOrNull()
            println("Channel closed due to: ${cause?.message}")
        }
    }

    // produce с отменой
    fun produceWithCancellation() = runBlocking {
        val numbers = produce {
            var i = 0
            try {
                while (true) {
                    send(i++)
                    delay(100)
                }
            } finally {
                println("Producer cancelled after $i items")
            }
        }

        repeat(5) {
            println(numbers.receive())
        }

        numbers.cancel() // Отмена продюсера и закрытие канала
    }
}
```

### Продвинутые Сценарии Очистки

```kotlin
class AdvancedCleanupRu(private val scope: CoroutineScope) {

    // Работа с внешними ресурсами
    suspend fun channelWithResources() = coroutineScope {
        class DatabaseConnection : AutoCloseable {
            fun query(sql: String): List<Int> = listOf(1, 2, 3)
            override fun close() {
                println("Database connection closed")
            }
        }

        val channel = Channel<Int>()

        val producer = launch {
            DatabaseConnection().use { db ->
                try {
                    val results = db.query("SELECT * FROM data")
                    for (result in results) {
                        channel.send(result)
                    }
                } finally {
                    channel.close()
                    println("Channel closed")
                }
            }
        }

        for (value in channel) {
            println("Received: $value")
        }

        producer.join()
    }

    // Очистка в pipeline
    suspend fun pipelineCleanup() = coroutineScope {
        val input = Channel<Int>()
        val output = Channel<String>()

        val producer = launch {
            try {
                for (i in 1..10) {
                    input.send(i)
                }
            } finally {
                input.close()
                println("Input closed")
            }
        }

        val processor = launch {
            try {
                for (value in input) {
                    output.send("Processed: $value")
                }
            } finally {
                output.close()
                println("Output closed")
            }
        }

        for (result in output) {
            println(result)
        }

        joinAll(producer, processor)
        println("Pipeline complete")
    }

    // Проброс ошибок по pipeline
    suspend fun errorPropagation() = coroutineScope {
        val channel1 = Channel<Int>()
        val channel2 = Channel<String>()

        val stage1 = launch {
            try {
                for (i in 1..10) {
                    if (i == 5) throw RuntimeException("Stage 1 error")
                    channel1.send(i)
                }
                channel1.close()
            } catch (e: Exception) {
                channel1.close(e)
            }
        }

        val stage2 = launch {
            try {
                for (value in channel1) {
                    channel2.send("Stage2: $value")
                }
                channel2.close()
            } catch (e: Exception) {
                val cause = channel1.getCompletionExceptionOrNull() ?: e
                channel2.close(cause)
            }
        }

        try {
            for (result in channel2) {
                println(result)
            }
        } catch (e: ClosedReceiveChannelException) {
            val cause = channel2.getCompletionExceptionOrNull()
            println("Consumer received error: ${cause?.message}")
        }

        joinAll(stage1, stage2)
    }
}
```

### Тестирование Закрытия Каналов

```kotlin
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlin.test.assertFailsWith

class ChannelClosureTestsRu {

    @Test
    fun `test channel closes after all values sent`() = runTest {
        val channel = Channel<Int>()

        launch {
            channel.send(1)
            channel.send(2)
            channel.close()
        }

        val values = mutableListOf<Int>()
        for (value in channel) {
            values.add(value)
        }

        assertEquals(listOf(1, 2), values)
        assertTrue(channel.isClosedForReceive)
    }

    @Test
    fun `test send to closed channel throws exception`() = runTest {
        val channel = Channel<Int>()
        channel.close()

        assertFailsWith<ClosedSendChannelException> {
            channel.send(1)
        }
    }

    @Test
    fun `test receive from empty closed channel throws exception`() = runTest {
        val channel = Channel<Int>()
        channel.close()

        assertFailsWith<ClosedReceiveChannelException> {
            channel.receive()
        }
    }

    @Test
    fun `test close with cause propagates error`() = runTest {
        val channel = Channel<Int>()
        val error = IllegalStateException("Test error")

        channel.close(error)

        assertFailsWith<ClosedReceiveChannelException> {
            channel.receive()
        }

        val completionCause = channel.getCompletionExceptionOrNull()
        assertEquals(error, completionCause)
    }

    @Test
    fun `test trySend on closed channel returns failure`() = runTest {
        val channel = Channel<Int>()
        channel.close()

        val result = channel.trySend(1)

        assertTrue(result.isFailure)
        assertTrue(result.isClosed)
    }
}
```

### Лучшие Практики И Анти-паттерны

```kotlin
class BestPracticesRu(private val scope: CoroutineScope) {

    // ХОРОШО: закрывать канал в finally в ответственной корутине-продюсере
    suspend fun goodClosePattern() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            try {
                repeat(10) {
                    channel.send(it)
                }
            } finally {
                channel.close()
            }
        }
    }

    // ПЛОХО: не закрыть канал — потребитель, итерирующийся по нему, может зависнуть
    suspend fun badNoClose() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            repeat(10) {
                channel.send(it)
            }
            // Нет close() — for (x in channel) не завершится
        }

        for (value in channel) {
            println(value)
        }
    }

    // ХОРОШО: использовать produce builder
    suspend fun goodProduceBuilder() = coroutineScope {
        val numbers = produce {
            repeat(10) { send(it) }
            // Автоматическое закрытие при завершении
        }

        for (num in numbers) {
            println(num)
        }
    }

    // ХОРОШО: обрабатывать ошибки закрытия/отправки
    suspend fun goodErrorHandling() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            try {
                channel.send(1)
            } catch (e: ClosedSendChannelException) {
                println("Channel already closed")
            }
        }
    }

    // ПЛОХО: многократное закрытие
    suspend fun badMultipleClose() = coroutineScope {
        val channel = Channel<Int>()

        val first = channel.close()
        val second = channel.close() // Бесполезно, вернет false
        val third = channel.close(IllegalStateException()) // Причина не переопределится

        println("First close=$first, second close=$second, third close=$third")
    }

    // ХОРОШО: закрывать после завершения всех продюсеров
    suspend fun goodMultipleProducers() = coroutineScope {
        val channel = Channel<Int>()

        val jobs = List(3) { id ->
            launch {
                repeat(10) {
                    channel.send(id * 10 + it)
                }
            }
        }

        jobs.joinAll()
        channel.close()
    }

    // ХОРОШО: cancel() при ошибке (закрывает канал с CancellationException)
    suspend fun goodCancelOnError() = coroutineScope {
        val channel = Channel<Int>()

        try {
            launch {
                for (i in generateSequence(0) { it + 1 }) {
                    channel.send(i)
                    delay(100)
                }
            }

            for (value in channel) {
                if (value > 10) {
                    throw IllegalStateException("Value too high")
                }
                println(value)
            }
        } finally {
            channel.cancel()
        }
    }
}
```

---

## Answer (EN)

Properly managing channel lifecycle is crucial to prevent resource leaks, handle errors gracefully, and ensure clean shutdown of coroutine-based systems.

### Understanding Channel States

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Channel has three main states
fun channelStates() = runBlocking {
    val channel = Channel<Int>()

    // 1. ACTIVE: Can send and receive
    println("isClosedForSend: ${channel.isClosedForSend}") // false
    println("isClosedForReceive: ${channel.isClosedForReceive}") // false

    channel.send(1)

    // 2. CLOSED FOR SEND: No more sends, but can still receive
    channel.close()
    println("isClosedForSend: ${channel.isClosedForSend}") // true
    println("isClosedForReceive: ${channel.isClosedForReceive}") // false

    // Can still receive buffered values
    println("Received: ${channel.receive()}") // 1

    // 3. CLOSED FOR RECEIVE: All values consumed
    println("isClosedForReceive: ${channel.isClosedForReceive}") // true
}
```

### close() Vs cancel() Vs close(cause)

Key ideas:
- close(): graceful, signals "no more elements"; buffered elements remain available for receive.
- cancel(cause): closes the channel with a (cancellation) cause; suspending send/receive operations are resumed with an exception; buffered elements may be discarded and should not be relied upon.
- close(cause): similar to close(), but records a completion cause (e.g., an error) that can be inspected via getCompletionExceptionOrNull().

```kotlin
class ChannelClosingMethods(private val scope: CoroutineScope) {

    // close(): Graceful shutdown
    suspend fun closeExample() = coroutineScope {
        val channel = Channel<Int>(capacity = 10)

        val producer = launch {
            try {
                for (i in 1..5) {
                    channel.send(i)
                }
            } finally {
                channel.close() // Signal no more values
                println("Channel closed normally")
            }
        }

        // Consumer can read all buffered values
        for (value in channel) {
            println("Received: $value")
        }
        producer.join()
        println("All values consumed")
    }

    // cancel(): Immediate cancellation with cause, may discard buffered elements
    suspend fun cancelExample() = coroutineScope {
        val channel = Channel<Int>(capacity = 10)

        val producerJob = launch {
            try {
                for (i in 1..100) {
                    channel.send(i)
                    delay(100)
                }
            } catch (e: CancellationException) {
                println("Producer cancelled")
                throw e
            }
        }

        delay(250) // Receive a few values (if there is a consumer)

        // Stop producer & channel; channel.cancel() closes it with CancellationException
        producerJob.cancel()
        channel.cancel()

        println("Channel cancelled")
    }

    // close(cause): Close with exception cause for diagnostic purposes
    suspend fun closeWithCauseExample() = coroutineScope {
        val channel = Channel<Int>()

        val producer = launch {
            try {
                repeat(10) {
                    if (it == 5) {
                        throw IllegalStateException("Something went wrong")
                    }
                    channel.send(it)
                }
            } catch (e: Exception) {
                channel.close(e) // Close with cause; consumers will observe closure
            }
        }

        for (value in channel) {
            println("Received: $value")
        }

        producer.join()

        // Access completion cause explicitly if needed
        val cause = channel.getCompletionExceptionOrNull()
        if (cause != null) {
            println("Channel closed due to: ${cause.message}")
        }
    }
}
```

### Exceptions: ClosedSendChannelException Vs ClosedReceiveChannelException

```kotlin
class ChannelExceptions(private val scope: CoroutineScope) {

    // ClosedSendChannelException: send() on closed channel
    suspend fun closedSendExample() = coroutineScope {
        val channel = Channel<Int>()

        channel.close()

        try {
            channel.send(1) // Throws ClosedSendChannelException
        } catch (e: ClosedSendChannelException) {
            println("Cannot send to closed channel: $e")
        }

        // Safe alternative: trySend
        val result = channel.trySend(1)
        if (result.isFailure) {
            println("trySend failed; closed=${result.isClosed}")
        }
    }

    // ClosedReceiveChannelException: receive() on empty closed channel
    suspend fun closedReceiveExample() = coroutineScope {
        val channel = Channel<Int>()

        channel.send(1)
        channel.close()

        // First receive succeeds (value in buffer)
        println("First: ${channel.receive()}") // 1

        try {
            // Second receive fails (no more values)
            channel.receive() // Throws ClosedReceiveChannelException
        } catch (e: ClosedReceiveChannelException) {
            println("No more values: $e")
        }

        // Safe alternative: tryReceive
        val result = channel.tryReceive()
        if (result.isFailure) {
            println("tryReceive failed; closed=${result.isClosed}")
        }

        // Best practice: iterate with for loop
        val channel2 = Channel<Int>()
        channel2.send(1)
        channel2.send(2)
        channel2.close()

        for (value in channel2) {
            println(value) // No exception, loop ends naturally
        }
    }

    // Handling close cause (prefer inspecting the channel's completion state)
    suspend fun closeCauseExample() = coroutineScope {
        val channel = Channel<String>()

        val producer = launch {
            try {
                channel.send("First")
                throw java.io.IOException("Network error")
            } catch (e: Exception) {
                channel.close(e) // Propagate error as channel completion cause
            }
        }

        for (value in channel) {
            println("Received: $value")
        }

        producer.join()

        val completionCause = channel.getCompletionExceptionOrNull()
        if (completionCause is java.io.IOException) {
            println("Channel closed due to network error: ${completionCause.message}")
        }
    }
}
```

### Producer-Consumer Patterns with Proper Cleanup

```kotlin
class ProperCleanupPatterns(private val scope: CoroutineScope) {

    // Pattern 1: Producer closes channel
    suspend fun producerClosesChannel() = coroutineScope {
        val channel = Channel<Int>()

        // Producer responsible for closing
        val producer = launch {
            try {
                for (i in 1..10) {
                    channel.send(i)
                }
            } catch (e: Exception) {
                println("Producer error: $e")
            } finally {
                channel.close()
                println("Producer closed channel")
            }
        }

        // Consumer just reads until closed
        for (value in channel) {
            println("Processed: $value")
        }

        producer.join()
    }

    // Pattern 2: Multiple producers, coordinator closes
    suspend fun multipleProducersPattern() = coroutineScope {
        val channel = Channel<Int>(capacity = 100)

        // Multiple producers
        val producers = List(3) { id ->
            launch {
                try {
                    repeat(10) {
                        channel.send(id * 100 + it)
                    }
                } catch (e: ClosedSendChannelException) {
                    println("Producer $id: Channel already closed")
                }
            }
        }

        // Wait for all producers to finish
        producers.joinAll()

        // Coordinator closes channel
        channel.close()
        println("All producers finished, channel closed")

        // Consumer
        for (value in channel) {
            println("Received: $value")
        }
    }

    // Pattern 3: Consumer cancels early
    suspend fun consumerCancelsEarly() = coroutineScope {
        val channel = Channel<Int>()

        val producer = launch {
            try {
                var i = 0
                while (true) {
                    channel.send(i++)
                    delay(100)
                }
            } catch (e: ClosedSendChannelException) {
                println("Channel closed by consumer")
            } finally {
                println("Producer cleaning up")
            }
        }

        // Consumer takes only a few values
        val consumer = launch {
            repeat(5) {
                println("Received: ${channel.receive()}")
            }
            // Consumer done, cancel everything
            channel.cancel()
            producer.cancel()
        }

        consumer.join()
    }

    // Pattern 4: Timeout-based closure
    suspend fun timeoutBasedClosure() = coroutineScope {
        val channel = Channel<Int>()

        val producer = launch {
            try {
                var i = 0
                while (true) {
                    channel.send(i++)
                    delay(50)
                }
            } catch (e: ClosedSendChannelException) {
                println("Channel closed")
            }
        }

        // Consume with timeout
        try {
            withTimeout(500) {
                for (value in channel) {
                    println("Received: $value")
                }
            }
        } catch (e: TimeoutCancellationException) {
            println("Timeout reached")
        } finally {
            channel.cancel()
            producer.cancel()
        }
    }
}
```

### Using Produce Builder (Recommended)

```kotlin
class ProduceBuilderPattern {

    // produce automatically closes the channel when the producer coroutine completes
    fun produceExample() = runBlocking {
        val numbers = produce {
            for (i in 1..10) {
                send(i)
            }
            // No need to close() - done automatically when this coroutine completes
        }

        for (num in numbers) {
            println(num)
        }
        // Channel is closed after the producer completes
    }

    // produce with exception handling: channel is closed with the exception as completion cause
    fun produceWithException() = runBlocking {
        val numbers = produce {
            for (i in 1..10) {
                if (i == 5) throw IllegalStateException("Error at 5")
                send(i)
            }
        }

        try {
            for (num in numbers) {
                println(num)
            }
        } catch (e: ClosedReceiveChannelException) {
            // ClosedReceiveChannelException indicates closure; inspect channel for cause
            val cause = numbers.getCompletionExceptionOrNull()
            println("Channel closed due to: ${cause?.message}")
        }
    }

    // produce with cancellation
    fun produceWithCancellation() = runBlocking {
        val numbers = produce {
            var i = 0
            try {
                while (true) {
                    send(i++)
                    delay(100)
                }
            } finally {
                println("Producer cancelled after $i items")
            }
        }

        // Take only first 5
        repeat(5) {
            println(numbers.receive())
        }

        numbers.cancel() // Cancels the producer coroutine and closes the channel
    }
}
```

### Advanced Cleanup Scenarios

```kotlin
class AdvancedCleanup(private val scope: CoroutineScope) {

    // Cleanup with resources
    suspend fun channelWithResources() = coroutineScope {
        class DatabaseConnection : AutoCloseable {
            fun query(sql: String): List<Int> = listOf(1, 2, 3)
            override fun close() {
                println("Database connection closed")
            }
        }

        val channel = Channel<Int>()

        val producer = launch {
            DatabaseConnection().use { db ->
                try {
                    val results = db.query("SELECT * FROM data")
                    for (result in results) {
                        channel.send(result)
                    }
                } finally {
                    channel.close()
                    println("Channel closed")
                }
            }
        }

        for (value in channel) {
            println("Received: $value")
        }

        producer.join()
    }

    // Pipeline cleanup
    suspend fun pipelineCleanup() = coroutineScope {
        val input = Channel<Int>()
        val output = Channel<String>()

        // Stage 1: Producer
        val producer = launch {
            try {
                for (i in 1..10) {
                    input.send(i)
                }
            } finally {
                input.close()
                println("Input closed")
            }
        }

        // Stage 2: Processor
        val processor = launch {
            try {
                for (value in input) {
                    output.send("Processed: $value")
                }
            } finally {
                output.close()
                println("Output closed")
            }
        }

        // Stage 3: Consumer
        for (result in output) {
            println(result)
        }

        joinAll(producer, processor)
        println("Pipeline complete")
    }

    // Error propagation through pipeline
    suspend fun errorPropagation() = coroutineScope {
        val channel1 = Channel<Int>()
        val channel2 = Channel<String>()

        val stage1 = launch {
            try {
                for (i in 1..10) {
                    if (i == 5) throw RuntimeException("Stage 1 error")
                    channel1.send(i)
                }
                channel1.close()
            } catch (e: Exception) {
                channel1.close(e) // Propagate error as completion cause
            }
        }

        val stage2 = launch {
            try {
                for (value in channel1) {
                    channel2.send("Stage2: $value")
                }
                channel2.close()
            } catch (e: Exception) {
                // On error or upstream close with cause, close downstream with same cause
                val cause = channel1.getCompletionExceptionOrNull() ?: e
                channel2.close(cause)
            }
        }

        try {
            for (result in channel2) {
                println(result)
            }
        } catch (e: ClosedReceiveChannelException) {
            val cause = channel2.getCompletionExceptionOrNull()
            println("Consumer received error: ${cause?.message}")
        }

        joinAll(stage1, stage2)
    }
}
```

### Testing Channel Closure

```kotlin
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlin.test.assertFailsWith

class ChannelClosureTests {

    @Test
    fun `test channel closes after all values sent`() = runTest {
        val channel = Channel<Int>()

        launch {
            channel.send(1)
            channel.send(2)
            channel.close()
        }

        val values = mutableListOf<Int>()
        for (value in channel) {
            values.add(value)
        }

        assertEquals(listOf(1, 2), values)
        assertTrue(channel.isClosedForReceive)
    }

    @Test
    fun `test send to closed channel throws exception`() = runTest {
        val channel = Channel<Int>()
        channel.close()

        assertFailsWith<ClosedSendChannelException> {
            channel.send(1)
        }
    }

    @Test
    fun `test receive from empty closed channel throws exception`() = runTest {
        val channel = Channel<Int>()
        channel.close()

        assertFailsWith<ClosedReceiveChannelException> {
            channel.receive()
        }
    }

    @Test
    fun `test close with cause propagates error`() = runTest {
        val channel = Channel<Int>()
        val error = IllegalStateException("Test error")

        channel.close(error)

        assertFailsWith<ClosedReceiveChannelException> {
            channel.receive()
        }

        // Completion cause is available from the channel
        val completionCause = channel.getCompletionExceptionOrNull()
        assertEquals(error, completionCause)
    }

    @Test
    fun `test trySend on closed channel returns failure`() = runTest {
        val channel = Channel<Int>()
        channel.close()

        val result = channel.trySend(1)

        assertTrue(result.isFailure)
        assertTrue(result.isClosed)
    }
}
```

### Best Practices and Anti-patterns

```kotlin
class BestPractices(private val scope: CoroutineScope) {

    //  GOOD: Always close in finally (from within a producer responsible for the channel)
    suspend fun goodClosePattern() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            try {
                repeat(10) {
                    channel.send(it)
                }
            } finally {
                channel.close()
            }
        }
    }

    //  BAD: Forgot to close — consumer that iterates will hang waiting for closure
    suspend fun badNoClose() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            repeat(10) {
                channel.send(it)
            }
            // Missing close() - consumer using `for (x in channel)` would hang
        }

        for (value in channel) {
            println(value)
        }
    }

    //  GOOD: Use produce builder
    suspend fun goodProduceBuilder() = coroutineScope {
        val numbers = produce {
            repeat(10) { send(it) }
            // Automatic close when producer completes
        }

        for (num in numbers) {
            println(num)
        }
    }

    //  GOOD: Handle close errors
    suspend fun goodErrorHandling() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            try {
                channel.send(1)
            } catch (e: ClosedSendChannelException) {
                println("Channel already closed")
            }
        }
    }

    //  BAD: Closing multiple times
    suspend fun badMultipleClose() = coroutineScope {
        val channel = Channel<Int>()

        val first = channel.close()
        val second = channel.close() // Harmless but unnecessary; returns false
        val third = channel.close(IllegalStateException()) // Ignored: cause is not updated

        println("First close=$first, second close=$second, third close=$third")
    }

    //  GOOD: Close after all producers finish
    suspend fun goodMultipleProducers() = coroutineScope {
        val channel = Channel<Int>()

        val jobs = List(3) { id ->
            launch {
                repeat(10) {
                    channel.send(id * 10 + it)
                }
            }
        }

        jobs.joinAll()
        channel.close() // Close after all done
    }

    //  GOOD: Cancel on error (channel.cancel closes with a CancellationException)
    suspend fun goodCancelOnError() = coroutineScope {
        val channel = Channel<Int>()

        try {
            launch {
                for (i in generateSequence(0) { it + 1 }) {
                    channel.send(i)
                    delay(100)
                }
            }

            for (value in channel) {
                if (value > 10) {
                    throw IllegalStateException("Value too high")
                }
                println(value)
            }
        } finally {
            channel.cancel() // Clean cancellation, signals error to sender/receivers
        }
    }
}
```

---

## Follow-ups

1. How to handle cleanup in complex channel pipelines?
   - Multiple stages
   - Error propagation
   - Resource management

2. What happens to buffered values when a channel is cancelled?
   - Buffer behavior
   - Data loss scenarios
   - Recovery strategies

3. How to implement graceful shutdown with channels?
   - Drain strategy
   - Timeout handling
   - Coordinated shutdown

4. How does `produce` builder simplify channel management?
   - Automatic closing
   - Exception handling
   - Scope integration

5. How to test channel closure scenarios?
   - Testing normal closure
   - Testing error cases
   - Testing cancellation

---

## References (Ссылки)

### Official Documentation
- [Channel Closing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-send-channel/close.html)
- [Channel Cancellation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-receive-channel/cancel.html)
- [produce Builder](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html)

### Learning Resources
- "Kotlin Coroutines" by Marcin Moskała - Channel `Lifecycle`
- [Channel Closing Best Practices](https://kotlinlang.org/docs/channels.html#closing-and-iteration-over-channels)

### Related Topics
- [[c-kotlin]]
- [[c-coroutines]]

---

## Related Questions (Связанные вопросы)

- [[q-channels-basics-types--kotlin--medium]] - Channel fundamentals
- [[q-produce-actor-builders--kotlin--medium]] - Channel builders
