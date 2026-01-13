---
anki_cards:
- slug: q-zip-parallelism-guarantee--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-zip-parallelism-guarantee--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: kotlin-163
title: "Zip Parallelism Guarantee / Гарантия параллелизма zip"
aliases: [Flow Zip, Parallelism, Zip Operator, Zip в Flow]
topic: kotlin
subtopics: [coroutines, flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-flow, c-stateflow, q-partition-function--kotlin--easy]
created: 2025-10-15
updated: 2025-11-11
tags: [coroutines, difficulty/medium, flow, kotlin, operators, zip]
---
# Вопрос (RU)

> Гарантирует ли `zip` параллельное выполнение двух сетевых запросов, запущенных в `Flow`/`Coroutine`?

# Question (EN)

> Will `zip` guarantee parallel execution of 2 network requests launched in `Flow`/`Coroutine`?

## Ответ (RU)

Оператор `zip` в Kotlin `Flow` НЕ гарантирует параллельное выполнение сетевых запросов. Он только объединяет элементы из двух `Flow`, попарно связывая i-й элемент каждого.

`zip`:
- сам по себе не запускает потоки параллельно,
- не управляет тем, на каких потоках/dispatchers выполняются upstream-`Flow`,
- лишь приостанавливает выполнение до тех пор, пока обе стороны не предоставят следующий элемент.

Фактический параллелизм (например, два сетевых запроса одновременно) зависит от того, как построены ваши `Flow` и какие диспетчеры/конструкции (`async` и др.) вы используете.

### Пример Поведения Zip
```kotlin
val flow1 = flow {
    println("Flow1: Starting")
    emit(1)
    delay(1000)
    emit(2)
}

val flow2 = flow {
    println("Flow2: Starting")
    emit("A")
    delay(500)
    emit("B")
}

flow1
    .zip(flow2) { num, letter ->
        "$num$letter"
    }
    .collect { println(it) }
// Сбор обоих Flow выполняется в той же корутине, что вызывает collect (если не используется flowOn и т.п.).
// Эмиссии flow1 и flow2 могут происходить конкурентно, если их тела неблокирующие и настроены соответствующие диспетчеры.
// Но zip сам лишь последовательно связывает пары: (1,"A"), затем (2,"B"), каждый раз ожидая оба значения.
```

### Ключевые Моменты

**1. Нет гарантии параллелизма**
- `Flow` — "холодные"; они не выполняются, пока их не начнут собирать.
- `zip` по контракту не обязан запускать каждый upstream в отдельной корутине; его задача — комбинировать элементы.
- Будут ли два запроса выполняться параллельно, зависит от реализации ваших upstream-`Flow` (например, использования `flowOn`, `channelFlow`, `async`, отдельных корутин), а не от `zip`.

**2. Ожидание и завершение**
```kotlin
val slow = flow {
    delay(2000)
    emit(1)
}

val fast = flow {
    emit("A")
    emit("B")
}

slow
    .zip(fast) { n, l -> "$n$l" }
    .collect { println(it) }
// Испускается только "1A" примерно через 2 секунды.
// После завершения slow оператор zip завершает работу.
// Второе значение "B" из fast остаётся без пары и фактически игнорируется.
```

**3. Для явного параллельного выполнения запросов**
Если нужно, чтобы два сетевых вызова выполнялись параллельно и затем их результаты были объединены, запускайте их явно в отдельных корутинах:
```kotlin
suspend fun parallelCalls(): Pair<Result1, Result2> = coroutineScope {
    val deferred1 = async(Dispatchers.IO) { operation1() }
    val deferred2 = async(Dispatchers.IO) { operation2() }
    Pair(deferred1.await(), deferred2.await())
}
```

См. также: , [[c-coroutines]], [[c-flow]].

### Дополнительные Вопросы (RU)

- Каковы ключевые отличия этого поведения от Java?
- Когда вы бы использовали это на практике?
- Какие распространенные подводные камни стоит учитывать?

### Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

### Связанные Вопросы (RU)

- [[q-partition-function--kotlin--easy]]

## Answer (EN)

The `zip` operator in Kotlin `Flow` does NOT guarantee parallel execution of network requests. It only combines emissions from two `Flow`s by pairing the i-th emission of each.

`zip`:
- does not start flows in parallel by itself,
- does not control which thread/dispatcher each flow runs on,
- only suspends until both sides provide the next element.

Actual parallelism (e.g., two network calls running at the same time) depends on how you build the flows and which dispatchers/constructs (like `async`) you use.

### Example Behavior of Zip
```kotlin
val flow1 = flow {
    println("Flow1: Starting")
    emit(1)
    delay(1000)
    emit(2)
}

val flow2 = flow {
    println("Flow2: Starting")
    emit("A")
    delay(500)
    emit("B")
}

flow1
    .zip(flow2) { num, letter ->
        "$num$letter"
    }
    .collect { println(it) }
// Collection of both flows happens within the same coroutine that calls collect (unless you use flowOn/etc.).
// Emissions from flow1 and flow2 can be produced concurrently if their bodies are non-blocking and dispatched appropriately.
// But zip itself only pairs emissions sequentially: (1,"A"), then (2,"B"), waiting for both sides each time.
```

### Key Points

**1. No Parallelism Guarantee**
- `Flow`s are cold; nothing runs until they are collected.
- `zip` does not launch separate coroutines for each upstream by contract; its job is to combine emissions.
- Whether two requests run in parallel depends on your upstream implementation (e.g., using `flowOn`, `channelFlow`, `async`, or separate coroutines), not on `zip`.

**2. Waiting and Completion Behavior**
```kotlin
val slow = flow {
    delay(2000)
    emit(1)
}

val fast = flow {
    emit("A")
    emit("B")
}

slow
    .zip(fast) { n, l -> "$n$l" }
    .collect { println(it) }
// Emits only "1A" after ~2 seconds.
// After slow completes, zip completes as well.
// The second emission "B" from fast has no matching partner and is effectively ignored.
```

**3. For Explicit Parallel Network Requests**
If you need two network calls to run in parallel and then combine their results, start them explicitly in separate coroutines:
```kotlin
suspend fun parallelCalls(): Pair<Result1, Result2> = coroutineScope {
    val deferred1 = async(Dispatchers.IO) { operation1() }
    val deferred2 = async(Dispatchers.IO) { operation2() }
    Pair(deferred1.await(), deferred2.await())
}
```

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-partition-function--kotlin--easy]]
