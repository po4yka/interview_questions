---
id: kotlin-078
title: "Channel Closing and Completion / Закрытие и завершение каналов"
aliases: ["Channel Closing and Completion, Закрытие и завершение каналов"]

# Classification
topic: kotlin
subtopics: [channel-closing, channels, cleanup]
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
related: [q-channel-exception-handling--kotlin--hard, q-channels-basics-types--kotlin--medium, q-produce-actor-builders--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [channels, cleanup, closing, completion, coroutines, difficulty/medium, kotlin]
---

# Question (EN)
> How do you properly close and complete channels? Explain close(), cancel(), the difference between ClosedSendChannelException and ClosedReceiveChannelException, and best practices for cleanup.

# Вопрос (RU)
> Как правильно закрывать и завершать каналы? Объясните close(), cancel(), разницу между ClosedSendChannelException и ClosedReceiveChannelException и лучшие практики очистки ресурсов.

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

### close() Vs cancel() Vs closeCause

```kotlin
class ChannelClosingMethods {

    // close(): Graceful shutdown
    suspend fun closeExample() {
        val channel = Channel<Int>(capacity = 10)

        launch {
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
        println("All values consumed")
    }

    // cancel(): Immediate cancellation
    suspend fun cancelExample() {
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
            } finally {
                channel.close()
            }
        }

        delay(250) // Receive a few values

        producerJob.cancel() // Stop producer immediately
        channel.cancel() // Cancel channel

        // No more values available
        println("Channel cancelled")
    }

    // close(cause): Close with exception
    suspend fun closeWithCauseExample() {
        val channel = Channel<Int>()

        launch {
            try {
                repeat(10) {
                    if (it == 5) {
                        throw IllegalStateException("Something went wrong")
                    }
                    channel.send(it)
                }
            } catch (e: Exception) {
                channel.close(e) // Close with cause
            }
        }

        try {
            for (value in channel) {
                println("Received: $value")
            }
        } catch (e: ClosedReceiveChannelException) {
            println("Channel closed due to: ${e.cause}")
        }
    }
}
```

### Exceptions: ClosedSendChannelException Vs ClosedReceiveChannelException

```kotlin
class ChannelExceptions {

    // ClosedSendChannelException: send() on closed channel
    suspend fun closedSendExample() {
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
            println("trySend failed: ${result.isClosedForSend}")
        }
    }

    // ClosedReceiveChannelException: receive() on empty closed channel
    suspend fun closedReceiveExample() {
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
            println("tryReceive failed: ${result.isClosedForReceive}")
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

    // Handling close cause
    suspend fun closeCauseExample() {
        val channel = Channel<String>()

        launch {
            try {
                channel.send("First")
                throw IOException("Network error")
            } catch (e: IOException) {
                channel.close(e) // Propagate error
            }
        }

        try {
            for (value in channel) {
                println("Received: $value")
            }
        } catch (e: ClosedReceiveChannelException) {
            val cause = e.cause
            if (cause is IOException) {
                println("Channel closed due to network error: ${cause.message}")
            }
        }
    }
}
```

### Producer-Consumer Patterns with Proper Cleanup

```kotlin
class ProperCleanupPatterns {

    // Pattern 1: Producer closes channel
    suspend fun producerClosesChannel() {
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
    suspend fun multipleProducersPattern() {
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
    suspend fun consumerCancelsEarly() {
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
    suspend fun timeoutBasedClosure() {
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

    // produce automatically handles closing
    fun produceExample() = runBlocking {
        val numbers = produce {
            for (i in 1..10) {
                send(i)
            }
            // No need to close() - done automatically
        }

        for (num in numbers) {
            println(num)
        }
        // Channel automatically closed
    }

    // produce with exception handling
    fun produceWithException() = runBlocking {
        val numbers = produce {
            try {
                for (i in 1..10) {
                    if (i == 5) throw IllegalStateException("Error at 5")
                    send(i)
                }
            } catch (e: IllegalStateException) {
                println("Producer error: ${e.message}")
                // Channel automatically closed with cause
            }
        }

        try {
            for (num in numbers) {
                println(num)
            }
        } catch (e: ClosedReceiveChannelException) {
            println("Channel closed: ${e.cause}")
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

        numbers.cancel() // Automatically cancels producer
    }
}
```

### Advanced Cleanup Scenarios

```kotlin
class AdvancedCleanup {

    // Cleanup with resources
    suspend fun channelWithResources() {
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
    suspend fun pipelineCleanup() {
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
    suspend fun errorPropagation() {
        val channel1 = Channel<Int>()
        val channel2 = Channel<String>()

        val stage1 = launch {
            try {
                for (i in 1..10) {
                    if (i == 5) throw RuntimeException("Stage 1 error")
                    channel1.send(i)
                }
            } catch (e: Exception) {
                channel1.close(e) // Propagate error
            }
        }

        val stage2 = launch {
            try {
                for (value in channel1) {
                    channel2.send("Stage2: $value")
                }
            } catch (e: ClosedReceiveChannelException) {
                println("Stage 2 received error: ${e.cause}")
                channel2.close(e.cause) // Propagate error
            }
        }

        try {
            for (result in channel2) {
                println(result)
            }
        } catch (e: ClosedReceiveChannelException) {
            println("Consumer received error: ${e.cause}")
        }

        joinAll(stage1, stage2)
    }
}
```

### Testing Channel Closure

```kotlin
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

        assertThrows<ClosedSendChannelException> {
            channel.send(1)
        }
    }

    @Test
    fun `test receive from empty closed channel throws exception`() = runTest {
        val channel = Channel<Int>()
        channel.close()

        assertThrows<ClosedReceiveChannelException> {
            channel.receive()
        }
    }

    @Test
    fun `test close with cause propagates error`() = runTest {
        val channel = Channel<Int>()
        val error = IllegalStateException("Test error")

        channel.close(error)

        val exception = assertThrows<ClosedReceiveChannelException> {
            channel.receive()
        }

        assertEquals(error, exception.cause)
    }

    @Test
    fun `test trySend on closed channel returns failure`() = runTest {
        val channel = Channel<Int>()
        channel.close()

        val result = channel.trySend(1)

        assertTrue(result.isFailure)
        assertTrue(result.isClosedForSend)
    }
}
```

### Best Practices and Anti-patterns

```kotlin
class BestPractices {

    //  GOOD: Always close in finally
    suspend fun goodClosePattern() {
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

    //  BAD: Forgot to close
    suspend fun badNoClose() {
        val channel = Channel<Int>()

        launch {
            repeat(10) {
                channel.send(it)
            }
            // Missing close() - consumer hangs!
        }

        for (value in channel) {
            println(value)
        }
    }

    //  GOOD: Use produce builder
    suspend fun goodProduceBuilder() {
        val numbers = produce {
            repeat(10) { send(it) }
            // Automatic close
        }

        for (num in numbers) {
            println(num)
        }
    }

    //  GOOD: Handle close errors
    suspend fun goodErrorHandling() {
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
    suspend fun badMultipleClose() {
        val channel = Channel<Int>()

        channel.close()
        channel.close() // Harmless but unnecessary
        channel.close(IllegalStateException()) // Ignored!
    }

    //  GOOD: Close after all producers finish
    suspend fun goodMultipleProducers() {
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

    //  GOOD: Cancel on error
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
            channel.cancel() // Clean cancellation
        }
    }
}
```

---

## Ответ (RU)

Правильное управление жизненным циклом каналов критически важно для предотвращения утечек ресурсов и обеспечения корректного завершения работы.

### Понимание Состояний Канала

Канал имеет три основных состояния:
1. **АКТИВЕН**: Можно отправлять и получать
2. **ЗАКРЫТ ДЛЯ ОТПРАВКИ**: Нельзя отправлять, но можно получать буферизованные значения
3. **ЗАКРЫТ ДЛЯ ПОЛУЧЕНИЯ**: Все значения получены

### close() Vs cancel()

```kotlin
// close(): Изящное завершение
channel.close() // Новые отправки запрещены, можно получить оставшиеся

// cancel(): Немедленная отмена
channel.cancel() // Все операции прекращаются
```

### Исключения

- **ClosedSendChannelException**: При send() в закрытый канал
- **ClosedReceiveChannelException**: При receive() из пустого закрытого канала

### Лучшие Практики

```kotlin
//  Всегда закрывать в finally
launch {
    try {
        channel.send(1)
    } finally {
        channel.close()
    }
}

//  Использовать produce builder
val numbers = produce {
    send(1)
    // Автоматическое закрытие
}

//  Использовать for loop вместо receive()
for (value in channel) {
    // Автоматическая обработка закрытия
}
```

---

## Follow-up Questions (Следующие вопросы)

1. **How to handle cleanup in complex channel pipelines?**
   - Multiple stages
   - Error propagation
   - Resource management

2. **What happens to buffered values when a channel is cancelled?**
   - Buffer behavior
   - Data loss scenarios
   - Recovery strategies

3. **How to implement graceful shutdown with channels?**
   - Drain strategy
   - Timeout handling
   - Coordinated shutdown

4. **How does produce builder simplify channel management?**
   - Automatic closing
   - Exception handling
   - Scope integration

5. **How to test channel closure scenarios?**
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
- "Kotlin Coroutines" by Marcin Moskała - Channel Lifecycle
- [Channel Closing Best Practices](https://kotlinlang.org/docs/channels.html#closing-and-iteration-over-channels)

### Related Topics
- Resource Management
- Exception Handling
- Graceful Shutdown
- Producer-Consumer Patterns

---

## Related Questions (Связанные вопросы)

- [[q-channels-basics-types--kotlin--medium]] - Channel fundamentals
- [[q-produce-actor-builders--kotlin--medium]] - Channel builders
- [[q-coroutine-resource-cleanup--kotlin--medium]] - Resource cleanup
- [[q-coroutine-exception-handling--kotlin--medium]] - Exception handling
- [[q-channel-pipelines--kotlin--hard]] - Channel pipelines
